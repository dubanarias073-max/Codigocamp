"""Retos de github. Los conceptos están en conceptos/github.py."""
from .conceptos.github import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
