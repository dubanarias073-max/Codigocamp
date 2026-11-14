"""Retos de C#: 5 etapas × 20 secciones × 4 lecciones. Los conceptos están en conceptos/csharp.py."""
from .conceptos.csharp import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
