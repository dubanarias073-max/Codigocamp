"""«Saltar aquí»: examen de lo anterior a una sección o etapa bloqueada."""
import unittest

from flask import g

import utilidades
from app import create_app
from models import Challenge, CompletedLevel, Course, Level, Profile, Section, Stage, User, db


class SaltoTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        c = Course(slug="py", nombre="Python", tipo="lenguaje", sigla="PY", color="#60a5fa", descripcion="", orden=1, activo=True)
        db.session.add(c); db.session.flush()
        self.secciones = []
        for e in range(1, 3):
            st = Stage(curso_id=c.id, orden=e, titulo=f"Etapa {e}", descripcion="")
            db.session.add(st); db.session.flush()
            for s in range(1, 3):
                sec = Section(etapa_id=st.id, orden=s, titulo=f"S{e}.{s}")
                db.session.add(sec); db.session.flush()
                self.secciones.append(sec)
                for n in range(1, 3):
                    lv = Level(seccion_id=sec.id, orden=n, titulo=f"L{e}.{s}.{n}", tipo="leccion", xp=10)
                    db.session.add(lv); db.session.flush()
                    for k in range(1, 4):
                        db.session.add(Challenge(nivel_id=lv.id, orden=k, tipo="opcion", enunciado=f"¿{lv.titulo}-{k}?",
                                                 opciones=["si", "no"], respuesta="si", explicacion="x"))
        db.session.commit()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.h = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana", "email": "ana@example.com", "password": "Clave123"}, headers=self.h)
        self.uid = User.query.one().id

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def get(self, url):
        g.pop("_login_user", None)
        return self.c.get(url)

    def post(self, url, datos=None):
        g.pop("_login_user", None)
        return self.c.post(url, json=datos or {}, headers=self.h)

    def test_aprobar_salta_a_la_etapa(self):
        etapa2 = Stage.query.filter_by(orden=2).one()
        r = self.get(f"/api/salto/etapa/{etapa2.id}/")
        self.assertEqual(r.status_code, 200, r.get_json())
        ex = r.get_json()
        self.assertEqual((ex["examen"]["total"], ex["examen"]["tolerancia"]), (12, 2))   # 12 retos antes de la etapa 2
        primera_etapa = {lv.id for sec in self.secciones[:2] for lv in sec.niveles}
        self.assertTrue(all(Challenge.query.get(x["id"]).nivel_id in primera_etapa for x in ex["retos"]), "solo temas anteriores")
        vidas_antes = Profile.query.one().vidas
        for i, x in enumerate(ex["retos"]):
            r = self.post(f"/api/reto/{x['id']}/responder/?salto=1", {"respuesta": "no" if i < 2 else "si"})
            self.assertEqual(r.status_code, 200, r.get_json())
        self.assertEqual(Profile.query.one().vidas, vidas_antes, "el examen no gasta vidas")
        fin = self.post("/api/salto/terminar/").get_json()
        self.assertTrue(fin["aprobado"])
        self.assertEqual(fin["desbloqueados"], 4)
        ruta = self.get("/api/ruta/?curso=py").get_json()
        self.assertEqual(ruta["etapas"][1]["secciones"][0]["niveles"][0]["estado"], "actual")

    def test_reprobar_no_desbloquea_y_no_se_puede_hacer_trampa(self):
        sec = self.secciones[1]   # S1.2: antes solo están los 6 retos de S1.1
        ex = self.get(f"/api/salto/seccion/{sec.id}/").get_json()
        self.assertEqual(ex["examen"]["tolerancia"], 1)
        for x in ex["retos"]:
            self.post(f"/api/reto/{x['id']}/responder/?salto=1", {"respuesta": "no"})
            self.post(f"/api/reto/{x['id']}/responder/?salto=1", {"respuesta": "si"})   # el segundo intento no cuenta
        self.assertFalse(self.post("/api/salto/terminar/").get_json()["aprobado"])
        self.assertEqual(CompletedLevel.query.count(), 0)
        # Sin examen activo, terminar no aprueba nada; y sin «?salto=1» un nivel bloqueado sigue bloqueado
        self.assertEqual(self.post("/api/salto/terminar/").status_code, 400)
        bloqueado = sec.niveles[0].retos[0]
        self.assertEqual(self.post(f"/api/reto/{bloqueado.id}/responder/", {"respuesta": "si"}).status_code, 403)

    def test_no_hace_falta_examen_si_ya_puedes_entrar(self):
        self.assertEqual(self.get(f"/api/salto/seccion/{self.secciones[0].id}/").status_code, 400)


if __name__ == "__main__":
    unittest.main()
