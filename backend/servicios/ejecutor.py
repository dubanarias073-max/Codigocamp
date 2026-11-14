"""Ejecutor de código para la página Aprende (ruta POST /api/run).

Cada lenguaje se ejecuta con el compilador/intérprete instalado en ESTE equipo.
Si no está instalado, se intenta un servicio Piston (variable PISTON_URL en .env).
Si tampoco hay, se devuelve un mensaje claro diciendo qué instalar.

JavaScript, TypeScript, Python y SQL NO pasan por aquí: corren en el navegador.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import json

ES_WINDOWS = os.name == "nt"
MAX_CODIGO = 20_000        # caracteres
MAX_SALIDA = 20_000        # caracteres devueltos
TIEMPO = 10                # segundos por paso (compilar / ejecutar)
TIEMPO_LENTO = 60          # Kotlin y .NET compilan despacio

EXE = ".exe" if ES_WINDOWS else ""


def _hay(*nombres):
    """Devuelve la ruta del primer programa encontrado en el PATH."""
    for n in nombres:
        r = shutil.which(n)
        if r:
            return r
    return None


def _limites():
    """En Linux/macOS limita memoria, CPU y procesos del programa del alumno."""
    if ES_WINDOWS:
        return None

    def poner():
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (TIEMPO + 5, TIEMPO + 5))
        resource.setrlimit(resource.RLIMIT_FSIZE, (5_000_000, 5_000_000))
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (256, 256))
        except (ValueError, OSError):
            pass
    return poner


def _correr(cmd, cwd, tiempo=TIEMPO, entrada=None):
    """Ejecuta un comando y devuelve (código_salida, texto_salida)."""
    env = {k: v for k, v in os.environ.items()
           if not k.upper().endswith(("KEY", "SECRET", "PASSWORD", "TOKEN"))
           and k.upper() not in {"DATABASE_URL"}}
    env.update({"PYTHONIOENCODING": "utf-8", "LC_ALL": "C.UTF-8", "HOME": cwd,
                "DOTNET_CLI_HOME": cwd, "DOTNET_NOLOGO": "1", "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
                "JAVA_TOOL_OPTIONS": "-Dfile.encoding=UTF-8"})
    try:
        r = subprocess.run(cmd, cwd=cwd, input=entrada, capture_output=True, timeout=tiempo,
                           env=env, preexec_fn=_limites())
    except subprocess.TimeoutExpired:
        return 124, "Tiempo agotado: ¿hay un bucle infinito?"
    except OSError as x:
        return 127, f"No se pudo iniciar el programa: {x}"
    texto = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode, texto


def _limpiar(texto, carpeta):
    """Quita rutas temporales del texto para que los errores sean legibles."""
    texto = texto.replace(carpeta + os.sep, "").replace(carpeta, "")
    return texto.replace("\r\n", "\n")


def _clase_java(codigo):
    m = re.search(r"public\s+(?:final\s+|abstract\s+)*(?:class|interface|enum|record)\s+(\w+)", codigo)
    return m.group(1) if m else "Main"


# ---------------------------------------------------------------- lenguajes ----
def _java(codigo, d):
    javac, java = _hay("javac"), _hay("java")
    if not (javac and java):
        return None, "Java (JDK)"
    nombre = _clase_java(codigo)
    open(os.path.join(d, nombre + ".java"), "w", encoding="utf-8").write(codigo)
    rc, o = _correr([javac, "-encoding", "UTF-8", nombre + ".java"], d)
    if rc:
        return (rc, o), None
    return _correr([java, "-cp", d, nombre], d), None


def _nativo(compilador, ext, extra=()):
    def f(codigo, d):
        cc = _hay(*compilador)
        if not cc:
            return None, compilador[0]
        open(os.path.join(d, "main" + ext), "w", encoding="utf-8").write(codigo)
        rc, o = _correr([cc, "main" + ext, "-o", "main" + EXE, *extra], d, TIEMPO_LENTO)
        if rc:
            return (rc, o), None
        return _correr([os.path.join(d, "main" + EXE)], d), None
    return f


def _interprete(nombres, ext, args=()):
    def f(codigo, d):
        p = _hay(*nombres)
        if not p:
            return None, nombres[0]
        open(os.path.join(d, "main" + ext), "w", encoding="utf-8").write(codigo)
        return _correr([p, *args, "main" + ext], d, TIEMPO_LENTO if nombres[0] == "go" else TIEMPO), None
    return f


def _swift(codigo, d):
    p = _hay("swiftc", "swift")
    if not p:
        return None, "swift"
    open(os.path.join(d, "main.swift"), "w", encoding="utf-8").write(codigo)
    if os.path.basename(p).startswith("swiftc"):
        rc, o = _correr([p, "main.swift", "-o", "main" + EXE], d, TIEMPO_LENTO)
        if rc:
            return (rc, o), None
        return _correr([os.path.join(d, "main" + EXE)], d), None
    return _correr([p, "main.swift"], d, TIEMPO_LENTO), None


def _kotlin(codigo, d):
    kc, java = _hay("kotlinc", "kotlinc.bat"), _hay("java")
    if not (kc and java):
        return None, "kotlinc"
    open(os.path.join(d, "main.kt"), "w", encoding="utf-8").write(codigo)
    rc, o = _correr([kc, "main.kt", "-include-runtime", "-d", "main.jar"], d, 120)
    if rc:
        return (rc, o), None
    return _correr([java, "-jar", "main.jar"], d, TIEMPO), None


def _csharp(codigo, d):
    dn = _hay("dotnet")
    if not dn:
        mcs, mono = _hay("mcs"), _hay("mono")
        if not (mcs and mono):
            return None, ".NET SDK (dotnet)"
        open(os.path.join(d, "main.cs"), "w", encoding="utf-8").write(codigo)
        rc, o = _correr([mcs, "main.cs", "-out:main.exe"], d, TIEMPO_LENTO)
        return ((rc, o) if rc else _correr([mono, "main.exe"], d)), None
    rc, v = _correr([dn, "--version"], d, 30)
    mayor = re.match(r"(\d+)", v.strip())
    mayor = mayor.group(1) if mayor else "8"
    open(os.path.join(d, "Program.cs"), "w", encoding="utf-8").write(codigo)
    open(os.path.join(d, "app.csproj"), "w", encoding="utf-8").write(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType>'
        f"<TargetFramework>net{mayor}.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings>"
        "<Nullable>disable</Nullable><InvariantGlobalization>true</InvariantGlobalization>"
        "</PropertyGroup></Project>")
    rc, o = _correr([dn, "build", "-c", "Release", "-o", "salida", "-v", "q", "-nologo"], d, 120)
    if rc:
        # Deja solo las líneas de error del compilador
        lin = [l for l in o.splitlines() if "error" in l]
        return (rc, "\n".join(dict.fromkeys(lin)) or o), None
    return _correr([dn, os.path.join(d, "salida", "app.dll")], d), None


LENGUAJES = {
    "java":   {"f": _java, "piston": ("java", "Main.java")},
    "c":      {"f": _nativo(("gcc", "cc", "clang"), ".c", ("-lm",)), "piston": ("c", "main.c")},
    "cpp":    {"f": _nativo(("g++", "clang++"), ".cpp", ("-std=c++17",)), "piston": ("c++", "main.cpp")},
    "csharp": {"f": _csharp, "piston": ("csharp", "Program.cs")},
    "php":    {"f": _interprete(("php",), ".php"), "piston": ("php", "main.php")},
    "go":     {"f": _interprete(("go",), ".go", ("run",)), "piston": ("go", "main.go")},
    "rust":   {"f": _nativo(("rustc",), ".rs", ("--edition", "2021")), "piston": ("rust", "main.rs")},
    "swift":  {"f": _swift, "piston": ("swift", "main.swift")},
    "kotlin": {"f": _kotlin, "piston": ("kotlin", "main.kt")},
    "ruby":   {"f": _interprete(("ruby",), ".rb"), "piston": ("ruby", "main.rb")},
}


# ------------------------------------------------------------------ Piston ----
def _piston(lenguaje, codigo):
    """Plan B: servicio Piston (propio o público). Devuelve (rc, texto) o None."""
    url = os.getenv("PISTON_URL", "").strip().rstrip("/")
    if not url:
        return None
    nombre, archivo = LENGUAJES[lenguaje]["piston"]
    if lenguaje == "java":
        archivo = _clase_java(codigo) + ".java"
    cuerpo = json.dumps({"language": nombre, "version": "*",
                         "files": [{"name": archivo, "content": codigo}],
                         "compile_timeout": 20000, "run_timeout": 10000}).encode()
    cab = {"Content-Type": "application/json"}
    if os.getenv("PISTON_KEY"):
        cab["Authorization"] = os.getenv("PISTON_KEY")
    try:
        req = urllib.request.Request(url + "/execute", cuerpo, cab)
        with urllib.request.urlopen(req, timeout=40) as r:
            d = json.load(r)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as x:
        return 1, f"El servicio de ejecución no respondió ({x})."
    c, e = d.get("compile") or {}, d.get("run") or {}
    if c.get("code"):
        return c["code"], (c.get("output") or c.get("stderr") or "Error al compilar.")
    return e.get("code", 0) or 0, e.get("output") or (e.get("stdout", "") + e.get("stderr", ""))


# ---------------------------------------------------------------- principal ----
INSTALAR = {
    "Java (JDK)": "Instala el JDK (Java 17 o superior) y asegúrate de que `javac` esté en el PATH.",
    "gcc": "Instala MinGW-w64/MSYS2 (Windows) o `build-essential` (Linux) para tener `gcc`.",
    "g++": "Instala MinGW-w64/MSYS2 (Windows) o `build-essential` (Linux) para tener `g++`.",
    ".NET SDK (dotnet)": "Instala el SDK de .NET desde dotnet.microsoft.com.",
    "php": "Instala PHP (con XAMPP ya viene en C:\\xampp\\php: agrégalo al PATH).",
    "go": "Instala Go desde go.dev/dl.",
    "rustc": "Instala Rust con rustup desde rustup.rs.",
    "swift": "Instala el toolchain de Swift desde swift.org.",
    "kotlinc": "Instala Kotlin (kotlinc) y un JDK.",
    "ruby": "Instala Ruby (rubyinstaller.org en Windows).",
}


def ejecutar(lenguaje, codigo):
    """Devuelve {'salida': texto, 'error': bool}. Lanza ValueError si la petición es inválida."""
    if lenguaje not in LENGUAJES:
        raise ValueError("Ese lenguaje no se ejecuta en el servidor.")
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("Escribe algo de código antes de ejecutar.")
    if len(codigo) > MAX_CODIGO:
        raise ValueError(f"El código es demasiado largo (máximo {MAX_CODIGO} caracteres).")

    d = tempfile.mkdtemp(prefix="cc_run_")
    try:
        res, falta = LENGUAJES[lenguaje]["f"](codigo, d)
        if res is None:
            res = _piston(lenguaje, codigo)
            if res is None:
                ayuda = INSTALAR.get(falta, f"Instala {falta}.")
                return {"salida": f"Este equipo no tiene {falta} instalado, por eso no se puede ejecutar "
                                  f"{lenguaje}.\n{ayuda}\nOpcional: define PISTON_URL en backend/.env "
                                  "para usar un servicio externo.", "error": True}
        rc, texto = res
        texto = _limpiar(texto, d)
        if len(texto) > MAX_SALIDA:
            texto = texto[:MAX_SALIDA] + "\n… (salida recortada)"
        return {"salida": texto, "error": rc != 0}
    finally:
        shutil.rmtree(d, ignore_errors=True)
