"""Ejecutor de código para Aprende y la terminal de Trabajo (ruta POST /api/run).

Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin y Ruby se ejecutan, en este orden:
  1. Con el compilador o intérprete instalado en ESTE equipo (si está en el PATH).
  2. Con un servicio Piston propio, si definiste PISTON_URL en backend/.env.
  3. En línea, sin instalar nada: Wandbox (wandbox.org) y, para Kotlin, el Kotlin Playground oficial
     (api.kotlinlang.org). Son servicios públicos y gratis; se apagan con EJECUCION_EN_LINEA=0 en .env.

Acepta la entrada del teclado (stdin) y, en Java, varias clases del mismo proyecto (se unen en un archivo).
JavaScript, TypeScript, Python y SQL NO pasan por aquí: corren en el navegador.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import unicodedata
import urllib.error
import urllib.request

ES_WINDOWS = os.name == "nt"
MAX_CODIGO = 60_000        # caracteres (con los demás archivos del proyecto)
MAX_ENTRADA = 20_000       # caracteres de entrada del teclado
MAX_SALIDA = 20_000        # caracteres devueltos
TIEMPO = 10                # segundos por paso (compilar / ejecutar)
TIEMPO_LENTO = 60          # Kotlin y .NET compilan despacio
TIEMPO_EN_LINEA = 40       # segundos máximos esperando a un servicio en línea

EXE = ".exe" if ES_WINDOWS else ""


def _hay(*nombres):
    """Devuelve la ruta del primer programa encontrado en el PATH."""
    for n in nombres:
        r = shutil.which(n)
        if r:
            return r
    return None


def _limites(compilar=False):
    """En Linux/macOS limita CPU, tamaño de archivos y procesos. Compilar (go run, rustc…) escribe archivos grandes."""
    if ES_WINDOWS:
        return None
    cpu = TIEMPO_LENTO + 30 if compilar else TIEMPO + 5
    tam = 1_000_000_000 if compilar else 5_000_000

    def poner():
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
        resource.setrlimit(resource.RLIMIT_FSIZE, (tam, tam))
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (256, 256))
        except (ValueError, OSError):
            pass
    return poner


CACHE = os.path.join(tempfile.gettempdir(), "codigocamp_cache")   # caché de Go y Cargo entre ejecuciones


def _correr(cmd, cwd, tiempo=TIEMPO, entrada=None, compilar=None):
    """Ejecuta un comando y devuelve (código_salida, texto_salida)."""
    env = {k: v for k, v in os.environ.items()
           if not k.upper().endswith(("KEY", "SECRET", "PASSWORD", "TOKEN"))
           and k.upper() not in {"DATABASE_URL"}}
    env.update({"PYTHONIOENCODING": "utf-8", "LC_ALL": "C.UTF-8", "HOME": cwd,
                "DOTNET_CLI_HOME": cwd, "DOTNET_NOLOGO": "1", "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
                "JAVA_TOOL_OPTIONS": "-Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8",
                "GOCACHE": os.path.join(CACHE, "go-build"), "GOPATH": os.path.join(CACHE, "go"),
                "GOFLAGS": "-mod=mod", "GOTOOLCHAIN": "local"})
    if compilar is None:
        compilar = tiempo > TIEMPO
    datos = entrada.encode("utf-8") if isinstance(entrada, str) else (entrada or b"")
    try:
        r = subprocess.run(cmd, cwd=cwd, input=datos, capture_output=True, timeout=tiempo,
                           env=env, preexec_fn=_limites(compilar))
    except subprocess.TimeoutExpired:
        return 124, "Tiempo agotado: ¿hay un bucle infinito o el programa espera datos del teclado?"
    except OSError as x:
        return 127, f"No se pudo iniciar el programa: {x}"
    texto = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode, texto


def _limpiar(texto, carpeta):
    """Quita rutas temporales y avisos internos de Java para que la salida sea legible."""
    texto = texto.replace(carpeta + os.sep, "").replace(carpeta, "")
    texto = re.sub(r"^Picked up (?:_JAVA_OPTIONS|JAVA_TOOL_OPTIONS|JDK_JAVA_OPTIONS):.*\n?", "", texto, flags=re.M)
    return texto.replace("\r\n", "\n")


# ------------------------------------------------------------ preparar código ----
_TIPO_JAVA = r"(?:class|interface|enum|record)"


def _clase_java(codigo):
    """Nombre de la clase que tiene main (o la primera pública)."""
    for m in re.finditer(rf"(?:public\s+)?(?:final\s+|abstract\s+)*{_TIPO_JAVA}\s+(\w+)", codigo):
        resto = codigo[m.end():]
        siguiente = re.search(rf"\b{_TIPO_JAVA}\s+\w+", resto)
        cuerpo = resto[: siguiente.start()] if siguiente else resto
        if re.search(r"static\s+(?:public\s+)?void\s+main\s*\(", cuerpo) or re.search(r"public\s+static\s+void\s+main\s*\(", cuerpo):
            return m.group(1)
    m = re.search(rf"public\s+(?:final\s+|abstract\s+)*{_TIPO_JAVA}\s+(\w+)", codigo)
    return m.group(1) if m else "Main"


def unir_java(principal, otros):
    """Une varias clases de Java en un solo archivo: imports arriba, sin package y sin `public` en los tipos de
    primer nivel (un archivo solo puede tener un tipo público)."""
    imports, cuerpos = [], []
    for texto in [principal, *otros]:
        texto = re.sub(r"^\s*package\s+[\w.]+\s*;\s*$", "", texto, flags=re.M)
        for imp in re.findall(r"^\s*import\s+[\w.*\s]+;\s*$", texto, flags=re.M):
            imp = imp.strip()
            if imp not in imports:
                imports.append(imp)
        texto = re.sub(r"^\s*import\s+[\w.*\s]+;\s*$", "", texto, flags=re.M)
        cuerpos.append(texto.strip())
    return "\n".join(imports) + ("\n\n" if imports else "") + "\n\n".join(cuerpos) + "\n"


def _sin_public(codigo):
    return re.sub(rf"^(\s*)public\s+((?:final\s+|abstract\s+|sealed\s+|non-sealed\s+)*{_TIPO_JAVA}\s)", r"\1\2",
                  codigo, flags=re.M)


def _utf8_java(codigo):
    """Hace que System.out escriba en UTF-8 (tildes y ñ) en servidores con otra configuración."""
    clase = _clase_java(codigo)
    m = re.search(rf"{_TIPO_JAVA}\s+{re.escape(clase)}\b[^{{]*\{{", codigo)
    if not m:
        return codigo
    bloque = (" static { try { System.setOut(new java.io.PrintStream(new java.io.FileOutputStream("
              "java.io.FileDescriptor.out), true, \"UTF-8\")); } catch (Exception e) { } }")
    return codigo[: m.end()] + bloque + codigo[m.end():]


def _escapar_java(codigo):
    """Java acepta \\uXXXX en cualquier parte del código: así el texto viaja solo en ASCII."""
    return "".join(c if ord(c) < 128 else "".join(f"\\u{u:04x}" for u in _utf16(c)) for c in codigo)


def _utf16(c):
    b = c.encode("utf-16-be")
    return [int.from_bytes(b[i:i + 2], "big") for i in range(0, len(b), 2)]


def _sin_tildes(texto):
    return "".join(ch for ch in unicodedata.normalize("NFKD", texto) if ord(ch) < 128) or "?"


# Escapes de un carácter no ASCII dentro de una cadena "…" de cada lenguaje.
_ESCAPE = {
    "c": lambda c: "".join(f"\\{b:03o}" for b in c.encode("utf-8")),
    "cpp": lambda c: "".join(f"\\{b:03o}" for b in c.encode("utf-8")),
    "go": lambda c: "".join(f"\\x{b:02x}" for b in c.encode("utf-8")),
    "rust": lambda c: f"\\u{{{ord(c):x}}}",
    "swift": lambda c: f"\\u{{{ord(c):x}}}",
    "php": lambda c: f"\\u{{{ord(c):x}}}",
    "ruby": lambda c: f"\\u{{{ord(c):x}}}",
    "csharp": lambda c: "".join(f"\\u{u:04x}" for u in _utf16(c)),
    "kotlin": lambda c: "".join(f"\\u{u:04x}" for u in _utf16(c)),
}
_CADENA = re.compile(r'"(?:\\.|[^"\\\n])*"')


def a_ascii(lenguaje, codigo):
    """Algunos servicios en línea dañan los caracteres que no son ASCII. Dentro de las cadenas "…" se cambian por
    escapes del lenguaje (el programa imprime lo mismo) y fuera de ellas (comentarios) se quitan las tildes."""
    if lenguaje == "java":
        return _escapar_java(codigo)
    if all(ord(c) < 128 for c in codigo) or lenguaje not in _ESCAPE:
        return codigo
    esc = _ESCAPE[lenguaje]
    partes, i = [], 0
    for m in _CADENA.finditer(codigo):
        partes.append(_sin_tildes_fuera(codigo[i:m.start()]))
        partes.append("".join(ch if ord(ch) < 128 else esc(ch) for ch in m.group(0)))
        i = m.end()
    partes.append(_sin_tildes_fuera(codigo[i:]))
    return "".join(partes)


def _sin_tildes_fuera(texto):
    return "".join(ch if ord(ch) < 128 else _sin_tildes(ch) for ch in texto)


def _arreglar_mojibake(texto):
    """Si la salida llegó como UTF-8 leído en Latin-1 («cÃ³mo»), la devuelve bien («cómo»)."""
    if not re.search("[ÃÂ][\u0080-\u00bf]", texto):
        return texto
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def unir_c(principal, archivos):
    """En C/C++ reemplaza #include "archivo.h" por su contenido y agrega su .c/.cpp, para enviarlo como uno solo."""
    por_nombre = {os.path.basename(a["nombre"]): a["contenido"] for a in archivos}
    incluidos = set()

    def expandir(texto, profundidad=0):
        def reemplazo(m):
            nombre = os.path.basename(m.group(1))
            if nombre in incluidos or nombre not in por_nombre or profundidad > 8:
                return "" if nombre in incluidos else m.group(0)
            incluidos.add(nombre)
            return expandir(por_nombre[nombre], profundidad + 1)
        return re.sub(r'^\s*#\s*include\s+"([^"]+)"\s*$', reemplazo, texto, flags=re.M)

    codigo = expandir(principal)
    for h in list(incluidos):
        base = os.path.splitext(h)[0]
        for ext in (".c", ".cpp", ".cc", ".cxx"):
            impl = por_nombre.get(base + ext)
            if impl and base + ext not in incluidos:
                incluidos.add(base + ext)
                codigo += "\n" + expandir(impl)
    return codigo


