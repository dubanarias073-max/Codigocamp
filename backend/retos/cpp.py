"""Retos de C++: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/cpp.py."""
from .conceptos.cpp import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
