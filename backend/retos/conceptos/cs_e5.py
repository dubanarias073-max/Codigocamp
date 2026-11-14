"""C# · Etapa 5: C# moderno y profesional."""
from ..generador import K

LISTA = [
K("Espacios de nombres",
  d="bloques namespace que agrupan clases relacionadas",
  u="organizar el código y evitar choques de nombres",
  mas="namespace MiApp.Modelos { ... } agrupa tipos. Se accede con el nombre completo o con using. En C# moderno puede escribirse en una línea: namespace MiApp;.",
  k=["namespace agrupa clases relacionadas.", "Evita choques de nombres.", "using permite omitir el nombre completo."],
  sit="Tu proyecto tiene dos clases llamadas Usuario en módulos distintos. ¿Qué evita el conflicto?",
  cod="""using System;

namespace Tienda {
    class Producto { public string Nombre = "Libro"; }
}

class Program {
    static void Main() {
        var p = new Tienda.Producto();      // nombre completo con el namespace
        Console.WriteLine(p.Nombre);
    }
}""",
  out="Libro",
  h="usa una clase de un espacio de nombres propio",
  pr=("La palabra que agrupa clases en un espacio de nombres es ___. (namespace)", "namespace"),
  ec="olvidar el using o el nombre completo del namespace"),
K("Operadores ?. y ??",
  d="operadores para acceder a miembros que pueden ser null y dar valores por defecto",
  u="evitar NullReferenceException",
  mas="?. detiene la cadena y devuelve null si el objeto es null. ?? da un valor alternativo cuando la izquierda es null. ??= asigna solo si es null.",
  k=["?. evita errores al acceder a algo que puede ser null.", "?? da un valor si la izquierda es null.", "??= asigna solo si la variable es null."],
  sit="Quieres leer la longitud de un texto que quizá sea null y usar 0 si falta. ¿Qué operadores usas?",
  cod="""using System;

class Program {
    static void Main() {
        string s = null;
        Console.WriteLine(s?.Length ?? 0);     // 0: no falla
        s = "hola";
        Console.WriteLine(s?.Length ?? 0);     // 4
    }
}""",
  out="0\n4",
  h="lee la longitud de un texto que puede ser null",
  pr=("El operador que accede de forma segura a un miembro es ?___. (.)", ".", "?."),
  ec="acceder a un miembro de un objeto null sin comprobarlo"),
K("Tuplas",
  d="agrupación ligera de varios valores sin crear una clase",
  u="devolver o guardar varios datos a la vez",
  mas="Se escriben entre paréntesis: (string, int) par = (\"Ana\", 20). Los elementos pueden tener nombre y se pueden deconstruir en variables.",
  k=["Una tupla agrupa varios valores.", "Sus elementos pueden tener nombre.", "Se pueden deconstruir en variables."],
  sit="Un método debe devolver un nombre y una edad a la vez sin crear una clase. ¿Qué usas?",
  cod="""using System;

class Program {
    static (string, int) Persona() { return ("Ana", 20); }

    static void Main() {
        var (nombre, edad) = Persona();          // deconstrucción
        Console.WriteLine(nombre + " " + edad);
    }
}""",
  out="Ana 20",
  h="devuelve dos valores en una tupla y los deconstruye",
  pr=("Una tupla se escribe entre ___. (paréntesis)", "parentesis", "paréntesis"),
  ec="olvidar el orden de los elementos de la tupla"),
K("Expresión switch",
  d="switch que devuelve un valor con flechas =>",
  u="elegir un valor según un caso sin break",
  mas="Se escribe valor switch { caso => resultado, _ => porDefecto }. El guion bajo cubre el resto. Es más corto que el switch clásico.",
  k=["La expresión switch devuelve un valor.", "Usa flechas => y no necesita break.", "El guion bajo _ cubre los demás casos."],
  sit="Quieres asignar el nombre de un día según su número sin escribir break. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int dia = 2;
        string nombre = dia switch {
            1 => "Lunes",
            2 => "Martes",
            _ => "Otro"
        };
        Console.WriteLine(nombre);
    }
}""",
  out="Martes",
  h="asigna el nombre de un día con una expresión switch",
  pr=("El caso por defecto de una expresión switch es el guion ___. (bajo)", "bajo", "_"),
  ec="olvidar el caso por defecto con _"),
K("Pattern matching",
  d="forma de comprobar el tipo y las propiedades de un valor con patrones",
  u="escribir condiciones más expresivas",
  mas="Con is y patrones se pueden comprobar tipos, rangos (>= 18) y combinaciones con and, or y not. También se usa dentro de switch.",
  k=["Pattern matching comprueba tipos y valores con patrones.", "Se combina con and, or y not.", "Se usa con is y con switch."],
  sit="Quieres comprobar si un número está entre 1 y 10 de forma legible. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int n = 5;
        Console.WriteLine(n is >= 1 and <= 10);     // True
        object o = "hola";
        Console.WriteLine(o is string s && s.Length == 4);   // True
    }
}""",
  out="True\nTrue",
  h="comprueba un rango y un tipo con patrones",
  pr=("En un patrón, la palabra para combinar condiciones es ___. (and)", "and"),
  ec="usar && dentro de un patrón en lugar de and"),
