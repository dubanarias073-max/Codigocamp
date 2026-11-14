"""Java · Etapa 5: Java moderno y profesional."""
from ..generador import K

LISTA = [
K("Paquetes e imports",
  d="carpetas lógicas que agrupan clases y la directiva para usarlas",
  u="organizar el código y evitar choques de nombres",
  mas="package declara a qué paquete pertenece la clase. import trae clases de otros paquetes, como java.util.List. java.lang se importa solo.",
  k=["package agrupa las clases.", "import trae clases de otros paquetes.", "java.lang se importa automáticamente."],
  sit="Tu proyecto tiene muchas clases y dos se llaman igual en módulos distintos. ¿Qué evita el conflicto?",
  cod="""import java.util.List;      // import de otro paquete

public class Main {
    public static void main(String[] args) {
        List<String> l = List.of("a", "b");
        System.out.println(l.size());
    }
}""",
  out="2",
  h="importa List de java.util y la usa",
  pr=("La palabra que trae clases de otro paquete es ___. (import)", "import"),
  ec="olvidar el import de una clase de java.util"),
K("Varargs",
  d="parámetro que acepta una cantidad variable de argumentos",
  u="escribir métodos con un número libre de argumentos",
  mas="Se escribe con tres puntos: int... numeros. Dentro del método se usa como un array. Debe ser el último parámetro.",
  k=["Varargs acepta una cantidad variable de argumentos.", "Se escribe con tres puntos.", "Dentro del método es un array."],
  sit="Quieres un método que sume cualquier cantidad de números. ¿Qué usas?",
  cod="""public class Main {
    static int sumar(int... nums) {          // varargs
        int s = 0;
        for (int n : nums) s += n;
        return s;
    }

    public static void main(String[] args) {
        System.out.println(sumar(1, 2, 3, 4));
    }
}""",
  out="10",
  h="suma cualquier cantidad de números",
  pr=("Un parámetro de cantidad variable se escribe con ___ puntos. (3)", "3", "tres"),
  ec="poner el parámetro varargs antes de otros parámetros"),
K("var",
  d="palabra que deja al compilador deducir el tipo de una variable local",
  u="escribir menos en tipos largos",
  mas="Desde Java 10, var x = 5; deduce que x es int. El tipo sigue siendo fijo y la variable debe inicializarse. Solo vale para variables locales.",
  k=["var deduce el tipo de una variable local.", "La variable debe inicializarse.", "El tipo deducido no cambia."],
  sit="Un tipo es larguísimo y el compilador puede deducirlo del valor. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        var n = 10;              // int
        var s = "hola";          // String
        System.out.println(n + s.length());
    }
}""",
  out="14",
  h="deja que el compilador deduzca los tipos",
  pr=("La palabra que deduce el tipo local es ___. (var)", "var"),
  ec="usar var sin inicializar la variable"),
K("Bloques de texto",
  d="textos de varias líneas entre tres comillas dobles",
  u="escribir textos largos como JSON o SQL sin escapes",
  mas="Un text block empieza y termina con tres comillas dobles. Conserva los saltos de línea y elimina la sangría común. Disponible desde Java 15.",
  k=["Un text block usa tres comillas dobles.", "Conserva los saltos de línea.", "Elimina la sangría común."],
  sit="Debes escribir un texto de varias líneas sin llenar el código de \\n y escapes. ¿Qué usas?",
  cod='''public class Main {
    public static void main(String[] args) {
        String t = """
            Hola
            mundo""";
        System.out.println(t);
    }
}''',
  out="Hola\nmundo",
  h="muestra un texto de varias líneas con un bloque de texto",
  pr=("Un bloque de texto usa ___ comillas dobles. (3)", "3", "tres"),
  ec="olvidar que el bloque de texto empieza en la línea siguiente a las comillas"),
K("Switch como expresión",
  d="switch que devuelve un valor con flechas ->",
  u="elegir un valor según un caso sin break",
  mas="Con -> cada caso devuelve un valor y no hace falta break. Se puede asignar a una variable. default cubre el resto.",
  k=["El switch moderno usa flechas ->.", "Devuelve un valor.", "No necesita break."],
  sit="Quieres asignar el nombre de un día según su número sin escribir break. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        int dia = 2;
        String nombre = switch (dia) {
            case 1 -> "Lunes";
            case 2 -> "Martes";
            default -> "Otro";
        };
        System.out.println(nombre);
    }
}""",
  out="Martes",
  h="asigna el nombre de un día con un switch moderno",
  pr=("Los casos del switch moderno usan la flecha ___. (->)", "->"),
  ec="olvidar el punto y coma tras la llave de cierre del switch expresión"),
