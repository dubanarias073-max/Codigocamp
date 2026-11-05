"""JavaScript: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import js_e1, js_e2, js_e3, js_e4, js_e5

ETAPAS_CONCEPTOS = [
    ("Qué es JavaScript", "Teoría para entender qué hace y dónde corre", js_e1.LISTA),
    ("Variables, tipos y operadores", "Guarda datos y haz cálculos y comparaciones", js_e2.LISTA),
    ("Decisiones, bucles y funciones", "Haz que el programa decida, repita y se organice", js_e3.LISTA),
    ("Arrays y objetos", "Maneja listas y datos estructurados", js_e4.LISTA),
    ("DOM, eventos y asincronía", "Haz páginas interactivas que hablan con servidores", js_e5.LISTA),
]
