"""Servidores de desarrollo reales en el servidor de CódigoCamp (hoy: `php -S`, el servidor integrado de PHP).

Trabajo copia el proyecto a una carpeta de la cuenta, enciende `php -S 127.0.0.1:<puerto interno> -t <carpeta>` y la
vista previa le manda cada petición por /api/trabajo/php/pedir (el puerto interno nunca se publica). Así funcionan
$_GET, $_POST, sesiones, cookies, header(), include… exactamente como en tu PC.

Seguridad: un servidor por cuenta, con límites de CPU, de tamaño de archivos y de procesos, entorno vacío, solo
escucha en 127.0.0.1 y se apaga solo tras 15 minutos sin peticiones. Se desactiva con PHP_SERVIDOR=0.
"""
import base64
import collections
import http.client
import os
import re
import shutil
import signal
import socket
import subprocess
import tempfile
import threading
import time

RAIZ = os.path.join(tempfile.gettempdir(), "codigocamp_dev")
INACTIVO = 15 * 60
MAX_TOTAL = 40_000_000
MAX_ARCHIVOS = 3000
RUTA = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[^\0\\:*?\"<>|]{1,400}$")
SALTO = {"connection", "keep-alive", "transfer-encoding", "upgrade", "proxy-connection", "te", "trailer"}

_procesos = {}
_candado = threading.Lock()


class ErrorServidor(Exception):
    pass


def activo():
    return os.getenv("PHP_SERVIDOR", "1") != "0" and bool(shutil.which("php"))


def _carpeta(uid):
    return os.path.join(RAIZ, f"u{int(uid)}", "php")


def sincronizar(uid, archivos):
    """Copia los archivos de texto del proyecto (lo que el proyecto borró, también se borra aquí)."""
    d = _carpeta(uid)
    os.makedirs(d, exist_ok=True)
    nuevos, total = {}, 0
    for a in (archivos or [])[:MAX_ARCHIVOS]:
        r, c = (a or {}).get("ruta"), (a or {}).get("contenido")
        if not isinstance(r, str) or not isinstance(c, str) or not RUTA.match(r):
            continue
        total += len(c)
        if total > MAX_TOTAL:
            raise ErrorServidor("El proyecto es demasiado grande para el servidor de PHP.")
        nuevos[r] = c
    for raiz, _, nombres in os.walk(d):
        for n in nombres:
            completo = os.path.join(raiz, n)
            rel = os.path.relpath(completo, d).replace(os.sep, "/")
            if rel not in nuevos and not rel.startswith(".sesiones/"):
                try:
                    os.remove(completo)
                except OSError:
                    pass
    for r, c in nuevos.items():
        destino = os.path.join(d, *r.split("/"))
        try:
            with open(destino, encoding="utf-8", newline="") as f:
                if f.read() == c:
                    continue
        except (OSError, UnicodeDecodeError):
            pass
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8", newline="") as f:
            f.write(c)
    return d


def _puerto_libre():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _limites():
    if os.name == "nt":
        return None

    def poner():
        import resource
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (600, 600))
        resource.setrlimit(resource.RLIMIT_FSIZE, (50_000_000, 50_000_000))
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
        except (ValueError, OSError):
            pass
    return poner


def _leer_log(info):
    for linea in iter(info["proc"].stderr.readline, b""):
        texto = linea.decode("utf-8", "replace").rstrip()
        if texto:
            info["log"].append(texto)


