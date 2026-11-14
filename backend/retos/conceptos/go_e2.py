"""Go · Etapa 2: decisiones, bucles y expresiones."""
from ..generador import K

LISTA = [
K("Decisiones", d="selección de instrucciones según una condición booleana", u="elegir qué camino sigue el programa", mas="Go usa if, else if y else para ejecutar bloques de acuerdo con condiciones. La condición debe ser de tipo bool; no se aceptan números como verdadero o falso. Las llaves son obligatorias incluso para bloques de una sola línea.",
  k=["if ejecuta un bloque cuando su condición es true.", "La condición de un if debe ser booleana.", "Las llaves son obligatorias en los bloques condicionales de Go."],
  sit="Un programa debe elegir un bloque de instrucciones según si una condición resulta verdadera o falsa. ¿Qué estructura usarías?",
  cod="""package main

import "fmt"

func main() {
    temperatura := 24
    if temperatura > 20 {
        fmt.Println("templado")
    }
}""", h="comprueba una condición y muestra un mensaje si es verdadera", pr=("La estructura que ejecuta código según una condición comienza con ___. (2 letras)", "if"), pr2=("La condición de if en Go debe tener tipo ___. (4 letras)", "bool"), ec="omitir las llaves de un bloque if", out="templado"),
K("Bucles", d="repetición de instrucciones mediante la palabra clave for", u="procesar varias veces un bloque de código", mas="Go utiliza for para todas sus formas de bucle; no tiene una palabra clave while separada. Un for puede tener inicialización, condición y actualización. También puede escribirse solo con condición o combinarse con range.",
  k=["for es la única palabra clave de bucle de Go.", "Un for clásico contiene inicialización, condición y actualización.", "for también puede recorrer valores con range."],
  sit="Necesitas repetir un bloque de instrucciones usando la única palabra clave de bucle de Go. ¿Qué estructura elegirías?",
  cod="""package main

import "fmt"

func main() {
    for vuelta := 1; vuelta <= 3; vuelta++ {
        fmt.Println(vuelta)
    }
}""", h="repite tres veces con un contador for", pr=("La palabra clave de Go para repetir instrucciones es ___. (3 letras)", "for"), pr2=("Go no tiene una palabra clave while: usa ___. (3 letras)", "for"), ec="buscar una sentencia while independiente en Go", out="1\n2\n3"),
K("Operadores aritméticos", d="símbolos que calculan suma, resta, producto, cociente y resto", u="realizar cálculos numéricos con expresiones", mas="Go ofrece +, -, *, / y % para operar con números enteros. El operador + también puede concatenar cadenas. Los operadores tienen reglas de precedencia, por lo que los paréntesis ayudan a expresar el orden deseado.",
  k=["+ suma números y también concatena cadenas.", "El operador % obtiene el resto de una división entera.", "Los paréntesis permiten aclarar la precedencia de las operaciones."],
  sit="Quieres calcular la suma, la diferencia y el producto de dos cantidades en una expresión. ¿Qué usarías?",
  cod="""package main

import "fmt"

func main() {
    a, b := 9, 4
    fmt.Println(a+b, a-b, a*b)
}""", h="calcula suma, diferencia y producto de dos enteros", pr=("El operador de multiplicación en Go es ___. (un carácter)", "*"), pr2=("El operador + también concatena ___. (7 letras)", "cadenas"), ec="usar ^ esperando que signifique potencia", out="13 5 36"),
K("División entera", d="operación entre enteros que descarta la parte fraccionaria", u="obtener un cociente entero sin decimales", mas="Cuando ambos operandos son enteros, / realiza división entera y trunca el resultado hacia cero. Por eso 7 / 2 da 3. Para conservar una fracción, uno de los valores debe convertirse a un tipo de punto flotante antes de dividir.",
  k=["La división entre enteros produce otro entero.", "La parte fraccionaria se trunca hacia cero.", "Convertir un operando a float64 permite una división decimal."],
  sit="Divides 7 elementos entre 2 grupos y necesitas solo el número entero de elementos por grupo. ¿Qué resultado obtienes?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println(7 / 2)
    fmt.Println(-7 / 2)
}""", h="muestra la división entera positiva y la truncada hacia cero", pr=("La expresión entera 7 / 2 produce ___. (un número)", "3"), pr2=("La división entera de Go trunca hacia ___. (4 letras)", "cero"), ec="esperar un resultado float al dividir dos valores int", out="3\n-3"),
K("Resto con porcentaje", d="operador % que devuelve el resto de una división entera", u="comprobar múltiplos y alternar valores", mas="El operador % calcula el residuo de dividir dos enteros. Una expresión n % 2 permite comprobar si un número es par o impar. En Go no se aplica a valores de punto flotante.",
  k=["% calcula el resto entre enteros.", "n % 2 es útil para comprobar paridad.", "El operador % no se aplica a float64."],
  sit="Quieres saber si un entero es divisible por 2 sin dejar residuo. ¿Qué operador usarías?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println(10 % 3)
    fmt.Println(8 % 2)
}""", h="muestra un resto distinto de cero y otro igual a cero", pr=("El operador que calcula el residuo entero es ___. (un carácter)", "%"), pr2=("El resto de 10 dividido entre 3 es ___. (un número)", "1"), ec="aplicar % a valores float en Go", out="1\n0"),
K("Conversión de tipos", d="construcción explícita de un valor de otro tipo compatible", u="combinar o presentar datos con tipos numéricos distintos", mas="Go no convierte automáticamente entre tipos numéricos diferentes. Se escribe el tipo destino seguido del valor entre paréntesis, como float64(cantidad) o int(3.9). Las conversiones numéricas pueden perder fracción o rango.",
  k=["Las conversiones numéricas deben escribirse de forma explícita.", "El tipo destino se escribe como una conversión, por ejemplo float64(n).", "Una conversión puede perder fracción o rango."],
  sit="Necesitas convertir un entero a decimal antes de dividir para conservar la fracción. ¿Qué operación aplicarías?",
  cod="""package main

import "fmt"

func main() {
    parte := float64(7) / 2
    fmt.Printf("%.1f\\n", parte)
}""", h="convierte un entero a float64 antes de dividir", pr=("Para convertir n al tipo float64 se escribe ___. (10 caracteres)", "float64(n)"), pr2=("Go realiza conversiones entre enteros y flotantes de forma ___. (9 letras)", "explícita"), ec="suponer que Go convierte int a float64 automáticamente en una operación", out="3.5"),
K("Precedencia de operadores", d="reglas que determinan el orden de evaluación de una expresión", u="interpretar cálculos compuestos correctamente", mas="En Go, multiplicación y división se evalúan antes que suma y resta. Los operadores del mismo nivel se evalúan de izquierda a derecha. Los paréntesis permiten indicar claramente otro orden.",
  k=["La multiplicación tiene mayor precedencia que la suma.", "Operadores del mismo nivel se evalúan de izquierda a derecha.", "Los paréntesis pueden cambiar el orden de evaluación."],
  sit="Quieres que una suma se realice antes de multiplicar su resultado. ¿Qué recurso usarías?",
  cod="""package main

import "fmt"

func main() {
    fmt.Println(2 + 3*4)
    fmt.Println((2 + 3) * 4)
}""", h="compara el resultado con y sin paréntesis", pr=("En 2 + 3*4, la operación de mayor precedencia es la ___. (14 letras)", "multiplicación"), pr2=("Para cambiar el orden de cálculo se usan ___. (10 letras)", "paréntesis"), ec="suponer que todas las operaciones se ejecutan estrictamente de izquierda a derecha", out="14\n20"),
K("Comparaciones", d="operadores que comparan valores y producen un resultado bool", u="construir condiciones para decisiones y bucles", mas="Los operadores ==, !=, <, <=, > y >= comparan valores compatibles y devuelven true o false. == comprueba igualdad y = asigna un valor, por lo que no son intercambiables. Las cadenas también se pueden comparar lexicográficamente.",
  k=["Las comparaciones producen valores bool.", "== compara igualdad y = asigna.", "Go define operadores de orden como < y >=."],
  sit="Necesitas obtener true o false al comparar si una edad es al menos 18. ¿Qué usarías?",
  cod="""package main

import "fmt"

func main() {
    edad := 18
    fmt.Println(edad >= 18, edad == 18)
}""", h="compara una edad con el umbral y con un valor exacto", pr=("El operador que comprueba igualdad es ___. (2 caracteres)", "=="), pr2=("Una comparación devuelve un valor de tipo ___. (4 letras)", "bool"), ec="escribir = cuando se quiere comparar dos valores", out="true true"),
K("Operadores lógicos", d="operadores &&, || y ! que combinan o niegan condiciones", u="expresar condiciones compuestas", mas="&& es verdadero cuando ambas condiciones lo son, mientras que || lo es cuando al menos una condición es verdadera. ! invierte el valor booleano. && y || usan evaluación de cortocircuito y no evalúan la parte derecha si el resultado ya está decidido.",
  k=["&& representa la conjunción lógica.", "|| representa la disyunción lógica.", "! invierte un valor bool y && y || usan cortocircuito."],
  sit="Una acción requiere que dos condiciones booleanas sean verdaderas al mismo tiempo. ¿Qué operador usarías para unirlas?",
  cod="""package main

import "fmt"

func main() {
    registrado, pago := true, false
    fmt.Println(registrado && pago)
    fmt.Println(registrado || pago)
    fmt.Println(!pago)
}""", h="muestra conjunción, disyunción y negación booleanas", pr=("El operador de conjunción lógica de Go es ___. (2 caracteres)", "&&"), pr2=("El operador de disyunción lógica es ___. (2 caracteres)", "||"), ec="usar una sola & o | al combinar condiciones booleanas", out="false\ntrue\ntrue"),
K("Condición en if", d="expresión booleana que controla si se ejecuta un bloque", u="ejecutar instrucciones solo cuando se cumple un caso", mas="La condición va después de if y antes de las llaves del bloque. Debe ser de tipo bool, sin paréntesis obligatorios alrededor. Las llaves de apertura y cierre son parte requerida de la sintaxis.",
  k=["if evalúa una condición bool.", "Go no requiere paréntesis alrededor de la condición.", "Las llaves del bloque if son obligatorias."],
  sit="Quieres ejecutar una instrucción solo si el saldo supera cero, usando un bloque con llaves. ¿Qué estructura escribirías?",
  cod="""package main

import "fmt"

func main() {
    saldo := 5
    if saldo > 0 {
        fmt.Println("disponible")
    }
}""", h="muestra un mensaje cuando el saldo es positivo", pr=("La palabra clave que inicia una condición es ___. (2 letras)", "if"), pr2=("A diferencia de algunos lenguajes, Go no necesita ___ alrededor de la condición. (10 letras)", "paréntesis"), ec="poner un punto y coma entre la condición y la llave de if", out="disponible"),
K("Rama else", d="bloque alternativo que se ejecuta cuando la condición de if es falsa", u="manejar el caso contrario de una decisión", mas="else se coloca después de la llave de cierre del bloque if y abre un bloque alternativo. Go exige que else aparezca en la misma línea que la llave de cierre anterior. Solo se ejecuta una de las dos ramas.",
  k=["else se ejecuta si la condición de if es false.", "else debe ir junto a la llave de cierre anterior.", "Solo se ejecuta una de las ramas if y else."],
  sit="Quieres mostrar un mensaje alternativo si no se cumple la condición del bloque if. ¿Qué rama añadirías?",
  cod="""package main

import "fmt"

func main() {
    edad := 16
    if edad >= 18 {
        fmt.Println("adulto")
    } else {
        fmt.Println("menor")
    }
}""", h="elige el mensaje correspondiente a una edad menor de 18", pr=("La rama alternativa de if se escribe con la palabra ___. (4 letras)", "else"), pr2=("La condición edad >= 18 es falsa, así que se ejecuta el bloque ___. (4 letras)", "else"), ec="poner else en una nueva línea después de la llave de cierre en Go", out="menor"),
K("Cadena else if", d="rama condicional adicional que prueba otro caso", u="evaluar varias alternativas en orden", mas="else if permite comprobar otra condición cuando la condición anterior fue falsa. Se pueden encadenar varias ramas y añadir un else final opcional. Se evalúan desde arriba y se ejecuta únicamente el primer bloque cuya condición es verdadera.",
  k=["else if prueba otra condición si las anteriores fallaron.", "Las condiciones se evalúan en orden.", "Un else final puede capturar los casos restantes."],
  sit="Debes clasificar una puntuación en alta, media o baja comprobando varios umbrales en orden. ¿Qué usarías?",
  cod="""package main

import "fmt"

func main() {
    puntos := 72
    if puntos >= 90 {
        fmt.Println("alto")
    } else if puntos >= 60 {
        fmt.Println("medio")
    } else {
        fmt.Println("bajo")
    }
}""", h="clasifica una puntuación con dos condiciones en orden", pr=("La rama que prueba una condición adicional se escribe ___. (8 letras y espacio)", "else if"), pr2=("Las condiciones de una cadena else if se prueban en ___. (5 letras)", "orden"), ec="comprobar primero una condición amplia que hace inalcanzables las más específicas", out="medio"),
K("Sentencia switch", d="estructura que elige una rama comparando una expresión con casos", u="organizar decisiones entre varios valores posibles", mas="switch evalúa una expresión y compara su resultado con los case. Go termina automáticamente cada caso cuando acaba su bloque, por lo que normalmente no se necesita break. default es opcional y cubre los valores que no coinciden.",
  k=["switch compara una expresión con distintos case.", "Los casos de Go no continúan automáticamente al siguiente.", "default es una rama opcional para otros valores."],
  sit="Un menú numérico tiene ramas distintas para las opciones 1, 2 y cualquier otro valor. ¿Qué estructura usarías?",
  cod="""package main

import "fmt"

func main() {
    opcion := 2
    switch opcion {
    case 1:
        fmt.Println("inicio")
    case 2:
        fmt.Println("ayuda")
    default:
        fmt.Println("desconocido")
    }
}""", h="selecciona la rama que coincide con la opción 2", pr=("La estructura que compara una expresión con varios casos es ___. (6 letras)", "switch"), pr2=("La rama opcional para valores no listados se llama ___. (7 letras)", "default"), ec="esperar que un case continúe al siguiente sin usar fallthrough", out="ayuda"),
K("Casos agrupados en switch", d="lista de valores separados por comas que comparte una rama", u="tratar varias opciones de la misma manera", mas="Un case puede incluir varios valores separados por comas. Si cualquiera coincide con la expresión de switch, se ejecuta su bloque. Los casos se revisan de arriba abajo y no se produce caída automática al caso siguiente.",
  k=["Un case puede enumerar varios valores separados por comas.", "Cualquiera de los valores del case puede seleccionar la rama.", "Go no continúa automáticamente al case siguiente."],
  sit="Tres códigos de estado deben generar la misma categoría y quieres evitar ramas duplicadas. ¿Cómo los agruparías?",
  cod="""package main

import "fmt"

func main() {
    codigo := 404
    switch codigo {
    case 200, 201, 202:
        fmt.Println("correcto")
    case 400, 404:
        fmt.Println("solicitud")
    }
}""", h="agrupa dos códigos para imprimir una categoría común", pr=("Los valores de un mismo case se separan con ___. (una palabra)", "comas"), pr2=("El caso 400, 404 coincide cuando el valor es ___. (3 números)", "404"), ec="escribir un case separado cuando varios valores comparten exactamente la misma acción", out="solicitud"),
K("Bucle for clásico", d="forma de for con inicialización, condición y actualización", u="repetir instrucciones usando un contador", mas="El for clásico tiene tres partes separadas por punto y coma: una instrucción inicial, una condición y una actualización. Cualquiera de las partes puede omitirse. La variable declarada en la inicialización pertenece al ámbito del bucle.",
  k=["El for clásico tiene inicialización, condición y actualización.", "Las tres partes se separan con punto y coma.", "La variable inicial del for queda limitada al bucle."],
  sit="Quieres contar desde 1 hasta 4 con una variable que se actualiza al final de cada vuelta. ¿Qué forma de for usarías?",
  cod="""package main

import "fmt"

func main() {
    for i := 1; i <= 4; i++ {
        fmt.Println(i)
    }
}""", h="recorre cuatro valores incrementando un contador", pr=("El bucle con tres partes separadas por punto y coma se llama for ___. (7 letras)", "clásico", "clasico"), pr2=("La parte que cambia el contador al terminar una vuelta es la ___. (13 letras)", "actualización", "actualizacion"), ec="olvidar cambiar la variable de control y crear un bucle infinito", out="1\n2\n3\n4"),
K("For con condición", d="forma de for que repite mientras una condición siga siendo verdadera", u="escribir repeticiones con una condición de parada", mas="Un for puede contener solo una condición, como for n > 0. Antes de cada vuelta se comprueba la condición y, cuando es falsa, termina. Es la forma de bucle condicional que reemplaza al while de otros lenguajes.",
  k=["La condición se comprueba antes de cada vuelta.", "El bucle termina al volverse falsa la condición.", "for con condición cumple el papel de while."],
  sit="Debes repetir una operación mientras un contador sea mayor que cero, sin declarar sus partes en la cabecera. ¿Qué bucle usarías?",
  cod="""package main

import "fmt"

func main() {
    n := 3
    for n > 0 {
        fmt.Println(n)
        n--
    }
}""", h="cuenta hacia atrás con un for condicionado", pr=("El for que solo contiene una condición se repite mientras esta sea ___. (9 letras)", "verdadera"), pr2=("En Go, un for con condición puede reemplazar a ___. (5 letras)", "while"), ec="olvidar actualizar el estado que controla la condición del for", out="3\n2\n1"),
K("range sobre cadenas", d="recorrido Unicode que produce índice en bytes y valor rune", u="procesar texto por puntos de código", mas="Al usar range sobre una cadena, cada iteración devuelve el índice en bytes de la runa y la runa misma. Si solo se necesita el carácter, el índice se puede descartar con _. Una letra multibyte hace que los índices no avancen de uno en uno.",
  k=["range sobre string devuelve un índice de byte y una rune.", "El índice marca el inicio UTF-8 de cada runa.", "El guion bajo descarta el índice si no se necesita."],
  sit="Quieres recorrer el texto «Go» carácter por carácter como puntos de código Unicode. ¿Qué usarías?",
  cod="""package main

import "fmt"

func main() {
    for indice, letra := range "Go" {
        fmt.Println(indice, string(letra))
    }
}""", h="muestra el índice en bytes y el carácter de cada posición", pr=("La forma idiomática de recorrer valores de una cadena usa ___. (5 letras)", "range"), pr2=("El segundo valor de range sobre string es una ___. (4 letras)", "rune"), ec="suponer que el índice de range siempre coincide con el número del carácter", out="0 G\n1 o"),
K("break", d="sentencia que termina inmediatamente el bucle más interno", u="salir de una repetición al cumplirse una condición", mas="break detiene el bucle envolvente más cercano y continúa la ejecución después de él. Puede utilizarse dentro de for y switch. Una etiqueta permite salir de bucles externos cuando hay varios niveles anidados.",
  k=["break termina el bucle más cercano.", "La ejecución continúa después del bucle interrumpido.", "Las etiquetas permiten salir de bucles externos anidados."],
  sit="Una búsqueda debe terminar en cuanto encuentra el primer valor que cumple el criterio. ¿Qué sentencia usarías?",
  cod="""package main

import "fmt"

func main() {
    for n := 1; n <= 5; n++ {
        if n == 3 {
            break
        }
        fmt.Println(n)
    }
}""", h="detiene el bucle antes de imprimir el valor 3", pr=("La sentencia que termina un bucle inmediatamente es ___. (5 letras)", "break"), pr2=("break detiene el bucle envolvente más ___. (7 letras)", "cercano"), ec="usar break esperando que solo salte una iteración", out="1\n2"),
K("continue", d="sentencia que omite el resto de la iteración actual", u="saltar elementos que no requieren procesamiento", mas="continue termina la iteración actual y pasa a comprobar la siguiente. No termina el bucle completo, a diferencia de break. En un for clásico, la instrucción de actualización sigue ejecutándose después de continue.",
  k=["continue omite el resto de la vuelta actual.", "El bucle continúa con la siguiente iteración.", "continue no termina la repetición completa."],
  sit="Al recorrer números, quieres ignorar los pares y seguir revisando los siguientes. ¿Qué sentencia usarías?",
  cod="""package main

import "fmt"

func main() {
    for n := 1; n <= 5; n++ {
        if n%2 == 0 {
            continue
        }
        fmt.Println(n)
    }
}""", h="omite los pares e imprime los impares", pr=("La sentencia que salta al siguiente ciclo es ___. (8 letras)", "continue"), pr2=("A diferencia de break, continue no termina el ___. (5 letras)", "bucle"), ec="usar break en lugar de continue cuando solo se quiere omitir una vuelta", out="1\n3\n5"),
K("Ámbito de bloque", d="región del código donde un nombre declarado puede utilizarse", u="mantener variables locales a una condición o repetición", mas="Una variable declarada dentro de un bloque solo está disponible desde su declaración hasta el final de ese bloque. Las llaves de if, switch y for crean bloques. Un nombre local puede ocultar otro nombre de un bloque exterior, lo que se conoce como sombreado.",
  k=["Las llaves delimitan bloques con ámbito propio.", "Un nombre local solo se usa dentro de su ámbito.", "Una declaración interna puede ocultar un nombre exterior."],
  sit="Quieres crear un contador que solo exista mientras se ejecuta una condición, sin exponerlo al resto de la función. ¿Qué aprovecharías?",
  cod="""package main

import "fmt"

func main() {
    total := 5
    if extra := 2; extra > 0 {
        fmt.Println(total + extra)
    }
    fmt.Println(total)
}""", h="usa una variable local al if y luego muestra el valor exterior", pr=("La región donde se puede usar un nombre se llama su ___. (6 letras)", "ámbito", "ambito"), pr2=("Las llaves delimitan el ámbito de un ___. (6 letras)", "bloque"), ec="intentar usar fuera de un if una variable declarada dentro de él", out="7\n5"),
]
