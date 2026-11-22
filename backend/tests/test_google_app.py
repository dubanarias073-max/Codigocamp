"""Entrar con Google desde la app de Android: el navegador vuelve a la app con un código de un solo uso."""
import re
import unittest
from datetime import timedelta
from unittest.mock import patch

from flask import g

from app import create_app
from models import AppLoginCode, User, db
from rutas.auth import oauth

APP_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36 CodigoCampApp/2.0"
CHROME_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36"
GOOGLE = {"sub": "sub-1", "email": "ana@example.com", "email_verified": True, "name": "Ana Ruiz"}


class GoogleAppTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "s", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "c", "GOOGLE_CLIENT_SECRET": "s"})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def navegador_con_google(self):
        """El navegador del celular: /auth/google/?app=1 y luego vuelve de Google."""
        nav = self.app.test_client()
        nav.environ_base.update(HTTP_USER_AGENT=CHROME_UA)
        with patch.object(oauth.google, "authorize_redirect", return_value=self.app.response_class("a google", 302, headers={"Location": "https://accounts.google.com/"})):
            nav.get("/auth/google/?app=1")
        with patch.object(oauth.google, "authorize_access_token", return_value={"access_token": "x"}), patch.object(oauth.google, "userinfo", return_value=GOOGLE):
            r = nav.get("/auth/google/callback/")
        return nav, r

    def test_el_navegador_devuelve_a_la_app_y_la_sesion_queda_en_la_app(self):
        nav, r = self.navegador_con_google()
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("intent://entrar?c=", html)
        self.assertIn("package=com.codigocamp.app", html)
        codigo = re.search(r"intent://entrar\?c=([A-Za-z0-9_-]+)", html).group(1)
        # el navegador NO queda con la sesión abierta
        g.pop("_login_user", None)
        self.assertIsNone(nav.get("/api/auth/me/").get_json()["user"])
        g.pop("_login_user", None)
        # la app abre el código: entra
        app = self.app.test_client()
        app.environ_base.update(HTTP_USER_AGENT=APP_UA)
        r = app.get(f"/api/auth/app/entrar?c={codigo}")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/pages/onboarding.html", r.location)
        g.pop("_login_user", None)
        self.assertEqual(app.get("/api/auth/me/").get_json()["user"]["email"], "ana@example.com")
        g.pop("_login_user", None)
        # y el widget de la app se puede conectar con esa sesión
        self.assertEqual(app.get("/api/widget/conectar/").status_code, 200)
        # un solo uso
        otra = self.app.test_client()
        g.pop("_login_user", None)
        r = otra.get(f"/api/auth/app/entrar?c={codigo}")
        self.assertIn("error=app", r.location)
        g.pop("_login_user", None)
        self.assertIsNone(otra.get("/api/auth/me/").get_json()["user"])

    def test_el_codigo_vence(self):
        _, r = self.navegador_con_google()
        codigo = re.search(r"intent://entrar\?c=([A-Za-z0-9_-]+)", r.get_data(as_text=True)).group(1)
        fila = AppLoginCode.query.one()
        fila.creado = fila.creado - timedelta(minutes=10)
        db.session.commit()
        r = self.app.test_client().get(f"/api/auth/app/entrar?c={codigo}")
        self.assertIn("error=app", r.location)
        self.assertIn("error=app", self.app.test_client().get("/api/auth/app/entrar?c=inventado123456789012345").location)

    def test_sin_app_entra_normal_en_el_navegador(self):
        nav = self.app.test_client()
        with patch.object(oauth.google, "authorize_redirect", return_value=self.app.response_class("", 302, headers={"Location": "https://accounts.google.com/"})):
            nav.get("/auth/google/")
        with patch.object(oauth.google, "authorize_access_token", return_value={"access_token": "x"}), patch.object(oauth.google, "userinfo", return_value=GOOGLE):
            r = nav.get("/auth/google/callback/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(nav.get("/api/auth/me/").get_json()["user"]["email"], "ana@example.com")
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(AppLoginCode.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
