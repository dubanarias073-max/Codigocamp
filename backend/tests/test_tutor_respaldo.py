"""Si Gemini está saturado (503) o sin cuota (429), la IA usa otro modelo en vez de fallar."""
import io
import json
import os
import unittest
import urllib.error

os.environ.setdefault("SECRET_KEY", "prueba")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import create_app  # noqa: E402
import rutas.tutor as tutor  # noqa: E402


class _R:
    def __init__(self, d): self.d = d
    def __enter__(self): return io.BytesIO(json.dumps(self.d).encode())
    def __exit__(self, *a): return False


class RespaldoGeminiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        tutor._descanso.clear(); tutor._modelo_que_funciona.clear()
        self.llamadas, self.original = [], tutor._peticion

    def tearDown(self):
        tutor._peticion = self.original
        tutor._descanso.clear(); tutor._modelo_que_funciona.clear()

    def _falso(self, codigos):
        def f(url, payload, h, metodo, timeout):
            m = url.split("/models/")[1].split(":")[0]
            self.llamadas.append(m)
            if m in codigos:
                raise urllib.error.HTTPError(url, codigos[m], "x", None, io.BytesIO(b"{}"))
            return _R({"candidates": [{"content": {"parts": [{"text": "hola"}]}}]})
        tutor._peticion = f

    def test_saturado_usa_otro_modelo_y_lo_deja_descansar(self):
        self._falso({"gemini-3.8-flash": 503})
        with self.app.app_context():
            self.assertEqual(tutor.generar(b"{}", "k", "gemini-3.8-flash")[1], "gemini-3.7-flash")
            self.llamadas.clear()
            self.assertEqual(tutor.generar(b"{}", "k", "gemini-3.8-flash")[1], "gemini-3.7-flash")
            self.assertNotIn("gemini-3.8-flash", self.llamadas)   # descansa: no se vuelve a pedir enseguida

    def test_sin_cuota_y_modelo_inexistente(self):
        self._falso({"gemini-3.8-flash": 429, "gemini-3.7-flash": 404})
        with self.app.app_context():
            self.assertEqual(tutor.generar(b"{}", "k", "gemini-3.8-flash")[1], "gemini-3.6-flash")

    def test_modelo_sin_thinking_se_reintenta_sin_el(self):
        vistos = []
        def f(url, payload, h, metodo, timeout):
            vistos.append(json.loads(payload))
            if "thinkingConfig" in vistos[-1].get("generationConfig", {}):
                raise urllib.error.HTTPError(url, 400, "x", None, io.BytesIO(b'{"error":{"message":"thinking_level is not supported"}}'))
            return _R({"candidates": [{"content": {"parts": [{"text": "hola"}]}}]})
        tutor._peticion = f
        cuerpo = json.dumps({"generationConfig": {"thinkingConfig": {"thinkingLevel": "low"}}}).encode()
        with self.app.app_context():
            self.assertEqual(tutor.generar(cuerpo, "k", "gemini-2.5-flash")[1], "gemini-2.5-flash")
        self.assertNotIn("thinkingConfig", vistos[-1]["generationConfig"])

    def test_todos_saturados_da_el_error(self):
        self._falso({m: 503 for m in tutor.MODELOS_RESPALDO})
        with self.app.app_context(), self.assertRaises(urllib.error.HTTPError) as e:
            tutor.generar(b"{}", "k", "gemini-3.8-flash")
        self.assertEqual(e.exception.code, 503)


if __name__ == "__main__":
    unittest.main()


class NivelPensarTest(unittest.TestCase):
    def test_simple_rapido_y_errores_piensan_mas(self):
        from rutas.tutor import nivel_pensar
        self.assertEqual(nivel_pensar("hola"), "minimal")
        self.assertEqual(nivel_pensar("por qué me sale TypeError en la línea 3"), "medium")
        self.assertEqual(nivel_pensar("cambia el color del botón", copiloto=True), "medium")
        self.assertEqual(nivel_pensar("refactoriza todo el proyecto", copiloto=True), "high")


