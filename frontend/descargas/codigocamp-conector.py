#!/usr/bin/env python3
"""Conector de CódigoCamp: conecta la terminal de Trabajo con ESTE computador o celular.

Mientras este programa esté abierto, los comandos que escribas en una terminal «Mi equipo» de Trabajo se ejecutan
de verdad aquí, dentro de la carpeta que elijas (python, node, npm, git, flutter, php, docker…), y ves la salida en vivo.
Ciérralo (Ctrl+C) cuando quieras y la conexión se corta al instante.

Uso:
    python codigocamp-conector.py CODIGO [--carpeta RUTA] [--servidor https://tu-codigocamp]
    python codigocamp-conector.py                 # vuelve a conectar el equipo que ya vinculaste

Funciona en Windows, macOS, Linux y Android (con la app Termux: pkg install python).
Solo necesita Python 3.8 o más reciente; no instala nada.

Seguridad:
  · Al abrirlo te pide el PIN, la huella o la contraseña con la que desbloqueas ESTE equipo (Windows Hello, la
    contraseña de tu usuario en macOS/Linux o la huella en Android). Sin eso no se conecta: aunque alguien tenga tu
    cuenta de CódigoCamp, no puede usar tu computador ni tu celular.
  · Nunca ejecuta comandos que borren el disco o el sistema, apaguen el equipo, desactiven el antivirus, roben
    contraseñas o den control remoto a otra persona (el servidor y este programa los bloquean por separado).
  · Si nadie lo usa por 30 minutos se cierra solo.
  · Los comandos corren con TUS permisos en este equipo: ciérralo (Ctrl+C) cuando termines.
  · Este programa solo SALE hacia CódigoCamp (no abre puertos en tu equipo).
  · Los archivos que Trabajo envía solo se escriben DENTRO de la carpeta elegida.
  · Con «Abrir carpeta» en Trabajo eliges una carpeta de este equipo y Trabajo la usa como tu proyecto (como un
    editor de escritorio): lo que guardas allá se escribe aquí y lo que cambias aquí (git, npm, otro editor) aparece
    allá. Nunca deja abrir carpetas del sistema (Windows, Archivos de programa, /etc, /usr…) ni las de contraseñas
    (.ssh, .gnupg, llaveros).
  · Usa el antivirus de ESTE equipo (Microsoft Defender en Windows, ClamAV si lo tienes en Linux/macOS) para revisar
    los programas y archivos que entran o salen de la carpeta y los ejecutables antes de correrlos. Si encuentra un
    virus, el archivo no se guarda, no se envía y no se ejecuta. Nunca apaga ni cambia tu antivirus.
  · El token se guarda en ~/.codigocamp-conector.json; bórralo o usa «Desconectar» en Trabajo para olvidar este equipo.
"""
import argparse
import getpass
import base64
import glob
import shlex
import json
import os
import platform
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

SERVIDOR = "%SERVIDOR%"   # al descargarlo desde CódigoCamp ya viene con la dirección correcta
CONFIG = os.path.join(os.path.expanduser("~"), ".codigocamp-conector.json")
WINDOWS = os.name == "nt"
VERSION_CONECTOR = 5          # sube cuando el Conector aprende algo nuevo (Trabajo avisa si el tuyo es viejo)
CAPACIDADES = ["pty", "partes", "ws", "actualizar"]
IGNORAR = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".dart_tool", "target"}
MAX_TRAER = 2_000_000   # bytes por archivo al traer la carpeta a Trabajo
INACTIVIDAD = 30 * 60   # se cierra solo tras 30 minutos sin órdenes
MAX_LEER = 30_000_000   # bytes por archivo en una sola lectura; los más grandes viajan por partes (leer_parte)
PARTE = 8 * 1024 * 1024  # tamaño de cada parte de un archivo grande (hasta 1 GB por archivo, como en CódigoCamp)
MAX_LISTAR = 5000       # archivos que se listan de la carpeta abierta
# Lo que el antivirus revisa sí o sí (aunque sea texto): programas, scripts e instaladores
EJECUTABLES = {".exe", ".msi", ".bat", ".cmd", ".com", ".scr", ".pif", ".ps1", ".psm1", ".vbs", ".vbe", ".wsf", ".hta", ".jar", ".apk",
               ".dll", ".sys", ".lnk", ".sh", ".command", ".app", ".dmg", ".pkg", ".deb", ".rpm", ".appimage", ".run", ".bin", ".elf",
               ".docm", ".xlsm", ".pptm", ".iso", ".img"}
GIT_PERMITIDOS = {"status", "add", "restore", "commit", "switch", "branch", "init", "log", "show", "diff", "rev-parse", "stash",
                  "checkout", "remote", "config", "reset", "merge", "fetch", "tag", "ls-files"}

# Filtro de comandos peligrosos (el mismo de backend/servicios/comandos_peligrosos.py; CódigoCamp lo copia aquí al descargar)
REVISAR_COMANDO = None  # %FILTRO%
if REVISAR_COMANDO is None:   # copia sin filtro incluido (por ejemplo, el archivo del repositorio): se busca el del backend
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backend"))
        from servicios.comandos_peligrosos import revisar_comando as REVISAR_COMANDO   # noqa: N812
    except Exception:
        REVISAR_COMANDO = None

V, R, A, G, N = ("", "", "", "", "") if WINDOWS and not os.environ.get("WT_SESSION") else ("\033[32m", "\033[31m", "\033[33m", "\033[90m", "\033[0m")


class ErrorConexion(OSError):
    """No se pudo hablar con CódigoCamp. Trae un mensaje en español con la causa y qué hacer."""


def _contexto_tls():
    """Certificados para https: los del sistema y, si está instalado, certifi (algunos Python de Windows no traen)."""
    import ssl
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except Exception:
        pass
    return ctx


def explicar_error_red(e, servidor):
    """Convierte un error de red en una explicación clara (sin el «Traceback» de Python)."""
    import ssl
    motivo = getattr(e, "reason", e)
    texto = str(motivo)
    host = urllib.parse.urlparse(servidor).netloc or servidor
    if isinstance(motivo, ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in texto or "SSL" in texto:
        return (f"La conexión segura con {host} falló ({texto[:120]}). Si tu CódigoCamp usa https con un certificado propio, "
                "abre el Conector con --servidor http://… o instala los certificados: py -m pip install certifi")
    if isinstance(motivo, ConnectionRefusedError) or "10061" in texto or "refused" in texto.lower() or "rechaz" in texto.lower():
        return (f"CódigoCamp no responde en {servidor}. ¿Está encendido el servidor de CódigoCamp (flask run / XAMPP)? "
                "Si en el navegador lo abres con otra dirección (por ejemplo http://192.168.1.5:5000), usa: "
                "py codigocamp-conector.py CODIGO --servidor http://esa-direccion")
    if isinstance(motivo, socket.gaierror) or "11001" in texto or "getaddrinfo" in texto or "Name or service" in texto:
        return f"No se encuentra «{host}». Revisa tu conexión a internet y la dirección del servidor."
    if isinstance(motivo, (socket.timeout, TimeoutError)) or "timed out" in texto.lower() or "10060" in texto:
        return f"{host} tardó demasiado en responder. Revisa tu internet o el firewall/antivirus (debe dejar salir a Python)."
    if "10013" in texto or "10065" in texto:
        return f"Windows bloqueó la conexión a {host} (firewall o antivirus). Permite que Python se conecte a la red."
    return f"No se pudo conectar con {servidor}: {texto[:200]}"


def servidor_rapido(servidor):
    """En Windows, «localhost» prueba primero IPv6 (::1); si CódigoCamp solo escucha en 127.0.0.1, Windows tarda ~2 s en
    rendirse en CADA conexión y todo se siente lento. Se usa directo la dirección que sí responde."""
    u = urllib.parse.urlparse(servidor)
    if (u.hostname or "").lower() != "localhost":
        return servidor
    puerto = u.port or (443 if u.scheme == "https" else 80)
    for ip, texto in (("127.0.0.1", "127.0.0.1"), ("::1", "[::1]")):
        try:
            with socket.create_connection((ip, puerto), timeout=0.4):
                return servidor.replace(u.netloc, f"{texto}:{puerto}" if u.port else texto, 1)
        except OSError:
            continue
    return servidor


def pedir(servidor, metodo, ruta, token=None, datos=None, espera=40):
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    req = urllib.request.Request(servidor.rstrip("/") + ruta, data=cuerpo, method=metodo)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "CodigoCampConector/1.0")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=espera, context=_contexto_tls() if servidor.startswith("https") else None) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except (urllib.error.URLError, OSError) as e:
        raise ErrorConexion(explicar_error_red(e, servidor)) from e


