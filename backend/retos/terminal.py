"""Retos de terminal. Los conceptos están en conceptos/terminal.py."""
from .conceptos.terminal import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
