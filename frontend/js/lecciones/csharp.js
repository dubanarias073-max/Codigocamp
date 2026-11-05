// Lecciones de C#. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"C# se usa en aplicaciones, videojuegos (Unity) y web.",
    p:["Console.WriteLine imprime una línea", "using System; trae la clase Console"],
    c:`using System;

class Program {
  static void Main() {
    Console.WriteLine("¡Hola, CódigoCamp!");
  }
}` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"Los tipos se indican antes del nombre.",
    p:["int, string, bool", "var deduce el tipo"],
    c:`using System;

class Program {
  static void Main() {
    int edad = 20;
    if (edad >= 18) Console.WriteLine("Mayor de edad");
  }
}` },
  { m:"Fundamentos", t:"Bucles", x:"for repite un bloque un número conocido de veces.",
    p:["for (inicio; condición; paso)", "Se puede unir texto con +"],
    c:`using System;

class Program {
  static void Main() {
    for (int i = 1; i <= 5; i++) {
      Console.WriteLine("Vuelta " + i);
    }
  }
}` },
  { m:"Fundamentos", t:"Métodos", x:"Un método agrupa instrucciones y puede devolver un valor.",
    p:["static permite llamarlo desde Main", "Por convención empiezan en mayúscula"],
    c:`using System;

class Program {
  static int Doble(int n) {
    return n * 2;
  }
  static void Main() {
    Console.WriteLine(Doble(21));
  }
}` },
  { m:"Intermedio", t:"Listas y diccionarios", x:"List<T> es una lista que crece y Dictionary<K, V> guarda pares clave-valor. foreach las recorre.",
    p:["List<string> guarda textos", "Dictionary<string, int> asocia claves con valores", "Count da la cantidad de elementos"],
    c:"using System;\nusing System.Collections.Generic;\n\nclass Program {\n  static void Main() {\n    var nombres = new List<string> { \"Ana\", \"Luis\" };\n    nombres.Add(\"Marta\");\n\n    var edades = new Dictionary<string, int> {\n      [\"Ana\"] = 20, [\"Luis\"] = 25, [\"Marta\"] = 30\n    };\n\n    foreach (var n in nombres) {\n      Console.WriteLine($\"{n} tiene {edades[n]}\");\n    }\n    Console.WriteLine(nombres.Count);\n  }\n}",
    r:"Busca con ContainsKey si \"Pedro\" está en el diccionario." },
  { m:"Intermedio", t:"Clases y propiedades", x:"Las propiedades exponen datos con get y set. El constructor prepara el objeto al crearlo.",
    p:["{ get; set; } crea una propiedad automática", "Los miembros son private por defecto", "this se refiere al objeto actual"],
    c:"using System;\n\nclass Persona {\n  public string Nombre { get; set; }\n  public int Edad { get; private set; }\n\n  public Persona(string nombre, int edad) {\n    Nombre = nombre;\n    Edad = edad;\n  }\n\n  public string Saludar() => $\"Hola, soy {Nombre} y tengo {Edad}\";\n}\n\nclass Program {\n  static void Main() {\n    var p = new Persona(\"Ana\", 20);\n    Console.WriteLine(p.Saludar());\n  }\n}",
    r:"Añade un método CumplirAnios() que sume 1 a Edad.",
    e:"Dejar todas las propiedades con set público: expón solo lo necesario." },
  { m:"Avanzado", t:"Excepciones", x:"try/catch captura errores y finally se ejecuta siempre. Con throw lanzas tus propias excepciones.",
    p:["try encierra el código que puede fallar", "catch (TipoDeError e) atrapa un error concreto", "using libera recursos automáticamente"],
    c:"using System;\n\nclass Program {\n  static int Dividir(int a, int b) {\n    if (b == 0) throw new ArgumentException(\"No se puede dividir entre 0\");\n    return a / b;\n  }\n\n  static void Main() {\n    try {\n      Console.WriteLine(Dividir(10, 2));\n      Console.WriteLine(Dividir(5, 0));\n    } catch (ArgumentException e) {\n      Console.WriteLine(\"Error: \" + e.Message);\n    } finally {\n      Console.WriteLine(\"Fin\");\n    }\n  }\n}",
    r:"Convierte \"abc\" con int.Parse y captura FormatException." },
  { m:"Avanzado", t:"Herencia, interfaces y polimorfismo", x:"Una clase hereda con \":\" y una interfaz define un contrato. virtual y override permiten cambiar el comportamiento.",
    p:["virtual permite reemplazar un método", "override lo reemplaza en la clase hija", "Una clase puede implementar varias interfaces"],
    c:"using System;\n\ninterface ISonido { string HacerSonido(); }\n\nclass Animal : ISonido {\n  public virtual string HacerSonido() => \"...\";\n}\n\nclass Perro : Animal {\n  public override string HacerSonido() => \"Guau\";\n}\n\nclass Program {\n  static void Main() {\n    Animal a = new Perro();\n    Console.WriteLine(a.HacerSonido());\n  }\n}",
    r:"Añade la clase Gato y usa un arreglo de Animal con varios animales." },
  { m:"Experto", t:"LINQ", x:"LINQ consulta colecciones con una sintaxis parecida a SQL: Where filtra, Select transforma y OrderBy ordena.",
    p:["using System.Linq; activa LINQ", "Where, Select y OrderBy se encadenan", "ToList() ejecuta la consulta"],
    c:"using System;\nusing System.Linq;\n\nclass Program {\n  static void Main() {\n    int[] nums = { 5, 2, 8, 1, 9, 4 };\n    var resultado = nums\n      .Where(n => n > 3)\n      .OrderBy(n => n)\n      .Select(n => n * 10)\n      .ToList();\n    Console.WriteLine(string.Join(\", \", resultado));\n  }\n}",
    r:"Calcula el promedio de los números con nums.Average()." },
  { m:"Experto", t:"async/await y NuGet", x:"async/await escribe código asíncrono legible. NuGet es el gestor de paquetes de .NET.",
    p:["async Task marca un método asíncrono", "await espera sin bloquear el programa", "dotnet add package instala paquetes"],
    c:"using System;\nusing System.Threading.Tasks;\n\nclass Program {\n  static async Task<string> CargarAsync() {\n    await Task.Delay(500);\n    return \"Datos listos\";\n  }\n\n  static async Task Main() {\n    Console.WriteLine(\"Cargando...\");\n    string datos = await CargarAsync();\n    Console.WriteLine(datos);\n  }\n}",
    r:"Lanza dos tareas a la vez con Task.WhenAll y mide el tiempo.",
    e:"Usar .Result o .Wait() en lugar de await puede bloquear el programa." },
];
