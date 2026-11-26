"""Retos de Lua generados a partir de sus 60 conceptos."""
from .conceptos.lua import ETAPAS_CONCEPTOS
from .generador import construir_etapas

ETAPAS = construir_etapas(ETAPAS_CONCEPTOS)
