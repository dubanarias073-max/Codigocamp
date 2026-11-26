"""Antivirus de CódigoCamp: revisa cada archivo que se sube (Trabajo, chats e IA usan la misma subida).

Capas (de la más rápida a la más completa):
  1. Firmas y formato: programas ejecutables de Windows/Linux/macOS (aunque les cambien la extensión), la firma de
     prueba EICAR, extensiones peligrosas (.exe, .scr, .vbs, .lnk…), doble extensión («foto.jpg.exe») y documentos de
     Office con macros (.docm, .xlsm…).
  2. Comprimidos (.zip, .jar, .apk, .docx…): se mira dentro sin descomprimir en disco; bomba zip → bloqueado.
  3. ClamAV, si está instalado en el servidor (servicio clamd o el comando clamscan): busca virus conocidos.
     En Ubuntu: sudo apt install clamav clamav-daemon && sudo freshclam

Un archivo bloqueado se borra al instante y no queda guardado en ninguna parte (ni su nombre en los registros).
ANTIVIRUS=0 en backend/.env apaga la revisión (no recomendado).
"""
import io
import os
import shutil
import socket
import struct
import subprocess
import zipfile

EICAR = b"".join((b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$", b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE!"))   # partida (también en el .pyc): así el antivirus de tu PC no confunde este archivo
PELIGROSAS = {
    "exe", "scr", "com", "pif", "cpl", "msi", "msp", "dll", "sys", "drv", "ocx", "hta", "vbs", "vbe", "jse", "wsf", "wsh",
    "lnk", "reg", "inf", "gadget", "application", "msc", "appref-ms", "scf", "url", "iqy", "slk", "xll", "ps1xml",
}
MACROS = {"docm", "dotm", "xlsm", "xltm", "xlam", "pptm", "potm", "ppam", "ppsm", "sldm"}
COMPRIMIDOS = {"zip", "jar", "war", "apk", "aab", "docx", "xlsx", "pptx", "odt", "ods", "odp", "epub", "whl", "nupkg", "vsix", "xpi"}
DISFRAZ = {"pdf", "jpg", "jpeg", "png", "gif", "doc", "docx", "txt", "mp3", "mp4", "xls", "xlsx", "zip", "html", "py", "js"}
MAX_REVISAR_ZIP = 2000       # entradas
MAX_PROPORCION_ZIP = 120     # descomprimido / comprimido
MAX_DESCOMPRIMIDO = 3 * 1024 ** 3
# Archivos de código que se revisan por dentro buscando programas dañinos (servicios/codigo_malicioso.py)
CODIGO = {"py", "pyw", "js", "mjs", "cjs", "ts", "php", "phtml", "php5", "rb", "sh", "bash", "zsh", "fish", "ksh", "command", "bat", "cmd",
          "ps1", "psm1", "psd1", "pl", "lua", "go", "rs", "c", "cc", "cpp", "h", "hpp", "java", "cs", "kt", "swift", "r", "vbs", "vba", "bas",
          "jsx", "tsx", "ipynb", "asp", "aspx", "jsp", "html", "htm", "svg", "txt", "md"}
MAX_CODIGO_REVISAR = 1024 * 1024


def _ext(nombre):
    n = os.path.basename(str(nombre or "")).lower()
    return n.rsplit(".", 1)[-1] if "." in n else ""


def _es_ejecutable(cabeza):
    """Programas compilados: Windows (MZ…PE), Linux (ELF) y macOS (Mach-O)."""
    if cabeza[:2] == b"MZ":
        return "un programa de Windows (.exe)"
    if cabeza[:4] == b"\x7fELF":
        return "un programa de Linux"
    if cabeza[:4] in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe"):
        return "un programa de macOS" if cabeza[:4] != b"\xca\xfe\xba\xbe" else None   # cafebabe también es .class de Java
    return None


def revisar_nombre(nombre):
    """Motivo para bloquear por el nombre, o None."""
    partes = os.path.basename(str(nombre or "")).lower().split(".")
    ext = partes[-1] if len(partes) > 1 else ""
    if ext in PELIGROSAS:
        return f"los archivos .{ext} pueden instalar virus o dañar el equipo"
    if ext in MACROS:
        return f"los documentos .{ext} traen macros, una forma común de esconder virus"
    if len(partes) > 2 and partes[-2] in DISFRAZ and ext in {"bat", "cmd", "ps1", "jar", "vbs", "js"} and partes[-2] != "min":
        return "tiene doble extensión (por ejemplo «foto.jpg.exe»), un truco típico para disfrazar virus"
    if "‮" in str(nombre or ""):
        return "su nombre usa un carácter invisible que invierte el texto para disfrazar la extensión"
    return None


