"""C# · Etapa 1: Primeros pasos."""
from ..generador import K

LISTA = [
K("Qué es C#",
  d="lenguaje moderno orientado a objetos creado por Microsoft para la plataforma .NET",
  u="crear aplicaciones web, de escritorio, móviles y videojuegos con Unity",
  mas="C# es un lenguaje con tipado estático y recolector de basura. Se ejecuta sobre .NET, que funciona en Windows, Mac y Linux. Es el lenguaje principal de Unity.",
  k=["C# es un lenguaje orientado a objetos.", "C# se ejecuta sobre la plataforma .NET.", "C# se usa en aplicaciones web y videojuegos con Unity."],
  sit="Quieres programar un videojuego con Unity y una aplicación web en el mismo lenguaje. ¿Qué lenguaje eliges?",
  cod="""using System;

class Program {
    static void Main() {
        Console.WriteLine("Hola desde C#");   // un programa mínimo
    }
}""",
  out="Hola desde C#",
  h="muestra un saludo desde C#",
  pr=("C# se ejecuta sobre la plataforma ___. (.NET)", ".net", "net", "dotnet"),
  ec="creer que C# solo funciona en Windows"),
K("dotnet run",
  d="comando que compila y ejecuta un proyecto de .NET",
  u="probar el programa rápidamente",
  mas="dotnet new console crea un proyecto, dotnet build lo compila y dotnet run lo compila y ejecuta. El código vive en un archivo Program.cs.",
  k=["dotnet run compila y ejecuta el proyecto.", "dotnet new console crea un proyecto de consola.", "El código se guarda en archivos .cs."],
  sit="Escribiste tu programa en Program.cs y quieres ejecutarlo. ¿Qué comando usas?",
  cod="""using System;

class Program {
    static void Main() {
        // dotnet new console   y luego   dotnet run
        Console.WriteLine("Ejecutado con dotnet run");
    }
}""",
  out="Ejecutado con dotnet run",
  h="muestra un mensaje de un programa ejecutado con dotnet",
  pr=("El comando que compila y ejecuta es dotnet ___. (run)", "run"),
  ec="olvidar crear el proyecto antes de ejecutar"),
K("Método Main",
  d="método donde empieza la ejecución de un programa C#",
  u="indicar el punto de entrada",
  mas="Main es un método estático dentro de una clase. En proyectos nuevos puede omitirse con instrucciones de nivel superior, pero sigue siendo el punto de entrada.",
  k=["Main es el punto de entrada del programa.", "Main es un método estático.", "Se escribe con M mayúscula."],
  sit="El compilador dice que no encuentra el punto de entrada del programa. ¿Qué falta?",
  cod="""using System;

class Program {
    static void Main() {              // aquí empieza todo
        Console.WriteLine("Dentro de Main");
    }
}""",
  out="Dentro de Main",
  h="ejecuta el código dentro de Main",
  pr=("El método donde empieza un programa C# es ___. (Main)", "main"),
  ec="escribir main con minúscula",
  err=("""using System;

class Program {
    static void main() {
        Console.WriteLine("Hola");
    }
}""", 4, "El punto de entrada debe llamarse Main, con M mayúscula.")),
K("using",
  d="directiva que importa un espacio de nombres",
  u="usar clases sin escribir su nombre completo",
  mas="using System; permite escribir Console en lugar de System.Console. Cada espacio de nombres agrupa clases relacionadas, como System.Collections.Generic.",
  k=["using importa un espacio de nombres.", "Evita escribir nombres completos.", "System contiene clases básicas como Console."],
  sit="Quieres escribir Console.WriteLine sin repetir System. ¿Qué agregas arriba?",
  cod="""using System;                     // ahora Console se puede usar directamente

class Program {
    static void Main() {
        Console.WriteLine("using System incluido");
    }
}""",
  out="using System incluido",
  h="usa Console gracias a importar System",
  pr=("La directiva para importar un espacio de nombres es ___. (using)", "using"),
  ec="olvidar using System al usar Console"),
K("Console.WriteLine",
  d="método que escribe una línea de texto en la consola",
  u="mostrar mensajes y valores",
  mas="WriteLine escribe y salta de línea; Write escribe sin saltar. Se pueden mostrar varios valores con interpolación o con +.",
  k=["WriteLine escribe y salta de línea.", "Write escribe sin salto de línea.", "Pertenece a la clase Console."],
  sit="Debes mostrar un mensaje y pasar a la línea siguiente. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        Console.WriteLine("Línea 1");
        Console.Write("Sin salto, ");
        Console.WriteLine("y continúa");
    }
}""",
  out="Línea 1\nSin salto, y continúa",
  h="muestra texto con WriteLine y Write",
  pr=("El método que escribe y salta de línea es Console.___. (WriteLine)", "writeline"),
  ec="olvidar el punto y coma al final"),
K("Comentarios",
  d="texto que el compilador ignora",
  u="explicar el código",
  mas="// comenta una línea y /* ... */ varias. /// genera comentarios de documentación XML.",
  k=["Los comentarios son ignorados al compilar.", "// comenta una línea.", "/// crea documentación XML."],
  sit="Quieres dejar una nota que no afecte al programa. ¿Qué escribes?",
  cod="""using System;

