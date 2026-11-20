"""Retos de node. Los conceptos están en conceptos/node.py."""
from .conceptos.node import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
