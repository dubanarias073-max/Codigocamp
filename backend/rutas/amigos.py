"""Amigos: buscar usuarios, enviar, aceptar y quitar solicitudes."""
import hashlib

from rutas.cosmeticos import equipados_de, foto_url
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from models import Friendship, Message, Profile, User, db
from servicios.amistades import my_friendships
from servicios.perfil import get_profile
from utilidades import api_error, json_body, too_many

bp = Blueprint("amigos", __name__)


@bp.get("/api/amigos/")
@login_required
def amigos():
    profile = get_profile(current_user)
    friendships = my_friendships(current_user.id).all()
    friends, received, sent = [], [], []
    for friendship in friendships:
        other = friendship.a_usuario if friendship.de_usuario_id == current_user.id else friendship.de_usuario
        item = {"id": friendship.id, "nombre": other.nombre, "alias": other.profile.alias if other.profile else "",
                "avatar": "", "foto": foto_url(other.id), "marco": equipados_de(other.id)["marco"]}
        if friendship.estado == "aceptada":
            from rutas.chat import borrado_hasta
            desde = borrado_hasta(current_user.id, friendship.id)   # lo que borré de mi vista no cuenta
            last = Message.query.filter(Message.amistad_id == friendship.id, Message.id > desde).order_by(Message.id.desc()).first()
            unread = Message.query.filter(
                Message.amistad_id == friendship.id, Message.id > desde, Message.leido.is_(False),
                Message.autor_id != current_user.id,
            ).count()
            op = other.profile
            from models import Medal
            item.update(nivel=op.nivel if op else 1, racha=op.racha_actual if op else 0,
                        medallas=Medal.query.filter_by(usuario_id=other.id).count())
            item.update(no_leidos=unread, ultimo=("🚫 Mensaje eliminado" if last.borrado_en else last.texto[:60]) if last else "", orden=last.id if last else 0)
            friends.append(item)
        elif friendship.a_usuario_id == current_user.id:
            received.append(item)
        else:
            sent.append(item)
    friends.sort(key=lambda item: -item["orden"])
    return jsonify(
        yo={"nombre": current_user.nombre, "alias": profile.alias, "codigo": profile.codigo, "avatar": "", "foto": foto_url(current_user.id), "marco": equipados_de(current_user.id)["marco"]},
        amigos=friends, recibidas=received, enviadas=sent,
    )


@bp.get("/api/usuarios/buscar/")
@login_required
def usuarios_buscar():
    texto = str(request.args.get("q", "")).strip().lstrip("@")
    if not 2 <= len(texto) <= 30:
        return jsonify(resultados=[])
    if too_many(f"buscar:{current_user.id}", 60, 600):
        return api_error("Has buscado muchas veces. Espera unos minutos.", 429)
    limpio = texto.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    filas = (Profile.query.join(User, User.id == Profile.usuario_id)
             .filter(User.activo.is_(True), Profile.usuario_id != current_user.id,
                     or_(Profile.alias.like(limpio + "%", escape="\\"), func.lower(User.nombre).like("%" + limpio + "%", escape="\\")))
             .order_by(Profile.alias).limit(8).all())
    relacion = {}
    for f in my_friendships(current_user.id).all():
        otro = f.a_usuario_id if f.de_usuario_id == current_user.id else f.de_usuario_id
        relacion[otro] = "amigo" if f.estado == "aceptada" else ("enviada" if f.de_usuario_id == current_user.id else "recibida")
    return jsonify(resultados=[{
        "nombre": p.user.nombre, "alias": p.alias, "avatar": "", "foto": foto_url(p.usuario_id), "relacion": relacion.get(p.usuario_id),
    } for p in filas if p.alias])


