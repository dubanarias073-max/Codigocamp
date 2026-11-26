"""Panel de administrador (solo para ADMIN_EMAIL con la clave ADMIN_CLAVE; ver servicios/admin.py).

Todo lo de /api/admin/* responde 404 a cualquier otra persona."""
import os
import re
from datetime import timedelta

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func, or_, select

from models import (ArticuloExtra, Bloqueo, Incidente, MedallaEspecial, MedallaOtorgada, Profile, Purchase, StoreItem, User,
                    UserSession, db, utcnow)
from seguridad import cerrar_sesiones
from servicios import admin as adm
from servicios.moderacion import ETIQUETAS, PUNTOS, RECOMENDACION, correo_bloqueo, enviar_aviso, impacto_de
from utilidades import api_error, client_ip, json_body, too_many



def _sin_tildes(texto):
    """«Aro galáctico» → «aro galactico» (para claves internas)."""
    import unicodedata
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


bp = Blueprint("admin", __name__)
requiere_admin = adm.requiere_admin


def _iso(d):
    return d.isoformat() if d else None


# ------------------------------------------------------------------------------------------------ entrar ----
@bp.get("/api/admin/estado")
@login_required
def estado():
    if not adm.es_admin(current_user):
        return api_error("No encontrado.", 404)
    return jsonify(activo=adm.modo_activo(), configurado=bool(adm.clave_admin()))


@bp.post("/api/admin/entrar")
@login_required
def entrar():
    if not adm.es_admin(current_user):
        return api_error("No encontrado.", 404)
    if not adm.clave_admin():
        return api_error("Falta configurar ADMIN_CLAVE en backend/.env (y reiniciar Flask) para usar el panel.", 409)
    if too_many(f"admin-entrar:{current_user.id}:{client_ip()}", 5, 900):
        return api_error("Demasiados intentos. Espera 15 minutos.", 429)
    data = json_body()
    if isinstance(data, tuple):
        return data
    if not adm.clave_correcta(data.get("clave")):
        return api_error("Clave de administrador incorrecta.", 403)
    adm.encender()
    return jsonify(ok=True)


@bp.post("/api/admin/salir")
@login_required
def salir():
    adm.apagar()
    return jsonify(ok=True)


# ---------------------------------------------------------------------------------------------- antivirus ----
@bp.get("/api/admin/antivirus")
@requiere_admin
def antivirus_estado():
    from servicios import heuristicas
    from servicios.antivirus import estado_clamav
    desde = utcnow() - timedelta(days=30)
    bloqueos = Incidente.query.filter(Incidente.creado_en >= desde).count()
    return jsonify(clamav=estado_clamav(), huellas=len(heuristicas.firmas()), bloqueos_30d=bloqueos,
                   activo=os.environ.get("ANTIVIRUS", "1") != "0")


@bp.post("/api/admin/antivirus/probar")
@requiere_admin
def antivirus_probar():
    from servicios.antivirus import autoprueba
    r = autoprueba()
    peligrosas = [x for x in r if x["peligrosa"]]
    normales = [x for x in r if not x["peligrosa"]]
    return jsonify(resultados=r, detectadas=sum(x["detectado"] for x in peligrosas), total_peligrosas=len(peligrosas),
                   falsos_positivos=sum(x["detectado"] for x in normales), total_normales=len(normales))


# ------------------------------------------------------------------------------------------------ resumen ----
@bp.get("/api/admin/resumen")
@requiere_admin
def resumen():
    hoy = utcnow() - timedelta(days=1)
    por_gravedad = dict(db.session.query(Incidente.gravedad, func.count()).filter(Incidente.estado == "pendiente").group_by(Incidente.gravedad).all())
    from servicios.antivirus import estado_antivirus
    from servicios.correo import _config, smtp_configurado
    cfg = _config(current_app)
    return jsonify(
        correo={"configurado": smtp_configurado(), "cuenta": cfg["usuario"], "servidor": cfg["servidor"]},
        antivirus=estado_antivirus(),
        correos_fallidos=Incidente.query.filter(Incidente.correo_estado.in_(("error", "sin_smtp"))).count(),
        usuarios=User.query.count(),
        activos_24h=db.session.query(func.count(func.distinct(UserSession.usuario_id))).filter(UserSession.ultima >= hoy).scalar() or 0,
        nuevos_7d=User.query.filter(User.creado_en >= utcnow() - timedelta(days=7)).count(),
        bloqueados=Bloqueo.query.count(),
        pendientes=sum(por_gravedad.values()),
        por_gravedad={g: por_gravedad.get(g, 0) for g in ("critica", "alta", "media", "baja")},
        incidentes=[_incidente(i) for i in Incidente.query.filter_by(estado="pendiente").order_by(Incidente.id.desc()).limit(8)],
    )


