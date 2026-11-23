"""Detección de errores en Trabajo (sin ejecutar el código), como los subrayados rojos de VS Code.

Devuelve una lista de problemas [{linea, columna, fin_linea, fin_columna, mensaje, grave}] para un archivo.
  · Python: compile() para la sintaxis + pyflakes (nombres sin definir, imports sin usar…), con mensajes en español.
  · Java (javac), C/C++ (gcc/g++ -fsyntax-only), Go (gofmt -e), PHP (php -l), Ruby (ruby -wc), Bash (bash -n), Lua (luac -p):
    solo se usan los que estén instalados y todos revisan sin ejecutar nada.
JavaScript, TypeScript, CSS, JSON y HTML se revisan en el navegador (Monaco y trabajo/analisis.js).
"""
import ast
import os
import re
import shutil
import tempfile

from servicios.ejecutor import _correr, _limpiar

MAX_CODIGO = 200_000
TIEMPO_ANALISIS = 8


def _p(linea, mensaje, grave=True, columna=1, fin_columna=None):
    linea = max(1, int(linea or 1))
    columna = max(1, int(columna or 1))
    return {"linea": linea, "columna": columna, "fin_linea": linea, "fin_columna": fin_columna or columna + 1,
            "mensaje": mensaje.strip()[:400], "grave": grave}


# ------------------------------------------------------------------------------------------------ Python ----
_PY_ES = [
    (r"^invalid syntax\. Perhaps you forgot a comma\?$", "Sintaxis inválida: ¿te faltó una coma?"),
    (r"^invalid syntax$", "Sintaxis inválida"),
    (r"^expected ':'$", "Falta «:» al final de la línea"),
    (r"^'(.)' was never closed$", r"El «\1» nunca se cerró"),
    (r"^unmatched '(.)'$", r"Sobra un «\1» (no tiene pareja)"),
    (r"^closing parenthesis '(.)' does not match opening parenthesis '(.)'.*$", r"El «\1» no corresponde con el «\2» que abriste"),
    (r"^unexpected indent$", "Sangría inesperada: esta línea tiene espacios de más"),
    (r"^expected an indented block.*$", "Falta la sangría: después de «:» la línea siguiente va con espacios"),
    (r"^unindent does not match any outer indentation level$", "La sangría no coincide con ninguna de las anteriores"),
    (r"^unterminated string literal.*$", "Falta cerrar las comillas del texto"),
    (r"^unterminated triple-quoted string literal.*$", "Falta cerrar las comillas triples"),
    (r"^EOL while scanning string literal$", "Falta cerrar las comillas del texto"),
    (r"^invalid character '(.)' .*$", r"Carácter no válido «\1» (¿comillas o signos copiados de otro lado?)"),
    (r"^Missing parentheses in call to 'print'.*$", "En Python 3 «print» lleva paréntesis: print(...)"),
    (r"^cannot assign to (.*)$", r"No se puede asignar a \1"),
    (r"^'return' outside function$", "«return» fuera de una función"),
    (r"^'break' outside loop$", "«break» fuera de un bucle"),
    (r"^'continue' not properly in loop$", "«continue» fuera de un bucle"),
    (r"^invalid decimal literal$", "Número no válido (¿un nombre que empieza con número?)"),
    (r"^Did you mean '(.+)'\?$", r"¿Quisiste decir «\1»?"),
    (r"^undefined name '(.+)'$", r"«\1» no está definido (¿lo escribiste bien o falta crearlo?)"),
    (r"^'(.+)' imported but unused$", r"Importaste «\1» pero no lo usas"),
    (r"^local variable '(.+)' is assigned to but never used$", r"La variable «\1» se crea pero nunca se usa"),
    (r"^redefinition of unused '(.+)' from line (\d+)$", r"«\1» ya se había definido en la línea \2 y no se usó"),
    (r"^'(.+)' may be undefined, or defined from star imports: (.+)$", r"«\1» quizá no existe (viene de «from \2 import *»)"),
    (r"^f-string is missing placeholders$", "El f-string no tiene ningún {…}: quita la f o agrega una variable"),
    (r"^import '(.+)' from line (\d+) shadowed by loop variable$", r"El bucle tapa el import «\1» de la línea \2"),
    (r"^dictionary key (.+) repeated with different values$", r"La clave \1 del diccionario está repetida"),
    (r"^'\.\.\.'\.format\(\.\.\.\) has unused arguments.*$", "format() recibe argumentos que no se usan"),
    (r"^use of >> is invalid with print function$", "Con print() no se usa >>"),
    (r"^'(.+)' is not callable.*$", r"«\1» no se puede llamar como función"),
]
# Avisos (no errores) de pyflakes
_PY_AVISOS = ("imported but unused", "is assigned to but never used", "redefinition of unused", "f-string is missing placeholders",
              "shadowed by loop variable", "may be undefined, or defined from star imports")


