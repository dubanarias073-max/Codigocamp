"""C++: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import cpp_e1, cpp_e2, cpp_e3, cpp_e4, cpp_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con C++", "Compilar, mostrar datos, tipos y decisiones", cpp_e1.LISTA),
    ("Bucles, funciones y contenedores", "Repetir, reutilizar código y manejar colecciones", cpp_e2.LISTA),
    ("Programación orientada a objetos", "Clases, herencia y polimorfismo", cpp_e3.LISTA),
    ("Memoria, plantillas y excepciones", "Punteros inteligentes, genéricos, errores y archivos", cpp_e4.LISTA),
    ("C++ moderno y profesional", "Herramientas modernas, concurrencia y buenas prácticas", cpp_e5.LISTA),
]
