"""Contactos: el teléfono manda sha256 de correos; el servidor dice quiénes ya están en CódigoCamp."""
import hashlib
import tempfile
import unittest

from flask import g

import utilidades
from app import create_app
from models import db

CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
h = lambda correo: hashlib.sha256(correo.strip().lower().encode()).hexdigest()  # noqa: E731


class ContactosTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.ana, self.beto = self.cliente("ana@example.com", "Ana Ruiz"), self.cliente("Beto@Example.com", "Beto Gil")

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def cliente(self, email, nombre):
        c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": nombre, "email": email, "password": "Clave123"}, headers=c.csrf)
        g.pop("_login_user", None)
        return c

    def pedir(self, c, url, datos):
        g.pop("_login_user", None)
        return c.post(url, json=datos, headers=c.csrf)

    def test_encuentra_solo_a_quien_esta(self):
        r = self.pedir(self.ana, "/api/amigos/contactos/", {"hashes": [h("beto@example.com"), h("nadie@example.com"), h("ana@example.com"), "basura"]})
        self.assertEqual(r.status_code, 200)
        res = r.get_json()["resultados"]
        self.assertEqual([x["nombre"] for x in res], ["Beto Gil"])          # ni ella misma ni los que no existen
        self.assertTrue(res[0]["alias"]) and self.assertNotIn("email", res[0])

    def test_quien_no_quiere_no_aparece(self):
        self.assertEqual(self.pedir(self.beto, "/api/ajustes/", {"buscable_correo": False}).status_code, 200)
        r = self.pedir(self.ana, "/api/amigos/contactos/", {"hashes": [h("beto@example.com")]})
        self.assertEqual(r.get_json()["resultados"], [])

    def test_valida_entrada(self):
        self.assertEqual(self.pedir(self.ana, "/api/amigos/contactos/", {"hashes": "x"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