class Program {
    static void Main() {
        // comentario de una línea
        /* comentario
           de varias líneas */
        Console.WriteLine("Los comentarios no se ejecutan");
    }
}""",
  out="Los comentarios no se ejecutan",
  h="muestra un mensaje; los comentarios se ignoran",
  pr=("El comentario de una línea empieza con ___. (//)", "//"),
  ec="dejar un /* sin cerrar"),
K("Variables",
  d="espacio con nombre que guarda un valor",
  u="almacenar datos que el programa usa",
  mas="En C# se declara el tipo antes del nombre: tipo nombre = valor;. El tipo es fijo y el compilador no deja asignar valores de otro tipo.",
  k=["Una variable guarda un valor con nombre.", "Hay que declarar su tipo.", "El tipo de una variable no cambia."],
  sit="Necesitas recordar la edad del usuario para usarla después. ¿Qué declaras?",
  cod="""using System;

class Program {
    static void Main() {
        int edad = 20;          // tipo nombre = valor
        edad = edad + 1;
        Console.WriteLine(edad);
    }
}""",
  out="21",
  h="guarda una edad y le suma uno",
  pr=("Antes del nombre de una variable se escribe su ___. (tipo)", "tipo"),
  ec="asignar un texto a una variable int",
  err=("""using System;

class Program {
    static void Main() {
        int edad = "veinte";
        Console.WriteLine(edad);
    }
}""", 5, "edad es int y no puede guardar un texto.")),
K("int",
  d="tipo para guardar números enteros",
  u="contar y calcular con valores sin decimales",
  mas="Un int ocupa 4 bytes. La división entre dos int descarta los decimales. Para enteros más grandes existe long.",
  k=["int guarda números enteros.", "La división entre int descarta los decimales.", "long guarda enteros más grandes."],
  sit="Debes guardar la cantidad de alumnos de una clase. ¿Qué tipo usas?",
  cod="""using System;

class Program {
    static void Main() {
        int alumnos = 25;
        Console.WriteLine(alumnos / 2);   // 12: se pierden los decimales
    }
}""",
  out="12",
  h="divide un entero entre 2 y pierde los decimales",
  pr=("El tipo para números enteros es ___. (3 letras)", "int"),
  ec="esperar decimales al dividir dos int"),
K("double",
  d="tipo para guardar números con decimales",
  u="trabajar con medidas y cálculos no enteros",
  mas="double tiene 64 bits y es el decimal por defecto. decimal es más exacto y se usa para dinero. Los literales float llevan f al final.",
  k=["double guarda números decimales.", "decimal es más exacto y sirve para dinero.", "Un literal float termina en f."],
  sit="Debes guardar un valor con decimales para un cálculo científico. ¿Qué tipo usas?",
  cod="""using System;

class Program {
    static void Main() {
        double altura = 2.0;
        Console.WriteLine(altura * 3);   // 6
    }
}""",
  out="6",
  h="multiplica una altura decimal por 3",
  pr=("El tipo decimal más usado es ___. (6 letras)", "double"),
  ec="usar double para guardar dinero con exactitud"),
K("bool",
  d="tipo con solo dos valores: true y false",
  u="representar condiciones verdaderas o falsas",
  mas="Las comparaciones dan un bool. Al mostrarlo, C# escribe True o False con inicial mayúscula.",
  k=["bool solo admite true o false.", "Las comparaciones devuelven bool.", "Al mostrarse aparece como True o False."],
  sit="Quieres guardar si un usuario está activo (sí o no). ¿Qué tipo usas?",
  cod="""using System;

