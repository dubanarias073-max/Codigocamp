"""El nivel «actual» es el siguiente después del más avanzado (no te devuelve atrás si hay lecciones nuevas antes)."""
import tempfile
import unittest

from flask import g

import utilidades
from app import create_app
from models import CompletedLevel, Course, Level, Section, Stage, User, db
from servicios.retos import all_levels, allowed_level, estados_niveles

CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


class ActualTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": "ana@example.com", "password": "Clave123"}, headers=csrf)
        self.c, self.user = c, User.query.filter_by(email="ana@example.com").first()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def test_huecos_quedan_pendientes_y_actual_es_el_siguiente_al_mas_avanzado(self):
        curso = Course(slug="prueba-html", nombre="HTML de prueba", tipo="lenguaje", sigla="HT", color="#f97316", descripcion="", orden=99, activo=True)
        db.session.add(curso); db.session.flush()
        etapa = Stage(curso_id=curso.id, orden=1, titulo="Etapa 1", descripcion="")
        db.session.add(etapa); db.session.flush()
        for so in (1, 2):
            sec = Section(etapa_id=etapa.id, orden=so, titulo=f"Sección {so}")
            db.session.add(sec); db.session.flush()
            for lo in range(1, 5):
                db.session.add(Level(seccion_id=sec.id, orden=lo, titulo=f"L{so}.{lo}", tipo="leccion", xp=10))
        db.session.commit()
        niveles = all_levels(curso)
        # hizo 0..5 menos el 2 (como si el 2 fuera una lección nueva agregada después)
        for i in (0, 1, 3, 4, 5):
            db.session.add(CompletedLevel(usuario_id=self.user.id, nivel_id=niveles[i].id, estrellas=3))
        db.session.commit()
        e = estados_niveles(self.user, curso)
        self.assertEqual(e[niveles[2].id], "pendiente")
        self.assertEqual(e[niveles[6].id], "actual")
        self.assertEqual(e[niveles[7].id], "bloqueado")
        self.assertTrue(allowed_level(self.user, niveles[2]))
        self.assertTrue(allowed_level(self.user, niveles[6]))
        self.assertFalse(allowed_level(self.user, niveles[7]))
        g.pop("_login_user", None)
        r = self.c.get(f"/api/ruta/?curso={curso.slug}").get_json()
        estados = [n["estado"] for et in r["etapas"] for s in et["secciones"] for n in s["niveles"]]
        self.assertEqual(estados[:8], ["hecho", "hecho", "pendiente", "hecho", "hecho", "hecho", "actual", "bloqueado"])
