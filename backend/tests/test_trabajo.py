import unittest
from unittest.mock import patch

from app import create_app
from models import User, UserWorkspace, db
from rutas.auth import oauth


class TrabajoAPITest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_COOKIE_SECURE": False,
            "GOOGLE_CLIENT_ID": "",
            "GOOGLE_CLIENT_SECRET": "",
        })
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.client.get("/api/auth/me/")
        self.csrf = {"X-CSRFToken": self.client.get_cookie("csrftoken").value}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def _registrar(self, client, email):
        client.get("/api/auth/me/")
        token = client.get_cookie("csrftoken").value
        response = client.post(
            "/api/auth/register/",
            json={"nombre": "Estudiante", "email": email, "password": "Clave123"},
            headers={"X-CSRFToken": token},
        )
        self.assertEqual(response.status_code, 201)

    def test_workspace_is_saved_and_private_to_each_account(self):
        self._registrar(self.client, "primero@example.com")
        project = {
            "files": {"index.html": "<h1>Hola</h1>"},
            "folders": ["src"],
            "git": {"initialized": True, "branch": "main", "staged": [], "tracked": []},
        }
        response = self.client.put("/api/trabajo/", json=project, headers=self.csrf)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/trabajo/").get_json()["proyecto"]["files"], project["files"])
        self.assertEqual(UserWorkspace.query.count(), 1)

        otro = self.app.test_client()
        self._registrar(otro, "segundo@example.com")
        self.assertIsNone(otro.get("/api/trabajo/").get_json()["proyecto"])

    def test_deleting_files_persists_even_when_project_becomes_empty(self):
        self._registrar(self.client, "borrador@example.com")
        completo = {"files": {"a.txt": "1", "src/b.js": "2"}, "folders": ["src"], "git": {}}
        self.assertEqual(self.client.put("/api/trabajo/", json=completo, headers=self.csrf).status_code, 200)
        menos = {"files": {"a.txt": "1"}, "folders": [], "git": {}}
        self.assertEqual(self.client.put("/api/trabajo/", json=menos, headers=self.csrf).status_code, 200)
        proyecto = self.client.get("/api/trabajo/").get_json()["proyecto"]
        self.assertEqual(proyecto["files"], {"a.txt": "1"})
        self.assertEqual(proyecto["folders"], [])
        vacio = {"files": {}, "folders": [], "git": {}}
        self.assertEqual(self.client.put("/api/trabajo/", json=vacio, headers=self.csrf).status_code, 200)
        proyecto = self.client.get("/api/trabajo/").get_json()["proyecto"]
        self.assertEqual(proyecto["files"], {})
        self.assertEqual(UserWorkspace.query.count(), 1)

    def test_responses_include_sync_mark_and_branches_are_kept(self):
        self._registrar(self.client, "marca@example.com")
        self.assertIsNone(self.client.get("/api/trabajo/").get_json()["actualizado"])
        git = {"initialized": True, "branch": "main", "branches": {"main": "abc1234", "dev": "abc1234"}}
        respuesta = self.client.put("/api/trabajo/", json={"files": {"a.txt": "1"}, "folders": [], "git": git}, headers=self.csrf)
        self.assertEqual(respuesta.status_code, 200)
        marca = respuesta.get_json()["actualizado"]
        self.assertTrue(marca)
        lectura = self.client.get("/api/trabajo/").get_json()
        self.assertEqual(lectura["actualizado"], marca)
        self.assertEqual(lectura["proyecto"]["git"]["branches"], git["branches"])

    def test_rejects_invalid_branches(self):
        self._registrar(self.client, "ramas@example.com")
        for malas in ({"mala rama": "abc"}, {"main": "NOHEX"}, "texto"):
            git = {"initialized": True, "branch": "main", "branches": malas}
            respuesta = self.client.put("/api/trabajo/", json={"files": {}, "folders": [], "git": git}, headers=self.csrf)
            self.assertEqual(respuesta.status_code, 400, malas)

    def test_rejects_traversal_and_google_shows_setup_hint(self):
        self._registrar(self.client, "estudiante@example.com")
        response = self.client.put(
            "/api/trabajo/",
            json={"files": {"../secreto": "no"}, "folders": []},
            headers=self.csrf,
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.get("/auth/google/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("google_config", response.location)

    def test_workspace_requires_login(self):
        response = self.app.test_client().get("/api/trabajo/")
        self.assertEqual(response.status_code, 401)

    def test_google_callback_creates_account_for_verified_email(self):
        app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_COOKIE_SECURE": False,
            "GOOGLE_CLIENT_ID": "test-client",
            "GOOGLE_CLIENT_SECRET": "test-secret",
        })
        with app.app_context():
            db.create_all()
            google = oauth.google
            with patch.object(google, "authorize_access_token", return_value={"access_token": "fake"}):
                with patch.object(google, "userinfo", return_value={
                    "sub": "google-subject",
                    "email": "google@example.com",
                    "email_verified": True,
                    "name": "Google User",
                }):
                    response = app.test_client().get("/auth/google/callback/")
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/pages/onboarding.html"))
            user = User.query.filter_by(email="google@example.com").one()
            self.assertEqual(user.google_id, "google-subject")
            self.assertIsNotNone(user.profile)
            db.drop_all()
            db.session.remove()
            db.engine.dispose()


if __name__ == "__main__":
    unittest.main()
