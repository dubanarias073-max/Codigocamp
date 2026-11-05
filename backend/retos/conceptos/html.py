"""HTML: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import html_e1, html_e2, html_e3, html_e4, html_e5

ETAPAS_CONCEPTOS = [
    ("La web y qué es HTML", "Teoría para entender dónde vive tu código", html_e1.LISTA),
    ("Estructura y texto", "Cómo se arma una página y cómo se escribe el texto", html_e2.LISTA),
    ("Enlaces, imágenes y multimedia", "Conecta páginas y añade imágenes, video y audio", html_e3.LISTA),
    ("Tablas y formularios", "Organiza datos y pide información a quien visita tu sitio", html_e4.LISTA),
    ("Semántica y buenas prácticas", "Escribe HTML ordenado, accesible y listo para publicar", html_e5.LISTA),
]
