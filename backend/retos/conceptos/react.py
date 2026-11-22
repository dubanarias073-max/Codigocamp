"""React: las 5 etapas con sus 20 conceptos cada una (un concepto = una sección del camino)."""
from . import react_e1, react_e2, react_e3, react_e4, react_e5

ETAPAS_CONCEPTOS = [
    ("Primeros pasos con React", "Componentes, JSX, props y listas", react_e1.LISTA),
    ("Estado e interacción", "useState, formularios y eventos", react_e2.LISTA),
    ("Efectos y hooks", "useEffect, refs, Context, useReducer y hooks propios", react_e3.LISTA),
    ("Rutas, datos y estilos", "React Router, APIs, estilos y carga diferida", react_e4.LISTA),
    ("React profesional", "TypeScript, pruebas, estado global, Next.js y despliegue", react_e5.LISTA),
]
