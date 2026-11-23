"""Rust: cinco etapas con veinte conceptos cada una."""
from . import rust_e1, rust_e2, rust_e3, rust_e4, rust_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos", "Conoce Rust, sus vinculaciones y los tipos básicos", rust_e1.LISTA),
    ("Decisiones y bucles", "Controla el flujo y representa alternativas", rust_e2.LISTA),
    ("Funciones y colecciones", "Organiza operaciones y procesa secuencias", rust_e3.LISTA),
    ("Propiedad y estructuras", "Comprende préstamos y crea tipos propios", rust_e4.LISTA),
    ("Errores y abstracciones", "Maneja fallos y usa herramientas avanzadas", rust_e5.LISTA),
]

from .rust_ref import ETAPAS_REF as _REF
ETAPAS_CONCEPTOS = ETAPAS_CONCEPTOS + _REF   # etapas de referencia: más temas del curso
