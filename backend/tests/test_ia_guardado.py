"""Conversaciones con la IA: se guardan aunque la conexión se corte (en cualquier dispositivo se ven igual)."""
import json
import unittest
from unittest import mock

from flask import g

import utilidades
from app import create_app
from models import AIConversation, AIMessage, db
from rutas import tutor


class IAGuardadoTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        tutor._descanso.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "GEMINI_API_KEY": "k"})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.h = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana", "email": "ana@example.com", "password": "Clave123"}, headers=self.h)

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def enviar(self, datos, trozos=("Hola ", "Ana"), leer=True, completa_txt=None):
        def falso(*_a, **_k):
            yield from trozos
        g.pop("_login_user", None)
        completa = ({"candidates": [{"content": {"parts": [{"text": completa_txt or "".join(trozos)}]}}]}, "m")
        with mock.patch.object(tutor, "_trozos_gemini", side_effect=falso), mock.patch.object(tutor, "generar", return_value=completa):
            r = self.c.post("/api/tutor/", json={**datos, "stream": True}, headers=self.h, buffered=False)
            db.session.remove()   # como en el servidor real: la sesión de la vista se cierra antes de que salga la respuesta en vivo
            eventos = []
            it = iter(r.response)
            for bloque in it:
                for linea in bloque.decode().split("\n\n"):
                    if linea.startswith("data:"):
                        eventos.append(json.loads(linea[5:]))
                if not leer:   # el navegador se desconecta después del primer evento
                    r.close()
                    break
            return eventos

    def test_la_conversacion_llega_primero_y_se_guarda(self):
        ev = self.enviar({"mensaje": "¿Qué es Python?", "guardar": True})
        self.assertIn("conv", ev[0], "el id llega antes que la respuesta")
        self.assertTrue(ev[-1]["fin"])
        conv = db.session.get(AIConversation, ev[0]["conv"]["id"])
        self.assertEqual([(m.rol, m.texto) for m in conv.mensajes], [("yo", "¿Qué es Python?"), ("tutor", "Hola Ana")])

    def test_si_se_desconecta_la_respuesta_igual_se_guarda(self):
        ev = self.enviar({"mensaje": "Explícame los bucles", "guardar": True}, trozos=("Un ", "bucle ", "repite."), leer=False)
        cid = ev[0]["conv"]["id"]
        db.session.expire_all()
        textos = [(m.rol, m.texto) for m in AIMessage.query.filter_by(conversacion_id=cid).order_by(AIMessage.id)]
        self.assertEqual(textos, [("yo", "Explícame los bucles"), ("tutor", "Un bucle repite.")])

    def test_si_falla_la_pregunta_queda_y_reintentar_no_la_duplica(self):
        def falla(*_a, **_k):
            raise TimeoutError()
            yield  # noqa
        g.pop("_login_user", None)
        with mock.patch.object(tutor, "_trozos_gemini", side_effect=falla), mock.patch.object(tutor, "generar", side_effect=TimeoutError()):
            r = self.c.post("/api/tutor/", json={"mensaje": "¿Y los arreglos?", "guardar": True, "stream": True}, headers=self.h)
        eventos = [json.loads(x[5:]) for x in r.get_data(as_text=True).split("\n\n") if x.startswith("data:")]
        self.assertIn("error", eventos[-1])
        cid = eventos[0]["conv"]["id"]
        self.assertEqual([m.rol for m in db.session.get(AIConversation, cid).mensajes], ["yo"], "la pregunta no se pierde")
        ev = self.enviar({"mensaje": "¿Y los arreglos?", "conversacion_id": cid, "reintento": True}, trozos=("Son listas.",))
        self.assertTrue(ev[-1]["fin"])
        db.session.expire_all()
        self.assertEqual([(m.rol, m.texto) for m in db.session.get(AIConversation, cid).mensajes], [("yo", "¿Y los arreglos?"), ("tutor", "Son listas.")])

    def test_flujo_de_la_pagina_una_sola_conversacion_sin_repetidos(self):
        g.pop("_login_user", None)
        cid = self.c.post("/api/ia/conversaciones/", json={"titulo": "hola chat, ¿ahora sí está bien? 😅"}, headers=self.h).get_json()["conversacion"]["id"]
        self.enviar({"mensaje": "hola chat, ¿ahora sí está bien? 😅", "conversacion_id": cid})
        # la red mandó la misma pregunta otra vez (o doble clic) mientras no había respuesta: no se repite
        conv = db.session.get(AIConversation, cid)
        db.session.add(AIMessage(conversacion=conv, rol="yo", texto="otra")); db.session.commit()
        self.enviar({"mensaje": "otra", "conversacion_id": cid})
        db.session.expire_all()
        self.assertEqual([m.texto for m in db.session.get(AIConversation, cid).mensajes if m.rol == "yo"], ["hola chat, ¿ahora sí está bien? 😅", "otra"])
        self.assertEqual(AIConversation.query.count(), 1, "nunca se abren conversaciones repetidas")
        self.assertEqual(db.session.get(AIConversation, cid).titulo, "hola chat, ¿ahora sí está bien? 😅")

    def test_reintentar_despues_de_que_se_guardo_devuelve_esa_respuesta(self):
        ev = self.enviar({"mensaje": "¿Qué es una variable?", "guardar": True}, trozos=("Una caja.",))
        cid = ev[0]["conv"]["id"]
        llamadas = []
        def no_llamar(*_a, **_k):
            llamadas.append(1)
            yield "otra respuesta"
        g.pop("_login_user", None)
        with mock.patch.object(tutor, "_trozos_gemini", side_effect=no_llamar):
            r = self.c.post("/api/tutor/", json={"mensaje": "¿Qué es una variable?", "conversacion_id": cid, "reintento": True, "stream": True}, headers=self.h)
        eventos = [json.loads(x[5:]) for x in r.get_data(as_text=True).split("\n\n") if x.startswith("data:")]
        self.assertEqual((eventos[-1]["respuesta"], llamadas), ("Una caja.", []))
        self.assertEqual(len(db.session.get(AIConversation, cid).mensajes), 2)

    def test_si_el_modo_en_vivo_no_trae_texto_se_usa_la_respuesta_completa(self):
        ev = self.enviar({"mensaje": "Hola", "guardar": True}, trozos=(), completa_txt="¡Hola!")
        self.assertEqual(ev[-1].get("respuesta"), "¡Hola!", ev)

    def test_limpieza_junta_conversaciones_repetidas(self):
        from models import User
        from servicios.workbench import limpiar_conversaciones_repetidas
        uid = User.query.one().id
        buena = AIConversation(usuario_id=uid, titulo="hola")
        db.session.add(buena); db.session.flush()
        db.session.add_all([AIMessage(conversacion=buena, rol="yo", texto="hola"), AIMessage(conversacion=buena, rol="tutor", texto="¡Hola!")])
        for _ in range(4):
            c = AIConversation(usuario_id=uid, titulo="hola"); db.session.add(c); db.session.flush()
            db.session.add(AIMessage(conversacion=c, rol="yo", texto="hola"))
        otra = AIConversation(usuario_id=uid, titulo="otra cosa"); db.session.add(otra); db.session.flush()
        db.session.add(AIMessage(conversacion=otra, rol="yo", texto="otra cosa"))
        db.session.commit()
        self.assertEqual(limpiar_conversaciones_repetidas(), 4)
        db.session.commit()
        self.assertEqual(sorted(c.titulo for c in AIConversation.query.all()), ["hola", "otra cosa"])


if __name__ == "__main__":
    unittest.main()
