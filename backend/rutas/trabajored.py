"""Internet, correo y «Iniciar con Google» para el Python de Trabajo (corre en el navegador, sin sockets).

Tu backend (FastAPI, Flask, Django…) dentro de Trabajo usa requests/httpx/urllib, smtplib y google-auth como en tu PC;
el Python del navegador manda esas operaciones aquí y CódigoCamp las hace por él:

  POST /api/trabajo/http           una petición HTTP(S) a internet (Gemini, APIs, llaves de Google…)
  POST /api/trabajo/smtp           enviar un correo con TU cuenta (la del .env de tu proyecto)
  POST /api/trabajo/google-token   «Iniciar con Google» en la vista previa: un token con tu cuenta de CódigoCamp
  POST /api/trabajo/google-token/verificar   lo comprueba tu backend (google.oauth2.id_token, parchado en Trabajo)

Seguridad:
  · solo con sesión iniciada y con límite por hora;
  · nunca a direcciones privadas (127.0.0.1, 10.x, 192.168.x, 169.254.x…): nadie puede usar esto para entrar a la red
    del servidor; tampoco por redirecciones;
  · correo solo a puertos de SMTP (25, 465, 587, 2525) y con usuario y contraseña (los tuyos): no es un relay abierto.
  TRABAJO_RED=0 en .env lo apaga.
"""
import base64
import hashlib
import hmac
import ipaddress
import json
import os
import smtplib
from smtplib import SMTP as _SMTP_REAL, SMTP_SSL as _SMTP_SSL_REAL
import socket
import ssl
import time
from urllib.parse import urlsplit

import requests
from flask import Blueprint, current_app, jsonify
from flask_login import current_user, login_required

from utilidades import api_error, json_body, too_many

bp = Blueprint("trabajored", __name__)

MAX_RESPUESTA = 15 * 1024 * 1024
MAX_CORREO = 10 * 1024 * 1024
PUERTOS_SMTP = {25, 465, 587, 2525}
SIN_REENVIAR = {"host", "content-length", "connection", "transfer-encoding", "accept-encoding", "cookie", "proxy-authorization", "upgrade"}


def _activo():
    valor = current_app.config.get("TRABAJO_RED")
    return str(valor if valor is not None else os.getenv("TRABAJO_RED", "1")) == "1"


def problema_host(host):
    """None si el host es público; si no, por qué no se puede usar (no existe, o es de la red local)."""
    try:
        socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError):
        return f"No se encontró el servidor «{host}» (¿está bien escrito? ¿hay internet en el servidor de CódigoCamp?)."
    return None if ip_publica(host) else f"«{host}» no es una dirección pública de internet: desde Trabajo no se puede entrar a la red local."


