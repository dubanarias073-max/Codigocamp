"""Medallas del mes (como las de Duolingo).

Cada mes tiene sus EXPERIENCIAS: el desafío del mes (encargos) y tres retos más que cambian cada mes (los mismos para
todos). Cada experiencia que completas da su premio; al completarlas TODAS ganas la medalla de ese mes, que queda para
siempre en tu perfil y la ven tus amigos. Las medallas de diciembre, octubre, septiembre… tienen el diseño de su temporada.
"""
import calendar
import random
from sqlalchemy import func

from constantes import MESES, META_MES, PUNTOS_POR_DESAFIO
from models import DailyActivity, DailyChallenge, Medal, StreakReward, db

# Diseño de la medalla de cada mes (el frontend la dibuja con estos datos: js/medallas.js)
MEDALLAS = {   # nombres por mes; cada año cambia la variante (y el frontend dibuja una insignia distinta por año)
    1: {"nombres": ["Chispa de Año Nuevo", "Despegue Anual", "Primer Commit del Año"], "icono": "🎆", "temporada": "Año nuevo"},
    2: {"nombres": ["Corazón de Código", "Amor Binario", "Match Perfecto"], "icono": "💘", "temporada": "Amor"},
    3: {"nombres": ["Brote Programador", "Semilla de Bits", "Raíz Cuadrada"], "icono": "🌱", "temporada": "Primavera"},
    4: {"nombres": ["Lluvia de Ideas", "Tormenta de Código", "Nube Creativa"], "icono": "🌧️", "temporada": "Lluvias"},
    5: {"nombres": ["Flor del Saber", "Jardín de Funciones", "Pétalo Pixel"], "icono": "🌸", "temporada": "Flores"},
    6: {"nombres": ["Sol de Vacaciones", "Verano Compilado", "Playa de Píxeles"], "icono": "☀️", "temporada": "Vacaciones"},
    7: {"nombres": ["Cometa Veloz", "Cohete Deploy", "Órbita Perfecta"], "icono": "🪁", "temporada": "Cometas"},
    8: {"nombres": ["Viento de Agosto", "Rama Maestra", "Huracán de Bucles"], "icono": "🌬️", "temporada": "Vientos"},
    9: {"nombres": ["Amistad Binaria", "Día 256", "Programador Legendario"], "icono": "💛", "temporada": "Amor y amistad · Día del programador"},
    10: {"nombres": ["Calabaza Hacker", "Bug Fantasma", "Bruja del Código"], "icono": "🎃", "temporada": "Halloween"},
    11: {"nombres": ["Búho Nocturno", "Terminal de Medianoche", "Guardián del Stack"], "icono": "🦉", "temporada": "Noches de estudio"},
    12: {"nombres": ["Estrella Navideña", "Regalo Compilado", "Nieve de Bits"], "icono": "🎄", "temporada": "Navidad"},
}

# Experiencias que pueden salir en un mes (además del desafío del mes, que siempre está)
POOL = [
    {"clave": "xp", "icono": "⭐", "titulo": "Gana {meta} XP este mes", "medida": "xp", "meta": 800, "premio": {"diamante": 120, "xp": 40}},
    {"clave": "niveles", "icono": "🎯", "titulo": "Completa {meta} niveles de retos", "medida": "niveles", "meta": 40, "premio": {"diamante": 120, "vidas": 3}},
    {"clave": "perfectos", "icono": "💎", "titulo": "Termina {meta} niveles sin fallos", "medida": "perfectos", "meta": 15, "premio": {"diamante": 140}},
    {"clave": "lecciones", "icono": "📚", "titulo": "Completa {meta} lecciones en Aprende", "medida": "lecciones", "meta": 25, "premio": {"diamante": 120, "xp": 40}},
    {"clave": "dias", "icono": "📅", "titulo": "Practica {meta} días distintos", "medida": "dias", "meta": 15, "premio": {"diamante": 150, "salvarrachas": 1}},
    {"clave": "ia", "icono": "🤖", "titulo": "Hazle {meta} preguntas al tutor de IA", "medida": "ia", "meta": 20, "premio": {"diamante": 100}},
    {"clave": "ejecuciones", "icono": "▶️", "titulo": "Ejecuta tu código {meta} veces en Trabajo", "medida": "ejecuciones", "meta": 30, "premio": {"diamante": 100, "xp": 30}},
    {"clave": "mensajes", "icono": "💬", "titulo": "Envía {meta} mensajes a tus amigos", "medida": "mensajes", "meta": 25, "premio": {"diamante": 90}},
]
PREMIO_MEDALLA = {"diamante": 500, "xp": 150, "vidas": 5, "salvarrachas": 1}
# Como Duolingo: la barra del mes se llena con los encargos de hoy que superas; cada tramo abre un cofre
HITOS_ENCARGOS = [
    {"meta": 10, "cofre": "plata", "premio": {"diamante": 50, "vidas": 2}},
    {"meta": 20, "cofre": "oro", "premio": {"diamante": 120, "xp": 50}},
    {"meta": 30, "cofre": "diamante", "premio": {"diamante": 250, "salvarrachas": 1}},
    {"meta": 50, "cofre": "legendario", "premio": {"diamante": 500, "vidas": 5, "salvarrachas": 1}},
]
# Recompensas por la experiencia (XP) que juntas en el mes: cada hito abre un cofre
HITOS_XP = [
    {"meta": 300, "cofre": "plata", "premio": {"diamante": 60, "vidas": 2}},
    {"meta": 800, "cofre": "oro", "premio": {"diamante": 150, "salvarrachas": 1}},
    {"meta": 1500, "cofre": "diamante", "premio": {"diamante": 300, "vidas": 5}},
    {"meta": 3000, "cofre": "legendario", "premio": {"diamante": 700, "salvarrachas": 2, "xp": 100}},
]


