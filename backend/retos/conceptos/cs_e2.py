"""C# · Etapa 2: Bucles, métodos, arrays y colecciones."""
from ..generador import K

LISTA = [
K("Bucle while",
  d="bucle que repite mientras una condición sea verdadera",
  u="repetir sin saber cuántas veces",
  mas="La condición se evalúa antes de cada vuelta. Algo dentro del bucle debe cambiarla o nunca terminará.",
  k=["while repite mientras la condición sea verdadera.", "La condición se evalúa antes de cada vuelta.", "Sin cambios en la condición, el bucle es infinito."],
  sit="Debes seguir repitiendo hasta que ocurra algo, sin saber cuántas veces. ¿Qué bucle usas?",
  cod="""using System;

class Program {
    static void Main() {
        int n = 3;
        while (n > 0) {
            Console.WriteLine("n = " + n);
            n--;                          // cambia la condición
        }
    }
}""",
  out="n = 3\nn = 2\nn = 1",
  h="cuenta hacia atrás de 3 a 1",
  pr=("El bucle que repite mientras una condición es cierta es ___. (5 letras)", "while"),
  ec="olvidar modificar la variable de la condición"),
K("Bucle do while",
  d="bucle que ejecuta el bloque al menos una vez y luego comprueba la condición",
  u="repetir algo que debe hacerse siempre una primera vez",
  mas="La condición se evalúa al final, por eso el cuerpo se ejecuta como mínimo una vez. Termina con punto y coma tras el while.",
  k=["do while ejecuta el bloque al menos una vez.", "La condición se evalúa al final.", "do while termina con punto y coma."],
  sit="Un menú debe mostrarse siempre una vez y repetirse solo si el usuario lo pide. ¿Qué bucle usas?",
  cod="""using System;

class Program {
    static void Main() {
        int i = 10;
        do {
            Console.WriteLine("i = " + i);   // se ejecuta aunque la condición sea falsa
            i++;
        } while (i < 5);
    }
}""",
  out="i = 10",
  h="muestra i una vez aunque la condición sea falsa",
  pr=("El bucle que se ejecuta al menos una vez es do ___. (while)", "while"),
  ec="olvidar el punto y coma después del while"),
K("Bucle for",
  d="bucle con inicio, condición y paso en una línea",
  u="repetir un número conocido de veces",
  mas="for (inicio; condición; paso) controla un contador. Es el bucle clásico para recorrer rangos.",
  k=["for tiene inicio, condición y paso.", "Se usa cuando se conoce el número de repeticiones.", "El contador suele declararse dentro del for."],
  sit="Quieres mostrar los números del 1 al 5. ¿Qué bucle usas?",
  cod="""using System;

class Program {
    static void Main() {
        for (int i = 1; i <= 5; i++) {      // inicio; condición; paso
            Console.Write(i + " ");
        }
        Console.WriteLine();
    }
}""",
  out="1 2 3 4 5 ",
  h="muestra los números del 1 al 5",
  pr=("El bucle con inicio, condición y paso es ___. (3 letras)", "for"),
  ec="usar <= cuando se quería < y pasarse una vuelta"),
K("foreach",
  d="bucle que recorre directamente los elementos de una colección",
  u="recorrer listas y arrays sin índices",
  mas="foreach (tipo x in coleccion) visita cada elemento. Es corto y seguro, pero no permite modificar la colección mientras se recorre.",
  k=["foreach recorre los elementos de una colección.", "No necesita índice.", "No se puede modificar la colección mientras se recorre."],
  sit="Quieres recorrer todos los elementos de un array sin escribir índices. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int[] notas = {7, 9, 8};
        foreach (int n in notas) {          // sin índices
            Console.WriteLine(n);
        }
    }
}""",
  out="7\n9\n8",
  h="recorre un array mostrando cada nota",
  pr=("El bucle que recorre elementos de una colección es ___. (foreach)", "foreach"),
  ec="modificar la colección dentro de un foreach"),
K("break y continue",
  d="instrucciones que salen del bucle o saltan a la siguiente vuelta",
  u="controlar la ejecución de un bucle",
  mas="break termina el bucle más interno. continue omite el resto de la vuelta actual y pasa a la siguiente.",
  k=["break sale del bucle.", "continue salta a la siguiente vuelta.", "Ambos afectan al bucle más interno."],
  sit="Quieres mostrar números del 1 al 5 sin el 3 y parar al llegar al 5. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        for (int i = 1; i <= 10; i++) {
            if (i == 3) continue;     // salta el 3
            if (i == 5) break;        // sale en el 5
            Console.Write(i + " ");
        }
        Console.WriteLine();
    }
}""",
  out="1 2 4 ",
  h="muestra números saltando el 3 y parando en el 5",
  pr=("La instrucción que sale de un bucle es ___. (5 letras)", "break"),
  ec="confundir break con continue"),
