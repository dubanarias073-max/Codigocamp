"""C · Etapa 4: Estructuras, bits y archivos."""
from ..generador import K

LISTA = [
K("struct",
  d="tipo compuesto que agrupa varios datos bajo un solo nombre",
  u="representar entidades como una persona o un producto",
  mas="Un struct agrupa campos de tipos distintos. Primero se define su forma y luego se declaran variables de ese tipo.",
  k=["Un struct agrupa varios datos en un solo tipo.", "Cada dato de un struct se llama campo.", "Los campos pueden ser de tipos distintos."],
  sit="Quieres guardar nombre y edad de una persona como una sola unidad. ¿Qué usas?",
  cod="""#include <stdio.h>

struct Persona {
    char nombre[20];
    int edad;
};

int main(void) {
    struct Persona p = {"Ana", 20};
    printf("%s %d\\n", p.nombre, p.edad);
    return 0;
}""",
  h="define una persona con nombre y edad y la muestra",
  pr=("La palabra para agrupar datos en un tipo propio es ___. (6 letras)", "struct"),
  ec="olvidar la palabra struct al declarar la variable"),
K("Acceso a campos",
  d="uso del punto para leer o cambiar un campo de un struct",
  u="trabajar con cada dato de una estructura",
  mas="Con variable.campo se lee o se asigna. Las cadenas dentro de un struct se copian con strcpy, no con =.",
  k=["El punto accede a un campo de un struct.", "Se puede leer y modificar un campo.", "Las cadenas se copian con strcpy."],
  sit="Quieres cambiar solo la edad de una persona ya creada. ¿Qué escribes?",
  cod="""#include <stdio.h>

struct Punto { int x; int y; };

int main(void) {
    struct Punto p = {1, 2};
    p.x = 10;                    // cambia un campo
    printf("%d %d\\n", p.x, p.y);
    return 0;
}""",
  h="modifica un campo de un punto",
  pr=("Se accede a un campo de un struct con un ___. (punto)", "punto", "."),
  ec="copiar una cadena de un struct con ="),
K("Puntero a struct",
  d="puntero que apunta a una estructura y accede a sus campos con ->",
  u="pasar estructuras a funciones sin copiarlas",
  mas="Con un puntero a struct se usa la flecha: p->campo, equivalente a (*p).campo. Evita copiar estructuras grandes al llamar a una función.",
  k=["-> accede a un campo a través de un puntero.", "p->campo equivale a (*p).campo.", "Evita copiar estructuras grandes."],
  sit="Una función debe modificar una estructura del que la llama sin copiarla. ¿Qué recibe?",
  cod="""#include <stdio.h>

struct Punto { int x; int y; };

void mover(struct Punto *p) {
    p->x += 5;                    // flecha: acceso por puntero
}

int main(void) {
    struct Punto a = {1, 1};
    mover(&a);
    printf("%d\\n", a.x);
    return 0;
}""",
  h="mueve un punto a través de un puntero",
  pr=("Para acceder a un campo mediante un puntero se usa la flecha ___. (->)", "->"),
  ec="usar el punto en lugar de -> con un puntero",
  err=("""#include <stdio.h>

struct P { int x; };

void f(struct P *p) {
    p.x = 1;
}""", 6, "Con un puntero se usa p->x, no p.x.")),
K("typedef",
  d="palabra que crea un nombre nuevo para un tipo",
  u="escribir menos al usar estructuras y tipos largos",
  mas="typedef struct { ... } Nombre; permite declarar variables sin escribir struct cada vez. También sirve para dar nombres claros a tipos básicos.",
  k=["typedef crea un alias para un tipo.", "Evita escribir struct en cada declaración.", "Mejora la legibilidad del código."],
  sit="Estás cansado de escribir struct Persona cada vez que declaras una variable. ¿Qué usas?",
  cod="""#include <stdio.h>

typedef struct {
    char letra;
    int valor;
} Carta;                      // ahora basta escribir Carta

int main(void) {
    Carta c = {'A', 11};
    printf("%c %d\\n", c.letra, c.valor);
    return 0;
}""",
  h="define un tipo Carta con typedef y lo usa",
  pr=("La palabra que crea un alias de tipo es ___. (7 letras)", "typedef"),
  ec="creer que typedef crea un tipo nuevo distinto"),
K("Array de structs",
  d="array donde cada elemento es una estructura",
  u="manejar listas de registros como alumnos o productos",
  mas="Se declara como struct Alumno lista[3] y se accede con lista[i].campo. Se recorre con un bucle for.",
  k=["Un array de structs guarda muchos registros.", "Se accede con lista[i].campo.", "Se recorre con un bucle."],
  sit="Necesitas guardar nombre y nota de tres alumnos. ¿Qué usas?",
  cod="""#include <stdio.h>

typedef struct { char nombre[10]; int nota; } Alumno;

int main(void) {
    Alumno lista[2] = {{"Ana", 9}, {"Luis", 7}};
    for (int i = 0; i < 2; i++) printf("%s %d\\n", lista[i].nombre, lista[i].nota);
    return 0;
}""",
  h="muestra los alumnos de un array de estructuras",
  pr=("Un elemento de un array de structs se accede con lista[i].___. (campo)", "campo"),
  ec="olvidar el índice y escribir lista.campo"),
K("Structs anidados",
  d="estructuras que contienen otras estructuras como campos",
  u="modelar datos con partes que a su vez tienen partes",
  mas="Un campo puede ser de tipo struct. Se accede encadenando puntos: a.b.c. Es útil para agrupar datos relacionados como dirección dentro de persona.",
  k=["Un struct puede contener otro struct.", "Se accede encadenando puntos.", "Agrupa datos relacionados."],
  sit="Cada persona tiene una dirección con calle y número y quieres agruparlo todo. ¿Qué usas?",
  cod="""#include <stdio.h>

typedef struct { int x, y; } Punto;
typedef struct { Punto origen; int radio; } Circulo;

int main(void) {
    Circulo c = {{1, 2}, 5};
    printf("%d\\n", c.origen.y);   // puntos encadenados
    return 0;
}""",
  h="accede a un campo de un struct dentro de otro",
  pr=("En structs anidados los campos se encadenan con ___. (puntos)", "puntos", "punto"),
  ec="olvidar el nombre del campo intermedio"),
K("union",
  d="tipo cuyos campos comparten la misma zona de memoria",
  u="ahorrar memoria cuando solo se usa un campo a la vez",
  mas="Una union ocupa lo que su campo más grande. Solo uno de sus campos es válido a la vez: escribir en uno pisa a los demás.",
  k=["Una union comparte memoria entre sus campos.", "Solo un campo es válido a la vez.", "Ocupa el tamaño de su campo más grande."],
  sit="Un dato puede ser entero o decimal, nunca los dos a la vez, y quieres ahorrar memoria. ¿Qué usas?",
  cod="""#include <stdio.h>

union Dato { int i; float f; };

int main(void) {
    union Dato d;
    d.i = 7;                     // solo este campo es válido ahora
    printf("%d\\n", d.i);
    return 0;
}""",
  h="guarda un entero en una union",
  pr=("El tipo cuyos campos comparten memoria es ___. (5 letras)", "union"),
  ec="leer un campo distinto del último que se escribió"),
K("enum",
  d="tipo con un conjunto de constantes enteras con nombre",
  u="dar nombres legibles a opciones o estados",
  mas="Los valores empiezan en 0 y aumentan de uno en uno, salvo que indiques otros. Hace el código más claro que usar números sueltos.",
  k=["enum define constantes con nombre.", "Los valores empiezan en 0 por defecto.", "Mejora la claridad frente a números sueltos."],
  sit="Tu programa usa los estados 0, 1 y 2 y nadie recuerda qué significan. ¿Qué usas?",
  cod="""#include <stdio.h>

enum Estado { PENDIENTE, ACTIVO, CERRADO };   // 0, 1, 2

int main(void) {
    enum Estado e = ACTIVO;
    printf("%d\\n", e);
    return 0;
}""",
  h="usa un estado nombrado en lugar de un número",
  pr=("El tipo de constantes con nombre es ___. (4 letras)", "enum"),
  ec="asumir que el primer valor de un enum es 1"),
K("Operadores de bits",
  d="operadores &, | y ^ que actúan sobre cada bit de un número",
  u="manejar banderas y datos a bajo nivel",
  mas="& deja 1 solo si ambos bits son 1, | si alguno es 1 y ^ si son distintos. Se usan para activar, apagar y comprobar bits individuales.",
  k=["& combina bit a bit con «y».", "| combina bit a bit con «o».", "^ da 1 cuando los bits son distintos."],
  sit="Quieres comprobar si un bit concreto de una bandera está encendido. ¿Qué operador usas?",
  cod="""#include <stdio.h>

int main(void) {
    int a = 6, b = 3;            // 110 y 011 en binario
    printf("%d %d %d\\n", a & b, a | b, a ^ b);
    return 0;
}""",
  h="aplica y, o, xor bit a bit a dos números",
  pr=("El operador «y» bit a bit es ___. (&)", "&"),
  ec="confundir & con &&"),
K("Desplazamientos",
  d="operadores << y >> que mueven los bits a izquierda o derecha",
  u="multiplicar o dividir por potencias de dos y armar máscaras",
  mas="x << n desplaza n posiciones a la izquierda (multiplica por 2^n) y x >> n a la derecha (divide). Se usan para crear máscaras como 1 << 3.",
  k=["<< desplaza los bits a la izquierda.", ">> desplaza los bits a la derecha.", "x << n equivale a multiplicar por 2 elevado a n."],
  sit="Quieres multiplicar un entero por 8 de forma rápida con bits. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int x = 3;
    printf("%d\\n", x << 3);   // 3 * 8 = 24
    printf("%d\\n", 16 >> 2);  // 16 / 4 = 4
    return 0;
}""",
  h="desplaza bits para multiplicar y dividir",
  pr=("Desplazar a la izquierda se escribe con ___. (<<)", "<<"),
  ec="confundir << con el operador de comparación"),
K("fopen y fclose",
  d="funciones para abrir y cerrar archivos",
  u="leer y guardar datos en disco",
  mas="fopen(nombre, modo) devuelve un FILE* o NULL si falla. Los modos principales son \"r\" (leer), \"w\" (escribir) y \"a\" (añadir). Al terminar se cierra con fclose.",
  k=["fopen abre un archivo.", "fclose lo cierra.", "fopen devuelve NULL si falla."],
  sit="Debes guardar datos en un archivo y asegurarte de cerrarlo al terminar. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    FILE *f = fopen("datos.txt", "w");   // "w": escribir
    if (f == NULL) return 1;
    fputs("hola\\n", f);
    fclose(f);                           // siempre se cierra
    printf("archivo creado\\n");
    return 0;
}""",
  h="crea un archivo, escribe en él y lo cierra",
  pr=("La función que abre un archivo es ___. (5 letras)", "fopen"),
  ec="no comprobar si fopen devolvió NULL"),
