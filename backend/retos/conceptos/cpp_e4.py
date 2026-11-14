"""C++ · Etapa 4: Memoria, plantillas y excepciones."""
from ..generador import K

LISTA = [
K("Punteros",
  d="variables que guardan la dirección de memoria de otro valor",
  u="acceder a datos de forma indirecta",
  mas="Se declaran con *. El operador & obtiene la dirección y * accede al valor apuntado. En C++ moderno se prefieren referencias y punteros inteligentes.",
  k=["Un puntero guarda una dirección de memoria.", "& obtiene la dirección y * accede al valor.", "Hay que inicializarlo antes de usarlo."],
  sit="Necesitas acceder a una variable a través de su dirección. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    int x = 10;
    int* p = &x;             // p guarda la dirección de x
    *p = 20;                 // cambia x a través del puntero
    std::cout << x << "\\n";
    return 0;
}""",
  h="cambia una variable a través de un puntero",
  pr=("Un puntero guarda una ___ de memoria. (dirección)", "direccion", "dirección"),
  ec="usar un puntero sin inicializar"),
K("new y delete",
  d="operadores que reservan y liberan memoria dinámica",
  u="crear objetos cuya vida controlas manualmente",
  mas="new reserva memoria y devuelve un puntero; delete la libera. Cada new necesita su delete. En código moderno se evitan a favor de punteros inteligentes.",
  k=["new reserva memoria dinámica.", "delete la libera.", "Cada new necesita su delete."],
  sit="Necesitas reservar memoria manualmente y liberarla después. ¿Qué usas?",
  cod="""#include <iostream>

int main() {
    int* p = new int(42);     // reserva
    std::cout << *p << "\\n";
    delete p;                 // libera
    return 0;
}""",
  h="reserva un entero con new y lo libera con delete",
  pr=("El operador que libera memoria dinámica es ___. (delete)", "delete"),
  ec="olvidar delete y causar una fuga de memoria"),
K("nullptr",
  d="valor que representa un puntero que no apunta a nada",
  u="marcar punteros vacíos de forma segura",
  mas="nullptr sustituye al antiguo NULL y tiene tipo propio. Conviene comprobar un puntero antes de usarlo.",
  k=["nullptr es un puntero vacío.", "Reemplaza a NULL en C++ moderno.", "Conviene comprobarlo antes de desreferenciar."],
  sit="Un puntero todavía no apunta a nada y quieres marcarlo así. ¿Qué valor usas?",
  cod="""#include <iostream>

int main() {
    int* p = nullptr;                // sin dirección
    if (p == nullptr) std::cout << "vacío\\n";
    return 0;
}""",
  h="comprueba que un puntero está vacío",
  pr=("El valor de un puntero vacío en C++ moderno es ___. (nullptr)", "nullptr"),
  ec="desreferenciar un nullptr"),
K("unique_ptr",
  d="puntero inteligente que posee en exclusiva un objeto y lo libera solo",
  u="gestionar memoria sin delete manual",
  mas="std::unique_ptr libera el objeto cuando sale del ámbito. No se puede copiar, solo mover. Se crea con std::make_unique.",
  k=["unique_ptr libera su objeto automáticamente.", "No se puede copiar, solo mover.", "Se crea con make_unique."],
  sit="Quieres gestionar memoria dinámica sin acordarte de llamar a delete. ¿Qué usas?",
  cod="""#include <iostream>
#include <memory>

int main() {
    auto p = std::make_unique<int>(7);   // dueño único
    std::cout << *p << "\\n";
    return 0;                            // se libera solo
}""",
  h="crea un entero gestionado por unique_ptr",
  pr=("El puntero inteligente de dueño único es ___. (unique_ptr)", "unique_ptr"),
  ec="intentar copiar un unique_ptr"),
K("shared_ptr",
  d="puntero inteligente que comparte la propiedad con un contador",
  u="permitir que varios dueños compartan un objeto",
  mas="Lleva un contador de referencias: el objeto se libera cuando el último shared_ptr desaparece. use_count() muestra cuántos lo comparten.",
  k=["shared_ptr comparte la propiedad del objeto.", "Usa un contador de referencias.", "El objeto se libera cuando el contador llega a cero."],
  sit="Varias partes del programa deben compartir el mismo objeto y liberarlo al terminar la última. ¿Qué usas?",
  cod="""#include <iostream>
#include <memory>

int main() {
    auto a = std::make_shared<int>(5);
    auto b = a;                              // comparten el objeto
    std::cout << a.use_count() << "\\n";     // 2
    return 0;
}""",
  h="comparte un entero entre dos punteros y cuenta los dueños",
  pr=("El puntero con propiedad compartida es ___. (shared_ptr)", "shared_ptr"),
  ec="crear ciclos de shared_ptr que nunca se liberan"),
K("RAII",
  d="técnica que liga la vida de un recurso a la vida de un objeto",
  u="liberar recursos automáticamente, incluso si hay errores",
  mas="El constructor adquiere el recurso y el destructor lo libera. Así no hay que acordarse de limpiar: ocurre al salir del ámbito. Los contenedores y los punteros inteligentes usan RAII.",
  k=["RAII liga un recurso a la vida de un objeto.", "El destructor libera el recurso.", "Funciona incluso cuando hay excepciones."],
  sit="Quieres que un archivo se cierre siempre, aunque el programa falle a mitad. ¿Qué técnica usas?",
  cod="""#include <iostream>

class Guardia {
public:
    Guardia() { std::cout << "adquirir\\n"; }
    ~Guardia() { std::cout << "liberar\\n"; }   // automático
};

int main() {
    Guardia g;
    std::cout << "trabajando\\n";
    return 0;
}""",
  h="adquiere y libera un recurso de forma automática",
  pr=("La técnica que libera recursos en el destructor se llama ___. (RAII)", "raii"),
  ec="liberar recursos a mano en vez de aprovechar el destructor"),
K("Semántica de movimiento",
  d="mecanismo que transfiere recursos en lugar de copiarlos",
  u="evitar copias costosas de datos grandes",
  mas="std::move convierte un objeto en candidato a ser «movido»: su contenido pasa a otro y el original queda vacío pero válido. Es mucho más barato que copiar.",
  k=["Mover transfiere recursos sin copiarlos.", "std::move pide que se mueva el objeto.", "El original queda en un estado válido pero vacío."],
  sit="Quieres pasar un vector enorme a otro sin copiar sus datos. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>
#include <utility>

int main() {
    std::vector<int> a = {1, 2, 3};
    std::vector<int> b = std::move(a);   // mueve los datos
    std::cout << b.size() << " " << a.size() << "\\n";   // 3 y 0
    return 0;
}""",
  h="mueve un vector a otro y deja el original vacío",
  pr=("La función que habilita mover un objeto es std::___. (move)", "move"),
  ec="usar un objeto después de moverlo esperando que conserve su contenido"),
