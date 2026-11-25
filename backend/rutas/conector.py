"""Conector de CódigoCamp: la terminal de Trabajo ejecuta comandos de verdad en TU computador o celular.

Cómo funciona (siempre lo decides tú):
  1. En Trabajo eliges «Conectar mi equipo» y aparece un código de 6 caracteres (vale 10 minutos).
  2. En tu equipo abres el Conector (frontend/descargas/codigocamp-conector.py) con ese código, dentro de la carpeta
     que quieres usar. El Conector te pregunta si aceptas antes de conectarse.
  3. Mientras el Conector está abierto, puedes abrir una terminal «Mi equipo» en Trabajo: los comandos corren en esa
     carpeta (python, node, npm, git, flutter, php -S, docker…) y la salida llega en vivo. Ctrl+C detiene el programa.
  4. Cierras el Conector (Ctrl+C en tu equipo) o lo desconectas desde Trabajo, y se acabó: no queda nada abierto.

El equipo solo SALE hacia CódigoCamp (pregunta si hay órdenes), así que no hay que abrir puertos ni configurar el router.
Las órdenes esperan en memoria del servidor (Flask con hilos; con varios procesos usa uno solo para /api/conector/).

  Persona (sesión) .............................................. Equipo (token Bearer, sin cookies)
  POST   /api/conector/codigo           → código para vincular     POST /api/conector/agente/vincular  {codigo,…} → token
  GET    /api/conector/                 → equipos y si están en línea   GET  /api/conector/agente/esperar   → próxima orden
  DELETE /api/conector/<id>             → desconectar y olvidar         POST /api/conector/agente/salida    {orden, texto, fin, codigo}
  POST   /api/conector/<id>/ejecutar    {linea, cwd} → orden
  GET    /api/conector/orden/<oid>?desde=n  → salida (espera hasta 20 s)
  POST   /api/conector/orden/<oid>/entrada {texto} · /detener
  POST   /api/conector/<id>/enviar      {archivos} → escribe archivos del proyecto en la carpeta del equipo
  POST   /api/conector/<id>/traer       → pide la lista de archivos de la carpeta (para importarlos al proyecto)
  POST   /api/conector/<id>/fs          {accion, …} → la carpeta del equipo abierta en Trabajo como proyecto:
         listar · leer · escribir · carpeta · borrar (dentro de la carpeta abierta), explorar · nueva · raiz (elegir otra
         carpeta, nunca del sistema), git (Git real del equipo, sin shell) y antivirus (estado del antivirus del equipo)
                                                                    POST /api/conector/agente/estado  {antivirus, carpeta}
"""
import hashlib
from pathlib import Path
import secrets
import threading
import json
import time
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Conector, db
from utilidades import api_error, json_body, too_many

bp = Blueprint("conector", __name__)

ESPERA_AGENTE = 25      # segundos que el equipo espera una orden antes de volver a preguntar
ESPERA_SALIDA = 20      # segundos que Trabajo espera salida nueva
EN_LINEA = 45           # sin preguntar en este tiempo → el equipo está desconectado
MAX_SALIDA = 2_000_000  # caracteres que se guardan por orden

_lock = threading.Condition()
_codigos = {}           # código → {usuario_id, vence}
_colas = {}             # conector_id → [orden, …] pendientes para el equipo
_ordenes = {}           # orden_id → {conector_id, usuario_id, texto, fin, codigo, creada}
_visto = {}             # conector_id → time.monotonic() de la última pregunta del equipo
_estado = {}            # conector_id → {antivirus: {...}, version, capacidades} que informa el equipo al conectarse
VERSION_CONECTOR = 6    # la del programa frontend/descargas/codigocamp-conector.py (Trabajo avisa si el del equipo es más viejo)
ACCIONES_FS = {"listar", "leer", "leer_parte", "escribir_parte", "leer_varios", "servicios", "escribir", "carpeta", "borrar", "explorar", "nueva", "raiz", "git", "antivirus"}
MAX_ESCRIBIR = 42_000_000   # caracteres base64 por pedido (unos 30 MB); los archivos grandes van por partes de 8 MB


