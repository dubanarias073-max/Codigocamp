"""C · Etapa 3: Punteros y memoria dinámica."""
from ..generador import K

LISTA = [
K("Punteros",
  d="variables que guardan la dirección de memoria de otro valor",
  u="acceder y modificar datos de forma indirecta",
  mas="Un puntero se declara con un asterisco: int *p. En lugar de un número, guarda la dirección donde vive otro dato. Son la base de la memoria dinámica y de las estructuras de datos.",
  k=["Un puntero guarda una dirección de memoria.", "Se declara con un asterisco.", "Los punteros permiten acceder a los datos de forma indirecta."],
  sit="Necesitas que una función modifique directamente una variable de quien la llama. ¿Qué necesitas?",
  cod="""#include <stdio.h>

int main(void) {
    int x = 10;
    int *p = &x;          // p guarda la dirección de x
    printf("%d\\n", *p);  // 10: valor al que apunta
    return 0;
}""",
  h="guarda la dirección de una variable en un puntero",
  pr=("Un puntero guarda una ___ de memoria. (dirección)", "direccion", "dirección"),
  ec="usar un puntero sin inicializarlo"),
K("Operador &",
  d="operador que obtiene la dirección de memoria de una variable",
  u="conseguir el puntero a una variable",
  mas="&x devuelve la dirección donde está x. Se usa para llenar punteros y para pasar variables a funciones como scanf, que escriben en ellas.",
  k=["& obtiene la dirección de una variable.", "El resultado de & es un puntero.", "scanf necesita la dirección de la variable."],
  sit="Quieres obtener la dirección de memoria de una variable para guardarla en un puntero. ¿Qué operador usas?",
  cod="""#include <stdio.h>

int main(void) {
    int edad = 30;
    int *p = &edad;               // & da la dirección
    printf("%d\\n", p == &edad);  // 1: misma dirección
    return 0;
}""",
  h="comprueba que un puntero guarda la dirección de una variable",
  pr=("El operador que da la dirección de una variable es ___. (&)", "&"),
  ec="olvidar & al pasar una variable a scanf"),
K("Desreferenciar con *",
  d="usar el asterisco para acceder al valor al que apunta un puntero",
  u="leer o cambiar el dato apuntado",
  mas="*p significa «el valor en la dirección p». Se puede leer y también asignar: *p = 5 cambia la variable original.",
  k=["*p accede al valor al que apunta p.", "*p = valor modifica la variable original.", "Desreferenciar un puntero nulo es un error."],
  sit="Tienes un puntero y quieres cambiar el valor de la variable a la que apunta. ¿Qué haces?",
  cod="""#include <stdio.h>

int main(void) {
    int x = 1;
    int *p = &x;
    *p = 99;              // cambia x a través del puntero
    printf("%d\\n", x);
    return 0;
}""",
  h="cambia una variable a través de un puntero",
  pr=("Para acceder al valor apuntado se usa el operador ___. (*)", "*"),
  ec="desreferenciar un puntero sin inicializar",
  err=("""#include <stdio.h>

int main(void) {
    int *p;
    *p = 5;
    return 0;
}""", 5, "p no apunta a ninguna parte: escribir en *p es un comportamiento indefinido.")),
K("Punteros y arrays",
  d="relación por la cual el nombre de un array actúa como puntero a su primer elemento",
  u="recorrer y pasar arrays de forma eficiente",
  mas="El nombre de un array equivale a la dirección de su primer elemento. Por eso a[i] y *(a + i) son lo mismo.",
  k=["El nombre de un array es la dirección de su primer elemento.", "a[i] equivale a *(a + i).", "Al pasar un array a una función se pasa un puntero."],
  sit="Una función debe recibir un array y recorrerlo. ¿Qué se le pasa realmente?",
  cod="""#include <stdio.h>

int main(void) {
    int a[3] = {10, 20, 30};
    int *p = a;                      // a es la dirección del primer elemento
    printf("%d %d\\n", p[1], *(a + 2));
    return 0;
}""",
  h="accede a elementos de un array usando un puntero",
  pr=("a[i] equivale a *(a + ___). (i)", "i"),
  ec="creer que sizeof de un array pasado a una función devuelve su tamaño"),
K("Aritmética de punteros",
  d="operaciones de suma y resta sobre direcciones, medidas en elementos",
  u="moverse por un array con un puntero",
  mas="Si p apunta a un int, p + 1 apunta al siguiente int (avanza sizeof(int) bytes). Así se recorre un array sin usar índices.",
  k=["p + 1 apunta al siguiente elemento.", "La suma avanza según el tamaño del tipo.", "Permite recorrer un array con un puntero."],
  sit="Quieres moverte por un array avanzando un puntero elemento a elemento. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int a[3] = {1, 2, 3};
    int *p = a;
    for (int i = 0; i < 3; i++) {
        printf("%d ", *p);
        p++;                 // pasa al siguiente int
    }
    printf("\\n");
    return 0;
}""",
  h="recorre un array avanzando un puntero",
  pr=("Al hacer p++ en un int*, el puntero avanza al siguiente ___. (elemento)", "elemento"),
  ec="avanzar un puntero más allá del final del array"),
K("Paso por referencia",
  d="enviar a una función la dirección de una variable para que la modifique",
  u="permitir que una función cambie variables del que la llama",
  mas="C pasa los valores por copia. Para que una función modifique el original se le pasa un puntero. Dentro se usa * para escribir en la variable original.",
  k=["Por defecto C pasa los valores por copia.", "Un puntero permite que la función modifique el original.", "Se pasa la dirección con &."],
  sit="Quieres escribir una función que intercambie los valores de dos variables. ¿Cómo la diseñas?",
  cod="""#include <stdio.h>

void duplicar(int *n) {
    *n = *n * 2;          // modifica el original
}

int main(void) {
    int x = 4;
    duplicar(&x);         // pasa la dirección
    printf("%d\\n", x);
    return 0;
}""",
  h="duplica una variable desde una función usando un puntero",
  pr=("Para que una función modifique el original se le pasa un ___. (puntero)", "puntero"),
  ec="esperar que una función modifique el original cuando se pasó por valor"),
K("NULL",
  d="valor especial de puntero que no apunta a ninguna parte",
  u="indicar que un puntero está vacío o que algo falló",
  mas="Conviene inicializar los punteros sin dirección a NULL y comprobarlo antes de usarlos. Funciones como malloc devuelven NULL cuando fallan.",
  k=["NULL es un puntero que no apunta a nada.", "Conviene comprobar si un puntero es NULL antes de usarlo.", "malloc devuelve NULL si falla."],
  sit="Un puntero todavía no tiene un dato asignado y quieres marcarlo como vacío. ¿Qué valor le das?",
  cod="""#include <stdio.h>

int main(void) {
    int *p = NULL;               // no apunta a nada
    if (p == NULL) printf("p está vacío\\n");
    return 0;
}""",
  h="comprueba que un puntero está vacío",
  pr=("El valor de un puntero vacío es ___. (4 letras)", "null"),
  ec="desreferenciar un puntero NULL"),
K("malloc",
  d="función que reserva memoria dinámica en el montón",
  u="pedir memoria en tiempo de ejecución",
  mas="malloc(bytes) devuelve un puntero a la memoria reservada, o NULL si no hay. La memoria no se inicializa. Se suele pedir con n * sizeof(tipo).",
  k=["malloc reserva memoria dinámica.", "Devuelve NULL si no puede reservar.", "La memoria reservada no está inicializada."],
  sit="No sabes cuántos elementos necesitarás hasta ejecutar el programa. ¿Qué usas para pedir memoria?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));   // pide memoria para un int
    if (p == NULL) return 1;
    *p = 42;
    printf("%d\\n", *p);
    free(p);
    return 0;
}""",
  h="reserva memoria para un entero, lo usa y la libera",
  pr=("La función que reserva memoria dinámica es ___. (6 letras)", "malloc"),
  ec="no comprobar si malloc devolvió NULL"),
