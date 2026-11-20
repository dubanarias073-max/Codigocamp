"""Progreso general, lecciones hechas y desafíos del día y del mes."""
import calendar
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from models import Course, DailyActivity, DailyChallenge, LessonDone, MonthChallenge, db
from constantes import DAILY_CHALLENGES, MESES, META_MES, PREMIO_MES
from servicios.perfil import award_xp, get_profile, progress, reward_text
from utilidades import api_error, json_body

bp = Blueprint("progreso", __name__)


@bp.get("/api/progreso/")
@login_required
def progreso():
    return jsonify(progress(current_user))


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
        rewards = award_xp(get_profile(current_user), 5)
    else:
        rewards = []
    db.session.commit()
    return jsonify(nueva=new, desafios_completados=rewards, **progress(current_user))


@bp.get("/api/desafios/")
@login_required
def desafios():
    today = date.today()
    now = datetime.now().astimezone()
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
            "progreso": min(item["meta"], getattr(activity, item["campo"], 0) if activity else 0),
            "premio": reward_text(item["premio"]), "completado": item["clave"] in completed,
            "datos": dict(item["premio"]), "cofre": "plata" if item["premio"].get("diamante", 0) >= 20 else "madera",
        } for item in DAILY_CHALLENGES],
    )