K("fprintf",
  d="función que escribe texto con formato en un archivo",
  u="guardar datos con formato en un archivo",
  mas="Funciona como printf pero con un primer argumento extra: el archivo donde escribir.",
  k=["fprintf escribe texto con formato en un archivo.", "Su primer argumento es el archivo.", "Funciona como printf."],
  sit="Quieres guardar «Ana 9» en un archivo con formato. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    FILE *f = fopen("notas.txt", "w");
    fprintf(f, "%s %d\\n", "Ana", 9);   // como printf pero al archivo
    fclose(f);
    printf("guardado\\n");
    return 0;
}""",
  h="guarda un nombre y una nota en un archivo",
  pr=("La versión de printf que escribe en un archivo es ___. (7 letras)", "fprintf"),
  ec="olvidar el archivo como primer argumento de fprintf"),
K("fgets",
  d="función que lee una línea de texto de un archivo",
  u="leer texto línea a línea de forma segura",
  mas="fgets(buffer, tamaño, archivo) lee como máximo tamaño-1 caracteres. Devuelve NULL al llegar al final. Es la alternativa segura a gets, que ya no existe.",
  k=["fgets lee una línea de texto.", "Limita la lectura al tamaño del búfer.", "Devuelve NULL al final del archivo."],
  sit="Quieres leer un archivo línea a línea sin riesgo de desbordar el búfer. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    FILE *f = fopen("lineas.txt", "w");
    fputs("uno\\ndos\\n", f);
    fclose(f);
    f = fopen("lineas.txt", "r");
    char linea[20];
    while (fgets(linea, sizeof(linea), f)) printf("%s", linea);
    fclose(f);
    return 0;
}""",
  h="escribe dos líneas en un archivo y las lee con fgets",
  pr=("La función segura para leer una línea es ___. (5 letras)", "fgets"),
  ec="usar gets, que no limita el tamaño"),
