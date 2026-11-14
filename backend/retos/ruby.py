"""Retos de Ruby generados a partir de sus 100 conceptos."""
from .conceptos.ruby import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
