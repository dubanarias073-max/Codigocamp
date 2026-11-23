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

EICAR = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!"
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


def _revisar_zip(datos):
    try:
        z = zipfile.ZipFile(io.BytesIO(datos))
    except (zipfile.BadZipFile, OSError, ValueError):
        return None   # no es un zip válido: lo demás decide
    infos = z.infolist()
    if len(infos) > 20000:
        return "el comprimido tiene demasiados archivos (posible bomba zip)"
    total = 0
    for i, info in enumerate(infos):
        total += info.file_size
        if total > MAX_DESCOMPRIMIDO or (info.compress_size and info.file_size / max(info.compress_size, 1) > MAX_PROPORCION_ZIP and info.file_size > 50 * 1024 ** 2):
            return "el comprimido se infla de forma anormal al abrirlo (bomba zip)"
        if i >= MAX_REVISAR_ZIP:
            continue
        motivo = revisar_nombre(info.filename)
        if motivo and not info.filename.lower().endswith(".url"):
            return f"dentro del comprimido hay «{os.path.basename(info.filename)[:60]}»: {motivo}"
        if info.file_size and not info.is_dir():
            try:
                with z.open(info) as f:
                    cabeza = f.read(64 * 1024)
            except Exception:
                continue
            if EICAR in cabeza:
                return "dentro del comprimido hay un archivo con firma de virus"
            ej = _es_ejecutable(cabeza)
            if ej and _ext(info.filename) not in {"so", "dylib", "node", "pyd", "class", "wasm"}:
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
    if os.environ.get("ANTIVIRUS", "1") == "0":
        return None
    motivo = revisar_nombre(nombre)
    if motivo:
        return motivo
    with open(ruta, "rb") as f:
        cabeza = f.read(1024 * 1024)
    if EICAR in cabeza:
        return "tiene la firma de un virus"
    ej = _es_ejecutable(cabeza)
    if ej:
        return f"es {ej}; por seguridad no se permiten programas compilados"
    if _ext(nombre) in COMPRIMIDOS or cabeza[:4] == b"PK\x03\x04":
        tam = os.path.getsize(ruta)
        if tam <= 300 * 1024 ** 2:
            with open(ruta, "rb") as f:
                motivo = _revisar_zip(f.read())
            if motivo:
                return motivo
    virus = _clamav(ruta)
    if virus:
        return f"el antivirus encontró «{virus}»"
    return None
