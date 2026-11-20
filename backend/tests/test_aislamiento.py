"""Trabajo: una cuenta nunca recibe el proyecto, los commits ni los archivos de otra (ni tras reiniciar la base)."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import utilidades
from app import create_app
from models import UserWorkspace, db

PROYECTO = {"files": {"secreto.py": "print('de Ana')"}, "folders": [], "git": {"initialized": True, "branch": "main", "staged": [], "tracked": ["secreto.py"],
            "committed": {"secreto.py": "print('de Ana')"}, "commits": [], "remote": "", "branches": {}, "repos": {}}}


class AislamientoTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.dir = tempfile.mkdtemp()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.dir})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop()
        shutil.rmtree(self.dir, ignore_errors=True)

    def pedir(self, c, metodo, url, **kw):
        # Las pruebas comparten el contexto de la app: se olvida el usuario de la petición anterior.
        from flask import g
        g.pop("_login_user", None)
        return getattr(c, metodo)(url, **kw)

    def cliente(self, email):
        c = self.app.test_client()
        self.pedir(c, "get", "/api/auth/me/")
        h = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        self.assertEqual(c.post("/api/auth/register/", json={"nombre": "Prueba", "email": email, "password": "Clave123"}, headers=h).status_code, 201)
        return c, h

    def test_cada_cuenta_ve_solo_lo_suyo(self):
        ana, ha = self.cliente("ana@example.com")
        self.assertEqual(self.pedir(ana, "put", "/api/trabajo/", json=PROYECTO, headers=ha).status_code, 200)
        luis, _ = self.cliente("luis@example.com")
        self.assertIsNone(self.pedir(luis, "get", "/api/trabajo/").get_json()["proyecto"])
        self.assertIn("secreto.py", self.pedir(ana, "get", "/api/trabajo/").get_json()["proyecto"]["files"])
        self.assertNotIn("_dueno", self.pedir(ana, "get", "/api/trabajo/").get_json()["proyecto"])

    def test_base_reiniciada_no_hereda_disco(self):
        # Quedó en disco la carpeta del usuario 1 de una base anterior.
        viejo = Path(self.dir) / "1"
        viejo.mkdir(parents=True)
        (viejo / "proyecto.json").write_text(json.dumps({**PROYECTO, "_dueno": "1:2020-01-01T00:00:00"}), encoding="utf-8")
        c, _ = self.cliente("nuevo@example.com")   # recibe el id 1
        self.assertFalse(viejo.exists())
        self.assertIsNone(self.pedir(c, "get", "/api/trabajo/").get_json()["proyecto"])

    def test_marca_de_otra_cuenta_no_se_entrega(self):
        c, h = self.cliente("ana@example.com")
        self.pedir(c, "put", "/api/trabajo/", json=PROYECTO, headers=h)
        ruta = Path(self.dir) / "1" / "proyecto.json"
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        datos["_dueno"] = "1:1999-01-01T00:00:00"
        ruta.write_text(json.dumps(datos), encoding="utf-8")
        self.assertIsNotNone(UserWorkspace.query.first())
        self.assertIsNone(self.pedir(c, "get", "/api/trabajo/").get_json()["proyecto"])


if __name__ == "__main__":
    unittest.main()


class CofreDelCaminoTest(unittest.TestCase):
    """Los cofres de cada sección del camino dan premios de verdad (no solo XP)."""

    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.dir = tempfile.mkdtemp()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.dir})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        from models import Course, Level, Section, Stage
        curso = Course(slug="zz", nombre="Prueba", sigla="ZZ"); db.session.add(curso); db.session.flush()
        etapa = Stage(curso_id=curso.id, orden=1, titulo="E1"); db.session.add(etapa); db.session.flush()
        sec = Section(etapa_id=etapa.id, orden=3, titulo="S"); db.session.add(sec); db.session.flush()
        self.cofre = Level(seccion_id=sec.id, orden=1, titulo="Cofre", tipo="cofre", xp=20); db.session.add(self.cofre)
        db.session.commit()

    def tearDown(self):
        db.session.remove(); db.drop_all(); self.ctx.pop()
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_cofre_da_diamantes_y_un_extra_una_sola_vez(self):
        from flask import g
        from models import Profile
        c = self.app.test_client(); c.get("/api/auth/me/"); h = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": "Prueba", "email": "a@example.com", "password": "Clave123"}, headers=h)
        antes = Profile.query.first().diamante
        g.pop("_login_user", None)
        r = c.post(f"/api/nivel/{self.cofre.id}/completar/", json={"fallos": 0}, headers=h).get_json()
        tipos = [p["tipo"] for p in r["premios"]]
        self.assertEqual(tipos[0], "diamante")
        self.assertGreaterEqual(r["premios"][0]["cantidad"], 40)
        self.assertEqual(len(tipos), 2 if tipos[-1] in {"salvarrachas", "vidas"} else 1)
        self.assertEqual(r["minerales_ganados"]["diamante"], r["premios"][0]["cantidad"])
        db.session.expire_all()
        self.assertEqual(Profile.query.first().diamante - antes, r["premios"][0]["cantidad"])
        g.pop("_login_user", None)
        otra = c.post(f"/api/nivel/{self.cofre.id}/completar/", json={"fallos": 0}, headers=h).get_json()
        self.assertEqual(otra["premios"], [])   # abrirlo otra vez no da más
