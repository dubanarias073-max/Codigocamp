"""«Saltar aquí» (como en Duolingo): un examen de TODO lo anterior a una sección o etapa. Si lo apruebas, los niveles
anteriores quedan hechos y sigues desde ahí. El examen no gasta vidas, cada pregunta sale una sola vez y el servidor
lleva la cuenta de aciertos (no se puede aprobar desde el navegador)."""
import random
import time

from flask import Blueprint, jsonify, session
from flask_login import current_user, login_required

from models import Challenge, CompletedLevel, RetoAdmin, Section, Stage, db
from servicios.perfil import award_xp, get_profile, progress
from servicios.retos import all_levels, challenge_item, estados_niveles
from utilidades import api_error

bp = Blueprint("salto", __name__)

MAX_PREGUNTAS = 15
MIN_PREGUNTAS = 5
SIN_TRAMPA = ("opcion", "completar", "error", "ordenar", "parejas", "armar")   # los que corrige el servidor
XP_APROBAR = 30
VIGENCIA = 2 * 3600


def tolerancia(n):
    """Errores permitidos: 1 de cada 5 preguntas (3 en un examen de 15)."""
    return max(1, n // 5)


def _objetivo(tipo, oid):
    if tipo == "seccion":
        s = db.session.get(Section, oid)
        return (s, s.etapa.course, f"la sección «{s.titulo}»") if s else (None, None, "")
    if tipo == "etapa":
        e = db.session.get(Stage, oid)
        return (e, e.course, f"la etapa «{e.titulo}»") if e else (None, None, "")
    return None, None, ""


def _niveles_antes(curso, tipo, obj):
    niveles = list(all_levels(curso))
    def dentro(n):
        return n.seccion_id == obj.id if tipo == "seccion" else n.seccion.etapa_id == obj.id
    i = next((k for k, n in enumerate(niveles) if dentro(n)), None)
    return (niveles[:i], niveles[i]) if i is not None else ([], None)


@bp.get("/api/salto/<tipo>/<int:oid>/")
@login_required
def examen(tipo, oid):
    obj, curso, nombre = _objetivo(tipo, oid)
    if not obj:
        return api_error("No encontramos esa parte del curso.", 404)
    antes, primero = _niveles_antes(curso, tipo, obj)
    if primero is None:
        return api_error("Esa parte del curso todavía no tiene niveles.", 404)
    estados = estados_niveles(current_user, curso)
    if estados.get(primero.id) != "bloqueado":
        return api_error("Ya puedes entrar ahí: no necesitas el examen.", 400)
    ocultos = {r.reto_id for r in RetoAdmin.query.filter_by(oculto=True).all()}
    ids_lecciones = [n.id for n in antes if n.tipo == "leccion"]
    pool = [c for c in Challenge.query.filter(Challenge.nivel_id.in_(ids_lecciones)).all() if c.tipo in SIN_TRAMPA and c.id not in ocultos] if ids_lecciones else []
    if len(pool) < MIN_PREGUNTAS:
        return api_error("Todavía no hay suficientes retos antes de esta parte para armar el examen.", 400)
    # Repartidas entre todas las secciones anteriores (no solo las últimas)
    por_seccion = {}
    nivel_seccion = {n.id: n.seccion_id for n in antes}
    for c in pool:
        por_seccion.setdefault(nivel_seccion[c.nivel_id], []).append(c)
    azar = random.Random()
    for lista in por_seccion.values():
        azar.shuffle(lista)
    elegidas = []
    while len(elegidas) < min(MAX_PREGUNTAS, len(pool)):
        for lista in por_seccion.values():
            if lista and len(elegidas) < MAX_PREGUNTAS:
                elegidas.append(lista.pop())
    azar.shuffle(elegidas)
    session["salto"] = {"obj": f"{tipo}:{oid}", "retos": [c.id for c in elegidas], "res": {}, "t": int(time.time())}
    return jsonify(
        nivel={"id": 0, "titulo": f"Examen para saltar a {nombre}", "xp": XP_APROBAR, "seccion": nombre, "etapa": ""},
        curso={"slug": curso.slug, "nombre": curso.nombre, "color": curso.color},
        retos=[challenge_item(c) for c in elegidas], vidas=get_profile(current_user).vidas,
        examen={"total": len(elegidas), "tolerancia": tolerancia(len(elegidas)), "objetivo": nombre, "saltados": len(antes)},
    )


def en_examen(challenge_id):
    """¿Esta respuesta es del examen de salto activo? (entonces no gasta vidas ni exige nivel desbloqueado)."""
    s = session.get("salto")
    return bool(s) and time.time() - s.get("t", 0) < VIGENCIA and challenge_id in s.get("retos", [])


def anotar(challenge_id, correcto):
    s = session.get("salto")
    if s and str(challenge_id) not in s["res"]:   # cuenta el primer intento
        s["res"][str(challenge_id)] = bool(correcto)
        session["salto"] = s
        session.modified = True


@bp.post("/api/salto/terminar/")
@login_required
def terminar():
    s = session.get("salto")
    if not s or time.time() - s.get("t", 0) > VIGENCIA:
        return api_error("El examen ya no está activo. Empiézalo otra vez.", 400)
    total = len(s["retos"])
    errores = sum(1 for v in s["res"].values() if not v)
    respondidas = len(s["res"])
    tol = tolerancia(total)
    aprobado = respondidas >= total and errores <= tol
    session.pop("salto", None)
    if not aprobado:
        return jsonify(aprobado=False, errores=errores, tolerancia=tol, respondidas=respondidas, total=total)
    tipo, oid = s["obj"].split(":")
    obj, curso, nombre = _objetivo(tipo, int(oid))
    antes, _ = _niveles_antes(curso, tipo, obj)
    hechos = {c.nivel_id for c in CompletedLevel.query.filter(CompletedLevel.usuario_id == current_user.id,
                                                               CompletedLevel.nivel_id.in_([n.id for n in antes])).all()}
    nuevos = 0
    for n in antes:
        if n.id not in hechos:
            db.session.add(CompletedLevel(usuario_id=current_user.id, nivel_id=n.id, estrellas=1))
            nuevos += 1
    profile = get_profile(current_user)
    premios = award_xp(profile, XP_APROBAR, levels=1, perfect=errores == 0)
    db.session.commit()
    return jsonify(aprobado=True, errores=errores, tolerancia=tol, total=total, desbloqueados=nuevos, objetivo=nombre,
                   xp_ganado=XP_APROBAR, curso=curso.slug, desafios_completados=premios, **progress(current_user))
