"""Java · Etapa 2: Bucles, métodos, arrays y colecciones."""
from ..generador import K

LISTA = [
K("Bucle while",
  d="bucle que repite mientras una condición sea verdadera",
  u="repetir sin saber cuántas veces",
  mas="La condición se evalúa antes de cada vuelta. Algo dentro del bucle debe cambiarla o nunca terminará.",
  k=["while repite mientras la condición sea verdadera.", "La condición se evalúa antes de cada vuelta.", "Sin cambios en la condición, el bucle es infinito."],
  sit="Debes seguir repitiendo hasta que ocurra algo, sin saber cuántas veces. ¿Qué bucle usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int n = 3;
        while (n > 0) {
            System.out.println("n = " + n);
            n--;                       // cambia la condición
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
  cod="""public class Main {
    public static void main(String[] args) {
        int i = 10;
        do {
            System.out.println("i = " + i);   // se ejecuta aunque la condición sea falsa
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
  cod="""public class Main {
    public static void main(String[] args) {
        for (int i = 1; i <= 5; i++) {      // inicio; condición; paso
            System.out.print(i + " ");
        }
        System.out.println();
    }
}""",
  out="1 2 3 4 5 ",
  h="muestra los números del 1 al 5",
  pr=("El bucle con inicio, condición y paso es ___. (3 letras)", "for"),
  ec="usar <= cuando se quería < y pasarse una vuelta"),
K("for mejorado",
  d="bucle que recorre directamente los elementos de un array o colección",
  u="recorrer listas sin manejar índices",
  mas="La forma es for (tipo x : coleccion). Es más corto y seguro que un for con índice cuando solo necesitas leer los elementos.",
  k=["El for mejorado recorre los elementos directamente.", "No necesita índice.", "Funciona con arrays y colecciones."],
  sit="Quieres recorrer todos los elementos de un array sin escribir índices. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int[] notas = {7, 9, 8};
        for (int n : notas) {          // for-each
            System.out.println(n);
        }
    }
}""",
  out="7\n9\n8",
  h="recorre un array mostrando cada nota",
  pr=("El for que recorre elementos usa los dos puntos ___. (:)", ":"),
  ec="intentar modificar el array a través de la variable del for mejorado"),
K("break y continue",
  d="instrucciones que salen del bucle o saltan a la siguiente vuelta",
  u="controlar la ejecución de un bucle",
  mas="break termina el bucle más interno. continue omite el resto de la vuelta actual y pasa a la siguiente.",
  k=["break sale del bucle.", "continue salta a la siguiente vuelta.", "Ambos afectan al bucle más interno."],
  sit="Quieres mostrar números del 1 al 5 sin el 3 y parar al llegar al 5. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        for (int i = 1; i <= 10; i++) {
            if (i == 3) continue;     // salta el 3
            if (i == 5) break;        // sale en el 5
            System.out.print(i + " ");
        }
        System.out.println();
    }
}""",
  out="1 2 4 ",
  h="muestra números saltando el 3 y parando en el 5",
  pr=("La instrucción que sale de un bucle es ___. (5 letras)", "break"),
  ec="confundir break con continue"),
K("Métodos",
  d="bloque con nombre que realiza una tarea reutilizable",
  u="no repetir código y organizar el programa",
  mas="Un método tiene modificadores, tipo de retorno, nombre, parámetros y cuerpo. Se llama escribiendo su nombre con paréntesis. Los métodos estáticos se llaman desde main sin crear objetos.",
  k=["Un método agrupa código reutilizable.", "Se llama por su nombre.", "Los métodos static se llaman sin crear un objeto."],
  sit="Repites el mismo cálculo en varios lugares. ¿Qué haces?",
  cod="""public class Main {
    static void saludar() {              // método sin parámetros ni retorno
        System.out.println("Hola desde un método");
    }

    public static void main(String[] args) {
        saludar();
        saludar();
    }
}""",
  out="Hola desde un método\nHola desde un método",
  h="llama dos veces a un método que saluda",
  pr=("Un método se llama escribiendo su nombre y ___. (paréntesis)", "parentesis", "paréntesis"),
  ec="definir un método y no llamarlo"),
K("Parámetros",
  d="valores que un método recibe para trabajar",
  u="hacer métodos que sirvan con distintos datos",
  mas="Cada parámetro se declara con su tipo. Al llamar se pasan los argumentos en el mismo orden. En Java los tipos básicos se pasan por copia.",
  k=["Los parámetros se declaran con su tipo.", "Los argumentos se pasan en el mismo orden.", "Los tipos básicos se pasan por copia."],
  sit="Quieres que un método salude al nombre que le indiques. ¿Qué necesita?",
  cod="""public class Main {
    static void saludar(String nombre, int veces) {   // dos parámetros
        for (int i = 0; i < veces; i++) System.out.println("Hola " + nombre);
    }

    public static void main(String[] args) {
        saludar("Ana", 2);
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
  cod="""public class Main {
    static int sumar(int a, int b) {
        return a + b;                  // devuelve el resultado
    }

    public static void main(String[] args) {
        int total = sumar(2, 3);
        System.out.println(total);
    }
}""",
  out="5",
  h="suma dos números con un método que devuelve el resultado",
  pr=("La instrucción que devuelve un valor es ___. (6 letras)", "return"),
  ec="olvidar el return en un método que debe devolver algo",
  err=("""public class Main {
    static int doble(int n) {
        n * 2;
    }
}""", 3, "Falta return: el método debe devolver n * 2.")),
K("Sobrecarga de métodos",
  d="varios métodos con el mismo nombre y distintos parámetros",
  u="usar un mismo nombre para operaciones parecidas",
  mas="Java elige la versión según el número y tipo de argumentos. El tipo de retorno por sí solo no distingue métodos.",
  k=["La sobrecarga permite métodos con igual nombre.", "Deben diferir en sus parámetros.", "Java elige según los argumentos."],
  sit="Quieres un método «mostrar» que funcione con enteros y con textos. ¿Qué usas?",
  cod="""public class Main {
    static void mostrar(int n) { System.out.println("int " + n); }
    static void mostrar(String s) { System.out.println("texto " + s); }

    public static void main(String[] args) {
        mostrar(5);
        mostrar("hola");
    }
}""",
  out="int 5\ntexto hola",
  h="llama a la versión de mostrar adecuada para cada tipo",
  pr=("Varios métodos con el mismo nombre es ___. (sobrecarga)", "sobrecarga"),
  ec="intentar sobrecargar cambiando solo el tipo de retorno"),
K("Arrays",
  d="conjunto de elementos del mismo tipo y tamaño fijo",
  u="guardar varios valores bajo un nombre",
  mas="Se declaran con new tipo[tamaño] o con llaves {..}. El primer índice es 0 y length da el tamaño. Salirse de rango lanza ArrayIndexOutOfBoundsException.",
  k=["Un array tiene tamaño fijo.", "El primer índice es 0.", "length da el tamaño del array."],
  sit="Debes guardar exactamente cinco notas con tamaño conocido. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int[] notas = {7, 9, 8};
        notas[1] = 10;
        System.out.println(notas[0] + " " + notas[1]);
        System.out.println(notas.length);
    }
}""",
  out="7 10\n3",
  h="guarda tres notas y cambia una",
  pr=("El primer elemento de un array tiene índice ___. (0)", "0", "cero"),
  ec="acceder a un índice fuera del array",
  err=("""public class Main {
    public static void main(String[] args) {
        int[] a = {1, 2, 3};
        System.out.println(a[3]);
    }
}""", 4, "El último índice válido es 2: a[3] lanza ArrayIndexOutOfBoundsException.")),
K("Recorrer arrays",
  d="visitar cada elemento de un array con un bucle",
  u="calcular totales, buscar y mostrar datos",
  mas="Se usa un for con índice de 0 a length-1, o un for mejorado. Con índice puedes saber la posición y modificar elementos.",
  k=["Se recorre un array con un bucle.", "El índice va de 0 a length-1.", "length da el número de elementos."],
  sit="Quieres sumar todas las notas de un array. ¿Qué haces?",
  cod="""public class Main {
    public static void main(String[] args) {
        int[] notas = {7, 9, 8};
        int suma = 0;
        for (int i = 0; i < notas.length; i++) {
            suma += notas[i];
        }
        System.out.println(suma);
    }
}""",
  out="24",
  h="suma todos los elementos de un array",
  pr=("Un array de n elementos se recorre con índices de 0 a ___. (n-1)", "n-1", "n - 1"),
  ec="recorrer hasta length en lugar de length-1"),
K("Arrays bidimensionales",
  d="arrays de arrays con filas y columnas",
  u="guardar tablas de datos",
  mas="Se declaran como int[][] y se accede con m[fila][columna]. Se recorren con dos bucles anidados.",
  k=["Una matriz es un array de arrays.", "Se accede con dos índices.", "Se recorre con dos bucles anidados."],
  sit="Debes guardar una tabla de 2 filas y 3 columnas. ¿Qué declaras?",
  cod="""public class Main {
    public static void main(String[] args) {
        int[][] m = {{1, 2, 3}, {4, 5, 6}};
        System.out.println(m[1][2]);        // fila 1, columna 2
        System.out.println(m.length);       // 2 filas
    }
}""",
  out="6\n2",
  h="guarda una tabla de 2x3 y muestra datos de ella",
  pr=("Una matriz se accede con dos ___. (índices)", "indices", "índices"),
  ec="intercambiar fila y columna al acceder"),
K("Métodos de String",
  d="métodos para consultar y transformar texto",
  u="trabajar con cadenas con facilidad",
  mas="length(), charAt(i), substring(a, b), indexOf(texto), toUpperCase(), equals() y contains() son los más usados. Como String es inmutable, devuelven un texto nuevo.",
  k=["length() da la longitud.", "substring() extrae una parte.", "Los métodos de String devuelven un texto nuevo."],
  sit="Quieres extraer una parte de un texto y pasarlo a mayúsculas. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        String s = "Hola mundo";
        System.out.println(s.substring(0, 4));      // Hola
        System.out.println(s.toUpperCase());
        System.out.println(s.indexOf("mundo"));     // 5
    }
}""",
  out="Hola\nHOLA MUNDO\n5",
  h="extrae, transforma y busca en un texto",
  pr=("El método que extrae una parte de un String es ___. (substring)", "substring"),
  ec="creer que toUpperCase modifica el String original"),
