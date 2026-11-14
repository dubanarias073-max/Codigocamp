"""C# · Etapa 4: Excepciones, genéricos, LINQ y delegados."""
from ..generador import K

LISTA = [
K("try y catch",
  d="estructura que captura errores sin detener el programa",
  u="manejar fallos de forma controlada",
  mas="El código que puede fallar va en try. Si lanza una excepción, la ejecución salta al catch donde se puede mostrar un mensaje o recuperar. El programa continúa después.",
  k=["try contiene el código que puede fallar.", "catch recibe y maneja la excepción.", "El programa continúa después del catch."],
  sit="Una división puede fallar y no quieres que se caiga todo el programa. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        try {
            int cero = 0;
            int x = 10 / cero;                   // DivideByZeroException
        } catch (DivideByZeroException) {
            Console.WriteLine("No se puede dividir entre cero");
        }
        Console.WriteLine("El programa continúa");
    }
}""",
  out="No se puede dividir entre cero\nEl programa continúa",
  h="captura una división entre cero y sigue ejecutando",
  pr=("El bloque que recibe la excepción es ___. (catch)", "catch"),
  ec="dejar el catch vacío y esconder los errores"),
K("Varios catch",
  d="varios bloques catch para distintos tipos de excepción",
  u="reaccionar de forma distinta según el error",
  mas="Cada catch maneja un tipo. Se evalúan en orden, así que los más específicos van primero y Exception, al final. También se puede filtrar con when.",
  k=["Se pueden escribir varios catch.", "Los más específicos van primero.", "Exception va al final por ser el más general."],
  sit="Un mismo código puede fallar por texto inválido o por otra causa y quieres tratarlos distinto. ¿Qué haces?",
  cod="""using System;

class Program {
    static void Main() {
        try {
            int.Parse("abc");
        } catch (FormatException) {
            Console.WriteLine("No es un número");
        } catch (Exception) {
            Console.WriteLine("Otro error");
        }
    }
}""",
  out="No es un número",
  h="trata distinto un texto que no es número",
  pr=("Varios tipos de error se tratan con varios bloques ___. (catch)", "catch"),
  ec="poner el catch general antes que los específicos"),
K("finally",
  d="bloque que se ejecuta siempre, haya o no excepción",
  u="liberar recursos pase lo que pase",
  mas="finally se ejecuta después de try y catch, incluso si hubo un return o una excepción. Se usa para cerrar archivos o conexiones.",
  k=["finally se ejecuta siempre.", "Se ejecuta aunque haya excepción.", "Se usa para liberar recursos."],
  sit="Quieres que un mensaje de limpieza se muestre siempre, falle o no el código. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        try {
            Console.WriteLine("Intentando");
        } finally {
            Console.WriteLine("Esto se ejecuta siempre");
        }
    }
}""",
  out="Intentando\nEsto se ejecuta siempre",
  h="muestra un mensaje que se ejecuta siempre",
  pr=("El bloque que se ejecuta siempre es ___. (finally)", "finally"),
  ec="creer que finally solo se ejecuta si hay error"),
K("throw",
  d="instrucción que lanza una excepción a propósito",
  u="avisar de que algo salió mal",
  mas="throw new TipoDeExcepcion(\"mensaje\") crea y lanza el error. El método termina y la excepción sube hasta que alguien la capture. Message da el mensaje.",
  k=["throw lanza una excepción.", "El método termina al lanzarla.", "Message contiene el mensaje del error."],
  sit="Un método recibe una edad negativa y debe avisar del error. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Validar(int edad) {
        if (edad < 0) throw new ArgumentException("edad negativa");
    }

    static void Main() {
        try {
            Validar(-5);
        } catch (ArgumentException e) {
            Console.WriteLine(e.Message);
        }
    }
}""",
  out="edad negativa",
  h="lanza una excepción por una edad negativa y la captura",
  pr=("La palabra que lanza una excepción es ___. (throw)", "throw"),
  ec="lanzar un tipo de excepción que no describe el error"),
K("Excepciones propias",
  d="clases que heredan de Exception para errores del programa",
  u="distinguir tus errores de los demás",
  mas="Se crea una clase que hereda de Exception y llama a base(mensaje). Permite capturar tu error por separado.",
  k=["Una excepción propia hereda de Exception.", "Llama a base(mensaje) en su constructor.", "Permite capturar tu error por separado."],
  sit="Quieres un error propio «SaldoInsuficiente» que se pueda capturar por separado. ¿Qué haces?",
  cod="""using System;

