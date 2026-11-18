"""Archivos del espacio de trabajo (imágenes, videos, audio, PDF, fuentes, datos…): subir, listar y servir.

Dónde viven: en disco, en ALMACEN_ARCHIVOS/<usuario>/<hash[:2]>/<hash> (configurable en backend/.env).
MySQL solo guarda la lista (tabla archivos_trabajo); así no hay límite de 16 MB por archivo ni de max_allowed_packet.

Límites (backend/.env):  CUOTA_ARCHIVOS_GB=10  (por cuenta)   MAX_ARCHIVO_MB=1024  (por archivo)

Seguridad:
  · Se sube por streaming (nunca se carga el archivo entero en memoria) y se corta si pasa del máximo.
  · El tipo se decide por los primeros bytes o la extensión. Solo los tipos «inofensivos» (imágenes, video, audio,
    PDF, fuentes, texto plano) se muestran en el navegador; todo lo demás (HTML, SVG, ejecutables…) se sirve como
    descarga application/octet-stream. Siempre con nosniff y CSP restrictiva.
  · Solo su dueño puede verlos, o quien tenga un enlace firmado que caduca (lo usa la vista previa aislada).
  · Antes de guardar se comprueba que quede espacio libre en el disco del servidor.
  · Lo que el proyecto ya no usa se borra solo una hora después (limpiar_huerfanas).
"""
import hashlib
import os
import re
import secrets
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file, url_for
from flask_login import current_user, login_required
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import func

from models import UserWorkspace, WorkspaceFile, db
from utilidades import api_error, json_body, too_many

bp = Blueprint("archivos", __name__)

MARGEN_LIMPIEZA = timedelta(hours=1)
VIGENCIA_ENLACE = 6 * 3600
RESERVA_DISCO = 1024 ** 3  # se deja siempre 1 GB libre en el disco del servidor
_HASH = re.compile(r"^[a-f0-9]{64}$")
MARCADOR = re.compile(r"^cc(?:img|bin):v1:([a-f0-9]{64}):[a-z]+/[a-z0-9.+-]{1,60}:\d{1,13}$")

_POR_EXTENSION = {
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp", "avif": "image/avif",
    "bmp": "image/bmp", "ico": "image/x-icon", "mp4": "video/mp4", "m4v": "video/mp4", "mov": "video/quicktime", "webm": "video/webm",
    "ogv": "video/ogg", "mp3": "audio/mpeg", "m4a": "audio/mp4", "wav": "audio/wav", "ogg": "audio/ogg", "oga": "audio/ogg",
    "pdf": "application/pdf", "ttf": "font/ttf", "otf": "font/otf", "woff": "font/woff", "woff2": "font/woff2",
    "zip": "application/zip", "txt": "text/plain", "csv": "text/csv", "json": "application/json",
}
EN_NAVEGADOR = {
    "image/png", "image/jpeg", "image/gif", "image/webp", "image/avif", "image/bmp", "image/x-icon",
    "video/mp4", "video/webm", "video/ogg", "video/quicktime", "audio/mpeg", "audio/mp4", "audio/wav", "audio/ogg", "audio/webm",
    "application/pdf", "font/ttf", "font/otf", "font/woff", "font/woff2", "text/plain", "text/csv",
}


