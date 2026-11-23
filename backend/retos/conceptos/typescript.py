"""TypeScript: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import ts_e1, ts_e2, ts_e3, ts_e4, ts_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con TypeScript", "Tipos básicos, variables y control de flujo", ts_e1.LISTA),
    ("Funciones, objetos e interfaces", "Describe funciones y datos con tipos precisos", ts_e2.LISTA),
    ("Clases y módulos", "Programación orientada a objetos y organización en archivos", ts_e3.LISTA),
    ("Genéricos y tipos avanzados", "Tipos reutilizables, utilitarios y transformaciones", ts_e4.LISTA),
    ("TypeScript profesional", "Configuración, asincronía, herramientas y buenas prácticas", ts_e5.LISTA),
]

from .typescript_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
