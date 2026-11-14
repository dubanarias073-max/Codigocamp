"""Go · Etapa 1: fundamentos del lenguaje."""
from ..generador import K

LISTA = [
K("Hola, mundo", d="programa mínimo de Go que muestra un saludo desde main", u="comprobar la instalación y la estructura básica del lenguaje", mas="El primer ejemplo suele imprimir «Hola, mundo». Un programa ejecutable declara package main, importa fmt y define func main. Con go run archivo.go se compila y ejecuta el ejemplo.",
  k=["Un programa ejecutable comienza en func main.", "fmt.Println muestra el saludo con salto de línea.", "go run permite compilar y ejecutar un archivo Go."],
  sit="Acabas de instalar Go y quieres comprobarlo ejecutando el ejemplo inicial que imprime un saludo. ¿Qué programa escribirías?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println("Hola, mundo")
}""", h="muestra el saludo inicial desde la función de entrada de Go", pr=("El primer ejemplo suele llamarse «Hola, ___». (5 letras)", "mundo"), pr2=("El punto de entrada de un programa Go es func ___. (4 letras)", "main"), ec="olvidar declarar package main o func main en el programa inicial", out="Hola, mundo"),
K("Variables", d="nombres asociados a valores de un tipo durante la ejecución", u="guardar y actualizar datos que usa el programa", mas="Una variable de Go se declara con var o con la forma corta := dentro de una función. Su tipo queda establecido al declararla, aunque puede cambiar el valor por otro del mismo tipo. Las variables sin inicializador reciben el valor cero.",
  k=["Una variable se declara con var o con := dentro de una función.", "El tipo de una variable no cambia durante su vida.", "Una variable declarada sin valor inicial recibe el valor cero."],
  sit="Necesitas guardar el puntaje de una partida y actualizarlo manteniendo un tipo definido. ¿Qué elemento usarías?",
  cod="""package main

import "fmt"

func main() {
    puntos := 0
    puntos = puntos + 10
    fmt.Println(puntos)
}""", h="declara una puntuación y la actualiza", pr=("Un nombre asociado a un valor que puede actualizarse se llama ___. (8 letras)", "variable"), pr2=("Una declaración local corta de Go usa el operador ___. (2 caracteres)", ":="), ec="intentar cambiar el tipo de una variable al reasignarla", out="10"),
K("Go es compilado", d="lenguaje cuyo código fuente se traduce a un ejecutable", u="generar programas que se pueden ejecutar sin intérprete", mas="El compilador de Go transforma los archivos fuente en código ejecutable para una plataforma. El comando go run compila y ejecuta el programa para facilitar el desarrollo. El comando go build crea un ejecutable sin iniciarlo.",
  k=["El compilador traduce el código fuente de Go.", "go run compila y ejecuta un programa.", "go build genera un ejecutable sin ejecutarlo."],
  sit="Quieres producir un archivo ejecutable a partir del código Go sin iniciar el programa. ¿Qué herramienta usarías?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println("go build crea un ejecutable")
    fmt.Println("go run compila y ejecuta")
}""", h="compara los propósitos de go build y go run", pr=("El comando que crea un ejecutable sin iniciarlo es go ___. (5 letras)", "build"), pr2=("Go traduce el código fuente con un ___. (10 letras)", "compilador"), ec="confundir go build, que compila, con go run, que también ejecuta", out="go build crea un ejecutable\ngo run compila y ejecuta"),
K("Paquete main", d="paquete que declara un programa ejecutable de Go", u="indicar que el paquete produce un comando", mas="Los programas ejecutables usan la declaración package main. Un paquete con otro nombre normalmente forma parte de una biblioteca importable. El punto de entrada del ejecutable es la función main del paquete main.",
  k=["Un programa ejecutable declara package main.", "Los paquetes de biblioteca pueden tener otro nombre.", "La función main es el punto de entrada del ejecutable."],
  sit="El archivo principal de un comando Go debe declarar el paquete reservado para los ejecutables. ¿Qué paquete escribirías?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println("Este paquete genera un programa")
}""", h="ejecuta un programa declarado en el paquete main", pr=("Un programa ejecutable de Go declara package ___. (4 letras)", "main"), pr2=("La declaración de paquete aparece antes de las ___. (13 letras)", "importaciones", "imports"), ec="declarar package fmt en el punto de entrada de un ejecutable", out="Este paquete genera un programa"),
K("Función main", d="función que Go ejecuta primero en un programa del paquete main", u="definir el inicio del programa", mas="La función main se declara con func main() y no recibe argumentos ni devuelve resultados. En un programa ejecutable debe existir exactamente una función main en el paquete principal. El código de esa función se ejecuta al iniciar el programa.",
  k=["La función main se declara con func main().", "Go inicia el programa ejecutando main.", "main no recibe argumentos ni devuelve resultados."],
  sit="Quieres decidir qué instrucciones se ejecutan al iniciar un comando Go. ¿Qué función defines?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println("Inicio")
    fmt.Println("Fin")
}""", h="ejecuta dos instrucciones en orden desde main", pr=("La función de entrada de un ejecutable Go se llama ___. (4 letras)", "main"), pr2=("Una función Go se declara con la palabra ___. (4 letras)", "func"), ec="escribir Main con mayúscula en lugar de main", out="Inicio\nFin"),
K("Paquete fmt", d="paquete estándar que ofrece funciones de formato y salida", u="mostrar y formatear valores en la terminal", mas="fmt pertenece a la biblioteca estándar de Go y se importa con import \"fmt\". fmt.Println imprime sus argumentos separados por espacios y termina con un salto de línea. fmt.Printf permite controlar el formato usando verbos como %s y %d.",
  k=["fmt es parte de la biblioteca estándar.", "fmt.Println separa argumentos con espacios y añade un salto de línea.", "fmt.Printf interpreta verbos de formato como %d."],
  sit="Quieres imprimir varios valores separados por espacios y terminar la línea automáticamente. ¿Qué función usarías?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println("puntos:", 12)
}""", h="imprime una etiqueta y un número en una línea", pr=("La función de fmt que imprime con salto de línea es fmt.___. (7 letras)", "Println"), pr2=("El paquete de formato de la biblioteca estándar se llama ___. (3 letras)", "fmt"), ec="olvidar importar fmt antes de llamar a fmt.Println", out="puntos: 12"),
K("Comentarios en Go", d="texto que documenta el código y no se ejecuta", u="explicar decisiones dentro de un programa", mas="Go admite comentarios de línea que empiezan con // y comentarios de bloque delimitados por /* y */. Los comentarios de documentación suelen colocarse antes del identificador que describen. No afectan la ejecución del programa.",
  k=["Los comentarios de línea comienzan con //.", "Los comentarios de bloque usan /* y */.", "Los comentarios no cambian la ejecución del programa."],
  sit="Quieres dejar una explicación breve al lado de una instrucción sin que Go la ejecute. ¿Qué usarías?",
  cod="""package main

