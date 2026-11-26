"""Espacio de archivos personal y estado didáctico de Git.

El proyecto (texto de los archivos, carpetas y Git) se guarda como JSON en disco:
ALMACEN_ARCHIVOS/<usuario>/proyecto.json. La tabla espacios_trabajo solo lleva la fecha de la última escritura.
Así un proyecto grande (hasta 5 millones de caracteres de texto) no choca con max_allowed_packet de MySQL.
Los proyectos guardados antes en las columnas JSON se siguen leyendo y pasan a disco al guardar.
"""
import gzip
import json
import os
import re
import secrets
from pathlib import Path
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from models import User, UserWorkspace, db
from rutas.archivos import limpiar_huerfanas
from utilidades import api_error

bp = Blueprint("trabajo", __name__)

# Igual que en el navegador (fs.js): todo menos  \ / : * ? " < > |, caracteres de control y espacio/punto al final.
_COMPONENTE = re.compile(r'^(?!\s)[^\\/:*?"<>|\x00-\x1f]{1,120}(?<![\s.])$|^\.[^\\/:*?"<>|\x00-\x1f]{1,119}$')
_RAMA = re.compile(r"^[A-Za-z0-9._/-]{1,80}$")
_HASH = re.compile(r"^[a-f0-9]{1,12}$")
_MAX_ARCHIVOS = 5000
_MAX_CARPETAS = 2000
_MARCADOR = re.compile(r"^cc(?:img|bin):v1:[a-f0-9]{64}:")
_MAX_CARACTERES = 5_000_000
_MAX_CUERPO = 64 * 1024 * 1024  # JSON descomprimido


def _texto(archivos):
    """Caracteres de texto editable: los marcadores de archivos guardados en la cuenta no cuentan."""
    return sum(len(t) for t in archivos.values() if isinstance(t, str) and not _MARCADOR.match(t))


def _ruta_valida(path):
    return (
        isinstance(path, str)
        and len(path) <= 400
        and all(
            _COMPONENTE.fullmatch(parte)
            and parte not in {".", ".."}
            and parte.lower() not in {"__proto__", "prototype", "constructor"}
            for parte in path.split("/")
        )
    )


def _validar_proyecto(data):
    files = data.get("files")
    folders = data.get("folders")
    git = data.get("git", {})
    if not isinstance(files, dict) or not isinstance(folders, list) or not isinstance(git, dict):
        return None
    if len(files) > _MAX_ARCHIVOS or len(folders) > _MAX_CARPETAS:
        return None
    if any(not _ruta_valida(path) or not isinstance(text, str) for path, text in files.items()):
        return None
    if any(not _ruta_valida(path) for path in folders) or len(set(folders)) != len(folders):
        return None
    if _texto(files) > _MAX_CARACTERES:
        return None

    file_paths = set(files)
    folder_paths = set(folders)
    for path in file_paths:
        if path in folder_paths or any(
            other.startswith(path + "/") for other in file_paths | folder_paths if other != path
        ):
            return None

    branch = git.get("branch", "main")
    staged = git.get("staged", [])
    tracked = git.get("tracked", [])
    committed = git.get("committed", {})
    commits = git.get("commits", [])
    remote = git.get("remote", "")
    branches = git.get("branches", {})
    repos = git.get("repos", {})
    if (
        not isinstance(repos, dict) or len(repos) > 50
        or any(
            not isinstance(carpeta, str) or not (carpeta == "" or _ruta_valida(carpeta))
            or not isinstance(info, dict)
            or not isinstance(info.get("remote", ""), str) or len(info.get("remote", "")) > 400
            or not isinstance(info.get("respaldo", ""), str) or len(info.get("respaldo", "")) > 200
            or not isinstance(info.get("rama", ""), str) or len(info.get("rama", "")) > 120
            for carpeta, info in repos.items()
        )
    ):
        return None
    if (
        not isinstance(branches, dict) or len(branches) > 50
        or any(
            not isinstance(name, str) or not _RAMA.fullmatch(name)
            or not isinstance(tip, str) or not (tip == "" or _HASH.fullmatch(tip))
            for name, tip in branches.items()
        )
    ):
        return None
    if (
        not isinstance(git.get("initialized", False), bool)
        or not isinstance(branch, str) or not _RAMA.fullmatch(branch)
        or not isinstance(staged, list) or not isinstance(tracked, list)
        or len(staged) > _MAX_ARCHIVOS or len(tracked) > _MAX_ARCHIVOS
        or any(not _ruta_valida(path) for path in staged + tracked)
        or not isinstance(committed, dict)
        or len(committed) > _MAX_ARCHIVOS
        or any(not _ruta_valida(path) or not isinstance(text, str) for path, text in committed.items())
        or _texto(committed) > _MAX_CARACTERES
        or not isinstance(commits, list) or len(commits) > 100
        or any(
            not isinstance(commit, dict)
            or not isinstance(commit.get("hash"), str) or not _HASH.fullmatch(commit["hash"])
            or not isinstance(commit.get("message"), str) or len(commit["message"]) > 200
            or not isinstance(commit.get("date"), str) or len(commit["date"]) > 40
            for commit in commits
        )
        or not isinstance(remote, str) or len(remote) > 250
    ):
        return None
    return {
        "files": files,
        "folders": folders,
        "git": {
            "initialized": git.get("initialized", False),
            "branch": branch,
            "staged": list(dict.fromkeys(staged)),
            "tracked": list(dict.fromkeys(tracked)),
            "committed": committed,
            "commits": [
                {"hash": commit["hash"], "message": commit["message"], "date": commit["date"]}
                for commit in commits
            ],
            "remote": remote,
            "branches": branches,
            "repos": {
                carpeta: {"remote": info.get("remote", ""), "respaldo": info.get("respaldo", ""), "rama": info.get("rama", "")}
                for carpeta, info in repos.items()
            },
        },
    }


