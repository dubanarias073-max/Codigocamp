"""Retos de CSS: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/css_e*.py."""
from .conceptos.css import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