# ------------------------------------------------------------------------------------------------ incidentes ----
def _incidente(i, usuario=None):
    u = usuario or db.session.get(User, i.usuario_id)
    return {"id": i.id, "tipo": i.tipo, "gravedad": i.gravedad, "gravedad_txt": ETIQUETAS.get(i.gravedad, i.gravedad), "puntos": i.puntos,
            "motivo": i.motivo, "evidencia": i.evidencia, "origen": i.origen, "ip": i.ip, "estado": i.estado,
            "correo_enviado": i.correo_enviado, "correo_estado": i.correo_estado, "correo_detalle": i.correo_detalle,
            "explicacion": i.explicacion, "creado": _iso(i.creado_en), "recomendacion": RECOMENDACION.get(i.gravedad, ""),
            "usuario": {"id": u.id, "nombre": u.nombre, "email": u.email, "activo": u.activo, "impacto": impacto_de(u.id)} if u else None}


@bp.get("/api/admin/incidentes")
@requiere_admin
def incidentes():
    q = Incidente.query
    est = request.args.get("estado", "pendiente")
    if est != "todos":
        q = q.filter(Incidente.estado == est)
    if request.args.get("usuario"):
        q = q.filter(Incidente.usuario_id == int(request.args["usuario"]))
    orden = func.field(Incidente.gravedad, "critica", "alta", "media", "baja") if db.engine.dialect.name in ("mysql", "mariadb") else Incidente.puntos.desc()
    filas = q.order_by(orden, Incidente.id.desc()).limit(300).all()
    return jsonify(incidentes=[_incidente(i) for i in filas])


