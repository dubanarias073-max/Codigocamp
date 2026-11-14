"""Seguridad de la app: inicio de sesión (Flask-Login), protección CSRF, cabeceras y errores en JSON."""
import secrets

from flask import request, session
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException

from models import User, db
from utilidades import api_error


def configurar_seguridad(app):
    """Conecta el login, la protección CSRF, las cabeceras seguras y el manejo de errores a la app."""
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

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
