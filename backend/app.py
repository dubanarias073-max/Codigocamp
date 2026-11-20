"""CódigoCamp · servidor Flask.

Este archivo solo arma la app: configuración, base de datos, seguridad, comandos y rutas.
La lógica está repartida en:  rutas/ (API por tema), servicios/ (reglas del juego),
models.py (tablas), constantes.py, utilidades.py, seguridad.py y comandos.py.
"""
import mimetypes
import os
from datetime import timedelta
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask

from constantes import BACKEND
from models import db

load_dotenv(BACKEND / ".env")   # lee backend/.env antes de configurar la app

from comandos import registrar_comandos  # noqa: E402
from rutas import registrar_rutas  # noqa: E402
from seguridad import configurar_seguridad  # noqa: E402


def _crear_tablas_nuevas(app):
    """Crea las tablas que agregan las versiones nuevas si la base aún no las tiene (no toca las que ya existen).
    Así no hace falta ejecutar a mano migracion_archivos.sql. Si MySQL no está encendido, se intentará al reiniciar."""
    from models import AIConversation, AIMessage, AppliedMigration, Attachment, UserSession, EmailSettings, EquippedCosmetics, KnownDevice, OpenedChest, OwnedCosmetic, ProfilePhoto, WorkspaceFile
    try:
        with app.app_context():
            from servicios.workbench import reparar
            cambios = reparar(db.engine)
            if cambios:
                app.logger.info("Base ajustada para el diagrama de MySQL Workbench: %s", "; ".join(cambios))
            nuevos = (WorkspaceFile, KnownDevice, EmailSettings, OwnedCosmetic, EquippedCosmetics, OpenedChest, ProfilePhoto, Attachment, AppliedMigration, UserSession, AIConversation, AIMessage)
            for modelo in nuevos:
                modelo.__table__.create(bind=db.engine, checkfirst=True)
            from servicios.workbench import agregar_columnas
            agregadas = agregar_columnas(db.engine, nuevos)
            if agregadas:
                app.logger.info("Columnas nuevas agregadas: %s", ", ".join(agregadas))
            from servicios.workbench import migraciones_de_datos
            for hecha in migraciones_de_datos(db):
                app.logger.info("Migración aplicada: %s", hecha)
    except Exception as error:  # noqa: BLE001 - solo se avisa; la app debe arrancar igual
        app.logger.warning("No se pudieron comprobar las tablas nuevas: %s", error)


mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/wasm", ".wasm")


def create_app(test_config=None):
    app = Flask(__name__)
    # Detrás de un túnel o proxy (Tailscale Funnel, Nginx, Cloudflare): PROXY_CONFIABLE=1 hace que la IP real de cada
    # persona y el https lleguen a Flask (límites de intentos por persona, enlaces correctos). Sin proxy, déjalo en 0.
    proxies = int(os.getenv("PROXY_CONFIABLE", "0") or 0)
    if proxies > 0:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxies, x_proto=proxies, x_host=proxies)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY") or ("solo-desarrollo-cambiame" if os.getenv("DEBUG", "1") == "1" else None),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("DEBUG", "1") != "1",
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", "").strip().strip('"'),
        GEMINI_MODEL=(os.getenv("GEMINI_MODEL") or "gemini-3.8-flash").strip(),
        GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID", ""),
        GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI", ""),
        # Archivos del espacio de Trabajo (imágenes, videos, PDF…): se guardan en disco, no en MySQL.
        ALMACEN_ARCHIVOS=os.getenv("ALMACEN_ARCHIVOS") or str(BACKEND / "almacen_archivos"),
        CUOTA_ARCHIVOS=int(float(os.getenv("CUOTA_ARCHIVOS_GB", "10")) * 1024 ** 3),
        MAX_ARCHIVO=int(float(os.getenv("MAX_ARCHIVO_MB", "1024")) * 1024 ** 2),
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
    if not app.config.get("TESTING"):
        _crear_tablas_nuevas(app)
    configurar_seguridad(app)
    from rutas.auth import configurar_google
    configurar_google(app)
    registrar_comandos(app)
    from servicios.correo import iniciar_programador
    iniciar_programador(app)
    registrar_rutas(app)
    return app


app = create_app()
