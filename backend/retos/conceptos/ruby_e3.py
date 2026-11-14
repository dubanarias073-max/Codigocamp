"""Ruby · Etapa 3: métodos, bloques y control del programa."""
from ..generador import K

LISTA = [
K("Métodos",
  d="procedimientos nombrados que reúnen instrucciones reutilizables",
  u="organizar una operación y llamarla desde distintos lugares",
  mas="Un método se define con def y termina con end. Se llama por su nombre y puede recibir argumentos. Ruby permite omitir paréntesis en muchas llamadas, aunque usarlos puede aclarar los límites de los argumentos.",
  k=["def inicia la definición de un método.", "Un método termina con end.", "Un método puede recibir argumentos y devolver un valor."],
  sit="Una operación de saludo se repite y quieres darle un nombre que puedas invocar. ¿Qué construyes?",
  cod="""def saludar
  puts "Hola"
end
saludar""",
  h="define e invoca un método que saluda",
  pr=("La palabra clave que inicia una definición de método Ruby es ___. (3 letras)", "def"),
  pr2=("El método definido se invoca escribiendo su ___. (nombre)", "nombre"),
  ec="definir un método sin llamarlo y esperar que su cuerpo se ejecute",
  out="Hola"),
K("Colecciones",
  d="objetos enumerables que ofrecen consultas agregadas sobre sus elementos",
  u="preguntar propiedades del conjunto sin escribir un bucle manual",
  mas="Enumerable proporciona operaciones de consulta a colecciones como Array. any? responde si algún elemento cumple una condición; all? responde si todos la cumplen; count puede contar elementos coincidentes. Estas consultas suelen detenerse pronto si el resultado ya se conoce.",
  k=["any? comprueba si algún elemento cumple la condición.", "all? comprueba si todos los elementos cumplen la condición.", "Enumerable comparte operaciones entre distintas colecciones."],
  sit="Necesitas saber si una lista contiene al menos una calificación aprobatoria. ¿Qué consulta enumerable aplicas?",
  cod="""notas = [5, 8, 6]
puts notas.any? { |nota| nota >= 7 }
puts notas.all? { |nota| nota >= 7 }""",
  h="comprueba si alguna y si todas las notas son aprobatorias",
  pr=("La consulta que responde true si algún elemento coincide es ___. (any?)", "any?"),
  pr2=("La consulta que requiere que cada elemento coincida es ___. (all?)", "all?"),
  ec="usar all? cuando solo se necesita saber si al menos un elemento coincide",
  out="true\nfalse"),
K("Argumentos posicionales",
  d="valores asociados a parámetros por el orden en que se pasan",
  u="dar datos de entrada a un método de forma explícita",
  mas="Los argumentos posicionales se asignan a parámetros de izquierda a derecha. La llamada debe proporcionar la cantidad requerida, a menos que la definición use parámetros opcionales o un splat. Nombres descriptivos de parámetros hacen más clara la definición.",
  k=["Los argumentos posicionales se emparejan por orden.", "La definición del método declara sus parámetros.", "Omitir un argumento obligatorio produce ArgumentError."],
  sit="Un método recibe primero una cantidad y después una unidad; el orden de entrada es importante. ¿Qué clase de argumentos usas?",
  cod="""def etiqueta(valor, unidad)
  puts "#{valor} #{unidad}"
end
etiqueta(5, "kg")""",
  h="asocia dos valores posicionales con sus parámetros",
  pr=("Los argumentos asociados por su posición son argumentos ___. (11 letras)", "posicionales"),
  pr2=("El orden de argumentos posicionales importa en la ___ del método. (llamada)", "llamada"),
  ec="pasar los argumentos posicionales en un orden distinto al esperado",
  out="5 kg"),
K("Argumentos opcionales",
  d="parámetros que tienen un valor predeterminado en la definición",
  u="permitir omitir una entrada cuando existe un valor razonable",
  mas="Un parámetro puede tener un valor predeterminado mediante nombre = valor. Si el llamador omite ese argumento, se usa el valor predeterminado; si lo proporciona, el valor recibido prevalece. Los parámetros opcionales suelen ubicarse después de los requeridos.",
  k=["Un parámetro opcional define un valor predeterminado.", "El llamador puede omitir el argumento opcional.", "Un argumento proporcionado sustituye el valor predeterminado."],
  sit="Un método debe usar una cantidad predeterminada de saludos si no se especifica otra. ¿Qué parámetro declaras?",
  cod="""def repetir(texto, veces = 2)
  puts texto * veces
end
repetir("ja")""",
  h="usa dos repeticiones al omitir el parámetro veces",
  pr=("Un parámetro con valor asignado en la definición es ___. (opcional)", "opcional"),
  pr2=("El valor indicado en la definición se usa si el argumento se ___. (omite)", "omite"),
  ec="colocar un parámetro obligatorio después de uno opcional posicional",
  out="jaja"),
K("Argumentos con nombre",
  d="argumentos keyword identificados por una etiqueta en la llamada",
  u="hacer explícito qué significa cada valor enviado a un método",
  mas="Los parámetros keyword se definen con dos puntos, como titulo:. La llamada indica el nombre del argumento, por lo que su orden puede variar. Desde Ruby 3, los argumentos keyword y los hash posicionales se manejan de forma separada en las llamadas a métodos.",
  k=["Los parámetros keyword se definen con nombre:.", "La llamada identifica cada argumento con su nombre.", "Ruby 3 separa los keyword arguments de los hash posicionales."],
  sit="Un método recibe un título y un color, y quieres que la llamada deje claro cada valor. ¿Qué argumentos usas?",
  cod="""def ficha(titulo:, color:)
  puts "#{titulo}: #{color}"
end
ficha(color: "azul", titulo: "Cielo")""",
  h="pasa dos argumentos keyword en orden distinto al de la definición",
  pr=("Los argumentos identificados por etiquetas son argumentos ___. (keyword)", "keyword"),
  pr2=("En Ruby 3, los keywords se separan de los hashes ___. (posicionales)", "posicionales"),
  ec="suponer que un Hash posicional siempre sustituye automáticamente todos los keywords requeridos",
  out="Cielo: azul"),
K("Parámetro splat",
  d="parámetro con * que reúne argumentos posicionales restantes en un Array",
  u="aceptar una cantidad variable de valores en un método",
  mas="Un parámetro como *valores reúne en un arreglo los argumentos posicionales sobrantes. Puede haber un único splat posicional en una definición. Al invocar un método también se puede anteponer * a un arreglo para expandir sus elementos como argumentos.",
  k=["*nombre en una definición reúne argumentos en un Array.", "El parámetro splat acepta una cantidad variable de argumentos.", "Anteponer * a un arreglo en una llamada expande sus elementos."],
  sit="Una suma debe aceptar una cantidad no fija de números. ¿Qué tipo de parámetro agregas?",
  cod="""def sumar(*numeros)
  numeros.sum
end
puts sumar(2, 3, 4)""",
  h="reúne tres números y muestra su suma",
  pr=("El parámetro prefijado con * que reúne valores se llama ___. (splat)", "splat"),
  pr2=("El parámetro splat reúne sus argumentos en un ___. (Array)", "Array"),
  ec="tratar el arreglo reunido por *numeros como si fuera un solo número",
  out="9"),
K("Retorno de un método",
  d="valor que una llamada a método entrega al código que la invoca",
  u="componer operaciones a partir de resultados calculados",
  mas="En Ruby, el valor de la última expresión evaluada en un método se devuelve automáticamente. puts devuelve nil, así que un método cuyo último paso solo imprime no devuelve el texto impreso. Distinguir la salida mostrada del valor de retorno evita errores de composición.",
  k=["Ruby devuelve implícitamente la última expresión del método.", "puts muestra texto, pero su valor de retorno es nil.", "El valor devuelto puede guardarse o usarse en otra expresión."],
  sit="Una función debe entregar el resultado de una multiplicación para que otra línea lo guarde. ¿Qué valor devuelve?",
  cod="""def doble(numero)
  numero * 2
end
puts doble(6)""",
  h="devuelve el producto de duplicar el número recibido",
  pr=("Por defecto, Ruby devuelve la ___ expresión del método. (última)", "última", "ultima"),
  pr2=("El valor de retorno de puts es ___. (nil)", "nil"),
  ec="suponer que imprimir un resultado equivale a devolverlo desde el método",
  out="12"),
K("Retorno explícito",
  d="uso de return para terminar un método y entregar un valor",
  u="salir temprano de un método cuando se cumple una condición",
  mas="return finaliza la ejecución del método actual y entrega el valor indicado. También se puede omitir el valor, en cuyo caso devuelve nil. Para un único resultado al final, el retorno implícito suele ser la forma idiomática.",
  k=["return termina el método actual inmediatamente.", "return puede entregar un valor al llamador.", "Sin valor explícito, return devuelve nil."],
  sit="Un método debe detenerse y devolver cero en cuanto recibe un número negativo. ¿Qué instrucción usas?",
  cod="""def absoluto_simple(numero)
  return 0 if numero < 0
  numero
end
puts absoluto_simple(-3)""",
  h="sale temprano y entrega cero para la entrada negativa",
  pr=("La palabra clave que termina un método y devuelve un valor es ___. (6 letras)", "return"),
  pr2=("Un return sin valor explícito devuelve ___. (nil)", "nil"),
  ec="colocar instrucciones después de un return esperando que se ejecuten",
  out="0"),
K("Bloque pasado con &",
  d="conversión de un bloque asociado a un parámetro Proc con &",
  u="guardar un bloque en un nombre y llamarlo explícitamente",
  mas="Un parámetro final escrito como &bloque convierte el bloque asociado a la llamada en un objeto Proc. Dentro del método se puede invocar con call. A la inversa, anteponer & a un Proc en la llamada lo pasa como bloque.",
  k=["&bloque convierte el bloque asociado en un Proc.", "El Proc recibido se puede invocar con call.", "Anteponer & a un Proc permite pasarlo como bloque a un método."],
  sit="Un método debe recibir un bloque y ejecutarlo más tarde desde su cuerpo. ¿Qué parámetro declaras?",
  cod="""def aplicar(&bloque)
  puts bloque.call(3)
end
aplicar { |numero| numero * 2 }""",
  h="convierte un bloque en Proc y lo llama con tres",
  pr=("El parámetro con prefijo & que captura un bloque es ___. (bloque)", "&bloque"),
  pr2=("Un Proc se puede ejecutar mediante el método ___. (call)", "call"),
  ec="olvidar que el bloque capturado se invoca explícitamente con call",
  out="6"),
K("Delegar con yield",
  d="instrucción que ejecuta el bloque entregado a un método",
  u="permitir que quien llama defina una acción dentro de un método",
  mas="yield transfiere el control al bloque que se pasó al método y luego continúa después de ese bloque. Si no se entrega uno, yield genera LocalJumpError. block_given? permite comprobar si hay un bloque antes de cederle el control.",
  k=["yield ejecuta el bloque asociado a la llamada.", "Tras ejecutar el bloque, el método continúa después de yield.", "block_given? comprueba si se proporcionó un bloque."],
  sit="Un método debe ejecutar una acción elegida por quien lo llama y continuar después. ¿Qué palabra clave usas?",
  cod="""def envolver
  puts "inicio"
  yield
  puts "fin"
end
envolver { puts "acción" }""",
  h="ejecuta el bloque entre dos mensajes del método",
  pr=("La instrucción que cede el control al bloque es ___. (5 letras)", "yield"),
  pr2=("block_given? responde si se proporcionó un ___. (bloque)", "bloque"),
  ec="llamar yield sin comprobar si el método recibió un bloque",
  out="inicio\nacción\nfin"),
K("Lambda",
  d="objeto Proc con reglas estrictas de argumentos y retorno local",
  u="representar una función anónima con aridad controlada",
  mas="Una lambda se crea con -> y puede invocarse con call. Comprueba estrictamente la cantidad de argumentos y return dentro de ella vuelve de la propia lambda, no del método que la contiene. Puede almacenarse en una variable y pasarse a otros métodos.",
  k=["-> crea una lambda.", "Las lambdas validan estrictamente la cantidad de argumentos.", "return dentro de una lambda retorna de esa lambda."],
  sit="Necesitas guardar una función anónima que exija exactamente un argumento. ¿Qué objeto creas?",
  cod="""duplicar = ->(numero) { numero * 2 }
puts duplicar.call(5)
puts duplicar.lambda?""",
  h="invoca una lambda y comprueba su tipo de Proc",
  pr=("El literal -> que crea una función anónima produce una ___. (lambda)", "lambda"),
  pr2=("Una lambda comprueba de manera estricta la cantidad de ___. (argumentos)", "argumentos"),
  ec="confundir una lambda con un Proc común al depender de sus reglas de argumentos",
  out="10\ntrue"),
K("Proc común",
  d="objeto Proc que encapsula un bloque con reglas flexibles de llamada",
  u="guardar un bloque como objeto reutilizable",
  mas="Proc.new crea un objeto Proc a partir de un bloque. A diferencia de una lambda, un Proc común es permisivo con la cantidad de argumentos: los que falten se vuelven nil y los sobrantes se ignoran. Su comportamiento de return también difiere, por lo que debe usarse con cuidado.",
  k=["Proc.new convierte un bloque en objeto Proc.", "Un Proc común no exige estrictamente la aridad como una lambda.", "Los argumentos faltantes de un Proc común pueden ser nil."],
  sit="Quieres guardar una operación de bloque en una variable para invocarla después. ¿Qué objeto usas?",
  cod="""saludo = Proc.new { |nombre| "Hola, #{nombre}" }
puts saludo.call("Ivo")""",
  h="guarda y ejecuta un bloque que construye un saludo",
  pr=("El objeto que encapsula un bloque se llama ___. (4 letras)", "Proc"),
  pr2=("Proc.new crea un objeto a partir de un ___. (bloque)", "bloque"),
  ec="suponer que un Proc común exige el mismo número exacto de argumentos que una lambda",
  out="Hola, Ivo"),
K("Cierre léxico",
  d="función que conserva acceso a variables de su ámbito de creación",
  u="crear operaciones que recuerdan el estado que las rodeaba",
  mas="Los bloques, lambdas y Proc pueden acceder a variables visibles en el lugar donde se crean. Ese acceso persiste aunque la ejecución haya salido del ámbito original; por eso un cierre puede mantener estado. No es lo mismo que una variable global.",
  k=["Un cierre conserva acceso a variables del ámbito donde se creó.", "Una lambda puede capturar una variable local.", "El estado capturado no necesita convertirse en global."],
  sit="Una función anónima debe usar el prefijo guardado cuando fue creada. ¿Qué propiedad del bloque aprovechas?",
  cod="""prefijo = "ID-"
crear_id = ->(numero) { "#{prefijo}#{numero}" }
puts crear_id.call(7)""",
  h="usa la variable local capturada por la lambda",
  pr=("Una función que conserva variables de su ámbito de creación se llama ___. (cierre)", "cierre"),
  pr2=("El nombre de la técnica de captura de entorno se relaciona con el ámbito ___. (léxico)", "léxico", "lexico"),
  ec="suponer que una función anónima pierde las variables locales capturadas al terminar su línea",
  out="ID-7"),
K("Condición inversa con unless",
  d="condicional que ejecuta su bloque cuando la condición es falsa",
  u="expresar de manera directa una acción para un caso no cumplido",
  mas="unless es la forma inversa de if: ejecuta el bloque si la condición es falsa. Puede llevar else, aunque condiciones complejas suelen ser más legibles con if. unless también tiene una forma modificadora para una instrucción sencilla.",
  k=["unless ejecuta su bloque cuando la condición es falsa.", "unless termina con end cuando se escribe como bloque.", "if suele ser más claro para condiciones con varias ramas."],
  sit="Debes mostrar una alerta solo cuando la cuenta no está activa. ¿Qué condicional inverso puedes usar?",
  cod="""activo = false
unless activo
  puts "cuenta pausada"
end""",
  h="muestra una alerta porque la cuenta no está activa",
  pr=("La estructura que ejecuta su bloque si la condición es falsa es ___. (unless)", "unless"),
  pr2=("unless es la forma ___ de if. (inversa)", "inversa"),
  ec="usar unless con una condición negativa difícil de leer",
  out="cuenta pausada"),
K("Elegir con case",
  d="estructura de selección que compara un valor con varias alternativas",
  u="elegir una rama según patrones o valores posibles",
  mas="case evalúa sus cláusulas when en orden y ejecuta la primera que coincide; else cubre el resto. En Ruby, las comparaciones de when suelen usar ===, así que los rangos y clases también pueden funcionar como patrones de caso.",
  k=["when introduce una alternativa de case.", "Se ejecuta la primera cláusula when coincidente.", "else cubre los casos restantes."],
  sit="Una puntuación debe clasificarse con varias alternativas mutuamente excluyentes. ¿Qué estructura eliges?",
  cod="""nota = 2
case nota
when 1 then puts "baja"
when 2 then puts "media"
else puts "alta"
end""",
  h="selecciona la categoría correspondiente al valor dos",
  pr=("La palabra clave que presenta cada alternativa de case es ___. (4 letras)", "when"),
  pr2=("La rama que cubre las alternativas restantes se introduce con ___. (else)", "else"),
  ec="olvidar que solo se ejecuta la primera alternativa coincidente",
  out="media"),
K("Operador ternario",
  d="expresión condicional breve con condición ? valor1 : valor2",
  u="elegir entre dos valores en una expresión sencilla",
  mas="El operador ternario evalúa una condición y produce el valor situado después de ? si es verdadera, o después de : si es falsa. Como es una expresión, su resultado puede asignarse. Para ramas extensas conviene usar if/else.",
  k=["La forma ternaria es condición ? valor_si : valor_no.", "El operador ternario produce uno de dos valores.", "if/else suele ser más legible para varias instrucciones."],
  sit="Una etiqueta debe ser \"par\" o \"impar\" según una condición simple. ¿Qué expresión breve eliges?",
  cod="""numero = 6
tipo = numero.even? ? "par" : "impar"
puts tipo""",
  h="elige el texto según si el número es par",
  pr=("El operador ternario usa los signos ___ y ___. (?, :)","?", ":"),
  pr2=("El ternario elige uno de ___ valores. (dos)", "dos"),
  ec="usar ternarios anidados en vez de escribir una decisión clara",
  out="par"),
K("Bucle while",
  d="bucle que repite mientras su condición sea verdadera",
  u="repetir una acción mientras siga vigente una condición",
  mas="while comprueba su condición antes de cada iteración. Si inicialmente es falsa, el cuerpo no se ejecuta. Es importante modificar dentro del ciclo el estado que hace que la condición termine para evitar un bucle infinito.",
  k=["while comprueba la condición antes de cada repetición.", "El cuerpo puede no ejecutarse si la condición inicial es falsa.", "Actualizar el estado del ciclo ayuda a que termine."],
  sit="Debes seguir aumentando un contador mientras sea menor que tres. ¿Qué bucle se ajusta?",
  cod="""contador = 0
while contador < 3
  puts contador
  contador += 1
end""",
  h="muestra el contador mientras su valor sea menor que tres",
  pr=("El bucle que repite mientras una condición sea verdadera es ___. (while)", "while"),
  pr2=("while comprueba la condición antes de ejecutar el ___. (cuerpo)", "cuerpo"),
  ec="olvidar actualizar la condición y dejar un bucle infinito",
  out="0\n1\n2"),
K("Bucle until",
  d="bucle que repite hasta que su condición se vuelve verdadera",
  u="expresar una repetición que termina al cumplirse una condición",
  mas="until es la forma inversa de while: repite mientras la condición sea falsa y termina cuando es verdadera. También comprueba la condición antes de entrar al cuerpo. La forma modificadora begin ... end until comprueba después, pero debe usarse con atención.",
  k=["until repite mientras su condición sea falsa.", "El bucle until termina cuando la condición es verdadera.", "until normal comprueba la condición antes del cuerpo."],
  sit="Un contador debe avanzar y repetir hasta alcanzar el valor tres. ¿Qué bucle expresa la condición final?",
  cod="""contador = 0
until contador == 3
  contador += 1
end
puts contador""",
  h="incrementa hasta que contador alcanza tres",
  pr=("La estructura que repite hasta que una condición se cumple es ___. (until)", "until"),
  pr2=("until se detiene cuando su condición es ___. (verdadera)", "verdadera"),
  ec="poner una condición que nunca pueda llegar a ser verdadera",
  out="3"),
K("Salir con break",
  d="instrucción que termina de inmediato el bucle más cercano",
  u="detener una búsqueda cuando ya se encontró el resultado",
  mas="break abandona el bucle actual sin completar las iteraciones restantes. Puede devolver un valor cuando se usa dentro de una expresión de iteración. No equivale a next, que solo salta a la siguiente iteración.",
  k=["break termina el bucle más cercano.", "Las instrucciones posteriores al bucle continúan ejecutándose.", "next salta una iteración sin terminar el bucle."],
  sit="Una búsqueda debe detener el recorrido cuando encuentra el primer número mayor que cuatro. ¿Qué instrucción usas?",
  cod="""[2, 5, 8].each do |numero|
  break if numero > 4
  puts numero
end""",
  h="termina el recorrido antes de imprimir el primer valor mayor que cuatro",
  pr=("La palabra clave que termina el bucle actual es ___. (5 letras)", "break"),
  pr2=("Para saltar una iteración y continuar se usa ___, no break. (next)", "next"),
  ec="usar break cuando solo se necesita omitir la iteración actual",
  out="2"),
K("Saltar con next",
  d="instrucción que omite el resto de la iteración actual",
  u="filtrar procesamiento dentro de un bucle sin detenerlo",
  mas="next interrumpe la iteración actual y continúa con la siguiente. A diferencia de break, no termina el bucle. En un bloque iterador, next devuelve el control al mecanismo que avanza al siguiente elemento.",
  k=["next omite el resto de la iteración actual.", "El bucle continúa con el siguiente elemento después de next.", "break termina el bucle, a diferencia de next."],
  sit="Un recorrido debe ignorar el valor cero y seguir revisando los demás. ¿Qué instrucción empleas?",
  cod="""[0, 1, 2].each do |numero|
  next if numero == 0
  puts numero
end""",
  h="omite cero y muestra los siguientes valores",
  pr=("La palabra clave que omite la iteración actual es ___. (4 letras)", "next"),
  pr2=("next continúa con la ___ iteración. (siguiente)", "siguiente"),
  ec="usar next esperando que detenga el ciclo completo",
  out="1\n2"),
]