# ------------------------------------------------------- WebSocket (solo biblioteca estándar, RFC 6455) ----
class CanalWS:
    """Canal WebSocket autenticado con el token (cabecera Authorization: Bearer …). El servidor empuja las órdenes al
    instante y la salida vuelve por el mismo canal, cifrado con TLS cuando CódigoCamp usa https."""
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, servidor, token, espera=15):
        import hashlib
        import socket
        import ssl
        u = urllib.parse.urlsplit(servidor.rstrip("/") + "/api/conector/agente/ws")
        seguro = u.scheme == "https"
        puerto = u.port or (443 if seguro else 80)
        crudo = socket.create_connection((u.hostname, puerto), timeout=espera)
        self.sock = _contexto_tls().wrap_socket(crudo, server_hostname=u.hostname) if seguro else crudo
        clave = base64.b64encode(os.urandom(16)).decode()
        host = u.hostname + ("" if u.port is None else f":{u.port}")
        self.sock.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {clave}\r\nSec-WebSocket-Version: 13\r\nAuthorization: Bearer {token}\r\n"
                           f"User-Agent: CodigoCampConector/1.1\r\nOrigin: {u.scheme}://{host}\r\n\r\n").encode())
        cabecera = b""
        while b"\r\n\r\n" not in cabecera:
            parte = self.sock.recv(4096)
            if not parte or len(cabecera) > 16384:
                raise OSError("El servidor no aceptó el WebSocket")
            cabecera += parte
        cabecera, self.resto = cabecera.split(b"\r\n\r\n", 1)
        lineas = cabecera.decode("latin-1").split("\r\n")
        if " 101 " not in lineas[0] + " ":
            raise OSError("El servidor no aceptó el WebSocket: " + lineas[0])
        esperado = base64.b64encode(hashlib.sha1((clave + self.GUID).encode()).digest()).decode()
        if not any(l.lower().startswith("sec-websocket-accept:") and l.split(":", 1)[1].strip() == esperado for l in lineas):
            raise OSError("Respuesta de WebSocket no válida")
        self.sock.settimeout(None)
        self.lock = threading.Lock()
        self.abierto = True

    def _leer(self, n):
        datos = self.resto[:n]
        self.resto = self.resto[n:]
        while len(datos) < n:
            parte = self.sock.recv(max(65536, n - len(datos)))
            if not parte:
                raise ConnectionError("WebSocket cerrado")
            datos += parte
        if len(datos) > n:
            self.resto, datos = datos[n:] + self.resto, datos[:n]
        return datos

    def _marco(self, opcode, carga):
        import struct
        cab = bytes([0x80 | opcode])
        n = len(carga)
        cab += bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack("!H", n) if n < 65536 else bytes([0x80 | 127]) + struct.pack("!Q", n)
        mascara = os.urandom(4)
        enmascarada = bytes(b ^ mascara[i % 4] for i, b in enumerate(carga)) if n < 4096 else _xor_rapido(carga, mascara)
        with self.lock:
            self.sock.sendall(cab + mascara + enmascarada)

    def enviar(self, texto):
        self._marco(0x1, texto.encode("utf-8"))

    def recibir(self):
        """El siguiente mensaje de texto (responde los ping). None si el servidor cerró."""
        import struct
        partes = []
        while True:
            b1, b2 = self._leer(2)
            fin, opcode, n = b1 & 0x80, b1 & 0x0F, b2 & 0x7F
            if n == 126:
                n = struct.unpack("!H", self._leer(2))[0]
            elif n == 127:
                n = struct.unpack("!Q", self._leer(8))[0]
            mascara = self._leer(4) if b2 & 0x80 else None
            carga = self._leer(n)
            if mascara:
                carga = _xor_rapido(carga, mascara)
            if opcode == 0x8:
                self.cerrar()
                return None
            if opcode == 0x9:
                self._marco(0xA, carga)
                continue
            if opcode == 0xA:
                continue
            partes.append(carga)
            if fin:
                return b"".join(partes).decode("utf-8", "replace")

    def cerrar(self):
        if self.abierto:
            self.abierto = False
            try:
                self._marco(0x8, b"")
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass


