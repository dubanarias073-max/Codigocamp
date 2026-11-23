"""Retos de React Native: 5 etapas × 20 secciones. Los conceptos están en conceptos/reactnative.py."""
from .conceptos.reactnative import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
