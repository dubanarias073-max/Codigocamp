"""Lógica de retos: arma las preguntas de un nivel y decide si un nivel está desbloqueado."""
import random

from models import Challenge, CompletedLevel, Level, Section, Stage, db


REPASO_PREGUNTAS = 10


def challenge_item(challenge):
    """Pregunta lista para enviar al navegador (sin la respuesta)."""
    data = challenge.datos or {}
    item = {"id": challenge.id, "tipo": challenge.tipo, "enunciado": challenge.enunciado, "codigo": challenge.codigo}
    if challenge.tipo == "opcion":
        item["opciones"] = random.sample(challenge.opciones, len(challenge.opciones))
    elif challenge.tipo == "ordenar":
        pieces = list(data.get("piezas", []))
        random.shuffle(pieces)
        item["piezas"] = pieces
    elif challenge.tipo == "codigo":
        item.update(fn=data.get("fn"), plantilla=data.get("plantilla", ""), casos=data.get("casos", []))
    elif challenge.tipo == "caso":
        item.update(fn=data.get("fn"), defectuosa=data.get("defectuosa", ""), correcta=data.get("correcta", ""))
    return item


def level_challenges(level):
    """Lección: sus 10 preguntas. Práctica: 10 al azar de lo visto en la etapa hasta esa sección.
    Trofeo (examen): 10 al azar de todas las lecciones de la etapa."""
    if level.tipo == "leccion":
        return list(level.retos)
    query = Challenge.query.join(Level).join(Section).filter(
        Section.etapa_id == level.seccion.etapa_id, Level.tipo == "leccion")
    if level.tipo == "practica":
        query = query.filter(Section.orden <= level.seccion.orden)
    pool = query.all()
    return random.sample(pool, min(REPASO_PREGUNTAS, len(pool)))


def all_levels(course):
    return (
        Level.query.join(Section).join(Stage).filter(Stage.curso_id == course.id)
        .order_by(Stage.orden, Section.orden, Level.orden).all()
    )


def allowed_level(user, level):
    course = level.seccion.etapa.course
    completed = {
        item[0] for item in db.session.query(CompletedLevel.nivel_id).join(Level).join(Section).join(Stage).filter(
            CompletedLevel.usuario_id == user.id, Stage.curso_id == course.id,
        ).all()
    }
    if level.id in completed:
        return True
    for item in all_levels(course):
        if item.id not in completed:
            return item.id == level.id
    return False