class SaldoInsuficienteException : Exception {
    public SaldoInsuficienteException(string msg) : base(msg) { }
}

class Program {
    static void Main() {
        try {
            throw new SaldoInsuficienteException("saldo insuficiente");
        } catch (SaldoInsuficienteException e) {
            Console.WriteLine(e.Message);
        }
    }
}""",
  out="saldo insuficiente",
  h="lanza y captura una excepción propia",
  pr=("Una excepción propia hereda de ___. (Exception)", "exception"),
  ec="crear excepciones que no heredan de Exception"),
K("using",
  d="instrucción que libera un recurso automáticamente al terminar el bloque",
  u="evitar olvidar cerrar archivos o conexiones",
  mas="Los recursos que implementan IDisposable se declaran con using. Al salir del bloque se llama a Dispose(), incluso si hay error.",
  k=["using libera el recurso automáticamente.", "El recurso implementa IDisposable.", "Dispose() se llama aunque haya error."],
  sit="Quieres que un recurso se cierre siempre sin escribir un finally. ¿Qué usas?",
  cod="""using System;

class Recurso : IDisposable {
    public Recurso() { Console.WriteLine("abrir"); }
    public void Dispose() { Console.WriteLine("cerrar"); }
}

class Program {
    static void Main() {
        using (var r = new Recurso()) {      // se cierra solo
            Console.WriteLine("usando");
        }
    }
}""",
  out="abrir\nusando\ncerrar",
  h="abre, usa y cierra un recurso automáticamente",
  pr=("La interfaz que permite liberar recursos es ___. (IDisposable)", "idisposable"),
  ec="olvidar liberar un recurso que no está en un using"),
K("Clases genéricas",
  d="clases que dependen de un tipo parámetro como <T>",
  u="crear estructuras reutilizables para cualquier tipo",
  mas="class Caja<T> guarda un valor de tipo T. Al usarla se indica el tipo: Caja<string>. El compilador comprueba que no mezcles tipos.",
  k=["Una clase genérica recibe un tipo parámetro.", "Se usa como Caja<string>.", "El compilador evita mezclar tipos."],
  sit="Quieres una «caja» que guarde un valor de cualquier tipo con seguridad. ¿Qué defines?",
  cod="""using System;

class Caja<T> {
    private T valor;
    public Caja(T valor) { this.valor = valor; }
    public T Ver() { return valor; }
}

class Program {
    static void Main() {
        var a = new Caja<string>("hola");
        var b = new Caja<int>(42);
        Console.WriteLine(a.Ver() + " " + b.Ver());
    }
}""",
  out="hola 42",
  h="crea cajas de texto y de entero con la misma clase",
  pr=("Una clase genérica usa un tipo parámetro como ___. (<T>)", "<t>", "t"),
  ec="usar object y perder la seguridad de tipos"),
K("Métodos genéricos",
  d="métodos con parámetros de tipo propios",
  u="operar sobre varios tipos con un solo método",
  mas="Se escribe <T> después del nombre: static T Primero<T>(List<T> l). C# deduce T a partir de los argumentos.",
  k=["Un método genérico declara <T> tras su nombre.", "C# deduce T de los argumentos.", "Un solo método sirve para muchos tipos."],
  sit="Quieres un método que devuelva el primer elemento de cualquier lista. ¿Qué escribes?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static T Primero<T>(List<T> lista) {
        return lista[0];
    }

    static void Main() {
        Console.WriteLine(Primero(new List<int> {10, 20}));
        Console.WriteLine(Primero(new List<string> {"a", "b"}));
    }
}""",
  out="10\na",
  h="obtiene el primer elemento de listas de distintos tipos",
  pr=("En un método genérico, <T> se escribe después del ___ del método. (nombre)", "nombre"),
  ec="olvidar declarar <T> después del nombre del método"),