K("Plantillas de función",
  d="funciones que sirven para varios tipos mediante un parámetro de tipo",
  u="escribir una sola función para muchos tipos",
  mas="Se declaran con template <typename T>. El compilador genera la versión para cada tipo que uses.",
  k=["Una plantilla de función sirve para varios tipos.", "Se declara con template <typename T>.", "El compilador genera una versión por tipo."],
  sit="Quieres una función que devuelva el mayor de dos valores, sean enteros o decimales. ¿Qué usas?",
  cod="""#include <iostream>

template <typename T>
T mayor(T a, T b) { return a > b ? a : b; }

int main() {
    std::cout << mayor(3, 7) << " " << mayor(2.5, 1.5) << "\\n";
    return 0;
}""",
  h="devuelve el mayor de dos valores de cualquier tipo",
  pr=("Una plantilla se declara con ___ <typename T>. (template)", "template"),
  ec="usar una plantilla con tipos que no admiten la operación"),
K("Plantillas de clase",
  d="clases que dependen de un tipo parámetro",
  u="crear estructuras reutilizables para cualquier tipo",
  mas="template <typename T> class Caja guarda un T. Al usarla se indica el tipo: Caja<int>. Los contenedores de la biblioteca estándar son plantillas.",
  k=["Una plantilla de clase depende de un tipo.", "Se usa como Caja<int>.", "vector y map son plantillas de clase."],
  sit="Quieres una «caja» que guarde un valor de cualquier tipo. ¿Qué defines?",
  cod="""#include <iostream>
#include <string>

template <typename T>
class Caja {
    T valor;
public:
    Caja(T v) : valor(v) {}
    T ver() const { return valor; }
};

int main() {
    Caja<int> a(5);
    Caja<std::string> b("hola");
    std::cout << a.ver() << " " << b.ver() << "\\n";
    return 0;
}""",
  h="crea cajas de entero y de texto con una misma plantilla",
  pr=("Una caja de enteros se escribe Caja___. (<int>)", "<int>"),
  ec="olvidar indicar el tipo al usar una plantilla de clase"),
