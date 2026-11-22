import shutil
import tempfile
import unittest

import utilidades
from app import create_app
from models import LessonDone, Course, Profile, db

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


class CosmeticosTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.dir = tempfile.mkdtemp()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.dir})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        import servicios.tienda as t
        t._ITEMS_LISTOS = False
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.h = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana", "email": "a@example.com", "password": "Clave123"}, headers=self.h)

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); shutil.rmtree(self.dir, ignore_errors=True)

    def test_comprar_y_equipar_un_fondo(self):
        t = self.c.get("/api/tienda/").get_json()
        fondo = next(i for i in t["items"] if i["clave"] == "fondo_matrix")
        self.assertEqual(fondo["tipo"], "fondo")
        self.assertFalse(any(i["clave"] == "fondo_dragon" for i in t["items"]), "los exclusivos no se venden")
        r = self.c.post("/api/cosmeticos/equipar/", json={"tipo": "fondo", "clave": "fondo_matrix"}, headers=self.h)
        self.assertEqual(r.status_code, 403, "no se puede equipar lo que no tienes")
        Profile.query.first().diamante = 5000; db.session.commit()
        r = self.c.post("/api/tienda/comprar/", json={"clave": "fondo_matrix"}, headers=self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(self.c.post("/api/tienda/comprar/", json={"clave": "fondo_matrix"}, headers=self.h).status_code, 400)
        r = self.c.post("/api/cosmeticos/equipar/", json={"tipo": "fondo", "clave": "fondo_matrix"}, headers=self.h)
        self.assertEqual(r.get_json()["equipados"]["fondo"], "fondo_matrix")
        self.assertEqual(self.c.get("/api/auth/me/").get_json()["user"]["cosmeticos"]["fondo"], "fondo_matrix")
        self.assertEqual(self.c.post("/api/cosmeticos/equipar/", json={"tipo": "cursor", "clave": "fondo_matrix"}, headers=self.h).status_code, 400)
        r = self.c.post("/api/cosmeticos/equipar/", json={"tipo": "fondo", "clave": None}, headers=self.h)
        self.assertIsNone(r.get_json()["equipados"]["fondo"])

    def test_cofres(self):
        j = self.c.get("/api/cofres/").get_json()
        self.assertGreaterEqual(len(j["cofres"]), 10)
        self.assertFalse(j["cofres"][0]["listo"])
        self.assertEqual(self.c.post("/api/cofres/abrir/", json={"clave": "c01_primer_paso"}, headers=self.h).status_code, 403)
        curso = Course(slug="html", nombre="HTML", tipo="web", sigla="HTML"); db.session.add(curso); db.session.flush()
        db.session.add(LessonDone(usuario_id=1, curso_id=curso.id, leccion="l1"))
        p = Profile.query.first(); p.racha_maxima = 3; db.session.commit()
        r = self.c.post("/api/cofres/abrir/", json={"clave": "c01_primer_paso"}, headers=self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(r.get_json()["premio"]["diamante"], 50)
        self.assertEqual(self.c.post("/api/cofres/abrir/", json={"clave": "c01_primer_paso"}, headers=self.h).status_code, 409)
        r = self.c.post("/api/cofres/abrir/", json={"clave": "c02_racha3"}, headers=self.h)
        self.assertEqual(r.get_json()["premio"]["cosmeticos"][0]["clave"], "cursor_estrella")
        r = self.c.post("/api/cosmeticos/equipar/", json={"tipo": "cursor", "clave": "cursor_estrella"}, headers=self.h)
        self.assertEqual(r.status_code, 200, "el exclusivo del cofre se puede equipar")

    def test_foto_de_perfil(self):
        self.assertEqual(self.c.post("/api/perfil/foto/", data=b"<svg onload=x>", headers=self.h).status_code, 400)
        r = self.c.post("/api/perfil/foto/", data=PNG, headers={**self.h, "Content-Type": "application/octet-stream"})
        self.assertEqual(r.status_code, 200, r.get_json())
        url = r.get_json()["foto"]
        self.assertTrue(url.startswith("/api/perfil/foto/1?v="))
        f = self.c.get(url)
        self.assertEqual((f.status_code, f.mimetype), (200, "image/png"))
        self.assertIn("sandbox", f.headers["Content-Security-Policy"])
        self.assertEqual(self.c.get("/api/auth/me/").get_json()["user"]["foto"], url)
        self.c.delete("/api/perfil/foto/", headers=self.h)
        self.assertEqual(self.c.get(url).status_code, 404)


if __name__ == "__main__":
    unittest.main()
