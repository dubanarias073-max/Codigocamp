"""C: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import c_e1, c_e2, c_e3, c_e4, c_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con C", "Compilar, mostrar datos, variables y decisiones", c_e1.LISTA),
    ("Bucles, funciones y arrays", "Repetir, reutilizar código y manejar listas y texto", c_e2.LISTA),
    ("Punteros y memoria", "Direcciones, memoria dinámica y sus peligros", c_e3.LISTA),
    ("Estructuras, bits y archivos", "Tipos propios, operaciones de bajo nivel y ficheros", c_e4.LISTA),
    ("C profesional", "Proyectos en varios archivos, herramientas y algoritmos", c_e5.LISTA),
]
