import unittest
from datetime import date, timedelta

import utilidades
from app import create_app
from models import EmailSettings, Profile, User, db
from servicios.correo import describir_dispositivo, huella_dispositivo, recordar_rachas

CHROME_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
SAFARI_IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


class CorreoTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.correos = self.app.extensions.setdefault("correos_enviados", [])

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def cliente(self, agente=CHROME_WIN, ip="181.50.10.20"):
        c = self.app.test_client()
        c.environ_base.update(HTTP_USER_AGENT=agente, REMOTE_ADDR=ip)
        c.get("/api/auth/me/")
        c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        return c

    def test_dispositivos(self):
        self.assertEqual(describir_dispositivo(CHROME_WIN), "Chrome en Windows")
        self.assertEqual(describir_dispositivo(SAFARI_IPHONE), "Safari en iPhone")
        self.assertEqual(huella_dispositivo(CHROME_WIN, "181.50.10.20"), huella_dispositivo(CHROME_WIN, "181.50.10.99"))
        self.assertNotEqual(huella_dispositivo(CHROME_WIN, "181.50.10.20"), huella_dispositivo(SAFARI_IPHONE, "181.50.10.20"))

    def test_aviso_de_nuevo_dispositivo_y_cambio_de_clave(self):
        a = self.cliente()
        a.post("/api/auth/register/", json={"nombre": "Ana Pérez", "email": "ana@example.com", "password": "Clave123"}, headers=a.csrf)
        self.assertEqual(len(self.correos), 1, "registrarse envía la bienvenida")
        self.assertIn("Bienvenido", self.correos[0]["asunto"])
        self.assertIn("Chrome en Windows", self.correos[0]["html"])
        self.correos.clear()
        b = self.cliente()  # mismo navegador y red
        b.post("/api/auth/login/", json={"email": "ana@example.com", "password": "Clave123"}, headers=b.csrf)
        self.assertEqual(self.correos, [], "el mismo dispositivo no avisa")
        c = self.cliente(SAFARI_IPHONE, "190.1.2.3")
        c.post("/api/auth/login/", json={"email": "ana@example.com", "password": "Clave123"}, headers=c.csrf)
        self.assertEqual(len(self.correos), 1)
        self.assertEqual(self.correos[0]["para"], "ana@example.com")
        self.assertIn("Nuevo inicio de sesión", self.correos[0]["asunto"])
        self.assertIn("Safari en iPhone", self.correos[0]["html"])
        # cambiar contraseña
        r = c.post("/api/auth/password/", json={"actual": "mala", "nueva": "Nueva123"}, headers=c.csrf)
        self.assertEqual(r.status_code, 400)
        r = c.post("/api/auth/password/", json={"actual": "Clave123", "nueva": "Nueva123"}, headers=c.csrf)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertIn("contraseña", self.correos[-1]["asunto"])
        # desactivar alertas
        r = c.post("/api/ajustes/correos/", json={"seguridad": False}, headers=c.csrf)
        self.assertFalse(r.get_json()["seguridad"])
        d = self.cliente("Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0", "10.0.0.1")
        d.post("/api/auth/login/", json={"email": "ana@example.com", "password": "Nueva123"}, headers=d.csrf)
        self.assertEqual(len(self.correos), 2, "con las alertas apagadas no se envía")
        j = d.get("/api/ajustes/correos/").get_json()
        self.assertEqual(len(j["dispositivos"]), 3)

    def test_recordatorio_de_racha(self):
        hoy = date(2026, 11, 19)
        for i, (racha, ultima) in enumerate([(5, hoy - timedelta(days=1)), (3, hoy), (2, hoy - timedelta(days=3)), (0, hoy - timedelta(days=1))]):
            u = User(email=f"u{i}@example.com", nombre=f"U{i}", password_hash="x")
            db.session.add(u); db.session.flush()
            db.session.add(Profile(user=u, racha_actual=racha, ultima_actividad=ultima, alias=f"u{i}x", codigo=f"C{i}"))
        db.session.commit()
        self.assertEqual(recordar_rachas(hoy), 1, "solo a quien practicó ayer y aún no hoy")
        self.assertIn("5 días", self.correos[0]["asunto"])
        self.assertIn("perderás tu racha", self.correos[0]["html"])
        self.assertEqual(recordar_rachas(hoy), 0, "una vez al día")
        self.assertEqual(recordar_rachas(hoy, nivel=2), 1, "aviso de última oportunidad")
        self.assertIn("medianoche", self.correos[1]["asunto"])
        self.assertEqual(recordar_rachas(hoy, nivel=2), 0)
        self.assertEqual(recordar_rachas(hoy, nivel=1), 0, "no se repite el de la tarde")
        db.session.get(EmailSettings, 1).racha = False
        db.session.commit()
        self.assertEqual(recordar_rachas(hoy + timedelta(days=0)), 0)


if __name__ == "__main__":
    unittest.main()
