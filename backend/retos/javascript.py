"""Retos de JavaScript: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/js_e*.py."""
from .conceptos.javascript import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
