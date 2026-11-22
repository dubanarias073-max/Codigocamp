"""Cuenta de usuario: ver sesión, registrarse, entrar y salir."""
import re
import secrets

from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, current_app, jsonify, redirect, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from rutas.trabajo import limpiar_almacen_de_id
from models import Profile, User, db
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from servicios.correo import _config, ajustes_de, avisar_cambio_clave, describir_dispositivo, enlace_restablecer, registrar_inicio
from seguridad import cerrar_sesiones, iniciar_sesion
from servicios.perfil import _user, ensure_identity, serialize_user
from utilidades import api_error, client_ip, direccion_actual, direcciones, json_body, too_many, valid_password

from servicios.zona import iso  # noqa: E402

bp = Blueprint("auth", __name__)
oauth = OAuth()


def configurar_google(app):
    oauth.init_app(app)
    if app.config["GOOGLE_CLIENT_ID"] and app.config["GOOGLE_CLIENT_SECRET"]:
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )


@bp.get("/auth/google/")
def google_login():
    if not current_app.config["GOOGLE_CLIENT_ID"] or not current_app.config["GOOGLE_CLIENT_SECRET"]:
        return redirect("/pages/login.html?error=google_config")
    # GOOGLE_REDIRECT_URI puede tener varias (localhost y el túnel): se usa la de la dirección por la que entró la persona.
    redirect_uri = direccion_actual(direcciones(current_app.config["GOOGLE_REDIRECT_URI"], quitar_barra=False)) or url_for(
        "auth.google_callback", _external=True,
    )
    # Si entró por otra dirección (127.0.0.1 y Google vuelve a localhost, por ejemplo), primero se pasa a la de Google:
    # si no, la sesión del inicio queda en una dirección y Google vuelve a otra, y nunca deja entrar.
    from urllib.parse import urlsplit
    destino = urlsplit(redirect_uri)
    if destino.netloc and destino.netloc.lower() != (request.host or "").lower() and request.args.get("paso") != "1":
        extra = "&app=1" if request.args.get("app") == "1" else ""
        if extra and re.fullmatch(r"[a-f0-9]{64}", str(request.args.get("espera", ""))):
            extra += f"&espera={request.args['espera']}"
        return redirect(f"{destino.scheme}://{destino.netloc}/auth/google/?paso=1{extra}")
    # Desde la app de Android: Google no deja entrar dentro de la app, así que esto corre en el navegador del celular y al
    # final se vuelve a la app con un código de un solo uso (ver google_callback y /api/auth/app/entrar).
    if request.args.get("app") == "1":
        session["google_app"] = True
        espera = str(request.args.get("espera", "")).lower()
        if re.fullmatch(r"[a-f0-9]{64}", espera):
            session["google_app_espera"] = espera
        else:
            session.pop("google_app_espera", None)
    else:
        session.pop("google_app", None)
        session.pop("google_app_espera", None)
    # select_account: Google siempre deja elegir (o agregar) otra cuenta en vez de entrar con la última usada.
    return oauth.google.authorize_redirect(redirect_uri, prompt="select_account")


@bp.get("/auth/google/callback/")
def google_callback():
    try:
        oauth.google.authorize_access_token()
        identity = oauth.google.userinfo()
    except OAuthError as e:
        current_app.logger.warning("Google no completó el inicio de sesión: %s", getattr(e, "error", e))
        motivo = "estado" if "state" in str(getattr(e, "error", "") or e).lower() else "rechazo" if getattr(e, "error", "") == "access_denied" else "otro"
        return redirect(f"/pages/login.html?error=google&motivo={motivo}")

    subject = identity.get("sub") if identity else None
    email = str(identity.get("email", "")).strip().lower() if identity else ""
    if not subject or not email or identity.get("email_verified") is not True:
        return redirect("/pages/login.html?error=google_email")

    user = User.query.filter_by(google_id=subject).first()
    nuevo = False
    if user is None:
        user = User.query.filter_by(email=email).first()
        if user and user.google_id and user.google_id != subject:
            return redirect("/pages/login.html?error=google_conflict")
        if user is None:
            nombre = str(identity.get("name") or email.split("@", 1)[0]).strip()[:50] or "Estudiante"
            user = User(
                email=email,
                nombre=nombre,
                google_id=subject,
                password_hash=generate_password_hash(secrets.token_urlsafe(48)),
            )
            db.session.add(user)
            db.session.flush()
            limpiar_almacen_de_id(user.id)
            profile = Profile(user=user)
            ensure_identity(profile, nombre)
            db.session.add(profile)
            nuevo = True
        else:
            user.google_id = subject

    if not user.activo:
        return redirect("/pages/login.html?error=google_inactive")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return redirect("/pages/login.html?error=google_conflict")
    if session.pop("google_app", False):
        # Se entró desde la app: la sesión NO se abre en este navegador, sino en la app (con el código).
        return _volver_a_la_app(user, nuevo)
    _entrar(user, "Google")
    _avisar_inicio(user, "Google", nuevo)
    destination = "/pages/inicio.html" if user.profile and user.profile.onboarding_completo else "/pages/onboarding.html"
    return redirect(destination)