K("Restricciones where",
  d="límites que obligan a que el tipo genérico cumpla cierta condición",
  u="usar miembros concretos dentro de un método genérico",
  mas="where T : IComparable<T> exige que T pueda compararse. Así dentro del método puedes llamar a CompareTo con seguridad. Otras restricciones: class, struct, new().",
  k=["where restringe los tipos que acepta un genérico.", "Permite usar miembros del tipo restringido.", "Un tipo que no cumple la restricción da error."],
  sit="Tu método genérico necesita comparar dos valores, así que solo debe aceptar tipos comparables. ¿Qué agregas?",
  cod="""using System;

class Program {
    static T Mayor<T>(T a, T b) where T : IComparable<T> {   // exige comparables
        return a.CompareTo(b) >= 0 ? a : b;
    }

    static void Main() {
        Console.WriteLine(Mayor(3, 7));
        Console.WriteLine(Mayor("a", "b"));
    }
}""",
  out="7\nb",
  h="devuelve el mayor de dos valores comparables",
  pr=("La cláusula que restringe un genérico es ___. (where)", "where"),
  ec="llamar a un método con un tipo que no cumple la restricción"),
K("HashSet",
  d="colección de elementos únicos",
  u="eliminar repetidos y comprobar pertenencia rápidamente",
  mas="Un HashSet no admite repetidos: Add devuelve false si el elemento ya estaba. Contains comprueba si existe rápidamente.",
  k=["Un HashSet no admite elementos repetidos.", "Add devuelve false si ya existía.", "Contains comprueba rápidamente si existe."],
  sit="Tienes una lista con repetidos y quieres quedarte con cada valor una sola vez. ¿Qué usas?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        var s = new HashSet<int>();
        s.Add(1); s.Add(2);
        Console.WriteLine(s.Add(2));       // False: ya estaba
        Console.WriteLine(s.Count);        // 2
    }
}""",
  out="False\n2",
  h="intenta añadir un repetido a un conjunto",
  pr=("La colección de elementos únicos es ___. (HashSet)", "hashset"),
  ec="esperar que un HashSet conserve el orden de inserción"),
K("Recorrer un Dictionary",
  d="forma de visitar las claves y valores de un diccionario",
  u="procesar todos los pares clave-valor",
  mas="foreach sobre el diccionario da KeyValuePair con Key y Value. Keys y Values dan solo las claves o solo los valores. SortedDictionary las mantiene ordenadas.",
  k=["foreach da pares con Key y Value.", "Keys da solo las claves.", "SortedDictionary mantiene las claves ordenadas."],
  sit="Quieres mostrar cada nombre junto con su edad guardados en un diccionario. ¿Qué usas?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        var m = new SortedDictionary<string, int>();   // ordenado por clave
        m["Luis"] = 25; m["Ana"] = 20;
        foreach (var par in m) {
            Console.WriteLine(par.Key + "=" + par.Value);
        }
    }
}""",
  out="Ana=20\nLuis=25",
  h="recorre un diccionario mostrando clave y valor",
  pr=("La propiedad que da la clave de un par es ___. (Key)", "key"),
  ec="suponer un orden en un Dictionary normal"),
