"""C++ · Etapa 2: Bucles, funciones y contenedores."""
from ..generador import K

LISTA = [
K("Bucle while",
  d="bucle que repite mientras una condición sea verdadera",
  u="repetir sin saber cuántas veces",
  mas="La condición se evalúa antes de cada vuelta. Algo dentro del bucle debe cambiarla, o nunca terminará.",
  k=["while repite mientras la condición sea verdadera.", "La condición se evalúa antes de cada vuelta.", "Sin cambios en la condición, el bucle es infinito."],
  sit="Debes seguir repitiendo hasta que ocurra algo, sin saber cuántas veces. ¿Qué bucle usas?",
  cod="""#include <iostream>

int main() {
    int n = 3;
    while (n > 0) {
        std::cout << n << " ";
        n--;                      // cambia la condición
    }
    std::cout << "\\n";
    return 0;
}""",
  h="cuenta hacia atrás de 3 a 1",
  pr=("El bucle que repite mientras una condición es cierta es ___. (5 letras)", "while"),
  ec="olvidar modificar la variable de la condición"),
K("Bucle for",
  d="bucle con inicio, condición y paso en una línea",
  u="repetir un número conocido de veces",
  mas="for (inicio; condición; paso) controla un contador. Es el bucle clásico para recorrer rangos.",
  k=["for tiene inicio, condición y paso.", "Se usa cuando se conoce el número de repeticiones.", "El contador se declara dentro del for."],
  sit="Quieres mostrar los números del 1 al 5. ¿Qué bucle usas?",
  cod="""#include <iostream>

int main() {
    for (int i = 1; i <= 5; i++) std::cout << i << " ";
    std::cout << "\\n";
    return 0;
}""",
  h="muestra del 1 al 5",
  pr=("El bucle con inicio, condición y paso es ___. (3 letras)", "for"),
  ec="usar <= cuando se quería < y pasarse una vuelta"),
K("for por rango",
  d="bucle que recorre directamente los elementos de un contenedor",
  u="recorrer listas sin manejar índices",
  mas="La forma es for (auto x : contenedor). Para evitar copias se usa const auto&. Funciona con arrays, vector, map y más.",
  k=["El for por rango recorre los elementos de un contenedor.", "No necesita índice.", "const auto& evita copiar cada elemento."],
  sit="Quieres recorrer todos los elementos de una lista sin escribir índices. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {10, 20, 30};
    for (const auto& x : v) std::cout << x << " ";   // sin índices
    std::cout << "\\n";
    return 0;
}""",
  h="recorre un vector mostrando cada elemento",
  pr=("El for que recorre un contenedor usa los dos puntos ___. (:)", ":"),
  ec="modificar un contenedor mientras lo recorres"),
K("break y continue",
  d="instrucciones que salen del bucle o saltan a la siguiente vuelta",
  u="controlar la ejecución de un bucle",
  mas="break termina el bucle más interno. continue omite el resto de la vuelta actual y sigue con la siguiente.",
  k=["break sale del bucle.", "continue salta a la siguiente vuelta.", "Ambos afectan al bucle más interno."],
  sit="Quieres mostrar números del 1 al 5 sin el 3 y parar al llegar a 5. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    for (int i = 1; i <= 10; i++) {
        if (i == 3) continue;    // salta el 3
        if (i == 5) break;       // sale en el 5
        std::cout << i << " ";
    }
    std::cout << "\\n";
    return 0;
}""",
  h="muestra números saltando el 3 y parando en 5",
  pr=("La instrucción que sale de un bucle es ___. (5 letras)", "break"),
  ec="confundir break con continue"),
