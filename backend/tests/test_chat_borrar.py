"""Chats: eliminar un mensaje para todos (solo quien lo mandó)."""
import tempfile
import unittest

from flask import g

import utilidades
from app import create_app
from models import Friendship, Message, User, db

CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


class ChatBorrarTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.ana, self.beto = self.cliente("ana@example.com", "Ana Ruiz"), self.cliente("beto@example.com", "Beto Gil")
        a, b = User.query.filter_by(email="ana@example.com").first(), User.query.filter_by(email="beto@example.com").first()
        self.f = Friendship(de_usuario_id=a.id, a_usuario_id=b.id, estado="aceptada")
        db.session.add(self.f); db.session.commit()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def cliente(self, email, nombre):
        c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": nombre, "email": email, "password": "Clave123"}, headers=c.csrf)
        g.pop("_login_user", None)
        return c

    def pedir(self, c, metodo, url, **kw):
        g.pop("_login_user", None)
        return getattr(c, metodo)(url, headers=c.csrf, **kw)

    def test_eliminar_para_todos(self):
        r = self.pedir(self.ana, "post", f"/api/chat/{self.f.id}/", json={"texto": "contraseña: 1234 (ups)"}).get_json()
        mid = r["mensajes"][-1]["id"]
        # Beto no puede borrar el mensaje de Ana
        self.assertEqual(self.pedir(self.beto, "delete", f"/api/chat/{self.f.id}/{mid}/").status_code, 403)
        r = self.pedir(self.ana, "delete", f"/api/chat/{self.f.id}/{mid}/")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["mensaje"]["borrado"])
        self.assertEqual(db.session.get(Message, mid).texto, "")          # el texto se borró de verdad
        vista = self.pedir(self.beto, "get", f"/api/chat/{self.f.id}/").get_json()
        m = next(x for x in vista["mensajes"] if x["id"] == mid)
        self.assertTrue(m["borrado"]); self.assertEqual(m["texto"], "")
        self.assertIn(mid, vista["borrados"])                               # para quitarlo de la pantalla de Beto
        lista = self.pedir(self.beto, "get", "/api/amigos/").get_json()
        self.assertIn("eliminado", str(lista))