class Program {
    static void Main() {
        bool activo = true;
        bool mayor = 20 >= 18;          // resultado de una comparación
        Console.WriteLine(activo);
        Console.WriteLine(mayor);
    }
}""",
  out="True\nTrue",
  h="muestra dos valores booleanos",
  pr=("El tipo que solo vale true o false es ___. (4 letras)", "bool"),
  ec="esperar que se muestre en minúsculas"),
K("char",
  d="tipo que guarda un solo carácter",
  u="trabajar con letras sueltas",
  mas="Se escribe entre comillas simples, como 'A'. Internamente es un número Unicode, y se puede convertir a int.",
  k=["char guarda un solo carácter.", "Se escribe entre comillas simples.", "Internamente es un número Unicode."],
  sit="Quieres guardar la inicial de un nombre. ¿Qué tipo usas?",
  cod="""using System;

class Program {
    static void Main() {
        char letra = 'A';
        Console.WriteLine(letra);
        Console.WriteLine((int)letra);   // código de la letra
    }
}""",
  out="A\n65",
  h="muestra una letra y su código",
  pr=("Un solo carácter se guarda en una variable ___. (char)", "char"),
  ec="usar comillas dobles para un solo char"),
K("string",
  d="tipo para guardar y manejar texto",
  u="trabajar con nombres, mensajes y palabras",
  mas="Un string va entre comillas dobles y es inmutable. Length da la longitud (sin paréntesis) y + concatena.",
  k=["string guarda texto.", "Se escribe entre comillas dobles.", "Length es una propiedad, no lleva paréntesis."],
  sit="Debes guardar el nombre de un usuario. ¿Qué tipo usas?",
  cod="""using System;

class Program {
    static void Main() {
        string nombre = "Ana";
        Console.WriteLine(nombre.Length);        // 3
        Console.WriteLine("Hola " + nombre);     // concatenar
    }
}""",
  out="3\nHola Ana",
  h="mide un texto y lo concatena con otro",
  pr=("El tipo para guardar texto es ___. (6 letras)", "string"),
  ec="escribir Length() con paréntesis"),
K("var",
  d="palabra que deja al compilador deducir el tipo de una variable local",
  u="escribir menos cuando el tipo es evidente",
  mas="Con var n = 5; el compilador deduce int. El tipo sigue siendo fijo: var no significa «cualquier tipo». La variable debe inicializarse.",
  k=["var deduce el tipo de la variable.", "La variable debe inicializarse.", "El tipo deducido no cambia."],
  sit="El tipo es evidente por el valor y no quieres repetirlo. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        var n = 10;              // int
        var s = "hola";          // string
        Console.WriteLine(n + s.Length);
    }
}""",
  out="14",
  h="deja que el compilador deduzca los tipos",
  pr=("La palabra que deduce el tipo local es ___. (var)", "var"),
  ec="usar var sin inicializar la variable"),
K("const",
  d="palabra que declara una constante que no cambia",
  u="dar nombre a valores fijos",
  mas="Una const se inicializa al declararla y su valor se conoce al compilar. Intentar cambiarla produce un error. readonly sirve para valores fijados al ejecutar.",
  k=["const declara un valor que no cambia.", "Se inicializa al declararla.", "Cambiarla es un error de compilación."],
  sit="El valor de pi no debe cambiar jamás. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        const int DOCENA = 12;      // no se puede reasignar
        Console.WriteLine(DOCENA * 2);
    }
}""",
  out="24",
  h="usa una constante en un cálculo",
  pr=("La palabra que declara un valor fijo es ___. (const)", "const"),
  ec="intentar reasignar una constante",
  err=("""using System;

class Program {
    static void Main() {
        const int N = 1;
        N = 2;
    }
}""", 6, "N es const y no se puede reasignar.")),
K("Operadores aritméticos",
  d="símbolos + - * / que realizan cálculos",
  u="hacer operaciones matemáticas",
  mas="* y / se evalúan antes que + y -. Los paréntesis cambian el orden. La división entre enteros devuelve un entero.",
  k=["+, -, * y / son operadores aritméticos.", "* y / van antes que + y -.", "Los paréntesis cambian el orden."],
  sit="Debes calcular 3 productos a 5 euros más 2 de envío. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        Console.WriteLine(3 * 5 + 2);       // 17
        Console.WriteLine(3 * (5 + 2));     // 21
    }
}""",
  out="17\n21",
  h="calcula un total con multiplicación y suma",
  pr=("El operador que multiplica es ___. (un signo)", "*"),
  ec="olvidar la precedencia de * sobre +"),
