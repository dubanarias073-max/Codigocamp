// Lecciones de Kotlin. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"Kotlin se usa en Android y en servidores.",
    p:["fun main es el inicio", "println imprime"],
    c:`fun main() {
  println("¡Hola, CódigoCamp!")
}` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"val es fijo y var puede cambiar.",
    p:["Los textos aceptan $variable", "if es una expresión"],
    c:`fun main() {
  val nombre = "Ana"
  var edad = 20
  edad += 1
  if (edad >= 18) println("$nombre es mayor de edad")
}` },
  { m:"Fundamentos", t:"Bucles", x:"for recorre un rango. 1..5 incluye el 5.",
    p:["1..5 llega hasta el 5", "until excluye el último"],
    c:`fun main() {
  for (i in 1..5) {
    println("Vuelta $i")
  }
}` },
  { m:"Fundamentos", t:"Funciones", x:"fun define una función. El tipo va después de los dos puntos.",
    p:["Indica el tipo que devuelve", "return devuelve el valor"],
    c:`fun doble(n: Int): Int {
  return n * 2
}

fun main() {
  println(doble(21))
}` },
  { m:"Intermedio", t:"Listas y mapas", x:"Kotlin distingue colecciones inmutables (listOf, mapOf) y mutables (mutableListOf). map y filter las transforman.",
    p:["listOf no se puede modificar; mutableListOf sí", "mapOf(\"a\" to 1) crea un mapa", "map y filter devuelven colecciones nuevas"],
    c:"fun main() {\n  val nums = listOf(1, 2, 3, 4, 5)\n  val pares = nums.filter { it % 2 == 0 }\n  val dobles = nums.map { it * 2 }\n  println(pares)\n  println(dobles)\n\n  val edades = mapOf(\"Ana\" to 20, \"Luis\" to 25)\n  for ((nombre, edad) in edades) {\n    println(\"$nombre tiene $edad\")\n  }\n}",
    r:"Suma todos los números con nums.sum()." },
  { m:"Intermedio", t:"Clases y data classes", x:"Una data class guarda datos y genera equals, toString y copy automáticamente. El constructor va junto al nombre.",
    p:["class Persona(val nombre: String) usa constructor primario", "data class evita escribir código repetido", "copy() crea una copia cambiando algunos campos"],
    c:"data class Persona(val nombre: String, val edad: Int)\n\nfun main() {\n  val p = Persona(\"Ana\", 20)\n  val mayor = p.copy(edad = 21)\n  println(p)\n  println(mayor)\n  println(p == Persona(\"Ana\", 20))\n}",
    r:"Crea una lista de Personas y ordénala por edad con sortedBy." },
  { m:"Avanzado", t:"Nulabilidad segura", x:"Kotlin separa tipos que aceptan null (String?) de los que no. Los operadores ?. y ?: evitan errores.",
    p:["String? puede ser null, String no", "?. accede solo si no es null", "?: da un valor por defecto"],
    c:"fun longitud(texto: String?): Int {\n  return texto?.length ?: 0\n}\n\nfun main() {\n  println(longitud(\"hola\"))\n  println(longitud(null))\n\n  val nombre: String? = null\n  nombre?.let { println(\"Hola $it\") }\n  println(nombre ?: \"Invitado\")\n}",
    r:"Evita usar !! y reemplázalo con ?: o let.",
    e:"!! lanza una excepción si el valor es null; úsalo muy poco." },
  { m:"Avanzado", t:"Herencia e interfaces", x:"Las clases son finales por defecto: usa open para permitir herencia. Una interfaz define un contrato.",
    p:["open permite heredar", "override reemplaza un miembro del padre", "Una clase puede implementar varias interfaces"],
    c:"interface Sonido { fun hacerSonido(): String }\n\nopen class Animal : Sonido {\n  override fun hacerSonido() = \"...\"\n}\n\nclass Perro : Animal() {\n  override fun hacerSonido() = \"Guau\"\n}\n\nfun main() {\n  val a: Animal = Perro()\n  println(a.hacerSonido())\n}",
    r:"Crea la clase Gato y recorre una lista de animales." },
  { m:"Experto", t:"Corrutinas", x:"Las corrutinas permiten tareas asíncronas ligeras. Una función suspend puede pausarse sin bloquear el hilo.",
    p:["suspend marca una función que puede suspenderse", "launch y async inician corrutinas", "Necesitan la librería kotlinx.coroutines"],
    c:"// Requiere: kotlinx-coroutines-core\n// import kotlinx.coroutines.*\n//\n// suspend fun cargar(): String {\n//   delay(500)\n//   return \"Datos listos\"\n// }\n//\n// fun main() = runBlocking {\n//   println(cargar())\n// }\n\nfun main() {\n  println(\"Las corrutinas se usan con kotlinx.coroutines\")\n}",
    r:"Lee la documentación de runBlocking y launch para lanzar dos tareas a la vez." },
  { m:"Experto", t:"Funciones de orden superior y extensiones", x:"Las funciones pueden recibir otras funciones como parámetro y las extensiones añaden métodos a clases existentes.",
    p:["Una lambda se escribe { x -> ... }", "Una función de extensión se declara como fun Tipo.nombre()", "Hacen el código más expresivo"],
    c:"fun String.alReves(): String = this.reversed()\n\nfun aplicar(n: Int, f: (Int) -> Int): Int = f(n)\n\nfun main() {\n  println(\"hola\".alReves())\n  println(aplicar(5) { it * 3 })\n}",
    r:"Crea una extensión Int.esPar() y úsala con filter." },
];