# Carpetas donde un proyecto guarda lo que COMPILA o descarga (dependencias). Un .dll o un .exe ahí es normal
# (un proyecto de C#, Java o C++ comprimido con su carpeta bin/); se siguen revisando la firma de virus y ClamAV.
CARPETAS_BUILD = {"bin", "obj", "target", "build", "dist", "out", "debug", "release", "x64", "x86", "node_modules", "packages",
                  "vendor", "venv", ".venv", "env", "__pycache__", ".gradle", "cmake-build-debug", "cmake-build-release", ".next"}
LIBRERIAS = {"dll", "so", "dylib", "node", "pyd", "class", "wasm", "pdb", "lib", "a", "o", "obj"}


def _de_compilacion(ruta):
    partes = [p.lower() for p in str(ruta).replace("\\", "/").split("/")[:-1]]
    return any(p in CARPETAS_BUILD for p in partes)


def _revisar_zip(datos):
    try:
        z = zipfile.ZipFile(io.BytesIO(datos))
    except (zipfile.BadZipFile, OSError, ValueError):
        return None   # no es un zip válido: lo demás decide
    infos = z.infolist()
    if len(infos) > 20000:
        return "el comprimido tiene demasiados archivos (posible bomba zip)"
    if any(i.flag_bits & 0x1 for i in infos[:MAX_REVISAR_ZIP]):
        return "el comprimido tiene contraseña y no se puede revisar por dentro (así se esconden los virus de los antivirus)"
    from servicios import heuristicas
    if any(i.filename == "[Content_Types].xml" for i in infos[:50]):
        office = heuristicas.revisar_office_zip(z)
        if office:
            return office["motivo"]
    total = 0
    for i, info in enumerate(infos):
        total += info.file_size
        if total > MAX_DESCOMPRIMIDO or (info.compress_size and info.file_size / max(info.compress_size, 1) > MAX_PROPORCION_ZIP and info.file_size > 50 * 1024 ** 2):
            return "el comprimido se infla de forma anormal al abrirlo (bomba zip)"
        if i >= MAX_REVISAR_ZIP:
            continue
        compilado = _de_compilacion(info.filename)
        motivo = revisar_nombre(info.filename)
        if motivo and not info.filename.lower().endswith(".url") and not (compilado and _ext(info.filename) in LIBRERIAS | {"exe"}):
            return f"dentro del comprimido hay «{os.path.basename(info.filename)[:60]}»: {motivo}"
        if info.file_size and not info.is_dir():
            try:
                with z.open(info) as f:
                    cabeza = f.read(64 * 1024)
            except Exception:
                continue
            if EICAR in cabeza:
                return "dentro del comprimido hay un archivo con firma de virus"
            formato = heuristicas.revisar_bytes(info.filename, cabeza)
            if formato:
                return f"dentro del comprimido, «{os.path.basename(info.filename)[:60]}»: {formato['motivo']}"
            if i < 500 and info.file_size <= MAX_CODIGO_REVISAR and _ext(info.filename) in CODIGO:
                try:
                    with z.open(info) as f:
                        hallazgo = _codigo_malicioso(info.filename, f.read(MAX_CODIGO_REVISAR))
                except Exception:
                    hallazgo = None
                if hallazgo:
                    return f"dentro del comprimido, «{os.path.basename(info.filename)[:60]}» contiene un programa malicioso: {hallazgo['motivo']}"
            ej = _es_ejecutable(cabeza)
            if ej and _ext(info.filename) not in LIBRERIAS and not compilado:
                return f"dentro del comprimido hay {ej}"
    return None


