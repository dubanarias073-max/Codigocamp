// Lecciones de Ruby. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"Ruby está pensado para que programar sea agradable.",
    p:["puts imprime una línea", "No lleva ; ni paréntesis obligatorios"],
    c:`puts "¡Hola, CódigoCamp!"` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"Las variables se crean al asignarlas.",
    p:["\"texto #{variable}\"", "if ... end"],
    c:`nombre = "Ana"
edad = 20
if edad >= 18
  puts "#{nombre} es mayor de edad"
end` },
  { m:"Fundamentos", t:"Bucles", x:"each recorre un rango o una lista ejecutando un bloque.",
    p:["(1..5) es un rango", "|i| recibe cada valor"],
    c:`(1..5).each do |i|
  puts "Vuelta #{i}"
end` },
  { m:"Fundamentos", t:"Métodos", x:"def define un método. La última línea se devuelve sola.",
    p:["No hace falta return", "end cierra el método"],
    c:`def doble(n)
  n * 2
end

puts doble(21)` },
  { m:"Intermedio", t:"Arreglos y hashes", x:"Un arreglo guarda valores en orden y un hash asocia claves con valores. Tienen métodos como map, select y each.",
    p:["[1, 2, 3] es un arreglo", "{ nombre: \"Ana\" } es un hash", "map y select devuelven colecciones nuevas"],
    c:"nums = [1, 2, 3, 4, 5]\nputs nums.select { |n| n.even? }.inspect\nputs nums.map { |n| n * 2 }.inspect\n\nedades = { ana: 20, luis: 25 }\nedades.each do |nombre, edad|\n  puts \"#{nombre} tiene #{edad}\"\nend",
    r:"Suma todos los números con nums.sum." },
  { m:"Intermedio", t:"Clases y objetos", x:"Una clase se define con class y se instancia con new. attr_accessor crea los métodos para leer y escribir atributos.",
    p:["initialize es el constructor", "@variable es una variable de instancia", "attr_accessor genera getters y setters"],
    c:"class Persona\n  attr_accessor :nombre\n\n  def initialize(nombre, edad)\n    @nombre = nombre\n    @edad = edad\n  end\n\n  def saludar\n    \"Hola, soy #{@nombre} y tengo #{@edad}\"\n  end\nend\n\np1 = Persona.new(\"Ana\", 20)\nputs p1.saludar",
    r:"Añade un método mayor? que devuelva true si @edad >= 18." },
  { m:"Avanzado", t:"Bloques, procs y yield", x:"Un bloque es código que se pasa a un método. yield lo ejecuta desde dentro del método.",
    p:["{ } o do…end crean un bloque", "yield ejecuta el bloque recibido", "Un proc guarda un bloque en una variable"],
    c:"def repetir(veces)\n  veces.times { |i| yield i + 1 }\nend\n\nrepetir(3) { |n| puts \"Vuelta #{n}\" }\n\ndoble = proc { |x| x * 2 }\nputs doble.call(5)",
    r:"Escribe un método que reciba un bloque y lo ejecute con cada elemento de un arreglo." },
  { m:"Avanzado", t:"Módulos y herencia", x:"Un módulo agrupa métodos que se mezclan en clases con include. La herencia usa \"<\".",
    p:["module agrupa comportamiento reutilizable", "include mezcla un módulo en una clase", "super llama al método del padre"],
    c:"module Saludable\n  def saludar\n    \"Hola, soy #{nombre}\"\n  end\nend\n\nclass Animal\n  attr_reader :nombre\n  def initialize(nombre) = @nombre = nombre\nend\n\nclass Perro < Animal\n  include Saludable\nend\n\nputs Perro.new(\"Rex\").saludar",
    r:"Crea otra clase que también incluya Saludable." },
  { m:"Experto", t:"Manejo de errores", x:"begin/rescue captura errores, ensure se ejecuta siempre y raise lanza uno propio.",
    p:["rescue atrapa el error", "ensure siempre se ejecuta", "raise lanza una excepción"],
    c:"def dividir(a, b)\n  raise ArgumentError, \"No se puede dividir entre 0\" if b == 0\n  a / b\nend\n\nbegin\n  puts dividir(10, 2)\n  puts dividir(5, 0)\nrescue ArgumentError => e\n  puts \"Error: #{e.message}\"\nensure\n  puts \"Fin\"\nend",
    r:"Captura ZeroDivisionError al dividir 5 / 0 directamente." },
  { m:"Experto", t:"Gems y Rails", x:"Las gems son librerías de Ruby y Bundler las gestiona. Ruby on Rails es el framework web más conocido del lenguaje.",
    p:["gem install instala una gema", "Gemfile lista las dependencias del proyecto", "Rails sigue el patrón MVC"],
    c:"# gem install rails\n# rails new mi_app\n# cd mi_app && rails server\n\nputs \"Ruby on Rails: convención sobre configuración\"",
    r:"Instala Ruby y crea tu primera app con rails new." },
];
