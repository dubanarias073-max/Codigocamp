"""Java · Etapa 1: Primeros pasos."""
from ..generador import K

LISTA = [
K("Qué es Java",
  d="lenguaje de programación orientado a objetos que se ejecuta en la máquina virtual de Java",
  u="crear aplicaciones que funcionan en distintos sistemas",
  mas="Java se compila a bytecode, un código intermedio que ejecuta la JVM. Por eso el mismo programa corre en Windows, Mac o Linux. Se usa en aplicaciones empresariales, Android y servidores.",
  k=["Java es un lenguaje orientado a objetos.", "Java se compila a bytecode que ejecuta la JVM.", "El mismo programa Java funciona en distintos sistemas."],
  sit="Necesitas un programa que funcione igual en Windows, Mac y Linux sin recompilar. ¿Qué lenguaje eliges?",
  cod="""public class Main {
    public static void main(String[] args) {
        System.out.println("Hola desde Java");   // un programa mínimo
    }
}""",
  out="Hola desde Java",
  h="muestra un saludo desde Java",
  pr=("Java se compila a ___ que ejecuta la JVM. (bytecode)", "bytecode"),
  ec="creer que Java se compila directamente a código de máquina"),
K("Compilar y ejecutar",
  d="proceso de traducir el código .java con javac y ejecutarlo con java",
  u="convertir tu código en un programa que corre",
  mas="javac Main.java genera Main.class con el bytecode. java Main lo ejecuta en la JVM. El nombre del archivo debe coincidir con el de la clase pública.",
  k=["javac compila el código fuente.", "java ejecuta el programa en la JVM.", "El archivo debe llamarse como la clase pública."],
  sit="Escribiste Main.java y quieres ejecutarlo. ¿Qué pasos sigues?",
  cod="""public class Main {
    public static void main(String[] args) {
        // javac Main.java   y luego   java Main
        System.out.println("Compilado con javac");
    }
}""",
  out="Compilado con javac",
  h="muestra un mensaje de un programa compilado con javac",
  pr=("El comando que compila código Java es ___. (5 letras)", "javac"),
  ec="ejecutar java Main.java sin entender que primero se compila"),
K("Clase y main",
  d="estructura mínima: una clase con un método main como punto de entrada",
  u="indicar por dónde empieza el programa",
  mas="Todo en Java vive dentro de una clase. El método public static void main(String[] args) es donde arranca la ejecución.",
  k=["Todo el código Java está dentro de clases.", "main es el punto de entrada del programa.", "main es public static void."],
  sit="Tu programa compila, pero al ejecutarlo dice que no encuentra el método principal. ¿Qué falta?",
  cod="""public class Main {
    public static void main(String[] args) {   // aquí empieza todo
        System.out.println("Dentro de main");
    }
}""",
  out="Dentro de main",
  h="ejecuta el código dentro de main",
  pr=("El método donde empieza un programa Java es ___. (4 letras)", "main"),
  ec="escribir main sin public static",
  err=("""public class Main {
    public void main(String[] args) {
        System.out.println("Hola");
    }
}""", 2, "main debe ser public static void para que la JVM pueda arrancarlo.")),
K("System.out.println",
  d="instrucción que escribe una línea de texto en la consola",
  u="mostrar mensajes y valores",
  mas="println escribe el texto y salta de línea. print escribe sin saltar. Puedes unir textos y valores con el operador +.",
  k=["println escribe y salta de línea.", "print escribe sin salto de línea.", "Se puede unir texto y valores con +."],
  sit="Debes mostrar un mensaje y pasar a la línea siguiente. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        System.out.println("Línea 1");
        System.out.print("Sin salto, ");
        System.out.println("y continúa");
    }
}""",
  out="Línea 1\nSin salto, y continúa",
  h="muestra texto con println y print",
  pr=("La instrucción que imprime y salta de línea es System.out.___. (println)", "println"),
  ec="olvidar el punto y coma al final de la instrucción"),
K("Comentarios",
  d="texto que el compilador ignora",
  u="explicar el código",
  mas="// comenta una línea y /* ... */ varias. /** ... */ es un comentario de documentación (Javadoc).",
  k=["Los comentarios son ignorados al compilar.", "// comenta una sola línea.", "/** */ crea documentación Javadoc."],
  sit="Quieres dejar una nota que no afecte al programa. ¿Qué escribes?",
  cod="""public class Main {
    public static void main(String[] args) {
        // comentario de una línea
        /* comentario
           de varias líneas */
        System.out.println("Los comentarios no se ejecutan");
    }
}""",
  out="Los comentarios no se ejecutan",
  h="muestra un mensaje; los comentarios se ignoran",
  pr=("El comentario de una línea empieza con ___. (//)", "//"),
  ec="dejar un /* sin cerrar"),
K("Variables",
  d="espacio con nombre que guarda un valor",
  u="almacenar datos que el programa usa",
  mas="En Java hay que declarar el tipo antes del nombre: tipo nombre = valor;. Java es de tipado estático: el tipo de una variable no cambia.",
  k=["Una variable guarda un valor con nombre.", "Hay que declarar su tipo.", "El tipo de una variable no cambia."],
  sit="Necesitas recordar la edad del usuario para usarla después. ¿Qué declaras?",
  cod="""public class Main {
    public static void main(String[] args) {
        int edad = 20;          // tipo nombre = valor
        edad = edad + 1;
        System.out.println(edad);
    }
}""",
  out="21",
  h="guarda una edad y le suma uno",
  pr=("Antes del nombre de una variable se escribe su ___. (tipo)", "tipo"),
  ec="asignar un texto a una variable declarada como int",
  err=("""public class Main {
    public static void main(String[] args) {
        int edad = "veinte";
        System.out.println(edad);
    }
}""", 3, "edad es int y no puede guardar un texto.")),
K("int",
  d="tipo para guardar números enteros",
  u="contar y calcular con valores sin decimales",
  mas="Un int ocupa 4 bytes y llega hasta unos 2.147 millones. La división entre dos int descarta los decimales.",
  k=["int guarda números enteros.", "La división entre int descarta los decimales.", "Un int ocupa 4 bytes."],
  sit="Debes guardar la cantidad de alumnos de una clase. ¿Qué tipo usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int alumnos = 25;
        System.out.println(alumnos / 2);   // 12: se pierden los decimales
    }
}""",
  out="12",
  h="divide un entero entre 2 y pierde los decimales",
  pr=("El tipo para números enteros es ___. (3 letras)", "int"),
  ec="esperar decimales al dividir dos int"),
