"""Cosméticos (equipar), los 10 cofres de recompensas y la foto de perfil."""
import hashlib
import os
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from constantes import MAX_SALVARRACHAS
from cosmeticos import COFRE_POR_CLAVE, COFRES, POR_CLAVE, TIPOS
from models import (CompletedLevel, DailyChallenge, EquippedCosmetics, Friendship, LessonDone, OpenedChest, OwnedCosmetic, Profile,
                    ProfilePhoto, User, db)
from servicios.perfil import apply_reward, get_profile, progress
from utilidades import api_error, json_body, too_many

bp = Blueprint("cosmeticos", __name__)
MAX_FOTO = 5 * 1024 * 1024
FIRMAS = {b"\x89PNG\r\n\x1a\n": "image/png", b"\xff\xd8\xff": "image/jpeg", b"RIFF": "image/webp", b"GIF87a": "image/gif", b"GIF89a": "image/gif"}


def equipados_de(usuario_id):
    e = db.session.get(EquippedCosmetics, usuario_id)
    return {t: getattr(e, t) if e else None for t in TIPOS}


def propios_de(usuario_id):
    return {c.clave for c in OwnedCosmetic.query.filter_by(usuario_id=usuario_id).all()}


def foto_url(usuario_id):
    f = db.session.get(ProfilePhoto, usuario_id)
    return f"/api/perfil/foto/{usuario_id}?v={f.hash[:12]}" if f else ""


def dar_cosmetico(usuario_id, clave, origen):
    if clave in POR_CLAVE and not OwnedCosmetic.query.filter_by(usuario_id=usuario_id, clave=clave).first():
        db.session.add(OwnedCosmetic(usuario_id=usuario_id, clave=clave, origen=origen))


# ------------------------------------------------------------------------------- cosméticos ----
@bp.get("/api/cosmeticos/")
@login_required
def ver():
    propios = propios_de(current_user.id)
    return jsonify(
        equipados=equipados_de(current_user.id),
        catalogo=[{**c, "tuyo": c["clave"] in propios} for c in POR_CLAVE.values()],
    )


@bp.post("/api/cosmeticos/equipar/")
@login_required
def equipar():
    data = json_body()
    if isinstance(data, tuple):
        return data
    tipo, clave = data.get("tipo"), data.get("clave")
    if tipo not in TIPOS:
        return api_error("Tipo de cosmético no válido.")
    if clave is not None:
        info = POR_CLAVE.get(str(clave))
        if not info or info["tipo"] != tipo:
            return api_error("Ese cosmético no existe.")
        if clave not in propios_de(current_user.id):
            return api_error("Todavía no tienes ese cosmético. Cómpralo en la tienda o gánalo en un cofre.", 403)
    e = db.session.get(EquippedCosmetics, current_user.id) or EquippedCosmetics(usuario_id=current_user.id)
    setattr(e, tipo, clave)
    db.session.add(e)
    db.session.commit()
    return jsonify(equipados=equipados_de(current_user.id))


# ----------------------------------------------------------------------------------- cofres ----
def _medidas(usuario):
    p = get_profile(usuario)
    amigos = Friendship.query.filter(Friendship.estado == "aceptada", or_(Friendship.de_usuario_id == usuario.id, Friendship.a_usuario_id == usuario.id)).count()
    return {
        "lecciones": LessonDone.query.filter_by(usuario_id=usuario.id).count(),
        "racha": max(p.racha_maxima, p.racha_actual),
        "xp": p.xp_total,
        "niveles": CompletedLevel.query.filter_by(usuario_id=usuario.id).count(),
        "desafios": DailyChallenge.query.filter_by(usuario_id=usuario.id).count(),
        "amigos": amigos,
    }


def _premio_publico(premio):
    salida = {k: v for k, v in premio.items() if k != "cosmetico"}
    lista = premio.get("cosmetico")
    if lista:
        lista = lista if isinstance(lista, list) else [lista]
        salida["cosmeticos"] = [{"clave": c, "nombre": POR_CLAVE[c]["nombre"], "tipo": POR_CLAVE[c]["tipo"], "rareza": POR_CLAVE[c]["rareza"]} for c in lista]
    return salida