K("Hilos con Thread",
  d="ejecución de varias tareas a la vez con la clase Thread",
  u="hacer varias cosas en paralelo",
  mas="Se crea un Thread con una tarea, start() lo lanza y join() espera a que termine. Llamar a run() directamente no crea un hilo nuevo.",
  k=["Thread ejecuta una tarea en paralelo.", "start() lanza el hilo.", "join() espera a que termine."],
  sit="Quieres ejecutar una tarea en segundo plano y esperar a que termine. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) throws Exception {
        Thread t = new Thread(() -> System.out.println("tarea en otro hilo"));
        t.start();
        t.join();                       // espera a que termine
        System.out.println("fin");
    }
}""",
  out="tarea en otro hilo\nfin",
  h="ejecuta una tarea en otro hilo y espera a que termine",
  pr=("El método que lanza un hilo es ___(). (start)", "start"),
  ec="llamar a run() en lugar de start()"),
K("Runnable",
  d="interfaz con un método run que representa una tarea",
  u="separar la tarea del hilo que la ejecuta",
  mas="Runnable tiene un único método run. Se puede implementar con una clase o con una lambda y se pasa a un Thread.",
  k=["Runnable representa una tarea.", "Tiene un único método run.", "Se pasa a un Thread para ejecutarla."],
  sit="Quieres definir una tarea reutilizable y decidir después en qué hilo ejecutarla. ¿Qué usas?",
  cod="""class Tarea implements Runnable {
    public void run() { System.out.println("ejecutando tarea"); }
}

public class Main {
    public static void main(String[] args) throws Exception {
        Thread t = new Thread(new Tarea());
        t.start();
        t.join();
    }
}""",
  out="ejecutando tarea",
  h="define una tarea con Runnable y la ejecuta en un hilo",
  pr=("La interfaz que representa una tarea es ___. (Runnable)", "runnable"),
  ec="olvidar implementar el método run"),
K("synchronized",
  d="palabra que impide que dos hilos ejecuten a la vez un bloque",
  u="evitar condiciones de carrera",
  mas="Un método o bloque synchronized solo lo ejecuta un hilo a la vez sobre el mismo objeto. Protege datos compartidos que varios hilos modifican.",
  k=["synchronized permite un solo hilo a la vez.", "Protege datos compartidos.", "Evita condiciones de carrera."],
  sit="Dos hilos suman a la misma variable y los resultados salen mal. ¿Qué usas?",
  cod="""class Contador {
    private int n = 0;
    synchronized void sumar() { n++; }     // un hilo a la vez
    int valor() { return n; }
}

public class Main {
    public static void main(String[] args) throws Exception {
        Contador c = new Contador();
        Runnable r = () -> { for (int i = 0; i < 1000; i++) c.sumar(); };
        Thread a = new Thread(r), b = new Thread(r);
        a.start(); b.start();
        a.join(); b.join();
        System.out.println(c.valor());
    }
}""",
  out="2000",
  h="dos hilos suman a un contador protegido con synchronized",
  pr=("La palabra que permite un solo hilo a la vez es ___. (synchronized)", "synchronized"),
  ec="modificar datos compartidos entre hilos sin sincronizar"),
K("ExecutorService",
  d="servicio que gestiona un grupo de hilos para ejecutar tareas",
  u="lanzar tareas sin crear hilos a mano",
  mas="Executors.newFixedThreadPool(n) crea un grupo de hilos. submit envía una tarea y devuelve un Future; get() espera el resultado. Hay que llamar a shutdown() al terminar.",
  k=["ExecutorService gestiona un grupo de hilos.", "submit envía una tarea y devuelve un Future.", "Hay que llamar a shutdown() al terminar."],
  sit="Quieres enviar varias tareas a un grupo de hilos y recoger su resultado. ¿Qué usas?",
  cod="""import java.util.concurrent.*;

