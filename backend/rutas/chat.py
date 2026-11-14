"""Chat de mensajes entre amigos."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Message, db
from servicios.amistades import my_friendships
from utilidades import api_error, json_body, local_time, parse_integer, too_many

bp = Blueprint("chat", __name__)


@bp.route("/api/chat/<int:friendship_id>/", methods=["GET", "POST"])
@login_required
def chat(friendship_id):
    friendship = my_friendships(current_user.id).filter_by(id=friendship_id, estado="aceptada").first()
    if not friendship:
        return api_error("Esa conversación no existe.", 404)
    if request.method == "POST":
        data = json_body()
        if isinstance(data, tuple):
            return data
        text = " ".join(str(data.get("texto", "")).split())
        if not text or len(text) > 300:
            return api_error("Escribe un mensaje de hasta 300 caracteres.")
        if too_many(f"chat:{current_user.id}", 20, 60):
            return api_error("Estás escribiendo muy rápido. Espera un momento.", 429)
        db.session.add(Message(amistad_id=friendship.id, autor_id=current_user.id, texto=text))
        db.session.commit()
    after = parse_integer(request.args.get("despues"), 0)
    query = Message.query.filter_by(amistad_id=friendship.id)
    messages = query.filter(Message.id > after).order_by(Message.id).limit(50).all() if after else query.order_by(Message.id.desc()).limit(50).all()[::-1]
    query.filter(Message.leido.is_(False), Message.autor_id != current_user.id).update(
        {Message.leido: True}, synchronize_session=False,
    )
    db.session.commit()
    return jsonify(mensajes=[{
        "id": message.id, "texto": message.texto, "yo": message.autor_id == current_user.id,
        "hora": local_time(message.creado_en),
    } for message in messages])
