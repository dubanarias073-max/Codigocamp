"""Sirve las páginas, el CSS, el JS y las imágenes de la carpeta frontend/."""
import gzip
import mimetypes
import os
import re
import threading
from collections import OrderedDict

from flask import Blueprint, Response, abort, request, send_from_directory
from werkzeug.security import safe_join

from constantes import FRONTEND

bp = Blueprint("frontend", __name__)


@bp.get("/")
def portada():
    return _con_politica(_servir(FRONTEND, "index.html"), "index.html")


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


# ---- Rápido: comprimido (gzip) y caché larga para lo que tiene huella en el nombre -----------------------------
# El JS, el CSS y el HTML viajan comprimidos (pesan ~70 % menos: Trabajo carga mucho más rápido en celulares y redes
# lentas). Lo comprimido se guarda en memoria, así no se vuelve a comprimir en cada visita.
COMPRIMIBLES = {".js", ".mjs", ".css", ".html", ".json", ".svg", ".webmanifest", ".txt", ".map", ".xml", ".py", ".md", ".wasm", ".data"}
_gz = OrderedDict()            # (ruta, mtime, tamaño) -> bytes comprimidos
_gz_peso = 0
_gz_lock = threading.Lock()
MAX_GZ = 64 * 1024 * 1024
HUELLA = re.compile(r"-[A-Za-z0-9_-]{8}\.(js|css)$")   # archivos de Monaco con huella: nunca cambian


def _comprimido(ruta, st):
    global _gz_peso
    clave = (ruta, st.st_mtime_ns, st.st_size)
    with _gz_lock:
        if clave in _gz:
            _gz.move_to_end(clave)
            return _gz[clave]
    with open(ruta, "rb") as f:
        datos = gzip.compress(f.read(), compresslevel=6, mtime=0)
    with _gz_lock:
        _gz[clave] = datos
        _gz_peso += len(datos)
        while _gz_peso > MAX_GZ and _gz:
            _, viejo = _gz.popitem(last=False)
            _gz_peso -= len(viejo)
    return datos


def _servir(carpeta, nombre):
    """Como send_from_directory, pero comprime si el navegador lo acepta y cachea para siempre lo que tiene huella."""
    ruta = safe_join(str(carpeta), nombre)
    ext = os.path.splitext(nombre)[1].lower()
    if ruta and ext in COMPRIMIBLES and "gzip" in request.headers.get("Accept-Encoding", "") and os.path.isfile(ruta):
        st = os.stat(ruta)
        if st.st_size > 1024:
            etag = f'W/"{st.st_mtime_ns:x}-{st.st_size:x}-gz"'
            inmutable = "/vendor/" in ruta.replace(os.sep, "/") and bool(HUELLA.search(nombre))
            cache = "public, max-age=31536000, immutable" if inmutable else "no-cache"
            if request.headers.get("If-None-Match") == etag:
                r = Response(status=304)
            else:
                tipo = {".webmanifest": "application/manifest+json", ".mjs": "text/javascript", ".js": "text/javascript", ".md": "text/markdown", ".wasm": "application/wasm"}.get(ext) \
                    or mimetypes.guess_type(nombre)[0] or "application/octet-stream"
                r = Response(_comprimido(ruta, st), mimetype=tipo)
                r.headers["Content-Encoding"] = "gzip"
            r.headers["ETag"] = etag
            r.headers["Cache-Control"] = cache
            r.headers["Vary"] = "Accept-Encoding"
            return r
    r = send_from_directory(carpeta, nombre)
    if HUELLA.search(nombre) and nombre.startswith("vendor/"):
        r.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return r


def _con_politica(respuesta, nombre):
    if respuesta.mimetype == "text/html":
        respuesta.headers["Content-Security-Policy"] = PERMISIVA if nombre in CON_CODIGO else ESTRICTA
    return respuesta


@bp.get("/pages/<path:filename>")
def pagina(filename):
    return _con_politica(_servir(FRONTEND / "pages", filename), filename.rsplit("/", 1)[-1])


@bp.get("/<path:filename>")
def archivo_frontend(filename):
    if filename.startswith(("api/", "admin/")):
        abort(404)
    return _servir(FRONTEND, filename)
