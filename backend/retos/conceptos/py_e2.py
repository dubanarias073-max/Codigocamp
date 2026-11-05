"""Python · Etapa 2: datos y operadores."""
from ..generador import K

LISTA = [
K("Variables y asignación",
  d="crear una variable dándole un valor con el signo igual",
  u="guardar y reutilizar datos en el programa",
  mas="nombre = \"Ana\" crea la variable nombre y le asigna el texto. El signo = no significa «igual» como en matemáticas, sino «guarda lo de la derecha en lo de la izquierda». Puedes asignar varias a la vez: a, b = 1, 2, e incluso intercambiar valores: a, b = b, a.",
  k=["El signo = guarda el valor de la derecha en la variable de la izquierda.", "Se pueden asignar varias variables a la vez.", "Una variable puede cambiar de valor cuando quieras."],
  sit="Quieres guardar la puntuación de un jugador y cambiarla durante el programa. ¿Qué haces?",
  cod="""puntos = 0                # crea la variable
puntos = puntos + 10      # usa su valor y lo actualiza
print(puntos)             # 10
a, b = 1, 2               # asignación múltiple
a, b = b, a               # intercambia los valores
print(a, b)               # 2 1""",
  h="crea una variable, la actualiza e intercambia dos valores",
  pr=("El signo que asigna un valor a una variable es ___. (un carácter)", "="),
  pr2=("Con a, b = b, a se ___ los valores de dos variables. (9 letras: intercambian)", "intercambian"),
  ec="leer una variable antes de asignarle un valor",
  err=("puntos = 10\nprint(punto)", 2, "El nombre está mal escrito: la variable se llama puntos, no punto.")),
K("Nombres de variables",
  d="reglas y estilo para escribir identificadores",
  u="que el código se entienda con facilidad",
  mas="Pueden llevar letras, números y guion bajo, pero no empezar por número ni usar palabras reservadas (if, for, class…). Python distingue mayúsculas de minúsculas. El estilo es snake_case: nombre_completo, edad_minima. Elige nombres que expliquen el contenido.",
  k=["Un nombre de variable no puede empezar por un número.", "Python distingue entre mayúsculas y minúsculas.", "El estilo habitual es snake_case."],
  sit="Quieres nombrar una variable de varias palabras con el estilo habitual de Python. ¿Qué convención usas?",
  cod="""nombre_completo = "Ana Pérez"      # snake_case
edad_minima = 18
Total = 1
total = 2                         # distinta de Total
print(nombre_completo, edad_minima, Total, total)""",
  h="usa snake_case y muestra que mayúsculas y minúsculas son nombres distintos",
  pr=("El estilo nombre_completo, con guion bajo entre palabras, se llama ___ case. (5 letras: snake)", "snake"),
  pr2=("Un nombre de variable no puede empezar por un ___. (6 letras: número)", "número", "numero"),
  ec="usar nombres como x1 o dato sin significado",
  err=("2edad = 20\nprint(2edad)", 1, "Un nombre de variable no puede empezar por un número.")),
K("Enteros",
  d="tipo int para números sin parte decimal",
  u="contar, numerar y hacer cálculos exactos",
  mas="Los enteros pueden ser positivos o negativos y de cualquier tamaño: Python no tiene límite práctico. Se pueden escribir con guiones bajos para leerlos mejor: 1_000_000. Las operaciones entre enteros (suma, resta, multiplicación) devuelven otro entero.",
  k=["Un int es un número sin parte decimal.", "Python permite enteros de cualquier tamaño.", "Se pueden escribir guiones bajos para facilitar la lectura."],
  sit="Quieres guardar el número de alumnos de una clase, que nunca tiene decimales. ¿Qué tipo usas?",
  cod="""alumnos = 25
millon = 1_000_000              # los guiones bajos solo ayudan a leer
grande = 2 ** 100               # sin límite práctico
print(alumnos, millon)
print(grande)
print(type(alumnos))""",
  h="usa enteros pequeños y gigantes y muestra su tipo",
  pr=("El tipo de los números enteros se llama ___. (3 letras)", "int"),
  pr2=("Los enteros de Python pueden tener ___ tamaño. (5 letras: // cualquier)", "cualquier"),
  ec="pensar que los enteros de Python tienen límite como en otros lenguajes"),
K("Decimales",
  d="tipo float para números con parte decimal",
  u="guardar medidas, precios y promedios",
  mas="Los decimales usan punto, no coma: 3.14. Se almacenan en binario, por lo que algunos cálculos dan resultados con pequeños errores: 0.1 + 0.2 da 0.30000000000000004. Para dinero exacto existe el módulo decimal; para mostrar, usa round() o un f-string.",
  k=["Los decimales se escriben con punto.", "Los float pueden tener pequeños errores de precisión.", "round() redondea a los decimales indicados."],
  sit="Quieres guardar el precio 4.5 para hacer cálculos con él. ¿Qué tipo usas?",
  cod="""precio = 4.5
print(type(precio))              # float
print(0.1 + 0.2)                 # 0.30000000000000004 (error típico de float)
print(round(0.1 + 0.2, 2))       # 0.3
print(10 / 4)                    # la división siempre da float""",
  h="muestra el tipo float y el error típico de precisión al sumar decimales",
  pr=("El tipo de los números con decimales se llama ___. (5 letras)", "float"),
  pr2=("La función que redondea un número es ___(). (5 letras)", "round"),
  ec="comparar decimales con == esperando precisión exacta"),
K("Textos str",
  d="tipo str para guardar texto entre comillas",
  u="trabajar con nombres, frases y mensajes",
  mas="Se escriben con comillas simples o dobles, y con triples comillas si ocupan varias líneas. Se pueden unir con + y repetir con *. len() cuenta los caracteres. Los textos son inmutables: no se puede cambiar una letra, se crea un texto nuevo.",
  k=["Un str se escribe entre comillas.", "Se pueden unir textos con +.", "Los textos son inmutables."],
  sit="Quieres guardar el nombre «Ana» como un dato de texto. ¿Qué tipo usas?",
  cod="""saludo = "Hola"
nombre = 'Ana'
print(saludo + ", " + nombre)       # une textos
print("ja" * 3)                     # repite: jajaja
print(len("Python"))                # 6 caracteres
largo = '''Texto
de varias líneas'''
print(largo)""",
  h="une, repite y mide textos, y escribe uno de varias líneas",
  pr=("La función que cuenta los caracteres de un texto es ___(). (3 letras)", "len"),
  pr2=("El operador que repite un texto es ___. (un carácter)", "*"),
  ec="intentar cambiar una letra de un texto ya creado"),
K("Booleanos en Python",
  d="tipo bool con solo dos valores: True y False",
  u="tomar decisiones según una condición",
  mas="True y False se escriben con la primera letra en mayúscula. Son el resultado de comparaciones como 5 > 3. Internamente True vale 1 y False vale 0, así que se pueden sumar: sum([True, True, False]) da 2.",
  k=["Los valores booleanos son True y False.", "Se escriben con la primera letra en mayúscula.", "Las comparaciones devuelven booleanos."],
  sit="Quieres guardar si un usuario está activo o no. ¿Qué tipo usas?",
  cod="""es_mayor = 20 >= 18          # resultado de una comparación
activo = False
print(es_mayor, activo)
print(type(es_mayor))
print(sum([True, True, False]))   # True vale 1 y False vale 0: da 2""",
  h="obtiene booleanos de una comparación y suma varios valores lógicos",
  pr=("Los dos valores de un booleano son True y ___. (5 letras)", "false"),
  pr2=("En Python, True vale ___ al sumarlo. (un número)", "1", "uno"),
  ec="escribir true o false en minúsculas",
  err=("activo = true\nprint(activo)", 1, "En Python el valor se escribe True con T mayúscula.")),
K("None",
  d="valor especial que representa la ausencia de un dato",
  u="indicar «todavía no hay valor» o «sin resultado»",
  mas="None es el único valor de su tipo (NoneType). Una función sin return devuelve None. Para comprobarlo, usa is None, no == None. Se considera falsy y es muy habitual como valor por defecto de parámetros opcionales.",
  k=["None representa la ausencia de valor.", "Se comprueba con is None.", "Una función sin return devuelve None."],
  sit="Quieres guardar que todavía no hay ningún valor en una variable. ¿Qué usas?",
  cod="""resultado = None
print(resultado)                    # None
print(resultado is None)            # True: la forma correcta de comprobarlo
def no_devuelve():
    pass
print(no_devuelve())                # None""",
  h="guarda None, lo comprueba con is y muestra que una función sin return lo devuelve",
  pr=("El valor que representa la ausencia de dato es ___. (4 letras)", "none"),
  pr2=("Para comprobar None se usa la palabra ___ None. (2 letras: is)", "is"),
  ec="comparar con == None en lugar de is None"),
K("Función type",
  d="función que devuelve el tipo de un valor",
  u="comprobar de qué tipo es un dato",
  mas="type(5) devuelve <class 'int'>. isinstance(valor, tipo) comprueba si un valor es de un tipo y es la forma recomendada de validar datos. Los tipos básicos son int, float, str, bool, list, tuple, set y dict.",
  k=["type() devuelve el tipo de un valor.", "isinstance() comprueba si un valor es de cierto tipo.", "Los tipos básicos incluyen int, float, str y bool."],
  sit="Quieres comprobar si una variable contiene un número entero antes de operar con ella. ¿Qué usas?",
  cod="""valor = 42
print(type(valor))                    # <class 'int'>
print(isinstance(valor, int))         # True
print(isinstance(valor, str))         # False
print(isinstance(3.5, (int, float)))  # True: admite varios tipos""",
  h="consulta el tipo de un valor y lo valida con isinstance",
  pr=("La función que comprueba si un valor es de un tipo es ___(). (10 letras)", "isinstance"),
  pr2=("La función que devuelve el tipo de un valor es ___(). (4 letras)", "type"),
  ec="comparar con type(x) == int en lugar de usar isinstance"),
K("Entrada con input",
  d="función que pide un dato al usuario por teclado",
  u="hacer programas interactivos",
  mas="input(\"pregunta\") muestra el mensaje, espera lo que escriba la persona y lo devuelve siempre como texto, incluso si escribe un número. Para operar hay que convertirlo con int() o float(). Aquí lo simulamos con variables para que se ejecute sin teclado.",
  k=["input() pide un dato por teclado.", "input() siempre devuelve un texto.", "Para calcular hay que convertir el texto con int() o float()."],
  sit="Quieres preguntar la edad al usuario y calcular con ella. ¿Qué haces con lo que devuelve input?",
  cod="""# nombre = input("¿Cómo te llamas? ")      # así se pide en tu computadora
nombre = "Ana"                              # aquí simulamos la respuesta
# edad = int(input("¿Cuántos años tienes? "))
edad = int("20")                            # input devuelve texto: lo convertimos
print(f"Hola, {nombre}. El año que viene tendrás {edad + 1}")""",
  h="simula una entrada del usuario y convierte la edad a número",
  pr=("La función que pide un dato por teclado es ___(). (5 letras)", "input"),
  pr2=("input() siempre devuelve un ___. (5 letras: texto)", "texto", "str", "string"),
  ec="sumar el resultado de input sin convertirlo a número"),
K("Conversión de tipos en Python",
  d="cambiar un dato de un tipo a otro con int, float, str y bool",
  u="operar con datos que llegan en otro formato",
  mas="int(\"42\") convierte texto en entero, float(\"3.5\") en decimal, str(42) en texto y bool(0) en booleano. int(3.9) trunca a 3 sin redondear. Si el texto no tiene formato numérico (int(\"hola\")), Python lanza un ValueError.",
  k=["int() convierte un valor en entero.", "str() convierte un valor en texto.", "int(\"hola\") produce un ValueError."],
  sit="Tienes el texto «42» y quieres sumarle 1. ¿Qué haces primero?",
  cod="""print(int("42") + 1)           # 43
print(float("3.5") * 2)         # 7.0
print(str(7) + "!")             # 7!
print(int(3.9))                 # 3 (trunca, no redondea)
try:
    int("hola")
except ValueError:
    print("«hola» no es un número")""",
  h="convierte entre tipos y captura el error de una conversión inválida",
  pr=("La función que convierte a entero es ___(). (3 letras)", "int"),
  pr2=("Convertir «hola» a entero produce un ___Error. (5 letras: Value)", "value"),
  ec="creer que int() redondea los decimales"),
K("Operadores aritméticos en Python",
  d="símbolos para sumar, restar, multiplicar y dividir",
  u="hacer cálculos con números",
  mas="+ suma, - resta, * multiplica, / divide (siempre devuelve float), // divide en enteros, % da el resto y ** eleva a una potencia. La multiplicación y la división se evalúan antes que la suma y la resta; los paréntesis cambian el orden.",
  k=["El operador / siempre devuelve un decimal.", "El operador // hace la división entera.", "Los paréntesis cambian el orden de las operaciones."],
  sit="Quieres dividir 7 entre 2 y obtener el resultado entero, 3. ¿Qué operador usas?",
  cod="""print(7 + 3, 7 - 3, 7 * 3)
print(7 / 2)          # 3.5 (siempre float)
print(7 // 2)         # 3   (división entera)
print(7 % 2)          # 1   (resto)
print((2 + 3) * 4)    # 20  (los paréntesis mandan)""",
  h="muestra los operadores aritméticos, la división entera y el efecto de los paréntesis",
  pr=("El operador de la división entera es ___. (2 caracteres)", "//"),
  pr2=("El operador que da el resto de una división es ___. (un carácter)", "%"),
  ec="confundir / con // y esperar un entero"),
K("Resto y división entera",
  d="operaciones % y // que trabajan con restos y cocientes",
  u="saber si un número es par, dividir en grupos o convertir unidades",
  mas="n % 2 == 0 indica que n es par. 125 // 60 da 2 horas y 125 % 60 da 5 minutos restantes. divmod(125, 60) devuelve ambos a la vez. También sirven para dar la vuelta en un ciclo (días de la semana, relojes).",
  k=["n % 2 == 0 comprueba si n es par.", "// da el cociente y % da el resto.", "divmod devuelve el cociente y el resto a la vez."],
  sit="Quieres convertir 125 minutos en horas y minutos restantes. ¿Qué operadores usas?",
  cod="""minutos = 125
horas = minutos // 60          # 2
resto = minutos % 60           # 5
print(f"{horas} h y {resto} min")
print(divmod(125, 60))         # (2, 5)
print(7 % 2 == 0, 8 % 2 == 0)  # ¿par?""",
  h="convierte minutos en horas y minutos y comprueba si un número es par",
  pr=("Un número n es par si n % 2 es igual a ___. (un número)", "0", "cero"),
  pr2=("La función que devuelve cociente y resto a la vez es ___(). (6 letras)", "divmod"),
  ec="usar / en lugar de // y obtener decimales"),
K("Potencias y orden de operaciones",
  d="operador ** y reglas de prioridad entre operadores",
  u="calcular exponentes y evitar resultados inesperados",
  mas="2 ** 3 es 2 elevado a 3 (8). Los exponentes se calculan primero, luego * / // %, y al final + y -. Con igual prioridad se evalúa de izquierda a derecha, salvo ** que va de derecha a izquierda. Ante la duda, usa paréntesis.",
  k=["El operador ** eleva a una potencia.", "Los exponentes se calculan antes que las multiplicaciones.", "Los paréntesis aclaran el orden de evaluación."],
  sit="Quieres calcular 2 elevado a 10. ¿Qué operador usas?",
  cod="""print(2 ** 10)             # 1024
print(2 + 3 * 4)           # 14 (primero la multiplicación)
print((2 + 3) * 4)         # 20
print(-3 ** 2)             # -9: la potencia va antes que el signo
print((-3) ** 2)           # 9""",
  h="calcula potencias y muestra cómo cambia el resultado con el orden y los paréntesis",
  pr=("El operador de potencia es ___. (2 caracteres)", "**"),
  pr2=("2 ** 3 es igual a ___. (un número)", "8"),
  ec="escribir -3 ** 2 esperando 9"),
K("Asignación compuesta en Python",
  d="operadores que modifican una variable usando su valor actual",
  u="acortar sumas, restas y contadores",
  mas="x += 5 equivale a x = x + 5. También existen -=, *=, /=, //=, %= y **=. Son muy habituales en bucles y acumuladores. Python no tiene los operadores ++ ni -- de otros lenguajes: se usa x += 1.",
  k=["x += 5 equivale a x = x + 5.", "Python no tiene los operadores ++ ni --.", "Los operadores compuestos son habituales en bucles."],
  sit="Quieres sumar 1 a un contador. ¿Qué escribes en Python?",
  cod="""puntos = 10
puntos += 5       # 15
puntos *= 2       # 30
puntos -= 10      # 20
puntos += 1       # 21 (Python no tiene ++)
print(puntos)""",
  h="modifica una variable con cuatro operadores compuestos distintos",
  pr=("Escribe el operador que suma y asigna a la vez (2 caracteres).", "+="),
  pr2=("Para sumar uno a un contador en Python se escribe contador ___ 1. (2 caracteres)", "+="),
  ec="intentar usar contador++ como en otros lenguajes",
  err=("contador = 0\ncontador++\nprint(contador)", 2, "Python no tiene ++: se escribe contador += 1.")),
K("Operadores de comparación",
  d="símbolos que comparan dos valores y devuelven un booleano",
  u="decidir según una condición",
  mas="== igual, != distinto, > mayor, < menor, >= mayor o igual, <= menor o igual. Para comparar igualdad se usan dos signos ==; un solo = es asignación. Python permite encadenar: 1 < x < 10. Los textos se comparan por orden alfabético.",
  k=["== comprueba igualdad y = asigna.", "Python permite comparaciones encadenadas como 1 < x < 10.", "Todas las comparaciones devuelven True o False."],
  sit="Quieres saber si una nota está entre 5 y 10 en una sola expresión. ¿Qué escribes?",
  cod="""nota = 7
print(nota >= 5)            # True
print(nota == 10)           # False
print(nota != 7)            # False
print(5 <= nota <= 10)      # True: comparación encadenada
print("ana" < "luis")       # True: orden alfabético""",
  h="compara números y textos, incluida una comparación encadenada",
  pr=("El operador que comprueba igualdad es ___. (2 caracteres)", "=="),
  pr2=("El operador que significa «distinto de» es ___. (2 caracteres)", "!="),
  ec="usar un solo = para comparar",
  err=("nota = 7\nif nota = 7:\n    print(\"Siete\")", 2, "Para comparar se usa ==; un solo = es asignación.")),
K("and, or y not",
  d="operadores lógicos que combinan condiciones",
  u="tomar decisiones con varios criterios",
  mas="and es True solo si las dos condiciones lo son; or es True si al menos una lo es; not invierte el valor. Se escriben como palabras, no con símbolos. Evalúan de izquierda a derecha y se detienen cuando conocen el resultado (cortocircuito).",
  k=["and exige que se cumplan las dos condiciones.", "or exige que se cumpla al menos una.", "not invierte un valor booleano."],
  sit="Quieres comprobar que alguien es mayor de edad y además tiene entrada. ¿Qué operador usas?",
  cod="""edad = 20
tiene_entrada = True
print(edad >= 18 and tiene_entrada)     # True: se cumplen las dos
print(edad < 18 or tiene_entrada)       # True: basta con una
print(not tiene_entrada)                # False: invierte""",
  h="combina condiciones con and, or y not",
  pr=("El operador lógico «y» en Python es ___. (3 letras)", "and"),
  pr2=("El operador lógico «o» en Python es ___. (2 letras)", "or"),
  ec="usar && o || como en otros lenguajes"),
K("f-strings",
  d="textos con f delante que insertan valores entre llaves",
  u="construir frases con variables de forma clara",
  mas="f\"Hola, {nombre}\" reemplaza {nombre} por su valor. Dentro de las llaves puedes poner expresiones y formato: {precio:.2f} muestra dos decimales y {n:05d} rellena con ceros. Es la forma moderna y recomendada de formatear texto.",
  k=["Un f-string lleva una f antes de las comillas.", "Los valores se insertan entre llaves.", "{precio:.2f} muestra un número con dos decimales."],
  sit="Quieres construir la frase «Hola, Ana, tienes 20 años» insertando variables sin concatenar. ¿Qué usas?",
  cod="""nombre = "Ana"
edad = 20
precio = 4.5
print(f"Hola, {nombre}, tienes {edad} años")
print(f"El año que viene tendrás {edad + 1}")     # admite expresiones
print(f"Precio: {precio:.2f} €")                  # dos decimales""",
  h="inserta variables, un cálculo y un número con formato en frases",
  pr=("Un f-string empieza con la letra ___ antes de las comillas. (una letra)", "f"),
  pr2=("Para mostrar dos decimales se escribe {valor:.___f}. (un número)", "2"),
  ec="olvidar la f y ver las llaves tal cual"),
K("Métodos de str",
  d="funciones propias de los textos para transformarlos o buscar en ellos",
  u="limpiar, buscar y cambiar textos",
  mas="upper() y lower() cambian las letras, strip() quita espacios sobrantes, replace() sustituye, split() divide en una lista, join() une una lista en un texto, startswith() y find() buscan. Todos devuelven un texto nuevo: el original no cambia.",
  k=["strip() quita los espacios de los extremos.", "split() divide un texto en una lista.", "Los métodos de str no modifican el original."],
  sit="Quieres quitar los espacios sobrantes del principio y del final de lo que escribió el usuario. ¿Qué método usas?",
  cod="""frase = "  Aprendo Python  "
print(frase.strip())                        # sin espacios en los extremos
print(frase.upper())                        # MAYÚSCULAS
print(frase.replace("Aprendo", "Disfruto").strip())
print("a,b,c".split(","))                   # ['a', 'b', 'c']
print("-".join(["x", "y", "z"]))             # x-y-z""",
  h="limpia, cambia, divide y une textos con métodos de str",
  pr=("El método que quita espacios de los extremos es ___(). (5 letras)", "strip"),
  pr2=("El método que divide un texto en una lista es ___(). (5 letras)", "split"),
  ec="creer que upper() modifica la variable original"),
K("Índices y cortes de texto",
  d="acceso a una letra o fragmento de un texto por su posición",
  u="extraer partes de un texto",
  mas="Las posiciones empiezan en 0: \"Python\"[0] es \"P\". Los índices negativos cuentan desde el final: [-1] es la última letra. Un corte [inicio:fin] extrae un fragmento sin incluir el fin, y [::-1] invierte el texto. Los cortes también funcionan en listas.",
  k=["La primera posición de un texto es la 0.", "El índice -1 es la última letra.", "En un corte [a:b], la posición b no se incluye."],
  sit="Quieres obtener las tres primeras letras de una palabra. ¿Qué técnica usas?",
  cod="""palabra = "Python"
print(palabra[0])         # P
print(palabra[-1])        # n  (la última)
print(palabra[0:3])       # Pyt (el 3 no se incluye)
print(palabra[2:])        # thon
print(palabra[::-1])      # nohtyP (invertida)""",
  h="extrae letras sueltas, fragmentos y la palabra invertida",
  pr=("La primera posición de un texto es la ___. (un número)", "0", "cero"),
  pr2=("El índice que apunta a la última letra es ___. (2 caracteres)", "-1"),
  ec="pensar que el corte [0:3] incluye la posición 3"),
K("Valores truthy y falsy",
  d="valores que se comportan como verdadero o falso en una condición",
  u="escribir condiciones más cortas y claras",
  mas="Son falsy: False, None, 0, 0.0, \"\" (texto vacío), [] (lista vacía), {} y (). Todo lo demás es truthy. Por eso if nombre: es verdadero si el texto no está vacío. bool(valor) convierte cualquier valor a booleano.",
  k=["0, texto vacío, None y las listas vacías son falsy.", "Una lista con elementos es truthy.", "bool() convierte cualquier valor en booleano."],
  sit="Quieres saber si una lista o un texto tiene algo, sin escribir una comparación larga. ¿Qué concepto aprovechas?",
  cod="""print(bool(0), bool(""), bool([]), bool(None))        # falsy: todos False
print(bool(1), bool("a"), bool([0]), bool({"a": 1}))   # truthy: todos True
nombre = ""
if not nombre:
    print("No escribiste tu nombre")""",
  h="muestra qué valores se consideran falsos y cuáles verdaderos",
  pr=("El número 0 se considera ___. (5 letras: falsy)", "falsy", "falso"),
  pr2=("Una lista vacía se considera ___. (5 letras: falsy)", "falsy", "falsa", "falso"),
  ec="pensar que una lista con un 0 dentro es falsy"),
]