def _es(mensaje):
    for patron, rep in _PY_ES:
        if re.match(patron, mensaje):
            return re.sub(patron, rep, mensaje)
    return mensaje


def _python(codigo):
    try:
        ast.parse(codigo)
    except SyntaxError as e:
        col = e.offset or 1
        fin = e.end_offset if getattr(e, "end_offset", None) and e.end_lineno == e.lineno else col + 1
        return [_p(e.lineno or 1, _es(e.msg or "Sintaxis inválida"), True, col, max(fin, col + 1))]
    except (ValueError, MemoryError, RecursionError) as e:
        return [_p(1, f"No se pudo analizar: {e}")]
    try:
        from pyflakes import api as pf_api
        from pyflakes import reporter as pf_rep
    except ImportError:
        return []
    salida = []

    class Rep(pf_rep.Reporter):
        def __init__(self):
            pass

        def unexpectedError(self, nombre, msg):
            pass

        def syntaxError(self, nombre, msg, linea, offset, texto):
            salida.append(_p(linea, _es(msg), True, offset or 1))

        def flake(self, m):
            texto = m.message % m.message_args
            grave = not any(a in texto for a in _PY_AVISOS)
            salida.append(_p(m.lineno, _es(texto), grave, (m.col or 0) + 1))

    pf_api.check(codigo, "main.py", Rep())
    return salida[:200]


# ------------------------------------------------------------------------------------------- compiladores ----
# lenguaje: (archivo, comando, patrón «archivo:línea[:columna]: mensaje»)
_RE_GCC = re.compile(r"^[^:\n]+:(\d+):(\d+):\s*(fatal error|error|warning):\s*(.+)$", re.M)
_HERRAMIENTAS = {
    "c": ("main.c", lambda f: ["gcc", "-fsyntax-only", "-Wall", "-std=c17", f], _RE_GCC),
    "cpp": ("main.cpp", lambda f: ["g++", "-fsyntax-only", "-Wall", "-std=c++20", f], _RE_GCC),
    "java": ("Main.java", lambda f: ["javac", "-Xlint:none", "-Xmaxerrs", "50", "-d", "clases", f],
             re.compile(r"^[^:\n]+\.java:(\d+):\s*(error|warning):\s*(.+)$", re.M)),
    "go": ("main.go", lambda f: ["gofmt", "-e", "-l", f], re.compile(r"^[^:\n]+:(\d+):(\d+):\s*(.+)$", re.M)),
    "php": ("main.php", lambda f: ["php", "-l", "-d", "display_errors=1", f],
            re.compile(r"^(?:PHP )?(Parse error|Fatal error|Warning):\s*(.+?) in .+? on line (\d+)", re.M)),
    "ruby": ("main.rb", lambda f: ["ruby", "-wc", f], re.compile(r"^(?:ruby: )?[^:\n]+\.rb:(\d+):\s*(?:(warning):\s*)?(.+)$", re.M)),
    "shell": ("main.sh", lambda f: ["bash", "-n", f], re.compile(r"^[^:\n]+: (?:line|línea) (\d+): (.+)$", re.M)),
    "lua": ("main.lua", lambda f: ["luac", "-p", f], re.compile(r"^luac: [^:\n]+:(\d+):\s*(.+)$", re.M)),
}
_EXTENSIONES = {"py": "python", "c": "c", "h": "c", "cpp": "cpp", "cc": "cpp", "cxx": "cpp", "hpp": "cpp", "java": "java", "go": "go",
                "php": "php", "rb": "ruby", "sh": "shell", "bash": "shell", "lua": "lua"}
