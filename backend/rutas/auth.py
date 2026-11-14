"""Cuenta de usuario: ver sesión, registrarse, entrar y salir."""
import re
import secrets

from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.flask_client import OAuth
from flask import Blueprint, current_app, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from models import Profile, User, db
from servicios.perfil import _user, ensure_identity, serialize_user
from utilidades import api_error, client_ip, json_body, too_many, valid_password

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
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"] or url_for(
        "auth.google_callback", _external=True,
    )
    return oauth.google.authorize_redirect(redirect_uri)


@bp.get("/auth/google/callback/")
def google_callback():
    try:
        oauth.google.authorize_access_token()
        identity = oauth.google.userinfo()
    except OAuthError:
        return redirect("/pages/login.html?error=google")

    subject = identity.get("sub") if identity else None
    email = str(identity.get("email", "")).strip().lower() if identity else ""
    if not subject or not email or identity.get("email_verified") is not True:
        return redirect("/pages/login.html?error=google_email")

    user = User.query.filter_by(google_id=subject).first()
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
            profile = Profile(user=user)
            ensure_identity(profile, nombre)
            db.session.add(profile)
        else:
            user.google_id = subject

    if not user.activo:
        return redirect("/pages/login.html?error=google_inactive")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return redirect("/pages/login.html?error=google_conflict")
    login_user(user, remember=True)
    destination = "/pages/inicio.html" if user.profile and user.profile.onboarding_completo else "/pages/onboarding.html"
    return redirect(destination)


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
    profile = Profile(user=user)
    ensure_identity(profile, nombre)
    db.session.add(profile)
    db.session.flush()
    user_data = serialize_user(user, profile)
    db.session.commit()
    login_user(user, remember=True)
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
    login_user(user, remember=True)
    return jsonify(user=_user(user))


@bp.post("/api/auth/logout/")
def salir():
    logout_user()
    return jsonify(ok=True)