K("Lambdas",
  d="funciones anónimas que se escriben con =>",
  u="pasar comportamiento corto a un método",
  mas="Se escriben como (parámetros) => expresión. Se usan con métodos que reciben funciones, como Sort, Where o Select.",
  k=["Una lambda es una función anónima.", "Se escribe con la flecha =>.", "Se usa con métodos que reciben funciones."],
  sit="Quieres pasar una acción corta a un método sin crear una función aparte. ¿Qué usas?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        var l = new List<string> {"Carlos", "Ana", "Luis"};
        l.Sort((a, b) => a.Length - b.Length);       // lambda como criterio
        Console.WriteLine(string.Join(", ", l));
    }
}""",
  out="Ana, Luis, Carlos",
  h="ordena nombres por longitud con una lambda",
  pr=("El símbolo de una lambda es ___. (=>)", "=>"),
  ec="confundir => de lambda con >= de comparación"),
K("Func y Action",
  d="tipos genéricos para guardar funciones con o sin resultado",
  u="guardar una función en una variable o pasarla como argumento",
  mas="Func<int, int> recibe un int y devuelve un int; el último tipo es siempre el retorno. Action no devuelve nada.",
  k=["Func guarda una función que devuelve un valor.", "El último tipo de Func es el retorno.", "Action guarda una función sin retorno."],
  sit="Quieres guardar una función que duplica un número en una variable. ¿Qué tipo usas?",
  cod="""using System;

class Program {
    static void Main() {
        Func<int, int> doble = n => n * 2;
        Action<string> saludar = s => Console.WriteLine("Hola " + s);
        Console.WriteLine(doble(21));
        saludar("Ana");
    }
}""",
  out="42\nHola Ana",
  h="guarda una función con Func y otra con Action",
  pr=("El tipo que guarda una función sin retorno es ___. (Action)", "action"),
  ec="olvidar que el último tipo de Func es el del retorno"),
K("LINQ Where",
  d="método que filtra los elementos que cumplen una condición",
  u="quedarte con parte de una colección",
  mas="Se usa con using System.Linq;. Where recibe una lambda y devuelve los elementos para los que es true. No modifica la colección original.",
  k=["Where filtra los elementos que cumplen una condición.", "Requiere using System.Linq.", "No modifica la colección original."],
  sit="Quieres quedarte solo con los números pares de una lista. ¿Qué usas?",
  cod="""using System;
using System.Linq;

class Program {
    static void Main() {
        int[] v = {1, 2, 3, 4, 5, 6};
        var pares = v.Where(n => n % 2 == 0);       // 2, 4, 6
        Console.WriteLine(string.Join(", ", pares));
    }
}""",
  out="2, 4, 6",
  h="filtra los números pares de un array",
  pr=("El método LINQ que filtra es ___. (Where)", "where"),
  ec="olvidar using System.Linq"),
K("LINQ Select",
  d="método que transforma cada elemento de una colección",
  u="obtener una nueva colección a partir de otra",
  mas="Select aplica una función a cada elemento y devuelve los resultados. Se puede encadenar con Where.",
  k=["Select transforma cada elemento.", "Devuelve una colección nueva.", "Se puede encadenar con Where."],
  sit="Quieres elevar al cuadrado cada número de una lista. ¿Qué usas?",
  cod="""using System;
using System.Linq;

class Program {
    static void Main() {
        int[] v = {1, 2, 3};
        var cuadrados = v.Select(n => n * n);       // 1, 4, 9
        Console.WriteLine(string.Join(", ", cuadrados));
    }
}""",
  out="1, 4, 9",
  h="eleva al cuadrado cada número de un array",
  pr=("El método LINQ que transforma cada elemento es ___. (Select)", "select"),
  ec="confundir Select con Where"),
K("LINQ OrderBy",
  d="método que ordena una colección por un criterio",
  u="obtener los elementos en un orden concreto",
  mas="OrderBy ordena de menor a mayor por la clave que indica la lambda; OrderByDescending de mayor a menor. Devuelve una colección nueva.",
  k=["OrderBy ordena por un criterio.", "OrderByDescending ordena de mayor a menor.", "Devuelve una colección nueva."],
  sit="Quieres ordenar nombres por su longitud sin modificar la lista original. ¿Qué usas?",
  cod="""using System;
using System.Linq;

