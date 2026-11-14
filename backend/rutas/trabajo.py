"""Espacio de archivos personal y estado didáctico de Git."""
import re
from datetime import datetime, timezone

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from models import UserWorkspace, db
from utilidades import api_error, json_body

bp = Blueprint("trabajo", __name__)

_COMPONENTE = re.compile(r"^[A-Za-z0-9_.-]{1,60}$")
_RAMA = re.compile(r"^[A-Za-z0-9._/-]{1,80}$")
_HASH = re.compile(r"^[a-f0-9]{1,12}$")
_MAX_ARCHIVOS = 250
_MAX_CARACTERES = 500_000


def _ruta_valida(path):
    return (
        isinstance(path, str)
        and len(path) <= 180
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
    if len(files) > _MAX_ARCHIVOS or len(folders) > _MAX_ARCHIVOS:
        return None
    if any(not _ruta_valida(path) or not isinstance(text, str) for path, text in files.items()):
        return None
    if any(not _ruta_valida(path) for path in folders) or len(set(folders)) != len(folders):
        return None
    if sum(len(text) for text in files.values()) > _MAX_CARACTERES:
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
        or sum(len(text) for text in committed.values()) > _MAX_CARACTERES
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


@bp.get("/api/trabajo/")
@login_required
def obtener_proyecto():
    workspace = UserWorkspace.query.filter_by(usuario_id=current_user.id).first()
    if workspace is None:
        return jsonify(proyecto=None, actualizado=None)
    return jsonify(proyecto={
        "files": workspace.archivos,
        "folders": workspace.carpetas,
        "git": workspace.git,
    }, actualizado=_marca(workspace))


@bp.put("/api/trabajo/")
@login_required
def guardar_proyecto():
    data = json_body()
    if isinstance(data, tuple):
        return data
    project = _validar_proyecto(data)
    if project is None:
        return api_error("El proyecto no es válido o supera el límite de almacenamiento.")

    workspace = UserWorkspace.query.filter_by(usuario_id=current_user.id).first()
    if workspace is None:
        workspace = UserWorkspace(usuario_id=current_user.id)
        db.session.add(workspace)
    workspace.archivos = project["files"]
    workspace.carpetas = project["folders"]
    workspace.git = project["git"]
    workspace.actualizado_en = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(ok=True, actualizado=_marca(workspace))
