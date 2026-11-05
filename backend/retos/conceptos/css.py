"""CSS: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import css_e1, css_e2, css_e3, css_e4, css_e5

ETAPAS_CONCEPTOS = [
    ("Qué es CSS", "Teoría para entender cómo se da estilo a una página", css_e1.LISTA),
    ("Selectores, texto y color", "Elige qué estilar y da formato al texto", css_e2.LISTA),
    ("La caja, el espacio y la posición", "Controla el tamaño, la separación y la colocación de cada elemento", css_e3.LISTA),
    ("Flexbox y Grid", "Organiza el diseño de la página con fila, columna y cuadrícula", css_e4.LISTA),
    ("Responsive y efectos", "Adapta la página a cualquier pantalla y añade movimiento", css_e5.LISTA),
]
