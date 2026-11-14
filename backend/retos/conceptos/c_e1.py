"""C · Etapa 1: Primeros pasos."""
from ..generador import K

LISTA = [
K("Qué es C",
  d="lenguaje de programación compilado, rápido y cercano al hardware",
  u="escribir sistemas operativos, controladores y programas muy eficientes",
  mas="C nació en 1972 y es la base de muchos lenguajes modernos. Te da control directo de la memoria, a cambio de mayor responsabilidad.",
  k=["C es un lenguaje compilado.", "C permite controlar la memoria directamente.", "Muchos sistemas operativos están escritos en C."],
  sit="Necesitas programar un componente muy rápido que hable casi directo con el hardware. ¿Qué lenguaje eliges?",
  cod="""#include <stdio.h>

int main(void) {
    printf("Hola desde C\\n");   // un programa mínimo en C
    return 0;
}""",
  h="muestra un saludo desde un programa en C",
  pr=("C es un lenguaje ___ antes de ejecutarse. (compilado)", "compilado"),
  ec="creer que C se ejecuta línea a línea sin compilar"),
K("Compilar con gcc",
  d="paso que traduce el código C a un programa ejecutable",
  u="convertir tu código fuente en algo que la máquina entiende",
  mas="gcc lee tus archivos .c y genera un ejecutable. Con gcc hola.c -o hola creas el programa hola. Si hay errores de sintaxis, no lo genera.",
  k=["gcc compila código C a un ejecutable.", "La opción -o elige el nombre del ejecutable.", "Los errores de sintaxis impiden compilar."],
  sit="Escribiste un archivo hola.c y necesitas convertirlo en un programa que se pueda ejecutar. ¿Qué haces?",
  cod="""#include <stdio.h>

int main(void) {
    printf("Compilado con gcc\\n");   // gcc hola.c -o hola
    return 0;
}""",
  h="muestra un mensaje de un programa compilado con gcc",
  pr=("El compilador más usado para C se llama ___. (3 letras)", "gcc"),
  ec="intentar ejecutar el archivo .c sin compilarlo antes"),
K("Función main",
  d="función donde empieza la ejecución de todo programa C",
  u="indicar por dónde arranca el programa",
  mas="Todo programa C tiene una función main. Devuelve un int: 0 significa que terminó bien y otro valor indica un error.",
  k=["main es el punto de entrada del programa.", "main devuelve un int al terminar.", "Devolver 0 indica que todo salió bien."],
  sit="Tu programa compila pero el enlazador dice que no encuentra por dónde empezar. ¿Qué falta?",
  cod="""#include <stdio.h>

int main(void) {   // aquí empieza todo
    printf("Dentro de main\\n");
    return 0;      // 0 = sin errores
}""",
  h="ejecuta el código dentro de main y devuelve 0",
  pr=("La función donde empieza un programa C es ___. (4 letras)", "main"),
  ec="olvidar la función main",
  err=("""#include <stdio.h>

int principal(void) {
    printf("Hola\\n");
    return 0;
}""", 3, "La función de entrada debe llamarse main.")),
K("#include",
  d="directiva que incorpora un archivo de cabecera al programa",
  u="usar funciones de las bibliotecas estándar",
  mas="#include <stdio.h> trae las declaraciones de printf y scanf. Las cabeceras estándar van entre ángulos y las propias entre comillas.",
  k=["#include incorpora una cabecera al programa.", "stdio.h declara printf y scanf.", "Las cabeceras propias se incluyen con comillas."],
  sit="Quieres usar printf pero el compilador no la reconoce. ¿Qué te falta?",
  cod="""#include <stdio.h>    // funciones de entrada y salida
#include <math.h>     // funciones matemáticas

int main(void) {
    printf("%.1f\\n", sqrt(16.0));
    return 0;
}""",
  h="incluye dos cabeceras y calcula una raíz cuadrada",
  pr=("La directiva para usar una biblioteca empieza con #___. (7 letras)", "include"),
  ec="usar printf sin incluir stdio.h"),
K("printf",
  d="función que escribe texto formateado en la pantalla",
  u="mostrar mensajes y valores al usuario",
  mas="printf escribe el texto que recibe. El carácter especial \\n produce un salto de línea. Sin él, todo sale seguido.",
  k=["printf escribe texto en la pantalla.", "\\n produce un salto de línea.", "printf viene de stdio.h."],
  sit="Debes mostrar un mensaje al usuario y pasar a la línea siguiente. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    printf("Línea 1\\n");   // \\n salta de línea
    printf("Línea 2\\n");
    return 0;
}""",
  h="muestra dos líneas de texto",
  pr=("La función que escribe en pantalla es ___. (6 letras)", "printf"),
  ec="olvidar \\n y que todo el texto salga en una sola línea"),
K("Formatos de printf",
  d="marcadores como %d, %f, %c y %s que insertan valores en el texto",
  u="mostrar variables dentro de un mensaje",
  mas="%d es para enteros, %f para decimales, %c para un carácter y %s para cadenas. Cada marcador se reemplaza por el valor que le sigue.",
  k=["%d muestra un entero.", "%f muestra un decimal.", "%s muestra una cadena de texto."],
  sit="Quieres mostrar «Ana tiene 20 años» usando variables dentro del mensaje. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int edad = 20;
    printf("Ana tiene %d años\\n", edad);   // %d recibe edad
    printf("Altura: %.2f\\n", 1.65);        // %.2f: dos decimales
    return 0;
}""",
  h="inserta una edad y una altura dentro de mensajes",
  pr=("El marcador para un entero en printf es %___. (d)", "d"),
  ec="usar %d para mostrar un decimal",
  err=("""#include <stdio.h>

int main(void) {
    int n = 5;
    printf("n = %s\\n", n);
    return 0;
}""", 5, "%s es para cadenas; un entero se muestra con %d.")),
K("Comentarios",
  d="texto que el compilador ignora",
  u="explicar el código a quien lo lea",
  mas="// comenta hasta el final de la línea y /* ... */ comenta varias líneas. Un buen comentario explica el porqué, no lo obvio.",
  k=["Los comentarios son ignorados por el compilador.", "// comenta una línea.", "/* */ permite comentar varias líneas."],
  sit="Quieres dejar una nota para otro programador que no afecte al programa. ¿Qué escribes?",
  cod="""#include <stdio.h>

int main(void) {
    // comentario de una línea
    /* comentario
       de varias líneas */
    printf("Los comentarios no se ejecutan\\n");
    return 0;
}""",
  h="muestra un mensaje; los comentarios se ignoran",
  pr=("El comentario de una línea empieza con ___. (//)", "//"),
  ec="olvidar cerrar un comentario /* */"),