def _xor_rapido(datos, mascara):
    n = len(datos)
    entero = int.from_bytes(datos, "big") ^ int.from_bytes((mascara * (n // 4 + 1))[:n], "big")
    return entero.to_bytes(n, "big")


def dentro(carpeta, relativa):
    """Ruta absoluta de `relativa` dentro de la carpeta, o None si intenta salirse (../, rutas absolutas)."""
    base = os.path.realpath(carpeta)
    destino = os.path.realpath(os.path.join(base, relativa.replace("\\", "/").lstrip("/")))
    return destino if destino == base or destino.startswith(base + os.sep) else None


def _ms(st):
    return int(st.st_mtime_ns // 1_000_000)


def _carpetas_sistema():
    """Carpetas que nunca se abren ni se listan desde Trabajo (sistema, programas y secretos del usuario)."""
    casa = os.path.realpath(os.path.expanduser("~"))
    secretos = [os.path.join(casa, x) for x in (".ssh", ".gnupg", ".aws", ".azure", ".kube", ".docker", ".password-store",
                                                 os.path.join("Library", "Keychains"), os.path.join("AppData", "Roaming", "Microsoft", "Credentials"),
                                                 os.path.join("AppData", "Local", "Microsoft", "Credentials"), os.path.join("AppData", "Roaming", "Microsoft", "Protect"))]
    if WINDOWS:
        base = [os.environ.get(k) for k in ("SystemRoot", "ProgramFiles", "ProgramFiles(x86)", "ProgramW6432", "ProgramData")]
        base += [os.path.join(os.environ.get("SystemDrive", "C:") + os.sep, x) for x in ("Windows", "Recovery", "$Recycle.Bin", "System Volume Information", "Boot")]
    else:
        base = ["/etc", "/bin", "/sbin", "/usr", "/lib", "/lib32", "/lib64", "/libx32", "/boot", "/dev", "/proc", "/sys", "/run", "/var",
                "/root", "/snap", "/System", "/Library", "/private", "/cores", "/Applications", "/Volumes/Recovery"]
    return [os.path.realpath(x) for x in base + secretos if x]


SISTEMA = _carpetas_sistema()


def permitida(ruta):
    """¿Se puede listar o abrir esta carpeta desde Trabajo?"""
    r = os.path.realpath(ruta)
    casa = os.path.realpath(os.path.expanduser("~"))
    norm = (lambda x: x.lower()) if WINDOWS else (lambda x: x)
    for s in SISTEMA:
        if norm(r) == norm(s) or norm(r).startswith(norm(s).rstrip(os.sep) + os.sep):
            # la carpeta personal puede estar dentro de una «del sistema» (Termux vive en /data/…, algunos Linux en /var/home)
            if not (norm(r) == norm(casa) or norm(r).startswith(norm(casa) + os.sep)) or norm(s).startswith(norm(casa) + os.sep):
                return False
    return True


def elegible(ruta):
    """¿Se puede usar como carpeta de proyecto? (no la raíz del disco ni la carpeta personal completa)"""
    r = os.path.realpath(ruta)
    casa = os.path.realpath(os.path.expanduser("~"))
    raiz_disco = os.path.dirname(r) == r
    compartido = os.path.realpath(os.path.join(casa, "storage", "shared"))
    todas_las_cuentas = os.path.dirname(casa)   # C:\Users, /home, /Users: las carpetas de todas las cuentas
    return permitida(r) and not raiz_disco and r not in {casa, compartido, todas_las_cuentas, "/storage/emulated/0", "/sdcard", "/home", "/Users"}


def es_texto(datos):
    if b"\0" in datos[:8000]:
        return False
    try:
        datos.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def revisar_ext(nombre):
    return os.path.splitext(nombre.lower())[1] in EJECUTABLES


class ErrorFs(Exception):
    def __init__(self, mensaje, **extra):
        super().__init__(mensaje)
        self.extra = extra


# --------------------------------------------------------------- antivirus del propio equipo ----
# ------------------------------------------------------ terminal REAL (pseudo-terminal, como la de VS Code) ----
class PTYUnix:
    """Linux, macOS y Android (Termux): pty.fork() con la shell del usuario."""

    def __init__(self, cwd, cols, rows, shell=""):
        import pty
        self.shell = shell if shell and shutil.which(shell) else os.environ.get("SHELL") or shutil.which("bash") or "/bin/sh"
        self.pid, self.fd = pty.fork()
        if self.pid == 0:   # proceso hijo: la shell
            try:
                os.chdir(cwd)
            except OSError:
                pass
            env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", CODIGOCAMP="1")
            os.execvpe(self.shell, [self.shell, "-i"], env)
        self.redimensionar(cols, rows)

    def leer(self):
        try:
            return os.read(self.fd, 65536)
        except OSError:
            return b""

    def escribir(self, datos):
        os.write(self.fd, datos)

    def redimensionar(self, cols, rows):
        import fcntl
        import struct
        import termios
        try:
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
        except OSError:
            pass

    def cerrar(self):
        try:
            os.kill(self.pid, signal.SIGHUP)
        except OSError:
            pass
        try:
            os.close(self.fd)
        except OSError:
            pass

    def codigo(self):
        try:
            _, estado = os.waitpid(self.pid, 0)
            return os.waitstatus_to_exitcode(estado)
        except Exception:
            return 0


class PTYWindows:
    """Windows 10/11: ConPTY (la misma consola virtual que usan Windows Terminal y VS Code), con PowerShell."""

    def __init__(self, cwd, cols, rows, shell=""):
        import ctypes
        from ctypes import wintypes as w
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        self.k, self.ct, self.w = k, ctypes, w

        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class STARTUPINFOW(ctypes.Structure):
            _fields_ = [("cb", w.DWORD), ("lpReserved", w.LPWSTR), ("lpDesktop", w.LPWSTR), ("lpTitle", w.LPWSTR), ("dwX", w.DWORD), ("dwY", w.DWORD),
                        ("dwXSize", w.DWORD), ("dwYSize", w.DWORD), ("dwXCountChars", w.DWORD), ("dwYCountChars", w.DWORD), ("dwFillAttribute", w.DWORD),
                        ("dwFlags", w.DWORD), ("wShowWindow", w.WORD), ("cbReserved2", w.WORD), ("lpReserved2", ctypes.c_void_p),
                        ("hStdInput", w.HANDLE), ("hStdOutput", w.HANDLE), ("hStdError", w.HANDLE)]

        class STARTUPINFOEXW(ctypes.Structure):
            _fields_ = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [("hProcess", w.HANDLE), ("hThread", w.HANDLE), ("dwProcessId", w.DWORD), ("dwThreadId", w.DWORD)]

        self.COORD = COORD
        # Tipos explícitos: en Windows de 64 bits, sin ellos los handles se cortan a 32 bits y nada funciona
        P = ctypes.POINTER
        k.CreatePipe.argtypes = [P(w.HANDLE), P(w.HANDLE), ctypes.c_void_p, w.DWORD]
        k.CloseHandle.argtypes = [w.HANDLE]
        k.ReadFile.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD, P(w.DWORD), ctypes.c_void_p]
        k.WriteFile.argtypes = [w.HANDLE, ctypes.c_char_p, w.DWORD, P(w.DWORD), ctypes.c_void_p]
        k.CreatePseudoConsole.restype = ctypes.c_long
        k.ResizePseudoConsole.restype = ctypes.c_long
        k.ClosePseudoConsole.argtypes = [ctypes.c_void_p]
        k.ClosePseudoConsole.restype = None
        k.InitializeProcThreadAttributeList.argtypes = [ctypes.c_void_p, w.DWORD, w.DWORD, P(ctypes.c_size_t)]
        k.CreateProcessW.argtypes = [w.LPCWSTR, w.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, w.BOOL, w.DWORD, ctypes.c_void_p, w.LPCWSTR, ctypes.c_void_p, ctypes.c_void_p]
        k.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
        k.WaitForSingleObject.restype = w.DWORD
        k.GetExitCodeProcess.argtypes = [w.HANDLE, P(w.DWORD)]
        k.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
        self.cerrada = False
        entrada_l, entrada_e, salida_l, salida_e = w.HANDLE(), w.HANDLE(), w.HANDLE(), w.HANDLE()
        if not k.CreatePipe(ctypes.byref(entrada_l), ctypes.byref(entrada_e), None, 0) or not k.CreatePipe(ctypes.byref(salida_l), ctypes.byref(salida_e), None, 0):
            raise OSError("No se pudo crear la terminal (CreatePipe).")
        self.hpc = ctypes.c_void_p()
        k.CreatePseudoConsole.argtypes = [COORD, w.HANDLE, w.HANDLE, w.DWORD, ctypes.POINTER(ctypes.c_void_p)]
        r = k.CreatePseudoConsole(COORD(cols, rows), entrada_l, salida_e, 0, ctypes.byref(self.hpc))
        if r != 0:
            raise OSError("Esta versión de Windows no tiene ConPTY (se necesita Windows 10 de 2018 o más nuevo).")
        k.CloseHandle(entrada_l)
        k.CloseHandle(salida_e)
        self.entrada, self.salida = entrada_e, salida_l
        tam = ctypes.c_size_t()
        k.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(tam))
        self.lista = ctypes.create_string_buffer(tam.value)
        if not k.InitializeProcThreadAttributeList(self.lista, 1, 0, ctypes.byref(tam)):
            raise OSError("No se pudo preparar la terminal.")
        k.UpdateProcThreadAttribute.argtypes = [ctypes.c_void_p, w.DWORD, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
        if not k.UpdateProcThreadAttribute(self.lista, 0, 0x00020016, self.hpc, ctypes.sizeof(ctypes.c_void_p), None, None):
            raise OSError("No se pudo conectar la consola virtual.")
        si = STARTUPINFOEXW()
        si.StartupInfo.cb = ctypes.sizeof(STARTUPINFOEXW)
        si.lpAttributeList = ctypes.cast(self.lista, ctypes.c_void_p)
        pi = PROCESS_INFORMATION()
        programa = {"cmd": "cmd.exe", "pwsh": "pwsh.exe -NoLogo"}.get(shell) or ("pwsh.exe -NoLogo" if shutil.which("pwsh") and shell == "pwsh" else "powershell.exe -NoLogo")
        linea = ctypes.create_unicode_buffer(programa)
        if not k.CreateProcessW(None, linea, None, None, False, 0x00080000, None, cwd, ctypes.byref(si), ctypes.byref(pi)):
            raise OSError(f"No se pudo abrir {programa} (error {ctypes.get_last_error()}).")
        self.proceso, self.hilo = w.HANDLE(pi.hProcess), w.HANDLE(pi.hThread)

        # ConPTY no cierra su salida cuando la shell termina (exit): se cierra aquí para que la lectura acabe
        def vigilar():
            k.WaitForSingleObject(self.proceso, 0xFFFFFFFF)
            time.sleep(0.3)   # deja salir lo último que escribió
            self._cerrar_consola()
        threading.Thread(target=vigilar, daemon=True).start()

    def _cerrar_consola(self):
        if self.cerrada:
            return
        self.cerrada = True
        try:
            self.k.ClosePseudoConsole(self.hpc)
        except Exception:
            pass

    def leer(self):
        buf = self.ct.create_string_buffer(65536)
        leidos = self.w.DWORD()
        if not self.k.ReadFile(self.salida, buf, 65536, self.ct.byref(leidos), None):
            return b""
        return buf.raw[: leidos.value]

    def escribir(self, datos):
        escritos = self.w.DWORD()
        self.k.WriteFile(self.entrada, datos, len(datos), self.ct.byref(escritos), None)

    def redimensionar(self, cols, rows):
        self.k.ResizePseudoConsole.argtypes = [self.ct.c_void_p, self.COORD]
        self.k.ResizePseudoConsole(self.hpc, self.COORD(cols, rows))

    def cerrar(self):
        try:
            self.k.TerminateProcess(self.proceso, 1)
        except Exception:
            pass
        self._cerrar_consola()

    def codigo(self):
        codigo = self.w.DWORD()
        self.k.WaitForSingleObject(self.proceso, 3000)
        self.k.GetExitCodeProcess(self.proceso, self.ct.byref(codigo))
        return codigo.value


class Linea:
    """Lo que la persona va escribiendo en la terminal real, para revisar el comando antes de que se ejecute (Enter).
    Es una aproximación (las flechas, el historial y Tab de la shell no se ven), pero frena los comandos peligrosos."""

    def __init__(self):
        self.texto = ""
        self.escape = False

    def agregar(self, datos):
        """Devuelve (lista de líneas completas escritas, hay_enter)."""
        completas = []
        i = 0
        while i < len(datos):
            c = datos[i]
            if self.escape:
                if c.isalpha() or c == "~":
                    self.escape = False
            elif c == "\x1b":
                self.escape = True
            elif c in "\r\n":
                completas.append(self.texto)
                self.texto = ""
            elif c in "\x7f\b":
                self.texto = self.texto[:-1]
            elif c in "\x15\x03":
                self.texto = ""
            elif c >= " ":
                self.texto += c
            i += 1
        return completas


class Antivirus:
    """Usa el antivirus que ya tiene el equipo. Nunca lo apaga ni lo configura: solo le pide revisar archivos."""

    def __init__(self):
        self.cache = {}           # (ruta, tamaño, fecha) → resultado
        self.lock = threading.Lock()
        self.nombre, self.activo, self.escaner = "", None, None
        try:
            self._detectar()
        except Exception:
            pass

    def _defender(self):
        plataformas = sorted(glob.glob(os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "Microsoft", "Windows Defender", "Platform", "*", "MpCmdRun.exe")))
        fijo = os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Windows Defender", "MpCmdRun.exe")
        return plataformas[-1] if plataformas else (fijo if os.path.exists(fijo) else None)

    def _detectar(self):
        if WINDOWS:
            nombres, encendido = [], False
            r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                                "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | ForEach-Object { $_.displayName + '|' + $_.productState }"],
                               capture_output=True, text=True, timeout=40)
            for linea in r.stdout.splitlines():
                if "|" in linea:
                    n, e = linea.rsplit("|", 1)
                    on = e.strip().isdigit() and (int(e) >> 12) & 0xF == 1
                    nombres.append(n.strip() + ("" if on else " (apagado)"))
                    encendido = encendido or on
            self.nombre = ", ".join(nombres) or "Microsoft Defender"
            self.activo = encendido if nombres else None
            mp = self._defender()
            if mp:
                self.escaner = ("defender", mp)
            return
        clam = shutil.which("clamdscan") or shutil.which("clamscan")
        if clam:
            self.escaner = ("clamav", clam)
        if "ANDROID_ROOT" in os.environ:
            self.nombre, self.activo = "Google Play Protect (Android no deja que otras apps le pidan revisar archivos)", None
        elif platform.system() == "Darwin":
            self.nombre, self.activo = "XProtect de macOS" + (" + ClamAV" if clam else ""), True
        else:
            self.nombre, self.activo = ("ClamAV", True) if clam else ("ninguno", False)

    def estado(self):
        return {"nombre": self.nombre, "activo": self.activo, "revisa": bool(self.escaner),
                "herramienta": self.escaner[0] if self.escaner else None}

    @property
    def en_tiempo_real(self):
        """Windows con el antivirus encendido: revisa cada archivo AL ABRIRLO (si tiene virus, Windows bloquea la lectura).
        No hace falta lanzar MpCmdRun por cada archivo que solo se lee (cada uno tarda 1-3 s)."""
        return WINDOWS and self.activo is True

    def revisar_varios(self, rutas):
        """{ruta: amenaza} de varios archivos con UNA sola revisión (ClamAV), no un programa por archivo."""
        if not self.escaner or not rutas:
            return {}
        tipo, prog = self.escaner
        if tipo != "clamav":
            return {r: a for r in rutas if (a := self.revisar(r))}
        resultado, faltan = {}, []
        for r in rutas:
            try:
                st = os.stat(r)
            except OSError:
                continue
            clave = (os.path.realpath(r), st.st_size, st.st_mtime_ns)
            with self.lock:
                if clave in self.cache:
                    if self.cache[clave]:
                        resultado[r] = self.cache[clave]
                    continue
            faltan.append((r, clave))
        for i in range(0, len(faltan), 200):
            grupo = faltan[i:i + 200]
            try:
                args = [prog, "--no-summary"] + (["--fdpass"] if prog.endswith("clamdscan") else []) + [r for r, _ in grupo]
                salida = subprocess.run(args, capture_output=True, text=True, timeout=600).stdout
            except (OSError, subprocess.TimeoutExpired):
                continue
            encontrados = {}
            for linea in salida.splitlines():
                if linea.endswith("FOUND") and ": " in linea:
                    ruta, nombre = linea.rsplit(": ", 1)
                    encontrados[os.path.realpath(ruta)] = nombre.replace("FOUND", "").strip() or "amenaza detectada"
            with self.lock:
                for r, clave in grupo:
                    amenaza = encontrados.get(os.path.realpath(r))
                    self.cache[clave] = amenaza
                    if amenaza:
                        resultado[r] = amenaza
        return resultado

    def revisar(self, ruta):
        """None si está limpio o no se pudo revisar; el nombre de la amenaza si es un virus."""
        if not self.escaner or not os.path.isfile(ruta):
            return None
        st = os.stat(ruta)
        clave = (os.path.realpath(ruta), st.st_size, st.st_mtime_ns)
        with self.lock:
            if clave in self.cache:
                return self.cache[clave]
        tipo, prog = self.escaner
        amenaza = None
        try:
            if tipo == "defender":
                r = subprocess.run([prog, "-Scan", "-ScanType", "3", "-File", ruta, "-DisableRemediation"], capture_output=True, text=True, timeout=300)
                if r.returncode == 2:
                    amenaza = next((l.split(":", 1)[1].strip() for l in r.stdout.splitlines() if l.strip().lower().startswith("threat ")), "amenaza detectada")
            else:
                args = [prog, "--no-summary"] + (["--fdpass"] if prog.endswith("clamdscan") else []) + [ruta]
                r = subprocess.run(args, capture_output=True, text=True, timeout=300)
                if r.returncode == 1:
                    amenaza = next((l.rsplit(":", 1)[1].replace("FOUND", "").strip() for l in r.stdout.splitlines() if l.endswith("FOUND")), "amenaza detectada")
        except (OSError, subprocess.TimeoutExpired):
            return None
        with self.lock:
            self.cache[clave] = amenaza
        return amenaza