class CursosNuevosTest(unittest.TestCase):
    def test_lua_y_r_en_el_catalogo(self):
        from retos import ORDEN, CURSOS_NUEVOS, errores_catalogo
        self.assertIn("lua", ORDEN); self.assertIn("r", ORDEN)
        self.assertIn("lua", CURSOS_NUEVOS); self.assertIn("r", CURSOS_NUEVOS)
        from retos import cargar_cursos
        todos = cargar_cursos()
        self.assertFalse(errores_catalogo({k: todos[k] for k in ("lua", "r")}))


class RespuestaEnVivoTest(unittest.TestCase):
    """La respuesta llega palabra por palabra; si el modelo principal falla antes de empezar, se usa uno de respaldo."""
    def setUp(self):
        self.app = create_app()
        self.app.config.update(GEMINI_API_KEY="k", TESTING=True)
        from models import db
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        tutor._descanso.clear(); tutor._modelo_que_funciona.clear()
        self.original = tutor._peticion

    def tearDown(self):
        self.ctx.pop()
        tutor._peticion = self.original
        tutor._descanso.clear(); tutor._modelo_que_funciona.clear()

    def _pedir(self):
        c = self.app.test_client()
        c.get("/api/auth/me/")
        token = c.get_cookie("csrftoken").value if c.get_cookie("csrftoken") else ""
        r = c.post("/api/tutor/", json={"mensaje": "hola", "stream": True}, headers={"X-CSRFToken": token})
        return r, [json.loads(b[5:]) for b in r.get_data(as_text=True).split("\n\n") if b.startswith("data:")]

    def test_trozos_en_vivo(self):
        class Sse:
            def __enter__(s): return s
            def __exit__(s, *a): return False
            def __iter__(s):
                for t in ("Ho", "la ", "mundo"):
                    yield f'data: {json.dumps({"candidates": [{"content": {"parts": [{"text": t}]}}]})}\n'.encode()
        tutor._peticion = lambda url, *a, **k: Sse()
        r, ev = self._pedir()
        self.assertIn("event-stream", r.content_type)
        self.assertEqual([e["t"] for e in ev if "t" in e], ["Ho", "la ", "mundo"])
        self.assertEqual(ev[-1]["respuesta"], "Hola mundo")

    def test_si_falla_antes_de_empezar_usa_respaldo(self):
        def f(url, *a, **k):
            if "streamGenerateContent" in url:
                raise urllib.error.HTTPError(url, 503, "x", None, io.BytesIO(b"{}"))
            return _R({"candidates": [{"content": {"parts": [{"text": "de respaldo"}]}}]})
        tutor._peticion = f
        r, ev = self._pedir()
        self.assertEqual(ev[-1].get("respuesta"), "de respaldo")


class CodiPiensaTest(unittest.TestCase):
    """Codi crea sus frases con la IA en el momento; si la IA no está, el navegador usa las de siempre."""
    def setUp(self):
        self.app = create_app()
        self.app.config.update(GEMINI_API_KEY="k", TESTING=True)
        from models import db
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.original = tutor._peticion

    def tearDown(self):
        self.ctx.pop(); tutor._peticion = self.original

    def test_frase_unica_con_animo_valido(self):
        visto = {}
        def f(url, payload, *a, **k):
            visto["prompt"] = json.loads(payload)["contents"][0]["parts"][0]["text"]
            return _R({"candidates": [{"content": {"parts": [{"text": '{"frase": "Hoy los bits huelen a café ☕", "animo": "raro"}'}]}}]})
        tutor._peticion = f
        c = self.app.test_client(); c.get("/api/auth/me/")
        r = c.post("/api/codi/pensar/", json={"motivo": "vida", "dichas": ["Hola"]}, headers={"X-CSRFToken": c.get_cookie("csrftoken").value})
        self.assertEqual(r.get_json(), {"frase": "Hoy los bits huelen a café ☕", "animo": "feliz"})
        self.assertIn("NO repitas", visto["prompt"])
