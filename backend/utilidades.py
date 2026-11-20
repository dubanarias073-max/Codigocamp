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


def direcciones(texto, quitar_barra=True):
    """«http://localhost:5000, https://codigocamp.tail.ts.net» -> lista. Para APP_URL se quita la barra final;
    para GOOGLE_REDIRECT_URI NO (quitar_barra=False): Google exige la dirección idéntica a la registrada, con su «/»."""
    return [(u.strip().rstrip("/") if quitar_barra else u.strip()) for u in str(texto or "").split(",") if u.strip()]


def direccion_actual(lista):
    """De varias direcciones del proyecto (localhost, el túnel…), la que coincide con cómo entró esta persona.
    Fuera de una petición (avisos automáticos) o si ninguna coincide, la primera."""
    from urllib.parse import urlsplit
    from flask import has_request_context
    if not lista:
        return None
    if has_request_context():
        host = (request.host or "").lower()
        exacta = f"{request.scheme}://{host}"
        for u in lista:
            p = urlsplit(u)
            if f"{p.scheme}://{p.netloc}".lower() == exacta:
                return u
        for u in lista:   # detrás de un túnel sin PROXY_CONFIABLE el esquema llega como http: basta el host
            if urlsplit(u).netloc.lower() == host:
                return u
    return lista[0]