# ---------------------------------------------------------------- lenguajes ----
def _java(codigo, d, entrada):
    javac, java = _hay("javac"), _hay("java")
    if not (javac and java):
        return None, "Java (JDK)"
    nombre = _clase_java(codigo)
    open(os.path.join(d, nombre + ".java"), "w", encoding="utf-8").write(codigo)
    rc, o = _correr([javac, "-encoding", "UTF-8", nombre + ".java"], d, TIEMPO_LENTO)
    if rc:
        return (rc, o), None
    return _correr([java, "-cp", d, nombre], d, entrada=entrada), None


def _nativo(compilador, ext, extra=()):
    def f(codigo, d, entrada):
        cc = _hay(*compilador)
        if not cc:
            return None, compilador[0]
        open(os.path.join(d, "main" + ext), "w", encoding="utf-8").write(codigo)
        rc, o = _correr([cc, "main" + ext, "-o", "main" + EXE, *extra], d, TIEMPO_LENTO)
        if rc:
            return (rc, o), None
        return _correr([os.path.join(d, "main" + EXE)], d, entrada=entrada), None
    return f


def _interprete(nombres, ext, args=()):
    def f(codigo, d, entrada):
        p = _hay(*nombres)
        if not p:
            return None, nombres[0]
        open(os.path.join(d, "main" + ext), "w", encoding="utf-8").write(codigo)
        return _correr([p, *args, "main" + ext], d, TIEMPO_LENTO if nombres[0] == "go" else TIEMPO, entrada,
                       compilar=nombres[0] == "go"), None
    return f


