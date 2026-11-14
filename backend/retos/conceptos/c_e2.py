"""C · Etapa 2: Repetición, funciones, arrays y cadenas."""
from ..generador import K

LISTA = [
K("Bucle while",
  d="bucle que repite un bloque mientras una condición sea verdadera",
  u="repetir cuando no sabes cuántas veces",
  mas="while evalúa la condición antes de cada vuelta. Si la condición es falsa desde el inicio, el bloque no se ejecuta nunca. Cuida que algo dentro cambie la condición.",
  k=["while repite mientras la condición sea verdadera.", "La condición se evalúa antes de cada vuelta.", "Si la condición nunca cambia, el bucle no termina."],
  sit="Debes seguir pidiendo algo hasta que ocurra un evento, sin saber cuántas veces. ¿Qué bucle usas?",
  cod="""#include <stdio.h>

int main(void) {
    int n = 3;
    while (n > 0) {          // mientras n sea mayor que 0
        printf("n = %d\\n", n);
        n--;                 // cambia la condición
    }
    return 0;
}""",
  h="cuenta hacia atrás de 3 a 1",
  pr=("El bucle que repite mientras una condición sea verdadera es ___. (5 letras)", "while"),
  ec="olvidar modificar la variable de la condición y crear un bucle infinito"),
K("Bucle do while",
  d="bucle que ejecuta el bloque al menos una vez y luego comprueba la condición",
  u="repetir algo que debe hacerse siempre una primera vez",
  mas="La condición se evalúa al final, por eso el cuerpo se ejecuta como mínimo una vez. Termina con punto y coma después del while.",
  k=["do while ejecuta el bloque al menos una vez.", "La condición se evalúa al final.", "do while termina con punto y coma."],
  sit="Un menú debe mostrarse siempre una vez y repetirse solo si el usuario lo pide. ¿Qué bucle usas?",
  cod="""#include <stdio.h>

int main(void) {
    int i = 10;
    do {
        printf("i = %d\\n", i);   // se ejecuta aunque i ya sea grande
        i++;
    } while (i < 5);            // punto y coma obligatorio
    return 0;
}""",
  h="muestra i una vez aunque la condición sea falsa",
  pr=("El bucle que se ejecuta al menos una vez es do ___. (5 letras)", "while"),
  ec="olvidar el punto y coma después del while"),
K("Bucle for",
  d="bucle que repite con inicio, condición y paso en una sola línea",
  u="repetir un número conocido de veces",
  mas="for (inicio; condición; paso) agrupa lo necesario para controlar el contador. Es el bucle más usado para recorrer rangos y arrays.",
  k=["for tiene inicio, condición y paso.", "for se usa cuando se conoce el número de repeticiones.", "El contador suele declararse dentro del for."],
  sit="Quieres mostrar los números del 1 al 5. ¿Qué bucle usas?",
  cod="""#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 5; i++) {   // inicio; condición; paso
        printf("%d ", i);
    }
    printf("\\n");
    return 0;
}""",
  h="muestra los números del 1 al 5",
  pr=("El bucle con inicio, condición y paso es ___. (3 letras)", "for"),
  ec="usar <= cuando se quería < y recorrer una vuelta de más"),
K("break",
  d="instrucción que sale inmediatamente del bucle",
  u="detener un bucle cuando ya encontraste lo que buscabas",
  mas="break termina el bucle más interno en el que está. También se usa para cerrar los casos de un switch.",
  k=["break sale del bucle inmediatamente.", "break afecta al bucle más interno.", "break también cierra los casos de un switch."],
  sit="Buscas un valor en una lista y quieres dejar de recorrer en cuanto lo encuentres. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 10; i++) {
        if (i == 4) break;   // sale del bucle
        printf("%d ", i);
    }
    printf("\\n");
    return 0;
}""",
  h="muestra números hasta llegar a 4 y sale",
  pr=("La instrucción que sale de un bucle es ___. (5 letras)", "break"),
  ec="creer que break solo sale de la vuelta actual"),
K("continue",
  d="instrucción que salta a la siguiente vuelta del bucle",
  u="omitir ciertas vueltas sin terminar el bucle",
  mas="continue ignora el resto del cuerpo en esa vuelta y pasa a la siguiente. En un for, antes ejecuta el paso del contador.",
  k=["continue salta a la siguiente vuelta.", "continue no termina el bucle.", "Ignora lo que queda del cuerpo en esa vuelta."],
  sit="Quieres mostrar del 1 al 5 pero sin el número 3. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 5; i++) {
        if (i == 3) continue;   // salta solo esta vuelta
        printf("%d ", i);
    }
    printf("\\n");
    return 0;
}""",
  h="muestra del 1 al 5 sin el 3",
  pr=("La instrucción que salta a la siguiente vuelta es ___. (8 letras)", "continue"),
  ec="confundir continue con break"),
