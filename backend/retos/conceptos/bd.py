"""Bases de datos: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import bd_e1, bd_e2, bd_e3, bd_e4, bd_e5

ETAPAS_CONCEPTOS = [
    ("Qué es una base de datos", "Teoría para entender dónde y cómo se guardan los datos", bd_e1.LISTA),
    ("Modelado de datos", "Diseña tablas y relaciones antes de crearlas", bd_e2.LISTA),
    ("SQL esencial", "Crea tablas y practica el CRUD con SQL", bd_e3.LISTA),
    ("Consultas avanzadas", "Resume, agrupa y combina datos de varias tablas", bd_e4.LISTA),
    ("Rendimiento y práctica profesional", "Hazlo rápido, seguro y listo para producción", bd_e5.LISTA),
]
