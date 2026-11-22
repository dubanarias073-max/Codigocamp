"""Python con pip de verdad en el servidor, para los paquetes que el navegador (Pyodide) no puede instalar:
los que traen código en C sin versión para el navegador (mysqlclient, psycopg2, opencv, tensorflow…).

Cada usuario tiene su propio entorno virtual en PYTHON_VENVS_DIR (por defecto <tmp>/codigocamp_venvs/u<id>).
Trabajo instala ahí solo lo que falló en el navegador, y ejecuta en el servidor los programas que lo importan.
Se apaga con PYTHON_SERVIDOR=0.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading

from servicios.ejecutor import ES_WINDOWS, _correr, _limpiar, CACHE

VENVS = os.getenv("PYTHON_VENVS_DIR") or os.path.join(tempfile.gettempdir(), "codigocamp_venvs")
TIEMPO_PIP = int(os.getenv("PYTHON_PIP_TIEMPO", "900"))     # segundos para un pip install (tensorflow tarda)
TIEMPO_RUN = int(os.getenv("PYTHON_RUN_TIEMPO", "40"))      # segundos para ejecutar un programa
MAX_PAQUETES = 40
MAX_ARCHIVOS = 80
MAX_TOTAL = 2_000_000           # caracteres de todos los archivos del proyecto juntos
MAX_SALIDA = 20_000

ESPEC = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?"                 # nombre de PyPI
    r"(?:\[[A-Za-z0-9._-]+(?:,[A-Za-z0-9._-]+)*\])?"                # extras: paquete[extra1,extra2]
    r"(?:(?:==|>=|<=|~=|!=|<|>)[A-Za-z0-9.*+!_-]+"                  # versión
    r"(?:,(?:==|>=|<=|~=|!=|<|>)[A-Za-z0-9.*+!_-]+)*)?$")
RUTA = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[\w .@()+-]+(?:/[\w .@()+-]+)*$")

_candados = {}
_candado_global = threading.Lock()


def activo():
    return os.getenv("PYTHON_SERVIDOR", "1") != "0"


def _candado(uid):
    with _candado_global:
        return _candados.setdefault(uid, threading.Lock())


def carpeta(uid):
    return os.path.join(VENVS, f"u{int(uid)}")


def python_de(uid):
    d = carpeta(uid)
    return os.path.join(d, "Scripts", "python.exe") if ES_WINDOWS else os.path.join(d, "bin", "python")


def nombre_de(espec):
    return re.split(r"[\[=<>~!]", espec, 1)[0].strip().lower().replace("_", "-")


def _asegurar_venv(uid):
    py = python_de(uid)
    if os.path.exists(py):
        return py
    os.makedirs(VENVS, exist_ok=True)
    r = subprocess.run([sys.executable, "-m", "venv", carpeta(uid)], capture_output=True, timeout=180)
    if r.returncode != 0 or not os.path.exists(py):
        shutil.rmtree(carpeta(uid), ignore_errors=True)
        raise RuntimeError("No se pudo crear el entorno de Python en el servidor: "
                           + (r.stderr or r.stdout).decode("utf-8", "replace")[-400:])
    return py


def _pip(py, args, tiempo=TIEMPO_PIP):
    os.makedirs(os.path.join(CACHE, "pip"), exist_ok=True)
    cmd = [py, "-m", "pip", *args, "--disable-pip-version-check", "--no-input"]
    viejo = os.environ.get("PIP_CACHE_DIR")
    os.environ["PIP_CACHE_DIR"] = os.path.join(CACHE, "pip")
    try:
        return _correr(cmd, os.path.dirname(os.path.dirname(py)), tiempo=tiempo, compilar=True)
    finally:
        if viejo is None:
            os.environ.pop("PIP_CACHE_DIR", None)
        else:
            os.environ["PIP_CACHE_DIR"] = viejo


_MODULOS = r"""
import importlib.metadata as m, json, sys
out = {}
for n in json.loads(sys.argv[1]):
    try:
        d = m.distribution(n)
    except Exception:
        continue
    mods = set()
    top = d.read_text("top_level.txt")
    if top:
        mods |= {x.strip() for x in top.split() if x.strip()}
    for f in d.files or []:
        p = str(f).replace("\\", "/")
        if p.startswith("..") or ".dist-info" in p or ".data/" in p or p.startswith("bin/") or p.startswith("Scripts/"):
            continue
        raiz = p.split("/")[0]
        if "/" in p and raiz != "__pycache__":
            mods.add(raiz)
        elif p.endswith(".py") or p.endswith(".so") or p.endswith(".pyd"):
            mods.add(raiz.split(".")[0])
    mods = sorted(x for x in mods if x.isidentifier() and not x.startswith("_") or x in ("_cffi_backend",))
    out[n] = {"version": d.version, "modulos": mods}