K("async y await",
  d="sintaxis para escribir código asíncrono que se lee como secuencial",
  u="esperar resultados largos sin bloquear el programa",
  mas="Un método async devuelve Task o Task<T>. Dentro, await espera a que termine otra tarea sin bloquear el hilo. Main también puede ser async Task.",
  k=["async marca un método asíncrono.", "await espera una tarea sin bloquear.", "Un método async devuelve Task."],
  sit="Necesitas esperar una operación lenta sin congelar el programa. ¿Qué usas?",
  cod="""using System;
using System.Threading.Tasks;

class Program {
    static async Task<int> Calcular() {
        await Task.Delay(10);               // simula una espera
        return 42;
    }

    static async Task Main() {
        int r = await Calcular();            // espera sin bloquear
        Console.WriteLine(r);
    }
}""",
  out="42",
  h="espera un resultado asíncrono y lo muestra",
  pr=("La palabra que espera una tarea asíncrona es ___. (await)", "await"),
  ec="usar await en un método que no es async"),
K("Task.Run",
  d="método que ejecuta trabajo en otro hilo del grupo de hilos",
  u="hacer cálculos pesados sin bloquear el hilo principal",
  mas="Task.Run(() => ...) ejecuta la función en segundo plano y devuelve una Task. Con await se obtiene su resultado.",
  k=["Task.Run ejecuta trabajo en segundo plano.", "Devuelve una Task.", "Con await se obtiene su resultado."],
  sit="Quieres hacer un cálculo pesado en segundo plano y recoger su resultado. ¿Qué usas?",
  cod="""using System;
using System.Threading.Tasks;

class Program {
    static async Task Main() {
        int r = await Task.Run(() => 6 * 7);     // en otro hilo
        Console.WriteLine(r);
    }
}""",
  out="42",
  h="calcula en segundo plano y muestra el resultado",
  pr=("El método que ejecuta trabajo en segundo plano es Task.___. (Run)", "run"),
  ec="usar Task.Run para operaciones triviales"),
K("Hilos con Thread",
  d="ejecución de varias tareas a la vez con la clase Thread",
  u="hacer varias cosas en paralelo a bajo nivel",
  mas="Se crea un Thread con una función, Start() lo lanza y Join() espera a que termine. En código moderno suele preferirse Task.",
  k=["Thread ejecuta una tarea en paralelo.", "Start() lanza el hilo.", "Join() espera a que termine."],
  sit="Quieres ejecutar una tarea en un hilo propio y esperar a que termine. ¿Qué usas?",
  cod="""using System;
using System.Threading;

class Program {
    static void Main() {
        var t = new Thread(() => Console.WriteLine("tarea en otro hilo"));
        t.Start();
        t.Join();                       // espera a que termine
        Console.WriteLine("fin");
    }
}""",
  out="tarea en otro hilo\nfin",
  h="ejecuta una tarea en otro hilo y espera a que termine",
  pr=("El método que espera a que un hilo termine es ___. (Join)", "join"),
  ec="olvidar Join y terminar el programa antes que el hilo"),