@bp.post("/api/admin/incidentes/<int:iid>")
@requiere_admin
def decidir(iid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    inc = db.session.get(Incidente, iid)
    if not inc:
        return api_error("Ese incidente no existe.", 404)
    decision = str(data.get("decision", ""))
    u = db.session.get(User, inc.usuario_id)
    if decision == "ignorar":
        inc.estado = "ignorado"
    elif decision == "advertir":
        inc.estado = "advertido"
        enviar_aviso(u, inc, mensaje=str(data.get("mensaje", "")).strip()[:500] or None)
    elif decision == "reenviar":
        enviar_aviso(u, inc)
        db.session.commit()
        return jsonify(ok=True, incidente=_incidente(inc, u))
    elif decision == "bloquear":
        if adm.es_admin(u):
            return api_error("No puedes bloquear tu propia cuenta de administrador.")
        inc.estado = "bloqueado"
        _bloquear(u, str(data.get("motivo", "")).strip()[:300] or inc.motivo, inc)
    else:
        return api_error("Decisión no válida.")
    inc.revisado_en = utcnow()
    db.session.commit()
    return jsonify(ok=True, incidente=_incidente(inc, u))


# ------------------------------------------------------------------------------------------------ usuarios ----
def _fila_usuario(u, p):
    return {"id": u.id, "nombre": u.nombre, "email": u.email, "activo": u.activo, "google": bool(u.google_id), "creado": _iso(u.creado_en),
            "alias": p.alias if p else None, "nivel": p.nivel if p else 1, "xp_total": p.xp_total if p else 0,
            "diamante": p.diamante if p else 0, "racha": p.racha_actual if p else 0,
            "ultima_actividad": _iso(p.ultima_actividad) if p else None, "impacto": impacto_de(u.id),
            "bloqueado": db.session.get(Bloqueo, u.id) is not None, "admin": adm.es_admin(u)}


@bp.get("/api/admin/usuarios")
@requiere_admin
def usuarios():
    texto = str(request.args.get("q", "")).strip()[:80]
    pagina = max(1, int(request.args.get("pagina", 1) or 1))
    q = db.session.query(User, Profile).outerjoin(Profile, Profile.usuario_id == User.id)
    if texto:
        like = f"%{texto}%"
        q = q.filter(or_(User.nombre.ilike(like), User.email.ilike(like), Profile.alias.ilike(like)))
    if request.args.get("filtro") == "bloqueados":
        q = q.filter(User.activo.is_(False))
    total = q.count()
    filas = q.order_by(User.id.desc()).offset((pagina - 1) * 50).limit(50).all()
    return jsonify(total=total, pagina=pagina, usuarios=[_fila_usuario(u, p) for u, p in filas])


def _columnas(obj, ocultar=()):
    return {c.name: (_iso(v) if hasattr(v, "isoformat") else v) for c in obj.__table__.columns
            if c.name not in ocultar for v in [getattr(obj, c.key)]}


@bp.get("/api/admin/usuarios/<int:uid>")
@requiere_admin
def usuario(uid):
    from models import Medal, OwnedCosmetic
    u = db.session.get(User, uid)
    if not u:
        return api_error("Esa cuenta no existe.", 404)
    p = Profile.query.filter_by(usuario_id=uid).first()
    b = db.session.get(Bloqueo, uid)
    return jsonify(
        usuario=_fila_usuario(u, p),
        cuenta=_columnas(u, ocultar={"password_hash", "google_id"}),
        perfil=_columnas(p) if p else None,
        bloqueo={"motivo": b.motivo, "desde": _iso(b.creado_en)} if b else None,
        sesiones=[{"dispositivo": s.dispositivo, "ip": s.ip, "metodo": s.metodo, "creada": _iso(s.creada), "ultima": _iso(s.ultima), "revocada": s.revocada}
                  for s in UserSession.query.filter_by(usuario_id=uid).order_by(UserSession.id.desc()).limit(30)],
        compras=[{"articulo": c.articulo.nombre if c.articulo else c.articulo_id, "precio": c.precio, "fecha": _iso(c.creada_en)}
                 for c in Purchase.query.filter_by(usuario_id=uid).order_by(Purchase.id.desc()).limit(50)],
        cosmeticos=[c.clave for c in OwnedCosmetic.query.filter_by(usuario_id=uid)],
        medallas_mes=[m.clave for m in Medal.query.filter_by(usuario_id=uid).order_by(Medal.clave.desc())],
        medallas_especiales=[{"id": o.medalla_id, "nombre": o.medalla.nombre, "icono": o.medalla.icono, "motivo": o.motivo, "fecha": _iso(o.creada_en)}
                             for o in MedallaOtorgada.query.filter_by(usuario_id=uid)],
        incidentes=[_incidente(i, u) for i in Incidente.query.filter_by(usuario_id=uid).order_by(Incidente.id.desc()).limit(100)],
    )


def _bloquear(u, motivo, incidente=None):
    u.activo = False
    b = db.session.get(Bloqueo, u.id)
    if b:
        b.motivo = motivo[:300]
    else:
        db.session.add(Bloqueo(usuario_id=u.id, motivo=motivo[:300]))
    db.session.flush()
    cerrar_sesiones(u.id)     # lo saca de todos sus dispositivos al instante (hace commit)
    correo_bloqueo(u, motivo, incidente)


EDITABLES = {"diamante": (0, 10_000_000), "xp_total": (0, 100_000_000), "vidas": (0, 99), "salvarrachas": (0, 10),
             "racha_actual": (0, 32000), "racha_maxima": (0, 32000)}


@bp.patch("/api/admin/usuarios/<int:uid>")
@requiere_admin
def editar_usuario(uid):
    """Edita la cuenta: nombre, alias, diamantes, XP, vidas, salvarrachas y rachas. Si «avisar», le llega un correo
    contando qué cambió («🎁 Recibiste 500 diamantes»…)."""
    from servicios.avisos_admin import correo_cambios, lineas_cambios
    data = json_body()
    if isinstance(data, tuple):
        return data
    u = db.session.get(User, uid)
    if not u:
        return api_error("Esa cuenta no existe.", 404)
    p = Profile.query.filter_by(usuario_id=uid).first()
    antes = {"nombre": u.nombre, "alias": p.alias if p else None, **({k: getattr(p, k) for k in EDITABLES} if p else {})}
    if "nombre" in data:
        nombre = " ".join(str(data["nombre"]).split())[:80]
        if len(nombre) < 2:
            return api_error("El nombre debe tener al menos 2 letras.")
        u.nombre = nombre
    if p is not None:
        if "alias" in data:
            alias = str(data["alias"] or "").strip().lower()
            if alias and not re.fullmatch(r"[a-z0-9_.]{3,20}", alias):
                return api_error("El alias debe tener de 3 a 20 letras, números, punto o guion bajo.")
            if alias and Profile.query.filter(Profile.alias == alias, Profile.usuario_id != uid).first():
                return api_error("Ese alias ya lo usa otra persona.")
            p.alias = alias or None
        for campo, (minimo, maximo) in EDITABLES.items():
            if campo not in data or data[campo] in ("", None):
                continue
            try:
                valor = int(data[campo])
            except (TypeError, ValueError):
                return api_error(f"Valor no válido para {campo}.")
            valor = max(minimo, min(maximo, valor))
            if campo == "xp_total":   # el XP «gastable» acompaña al total
                p.xp = max(0, p.xp + (valor - p.xp_total))
            setattr(p, campo, valor)
        if p.racha_maxima < p.racha_actual:
            p.racha_maxima = p.racha_actual
    db.session.commit()
    despues = {"nombre": u.nombre, "alias": p.alias if p else None, **({k: getattr(p, k) for k in EDITABLES} if p else {})}
    lineas, regalo = lineas_cambios(antes, despues)
    correo = bool(data.get("avisar", True)) and correo_cambios(u, lineas, nota=str(data.get("nota", "")).strip()[:500], regalo=regalo)
    return jsonify(ok=True, usuario=_fila_usuario(u, p), cambios=len(lineas), correo=bool(correo))


@bp.post("/api/admin/usuarios/<int:uid>/<accion>")
@requiere_admin
def accion_usuario(uid, accion):
    from servicios.avisos_admin import correo_cambios
    data = json_body() if request.data else {}
    if isinstance(data, tuple):
        return data
    u = db.session.get(User, uid)
    if not u:
        return api_error("Esa cuenta no existe.", 404)
    avisar = bool(data.get("avisar", True))
    nota = str(data.get("nota", "")).strip()[:500]
    if accion == "bloquear":
        if adm.es_admin(u):
            return api_error("No puedes bloquear tu propia cuenta de administrador.")
        _bloquear(u, str(data.get("motivo", "")).strip()[:300])
    elif accion == "desbloquear":
        u.activo = True
        Bloqueo.query.filter_by(usuario_id=uid).delete()
        Incidente.query.filter_by(usuario_id=uid, estado="bloqueado").update({Incidente.estado: "advertido"})
        db.session.commit()
        if avisar:
            correo_cambios(u, ["✅ <b>Tu cuenta fue desbloqueada.</b> Ya puedes volver a entrar a CódigoCamp."], nota=nota, asunto="✅ Tu cuenta de CódigoCamp fue desbloqueada")
    elif accion == "advertir":
        mensaje = str(data.get("mensaje", "")).strip()[:500]
        if not mensaje:
            return api_error("Escribe el mensaje de la advertencia.")
        gravedad = data.get("gravedad") if data.get("gravedad") in ETIQUETAS else "media"
        inc = Incidente(usuario_id=uid, tipo="manual", gravedad=gravedad, puntos=PUNTOS[gravedad], motivo=mensaje[:300],
                        explicacion="Advertencia escrita por el administrador.", origen="advertencia del administrador",
                        estado="advertido", revisado_en=utcnow())
        db.session.add(inc)
        db.session.flush()
        enviar_aviso(u, inc)
    elif accion == "limpiar-faltas":
        n = Incidente.query.filter_by(usuario_id=uid).delete()
        db.session.commit()
        if avisar and n:
            correo_cambios(u, [f"✅ <b>Se retiraron tus faltas</b> ({n}). Tu historial de seguridad quedó limpio."], nota=nota,
                           asunto="✅ Se retiraron tus faltas en CódigoCamp")
        return jsonify(ok=True, borradas=n)
    elif accion == "medalla":
        m = db.session.get(MedallaEspecial, int(data.get("medalla_id") or 0))
        if not m:
            return api_error("Esa medalla no existe.", 404)
        if MedallaOtorgada.query.filter_by(usuario_id=uid, medalla_id=m.id).first():
            return api_error("Esa persona ya tiene esa medalla.")
        db.session.add(MedallaOtorgada(usuario_id=uid, medalla_id=m.id, motivo=str(data.get("motivo", "")).strip()[:160]))
        db.session.commit()
        if avisar:
            import html as _h
            correo_cambios(u, [f"🏅 <b>Recibiste la medalla «{_h.escape(m.nombre)}»</b> {_h.escape(m.icono)}. Ya aparece en tu perfil."]
                           + ([f"Motivo: {_h.escape(str(data.get('motivo')))}"] if data.get("motivo") else []), nota=nota, regalo=True,
                           asunto=f"🏅 ¡Recibiste la medalla {m.nombre}!")
    elif accion == "quitar-medalla":
        MedallaOtorgada.query.filter_by(usuario_id=uid, medalla_id=int(data.get("medalla_id") or 0)).delete()
    elif accion == "regalar":
        from cosmeticos import POR_CLAVE
        from models import OwnedCosmetic
        from servicios.catalogo_admin import refrescar
        refrescar(forzar=True)
        clave = str(data.get("clave", ""))
        info = POR_CLAVE.get(clave)
        if not info:
            return api_error("Ese cosmético no existe.", 404)
        if OwnedCosmetic.query.filter_by(usuario_id=uid, clave=clave).first():
            return api_error("Esa persona ya tiene ese cosmético.")
        db.session.add(OwnedCosmetic(usuario_id=uid, clave=clave))
        db.session.commit()
        if avisar:
            import html as _h
            correo_cambios(u, [f"🎁 <b>Te regalaron «{_h.escape(info['nombre'])}»</b> ({_h.escape(info['tipo'])}). Póntelo desde la Tienda → «Míos»."],
                           nota=nota, regalo=True, asunto=f"🎁 ¡Te regalaron {info['nombre']} en CódigoCamp!")
    elif accion == "quitar-cosmetico":
        from models import EquippedCosmetics, OwnedCosmetic
        clave = str(data.get("clave", ""))
        OwnedCosmetic.query.filter_by(usuario_id=uid, clave=clave).delete()
        item = StoreItem.query.filter_by(clave=clave).first()
        if item:   # la compra tampoco cuenta: deja de salir como «tuyo» y puede volver a comprarlo
            Purchase.query.filter_by(usuario_id=uid, articulo_id=item.id).delete()
        eq = db.session.get(EquippedCosmetics, uid)
        if eq:
            for tipo in ("fondo", "cursor", "tema", "marco", "efecto", "dedo", "codi", "teclado"):
                if getattr(eq, tipo, None) == clave:
                    setattr(eq, tipo, None)
    else:
        return api_error("Acción no válida.", 404)
    db.session.commit()
    return jsonify(ok=True)


@bp.delete("/api/admin/incidentes/<int:iid>")
@requiere_admin
def borrar_incidente(iid):
    """Quita una falta (ya no cuenta en el impacto de la persona)."""
    n = Incidente.query.filter_by(id=iid).delete()
    db.session.commit()
    return jsonify(ok=bool(n))


# ------------------------------------------------------------------------------------------------ base de datos ----
# Se ven todas las tablas. Se ocultan secretos (contraseñas cifradas, tokens) y el contenido privado de chats y de la IA.
OCULTAS = {"password_hash", "token_hash", "codigo_hash", "espera_hash", "google_id", "gemini_uri"}
PRIVADAS = {("mensajes", "texto"), ("mensajes_ia", "texto"), ("espacios_trabajo", "archivos"), ("espacios_trabajo", "git"), ("espacios_trabajo", "live_clave")}


def _tablas():
    return {t.name: t for t in db.metadata.sorted_tables}


@bp.get("/api/admin/tablas")
@requiere_admin
def tablas():
    salida = []
    for nombre, t in sorted(_tablas().items()):
        try:
            n = db.session.execute(select(func.count()).select_from(t)).scalar()
        except Exception:  # noqa: BLE001 - una tabla que aún no existe en esta base
            db.session.rollback()
            n = None
        salida.append({"nombre": nombre, "filas": n})
    return jsonify(tablas=salida)


@bp.get("/api/admin/tablas/<nombre>")
@requiere_admin
def tabla(nombre):
    t = _tablas().get(nombre)
    if t is None:
        return api_error("Esa tabla no existe.", 404)
    pagina = max(1, int(request.args.get("pagina", 1) or 1))
    por = 50
    q = select(t)
    texto = str(request.args.get("q", "")).strip()[:80]
    if texto:
        textuales = _textuales(t, nombre)
        if textuales:
            q = q.where(or_(*[c.ilike(f"%{texto}%") for c in textuales]))
    pk = list(t.primary_key.columns)
    if pk:
        q = q.order_by(pk[0].desc())
    total = db.session.execute(select(func.count()).select_from(q.subquery())).scalar()
    filas = db.session.execute(q.offset((pagina - 1) * por).limit(por)).mappings().all()
    cols = [c.name for c in t.columns]

    def valor(col, v):
        if col in OCULTAS:
            return "••• oculto"
        if (nombre, col) in PRIVADAS:
            return "••• privado"
        if hasattr(v, "isoformat"):
            return v.isoformat()
        if isinstance(v, (dict, list)):
            v = str(v)
        if isinstance(v, str) and len(v) > 200:
            return v[:200] + "…"
        return v
    return jsonify(columnas=cols, total=total, pagina=pagina, por_pagina=por,
                   filas=[{c: valor(c, f[c]) for c in cols} for f in filas])


def _python_type_str(c):
    try:
        return c.type.python_type is str
    except NotImplementedError:
        return False


def _textuales(t, nombre):
    return [c for c in t.columns if c.name not in OCULTAS and (nombre, c.name) not in PRIVADAS and _python_type_str(c)]


# ------------------------------------------------------------------------------------------------ tienda ----
def _origen(clave):
    if clave.startswith("x_"):
        return "panel"           # artículo con premios creado en el panel
    if clave.startswith("a_"):
        return "diseno"          # cosmético diseñado en el panel
    return "fabrica"             # viene del código (constantes.py / cosmeticos.py)


def _articulo(i):
    from constantes import RAREZA
    from cosmeticos import POR_CLAVE
    from models import AjusteArticulo, CosmeticoAdmin
    e = db.session.get(ArticuloExtra, i.id)
    aj = db.session.get(AjusteArticulo, i.clave)
    cos = CosmeticoAdmin.query.filter_by(clave=i.clave).first() if i.clave.startswith("a_") else None
    info = POR_CLAVE.get(i.clave)
    tipo = info["tipo"] if info else ("cofre" if i.clave.startswith("cofre") else "potenciador")
    return {"id": i.id, "clave": i.clave, "nombre": i.nombre, "descripcion": i.descripcion, "icono": i.icono, "precio": i.precio,
            "activo": i.activo, "orden": i.orden, "origen": _origen(i.clave), "propio": i.clave.startswith("x_"), "tipo": tipo,
            "rareza": RAREZA.get(i.clave, "comun"), "ajustado": bool(aj and (aj.precio is not None or aj.nombre or aj.descripcion or aj.rareza)),
            "oculto": bool(aj and aj.oculto), "vendidos": Purchase.query.filter_by(articulo_id=i.id).count(),
            "diseno": cos.diseno if cos else None,
            "extra": {"xp": e.xp, "vidas": e.vidas, "salvarrachas": e.salvarrachas, "medalla_id": e.medalla_id, "permanente": e.permanente,
                      "imagen": e.imagen or "", "vitrina": e.vitrina or {}} if e else None}


@bp.get("/api/admin/tienda")
@requiere_admin
def tienda():
    from servicios.catalogo_admin import refrescar
    from servicios.tienda import asegurar_articulos
    refrescar(forzar=True)
    asegurar_articulos()
    return jsonify(articulos=[_articulo(i) for i in StoreItem.query.order_by(StoreItem.orden, StoreItem.id).all()])


def _texto(data, campo, minimo, maximo, etiqueta):
    v = " ".join(str(data.get(campo, "")).split())
    if not minimo <= len(v) <= maximo:
        return None, f"{etiqueta} debe tener entre {minimo} y {maximo} caracteres."
    return v, None


def _precio(data):
    try:
        v = int(data.get("precio"))
    except (TypeError, ValueError):
        return None, "Precio no válido."
    if not 0 <= v <= 1_000_000:
        return None, "El precio debe estar entre 0 y 1.000.000 diamantes."
    return v, None


def _extra(data):
    def entero(k, maximo):
        try:
            return max(0, min(maximo, int(data.get(k) or 0)))
        except (TypeError, ValueError):
            return 0
    mid = data.get("medalla_id")
    mid = int(mid) if str(mid or "").isdigit() and db.session.get(MedallaEspecial, int(mid)) else None
    from servicios.catalogo_admin import _img, limpiar_vitrina
    return {"xp": entero("xp", 100000), "vidas": entero("vidas", 50), "salvarrachas": entero("salvarrachas", 10),
            "medalla_id": mid, "permanente": bool(data.get("permanente")) or bool(mid),
            "imagen": _img(data.get("imagen")) or None, "vitrina": limpiar_vitrina(data.get("vitrina"))}


def _clave_nueva(prefijo, nombre):
    base = re.sub(r"[^a-z0-9]+", "_", _sin_tildes(nombre)).strip("_")[:20] or "articulo"
    clave, n = f"{prefijo}{base}", 1
    while StoreItem.query.filter_by(clave=clave).first():
        n += 1
        clave = f"{prefijo}{base[:17]}_{n}"
    return clave


def _orden_nuevo():
    return min((db.session.query(func.max(StoreItem.orden)).scalar() or 0) + 1, 32000)


@bp.post("/api/admin/tienda")
@requiere_admin
def crear_articulo():
    """Artículo con premios (XP, vidas, salvarrachas, medalla). Los cosméticos se crean en /api/admin/cosmeticos."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    nombre, error = _texto(data, "nombre", 2, 50, "El nombre")
    precio, error2 = _precio(data)
    if error or error2:
        return api_error(error or error2)
    extra = _extra(data)
    if not any((extra["xp"], extra["vidas"], extra["salvarrachas"], extra["medalla_id"])):
        return api_error("El artículo debe dar algo: XP, vidas, salvarrachas o una medalla.")
    item = StoreItem(clave=_clave_nueva("x_", nombre), nombre=nombre, descripcion=str(data.get("descripcion", "")).strip()[:140] or nombre,
                     icono=(str(data.get("icono", "")).strip() or "🎁")[:8], precio=precio, moneda="diamante", categoria="diamante",
                     orden=_orden_nuevo(), activo=bool(data.get("activo", True)))
    db.session.add(item)
    db.session.flush()
    db.session.add(ArticuloExtra(articulo_id=item.id, **extra))
    db.session.commit()
    return jsonify(articulo=_articulo(item)), 201


@bp.patch("/api/admin/tienda/<int:aid>")
@requiere_admin
def editar_articulo(aid):
    """Cambia precio, nombre, descripción, rareza o visibilidad de CUALQUIER artículo (también los de fábrica: el cambio
    se guarda en ajustes_tienda y se aplica encima del código, así no se pierde al reiniciar)."""
    from models import AjusteArticulo, CosmeticoAdmin
    from servicios.catalogo_admin import RAREZAS, refrescar
    data = json_body()
    if isinstance(data, tuple):
        return data
    item = db.session.get(StoreItem, aid)
    if not item:
        return api_error("Ese artículo no existe.", 404)
    origen = _origen(item.clave)
    cambios = {}
    if "nombre" in data:
        cambios["nombre"], error = _texto(data, "nombre", 2, 60, "El nombre")
        if error:
            return api_error(error)
    if "descripcion" in data:
        cambios["descripcion"] = " ".join(str(data["descripcion"]).split())[:200]
    if "precio" in data:
        cambios["precio"], error = _precio(data)
        if error:
            return api_error(error)
    if "icono" in data and origen == "panel":
        item.icono = (str(data["icono"]).strip() or "🎁")[:8]
    rareza = data.get("rareza") if data.get("rareza") in RAREZAS else None
    for k, v in cambios.items():
        setattr(item, k, v)
    if "activo" in data:
        item.activo = bool(data["activo"])
    if origen == "fabrica":
        aj = db.session.get(AjusteArticulo, item.clave) or AjusteArticulo(clave=item.clave)
        for k, v in cambios.items():
            setattr(aj, k, v)
        if rareza:
            aj.rareza = rareza
        if "activo" in data:
            aj.oculto = not item.activo
        db.session.add(aj)
    elif origen == "diseno":
        cos = CosmeticoAdmin.query.filter_by(clave=item.clave).first()
        if cos:
            for k, v in cambios.items():
                setattr(cos, k, v)
            if rareza:
                cos.rareza = rareza
            if "activo" in data:
                cos.activo = item.activo
    elif origen == "panel":
        if rareza:
            aj = db.session.get(AjusteArticulo, item.clave) or AjusteArticulo(clave=item.clave)
            aj.rareza = rareza
            db.session.add(aj)
        if any(k in data for k in ("xp", "vidas", "salvarrachas", "medalla_id", "permanente", "imagen", "vitrina")):
            e = db.session.get(ArticuloExtra, item.id) or ArticuloExtra(articulo_id=item.id)
            for k, v in _extra(data).items():
                setattr(e, k, v)
            db.session.add(e)
    db.session.commit()
    refrescar(forzar=True)
    return jsonify(articulo=_articulo(item))


@bp.delete("/api/admin/tienda/<int:aid>")
@requiere_admin
def borrar_articulo(aid):
    """Quita un artículo de la tienda. Los creados en el panel se borran (quien ya lo compró conserva lo que recibió);
    los de fábrica se ocultan para siempre (el código los volvería a crear) y se pueden restaurar."""
    from models import AjusteArticulo, CosmeticoAdmin, EquippedCosmetics, OwnedCosmetic
    from servicios.catalogo_admin import refrescar
    item = db.session.get(StoreItem, aid)
    if not item:
        return api_error("Ese artículo no existe.", 404)
    origen = _origen(item.clave)
    if origen == "fabrica":
        aj = db.session.get(AjusteArticulo, item.clave) or AjusteArticulo(clave=item.clave)
        aj.oculto = True
        item.activo = False
        db.session.add(aj)
        db.session.commit()
        return jsonify(ok=True, oculto=True)
    Purchase.query.filter_by(articulo_id=item.id).delete()
    ArticuloExtra.query.filter_by(articulo_id=item.id).delete()
    AjusteArticulo.query.filter_by(clave=item.clave).delete()
    if origen == "diseno":
        CosmeticoAdmin.query.filter_by(clave=item.clave).delete()
        OwnedCosmetic.query.filter_by(clave=item.clave).delete()
        for eq in EquippedCosmetics.query.all():
            for tipo in ("fondo", "cursor", "tema", "marco", "efecto", "dedo", "codi", "teclado"):
                if getattr(eq, tipo, None) == item.clave:
                    setattr(eq, tipo, None)
    db.session.delete(item)
    db.session.commit()
    refrescar(forzar=True)
    return jsonify(ok=True, borrado=True)


@bp.post("/api/admin/tienda/<int:aid>/restaurar")
@requiere_admin
def restaurar_articulo(aid):
    """Artículo de fábrica: vuelve a su precio, nombre y descripción del código y se muestra otra vez."""
    import servicios.tienda as st
    from models import AjusteArticulo
    from servicios.catalogo_admin import refrescar
    item = db.session.get(StoreItem, aid)
    if not item or _origen(item.clave) != "fabrica":
        return api_error("Solo los artículos de fábrica se restauran.", 404)
    AjusteArticulo.query.filter_by(clave=item.clave).delete()
    item.activo = True
    db.session.commit()
    import constantes
    import cosmeticos
    if item.clave in cosmeticos.POR_CLAVE:
        constantes.RAREZA[item.clave] = next((c["rareza"] for c in cosmeticos.COSMETICOS if c["clave"] == item.clave), "comun")
    st._ITEMS_LISTOS = False
    st.asegurar_articulos()   # vuelve a poner los valores del código
    refrescar(forzar=True)
    return jsonify(articulo=_articulo(item))


# ------------------------------------------------------------------------------------------------ medallas ----
def _medalla(m):
    return {"id": m.id, "nombre": m.nombre, "descripcion": m.descripcion, "icono": m.icono, "color": m.color, "activa": m.activa,
            "diseno": m.diseno or None, "otorgadas": MedallaOtorgada.query.filter_by(medalla_id=m.id).count(), "creada": _iso(m.creada_en)}


def _datos_medalla(data):
    nombre = str(data.get("nombre", "")).strip()
    if not 2 <= len(nombre) <= 50:
        return None, "El nombre debe tener entre 2 y 50 caracteres."
    color = str(data.get("color", "#c4ff3d")).strip()
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        color = "#c4ff3d"
    from servicios.catalogo_admin import limpiar_medalla
    campos = {"nombre": nombre, "descripcion": str(data.get("descripcion", "")).strip()[:160], "icono": (str(data.get("icono", "")).strip() or "🏅")[:8],
              "color": color, "activa": bool(data.get("activa", True))}
    if isinstance(data.get("diseno"), dict):
        campos["diseno"] = limpiar_medalla(data["diseno"])
        campos["icono"] = campos["diseno"]["emoji"]   # el ícono y el color de siempre siguen sirviendo (correos, listas)
        campos["color"] = campos["diseno"]["c1"]
    return campos, None


@bp.get("/api/admin/medallas")
@requiere_admin
def medallas():
    return jsonify(medallas=[_medalla(m) for m in MedallaEspecial.query.order_by(MedallaEspecial.id.desc())])


@bp.post("/api/admin/medallas")
@requiere_admin
def crear_medalla():
    data = json_body()
    if isinstance(data, tuple):
        return data
    campos, error = _datos_medalla(data)
    if error:
        return api_error(error)
    m = MedallaEspecial(**campos)
    db.session.add(m)
    db.session.commit()
    return jsonify(medalla=_medalla(m)), 201


@bp.delete("/api/admin/medallas/<int:mid>")
@requiere_admin
def borrar_medalla(mid):
    """Borra la medalla y se la quita a quien la tenía."""
    m = db.session.get(MedallaEspecial, mid)
    if not m:
        return api_error("Esa medalla no existe.", 404)
    MedallaOtorgada.query.filter_by(medalla_id=mid).delete()
    ArticuloExtra.query.filter_by(medalla_id=mid).update({ArticuloExtra.medalla_id: None})
    db.session.delete(m)
    db.session.commit()
    return jsonify(ok=True)


@bp.patch("/api/admin/medallas/<int:mid>")
@requiere_admin
def editar_medalla(mid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    m = db.session.get(MedallaEspecial, mid)
    if not m:
        return api_error("Esa medalla no existe.", 404)
    campos, error = _datos_medalla({**_medalla(m), **data})
    if error:
        return api_error(error)
    for k, v in campos.items():
        setattr(m, k, v)
    db.session.commit()
    return jsonify(medalla=_medalla(m))


@bp.post("/api/admin/correo-prueba")
@requiere_admin
def correo_prueba():
    """Te manda un correo de prueba a ti mismo y espera el resultado: así sabes si los avisos salen de verdad."""
    from servicios.correo import enviar, plantilla
    resultado = {}

    def fin(estado, detalle):
        resultado.update(estado=estado, detalle=detalle)
    enviar(current_user.email, "✅ Prueba de correo del panel de CódigoCamp",
           plantilla("Los avisos funcionan", ["Si lees esto, los correos de advertencia de CódigoCamp están saliendo de verdad."], animo="celebra"),
           esperar=True, al_terminar=fin)
    if resultado.get("estado") == "enviado":
        return jsonify(ok=True, mensaje=f"Correo enviado a {current_user.email}. Revisa tu bandeja (y la carpeta de spam).")
    return api_error(resultado.get("detalle") or "No se pudo enviar.", 502)
