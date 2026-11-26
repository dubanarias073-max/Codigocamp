"""Quién es el administrador de CódigoCamp y cuándo su sesión tiene el modo administrador encendido.

El administrador NO es una fila de la base de datos: es el correo ADMIN_EMAIL (backend/.env). Así, aunque se borre la
base, basta con volver a registrarse (con Google o con correo y contraseña) para recuperar el panel.

Para entrar al panel hacen falta DOS cosas:
  1. Haber iniciado sesión con la cuenta de ese correo.
  2. Escribir la clave de administrador ADMIN_CLAVE (backend/.env). Sin ella nadie entra, ni siquiera tú: así, si
     alguien roba tu contraseña, o se registra con tu correo antes que tú tras borrar la base, igual queda fuera.
El modo administrador vale solo en ESE dispositivo/sesión y se apaga solo a las 12 horas.
"""
import os
import secrets
import time
from functools import wraps

from flask import abort, session
from flask_login import current_user

ADMIN_EMAIL_DEFECTO = "dubanarias073@gmail.com"
HORAS_MODO_ADMIN = 12


def correo_admin():
    return (os.getenv("ADMIN_EMAIL") or ADMIN_EMAIL_DEFECTO).strip().strip('"').lower()


def clave_admin():
    return (os.getenv("ADMIN_CLAVE") or "").strip().strip('"')


def es_admin(user):
    """¿Esta cuenta es la del administrador? (solo por el correo)."""
    return bool(user and getattr(user, "email", None) and user.email.strip().lower() == correo_admin())


def clave_correcta(clave):
    real = clave_admin()
    return bool(real) and secrets.compare_digest(str(clave or "").encode(), real.encode())


def encender():
    session["admin_sid"] = getattr(current_user, "_sid", None)
    session["admin_desde"] = int(time.time())


def apagar():
    session.pop("admin_sid", None)
    session.pop("admin_desde", None)


def modo_activo():
    if not current_user.is_authenticated or not es_admin(current_user) or not clave_admin():
        return False
    sid = getattr(current_user, "_sid", None)
    desde = session.get("admin_desde") or 0
    if not sid or session.get("admin_sid") != sid or time.time() - desde > HORAS_MODO_ADMIN * 3600:
        apagar()
        return False
    return True


def requiere_admin(f):
    """Las rutas del panel responden 404 a cualquier otra persona: ni siquiera se sabe que existen."""
    @wraps(f)
    def envuelta(*a, **k):
        if not modo_activo():
            abort(404)
        return f(*a, **k)
    return envuelta