K("fscanf",
  d="función que lee datos con formato desde un archivo",
  u="leer números y palabras sueltas de un archivo",
  mas="Funciona como scanf pero sobre un archivo. Devuelve cuántos datos leyó, o EOF al terminar.",
  k=["fscanf lee datos con formato de un archivo.", "Devuelve el número de datos leídos.", "Funciona como scanf."],
  sit="Tienes un archivo con números separados por espacios y quieres leerlos. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    FILE *f = fopen("n.txt", "w");
    fprintf(f, "10 20");
    fclose(f);
    f = fopen("n.txt", "r");
    int a, b;
    fscanf(f, "%d %d", &a, &b);   // lee dos enteros
    fclose(f);
    printf("%d\\n", a + b);
    return 0;
}""",
  h="lee dos números de un archivo y los suma",
  pr=("La versión de scanf para archivos es ___. (6 letras)", "fscanf"),
  ec="olvidar & en las variables de fscanf"),
K("fwrite y fread",
  d="funciones para escribir y leer bloques de bytes",
  u="guardar estructuras completas en formato binario",
  mas="fwrite(dato, tamaño, cantidad, archivo) guarda bytes tal cual. fread hace lo contrario. El archivo se abre en modo binario (\"wb\" o \"rb\").",
  k=["fwrite escribe bloques de bytes.", "fread lee bloques de bytes.", "Se usan con modos binarios wb y rb."],
  sit="Quieres guardar una estructura completa en un archivo de una sola vez. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int n = 42, leido = 0;
    FILE *f = fopen("bin.dat", "wb");
    fwrite(&n, sizeof(int), 1, f);     // guarda 4 bytes
    fclose(f);
    f = fopen("bin.dat", "rb");
    fread(&leido, sizeof(int), 1, f);  // los recupera
    fclose(f);
    printf("%d\\n", leido);
    return 0;
}""",
  h="guarda un entero en binario y lo vuelve a leer",
  pr=("La función que escribe bloques binarios es ___. (6 letras)", "fwrite"),
  ec="abrir en modo texto un archivo binario"),
