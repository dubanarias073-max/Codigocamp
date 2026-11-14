"""Retos de C: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/c.py."""
from .conceptos.c import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
