import calendar
import click
import json
import os
import random
import re
import secrets
import threading
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request, send_from_directory, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

from models import (
    Challenge, CompletedLevel, Course, DailyActivity, DailyChallenge, Friendship,
    LessonDone, Level, Message, MonthChallenge, Profile, Purchase, StoreItem,
    Section, Stage, TutorUsage, User, db, utcnow,
)

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
BACKEND = Path(__file__).resolve().parent
load_dotenv(BACKEND / ".env")

MAX_VIDAS_REGEN = 5
MAX_VIDAS = 10
MAX_SALVARRACHAS = 2
MINUTOS_VIDA = 30
META_MES = 60
PUNTOS_POR_DESAFIO = 5
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DAILY_CHALLENGES = [
    {"clave": "xp30", "icono": "⭐", "titulo": "Gana 30 XP", "campo": "xp", "meta": 30, "premio": {"diamante": 1}},
    {"clave": "niveles2", "icono": "🎯", "titulo": "Completa 2 niveles", "campo": "niveles", "meta": 2, "premio": {"diamante": 2}},
    {"clave": "perfecto", "icono": "💎", "titulo": "Termina un nivel sin fallos", "campo": "perfectos", "meta": 1, "premio": {"diamante": 1}},
]
PREMIO_MES = {"diamante": 5}
# Artículos que se pagan con diamantes. Se crean solos en la base la primera vez que se abre la tienda.
# tipo: "consumible" (se puede comprar muchas veces) o "permanente" (se compra una vez y queda en tu colección)
ARTICULOS_DIAMANTE = [
    {"clave": "impulso_xp", "nombre": "Impulso de XP", "icono": "⚡", "precio": 2, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Gana 60 XP al instante y sube de nivel más rápido."},
    {"clave": "mega_vidas", "nombre": "Mega pack de vidas", "icono": "🔋", "precio": 4, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Llena tus vidas hasta diez. ¡Practica sin parar!"},
    {"clave": "cofre_misterioso", "nombre": "Cofre misterioso", "icono": "📦", "precio": 2, "rareza": "raro", "tipo": "consumible",
     "descripcion": "Ábrelo y descubre un premio sorpresa: XP, vidas o más diamantes."},
    {"clave": "cofre_legendario", "nombre": "Cofre legendario", "icono": "🎁", "precio": 5, "rareza": "legendario", "tipo": "consumible",
     "descripcion": "Premio grande garantizado: 150 XP, 3 vidas y a veces diamantes extra."},
    {"clave": "gafas_pro", "nombre": "Gafas de programador", "icono": "😎", "precio": 2, "rareza": "comun", "tipo": "permanente",
     "descripcion": "Presume tu estilo en la colección de tu perfil."},
    {"clave": "marco_dorado", "nombre": "Marco dorado", "icono": "🖼️", "precio": 3, "rareza": "raro", "tipo": "permanente",
     "descripcion": "Un marco brillante para tu colección."},
    {"clave": "estela_cohete", "nombre": "Estela de cohete", "icono": "🚀", "precio": 3, "rareza": "raro", "tipo": "permanente",
     "descripcion": "Deja una estela de fuego por donde pases."},
    {"clave": "aura_neon", "nombre": "Aura neón", "icono": "🌈", "precio": 5, "rareza": "epico", "tipo": "permanente",
     "descripcion": "Un resplandor de colores que solo tienen los mejores."},
    {"clave": "corona_campeon", "nombre": "Corona de campeón", "icono": "👑", "precio": 6, "rareza": "epico", "tipo": "permanente",
     "descripcion": "La corona de quien no se rinde."},
    {"clave": "mascota_dragon", "nombre": "Mascota dragón", "icono": "🐉", "precio": 8, "rareza": "legendario", "tipo": "permanente",
     "descripcion": "Un dragón que cuida tu código."},
    {"clave": "titulo_leyenda", "nombre": "Título: Leyenda del código", "icono": "🌟", "precio": 10, "rareza": "legendario", "tipo": "permanente",
     "descripcion": "El título más raro de CódigoCamp."},
]
RAREZA = {"vida": "comun", "vidas_llenas": "comun", "salvarracha": "raro", "kit_experto": "raro",
          **{a["clave"]: a["rareza"] for a in ARTICULOS_DIAMANTE}}
PERMANENTES = {a["clave"] for a in ARTICULOS_DIAMANTE if a["tipo"] == "permanente"}
BASICOS_DIAMANTE = {"vida": 1, "vidas_llenas": 3, "salvarracha": 2, "kit_experto": 4}   # clave -> precio en diamantes
AVATARES_LIBRES = ["🙂", "😎", "🤖", "🦊", "🐱", "🐼", "🦄", "👾", "🐸", "🦉"]
_ITEMS_LISTOS = False
ALIAS_OK = re.compile(r"^[a-z0-9_]{3,20}$")
_RATE_LIMITS = {}
_RATE_LOCK = threading.Lock()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY") or ("solo-desarrollo-cambiame" if os.getenv("DEBUG", "1") == "1" else None),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("DEBUG", "1") != "1",
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", ""),
        GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    )
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_user = quote_plus(os.getenv("DB_USER", "root"))
        db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "codigocamp")
        db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Configura SECRET_KEY en backend/.env antes de iniciar la app.")

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    @login_manager.unauthorized_handler
    def unauthorized():
        return api_error("Inicia sesión para continuar.", 401)

    @app.before_request
    def csrf_protection():
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            session.setdefault("_csrf_token", secrets.token_urlsafe(32))
            return None
        if request.path.startswith("/api/"):
            cookie_token = request.cookies.get("csrftoken", "")
            session_token = session.get("_csrf_token", "")
            header_token = request.headers.get("X-CSRFToken", "")
            if not cookie_token or not session_token or not secrets.compare_digest(cookie_token, session_token) or not secrets.compare_digest(header_token, session_token):
                return api_error("La sesión de seguridad venció. Recarga la página e inténtalo otra vez.", 403)
        return None

    @app.after_request
    def set_csrf_cookie(response):
        token = session.get("_csrf_token")
        if token:
            response.set_cookie("csrftoken", token, httponly=False, samesite="Lax", secure=app.config["SESSION_COOKIE_SECURE"])
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        if request.path.startswith("/api/"):
            return api_error(error.description, error.code or 400)
        return error

    @app.get("/")
    def portada():
        return send_from_directory(FRONTEND, "index.html")

    @app.cli.command("seed-retos")
    @click.option("--reset", is_flag=True, help="Borra el catálogo (y el progreso de niveles) y lo vuelve a cargar.")
    def seed_retos(reset):
        """Carga etapas, secciones, lecciones y preguntas desde backend/retos/*.py."""
        from retos import poblar_catalogo

        if poblar_catalogo(db.session, reset=reset):
            print("Catálogo cargado: etapas, secciones, lecciones y preguntas listas.")
        else:
            print("El catálogo ya estaba completo; no se hicieron cambios. Usa --reset tras editar los retos.")

    @app.cli.command("check-retos")
    def check_retos():
        """Revisa los archivos de retos (sin base de datos) y muestra cuántas preguntas tiene cada curso."""
        from retos import revisar_catalogo

        raise SystemExit(revisar_catalogo())

    @app.get("/pages/<path:filename>")
    def pagina(filename):
        return send_from_directory(FRONTEND / "pages", filename)

    @app.get("/<path:filename>")
    def archivo_frontend(filename):
        if filename.startswith(("api/", "admin/")):
            abort(404)
        return send_from_directory(FRONTEND, filename)

    @app.get("/api/auth/me/")
    def yo():
        return jsonify(user=_user(current_user) if current_user.is_authenticated else None)

    @app.post("/api/auth/register/")
    def registro():
        if too_many(f"auth:{client_ip()}", 15, 900):
            return api_error("Demasiados intentos. Espera unos minutos.", 429)
        data = json_body()
        if isinstance(data, tuple):
            return data
        nombre = str(data.get("nombre", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        if not 2 <= len(nombre) <= 50:
            return api_error("El nombre debe tener entre 2 y 50 caracteres.")
        if len(email) > 150 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return api_error("Correo electrónico no válido.")
        if not valid_password(password):
            return api_error("La contraseña debe tener mínimo 6 caracteres, una mayúscula y un número.")
        if User.query.filter_by(email=email).first():
            return api_error("Ese correo ya está registrado.", 409)
        user = User(email=email, nombre=nombre, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.flush()
        profile = Profile(user=user)
        ensure_identity(profile, nombre)
        db.session.add(profile)
        db.session.commit()
        login_user(user, remember=True)
        return jsonify(user=_user(user)), 201

    @app.post("/api/auth/login/")
    def entrar():
        if too_many(f"auth:{client_ip()}", 15, 900):
            return api_error("Demasiados intentos. Espera unos minutos.", 429)
        data = json_body()
        if isinstance(data, tuple):
            return data
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        user = User.query.filter_by(email=email, activo=True).first() if email else None
        if not user or len(password) > 100 or not check_password_hash(user.password_hash, password):
            return api_error("Correo o contraseña incorrectos.", 401)
        login_user(user, remember=True)
        return jsonify(user=_user(user))

    @app.post("/api/auth/logout/")
    def salir():
        logout_user()
        return jsonify(ok=True)

    @app.route("/api/perfil/", methods=["GET", "POST"])
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
            interests = data.get("intereses") if isinstance(data.get("intereses"), list) else []
            profile.rol = rol
            profile.nivel_previo = nivel
            profile.meta_minutos = meta
            profile.curso_actual = course
            profile.intereses = [item for item in interests if item in {"web", "movil", "juegos", "datos", "auto", "bd"}]
            profile.onboarding_completo = True
            db.session.commit()
        return jsonify(perfil={
            "rol": profile.rol, "intereses": profile.intereses, "nivel": profile.nivel_previo,
            "meta": profile.meta_minutos, "curso": profile.curso_actual.slug if profile.curso_actual else None,
            "onboarding": profile.onboarding_completo, "tema": profile.tema,
        })

    @app.post("/api/ajustes/")
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
        if "avatar" in data:
            emoji = str(data["avatar"]).strip()
            if emoji:
                propios = {c.articulo.icono for c in Purchase.query.filter_by(usuario_id=current_user.id).all() if c.articulo.clave in PERMANENTES}
                if emoji not in set(AVATARES_LIBRES) | propios:
                    return api_error("Ese avatar no está disponible. Los de colección se consiguen en la tienda.")
            profile.avatar = emoji or None
        db.session.commit()
        return jsonify(user=_user(current_user), **progress(current_user))

    @app.get("/api/avatares/")
    @login_required
    def avatares():
        propios = [c.articulo.icono for c in Purchase.query.filter_by(usuario_id=current_user.id).all() if c.articulo.clave in PERMANENTES]
        return jsonify(libres=AVATARES_LIBRES, coleccion=list(dict.fromkeys(propios)))

    @app.get("/api/progreso/")
    @login_required
    def progreso():
        return jsonify(progress(current_user))

    @app.post("/api/progreso/leccion/")
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

    @app.get("/api/cursos/")
    def cursos():
        course_ids = {row[0] for row in db.session.query(Stage.curso_id).distinct().all()}
        courses = Course.query.filter_by(activo=True).order_by(Course.orden, Course.nombre).all()
        base = db.session.query(Stage.curso_id, func.count(Level.id)).join(Section, Section.etapa_id == Stage.id).join(
            Level, Level.seccion_id == Section.id).filter(Level.tipo == "leccion")
        totals = dict(base.group_by(Stage.curso_id).all())
        done = {}
        if current_user.is_authenticated:
            done = dict(base.join(CompletedLevel, CompletedLevel.nivel_id == Level.id).filter(
                CompletedLevel.usuario_id == current_user.id).group_by(Stage.curso_id).all())
        return jsonify(cursos=[{
            "slug": item.slug, "nombre": item.nombre, "tipo": item.tipo, "sigla": item.sigla,
            "color": item.color, "descripcion": item.descripcion, "tiene_retos": item.id in course_ids,
            "lecciones": totals.get(item.id, 0), "hechas": done.get(item.id, 0),
        } for item in courses])

    @app.get("/api/ruta/")
    @login_required
    def ruta():
        profile = get_profile(current_user)
        course = Course.query.filter_by(slug=request.args.get("curso", ""), activo=True).first() or profile.curso_actual
        if not course:
            return api_error("Elige un curso.", 404)
        completed = {
            entry.nivel_id: entry.estrellas
            for entry in CompletedLevel.query.join(Level).join(Section).join(Stage).filter(
                CompletedLevel.usuario_id == current_user.id, Stage.curso_id == course.id
            ).all()
        }
        marked = False
        stages = []
        for stage in course.etapas:
            sections = []
            for section in stage.secciones:
                levels = []
                for level in section.niveles:
                    if level.id in completed:
                        state = "hecho"
                    elif not marked:
                        state, marked = "actual", True
                    else:
                        state = "bloqueado"
                    levels.append({
                        "id": level.id, "titulo": level.titulo, "tipo": level.tipo, "estado": state,
                        "estrellas": completed.get(level.id, 0), "xp": level.xp,
                    })
                sections.append({"id": section.id, "orden": section.orden, "titulo": section.titulo, "niveles": levels})
            stages.append({
                "id": stage.id, "orden": stage.orden, "titulo": stage.titulo,
                "descripcion": stage.descripcion, "secciones": sections,
            })
        return jsonify(curso={"slug": course.slug, "nombre": course.nombre, "color": course.color}, etapas=stages)

    @app.get("/api/nivel/<int:level_id>/")
    @login_required
    def nivel_detalle(level_id):
        level = db.session.get(Level, level_id)
        if not level or level.tipo not in ("leccion", "practica", "trofeo"):
            return api_error("No encontramos ese nivel.", 404)
        if not allowed_level(current_user, level):
            return api_error("Primero completa los niveles anteriores.", 403)
        challenges = [challenge_item(challenge) for challenge in level_challenges(level)]
        course = level.seccion.etapa.course
        return jsonify(
            nivel={"id": level.id, "titulo": level.titulo, "xp": level.xp, "seccion": level.seccion.titulo,
                   "etapa": level.seccion.etapa.titulo},
            curso={"slug": course.slug, "nombre": course.nombre, "color": course.color},
            retos=challenges, vidas=refresh_lives(get_profile(current_user)),
        )

    @app.post("/api/reto/<int:challenge_id>/responder/")
    @login_required
    def reto_responder(challenge_id):
        challenge = db.session.get(Challenge, challenge_id)
        if not challenge:
            return api_error("No encontramos ese reto.", 404)
        get_profile(current_user)
        profile = Profile.query.filter_by(usuario_id=current_user.id).with_for_update().one()
        refresh_lives(profile)
        if profile.vidas <= 0:
            db.session.commit()
            return api_error("Te quedaste sin vidas.", 403)
        if not allowed_level(current_user, challenge.nivel):
            return api_error("Nivel bloqueado.", 403)
        data = json_body()
        if isinstance(data, tuple):
            return data
        extra = challenge.datos or {}
        if challenge.tipo == "opcion":
            correct, answer = str(data.get("respuesta", "")) == challenge.respuesta, challenge.respuesta
        elif challenge.tipo == "completar":
            accepted = challenge.respuesta.split("|")
            correct = normalize(data.get("respuesta", "")) in {normalize(item) for item in accepted}
            answer = accepted[0]
        elif challenge.tipo == "error":
            correct = str(data.get("respuesta", "")).strip() == challenge.respuesta.strip()
            answer = f"la línea {challenge.respuesta}"
        elif challenge.tipo == "ordenar":
            pieces = extra.get("piezas", [])
            given = data.get("respuesta")
            correct = isinstance(given, list) and [str(item) for item in given] == pieces
            answer = "  →  ".join(pieces)
        else:
            correct, answer = bool(data.get("correcto")), ""
        if not correct:
            lose_life(profile)
        db.session.commit()
        return jsonify(
            correcto=correct, correcta=answer, explicacion=challenge.explicacion, vidas=profile.vidas,
        )

    @app.post("/api/nivel/<int:level_id>/completar/")
    @login_required
    def nivel_completar(level_id):
        level = db.session.get(Level, level_id)
        if not level:
            return api_error("No encontramos ese nivel.", 404)
        if not allowed_level(current_user, level):
            return api_error("Primero completa los niveles anteriores.", 403)
        data = json_body()
        if isinstance(data, tuple):
            return data
        failures = max(0, min(parse_integer(data.get("fallos"), 0), 1000))
        profile = get_profile(current_user)
        chest = level.tipo == "cofre"
        stars = 3 if failures == 0 else 2 if failures <= 2 else 1
        completed = CompletedLevel.query.filter_by(usuario_id=current_user.id, nivel_id=level.id).first()
        new = completed is None
        if new:
            completed = CompletedLevel(usuario_id=current_user.id, nivel_id=level.id, estrellas=stars)
            db.session.add(completed)
            db.session.flush()
        else:
            completed.estrellas = max(completed.estrellas, stars)
            completed.veces += 1
        xp = level.xp if new else (0 if chest else 5)
        rewards = award_xp(profile, xp, levels=0 if chest else 1, perfect=(failures == 0 and not chest))
        minerals = {"diamante": 0}
        if new:
            completed_count = CompletedLevel.query.filter_by(usuario_id=current_user.id).count()
            if completed_count and completed_count % 5 == 0:   # cada cinco niveles nuevos, un diamante
                profile.diamante += 1
                minerals["diamante"] = 1
        db.session.commit()
        return jsonify(
            xp_ganado=xp, minerales_ganados=minerals, estrellas=completed.estrellas, nueva=new,
            desafios_completados=rewards, **progress(current_user),
        )

    @app.get("/api/desafios/")
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
            } for item in DAILY_CHALLENGES],
        )

    @app.get("/api/tienda/")
    @login_required
    def tienda():
        asegurar_articulos()
        profile = get_profile(current_user)
        refresh_lives(profile)
        db.session.commit()
        tuyos = {c.articulo.clave for c in Purchase.query.filter_by(usuario_id=current_user.id).all()} & PERMANENTES
        return jsonify(
            items=[{
                "clave": item.clave, "nombre": item.nombre, "descripcion": item.descripcion,
                "icono": item.icono, "precio": item.precio, "moneda": item.moneda,
                "categoria": item.categoria, "rareza": RAREZA.get(item.clave, "comun"),
                "permanente": item.clave in PERMANENTES, "tuyo": item.clave in tuyos,
            } for item in StoreItem.query.filter_by(activo=True).order_by(StoreItem.orden).all()],
            minerales={"diamante": profile.diamante},
            xp=profile.xp, vidas=profile.vidas, salvarrachas=profile.salvarrachas,
        )

    @app.post("/api/tienda/comprar/")
    @login_required
    def tienda_comprar():
        data = json_body()
        if isinstance(data, tuple):
            return data
        asegurar_articulos()
        item = StoreItem.query.filter_by(clave=str(data.get("clave", "")), activo=True).first()
        if not item:
            return api_error("Ese artículo no existe.", 404)
        get_profile(current_user)
        profile = Profile.query.filter_by(usuario_id=current_user.id).with_for_update().one()
        refresh_lives(profile)
        if profile.diamante < item.precio:
            return api_error("No tienes suficientes diamantes.")
        if item.clave == "vida" and profile.vidas >= MAX_VIDAS:
            return api_error("Ya tienes el máximo de vidas.")
        if item.clave == "vidas_llenas" and profile.vidas >= MAX_VIDAS_REGEN:
            return api_error("Tus vidas ya están llenas.")
        if item.clave == "salvarracha" and profile.salvarrachas >= MAX_SALVARRACHAS:
            return api_error("Ya tienes el máximo de salvarrachas.")
        if item.clave == "kit_experto" and (profile.vidas >= MAX_VIDAS and profile.salvarrachas >= MAX_SALVARRACHAS):
            return api_error("Ya tienes el máximo de vidas y salvarrachas.")
        if item.clave in PERMANENTES and any(c.articulo_id == item.id for c in Purchase.query.filter_by(usuario_id=current_user.id).all()):
            return api_error("Ya tienes este artículo en tu colección.")
        if item.clave == "mega_vidas" and profile.vidas >= MAX_VIDAS:
            return api_error("Ya tienes el máximo de vidas.")
        profile.diamante -= item.precio
        premio = None
        if item.clave == "impulso_xp":
            premio = {"xp": 60}
        elif item.clave == "mega_vidas":
            profile.vidas = MAX_VIDAS
        elif item.clave == "cofre_misterioso":
            premio = random.choice([{"xp": 40}, {"xp": 80}, {"xp": 120}, {"vidas": 2}, {"vidas": 3}, {"diamante": 1}, {"diamante": 3}])
        elif item.clave == "cofre_legendario":
            premio = {"xp": 150, "vidas": 3}
            if random.random() < 0.3:
                premio["diamante"] = 3
        if premio:
            apply_reward(profile, premio)
        if item.clave == "vida":
            profile.vidas += 1
        elif item.clave == "vidas_llenas":
            profile.vidas = MAX_VIDAS_REGEN
        elif item.clave == "salvarracha":
            profile.salvarrachas += 1
        elif item.clave == "kit_experto":
            profile.vidas = min(MAX_VIDAS, profile.vidas + 3)
            profile.salvarrachas = min(MAX_SALVARRACHAS, profile.salvarrachas + 1)
        db.session.add(Purchase(usuario_id=current_user.id, articulo=item, precio=item.precio, moneda="diamante"))
        db.session.commit()
        return jsonify(
            ok=True, minerales={"diamante": profile.diamante},
            xp=profile.xp, vidas=profile.vidas, salvarrachas=profile.salvarrachas,
            premio=reward_text(premio) if premio else None,
        )

    @app.get("/api/amigos/")
    @login_required
    def amigos():
        profile = get_profile(current_user)
        friendships = my_friendships(current_user.id).all()
        friends, received, sent = [], [], []
        for friendship in friendships:
            other = friendship.a_usuario if friendship.de_usuario_id == current_user.id else friendship.de_usuario
            item = {"id": friendship.id, "nombre": other.nombre, "alias": other.profile.alias if other.profile else "",
                    "avatar": (other.profile.avatar or "") if other.profile else ""}
            if friendship.estado == "aceptada":
                last = Message.query.filter_by(amistad_id=friendship.id).order_by(Message.id.desc()).first()
                unread = Message.query.filter(
                    Message.amistad_id == friendship.id, Message.leido.is_(False),
                    Message.autor_id != current_user.id,
                ).count()
                item.update(no_leidos=unread, ultimo=last.texto[:60] if last else "", orden=last.id if last else 0)
                friends.append(item)
            elif friendship.a_usuario_id == current_user.id:
                received.append(item)
            else:
                sent.append(item)
        friends.sort(key=lambda item: -item["orden"])
        return jsonify(
            yo={"nombre": current_user.nombre, "alias": profile.alias, "codigo": profile.codigo, "avatar": profile.avatar or ""},
            amigos=friends, recibidas=received, enviadas=sent,
        )

    @app.get("/api/usuarios/buscar/")
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
            "nombre": p.user.nombre, "alias": p.alias, "avatar": p.avatar or "", "relacion": relacion.get(p.usuario_id),
        } for p in filas if p.alias])

    @app.post("/api/amigos/agregar/")
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

    @app.post("/api/amigos/<int:friendship_id>/responder/")
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

    @app.post("/api/amigos/<int:friendship_id>/quitar/")
    @login_required
    def amigo_quitar(friendship_id):
        friendship = my_friendships(current_user.id).filter_by(id=friendship_id).first()
        if not friendship:
            return api_error("Esa amistad no existe.", 404)
        db.session.delete(friendship)
        db.session.commit()
        return jsonify(ok=True)

    @app.route("/api/chat/<int:friendship_id>/", methods=["GET", "POST"])
    @login_required
    def chat(friendship_id):
        friendship = my_friendships(current_user.id).filter_by(id=friendship_id, estado="aceptada").first()
        if not friendship:
            return api_error("Esa conversación no existe.", 404)
        if request.method == "POST":
            data = json_body()
            if isinstance(data, tuple):
                return data
            text = " ".join(str(data.get("texto", "")).split())
            if not text or len(text) > 300:
                return api_error("Escribe un mensaje de hasta 300 caracteres.")
            if too_many(f"chat:{current_user.id}", 20, 60):
                return api_error("Estás escribiendo muy rápido. Espera un momento.", 429)
            db.session.add(Message(amistad_id=friendship.id, autor_id=current_user.id, texto=text))
            db.session.commit()
        after = parse_integer(request.args.get("despues"), 0)
        query = Message.query.filter_by(amistad_id=friendship.id)
        messages = query.filter(Message.id > after).order_by(Message.id).limit(50).all() if after else query.order_by(Message.id.desc()).limit(50).all()[::-1]
        query.filter(Message.leido.is_(False), Message.autor_id != current_user.id).update(
            {Message.leido: True}, synchronize_session=False,
        )
        db.session.commit()
        return jsonify(mensajes=[{
            "id": message.id, "texto": message.texto, "yo": message.autor_id == current_user.id,
            "hora": local_time(message.creado_en),
        } for message in messages])

    @app.post("/api/tutor/")
    def tutor():
        data = json_body()
        if isinstance(data, tuple):
            return data
        message = str(data.get("mensaje", "")).strip()
        if not message or len(message) > 3500:
            return api_error("Escribe una pregunta de hasta 3500 caracteres.")
        api_key = app.config["GEMINI_API_KEY"]
        if not api_key:
            return api_error("El tutor todavía no está configurado.", 503)
        now = utcnow()
        since = now - timedelta(minutes=1)
        if current_user.is_authenticated:
            used = TutorUsage.query.filter(TutorUsage.usuario_id == current_user.id, TutorUsage.creado_en >= since).count()
            maximum = 20
        else:
            used = TutorUsage.query.filter(
                TutorUsage.usuario_id.is_(None), TutorUsage.ip == client_ip(), TutorUsage.creado_en >= since,
            ).count()
            maximum = 6
        if used >= maximum:
            return api_error("Has hecho muchas preguntas seguidas. Espera un minuto.", 429)
        db.session.add(TutorUsage(usuario_id=current_user.id if current_user.is_authenticated else None, ip=client_ip()))
        db.session.commit()
        history = data.get("historial") if isinstance(data.get("historial"), list) else []
        contents = [{
            "role": "model" if item.get("rol") == "tutor" else "user",
            "parts": [{"text": str(item.get("texto", ""))[:3500]}],
        } for item in history[-10:] if isinstance(item, dict)]
        contents.append({"role": "user", "parts": [{"text": message}]})
        perfil_tutor = get_profile(current_user) if current_user.is_authenticated else None
        contexto = ""
        if perfil_tutor:
            niveles = {"cero": "empieza desde cero", "probado": "ha probado algo", "basico": "sabe lo básico", "avanzado": "tiene experiencia"}
            partes = [f"Se llama {current_user.nombre.split()[0]}."]
            if perfil_tutor.curso_actual:
                partes.append(f"Estudia {perfil_tutor.curso_actual.nombre} en CódigoCamp.")
            if perfil_tutor.nivel_previo in niveles:
                partes.append(f"Su nivel: {niveles[perfil_tutor.nivel_previo]}.")
            contexto = " Datos del alumno: " + " ".join(partes) + " Adapta la explicación a su nivel y usa ejemplos de su curso cuando sea posible."
        system_prompt = (
            "Eres el tutor de CódigoCamp. Responde siempre en español, con frases cortas y amables. "
            "Explica código, corrige errores con su causa y propone un ejercicio pequeño. Ayudas con HTML, CSS, "
            "JavaScript, TypeScript, Python, Java, C, C++, C#, PHP, SQL, Go, Rust, Swift, Kotlin, Ruby y bases de datos. "
            "Si la pregunta no es sobre programación, explica que solo puedes ayudar con eso. No des la solución completa "
            "de un reto sin antes ofrecer una pista. Formato: usa bloques de código con ``` y el nombre del lenguaje, "
            "listas cortas con guiones y evita tablas y títulos largos. Si el alumno quiere hablar con otras personas, "
            "recuérdale que puede agregar amigos en la sección Chats." + contexto
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{app.config['GEMINI_MODEL']}:generateContent"
        payload = json.dumps({"systemInstruction": {"parts": [{"text": system_prompt}]}, "contents": contents,
                              "generationConfig": {"temperature": 0.6, "maxOutputTokens": 1500}}).encode()
        outbound = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        )
        try:
            with urllib.request.urlopen(outbound, timeout=30) as response:
                result = json.load(response)
            answer = "".join(part.get("text", "") for part in result["candidates"][0]["content"]["parts"]).strip()
            if not answer:
                raise ValueError("respuesta vacía")
        except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError):
            app.logger.exception("No se pudo completar la solicitud al tutor de IA.")
            return api_error("El tutor no pudo responder ahora. Inténtalo de nuevo.", 502)
        return jsonify(respuesta=answer)

    # --- Ejecutor de código de la página Aprende (Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin, Ruby) ---
    ejecuciones = {}                       # usuario_id -> marcas de tiempo de las últimas ejecuciones
    cupo = threading.BoundedSemaphore(3)   # máximo 3 programas a la vez en el servidor

    @app.post("/api/run")
    @login_required
    def ejecutar_codigo():
        from ejecutor import ejecutar

        data = json_body()
        if isinstance(data, tuple):
            return data
        ahora = time.monotonic()
        marcas = [t for t in ejecuciones.get(current_user.id, []) if ahora - t < 60]
        if len(marcas) >= 15:
            return api_error("Estás ejecutando muy seguido. Espera un momento.", 429)
        ejecuciones[current_user.id] = marcas + [ahora]
        if not cupo.acquire(timeout=15):
            return api_error("El servidor está ocupado ejecutando otros programas. Inténtalo de nuevo.", 503)
        try:
            return jsonify(ejecutar(str(data.get("lenguaje", "")), data.get("codigo")))
        except ValueError as error:
            return api_error(str(error))
        except Exception:
            app.logger.exception("Falló el ejecutor de código.")
            return api_error("No se pudo ejecutar el código.", 500)
        finally:
            cupo.release()

    return app


