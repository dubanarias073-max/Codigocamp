import unittest
from unittest import mock

import utilidades
from app import create_app
from models import db
from rutas import gitproxy


class Falsa:
    def __init__(self, estado=200, cuerpo=b"001e# service=git-upload-pack\n0000", cabeceras=None):
        self.status_code, self._c = estado, cuerpo
        self.headers = cabeceras or {"Content-Type": "application/x-git-upload-pack-advertisement"}
        self.cerrada = False

    def iter_content(self, n):
        yield self._c

    def close(self):
        self.cerrada = True


class GitProxyTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.csrf = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana", "email": "a@example.com", "password": "Clave123"}, headers=self.csrf)

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def test_reenvia_info_refs_y_upload_pack_con_el_token(self):
        with mock.patch.object(gitproxy.requests, "request", return_value=Falsa()) as req:
            r = self.c.get("/api/git/github.com/ana/repo.git/info/refs?service=git-upload-pack", headers={"Authorization": "Basic eDp5", "Cookie": "no"})
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.data, b"001e# service=git-upload-pack\n0000")
            args, kw = req.call_args
            self.assertEqual(args, ("GET", "https://github.com/ana/repo.git/info/refs?service=git-upload-pack"))
            self.assertEqual(kw["headers"]["Authorization"], "Basic eDp5")
            self.assertNotIn("Cookie", kw["headers"], "las cookies de CódigoCamp no salen hacia GitHub")
            r = self.c.post("/api/git/github.com/ana/repo.git/git-upload-pack", data=b"0032want x", headers={**self.csrf, "Content-Type": "application/x-git-upload-pack-request"})
            self.assertEqual(r.status_code, 200)
            self.assertEqual(req.call_args[0][0], "POST")

    def test_bloquea_hosts_rutas_y_metodos_no_permitidos(self):
        with mock.patch.object(gitproxy.requests, "request", return_value=Falsa()) as req:
            self.assertEqual(self.c.get("/api/git/169.254.169.254/latest/meta-data/info/refs?service=git-upload-pack").status_code, 403)
            self.assertEqual(self.c.get("/api/git/github.com/ana/repo.git/settings").status_code, 400)
            self.assertEqual(self.c.get("/api/git/github.com/ana/../repo.git/info/refs?service=git-upload-pack").status_code, 400)
            self.assertEqual(self.c.get("/api/git/github.com/ana/repo.git/info/refs?service=otro").status_code, 400)
            self.assertEqual(self.c.post("/api/git/github.com/ana/repo.git/git-upload-pack", data=b"x").status_code, 403, "sin CSRF")
            req.assert_not_called()

    def test_quita_www_authenticate_para_que_el_navegador_no_abra_su_ventana(self):
        with mock.patch.object(gitproxy.requests, "request", return_value=Falsa(401, b"", {"WWW-Authenticate": 'Basic realm="GitHub"'})):
            r = self.c.get("/api/git/github.com/ana/privado.git/info/refs?service=git-upload-pack")
            self.assertEqual(r.status_code, 401)
            self.assertNotIn("WWW-Authenticate", r.headers)
            self.assertEqual(r.headers["X-Git-Auth"], "required")

    def test_requiere_sesion(self):
        self.c.post("/api/auth/logout/", headers=self.csrf)
        self.assertEqual(self.c.get("/api/git/github.com/a/b.git/info/refs?service=git-upload-pack").status_code, 401)


if __name__ == "__main__":
    unittest.main()