print(json.dumps(out))
"""


def _info(py, nombres):
    codigo, texto = _correr([py, "-c", _MODULOS, json.dumps(nombres)], os.path.dirname(os.path.dirname(py)), tiempo=60)
    try:
        return json.loads(texto.strip().splitlines()[-1]) if codigo == 0 else {}
    except (ValueError, IndexError):
        return {}


def _motivo(texto):
    """Lo más útil del final del log de pip."""
    lineas = [l for l in texto.splitlines() if l.strip()]
    errores = [l for l in lineas if re.search(r"error|ERROR|No matching distribution|Could not find", l)]
    return ((errores or lineas)[-1] if lineas else "pip no devolvió detalles")[:300]


def instalar(uid, paquetes):
    if not activo():
        raise ValueError("La instalación de paquetes en el servidor está desactivada (PYTHON_SERVIDOR=0).")
    if not isinstance(paquetes, list) or not paquetes:
        raise ValueError("Indica qué paquetes instalar.")
    paquetes = [str(p).strip() for p in paquetes][:MAX_PAQUETES]
    malos = [p for p in paquetes if not ESPEC.match(p)]
    if malos:
        raise ValueError(f"«{malos[0][:80]}» no es un nombre de paquete válido de PyPI.")
    with _candado(uid):
        py = _asegurar_venv(uid)
        codigo, log = _pip(py, ["install", "--prefer-binary", *paquetes])
        fallidos = []
        if codigo != 0:
            # Uno a uno, para instalar todo lo que sí se puede y decir exactamente qué falló.
            log = ""
            for p in paquetes:
                c, t = _pip(py, ["install", "--prefer-binary", p])
                log += t
                if c != 0:
                    fallidos.append({"paquete": p, "motivo": _motivo(t)})
        malos = {f["paquete"] for f in fallidos}
        nombres = [nombre_de(p) for p in paquetes if p not in malos]
        info = _info(py, nombres)
    instalados = [{"paquete": n, "version": info.get(n, {}).get("version", ""), "modulos": info.get(n, {}).get("modulos", [])}
                  for n in nombres]
    return {"instalados": instalados, "fallidos": fallidos, "log": log[-4000:]}


def desinstalar(uid, nombres):
    nombres = [nombre_de(str(n)) for n in (nombres or [])][:MAX_PAQUETES]
    if not nombres or any(not ESPEC.match(n) for n in nombres):
        raise ValueError("Indica qué paquetes desinstalar.")
    if not os.path.exists(python_de(uid)):
        return {"ok": True}
    with _candado(uid):
        codigo, texto = _pip(python_de(uid), ["uninstall", "-y", *nombres], tiempo=180)
    return {"ok": codigo == 0, "log": texto[-2000:]}


def lista(uid):
    if not os.path.exists(python_de(uid)):
        return []
    codigo, texto = _pip(python_de(uid), ["list", "--format=json", "--exclude", "pip", "--exclude", "setuptools"], tiempo=60)
    try:
        return [{"paquete": x["name"], "version": x["version"]} for x in json.loads(texto.strip().splitlines()[-1])]
    except (ValueError, IndexError, KeyError, TypeError):
        return []


def ejecutar(uid, ruta, archivos, entrada="", args=None):
    """Ejecuta `ruta` (un .py del proyecto) con el Python del servidor y los paquetes del usuario."""
    if not activo():
        raise ValueError("La ejecución de Python en el servidor está desactivada (PYTHON_SERVIDOR=0).")
    if not isinstance(archivos, list) or not archivos:
        raise ValueError("Faltan los archivos del proyecto.")
    if not isinstance(ruta, str) or not RUTA.match(ruta) or not ruta.endswith(".py"):
        raise ValueError("Archivo de Python no válido.")
    total = 0
    limpios = {}
    for a in archivos[:MAX_ARCHIVOS]:
        if not isinstance(a, dict):
            continue
        r, c = a.get("ruta"), a.get("contenido")
        if not isinstance(r, str) or not isinstance(c, str) or not RUTA.match(r):
            continue
        total += len(c)
        if total > MAX_TOTAL:
            raise ValueError("El proyecto es demasiado grande para ejecutarlo en el servidor.")
        limpios[r] = c
    if ruta not in limpios:
        raise ValueError("El archivo a ejecutar no está entre los archivos enviados.")
    args = [str(x)[:200] for x in (args or [])][:20]
    py = python_de(uid) if os.path.exists(python_de(uid)) else sys.executable
    with tempfile.TemporaryDirectory(prefix="cc_py_") as d:
        for r, c in limpios.items():
            destino = os.path.join(d, *r.split("/"))
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, "w", encoding="utf-8", newline="\n") as f:
                f.write(c)
        cwd = os.path.join(d, *ruta.split("/")[:-1]) if "/" in ruta else d
        principal = os.path.join(d, *ruta.split("/"))
        codigo, texto = _correr([py, "-X", "utf8", principal, *args], cwd, tiempo=TIEMPO_RUN,
                                entrada=entrada or "", compilar=True)
        texto = _limpiar(texto, d)
    if len(texto) > MAX_SALIDA:
        texto = texto[:MAX_SALIDA] + "\n… (salida recortada)"
    return {"salida": texto, "error": codigo != 0, "donde": "servidor"}