K("Métodos",
  d="bloque con nombre que realiza una tarea reutilizable",
  u="no repetir código y organizar el programa",
  mas="Un método tiene modificadores, tipo de retorno, nombre, parámetros y cuerpo. Los métodos static se llaman desde Main sin crear objetos.",
  k=["Un método agrupa código reutilizable.", "Se llama por su nombre.", "Los métodos static se llaman sin crear un objeto."],
  sit="Repites el mismo cálculo en varios lugares. ¿Qué haces?",
  cod="""using System;

class Program {
    static void Saludar() {                 // método sin parámetros ni retorno
        Console.WriteLine("Hola desde un método");
    }

    static void Main() {
        Saludar();
        Saludar();
    }
}""",
  out="Hola desde un método\nHola desde un método",
  h="llama dos veces a un método que saluda",
  pr=("Un método se llama escribiendo su nombre y ___. (paréntesis)", "parentesis", "paréntesis"),
  ec="definir un método y no llamarlo"),
K("Parámetros",
  d="valores que un método recibe para trabajar",
  u="hacer métodos que sirvan con distintos datos",
  mas="Cada parámetro se declara con su tipo. Al llamar se pasan los argumentos en el mismo orden. Los tipos básicos se pasan por copia.",
  k=["Los parámetros se declaran con su tipo.", "Los argumentos se pasan en el mismo orden.", "Los tipos básicos se pasan por copia."],
  sit="Quieres que un método salude al nombre que le indiques. ¿Qué necesita?",
  cod="""using System;

class Program {
    static void Saludar(string nombre, int veces) {   // dos parámetros
        for (int i = 0; i < veces; i++) Console.WriteLine("Hola " + nombre);
    }

    static void Main() {
        Saludar("Ana", 2);
    }
}""",
  out="Hola Ana\nHola Ana",
  h="saluda a Ana dos veces usando parámetros",
  pr=("Los valores que recibe un método se llaman ___. (parámetros)", "parametros", "parámetros", "argumentos"),
  ec="pasar los argumentos en distinto orden que los parámetros"),
