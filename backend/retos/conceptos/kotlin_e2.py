"""Kotlin · Etapa 2: control de flujo y funciones."""
from ..generador import K

LISTA = [
K("Decisiones",
  d="construcción condicional que también puede producir un valor",
  u="elegir un resultado según una condición",
  mas="En Kotlin `if` puede usarse como expresión y asignarse a una variable. En ese caso ambas ramas deben producir un valor compatible.",
  k=["`if` puede producir un valor.", "Una expresión if usada como valor necesita una rama else.", "La condición de if debe ser Boolean."],
  sit="El precio con descuento depende de una condición y quieres asignar directamente el resultado. ¿Qué construcción eliges?",
  cod="""fun main() {
    val edad = 20
    val acceso = if (edad >= 18) "permitido" else "denegado"
    println(acceso)
}""", out="permitido",
  h="elige el resultado de acuerdo con la edad",
  pr=("La construcción que puede elegirse como valor en Kotlin es ___.", "if"),
  pr2=("Una expresión if usada como valor debe incluir una rama ___.", "else"),
  ec="omitir else al usar if para producir un valor"),
K("Bucles",
  d="estructuras que repiten una instrucción o bloque de código",
  u="automatizar acciones repetidas sin duplicar instrucciones",
  mas="Kotlin ofrece `for`, `while` y `do while` para recorrer datos o repetir según una condición. La función estándar `repeat` es otra opción cuando se conoce de antemano un número fijo de repeticiones.",
  k=["Un bucle ejecuta repetidamente un bloque.", "`repeat(n)` ejecuta su bloque n veces si n es positivo.", "while comprueba la condición antes de cada iteración."],
  sit="Debes mostrar el mismo aviso tres veces sin escribir tres llamadas separadas. ¿Qué mecanismo aplicas?",
  cod="""fun main() {
    repeat(3) { println("Aviso") }
}""", out="Aviso\nAviso\nAviso",
  h="repite tres veces un bloque que muestra un aviso",
  pr=("La estructura que repite un bloque de instrucciones se llama ___.", "bucle"),
  pr2=("La función de la biblioteca estándar para repetir n veces es ___.", "repeat"),
  ec="usar una repetición sin definir cuántas veces debe terminar"),
K("Rangos",
  d="secuencia de valores delimitada con operadores como .., until o downTo",
  u="describir intervalos para recorridos o comprobaciones",
  mas="`1..4` incluye ambos extremos, mientras que `1 until 4` excluye el límite superior. `downTo` crea un rango descendente y los rangos también pueden comprobarse con `in`.",
  k=["`..` incluye el límite final.", "`until` excluye el límite superior.", "`downTo` crea un rango descendente."],
  sit="Necesitas recorrer las posiciones 1, 2 y 3 sin incluir 4. ¿Qué operador de rango eliges?",
  cod="""fun main() {
    for (n in 1 until 4) print(n)
}""", out="123",
  h="recorre del 1 al 3 sin incluir el límite 4",
  pr=("El operador de rango que excluye el límite superior es ___.", "until"),
  pr2=("El rango inclusivo que termina en 4 se escribe 1 ___ 4.", ".."),
  ec="suponer que until incluye su límite final"),
K("Bucle for",
  d="bucle que itera sobre los elementos de una colección o rango",
  u="repetir instrucciones por cada elemento disponible",
  mas="En Kotlin `for` recorre objetos iterables, como rangos, listas y cadenas. No usa la forma tradicional de tres expresiones de C; la variable de iteración se declara tras `for`.",
  k=["`for (x in elementos)` visita cada elemento.", "Un rango puede usarse como fuente de iteración.", "La variable de iteración no necesita declararse con var."],
  sit="Quieres imprimir cada número de un rango sin gestionar manualmente un contador. ¿Qué bucle usas?",
  cod="""fun main() {
    for (n in 1..3) println(n)
}""", out="1\n2\n3",
  h="imprime cada valor del rango inclusivo",
  pr=("El bucle Kotlin que recorre elementos con `in` es ___.", "for"),
  pr2=("La forma habitual de recorrer elementos es `for (x ___ datos)`.", "in"),
  ec="esperar que Kotlin use en for la sintaxis de tres expresiones de C"),
K("Bucle while",
  d="bucle que repite su cuerpo mientras una condición booleana sea verdadera",
  u="repetir trabajo cuyo número de iteraciones depende de una condición",
  mas="`while` comprueba la condición antes de entrar al cuerpo. Si la condición es falsa desde el principio, el cuerpo no se ejecuta ninguna vez.",
  k=["`while` evalúa su condición antes del cuerpo.", "La condición debe ser Boolean.", "El cuerpo puede ejecutarse cero veces."],
  sit="El número de reintentos depende de una condición que puede ser falsa antes de empezar. ¿Qué bucle eliges?",
  cod="""fun main() {
    var cuenta = 1
    while (cuenta <= 3) {
        print(cuenta)
        cuenta++
    }
}""", out="123",
  h="repite tres veces mientras el contador cumpla la condición",
  pr=("El bucle que comprueba la condición antes de cada iteración es ___.", "while"),
  pr2=("Si la condición inicial de while es falsa, el cuerpo puede ejecutarse ___ veces.", "cero"),
  ec="olvidar modificar el estado y crear un while infinito"),
K("Bucle do while",
  d="bucle que ejecuta primero el cuerpo y comprueba la condición al final",
  u="garantizar que una acción ocurra al menos una vez",
  mas="En `do { ... } while (condicion)`, el cuerpo se ejecuta antes de probar la condición. Por eso se ejecuta al menos una vez, incluso si la condición resulta falsa.",
  k=["do while comprueba la condición después del cuerpo.", "El cuerpo de do while se ejecuta al menos una vez.", "La condición de continuación debe ser Boolean."],
  sit="Debes mostrar un menú una vez antes de comprobar si la persona desea repetir. ¿Qué bucle conviene?",
  cod="""fun main() {
    var vuelta = 0
    do {
        vuelta++
    } while (vuelta < 1)
    println(vuelta)
}""", out="1",
  h="ejecuta el cuerpo una vez aunque la condición final sea falsa",
  pr=("El bucle que revisa su condición después del cuerpo es ___.", "do while"),
  pr2=("El cuerpo de do while se ejecuta al menos ___ vez.", "una"),
  ec="elegir while cuando la acción debe ocurrir obligatoriamente una vez"),
K("break",
  d="instrucción que termina inmediatamente el bucle más cercano",
  u="salir de una repetición al cumplirse una condición",
  mas="`break` transfiere el control fuera del bucle más cercano. No es lo mismo que `continue`, que termina solo la iteración actual.",
  k=["`break` sale del bucle más cercano.", "`break` detiene iteraciones posteriores.", "`continue` salta a la siguiente iteración sin salir del bucle."],
  sit="Buscas elementos hasta hallar el primero que cumple la condición y después debes abandonar el recorrido. ¿Qué instrucción usas?",
  cod="""fun main() {
    for (n in 1..5) {
        if (n == 3) break
        print(n)
    }
}""", out="12",
  h="detiene el recorrido antes de imprimir el 3",
  pr=("La instrucción que sale del bucle es ___.", "break"),
  pr2=("break abandona el bucle ___ más cercano.", "más", "mas"),
  ec="usar continue esperando que termine el bucle"),
K("continue",
  d="instrucción que omite el resto de la iteración actual y pasa a la siguiente",
  u="saltar elementos que no requieren procesamiento",
  mas="`continue` mantiene el bucle activo y pasa a la siguiente iteración. A diferencia de `break`, no lo termina.",
  k=["`continue` omite el resto de la iteración actual.", "El bucle sigue después de continue.", "`break` termina el bucle en vez de saltar una iteración."],
  sit="Recorres números y quieres ignorar los pares, pero seguir procesando los demás. ¿Qué instrucción usas?",
  cod="""fun main() {
    for (n in 1..4) {
        if (n % 2 == 0) continue
        print(n)
    }
}""", out="13",
  h="omite los pares y muestra los impares",
  pr=("La instrucción para saltar a la siguiente iteración es ___.", "continue"),
  pr2=("continue omite la iteración actual, pero no termina el ___.", "bucle"),
  ec="confundir continue, que salta una iteración, con break"),
K("Declaración de función",
  d="bloque reutilizable declarado con fun, un nombre, paréntesis y un cuerpo",
  u="agrupar instrucciones para llamarlas en distintos lugares",
  mas="Una función de nivel superior se declara con `fun`. Puede llamarse antes o después de su declaración dentro del mismo archivo, y su cuerpo se delimita con llaves.",
  k=["`fun` declara una función Kotlin.", "Una función se ejecuta al invocarla, no al declararla.", "Las funciones pueden declararse en el nivel superior del archivo."],
  sit="Una conversión de unidades se necesita desde varias partes del programa y no quieres copiar sus instrucciones. ¿Qué declaras?",
  cod="""fun saludo() {
    println("Hola")
}
fun main() {
    saludo()
}""", out="Hola",
  h="declara una función y la invoca desde main",
  pr=("La palabra clave para declarar una función es ___.", "fun"),
  pr2=("Declarar una función no la ejecuta; hace falta ___ la función.", "invocar"),
  ec="confundir la declaración de una función con su llamada"),
K("Parámetros",
  d="nombres con tipo declarados en la firma para recibir argumentos",
  u="hacer que una función trabaje con datos proporcionados al llamarla",
  mas="Cada parámetro tiene un nombre y un tipo después de dos puntos. El argumento correspondiente se proporciona al llamar la función, salvo que haya un valor predeterminado.",
  k=["El tipo del parámetro se escribe después de dos puntos.", "Los argumentos se entregan en la llamada.", "Los parámetros permiten reutilizar una función con distintos datos."],
  sit="Una función de saludo debe aceptar un nombre diferente cada vez que se llama. ¿Qué agregas a su firma?",
  cod="""fun saludar(nombre: String) {
    println("Hola, $nombre")
}
fun main() {
    saludar("Mia")
}""", out="Hola, Mia",
  h="recibe un nombre como parámetro y lo saluda",
  pr=("El tipo de un parámetro se escribe después de ___.", ":"),
  pr2=("El dato que se pasa al llamar una función se llama ___.", "argumento"),
  ec="omitir el tipo de un parámetro en una declaración Kotlin"),
K("Tipo de retorno",
  d="tipo que una función declara después de dos puntos para el valor que devuelve",
  u="especificar el resultado disponible para quien llama a la función",
  mas="Una firma como `fun doble(n: Int): Int` declara que devuelve un Int. Si el cuerpo no devuelve un valor útil, el retorno por defecto es `Unit`.",
  k=["El tipo de retorno se escribe tras los paréntesis y dos puntos.", "La palabra clave return devuelve un valor desde una función.", "Una función sin retorno explícito usa Unit."],
  sit="La firma de una función debe indicar que su resultado es un número entero. ¿Qué parte declaras?",
  cod="""fun doble(n: Int): Int {
    return n * 2
}
fun main() {
    println(doble(6))
}""", out="12",
  h="devuelve el doble de un entero",
  pr=("El tipo de retorno se escribe después de paréntesis y ___.", ":"),
  pr2=("Una función sin valor de retorno útil devuelve ___.", "Unit"),
  ec="confundir el tipo de retorno con el tipo de un parámetro"),
K("return",
  d="instrucción que devuelve un valor y termina la ejecución de la función actual",
  u="entregar un resultado al código que llamó a la función",
  mas="`return expresion` sale de la función actual y proporciona el valor indicado. En una función que devuelve Unit, `return` también puede terminarla sin valor.",
  k=["return entrega el resultado de una función.", "La ejecución de esa función se detiene al llegar a return.", "El valor devuelto debe ser compatible con el tipo de retorno."],
  sit="Una función encuentra el total calculado y debe entregarlo al código que la invocó. ¿Qué instrucción usa?",
  cod="""fun sumar(a: Int, b: Int): Int {
    return a + b
}
fun main() {
    println(sumar(2, 5))
}""", out="7",
  h="devuelve la suma para que main pueda mostrarla",
  pr=("La instrucción que entrega un valor al llamador es ___.", "return"),
  pr2=("El valor tras return debe coincidir con el tipo de ___.", "retorno"),
  ec="mostrar un valor con println cuando la función debía devolverlo"),
K("Argumentos predeterminados",
  d="valores asignados a parámetros que pueden omitirse en una llamada",
  u="ofrecer una opción común sin exigirla en cada invocación",
  mas="Un valor predeterminado se declara en la firma, por ejemplo `veces: Int = 1`. Si se omite ese argumento, se usa el valor predeterminado.",
  k=["Un parámetro predeterminado puede omitirse al llamar.", "El valor por defecto se declara en la firma.", "Los argumentos posteriores pueden proporcionarse por nombre."],
  sit="Una función debe repetir una frase una vez por defecto, pero permitir que se indique otro número. ¿Qué característica de parámetros usas?",
  cod="""fun repetir(texto: String, veces: Int = 1) {
    repeat(veces) { print(texto) }
}
fun main() {
    repetir("ha", 2)
}""", out="haha",
  h="usa el parámetro veces para repetir el texto",
  pr=("Un valor opcional definido en la firma es un argumento ___.", "predeterminado"),
  pr2=("Un parámetro con valor predeterminado puede ___ en una llamada.", "omitirse"),
  ec="poner un parámetro obligatorio después de uno predeterminado y llamarlos posicionalmente"),
K("Argumentos con nombre",
  d="argumentos que identifican el parámetro por su nombre en la llamada",
  u="hacer llamadas legibles o especificar opciones posteriores",
  mas="La sintaxis `saludar(nombre = \"Ana\")` asocia el valor al parámetro por nombre. Es especialmente útil para omitir parámetros predeterminados anteriores o aclarar booleanos.",
  k=["Un argumento con nombre usa `nombre = valor`.", "La llamada no depende del orden posicional de argumentos nombrados.", "Nombrar argumentos puede mejorar la legibilidad."],
  sit="Una función tiene varios parámetros y quieres indicar claramente qué valor corresponde a cada uno. ¿Qué sintaxis usas?",
  cod="""fun ficha(nombre: String, activo: Boolean) {
    println("$nombre:$activo")
}
fun main() {
    ficha(activo = true, nombre = "Ivo")
}""", out="Ivo:true",
  h="pasa los argumentos indicando cada nombre de parámetro",
  pr=("La sintaxis `parametro = valor` crea un argumento con ___.", "nombre"),
  pr2=("Los argumentos con nombre indican explícitamente el ___ del parámetro.", "nombre"),
  ec="suponer que el nombre escrito en la llamada puede ser distinto al parámetro"),
K("Función de cuerpo expresión",
  d="función cuyo cuerpo consiste en una expresión precedida por el signo igual",
  u="escribir funciones breves que devuelven directamente una expresión",
  mas="La forma `fun doble(n: Int) = n * 2` infiere el tipo de retorno a partir de la expresión. No se escribe `return` en esta forma concisa.",
  k=["El cuerpo expresión se introduce con `=`.", "El compilador puede inferir su tipo de retorno.", "No se usa return antes de la expresión del cuerpo."],
  sit="Una función de una sola operación debe devolver el resultado sin un bloque extenso. ¿Qué forma concisa puedes usar?",
  cod="""fun triple(n: Int) = n * 3
fun main() {
    println(triple(4))
}""", out="12",
  h="calcula el triple mediante el cuerpo de una expresión",
  pr=("Una función de cuerpo expresión introduce su cuerpo con ___.", "="),
  pr2=("En un cuerpo expresión simple, el tipo de retorno puede ser ___.", "inferido"),
  ec="añadir return antes de la expresión de un cuerpo expresión"),
K("Variable local",
  d="variable declarada dentro de una función o bloque y visible en ese ámbito",
  u="guardar valores temporales que no deben filtrarse fuera del bloque",
  mas="El ámbito léxico determina dónde puede usarse una variable local. Una variable declarada dentro de unas llaves no es visible fuera de ellas.",
  k=["Una variable local solo está disponible en su ámbito.", "Las llaves delimitan muchos ámbitos locales.", "El nombre de una variable local no es visible antes de su declaración."],
  sit="Un cálculo intermedio solo se necesita dentro de una función y no debe ser global. ¿Dónde lo declaras?",
  cod="""fun calcular(): Int {
    val base = 4
    return base + 1
}
fun main() {
    println(calcular())
}""", out="5",
  h="usa una variable local para obtener el resultado",
  pr=("Una variable declarada dentro de una función es una variable ___.", "local"),
  pr2=("El conjunto de lugares donde puede usarse una variable es su ___.", "ámbito", "ambito"),
  ec="intentar usar fuera de su bloque una variable local"),
K("Lambda",
  d="expresión que crea una función anónima y puede capturar valores del ámbito",
  u="pasar una operación breve como valor",
  mas="Una lambda usa llaves; sus parámetros se escriben antes de `->`. Si tiene un solo parámetro, Kotlin puede referirse a él con `it`.",
  k=["Una lambda es una función sin nombre.", "La flecha separa parámetros y cuerpo.", "Una lambda puede capturar variables visibles en el contexto."],
  sit="Una operación breve debe pasarse a una función sin crear una declaración con nombre. ¿Qué expresión usas?",
  cod="""fun main() {
    val duplicar: (Int) -> Int = { n -> n * 2 }
    println(duplicar(5))
}""", out="10",
  h="crea y llama una lambda que duplica un entero",
  pr=("Una función anónima expresada con llaves se llama ___.", "lambda"),
  pr2=("La flecha que separa parámetros del cuerpo es ___.", "->"),
  ec="confundir el cuerpo de una lambda con una declaración fun nombrada"),
K("Función de orden superior",
  d="función que recibe otra función como argumento o devuelve una función",
  u="parametrizar una operación para reutilizar un algoritmo",
  mas="Las funciones son valores en Kotlin y sus tipos se escriben como `(Int) -> String`. Una función de orden superior puede invocar la función que recibe.",
  k=["Una función de orden superior recibe o devuelve funciones.", "El tipo `(Int) -> Int` describe una función de Int a Int.", "La lambda puede pasarse como argumento."],
  sit="Un mismo recorrido debe aceptar diferentes reglas de transformación proporcionadas por quien lo llama. ¿Qué tipo de función diseñas?",
  cod="""fun aplicar(n: Int, operacion: (Int) -> Int) = operacion(n)
fun main() {
    println(aplicar(6) { it + 1 })
}""", out="7",
  h="recibe una lambda y la aplica al número",
  pr=("La función que recibe otra función como argumento es de orden ___.", "superior"),
  pr2=("El tipo `(Int) -> Int` representa una función que recibe y devuelve ___.", "Int"),
  ec="intentar llamar una función recibida como si fuera un valor numérico"),
K("Función inline",
  d="función marcada con inline cuyo cuerpo puede insertarse en el punto de llamada por el compilador",
  u="reducir ciertos costos de llamadas y habilitar retornos no locales desde lambdas",
  mas="`inline` es una indicación al compilador, no una garantía de mejora de rendimiento. Se usa a menudo con funciones de orden superior; sus parámetros funcionales pueden anotarse `noinline` o `crossinline` cuando se requiere otro comportamiento.",
  k=["La palabra clave inline permite insertar el cuerpo en llamadas.", "inline se usa frecuentemente con parámetros lambda.", "La expansión inline no garantiza que todo programa sea más rápido."],
  sit="Una función de orden superior pequeña se marca para permitir al compilador insertar su cuerpo en los llamadores. ¿Qué modificador aplicas?",
  cod="""inline fun medir(n: Int, accion: (Int) -> Int) = accion(n)
fun main() {
    println(medir(4) { it * 2 })
}""", out="8",
  h="invoca una función inline con una lambda",
  pr=("El modificador Kotlin que permite insertar un cuerpo en la llamada es ___.", "inline"),
  pr2=("El modificador inline es una garantía de que el programa será más ___.", "rápido", "rapido"),
  ec="añadir inline a toda función suponiendo que siempre mejora el rendimiento"),
K("Punto de entrada main",
  d="función de nivel superior que la JVM puede usar para iniciar un programa Kotlin",
  u="definir las primeras instrucciones que se ejecutan",
  mas="En Kotlin/JVM puede declararse una función main de nivel superior. La forma habitual `fun main()` no necesita recibir argumentos si el programa no los usa; la sobrecarga con `Array<String>` recibe los argumentos de consola.",
  k=["`fun main()` puede ser el punto de entrada de Kotlin/JVM.", "Una función de nivel superior no necesita pertenecer a una clase escrita por el usuario.", "La sobrecarga main(args: Array<String>) recibe argumentos de consola."],
  sit="Tu programa debe leer los argumentos de consola que entrega la JVM desde su función inicial. ¿Qué firma declaras?",
  cod="""fun main(args: Array<String>) {
    println(args.size)
}""", out="0",
  h="muestra la cantidad de argumentos recibidos al iniciar",
  pr=("La función habitual que inicia un programa Kotlin se llama ___.", "main"),
  pr2=("El tipo de la lista de argumentos del punto de entrada es Array<___>.", "String"),
  ec="creer que main sin parámetros recibe automáticamente los argumentos de consola"),
]
