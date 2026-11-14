"""C++ · Etapa 1: Primeros pasos."""
from ..generador import K

LISTA = [
K("Qué es C++",
  d="lenguaje compilado que amplía C con clases, plantillas y una gran biblioteca estándar",
  u="crear programas rápidos, desde videojuegos hasta sistemas",
  mas="C++ conserva el control de bajo nivel de C y añade programación orientada a objetos y genéricos. Se usa en motores de juegos, navegadores y software de alto rendimiento.",
  k=["C++ es un lenguaje compilado.", "C++ amplía C con clases y plantillas.", "Se usa donde el rendimiento es importante."],
  sit="Necesitas programar un motor de videojuegos muy rápido con programación orientada a objetos. ¿Qué lenguaje eliges?",
  cod="""#include <iostream>

int main() {
    std::cout << "Hola desde C++" << std::endl;   // un programa mínimo
    return 0;
}""",
  h="muestra un saludo desde C++",
  pr=("C++ es un lenguaje ___ antes de ejecutarse. (compilado)", "compilado"),
  ec="creer que C++ y C son exactamente el mismo lenguaje"),
K("Compilar con g++",
  d="paso que traduce el código C++ a un ejecutable",
  u="obtener un programa que el sistema pueda ejecutar",
  mas="g++ programa.cpp -o programa compila el archivo. Con -std=c++17 eliges la versión del lenguaje y con -Wall activas advertencias útiles.",
  k=["g++ compila código C++.", "-std=c++17 elige la versión del lenguaje.", "-Wall activa advertencias útiles."],
  sit="Tienes un archivo .cpp y quieres un programa ejecutable. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    std::cout << "Compilado con g++" << "\\n";   // g++ -std=c++17 -Wall main.cpp -o main
    return 0;
}""",
  h="muestra un mensaje de un programa compilado con g++",
  pr=("El compilador de C++ de GNU se llama ___. (3 símbolos)", "g++"),
  ec="compilar un archivo .cpp con gcc sin enlazar la biblioteca de C++"),
K("Función main",
  d="función donde empieza la ejecución del programa",
  u="indicar el punto de entrada",
  mas="En C++ main devuelve int. Si llega al final sin return, el compilador asume return 0. Devolver un valor distinto de 0 indica error.",
  k=["main es el punto de entrada.", "main devuelve un int.", "Devolver 0 indica éxito."],
  sit="El enlazador dice que no encuentra por dónde empezar el programa. ¿Qué falta?",
  cod="""#include <iostream>

int main() {                          // aquí empieza todo
    std::cout << "Dentro de main\\n";
    return 0;                         // 0 = todo bien
}""",
  h="ejecuta el código de main y devuelve 0",
  pr=("La función donde empieza un programa C++ es ___. (4 letras)", "main"),
  ec="escribir void main en lugar de int main",
  err=("""#include <iostream>

void main() {
    std::cout << "Hola";
}""", 3, "main debe devolver int, no void.")),
K("iostream",
  d="cabecera de la biblioteca de entrada y salida de C++",
  u="mostrar y leer datos con cout y cin",
  mas="#include <iostream> declara cout, cin y cerr. Es la cabecera más usada en programas de consola.",
  k=["iostream declara cout y cin.", "Se incluye con #include.", "Es la cabecera de entrada y salida estándar."],
  sit="Quieres mostrar texto con cout y el compilador no lo reconoce. ¿Qué te falta?",
  cod="""#include <iostream>   // trae cout y cin

int main() {
    std::cout << "iostream incluido\\n";
    return 0;
}""",
  h="usa cout gracias a incluir iostream",
  pr=("La cabecera de entrada y salida de C++ es ___. (8 letras)", "iostream"),
  ec="usar cout sin incluir iostream"),
K("cout",
  d="flujo de salida que escribe en la pantalla",
  u="mostrar mensajes y valores",
  mas="Se usa con el operador << para encadenar valores: cout << \"Edad: \" << edad. \\n o endl producen un salto de línea.",
  k=["cout escribe en la pantalla.", "El operador << encadena valores.", "\\n produce un salto de línea."],
  sit="Debes mostrar varios valores seguidos en una línea. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    int edad = 20;
    std::cout << "Edad: " << edad << "\\n";   // << encadena valores
    return 0;
}""",
  h="muestra un texto y una variable con cout",
  pr=("El flujo que escribe en pantalla es ___. (4 letras)", "cout"),
  ec="usar >> en lugar de << con cout",
  err=("""#include <iostream>

int main() {
    std::cout >> "Hola";
}""", 4, "cout usa el operador <<, no >>.")),
K("Espacio de nombres std",
  d="espacio donde viven los elementos de la biblioteca estándar",
  u="evitar choques de nombres entre bibliotecas",
  mas="Los elementos estándar se escriben con el prefijo std::. Un espacio de nombres agrupa nombres para que no se confundan con los tuyos.",
  k=["std agrupa la biblioteca estándar.", "Se accede con std::nombre.", "Los espacios de nombres evitan choques de nombres."],
  sit="Tu código tiene una función llamada sort y la biblioteca también. ¿Qué evita el conflicto?",
  cod="""#include <iostream>

int main() {
    std::cout << "std:: indica el espacio de nombres\\n";
    return 0;
}""",
  h="usa el prefijo std:: para acceder a cout",
  pr=("El prefijo de la biblioteca estándar es ___::. (std)", "std"),
  ec="olvidar el prefijo std:: sin usar using"),