K("argc y argv",
  d="parámetros de main que reciben los argumentos de la línea de comandos",
  u="recibir datos al ejecutar el programa",
  mas="argc es la cantidad de argumentos y argv un array de cadenas. argv[0] es el nombre del programa. Se declara como int main(int argc, char *argv[]).",
  k=["argc es el número de argumentos.", "argv es un array de cadenas.", "argv[0] es el nombre del programa."],
  sit="Quieres que el usuario escriba una opción al ejecutar el programa. ¿Qué usas en main?",
  cod="""#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("argumentos: %d\\n", argc);    // al menos 1: el programa
    if (argc > 1) printf("primero: %s\\n", argv[1]);
    return 0;
}""",
  h="muestra cuántos argumentos recibió el programa",
  pr=("El número de argumentos de main se llama ___. (argc)", "argc"),
  ec="usar argv[1] sin comprobar que existe"),
K("snprintf",
  d="función que escribe texto con formato en una cadena con límite de tamaño",
  u="construir textos de forma segura",
  mas="snprintf(destino, tamaño, formato, ...) escribe sin superar el tamaño dado, así evita desbordamientos. Es la alternativa segura a sprintf.",
  k=["snprintf escribe texto con formato en una cadena.", "Limita la escritura al tamaño indicado.", "Es más segura que sprintf."],
  sit="Quieres construir un mensaje en una cadena sin riesgo de desbordarla. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    char msg[30];
    snprintf(msg, sizeof(msg), "Hola %s, tienes %d", "Ana", 20);
    printf("%s\\n", msg);
    return 0;
}""",
  h="construye un mensaje en una cadena de forma segura",
  pr=("La versión segura para escribir en una cadena es ___. (8 letras)", "snprintf"),
  ec="usar sprintf sin controlar el tamaño"),
K("sscanf",
  d="función que lee datos con formato desde una cadena",
  u="extraer números o palabras de un texto",
  mas="Funciona como scanf pero la entrada es una cadena en memoria. Devuelve cuántos valores pudo leer.",
  k=["sscanf lee datos con formato de una cadena.", "Devuelve cuántos valores leyó.", "Sirve para extraer números de un texto."],
  sit="Tienes el texto «12 34» y quieres sacar los dos números. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int a, b;
    sscanf("12 34", "%d %d", &a, &b);   // lee desde una cadena
    printf("%d\\n", a * b);
    return 0;
}""",
  h="extrae dos números de un texto y los multiplica",
  pr=("La función que lee datos desde una cadena es ___. (6 letras)", "sscanf"),
  ec="no comprobar el valor que devuelve sscanf"),
