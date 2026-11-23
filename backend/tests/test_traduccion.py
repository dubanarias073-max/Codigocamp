"""Versión en inglés: los textos se traducen con la IA una sola vez y se guardan."""
import unittest
from unittest import mock

from app import create_app
from models import Traduccion, db


class TraduccionTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "GEMINI_API_KEY": "k",
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def test_traduce_una_vez_y_guarda(self):
        from servicios import traduccion
        llamadas = []

        def falsa(textos, idioma):
            llamadas.append(list(textos))
            return [f"EN:{t}" for t in textos]
        with mock.patch.object(traduccion, "_llamar_ia", falsa):
            r, n = traduccion.traducir(["¿Qué imprime este código?", "Elige la respuesta", "¿Qué imprime este código?", ""], "en")
            self.assertEqual(r, ["EN:¿Qué imprime este código?", "EN:Elige la respuesta", "EN:¿Qué imprime este código?", ""])
            self.assertEqual(n, 2)
            r2, n2 = traduccion.traducir(["Elige la respuesta"], "en")
        self.assertEqual(r2, ["EN:Elige la respuesta"])
        self.assertEqual(n2, 0)
        self.assertEqual(len(llamadas), 1)
        self.assertEqual(Traduccion.query.count(), 2)

    def test_sin_ia_devuelve_el_original(self):
        from servicios import traduccion
        with mock.patch.object(traduccion, "_llamar_ia", side_effect=ValueError("sin IA")):
            r, n = traduccion.traducir(["Hola"], "en")
        self.assertEqual((r, n), (["Hola"], 0))


if __name__ == "__main__":
    unittest.main()
