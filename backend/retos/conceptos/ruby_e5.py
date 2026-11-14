"""Ruby · Etapa 5: herramientas avanzadas y manejo de errores."""
from ..generador import K

LISTA = [
K("Avanzado",
  d="uso combinado de sintaxis moderna para expresar operaciones con claridad",
  u="aprovechar capacidades de Ruby 3 en programas compactos",
  mas="Ruby 3 incluye funciones como el pattern matching, las definiciones endless y el reenvío de argumentos con .... Estas herramientas reducen código repetitivo, pero deben elegirse cuando hacen más clara la intención. Esta etapa practica esas capacidades en ejemplos pequeños.",
  k=["Ruby 3 ofrece pattern matching en expresiones case/in.", "Ruby 3 permite definiciones endless de métodos.", "El operador ... puede reenviar argumentos en una definición."],
  sit="Quieres usar sintaxis moderna de Ruby para combinar una definición breve y una selección por patrón. ¿Qué enfoque estudias?",
  cod="""def triple(numero) = numero * 3
case [triple(2)]
in [valor]
  puts valor
end""",
  h="define un método endless y obtiene un valor con pattern matching",
  pr=("Una de las funciones modernas de Ruby 3 para seleccionar por forma es pattern ___. (matching)", "matching"),
  pr2=("Una definición endless termina en la misma ___ que inicia. (línea)", "línea", "linea"),
  ec="usar una sintaxis moderna sin comprobar la versión mínima de Ruby del proyecto",
  out="6"),
K("Errores",
  d="eventos excepcionales que interrumpen el flujo normal de un programa",
  u="detectar fallos y responder con un resultado controlado",
  mas="Ruby representa fallos recuperables mediante excepciones. begin delimita el código protegido y rescue maneja una clase concreta de error. Es preferible rescatar tipos específicos en vez de ocultar cualquier StandardError sin decidir cómo recuperarse.",
  k=["Una excepción interrumpe el flujo normal hasta ser manejada.", "rescue puede manejar una clase específica de excepción.", "Rescatar excepciones específicas evita ocultar fallos inesperados."],
  sit="Una división puede fallar si el divisor es cero y el programa debe mostrar un mensaje alternativo. ¿Qué mecanismo usas?",
  cod="""begin
  8 / 0
rescue ZeroDivisionError
  puts "no se puede dividir entre cero"
end""",
  h="maneja el error de dividir un entero por cero",
  pr=("La estructura que maneja una excepción dentro de begin usa ___. (rescue)", "rescue"),
  pr2=("Conviene rescatar una clase de error ___. (específica)", "específica", "especifica"),
  ec="rescatar Exception de manera general y ocultar errores inesperados",
  out="no se puede dividir entre cero"),
K("Patrones de arreglo",
  d="descomposición de arreglos mediante patrones case/in",
  u="extraer partes de una secuencia y comprobar su forma",
  mas="El pattern matching puede verificar que un Array tenga una forma determinada y asignar sus partes a variables. El patrón [primero, *resto] captura el primer elemento y todos los restantes. Si ningún patrón coincide y no hay else, Ruby puede generar NoMatchingPatternError.",
  k=["case/in compara un valor con patrones.", "*resto captura los elementos restantes de un arreglo.", "La coincidencia de patrones puede extraer y asignar valores."],
  sit="Una lista de comandos debe separar su primera palabra de los argumentos restantes. ¿Qué patrón aplicas?",
  cod="""comando = ["copiar", "origen", "destino"]
case comando
in [accion, *argumentos]
  puts "#{accion}: #{argumentos.length}"
end""",
  h="captura el primer elemento y cuenta los valores restantes",
  pr=("La forma de Ruby que compara un valor con un patrón se escribe case/___ . (in)", "in"),
  pr2=("El patrón *argumentos captura los elementos ___. (restantes)", "restantes"),
  ec="olvidar un patrón de respaldo cuando la forma de entrada puede variar",
  out="copiar: 2"),
K("Patrones de Hash",
  d="coincidencia de un Hash con claves y patrones de sus valores",
  u="extraer campos nombrados de datos estructurados",
  mas="Un patrón Hash especifica las claves que deben estar presentes y los patrones que deben cumplir sus valores. La sintaxis { nombre: } enlaza el valor de la clave símbolo :nombre a una variable local del mismo nombre. Las claves adicionales se permiten si no se exige que el patrón sea exacto.",
  k=["Los patrones Hash indican las claves requeridas.", "{ nombre: } enlaza el valor a una variable local nombre.", "Por defecto pueden existir claves adicionales a las indicadas."],
  sit="Un Hash con clave símbolo nombre debe ceder ese dato para construir un saludo. ¿Qué patrón usas?",
  cod="""persona = { nombre: "Nia", edad: 10 }
case persona
in { nombre: }
  puts "Hola, #{nombre}"
end""",
  h="extrae la clave nombre del Hash e imprime un saludo",
  pr=("El patrón abreviado para extraer la clave símbolo nombre es ___. ({ nombre: })", "{ nombre: }"),
  pr2=("El patrón { nombre: } enlaza el valor a una variable local llamada ___. (nombre)", "nombre"),
  ec="confundir una clave String con una clave Symbol en el patrón Hash",
  out="Hola, Nia"),
K("Asignación derecha de patrón",
  d="operador => que exige que un valor coincida con un patrón",
  u="extraer datos con una coincidencia que debe tener éxito",
  mas="Ruby permite escribir valor => patrón para hacer una asignación derecha de pattern matching. Si el valor no satisface el patrón, se genera NoMatchingPatternError. Es útil cuando la forma correcta es un requisito y no una alternativa entre varias.",
  k=["=> realiza una asignación derecha de patrón.", "El valor debe coincidir con el patrón requerido.", "Una no coincidencia genera NoMatchingPatternError."],
  sit="Una estructura válida debe contener dos coordenadas y quieres extraerlas o recibir un error. ¿Qué asignación usas?",
  cod="""[4, 9] => [x, y]
puts x + y""",
  h="extrae dos valores con una coincidencia obligatoria",
  pr=("El operador de asignación derecha de patrón es ___. (=>)", "=>"),
  pr2=("Una forma que no coincide produce NoMatchingPattern___. (Error)", "Error"),
  ec="usar => cuando la forma podría no coincidir y no se quiere manejar el error",
  out="13"),
K("Navegación segura",
  d="operador &. que evita llamar un método sobre nil",
  u="consultar una cadena opcional de valores sin excepción por nil",
  mas="El operador &. llama el método de la derecha solo si el receptor no es nil; si lo es, la expresión completa devuelve nil. No evita errores si un objeto no nil carece del método. En una cadena de accesos opcionales puede reducir comprobaciones repetitivas.",
  k=["&. omite la llamada cuando el receptor es nil.", "La navegación segura devuelve nil si el receptor es nil.", "&. no oculta errores de métodos inexistentes en receptores no nil."],
  sit="Una persona puede no tener apodo y el programa no debe llamar upcase sobre nil. ¿Qué operador empleas?",
  cod="""apodo = nil
puts apodo&.upcase
puts "listo" """,
  h="omite upcase para nil y continúa con la siguiente instrucción",
  pr=("El operador de navegación segura de Ruby es ___. (&.)", "&."),
  pr2=("Si el receptor es nil, &. devuelve ___. (nil)", "nil"),
  ec="suponer que &. evita cualquier error del método invocado",
  out="\nlisto"),
K("Consultar hashes anidados con dig",
  d="método que sigue una secuencia de claves o índices anidados",
  u="leer datos anidados sin encadenar accesos manuales",
  mas="dig consulta claves sucesivas en Hash u objetos compatibles, como Array. Si una parte intermedia es nil, la consulta devuelve nil en vez de intentar indexarla. La clave final también puede faltar y producir nil.",
  k=["dig consulta una ruta de claves o índices anidados.", "Si un valor intermedio es nil, dig devuelve nil.", "Hash y Array ofrecen formas de acceso con dig."],
  sit="Un perfil puede carecer de la sección dirección y necesitas consultar su calle sin indexar nil. ¿Qué método usas?",
  cod="""perfil = { direccion: { calle: "Sol" } }
puts perfil.dig(:direccion, :calle)
puts perfil.dig(:contacto, :calle).nil?""",
  h="consulta una calle anidada y comprueba una ruta ausente",
  pr=("El método para consultar claves anidadas es ___. (dig)", "dig"),
  pr2=("Si un valor intermedio de la ruta es nil, dig devuelve ___. (nil)", "nil"),
  ec="encadenar varios accesos [] cuando una parte intermedia puede ser nil",
  out="Sol\ntrue"),
K("Transformar y filtrar con filter_map",
  d="método que transforma elementos y descarta resultados nil o false",
  u="crear una lista de resultados válidos en una sola pasada",
  mas="filter_map aplica un bloque y recoge únicamente los resultados que no son nil ni false. Apareció en Ruby 2.7 y está disponible en Ruby 3. Es distinto de select, que conserva los elementos originales que cumplen la condición.",
  k=["filter_map combina transformación y filtrado.", "filter_map descarta resultados nil y false.", "filter_map está disponible desde Ruby 2.7."],
  sit="De una lista quieres conservar solo números pares y guardarlos divididos entre dos. ¿Qué método combina ambos pasos?",
  cod="""numeros = [2, 3, 4]
pares = numeros.filter_map { |n| n / 2 if n.even? }
puts pares.join(", ")""",
  h="filtra los pares y guarda la mitad de cada uno",
  pr=("El método que transforma y descarta resultados falsos o nil se llama ___. (filter_map)", "filter_map"),
  pr2=("filter_map está disponible desde Ruby ___. (2.7)", "2.7"),
  ec="esperar que filter_map descarte cualquier valor considerado falso en una condición",
  out="1, 2"),
K("Enumerador lazy",
  d="evaluación diferida de operaciones encadenadas sobre un Enumerable",
  u="evitar calcular resultados que no se van a consumir",
  mas="lazy transforma un Enumerable en un enumerador que calcula sus etapas cuando se solicitan valores. Operaciones como map y select se pueden encadenar y take limita cuántos resultados se consumen. En colecciones finitas, force materializa los resultados pendientes.",
  k=["lazy retrasa la evaluación de operaciones enumerables.", "take puede limitar los valores que se consumen.", "force materializa los resultados del enumerador lazy."],
  sit="Una transformación debe procesar solo los dos primeros resultados de una cadena de operaciones. ¿Qué modo de enumeración eliges?",
  cod="""resultado = [1, 2, 3, 4].lazy
  .map { |n| n * 10 }
  .take(2)
  .force
puts resultado.join(", ")""",
  h="transforma de forma diferida y materializa solo dos valores",
  pr=("La forma de evaluación diferida de Enumerable se inicia con ___. (lazy)", "lazy"),
  pr2=("force materializa los resultados que quedaron ___ . (pendientes)", "pendientes"),
  ec="esperar que lazy calcule todos los elementos antes de solicitar alguno",
  out="10, 20"),
K("Métodos endless",
  d="definición de método breve cuyo cuerpo aparece después de un igual",
  u="reducir sintaxis repetitiva en métodos de una sola expresión",
  mas="Ruby 3.0 incorporó definiciones endless con la forma def nombre = expresión. El valor de la expresión se convierte en el retorno del método. Esta forma no usa end y es adecuada para cuerpos breves, no para operaciones extensas.",
  k=["La sintaxis endless usa def nombre = expresión.", "Ruby 3.0 incorporó las definiciones endless.", "La expresión del cuerpo es el valor devuelto."],
  sit="Un método de una sola expresión calcula el cuadrado de un número y quieres escribirlo de forma compacta. ¿Qué sintaxis usas?",
  cod="""def cuadrado(n) = n * n
puts cuadrado(5)""",
  h="define y llama una función breve con sintaxis endless",
  pr=("La sintaxis de método breve de Ruby 3 se llama ___ . (endless)", "endless"),
  pr2=("Las definiciones endless se incorporaron en Ruby ___. (3.0)", "3.0"),
  ec="usar una definición endless para un método largo que sería más fácil de leer en varias líneas",
  out="25"),
K("Reenviar todos los argumentos",
  d="operador ... que reenvía argumentos y bloque a otro método",
  u="crear un método intermediario sin listar cada parámetro",
  mas="Una definición como def envolver(...) puede reenviar el conjunto de argumentos posicionales, keywords y bloque con super(...) o con otra llamada. Ruby incorporó este operador en 2.7. Facilita envoltorios, pero puede ocultar la interfaz exacta del método.",
  k=["... permite reenviar argumentos y bloque.", "El operador de reenvío se incorporó en Ruby 2.7.", "Un método envoltorio puede usar ... al delegar."],
  sit="Un método intermediario debe pasar sin cambios los argumentos y el bloque a otra operación. ¿Qué sintaxis usas?",
  cod="""def original(texto, prefijo:)
  "#{prefijo}#{texto}"
end
def envolver(...)
  original(...)
end
puts envolver("sol", prefijo: "ID-")""",
  h="reenvía argumento posicional y keyword al método original",
  pr=("La sintaxis que reenvía todos los argumentos de un método es ___. (...)", "..."),
  pr2=("El reenvío de argumentos se agregó en Ruby ___. (2.7)", "2.7"),
  ec="usar ... en un método que necesita modificar o validar cada argumento reenviado",
  out="ID-sol"),
K("Reenviar argumentos keyword",
  d="uso de ** para reunir y reenviar argumentos keyword como un Hash",
  u="adaptar opciones nombradas entre métodos intermediarios",
  mas="Un parámetro **opciones captura los argumentos keyword restantes en un Hash. Pasar **opciones a otra llamada los expande como keywords. Ruby 3 distingue keywords de hashes posicionales, por lo que la expansión explícita deja claro qué forma de argumentos se envía.",
  k=["**opciones reúne keyword arguments en un Hash.", "**opciones en una llamada expande un Hash a keywords.", "Ruby 3 separa los keywords de los hashes posicionales."],
  sit="Un envoltorio debe capturar opciones nombradas y enviarlas a otra función como keywords. ¿Qué operador aplicas?",
  cod="""def destino(color:)
  color
end
def envolver(**opciones)
  destino(**opciones)
end
puts envolver(color: "verde")""",
  h="captura y reenvía explícitamente una opción keyword",
  pr=("El prefijo que captura o expande un Hash de keywords es ___. (**)", "**"),
  pr2=("Los argumentos keyword se escriben con nombre y dos ___. (:)", "puntos"),
  ec="pasar un Hash posicional esperando que sustituya de forma implícita un keyword requerido",
  out="verde"),
K("Parámetros numerados de bloque",
  d="variables abreviadas _1, _2 y sucesivas para parámetros de bloque",
  u="escribir transformaciones breves sin declarar nombres de parámetros",
  mas="En bloques sin parámetros explícitos, _1 representa el primer argumento, _2 el segundo y así sucesivamente. La característica se añadió en Ruby 2.7. No se pueden mezclar con una lista explícita de parámetros en el mismo bloque.",
  k=["_1 referencia el primer argumento implícito del bloque.", "_2 referencia el segundo argumento implícito.", "Los parámetros numerados se añadieron en Ruby 2.7."],
  sit="Un bloque breve debe duplicar cada elemento y no necesita nombrar explícitamente su parámetro. ¿Qué abreviatura usas?",
  cod="""puts [2, 4].map { _1 * 2 }.join(", ")""",
  h="usa _1 para duplicar cada elemento",
  pr=("La variable abreviada del primer argumento de bloque es ___. (_1)", "_1"),
  pr2=("Los parámetros numerados de bloque se añadieron en Ruby ___. (2.7)", "2.7"),
  ec="combinar _1 con una declaración explícita de parámetros en el mismo bloque",
  out="4, 8"),
K("Objetos Method",
  d="valores Method que representan un método enlazado a su receptor",
  u="guardar una operación existente y llamarla posteriormente",
  mas="method(:nombre) devuelve un objeto Method enlazado al receptor actual. Puede invocarse con call y pasarse como valor a otro método. El objeto Method mantiene el receptor al que se obtuvo; no es una cadena con el nombre del método.",
  k=["method(:nombre) obtiene un objeto Method.", "Un objeto Method se puede invocar con call.", "Un objeto Method queda enlazado a su receptor."],
  sit="Quieres guardar una operación de texto existente y ejecutar después el método elegido. ¿Qué objeto obtienes?",
  cod="""mayusculas = "ruby".method(:upcase)
puts mayusculas.call
puts mayusculas.class""",
  h="guarda upcase como objeto Method y lo invoca",
  pr=("El valor que representa un método enlazado se llama objeto ___. (Method)", "Method"),
  pr2=("El objeto Method se ejecuta con el método ___. (call)", "call"),
  ec="confundir un objeto Method con el nombre del método como String",
  out="RUBY\nMethod"),
K("Llamar métodos con public_send",
  d="método que invoca dinámicamente un método público por nombre",
  u="seleccionar entre operaciones públicas de forma explícita",
  mas="public_send recibe el nombre del método y sus argumentos, pero respeta la visibilidad pública. A diferencia de send, no permite invocar métodos privados. Si el nombre procede de datos externos, debe validarse contra una lista permitida antes de usarlo.",
  k=["public_send invoca un método por nombre.", "public_send respeta la visibilidad pública.", "Un nombre de método dinámico debe validarse si proviene de entrada externa."],
  sit="Una operación seleccionada debe invocarse por nombre y no debe acceder a métodos privados. ¿Qué método dinámico usas?",
  cod="""texto = "ruby"
puts texto.public_send(:upcase)""",
  h="invoca públicamente upcase con un nombre de método símbolo",
  pr=("El método que invoca dinámicamente solo operaciones públicas es ___. (public_send)", "public_send"),
  pr2=("public_send respeta la ___ pública del método. (visibilidad)", "visibilidad"),
  ec="pasar nombres de métodos no validados desde datos externos a una invocación dinámica",
  out="RUBY"),
K("Definir métodos con define_method",
  d="método de Module que define una operación a partir de un bloque",
  u="generar métodos de instancia durante la definición de una clase",
  mas="define_method crea un método de instancia a partir de un bloque y se suele llamar en el contexto de la clase. El bloque conserva el entorno léxico donde fue creado. Es una herramienta dinámica que debe usarse con moderación para mantener clara la interfaz.",
  k=["define_method crea un método usando un bloque.", "El método definido pertenece a la clase en cuyo contexto se llama.", "El bloque de define_method puede conservar su entorno léxico."],
  sit="Una clase debe generar un lector cuyo nombre se decide en tiempo de definición. ¿Qué método metaprogramable aplicas?",
  cod="""class Estado
  define_method(:activo?) { true }
end
puts Estado.new.activo?""",
  h="define en la clase un predicado que devuelve true",
  pr=("El método de Module que define un método desde un bloque es ___. (define_method)", "define_method"),
  pr2=("El bloque de define_method conserva el entorno ___. (léxico)", "léxico", "lexico"),
  ec="generar métodos dinámicamente cuando una definición explícita sería más fácil de entender",
  out="true"),
K("Cambiar búsqueda con prepend",
  d="inserción de un módulo antes de la clase en la cadena de ancestros",
  u="envolver comportamiento heredado antes de delegar con super",
  mas="prepend coloca un módulo antes de la clase receptora en la cadena de búsqueda de métodos. Un método del módulo puede ejecutar lógica adicional y llamar super para continuar con la implementación de la clase. A diferencia de include, el módulo queda antes de ella.",
  k=["prepend coloca el módulo antes de la clase en la búsqueda.", "super desde el módulo continúa hacia el siguiente método.", "include y prepend producen órdenes de búsqueda diferentes."],
  sit="Un módulo debe envolver un método de la clase y luego continuar hacia su implementación original. ¿Qué mecanismo eliges?",
  cod="""module Registro
  def valor
    "log-" + super
  end
end
class Dato
  def valor
    "ok"
  end
  prepend Registro
end
puts Dato.new.valor""",
  h="antepone el texto del módulo antes del valor de la clase",
  pr=("El mecanismo que coloca un módulo antes de la clase es ___. (prepend)", "prepend"),
  pr2=("El módulo puede continuar la búsqueda de método llamando ___. (super)", "super"),
  ec="usar include cuando el módulo debe interceptar el método antes de la clase",
  out="log-ok"),
K("Refinamientos",
  d="mecanismo para modificar métodos de una clase en un ámbito léxico limitado",
  u="añadir comportamiento local sin alterar globalmente la clase",
  mas="Un refinement se declara con refine dentro de un módulo y se activa léxicamente con using. Solo afecta llamadas dentro del ámbito activado, no cambia globalmente la clase para todo el programa. Esta limitación evita que una modificación afecte código ajeno de forma inesperada.",
  k=["refine declara un refinamiento dentro de un módulo.", "using activa el refinamiento en su ámbito léxico.", "Un refinement no modifica globalmente el comportamiento de la clase."],
  sit="Un método adicional de Integer debe existir solo en un ámbito de código acotado. ¿Qué mecanismo eliges?",
  cod="""module DobleLocal
  refine Integer do
    def doble
      self * 2
    end
  end
end
using DobleLocal
puts 4.doble""",
  h="activa un método adicional de Integer en el ámbito actual",
  pr=("La palabra clave que declara una extensión léxica de clase es ___. (refine)", "refine"),
  pr2=("La palabra clave que activa un refinamiento es ___. (using)", "using"),
  ec="modificar una clase globalmente cuando solo se requiere un método local",
  out="8"),
K("Fibers cooperativas",
  d="mecanismo que suspende y reanuda una secuencia de ejecución explícitamente",
  u="dividir un flujo en pasos reanudables sin crear un hilo autónomo",
  mas="Fiber.new crea una fibra cuyo bloque se ejecuta al llamar resume. Fiber.yield suspende la fibra y entrega un valor al llamador; el siguiente resume continúa desde ese punto. La ejecución es cooperativa y explícita, no se alterna automáticamente como en un hilo.",
  k=["resume inicia o continúa la fibra.", "Fiber.yield suspende la ejecución y devuelve un valor.", "Una fibra se reanuda explícitamente y no es un hilo autónomo."],
  sit="Una secuencia debe pausar después de entregar un primer resultado y continuar solo cuando se reanude. ¿Qué mecanismo usas?",
  cod="""fibra = Fiber.new do
  Fiber.yield "pausa"
  "fin"
end
puts fibra.resume
puts fibra.resume""",
  h="reanuda una fibra antes y después de su pausa",
  pr=("El objeto cooperativo que se reanuda explícitamente es una ___. (Fiber)", "Fiber"),
  pr2=("La fibra se continúa llamando a ___. (resume)", "resume"),
  ec="esperar que una Fiber avance automáticamente sin llamar resume",
  out="pausa\nfin"),
K("Congelar objetos",
  d="estado que impide modificar directamente un objeto congelado",
  u="proteger un valor para que no reciba mutaciones posteriores",
  mas="freeze marca un objeto como inmodificable y devuelve el mismo objeto; frozen? comprueba ese estado. La congelación es superficial: congelar un Array no congela automáticamente los objetos mutables que contiene. Intentar modificar el objeto congelado genera FrozenError.",
  k=["freeze impide modificar directamente el objeto.", "frozen? informa si un objeto está congelado.", "freeze es superficial y no congela automáticamente objetos anidados."],
  sit="Una configuración de texto no debe cambiarse accidentalmente después de inicializarse. ¿Qué método aplicas?",
  cod="""configuracion = "solo lectura".freeze
puts configuracion.frozen?
puts configuracion""",
  h="congela un String y comprueba su estado",
  pr=("El método que congela directamente un objeto es ___. (freeze)", "freeze"),
  pr2=("La congelación de un arreglo es ___ respecto a sus elementos anidados. (superficial)", "superficial"),
  ec="creer que congelar un contenedor congela automáticamente todos sus objetos internos",
  out="true\nsolo lectura"),
]
