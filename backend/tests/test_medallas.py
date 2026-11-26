"""Medallas del mes (como Duolingo): completar todas las experiencias del mes da la medalla, que sale en el perfil."""
import os
import unittest
from datetime import date

from app import create_app
from models import DailyActivity, DailyChallenge, Medal, User, db
from servicios.medallas import POOL, estado_del_mes, experiencias_del_mes, medallas_de, revisar_mes
from servicios.perfil import encargos_del_dia, get_profile


class MedallasTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.u = User(nombre="Ana", email="ana@example.com", password_hash="x")
        db.session.add(self.u); db.session.commit()
        self.p = get_profile(self.u); db.session.commit()
        os.environ["MEDALLAS_DESDE"] = "2026-01"   # estas pruebas usan noviembre de 2026 como mes con medalla

    def tearDown(self):
        os.environ.pop("MEDALLAS_DESDE", None)
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def test_antes_de_diciembre_de_2026_no_hay_medallas(self):
        """Las medallas del mes empiezan el 1 de diciembre de 2026: en noviembre no hay medalla ni experiencias."""
        os.environ.pop("MEDALLAS_DESDE")
        dia = date(2026, 11, 20)
        metas = {e["medida"]: e["meta"] for e in POOL}
        for i in range(1, 21):
            db.session.add(DailyActivity(usuario_id=self.u.id, fecha=dia.replace(day=i), xp=metas["xp"], niveles=metas["niveles"], perfectos=metas["perfectos"],
                                         lecciones=metas["lecciones"], mensajes=metas["mensajes"], ia=metas["ia"], ejecuciones=metas["ejecuciones"]))
        db.session.commit()
        e = estado_del_mes(self.u.id, dia)
        self.assertTrue(e["antes_de_inicio"])
        self.assertEqual(e["experiencias"], [])
        self.assertEqual((e["proxima"]["mes"], e["proxima"]["anio"]), ("diciembre", 2026))
        premios = revisar_mes(self.p, dia)
        self.assertFalse(any(x.get("medalla") or x["clave"].startswith("exp-") for x in premios))
        self.assertEqual(Medal.query.count(), 0)
        self.assertFalse(estado_del_mes(self.u.id, date(2026, 12, 3)).get("antes_de_inicio"))   # en diciembre sí empiezan

    def test_experiencias_iguales_para_todos_y_distintas_cada_mes(self):
        a, b = experiencias_del_mes(date(2026, 11, 5)), experiencias_del_mes(date(2026, 11, 28))
        self.assertEqual([e["clave"] for e in a], [e["clave"] for e in b])
        self.assertEqual(len(a), 4)
        self.assertEqual(a[0]["clave"], "desafio")
        distintos = {tuple(e["clave"] for e in experiencias_del_mes(date(2026, m, 1))) for m in range(1, 13)}
        self.assertGreater(len(distintos), 3)

    def test_completar_todo_da_la_medalla_una_sola_vez(self):
        dia = date(2026, 11, 20)
        diamantes = self.p.diamante
        metas = {e["medida"]: e["meta"] for e in POOL}
        for i in range(1, 21):   # 20 días de práctica con todo
            db.session.add(DailyActivity(usuario_id=self.u.id, fecha=dia.replace(day=i), xp=metas["xp"], niveles=metas["niveles"], perfectos=metas["perfectos"],
                                         lecciones=metas["lecciones"], mensajes=metas["mensajes"], ia=metas["ia"], ejecuciones=metas["ejecuciones"]))
        for i in range(1, 51):   # 50 encargos en el mes: llena la barra (y sus cofres) y la experiencia del desafío
            db.session.add(DailyChallenge(usuario_id=self.u.id, clave=f"x{i}", fecha=dia.replace(day=(i % 28) + 1)))
        db.session.commit()
        premios = revisar_mes(self.p, dia)
        db.session.commit()
        self.assertTrue(any(x.get("medalla") for x in premios))
        self.assertEqual(sum(1 for x in premios if x["clave"].startswith("exp-")), 4)
        self.assertEqual(sum(1 for x in premios if x["clave"].startswith("encmes-")), 4)   # cofres de 10, 20, 30 y 50 encargos
        self.assertEqual(sum(1 for x in premios if x["clave"].startswith("xpmes-")), 4)    # cofres de XP del mes
        self.assertGreater(self.p.diamante, diamantes + 500)
        self.assertEqual(revisar_mes(self.p, dia), [])          # no se repite
        self.assertEqual(Medal.query.count(), 1)
        m = medallas_de(self.u.id)[0]
        self.assertEqual((m["anio"], m["numero"]), (2026, 11))
        from servicios.medallas import diseno
        self.assertNotEqual(diseno(11, 2026)["nombre"], diseno(11, 2027)["nombre"])   # cada año, otra medalla
        self.assertTrue(estado_del_mes(self.u.id, dia)["ganada"])

    def test_siete_encargos_variados_por_dia(self):
        e = encargos_del_dia(self.u.id, date(2026, 11, 26))
        self.assertEqual(len(e), 7)
        self.assertEqual(len({x["clave"] for x in e}), 7)
        self.assertGreaterEqual(len({x["campo"] for x in e}), 5)

    def test_api_medallas_y_cofres_nuevos(self):
        c = self.app.test_client()
        c.get("/api/auth/me/")
        h = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": "Leo", "email": "leo@example.com", "password": "Clave123"}, headers=h)
        self.assertIn("disenos", c.get("/api/medallas/").get_json())
        d = c.get("/api/desafios/").get_json()
        self.assertEqual(len(d["hoy"]), 7)
        self.assertEqual(len(d["medalla"]["experiencias"]), 4)
        cofres = c.get("/api/cofres/").get_json()["cofres"]
        self.assertEqual(len(cofres), 45)


if __name__ == "__main__":
    unittest.main()


class MedallasEnChatsTest(unittest.TestCase):
    """En Chats se ven los detalles del amigo: nivel, racha, medallas y logros."""
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def cliente(self, email, nombre):
        c = self.app.test_client(); c.get("/api/auth/me/")
        c.h = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": nombre, "email": email, "password": "Clave123"}, headers=c.h)
        return c

    def test_perfil_del_amigo_con_medallas(self):
        from models import Friendship
        a, b = self.cliente("ana@example.com", "Ana"), self.cliente("leo@example.com", "Leo")
        ua, ub = User.query.filter_by(email="ana@example.com").one(), User.query.filter_by(email="leo@example.com").one()
        f = Friendship(de_usuario_id=ua.id, a_usuario_id=ub.id, estado="aceptada")
        db.session.add(f)
        for u in (ua, ub):
            db.session.add(Medal(usuario_id=u.id, clave="2026-10"))
        db.session.commit()
        lista = a.get("/api/amigos/").get_json()
        amigo = lista["amigos"][0]
        self.assertEqual((amigo["medallas"], amigo["nivel"]), (1, 1))
        p = a.get(f"/api/amigos/{f.id}/perfil/").get_json()
        self.assertEqual(p["medallas"][0]["numero"], 10)
        self.assertIn("logros_total", p); self.assertIn("encargos_total", p)
