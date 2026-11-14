"""C++ · Etapa 5: C++ moderno y profesional."""
from ..generador import K

LISTA = [
K("constexpr",
  d="palabra que permite evaluar un valor o función al compilar",
  u="calcular constantes sin coste al ejecutar",
  mas="Un valor constexpr se calcula durante la compilación. Una función constexpr puede evaluarse al compilar si recibe constantes.",
  k=["constexpr se evalúa al compilar.", "Sirve para constantes calculadas.", "Una función constexpr puede usarse en tiempo de compilación."],
  sit="Quieres que un cálculo con constantes se haga al compilar y no al ejecutar. ¿Qué usas?",
  cod="""#include <iostream>

constexpr int cuadrado(int n) { return n * n; }

int main() {
    constexpr int c = cuadrado(7);   // calculado al compilar
    std::cout << c << "\\n";
    return 0;
}""",
  h="calcula un cuadrado al compilar",
  pr=("La palabra que evalúa al compilar es ___. (constexpr)", "constexpr"),
  ec="creer que constexpr solo sirve para variables"),
K("static_assert",
  d="comprobación de una condición durante la compilación",
  u="detectar errores antes de ejecutar",
  mas="static_assert(condición, mensaje) falla la compilación si la condición es falsa. Se usa para verificar tamaños o suposiciones sobre tipos.",
  k=["static_assert comprueba al compilar.", "Si falla, no se genera el programa.", "Sirve para verificar suposiciones."],
  sit="Quieres asegurarte al compilar de que un int tiene al menos 4 bytes. ¿Qué usas?",
  cod="""#include <iostream>

static_assert(sizeof(int) >= 4, "int demasiado pequeño");   // se comprueba al compilar

int main() {
    std::cout << "comprobado\\n";
    return 0;
}""",
  h="comprueba una condición durante la compilación",
  pr=("La comprobación en tiempo de compilación es ___. (static_assert)", "static_assert"),
  ec="usar static_assert con valores que solo se conocen al ejecutar"),
K("Enlaces estructurados",
  d="sintaxis que descompone un par o estructura en varias variables",
  u="usar los campos de un par sin first ni second",
  mas="Se escribe auto [a, b] = valor. Es muy cómodo con pair, tuple y al recorrer un map.",
  k=["Los enlaces estructurados descomponen valores.", "Se escriben auto [a, b] = valor.", "Son útiles al recorrer un map."],
  sit="Quieres recorrer un map usando nombres claros en vez de first y second. ¿Qué usas?",
  cod="""#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> m = {{"Ana", 20}};
    for (const auto& [nombre, edad] : m) std::cout << nombre << " " << edad << "\\n";
    return 0;
}""",
  h="recorre un map con nombres claros para clave y valor",
  pr=("Descomponer un par se escribe auto ___ = par. ([a, b])", "[a, b]", "[a,b]"),
  ec="usar más nombres de los que tiene el par"),
K("variant",
  d="tipo que guarda un valor de uno entre varios tipos posibles",
  u="representar datos que pueden ser de tipos distintos",
  mas="std::variant<int, string> guarda un int o un string, nunca ambos. Se consulta con std::get o std::visit.",
  k=["variant guarda un valor de entre varios tipos.", "Solo tiene un tipo activo a la vez.", "Se consulta con std::get o std::visit."],
  sit="Un dato puede ser un número o un texto, pero nunca los dos. ¿Qué usas?",
  cod="""#include <iostream>
#include <variant>
#include <string>

int main() {
    std::variant<int, std::string> v = 42;
    v = std::string("hola");                     // ahora guarda texto
    std::cout << std::get<std::string>(v) << "\\n";
    return 0;
}""",
  h="guarda primero un número y luego un texto en un variant",
  pr=("El tipo que guarda uno entre varios tipos es std::___. (variant)", "variant"),
  ec="leer un tipo distinto del que está activo"),
K("std::function",
  d="contenedor que puede guardar cualquier función, lambda u objeto invocable",
  u="almacenar y pasar funciones con un tipo uniforme",
  mas="std::function<int(int)> guarda cualquier cosa que reciba un int y devuelva un int. Es más flexible, aunque algo más lento que una lambda directa.",
  k=["std::function guarda cualquier invocable.", "Se declara con la firma como tipo.", "Es flexible pero algo más lenta."],
  sit="Quieres guardar una función elegida en tiempo de ejecución en una variable. ¿Qué usas?",
  cod="""#include <iostream>
#include <functional>

int main() {
    std::function<int(int)> f = [](int n) { return n * 3; };
    std::cout << f(5) << "\\n";   // 15
    return 0;
}""",
  h="guarda una lambda en una variable y la llama",
  pr=("El contenedor genérico de funciones es std::___. (function)", "function"),
  ec="usar std::function donde basta una lambda directa"),
K("Capturas de lambda",
  d="forma de dar a una lambda acceso a variables externas",
  u="usar datos del entorno dentro de una lambda",
  mas="[x] captura x por copia, [&x] por referencia, [=] todo por copia y [&] todo por referencia. Capturar por referencia una variable que ya no existe es un error grave.",
  k=["[x] captura por copia.", "[&x] captura por referencia.", "Capturar por referencia una variable destruida es peligroso."],
  sit="Una lambda necesita usar una variable externa y modificarla. ¿Cómo la captura?",
  cod="""#include <iostream>

int main() {
    int total = 0;
    auto sumar = [&total](int n) { total += n; };   // captura por referencia
    sumar(5); sumar(7);
    std::cout << total << "\\n";   // 12
    return 0;
}""",
  h="acumula valores en una variable externa mediante una lambda",
  pr=("Capturar por referencia se escribe [___x]. (&)", "&"),
  ec="capturar por copia y esperar modificar la variable original"),
K("Algoritmos con lambdas",
  d="uso de count_if, transform y similares con criterios propios",
  u="procesar rangos con reglas personalizadas",
  mas="count_if cuenta los que cumplen una condición, transform aplica una función a cada elemento y any_of comprueba si alguno cumple.",
  k=["count_if cuenta según una condición.", "transform aplica una función a cada elemento.", "any_of comprueba si alguno cumple."],
  sit="Quieres contar cuántos números son pares en un vector. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> v = {1, 2, 3, 4, 5, 6};
    int pares = std::count_if(v.begin(), v.end(), [](int n) { return n % 2 == 0; });
    std::cout << pares << "\\n";   // 3
    return 0;
}""",
  h="cuenta los números pares de un vector",
  pr=("La función que cuenta según una condición es std::___. (count_if)", "count_if"),
  ec="escribir un bucle manual donde existe un algoritmo"),
K("string_view",
  d="vista ligera de solo lectura sobre un texto existente",
  u="pasar texto sin copiarlo",
  mas="std::string_view guarda un puntero y una longitud, sin copiar los caracteres. Es ideal como parámetro de solo lectura, pero el texto original debe seguir vivo.",
  k=["string_view es una vista de solo lectura.", "No copia los caracteres.", "El texto original debe seguir existiendo."],
  sit="Una función solo lee un texto y quieres evitar cualquier copia. ¿Qué tipo usas?",
  cod="""#include <iostream>
#include <string_view>

void mostrar(std::string_view s) {
    std::cout << s << " " << s.size() << "\\n";
}

int main() {
    mostrar("hola mundo");
    return 0;
}""",
  h="muestra un texto y su tamaño sin copiarlo",
  pr=("La vista de solo lectura sobre un texto es std::___. (string_view)", "string_view"),
  ec="guardar un string_view de un texto que ya se destruyó"),
K("Hilos",
  d="ejecución de varias tareas a la vez con std::thread",
  u="aprovechar varios núcleos del procesador",
  mas="std::thread ejecuta una función en paralelo. join() espera a que termine. Hay que llamar a join (o detach) antes de destruirlo.",
  k=["std::thread ejecuta una tarea en paralelo.", "join espera a que termine.", "Un hilo sin join provoca un error."],
  sit="Quieres ejecutar una tarea en segundo plano mientras el programa sigue. ¿Qué usas?",
  cod="""#include <iostream>
#include <thread>

void tarea() { std::cout << "tarea en otro hilo\\n"; }

int main() {
    std::thread t(tarea);
    t.join();                 // espera a que termine
    std::cout << "fin\\n";
    return 0;
}""",
  h="ejecuta una función en otro hilo y espera a que termine",
  pr=("El método que espera a que un hilo termine es ___. (join)", "join"),
  ec="destruir un std::thread sin llamar a join"),
K("mutex",
  d="objeto que impide que dos hilos usen un recurso a la vez",
  u="evitar condiciones de carrera",
  mas="Se bloquea con std::lock_guard, que libera el mutex automáticamente. Proteger los datos compartidos evita resultados impredecibles.",
  k=["Un mutex protege datos compartidos.", "lock_guard lo libera automáticamente.", "Evita condiciones de carrera."],
  sit="Dos hilos suman a la misma variable y los resultados salen mal. ¿Qué usas?",
  cod="""#include <iostream>
#include <thread>
#include <mutex>

int main() {
    int total = 0;
    std::mutex m;
    auto sumar = [&] { for (int i = 0; i < 1000; i++) { std::lock_guard<std::mutex> g(m); total++; } };
    std::thread a(sumar), b(sumar);
    a.join(); b.join();
    std::cout << total << "\\n";   // 2000
    return 0;
}""",
  h="dos hilos suman a una variable protegida con un mutex",
  pr=("El objeto que protege datos compartidos entre hilos es el ___. (mutex)", "mutex"),
  ec="modificar datos compartidos entre hilos sin protegerlos"),
K("Cabeceras y fuentes",
  d="división del código en archivos .h y .cpp",
  u="organizar proyectos grandes y compilar más rápido",
  mas="El .h declara la interfaz y el .cpp la implementa. Otros archivos incluyen el .h. Así solo se recompila lo que cambió.",
  k=["El .h declara y el .cpp implementa.", "Otros archivos incluyen el .h.", "Se recompila solo lo que cambió."],
  sit="Tu proyecto crece y quieres separar la declaración de la implementación. ¿Qué haces?",
  cod="""#include <iostream>

// saludo.h:   void saludar();
// saludo.cpp: void saludar() { ... }
void saludar() { std::cout << "Hola desde otro módulo\\n"; }

int main() {
    saludar();
    return 0;
}""",
  h="usa una función que viviría en su propio módulo",
  pr=("Las declaraciones se guardan en archivos con extensión ___. (.h)", ".h", "h", ".hpp"),
  ec="definir funciones completas en una cabecera incluida en varios archivos"),
K("Include guards y pragma once",
  d="protecciones para no incluir una cabecera dos veces",
  u="evitar errores de redefinición",
  mas="Se puede usar #ifndef/#define/#endif o la directiva #pragma once al inicio de la cabecera. Ambas evitan la doble inclusión.",
  k=["Evitan incluir una cabecera más de una vez.", "#pragma once lo hace con una sola línea.", "Se colocan en las cabeceras."],
  sit="Una cabecera incluida dos veces causa errores de redefinición. ¿Qué agregas?",
  cod="""#include <iostream>
#pragma once          // en una cabecera evita la doble inclusión

int main() {
    std::cout << "una sola inclusión\\n";
    return 0;
}""",
  h="muestra un mensaje y marca una cabecera como protegida",
  pr=("La directiva de una sola línea contra doble inclusión es #pragma ___. (once)", "once"),
  ec="olvidar la protección en una cabecera propia"),
K("CMake",
  d="herramienta que genera los archivos de compilación de un proyecto",
  u="compilar proyectos en distintas plataformas",
  mas="Un archivo CMakeLists.txt describe los archivos y opciones. CMake genera el sistema de compilación adecuado, como Makefiles.",
  k=["CMake genera archivos de compilación.", "Se configura con CMakeLists.txt.", "Funciona en varias plataformas."],
  sit="Tu proyecto debe compilarse igual en Linux, Windows y Mac. ¿Qué usas?",
  cod="""#include <iostream>

/* CMakeLists.txt:
   cmake_minimum_required(VERSION 3.10)
   project(app)
   add_executable(app main.cpp)     */
int main() {
    std::cout << "construido con CMake\\n";
    return 0;
}""",
  h="muestra un mensaje; el comentario describe un CMakeLists.txt",
  pr=("El archivo de configuración de CMake es ___.txt. (CMakeLists)", "cmakelists"),
  ec="escribir rutas absolutas dependientes del equipo"),
K("Const correctness",
  d="uso sistemático de const donde no se modifica un dato",
  u="evitar cambios accidentales y documentar la intención",
  mas="Se marcan const los parámetros por referencia, los métodos que no modifican y las variables que no cambian. El compilador ayuda a encontrar errores.",
  k=["const correctness usa const donde no se modifica nada.", "Ayuda al compilador a detectar errores.", "Documenta la intención del código."],
  sit="Quieres que el compilador te avise si una función modifica algo que no debía. ¿Qué práctica sigues?",
  cod="""#include <iostream>
#include <vector>

int suma(const std::vector<int>& v) {   // no puede modificar v
    int s = 0;
    for (int x : v) s += x;
    return s;
}

int main() {
    std::cout << suma({1, 2, 3}) << "\\n";
    return 0;
}""",
  h="suma los elementos de un vector sin poder modificarlo",
  pr=("Usar const donde no se modifica nada es const ___. (correctness)", "correctness"),
  ec="olvidar const en parámetros y métodos que no modifican"),
K("Regla del cero",
  d="diseñar clases sin escribir destructor ni copia manual",
  u="evitar errores de gestión de recursos",
  mas="Si tus atributos son vector, string o punteros inteligentes, no necesitas destructor ni constructores de copia: el compilador genera los correctos.",
  k=["La regla del cero evita escribir destructor y copia.", "Se apoya en contenedores y punteros inteligentes.", "El compilador genera lo necesario."],
  sit="Tu clase solo guarda strings y vectores. ¿Necesitas escribir un destructor?",
  cod="""#include <iostream>
#include <string>
#include <vector>

struct Alumno {
    std::string nombre;          // se libera solo
    std::vector<int> notas;      // se libera solo
};

int main() {
    Alumno a{"Ana", {7, 9}};
    std::cout << a.nombre << " " << a.notas.size() << "\\n";
    return 0;
}""",
  h="usa una clase que gestiona sus recursos sin destructor",
  pr=("La regla de no escribir destructor ni copia manual es la regla del ___. (cero)", "cero"),
  ec="escribir destructor sin necesitarlo"),
K("Advertencias y sanitizers",
  d="opciones del compilador que detectan errores sutiles",
  u="encontrar fallos de memoria y comportamientos indefinidos",
  mas="-Wall -Wextra muestran advertencias. -fsanitize=address detecta accesos inválidos a memoria y -fsanitize=undefined detecta comportamiento indefinido.",
  k=["-Wall y -Wextra activan advertencias.", "-fsanitize=address detecta errores de memoria.", "Ayudan a encontrar errores sutiles."],
  sit="Sospechas que tu programa accede a memoria que no debe. ¿Qué activas al compilar?",
  cod="""#include <iostream>

int main() {
    int v[3] = {1, 2, 3};
    std::cout << v[2] << "\\n";   // g++ -fsanitize=address detectaría v[3]
    return 0;
}""",
  h="accede a un elemento válido de un array",
  pr=("La opción que activa advertencias principales es -W___. (all)", "all"),
  ec="ignorar las advertencias del compilador"),
K("Formato de salida",
  d="manipuladores como setw y setprecision para dar formato",
  u="alinear columnas y controlar decimales",
  mas="Con <iomanip>, setw fija el ancho, setprecision los decimales (con fixed) y setfill el relleno.",
  k=["setw fija el ancho de un campo.", "setprecision controla los decimales.", "Se incluyen con iomanip."],
  sit="Quieres mostrar un precio siempre con dos decimales. ¿Qué usas?",
  cod="""#include <iostream>
#include <iomanip>

int main() {
    std::cout << std::fixed << std::setprecision(2) << 3.14159 << "\\n";   // 3.14
    std::cout << std::setw(5) << 42 << "\\n";                              // alineado
    return 0;
}""",
  h="muestra un decimal con dos cifras y un número con ancho fijo",
  pr=("La cabecera con setw y setprecision es ___. (iomanip)", "iomanip"),
  ec="olvidar fixed y obtener notación científica"),
K("Pruebas unitarias",
  d="pruebas automáticas de pequeñas partes del código",
  u="detectar errores al cambiar el programa",
  mas="Una prueba llama a una función con datos conocidos y comprueba el resultado. Bibliotecas como Catch2 o GoogleTest facilitan escribirlas.",
  k=["Una prueba unitaria comprueba una parte pequeña.", "Compara el resultado real con el esperado.", "Catch2 y GoogleTest son bibliotecas comunes."],
  sit="Cada vez que cambias código temes romper algo ya hecho. ¿Qué práctica te protege?",
  cod="""#include <iostream>
#include <cassert>

int doble(int n) { return n * 2; }

int main() {
    assert(doble(4) == 8);            // la prueba pasa si es cierto
    std::cout << "pruebas superadas\\n";
    return 0;
}""",
  h="comprueba con assert que una función da el resultado esperado",
  pr=("Una comprobación automática de una función es una prueba ___. (unitaria)", "unitaria"),
  ec="cambiar código sin pruebas que lo respalden"),
K("Buenas prácticas",
  d="costumbres para escribir C++ claro, seguro y mantenible",
  u="reducir errores y facilitar el trabajo en equipo",
  mas="Prefiere vector y string a arrays y char*, punteros inteligentes a new/delete, const y referencias, y nombres claros. Evita variables globales y macros cuando hay alternativas.",
  k=["Conviene preferir vector y string a arrays y char*.", "Conviene preferir punteros inteligentes a new y delete.", "Conviene evitar variables globales."],
  sit="Estás revisando código con muchos new, delete y arrays a mano. ¿Qué buena práctica aplicarías?",
  cod="""#include <iostream>
#include <vector>
#include <memory>

int main() {
    std::vector<int> v = {1, 2, 3};          // en vez de un array con new
    auto p = std::make_unique<int>(9);       // en vez de new/delete
    std::cout << v.size() << " " << *p << "\\n";
    return 0;
}""",
  h="usa vector y unique_ptr en lugar de gestión manual de memoria",
  pr=("Es preferible usar punteros ___ en lugar de new y delete. (inteligentes)", "inteligentes", "inteligente"),
  ec="mezclar gestión manual de memoria con contenedores modernos"),
K("std::array",
  d="array de tamaño fijo con la interfaz de un contenedor",
  u="tener un array seguro y con métodos como size()",
  mas="std::array<T, N> no decae a puntero y conoce su tamaño. Ofrece at(), size(), begin() y end(), sin coste extra respecto a un array normal.",
  k=["std::array tiene tamaño fijo conocido al compilar.", "Ofrece size() y at().", "No decae a puntero."],
  sit="Necesitas un array de tamaño fijo pero con métodos como size(). ¿Qué usas?",
  cod="""#include <iostream>
#include <array>

int main() {
    std::array<int, 3> a = {4, 5, 6};
    std::cout << a.size() << " " << a.at(1) << "\\n";   // 3 y 5
    return 0;
}""",
  h="usa un array de tamaño fijo con métodos de contenedor",
  pr=("El array moderno de tamaño fijo es std::___. (array)", "array"),
  ec="creer que std::array puede cambiar de tamaño"),
]