def _huella(token):
    return hashlib.sha256(token.encode()).hexdigest()


def _ahora():
    return datetime.now(timezone.utc)


def _en_linea(cid):
    return time.monotonic() - _visto.get(cid, -1e9) < EN_LINEA


def _limpiar():
    """Quita códigos vencidos y órdenes viejas (se llama con el candado tomado)."""
    t = time.monotonic()
    for c in [c for c, d in _codigos.items() if d["vence"] < t]:
        del _codigos[c]
    for o in [o for o, d in _ordenes.items() if t - d["creada"] > 6 * 3600 or (d.get("entregada") and t - d["entregada"] > 120)]:
        del _ordenes[o]


def _encolar(conector, tipo, **datos):
    oid = secrets.token_urlsafe(12)
    with _lock:
        _limpiar()
        _ordenes[oid] = {"conector_id": conector.id, "usuario_id": conector.usuario_id, "texto": "", "fin": False, "codigo": None,
                         "creada": time.monotonic(), "datos": None, "base": 0, "tipo": tipo}
        _colas.setdefault(conector.id, []).append({"id": oid, "tipo": tipo, **datos})
        _lock.notify_all()
    return oid


def _mio(cid):
    c = db.session.get(Conector, cid)
    return c if c and c.usuario_id == current_user.id else None


def current_app_max_archivo():
    """Tamaño máximo por archivo de la cuenta (MAX_ARCHIVO_MB, 1 GB de fábrica)."""
    from flask import current_app
    return int(current_app.config.get("MAX_ARCHIVO", 1024 ** 3))


def _agente():
    """El equipo se identifica con su token (cabecera Authorization: Bearer …)."""
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if len(token) < 30:
        return None
    return Conector.query.filter_by(token_hash=_huella(token)).first()


# ----------------------------------------------------------------------------------------- la persona ----
@bp.post("/api/conector/codigo")
@login_required
def crear_codigo():
    data = json_body()
    if isinstance(data, tuple):
        return data
    if data.get("acepto") is not True:
        return api_error("Para conectar un equipo acepta primero las condiciones del Conector (sección 7 de los Términos).", 400)
    if too_many(f"conector-codigo:{current_user.id}", 10, 600):
        return api_error("Pediste muchos códigos. Espera unos minutos.", 429)
    alfabeto = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    with _lock:
        _limpiar()
        codigo = "".join(secrets.choice(alfabeto) for _ in range(6))
        _codigos[codigo] = {"usuario_id": current_user.id, "vence": time.monotonic() + 600}
    return jsonify(codigo=codigo, vence_en=600)


@bp.get("/api/conector/")
@login_required
def listar():
    filas = Conector.query.filter_by(usuario_id=current_user.id).order_by(Conector.creado.desc()).all()
    return jsonify(version_actual=VERSION_CONECTOR, archivo=f"codigocamp-conector-v{VERSION_CONECTOR}.py", equipos=[{"id": c.id, "equipo": c.equipo, "sistema": c.sistema, "carpeta": c.carpeta, "en_linea": _en_linea(c.id),
                             "antivirus": _estado.get(c.id, {}).get("antivirus"),
                             "version": _estado.get(c.id, {}).get("version"), "version_actual": VERSION_CONECTOR,
                             "pty": _tiene_pty(c.id),
                             "ultimo": c.ultimo.isoformat() if c.ultimo else None} for c in filas])


