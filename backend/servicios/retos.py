"""Lógica de retos: arma las preguntas de un nivel y decide si un nivel está desbloqueado."""
import hashlib
import hmac
import random
import secrets

from flask import current_app

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
    elif challenge.tipo == "parejas":
        pares = data.get("pares", [])
        izq = [{"id": i, "t": a} for i, (a, _b) in enumerate(pares)]
        der = [{"id": id_pareja(challenge.id, i), "t": b} for i, (_a, b) in enumerate(pares)]
        random.shuffle(izq)
        random.shuffle(der)
        sal = secrets.token_hex(6)
        # Sellos para que el navegador diga «bien/mal» al unir cada pareja (como Duolingo) sin mandar las parejas
        item.update(izq=izq, der=der, sal=sal, sellos=sorted(fnv1a(f"{sal}|{i}|{id_pareja(challenge.id, i)}") for i in range(len(pares))),
                    tolerancia=tolerancia_parejas(len(pares)))
    elif challenge.tipo == "armar":
        fichas = list(data.get("solucion", [])) + list(data.get("trampas", []))
        random.shuffle(fichas)
        item["fichas"] = fichas
    return item


def id_pareja(challenge_id, i):
    """Id de la columna derecha: el navegador no puede saber cuál va con cuál (el servidor sí puede comprobarlo)."""
    clave = (current_app.config.get("SECRET_KEY") or "codigocamp").encode()
    return hmac.new(clave, f"pareja:{challenge_id}:{i}".encode(), hashlib.sha256).hexdigest()[:10]


def fnv1a(texto):
    """Hash corto (FNV-1a de 32 bits) que el navegador calcula igual, también en http:// (sin crypto.subtle)."""
    h = 0x811C9DC5
    for b in texto.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


def tolerancia_parejas(n):
    """Errores permitidos al unir: ninguno con 3 o 4 parejas, uno con 5 o más (más parejas, más fácil equivocarse)."""
    return 1 if n >= 5 else 0


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


def estados_niveles(user, course):
    """Estado de cada nivel de un curso: hecho, actual, pendiente o bloqueado.

    «actual» es el siguiente DESPUÉS del más avanzado que hiciste (no el primero que falte en todo el curso): si se
    agregan lecciones nuevas en secciones que ya pasaste, no te devuelve atrás. Esos huecos quedan como «pendiente»
    (abiertos, para hacerlos cuando quieras)."""
    completed = {
        item[0] for item in db.session.query(CompletedLevel.nivel_id).join(Level).join(Section).join(Stage).filter(
            CompletedLevel.usuario_id == user.id, Stage.curso_id == course.id,
        ).all()
    }
    niveles = list(all_levels(course))
    ultimo = max((i for i, n in enumerate(niveles) if n.id in completed), default=-1)
    actual = next((n.id for i, n in enumerate(niveles) if i > ultimo and n.id not in completed), None)
    if actual is None:
        actual = next((n.id for n in niveles if n.id not in completed), None)
    estados = {}
    for i, n in enumerate(niveles):
        if n.id in completed:
            estados[n.id] = "hecho"
        elif n.id == actual:
            estados[n.id] = "actual"
        elif i < ultimo:
            estados[n.id] = "pendiente"
        else:
            estados[n.id] = "bloqueado"
    return estados


def allowed_level(user, level):
    course = level.seccion.etapa.course
    return estados_niveles(user, course).get(level.id) in ("hecho", "actual", "pendiente")