def tipo_de(cabeza, nombre=""):
    """Tipo MIME según los primeros bytes; si no se reconoce, según la extensión; si no, application/octet-stream."""
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if cabeza.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if cabeza.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if cabeza[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if len(cabeza) >= 12 and cabeza[:4] == b"RIFF" and cabeza[8:12] == b"WEBP":
        return "image/webp"
    if len(cabeza) >= 12 and cabeza[:4] == b"RIFF" and cabeza[8:12] == b"WAVE":
        return "audio/wav"
    if cabeza.startswith(b"%PDF-"):
        return "application/pdf"
    if len(cabeza) >= 12 and cabeza[4:8] == b"ftyp":
        return "audio/mp4" if ext == "m4a" else "video/quicktime" if cabeza[8:12] == b"qt  " else "video/mp4"
    if cabeza.startswith(b"\x1a\x45\xdf\xa3"):
        return "video/webm"
    if cabeza.startswith(b"OggS"):
        return "video/ogg" if ext == "ogv" else "audio/ogg"
    if cabeza.startswith(b"ID3") or cabeza[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "audio/mpeg"
    if cabeza.startswith(b"wOF2"):
        return "font/woff2"
    if cabeza.startswith(b"wOFF"):
        return "font/woff"
    return _POR_EXTENSION.get(ext, "application/octet-stream")


def _almacen():
    return Path(current_app.config["ALMACEN_ARCHIVOS"])


def _ruta(usuario_id, huella):
    return _almacen() / str(int(usuario_id)) / huella[:2] / huella


def hashes_usados(archivos, git):
    """Huellas que aparecen en los archivos del proyecto o en su último commit."""
    usados = set()
    for fuente in (archivos or {}, (git or {}).get("committed") or {}):
        if not isinstance(fuente, dict):
            continue
        for texto in fuente.values():
            if isinstance(texto, str) and texto.startswith("cc"):
                m = MARCADOR.match(texto)
                if m:
                    usados.add(m.group(1))
    return usados


def limpiar_huerfanas(usuario_id, archivos, git):
    """Borra (fila y bytes) los archivos que el proyecto ya no usa y que tienen más de una hora."""
    usados = hashes_usados(archivos, git)
    limite = datetime.now(timezone.utc) - MARGEN_LIMPIEZA
    borrar = []
    for ident, huella, creado in WorkspaceFile.query.filter_by(usuario_id=usuario_id).with_entities(
            WorkspaceFile.id, WorkspaceFile.hash, WorkspaceFile.creado_en).all():
        if creado is not None and creado.tzinfo is None:
            creado = creado.replace(tzinfo=timezone.utc)
        if huella not in usados and creado is not None and creado < limite:
            borrar.append((ident, huella))
    if borrar:
        WorkspaceFile.query.filter(WorkspaceFile.id.in_([i for i, _ in borrar])).delete(synchronize_session=False)
        for _, huella in borrar:
            try:
                _ruta(usuario_id, huella).unlink(missing_ok=True)
            except OSError:
                pass  # lo recoge «flask limpiar-archivos»
    return len(borrar)


def _uso(usuario_id):
    return int(db.session.query(func.coalesce(func.sum(WorkspaceFile.tamano), 0)).filter(
        WorkspaceFile.usuario_id == usuario_id).scalar() or 0)


def _limites(usuario_id):
    c = current_app.config
    return {"uso": _uso(usuario_id), "limite": c["CUOTA_ARCHIVOS"], "max_archivo": c["MAX_ARCHIVO"]}


def _gb(n):
    return f"{n / 1024 ** 3:.2f} GB" if n >= 1024 ** 3 else f"{n / 1024 ** 2:.1f} MB"


def _sin_espacio(uso, extra):
    libre = max(0, current_app.config["CUOTA_ARCHIVOS"] - uso)
    return api_error(
        f"No queda espacio en tu cuenta para este archivo ({_gb(extra)}): usas {_gb(uso)} de {_gb(current_app.config['CUOTA_ARCHIVOS'])} "
        f"y quedan {_gb(libre)}. Borra archivos que ya no uses; el espacio se libera una hora después de guardar.", 413)


def _liberar_si_falta(usuario_id, uso, extra):
    if uso + extra <= current_app.config["CUOTA_ARCHIVOS"]:
        return uso
    from rutas.trabajo import leer_proyecto
    proyecto = leer_proyecto(UserWorkspace.query.filter_by(usuario_id=usuario_id).first())
    if proyecto is not None and limpiar_huerfanas(usuario_id, proyecto.get("files"), proyecto.get("git")):
        db.session.commit()
        return _uso(usuario_id)
    return uso


@bp.get("/api/trabajo/archivos/")
@login_required
def listar():
    filas = WorkspaceFile.query.filter_by(usuario_id=current_user.id).with_entities(
        WorkspaceFile.hash, WorkspaceFile.tipo, WorkspaceFile.tamano).all()
    return jsonify(archivos=[{"hash": h, "tipo": t, "tamano": s} for h, t, s in filas], **_limites(current_user.id))


@bp.post("/api/trabajo/archivos/")
@login_required
def subir():
    maximo = current_app.config["MAX_ARCHIVO"]
    largo = request.content_length
    if largo is not None and largo > maximo:
        return api_error(f"El archivo pesa {_gb(largo)}; el máximo por archivo es {_gb(maximo)}.", 413)
    if too_many(f"archivos:{current_user.id}", 1200, 60):
        return api_error("Estás subiendo demasiados archivos seguidos. Espera un minuto.", 429)
    uso = _uso(current_user.id)
    if largo:
        uso = _liberar_si_falta(current_user.id, uso, largo)
        if uso + largo > current_app.config["CUOTA_ARCHIVOS"]:
            return _sin_espacio(uso, largo)
    carpeta = _almacen() / str(int(current_user.id))
    carpeta.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(carpeta).free < (largo or 0) + RESERVA_DISCO:
        return api_error("El servidor se está quedando sin espacio en disco. Avísale a quien administra CódigoCamp.", 507)

    temporal = carpeta / f".subida-{secrets.token_hex(8)}"
    huella = hashlib.sha256()
    total = 0
    cabeza = b""
    try:
        with open(temporal, "wb") as destino:
            while True:
                trozo = request.stream.read(1024 * 1024)
                if not trozo:
                    break
                total += len(trozo)
                if total > maximo:
                    raise ValueError("grande")
                if len(cabeza) < 64:
                    cabeza += trozo[:64 - len(cabeza)]
                huella.update(trozo)
                destino.write(trozo)
    except ValueError:
        temporal.unlink(missing_ok=True)
        return api_error(f"El archivo pasa del máximo de {_gb(maximo)} por archivo.", 413)
    except OSError:
        temporal.unlink(missing_ok=True)
        return api_error("No se pudo guardar el archivo en el servidor (¿disco lleno?).", 507)
    if total == 0:
        temporal.unlink(missing_ok=True)
        return api_error("El archivo está vacío.")

    hexa = huella.hexdigest()
    tipo = tipo_de(cabeza, request.args.get("nombre", "")[:200])
    existente = WorkspaceFile.query.filter_by(usuario_id=current_user.id, hash=hexa).first()
    final = _ruta(current_user.id, hexa)
    if existente is not None:
        if final.exists():
            temporal.unlink(missing_ok=True)
        else:  # el disco había perdido el archivo: se repone con esta subida
            final.parent.mkdir(parents=True, exist_ok=True)
            os.replace(temporal, final)
        existente.creado_en = datetime.now(timezone.utc)  # se renueva: la limpieza no lo borra mientras se guarda el proyecto
        tipo = existente.tipo
    else:
        uso = _liberar_si_falta(current_user.id, _uso(current_user.id), total)
        if uso + total > current_app.config["CUOTA_ARCHIVOS"]:
            temporal.unlink(missing_ok=True)
            return _sin_espacio(uso, total)
        final.parent.mkdir(parents=True, exist_ok=True)
        os.replace(temporal, final)
        db.session.add(WorkspaceFile(usuario_id=current_user.id, hash=hexa, tipo=tipo, tamano=total))
    db.session.commit()
    return jsonify(hash=hexa, tipo=tipo, tamano=total, marcador=f"ccbin:v1:{hexa}:{tipo}:{total}", **_limites(current_user.id)), 201


def _enviar(usuario_id, huella):
    archivo = WorkspaceFile.query.filter_by(usuario_id=usuario_id, hash=huella).first()
    ruta = _ruta(usuario_id, huella) if archivo else None
    if archivo is None or not ruta.exists():
        return api_error("Archivo no encontrado.", 404)
    en_navegador = archivo.tipo in EN_NAVEGADOR and request.args.get("descargar") != "1"
    tipo = archivo.tipo if en_navegador else "application/octet-stream"
    if tipo.startswith("text/"):
        tipo += "; charset=utf-8"
    nombre = re.sub(r"[^A-Za-z0-9_.-]", "_", request.args.get("nombre", "") or huella)[:120]
    respuesta = send_file(ruta, mimetype=tipo, as_attachment=not en_navegador, download_name=nombre, conditional=True, etag=huella, max_age=0)
    respuesta.headers["Cache-Control"] = "private, max-age=31536000, immutable"
    # Los PDF necesitan el visor del navegador, que no funciona con «sandbox»; el resto queda totalmente aislado.
    respuesta.headers["Content-Security-Policy"] = "default-src 'none'; object-src 'self'" if tipo == "application/pdf" else "default-src 'none'; sandbox"
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    return respuesta


@bp.get("/api/trabajo/archivos/<huella>")
@login_required
def servir(huella):
    if not _HASH.fullmatch(huella):
        return api_error("Archivo no encontrado.", 404)
    return _enviar(current_user.id, huella)


def _firmador():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="archivos-trabajo")


@bp.post("/api/trabajo/archivos/enlaces/")
@login_required
def enlaces():
    """Enlaces temporales (6 h) para la vista previa: el iframe aislado no envía la sesión, así que no puede usar /archivos/<hash>."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    pedidas = data.get("hashes")
    if not isinstance(pedidas, list) or len(pedidas) > 2000:
        return api_error("Lista de archivos no válida.")
    pedidas = {h for h in pedidas if isinstance(h, str) and _HASH.fullmatch(h)}
    propias = {h for (h,) in WorkspaceFile.query.filter(WorkspaceFile.usuario_id == current_user.id,
                                                        WorkspaceFile.hash.in_(pedidas)).with_entities(WorkspaceFile.hash)} if pedidas else set()
    firmador = _firmador()
    return jsonify(enlaces={h: url_for("archivos.publico", token=firmador.dumps([current_user.id, h]), _external=True) for h in propias},
                   vigencia=VIGENCIA_ENLACE)


@bp.get("/api/trabajo/archivos/p/<token>")
def publico(token):
    try:
        usuario_id, huella = _firmador().loads(token, max_age=VIGENCIA_ENLACE)
    except (BadSignature, ValueError, TypeError):
        return api_error("Enlace vencido o no válido.", 404)
    if not isinstance(huella, str) or not _HASH.fullmatch(huella) or not isinstance(usuario_id, int):
        return api_error("Enlace no válido.", 404)
    return _enviar(usuario_id, huella)


def limpiar_disco(app):
    """Borra del disco lo que ya no está en la base (cuentas eliminadas, subidas interrumpidas). Devuelve cuántos."""
    base = Path(app.config["ALMACEN_ARCHIVOS"])
    if not base.exists():
        return 0
    conocidos = {(u, h) for u, h in WorkspaceFile.query.with_entities(WorkspaceFile.usuario_id, WorkspaceFile.hash).all()}
    viejo = datetime.now().timestamp() - 24 * 3600
    borrados = 0
    for carpeta in base.iterdir():
        if not carpeta.is_dir() or not carpeta.name.isdigit():
            continue
        uid = int(carpeta.name)
        for archivo in carpeta.rglob("*"):
            if not archivo.is_file():
                continue
            if archivo.name == "proyecto.json":
                continue  # el proyecto de la cuenta, no un archivo subido
            temporal = archivo.name.startswith((".subida-", ".proyecto-"))
            if (temporal and archivo.stat().st_mtime < viejo) or (not temporal and (uid, archivo.name) not in conocidos):
                archivo.unlink(missing_ok=True)
                borrados += 1
    return borrados