K("free",
  d="función que libera memoria reservada dinámicamente",
  u="devolver al sistema la memoria que ya no usas",
  mas="Cada malloc debe tener su free. Tras liberar, el puntero queda apuntando a memoria inválida: conviene ponerlo a NULL. Liberar dos veces es un error.",
  k=["free libera memoria reservada con malloc.", "Cada malloc necesita su free.", "Liberar dos veces la misma memoria es un error."],
  sit="Ya no necesitas un bloque de memoria que reservaste. ¿Qué haces con él?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *p = malloc(sizeof(int));
    *p = 7;
    free(p);        // libera la memoria
    p = NULL;       // evita usar un puntero colgante
    printf("liberada\\n");
    return 0;
}""",
  h="libera la memoria y deja el puntero en NULL",
  pr=("La función que libera memoria dinámica es ___. (4 letras)", "free"),
  ec="usar un puntero después de liberarlo"),
K("calloc",
  d="función que reserva memoria dinámica y la inicializa a cero",
  u="reservar arrays que empiezan con valores en cero",
  mas="calloc(n, tamaño) reserva n elementos y pone todos los bytes a cero. Es más seguro que malloc cuando necesitas valores iniciales conocidos.",
  k=["calloc reserva memoria inicializada a cero.", "Recibe el número de elementos y el tamaño de cada uno.", "También devuelve NULL si falla."],
  sit="Necesitas un array dinámico cuyos valores empiecen todos en cero. ¿Qué usas?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *a = calloc(3, sizeof(int));   // 3 enteros en cero
    printf("%d %d %d\\n", a[0], a[1], a[2]);
    free(a);
    return 0;
}""",
  h="reserva tres enteros inicializados a cero",
  pr=("La función que reserva memoria inicializada a cero es ___. (6 letras)", "calloc"),
  ec="creer que malloc inicializa la memoria a cero"),