import "fmt"

func main() {
    // Esta nota no se ejecuta
    fmt.Println("El programa sí ejecuta esta línea")
}""", h="deja una nota y ejecuta una impresión", pr=("El marcador de comentario de línea en Go es ___. (2 caracteres)", "//"), pr2=("Go ignora los comentarios durante la ___. (9 letras)", "ejecución", "ejecucion"), ec="usar # para iniciar un comentario en Go", out="El programa sí ejecuta esta línea"),
K("Identificadores exportados", d="nombres que comienzan con mayúscula y son accesibles desde otros paquetes", u="decidir qué nombres de un paquete forman su API pública", mas="En Go, un identificador cuyo primer carácter es una letra mayúscula se exporta desde su paquete. Los nombres que empiezan con minúscula solo son visibles dentro del paquete. La regla se aplica a funciones, tipos, variables y constantes.",
  k=["Los identificadores exportados comienzan con mayúscula.", "Los nombres en minúscula quedan privados al paquete.", "La regla se aplica a funciones, tipos y variables."],
  sit="Vas a exponer una función para que otros paquetes puedan llamarla; su nombre debe comenzar en mayúscula. ¿Qué regla aplicarías?",
  cod="""package main

import "fmt"

func Saludar() string { return "Hola" }
func interno() string { return "oculto" }

