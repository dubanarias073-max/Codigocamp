"""Go: cinco etapas con veinte conceptos cada una."""
from . import go_e1, go_e2, go_e3, go_e4, go_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con Go", "Escribe tu primer programa y aprende los tipos y declaraciones básicos", go_e1.LISTA),
    ("Expresiones y control de flujo", "Realiza cálculos, toma decisiones y repite instrucciones", go_e2.LISTA),
    ("Funciones y colecciones", "Organiza operaciones reutilizables y agrupa datos", go_e3.LISTA),
    ("Tipos, interfaces y errores", "Modela datos y comportamientos con tipos propios", go_e4.LISTA),
    ("Concurrencia y herramientas", "Coordina tareas y aprovecha las herramientas modernas de Go", go_e5.LISTA),
]

from .go_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