def ip_publica(host):
    """El host apunta solo a direcciones públicas de internet (nada de la red local ni del propio servidor)."""
    try:
        datos = socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError):
        return False
    if not datos:
        return False
    for *_, direccion in datos:
        ip = ipaddress.ip_address(direccion[0].split("%")[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            return False
        if getattr(ip, "ipv4_mapped", None) and not ip_publica(str(ip.ipv4_mapped)):
            return False
    return True


def _url_permitida(url):
    p = urlsplit(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        return "Solo se pueden pedir direcciones http:// o https://."
    motivo = problema_host(p.hostname)
    if motivo:
        return motivo + (" Si es tu propio backend, usa la vista previa (fetch a /api o a http://localhost:<puerto>)." if "red local" in motivo else "")
    return None


@bp.post("/api/trabajo/http")
@login_required
def http():
    if not _activo():
        return api_error("Este servidor no permite que el Python de Trabajo salga a internet (TRABAJO_RED=0).", 403)
    if too_many(f"red:{current_user.id}", 600, 3600):
        return api_error("Hiciste demasiadas peticiones a internet en esta hora. Espera un poco.", 429)
    datos = json_body()
    if isinstance(datos, tuple):
        return datos
    metodo = str(datos.get("metodo") or "GET").upper()[:10]
    url = str(datos.get("url") or "")
    cabeceras = {str(k): str(v) for k, v in (datos.get("cabeceras") or []) if str(k).lower() not in SIN_REENVIAR}
    try:
        cuerpo = base64.b64decode(datos.get("cuerpo") or "")
    except (ValueError, TypeError):
        return api_error("Cuerpo inválido.")
    if len(cuerpo) > MAX_RESPUESTA:
        return api_error("El cuerpo de la petición es demasiado grande (máximo 15 MB).", 413)
    espera = min(max(float(datos.get("timeout") or 30), 1), 90)
    for _ in range(6):   # redirecciones a mano: cada salto se revisa (no se puede saltar a la red local)
        motivo = _url_permitida(url)
        if motivo:
            return api_error(motivo, 403)
        try:
            r = requests.request(metodo, url, headers=cabeceras, data=cuerpo or None, timeout=espera, allow_redirects=False, stream=True)
        except requests.exceptions.Timeout:
            return jsonify(error="timeout", detalle=f"La conexión a {urlsplit(url).hostname} tardó demasiado."), 200
        except requests.exceptions.RequestException as e:
            return jsonify(error="conexion", detalle=str(e)[:300]), 200
        if r.is_redirect and datos.get("seguir", True):
            url = requests.compat.urljoin(url, r.headers.get("location", ""))
            if r.status_code in (301, 302, 303) and metodo != "HEAD":
                metodo, cuerpo = "GET", b""
            r.close()
            continue
        contenido = b""
        for trozo in r.iter_content(65536):
            contenido += trozo
            if len(contenido) > MAX_RESPUESTA:
                r.close()
                return api_error("La respuesta es demasiado grande (máximo 15 MB).", 413)
        return jsonify(status=r.status_code, motivo=r.reason or "", url=url,
                       cabeceras=[[k, v] for k, v in r.raw.headers.items() if k.lower() not in ("content-encoding", "transfer-encoding", "content-length")],
                       cuerpo=base64.b64encode(contenido).decode())
    return api_error("Demasiadas redirecciones.", 400)


@bp.post("/api/trabajo/smtp")
@login_required
def smtp():
    if not _activo():
        return api_error("Este servidor no permite enviar correos desde Trabajo (TRABAJO_RED=0).", 403)
    if too_many(f"smtp:{current_user.id}", 30, 3600):
        return api_error("Enviaste demasiados correos desde Trabajo en esta hora (máximo 30).", 429)
    datos = json_body()
    if isinstance(datos, tuple):
        return datos
    host, puerto = str(datos.get("host") or "").strip(), int(datos.get("puerto") or 587)
    usuario, clave = str(datos.get("usuario") or ""), str(datos.get("clave") or "")
    para = [str(x) for x in (datos.get("para") or [])][:50]
    if puerto not in PUERTOS_SMTP:
        return api_error(f"Puerto {puerto} no permitido para correo (usa 587, 465, 25 o 2525).", 403)
    motivo = problema_host(host) if host else "Falta el servidor de correo (SMTP_HOST)."
    if motivo:
        return api_error(motivo, 403)
    if not usuario or not clave:
        return api_error("Para enviar correos desde Trabajo hace falta iniciar sesión en el servidor de correo (smtp.login con tu usuario y contraseña de aplicación).", 403)
    if not para:
        return api_error("El correo no tiene destinatarios.")
    try:
        mensaje = base64.b64decode(datos.get("mensaje") or "")
    except (ValueError, TypeError):
        return api_error("Mensaje inválido.")
    if len(mensaje) > MAX_CORREO:
        return api_error("El correo es demasiado grande (máximo 10 MB).", 413)
    modo = datos.get("modo") or ("ssl" if puerto == 465 else "starttls")
    try:
        if modo == "ssl":
            s = _SMTP_SSL_REAL(host, puerto, timeout=20, context=ssl.create_default_context())
        else:
            s = _SMTP_REAL(host, puerto, timeout=20)
        with s:
            s.ehlo()
            if modo == "starttls":
                s.starttls(context=ssl.create_default_context())
                s.ehlo()
            s.login(usuario, clave)
            rechazados = s.sendmail(str(datos.get("de") or usuario), para, mensaje)
    except smtplib.SMTPAuthenticationError as e:
        return jsonify(error="auth", codigo=e.smtp_code, detalle=(e.smtp_error or b"").decode(errors="replace")[:300]), 200
    except smtplib.SMTPRecipientsRefused as e:
        return jsonify(error="destinatarios", detalle=str(e.recipients)[:300]), 200
    except (smtplib.SMTPException, OSError) as e:
        return jsonify(error="smtp", detalle=str(e)[:300]), 200
    return jsonify(rechazados={k: [v[0], v[1].decode(errors="replace") if isinstance(v[1], bytes) else str(v[1])] for k, v in (rechazados or {}).items()})


# --------------------------------------------------- «Iniciar con Google» dentro de la vista previa --
def _clave_token():
    return hashlib.sha256(("trabajo-google:" + str(current_app.config["SECRET_KEY"])).encode()).digest()


def _b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _deb64(t):
    return base64.urlsafe_b64decode(t + "=" * (-len(t) % 4))


@bp.post("/api/trabajo/google-token")
@login_required
def google_token():
    """Token con la forma de un ID token de Google, para la cuenta de CódigoCamp de quien prueba su app en Trabajo.
    Solo lo acepta el backend de esa misma persona dentro de Trabajo (lo verifica /verificar, nunca Google)."""
    if too_many(f"gtoken:{current_user.id}", 60, 3600):
        return api_error("Demasiados intentos.", 429)
    datos = json_body()
    if isinstance(datos, tuple):
        return datos
    ahora = int(time.time())
    foto = None
    try:
        foto = current_user.profile.foto_url if current_user.profile else None
    except AttributeError:
        foto = None
    reclamos = {
        "iss": "https://accounts.google.com", "azp": str(datos.get("aud") or "")[:200], "aud": str(datos.get("aud") or "")[:200],
        "sub": f"codigocamp-{current_user.id}", "email": current_user.email, "email_verified": True,
        "name": current_user.nombre, "given_name": current_user.nombre.split(" ")[0], "picture": foto,
        "iat": ahora, "exp": ahora + 3600, "nonce": datos.get("nonce"), "cc_dueno": current_user.id,
    }
    cabeza = _b64(json.dumps({"alg": "HS256", "typ": "JWT", "kid": "codigocamp-trabajo"}).encode())
    cuerpo = _b64(json.dumps({k: v for k, v in reclamos.items() if v is not None}).encode())
    firma = _b64(hmac.new(_clave_token(), f"{cabeza}.{cuerpo}".encode(), hashlib.sha256).digest())
    return jsonify(credential=f"{cabeza}.{cuerpo}.{firma}", email=current_user.email, nombre=current_user.nombre)


@bp.post("/api/trabajo/google-token/verificar")
@login_required
def google_token_verificar():
    datos = json_body()
    if isinstance(datos, tuple):
        return datos
    try:
        cabeza, cuerpo, firma = str(datos.get("token") or "").split(".")
        esperada = _b64(hmac.new(_clave_token(), f"{cabeza}.{cuerpo}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(esperada, firma):
            raise ValueError("firma")
        reclamos = json.loads(_deb64(cuerpo))
    except (ValueError, TypeError):
        return api_error("Token de Google (Trabajo) inválido.", 401)
    if reclamos.get("cc_dueno") != current_user.id:
        return api_error("Ese token es de otra cuenta de CódigoCamp.", 401)
    if int(reclamos.get("exp", 0)) < time.time():
        return api_error("El token de Google (Trabajo) venció. Vuelve a iniciar sesión.", 401)
    aud = datos.get("aud")
    if aud and reclamos.get("aud") and aud != reclamos["aud"]:
        return api_error("El token es para otro GOOGLE_CLIENT_ID.", 401)
    reclamos.pop("cc_dueno", None)
    return jsonify(reclamos=reclamos)
