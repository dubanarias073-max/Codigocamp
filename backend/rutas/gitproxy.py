"""Proxy del protocolo Git (smart HTTP) para el Git real de Trabajo (isomorphic-git en el navegador).

GitHub, GitLab… no permiten que una página web hable directamente con sus servidores Git (CORS). El navegador
le pide a CódigoCamp /api/git/<host>/<repo>/info/refs | git-upload-pack | git-receive-pack y CódigoCamp lo
reenvía tal cual, en streaming. Solo a los hosts permitidos y solo esas tres rutas del protocolo.

El token de GitHub viaja en la cabecera Authorization de esa petición y se reenvía al host; CódigoCamp no lo guarda.
backend/.env:  GIT_HOSTS=github.com,gitlab.com,bitbucket.org,codeberg.org   (hosts a los que se puede clonar/enviar)
"""
import os
import re

import requests
from flask import Blueprint, Response, current_app, request, stream_with_context
from flask_login import current_user, login_required

from utilidades import api_error, too_many

bp = Blueprint("gitproxy", __name__)

HOSTS = ("github.com", "gitlab.com", "bitbucket.org", "codeberg.org")
_RUTA = re.compile(r"^[A-Za-z0-9._~/-]{1,300}/(info/refs|git-upload-pack|git-receive-pack)$")
_CABECERAS_IDA = ("Authorization", "Content-Type", "Accept", "Git-Protocol", "Content-Encoding")
_CABECERAS_VUELTA = ("Content-Type", "Cache-Control", "Expires", "Pragma", "WWW-Authenticate")
MAX_ENVIO = 2 * 1024 ** 3  # 2 GB por push


def _hosts():
    valor = current_app.config.get("GIT_HOSTS") or os.getenv("GIT_HOSTS", "")
    return [h.strip().lower() for h in valor.split(",") if h.strip()] or list(HOSTS)


@bp.route("/api/git/<host>/<path:ruta>", methods=["GET", "POST"])
@login_required
def proxy(host, ruta):
    host = host.lower()
    if host not in _hosts():
        return api_error(f"CódigoCamp no permite Git con «{host}». Hosts permitidos: {', '.join(_hosts())}.", 403)
    if ".." in ruta or not _RUTA.fullmatch(ruta):
        return api_error("Ruta de Git no válida.", 400)
    servicio = request.args.get("service")
    if ruta.endswith("info/refs"):
        if request.method != "GET" or servicio not in ("git-upload-pack", "git-receive-pack"):
            return api_error("Petición de Git no válida.", 400)
    elif request.method != "POST":
        return api_error("Petición de Git no válida.", 405)
    if too_many(f"git:{current_user.id}", 300, 60):
        return api_error("Demasiadas operaciones de Git seguidas. Espera un momento.", 429)
    largo = request.content_length
    if largo is not None and largo > MAX_ENVIO:
        return api_error("El envío es demasiado grande.", 413)

    url = f"https://{host}/{ruta}" + (f"?service={servicio}" if servicio else "")
    cabeceras = {k: request.headers[k] for k in _CABECERAS_IDA if k in request.headers}
    cabeceras["User-Agent"] = "git/2.45 (CodigoCamp)"
    try:
        arriba = requests.request(
            request.method, url, headers=cabeceras, stream=True, allow_redirects=False, timeout=(10, 300),
            data=request.stream if request.method == "POST" else None,
        )
    except requests.RequestException:
        return api_error(f"No se pudo conectar con {host}. Revisa la conexión del servidor.", 502)
    if 300 <= arriba.status_code < 400:
        arriba.close()
        return api_error(f"{host} redirigió la petición (¿el repositorio cambió de nombre?).", 502)

    def cuerpo():
        try:
            for trozo in arriba.iter_content(64 * 1024):
                yield trozo
        finally:
            arriba.close()

    respuesta = Response(stream_with_context(cuerpo()), status=arriba.status_code)
    for k in _CABECERAS_VUELTA:
        if k in arriba.headers:
            if k == "WWW-Authenticate":
                # Sin esto el navegador mostraría su propia ventana de usuario/clave; el token se pide en la terminal.
                respuesta.headers["X-Git-Auth"] = "required"
                continue
            respuesta.headers[k] = arriba.headers[k]
    respuesta.headers["Cache-Control"] = "no-store"
    return respuesta
