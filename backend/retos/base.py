"""Piezas comunes para escribir los retos de cada lenguaje.

Estructura (como Duolingo):

    curso (un archivo .py por lenguaje: html.py, css.py, python.py...)
      └─ etapa      "Primeros pasos", "Fundamentos"...   -> tabla `etapas`
           └─ sección  "Estructura de la página"         -> tabla `secciones`
                └─ lección  "Tu primera página"          -> tabla `niveles`
                     └─ pregunta (unas 10 por lección)   -> tabla `retos`

Cómo se escribe (ejemplo mínimo):

    ETAPAS = [
        etapa("Primeros pasos", "Lo básico para empezar",
            seccion("Estructura",
                leccion("Tu primera página",
                    O("¿Qué etiqueta contiene lo visible?", "<body>", "<head>", "<title>"),
                    C("¿Qué etiqueta crea un párrafo? (sin < >)", "p"),
                ),
            ),
        ),
    ]
"""

XP_ETAPA = [15, 20, 25, 30, 35]   # cada etapa da más XP que la anterior
PREGUNTAS_POR_LECCION = 4          # mínimo recomendado (antes 10); `flask check-retos` avisa si una lección se aleja


def _reto(tipo, enunciado, opciones, respuesta, codigo="", explicacion="", datos=None):
    return {"tipo": tipo, "enunciado": enunciado, "codigo": codigo, "opciones": opciones,
            "respuesta": respuesta, "explicacion": explicacion, "datos": datos or {}}


def O(pregunta, correcta, *falsas, codigo="", explicacion=""):
    """Elegir una opción. La primera es la correcta; el servidor baraja el orden."""
    return _reto("opcion", pregunta, [correcta, *falsas], correcta, codigo, explicacion)


def C(pregunta, *validas, codigo="", explicacion=""):
    """Escribir la respuesta. Se aceptan varias respuestas válidas (sin importar mayúsculas ni espacios)."""
    return _reto("completar", pregunta, [], "|".join(validas), codigo, explicacion)


def E(pregunta, codigo, linea, explicacion=""):
    """Encontrar la línea con el error (la línea se cuenta desde 1)."""
    return _reto("error", pregunta, [], str(linea), codigo, explicacion)


def ORD(pregunta, *piezas, explicacion=""):
    """Ordenar piezas: se escriben en el orden CORRECTO; el servidor las baraja."""
    return _reto("ordenar", pregunta, [], "", "", explicacion, {"piezas": list(piezas)})


def reto(**campos):
    """Pregunta con todos los campos a mano (tipos 'codigo' y 'caso', que llevan datos extra)."""
    return _reto(campos["tipo"], campos["enunciado"], campos.get("opciones", []), campos.get("respuesta", ""),
                 campos.get("codigo", ""), campos.get("explicacion", ""), campos.get("datos"))


def leccion(titulo, *preguntas):
    return {"titulo": titulo, "retos": list(preguntas)}


def seccion(titulo, *lecciones):
    return {"titulo": titulo, "lecciones": list(lecciones)}


def etapa(titulo, descripcion, *secciones):
    return {"titulo": titulo, "descripcion": descripcion, "secciones": list(secciones)}