K("StringBuilder",
  d="clase para construir textos modificables de forma eficiente",
  u="concatenar muchos textos sin crear objetos de más",
  mas="Concatenar con + dentro de un bucle crea muchos Strings. StringBuilder los va acumulando con append y al final se obtiene el resultado con toString().",
  k=["StringBuilder construye textos modificables.", "append añade texto al final.", "toString() devuelve el resultado."],
  sit="Debes armar un texto largo uniendo cientos de trozos en un bucle. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= 3; i++) {
            sb.append(i).append(",");     // append añade al final
        }
        System.out.println(sb.toString());
    }
}""",
  out="1,2,3,",
  h="construye un texto con números separados por comas",
  pr=("La clase para construir textos modificables es ___. (StringBuilder)", "stringbuilder"),
  ec="concatenar con + dentro de un bucle largo"),
K("Math",
  d="clase con funciones matemáticas estáticas",
  u="hacer cálculos como potencias, raíces y redondeos",
  mas="Math.sqrt, Math.pow, Math.abs, Math.max, Math.min y Math.round no necesitan crear objetos: se llaman con Math.nombre().",
  k=["Math ofrece funciones matemáticas estáticas.", "No se crea un objeto Math.", "Math.sqrt calcula la raíz cuadrada."],
  sit="Necesitas calcular una raíz cuadrada y una potencia. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        System.out.println(Math.sqrt(81));     // 9.0
        System.out.println(Math.pow(2, 10));   // 1024.0
        System.out.println(Math.max(3, 7));    // 7
    }
}""",
  out="9.0\n1024.0\n7",
  h="calcula una raíz, una potencia y un máximo",
  pr=("La clase de funciones matemáticas es ___. (Math)", "math"),
  ec="olvidar que sqrt y pow devuelven double"),