K("Funciones",
  d="bloque de código con nombre que realiza una tarea y puede reutilizarse",
  u="no repetir código y organizar el programa",
  mas="Una función tiene tipo de retorno, nombre, parámetros y cuerpo. Se llama escribiendo su nombre con paréntesis. Dividir un programa en funciones lo hace más fácil de leer.",
  k=["Una función agrupa código reutilizable.", "Una función se llama por su nombre.", "Las funciones organizan el programa."],
  sit="Repites el mismo cálculo en cinco lugares del programa. ¿Qué haces?",
  cod="""#include <stdio.h>

void saludar(void) {          // función sin parámetros ni retorno
    printf("Hola desde una función\\n");
}

int main(void) {
    saludar();                // llamada
    saludar();
    return 0;
}""",
  h="llama dos veces a una función que saluda",
  pr=("Una función se ejecuta escribiendo su nombre y ___. (paréntesis)", "parentesis", "paréntesis"),
  ec="definir una función pero no llamarla"),
K("Parámetros",
  d="valores que una función recibe para trabajar",
  u="hacer funciones que sirvan con distintos datos",
  mas="Cada parámetro se declara con su tipo entre los paréntesis. Al llamar, se pasan los argumentos en el mismo orden. En C los valores se copian a la función.",
  k=["Los parámetros se declaran con su tipo.", "Los argumentos se pasan en el mismo orden.", "En C los valores se pasan por copia."],
  sit="Quieres que una función salude al nombre que le indiques. ¿Qué necesita?",
  cod="""#include <stdio.h>

void saludar(const char *nombre, int veces) {   // dos parámetros
    for (int i = 0; i < veces; i++) printf("Hola %s\\n", nombre);
}

int main(void) {
    saludar("Ana", 2);
    return 0;
}""",
  h="saluda a Ana dos veces usando parámetros",
  pr=("Los valores que recibe una función se llaman ___. (parámetros)", "parametros", "parámetros", "argumentos"),
  ec="pasar los argumentos en distinto orden que los parámetros"),