class Program {
    static void Main() {
        string[] n = {"Carlos", "Ana", "Luis"};
        var ord = n.OrderBy(s => s.Length);         // por longitud
        Console.WriteLine(string.Join(", ", ord));
    }
}""",
  out="Ana, Luis, Carlos",
  h="ordena nombres por su longitud",
  pr=("El método LINQ que ordena es ___. (OrderBy)", "orderby"),
  ec="creer que OrderBy modifica la colección original"),
K("Sum, Count y Max",
  d="métodos de LINQ que resumen una colección en un valor",
  u="calcular totales, cantidades y extremos",
  mas="Sum suma, Count cuenta (opcionalmente con condición), Max y Min dan los extremos y Average el promedio.",
  k=["Sum suma los elementos.", "Count cuenta los elementos.", "Max devuelve el mayor."],
  sit="Quieres sumar las notas y saber cuántas son mayores de 7. ¿Qué usas?",
  cod="""using System;
using System.Linq;

class Program {
    static void Main() {
        int[] notas = {7, 9, 8, 5};
        Console.WriteLine(notas.Sum());                   // 29
        Console.WriteLine(notas.Count(n => n > 7));       // 2
        Console.WriteLine(notas.Max());                   // 9
    }
}""",
  out="29\n2\n9",
  h="suma, cuenta y halla el máximo de unas notas",
  pr=("El método que suma los elementos es ___. (Sum)", "sum"),
  ec="usar Count() cuando se quería la suma"),
K("Tipos nulables",
  d="tipos de valor que pueden valer null, escritos con ?",
  u="representar datos que pueden faltar",
  mas="int? guarda un entero o null. HasValue indica si hay valor, Value lo obtiene y ?? da un valor por defecto.",
  k=["int? puede guardar un entero o null.", "HasValue indica si hay valor.", "?? da un valor por defecto."],
  sit="Una edad puede no estar disponible y no quieres usar -1 como señal. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int? edad = null;
        Console.WriteLine(edad.HasValue);       // False
        Console.WriteLine(edad ?? 18);          // 18: valor por defecto
    }
}""",
  out="False\n18",
  h="usa un entero que puede ser null con un valor por defecto",
  pr=("Un tipo que puede valer null se escribe con el signo ___. (?)", "?"),
  ec="usar Value sobre un nulable que vale null"),
K("Delegados y eventos",
  d="tipos que representan referencias a métodos y notificaciones entre objetos",
  u="avisar a otras partes del programa cuando ocurre algo",
  mas="Un evento se declara con event y se dispara con ?.Invoke(). Quienes quieran enterarse se suscriben con +=.",
  k=["Un evento avisa cuando ocurre algo.", "Se suscribe con +=.", "Se dispara con Invoke."],
  sit="Quieres que otras clases se enteren cuando termina una descarga sin que la clase conozca a todas. ¿Qué usas?",
  cod="""using System;

class Descarga {
    public event Action Terminada;                  // evento
    public void Iniciar() { Terminada?.Invoke(); }  // lo dispara
}

class Program {
    static void Main() {
        var d = new Descarga();
        d.Terminada += () => Console.WriteLine("Descarga terminada");   // suscripción
        d.Iniciar();
    }
}""",
  out="Descarga terminada",
  h="se suscribe a un evento y lo dispara",
  pr=("La palabra que declara un evento es ___. (event)", "event"),
  ec="disparar un evento sin comprobar si hay suscriptores"),
K("yield return",
  d="instrucción que produce una secuencia de valores uno a uno",
  u="generar secuencias sin construir una lista completa",
  mas="Un método con yield return devuelve IEnumerable<T> y produce cada valor cuando se pide. Es útil para secuencias largas o infinitas.",
  k=["yield return produce valores uno a uno.", "El método devuelve IEnumerable<T>.", "Evita construir una lista completa."],
  sit="Quieres generar los cuadrados del 1 al 4 sin armar una lista. ¿Qué usas?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static IEnumerable<int> Cuadrados(int n) {
        for (int i = 1; i <= n; i++) yield return i * i;   // uno a uno
    }

    static void Main() {
        foreach (var c in Cuadrados(4)) Console.Write(c + " ");
        Console.WriteLine();
    }
}""",
  out="1 4 9 16 ",
  h="genera los cuadrados del 1 al 4 con yield return",
  pr=("La instrucción que produce valores uno a uno es yield ___. (return)", "return"),
  ec="olvidar que un método con yield devuelve IEnumerable"),
]
