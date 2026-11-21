"""Seguridad de la app: inicio de sesión (Flask-Login), protección CSRF, cabeceras y errores en JSON."""
import secrets

from flask import request, session
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException

import hashlib
from datetime import timezone

from flask_login import login_user

from models import User, db, utcnow
from utilidades import api_error


def configurar_seguridad(app):
    """Conecta el login, la protección CSRF, las cabeceras seguras y el manejo de errores a la app."""
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Solo valen las sesiones registradas y no cerradas (cerrar en un dispositivo o en todos es real).
        try:
            uid, sid = str(user_id).split(":", 1)
            uid = int(uid)
        except (TypeError, ValueError):
            return None
        from models import UserSession
        fila = UserSession.query.filter_by(token_hash=_hash(sid), usuario_id=uid, revocada=False).first()
        if fila is None:
            return None
        user = db.session.get(User, uid)
        if user is None or not user.activo:
            return None
        user._sid = sid
        user._sesion_id = fila.id
        ahora = utcnow()
        ultima = fila.ultima if fila.ultima.tzinfo else fila.ultima.replace(tzinfo=timezone.utc)
        if (ahora - ultima).total_seconds() > 300:
            fila.ultima = ahora
            db.session.commit()
        return user

    @login_manager.unauthorized_handler
    def unauthorized():
        return api_error("Inicia sesión para continuar.", 401)

    @app.before_request
    def csrf_protection():
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            session.setdefault("_csrf_token", secrets.token_urlsafe(32))
            return None
        if request.path.startswith("/api/"):
            cookie_token = request.cookies.get("csrftoken", "")
            session_token = session.get("_csrf_token", "")
            header_token = request.headers.get("X-CSRFToken", "")
            if not cookie_token or not session_token or not secrets.compare_digest(cookie_token, session_token) or not secrets.compare_digest(header_token, session_token):
                return api_error("La sesión de seguridad venció. Recarga la página e inténtalo otra vez.", 403)
        return None

    @app.before_request
    def guardar_zona_horaria():
        """La zona horaria la detecta el dispositivo (cabecera X-Zona-Horaria): se guarda en el perfil si cambió
        (la usan los correos de racha y los widgets, que no pasan por el navegador)."""
        if not request.path.startswith("/api/") or not request.headers.get("X-Zona-Horaria"):
            return None
        from flask_login import current_user
        if not current_user.is_authenticated:
            return None
        from models import Profile
        from servicios.zona import guardar_de_peticion
        perfil = Profile.query.filter_by(usuario_id=current_user.id).first()
        if guardar_de_peticion(perfil):
            db.session.commit()
        return None

    @app.after_request
    def set_csrf_cookie(response):
        token = session.get("_csrf_token")
        if token:
            response.set_cookie("csrftoken", token, httponly=False, samesite="Lax", secure=app.config["SESSION_COOKIE_SECURE"])
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        if request.path.startswith("/api/"):
            return api_error(error.description, error.code or 400)
        return error


def _hash(sid):
    return hashlib.sha256(str(sid).encode()).hexdigest()


def iniciar_sesion(user, *, metodo="contraseña", dispositivo="", ip=""):
    """Crea la sesión de este dispositivo y deja a la persona dentro (cookie de sesión + «recordarme»)."""
    from models import UserSession
    sid = secrets.token_urlsafe(32)
    fila = UserSession(usuario_id=user.id, token_hash=_hash(sid), dispositivo=(dispositivo or "")[:120], ip=(ip or "")[:45], metodo=metodo[:20])
    db.session.add(fila)
    db.session.commit()
    user._sid = sid
    user._sesion_id = fila.id
    login_user(user, remember=True)
    return fila


def cerrar_sesiones(usuario_id, *, excepto=None):
    """Revoca las sesiones de la persona (todas, o todas menos `excepto`). Devuelve cuántas cerró."""
    from models import UserSession
    q = UserSession.query.filter_by(usuario_id=usuario_id, revocada=False)
    if excepto:
        q = q.filter(UserSession.id != excepto)
    n = q.update({UserSession.revocada: True}, synchronize_session=False)
    db.session.commit()
    return n
