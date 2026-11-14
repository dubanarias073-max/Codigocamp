"""Go · Etapa 3: funciones y colecciones."""
from ..generador import K

LISTA = [
K("Funciones", d="bloques reutilizables que realizan una tarea con nombre", u="organizar el programa y evitar repetir instrucciones", mas="Una función se declara con func, puede recibir parámetros y puede devolver resultados. Su cuerpo se ejecuta cuando se la llama. Go permite tener varias funciones en un mismo paquete, siempre que sus nombres sean distintos.",
  k=["Las funciones se declaran con func.", "Una función se ejecuta cuando se la llama.", "Las funciones pueden recibir parámetros y devolver resultados."],
  sit="Quieres dar un nombre a un bloque reutilizable que realiza una tarea y luego llamarlo desde main. ¿Qué definirías?",
  cod="""package main

import "fmt"

func saludar() {
    fmt.Println("Hola")
}

func main() {
    saludar()
}""", h="define una función sin parámetros y la ejecuta", pr=("La palabra clave para declarar una función de Go es ___. (4 letras)", "func"), pr2=("Para ejecutar una función se la debe ___. (6 letras)", "llamar"), ec="definir una función y asumir que se ejecuta automáticamente", out="Hola"),
K("Colecciones", d="estructuras que agrupan varios valores para recorrerlos o consultarlos", u="trabajar con conjuntos de datos relacionados", mas="Go ofrece arrays de tamaño fijo, slices de tamaño dinámico y mapas de pares clave-valor. Los arrays y slices guardan elementos indexados; un mapa permite buscar por clave. Cada colección tiene reglas distintas de tamaño, almacenamiento y uso.",
  k=["Los arrays y slices almacenan elementos indexados.", "Los mapas relacionan claves con valores.", "Los arrays tienen tamaño fijo y los slices pueden crecer."],
  sit="Necesitas agrupar varios valores y elegir entre posiciones numeradas o búsquedas por clave. ¿Qué familia de tipos estudiarías?",
  cod="""package main

import "fmt"

func main() {
    numeros := [3]int{4, 5, 6}
    colores := []string{"rojo", "azul"}
    edades := map[string]int{"Eva": 9}
    fmt.Println(numeros[1], colores[0], edades["Eva"])
}""", h="lee valores de un array, un slice y un mapa", pr=("Las estructuras de Go que agrupan valores se llaman ___. (11 letras)", "colecciones"), pr2=("Un mapa almacena pares de clave y ___. (7 letras)", "valores"), ec="confundir un slice redimensionable con un array de longitud fija", out="5 rojo 9"),
K("Parámetros", d="nombres y tipos que reciben los valores al llamar una función", u="proporcionar datos de entrada a una operación reutilizable", mas="Los parámetros se declaran entre paréntesis con su tipo. Varios parámetros consecutivos del mismo tipo pueden compartir una anotación, como func sumar(a, b int). Go pasa argumentos por valor; un puntero o el almacenamiento compartido de un slice permite acceder a los datos originales.",
  k=["Los parámetros se declaran con un tipo en la firma.", "Parámetros contiguos pueden compartir la anotación del tipo.", "Go pasa los argumentos por valor."],
  sit="Una operación de suma debe recibir dos números enteros cada vez que se la llama. ¿Qué declararías en su firma?",
  cod="""package main

import "fmt"

func sumar(a, b int) int {
    return a + b
}

func main() {
    fmt.Println(sumar(3, 4))
}""", h="recibe dos enteros y muestra su suma", pr=("Los valores de entrada de una función se declaran como ___. (10 letras)", "parámetros", "parametros"), pr2=("En func sumar(a, b int), los dos argumentos son de tipo ___. (3 letras)", "int"), ec="omitir el tipo de un parámetro en la declaración de una función", out="7"),
K("return", d="sentencia que termina una función y entrega su resultado", u="devolver un valor calculado al código que llamó", mas="Una función con tipo de resultado debe devolver un valor compatible usando return. Al ejecutarse, return termina inmediatamente la función actual. Una función que no declara resultados puede terminar al llegar al final de su cuerpo.",
  k=["return entrega el resultado de una función.", "Una función puede declarar su tipo de resultado después de los parámetros.", "return termina la ejecución de la función actual."],
  sit="Una función calcula un total y debe entregar ese número al lugar donde fue llamada. ¿Qué sentencia usarías?",
  cod="""package main

import "fmt"

func doble(n int) int {
    return n * 2
}

func main() {
    fmt.Println(doble(6))
}""", h="devuelve el doble de un entero a quien llama", pr=("La sentencia para devolver un resultado es ___. (6 letras)", "return"), pr2=("Después de los parámetros, la función indica el tipo de ___. (9 letras)", "resultado"), ec="declarar un tipo de resultado y olvidarse de devolverlo en todos los caminos", out="12"),
K("Múltiples resultados", d="firma de función que devuelve más de un valor", u="entregar juntos un resultado y sus datos asociados", mas="Go permite listar varios tipos de resultado entre paréntesis en la firma. Una sola sentencia return puede proporcionar todos los valores. Al llamar, cada resultado se asigna a una variable distinta, o se descarta con el identificador _.",
  k=["Una función Go puede devolver varios valores.", "Los tipos de resultado múltiples se escriben entre paréntesis.", "Cada resultado se recibe en su propia variable o se descarta con _."],
  sit="Una operación necesita entregar al mismo tiempo el cociente entero y el resto de una división. ¿Qué diseño usarías?",
  cod="""package main

import "fmt"

func dividir(a, b int) (int, int) {
    return a / b, a % b
}

func main() {
    cociente, resto := dividir(17, 5)
    fmt.Println(cociente, resto)
}""", h="devuelve y recibe el cociente y el resto", pr=("Go permite que una función devuelva ___ valores. (9 letras)", "múltiples", "multiples"), pr2=("Los resultados de dividir 17 entre 5 son 3 y ___. (un número)", "2"), ec="asignar una llamada de varios resultados a una sola variable", out="3 2"),
K("Resultados con nombre", d="resultados declarados con identificadores en la firma de función", u="documentar y asignar directamente los valores de retorno", mas="Los resultados con nombre se declaran en la lista de resultados de la función. Actúan como variables locales inicializadas con sus valores cero. Se puede usar return sin expresión, aunque un return explícito suele hacer más claro el código.",
  k=["Los resultados con nombre son variables locales de la función.", "Sus valores iniciales son los valores cero de sus tipos.", "Un return sin expresión devuelve los resultados nombrados."],
  sit="Quieres nombrar los resultados en la firma y asignarlos antes de devolverlos desde una función. ¿Qué forma usarías?",
  cod="""package main

import "fmt"

func rectangulo(ancho, alto int) (area int) {
    area = ancho * alto
    return
}

func main() {
    fmt.Println(rectangulo(3, 4))
}""", h="calcula el área en una variable de resultado con nombre", pr=("Los valores de retorno que tienen identificador en la firma se llaman resultados con ___. (6 letras)", "nombre"), pr2=("El valor inicial de un resultado nombrado es el valor ___. (4 letras)", "cero"), ec="usar retornos con nombre para ocultar el flujo de valores en una función extensa", out="12"),
K("Funciones variádicas", d="funciones que reciben cero o más argumentos de un tipo", u="aceptar una cantidad variable de valores", mas="El último parámetro de una función variádica se declara con ... antes del tipo, por ejemplo ...int. Dentro de la función, ese parámetro se comporta como un slice. Al pasar un slice existente se añade ... después del argumento para expandirlo.",
  k=["El parámetro variádico se marca con ... antes de su tipo.", "El parámetro variádico se recibe como un slice.", "Un slice se expande como argumentos con ... al llamar."],
  sit="Una función de suma debe aceptar cualquier cantidad de enteros en una sola llamada. ¿Qué clase de parámetro usarías?",
  cod="""package main

import "fmt"

func sumar(valores ...int) int {
    total := 0
    for _, valor := range valores {
        total += valor
    }
    return total
}

func main() {
    fmt.Println(sumar(2, 3, 4))
}""", h="suma un número variable de argumentos enteros", pr=("El marcador que permite recibir cero o más argumentos es ___. (3 puntos)", "..."), pr2=("Dentro de la función, el parámetro variádico se comporta como un ___. (5 letras)", "slice"), ec="declarar el parámetro variádico antes de otros parámetros", out="9"),
K("Recursión", d="técnica en que una función se llama a sí misma para resolver un caso menor", u="resolver problemas que se dividen en subproblemas similares", mas="Una función recursiva necesita un caso base que detenga las llamadas y un paso que reduzca el problema. Sin caso base, la recursión continúa hasta agotar la pila. Para ciertos problemas iterativos, un bucle puede ser más simple y usar menos memoria.",
  k=["Una función recursiva se llama a sí misma.", "El caso base detiene las llamadas recursivas.", "Cada paso debe acercarse al caso base."],
  sit="Quieres definir el factorial reduciendo n a una llamada con n-1 hasta llegar a un valor de parada. ¿Qué técnica aplicarías?",
  cod="""package main

import "fmt"

func factorial(n int) int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n-1)
}

func main() {
    fmt.Println(factorial(5))
}""", h="calcula el factorial con un caso base y llamadas recursivas", pr=("Una función que se llama a sí misma usa la ___. (9 letras)", "recursión", "recursion"), pr2=("La condición que detiene una función recursiva es el caso ___. (4 letras)", "base"), ec="olvidar el caso base y producir llamadas recursivas sin fin", out="120"),
K("Funciones anónimas", d="funciones sin nombre que se pueden asignar o invocar directamente", u="definir una operación breve junto al lugar donde se usa", mas="Una función anónima se escribe con func y una lista de parámetros, pero sin nombre entre func y los paréntesis. Se puede asignar a una variable o llamar inmediatamente. El tipo de la variable se infiere a partir de la firma de la función.",
  k=["Una función anónima no tiene nombre en su declaración.", "Se puede asignar a una variable.", "También se puede invocar inmediatamente."],
  sit="Necesitas definir una operación pequeña cerca de su uso y no hace falta darle un nombre global. ¿Qué escribirías?",
  cod="""package main

import "fmt"

func main() {
    triple := func(n int) int { return n * 3 }
    fmt.Println(triple(4))
}""", h="asigna una función anónima y la llama", pr=("Una función declarada sin identificador se llama ___. (7 letras)", "anónima", "anonima"), pr2=("La variable triple guarda un valor de tipo ___. (7 letras)", "función", "funcion"), ec="confundir una función anónima con una llamada a una función inexistente", out="12"),
K("Closures", d="funciones que conservan acceso a variables de su entorno léxico", u="crear operaciones con estado encapsulado", mas="Una función literal puede usar variables declaradas en una función exterior. Esa función y las variables capturadas forman un closure. El estado permanece disponible entre llamadas mientras el closure siga referenciado.",
  k=["Un closure captura variables de su entorno léxico.", "El estado capturado puede sobrevivir a la función exterior.", "Los valores capturados pueden compartirse entre llamadas."],
  sit="Quieres crear un contador independiente cuyo estado se conserve entre varias llamadas a la función devuelta. ¿Qué usarías?",
  cod="""package main

import "fmt"

func crearContador() func() int {
    n := 0
    return func() int {
        n++
        return n
    }
}

func main() {
    contador := crearContador()
    fmt.Println(contador(), contador())
}""", h="conserva e incrementa un contador dentro de un closure", pr=("Una función que conserva variables de su entorno se conoce como ___. (7 letras)", "closure"), pr2=("En el ejemplo, la variable capturada es ___. (una letra)", "n"), ec="esperar que las variables capturadas desaparezcan al retornar la función exterior", out="1 2"),
K("Arrays", d="secuencia de elementos del mismo tipo con longitud fija", u="representar datos indexados de tamaño conocido", mas="La longitud forma parte del tipo del array, por lo que [3]int y [4]int son tipos distintos. Los arrays se inicializan con literales compuestos y se accede a sus elementos desde el índice cero. Asignar un array copia todos sus elementos.",
  k=["La longitud del array forma parte de su tipo.", "Los índices de un array comienzan en cero.", "Asignar un array copia sus elementos."],
  sit="El tamaño de una secuencia de tres coordenadas siempre es fijo y conocido. ¿Qué estructura de Go usarías?",
  cod="""package main

import "fmt"

func main() {
    coordenadas := [3]int{4, 5, 6}
    fmt.Println(len(coordenadas), coordenadas[0], coordenadas[2])
}""", h="crea un array fijo y consulta su longitud y extremos", pr=("La cantidad de elementos de un array forma parte de su ___. (4 letras)", "tipo"), pr2=("El primer elemento de un array tiene índice ___. (un número)", "0", "cero"), ec="intentar agregar un elemento a un array que tiene longitud fija", out="3 4 6"),
K("Slices", d="vista de longitud variable sobre los elementos de un array", u="guardar secuencias que pueden crecer", mas="Un slice contiene una referencia a un array subyacente, su longitud y su capacidad. Se crea con un literal como []int{1, 2} o tomando un segmento de un array. Un slice nil tiene longitud y capacidad cero.",
  k=["Un slice describe una porción de un array subyacente.", "La longitud y la capacidad son propiedades diferentes.", "El literal []T crea un slice de tipo T."],
  sit="Necesitas una secuencia indexada cuya longitud pueda crecer según los datos. ¿Qué colección elegirías?",
  cod="""package main

import "fmt"

func main() {
    notas := []int{7, 9, 8}
    fmt.Println(len(notas), notas[1])
}""", h="crea un slice de enteros y consulta su longitud y un elemento", pr=("La colección indexada que puede redimensionarse se llama ___. (5 letras)", "slice"), pr2=("La expresión literal de un slice de enteros comienza con ___. (5 caracteres)", "[]int"), ec="confundir la longitud actual del slice con su capacidad", out="3 9"),
K("append", d="función integrada que agrega elementos al final de un slice", u="ampliar una secuencia dinámicamente", mas="append devuelve un slice que contiene los elementos agregados. Puede reutilizar el array subyacente si hay capacidad suficiente o asignar otro si necesita más espacio. Por eso se debe guardar el slice devuelto, normalmente reasignándolo a la misma variable.",
  k=["append agrega elementos al final de un slice.", "append devuelve el slice resultante.", "El array subyacente puede cambiar cuando se supera la capacidad."],
  sit="Quieres añadir un valor al final de una secuencia y conservar el slice actualizado. ¿Qué función usarías?",
  cod="""package main

import "fmt"

func main() {
    valores := []int{2, 4}
    valores = append(valores, 6)
    fmt.Println(valores)
}""", h="agrega un elemento y guarda el slice devuelto", pr=("La función integrada para añadir elementos a un slice es ___. (6 letras)", "append"), pr2=("Después de añadir, hay que guardar el slice que ___ devuelve. (6 letras)", "append"), ec="llamar append sin usar el slice que devuelve", out="[2 4 6]"),
K("copy de slices", d="función integrada que copia elementos entre slices", u="duplicar valores sin compartir el mismo segmento", mas="copy(destino, origen) copia hasta el mínimo entre las longitudes de ambos slices y devuelve el número de elementos copiados. No amplía el destino, así que debe tener longitud suficiente. Si origen y destino se solapan, copy también está definido.",
  k=["copy copia elementos del origen al destino.", "copy devuelve el número de elementos copiados.", "La longitud del destino limita cuántos elementos se copian."],
  sit="Quieres copiar elementos de un slice a otro ya asignado y saber cuántos se copiaron. ¿Qué función usarías?",
  cod="""package main

import "fmt"

func main() {
    origen := []int{3, 6, 9}
    destino := make([]int, len(origen))
    cantidad := copy(destino, origen)
    fmt.Println(cantidad, destino)
}""", h="copia tres enteros en otro slice de longitud suficiente", pr=("La función que copia entre slices se llama ___. (4 letras)", "copy"), pr2=("copy devuelve la cantidad de elementos ___. (8 letras)", "copiados"), ec="crear un destino vacío y esperar que copy lo amplíe", out="3 [3 6 9]"),
K("make para slices", d="función integrada que crea slices, mapas o canales inicializados", u="reservar una colección con longitud o capacidad concreta", mas="make([]T, longitud, capacidad) crea un slice con longitud y capacidad indicadas; el tercer argumento es opcional. Los elementos reciben el valor cero del tipo. A diferencia de new, make inicializa las estructuras internas de slices, mapas y canales.",
  k=["make puede crear slices, mapas y canales.", "make([]T, n) crea un slice de longitud n.", "La capacidad opcional puede ser mayor que la longitud."],
  sit="Quieres reservar un slice de cuatro enteros ya inicializados con el valor cero. ¿Qué función usarías?",
  cod="""package main

import "fmt"

func main() {
    datos := make([]int, 4, 6)
    fmt.Println(len(datos), cap(datos), datos[0])
}""", h="crea un slice y muestra longitud, capacidad y valor cero", pr=("La función integrada que inicializa un slice con longitud elegida es ___. (4 letras)", "make"), pr2=("Para make([]int, 4, 6), la capacidad es ___. (un número)", "6"), ec="usar una capacidad menor que la longitud al llamar make para slice", out="4 6 0"),
K("len y cap", d="funciones integradas que informan longitud y capacidad de una colección", u="consultar cuántos elementos hay y cuánto puede crecer un slice", mas="len devuelve la cantidad de elementos de un array, slice, cadena o mapa. cap informa la capacidad de arrays, slices y canales, pero no de mapas. En un slice, la capacidad mide el espacio desde su primer elemento hasta el final del array subyacente.",
  k=["len funciona con arrays, slices, cadenas y mapas.", "cap informa capacidad de arrays, slices y canales.", "La capacidad de un slice puede exceder su longitud."],
  sit="Quieres conocer tanto los elementos actuales como el espacio disponible para que crezca un slice. ¿Qué funciones llamarías?",
  cod="""package main

import "fmt"

func main() {
    numeros := make([]int, 2, 5)
    fmt.Println(len(numeros), cap(numeros))
}""", h="muestra la longitud y capacidad del mismo slice", pr=("La función que cuenta elementos actuales es ___. (3 letras)", "len"), pr2=("La función que obtiene la capacidad de un slice es ___. (3 letras)", "cap"), ec="usar cap para consultar la capacidad de un mapa", out="2 5"),
K("Mapas", d="colecciones que asocian claves únicas con valores de un tipo", u="buscar datos por una clave en lugar de una posición", mas="Un mapa se declara con map[TipoClave]TipoValor y se crea con make o un literal. Las claves deben ser comparables. Al leer una clave ausente se obtiene el valor cero del tipo de valor, por lo que a menudo se usa la forma de dos resultados para distinguirla.",
  k=["Un mapa asocia claves comparables con valores.", "make o un literal permiten crear un mapa utilizable.", "Leer una clave ausente produce el valor cero del valor."],
  sit="Quieres encontrar la edad asociada al nombre de una persona en lugar de buscarla por posición. ¿Qué colección usarías?",
  cod="""package main

import "fmt"

func main() {
    edades := map[string]int{"Ana": 20, "Luis": 25}
    fmt.Println(edades["Luis"])
}""", h="consulta la edad asociada a una clave de texto", pr=("La colección que asocia claves y valores se llama ___. (3 letras)", "map"), pr2=("Las claves de un mapa deben ser ___. (11 letras)", "comparables"), ec="leer o escribir un mapa nil sin inicializarlo con make o un literal", out="25"),
K("Consulta comma ok", d="forma de dos resultados para comprobar si una clave existe en un mapa", u="distinguir una clave ausente del valor cero almacenado", mas="Al consultar valor, ok := mapa[clave], el primer resultado es el valor y el segundo indica si la clave existe. Esta distinción es importante cuando el valor cero también es válido. La misma forma de dos resultados se usa con aserciones de tipo y recepción de canales.",
  k=["Una consulta de mapa puede devolver valor y existencia.", "ok es true solo si la clave está presente.", "La forma de dos resultados también aparece en aserciones y canales."],
  sit="El valor cero es válido en tus datos, así que necesitas distinguirlo de una clave inexistente. ¿Qué comprobación harías?",
  cod="""package main

import "fmt"

func main() {
    edades := map[string]int{"Ana": 0}
    edad, existe := edades["Ana"]
    fmt.Println(edad, existe)
}""", h="distingue una clave existente que almacena cero", pr=("El segundo resultado de una consulta comma ok indica si la clave ___. (6 letras)", "existe"), pr2=("La variable booleana suele llamarse ___ en la forma valor, ok. (2 letras)", "ok"), ec="interpretar el valor cero como prueba suficiente de que una clave no existe", out="0 true"),
K("range en colecciones", d="forma de recorrer índices y valores de arrays, slices o mapas", u="procesar todos los elementos de una colección", mas="range sobre un slice o array produce índice y valor en cada vuelta. Sobre un mapa produce clave y valor, pero el orden de iteración de mapas no está especificado y puede variar. Se puede descartar un resultado con _ si no se necesita.",
  k=["range recorre arrays, slices y mapas.", "En slices produce índice y valor.", "El orden de recorrido de un mapa no está especificado."],
  sit="Quieres procesar cada valor de una secuencia indexada sin gestionar manualmente el contador. ¿Qué forma de recorrido usarías?",
  cod="""package main

import "fmt"

func main() {
    valores := []int{3, 5, 7}
    for indice, valor := range valores {
        fmt.Println(indice, valor)
    }
}""", h="recorre todos los índices y valores de un slice", pr=("La palabra clave para recorrer los elementos de una colección es ___. (5 letras)", "range"), pr2=("El orden de iteración de las claves de un mapa es ___. (14 letras)", "inespecificado"), ec="suponer que un mapa siempre se recorre en el orden de inserción", out="0 3\n1 5\n2 7"),
K("Expresiones de slice", d="notación de rangos que crea una vista sobre una parte de un array o slice", u="seleccionar un segmento sin copiar sus elementos", mas="La expresión s[inicio:fin] incluye el índice inicial y excluye el final. El resultado comparte el array subyacente con el slice original, por lo que cambiar un elemento del segmento puede cambiar el original. Los límites deben estar dentro de las reglas de longitud y capacidad.",
  k=["El límite inicial de s[a:b] se incluye y el final se excluye.", "Un slice de segmento comparte el array subyacente.", "Modificar un elemento compartido puede afectar el slice original."],
  sit="Quieres seleccionar los elementos con índices 1 y 2 sin duplicarlos en otra colección. ¿Qué expresión usarías?",
  cod="""package main

import "fmt"

func main() {
    datos := []int{10, 20, 30, 40}
    segmento := datos[1:3]
    segmento[0] = 99
    fmt.Println(segmento, datos)
}""", h="toma un segmento y muestra el cambio compartido", pr=("En s[a:b], el índice final b queda ___. (8 letras)", "excluido"), pr2=("Un segmento de slice comparte el array ___ con el original. (10 letras)", "subyacente"), ec="suponer que cortar un slice crea automáticamente una copia independiente", out="[99 30] [10 99 30 40]"),
]