def _nativo_fpc(codigo, d, entrada):
    fpc = _hay("fpc")
    if not fpc:
        return None, "fpc"
    open(os.path.join(d, "main.pas"), "w", encoding="utf-8").write(codigo)
    rc, o = _correr([fpc, "-v0", "main.pas", "-omain" + EXE], d, TIEMPO_LENTO, compilar=True)
    if rc:
        return (rc, o), None
    return _correr([os.path.join(d, "main" + EXE)], d, entrada=entrada), None


def _swift(codigo, d, entrada):
    p = _hay("swiftc", "swift")
    if not p:
        return None, "swift"
    open(os.path.join(d, "main.swift"), "w", encoding="utf-8").write(codigo)
    if os.path.basename(p).startswith("swiftc"):
        rc, o = _correr([p, "main.swift", "-o", "main" + EXE], d, TIEMPO_LENTO)
        if rc:
            return (rc, o), None
        return _correr([os.path.join(d, "main" + EXE)], d, entrada=entrada), None
    return _correr([p, "main.swift"], d, TIEMPO_LENTO, entrada), None


def _kotlin(codigo, d, entrada):
    kc, java = _hay("kotlinc", "kotlinc.bat"), _hay("java")
    if not (kc and java):
        return None, "kotlinc"
    open(os.path.join(d, "main.kt"), "w", encoding="utf-8").write(codigo)
    rc, o = _correr([kc, "main.kt", "-include-runtime", "-d", "main.jar"], d, 120)
    if rc:
        return (rc, o), None
    return _correr([java, "-jar", "main.jar"], d, TIEMPO, entrada), None


