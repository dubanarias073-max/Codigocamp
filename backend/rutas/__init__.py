"""Rutas de la API y del frontend. Cada archivo es un Blueprint de Flask con un tema."""
from rutas import adjuntos, amigos, archivos, auth, bd, conversaciones, cosmeticos, github, gitproxy, chat, ejecucion, frontend, perfil, progreso, retos, tienda, trabajo, trabajored, tutor

BLUEPRINTS = (auth, perfil, progreso, retos, tienda, amigos, chat, trabajo, trabajored, archivos, adjuntos, bd, gitproxy, github, cosmeticos, conversaciones, tutor, ejecucion, frontend)


def registrar_rutas(app):
    """Registra todos los Blueprints. `frontend` va al final porque tiene la ruta comodín /<archivo>."""
    for modulo in BLUEPRINTS:
        app.register_blueprint(modulo.bp)
