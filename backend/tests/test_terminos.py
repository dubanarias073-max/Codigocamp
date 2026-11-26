"""Términos y condiciones: obligatorios en el onboarding y otra vez si cambia la versión."""
import unittest

import utilidades
from app import create_app
from models import Course, db
from servicios import terminos


class TerminosTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        if not Course.query.filter_by(slug="python").first():
            db.session.add(Course(slug="python", nombre="Python", sigla="PY", activo=True)); db.session.commit()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.csrf = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana", "email": "a@example.com", "password": "Clave123"}, headers=self.csrf)
        self.datos = {"rol": "estudiante", "intereses": ["web"], "nivel": "cero", "curso": "python", "meta": "10"}

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def yo(self):
        return self.c.get("/api/auth/me/").get_json()["user"]

    def test_version_sale_de_la_pagina(self):
        self.assertEqual(terminos.version_actual(), "2026-11-26")

    def test_onboarding_exige_aceptar(self):
        r = self.c.post("/api/perfil/", json=self.datos, headers=self.csrf)
        self.assertEqual(r.status_code, 400)
        self.assertIn("Términos", r.get_json()["error"])
        self.assertFalse(self.yo()["terminos"])
        r = self.c.post("/api/perfil/", json={**self.datos, "terminos": "2026-11-24"}, headers=self.csrf)
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))
        self.assertTrue(self.yo()["terminos"])

    def test_version_nueva_pide_aceptar_otra_vez(self):
        self.c.post("/api/perfil/", json={**self.datos, "terminos": "x"}, headers=self.csrf)
        self.assertTrue(self.yo()["terminos"])
        terminos._cache.update(mtime=-1, version="2099-01-01")
        orig = terminos.version_actual
        terminos.version_actual = lambda: "2099-01-01"
        try:
            self.assertFalse(self.yo()["terminos"])
            self.assertEqual(self.c.post("/api/terminos/aceptar/", json={}, headers=self.csrf).status_code, 400)
            self.assertEqual(self.c.post("/api/terminos/aceptar/", json={"acepto": True}, headers=self.csrf).status_code, 200)
            self.assertTrue(self.yo()["terminos"])
        finally:
            terminos.version_actual = orig
            terminos._cache["mtime"] = None
