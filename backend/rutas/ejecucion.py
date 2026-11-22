"""Ejecuta el código de la página Aprende (Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin, Ruby)."""
import threading
import time

from flask import Blueprint, current_app, jsonify
from flask_login import current_user, login_required

from utilidades import api_error, json_body

bp = Blueprint("ejecucion", __name__)


ejecuciones = {}                       # usuario_id -> marcas de tiempo de las últimas ejecuciones
cupo = threading.BoundedSemaphore(6)   # máximo 6 programas a la vez (los que van en línea casi no gastan CPU aquí)


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
        archivos = data.get("archivos") if isinstance(data.get("archivos"), list) else None
        return jsonify(ejecutar(str(data.get("lenguaje", "")), data.get("codigo"), data.get("entrada") or "", archivos))
    except ValueError as error:
        return api_error(str(error))
    except Exception:
        current_app.logger.exception("Falló el ejecutor de código.")
        return api_error("No se pudo ejecutar el código.", 500)
    finally:
        cupo.release()


# ----------------------------------------------- Python con pip de verdad en el servidor ----
cupo_pip = threading.BoundedSemaphore(2)


def _datos():
    data = json_body()
    return data


@bp.post("/api/python/pip")
@login_required
def pip_servidor():
    from servicios import python_servidor as ps

    data = _datos()
    if isinstance(data, tuple):
        return data
    if not cupo_pip.acquire(timeout=30):
        return api_error("El servidor está instalando paquetes para otras personas. Inténtalo en un momento.", 503)
    try:
        if data.get("accion") == "desinstalar":
            return jsonify(ps.desinstalar(current_user.id, data.get("paquetes")))
        return jsonify(ps.instalar(current_user.id, data.get("paquetes")))
    except ValueError as error:
        return api_error(str(error))
    except Exception as error:
        current_app.logger.exception("Falló pip en el servidor.")
        return api_error(f"No se pudo instalar en el servidor: {error}", 500)
    finally:
        cupo_pip.release()


@bp.get("/api/python/pip")
@login_required
def pip_lista():
    from servicios import python_servidor as ps
    return jsonify({"paquetes": ps.lista(current_user.id), "activo": ps.activo()})


@bp.post("/api/python/run")
@login_required
def python_servidor():
    from servicios import python_servidor as ps

    data = _datos()
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
        return jsonify(ps.ejecutar(current_user.id, data.get("ruta"), data.get("archivos"),
                                   str(data.get("entrada") or "")[:20_000], data.get("args")))
    except ValueError as error:
        return api_error(str(error))
    except Exception:
        current_app.logger.exception("Falló Python en el servidor.")
        return api_error("No se pudo ejecutar el programa en el servidor.", 500)
    finally:
        cupo.release()


# ------------------------------------------------------------------------ Docker ----
cupo_docker = threading.BoundedSemaphore(3)


@bp.get("/api/docker")
@login_required
def docker_estado():
    from servicios import docker_trabajo as dk
    return jsonify(dk.estado())


@bp.post("/api/docker")
@login_required
def docker_orden():
    from servicios import docker_trabajo as dk

    data = _datos()
    if isinstance(data, tuple):
        return data
    if not cupo_docker.acquire(timeout=30):
        return api_error("Docker está ocupado con otras órdenes. Inténtalo en un momento.", 503)
    try:
        archivos = data.get("archivos") if isinstance(data.get("archivos"), list) else None
        return jsonify(dk.ejecutar(current_user.id, data.get("args"), str(data.get("proyecto") or "proyecto"),
                                   archivos, str(data.get("entrada") or "")[:20_000], str(data.get("cwd") or "")))
    except ValueError as error:
        return api_error(str(error))
    except Exception:
        current_app.logger.exception("Falló docker.")
        return api_error("No se pudo ejecutar la orden de Docker.", 500)
    finally:
        cupo_docker.release()
