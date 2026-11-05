// Lecciones de C. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"C es un lenguaje rápido y cercano a la máquina.",
    p:["#include trae funciones", "printf imprime; \\n es salto de línea"],
    c:`#include <stdio.h>

int main() {
  printf("¡Hola, CódigoCamp!\\n");
  return 0;
}` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"Cada variable lleva su tipo y printf usa marcadores como %d.",
    p:["int guarda enteros", "%d imprime un entero"],
    c:`#include <stdio.h>

int main() {
  int edad = 20;
  if (edad >= 18) printf("Mayor de edad: %d\\n", edad);
  return 0;
}` },
  { m:"Fundamentos", t:"Bucles", x:"for repite un bloque un número conocido de veces.",
    p:["for (inicio; condición; paso)", "%d muestra un entero"],
    c:`#include <stdio.h>

int main() {
  for (int i = 1; i <= 5; i++) {
    printf("Vuelta %d\\n", i);
  }
  return 0;
}` },
  { m:"Fundamentos", t:"Funciones", x:"Una función agrupa instrucciones y puede devolver un valor.",
    p:["Indica el tipo que devuelve", "Se define antes de usarla"],
    c:`#include <stdio.h>

int doble(int n) {
  return n * 2;
}

int main() {
  printf("%d\\n", doble(21));
  return 0;
}` },
  { m:"Intermedio", t:"Arreglos y cadenas", x:"Un arreglo guarda varios valores del mismo tipo. Un texto es un arreglo de char terminado en el carácter nulo.",
    p:["int a[5] declara 5 enteros", "El primer índice es 0", "strlen y strcpy trabajan con textos"],
    c:"#include <stdio.h>\n#include <string.h>\n\nint main() {\n  int notas[3] = {7, 9, 8};\n  int suma = 0;\n  for (int i = 0; i < 3; i++) {\n    suma += notas[i];\n  }\n  printf(\"Promedio: %d\\n\", suma / 3);\n\n  char nombre[20] = \"Ana\";\n  printf(\"%s tiene %d letras\\n\", nombre, (int)strlen(nombre));\n  return 0;\n}",
    r:"Cambia el programa para calcular el promedio como decimal con float.",
    e:"Salirse de los límites del arreglo causa errores graves e impredecibles." },
  { m:"Intermedio", t:"Punteros", x:"Un puntero guarda la dirección de otra variable. & obtiene la dirección y * accede al valor.",
    p:["int *p declara un puntero a entero", "&x es la dirección de x", "*p lee o cambia el valor apuntado"],
    c:"#include <stdio.h>\n\nvoid duplicar(int *n) {\n  *n = *n * 2;\n}\n\nint main() {\n  int x = 5;\n  int *p = &x;\n  printf(\"%d\\n\", *p);\n  duplicar(&x);\n  printf(\"%d\\n\", x);\n  return 0;\n}",
    r:"Escribe una función intercambiar(int *a, int *b) que cambie dos valores.",
    e:"Usar un puntero sin inicializar apunta a memoria desconocida." },
  { m:"Avanzado", t:"Memoria dinámica", x:"malloc reserva memoria en tiempo de ejecución y free la devuelve. Olvidar free causa fugas de memoria.",
    p:["malloc devuelve un puntero", "Hay que comprobar que no sea NULL", "Cada malloc necesita su free"],
    c:"#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n  int n = 4;\n  int *a = malloc(n * sizeof(int));\n  if (a == NULL) return 1;\n  for (int i = 0; i < n; i++) a[i] = i * i;\n  for (int i = 0; i < n; i++) printf(\"%d \", a[i]);\n  printf(\"\\n\");\n  free(a);\n  return 0;\n}",
    r:"Pide el tamaño n con scanf y reserva ese número de enteros.",
    e:"Usar la memoria después de free es un error muy común y peligroso." },
  { m:"Avanzado", t:"Structs y typedef", x:"Una struct agrupa variables de distintos tipos. typedef le da un nombre corto.",
    p:["struct agrupa campos", ". accede a un campo y -> con un puntero", "typedef crea un alias de tipo"],
    c:"#include <stdio.h>\n\ntypedef struct {\n  char nombre[20];\n  int edad;\n} Persona;\n\nint main() {\n  Persona p = {\"Ana\", 20};\n  Persona *q = &p;\n  printf(\"%s tiene %d\\n\", p.nombre, q->edad);\n  return 0;\n}",
    r:"Crea un arreglo de 3 Personas y muéstralas con un for." },
  { m:"Experto", t:"Archivos", x:"fopen abre un archivo, fprintf y fgets escriben y leen, y fclose lo cierra.",
    p:["\"r\" lee, \"w\" escribe, \"a\" añade", "Comprueba que fopen no devuelva NULL", "Siempre cierra con fclose"],
    c:"#include <stdio.h>\n\nint main() {\n  FILE *f = fopen(\"datos.txt\", \"w\");\n  if (f == NULL) return 1;\n  fprintf(f, \"Hola, archivo\\n\");\n  fclose(f);\n\n  char linea[50];\n  f = fopen(\"datos.txt\", \"r\");\n  if (f != NULL && fgets(linea, 50, f)) printf(\"%s\", linea);\n  if (f) fclose(f);\n  return 0;\n}",
    r:"Escribe tres líneas en el archivo y léelas con un while." },
  { m:"Experto", t:"Preprocesador, Makefile y depuración", x:"El preprocesador procesa #include y #define antes de compilar. gcc compila, make automatiza y gdb depura.",
    p:["#define crea constantes y macros", "gcc -Wall muestra advertencias", "gdb permite ejecutar paso a paso"],
    c:"#include <stdio.h>\n#define PI 3.14159\n#define AL_CUADRADO(x) ((x) * (x))\n\nint main() {\n  printf(\"%.2f\\n\", PI * AL_CUADRADO(2));\n  return 0;\n}",
    r:"Compila siempre con gcc -Wall -Wextra y corrige todas las advertencias." },
];
