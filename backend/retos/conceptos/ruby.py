"""Ruby: cinco etapas con veinte conceptos cada una."""
from . import ruby_e1, ruby_e2, ruby_e3, ruby_e4, ruby_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con Ruby", "Conoce Ruby, sus valores y expresiones básicas", ruby_e1.LISTA),
    ("Decisiones y colecciones", "Controla el flujo y organiza datos en colecciones", ruby_e2.LISTA),
    ("Métodos y control", "Crea métodos, trabaja con bloques y controla repeticiones", ruby_e3.LISTA),
    ("Objetos y módulos", "Modela objetos con clases, bloques y módulos reutilizables", ruby_e4.LISTA),
    ("Ruby avanzado y errores", "Usa herramientas modernas y maneja fallos con cuidado", ruby_e5.LISTA),
]

from .ruby_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