K("Variables",
  d="espacio con nombre que guarda un valor en memoria",
  u="almacenar datos que el programa va a usar",
  mas="En C debes declarar el tipo de cada variable antes de usarla: tipo nombre = valor;. El tipo decide cuánta memoria ocupa y qué valores admite.",
  k=["Una variable guarda un valor con nombre.", "En C hay que declarar el tipo de la variable.", "El tipo decide qué valores admite."],
  sit="Necesitas guardar la edad de un usuario para usarla después. ¿Qué declaras?",
  cod="""#include <stdio.h>

int main(void) {
    int edad = 20;      // tipo nombre = valor
    edad = edad + 1;    // la variable puede cambiar
    printf("%d\\n", edad);
    return 0;
}""",
  h="guarda una edad y la aumenta en uno",
  pr=("Antes de usar una variable en C hay que declarar su ___. (4 letras)", "tipo"),
  ec="usar una variable sin declararla antes",
  err=("""#include <stdio.h>

int main(void) {
    total = 5;
    printf("%d\\n", total);
    return 0;
}""", 4, "total no se declaró: falta indicar su tipo (int total).")),
K("int",
  d="tipo para guardar números enteros",
  u="contar y calcular con valores sin decimales",
  mas="Un int suele ocupar 4 bytes. Guarda enteros positivos y negativos. La división entre dos int descarta los decimales.",
  k=["int guarda números enteros.", "La división entre int descarta los decimales.", "Un int suele ocupar 4 bytes."],
  sit="Debes guardar la cantidad de alumnos de una clase. ¿Qué tipo usas?",
  cod="""#include <stdio.h>

int main(void) {
    int alumnos = 25;
    printf("%d\\n", alumnos / 2);   // 12: se pierden los decimales
    return 0;
}""",
  h="divide un entero entre 2 y pierde los decimales",
  pr=("El tipo para números enteros es ___. (3 letras)", "int"),
  ec="esperar decimales al dividir dos enteros"),
K("float y double",
  d="tipos para guardar números con decimales",
  u="trabajar con medidas y cálculos no enteros",
  mas="float tiene menos precisión y ocupa menos; double tiene más precisión y es el más usado. Los literales decimales como 3.14 son double por defecto.",
  k=["float y double guardan números decimales.", "double tiene más precisión que float.", "3.14 es un double por defecto."],
  sit="Necesitas guardar la altura de una persona con decimales y buena precisión. ¿Qué tipo usas?",
  cod="""#include <stdio.h>

int main(void) {
    double altura = 1.75;
    float peso = 70.5f;
    printf("%.2f %.1f\\n", altura, peso);
    return 0;
}""",
  h="guarda una altura y un peso decimales",
  pr=("El tipo decimal de mayor precisión es ___. (6 letras)", "double"),
  ec="usar int para guardar valores con decimales"),
