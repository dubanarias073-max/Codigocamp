"""¿Olvidaste tu contraseña?: enlace por correo, un solo uso, vence y cierra todas las sesiones."""
import re
import tempfile
import unittest
from unittest import mock

import utilidades
from app import create_app
from models import db


class RestablecerTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": tempfile.mkdtemp()})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.enviados = []
        self.p = mock.patch("servicios.correo.enviar", lambda para, asunto, cuerpo, **k: self.enviados.append((para, asunto, cuerpo)))
        self.p.start()

    def tearDown(self):
        self.p.stop(); db.session.remove(); db.drop_all(); self.ctx.pop()

    def pedir(self, c, metodo, url, **kw):
        from flask import g
        g.pop("_login_user", None)
        return getattr(c, metodo)(url, **kw)

    def nuevo(self):
        c = self.app.test_client(); self.pedir(c, "get", "/api/auth/me/")
        return c, {"X-CSRFToken": c.get_cookie("csrftoken").value}

    def test_flujo_completo(self):
        ana, h = self.nuevo()
        self.pedir(ana, "post", "/api/auth/register/", json={"nombre": "Ana Prueba", "email": "ana@example.com", "password": "Clave123"}, headers=h)
        self.enviados.clear()
        anonimo, h2 = self.nuevo()
        r = self.pedir(anonimo, "post", "/api/auth/olvide/", json={"email": "ana@example.com"}, headers=h2)
        self.assertEqual(r.status_code, 200)
        # Un correo que no existe recibe la misma respuesta y no se envía nada.
        r2 = self.pedir(anonimo, "post", "/api/auth/olvide/", json={"email": "nadie@example.com"}, headers=h2)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(len(self.enviados), 1)
        token = re.search(r"restablecer\.html\?t=([\w.\-]+)", self.enviados[0][2]).group(1)
        v = self.pedir(anonimo, "post", "/api/auth/restablecer/validar/", json={"token": token}, headers=h2).get_json()
        self.assertTrue(v["email"].endswith("@example.com")); self.assertNotIn("ana@", v["email"])
        self.assertEqual(self.pedir(anonimo, "post", "/api/auth/restablecer/", json={"token": token, "password": "debil"}, headers=h2).status_code, 400)
        self.assertEqual(self.pedir(anonimo, "post", "/api/auth/restablecer/", json={"token": token, "password": "Nueva456"}, headers=h2).status_code, 200)
        # La sesión que Ana tenía abierta quedó cerrada.
        self.assertIsNone(self.pedir(ana, "get", "/api/auth/me/").get_json().get("user"))
        # Un solo uso.
        self.assertEqual(self.pedir(anonimo, "post", "/api/auth/restablecer/", json={"token": token, "password": "Otra7890"}, headers=h2).status_code, 400)
        self.assertEqual(self.pedir(anonimo, "post", "/api/auth/login/", json={"email": "ana@example.com", "password": "Nueva456"}, headers=h2).status_code, 200)

    def test_enlace_falso_o_vencido(self):
        c, h = self.nuevo()
        self.assertEqual(self.pedir(c, "post", "/api/auth/restablecer/validar/", json={"token": "abc"}, headers=h).status_code, 400)
        from itsdangerous import URLSafeTimedSerializer
        with mock.patch("rutas.auth.MINUTOS_RESTABLECER", -1):
            t = URLSafeTimedSerializer("x", salt="restablecer-clave").dumps({"u": 1, "h": "z"})
            r = self.pedir(c, "post", "/api/auth/restablecer/validar/", json={"token": t}, headers=h).get_json()
        self.assertIn("venció", r["error"])


if __name__ == "__main__":
    unittest.main()


class VariasDireccionesTest(unittest.TestCase):
    """APP_URL y GOOGLE_REDIRECT_URI con localhost y el túnel: se usa la de la visita."""

    def test_elige_la_de_la_visita(self):
        from flask import Flask
        from utilidades import direccion_actual, direcciones
        lista = direcciones("http://localhost:5000/, https://codigocamp.taila41f89.ts.net")
        app = Flask(__name__)
        with app.test_request_context("/", base_url="http://localhost:5000"):
            self.assertEqual(direccion_actual(lista), "http://localhost:5000")
        with app.test_request_context("/", base_url="https://codigocamp.taila41f89.ts.net"):
            self.assertEqual(direccion_actual(lista), "https://codigocamp.taila41f89.ts.net")
        with app.test_request_context("/", base_url="http://codigocamp.taila41f89.ts.net"):   # túnel sin PROXY_CONFIABLE
            self.assertEqual(direccion_actual(lista), "https://codigocamp.taila41f89.ts.net")
        self.assertEqual(direccion_actual(lista), "http://localhost:5000")   # avisos automáticos: la primera

    def test_correo_con_enlace_del_tunel(self):
        enviados = []
        with mock.patch("servicios.correo.enviar", lambda para, asunto, cuerpo, **k: enviados.append(cuerpo)):
            app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                              "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": tempfile.mkdtemp(),
                              "APP_URL": "http://localhost:5000,https://codigocamp.taila41f89.ts.net"})
            utilidades._RATE_LIMITS.clear()
            with app.app_context():
                db.create_all()
                c = app.test_client()
                b = "https://codigocamp.taila41f89.ts.net"
                c.get("/api/auth/me/", base_url=b); h = {"X-CSRFToken": c.get_cookie("csrftoken", domain="codigocamp.taila41f89.ts.net").value}
                c.post("/api/auth/register/", json={"nombre": "Ana Prueba", "email": "ana@example.com", "password": "Clave123"}, headers=h, base_url=b)
                enviados.clear()
                c.post("/api/auth/olvide/", json={"email": "ana@example.com"}, headers=h, base_url=b)
                self.assertIn("https://codigocamp.taila41f89.ts.net/pages/restablecer.html?t=", enviados[0])
                db.session.remove(); db.drop_all()


class GoogleMismaDireccionTest(unittest.TestCase):
    def test_pasa_a_la_direccion_registrada_antes_de_ir_a_google(self):
        app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                          "GOOGLE_CLIENT_ID": "id", "GOOGLE_CLIENT_SECRET": "secreto", "ALMACEN_ARCHIVOS": tempfile.mkdtemp(),
                          "GOOGLE_REDIRECT_URI": "http://localhost:5000/auth/google/callback/,https://codigocamp.taila41f89.ts.net/auth/google/callback/"})
        c = app.test_client()
        r = c.get("/auth/google/", base_url="http://127.0.0.1:5000")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["Location"], "http://localhost:5000/auth/google/?paso=1")
        with mock.patch("rutas.auth.oauth") as o:
            o.google.authorize_redirect.return_value = "a-google"
            c.get("/auth/google/", base_url="https://codigocamp.taila41f89.ts.net")
            self.assertEqual(o.google.authorize_redirect.call_args[0][0], "https://codigocamp.taila41f89.ts.net/auth/google/callback/")
