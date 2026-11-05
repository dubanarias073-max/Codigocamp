// Lecciones de Go. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"Go es simple y rápido, creado en Google.",
    p:["package main es obligatorio", "fmt.Println imprime"],
    c:`package main

import "fmt"

func main() {
  fmt.Println("¡Hola, CódigoCamp!")
}` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:":= crea una variable deduciendo el tipo.",
    p:["var o :=", "if sin paréntesis"],
    c:`package main

import "fmt"

func main() {
  edad := 20
  if edad >= 18 {
    fmt.Println("Mayor de edad")
  }
}` },
  { m:"Fundamentos", t:"Bucles", x:"En Go solo existe for, y sirve para todo tipo de repetición.",
    p:["for inicio; condición; paso", "No lleva paréntesis"],
    c:`package main

import "fmt"

func main() {
  for i := 1; i <= 5; i++ {
    fmt.Println("Vuelta", i)
  }
}` },
  { m:"Fundamentos", t:"Funciones", x:"func define una función. Los tipos van después del nombre.",
    p:["Indica el tipo del resultado al final", "return devuelve el valor"],
    c:`package main

import "fmt"

func doble(n int) int {
  return n * 2
}

func main() {
  fmt.Println(doble(21))
}` },
  { m:"Intermedio", t:"Slices y mapas", x:"Un slice es una lista dinámica y un mapa asocia claves con valores. append agrega elementos y range los recorre.",
    p:["[]int es un slice de enteros", "append devuelve el slice actualizado", "map[string]int asocia textos con enteros"],
    c:"package main\n\nimport \"fmt\"\n\nfunc main() {\n  nums := []int{1, 2, 3}\n  nums = append(nums, 4)\n  for i, n := range nums {\n    fmt.Println(i, n)\n  }\n\n  edades := map[string]int{\"Ana\": 20, \"Luis\": 25}\n  edades[\"Marta\"] = 30\n  fmt.Println(len(edades), edades[\"Ana\"])\n}",
    r:"Suma todos los elementos de nums con un for range.",
    e:"Olvidar asignar el resultado de append: nums = append(nums, 4)." },
  { m:"Intermedio", t:"Structs y métodos", x:"Go no tiene clases: usa struct para agrupar datos y métodos con receptor para darles comportamiento.",
    p:["struct define campos", "Un método usa un receptor: func (p Persona) Hola()", "Los nombres en mayúscula se exportan"],
    c:"package main\n\nimport \"fmt\"\n\ntype Persona struct {\n  Nombre string\n  Edad   int\n}\n\nfunc (p Persona) Saludar() string {\n  return fmt.Sprintf(\"Hola, soy %s y tengo %d\", p.Nombre, p.Edad)\n}\n\nfunc main() {\n  p := Persona{Nombre: \"Ana\", Edad: 20}\n  fmt.Println(p.Saludar())\n}",
    r:"Añade un método EsMayor() que devuelva un bool." },
  { m:"Avanzado", t:"Errores y defer", x:"Go devuelve los errores como un valor. Se comprueban con if err != nil. defer retrasa una acción hasta el final de la función.",
    p:["Una función puede devolver (resultado, error)", "if err != nil maneja el error", "defer se ejecuta al salir de la función"],
    c:"package main\n\nimport (\n  \"errors\"\n  \"fmt\"\n)\n\nfunc dividir(a, b int) (int, error) {\n  if b == 0 {\n    return 0, errors.New(\"no se puede dividir entre 0\")\n  }\n  return a / b, nil\n}\n\nfunc main() {\n  defer fmt.Println(\"Fin\")\n  if r, err := dividir(10, 0); err != nil {\n    fmt.Println(\"Error:\", err)\n  } else {\n    fmt.Println(r)\n  }\n}",
    r:"Cambia los argumentos para que la división sea válida.",
    e:"Ignorar el error con _ esconde fallos: compruébalo siempre." },
  { m:"Avanzado", t:"Punteros e interfaces", x:"Un puntero guarda la dirección de una variable. Una interfaz se cumple automáticamente si el tipo tiene los métodos.",
    p:["& obtiene la dirección y * accede al valor", "Un puntero permite modificar el original", "Las interfaces se implementan de forma implícita"],
    c:"package main\n\nimport \"fmt\"\n\ntype Sonido interface{ Hacer() string }\n\ntype Perro struct{}\n\nfunc (Perro) Hacer() string { return \"Guau\" }\n\nfunc duplicar(n *int) { *n = *n * 2 }\n\nfunc main() {\n  x := 5\n  duplicar(&x)\n  fmt.Println(x)\n\n  var s Sonido = Perro{}\n  fmt.Println(s.Hacer())\n}",
    r:"Crea otro tipo que también tenga Hacer() y úsalo como Sonido." },
  { m:"Experto", t:"Goroutines y canales", x:"Una goroutine es una función concurrente ligera y un canal comunica datos entre ellas.",
    p:["go f() lanza una goroutine", "ch <- v envía y <-ch recibe", "sync.WaitGroup espera a varias goroutines"],
    c:"package main\n\nimport \"fmt\"\n\nfunc trabajar(id int, ch chan string) {\n  ch <- fmt.Sprintf(\"trabajador %d listo\", id)\n}\n\nfunc main() {\n  ch := make(chan string)\n  for i := 1; i <= 3; i++ {\n    go trabajar(i, ch)\n  }\n  for i := 0; i < 3; i++ {\n    fmt.Println(<-ch)\n  }\n}",
    r:"Lanza 5 goroutines en lugar de 3 y observa que el orden puede variar." },
  { m:"Experto", t:"Módulos, pruebas y herramientas", x:"go mod gestiona dependencias, go test ejecuta pruebas y gofmt unifica el estilo.",
    p:["go mod init crea un módulo", "Las pruebas están en archivos *_test.go", "go build genera el binario"],
    c:"// go mod init ejemplo.com/app\n// go test ./...\n// go build\n\npackage main\n\nimport \"fmt\"\n\nfunc suma(a, b int) int { return a + b }\n\nfunc main() {\n  fmt.Println(suma(2, 3))\n}",
    r:"Escribe suma_test.go con una prueba para suma(2, 3)." },
];
