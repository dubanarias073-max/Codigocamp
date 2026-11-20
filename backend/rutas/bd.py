"""Bases de datos del usuario (MySQL/MariaDB de XAMPP, PostgreSQL, MongoDB, Redis) desde la terminal y Python de Trabajo.

Sirve cuando CódigoCamp corre en el mismo PC que la base (el caso normal con XAMPP). Si CódigoCamp está en
internet, el usuario abre en su PC el puente (herramientas/puente_bd.py), que expone esta misma API.

backend/.env:
  BD_EXTERNAS=1               activa estas rutas (por defecto: activas solo con DEBUG=1)
  BD_HOSTS=localhost,127.0.0.1,::1    a qué servidores se puede conectar (acepta redes: 192.168.1.0/24, o *)
  BD_PERMITIR_PROPIA=0        1 = permitir abrir la base de CódigoCamp (DB_NAME); por defecto no, para no romperla sin querer
"""
import os
import re

import ipaddress

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from servicios.bd_externa import HOSTS_LOCALES, Sesiones, host_de_uri, host_permitido, peticion
from utilidades import api_error, json_body, too_many

bp = Blueprint("bd", __name__)
SESIONES = Sesiones()


def _activo():
    valor = current_app.config.get("BD_EXTERNAS")
    if valor is None:
        valor = os.getenv("BD_EXTERNAS", os.getenv("DEBUG", "1"))
    return str(valor) == "1"


def _hosts():
    valor = current_app.config.get("BD_HOSTS") or os.getenv("BD_HOSTS", "")
    return [h for h in valor.split(",") if h.strip()] or list(HOSTS_LOCALES)


def _base_propia(nombre):
    if (current_app.config.get("BD_PERMITIR_PROPIA") or os.getenv("BD_PERMITIR_PROPIA", "0")) in ("1", 1, True):
        return False
    propia = os.getenv("DB_NAME", "codigocamp")
    return bool(nombre) and nombre.strip().strip("`").lower() == propia.lower()


# Órdenes que nunca se permiten por el servidor: leen o escriben archivos del servidor, cambian usuarios/permisos
# de MySQL, apagan el servidor o arman SQL dinámico (con el que se podría saltar cualquier revisión).
_PELIGROSO = re.compile(
    r"\bINTO\s+(?:OUT|DUMP)FILE\b|\bLOAD_FILE\s*\(|\bLOAD\s+DATA\b|\bLOAD\s+XML\b|\b(?:PREPARE|EXECUTE|DEALLOCATE)\b"
    r"|\bGRANT\b|\bREVOKE\b|\b(?:CREATE|ALTER|DROP|RENAME)\s+USER\b|\bSET\s+PASSWORD\b|\bSET\s+(?:GLOBAL|PERSIST)\b|\bSHUTDOWN\b"
    r"|\bINSTALL\s+(?:PLUGIN|SONAME|COMPONENT)\b|\bUNINSTALL\b|\bmysql\s*`?\s*\.\s*`?\s*(?:user|db|global_priv)\b|\bsys_exec\b|\bCOPY\b[\s\S]*\b(?:PROGRAM|FROM|TO)\b\s*'",
    re.I,
)


def _sin_comentarios(sql):
    return re.sub(r"/\*.*?\*/|--[^\n]*|#[^\n]*", " ", sql, flags=re.S)


def problema_sql(sql, motor="mysql"):
    """Por qué no se puede ejecutar esta consulta por el servidor (o None si se puede)."""
    if not isinstance(sql, str):
        return None
    limpio = _sin_comentarios(sql)
    if _PELIGROSO.search(limpio):
        return "Por seguridad, esa orden no se permite desde CódigoCamp (archivos del servidor, usuarios y permisos, o SQL dinámico). Ejecútala en tu PC (XAMPP / Workbench)."
    if str(motor or "mysql").lower() in ("mysql", "mariadb") and not _permitir_propia():
        propia = re.escape(os.getenv("DB_NAME", "codigocamp"))
        if re.search(rf"[`\"]?\b{propia}\b[`\"]?\s*\.|\bUSE\s+[`\"]?{propia}\b|\b(?:DATABASE|SCHEMA)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?[`\"]?{propia}\b", limpio, re.I):
            return "Esa es la base de datos de CódigoCamp (cuentas y contraseñas de todos); no se puede leer ni cambiar desde aquí."
    return None