K("return",
  d="instrucción que devuelve un valor y termina la función",
  u="obtener un resultado de una función",
  mas="El valor devuelto debe coincidir con el tipo de retorno de la función. Al ejecutar return, la función termina en ese punto.",
  k=["return devuelve un valor desde una función.", "return termina la función.", "El valor debe coincidir con el tipo de retorno."],
  sit="Una función calcula la suma y quieres usar el resultado en otro lugar. ¿Qué usas?",
  cod="""#include <stdio.h>

int sumar(int a, int b) {
    return a + b;               // devuelve el resultado
}

int main(void) {
    int total = sumar(2, 3);    // guarda el valor devuelto
    printf("%d\\n", total);
    return 0;
}""",
  h="suma dos números con una función que devuelve el resultado",
  pr=("La instrucción que devuelve un valor es ___. (6 letras)", "return"),
  ec="escribir código después de un return esperando que se ejecute",
  err=("""#include <stdio.h>

int doble(int n) {
    return n * 2;
    printf("nunca se muestra");
}""", 5, "Después de return la función termina: esa línea nunca se ejecuta.")),
K("void",
  d="tipo que indica ausencia de valor",
  u="declarar funciones que no devuelven nada",
  mas="Una función void no devuelve resultado. También se escribe en la lista de parámetros, f(void), para indicar que no recibe ninguno.",
  k=["void indica que no se devuelve un valor.", "Una función void no usa return con valor.", "f(void) indica que no tiene parámetros."],
  sit="Tu función solo imprime un mensaje y no tiene nada que devolver. ¿Qué tipo declaras?",
  cod="""#include <stdio.h>

void aviso(void) {     // no recibe ni devuelve nada
    printf("Aviso\\n");
}

int main(void) {
    aviso();
    return 0;
}""",
  h="llama a una función que no devuelve nada",
  pr=("El tipo de una función que no devuelve nada es ___. (4 letras)", "void"),
  ec="usar el resultado de una función void"),
K("Prototipos",
  d="declaración de una función antes de su definición",
  u="usar una función antes de escribir su cuerpo",
  mas="Un prototipo indica tipo de retorno, nombre y parámetros terminando en punto y coma. Permite llamar a la función aunque su definición esté más abajo.",
  k=["Un prototipo declara una función sin su cuerpo.", "Termina en punto y coma.", "Permite llamar a la función antes de definirla."],
  sit="Quieres escribir main arriba y las funciones debajo, sin que el compilador proteste. ¿Qué agregas?",
  cod="""#include <stdio.h>

int triple(int n);          // prototipo

int main(void) {
    printf("%d\\n", triple(4));
    return 0;
}

int triple(int n) {         // definición
    return n * 3;
}""",
  h="declara una función con prototipo y la define después",
  pr=("La declaración de una función sin cuerpo es un ___. (prototipo)", "prototipo"),
  ec="llamar a una función antes de declararla"),
K("Ámbito de variables",
  d="zona del programa donde una variable es visible",
  u="evitar conflictos entre variables con el mismo nombre",
  mas="Una variable local solo existe dentro de las llaves donde se declara. Una global se declara fuera de las funciones y la ven todas, pero conviene evitarlas.",
  k=["Una variable local solo existe en su bloque.", "Una variable global es visible en todo el archivo.", "Conviene evitar variables globales."],
  sit="Dos funciones usan una variable llamada i y no quieres que se pisen. ¿Qué aprovechas?",
  cod="""#include <stdio.h>

int global = 100;           // visible en todo el archivo

int main(void) {
    int local = 5;          // solo existe dentro de main
    printf("%d %d\\n", global, local);
    return 0;
}""",
  h="muestra una variable global y una local",
  pr=("Una variable declarada dentro de una función es ___. (local)", "local"),
  ec="usar una variable local fuera del bloque donde se declaró"),
K("Recursión",
  d="técnica en la que una función se llama a sí misma",
  u="resolver problemas que se repiten en versión más pequeña",
  mas="Una función recursiva necesita un caso base que detenga las llamadas y un caso recursivo que se acerque a él. Sin caso base, el programa agota la memoria de pila.",
  k=["En la recursión una función se llama a sí misma.", "Necesita un caso base para detenerse.", "Sin caso base se desborda la pila."],
  sit="Quieres calcular el factorial de un número definiéndolo en función del factorial del anterior. ¿Qué técnica usas?",
  cod="""#include <stdio.h>

int factorial(int n) {
    if (n <= 1) return 1;          // caso base
    return n * factorial(n - 1);   // caso recursivo
}

int main(void) {
    printf("%d\\n", factorial(5));
    return 0;
}""",
  h="calcula el factorial de 5 con recursión",
  pr=("Toda función recursiva necesita un caso ___. (4 letras)", "base"),
  ec="olvidar el caso base"),
