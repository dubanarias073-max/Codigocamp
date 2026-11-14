"""Java · Etapa 3: Programación orientada a objetos."""
from ..generador import K

LISTA = [
K("Clases y objetos",
  d="una clase es la plantilla y un objeto es una instancia creada con new",
  u="modelar entidades con sus datos y acciones",
  mas="La clase define cómo es y qué hace algo. Con new se crea un objeto, y cada objeto tiene sus propios datos. Los objetos se usan con el operador punto.",
  k=["Una clase es una plantilla de objetos.", "new crea un objeto a partir de una clase.", "Cada objeto tiene sus propios datos."],
  sit="Quieres modelar muchos alumnos con la misma estructura. ¿Qué defines?",
  cod="""class Alumno {
    void saludar() { System.out.println("Hola, soy alumno"); }
}

public class Main {
    public static void main(String[] args) {
        Alumno a = new Alumno();   // objeto creado con new
        a.saludar();
    }
}""",
  out="Hola, soy alumno",
  h="define una clase y usa un objeto",
  pr=("La palabra que crea un objeto es ___. (new)", "new"),
  ec="usar la clase sin crear antes un objeto con new"),
K("Atributos y métodos",
  d="datos y funciones que pertenecen a una clase",
  u="guardar el estado del objeto y definir qué puede hacer",
  mas="Los atributos guardan datos del objeto. Los métodos son funciones de la clase que pueden usar y cambiar esos atributos.",
  k=["Los atributos guardan el estado.", "Los métodos definen el comportamiento.", "Un método puede usar los atributos del objeto."],
  sit="Quieres que cada contador recuerde su valor y sepa incrementarse. ¿Qué defines?",
  cod="""class Contador {
    int valor = 0;                 // atributo
    void sumar() { valor++; }      // método
}

public class Main {
    public static void main(String[] args) {
        Contador c = new Contador();
        c.sumar(); c.sumar();
        System.out.println(c.valor);
    }
}""",
  out="2",
  h="incrementa un contador mediante un método",
  pr=("Los datos de una clase se llaman ___. (atributos)", "atributos"),
  ec="olvidar que cada objeto tiene sus propios atributos"),
K("Constructor",
  d="método especial que inicializa un objeto al crearlo",
  u="dejar el objeto listo desde su creación",
  mas="Tiene el mismo nombre que la clase y no declara tipo de retorno. Recibe parámetros para asignar los atributos iniciales.",
  k=["El constructor se ejecuta al crear el objeto.", "Tiene el nombre de la clase.", "No declara tipo de retorno."],
  sit="Cada alumno debe nacer con su nombre y edad ya asignados. ¿Qué usas?",
  cod="""class Alumno {
    String nombre; int edad;
    Alumno(String nombre, int edad) {    // constructor
        this.nombre = nombre;
        this.edad = edad;
    }
}

public class Main {
    public static void main(String[] args) {
        Alumno a = new Alumno("Ana", 20);
        System.out.println(a.nombre + " " + a.edad);
    }
}""",
  out="Ana 20",
  h="crea un alumno con nombre y edad iniciales",
  pr=("El método que inicializa un objeto se llama ___. (constructor)", "constructor"),
  ec="ponerle tipo de retorno al constructor",
  err=("""class A {
    int x;
    void A(int x) { this.x = x; }
}""", 3, "Un constructor no lleva tipo de retorno: con void es un método normal.")),
K("this",
  d="referencia al objeto actual dentro de un método o constructor",
  u="distinguir atributos de parámetros con el mismo nombre",
  mas="this.nombre es el atributo del objeto y nombre sin this es el parámetro. También sirve para pasar el objeto actual a otro método.",
  k=["this representa el objeto actual.", "this.x es el atributo x del objeto.", "Evita ambigüedad con parámetros del mismo nombre."],
  sit="Un parámetro se llama igual que un atributo y necesitas distinguirlos. ¿Qué usas?",
  cod="""class P {
    int x;
    void poner(int x) { this.x = x; }    // this.x es el atributo
}

public class Main {
    public static void main(String[] args) {
        P p = new P();
        p.poner(7);
        System.out.println(p.x);
    }
}""",
  out="7",
  h="asigna un parámetro a un atributo del mismo nombre",
  pr=("La palabra que representa el objeto actual es ___. (this)", "this"),
  ec="asignar el parámetro a sí mismo en lugar de al atributo"),
K("Encapsulamiento",
  d="ocultar los datos internos y exponerlos solo mediante métodos",
  u="proteger los datos de cambios incorrectos",
  mas="Los atributos se declaran private y se accede a ellos con métodos public. Así la clase controla qué valores acepta.",
  k=["El encapsulamiento oculta los datos internos.", "Los atributos se declaran private.", "Se accede mediante métodos públicos."],
  sit="El saldo de una cuenta no debe modificarse directamente desde fuera. ¿Qué aplicas?",
  cod="""class Cuenta {
    private double saldo = 100;                // oculto al exterior
    public double ver() { return saldo; }      // acceso controlado
}

public class Main {
    public static void main(String[] args) {
        Cuenta c = new Cuenta();
        System.out.println(c.ver());
    }
}""",
  out="100.0",
  h="expone el saldo solo mediante un método",
  pr=("El modificador que oculta un miembro fuera de su clase es ___. (private)", "private"),
  ec="declarar todos los atributos public",
  err=("""class C {
    private int x = 1;
}

public class Main {
    public static void main(String[] args) {
        System.out.println(new C().x);
    }
}""", 7, "x es private: no se puede leer desde otra clase.")),
K("Getters y setters",
  d="métodos que leen y modifican atributos privados",
  u="controlar y validar el acceso a los datos",
  mas="Un getter devuelve el valor (getEdad) y un setter lo asigna (setEdad). El setter puede validar antes de guardar.",
  k=["Un getter devuelve el valor de un atributo.", "Un setter asigna el valor.", "El setter puede validar antes de guardar."],
  sit="Quieres validar que la edad no sea negativa cada vez que se asigna. ¿Qué usas?",
  cod="""class Persona {
    private int edad;
    public int getEdad() { return edad; }
    public void setEdad(int e) { if (e >= 0) edad = e; }   // valida
}

public class Main {
    public static void main(String[] args) {
        Persona p = new Persona();
        p.setEdad(20);
        p.setEdad(-5);              // se ignora
        System.out.println(p.getEdad());
    }
}""",
  out="20",
  h="guarda la edad solo si no es negativa",
  pr=("El método que asigna un atributo se llama ___. (setter)", "setter"),
  ec="crear setters que no validan nada"),
K("static",
  d="miembro que pertenece a la clase y no a cada objeto",
  u="compartir datos o utilidades sin crear objetos",
  mas="Un atributo static existe una sola vez y lo comparten todos los objetos. Se accede con NombreClase.miembro.",
  k=["static pertenece a la clase.", "Se comparte entre todos los objetos.", "Se accede con NombreClase.miembro."],
  sit="Quieres contar cuántos objetos se han creado en total. ¿Qué usas?",
  cod="""class Contador {
    static int total = 0;               // compartido
    Contador() { total++; }
}

public class Main {
    public static void main(String[] args) {
        new Contador(); new Contador(); new Contador();
        System.out.println(Contador.total);
    }
}""",
  out="3",
  h="cuenta cuántos objetos se crearon",
  pr=("Un atributo compartido por todos los objetos es ___. (static)", "static"),
  ec="usar un atributo static esperando que cada objeto tenga el suyo"),
K("Herencia",
  d="mecanismo por el que una clase hereda de otra con extends",
  u="reutilizar código entre clases relacionadas",
  mas="class Hija extends Padre hereda atributos y métodos no privados. Java solo permite heredar de una clase.",
  k=["extends crea una clase hija.", "La hija hereda atributos y métodos del padre.", "Java solo permite una clase padre."],
  sit="Perro y Gato comparten comportamiento de Animal. ¿Qué usas para no repetirlo?",
  cod="""class Animal {
    void respirar() { System.out.println("respira"); }
}
class Perro extends Animal {           // hereda de Animal
    void ladrar() { System.out.println("guau"); }
}

public class Main {
    public static void main(String[] args) {
        Perro p = new Perro();
        p.respirar();
        p.ladrar();
    }
}""",
  out="respira\nguau",
  h="un perro usa un método heredado y uno propio",
  pr=("La palabra para heredar de una clase es ___. (extends)", "extends"),
  ec="intentar heredar de dos clases a la vez"),
K("super",
  d="palabra que se refiere a la clase padre",
  u="reutilizar el constructor o los métodos del padre",
  mas="super(...) llama al constructor del padre y debe ser la primera línea del constructor de la hija. super.metodo() ejecuta la versión del padre.",
  k=["super llama al constructor del padre.", "super(...) debe ser la primera línea.", "super.metodo() usa la versión del padre."],
  sit="Una clase hija necesita ejecutar la inicialización de su padre antes de la suya. ¿Qué usas?",
  cod="""class Persona {
    String nombre;
    Persona(String nombre) { this.nombre = nombre; }
}
class Alumno extends Persona {
    Alumno(String nombre) {
        super(nombre);                 // llama al constructor del padre
    }
}

public class Main {
    public static void main(String[] args) {
        System.out.println(new Alumno("Ana").nombre);
    }
}""",
  out="Ana",
  h="inicializa el nombre con el constructor del padre",
  pr=("La palabra que se refiere a la clase padre es ___. (super)", "super"),
  ec="llamar a super después de otras instrucciones"),
K("@Override",
  d="anotación que indica que un método reemplaza el del padre",
  u="reescribir comportamiento heredado con seguridad",
  mas="Al reescribir un método de la clase padre se usa @Override. Si el nombre o los parámetros no coinciden, el compilador avisa del error.",
  k=["@Override marca un método que reemplaza al del padre.", "El compilador comprueba que realmente reemplaza algo.", "Se usa al reescribir métodos."],
  sit="Quieres que cada animal haga su propio sonido reemplazando el método del padre. ¿Qué usas?",
  cod="""class Animal {
    void hablar() { System.out.println("..."); }
}
class Perro extends Animal {
    @Override
    void hablar() { System.out.println("guau"); }   // reemplaza al del padre
}

public class Main {
    public static void main(String[] args) {
        new Perro().hablar();
    }
}""",
  out="guau",
  h="una clase hija reemplaza el método del padre",
  pr=("La anotación que marca un método reescrito es ___. (@Override)", "@override", "override"),
  ec="escribir mal el nombre del método y crear uno nuevo sin darse cuenta"),
K("Polimorfismo",
  d="capacidad de objetos distintos de responder al mismo método a su manera",
  u="tratar objetos distintos de forma uniforme",
  mas="Una variable del tipo padre puede guardar un objeto hijo. Al llamar a un método, Java ejecuta la versión del objeto real, no la del tipo de la variable.",
  k=["El polimorfismo permite que cada clase responda a su manera.", "Una variable padre puede guardar un objeto hijo.", "Java ejecuta la versión del objeto real."],
  sit="Tienes una lista de animales distintos y quieres que cada uno haga su propio sonido con la misma llamada. ¿Qué aprovechas?",
  cod="""class Animal { String hablar() { return "..."; } }
class Perro extends Animal { String hablar() { return "guau"; } }
class Gato extends Animal { String hablar() { return "miau"; } }

public class Main {
    public static void main(String[] args) {
        Animal[] zoo = { new Perro(), new Gato() };
        for (Animal a : zoo) System.out.println(a.hablar());
    }
}""",
  out="guau\nmiau",
  h="cada animal responde con su propio sonido",
  pr=("Que objetos distintos respondan al mismo método a su manera es ___. (polimorfismo)", "polimorfismo"),
  ec="usar muchos if para distinguir clases en lugar de polimorfismo"),
K("Clases abstractas",
  d="clases que no se pueden instanciar y pueden tener métodos sin cuerpo",
  u="definir una base común que obliga a las hijas a completar métodos",
  mas="Se declaran con abstract. Un método abstract no tiene cuerpo y cada clase hija debe implementarlo. No se puede hacer new de una clase abstracta.",
  k=["Una clase abstracta no se puede instanciar.", "Un método abstract no tiene cuerpo.", "Las hijas deben implementar los métodos abstractos."],
  sit="Quieres obligar a toda figura a calcular su área y no crear nunca una «figura» genérica. ¿Qué usas?",
  cod="""abstract class Figura {
    abstract double area();                 // sin cuerpo
}
class Cuadrado extends Figura {
    double lado;
    Cuadrado(double lado) { this.lado = lado; }
    double area() { return lado * lado; }
}

public class Main {
    public static void main(String[] args) {
        System.out.println(new Cuadrado(3).area());
    }
}""",
  out="9.0",
  h="calcula el área de un cuadrado desde una clase abstracta",
  pr=("La palabra que marca una clase como no instanciable es ___. (abstract)", "abstract"),
  ec="intentar crear un objeto de una clase abstracta"),
K("Interfaces",
  d="contrato que define métodos que una clase debe implementar",
  u="exigir un comportamiento sin imponer una herencia",
  mas="Una interface declara métodos sin cuerpo. Una clase la cumple con implements y puede implementar varias interfaces a la vez.",
  k=["Una interface define un contrato de métodos.", "Se cumple con implements.", "Una clase puede implementar varias interfaces."],
  sit="Quieres asegurar que la clase Pato tenga el método volar sin obligar a una herencia. ¿Qué usas?",
  cod="""interface Volador {
    void volar();
}
class Pato implements Volador {           // cumple el contrato
    public void volar() { System.out.println("El pato vuela"); }
}

public class Main {
    public static void main(String[] args) {
        Volador v = new Pato();
        v.volar();
    }
}""",
  out="El pato vuela",
  h="un pato cumple la interfaz Volador",
  pr=("Una clase cumple una interfaz con la palabra ___. (implements)", "implements"),
  ec="olvidar implementar un método de la interfaz"),
K("Métodos default",
  d="métodos con cuerpo dentro de una interfaz",
  u="añadir comportamiento común sin obligar a reescribirlo",
  mas="Desde Java 8 una interface puede incluir métodos default con cuerpo. Las clases que la implementan los heredan y pueden reemplazarlos.",
  k=["Un método default tiene cuerpo dentro de la interfaz.", "Las clases que implementan lo heredan.", "Se pueden reemplazar si hace falta."],
  sit="Quieres añadir un método a una interfaz sin romper a las clases que ya la implementan. ¿Qué usas?",
  cod="""interface Saludo {
    default void hola() { System.out.println("Hola por defecto"); }
}
class Persona implements Saludo { }

public class Main {
    public static void main(String[] args) {
        new Persona().hola();
    }
}""",
  out="Hola por defecto",
  h="una clase usa un método default de su interfaz",
  pr=("El método con cuerpo en una interfaz se marca ___. (default)", "default"),
  ec="creer que una interfaz no puede tener métodos con cuerpo"),
K("instanceof",
  d="operador que comprueba si un objeto es de una clase",
  u="saber de qué clase es un objeto en tiempo de ejecución",
  mas="x instanceof Clase devuelve true si x es de esa clase o de una hija. Se suele usar antes de convertir el objeto a un tipo más concreto.",
  k=["instanceof comprueba la clase de un objeto.", "Devuelve true también para subclases.", "Se usa antes de convertir tipos."],
  sit="Recibes un objeto y debes saber si es un Perro antes de pedirle que ladre. ¿Qué usas?",
  cod="""class Animal { }
class Perro extends Animal { void ladrar() { System.out.println("guau"); } }

public class Main {
    public static void main(String[] args) {
        Animal a = new Perro();
        if (a instanceof Perro) {
            ((Perro) a).ladrar();      // conversión segura
        }
    }
}""",
  out="guau",
  h="comprueba que es un perro antes de ladrar",
  pr=("El operador que comprueba la clase de un objeto es ___. (instanceof)", "instanceof"),
  ec="convertir un objeto sin comprobar antes su clase"),
K("toString",
  d="método que devuelve la representación en texto de un objeto",
  u="mostrar un objeto de forma legible",
  mas="Todas las clases heredan toString de Object. Si lo reescribes, println y la concatenación con + usan tu versión. Sin él se muestra algo poco útil como Alumno@1b6d3586.",
  k=["toString devuelve el objeto como texto.", "println usa toString automáticamente.", "Sin reescribirlo se muestra una referencia poco útil."],
  sit="Al imprimir un objeto sale un código raro en vez de sus datos. ¿Qué reescribes?",
  cod="""class Punto {
    int x = 1, y = 2;
    @Override
    public String toString() { return "(" + x + ", " + y + ")"; }
}

public class Main {
    public static void main(String[] args) {
        System.out.println(new Punto());
    }
}""",
  out="(1, 2)",
  h="muestra un objeto con una representación legible",
  pr=("El método que convierte un objeto en texto es ___. (toString)", "tostring"),
  ec="no reescribir toString y mostrar una referencia sin sentido"),
K("equals y hashCode",
  d="métodos para comparar objetos por su contenido",
  u="decidir cuándo dos objetos son iguales",
  mas="== compara referencias y equals compara contenido si lo reescribes. Si reescribes equals también debes reescribir hashCode para que funcionen HashMap y HashSet.",
  k=["equals compara el contenido de dos objetos.", "== compara referencias.", "Si reescribes equals, reescribe también hashCode."],
  sit="Dos objetos con los mismos datos deben considerarse iguales. ¿Qué reescribes?",
  cod="""class Punto {
    int x;
    Punto(int x) { this.x = x; }
    @Override
    public boolean equals(Object o) {
        return o instanceof Punto && ((Punto) o).x == x;
    }
    @Override
    public int hashCode() { return x; }
}

public class Main {
    public static void main(String[] args) {
        Punto a = new Punto(5), b = new Punto(5);
        System.out.println(a == b);          // false: distintas referencias
        System.out.println(a.equals(b));     // true: mismo contenido
    }
}""",
  out="false\ntrue",
  h="compara dos puntos por referencia y por contenido",
  pr=("El método para comparar el contenido de objetos es ___. (equals)", "equals"),
  ec="comparar objetos con == esperando comparar su contenido"),
K("enum",
  d="tipo con un conjunto fijo de constantes con nombre",
  u="representar opciones o estados limitados",
  mas="Se declara con enum y sus valores en mayúsculas. Puede usarse en un switch, y values() devuelve todas las constantes.",
  k=["enum define un conjunto fijo de constantes.", "values() devuelve todas las constantes.", "Se puede usar en un switch."],
  sit="Tu programa usa los estados «pendiente», «activo» y «cerrado». ¿Qué usas para representarlos?",
  cod="""enum Estado { PENDIENTE, ACTIVO, CERRADO }

public class Main {
    public static void main(String[] args) {
        Estado e = Estado.ACTIVO;
        System.out.println(e);
        System.out.println(Estado.values().length);   // 3
    }
}""",
  out="ACTIVO\n3",
  h="usa una enumeración de estados",
  pr=("El tipo de constantes con nombre es ___. (enum)", "enum"),
  ec="usar números o textos sueltos en lugar de un enum"),
K("Composición",
  d="clase que contiene objetos de otras clases como atributos",
  u="construir objetos complejos a partir de partes",
  mas="Se usa cuando un objeto «tiene un» otro (un coche tiene un motor). Suele ser preferible a la herencia cuando no hay relación «es un».",
  k=["La composición usa objetos como atributos.", "Expresa la relación «tiene un».", "Suele preferirse a la herencia cuando no hay «es un»."],
  sit="Un coche tiene un motor, pero no es un motor. ¿Qué relación usas?",
  cod="""class Motor { int cv = 90; }
class Coche {
    Motor motor = new Motor();         // un coche TIENE un motor
}

public class Main {
    public static void main(String[] args) {
        System.out.println(new Coche().motor.cv);
    }
}""",
  out="90",
  h="un coche contiene un objeto motor",
  pr=("La relación «tiene un» se logra por ___. (composición)", "composicion", "composición"),
  ec="usar herencia donde la relación es «tiene un»"),
K("record",
  d="clase compacta para guardar datos inmutables",
  u="crear clases de datos con muy poco código",
  mas="Desde Java 16, record Punto(int x, int y) genera constructor, getters, equals, hashCode y toString automáticamente. Sus campos no cambian.",
  k=["Un record es una clase compacta de datos.", "Genera constructor, getters y toString automáticamente.", "Sus campos son inmutables."],
  sit="Necesitas una clase solo para guardar dos valores sin escribir tanto código repetitivo. ¿Qué usas?",
  cod="""record Punto(int x, int y) { }

public class Main {
    public static void main(String[] args) {
        Punto p = new Punto(3, 4);
        System.out.println(p.x() + " " + p.y());
        System.out.println(p);
    }
}""",
  out="3 4\nPunto[x=3, y=4]",
  h="crea un punto con un record y lo muestra",
  pr=("La clase compacta de datos inmutables es un ___. (record)", "record"),
  ec="intentar modificar un campo de un record"),
]