K("Scanner",
  d="clase para leer datos de una fuente de texto",
  u="leer números y palabras",
  mas="new Scanner(System.in) lee del teclado. También puede leer de un String. nextInt, nextDouble y next leen cada valor, y nextLine lee una línea.",
  k=["Scanner lee datos de una fuente.", "nextInt lee un entero.", "Se puede usar con el teclado o con un texto."],
  sit="Quieres leer dos números que escribe el usuario. ¿Qué usas?",
  cod="""import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner("10 20");   // en un programa real: System.in
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}""",
  out="30",
  h="lee dos números de un texto y los suma",
  pr=("La clase para leer datos es ___. (Scanner)", "scanner"),
  ec="olvidar importar java.util.Scanner"),
K("ArrayList",
  d="lista que crece dinámicamente",
  u="guardar colecciones cuyo tamaño cambia",
  mas="ArrayList<tipo> es un array que crece solo. Se importa de java.util y se usa con add, get y size. Solo guarda objetos, por eso se usa Integer en lugar de int.",
  k=["ArrayList es una lista que crece.", "add añade, get lee y size cuenta.", "Solo guarda objetos, como Integer."],
  sit="No sabes cuántos elementos tendrá tu lista y debe crecer. ¿Qué usas?",
  cod="""import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        ArrayList<String> nombres = new ArrayList<>();
        nombres.add("Ana");
        nombres.add("Luis");
        System.out.println(nombres.size() + " " + nombres.get(1));
    }
}""",
  out="2 Luis",
  h="añade dos nombres a una lista y consulta datos",
  pr=("La lista que crece dinámicamente es ___. (ArrayList)", "arraylist"),
  ec="usar un array normal cuando el tamaño cambia"),