K("double",
  d="tipo para guardar números con decimales",
  u="trabajar con medidas y cálculos no enteros",
  mas="double tiene 64 bits y buena precisión. float es de 32 bits y menos preciso. Los literales decimales como 2.5 son double por defecto.",
  k=["double guarda números decimales.", "double tiene más precisión que float.", "2.5 es un double por defecto."],
  sit="Debes guardar la altura de una persona con decimales. ¿Qué tipo usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        double altura = 1.75;
        System.out.println(altura * 2);
    }
}""",
  out="3.5",
  h="duplica una altura decimal",
  pr=("El tipo decimal más usado es ___. (6 letras)", "double"),
  ec="guardar un decimal en un int"),
K("boolean",
  d="tipo con solo dos valores: true y false",
  u="representar condiciones verdaderas o falsas",
  mas="Las comparaciones dan un boolean. if y while exigen un boolean: no aceptan números como en C.",
  k=["boolean solo admite true o false.", "Las comparaciones devuelven boolean.", "if exige un boolean."],
  sit="Quieres guardar si un usuario está activo (sí o no). ¿Qué tipo usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        boolean activo = true;
        boolean mayor = 20 >= 18;     // resultado de una comparación
        System.out.println(activo + " " + mayor);
    }
}""",
  out="true true",
  h="muestra dos valores booleanos",
  pr=("El tipo que solo vale true o false es ___. (7 letras)", "boolean"),
  ec="usar un número como condición de un if"),
