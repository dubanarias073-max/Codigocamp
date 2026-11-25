"""Piezas comunes para escribir los retos de cada lenguaje.

Estructura (como Duolingo):

    curso (un archivo .py por lenguaje: html.py, css.py, python.py...)
      └─ etapa      "Primeros pasos", "Fundamentos"...   -> tabla `etapas`
           └─ sección  "Estructura de la página"         -> tabla `secciones`
                └─ lección  "Tu primera página"          -> tabla `niveles`
                     └─ pregunta (4 o más por lección)    -> tabla `retos`

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
import re

XP_ETAPA = [15, 18, 20, 23, 25, 28, 30, 33, 35, 38, 40]   # cada etapa da más XP que la anterior
PREGUNTAS_POR_LECCION = 3          # mínimo validado; ninguna pregunta se repite en el curso, así que las lecciones son cortas


def _reto(tipo, enunciado, opciones, respuesta, codigo="", explicacion="", datos=None):
    return {"tipo": tipo, "enunciado": enunciado, "codigo": codigo, "opciones": opciones,
            "respuesta": respuesta, "explicacion": explicacion, "datos": datos or {}}


def O(pregunta, correcta, *falsas, codigo="", explicacion=""):
    """Elegir una opción. La primera es la correcta; el servidor baraja el orden."""
    if not explicacion:
        explicacion = f"La respuesta correcta es «{correcta}»."
    return _reto("opcion", pregunta, [correcta, *falsas], correcta, codigo, explicacion)


def C(pregunta, *validas, codigo="", explicacion=""):
    """Escribir la respuesta. Se aceptan varias respuestas válidas (sin importar mayúsculas ni espacios)."""
    if not explicacion and validas:
        if "___" in pregunta:
            frase = re.sub(r"\s*\([^()]*\)\s*$", "", pregunta)
            explicacion = f"La frase completa es: «{re.sub(r'_{2,}', lambda _m: validas[0], frase, count=1).strip().rstrip('.')}»."
        else:
            explicacion = f"La respuesta es «{validas[0]}»."
    return _reto("completar", pregunta, [], "|".join(validas), codigo, explicacion)


def E(pregunta, codigo, linea, explicacion=""):
    """Encontrar la línea con el error (la línea se cuenta desde 1)."""
    if not explicacion:
        explicacion = f"El error está en la línea {linea}."
    return _reto("error", pregunta, [], str(linea), codigo, explicacion)


def ORD(pregunta, *piezas, explicacion=""):
    """Ordenar piezas: se escriben en el orden CORRECTO; el servidor las baraja."""
    if not explicacion:
        explicacion = "Las piezas están ordenadas para formar el código correcto."
    return _reto("ordenar", pregunta, [], "", "", explicacion, {"piezas": list(piezas)})


def PAR(pregunta, pares, explicacion=""):
    """Unir parejas (como en Duolingo): [(izquierda, derecha), ...]. El servidor baraja las dos columnas."""
    pares = [[str(a), str(b)] for a, b in pares]
    if not explicacion:
        explicacion = "Las parejas son: " + "; ".join(f"{a} → {b}" for a, b in pares) + "."
    return _reto("parejas", pregunta, [], "", "", explicacion, {"pares": pares})


def ARM(pregunta, codigo, solucion, trampas=(), explicacion=""):
    """Armar una línea con fichas (como el banco de palabras de Duolingo). `solucion`: fichas en orden;
    `trampas`: fichas que sobran. El código se muestra con la línea que falta marcada con ▁▁▁."""
    solucion = [str(x) for x in solucion]
    if not explicacion:
        explicacion = f"La línea completa es: {' '.join(solucion)}"
    return _reto("armar", pregunta, [], " ".join(solucion), codigo, explicacion,
                 {"solucion": solucion, "trampas": [str(x) for x in trampas]})


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
