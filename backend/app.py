"""CódigoCamp · servidor Flask.

Este archivo solo arma la app: configuración, base de datos, seguridad, comandos y rutas.
La lógica está repartida en:  rutas/ (API por tema), servicios/ (reglas del juego),
models.py (tablas), constantes.py, utilidades.py, seguridad.py y comandos.py.
"""
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
    configurar_seguridad(app)
    from rutas.auth import configurar_google
    configurar_google(app)
    registrar_comandos(app)
    registrar_rutas(app)
    return app


app = create_app()
