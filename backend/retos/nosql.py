"""Retos de nosql. Los conceptos están en conceptos/nosql.py."""
from .conceptos.nosql import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
