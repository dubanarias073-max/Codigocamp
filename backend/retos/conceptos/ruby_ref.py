"""Ruby · referencia completa (etapas 6 y 7)."""
from .tabla import filas

E6 = filas(r"""
Métodos de String en Ruby ¦ upcase ¦ métodos para cambiar y revisar textos ¦ normalizar el nombre de un usuario ¦ s = "  hola ruby  "⏎puts s.strip.capitalize, s.include?("ruby") ¦ limpia, pone mayúscula y busca una palabra ¦ olvidar que los métodos con ! modifican el texto
Formato con format ¦ format ¦ método para dar formato a números y textos ¦ mostrar un precio con dos decimales ¦ puts format("Total: %.2f", 12.5)⏎puts "7".rjust(3, "0") ¦ muestra el precio y un código con ceros ¦ concatenar números sin convertirlos a texto
Enumerable reduce y sum ¦ reduce ¦ métodos para acumular valores de colecciones ¦ sumar el total de un carrito ¦ p = [10, 20, 30]⏎puts p.sum, p.reduce(:+), p.max ¦ suma y busca el mayor ¦ hacer bucles manuales para sumar
sort_by y min_by ¦ sort_by ¦ métodos para ordenar y buscar según un criterio ¦ ordenar productos por precio ¦ p = [{ n: "café", p: 8 }, { n: "pan", p: 3 }]⏎puts p.sort_by { _1[:p] }.first[:n], p.max_by { _1[:p] }[:n] ¦ ordena por precio y busca el más caro ¦ ordenar y luego invertir cuando max_by basta
group_by y tally ¦ tally ¦ métodos para agrupar y contar elementos ¦ contar cuántas veces aparece cada palabra ¦ p %w[a b a c a]⏎p %w[a b a c a].tally ¦ cuenta cada letra ¦ contar con hashes y bucles a mano
partition y each_slice ¦ partition ¦ métodos para dividir colecciones ¦ separar aprobados y reprobados ¦ ok, no = [4, 2, 5].partition { _1 >= 3 }⏎p ok, no, (1..5).each_slice(2).to_a ¦ separa por condición y en grupos de dos ¦ recorrer la lista dos veces
each_with_object ¦ each_with_object ¦ método que recorre y construye un objeto a la vez ¦ crear un hash a partir de una lista ¦ h = %w[ana luis].each_with_object({}) { |n, acc| acc[n] = n.length }⏎p h ¦ crea un hash nombre → largo ¦ olvidar que el objeto se pasa como segundo parámetro
zip, flatten y uniq ¦ uniq ¦ métodos para combinar, aplanar y quitar repetidos ¦ juntar etiquetas sin repetir ¦ p [[1, 2], [2, 3]].flatten.uniq⏎p [1, 2].zip(["a", "b"]) ¦ aplana, quita repetidos y empareja ¦ usar uniq! y recibir nil cuando no hubo cambios
Hash: select, map y transform_values ¦ transform_values ¦ métodos para filtrar y transformar hashes ¦ aplicar IVA a todos los precios ¦ precios = { cafe: 5, te: 4 }⏎p precios.transform_values { _1 * 1.19 }⏎p precios.select { |_, v| v > 4 } ¦ transforma y filtra los precios ¦ convertir a arreglo y de vuelta sin necesidad
Hash con valor por defecto ¦ Hash.new ¦ hash que devuelve un valor cuando falta una clave ¦ contar sin revisar si la clave existe ¦ c = Hash.new(0)⏎"banana".each_char { c[_1] += 1 }⏎p c ¦ cuenta las letras de banana ¦ usar Hash.new([]) y compartir el mismo arreglo
Fechas con Time y Date ¦ Time.now ¦ clases para fechas y horas ¦ mostrar la fecha de hoy con formato ¦ require "date"⏎d = Date.new(2026, 12, 24)⏎puts d.strftime("%d/%m/%Y"), (d + 7).to_s ¦ formatea la fecha y suma una semana ¦ confundir %m (mes) con %M (minutos)
Expresiones regulares en Ruby ¦ =~ ¦ patrones para validar y buscar en textos ¦ validar una placa de carro ¦ puts "ABC123".match?(/\A[A-Z]{3}\d{3}\z/)⏎p "3 gatos y 12 peces".scan(/\d+/) ¦ valida una placa y saca los números ¦ usar ^ y $ en vez de \A y \z para validar
Excepciones con rescue ¦ rescue ¦ manejo de errores en Ruby ¦ convertir un texto con respaldo ¦ n = begin⏎  Integer("x")⏎rescue ArgumentError⏎  -1⏎end⏎puts n ¦ devuelve -1 si la conversión falla ¦ rescatar Exception y ocultar todo
ensure y retry ¦ ensure ¦ bloques que siempre se ejecutan o reintentan ¦ cerrar un recurso aunque haya error ¦ intentos = 0⏎begin⏎  intentos += 1⏎  raise "falló" if intentos < 3⏎  puts "ok en #{intentos}"⏎rescue⏎  retry⏎ensure⏎  puts "fin"⏎end ¦ reintenta hasta lograrlo y siempre muestra fin ¦ reintentar sin límite y crear un bucle infinito
""")