@bp.get("/api/cofres/")
@login_required
def cofres():
    m = _medidas(current_user)
    from servicios.zona import iso
    abiertos = {c.clave: iso(c.abierto_en) for c in OpenedChest.query.filter_by(usuario_id=current_user.id).all()}
    db.session.commit()
    return jsonify(cofres=[{
        "clave": c["clave"], "nombre": c["nombre"], "cofre": c["cofre"], "texto": c["texto"], "meta": c["meta"],
        "progreso": min(m[c["medida"]], c["meta"]), "listo": m[c["medida"]] >= c["meta"], "abierto": c["clave"] in abiertos,
        "abierto_en": abiertos.get(c["clave"]), "premio": _premio_publico(c["premio"]),
    } for c in COFRES])


@bp.post("/api/cofres/abrir/")
@login_required
def abrir_cofre():
    data = json_body()
    if isinstance(data, tuple):
        return data
    c = COFRE_POR_CLAVE.get(str(data.get("clave", "")))
    if not c:
        return api_error("Ese cofre no existe.", 404)
    if OpenedChest.query.filter_by(usuario_id=current_user.id, clave=c["clave"]).first():
        return api_error("Ya abriste este cofre.", 409)
    if _medidas(current_user)[c["medida"]] < c["meta"]:
        return api_error(f"Todavía no: {c['texto'].lower()}.", 403)
    get_profile(current_user)
    perfil = Profile.query.filter_by(usuario_id=current_user.id).with_for_update().one()
    premio = c["premio"]
    apply_reward(perfil, {k: premio[k] for k in ("diamante", "xp", "vidas") if k in premio})
    if premio.get("salvarrachas"):
        perfil.salvarrachas = min(MAX_SALVARRACHAS, perfil.salvarrachas + premio["salvarrachas"])
    lista = premio.get("cosmetico")
    for clave in (lista if isinstance(lista, list) else [lista] if lista else []):
        dar_cosmetico(current_user.id, clave, "cofre")
    db.session.add(OpenedChest(usuario_id=current_user.id, clave=c["clave"]))
    db.session.commit()
    return jsonify(premio=_premio_publico(premio), **progress(current_user))


# ----------------------------------------------------------------------------- foto de perfil ----
def _dir_fotos(usuario_id):
    return Path(current_app.config["ALMACEN_ARCHIVOS"]) / str(int(usuario_id))


@bp.post("/api/perfil/foto/")
@login_required
def subir_foto():
    if too_many(f"foto:{current_user.id}", 20, 3600):
        return api_error("Demasiados cambios de foto. Espera un rato.", 429)
    datos = request.get_data(cache=False)
    if not datos:
        return api_error("No llegó ninguna imagen.")
    if len(datos) > MAX_FOTO:
        return api_error("La foto pesa demasiado (máximo 5 MB).", 413)
    tipo = next((t for firma, t in FIRMAS.items() if datos.startswith(firma)), None)
    if tipo == "image/webp" and datos[8:12] != b"WEBP":
        tipo = None
    if not tipo:
        return api_error("La foto debe ser PNG, JPG, WEBP o GIF.")
    h = hashlib.sha256(datos).hexdigest()
    carpeta = _dir_fotos(current_user.id)
    carpeta.mkdir(parents=True, exist_ok=True)
    anterior = db.session.get(ProfilePhoto, current_user.id)
    destino = carpeta / f"foto-{h}"
    tmp = carpeta / f".foto-{h}.tmp"
    tmp.write_bytes(datos)
    os.replace(tmp, destino)
    if anterior and anterior.hash != h:
        try:
            (carpeta / f"foto-{anterior.hash}").unlink()
        except OSError:
            pass
    foto = anterior or ProfilePhoto(usuario_id=current_user.id)
    foto.hash, foto.tipo = h, tipo
    foto.actualizada_en = func.now()
    db.session.add(foto)
    db.session.commit()
    return jsonify(foto=foto_url(current_user.id))


