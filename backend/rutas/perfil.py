"""Perfil del usuario y ajustes."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Course, Profile, db
from constantes import ALIAS_OK
from servicios.perfil import _user, get_profile, progress
from utilidades import api_error, json_body, parse_integer

bp = Blueprint("perfil", __name__)


@bp.route("/api/perfil/", methods=["GET", "POST"])
@login_required
def perfil():
    profile = get_profile(current_user)
    if request.method == "POST":
        data = json_body()
        if isinstance(data, tuple):
            return data
        rol, nivel = data.get("rol", ""), data.get("nivel", "")
        if rol not in Profile.ROLES or nivel not in Profile.NIVELES:
            return api_error("Respuestas no válidas.")
        meta = parse_integer(data.get("meta"), 0)
        if meta not in {5, 10, 15, 30}:
            return api_error("Meta diaria no válida.")
        course = Course.query.filter_by(slug=str(data.get("curso", "")), activo=True).first()
        if not course:
            return api_error("Curso no válido.")
        if not data.get("terminos"):
            return api_error("Para empezar debes aceptar los Términos y condiciones.")
        interests = data.get("intereses") if isinstance(data.get("intereses"), list) else []
        profile.rol = rol
        profile.nivel_previo = nivel
        profile.meta_minutos = meta
        profile.curso_actual = course
        profile.intereses = [item for item in interests if item in {"web", "movil", "juegos", "datos", "auto", "bd"}]
        profile.onboarding_completo = True
        from servicios.terminos import registrar_aceptacion
        registrar_aceptacion(current_user.id)
        db.session.commit()
    return jsonify(perfil={
        "rol": profile.rol, "intereses": profile.intereses, "nivel": profile.nivel_previo,
        "meta": profile.meta_minutos, "curso": profile.curso_actual.slug if profile.curso_actual else None,
        "onboarding": profile.onboarding_completo, "tema": profile.tema, "idioma": profile.idioma or "es", "buscable_correo": profile.buscable_correo is not False,
    })


@bp.post("/api/ajustes/")
@login_required
def ajustes():
    data = json_body()
    if isinstance(data, tuple):
        return data
    profile = get_profile(current_user)
    if "nombre" in data:
        name = str(data["nombre"]).strip()
        if not 2 <= len(name) <= 50:
            return api_error("El nombre debe tener entre 2 y 50 caracteres.")
        current_user.nombre = name
    if "alias" in data:
        alias = str(data["alias"]).strip().lstrip("@").lower()
        if not ALIAS_OK.fullmatch(alias):
            return api_error("El nombre de usuario debe tener de 3 a 20 letras, números o guion bajo (_).")
        if Profile.query.filter(Profile.alias == alias, Profile.id != profile.id).first():
            return api_error("Ese nombre de usuario ya está en uso.", 409)
        profile.alias = alias
    if "tema" in data:
        if data["tema"] not in Profile.TEMAS:
            return api_error("Tema no válido.")
        profile.tema = data["tema"]
    if "buscable_correo" in data:
        profile.buscable_correo = bool(data["buscable_correo"])
    if "idioma" in data:   # la app es solo en español
        profile.idioma = "es"
    if "meta" in data:
        if data["meta"] not in {5, 10, 15, 30}:
            return api_error("Meta no válida.")
        profile.meta_minutos = data["meta"]
    if "curso" in data:
        course = Course.query.filter_by(slug=str(data["curso"]), activo=True).first()
        if not course:
            return api_error("Curso no válido.")
        profile.curso_actual = course
    if "rol" in data:
        if data["rol"] not in Profile.ROLES:
            return api_error("Esa opción de \"qué eres\" no es válida.")
        profile.rol = data["rol"]
    if "nivel" in data:
        if data["nivel"] not in Profile.NIVELES:
            return api_error("Ese nivel no es válido.")
        profile.nivel_previo = data["nivel"]
    if "avatar" in data:   # los avatares se retiraron: se queda la foto o la inicial
        profile.avatar = None
    db.session.commit()
    return jsonify(user=_user(current_user), **progress(current_user))


@bp.get("/api/avatares/")
@login_required
def avatares():
    """Los avatares se retiraron (se devolvieron los diamantes). Se deja la ruta para versiones viejas de la app."""
    return jsonify(libres=[], coleccion=[])


@bp.get("/api/terminos/")
def terminos():
    from servicios.terminos import acepto_actual, version_actual
    return jsonify(version=version_actual(), aceptado=acepto_actual(current_user.id) if current_user.is_authenticated else False)


@bp.post("/api/terminos/aceptar/")
@login_required
def aceptar_terminos():
    """Para cuentas que ya hicieron el onboarding y deben aceptar una versión nueva de los términos."""
    from servicios.terminos import registrar_aceptacion, version_actual
    data = json_body()
    if isinstance(data, tuple):
        return data
    if not data.get("acepto"):
        return api_error("Debes aceptar los Términos y condiciones para seguir usando CódigoCamp.")
    registrar_aceptacion(current_user.id)
    db.session.commit()
    return jsonify(ok=True, version=version_actual())
