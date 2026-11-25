from unittest.mock import patch
"""Enlace «en vivo» de Trabajo (como Live Server): /live/<clave>/…"""
import tempfile
import unittest

from flask import g

import utilidades
from app import create_app
from models import UserWorkspace, db

CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PROYECTO = {
    "files": {
        "index.html": '<!doctype html><html><head><link rel="stylesheet" href="/css/estilos.css"></head><body><a href="contacto.html">Contacto</a><img src="/img/logo.svg"></body></html>',
        "contacto.html": "<!doctype html><html><head></head><body><h1>Contacto</h1></body></html>",
        "css/estilos.css": "body{background:url(/img/fondo.png)}",
        "js/app.js": "console.log('hola')",
        "blog/index.html": "<html><head></head><body>Blog</body></html>",
        "img/logo.svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
    },
    "folders": ["css", "js", "blog", "img"],
    "git": {},
}


class LiveTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def cliente(self, email="ana@example.com"):
        c = self.app.test_client()
        c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/")
        c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        r = c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": email, "password": "Clave123"}, headers=c.csrf)
        self.assertIn(r.status_code, (200, 201), r.get_data(as_text=True))
        g.pop("_login_user", None)
        return c

    def guardar(self, c, proyecto=PROYECTO):
        g.pop("_login_user", None)
        r = c.put("/api/trabajo/", json=proyecto, headers=c.csrf)
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))

    def enlace(self, c):
        g.pop("_login_user", None)
        r = c.get("/api/trabajo/live/")
        self.assertEqual(r.status_code, 200)
        url = r.get_json()["url"]
        self.assertRegex(url, r"/live/[A-Za-z0-9_-]{16}/$")
        return url[url.index("/live/"):]

    def test_sirve_paginas_estilos_y_carpetas_como_un_servidor(self):
        c = self.cliente(); self.guardar(c); base = self.enlace(c)
        anonimo = self.app.test_client()   # otro navegador, sin sesión
        r = anonimo.get(base)
        self.assertEqual(r.status_code, 200)
        self.assertIn("/js/live.js", r.get_data(as_text=True))          # se arma con el motor de la vista previa
        proyecto = anonimo.get(base + "__cc_proyecto").get_json()
        self.assertIn("contacto.html", proyecto["files"])
        self.assertTrue(proyecto["v"])
        r = anonimo.get(base + "?crudo=1")                              # el HTML tal cual
        html = r.get_data(as_text=True)
        self.assertIn('href="contacto.html"', html)
        self.assertIn(f'href="{base}css/estilos.css"', html)          # la ruta absoluta apunta a tu proyecto
        self.assertIn("__cc_version", html)                             # recarga en vivo
        self.assertIn("sandbox allow-scripts", r.headers["Content-Security-Policy"])   # aislada de la cuenta
        self.assertNotIn("allow-same-origin", r.headers["Content-Security-Policy"])
        self.assertIn("<h1>Contacto</h1>", anonimo.get(base + "contacto.html?crudo=1").get_data(as_text=True))
        css = anonimo.get(base + "css/estilos.css")
        self.assertTrue(css.content_type.startswith("text/css"))
        self.assertIn(f"url({base}img/fondo.png)", css.get_data(as_text=True))
        self.assertTrue(anonimo.get(base + "js/app.js").content_type.startswith("text/javascript"))
        self.assertEqual(anonimo.get(base + "js/app.js").headers["Access-Control-Allow-Origin"], "*")   # sirve para type="module"
        self.assertEqual(anonimo.get(base + "blog").status_code, 302)
        self.assertIn("Blog", anonimo.get(base + "blog/?crudo=1").get_data(as_text=True))
        no = anonimo.get(base + "no-existe.html")
        self.assertEqual(no.status_code, 404)
        self.assertIn("contacto.html", no.get_data(as_text=True))       # lista las páginas que sí hay

    def test_se_recarga_cuando_guardas(self):
        c = self.cliente(); self.guardar(c); base = self.enlace(c)
        v1 = self.app.test_client().get(base + "__cc_version").get_json()["v"]
        self.assertTrue(v1)
        nuevo = {**PROYECTO, "files": {**PROYECTO["files"], "index.html": "<html><head></head><body>Cambié</body></html>"}}
        import time; time.sleep(0.01)
        self.guardar(c, nuevo)
        self.assertNotEqual(self.app.test_client().get(base + "__cc_version").get_json()["v"], v1)
        self.assertIn("Cambié", self.app.test_client().get(base + "__cc_proyecto").get_json()["files"]["index.html"])

    def test_enlaces_externos_de_la_pagina_compartida_se_revisan_sin_cuenta(self):
        c = self.cliente(); self.guardar(c); base = self.enlace(c)
        otro = self.app.test_client()   # quien abre la página compartida no tiene cuenta
        with patch("servicios.seguridad_enlaces._safe_browsing", return_value=None):
            r = otro.post(base + "__cc_enlace", json={"url": "https://example.com/"})
            self.assertEqual(r.status_code, 200); self.assertEqual(r.get_json()["nivel"], "seguro")
            r = otro.post(base + "__cc_enlace", json={"url": "https://login-microsoftonline.com.evil.ru/"})
            self.assertEqual(r.get_json()["nivel"], "bloqueado")
        self.assertEqual(otro.post("/live/claveQueNoExiste1/__cc_enlace", json={"url": "https://example.com/"}).status_code, 404)

    def test_cambiar_enlace_corta_el_anterior_y_cada_cuenta_tiene_el_suyo(self):
        c = self.cliente(); self.guardar(c); base = self.enlace(c)
        self.assertEqual(self.enlace(c), base)                           # el mismo mientras no lo cambies
        g.pop("_login_user", None)
        nuevo = c.post("/api/trabajo/live/cambiar/", headers=c.csrf).get_json()["url"]
        self.assertNotIn(base, nuevo)
        self.assertEqual(self.app.test_client().get(base).status_code, 404)
        otra = self.cliente("beto@example.com")
        self.assertNotEqual(self.enlace(otra), base)
        g.pop("_login_user", None)
        c.delete("/api/trabajo/live/", headers=c.csrf)
        self.assertIsNone(UserWorkspace.query.filter(UserWorkspace.live_clave.isnot(None)).filter_by(usuario_id=1).first())

    def test_claves_raras_no_sirven(self):
        anonimo = self.app.test_client()
        for mala in ("abc", "../../etc", "x" * 40):
            self.assertEqual(anonimo.get(f"/live/{mala}/").status_code, 404)
        self.assertEqual(anonimo.get("/api/trabajo/live/").status_code, 401)


    def test_desde_localhost_el_enlace_usa_la_direccion_publica(self):
        import os
        c = self.cliente(); self.guardar(c)
        os.environ["APP_URL"] = "http://localhost:5000,https://codigocamp.ejemplo.ts.net"
        try:
            g.pop("_login_user", None)
            r = c.get("/api/trabajo/live/", base_url="http://localhost:5000").get_json()
            self.assertTrue(r["url"].startswith("https://codigocamp.ejemplo.ts.net/live/"))
            self.assertFalse(r["solo_local"])
        finally:
            os.environ.pop("APP_URL", None)
        g.pop("_login_user", None)
        self.assertTrue(c.get("/api/trabajo/live/", base_url="http://localhost:5000").get_json()["solo_local"])
