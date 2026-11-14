"""Kotlin · Etapa 5: técnicas avanzadas y herramientas."""
from ..generador import K

LISTA = [
K("Avanzado",
  d="uso de características del lenguaje para crear abstracciones reutilizables y precisas",
  u="resolver problemas de tipos y diseño más allá de la sintaxis básica",
  mas="Kotlin combina inferencia de tipos con un sistema estático, funciones como valores y abstracciones genéricas. Las características avanzadas permiten expresar restricciones y reutilizar implementaciones sin perder comprobaciones de compilación.",
  k=["Kotlin ofrece genéricos con parámetros de tipo.", "Las funciones pueden recibirse como valores.", "El compilador comprueba restricciones de tipos estáticamente."],
  sit="Necesitas diseñar una solución reutilizable con tipos comprobados en compilación, en vez de copiar código para cada tipo de dato. ¿Qué enfoque de lenguaje aplicas?",
  cod="""fun <T> primero(elementos: List<T>): T = elementos[0]
fun main() {
    println(primero(listOf("K", "J")))
}""", out="K",
  h="usa una función genérica para recuperar el primer elemento",
  pr=("El término que describe características más allá de los fundamentos es ___.", "avanzado"),
  pr2=("El mecanismo Kotlin que parametriza una declaración con tipos es ___.", "genéricos", "genericos"),
  ec="usar abstracciones avanzadas sin comprobar sus restricciones de tipo"),
K("Herramientas",
  d="programas y configuraciones que compilan, prueban y empaquetan proyectos Kotlin",
  u="automatizar tareas repetibles del desarrollo y la construcción",
  mas="El compilador `kotlinc` compila Kotlin y Gradle automatiza tareas de construcción mediante archivos como `build.gradle.kts`. El Gradle Wrapper del proyecto fija una versión de Gradle para que el equipo use una herramienta coherente.",
  k=["kotlinc es el compilador de Kotlin.", "Gradle automatiza tareas de construcción.", "El Gradle Wrapper fija la versión de Gradle usada por el proyecto."],
  sit="Un equipo necesita que todas las computadoras ejecuten la misma versión de Gradle al construir el proyecto. ¿Qué herramienta distribuye?",
  cod="""fun main() {
    val herramienta = "Gradle Wrapper"
    println("Usar $herramienta")
}""", out="Usar Gradle Wrapper",
  h="muestra la herramienta que fija Gradle para el proyecto",
  pr=("El compilador de Kotlin se llama ___.", "kotlinc"),
  pr2=("El archivo de configuración Kotlin DSL de Gradle suele llamarse build.gradle.___.", "kts"),
  ec="depender de una versión de Gradle instalada localmente y distinta a la del proyecto"),
K("Función genérica",
  d="función con un parámetro de tipo que puede operar sobre varios tipos compatibles",
  u="reutilizar lógica manteniendo seguridad de tipos",
  mas="El parámetro de tipo se declara entre `< >` antes del nombre o los parámetros de la función. El compilador suele inferirlo desde los argumentos de llamada.",
  k=["Un parámetro de tipo de función se declara entre < y >.", "El tipo genérico conserva información estática.", "Kotlin puede inferir el parámetro de tipo en una llamada."],
  sit="Una función devuelve el elemento inicial sin importar si la lista contiene texto o números. ¿Qué función defines?",
  cod="""fun <T> primero(lista: List<T>): T = lista[0]
fun main() {
    println(primero(listOf(6, 8)))
}""", out="6",
  h="invoca una función genérica con una lista de enteros",
  pr=("La función que declara un parámetro de tipo usa un genérico ___.", "T"),
  pr2=("Los parámetros de tipo se escriben entre signos ___ y >.", "<"),
  ec="reemplazar un parámetro genérico por Any y perder el tipo específico"),
K("Restricción de tipo",
  d="límite declarado que exige que un parámetro genérico cumpla una condición de tipo",
  u="usar operaciones de una interfaz o clase base en valores genéricos",
  mas="Una restricción simple se escribe con `T : Comparable<T>`. Para múltiples restricciones se usa una cláusula `where`, que permite requerir varios tipos base o interfaces.",
  k=["La forma T : Tipo establece una restricción superior.", "where permite declarar restricciones adicionales.", "El compilador impide usar tipos que no satisfacen la restricción."],
  sit="Una función genérica necesita comparar sus valores y solo debe aceptar tipos comparables. ¿Qué declaras?",
  cod="""fun <T : Comparable<T>> mayor(a: T, b: T) = if (a >= b) a else b
fun main() {
    println(mayor(3, 5))
}""", out="5",
  h="compara dos valores respetando una restricción genérica",
  pr=("La declaración T : Comparable<T> establece una restricción de tipo ___.", "superior"),
  pr2=("La palabra clave que añade restricciones genéricas adicionales es ___.", "where"),
  ec="usar una operación en T sin declarar que todos los tipos T la soportan"),
K("Variancia out",
  d="declaración de variancia que permite producir T y usar subtipado covariante",
  u="aceptar productores de un tipo específico donde se espera un tipo más general",
  mas="`interface Fuente<out T>` marca T como covariante porque solo se produce. Si Perro es subtipo de Animal, una Fuente<Perro> puede usarse como Fuente<Animal>.",
  k=["out permite covariancia del parámetro de tipo.", "Un T covariante se usa en posiciones de salida.", "List de Kotlin declara su elemento como covariante."],
  sit="Una fuente que produce Perro debe poder usarse cuando el código acepta una fuente de Animal. ¿Qué variancia declaras?",
  cod="""open class Animal
class Perro : Animal()
interface Fuente<out T> { fun obtener(): T }
class Mascota : Fuente<Perro> { override fun obtener() = Perro() }
fun main() {
    val fuente: Fuente<Animal> = Mascota()
    println(fuente.obtener() is Perro)
}""", out="true",
  h="asigna un productor de Perro a una referencia de productor de Animal",
  pr=("La palabra clave que declara covariancia en Kotlin es ___.", "out"),
  pr2=("Un parámetro out se usa como productor, es decir, en posición de ___.", "salida"),
  ec="usar un parámetro out como argumento de entrada del productor"),
K("Variancia in",
  d="declaración de variancia que permite contravariancia para un parámetro consumidor",
  u="pasar un consumidor general donde se requiere uno de un subtipo",
  mas="`interface Receptor<in T>` acepta T como entrada y declara variancia contravariante. Un receptor de Animal puede procesar Perro, por lo que puede usarse donde se necesita un Receptor<Perro>.",
  k=["in declara contravariancia.", "Un parámetro in se consume como entrada.", "Un consumidor de un tipo base puede aceptar valores de un subtipo."],
  sit="Una operación que acepta cualquier Animal debe servir donde se solicita una operación que acepte Perro. ¿Qué variancia aplicas?",
  cod="""open class Animal
class Perro : Animal()
interface Receptor<in T> { fun aceptar(valor: T) }
class Impresor : Receptor<Animal> {
    override fun aceptar(valor: Animal) {}
}
fun main() {
    val receptor: Receptor<Perro> = Impresor()
    receptor.aceptar(Perro())
    println("aceptado")
}""", out="aceptado",
  h="usa un consumidor de Animal donde se solicita uno de Perro",
  pr=("La palabra clave para declarar contravariancia es ___.", "in"),
  pr2=("Un parámetro in se usa en posición de ___.", "entrada"),
  ec="declarar in en un tipo que devuelve el parámetro como resultado"),
K("Proyección estrella",
  d="uso de * para expresar un tipo genérico cuyo argumento exacto se desconoce",
  u="aceptar valores genéricos sin depender de un parámetro de tipo concreto",
  mas="`List<*>` significa una lista de algún tipo desconocido. Se pueden leer sus elementos con tipo seguro `Any?`, pero no añadir un valor arbitrario porque el tipo real de la lista no está especificado.",
  k=["El asterisco representa un argumento de tipo desconocido.", "List<*> permite leer elementos como Any?.", "No se puede añadir un valor arbitrario a una MutableList<*>."],
  sit="Una función solo inspecciona el tamaño de cualquier lista y no necesita conocer su tipo de elemento. ¿Qué tipo usa?",
  cod="""fun cantidad(datos: List<*>) = datos.size
fun main() {
    println(cantidad(listOf("a", 2, true)))
}""", out="3",
  h="recibe una lista cuyo tipo de elemento se desconoce",
  pr=("El símbolo que expresa un argumento genérico desconocido es ___.", "*"),
  pr2=("El tipo seguro de lectura de un elemento de List<*> es ___.", "Any?"),
  ec="añadir un valor a MutableList<*> sin conocer su tipo real"),
K("Parámetro reified",
  d="parámetro de tipo inline cuyo tipo concreto puede consultarse dentro de la función",
  u="realizar comprobaciones de tipo sin pasar una referencia Class explícita",
  mas="Los genéricos JVM normalmente se borran en tiempo de ejecución. Una función `inline` con `reified T` puede usar operaciones como `value is T` porque el compilador sustituye el tipo en los puntos de llamada.",
  k=["reified solo se permite para parámetros de tipo de funciones inline.", "reified permite comprobar el tipo concreto con is.", "El reified evita el borrado de tipo dentro de esa función inline."],
  sit="Una función genérica necesita comprobar si un valor es del tipo concreto solicitado, sin recibir una clase como argumento. ¿Qué parámetro declaras?",
  cod="""inline fun <reified T> coincide(valor: Any) = valor is T
fun main() {
    println(coincide<String>("K"))
}""", out="true",
  h="comprueba el tipo concreto mediante un parámetro reified",
  pr=("El modificador que conserva el tipo concreto de un parámetro inline es ___.", "reified"),
  pr2=("Un parámetro reified requiere que la función sea ___.", "inline"),
  ec="intentar usar reified en una clase o función que no es inline"),
K("typealias",
  d="declaración que da un nombre alternativo a un tipo existente",
  u="hacer más legibles firmas con tipos extensos",
  mas="`typealias Texto = String` introduce un nombre alternativo para el mismo tipo. No crea un tipo nuevo ni evita que Texto y String sean intercambiables.",
  k=["typealias crea un alias, no un tipo distinto.", "El alias puede simplificar tipos funcionales largos.", "El compilador trata el alias como el tipo subyacente."],
  sit="Una firma repite una función con muchos parámetros y quieres abreviarla sin crear un tipo nuevo. ¿Qué declaras?",
  cod="""typealias Operacion = (Int, Int) -> Int
fun main() {
    val sumar: Operacion = { a, b -> a + b }
    println(sumar(2, 4))
}""", out="6",
  h="usa un alias para declarar una función de suma",
  pr=("La declaración que da un nombre alternativo a un tipo es ___.", "typealias"),
  pr2=("typealias crea un tipo nuevo distinto del tipo ___?", "subyacente"),
  ec="suponer que typealias impide intercambiar el alias y su tipo original"),
K("Value class",
  d="clase de valor inline que envuelve una única propiedad para aportar identidad de tipo",
  u="evitar mezclar valores primitivos con significados distintos",
  mas="Una `value class` se declara con `@JvmInline` y debe tener una única propiedad principal marcada `val`. El compilador puede representarla como su valor subyacente en muchos contextos, aunque el boxing puede ocurrir en otros.",
  k=["Una value class tiene exactamente una propiedad principal.", "En JVM se marca con @JvmInline.", "Su tipo permite distinguir semánticamente el valor subyacente."],
  sit="Un identificador y una cantidad usan ambos Int, pero quieres que el compilador evite intercambiarlos accidentalmente. ¿Qué tipo defines?",
  cod="""@JvmInline
value class UsuarioId(val valor: Int)
fun main() {
    println(UsuarioId(12).valor)
}""", out="12",
  h="envuelve un entero en un tipo dedicado de identificador",
  pr=("El tipo Kotlin que envuelve un valor con identidad de dominio es value ___.", "class"),
  pr2=("La anotación JVM requerida para una value class es ___.", "@JvmInline"),
  ec="declarar más de una propiedad en el constructor principal de una value class"),
K("Sobrecarga de operador",
  d="definición de una función miembro o extensión con operator para un símbolo del lenguaje",
  u="dar semántica apropiada a operadores para un tipo propio",
  mas="La palabra clave `operator` habilita nombres convencionales como `plus` para expresiones con `+`. Kotlin exige firmas concretas y no permite inventar símbolos arbitrarios.",
  k=["La función plus puede habilitar el operador +.", "La función debe declararse con operator.", "La sobrecarga no cambia la precedencia definida por el lenguaje."],
  sit="Dos vectores propios deben poder sumarse con + siguiendo una regla definida por el tipo. ¿Qué característica implementas?",
  cod="""data class Vector(val x: Int) {
    operator fun plus(otro: Vector) = Vector(x + otro.x)
}
fun main() {
    println((Vector(2) + Vector(3)).x)
}""", out="5",
  h="define la suma de dos vectores mediante plus",
  pr=("La función convencional que implementa el operador + es ___.", "plus"),
  pr2=("Una función debe llevar operator para participar en la sobrecarga de ___.", "operadores"),
  ec="declarar una función plus sin operator y esperar que acepte el símbolo +"),
K("Función infix",
  d="función de un solo parámetro marcada infix que puede llamarse sin punto ni paréntesis",
  u="expresar operaciones binarias con una notación legible",
  mas="Una función infix debe ser miembro o extensión y tener un solo parámetro. La notación infix tiene menor precedencia que los operadores aritméticos y las conversiones de tipo.",
  k=["La función infix se declara con la palabra clave infix.", "Debe recibir exactamente un parámetro.", "Puede ser miembro o función de extensión."],
  sit="Una relación binaria entre dos valores debe poder escribirse como `a contiene b` en vez de con punto y paréntesis. ¿Qué forma de función declaras?",
  cod="""infix fun Int.veces(n: Int) = this * n
fun main() {
    println(3 veces 4)
}""", out="12",
  h="llama una extensión infix para multiplicar dos enteros",
  pr=("La palabra clave para permitir una llamada binaria sin punto es ___.", "infix"),
  pr2=("Una función infix debe tener exactamente ___ parámetro.", "un"),
  ec="marcar infix una función que tiene dos parámetros"),
K("tailrec",
  d="modificador que permite optimizar una llamada recursiva final compatible",
  u="escribir recursión de cola con oportunidad de evitar crecimiento de pila",
  mas="Una llamada recursiva es de cola cuando es la última operación de la función. `tailrec` solicita al compilador optimizar esa forma cuando se cumplen las restricciones; una recursión no compatible no recibe esa optimización.",
  k=["tailrec se aplica a una función recursiva compatible.", "La llamada recursiva debe ser la última operación.", "La optimización evita acumular marcos de llamada en cada iteración."],
  sit="Una cuenta regresiva recursiva vuelve a llamarse al final y debe optimizarse como un ciclo cuando es posible. ¿Qué modificador indicas?",
  cod="""tailrec fun suma(n: Int, total: Int = 0): Int =
    if (n == 0) total else suma(n - 1, total + n)
fun main() {
    println(suma(4))
}""", out="10",
  h="suma de forma recursiva de cola con un acumulador",
  pr=("El modificador de recursión de cola en Kotlin es ___.", "tailrec"),
  pr2=("La llamada recursiva optimizable debe ser la última ___ de la función.", "operación"),
  ec="poner trabajo después de la llamada recursiva e impedir la forma de cola"),
K("Delegado lazy",
  d="delegado de propiedad que calcula y almacena el valor al primer acceso",
  u="posponer un cálculo hasta que el valor se necesite",
  mas="`by lazy { ... }` crea una propiedad de solo lectura inicializada en el primer acceso. La implementación estándar sincroniza la inicialización de forma predeterminada en JVM.",
  k=["lazy calcula el valor en el primer acceso.", "El resultado se reutiliza en accesos siguientes.", "La inicialización estándar es segura para hilos."],
  sit="Un valor costoso no se necesita en todas las ejecuciones y solo debe calcularse cuando alguien lo consulta. ¿Qué delegado eliges?",
  cod="""fun main() {
    val etiqueta by lazy { "lista" }
    println(etiqueta)
}""", out="lista",
  h="inicializa la propiedad al consultar su valor",
  pr=("El delegado de inicialización diferida se llama ___.", "lazy"),
  pr2=("Una propiedad delegada se introduce en la declaración con ___.", "by"),
  ec="suponer que una propiedad lazy se calcula al crear su objeto"),
K("Delegación de interfaz",
  d="mecanismo by que reenvía a otro objeto la implementación de una interfaz",
  u="componer comportamiento sin repetir cada método delegado",
  mas="Una clase puede implementar una interfaz delegando explícitamente en una propiedad mediante `: Interfaz by delegado`. La clase todavía puede sobrescribir miembros y personalizar el comportamiento.",
  k=["La sintaxis de delegación de interfaz usa by.", "El objeto delegado implementa la interfaz.", "La clase delegante puede sobrescribir miembros reenviados."],
  sit="Una clase envolvente debe implementar una interfaz reutilizando otro objeto que ya la implementa. ¿Qué mecanismo declaras?",
  cod="""interface Fuente { fun valor(): Int }
class Fija : Fuente { override fun valor() = 9 }
class Envolvente(fuente: Fuente) : Fuente by fuente
fun main() {
    println(Envolvente(Fija()).valor())
}""", out="9",
  h="delega la implementación de Fuente a otro objeto",
  pr=("El mecanismo que reenvía miembros de una interfaz se declara con ___.", "by"),
  pr2=("El objeto que proporciona los miembros reenviados es el ___.", "delegado"),
  ec="olvidar que el objeto delegado debe implementar la interfaz declarada"),
K("Conversión SAM",
  d="conversión automática de una lambda a una interfaz funcional de un solo método abstracto",
  u="usar lambdas con interfaces Java funcionales",
  mas="Kotlin permite convertir una lambda a una interfaz SAM de Java, como `Runnable`. La lambda implementa el único método abstracto y puede invocarse directamente sin iniciar un hilo.",
  k=["Una interfaz SAM tiene un solo método abstracto.", "Una lambda puede convertirse a Runnable.", "Llamar Runnable.run ejecuta la acción en el hilo actual."],
  sit="Una API Java recibe una interfaz con un solo método abstracto y quieres proporcionarle una lambda. ¿Qué conversión usa Kotlin?",
  cod="""fun main() {
    val accion = Runnable { println("hecho") }
    accion.run()
}""", out="hecho",
  h="convierte una lambda a Runnable y la ejecuta directamente",
  pr=("La conversión de lambda para interfaz de método único se llama ___.", "SAM"),
  pr2=("La interfaz Java estándar implementada en el ejemplo es ___.", "Runnable"),
  ec="suponer que Runnable.run crea un hilo nuevo automáticamente"),
K("Anotación",
  d="metadato declarativo aplicado a una clase, propiedad o función",
  u="aportar información a compiladores, herramientas o tiempo de ejecución",
  mas="Una anotación se declara con `annotation class` y se aplica con `@Nombre`. El efecto depende de la anotación y de la herramienta o biblioteca que la procese.",
  k=["Una anotación se aplica con el prefijo @.", "annotation class declara una anotación propia.", "Una anotación no cambia por sí sola el comportamiento si nadie la procesa."],
  sit="Una herramienta debe reconocer una marca en una función para generar o validar comportamiento adicional. ¿Qué metadato puedes aplicar?",
  cod="""annotation class Revisar
@Revisar
fun dato() = 5
fun main() {
    println(dato())
}""", out="5",
  h="declara una anotación y la aplica a una función",
  pr=("El metadato declarativo aplicado con @ se llama ___.", "anotación", "anotacion"),
  pr2=("Una anotación propia se declara con annotation ___.", "class"),
  ec="creer que una anotación personalizada tiene efecto automático sin un procesador"),
K("apply",
  d="función de alcance que ejecuta un bloque con el receptor como this y devuelve ese receptor",
  u="configurar un objeto y continuar usando el mismo objeto",
  mas="En `objeto.apply { ... }`, el bloque se ejecuta con el objeto como receptor implícito. El resultado de apply es el objeto original, no el valor de la última expresión del bloque.",
  k=["apply usa el objeto como this dentro del bloque.", "apply devuelve el receptor original.", "apply puede encadenarse durante la configuración."],
  sit="Debes configurar varias propiedades de un objeto recién creado y luego conservar esa misma instancia. ¿Qué función de alcance usas?",
  cod="""data class Caja(var ancho: Int)
fun main() {
    val caja = Caja(1).apply { ancho = 4 }
    println(caja.ancho)
}""", out="4",
  h="configura una caja y devuelve la misma instancia",
  pr=("La función de alcance que devuelve el receptor es ___.", "apply"),
  pr2=("Dentro del bloque de apply, el objeto es el receptor implícito llamado ___.", "this"),
  ec="esperar que apply devuelva el resultado de la última línea del bloque"),
K("let",
  d="función de alcance que pasa el receptor como it y devuelve el resultado del bloque",
  u="transformar un valor o encadenar una operación que produce otro resultado",
  mas="`valor.let { ... }` pasa el receptor como argumento del bloque, normalmente nombrado `it`. El valor que devuelve let es el resultado de la última expresión del bloque.",
  k=["let recibe el receptor como it si no se da nombre.", "let devuelve el resultado del bloque.", "let puede combinarse con una llamada segura para un valor nullable."],
  sit="Un valor debe transformarse a una representación distinta usando su lambda como argumento con nombre implícito. ¿Qué función de alcance aplicas?",
  cod="""fun main() {
    val longitud = "Kotlin".let { it.length }
    println(longitud)
}""", out="6",
  h="transforma una cadena en el resultado de su longitud",
  pr=("La función de alcance que suele recibir el valor como it es ___.", "let"),
  pr2=("let devuelve el resultado del bloque, no el receptor ___?", "original"),
  ec="esperar que let devuelva siempre el mismo objeto que recibió"),
K("runCatching",
  d="función estándar que ejecuta un bloque y captura excepciones en un Result",
  u="expresar un cálculo que puede fallar sin propagar inmediatamente su excepción",
  mas="`runCatching { ... }` devuelve `Result<T>`, exitoso o fallido, y captura cualquier Throwable. Como eso incluye errores que normalmente no conviene tratar como recuperables, úsalo con cuidado; se puede consultar el resultado con `getOrDefault`.",
  k=["runCatching envuelve el resultado en Result.", "El bloque captura objetos Throwable y los guarda como fallo.", "getOrDefault devuelve una alternativa para el caso fallido."],
  sit="Una conversión puede lanzar una excepción y quieres obtener un resultado consultable con un valor de reserva. ¿Qué función estándar usas?",
  cod="""fun main() {
    val resultado = runCatching { "x".toInt() }
    println(resultado.getOrDefault(0))
}""", out="0",
  h="captura el fallo de conversión y usa cero como alternativa",
  pr=("La función estándar que captura el resultado de un bloque es ___.", "runCatching"),
  pr2=("runCatching representa su resultado con el tipo ___.", "Result"),
  ec="suponer que runCatching convierte automáticamente un fallo en un valor exitoso"),
]
