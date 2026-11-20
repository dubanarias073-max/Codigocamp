import unittest

import utilidades
from app import create_app
from models import UserSession, db
from flask import g

CHROME_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SAFARI_IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


class SesionesTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def cliente(self, agente=CHROME_WIN):
        c = self.app.test_client()
        c.environ_base.update(HTTP_USER_AGENT=agente)
        c.get("/api/auth/me/")
        c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        return c

    def dentro(self, c):
        g.pop("_login_user", None)
        return c.get("/api/auth/me/").get_json()["user"] is not None

    def test_cerrar_en_un_dispositivo_y_en_todos(self):
        a = self.cliente()
        a.post("/api/auth/register/", json={"nombre": "Ana", "email": "ana@example.com", "password": "Clave123"}, headers=a.csrf)
        b = self.cliente(SAFARI_IPHONE)
        b.post("/api/auth/login/", json={"email": "ana@example.com", "password": "Clave123"}, headers=b.csrf)
        c = self.cliente()
        c.post("/api/auth/login/", json={"email": "ana@example.com", "password": "Clave123"}, headers=c.csrf)
        self.assertTrue(self.dentro(a) and self.dentro(b) and self.dentro(c))
        g.pop("_login_user", None)
        lista = a.get("/api/sesiones/").get_json()["sesiones"]
        self.assertEqual(len(lista), 3)
        self.assertEqual(sum(s["actual"] for s in lista), 1)
        iphone = next(s for s in lista if "iPhone" in s["dispositivo"])
        g.pop("_login_user", None)
        self.assertEqual(a.delete(f"/api/sesiones/{iphone['id']}", headers=a.csrf).status_code, 200)
        self.assertFalse(self.dentro(b), "el iPhone quedó fuera de verdad")
        self.assertTrue(self.dentro(a))
        # La cookie «recordarme» robada tampoco sirve
        b.delete_cookie("session")
        self.assertFalse(self.dentro(b))
        # Todos menos este
        g.pop("_login_user", None)
        r = a.post("/api/sesiones/cerrar-todas/", json={"excepto_este": True}, headers=a.csrf).get_json()
        self.assertEqual(r["cerradas"], 1)
        self.assertFalse(self.dentro(c))
        self.assertTrue(self.dentro(a))
        # Todos (incluido este)
        g.pop("_login_user", None)
        a.post("/api/sesiones/cerrar-todas/", json={}, headers=a.csrf)
        self.assertFalse(self.dentro(a))
        self.assertEqual(UserSession.query.filter_by(revocada=False).count(), 0)

    def test_salir_revoca_y_cambiar_clave_saca_a_los_demas(self):
        a = self.cliente()
        a.post("/api/auth/register/", json={"nombre": "Ana", "email": "ana@example.com", "password": "Clave123"}, headers=a.csrf)
        b = self.cliente(SAFARI_IPHONE)
        b.post("/api/auth/login/", json={"email": "ana@example.com", "password": "Clave123"}, headers=b.csrf)
        g.pop("_login_user", None)
        r = a.post("/api/auth/password/", json={"actual": "Clave123", "nueva": "Nueva123"}, headers=a.csrf).get_json()
        self.assertEqual(r["sesiones_cerradas"], 1)
        self.assertFalse(self.dentro(b))
        self.assertTrue(self.dentro(a))
        g.pop("_login_user", None)
        a.post("/api/auth/logout/", headers=a.csrf)
        self.assertEqual(UserSession.query.filter_by(revocada=False).count(), 0)


if __name__ == "__main__":
    unittest.main()
