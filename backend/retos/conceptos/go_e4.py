"""Go · Etapa 4: estructuras, tipos e interfaces."""
from ..generador import K

LISTA = [
K("Structs", d="tipos compuestos que agrupan campos con nombre", u="representar entidades con varios datos relacionados", mas="Un struct define campos con nombre y tipo, y sus valores se inicializan con un literal compuesto. Se accede a cada campo con punto. Los campos exportados comienzan con mayúscula y los demás son privados al paquete.",
  k=["Un struct agrupa campos nombrados.", "Los campos se consultan con la notación punto.", "Los nombres de campos exportados comienzan con mayúscula."],
  sit="Quieres representar una ubicación guardando en un solo valor su nombre y su población. ¿Qué tipo compuesto definirías?",
  cod="""package main

import "fmt"

type Ciudad struct {
    Nombre string
    Poblacion int
}

func main() {
    ciudad := Ciudad{Nombre: "Lima", Poblacion: 10}
    fmt.Println(ciudad.Nombre, ciudad.Poblacion)
}""", h="define una ciudad y muestra dos campos", pr=("El tipo que agrupa campos con nombre se llama ___. (6 letras)", "struct"), pr2=("Los campos de un struct se leen con la notación de ___. (5 letras)", "punto"), ec="omitir el tipo o el nombre de un campo en la definición del struct", out="Lima 10"),
K("Punteros", d="valores que contienen la dirección de memoria de otro valor", u="compartir o modificar un valor a través de su dirección", mas="Un puntero de tipo *T puede apuntar a un valor de tipo T. El operador & obtiene una dirección y * accede al valor apuntado. El valor cero de un puntero es nil, y desreferenciar nil provoca un panic.",
  k=["& obtiene la dirección de una variable.", "* desreferencia un puntero para acceder al valor.", "El valor cero de un puntero es nil."],
  sit="Una función necesita modificar el entero original mediante su dirección, no solo una copia. ¿Qué tipo de valor le pasarías?",
  cod="""package main

import "fmt"

func main() {
    numero := 7
    puntero := &numero
    *puntero = 9
    fmt.Println(numero)
}""", h="cambia un entero al escribir a través de su puntero", pr=("El operador que obtiene la dirección de una variable es ___. (un carácter)", "&"), pr2=("El valor cero de un puntero se llama ___. (3 letras)", "nil"), ec="desreferenciar un puntero nil", out="9"),
K("Métodos con valor receptor", d="funciones asociadas a un tipo mediante un receptor pasado por valor", u="definir operaciones que pertenecen a un tipo", mas="Un método declara un receptor entre la palabra func y su nombre. Con receptor por valor, el método opera sobre una copia del valor receptor. Los métodos pueden llamarse usando la notación punto, igual que los campos de un struct.",
  k=["Un método declara su receptor junto a func.", "Un receptor por valor recibe una copia.", "Los métodos se invocan con notación punto."],
  sit="Quieres asociar a un tipo Rectangulo una operación que calcula su área sin modificarlo. ¿Qué declararías?",
  cod="""package main

import "fmt"

type Rectangulo struct{ Ancho, Alto int }

func (r Rectangulo) Area() int {
    return r.Ancho * r.Alto
}

func main() {
    fmt.Println(Rectangulo{3, 4}.Area())
}""", h="calcula el área con un método que recibe el rectángulo por valor", pr=("Una función asociada a un tipo por medio de un receptor es un ___. (6 letras)", "método", "metodo"), pr2=("Un receptor de valor recibe una ___. (5 letras)", "copia"), ec="creer que cambiar el receptor por valor modifica el struct original", out="12"),
K("Métodos con puntero receptor", d="métodos cuyo receptor es un puntero al valor del tipo", u="modificar el valor receptor sin copiar toda la estructura", mas="Un receptor *T permite que el método modifique el valor original. Go puede tomar la dirección automáticamente al llamar un método con puntero receptor sobre una variable direccionable. El conjunto de métodos de T y *T no es idéntico, lo que afecta la implementación de interfaces.",
  k=["Un receptor *T puede modificar el valor apuntado.", "Go puede tomar la dirección de una variable para una llamada adecuada.", "Los conjuntos de métodos de T y *T pueden diferir."],
  sit="Un método debe cambiar el saldo del mismo objeto que lo recibe. ¿Qué clase de receptor declararías?",
  cod="""package main

import "fmt"

type Cuenta struct{ Saldo int }

func (c *Cuenta) Depositar(monto int) {
    c.Saldo += monto
}

func main() {
    cuenta := Cuenta{Saldo: 5}
    cuenta.Depositar(3)
    fmt.Println(cuenta.Saldo)
}""", h="modifica el saldo de la cuenta mediante un receptor puntero", pr=("El tipo de receptor que permite modificar el valor original es un receptor ___. (7 letras)", "puntero"), pr2=("La firma del método modificador usa *Cuenta como ___. (8 letras)", "receptor"), ec="declarar un receptor por valor cuando se quiere modificar el original", out="8"),
K("Interfaces", d="tipos que especifican un conjunto de métodos requeridos", u="describir comportamientos que varios tipos pueden ofrecer", mas="Una interfaz contiene firmas de métodos, no datos de instancia. Un valor de interfaz puede guardar un valor concreto que implemente sus métodos. La interfaz vacía interface{} no requiere métodos; desde Go 1.18 se puede escribir any como alias.",
  k=["Una interfaz especifica firmas de métodos.", "Un valor concreto puede almacenarse en una interfaz.", "any es un alias de interface{} disponible desde Go 1.18."],
  sit="Quieres definir un tipo que describa cualquier objeto capaz de dibujarse, sin decidir su implementación concreta. ¿Qué declararías?",
  cod="""package main

import "fmt"

type Dibujable interface {
    Dibujar() string
}

type Circulo struct{}

func (Circulo) Dibujar() string { return "círculo" }

func main() {
    var figura Dibujable = Circulo{}
    fmt.Println(figura.Dibujar())
}""", h="almacena un círculo que cumple una interfaz de comportamiento", pr=("Un tipo que declara firmas de métodos se llama ___. (8 letras)", "interfaz"), pr2=("La interfaz Dibujable exige el método ___. (7 letras)", "Dibujar"), ec="intentar declarar campos de datos dentro de una interfaz ordinaria", out="círculo"),
K("Implementación implícita", d="satisfacción de interfaz al definir todos sus métodos sin declaración especial", u="desacoplar una interfaz de los tipos concretos", mas="Go no tiene una cláusula explícita como implements. Un tipo satisface una interfaz si su conjunto de métodos contiene todas las firmas requeridas. Esto permite que interfaces y tipos se definan en paquetes distintos sin modificar el tipo para cada interfaz.",
  k=["Go no requiere escribir implements para satisfacer una interfaz.", "La implementación se determina por el conjunto de métodos.", "Un tipo puede satisfacer varias interfaces."],
  sit="Un tipo ya tiene todos los métodos exigidos por una interfaz y no quieres modificar su declaración. ¿Cómo la satisface?",
  cod="""package main

import "fmt"

type Sonoro interface{ Sonar() string }
type Campana struct{}

func (Campana) Sonar() string { return "din" }

func reproducir(s Sonoro) { fmt.Println(s.Sonar()) }

func main() { reproducir(Campana{}) }""", h="pasa un tipo a una interfaz que satisface implícitamente", pr=("Go reconoce interfaces por sus métodos, sin declarar ___. (10 letras)", "implements"), pr2=("Campana satisface Sonoro porque tiene el método ___. (5 letras)", "Sonar"), ec="buscar una palabra clave implements obligatoria en Go", out="din"),
K("Composición de interfaces", d="interfaz que combina los métodos de otras interfaces", u="construir contratos de comportamiento a partir de piezas", mas="Una interfaz puede incluir otras interfaces dentro de su declaración. La interfaz resultante exige todos los métodos de cada parte incluida. La biblioteca estándar usa este patrón para combinar capacidades pequeñas, como lectura y escritura.",
  k=["Una interfaz puede incluir otras interfaces.", "La interfaz compuesta requiere los métodos de todos sus componentes.", "La biblioteca estándar compone interfaces pequeñas para describir capacidades."],
  sit="Un tipo debe cumplir dos contratos de comportamiento pequeños al mismo tiempo y quieres nombrar el contrato combinado. ¿Qué usarías?",
  cod="""package main

import "fmt"

type Lector interface{ Leer() string }
type Cerrador interface{ Cerrar() string }
type Recurso interface {
    Lector
    Cerrador
}
type Caja struct{}

func (Caja) Leer() string { return "leer" }
func (Caja) Cerrar() string { return "cerrar" }

func mostrar(recurso Recurso) {
    fmt.Println(recurso.Leer(), recurso.Cerrar())
}

func main() { mostrar(Caja{}) }""", h="usa un valor que implementa las dos interfaces incluidas", pr=("Una interfaz que incluye otras combina sus ___. (7 letras)", "métodos"), pr2=("La interfaz Recurso reúne Lector y ___. (8 letras)", "Cerrador"), ec="olvidar que la interfaz compuesta exige todos los métodos incluidos", out="leer cerrar"),
K("Aserción de tipo", d="operación que consulta o extrae el tipo concreto de un valor de interfaz", u="recuperar un valor concreto guardado en una interfaz", mas="La expresión valor, ok := interfaz.(T) comprueba si el valor dinámico es de tipo T sin provocar panic si no coincide. La forma interfaz.(T) de un solo resultado sí provoca panic ante una discrepancia. Las aserciones solo se permiten sobre valores de interfaz.",
  k=["Una aserción de tipo extrae o comprueba el tipo dinámico.", "La forma de dos resultados evita panic si el tipo no coincide.", "Las aserciones se aplican a valores de interfaz."],
  sit="Quieres comprobar si un valor de interfaz contiene un string y manejar con seguridad el caso contrario. ¿Qué operación usarías?",
  cod="""package main

import "fmt"

func main() {
    var valor any = "Go"
    texto, ok := valor.(string)
    fmt.Println(texto, ok)
}""", h="extrae con seguridad una cadena desde una interfaz", pr=("La operación interfaz.(T) que obtiene un tipo dinámico se llama aserción de ___. (4 letras)", "tipo"), pr2=("La forma de dos resultados devuelve un booleano de comprobación llamado normalmente ___. (2 letras)", "ok"), ec="usar la aserción de un solo resultado sin garantizar que el tipo coincida", out="Go true"),
K("Type switch", d="sentencia switch que elige ramas según el tipo dinámico de una interfaz", u="procesar distintos tipos concretos con un mismo parámetro de interfaz", mas="Un type switch usa la forma switch v := x.(type) y enumera tipos en los case. En cada rama, v tiene el tipo correspondiente al caso. La expresión x debe ser un valor de interfaz.",
  k=["Un type switch usa la expresión especial x.(type).", "Cada case puede nombrar un tipo concreto.", "La variable declarada en el switch adopta el tipo del caso."],
  sit="Una función recibe valores de interfaz y debe aplicar una respuesta distinta según el tipo concreto. ¿Qué estructura usarías?",
  cod="""package main

import "fmt"

func describir(valor any) string {
    switch v := valor.(type) {
    case int:
        return fmt.Sprintf("entero %d", v)
    case string:
        return "texto " + v
    default:
        return "otro"
    }
}

func main() { fmt.Println(describir(5), describir("Go")) }""", h="elige una descripción según el tipo dinámico", pr=("La forma de switch que selecciona por tipo se llama ___ switch. (4 letras)", "type"), pr2=("En un type switch, la variable local recibe el tipo de cada ___. (4 letras)", "case"), ec="escribir un type switch sobre un valor que no es de interfaz", out="entero 5 texto Go"),
K("Embedding de structs", d="inclusión de un tipo como campo sin nombre para promover sus miembros", u="reutilizar campos y métodos dentro de otro struct", mas="Al incluir un tipo sin nombre explícito en un struct, sus campos y métodos promovidos pueden accederse desde el struct contenedor. El valor embebido sigue siendo un campo interno y puede nombrarse por el tipo. La composición por embedding no crea herencia de clases.",
  k=["Un struct puede incluir un campo de tipo embebido.", "Los campos y métodos del tipo embebido pueden promoverse.", "Embedding es composición, no herencia de clases."],
  sit="Quieres reutilizar los datos y métodos de un tipo Dirección dentro de Cliente, sin copiar sus campos manualmente. ¿Qué técnica aplicarías?",
  cod="""package main

import "fmt"

type Direccion struct{ Ciudad string }
type Cliente struct {
    Nombre string
    Direccion
}

func main() {
    c := Cliente{Nombre: "Ana", Direccion: Direccion{Ciudad: "Quito"}}
    fmt.Println(c.Nombre, c.Ciudad)
}""", h="accede a un campo promovido desde un struct embebido", pr=("La inclusión de un tipo sin campo nombrado explícitamente se llama ___. (9 letras)", "embedding"), pr2=("Un struct embebido ofrece composición, no ___. (8 letras)", "herencia"), ec="tratar el embedding como si creara herencia de clases", out="Ana Quito"),
K("Tipos definidos", d="tipos nuevos basados en un tipo subyacente mediante type Nombre Tipo", u="dar significado y operaciones propias a valores existentes", mas="type Metros float64 crea un tipo definido distinto de float64, aunque comparta su representación subyacente. No se convierte implícitamente con el tipo original. Los métodos permiten asociar comportamiento al tipo definido.",
  k=["type Nombre Tipo declara un tipo definido nuevo.", "El tipo definido es distinto de su tipo subyacente.", "Se pueden declarar métodos para tipos definidos del paquete."],
  sit="Una cantidad en metros debe ser distinta de un float64 común para evitar mezclas accidentales. ¿Qué declararías?",
  cod="""package main

import "fmt"

type Metros float64

func main() {
    altura := Metros(1.75)
    fmt.Printf("%.2f\\n", altura)
}""", h="declara y muestra un tipo de medida definido", pr=("La declaración type Nombre Tipo crea un tipo ___. (8 letras)", "definido"), pr2=("El tipo base de Metros en el ejemplo es ___. (7 caracteres)", "float64"), ec="creer que dos tipos definidos distintos siempre se asignan entre sí sin conversión", out="1.75"),
K("Alias de tipo", d="nombre alternativo que representa exactamente el mismo tipo", u="aclarar o simplificar un nombre de tipo", mas="Un alias se declara con type Nombre = Tipo y no crea un tipo nuevo. El signo igual lo distingue de una definición de tipo. Un valor del tipo original se puede usar directamente mediante su alias.",
  k=["Un alias se declara con el signo igual tras el nombre.", "El alias y el tipo original son el mismo tipo.", "Un tipo definido nuevo no es lo mismo que un alias."],
  sit="Quieres ofrecer un nombre alternativo para un tipo sin crear incompatibilidades ni conversiones. ¿Qué declararías?",
  cod="""package main

import "fmt"

type Identificador = int

func main() {
    var id Identificador = 42
    var numero int = id
    fmt.Println(numero)
}""", h="usa un alias int como el mismo tipo int", pr=("Un nombre alternativo del mismo tipo se llama ___. (5 letras)", "alias"), pr2=("En type Identificador = int, el signo igual indica que es un ___. (5 letras)", "alias"), ec="confundir un alias con un tipo definido nuevo sin signo igual", out="42"),
K("Constantes iota", d="identificador que genera una secuencia de constantes enteras en una declaración const", u="enumerar estados o categorías con nombres", mas="iota comienza en cero y aumenta en uno en cada línea de una declaración const. Cada bloque const reinicia su contador. Es una herramienta idiomática para declarar conjuntos de constantes relacionadas, aunque el tipo puede quedar implícito.",
  k=["iota inicia su secuencia en cero.", "Su valor aumenta en cada línea de una declaración const.", "Cada bloque const comienza una secuencia nueva."],
  sit="Quieres declarar estados enteros consecutivos con nombres en un mismo bloque const. ¿Qué identificador usarías?",
  cod="""package main

import "fmt"

const (
    Pendiente = iota
    EnCurso
    Terminado
)

func main() { fmt.Println(Pendiente, EnCurso, Terminado) }""", h="asigna valores consecutivos a tres estados", pr=("El identificador que enumera constantes en Go es ___. (4 letras)", "iota"), pr2=("La primera constante del bloque obtiene el valor ___. (un número)", "0", "cero"), ec="esperar que iota empiece desde uno en cada bloque const", out="0 1 2"),
K("Interfaz error", d="interfaz estándar que representa un resultado de error", u="comunicar fallos como valores que el llamador puede revisar", mas="La interfaz predefinida error requiere el método Error() string. Una función que puede fallar suele devolver un error como último resultado y usa nil cuando no hay fallo. Quien llama debe revisar explícitamente el valor recibido.",
  k=["error es una interfaz con el método Error() string.", "Una operación exitosa suele devolver error nil.", "El llamador decide cómo manejar un error recibido."],
  sit="Una función puede fallar y debe comunicar el motivo sin detener por sí sola el programa. ¿Qué valor de la biblioteca estándar devolvería?",
  cod="""package main

import (
    "errors"
    "fmt"
)

func validar(n int) error {
    if n < 0 {
        return errors.New("negativo")
    }
    return nil
}

func main() { fmt.Println(validar(-1)) }""", h="devuelve un valor de error cuando el entero es negativo", pr=("La interfaz que representa fallos en Go se llama ___. (5 letras)", "error"), pr2=("El método requerido por error es Error que devuelve un ___. (6 letras)", "string"), ec="ignorar el resultado error que una función puede devolver", out="negativo"),
K("Errores definidos", d="tipos propios que implementan la interfaz error", u="incluir datos estructurados en un fallo", mas="Un tipo puede convertirse en error al definir el método Error() string con un receptor adecuado. Los errores estructurados pueden guardar campos como un código o el valor rechazado. El llamador puede inspeccionar esos datos mediante una aserción o errors.As.",
  k=["Un tipo satisface error al implementar Error() string.", "Un error definido puede guardar datos estructurados.", "errors.As permite localizar un tipo de error en una cadena de errores."],
  sit="Un fallo debe comunicar su mensaje y conservar el número inválido para que el llamador lo inspeccione. ¿Qué declararías?",
  cod="""package main

import "fmt"

type RangoError struct{ Valor int }

func (e RangoError) Error() string {
    return fmt.Sprintf("fuera de rango: %d", e.Valor)
}

func main() { fmt.Println(RangoError{Valor: 12}) }""", h="define un error que incluye el valor no aceptado", pr=("Un tipo propio implementa error con el método Error que devuelve ___. (6 letras)", "string"), pr2=("RangoError conserva el dato en un campo llamado ___. (5 letras)", "Valor"), ec="devolver un mensaje sin conservar ningún dato útil del error", out="fuera de rango: 12"),
K("fmt.Errorf", d="función que construye errores formateados con contexto", u="añadir valores dinámicos a un mensaje de error", mas="fmt.Errorf construye un error aplicando formato a los argumentos. El verbo %w envuelve un error existente para mantener su relación causal y permitir inspeccionarlo después con errors.Is o errors.As. Un error envuelto debe manejarse o propagarse de forma deliberada.",
  k=["fmt.Errorf crea errores con formato.", "%w envuelve otro error y conserva su cadena.", "errors.Is y errors.As pueden inspeccionar errores envueltos."],
  sit="Una operación debe añadir el nombre de un archivo al mensaje de un error previo y conservar su causa. ¿Qué función usarías?",
  cod="""package main

import (
    "errors"
    "fmt"
)

func main() {
    causa := errors.New("sin permiso")
    err := fmt.Errorf("abrir datos: %w", causa)
    fmt.Println(err)
}""", h="envuelve un error con contexto adicional", pr=("El verbo de fmt.Errorf que envuelve un error es ___. (2 caracteres)", "%w"), pr2=("La función de formato de errores pertenece al paquete ___. (3 letras)", "fmt"), ec="usar %v en vez de %w cuando se necesita conservar la causa", out="abrir datos: sin permiso"),
K("errors.Is", d="función que busca si una causa de error coincide con un valor objetivo", u="comprobar errores envueltos sin comparar sus mensajes", mas="errors.Is recorre la cadena de errores y busca una coincidencia con el error objetivo. La comparación puede usar igualdad o el método Is de un error personalizado. No conviene analizar el texto del mensaje para decidir cómo manejar un error.",
  k=["errors.Is comprueba la cadena de errores envueltos.", "La función compara errores centinela sin examinar su texto.", "Un tipo personalizado puede definir su método Is."],
  sit="Un error pudo envolverse varias veces, pero necesitas saber si su causa es io.EOF. ¿Qué función consultarías?",
  cod="""package main

import (
    "errors"
    "fmt"
)

func main() {
    causa := errors.New("sin permiso")
    envuelto := fmt.Errorf("leer: %w", causa)
    fmt.Println(errors.Is(envuelto, causa))
}""", h="comprueba que el error original permanece en la cadena", pr=("La función que busca una causa de error envuelta se llama errors.___. (2 letras)", "Is"), pr2=("El método personalizado opcional que puede usar errors.Is también se llama ___. (2 letras)", "Is"), ec="comparar el texto del error en lugar de comprobar su identidad o causa", out="true"),
K("panic", d="mecanismo que detiene el flujo normal y comienza a desenrollar la pila", u="señalar una condición excepcional irrecuperable o un error de programación", mas="panic detiene la ejecución normal de la goroutine actual y ejecuta las funciones diferidas en orden inverso. Si no se recupera, el programa termina mostrando información de la pila. Para fallos esperados, Go suele preferir devolver un error.",
  k=["panic inicia el desenrollado de la pila de la goroutine actual.", "Las funciones defer se ejecutan mientras ocurre el desenrollado.", "Los errores esperados suelen comunicarse con valores error."],
  sit="Una condición imposible de recuperar debe interrumpir el flujo normal y ejecutar las funciones diferidas. ¿Qué mecanismo existe?",
  cod="""package main

import "fmt"

func disparar() {
    defer func() {
        fmt.Println("recuperado", recover())
    }()
    panic("fallo")
}

func main() {
    fmt.Println("inicia")
    disparar()
    fmt.Println("continúa")
}""", h="recupera un panic y continúa la ejecución de main", pr=("El mecanismo que inicia el desenrollado de pila se llama ___. (5 letras)", "panic"), pr2=("Antes de terminar o recuperarse, panic ejecuta las funciones ___. (5 letras)", "defer"), ec="usar panic para manejar un error de entrada que debería devolverse normalmente", out="inicia\nrecuperado fallo\ncontinúa"),
K("recover", d="función integrada que permite recuperar un panic durante una llamada defer", u="capturar una interrupción excepcional en un límite controlado", mas="recover devuelve el valor pasado a panic y detiene el desenrollado si se llama desde una función diferida de la misma goroutine. Fuera de ese contexto devuelve nil y no tiene efecto. recover debe reservarse para límites donde el programa pueda recuperarse con seguridad.",
  k=["recover puede detener un panic si se llama desde una función defer.", "recover devuelve el valor usado para provocar el panic.", "recover no captura panics de otra goroutine."],
  sit="Una frontera del programa necesita capturar un panic de la misma goroutine dentro de una función diferida. ¿Qué función usarías?",
  cod="""package main

import "fmt"

func seguro() {
    defer func() {
        fmt.Println(recover())
    }()
    panic("capturado")
}

func main() { seguro() }""", h="recupera un panic desde una función diferida", pr=("La función integrada que captura un panic en defer es ___. (7 letras)", "recover"), pr2=("recover tiene efecto cuando se ejecuta desde una función ___. (5 letras)", "defer"), ec="llamar recover fuera de una función defer y esperar que detenga un panic", out="capturado"),
K("defer", d="sentencia que programa la ejecución de una llamada al salir de la función", u="garantizar una limpieza local al terminar una operación", mas="Una llamada defer se ejecuta justo antes de que retorne la función que la contiene, incluso si termina por panic. Varias llamadas defer se ejecutan en orden LIFO, es decir, la última programada se ejecuta primero. Los argumentos de la llamada diferida se evalúan al llegar al defer.",
  k=["defer programa una llamada para el retorno de la función actual.", "Varias llamadas diferidas se ejecutan en orden LIFO.", "Los argumentos de una llamada defer se evalúan al declararla."],
  sit="Quieres garantizar que una acción de limpieza se ejecute al abandonar una función, aunque haya varios caminos de salida. ¿Qué sentencia usarías?",
  cod="""package main

import "fmt"

func proceso() {
    defer fmt.Println("cierre")
    fmt.Println("trabajo")
}

func main() { proceso() }""", h="imprime el trabajo y luego la acción diferida", pr=("La sentencia para programar una llamada al salir de la función es ___. (5 letras)", "defer"), pr2=("Las llamadas defer se ejecutan en orden ___: la última primero. (4 letras)", "LIFO"), ec="esperar que defer se ejecute al final de todo el programa y no al salir de la función", out="trabajo\ncierre"),
]
