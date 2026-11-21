"""Enlace «en vivo» de Trabajo, como Live Server de VS Code.

Tu proyecto se puede abrir en cualquier navegador con una dirección de verdad:
    /live/<clave>/              -> index.html
    /live/<clave>/contacto.html -> otra página;  /live/<clave>/css/estilos.css, imágenes, etc.
Los enlaces entre páginas, el CSS, el JavaScript y las imágenes funcionan como en un servidor normal, y la página se
recarga sola cuando guardas (pregunta cada segundo a /live/<clave>/__cc_version).

Seguridad: el código de la página corre AISLADO (Content-Security-Policy: sandbox, sin allow-same-origin), así que
aunque se sirva desde CódigoCamp no puede leer la sesión ni usar la cuenta de quien la abre. Cualquiera con el enlace
ve la página (como cuando compartes la de Live Server en tu red); con «Cambiar enlace» el anterior deja de servir.
"""
import mimetypes
import re
import secrets

from flask import Blueprint, Response, jsonify, redirect, request
from flask_login import current_user, login_required

from models import UserWorkspace, db
from rutas.archivos import _enviar
from rutas.trabajo import _marca, leer_proyecto

bp = Blueprint("live", __name__)

_CLAVE = re.compile(r"^[A-Za-z0-9_-]{8,24}$")
_MARCADOR = re.compile(r"^cc(?:img|bin):v1:([a-f0-9]{64}):")
SANDBOX = "sandbox allow-scripts allow-forms allow-popups allow-modals allow-downloads allow-popups-to-escape-sandbox"
TIPOS = {
    "html": "text/html", "htm": "text/html", "css": "text/css", "js": "text/javascript", "mjs": "text/javascript", "cjs": "text/javascript",
    "json": "application/json", "svg": "image/svg+xml", "txt": "text/plain", "md": "text/plain", "csv": "text/csv", "xml": "application/xml",
    "webmanifest": "application/manifest+json", "map": "application/json", "py": "text/plain", "java": "text/plain", "sql": "text/plain",
    "php": "text/plain", "ts": "text/plain", "tsx": "text/plain", "jsx": "text/plain",
}

# Va al principio de cada página: localStorage/sessionStorage en memoria (el aislamiento los bloquea) y recarga en vivo.
_SCRIPT = """<script>(function(){try{localStorage.length}catch(e){var M=function(){var d={};return{getItem:function(k){return Object.prototype.hasOwnProperty.call(d,k)?d[k]:null},setItem:function(k,v){d[k]=String(v)},removeItem:function(k){delete d[k]},clear:function(){d={}},key:function(i){return Object.keys(d)[i]||null},get length(){return Object.keys(d).length}}};try{Object.defineProperty(window,"localStorage",{value:M(),configurable:true});Object.defineProperty(window,"sessionStorage",{value:M(),configurable:true})}catch(x){}}
if(window.top!==window&&window.name==="cc-sin-recarga")return;var V=%(version)s,U=%(url)s,f=0;function mirar(){fetch(U,{cache:"no-store"}).then(function(r){return r.json()}).then(function(j){f=0;if(j.v!==V){V=j.v;location.reload()}}).catch(function(){f++}).then(function(){setTimeout(mirar,f>5?5000:1000)})}setTimeout(mirar,1000)})();</script>"""


def _base(clave):
    return f"/live/{clave}"


def _cabeceras(resp):
    resp.headers["Content-Security-Policy"] = SANDBOX
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


def _no_encontrado(clave, ruta, archivos=None):
    paginas = sorted(r for r in (archivos or {}) if r.lower().endswith((".html", ".htm")))
    lista = "".join(f'<li><a href="{_base(clave)}/{_esc(p)}">{_esc(p)}</a></li>' for p in paginas[:200])
    html = (f'<!doctype html><meta charset="utf-8"><title>No encontrado</title><body style="font:15px system-ui;padding:28px;max-width:640px">'
            f"<h2>Cannot GET /{_esc(ruta)}</h2><p>No hay ningún archivo en esa dirección de tu proyecto.</p>"
            + (f"<p>Páginas de tu proyecto:</p><ul>{lista}</ul>" if lista else "") + "</body>")
    return _cabeceras(Response(html, 404, mimetype="text/html"))


def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _workspace(clave):
    if not _CLAVE.fullmatch(clave or ""):
        return None
    return UserWorkspace.query.filter_by(live_clave=clave).first()


def _absolutas(texto, base, html=True):
    """Las rutas absolutas de tu proyecto («/css/estilos.css») apuntan a la raíz del proyecto, como en Live Server."""
    if html:
        texto = re.sub(r'(\s(?:href|src|action|poster|data-src)\s*=\s*["\'])/(?!/)', lambda m: f"{m.group(1)}{base}/", texto, flags=re.I)
    return re.sub(r'url\(\s*(["\']?)/(?!/)', lambda m: f"url({m.group(1)}{base}/", texto)