def _csharp(codigo, d, entrada):
    dn = _hay("dotnet")
    if not dn:
        mcs, mono = _hay("mcs"), _hay("mono")
        if not (mcs and mono):
            return None, ".NET SDK (dotnet)"
        open(os.path.join(d, "main.cs"), "w", encoding="utf-8").write(codigo)
        rc, o = _correr([mcs, "main.cs", "-out:main.exe"], d, TIEMPO_LENTO)
        return ((rc, o) if rc else _correr([mono, "main.exe"], d, entrada=entrada)), None
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
        lin = [l for l in o.splitlines() if "error" in l]
        return (rc, "\n".join(dict.fromkeys(lin)) or o), None
    return _correr([dn, os.path.join(d, "salida", "app.dll")], d, entrada=entrada), None


LENGUAJES = {
    "java":   {"f": _java, "piston": ("java", "Main.java")},
    "c":      {"f": _nativo(("gcc", "cc", "clang"), ".c", ("-lm",)), "piston": ("c", "main.c")},
    "cpp":    {"f": _nativo(("g++", "clang++"), ".cpp", ("-std=c++20",)), "piston": ("c++", "main.cpp")},
    "csharp": {"f": _csharp, "piston": ("csharp", "Program.cs")},
    "php":    {"f": _interprete(("php",), ".php"), "piston": ("php", "main.php")},
    "go":     {"f": _interprete(("go",), ".go", ("run",)), "piston": ("go", "main.go")},
    "rust":   {"f": _nativo(("rustc",), ".rs", ("--edition", "2021")), "piston": ("rust", "main.rs")},
    "swift":  {"f": _swift, "piston": ("swift", "main.swift")},
    "kotlin": {"f": _kotlin, "piston": ("kotlin", "main.kt")},
    "ruby":   {"f": _interprete(("ruby",), ".rb"), "piston": ("ruby", "main.rb")},
    # Más lenguajes: se usan si están instalados en el servidor y, si no, en línea (Wandbox / Compiler Explorer).
    "lua":     {"f": _interprete(("lua", "lua5.4", "lua54", "luajit"), ".lua"), "piston": ("lua", "main.lua")},
    "perl":    {"f": _interprete(("perl",), ".pl"), "piston": ("perl", "main.pl")},
    "r":       {"f": _interprete(("Rscript",), ".R"), "piston": ("rscript", "main.R")},
    "scala":   {"f": _interprete(("scala-cli",), ".scala", ("run", "--server=false")), "piston": ("scala", "Main.scala")},
    "haskell": {"f": _interprete(("runghc", "runhaskell"), ".hs"), "piston": ("haskell", "main.hs")},
    "elixir":  {"f": _interprete(("elixir",), ".exs"), "piston": ("elixir", "main.exs")},
    "julia":   {"f": _interprete(("julia",), ".jl"), "piston": ("julia", "main.jl")},
    "groovy":  {"f": _interprete(("groovy",), ".groovy"), "piston": ("groovy", "main.groovy")},
    "crystal": {"f": _interprete(("crystal",), ".cr", ("run",)), "piston": ("crystal", "main.cr")},
    "nim":     {"f": _interprete(("nim",), ".nim", ("r", "--hints:off")), "piston": ("nim", "main.nim")},
    "ocaml":   {"f": _interprete(("ocaml",), ".ml"), "piston": ("ocaml", "main.ml")},
    "d":       {"f": _interprete(("rdmd", "ldc2"), ".d", ()), "piston": ("d", "main.d")},
    "pascal":  {"f": _nativo_fpc, "piston": ("pascal", "main.pas")},
    "zig":     {"f": _interprete(("zig",), ".zig", ("run",)), "piston": ("zig", "main.zig")},
    "lisp":    {"f": _interprete(("sbcl", "clisp"), ".lisp", ("--script",)), "piston": ("commonlisp", "main.lisp")},
    "bash":    {"f": _interprete(("bash",), ".sh"), "piston": ("bash", "main.sh")},
}

NOMBRES = {"java": "Java", "c": "C", "cpp": "C++", "csharp": "C#", "php": "PHP", "go": "Go", "rust": "Rust",
           "swift": "Swift", "kotlin": "Kotlin", "ruby": "Ruby",
           "lua": "Lua", "perl": "Perl", "r": "R", "scala": "Scala", "haskell": "Haskell", "elixir": "Elixir", "julia": "Julia",
           "groovy": "Groovy", "crystal": "Crystal", "nim": "Nim", "ocaml": "OCaml", "d": "D", "pascal": "Pascal", "zig": "Zig",
           "lisp": "Common Lisp", "bash": "Bash"}


