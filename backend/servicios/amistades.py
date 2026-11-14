"""Lógica de amistades: consulta las amistades aceptadas de un usuario."""
from sqlalchemy import or_

from models import Friendship


def my_friendships(user_id):
    return Friendship.query.filter(or_(
        Friendship.de_usuario_id == user_id, Friendship.a_usuario_id == user_id,
    ))