def _permitir_propia():
    return (current_app.config.get("BD_PERMITIR_PROPIA") or os.getenv("BD_PERMITIR_PROPIA", "0")) in ("1", 1, True)


def _config(nombre, defecto=""):
    valor = current_app.config.get(nombre)
    return str(valor if valor is not None else os.getenv(nombre, defecto))


def _desde_este_pc():
    """La petición viene del mismo computador donde corre CódigoCamp (y su MySQL)."""
    try:
        return ipaddress.ip_address(request.remote_addr or "").is_loopback
    except ValueError:
        return False


def _autorizado():
    """Quién puede usar las bases de datos del servidor desde Trabajo.
    Con estas rutas se puede borrar cualquier base (DROP DATABASE) si la clave de MySQL lo permite (root sin clave en XAMPP),
    así que por defecto solo la persona sentada en ese PC. BD_USUARIOS=correo1,correo2 autoriza cuentas concretas desde
    cualquier lugar. Los demás usan su propia base (SQLite en su proyecto) o el puente en su propio PC."""
    lista = {e.strip().lower() for e in _config("BD_USUARIOS").split(",") if e.strip()}
    if lista:
        return (current_user.email or "").lower() in lista
    return _desde_este_pc() or _config("BD_EXTERNAS_REMOTO", "0") == "1"


_NO_AUTORIZADO = ("Este servidor no permite conectar a bases de datos desde tu cuenta: solo desde el computador donde está "
                  "instalado CódigoCamp (o las cuentas en BD_USUARIOS). Tu app usará una base SQLite propia en el proyecto, "
                  "o abre el puente en tu PC (bd-puente).")


@bp.get("/api/bd/estado")
@login_required
def estado():
    activo = _activo() and _autorizado()
    return jsonify(activo=activo, hosts=_hosts() if activo else [], motivo=None if activo or not _activo() else _NO_AUTORIZADO)


@bp.post("/api/bd/<accion>")
@login_required
def accion(accion):
    if not _activo():
        return api_error("Este servidor no permite conectar a bases de datos externas. Usa el puente (bd-puente) o activa BD_EXTERNAS=1.", 403)
    if not _autorizado():
        return api_error(_NO_AUTORIZADO, 403)
    if too_many(f"bd:{current_user.id}", 600, 60):
        return api_error("Demasiadas consultas seguidas. Espera un momento.", 429)
    datos = json_body()
    if not isinstance(datos, dict):
        return datos
    if accion == "conectar":
        uri = datos.get("uri") or ""
        hosts = host_de_uri(uri) if uri else [(datos.get("host") or "127.0.0.1").strip()]
        if not hosts:
            return api_error("La dirección de MongoDB no es válida.", 400)
        malo = next((h for h in hosts if not host_permitido(h, _hosts())), None)
        if malo:
            return api_error(f"No se permite conectar a «{malo}» desde este servidor (BD_HOSTS).", 403)
        if str(datos.get("motor") or "mysql").lower() in ("mysql", "mariadb") and _base_propia(datos.get("base")):
            return api_error("Esa es la base de datos de CódigoCamp; no se abre desde aquí para no romperla (BD_PERMITIR_PROPIA=1 lo permite).", 403)
    elif accion == "consulta":
        sql = datos.get("sql") or ""
        motivo = problema_sql(sql)
        if motivo:
            return api_error(motivo, 403)
    respuesta, codigo = peticion(SESIONES, current_user.id, accion, datos)
    return jsonify(respuesta), codigo
