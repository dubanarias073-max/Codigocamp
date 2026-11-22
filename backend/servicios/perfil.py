"""Lógica del perfil: vidas, racha, XP, premios y desafíos. Aquí se decide cuánto progreso gana el usuario."""
import re
import secrets
import unicodedata
from datetime import timedelta, timezone

from sqlalchemy import func

from models import CompletedLevel, Course, DailyActivity, DailyChallenge, LessonDone, MonthChallenge, Profile, db, utcnow
from constantes import DAILY_CHALLENGES, ENCARGOS, ENCARGOS_POR_DIA, MAX_VIDAS, MAX_VIDAS_REGEN, MESES, META_MES, MINUTOS_VIDA, PREMIO_MES, PUNTOS_POR_DESAFIO


def ensure_identity(profile, name):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    profile.codigo = "".join(secrets.choice(chars) for _ in range(6))
    base = unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]", "", base)[:12] or "usuario"
    profile.alias = f"{base}{secrets.randbelow(9000) + 1000}"


def get_profile(user):
    profile = user.profile
    if profile is None:
        profile = Profile(user=user)
        ensure_identity(profile, user.nombre)
        db.session.add(profile)
        db.session.flush()
    if not profile.alias or not profile.codigo:
        ensure_identity(profile, user.nombre)
    refresh_lives(profile)
    return profile


def serialize_user(user, profile):
    return {
        "id": user.id, "nombre": user.nombre, "email": user.email,
        "onboarding": profile.onboarding_completo, "tema": profile.tema, "idioma": profile.idioma or "es", "buscable_correo": profile.buscable_correo is not False,
        "alias": profile.alias, "codigo": profile.codigo, "avatar": "",
        "desde": user.creado_en.date().isoformat(),
        **_extras(user.id),
    }


def _extras(usuario_id):
    from rutas.cosmeticos import equipados_de, foto_url
    from servicios.terminos import acepto_actual
    return {"foto": foto_url(usuario_id), "cosmeticos": equipados_de(usuario_id), "terminos": acepto_actual(usuario_id)}


def _user(user):
    profile = get_profile(user)
    data = serialize_user(user, profile)
    db.session.commit()
    return data


def progress(user):
    profile = get_profile(user)
    lessons = db.session.query(Course.slug, func.count(LessonDone.id)).join(
        LessonDone, LessonDone.curso_id == Course.id,
    ).filter(LessonDone.usuario_id == user.id).group_by(Course.slug).all()
    completed_count = CompletedLevel.query.filter_by(usuario_id=user.id).count()
    db.session.commit()
    return {
        "perfil": {
            "xp": profile.xp, "xp_total": profile.xp_total, "nivel": profile.nivel,
            "xp_nivel": profile.xp_total % 100,
            "diamante": profile.diamante, "vidas": profile.vidas,
            "segundos_vida": seconds_to_next_life(profile), "salvarrachas": profile.salvarrachas,
            "racha_actual": profile.racha_actual, "racha_maxima": profile.racha_maxima,
            "meta_minutos": profile.meta_minutos,
        },
        "curso_actual": {"slug": profile.curso_actual.slug, "nombre": profile.curso_actual.nombre} if profile.curso_actual else None,
        "lecciones_hechas": {slug: count for slug, count in lessons},
        "niveles_hechos": completed_count,
    }