_DE_GCC = [(r"expected '(.+)' or '(.+)' before '(.+)'", r"Falta «\1» o «\2» antes de «\3»"), (r"unused variable '(.+)'.*", r"La variable «\1» no se usa"),
           (r"expected '(.+)' before '(.+)'", r"Falta «\1» antes de «\2»"), (r"'(.+)' undeclared.*", r"«\1» no está declarado"),
           (r"unknown type name '(.+)'", r"Tipo desconocido «\1»"), (r"expected ';'.*", "Falta «;»"),
           (r"use of undeclared identifier '(.+)'", r"«\1» no está declarado"), (r"'(.+)' was not declared in this scope.*", r"«\1» no está declarado")]
_DE_JAVA = [(r"';' expected", "Falta «;»"), (r"cannot find symbol", "No se encuentra ese nombre (¿está bien escrito o falta declararlo?)"),
            (r"incompatible types: (.+) cannot be converted to (.+)", r"Tipos incompatibles: \1 no se puede convertir a \2"),
            (r"reached end of file while parsing", "El archivo termina antes de tiempo: falta cerrar una «}»"),
            (r"class, interface, enum, or record expected", "Se esperaba una clase (¿sobra una «}»?)"),
            (r"'\)' expected", "Falta «)»"), (r"not a statement", "Eso no es una instrucción válida"),
            (r"missing return statement", "Falta el «return»"), (r"unclosed string literal", "Falta cerrar las comillas")]


_CLASES_JAVA = ["System", "String", "Math", "Integer", "Double", "Float", "Long", "Boolean", "Character", "Object", "Scanner", "ArrayList",
                "List", "HashMap", "Map", "HashSet", "Set", "Arrays", "Collections", "StringBuilder", "Exception", "Thread", "Random", "LocalDate"]


def _traducir(mensaje, tabla):
    for patron, rep in tabla:
        if re.search(patron, mensaje):
            return re.sub(patron, rep, mensaje)
    return mensaje


def lenguaje_de(ruta, lenguaje=None):
    if lenguaje in _HERRAMIENTAS or lenguaje == "python":
        return lenguaje
    ext = os.path.splitext(ruta or "")[1].lstrip(".").lower()
    return _EXTENSIONES.get(ext)


def disponibles():
    """Lenguajes que este servidor puede revisar."""
    hay = ["python"]
    for lang, (_, cmd, _) in _HERRAMIENTAS.items():
        if shutil.which(cmd("x")[0]):
            hay.append(lang)
    return hay


