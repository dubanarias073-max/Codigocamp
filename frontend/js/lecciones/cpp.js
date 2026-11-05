// Lecciones de C++. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"C++ amplía C con clases y una biblioteca muy completa.",
    p:["cout imprime en pantalla", "<< encadena los datos"],
    c:`#include <iostream>
using namespace std;

int main() {
  cout << "¡Hola, CódigoCamp!" << endl;
  return 0;
}` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"Igual que en C, pero la salida es más cómoda.",
    p:["int, double, string", "if / else como en C"],
    c:`#include <iostream>
using namespace std;

int main() {
  int edad = 20;
  if (edad >= 18) cout << "Mayor de edad" << endl;
  return 0;
}` },
  { m:"Fundamentos", t:"Bucles", x:"for repite un bloque un número conocido de veces.",
    p:["for (inicio; condición; paso)", "endl termina la línea"],
    c:`#include <iostream>
using namespace std;

int main() {
  for (int i = 1; i <= 5; i++) {
    cout << "Vuelta " << i << endl;
  }
  return 0;
}` },
  { m:"Fundamentos", t:"Funciones", x:"Una función agrupa instrucciones y puede devolver un valor.",
    p:["Indica el tipo que devuelve", "return devuelve el resultado"],
    c:`#include <iostream>
using namespace std;

int doble(int n) {
  return n * 2;
}

int main() {
  cout << doble(21) << endl;
  return 0;
}` },
  { m:"Intermedio", t:"Vectores y mapas", x:"std::vector es un arreglo que crece y std::map asocia claves con valores. La STL trae algoritmos como sort.",
    p:["push_back agrega al final", "std::sort ordena un rango", "map guarda pares clave-valor ordenados"],
    c:"#include <iostream>\n#include <vector>\n#include <map>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n  vector<int> nums = {3, 1, 2};\n  nums.push_back(0);\n  sort(nums.begin(), nums.end());\n  for (int n : nums) cout << n << \" \";\n  cout << endl;\n\n  map<string, int> edades = {{\"Ana\", 20}, {\"Luis\", 25}};\n  cout << edades[\"Ana\"] << endl;\n  return 0;\n}",
    r:"Ordena el vector de mayor a menor con sort(nums.rbegin(), nums.rend())." },
  { m:"Intermedio", t:"Clases y objetos", x:"Una clase agrupa datos y funciones. El constructor inicializa el objeto y private oculta los datos.",
    p:["class define el tipo", "El constructor lleva el nombre de la clase", "private por defecto en class"],
    c:"#include <iostream>\n#include <string>\nusing namespace std;\n\nclass Persona {\n  string nombre;\n  int edad;\npublic:\n  Persona(string n, int e) : nombre(n), edad(e) {}\n  string saludar() const {\n    return \"Hola, soy \" + nombre + \" y tengo \" + to_string(edad);\n  }\n};\n\nint main() {\n  Persona p(\"Ana\", 20);\n  cout << p.saludar() << endl;\n  return 0;\n}",
    r:"Añade un método esMayor() que devuelva bool." },
  { m:"Avanzado", t:"Memoria y punteros inteligentes", x:"Los punteros inteligentes liberan la memoria solos. unique_ptr tiene un único dueño y shared_ptr cuenta referencias.",
    p:["make_unique crea un unique_ptr", "No hace falta llamar a delete", "RAII ata el recurso a la vida del objeto"],
    c:"#include <iostream>\n#include <memory>\nusing namespace std;\n\nstruct Caja {\n  int valor;\n  Caja(int v) : valor(v) { cout << \"Creada\" << endl; }\n  ~Caja() { cout << \"Destruida\" << endl; }\n};\n\nint main() {\n  auto c = make_unique<Caja>(42);\n  cout << c->valor << endl;\n  return 0;\n}",
    r:"Cambia a shared_ptr y copia el puntero para ver use_count().",
    e:"Mezclar new/delete a mano con punteros inteligentes provoca errores." },
  { m:"Avanzado", t:"Herencia y polimorfismo", x:"Una clase hereda con \":\" y las funciones virtual permiten que cada clase hija responda a su manera.",
    p:["virtual habilita el polimorfismo", "override indica que se reemplaza un método", "El destructor del padre debe ser virtual"],
    c:"#include <iostream>\n#include <memory>\nusing namespace std;\n\nclass Animal {\npublic:\n  virtual string sonido() const { return \"...\"; }\n  virtual ~Animal() = default;\n};\n\nclass Perro : public Animal {\npublic:\n  string sonido() const override { return \"Guau\"; }\n};\n\nint main() {\n  unique_ptr<Animal> a = make_unique<Perro>();\n  cout << a->sonido() << endl;\n  return 0;\n}",
    r:"Crea la clase Gato y guarda varios animales en un vector de unique_ptr." },
  { m:"Experto", t:"Plantillas y lambdas", x:"Las plantillas escriben código para cualquier tipo y las lambdas son funciones anónimas muy usadas con la STL.",
    p:["template <typename T> crea una plantilla", "[](int x){ ... } es una lambda", "Las lambdas capturan variables con [ ]"],
    c:"#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\ntemplate <typename T>\nT mayor(T a, T b) { return a > b ? a : b; }\n\nint main() {\n  cout << mayor(3, 7) << \" \" << mayor(2.5, 1.5) << endl;\n\n  vector<int> nums = {1, 2, 3, 4, 5, 6};\n  int pares = count_if(nums.begin(), nums.end(), [](int n) { return n % 2 == 0; });\n  cout << pares << endl;\n  return 0;\n}",
    r:"Usa una lambda con sort para ordenar de mayor a menor." },
  { m:"Experto", t:"C++ moderno y herramientas", x:"C++17 y C++20 añaden optional, structured bindings, ranges y concepts. CMake compila proyectos grandes.",
    p:["auto y rangos simplifican el código", "std::optional representa un valor opcional", "CMake describe cómo compilar"],
    c:"#include <iostream>\n#include <optional>\n#include <map>\nusing namespace std;\n\noptional<int> buscar(const map<string, int>& m, const string& k) {\n  auto it = m.find(k);\n  if (it == m.end()) return nullopt;\n  return it->second;\n}\n\nint main() {\n  map<string, int> edades = {{\"Ana\", 20}};\n  if (auto e = buscar(edades, \"Ana\")) cout << *e << endl;\n  cout << buscar(edades, \"Pedro\").value_or(-1) << endl;\n  return 0;\n}",
    r:"Compila con g++ -std=c++20 -Wall y revisa las advertencias." },
];
