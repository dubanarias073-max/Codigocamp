"""Python · Etapa 5: errores, archivos y objetos."""
from ..generador import K

LISTA = [
K("try y except",
  d="estructura que captura errores para que el programa siga funcionando",
  u="evitar que un error detenga todo el programa",
  mas="El código que puede fallar va en try. Si ocurre un error, Python salta al bloque except, donde puedes avisar y recuperarte. Es preferible capturar errores concretos (except ValueError) en vez de todos, para no esconder fallos que no esperabas.",
  k=["try contiene el código que puede fallar.", "except se ejecuta cuando ocurre el error indicado.", "Conviene capturar errores concretos."],
  sit="Quieres que el programa siga funcionando aunque el usuario escriba un texto donde se esperaba un número. ¿Qué estructura usas?",
  cod="""texto = "abc"
try:
    numero = int(texto)              # puede fallar
    print("Número:", numero)
except ValueError:
    print("«" + texto + "» no es un número válido")
print("El programa continúa")""",
  h="captura el error de convertir un texto que no es un número",
  pr=("El bloque que captura un error se escribe ___. (6 letras)", "except"),
  pr2=("El bloque que contiene el código que puede fallar es ___. (3 letras)", "try"),
  ec="usar un except vacío que esconde todos los errores",
  err=("try:\n    n = int(\"abc\")\nprint(n)\nexcept ValueError:\n    print(\"Error\")", 3, "Entre try y except no puede haber otras instrucciones: el except debe ir justo después del bloque try.")),
K("else y finally",
  d="bloques extra de try que se ejecutan sin error o siempre",
  u="separar el éxito de la limpieza final",
  mas="else se ejecuta solo si no hubo error en el try. finally se ejecuta siempre, haya error o no, y es ideal para cerrar archivos o conexiones. Se pueden encadenar varios except para tipos de error distintos.",
  k=["else se ejecuta solo si no ocurrió ningún error.", "finally se ejecuta siempre.", "Se pueden encadenar varios except."],
  sit="Quieres ejecutar una limpieza final tanto si hubo error como si no. ¿Qué bloque usas?",
  cod="""def dividir(a, b):
    try:
        r = a / b
    except ZeroDivisionError:
        print("No se puede dividir entre cero")
    except TypeError:
        print("Solo números")
    else:
        print("Resultado:", r)             # solo si no hubo error
    finally:
        print("Operación terminada")      # siempre

dividir(10, 2)
dividir(10, 0)""",
  h="divide números, captura dos tipos de error y muestra un mensaje final siempre",
  pr=("El bloque que se ejecuta siempre es ___. (7 letras)", "finally"),
  pr2=("El bloque que se ejecuta solo si no hubo error es ___. (4 letras)", "else"),
  ec="poner código que puede fallar dentro de else"),
K("Lanzar errores con raise",
  d="instrucción que provoca un error a propósito",
  u="avisar de datos inválidos y proteger funciones",
  mas="raise ValueError(\"mensaje\") detiene la función y avisa de que algo es incorrecto. Es mejor fallar pronto con un mensaje claro que seguir con datos erróneos. Quien llama a la función puede capturar el error con try/except.",
  k=["raise provoca un error de forma voluntaria.", "Conviene fallar pronto con un mensaje claro.", "Quien llama puede capturar el error con try/except."],
  sit="Quieres que una función avise con un error si recibe una edad negativa. ¿Qué instrucción usas?",
  cod="""def comprobar_edad(edad):
    if edad < 0:
        raise ValueError("La edad no puede ser negativa")
    return edad

try:
    comprobar_edad(-5)
except ValueError as error:
    print("Error:", error)""",
  h="lanza un error por una edad negativa y lo captura",
  pr=("La instrucción que provoca un error voluntariamente es ___. (5 letras)", "raise"),
  pr2=("El error por un valor inadecuado se llama ___Error. (5 letras: Value)", "value"),
  ec="devolver un valor falso en vez de avisar del error"),
K("Excepciones propias",
  d="clases de error creadas por ti para casos específicos",
  u="distinguir los errores de tu programa de los demás",
  mas="Se crean heredando de Exception: class SaldoInsuficiente(Exception): pass. Después se lanzan con raise y se capturan por su nombre. Dan significado al error y permiten reaccionar de forma distinta según el caso.",
  k=["Una excepción propia hereda de Exception.", "Se lanza con raise y se captura por su nombre.", "Dan significado a los errores de tu programa."],
  sit="Quieres un error propio llamado SaldoInsuficiente para un cajero. ¿Qué creas?",
  cod="""class SaldoInsuficiente(Exception):
    pass

def retirar(saldo, cantidad):
    if cantidad > saldo:
        raise SaldoInsuficiente(f"Faltan {cantidad - saldo} €")
    return saldo - cantidad

try:
    retirar(50, 80)
except SaldoInsuficiente as e:
    print("No se puede:", e)""",
  h="define un error propio y lo lanza cuando el saldo no alcanza",
  pr=("Una excepción propia hereda de la clase ___. (9 letras)", "exception"),
  pr2=("Una excepción propia se declara con la palabra ___. (5 letras)", "class"),
  ec="heredar de una clase equivocada en vez de Exception"),
K("Leer archivos",
  d="abrir un archivo de texto y obtener su contenido",
  u="usar datos guardados fuera del programa",
  mas="open(\"nombre.txt\", \"r\", encoding=\"utf-8\") abre un archivo para leer. read() devuelve todo el texto, readline() una línea y readlines() una lista de líneas. También se puede recorrer con for. Si el archivo no existe, aparece un FileNotFoundError.",
  k=["open() abre un archivo.", "read() devuelve todo el contenido como texto.", "Un archivo que no existe provoca FileNotFoundError."],
  sit="Quieres leer el contenido de un archivo de texto desde Python. ¿Qué función usas?",
  cod="""# Preparamos un archivo de ejemplo
with open("ejemplo.txt", "w", encoding="utf-8") as f:
    f.write("Línea uno\\nLínea dos\\nLínea tres\\n")

with open("ejemplo.txt", "r", encoding="utf-8") as f:
    for numero, linea in enumerate(f, start=1):
        print(numero, linea.strip())

try:
    open("no_existe.txt")
except FileNotFoundError:
    print("El archivo no existe")""",
  h="crea un archivo, lo lee línea a línea y captura el error de uno inexistente",
  pr=("La función que abre un archivo es ___(). (4 letras)", "open"),
  pr2=("El error por abrir un archivo que no existe es ___. (17 letras)", "filenotfounderror"),
  ec="olvidar indicar la codificación utf-8"),
K("Escribir archivos",
  d="guardar texto en un archivo desde Python",
  u="conservar resultados y registros",
  mas="open(nombre, \"w\") crea el archivo o lo vacía si ya existe; \"a\" añade al final sin borrar. write() escribe el texto exacto, sin salto de línea automático. Cuidado con \"w\": borra lo que hubiera.",
  k=["El modo \"w\" crea o vacía el archivo.", "El modo \"a\" añade al final.", "write() no añade saltos de línea."],
  sit="Quieres añadir una línea al final de un registro sin borrar lo anterior. ¿Qué modo usas?",
  cod="""with open("registro.txt", "w", encoding="utf-8") as f:
    f.write("Inicio\\n")                    # w: crea o vacía
with open("registro.txt", "a", encoding="utf-8") as f:
    f.write("Segunda línea\\n")             # a: añade al final
print(open("registro.txt", encoding="utf-8").read())""",
  h="crea un archivo y le añade una línea sin borrar el contenido",
  pr=("El modo que añade al final de un archivo es ___. (una letra)", "a"),
  pr2=("El modo que crea o vacía el archivo es ___. (una letra)", "w"),
  ec="usar el modo w y borrar el contenido anterior"),
K("with",
  d="estructura que abre un recurso y lo cierra automáticamente",
  u="no olvidar cerrar archivos aunque haya errores",
  mas="with open(...) as archivo: abre el archivo y garantiza que se cierre al salir del bloque, incluso si ocurre una excepción. Es la forma recomendada de trabajar con archivos, conexiones y bloqueos.",
  k=["with cierra el archivo automáticamente.", "El cierre ocurre aunque haya un error.", "Es la forma recomendada de abrir archivos."],
  sit="Quieres asegurarte de que un archivo se cierre aunque ocurra un error mientras lo lees. ¿Qué usas?",
  cod="""with open("datos.txt", "w", encoding="utf-8") as archivo:
    archivo.write("hola")
print("¿Cerrado fuera del with?", archivo.closed)     # True""",
  h="escribe en un archivo y comprueba que se cerró solo al salir del bloque",
  pr=("La palabra que cierra un archivo automáticamente es ___. (4 letras)", "with"),
  pr2=("with cierra el archivo aunque ocurra un ___. (5 letras: error)", "error"),
  ec="abrir archivos sin with y olvidar cerrarlos"),
K("Rutas con pathlib",
  d="módulo que representa rutas de archivos como objetos",
  u="trabajar con carpetas y archivos en cualquier sistema operativo",
  mas="Path(\"datos\") / \"notas.txt\" une rutas con / sin preocuparte por la barra del sistema. Path tiene métodos como exists(), read_text(), write_text(), mkdir() y iterdir(). Funciona igual en Windows, Mac y Linux.",
  k=["Path representa una ruta como objeto.", "El operador / une partes de una ruta.", "Funciona igual en todos los sistemas operativos."],
  sit="Quieres construir la ruta datos/notas.txt de forma válida en cualquier sistema operativo. ¿Qué usas?",
  cod="""from pathlib import Path
carpeta = Path("datos")
carpeta.mkdir(exist_ok=True)
archivo = carpeta / "notas.txt"                 # une con /
archivo.write_text("Mis notas", encoding="utf-8")
print(archivo.exists(), archivo.name, archivo.suffix)
print(archivo.read_text(encoding="utf-8"))""",
  h="crea una carpeta, escribe y lee un archivo con pathlib",
  pr=("El módulo que representa rutas como objetos es ___. (7 letras)", "pathlib"),
  pr2=("El operador que une partes de una ruta en pathlib es ___. (un carácter)", "/"),
  ec="escribir rutas con barras de un solo sistema operativo"),
K("CSV",
  d="formato de texto con datos separados por comas",
  u="intercambiar tablas con hojas de cálculo",
  mas="El módulo csv lee y escribe archivos CSV. csv.reader da cada fila como lista y csv.DictReader como diccionario con los nombres de las columnas. Las primeras líneas suelen ser los títulos. Cualquier hoja de cálculo abre y guarda CSV.",
  k=["Un CSV guarda datos tabulares separados por comas.", "csv.DictReader devuelve cada fila como diccionario.", "Las hojas de cálculo pueden abrir y guardar CSV."],
  sit="Quieres leer un archivo exportado desde una hoja de cálculo con filas y columnas. ¿Qué módulo usas?",
  cod="""import csv
with open("alumnos.csv", "w", newline="", encoding="utf-8") as f:
    escritor = csv.writer(f)
    escritor.writerow(["nombre", "nota"])
    escritor.writerow(["Ana", 9])
    escritor.writerow(["Luis", 6])

with open("alumnos.csv", newline="", encoding="utf-8") as f:
    for fila in csv.DictReader(f):
        print(fila["nombre"], int(fila["nota"]))""",
  h="escribe un CSV con alumnos y lo lee como diccionarios",
  pr=("El módulo de Python para leer y escribir CSV se llama ___. (3 letras)", "csv"),
  pr2=("La clase que lee cada fila como diccionario es csv.___Reader. (4 letras: Dict)", "dict"),
  ec="olvidar convertir a número los valores leídos de un CSV"),
K("JSON en Python",
  d="formato de texto para guardar y enviar datos estructurados",
  u="intercambiar datos con APIs y guardar configuraciones",
  mas="El módulo json convierte entre diccionarios de Python y texto JSON. json.dumps(dic) devuelve texto, json.loads(texto) devuelve el diccionario; json.dump y json.load trabajan directamente con archivos. Las claves del JSON siempre son textos.",
  k=["json.dumps convierte un objeto en texto JSON.", "json.loads convierte texto JSON en objeto.", "json.dump y json.load trabajan con archivos."],
  sit="Quieres guardar un diccionario en un archivo en formato de intercambio estándar. ¿Qué usas?",
  cod="""import json
persona = {"nombre": "Ana", "edad": 20, "intereses": ["web", "datos"]}
texto = json.dumps(persona, ensure_ascii=False, indent=2)
print(texto)
vuelta = json.loads(texto)
print(vuelta["intereses"][0])
with open("persona.json", "w", encoding="utf-8") as f:
    json.dump(persona, f, ensure_ascii=False)""",
  h="convierte un diccionario en JSON, lo recupera y lo guarda en un archivo",
  pr=("La función que convierte un diccionario en texto JSON es json.___(). (5 letras: dumps)", "dumps"),
  pr2=("La función que convierte texto JSON en diccionario es json.___(). (5 letras: loads)", "loads"),
  ec="intentar guardar un conjunto (set) en JSON"),
K("Módulos propios",
  d="archivos .py tuyos que se importan desde otros programas",
  u="dividir un proyecto en archivos organizados",
  mas="Cualquier archivo .py es un módulo. Si guardas funciones en utilidades.py, otro archivo puede hacer import utilidades o from utilidades import saludar. Python busca los módulos primero en la carpeta del programa. Evita nombres que coincidan con módulos estándar (random.py).",
  k=["Cualquier archivo .py puede importarse como módulo.", "from modulo import nombre trae solo lo necesario.", "No conviene llamar a tus módulos como los estándar."],
  sit="Quieres guardar tus funciones en otro archivo para usarlas desde varios programas. ¿Qué haces?",
  cod="""# Guarda en utilidades.py:
#   def saludar(nombre):
#       return f"Hola, {nombre}"
# Y en principal.py:
#   from utilidades import saludar
#   print(saludar("Ana"))
def saludar(nombre):
    return f"Hola, {nombre}"
print(saludar("Ana"))""",
  h="muestra cómo guardar una función en un módulo y usarla desde otro archivo",
  pr=("Para traer una función concreta de un módulo se escribe from módulo ___ función. (6 letras)", "import"),
  pr2=("Cualquier archivo con extensión ___ es un módulo. (3 caracteres)", ".py", "py"),
  ec="nombrar un módulo propio como uno estándar y provocar conflictos"),
K("if __name__ == main",
  d="comprobación que ejecuta código solo al correr el archivo directamente",
  u="separar lo que se importa de lo que se ejecuta",
  mas="Cuando un archivo se ejecuta directamente, __name__ vale \"__main__\"; cuando se importa, vale el nombre del módulo. El bloque if __name__ == \"__main__\": permite que un archivo sirva a la vez como módulo y como programa sin ejecutar cosas al importarlo.",
  k=["__name__ vale __main__ al ejecutar el archivo directamente.", "Al importar un módulo, __name__ vale el nombre del módulo.", "Evita ejecutar código al importar."],
  sit="Quieres que cierto código se ejecute solo cuando corres el archivo, no cuando alguien lo importa. ¿Qué escribes?",
  cod="""def principal():
    print("Programa en marcha")

if __name__ == "__main__":      # solo si se ejecuta directamente
    principal()
print("Valor de __name__:", __name__)""",
  h="ejecuta una función principal solo cuando el archivo se corre directamente",
  pr=("Al ejecutar un archivo directamente, __name__ vale \"__main___\". Escribe el valor sin comillas.", "__main__"),
  pr2=("Al importar un módulo, __name__ vale el ___ del módulo. (6 letras)", "nombre"),
  ec="dejar código suelto que se ejecuta al importar el módulo"),
K("Fechas con datetime",
  d="módulo para trabajar con fechas, horas y duraciones",
  u="registrar momentos, calcular plazos y edades",
  mas="datetime.now() da el momento actual. date(2026, 3, 15) crea una fecha. Restar dos fechas da un timedelta con los días de diferencia. strftime(\"%d/%m/%Y\") da formato al texto y strptime convierte un texto en fecha.",
  k=["datetime.now() devuelve la fecha y hora actuales.", "Restar dos fechas devuelve un timedelta.", "strftime da formato a una fecha como texto."],
  sit="Quieres calcular cuántos días faltan para una fecha concreta. ¿Qué módulo usas?",
  cod="""from datetime import date, datetime
hoy = date(2026, 3, 1)
examen = date(2026, 3, 15)
print((examen - hoy).days, "días")               # 14 días
print(examen.strftime("%d/%m/%Y"))               # 15/03/2026
print(datetime.strptime("20/05/2026", "%d/%m/%Y").year)
print(type(datetime.now()).__name__)""",
  h="calcula días entre fechas y convierte entre texto y fecha",
  pr=("El módulo de Python para fechas y horas es ___. (8 letras)", "datetime"),
  pr2=("Restar dos fechas devuelve un objeto ___. (9 letras: timedelta)", "timedelta"),
  ec="comparar fechas como si fueran textos"),
K("Números aleatorios con random",
  d="módulo que genera valores al azar",
  u="crear juegos, sorteos y simulaciones",
  mas="random.randint(1, 6) da un entero entre 1 y 6 (ambos incluidos). random.choice(lista) elige un elemento, random.shuffle(lista) desordena y random.sample(lista, 3) elige varios sin repetir. random.seed(42) hace que los resultados sean reproducibles.",
  k=["randint incluye los dos extremos.", "choice elige un elemento al azar de una lista.", "seed hace reproducible la secuencia aleatoria."],
  sit="Quieres simular una tirada de dado de 1 a 6. ¿Qué función usas?",
  cod="""import random
random.seed(42)                       # resultados reproducibles
print(random.randint(1, 6))           # 1 a 6, ambos incluidos
print(random.choice(["piedra", "papel", "tijera"]))
cartas = list(range(1, 6))
random.shuffle(cartas)
print(cartas)
print(random.sample(range(1, 50), 3))""",
  h="simula un dado, elige al azar, desordena una lista y sortea tres números",
  pr=("La función que da un entero al azar entre dos valores es random.___(). (7 letras)", "randint"),
  pr2=("La función que elige un elemento de una lista es random.___(). (6 letras)", "choice"),
  ec="creer que randint no incluye el límite superior"),
K("Clases y objetos",
  d="plantillas para crear objetos con datos y comportamientos",
  u="modelar cosas del mundo real dentro del programa",
  mas="Una clase es el molde (Perro) y un objeto es cada ejemplar creado con él (rex = Perro()). La clase agrupa datos (atributos) y acciones (métodos). Se escribe en mayúscula inicial: class Perro:. Es la base de la programación orientada a objetos.",
  k=["Una clase es una plantilla y un objeto es un ejemplar suyo.", "Las clases se escriben con la primera letra en mayúscula.", "Una clase agrupa atributos y métodos."],
  sit="Quieres crear muchos perros distintos a partir de una misma plantilla. ¿Qué usas?",
  cod="""class Perro:
    def ladrar(self):
        return "¡Guau!"

rex = Perro()            # objeto 1
luna = Perro()           # objeto 2
print(rex.ladrar(), luna.ladrar())
print(type(rex).__name__)""",
  h="define una clase Perro y crea dos objetos a partir de ella",
  pr=("La palabra que define una clase es ___. (5 letras)", "class"),
  pr2=("Cada ejemplar creado con una clase se llama ___. (6 letras)", "objeto"),
  ec="confundir la clase (el molde) con el objeto (el ejemplar)"),
K("__init__ y atributos",
  d="método especial que prepara cada objeto al crearlo",
  u="guardar los datos propios de cada objeto",
  mas="__init__(self, nombre) se ejecuta automáticamente al crear el objeto. Dentro, self.nombre = nombre guarda un atributo propio de ese objeto. self es el propio objeto y siempre es el primer parámetro de los métodos. Cada objeto tiene sus propios valores.",
  k=["__init__ se ejecuta al crear un objeto.", "self representa al propio objeto.", "Cada objeto tiene sus propios atributos."],
  sit="Quieres que cada perro creado guarde su propio nombre y edad. ¿Qué defines?",
  cod="""class Perro:
    def __init__(self, nombre, edad):       # se ejecuta al crear el objeto
        self.nombre = nombre                # atributos propios
        self.edad = edad

rex = Perro("Rex", 3)
luna = Perro("Luna", 5)
print(rex.nombre, rex.edad)
print(luna.nombre, luna.edad)""",
  h="guarda nombre y edad propios en cada perro creado",
  pr=("El método especial que se ejecuta al crear un objeto es ___. (8 caracteres: __init__)", "__init__"),
  pr2=("El primer parámetro de un método, que representa al objeto, es ___. (4 letras)", "self"),
  ec="olvidar self en un método o al guardar un atributo",
  err=("class Perro:\n    def __init__(self, nombre):\n        nombre = nombre\n\nrex = Perro(\"Rex\")\nprint(rex.nombre)", 3, "Falta self: debe ser self.nombre = nombre para guardarlo en el objeto.")),
K("Métodos de objetos en Python",
  d="funciones definidas dentro de una clase",
  u="darle acciones a los objetos que usan sus propios datos",
  mas="Un método es una función de la clase y su primer parámetro es self. Puede leer y modificar los atributos del objeto: self.energia -= 10. Se llama con el punto: rex.correr(). Los métodos describen lo que el objeto sabe hacer.",
  k=["Un método es una función definida dentro de una clase.", "Su primer parámetro es self.", "Puede leer y modificar los atributos del objeto."],
  sit="Quieres que un perro pueda correr y gastar energía. ¿Qué defines en la clase?",
  cod="""class Perro:
    def __init__(self, nombre):
        self.nombre = nombre
        self.energia = 100

    def correr(self):
        self.energia -= 30                       # modifica su propio atributo
        return f"{self.nombre} corre. Energía: {self.energia}"

rex = Perro("Rex")
print(rex.correr())
print(rex.correr())""",
  h="define un método que modifica la energía del propio objeto",
  pr=("Una función definida dentro de una clase se llama ___. (6 letras: método)", "método", "metodo"),
  pr2=("Los métodos se llaman usando un ___ después del objeto. (5 letras: punto)", "punto"),
  ec="llamar a un método sin crear antes el objeto"),
K("Herencia",
  d="mecanismo por el que una clase hereda de otra",
  u="reutilizar código y crear variantes de una clase",
  mas="class Perro(Animal): hace que Perro tenga todo lo de Animal y pueda añadir o cambiar cosas. super() llama a la clase padre. Sirve para evitar repetir código común (como nombre) entre clases parecidas. Conviene usarla cuando «X es un tipo de Y».",
  k=["Una clase hija hereda atributos y métodos de la clase padre.", "super() permite llamar al código de la clase padre.", "La herencia evita repetir código común."],
  sit="Quieres que Perro y Gato reutilicen lo que tienen en común de Animal. ¿Qué mecanismo usas?",
  cod="""class Animal:
    def __init__(self, nombre):
        self.nombre = nombre
    def presentarse(self):
        return f"Soy {self.nombre}"

class Perro(Animal):                    # hereda de Animal
    def hablar(self):
        return "¡Guau!"

class Gato(Animal):
    def hablar(self):
        return "¡Miau!"

for animal in [Perro("Rex"), Gato("Misu")]:
    print(animal.presentarse(), animal.hablar())""",
  h="reutiliza la clase Animal en Perro y Gato, que añaden su propio sonido",
  pr=("En class Perro(Animal), la clase padre es ___. (6 letras)", "animal"),
  pr2=("La función que llama al código de la clase padre es ___(). (5 letras)", "super"),
  ec="usar herencia cuando no existe una relación «es un tipo de»"),
K("Métodos especiales",
  d="métodos con doble guion bajo que personalizan los objetos",
  u="controlar cómo se muestra, compara y opera un objeto",
  mas="__str__ define cómo se muestra el objeto con print. __len__ permite usar len(objeto), __eq__ define la igualdad y __add__ el operador +. Dan a tus clases el comportamiento natural de los tipos de Python.",
  k=["__str__ define cómo se muestra un objeto con print.", "__len__ permite usar len() con el objeto.", "Los métodos especiales llevan doble guion bajo."],
  sit="Quieres que al imprimir un objeto aparezca un texto descriptivo y no algo como <Perro object>. ¿Qué defines?",
  cod="""class Perro:
    def __init__(self, nombre, edad):
        self.nombre, self.edad = nombre, edad
    def __str__(self):                         # cómo se muestra con print
        return f"{self.nombre} ({self.edad} años)"
    def __eq__(self, otro):                    # cómo se compara con ==
        return self.nombre == otro.nombre

rex = Perro("Rex", 3)
print(rex)
print(rex == Perro("Rex", 9))""",
  h="personaliza cómo se muestra y se compara un objeto",
  pr=("El método especial que define cómo se muestra un objeto es ___. (7 caracteres: __str__)", "__str__"),
  pr2=("Los métodos especiales se escriben con doble guion ___. (4 letras: bajo)", "bajo"),
  ec="olvidar que __str__ debe devolver un texto"),
K("Proyecto: gestor de tareas",
  d="programa que reúne funciones, colecciones, archivos y clases",
  u="practicar todo lo aprendido en un caso completo",
  mas="Para cerrar Python, crea un gestor de tareas: una clase Tarea (texto, hecha), una lista de tareas, funciones para añadir, completar y mostrar, y guardado en un archivo JSON. Después puedes ampliarlo con fechas, prioridades o una interfaz web.",
  k=["Un proyecto completo combina clases, colecciones y archivos.", "JSON permite guardar las tareas entre ejecuciones.", "Dividir el programa en funciones lo hace más claro."],
  sit="Quieres cerrar el curso con un programa que añada, complete y guarde tareas. ¿Qué construyes?",
  cod="""import json
class Tarea:
    def __init__(self, texto, hecha=False):
        self.texto, self.hecha = texto, hecha
    def __str__(self):
        return ("[x] " if self.hecha else "[ ] ") + self.texto

tareas = [Tarea("Estudiar Python"), Tarea("Hacer ejercicio")]
tareas[0].hecha = True
for t in tareas:
    print(t)
datos = [{"texto": t.texto, "hecha": t.hecha} for t in tareas]
with open("tareas.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False)
print("Guardadas:", len(datos))""",
  h="modela tareas con una clase, las muestra y las guarda en JSON",
  pr=("Para cerrar el curso conviene hacer un ___ completo. (8 letras)", "proyecto"),
  pr2=("Para guardar las tareas entre ejecuciones se puede usar un archivo ___. (4 letras)", "json"),
  ec="escribir todo el programa en una sola función gigante"),
]
