"""Versión 0.6: zona horaria del dispositivo, cerrar sesión de verdad (y correo al volver), avatares retirados,
estelas del dedo y la app de Android."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock
from zoneinfo import ZoneInfo

from flask import g

import utilidades
from app import create_app
from models import AppliedMigration, KnownDevice, Profile, Purchase, StoreItem, User, db
from servicios import zona

CHROME_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


class Base(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.correos = self.app.extensions.setdefault("correos_enviados", [])

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def cliente(self, ip="181.50.10.20", zona_h="America/Bogota"):
        c = self.app.test_client()
        c.environ_base.update(HTTP_USER_AGENT=CHROME_WIN, REMOTE_ADDR=ip, HTTP_X_ZONA_HORARIA=zona_h)
        c.get("/api/auth/me/")
        c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        return c

    def registrar(self, c, email="ana@example.com"):
        r = c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": email, "password": "Clave123"}, headers=c.csrf)
        self.assertIn(r.status_code, (200, 201), r.get_data(as_text=True))
        return User.query.filter_by(email=email).one()

    def entrar(self, c, email="ana@example.com"):
        g.pop("_login_user", None)
        r = c.post("/api/auth/login/", json={"email": email, "password": "Clave123"}, headers=c.csrf)
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))


class ZonaHorariaTest(Base):
    def test_valida(self):
        self.assertEqual(zona.valida("America/Bogota"), "America/Bogota")
        for malo in ("", "Marte/Olimpo", "../etc/passwd", "x" * 80):
            self.assertIsNone(zona.valida(malo))

    def test_se_guarda_la_zona_del_dispositivo_y_hoy_es_su_dia(self):
        c = self.cliente(zona_h="Asia/Tokyo")
        u = self.registrar(c)
        g.pop("_login_user", None)
        c.get("/api/auth/me/")
        perfil = Profile.query.filter_by(usuario_id=u.id).one()
        self.assertEqual(perfil.zona_horaria, "Asia/Tokyo")
        # Sin petición (correos, widgets): se usa la guardada
        with self.app.app_context():
            self.assertEqual(zona.hoy_de(perfil), datetime.now(ZoneInfo("Asia/Tokyo")).date())

    def test_las_fechas_van_con_zona(self):
        self.assertEqual(zona.iso(datetime(2026, 11, 21, 12, 0)), "2026-11-21T12:00:00+00:00")
        self.assertEqual(zona.hora_local(datetime(2026, 11, 21, 12, 0), type("P", (), {"zona_horaria": "America/Bogota"})()), "07:00")

    def test_las_sesiones_salen_con_zona(self):
        c = self.cliente()
        self.registrar(c)
        g.pop("_login_user", None)
        s = c.get("/api/sesiones/").get_json()["sesiones"][0]
        self.assertTrue(s["creada"].endswith("+00:00"), s["creada"])


class CerrarSesionTest(Base):
    def test_cerrar_en_todos_y_volver_avisa_por_correo(self):
        c = self.cliente()
        u = self.registrar(c)                  # correo de bienvenida
        n = len(self.correos)
        g.pop("_login_user", None)
        self.assertEqual(c.post("/api/auth/logout/", json={}, headers=c.csrf).status_code, 200)
        self.entrar(c)                        # cerrar sesión normal: mismo dispositivo conocido, sin correo
        self.assertEqual(len(self.correos), n)
        g.pop("_login_user", None)
        c.post("/api/sesiones/cerrar-todas/", json={}, headers=c.csrf)
        g.pop("_login_user", None)
        self.assertIsNone(c.get("/api/auth/me/").get_json()["user"], "cerró de verdad")
        self.assertEqual(KnownDevice.query.filter_by(usuario_id=u.id).count(), 0)
        self.entrar(c)
        self.assertEqual(len(self.correos), n + 1, "al volver a entrar llega «Nuevo inicio de sesión»")
        self.assertIn("Nuevo inicio de sesión", self.correos[-1]["asunto"] if isinstance(self.correos[-1], dict) else str(self.correos[-1]))

    def test_cerrar_aqui_desde_la_lista_y_el_widget_deja_de_servir(self):
        c = self.cliente()
        self.registrar(c)
        n = len(self.correos)
        g.pop("_login_user", None)
        token = c.get("/api/widget/conectar/").get_json()["token"]
        g.pop("_login_user", None)
        yo = next(s for s in c.get("/api/sesiones/").get_json()["sesiones"] if s["actual"])
        g.pop("_login_user", None)
        r = c.delete(f"/api/sesiones/{yo['id']}", headers=c.csrf).get_json()
        self.assertTrue(r["era_esta"])
        g.pop("_login_user", None)
        self.assertIsNone(c.get("/api/auth/me/").get_json()["user"])
        anon = self.app.test_client()
        g.pop("_login_user", None)
        self.assertEqual(anon.get(f"/api/widget/?t={token}").status_code, 401, "el token del widget murió con la sesión")
        self.entrar(c)
        self.assertEqual(len(self.correos), n + 1)


class AvataresYDedoTest(Base):
    def test_migracion_devuelve_diamantes_de_avatares(self):
        c = self.cliente()
        u = self.registrar(c)
        perfil = Profile.query.filter_by(usuario_id=u.id).one()
        item = StoreItem(clave="mascota_dragon", nombre="Avatar: Dragón", descripcion="", icono="dragon", moneda="diamante", precio=1400, categoria="diamante", orden=1, activo=True)
        db.session.add(item); db.session.flush()
        db.session.add(Purchase(usuario_id=u.id, articulo_id=item.id, precio=1400, moneda="diamante"))
        perfil.avatar, antes = "dragon", perfil.diamante
        hecha = db.session.get(AppliedMigration, "quitar_avatares")
        if hecha:
            db.session.delete(hecha)
        db.session.commit()
        from servicios.workbench import migraciones_de_datos
        self.assertIn("quitar_avatares", migraciones_de_datos(db))
        db.session.refresh(perfil)
        self.assertEqual(perfil.diamante, antes + 1400)
        self.assertIsNone(perfil.avatar)
        self.assertFalse(db.session.get(StoreItem, item.id).activo)

    def test_tienda_sin_avatares_y_con_estelas_del_dedo(self):
        c = self.cliente()
        u = self.registrar(c)
        Profile.query.filter_by(usuario_id=u.id).update({Profile.diamante: 5000}); db.session.commit()
        g.pop("_login_user", None)
        items = c.get("/api/tienda/").get_json()["items"]
        self.assertFalse([i for i in items if i["tipo"] == "avatar"])
        self.assertTrue([i for i in items if i["tipo"] == "dedo"])
        g.pop("_login_user", None)
        self.assertEqual(c.post("/api/tienda/comprar/", json={"clave": "dedo_neon"}, headers=c.csrf).status_code, 200)
        g.pop("_login_user", None)
        r = c.post("/api/cosmeticos/equipar/", json={"tipo": "dedo", "clave": "dedo_neon"}, headers=c.csrf)
        self.assertEqual(r.get_json()["equipados"]["dedo"], "dedo_neon")


class AppAndroidTest(Base):
    def test_sin_apk(self):
        with mock.patch("rutas.cosmeticos._apk", return_value=None):
            self.assertEqual(self.app.test_client().get("/api/app/").get_json()["android"], False)