public class Main {
    public static void main(String[] args) throws Exception {
        ExecutorService ex = Executors.newFixedThreadPool(2);
        Future<Integer> f = ex.submit(() -> 6 * 7);   // tarea con resultado
        System.out.println(f.get());                    // espera el resultado
        ex.shutdown();
    }
}""",
  out="42",
  h="envía una tarea a un grupo de hilos y recoge el resultado",
  pr=("El método que envía una tarea a un ExecutorService es ___. (submit)", "submit"),
  ec="olvidar llamar a shutdown y dejar el programa sin terminar"),
K("LocalDate",
  d="clase para trabajar con fechas sin hora",
  u="calcular y comparar fechas",
  mas="LocalDate.of(año, mes, día) crea una fecha y LocalDate.now() la de hoy. plusDays, minusMonths y similares devuelven una fecha nueva porque es inmutable.",
  k=["LocalDate representa una fecha sin hora.", "plusDays devuelve una fecha nueva.", "LocalDate es inmutable."],
  sit="Quieres calcular la fecha 20 días después de otra. ¿Qué usas?",
  cod="""import java.time.LocalDate;

public class Main {
    public static void main(String[] args) {
        LocalDate f = LocalDate.of(2026, 1, 15);
        LocalDate despues = f.plusDays(20);       // devuelve una fecha nueva
        System.out.println(despues);
    }
}""",
  out="2026-02-04",
  h="calcula la fecha 20 días después del 15 de enero",
  pr=("La clase para fechas sin hora es ___. (LocalDate)", "localdate"),
  ec="esperar que plusDays modifique la fecha original"),
K("Random",
  d="clase para generar números pseudoaleatorios",
  u="simular azar en juegos y pruebas",
  mas="nextInt(n) devuelve un número entre 0 y n-1. Con una semilla fija la secuencia siempre es la misma, lo que sirve para pruebas.",
  k=["Random genera números pseudoaleatorios.", "nextInt(n) devuelve de 0 a n-1.", "Con semilla fija la secuencia se repite."],
  sit="Necesitas simular la tirada de un dado. ¿Qué usas?",
  cod="""import java.util.Random;

public class Main {
    public static void main(String[] args) {
        Random r = new Random(7);
        int dado = r.nextInt(6) + 1;                 // entre 1 y 6
        System.out.println(dado >= 1 && dado <= 6);
    }
}""",
  out="true",
  h="simula un dado y comprueba que está entre 1 y 6",
  pr=("La clase que genera números aleatorios es ___. (Random)", "random"),
  ec="olvidar sumar 1 y obtener un 0 en el dado"),
K("BigDecimal",
  d="clase para números decimales exactos",
  u="calcular dinero sin errores de redondeo",
  mas="double no representa 0.1 con exactitud. BigDecimal sí, pero se opera con métodos (add, multiply) y se crea desde un texto.",
  k=["BigDecimal ofrece decimales exactos.", "Se opera con métodos como add y multiply.", "Conviene crearlo desde un String."],
  sit="Estás sumando dinero y los decimales de double dan resultados raros. ¿Qué usas?",
  cod="""import java.math.BigDecimal;

public class Main {
    public static void main(String[] args) {
        BigDecimal a = new BigDecimal("0.1");
        BigDecimal b = new BigDecimal("0.2");
        System.out.println(a.add(b));            // 0.3 exacto
    }
}""",
  out="0.3",
  h="suma 0.1 y 0.2 con exactitud",
  pr=("La clase para decimales exactos es ___. (BigDecimal)", "bigdecimal"),
  ec="crear un BigDecimal a partir de un double impreciso"),
K("Archivos con Files",
  d="clase para leer y escribir archivos de forma sencilla",
  u="guardar y recuperar texto en disco",
  mas="Files.writeString escribe un texto y Files.readString lo lee entero. Trabajan con un Path y pueden lanzar IOException.",
  k=["Files lee y escribe archivos.", "Files.writeString guarda un texto.", "Pueden lanzar IOException."],
  sit="Quieres guardar un texto en un archivo y leerlo después. ¿Qué usas?",
  cod="""import java.nio.file.Files;
