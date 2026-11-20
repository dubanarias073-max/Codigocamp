"""Términos y condiciones: la versión vigente sale de frontend/pages/terminos.html (atributo data-version),
así el texto y su versión viven en un solo lugar. Si la versión cambia, a todas las cuentas se les pide aceptar otra vez."""
import re

from flask import has_request_context, request

from constantes import FRONTEND

_cache = {"mtime": None, "version": "1"}


def version_actual():
    ruta = FRONTEND / "pages" / "terminos.html"
    try:
        mtime = ruta.stat().st_mtime
        if mtime != _cache["mtime"]:
            m = re.search(r'id="terminosTexto"[^>]*data-version="([^"]{1,20})"', ruta.read_text(encoding="utf-8"))
            _cache.update(mtime=mtime, version=m.group(1) if m else "1")
    except OSError:
        pass
    return _cache["version"]


def acepto_actual(usuario_id):
    from models import TermsAcceptance, db
    fila = db.session.get(TermsAcceptance, usuario_id)
    return bool(fila and fila.version == version_actual())


def registrar_aceptacion(usuario_id):
    from models import TermsAcceptance, db, utcnow
    ip = (request.remote_addr or "")[:45] if has_request_context() else ""
    fila = db.session.get(TermsAcceptance, usuario_id)
    if fila:
        fila.version, fila.aceptado, fila.ip = version_actual(), utcnow(), ip
    else:
        db.session.add(TermsAcceptance(usuario_id=usuario_id, version=version_actual(), ip=ip))