def _con_script(html, version, url_version):
    script = _SCRIPT % {"version": _json(version), "url": _json(url_version)}
    m = re.search(r"<head[^>]*>", html, re.I)
    if m:
        return html[:m.end()] + script + html[m.end():]
    m = re.search(r"<html[^>]*>", html, re.I)
    if m:
        return html[:m.end()] + script + html[m.end():]
    return script + html


def _json(v):
    import json
    return json.dumps(v).replace("<", "\\u003c")


# --------------------------------------------------------------------------------- API (con sesión) ----
def _mi_workspace(crear=True):
    ws = UserWorkspace.query.filter_by(usuario_id=current_user.id).first()
    if ws is None and crear:
        ws = UserWorkspace(usuario_id=current_user.id, archivos={}, carpetas=[], git={})
        db.session.add(ws)
    return ws


def _respuesta(ws):
    base = request.host_url.rstrip("/")
    return jsonify(activo=bool(ws and ws.live_clave), url=f"{base}{_base(ws.live_clave)}/" if ws and ws.live_clave else None)


@bp.get("/api/trabajo/live/")
@login_required
def estado_live():
    """Devuelve (y si no existe, crea) tu enlace en vivo."""
    ws = _mi_workspace()
    if not ws.live_clave:
        ws.live_clave = secrets.token_urlsafe(12)[:16]
        db.session.commit()
    return _respuesta(ws)


@bp.post("/api/trabajo/live/cambiar/")
@login_required
def cambiar_live():
    """Nuevo enlace: el anterior deja de funcionar al instante."""
    ws = _mi_workspace()
    ws.live_clave = secrets.token_urlsafe(12)[:16]
    db.session.commit()
    return _respuesta(ws)


@bp.delete("/api/trabajo/live/")
@login_required
def apagar_live():
    ws = _mi_workspace(crear=False)
    if ws is not None:
        ws.live_clave = None
        db.session.commit()
    return jsonify(activo=False, url=None)


# ------------------------------------------------------------------------------ páginas públicas ----
@bp.get("/live/<clave>/__cc_version")
def version_live(clave):
    ws = _workspace(clave)
    resp = jsonify(v=_marca(ws) if ws else None)
    if ws is None:
        resp.status_code = 404
    return _cabeceras(resp)


@bp.get("/live/<clave>")
def raiz_sin_barra(clave):
    return redirect(f"{_base(clave)}/", 302)


@bp.get("/live/<clave>/")
@bp.get("/live/<clave>/<path:ruta>")
def servir_live(clave, ruta=""):
    ws = _workspace(clave)
    if ws is None:
        return _cabeceras(Response("<!doctype html><meta charset=utf-8><body style='font:15px system-ui;padding:28px'><h2>Este enlace ya no funciona</h2><p>Pídele a quien te lo pasó el enlace nuevo de su vista previa.</p>", 404, mimetype="text/html"))
    proyecto = leer_proyecto(ws) or {"files": {}}
    archivos = proyecto.get("files") or {}
    carpetas = set(proyecto.get("folders") or [])
    ruta = ruta.strip("/") if ruta.endswith("/") else ruta
    # carpeta -> su index.html (con la barra final, para que los enlaces relativos funcionen)
    if ruta == "" or ruta in carpetas or any(r.startswith(ruta + "/") for r in archivos) and ruta not in archivos:
        if ruta and not request.path.endswith("/"):
            return redirect(f"{_base(clave)}/{ruta}/", 302)
        candidata = f"{ruta}/index.html" if ruta else "index.html"
        if candidata not in archivos:
            # sin index.html en la raíz: la primera página que haya
            paginas = sorted((r for r in archivos if r.lower().endswith((".html", ".htm")) and (not ruta or r.startswith(ruta + "/"))), key=lambda r: (r.count("/"), r))
            if not paginas:
                return _no_encontrado(clave, ruta, archivos)
            return redirect(f"{_base(clave)}/{paginas[0]}", 302)
        ruta = candidata
    if ruta not in archivos:
        return _no_encontrado(clave, ruta, archivos)
    texto = archivos[ruta]
    if not isinstance(texto, str):
        return _no_encontrado(clave, ruta, archivos)
    m = _MARCADOR.match(texto)
    if m:
        resp = _enviar(ws.usuario_id, m.group(1))
        if isinstance(resp, tuple):
            return _no_encontrado(clave, ruta, archivos)
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    ext = ruta.rsplit(".", 1)[-1].lower() if "." in ruta.rsplit("/", 1)[-1] else ""
    tipo = TIPOS.get(ext) or mimetypes.guess_type(ruta)[0] or "text/plain"
    base = _base(clave)
    if tipo == "text/html":
        texto = _con_script(_absolutas(texto, base), _marca(ws), f"{base}/__cc_version")
    elif tipo == "text/css":
        texto = _absolutas(texto, base, html=False)
    if tipo.startswith("text/") or tipo in {"application/json", "image/svg+xml", "application/xml", "application/manifest+json"}:
        tipo += "; charset=utf-8"
    return _cabeceras(Response(texto, 200, content_type=tipo))