K("Métodos de string",
  d="funciones de std::string para consultar y modificar texto",
  u="trabajar con cadenas con facilidad",
  mas="size() da la longitud, substr extrae una parte, find busca, append o += añade, y at() accede a un carácter con comprobación.",
  k=["size() devuelve la longitud.", "substr extrae una parte del texto.", "find busca dentro del texto."],
  sit="Quieres extraer una parte de un texto y saber dónde aparece una palabra. ¿Qué usas?",
  cod="""#include <iostream>
#include <string>

int main() {
    std::string s = "Hola mundo";
    std::cout << s.substr(0, 4) << " " << s.find("mundo") << "\\n";   // Hola y 5
    return 0;
}""",
  h="extrae una parte de un texto y busca una palabra",
  pr=("El método que busca dentro de un string es ___. (find)", "find"),
  ec="olvidar que find devuelve npos si no encuentra"),
K("to_string y stoi",
  d="funciones que convierten números a texto y texto a números",
  u="pasar datos entre tipos",
  mas="std::to_string convierte un número en texto y std::stoi un texto en entero. stoi lanza una excepción si el texto no es un número.",
  k=["to_string convierte números en texto.", "stoi convierte texto en entero.", "stoi lanza excepción si el texto no es válido."],
  sit="Tienes el texto «123» y necesitas sumarlo como número. ¿Qué usas?",
  cod="""#include <iostream>
#include <string>

int main() {
    int n = std::stoi("123") + 1;
    std::string t = std::to_string(n);
    std::cout << t << "\\n";   // 124
    return 0;
}""",
  h="convierte un texto en número, lo incrementa y lo vuelve texto",
  pr=("La función que convierte texto a entero es std::___. (stoi)", "stoi"),
  ec="usar stoi con texto no numérico sin controlar el error"),
K("stringstream",
  d="flujo en memoria para construir o leer texto con formato",
  u="armar y analizar cadenas como si fueran flujos",
  mas="std::ostringstream permite escribir con << y obtener el resultado con str(). std::istringstream lee con >> desde un texto.",
  k=["ostringstream construye texto con <<.", "istringstream lee datos con >>.", "str() devuelve el texto resultante."],
  sit="Quieres armar un mensaje juntando varios valores en un texto. ¿Qué usas?",
  cod="""#include <iostream>
#include <sstream>

int main() {
    std::ostringstream os;
    os << "x=" << 5 << ", y=" << 7;
    std::cout << os.str() << "\\n";
    return 0;
}""",
  h="construye un texto con varios valores",
  pr=("El flujo en memoria para construir texto es ___stringstream. (o)", "o", "ostringstream"),
  ec="olvidar llamar a str() para obtener el texto"),
