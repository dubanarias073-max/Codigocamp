"""Java · Etapa 4: Excepciones, genéricos y colecciones."""
from ..generador import K

LISTA = [
K("try y catch",
  d="estructura que captura errores sin detener el programa",
  u="manejar fallos de forma controlada",
  mas="El código que puede fallar va en try. Si lanza una excepción, la ejecución salta al catch correspondiente donde se puede mostrar un mensaje o recuperar.",
  k=["try contiene el código que puede fallar.", "catch recibe y maneja la excepción.", "El programa continúa después del catch."],
  sit="Una división puede fallar y no quieres que se caiga todo el programa. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        try {
            int x = 10 / 0;                  // lanza ArithmeticException
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
        System.out.println("El programa continúa");
    }
}""",
  out="Error: / by zero\nEl programa continúa",
  h="captura una división entre cero y sigue ejecutando",
  pr=("El bloque que recibe la excepción es ___. (catch)", "catch"),
  ec="dejar el catch vacío y esconder los errores"),
K("Varios catch",
  d="varios bloques catch para distintos tipos de excepción",
  u="reaccionar de forma distinta según el error",
  mas="Cada catch maneja un tipo. Se evalúan en orden, así que los más específicos van primero. También se pueden agrupar con | en un solo catch.",
  k=["Se pueden escribir varios catch.", "Los más específicos van primero.", "Se pueden agrupar tipos con |."],
  sit="Un mismo código puede fallar por texto inválido o por índice fuera de rango y quieres tratarlos distinto. ¿Qué haces?",
  cod="""public class Main {
    public static void main(String[] args) {
        try {
            Integer.parseInt("abc");
        } catch (NumberFormatException e) {
            System.out.println("No es un número");
        } catch (Exception e) {
            System.out.println("Otro error");
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
  cod="""public class Main {
    public static void main(String[] args) {
        try {
            System.out.println("Intentando");
        } finally {
            System.out.println("Esto se ejecuta siempre");
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
  mas="throw new TipoDeExcepcion(\"mensaje\") crea y lanza el error. A partir de ahí el método termina y la excepción sube hasta que alguien la capture.",
  k=["throw lanza una excepción.", "El método termina al lanzarla.", "La excepción sube hasta que se capture."],
  sit="Un método recibe una edad negativa y debe avisar del error. ¿Qué usas?",
  cod="""public class Main {
    static void validar(int edad) {
        if (edad < 0) throw new IllegalArgumentException("edad negativa");
    }

    public static void main(String[] args) {
        try {
            validar(-5);
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }
    }
}""",
  out="edad negativa",
  h="lanza una excepción por una edad negativa y la captura",
  pr=("La palabra que lanza una excepción es ___. (throw)", "throw"),
  ec="confundir throw con throws"),
K("throws",
  d="palabra en la firma que declara que un método puede lanzar una excepción",
  u="avisar a quien llama de los errores que debe manejar",
  mas="Se escribe después de los paréntesis: void leer() throws IOException. Quien llame al método debe capturar la excepción o declararla también.",
  k=["throws declara las excepciones que puede lanzar un método.", "Va después de los paréntesis.", "Quien llama debe manejarlas o declararlas."],
  sit="Tu método puede lanzar un error comprobado y quieres avisarlo en su firma. ¿Qué usas?",
  cod="""public class Main {
    static void riesgo() throws Exception {
        throw new Exception("fallo declarado");
    }

    public static void main(String[] args) {
        try {
            riesgo();
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }
}""",
  out="fallo declarado",
  h="declara con throws y captura el error",
  pr=("La palabra de la firma que declara excepciones es ___. (throws)", "throws"),
  ec="llamar a un método con throws sin manejar la excepción"),
K("Excepciones propias",
  d="clases que heredan de Exception para errores del programa",
  u="distinguir tus errores de los demás",
  mas="Se crea una clase que extiende Exception (comprobada) o RuntimeException (no comprobada). Permite capturar tu error por separado.",
  k=["Una excepción propia hereda de Exception.", "Permite capturar tu error por separado.", "Extender RuntimeException la hace no comprobada."],
  sit="Quieres un error propio «SaldoInsuficiente» que se pueda capturar por separado. ¿Qué haces?",
  cod="""class SaldoInsuficiente extends Exception {
    SaldoInsuficiente(String msg) { super(msg); }
}

public class Main {
    public static void main(String[] args) {
        try {
            throw new SaldoInsuficiente("saldo insuficiente");
        } catch (SaldoInsuficiente e) {
            System.out.println(e.getMessage());
        }
    }
}""",
  out="saldo insuficiente",
  h="lanza y captura una excepción propia",
  pr=("Una excepción propia hereda de ___. (Exception)", "exception"),
  ec="crear excepciones que no heredan de Exception"),
K("Comprobadas y no comprobadas",
  d="excepciones que el compilador obliga a manejar y las que no",
  u="saber cuándo hay que declarar o capturar un error",
  mas="Las comprobadas (como IOException) deben capturarse o declararse con throws. Las no comprobadas (RuntimeException, como NullPointerException) no obligan a nada y suelen indicar errores de programación.",
  k=["Las excepciones comprobadas obligan a capturar o declarar.", "RuntimeException no es comprobada.", "Las no comprobadas suelen indicar errores de programación."],
  sit="El compilador te obliga a capturar un error al abrir un archivo pero no al dividir entre cero. ¿Por qué?",
  cod="""public class Main {
    public static void main(String[] args) {
        try {
            Object o = null;
            o.toString();                        // NullPointerException: no comprobada
        } catch (NullPointerException e) {
            System.out.println("objeto nulo");
        }
    }
}""",
  out="objeto nulo",
  h="captura una excepción no comprobada por un objeto nulo",
  pr=("Las excepciones que obligan a capturar o declarar son las ___. (comprobadas)", "comprobadas", "checked"),
  ec="capturar RuntimeException para esconder errores de programación"),
K("try-with-resources",
  d="try que cierra automáticamente los recursos al terminar",
  u="evitar olvidar cerrar archivos o conexiones",
  mas="Los recursos se declaran entre paréntesis tras try y deben implementar AutoCloseable. Java llama a close() al salir del bloque, incluso si hay error.",
  k=["try-with-resources cierra los recursos automáticamente.", "Los recursos implementan AutoCloseable.", "close() se llama aunque haya error."],
  sit="Quieres que un recurso se cierre siempre sin escribir un finally. ¿Qué usas?",
  cod="""class Recurso implements AutoCloseable {
    Recurso() { System.out.println("abrir"); }
    public void close() { System.out.println("cerrar"); }
}

public class Main {
    public static void main(String[] args) {
        try (Recurso r = new Recurso()) {      // se cierra solo
            System.out.println("usando");
        }
    }
}""",
  out="abrir\nusando\ncerrar",
  h="abre, usa y cierra un recurso automáticamente",
  pr=("La interfaz que permite cerrar recursos automáticamente es ___. (AutoCloseable)", "autocloseable"),
  ec="olvidar cerrar un recurso que no está en un try-with-resources"),
K("Clases genéricas",
  d="clases que dependen de un tipo parámetro como <T>",
  u="crear estructuras reutilizables para cualquier tipo",
  mas="class Caja<T> guarda un valor de tipo T. Al usarla se indica el tipo: Caja<String>. El compilador comprueba que no mezcles tipos.",
  k=["Una clase genérica recibe un tipo parámetro.", "Se usa como Caja<String>.", "El compilador evita mezclar tipos."],
  sit="Quieres una «caja» que guarde un valor de cualquier tipo con seguridad. ¿Qué defines?",
  cod="""class Caja<T> {
    private T valor;
    Caja(T valor) { this.valor = valor; }
    T ver() { return valor; }
}

public class Main {
    public static void main(String[] args) {
        Caja<String> a = new Caja<>("hola");
        Caja<Integer> b = new Caja<>(42);
        System.out.println(a.ver() + " " + b.ver());
    }
}""",
  out="hola 42",
  h="crea cajas de texto y de entero con la misma clase",
  pr=("Una clase genérica usa un tipo parámetro como ___. (<T>)", "<t>", "t"),
  ec="usar tipos primitivos como int en lugar de Integer en un genérico"),
K("Métodos genéricos",
  d="métodos con parámetros de tipo propios",
  u="operar sobre varios tipos con un solo método",
  mas="Se escribe <T> antes del tipo de retorno: static <T> T primero(List<T> l). Java deduce T a partir de los argumentos.",
  k=["Un método genérico declara <T> antes del retorno.", "Java deduce T de los argumentos.", "Un solo método sirve para muchos tipos."],
  sit="Quieres un método que devuelva el primer elemento de cualquier lista. ¿Qué escribes?",
  cod="""import java.util.List;

public class Main {
    static <T> T primero(List<T> lista) {
        return lista.get(0);
    }

    public static void main(String[] args) {
        System.out.println(primero(List.of(10, 20)));
        System.out.println(primero(List.of("a", "b")));
    }
}""",
  out="10\na",
  h="obtiene el primer elemento de listas de distintos tipos",
  pr=("En un método genérico, <T> se escribe antes del tipo de ___. (retorno)", "retorno"),
  ec="olvidar declarar <T> antes del tipo de retorno"),
K("List",
  d="interfaz de las listas ordenadas con elementos repetibles",
  u="programar contra la interfaz y no contra una implementación",
  mas="Se suele declarar la variable como List y crear un ArrayList o LinkedList. List.of crea una lista inmutable. Permite posiciones, repetidos y orden de inserción.",
  k=["List es una interfaz de listas ordenadas.", "Admite elementos repetidos.", "List.of crea una lista inmutable."],
  sit="Quieres declarar una lista sin atarte a una implementación concreta. ¿Qué tipo usas en la variable?",
  cod="""import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<String> l = new ArrayList<>();     // variable de tipo List
        l.add("a"); l.add("b"); l.add("a");     // admite repetidos
        System.out.println(l);
    }
}""",
  out="[a, b, a]",
  h="usa una lista con elementos repetidos",
  pr=("La interfaz de las listas ordenadas es ___. (List)", "list"),
  ec="declarar la variable con la clase concreta en lugar de la interfaz"),
K("HashSet",
  d="colección de elementos únicos sin orden garantizado",
  u="eliminar repetidos y comprobar pertenencia rápidamente",
  mas="Un Set no admite repetidos: add devuelve false si el elemento ya estaba. contains comprueba rápido si existe. HashSet no garantiza el orden; TreeSet los ordena.",
  k=["Un Set no admite elementos repetidos.", "add devuelve false si ya existía.", "HashSet no garantiza el orden."],
  sit="Tienes una lista con repetidos y quieres quedarte con cada valor una sola vez. ¿Qué usas?",
  cod="""import java.util.HashSet;
import java.util.Set;

public class Main {
    public static void main(String[] args) {
        Set<Integer> s = new HashSet<>();
        s.add(1); s.add(2);
        System.out.println(s.add(2));       // false: ya estaba
        System.out.println(s.size());       // 2
    }
}""",
  out="false\n2",
  h="intenta añadir un repetido a un conjunto",
  pr=("La colección de elementos únicos es ___. (Set)", "set", "hashset"),
  ec="esperar que HashSet conserve el orden de inserción"),
K("Recorrer un Map",
  d="forma de visitar las claves y valores de un Map",
  u="procesar todos los pares clave-valor",
  mas="entrySet() da los pares y se recorre con for mejorado usando getKey() y getValue(). keySet() da las claves y values() los valores.",
  k=["entrySet() da los pares clave-valor.", "getKey() y getValue() leen cada par.", "keySet() da solo las claves."],
  sit="Quieres mostrar cada nombre junto con su edad guardados en un mapa. ¿Qué usas?",
  cod="""import java.util.Map;
import java.util.TreeMap;

public class Main {
    public static void main(String[] args) {
        Map<String, Integer> m = new TreeMap<>();   // TreeMap ordena por clave
        m.put("Luis", 25); m.put("Ana", 20);
        for (Map.Entry<String, Integer> e : m.entrySet()) {
            System.out.println(e.getKey() + "=" + e.getValue());
        }
    }
}""",
  out="Ana=20\nLuis=25",
  h="recorre un mapa mostrando clave y valor",
  pr=("El método que da los pares clave-valor es ___(). (entrySet)", "entryset"),
  ec="suponer un orden en un HashMap"),
K("Iterator",
  d="objeto que recorre una colección y permite quitar elementos con seguridad",
  u="eliminar elementos mientras se recorre",
  mas="hasNext() indica si quedan elementos, next() devuelve el siguiente y remove() quita el último devuelto. Quitar con list.remove dentro de un for-each lanza ConcurrentModificationException.",
  k=["Un Iterator recorre una colección.", "remove() quita el último elemento devuelto.", "list.remove dentro de un for-each lanza una excepción."],
  sit="Quieres eliminar elementos de una lista mientras la recorres sin errores. ¿Qué usas?",
  cod="""import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<Integer> l = new ArrayList<>(List.of(1, 2, 3, 4));
        Iterator<Integer> it = l.iterator();
        while (it.hasNext()) {
            if (it.next() % 2 == 0) it.remove();   // quita los pares
        }
        System.out.println(l);
    }
}""",
  out="[1, 3]",
  h="elimina los números pares de una lista mientras la recorre",
  pr=("El método que indica si quedan elementos es ___(). (hasNext)", "hasnext"),
  ec="quitar elementos de una lista dentro de un for mejorado"),
K("Collections.sort",
  d="método que ordena una lista",
  u="ordenar listas sin escribir tu propio algoritmo",
  mas="Collections.sort(lista) ordena de menor a mayor usando el orden natural de los elementos. También existe lista.sort(null).",
  k=["Collections.sort ordena una lista.", "Usa el orden natural de los elementos.", "Modifica la lista original."],
  sit="Quieres ordenar una lista de números de menor a mayor. ¿Qué usas?",
  cod="""import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<Integer> l = new ArrayList<>(List.of(3, 1, 2));
        Collections.sort(l);
        System.out.println(l);
    }
}""",
  out="[1, 2, 3]",
  h="ordena una lista de menor a mayor",
  pr=("El método que ordena una lista es Collections.___. (sort)", "sort"),
  ec="intentar ordenar una lista inmutable creada con List.of"),
K("Comparable",
  d="interfaz que define el orden natural de una clase",
  u="permitir ordenar objetos propios",
  mas="Una clase implementa Comparable<T> y escribe compareTo, que devuelve un número negativo, cero o positivo según el orden. Con eso sort y TreeSet saben ordenarla.",
  k=["Comparable define el orden natural de una clase.", "compareTo devuelve negativo, cero o positivo.", "Permite usar sort con objetos propios."],
  sit="Quieres que una lista de alumnos se ordene por su nota con Collections.sort. ¿Qué implementas?",
  cod="""import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

