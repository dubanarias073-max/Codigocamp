"""C# · Etapa 3: Programación orientada a objetos."""
from ..generador import K

LISTA = [
K("Clases y objetos",
  d="una clase es la plantilla y un objeto es una instancia creada con new",
  u="modelar entidades con sus datos y acciones",
  mas="La clase define cómo es y qué hace algo. Con new se crea un objeto y cada objeto tiene sus propios datos. Los objetos se usan con el operador punto.",
  k=["Una clase es una plantilla de objetos.", "new crea un objeto a partir de una clase.", "Cada objeto tiene sus propios datos."],
  sit="Quieres modelar muchos alumnos con la misma estructura. ¿Qué defines?",
  cod="""using System;

class Alumno {
    public void Saludar() { Console.WriteLine("Hola, soy alumno"); }
}

class Program {
    static void Main() {
        Alumno a = new Alumno();    // objeto creado con new
        a.Saludar();
    }
}""",
  out="Hola, soy alumno",
  h="define una clase y usa un objeto",
  pr=("La palabra que crea un objeto es ___. (new)", "new"),
  ec="usar la clase sin crear antes un objeto con new"),
K("Campos y métodos",
  d="datos y funciones que pertenecen a una clase",
  u="guardar el estado del objeto y definir qué puede hacer",
  mas="Los campos guardan datos del objeto. Los métodos son funciones de la clase que pueden usar y cambiar esos campos.",
  k=["Los campos guardan el estado.", "Los métodos definen el comportamiento.", "Un método puede usar los campos del objeto."],
  sit="Quieres que cada contador recuerde su valor y sepa incrementarse. ¿Qué defines?",
  cod="""using System;

class Contador {
    public int valor = 0;                  // campo
    public void Sumar() { valor++; }       // método
}

class Program {
    static void Main() {
        var c = new Contador();
        c.Sumar(); c.Sumar();
        Console.WriteLine(c.valor);
    }
}""",
  out="2",
  h="incrementa un contador mediante un método",
  pr=("Los datos de una clase se guardan en ___. (campos)", "campos", "atributos"),
  ec="olvidar que cada objeto tiene sus propios campos"),
K("Constructor",
  d="método especial que inicializa un objeto al crearlo",
  u="dejar el objeto listo desde su creación",
  mas="Tiene el mismo nombre que la clase y no declara tipo de retorno. Recibe parámetros para asignar los valores iniciales.",
  k=["El constructor se ejecuta al crear el objeto.", "Tiene el nombre de la clase.", "No declara tipo de retorno."],
  sit="Cada alumno debe nacer con su nombre y edad ya asignados. ¿Qué usas?",
  cod="""using System;

class Alumno {
    public string nombre; public int edad;
    public Alumno(string nombre, int edad) {     // constructor
        this.nombre = nombre;
        this.edad = edad;
    }
}

class Program {
    static void Main() {
        var a = new Alumno("Ana", 20);
        Console.WriteLine(a.nombre + " " + a.edad);
    }
}""",
  out="Ana 20",
  h="crea un alumno con nombre y edad iniciales",
  pr=("El método que inicializa un objeto se llama ___. (constructor)", "constructor"),
  ec="ponerle tipo de retorno al constructor"),
K("this",
  d="referencia al objeto actual dentro de un método o constructor",
  u="distinguir campos de parámetros con el mismo nombre",
  mas="this.x es el campo del objeto y x sin this es el parámetro. También sirve para pasar el objeto actual a otro método.",
  k=["this representa el objeto actual.", "this.x es el campo x del objeto.", "Evita ambigüedad con parámetros del mismo nombre."],
  sit="Un parámetro se llama igual que un campo y necesitas distinguirlos. ¿Qué usas?",
  cod="""using System;

class P {
    public int x;
    public void Poner(int x) { this.x = x; }    // this.x es el campo
}

class Program {
    static void Main() {
        var p = new P();
        p.Poner(7);
        Console.WriteLine(p.x);
    }
}""",
  out="7",
  h="asigna un parámetro a un campo del mismo nombre",
  pr=("La palabra que representa el objeto actual es ___. (this)", "this"),
  ec="asignar el parámetro a sí mismo en lugar de al campo"),
K("Encapsulamiento",
  d="ocultar los datos internos y exponerlos solo mediante miembros controlados",
  u="proteger los datos de cambios incorrectos",
  mas="Los campos se declaran private y se exponen con propiedades o métodos public. Así la clase controla qué valores acepta. private es el acceso por defecto en una clase.",
  k=["El encapsulamiento oculta los datos internos.", "Los campos se declaran private.", "private es el acceso por defecto de un miembro de clase."],
  sit="El saldo de una cuenta no debe modificarse directamente desde fuera. ¿Qué aplicas?",
  cod="""using System;

class Cuenta {
    private int saldo = 100;                       // oculto al exterior
    public int Ver() { return saldo; }             // acceso controlado
}

class Program {
    static void Main() {
        var c = new Cuenta();
        Console.WriteLine(c.Ver());
    }
}""",
  out="100",
  h="expone el saldo solo mediante un método",
  pr=("El modificador que oculta un miembro fuera de su clase es ___. (private)", "private"),
  ec="declarar todos los campos public",
  err=("""using System;

class C {
    private int x = 1;
}

class Program {
    static void Main() {
        Console.WriteLine(new C().x);
    }
}""", 9, "x es private: no se puede leer desde otra clase.")),
K("Propiedades",
  d="miembros con get y set que controlan el acceso a un dato",
  u="leer y validar datos como si fueran campos",
  mas="Una propiedad se declara con get y set. Se usa como un campo, pero el set puede validar. value es el valor que se está asignando.",
  k=["Una propiedad usa get y set.", "Se usa como si fuera un campo.", "El set puede validar con value."],
  sit="Quieres validar que la edad no sea negativa cada vez que se asigna. ¿Qué usas?",
  cod="""using System;

class Persona {
    private int edad;
    public int Edad {
        get { return edad; }
        set { if (value >= 0) edad = value; }   // valida
    }
}

class Program {
    static void Main() {
        var p = new Persona();
        p.Edad = 20;
        p.Edad = -5;             // se ignora
        Console.WriteLine(p.Edad);
    }
}""",
  out="20",
  h="guarda la edad solo si no es negativa",
  pr=("La palabra que representa el valor asignado en un set es ___. (value)", "value"),
  ec="crear propiedades set que no validan nada"),
K("Propiedades automáticas",
  d="propiedades con get y set sin escribir el campo",
  u="declarar datos con muy poco código",
  mas="public string Nombre { get; set; } crea el campo oculto automáticamente. Con init solo se puede asignar al crear el objeto.",
  k=["Una propiedad automática no necesita campo propio.", "Se escribe { get; set; }.", "init permite asignar solo al crear el objeto."],
  sit="Necesitas un dato simple con acceso de lectura y escritura sin escribir un campo aparte. ¿Qué usas?",
  cod="""using System;

class Alumno {
    public string Nombre { get; set; }
    public int Nota { get; set; } = 5;      // valor inicial
}

class Program {
    static void Main() {
        var a = new Alumno { Nombre = "Ana" };
        Console.WriteLine(a.Nombre + " " + a.Nota);
    }
}""",
  out="Ana 5",
  h="crea un alumno con propiedades automáticas",
  pr=("Una propiedad automática se escribe { get; ___; }. (set)", "set"),
  ec="olvidar que una propiedad automática también necesita acceso public"),
K("static",
  d="miembro que pertenece a la clase y no a cada objeto",
  u="compartir datos o utilidades sin crear objetos",
  mas="Un campo static existe una sola vez y lo comparten todos los objetos. Se accede con NombreClase.miembro.",
  k=["static pertenece a la clase.", "Se comparte entre todos los objetos.", "Se accede con NombreClase.miembro."],
  sit="Quieres contar cuántos objetos se han creado en total. ¿Qué usas?",
  cod="""using System;

class Contador {
    public static int total = 0;           // compartido
    public Contador() { total++; }
}

class Program {
    static void Main() {
        new Contador(); new Contador(); new Contador();
        Console.WriteLine(Contador.total);
    }
}""",
  out="3",
  h="cuenta cuántos objetos se crearon",
  pr=("Un campo compartido por todos los objetos es ___. (static)", "static"),
  ec="usar un campo static esperando que cada objeto tenga el suyo"),
K("Herencia",
  d="mecanismo por el que una clase hereda de otra con dos puntos",
  u="reutilizar código entre clases relacionadas",
  mas="class Hija : Padre hereda campos y métodos no privados. C# solo permite heredar de una clase.",
  k=["Los dos puntos crean una clase hija.", "La hija hereda miembros del padre.", "C# solo permite una clase padre."],
  sit="Perro y Gato comparten comportamiento de Animal. ¿Qué usas para no repetirlo?",
  cod="""using System;

class Animal {
    public void Respirar() { Console.WriteLine("respira"); }
}
class Perro : Animal {                   // hereda de Animal
    public void Ladrar() { Console.WriteLine("guau"); }
}

class Program {
    static void Main() {
        var p = new Perro();
        p.Respirar();
        p.Ladrar();
    }
}""",
  out="respira\nguau",
  h="un perro usa un método heredado y uno propio",
  pr=("La herencia en C# se escribe con el signo ___. (:)", ":"),
  ec="intentar heredar de dos clases a la vez"),
K("base",
  d="palabra que se refiere a la clase padre",
  u="reutilizar el constructor o los métodos del padre",
  mas="base(...) llama al constructor del padre y se escribe tras los dos puntos del constructor de la hija. base.Metodo() ejecuta la versión del padre.",
  k=["base llama al constructor del padre.", "Se escribe tras los dos puntos del constructor.", "base.Metodo() usa la versión del padre."],
  sit="Una clase hija necesita ejecutar la inicialización de su padre. ¿Qué usas?",
  cod="""using System;

class Persona {
    public string nombre;
    public Persona(string nombre) { this.nombre = nombre; }
}
class Alumno : Persona {
    public Alumno(string nombre) : base(nombre) { }   // llama al padre
}

class Program {
    static void Main() {
        Console.WriteLine(new Alumno("Ana").nombre);
    }
}""",
  out="Ana",
  h="inicializa el nombre con el constructor del padre",
  pr=("La palabra que se refiere a la clase padre es ___. (base)", "base"),
  ec="olvidar llamar al constructor del padre cuando este exige parámetros"),
K("virtual y override",
  d="palabras que permiten que una clase hija reemplace un método del padre",
  u="lograr comportamiento polimórfico",
  mas="El padre marca el método virtual y la hija lo reemplaza con override. Sin virtual no se puede reemplazar. new oculta el método en lugar de reemplazarlo.",
  k=["virtual permite que un método sea reemplazado.", "override reemplaza el método del padre.", "Sin virtual no se puede usar override."],
  sit="Quieres que cada animal haga su propio sonido reemplazando el método del padre. ¿Qué usas?",
  cod="""using System;

class Animal {
    public virtual void Hablar() { Console.WriteLine("..."); }
}
class Perro : Animal {
    public override void Hablar() { Console.WriteLine("guau"); }   // reemplaza
}

class Program {
    static void Main() {
        Animal a = new Perro();
        a.Hablar();
    }
}""",
  out="guau",
  h="una clase hija reemplaza el método del padre",
  pr=("La palabra de la hija que reemplaza un método virtual es ___. (override)", "override"),
  ec="olvidar virtual en el método del padre"),
K("Polimorfismo",
  d="capacidad de objetos distintos de responder al mismo método a su manera",
  u="tratar objetos distintos de forma uniforme",
  mas="Una variable del tipo padre puede guardar un objeto hijo. Al llamar a un método virtual, C# ejecuta la versión del objeto real.",
  k=["El polimorfismo permite que cada clase responda a su manera.", "Una variable padre puede guardar un objeto hijo.", "C# ejecuta la versión del objeto real."],
  sit="Tienes una lista de animales distintos y quieres que cada uno haga su sonido con la misma llamada. ¿Qué aprovechas?",
  cod="""using System;

class Animal { public virtual string Hablar() { return "..."; } }
class Perro : Animal { public override string Hablar() { return "guau"; } }
class Gato : Animal { public override string Hablar() { return "miau"; } }

class Program {
    static void Main() {
        Animal[] zoo = { new Perro(), new Gato() };
        foreach (var a in zoo) Console.WriteLine(a.Hablar());
    }
}""",
  out="guau\nmiau",
  h="cada animal responde con su propio sonido",
  pr=("Que objetos distintos respondan al mismo método a su manera es ___. (polimorfismo)", "polimorfismo"),
  ec="usar muchos if para distinguir clases en lugar de polimorfismo"),
K("Clases abstractas",
  d="clases que no se pueden instanciar y pueden tener métodos sin cuerpo",
  u="definir una base común que obliga a las hijas a completar métodos",
  mas="Se declaran con abstract. Un método abstract no tiene cuerpo y cada hija debe implementarlo con override. No se puede hacer new de una clase abstracta.",
  k=["Una clase abstracta no se puede instanciar.", "Un método abstract no tiene cuerpo.", "Las hijas deben implementarlo con override."],
  sit="Quieres obligar a toda figura a calcular su área y no crear nunca una «figura» genérica. ¿Qué usas?",
  cod="""using System;

abstract class Figura {
    public abstract int Area();                   // sin cuerpo
}
class Cuadrado : Figura {
    int lado;
    public Cuadrado(int lado) { this.lado = lado; }
    public override int Area() { return lado * lado; }
}

class Program {
    static void Main() {
        Console.WriteLine(new Cuadrado(3).Area());
    }
}""",
  out="9",
  h="calcula el área de un cuadrado desde una clase abstracta",
  pr=("La palabra que marca una clase como no instanciable es ___. (abstract)", "abstract"),
  ec="intentar crear un objeto de una clase abstracta"),
K("Interfaces",
  d="contrato que define miembros que una clase debe implementar",
  u="exigir un comportamiento sin imponer una herencia",
  mas="Una interface declara miembros sin cuerpo y su nombre empieza por I por convención. Una clase la cumple con los dos puntos y puede implementar varias interfaces.",
  k=["Una interface define un contrato.", "Su nombre empieza por I por convención.", "Una clase puede implementar varias interfaces."],
  sit="Quieres asegurar que la clase Pato tenga el método Volar sin obligar a una herencia. ¿Qué usas?",
  cod="""using System;

interface IVolador {
    void Volar();
}
class Pato : IVolador {                         // cumple el contrato
    public void Volar() { Console.WriteLine("El pato vuela"); }
}

class Program {
    static void Main() {
        IVolador v = new Pato();
        v.Volar();
    }
}""",
  out="El pato vuela",
  h="un pato cumple la interfaz IVolador",
  pr=("Una interfaz por convención empieza con la letra ___. (I)", "i"),
  ec="olvidar implementar un miembro de la interfaz"),
K("is y as",
  d="operadores que comprueban o convierten el tipo de un objeto",
  u="saber de qué clase es un objeto y usarlo como tal",
  mas="x is Tipo devuelve bool. Con patrón, x is Perro p comprueba y crea la variable p a la vez. as convierte y devuelve null si no es posible.",
  k=["is comprueba el tipo de un objeto.", "is permite declarar una variable con el patrón.", "as convierte o devuelve null."],
  sit="Recibes un objeto y debes saber si es un Perro antes de pedirle que ladre. ¿Qué usas?",
  cod="""using System;

class Animal { }
class Perro : Animal { public void Ladrar() { Console.WriteLine("guau"); } }

class Program {
    static void Main() {
        Animal a = new Perro();
        if (a is Perro p) {            // comprueba y convierte
            p.Ladrar();
        }
    }
}""",
  out="guau",
  h="comprueba que es un perro antes de ladrar",
  pr=("El operador que comprueba el tipo de un objeto es ___. (is)", "is"),
  ec="convertir un objeto con un cast sin comprobar su tipo"),
K("ToString",
  d="método que devuelve la representación en texto de un objeto",
  u="mostrar un objeto de forma legible",
  mas="Todas las clases heredan ToString de object. Si lo reemplazas con override, WriteLine y la interpolación usan tu versión. Sin él se muestra el nombre de la clase.",
  k=["ToString devuelve el objeto como texto.", "WriteLine usa ToString automáticamente.", "Sin reemplazarlo se muestra el nombre de la clase."],
  sit="Al imprimir un objeto sale el nombre de la clase en vez de sus datos. ¿Qué reemplazas?",
  cod="""using System;

class Punto {
    public int x = 1, y = 2;
    public override string ToString() { return "(" + x + ", " + y + ")"; }
}

class Program {
    static void Main() {
        Console.WriteLine(new Punto());
    }
}""",
  out="(1, 2)",
  h="muestra un objeto con una representación legible",
  pr=("El método que convierte un objeto en texto es ___. (ToString)", "tostring"),
  ec="no reemplazar ToString y mostrar solo el nombre de la clase"),
K("enum",
  d="tipo con un conjunto fijo de constantes con nombre",
  u="representar opciones o estados limitados",
  mas="Se declara con enum y sus valores en PascalCase. Internamente son enteros que empiezan en 0. Se pueden usar en un switch.",
  k=["enum define un conjunto fijo de constantes.", "Los valores son enteros que empiezan en 0.", "Se puede usar en un switch."],
  sit="Tu programa usa los estados «pendiente», «activo» y «cerrado». ¿Qué usas para representarlos?",
  cod="""using System;

enum Estado { Pendiente, Activo, Cerrado }

class Program {
    static void Main() {
        Estado e = Estado.Activo;
        Console.WriteLine(e);
        Console.WriteLine((int)e);        // 1
    }
}""",
  out="Activo\n1",
  h="usa una enumeración de estados",
  pr=("El tipo de constantes con nombre es ___. (enum)", "enum"),
  ec="usar números sueltos en lugar de un enum"),
K("Composición",
  d="clase que contiene objetos de otras clases como campos",
  u="construir objetos complejos a partir de partes",
  mas="Se usa cuando un objeto «tiene un» otro (un coche tiene un motor). Suele ser preferible a la herencia cuando no hay relación «es un».",
  k=["La composición usa objetos como campos.", "Expresa la relación «tiene un».", "Suele preferirse a la herencia cuando no hay «es un»."],
  sit="Un coche tiene un motor, pero no es un motor. ¿Qué relación usas?",
  cod="""using System;

class Motor { public int cv = 90; }
class Coche {
    public Motor motor = new Motor();     // un coche TIENE un motor
}

class Program {
    static void Main() {
        Console.WriteLine(new Coche().motor.cv);
    }
}""",
  out="90",
  h="un coche contiene un objeto motor",
  pr=("La relación «tiene un» se logra por ___. (composición)", "composicion", "composición"),
  ec="usar herencia donde la relación es «tiene un»"),
K("record",
  d="tipo compacto para guardar datos con igualdad por valor",
  u="crear clases de datos con muy poco código",
  mas="record Punto(int X, int Y); genera propiedades, constructor, ToString y comparación por valor. Dos records con los mismos datos son iguales.",
  k=["Un record es un tipo compacto de datos.", "Genera propiedades y ToString automáticamente.", "Dos records con los mismos datos son iguales."],
  sit="Necesitas un tipo solo para guardar dos valores y compararlo por su contenido. ¿Qué usas?",
  cod="""using System;

record Punto(int X, int Y);

class Program {
    static void Main() {
        var a = new Punto(3, 4);
        var b = new Punto(3, 4);
        Console.WriteLine(a.X + " " + a.Y);
        Console.WriteLine(a == b);            // True: igualdad por valor
    }
}""",
  out="3 4\nTrue",
  h="crea dos puntos con un record y los compara",
  pr=("El tipo compacto de datos con igualdad por valor es un ___. (record)", "record"),
  ec="esperar que dos records distintos se comparen por referencia"),
K("struct",
  d="tipo de valor ligero que se copia al asignarse",
  u="representar datos pequeños sin crear objetos en el montón",
  mas="Un struct es un tipo de valor: al asignarlo se copia. Una clase es de referencia: dos variables apuntan al mismo objeto. Se usa para datos pequeños e inmutables.",
  k=["Un struct es un tipo de valor.", "Al asignarlo se copia.", "Se usa para datos pequeños."],
  sit="Necesitas un tipo muy pequeño que se copie al asignarlo en lugar de compartirse. ¿Qué usas?",
  cod="""using System;

struct Punto { public int X; }

class Program {
    static void Main() {
        Punto a = new Punto { X = 1 };
        Punto b = a;                    // se copia
        b.X = 99;
        Console.WriteLine(a.X);         // 1: a no cambió
    }
}""",
  out="1",
  h="copia un struct y comprueba que el original no cambia",
  pr=("Un struct es un tipo de ___. (valor)", "valor"),
  ec="creer que cambiar la copia de un struct modifica el original"),
]
