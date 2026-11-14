"""SQL: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import sql_e1, sql_e2, sql_e3, sql_e4, sql_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con consultas", "Lee, filtra y ordena datos con SELECT", sql_e1.LISTA),
    ("Funciones y resúmenes", "Calcula, transforma textos y agrupa datos", sql_e2.LISTA),
    ("Crear tablas y modificar datos", "Define tablas, restricciones y cambia datos con seguridad", sql_e3.LISTA),
    ("Unir tablas y subconsultas", "Combina tablas y consultas para responder preguntas más completas", sql_e4.LISTA),
    ("Rendimiento y práctica profesional", "Índices, ventanas, seguridad y buenas prácticas", sql_e5.LISTA),
]