# ------------------------------------------------------------------ Piston ----
def _piston(lenguaje, codigo, entrada):
    """Servicio Piston propio (PISTON_URL). Devuelve (rc, texto) o None si no está configurado."""
    url = os.getenv("PISTON_URL", "").strip().rstrip("/")
    if not url:
        return None
    nombre, archivo = LENGUAJES[lenguaje]["piston"]
    if lenguaje == "java":
        archivo = _clase_java(codigo) + ".java"
    cuerpo = json.dumps({"language": nombre, "version": "*", "stdin": entrada or "",
                         "files": [{"name": archivo, "content": codigo}],
                         "compile_timeout": 20000, "run_timeout": 10000}).encode()
    cab = {"Content-Type": "application/json"}
    if os.getenv("PISTON_KEY"):
        cab["Authorization"] = os.getenv("PISTON_KEY")
    try:
        d = _pedir_json(url + "/execute", cuerpo, cab, 40)
    except _FalloServicio:
        return None   # se prueba el siguiente servicio
    c, e = d.get("compile") or {}, d.get("run") or {}
    if c.get("code"):
        return c["code"], (c.get("output") or c.get("stderr") or "Error al compilar.")
    return e.get("code", 0) or 0, e.get("output") or (e.get("stdout", "") + e.get("stderr", ""))


# --------------------------------------------------------- servicios en línea ----
class _FalloServicio(Exception):
    """El servicio no respondió o falló por dentro (no es un error del código del alumno)."""


def _pedir_json(url, cuerpo=None, cab=None, tiempo=TIEMPO_EN_LINEA):
    cab = {"User-Agent": "CodigoCamp/1.0 (ejecutor educativo)", "Accept": "application/json", **(cab or {})}
    try:
        req = urllib.request.Request(url, cuerpo, cab)
        with urllib.request.urlopen(req, timeout=tiempo) as r:
            return json.loads(r.read().decode("utf-8", "replace") or "{}")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as x:
        raise _FalloServicio(str(x)) from x


def en_linea_activo():
    return os.getenv("EJECUCION_EN_LINEA", "1").strip().lower() not in ("0", "no", "false", "off")


WANDBOX = os.getenv("WANDBOX_URL", "https://wandbox.org").rstrip("/")
# Versiones que se prueban primero (las más nuevas de algunos lenguajes a veces fallan en Wandbox).
WANDBOX_PREFERIDOS = {
    "java": ["openjdk-jdk-22+36", "openjdk-jdk-21+35"],
    "c": ["gcc-13.2.0-c", "clang-17.0.1-c"],
    "cpp": ["gcc-13.2.0", "clang-17.0.1"],
    "csharp": ["dotnetcore-8.0.402", "mono-6.12.0.199"],
    "php": ["php-8.3.12", "php-8.2.24"],
    "ruby": ["ruby-3.4.9", "ruby-3.3.11"],
    "go": ["go-1.23.12", "go-1.22.8"],
    "rust": ["rust-1.82.0", "rust-1.80.1"],
    "swift": ["swift-6.0.1", "swift-5.10.1"],
    "lua": ["lua-5.4.7"], "perl": ["perl-5.40.0"], "r": ["r-4.4.1"], "scala": ["scala-3.5.1", "scala-3.3.4"],
    "haskell": ["ghc-9.10.1"], "elixir": ["elixir-1.17.3"], "julia": ["julia-1.10.5"], "groovy": ["groovy-4.0.23"],
    "crystal": ["crystal-1.13.3"], "nim": ["nim-2.2.0"], "ocaml": ["ocaml-5.2.0"], "d": ["ldc-1.39.0", "dmd-2.109.1"],
    "pascal": ["fpc-3.2.2"], "zig": ["zig-0.13.0"], "lisp": ["sbcl-2.4.9", "clisp-2.49"], "bash": ["bash"],
}
_WANDBOX_PATRON = {
    "java": r"^openjdk-jdk-\d", "c": r"^(gcc|clang)-\d[\d.]*-c$", "cpp": r"^(gcc|clang)-\d[\d.]*$",
    "csharp": r"^(dotnetcore|mono)-\d", "php": r"^php-8", "ruby": r"^ruby-3", "go": r"^go-1\.", "rust": r"^rust-1\.",
    "swift": r"^swift-\d",
    "lua": r"^lua-5", "perl": r"^perl-5", "r": r"^r-\d", "scala": r"^scala-3", "haskell": r"^ghc-\d", "elixir": r"^elixir-",
    "julia": r"^julia-1", "groovy": r"^groovy-", "crystal": r"^crystal-", "nim": r"^nim-2", "ocaml": r"^ocaml-", "d": r"^(ldc|dmd)-",
    "pascal": r"^fpc-", "zig": r"^zig-0\.1[3-9]", "lisp": r"^(sbcl|clisp)-", "bash": r"^bash$",
}
_lista = {"cuando": 0.0, "nombres": set()}
_candado = threading.Lock()