K("Excepciones",
  d="mecanismo para señalar y manejar errores mediante throw y catch",
  u="separar el manejo de errores del flujo normal",
  mas="throw lanza un error, try rodea el código que puede fallar y catch lo captura. Si nadie lo captura, el programa termina.",
  k=["throw lanza una excepción.", "try rodea el código que puede fallar.", "catch captura y maneja la excepción."],
  sit="Una división puede fallar y quieres manejar el error sin que se caiga el programa. ¿Qué usas?",
  cod="""#include <iostream>
#include <stdexcept>

int main() {
    try {
        throw std::runtime_error("algo falló");   // lanza
    } catch (const std::exception& e) {           // captura
        std::cout << "Error: " << e.what() << "\\n";
    }
    return 0;
}""",
  h="lanza y captura una excepción mostrando su mensaje",
  pr=("La palabra que lanza una excepción es ___. (throw)", "throw"),
  ec="capturar excepciones por valor en lugar de por referencia"),
K("std::exception",
  d="clase base de las excepciones de la biblioteca estándar",
  u="capturar cualquier error estándar con un solo catch",
  mas="Clases como runtime_error, out_of_range e invalid_argument heredan de std::exception. El método what() devuelve el mensaje.",
  k=["std::exception es la base de las excepciones estándar.", "what() devuelve el mensaje de error.", "Se captura por referencia constante."],
  sit="Quieres capturar cualquier excepción estándar con un solo catch. ¿Qué tipo usas?",
  cod="""#include <iostream>
#include <vector>

int main() {
    std::vector<int> v = {1, 2};
    try {
        v.at(5);                                   // fuera de rango
    } catch (const std::exception& e) {
        std::cout << "capturado\\n";
    }
    return 0;
}""",
  h="captura el error de un acceso fuera de rango",
  pr=("El método que da el mensaje de una excepción es ___(). (what)", "what"),
  ec="usar catch (...) y perder información del error"),
K("Excepciones propias",
  d="clases que heredan de std::exception para errores del programa",
  u="distinguir tus errores de los demás",
  mas="Se crea una clase que hereda de std::exception y sobrescribe what(). Permite capturar tu error específico por separado.",
  k=["Una excepción propia hereda de std::exception.", "Sobrescribe what().", "Permite capturar tu error por separado."],
  sit="Quieres un error propio «SaldoInsuficiente» que se pueda capturar por separado. ¿Qué haces?",
  cod="""#include <iostream>
#include <exception>

class SaldoInsuficiente : public std::exception {
public:
    const char* what() const noexcept override { return "saldo insuficiente"; }
};

int main() {
    try { throw SaldoInsuficiente(); }
    catch (const SaldoInsuficiente& e) { std::cout << e.what() << "\\n"; }
    return 0;
}""",
  h="lanza y captura una excepción propia",
  pr=("Una excepción propia hereda de std::___. (exception)", "exception"),
  ec="lanzar tipos que no heredan de std::exception"),
K("Archivos con fstream",
  d="biblioteca para leer y escribir archivos con flujos",
  u="guardar y recuperar datos en disco",
  mas="ofstream escribe y ifstream lee. Se usan igual que cout y cin. Al salir del ámbito el archivo se cierra solo (RAII).",
  k=["ofstream escribe en archivos.", "ifstream lee de archivos.", "El archivo se cierra solo al salir del ámbito."],
  sit="Quieres guardar texto en un archivo y leerlo después. ¿Qué usas?",
  cod="""#include <iostream>
#include <fstream>
#include <string>

int main() {
    { std::ofstream out("datos.txt"); out << "hola archivo\\n"; }   // escribe y cierra
    std::ifstream in("datos.txt");
    std::string linea;
    std::getline(in, linea);
    std::cout << linea << "\\n";
    return 0;
}""",
  h="escribe una línea en un archivo y la vuelve a leer",
  pr=("El flujo para escribir en archivos es ___. (ofstream)", "ofstream"),
  ec="no comprobar si el archivo se abrió"),
