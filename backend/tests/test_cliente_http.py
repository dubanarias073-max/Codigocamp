"""Cliente HTTP de Trabajo: el puente del servidor hace peticiones a internet pero nunca a redes internas (SSRF)."""
import base64
import http.server
import threading
import unittest
from unittest import mock

from flask import g

import utilidades
from app import create_app
from models import db
from servicios import proxy_http

RESOLVER_REAL = proxy_http.resolver


class Api(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/redirige-interno":
            self.send_response(302); self.send_header("Location", "http://169.254.169.254/latest/meta-data"); self.end_headers(); return
        if self.path == "/redirige":
            self.send_response(302); self.send_header("Location", "/hola?x=1"); self.end_headers(); return
        cuerpo = b'{"hola": "mundo", "ruta": "%s", "auth": "%s"}' % (self.path.encode(), (self.headers.get("Authorization") or "").encode())
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(cuerpo))); self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        datos = self.rfile.read(n)
        self.send_response(201); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(b'{"recibido": ' + datos + b"}")


class ClienteHttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Api)
        cls.puerto = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.h = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana", "email": "ana@example.com", "password": "Clave123"}, headers=self.h)

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def pedir(self, **datos):
        g.pop("_login_user", None)
        return self.c.post("/api/trabajo/cliente-http", json=datos, headers=self.h)

    def publico(self, nombre, puerto):
        """En las pruebas, «api.ejemplo.com» es el servidor local de arriba (como si fuera un sitio público)."""
        if nombre == "api.ejemplo.com":
            return "127.0.0.1"
        return RESOLVER_REAL(nombre, puerto)

    def test_get_post_y_redireccion_a_un_sitio_publico(self):
        with mock.patch.object(proxy_http, "resolver", side_effect=self.publico):
            r = self.pedir(metodo="GET", url=f"http://api.ejemplo.com:{self.puerto}/usuarios?pagina=2", cabeceras=[["Authorization", "Bearer abc"]]).get_json()
            self.assertEqual(r["status"], 200)
            self.assertIn(b'"ruta": "/usuarios?pagina=2"', base64.b64decode(r["cuerpo_b64"]))
            self.assertIn(b"Bearer abc", base64.b64decode(r["cuerpo_b64"]))
            r = self.pedir(metodo="POST", url=f"http://api.ejemplo.com:{self.puerto}/items", cabeceras=[["Content-Type", "application/json"]],
                           cuerpo_b64=base64.b64encode(b'{"n": 1}').decode()).get_json()
            self.assertEqual((r["status"], base64.b64decode(r["cuerpo_b64"])), (201, b'{"recibido": {"n": 1}}'))
            r = self.pedir(metodo="GET", url=f"http://api.ejemplo.com:{self.puerto}/redirige").get_json()
            self.assertEqual((r["status"], r["url"].endswith("/hola?x=1")), (200, True))

    def test_no_llega_a_redes_internas(self):
        for url in (f"http://127.0.0.1:{self.puerto}/", f"http://localhost:{self.puerto}/", "http://169.254.169.254/latest/meta-data",
                    "http://[::1]/", "http://10.0.0.1/", "file:///etc/passwd", "gopher://x"):
            r = self.pedir(metodo="GET", url=url)
            self.assertEqual(r.status_code, 422, url)
        with mock.patch.object(proxy_http, "resolver", side_effect=self.publico):
            r = self.pedir(metodo="GET", url=f"http://api.ejemplo.com:{self.puerto}/redirige-interno")
            self.assertEqual(r.status_code, 422, "una redirección hacia la red interna también se bloquea")

    def test_respeta_el_escudo_y_el_interruptor_de_red(self):
        import rutas.trabajored as tr
        with mock.patch.object(proxy_http, "resolver", side_effect=self.publico), \
             mock.patch.object(tr, "_enlace_peligroso", lambda u: "🛡️ bloqueado" if "malo" in u else None):
            r = self.pedir(metodo="GET", url=f"http://api.ejemplo.com:{self.puerto}/malo")
            self.assertEqual((r.status_code, r.get_json().get("error", "") or r.get_json().get("detail", "")), (422, "🛡️ bloqueado"))
            self.assertEqual(self.pedir(metodo="GET", url=f"http://api.ejemplo.com:{self.puerto}/bien").status_code, 200)
        self.app.config["TRABAJO_RED"] = "0"
        self.assertEqual(self.pedir(metodo="GET", url="https://example.com").status_code, 403)

    def test_metodo_raro_y_sin_sesion(self):
        self.assertEqual(self.pedir(metodo="TRACE", url="https://example.com").status_code, 422)
        g.pop("_login_user", None)
        self.c.post("/api/auth/logout/", headers=self.h)
        g.pop("_login_user", None)
        self.assertIn(self.c.post("/api/trabajo/cliente-http", json={"url": "https://example.com"}, headers=self.h).status_code, (401, 403))


if __name__ == "__main__":
    unittest.main()