def _clamav(ruta):
    """Resultado de ClamAV: None (limpio o sin ClamAV) o el nombre del virus."""
    sock = os.environ.get("CLAMAV_SOCKET") or next((s for s in ("/var/run/clamav/clamd.ctl", "/run/clamav/clamd.ctl", "/var/run/clamd.scan/clamd.sock") if os.path.exists(s)), None)
    if sock:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s, open(ruta, "rb") as f:
                s.settimeout(60)
                s.connect(sock)
                s.sendall(b"zINSTREAM\0")
                while True:
                    trozo = f.read(1024 * 1024)
                    if not trozo:
                        break
                    s.sendall(struct.pack("!L", len(trozo)) + trozo)
                s.sendall(struct.pack("!L", 0))
                respuesta = s.recv(4096).decode(errors="replace").strip("\0 \n")
            if respuesta.endswith("FOUND"):
                return respuesta.split(":", 1)[-1].replace("FOUND", "").strip() or "virus"
            return None
        except OSError:
            pass
    binario = shutil.which("clamdscan") or shutil.which("clamscan")
    if binario:
        try:
            r = subprocess.run([binario, "--no-summary", "--infected", ruta], capture_output=True, text=True, timeout=180)
            if r.returncode == 1:
                return (r.stdout.split(":", 1)[-1].replace("FOUND", "").strip() or "virus")[:80]
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None


def revisar_archivo(ruta, nombre=""):
    """Revisa un archivo ya escrito en disco. Devuelve None si está bien o el motivo (en español) para bloquearlo."""
    r = revisar_archivo_completo(ruta, nombre)
    return r["motivo"] if r else None


def _codigo_malicioso(nombre, datos):
    """Archivos de código (.py, .sh, .php…): busca programas dañinos (shell reversa, minero, robo de claves…)."""
    if _ext(nombre) not in CODIGO or len(datos) > MAX_CODIGO_REVISAR:
        return None
    from servicios.codigo_malicioso import revisar_codigo
    return revisar_codigo(datos.decode("utf-8", "replace"), nombre)


def revisar_archivo_completo(ruta, nombre="", aprender=True):
    """Como revisar_archivo, pero devuelve {"motivo", "gravedad", "explicacion", "evidencia"} (o None) para el aviso."""
    if os.environ.get("ANTIVIRUS", "1") == "0":
        return None

    def r(motivo, gravedad=None, explicacion=None, evidencia=None):
        return {"motivo": motivo, "gravedad": gravedad, "explicacion": explicacion, "evidencia": evidencia or nombre}
    motivo = revisar_nombre(nombre)
    if motivo:
        return r(motivo)
    from servicios import heuristicas
    try:
        huella = heuristicas.huella_archivo(ruta)
    except OSError:
        huella = ""
    conocido = heuristicas.revisar_huella(huella, aprendidas=aprender)   # en modo prueba solo las huellas de fábrica
    if conocido:
        return r(conocido["motivo"], conocido["gravedad"], conocido["explicacion"])
    with open(ruta, "rb") as f:
        cabeza = f.read(16 * 1024 * 1024 if os.path.getsize(ruta) <= 16 * 1024 * 1024 else 1024 * 1024)
    if EICAR in cabeza:
        aprender and heuristicas.aprender(huella, nombre)
        return r("tiene la firma de un virus", "critica")
    formato = heuristicas.revisar_bytes(nombre, cabeza)
    if formato:
        if formato["gravedad"] == "critica":
            aprender and heuristicas.aprender(huella, nombre)
        return r(formato["motivo"], formato["gravedad"], formato["explicacion"])
    ej = _es_ejecutable(cabeza)
    if ej:
        return r(f"es {ej}; por seguridad no se permiten programas compilados")
    if _ext(nombre) in COMPRIMIDOS or cabeza[:4] == b"PK\x03\x04":
        tam = os.path.getsize(ruta)
        if tam <= 300 * 1024 ** 2:
            with open(ruta, "rb") as f:
                motivo = _revisar_zip(f.read())
            if motivo:
                return r(motivo)
    hallazgo = _codigo_malicioso(nombre, cabeza)
    if hallazgo:
        return r(f"contiene un programa malicioso: {hallazgo['motivo']}", hallazgo["gravedad"], hallazgo["explicacion"],
                 f"{nombre}: {hallazgo['fragmento']}" if hallazgo.get("fragmento") else nombre)
    virus = _clamav(ruta)
    if virus:
        aprender and heuristicas.aprender(huella, nombre)
        return r(f"el antivirus encontró «{virus}»", "critica")
    return None


def estado_antivirus():
    """Qué capas están encendidas (se muestra en el panel de administrador)."""
    sock = os.environ.get("CLAMAV_SOCKET") or next((s for s in ("/var/run/clamav/clamd.ctl", "/run/clamav/clamd.ctl", "/var/run/clamd.scan/clamd.sock") if os.path.exists(s)), None)
    binario = shutil.which("clamdscan") or shutil.which("clamscan")
    return {"activo": os.environ.get("ANTIVIRUS", "1") != "0",
            "clamav": "servicio clamd" if sock else ("comando " + os.path.basename(binario)) if binario else None}


