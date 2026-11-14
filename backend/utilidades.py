"""Funciones pequeñas que usan todas las rutas: errores JSON, lectura del cuerpo, límites de peticiones, fechas."""
import threading
import time
from datetime import timezone

from flask import jsonify, request
from werkzeug.exceptions import HTTPException


_RATE_LIMITS = {}
_RATE_LOCK = threading.Lock()


def api_error(message, status=400):
    return jsonify(error=message), status


def json_body():
    try:
        data = request.get_json(silent=False)
    except HTTPException:
        return api_error("El cuerpo de la solicitud debe ser JSON válido.")
    if not isinstance(data, dict):
        return api_error("El cuerpo de la solicitud debe ser un objeto JSON.")
    return data


def parse_integer(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def valid_password(password):
    return 6 <= len(password) <= 100 and any(char.isupper() for char in password) and any(char.isdigit() for char in password)


def client_ip():
    return request.remote_addr or "0.0.0.0"


def too_many(key, maximum, seconds):
    now = time.monotonic()
    with _RATE_LOCK:
        recent = [item for item in _RATE_LIMITS.get(key, []) if now - item < seconds]
        _RATE_LIMITS[key] = recent
        if len(recent) >= maximum:
            return True
        recent.append(now)
        return False


def normalize(value):
    return "".join(str(value).lower().split())


def local_time(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone().strftime("%H:%M")
