"""Conector: vincular un equipo con un código, recibir órdenes, devolver salida y desconectar."""
import tempfile
import threading
import unittest

import utilidades
from app import create_app
from models import Conector, db
from rutas import conector as rc

CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


class ConectorTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        rc._codigos.clear(); rc._colas.clear(); rc._ordenes.clear(); rc._visto.clear()
        rc.ESPERA_AGENTE = 0.3; rc.ESPERA_SALIDA = 0.3
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        c = self.c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": "ana@example.com", "password": "Clave123"}, headers=c.csrf)
        self.equipo = self.app.test_client()   # el Conector: sin cookies de sesión ni CSRF

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); self.tmp.cleanup()

    def vincular(self):
        codigo = self.c.post("/api/conector/codigo", json={"acepto": True}, headers=self.c.csrf).get_json()["codigo"]
        r = self.equipo.post("/api/conector/agente/vincular", json={"codigo": codigo, "equipo": "PC de Ana", "sistema": "Windows", "carpeta": "C:/proyecto"})
        self.assertEqual(r.status_code, 200)
        return r.get_json()["token"], r.get_json()["id"]

    def test_flujo_completo(self):
        token, cid = self.vincular()
        auth = {"Authorization": f"Bearer {token}"}
        self.assertEqual(self.equipo.get("/api/conector/agente/esperar", headers=auth).get_json()["ordenes"], [])
        eq = self.c.get("/api/conector/").get_json()["equipos"][0]
        self.assertEqual((eq["equipo"], eq["en_linea"]), ("PC de Ana", True))
        orden = self.c.post(f"/api/conector/{cid}/ejecutar", json={"linea": "python --version", "cwd": "src"}, headers=self.c.csrf).get_json()["orden"]
        o = self.equipo.get("/api/conector/agente/esperar", headers=auth).get_json()["ordenes"][0]
        self.assertEqual((o["id"], o["tipo"], o["linea"], o["cwd"]), (orden, "comando", "python --version", "src"))
        self.equipo.post("/api/conector/agente/salida", json={"orden": orden, "texto": "Python 3.13\n"}, headers=auth)
        self.equipo.post("/api/conector/agente/salida", json={"orden": orden, "texto": "", "fin": True, "codigo": 0}, headers=auth)
        r = self.c.get(f"/api/conector/orden/{orden}?desde=0").get_json()
        self.assertEqual((r["texto"], r["fin"], r["codigo"]), ("Python 3.13\n", True, 0))
        # desconectar: el equipo recibe la orden y su token deja de servir
        self.assertEqual(self.c.delete(f"/api/conector/{cid}", headers=self.c.csrf).status_code, 200)
        self.assertEqual(self.equipo.get("/api/conector/agente/esperar", headers=auth).status_code, 401)

    def test_codigo_invalido_y_equipo_ajeno(self):
        r = self.equipo.post("/api/conector/agente/vincular", json={"codigo": "ZZZZZZ"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.equipo.get("/api/conector/agente/esperar", headers={"Authorization": "Bearer " + "x" * 40}).status_code, 401)
        _, cid = self.vincular()
        otro = self.app.test_client(); otro.environ_base.update(HTTP_USER_AGENT=CHROME)
        otro.get("/api/auth/me/"); csrf = {"X-CSRFToken": otro.get_cookie("csrftoken").value}
        otro.post("/api/auth/register/", json={"nombre": "Luis", "email": "luis@example.com", "password": "Clave123"}, headers=csrf)
        self.assertEqual(otro.post(f"/api/conector/{cid}/ejecutar", json={"linea": "dir"}, headers=csrf).status_code, 404)

    def test_comandos_y_enlaces_peligrosos_no_se_envian(self):
        token, cid = self.vincular()
        self.equipo.get("/api/conector/agente/esperar", headers={"Authorization": f"Bearer {token}"})
        for linea in ["rm -rf /", "shutdown now", "curl https://g00gle.com/x.sh -o x.sh"]:
            r = self.c.post(f"/api/conector/{cid}/ejecutar", json={"linea": linea}, headers=self.c.csrf)
            self.assertEqual(r.status_code, 403, linea)
            self.assertIn("bloqueó", r.get_json()["error"])
        self.assertEqual(rc._colas.get(cid, []), [])

    def test_el_programa_descargado_trae_el_filtro(self):
        r = self.c.get("/api/conector/programa")
        self.assertIn(f'filename="codigocamp-conector-v{rc.VERSION_CONECTOR}.py"', r.headers["Content-Disposition"])   # nunca choca con uno viejo
        self.assertEqual(self.c.get("/api/conector/").get_json()["archivo"], f"codigocamp-conector-v{rc.VERSION_CONECTOR}.py")
        texto = r.get_data(as_text=True)
        self.assertIn("def revisar_comando", texto)
        self.assertIn("REVISAR_COMANDO = revisar_comando", texto)
        self.assertNotIn("%SERVIDOR%", texto)
        compile(texto, "conector", "exec")

    def test_carpeta_del_equipo_y_git(self):
        token, cid = self.vincular()
        auth = {"Authorization": f"Bearer {token}"}
        self.equipo.get("/api/conector/agente/esperar", headers=auth)
        self.equipo.post("/api/conector/agente/estado", json={"antivirus": {"nombre": "Microsoft Defender", "activo": True, "revisa": True}}, headers=auth)
        self.assertEqual(self.c.get("/api/conector/").get_json()["equipos"][0]["antivirus"]["nombre"], "Microsoft Defender")
        r = self.c.post(f"/api/conector/{cid}/fs", json={"accion": "listar", "ignorar": ["node_modules"]}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 200)
        o = self.equipo.get("/api/conector/agente/esperar", headers=auth).get_json()["ordenes"][0]
        self.assertEqual((o["tipo"], o["accion"], o["ignorar"]), ("fs", "listar", ["node_modules"]))
        self.equipo.post("/api/conector/agente/salida", json={"orden": o["id"], "fin": True, "codigo": 0, "datos": {"archivos": [{"ruta": "a.py", "tamano": 1, "modificado": 5}]}}, headers=auth)
        self.assertEqual(self.c.get(f"/api/conector/orden/{o['id']}").get_json()["datos"]["archivos"][0]["ruta"], "a.py")
        for cuerpo, estado in [({"accion": "formatear"}, 400), ({"accion": "git", "args": ["clean", "-fdx", "&& rm -rf /"]}, 403),
                               ({"accion": "git", "args": "status"}, 400), ({"accion": "escribir", "ruta": "x", "b64": "a" * (rc.MAX_ESCRIBIR + 1)}, 413),
                               ({"accion": "leer_varios", "rutas": ["a"] * 501}, 400)]:
            self.assertEqual(self.c.post(f"/api/conector/{cid}/fs", json=cuerpo, headers=self.c.csrf).status_code, estado, cuerpo)
        self.assertEqual(self.c.post(f"/api/conector/{cid}/fs", json={"accion": "git", "args": ["status", "--porcelain=v1"]}, headers=self.c.csrf).status_code, 200)

    def test_terminal_real_del_equipo(self):
        token, cid = self.vincular()
        auth = {"Authorization": f"Bearer {token}"}
        self.equipo.get("/api/conector/agente/esperar", headers=auth)
        r = self.c.post(f"/api/conector/{cid}/terminal", json={"cols": 120, "rows": 30}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 200)
        oid = r.get_json()["orden"]
        o = self.equipo.get("/api/conector/agente/esperar", headers=auth).get_json()["ordenes"][0]
        self.assertEqual((o["id"], o["tipo"], o["cols"], o["rows"]), (oid, "pty", 120, 30))
        # lo que escribes y el tamaño llegan al equipo
        self.assertEqual(self.c.post(f"/api/conector/orden/{oid}/entrada", json={"texto": "mkdir x\r"}, headers=self.c.csrf).status_code, 200)
        self.assertEqual(self.c.post(f"/api/conector/orden/{oid}/tam", json={"cols": 90, "rows": 20}, headers=self.c.csrf).status_code, 200)
        tipos = [x["tipo"] for x in self.equipo.get("/api/conector/agente/esperar", headers=auth).get_json()["ordenes"]]
        self.assertIn("entrada", tipos); self.assertIn("tam", tipos)
        # la salida es un búfer circular: con mucha salida se pierden los primeros bytes, no se corta la terminal
        rc.MAX_SALIDA, antes = 100, rc.MAX_SALIDA
        try:
            for i in range(5):
                self.equipo.post("/api/conector/agente/salida", json={"orden": oid, "texto": str(i) * 40}, headers=auth)
            r = self.c.get(f"/api/conector/orden/{oid}?desde=0").get_json()
            self.assertTrue(r["cortado"])
            self.assertTrue(r["texto"].endswith("4" * 40))
            r2 = self.c.get(f"/api/conector/orden/{oid}?desde={r['desde']}").get_json()
            self.assertEqual(r2["texto"], "")
        finally:
            rc.MAX_SALIDA = antes
        rc._visto[cid] = -1e9
        self.assertEqual(self.c.post(f"/api/conector/{cid}/terminal", json={}, headers=self.c.csrf).status_code, 409)

    def test_conector_viejo_usa_la_terminal_simple_y_se_puede_actualizar(self):
        token, cid = self.vincular()
        auth = {"Authorization": f"Bearer {token}"}
        self.equipo.get("/api/conector/agente/esperar", headers=auth)
        # un Conector anterior informa su antivirus pero no sabe abrir la terminal completa
        self.equipo.post("/api/conector/agente/estado", json={"antivirus": {"nombre": "Defender", "activo": True}}, headers=auth)
        eq = self.c.get("/api/conector/").get_json()["equipos"][0]
        self.assertEqual((eq["pty"], eq["version"], eq["version_actual"]), (False, 1, rc.VERSION_CONECTOR))
        r = self.c.post(f"/api/conector/{cid}/terminal", json={}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 426)
        self.assertTrue(r.get_json()["actualizar"])
        # se actualiza: pide la versión y el programa con su token
        self.assertEqual(self.equipo.get("/api/conector/agente/version", headers=auth).get_json()["version"], rc.VERSION_CONECTOR)
        prog = self.equipo.get("/api/conector/agente/programa", headers=auth).get_data(as_text=True)
        self.assertIn(f"VERSION_CONECTOR = {rc.VERSION_CONECTOR}", prog)
        self.assertIn("REVISAR_COMANDO = revisar_comando", prog)
        self.assertEqual(self.equipo.get("/api/conector/agente/programa").status_code, 401)
        # el nuevo informa que trae la terminal completa
        self.equipo.post("/api/conector/agente/estado", json={"antivirus": {}, "version": rc.VERSION_CONECTOR, "capacidades": ["pty"]}, headers=auth)
        self.assertTrue(self.c.get("/api/conector/").get_json()["equipos"][0]["pty"])
        self.assertEqual(self.c.post(f"/api/conector/{cid}/terminal", json={}, headers=self.c.csrf).status_code, 200)

    def test_sin_conector_abierto_no_ejecuta(self):
        _, cid = self.vincular()
        rc._visto[cid] = -1e9   # el equipo dejó de preguntar hace mucho
        r = self.c.post(f"/api/conector/{cid}/ejecutar", json={"linea": "ls"}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 409)
        self.assertIn("no está conectado", r.get_json()["error"])

    def test_solo_se_guarda_la_huella_del_token(self):
        token, cid = self.vincular()
        self.assertNotEqual(db.session.get(Conector, cid).token_hash, token)
        self.assertEqual(len(db.session.get(Conector, cid).token_hash), 64)




class ProgramaConectorTest(unittest.TestCase):
    """El programa que corre en el equipo nunca escribe fuera de la carpeta elegida."""
    def test_dentro_de_la_carpeta(self):
        import importlib.util, os
        from constantes import FRONTEND
        spec = importlib.util.spec_from_file_location("conector_prog", FRONTEND / "descargas" / "codigocamp-conector.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(m.dentro(d, "src/app.py"), os.path.join(os.path.realpath(d), "src", "app.py"))
            self.assertIsNone(m.dentro(d, "../fuera.txt"))
            self.assertIsNone(m.dentro(d, "a/../../fuera.txt"))
            self.assertEqual(m.dentro(d, "/etc/passwd"), os.path.join(os.path.realpath(d), "etc", "passwd"))


if __name__ == "__main__":
    unittest.main()