K("lock",
  d="palabra que impide que dos hilos ejecuten a la vez un bloque",
  u="evitar condiciones de carrera",
  mas="lock (objeto) { ... } permite que solo un hilo a la vez entre al bloque. Protege datos compartidos que varios hilos modifican.",
  k=["lock permite un solo hilo a la vez.", "Protege datos compartidos.", "Evita condiciones de carrera."],
  sit="Dos hilos suman a la misma variable y los resultados salen mal. ¿Qué usas?",
  cod="""using System;
using System.Threading;

class Program {
    static int n = 0;
    static readonly object cerrojo = new object();

    static void Sumar() {
        for (int i = 0; i < 1000; i++) {
            lock (cerrojo) { n++; }          // un hilo a la vez
        }
    }

    static void Main() {
        var a = new Thread(Sumar); var b = new Thread(Sumar);
        a.Start(); b.Start();
        a.Join(); b.Join();
        Console.WriteLine(n);
    }
}""",
  out="2000",
  h="dos hilos suman a un contador protegido con lock",
  pr=("La palabra que permite un solo hilo a la vez es ___. (lock)", "lock"),
  ec="modificar datos compartidos entre hilos sin protegerlos"),
K("DateTime",
  d="estructura para trabajar con fechas y horas",
  u="calcular y formatear fechas",
  mas="new DateTime(año, mes, día) crea una fecha y DateTime.Now la actual. AddDays y similares devuelven una fecha nueva porque DateTime es inmutable. ToString(\"yyyy-MM-dd\") da el formato.",
  k=["DateTime representa fecha y hora.", "AddDays devuelve una fecha nueva.", "ToString permite elegir el formato."],
  sit="Quieres calcular la fecha 20 días después de otra y mostrarla como año-mes-día. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        var f = new DateTime(2026, 1, 15);
        var despues = f.AddDays(20);                    // devuelve una fecha nueva
        Console.WriteLine(despues.ToString("yyyy-MM-dd"));
    }
}""",
  out="2026-02-04",
  h="calcula la fecha 20 días después del 15 de enero",
  pr=("La estructura para fechas y horas es ___. (DateTime)", "datetime"),
  ec="esperar que AddDays modifique la fecha original"),
K("Archivos con File",
  d="clase para leer y escribir archivos de forma sencilla",
  u="guardar y recuperar texto en disco",
  mas="File.WriteAllText escribe un texto y File.ReadAllText lo lee entero. También existen WriteAllLines y ReadAllLines. Pueden lanzar IOException.",
  k=["File lee y escribe archivos.", "WriteAllText guarda un texto.", "Pueden lanzar IOException."],
  sit="Quieres guardar un texto en un archivo y leerlo después. ¿Qué usas?",
  cod="""using System;
using System.IO;

class Program {
    static void Main() {
        File.WriteAllText("datos.txt", "hola archivo");
        Console.WriteLine(File.ReadAllText("datos.txt"));
    }
}""",
  out="hola archivo",
  h="escribe un texto en un archivo y lo lee",
  pr=("La clase para leer y escribir archivos sencillos es ___. (File)", "file"),
  ec="no manejar las excepciones de entrada y salida"),
K("NuGet",
  d="gestor de paquetes de .NET para usar librerías externas",
  u="añadir librerías al proyecto con un comando",
  mas="dotnet add package Nombre descarga e instala una librería y la registra en el archivo .csproj. NuGet es el repositorio oficial de paquetes de .NET.",
  k=["NuGet gestiona paquetes de .NET.", "dotnet add package instala una librería.", "Las dependencias se registran en el .csproj."],
  sit="Necesitas usar una librería externa de JSON en tu proyecto. ¿Qué usas para instalarla?",
  cod="""using System;

class Program {
    static void Main() {
        // dotnet add package Newtonsoft.Json   -> se registra en el .csproj
        Console.WriteLine("Paquetes gestionados con NuGet");
    }
}""",
  out="Paquetes gestionados con NuGet",
  h="muestra un mensaje; el comentario describe la instalación de un paquete",
  pr=("El gestor de paquetes de .NET se llama ___. (NuGet)", "nuget"),
  ec="copiar los archivos .dll de las librerías a mano"),
K("Pruebas con xUnit",
  d="biblioteca para escribir pruebas automáticas",
  u="comprobar que el código funciona al cambiarlo",
  mas="Cada prueba es un método con [Fact] que usa Assert.Equal(esperado, real). Se ejecutan con dotnet test. Si algo no coincide, la prueba falla.",
  k=["xUnit permite escribir pruebas automáticas.", "Cada prueba se marca con [Fact].", "dotnet test ejecuta las pruebas."],
  sit="Cada vez que cambias código temes romper algo ya hecho. ¿Qué práctica te protege?",
  cod="""using System;