func main() {
    fmt.Println(Saludar())
}""", h="declara una función exportada y otra interna al paquete", pr=("Un nombre exportado de Go comienza con letra ___. (9 letras)", "mayúscula"), pr2=("Un identificador que empieza en minúscula no se exporta fuera del ___. (7 letras)", "paquete"), ec="creer que basta con escribir un nombre en mayúsculas en cualquier lenguaje", out="Hola"),
K("Declaración corta :=", d="forma de declarar y asignar una variable dentro de una función", u="crear variables locales de manera concisa", mas="El operador := declara una variable local e infiere su tipo desde el valor de la derecha. Solo puede usarse dentro de funciones, no en el nivel del paquete. Una variable ya declarada no puede volver a declararse en el mismo bloque sin introducir un nombre nuevo.",
  k=[":= declara e inicializa una variable local.", "El tipo se infiere a partir del valor asignado.", "La declaración corta solo puede usarse dentro de funciones."],
  sit="Dentro de una función quieres crear una variable local y dejar que Go deduzca su tipo. ¿Qué sintaxis usarías?",
  cod="""package main

import "fmt"

func main() {
    ciudad := "Quito"
    fmt.Println(ciudad)
}""", h="declara una cadena local usando inferencia de tipo", pr=("El operador de declaración corta de Go es ___. (2 caracteres)", ":="), pr2=("La declaración corta no se puede usar fuera de una ___. (7 letras)", "función"), ec="usar := en la declaración de una variable global", out="Quito"),
K("Declaración var", d="palabra clave para declarar una variable local o de paquete", u="declarar variables con o sin valor inicial", mas="La palabra clave var permite declarar una variable indicando su tipo o dejando que se infiera desde el valor. Una variable declarada sin inicializador recibe el valor cero de su tipo. A diferencia de :=, var también puede aparecer fuera de una función.",
  k=["var declara variables dentro o fuera de funciones.", "var permite indicar el tipo explícitamente.", "Sin inicializador, la variable recibe su valor cero."],
  sit="Necesitas declarar una variable en el nivel del paquete, donde no se permite :=. ¿Qué palabra clave usarías?",
  cod="""package main

import "fmt"

var idioma string

func main() {
    var nivel = 2
    fmt.Println(idioma, nivel)
}""", h="declara una cadena global y una variable local inferida", pr=("La palabra clave de declaración de variables en Go es ___. (3 letras)", "var"), pr2=("Una variable string sin inicializar tiene como valor cero la cadena ___. (vacía)", "vacía", "vacia", "\"\""), ec="usar := para declarar una variable en el nivel del paquete", out=" 2"),
K("Tipos explícitos", d="tipos escritos en una declaración para precisar la clase de dato", u="hacer visible qué valores admite una variable", mas="Go permite incluir el tipo en una declaración var, por ejemplo var edad int = 18. El compilador verifica que los valores asignados sean compatibles con ese tipo. Las declaraciones explícitas resultan útiles cuando el valor inicial no permite inferir el tipo deseado.",
  k=["Se puede escribir el tipo en una declaración var.", "El compilador comprueba la compatibilidad de las asignaciones.", "Un tipo explícito puede aclarar la intención del código."],
  sit="Quieres declarar una variable y dejar claro desde el inicio que solo guardará enteros. ¿Qué escribirías?",
  cod="""package main

import "fmt"

func main() {
    var intentos int = 3
    fmt.Println(intentos)
}""", h="declara una variable de tipo int y muestra su valor", pr=("En var intentos int = 3, el tipo explícito es ___. (3 letras)", "int"), pr2=("El compilador revisa que los valores respeten el ___. (4 letras)", "tipo"), ec="asignar un valor de tipo incompatible con la variable", out="3"),
K("Constantes", d="valores con nombre que no pueden cambiar después de declararse", u="representar datos fijos del programa", mas="Una constante se declara con const y debe tener un valor constante conocido en compilación. No se puede reasignar una constante después de declararla. Go permite constantes de cadenas, booleanos y números.",
  k=["Las constantes se declaran con const.", "Una constante no se puede reasignar.", "Go admite constantes numéricas, de texto y booleanas."],
  sit="Una tasa de impuesto fija no debe cambiar durante la ejecución del programa. ¿Qué declaración usarías?",
  cod="""package main

import "fmt"

func main() {
    const impuesto = 0.15
    fmt.Println(impuesto)
}""", h="declara y muestra una constante numérica", pr=("La palabra clave para declarar un valor inmutable es ___. (5 letras)", "const"), pr2=("Una constante no se puede volver a ___. (9 letras)", "reasignar"), ec="intentar cambiar el valor de una constante", out="0.15"),
K("Inferencia de tipos", d="deducción del tipo a partir del valor inicial asignado", u="escribir declaraciones sin repetir el tipo", mas="Cuando una variable se inicializa con := o con var y un valor, Go determina el tipo según la expresión. Por ejemplo, 7 infiere int y \"hola\" infiere string. La inferencia no convierte automáticamente tipos incompatibles.",
  k=[":= infiere el tipo a partir del valor inicial.", "El literal 7 infiere el tipo int.", "La inferencia no elimina la distinción entre tipos."],
  sit="Quieres asignar un valor literal y permitir que Go determine el tipo de la variable. ¿Qué característica aprovecharías?",
  cod="""package main

