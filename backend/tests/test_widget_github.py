"""Widgets en cualquier sistema (enlace privado ?t=…) e «Iniciar sesión con GitHub» para git push."""
import unittest
from unittest import mock

import utilidades
from app import create_app
from models import db
from rutas import github


class Resp:
    def __init__(self, datos, estado=200):
        self._d, self.status_code = datos, estado

    def json(self):
        return self._d


class Base(unittest.TestCase):
    extra = {}

    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", **self.extra})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.csrf = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        r = self.c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": "a@example.com", "password": "Clave123"}, headers=self.csrf)
        self.assertIn(r.status_code, (200, 201), r.get_data(as_text=True))

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()


class WidgetTest(Base):
    def _anonimo(self):
        from flask import g
        g.pop("_login_user", None)   # la prueba comparte el contexto de la app: se olvida la sesión de setUp
        return self.app.test_client()

    def test_widgets_usan_la_sesion_abierta_hasta_que_se_cierre(self):
        e = self.c.get("/api/widget/conectar/").get_json()
        self.assertIn("/pages/widget.html?t=", e["pagina"])
        self.assertTrue(e["android"].startswith("intent://conectar?base="))
        self.assertEqual(self.c.get("/api/widget/conectar/").get_json()["token"], e["token"], "el token es estable para la sesión")
        # el script de Scriptable se descarga con la sesión, sin crear nada
        s = self.c.get("/api/widget/scriptable.js")
        self.assertEqual(s.status_code, 200)
        self.assertIn(e["token"], s.get_data(as_text=True))
        self.assertNotIn("__CC_", s.get_data(as_text=True))
        anonimo = self._anonimo()
        d = anonimo.get(f"/api/widget/?t={e['token']}")
        self.assertEqual(d.status_code, 200)
        self.assertEqual(d.get_json()["nombre"], "Ana")
        self.assertEqual(len(d.get_json()["semana"]), 7)
        # token alterado: no sirve
        self.assertEqual(anonimo.get(f"/api/widget/?t={e['token'][:-2]}xx").status_code, 401)
        # cerrar sesión apaga los widgets de esa sesión
        from flask import g
        g.pop("_login_user", None)
        self.assertEqual(self.c.post("/api/auth/logout/", json={}, headers=self.csrf).status_code, 200)
        self.assertEqual(self._anonimo().get(f"/api/widget/?t={e['token']}").status_code, 401)

    def test_sin_sesion_no_da_datos(self):
        anonimo = self._anonimo()
        self.assertEqual(anonimo.get("/api/widget/").status_code, 401)
        self.assertEqual(anonimo.get("/api/widget/?t=1." + "x" * 43).status_code, 401)
        self.assertEqual(anonimo.get("/api/widget/scriptable.js").status_code, 401)

    def test_con_sesion_sigue_funcionando_para_windows(self):
        r = self.c.get("/api/widget/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("semana_texto", r.get_json())

    def test_la_sesion_dura_hasta_cerrarla(self):
        self.assertGreaterEqual(self.app.config["REMEMBER_COOKIE_DURATION"].days, 365)
        self.assertTrue(self.app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"])


class GitHubSinConfigTest(Base):
    def test_sin_client_id_no_ofrece_oauth(self):
        with mock.patch.dict("os.environ", {"GITHUB_CLIENT_ID": "", "GITHUB_CLIENT_SECRET": ""}):
            r = self.c.get("/api/github/config/").get_json()
            self.assertEqual(r, {"web": False, "dispositivo": False, "configurado": False})
            self.assertEqual(self.c.post("/api/github/dispositivo/", json={}, headers=self.csrf).status_code, 503)


class GitHubTest(Base):
    extra = {"GITHUB_CLIENT_ID": "Iv1.prueba", "GITHUB_CLIENT_SECRET": "secreto"}

    def test_config(self):
        r = self.c.get("/api/github/config/").get_json()
        self.assertTrue(r["web"]); self.assertTrue(r["dispositivo"])

    def test_flujo_de_dispositivo(self):
        respuestas = [Resp({"device_code": "dc", "user_code": "ABCD-1234", "verification_uri": "https://github.com/login/device", "interval": 5, "expires_in": 900}),
                      Resp({"error": "authorization_pending"}), Resp({"access_token": "gho_x", "scope": "repo"})]
        with mock.patch.object(github.requests, "post", side_effect=respuestas) as post:
            d = self.c.post("/api/github/dispositivo/", json={}, headers=self.csrf).get_json()
            self.assertEqual(d["codigo"], "ABCD-1234")
            self.assertNotIn("device_code", d)
            p = self.c.post("/api/github/dispositivo/sondear/", json={"id": d["id"]}, headers=self.csrf).get_json()
            self.assertTrue(p["pendiente"])
            t = self.c.post("/api/github/dispositivo/sondear/", json={"id": d["id"]}, headers=self.csrf).get_json()
            self.assertEqual(t["token"], "gho_x")
            self.assertEqual(post.call_args.kwargs["data"]["device_code"], "dc")
        # ya usado: no se puede volver a sondear
        self.assertEqual(self.c.post("/api/github/dispositivo/sondear/", json={"id": d["id"]}, headers=self.csrf).status_code, 410)

    def test_ventana_emergente_valida_el_estado(self):
        r = self.c.get("/auth/github/?estado=abc123def456ghi7")
        self.assertEqual(r.status_code, 302)
        self.assertIn("github.com/login/oauth/authorize", r.headers["Location"])
        self.assertIn("scope=repo", r.headers["Location"])
        malo = self.c.get("/auth/github/callback/?state=otro&code=c")
        self.assertNotIn("gho_", malo.get_data(as_text=True))
        self.c.get("/auth/github/?estado=abc123def456ghi7")
        with mock.patch.object(github.requests, "post", return_value=Resp({"access_token": "gho_web", "scope": "repo"})):
            ok = self.c.get("/auth/github/callback/?state=abc123def456ghi7&code=c")
        html = ok.get_data(as_text=True)
        self.assertIn("gho_web", html)
        self.assertIn("BroadcastChannel", html)
        self.assertEqual(ok.headers["Cache-Control"], "no-store")