def _compiladores_wandbox(lenguaje):
    """Compiladores a probar: primero los preferidos que existan, luego los demás de la lista (cacheada 6 h)."""
    with _candado:
        if time.time() - _lista["cuando"] > 6 * 3600:
            try:
                datos = _pedir_json(WANDBOX + "/api/list.json", tiempo=15)
                _lista["nombres"] = {c.get("name", "") for c in datos if isinstance(c, dict)}
            except _FalloServicio:
                pass
            _lista["cuando"] = time.time()
        nombres = set(_lista["nombres"])
    preferidos = WANDBOX_PREFERIDOS.get(lenguaje, [])
    if not nombres:
        return preferidos
    elegidos = [p for p in preferidos if p in nombres]
    otros = sorted((n for n in nombres if re.match(_WANDBOX_PATRON[lenguaje], n) and n not in elegidos),
                   key=lambda n: [int(x) if x.isdigit() else 0 for x in re.findall(r"\d+", n)], reverse=True)
    return (elegidos + otros)[:3] or preferidos


RUBY_UTF8 = ("Encoding.default_external = Encoding::UTF_8; Encoding.default_internal = Encoding::UTF_8; "
             "$stdin.set_encoding('UTF-8'); $stdout.set_encoding('UTF-8'); ")


def _wandbox(lenguaje, codigo, entrada):
    if lenguaje == "java":
        codigo = _utf8_java(_sin_public(codigo))
    elif lenguaje == "ruby":
        # Servidores sin UTF-8: gets daría texto ASCII y mezclarlo con "ñ" falla. Va en la línea 1 para no mover líneas.
        codigo = RUBY_UTF8 + codigo
    codigo = a_ascii(lenguaje, codigo)
    ultimo_fallo = ""
    inicio = time.monotonic()
    for compilador in _compiladores_wandbox(lenguaje):
        if time.monotonic() - inicio > TIEMPO_EN_LINEA:
            break
        cuerpo = json.dumps({"compiler": compilador, "code": codigo, "stdin": entrada or "",
                             "save": False}).encode()
        try:
            d = _pedir_json(WANDBOX + "/api/compile.json", cuerpo, {"Content-Type": "application/json"})
        except _FalloServicio as x:
            ultimo_fallo = str(x)
            continue
        estado, senal = str(d.get("status", "")).strip(), str(d.get("signal", "")).strip()
        compilacion = d.get("compiler_error") or ""
        if compilacion and estado not in ("", "0") and not d.get("program_message"):
            return int(estado) if estado.lstrip("-").isdigit() else 1, d.get("compiler_message") or compilacion
        salida = d.get("program_message") or ((d.get("program_output") or "") + (d.get("program_error") or ""))
        if not estado and not salida and not compilacion:
            ultimo_fallo = senal or "respuesta vacía"
            continue   # falla interna del compilador: se prueba otra versión
        if senal and "Killed" in senal and not salida:
            return 124, "Tiempo agotado: ¿hay un bucle infinito o el programa espera datos del teclado?"
        rc = int(estado) if estado.lstrip("-").isdigit() else (1 if senal else 0)
        return rc, salida
    raise _FalloServicio(ultimo_fallo or "sin compiladores disponibles")


KOTLIN_API = os.getenv("KOTLIN_API_URL", "https://api.kotlinlang.org").rstrip("/")


def _version_kotlin():
    try:
        versiones = _pedir_json(KOTLIN_API + "/versions", tiempo=10)
        estables = [v["version"] for v in versiones if isinstance(v, dict) and v.get("latestStable")]
        if estables:
            return estables[0]
    except (_FalloServicio, KeyError, TypeError):
        pass
    return "2.1.20"


def _kotlin_playground(codigo, entrada):
    cuerpo = json.dumps({"args": "", "confType": "java",
                         "files": [{"name": "File.kt", "text": codigo, "publicId": ""}]}).encode()
    d = _pedir_json(f"{KOTLIN_API}/api/{_version_kotlin()}/compiler/run", cuerpo,
                    {"Content-Type": "application/json"})
    errores = []
    for lista in (d.get("errors") or {}).values():
        for e in lista or []:
            if str(e.get("severity", "")).upper() == "ERROR":
                inicio = (e.get("interval") or {}).get("start") or {}
                linea = f"main.kt:{inicio.get('line', 0) + 1}:{inicio.get('ch', 0) + 1}: " if inicio else ""
                errores.append(f"{linea}error: {e.get('message', '')}")
    if errores:
        return 1, "\n".join(errores)
    texto = d.get("text") or ""
    salida = re.sub(r"</?outStream>", "", texto)
    salida = re.sub(r"<errStream>(.*?)</errStream>", r"\1", salida, flags=re.S)
    exc = d.get("exception")
    if exc:
        salida += f"Exception in thread \"main\" {exc.get('fullName') or exc.get('message') or exc}\n"
        return 1, salida
    if entrada and "readln" in codigo:
        salida += "\n(Nota: Kotlin en línea no recibe datos del teclado; readln() no ve lo que escribiste.)"
    return 0, salida


