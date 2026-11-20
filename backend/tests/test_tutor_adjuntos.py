import io
import json
import shutil
import tempfile
import unittest
from unittest import mock

import utilidades
from flask import g
from app import create_app
from models import Friendship, User, db
from rutas import tutor as modulo

PNG = b"\x89PNG\r\n\x1a\n" + b"\x01" * 100


class Respuesta(io.BytesIO):
    headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


class TutorAdjuntosTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.dir = tempfile.mkdtemp()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": self.dir, "GEMINI_API_KEY": "k",
                               "CUOTA_ARCHIVOS": 10_000_000, "MAX_ARCHIVO": 5_000_000})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.a = self.cliente("ana@example.com", "Ana")

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop(); shutil.rmtree(self.dir, ignore_errors=True)

    def cliente(self, email, nombre):
        c = self.app.test_client()
        c.get("/api/auth/me/")
        c.h = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        c.post("/api/auth/register/", json={"nombre": nombre, "email": email, "password": "Clave123"}, headers=c.h)
        return c

    def adjunto(self, c, datos, nombre, destino):
        r = c.post(f"/api/trabajo/archivos/?nombre={nombre}", data=datos, headers={**c.h, "Content-Type": "application/octet-stream"})
        self.assertEqual(r.status_code, 201, r.get_json())
        r = c.post("/api/adjuntos/", json={"marcador": r.get_json()["marcador"], "nombre": nombre, "destino": destino}, headers=c.h)
        self.assertEqual(r.status_code, 201, r.get_json())
        return r.get_json()["adjunto"]

    def test_ia_recibe_imagen_codigo_contexto_y_copiloto(self):
        img = self.adjunto(self.a, PNG, "captura.png", "ia")
        cod = self.adjunto(self.a, b"print('hola')\n", "app.py", "ia")
        enviado = {}

        def falso(req, timeout=0):
            enviado["url"], enviado["cuerpo"] = req.full_url, json.loads(req.data)
            return Respuesta(json.dumps({"candidates": [{"content": {"parts": [{"text": "Listo"}]}}]}).encode())

        with mock.patch.object(modulo.urllib.request, "urlopen", side_effect=falso):
            r = self.a.post("/api/tutor/", json={"mensaje": "¿Qué falla?", "adjuntos": [img["id"], cod["id"]],
                                                  "contexto": {"pagina": "Trabajo", "copiloto": True, "archivos": ["app.py"], "archivo": {"ruta": "app.py", "contenido": "x = 1"}}}, headers=self.a.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertTrue(r.get_json()["copiloto"])
        partes = enviado["cuerpo"]["contents"][-1]["parts"]
        self.assertTrue(any("inline_data" in p and p["inline_data"]["mime_type"] == "image/png" for p in partes))
        self.assertTrue(any("print('hola')" in p.get("text", "") for p in partes))
        sistema = enviado["cuerpo"]["systemInstruction"]["parts"][0]["text"]
        self.assertIn("MODO COPILOTO", sistema)
        self.assertIn("Archivo abierto: app.py", sistema)
        self.assertIn("Se llama Ana", sistema)

    def test_chat_con_archivos_solo_lo_ven_los_dos(self):
        b = self.cliente("beto@example.com", "Beto")
        c = self.cliente("caro@example.com", "Caro")
        g.pop("_login_user", None)  # Flask-Login guarda el último usuario en g durante la prueba
        f = Friendship(de_usuario_id=1, a_usuario_id=2, estado="aceptada")
        db.session.add(f); db.session.commit()
        adj = self.adjunto(self.a, PNG, "foto.png", "chat")
        r = self.a.post(f"/api/chat/{f.id}/", json={"texto": "", "adjuntos": [adj["id"]]}, headers=self.a.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        msg = r.get_json()["mensajes"][-1]
        self.assertEqual(msg["adjuntos"][0]["clase"], "imagen")
        g.pop("_login_user", None)
        self.assertEqual(b.get(adj["url"]).status_code, 200, "el amigo lo ve")
        g.pop("_login_user", None)
        self.assertEqual(c.get(adj["url"]).status_code, 404, "otra persona no")
        g.pop("_login_user", None)
        self.assertEqual(self.a.post(f"/api/chat/{f.id}/", json={"texto": "otra vez", "adjuntos": [adj["id"]]}, headers=self.a.h).status_code, 400)
        # limpiar el proyecto no borra lo adjuntado
        from rutas.archivos import limpiar_huerfanas
        from datetime import timedelta
        from models import WorkspaceFile, utcnow
        WorkspaceFile.query.update({WorkspaceFile.creado_en: utcnow() - timedelta(days=2)}); db.session.commit()
        g.pop("_login_user", None)
        limpiar_huerfanas(1, {}, {})
        db.session.commit()
        g.pop("_login_user", None)
        self.assertEqual(b.get(adj["url"]).status_code, 200)


    def test_conversaciones_guardadas(self):
        recibido = []

        def falso(req, timeout=0):
            recibido.append(json.loads(req.data)["contents"])
            return Respuesta(json.dumps({"candidates": [{"content": {"parts": [{"text": f"Respuesta {len(recibido)}"}]}}]}).encode())

        with mock.patch.object(modulo.urllib.request, "urlopen", side_effect=falso):
            r = self.a.post("/api/tutor/", json={"mensaje": "¿Qué es una variable en Python?", "guardar": True}, headers=self.a.h).get_json()
            cid = r["conversacion"]["id"]
            self.assertEqual(r["conversacion"]["titulo"], "¿Qué es una variable en Python?")
            g.pop("_login_user", None)
            self.a.post("/api/tutor/", json={"mensaje": "Dame un ejemplo", "conversacion_id": cid}, headers=self.a.h)
        self.assertEqual(len(recibido[-1]), 3, "el servidor manda el historial de la conversación")
        g.pop("_login_user", None)
        lista = self.a.get("/api/ia/conversaciones/").get_json()["conversaciones"]
        self.assertEqual([c["id"] for c in lista], [cid])
        g.pop("_login_user", None)
        conv = self.a.get(f"/api/ia/conversaciones/{cid}").get_json()["conversacion"]
        self.assertEqual([m["rol"] for m in conv["mensajes"]], ["yo", "tutor", "yo", "tutor"])
        g.pop("_login_user", None)
        self.assertEqual(len(self.a.get("/api/ia/conversaciones/?q=ejemplo").get_json()["conversaciones"]), 1)
        g.pop("_login_user", None)
        self.a.patch(f"/api/ia/conversaciones/{cid}", json={"titulo": "Variables", "fijada": True}, headers=self.a.h)
        # Otra persona no la ve
        b = self.cliente("luis@example.com", "Luis")
        g.pop("_login_user", None)
        self.assertEqual(b.get(f"/api/ia/conversaciones/{cid}").status_code, 404)
        g.pop("_login_user", None)
        self.assertEqual(self.a.delete(f"/api/ia/conversaciones/{cid}", headers=self.a.h).status_code, 200)
        g.pop("_login_user", None)
        self.assertEqual(self.a.get("/api/ia/conversaciones/").get_json()["conversaciones"], [])

if __name__ == "__main__":
    unittest.main()