K("getline",
  d="función que lee una línea completa de un flujo",
  u="leer texto con espacios",
  mas="std::getline(flujo, texto) lee hasta el salto de línea. A diferencia de >>, no se detiene en los espacios.",
  k=["getline lee una línea completa.", "No se detiene en los espacios.", "Guarda el resultado en un string."],
  sit="Quieres leer una frase completa con espacios. ¿Qué usas?",
  cod="""#include <iostream>
#include <sstream>
#include <string>

int main() {
    std::istringstream in("Hola mundo cruel\\nsegunda");
    std::string l;
    std::getline(in, l);          // toda la primera línea
    std::cout << l << "\\n";
    return 0;
}""",
  h="lee una línea completa con espacios",
  pr=("La función que lee una línea completa es std::___. (getline)", "getline"),
  ec="usar >> para leer frases con espacios"),
K("optional",
  d="tipo que puede contener un valor o estar vacío",
  u="representar resultados que pueden no existir",
  mas="std::optional<T> evita usar valores especiales como -1. has_value() comprueba si hay valor y value_or() da uno por defecto.",
  k=["optional puede contener un valor o estar vacío.", "has_value() comprueba si hay valor.", "value_or() da un valor por defecto."],
  sit="Una búsqueda puede no encontrar nada y no quieres usar -1 como señal. ¿Qué usas?",
  cod="""#include <iostream>
#include <optional>

std::optional<int> buscar(bool existe) {
    if (existe) return 42;
    return std::nullopt;               // sin valor
}

int main() {
    std::cout << buscar(true).value_or(-1) << " " << buscar(false).value_or(-1) << "\\n";
    return 0;
}""",
  h="devuelve un valor opcional y usa uno por defecto si falta",
  pr=("El tipo que puede estar vacío es std::___. (optional)", "optional"),
  ec="llamar a value() sobre un optional vacío"),
K("Rango y algoritmos numéricos",
  d="funciones como accumulate que operan sobre rangos de números",
  u="sumar, contar o transformar rangos sin escribir bucles",
  mas="std::accumulate suma un rango, std::count cuenta coincidencias y std::max_element encuentra el mayor. Evitan bucles repetitivos.",
  k=["accumulate suma los elementos de un rango.", "count cuenta coincidencias.", "max_element halla el mayor."],
  sit="Quieres sumar todos los elementos de un vector sin escribir un bucle. ¿Qué usas?",
  cod="""#include <iostream>
#include <vector>
#include <numeric>

int main() {
    std::vector<int> v = {1, 2, 3, 4};
    std::cout << std::accumulate(v.begin(), v.end(), 0) << "\\n";   // 10
    return 0;
}""",
  h="suma los elementos de un vector con accumulate",
  pr=("La función que suma un rango es std::___. (accumulate)", "accumulate"),
  ec="empezar accumulate con un valor inicial del tipo equivocado"),
K("weak_ptr",
  d="puntero inteligente que observa un objeto sin poseerlo",
  u="romper ciclos de shared_ptr",
  mas="Un weak_ptr no aumenta el contador de referencias. Antes de usar el objeto se convierte a shared_ptr con lock(), que devuelve vacío si ya fue liberado.",
  k=["weak_ptr observa sin poseer.", "No aumenta el contador de referencias.", "lock() obtiene un shared_ptr si el objeto sigue vivo."],
  sit="Dos objetos se apuntan mutuamente con shared_ptr y nunca se liberan. ¿Qué usas para romper el ciclo?",
  cod="""#include <iostream>
#include <memory>

int main() {
    auto s = std::make_shared<int>(9);
    std::weak_ptr<int> w = s;                 // observa, no posee
    if (auto p = w.lock()) std::cout << *p << " " << s.use_count() << "\\n";
    return 0;
}""",
  h="observa un objeto compartido sin aumentar su contador",
  pr=("El puntero que observa sin poseer es ___. (weak_ptr)", "weak_ptr"),
  ec="usar un weak_ptr sin comprobar si el objeto sigue vivo"),
]