# ---------------------------------------------------- segundo servicio: Compiler Explorer (godbolt.org) ----
GODBOLT = os.getenv("GODBOLT_URL", "https://godbolt.org").rstrip("/")
GODBOLT_LENGUAJE = {"c": "c", "cpp": "c++", "rust": "rust", "go": "go", "swift": "swift", "kotlin": "kotlin",
                    "csharp": "csharp", "java": "java", "ruby": "ruby", "scala": "scala", "haskell": "haskell", "d": "d",
                    "nim": "nim", "zig": "zig", "ocaml": "ocaml", "pascal": "pascal", "crystal": "crystal"}
_godbolt_lista = {}


def _compiladores_godbolt(lenguaje):
    lang = GODBOLT_LENGUAJE.get(lenguaje)
    if not lang:
        return []
    with _candado:
        guardado = _godbolt_lista.get(lang)
        if guardado and time.time() - guardado[0] < 6 * 3600:
            return guardado[1]
    datos = _pedir_json(f"{GODBOLT}/api/compilers/{lang}?fields=id,name,semver,supportsExecute", None,
                        {"Accept": "application/json"}, tiempo=15)
    candidatos = [c for c in datos if isinstance(c, dict) and c.get("supportsExecute", True) is not False
                  and not re.search(r"trunk|nightly|snapshot|beta|rc\d|assert|clang-tidy|mrustc|gccrs", f"{c.get('id')} {c.get('name')}", re.I)]
    clave = lambda c: [int(x) for x in re.findall(r"\d+", str(c.get("semver") or c.get("name") or ""))[:4]]
    ids = [c["id"] for c in sorted(candidatos, key=clave, reverse=True)][:2]
    with _candado:
        _godbolt_lista[lang] = (time.time(), ids)
    return ids


def _texto_godbolt(partes):
    return "\n".join(str(x.get("text", "")) for x in (partes or []) if isinstance(x, dict))


def _godbolt(lenguaje, codigo, entrada):
    ultimo = None
    for cid in _compiladores_godbolt(lenguaje):
        cuerpo = json.dumps({"source": codigo, "lang": GODBOLT_LENGUAJE[lenguaje], "allowStoreCodeDebug": False, "options": {
            "userArguments": "", "executeParameters": {"args": [], "stdin": entrada or "", "runtimeTools": []},
            "compilerOptions": {"executorRequest": True}, "filters": {"execute": True}, "tools": [], "libraries": []}}).encode()
        d = _pedir_json(f"{GODBOLT}/api/compiler/{cid}/compile", cuerpo, {"Content-Type": "application/json", "Accept": "application/json"})
        r = d.get("execResult") if isinstance(d.get("execResult"), dict) else d
        build = r.get("buildResult") or {}
        if build and build.get("code", 0) != 0:
            return 1, (_texto_godbolt(build.get("stderr")) or _texto_godbolt(build.get("stdout")) or "Error de compilación").rstrip() + "\n"
        if r.get("didExecute") is False and not r.get("stdout"):
            ultimo = (1, _texto_godbolt(r.get("stderr")) or "No se pudo ejecutar.")
            continue
        salida = _texto_godbolt(r.get("stdout"))
        err = _texto_godbolt(r.get("stderr"))
        texto = (salida + ("\n" if salida else "")) + (err + "\n" if err else "")
        return int(r.get("code", 0) or 0), texto
    if ultimo:
        return ultimo
    raise _FalloServicio("Compiler Explorer no tiene compilador para este lenguaje")


def _en_linea(lenguaje, codigo, entrada):
    """Ejecuta en un servicio público: primero Wandbox (o Kotlin Playground) y, si falla, Compiler Explorer.
    Devuelve (rc, texto) o None si ninguno respondió."""
    if not en_linea_activo():
        return None
    servicios = [_kotlin_playground] if lenguaje == "kotlin" else [lambda c, e: _wandbox(lenguaje, c, e)]
    if lenguaje in GODBOLT_LENGUAJE:
        servicios.append(lambda c, e: _godbolt(lenguaje, c, e))
    for servicio in servicios:
        try:
            return servicio(codigo, entrada)
        except _FalloServicio:
            continue
        except Exception:   # respuesta rara de un servicio: se prueba el siguiente
            continue
    return None


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
    "lua": "Instala Lua (luabinaries.sourceforge.net en Windows, `apt install lua5.4` en Linux).",
    "perl": "Instala Perl (strawberryperl.com en Windows).", "Rscript": "Instala R desde cran.r-project.org.",
    "scala-cli": "Instala Scala desde scala-lang.org (trae scala-cli).", "runghc": "Instala Haskell con GHCup (haskell.org/ghcup).",
    "elixir": "Instala Elixir desde elixir-lang.org.", "julia": "Instala Julia desde julialang.org.",
    "groovy": "Instala Groovy (groovy-lang.org) y un JDK.", "crystal": "Instala Crystal desde crystal-lang.org.",
    "nim": "Instala Nim desde nim-lang.org.", "ocaml": "Instala OCaml desde ocaml.org.", "rdmd": "Instala D (dlang.org).",
    "fpc": "Instala Free Pascal desde freepascal.org.", "zig": "Instala Zig desde ziglang.org.",
    "sbcl": "Instala SBCL desde sbcl.org.", "bash": "Instala Git for Windows (trae bash) o usa WSL.",
}


