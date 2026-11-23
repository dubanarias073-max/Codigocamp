"""Kotlin: cinco etapas con veinte conceptos cada una."""
from . import kotlin_e1, kotlin_e2, kotlin_e3, kotlin_e4, kotlin_e5

ETAPAS_CONCEPTOS = [
    ("Fundamentos de Kotlin", "Conoce el lenguaje, sus valores y expresiones", kotlin_e1.LISTA),
    ("Decisiones y funciones", "Controla el flujo y organiza operaciones reutilizables", kotlin_e2.LISTA),
    ("Funciones y colecciones", "Trabaja con abstracciones, datos agrupados y transformaciones", kotlin_e3.LISTA),
    ("Clases y seguridad de tipos", "Modela objetos y controla valores ausentes con null safety", kotlin_e4.LISTA),
    ("Kotlin avanzado y herramientas", "Aplica abstracciones avanzadas y comprende el entorno de construcción", kotlin_e5.LISTA),
]

from .kotlin_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
