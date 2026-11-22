"""Camino de retos: cursos, ruta, niveles, preguntas y completar niveles."""
import random

from constantes import MAX_SALVARRACHAS, MAX_VIDAS_REGEN
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func

from models import Challenge, CompletedLevel, Course, Level, Profile, Section, Stage, db
from servicios.perfil import award_xp, get_profile, lose_life, progress, refresh_lives
from servicios.retos import allowed_level, challenge_item, estados_niveles, level_challenges
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
    estados = estados_niveles(current_user, course)
    stages = []
    for stage in course.etapas:
        sections = []
        for section in stage.secciones:
            levels = []
            for level in section.niveles:
                state = estados.get(level.id, "bloqueado")
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


def _premios_de_cofre(profile, level):
    """Cofre del camino (uno por sección): diamantes siempre, y además vidas llenas o un salvarrachas.
    Más avanzada la sección, más diamantes. El sorteo es fijo por persona y cofre (no se repite recargando)."""
    seccion = db.session.get(Section, level.seccion_id)
    tramo = min(int(getattr(seccion, "orden", 1) or 1), 10)
    suerte = random.Random(f"{profile.usuario_id}:{level.id}")
    gemas = suerte.randint(25, 45) + 5 * tramo
    if suerte.random() < 0.15:          # cofre dorado: el doble
        gemas *= 2
    profile.diamante += gemas
    premios = [{"tipo": "diamante", "cantidad": gemas, "texto": f"+{gemas} diamantes"}]
    if profile.salvarrachas < MAX_SALVARRACHAS and suerte.random() < 0.4:
        profile.salvarrachas += 1
        premios.append({"tipo": "salvarrachas", "cantidad": 1, "texto": "+1 salvarrachas"})
    elif profile.vidas < MAX_VIDAS_REGEN:
        ganadas = MAX_VIDAS_REGEN - profile.vidas
        profile.vidas = MAX_VIDAS_REGEN
        premios.append({"tipo": "vidas", "cantidad": ganadas, "texto": "Vidas llenas"})
    else:
        extra = 10 + 5 * tramo
        profile.diamante += extra
        premios[0]["cantidad"] += extra
        premios[0]["texto"] = f"+{premios[0]['cantidad']} diamantes"
    return premios


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
    racha_antes, actividad_antes = profile.racha_actual, profile.ultima_actividad
    rewards = award_xp(profile, xp, levels=0 if chest else 1, perfect=(failures == 0 and not chest))
    # ¿Esta lección hizo la racha de hoy? (para el sonido y la animación de la racha, como en Duolingo)
    racha_hoy = profile.ultima_actividad != actividad_antes and profile.racha_actual >= 1
    minerals = {"diamante": 0}
    premios = []
    if new and chest:
        premios = _premios_de_cofre(profile, level)
        minerals["diamante"] = sum(p["cantidad"] for p in premios if p["tipo"] == "diamante")
    if new and not chest:
        completed_count = CompletedLevel.query.filter_by(usuario_id=current_user.id).count()
        ganados = 5 + (10 if failures == 0 else 0)          # cada nivel nuevo da diamantes; sin fallos, más
        if completed_count and completed_count % 5 == 0:   # y cada cinco niveles nuevos, un bono
            ganados += 25
        profile.diamante += ganados
        minerals["diamante"] = ganados
    db.session.commit()
    return jsonify(
        xp_ganado=xp, minerales_ganados=minerals, estrellas=completed.estrellas, nueva=new, premios=premios,
        racha_hoy=bool(racha_hoy), racha_antes=racha_antes,
        desafios_completados=rewards, **progress(current_user),
    )