K("char",
  d="tipo que guarda un solo carácter",
  u="trabajar con letras sueltas",
  mas="Un char se escribe entre comillas simples, como 'A'. Internamente es un número Unicode, por eso se puede sumar o comparar.",
  k=["char guarda un solo carácter.", "Se escribe entre comillas simples.", "Internamente es un número Unicode."],
  sit="Quieres guardar la inicial de un nombre. ¿Qué tipo usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        char letra = 'A';
        System.out.println(letra);
        System.out.println((int) letra);   // código de la letra
    }
}""",
  out="A\n65",
  h="muestra una letra y su código",
  pr=("Un solo carácter se guarda en una variable ___. (char)", "char"),
  ec="usar comillas dobles para un solo char"),
K("String",
  d="clase para guardar y manejar texto",
  u="trabajar con nombres, mensajes y palabras",
  mas="Un String va entre comillas dobles. Es inmutable: sus métodos devuelven un texto nuevo. length() da la longitud y + concatena.",
  k=["String guarda texto.", "Se escribe entre comillas dobles.", "Un String es inmutable."],
  sit="Debes guardar el nombre de un usuario. ¿Qué tipo usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        String nombre = "Ana";
        System.out.println(nombre.length());          // 3
        System.out.println("Hola " + nombre);         // concatenar
    }
}""",
  out="3\nHola Ana",
  h="mide un texto y lo concatena con otro",
  pr=("El tipo para guardar texto es ___. (6 letras)", "string"),
  ec="comparar Strings con == en lugar de equals"),
K("final",
  d="palabra que impide cambiar el valor de una variable",
  u="declarar constantes",
  mas="Una variable final solo se asigna una vez. Por convención las constantes se escriben en MAYÚSCULAS.",
  k=["final impide reasignar una variable.", "Se asigna una sola vez.", "Las constantes se escriben en mayúsculas por convención."],
  sit="El valor de pi no debe cambiar jamás. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        final double PI = 3.14;    // no se puede reasignar
        System.out.println(PI * 2);
    }
}""",
  out="6.28",
  h="usa una constante PI en un cálculo",
  pr=("La palabra que impide reasignar una variable es ___. (5 letras)", "final"),
  ec="intentar reasignar una variable final",
  err=("""public class Main {
    public static void main(String[] args) {
        final int n = 1;
        n = 2;
    }
}""", 4, "n es final y no se puede reasignar.")),
K("Operadores aritméticos",
  d="símbolos + - * / que realizan cálculos",
  u="hacer operaciones matemáticas",
  mas="* y / se evalúan antes que + y -. Los paréntesis cambian el orden. La división entre enteros devuelve un entero.",
  k=["+, -, * y / son operadores aritméticos.", "* y / van antes que + y -.", "Los paréntesis cambian el orden."],
  sit="Debes calcular 3 productos a 5 euros más 2 de envío. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int total = 3 * 5 + 2;            // primero 3*5
        System.out.println(total);
        System.out.println(3 * (5 + 2));
    }
}""",
  out="17\n21",
  h="calcula un total con multiplicación y suma",
  pr=("El operador que multiplica es ___. (un signo)", "*"),
  ec="olvidar la precedencia de * sobre +"),
K("Resto %",
  d="operador que devuelve el resto de una división",
  u="saber si un número es par o múltiplo de otro",
  mas="7 % 3 vale 1. Un número es par cuando n % 2 == 0. También funciona con decimales en Java.",
  k=["% devuelve el resto de una división.", "n % 2 == 0 indica que n es par.", "Sirve para comprobar múltiplos."],
  sit="Necesitas saber si un número es par. ¿Qué operador usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        System.out.println(7 % 3);           // 1
        System.out.println(10 % 2 == 0);     // true: es par
    }
}""",
  out="1\ntrue",
  h="calcula un resto y comprueba si 10 es par",
  pr=("El operador del resto de una división es ___. (%)", "%"),
  ec="confundir % con una división"),
K("Incremento ++ y --",
  d="operadores que suman o restan uno a una variable",
  u="contar de uno en uno de forma corta",
  mas="i++ equivale a i = i + 1 e i-- a i = i - 1. Se usan mucho en bucles.",
  k=["++ suma uno a una variable.", "-- resta uno a una variable.", "i++ equivale a i = i + 1."],
  sit="Quieres sumar uno a un contador escribiendo lo menos posible. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int i = 5;
        i++;                       // 6
        i--;                       // 5
        i++;                       // 6
        System.out.println(i);
    }
}""",
  out="6",
  h="suma y resta uno a una variable",
  pr=("El operador que suma uno a una variable es ___. (++)", "++"),
  ec="confundir i++ con ++i dentro de una expresión"),
