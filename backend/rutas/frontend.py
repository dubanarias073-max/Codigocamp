"""Sirve las páginas, el CSS, el JS y las imágenes de la carpeta frontend/."""
from flask import Blueprint, abort, send_from_directory

from constantes import FRONTEND

bp = Blueprint("frontend", __name__)


@bp.get("/")
def portada():
    return send_from_directory(FRONTEND, "index.html")


@bp.get("/pages/<path:filename>")
def pagina(filename):
    return send_from_directory(FRONTEND / "pages", filename)


@bp.get("/<path:filename>")
def archivo_frontend(filename):
    if filename.startswith(("api/", "admin/")):
        abort(404)
    return send_from_directory(FRONTEND, filename)