import java.nio.file.Path;

public class Main {
    public static void main(String[] args) throws Exception {
        Path p = Path.of("datos.txt");
        Files.writeString(p, "hola archivo");
        System.out.println(Files.readString(p));
    }
}""",
  out="hola archivo",
  h="escribe un texto en un archivo y lo lee",
  pr=("La clase para leer y escribir archivos sencillos es ___. (Files)", "files"),
  ec="no manejar la IOException"),
K("Maven y Gradle",
  d="herramientas que gestionan dependencias y compilación del proyecto",
  u="descargar librerías y construir el proyecto con un comando",
  mas="Maven usa pom.xml y Gradle usa build.gradle. Descargan las librerías declaradas, compilan, ejecutan pruebas y generan el paquete final.",
  k=["Maven y Gradle gestionan dependencias.", "Compilan y empaquetan el proyecto.", "Maven usa pom.xml."],
  sit="Tu proyecto usa varias librerías externas y quieres descargarlas y compilar con un comando. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        // pom.xml (Maven) o build.gradle (Gradle) declaran las dependencias
        System.out.println("Construido con Maven o Gradle");
    }
}""",
  out="Construido con Maven o Gradle",
  h="muestra un mensaje; los comentarios describen la configuración",
  pr=("El archivo de configuración de Maven es ___.xml. (pom)", "pom"),
  ec="copiar los archivos .jar de las librerías a mano"),
K("Pruebas con JUnit",
  d="biblioteca para escribir pruebas automáticas",
  u="comprobar que el código funciona al cambiarlo",
  mas="Cada prueba es un método con @Test que usa asserts como assertEquals(esperado, real). Si algo no coincide, la prueba falla.",
  k=["JUnit permite escribir pruebas automáticas.", "Cada prueba se marca con @Test.", "assertEquals compara lo esperado con lo real."],
  sit="Cada vez que cambias código temes romper algo ya hecho. ¿Qué práctica te protege?",
  cod="""public class Main {
    static int doble(int n) { return n * 2; }

    public static void main(String[] args) {
        // en JUnit sería: assertEquals(8, doble(4));
        System.out.println(doble(4) == 8 ? "prueba superada" : "prueba fallida");
    }
}""",
  out="prueba superada",
  h="comprueba que una función da el resultado esperado",
  pr=("La anotación que marca una prueba en JUnit es @___. (Test)", "test"),
  ec="cambiar código sin pruebas que lo respalden"),
K("Javadoc",
  d="comentarios especiales que generan documentación",
  u="documentar clases y métodos",
  mas="Los comentarios /** ... */ con etiquetas como @param y @return generan una página HTML con la herramienta javadoc. Los IDE los muestran al usar el método.",
  k=["Javadoc documenta con comentarios /** */.", "@param y @return describen parámetros y retorno.", "Genera documentación en HTML."],
  sit="Quieres que otros programadores vean la explicación de tu método al usarlo. ¿Qué escribes?",
  cod="""public class Main {
    /**
     * Suma dos números.
     * @param a primer número
     * @param b segundo número
     * @return la suma
     */
    static int sumar(int a, int b) { return a + b; }

    public static void main(String[] args) {
        System.out.println(sumar(2, 3));
    }
}""",
  out="5",
  h="usa un método documentado con Javadoc",
  pr=("La etiqueta que describe un parámetro es @___. (param)", "param"),
  ec="escribir comentarios que repiten lo que dice el código"),