K("realloc",
  d="función que cambia el tamaño de un bloque de memoria ya reservado",
  u="hacer crecer o encoger un array dinámico",
  mas="realloc(p, nuevo_tamaño) devuelve un puntero al bloque redimensionado, que puede estar en otra dirección. Se guarda en una variable temporal por si devuelve NULL.",
  k=["realloc cambia el tamaño de un bloque reservado.", "Puede devolver una dirección distinta.", "Conviene guardar el resultado en una variable temporal."],
  sit="Tu array dinámico se llenó y necesitas más espacio sin perder los datos. ¿Qué usas?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *a = malloc(2 * sizeof(int));
    a[0] = 1; a[1] = 2;
    int *b = realloc(a, 4 * sizeof(int));   // ahora cabe el doble
    if (b == NULL) { free(a); return 1; }
    b[2] = 3; b[3] = 4;
    printf("%d %d\\n", b[1], b[3]);
    free(b);
    return 0;
}""",
  h="amplía un array dinámico de 2 a 4 enteros",
  pr=("La función que redimensiona un bloque es ___. (7 letras)", "realloc"),
  ec="perder el bloque original si realloc falla"),
K("Fuga de memoria",
  d="memoria reservada que nunca se libera",
  u="entender por qué los programas largos consumen cada vez más memoria",
  mas="Ocurre cuando pierdes el puntero a un bloque sin llamar a free. Un programa de corta vida lo oculta, pero uno que corre días puede agotar la memoria.",
  k=["Una fuga es memoria reservada y no liberada.", "Ocurre al perder el puntero sin hacer free.", "Afecta sobre todo a programas que corren mucho tiempo."],
  sit="Tu programa consume cada vez más memoria mientras funciona. ¿Qué problema probable tienes?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    for (int i = 0; i < 3; i++) {
        int *p = malloc(100);   // reservamos
        free(p);                // y liberamos siempre: sin fuga
    }
    printf("sin fugas\\n");
    return 0;
}""",
  h="reserva y libera memoria en cada vuelta para evitar fugas",
  pr=("Memoria reservada que no se libera es una ___ de memoria. (fuga)", "fuga"),
  ec="reasignar el puntero sin liberar antes el bloque anterior"),