def api_error(message, status=400):
    return jsonify(error=message), status


def json_body():
    try:
        data = request.get_json(silent=False)
    except HTTPException:
        return api_error("El cuerpo de la solicitud debe ser JSON válido.")
    if not isinstance(data, dict):
        return api_error("El cuerpo de la solicitud debe ser un objeto JSON.")
    return data


def parse_integer(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def valid_password(password):
    return 6 <= len(password) <= 100 and any(char.isupper() for char in password) and any(char.isdigit() for char in password)


def client_ip():
    return request.remote_addr or "0.0.0.0"


def too_many(key, maximum, seconds):
    now = time.monotonic()
    with _RATE_LOCK:
        recent = [item for item in _RATE_LIMITS.get(key, []) if now - item < seconds]
        _RATE_LIMITS[key] = recent
        if len(recent) >= maximum:
            return True
        recent.append(now)
        return False


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


def _user(user):
    profile = get_profile(user)
    db.session.commit()
    return {
        "id": user.id, "nombre": user.nombre, "email": user.email,
        "onboarding": profile.onboarding_completo, "tema": profile.tema,
        "alias": profile.alias, "codigo": profile.codigo, "avatar": profile.avatar or "",
        "desde": user.creado_en.date().isoformat(),
    }


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
    today = date.today()
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


def asegurar_articulos():
    """Crea en la base los artículos de diamante que falten (una vez por arranque del servidor)."""
    global _ITEMS_LISTOS
    if _ITEMS_LISTOS:
        return
    existentes = {i.clave for i in StoreItem.query.all()}
    for i in StoreItem.query.filter(StoreItem.clave.in_(list(BASICOS_DIAMANTE))).all():   # antes costaban cobre/hierro
        i.moneda, i.categoria, i.precio = "diamante", "diamante", BASICOS_DIAMANTE[i.clave]
    orden = 10
    for a in ARTICULOS_DIAMANTE:
        orden += 1
        if a["clave"] not in existentes:
            db.session.add(StoreItem(clave=a["clave"], nombre=a["nombre"], descripcion=a["descripcion"], icono=a["icono"],
                                     moneda="diamante", precio=a["precio"], categoria="diamante", orden=orden, activo=True))
    try:
        db.session.commit()
        _ITEMS_LISTOS = True
    except Exception:
        db.session.rollback()


def apply_reward(profile, reward):
    for key in ("xp", "diamante"):
        amount = reward.get(key, 0)
        setattr(profile, key, getattr(profile, key) + amount)
        if key == "xp":
            profile.xp_total += amount
    profile.vidas = min(MAX_VIDAS, profile.vidas + reward.get("vidas", 0))


def review_challenges(profile, activity):
    new_rewards = []
    for challenge in DAILY_CHALLENGES:
        if getattr(activity, challenge["campo"]) < challenge["meta"]:
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
        new_rewards.append({"titulo": challenge["titulo"], "premio": reward_text(challenge["premio"])})
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
            new_rewards.append({"titulo": f"Desafío de {MESES[activity.fecha.month - 1]}", "premio": reward_text(month_reward)})
    return new_rewards


def award_xp(profile, amount, levels=0, perfect=False):
    update_streak(profile)
    profile.xp += amount
    profile.xp_total += amount
    today = date.today()
    activity = DailyActivity.query.filter_by(usuario_id=profile.usuario_id, fecha=today).first()
    if not activity:
        activity = DailyActivity(usuario_id=profile.usuario_id, fecha=today, xp=0, niveles=0, perfectos=0)
        db.session.add(activity)
    activity.xp += amount
    activity.niveles += levels
    activity.perfectos += int(perfect)
    db.session.flush()
    return review_challenges(profile, activity)


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
    return item


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


def allowed_level(user, level):
    course = level.seccion.etapa.course
    completed = {
        item[0] for item in db.session.query(CompletedLevel.nivel_id).join(Level).join(Section).join(Stage).filter(
            CompletedLevel.usuario_id == user.id, Stage.curso_id == course.id,
        ).all()
    }
    if level.id in completed:
        return True
    for item in all_levels(course):
        if item.id not in completed:
            return item.id == level.id
    return False


def normalize(value):
    return "".join(str(value).lower().split())


def my_friendships(user_id):
    return Friendship.query.filter(or_(
        Friendship.de_usuario_id == user_id, Friendship.a_usuario_id == user_id,
    ))


def local_time(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone().strftime("%H:%M")


app = create_app()