# ---------- Entrar con Google desde la app de Android ----------
SEGUNDOS_CODIGO_APP = 180
PAQUETE_APP = "com.codigocamp.app"


def _hash_codigo(codigo):
    import hashlib
    return hashlib.sha256(codigo.encode()).hexdigest()


def _volver_a_la_app(user, nuevo):
    from datetime import timedelta

    from models import AppLoginCode, utcnow
    AppLoginCode.query.filter(AppLoginCode.creado < utcnow() - timedelta(hours=1)).delete()
    codigo = secrets.token_urlsafe(32)
    db.session.add(AppLoginCode(codigo_hash=_hash_codigo(codigo), usuario_id=user.id, nuevo=nuevo, espera_hash=session.pop("google_app_espera", None)))
    db.session.commit()
    from urllib.parse import quote
    respaldo = quote(f"{request.host_url.rstrip('/')}/pages/login.html?error=app", safe="")
    intento = f"intent://entrar?c={codigo}#Intent;scheme=codigocamp-app;package={PAQUETE_APP};S.browser_fallback_url={respaldo};end"
    directo = f"codigocamp-app://entrar?c={codigo}"
    nombre = (user.nombre or "").split(" ")[0]
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Volviendo a CódigoCamp</title><meta name="robots" content="noindex"></head>
<body style="margin:0;min-height:100vh;display:grid;place-items:center;background:#0b1020;color:#e5eaff;font:16px system-ui;text-align:center;padding:24px;box-sizing:border-box">
<div style="max-width:360px"><div style="font-size:52px">✅</div><h2 style="margin:8px 0">¡Listo{', ' + _esc_html(nombre) if nombre else ''}!</h2>
<p style="opacity:.8;line-height:1.5">Entraste con Google. Vuelve a la app de CódigoCamp: ya tiene tu sesión abierta (y tu widget se conecta solo). Puedes cerrar esta pestaña.</p>
<a id="ir" href="{intento}" style="display:block;margin-top:18px;padding:15px 22px;border-radius:14px;background:#caff4e;color:#04130d;font-weight:800;text-decoration:none">Abrir la app CódigoCamp</a>
<p style="opacity:.6;font-size:13px;margin-top:16px">Este enlace sirve una sola vez y vence en 3 minutos.</p></div>
<script>setTimeout(function(){{location.href={_json_js(intento)}}},300);document.getElementById("ir").addEventListener("click",function(e){{if(!/android/i.test(navigator.userAgent)){{e.preventDefault();location.href={_json_js(directo)}}}}});</script>
</body></html>"""
    resp = current_app.response_class(html, mimetype="text/html")
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


def _esc_html(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _json_js(v):
    import json
    return json.dumps(v).replace("<", "\\u003c")


@bp.get("/api/auth/app/entrar")
def entrar_desde_app():
    """La app abre esta dirección con el código que le pasó el navegador: la sesión queda en la app (y su widget)."""
    from datetime import timedelta

    from models import AppLoginCode, utcnow
    codigo = str(request.args.get("c", ""))[:100]
    if too_many(f"app-entrar:{client_ip()}", 20, 600):
        return redirect("/pages/login.html?error=app")
    fila = AppLoginCode.query.filter_by(codigo_hash=_hash_codigo(codigo)).first() if codigo else None
    creado = fila.creado if fila else None
    if creado is not None and creado.tzinfo is None:
        from datetime import timezone
        creado = creado.replace(tzinfo=timezone.utc)
    if fila is None or fila.usado or creado < utcnow() - timedelta(seconds=SEGUNDOS_CODIGO_APP):
        return redirect("/pages/login.html?error=app")
    fila.usado = True
    db.session.commit()
    user = db.session.get(User, fila.usuario_id)
    if user is None or not user.activo:
        return redirect("/pages/login.html?error=google_inactive")
    _entrar(user, "Google")
    _avisar_inicio(user, "Google", fila.nuevo)
    destino = "/pages/inicio.html" if user.profile and user.profile.onboarding_completo else "/pages/onboarding.html"
    return redirect(destino + "?app=1")


@bp.post("/api/auth/app/esperar")
def esperar_desde_app():
    """La app pregunta cada 2 s mientras eliges tu cuenta de Google en el navegador. Cuando Google termina, la sesión se
    abre aquí (en la app), aunque el navegador no haya podido volver a la app. Solo la app conoce el secreto: el
    navegador únicamente vio su sha256."""
    from datetime import timedelta

    from models import AppLoginCode, utcnow
    secreto = str((request.get_json(silent=True) or {}).get("secreto", ""))[:100]
    if not re.fullmatch(r"[A-Za-z0-9_-]{30,100}", secreto) or too_many(f"app-esperar:{client_ip()}", 200, 600):
        return jsonify(listo=False), 400
    fila = AppLoginCode.query.filter_by(espera_hash=_hash_codigo(secreto)).order_by(AppLoginCode.id.desc()).first()
    creado = fila.creado if fila else None
    if creado is not None and creado.tzinfo is None:
        from datetime import timezone
        creado = creado.replace(tzinfo=timezone.utc)
    if fila is None or fila.usado or creado < utcnow() - timedelta(seconds=SEGUNDOS_CODIGO_APP):
        return jsonify(listo=False)
    fila.usado = True
    db.session.commit()
    user = db.session.get(User, fila.usuario_id)
    if user is None or not user.activo:
        return jsonify(listo=False, error="Esta cuenta está desactivada."), 403
    _entrar(user, "Google")
    _avisar_inicio(user, "Google", fila.nuevo)
    destino = "/pages/inicio.html" if user.profile and user.profile.onboarding_completo else "/pages/onboarding.html"
    return jsonify(listo=True, destino=destino + "?app=1")


@bp.get("/api/auth/me/")
def yo():
    return jsonify(user=_user(current_user) if current_user.is_authenticated else None)


@bp.post("/api/auth/register/")
def registro():
    if too_many(f"auth:{client_ip()}", 15, 900):
        return api_error("Demasiados intentos. Espera unos minutos.", 429)
    data = json_body()
    if isinstance(data, tuple):
        return data
    nombre = str(data.get("nombre", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not 2 <= len(nombre) <= 50:
        return api_error("El nombre debe tener entre 2 y 50 caracteres.")
    if len(email) > 150 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return api_error("Correo electrónico no válido.")
    if not valid_password(password):
        return api_error("La contraseña debe tener mínimo 6 caracteres, una mayúscula y un número.")
    if User.query.filter_by(email=email).first():
        return api_error("Ese correo ya está registrado.", 409)
    user = User(email=email, nombre=nombre, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.flush()
    limpiar_almacen_de_id(user.id)
    profile = Profile(user=user)
    ensure_identity(profile, nombre)
    db.session.add(profile)
    db.session.flush()
    user_data = serialize_user(user, profile)
    db.session.commit()
    _entrar(user, "contraseña")
    _avisar_inicio(user, "contraseña", True)
    return jsonify(user=user_data), 201


@bp.post("/api/auth/login/")
def entrar():
    if too_many(f"auth:{client_ip()}", 15, 900):
        return api_error("Demasiados intentos. Espera unos minutos.", 429)
    data = json_body()
    if isinstance(data, tuple):
        return data
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    user = User.query.filter_by(email=email, activo=True).first() if email else None
    if not user or len(password) > 100 or not check_password_hash(user.password_hash, password):
        return api_error("Correo o contraseña incorrectos.", 401)
    _entrar(user, "contraseña")
    _avisar_inicio(user, "contraseña", False)
    return jsonify(user=_user(user))


def _entrar(user, metodo):
    iniciar_sesion(user, metodo=metodo, dispositivo=describir_dispositivo(request.headers.get("User-Agent", "")), ip=client_ip())


def _avisar_inicio(user, metodo, nuevo):
    try:
        registrar_inicio(user, request.headers.get("User-Agent", ""), client_ip(), metodo=metodo, nuevo_usuario=nuevo)
    except Exception as e:  # noqa: BLE001 - el aviso nunca impide entrar
        db.session.rollback()
        current_app.logger.warning("No se pudo registrar el dispositivo: %s", e)


# ---------- ¿Olvidaste tu contraseña? ----------
MINUTOS_RESTABLECER = 30


def _firmador():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="restablecer-clave")


def _huella_clave(user):
    # Va dentro del enlace: en cuanto la contraseña cambia, el enlace deja de servir (un solo uso).
    import hashlib
    return hashlib.sha256(f"{user.id}:{user.password_hash}".encode()).hexdigest()[:20]


def token_restablecer(user):
    return _firmador().dumps({"u": user.id, "h": _huella_clave(user)})


def _usuario_de_token(token):
    try:
        datos = _firmador().loads(str(token or ""), max_age=MINUTOS_RESTABLECER * 60)
    except SignatureExpired:
        return None, "El enlace venció. Pide uno nuevo."
    except BadSignature:
        return None, "El enlace no es válido. Pide uno nuevo."
    user = db.session.get(User, int(datos.get("u", 0) or 0))
    if not user or not user.activo or datos.get("h") != _huella_clave(user):
        return None, "Este enlace ya se usó o no es válido. Pide uno nuevo."
    return user, None


def _ocultar(email):
    nombre, _, dominio = email.partition("@")
    return (nombre[:2] + "•" * max(1, len(nombre) - 2)) + "@" + dominio


@bp.post("/api/auth/olvide/")
def olvide_clave():
    data = json_body()
    if isinstance(data, tuple):
        return data
    email = str(data.get("email", "")).strip().lower()[:120]
    if too_many(f"olvide:{client_ip()}", 5, 900) or (email and too_many(f"olvide-mail:{email}", 3, 3600)):
        return api_error("Pediste demasiados enlaces. Espera un rato y revisa tu correo (también la carpeta de spam).", 429)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return api_error("Escribe un correo válido.")
    user = User.query.filter_by(email=email, activo=True).first()
    if user:
        enlace = f"{_config(current_app)['url']}/pages/restablecer.html?t={token_restablecer(user)}"
        try:
            enlace_restablecer(user, enlace, request.headers.get("User-Agent", ""), client_ip(), MINUTOS_RESTABLECER)
        except Exception as e:  # noqa: BLE001
            current_app.logger.warning("No se pudo enviar el enlace de restablecer: %s", e)
    # Misma respuesta exista o no la cuenta: así nadie puede averiguar qué correos están registrados.
    return jsonify(ok=True, mensaje=f"Si {email} tiene una cuenta, te llegará un enlace en unos minutos. Revisa también la carpeta de spam.")


@bp.post("/api/auth/restablecer/validar/")
def validar_restablecer():
    data = json_body()
    if isinstance(data, tuple):
        return data
    user, error = _usuario_de_token(data.get("token"))
    if error:
        return api_error(error, 400)
    return jsonify(ok=True, email=_ocultar(user.email), minutos=MINUTOS_RESTABLECER)


@bp.post("/api/auth/restablecer/")
def restablecer_clave():
    if too_many(f"restablecer:{client_ip()}", 10, 900):
        return api_error("Demasiados intentos. Espera unos minutos.", 429)
    data = json_body()
    if isinstance(data, tuple):
        return data
    user, error = _usuario_de_token(data.get("token"))
    if error:
        return api_error(error, 400)
    nueva = str(data.get("password", ""))
    if not valid_password(nueva):
        return api_error("La nueva contraseña debe tener mínimo 6 caracteres, una mayúscula y un número.")
    user.password_hash = generate_password_hash(nueva)
    db.session.commit()
    cerrar_sesiones(user.id)   # quien tuviera la sesión abierta (por ejemplo, quien te la robó) queda afuera
    try:
        avisar_cambio_clave(user, request.headers.get("User-Agent", ""), client_ip())
        db.session.commit()
    except Exception as e:  # noqa: BLE001
        db.session.rollback()
        current_app.logger.warning("No se pudo avisar el cambio de contraseña: %s", e)
    return jsonify(ok=True, email=user.email)


@bp.post("/api/auth/password/")
@login_required
def cambiar_clave():
    if too_many(f"clave:{current_user.id}", 8, 900):
        return api_error("Demasiados intentos. Espera unos minutos.", 429)
    data = json_body()
    if isinstance(data, tuple):
        return data
    actual, nueva = str(data.get("actual", "")), str(data.get("nueva", ""))
    if len(actual) > 100 or not check_password_hash(current_user.password_hash, actual):
        extra = " Si entras con Google y nunca creaste una contraseña, no necesitas una." if current_user.google_id else ""
        return api_error("La contraseña actual no es correcta." + extra, 400)
    if not valid_password(nueva):
        return api_error("La nueva contraseña debe tener mínimo 6 caracteres, una mayúscula y un número.")
    if check_password_hash(current_user.password_hash, nueva):
        return api_error("La nueva contraseña debe ser distinta de la actual.")
    current_user.password_hash = generate_password_hash(nueva)
    db.session.commit()
    cerradas = 0
    if data.get("cerrar_otras", True) is not False:   # como Google: cambiar la contraseña saca a los otros dispositivos
        cerradas = cerrar_sesiones(current_user.id, excepto=getattr(current_user, "_sesion_id", None))
    try:
        avisar_cambio_clave(current_user, request.headers.get("User-Agent", ""), client_ip())
        db.session.commit()
    except Exception as e:  # noqa: BLE001
        db.session.rollback()
        current_app.logger.warning("No se pudo avisar el cambio de contraseña: %s", e)
    return jsonify(ok=True, sesiones_cerradas=cerradas)


@bp.get("/api/ajustes/correos/")
@login_required
def ver_correos():
    a = ajustes_de(current_user)
    db.session.commit()
    from models import KnownDevice
    dispositivos = KnownDevice.query.filter_by(usuario_id=current_user.id).order_by(KnownDevice.ultimo.desc()).limit(20).all()
    return jsonify(seguridad=a.seguridad, racha=a.racha, novedades=a.novedades,
                   dispositivos=[{"nombre": d.nombre, "ultimo": iso(d.ultimo), "primero": iso(d.primero)} for d in dispositivos])


@bp.post("/api/ajustes/correos/")
@login_required
def guardar_correos():
    data = json_body()
    if isinstance(data, tuple):
        return data
    a = ajustes_de(current_user)
    for clave in ("seguridad", "racha", "novedades"):
        if clave in data:
            if not isinstance(data[clave], bool):
                return api_error("Valor no válido.")
            setattr(a, clave, data[clave])
    db.session.commit()
    return jsonify(seguridad=a.seguridad, racha=a.racha, novedades=a.novedades)


@bp.post("/api/auth/logout/")
def salir():
    """Cerrar sesión en este dispositivo (la sesión queda revocada: la cookie ya no sirve aunque alguien la copie)."""
    sid = getattr(current_user, "_sesion_id", None) if current_user.is_authenticated else None
    if sid:
        from models import UserSession
        fila = db.session.get(UserSession, sid)
        if fila:
            fila.revocada = True
            db.session.commit()
    logout_user()
    return jsonify(ok=True)


@bp.get("/api/sesiones/")
@login_required
def ver_sesiones():
    from models import UserSession
    actual = getattr(current_user, "_sesion_id", None)
    filas = (UserSession.query.filter_by(usuario_id=current_user.id, revocada=False)
             .order_by(UserSession.ultima.desc()).limit(50).all())
    return jsonify(sesiones=[{
        "id": f.id, "dispositivo": f.dispositivo or "Dispositivo", "ip": f.ip, "metodo": f.metodo,
        "creada": iso(f.creada), "ultima": iso(f.ultima), "actual": f.id == actual,
    } for f in filas])


@bp.delete("/api/sesiones/<int:sesion_id>")
@login_required
def cerrar_sesion_dispositivo(sesion_id):
    """Cerrar sesión en ese dispositivo: la próxima petición de ese navegador ya no estará dentro."""
    from models import UserSession
    fila = UserSession.query.filter_by(id=sesion_id, usuario_id=current_user.id).first()
    if fila is None:
        return api_error("Esa sesión no existe.", 404)
    fila.revocada = True
    db.session.commit()
    from servicios.correo import olvidar_dispositivos
    olvidar_dispositivos(current_user.id, sesiones=[fila])   # al volver a entrar ahí, llega el correo de nuevo inicio
    era_esta = fila.id == getattr(current_user, "_sesion_id", None)
    if era_esta:
        logout_user()
    return jsonify(ok=True, era_esta=era_esta)


@bp.post("/api/sesiones/cerrar-todas/")
@login_required
def cerrar_todas():
    """Cerrar sesión en todos los dispositivos (o en todos menos este, con {"excepto_este": true})."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    excepto = getattr(current_user, "_sesion_id", None) if data.get("excepto_este") else None
    from models import UserSession
    from servicios.correo import olvidar_dispositivos
    abiertas = UserSession.query.filter_by(usuario_id=current_user.id, revocada=False).all()
    n = cerrar_sesiones(current_user.id, excepto=excepto)
    # Los dispositivos que se cerraron dejan de ser conocidos (también este, si se cerró): al volver a entrar llega el correo.
    olvidar_dispositivos(current_user.id, sesiones=[x for x in abiertas if x.id != excepto] if excepto else None)
    if not excepto:
        logout_user()
    return jsonify(ok=True, cerradas=n, sigues_dentro=bool(excepto))