K("Operaciones de lista",
  d="métodos como remove y contains para manipular una lista",
  u="quitar elementos y comprobar si existen",
  mas="remove elimina por posición o por valor, contains comprueba si un valor está, isEmpty indica si está vacía y indexOf da la posición.",
  k=["remove elimina un elemento.", "contains comprueba si un valor está.", "isEmpty indica si la lista está vacía."],
  sit="Quieres saber si un nombre está en la lista y quitarlo. ¿Qué usas?",
  cod="""import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        ArrayList<String> l = new ArrayList<>();
        l.add("Ana"); l.add("Luis");
        System.out.println(l.contains("Ana"));   // true
        l.remove("Ana");
        System.out.println(l);                   // [Luis]
    }
}""",
  out="true\n[Luis]",
  h="comprueba si un nombre está y lo elimina",
  pr=("El método que comprueba si un valor está en la lista es ___. (contains)", "contains"),
  ec="quitar elementos mientras recorres la lista con un for-each"),
K("HashMap",
  d="colección que asocia claves con valores",
  u="buscar valores a partir de una clave",
  mas="HashMap<K, V> guarda pares clave-valor. put añade o reemplaza, get consulta y containsKey comprueba si existe una clave. No garantiza el orden.",
  k=["HashMap asocia claves con valores.", "put añade y get consulta.", "No garantiza el orden de los elementos."],
  sit="Quieres guardar la edad de cada persona buscándola por su nombre. ¿Qué usas?",
  cod="""import java.util.HashMap;

public class Main {
    public static void main(String[] args) {
        HashMap<String, Integer> edades = new HashMap<>();
        edades.put("Ana", 20);
        edades.put("Luis", 25);
        System.out.println(edades.get("Luis"));          // 25
        System.out.println(edades.containsKey("Eva"));   // false
    }
}""",
  out="25\nfalse",
  h="guarda edades por nombre y consulta datos",
  pr=("La colección clave-valor es ___. (HashMap)", "hashmap"),
  ec="suponer que HashMap conserva el orden de inserción"),
K("Convertir texto a número",
  d="métodos como Integer.parseInt que pasan un texto a número",
  u="usar como número un dato recibido como texto",
  mas="Integer.parseInt convierte a int y Double.parseDouble a double. Si el texto no es un número válido lanzan NumberFormatException.",
  k=["Integer.parseInt convierte texto a int.", "Double.parseDouble convierte texto a double.", "Un texto inválido lanza NumberFormatException."],
  sit="Tienes el texto «123» y necesitas sumarlo como número. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int n = Integer.parseInt("123") + 1;
        System.out.println(n);                  // 124
        System.out.println(String.valueOf(n).length());   // 3
    }
}""",
  out="124\n3",
  h="convierte un texto en número, lo incrementa y mide su texto",
  pr=("El método que convierte un texto a int es Integer.___. (parseInt)", "parseint"),
  ec="usar parseInt con un texto no numérico sin controlar el error"),
]
