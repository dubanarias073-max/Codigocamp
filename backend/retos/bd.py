"""Retos de Bases de datos: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/bd_e*.py."""
from .conceptos.bd import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
