"""Capas del antivirus de CódigoCamp que miran DENTRO de los archivos según su tipo real (no según el nombre).

- Huellas SHA-256 de virus conocidos (servicios/firmas/sha256.txt, FIRMAS_SHA256 en .env y las que el antivirus aprende).
- Tipo real: accesos directos de Windows (.lnk) y scripts disfrazados de imagen o documento.
- Imágenes con un programa escondido (políglotas: PHP, JavaScript o un .exe pegado dentro de la foto).
- SVG con código (roban la sesión al abrir la imagen).
- PDF con JavaScript que se ejecuta al abrirlo, que lanzan programas o que traen archivos peligrosos dentro.
- Office: macros (.doc/.xls antiguos y .docx/.xlsx con vbaProject), plantillas remotas con macros y campos DDE.
- RTF con objetos incrustados (exploits de Office).

Cada función devuelve None o {"motivo", "gravedad", "explicacion"}.
"""
import hashlib
import os
import re
import threading

AQUI = os.path.dirname(os.path.abspath(__file__))
FIRMAS_BASE = os.path.join(AQUI, "firmas", "sha256.txt")

EXPLICA = {
    "conocido": "La huella digital del archivo coincide con la de un virus ya identificado.",
    "disfraz": "El archivo dice ser una cosa (por su nombre) pero por dentro es otra: es el truco más común para que alguien abra un virus sin darse cuenta.",
    "poliglota": "La imagen trae pegado un programa escondido. Si el servidor o el navegador lo ejecuta, el atacante toma el control.",
    "svg": "Las imágenes SVG pueden llevar código: al abrirlas en el navegador se ejecuta y puede robar la sesión de quien la mire.",
    "pdf": "El PDF trae código o acciones automáticas que se ejecutan al abrirlo; así se usan los PDF para meter virus.",
    "macro": "Las macros de Office son pequeños programas dentro del documento; los virus las usan para instalarse al abrir el archivo.",
    "rtf": "El documento trae un objeto incrustado de los que se usan para aprovechar fallas de Microsoft Office.",
    "lnk": "Un acceso directo de Windows puede ejecutar cualquier orden al hacer doble clic, aunque parezca un documento.",
}


def _h(motivo, gravedad, categoria):
    return {"motivo": motivo, "gravedad": gravedad, "explicacion": EXPLICA[categoria]}


# ------------------------------------------------------------------------------------- huellas conocidas ----
_firmas = None
_firmas_marca = None
_cerrojo = threading.Lock()


def _archivo_aprendidas():
    carpeta = os.environ.get("ALMACEN_ARCHIVOS") or os.path.join(AQUI, "..", "almacen_archivos")
    return os.path.join(carpeta, "firmas_aprendidas.txt")


def _rutas_firmas(aprendidas=True):
    rutas = [FIRMAS_BASE] + ([_archivo_aprendidas()] if aprendidas else [])
    extra = os.environ.get("FIRMAS_SHA256", "")
    rutas += [r.strip() for r in extra.split(os.pathsep) if r.strip()]
    return rutas


def firmas(aprendidas=True):
    """Conjunto de huellas SHA-256 (se vuelve a leer si alguno de los archivos cambió)."""
    global _firmas, _firmas_marca
    if not aprendidas:
        return _leer(_rutas_firmas(False))
    rutas = _rutas_firmas()
    marca = tuple((r, os.path.getmtime(r)) for r in rutas if os.path.exists(r))
    if _firmas is not None and marca == _firmas_marca:
        return _firmas
    nuevas = set()
    for r, _ in marca:
        try:
            with open(r, encoding="utf-8", errors="ignore") as f:
                for linea in f:
                    h = linea.split("#", 1)[0].strip().lower()[:64]
                    if re.fullmatch(r"[0-9a-f]{64}", h):
                        nuevas.add(h)
        except OSError:
            continue
    _firmas, _firmas_marca = nuevas, marca
    return nuevas


def _leer(rutas):
    nuevas = set()
    for r in rutas:
        try:
            with open(r, encoding="utf-8", errors="ignore") as f:
                nuevas.update(h for h in (l.split("#", 1)[0].strip().lower()[:64] for l in f) if re.fullmatch(r"[0-9a-f]{64}", h))
        except OSError:
            continue
    return nuevas


