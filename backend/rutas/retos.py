"""Camino de retos: cursos, ruta, niveles, preguntas y completar niveles."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func

from models import Challenge, CompletedLevel, Course, Level, Profile, Section, Stage, db
from servicios.perfil import award_xp, get_profile, lose_life, progress, refresh_lives
from servicios.retos import allowed_level, challenge_item, level_challenges
from utilidades import api_error, json_body, normalize, parse_integer

bp = Blueprint("retos", __name__)


@bp.get("/api/cursos/")
def cursos():
    course_ids = {row[0] for row in db.session.query(Stage.curso_id).distinct().all()}
    courses = Course.query.filter_by(activo=True).order_by(Course.orden, Course.nombre).all()
    base = db.session.query(Stage.curso_id, func.count(Level.id)).join(Section, Section.etapa_id == Stage.id).join(
        Level, Level.seccion_id == Section.id).filter(Level.tipo == "leccion")
    totals = dict(base.group_by(Stage.curso_id).all())
    done = {}
    if current_user.is_authenticated:
        done = dict(base.join(CompletedLevel, CompletedLevel.nivel_id == Level.id).filter(
            CompletedLevel.usuario_id == current_user.id).group_by(Stage.curso_id).all())
    return jsonify(cursos=[{
        "slug": item.slug, "nombre": item.nombre, "tipo": item.tipo, "sigla": item.sigla,
        "color": item.color, "descripcion": item.descripcion, "tiene_retos": item.id in course_ids,
        "lecciones": totals.get(item.id, 0), "hechas": done.get(item.id, 0),
    } for item in courses])


@bp.get("/api/ruta/")
@login_required
def ruta():
    profile = get_profile(current_user)
    course = Course.query.filter_by(slug=request.args.get("curso", ""), activo=True).first() or profile.curso_actual
    if not course:
        return api_error("Elige un curso.", 404)
    completed = {
        entry.nivel_id: entry.estrellas
        for entry in CompletedLevel.query.join(Level).join(Section).join(Stage).filter(
            CompletedLevel.usuario_id == current_user.id, Stage.curso_id == course.id
        ).all()
    }
    marked = False
    stages = []
    for stage in course.etapas:
        sections = []
        for section in stage.secciones:
            levels = []
            for level in section.niveles:
                if level.id in completed:
                    state = "hecho"
                elif not marked:
                    state, marked = "actual", True
                else:
                    state = "bloqueado"
                levels.append({
                    "id": level.id, "titulo": level.titulo, "tipo": level.tipo, "estado": state,
                    "estrellas": completed.get(level.id, 0), "xp": level.xp,
                })
            sections.append({"id": section.id, "orden": section.orden, "titulo": section.titulo, "niveles": levels})
        stages.append({
            "id": stage.id, "orden": stage.orden, "titulo": stage.titulo,
            "descripcion": stage.descripcion, "secciones": sections,
        })
    return jsonify(curso={"slug": course.slug, "nombre": course.nombre, "color": course.color}, etapas=stages)


@bp.get("/api/nivel/<int:level_id>/")
@login_required
def nivel_detalle(level_id):
    level = db.session.get(Level, level_id)
    if not level or level.tipo not in ("leccion", "practica", "trofeo"):
        return api_error("No encontramos ese nivel.", 404)
    if not allowed_level(current_user, level):
        return api_error("Primero completa los niveles anteriores.", 403)
    challenges = [challenge_item(challenge) for challenge in level_challenges(level)]
    course = level.seccion.etapa.course
    return jsonify(
        nivel={"id": level.id, "titulo": level.titulo, "xp": level.xp, "seccion": level.seccion.titulo,
               "etapa": level.seccion.etapa.titulo},
        curso={"slug": course.slug, "nombre": course.nombre, "color": course.color},
        retos=challenges, vidas=refresh_lives(get_profile(current_user)),
    )


@bp.post("/api/reto/<int:challenge_id>/responder/")
@login_required
def reto_responder(challenge_id):
    challenge = db.session.get(Challenge, challenge_id)
    if not challenge:
        return api_error("No encontramos ese reto.", 404)
    get_profile(current_user)
    profile = Profile.query.filter_by(usuario_id=current_user.id).with_for_update().one()
    refresh_lives(profile)
    if profile.vidas <= 0:
        db.session.commit()
        return api_error("Te quedaste sin vidas.", 403)
    if not allowed_level(current_user, challenge.nivel):
        return api_error("Nivel bloqueado.", 403)
    data = json_body()
    if isinstance(data, tuple):
        return data
    extra = challenge.datos or {}
    if challenge.tipo == "opcion":
        correct, answer = str(data.get("respuesta", "")) == challenge.respuesta, challenge.respuesta
    elif challenge.tipo == "completar":
        accepted = challenge.respuesta.split("|")
        correct = normalize(data.get("respuesta", "")) in {normalize(item) for item in accepted}
        answer = accepted[0]
    elif challenge.tipo == "error":
        correct = str(data.get("respuesta", "")).strip() == challenge.respuesta.strip()
        answer = f"la línea {challenge.respuesta}"
    elif challenge.tipo == "ordenar":
        pieces = extra.get("piezas", [])
        given = data.get("respuesta")
        correct = isinstance(given, list) and [str(item) for item in given] == pieces
        answer = "  →  ".join(pieces)
    else:
        correct, answer = bool(data.get("correcto")), ""
    if not correct:
        lose_life(profile)
    db.session.commit()
    return jsonify(
        correcto=correct, correcta=answer, explicacion=challenge.explicacion, vidas=profile.vidas,
    )


@bp.post("/api/nivel/<int:level_id>/completar/")
@login_required
def nivel_completar(level_id):
    level = db.session.get(Level, level_id)
    if not level:
        return api_error("No encontramos ese nivel.", 404)
    if not allowed_level(current_user, level):
        return api_error("Primero completa los niveles anteriores.", 403)
    data = json_body()
    if isinstance(data, tuple):
        return data
    failures = max(0, min(parse_integer(data.get("fallos"), 0), 1000))
    profile = get_profile(current_user)
    chest = level.tipo == "cofre"
    stars = 3 if failures == 0 else 2 if failures <= 2 else 1
    completed = CompletedLevel.query.filter_by(usuario_id=current_user.id, nivel_id=level.id).first()
    new = completed is None
    if new:
        completed = CompletedLevel(usuario_id=current_user.id, nivel_id=level.id, estrellas=stars)
        db.session.add(completed)
        db.session.flush()
    else:
        completed.estrellas = max(completed.estrellas, stars)
        completed.veces += 1
    xp = level.xp if new else (0 if chest else 5)
    rewards = award_xp(profile, xp, levels=0 if chest else 1, perfect=(failures == 0 and not chest))
    minerals = {"diamante": 0}
    if new:
        completed_count = CompletedLevel.query.filter_by(usuario_id=current_user.id).count()
        if completed_count and completed_count % 5 == 0:   # cada cinco niveles nuevos, un diamante
            profile.diamante += 1
            minerals["diamante"] = 1
    db.session.commit()
    return jsonify(
        xp_ganado=xp, minerales_ganados=minerals, estrellas=completed.estrellas, nueva=new,
        desafios_completados=rewards, **progress(current_user),
    )