@bp.delete("/api/perfil/foto/")
@login_required
def borrar_foto():
    foto = db.session.get(ProfilePhoto, current_user.id)
    if foto:
        try:
            (_dir_fotos(current_user.id) / f"foto-{foto.hash}").unlink()
        except OSError:
            pass
        db.session.delete(foto)
        db.session.commit()
    return jsonify(foto="")


@bp.get("/api/perfil/foto/<int:usuario_id>")
@login_required
def ver_foto(usuario_id):
    # Cualquier persona con sesión puede ver fotos de perfil (aparecen en chats, amigos y clasificaciones).
    foto = db.session.get(ProfilePhoto, usuario_id)
    if not foto or not db.session.get(User, usuario_id):
        return api_error("Sin foto.", 404)
    ruta = _dir_fotos(usuario_id) / f"foto-{foto.hash}"
    if not ruta.exists():
        return api_error("Sin foto.", 404)
    r = send_file(ruta, mimetype=foto.tipo, conditional=True, max_age=86400 * 30)
    r.headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
    r.headers["X-Content-Type-Options"] = "nosniff"
    return r


# ------------------------------------------------------------------------- widget de la app ----
def _racha_info(p, hoy):
    """Días de la racha actual (si sigue viva hoy o ayer)."""
    from datetime import timedelta
    if not p.ultima_actividad or (hoy - p.ultima_actividad).days > 1 or not p.racha_actual:
        return set()
    return {p.ultima_actividad - timedelta(days=i) for i in range(p.racha_actual)}


@bp.get("/api/racha/calendario/")
@login_required
def calendario_racha():
    """Calendario de racha (como Duolingo): los días que practicaste en un mes y los de tu racha actual."""
    import calendar as _cal
    from datetime import date
    from models import DailyActivity
    from servicios.zona import hoy_de
    hoy = hoy_de(get_profile(current_user))
    try:
        anio, mes = (int(x) for x in str(request.args.get("mes", f"{hoy:%Y-%m}")).split("-", 1))
        inicio = date(anio, mes, 1)
    except (TypeError, ValueError):
        return api_error("Mes no válido (usa AAAA-MM).")
    fin = date(anio, mes, _cal.monthrange(anio, mes)[1])
    p = get_profile(current_user)
    db.session.commit()
    racha = _racha_info(p, hoy)
    filas = (DailyActivity.query.filter(DailyActivity.usuario_id == current_user.id, DailyActivity.fecha >= inicio, DailyActivity.fecha <= fin)
             .order_by(DailyActivity.fecha).all())
    dias = [{"fecha": f.fecha.isoformat(), "xp": f.xp, "niveles": f.niveles, "en_racha": f.fecha in racha} for f in filas if f.xp > 0 or f.niveles > 0]
    vistos = {d["fecha"] for d in dias}
    for d in sorted(racha):   # días de racha sin fila de actividad (p. ej. lecciones de Aprende): también cuentan
        if inicio <= d <= fin and d.isoformat() not in vistos:
            dias.append({"fecha": d.isoformat(), "xp": 0, "niveles": 0, "en_racha": True})
    dias.sort(key=lambda d: d["fecha"])
    return jsonify(mes=f"{anio:04d}-{mes:02d}", hoy=hoy.isoformat(), es_mes_actual=(anio, mes) == (hoy.year, hoy.month),
                   dias=dias, dias_mes=len(dias), racha_actual=p.racha_actual if racha else 0, racha_maxima=p.racha_maxima,
                   salvarrachas=p.salvarrachas, practicado_hoy=p.ultima_actividad == hoy)