K("JVM y recolector de basura",
  d="máquina virtual que ejecuta el bytecode y libera la memoria sin uso",
  u="entender cómo Java gestiona la memoria",
  mas="Los objetos se crean con new en el montón. El recolector de basura (garbage collector) elimina automáticamente los que ya no tienen referencias. Por eso en Java no hay free ni delete.",
  k=["La JVM ejecuta el bytecode.", "El recolector de basura libera los objetos sin referencias.", "En Java no se libera memoria manualmente."],
  sit="En Java no llamas a free ni delete y la memoria no se llena. ¿Quién libera los objetos?",
  cod="""public class Main {
    public static void main(String[] args) {
        String s = new String("temporal");
        s = null;                          // ya no hay referencias: elegible para el GC
        System.out.println("el recolector liberará el objeto");
    }
}""",
  out="el recolector liberará el objeto",
  h="deja un objeto sin referencias para que lo libere el recolector",
  pr=("El mecanismo que libera objetos sin referencias es el recolector de ___. (basura)", "basura"),
  ec="creer que hay que liberar memoria manualmente en Java"),
K("Inmutabilidad",
  d="objetos cuyo estado no cambia después de crearse",
  u="evitar errores y compartir objetos con seguridad entre hilos",
  mas="Una clase inmutable declara sus atributos private final, no tiene setters y devuelve objetos nuevos al «modificarse». String y LocalDate son inmutables.",
  k=["Un objeto inmutable no cambia tras crearse.", "Sus atributos son private final.", "String es un ejemplo de clase inmutable."],
  sit="Quieres que un objeto pueda compartirse entre hilos sin riesgo de cambios. ¿Qué diseño usas?",
  cod="""final class Punto {
    private final int x, y;                       // no cambian
    Punto(int x, int y) { this.x = x; this.y = y; }
    Punto mover(int dx) { return new Punto(x + dx, y); }   // devuelve uno nuevo
    int x() { return x; }
}

public class Main {
    public static void main(String[] args) {
        Punto p = new Punto(1, 2);
        Punto q = p.mover(5);
        System.out.println(p.x() + " " + q.x());
    }
}""",
  out="1 6",
  h="mueve un punto inmutable devolviendo uno nuevo",
  pr=("Un objeto que no cambia después de crearse es ___. (inmutable)", "inmutable"),
  ec="añadir setters a una clase que debía ser inmutable"),
K("Buenas prácticas",
  d="costumbres para escribir Java claro, seguro y mantenible",
  u="reducir errores y facilitar el trabajo en equipo",
  mas="Usa nombres claros (camelCase para variables y métodos, MayúsculaInicial para clases), programa contra interfaces, evita null, cierra recursos, usa final cuando puedas y mantén los métodos cortos.",
  k=["Conviene usar nombres claros en camelCase.", "Conviene programar contra interfaces.", "Conviene mantener los métodos cortos."],
  sit="Estás revisando código con variables llamadas x1, tmp y datoFinal2 y métodos de 300 líneas. ¿Qué buena práctica aplicarías?",
  cod="""import java.util.List;

public class Main {
    static double promedio(List<Integer> notas) {       // nombre claro, método corto
        int suma = 0;
        for (int n : notas) suma += n;
        return (double) suma / notas.size();
    }

    public static void main(String[] args) {
        System.out.println(promedio(List.of(7, 9, 8)));
    }
}""",
  out="8.0",
  h="calcula un promedio con un método claro y corto",
  pr=("En Java las variables y métodos se escriben en ___Case. (camel)", "camel"),
  ec="usar nombres que solo entiende quien los escribió"),
K("Streams y collect",
  d="uso de collect para convertir el resultado de un stream en una colección",
  u="obtener una lista o un texto a partir de un procesamiento",
  mas="Collectors.toList() reúne los elementos en una lista y Collectors.joining(\", \") une textos. toList() directo existe desde Java 16.",
  k=["collect reúne el resultado de un stream.", "Collectors.toList() produce una lista.", "Collectors.joining une textos."],
  sit="Tienes un stream de nombres y quieres un único texto separado por comas. ¿Qué usas?",
  cod="""import java.util.List;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        List<String> n = List.of("ana", "luis");
        String r = n.stream()
                    .map(String::toUpperCase)
                    .collect(Collectors.joining(", "));
        System.out.println(r);
    }
}""",
  out="ANA, LUIS",
  h="pasa nombres a mayúsculas y los une con comas",
  pr=("El método que reúne el resultado de un stream es ___. (collect)", "collect"),
  ec="olvidar la operación final y no obtener ningún resultado"),
]
