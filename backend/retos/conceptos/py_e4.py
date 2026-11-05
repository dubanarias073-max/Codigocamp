"""Python · Etapa 4: colecciones (listas, tuplas, conjuntos y diccionarios)."""
from ..generador import K

LISTA = [
K("Listas",
  d="colección ordenada y modificable de elementos entre corchetes",
  u="manejar muchos datos relacionados en una variable",
  mas="Se escriben entre corchetes y separados por comas: [\"Ana\", \"Luis\"]. Pueden contener cualquier tipo, incluso mezclados. Cada elemento tiene una posición que empieza en 0. len() dice cuántos hay y se pueden modificar elementos individualmente.",
  k=["Una lista se escribe entre corchetes.", "Los elementos de una lista se pueden modificar.", "La primera posición de una lista es la 0."],
  sit="Quieres guardar cinco nombres de alumnos en una sola variable que se pueda modificar. ¿Qué estructura usas?",
  cod="""alumnos = ["Ana", "Luis", "Marta"]
print(alumnos[0])              # Ana (primera posición = 0)
print(len(alumnos))            # 3
alumnos[1] = "Pablo"           # se puede modificar
print(alumnos)""",
  h="lee, mide y modifica elementos de una lista",
  pr=("Una lista se escribe entre ___. (corchetes)", "corchetes", "[]"),
  pr2=("La primera posición de una lista es la ___. (un número)", "0", "cero"),
  ec="pedir el elemento en la posición len(lista) y salirse del rango",
  err=("colores = [\"rojo\", \"verde\"]\nprint(colores[2])", 2, "La lista solo tiene las posiciones 0 y 1: la 2 está fuera de rango (IndexError).")),
K("Cortes de listas",
  d="forma de extraer una parte de una lista con [inicio:fin]",
  u="obtener sublistas y copias rápidas",
  mas="lista[1:3] devuelve los elementos de la posición 1 a la 2 (el fin no se incluye). lista[:2] son los dos primeros, lista[-2:] los dos últimos y lista[::2] uno de cada dos. Un corte siempre devuelve una lista nueva y no modifica la original.",
  k=["En [a:b], la posición b no se incluye.", "[-2:] devuelve los dos últimos elementos.", "Un corte devuelve una lista nueva."],
  sit="Quieres obtener los tres primeros elementos de una lista sin modificarla. ¿Qué técnica usas?",
  cod="""letras = ["a", "b", "c", "d", "e"]
print(letras[1:3])       # ['b', 'c']
print(letras[:3])        # ['a', 'b', 'c']
print(letras[-2:])       # ['d', 'e']
print(letras[::2])       # ['a', 'c', 'e']
print(letras)            # la original no cambia""",
  h="extrae varios fragmentos de una lista sin modificarla",
  pr=("En lista[1:3], la posición ___ no se incluye. (un número)", "3"),
  pr2=("[-2:] devuelve los ___ últimos elementos. (un número)", "2", "dos"),
  ec="pensar que el índice final del corte se incluye"),
K("Añadir y quitar elementos de una lista",
  d="métodos append, insert, remove y pop para modificar una lista",
  u="hacer crecer o encoger una lista durante el programa",
  mas="append añade al final, insert añade en una posición, remove quita el primer elemento con ese valor y pop quita (y devuelve) el de una posición, por defecto el último. extend une otra lista y del borra por posición. Todos modifican la lista original.",
  k=["append añade un elemento al final.", "pop quita y devuelve un elemento.", "remove quita el primer elemento con ese valor."],
  sit="Quieres añadir un nombre al final de una lista ya creada. ¿Qué método usas?",
  cod="""cola = ["Ana", "Luis"]
cola.append("Marta")          # final
cola.insert(0, "Pablo")       # en la posición 0
print(cola)
salio = cola.pop(0)           # quita y devuelve el primero
cola.remove("Luis")           # quita por valor
print(salio, cola)""",
  h="añade y quita elementos de una lista de varias formas",
  pr=("El método que añade un elemento al final es ___(). (6 letras)", "append"),
  pr2=("El método que quita y devuelve un elemento es ___(). (3 letras)", "pop"),
  ec="usar remove con un valor que no está en la lista"),
K("Recorrer y comprobar listas",
  d="formas de recorrer una lista y comprobar si contiene algo",
  u="buscar, contar y procesar elementos",
  mas="for x in lista recorre; x in lista devuelve True o False; lista.index(x) da la posición (error si no está) y lista.count(x) cuenta cuántas veces aparece. Comprobar con in antes de usar index evita errores.",
  k=["El operador in comprueba si un valor está en la lista.", "count() cuenta cuántas veces aparece un valor.", "index() da la posición de un valor."],
  sit="Quieres saber si «Ana» está en una lista de invitados. ¿Qué operador usas?",
  cod="""invitados = ["Ana", "Luis", "Marta", "Ana"]
print("Ana" in invitados)            # True
print("Pablo" not in invitados)      # True
print(invitados.index("Marta"))      # 2
print(invitados.count("Ana"))        # 2""",
  h="comprueba presencia, posición y cantidad de un valor en una lista",
  pr=("El operador que comprueba si un valor está en una lista es ___. (2 letras)", "in"),
  pr2=("El método que cuenta cuántas veces aparece un valor es ___(). (5 letras)", "count"),
  ec="usar index sin comprobar antes que el valor existe"),
K("Ordenar listas",
  d="métodos sort y sorted para ordenar elementos",
  u="mostrar listas de menor a mayor o por otro criterio",
  mas="lista.sort() ordena la lista original y devuelve None. sorted(lista) devuelve una lista nueva ordenada sin tocar la original. reverse=True ordena de mayor a menor y key=función indica el criterio (por ejemplo len o una lambda).",
  k=["sort() modifica la lista original.", "sorted() devuelve una lista nueva.", "reverse=True ordena de mayor a menor."],
  sit="Quieres obtener una copia ordenada de una lista, sin cambiar la original. ¿Qué función usas?",
  cod="""numeros = [10, 9, 1, 100]
print(sorted(numeros))                    # [1, 9, 10, 100]
print(sorted(numeros, reverse=True))      # de mayor a menor
print(numeros)                            # la original no cambia
palabras = ["pera", "kiwi", "manzana"]
palabras.sort(key=len)                    # ordena la propia lista por longitud
print(palabras)""",
  h="ordena una lista de varias formas, con y sin modificar la original",
  pr=("La función que devuelve una lista ordenada nueva es ___(). (6 letras)", "sorted"),
  pr2=("Para ordenar de mayor a menor se añade reverse=___. (4 letras)", "true"),
  ec="escribir lista = lista.sort() y quedarse con None",
  err=("numeros = [3, 1, 2]\nnumeros = numeros.sort()\nprint(numeros[0])", 2, "sort() devuelve None: así la variable numeros pierde la lista.")),
K("Copiar listas",
  d="diferencia entre copiar una lista y copiar la referencia",
  u="evitar cambios inesperados al copiar",
  mas="b = a no copia la lista: ambas variables apuntan a la misma. Para copiar usa a.copy(), a[:] o list(a). Es una copia superficial: si la lista contiene otras listas, estas se comparten. copy.deepcopy copia todo el contenido en profundidad.",
  k=["b = a no crea una copia independiente de una lista.", "copy() y [:] crean una copia superficial.", "deepcopy copia también los objetos internos."],
  sit="Al cambiar una copia de una lista cambia también la original. ¿Qué concepto lo explica?",
  cod="""a = [1, 2, 3]
b = a                  # NO es una copia: apunta a la misma lista
b.append(4)
print(a)               # [1, 2, 3, 4]
c = a.copy()           # copia real
c.append(5)
print(a, c)""",
  h="muestra que asignar no copia y que copy() sí crea una copia independiente",
  pr=("El método que crea una copia de una lista es ___(). (4 letras)", "copy"),
  pr2=("Con b = a, las dos variables apuntan a la ___ lista. (5 letras: misma)", "misma"),
  ec="creer que b = a copia la lista"),
K("Listas anidadas",
  d="listas que contienen otras listas como elementos",
  u="representar tablas, cuadrículas o matrices",
  mas="[[1, 2], [3, 4]] es una lista de dos filas. Se accede con dos índices: tabla[1][0] es 3. Se recorren con bucles anidados. Son ideales para tableros de juegos, hojas de datos y matrices matemáticas.",
  k=["Una lista anidada contiene otras listas.", "Se accede con dos índices: lista[fila][columna].", "Se recorren con bucles anidados."],
  sit="Quieres representar un tablero de 3 filas por 3 columnas. ¿Qué estructura usas?",
  cod="""tablero = [
    ["X", "O", "X"],
    ["O", "X", "O"],
    ["O", "O", "X"],
]
print(tablero[0][2])          # X: fila 0, columna 2
tablero[1][1] = "-"
for fila in tablero:
    print(" ".join(fila))""",
  h="crea un tablero como lista de listas y lo muestra fila por fila",
  pr=("Una lista dentro de otra lista se llama lista ___. (8 letras)", "anidada"),
  pr2=("En tablero[1][2], el primer índice es la ___. (4 letras)", "fila"),
  ec="intercambiar fila y columna al acceder"),
K("Tuplas",
  d="secuencia ordenada e inmutable entre paréntesis",
  u="guardar datos que no deben cambiar, como coordenadas",
  mas="Una tupla se escribe (3, 4) y no se puede modificar después de creada. Son más ligeras que las listas y pueden usarse como claves de diccionario. Una tupla de un solo elemento lleva coma: (5,). Las funciones que devuelven varios valores devuelven una tupla.",
  k=["Una tupla se escribe entre paréntesis.", "Una tupla no se puede modificar.", "Una tupla de un elemento necesita una coma."],
  sit="Quieres guardar unas coordenadas (x, y) que nunca deben cambiar. ¿Qué estructura usas?",
  cod="""punto = (3, 4)
print(punto[0], len(punto))        # 3 2
try:
    punto[0] = 10                  # no se puede modificar
except TypeError:
    print("Las tuplas no se modifican")
uno = (5,)                         # con una sola coma
print(type(uno), type((5)))""",
  h="crea una tupla, intenta modificarla y muestra la coma de un solo elemento",
  pr=("Una secuencia que no se puede modificar es una ___. (5 letras)", "tupla"),
  pr2=("Una tupla de un solo elemento lleva una ___. (4 letras: coma)", "coma"),
  ec="olvidar la coma en una tupla de un solo elemento"),
K("Desempaquetado",
  d="asignar los elementos de una secuencia a varias variables",
  u="sacar valores de listas y tuplas en una línea",
  mas="x, y = (3, 4) crea x = 3 e y = 4. El número de variables debe coincidir, salvo que uses * para recoger el resto: primero, *resto = [1, 2, 3, 4]. Se usa al recorrer pares y al recibir varios valores de una función.",
  k=["El desempaquetado asigna cada elemento a una variable.", "El número de variables debe coincidir con los elementos.", "Con * se recogen los elementos sobrantes."],
  sit="Una función devuelve (3, 4) y quieres guardar cada valor en su variable en una sola línea. ¿Qué usas?",
  cod="""x, y = (3, 4)
print(x, y)
primero, *resto = [10, 20, 30, 40]
print(primero, resto)               # 10 [20, 30, 40]
def min_max(lista):
    return min(lista), max(lista)
menor, mayor = min_max([4, 9, 2])
print(menor, mayor)""",
  h="reparte valores de secuencias en variables, incluyendo los sobrantes con *",
  pr=("El símbolo que recoge los elementos sobrantes es ___. (un carácter)", "*"),
  pr2=("El desempaquetado asigna cada elemento a una ___. (8 letras: variable)", "variable"),
  ec="usar más variables que elementos y provocar un ValueError"),
K("Conjuntos set",
  d="colección sin orden ni elementos repetidos",
  u="eliminar duplicados y comprobar pertenencia rápido",
  mas="Se escribe con llaves {1, 2, 3} o set(lista). No admite elementos repetidos ni tiene posiciones. Es muy rápido para comprobar si un valor está dentro. set(lista) es la forma clásica de quitar duplicados. Un conjunto vacío se crea con set(), no con {}.",
  k=["Un set no admite elementos repetidos.", "Un set no tiene orden ni posiciones.", "Un conjunto vacío se crea con set()."],
  sit="Quieres quitar los valores repetidos de una lista. ¿Qué estructura usas?",
  cod="""repetidos = [1, 2, 2, 3, 3, 3]
unicos = set(repetidos)
print(unicos)                        # {1, 2, 3}
unicos.add(4)
print(4 in unicos, len(unicos))      # True 4
print(type({}), type(set()))         # {} es un diccionario, no un conjunto""",
  h="elimina duplicados con un set y muestra por qué {} no crea un conjunto vacío",
  pr=("La estructura que no admite elementos repetidos es el ___. (3 letras)", "set"),
  pr2=("Un conjunto vacío se crea con ___(). (3 letras)", "set"),
  ec="crear un set vacío con {} y obtener un diccionario"),
K("Operaciones con conjuntos",
  d="unión, intersección y diferencia entre conjuntos",
  u="comparar colecciones: qué comparten y qué las distingue",
  mas="a | b es la unión (todo), a & b la intersección (lo común), a - b la diferencia (lo que está en a pero no en b) y a ^ b lo que está en uno solo. Son perfectas para comparar listas de alumnos, etiquetas o permisos.",
  k=["a & b devuelve los elementos comunes.", "a | b devuelve la unión de los dos conjuntos.", "a - b devuelve lo que está en a y no en b."],
  sit="Quieres saber qué alumnos están en las dos clases a la vez. ¿Qué operación usas?",
  cod="""clase_a = {"Ana", "Luis", "Marta"}
clase_b = {"Luis", "Pablo", "Marta"}
print(clase_a & clase_b)       # en las dos: Luis, Marta
print(clase_a | clase_b)       # todos
print(clase_a - clase_b)       # solo en A: Ana
print(clase_a ^ clase_b)       # en una sola clase""",
  h="compara dos conjuntos de alumnos con las cuatro operaciones",
  pr=("El operador de intersección de conjuntos es ___. (un carácter)", "&"),
  pr2=("El operador de unión de conjuntos es ___. (un carácter)", "|"),
  ec="confundir la intersección con la unión"),
K("Diccionarios",
  d="colección de pares clave-valor entre llaves",
  u="asociar datos con nombres para encontrarlos rápido",
  mas="{\"nombre\": \"Ana\", \"edad\": 20} asocia cada clave con un valor. Se accede con la clave: persona[\"nombre\"]. Las claves deben ser únicas e inmutables (textos, números, tuplas). Desde Python 3.7 conservan el orden de inserción.",
  k=["Un diccionario guarda pares clave-valor entre llaves.", "Se accede a un valor con su clave entre corchetes.", "Las claves de un diccionario son únicas."],
  sit="Quieres guardar nombre, edad y ciudad de una persona en una sola variable. ¿Qué usas?",
  cod="""persona = {"nombre": "Ana", "edad": 20, "ciudad": "Lima"}
print(persona["nombre"])               # Ana
persona["edad"] = 21                   # modificar
persona["correo"] = "ana@correo.com"   # añadir
del persona["ciudad"]                  # borrar
print(persona, len(persona))""",
  h="crea un diccionario y lee, modifica, añade y borra datos",
  pr=("Un diccionario se escribe entre ___. (llaves)", "llaves", "{}"),
  pr2=("Cada elemento de un diccionario es un par clave y ___. (5 letras)", "valor"),
  ec="leer una clave que no existe y provocar un KeyError",
  err=("persona = {\"nombre\": \"Ana\"}\nprint(persona[\"edad\"])", 2, "La clave edad no existe: Python lanza un KeyError.")),
K("Métodos de diccionarios",
  d="get, keys, values, items, pop y update para trabajar con diccionarios",
  u="leer, recorrer y modificar diccionarios con seguridad",
  mas="get(clave, defecto) lee sin error si no existe. keys(), values() e items() devuelven las claves, los valores y los pares. pop(clave) quita y devuelve; update(otro) fusiona dos diccionarios. setdefault añade una clave solo si falta.",
  k=["get() lee un valor sin provocar error si falta la clave.", "items() devuelve los pares clave-valor.", "update() fusiona otro diccionario."],
  sit="Quieres leer una clave que puede no existir y obtener un valor por defecto en vez de un error. ¿Qué usas?",
  cod="""persona = {"nombre": "Ana", "edad": 20}
print(persona.get("ciudad", "sin ciudad"))     # no falla
print(list(persona.keys()))                    # ['nombre', 'edad']
print(list(persona.values()))                  # ['Ana', 20]
persona.update({"edad": 21, "pais": "Perú"})   # fusiona
print(persona)
print(persona.pop("pais"), persona)""",
  h="lee con valor por defecto, lista claves y valores, fusiona y quita datos",
  pr=("El método que lee una clave sin provocar error es ___(). (3 letras)", "get"),
  pr2=("El método que devuelve los pares clave-valor es ___(). (5 letras)", "items"),
  ec="leer con corchetes una clave que puede no existir"),
K("Recorrer diccionarios",
  d="formas de recorrer claves, valores o pares de un diccionario",
  u="procesar todos los datos de un diccionario",
  mas="for clave in dic recorre las claves. for valor in dic.values() recorre los valores y for clave, valor in dic.items() los pares. Es la forma más habitual. No se debe añadir ni borrar claves mientras se recorre el diccionario.",
  k=["for x in diccionario recorre las claves.", "items() permite recorrer clave y valor a la vez.", "No se deben añadir ni quitar claves mientras se recorre."],
  sit="Quieres mostrar cada producto con su precio. ¿Qué forma de recorrer usas?",
  cod="""precios = {"pan": 1.2, "leche": 0.9, "huevos": 2.5}
for producto in precios:                        # solo claves
    print(producto)
for producto, precio in precios.items():        # pares
    print(f"{producto}: {precio} €")
print(sum(precios.values()))                    # suma de valores""",
  h="recorre un diccionario por claves y por pares y suma sus valores",
  pr=("El método para recorrer claves y valores a la vez es ___(). (5 letras)", "items"),
  pr2=("Por defecto, for x in diccionario recorre las ___. (6 letras)", "claves"),
  ec="modificar el diccionario mientras se recorre"),
K("Diccionarios anidados",
  d="diccionarios cuyos valores son otros diccionarios o listas",
  u="representar datos con estructura, como fichas de alumnos",
  mas="Un alumno puede ser un diccionario con una lista de notas: {\"nombre\": \"Ana\", \"notas\": [8, 9]}. Se accede encadenando claves: alumnos[\"ana\"][\"notas\"][0]. Es la misma estructura que usa JSON en las API.",
  k=["Un diccionario puede contener otros diccionarios y listas.", "Se accede encadenando claves e índices.", "Es la estructura que usa JSON."],
  sit="Quieres guardar varios alumnos, cada uno con su lista de notas. ¿Qué estructura usas?",
  cod="""alumnos = {
    "ana":  {"edad": 20, "notas": [8, 9, 7]},
    "luis": {"edad": 22, "notas": [6, 5]},
}
print(alumnos["ana"]["edad"])               # 20
print(alumnos["luis"]["notas"][0])          # 6
alumnos["ana"]["notas"].append(10)
for nombre, ficha in alumnos.items():
    print(nombre, sum(ficha["notas"]) / len(ficha["notas"]))""",
  h="guarda alumnos con sus notas y calcula el promedio de cada uno",
  pr=("En alumnos[\"ana\"][\"edad\"], «ana» es una ___. (5 letras)", "clave"),
  pr2=("La estructura de las API que se parece a un diccionario anidado es ___. (4 letras)", "json"),
  ec="olvidar una de las claves intermedias al acceder"),
K("Comprensión de listas",
  d="forma corta de crear una lista a partir de otra",
  u="transformar y filtrar listas en una sola línea",
  mas="[x * 2 for x in numeros] crea una lista con el doble de cada número. Se puede filtrar con if: [x for x in numeros if x > 5]. Es más rápida y legible que un bucle con append, siempre que no se complique demasiado.",
  k=["Una comprensión de lista crea una lista en una línea.", "Puede incluir un if para filtrar.", "Es más corta que un bucle con append."],
  sit="Quieres crear una lista con el doble de cada número de otra, en una sola línea. ¿Qué técnica usas?",
  cod="""numeros = [1, 2, 3, 4, 5, 6]
dobles = [n * 2 for n in numeros]
pares = [n for n in numeros if n % 2 == 0]
cuadrados_pares = [n ** 2 for n in numeros if n % 2 == 0]
print(dobles)
print(pares)
print(cuadrados_pares)""",
  h="crea listas transformando y filtrando otra lista en una sola línea",
  pr=("En [n * 2 for n in lista], la palabra que introduce el bucle es ___. (3 letras)", "for"),
  pr2=("Para filtrar elementos se añade al final un ___. (2 letras)", "if"),
  ec="escribir comprensiones tan largas que no se entienden"),
K("Comprensión de diccionarios y conjuntos",
  d="comprensiones que crean diccionarios o conjuntos en una línea",
  u="construir estructuras a partir de otras con pocas líneas",
  mas="{p: len(p) for p in palabras} crea un diccionario palabra → longitud. {x % 3 for x in numeros} crea un conjunto. Funcionan igual que las de lista, con llaves y, en el caso del diccionario, con el par clave: valor.",
  k=["Una comprensión de diccionario usa llaves y clave: valor.", "Una comprensión de conjunto usa llaves sin pares.", "Siguen la misma lógica que las de lista."],
  sit="Quieres crear un diccionario que asocie cada palabra con su longitud en una sola línea. ¿Qué técnica usas?",
  cod="""palabras = ["pera", "kiwi", "manzana"]
longitudes = {p: len(p) for p in palabras}
print(longitudes)                   # {'pera': 4, 'kiwi': 4, 'manzana': 7}
restos = {n % 3 for n in range(10)}
print(restos)                       # {0, 1, 2}""",
  h="crea un diccionario de longitudes y un conjunto de restos con comprensiones",
  pr=("En una comprensión de diccionario, clave y valor se separan con ___. (dos puntos)", ":", "dos puntos"),
  pr2=("Una comprensión de conjunto usa ___ sin pares. (6 letras: llaves)", "llaves"),
  ec="olvidar los dos puntos entre clave y valor"),
K("enumerate y zip",
  d="funciones que numeran elementos o recorren varias listas a la vez",
  u="recorrer con índices o emparejar listas sin bucles complicados",
  mas="enumerate(lista) da pares (posición, elemento); admite start=1 para contar desde uno. zip(a, b) empareja elementos de dos listas y se detiene en la más corta. Se combinan con desempaquetado en el for.",
  k=["enumerate entrega la posición y el elemento.", "zip empareja elementos de varias listas.", "zip se detiene cuando termina la lista más corta."],
  sit="Quieres recorrer una lista mostrando el número de cada elemento. ¿Qué función usas?",
  cod="""frutas = ["manzana", "pera", "uva"]
for i, fruta in enumerate(frutas, start=1):
    print(i, fruta)
nombres = ["Ana", "Luis"]
notas = [9, 7]
for nombre, nota in zip(nombres, notas):
    print(nombre, "->", nota)
print(dict(zip(nombres, notas)))""",
  h="numera elementos, empareja dos listas y crea un diccionario con zip",
  pr=("La función que entrega posición y elemento es ___(). (9 letras)", "enumerate"),
  pr2=("La función que empareja elementos de varias listas es ___(). (3 letras)", "zip"),
  ec="usar range(len(lista)) cuando bastaba enumerate"),
K("Ordenar con key",
  d="parámetro que indica el criterio de ordenación",
  u="ordenar listas de objetos o textos por un campo concreto",
  mas="sorted(lista, key=funcion) ordena según el valor que devuelve la función para cada elemento. Con listas de diccionarios se usa una lambda: key=lambda a: a[\"nota\"]. Combinado con reverse=True da rankings. Es la base de «los 3 mejores».",
  k=["El parámetro key define el criterio de ordenación.", "Con una lambda se ordena por un campo de un diccionario.", "reverse=True invierte el orden."],
  sit="Quieres ordenar una lista de alumnos por su nota, de mayor a menor. ¿Qué parámetro usas?",
  cod="""alumnos = [
    {"nombre": "Ana", "nota": 9},
    {"nombre": "Luis", "nota": 5},
    {"nombre": "Marta", "nota": 8},
]
ranking = sorted(alumnos, key=lambda a: a["nota"], reverse=True)
print([a["nombre"] for a in ranking])        # ['Ana', 'Marta', 'Luis']
print(ranking[0]["nombre"])                  # el mejor""",
  h="ordena alumnos por nota de mayor a menor y obtiene al mejor",
  pr=("El parámetro que indica el criterio de ordenación es ___. (3 letras)", "key"),
  pr2=("Para un ranking de mayor a menor se usa reverse=___. (4 letras)", "true"),
  ec="olvidar la lambda y ordenar por el diccionario completo"),
K("Contar y agrupar",
  d="técnicas para contar elementos y agruparlos con diccionarios",
  u="calcular frecuencias y clasificaciones",
  mas="Un diccionario sirve de contador: conteo[palabra] = conteo.get(palabra, 0) + 1. El módulo collections ofrece Counter, que lo hace solo, y defaultdict, que crea valores por defecto. Con Counter(lista).most_common(3) obtienes los más frecuentes.",
  k=["Un diccionario puede usarse como contador.", "Counter cuenta automáticamente los elementos.", "most_common devuelve los más frecuentes."],
  sit="Quieres contar cuántas veces aparece cada palabra en una lista. ¿Qué usas?",
  cod="""from collections import Counter
palabras = ["sol", "luna", "sol", "mar", "sol", "luna"]
conteo = {}
for p in palabras:
    conteo[p] = conteo.get(p, 0) + 1          # contador manual
print(conteo)
print(Counter(palabras).most_common(2))       # los 2 más frecuentes""",
  h="cuenta palabras a mano y con Counter",
  pr=("La clase de collections que cuenta elementos es ___. (7 letras)", "counter"),
  pr2=("El método que devuelve los elementos más frecuentes es most____(). (6 letras)", "common"),
  ec="contar elementos con un bucle anidado cuando Counter lo resuelve"),
]