def _datos_widget(usuario):
    """Racha, semana, meta de hoy y calendario para todos los widgets (Windows 11, iPhone/iPad, Android, escritorio)."""
    from datetime import timedelta
    from models import DailyActivity
    p = get_profile(usuario)
    db.session.commit()
    from servicios.zona import ahora_de
    ahora = ahora_de(p)   # la hora del lugar donde está la persona (su dispositivo)
    hoy = ahora.date()
    practicado = p.ultima_actividad == hoy
    racha_dias = _racha_info(p, hoy)
    racha = p.racha_actual if racha_dias else 0
    # Semana (lunes a domingo) para los widgets: 🔥 practicado · ⏳ hoy pendiente · «·» no practicado · ○ por venir
    lunes = hoy - timedelta(days=hoy.weekday())
    activos = {a.fecha for a in DailyActivity.query.filter(DailyActivity.usuario_id == usuario.id, DailyActivity.fecha >= lunes,
                                                           DailyActivity.fecha <= hoy) if a.xp > 0 or a.niveles > 0} | racha_dias
    semana = []
    for i, letra in enumerate("LMMJVSD"):
        d = lunes + timedelta(days=i)
        estado_dia = "hecho" if d in activos else ("hoy" if d == hoy else ("perdido" if d < hoy else "futuro"))
        semana.append({"letra": letra, "icono": {"hecho": "🔥", "hoy": "⏳", "perdido": "·", "futuro": "○"}[estado_dia], "hoy": d == hoy,
                       "estado": estado_dia, "fecha": d.isoformat()})
    act = DailyActivity.query.filter_by(usuario_id=usuario.id, fecha=hoy).first()
    xp_hoy = act.xp if act else 0
    meta_xp = max(10, p.meta_minutos * 3)
    hora = ahora.hour
    if practicado:
        estado = "¡Ya practicaste hoy! 💪"
    elif racha:
        estado = f"⚠️ Practica antes de medianoche o pierdes tu racha de {racha}" if hora >= 18 else "Practica hoy para no perder tu racha"
    else:
        estado = "Empieza tu racha hoy"
    base = request.host_url.rstrip("/")
    return dict(
        racha=racha, racha_maxima=p.racha_maxima, xp=p.xp_total, diamantes=p.diamante, meta=p.meta_minutos,
        nombre=(usuario.nombre or "").split(" ")[0], practicado_hoy=practicado, estado=estado, salvarrachas=p.salvarrachas,
        semana=semana, semana_texto=" ".join(x["icono"] for x in semana), xp_hoy=xp_hoy, meta_xp=meta_xp,
        progreso_hoy=min(100, round(xp_hoy * 100 / meta_xp)), vidas=p.vidas,
        mes=hoy.strftime("%m/%Y"), titulo=f"🔥 {racha} día{'s' if racha != 1 else ''}",
        # Direcciones absolutas: el panel de widgets de Windows y las apps de widgets no conocen la página de origen.
        url_practicar=f"{base}/pages/inicio.html?app=1", url_cofres=f"{base}/pages/recompensas.html?app=1",
        url_calendario=f"{base}/pages/perfil.html?app=1#calendario", actualizado=ahora.strftime("%H:%M"), zona=ahora.tzname(),
    )


