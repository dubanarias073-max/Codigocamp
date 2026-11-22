"""«Iniciar sesión con GitHub» para git push / pull / clone en Trabajo (como VS Code o Git Credential Manager).

Dos formas, las dos con una OAuth App de GitHub (github.com/settings/developers → New OAuth App):

1. Ventana emergente (flujo web): necesita GITHUB_CLIENT_ID + GITHUB_CLIENT_SECRET y que la «Authorization callback URL»
   de la app sea <tu dirección>/auth/github/callback/  (GITHUB_REDIRECT_URI si tienes varias direcciones).
2. Código de dispositivo (como `gh auth login`): solo necesita GITHUB_CLIENT_ID y marcar «Enable Device Flow» en la app.
   Funciona desde cualquier dirección (localhost, el túnel de Tailscale…), porque GitHub no tiene que volver a CódigoCamp.

El token de GitHub NO se guarda en la base de datos ni en el servidor: pasa directo a la pestaña de Trabajo,
que lo guarda solo mientras esa pestaña siga abierta (sessionStorage).
"""
import json
import os
import secrets
import time

import requests
from flask import Blueprint, current_app, jsonify, redirect, request, session, url_for
from flask_login import current_user, login_required

from utilidades import api_error, direccion_actual, direcciones, json_body, too_many

bp = Blueprint("github", __name__)

ALCANCES = "repo workflow read:user user:email"   # repo: push/pull privados · workflow: subir .github/workflows
_UA = {"User-Agent": "CodigoCamp", "Accept": "application/json"}


def _cfg(nombre):
    return (current_app.config.get(nombre) or os.getenv(nombre, "")).strip().strip('"')


def _redirect_uri():
    lista = direcciones(_cfg("GITHUB_REDIRECT_URI"), quitar_barra=False)
    return direccion_actual(lista) if lista else url_for("github.callback", _external=True)


def _web_disponible():
    """La ventana emergente solo sirve si GitHub puede volver a la dirección por la que entró la persona."""
    if not (_cfg("GITHUB_CLIENT_ID") and _cfg("GITHUB_CLIENT_SECRET")):
        return False
    lista = direcciones(_cfg("GITHUB_REDIRECT_URI"), quitar_barra=False)
    if not lista:
        return True
    from urllib.parse import urlsplit
    host = (request.host or "").lower()
    return any(urlsplit(u).netloc.lower() == host for u in lista)


@bp.get("/api/github/config/")
@login_required
def config():
    cid = _cfg("GITHUB_CLIENT_ID")
    dispositivo = bool(cid) and _cfg("GITHUB_DEVICE_FLOW").lower() not in ("0", "no", "false")
    return jsonify(web=_web_disponible(), dispositivo=dispositivo, configurado=bool(cid))


# ------------------------------------------------------------------------------ ventana emergente ----
@bp.get("/auth/github/")
@login_required
def iniciar():
    if not _web_disponible():
        return _pagina(None, "El inicio de sesión con GitHub no está configurado para esta dirección.", "")
    estado = request.args.get("estado", "")
    if not (8 <= len(estado) <= 80) or not estado.replace("-", "").replace("_", "").isalnum():
        return _pagina(None, "Petición no válida.", "")
    session["gh_estado"] = estado
    from urllib.parse import urlencode
    datos = {"client_id": _cfg("GITHUB_CLIENT_ID"), "redirect_uri": _redirect_uri(), "scope": ALCANCES, "state": estado, "allow_signup": "true"}
    if request.args.get("otra") == "1":
        datos["prompt"] = "select_account"   # agregar otra cuenta: GitHub deja elegir con cuál entrar
    q = urlencode(datos)
    return redirect(f"https://github.com/login/oauth/authorize?{q}")


@bp.get("/auth/github/callback/")
@login_required
def callback():
    estado = request.args.get("state", "")
    esperado = session.pop("gh_estado", None)
    if not esperado or not secrets.compare_digest(estado, esperado):
        return _pagina(None, "La sesión de GitHub venció o no coincide. Vuelve a intentarlo desde Trabajo.", estado)
    if request.args.get("error"):
        return _pagina(None, "Cancelaste el inicio de sesión en GitHub." if request.args["error"] == "access_denied" else f"GitHub respondió: {request.args.get('error_description') or request.args['error']}", estado)
    try:
        r = requests.post("https://github.com/login/oauth/access_token", headers=_UA, timeout=15, data={
            "client_id": _cfg("GITHUB_CLIENT_ID"), "client_secret": _cfg("GITHUB_CLIENT_SECRET"),
            "code": request.args.get("code", ""), "redirect_uri": _redirect_uri(),
        })
        datos = r.json()
    except (requests.RequestException, ValueError):
        return _pagina(None, "El servidor no pudo conectar con GitHub.", estado)
    if not datos.get("access_token"):
        return _pagina(None, f"GitHub no entregó el token: {datos.get('error_description') or datos.get('error') or r.status_code}", estado)
    return _pagina(datos["access_token"], None, estado, datos.get("scope", ""))


