"""Premios de racha: +1 salvarrachas cada 10 días (puede pasar de 2), semana perfecta y mes perfecto."""
import unittest
from datetime import date, timedelta
from unittest import mock

import servicios.zona as zona
from app import create_app
from models import DailyActivity, StreakReward, User, db
from servicios.perfil import award_xp, get_profile


class PremiosRachaTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        u = User(nombre="Ana", email="ana@example.com", password_hash="x")
        db.session.add(u); db.session.commit()
        self.p = get_profile(u); db.session.commit()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def practicar(self, dia):
        with mock.patch.object(zona, "hoy_de", lambda _p: dia):
            r = award_xp(self.p, 10)
        db.session.commit()
        return [x["clave"] for x in r]

    def test_cada_diez_dias_un_salvarrachas_aunque_pase_de_dos(self):
        self.p.salvarrachas = 2
        inicio = date(2026, 3, 2)   # lunes
        claves = []
        for i in range(30):
            claves += self.practicar(inicio + timedelta(days=i))
        self.assertEqual(self.p.racha_actual, 30)
        self.assertEqual(sum(1 for c in claves if c.startswith("racha")), 3)
        # 3 de los 10 días + 4 semanas perfectas (1 c/u) → 2 + 3 + 4 = 9
        self.assertEqual(sum(1 for c in claves if c.startswith("semana")), 4)
        self.assertEqual(self.p.salvarrachas, 9)

    def test_semana_perfecta_no_cuenta_si_uso_salvarrachas(self):
        self.p.salvarrachas = 1
        lunes = date(2026, 3, 9)
        claves = self.practicar(lunes - timedelta(days=1))   # domingo anterior
        for i in (0, 1, 2, 4, 5, 6):   # se salta el jueves: lo cubre un salvarrachas
            claves += self.practicar(lunes + timedelta(days=i))
        self.assertEqual(self.p.racha_actual, 7)
        self.assertFalse(any(c.startswith("semana") for c in claves))
        self.assertTrue(DailyActivity.query.filter_by(fecha=lunes + timedelta(days=3), salvada=True).first())

    def test_mes_perfecto_da_cofre_legendario_una_vez(self):
        claves = []
        for i in range(30):   # todo abril
            claves += self.practicar(date(2026, 4, 1) + timedelta(days=i))
        self.assertIn("mes-2026-04", claves)
        self.assertEqual(StreakReward.query.filter_by(clave="mes-2026-04").count(), 1)
        self.assertGreaterEqual(self.p.diamante, 2000)

    def test_mes_con_salvarrachas_no_es_perfecto(self):
        self.p.salvarrachas = 1
        claves = self.practicar(date(2026, 3, 31))   # racha que viene de marzo: llega a 30 aunque falte un día
        for i in range(30):
            if i == 15:
                continue
            claves += self.practicar(date(2026, 4, 1) + timedelta(days=i))
        self.assertEqual(self.p.racha_actual, 30)
        self.assertNotIn("mes-2026-04", claves)


if __name__ == "__main__":
    unittest.main()
