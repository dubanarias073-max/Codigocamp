"""Retos de R generados a partir de sus 60 conceptos."""
from .conceptos.r import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