def _marca(workspace):
    """Marca de la última escritura (ISO, UTC). El navegador la usa para saber si la cuenta cambió desde su última sincronización."""
    valor = workspace.actualizado_en
    if valor is None:
        return None
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc).isoformat()


def _archivo_proyecto(usuario_id):
    return Path(current_app.config["ALMACEN_ARCHIVOS"]) / str(int(usuario_id)) / "proyecto.json"


def limpiar_almacen_de_id(usuario_id):
    """Cuenta nueva: si en disco quedó una carpeta con este id (de una base de datos anterior), se borra entera.
    Así una persona nueva nunca hereda proyectos, commits ni archivos de otra."""
    carpeta = Path(current_app.config["ALMACEN_ARCHIVOS"]) / str(int(usuario_id))
    if carpeta.exists():
        import shutil
        shutil.rmtree(carpeta, ignore_errors=True)


def dueno_de(usuario):
    """Marca de la cuenta dueña de una carpeta del almacén. Si la base se reinicia y otra persona recibe el mismo id,
    la marca no coincide (otra fecha de registro) y no puede leer lo que quedó en disco de la anterior."""
    creado = usuario.creado_en.replace(tzinfo=None).isoformat(timespec="seconds") if usuario and usuario.creado_en else ""
    return f"{usuario.id}:{creado}"


def leer_proyecto(workspace):
    """El proyecto guardado de una cuenta: desde disco o, si es de antes, desde las columnas de la tabla."""
    if workspace is None:
        return None
    ruta = _archivo_proyecto(workspace.usuario_id)
    if ruta.exists():
        with open(ruta, encoding="utf-8") as f:
            proyecto = json.load(f)
        dueno = proyecto.pop("_dueno", None)
        usuario = db.session.get(User, workspace.usuario_id)
        if dueno is not None and usuario is not None and dueno != dueno_de(usuario):
            return None   # es de otra cuenta que tuvo este id antes: nunca se entrega
        return proyecto
    return {"files": workspace.archivos or {}, "folders": workspace.carpetas or [], "git": workspace.git or {}}