K("return",
  d="instrucción que devuelve un valor y termina el método",
  u="obtener un resultado de un método",
  mas="El valor devuelto debe coincidir con el tipo de retorno. Al ejecutar return, el método termina en ese punto.",
  k=["return devuelve un valor desde un método.", "return termina el método.", "El valor debe coincidir con el tipo de retorno."],
  sit="Un método calcula la suma y quieres usar el resultado en otro lugar. ¿Qué usas?",
  cod="""using System;

class Program {
    static int Sumar(int a, int b) {
        return a + b;                  // devuelve el resultado
    }

    static void Main() {
        int total = Sumar(2, 3);
        Console.WriteLine(total);
    }
}""",
  out="5",
  h="suma dos números con un método que devuelve el resultado",
  pr=("La instrucción que devuelve un valor es ___. (6 letras)", "return"),
  ec="olvidar el return en un método que debe devolver algo",
  err=("""using System;

class Program {
    static int Doble(int n) {
        n * 2;
    }
}""", 5, "Falta return: el método debe devolver n * 2.")),
K("Parámetros opcionales y con nombre",
  d="parámetros con valor por defecto y argumentos indicados por su nombre",
  u="hacer llamadas más cortas y legibles",
  mas="Un parámetro con valor por defecto, como string saludo = \"Hola\", puede omitirse. Con nombre: argumento, se indica a qué parámetro corresponde sin importar el orden.",
  k=["Un parámetro opcional tiene valor por defecto.", "Se puede omitir al llamar.", "Los argumentos con nombre no dependen del orden."],
  sit="Si no se indica el saludo quieres usar «Hola», y al llamar prefieres nombrar los argumentos. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Saludar(string nombre, string saludo = "Hola") {
        Console.WriteLine(saludo + " " + nombre);
    }

    static void Main() {
        Saludar("Ana");
        Saludar(saludo: "Buenas", nombre: "Luis");   // argumentos con nombre
    }
}""",
  out="Hola Ana\nBuenas Luis",
  h="saluda con un saludo por defecto o uno nombrado",
  pr=("Un parámetro que puede omitirse tiene un valor por ___. (defecto)", "defecto", "default"),
  ec="poner un parámetro opcional antes de uno obligatorio"),
K("Sobrecarga de métodos",
  d="varios métodos con el mismo nombre y distintos parámetros",
  u="usar un mismo nombre para operaciones parecidas",
  mas="El compilador elige la versión según el número y tipo de argumentos. El tipo de retorno por sí solo no distingue métodos.",
  k=["La sobrecarga permite métodos con igual nombre.", "Deben diferir en sus parámetros.", "El compilador elige según los argumentos."],
  sit="Quieres un método «Mostrar» que funcione con enteros y con textos. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Mostrar(int n) { Console.WriteLine("int " + n); }
    static void Mostrar(string s) { Console.WriteLine("texto " + s); }

    static void Main() {
        Mostrar(5);
        Mostrar("hola");
    }
}""",
  out="int 5\ntexto hola",
  h="llama a la versión de Mostrar adecuada para cada tipo",
  pr=("Varios métodos con el mismo nombre es ___. (sobrecarga)", "sobrecarga"),
  ec="intentar sobrecargar cambiando solo el tipo de retorno"),
K("Arrays",
  d="conjunto de elementos del mismo tipo y tamaño fijo",
  u="guardar varios valores bajo un nombre",
  mas="Se declaran con tipo[] y llaves o con new tipo[tamaño]. El primer índice es 0 y Length da el tamaño. Salirse de rango lanza IndexOutOfRangeException.",
  k=["Un array tiene tamaño fijo.", "El primer índice es 0.", "Length da el tamaño del array."],
  sit="Debes guardar exactamente cinco notas con tamaño conocido. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int[] notas = {7, 9, 8};
        notas[1] = 10;
        Console.WriteLine(notas[0] + " " + notas[1]);
        Console.WriteLine(notas.Length);
    }
}""",
  out="7 10\n3",
  h="guarda tres notas y cambia una",
  pr=("El primer elemento de un array tiene índice ___. (0)", "0", "cero"),
  ec="acceder a un índice fuera del array",
  err=("""using System;

class Program {
    static void Main() {
        int[] a = {1, 2, 3};
        Console.WriteLine(a[3]);
    }
}""", 6, "El último índice válido es 2: a[3] lanza IndexOutOfRangeException.")),
K("Recorrer arrays",
  d="visitar cada elemento de un array con un bucle",
  u="calcular totales, buscar y mostrar datos",
  mas="Se usa un for con índice de 0 a Length-1, o un foreach. Con índice puedes saber la posición y modificar elementos.",
  k=["Se recorre un array con un bucle.", "El índice va de 0 a Length-1.", "Length da el número de elementos."],
  sit="Quieres sumar todas las notas de un array. ¿Qué haces?",
  cod="""using System;

