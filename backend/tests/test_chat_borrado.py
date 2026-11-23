"""«Eliminar chat» solo para quien lo borra: la otra persona conserva su historial."""
import tempfile
import unittest

from flask import g

import utilidades
from app import create_app
from models import ChatBorrado, Friendship, Message, User, db

CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


class ChatBorradoTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.ana, self.beto = self.cliente("Ana Ruiz", "ana@example.com"), self.cliente("Beto Paz", "beto@example.com")
        a, b = User.query.filter_by(email="ana@example.com").one(), User.query.filter_by(email="beto@example.com").one()
        f = Friendship(de_usuario_id=a.id, a_usuario_id=b.id, estado="aceptada")
        db.session.add(f); db.session.commit()
        self.fid = f.id

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def cliente(self, nombre, email):
        c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": nombre, "email": email, "password": "Clave123"}, headers=c.csrf)
        g.pop("_login_user", None)
        original = c.open

        def abrir(*a, **kw):   # el contexto de la app guarda el último usuario: se limpia en cada pedido
            g.pop("_login_user", None)
            return original(*a, **kw)
        c.open = abrir
        return c

    def enviar(self, c, texto):
        self.assertEqual(c.post(f"/api/chat/{self.fid}/", json={"texto": texto}, headers=c.csrf).status_code, 200)

    def textos(self, c):
        return [m["texto"] for m in c.get(f"/api/chat/{self.fid}/").get_json()["mensajes"]]

    def test_borrar_solo_para_mi(self):
        self.enviar(self.ana, "hola"); self.enviar(self.beto, "qué tal")
        self.assertEqual(self.ana.delete(f"/api/chat/{self.fid}/", headers=self.ana.csrf).status_code, 200)
        self.assertEqual(self.textos(self.ana), [])
        self.assertEqual(self.textos(self.beto), ["hola", "qué tal"])          # Beto conserva todo
        amigo = self.ana.get("/api/amigos/").get_json()["amigos"][0]
        self.assertEqual((amigo["ultimo"], amigo["no_leidos"]), ("", 0))
        self.enviar(self.beto, "¿sigues?")                                       # lo nuevo sí le llega a Ana
        self.assertEqual(self.textos(self.ana), ["¿sigues?"])
        self.assertEqual(Message.query.count(), 3)

    def test_si_los_dos_borran_se_elimina_de_verdad(self):
        self.enviar(self.ana, "uno"); self.enviar(self.beto, "dos")
        self.ana.delete(f"/api/chat/{self.fid}/", headers=self.ana.csrf)
        self.assertEqual(Message.query.count(), 2)
        self.enviar(self.ana, "tres")
        self.beto.delete(f"/api/chat/{self.fid}/", headers=self.beto.csrf)
        self.assertEqual([m.texto for m in Message.query.all()], ["tres"])       # «tres» aún lo ve Ana
        self.assertEqual(self.textos(self.ana), ["tres"])
        self.assertEqual(ChatBorrado.query.count(), 2)

    def test_chat_ajeno(self):
        otro = self.cliente("Caro Gil", "caro@example.com")
        self.assertEqual(otro.delete(f"/api/chat/{self.fid}/", headers=otro.csrf).status_code, 404)


if __name__ == "__main__":
    unittest.main()