class Program {
    static int Doble(int n) { return n * 2; }

    static void Main() {
        // en xUnit sería: Assert.Equal(8, Doble(4));
        Console.WriteLine(Doble(4) == 8 ? "prueba superada" : "prueba fallida");
    }
}""",
  out="prueba superada",
  h="comprueba que una función da el resultado esperado",
  pr=("El atributo que marca una prueba en xUnit es [___]. (Fact)", "fact"),
  ec="cambiar código sin pruebas que lo respalden"),
K("Comentarios XML",
  d="comentarios /// con etiquetas que generan documentación",
  u="documentar clases y métodos",
  mas="Los comentarios /// con etiquetas como <summary>, <param> y <returns> aparecen en el editor al usar el método y pueden generar documentación.",
  k=["Los comentarios /// documentan el código.", "<summary> describe el miembro.", "El editor los muestra al usar el método."],
  sit="Quieres que otros programadores vean la explicación de tu método al usarlo. ¿Qué escribes?",
  cod="""using System;

class Program {
    /// <summary>Suma dos números.</summary>
    /// <param name="a">primer número</param>
    /// <param name="b">segundo número</param>
    /// <returns>la suma</returns>
    static int Sumar(int a, int b) { return a + b; }

    static void Main() {
        Console.WriteLine(Sumar(2, 3));
    }
}""",
  out="5",
  h="usa un método documentado con comentarios XML",
  pr=("Los comentarios de documentación empiezan con ___. (///)", "///"),
  ec="escribir comentarios que repiten lo que dice el código"),
K("Recolector de basura",
  d="mecanismo que libera automáticamente los objetos sin referencias",
  u="entender cómo C# gestiona la memoria",
  mas="Los objetos se crean con new en el montón. El recolector de basura elimina los que ya no tienen referencias, así que no hay free ni delete. Los recursos externos se liberan con IDisposable.",
  k=["El recolector de basura libera objetos sin referencias.", "En C# no se libera memoria manualmente.", "Los recursos externos requieren IDisposable."],
  sit="En C# no llamas a free ni delete y la memoria no se llena. ¿Quién libera los objetos?",
  cod="""using System;

class Program {
    static void Main() {
        string s = new string('a', 3);
        s = null;                               // sin referencias: elegible para el GC
        Console.WriteLine("el recolector liberará el objeto");
    }
}""",
  out="el recolector liberará el objeto",
  h="deja un objeto sin referencias para que lo libere el recolector",
  pr=("El mecanismo que libera objetos sin referencias es el recolector de ___. (basura)", "basura"),
  ec="creer que hay que liberar memoria manualmente en C#"),
K("Inmutabilidad",
  d="objetos cuyo estado no cambia después de crearse",
  u="evitar errores y compartir objetos con seguridad entre hilos",
  mas="Una clase inmutable usa propiedades con init o campos readonly y devuelve objetos nuevos al «modificarse». string y DateTime son inmutables. with crea una copia modificada de un record.",
  k=["Un objeto inmutable no cambia tras crearse.", "readonly e init impiden modificarlo después.", "with crea una copia modificada de un record."],
  sit="Quieres que un objeto pueda compartirse entre hilos sin riesgo de cambios. ¿Qué diseño usas?",
  cod="""using System;

record Punto(int X, int Y);

class Program {
    static void Main() {
        var p = new Punto(1, 2);
        var q = p with { X = 5 };              // copia modificada
        Console.WriteLine(p.X + " " + q.X);
    }
}""",
  out="1 5",
  h="crea una copia modificada de un record sin cambiar el original",
  pr=("Un objeto que no cambia después de crearse es ___. (inmutable)", "inmutable"),
  ec="añadir setters públicos a una clase que debía ser inmutable"),
K("Métodos de extensión",
  d="métodos estáticos que se usan como si fueran del tipo extendido",
  u="añadir funcionalidad a tipos existentes sin modificarlos",
  mas="Se declaran en una clase estática con this en el primer parámetro. LINQ está hecho con métodos de extensión.",
  k=["Un método de extensión añade funcionalidad a un tipo.", "Se declara con this en el primer parámetro.", "LINQ usa métodos de extensión."],
  sit="Quieres añadir un método «EsPar» a int sin modificar el tipo. ¿Qué usas?",
  cod="""using System;