K("char",
  d="tipo que guarda un solo carácter",
  u="trabajar con letras y símbolos sueltos",
  mas="Un char ocupa 1 byte y se escribe entre comillas simples, como 'A'. Internamente guarda un número: el código ASCII de la letra.",
  k=["char guarda un solo carácter.", "Un char se escribe entre comillas simples.", "Internamente un char es un número (código ASCII)."],
  sit="Quieres guardar la inicial de un nombre, solo una letra. ¿Qué tipo usas?",
  cod="""#include <stdio.h>

int main(void) {
    char inicial = 'A';
    printf("%c vale %d\\n", inicial, inicial);   // letra y su código ASCII
    return 0;
}""",
  h="muestra una letra y su código ASCII",
  pr=("Un solo carácter se guarda en una variable de tipo ___. (4 letras)", "char"),
  ec="usar comillas dobles para un char"),
K("const",
  d="palabra que impide cambiar el valor de una variable",
  u="proteger valores que no deben modificarse",
  mas="Una variable const debe inicializarse al declararla. Si intentas cambiarla después, el compilador da error.",
  k=["const impide modificar una variable.", "Una variable const se inicializa al declararla.", "Cambiarla produce un error de compilación."],
  sit="El valor de pi no debe cambiar jamás durante el programa. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    const double PI = 3.14159;   // no se puede modificar
    printf("%.2f\\n", PI * 2);
    return 0;
}""",
  h="usa una constante PI para un cálculo",
  pr=("La palabra que crea una variable inmodificable es ___. (5 letras)", "const"),
  ec="intentar asignar un nuevo valor a una constante",
  err=("""#include <stdio.h>

int main(void) {
    const int n = 1;
    n = 2;
    return 0;
}""", 5, "n es const y no se puede reasignar.")),
K("#define",
  d="directiva que define una constante o macro simple",
  u="dar nombre a valores que se repiten",
  mas="El preprocesador sustituye el nombre por su valor antes de compilar. No lleva punto y coma ni signo igual. Por convención se escribe en mayúsculas.",
  k=["#define sustituye un nombre por un valor antes de compilar.", "#define no lleva punto y coma.", "Por convención se escribe en mayúsculas."],
  sit="Un valor aparece en veinte lugares y quieres cambiarlo en uno solo. ¿Qué usas?",
  cod="""#include <stdio.h>
#define MAX 10   // sin signo igual ni punto y coma

int main(void) {
    printf("%d\\n", MAX * 2);
    return 0;
}""",
  h="usa una constante MAX definida con #define",
  pr=("La directiva para definir una constante es #___. (6 letras)", "define"),
  ec="poner punto y coma al final de un #define"),
K("Operadores aritméticos",
  d="símbolos + - * / que realizan cálculos",
  u="hacer operaciones matemáticas",
  mas="Suman, restan, multiplican y dividen. La multiplicación y la división se evalúan antes que la suma y la resta; los paréntesis cambian el orden.",
  k=["+, -, * y / son operadores aritméticos.", "* y / se evalúan antes que + y -.", "Los paréntesis cambian el orden de evaluación."],
  sit="Debes calcular el total de 3 productos a 5 euros más 2 de envío. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int total = 3 * 5 + 2;   // primero 3*5, luego +2
    printf("%d\\n", total);
    printf("%d\\n", 3 * (5 + 2));
    return 0;
}""",
  h="calcula un total con multiplicación y suma",
  pr=("El operador que multiplica es ___. (un signo)", "*"),
  ec="olvidar que * se evalúa antes que +"),
K("Resto %",
  d="operador que devuelve el resto de una división entera",
  u="saber si un número es par o múltiplo de otro",
  mas="7 % 3 vale 1 porque 7 = 2*3 + 1. Un número es par cuando n % 2 vale 0. Solo funciona con enteros.",
  k=["% devuelve el resto de una división.", "n % 2 == 0 indica que n es par.", "% solo funciona con enteros."],
  sit="Necesitas saber si un número es par. ¿Qué operador usas?",
  cod="""#include <stdio.h>

int main(void) {
    printf("%d\\n", 7 % 3);          // resto 1
    printf("%d\\n", 10 % 2 == 0);    // 1: es par
    return 0;
}""",
  h="calcula un resto y comprueba si 10 es par",
  pr=("El operador que da el resto de una división es el signo ___. (%)", "%"),
  ec="usar % con números decimales"),
