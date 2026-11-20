"""Retos de git. Los conceptos están en conceptos/git.py."""
from .conceptos.git import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