K("Operadores de comparación",
  d="símbolos como ==, !=, <, > que comparan valores",
  u="construir condiciones",
  mas="Devuelven un boolean. Para comparar igualdad se usa ==; un solo = asigna. Los Strings se comparan con equals, no con ==.",
  k=["Los operadores de comparación devuelven boolean.", "== compara igualdad.", "Un solo = asigna."],
  sit="Quieres saber si la edad es mayor o igual a 18. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int edad = 20;
        System.out.println(edad >= 18);    // true
        System.out.println(edad == 30);    // false
    }
}""",
  out="true\nfalse",
  h="compara una edad con dos valores",
  pr=("Para comprobar igualdad de números se usa ___. (==)", "=="),
  ec="usar = en lugar de == en una condición"),
K("Operadores lógicos",
  d="operadores &&, || y ! que combinan condiciones",
  u="comprobar varias condiciones a la vez",
  mas="&& exige que ambas condiciones sean ciertas, || que alguna lo sea y ! invierte el resultado. Se evalúan de izquierda a derecha.",
  k=["&& exige que se cumplan ambas condiciones.", "|| acepta que se cumpla alguna.", "! invierte una condición."],
  sit="Quieres comprobar que la edad sea mayor de 17 y menor de 65. ¿Qué operador usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int edad = 30;
        System.out.println(edad > 17 && edad < 65);   // true
        System.out.println(edad < 10 || edad > 20);   // true
        System.out.println(!(edad > 20));             // false
    }
}""",
  out="true\ntrue\nfalse",
  h="combina condiciones con y, o, no",
  pr=("El operador lógico «y» es ___. (&&)", "&&"),
  ec="usar & en lugar de && sin querer"),
K("if y else",
  d="estructura que ejecuta código según una condición",
  u="tomar decisiones",
  mas="if ejecuta su bloque si la condición es true. else cubre el caso contrario y else if encadena varias.",
  k=["if ejecuta un bloque si la condición es true.", "else cubre el caso contrario.", "else if encadena condiciones."],
  sit="Debes mostrar «mayor» o «menor» según la edad. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int edad = 20;
        if (edad >= 18) {
            System.out.println("Mayor de edad");
        } else {
            System.out.println("Menor de edad");
        }
    }
}""",
  out="Mayor de edad",
  h="muestra si la persona es mayor o menor",
  pr=("La palabra del caso contrario de un if es ___. (else)", "else"),
  ec="olvidar que la condición debe ser boolean",
  err=("""public class Main {
    public static void main(String[] args) {
        int x = 1;
        if (x) { System.out.println("uno"); }
    }
}""", 4, "if necesita un boolean; x es int. Usa x == 1.")),
K("switch",
  d="estructura que elige entre varios casos",
  u="reemplazar muchos if encadenados",
  mas="switch compara un valor con cada case. Cada caso cierra con break; sin él continúa en el siguiente. default cubre el resto.",
  k=["switch elige un caso según un valor.", "break evita seguir con el siguiente caso.", "default cubre los valores no previstos."],
  sit="Según un número de día debes mostrar su nombre. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int dia = 2;
        switch (dia) {
            case 1: System.out.println("Lunes"); break;
            case 2: System.out.println("Martes"); break;   // break evita seguir
            default: System.out.println("Otro día");
        }
    }
}""",
  out="Martes",
  h="muestra el nombre de un día según su número",
  pr=("La palabra que evita pasar al siguiente caso es ___. (break)", "break"),
  ec="olvidar break y ejecutar varios casos"),
K("Operador ternario",
  d="operador ?: que elige entre dos valores según una condición",
  u="escribir un if corto dentro de una expresión",
  mas="Se escribe condición ? valorSiCierto : valorSiFalso. Es útil para asignaciones simples, pero no conviene anidarlo mucho.",
  k=["El ternario elige entre dos valores.", "Se escribe condición ? a : b.", "Es un if compacto dentro de una expresión."],
  sit="Quieres asignar «mayor» o «menor» a un texto en una sola línea. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int edad = 20;
        String r = edad >= 18 ? "mayor" : "menor";   // condición ? si : no
        System.out.println(r);
    }
}""",
  out="mayor",
  h="asigna mayor o menor con un operador ternario",
  pr=("El operador ternario usa los signos ? y ___. (:)", ":"),
  ec="anidar muchos ternarios y volverlos ilegibles"),
]