K("using namespace",
  d="directiva que permite omitir el prefijo de un espacio de nombres",
  u="escribir menos en programas pequeños",
  mas="using namespace std; permite escribir cout en vez de std::cout. En proyectos grandes se evita porque puede causar choques de nombres.",
  k=["using namespace permite omitir el prefijo.", "Es cómodo en programas pequeños.", "En proyectos grandes conviene evitarlo."],
  sit="En un ejercicio corto estás cansado de escribir std:: cada vez. ¿Qué usas?",
  cod="""#include <iostream>
using namespace std;   // ahora cout se escribe sin std::

int main() {
    cout << "Sin prefijo\\n";
    return 0;
}""",
  h="usa cout sin escribir el prefijo std::",
  pr=("La directiva para omitir std:: es using ___ std. (namespace)", "namespace"),
  ec="usar using namespace std en una cabecera"),
K("Comentarios",
  d="texto que el compilador ignora",
  u="explicar el código",
  mas="// comenta una línea y /* */ varias. Un buen comentario explica el porqué, no lo evidente.",
  k=["Los comentarios son ignorados al compilar.", "// comenta una línea.", "/* */ comenta varias líneas."],
  sit="Quieres dejar una nota para quien lea tu código. ¿Qué escribes?",
  cod="""#include <iostream>

int main() {
    // comentario de una línea
    /* comentario
       de varias líneas */
    std::cout << "ok\\n";
    return 0;
}""",
  h="muestra ok; los comentarios no se ejecutan",
  pr=("El comentario de una línea empieza con ___. (//)", "//"),
  ec="dejar un /* sin cerrar"),
K("Variables",
  d="espacio con nombre que guarda un valor",
  u="almacenar datos que el programa usa",
  mas="En C++ se declara el tipo antes del nombre. Se recomienda inicializar siempre con un valor, o con llaves: int n{5};.",
  k=["Una variable guarda un valor con nombre.", "Hay que declarar su tipo.", "Conviene inicializarla al declararla."],
  sit="Necesitas recordar la edad del usuario para usarla después. ¿Qué declaras?",
  cod="""#include <iostream>

int main() {
    int edad = 20;       // tipo nombre = valor
    edad = edad + 1;
    std::cout << edad << "\\n";
    return 0;
}""",
  h="guarda una edad y le suma uno",
  pr=("Antes del nombre de la variable se escribe su ___. (tipo)", "tipo"),
  ec="usar una variable sin inicializar",
  err=("""#include <iostream>

int main() {
    total = 5;
    std::cout << total;
}""", 4, "total no está declarada: falta su tipo (int total).")),
K("int y double",
  d="tipos para enteros y para decimales",
  u="calcular con números",
  mas="int guarda enteros y la división entre enteros descarta decimales. double guarda decimales con buena precisión.",
  k=["int guarda enteros.", "double guarda decimales.", "La división entre int descarta los decimales."],
  sit="Quieres guardar un precio con decimales. ¿Qué tipo usas?",
  cod="""#include <iostream>

int main() {
    int a = 7;
    double b = 2.5;
    std::cout << a / 2 << " " << b * 2 << "\\n";   // 3 y 5
    return 0;
}""",
  h="muestra una división entera y un producto decimal",
  pr=("El tipo para decimales es ___. (6 letras)", "double"),
  ec="esperar decimales al dividir dos enteros"),