import "fmt"

func main() {
    cantidad := 7
    nombre := "Luz"
    fmt.Printf("%T %T\\n", cantidad, nombre)
}""", h="muestra los tipos inferidos para un entero y una cadena", pr=("La característica que deduce el tipo según el valor es la ___. (10 letras)", "inferencia"), pr2=("El literal entero 7 infiere el tipo ___. (3 letras)", "int"), ec="suponer que una variable puede cambiar de tipo tras declararse", out="int string"),
K("Enteros int", d="tipo entero con tamaño dependiente de la arquitectura", u="guardar cantidades que no requieren fracciones", mas="int representa números enteros con un tamaño adecuado para la arquitectura, de al menos 32 bits. Para tamaños fijos también existen int8, int16, int32 e int64. La división entre dos valores int descarta la parte fraccionaria.",
  k=["int representa valores enteros.", "El tamaño de int depende de la arquitectura.", "Go también ofrece enteros de anchos fijos."],
  sit="Vas a guardar el número de elementos de una colección, que es un entero sin parte decimal. ¿Qué tipo elegirías?",
  cod="""package main

import "fmt"

func main() {
    elementos := 8
    fmt.Printf("%T %d\\n", elementos, elementos)
}""", h="muestra el tipo y el valor de una cantidad entera", pr=("El tipo entero general de Go se llama ___. (3 letras)", "int"), pr2=("Los tipos int8 e int64 tienen ancho ___. (4 letras)", "fijo"), ec="esperar que int siempre tenga exactamente 64 bits", out="int 8"),
K("Números float64", d="tipo de punto flotante de 64 bits para valores con fracción", u="representar mediciones y resultados decimales", mas="float64 es el tipo de punto flotante predeterminado para muchos literales decimales. Como otros formatos binarios de coma flotante, no representa exactamente todos los decimales. Para cálculos financieros que exigen decimales exactos, se necesita una estrategia distinta a float64.",
  k=["float64 almacena números de punto flotante de 64 bits.", "Los literales decimales suelen inferir float64.", "No todos los decimales tienen representación binaria exacta."],
  sit="Necesitas representar una medida con parte fraccionaria y una precisión binaria de 64 bits. ¿Qué tipo usarías?",
  cod="""package main

import "fmt"

func main() {
    medida := 2.5
    fmt.Printf("%T %.1f\\n", medida, medida)
}""", h="muestra el tipo inferido y un decimal con una cifra", pr=("El tipo de punto flotante de 64 bits se llama ___. (7 caracteres)", "float64"), pr2=("El literal 2.5 infiere el tipo ___. (7 caracteres)", "float64"), ec="usar float64 suponiendo que todos los decimales son exactos", out="float64 2.5"),
K("Booleanos", d="tipo bool con los valores true y false", u="guardar resultados lógicos y condiciones", mas="El tipo bool tiene únicamente dos valores, true y false, escritos en minúscula. Las comparaciones producen valores booleanos que se pueden usar en condiciones. Go no convierte automáticamente enteros en booleanos ni al revés.",
  k=["Los valores de bool son true y false.", "Los booleanos se escriben en minúscula.", "Go no convierte números en booleanos automáticamente."],
  sit="Quieres guardar si una puerta está abierta o cerrada usando uno de dos estados lógicos. ¿Qué tipo usarías?",
  cod="""package main

import "fmt"