def aprender(huella, nombre=""):
    """Guarda la huella de un archivo peligroso: si alguien lo vuelve a subir (con otro nombre) se reconoce al instante."""
    if not re.fullmatch(r"[0-9a-f]{64}", huella or "") or huella in firmas():
        return
    ruta = _archivo_aprendidas()
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with _cerrojo, open(ruta, "a", encoding="utf-8") as f:
            f.write(f"{huella}  # {os.path.basename(str(nombre))[:60]}\n")
    except OSError:
        pass


def huella_archivo(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(1024 * 1024), b""):
            h.update(trozo)
    return h.hexdigest()


def revisar_huella(huella, aprendidas=True):
    if huella and huella in firmas(aprendidas):
        return _h("coincide con un virus conocido (huella digital)", "critica", "conocido")
    return None


# ---------------------------------------------------------------------------------------------- formatos ----
IMAGENES = {"png", "jpg", "jpeg", "gif", "webp", "bmp", "ico", "tif", "tiff", "avif", "heic"}
DOCUMENTOS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "rtf", "txt", "csv", "md"}
LNK = b"L\x00\x00\x00\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00F"
OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
# Código escondido dentro de una imagen
ESCONDIDO_EN_IMAGEN = re.compile(rb"<\?php|<\?=|<script[\s>]|\beval\s*\(|\b(?:system|shell_exec|passthru|base64_decode)\s*\(\s*\$_|"
                                 rb"This program cannot be run in DOS mode|#!/bin/(?:ba)?sh", re.I)
SCRIPT_AL_INICIO = re.compile(rb"^\s*(?:<\?php|<script[\s>]|#!/|<html|<!doctype html|@echo off|powershell|<hta:)", re.I)
SVG_CODIGO = re.compile(rb"<script[\s>]|\son[a-z]+\s*=\s*['\"]|(?:href|src)\s*=\s*['\"]\s*(?:javascript|data:text/html):|<foreignObject[\s\S]{0,400}<(?:iframe|script)", re.I)


def _ext(nombre):
    n = os.path.basename(str(nombre or "")).lower()
    return n.rsplit(".", 1)[-1] if "." in n else ""


def _nombres_pdf(datos):
    """Los nombres de PDF pueden venir disfrazados con #xx («/J#61vaScript» = /JavaScript)."""
    return re.sub(rb"#([0-9a-fA-F]{2})", lambda m: bytes([int(m.group(1), 16)]), datos)


def revisar_pdf(datos):
    d = _nombres_pdf(datos[: 8 * 1024 * 1024])
    if re.search(rb"/Launch\b", d):
        return _h("el PDF intenta abrir un programa del equipo", "critica", "pdf")
    if re.search(rb"/EmbeddedFile\b", d) and re.search(rb"\.(?:exe|scr|bat|cmd|vbs|js|jse|hta|ps1|lnk|jar|msi)\b", d, re.I):
        return _h("el PDF trae escondido un programa", "critica", "pdf")
    js = re.search(rb"/(?:JavaScript|JS)\b", d)
    auto = re.search(rb"/(?:OpenAction|AA)\b", d)
    if js and auto:
        return _h("el PDF ejecuta JavaScript al abrirse", "alta", "pdf")
    if re.search(rb"/(?:XFA|RichMedia)\b", d) and js:
        return _h("el PDF trae código en formularios o contenido multimedia", "alta", "pdf")
    return None


AUTO_MACRO = re.compile(rb"Auto_?Open|AutoExec|AutoClose|Document_Open|Workbook_Open|Workbook_Activate|Auto_Close|Document_Close", re.I)
MACRO_PELIGROSA = re.compile(rb"\bShell\b|WScript\.Shell|CreateObject|URLDownloadToFile|MSXML2|powershell|cmd\s*/c|Environ\(|Kill\s|\.Run\b|CallByName|ExecuteExcel4Macro", re.I)


def revisar_ole(nombre, datos):
    """Documentos de Office antiguos (.doc, .xls, .ppt): ¿traen macros?"""
    d = datos[: 16 * 1024 * 1024]
    tiene_vba = b"_VBA_PROJECT" in d or b"Attribute VB_" in d or b"VBA\x00" in d.replace(b"\x00\x00", b"")
    if tiene_vba and (AUTO_MACRO.search(d) or MACRO_PELIGROSA.search(d)):
        return _h("el documento trae una macro que se ejecuta sola o que abre programas", "critica", "macro")
    if tiene_vba:
        return _h("el documento trae macros (pequeños programas escondidos)", "alta", "macro")
    if re.search(rb"Excel 4\.0|\bEXEC\s*\(|\bCALL\s*\(\s*\"", d) and AUTO_MACRO.search(d):
        return _h("la hoja de cálculo trae macros antiguas de Excel 4.0 que se ejecutan solas", "critica", "macro")
    return None