def _escribir_proyecto(usuario_id, proyecto):
    ruta = _archivo_proyecto(usuario_id)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(f".proyecto-{secrets.token_hex(6)}.json")
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(proyecto, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(temporal, ruta)  # atómico: nunca queda un proyecto a medio escribir


def _cuerpo_json():
    """JSON del cuerpo, aceptando que venga comprimido (Content-Encoding: gzip), como lo envía el navegador."""
    crudo = request.get_data(cache=False)
    if request.headers.get("Content-Encoding", "").lower() == "gzip":
        try:
            with gzip.GzipFile(fileobj=__import__("io").BytesIO(crudo)) as g:
                crudo = g.read(_MAX_CUERPO + 1)
        except (OSError, EOFError):
            return api_error("El cuerpo comprimido no es válido.")
    if len(crudo) > _MAX_CUERPO:
        return api_error("El proyecto es demasiado grande.", 413)
    try:
        data = json.loads(crudo.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return api_error("El cuerpo de la solicitud debe ser JSON válido.")
    if not isinstance(data, dict):
        return api_error("El cuerpo de la solicitud debe ser un objeto JSON.")
    return data


@bp.get("/api/trabajo/")
@login_required
def obtener_proyecto():
    workspace = UserWorkspace.query.filter_by(usuario_id=current_user.id).first()
    if workspace is None:
        return jsonify(proyecto=None, actualizado=None)
    return jsonify(proyecto=leer_proyecto(workspace), actualizado=_marca(workspace))


def _revisar_archivos_editor(project):
    """Antivirus también para lo que se crea o escribe DENTRO del editor (no solo para lo que se sube): un archivo con
    nombre peligroso (.exe, .vbs…), la firma de un virus o código malicioso no se guarda en el servidor. Se avisa al
    estudiante (correo) y al administrador (panel) una sola vez por archivo. Lo que se trabaja con el Conector, en el
    equipo de la persona, nunca llega aquí."""
    from datetime import timedelta
    from models import Incidente, utcnow
    from servicios.antivirus import revisar_texto
    from servicios.moderacion import registrar
    bloqueados = []
    for ruta, texto in list(project["files"].items()):
        try:
            h = revisar_texto(ruta, texto)
        except Exception:  # noqa: BLE001 - el antivirus nunca debe impedir guardar el resto
            current_app.logger.exception("No se pudo revisar %s", ruta)
            continue
        if not h:
            continue
        del project["files"][ruta]
        git = project.get("git") or {}
        for k in ("staged", "tracked"):
            if isinstance(git.get(k), list) and ruta in git[k]:
                git[k] = [x for x in git[k] if x != ruta]
        if isinstance(git.get("committed"), dict):
            git["committed"].pop(ruta, None)
        bloqueados.append({"ruta": ruta, "motivo": h["motivo"]})
        ya = Incidente.query.filter(Incidente.usuario_id == current_user.id, Incidente.evidencia == str(h["evidencia"])[:400],
                                    Incidente.creado_en >= utcnow() - timedelta(hours=24)).first()
        if not ya:
            registrar(current_user, "archivo", h["motivo"], evidencia=h["evidencia"], origen="Trabajo (editor)",
                      gravedad=h["gravedad"], explicacion=h["explicacion"])
    return bloqueados


@bp.put("/api/trabajo/")
@login_required
def guardar_proyecto():
    data = _cuerpo_json()
    if isinstance(data, tuple):
        return data
    project = _validar_proyecto(data)
    if project is None:
        return api_error("El proyecto no es válido o supera el límite de almacenamiento.")

    bloqueados = _revisar_archivos_editor(project)
    workspace = UserWorkspace.query.filter_by(usuario_id=current_user.id).first()
    if workspace is None:
        workspace = UserWorkspace(usuario_id=current_user.id)
        db.session.add(workspace)
    _escribir_proyecto(current_user.id, {**project, "_dueno": dueno_de(current_user)})
    workspace.archivos, workspace.carpetas, workspace.git = {}, [], {}  # el contenido vive en disco
    workspace.actualizado_en = datetime.now(timezone.utc)
    limpiar_huerfanas(current_user.id, project["files"], project["git"])
    db.session.commit()
    return jsonify(ok=True, actualizado=_marca(workspace), bloqueados=bloqueados)


# ------------------------------------------------------------------------- cliente HTTP (tipo Postman) ----
@bp.post("/api/trabajo/cliente-http")
@login_required
def cliente_http():
    """Peticiones del cliente HTTP de Trabajo a APIs públicas de internet (ver servicios/proxy_http.py)."""
    import base64
    from servicios.proxy_http import ErrorProxy, pedir
    from utilidades import too_many
    from rutas.trabajored import _activo, _enlace_peligroso
    if not _activo():
        return api_error("Este servidor no permite peticiones a internet desde Trabajo (TRABAJO_RED=0).", 403)
    if too_many(f"http:{current_user.id}", 40, 60):
        return api_error("Muchas peticiones seguidas: espera un minuto.", 429)
    data = request.get_json(silent=True) or {}
    try:
        cuerpo = base64.b64decode(str(data.get("cuerpo_b64") or ""), validate=True) if data.get("cuerpo_b64") else str(data.get("cuerpo") or "").encode()
    except (ValueError, TypeError):
        return api_error("El cuerpo no es válido.")
    cabeceras = [(c[0], c[1]) for c in (data.get("cabeceras") or []) if isinstance(c, (list, tuple)) and len(c) == 2]
    try:
        r = pedir(data.get("metodo"), str(data.get("url") or "").strip(), cabeceras, cuerpo, verificar_tls=data.get("verificar", True) is not False,
                  revisar=_enlace_peligroso)
    except ErrorProxy as e:
        return api_error(str(e), 422)
    return jsonify(status=r["status"], razon=r["razon"], cabeceras=r["cabeceras"], cuerpo_b64=base64.b64encode(r["cuerpo"]).decode(),
                   truncado=r["truncado"], ms=r["ms"], url=r["url"])
