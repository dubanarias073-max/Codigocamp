"""C++ · Etapa 3: Programación orientada a objetos."""
from ..generador import K

LISTA = [
K("class",
  d="plantilla que define datos y comportamiento de un tipo de objeto",
  u="modelar entidades con sus propiedades y acciones",
  mas="Una clase agrupa atributos y métodos. Una vez definida, se crean objetos (instancias) de ella. Termina con punto y coma después de la llave.",
  k=["Una clase es una plantilla de objetos.", "Agrupa atributos y métodos.", "La definición termina con punto y coma."],
  sit="Quieres modelar un alumno con sus datos y acciones. ¿Qué defines?",
  cod="""#include <iostream>

class Alumno {
public:
    void saludar() { std::cout << "Hola, soy alumno\\n"; }
};

int main() {
    Alumno a;       // objeto
    a.saludar();
    return 0;
}""",
  h="define una clase y usa un objeto",
  pr=("La palabra para definir una plantilla de objetos es ___. (5 letras)", "class"),
  ec="olvidar el punto y coma al final de la clase",
  err=("""#include <iostream>

class A {
public:
    int x;
}

int main() {}""", 6, "Falta el punto y coma después de la llave de cierre de la clase.")),
K("Atributos y métodos",
  d="datos y funciones que pertenecen a una clase",
  u="guardar el estado del objeto y definir qué puede hacer",
  mas="Los atributos guardan datos del objeto. Los métodos son funciones de la clase que pueden usar y cambiar esos atributos.",
  k=["Los atributos guardan el estado.", "Los métodos definen el comportamiento.", "Un método puede usar los atributos del objeto."],
  sit="Quieres que cada contador recuerde su valor y sepa incrementarse. ¿Qué defines?",
  cod="""#include <iostream>

class Contador {
public:
    int valor = 0;                  // atributo
    void sumar() { valor++; }       // método
};

int main() {
    Contador c;
    c.sumar(); c.sumar();
    std::cout << c.valor << "\\n";
    return 0;
}""",
  h="incrementa un contador mediante un método",
  pr=("Los datos de una clase se llaman ___. (atributos)", "atributos"),
  ec="olvidar que cada objeto tiene sus propios atributos"),
K("Constructor",
  d="método especial que inicializa un objeto al crearlo",
  u="dejar el objeto listo desde su creación",
  mas="Tiene el mismo nombre que la clase y no devuelve nada. Una lista de inicialización (: nombre(valor)) es la forma recomendada de asignar atributos.",
  k=["El constructor se ejecuta al crear el objeto.", "Tiene el nombre de la clase.", "La lista de inicialización asigna los atributos."],
  sit="Cada alumno debe nacer con su nombre y edad ya asignados. ¿Qué usas?",
  cod="""#include <iostream>
#include <string>

class Alumno {
public:
    std::string nombre; int edad;
    Alumno(std::string n, int e) : nombre(n), edad(e) {}   // lista de inicialización
};

int main() {
    Alumno a("Ana", 20);
    std::cout << a.nombre << " " << a.edad << "\\n";
    return 0;
}""",
  h="crea un alumno con nombre y edad iniciales",
  pr=("El método que inicializa un objeto es el ___. (constructor)", "constructor"),
  ec="devolver un valor desde el constructor"),
K("Destructor",
  d="método que se ejecuta automáticamente al destruir un objeto",
  u="liberar recursos como memoria o archivos",
  mas="Se escribe con ~ y el nombre de la clase. Se llama al salir del ámbito del objeto. Es la base de RAII.",
  k=["El destructor se ejecuta al destruir el objeto.", "Se escribe con ~NombreClase.", "Sirve para liberar recursos."],
  sit="Un objeto abre un archivo y debe cerrarlo al desaparecer. ¿Qué usas?",
  cod="""#include <iostream>

class Recurso {
public:
    Recurso() { std::cout << "abrir\\n"; }
    ~Recurso() { std::cout << "cerrar\\n"; }   // se ejecuta al salir del ámbito
};

int main() {
    Recurso r;
    std::cout << "usando\\n";
    return 0;
}""",
  h="muestra cuándo se crea y se destruye un objeto",
  pr=("El destructor se escribe con el signo ___ delante del nombre. (~)", "~"),
  ec="olvidar liberar recursos en el destructor"),
K("public y private",
  d="modificadores que controlan quién accede a los miembros de una clase",
  u="ocultar los detalles internos",
  mas="public es accesible desde fuera. private solo desde dentro de la clase. En class el acceso por defecto es private; en struct, public.",
  k=["public es accesible desde fuera.", "private solo desde dentro de la clase.", "En class el acceso por defecto es private."],
  sit="El saldo de una cuenta no debe modificarse directamente desde fuera. ¿Qué modificador usas?",
  cod="""#include <iostream>

class Cuenta {
private:
    double saldo = 100;        // oculto al exterior
public:
    double ver() const { return saldo; }
};

int main() {
    Cuenta c;
    std::cout << c.ver() << "\\n";
    return 0;
}""",
  h="expone el saldo solo mediante un método público",
  pr=("El modificador que oculta miembros fuera de la clase es ___. (private)", "private"),
  ec="acceder a un miembro private desde fuera de la clase",
  err=("""#include <iostream>

class C {
    int x = 1;
};

int main() {
    C c;
    std::cout << c.x;
}""", 9, "x es private: no se puede leer desde fuera de la clase.")),
K("this",
  d="puntero al objeto actual dentro de un método",
  u="referirse al propio objeto",
  mas="Dentro de un método, this apunta al objeto sobre el que se llamó. Sirve para distinguir un atributo de un parámetro con el mismo nombre.",
  k=["this apunta al objeto actual.", "Se accede con this->.", "Sirve para evitar ambigüedades de nombres."],
  sit="Un parámetro se llama igual que un atributo y necesitas distinguirlos. ¿Qué usas?",
  cod="""#include <iostream>

class P {
public:
    int x = 0;
    void poner(int x) { this->x = x; }   // this->x es el atributo
};

int main() {
    P p;
    p.poner(7);
    std::cout << p.x << "\\n";
    return 0;
}""",
  h="asigna un parámetro a un atributo del mismo nombre",
  pr=("El puntero al objeto actual es ___. (this)", "this"),
  ec="asignar el parámetro a sí mismo en lugar de al atributo"),
K("Métodos const",
  d="métodos que prometen no modificar el objeto",
  u="permitir su uso con objetos constantes y documentar la intención",
  mas="Se escribe const después de los paréntesis. Un método const no puede cambiar atributos y es el único que se puede llamar sobre un objeto const.",
  k=["Un método const no modifica el objeto.", "Se escribe const tras los paréntesis.", "Solo estos métodos se llaman sobre objetos const."],
  sit="Un método solo lee datos y quieres garantizarlo. ¿Qué escribes?",
  cod="""#include <iostream>

class Caja {
    int n = 5;
public:
    int ver() const { return n; }   // const: no modifica
};

int main() {
    const Caja c;
    std::cout << c.ver() << "\\n";
    return 0;
}""",
  h="llama a un método const sobre un objeto constante",
  pr=("Un método que no modifica el objeto se marca ___. (const)", "const"),
  ec="modificar un atributo dentro de un método const"),
K("Herencia",
  d="mecanismo por el que una clase hereda de otra",
  u="reutilizar código entre clases relacionadas",
  mas="class Hija : public Padre hereda atributos y métodos públicos y protegidos. La hija puede añadir los suyos.",
  k=["La herencia reutiliza código de otra clase.", "Se escribe class Hija : public Padre.", "La hija añade sus propios miembros."],
  sit="Perro y Gato comparten comportamiento de Animal. ¿Qué usas para no repetirlo?",
  cod="""#include <iostream>

class Animal {
public:
    void respirar() { std::cout << "respira\\n"; }
};
class Perro : public Animal {      // hereda de Animal
public:
    void ladrar() { std::cout << "guau\\n"; }
};

int main() {
    Perro p;
    p.respirar();
    p.ladrar();
    return 0;
}""",
  h="un perro usa un método heredado y uno propio",
  pr=("La herencia se escribe class Hija : public ___. (Padre)", "padre", "base", "animal"),
  ec="repetir el mismo código en clases que podrían heredar"),
K("protected",
  d="modificador visible para la clase y sus derivadas",
  u="compartir miembros con las clases hijas",
  mas="Un miembro protected no es accesible desde fuera, pero sí desde las clases que heredan. Es un punto medio entre public y private.",
  k=["protected es visible para las clases hijas.", "No es visible desde fuera.", "Es un punto medio entre public y private."],
  sit="Quieres que una propiedad la vean las clases hijas pero no el exterior. ¿Qué usas?",
  cod="""#include <iostream>

class Animal {
protected:
    int energia = 10;
};
class Perro : public Animal {
public:
    void ver() { std::cout << energia << "\\n"; }   // accede a un protected
};

int main() {
    Perro p;
    p.ver();
    return 0;
}""",
  h="una clase hija lee un atributo protegido",
  pr=("El modificador visible para las hijas pero no desde fuera es ___. (protected)", "protected"),
  ec="confundir protected con private"),
K("virtual y override",
  d="palabras que permiten que una clase hija reemplace un método del padre",
  u="lograr comportamiento polimórfico",
  mas="Un método virtual se resuelve según el tipo real del objeto, no del puntero. override en la hija pide al compilador comprobar que de verdad reemplaza un método virtual.",
  k=["virtual permite sobrescribir un método.", "override comprueba que se reemplaza un método virtual.", "Habilita el polimorfismo."],
  sit="Quieres que cada animal haga su propio sonido aunque se use a través de un puntero a Animal. ¿Qué usas?",
  cod="""#include <iostream>

class Animal {
public:
    virtual void hablar() { std::cout << "...\\n"; }
};
class Perro : public Animal {
public:
    void hablar() override { std::cout << "guau\\n"; }
};

int main() {
    Perro p;
    Animal* a = &p;
    a->hablar();     // guau
    return 0;
}""",
  h="llama al método de la clase hija a través de un puntero base",
  pr=("La palabra que permite reemplazar un método en la hija es ___. (virtual)", "virtual"),
  ec="olvidar virtual en el método del padre"),
K("Clase abstracta",
  d="clase con al menos un método virtual puro que no puede instanciarse",
  u="definir una interfaz que las hijas deben implementar",
  mas="Un método virtual puro se declara con = 0. Una clase con alguno no se puede instanciar, y cada hija debe implementarlo.",
  k=["Una clase abstracta no se puede instanciar.", "Tiene métodos virtuales puros (= 0).", "Las hijas deben implementarlos."],
  sit="Quieres obligar a toda figura a calcular su área y no crear nunca una «figura» genérica. ¿Qué usas?",
  cod="""#include <iostream>

class Figura {
public:
    virtual double area() const = 0;     // virtual puro
    virtual ~Figura() = default;
};
class Cuadrado : public Figura {
    double l;
public:
    Cuadrado(double l) : l(l) {}
    double area() const override { return l * l; }
};

int main() {
    Cuadrado c(3);
    std::cout << c.area() << "\\n";
    return 0;
}""",
  h="calcula el área de un cuadrado desde una clase abstracta",
  pr=("Un método virtual puro termina con ___. (= 0)", "= 0", "=0"),
  ec="intentar crear un objeto de una clase abstracta"),
K("Sobrecarga de operadores",
  d="definir el comportamiento de operadores como + para tus clases",
  u="usar tus tipos con la sintaxis natural",
  mas="Se escribe operator+ (u otro) como método o función. Debe mantener el significado intuitivo del operador.",
  k=["Permite definir operadores para tus clases.", "Se escribe operator seguido del símbolo.", "Debe mantener un significado intuitivo."],
  sit="Quieres sumar dos puntos con el signo +. ¿Qué defines?",
  cod="""#include <iostream>

struct Punto {
    int x, y;
    Punto operator+(const Punto& o) const { return {x + o.x, y + o.y}; }
};

int main() {
    Punto a{1, 2}, b{3, 4};
    Punto c = a + b;
    std::cout << c.x << " " << c.y << "\\n";
    return 0;
}""",
  h="suma dos puntos con el operador +",
  pr=("Para sobrecargar + se define ___+. (operator)", "operator"),
  ec="darle a un operador un significado sorprendente"),
K("static",
  d="miembros que pertenecen a la clase y no a cada objeto",
  u="compartir datos entre todos los objetos",
  mas="Un atributo static existe una sola vez y lo comparten todas las instancias. Se accede con NombreClase::miembro.",
  k=["static pertenece a la clase.", "Se comparte entre todos los objetos.", "Se accede con NombreClase::miembro."],
  sit="Quieres contar cuántos objetos se han creado en total. ¿Qué usas?",
  cod="""#include <iostream>

class Contador {
public:
    static int total;                 // compartido
    Contador() { total++; }
};
int Contador::total = 0;

int main() {
    Contador a, b, c;
    std::cout << Contador::total << "\\n";   // 3
    return 0;
}""",
  h="cuenta cuántos objetos se crearon",
  pr=("Un atributo compartido por todos los objetos es ___. (static)", "static"),
  ec="olvidar definir fuera de la clase un atributo static"),
K("Composición",
  d="clase que contiene objetos de otras clases como atributos",
  u="construir objetos complejos a partir de partes",
  mas="Se usa cuando un objeto «tiene un» otro (un coche tiene un motor). Suele ser preferible a la herencia cuando no hay relación «es un».",
  k=["La composición usa objetos como atributos.", "Expresa la relación «tiene un».", "Suele preferirse a la herencia cuando no hay «es un»."],
  sit="Un coche tiene un motor, pero no es un motor. ¿Qué relación usas?",
  cod="""#include <iostream>

class Motor { public: int cv = 90; };
class Coche {
public:
    Motor motor;                 // un coche TIENE un motor
};

int main() {
    Coche c;
    std::cout << c.motor.cv << "\\n";
    return 0;
}""",
  h="un coche contiene un objeto motor",
  pr=("La relación «tiene un» se logra por ___. (composición)", "composicion", "composición"),
  ec="usar herencia donde la relación es «tiene un»"),
K("struct frente a class",
  d="diferencia de acceso por defecto entre struct y class",
  u="elegir la palabra adecuada según el uso",
  mas="En struct los miembros son public por defecto y en class son private. Por convención struct se usa para datos simples y class para objetos con comportamiento.",
  k=["En struct el acceso por defecto es public.", "En class el acceso por defecto es private.", "Son equivalentes salvo ese valor por defecto."],
  sit="Necesitas un tipo de datos simple con todos los campos accesibles. ¿Qué eliges por convención?",
  cod="""#include <iostream>

struct Punto { int x; int y; };   // public por defecto

int main() {
    Punto p{1, 2};
    std::cout << p.x + p.y << "\\n";
    return 0;
}""",
  h="usa un struct simple con campos públicos",
  pr=("El acceso por defecto de un struct es ___. (public)", "public"),
  ec="creer que struct y class son muy distintos"),
K("friend",
  d="palabra que da a una función o clase acceso a los miembros privados",
  u="permitir acceso especial sin hacer públicos los datos",
  mas="Una función friend no es miembro de la clase pero puede ver sus miembros privados. Se usa, por ejemplo, para sobrecargar << al mostrar objetos.",
  k=["friend da acceso a miembros privados.", "Una función friend no es miembro de la clase.", "Se usa a menudo para operator<<."],
  sit="Quieres mostrar un objeto con cout << obj accediendo a sus datos privados. ¿Qué usas?",
  cod="""#include <iostream>

class Punto {
    int x = 3, y = 4;
public:
    friend std::ostream& operator<<(std::ostream& os, const Punto& p) {
        return os << p.x << "," << p.y;   // accede a privados
    }
};

int main() {
    Punto p;
    std::cout << p << "\\n";
    return 0;
}""",
  h="muestra un objeto con cout usando una función friend",
  pr=("La palabra que da acceso a privados a una función es ___. (friend)", "friend"),
  ec="abusar de friend y romper el encapsulamiento"),
K("enum class",
  d="enumeración con alcance propio y tipado fuerte",
  u="evitar choques de nombres y conversiones accidentales",
  mas="Los valores se usan con el nombre del enum: Color::Rojo. No se convierten implícitamente a int, lo que evita errores.",
  k=["enum class tiene alcance propio.", "Los valores se usan como Color::Rojo.", "No se convierten implícitamente a int."],
  sit="Dos enumeraciones tienen un valor llamado Rojo y chocan. ¿Qué usas?",
  cod="""#include <iostream>

enum class Color { Rojo, Verde };

int main() {
    Color c = Color::Verde;
    std::cout << (c == Color::Verde) << "\\n";
    return 0;
}""",
  h="compara un valor de una enumeración con alcance",
  pr=("La enumeración con alcance propio es enum ___. (class)", "class"),
  ec="usar un enum class como si fuera un int"),
K("Espacios de nombres propios",
  d="bloque namespace que agrupa tus propios nombres",
  u="organizar el código y evitar choques",
  mas="Se escribe namespace nombre { ... }. Se accede con nombre::elemento. Ayuda a separar partes grandes de un programa.",
  k=["namespace agrupa nombres propios.", "Se accede con nombre::elemento.", "Evita choques entre partes del programa."],
  sit="Dos módulos de tu programa tienen una función llamada calcular. ¿Cómo las separas?",
  cod="""#include <iostream>

namespace geometria {
    int doble(int n) { return n * 2; }
}

int main() {
    std::cout << geometria::doble(21) << "\\n";
    return 0;
}""",
  h="usa una función dentro de un espacio de nombres propio",
  pr=("Para agrupar nombres propios se usa ___. (namespace)", "namespace"),
  ec="olvidar el prefijo del espacio de nombres al usar la función"),
K("Funciones miembro fuera de la clase",
  d="definir métodos fuera del cuerpo de la clase con ::",
  u="separar declaración e implementación",
  mas="Se declara el método dentro de la clase y se define fuera con Clase::metodo. Es la base de separar .h y .cpp.",
  k=["Un método puede definirse fuera de la clase.", "Se usa NombreClase::metodo.", "Separa la declaración de la implementación."],
  sit="Quieres dejar la clase limpia y escribir el código de sus métodos aparte. ¿Cómo lo haces?",
  cod="""#include <iostream>

class Saludo {
public:
    void decir();                       // declaración
};

void Saludo::decir() {                  // definición fuera de la clase
    std::cout << "Hola\\n";
}

int main() {
    Saludo s;
    s.decir();
    return 0;
}""",
  h="define un método fuera de su clase",
  pr=("Para definir un método fuera de la clase se usa el operador ___. (::)", "::"),
  ec="olvidar el prefijo Clase:: al definir el método"),
K("Constructor de copia",
  d="constructor que crea un objeto a partir de otro de su misma clase",
  u="controlar cómo se copian los objetos",
  mas="Se declara como Clase(const Clase& otro). Si no lo escribes, el compilador copia atributo por atributo. Es importante cuando la clase maneja recursos.",
  k=["El constructor de copia crea un objeto a partir de otro.", "Recibe una referencia constante a la misma clase.", "Por defecto copia atributo por atributo."],
  sit="Quieres controlar qué ocurre cuando un objeto se copia a otro. ¿Qué defines?",
  cod="""#include <iostream>

class Caja {
public:
    int valor;
    Caja(int v) : valor(v) {}
    Caja(const Caja& otra) : valor(otra.valor) { std::cout << "copiando\\n"; }
};

int main() {
    Caja a(5);
    Caja b = a;                    // usa el constructor de copia
    std::cout << b.valor << "\\n";
    return 0;
}""",
  h="copia un objeto con un constructor de copia propio",
  pr=("Un constructor de copia recibe una referencia ___ del mismo tipo. (const)", "const"),
  ec="olvidar el const o la referencia en el constructor de copia"),
]
