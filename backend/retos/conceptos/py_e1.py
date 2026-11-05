"""Python · Etapa 1: qué es Python (casi todo teoría)."""
from ..generador import K

LISTA = [
K("Qué es Python",
  d="lenguaje de programación sencillo, legible y muy versátil",
  u="programar desde cosas simples hasta inteligencia artificial",
  mas="Python se creó en 1991 con la idea de que el código se lea casi como inglés. Es uno de los lenguajes más populares del mundo y el favorito para empezar. Se usa en páginas web, análisis de datos, automatización, videojuegos e inteligencia artificial.",
  k=["Python es un lenguaje de programación fácil de leer.", "Se usa en web, datos, automatización e inteligencia artificial.", "Es muy recomendado para empezar a programar."],
  sit="Buscas un lenguaje fácil de leer para empezar a programar y que luego sirva para muchas cosas. ¿Qué eliges?",
  cod="""# Un programa en Python se lee casi como una frase
nombre = "Ana"
print("Hola,", nombre)
print("Python es fácil de leer")""",
  h="guarda un nombre y muestra dos mensajes",
  pr=("El lenguaje que se lee casi como inglés y es ideal para empezar es ___. (6 letras)", "python"),
  pr2=("Python se usa en web, datos, automatización e inteligencia ___. (10 letras)", "artificial"),
  ec="creer que Python solo sirve para principiantes"),
K("Para qué sirve Python",
  d="repaso de los campos donde se usa Python hoy",
  u="saber qué puedes construir con lo que aprendas",
  mas="Con Python se analizan datos (pandas), se crean sitios web (Django, Flask), se automatizan tareas aburridas, se programan robots y se entrenan modelos de inteligencia artificial. Empresas como Google, Netflix o Instagram lo usan.",
  k=["Python se usa para analizar datos y crear sitios web.", "Se puede usar para automatizar tareas repetitivas.", "Grandes empresas usan Python."],
  sit="Te preguntas si Python sirve para crear sitios web, analizar datos y automatizar tareas. ¿Qué analizas?",
  cod="""usos = ["análisis de datos", "sitios web", "automatización", "inteligencia artificial"]
print("Con Python puedes hacer:")
for uso in usos:
    print("-", uso)""",
  h="lista cuatro usos de Python recorriendo una lista",
  pr=("Una librería muy usada de Python para analizar datos es ___. (6 letras)", "pandas"),
  pr2=("Flask y Django sirven para crear sitios ___. (3 letras)", "web"),
  ec="pensar que Python solo sirve para hacer scripts pequeños"),
K("Lenguaje interpretado",
  d="lenguaje que se ejecuta línea a línea sin compilar antes",
  u="probar código rápido y ver errores al instante",
  mas="Python lee y ejecuta tu código instrucción por instrucción mediante un intérprete. Puedes escribir una línea y ver el resultado al momento, algo ideal para aprender. A cambio, suele ser más lento que lenguajes compilados como C.",
  k=["Python ejecuta el código línea a línea con un intérprete.", "No hace falta compilar antes de ejecutar.", "Suele ser más lento que los lenguajes compilados."],
  sit="Quieres escribir una línea de código y ver su resultado al instante sin compilar nada. ¿Qué característica tiene Python?",
  cod="""print("Primera línea: se ejecuta al momento")
print(2 + 3)
print("El intérprete va leyendo línea a línea")""",
  h="ejecuta tres líneas una tras otra sin compilar",
  pr=("El programa que lee y ejecuta tu código Python se llama ___. (11 letras)", "intérprete", "interprete"),
  pr2=("Python ___ necesita compilar antes de ejecutar. (no)", "no"),
  ec="creer que hay que compilar un programa Python antes de correrlo"),
K("Python 3",
  d="versión actual y única recomendada del lenguaje",
  u="saber qué versión usar y evitar tutoriales antiguos",
  mas="Python 2 dejó de recibir soporte en 2020. Hoy todo se hace con Python 3 (3.12 o superior). Si un tutorial usa print \"hola\" sin paréntesis, es de Python 2 y no funcionará. Para ver tu versión: python --version.",
  k=["Hoy se usa Python 3.", "Python 2 dejó de tener soporte en 2020.", "En Python 3, print lleva paréntesis."],
  sit="Un tutorial usa print \"hola\" sin paréntesis y te da error. ¿De qué versión es ese código?",
  cod="""import sys
print(sys.version_info.major >= 3)     # True: estamos en Python 3
print("print lleva paréntesis en Python 3")""",
  h="comprueba que se está usando Python 3",
  pr=("La versión de Python que se usa hoy es la ___. (un número)", "3"),
  pr2=("Python 2 dejó de recibir soporte en el año ___. (4 números)", "2020"),
  ec="seguir tutoriales de Python 2 con print sin paréntesis",
  err=("print(\"Hola\")\nprint \"Adiós\"", 2, "En Python 3, print es una función y lleva paréntesis: print(\"Adiós\").")),
K("Instalar Python",
  d="proceso de poner el intérprete de Python en tu computadora",
  u="poder ejecutar programas Python en tu equipo",
  mas="Se descarga de python.org. En Windows, marca la casilla «Add Python to PATH» al instalar; así podrás usar python desde cualquier carpeta. Al terminar, comprueba con python --version (o python3 --version en Mac y Linux).",
  k=["Python se descarga desde python.org.", "En Windows conviene marcar «Add Python to PATH».", "python --version comprueba la instalación."],
  sit="Quieres poder ejecutar Python desde cualquier carpeta de tu computadora en Windows. ¿Qué marcas al instalar?",
  cod="""# En la terminal (no es código Python):
#   python --version
# Si todo va bien muestra algo como: Python 3.12.2
import platform
print("Versión instalada:", platform.python_version())""",
  h="muestra la versión de Python instalada",
  pr=("La página oficial para descargar Python es python.___. (3 letras)", "org"),
  pr2=("En Windows hay que marcar «Add Python to ___». (4 letras)", "path"),
  ec="olvidar marcar PATH y no poder ejecutar python desde la terminal"),
K("La terminal y el REPL",
  d="entornos donde escribes y ejecutas Python directamente",
  u="probar ideas rápido sin crear archivos",
  mas="Si escribes python en la terminal, entras al REPL (Read-Eval-Print Loop): escribes una instrucción, Python la evalúa e imprime el resultado. Se reconoce por el símbolo >>>. Se sale con exit() o Ctrl+Z / Ctrl+D.",
  k=["El REPL ejecuta una instrucción y muestra su resultado.", "Se reconoce por el símbolo >>>.", "Se sale con exit()."],
  sit="Quieres probar una operación suelta escribiéndola y viendo el resultado al instante, sin crear un archivo. ¿Qué usas?",
  cod="""# En el REPL verías:
# >>> 2 + 3
# 5
# >>> "hola".upper()
# 'HOLA'
print(2 + 3)
print("hola".upper())""",
  h="reproduce dos operaciones que probarías en el REPL",
  pr=("El símbolo que muestra el REPL de Python es ___. (3 caracteres)", ">>>"),
  pr2=("Para salir del REPL se escribe ___(). (4 letras)", "exit", "quit"),
  ec="guardar código largo en el REPL en lugar de un archivo"),
K("Tu primer programa con print",
  d="programa que muestra un mensaje en pantalla",
  u="ver resultados y comprobar que funciona el código",
  mas="print() muestra en pantalla lo que le pases: textos entre comillas, números o varios valores separados por comas. Después de cada print, Python salta de línea. Es tu herramienta principal para ver qué hace tu programa.",
  k=["print() muestra información en pantalla.", "Los textos van entre comillas.", "Se pueden mostrar varios valores separados por comas."],
  sit="Quieres mostrar «Hola, mundo» en pantalla. ¿Qué función usas?",
  cod="""print("Hola, mundo")
print("Tengo", 20, "años")        # varios valores separados por comas
print(7 * 6)                      # también resultados de operaciones""",
  h="muestra un saludo, una frase con un número y un cálculo",
  pr=("La función que muestra algo en pantalla es ___(). (5 letras)", "print"),
  pr2=("Los textos en Python van entre ___. (comillas)", "comillas"),
  ec="olvidar las comillas del texto",
  err=("print(\"Hola\")\nprint(Adiós)", 2, "Falta poner comillas: print(\"Adiós\").")),
K("Archivo .py",
  d="archivo de texto con código Python que termina en .py",
  u="guardar un programa y ejecutarlo cuando quieras",
  mas="Creas un archivo, por ejemplo hola.py, escribes tu código y lo guardas. En la terminal ejecutas python hola.py desde su carpeta. Python ejecuta el archivo de arriba abajo. Los nombres de archivo no deben llevar espacios ni empezar por números.",
  k=["Un archivo Python termina en .py.", "Se ejecuta con python nombre.py.", "Python ejecuta el archivo de arriba abajo."],
  sit="Quieres guardar tu programa en un archivo y ejecutarlo cuando quieras. ¿Qué extensión le pones?",
  cod="""# Guarda esto como hola.py y ejecútalo con:  python hola.py
print("Estoy dentro de un archivo .py")
print("Python ejecuta de arriba abajo")""",
  h="muestra dos mensajes pensados para guardarse en hola.py",
  pr=("Un archivo de Python termina en ___. (3 caracteres con punto)", ".py", "py"),
  pr2=("Para ejecutar hola.py se escribe python ___.py. (4 letras)", "hola"),
  ec="guardar el archivo como .txt"),
K("Comentarios en Python",
  d="notas que empiezan con # y que Python ignora",
  u="explicar el código y desactivar líneas",
  mas="Todo lo que sigue a # en una línea se ignora. Los comentarios explican el porqué del código, no lo evidente. También puedes comentar una línea para desactivarla mientras pruebas. Los textos de varias líneas con triple comilla se usan como documentación (docstrings).",
  k=["Los comentarios empiezan con #.", "Python ignora los comentarios.", "Un comentario debería explicar el porqué del código."],
  sit="Quieres dejar una nota en el código que Python no ejecute. ¿Qué símbolo usas?",
  cod="""# Esto es un comentario: Python lo ignora
print("Esto sí se ejecuta")     # también se puede comentar al final de una línea
# print("Esta línea está desactivada")""",
  h="deja notas que se ignoran y una línea desactivada",
  pr=("Los comentarios en Python empiezan con el símbolo ___. (un carácter)", "#"),
  pr2=("Python ___ los comentarios al ejecutar. (7 letras: ignora)", "ignora"),
  ec="usar // como comentario como en otros lenguajes",
  err=("print(\"Hola\")\n// esto es un comentario\nprint(\"Adiós\")", 2, "En Python los comentarios empiezan con #, no con //.")),
K("Indentación",
  d="sangría que indica qué líneas pertenecen a un bloque",
  u="estructurar el código: la sangría es parte de la sintaxis",
  mas="En Python, los bloques (if, for, def) se marcan con sangría de 4 espacios en lugar de llaves. Si la sangría es incorrecta, Python da IndentationError. Todas las líneas de un mismo bloque deben tener la misma sangría. No mezcles tabuladores y espacios.",
  k=["En Python, la sangría define los bloques de código.", "La convención es usar 4 espacios.", "Una sangría incorrecta provoca IndentationError."],
  sit="Quieres indicar qué líneas pertenecen al interior de un if. ¿Qué usas en Python?",
  cod="""edad = 20
if edad >= 18:
    print("Eres mayor de edad")      # sangría de 4 espacios: dentro del if
    print("Puedes votar")            # también dentro
print("Esto se ejecuta siempre")     # sin sangría: fuera del if""",
  h="usa sangría para separar lo que va dentro del if de lo que va fuera",
  pr=("La convención de sangría en Python es ___ espacios. (un número)", "4", "cuatro"),
  pr2=("Una sangría incorrecta produce un ___Error. (11 letras: Indentation)", "indentation"),
  ec="mezclar tabuladores y espacios",
  err=("edad = 20\nif edad >= 18:\nprint(\"Mayor\")", 3, "Falta la sangría: la línea dentro del if debe llevar 4 espacios.")),
K("Código legible",
  d="estilo de escribir código claro, como pide el Zen de Python",
  u="que otras personas (y tú mañana) entiendan tu programa",
  mas="El Zen de Python (import this) resume la filosofía: «Legible cuenta», «Simple es mejor que complejo», «Explícito es mejor que implícito». Escribir pensando en quien leerá el código es tan importante como que funcione.",
  k=["La legibilidad es un valor central en Python.", "Simple es mejor que complejo.", "Se programa pensando en quien leerá el código."],
  sit="Quieres entender la filosofía de Python resumida en frases como «Simple es mejor que complejo». ¿Qué consultas?",
  cod="""# Compara: ¿cuál se entiende mejor?
t = 20 * 0.21 + 20                       # difícil de entender
precio = 20
iva = precio * 0.21                      # claro: se entiende cada paso
total = precio + iva
print(total)""",
  h="compara un cálculo confuso con otro claro paso a paso",
  pr=("Para ver la filosofía de Python se escribe import ___. (4 letras)", "this"),
  pr2=("Según el Zen de Python, simple es mejor que ___. (8 letras: complejo)", "complejo"),
  ec="escribir código muy corto pero imposible de entender"),
K("Qué es una variable en Python",
  d="nombre que apunta a un valor guardado en memoria",
  u="recordar datos para usarlos más tarde",
  mas="En Python creas una variable simplemente asignándole un valor con =, sin declarar su tipo. nombre = \"Ana\" crea la variable y apunta al texto «Ana». Puedes volver a asignarle otro valor, incluso de otro tipo. Las irás usando en toda la etapa siguiente.",
  k=["Una variable se crea asignándole un valor con =.", "No hace falta declarar el tipo.", "El valor de una variable puede cambiar."],
  sit="Quieres guardar la edad de alguien para usarla en varios sitios del programa. ¿Qué creas?",
  cod="""edad = 20                # se crea al asignar
print(edad)
edad = 21                # se puede cambiar
print(edad)
edad = "veintiuno"       # incluso a otro tipo (no siempre recomendable)
print(edad)""",
  h="crea una variable y cambia su valor, incluso de tipo",
  pr=("El símbolo que asigna un valor a una variable es ___. (un carácter)", "="),
  pr2=("En Python ___ hace falta declarar el tipo de una variable. (no)", "no"),
  ec="usar un nombre de variable antes de asignarle valor"),
K("Qué es un tipo de dato en Python",
  d="clase de valor: texto, entero, decimal o booleano",
  u="saber qué operaciones se pueden hacer con cada dato",
  mas="Los tipos básicos son str (texto), int (entero), float (decimal) y bool (True o False). La función type() dice de qué tipo es un valor. Cada tipo permite operaciones distintas: se puede sumar 2 + 3, y también unir textos con +, pero no sumar un texto con un número.",
  k=["Los tipos básicos son str, int, float y bool.", "type() devuelve el tipo de un valor.", "No se puede sumar un texto con un número directamente."],
  sit="Quieres saber si el valor de una variable es un texto, un entero o un decimal. ¿Qué función usas?",
  cod="""print(type("hola"))      # <class 'str'>
print(type(42))          # <class 'int'>
print(type(3.14))        # <class 'float'>
print(type(True))        # <class 'bool'>""",
  h="muestra el tipo de cuatro valores distintos",
  pr=("La función que devuelve el tipo de un valor es ___(). (4 letras)", "type"),
  pr2=("El tipo de los números enteros se llama ___. (3 letras)", "int"),
  ec="intentar sumar un texto con un número"),
K("Qué es una función en Python",
  d="bloque de código con nombre que se ejecuta al llamarlo",
  u="no repetir código y organizar el programa",
  mas="Se define con la palabra def y se ejecuta escribiendo su nombre con paréntesis. Puede recibir datos y devolver un resultado. print() y len() son funciones que ya trae Python; tú crearás las tuyas. Las verás en detalle en la etapa 3.",
  k=["Una función se define con def.", "Se ejecuta escribiendo su nombre con paréntesis.", "Python incluye muchas funciones ya hechas."],
  sit="Quieres agrupar tres líneas de código bajo un nombre para usarlas varias veces. ¿Qué creas?",
  cod="""def saludar():
    print("¡Hola!")
    print("Bienvenida a Python")

saludar()        # primera llamada
saludar()        # segunda llamada""",
  h="define un saludo una vez y lo ejecuta dos veces",
  pr=("La palabra que define una función en Python es ___. (3 letras)", "def"),
  pr2=("Una función que Python ya trae incorporada es ___(). (5 letras: print)", "print", "len", "type"),
  ec="definir la función y olvidar llamarla"),
K("Módulos y librerías",
  d="archivos de código listos para importar y reutilizar",
  u="usar funciones ya hechas sin escribirlas",
  mas="import math trae el módulo math con funciones matemáticas (math.sqrt). Python incluye una gran «biblioteca estándar»: random, datetime, json, os… Además existen miles de librerías de terceros (requests, pandas). Con import accedes a todas.",
  k=["import trae un módulo para usar sus funciones.", "Python incluye una biblioteca estándar muy completa.", "Existen miles de librerías de terceros."],
  sit="Quieres usar funciones matemáticas ya hechas, como la raíz cuadrada. ¿Qué haces?",
  cod="""import math
print(math.sqrt(16))        # 4.0
print(math.pi)              # 3.14159...
import random
print(random.randint(1, 1))  # número entero entre 1 y 1 (siempre 1)""",
  h="importa dos módulos y usa algunas de sus funciones",
  pr=("La palabra que trae un módulo es ___. (6 letras)", "import"),
  pr2=("Un módulo de Python para matemáticas se llama ___. (4 letras)", "math"),
  ec="usar math.sqrt sin importar antes math",
  err=("print(math.sqrt(25))\nimport math", 1, "Hay que importar math antes de usarlo.")),
K("pip",
  d="gestor que instala librerías externas de Python",
  u="añadir herramientas creadas por la comunidad",
  mas="pip install requests descarga e instala la librería requests desde PyPI, el repositorio oficial. pip list muestra lo instalado y pip uninstall elimina una librería. Se ejecuta en la terminal, no dentro de Python.",
  k=["pip instala librerías externas.", "Las librerías se descargan de PyPI.", "pip se usa en la terminal, no dentro del código."],
  sit="Quieres instalar la librería requests para pedir datos a internet. ¿Qué herramienta usas?",
  cod="""# En la terminal (no es código Python):
#   pip install requests
#   pip list
#   pip uninstall requests
print("pip se ejecuta en la terminal, no en Python")""",
  h="resume tres comandos de pip que se escriben en la terminal",
  pr=("El comando que instala una librería es pip ___. (7 letras)", "install"),
  pr2=("El repositorio oficial de librerías de Python se llama ___. (4 letras)", "pypi"),
  ec="escribir pip install dentro de un archivo .py"),
K("Entornos virtuales",
  d="carpetas aisladas con sus propias librerías para cada proyecto",
  u="evitar conflictos entre proyectos distintos",
  mas="Con python -m venv .venv creas un entorno. Al activarlo, pip instala solo dentro de él. Así un proyecto puede usar una versión de una librería y otro una distinta. Es un hábito profesional: un entorno por cada proyecto.",
  k=["Un entorno virtual aísla las librerías de cada proyecto.", "Se crea con python -m venv.", "Conviene tener un entorno por proyecto."],
  sit="Dos proyectos necesitan versiones distintas de la misma librería. ¿Qué usas para separarlos?",
  cod="""# En la terminal:
#   python -m venv .venv
#   .venv\\Scripts\\activate        (Windows)
#   source .venv/bin/activate      (Mac y Linux)
#   pip install requests
import sys
print("Python en uso:", sys.prefix != sys.base_prefix)""",
  h="resume cómo crear y activar un entorno virtual",
  pr=("El módulo que crea entornos virtuales se llama ___. (4 letras)", "venv"),
  pr2=("Un entorno virtual aísla las ___ de cada proyecto. (10 letras: librerías)", "librerías", "librerias"),
  ec="instalar todas las librerías en el Python global"),
K("Errores y tracebacks",
  d="mensajes que indican qué falló y en qué línea",
  u="encontrar y corregir errores",
  mas="Python imprime un traceback: el recorrido hasta el error, con archivo, número de línea y tipo (NameError, TypeError, SyntaxError…). Se lee de abajo hacia arriba: la última línea es el error real. Léelo entero antes de cambiar nada.",
  k=["Un traceback indica la línea y el tipo del error.", "La última línea del traceback es el error real.", "Se debe leer el mensaje completo antes de cambiar el código."],
  sit="Tu programa se detiene y muestra varias líneas con un número de línea y un tipo de error. ¿Qué es eso?",
  cod="""try:
    print(variable_inexistente)
except NameError as error:
    print("Tipo:", type(error).__name__)
    print("Mensaje:", error)""",
  h="captura un NameError y muestra su tipo y su mensaje",
  pr=("El error por usar una variable que no existe es un ___Error. (4 letras: Name)", "name"),
  pr2=("El traceback se lee de abajo hacia ___. (6 letras)", "arriba"),
  ec="ignorar el traceback y cambiar código al azar"),
K("PEP 8",
  d="guía de estilo oficial para escribir código Python",
  u="que todo el código Python se vea parecido y sea legible",
  mas="PEP 8 recomienda nombres en minúsculas con guion bajo (nombre_completo), 4 espacios de sangría, líneas de hasta 79 caracteres y espacios alrededor de los operadores. Herramientas como flake8, black o ruff lo revisan o lo aplican por ti.",
  k=["PEP 8 es la guía de estilo de Python.", "Los nombres de variables usan minúsculas y guion bajo.", "Herramientas como black aplican el estilo automáticamente."],
  sit="Quieres seguir la guía oficial de estilo para que tu código se vea como el de otros programadores de Python. ¿Qué sigues?",
  cod="""# Estilo PEP 8: minúsculas con guion bajo y espacios entre operadores
nombre_completo = "Ana Pérez"
edad_minima = 18
total = edad_minima + 2
print(nombre_completo, total)
# Evita: NombreCompleto=\"Ana\"; edadMinima=18""",
  h="escribe nombres y operaciones siguiendo la guía de estilo",
  pr=("La guía oficial de estilo de Python se llama PEP ___. (un número)", "8"),
  pr2=("El estilo de nombres de PEP 8 usa minúsculas y guion ___. (4 letras)", "bajo"),
  ec="mezclar estilos de nombres en el mismo programa"),
K("Cómo practicar Python",
  d="costumbre de escribir y probar código a diario",
  u="aprender más rápido y fijar lo estudiado",
  mas="Programar se aprende programando. Teclea cada ejemplo (no copies y pegues), cámbialo y rómpelo a propósito. Mini-proyectos como un adivinador de números o una lista de tareas enseñan mucho. Un poco cada día funciona mejor que mucho de golpe.",
  k=["Programar se aprende escribiendo código.", "Teclear los ejemplos ayuda más que copiarlos.", "Practicar un poco cada día es mejor que mucho de golpe."],
  sit="Quieres aprender Python de verdad y no solo memorizarlo. ¿Qué haces?",
  cod="""# Reto: cambia los valores y observa el resultado
nombre = "Ana"
edad = 20
print("Me llamo", nombre, "y tengo", edad, "años")
# Ahora crea una variable «ciudad» y muéstrala""",
  h="une un nombre y una edad en una frase y deja un reto para ampliarla",
  pr=("Programar se aprende ___. (11 letras: programando)", "programando", "practicando", "escribiendo"),
  pr2=("Practicar un poco cada ___ es mejor que mucho de golpe. (3 letras)", "día", "dia"),
  ec="copiar y pegar ejemplos sin escribirlos"),
]
