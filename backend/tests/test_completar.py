"""Copiloto en línea: /api/tutor/completar/ devuelve solo el texto que va en el cursor."""
import tempfile
import unittest
from unittest import mock

from flask import g

import utilidades
from app import create_app
from models import db
from rutas import tutor

CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


class CompletarTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name, "GEMINI_API_KEY": "k"})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        c = self.c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": "ana@example.com", "password": "Clave123"}, headers=c.csrf)

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def pedir(self, datos):
        g.pop("_login_user", None)
        return self.c.post("/api/tutor/completar/", json=datos, headers=self.c.csrf)

    def test_devuelve_lo_que_va_en_el_cursor(self):
        respuesta = {"candidates": [{"content": {"parts": [{"text": "```js\n  return a + b;\n```"}]}}]}
        with mock.patch.object(tutor, "generar", return_value=(respuesta, "m")) as g_:
            r = self.pedir({"antes": "function suma(a, b) {\n", "despues": "\n}", "ruta": "app.js", "lenguaje": "javascript"})
        self.assertEqual(r.get_json()["texto"], "  return a + b;")
        self.assertIn("<CURSOR>", g_.call_args[0][0].decode())

    def test_sin_texto_no_llama_a_la_ia(self):
        with mock.patch.object(tutor, "generar") as g_:
            self.assertEqual(self.pedir({"antes": "   ", "despues": ""}).get_json()["texto"], "")
        g_.assert_not_called()

    def test_error_de_la_ia_no_rompe_el_editor(self):
        with mock.patch.object(tutor, "generar", side_effect=TimeoutError()):
            r = self.pedir({"antes": "const x = ", "despues": ""})
        self.assertEqual((r.status_code, r.get_json()["texto"]), (200, ""))


if __name__ == "__main__":
    unittest.main()