def _apagar(info):
    p = info["proc"]
    if p.poll() is None:
        try:
            if os.name != "nt":
                os.killpg(p.pid, signal.SIGTERM)
            else:
                p.terminate()
            p.wait(3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass


def iniciar(uid, archivos, docroot="", router=None):
    """Enciende (o reinicia) el `php -S` de la cuenta. Devuelve la versión de PHP."""
    if not activo():
        raise ErrorServidor("El servidor de PHP no está disponible en este servidor de CódigoCamp.")
    detener(uid)
    d = sincronizar(uid, archivos)
    raiz_docs = os.path.normpath(os.path.join(d, *[p for p in str(docroot or "").split("/") if p and p != ".."]))
    if not raiz_docs.startswith(d) or not os.path.isdir(raiz_docs):
        raise ErrorServidor(f"La carpeta «{docroot}» no existe en tu proyecto.")
    cmd = ["php", "-d", "display_errors=1", "-d", "error_reporting=E_ALL", "-d", f"session.save_path={os.path.join(d, '.sesiones')}",
           "-S", f"127.0.0.1:{_puerto_libre()}", "-t", raiz_docs]
    os.makedirs(os.path.join(d, ".sesiones"), exist_ok=True)
    if router:
        r = os.path.normpath(os.path.join(d, *[p for p in str(router).split("/") if p and p != ".."]))
        if not r.startswith(d) or not os.path.isfile(r):
            raise ErrorServidor(f"No existe el archivo router «{router}».")
        cmd.append(r)
    entorno = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": d, "LANG": "C.UTF-8", "TMPDIR": d}
    proc = subprocess.Popen(cmd, cwd=d, env=entorno, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                            preexec_fn=_limites())
    puerto = int(cmd[cmd.index("-S") + 1].rsplit(":", 1)[1])
    info = {"proc": proc, "puerto": puerto, "uso": time.time(), "log": collections.deque(maxlen=400), "leido": 0}
    threading.Thread(target=_leer_log, args=(info,), daemon=True).start()
    for _ in range(50):   # espera a que acepte conexiones (máx. 5 s)
        if proc.poll() is not None:
            break
        try:
            with socket.create_connection(("127.0.0.1", puerto), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    if proc.poll() is not None:
        time.sleep(0.2)
        raise ErrorServidor("PHP no pudo arrancar:\n" + "\n".join(info["log"]))
    with _candado:
        _procesos[int(uid)] = info
    _vigilar()
    version = subprocess.run(["php", "-r", "echo PHP_VERSION;"], capture_output=True, text=True, timeout=5).stdout.strip() or "8"
    return version


def detener(uid):
    with _candado:
        info = _procesos.pop(int(uid), None)
    if info:
        _apagar(info)
        return True
    return False


def pedir(uid, metodo, ruta, cabeceras, cuerpo):
    """Manda una petición al `php -S` de la cuenta. Devuelve (status, cabeceras, cuerpo_bytes, nuevas_lineas_de_log)."""
    with _candado:
        info = _procesos.get(int(uid))
    if not info or info["proc"].poll() is not None:
        raise ErrorServidor("El servidor de PHP no está encendido. Ejecútalo con: php -S localhost:8000")
    info["uso"] = time.time()
    if not str(ruta).startswith("/"):
        ruta = "/" + str(ruta)
    con = http.client.HTTPConnection("127.0.0.1", info["puerto"], timeout=30)
    try:
        enviar = {k: v for k, v in (cabeceras or []) if isinstance(k, str) and k.lower() not in SALTO | {"host", "content-length"}}
        enviar["Host"] = "localhost"
        con.request(metodo or "GET", ruta, body=cuerpo or None, headers=enviar)
        r = con.getresponse()
        datos = r.read(60_000_000)
        cab = [(k, v) for k, v in r.getheaders() if k.lower() not in SALTO]
        estado = r.status
    except (OSError, http.client.HTTPException) as e:
        raise ErrorServidor(f"PHP no respondió: {e}") from e
    finally:
        con.close()
    lineas = list(info["log"])
    nuevas = lineas[info["leido"]:] if info["leido"] <= len(lineas) else lineas
    info["leido"] = len(lineas)
    return estado, cab, datos, nuevas


_vigilante = None


def _vigilar():
    global _vigilante
    if _vigilante and _vigilante.is_alive():
        return

    def bucle():
        while True:
            time.sleep(60)
            ahora = time.time()
            with _candado:
                viejos = [u for u, i in _procesos.items() if ahora - i["uso"] > INACTIVO or i["proc"].poll() is not None]
                quitar = [_procesos.pop(u) for u in viejos]
            for i in quitar:
                _apagar(i)
    _vigilante = threading.Thread(target=bucle, daemon=True)
    _vigilante.start()


def b64(datos):
    return base64.b64encode(datos).decode("ascii")
