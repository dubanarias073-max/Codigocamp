"""Rutas de la API y del frontend. Cada archivo es un Blueprint de Flask con un tema."""
from rutas import amigos, auth, chat, ejecucion, frontend, perfil, progreso, retos, tienda, trabajo, tutor

BLUEPRINTS = (auth, perfil, progreso, retos, tienda, amigos, chat, trabajo, tutor, ejecucion, frontend)


def registrar_rutas(app):
    """Registra todos los Blueprints. `frontend` va al final porque tiene la ruta comodín /<archivo>."""
    for modulo in BLUEPRINTS:
        app.register_blueprint(modulo.bp)
