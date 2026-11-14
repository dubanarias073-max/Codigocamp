"""C#: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import cs_e1, cs_e2, cs_e3, cs_e4, cs_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con C#", "Compilar, mostrar datos, tipos y decisiones", cs_e1.LISTA),
    ("Bucles, métodos y colecciones básicas", "Repetir, reutilizar código y manejar arrays, listas y diccionarios", cs_e2.LISTA),
    ("Programación orientada a objetos", "Clases, propiedades, herencia e interfaces", cs_e3.LISTA),
    ("Excepciones, genéricos y LINQ", "Errores controlados, tipos genéricos, lambdas y consultas", cs_e4.LISTA),
    ("C# moderno y profesional", "Asincronía, hilos, archivos, herramientas y buenas prácticas", cs_e5.LISTA),
]
