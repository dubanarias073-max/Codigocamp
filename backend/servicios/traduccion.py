"""Traducción de textos para la versión en inglés (retos, lecciones, avisos del servidor). Ver servicios/traduccion.py."""
from flask import Blueprint, jsonify, request
from flask_login import current_user

from utilidades import api_error, json_body, too_many

bp = Blueprint("traduccion", __name__)


@bp.post("/api/traducir/")
def traducir_textos():
    from servicios.traduccion import IDIOMAS, MAX_TEXTO, traducir
    data = json_body()
    if isinstance(data, tuple):
        return data
    idioma = str(data.get("idioma") or "en")
    textos = data.get("textos")
    if idioma not in IDIOMAS or not isinstance(textos, list) or not textos:
        return api_error("Faltan los textos o el idioma.")
    textos = [str(t)[:MAX_TEXTO] for t in textos[:80]]
    quien = f"u{current_user.id}" if current_user.is_authenticated else (request.remote_addr or "anon")
    con_ia = not too_many(f"traducir:{quien}", 40, 60)
    lista, nuevos = traducir(textos, idioma, con_ia=con_ia)
    return jsonify(textos=lista, nuevos=nuevos)
