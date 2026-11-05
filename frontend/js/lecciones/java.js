// Lecciones de Java. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"Todo programa Java vive dentro de una clase y empieza en main.",
    p:["La clase se llama Main", "System.out.println imprime una línea"],
    c:`public class Main {
  public static void main(String[] args) {
    System.out.println("¡Hola, CódigoCamp!");
  }
}` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"Java exige indicar el tipo de cada variable.",
    p:["int, double, String, boolean", "if (condición) { ... }"],
    c:`public class Main {
  public static void main(String[] args) {
    int edad = 20;
    if (edad >= 18) System.out.println("Eres mayor de edad");
    else System.out.println("Eres menor de edad");
  }
}` },
  { m:"Fundamentos", t:"Bucles", x:"for repite un bloque un número conocido de veces.",
    p:["for (inicio; condición; paso)", "i++ suma 1 en cada vuelta"],
    c:`public class Main {
  public static void main(String[] args) {
    for (int i = 1; i <= 5; i++) {
      System.out.println("Vuelta " + i);
    }
  }
}` },
  { m:"Fundamentos", t:"Métodos", x:"Un método agrupa instrucciones. static permite llamarlo sin crear un objeto.",
    p:["Indica el tipo que devuelve", "return devuelve el resultado"],
    c:`public class Main {
  static int doble(int n) {
    return n * 2;
  }
  public static void main(String[] args) {
    System.out.println(doble(21));
  }
}` },
  { m:"Intermedio", t:"Colecciones: ArrayList y HashMap", x:"Las colecciones guardan datos que crecen. ArrayList es una lista y HashMap asocia claves con valores.",
    p:["ArrayList<String> es una lista de textos", "HashMap<String, Integer> guarda pares clave-valor", "Se recorren con for-each"],
    c:"import java.util.ArrayList;\nimport java.util.HashMap;\n\npublic class Main {\n  public static void main(String[] args) {\n    ArrayList<String> nombres = new ArrayList<>();\n    nombres.add(\"Ana\");\n    nombres.add(\"Luis\");\n\n    HashMap<String, Integer> edades = new HashMap<>();\n    edades.put(\"Ana\", 20);\n    edades.put(\"Luis\", 25);\n\n    for (String n : nombres) {\n      System.out.println(n + \" tiene \" + edades.get(n));\n    }\n  }\n}",
    r:"Añade un tercer nombre y su edad, y muestra cuántos elementos hay con size().",
    e:"Usar tipos primitivos como int en <>: hay que usar Integer." },
  { m:"Intermedio", t:"Clases y objetos", x:"Una clase es el molde y un objeto es una copia creada con new. El encapsulamiento oculta los datos y los expone con métodos.",
    p:["Los atributos suelen ser private", "El constructor inicializa el objeto", "this se refiere al objeto actual"],
    c:"class Persona {\n  private String nombre;\n  private int edad;\n\n  Persona(String nombre, int edad) {\n    this.nombre = nombre;\n    this.edad = edad;\n  }\n\n  String saludar() {\n    return \"Hola, soy \" + nombre + \" y tengo \" + edad;\n  }\n}\n\npublic class Main {\n  public static void main(String[] args) {\n    Persona p = new Persona(\"Ana\", 20);\n    System.out.println(p.saludar());\n  }\n}",
    r:"Añade un método esMayor() que devuelva true si edad >= 18.",
    e:"Comparar textos con == en lugar de equals()." },
  { m:"Avanzado", t:"Excepciones", x:"Las excepciones representan errores en tiempo de ejecución. try/catch los captura y finally se ejecuta siempre.",
    p:["try encierra el código que puede fallar", "catch decide qué hacer con el error", "throw lanza una excepción propia"],
    c:"public class Main {\n  static int dividir(int a, int b) {\n    if (b == 0) throw new IllegalArgumentException(\"No se puede dividir entre 0\");\n    return a / b;\n  }\n\n  public static void main(String[] args) {\n    try {\n      System.out.println(dividir(10, 2));\n      System.out.println(dividir(5, 0));\n    } catch (IllegalArgumentException e) {\n      System.out.println(\"Error: \" + e.getMessage());\n    } finally {\n      System.out.println(\"Fin\");\n    }\n  }\n}",
    r:"Captura también NumberFormatException al convertir \"abc\" con Integer.parseInt.",
    e:"Atrapar Exception genérica y no hacer nada oculta los errores." },
  { m:"Avanzado", t:"Herencia e interfaces", x:"La herencia reutiliza una clase con extends. Una interfaz define qué métodos debe tener una clase con implements.",
    p:["extends hereda atributos y métodos", "@Override reemplaza un método del padre", "Una clase puede implementar varias interfaces"],
    c:"interface Sonido { String hacerSonido(); }\n\nclass Animal implements Sonido {\n  public String hacerSonido() { return \"...\"; }\n}\n\nclass Perro extends Animal {\n  @Override\n  public String hacerSonido() { return \"Guau\"; }\n}\n\npublic class Main {\n  public static void main(String[] args) {\n    Animal a = new Perro();\n    System.out.println(a.hacerSonido());\n  }\n}",
    r:"Crea la clase Gato con su propio sonido y úsala en la misma variable de tipo Animal." },
  { m:"Experto", t:"Lambdas y Streams", x:"Las expresiones lambda son funciones cortas. Los streams procesan colecciones con filtros y transformaciones.",
    p:["x -> x * 2 es una lambda", "filter, map y collect forman una tubería", "Los streams no modifican la lista original"],
    c:"import java.util.List;\nimport java.util.stream.Collectors;\n\npublic class Main {\n  public static void main(String[] args) {\n    List<Integer> nums = List.of(1, 2, 3, 4, 5, 6);\n    List<Integer> dobles = nums.stream()\n        .filter(n -> n % 2 == 0)\n        .map(n -> n * 2)\n        .collect(Collectors.toList());\n    System.out.println(dobles);\n  }\n}",
    r:"Cambia el filtro para quedarte con los mayores que 3." },
  { m:"Experto", t:"Maven y pruebas con JUnit", x:"Maven descarga dependencias y organiza el proyecto. JUnit ejecuta pruebas automáticas.",
    p:["pom.xml describe el proyecto y sus dependencias", "Una prueba usa @Test y assertEquals", "mvn test ejecuta todas las pruebas"],
    c:"// Ejemplo de prueba JUnit 5 (necesita Maven)\n// import org.junit.jupiter.api.Test;\n// import static org.junit.jupiter.api.Assertions.assertEquals;\n//\n// class CalculadoraTest {\n//   @Test\n//   void sumaDosNumeros() {\n//     assertEquals(5, 2 + 3);\n//   }\n// }\n\npublic class Main {\n  static int suma(int a, int b) { return a + b; }\n\n  public static void main(String[] args) {\n    System.out.println(suma(2, 3) == 5 ? \"OK\" : \"FALLA\");\n  }\n}",
    r:"Escribe una segunda comprobación para suma(-1, 1)." },
];
