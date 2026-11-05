"""Crea las lecciones de Aprende (frontend/js/lecciones/<lenguaje>.js) a partir de los conceptos de retos/conceptos/.

Uso (desde la carpeta backend):
    python herramientas/generar_aprende.py            # todos los lenguajes que tengan conceptos
    python herramientas/generar_aprende.py html css   # solo esos
"""
import json
import sys
from importlib import import_module
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from retos.generador import lecciones_aprende  # noqa: E402

DESTINO = RAIZ.parent / "frontend" / "js" / "lecciones"
TODOS = ["html", "css", "bd", "javascript", "python"]


def escribir(slug):
    datos = import_module(f"retos.conceptos.{slug}").ETAPAS_CONCEPTOS
    lecciones = lecciones_aprende(datos, editable=slug != "bd")   # bd solo se muestra: no se ejecuta
    cuerpo = ",\n".join("  " + json.dumps(l, ensure_ascii=False) for l in lecciones)
    (DESTINO / f"{slug}.js").write_text(
        "// GENERADO por backend/herramientas/generar_aprende.py a partir de backend/retos/conceptos/"
        f"{slug}.py. No lo edites a mano: cambia los conceptos y vuelve a generarlo.\n"
        "// m = etapa · t = título · x = qué es · u = para qué sirve · p = puntos clave · c = código · h = qué hace · r = ahora tú · e = error común\n"
        f"export default [\n{cuerpo}\n];\n", encoding="utf-8")
    print(f"{slug}: {len(lecciones)} lecciones")


if __name__ == "__main__":
    for s in (sys.argv[1:] or TODOS):
        escribir(s)