def _firma_widget(fila):
    import hmac
    import base64
    clave = str(current_app.config["SECRET_KEY"]).encode()
    firma = hmac.new(clave, f"cc-widget|{fila.usuario_id}|{fila.token_hash}".encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(firma).decode().rstrip("=")


def token_widget(fila):
    """Token del widget para ESTE inicio de sesión: «<id de sesión>.<firma>». No se guarda en ningún lado: se calcula.
    Sirve mientras esa sesión siga abierta; al cerrar sesión (aquí o desde otro dispositivo) deja de funcionar."""
    return f"{fila.id}.{_firma_widget(fila)}"


def _usuario_de_enlace(token):
    import hmac
    from models import UserSession
    sid, _, firma = str(token or "").partition(".")
    if not sid.isdigit() or not (20 <= len(firma) <= 60):
        return None
    fila = db.session.get(UserSession, int(sid))
    if fila is None or fila.revocada or not hmac.compare_digest(firma, _firma_widget(fila)):
        return None
    usuario = db.session.get(User, fila.usuario_id)
    return usuario if usuario and usuario.activo else None


def _enlaces(token):
    from urllib.parse import quote
    base = request.host_url.rstrip("/")
    t = quote(token, safe="")
    return dict(token=token, base=base, datos=f"{base}/api/widget/?t={t}", pagina=f"{base}/pages/widget.html?t={t}",
                scriptable=f"{base}/api/widget/scriptable.js?t={t}",
                android=f"intent://conectar?base={quote(base, safe='')}&t={t}#Intent;scheme=codigocamp-widget;package=com.codigocamp.widget;end",
                android_directo=f"codigocamp-widget://conectar?base={quote(base, safe='')}&t={t}")


@bp.get("/api/widget/")
def widget():
    """Datos de los widgets. Con la sesión de CódigoCamp (la app, Windows 11, el widget flotante) o con el token de
    la sesión ?t=… (widgets de iPhone/iPad con Scriptable y de Android, que no comparten las cookies del navegador)."""
    token = request.args.get("t") or request.headers.get("X-Widget-Token", "")
    if current_user.is_authenticated and not token:
        usuario = current_user
    elif token:
        if too_many(f"widget:{request.remote_addr}", 120, 60):
            return api_error("Demasiadas consultas. Espera un momento.", 429)
        usuario = _usuario_de_enlace(token)
        if not usuario:
            return api_error("Tu sesión de CódigoCamp se cerró. Inicia sesión otra vez y vuelve a conectar el widget.", 401)
    else:
        return api_error("Inicia sesión para continuar.", 401)
    r = jsonify(_datos_widget(usuario))
    r.headers["Cache-Control"] = "no-store"
    if token:
        r.headers["Access-Control-Allow-Origin"] = "*"   # solo lectura y sin cookies: lo pueden pedir apps de widgets
    return r


def _apk():
    from constantes import FRONTEND
    ruta = FRONTEND / "descargas" / "CodigoCamp.apk"
    return ruta if ruta.is_file() else None


@bp.get("/api/app/")
def app_android():
    """¿Hay app de Android para descargar? (botón «Descargar la app» de la página de inicio). Público."""
    ruta = _apk()
    r = jsonify(android=bool(ruta), url="/descargas/CodigoCamp.apk" if ruta else None,
                tam=ruta.stat().st_size if ruta else 0, version=int(ruta.stat().st_mtime) if ruta else 0)
    r.headers["Cache-Control"] = "no-cache"
    return r


@bp.get("/api/widget/conectar/")
@login_required
def conectar_widget():
    """Enlaces del widget para la sesión actual (no hay que crear nada: se usa la sesión que ya está abierta)."""
    from models import UserSession
    sesion_id = getattr(current_user, "_sesion_id", None)
    fila = db.session.get(UserSession, sesion_id) if sesion_id else None
    if fila is None or fila.revocada:
        return api_error("Vuelve a iniciar sesión para conectar los widgets.", 401)
    r = jsonify(**_enlaces(token_widget(fila)), apk=_apk() is not None)
    r.headers["Cache-Control"] = "no-store"
    return r


@bp.get("/api/widget/scriptable.js")
def widget_scriptable():
    """Script para la app gratuita Scriptable (iPhone, iPad y Mac con Apple Silicon): widget de pantalla de inicio de verdad."""
    token = request.args.get("t", "")
    if not token and current_user.is_authenticated:
        from models import UserSession
        fila = db.session.get(UserSession, getattr(current_user, "_sesion_id", 0) or 0)
        token = token_widget(fila) if fila and not fila.revocada else ""
    if not _usuario_de_enlace(token):
        return api_error("Inicia sesión en CódigoCamp para descargar el widget.", 401)
    from constantes import FRONTEND
    plantilla = (FRONTEND / "widgets" / "scriptable.js").read_text(encoding="utf-8")
    base = request.host_url.rstrip("/")
    codigo = plantilla.replace("__CC_BASE__", base).replace("__CC_TOKEN__", token)
    r = current_app.response_class(codigo, mimetype="text/javascript")
    r.headers["Content-Disposition"] = 'attachment; filename="CodigoCamp.js"'
    r.headers["Cache-Control"] = "no-store"
    return r