class Program {
    static void Main() {
        int[] notas = {7, 9, 8};
        int suma = 0;
        for (int i = 0; i < notas.Length; i++) {
            suma += notas[i];
        }
        Console.WriteLine(suma);
    }
}""",
  out="24",
  h="suma todos los elementos de un array",
  pr=("Un array de n elementos se recorre con índices de 0 a ___. (n-1)", "n-1", "n - 1"),
  ec="recorrer hasta Length en lugar de Length-1"),
K("Interpolación de texto",
  d="texto con $ que inserta valores dentro de llaves",
  u="construir mensajes mezclando texto y variables",
  mas="Se escribe $\"Hola {nombre}\" y cada expresión entre llaves se sustituye por su valor. Es más legible que concatenar con +.",
  k=["La interpolación usa $ antes de las comillas.", "Las llaves insertan valores.", "Es más legible que concatenar con +."],
  sit="Quieres armar «Hola Ana, tienes 20 años» con variables sin sumar textos a mano. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        string nombre = "Ana";
        int edad = 20;
        Console.WriteLine($"Hola {nombre}, tienes {edad} años");   // $ y llaves
    }
}""",
  out="Hola Ana, tienes 20 años",
  h="arma un saludo con el nombre y la edad",
  pr=("La interpolación empieza con el signo ___ antes de las comillas. ($)", "$"),
  ec="olvidar el signo $ y ver las llaves tal cual",
  err=("""using System;

class Program {
    static void Main() {
        string n = "Ana";
        Console.WriteLine("Hola {n}");
    }
}""", 6, "Sin el signo $ las llaves no se sustituyen: debe ser $\"Hola {n}\".")),
K("Métodos de string",
  d="métodos para consultar y transformar texto",
  u="trabajar con cadenas con facilidad",
  mas="Length, Substring, IndexOf, ToUpper, Contains, Replace y Trim son los más usados. Como string es inmutable, devuelven un texto nuevo.",
  k=["Substring extrae una parte del texto.", "ToUpper pasa el texto a mayúsculas.", "Los métodos de string devuelven un texto nuevo."],
  sit="Quieres extraer una parte de un texto y pasarlo a mayúsculas. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        string s = "Hola mundo";
        Console.WriteLine(s.Substring(0, 4));       // Hola
        Console.WriteLine(s.ToUpper());
        Console.WriteLine(s.IndexOf("mundo"));      // 5
    }
}""",
  out="Hola\nHOLA MUNDO\n5",
  h="extrae, transforma y busca en un texto",
  pr=("El método que extrae una parte de un string es ___. (Substring)", "substring"),
  ec="creer que ToUpper modifica el string original"),
K("StringBuilder",
  d="clase para construir textos modificables de forma eficiente",
  u="concatenar muchos textos sin crear objetos de más",
  mas="Concatenar con + dentro de un bucle crea muchos strings. StringBuilder los acumula con Append y al final se obtiene el resultado con ToString().",
  k=["StringBuilder construye textos modificables.", "Append añade texto al final.", "ToString() devuelve el resultado."],
  sit="Debes armar un texto largo uniendo cientos de trozos en un bucle. ¿Qué usas?",
  cod="""using System;
using System.Text;

class Program {
    static void Main() {
        var sb = new StringBuilder();
        for (int i = 1; i <= 3; i++) {
            sb.Append(i).Append(",");      // Append añade al final
        }
        Console.WriteLine(sb.ToString());
    }
}""",
  out="1,2,3,",
  h="construye un texto con números separados por comas",
  pr=("La clase para construir textos modificables es ___. (StringBuilder)", "stringbuilder"),
  ec="concatenar con + dentro de un bucle largo"),
K("Math",
  d="clase con funciones matemáticas estáticas",
  u="hacer cálculos como potencias, raíces y redondeos",
  mas="Math.Sqrt, Math.Pow, Math.Abs, Math.Max y Math.Min se llaman con Math.Nombre(), sin crear objetos. Sqrt y Pow devuelven double.",
  k=["Math ofrece funciones matemáticas estáticas.", "Math.Sqrt calcula la raíz cuadrada.", "No se crea un objeto Math."],
  sit="Necesitas calcular una raíz cuadrada y una potencia. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        Console.WriteLine(Math.Sqrt(81));     // 9
        Console.WriteLine(Math.Pow(2, 10));   // 1024
        Console.WriteLine(Math.Max(3, 7));    // 7
    }
}""",
  out="9\n1024\n7",
  h="calcula una raíz, una potencia y un máximo",
  pr=("La clase de funciones matemáticas es ___. (Math)", "math"),
  ec="olvidar que Sqrt y Pow devuelven double"),
