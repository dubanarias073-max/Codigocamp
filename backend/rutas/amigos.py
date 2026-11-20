"""Amigos: buscar usuarios, enviar, aceptar y quitar solicitudes."""
from rutas.cosmeticos import equipados_de, foto_url
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from models import Friendship, Message, Profile, User, db
from servicios.amistades import my_friendships
from servicios.perfil import get_profile
from utilidades import api_error, json_body, too_many

bp = Blueprint("amigos", __name__)


@bp.get("/api/amigos/")
@login_required
def amigos():
    profile = get_profile(current_user)
    friendships = my_friendships(current_user.id).all()
    friends, received, sent = [], [], []
    for friendship in friendships:
        other = friendship.a_usuario if friendship.de_usuario_id == current_user.id else friendship.de_usuario
        item = {"id": friendship.id, "nombre": other.nombre, "alias": other.profile.alias if other.profile else "",
                "avatar": (other.profile.avatar or "") if other.profile else "", "foto": foto_url(other.id), "marco": equipados_de(other.id)["marco"]}
        if friendship.estado == "aceptada":
            last = Message.query.filter_by(amistad_id=friendship.id).order_by(Message.id.desc()).first()
            unread = Message.query.filter(
                Message.amistad_id == friendship.id, Message.leido.is_(False),
                Message.autor_id != current_user.id,
            ).count()
            item.update(no_leidos=unread, ultimo=last.texto[:60] if last else "", orden=last.id if last else 0)
            friends.append(item)
        elif friendship.a_usuario_id == current_user.id:
            received.append(item)
        else:
            sent.append(item)
    friends.sort(key=lambda item: -item["orden"])
    return jsonify(
        yo={"nombre": current_user.nombre, "alias": profile.alias, "codigo": profile.codigo, "avatar": profile.avatar or "", "foto": foto_url(current_user.id), "marco": equipados_de(current_user.id)["marco"]},
        amigos=friends, recibidas=received, enviadas=sent,
    )


@bp.get("/api/usuarios/buscar/")
@login_required
def usuarios_buscar():
    texto = str(request.args.get("q", "")).strip().lstrip("@")
    if not 2 <= len(texto) <= 30:
        return jsonify(resultados=[])
    if too_many(f"buscar:{current_user.id}", 60, 600):
        return api_error("Has buscado muchas veces. Espera unos minutos.", 429)
    limpio = texto.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    filas = (Profile.query.join(User, User.id == Profile.usuario_id)
             .filter(User.activo.is_(True), Profile.usuario_id != current_user.id,
                     or_(Profile.alias.like(limpio + "%", escape="\\"), func.lower(User.nombre).like("%" + limpio + "%", escape="\\")))
             .order_by(Profile.alias).limit(8).all())
    relacion = {}
    for f in my_friendships(current_user.id).all():
        otro = f.a_usuario_id if f.de_usuario_id == current_user.id else f.de_usuario_id
        relacion[otro] = "amigo" if f.estado == "aceptada" else ("enviada" if f.de_usuario_id == current_user.id else "recibida")
    return jsonify(resultados=[{
        "nombre": p.user.nombre, "alias": p.alias, "avatar": p.avatar or "", "foto": foto_url(p.usuario_id), "relacion": relacion.get(p.usuario_id),
    } for p in filas if p.alias])


@bp.post("/api/amigos/agregar/")
@login_required
def amigo_agregar():
    data = json_body()
    if isinstance(data, tuple):
        return data
    text = str(data.get("usuario", "")).strip().lstrip("@")
    if not text or len(text) > 30:
        return api_error("Escribe un ID o un nombre de usuario.")
    if too_many(f"amigos:{current_user.id}", 20, 3600):
        return api_error("Has buscado muchas veces. Inténtalo más tarde.", 429)
    other_profile = Profile.query.filter(
        or_(Profile.alias == text.lower(), Profile.codigo == text.upper())
    ).first()
    if not other_profile or not other_profile.user.activo:
        return api_error("No encontramos a nadie con ese ID o nombre de usuario.", 404)
    if other_profile.usuario_id == current_user.id:
        return api_error("Ese eres tú.")
    previous = my_friendships(current_user.id).filter(
        or_(Friendship.de_usuario_id == other_profile.usuario_id, Friendship.a_usuario_id == other_profile.usuario_id)
    ).first()
    if previous:
        if previous.estado == "aceptada":
            return api_error("Ya son amigos.", 409)
        if previous.de_usuario_id == current_user.id:
            return api_error("Ya le enviaste una solicitud.", 409)
        previous.estado = "aceptada"
        db.session.commit()
        return jsonify(estado="aceptada", nombre=other_profile.user.nombre)
    db.session.add(Friendship(de_usuario_id=current_user.id, a_usuario_id=other_profile.usuario_id))
    db.session.commit()
    return jsonify(estado="pendiente", nombre=other_profile.user.nombre), 201


@bp.post("/api/amigos/<int:friendship_id>/responder/")
@login_required
def amigo_responder(friendship_id):
    friendship = Friendship.query.filter_by(
        id=friendship_id, a_usuario_id=current_user.id, estado="pendiente",
    ).first()
    if not friendship:
        return api_error("Esa solicitud no existe.", 404)
    data = json_body()
    if isinstance(data, tuple):
        return data
    if data.get("aceptar"):
        friendship.estado = "aceptada"
    else:
        db.session.delete(friendship)
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/api/amigos/<int:friendship_id>/quitar/")
@login_required
def amigo_quitar(friendship_id):
    friendship = my_friendships(current_user.id).filter_by(id=friendship_id).first()
    if not friendship:
        return api_error("Esa amistad no existe.", 404)
    db.session.delete(friendship)
    db.session.commit()
    return jsonify(ok=True)
