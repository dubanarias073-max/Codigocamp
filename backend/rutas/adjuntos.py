"""Adjuntos para chats e IA (fotos, videos, audio, PDF, código, cualquier archivo; hasta MAX_ARCHIVO, 1 GB).

Cómo funciona:
  1. El navegador sube el archivo al almacén de la cuenta (POST /api/trabajo/archivos/, en streaming y con progreso).
  2. Con el marcador que devuelve, crea el adjunto: POST /api/adjuntos/ {marcador, nombre, destino: chat|ia}.
  3. Lo manda con el mensaje (chat) o con la pregunta (IA) usando el id del adjunto.
Solo lo ven su dueño y, si va en un chat, la otra persona de esa conversación.
"""
import re

from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user, login_required
from sqlalchemy import or_

from models import Attachment, Friendship, Message, WorkspaceFile, db
from rutas.archivos import EN_NAVEGADOR, MARCADOR, _ruta
from utilidades import api_error, json_body, too_many

bp = Blueprint("adjuntos", __name__)
_NOMBRE_MALO = re.compile(r'[\x00-\x1f\\/:*?"<>|]')


def publico(a):
    return {"id": a.id, "nombre": a.nombre, "tipo": a.tipo, "tamano": a.tamano, "url": f"/api/adjuntos/{a.id}",
            "clase": "imagen" if a.tipo.startswith("image/") else "video" if a.tipo.startswith("video/") else "audio" if a.tipo.startswith("audio/") else "pdf" if a.tipo == "application/pdf" else "archivo"}


@bp.post("/api/adjuntos/")
@login_required
def crear():
    if too_many(f"adjuntos:{current_user.id}", 120, 60):
        return api_error("Demasiados archivos seguidos. Espera un momento.", 429)
    data = json_body()
    if isinstance(data, tuple):
        return data
    m = MARCADOR.match(str(data.get("marcador", "")))
    if not m:
        return api_error("Archivo no válido.")
    archivo = WorkspaceFile.query.filter_by(usuario_id=current_user.id, hash=m.group(1)).first()
    if not archivo:
        return api_error("Ese archivo no está en tu cuenta (súbelo primero).", 404)
    nombre = _NOMBRE_MALO.sub("_", str(data.get("nombre") or "archivo").strip())[:160] or "archivo"
    destino = data.get("destino") if data.get("destino") in ("chat", "ia") else "chat"
    a = Attachment(usuario_id=current_user.id, destino=destino, hash=archivo.hash, nombre=nombre, tipo=archivo.tipo, tamano=archivo.tamano)
    db.session.add(a)
    db.session.commit()
    return jsonify(adjunto=publico(a)), 201


def _puede_ver(a):
    if a.usuario_id == current_user.id:
        return True
    if not a.mensaje_id:
        return False
    msg = db.session.get(Message, a.mensaje_id)
    if not msg:
        return False
    return Friendship.query.filter(Friendship.id == msg.amistad_id, Friendship.estado == "aceptada",
                                   or_(Friendship.de_usuario_id == current_user.id, Friendship.a_usuario_id == current_user.id)).first() is not None


@bp.get("/api/adjuntos/<int:ident>")
@login_required
def ver(ident):
    a = db.session.get(Attachment, ident)
    if not a or not _puede_ver(a):
        return api_error("Archivo no encontrado.", 404)
    ruta = _ruta(a.usuario_id, a.hash)
    if not ruta.exists():
        return api_error("El archivo ya no está disponible.", 410)
    en_navegador = a.tipo in EN_NAVEGADOR and request.args.get("descargar") != "1"
    tipo = a.tipo if en_navegador else "application/octet-stream"
    r = send_file(ruta, mimetype=tipo + ("; charset=utf-8" if tipo.startswith("text/") else ""), as_attachment=not en_navegador,
                  download_name=a.nombre, conditional=True, etag=a.hash, max_age=0)
    r.headers["Cache-Control"] = "private, max-age=31536000, immutable"
    r.headers["Content-Security-Policy"] = "default-src 'none'; object-src 'self'" if tipo == "application/pdf" else "default-src 'none'; sandbox"
    r.headers["X-Content-Type-Options"] = "nosniff"
    return r


def tomar(ids, destino, mensaje_id=None):
    """Valida y devuelve los adjuntos (del usuario actual, sin usar) para un mensaje o una pregunta."""
    if not ids:
        return []
    if not isinstance(ids, list) or len(ids) > 10 or not all(isinstance(i, int) for i in ids):
        raise ValueError("Máximo 10 archivos por mensaje.")
    lista = Attachment.query.filter(Attachment.id.in_(ids), Attachment.usuario_id == current_user.id).all()
    if len(lista) != len(set(ids)):
        raise ValueError("Algún archivo adjunto no existe.")
    for a in lista:
        if destino == "chat":
            if a.mensaje_id:
                raise ValueError("Ese archivo ya se envió.")
            a.mensaje_id = mensaje_id
    return lista