static class Extensiones {
    public static bool EsPar(this int n) { return n % 2 == 0; }
}

class Program {
    static void Main() {
        Console.WriteLine(10.EsPar());        // True
        Console.WriteLine(7.EsPar());         // False
    }
}""",
  out="True\nFalse",
  h="añade un método EsPar al tipo int",
  pr=("En un método de extensión el primer parámetro lleva la palabra ___. (this)", "this"),
  ec="declarar el método de extensión en una clase no estática"),
K("Indexadores",
  d="miembros que permiten usar un objeto con corchetes como un array",
  u="acceder a los elementos internos de un objeto por posición",
  mas="Se declaran como public tipo this[int i] { get; set; }. Permiten escribir objeto[0] igual que con un array o una lista.",
  k=["Un indexador permite usar corchetes con un objeto.", "Se declara con this[...].", "Tiene get y set como una propiedad."],
  sit="Quieres leer los elementos de tu clase con equipo[0] en lugar de un método. ¿Qué defines?",
  cod="""using System;

class Equipo {
    private string[] nombres = {"Ana", "Luis"};
    public string this[int i] {              // indexador
        get { return nombres[i]; }
        set { nombres[i] = value; }
    }
}

class Program {
    static void Main() {
        var e = new Equipo();
        Console.WriteLine(e[1]);
    }
}""",
  out="Luis",
  h="lee un elemento de un objeto con corchetes",
  pr=("Un indexador se declara con ___[...]. (this)", "this"),
  ec="olvidar comprobar el rango dentro del indexador"),
K("Top-level statements",
  d="programas sin clase ni Main, solo con instrucciones",
  u="escribir programas pequeños con menos código",
  mas="Desde C# 9 el archivo Program.cs puede contener directamente las instrucciones. El compilador genera la clase y Main por ti. Solo un archivo del proyecto puede usarlos.",
  k=["Las instrucciones de nivel superior no necesitan Main.", "El compilador genera la clase y el Main.", "Solo un archivo del proyecto puede usarlas."],
  sit="Quieres un programa pequeño sin la ceremonia de clase y Main. ¿Qué usas?",
  cod="""using System;

// Con top-level statements bastaría con estas líneas:
//   Console.WriteLine("Hola");
class Program {
    static void Main() {
        Console.WriteLine("Hola sin ceremonia");
    }
}""",
  out="Hola sin ceremonia",
  h="muestra un saludo; el comentario muestra la forma abreviada",
  pr=("Las instrucciones sin clase ni Main son de ___ superior. (nivel)", "nivel"),
  ec="usar top-level statements en más de un archivo"),
K("Buenas prácticas",
  d="costumbres para escribir C# claro, seguro y mantenible",
  u="reducir errores y facilitar el trabajo en equipo",
  mas="Usa PascalCase para clases y métodos y camelCase para variables, programa contra interfaces, activa los tipos que admiten null (nullable), libera recursos con using, usa async para operaciones lentas y mantén los métodos cortos.",
  k=["Conviene usar PascalCase para clases y métodos.", "Conviene programar contra interfaces.", "Conviene mantener los métodos cortos."],
  sit="Estás revisando código con métodos de 300 líneas y nombres como x1 y tmp2. ¿Qué buena práctica aplicarías?",
  cod="""using System;
using System.Collections.Generic;
using System.Linq;

class Program {
    static double Promedio(IEnumerable<int> notas) {     // nombre claro, método corto
        return notas.Average();
    }

    static void Main() {
        Console.WriteLine(Promedio(new[] {7, 9, 8}));    // 8
    }
}""",
  out="8",
  h="calcula un promedio con un método claro y corto",
  pr=("En C# las clases y métodos se escriben en ___Case. (Pascal)", "pascal"),
  ec="usar nombres que solo entiende quien los escribió"),
]