K("char",
  d="tipo que guarda un solo carácter",
  u="trabajar con letras sueltas",
  mas="Se escribe entre comillas simples, como 'A'. Internamente es un número: el código de la letra.",
  k=["char guarda un solo carácter.", "Se escribe entre comillas simples.", "Internamente es un número."],
  sit="Quieres guardar una inicial. ¿Qué tipo usas?",
  cod="""#include <iostream>

int main() {
    char letra = 'B';
    std::cout << letra << " " << int(letra) << "\\n";   // letra y su código
    return 0;
}""",
  h="muestra una letra y su código numérico",
  pr=("Un solo carácter se guarda en un ___. (char)", "char"),
  ec="usar comillas dobles para un solo char"),
K("bool",
  d="tipo con solo dos valores: true y false",
  u="representar condiciones verdaderas o falsas",
  mas="Las comparaciones dan un bool. Con cout aparece como 1 o 0 salvo que uses boolalpha.",
  k=["bool solo admite true o false.", "Las comparaciones devuelven bool.", "cout muestra 1 o 0 por defecto."],
  sit="Quieres guardar si un usuario está activo (sí o no). ¿Qué tipo usas?",
  cod="""#include <iostream>

int main() {
    bool activo = true;
    std::cout << std::boolalpha << activo << "\\n";   // true en lugar de 1
    return 0;
}""",
  h="muestra un bool como true",
  pr=("El tipo que vale true o false es ___. (4 letras)", "bool"),
  ec="creer que un bool se muestra como la palabra true sin boolalpha"),
K("string",
  d="tipo de la biblioteca estándar para manejar texto",
  u="guardar y manipular cadenas cómodamente",
  mas="std::string crece automáticamente y ofrece métodos como size() y operadores como +. Necesita #include <string>.",
  k=["string guarda texto.", "size() devuelve su longitud.", "El operador + concatena textos."],
  sit="Debes guardar un nombre y poder unirlo con otros textos. ¿Qué usas?",
  cod="""#include <iostream>
#include <string>

int main() {
    std::string nombre = "Ana";
    std::string saludo = "Hola " + nombre;   // + une textos
    std::cout << saludo << " " << saludo.size() << "\\n";
    return 0;
}""",
  h="une dos textos y muestra su longitud",
  pr=("El tipo de la biblioteca para texto es std::___. (string)", "string"),
  ec="sumar dos literales de texto directamente"),
K("const",
  d="palabra que impide modificar una variable",
  u="proteger valores que no deben cambiar",
  mas="Una variable const debe inicializarse al declararla. El compilador rechaza cualquier intento de cambiarla.",
  k=["const impide modificar una variable.", "Debe inicializarse al declararla.", "Cambiarla da error de compilación."],
  sit="El valor de pi no debe cambiar jamás. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    const double PI = 3.14159;   // no se puede modificar
    std::cout << PI * 2 << "\\n";
    return 0;
}""",
  h="usa una constante PI en un cálculo",
  pr=("La palabra que impide modificar una variable es ___. (5 letras)", "const"),
  ec="intentar reasignar una variable const"),
K("auto",
  d="palabra que deja que el compilador deduzca el tipo",
  u="escribir menos en tipos largos",
  mas="Con auto x = 5; el compilador deduce que x es int. El tipo sigue siendo fijo: auto no significa «cualquier tipo».",
  k=["auto deduce el tipo de la variable.", "Exige que la variable se inicialice.", "El tipo deducido no cambia después."],
  sit="Un tipo es larguísimo y el compilador puede deducirlo del valor. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    auto n = 10;        // int
    auto x = 2.5;       // double
    std::cout << n + x << "\\n";
    return 0;
}""",
  h="deja que el compilador deduzca los tipos",
  pr=("La palabra que deduce el tipo es ___. (4 letras)", "auto"),
  ec="usar auto sin inicializar la variable"),