K("Arrays dinámicos",
  d="arrays cuyo tamaño se decide al ejecutar el programa",
  u="guardar una cantidad de datos desconocida de antemano",
  mas="Se piden con malloc(n * sizeof(tipo)) y se usan igual que un array normal. Al terminar se liberan con free.",
  k=["Un array dinámico se reserva con malloc.", "Se usa igual que un array normal.", "Debe liberarse con free."],
  sit="El usuario elegirá cuántos números guardar y no lo sabes al compilar. ¿Qué usas?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n = 4;
    int *a = malloc(n * sizeof(int));   // tamaño decidido al ejecutar
    for (int i = 0; i < n; i++) a[i] = i * i;
    printf("%d\\n", a[3]);
    free(a);
    return 0;
}""",
  h="crea un array dinámico de cuatro cuadrados",
  pr=("Un array dinámico se reserva con ___. (malloc)", "malloc"),
  ec="reservar n bytes en lugar de n * sizeof(tipo)"),
K("Puntero a puntero",
  d="puntero que guarda la dirección de otro puntero",
  u="modificar un puntero desde una función o manejar arrays de cadenas",
  mas="Se declara con dos asteriscos: int **pp. Permite que una función cambie hacia dónde apunta un puntero del que la llama.",
  k=["Un puntero a puntero se declara con dos asteriscos.", "Guarda la dirección de otro puntero.", "Permite a una función cambiar a dónde apunta un puntero."],
  sit="Quieres que una función reserve memoria y deje el puntero del que llama apuntando a ella. ¿Qué necesitas?",
  cod="""#include <stdio.h>

int main(void) {
    int x = 8;
    int *p = &x;
    int **pp = &p;           // dirección de un puntero
    printf("%d\\n", **pp);   // 8
    return 0;
}""",
  h="accede a una variable a través de un puntero a puntero",
  pr=("Un puntero a puntero se declara con ___ asteriscos. (2)", "2", "dos"),
  ec="confundir cuántos niveles de * hay que desreferenciar"),
K("const con punteros",
  d="uso de const para proteger el dato apuntado o el puntero",
  u="evitar modificaciones accidentales",
  mas="const int *p impide modificar el valor apuntado. int * const p impide cambiar a dónde apunta p. Es habitual en parámetros para indicar que la función no modificará el dato.",
  k=["const int *p protege el dato apuntado.", "int * const p protege la dirección guardada.", "Es habitual usarlo en parámetros de solo lectura."],
  sit="Una función solo debe leer un texto y nunca modificarlo. ¿Cómo lo declaras?",
  cod="""#include <stdio.h>

void mostrar(const char *s) {   // la función no puede modificar s
    printf("%s\\n", s);
}

int main(void) {
    mostrar("solo lectura");
    return 0;
}""",
  h="muestra un texto recibido como puntero de solo lectura",
  pr=("Un puntero a un dato de solo lectura se declara const ___ *p. (int)", "int", "char"),
  ec="intentar modificar el dato apuntado por un const"),
K("Punteros a funciones",
  d="punteros que guardan la dirección de una función",
  u="elegir qué función ejecutar en tiempo de ejecución",
  mas="Se declaran como tipo (*nombre)(parámetros). Permiten pasar funciones como argumento, lo que se llama callback.",
  k=["Un puntero a función guarda la dirección de una función.", "Permite elegir la función a ejecutar.", "Se usa para callbacks."],
  sit="Quieres pasar a otra función cuál operación debe ejecutar. ¿Qué usas?",
  cod="""#include <stdio.h>

int doble(int n) { return n * 2; }

