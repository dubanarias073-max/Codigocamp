"""Entrar con Google desde la app de Android: la app espera y entra sola aunque el navegador no vuelva a la app."""
import hashlib
import tempfile
import unittest

from flask import g

import utilidades
from app import create_app
from models import AppLoginCode, User, db

CHROME = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36 CodigoCampApp/2.0"


class AppGoogleTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": "ana@example.com", "password": "Clave123"}, headers=csrf)
        self.user = User.query.filter_by(email="ana@example.com").first()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def app_cliente(self):
        c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        return c

    def test_la_app_entra_sola_cuando_google_termina(self):
        secreto = "s" * 43
        app = self.app_cliente()
        g.pop("_login_user", None)
        self.assertFalse(app.post("/api/auth/app/esperar", json={"secreto": secreto}, headers=app.csrf).get_json()["listo"])
        # Google terminó en el navegador: el servidor guardó el código con la huella del secreto
        db.session.add(AppLoginCode(codigo_hash="x" * 64, usuario_id=self.user.id, espera_hash=hashlib.sha256(secreto.encode()).hexdigest()))
        db.session.commit()
        g.pop("_login_user", None)
        r = app.post("/api/auth/app/esperar", json={"secreto": secreto}, headers=app.csrf).get_json()
        self.assertTrue(r["listo"])
        g.pop("_login_user", None)
        self.assertEqual(app.get("/api/auth/me/").get_json()["user"]["email"], "ana@example.com")
        # un solo uso, y otro dispositivo con otro secreto no entra
        g.pop("_login_user", None)
        self.assertFalse(app.post("/api/auth/app/esperar", json={"secreto": secreto}, headers=app.csrf).get_json()["listo"])
        otro = self.app_cliente(); g.pop("_login_user", None)
        self.assertFalse(otro.post("/api/auth/app/esperar", json={"secreto": "t" * 43}, headers=otro.csrf).get_json()["listo"])
