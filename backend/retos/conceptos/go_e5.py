"""Go · Etapa 5: concurrencia, herramientas y recursos modernos."""
from ..generador import K

LISTA = [
K("Concurrencia", d="diseño de programas que gestionan varias tareas en progreso", u="coordinar trabajos independientes con goroutines y canales", mas="Go ofrece goroutines ligeras y canales para coordinar el intercambio de datos. La concurrencia describe tareas que progresan durante periodos que se solapan; no implica necesariamente ejecución simultánea en varios núcleos. Compartir datos requiere sincronización segura.",
  k=["Una goroutine es una unidad ligera de ejecución de Go.", "Los canales permiten coordinar y comunicar goroutines.", "Concurrencia no significa necesariamente paralelismo."],
  sit="Un programa necesita iniciar una tarea independiente y recibir su resultado mediante una comunicación segura. ¿Qué enfoque de Go aplicarías?",
  cod="""package main

import "fmt"

func main() {
    resultado := make(chan string)
    go func() { resultado <- "tarea lista" }()
    fmt.Println(<-resultado)
}""", h="recibe el resultado de una tarea concurrente por un canal", pr=("El diseño de tareas que pueden progresar de forma solapada se llama ___. (12 letras)", "concurrencia"), pr2=("El código comunica el resultado a través de un ___. (5 letras)", "canal"), ec="creer que concurrencia siempre significa ejecutar en paralelo", out="tarea lista"),
K("Herramientas", d="comandos del toolchain que formatean, construyen y revisan proyectos Go", u="mantener y verificar código Go con un flujo reproducible", mas="El comando gofmt aplica formato al código; go test ejecuta pruebas; go vet busca construcciones sospechosas; go doc muestra documentación; y go mod administra módulos y dependencias. El comando go build compila paquetes. Estas herramientas vienen con la distribución de Go.",
  k=["gofmt aplica el formato convencional al código.", "go test ejecuta pruebas del proyecto.", "go vet revisa posibles errores y go mod gestiona módulos."],
  sit="Necesitas recordar los comandos del toolchain que formatean, prueban y analizan un proyecto Go. ¿Qué conjunto consultarías?",
  cod="""package main

import "fmt"

func main() {
    comandos := []string{"gofmt", "go test", "go vet", "go mod"}
    for _, comando := range comandos {
        fmt.Println(comando)
    }
}""", h="muestra cuatro herramientas habituales del toolchain", pr=("La herramienta que da formato al código fuente se llama ___. (5 letras)", "gofmt"), pr2=("El comando que ejecuta las pruebas del proyecto es go ___. (4 letras)", "test"), ec="formatear código manualmente y omitir las herramientas incluidas con Go", out="gofmt\ngo test\ngo vet\ngo mod"),
K("Goroutines", d="tareas ligeras de ejecución iniciadas con la palabra clave go", u="ejecutar una función concurrentemente", mas="Una goroutine se inicia anteponiendo go a una llamada de función. El planificador de Go administra muchas goroutines sobre un conjunto de hilos del sistema operativo. El programa debe sincronizar para que el trabajo termine antes de salir.",
  k=["go antes de una llamada inicia una goroutine.", "El planificador de Go gestiona las goroutines.", "El programa debe esperar o sincronizar para asegurar que la tarea termine."],
  sit="Quieres lanzar una función ligera de forma concurrente en lugar de ejecutarla en la misma secuencia. ¿Qué mecanismo usarías?",
  cod="""package main

import "fmt"

func main() {
    hecho := make(chan int)
    go func() { hecho <- 21 }()
    valor := <-hecho
    fmt.Println(valor)
}""", h="inicia una goroutine y espera su resultado por un canal", pr=("Una tarea ligera iniciada con go se llama ___. (9 letras)", "goroutine"), pr2=("La palabra que inicia una llamada concurrente es ___. (2 letras)", "go"), ec="iniciar una goroutine y terminar main sin esperar su resultado", out="21"),
K("Canales", d="tipos de comunicación que envían valores entre goroutines", u="coordinar productores y consumidores concurrentes", mas="Un canal se crea con make(chan T) y permite enviar valores con <- y recibirlos también con <-. Un canal sin búfer sincroniza el envío con una recepción. El tipo del canal determina qué valores transporta.",
  k=["make(chan T) crea un canal para valores de tipo T.", "El operador <- se usa para enviar o recibir.", "Un canal sin búfer sincroniza envío y recepción."],
  sit="Dos goroutines necesitan intercambiar un entero y sincronizar el momento de la transferencia. ¿Qué estructura usarías?",
  cod="""package main

import "fmt"

func main() {
    canal := make(chan int)
    go func() { canal <- 8 }()
    fmt.Println(<-canal)
}""", h="envía y recibe un entero mediante un canal sin búfer", pr=("La estructura tipada para comunicar goroutines se llama ___. (5 letras)", "canal"), pr2=("El operador de envío y recepción de canales es ___. (2 caracteres)", "<-"), ec="enviar por un canal sin búfer sin que exista una recepción correspondiente", out="8"),
K("Canales con búfer", d="canales que permiten guardar una cantidad limitada de valores antes de recibirlos", u="separar temporalmente el ritmo de productores y consumidores", mas="make(chan T, n) crea un canal con capacidad n. Se puede enviar mientras no se llene y recibir mientras haya datos; al llenarse, el envío bloquea hasta que se libere espacio. Un canal con búfer no sustituye la coordinación necesaria para terminar tareas.",
  k=["La capacidad se indica como segundo argumento de make.", "Un canal con búfer puede guardar valores antes de recibirlos.", "Enviar en un canal lleno bloquea hasta que haya espacio."],
  sit="Un productor debe poder colocar dos resultados antes de que el consumidor empiece a leerlos. ¿Qué clase de canal necesita?",
  cod="""package main

import "fmt"

func main() {
    canal := make(chan int, 2)
    canal <- 4
    canal <- 6
    fmt.Println(<-canal, <-canal)
}""", h="envía dos valores a un canal con búfer y luego los recibe", pr=("El segundo argumento make(chan int, 2) define la ___. (9 letras)", "capacidad"), pr2=("Un canal con búfer de capacidad dos puede almacenar ___ valores sin recibirlos. (un número)", "2", "dos"), ec="enviar más valores que la capacidad de un canal con búfer sin leerlo", out="4 6"),
K("Canales direccionales", d="tipos de canal limitados a enviar o recibir valores", u="restringir y documentar el uso de canales en parámetros", mas="chan<- T es un canal de solo envío y <-chan T es de solo recepción. La dirección se usa comúnmente en parámetros de función para limitar las operaciones permitidas. Un canal bidireccional puede pasarse a cualquiera de esas direcciones compatibles.",
  k=["chan<- T permite enviar valores de tipo T.", "<-chan T permite recibir valores de tipo T.", "Los canales direccionales hacen explícito el flujo permitido."],
  sit="Una función solo debe publicar resultados y no leer del canal que recibe. ¿Qué tipo de parámetro declararías?",
  cod="""package main

import "fmt"

func publicar(salida chan<- int) {
    salida <- 12
}

func main() {
    canal := make(chan int, 1)
    publicar(canal)
    fmt.Println(<-canal)
}""", h="limita la función a enviar por su canal", pr=("Un canal de solo envío se escribe ___. (8 caracteres)", "chan<- T"), pr2=("La función publicar recibe un canal de solo ___. (5 letras)", "envío", "envio"), ec="intentar recibir desde un canal declarado como solo envío", out="12"),
K("Cerrar canales", d="operación que indica que no se enviarán más valores por un canal", u="permitir que receptores detecten el final de un flujo", mas="close(canal) marca que no habrá nuevos envíos; solo el emisor o quien conoce el ciclo de vida debería cerrarlo. Recibir de un canal cerrado y vacío devuelve el valor cero inmediatamente. En el patrón for range, el bucle termina al cerrarse el canal.",
  k=["close marca el canal como cerrado para nuevos envíos.", "Recibir de un canal cerrado y vacío devuelve el valor cero.", "range sobre un canal termina cuando este se cierra y se vacía."],
  sit="Un productor terminó de enviar datos y necesita avisar al consumidor para que finalice su recorrido. ¿Qué operación usarías?",
  cod="""package main

import "fmt"

func main() {
    canal := make(chan int, 2)
    canal <- 3
    canal <- 5
    close(canal)
    for valor := range canal {
        fmt.Println(valor)
    }
}""", h="cierra un canal y recorre los valores restantes", pr=("La operación que señala que no habrá más envíos es ___. (5 letras)", "close"), pr2=("El bucle range sobre un canal cerrado termina al consumir los valores y detectar el ___. (6 letras)", "cierre"), ec="cerrar un canal desde varios emisores sin coordinar quién lo cierra", out="3\n5"),
K("sync.WaitGroup", d="primitiva que espera a que un conjunto de goroutines termine", u="sincronizar el final de varias tareas", mas="Un WaitGroup cuenta tareas pendientes. Add incrementa el contador, Done lo decrementa y Wait bloquea hasta llegar a cero. Si Add se llama desde la goroutine nueva, debe ejecutarse antes de iniciar esa goroutine para evitar una carrera de coordinación.",
  k=["Add registra tareas en el contador del grupo.", "Done señala que una tarea terminó.", "Wait espera hasta que el contador llegue a cero."],
  sit="Una función principal debe esperar a que finalicen todas las goroutines iniciadas antes de continuar. ¿Qué primitiva usarías?",
  cod="""package main

import (
    "fmt"
    "sync"
)

func main() {
    var grupo sync.WaitGroup
    grupo.Add(1)
    go func() {
        defer grupo.Done()
        fmt.Println("terminada")
    }()
    grupo.Wait()
}""", h="espera una goroutine y registra su finalización con defer", pr=("El tipo de sync que permite esperar varias tareas se llama ___. (9 letras)", "WaitGroup"), pr2=("El método que bloquea hasta terminar el grupo es ___. (4 letras)", "Wait"), ec="llamar Done más veces que Add y hacer negativo el contador", out="terminada"),
K("sync.Mutex", d="candado que permite acceso exclusivo a una sección crítica", u="proteger datos compartidos entre goroutines", mas="Un Mutex proporciona Lock y Unlock para asegurar que una sola goroutine entre a la vez en una sección crítica. Unlock se suele diferir justo después de Lock para garantizar que se libere. Un mutex evita carreras solo si todos los accesos compartidos respetan el mismo bloqueo.",
  k=["Lock adquiere el mutex y Unlock lo libera.", "El mutex protege una sección crítica de accesos simultáneos.", "Todos los accesos relevantes deben usar el mismo bloqueo."],
  sit="Varias goroutines actualizan un contador compartido y necesitas impedir escrituras simultáneas. ¿Qué primitiva usarías?",
  cod="""package main

import (
    "fmt"
    "sync"
)

func main() {
    var candado sync.Mutex
    contador := 0
    candado.Lock()
    contador++
    candado.Unlock()
    fmt.Println(contador)
}""", h="protege una actualización con un mutex", pr=("El candado de exclusión mutua de sync se llama ___. (5 letras)", "Mutex"), pr2=("El método que libera un mutex es ___. (6 letras)", "Unlock"), ec="bloquear un mutex y olvidar desbloquearlo en un camino de ejecución", out="1"),
K("sync.Once", d="primitiva que garantiza que una función se ejecute una sola vez", u="realizar inicialización única desde varias goroutines", mas="Una variable sync.Once coordina llamadas concurrentes a Do y ejecuta la función pasada una sola vez. Las llamadas siguientes esperan si la primera sigue ejecutándose y después retornan sin repetir la función. Cada instancia Once se utiliza para una única inicialización.",
  k=["Do ejecuta la función proporcionada una sola vez por instancia.", "sync.Once es seguro para uso concurrente.", "Las llamadas posteriores a Do no repiten la inicialización."],
  sit="Varios componentes podrían solicitar una misma inicialización y quieres que ocurra exactamente una vez. ¿Qué tipo usarías?",
  cod="""package main

import (
    "fmt"
    "sync"
)

func main() {
    var unaVez sync.Once
    iniciar := func() { fmt.Println("iniciado") }
    unaVez.Do(iniciar)
    unaVez.Do(iniciar)
}""", h="ejecuta la función de inicialización una sola vez", pr=("La primitiva que ejecuta una acción una vez se llama sync.___. (4 letras)", "Once"), pr2=("El método de sync.Once que recibe la acción es ___. (2 letras)", "Do"), ec="crear una variable Once nueva en cada llamada y esperar que comparta su estado", out="iniciado"),
K("Pipeline de canales", d="secuencia de etapas concurrentes que reciben y envían valores por canales", u="componer trabajos como productor, transformación y consumidor", mas="Un pipeline separa el procesamiento en etapas que se comunican mediante canales. Cada etapa recibe del canal anterior, transforma los datos y envía al siguiente. Un diseño completo debe definir cómo se cierran canales y cómo se cancelan tareas para evitar goroutines bloqueadas.",
  k=["Cada etapa de un pipeline puede procesar valores recibidos por canal.", "Los canales conectan la salida de una etapa con la siguiente.", "El ciclo de vida de los canales debe evitar goroutines bloqueadas."],
  sit="Un flujo debe generar números, transformarlos y entregar los resultados a una etapa posterior. ¿Qué patrón de concurrencia aplicarías?",
  cod="""package main

import "fmt"

func main() {
    entrada := make(chan int, 3)
    salida := make(chan int, 3)
    for _, n := range []int{1, 2, 3} {
        entrada <- n
    }
    close(entrada)
    for n := range entrada {
        salida <- n * 10
    }
    close(salida)
    for n := range salida {
        fmt.Println(n)
    }
}""", h="conecta una etapa de transformación entre entrada y salida", pr=("Una sucesión de etapas conectadas por canales se llama ___. (8 letras)", "pipeline"), pr2=("Cada etapa entrega valores a la siguiente mediante ___. (7 letras)", "canales"), ec="olvidar definir el cierre o la cancelación en una etapa que espera datos", out="10\n20\n30"),
K("Resultados concurrentes deterministas", d="recolección y ordenamiento de resultados para ocultar el orden de finalización", u="producir una salida estable desde tareas concurrentes", mas="Las goroutines pueden terminar en distinto orden y no se debe depender de ese orden. Un patrón útil es enviar resultados a un canal, esperar a todos los trabajadores y ordenar los resultados antes de mostrarlos. Así se conserva la concurrencia y se obtiene una salida determinista.",
  k=["El orden de finalización de goroutines puede variar.", "Un canal puede recolectar los resultados de trabajadores.", "Ordenar los resultados permite presentar una salida estable."],
  sit="Varias tareas terminan en cualquier orden, pero el reporte final debe mostrar sus valores siempre ordenados. ¿Qué estrategia aplicarías?",
  cod="""package main

import (
    "fmt"
    "sort"
    "sync"
)

func main() {
    resultados := make(chan int, 3)
    var grupo sync.WaitGroup
    for _, n := range []int{3, 1, 2} {
        grupo.Add(1)
        go func(valor int) {
            defer grupo.Done()
            resultados <- valor
        }(n)
    }
    grupo.Wait()
    close(resultados)
    ordenados := make([]int, 0, 3)
    for valor := range resultados {
        ordenados = append(ordenados, valor)
    }
    sort.Ints(ordenados)
    fmt.Println(ordenados)
}""", h="recolecta resultados concurrentes y los ordena antes de imprimir", pr=("La propiedad de que una salida sea igual en cada ejecución se llama ___. (12 letras)", "determinismo"), pr2=("El ejemplo usa sort.Ints para ordenar los resultados de forma ___. (10 letras)", "ascendente"), ec="imprimir desde cada goroutine y depender del orden de planificación", out="[1 2 3]"),
K("Genéricos", d="funciones y tipos parametrizados por uno o varios tipos", u="reutilizar lógica con distintos tipos sin usar interface{}", mas="Go admite parámetros de tipo en funciones y tipos desde la versión 1.18. El parámetro se declara entre corchetes y se usa en los argumentos y resultados. El compilador instancia el código para los tipos concretos usados.",
  k=["Los parámetros de tipo se escriben entre corchetes.", "Los genéricos están disponibles desde Go 1.18.", "Una función genérica puede usarse con varios tipos compatibles."],
  sit="Una misma función debe devolver intacto un entero o una cadena conservando su tipo estático. ¿Qué característica usarías?",
  cod="""package main

import "fmt"

func identidad[T any](valor T) T {
    return valor
}

func main() {
    fmt.Println(identidad(7), identidad("Go"))
}""", h="usa una función genérica con un entero y con una cadena", pr=("Las funciones parametrizadas por tipos se llaman ___. (9 letras)", "genéricas", "genericas"), pr2=("Los parámetros de tipo se escriben entre ___. (9 letras)", "corchetes"), ec="usar paréntesis en lugar de corchetes para declarar parámetros de tipo", out="7 Go"),
K("Restricciones genéricas", d="interfaces que limitan los tipos permitidos en parámetros genéricos", u="especificar operaciones disponibles para los tipos aceptados", mas="Un parámetro de tipo necesita una restricción que describa qué tipos y operaciones admite. La restricción any permite cualquier tipo. Las interfaces con conjuntos de tipos, como ~int | ~float64, pueden declarar restricciones para funciones genéricas.",
  k=["Una restricción indica los tipos admitidos por un parámetro genérico.", "any es la restricción más amplia.", "Una interfaz puede combinar tipos con el operador |."],
  sit="Una función genérica solo debe aceptar enteros y flotantes, pues usa operaciones numéricas comunes. ¿Qué definirías?",
  cod="""package main

import "fmt"

type Numero interface{ ~int | ~float64 }

func doble[T Numero](n T) T { return n * 2 }

func main() { fmt.Println(doble(3), doble(1.5)) }""", h="restringe una función genérica a int o float64", pr=("La interfaz que limita los tipos de un parámetro genérico es una ___. (11 letras)", "restricción", "restriccion"), pr2=("El operador que reúne tipos alternativos en una restricción es ___. (un carácter)", "|"), ec="omitir de la restricción una operación que la función genérica necesita", out="6 3"),
K("Restricción comparable", d="restricción predefinida que permite comparar valores con == y !=", u="usar tipos como claves de mapas genéricos", mas="La restricción comparable permite utilizar == y != sobre valores del parámetro. Es necesaria para usar ese parámetro como clave de map. Algunos tipos compuestos que contienen campos no comparables, como slices, no satisfacen comparable.",
  k=["comparable permite usar == y != en el parámetro genérico.", "Las claves de mapas deben ser comparables.", "Los slices no son tipos comparables."],
  sit="Una función genérica usa valores como claves de un mapa y necesita admitir solo tipos comparables. ¿Qué restricción indicarías?",
  cod="""package main

import "fmt"

func contar[T comparable](valores []T, buscado T) int {
    cantidad := 0
    for _, valor := range valores {
        if valor == buscado {
            cantidad++
        }
    }
    return cantidad
}

func main() { fmt.Println(contar([]string{"go", "py", "go"}, "go")) }""", h="cuenta coincidencias usando la comparación de valores genéricos", pr=("La restricción predefinida para tipos comparables se llama ___. (10 letras)", "comparable"), pr2=("Los slices no se pueden usar directamente como claves de un ___. (3 letras)", "map"), ec="usar comparable con un tipo que contiene campos no comparables como slices", out="2"),
K("JSON en memoria", d="codificación y decodificación de datos JSON desde valores Go", u="intercambiar datos estructurados sin leer ni escribir archivos", mas="encoding/json convierte valores Go a JSON con json.Marshal y decodifica JSON con json.Unmarshal. Los campos exportados de una estructura participan en la codificación; una etiqueta json permite personalizar el nombre. La conversión en memoria no requiere acceso a archivos ni red.",
  k=["json.Marshal convierte un valor Go en bytes JSON.", "json.Unmarshal decodifica bytes JSON en un valor Go.", "Los campos no exportados de un struct no se codifican."],
  sit="Necesitas transformar una estructura Go a JSON y volver a decodificarla sin usar archivos ni red. ¿Qué paquete usarías?",
  cod="""package main

import (
    "encoding/json"
    "fmt"
)

type Persona struct {
    Nombre string `json:"nombre"`
    Edad int `json:"edad"`
}

func main() {
    datos, _ := json.Marshal(Persona{Nombre: "Ana", Edad: 9})
    fmt.Println(string(datos))
}""", h="codifica una estructura Go como un objeto JSON", pr=("El paquete estándar para codificar y decodificar JSON es encoding/ ___. (4 letras)", "json"), pr2=("La función que codifica un valor Go a JSON se llama json.___. (7 letras)", "Marshal"), ec="olvidar que la codificación JSON incluye campos exportados y no los privados", out="{\"nombre\":\"Ana\",\"edad\":9}"),
K("sort.Slice", d="función que ordena un slice usando una condición de comparación", u="ordenar registros según uno de sus campos", mas="sort.Slice recibe un slice y una función less que compara los elementos por índice. La función reordena el slice en el lugar y no garantiza estabilidad para elementos equivalentes. Los tipos con un orden natural pueden usar funciones más sencillas como sort.Ints.",
  k=["sort.Slice ordena el slice en el lugar.", "La función less define el orden de comparación.", "sort.Slice no garantiza un orden estable para elementos equivalentes."],
  sit="Una lista de registros debe ordenarse por un campo elegido que no es el orden natural del tipo. ¿Qué función usarías?",
  cod="""package main

import (
    "fmt"
    "sort"
)

type Alumno struct{ Nombre string; Nota int }

func main() {
    alumnos := []Alumno{{"Ana", 8}, {"Luis", 6}}
    sort.Slice(alumnos, func(i, j int) bool {
        return alumnos[i].Nota < alumnos[j].Nota
    })
    fmt.Println(alumnos[0].Nombre, alumnos[1].Nombre)
}""", h="ordena alumnos por nota ascendente usando less", pr=("La función que ordena con un comparador personalizado es sort.___. (5 letras)", "Slice"), pr2=("El comparador less devuelve true cuando el elemento de índice i debe ir antes de ___. (una letra)", "j"), ec="escribir un comparador que no produzca un orden coherente", out="Luis Ana"),
K("sort.Search", d="búsqueda binaria del primer índice que satisface una condición", u="encontrar eficientemente un límite en datos ordenados", mas="sort.Search(n, f) devuelve el primer índice i en [0,n) para el que f(i) es true, o n si no existe. La condición debe ser monótona: primero falsa y después verdadera. Para buscar valores concretos, los datos deben estar ordenados de acuerdo con esa condición.",
  k=["sort.Search realiza una búsqueda binaria sobre índices.", "La condición debe cambiar como máximo una vez de false a true.", "Si no encuentra índice válido, devuelve n."],
  sit="Una lista ordenada debe localizar el primer elemento que alcanza un umbral con búsqueda binaria. ¿Qué función usarías?",
  cod="""package main

import (
    "fmt"
    "sort"
)

func main() {
    valores := []int{2, 4, 6, 8, 10}
    indice := sort.Search(len(valores), func(i int) bool {
        return valores[i] >= 7
    })
    fmt.Println(indice, valores[indice])
}""", h="encuentra el primer valor mayor o igual que siete", pr=("La función estándar que busca con una condición binaria es sort.___. (6 letras)", "Search"), pr2=("Si no encuentra un índice, sort.Search devuelve el límite ___. (una letra)", "n"), ec="usar sort.Search sobre datos que no están ordenados según el predicado", out="3 8"),
K("gofmt", d="formateador oficial que aplica un estilo uniforme a archivos Go", u="mantener código consistente sin debatir preferencias de formato", mas="gofmt analiza el código Go y lo reescribe con el formato convencional. Se puede ejecutar sobre archivos o usar gofmt -w para escribir los cambios en el mismo archivo. El formato uniforme facilita revisar diffs y mantener repositorios.",
  k=["gofmt aplica el formato convencional del lenguaje.", "gofmt -w escribe los cambios en los archivos indicados.", "El formato uniforme hace más sencillas las revisiones de cambios."],
  sit="Quieres aplicar automáticamente el formato convencional de Go a un archivo fuente. ¿Qué herramienta ejecutarías?",
  cod="""package main

import (
    "fmt"
    "go/format"
)

func main() {
    fuente := []byte("package demo\\nfunc Hola(){fmt.Println(\\"hola\\")}\\n")
    formateado, _ := format.Source(fuente)
    fmt.Print(string(formateado))
}""", h="formatea una fuente Go en memoria con la biblioteca go/format", pr=("El formateador oficial de Go se llama ___. (5 letras)", "gofmt"), pr2=("La opción que reescribe el archivo en el mismo lugar es ___. (2 caracteres)", "-w"), ec="formatear código Go con un estilo personal en lugar de ejecutar gofmt", out="package demo\n\nfunc Hola() { fmt.Println(\"hola\") }\n"),
K("Pruebas con go test", d="comando y paquete para ejecutar pruebas automatizadas de Go", u="comprobar comportamientos de funciones de forma repetible", mas="go test descubre archivos terminados en _test.go y ejecuta funciones de prueba con la firma TestXxx(t *testing.T). El paquete testing proporciona aserciones mediante condiciones y métodos para reportar fallos. Las pruebas deben ser deterministas y no depender de servicios externos.",
  k=["Los archivos de prueba suelen terminar en _test.go.", "Una función de prueba usa la firma TestNombre(t *testing.T).", "go test ejecuta las pruebas del paquete."],
  sit="Quieres ejecutar pruebas automatizadas almacenadas junto al paquete en archivos terminados en _test.go. ¿Qué comando usarías?",
  cod="""package main

import "fmt"

func sumar(a, b int) int { return a + b }

func main() {
    if sumar(2, 3) != 5 {
        panic("prueba fallida")
    }
    fmt.Println("prueba superada")
}""", h="comprueba una suma con una condición y reporta el resultado", pr=("El comando que ejecuta las pruebas Go es go ___. (4 letras)", "test"), pr2=("Los archivos de pruebas automatizadas suelen terminar en ___. (8 caracteres)", "_test.go"), ec="escribir pruebas que dependan del orden de ejecución o de datos externos", out="prueba superada"),
]