def medallas_desde():
    """Primer mes con medalla (las medallas empiezan el 1 de diciembre de 2026). Se puede cambiar con
    MEDALLAS_DESDE=AAAA-MM en backend/.env. Antes de esa fecha no hay medalla del mes ni sus experiencias."""
    import os
    from datetime import date
    try:
        anio, mes = (int(x) for x in (os.getenv("MEDALLAS_DESDE") or "2026-12").strip().strip('"').split("-")[:2])
        return date(anio, mes, 1)
    except (TypeError, ValueError):
        return date(2026, 12, 1)


def antes_de_medallas(fecha):
    return _mes(fecha) < medallas_desde()


def _mes(fecha):
    return fecha.replace(day=1)


def experiencias_del_mes(fecha):
    """Las 4 experiencias de ese mes: el desafío (encargos) y 3 que cambian cada mes (iguales para todos)."""
    r = random.Random(f"cc-medalla-{fecha:%Y-%m}")
    extra = r.sample(POOL, 3)
    desafio = {"clave": "desafio", "icono": "🗓️", "titulo": f"Supera {META_MES // PUNTOS_POR_DESAFIO} encargos del día",
               "medida": "encargos", "meta": META_MES // PUNTOS_POR_DESAFIO, "premio": {"diamante": 150}}
    return [desafio] + [{**e, "titulo": e["titulo"].format(meta=e["meta"])} for e in extra]


def medidas_del_mes(usuario_id, fecha):
    inicio = _mes(fecha)
    fin = inicio.replace(day=calendar.monthrange(inicio.year, inicio.month)[1])
    filtro = (DailyActivity.usuario_id == usuario_id, DailyActivity.fecha >= inicio, DailyActivity.fecha <= fin)
    suma = db.session.query(*(func.coalesce(func.sum(getattr(DailyActivity, c)), 0) for c in ("xp", "niveles", "perfectos", "lecciones", "ia", "ejecuciones", "mensajes"))).filter(*filtro).one()
    dias = DailyActivity.query.filter(*filtro, (DailyActivity.xp > 0) | (DailyActivity.lecciones > 0) | (DailyActivity.niveles > 0)).count()
    encargos = DailyChallenge.query.filter(DailyChallenge.usuario_id == usuario_id, DailyChallenge.fecha >= inicio, DailyChallenge.fecha <= fin).count()
    claves = ("xp", "niveles", "perfectos", "lecciones", "ia", "ejecuciones", "mensajes")
    return {**{k: int(v) for k, v in zip(claves, suma[:7])}, "dias": dias, "encargos": encargos}


def estado_del_mes(usuario_id, fecha):
    """Experiencias del mes con su progreso y si la medalla ya se ganó."""
    m = medidas_del_mes(usuario_id, fecha)
    exps = [{**e, "progreso": min(m[e["medida"]], e["meta"]), "completada": m[e["medida"]] >= e["meta"]} for e in experiencias_del_mes(fecha)]
    clave = f"{fecha:%Y-%m}"
    ganada = Medal.query.filter_by(usuario_id=usuario_id, clave=clave).first() is not None
    hitos = [{**h, "progreso": min(m["xp"], h["meta"]), "completado": m["xp"] >= h["meta"]} for h in HITOS_XP]
    hitos_enc = [{**h, "progreso": min(m["encargos"], h["meta"]), "completado": m["encargos"] >= h["meta"]} for h in HITOS_ENCARGOS]
    desde = medallas_desde()
    estado = {"clave": clave, "mes": MESES[fecha.month - 1], "anio": fecha.year, **diseno(fecha.month, fecha.year),
              "experiencias": exps, "ganada": ganada, "premio": dict(PREMIO_MEDALLA), "xp_mes": m["xp"], "hitos_xp": hitos,
              "encargos_mes": m["encargos"], "hitos_encargos": hitos_enc,
              "desde": {"anio": desde.year, "mes": desde.month, "nombre_mes": MESES[desde.month - 1]}}
    if antes_de_medallas(fecha):   # todavía no empiezan: se muestra la primera medalla que viene, sin experiencias
        estado.update(antes_de_inicio=True, experiencias=[], ganada=False,
                      proxima={"mes": MESES[desde.month - 1], "anio": desde.year, **diseno(desde.month, desde.year)})
    return estado


def diseno(mes, anio):
    """Nombre e info de la medalla de ese mes de ese año (cada año cambia)."""
    m = MEDALLAS[mes]
    return {"numero": mes, "nombre": m["nombres"][anio % len(m["nombres"])], "icono": m["icono"], "temporada": m["temporada"]}


def revisar_mes(profile, fecha):
    """Da los premios de las experiencias recién completadas y, si ya están todas, la medalla del mes."""
    from servicios.perfil import apply_reward, cofre_de, dar_salvarrachas, reward_text
    estado = estado_del_mes(profile.usuario_id, fecha)
    ganados = []

    def dar(premio):
        apply_reward(profile, {k: v for k, v in premio.items() if k in ("xp", "diamante", "vidas")})
        if premio.get("salvarrachas"):
            dar_salvarrachas(profile, premio["salvarrachas"])

    for e in estado["experiencias"]:   # (antes de que empiecen las medallas la lista viene vacía)
        if not e["completada"]:
            continue
        clave = f"exp-{estado['clave']}-{e['clave']}"
        if StreakReward.query.filter_by(usuario_id=profile.usuario_id, clave=clave).first():
            continue
        db.session.add(StreakReward(usuario_id=profile.usuario_id, clave=clave))
        dar(e["premio"])
        ganados.append({"clave": clave, "titulo": f"Experiencia de {estado['mes']}: {e['titulo']}", "premio": reward_text(e["premio"]),
                        "datos": dict(e["premio"]), "cofre": cofre_de(e["premio"])})
    for tipo, h in [("xp", h) for h in estado["hitos_xp"]] + [("enc", h) for h in estado["hitos_encargos"]]:   # XP y encargos del mes
        if not h["completado"]:
            continue
        clave = f"{'xpmes' if tipo == 'xp' else 'encmes'}-{estado['clave']}-{h['meta']}"
        if StreakReward.query.filter_by(usuario_id=profile.usuario_id, clave=clave).first():
            continue
        db.session.add(StreakReward(usuario_id=profile.usuario_id, clave=clave))
        dar(h["premio"])
        ganados.append({"clave": clave, "titulo": f"Juntaste {h['meta']} XP en {estado['mes']}" if tipo == "xp" else f"Superaste {h['meta']} encargos en {estado['mes']}",
                        "encabezado": f"⭐ {h['meta']} XP este mes" if tipo == "xp" else f"🗓️ {h['meta']} encargos este mes",
                        "premio": reward_text(h["premio"]), "datos": dict(h["premio"]), "cofre": h["cofre"]})
    if not estado.get("antes_de_inicio") and not estado["ganada"] and estado["experiencias"] and all(e["completada"] for e in estado["experiencias"]):
        db.session.add(Medal(usuario_id=profile.usuario_id, clave=estado["clave"]))
        dar(PREMIO_MEDALLA)
        ganados.append({"clave": f"medalla-{estado['clave']}", "titulo": f"¡Ganaste la medalla de {estado['mes']}: {estado['nombre']}!",
                        "encabezado": f"🏅 Medalla de {estado['mes']}", "premio": reward_text(PREMIO_MEDALLA), "datos": dict(PREMIO_MEDALLA),
                        "cofre": "legendario", "medalla": {"clave": estado["clave"], "numero": estado["numero"], "nombre": estado["nombre"], "icono": estado["icono"]}})
    if ganados:
        db.session.flush()
    return ganados


def medallas_de(usuario_id):
    """Medallas ganadas (más nuevas primero), con su diseño."""
    filas = Medal.query.filter_by(usuario_id=usuario_id).order_by(Medal.clave.desc()).all()
    salida = []
    for f in filas:
        anio, mes = (int(x) for x in f.clave.split("-"))
        salida.append({"clave": f.clave, "anio": anio, "mes": MESES[mes - 1], **diseno(mes, anio), "ganada_en": f.creada_en.date().isoformat()})
    return salida


