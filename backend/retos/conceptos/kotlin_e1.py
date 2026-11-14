"""Kotlin · Etapa 1: fundamentos del lenguaje y expresiones."""
from ..generador import K

LISTA = [
K("Hola, mundo",
  d="programa mínimo de Kotlin que inicia en main y muestra un saludo",
  u="verificar que el entorno compila y ejecuta un primer ejemplo",
  mas="Un primer programa Kotlin/JVM suele declarar `fun main()` y mostrar texto con `println`. Kotlin es un lenguaje de tipado estático que también puede compilarse para otros destinos.",
  k=["Un programa Kotlin/JVM puede comenzar en fun main().", "println muestra el saludo en la salida estándar.", "Kotlin es un lenguaje de tipado estático."],
  sit="Quieres probar una instalación de Kotlin mostrando un saludo desde el punto de entrada. ¿Qué ejemplo escribes?",
  cod="""fun main() {
    println("Hola, mundo")
}""", out="Hola, mundo",
  h="inicia el programa y muestra un saludo",
  pr=("La función de entrada de un programa Kotlin habitual se llama ___.", "main"),
  pr2=("La función Kotlin que muestra una línea se llama ___.", "println"),
  ec="empezar un programa de consola sin definir su punto de entrada main"),
K("Variables",
  d="espacios con nombre que guardan valores mediante declaraciones Kotlin",
  u="conservar y consultar datos durante la ejecución",
  mas="Las variables locales se declaran con `val` si no se reasignarán o con `var` si deben cambiar. El compilador infiere un tipo a partir del inicializador cuando no se escribe uno explícitamente.",
  k=["`val` declara una referencia no reasignable.", "`var` permite reasignar una variable.", "Kotlin puede inferir el tipo desde el valor inicial."],
  sit="Un programa necesita guardar el nombre de una persona para usarlo en un mensaje posterior. ¿Qué declaras?",
  cod="""fun main() {
    val lenguaje = "Kotlin"
    println("Lenguaje: $lenguaje")
}""", out="Lenguaje: Kotlin",
  h="guarda un nombre en una variable y lo inserta en un texto",
  pr=("La palabra clave para declarar una referencia no reasignable es ___.", "val"),
  pr2=("La palabra clave para declarar una variable reasignable es ___.", "var"),
  ec="usar val para un dato que debe reasignarse después"),
K("println",
  d="función que escribe un valor en la salida estándar y termina la línea",
  u="mostrar texto o resultados durante la ejecución",
  mas="`println` convierte su argumento en texto y añade un salto de línea. Varias llamadas producen líneas separadas; `print` escribe sin añadir ese salto.",
  k=["`println` añade un salto de línea al final.", "`print` no añade automáticamente un salto de línea.", "Ambas funciones pueden mostrar texto y valores."],
  sit="Quieres mostrar un resultado y que la siguiente salida aparezca en otra línea. ¿Qué función usas?",
  cod="""fun main() {
    println("Uno")
    println(2)
}""", out="Uno\n2",
  h="muestra dos valores en líneas separadas",
  pr=("La función que imprime y termina la línea es ___.", "println"),
  pr2=("La función que imprime sin salto de línea es ___.", "print"),
  ec="suponer que `print` y `println` añaden el mismo formato"),
K("Comentarios de línea",
  d="texto iniciado con // que Kotlin ignora hasta el final de esa línea",
  u="explicar una instrucción sin cambiar el comportamiento del programa",
  mas="Un comentario de línea comienza con `//` y termina al cerrar la línea. Sirve para explicar decisiones o intención, no para ejecutar código.",
  k=["`//` inicia un comentario de línea.", "El comentario termina al final de la línea.", "El compilador no ejecuta el texto comentado."],
  sit="Quieres dejar una explicación breve al lado de una instrucción sin que se ejecute. ¿Qué escribes?",
  cod="""fun main() {
    // Este texto solo documenta el ejemplo
    println("Listo")
}""", out="Listo",
  h="muestra un mensaje mientras ignora el comentario",
  pr=("El marcador de comentario de una línea en Kotlin es ___.", "//"),
  pr2=("El comentario iniciado con // termina al final de la ___.", "línea", "linea"),
  ec="creer que un comentario con // puede continuar en la línea siguiente"),
K("Comentario de bloque",
  d="texto entre /* y */ que el compilador no ejecuta",
  u="documentar una sección con varias líneas",
  mas="Los comentarios de bloque empiezan con `/*` y terminan con `*/`. Kotlin también admite comentarios de bloque anidados, a diferencia de algunos lenguajes populares.",
  k=["`/*` abre un comentario de bloque.", "`*/` cierra el comentario.", "Kotlin permite anidar comentarios de bloque."],
  sit="Necesitas explicar varias líneas de código sin ejecutarlas. ¿Qué tipo de comentario eliges?",
  cod="""fun main() {
    /* Este bloque
       ocupa dos líneas */
    println("Visible")
}""", out="Visible",
  h="ignora dos líneas comentadas y muestra la salida",
  pr=("El marcador que abre un comentario de bloque es ___.", "/*"),
  pr2=("Los comentarios de bloque Kotlin pueden estar ___.", "anidados"),
  ec="olvidar cerrar un comentario con */"),
K("Declaración val",
  d="declaración de una referencia que no puede reasignarse después de inicializarse",
  u="representar un valor que debe conservar la misma referencia",
  mas="`val` crea una referencia de solo lectura y puede inicializarse más tarde si el compilador demuestra que recibe un valor antes de usarse. No implica que el objeto referenciado sea inmutable.",
  k=["Una referencia declarada con `val` no puede reasignarse.", "Un `val` puede inicializarse una sola vez en una ruta válida.", "El objeto apuntado por un `val` mutable todavía puede cambiar."],
  sit="Guardas el nombre de una persona y no quieres reasignar esa referencia. ¿Qué declaración eliges?",
  cod="""fun main() {
    val nombre = "Luz"
    println(nombre)
}""", out="Luz",
  h="declara una referencia de solo lectura y la muestra",
  pr=("La palabra clave para una referencia no reasignable es ___.", "val"),
  pr2=("Una variable val no puede ser ___ después de inicializarse.", "reasignada"),
  ec="decir que val hace inmutable cualquier objeto que contiene"),
K("Declaración var",
  d="declaración de una variable cuya referencia puede recibir otro valor",
  u="guardar un estado que necesita actualizarse",
  mas="`var` permite reasignar la variable a lo largo del programa, pero el nuevo valor debe respetar el tipo declarado o inferido. Se puede preferir `val` cuando no hace falta reasignación.",
  k=["Una variable `var` admite reasignación.", "Los valores reasignados deben ser compatibles con su tipo.", "`val` suele ser preferible si la referencia no necesita cambiar."],
  sit="El marcador de una partida debe aumentar después de cada punto. ¿Qué declaración permite actualizarlo?",
  cod="""fun main() {
    var puntos = 2
    puntos = puntos + 1
    println(puntos)
}""", out="3",
  h="actualiza un marcador y muestra su nuevo valor",
  pr=("La palabra clave para una variable reasignable es ___.", "var"),
  pr2=("Al reasignar una var, el valor debe respetar su ___.", "tipo"),
  ec="usar val y luego intentar reasignar la variable"),
K("Inferencia de tipos",
  d="capacidad del compilador de deducir el tipo desde el valor inicial",
  u="evitar anotar tipos cuando la expresión ya los deja claros",
  mas="Kotlin infiere el tipo de una variable local a partir de su inicializador. La inferencia no elimina el chequeo estático: el tipo sigue determinando qué operaciones son válidas.",
  k=["`val total = 4` infiere que total es Int.", "La inferencia ocurre durante la compilación.", "Un tipo inferido sigue restringiendo las asignaciones posteriores."],
  sit="El valor inicial 8 basta para que Kotlin determine que una variable es entera. ¿Qué mecanismo usa?",
  cod="""fun main() {
    val cantidad = 8
    println(cantidad)
}""", out="8",
  h="usa y muestra una variable cuyo tipo se infiere como Int",
  pr=("El mecanismo que deduce un tipo desde su inicializador es la ___.", "inferencia"),
  pr2=("La inferencia de tipos ocurre durante la ___.", "compilación"),
  ec="pensar que inferir un tipo significa que Kotlin deja de comprobarlo"),
K("Tipo Int",
  d="tipo entero de 32 bits con signo en Kotlin/JVM",
  u="representar conteos y números enteros de rango moderado",
  mas="`Int` almacena enteros desde -2 147 483 648 hasta 2 147 483 647. Los literales enteros habituales se infieren como Int cuando caben en ese rango.",
  k=["`Int` tiene 32 bits en Kotlin.", "Su rango incluye valores negativos y positivos.", "Un literal como 42 se infiere normalmente como Int."],
  sit="Necesitas guardar una cantidad entera pequeña como 27 sin decimales. ¿Qué tipo estándar usas?",
  cod="""fun main() {
    val cantidad: Int = 27
    println(cantidad)
}""", out="27",
  h="declara y muestra un valor Int",
  pr=("El tipo entero estándar de 32 bits en Kotlin es ___.", "Int"),
  pr2=("El tipo Int de Kotlin tiene ___ bits.", "32"),
  ec="usar Int esperando que almacene enteros de tamaño ilimitado"),
K("Tipo Long",
  d="tipo entero de 64 bits con signo en Kotlin/JVM",
  u="representar enteros que pueden superar el rango de Int",
  mas="`Long` ofrece un rango mayor que `Int` al usar 64 bits. Un literal puede marcarse con `L`, por ejemplo `3_000_000_000L`, cuando excede el máximo de Int.",
  k=["`Long` tiene 64 bits en Kotlin/JVM.", "Su rango es mayor que el de Int.", "El sufijo L identifica un literal Long."],
  sit="Un contador puede superar 2 147 483 647 y debe seguir siendo entero. ¿Qué tipo eliges?",
  cod="""fun main() {
    val poblacion: Long = 3_000_000_000L
    println(poblacion)
}""", out="3000000000",
  h="almacena y muestra un entero mayor que el máximo de Int",
  pr=("El tipo entero de 64 bits en Kotlin es ___.", "Long"),
  pr2=("El sufijo habitual de un literal Long es ___.", "L"),
  ec="escribir un literal que excede Int sin convertirlo a Long"),
K("Tipo Double",
  d="tipo de punto flotante de doble precisión en Kotlin/JVM",
  u="representar medidas o cálculos que requieren parte fraccionaria",
  mas="`Double` usa representación binaria de punto flotante de 64 bits. Algunos decimales no tienen representación binaria exacta, por lo que no es apropiado para dinero que exija precisión decimal exacta.",
  k=["`Double` tiene precisión de 64 bits.", "Los literales decimales se infieren normalmente como Double.", "El punto flotante puede introducir aproximaciones."],
  sit="Quieres representar una medida con decimales y aceptas la aproximación de punto flotante. ¿Qué tipo usas?",
  cod="""fun main() {
    val altura: Double = 1.75
    println(altura)
}""", out="1.75",
  h="representa y muestra una medida decimal",
  pr=("El tipo de punto flotante de doble precisión es ___.", "Double"),
  pr2=("Double usa una representación de punto flotante de ___ bits.", "64"),
  ec="usar Double para dinero que requiere decimales exactos"),
K("Tipo Boolean",
  d="tipo que solo puede tomar los valores true o false",
  u="representar el resultado de una condición lógica",
  mas="`Boolean` modela dos estados y es el tipo de expresiones de comparación. Kotlin no convierte automáticamente números o cadenas a booleanos.",
  k=["Los valores Boolean son true y false.", "Las comparaciones producen Boolean.", "Kotlin no trata 0 como false automáticamente."],
  sit="Necesitas guardar si una puerta está abierta o cerrada usando dos estados. ¿Qué tipo eliges?",
  cod="""fun main() {
    val esPar: Boolean = 8 % 2 == 0
    println(esPar)
}""", out="true",
  h="calcula si un número es par y muestra el booleano",
  pr=("El tipo con valores true y false es ___.", "Boolean"),
  pr2=("Una comparación como 4 > 2 produce un valor ___.", "Boolean"),
  ec="suponer que el número 1 se convierte automáticamente en true"),
K("Tipo Char",
  d="tipo que representa un único carácter Unicode y se escribe entre comillas simples",
  u="guardar una letra, dígito u otro carácter individual",
  mas="Un literal `Char` usa comillas simples, por ejemplo `'K'`. En Kotlin/JVM Char representa una unidad de código UTF-16, por lo que ciertos símbolos Unicode suplementarios requieren más de un Char.",
  k=["Un literal Char usa comillas simples.", "Char representa una unidad de código UTF-16 en JVM.", "Una cadena de varios caracteres no es Char."],
  sit="Solo necesitas almacenar la letra inicial de una palabra. ¿Qué tipo eliges?",
  cod="""fun main() {
    val inicial: Char = 'K'
    println(inicial)
}""", out="K",
  h="declara y muestra un carácter",
  pr=("El tipo Kotlin para un carácter individual es ___.", "Char"),
  pr2=("Los literales Char se escriben entre comillas ___.", "simples"),
  ec="escribir un literal Char entre comillas dobles"),
K("Tipo String",
  d="tipo que representa una secuencia inmutable de caracteres",
  u="guardar y procesar texto",
  mas="Los literales String se escriben entre comillas dobles. Una cadena no cambia su contenido: operaciones como `uppercase()` devuelven otra cadena.",
  k=["Un literal String usa comillas dobles.", "String es una secuencia de caracteres.", "Las operaciones de transformación devuelven una cadena, no modifican la original."],
  sit="Vas a guardar el título de un libro como texto de varios caracteres. ¿Qué tipo usas?",
  cod="""fun main() {
    val titulo: String = "Mar de datos"
    println(titulo)
}""", out="Mar de datos",
  h="almacena y muestra un texto",
  pr=("El tipo usado para guardar una secuencia de texto es ___.", "String"),
  pr2=("Los literales String se escriben entre comillas ___.", "dobles"),
  ec="usar comillas simples para intentar crear una cadena"),
K("Plantilla de cadena",
  d="cadena con expresiones interpoladas mediante el prefijo $",
  u="insertar valores en texto sin concatenaciones manuales",
  mas="`$nombre` inserta una variable simple dentro de una cadena. `${expresion}` permite evaluar una expresión y convertir su resultado en texto.",
  k=["`$variable` interpola una variable en una cadena.", "`${...}` interpola una expresión.", "La plantilla se evalúa al construir la cadena."],
  sit="Quieres incluir el valor de una variable en un saludo sin concatenar con +. ¿Qué recurso utilizas?",
  cod="""fun main() {
    val nombre = "Eva"
    println("Hola, $nombre")
}""", out="Hola, Eva",
  h="inserta el valor de una variable en el saludo",
  pr=("El mecanismo Kotlin que inserta valores en texto es una plantilla de ___.", "cadena"),
  pr2=("Para interpolar una expresión se escribe entre ${ y ___.", "}"),
  ec="olvidar el signo $ delante de la variable interpolada"),
K("Operadores aritméticos",
  d="símbolos como +, -, * y / que realizan operaciones numéricas",
  u="calcular nuevos valores a partir de números",
  mas="Kotlin ofrece operadores aritméticos habituales y `%` para el resto. El significado de la división depende de los tipos: con dos Int el resultado también es entero.",
  k=["`+` suma y `*` multiplica.", "`%` calcula el resto de la división.", "La división de dos Int trunca la parte fraccionaria."],
  sit="Necesitas calcular el total de 4 cajas con 3 objetos cada una. ¿Qué familia de operadores usas?",
  cod="""fun main() {
    val total = 4 * 3
    println(total)
}""", out="12",
  h="multiplica la cantidad de cajas por objetos por caja",
  pr=("El operador Kotlin para obtener el resto es ___.", "%"),
  pr2=("El operador que multiplica dos números es ___.", "*"),
  ec="esperar que una división Int conserve la parte decimal"),
K("División entera",
  d="división entre enteros cuyo resultado descarta la parte fraccionaria",
  u="calcular cocientes enteros como grupos completos",
  mas="Cuando ambos operandos son Int, `/` produce un Int y trunca hacia cero. Si se necesita una fracción, al menos uno de los operandos debe ser Float o Double.",
  k=["`7 / 2` con operandos Int da 3.", "La división entera trunca hacia cero.", "Convertir un operando a Double permite un resultado decimal."],
  sit="Repartes 7 elementos en grupos de 2 y solo cuentas grupos completos. ¿Qué división aplicas?",
  cod="""fun main() {
    val grupos = 7 / 2
    println(grupos)
}""", out="3",
  h="divide enteros y conserva solo el cociente entero",
  pr=("La división de dos Int que descarta fracciones es división ___.", "entera"),
  pr2=("La expresión 7 / 2 con Int devuelve ___.", "3"),
  ec="esperar que 7 / 2 con Int produzca 3.5"),
K("Comparaciones",
  d="operaciones como <, >, <= y >= que comparan valores y devuelven Boolean",
  u="comprobar relaciones de orden entre datos",
  mas="Los operadores de comparación producen `true` o `false`. Para tipos numéricos comparan magnitudes; para otros tipos, el soporte depende de que exista un orden comparable.",
  k=["`<` comprueba si el valor izquierdo es menor.", "`>=` incluye la igualdad.", "El resultado de una comparación es Boolean."],
  sit="Quieres saber si una temperatura supera el límite de 30 grados. ¿Qué tipo de operación usas?",
  cod="""fun main() {
    val superaLimite = 32 > 30
    println(superaLimite)
}""", out="true",
  h="comprueba si 32 es mayor que 30",
  pr=("El operador para comprobar que x no supera y es ___.", "<="),
  pr2=("Una comparación devuelve un valor de tipo ___.", "Boolean"),
  ec="confundir = de asignación con == de igualdad"),
K("Igualdad estructural",
  d="comparación con == que comprueba si dos valores son iguales según su contenido",
  u="comparar valores sin exigir que sean el mismo objeto",
  mas="En Kotlin `==` realiza una comprobación segura de igualdad estructural, equivalente a llamar a `equals` con manejo de nulos. Para comprobar identidad de referencia se usa `===`.",
  k=["`==` compara igualdad estructural.", "`===` comprueba identidad de referencia.", "`==` puede delegar en una implementación de equals."],
  sit="Dos cadenas creadas por separado contienen el mismo texto y quieres comparar su valor. ¿Qué operador usas?",
  cod="""fun main() {
    val iguales = "sol" == "s" + "ol"
    println(iguales)
}""", out="true",
  h="compara el contenido de dos cadenas",
  pr=("El operador Kotlin de igualdad estructural es ___.", "=="),
  pr2=("El operador para comprobar identidad de referencia es ___.", "==="),
  ec="usar === cuando se quiere comparar el contenido de dos valores"),
K("Conversión explícita",
  d="llamada a funciones como toLong o toDouble para convertir un valor numérico",
  u="cambiar a propósito el tipo de un número",
  mas="Kotlin no convierte automáticamente un Int a Long al asignarlo. Las conversiones numéricas se expresan con funciones como `toLong()` y pueden perder información si se convierte a un tipo más pequeño.",
  k=["`Int.toLong()` produce un Long.", "Kotlin no ensancha tipos numéricos de forma implícita.", "Convertir Double a Int descarta la fracción."],
  sit="Tienes un Int y una API requiere recibir un Long de forma explícita. ¿Qué operación usas?",
  cod="""fun main() {
    val numero: Int = 12
    val grande: Long = numero.toLong()
    println(grande)
}""", out="12",
  h="convierte un Int en Long antes de mostrarlo",
  pr=("La función de conversión de Int a Long se llama ___.", "toLong"),
  pr2=("Kotlin requiere una conversión numérica ___.", "explícita"),
  ec="asignar un Int a Long suponiendo que Kotlin lo convierte automáticamente"),
]
