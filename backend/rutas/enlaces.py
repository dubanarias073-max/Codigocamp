"""Revisión de enlaces antes de abrirlos (Trabajo, chats, IA). Ver servicios/seguridad_enlaces.py.
Los enlaces NO se guardan: se revisan y se responde."""
from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from servicios.seguridad_enlaces import revisar_enlace
from utilidades import api_error, json_body, too_many

bp = Blueprint("enlaces", __name__)


@bp.post("/api/seguridad/enlace")
@login_required
def revisar():
    data = json_body()
    if isinstance(data, tuple):
        return data
    if too_many(f"enlaces:{current_user.id}", 120, 60):
        return api_error("Demasiadas revisiones seguidas. Espera un momento.", 429)
    return jsonify(revisar_enlace(str(data.get("url", ""))[:4000]))