K("Funciones",
  d="bloque con nombre que realiza una tarea reutilizable",
  u="no repetir código y organizar el programa",
  mas="Una función tiene tipo de retorno, nombre, parámetros y cuerpo. Se llama escribiendo su nombre con paréntesis.",
  k=["Una función agrupa código reutilizable.", "Se llama por su nombre.", "Puede devolver un valor con return."],
  sit="Repites el mismo cálculo en varios lugares. ¿Qué haces?",
  cod="""#include <iostream>

int sumar(int a, int b) {
    return a + b;              // devuelve el resultado
}

int main() {
    std::cout << sumar(2, 3) << "\\n";
    return 0;
}""",
  h="suma dos números con una función",
  pr=("La instrucción que devuelve un valor es ___. (6 letras)", "return"),
  ec="llamar a una función antes de declararla",
  err=("""#include <iostream>

int main() {
    std::cout << doble(4);
}

int doble(int n) { return n * 2; }""", 4, "doble se usa antes de declararla: falta un prototipo arriba.")),
K("Paso por referencia",
  d="enviar a una función el propio dato en lugar de una copia",
  u="permitir que la función modifique el original",
  mas="Un parámetro declarado con & recibe el original. Evita copias y deja modificar la variable del que llama.",
  k=["Una referencia es otro nombre para la misma variable.", "El parámetro con & modifica el original.", "Evita copiar datos."],
  sit="Una función debe duplicar la variable del que la llama. ¿Cómo la recibe?",
  cod="""#include <iostream>

void duplicar(int& n) {   // & recibe el original
    n = n * 2;
}

int main() {
    int x = 4;
    duplicar(x);
    std::cout << x << "\\n";   // 8
    return 0;
}""",
  h="duplica una variable usando una referencia",
  pr=("Un parámetro por referencia se declara con el signo ___. (&)", "&"),
  ec="esperar cambios en el original con un parámetro por valor"),
K("Referencia constante",
  d="parámetro const& que evita copias sin permitir modificar",
  u="pasar datos grandes de forma eficiente y segura",
  mas="Para tipos pesados como string o vector, const& evita copiarlos y garantiza que la función no los modifique.",
  k=["const& evita copias.", "No permite modificar el dato.", "Es lo habitual para strings y vectores."],
  sit="Una función solo debe leer un texto largo sin copiarlo. ¿Cómo lo recibe?",
  cod="""#include <iostream>
#include <string>

void mostrar(const std::string& s) {   // sin copia y sin modificar
    std::cout << s << "\\n";
}

int main() {
    mostrar("texto largo");
    return 0;
}""",
  h="muestra un texto sin copiarlo",
  pr=("Un parámetro de solo lectura sin copia se declara ___&. (const)", "const"),
  ec="pasar objetos grandes por valor"),
K("Valores por defecto",
  d="valor que toma un parámetro si no se envía",
  u="permitir llamadas con menos argumentos",
  mas="Se escribe con = en la declaración. Los parámetros con valor por defecto van al final de la lista.",
  k=["Un valor por defecto se escribe con =.", "Se usa si se omite el argumento.", "Va al final de los parámetros."],
  sit="Si no se indica el saludo quieres usar «Hola». ¿Qué escribes?",
  cod="""#include <iostream>
#include <string>

void saludar(const std::string& n, const std::string& s = "Hola") {
    std::cout << s << " " << n << "\\n";
}

int main() {
    saludar("Ana");
    saludar("Luis", "Buenas");
    return 0;
}""",
  h="saluda con un saludo por defecto o uno elegido",
  pr=("El valor por defecto se asigna con el signo ___. (=)", "="),
  ec="poner un parámetro por defecto antes de uno obligatorio"),
K("Sobrecarga de funciones",
  d="varias funciones con el mismo nombre y distintos parámetros",
  u="usar un mismo nombre para operaciones parecidas",
  mas="El compilador elige la versión según el tipo y número de argumentos. El tipo de retorno por sí solo no basta para distinguirlas.",
  k=["La sobrecarga permite funciones con igual nombre.", "Deben diferir en sus parámetros.", "El compilador elige según los argumentos."],
  sit="Quieres una función «imprimir» que funcione con enteros y con textos. ¿Qué usas?",
  cod="""#include <iostream>
#include <string>

void imprimir(int n) { std::cout << "int " << n << "\\n"; }
void imprimir(const std::string& s) { std::cout << "texto " << s << "\\n"; }

int main() {
    imprimir(5);
    imprimir("hola");
    return 0;
}""",
  h="llama a la versión de imprimir adecuada para cada tipo",
  pr=("Varias funciones con el mismo nombre es ___. (sobrecarga)", "sobrecarga"),
  ec="intentar sobrecargar solo cambiando el tipo de retorno"),