def analizar(codigo, ruta="", lenguaje=None):
    """Lista de problemas del archivo (vacía si no hay o si no se puede revisar ese lenguaje aquí)."""
    if not isinstance(codigo, str) or len(codigo) > MAX_CODIGO:
        return []
    lang = lenguaje_de(ruta, lenguaje)
    if lang == "python":
        return _python(codigo)
    herr = _HERRAMIENTAS.get(lang)
    if not herr:
        return []
    nombre, comando, patron = herr
    if lang == "java":   # javac exige que el archivo se llame como la clase pública
        m = re.search(r"public\s+(?:final\s+|abstract\s+)*(?:class|interface|enum|record)\s+(\w+)", codigo)
        nombre = f"{m.group(1)}.java" if m else "Main.java"
    if lang in ("c", "cpp") and re.search(r'#\s*include\s*[<"]\s*(/|\.\.)', codigo):   # no leer archivos del servidor
        return [_p(1, "Por seguridad no se revisan #include con rutas absolutas o «..».", False)]
    cmd = comando(nombre)
    if not shutil.which(cmd[0]):
        return []

    def compilar(texto):
        with tempfile.TemporaryDirectory(prefix="cc_lint_") as carpeta:
            os.makedirs(os.path.join(carpeta, "clases"), exist_ok=True)
            with open(os.path.join(carpeta, nombre), "w", encoding="utf-8") as f:
                f.write(texto)
            _, sal = _correr(cmd, carpeta, tiempo=TIEMPO_ANALISIS, compilar=True)
            return _limpiar(sal, carpeta).replace("‘", "'").replace("’", "'")

    salida = compilar(codigo)
    # C/C++: el servidor ve un solo archivo; un #include que no tiene (tu .h, mysql.h, una librería de tu equipo) no es
    # un error de tu código. Se aparta esa línea y se revisa el resto (como hace VS Code cuando falta una ruta de include).
    sin_include = set()
    if lang in ("c", "cpp"):
        lineas = codigo.split("\n")
        for _ in range(8):
            m = re.search(r"^[^:\n]+:(\d+):\d+:\s*fatal error:\s*[^:\n]+: No such file or directory", salida, re.M)
            if not m:
                break
            n = int(m.group(1))
            if n < 1 or n > len(lineas) or not re.match(r"\s*#\s*include", lineas[n - 1]) or n in sin_include:
                break
            sin_include.add(n)
            lineas[n - 1] = ""
            salida = compilar("\n".join(lineas))
    importados = {x.split(".")[-1] for x in re.findall(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;", codigo, re.M)} if lang == "java" else set()
    problemas = []
    for m in patron.finditer(salida):
        g = m.groups()
        if lang in ("c", "cpp"):
            linea, col, tipo, msg = g
            # Con un #include apartado, lo que venía de ese archivo (tipos, funciones) no se conoce: no se marca
            if sin_include and re.search(r"undeclared|not declared|unknown type name|implicit declaration|has no member|incomplete type|"
                                         r"storage size|does not name a type|is not a (?:namespace|member)|no matching function|"
                                         r"has not been declared|invalid use of|was not declared|makes (?:pointer|integer) from|incompatible implicit", msg):
                continue
            problemas.append(_p(linea, _traducir(msg, _DE_GCC), tipo != "warning", col))
        elif lang == "java":
            linea, tipo, msg = g
            # Un archivo solo no ve las otras clases de tu proyecto ni las librerías (Spring, MySQL…): eso no es error tuyo
            simbolo = re.search(r"^\s*symbol:\s+(\w+)\s+([\w.]+)", salida[m.end():m.end() + 400], re.M)
            de_fuera = bool(simbolo) and (simbolo.group(1) in ("class", "interface", "enum", "record", "static")
                                          or (simbolo.group(1) == "variable" and simbolo.group(2)[:1].isupper())   # Clase.metodo()
                                          or simbolo.group(2).split(".")[0] in importados)
            paquete = re.match(r"package (\w+) does not exist", msg)   # «Sytem.out»: javac cree que Sytem es un paquete
            nombre_raro = simbolo.group(2).split(".")[0] if (simbolo and de_fuera) else (paquete.group(1) if paquete else None)
            if nombre_raro:   # ¿un error al escribir System, String, Scanner…? eso sí se marca
                import difflib
                parecido = difflib.get_close_matches(nombre_raro, _CLASES_JAVA, n=1, cutoff=0.8)
                if parecido and parecido[0] != nombre_raro:
                    problemas.append(_p(linea, f"«{nombre_raro}» no existe. ¿Quisiste decir «{parecido[0]}»?", True))
                    continue
            if re.search(r"package .+ does not exist|^package \S+ is not visible|is public, should be declared in a file named", msg) or (
                    "cannot find symbol" in msg and de_fuera):
                continue
            problemas.append(_p(linea, _traducir(msg, _DE_JAVA), tipo == "error"))
        elif lang == "go":
            linea, col, msg = g
            problemas.append(_p(linea, msg, True, col))
        elif lang == "php":
            tipo, msg, linea = g
            if "No syntax errors" not in msg:
                problemas.append(_p(linea, msg, tipo != "Warning"))
        elif lang == "ruby":
            linea, aviso, msg = g
            if msg.strip() != "Syntax OK":
                problemas.append(_p(linea, msg, not aviso))
        else:
            linea, msg = g
            problemas.append(_p(linea, msg, True))
    vistos, unicos = set(), []
    for x in problemas:   # sin repetidos
        k = (x["linea"], x["mensaje"])
        if k not in vistos:
            vistos.add(k)
            x["mensaje"] = re.sub(r"\s*\((?:SyntaxError)\)$", "", x["mensaje"])
            unicos.append(x)
    return unicos[:200]
