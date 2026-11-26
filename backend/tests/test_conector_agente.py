"""El programa Conector (lo que corre en el equipo del estudiante): carpetas permitidas, antivirus del equipo y Git."""
import base64
import importlib.util
import os
import stat
import tempfile
import unittest
from pathlib import Path

RUTA = Path(__file__).resolve().parents[2] / "frontend" / "descargas" / "codigocamp-conector.py"
EICAR = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$" + b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
FALSO_CLAMSCAN = """#!/bin/sh
for f in "$@"; do case "$f" in --*) ;; *) if grep -q "EICAR-STANDARD" "$f" 2>/dev/null; then echo "$f: Eicar-Test-Signature FOUND"; exit 1; fi;; esac; done
exit 0
"""


@unittest.skipIf(os.name == "nt", "las pruebas usan un antivirus falso de shell")
class AgenteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.casa = Path(self.tmp.name) / "casa"
        self.bin = Path(self.tmp.name) / "bin"
        (self.casa / "proyecto" / "src").mkdir(parents=True)
        (self.casa / ".ssh").mkdir()
        self.bin.mkdir()
        av = self.bin / "clamscan"
        av.write_text(FALSO_CLAMSCAN)
        av.chmod(av.stat().st_mode | stat.S_IEXEC)
        self.entorno = {k: os.environ.get(k) for k in ("HOME", "PATH")}
        os.environ["HOME"] = str(self.casa)
        os.environ["PATH"] = f"{self.bin}{os.pathsep}{os.environ['PATH']}"
        spec = importlib.util.spec_from_file_location("conector_agente", RUTA)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.m.CONFIG = str(Path(self.tmp.name) / "config.json")
        self.proyecto = str(self.casa / "proyecto")
        self.a = self.m.Agente("http://x", "t" * 40, self.proyecto)

    def tearDown(self):
        for k, v in self.entorno.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def test_carpetas_del_sistema_y_secretos_nunca(self):
        m = self.m
        for r in ["/etc", "/usr/lib", str(self.casa / ".ssh")]:
            self.assertFalse(m.permitida(r), r)
        self.assertFalse(m.elegible(str(self.casa)))   # toda la carpeta personal: no
        self.assertFalse(m.elegible("/"))
        self.assertTrue(m.elegible(self.proyecto))
        self.assertEqual(self.a.fs_explorar({"ruta": "/etc"})["ruta"], os.path.realpath(self.casa))
        with self.assertRaises(m.ErrorFs):
            self.a.fs_raiz({"ruta": "/etc"})
        with self.assertRaises(m.ErrorFs):
            self.a.fs_leer({"ruta": "../../etc/passwd"})
        self.assertNotIn(".ssh", self.a.fs_explorar({"ruta": str(self.casa)})["carpetas"])

    def test_cliente_http_desde_el_equipo(self):
        """El cliente HTTP de Trabajo llega a la API que corre en el equipo (localhost) a través del Conector."""
        import http.server
        import threading

        class Api(http.server.BaseHTTPRequestHandler):
            def log_message(self, *x):
                pass

            def do_POST(self):
                datos = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                self.send_response(201); self.send_header("Content-Type", "application/json"); self.end_headers()
                self.wfile.write(b'{"eco": ' + datos + b', "token": "' + (self.headers.get("Authorization") or "").encode() + b'"}')

            def do_GET(self):
                self.send_response(404); self.end_headers(); self.wfile.write(b"no existe")
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Api)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            url = f"http://127.0.0.1:{srv.server_address[1]}"
            r = self.a.fs_http({"metodo": "POST", "url": url + "/items", "cabeceras": [["Content-Type", "application/json"], ["Authorization", "Bearer x"]],
                                "cuerpo_b64": base64.b64encode(b'{"a": 1}').decode()})
            self.assertEqual((r["status"], base64.b64decode(r["cuerpo_b64"])), (201, b'{"eco": {"a": 1}, "token": "Bearer x"}'))
            self.assertEqual(self.a.fs_http({"metodo": "GET", "url": url + "/nada"})["status"], 404, "los errores HTTP también son respuestas")
        finally:
            srv.shutdown()
        with self.assertRaises(self.m.ErrorFs):
            self.a.fs_http({"metodo": "GET", "url": "file:///etc/passwd"})
        with self.assertRaises(self.m.ErrorFs):
            self.a.fs_http({"metodo": "GET", "url": "http://127.0.0.1:1/"})   # nada escuchando: mensaje claro

    def test_archivos_de_la_carpeta(self):
        a = self.a
        r = a.fs_escribir({"ruta": "src/app.py", "b64": base64.b64encode(b"print(1)\n").decode()})
        lista = a.fs_listar({})
        self.assertEqual([(x["ruta"], x["modificado"]) for x in lista["archivos"]], [("src/app.py", r["modificado"])])
        self.assertEqual(base64.b64decode(a.fs_leer({"ruta": "src/app.py"})["b64"]), b"print(1)\n")
        a.fs_borrar({"ruta": "src/app.py"})
        self.assertFalse(os.path.exists(os.path.join(self.proyecto, "src")))   # la carpeta vacía también se va

    def test_no_revisa_archivos_ni_comandos_solo_carpetas_del_sistema(self):
        """Con tu equipo, CódigoCamp no revisa archivos (lo hace tu antivirus en tiempo real): solo frena comandos
        destructivos y carpetas del sistema."""
        a, m = self.a, self.m
        self.assertEqual(a.av.estado()["herramienta"], "clamav")      # informa qué antivirus tienes
        a.fs_escribir({"ruta": "programa.exe", "b64": base64.b64encode(b"MZ\x00datos").decode()})
        self.assertTrue(Path(self.proyecto, "programa.exe").exists())   # se guarda directo, sin esperas
        self.assertIsNone(m.REVISAR_COMANDO)   # en su equipo no se filtran comandos (la persona es responsable)
        self.assertFalse(m.elegible("C:\\Windows\\System32" if os.name == "nt" else "/etc"))

    def test_archivos_grandes_por_partes(self):
        a, m = self.a, self.m
        m.PARTE = 1000   # partes chiquitas para la prueba
        datos = os.urandom(3500)
        Path(self.proyecto, "video.bin").write_bytes(datos)
        m.MAX_LEER = 2000
        with self.assertRaises(m.ErrorFs) as e:
            a.fs_leer({"ruta": "video.bin"})
        self.assertTrue(e.exception.extra.get("grande"))
        leido, desde = b"", 0
        while True:
            r = a.fs_leer_parte({"ruta": "video.bin", "desde": desde})
            parte = base64.b64decode(r["b64"]); leido += parte; desde += len(parte)
            if r["fin"]:
                break
        self.assertEqual(leido, datos)
        for i in range(0, len(datos), 1000):   # y de vuelta, por partes
            r = a.fs_escribir_parte({"ruta": "copia.bin", "desde": i, "b64": base64.b64encode(datos[i:i + 1000]).decode(), "fin": i + 1000 >= len(datos)})
        self.assertEqual(Path(self.proyecto, "copia.bin").read_bytes(), datos)
        self.assertEqual(r["tamano"], 3500)
        self.assertFalse(Path(self.proyecto, "copia.bin.ccparcial").exists())

    def test_terminal_real_crea_carpetas_sin_filtro(self):
        import queue, time
        a = self.a
        salida = queue.Queue()
        a.salida = lambda orden, texto="", fin=False, codigo=0, datos=None: salida.put((texto, fin, datos))
        a.pty({"id": "p1", "cols": 80, "rows": 24})
        texto, fin, datos = "", False, None
        def leer(hasta, s=8):
            nonlocal texto, fin, datos
            limite = time.time() + s
            while time.time() < limite and hasta not in texto and not fin:
                try:
                    t, f, d = salida.get(timeout=0.3)
                    texto += t; fin = fin or f; datos = d or datos
                except queue.Empty:
                    pass
        time.sleep(0.5)
        a.entrada({"id": "p1", "texto": "mkdir -p nueva/sub && echo hola > nueva/sub/a.txt && echo $((40+2))OK\r"})
        leer("42OK")
        self.assertTrue(Path(self.proyecto, "nueva", "sub", "a.txt").exists(), texto)
        a.entrada({"id": "p1", "texto": "echo $((6*7))SINFILTRO\r"})   # nada se bloquea en la terminal del equipo
        leer("42SINFILTRO")
        self.assertIn("42SINFILTRO", texto)
        self.assertNotIn("bloque", texto)
        a.detener({"id": "p1"})
        leer("__nada__", 5)
        self.assertTrue(fin)

    def test_abrir_una_carpeta_no_llama_al_antivirus(self):
        """Como VS Code: abrir y leer la carpeta no llama al antivirus (lo hace el del equipo en tiempo real)."""
        llamadas = Path(self.tmp.name) / "llamadas"
        av = self.bin / "clamscan"
        av.write_text(f'#!/bin/sh\necho x >> "{llamadas}"\n' + FALSO_CLAMSCAN.split("\n", 1)[1])
        for i in range(30):
            Path(self.proyecto, f"img{i}.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00" + bytes([i]))
        a = self.m.Agente("http://x", "t" * 40, self.proyecto)
        r = a.fs_leer_varios({"rutas": [f"img{i}.png" for i in range(30)]})["archivos"]
        self.assertFalse(llamadas.exists())          # ninguna revisión extra: rápido
        self.assertIn("b64", r["img3.png"])
        self.assertFalse(self.m.elegible(os.path.dirname(str(self.casa))))   # la carpeta de todas las cuentas (C:\\Users), tampoco

    def test_listar_solo_manda_los_cambios(self):
        """Como el vigilante de VS Code: tras la primera vez, solo viaja lo que cambió."""
        a = self.a
        r1 = a.fs_listar({})
        r2 = a.fs_listar({"previo": r1["token"]})
        self.assertTrue(r2["cambios"])
        self.assertEqual((r2["archivos"], r2["borrados"]), ([], []))
        Path(self.proyecto, "nuevo.txt").write_text("hola")
        r3 = a.fs_listar({"previo": r2["token"]})
        self.assertEqual([x["ruta"] for x in r3["archivos"]], ["nuevo.txt"])
        os.remove(Path(self.proyecto, "nuevo.txt"))
        self.assertEqual(a.fs_listar({"previo": r3["token"]})["borrados"], ["nuevo.txt"])
        self.assertNotIn("cambios", a.fs_listar({"previo": "viejo"}))   # token desconocido: lista completa

    def test_carpetas_pesadas_se_ven_pero_se_leen_al_abrirlas(self):
        """Como VS Code: node_modules y venv aparecen, su contenido solo cuando las abres; .git no aparece."""
        for d in ("node_modules/react", "venv/lib", ".git/objects"):
            os.makedirs(Path(self.proyecto, d), exist_ok=True)
        Path(self.proyecto, "node_modules/react/index.js").write_text("x")
        r = self.a.fs_listar({"ignorar": ["node_modules", "venv", ".git"]})
        self.assertIn("node_modules", r["carpetas"]); self.assertIn("venv", r["carpetas"])
        self.assertFalse(any(c.startswith(".git") for c in r["carpetas"]))
        self.assertIn("node_modules", r["pesadas"])
        self.assertNotIn("node_modules/react/index.js", [x["ruta"] for x in r["archivos"]])
        r = self.a.fs_listar({"ignorar": ["node_modules"], "abrir": ["node_modules", "node_modules/react"]})
        self.assertIn("node_modules/react/index.js", [x["ruta"] for x in r["archivos"]])

    def test_git_solo_lo_permitido(self):
        with self.assertRaises(self.m.ErrorFs):
            self.a.fs_git({"args": ["push", "--force"]})
        if self.m.shutil.which("git"):
            self.assertEqual(self.a.fs_git({"args": ["init"]})["codigo"], 0)
            self.assertIn("## ", self.a.fs_git({"args": ["status", "--porcelain=v1", "-b"]})["salida"])


if __name__ == "__main__":
    unittest.main()