K("Arrays",
  d="conjunto de elementos del mismo tipo y tamaño fijo",
  u="guardar varios valores bajo un nombre",
  mas="Se declaran con tamaño fijo: int a[3]. El primer índice es 0 y no se comprueban los límites, por eso en C++ moderno se prefieren vector o std::array.",
  k=["Un array tiene tamaño fijo.", "El primer índice es 0.", "No se comprueban los límites automáticamente."],
  sit="Debes guardar exactamente cinco notas de tamaño conocido. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    int notas[3] = {7, 9, 8};
    notas[1] = 10;
    std::cout << notas[0] << " " << notas[1] << "\\n";
    return 0;
}""",
  h="guarda tres notas y cambia una",
  pr=("El primer elemento de un array tiene índice ___. (0)", "0", "cero"),
  ec="acceder fuera de los límites del array"),
K("vector",
  d="contenedor de la biblioteca estándar que crece dinámicamente",
  u="guardar listas cuyo tamaño cambia",
  mas="std::vector<tipo> es un array dinámico. Conoce su tamaño con size(), crece solo y libera su memoria automáticamente.",
  k=["vector es un array que crece.", "size() devuelve cuántos elementos tiene.", "Libera su memoria automáticamente."],
  sit="No sabes cuántos elementos tendrá tu lista y debe crecer. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {1, 2, 3};
    std::cout << v.size() << "\\n";   // 3
    return 0;
}""",
  h="crea un vector y muestra su tamaño",
  pr=("El contenedor que crece dinámicamente es std::___. (vector)", "vector"),
  ec="usar arrays fijos cuando el tamaño cambia"),
K("push_back",
  d="método que añade un elemento al final de un vector",
  u="hacer crecer una lista",
  mas="push_back copia o mueve el elemento al final. pop_back quita el último. El tamaño aumenta o disminuye en uno.",
  k=["push_back añade un elemento al final.", "pop_back quita el último elemento.", "Cambia el tamaño del vector."],
  sit="Quieres añadir un número al final de una lista existente. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> v;
    v.push_back(5);
    v.push_back(8);
    std::cout << v.size() << " " << v.back() << "\\n";   // 2 y 8
    return 0;
}""",
  h="añade dos elementos a un vector vacío",
  pr=("El método que añade al final es ___. (push_back)", "push_back"),
  ec="intentar añadir con v[i] en un índice que no existe"),
K("Acceder a un vector",
  d="uso de [] y at() para leer elementos de un vector",
  u="obtener o modificar un elemento por posición",
  mas="v[i] no comprueba límites y es rápido; v.at(i) lanza una excepción si el índice no existe. front() y back() dan el primero y el último.",
  k=["v[i] accede por posición sin comprobar.", "at() comprueba los límites.", "front() y back() dan los extremos."],
  sit="Quieres leer un elemento y que falle claramente si el índice no existe. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {4, 5, 6};
    std::cout << v[0] << " " << v.at(2) << " " << v.front() << "\\n";
    return 0;
}""",
  h="lee elementos de un vector de distintas formas",
  pr=("El método que comprueba los límites al acceder es ___. (at)", "at"),
  ec="usar v[i] con un índice fuera del rango"),
K("map",
  d="contenedor que asocia claves con valores ordenados por clave",
  u="buscar valores a partir de una clave",
  mas="std::map<K, V> guarda pares clave-valor ordenados por clave. m[clave] accede al valor y lo crea si no existe.",
  k=["map asocia claves con valores.", "Mantiene las claves ordenadas.", "m[clave] crea el elemento si no existe."],
  sit="Quieres guardar la edad de cada persona buscándola por su nombre. ¿Qué usas?",
  cod="""#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> edades;
    edades["Ana"] = 20;
    edades["Luis"] = 25;
    std::cout << edades["Luis"] << "\\n";
    return 0;
}""",
  h="guarda edades por nombre y consulta una",
  pr=("El contenedor clave-valor ordenado es std::___. (map)", "map"),
  ec="consultar con [] una clave inexistente y crearla sin querer"),
K("set",
  d="contenedor de elementos únicos y ordenados",
  u="eliminar repetidos y comprobar pertenencia",
  mas="std::set guarda cada valor una sola vez y los mantiene ordenados. insert añade y count o find comprueban si existe.",
  k=["set guarda elementos únicos.", "Los mantiene ordenados.", "insert añade y count comprueba existencia."],
  sit="Tienes una lista con repetidos y quieres quedarte con cada valor una sola vez. ¿Qué usas?",
  cod="""#include <iostream>
#include <set>

int main() {
    std::set<int> s = {3, 1, 3, 2, 1};   // los repetidos se ignoran
    for (int x : s) std::cout << x << " ";
    std::cout << "\\n";
    return 0;
}""",
  h="elimina repetidos y muestra los valores ordenados",
  pr=("El contenedor de valores únicos es std::___. (set)", "set"),
  ec="esperar que set conserve el orden de inserción"),
