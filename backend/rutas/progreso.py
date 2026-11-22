"""Progreso general, lecciones hechas y desafíos del día y del mes."""
import calendar
from datetime import timedelta

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from models import Course, DailyActivity, DailyChallenge, LessonDone, MonthChallenge, db
from constantes import MESES, META_MES, PREMIO_MES
from servicios.perfil import award_xp, contar_actividad, encargos_del_dia, get_profile, progreso_encargo, progress, reward_text
from utilidades import api_error, json_body

bp = Blueprint("progreso", __name__)


@bp.get("/api/progreso/")
@login_required
def progreso():
    return jsonify(progress(current_user))


@bp.get("/api/progreso/lecciones/<slug>/")
@login_required
def lecciones_hechas(slug):
    """Títulos de las lecciones que ya hiciste en un curso (Aprende las marca y abre la primera que te falta)."""
    course = Course.query.filter_by(slug=str(slug)[:40], activo=True).first()
    if not course:
        return jsonify(hechas=[])
    filas = LessonDone.query.filter_by(usuario_id=current_user.id, curso_id=course.id).all()
    return jsonify(hechas=sorted({f.leccion for f in filas}))


@bp.post("/api/progreso/leccion/")
@login_required
def leccion_hecha():
    data = json_body()
    if isinstance(data, tuple):
        return data
    course = Course.query.filter_by(slug=str(data.get("curso", "")), activo=True).first()
    lesson = str(data.get("leccion", "")).strip()[:120]
    if not course or not lesson:
        return api_error("Datos no válidos.")
    done = LessonDone.query.filter_by(usuario_id=current_user.id, curso_id=course.id, leccion=lesson).first()
    new = done is None
    if new:
        db.session.add(LessonDone(usuario_id=current_user.id, curso_id=course.id, leccion=lesson))
        profile = get_profile(current_user)
        rewards = award_xp(profile, 5) + contar_actividad(profile, "lecciones")
    else:
        rewards = []
    db.session.commit()
    return jsonify(nueva=new, desafios_completados=rewards, **progress(current_user))


@bp.get("/api/desafios/")
@login_required
def desafios():
    from servicios.zona import ahora_de
    now = ahora_de(get_profile(current_user))   # medianoche y «hoy» en la zona horaria de la persona
    today = now.date()
    activity = DailyActivity.query.filter_by(usuario_id=current_user.id, fecha=today).first()
    completed = {item.clave for item in DailyChallenge.query.filter_by(usuario_id=current_user.id, fecha=today).all()}
    month = MonthChallenge.query.filter_by(usuario_id=current_user.id, mes=today.replace(day=1)).first()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    month_reward = reward_text(PREMIO_MES)
    return jsonify(
        mes={
            "nombre": MESES[today.month - 1], "puntos": min(month.puntos if month else 0, META_MES),
            "meta": META_MES, "dias_restantes": calendar.monthrange(today.year, today.month)[1] - today.day,
            "premio": month_reward, "completado": bool(month and month.premio_dado),
        },
        horas_restantes=max(0, int((midnight - now).total_seconds() // 3600)),
        hoy=[{
            "clave": item["clave"], "icono": item["icono"], "titulo": item["titulo"], "meta": item["meta"],
            "progreso": progreso_encargo(item, activity),
            "premio": reward_text(item["premio"]), "completado": item["clave"] in completed,
            "datos": dict(item["premio"]), "cofre": "plata" if item["premio"].get("diamante", 0) >= 20 else "madera",
        } for item in encargos_del_dia(current_user.id, today)],
    )


@bp.post("/api/actividad/")
@login_required
def actividad():
    """Acciones que cuentan para los encargos y no pasan por otra ruta (por ahora: ejecutar código en Trabajo)."""
    from utilidades import too_many
    data = json_body()
    if isinstance(data, tuple):
        return data
    campo = str(data.get("campo", ""))
    if campo != "ejecuciones":
        return api_error("Acción no válida.")
    if too_many(f"actividad:{current_user.id}:{campo}", 1, 15):   # como mucho una cada 15 s (no se puede inflar)
        return jsonify(desafios_completados=[])
    rewards = contar_actividad(get_profile(current_user), campo)
    db.session.commit()
    return jsonify(desafios_completados=rewards)