K("List<T>",
  d="lista genérica que crece dinámicamente",
  u="guardar colecciones cuyo tamaño cambia",
  mas="List<tipo> se importa de System.Collections.Generic. Se usa con Add, Count, indexador [i], Remove y Contains.",
  k=["List<T> es una lista que crece.", "Add añade y Count cuenta.", "Se accede por posición con [i]."],
  sit="No sabes cuántos elementos tendrá tu lista y debe crecer. ¿Qué usas?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        var nombres = new List<string>();
        nombres.Add("Ana");
        nombres.Add("Luis");
        Console.WriteLine(nombres.Count + " " + nombres[1]);
    }
}""",
  out="2 Luis",
  h="añade dos nombres a una lista y consulta datos",
  pr=("La lista genérica que crece dinámicamente es ___<T>. (List)", "list"),
  ec="usar un array cuando el tamaño cambia"),
K("Operaciones de lista",
  d="métodos como Remove, Contains y Sort para manipular una lista",
  u="quitar, buscar y ordenar elementos",
  mas="Remove elimina un valor, Contains comprueba si existe, Sort ordena y string.Join une los elementos en un texto.",
  k=["Remove elimina un elemento.", "Contains comprueba si un valor está.", "Sort ordena la lista."],
  sit="Quieres saber si un número está en la lista, quitarlo y ordenar el resto. ¿Qué usas?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        var l = new List<int> {3, 1, 2};
        Console.WriteLine(l.Contains(1));        // True
        l.Remove(1);
        l.Sort();
        Console.WriteLine(string.Join(", ", l)); // 2, 3
    }
}""",
  out="True\n2, 3",
  h="comprueba, quita y ordena elementos de una lista",
  pr=("El método que ordena una lista es ___. (Sort)", "sort"),
  ec="quitar elementos de una lista mientras se recorre con foreach"),
K("Dictionary",
  d="colección que asocia claves con valores",
  u="buscar valores a partir de una clave",
  mas="Dictionary<K, V> guarda pares clave-valor. Se asigna con d[clave] = valor, se consulta con d[clave] y ContainsKey comprueba si existe. Consultar una clave inexistente lanza una excepción.",
  k=["Dictionary asocia claves con valores.", "ContainsKey comprueba si existe una clave.", "Consultar una clave inexistente lanza una excepción."],
  sit="Quieres guardar la edad de cada persona buscándola por su nombre. ¿Qué usas?",
  cod="""using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        var edades = new Dictionary<string, int>();
        edades["Ana"] = 20;
        edades["Luis"] = 25;
        Console.WriteLine(edades["Luis"]);              // 25
        Console.WriteLine(edades.ContainsKey("Eva"));   // False
    }
}""",
  out="25\nFalse",
  h="guarda edades por nombre y consulta datos",
  pr=("La colección clave-valor es ___. (Dictionary)", "dictionary"),
  ec="consultar una clave que no existe sin comprobarla"),
K("Convertir texto a número",
  d="métodos como int.Parse y int.TryParse que pasan un texto a número",
  u="usar como número un dato recibido como texto",
  mas="int.Parse lanza una excepción si el texto no es válido. int.TryParse devuelve bool e indica si pudo convertir, sin lanzar excepción.",
  k=["int.Parse convierte texto a int.", "int.TryParse no lanza excepción.", "Un texto inválido en Parse lanza FormatException."],
  sit="Tienes el texto «123» y necesitas sumarlo como número, sin que falle con texto inválido. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        if (int.TryParse("123", out int n)) {
            Console.WriteLine(n + 1);        // 124
        }
        Console.WriteLine(int.TryParse("abc", out int m));   // False
    }
}""",
  out="124\nFalse",
  h="convierte un texto en número sin lanzar excepción",
  pr=("El método que convierte sin lanzar excepción es int.___. (TryParse)", "tryparse"),
  ec="usar Parse con un texto no numérico sin controlar el error"),
]
