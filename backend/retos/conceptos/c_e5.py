"""C · Etapa 5: C profesional."""
from ..generador import K

LISTA = [
K("Archivos de cabecera",
  d="archivos .h que declaran funciones y tipos para otros archivos",
  u="dividir un programa en varios archivos",
  mas="Un .h contiene prototipos y tipos; el .c contiene la implementación. Quien necesite las funciones incluye el .h con comillas: #include \"mates.h\".",
  k=["Un archivo .h declara funciones y tipos.", "El .c contiene la implementación.", "Las cabeceras propias se incluyen con comillas."],
  sit="Tu programa creció y quieres separar las funciones de cálculo en otro archivo. ¿Qué creas?",
  cod="""#include <stdio.h>

/* mates.h:   int doble(int n);        <- declaración
   mates.c:   int doble(int n) {...}   <- implementación */
int doble(int n) { return n * 2; }

int main(void) {
    printf("%d\\n", doble(21));
    return 0;
}""",
  h="usa una función que vive en su propio módulo",
  pr=("Las declaraciones se guardan en archivos con extensión ___. (.h)", ".h", "h"),
  ec="definir funciones en un .h incluido desde varios archivos"),
K("Include guards",
  d="directivas que evitan incluir una cabecera más de una vez",
  u="prevenir errores de declaraciones duplicadas",
  mas="Se escriben con #ifndef, #define y #endif alrededor del contenido del .h. Si el archivo ya se incluyó, el compilador lo ignora.",
  k=["Los include guards evitan inclusiones duplicadas.", "Usan #ifndef, #define y #endif.", "Se colocan en las cabeceras."],
  sit="Una cabecera se incluye dos veces y el compilador protesta por redefiniciones. ¿Qué agregas?",
  cod="""#include <stdio.h>
#ifndef MATES_H      // si aún no se definió...
#define MATES_H      // ...se define y se incluye el contenido
#define VERSION 1
#endif               // fin del guarda

int main(void) {
    printf("%d\\n", VERSION);
    return 0;
}""",
  h="protege una definición con include guards",
  pr=("El guarda empieza con #___ y un nombre. (ifndef)", "ifndef"),
  ec="usar el mismo nombre de guarda en dos cabeceras"),
K("Makefile",
  d="archivo que automatiza la compilación del proyecto",
  u="compilar solo lo que cambió con un único comando",
  mas="Un Makefile describe objetivos, dependencias y comandos. make compara fechas y recompila solo los archivos modificados.",
  k=["Un Makefile automatiza la compilación.", "make recompila solo lo que cambió.", "Describe objetivos, dependencias y comandos."],
  sit="Tu proyecto tiene muchos archivos y compilar a mano es lento y propenso a errores. ¿Qué usas?",
  cod="""#include <stdio.h>

/* Makefile:
   programa: main.c util.c
   <tab>gcc -Wall main.c util.c -o programa */
int main(void) {
    printf("compilado con make\\n");
    return 0;
}""",
  h="muestra un mensaje; el comentario describe un Makefile",
  pr=("La herramienta que lee un Makefile es ___. (4 letras)", "make"),
  ec="usar espacios en lugar de tabulador en los comandos del Makefile"),
K("static",
  d="modificador que fija la duración o el alcance de una variable o función",
  u="conservar valores entre llamadas o ocultar funciones al resto de archivos",
  mas="Una variable local static conserva su valor entre llamadas. Una función o variable global static solo es visible dentro de su archivo.",
  k=["Una variable local static conserva su valor entre llamadas.", "Una función static solo es visible en su archivo.", "static se inicializa una sola vez."],
  sit="Una función debe recordar cuántas veces fue llamada. ¿Qué modificador usas?",
  cod="""#include <stdio.h>

int contar(void) {
    static int n = 0;     // se inicializa una sola vez
    return ++n;
}

int main(void) {
    contar(); contar();
    printf("%d\\n", contar());
    return 0;
}""",
  h="cuenta las llamadas con una variable static",
  pr=("El modificador que conserva el valor entre llamadas es ___. (6 letras)", "static"),
  ec="esperar que una variable local normal conserve su valor"),
K("extern",
  d="palabra que declara una variable definida en otro archivo",
  u="compartir una variable global entre archivos",
  mas="extern int n; avisa de que n existe en otro lugar. La definición real, con memoria, está en un solo archivo.",
  k=["extern declara una variable definida en otro archivo.", "No reserva memoria.", "La definición debe estar en un solo archivo."],
  sit="Dos archivos necesitan compartir el mismo contador global. ¿Qué usas en el segundo?",
  cod="""#include <stdio.h>

int total = 5;           // definición (un solo archivo)
extern int total;        // declaración: otro archivo escribiría solo esto

int main(void) {
    printf("%d\\n", total);
    return 0;
}""",
  h="declara y usa una variable global",
  pr=("La palabra que declara una variable definida en otro archivo es ___. (6 letras)", "extern"),
  ec="definir la misma variable global en dos archivos"),
K("Macros con argumentos",
  d="macros #define que reciben parámetros",
  u="escribir pequeñas operaciones sin llamar a una función",
  mas="El preprocesador sustituye el texto. Conviene poner paréntesis alrededor de cada parámetro y de toda la expresión para evitar sorpresas con la precedencia.",
  k=["Una macro con argumentos se sustituye como texto.", "Conviene proteger cada parámetro con paréntesis.", "No comprueba tipos."],
  sit="Quieres una operación cortísima como calcular el cuadrado sin crear una función. ¿Qué usas?",
  cod="""#include <stdio.h>
#define CUADRADO(x) ((x) * (x))   // paréntesis para evitar errores

int main(void) {
    printf("%d\\n", CUADRADO(2 + 3));   // 25
    return 0;
}""",
  h="calcula un cuadrado con una macro",
  pr=("Una macro con parámetros se define con #___. (define)", "define"),
  ec="olvidar los paréntesis dentro de la macro"),
K("Compilación condicional",
  d="directivas que incluyen o excluyen código según una condición",
  u="adaptar el programa a distintas plataformas o modos",
  mas="#ifdef incluye un bloque solo si existe una macro. Se usa para activar mensajes de depuración con -DDEBUG.",
  k=["#ifdef incluye código si una macro existe.", "#endif cierra el bloque condicional.", "Sirve para activar o quitar depuración."],
  sit="Quieres mensajes de depuración solo mientras desarrollas. ¿Qué usas?",
  cod="""#include <stdio.h>
#define DEBUG 1

int main(void) {
#ifdef DEBUG
    printf("modo depuración\\n");   // solo se compila si DEBUG existe
#endif
    printf("fin\\n");
    return 0;
}""",
  h="muestra un mensaje solo si DEBUG está definido",
  pr=("La directiva que incluye código si una macro existe es #___. (ifdef)", "ifdef"),
  ec="olvidar el #endif"),
K("assert",
  d="macro que comprueba una condición y detiene el programa si es falsa",
  u="detectar errores de lógica durante el desarrollo",
  mas="assert(condición) está en assert.h. Si la condición es falsa, muestra dónde falló y aborta. Con -DNDEBUG se desactiva.",
  k=["assert detiene el programa si la condición es falsa.", "Está en assert.h.", "Se desactiva con NDEBUG."],
  sit="Quieres asegurarte durante el desarrollo de que un divisor nunca sea cero. ¿Qué usas?",
  cod="""#include <stdio.h>
#include <assert.h>

int dividir(int a, int b) {
    assert(b != 0);        // si falla, el programa se detiene
    return a / b;
}

int main(void) {
    printf("%d\\n", dividir(10, 2));
    return 0;
}""",
  h="comprueba que el divisor no sea cero antes de dividir",
  pr=("La macro que comprueba condiciones es ___. (6 letras)", "assert"),
  ec="usar assert para validar entradas del usuario"),
K("errno y perror",
  d="mecanismo que informa del motivo de un fallo del sistema",
  u="mostrar mensajes claros cuando una función falla",
  mas="Cuando una función del sistema falla, guarda un código en errno. perror muestra un mensaje legible basado en él.",
  k=["errno guarda el código del último error.", "perror muestra un mensaje descriptivo.", "Se usan cuando una función devuelve un fallo."],
  sit="fopen devolvió NULL y quieres explicar por qué falló. ¿Qué usas?",
  cod="""#include <stdio.h>
#include <errno.h>

int main(void) {
    FILE *f = fopen("no_existe.txt", "r");
    if (f == NULL) printf("error %d\\n", errno);   // ENOENT = 2
    return 0;
}""",
  h="muestra el código de error al abrir un archivo inexistente",
  pr=("La variable que guarda el código de error es ___. (errno)", "errno"),
  ec="ignorar el valor de retorno de funciones que pueden fallar"),
K("Advertencias del compilador",
  d="avisos de gcc sobre posibles errores con opciones como -Wall",
  u="detectar problemas antes de ejecutar",
  mas="Compila siempre con -Wall -Wextra. Una advertencia no impide compilar, pero suele señalar un error real, como una variable sin usar o un formato incorrecto.",
  k=["-Wall activa las advertencias principales.", "Una advertencia suele señalar un error real.", "Conviene tratar las advertencias como errores."],
  sit="Tu programa compila pero se comporta raro y gcc no dijo nada. ¿Qué te faltó?",
  cod="""#include <stdio.h>

int main(void) {
    int n = 5;
    printf("%d\\n", n);   // gcc -Wall -Wextra avisaría de errores de formato
    return 0;
}""",
  h="muestra un valor con un formato correcto",
  pr=("La opción que activa las advertencias principales es -W___. (all)", "all"),
  ec="ignorar las advertencias del compilador"),
K("Depuración con gdb",
  d="uso de un depurador para ejecutar el programa paso a paso",
  u="encontrar la causa de un fallo",
  mas="gdb permite poner puntos de parada, avanzar línea a línea e inspeccionar variables. Compila con -g para incluir la información necesaria.",
  k=["gdb ejecuta el programa paso a paso.", "Permite inspeccionar variables.", "Hay que compilar con -g."],
  sit="Tu programa se cae con «segmentation fault» y no sabes dónde. ¿Qué herramienta usas?",
  cod="""#include <stdio.h>

int main(void) {
    int suma = 0;
    for (int i = 1; i <= 3; i++) suma += i;   // gdb: break main, next, print suma
    printf("%d\\n", suma);
    return 0;
}""",
  h="suma del 1 al 3, ideal para depurar paso a paso",
  pr=("El depurador de GNU se llama ___. (3 letras)", "gdb"),
  ec="depurar sin compilar con -g"),
K("Valgrind",
  d="herramienta que detecta fugas y errores de memoria",
  u="encontrar accesos inválidos y memoria sin liberar",
  mas="Ejecutas tu programa con valgrind ./programa y te informa de lecturas fuera de rango, usos de memoria liberada y bloques no liberados.",
  k=["Valgrind detecta fugas de memoria.", "Detecta accesos inválidos a memoria.", "Se ejecuta con valgrind ./programa."],
  sit="Sospechas que tu programa tiene una fuga de memoria. ¿Qué herramienta usas?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));
    *p = 1;
    printf("%d\\n", *p);
    free(p);            // valgrind confirmaría que no hay fugas
    return 0;
}""",
  h="reserva y libera memoria, sin fugas",
  pr=("La herramienta que detecta fugas de memoria es ___. (8 letras)", "valgrind"),
  ec="creer que un programa sin fallos visibles no tiene fugas"),
K("Tipos de ancho fijo",
  d="tipos de stdint.h con tamaño exacto como int32_t",
  u="escribir código con tamaños predecibles en cualquier plataforma",
  mas="int puede tener distinto tamaño según el sistema. Con int32_t, uint8_t o int64_t el tamaño es siempre el mismo.",
  k=["Los tipos de ancho fijo tienen un tamaño exacto.", "Están en stdint.h.", "Dan portabilidad entre plataformas."],
  sit="Necesitas un entero de exactamente 32 bits en cualquier computadora. ¿Qué usas?",
  cod="""#include <stdio.h>
#include <stdint.h>

int main(void) {
    int32_t a = 100000;
    uint8_t b = 200;           // 0 a 255
    printf("%d %d\\n", (int)a, (int)b);
    return 0;
}""",
  h="usa enteros de tamaño exacto",
  pr=("La cabecera con enteros de ancho fijo es ___.h. (stdint)", "stdint"),
  ec="suponer que int siempre tiene 32 bits"),
K("size_t",
  d="tipo entero sin signo para tamaños y conteos",
  u="representar tamaños de memoria y longitudes",
  mas="sizeof y strlen devuelven size_t. Se imprime con %zu. Al ser sin signo, restar de más puede dar un número enorme.",
  k=["size_t guarda tamaños y conteos.", "No tiene signo.", "Se imprime con %zu."],
  sit="Quieres guardar el resultado de strlen en una variable del tipo adecuado. ¿Cuál usas?",
  cod="""#include <stdio.h>
#include <string.h>

int main(void) {
    size_t n = strlen("hola");
    printf("%zu\\n", n);
    return 0;
}""",
  h="guarda la longitud de una cadena en un size_t",
  pr=("El tipo de los tamaños es ___. (size_t)", "size_t"),
  ec="restar de un size_t y obtener un número negativo"),
K("Biblioteca math.h",
  d="cabecera con funciones matemáticas como sqrt y pow",
  u="hacer cálculos matemáticos",
  mas="Incluye sqrt (raíz), pow (potencia), sin, cos, fabs y más. En muchos sistemas hay que enlazar con -lm al compilar.",
  k=["math.h ofrece funciones matemáticas.", "sqrt calcula la raíz cuadrada.", "Puede requerir enlazar con -lm."],
  sit="Necesitas calcular la raíz cuadrada y una potencia. ¿Qué cabecera incluyes?",
  cod="""#include <stdio.h>
#include <math.h>

int main(void) {
    printf("%.0f\\n", sqrt(81.0));    // 9
    printf("%.0f\\n", pow(2.0, 10.0)); // 1024
    return 0;
}""",
  h="calcula una raíz cuadrada y una potencia",
  pr=("La cabecera de funciones matemáticas es ___.h. (math)", "math"),
  ec="olvidar enlazar con -lm"),
K("Biblioteca ctype.h",
  d="cabecera con funciones para clasificar y convertir caracteres",
  u="validar letras, dígitos y pasar a mayúsculas",
  mas="isalpha, isdigit y isspace clasifican; toupper y tolower convierten. Trabajan carácter a carácter.",
  k=["ctype.h clasifica caracteres.", "toupper pasa un carácter a mayúscula.", "isdigit comprueba si es un dígito."],
  sit="Quieres comprobar si un carácter es un dígito. ¿Qué cabecera usas?",
  cod="""#include <stdio.h>
#include <ctype.h>

int main(void) {
    printf("%d\\n", isdigit('7') != 0);    // 1
    printf("%c\\n", toupper('a'));         // A
    return 0;
}""",
  h="comprueba un dígito y pasa una letra a mayúscula",
  pr=("La función que pasa un carácter a mayúscula es ___. (toupper)", "toupper"),
  ec="aplicar toupper a una cadena entera sin recorrerla"),
K("Listas enlazadas",
  d="estructura de nodos conectados mediante punteros",
  u="guardar datos que crecen y cambian con facilidad",
  mas="Cada nodo guarda un dato y un puntero al siguiente. Insertar al inicio es rápido; para llegar a un elemento hay que recorrer desde la cabeza.",
  k=["Una lista enlazada se compone de nodos con punteros.", "Cada nodo apunta al siguiente.", "Se accede recorriendo desde la cabeza."],
  sit="Necesitas insertar elementos con frecuencia sin redimensionar un array. ¿Qué estructura usas?",
  cod="""#include <stdio.h>
#include <stdlib.h>

typedef struct Nodo { int dato; struct Nodo *sig; } Nodo;

int main(void) {
    Nodo *b = malloc(sizeof(Nodo)); b->dato = 2; b->sig = NULL;
    Nodo *a = malloc(sizeof(Nodo)); a->dato = 1; a->sig = b;
    for (Nodo *p = a; p; p = p->sig) printf("%d ", p->dato);
    printf("\\n");
    free(a); free(b);
    return 0;
}""",
  h="crea una lista de dos nodos y la recorre",
  pr=("En una lista enlazada cada nodo apunta al ___. (siguiente)", "siguiente", "sig"),
  ec="perder la cabeza de la lista"),
K("Pilas y colas",
  d="estructuras con orden fijo: la pila saca el último, la cola el primero",
  u="modelar deshacer, turnos y recorridos",
  mas="Una pila es LIFO: el último en entrar es el primero en salir. Una cola es FIFO: el primero en entrar es el primero en salir.",
  k=["Una pila es LIFO.", "Una cola es FIFO.", "Ambas controlan el orden de salida."],
  sit="Quieres implementar el botón deshacer, donde se revierte lo último hecho. ¿Qué estructura usas?",
  cod="""#include <stdio.h>

int main(void) {
    int pila[3], tope = 0;
    pila[tope++] = 1;          // apilar
    pila[tope++] = 2;
    pila[tope++] = 3;
    printf("%d\\n", pila[--tope]);   // desapilar: sale el último (3)
    return 0;
}""",
  h="apila tres valores y desapila el último",
  pr=("La pila sigue el orden LIFO: el último en ___ es el primero en salir. (entrar)", "entrar"),
  ec="confundir pila (LIFO) con cola (FIFO)"),
K("Búsqueda binaria",
  d="algoritmo que busca en una lista ordenada dividiéndola por la mitad",
  u="encontrar un valor rápidamente en datos ordenados",
  mas="Compara con el elemento central y descarta la mitad que no puede contenerlo. Necesita que la lista esté ordenada y es mucho más rápida que recorrer todo.",
  k=["La búsqueda binaria requiere una lista ordenada.", "Descarta la mitad en cada paso.", "Es mucho más rápida que la búsqueda lineal."],
  sit="Tienes un millón de números ordenados y buscas uno con pocas comparaciones. ¿Qué algoritmo usas?",
  cod="""#include <stdio.h>

int buscar(int v[], int n, int x) {
    int ini = 0, fin = n - 1;
    while (ini <= fin) {
        int mid = (ini + fin) / 2;
        if (v[mid] == x) return mid;
        if (v[mid] < x) ini = mid + 1; else fin = mid - 1;
    }
    return -1;
}

int main(void) {
    int v[] = {1, 3, 5, 7, 9};
    printf("%d\\n", buscar(v, 5, 7));
    return 0;
}""",
  h="busca un número en un array ordenado y muestra su posición",
  pr=("La búsqueda binaria exige que la lista esté ___. (ordenada)", "ordenada", "ordenado"),
  ec="aplicar búsqueda binaria a una lista desordenada"),
K("Ordenamiento burbuja",
  d="algoritmo que ordena intercambiando elementos vecinos fuera de orden",
  u="aprender cómo funciona un ordenamiento simple",
  mas="Recorre la lista varias veces comparando pares contiguos. En cada pasada el mayor «sube» al final. Es fácil de entender pero lento con muchos datos.",
  k=["El ordenamiento burbuja compara elementos vecinos.", "Intercambia los que están fuera de orden.", "Es lento con muchos datos."],
  sit="Quieres entender un algoritmo de ordenamiento sencillo para practicar bucles. ¿Cuál eliges?",
  cod="""#include <stdio.h>

int main(void) {
    int v[4] = {4, 2, 3, 1};
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3 - i; j++)
            if (v[j] > v[j + 1]) { int t = v[j]; v[j] = v[j + 1]; v[j + 1] = t; }
    for (int i = 0; i < 4; i++) printf("%d ", v[i]);
    printf("\\n");
    return 0;
}""",
  h="ordena un array pequeño con el método de la burbuja",
  pr=("El algoritmo que intercambia vecinos fuera de orden es el de la ___. (burbuja)", "burbuja"),
  ec="usar burbuja con millones de datos"),
]