@bp.post("/api/amigos/contactos/")
@login_required
def amigos_contactos():
    """Quién de tus contactos ya está en CódigoCamp. El teléfono manda solo el sha256 de cada correo (en minúsculas):
    la agenda nunca llega al servidor y no se guarda nada. Solo aparecen quienes dejan que los encuentren por su correo."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    hashes = data.get("hashes")
    if not isinstance(hashes, list):
        return api_error("Faltan los contactos.")
    pedidos = {str(h).lower() for h in hashes[:1000] if isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h.lower())}
    if not pedidos:
        return jsonify(resultados=[])
    if too_many(f"contactos:{current_user.id}", 10, 3600):
        return api_error("Ya buscaste tus contactos varias veces. Inténtalo en una hora.", 429)
    relacion = {}
    for f in my_friendships(current_user.id).all():
        otro = f.a_usuario_id if f.de_usuario_id == current_user.id else f.de_usuario_id
        relacion[otro] = "amigo" if f.estado == "aceptada" else ("enviada" if f.de_usuario_id == current_user.id else "recibida")
    resultados = []
    filas = (db.session.query(User, Profile).join(Profile, Profile.usuario_id == User.id)
             .filter(User.activo.is_(True), User.id != current_user.id, Profile.buscable_correo.is_(True), Profile.alias.isnot(None)))
    for user, p in filas.yield_per(500):
        h = hashlib.sha256(user.email.strip().lower().encode()).hexdigest()
        if h in pedidos:
            resultados.append({"hash": h, "nombre": user.nombre, "alias": p.alias, "foto": foto_url(user.id), "relacion": relacion.get(user.id)})
    return jsonify(resultados=resultados[:200])


@bp.post("/api/amigos/agregar/")
@login_required
def amigo_agregar():
    data = json_body()
    if isinstance(data, tuple):
        return data
    text = str(data.get("usuario", "")).strip().lstrip("@")
    if not text or len(text) > 30:
        return api_error("Escribe un ID o un nombre de usuario.")
    if too_many(f"amigos:{current_user.id}", 20, 3600):
        return api_error("Has buscado muchas veces. Inténtalo más tarde.", 429)
    other_profile = Profile.query.filter(
        or_(Profile.alias == text.lower(), Profile.codigo == text.upper())
    ).first()
    if not other_profile or not other_profile.user.activo:
        return api_error("No encontramos a nadie con ese ID o nombre de usuario.", 404)
    if other_profile.usuario_id == current_user.id:
        return api_error("Ese eres tú.")
    previous = my_friendships(current_user.id).filter(
        or_(Friendship.de_usuario_id == other_profile.usuario_id, Friendship.a_usuario_id == other_profile.usuario_id)
    ).first()
    if previous:
        if previous.estado == "aceptada":
            return api_error("Ya son amigos.", 409)
        if previous.de_usuario_id == current_user.id:
            return api_error("Ya le enviaste una solicitud.", 409)
        previous.estado = "aceptada"
        db.session.commit()
        return jsonify(estado="aceptada", nombre=other_profile.user.nombre)
    db.session.add(Friendship(de_usuario_id=current_user.id, a_usuario_id=other_profile.usuario_id))
    db.session.commit()
    return jsonify(estado="pendiente", nombre=other_profile.user.nombre), 201


@bp.post("/api/amigos/<int:friendship_id>/responder/")
@login_required
def amigo_responder(friendship_id):
    friendship = Friendship.query.filter_by(
        id=friendship_id, a_usuario_id=current_user.id, estado="pendiente",
    ).first()
    if not friendship:
        return api_error("Esa solicitud no existe.", 404)
    data = json_body()
    if isinstance(data, tuple):
        return data
    if data.get("aceptar"):
        friendship.estado = "aceptada"
    else:
        db.session.delete(friendship)
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/api/amigos/<int:friendship_id>/quitar/")
@login_required
def amigo_quitar(friendship_id):
    friendship = my_friendships(current_user.id).filter_by(id=friendship_id).first()
    if not friendship:
        return api_error("Esa amistad no existe.", 404)
    db.session.delete(friendship)
    db.session.commit()
    return jsonify(ok=True)


@bp.get("/api/amigos/<int:friendship_id>/perfil/")
@login_required
def amigo_perfil(friendship_id):
    """Perfil de un amigo: lo que se ve al tocar su nombre en el chat. Solo entre amigos (solicitud aceptada)."""
    from datetime import date, timedelta

    from cosmeticos import POR_CLAVE
    from models import CompletedLevel, Course, DailyActivity, LessonDone, Level, OwnedCosmetic, Section, Stage

    amistad = db.session.get(Friendship, friendship_id)
    if not amistad or amistad.estado != "aceptada" or current_user.id not in (amistad.de_usuario_id, amistad.a_usuario_id):
        return api_error("No encontramos a ese amigo.", 404)
    otro = amistad.a_usuario if amistad.de_usuario_id == current_user.id else amistad.de_usuario
    p = get_profile(otro)

    # Retos: niveles completados y estrellas por curso
    filas = (db.session.query(Course.id, Course.nombre, Course.sigla, Course.color, Course.slug,
                              func.count(CompletedLevel.id), func.coalesce(func.sum(CompletedLevel.estrellas), 0))
             .join(Stage, Stage.curso_id == Course.id).join(Section, Section.etapa_id == Stage.id)
             .join(Level, Level.seccion_id == Section.id).join(CompletedLevel, CompletedLevel.nivel_id == Level.id)
             .filter(CompletedLevel.usuario_id == otro.id).group_by(Course.id).all())
    ids = [f[0] for f in filas]
    totales = dict(db.session.query(Course.id, func.count(Level.id)).join(Stage, Stage.curso_id == Course.id)
                   .join(Section, Section.etapa_id == Stage.id).join(Level, Level.seccion_id == Section.id)
                   .filter(Course.id.in_(ids)).group_by(Course.id).all()) if ids else {}
    cursos = [{"nombre": n, "sigla": s, "color": c, "slug": sl, "niveles": cnt, "total": totales.get(i, 0), "estrellas": int(e)}
              for i, n, s, c, sl, cnt, e in filas]
    cursos.sort(key=lambda x: -x["niveles"])
    # Aprende: lecciones hechas por curso
    lecc = (db.session.query(Course.nombre, Course.color, func.count(LessonDone.id)).join(LessonDone, LessonDone.curso_id == Course.id)
            .filter(LessonDone.usuario_id == otro.id).group_by(Course.id).order_by(func.count(LessonDone.id).desc()).all())
    # Actividad de los últimos 7 días
    hoy = date.today()
    dias = {a.fecha: a.xp for a in DailyActivity.query.filter(DailyActivity.usuario_id == otro.id,
                                                               DailyActivity.fecha >= hoy - timedelta(days=6)).all()}
    semana = [{"dia": (hoy - timedelta(days=6 - k)).isoformat(), "xp": dias.get(hoy - timedelta(days=6 - k), 0)} for k in range(7)]
    # Cosméticos: los que tiene puestos y cuántos tiene
    equipados = {t: ({"clave": c, "nombre": POR_CLAVE[c]["nombre"], "rareza": POR_CLAVE[c]["rareza"]} if c in POR_CLAVE else None)
                 for t, c in equipados_de(otro.id).items()}
    propios = OwnedCosmetic.query.filter_by(usuario_id=otro.id).count()

    return jsonify(
        nombre=otro.nombre, alias=p.alias, codigo=p.codigo, foto=foto_url(otro.id), avatar=p.avatar or "",
        nivel=p.nivel, xp_total=p.xp_total, xp_nivel=p.xp_total % 100,
        racha_actual=p.racha_actual, racha_maxima=p.racha_maxima,
        activo_hoy=p.ultima_actividad == hoy,
        rol=p.rol, intereses=p.intereses or [],
        curso_actual=({"nombre": p.curso_actual.nombre, "sigla": p.curso_actual.sigla, "color": p.curso_actual.color}
                      if p.curso_actual else None),
        miembro_desde=p.creado_en.date().isoformat() if p.creado_en else None,
        amigos_desde=amistad.creada_en.date().isoformat() if amistad.creada_en else None,
        niveles_completados=sum(c["niveles"] for c in cursos), estrellas=sum(c["estrellas"] for c in cursos),
        cursos=cursos[:12], lecciones=[{"nombre": n, "color": c, "hechas": k} for n, c, k in lecc[:12]],
        lecciones_total=sum(k for _, _, k in lecc), semana=semana,
        equipados=equipados, cosmeticos_total=propios,
        **_logros_de(otro.id),
    )


def _logros_de(usuario_id):
    """Medallas del mes, cofres de logro abiertos y encargos superados (se ven en el perfil del chat)."""
    from cosmeticos import COFRE_POR_CLAVE, COFRES
    from models import DailyChallenge, OpenedChest
    from servicios.medallas import medallas_de
    abiertos = [c.clave for c in OpenedChest.query.filter_by(usuario_id=usuario_id).all() if c.clave in COFRE_POR_CLAVE]
    orden = {"legendario": 0, "diamante": 1, "oro": 2, "plata": 3, "madera": 4}
    mejores = sorted((COFRE_POR_CLAVE[k] for k in abiertos), key=lambda c: orden.get(c["cofre"], 9))[:8]
    from servicios.medallas import medallas_desde
    desde = medallas_desde()
    return {"medallas": medallas_de(usuario_id), "medallas_desde": {"anio": desde.year, "mes": desde.month}, "logros_abiertos": len(abiertos), "logros_total": len(COFRES),
            "logros": [{"nombre": c["nombre"], "cofre": c["cofre"], "texto": c["texto"]} for c in mejores],
            "encargos_total": DailyChallenge.query.filter_by(usuario_id=usuario_id).count()}
