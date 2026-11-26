"""Banco de muestras: el antivirus debe atrapar TODAS las peligrosas y dejar pasar TODO el código normal de estudiantes."""
import os
import tempfile
import unittest

from servicios.antivirus import revisar_archivo_completo, revisar_texto
from servicios.muestras_antivirus import NORMALES, PELIGROSAS


def revisar(nombre, datos):
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, "subida.bin")
        with open(ruta, "wb") as f:
            f.write(datos)
        return revisar_archivo_completo(ruta, nombre, aprender=False)   # sin aprender: cada capa debe detectar por sí sola


class MuestrasTest(unittest.TestCase):
    def test_atrapa_todas_las_peligrosas_al_subirlas(self):
        fallan = [f"{n}: {q}" for n, d, q in PELIGROSAS if not revisar(n, d)]
        self.assertEqual(fallan, [], "no se detectaron")

    def test_no_bloquea_codigo_normal(self):
        falsos = [f"{n}: {revisar(n, d)['motivo']}" for n, d in NORMALES if revisar(n, d)]
        self.assertEqual(falsos, [], "falsos positivos")

    def test_tambien_en_el_editor(self):
        texto = [(n, d.decode("utf-8")) for n, d, _ in PELIGROSAS if _es_texto(d)]
        fallan = [n for n, t in texto if not revisar_texto(n, t)]
        self.assertEqual(fallan, [])
        falsos = [n for n, d in NORMALES if _es_texto(d) and revisar_texto(n, d.decode("utf-8"))]
        self.assertEqual(falsos, [])


def _es_texto(d):
    try:
        d.decode("utf-8")
        return b"\x00" not in d
    except UnicodeDecodeError:
        return False


if __name__ == "__main__":
    unittest.main()
