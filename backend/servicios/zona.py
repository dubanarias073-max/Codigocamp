"""Zona horaria de cada persona: la detecta su propio dispositivo (Intl.DateTimeFormat en el navegador o la app).

· Cada petición de la página manda la cabecera X-Zona-Horaria (p. ej. «America/Bogota»).
· Se guarda en el perfil (perfiles.zona_horaria) para lo que corre sin navegador: los correos de racha y los widgets.
· «Hoy» (racha, metas, desafíos, calendario) es el día del lugar donde está la persona, no el del servidor.
"""
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import has_request_context, request

DEFECTO = "America/Bogota"


def valida(nombre):
    """Devuelve el nombre si es una zona IANA válida («America/Bogota»), o None."""
    nombre = str(nombre or "").strip()
    if not nombre or len(nombre) > 64 or nombre.startswith(("/", ".")) or ".." in nombre:
        return None
    try:
        ZoneInfo(nombre)
        return nombre
    except (ZoneInfoNotFoundError, ValueError, OSError):
        return None


def defecto():
    return valida(os.getenv("ZONA_HORARIA")) or DEFECTO


def nombre_zona(perfil=None):
    """Zona de la persona: la que manda su dispositivo en esta petición, si no la guardada, si no la por defecto."""
    if has_request_context():
        z = valida(request.headers.get("X-Zona-Horaria"))
        if z:
            return z
    return valida(getattr(perfil, "zona_horaria", None)) or defecto()


def zona(perfil=None):
    return ZoneInfo(nombre_zona(perfil))


def ahora_de(perfil=None):
    return datetime.now(zona(perfil))


def hoy_de(perfil=None):
    return ahora_de(perfil).date()


def a_utc(valor):
    """Las fechas de MySQL llegan sin zona (se guardan en UTC): se marcan como UTC."""
    if valor is None:
        return None
    return valor.replace(tzinfo=timezone.utc) if valor.tzinfo is None else valor.astimezone(timezone.utc)


def iso(valor):
    """ISO 8601 con zona («…+00:00»): el navegador la convierte bien a la hora local de cada persona."""
    v = a_utc(valor)
    return v.isoformat() if v else None


def hora_local(valor, perfil=None, formato="%H:%M"):
    v = a_utc(valor)
    return v.astimezone(zona(perfil)).strftime(formato) if v else ""


def guardar_de_peticion(perfil):
    """Si el dispositivo mandó una zona distinta de la guardada, la guarda. Devuelve True si cambió."""
    if not has_request_context() or perfil is None:
        return False
    z = valida(request.headers.get("X-Zona-Horaria"))
    if z and z != perfil.zona_horaria:
        perfil.zona_horaria = z
        return True
    return False