# ------------------------------------------------------------------ archivos escritos en el editor de Trabajo ----
_LIMPIOS = {}   # huella -> True: lo que ya se revisó y estaba bien (el autoguardado manda el proyecto entero cada vez)


def revisar_texto(ruta, texto):
    """Archivo creado o escrito DENTRO de Trabajo (llega como texto al guardar el proyecto en la cuenta).
    Misma revisión que una subida: nombre peligroso, firma de virus y código malicioso. Devuelve None o el hallazgo."""
    if os.environ.get("ANTIVIRUS", "1") == "0":
        return None
    import hashlib
    texto = texto or ""
    huella = hashlib.sha1(f"{ruta}\0{texto}".encode("utf-8", "replace")).hexdigest()
    if huella in _LIMPIOS:
        return None

    def r(motivo, gravedad=None, explicacion=None, evidencia=None):
        return {"motivo": motivo, "gravedad": gravedad, "explicacion": explicacion, "evidencia": evidencia or ruta}
    hallazgo = None
    motivo = None if _de_compilacion(ruta) else revisar_nombre(ruta)
    datos = texto.encode("utf-8", "replace")
    from servicios import heuristicas
    conocido = heuristicas.revisar_huella(hashlib.sha256(datos).hexdigest())
    formato = None if motivo or conocido else heuristicas.revisar_bytes(ruta, datos[: 4 * 1024 * 1024])
    if motivo:
        hallazgo = r(motivo)
    elif conocido:
        hallazgo = r(conocido["motivo"], "critica", conocido["explicacion"])
    elif EICAR in datos[: 1024 * 1024]:
        hallazgo = r("tiene la firma de un virus", "critica")
    elif formato:
        hallazgo = r(formato["motivo"], formato["gravedad"], formato["explicacion"])
    else:
        h = _codigo_malicioso(ruta, datos[:MAX_CODIGO_REVISAR])
        if h:
            hallazgo = r(f"contiene un programa malicioso: {h['motivo']}", h["gravedad"], h["explicacion"],
                         f"{ruta}: {h['fragmento']}" if h.get("fragmento") else ruta)
    if hallazgo is None:
        if len(_LIMPIOS) > 50000:
            _LIMPIOS.clear()
        _LIMPIOS[huella] = True
    return hallazgo


# ------------------------------------------------------------------------------------- estado y autoprueba ----
def estado_clamav():
    """{"activo": bool, "version": str, "modo": "servicio"|"programa"|""} (ClamAV es el motor de firmas de virus reales)."""
    sock = os.environ.get("CLAMAV_SOCKET") or next((s for s in ("/var/run/clamav/clamd.ctl", "/run/clamav/clamd.ctl", "/var/run/clamd.scan/clamd.sock") if os.path.exists(s)), None)
    if sock:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(sock)
                s.sendall(b"zVERSION\0")
                v = s.recv(512).decode(errors="replace").strip("\0 \n")
            return {"activo": True, "version": v[:120], "modo": "servicio"}
        except OSError:
            pass
    binario = shutil.which("clamdscan") or shutil.which("clamscan")
    if binario:
        try:
            v = subprocess.run([binario, "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
            return {"activo": True, "version": v[:120], "modo": "programa"}
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {"activo": False, "version": "", "modo": ""}


def autoprueba():
    """Pasa el banco de muestras por el antivirus real (sin registrar faltas). Para el botón «Probar antivirus» del panel."""
    import tempfile
    import time as _t
    from servicios.muestras_antivirus import NORMALES, PELIGROSAS
    resultados = []
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "muestra.bin")
        for peligrosa, lista in ((True, PELIGROSAS), (False, [(n, d, "") for n, d in NORMALES])):
            for nombre, datos, que in lista:
                with open(ruta, "wb") as f:
                    f.write(datos)
                ini = _t.perf_counter()
                h = revisar_archivo_completo(ruta, nombre, aprender=False)
                ms = round((_t.perf_counter() - ini) * 1000, 1)
                resultados.append({"nombre": nombre, "que": que, "peligrosa": peligrosa, "detectado": bool(h), "ok": bool(h) == peligrosa,
                                   "motivo": h["motivo"] if h else "", "gravedad": (h or {}).get("gravedad") or "", "ms": ms})
    return resultados
