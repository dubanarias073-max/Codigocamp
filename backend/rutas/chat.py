"""Chat de mensajes entre amigos."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Attachment, Message, db
from rutas.adjuntos import publico, tomar
from servicios.amistades import my_friendships
from utilidades import api_error, json_body, parse_integer, too_many
from servicios.zona import hora_local, iso

bp = Blueprint("chat", __name__)


def _perfil_zona():
    """Perfil de quien pide (para la hora de los mensajes en su zona horaria)."""
    from flask import g
    from models import Profile
    if "cc_perfil_zona" not in g:
        g.cc_perfil_zona = Profile.query.filter_by(usuario_id=current_user.id).first() if current_user.is_authenticated else None
    return g.cc_perfil_zona


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
        ids = data.get("adjuntos") or []
        if (not text and not ids) or len(text) > 300:
            return api_error("Escribe un mensaje de hasta 300 caracteres o adjunta un archivo.")
        if too_many(f"chat:{current_user.id}", 20, 60):
            return api_error("Estás escribiendo muy rápido. Espera un momento.", 429)
        mensaje = Message(amistad_id=friendship.id, autor_id=current_user.id, texto=text)
        db.session.add(mensaje)
        db.session.flush()
        try:
            tomar(ids, "chat", mensaje.id)
        except ValueError as e:
            db.session.rollback()
            return api_error(str(e))
        db.session.commit()
    after = parse_integer(request.args.get("despues"), 0)
    query = Message.query.filter_by(amistad_id=friendship.id)
    messages = query.filter(Message.id > after).order_by(Message.id).limit(50).all() if after else query.order_by(Message.id.desc()).limit(50).all()[::-1]
    query.filter(Message.leido.is_(False), Message.autor_id != current_user.id).update(
        {Message.leido: True}, synchronize_session=False,
    )
    db.session.commit()
    adj = {}
    if messages:
        for a in Attachment.query.filter(Attachment.mensaje_id.in_([m.id for m in messages])).order_by(Attachment.id).all():
            adj.setdefault(a.mensaje_id, []).append(publico(a))
    return jsonify(mensajes=[{
        "id": message.id, "texto": message.texto, "yo": message.autor_id == current_user.id,
        "hora": hora_local(message.creado_en, _perfil_zona()), "fecha": iso(message.creado_en), "adjuntos": adj.get(message.id, []),
    } for message in messages])