K("pair",
  d="estructura que agrupa dos valores",
  u="devolver o guardar dos datos relacionados",
  mas="std::pair<A, B> tiene dos campos: first y second. std::make_pair o llaves crean pares. Los elementos de un map son pares.",
  k=["pair agrupa dos valores.", "Se accede con first y second.", "Los elementos de un map son pares."],
  sit="Una función debe devolver dos valores relacionados a la vez. ¿Qué usas?",
  cod="""#include <iostream>
#include <string>
#include <utility>

int main() {
    std::pair<std::string, int> p = {"Ana", 20};
    std::cout << p.first << " " << p.second << "\\n";
    return 0;
}""",
  h="guarda un nombre y una edad en un par",
  pr=("El primer elemento de un par se llama ___. (first)", "first"),
  ec="confundir first con second"),
K("Iteradores",
  d="objetos que apuntan a un elemento de un contenedor y avanzan por él",
  u="recorrer y manipular contenedores de forma genérica",
  mas="begin() apunta al primer elemento y end() justo después del último. Se avanza con ++ y se accede al valor con *.",
  k=["Un iterador apunta a un elemento.", "begin() apunta al inicio y end() al final.", "Se avanza con ++ y se desreferencia con *."],
  sit="Quieres recorrer cualquier contenedor con la misma técnica. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {1, 2, 3};
    for (auto it = v.begin(); it != v.end(); ++it) std::cout << *it << " ";
    std::cout << "\\n";
    return 0;
}""",
  h="recorre un vector con iteradores",
  pr=("El iterador que apunta al primer elemento es ___(). (begin)", "begin"),
  ec="desreferenciar end()"),
K("sort",
  d="algoritmo de la biblioteca que ordena un rango de elementos",
  u="ordenar listas sin escribir tu propio algoritmo",
  mas="std::sort(inicio, fin) ordena de menor a mayor. Se necesita #include <algorithm>. Admite un criterio propio como tercer argumento.",
  k=["sort ordena un rango.", "Está en la cabecera algorithm.", "Ordena de menor a mayor por defecto."],
  sit="Quieres ordenar un vector de números. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> v = {3, 1, 4, 2};
    std::sort(v.begin(), v.end());
    for (int x : v) std::cout << x << " ";
    std::cout << "\\n";
    return 0;
}""",
  h="ordena un vector de menor a mayor",
  pr=("La función que ordena un rango es std::___. (sort)", "sort"),
  ec="olvidar incluir algorithm"),
K("Funciones lambda",
  d="funciones anónimas que se escriben en el lugar donde se usan",
  u="pasar comportamientos cortos a algoritmos",
  mas="Se escriben como [captura](parámetros){ cuerpo }. Son ideales como criterio de ordenación o filtro.",
  k=["Una lambda es una función sin nombre.", "Se escribe con corchetes, parámetros y cuerpo.", "Es útil como argumento de algoritmos."],
  sit="Quieres ordenar de mayor a menor con un criterio corto, sin crear una función aparte. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> v = {3, 1, 4};
    std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });   // lambda
    for (int x : v) std::cout << x << " ";
    std::cout << "\\n";
    return 0;
}""",
  h="ordena de mayor a menor con una lambda",
  pr=("Una función anónima en C++ se llama ___. (lambda)", "lambda"),
  ec="olvidar capturar las variables externas que usa la lambda"),
K("Bucle do while",
  d="bucle que ejecuta el bloque al menos una vez y luego comprueba la condición",
  u="repetir algo que debe hacerse siempre una primera vez",
  mas="La condición se evalúa al final, por eso el cuerpo se ejecuta como mínimo una vez. Termina con punto y coma después del while.",
  k=["do while ejecuta el bloque al menos una vez.", "La condición se evalúa al final.", "do while termina con punto y coma."],
  sit="Un menú debe mostrarse siempre una vez y repetirse solo si el usuario lo pide. ¿Qué bucle usas?",
  cod="""#include <iostream>

int main() {
    int i = 10;
    do {
        std::cout << "i = " << i << "\\n";   // se ejecuta aunque la condición sea falsa
        i++;
    } while (i < 5);
    return 0;
}""",
  h="muestra i una vez aunque la condición sea falsa",
  pr=("El bucle que se ejecuta al menos una vez es do ___. (while)", "while"),
  ec="olvidar el punto y coma después del while"),
]