int main(void) {
    int (*f)(int) = doble;     // puntero a función
    printf("%d\\n", f(21));
    return 0;
}""",
  h="llama a una función a través de un puntero",
  pr=("Pasar una función como argumento se llama ___. (callback)", "callback"),
  ec="olvidar los paréntesis alrededor de (*f) al declararlo"),
K("void*",
  d="puntero genérico que puede apuntar a cualquier tipo",
  u="escribir funciones que sirvan para varios tipos",
  mas="Un void* no sabe qué tipo apunta, así que antes de usarlo hay que convertirlo al tipo correcto. malloc devuelve void*.",
  k=["void* es un puntero genérico.", "Hay que convertirlo antes de desreferenciarlo.", "malloc devuelve un void*."],
  sit="Una función debe aceptar un puntero a cualquier tipo de dato. ¿Qué tipo usas?",
  cod="""#include <stdio.h>

int main(void) {
    int x = 5;
    void *p = &x;                 // apunta a cualquier cosa
    printf("%d\\n", *(int *)p);   // se convierte a int* para usarlo
    return 0;
}""",
  h="usa un puntero genérico convirtiéndolo a int*",
  pr=("El puntero genérico se escribe ___*. (void)", "void"),
  ec="desreferenciar un void* sin convertirlo"),
K("Cadenas con punteros",
  d="uso de char* para recorrer y manejar texto",
  u="manipular cadenas sin índices",
  mas="Un char* puede apuntar al primer carácter de una cadena y avanzar hasta encontrar '\\0'. Un literal como \"hola\" no debe modificarse.",
  k=["Un char* apunta al primer carácter de una cadena.", "Se avanza hasta encontrar el terminador nulo.", "Un literal de cadena no debe modificarse."],
  sit="Quieres recorrer un texto carácter por carácter usando un puntero. ¿Qué haces?",
  cod="""#include <stdio.h>

int main(void) {
    const char *s = "hola";
    int n = 0;
    while (*s != '\\0') { n++; s++; }   // avanza hasta el terminador
    printf("%d\\n", n);
    return 0;
}""",
  h="cuenta los caracteres de una cadena con un puntero",
  pr=("Una cadena termina con el carácter ___. ('\\0' nulo)", "nulo", "\\0"),
  ec="modificar un literal de cadena"),
K("Pila y montón",
  d="las dos zonas de memoria: automática (pila) y dinámica (montón)",
  u="entender dónde viven las variables",
  mas="Las variables locales viven en la pila y desaparecen al salir de la función. La memoria de malloc vive en el montón hasta que la liberas. Devolver la dirección de una local es un error.",
  k=["Las variables locales viven en la pila.", "La memoria de malloc vive en el montón.", "Devolver la dirección de una variable local es un error."],
  sit="Una función devuelve la dirección de una variable local y el programa falla después. ¿Qué ocurrió?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int local = 1;               // pila
    int *dinamico = malloc(4);   // montón
    *dinamico = 2;
    printf("%d %d\\n", local, *dinamico);
    free(dinamico);
    return 0;
}""",
  h="usa una variable de la pila y otra del montón",
  pr=("La memoria de malloc vive en el ___. (montón)", "monton", "montón", "heap"),
  ec="devolver un puntero a una variable local"),
K("Desbordamiento de búfer",
  d="escribir más datos de los que caben en un array",
  u="entender uno de los errores de seguridad más graves",
  mas="Ocurre al escribir fuera de los límites de un array. Puede corromper otras variables o permitir ataques. Se evita comprobando tamaños y usando funciones seguras como snprintf.",
  k=["Un desbordamiento escribe fuera de los límites del array.", "Puede corromper datos o permitir ataques.", "Se evita comprobando tamaños."],
  sit="Copias el nombre de un usuario en un array pequeño sin comprobar su longitud. ¿Qué riesgo corres?",
  cod="""#include <stdio.h>
#include <string.h>

int main(void) {
    char buf[8];
    snprintf(buf, sizeof(buf), "%s", "Texto largo que no cabe");   // limita a 7 + \\0
    printf("%s\\n", buf);
    return 0;
}""",
  h="copia un texto largo en un búfer pequeño sin desbordarlo",
  pr=("Escribir fuera de un array es un ___ de búfer. (desbordamiento)", "desbordamiento"),
  ec="usar funciones que no comprueban el tamaño del destino"),
]
