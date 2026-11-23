"""Swift: cinco etapas con veinte conceptos cada una."""
from . import swift_e1, swift_e2, swift_e3, swift_e4, swift_e5

ETAPAS_CONCEPTOS = [
    ("Fundamentos de Swift", "Aprende el lenguaje, sus valores y expresiones básicas", swift_e1.LISTA),
    ("Control y funciones", "Dirige el flujo y organiza operaciones en tipos", swift_e2.LISTA),
    ("Funciones y colecciones", "Trabaja con colecciones y diseña tipos propios", swift_e3.LISTA),
    ("Opcionales y abstracciones", "Modela ausencia de datos y crea abstracciones seguras", swift_e4.LISTA),
    ("Swift avanzado y herramientas", "Explora memoria, concurrencia y herramientas del ecosistema", swift_e5.LISTA),
]

from .swift_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