class Agente:
    def __init__(self, servidor, token, carpeta):
        self.servidor, self.token, self.carpeta = servidor, token, os.path.realpath(carpeta)
        self.procesos = {}          # orden → Popen
        self.ptys = {}              # orden → terminal real abierta (PTYUnix / PTYWindows)
        self.salidas = queue.Queue()
        self.sin_ws_hasta = 0
        self.ws = None              # canal WebSocket (si el servidor lo permite); si no, peticiones HTTP
        self.activo = True
        self.ultima_orden = time.time()
        self.av = Antivirus()
        self.infectados = set()     # rutas relativas que el antivirus marcó (no se listan ni se envían)

    # ---------------------------------------------------------------- envío de salida (en lotes, sin bloquear) ----
    def enviar_salidas(self):
        while self.activo:
            try:
                primero = self.salidas.get(timeout=0.5)
            except queue.Empty:
                continue
            lote = [primero]
            time.sleep(0.02)   # junta lo que llega casi al mismo tiempo (la terminal real responde rápido)
            while not self.salidas.empty() and len(lote) < 200:
                lote.append(self.salidas.get())
            juntos = {}
            for orden, texto, fin, codigo, datos in lote:
                j = juntos.setdefault(orden, {"orden": orden, "texto": "", "fin": False, "codigo": 0})
                j["texto"] += texto
                if fin:
                    j.update(fin=True, codigo=codigo, datos=datos)
            for j in juntos.values():
                if self.ws and self.ws.abierto:
                    try:
                        self.ws.enviar(json.dumps({"tipo": "salida", **j}))
                        continue
                    except OSError:
                        self.ws.cerrar()
                for _ in range(3):
                    try:
                        pedir(self.servidor, "POST", "/api/conector/agente/salida", self.token, j, espera=30)
                        break
                    except Exception:
                        time.sleep(1)

    def salida(self, orden, texto="", fin=False, codigo=0, datos=None):
        self.salidas.put((orden, texto, fin, codigo, datos))

    # ---------------------------------------------------------------------------------------------- órdenes ----
    def comando(self, o):
        cwd = dentro(self.carpeta, o.get("cwd") or "") or self.carpeta
        if not os.path.isdir(cwd):
            cwd = self.carpeta
        linea = o.get("linea", "")
        motivo = REVISAR_COMANDO(linea) if REVISAR_COMANDO else None
        if motivo:
            print(f"{R}[bloqueado]{N} {linea.splitlines()[0][:120] if linea else ''}")
            self.salida(o["id"], f"🛡️ Este equipo bloqueó el comando porque {motivo}.\n", True, 126)
            return
        self.ultima_orden = time.time()
        amenaza = self.revisar_programa(linea, cwd)
        if amenaza:
            print(f"{R}[virus]{N} {amenaza}")
            self.salida(o["id"], f"🛡️ El antivirus de este equipo encontró «{amenaza}» en el programa que ibas a ejecutar. No se ejecutó.\n", True, 126)
            return
        print(f"{G}[{time.strftime('%H:%M:%S')}]{N} {V}${N} {linea.splitlines()[0][:120] if linea else ''}")
        env = dict(os.environ, FORCE_COLOR="1", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8", COLUMNS=str(o.get("columnas") or 100), TERM="xterm-256color")
        try:
            if WINDOWS:
                p = subprocess.Popen(["cmd.exe", "/d", "/s", "/c", linea], cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                shell = shutil.which("bash") or shutil.which("sh") or "/bin/sh"
                p = subprocess.Popen([shell, "-c", linea], cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, start_new_session=True)
        except Exception as e:
            self.salida(o["id"], f"No se pudo ejecutar: {e}\n", True, 127)
            return
        self.procesos[o["id"]] = p

        def leer():
            while True:
                trozo = p.stdout.read1(4096) if hasattr(p.stdout, "read1") else p.stdout.read(1)
                if not trozo:
                    break
                self.salida(o["id"], trozo.decode("utf-8", "replace"))
            codigo = p.wait()
            self.procesos.pop(o["id"], None)
            self.salida(o["id"], "", True, codigo)
        threading.Thread(target=leer, daemon=True).start()

    def revisar_programa(self, linea, cwd):
        """Si el comando ejecuta un programa o script de la carpeta (./app, app.exe, instalar.bat, java -jar x.jar…), lo revisa antes."""
        try:
            partes = shlex.split(linea, posix=not WINDOWS)[:4]
        except ValueError:
            partes = linea.split()[:4]
        for p in partes:
            p = p.strip("\"'")
            ruta = os.path.join(cwd, p)
            if p and os.path.isfile(ruta) and (revisar_ext(p) or (not WINDOWS and os.access(ruta, os.X_OK) and p.startswith("./"))):
                amenaza = self.av.revisar(ruta)
                if amenaza:
                    return amenaza
        return None

    # ---------------------------------------------------------------------------- terminal real ----
    def pty(self, o):
        """Abre la shell del equipo en una pseudo-terminal y manda todo lo que muestra (colores, editores, Tab…)."""
        self.ultima_orden = time.time()
        cwd = dentro(self.carpeta, o.get("cwd") or "") or self.carpeta
        try:
            t = (PTYWindows if WINDOWS else PTYUnix)(cwd, int(o.get("cols") or 100), int(o.get("rows") or 30), str(o.get("shell") or ""))
        except Exception as e:
            self.salida(o["id"], f"No se pudo abrir la terminal real: {e}\r\n", True, 1, {"sin_pty": True})
            return
        t.linea = Linea()
        self.ptys[o["id"]] = t
        print(f"{G}[{time.strftime('%H:%M:%S')}]{N} Terminal abierta desde Trabajo en {cwd}")

        def leer():
            import codecs
            dec = codecs.getincrementaldecoder("utf-8")("replace")
            while True:
                datos = t.leer()
                if not datos:
                    break
                self.salida(o["id"], dec.decode(datos))
            codigo = t.codigo()
            self.ptys.pop(o["id"], None)
            self.salida(o["id"], f"\r\n[La terminal se cerró (código {codigo})]\r\n", True, codigo)
        threading.Thread(target=leer, daemon=True).start()

    def entrada_pty(self, t, oid, texto):
        """Escribe en la terminal real; antes de cada Enter revisa el comando (comandos destructivos y programas con virus)."""
        self.ultima_orden = time.time()
        partes = re.split(r"(\r|\n)", texto)
        for parte in partes:
            for linea in t.linea.agregar(parte):
                motivo = REVISAR_COMANDO(linea) if REVISAR_COMANDO and linea.strip() else None
                amenaza = None if motivo else (self.revisar_programa(linea, self.carpeta) if linea.strip() else None)
                if motivo or amenaza:
                    print(f"{R}[bloqueado]{N} {linea[:120]}")
                    t.escribir(b"\x1b" if WINDOWS else b"\x15")   # borra la línea escrita en la shell
                    aviso = f"porque {motivo}" if motivo else f"porque el antivirus de este equipo encontró «{amenaza}»"
                    self.salida(oid, f"\r\n\x1b[1;31m🛡️ Este equipo bloqueó el comando {aviso}.\x1b[0m\r\n")
                    t.escribir(b"\r")
                    break
            else:
                t.escribir(parte.encode("utf-8"))

    def tam(self, o):
        t = self.ptys.get(o["id"])
        if t:
            t.redimensionar(int(o.get("cols") or 80), int(o.get("rows") or 24))

    def entrada(self, o):
        t = self.ptys.get(o["id"])
        if t:
            try:
                self.entrada_pty(t, o["id"], o.get("texto", ""))
            except OSError:
                pass
            return
        p = self.procesos.get(o["id"])
        if p and p.stdin:
            try:
                p.stdin.write(o.get("texto", "").encode())
                p.stdin.flush()
            except Exception:
                pass

    def detener(self, o):
        t = self.ptys.pop(o["id"], None)
        if t:
            t.cerrar()
            return
        p = self.procesos.get(o["id"])
        if not p:
            return
        try:
            if WINDOWS:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
            else:
                os.killpg(os.getpgid(p.pid), signal.SIGINT)
                time.sleep(1.5)
                if p.poll() is None:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            p.kill()

    def escribir(self, o):
        n = 0
        for ruta, texto in (o.get("archivos") or {}).items():
            destino = dentro(self.carpeta, ruta)
            if not destino:
                continue
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            if isinstance(texto, str) and texto.startswith("ccb64:"):
                try:
                    self.guardar_revisado(destino, base64.b64decode(texto[6:]), ruta)
                except ErrorFs as e:
                    self.salida(o["id"], f"{e}\n")
                    continue
            else:
                with open(destino, "w", encoding="utf-8", newline="") as f:
                    f.write(texto)
            n += 1
        for ruta in o.get("borrar") or []:
            destino = dentro(self.carpeta, ruta)
            if destino and destino != self.carpeta and os.path.isfile(destino):
                os.remove(destino)
        print(f"{G}[{time.strftime('%H:%M:%S')}]{N} Recibí {n} archivo(s) de Trabajo")
        self.salida(o["id"], f"{n} archivo(s) copiados a {self.carpeta}\n", True, 0)

    def leer(self, o):
        archivos, saltados = {}, 0
        for raiz, dirs, nombres in os.walk(self.carpeta):
            dirs[:] = [d for d in dirs if d not in IGNORAR]
            for nombre in nombres:
                ruta = os.path.join(raiz, nombre)
                rel = os.path.relpath(ruta, self.carpeta).replace(os.sep, "/")
                try:
                    if os.path.getsize(ruta) > MAX_TRAER or len(archivos) >= 3000:
                        saltados += 1
                        continue
                    with open(ruta, "rb") as f:
                        b = f.read()
                    if (revisar_ext(nombre) or not es_texto(b)) and self.av.revisar(ruta):
                        saltados += 1
                        continue
                    try:
                        archivos[rel] = b.decode("utf-8")
                    except UnicodeDecodeError:
                        archivos[rel] = "ccb64:" + base64.b64encode(b).decode()
                except OSError:
                    saltados += 1
        texto = f"{len(archivos)} archivo(s) leídos" + (f" ({saltados} omitidos por tamaño)" if saltados else "") + "\n"
        self.salida(o["id"], texto, True, 0, {"archivos": archivos})

    # ------------------------------------------------------- carpeta abierta en Trabajo (como un editor) ----
    def guardar_revisado(self, destino, datos, rel):
        """Escribe el archivo; si es un programa o binario, el antivirus del equipo lo revisa antes de dejarlo."""
        if not (revisar_ext(destino) or not es_texto(datos)) or not self.av.escaner:
            with open(destino, "wb") as f:
                f.write(datos)
            return
        temporal = destino + ".ccrevision"
        with open(temporal, "wb") as f:
            f.write(datos)
        time.sleep(0.05)
        if not os.path.exists(temporal):   # el antivirus en tiempo real ya lo quitó
            raise ErrorFs(f"🛡️ El antivirus de este equipo eliminó «{rel}» al guardarlo (tenía un virus).", virus=True)
        amenaza = self.av.revisar(temporal)
        if amenaza:
            try:
                os.remove(temporal)
            except OSError:
                pass
            raise ErrorFs(f"🛡️ El antivirus de este equipo encontró «{amenaza}» en «{rel}». No se guardó.", virus=True)
        os.replace(temporal, destino)

    def fs(self, o):
        accion = str(o.get("accion", ""))
        metodo = getattr(self, "fs_" + accion, None) if accion in {"listar", "leer", "escribir", "carpeta", "borrar", "explorar",
                                                                    "nueva", "raiz", "git", "antivirus", "leer_varios", "servicios", "leer_parte", "escribir_parte"} else None
        if accion not in {"listar", "antivirus", "servicios"}:   # revisar la carpeta cada pocos segundos no cuenta como «usarlo»
            self.ultima_orden = time.time()

        def correr():
            try:
                if not metodo:
                    raise ErrorFs("Acción no válida.")
                self.salida(o["id"], "", True, 0, metodo(o) or {})
            except ErrorFs as e:
                self.salida(o["id"], str(e) + "\n", True, 1, {"error": str(e), **e.extra})
            except FileNotFoundError:
                self.salida(o["id"], "No existe.\n", True, 1, {"error": "No existe ese archivo o carpeta.", "no_existe": True})
            except PermissionError:
                self.salida(o["id"], "Sin permiso.\n", True, 1, {"error": "Este equipo no da permiso para usar ese archivo (¿está abierto en otro programa?)."})
            except Exception as e:
                self.salida(o["id"], f"{e}\n", True, 1, {"error": str(e)})
        threading.Thread(target=correr, daemon=True).start()

    def _ruta(self, o, clave="ruta"):
        destino = dentro(self.carpeta, str(o.get(clave) or ""))
        if not destino:
            raise ErrorFs("Esa ruta está fuera de la carpeta abierta.")
        return destino

    def fs_listar(self, o):
        ignorar = set(o.get("ignorar") or IGNORAR)
        archivos, carpetas = [], []
        for raiz, dirs, nombres in os.walk(self.carpeta):
            dirs[:] = sorted(d for d in dirs if d not in ignorar and not os.path.islink(os.path.join(raiz, d)))
            rel_dir = os.path.relpath(raiz, self.carpeta).replace(os.sep, "/")
            if rel_dir != ".":
                carpetas.append(rel_dir)
            for nombre in nombres:
                if nombre.endswith((".ccrevision", ".ccparcial")):
                    continue
                ruta = os.path.join(raiz, nombre)
                rel = nombre if rel_dir == "." else f"{rel_dir}/{nombre}"
                if rel in self.infectados:
                    continue
                try:
                    st = os.stat(ruta)
                except OSError:
                    continue
                archivos.append({"ruta": rel, "tamano": st.st_size, "modificado": _ms(st)})
                if len(archivos) >= MAX_LISTAR:
                    return {"archivos": archivos, "carpetas": carpetas, "incompleto": True}
        return {"archivos": archivos, "carpetas": carpetas}

    def _leer_bytes(self, ruta, rel):
        try:
            with open(ruta, "rb") as f:
                return f.read()
        except OSError as e:
            # Windows bloquea la lectura de un archivo con virus (error 225): es el antivirus en tiempo real
            if getattr(e, "winerror", None) in (225, 226) or "virus" in str(e).lower():
                self.infectados.add(rel)
                print(f"{R}[virus]{N} {rel}")
                raise ErrorFs(f"🛡️ El antivirus de este equipo bloqueó «{rel}» (tiene un virus o software no deseado). No se envió a CódigoCamp.", virus=True)
            raise

    def fs_leer(self, o, revisar=True):
        ruta = self._ruta(o)
        rel = str(o.get("ruta"))
        st = os.stat(ruta)
        if st.st_size > MAX_LEER:
            raise ErrorFs(f"«{rel}» es grande: se pide por partes.", grande=True, tamano=st.st_size)
        datos = self._leer_bytes(ruta, rel)
        if not revisar:   # leer_varios los revisa todos juntos
            return {"b64": base64.b64encode(datos).decode(), "tamano": st.st_size, "modificado": _ms(st),
                    "_revisar": bool(revisar_ext(ruta) or not es_texto(datos)), "_ruta": ruta}
        if (revisar_ext(ruta) or not es_texto(datos)) and not self.av.en_tiempo_real:
            amenaza = self.av.revisar(ruta)
            if amenaza:
                self.infectados.add(rel)
                print(f"{R}[virus]{N} {rel}: {amenaza}")
                raise ErrorFs(f"🛡️ El antivirus de este equipo encontró «{amenaza}» en «{rel}». No se envió a CódigoCamp.", virus=True)
        return {"b64": base64.b64encode(datos).decode(), "tamano": st.st_size, "modificado": _ms(st)}

    def fs_leer_varios(self, o):
        """Varios archivos de una vez. Los binarios y ejecutables se revisan con el antivirus TODOS JUNTOS (antes era un
        programa por archivo: abrir una carpeta con imágenes tardaba minutos)."""
        archivos, total, por_revisar = {}, 0, {}
        for rel in [str(r) for r in (o.get("rutas") or [])][:500]:
            try:
                d = self.fs_leer({"ruta": rel}, revisar=False)
                if d.pop("_revisar") and not self.av.en_tiempo_real:
                    por_revisar[d["_ruta"]] = rel
                d.pop("_ruta")
                total += d["tamano"]
                archivos[rel] = d
            except ErrorFs as e:
                archivos[rel] = {"error": str(e), **e.extra}
            except OSError:
                archivos[rel] = {"error": "No se pudo leer (¿está abierto en otro programa?)."}
            if total > 12_000_000:
                break
        for ruta, amenaza in self.av.revisar_varios(list(por_revisar)).items():
            rel = por_revisar[ruta]
            self.infectados.add(rel)
            print(f"{R}[virus]{N} {rel}: {amenaza}")
            archivos[rel] = {"error": f"🛡️ El antivirus de este equipo encontró «{amenaza}» en «{rel}». No se envió a CódigoCamp.", "virus": True}
        return {"archivos": archivos}

    def fs_leer_parte(self, o):
        """Una parte de un archivo grande. En la primera parte, el antivirus del equipo revisa el archivo completo."""
        ruta = self._ruta(o)
        rel = str(o.get("ruta"))
        desde = max(0, int(o.get("desde") or 0))
        st = os.stat(ruta)
        if desde == 0 and not self.av.en_tiempo_real:
            amenaza = self.av.revisar(ruta)
            if amenaza:
                self.infectados.add(rel)
                raise ErrorFs(f"🛡️ El antivirus de este equipo encontró «{amenaza}» en «{rel}». No se envió a CódigoCamp.", virus=True)
        with open(ruta, "rb") as f:
            f.seek(desde)
            datos = f.read(PARTE)
        return {"b64": base64.b64encode(datos).decode(), "desde": desde, "total": st.st_size, "modificado": _ms(st), "fin": desde + len(datos) >= st.st_size}

    def fs_escribir_parte(self, o):
        """Escribe un archivo grande por partes en un temporal; con la última parte, antivirus y se reemplaza el archivo."""
        ruta = self._ruta(o)
        if ruta == self.carpeta:
            raise ErrorFs("Ruta no válida.")
        rel = str(o.get("ruta"))
        temporal = ruta + ".ccparcial"
        desde = max(0, int(o.get("desde") or 0))
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(temporal, "r+b" if desde and os.path.exists(temporal) else "wb") as f:
            f.seek(desde)
            f.write(base64.b64decode(str(o.get("b64") or "")))
            f.truncate()
        if not o.get("fin"):
            return {"recibido": os.path.getsize(temporal)}
        amenaza = self.av.revisar(temporal) if os.path.exists(temporal) else "eliminado por el antivirus"
        if amenaza or not os.path.exists(temporal):
            try:
                os.remove(temporal)
            except OSError:
                pass
            raise ErrorFs(f"🛡️ El antivirus de este equipo encontró «{amenaza}» en «{rel}». No se guardó.", virus=True)
        os.replace(temporal, ruta)
        st = os.stat(ruta)
        return {"tamano": st.st_size, "modificado": _ms(st)}

    def fs_escribir(self, o):
        ruta = self._ruta(o)
        if ruta == self.carpeta:
            raise ErrorFs("Ruta no válida.")
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        self.guardar_revisado(ruta, base64.b64decode(str(o.get("b64") or "")), str(o.get("ruta")))
        st = os.stat(ruta)
        return {"tamano": st.st_size, "modificado": _ms(st)}

    def fs_carpeta(self, o):
        os.makedirs(self._ruta(o), exist_ok=True)
        return {}

    def fs_borrar(self, o):
        ruta = self._ruta(o)
        if ruta == self.carpeta:
            raise ErrorFs("No se puede borrar la carpeta abierta.")
        if os.path.isfile(ruta) or os.path.islink(ruta):
            os.remove(ruta)
        elif os.path.isdir(ruta) and not os.listdir(ruta):
            os.rmdir(ruta)
        padre = os.path.dirname(ruta)   # quita las carpetas que quedaron vacías (sin salirse de la abierta)
        while padre != self.carpeta and padre.startswith(self.carpeta + os.sep):
            try:
                os.rmdir(padre)
            except OSError:
                break
            padre = os.path.dirname(padre)
        return {}

    def _raices(self):
        casa = os.path.expanduser("~")
        lista = [("🏠 Personal", casa)]
        for nombres, etiqueta in ((("Desktop", "Escritorio"), "🖥 Escritorio"), (("Documents", "Documentos"), "📄 Documentos"), (("Downloads", "Descargas"), "⬇ Descargas")):
            for n in nombres:
                for base in (casa, os.path.join(casa, "OneDrive")):
                    if os.path.isdir(os.path.join(base, n)):
                        lista.append((etiqueta, os.path.join(base, n)))
                        break
                else:
                    continue
                break
        if "ANDROID_ROOT" in os.environ and os.path.isdir(os.path.join(casa, "storage", "shared")):
            lista.append(("📱 Almacenamiento", os.path.join(casa, "storage", "shared")))
        if WINDOWS:
            import string
            for letra in string.ascii_uppercase:
                if os.path.exists(f"{letra}:\\"):
                    lista.append((f"💽 Disco {letra}:", f"{letra}:\\"))
        return [{"nombre": n, "ruta": os.path.realpath(r)} for n, r in lista]

    def fs_explorar(self, o):
        ruta = os.path.realpath(str(o.get("ruta") or "") or self.carpeta)
        if not os.path.isdir(ruta) or not permitida(ruta):
            ruta = os.path.realpath(os.path.expanduser("~"))
        carpetas = []
        try:
            for e in sorted(os.scandir(ruta), key=lambda x: x.name.lower()):
                if e.name.startswith(".") or e.name.startswith("$") or e.name in {"node_modules", "__pycache__", "AppData", "Library"}:
                    continue
                try:
                    if e.is_dir() and permitida(e.path):
                        carpetas.append(e.name)
                except OSError:
                    pass
        except PermissionError:
            pass
        padre = os.path.dirname(ruta)
        return {"ruta": ruta, "padre": padre if padre != ruta and permitida(padre) else None, "carpetas": carpetas[:1000],
                "elegible": elegible(ruta), "actual": self.carpeta, "separador": os.sep, "raices": self._raices()}

    def fs_nueva(self, o):
        base = os.path.realpath(str(o.get("ruta") or ""))
        nombre = str(o.get("nombre") or "").strip()
        if not nombre or any(c in nombre for c in '\\/:*?"<>|') or nombre in {".", ".."}:
            raise ErrorFs("Ese nombre de carpeta no es válido.")
        if not os.path.isdir(base) or not permitida(base):
            raise ErrorFs("No se pueden crear carpetas ahí.")
        nueva = os.path.join(base, nombre)
        os.makedirs(nueva, exist_ok=True)
        return {"ruta": os.path.realpath(nueva)}

    def fs_raiz(self, o):
        ruta = os.path.realpath(str(o.get("ruta") or ""))
        if not os.path.isdir(ruta):
            raise ErrorFs("Esa carpeta no existe en este equipo.")
        if not elegible(ruta):
            raise ErrorFs("Por seguridad no se puede abrir esa carpeta (es del sistema, de contraseñas o es demasiado grande). Elige o crea la carpeta de tu proyecto.")
        self.carpeta = ruta
        self.infectados.clear()
        try:
            with open(CONFIG, encoding="utf-8") as f:
                datos = json.load(f)
            datos["carpeta"] = ruta
            guardar(datos)
        except Exception:
            pass
        print(f"{G}[{time.strftime('%H:%M:%S')}]{N} Carpeta abierta en Trabajo: {ruta}")
        threading.Thread(target=self.avisar_estado, daemon=True).start()   # Trabajo ve la carpeta nueva al instante
        return {"carpeta": ruta, "nombre": os.path.basename(ruta) or ruta}

    def fs_git(self, o):
        args = [str(a) for a in (o.get("args") or [])][:60]
        if not args or args[0] not in GIT_PERMITIDOS:
            raise ErrorFs("Ese comando de Git no está permitido aquí; úsalo en la terminal.")
        git = shutil.which("git")
        if not git:
            raise ErrorFs("Git no está instalado en este equipo. Descárgalo en https://git-scm.com/downloads", sin_git=True)
        if REVISAR_COMANDO:
            motivo = REVISAR_COMANDO("git " + " ".join(shlex.quote(a) for a in args))
            if motivo:
                raise ErrorFs(f"🛡️ Bloqueado porque {motivo}.")
        cwd = dentro(self.carpeta, str(o.get("cwd") or "")) or self.carpeta
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
        r = subprocess.run([git, "-c", "core.quotepath=off", *args], cwd=cwd, capture_output=True, timeout=120, env=env)
        return {"codigo": r.returncode, "salida": r.stdout.decode("utf-8", "replace")[:3_000_000], "error": r.stderr.decode("utf-8", "replace")[:20000]}

    def fs_servicios(self, o):
        """Servicios locales de este equipo (XAMPP, Apache, MySQL/MariaDB, PostgreSQL, MongoDB, Redis…): solo se mira si
        el puerto responde en 127.0.0.1 y qué programas hay instalados. No se conecta a ninguna base ni lee datos."""
        def abierto(puerto):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as x:
                x.settimeout(0.25)
                return x.connect_ex(("127.0.0.1", puerto)) == 0
        xampp = next((r for r in ([r"C:\xampp", r"D:\xampp"] if WINDOWS else ["/opt/lampp", "/Applications/XAMPP/xamppfiles"]) if os.path.isdir(r)), None)
        def cli(nombre, en_xampp=None):
            if xampp and en_xampp:
                r = os.path.join(xampp, *en_xampp)
                if os.path.isfile(r):
                    return r
            return shutil.which(nombre)
        mysql = cli("mysql", ["mysql", "bin", "mysql.exe" if WINDOWS else "mysql"]) if WINDOWS else cli("mysql", ["bin", "mysql"])
        q = (lambda r: f'"{r}"' if r and " " in r else r)
        lista = [
            {"id": "web", "nombre": "Apache / servidor web" + (" (XAMPP)" if xampp else ""), "puerto": 80, "tipo": "web"},
            {"id": "web8080", "nombre": "Servidor web", "puerto": 8080, "tipo": "web"},
            {"id": "mysql", "nombre": "MySQL / MariaDB" + (" (XAMPP)" if xampp else ""), "puerto": 3306, "tipo": "bd",
             "consola": f"{q(mysql)} -u root -h 127.0.0.1 -t" if mysql else None, "phpmyadmin": bool(xampp)},
            {"id": "postgres", "nombre": "PostgreSQL", "puerto": 5432, "tipo": "bd", "consola": "psql -U postgres -h 127.0.0.1" if shutil.which("psql") else None},
            {"id": "mongo", "nombre": "MongoDB", "puerto": 27017, "tipo": "bd", "consola": "mongosh --quiet" if shutil.which("mongosh") else ("mongo --quiet" if shutil.which("mongo") else None)},
            {"id": "redis", "nombre": "Redis", "puerto": 6379, "tipo": "bd", "consola": "redis-cli" if shutil.which("redis-cli") else None},
            {"id": "sqlserver", "nombre": "SQL Server", "puerto": 1433, "tipo": "bd", "consola": "sqlcmd -S localhost" if shutil.which("sqlcmd") else None},
        ]
        for x in lista:
            x["activo"] = abierto(x["puerto"])
        visibles = [x for x in lista if x["activo"] or x.get("consola") or (xampp and x["id"] in {"web", "mysql"})]
        iniciar = None
        if xampp:
            iniciar = (q(os.path.join(xampp, "xampp-control.exe")) if WINDOWS else
                       f"sudo {xampp}/lampp start" if xampp.startswith("/opt") else "sudo /Applications/XAMPP/xamppfiles/xampp start")
        return {"servicios": visibles, "xampp": xampp, "iniciar_xampp": iniciar}

    def fs_antivirus(self, o):
        return self.av.estado()

    # ------------------------------------------------------------------------------------------- bucle ----
    def avisar_estado(self):
        try:
            if self.ws and self.ws.abierto:
                self.ws.enviar(json.dumps({"tipo": "estado", "antivirus": self.av.estado(), "carpeta": self.carpeta,
                                           "version": VERSION_CONECTOR, "capacidades": CAPACIDADES}))
                return
            pedir(self.servidor, "POST", "/api/conector/agente/estado", self.token,
                  {"antivirus": self.av.estado(), "carpeta": self.carpeta, "version": VERSION_CONECTOR, "capacidades": CAPACIDADES}, espera=20)
        except Exception:
            pass

    def correr(self):
        threading.Thread(target=self.enviar_salidas, daemon=True).start()
        threading.Thread(target=self.avisar_estado, daemon=True).start()
        fallos = 0
        while self.activo:
            try:
                estado, r = pedir(self.servidor, "GET", "/api/conector/agente/esperar?carpeta=" + urllib.request.quote(self.carpeta), self.token)
            except Exception:
                fallos += 1
                if fallos == 1:
                    print(f"{A}Sin conexión con CódigoCamp. Reintentando…{N}")
                time.sleep(min(30, 2 * fallos))
                continue
            if fallos:
                print(f"{V}Conexión recuperada.{N}")
                fallos = 0
            if not self.procesos and not self.ptys and time.time() - self.ultima_orden > INACTIVIDAD:
                print(f"{A}30 minutos sin usar: el Conector se cerró por seguridad. Ábrelo otra vez cuando lo necesites.{N}")
                self.activo = False
                return
            if estado == 401:
                print(f"{R}Este equipo fue desconectado desde Trabajo.{N}")
                olvidar()
                return
            if estado != 200:
                time.sleep(3)
                continue
            for o in r.get("ordenes", []):
                if not self.atender(o):
                    return
            if self.intentar_ws():
                return

    def atender(self, o):
        """Ejecuta una orden. False si hay que cerrar el Conector (lo desconectaron desde Trabajo)."""
        tipo = o.get("tipo")
        if tipo == "desconectar":
            print(f"{A}Desconectado desde Trabajo. ¡Hasta pronto!{N}")
            olvidar()
            self.activo = False
            return False
        if tipo in {"escribir", "leer"}:
            self.ultima_orden = time.time()
        metodo = getattr(self, tipo, None) if tipo in {"comando", "entrada", "detener", "escribir", "leer", "fs", "pty", "tam"} else None
        if metodo:
            try:
                metodo(o)
            except Exception as e:
                self.salida(o.get("id", ""), f"Error del Conector: {e}\n", True, 1)
        return True

    def intentar_ws(self):
        """Pasa al canal WebSocket si se puede (cada minuto lo vuelve a intentar). True si hay que cerrar el Conector."""
        if self.sin_ws_hasta > time.time() or os.environ.get("CC_SIN_WEBSOCKET"):
            return False
        try:
            self.ws = CanalWS(self.servidor, self.token)
        except Exception:
            self.ws = None
            self.sin_ws_hasta = time.time() + 60
            return False
        print(f"{G}[{time.strftime('%H:%M:%S')}]{N} Canal seguro WebSocket abierto.")
        self.avisar_estado()
        vigia = threading.Thread(target=self._vigilar_inactividad, daemon=True)
        vigia.start()
        try:
            while self.activo and self.ws.abierto:
                m = self.ws.recibir()
                if m is None:
                    break
                try:
                    data = json.loads(m)
                except ValueError:
                    continue
                if data.get("tipo") == "error" and data.get("codigo") == 401:
                    print(f"{R}Este equipo fue desconectado desde Trabajo.{N}")
                    olvidar()
                    self.activo = False
                    return True
                for o in data.get("ordenes", []) if data.get("tipo") == "ordenes" else []:
                    if not self.atender(o):
                        self.ws.cerrar()
                        return True
        except (OSError, ConnectionError, ValueError):
            pass
        finally:
            if self.ws:
                self.ws.cerrar()
            self.ws = None
        if not self.activo:
            return True
        print(f"{A}Se cerró el canal WebSocket; sigo con la conexión normal.{N}")
        self.sin_ws_hasta = time.time() + 10
        return False

    def _vigilar_inactividad(self):
        while self.activo and self.ws and self.ws.abierto:
            time.sleep(15)
            if not self.procesos and not self.ptys and time.time() - self.ultima_orden > INACTIVIDAD:
                print(f"{A}30 minutos sin usar: el Conector se cerró por seguridad. Ábrelo otra vez cuando lo necesites.{N}")
                self.activo = False
                if self.ws:
                    self.ws.cerrar()


# --------------------------------------------------------- ¿eres el dueño de este equipo? (PIN, huella o clave) ----
_HELLO = r"""
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Security.Credentials.UI.UserConsentVerifier,Windows.Security.Credentials.UI,ContentType=WindowsRuntime]
$asTask=([System.WindowsRuntimeSystemExtensions].GetMethods()|Where-Object{$_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'})[0]
function Esperar($op,[Type]$t){$x=$asTask.MakeGenericMethod($t).Invoke($null,@($op));$x.Wait(-1)|Out-Null;$x.Result}
$d=Esperar ([Windows.Security.Credentials.UI.UserConsentVerifier]::CheckAvailabilityAsync()) ([Windows.Security.Credentials.UI.UserConsentVerifierAvailability])
if("$d" -ne 'Available'){Write-Output 'NO_DISPONIBLE';exit 2}
$r=Esperar ([Windows.Security.Credentials.UI.UserConsentVerifier]::RequestVerificationAsync('CodigoCamp quiere conectar la terminal de Trabajo a este equipo')) ([Windows.Security.Credentials.UI.UserConsentVerificationResult])
if("$r" -eq 'Verified'){exit 0}else{Write-Output "$r";exit 1}
"""


def _clave_windows(clave):
    import ctypes
    from ctypes import wintypes
    usuario = os.environ.get("USERNAME", "")
    dominio = os.environ.get("USERDOMAIN", ".")
    token = wintypes.HANDLE()
    LogonUserW = ctypes.windll.advapi32.LogonUserW
    for tipo in (2, 3):   # interactivo y de red (sirve también con cuenta Microsoft)
        for dom in (dominio, "."):
            if LogonUserW(usuario, dom, clave, tipo, 0, ctypes.byref(token)):
                ctypes.windll.kernel32.CloseHandle(token)
                return True
    return False


def verificar_dueno():
    """Pide el PIN, la huella o la contraseña con la que se desbloquea este equipo. True si es su dueño."""
    print(f"  {A}🔒 Confirma que eres el dueño de este equipo{N}")
    if WINDOWS:
        print("  Windows te pedirá tu PIN, huella o rostro (Windows Hello)…")
        try:
            r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", _HELLO],
                               capture_output=True, text=True, timeout=180)
            if r.returncode == 0:
                return True
            if "NO_DISPONIBLE" not in r.stdout:
                print(f"  {R}No se confirmó tu identidad.{N}")
                return False
        except (OSError, subprocess.TimeoutExpired):
            pass
        print("  Windows Hello no está configurado: escribe la contraseña con la que entras a Windows.")
        for _ in range(3):
            if _clave_windows(getpass.getpass("  Contraseña de Windows: ")):
                return True
            print(f"  {R}Contraseña incorrecta.{N}")
        return False
    if "ANDROID_ROOT" in os.environ:
        if not shutil.which("termux-fingerprint"):
            print(f"  {R}En Android se necesita la app Termux:API y el comando: pkg install termux-api{N}")
            return False
        print("  Pon tu huella en el sensor…")
        try:
            r = subprocess.run(["termux-fingerprint", "-t", "CódigoCamp", "-d", "Conectar la terminal de Trabajo a este celular"],
                               capture_output=True, text=True, timeout=120)
            return '"AUTH_RESULT_SUCCESS"' in r.stdout
        except (OSError, subprocess.TimeoutExpired):
            return False
    usuario = getpass.getuser()
    if platform.system() == "Darwin" and shutil.which("dscl"):
        for _ in range(3):
            clave = getpass.getpass(f"  Contraseña de tu Mac ({usuario}): ")
            if subprocess.run(["dscl", "/Local/Default", "-authonly", usuario, clave], capture_output=True).returncode == 0:
                return True
            print(f"  {R}Contraseña incorrecta.{N}")
        return False
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print(f"  {A}Estás como administrador (root): no se puede pedir una contraseña distinta.{N}")
        return True
    print(f"  Escribe la contraseña de tu usuario ({usuario}) de Linux:")
    for _ in range(3):
        if subprocess.run(["su", usuario, "-c", "true"]).returncode == 0:
            return True
    return False


def guardar(datos):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(datos, f)
    try:
        os.chmod(CONFIG, 0o600)
    except OSError:
        pass


def olvidar():
    try:
        os.remove(CONFIG)
    except OSError:
        pass


def actualizar_si_hay(servidor, token):
    """Si CódigoCamp tiene un Conector más nuevo, pregunta y se actualiza solo (tú decides; nunca sin preguntar)."""
    try:
        estado, r = pedir(servidor, "GET", "/api/conector/agente/version", token, espera=15)
        nueva = int(r.get("version") or 0) if estado == 200 else 0
    except Exception:
        return
    if nueva <= VERSION_CONECTOR:
        return
    print(f"  {A}Hay un Conector más nuevo (versión {nueva}; tienes la {VERSION_CONECTOR}).{N}")
    try:
        if input("  ¿Actualizar ahora? (s/n) ").strip().lower() not in {"s", "si", "sí", "y", "yes"}:
            return
    except EOFError:
        return
    try:
        req = urllib.request.Request(servidor + "/api/conector/agente/programa", headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            texto = resp.read().decode("utf-8")
        compile(texto, "codigocamp-conector.py", "exec")            # que sea un programa de Python válido
        if "VERSION_CONECTOR" not in texto or "revisar_comando" not in texto:
            raise ValueError("el programa descargado no es el Conector")
        destino = os.path.realpath(sys.argv[0])
        temporal = destino + ".nuevo"
        with open(temporal, "w", encoding="utf-8") as f:
            f.write(texto)
        os.replace(temporal, destino)
    except Exception as e:
        print(f"  {R}No se pudo actualizar: {e}. Descárgalo de nuevo desde Trabajo.{N}")
        return
    print(f"  {V}✔ Actualizado. Reiniciando el Conector…{N}\n")
    args = [a for a in sys.argv[1:] if not re.fullmatch(r"[A-Za-z0-9]{6}", a)]   # el código ya se usó
    os.execv(sys.executable, [sys.executable, os.path.realpath(sys.argv[0]), *args])


def main():
    ap = argparse.ArgumentParser(description="Conecta la terminal de Trabajo (CódigoCamp) con este equipo.")
    ap.add_argument("codigo", nargs="?", help="código de 6 caracteres que muestra Trabajo → Conectar mi equipo")
    ap.add_argument("--carpeta", default=None, help="carpeta donde se ejecutan los comandos (por defecto, la actual)")
    ap.add_argument("--servidor", default=None, help="dirección de CódigoCamp")
    ap.add_argument("--depurar", action="store_true", help="muestra el detalle técnico si algo falla")
    a = ap.parse_args()

    previo = {}
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG, encoding="utf-8") as f:
                previo = json.load(f)
        except Exception:
            previo = {}
    servidor = (a.servidor or (SERVIDOR if not SERVIDOR.startswith("%") else "") or previo.get("servidor") or "http://localhost:5000").rstrip("/")
    carpeta = os.path.realpath(a.carpeta or (previo.get("carpeta") if not a.codigo else None) or os.getcwd())
    if not os.path.isdir(carpeta):
        print(f"{R}La carpeta no existe: {carpeta}{N}")
        sys.exit(1)

    print(f"\n  {V}▌ Conector de CódigoCamp{N}\n")
    print(f"  Servidor: {servidor}")
    print(f"  Carpeta:  {carpeta}\n")
    print("  Mientras este programa esté abierto, la terminal «Mi equipo» de Trabajo podrá ejecutar comandos en este")
    print("  equipo (empezando en esta carpeta) y copiar archivos dentro de ella, con los mismos permisos que tienes tú.")
    print("  Los comandos peligrosos (borrar el sistema, apagar, desactivar el antivirus…) siempre se bloquean.")
    print(f"\n  {A}Al conectar aceptas los Términos de CódigoCamp (sección 7): eres responsable de los comandos que se")
    print("  ejecuten en tu terminal, de los cambios en tus archivos y bases de datos locales y de guardar en secreto")
    print(f"  tu código y tu token (~/.codigocamp-conector.json). No compartas ni subas ese archivo a GitHub.{N}\n")
    try:
        if input("  ¿Conectar este equipo? (s/n) ").strip().lower() not in {"s", "si", "sí", "y", "yes"}:
            print("  Cancelado.")
            return
    except EOFError:
        return
    if not verificar_dueno():
        print(f"  {R}No se pudo confirmar que eres el dueño del equipo. No se conectó.{N}")
        sys.exit(1)
    print(f"  {V}✔ Identidad confirmada.{N}")

    token = previo.get("token") if previo.get("servidor") == servidor and not a.codigo else None
    if not token:
        if not a.codigo:
            print(f"{A}  Falta el código. En Trabajo: menú de la terminal → «Conectar mi equipo».{N}")
            sys.exit(1)
        sistema = "Android" if "ANDROID_ROOT" in os.environ else platform.system().replace("Darwin", "macOS")
        datos = {"codigo": a.codigo, "equipo": socket.gethostname()[:80] or "Mi equipo", "sistema": sistema, "carpeta": carpeta}
        estado, r, ultimo = None, {}, None
        # localhost y 127.0.0.1 a veces no son lo mismo en Windows (IPv6): se prueban las dos
        candidatos = list(dict.fromkeys([servidor_rapido(servidor), servidor]))
        for x, y in (("//localhost", "//127.0.0.1"), ("//127.0.0.1", "//localhost")):
            if x in servidor:
                candidatos.append(servidor.replace(x, y, 1))
        for intento in range(3):
            for cand in candidatos:
                try:
                    estado, r = pedir(cand, "POST", "/api/conector/agente/vincular", None, datos, espera=25)
                    break
                except ErrorConexion as e:
                    ultimo = e
            if estado is not None:
                break
            print(f"  {A}Reintentando la conexión con CódigoCamp ({intento + 1}/3)…{N}")
            time.sleep(2 + 2 * intento)
        if estado is None:
            print(f"\n  {R}✖ {ultimo}{N}\n")
            sys.exit(1)
        if estado != 200 or not r.get("token"):
            print(f"{R}  {r.get('error') or 'No se pudo conectar (' + str(estado) + ').'}{N}")
            sys.exit(1)
        token = r["token"]
        guardar({"servidor": servidor, "token": token, "carpeta": carpeta})
    else:
        guardar({**previo, "carpeta": carpeta})

    print(f"\n  {V}✔ Conectado.{N} Abre Trabajo → terminal → «Mi equipo». Ctrl+C aquí para desconectar.\n")
    actualizar_si_hay(servidor, token)
    agente = Agente(servidor_rapido(servidor), token, carpeta)
    av = agente.av.estado()
    if av["activo"] is False:
        print(f"  {A}⚠️ Antivirus: {av['nombre']}. Te recomendamos encenderlo (CódigoCamp nunca lo cambia).{N}")
    else:
        print(f"  🛡️ Antivirus: {av['nombre']}" + ("" if av["revisa"] else " (no deja revisar archivos desde otros programas)"))
    try:
        agente.correr()
    except KeyboardInterrupt:
        agente.activo = False
        for p in list(agente.procesos.values()):
            try:
                p.kill()
            except Exception:
                pass
        print(f"\n  {A}Conector cerrado. Trabajo ya no puede usar este equipo.{N}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Conector cerrado.")
    except ErrorConexion as e:   # nunca un «Traceback»: la causa y qué hacer, en español
        print(f"\n  {R}✖ {e}{N}\n")
        sys.exit(1)
    except Exception as e:
        if "--depurar" in sys.argv:
            raise
        print(f"\n  {R}✖ El Conector tuvo un problema: {type(e).__name__}: {e}{N}")
        print("  Si se repite, ejecútalo con --depurar y envía lo que aparece.\n")
        sys.exit(1)