def _pagina(token, error, estado, alcance=""):
    """Página mínima que entrega el token a la pestaña de Trabajo (misma dirección) y se cierra."""
    mensaje = {"tipo": "cc-github", "estado": estado, "token": token, "error": error, "alcance": alcance}
    datos = json.dumps(mensaje).replace("<", "\\u003c")
    titulo = "Listo: ya puedes volver a CódigoCamp" if token else "No se pudo iniciar sesión"
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitHub · CódigoCamp</title><meta name="referrer" content="no-referrer">
<style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b1020;color:#e5eaff;font:16px system-ui,sans-serif;text-align:center;padding:20px}}
.c{{max-width:420px}}h1{{font-size:20px}}p{{opacity:.8}}button{{margin-top:12px;padding:10px 18px;border:0;border-radius:8px;background:#caff4e;font-weight:700;cursor:pointer}}</style></head>
<body><div class="c"><h1>{'✅' if token else '⚠️'} {titulo}</h1><p id="m">{'Esta ventana se cerrará sola.' if token else (error or '')}</p>
<button type="button" onclick="window.close()">Cerrar ventana</button></div>
<script>(function(){{var d={datos};
try{{var c=new BroadcastChannel("cc-github");c.postMessage(d);setTimeout(function(){{c.close()}},1500)}}catch(e){{}}
try{{localStorage.setItem("cc-github-ping",JSON.stringify(d));setTimeout(function(){{localStorage.removeItem("cc-github-ping")}},4000)}}catch(e){{}}
try{{if(window.opener)window.opener.postMessage(d,location.origin)}}catch(e){{}}
if(d.token)setTimeout(function(){{window.close()}},900);}})();</script></body></html>"""
    respuesta = current_app.response_class(html, mimetype="text/html")
    respuesta.headers["Cache-Control"] = "no-store"
    respuesta.headers["Referrer-Policy"] = "no-referrer"
    return respuesta


# ------------------------------------------------------------------------- código de dispositivo ----
@bp.post("/api/github/dispositivo/")
@login_required
def dispositivo():
    cid = _cfg("GITHUB_CLIENT_ID")
    if not cid:
        return api_error("El inicio de sesión con GitHub no está configurado (falta GITHUB_CLIENT_ID en backend/.env).", 503)
    if too_many(f"ghdev:{current_user.id}", 10, 300):
        return api_error("Demasiados intentos. Espera unos minutos.", 429)
    try:
        r = requests.post("https://github.com/login/device/code", headers=_UA, timeout=15, data={"client_id": cid, "scope": ALCANCES})
        datos = r.json()
    except (requests.RequestException, ValueError):
        return api_error("El servidor no pudo conectar con GitHub.", 502)
    if not datos.get("device_code"):
        motivo = datos.get("error_description") or datos.get("error") or f"HTTP {r.status_code}"
        if datos.get("error") == "device_flow_disabled":
            motivo = "Activa «Enable Device Flow» en la OAuth App de GitHub."
        return api_error(f"GitHub no dio un código: {motivo}", 502)
    sesiones = session.get("gh_disp", {})
    clave = secrets.token_urlsafe(12)
    sesiones = {k: v for k, v in sesiones.items() if v.get("vence", 0) > time.time()}
    sesiones[clave] = {"codigo": datos["device_code"], "vence": time.time() + int(datos.get("expires_in", 900))}
    session["gh_disp"] = sesiones
    return jsonify(id=clave, codigo=datos["user_code"], url=datos.get("verification_uri", "https://github.com/login/device"),
                   intervalo=max(5, int(datos.get("interval", 5))), vence=int(datos.get("expires_in", 900)))


@bp.post("/api/github/dispositivo/sondear/")
@login_required
def sondear():
    clave = str(json_body().get("id", ""))
    sesiones = session.get("gh_disp", {})
    info = sesiones.get(clave)
    if not info or info.get("vence", 0) < time.time():
        return api_error("El código venció. Vuelve a iniciar sesión.", 410)
    try:
        r = requests.post("https://github.com/login/oauth/access_token", headers=_UA, timeout=15, data={
            "client_id": _cfg("GITHUB_CLIENT_ID"), "device_code": info["codigo"], "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        })
        datos = r.json()
    except (requests.RequestException, ValueError):
        return jsonify(pendiente=True, intervalo=10)
    if datos.get("access_token"):
        sesiones.pop(clave, None)
        session["gh_disp"] = sesiones
        return jsonify(token=datos["access_token"], alcance=datos.get("scope", ""))
    error = datos.get("error")
    if error in ("authorization_pending", "slow_down"):
        return jsonify(pendiente=True, intervalo=int(datos.get("interval", 5)) + (5 if error == "slow_down" else 0))
    sesiones.pop(clave, None)
    session["gh_disp"] = sesiones
    if error == "access_denied":
        return api_error("Cancelaste el inicio de sesión en GitHub.", 400)
    if error == "expired_token":
        return api_error("El código venció. Vuelve a iniciar sesión.", 410)
    return api_error(f"GitHub respondió: {datos.get('error_description') or error or r.status_code}", 502)
