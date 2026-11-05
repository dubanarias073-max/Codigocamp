"""Retos de Python: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/py_e*.py."""
from .conceptos.python import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