E7 = filas(r"""
Leer y escribir archivos ¦ File.write ¦ métodos para guardar y leer archivos ¦ guardar notas en un archivo ¦ require "tmpdir"⏎f = File.join(Dir.tmpdir, "notas.txt")⏎File.write(f, "uno\ndos")⏎puts File.readlines(f).size ¦ escribe y cuenta las líneas ¦ abrir archivos sin bloque y olvidar cerrarlos
JSON en Ruby ¦ JSON.parse ¦ librería para convertir hashes a JSON y al revés ¦ leer la respuesta de una API ¦ require "json"⏎h = JSON.parse('{"nombre":"Ana"}', symbolize_names: true)⏎puts h[:nombre], { ok: true }.to_json ¦ lee y genera JSON ¦ olvidar symbolize_names y buscar con símbolos
Gemas y Bundler ¦ bundle install ¦ sistema de paquetes de Ruby ¦ instalar librerías en tu proyecto ¦ # Gemfile: gem "colorize"⏎# bundle install⏎puts "gemas" ¦ instala las gemas del Gemfile ¦ no fijar versiones y romper el proyecto
Pruebas con Minitest ¦ assert_equal ¦ librería de pruebas incluida en Ruby ¦ comprobar que un método funciona ¦ def sumar(a, b) = a + b⏎# class TestSuma < Minitest::Test; def test_suma = assert_equal(5, sumar(2, 3)); end⏎puts sumar(2, 3) == 5 ¦ prueba la suma ¦ probar solo los casos felices
RSpec ¦ expect ¦ framework de pruebas muy usado en Ruby ¦ describir el comportamiento esperado ¦ # describe "sumar" do⏎#   it("suma dos números") { expect(sumar(2, 3)).to eq(5) }⏎# end⏎puts "rspec" ¦ describe y prueba la suma ¦ escribir pruebas que dependen unas de otras
Comparable ¦ <=> ¦ módulo que agrega comparaciones a partir de <=> ¦ comparar versiones o productos ¦ class Precio⏎  include Comparable⏎  attr_reader :v⏎  def initialize(v) = @v = v⏎  def <=>(o) = v <=> o.v⏎end⏎puts Precio.new(3) < Precio.new(5) ¦ compara precios con < ¦ definir < > == a mano uno por uno
Enumerable propio ¦ include Enumerable ¦ módulo que da map, select y más a tus clases ¦ recorrer una colección propia con métodos de Ruby ¦ class Lista⏎  include Enumerable⏎  def initialize(*x) = @x = x⏎  def each(&b) = @x.each(&b)⏎end⏎p Lista.new(3, 1, 2).sort ¦ ordena una colección propia ¦ olvidar definir each
method_missing ¦ method_missing ¦ método que se llama cuando no existe el que se pidió ¦ crear objetos que responden a nombres dinámicos ¦ class Config⏎  def method_missing(n, *) = "valor de #{n}"⏎  def respond_to_missing?(*) = true⏎end⏎puts Config.new.tema ¦ responde a cualquier método ¦ olvidar respond_to_missing?
Ruby on Rails ¦ rails new ¦ framework para crear aplicaciones web completas ¦ hacer una app con base de datos en poco tiempo ¦ # rails new tienda⏎# rails generate scaffold Producto nombre:string precio:decimal⏎# rails db:migrate⏎puts "Rails" ¦ crea una app con productos ¦ poner toda la lógica en los controladores
Active Record ¦ where ¦ ORM de Rails para trabajar con tablas como objetos ¦ consultar productos sin escribir SQL ¦ # Producto.where("precio > ?", 100).order(:precio)⏎puts "Active Record" ¦ busca productos caros ordenados ¦ hacer una consulta por cada fila
Rutas de Rails ¦ resources ¦ archivo que conecta direcciones con controladores ¦ crear las rutas de un CRUD con una línea ¦ # config/routes.rb⏎# resources :productos⏎puts "rutas" ¦ crea las siete rutas del CRUD ¦ escribir cada ruta a mano
Sinatra ¦ get ¦ microframework para APIs y páginas pequeñas ¦ hacer una API sencilla ¦ # require "sinatra"⏎# get("/hola") { "Hola" }⏎puts "Sinatra" ¦ crea una ruta que responde Hola ¦ usar Sinatra para apps enormes sin estructura
Ractors ¦ Ractor ¦ unidades que ejecutan código Ruby en paralelo de verdad ¦ aprovechar varios núcleos del procesador ¦ r = Ractor.new { 2 + 3 }⏎puts r.respond_to?(:value) ? r.value : r.take ¦ calcula en paralelo y lee el resultado ¦ compartir objetos mutables entre ractors
Proyecto final con Ruby ¦ ruby main.rb ¦ programa completo con clases, módulos, archivos y pruebas ¦ practicar todo lo aprendido ¦ Tarea = Struct.new(:texto, :hecha)⏎tareas = [Tarea.new("Estudiar Ruby", false)]⏎tareas.each { puts "#{_1.hecha ? '✔' : '•'} #{_1.texto}" } ¦ muestra una lista de tareas ¦ escribir todo en un solo archivo sin clases
""")

ETAPAS_REF = [
    ("Ruby a fondo: textos y colecciones", "Textos, Enumerable completo, hashes, fechas, regex y errores", E6),
    ("Ruby profesional", "Archivos, JSON, gemas, pruebas, metaprogramación, Rails, Sinatra y Ractors", E7),
]