def refresh_lives(profile):
    if profile.vidas >= MAX_VIDAS_REGEN:
        return profile.vidas
    last = profile.vidas_actualizadas
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    elapsed = int((utcnow() - last).total_seconds() // (MINUTOS_VIDA * 60))
    if elapsed > 0:
        profile.vidas = min(MAX_VIDAS_REGEN, profile.vidas + elapsed)
        profile.vidas_actualizadas = utcnow() if profile.vidas >= MAX_VIDAS_REGEN else last + timedelta(minutes=MINUTOS_VIDA * elapsed)
    return profile.vidas


def seconds_to_next_life(profile):
    if profile.vidas >= MAX_VIDAS_REGEN:
        return 0
    last = profile.vidas_actualizadas
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    remaining = MINUTOS_VIDA * 60 - (utcnow() - last).total_seconds()
    return max(0, int(remaining))


def lose_life(profile):
    if profile.vidas >= MAX_VIDAS_REGEN:
        profile.vidas_actualizadas = utcnow()
    profile.vidas = max(0, profile.vidas - 1)


def update_streak(profile):
    from servicios.zona import hoy_de
    today = hoy_de(profile)   # el día donde está la persona (su dispositivo), no el del servidor
    if profile.ultima_actividad == today:
        return
    days = (today - profile.ultima_actividad).days if profile.ultima_actividad else None
    if days == 1:
        profile.racha_actual += 1
    elif days == 2 and profile.salvarrachas > 0:
        profile.salvarrachas -= 1
        profile.racha_actual += 1
    else:
        profile.racha_actual = 1
    profile.racha_maxima = max(profile.racha_maxima, profile.racha_actual)
    profile.ultima_actividad = today


def reward_text(reward):
    labels = {"diamante": ("diamante", "diamantes"), "xp": ("XP", "XP"), "vidas": ("vida", "vidas")}
    return " y ".join(f"+{amount} {labels[key][0 if amount == 1 else 1]}" for key, amount in reward.items())


def apply_reward(profile, reward):
    for key in ("xp", "diamante"):
        amount = reward.get(key, 0)
        setattr(profile, key, getattr(profile, key) + amount)
        if key == "xp":
            profile.xp_total += amount
    profile.vidas = min(MAX_VIDAS, profile.vidas + reward.get("vidas", 0))


def encargos_del_dia(usuario_id, fecha):
    """Los 5 encargos de hoy para esta persona: cambian cada día (y no son los mismos para todos), siempre con uno de XP,
    uno de retos y el resto variados (Aprende, Chats, IA, Trabajo, combos)."""
    import random
    r = random.Random(f"cc-encargos-{usuario_id}-{fecha.isoformat()}")
    por_campo = {}
    for e in ENCARGOS:
        por_campo.setdefault(e["campo"], []).append(e)
    elegidos = [r.choice(por_campo["xp"]), r.choice(por_campo["niveles"] + por_campo["perfectos"])]
    resto = [e for e in ENCARGOS if e not in elegidos]
    r.shuffle(resto)
    campos = {e["campo"] for e in elegidos}
    for e in resto:                       # primero de campos que aún no salieron, para que sean variados
        if len(elegidos) >= ENCARGOS_POR_DIA:
            break
        if e["campo"] not in campos:
            elegidos.append(e); campos.add(e["campo"])
    for e in resto:
        if len(elegidos) >= ENCARGOS_POR_DIA:
            break
        if e not in elegidos:
            elegidos.append(e)
    return sorted(elegidos, key=lambda e: (e["premio"].get("diamante", 0), e["clave"]))


def progreso_encargo(encargo, activity):
    """Progreso (0..meta) de un encargo; los combinados («y») cuentan solo cuando se cumplen las dos partes."""
    if not activity:
        return 0
    actual = min(encargo["meta"], getattr(activity, encargo["campo"], 0) or 0)
    extra = encargo.get("y")
    if extra and (getattr(activity, extra["campo"], 0) or 0) < extra["meta"]:
        return min(actual, encargo["meta"] - 1)
    return actual


def review_challenges(profile, activity):
    new_rewards = []
    for challenge in encargos_del_dia(profile.usuario_id, activity.fecha):
        if progreso_encargo(challenge, activity) < challenge["meta"]:
            continue
        record = DailyChallenge.query.filter_by(
            usuario_id=profile.usuario_id, clave=challenge["clave"], fecha=activity.fecha,
        ).first()
        if record:
            continue
        db.session.add(DailyChallenge(
            usuario_id=profile.usuario_id, clave=challenge["clave"], fecha=activity.fecha,
        ))
        apply_reward(profile, challenge["premio"])
        new_rewards.append({"clave": challenge["clave"], "titulo": challenge["titulo"], "premio": reward_text(challenge["premio"]),
                            "datos": dict(challenge["premio"]), "cofre": "plata" if challenge["premio"].get("diamante", 0) >= 20 else "madera"})
        month = activity.fecha.replace(day=1)
        points = MonthChallenge.query.filter_by(usuario_id=profile.usuario_id, mes=month).first()
        if not points:
            points = MonthChallenge(usuario_id=profile.usuario_id, mes=month)
            db.session.add(points)
            db.session.flush()
        points.puntos += PUNTOS_POR_DESAFIO
        if points.puntos >= META_MES and not points.premio_dado:
            month_reward = dict(PREMIO_MES)
            points.premio_dado = True
            apply_reward(profile, month_reward)
            new_rewards.append({"clave": "mes", "titulo": f"Desafío de {MESES[activity.fecha.month - 1]}", "premio": reward_text(month_reward),
                                "datos": dict(month_reward), "cofre": "oro"})
    return new_rewards


def award_xp(profile, amount, levels=0, perfect=False):
    update_streak(profile)
    profile.xp += amount
    profile.xp_total += amount
    from servicios.zona import hoy_de
    today = hoy_de(profile)
    activity = actividad_de_hoy(profile)
    activity.xp += amount
    activity.niveles += levels
    activity.perfectos += int(perfect)
    db.session.flush()
    return review_challenges(profile, activity)


def actividad_de_hoy(profile):
    from servicios.zona import hoy_de
    today = hoy_de(profile)
    activity = DailyActivity.query.filter_by(usuario_id=profile.usuario_id, fecha=today).first()
    if not activity:
        activity = DailyActivity(usuario_id=profile.usuario_id, fecha=today, xp=0, niveles=0, perfectos=0, lecciones=0, mensajes=0, ia=0, ejecuciones=0)
        db.session.add(activity)
        db.session.flush()
    return activity


def contar_actividad(profile, campo, cantidad=1):
    """Suma una acción del día (lecciones, mensajes, ia, ejecuciones) y revisa los encargos. Devuelve los premios nuevos."""
    activity = actividad_de_hoy(profile)
    setattr(activity, campo, (getattr(activity, campo) or 0) + cantidad)
    db.session.flush()
    return review_challenges(profile, activity)
