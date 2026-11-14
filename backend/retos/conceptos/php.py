"""PHP: cinco etapas con veinte conceptos cada una."""
from . import php_e1, php_e2, php_e3, php_e4, php_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos", "Empieza con PHP, su sintaxis, variables y valores", php_e1.LISTA),
    ("Decisiones y bucles", "Compara valores, elige caminos y repite instrucciones", php_e2.LISTA),
    ("Arreglos y funciones", "Organiza colecciones y crea operaciones reutilizables", php_e3.LISTA),
    ("Formularios y objetos", "Modela datos, clases y relaciones entre tipos", php_e4.LISTA),
    ("PHP moderno", "Valida datos y conoce recursos avanzados de PHP 8", php_e5.LISTA),
]
