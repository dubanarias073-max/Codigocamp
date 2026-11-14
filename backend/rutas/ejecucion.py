"""Ejecuta el código de la página Aprende (Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin, Ruby)."""
import threading
import time

from flask import Blueprint, current_app, jsonify
from flask_login import current_user, login_required

from utilidades import api_error, json_body

bp = Blueprint("ejecucion", __name__)


ejecuciones = {}                       # usuario_id -> marcas de tiempo de las últimas ejecuciones
cupo = threading.BoundedSemaphore(3)   # máximo 3 programas a la vez en el servidor


@bp.post("/api/run")
@login_required
def ejecutar_codigo():
    from servicios.ejecutor import ejecutar

    data = json_body()
    if isinstance(data, tuple):
        return data
    ahora = time.monotonic()
    marcas = [t for t in ejecuciones.get(current_user.id, []) if ahora - t < 60]
    if len(marcas) >= 15:
        return api_error("Estás ejecutando muy seguido. Espera un momento.", 429)
    ejecuciones[current_user.id] = marcas + [ahora]
    if not cupo.acquire(timeout=15):
        return api_error("El servidor está ocupado ejecutando otros programas. Inténtalo de nuevo.", 503)
    try:
        return jsonify(ejecutar(str(data.get("lenguaje", "")), data.get("codigo")))
    except ValueError as error:
        return api_error(str(error))
    except Exception:
        current_app.logger.exception("Falló el ejecutor de código.")
        return api_error("No se pudo ejecutar el código.", 500)
    finally:
        cupo.release()
