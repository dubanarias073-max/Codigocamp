"""Retos de HTML: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/html_e*.py."""
from .conceptos.html import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
