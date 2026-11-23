"""Canal WebSocket del Conector: autenticado con el token, el servidor empuja las órdenes y la salida vuelve por el mismo canal."""
import importlib.util
import json
import tempfile
import threading
import unittest
from pathlib import Path

import utilidades
from app import create_app
from models import db
from rutas import conector as rc

RUTA = Path(__file__).resolve().parents[2] / "frontend" / "descargas" / "codigocamp-conector.py"
CHROME = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


@unittest.skipIf(rc.sock is None, "flask-sock no está instalado")
class ConectorWebSocketTest(unittest.TestCase):
    def setUp(self):
        from werkzeug.serving import make_server
        utilidades._RATE_LIMITS.clear()
        rc._codigos.clear(); rc._colas.clear(); rc._ordenes.clear(); rc._visto.clear()
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name) / "cc.db"
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": f"sqlite:///{base}", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.tmp.name})
        with self.app.app_context():
            db.create_all()
        self.servidor = make_server("127.0.0.1", 0, self.app, threaded=True)
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.servidor.server_port}"
        c = self.c = self.app.test_client(); c.environ_base.update(HTTP_USER_AGENT=CHROME)
        c.get("/api/auth/me/"); c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": "Ana Ruiz", "email": "ana@example.com", "password": "Clave123"}, headers=c.csrf)
        spec = importlib.util.spec_from_file_location("conector_ws", RUTA)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)

    def tearDown(self):
        self.servidor.shutdown()
        with self.app.app_context():
            db.session.remove(); db.drop_all(); db.engine.dispose()
        self.tmp.cleanup()

    def test_ordenes_y_salida_por_websocket(self):
        sin_acepto = self.c.post("/api/conector/codigo", json={}, headers=self.c.csrf)
        self.assertEqual(sin_acepto.status_code, 400)   # primero hay que aceptar las condiciones del Conector
        codigo = self.c.post("/api/conector/codigo", json={"acepto": True}, headers=self.c.csrf).get_json()["codigo"]
        estado, r = self.m.pedir(self.url, "POST", "/api/conector/agente/vincular", datos={"codigo": codigo, "equipo": "PC", "sistema": "Linux", "carpeta": "/p"})
        self.assertEqual(estado, 200)
        malo = self.m.CanalWS(self.url, "x" * 40)   # sin token válido: el servidor avisa y cierra, no envía órdenes
        self.assertEqual(json.loads(malo.recibir())["codigo"], 401)
        malo.cerrar()
        ws = self.m.CanalWS(self.url, r["token"])
        cid = r["id"]
        orden = self.c.post(f"/api/conector/{cid}/ejecutar", json={"linea": "python --version"}, headers=self.c.csrf).get_json()["orden"]
        msg = json.loads(ws.recibir())
        self.assertEqual((msg["tipo"], msg["ordenes"][0]["id"], msg["ordenes"][0]["linea"]), ("ordenes", orden, "python --version"))
        ws.enviar(json.dumps({"tipo": "salida", "orden": orden, "texto": "Python 3.13\n" + "x" * 70000, "fin": True, "codigo": 0}))
        ws.enviar(json.dumps({"tipo": "estado", "antivirus": {"nombre": "ClamAV", "activo": True, "revisa": True}}))
        r = self.c.get(f"/api/conector/orden/{orden}?desde=0").get_json()
        self.assertTrue(r["texto"].startswith("Python 3.13"))
        self.assertTrue(r["fin"])
        eq = self.c.get("/api/conector/").get_json()["equipos"][0]
        self.assertTrue(eq["en_linea"])
        # desconectar desde Trabajo: la orden llega por el canal
        self.c.delete(f"/api/conector/{cid}", headers=self.c.csrf)
        self.assertEqual(json.loads(ws.recibir())["ordenes"][0]["tipo"], "desconectar")
        ws.cerrar()


if __name__ == "__main__":
    unittest.main()