def preparar(lenguaje, codigo, archivos=None):
    """Une los demás archivos del proyecto que hacen falta (clases de Java, .h y .c de C/C++)."""
    archivos = [a for a in (archivos or []) if isinstance(a, dict) and isinstance(a.get("contenido"), str)
                and isinstance(a.get("nombre"), str)][:40]
    if not archivos:
        return codigo
    if lenguaje == "java":
        otros = [a["contenido"] for a in archivos if a["nombre"].endswith(".java") and a["contenido"].strip() != codigo.strip()]
        # Solo un tipo puede ser público por archivo: el de main se queda como está y los demás pierden «public».
        return unir_java(codigo, [_sin_public(o) for o in otros]) if otros else codigo
    if lenguaje in ("c", "cpp"):
        return unir_c(codigo, archivos)
    return codigo


def ejecutar(lenguaje, codigo, entrada="", archivos=None):
    """Devuelve {'salida': texto, 'error': bool, 'donde': 'local'|'piston'|'en_linea'}.
    Lanza ValueError si la petición es inválida."""
    if lenguaje not in LENGUAJES:
        raise ValueError("Ese lenguaje no se ejecuta en el servidor.")
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("Escribe algo de código antes de ejecutar.")
    entrada = entrada if isinstance(entrada, str) else ""
    if len(entrada) > MAX_ENTRADA:
        raise ValueError(f"La entrada es demasiado larga (máximo {MAX_ENTRADA} caracteres).")
    codigo = preparar(lenguaje, codigo, archivos)
    if len(codigo) > MAX_CODIGO:
        raise ValueError(f"El código es demasiado largo (máximo {MAX_CODIGO} caracteres).")
    if entrada and not entrada.endswith("\n"):
        entrada += "\n"

    d = tempfile.mkdtemp(prefix="cc_run_")
    donde = "local"
    try:
        res, falta = LENGUAJES[lenguaje]["f"](codigo, d, entrada)
        if res is None:
            res, donde = _piston(lenguaje, codigo, entrada), "piston"
        if res is None:
            res, donde = _en_linea(lenguaje, codigo, entrada), "en_linea"
        if res is None:
            ayuda = INSTALAR.get(falta, f"Instala {falta}.")
            if en_linea_activo():
                motivo = ("Los servicios en línea (Wandbox / Kotlin Playground) no respondieron: revisa la conexión a "
                          "internet del servidor o inténtalo en un momento.")
            else:
                motivo = "La ejecución en línea está apagada (EJECUCION_EN_LINEA=0 en backend/.env)."
            return {"salida": f"No se pudo ejecutar {NOMBRES[lenguaje]}. {motivo}\n"
                              f"Para ejecutarlo en este equipo sin internet: {ayuda}", "error": True, "donde": ""}
        rc, texto = res
        texto = _arreglar_mojibake(_limpiar(texto or "", d)).replace(RUBY_UTF8, "")
        if lenguaje == "java":
            texto = texto.replace("prog.java", f"{_clase_java(codigo)}.java")
        elif donde == "en_linea":
            ext = {"c": "c", "cpp": "cpp", "csharp": "cs", "php": "php", "go": "go", "rust": "rs", "swift": "swift",
                   "ruby": "rb", "lua": "lua", "perl": "pl", "haskell": "hs", "nim": "nim", "zig": "zig", "d": "d",
                   "ocaml": "ml", "pascal": "pas", "crystal": "cr", "scala": "scala", "julia": "jl"}.get(lenguaje)
            texto = re.sub(r"\bprog\.(?:cc|c|cs|php|go|rs|swift|rb|lua|pl|hs|nim|zig|d|ml|pas|cr|scala|jl)\b", f"main.{ext}", texto) if ext else texto
        if len(texto) > MAX_SALIDA:
            texto = texto[:MAX_SALIDA] + "\n… (salida recortada)"
        return {"salida": texto, "error": rc != 0, "donde": donde}
    finally:
        shutil.rmtree(d, ignore_errors=True)
