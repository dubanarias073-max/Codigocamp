"""Kotlin · Etapa 4: clases y seguridad frente a nulos."""
from ..generador import K

LISTA = [
K("Clases",
  d="declaraciones que definen un tipo con estado y comportamiento",
  u="modelar entidades propias y crear instancias con propiedades",
  mas="Una clase agrupa datos y funciones relacionadas. Se crea una instancia llamando al nombre de la clase con los argumentos requeridos por su constructor.",
  k=["class declara un tipo definido por el usuario.", "Una instancia se crea mediante una llamada al constructor.", "Una clase puede declarar propiedades y funciones miembro."],
  sit="Necesitas representar una lámpara con estado y una acción para encenderla. ¿Qué estructura defines?",
  cod="""class Lampara(val encendida: Boolean)
fun main() {
    println(Lampara(true).encendida)
}""", out="true",
  h="crea una instancia y consulta una propiedad",
  pr=("La declaración que define un tipo propio en Kotlin es una ___.", "clase"),
  pr2=("El valor concreto creado a partir de una clase es una ___.", "instancia"),
  ec="confundir el nombre de la clase con una instancia ya creada"),
K("Nulos",
  d="valores ausentes que Kotlin controla mediante tipos nullable explícitos",
  u="representar datos que pueden no estar disponibles y tratarlos con seguridad",
  mas="Un tipo como `String?` admite una cadena o null, mientras que `String` no admite null. El sistema de tipos exige manejar la posibilidad de ausencia antes de usar ese valor.",
  k=["El sufijo ? hace nullable un tipo.", "String no admite null por defecto.", "El compilador comprueba usos de valores nullable."],
  sit="Un perfil puede no tener segundo nombre y quieres modelar explícitamente esa ausencia. ¿Qué característica de tipos usas?",
  cod="""fun main() {
    val segundoNombre: String? = null
    println(segundoNombre == null)
}""", out="true",
  h="declara una cadena nullable y comprueba su ausencia",
  pr=("El sufijo que permite null en un tipo Kotlin es ___.", "?"),
  pr2=("El tipo String sin sufijo no admite el valor ___.", "null"),
  ec="asumir que cualquier referencia Kotlin puede contener null"),
K("Constructor principal",
  d="parte de la declaración de clase que recibe los valores iniciales de la instancia",
  u="inicializar propiedades necesarias al crear un objeto",
  mas="Los parámetros del constructor principal se escriben después del nombre de la clase. Si llevan `val` o `var`, también declaran propiedades; de lo contrario solo están disponibles durante la inicialización.",
  k=["El constructor principal aparece en la cabecera de la clase.", "Un parámetro con val se convierte en propiedad de solo lectura.", "Un parámetro sin val o var no es una propiedad pública de instancia."],
  sit="Cada objeto de una clase debe recibir un identificador al crearse y conservarlo como propiedad. ¿Dónde lo declaras?",
  cod="""class Usuario(val id: Int)
fun main() {
    println(Usuario(42).id)
}""", out="42",
  h="inicializa y consulta un identificador declarado en el constructor",
  pr=("El constructor escrito en la cabecera de clase es el constructor ___.", "principal"),
  pr2=("El modificador que convierte un parámetro principal en propiedad no reasignable es ___.", "val"),
  ec="omitir val y luego intentar acceder al parámetro como propiedad"),
K("Propiedad",
  d="miembro con nombre que expone un valor y puede tener acceso de lectura o escritura",
  u="representar estado encapsulado de un objeto",
  mas="Una propiedad declarada con `val` es de solo lectura y una con `var` tiene un setter. Las propiedades pueden definir getters o setters personalizados sin exponer campos directamente.",
  k=["val declara una propiedad sin setter.", "var permite definir un setter.", "Una propiedad no equivale necesariamente a un campo público."],
  sit="Una cuenta debe exponer su saldo actual, pero impedir que otros lo reasignen directamente. ¿Qué miembro declaras?",
  cod="""class Cuenta(val saldo: Int)
fun main() {
    println(Cuenta(30).saldo)
}""", out="30",
  h="expone el saldo mediante una propiedad de solo lectura",
  pr=("El miembro Kotlin que representa un valor con acceso es una ___.", "propiedad"),
  pr2=("La palabra clave de una propiedad reasignable es ___.", "var"),
  ec="tratar toda propiedad como si fuera un campo mutable público"),
K("Bloque init",
  d="bloque de inicialización que se ejecuta durante la creación de cada instancia",
  u="validar o preparar datos del constructor principal",
  mas="Un bloque `init` se ejecuta durante la inicialización de una instancia, en el orden en que aparece respecto de otras propiedades y bloques init. Puede acceder a los parámetros del constructor principal.",
  k=["Cada bloque init corre al crear una instancia.", "Los bloques init se ejecutan según su orden en el cuerpo de clase.", "init puede validar parámetros del constructor."],
  sit="Al crear un objeto debes comprobar inmediatamente que su código no esté vacío. ¿Qué bloque de clase utilizas?",
  cod="""class Codigo(val texto: String) {
    init { require(texto.isNotEmpty()) }
}
fun main() {
    println(Codigo("A7").texto)
}""", out="A7",
  h="valida un código durante la inicialización de la instancia",
  pr=("El bloque de clase ejecutado al inicializar una instancia es ___.", "init"),
  pr2=("La función estándar que verifica una condición de argumento es ___.", "require"),
  ec="poner validación en un bloque que nunca se ejecuta al crear la instancia"),
K("Función miembro",
  d="función declarada dentro de una clase que puede operar sobre la instancia",
  u="agrupar comportamiento relacionado con los datos del objeto",
  mas="Una función miembro se llama usando una instancia y puede acceder a sus propiedades. En una instancia, `this` refiere al receptor actual y a menudo se puede omitir.",
  k=["Una función miembro pertenece a la declaración de una clase.", "Puede leer propiedades de la instancia.", "this identifica el receptor actual."],
  sit="Un círculo debe calcular su diámetro a partir del radio que guarda. ¿Dónde declaras ese comportamiento?",
  cod="""class Circulo(val radio: Int) {
    fun diametro() = radio * 2
}
fun main() {
    println(Circulo(5).diametro())
}""", out="10",
  h="calcula el diámetro usando la propiedad de la instancia",
  pr=("La función declarada dentro de una clase es una función ___.", "miembro"),
  pr2=("La referencia explícita al objeto receptor actual es ___.", "this"),
  ec="llamar una función miembro sin usar una instancia cuando no es estática"),
K("Visibilidad",
  d="control de acceso que determina desde dónde se puede usar una declaración",
  u="exponer solo la API necesaria y ocultar detalles internos",
  mas="Los modificadores incluyen `public`, `private`, `protected` e `internal`. Por defecto, las declaraciones Kotlin son públicas; `internal` restringe el acceso al mismo módulo.",
  k=["La visibilidad predeterminada de Kotlin es public.", "private limita el acceso según el ámbito declarado.", "internal permite acceso dentro del mismo módulo."],
  sit="Un auxiliar de implementación solo debe usarse dentro de su clase. ¿Qué visibilidad le das?",
  cod="""class Caja {
    private val clave = "X"
    fun etiqueta() = clave
}
fun main() {
    println(Caja().etiqueta())
}""", out="X",
  h="mantiene privada la clave y la expone por un método",
  pr=("El modificador de acceso predeterminado en Kotlin es ___.", "public"),
  pr2=("El modificador para limitar una declaración al mismo módulo es ___.", "internal"),
  ec="suponer que internal significa acceso desde cualquier módulo"),
K("Herencia abierta",
  d="mecanismo para derivar una clase de otra marcada explícitamente como open",
  u="especializar una implementación existente",
  mas="Las clases y funciones Kotlin son finales por defecto. Para permitir herencia, la clase base debe declararse `open`; el subtipo indica el tipo base tras dos puntos.",
  k=["Las clases Kotlin son final por defecto.", "open permite heredar de una clase.", "Una subclase inicia la llamada al constructor de su clase base."],
  sit="Una clase base debe permitir que otros tipos la extiendan para agregar comportamiento especializado. ¿Qué modificador necesita?",
  cod="""open class Figura(val lados: Int)
class Triangulo : Figura(3)
fun main() {
    println(Triangulo().lados)
}""", out="3",
  h="hereda una clase base abierta para crear un triángulo",
  pr=("El modificador que permite extender una clase Kotlin es ___.", "open"),
  pr2=("Las clases Kotlin son ___ por defecto.", "final"),
  ec="intentar heredar de una clase que no está marcada open"),
K("override",
  d="modificador que declara la implementación de un miembro abierto heredado",
  u="personalizar en una subclase un comportamiento de la clase base",
  mas="La función base debe ser `open` o abstracta para sobrescribirse. `override` es obligatorio y el compilador verifica que la firma coincida con un miembro heredado.",
  k=["La función base debe permitir override.", "override es obligatorio al sobrescribir.", "El compilador valida la firma del miembro sobrescrito."],
  sit="Una subclase necesita cambiar el resultado de una función abierta definida por su clase padre. ¿Qué modificador declara?",
  cod="""open class Saludo {
    open fun texto() = "hola"
}
class SaludoFormal : Saludo() {
    override fun texto() = "buen día"
}
fun main() {
    println(SaludoFormal().texto())
}""", out="buen día",
  h="sobrescribe el saludo de la clase base",
  pr=("El modificador que declara una sobrescritura válida es ___.", "override"),
  pr2=("El miembro de la clase base debe ser open o ___.", "abstract"),
  ec="escribir override para una función base que no es abierta"),
K("Interface",
  d="contrato de miembros que una clase puede implementar",
  u="definir capacidades compartidas sin imponer una única clase base",
  mas="Una clase implementa una interfaz después de dos puntos y debe proporcionar los miembros abstractos requeridos. Kotlin permite que una clase implemente varias interfaces.",
  k=["Una interfaz puede declarar funciones abstractas.", "Una clase puede implementar más de una interfaz.", "La implementación se indica con dos puntos en la cabecera."],
  sit="Varios tipos no relacionados deben ofrecer una operación común sin compartir una clase padre. ¿Qué contrato defines?",
  cod="""interface Medible {
    fun unidades(): Int
}
class Paquete : Medible {
    override fun unidades() = 4
}
fun main() {
    println(Paquete().unidades())
}""", out="4",
  h="implementa un contrato de medición en un tipo",
  pr=("El contrato que puede implementar una clase se llama ___.", "interface"),
  pr2=("Una clase Kotlin puede implementar ___ interfaces.", "varias"),
  ec="intentar crear directamente una instancia de una interfaz"),
K("Clase abstracta",
  d="clase incompleta que no puede instanciarse directamente y puede exigir miembros",
  u="compartir estado o lógica base entre subclases relacionadas",
  mas="Una clase abstracta puede combinar implementaciones concretas con miembros abstractos. La subclase concreta debe implementar los miembros abstractos antes de poder instanciarse.",
  k=["Una clase abstracta no se instancia directamente.", "Puede contener miembros concretos y abstractos.", "Una subclase concreta implementa los miembros abstractos."],
  sit="Varios tipos comparten estado inicial y una operación obligatoria pero no deben instanciarse como tipo base. ¿Qué clase diseñas?",
  cod="""abstract class Figura {
    abstract fun lados(): Int
}
class Cuadrado : Figura() {
    override fun lados() = 4
}
fun main() {
    println(Cuadrado().lados())
}""", out="4",
  h="implementa en una clase concreta el miembro abstracto",
  pr=("La clase que no puede instanciarse directamente es ___.", "abstracta", "abstract"),
  pr2=("Una subclase concreta debe implementar miembros ___.", "abstractos"),
  ec="intentar crear una instancia directa de una clase abstracta"),
K("Sealed class",
  d="clase sellada que restringe sus subclases directas al mismo paquete y módulo",
  u="modelar jerarquías cerradas de estados o resultados",
  mas="Una jerarquía sellada permite que el compilador conozca las subclases directas posibles. Por ello, un `when` sobre el tipo puede ser exhaustivo sin una rama `else` cuando cubre todas las variantes.",
  k=["Las subclases directas de una sealed class están restringidas al mismo paquete y módulo.", "sealed class expresa una jerarquía cerrada.", "when puede comprobar exhaustivamente los subtipos conocidos."],
  sit="El resultado de una operación solo puede ser éxito o fallo y quieres que el compilador conozca todas las variantes. ¿Qué tipo base usas?",
  cod="""sealed class Resultado
data class Exito(val valor: Int) : Resultado()
object Fallo : Resultado()
fun texto(r: Resultado) = when (r) {
    is Exito -> "ok"
    Fallo -> "error"
}
fun main() {
    println(texto(Exito(1)))
}""", out="ok",
  h="selecciona de forma exhaustiva la variante de resultado",
  pr=("La clase para modelar un conjunto restringido de subtipos es ___.", "sealed"),
  pr2=("Una selección exhaustiva de variantes se expresa con ___.", "when"),
  ec="agregar else sin notar que when ya podría ser exhaustivo"),
K("Declaración object",
  d="declaración que crea una única instancia con nombre de un tipo",
  u="representar un singleton o agrupar miembros relacionados",
  mas="Una declaración `object` inicializa su instancia de forma perezosa y segura para hilos en JVM. Se accede a sus miembros mediante el nombre del objeto, sin construirlo con un constructor público.",
  k=["Una declaración object crea una instancia singleton.", "Sus miembros se acceden mediante el nombre del objeto.", "La inicialización del objeto es perezosa."],
  sit="Una aplicación necesita un único catálogo compartido con un identificador fijo. ¿Qué declaración usas?",
  cod="""object Catalogo {
    val codigo = "C1"
}
fun main() {
    println(Catalogo.codigo)
}""", out="C1",
  h="accede a la propiedad del singleton Catalogo",
  pr=("La declaración singleton de Kotlin se escribe con ___.", "object"),
  pr2=("Los miembros de una declaración object se consultan con su ___.", "nombre"),
  ec="intentar crear instancias de una declaración object con paréntesis"),
K("Companion object",
  d="objeto asociado a una clase que contiene miembros accesibles mediante el nombre de la clase",
  u="agrupar fábricas y valores relacionados con el tipo",
  mas="Kotlin no declara miembros estáticos propios al estilo de Java; un `companion object` ofrece un objeto asociado a la clase. Sus miembros se pueden referir por el nombre de la clase desde Kotlin.",
  k=["Cada clase puede declarar un companion object.", "Sus miembros se acceden por el nombre de la clase desde Kotlin.", "Los miembros del companion siguen perteneciendo a un objeto."],
  sit="Una clase debe ofrecer una función de fábrica invocable mediante el nombre de la clase. ¿Qué miembro usas?",
  cod="""class Punto private constructor(val x: Int) {
    companion object {
        fun origen() = Punto(0)
    }
}
fun main() {
    println(Punto.origen().x)
}""", out="0",
  h="crea una instancia mediante una fábrica del objeto acompañante",
  pr=("El objeto asociado a una clase se declara con companion ___.", "object"),
  pr2=("Desde Kotlin, los miembros acompañantes se pueden llamar con el nombre de la ___.", "clase"),
  ec="afirmar que un miembro de companion object es literalmente un campo estático Kotlin"),
K("Tipo nullable",
  d="tipo marcado con ? que acepta una referencia de valor o null",
  u="representar explícitamente un resultado opcional",
  mas="Un tipo nullable, como `Int?`, puede contener `null`; el tipo `Int` no. Antes de usar sus miembros hay que comprobarlo o usar operaciones seguras para null.",
  k=["El sufijo ? marca un tipo nullable.", "Un tipo nullable puede contener null.", "El compilador impide usar directamente un valor nullable sin manejo."],
  sit="Una búsqueda puede no encontrar un número y quieres representar ambos resultados en el tipo. ¿Qué tipo declaras?",
  cod="""fun buscar(): Int? = null
fun main() {
    println(buscar() == null)
}""", out="true",
  h="devuelve un Int nullable ausente y comprueba el resultado",
  pr=("El sufijo de un tipo que puede contener null es ___.", "?"),
  pr2=("El tipo Int? puede contener el valor ___.", "null"),
  ec="asignar null a Int sin marcarlo como nullable"),
K("Llamada segura",
  d="operador ?. que accede a un miembro solo si el receptor no es null",
  u="propagar ausencia sin lanzar una excepción por acceso nulo",
  mas="Una llamada como `nombre?.length` devuelve null si el receptor es null; de lo contrario devuelve la longitud. El resultado es nullable si el receptor puede serlo.",
  k=["El operador de llamada segura es ?.", "Si el receptor es null, la expresión produce null.", "La llamada segura no ejecuta el acceso al miembro para un receptor nulo."],
  sit="Un nombre puede estar ausente y solo debes leer su longitud cuando existe. ¿Qué operador usas?",
  cod="""fun main() {
    val nombre: String? = null
    println(nombre?.length)
}""", out="null",
  h="lee la longitud solo si nombre no es null",
  pr=("El operador de acceso seguro a un miembro es ___.", "?."),
  pr2=("Una llamada segura sobre un receptor null produce ___.", "null"),
  ec="usar punto normal para acceder directamente a una referencia nullable"),
K("Operador Elvis",
  d="operador ?: que elige un valor alternativo cuando la expresión izquierda es null",
  u="proporcionar un valor de reserva o salir temprano",
  mas="La expresión `valor ?: alternativa` devuelve el valor no nulo de la izquierda o evalúa la alternativa si es null. El lado derecho se evalúa solo cuando hace falta.",
  k=["El operador Elvis se escribe ?: .", "La alternativa se evalúa si la izquierda es null.", "El operador puede combinarse con return o throw a la derecha."],
  sit="Una búsqueda nullable debe convertirse en una etiqueta predeterminada cuando no hay resultado. ¿Qué operador aplicas?",
  cod="""fun main() {
    val etiqueta: String? = null
    println(etiqueta ?: "sin etiqueta")
}""", out="sin etiqueta",
  h="elige el texto alternativo al encontrar null",
  pr=("El operador Kotlin para proporcionar una alternativa a null es ___.", "?:"),
  pr2=("En `valor ?: reserva`, la reserva se usa si valor es ___.", "null"),
  ec="usar el operador Elvis creyendo que reemplaza también valores vacíos"),
K("Aserción no nula",
  d="operador !! que convierte una referencia nullable en no nullable o lanza excepción",
  u="forzar una comprobación cuando el programa garantiza un valor no nulo",
  mas="`valor!!` produce el valor si no es null y lanza `NullPointerException` si sí lo es. Kotlin permite la operación, pero usarla innecesariamente pierde la protección del sistema de tipos.",
  k=["!! elimina el nullable del tipo en la expresión.", "!! lanza NullPointerException cuando el valor es null.", "Las llamadas seguras o Elvis suelen ser alternativas más seguras."],
  sit="Una integración antigua garantiza un valor en esta ruta, aunque el tipo expuesto todavía es nullable. ¿Qué operador lo afirma explícitamente?",
  cod="""fun main() {
    val codigo: String? = "A4"
    println(codigo!!.length)
}""", out="2",
  h="afirma que el código no es null y muestra su longitud",
  pr=("El operador de aserción no nula de Kotlin es ___.", "!!"),
  pr2=("Aplicar !! a null lanza NullPointer___.", "Exception"),
  ec="usar !! sin garantizar que la referencia no sea null"),
K("Smart cast",
  d="refinamiento automático del tipo tras una comprobación que prueba una condición",
  u="usar un miembro específico después de comprobar el tipo o la nulidad",
  mas="Tras comprobar `x != null`, el compilador puede tratar `x` como no nullable si su valor no puede cambiar de forma que invalide la comprobación. También puede refinar tipos tras una comprobación `is`.",
  k=["Una comprobación de null puede refinar el tipo.", "`is` puede permitir un smart cast al subtipo comprobado.", "Una propiedad mutable o con getter personalizado puede no ser smart-casteable si el valor no es estable."],
  sit="Una variable de tipo Any se comprueba con is String y luego debe usarse como cadena sin conversión manual. ¿Qué hace el compilador?",
  cod="""fun main() {
    val dato: Any = "Kotlin"
    if (dato is String) println(dato.length)
}""", out="6",
  h="refina Any a String dentro de la rama comprobada",
  pr=("El refinamiento automático del tipo tras una comprobación se llama smart ___.", "cast"),
  pr2=("El operador que comprueba si un valor es de un tipo es ___.", "is"),
  ec="esperar un smart cast cuando el compilador no puede demostrar que el valor sea estable"),
K("Conversión segura as?",
  d="operador as? que intenta convertir un valor y devuelve null si falla",
  u="probar un tipo sin lanzar una excepción de conversión",
  mas="`valor as? Tipo` devuelve una instancia de ese tipo o null si la conversión no es posible. El resultado es nullable y debe tratarse en consecuencia.",
  k=["as? es una conversión segura.", "Una conversión fallida con as? produce null.", "as sin ? puede lanzar ClassCastException."],
  sit="Un dato Any podría no ser una cadena y quieres intentar convertirlo sin lanzar una excepción. ¿Qué operador eliges?",
  cod="""fun main() {
    val dato: Any = 12
    val texto = dato as? String
    println(texto == null)
}""", out="true",
  h="intenta convertir un entero a String y obtiene null",
  pr=("El operador de conversión segura que devuelve null al fallar es ___.", "as?"),
  pr2=("La conversión insegura que puede lanzar excepción usa el operador ___.", "as"),
  ec="usar as cuando el objeto podría no ser del tipo esperado"),
]
