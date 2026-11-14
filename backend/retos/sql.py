"""Retos de SQL: 5 etapas × 20 secciones × 5 lecciones. Los conceptos están en conceptos/sql_e*.py."""
from .conceptos.sql import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS, repaso=False)
