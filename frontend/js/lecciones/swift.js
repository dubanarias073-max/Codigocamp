// Lecciones de Swift. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"Swift es el lenguaje de las apps de Apple.",
    p:["print imprime", "No necesita ;"],
    c:`print("¡Hola, CódigoCamp!")` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"let es fijo y var puede cambiar.",
    p:["let nombre = \"Ana\"", "if condición { ... }"],
    c:`let nombre = "Ana"
var edad = 20
edad += 1
if edad >= 18 {
  print(nombre, "es mayor de edad")
}` },
  { m:"Fundamentos", t:"Bucles", x:"for recorre un rango. 1...5 incluye el 5.",
    p:["1...5 llega hasta el 5", "1..<5 llega hasta el 4"],
    c:`for i in 1...5 {
  print("Vuelta", i)
}` },
  { m:"Fundamentos", t:"Funciones", x:"func define una función. Indica el tipo que devuelve con ->.",
    p:["_ permite llamarla sin nombre de parámetro", "return devuelve el valor"],
    c:`func doble(_ n: Int) -> Int {
  return n * 2
}
print(doble(21))` },
  { m:"Intermedio", t:"Arreglos y diccionarios", x:"Un arreglo guarda valores en orden y un diccionario asocia claves con valores. map y filter los transforman.",
    p:["[1, 2, 3] es un arreglo", "[\"a\": 1] es un diccionario", "map y filter devuelven colecciones nuevas"],
    c:"let nums = [1, 2, 3, 4, 5]\nlet pares = nums.filter { $0 % 2 == 0 }\nlet dobles = nums.map { $0 * 2 }\nprint(pares)\nprint(dobles)\n\nlet edades = [\"Ana\": 20, \"Luis\": 25]\nfor (nombre, edad) in edades.sorted(by: { $0.key < $1.key }) {\n  print(\"\\(nombre) tiene \\(edad)\")\n}",
    r:"Calcula la suma con reduce(0, +)." },
  { m:"Intermedio", t:"Structs y clases", x:"Las struct se copian al asignarse (tipo valor) y las clases se comparten (tipo referencia). Ambas pueden tener métodos.",
    p:["struct es de tipo valor", "class es de tipo referencia", "init prepara una instancia"],
    c:"struct Punto {\n  var x: Int\n  var y: Int\n\n  func descripcion() -> String {\n    return \"(\\(x), \\(y))\"\n  }\n}\n\nvar a = Punto(x: 1, y: 2)\nvar b = a\nb.x = 10\nprint(a.descripcion(), b.descripcion())",
    r:"Cambia struct por class y observa qué pasa con a.",
    e:"Usar class cuando una struct bastaría: prefiere struct para datos simples." },
  { m:"Avanzado", t:"Opcionales", x:"Un opcional (Int?) puede contener un valor o nil. if let, guard let y ?? lo desenvuelven con seguridad.",
    p:["nil indica ausencia de valor", "if let ejecuta un bloque si hay valor", "?? da un valor por defecto"],
    c:"func buscar(_ nombre: String) -> Int? {\n  let edades = [\"Ana\": 20, \"Luis\": 25]\n  return edades[nombre]\n}\n\nif let edad = buscar(\"Ana\") {\n  print(\"Ana tiene \\(edad)\")\n}\nprint(buscar(\"Pedro\") ?? 0)",
    r:"Usa guard let para salir pronto de una función cuando no hay valor.",
    e:"Forzar el desenvuelto con ! cuando el valor puede ser nil bloquea la app." },
  { m:"Avanzado", t:"Protocolos y extensiones", x:"Un protocolo define métodos que un tipo debe tener. Una extensión añade funciones a tipos existentes.",
    p:["protocol declara un contrato", "Los tipos adoptan protocolos con \":\"", "extension agrega métodos sin heredar"],
    c:"protocol Saludable {\n  func saludar() -> String\n}\n\nstruct Persona: Saludable {\n  let nombre: String\n  func saludar() -> String { \"Hola, soy \\(nombre)\" }\n}\n\nextension Int {\n  var esPar: Bool { self % 2 == 0 }\n}\n\nprint(Persona(nombre: \"Ana\").saludar())\nprint(4.esPar)",
    r:"Crea otro tipo que adopte Saludable." },
  { m:"Experto", t:"Closures y funciones de orden superior", x:"Un closure es un bloque de código que se guarda en una variable o se pasa a una función.",
    p:["{ (a, b) in ... } es un closure", "sorted(by:) recibe un closure", "Los closures capturan variables de su entorno"],
    c:"let nombres = [\"Luis\", \"Ana\", \"Marta\"]\nlet ordenados = nombres.sorted { $0 < $1 }\nprint(ordenados)\n\nfunc aplicar(_ n: Int, _ f: (Int) -> Int) -> Int { f(n) }\nprint(aplicar(5) { $0 * 3 })",
    r:"Ordena los nombres por su longitud." },
  { m:"Experto", t:"Genéricos y concurrencia", x:"Los genéricos escriben código para cualquier tipo. async/await simplifica la concurrencia en Swift moderno.",
    p:["<T> declara un tipo genérico", "async marca una función asíncrona", "await espera su resultado"],
    c:"func primero<T>(_ lista: [T]) -> T? {\n  return lista.first\n}\n\nprint(primero([10, 20, 30]) ?? 0)\nprint(primero([\"a\", \"b\"]) ?? \"\")\n\n// Con concurrencia moderna:\n// func cargar() async -> String { \"listo\" }\n// let datos = await cargar()",
    r:"Escribe una función generica ultimo<T> que devuelva el último elemento." },
];
