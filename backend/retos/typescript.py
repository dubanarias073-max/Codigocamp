"""Retos de TypeScript: 5 etapas × 20 secciones × 4 lecciones. Los conceptos están en conceptos/typescript.py."""
from .conceptos.typescript import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