K("Operadores aritméticos",
  d="símbolos +, -, *, / y % que realizan cálculos",
  u="hacer operaciones matemáticas",
  mas="* y / se evalúan antes que + y -. El operador % da el resto de una división entera. Los paréntesis cambian el orden.",
  k=["+, -, *, / y % son operadores aritméticos.", "* y / van antes que + y -.", "% da el resto de la división."],
  sit="Quieres calcular el total de 3 productos a 5 más un envío de 2. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    std::cout << 3 * 5 + 2 << "\\n";    // 17
    std::cout << 17 % 5 << "\\n";       // resto 2
    return 0;
}""",
  h="calcula un total y un resto",
  pr=("El operador que da el resto de una división es ___. (%)", "%"),
  ec="olvidar la precedencia de * sobre +"),
K("Comparación y lógica",
  d="operadores ==, !=, <, >, && y || para formar condiciones",
  u="decidir según varias condiciones",
  mas="Las comparaciones devuelven bool. && exige que ambas condiciones sean verdaderas y || que lo sea al menos una. Un solo = asigna, no compara.",
  k=["== compara igualdad.", "&& exige ambas condiciones.", "|| exige al menos una."],
  sit="Quieres saber si la edad es mayor de 17 y menor de 65. ¿Qué operadores usas?",
  cod="""#include <iostream>

int main() {
    int edad = 30;
    std::cout << (edad > 17 && edad < 65) << "\\n";   // 1
    std::cout << (edad == 30 || edad == 31) << "\\n"; // 1
    return 0;
}""",
  h="combina condiciones con y, o",
  pr=("El operador lógico «y» es ___. (&&)", "&&"),
  ec="usar = en lugar de == en una condición"),
K("if y else",
  d="estructura que ejecuta código según una condición",
  u="tomar decisiones",
  mas="if ejecuta su bloque si la condición es verdadera; else cubre el resto y else if encadena varias condiciones.",
  k=["if ejecuta un bloque si la condición es verdadera.", "else cubre el caso contrario.", "else if encadena condiciones."],
  sit="Debes mostrar «mayor» o «menor» según la edad. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    int edad = 20;
    if (edad >= 18) std::cout << "Mayor\\n";
    else std::cout << "Menor\\n";
    return 0;
}""",
  h="muestra si la persona es mayor o menor",
  pr=("La palabra del caso contrario de un if es ___. (4 letras)", "else"),
  ec="olvidar las llaves en bloques de varias instrucciones"),
K("switch",
  d="estructura que elige entre varios casos según un valor",
  u="reemplazar muchos if encadenados",
  mas="Compara una expresión entera o enum con cada case. Cada caso suele cerrar con break; sin él continúa en el siguiente. default cubre el resto.",
  k=["switch elige un caso según un valor.", "break evita seguir con el siguiente caso.", "default cubre los valores no previstos."],
  sit="Según un número de día debes mostrar su nombre con muchas opciones. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    int dia = 2;
    switch (dia) {
        case 1: std::cout << "Lunes\\n"; break;
        case 2: std::cout << "Martes\\n"; break;   // break evita seguir
        default: std::cout << "Otro\\n";
    }
    return 0;
}""",
  h="muestra el nombre de un día según su número",
  pr=("La palabra que evita pasar al siguiente caso es ___. (5 letras)", "break"),
  ec="olvidar break y ejecutar varios casos"),
K("Operador ternario",
  d="operador ?: que elige entre dos valores según una condición",
  u="escribir un if corto dentro de una expresión",
  mas="La forma es condición ? valor_si_cierto : valor_si_falso. Es cómodo para asignaciones simples, pero no conviene anidarlo mucho.",
  k=["El ternario elige entre dos valores.", "Se escribe condición ? a : b.", "Es un if compacto dentro de una expresión."],
  sit="Quieres asignar «mayor» o «menor» a un texto en una sola línea. ¿Qué usas?",
  cod="""#include <iostream>
#include <string>

int main() {
    int edad = 20;
    std::string r = edad >= 18 ? "mayor" : "menor";   // condición ? si : no
    std::cout << r << "\\n";
    return 0;
}""",
  h="asigna mayor o menor con un operador ternario",
  pr=("El operador ternario usa los signos ? y ___. (:)", ":"),
  ec="anidar muchos ternarios y volverlos ilegibles"),
]