K("Arrays",
  d="conjunto de elementos del mismo tipo guardados en posiciones consecutivas",
  u="manejar muchos valores con un solo nombre",
  mas="Se declara con el tipo, el nombre y el tamaño: int notas[5]. Los índices empiezan en 0. C no comprueba que el índice esté dentro del rango.",
  k=["Un array guarda varios valores del mismo tipo.", "El primer índice es 0.", "C no comprueba los límites del array."],
  sit="Debes guardar cinco notas bajo un solo nombre. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int notas[3] = {7, 9, 8};    // tres elementos
    printf("%d\\n", notas[0]);   // primer elemento
    notas[1] = 10;               // modificar uno
    printf("%d\\n", notas[1]);
    return 0;
}""",
  h="guarda tres notas y modifica una",
  pr=("El primer elemento de un array está en el índice ___. (0)", "0", "cero"),
  ec="acceder a un índice fuera de los límites del array"),
K("Recorrer arrays",
  d="visitar cada elemento de un array con un bucle",
  u="calcular totales, buscar y mostrar datos",
  mas="Se usa un for con un índice de 0 a n-1. Para saber cuántos elementos tiene, se divide sizeof(array) entre sizeof(array[0]).",
  k=["Se recorre un array con un bucle for.", "El índice va de 0 a n-1.", "sizeof permite calcular el número de elementos."],
  sit="Quieres sumar todas las notas guardadas en un array. ¿Qué haces?",
  cod="""#include <stdio.h>

int main(void) {
    int notas[] = {7, 9, 8};
    int n = sizeof(notas) / sizeof(notas[0]);   // 3 elementos
    int suma = 0;
    for (int i = 0; i < n; i++) suma += notas[i];
    printf("%d\\n", suma);
    return 0;
}""",
  h="suma todos los elementos de un array",
  pr=("Un array de n elementos se recorre con índices de 0 a ___. (n-1)", "n-1", "n - 1"),
  ec="recorrer hasta n en lugar de n-1",
  err=("""#include <stdio.h>

int main(void) {
    int a[3] = {1, 2, 3};
    for (int i = 0; i <= 3; i++) printf("%d ", a[i]);
    return 0;
}""", 5, "Con i <= 3 se lee a[3], que no existe: los índices llegan hasta 2.")),
K("Cadenas de texto",
  d="arrays de char que terminan con el carácter nulo",
  u="guardar y manejar texto",
  mas="Una cadena es un array de char terminado en '\\0'. Se escribe entre comillas dobles y el compilador añade el terminador. Se muestra con %s.",
  k=["Una cadena es un array de char.", "Termina con el carácter nulo.", "Se muestra con %s."],
  sit="Debes guardar un nombre completo en una variable. ¿Qué usas en C?",
  cod="""#include <stdio.h>

int main(void) {
    char nombre[] = "Ana";           // 3 letras + el terminador \\0
    printf("%s\\n", nombre);
    printf("%c\\n", nombre[0]);      // primera letra
    return 0;
}""",
  h="guarda un nombre en una cadena y muestra su primera letra",
  pr=("Una cadena de C termina con el carácter ___. (nulo)", "nulo", "\\0"),
  ec="olvidar que la cadena necesita espacio para el terminador"),
K("strlen",
  d="función que devuelve la longitud de una cadena",
  u="saber cuántos caracteres tiene un texto",
  mas="strlen cuenta los caracteres hasta el terminador nulo, sin contarlo. Está en string.h. Devuelve un size_t.",
  k=["strlen devuelve la longitud de una cadena.", "No cuenta el terminador nulo.", "Está en string.h."],
  sit="Quieres saber cuántas letras tiene un nombre. ¿Qué función usas?",
  cod="""#include <stdio.h>
#include <string.h>

