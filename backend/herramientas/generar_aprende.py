"""Crea las lecciones de Aprende (frontend/js/lecciones/<lenguaje>.js) a partir de los conceptos de retos/conceptos/.

Uso (desde la carpeta backend):
    python herramientas/generar_aprende.py            # todos los lenguajes que tengan conceptos
    python herramientas/generar_aprende.py html css   # solo esos
"""
import json, os, subprocess, tempfile
import sys
from importlib import import_module
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from retos.generador import lecciones_aprende  # noqa: E402

DESTINO = RAIZ.parent / "frontend" / "js" / "lecciones"
TODOS = [
    "html", "css", "bd", "javascript", "python", "sql", "typescript", "c", "cpp", "java", "csharp",
    "go", "kotlin", "php", "ruby", "rust", "swift",
]
SALIDA_SRV = {"c", "cpp", "java", "csharp", "php", "go", "rust", "swift", "kotlin", "ruby"}   # lenguajes que muestran la salida esperada


SALIDAS = DESTINO / "salidas.js"
COMPILADOR = {"c": ("gcc", ".c", ["-std=c11", "-Wall", "-lm"]), "cpp": ("g++", ".cpp", ["-std=c++17", "-Wall"])}


def _salida(slug, c):
    """Salida esperada de un ejemplo: C y C++ se compilan y ejecutan; el resto usa el campo out."""
    if slug not in COMPILADOR:
        if c["out"] is None:
            raise SystemExit(f"FALTA out=... (salida esperada) en el concepto «{c['t']}» de {slug}")
        return c["out"]
    cc, ext, flags = COMPILADOR[slug]
    with tempfile.TemporaryDirectory() as d:
        src, exe = os.path.join(d, "p" + ext), os.path.join(d, "p")
        open(src, "w", encoding="utf-8").write(c["cod"])
        r = subprocess.run([cc, src, "-o", exe] + flags, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"NO COMPILA «{c['t']}»:\n{r.stderr}")
        r = subprocess.run([exe], capture_output=True, text=True, cwd=d, timeout=10)
        return (r.stdout).rstrip("\n")


def escribir_salidas(slug, datos):
    texto = SALIDAS.read_text(encoding="utf-8")
    cab, cuerpo = texto.split("export default", 1)
    obj = json.loads(cuerpo.strip().rstrip(";"))
    obj[slug] = [_salida(slug, c) for _, _, lista in datos for c in lista]
    SALIDAS.write_text(cab + "export default " + json.dumps(obj, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")


def escribir(slug):
    datos = import_module(f"retos.conceptos.{slug}").ETAPAS_CONCEPTOS
    lecciones = lecciones_aprende(datos, editable=slug != "bd")   # bd solo se muestra: no se ejecuta
    cuerpo = ",\n".join("  " + json.dumps(l, ensure_ascii=False) for l in lecciones)
    (DESTINO / f"{slug}.js").write_text(
        "// GENERADO por backend/herramientas/generar_aprende.py a partir de backend/retos/conceptos/"
        f"{slug}.py. No lo edites a mano: cambia los conceptos y vuelve a generarlo.\n"
        "// m = etapa · t = título · x = qué es · u = para qué sirve · p = puntos clave · c = código · h = qué hace · r = ahora tú · e = error común\n"
        f"export default [\n{cuerpo}\n];\n", encoding="utf-8")
    if slug in SALIDA_SRV:
        escribir_salidas(slug, datos)
    print(f"{slug}: {len(lecciones)} lecciones")


if __name__ == "__main__":
    for s in (sys.argv[1:] or TODOS):
        escribir(s)
