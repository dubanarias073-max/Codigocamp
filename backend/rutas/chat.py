"""Chat de mensajes entre amigos."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from datetime import timedelta

from models import Attachment, ChatBorrado, Message, db, utcnow
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
        from servicios.perfil import contar_actividad, get_profile
        contar_actividad(get_profile(current_user), "mensajes")
        db.session.commit()
    after = parse_integer(request.args.get("despues"), 0)
    query = Message.query.filter(Message.amistad_id == friendship.id, Message.id > borrado_hasta(current_user.id, friendship.id))
    messages = query.filter(Message.id > after).order_by(Message.id).limit(50).all() if after else query.order_by(Message.id.desc()).limit(50).all()[::-1]
    query.filter(Message.leido.is_(False), Message.autor_id != current_user.id).update(
        {Message.leido: True}, synchronize_session=False,
    )
    db.session.commit()
    adj = {}
    if messages:
        for a in Attachment.query.filter(Attachment.mensaje_id.in_([m.id for m in messages])).order_by(Attachment.id).all():
            adj.setdefault(a.mensaje_id, []).append(publico(a))
    # Mensajes que se eliminaron hace poco (para quitarlos también de la pantalla de la otra persona)
    borrados = [m.id for m in query.filter(Message.borrado_en.isnot(None), Message.borrado_en > utcnow() - timedelta(days=2)).with_entities(Message.id).all()]
    return jsonify(mensajes=[_ser(message, adj) for message in messages], borrados=borrados)


def borrado_hasta(usuario_id, amistad_id):
    """Último mensaje que esta persona eliminó de su vista (0 si nunca borró el chat)."""
    b = ChatBorrado.query.filter_by(usuario_id=usuario_id, amistad_id=amistad_id).first()
    return b.hasta_mensaje_id if b else 0


@bp.delete("/api/chat/<int:friendship_id>/")
@login_required
def borrar_chat(friendship_id):
    """«Eliminar chat»: desaparece solo para quien lo borra. La otra persona conserva la conversación completa."""
    friendship = my_friendships(current_user.id).filter_by(id=friendship_id).first()
    if not friendship:
        return api_error("Esa conversación no existe.", 404)
    ultimo = db.session.query(db.func.max(Message.id)).filter(Message.amistad_id == friendship.id).scalar() or 0
    b = ChatBorrado.query.filter_by(usuario_id=current_user.id, amistad_id=friendship.id).first()
    if b:
        b.hasta_mensaje_id, b.creado_en = max(b.hasta_mensaje_id, ultimo), utcnow()
    else:
        db.session.add(ChatBorrado(usuario_id=current_user.id, amistad_id=friendship.id, hasta_mensaje_id=ultimo))
    db.session.flush()
    # Lo que ya borraron las dos personas no le sirve a nadie: se elimina de verdad (con sus adjuntos)
    otro = friendship.a_usuario_id if friendship.de_usuario_id == current_user.id else friendship.de_usuario_id
    ambos = min(ultimo, borrado_hasta(otro, friendship.id))
    if ambos:
        viejos = [m.id for m in Message.query.filter(Message.amistad_id == friendship.id, Message.id <= ambos).with_entities(Message.id).all()]
        if viejos:
            Attachment.query.filter(Attachment.mensaje_id.in_(viejos)).delete(synchronize_session=False)
            Message.query.filter(Message.id.in_(viejos)).delete(synchronize_session=False)
    db.session.commit()
    return jsonify(ok=True)


def _ser(message, adj):
    return {
        "id": message.id, "texto": "" if message.borrado_en else message.texto, "yo": message.autor_id == current_user.id,
        "hora": hora_local(message.creado_en, _perfil_zona()), "fecha": iso(message.creado_en),
        "adjuntos": [] if message.borrado_en else adj.get(message.id, []), "borrado": bool(message.borrado_en),
    }


@bp.delete("/api/chat/<int:friendship_id>/<int:mensaje_id>/")
@login_required
def borrar_mensaje(friendship_id, mensaje_id):
    """«Eliminar para todos»: solo quien lo mandó. Se borran el texto y los adjuntos (la otra persona ya no los ve)."""
    friendship = my_friendships(current_user.id).filter_by(id=friendship_id).first()
    mensaje = Message.query.filter_by(id=mensaje_id, amistad_id=friendship.id).first() if friendship else None
    if mensaje is None:
        return api_error("Ese mensaje no existe.", 404)
    if mensaje.autor_id != current_user.id:
        return api_error("Solo puedes eliminar los mensajes que tú enviaste.", 403)
    if not mensaje.borrado_en:
        mensaje.texto = ""
        mensaje.borrado_en = utcnow()
        Attachment.query.filter_by(mensaje_id=mensaje.id).delete()
        db.session.commit()
    return jsonify(ok=True, mensaje=_ser(mensaje, {}))