K("Incremento ++ y --",
  d="operadores que suman o restan uno a una variable",
  u="contar de uno en uno de forma corta",
  mas="i++ equivale a i = i + 1 e i-- a i = i - 1. Se usan mucho en bucles. Como prefijo (++i) o sufijo (i++) cambian cuándo se aplica el cambio.",
  k=["++ suma uno a una variable.", "-- resta uno a una variable.", "i++ equivale a i = i + 1."],
  sit="Quieres sumar uno a un contador cada vez que ocurre algo, escribiendo lo menos posible. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int i = 5;
    i++;               // ahora 6
    i--;               // vuelve a 5
    printf("%d\\n", i);
    return 0;
}""",
  h="suma y resta uno a una variable",
  pr=("El operador que suma uno a una variable es ___. (++)", "++"),
  ec="confundir i++ con ++i dentro de una expresión"),
K("Operadores de comparación",
  d="símbolos como ==, !=, <, > que comparan dos valores",
  u="construir condiciones",
  mas="Devuelven 1 (verdadero) o 0 (falso). Para igualdad se usa == (dos signos); un solo = asigna y no compara.",
  k=["Los operadores de comparación devuelven 1 o 0.", "== compara igualdad.", "Un solo = asigna un valor, no compara."],
  sit="Quieres saber si la edad es mayor o igual a 18. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int edad = 20;
    printf("%d\\n", edad >= 18);   // 1: verdadero
    printf("%d\\n", edad == 30);   // 0: falso
    return 0;
}""",
  h="compara una edad con dos valores",
  pr=("Para comprobar igualdad se usa el operador ___. (==)", "=="),
  ec="usar = en lugar de == dentro de un if"),
K("Operadores lógicos",
  d="operadores &&, || y ! que combinan condiciones",
  u="comprobar varias condiciones a la vez",
  mas="&& es «y» (ambas verdaderas), || es «o» (basta una) y ! invierte. Evalúan de izquierda a derecha y se detienen en cuanto conocen el resultado.",
  k=["&& exige que se cumplan ambas condiciones.", "|| acepta que se cumpla alguna.", "! invierte una condición."],
  sit="Quieres comprobar que la edad sea mayor de 17 y además menor de 65. ¿Qué operador usas?",
  cod="""#include <stdio.h>

int main(void) {
    int edad = 30;
    printf("%d\\n", edad > 17 && edad < 65);   // 1
    printf("%d\\n", edad < 10 || edad > 20);   // 1
    printf("%d\\n", !(edad > 20));             // 0
    return 0;
}""",
  h="combina condiciones con y, o, no",
  pr=("El operador lógico «y» se escribe ___. (&&)", "&&"),
  ec="usar & en lugar de && para combinar condiciones"),
K("if y else",
  d="estructura que ejecuta código según una condición",
  u="tomar decisiones en el programa",
  mas="if ejecuta su bloque si la condición es distinta de cero. else cubre el caso contrario y else if permite encadenar varias condiciones.",
  k=["if ejecuta un bloque solo si la condición es verdadera.", "else se ejecuta cuando la condición es falsa.", "else if encadena condiciones."],
  sit="Debes mostrar un mensaje distinto según el usuario sea mayor de edad o no. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int edad = 20;
    if (edad >= 18) {
        printf("Mayor de edad\\n");
    } else {
        printf("Menor de edad\\n");
    }
    return 0;
}""",
  h="muestra si una persona es mayor de edad",
  pr=("La palabra del caso contrario de un if es ___. (4 letras)", "else"),
  ec="usar = dentro de la condición del if",
  err=("""#include <stdio.h>

int main(void) {
    int x = 5;
    if (x = 3) printf("tres");
    return 0;
}""", 5, "x = 3 asigna; para comparar hay que usar x == 3.")),
K("switch",
  d="estructura que elige entre varios casos según un valor",
  u="reemplazar muchos if encadenados",
  mas="switch compara una expresión entera con cada case. Cada caso suele terminar con break; si lo olvidas, la ejecución continúa en el siguiente (fall-through). default cubre los casos no previstos.",
  k=["switch elige un caso según un valor.", "break evita seguir con el caso siguiente.", "default cubre los valores no previstos."],
  sit="Según el número de día (1 a 7) debes mostrar su nombre y tienes muchas opciones. ¿Qué usas?",
  cod="""#include <stdio.h>

int main(void) {
    int dia = 2;
    switch (dia) {
        case 1: printf("Lunes\\n"); break;
        case 2: printf("Martes\\n"); break;   // break evita el fall-through
        default: printf("Otro día\\n");
    }
    return 0;
}""",
  h="muestra el nombre del día según su número",
  pr=("La palabra que evita pasar al siguiente caso es ___. (5 letras)", "break"),
  ec="olvidar break y ejecutar varios casos seguidos"),
]