K("rand y srand",
  d="funciones para generar números pseudoaleatorios",
  u="simular azar en juegos y pruebas",
  mas="rand() devuelve un número pseudoaleatorio. Si no se cambia la semilla con srand, cada ejecución da la misma secuencia. Se suele usar srand(time(NULL)).",
  k=["rand genera números pseudoaleatorios.", "srand cambia la semilla.", "Sin cambiar la semilla la secuencia se repite."],
  sit="Necesitas simular una tirada de dado. ¿Qué funciones usas?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    srand(7);                       // semilla fija: resultado repetible
    int dado = rand() % 6 + 1;      // entre 1 y 6
    printf("%s\\n", (dado >= 1 && dado <= 6) ? "válido" : "fuera de rango");
    return 0;
}""",
  h="simula un dado y comprueba que está entre 1 y 6",
  pr=("La función que genera un número pseudoaleatorio es ___. (4 letras)", "rand"),
  ec="olvidar cambiar la semilla y obtener siempre lo mismo"),
K("qsort",
  d="función que ordena un array con una función de comparación",
  u="ordenar datos de cualquier tipo",
  mas="qsort(array, n, tamaño, comparar) ordena en el lugar. La función de comparación devuelve negativo, cero o positivo según el orden.",
  k=["qsort ordena un array.", "Recibe una función de comparación.", "La comparación devuelve un valor negativo, cero o positivo."],
  sit="Quieres ordenar un array de enteros sin escribir tu propio algoritmo. ¿Qué usas?",
  cod="""#include <stdio.h>
#include <stdlib.h>

int comparar(const void *a, const void *b) {
    return *(const int *)a - *(const int *)b;   // menor a mayor
}

int main(void) {
    int v[4] = {3, 1, 4, 2};
    qsort(v, 4, sizeof(int), comparar);
    for (int i = 0; i < 4; i++) printf("%d ", v[i]);
    printf("\\n");
    return 0;
}""",
  h="ordena un array de enteros de menor a mayor",
  pr=("La función estándar para ordenar arrays es ___. (5 letras)", "qsort"),
  ec="devolver un valor incorrecto en la función de comparación"),
]
