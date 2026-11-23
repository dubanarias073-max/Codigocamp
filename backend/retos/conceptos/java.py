"""Java: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import java_e1, java_e2, java_e3, java_e4, java_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con Java", "Compilar, mostrar datos, tipos y decisiones", java_e1.LISTA),
    ("Bucles, métodos y colecciones básicas", "Repetir, reutilizar código y manejar arrays, listas y mapas", java_e2.LISTA),
    ("Programación orientada a objetos", "Clases, herencia, interfaces y polimorfismo", java_e3.LISTA),
    ("Excepciones, genéricos y colecciones", "Errores controlados, tipos genéricos, lambdas y streams", java_e4.LISTA),
    ("Java moderno y profesional", "Hilos, fechas, archivos, herramientas y buenas prácticas", java_e5.LISTA),
]

from .java_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