def revisar_office_zip(z):
    """Office moderno (.docx/.xlsx/.pptx son zip): macros escondidas, plantillas remotas y campos DDE."""
    nombres = [i.filename for i in z.infolist()[:3000]]
    if any(n.lower().endswith("vbaproject.bin") for n in nombres):
        return _h("el documento trae macros escondidas (vbaProject) aunque su nombre no lo diga", "alta", "macro")
    for n in nombres:
        bajo = n.lower()
        if bajo.endswith(".rels") and ("settings" in bajo or "document" in bajo or "workbook" in bajo):
            try:
                with z.open(n) as f:
                    t = f.read(256 * 1024)
            except Exception:  # noqa: BLE001
                continue
            if re.search(rb"(?:attachedTemplate|oleObject|frame)[^>]*Target\s*=\s*['\"](?:https?:|\\\\)", t, re.I) or \
                    re.search(rb"Target\s*=\s*['\"](?:https?:|\\\\)[^'\"]*\.(?:dotm|docm|xlsm|rtf|hta|exe)['\"]", t, re.I):
                return _h("el documento descarga desde internet una plantilla o un objeto con macros", "critica", "macro")
        if bajo.endswith((".xml",)) and (bajo.startswith(("word/", "xl/", "ppt/"))):
            try:
                with z.open(n) as f:
                    t = f.read(2 * 1024 * 1024)
            except Exception:  # noqa: BLE001
                continue
            if re.search(rb"DDEAUTO|\bDDE\s+[\"']?\w|instr=['\"][^'\"]*\bDDE", t, re.I):
                return _h("el documento trae un campo DDE que ejecuta órdenes al abrirlo", "critica", "macro")
    return None


def revisar_rtf(datos):
    d = datos[: 16 * 1024 * 1024]
    if b"\\objdata" in d and (re.search(rb"\\objupdate|\\objautlink|Equation\.3|Package|\\objocx|OLE2Link|htmlfile", d, re.I)):
        return _h("el documento trae un objeto incrustado que se activa solo (exploit de Office)", "critica", "rtf")
    if re.search(rb"\\objdata", d) and re.search(rb"\.(?:exe|scr|hta|vbs|ps1|bat|cmd)\b", d, re.I):
        return _h("el documento trae un programa incrustado", "critica", "rtf")
    return None


def revisar_bytes(nombre, datos):
    """Revisión según el tipo REAL del contenido (las primeras partes del archivo). Devuelve None o el hallazgo."""
    ext = _ext(nombre)
    if datos.startswith(LNK):
        return _h("es un acceso directo de Windows (.lnk) disfrazado" if ext != "lnk" else "es un acceso directo de Windows (.lnk)", "critica", "lnk")
    if ext in IMAGENES:
        if SCRIPT_AL_INICIO.search(datos[:512]):
            return _h("dice ser una imagen pero por dentro es un programa o una página web", "alta", "disfraz")
        if ESCONDIDO_EN_IMAGEN.search(datos):
            return _h("la imagen trae un programa escondido dentro", "critica", "poliglota")
    if ext == "svg" or datos[:512].lstrip().lower().startswith((b"<svg", b"<?xml")) and b"<svg" in datos[:4096].lower():
        if SVG_CODIGO.search(datos):
            return _h("la imagen SVG trae código que se ejecuta al abrirla", "alta", "svg")
    if datos.startswith(b"%PDF") or ext == "pdf" and b"%PDF" in datos[:1024]:
        return revisar_pdf(datos)
    if datos.startswith(OLE):
        return revisar_ole(nombre, datos)
    if datos.lstrip()[:5].lower() == b"{\\rtf":
        return revisar_rtf(datos)
    if ext in DOCUMENTOS - {"txt", "csv", "md"} and SCRIPT_AL_INICIO.search(datos[:512]) and not datos.startswith((b"%PDF", b"PK")):
        return _h("dice ser un documento pero por dentro es un programa o una página web", "alta", "disfraz")
    return None