class Alumno implements Comparable<Alumno> {
    String nombre; int nota;
    Alumno(String n, int nota) { nombre = n; this.nota = nota; }
    public int compareTo(Alumno o) { return nota - o.nota; }   // por nota
}

public class Main {
    public static void main(String[] args) {
        List<Alumno> l = new ArrayList<>();
        l.add(new Alumno("Ana", 9)); l.add(new Alumno("Luis", 7));
        Collections.sort(l);
        System.out.println(l.get(0).nombre);
    }
}""",
  out="Luis",
  h="ordena alumnos por nota y muestra el de menor nota",
  pr=("El método que define el orden de Comparable es ___. (compareTo)", "compareto"),
  ec="devolver un valor incorrecto en compareTo"),
K("Comparator",
  d="objeto que define un orden alternativo para comparar elementos",
  u="ordenar de varias formas sin cambiar la clase",
  mas="Comparator.comparing(...) crea un criterio a partir de un campo y .reversed() lo invierte. Se pasa a list.sort.",
  k=["Comparator define un orden alternativo.", "comparing crea un criterio desde un campo.", "reversed() invierte el orden."],
  sit="Quieres ordenar nombres por longitud sin modificar la clase String. ¿Qué usas?",
  cod="""import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<String> l = new ArrayList<>(List.of("Carlos", "Ana", "Luis"));
        l.sort(Comparator.comparing(String::length));   // por longitud
        System.out.println(l);
    }
}""",
  out="[Ana, Luis, Carlos]",
  h="ordena nombres por su longitud",
  pr=("El objeto que define un orden alternativo es ___. (Comparator)", "comparator"),
  ec="confundir Comparable con Comparator"),
K("Lambdas",
  d="funciones anónimas que se escriben con ->",
  u="pasar comportamiento corto a un método",
  mas="Se escriben como (parámetros) -> expresión. Funcionan con interfaces que tienen un solo método, como Runnable o Comparator.",
  k=["Una lambda es una función anónima.", "Se escribe con la flecha ->.", "Funciona con interfaces de un solo método."],
  sit="Quieres pasar una acción corta a un método sin crear una clase aparte. ¿Qué usas?",
  cod="""public class Main {
    public static void main(String[] args) {
        Runnable r = () -> System.out.println("Hola desde una lambda");
        r.run();
        java.util.function.Function<Integer, Integer> doble = n -> n * 2;
        System.out.println(doble.apply(21));
    }
}""",
  out="Hola desde una lambda\n42",
  h="define y ejecuta dos funciones lambda",
  pr=("El símbolo de una lambda es ___. (->)", "->"),
  ec="usar una lambda con una interfaz de varios métodos"),
K("Streams",
  d="API para procesar colecciones con filtros y transformaciones encadenadas",
  u="escribir procesamientos de datos de forma declarativa",
  mas="Se crean con lista.stream(). Operaciones como filter, map y sum se encadenan. Las operaciones finales como collect o sum producen el resultado. El stream no modifica la lista original.",
  k=["Un stream procesa colecciones con operaciones encadenadas.", "filter y map son operaciones intermedias.", "El stream no modifica la lista original."],
  sit="Quieres quedarte con los pares de una lista, elevarlos al cuadrado y sumarlos. ¿Qué usas?",
  cod="""import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<Integer> v = List.of(1, 2, 3, 4, 5, 6);
        int total = v.stream()
                     .filter(n -> n % 2 == 0)      // 2, 4, 6
                     .mapToInt(n -> n * n)          // 4, 16, 36
                     .sum();
        System.out.println(total);
    }
}""",
  out="56",
  h="filtra pares, los eleva al cuadrado y los suma",
  pr=("El método que se queda con los elementos que cumplen una condición es ___. (filter)", "filter"),
  ec="creer que un stream modifica la lista original"),
K("Optional",
  d="contenedor que puede tener un valor o estar vacío",
  u="evitar los errores por valores nulos",
  mas="Optional<T> obliga a pensar en el caso vacío. isPresent() comprueba si hay valor, get() lo obtiene y orElse() da un valor alternativo.",
  k=["Optional puede contener un valor o estar vacío.", "orElse() da un valor alternativo.", "Ayuda a evitar NullPointerException."],
  sit="Una búsqueda puede no encontrar nada y no quieres devolver null. ¿Qué usas?",
  cod="""import java.util.Optional;

public class Main {
    public static void main(String[] args) {
        Optional<String> a = Optional.of("hola");
        Optional<String> b = Optional.empty();
        System.out.println(a.orElse("sin valor"));
        System.out.println(b.orElse("sin valor"));
    }
}""",
  out="hola\nsin valor",
  h="muestra un valor opcional o uno alternativo si falta",
  pr=("El tipo que puede estar vacío es ___. (Optional)", "optional"),
  ec="llamar a get() sobre un Optional vacío"),
]
