"""Retos de docker. Los conceptos están en conceptos/docker.py."""
from .conceptos.docker import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
