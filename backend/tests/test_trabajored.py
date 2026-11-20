"""Internet, correo y Google para el Python de Trabajo: seguridad (nada de la red local) y el token de Google."""
import json
import tempfile
import unittest
from unittest import mock

import utilidades
from app import create_app
from models import db


class TrabajoRedTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": tempfile.mkdtemp()})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.c = self.app.test_client(); self.c.get("/api/auth/me/")
        self.h = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Cris Prueba", "email": "cris@example.com", "password": "Clave123"}, headers=self.h)

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop()

    def post(self, ruta, datos):
        from flask import g
        g.pop("_login_user", None)
        return self.c.post(ruta, json=datos, headers=self.h)

    def test_nunca_a_la_red_local(self):
        for url in ("http://127.0.0.1:3306/", "http://localhost:5000/api/auth/me/", "http://169.254.169.254/latest/meta-data/", "http://10.12.19.82/", "file:///etc/passwd"):
            self.assertEqual(self.post("/api/trabajo/http", {"url": url}).status_code, 403, url)
        r = self.post("/api/trabajo/smtp", {"host": "127.0.0.1", "puerto": 25, "usuario": "a", "clave": "b", "para": ["x@y.co"], "mensaje": ""})
        self.assertEqual(r.status_code, 403)
        r = self.post("/api/trabajo/smtp", {"host": "smtp.gmail.com", "puerto": 3306, "usuario": "a", "clave": "b", "para": ["x@y.co"], "mensaje": ""})
        self.assertEqual(r.status_code, 403)

    def test_redireccion_a_la_red_local_bloqueada(self):
        import rutas.trabajored as tr
        respuesta = mock.Mock(is_redirect=True, status_code=302, headers={"location": "http://127.0.0.1:5000/secreto"})
        with mock.patch.object(tr, "problema_host", lambda h: None if h == "ejemplo.com" else "red local"), \
             mock.patch.object(tr.requests, "request", return_value=respuesta):
            self.assertEqual(self.post("/api/trabajo/http", {"url": "https://ejemplo.com/"}).status_code, 403)

    def test_smtp_exige_login(self):
        import rutas.trabajored as tr
        with mock.patch.object(tr, "problema_host", lambda h: None):
            r = self.post("/api/trabajo/smtp", {"host": "smtp.gmail.com", "puerto": 587, "para": ["x@y.co"], "mensaje": ""})
        self.assertEqual(r.status_code, 403)

    def test_token_de_google_solo_para_su_dueno(self):
        tok = self.post("/api/trabajo/google-token", {"aud": "cliente-1"}).get_json()["credential"]
        r = self.post("/api/trabajo/google-token/verificar", {"token": tok, "aud": "cliente-1"}).get_json()["reclamos"]
        self.assertEqual((r["email"], r["email_verified"], r["aud"]), ("cris@example.com", True, "cliente-1"))
        self.assertEqual(self.post("/api/trabajo/google-token/verificar", {"token": tok, "aud": "otro"}).status_code, 401)
        self.assertEqual(self.post("/api/trabajo/google-token/verificar", {"token": tok[:-3] + "abc", "aud": "cliente-1"}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
