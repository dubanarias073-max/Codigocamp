"""Python · Etapa 3: decisiones, bucles y funciones."""
from ..generador import K

LISTA = [
K("if en Python",
  d="estructura que ejecuta un bloque solo si la condición es verdadera",
  u="tomar decisiones en el programa",
  mas="Se escribe if condición: seguido de un bloque con sangría. No necesita paréntesis alrededor de la condición ni llaves. Los dos puntos (:) y la sangría son obligatorios. Si la condición es False, el bloque se salta.",
  k=["if ejecuta un bloque solo si la condición es verdadera.", "La línea del if termina con dos puntos.", "El bloque del if debe llevar sangría."],
  sit="Quieres mostrar un aviso solo cuando la edad sea 18 o más. ¿Qué estructura usas?",
  cod="""edad = 20
if edad >= 18:
    print("Eres mayor de edad")      # solo si la condición es True
print("Fin del programa")           # se ejecuta siempre""",
  h="muestra un aviso solo si la edad es mayor o igual a 18",
  pr=("La línea de un if termina con el símbolo ___. (dos puntos)", ":", "dos puntos"),
  pr2=("El bloque de un if se marca con ___. (8 letras: sangría)", "sangría", "sangria", "indentación", "indentacion"),
  ec="olvidar los dos puntos al final del if",
  err=("edad = 20\nif edad >= 18\n    print(\"Mayor\")", 2, "Falta el símbolo : al final de la línea del if.")),
K("else",
  d="rama que se ejecuta cuando la condición del if es falsa",
  u="elegir entre dos caminos",
  mas="else va alineado con el if y no lleva condición, solo los dos puntos. Garantiza que siempre se ejecute exactamente una de las dos ramas. Una línea como «x = a if condicion else b» es la versión corta (expresión condicional).",
  k=["else se ejecuta cuando el if no se cumple.", "else no lleva condición.", "Existe una versión corta: valor_si if condicion else otro."],
  sit="Quieres mostrar «Mayor» si la edad es 18 o más y «Menor» en caso contrario. ¿Qué estructura usas?",
  cod="""edad = 15
if edad >= 18:
    print("Mayor de edad")
else:
    print("Menor de edad")        # se ejecuta porque 15 no es >= 18
etiqueta = "Adulto" if edad >= 18 else "Menor"   # versión corta
print(etiqueta)""",
  h="elige entre dos mensajes con if/else y con la versión corta",
  pr=("La rama que se ejecuta cuando el if es falso es ___. (4 letras)", "else"),
  pr2=("else ___ lleva condición. (no)", "no"),
  ec="escribir una condición después de else"),
K("elif",
  d="rama intermedia que prueba otra condición",
  u="elegir entre más de dos caminos",
  mas="elif es la abreviatura de «else if». Python prueba cada condición de arriba abajo y ejecuta solo la primera verdadera. El orden importa: pon primero las condiciones más específicas. El else final es opcional.",
  k=["elif añade una condición intermedia.", "Se ejecuta solo la primera rama cuya condición sea verdadera.", "El orden de las condiciones importa."],
  sit="Quieres asignar una letra según la nota: A, B o C. ¿Qué estructura usas?",
  cod="""nota = 7
if nota >= 9:
    print("A")
elif nota >= 7:
    print("B")          # esta se ejecuta
else:
    print("C")""",
  h="asigna una letra según la nota probando condiciones en orden",
  pr=("La rama intermedia entre if y else se escribe ___. (4 letras)", "elif"),
  pr2=("De varias ramas, se ejecuta la ___ cuya condición sea verdadera. (7 letras)", "primera"),
  ec="escribir else if en lugar de elif",
  err=("nota = 7\nif nota >= 9:\n    print(\"A\")\nelse if nota >= 7:\n    print(\"B\")", 4, "En Python se escribe elif, no else if.")),
K("match",
  d="estructura que compara un valor con varios patrones",
  u="elegir entre muchas opciones fijas de forma clara",
  mas="match valor: con varios case patron: compara de arriba abajo (disponible desde Python 3.10). El guion bajo _ actúa como caso por defecto. Es más potente que una cadena de elif porque puede desestructurar listas y objetos.",
  k=["match compara un valor con varios patrones case.", "El patrón _ equivale al caso por defecto.", "match está disponible desde Python 3.10."],
  sit="Quieres mostrar el nombre del día según un número del 1 al 7. ¿Qué estructura usas?",
  cod="""dia = 3
match dia:
    case 1:
        print("Lunes")
    case 2:
        print("Martes")
    case 3:
        print("Miércoles")        # coincide
    case _:
        print("Otro día")         # por defecto""",
  h="muestra el nombre de un día según su número",
  pr=("El patrón que equivale al caso por defecto en match es ___. (un carácter)", "_"),
  pr2=("Cada opción de un match se escribe con la palabra ___. (4 letras)", "case"),
  ec="usar match en versiones anteriores a Python 3.10"),
K("Bucle while en Python",
  d="bucle que repite un bloque mientras se cumpla una condición",
  u="repetir cuando no se sabe cuántas veces",
  mas="while condición: comprueba la condición antes de cada vuelta. Dentro del bucle debe cambiar algo para que la condición llegue a ser falsa; si no, el bucle es infinito. Es ideal para «repite hasta que ocurra algo».",
  k=["while repite mientras la condición sea verdadera.", "La condición se comprueba antes de cada vuelta.", "Dentro del bucle debe cambiar algo para que termine."],
  sit="Quieres dividir un número entre 2 mientras sea mayor que 1, sin saber cuántas veces. ¿Qué bucle usas?",
  cod="""n = 100
pasos = 0
while n > 1:            # se repite mientras n sea mayor que 1
    n = n / 2
    pasos += 1
print("Pasos:", pasos)""",
  h="divide un número entre dos mientras sea mayor que uno y cuenta los pasos",
  pr=("El bucle que repite mientras se cumpla una condición es ___. (5 letras)", "while"),
  pr2=("Un bucle cuya condición nunca se vuelve falsa es un bucle ___. (8 letras)", "infinito"),
  ec="olvidar actualizar la variable de la condición"),
K("Bucle for y range",
  d="bucle que recorre una secuencia, como un rango de números",
  u="repetir un número conocido de veces",
  mas="for i in range(5): repite 5 veces con i valiendo 0, 1, 2, 3, 4. range(inicio, fin, paso) permite empezar donde quieras (el fin no se incluye) y saltar de dos en dos. El for de Python recorre elementos, no cuenta con condición como en otros lenguajes.",
  k=["range(5) genera los números del 0 al 4.", "En range(a, b), el valor b no se incluye.", "El tercer argumento de range es el paso."],
  sit="Quieres mostrar los números del 1 al 5, repitiendo la misma instrucción. ¿Qué bucle usas?",
  cod="""for i in range(1, 6):          # 1, 2, 3, 4, 5 (el 6 no se incluye)
    print("Vuelta", i)
for par in range(0, 10, 2):    # de 2 en 2
    print(par)""",
  h="repite cinco vueltas numeradas y cuenta de dos en dos",
  pr=("La función que genera una secuencia de números para un for es ___(). (5 letras)", "range"),
  pr2=("range(5) genera los números del 0 al ___. (un número)", "4"),
  ec="creer que range(5) incluye el 5"),
K("break y continue en Python",
  d="instrucciones que cortan un bucle o saltan una vuelta",
  u="salir antes de tiempo o ignorar ciertos casos",
  mas="break termina el bucle completamente y continue salta el resto de la vuelta actual. Los bucles de Python tienen además una cláusula else que se ejecuta solo si el bucle terminó sin usar break; es útil para búsquedas.",
  k=["break termina el bucle por completo.", "continue salta solo la vuelta actual.", "El else de un bucle se ejecuta si no hubo break."],
  sit="Quieres dejar de recorrer una lista en cuanto encuentres el número 7. ¿Qué instrucción usas?",
  cod="""for i in range(1, 11):
    if i % 2 == 0:
        continue          # salta los pares
    if i == 7:
        break             # sale del bucle al llegar a 7
    print(i)              # 1, 3, 5
else:
    print("Nunca se ejecuta aquí porque hubo break")""",
  h="salta números pares y se detiene al llegar al 7",
  pr=("La instrucción que termina un bucle es ___. (5 letras)", "break"),
  pr2=("La instrucción que salta a la siguiente vuelta es ___. (8 letras)", "continue"),
  ec="usar break cuando se quería continue"),
K("Bucles anidados en Python",
  d="bucles escritos dentro de otros bucles",
  u="recorrer tablas, cuadrículas y combinaciones",
  mas="Por cada vuelta del bucle externo, el interno realiza todas sus vueltas. Un bucle de 3 con otro interno de 4 ejecuta el interior 12 veces. Se usan para tablas de multiplicar, matrices y dibujar figuras con texto.",
  k=["El bucle interno completa todas sus vueltas por cada vuelta del externo.", "Dos bucles de 3 y 4 vueltas ejecutan el interior 12 veces.", "Sirven para recorrer tablas y cuadrículas."],
  sit="Quieres imprimir una tabla de multiplicar completa recorriendo filas y columnas. ¿Qué técnica usas?",
  cod="""for fila in range(1, 4):
    linea = ""
    for col in range(1, 4):
        linea += str(fila * col) + " "     # el interno se repite por cada fila
    print(linea)""",
  h="construye una tabla de multiplicar 3 por 3 con dos bucles",
  pr=("Un bucle dentro de otro bucle se llama bucle ___. (8 letras)", "anidado"),
  pr2=("Si el externo da 3 vueltas y el interno 4, el interior se ejecuta ___ veces. (un número)", "12"),
  ec="usar el mismo nombre de contador en los dos bucles"),
K("Funciones con def",
  d="bloques de código con nombre que se ejecutan al llamarlos",
  u="reutilizar código y dividir un programa en partes",
  mas="def saludar(): define la función y saludar() la ejecuta. El cuerpo va con sangría. Un nombre claro en forma de verbo (calcular_total, mostrar_menu) hace el programa más fácil de leer. Una función debe definirse antes de llamarse.",
  k=["Una función se define con def.", "El cuerpo de la función lleva sangría.", "Una función debe definirse antes de llamarla."],
  sit="Quieres agrupar tres líneas de código bajo un nombre para usarlas varias veces. ¿Qué creas?",
  cod="""def mostrar_bienvenida():
    print("¡Bienvenida!")
    print("Aprende a tu ritmo")

mostrar_bienvenida()      # llamada 1
mostrar_bienvenida()      # llamada 2""",
  h="define una función de bienvenida y la llama dos veces",
  pr=("La palabra que define una función es ___. (3 letras)", "def"),
  pr2=("Para ejecutar una función se escribe su nombre seguido de ___. (paréntesis)", "paréntesis", "parentesis", "()"),
  ec="llamar a una función antes de definirla",
  err=("def saludar():\nprint(\"Hola\")\nsaludar()", 2, "El cuerpo de la función debe ir con sangría.")),
K("Parámetros y argumentos en Python",
  d="datos que una función recibe para trabajar con ellos",
  u="hacer funciones flexibles",
  mas="Los parámetros son los nombres entre paréntesis al definir; los argumentos son los valores al llamarla. Pueden pasarse por posición (saludar(\"Ana\", \"Lima\")) o por nombre (saludar(ciudad=\"Lima\", nombre=\"Ana\")), y entonces el orden no importa.",
  k=["Los parámetros se escriben al definir la función.", "Los argumentos son los valores que se pasan al llamarla.", "Los argumentos por nombre permiten cambiar el orden."],
  sit="Quieres que una función salude a quien le indiques, no siempre a la misma persona. ¿Qué usas?",
  cod="""def saludar(nombre, ciudad):
    print(f"Hola, {nombre} de {ciudad}")

saludar("Ana", "Lima")                    # por posición
saludar(ciudad="Bogotá", nombre="Luis")   # por nombre: el orden no importa""",
  h="saluda a distintas personas pasando argumentos por posición y por nombre",
  pr=("Los nombres entre paréntesis al definir una función son los ___. (10 letras)", "parámetros", "parametros"),
  pr2=("Los valores que se pasan al llamar una función son los ___. (10 letras)", "argumentos"),
  ec="pasar los argumentos en distinto orden al esperado"),
K("return en Python",
  d="instrucción que devuelve un valor desde una función",
  u="obtener el resultado de una función para usarlo después",
  mas="return termina la función y entrega un valor. Una función sin return devuelve None. print solo muestra algo; return permite guardar el resultado. Puede devolver varios valores a la vez separados por comas (en realidad, una tupla).",
  k=["return devuelve un valor y termina la función.", "Sin return, una función devuelve None.", "Puede devolver varios valores a la vez."],
  sit="Quieres que una función calcule un total y te lo entregue para guardarlo en una variable. ¿Qué usas?",
  cod="""def sumar(a, b):
    return a + b           # devuelve y termina
    print("No se ejecuta")

total = sumar(3, 4)        # el resultado se guarda
print(total)               # 7

def min_max(lista):
    return min(lista), max(lista)    # devuelve dos valores
print(min_max([4, 9, 2]))""",
  h="devuelve una suma y un par de valores desde funciones",
  pr=("La instrucción que devuelve un valor desde una función es ___. (6 letras)", "return"),
  pr2=("Una función sin return devuelve ___. (4 letras)", "none"),
  ec="usar print en lugar de return y no poder guardar el resultado",
  err=("def doble(n):\n    n * 2\n\nprint(doble(4))", 2, "Falta return: sin él la función devuelve None.")),
K("Valores por defecto",
  d="valores que usa un parámetro cuando no se le pasa argumento",
  u="evitar errores cuando falta un dato opcional",
  mas="def saludar(nombre=\"visitante\") usa «visitante» si llamas a saludar() sin argumento. Los parámetros con valor por defecto van después de los obligatorios. No uses una lista o diccionario vacíos como valor por defecto: se comparten entre llamadas; usa None.",
  k=["Un parámetro por defecto se escribe parámetro=valor.", "Los parámetros opcionales van después de los obligatorios.", "No conviene usar listas vacías como valor por defecto."],
  sit="Quieres que una función use «visitante» si no le dicen el nombre. ¿Qué técnica usas?",
  cod="""def saludar(nombre="visitante"):
    print(f"Hola, {nombre}")

saludar("Ana")        # Hola, Ana
saludar()             # Hola, visitante""",
  h="saluda con un nombre por defecto cuando no se indica ninguno",
  pr=("Un parámetro por defecto se escribe parámetro ___ valor. (un carácter)", "="),
  pr2=("Como valor por defecto de una lista conviene usar ___ en vez de []. (4 letras)", "none"),
  ec="usar una lista vacía como valor por defecto"),
K("Argumentos variables",
  d="parámetros *args y **kwargs que aceptan cantidades variables de datos",
  u="crear funciones que reciben tantos valores como se quiera",
  mas="*args agrupa los argumentos posicionales sobrantes en una tupla y **kwargs agrupa los argumentos por nombre en un diccionario. Con ellos una función como sumar(1, 2, 3, 4) puede recibir cualquier cantidad de números.",
  k=["*args agrupa argumentos posicionales en una tupla.", "**kwargs agrupa argumentos por nombre en un diccionario.", "Permiten recibir una cantidad variable de datos."],
  sit="Quieres una función que sume cuantos números le pases, sin saber cuántos serán. ¿Qué usas?",
  cod="""def sumar(*numeros):
    return sum(numeros)

print(sumar(1, 2, 3, 4))          # 10

def ficha(**datos):
    for clave, valor in datos.items():
        print(clave, "=", valor)

ficha(nombre="Ana", edad=20)""",
  h="suma una cantidad variable de números y muestra datos recibidos por nombre",
  pr=("El parámetro que agrupa argumentos posicionales sobrantes es ___args. (un carácter: *)", "*"),
  pr2=("El parámetro que agrupa argumentos por nombre es ___kwargs. (2 caracteres)", "**"),
  ec="olvidar el asterisco y recibir un único valor"),
K("Ámbito de variables en Python",
  d="zona del código donde una variable existe",
  u="saber dónde se puede leer cada variable",
  mas="Una variable creada dentro de una función es local y solo existe ahí. Las variables definidas fuera son globales y pueden leerse desde las funciones, pero para modificarlas hay que declarar global (se desaconseja). Es mejor pasar datos por parámetros y devolver resultados.",
  k=["Una variable local solo existe dentro de su función.", "Una variable global se puede leer desde las funciones.", "Es mejor pasar datos por parámetros que modificar globales."],
  sit="Una variable creada dentro de una función no se puede leer desde fuera. ¿Qué concepto lo explica?",
  cod="""global_ = "visible en todas partes"
def prueba():
    local = "solo existe aquí"
    print(global_, local)

prueba()
try:
    print(local)                 # no existe fuera de la función
except NameError:
    print("local no existe fuera de la función")""",
  h="compara una variable global con otra local que no existe fuera de su función",
  pr=("Una variable que solo existe dentro de una función es ___. (5 letras)", "local"),
  pr2=("Una variable visible en todo el programa es ___. (6 letras)", "global"),
  ec="intentar usar fuera de una función una variable local"),
K("lambda",
  d="función anónima de una sola expresión",
  u="escribir funciones muy cortas donde se necesitan",
  mas="lambda x: x * 2 equivale a una función que devuelve el doble. Solo admite una expresión, sin return ni varias líneas. Se usa sobre todo como argumento de sorted, map o filter. Si la lógica es más larga, es mejor usar def.",
  k=["lambda crea una función anónima de una sola expresión.", "No lleva return explícito.", "Se usa mucho como argumento de sorted, map y filter."],
  sit="Necesitas una función muy corta para indicar cómo ordenar una lista, usada solo una vez. ¿Qué usas?",
  cod="""doble = lambda x: x * 2
print(doble(21))                        # 42
palabras = ["pera", "kiwi", "manzana"]
print(sorted(palabras, key=lambda p: len(p)))    # ordena por longitud""",
  h="define una función lambda y la usa para ordenar palabras por longitud",
  pr=("La palabra que crea una función anónima es ___. (6 letras)", "lambda"),
  pr2=("Una lambda solo admite una ___. (9 letras: expresión)", "expresión", "expresion"),
  ec="intentar escribir varias líneas dentro de una lambda"),
K("Recursividad en Python",
  d="técnica en la que una función se llama a sí misma",
  u="resolver problemas que se repiten de forma similar",
  mas="Una función recursiva necesita un caso base (cuándo parar) y un caso recursivo (cómo acercarse al caso base). Sin caso base, Python lanza RecursionError al superar unas mil llamadas. Muchos problemas recursivos pueden resolverse también con bucles.",
  k=["Una función recursiva se llama a sí misma.", "Necesita un caso base para detenerse.", "Sin caso base se produce un RecursionError."],
  sit="Quieres calcular el factorial de un número con una función que se llama a sí misma. ¿Qué técnica usas?",
  cod="""def factorial(n):
    if n <= 1:
        return 1                    # caso base: aquí se detiene
    return n * factorial(n - 1)     # caso recursivo

print(factorial(5))                 # 120""",
  h="calcula un factorial con una función que se llama a sí misma",
  pr=("La condición que detiene una función recursiva es el caso ___. (4 letras)", "base"),
  pr2=("Una función que se llama a sí misma es ___. (9 letras)", "recursiva"),
  ec="olvidar el caso base y provocar un RecursionError"),
K("Docstrings",
  d="texto entre triples comillas que documenta una función",
  u="explicar qué hace una función y cómo se usa",
  mas="La primera línea de una función puede ser una cadena entre triples comillas que describe su propósito, sus parámetros y lo que devuelve. help(funcion) y los editores la muestran al usar la función. Documentar es una señal de calidad profesional.",
  k=["Un docstring se escribe con triples comillas dentro de la función.", "help() muestra el docstring de una función.", "Los docstrings explican qué hace la función."],
  sit="Quieres dejar escrito dentro de una función qué hace, para que cualquiera pueda consultarlo. ¿Qué usas?",
  cod="""def area_circulo(radio):
    \"\"\"Calcula el área de un círculo.

    radio: radio del círculo (número positivo).
    Devuelve el área como número decimal.
    \"\"\"
    return 3.1416 * radio ** 2

print(area_circulo(2))
print(area_circulo.__doc__.splitlines()[0])""",
  h="documenta una función con un docstring y lo consulta",
  pr=("Un docstring se escribe entre ___ comillas. (6 letras: triples)", "triples"),
  pr2=("La función que muestra la ayuda de otra función es ___(). (4 letras)", "help"),
  ec="escribir un comentario con # en vez de un docstring"),
K("Funciones integradas",
  d="funciones que Python ya trae listas para usar",
  u="evitar escribir de nuevo operaciones comunes",
  mas="len cuenta elementos, sum suma, min y max encuentran el menor y mayor, abs da el valor absoluto, round redondea, sorted ordena, reversed invierte, any y all comprueban condiciones, enumerate numera y zip une listas. Conócelas: te ahorran mucho código.",
  k=["len() cuenta los elementos de una secuencia.", "sum(), min() y max() trabajan sobre listas de números.", "sorted() devuelve una lista ordenada sin modificar la original."],
  sit="Quieres saber el mayor de una lista de números sin escribir ningún bucle. ¿Qué usas?",
  cod="""numeros = [4, 9, 2, 7]
print(len(numeros), sum(numeros))             # 4 22
print(min(numeros), max(numeros))             # 2 9
print(sorted(numeros))                        # [2, 4, 7, 9]
print(abs(-5), round(3.14159, 2))             # 5 3.14
print(any(n > 8 for n in numeros), all(n > 1 for n in numeros))""",
  h="usa seis funciones integradas para medir, sumar, ordenar y comprobar una lista",
  pr=("La función que devuelve el mayor de varios valores es ___(). (3 letras)", "max"),
  pr2=("La función que cuenta los elementos de una lista es ___(). (3 letras)", "len"),
  ec="escribir un bucle para algo que ya hace sum() o max()"),
K("Bucle for sobre listas y textos",
  d="bucle que recorre directamente los elementos de una secuencia",
  u="procesar cada elemento sin manejar índices",
  mas="for fruta in frutas: da en cada vuelta un elemento de la lista, sin contadores. También recorre los caracteres de un texto. Es más claro y menos propenso a errores que recorrer con range(len(lista)); usa el índice solo cuando de verdad lo necesites.",
  k=["for recorre directamente los elementos de una lista.", "También puede recorrer los caracteres de un texto.", "No hace falta manejar índices para recorrer una lista."],
  sit="Quieres mostrar cada nombre de una lista sin preocuparte por los índices. ¿Qué bucle usas?",
  cod="""frutas = ["manzana", "pera", "uva"]
for fruta in frutas:              # fruta toma cada elemento
    print("Me gusta la", fruta)
for letra in "Hola":              # también recorre textos
    print(letra)""",
  h="recorre una lista y las letras de un texto sin usar índices",
  pr=("En for fruta ___ frutas, la palabra que va antes de la lista es ___. (2 letras: in)", "in"),
  pr2=("Un for puede recorrer los ___ de un texto. (11 letras: caracteres)", "caracteres", "letras"),
  ec="recorrer con range(len(lista)) cuando bastaba recorrer la lista"),
K("Depurar con print",
  d="técnica de mostrar valores intermedios para encontrar errores",
  u="descubrir por qué un programa no hace lo esperado",
  mas="Cuando un cálculo da algo distinto a lo esperado, imprime los valores en los puntos clave y compáralos con lo que deberían ser. También existen el depurador (pdb o el de tu editor) y los asserts, que comprueban suposiciones: assert x > 0, \"x debe ser positivo\".",
  k=["Mostrar valores intermedios ayuda a localizar errores.", "assert comprueba que una suposición sea cierta.", "Conviene comparar lo esperado con lo real."],
  sit="Un cálculo da un resultado distinto al esperado y quieres inspeccionar los valores intermedios. ¿Qué haces?",
  cod="""def promedio(a, b, c):
    print("Entradas:", a, b, c)        # ¿llegan bien los datos?
    suma = a + b + c
    print("Suma:", suma)               # ¿es la suma esperada?
    return suma / 3

print("Resultado:", promedio(6, 8, 10))
assert promedio(3, 3, 3) == 3, "el promedio de tres 3 debe ser 3\"""",
  h="imprime valores intermedios y comprueba una suposición con assert",
  pr=("La instrucción que comprueba que una suposición sea cierta es ___. (6 letras)", "assert"),
  pr2=("Para localizar errores se muestran los valores ___ del cálculo. (11 letras: intermedios)", "intermedios"),
  ec="cambiar código al azar sin inspeccionar los valores"),
]