int main(void) {
    char nombre[] = "Carlos";
    printf("%zu\\n", strlen(nombre));   // 6
    return 0;
}""",
  h="cuenta las letras de un nombre",
  pr=("La función que mide una cadena es ___. (6 letras)", "strlen"),
  ec="creer que strlen cuenta el terminador nulo"),
K("strcpy",
  d="función que copia una cadena en otra",
  u="duplicar el contenido de un texto",
  mas="strcpy(destino, origen) copia todos los caracteres y el terminador. El destino debe tener espacio suficiente, o habrá un desbordamiento.",
  k=["strcpy copia una cadena en otra.", "El destino debe tener espacio suficiente.", "Está en string.h."],
  sit="Necesitas copiar un texto en otra variable. ¿Qué función usas?",
  cod="""#include <stdio.h>
#include <string.h>

int main(void) {
    char copia[20];
    strcpy(copia, "Hola");   // destino, origen
    printf("%s\\n", copia);
    return 0;
}""",
  h="copia un texto en otra variable",
  pr=("La función que copia cadenas es ___. (6 letras)", "strcpy"),
  ec="copiar a un destino demasiado pequeño"),
K("strcmp",
  d="función que compara dos cadenas",
  u="saber si dos textos son iguales o cuál va antes",
  mas="strcmp devuelve 0 si las cadenas son iguales, un número negativo si la primera va antes y positivo si va después. No se comparan cadenas con ==.",
  k=["strcmp compara dos cadenas.", "Devuelve 0 si son iguales.", "No se deben comparar cadenas con ==."],
  sit="Quieres comprobar si dos textos son idénticos. ¿Qué función usas?",
  cod="""#include <stdio.h>
#include <string.h>

int main(void) {
    if (strcmp("abc", "abc") == 0) printf("iguales\\n");   // 0 = iguales
    else printf("distintas\\n");
    return 0;
}""",
  h="comprueba que dos cadenas son iguales",
  pr=("strcmp devuelve ___ si las cadenas son iguales. (0)", "0", "cero"),
  ec="comparar cadenas con =="),
K("Matrices",
  d="arrays de dos dimensiones con filas y columnas",
  u="guardar tablas de datos",
  mas="Se declaran con dos tamaños: int m[2][3]. Se accede con m[fila][columna] y se recorren con dos bucles for anidados.",
  k=["Una matriz es un array con filas y columnas.", "Se accede con dos índices.", "Se recorre con dos bucles anidados."],
  sit="Debes guardar una tabla de 2 filas y 3 columnas. ¿Qué declaras?",
  cod="""#include <stdio.h>

int main(void) {
    int m[2][3] = {{1, 2, 3}, {4, 5, 6}};   // 2 filas, 3 columnas
    printf("%d\\n", m[1][2]);               // fila 1, columna 2
    return 0;
}""",
  h="guarda una tabla de 2x3 y muestra un elemento",
  pr=("Una matriz se accede con dos ___. (índices)", "indices", "índices"),
  ec="intercambiar fila y columna al acceder"),
K("sizeof",
  d="operador que devuelve el tamaño en bytes de un tipo o variable",
  u="conocer cuánta memoria ocupa algo",
  mas="sizeof se evalúa al compilar y devuelve un size_t. Con arrays permite calcular el número de elementos dividiendo entre el tamaño de un elemento.",
  k=["sizeof devuelve el tamaño en bytes.", "Se evalúa al compilar.", "Sirve para calcular la longitud de un array."],
  sit="Quieres saber cuántos bytes ocupa un entero en tu sistema. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int n = 0;
    printf("%zu\\n", sizeof(int));   // bytes de un int
    printf("%zu\\n", sizeof(n));
    return 0;
}""",
  h="muestra cuántos bytes ocupa un int",
  pr=("El operador que da el tamaño en bytes es ___. (6 letras)", "sizeof"),
  ec="creer que sizeof de un puntero da el tamaño del array"),
]
