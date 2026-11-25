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

    def test_todos_saturados_da_el_error(self):
        self._falso({m: 503 for m in tutor.MODELOS_RESPALDO})
        with self.app.app_context(), self.assertRaises(urllib.error.HTTPError) as e:
            tutor.generar(b"{}", "k", "gemini-3.8-flash")
        self.assertEqual(e.exception.code, 503)


if __name__ == "__main__":
    unittest.main()
