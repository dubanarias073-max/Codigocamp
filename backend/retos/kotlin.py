"""Retos de Kotlin generados a partir de sus 100 conceptos."""
from .conceptos.kotlin import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
