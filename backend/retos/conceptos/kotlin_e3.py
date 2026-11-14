"""Kotlin · Etapa 3: funciones y colecciones."""
from ..generador import K

LISTA = [
K("Funciones",
  d="bloques reutilizables que pueden llamarse desde otros puntos del programa",
  u="separar una tarea y usarla repetidamente con distintos argumentos",
  mas="Una función puede llamar a otra función, incluso a sí misma. Una función recursiva necesita un caso base que detenga las llamadas para evitar recursión sin fin.",
  k=["Una llamada recursiva invoca la misma función.", "El caso base detiene la recursión.", "Cada llamada conserva sus propios parámetros y variables locales."],
  sit="Una operación se define reduciendo repetidamente un problema hasta alcanzar un caso sencillo. ¿Qué técnica de función puede expresarla?",
  cod="""fun cuenta(n: Int) {
    if (n == 0) return
    print(n)
    cuenta(n - 1)
}
fun main() {
    cuenta(3)
}""", out="321",
  h="cuenta hacia atrás usando una llamada recursiva",
  pr=("Una función que se invoca a sí misma usa la técnica llamada ___.", "recursión", "recursion"),
  pr2=("La condición que detiene una llamada recursiva es el caso ___.", "base"),
  ec="escribir una función recursiva sin un caso base alcanzable"),
K("Colecciones",
  d="abstracciones que agrupan valores y permiten consultarlos o recorrerlos",
  u="manejar conjuntos de datos sin declarar una variable por cada elemento",
  mas="Kotlin ofrece interfaces de colección de solo lectura como `List` y variantes mutables como `MutableList`. Solo lectura describe las operaciones disponibles mediante esa referencia, no garantiza que nadie más pueda cambiar los datos.",
  k=["List representa una colección ordenada con índices.", "MutableList añade operaciones de modificación.", "Una interfaz de solo lectura no garantiza inmutabilidad profunda."],
  sit="Quieres guardar una serie ordenada de puntuaciones y recorrerlas como un solo grupo. ¿Qué abstracción utilizas?",
  cod="""fun main() {
    val puntuaciones = listOf(8, 10, 7)
    println(puntuaciones.size)
}""", out="3",
  h="crea una colección ordenada y muestra cuántos elementos contiene",
  pr=("La abstracción Kotlin para agrupar valores es una ___.", "colección"),
  pr2=("La interfaz mutable de lista se llama ___.", "MutableList"),
  ec="suponer que una referencia List garantiza que nadie pueda cambiar sus datos"),
K("Array",
  d="estructura de tamaño fijo que almacena elementos accesibles por índice",
  u="guardar una cantidad establecida de posiciones y actualizarlas",
  mas="`arrayOf` crea un arreglo genérico y `Array(size) { ... }` inicializa cada posición. Un Array permite reemplazar elementos, pero su tamaño no cambia.",
  k=["Array tiene un tamaño fijo después de crearse.", "Los elementos se consultan mediante índices desde cero.", "`arrayOf` puede inferir un tipo común para los elementos."],
  sit="Debes guardar exactamente tres calificaciones y luego actualizar una posición por índice. ¿Qué estructura eliges?",
  cod="""fun main() {
    val valores = arrayOf(4, 5, 6)
    valores[1] = 9
    println(valores[1])
}""", out="9",
  h="reemplaza el elemento del índice uno de un arreglo",
  pr=("La estructura Kotlin de tamaño fijo accesible por índices es ___.", "Array"),
  pr2=("El primer índice de un Array Kotlin es ___.", "0"),
  ec="intentar agregar un nuevo elemento a un Array ya creado"),
K("List de solo lectura",
  d="interfaz para una secuencia ordenada que expone operaciones de lectura",
  u="representar datos ordenados sin ofrecer modificación desde esa referencia",
  mas="`listOf` crea una lista de solo lectura expuesta como `List`. La interfaz permite consultar el tamaño, acceder por índice y recorrerla; no incluye métodos para añadir o quitar elementos.",
  k=["List conserva el orden de los elementos.", "Los índices de List comienzan en cero.", "`listOf` devuelve una lista de solo lectura."],
  sit="Recibes nombres ordenados que solo debes consultar y no modificar desde esta referencia. ¿Qué interfaz declaras?",
  cod="""fun main() {
    val nombres: List<String> = listOf("Ana", "Leo")
    println(nombres[0])
}""", out="Ana",
  h="consulta el primer elemento de una lista de solo lectura",
  pr=("La interfaz Kotlin de lista de solo lectura se llama ___.", "List"),
  pr2=("La función de fábrica habitual para una lista de solo lectura es ___.", "listOf"),
  ec="llamar add en una referencia cuyo tipo es List"),
K("MutableList",
  d="interfaz de lista ordenada que ofrece operaciones para cambiar su contenido",
  u="añadir, quitar o reemplazar elementos durante la ejecución",
  mas="`mutableListOf` crea una lista mutable. La interfaz incluye métodos como `add`, `remove` y acceso de escritura por índice, manteniendo el orden de los elementos.",
  k=["MutableList permite añadir elementos.", "MutableList conserva el orden.", "`mutableListOf` crea una lista que puede modificarse."],
  sit="Una lista de tareas debe aceptar elementos nuevos durante la ejecución. ¿Qué tipo utilizas?",
  cod="""fun main() {
    val tareas = mutableListOf("leer")
    tareas.add("practicar")
    println(tareas.size)
}""", out="2",
  h="añade una tarea y muestra el tamaño actualizado",
  pr=("La interfaz Kotlin de lista modificable se llama ___.", "MutableList"),
  pr2=("El método que añade un elemento al final de una lista mutable es ___.", "add"),
  ec="usar una lista de solo lectura cuando hace falta añadir elementos"),
K("Set",
  d="colección que no contiene elementos duplicados según su igualdad",
  u="representar valores únicos sin asignarles posiciones por ocurrencia",
  mas="`setOf` construye un conjunto de solo lectura y `mutableSetOf` uno modificable. Un Set no promete un orden de iteración universal, por lo que no debe usarse como sustituto de una lista ordenada.",
  k=["Set elimina duplicados según igualdad.", "Set no ofrece acceso por índice.", "`setOf` crea una vista de solo lectura."],
  sit="Debes registrar etiquetas únicas y evitar almacenar dos veces la misma etiqueta. ¿Qué colección eliges?",
  cod="""fun main() {
    val etiquetas = setOf("azul", "rojo", "azul")
    println(etiquetas.size)
}""", out="2",
  h="crea un conjunto y cuenta solo sus valores únicos",
  pr=("La colección Kotlin que evita elementos duplicados es ___.", "Set"),
  pr2=("Set garantiza acceso por ___ numérico como List.", "índice", "indice"),
  ec="suponer que un Set conserva necesariamente el orden de inserción"),
K("Map",
  d="colección que relaciona claves únicas con valores",
  u="consultar información mediante una clave en lugar de una posición",
  mas="`mapOf` crea un mapa de solo lectura y `mutableMapOf` uno modificable. Una clave aparece una sola vez; una nueva asociación para una clave existente reemplaza su valor.",
  k=["Map relaciona cada clave con un valor.", "Las claves de un Map son únicas.", "`mapOf` crea un mapa de solo lectura."],
  sit="Necesitas consultar el precio de un producto usando su nombre como clave. ¿Qué colección representa esas asociaciones?",
  cod="""fun main() {
    val precios = mapOf("té" to 3, "pan" to 5)
    println(precios["pan"])
}""", out="5",
  h="busca el precio asociado a la clave pan",
  pr=("La colección que asocia claves y valores se llama ___.", "Map"),
  pr2=("En un Map, cada ___ identifica una asociación.", "clave"),
  ec="intentar recuperar una entrada de Map con una posición de lista"),
K("Consulta de Map segura",
  d="acceso con corchetes que devuelve un valor nullable si la clave puede faltar",
  u="buscar una asociación sin asumir que la clave existe",
  mas="La expresión `mapa[clave]` devuelve el valor correspondiente o `null` si no existe. `getValue` también consulta una clave, pero falla si está ausente; el operador `in` permite comprobarla primero.",
  k=["El acceso con corchetes puede devolver null.", "`in` comprueba si el mapa contiene una clave.", "`getValue` lanza una excepción para una clave ausente."],
  sit="Una clave podría no estar en el mapa y quieres manejar ese caso sin excepción. ¿Cómo consultas?",
  cod="""fun main() {
    val edades = mapOf("Sol" to 9)
    val resultado = edades["Nia"] ?: 0
    println(resultado)
}""", out="0",
  h="usa un valor alternativo cuando la clave consultada no existe",
  pr=("El acceso `mapa[clave]` puede devolver ___.", "null"),
  pr2=("El operador para comprobar que una clave pertenece al mapa es ___.", "in"),
  ec="usar getValue sin comprobar una clave que puede faltar"),
K("Pair",
  d="tipo que agrupa dos valores posiblemente de tipos diferentes",
  u="devolver o transportar juntos dos datos relacionados",
  mas="`Pair<A, B>` expone sus componentes como `first` y `second`. El operador `to` crea un Pair y también se usa a menudo para construir asociaciones de mapas.",
  k=["Pair contiene dos componentes.", "Sus propiedades son first y second.", "La expresión `a to b` crea un Pair."],
  sit="Una función debe devolver juntas una etiqueta y su conteo, sin crear una clase propia. ¿Qué tipo estándar usas?",
  cod="""fun main() {
    val dato = "puntos" to 7
    println("${dato.first}:${dato.second}")
}""", out="puntos:7",
  h="agrupa una etiqueta y un número en un Pair",
  pr=("El tipo estándar que agrupa dos valores es ___.", "Pair"),
  pr2=("La propiedad del primer componente de Pair se llama ___.", "first"),
  ec="intercambiar first y second y asumir que Pair asigna significado a sus posiciones"),
K("Desestructuración",
  d="declaración que asigna componentes de un objeto a variables separadas",
  u="extraer campos de Pair, data class u otros tipos compatibles",
  mas="La sintaxis `val (nombre, puntos) = resultado` usa funciones `componentN` para obtener los componentes. Las data class generan estas funciones para sus propiedades del constructor principal.",
  k=["La desestructuración declara varias variables a la vez.", "Se basa en las funciones componentN.", "Las data class generan operadores componentN para propiedades principales."],
  sit="Una función devuelve un Pair y quieres asignar sus dos componentes a nombres locales de una vez. ¿Qué sintaxis usas?",
  cod="""fun main() {
    val (nombre, puntos) = "Mia" to 8
    println("$nombre:$puntos")
}""", out="Mia:8",
  h="separa los dos componentes de un Pair",
  pr=("La sintaxis que extrae componentes en varias variables es la ___.", "desestructuración", "desestructuracion"),
  pr2=("La desestructuración de Kotlin se apoya en funciones component___.", "N"),
  ec="usar una variable adicional sin reconocer que la desestructuración crea nombres locales"),
K("Data class",
  d="clase declarada con data que genera operaciones comunes basadas en el constructor principal",
  u="modelar registros de datos con igualdad por valor y representación útil",
  mas="El compilador genera `equals`, `hashCode`, `toString`, `componentN` y `copy` para las propiedades del constructor principal. Una data class debe tener al menos un parámetro en ese constructor.",
  k=["data class debe declarar al menos un parámetro principal.", "equals y hashCode consideran las propiedades del constructor principal.", "El compilador genera una función copy."],
  sit="Necesitas un tipo de registro con igualdad por contenido y una operación para copiarlo con cambios. ¿Qué declaración eliges?",
  cod="""data class Punto(val x: Int, val y: Int)
fun main() {
    val nuevo = Punto(2, 3).copy(y = 4)
    println(nuevo)
}""", out="Punto(x=2, y=4)",
  h="copia una data class cambiando solo la coordenada y",
  pr=("La declaración Kotlin que genera copy y equals por valor es ___.", "data class"),
  pr2=("La operación generada que copia una data class se llama ___.", "copy"),
  ec="esperar que propiedades fuera del constructor principal participen en equals generado"),
K("Enum class",
  d="tipo que define un conjunto finito de constantes nombradas",
  u="representar opciones cerradas y conocidas de antemano",
  mas="Cada constante enum es una instancia del tipo enum. Las constantes se enumeran con `Enum.entries` en versiones modernas de Kotlin; `values()` también está disponible para interoperabilidad y compatibilidad.",
  k=["Las constantes enum pertenecen a un conjunto finito.", "Cada entrada es una instancia del tipo enum.", "when puede comprobar exhaustivamente las constantes de un enum."],
  sit="El estado de una puerta solo puede ser abierta, cerrada o bloqueada. ¿Qué tipo modela esas opciones cerradas?",
  cod="""enum class Estado { ABIERTA, CERRADA }
fun main() {
    println(Estado.CERRADA.name)
}""", out="CERRADA",
  h="declara estados finitos y muestra el nombre de una constante",
  pr=("El tipo que define constantes de un conjunto finito es enum ___.", "class"),
  pr2=("La propiedad con el nombre de una constante enum es ___.", "name"),
  ec="usar cadenas arbitrarias para un estado que solo admite opciones definidas"),
K("map de colección",
  d="operación que transforma cada elemento y devuelve una nueva lista de resultados",
  u="convertir elementos de una colección sin modificar la original",
  mas="`map` aplica la lambda a cada elemento y conserva la cantidad y el orden del recorrido de origen. El resultado tiene el tipo de la colección de destino, normalmente una List.",
  k=["map aplica una transformación a cada elemento.", "El resultado conserva el orden de la iteración.", "map no modifica la colección original."],
  sit="Quieres convertir una lista de precios en otra lista con cada precio duplicado. ¿Qué operación aplicas?",
  cod="""fun main() {
    val dobles = listOf(2, 4).map { it * 2 }
    println(dobles)
}""", out="[4, 8]",
  h="transforma cada número en su doble",
  pr=("La operación de colección que transforma cada elemento es ___.", "map"),
  pr2=("map devuelve una nueva colección y no modifica la colección ___.", "original"),
  ec="usar map con una lambda que no devuelve el resultado transformado"),
K("filter de colección",
  d="operación que conserva los elementos que satisfacen un predicado",
  u="seleccionar valores sin cambiar la colección de origen",
  mas="`filter` recibe una condición que debe devolver Boolean para cada elemento. El resultado contiene solo los elementos cuyo predicado fue verdadero.",
  k=["filter conserva elementos que pasan su predicado.", "La lambda de filter devuelve Boolean.", "filter no modifica la colección original."],
  sit="De una lista de números quieres crear otra con solo los valores pares. ¿Qué operación usas?",
  cod="""fun main() {
    val pares = listOf(1, 2, 4, 5).filter { it % 2 == 0 }
    println(pares)
}""", out="[2, 4]",
  h="conserva los elementos pares de la lista",
  pr=("La operación que selecciona elementos mediante un predicado es ___.", "filter"),
  pr2=("La condición de filter debe devolver un valor ___.", "Boolean"),
  ec="devolver un valor que no sea Boolean desde el predicado de filter"),
K("fold",
  d="operación que combina elementos en un único acumulador desde un valor inicial",
  u="calcular agregados personalizados en un recorrido",
  mas="`fold(inicial) { acumulado, elemento -> ... }` visita los elementos de la colección y actualiza el acumulador. El resultado tiene el tipo del acumulador, que puede diferir del tipo de los elementos.",
  k=["fold requiere un valor inicial.", "La lambda recibe el acumulador y el elemento actual.", "El resultado final es el acumulador tras recorrer los elementos."],
  sit="Quieres calcular la suma empezando desde un total conocido y combinando cada elemento en orden. ¿Qué operación usas?",
  cod="""fun main() {
    val total = listOf(2, 3, 4).fold(0) { suma, n -> suma + n }
    println(total)
}""", out="9",
  h="acumula la suma de una lista desde cero",
  pr=("La operación que reduce una colección desde un acumulador inicial es ___.", "fold"),
  pr2=("El primer argumento de fold proporciona el valor ___.", "inicial"),
  ec="olvidar que el acumulador debe tener un valor inicial"),
K("sortedBy",
  d="operación que devuelve los elementos ordenados según una clave seleccionada",
  u="obtener una nueva colección ordenada por una propiedad",
  mas="`sortedBy` recibe un selector de clave comparable y devuelve una lista ordenada ascendentemente. La operación no reordena la colección original.",
  k=["sortedBy ordena usando una clave calculada por el selector.", "La ordenación resultante es ascendente.", "sortedBy devuelve una lista nueva."],
  sit="Debes ordenar palabras alfabéticamente según su longitud sin reordenar la lista original. ¿Qué operación eliges?",
  cod="""fun main() {
    val ordenadas = listOf("kiwi", "sol", "luna").sortedBy { it.length }
    println(ordenadas)
}""", out="[sol, kiwi, luna]",
  h="ordena las palabras por longitud ascendente",
  pr=("La operación de ordenación por clave se llama ___.", "sortedBy"),
  pr2=("sortedBy devuelve los elementos en orden ___.", "ascendente"),
  ec="esperar que sortedBy modifique en el lugar la lista de origen"),
K("any y all",
  d="operaciones que comprueban si algún elemento o todos satisfacen un predicado",
  u="expresar condiciones sobre los elementos de una colección",
  mas="`any` devuelve verdadero si al menos un elemento cumple el predicado; `all` requiere que todos lo cumplan. En una colección vacía, any devuelve false y all devuelve true.",
  k=["any busca al menos una coincidencia.", "all exige que cada elemento cumpla el predicado.", "Para una colección vacía, any es false y all es true."],
  sit="Necesitas saber si al menos una puntuación supera diez, sin filtrar ni contar. ¿Qué operación consultas?",
  cod="""fun main() {
    val hayAprobado = listOf(4, 12, 8).any { it >= 10 }
    println(hayAprobado)
}""", out="true",
  h="comprueba si alguna puntuación alcanza diez",
  pr=("La operación que comprueba si al menos un elemento cumple es ___.", "any"),
  pr2=("La operación que exige que todos cumplan se llama ___.", "all"),
  ec="usar all cuando basta con que una sola entrada cumpla la condición"),
K("groupBy",
  d="operación que agrupa elementos bajo claves calculadas a partir de ellos",
  u="organizar una colección en grupos por una característica común",
  mas="`groupBy` recibe una función que produce una clave para cada elemento. El resultado es un mapa entre cada clave y la lista de elementos que la comparten.",
  k=["groupBy crea un mapa de claves a listas.", "La lambda determina la clave del grupo.", "Cada elemento aparece en el grupo de su clave calculada."],
  sit="Quieres organizar palabras según su primera letra y consultar luego cada grupo. ¿Qué operación aplicas?",
  cod="""fun main() {
    val grupos = listOf("sol", "sal", "mar").groupBy { it.first() }
    println(grupos['s'])
}""", out="[sol, sal]",
  h="agrupa palabras por primera letra y consulta el grupo s",
  pr=("La operación que agrupa elementos por una clave calculada es ___.", "groupBy"),
  pr2=("groupBy devuelve un mapa cuyos valores son listas de ___.", "elementos"),
  ec="suponer que groupBy devuelve una lista plana en vez de un mapa"),
K("Sequence",
  d="interfaz para procesar elementos de forma perezosa en una canalización",
  u="encadenar operaciones y evitar colecciones intermedias innecesarias",
  mas="Las operaciones intermedias de una Sequence son perezosas y se ejecutan al solicitar un resultado terminal. Convertir una colección con `asSequence()` no cambia por sí solo sus valores.",
  k=["Las transformaciones intermedias de Sequence son perezosas.", "Una operación terminal dispara el recorrido.", "asSequence crea una vista de procesamiento secuencial."],
  sit="Una colección grande pasa por transformaciones encadenadas y solo necesitas el primer resultado. ¿Qué procesamiento perezoso puedes usar?",
  cod="""fun main() {
    val primero = sequenceOf(1, 2, 3).map { it * 2 }.first()
    println(primero)
}""", out="2",
  h="transforma perezosamente los valores y toma el primero",
  pr=("La abstracción Kotlin de procesamiento perezoso es ___.", "Sequence"),
  pr2=("Una operación terminal hace que una Sequence comience el ___.", "recorrido"),
  ec="esperar que map de Sequence se ejecute antes de una operación terminal"),
K("buildList",
  d="función que construye una List usando un bloque con un MutableList receptor",
  u="crear una lista paso a paso y exponer el resultado como solo lectura",
  mas="Dentro del bloque de `buildList`, `add` modifica el receptor de construcción. Al terminar, el resultado se expone como List; el bloque evita publicar la referencia mutable usada durante la construcción.",
  k=["buildList entrega una List como resultado.", "El bloque receptor permite añadir elementos.", "El receptor mutable de construcción no se devuelve como MutableList."],
  sit="Quieres construir una lista condicionalmente con add y luego compartir el resultado como colección de solo lectura. ¿Qué función usas?",
  cod="""fun main() {
    val numeros = buildList {
        add(2)
        add(4)
    }
    println(numeros)
}""", out="[2, 4]",
  h="construye una lista agregando elementos dentro del bloque",
  pr=("La función de construcción de listas con bloque receptor es ___.", "buildList"),
  pr2=("El bloque de buildList permite agregar elementos con ___.", "add"),
  ec="esperar que buildList devuelva el MutableList de construcción"),
]