@bp.delete("/api/conector/<int:cid>")
@login_required
def desconectar(cid):
    c = _mio(cid)
    if not c:
        return api_error("Ese equipo no existe.", 404)
    with _lock:
        _colas.setdefault(cid, []).append({"id": "fin", "tipo": "desconectar"})
        _lock.notify_all()
    db.session.delete(c)
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/api/conector/<int:cid>/ejecutar")
@login_required
def ejecutar(cid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    c = _mio(cid)
    if not c:
        return api_error("Ese equipo no existe.", 404)
    if not _en_linea(cid):
        return api_error(f"«{c.equipo}» no está conectado. Abre el Conector en ese equipo.", 409)
    linea = str(data.get("linea", ""))[:20000]
    if not linea.strip():
        return api_error("Escribe un comando.")
    if too_many(f"conector-ejecutar:{current_user.id}", 120, 60):
        return api_error("Demasiados comandos seguidos. Espera un momento.", 429)
    # Protección del equipo: comandos destructivos y enlaces peligrosos no se envían (y no se guardan)
    from servicios.comandos_peligrosos import revisar_comando
    from servicios.seguridad_enlaces import enlaces_en, revisar_enlace
    motivo = revisar_comando(linea)
    if motivo:
        return api_error(f"🛡️ CódigoCamp bloqueó este comando porque {motivo}. Esto protege tu equipo y no se puede saltar.", 403)
    for url in enlaces_en(linea)[:10]:
        r = revisar_enlace(url)
        if r["nivel"] == "bloqueado":
            return api_error(f"🛡️ CódigoCamp bloqueó este comando: el enlace {url[:80]} es peligroso ({r['motivo']}).", 403)
    oid = _encolar(c, "comando", linea=linea, cwd=str(data.get("cwd", ""))[:400],
                   columnas=int(data.get("columnas") or 100))
    return jsonify(orden=oid)


@bp.post("/api/conector/<int:cid>/terminal")
@login_required
def abrir_terminal(cid):
    """Terminal REAL del equipo (pseudo-terminal, como la de VS Code): shell interactiva con colores, nano/vim, htop,
    Python interactivo, Tab para completar… Lo que escribes va tal cual al equipo; la salida vuelve por /orden/<id>."""
    data = json_body() if request.data else {}
    if isinstance(data, tuple):
        return data
    c = _mio(cid)
    if not c:
        return api_error("Ese equipo no existe.", 404)
    if not _en_linea(cid):
        return api_error(f"«{c.equipo}» no está conectado. Abre el Conector en ese equipo.", 409)
    if _tiene_pty(cid) is False:
        return jsonify(error=f"El Conector de «{c.equipo}» es una versión anterior y no trae la terminal completa. Descárgalo de nuevo "
                             "(o ciérralo y ábrelo: se ofrece a actualizarse solo).", actualizar=True), 426
    if too_many(f"conector-terminal:{current_user.id}", 30, 60):
        return api_error("Abriste muchas terminales seguidas. Espera un momento.", 429)
    oid = _encolar(c, "pty", cols=max(10, min(500, int(data.get("cols") or 100))), rows=max(3, min(200, int(data.get("rows") or 30))),
                   cwd=str(data.get("cwd", ""))[:400], shell=str(data.get("shell", ""))[:40])
    return jsonify(orden=oid)


@bp.get("/api/conector/orden/<oid>")
@login_required
def ver_orden(oid):
    desde = max(0, int(request.args.get("desde", 0) or 0))   # posición absoluta (en terminales, la salida es un anillo)
    limite = time.monotonic() + ESPERA_SALIDA
    with _lock:
        while True:
            o = _ordenes.get(oid)
            if not o or o["usuario_id"] != current_user.id:
                return api_error("Esa orden ya no existe.", 404)
            if o["base"] + len(o["texto"]) > desde or o["fin"]:
                if o["fin"]:
                    o.setdefault("entregada", time.monotonic())   # los datos (archivos) se liberan de la memoria poco después
                break
            if not _en_linea(o["conector_id"]):
                o["fin"], o["codigo"] = True, 255
                o["texto"] += "\n[El equipo se desconectó: abre el Conector otra vez]\n"
                break
            resto = limite - time.monotonic()
            if resto <= 0:
                break
            _lock.wait(min(resto, 5))
        inicio = max(0, desde - o["base"])
        return jsonify(texto=o["texto"][inicio:], desde=o["base"] + len(o["texto"]), fin=o["fin"], codigo=o["codigo"], datos=o["datos"] if o["fin"] else None,
                       cortado=desde < o["base"])


@bp.post("/api/conector/orden/<oid>/<accion>")
@login_required
def accion_orden(oid, accion):
    if accion not in {"entrada", "detener", "tam"}:
        return api_error("Acción no válida.", 404)
    data = json_body() if request.data else {}
    if isinstance(data, tuple):
        return data
    with _lock:
        o = _ordenes.get(oid)
        if not o or o["usuario_id"] != current_user.id:
            return api_error("Esa orden ya no existe.", 404)
        _encolar_accion(o, accion, {**data, "_oid": oid})
    return jsonify(ok=True)


@bp.post("/api/conector/<int:cid>/enviar")
@login_required
def enviar_archivos(cid):
    """Copia archivos del proyecto de Trabajo a la carpeta del equipo (para ejecutarlos allá)."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    c = _mio(cid)
    if not c or not _en_linea(cid):
        return api_error("El equipo no está conectado.", 409)
    archivos = data.get("archivos") or {}
    if not isinstance(archivos, dict) or len(archivos) > 3000:
        return api_error("Lista de archivos no válida.")
    total = sum(len(str(v)) for v in archivos.values())
    if total > 40_000_000:
        return api_error("El proyecto es demasiado grande para enviarlo de una vez (máximo 40 MB).", 413)
    limpios = {str(k)[:400]: str(v) for k, v in archivos.items() if isinstance(k, str)}
    oid = _encolar(c, "escribir", archivos=limpios, borrar=[str(x)[:400] for x in (data.get("borrar") or [])][:3000])
    return jsonify(orden=oid)


@bp.post("/api/conector/<int:cid>/traer")
@login_required
def traer_archivos(cid):
    c = _mio(cid)
    if not c or not _en_linea(cid):
        return api_error("El equipo no está conectado.", 409)
    return jsonify(orden=_encolar(c, "leer"))


@bp.post("/api/conector/<int:cid>/fs")
@login_required
def sistema_archivos(cid):
    """La carpeta del equipo como proyecto de Trabajo (listar, leer, guardar…) y su Git real."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    c = _mio(cid)
    if not c:
        return api_error("Ese equipo no existe.", 404)
    if not _en_linea(cid):
        return api_error(f"«{c.equipo}» no está conectado. Abre el Conector en ese equipo.", 409)
    accion = str(data.get("accion", ""))
    if accion not in ACCIONES_FS:
        return api_error("Acción no válida.")
    if too_many(f"conector-fs:{current_user.id}", 900, 60):
        return api_error("Demasiadas operaciones seguidas. Espera un momento.", 429)
    datos = {"accion": accion}
    for k in ("ruta", "nombre", "cwd"):
        if k in data:
            datos[k] = str(data[k])[:1000]
    if accion == "leer_varios":
        rutas = data.get("rutas")
        if not isinstance(rutas, list) or len(rutas) > 500:
            return api_error("Lista de archivos no válida.")
        datos["rutas"] = [str(r)[:1000] for r in rutas]
    if accion == "listar":
        datos["ignorar"] = [str(x)[:80] for x in (data.get("ignorar") or [])][:50]
    if accion in {"leer_parte", "escribir_parte"}:
        desde = data.get("desde", 0)
        if not isinstance(desde, int) or desde < 0 or desde > current_app_max_archivo():
            return api_error("Parte no válida.")
        datos["desde"] = desde
        if accion == "escribir_parte":
            datos["fin"] = bool(data.get("fin"))
    if accion in {"escribir", "escribir_parte"}:
        b64 = data.get("b64")
        if not isinstance(b64, str) or len(b64) > MAX_ESCRIBIR:
            return api_error("Archivo no válido o demasiado grande (máximo 30 MB).", 413)
        datos["b64"] = b64
    if accion == "git":
        args = data.get("args")
        if not isinstance(args, list) or not args or len(args) > 60 or not all(isinstance(a, str) and len(a) < 4000 for a in args):
            return api_error("Comando de Git no válido.")
        from servicios.comandos_peligrosos import revisar_comando
        from servicios.seguridad_enlaces import enlaces_en, revisar_enlace
        linea = "git " + " ".join(args)
        motivo = revisar_comando(linea)
        if motivo:
            return api_error(f"🛡️ CódigoCamp bloqueó este comando porque {motivo}.", 403)
        for url in enlaces_en(linea)[:5]:
            if revisar_enlace(url)["nivel"] == "bloqueado":
                return api_error(f"🛡️ CódigoCamp bloqueó este comando: el enlace {url[:80]} es peligroso.", 403)
        datos["args"] = args
    oid = _encolar(c, "fs", **datos)
    # Rápido: casi todas las operaciones de archivos tardan milisegundos en el equipo, así que se espera aquí mismo
    # y se responde en UNA sola petición (antes eran dos: encolar y luego preguntar por el resultado).
    hecho = _esperar_fin(oid, 6 if accion not in {"git", "servicios"} else 12)
    return jsonify(orden=oid, resultado=hecho) if hecho else jsonify(orden=oid)


def _esperar_fin(oid, segundos):
    from flask import current_app
    if current_app.testing:   # en las pruebas el «equipo» responde después, en el mismo hilo
        segundos = min(segundos, 0.05)
    limite = time.monotonic() + segundos
    with _lock:
        while True:
            o = _ordenes.get(oid)
            if not o:
                return None
            if o["fin"]:
                o.setdefault("entregada", time.monotonic())
                return {"texto": o["texto"], "codigo": o["codigo"], "datos": o["datos"]}
            resto = limite - time.monotonic()
            if resto <= 0 or not _en_linea(o["conector_id"]):
                return None
            _lock.wait(min(resto, 2))


# ------------------------------------------------------------------------------------------ el equipo ----
@bp.post("/api/conector/agente/vincular")
def vincular():
    data = json_body()
    if isinstance(data, tuple):
        return data
    if too_many(f"conector-vincular:{request.remote_addr}", 20, 600):
        return api_error("Demasiados intentos. Espera unos minutos.", 429)
    codigo = str(data.get("codigo", "")).strip().upper().replace(" ", "").replace("-", "")
    with _lock:
        _limpiar()
        d = _codigos.pop(codigo, None)
    if not d:
        return api_error("Código no válido o vencido. Pide uno nuevo en Trabajo → Conectar mi equipo.", 403)
    token = secrets.token_urlsafe(40)
    c = Conector(usuario_id=d["usuario_id"], token_hash=_huella(token), equipo=str(data.get("equipo") or "Mi equipo")[:80],
                 sistema=str(data.get("sistema") or "")[:40], carpeta=str(data.get("carpeta") or "")[:400], ultimo=_ahora())
    db.session.add(c)
    db.session.commit()
    with _lock:
        _visto[c.id] = time.monotonic()
        _lock.notify_all()
    return jsonify(token=token, id=c.id)


@bp.get("/api/conector/agente/esperar")
def esperar():
    c = _agente()
    if not c:
        return api_error("Este equipo ya no está vinculado. Vuelve a conectarlo desde Trabajo.", 401)
    carpeta = request.args.get("carpeta")
    if carpeta is not None and carpeta[:400] != c.carpeta:
        c.carpeta = carpeta[:400]
    if not c.ultimo or (_ahora() - (c.ultimo if c.ultimo.tzinfo else c.ultimo.replace(tzinfo=timezone.utc))).total_seconds() > 60:
        c.ultimo = _ahora()
    db.session.commit()
    cid = c.id
    limite = time.monotonic() + ESPERA_AGENTE
    with _lock:
        while True:
            _visto[cid] = time.monotonic()
            cola = _colas.get(cid)
            if cola:
                _colas[cid] = cola[50:]
                return jsonify(ordenes=cola[:50])
            resto = limite - time.monotonic()
            if resto <= 0:
                return jsonify(ordenes=[])
            _lock.wait(min(resto, 10))


def _guardar_estado(c, data):
    """El equipo informa qué antivirus tiene y qué carpeta tiene abierta (el antivirus no se guarda en la base)."""
    av = data.get("antivirus") if isinstance(data.get("antivirus"), dict) else {}
    with _lock:
        _visto[c.id] = time.monotonic()
        caps = data.get("capacidades") if isinstance(data.get("capacidades"), list) else []
        version = data.get("version") if isinstance(data.get("version"), int) else 1
        _estado[c.id] = {"antivirus": {"nombre": str(av.get("nombre") or "")[:200], "activo": av.get("activo") if isinstance(av.get("activo"), bool) else None,
                                       "revisa": bool(av.get("revisa"))},
                         "version": version, "capacidades": [str(x)[:20] for x in caps[:20]]}
    if isinstance(data.get("carpeta"), str) and data["carpeta"][:400] != c.carpeta:
        c.carpeta = data["carpeta"][:400]
        db.session.commit()


class _Eq:
    """Lo único que _guardar_salida necesita del equipo: su id."""
    __slots__ = ("id",)

    def __init__(self, cid):
        self.id = cid


def _guardar_salida(c, data):
    """Texto (y al final, código y datos) que devuelve el equipo para una orden. False si la orden no es suya."""
    with _lock:
        _visto[c.id] = time.monotonic()
        o = _ordenes.get(str(data.get("orden", "")))
        if not o or o["conector_id"] != c.id:
            return False
        texto = str(data.get("texto", ""))
        if o.get("tipo") == "pty":
            # Terminal real: la salida no tiene fin; se guarda como anillo (se descarta lo más viejo)
            o["texto"] += texto
            if len(o["texto"]) > MAX_SALIDA:
                cortar = len(o["texto"]) - MAX_SALIDA // 2
                o["texto"] = o["texto"][cortar:]
                o["base"] += cortar
            o["creada"] = time.monotonic()   # una terminal abierta no caduca mientras se use
        elif len(o["texto"]) < MAX_SALIDA:
            o["texto"] += texto[: MAX_SALIDA - len(o["texto"])]
        if data.get("fin"):
            o["fin"] = True
            o["codigo"] = int(data.get("codigo") or 0)
            if isinstance(data.get("datos"), (dict, list)):
                o["datos"] = data["datos"]
        _lock.notify_all()
    return True


def _tiene_pty(cid):
    """True/False si el equipo ya informó qué sabe hacer; None si todavía no se sabe."""
    e = _estado.get(cid)
    if not e:
        return None
    return "pty" in (e.get("capacidades") or [])


@bp.get("/api/conector/agente/version")
def version_agente():
    if not _agente():
        return api_error("Este equipo ya no está vinculado.", 401)
    return jsonify(version=VERSION_CONECTOR)


@bp.get("/api/conector/agente/programa")
def programa_agente():
    """El Conector nuevo para que el equipo se actualice (pide su token: solo un equipo vinculado lo descarga así)."""
    if not _agente():
        return api_error("Este equipo ya no está vinculado.", 401)
    return _texto_programa()


@bp.post("/api/conector/agente/estado")
def estado_agente():
    c = _agente()
    if not c:
        return api_error("Este equipo ya no está vinculado.", 401)
    data = json_body()
    if isinstance(data, tuple):
        return data
    _guardar_estado(c, data)
    return jsonify(ok=True)


@bp.post("/api/conector/agente/salida")
def salida():
    c = _agente()
    if not c:
        return api_error("Este equipo ya no está vinculado.", 401)
    data = json_body()
    if isinstance(data, tuple):
        return data
    return jsonify(ok=_guardar_salida(c, data))


# ------------------------------------------------------------------ canal WebSocket (más rápido) ----
# El Conector abre un WebSocket autenticado con su token (Authorization: Bearer …): el servidor le empuja las órdenes al
# instante y el equipo devuelve la salida por el mismo canal. Si el WebSocket no se puede abrir (proxy, versión vieja
# del servidor), el Conector sigue funcionando con las peticiones de siempre (/agente/esperar y /agente/salida).
try:
    from flask_sock import Sock as _Sock
except ImportError:   # pragma: no cover - flask-sock es opcional
    _Sock = None
sock = _Sock() if _Sock else None
WS_PING = 20   # segundos sin órdenes → ping (mantiene vivos los proxies y marca el equipo como conectado)

def _encolar_accion(o, accion, data):
    """Lo que la terminal del navegador manda a una orden (teclas, tamaño, detener). Con el candado tomado."""
    extra = {"texto": str(data.get("texto", ""))[:20000]} if accion == "entrada" else {}
    if accion == "tam":
        extra = {"cols": max(10, min(500, int(data.get("cols") or 80))), "rows": max(3, min(200, int(data.get("rows") or 24)))}
    _colas.setdefault(o["conector_id"], []).append({"id": data["_oid"], "tipo": accion, **extra})
    _lock.notify_all()


if sock:
    @sock.route("/api/conector/orden/<oid>/ws", bp=bp)
    def ws_terminal(ws, oid):
        """Terminal del navegador por WebSocket: las teclas van y la salida vuelve al instante, sin una petición por tecla
        (como la terminal de VS Code). Usa la sesión de la página; solo desde este mismo sitio (no desde otras webs)."""
        from urllib.parse import urlparse
        origen = request.headers.get("Origin", "")
        if not current_user.is_authenticated or (origen and urlparse(origen).netloc != request.host):
            ws.send(json.dumps({"error": "Sesión no válida.", "fin": True}))
            return
        uid = current_user.id
        with _lock:
            o = _ordenes.get(oid)
            if not o or o["usuario_id"] != uid:
                ws.send(json.dumps({"error": "Esa terminal ya no existe.", "fin": True}))
                return
        vivo = threading.Event()
        vivo.set()

        def leer():   # teclas, tamaño y cerrar
            try:
                while vivo.is_set():
                    m = ws.receive()
                    if m is None:
                        continue
                    try:
                        data = json.loads(m)
                    except (TypeError, ValueError):
                        continue
                    accion = data.get("a") if isinstance(data, dict) else None
                    if accion not in {"entrada", "tam", "detener"}:
                        continue
                    with _lock:
                        o = _ordenes.get(oid)
                        if not o or o["usuario_id"] != uid:
                            break
                        _encolar_accion(o, accion, {**data, "_oid": oid})
            except Exception:
                pass
            finally:
                vivo.clear()
                with _lock:
                    _lock.notify_all()

        threading.Thread(target=leer, daemon=True).start()
        pos = max(0, int(request.args.get("desde", 0) or 0))
        try:
            while vivo.is_set() and ws.connected:
                with _lock:
                    o = _ordenes.get(oid)
                    if not o:
                        break
                    if o["base"] + len(o["texto"]) <= pos and not o["fin"]:
                        if not _en_linea(o["conector_id"]):
                            o["fin"], o["codigo"] = True, 255
                            o["texto"] += "\n[El equipo se desconectó: abre el Conector otra vez]\n"
                        else:
                            _lock.wait(5)
                            continue
                    inicio = max(0, pos - o["base"])
                    paquete = {"texto": o["texto"][inicio:], "desde": o["base"] + len(o["texto"]), "fin": o["fin"], "codigo": o["codigo"],
                               "datos": o["datos"] if o["fin"] else None, "cortado": pos < o["base"]}
                    if o["fin"]:
                        o.setdefault("entregada", time.monotonic())
                pos = paquete["desde"]
                ws.send(json.dumps(paquete))
                if paquete["fin"]:
                    break
        finally:
            vivo.clear()

    @sock.route("/api/conector/agente/ws", bp=bp)
    def ws_agente(ws):
        from flask import current_app
        c = _agente()
        if not c:
            ws.send(json.dumps({"tipo": "error", "error": "Este equipo ya no está vinculado. Vuelve a conectarlo desde Trabajo.", "codigo": 401}))
            return
        cid, app = c.id, current_app._get_current_object()
        c.ultimo = _ahora()
        db.session.commit()
        vivo = threading.Event()
        vivo.set()

        def leer():   # lo que manda el equipo: salida de órdenes y su estado
            try:
                while vivo.is_set():
                    m = ws.receive()
                    if m is None:
                        continue
                    try:
                        data = json.loads(m)
                    except (TypeError, ValueError):
                        continue
                    if not isinstance(data, dict):
                        continue
                    if data.get("tipo") == "salida":
                        # Rápido: la salida de la terminal no toca la base de datos (solo memoria)
                        _guardar_salida(_Eq(cid), data)
                    elif data.get("tipo") == "estado":
                        with app.app_context():
                            eq = db.session.get(Conector, cid)
                            if not eq:
                                break
                            _guardar_estado(eq, data)
                        with _lock:
                            _visto[cid] = time.monotonic()
            except Exception:   # se cerró la conexión
                pass
            finally:
                vivo.clear()
                with _lock:
                    _lock.notify_all()

        lector = threading.Thread(target=leer, daemon=True)
        lector.start()
        ultimo_envio = time.monotonic()
        try:
            while vivo.is_set() and ws.connected:
                with _lock:
                    _visto[cid] = time.monotonic()
                    cola = _colas.get(cid)
                    if not cola:
                        _lock.wait(5)
                        cola = _colas.get(cid)
                    if cola:
                        _colas[cid] = cola[50:]
                        enviar = cola[:50]
                    else:
                        enviar = None
                if enviar:
                    ws.send(json.dumps({"tipo": "ordenes", "ordenes": enviar}))
                    ultimo_envio = time.monotonic()
                elif time.monotonic() - ultimo_envio > WS_PING:
                    ws.send(json.dumps({"tipo": "ping"}))
                    ultimo_envio = time.monotonic()
        finally:
            vivo.clear()


@bp.get("/api/conector/programa")
@login_required
def programa():
    """El Conector listo para descargar, ya con la dirección de este CódigoCamp."""
    return _texto_programa()


def _texto_programa():
    from flask import Response
    from constantes import FRONTEND
    texto = (FRONTEND / "descargas" / "codigocamp-conector.py").read_text(encoding="utf-8")
    texto = texto.replace('SERVIDOR = "%SERVIDOR%"', f'SERVIDOR = {request.host_url.rstrip("/")!r}', 1)
    # El filtro de comandos peligrosos viaja DENTRO del programa: el equipo los bloquea aunque el servidor fallara
    filtro = (Path(__file__).resolve().parent.parent / "servicios" / "comandos_peligrosos.py").read_text(encoding="utf-8")
    texto = texto.replace("REVISAR_COMANDO = None  # %FILTRO%", f"{filtro}\nREVISAR_COMANDO = revisar_comando", 1)
    return Response(texto, mimetype="text/x-python", headers={"Content-Disposition": f'attachment; filename="codigocamp-conector-v{VERSION_CONECTOR}.py"', "Cache-Control": "no-store"})