K("Resto %",
  d="operador que devuelve el resto de una división",
  u="saber si un número es par o múltiplo de otro",
  mas="7 % 3 vale 1. Un número es par cuando n % 2 == 0.",
  k=["% devuelve el resto de una división.", "n % 2 == 0 indica que n es par.", "Sirve para comprobar múltiplos."],
  sit="Necesitas saber si un número es par. ¿Qué operador usas?",
  cod="""using System;

class Program {
    static void Main() {
        Console.WriteLine(7 % 3);           // 1
        Console.WriteLine(10 % 2 == 0);     // True
    }
}""",
  out="1\nTrue",
  h="calcula un resto y comprueba si 10 es par",
  pr=("El operador del resto de una división es ___. (%)", "%"),
  ec="confundir % con un porcentaje"),
K("Comparación y lógica",
  d="operadores ==, !=, <, >, && y || para formar condiciones",
  u="decidir según varias condiciones",
  mas="Las comparaciones devuelven bool. && exige ambas condiciones, || al menos una y ! invierte. Un solo = asigna.",
  k=["== compara igualdad.", "&& exige ambas condiciones.", "|| exige al menos una."],
  sit="Quieres saber si la edad es mayor de 17 y menor de 65. ¿Qué operadores usas?",
  cod="""using System;

class Program {
    static void Main() {
        int edad = 30;
        Console.WriteLine(edad > 17 && edad < 65);    // True
        Console.WriteLine(edad == 30 || edad == 31);  // True
        Console.WriteLine(!(edad > 20));              // False
    }
}""",
  out="True\nTrue\nFalse",
  h="combina condiciones con y, o, no",
  pr=("El operador lógico «y» es ___. (&&)", "&&"),
  ec="usar = en lugar de == en una condición"),
K("if y else",
  d="estructura que ejecuta código según una condición",
  u="tomar decisiones",
  mas="if ejecuta su bloque si la condición es true; else cubre el caso contrario y else if encadena varias. La condición debe ser bool.",
  k=["if ejecuta un bloque si la condición es true.", "else cubre el caso contrario.", "La condición debe ser de tipo bool."],
  sit="Debes mostrar «mayor» o «menor» según la edad. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int edad = 20;
        if (edad >= 18) {
            Console.WriteLine("Mayor de edad");
        } else {
            Console.WriteLine("Menor de edad");
        }
    }
}""",
  out="Mayor de edad",
  h="muestra si la persona es mayor o menor",
  pr=("La palabra del caso contrario de un if es ___. (else)", "else"),
  ec="usar un número como condición del if"),
K("switch",
  d="estructura que elige entre varios casos",
  u="reemplazar muchos if encadenados",
  mas="switch compara un valor con cada case. En C# cada caso debe terminar con break (no hay fall-through implícito). default cubre el resto.",
  k=["switch elige un caso según un valor.", "Cada case termina con break.", "default cubre los valores no previstos."],
  sit="Según un número de día debes mostrar su nombre. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int dia = 2;
        switch (dia) {
            case 1: Console.WriteLine("Lunes"); break;
            case 2: Console.WriteLine("Martes"); break;
            default: Console.WriteLine("Otro día"); break;
        }
    }
}""",
  out="Martes",
  h="muestra el nombre de un día según su número",
  pr=("La palabra que cierra cada caso del switch es ___. (break)", "break"),
  ec="olvidar break al final de un caso"),
K("Operador ternario",
  d="operador ?: que elige entre dos valores según una condición",
  u="escribir un if corto dentro de una expresión",
  mas="Se escribe condición ? valorSiCierto : valorSiFalso. Es útil para asignaciones simples, sin anidar demasiado.",
  k=["El ternario elige entre dos valores.", "Se escribe condición ? a : b.", "Es un if compacto dentro de una expresión."],
  sit="Quieres asignar «mayor» o «menor» a un texto en una sola línea. ¿Qué usas?",
  cod="""using System;

class Program {
    static void Main() {
        int edad = 20;
        string r = edad >= 18 ? "mayor" : "menor";   // condición ? si : no
        Console.WriteLine(r);
    }
}""",
  out="mayor",
  h="asigna mayor o menor con un operador ternario",
  pr=("El operador ternario usa los signos ? y ___. (:)", ":"),
  ec="anidar muchos ternarios y volverlos ilegibles"),
]