func main() {
    abierto := true
    fmt.Printf("%T %t\\n", abierto, abierto)
}""", h="declara un booleano y muestra su tipo y valor", pr=("El tipo lógico de Go se llama ___. (4 letras)", "bool"), pr2=("Los booleanos de Go se escriben en minúscula: true y ___. (5 letras)", "false"), ec="escribir True o False con mayúscula como en Python", out="bool true"),
K("Cadenas string", d="tipo inmutable que representa una secuencia de bytes, normalmente texto UTF-8", u="guardar y combinar palabras y mensajes", mas="Las cadenas se escriben entre comillas dobles o con acentos graves para texto sin procesar. En Go una cadena es inmutable y su longitud con len cuenta bytes, no necesariamente caracteres. El texto UTF-8 puede contener caracteres que ocupan varios bytes.",
  k=["Las cadenas de Go son inmutables.", "len cuenta bytes, no siempre caracteres Unicode.", "Las cadenas pueden escribirse entre comillas dobles o acentos graves."],
  sit="Necesitas almacenar un mensaje textual y combinarlo con otro mensaje sin cambiar su contenido original. ¿Qué tipo usarías?",
  cod="""package main

import "fmt"

func main() {
    saludo := "Hola"
    completo := saludo + ", Go"
    fmt.Println(completo)
}""", h="combina dos cadenas y muestra el resultado", pr=("El tipo para guardar texto en Go se llama ___. (6 letras)", "string"), pr2=("Las cadenas de Go no se pueden modificar: son ___. (10 letras)", "inmutables"), ec="suponer que len de una cadena siempre cuenta caracteres visibles", out="Hola, Go"),
K("Runas rune", d="alias de int32 que representa un punto de código Unicode", u="recorrer texto por caracteres Unicode", mas="rune es un alias de int32 y representa un punto de código Unicode. Al recorrer una cadena con range, Go devuelve el índice en bytes y el valor de cada runa. Un carácter visible puede componerse de más de un punto de código.",
  k=["rune es un alias de int32.", "range sobre una cadena produce índices de bytes y runas.", "Un punto de código no siempre equivale a un carácter visual."],
  sit="Vas a recorrer una cadena que contiene letras acentuadas y quieres obtener cada punto de código Unicode. ¿Qué tipo usarías?",
  cod="""package main

import "fmt"

func main() {
    for _, letra := range "Goñ" {
        fmt.Printf("%c ", letra)
    }
}""", h="recorre y muestra los puntos de código de una cadena", pr=("El alias entero para puntos de código Unicode se llama ___. (4 letras)", "rune"), pr2=("rune tiene como tipo base int___. (2 números)", "32"), ec="indexar una cadena por bytes esperando obtener siempre una letra completa", out="G o ñ "),
K("Bytes byte", d="alias de uint8 para representar un byte individual", u="manejar datos binarios y bytes de texto", mas="byte es un alias de uint8, por lo que puede almacenar valores entre 0 y 255. Al convertir una cadena a []byte se obtiene su secuencia UTF-8. Un carácter Unicode puede ocupar varios bytes.",
  k=["byte es un alias de uint8.", "Un byte puede representar valores de 0 a 255.", "Un carácter UTF-8 puede ocupar varios bytes."],
  sit="Estás procesando los valores binarios de una cadena UTF-8, un elemento de ocho bits a la vez. ¿Qué tipo usarías?",
  cod="""package main

import "fmt"

func main() {
    datos := []byte("Go")
    fmt.Println(datos[0], datos[1])
}""", h="convierte una cadena en bytes y muestra sus dos valores", pr=("El alias de uint8 para un byte se llama ___. (4 letras)", "byte"), pr2=("Un byte tiene ___ bits. (un número)", "8", "ocho"), ec="creer que cada byte de una cadena Unicode equivale a un carácter", out="71 111"),
K("Formato con fmt.Printf", d="impresión con verbos que controlan cómo se muestran los valores", u="presentar números y cadenas con un formato definido", mas="fmt.Printf escribe texto con marcadores como %s para cadenas, %d para enteros y %f para flotantes. El verbo %T muestra el tipo del argumento. A diferencia de Println, Printf no agrega automáticamente un salto de línea.",
  k=["%s formatea cadenas y %d formatea enteros.", "%T muestra el tipo del argumento.", "Printf no añade un salto de línea automáticamente."],
  sit="Quieres insertar un nombre y una edad en una frase usando marcadores de formato. ¿Qué función elegirías?",
  cod="""package main

import "fmt"

func main() {
    fmt.Printf("%s tiene %d años\\n", "Eva", 9)
}""", h="inserta una cadena y un entero en una frase formateada", pr=("El verbo de fmt.Printf para un entero decimal es ___. (2 caracteres)", "%d"), pr2=("La función de fmt que usa verbos de formato es ___. (6 letras)", "Printf"), ec="olvidar el salto de línea cuando se espera que Printf termine la línea", out="Eva tiene 9 años"),
]
