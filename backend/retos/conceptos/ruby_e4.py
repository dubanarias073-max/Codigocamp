"""Ruby · Etapa 4: clases, objetos, bloques y módulos."""
from ..generador import K

LISTA = [
K("Clases",
  d="plantillas que definen el comportamiento y la clase de los objetos",
  u="agrupar datos y operaciones que pertenecen a un mismo tipo",
  mas="class inicia la definición de una clase y end la cierra. Los objetos se crean al llamar a new. En Ruby, las clases también son objetos y forman parte de una jerarquía que parte de BasicObject y Object.",
  k=["class define una clase.", "new crea una instancia de una clase.", "Las clases Ruby también son objetos."],
  sit="Un programa necesita representar varias cuentas con el mismo conjunto de operaciones. ¿Qué estructura defines?",
  cod="""class Cuenta
  def saldo
    0
  end
end
puts Cuenta.new.saldo""",
  h="define una clase y consulta el saldo de una instancia",
  pr=("La palabra clave que comienza una definición de tipo Ruby es ___. (class)", "class"),
  pr2=("El método que normalmente crea una instancia es ___. (new)", "new"),
  ec="confundir la clase con una instancia creada a partir de ella",
  out="0"),
K("Bloques",
  d="fragmentos de código asociados a una llamada de método",
  u="pasar una acción breve que el método ejecuta por cada elemento",
  mas="Un bloque se escribe con do ... end o con llaves. Los parámetros del bloque se encierran entre barras verticales. Las llaves tienen mayor precedencia que do ... end en expresiones; el estilo habitual usa llaves para bloques cortos y do ... end para varios pasos.",
  k=["Un bloque se escribe con do ... end o con llaves.", "Los parámetros de un bloque se escriben entre barras verticales.", "Las llaves tienen mayor precedencia que do ... end."],
  sit="Quieres dar al método each una operación corta que se aplique a cada elemento. ¿Qué fragmento pasas?",
  cod="""[2, 4].each do |numero|
  puts numero
end""",
  h="pasa un bloque que muestra cada número",
  pr=("El fragmento de código asociado a una llamada se llama ___. (bloque)", "bloque"),
  pr2=("Los parámetros de un bloque se encierran entre ___ verticales. (barras)", "barras"),
  ec="olvidar delimitar los parámetros del bloque con barras verticales",
  out="2\n4"),
K("Constructor initialize",
  d="método de inicialización llamado automáticamente por new",
  u="preparar el estado inicial de cada objeto",
  mas="initialize se ejecuta cuando se llama a new y recibe los argumentos de construcción. No se invoca directamente en la creación habitual: Class#new crea la instancia y llama a initialize. Su valor de retorno no sustituye al objeto creado.",
  k=["new llama automáticamente a initialize.", "initialize recibe los argumentos usados al crear la instancia.", "initialize no determina el valor devuelto por new."],
  sit="Cada objeto de una clase debe guardar un nombre recibido al crearlo. ¿Qué método implementas?",
  cod="""class Saludo
  def initialize(nombre)
    @nombre = nombre
  end
  def texto
    "Hola, #{@nombre}"
  end
end
puts Saludo.new("Eva").texto""",
  h="inicializa un nombre y construye un saludo",
  pr=("El método llamado por new para inicializar una instancia es ___. (initialize)", "initialize"),
  pr2=("La creación habitual de una instancia comienza llamando a ___. (new)", "new"),
  ec="intentar usar el valor de retorno de initialize como si reemplazara la instancia",
  out="Hola, Eva"),
K("Variables de instancia",
  d="nombres iniciados con @ que guardan estado en cada objeto",
  u="mantener datos propios de cada instancia",
  mas="Una variable de instancia empieza con @ y pertenece al objeto que la usa. Dos instancias tienen estados separados aunque empleen el mismo nombre de variable. Leer una variable de instancia todavía no asignada devuelve nil.",
  k=["Una variable de instancia comienza con @.", "Cada objeto mantiene sus propias variables de instancia.", "Una variable de instancia no inicializada devuelve nil al leerse."],
  sit="Cada cuenta debe conservar un número de saldo independiente de las demás. ¿Qué clase de variable usas?",
  cod="""class Marcador
  def initialize(valor)
    @valor = valor
  end
  def valor
    @valor
  end
end
puts Marcador.new(8).valor""",
  h="guarda y consulta un valor de instancia",
  pr=("El prefijo de una variable de instancia Ruby es ___. (@)", "@"),
  pr2=("El estado de instancia pertenece a cada ___ creado. (objeto)", "objeto"),
  ec="usar una variable local dentro de initialize esperando conservarla como estado del objeto",
  out="8"),
K("Lector attr_reader",
  d="macro que define un método lector para una variable de instancia",
  u="exponer la lectura de un atributo sin escribir un método repetitivo",
  mas="attr_reader :nombre define un método nombre que devuelve @nombre. Es una macro de clase que crea métodos; no declara un campo con tipo ni expone una escritura. Es útil cuando el estado debe poder consultarse pero no asignarse desde fuera.",
  k=["attr_reader crea un método lector.", "El lector nombre devuelve el valor de @nombre.", "attr_reader no define un método escritor."],
  sit="Una clase debe permitir consultar el nombre de una persona, pero no asignarlo desde fuera. ¿Qué macro declaras?",
  cod="""class Usuario
  attr_reader :nombre
  def initialize(nombre)
    @nombre = nombre
  end
end
puts Usuario.new("Uma").nombre""",
  h="define un lector para el nombre de usuario",
  pr=("La macro que define un método de lectura es ___. (attr_reader)", "attr_reader"),
  pr2=("attr_reader devuelve el contenido de la variable de instancia @___. (nombre)", "nombre"),
  ec="esperar que attr_reader genere también un método de asignación",
  out="Uma"),
K("Acceso attr_accessor",
  d="macro que define métodos lector y escritor para un atributo",
  u="leer y actualizar un atributo con una interfaz breve",
  mas="attr_accessor :nivel genera los métodos nivel y nivel=. La asignación con objeto.nivel = valor llama al escritor generado. Esto es cómodo, pero para validar valores antes de guardarlos conviene definir explícitamente un escritor.",
  k=["attr_accessor crea un lector y un escritor.", "El método escritor generado termina con =.", "Un escritor explícito permite validar antes de asignar."],
  sit="Un objeto necesita que se lea y actualice directamente su nivel sin validación adicional. ¿Qué macro usas?",
  cod="""class Juego
  attr_accessor :nivel
end
juego = Juego.new
juego.nivel = 2
puts juego.nivel""",
  h="asigna y lee un atributo generado",
  pr=("La macro que crea un lector y un escritor es ___. (attr_accessor)", "attr_accessor"),
  pr2=("El escritor generado para nivel termina con el signo ___. (=)", "="),
  ec="usar attr_accessor cuando el atributo requiere validar cada asignación",
  out="2"),
K("El receptor self",
  d="referencia al objeto que recibe la llamada actual",
  u="consultar el receptor y aclarar llamadas de métodos",
  mas="Dentro de un método de instancia, self es el objeto receptor. En el cuerpo de una clase, self es la clase mientras se ejecutan las expresiones de definición. self también se usa explícitamente para llamar a un escritor propio, como self.nombre = valor.",
  k=["En un método de instancia, self referencia al receptor.", "En el cuerpo de clase, self referencia a la clase actual.", "self puede aclarar una llamada a un escritor."],
  sit="Un método debe comprobar que su receptor es el mismo objeto que se pasó como argumento. ¿Qué referencia consulta?",
  cod="""class Identidad
  def mismo?(otro)
    self.equal?(otro)
  end
end
objeto = Identidad.new
puts objeto.mismo?(objeto)""",
  h="compara el receptor actual con el mismo objeto",
  pr=("La palabra que referencia al receptor actual es ___. (self)", "self"),
  pr2=("Dentro de un método de instancia, self es el ___ que recibió la llamada. (receptor)", "receptor"),
  ec="confundir self con la clase cuando se está dentro de un método de instancia",
  out="true"),
K("Métodos de clase",
  d="métodos definidos en la clase y llamados sin crear una instancia",
  u="ofrecer operaciones relacionadas con una clase completa",
  mas="La forma def self.nombre define un método singleton sobre la clase y se invoca como Clase.nombre. Ruby no declara métodos estáticos de la misma manera que algunos otros lenguajes; el método pertenece al objeto clase.",
  k=["def self.nombre define un método sobre el objeto clase.", "Un método de clase se llama con el nombre de la clase como receptor.", "Las clases Ruby son objetos."],
  sit="Quieres calcular un valor usando la clase como receptor, sin construir un objeto. ¿Qué método defines?",
  cod="""class Medida
  def self.unidad
    "cm"
  end
end
puts Medida.unidad""",
  h="define y llama un método en el objeto clase",
  pr=("La forma habitual de definir un método sobre la clase es def ___. (self.nombre)", "self.nombre"),
  pr2=("Un método de clase se llama sin crear una ___. (instancia)", "instancia"),
  ec="intentar llamar un método de instancia directamente en el nombre de la clase",
  out="cm"),
K("Herencia",
  d="relación donde una subclase deriva comportamiento de una superclase",
  u="especializar una clase conservando comportamiento heredado",
  mas="Una clase puede heredar de una superclase con el operador <. La subclase hereda métodos y puede agregar o redefinir comportamiento. En Ruby una clase solo tiene una superclase directa, aunque puede incorporar comportamiento de módulos.",
  k=["El operador < indica herencia de clases.", "Una subclase hereda métodos de su superclase.", "Una clase Ruby tiene una sola superclase directa."],
  sit="Un tipo de bicicleta debe conservar operaciones generales de vehículo y agregar las suyas. ¿Qué relación modelas?",
  cod="""class Vehiculo
  def ruedas
    2
  end
end
class Bicicleta < Vehiculo
end
puts Bicicleta.new.ruedas""",
  h="hereda ruedas desde Vehiculo a Bicicleta",
  pr=("La relación entre una subclase y su clase base se expresa con el operador ___. (<)", "<"),
  pr2=("Una clase Ruby puede tener una superclase directa. (¿Cuántas?)", "una", "1"),
  ec="duplicar métodos heredados en lugar de especializar la clase base",
  out="2"),
K("Llamar super",
  d="palabra clave que invoca la implementación heredada del método",
  u="extender el comportamiento de un método sobrescrito",
  mas="super llama al método de igual nombre encontrado en la jerarquía superior. Sin paréntesis ni argumentos, reenvía los argumentos actuales; super() llama explícitamente sin argumentos. Es común usarlo en initialize y en métodos sobrescritos.",
  k=["super llama a una implementación heredada.", "super sin argumentos explícitos reenvía los argumentos actuales.", "super() llama a la implementación heredada sin argumentos."],
  sit="Una subclase redefine un mensaje y luego quiere añadir el resultado de la clase base. ¿Qué palabra clave usa?",
  cod="""class Base
  def sonido
    "base"
  end
end
class Derivada < Base
  def sonido
    super + " mejorado"
  end
end
puts Derivada.new.sonido""",
  h="extiende el texto que devuelve la implementación heredada",
  pr=("La palabra clave para invocar una implementación heredada es ___. (super)", "super"),
  pr2=("super() reenvía ___ argumentos al método base. (cero)", "cero", "0"),
  ec="usar super() cuando se pretende reenviar los argumentos actuales",
  out="base mejorado"),
K("Polimorfismo por respuesta",
  d="uso de objetos distintos mediante una misma operación disponible",
  u="escribir código que depende del comportamiento y no de la clase exacta",
  mas="En Ruby es habitual el duck typing: una operación se usa si el objeto responde al método requerido. Distintas clases pueden implementar hablar y ser procesadas por el mismo código. Esto no significa que todas las llamadas sean seguras, por lo que la interfaz esperada debe estar clara.",
  k=["El duck typing se centra en los métodos que responde un objeto.", "Objetos de clases distintas pueden ofrecer la misma operación.", "respond_to? permite comprobar si un objeto responde a un método."],
  sit="Un proceso debe llamar hablar sobre varios objetos sin exigir que sean de la misma clase. ¿Qué enfoque usas?",
  cod="""class Gato
  def hablar
    "miau"
  end
end
class Robot
  def hablar
    "bip"
  end
end
puts [Gato.new, Robot.new].map { |ser| ser.hablar }.join(", ")""",
  h="invoca una operación común en dos clases diferentes",
  pr=("El estilo que se guía por las operaciones disponibles se llama ___ typing. (duck)", "duck"),
  pr2=("respond_to? comprueba si el objeto responde a un ___. (método)", "método"),
  ec="comprobar la clase exacta cuando basta con usar una interfaz de comportamiento",
  out="miau, bip"),
K("Composición de objetos",
  d="diseño donde un objeto contiene y delega tareas a otros objetos",
  u="combinar responsabilidades sin crear una jerarquía de herencia",
  mas="La composición construye un objeto a partir de otros objetos que colaboran. Un reproductor puede guardar un motor y delegarle la operación iniciar. Esto facilita cambiar una pieza sin alterar una jerarquía de clases.",
  k=["La composición expresa relaciones de colaboración entre objetos.", "Un objeto puede delegar operaciones a una pieza que contiene.", "La composición es una alternativa a la herencia."],
  sit="Un reproductor necesita usar un motor intercambiable sin ser un tipo de motor. ¿Qué diseño eliges?",
  cod="""class Motor
  def iniciar
    "motor listo"
  end
end
class Reproductor
  def initialize
    @motor = Motor.new
  end
  def estado
    @motor.iniciar
  end
end
puts Reproductor.new.estado""",
  h="construye un reproductor que delega en su motor",
  pr=("El diseño que combina objetos colaboradores se llama ___. (composición)", "composición", "composicion"),
  pr2=("Delegar significa encargar una operación a otro ___. (objeto)", "objeto"),
  ec="usar herencia para representar una relación de «tiene un»",
  out="motor listo"),
K("Módulos como espacios de nombres",
  d="contenedores que agrupan constantes, clases y métodos relacionados",
  u="organizar nombres y evitar colisiones entre clases",
  mas="Un módulo agrupa nombres dentro de un espacio, como Tienda::Producto. El operador :: accede a una constante o clase anidada. Los módulos también pueden aportar comportamiento mediante mixins, pero este concepto se centra en organizar el espacio de nombres.",
  k=["module define un módulo.", "El operador :: accede a nombres dentro de un espacio de nombres.", "Los módulos ayudan a evitar colisiones entre nombres."],
  sit="Dos partes de un programa podrían definir una clase Producto y necesitan mantener sus nombres separados. ¿Qué estructura las agrupa?",
  cod="""module Tienda
  class Producto
    def nombre
      "taza"
    end
  end
end
puts Tienda::Producto.new.nombre""",
  h="define una clase dentro de un módulo y la consulta con ::",
  pr=("La palabra clave que define un espacio de nombres es ___. (module)", "module"),
  pr2=("El operador que accede a una clase anidada es ___. (::)", "::"),
  ec="olvidar el módulo al referenciar una constante anidada fuera de él",
  out="taza"),
K("Incluir un mixin",
  d="uso de include para agregar métodos de un módulo a instancias",
  u="compartir comportamiento entre clases sin heredar de una clase base",
  mas="include agrega el módulo a la cadena de ancestros de la clase y hace disponibles sus métodos de instancia. Una clase puede incluir varios módulos. El orden de inclusión influye en la búsqueda de métodos.",
  k=["include incorpora métodos de instancia de un módulo.", "El módulo aparece en la cadena de ancestros.", "El orden de inclusión afecta la búsqueda de métodos."],
  sit="Dos clases no relacionadas necesitan compartir el mismo método de instancia. ¿Qué mecanismo aplicas?",
  cod="""module Saludable
  def mensaje
    "todo bien"
  end
end
class Persona
  include Saludable
end
puts Persona.new.mensaje""",
  h="incorpora un método de módulo a las instancias de Persona",
  pr=("La palabra clave que incorpora un mixin a instancias es ___. (include)", "include"),
  pr2=("Los métodos incorporados con include suelen ser métodos de ___. (instancia)", "instancia"),
  ec="usar include esperando llamar el método como método de clase",
  out="todo bien"),
K("Extender con módulos",
  d="uso de extend para añadir métodos del módulo a un objeto receptor",
  u="agregar capacidades de módulo al objeto clase",
  mas="extend añade los métodos de instancia del módulo como métodos singleton del receptor. Cuando el receptor es una clase, esos métodos se pueden invocar en el nombre de la clase. No es lo mismo que include, que incorpora métodos a las instancias.",
  k=["extend añade métodos singleton al receptor.", "extend sobre una clase permite llamarlos en la clase.", "include incorpora métodos a instancias, no a la clase receptora."],
  sit="Una clase necesita una operación de módulo invocable directamente en el nombre de la clase. ¿Qué palabra clave usas?",
  cod="""module Identificable
  def tipo
    "documento"
  end
end
class Archivo
  extend Identificable
end
puts Archivo.tipo""",
  h="agrega y llama un método singleton en Archivo",
  pr=("La palabra clave que añade métodos singleton del módulo es ___. (extend)", "extend"),
  pr2=("extend agrega métodos al objeto que actúa como ___. (receptor)", "receptor"),
  ec="confundir extend con include al decidir si el método va en la clase o en sus instancias",
  out="documento"),
K("Constantes de módulo",
  d="nombres constantes accesibles mediante el módulo que los contiene",
  u="agrupar valores fijos y clases bajo un espacio de nombres",
  mas="Las constantes de Ruby empiezan con mayúscula. Dentro de un módulo se acceden como Modulo::NOMBRE desde fuera. Los nombres completamente en mayúsculas con guion bajo son una convención frecuente para constantes.",
  k=["Los nombres de constantes comienzan con mayúscula.", "El operador :: accede a una constante dentro de un módulo.", "Las constantes de módulo quedan asociadas a su espacio de nombres."],
  sit="Una tasa fija debe tener un nombre propio dentro del módulo Finanzas para evitar colisiones. ¿Cómo la declaras?",
  cod="""module Finanzas
  TASA = 3
end
puts Finanzas::TASA""",
  h="declara una constante de módulo y la consulta desde fuera",
  pr=("La constante de módulo se consulta con el operador ___. (::)", "::"),
  pr2=("Los nombres de constantes Ruby comienzan con letra ___. (mayúscula)", "mayúscula", "mayuscula"),
  ec="referenciar una constante de módulo sin incluir su espacio de nombres cuando hace falta",
  out="3"),
K("Métodos privados",
  d="métodos de instancia que no se llaman con un receptor explícito normal",
  u="mantener operaciones internas fuera de la interfaz pública",
  mas="private cambia la visibilidad de los métodos definidos después de él en el contexto de clase. Una llamada privada suele hacerse sin receptor explícito, dentro del mismo objeto. En Ruby moderno existen formas limitadas de llamadas explícitas privadas, pero la regla de diseño es mantenerlas como detalles internos.",
  k=["private cambia la visibilidad de métodos.", "Un método privado se llama normalmente sin receptor explícito.", "La visibilidad ayuda a separar interfaz pública e implementación."],
  sit="Una clase tiene un cálculo auxiliar que no debe ser parte de su interfaz pública. ¿Qué visibilidad asignas?",
  cod="""class Secreto
  private
  def clave
    "interna"
  end
end
puts Secreto.new.respond_to?(:clave)""",
  h="comprueba que el método privado no aparece como respuesta pública",
  pr=("La palabra clave que marca métodos no públicos es ___. (private)", "private"),
  pr2=("Un método private se invoca normalmente sin receptor ___. (explícito)", "explícito", "explicito"),
  ec="marcar como privado un método que forma parte de la interfaz pública necesaria",
  out="false"),
K("Métodos protegidos",
  d="métodos accesibles desde instancias de la clase y sus descendientes",
  u="permitir colaboración interna entre objetos relacionados por herencia",
  mas="protected hace que un método pueda ser llamado sin receptor explícito o con un receptor de self del mismo contexto de clase o de una subclase. Su uso es menos común que public y private; una API pública suele ser más simple cuando basta con ellos.",
  k=["protected limita el método a contextos relacionados con la clase.", "Una subclase puede usar métodos protegidos heredados.", "protected es distinto de private y public."],
  sit="Una subclase debe llamar una operación heredada que no quieres exponer como pública. ¿Qué visibilidad declaras?",
  cod="""class Base
  protected
  def codigo
    "X"
  end
end
class Hija < Base
  def codigo_base
    codigo
  end
end
puts Hija.new.codigo_base""",
  h="llama un método protegido heredado desde una subclase",
  pr=("La visibilidad para una operación de uso interno entre clases relacionadas es ___. (protected)", "protected"),
  pr2=("Una subclase puede usar un método protegido que fue ___. (heredado)", "heredado"),
  ec="hacer protected un método solo porque no se conoce la diferencia con private",
  out="X"),
K("Estructura Struct",
  d="clase compacta para crear objetos con un conjunto fijo de miembros",
  u="representar registros sencillos sin escribir una clase completa",
  mas="Struct.new crea una clase cuyos miembros se especifican al construirla. Sus instancias ofrecen lectores y escritores para esos miembros y comparación por valores. Es apropiado para registros simples; para reglas de negocio extensas suele ser mejor definir una clase explícita.",
  k=["Struct.new crea una clase de registro.", "Los miembros de Struct reciben lectores y escritores.", "Struct resulta útil para objetos simples con campos fijos."],
  sit="Un punto sencillo solo necesita coordenadas x e y y no reglas adicionales. ¿Qué herramienta eliges?",
  cod="""Punto = Struct.new(:x, :y)
punto = Punto.new(3, 4)
puts punto.x
puts punto.y""",
  h="crea un registro de punto y consulta sus dos miembros",
  pr=("La herramienta que crea clases compactas de registro es ___. (Struct)", "Struct"),
  pr2=("Los miembros de Struct.new se indican como ___. (:x)", "símbolos", "simbolos"),
  ec="usar Struct para ocultar un modelo con reglas complejas que necesita métodos propios",
  out="3\n4"),
K("Igualdad personalizada",
  d="redefinición de == para comparar el valor significativo de objetos",
  u="hacer que instancias equivalentes se consideren iguales",
  mas="La igualdad de == depende de la clase y puede sobrescribirse. Al definirla, conviene comprobar el tipo de la otra instancia y comparar los atributos que representan el valor. No es necesario ni correcto confundirla con equal?, que comprueba identidad.",
  k=["== se puede redefinir en una clase.", "Una implementación de igualdad debe comparar el estado relevante.", "equal? sigue comprobando identidad del objeto."],
  sit="Dos puntos creados por separado deben considerarse iguales si sus coordenadas coinciden. ¿Qué método redefinirías?",
  cod="""class Punto
  def initialize(x)
    @x = x
  end
  def ==(otro)
    otro.is_a?(Punto) && @x == otro.instance_variable_get(:@x)
  end
end
puts Punto.new(2) == Punto.new(2)""",
  h="compara el estado de dos puntos del mismo tipo",
  pr=("El método que expresa igualdad de valor en Ruby es ___. (==)", "=="),
  pr2=("equal? comprueba identidad, no igualdad de ___. (valor)", "valor"),
  ec="redefinir == sin comprobar que el otro objeto admite la comparación",
  out="true"),
]
