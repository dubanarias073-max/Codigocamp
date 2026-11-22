"""Retos de React: 5 etapas × 20 secciones. Los conceptos están en conceptos/react_e*.py."""
from .conceptos.react import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
