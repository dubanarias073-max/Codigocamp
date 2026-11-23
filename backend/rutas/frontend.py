"""Sirve las páginas, el CSS, el JS y las imágenes de la carpeta frontend/."""
from flask import Blueprint, abort, send_from_directory

from constantes import FRONTEND

bp = Blueprint("frontend", __name__)


@bp.get("/")
def portada():
    return _con_politica(send_from_directory(FRONTEND, "index.html"), "index.html")


# Páginas que ejecutan el código del estudiante (vista previa, lecciones, retos): sus iframes heredan la política, así
# que necesitan cargar librerías de cualquier CDN. El resto de la app usa una política estricta: ningún script que no
# sea de CódigoCamp o de los CDN conocidos, y nada de scripts en línea (bloquea la inyección de código / XSS).
CON_CODIGO = {"trabajo.html", "aprende.html", "reto.html", "widget.html"}
COMUN = ("object-src 'none'; base-uri 'self'; frame-ancestors 'self'; "
         "img-src 'self' data: blob: https:; media-src 'self' data: blob: https:; font-src 'self' data: https:; "
         "style-src 'self' 'unsafe-inline' https:; worker-src 'self' blob:; manifest-src 'self'; ")
ESTRICTA = (COMUN + "form-action 'self' https://github.com https://accounts.google.com; default-src 'self'; script-src 'self' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://esm.sh; "
            "script-src-attr 'none'; connect-src 'self' https: wss:; frame-src 'self' blob: data: https:")
PERMISIVA = (COMUN + "form-action 'self' https: http://localhost:* http://127.0.0.1:*; default-src 'self' https: data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data: https:; "
             "connect-src 'self' https: wss: ws://localhost:* ws://127.0.0.1:* http://localhost:* http://127.0.0.1:* blob: data:; frame-src 'self' blob: data: https: http://localhost:* http://127.0.0.1:*")


def _con_politica(respuesta, nombre):
    if respuesta.mimetype == "text/html":
        respuesta.headers["Content-Security-Policy"] = PERMISIVA if nombre in CON_CODIGO else ESTRICTA
    return respuesta


@bp.get("/pages/<path:filename>")
def pagina(filename):
    return _con_politica(send_from_directory(FRONTEND / "pages", filename), filename.rsplit("/", 1)[-1])


@bp.get("/<path:filename>")
def archivo_frontend(filename):
    if filename.startswith(("api/", "admin/")):
        abort(404)
    return send_from_directory(FRONTEND, filename)
