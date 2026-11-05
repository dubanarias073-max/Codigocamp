"""JavaScript · Etapa 3: decisiones, bucles y funciones."""
from ..generador import K

LISTA = [
K("if",
  d="estructura que ejecuta código solo si una condición es verdadera",
  u="tomar decisiones en el programa",
  mas="Se escribe if (condición) { ... }. Si la condición es true se ejecuta el bloque; si es false se salta. La condición va entre paréntesis y el código entre llaves. Aunque con una sola línea las llaves son opcionales, es mejor ponerlas siempre.",
  k=["if ejecuta un bloque solo si la condición es verdadera.", "La condición va entre paréntesis.", "El bloque de código va entre llaves."],
  sit="Quieres mostrar un aviso solo cuando la edad sea 18 o más. ¿Qué estructura usas?",
  cod="""const edad = 20;
if (edad >= 18) {
  console.log("Eres mayor de edad");   // solo se ejecuta si la condición es true
}
console.log("Fin del programa");       // esta línea se ejecuta siempre""",
  h="muestra un aviso solo si la edad es mayor o igual a 18",
  pr=("La estructura que ejecuta código solo si algo es verdadero es ___. (2 letras)", "if"),
  pr2=("La condición de un if va entre ___. (paréntesis)", "paréntesis", "parentesis", "()"),
  ec="olvidar los paréntesis de la condición",
  err=("const edad = 20;\nif edad >= 18 {\n  console.log(\"Mayor\");\n}", 2, "La condición debe ir entre paréntesis: if (edad >= 18).")),
K("else",
  d="rama que se ejecuta cuando la condición del if es falsa",
  u="elegir entre dos caminos",
  mas="else va justo después del bloque del if y se ejecuta si la condición no se cumplió. Garantiza que siempre se ejecute exactamente una de las dos ramas. No lleva condición propia.",
  k=["else se ejecuta cuando el if no se cumple.", "else no lleva condición.", "Con if y else siempre se ejecuta exactamente una rama."],
  sit="Quieres mostrar «Mayor» si la edad es 18 o más y «Menor» en caso contrario. ¿Qué estructura usas?",
  cod="""const edad = 15;
if (edad >= 18) {
  console.log("Mayor de edad");
} else {
  console.log("Menor de edad");   // se ejecuta porque 15 no es >= 18
}""",
  h="elige entre dos mensajes según la edad",
  pr=("La rama que se ejecuta cuando el if es falso es ___. (4 letras)", "else"),
  pr2=("Else ___ lleva condición. (sí o no)", "no"),
  ec="escribir una condición después de else"),
K("else if",
  d="rama intermedia que prueba otra condición",
  u="elegir entre más de dos caminos",
  mas="Encadena condiciones: if (a) {...} else if (b) {...} else {...}. JavaScript prueba cada una de arriba abajo y ejecuta solo la primera que sea verdadera. El orden importa: pon primero las condiciones más específicas.",
  k=["else if añade una condición intermedia.", "Se ejecuta solo la primera rama cuya condición sea verdadera.", "El orden de las condiciones importa."],
  sit="Quieres asignar una letra según la nota: A, B o C. ¿Qué estructura usas?",
  cod="""const nota = 7;
if (nota >= 9) {
  console.log("A");
} else if (nota >= 7) {
  console.log("B");          // esta se ejecuta
} else {
  console.log("C");
}""",
  h="asigna una letra según la nota probando condiciones en orden",
  pr=("La rama intermedia entre if y else se escribe else ___. (2 letras)", "if"),
  pr2=("De varias ramas, se ejecuta la ___ cuya condición sea verdadera. (7 letras: primera)", "primera"),
  ec="poner las condiciones en un orden que nunca se cumple",
  err=("const nota = 9;\nif (nota >= 5) {\n  console.log(\"Aprobado\");\n} else if (nota >= 9) {\n  console.log(\"Sobresaliente\");\n}", 4, "La condición nota >= 9 nunca se alcanza: ya entró la primera. Hay que poner la más específica primero.")),
K("switch",
  d="estructura que compara un valor con varios casos",
  u="elegir entre muchas opciones fijas de forma clara",
  mas="switch (valor) { case 1: ...; break; default: ... }. Compara con === cada caso. break evita que continúe con el siguiente caso; default funciona como else. Ideal para días de la semana, opciones de menú o estados.",
  k=["switch compara un valor con varios casos.", "break evita que se ejecuten los casos siguientes.", "default se ejecuta si ningún caso coincide."],
  sit="Quieres mostrar el nombre del día según un número del 1 al 7. ¿Qué estructura usas?",
  cod="""const dia = 3;
switch (dia) {
  case 1: console.log("Lunes"); break;
  case 2: console.log("Martes"); break;
  case 3: console.log("Miércoles"); break;   // coincide
  default: console.log("Otro día");          // si nada coincide
}""",
  h="muestra el nombre de un día según su número",
  pr=("La palabra que evita seguir con los casos siguientes es ___. (5 letras)", "break"),
  pr2=("El caso que se ejecuta si ninguno coincide es ___. (7 letras)", "default"),
  ec="olvidar break y ejecutar casos de más"),
K("Bucle for",
  d="bucle que repite código un número de veces conocido",
  u="repetir tareas sin copiar el código",
  mas="for (let i = 0; i < 5; i++) { ... } tiene tres partes: inicio (let i = 0), condición (i < 5) y avance (i++). Se repite mientras la condición sea true. Cuidado con empezar en 1 si quieres cinco vueltas desde 0.",
  k=["El for tiene inicio, condición y avance.", "Se repite mientras la condición sea verdadera.", "i++ aumenta el contador en uno."],
  sit="Quieres mostrar los números del 1 al 5, repitiendo la misma instrucción. ¿Qué bucle usas?",
  cod="""for (let i = 1; i <= 5; i++) {
  console.log("Vuelta", i);       // se repite 5 veces
}
console.log("Fin");""",
  h="repite cinco vueltas numeradas con un bucle for",
  pr=("El bucle que repite un número conocido de veces es el ___. (3 letras)", "for"),
  pr2=("En for (let i = 0; i < 5; i++), «i++» es el ___. (6 letras: avance)", "avance"),
  ec="escribir una condición que nunca se vuelve falsa y crear un bucle infinito"),
K("Bucle while",
  d="bucle que repite código mientras se cumpla una condición",
  u="repetir cuando no se sabe cuántas veces",
  mas="while (condición) { ... } comprueba la condición antes de cada vuelta. Si la condición nunca cambia, el bucle es infinito, así que dentro debe modificarse algo que acabe haciéndola falsa. Es ideal para «repite hasta que ocurra algo».",
  k=["while repite mientras la condición sea verdadera.", "La condición se comprueba antes de cada vuelta.", "Dentro del bucle debe cambiar algo para que termine."],
  sit="Quieres dividir un número entre 2 repetidamente mientras sea mayor que 1, sin saber cuántas veces. ¿Qué bucle usas?",
  cod="""let n = 100;
let pasos = 0;
while (n > 1) {          // se repite mientras n sea mayor que 1
  n = n / 2;
  pasos++;
}
console.log("Pasos:", pasos);""",
  h="divide un número entre dos mientras sea mayor que uno y cuenta los pasos",
  pr=("El bucle que repite mientras se cumpla una condición es ___. (5 letras)", "while"),
  pr2=("Un bucle cuya condición nunca se vuelve falsa es un bucle ___. (8 letras)", "infinito"),
  ec="olvidar actualizar la variable de la condición"),
K("Bucle do while",
  d="bucle que ejecuta el bloque al menos una vez",
  u="repetir comprobando la condición al final",
  mas="do { ... } while (condición); ejecuta primero el bloque y luego comprueba la condición. Por eso siempre se ejecuta al menos una vez, a diferencia de while. Es útil para menús o para pedir un dato hasta que sea válido.",
  k=["do while ejecuta el bloque al menos una vez.", "La condición se comprueba después de cada vuelta.", "Termina con punto y coma tras el while."],
  sit="Quieres que un mensaje se muestre al menos una vez aunque la condición sea falsa desde el principio. ¿Qué bucle usas?",
  cod="""let intentos = 5;
do {
  console.log("Se ejecuta al menos una vez, intentos =", intentos);
  intentos++;
} while (intentos < 3);    // la condición ya era falsa, pero el bloque corrió una vez""",
  h="ejecuta un bloque una vez aunque la condición sea falsa desde el inicio",
  pr=("El bucle que ejecuta el bloque al menos una vez es do ___. (5 letras)", "while"),
  pr2=("En do while, la condición se comprueba ___ de cada vuelta. (7 letras: después)", "después", "despues"),
  ec="creer que do while puede no ejecutarse nunca"),
K("break y continue",
  d="instrucciones que cortan un bucle o saltan una vuelta",
  u="salir antes de tiempo o ignorar ciertos casos",
  mas="break termina el bucle completamente. continue salta el resto de la vuelta actual y pasa a la siguiente. Se usan con un if: «si encuentro lo que buscaba, break» o «si el número es par, continue».",
  k=["break termina el bucle por completo.", "continue salta solo la vuelta actual.", "Suelen usarse dentro de un if."],
  sit="Quieres dejar de recorrer una lista en cuanto encuentres el número 7. ¿Qué instrucción usas?",
  cod="""for (let i = 1; i <= 10; i++) {
  if (i % 2 === 0) continue;     // salta los pares
  if (i === 7) break;            // sale del bucle al llegar a 7
  console.log(i);                // 1, 3, 5
}""",
  h="salta números pares y se detiene al llegar al 7",
  pr=("La instrucción que termina un bucle es ___. (5 letras)", "break"),
  pr2=("La instrucción que salta a la siguiente vuelta es ___. (8 letras)", "continue"),
  ec="usar break cuando se quería continue"),
K("Bucles anidados",
  d="bucles escritos dentro de otros bucles",
  u="recorrer tablas, cuadrículas y combinaciones",
  mas="Por cada vuelta del bucle externo, el interno realiza todas sus vueltas. Un bucle de 3 vueltas con otro interno de 4 ejecuta el interior 12 veces. Se usan para tablas de multiplicar, matrices y dibujar figuras con texto.",
  k=["El bucle interno completa todas sus vueltas por cada vuelta del externo.", "Dos bucles de 3 y 4 vueltas ejecutan el interior 12 veces.", "Sirven para recorrer tablas y cuadrículas."],
  sit="Quieres imprimir una tabla de multiplicar completa recorriendo filas y columnas. ¿Qué técnica usas?",
  cod="""for (let fila = 1; fila <= 3; fila++) {
  let linea = "";
  for (let col = 1; col <= 3; col++) {
    linea += fila * col + " ";          // el interno se repite por cada fila
  }
  console.log(linea);
}""",
  h="construye una tabla de multiplicar 3 por 3 con dos bucles",
  pr=("Un bucle dentro de otro bucle se llama bucle ___. (8 letras)", "anidado"),
  pr2=("Si el externo da 3 vueltas y el interno 4, el interior se ejecuta ___ veces. (un número)", "12"),
  ec="usar el mismo nombre de contador en los dos bucles"),
K("Funciones",
  d="bloques de código con nombre que se ejecutan al llamarlos",
  u="reutilizar código y dividir un programa en partes",
  mas="function saludar() { ... } define la función y saludar() la ejecuta. Dar un nombre claro a cada función hace el programa más fácil de leer. Una función puede llamarse cuantas veces haga falta y desde cualquier punto donde sea visible.",
  k=["Una función se define con la palabra function.", "Se ejecuta al llamarla con paréntesis.", "Un buen nombre de función describe lo que hace."],
  sit="Quieres agrupar tres líneas de código bajo un nombre para usarlas varias veces. ¿Qué creas?",
  cod="""function mostrarBienvenida() {
  console.log("¡Bienvenida!");
  console.log("Aprende a tu ritmo");
}
mostrarBienvenida();     // llamada 1
mostrarBienvenida();     // llamada 2""",
  h="define una función de bienvenida y la llama dos veces",
  pr=("La palabra que define una función es ___. (8 letras)", "function"),
  pr2=("Para ejecutar una función se escribe su nombre seguido de ___. (paréntesis)", "paréntesis", "parentesis", "()"),
  ec="definir una función y olvidarse de llamarla",
  err=("function saludar() {\n  console.log(\"Hola\");\n}\nsaludar;", 4, "Falta llamar a la función con paréntesis: saludar().")),
K("Parámetros y argumentos",
  d="datos que una función recibe para trabajar con ellos",
  u="hacer funciones flexibles que sirven para distintos valores",
  mas="Los parámetros son los nombres entre paréntesis al definir la función; los argumentos son los valores que pasas al llamarla. function saludar(nombre) recibe un valor distinto cada vez: saludar(\"Ana\"), saludar(\"Luis\"). El orden de los argumentos importa.",
  k=["Los parámetros se escriben al definir la función.", "Los argumentos son los valores que se pasan al llamarla.", "El orden de los argumentos importa."],
  sit="Quieres que una función salude a quien le indiques, no siempre a la misma persona. ¿Qué usas?",
  cod="""function saludar(nombre, ciudad) {      // nombre y ciudad: parámetros
  console.log(`Hola, ${nombre} de ${ciudad}`);
}
saludar("Ana", "Lima");                  // "Ana" y "Lima": argumentos
saludar("Luis", "Bogotá");""",
  h="saluda a distintas personas pasando valores distintos a la función",
  pr=("Los nombres entre paréntesis al definir una función son los ___. (10 letras)", "parámetros", "parametros"),
  pr2=("Los valores que se pasan al llamar una función son los ___. (10 letras)", "argumentos"),
  ec="pasar los argumentos en distinto orden al esperado"),
K("return",
  d="instrucción que devuelve un valor desde una función",
  u="obtener el resultado de una función para usarlo después",
  mas="return termina la función y entrega un valor a quien la llamó. Una función sin return devuelve undefined. console.log solo muestra algo en pantalla; return permite guardar el resultado en una variable. Lo que escribas después de return no se ejecuta.",
  k=["return devuelve un valor y termina la función.", "Sin return, una función devuelve undefined.", "Lo escrito después de return no se ejecuta."],
  sit="Quieres que una función calcule un total y te lo entregue para guardarlo en una variable. ¿Qué usas?",
  cod="""function sumar(a, b) {
  return a + b;            // devuelve el resultado y termina
  console.log("No se ejecuta");
}
const total = sumar(3, 4); // el resultado se guarda
console.log(total);        // 7""",
  h="devuelve la suma de dos números y la guarda en una variable",
  pr=("La instrucción que devuelve un valor desde una función es ___. (6 letras)", "return"),
  pr2=("Una función sin return devuelve ___. (9 letras)", "undefined"),
  ec="usar console.log en lugar de return y no poder guardar el resultado",
  err=("function doble(n) {\n  n * 2;\n}\nconsole.log(doble(4));", 2, "Falta return: sin él la función devuelve undefined.")),
K("Funciones flecha",
  d="sintaxis corta para escribir funciones con =>",
  u="escribir funciones breves, sobre todo como argumentos",
  mas="const doble = (n) => n * 2; equivale a una función normal. Si solo hay una expresión, el return es implícito; con llaves, hay que escribir return. Con un único parámetro se pueden omitir los paréntesis. No tienen su propio this.",
  k=["Las funciones flecha usan la sintaxis =>.", "Con una sola expresión, el return es implícito.", "Con llaves hay que escribir return explícitamente."],
  sit="Quieres escribir una función corta que devuelva el doble de un número en una sola línea. ¿Qué sintaxis usas?",
  cod="""const doble = (n) => n * 2;            // return implícito
const sumar = (a, b) => {
  const resultado = a + b;
  return resultado;                    // con llaves, return explícito
};
console.log(doble(21), sumar(3, 4));""",
  h="define funciones con flecha, una de una línea y otra con llaves",
  pr=("El símbolo de las funciones flecha es ___. (2 caracteres)", "=>"),
  pr2=("En una flecha con llaves, el valor se devuelve con ___. (6 letras)", "return"),
  ec="usar llaves en una flecha y olvidar el return"),
K("Parámetros por defecto",
  d="valores que usa un parámetro cuando no se le pasa argumento",
  u="evitar errores cuando falta un dato opcional",
  mas="function saludar(nombre = \"visitante\") usa «visitante» si llamas a saludar() sin argumento. Solo se aplica cuando el valor es undefined. Los parámetros con valor por defecto suelen ir al final.",
  k=["Un parámetro por defecto se escribe con = y un valor.", "Solo se usa cuando falta el argumento.", "Suelen colocarse al final de la lista de parámetros."],
  sit="Quieres que una función use «visitante» si no le dicen el nombre. ¿Qué técnica usas?",
  cod="""function saludar(nombre = "visitante") {
  console.log(`Hola, ${nombre}`);
}
saludar("Ana");      // Hola, Ana
saludar();           // Hola, visitante""",
  h="saluda con un nombre por defecto cuando no se indica ninguno",
  pr=("Un parámetro por defecto se escribe parámetro ___ valor. (un carácter)", "="),
  pr2=("El valor por defecto se usa cuando el argumento es ___. (9 letras)", "undefined"),
  ec="poner el parámetro por defecto antes de los obligatorios"),
K("Ámbito de variables",
  d="zona del código donde una variable existe y se puede usar",
  u="saber dónde se puede leer cada variable",
  mas="Una variable declarada dentro de una función o de unas llaves solo existe ahí (ámbito local). Una declarada fuera es global y la ven todas las funciones. Evita las globales: pueden modificarse desde cualquier parte y provocar errores difíciles de rastrear.",
  k=["Una variable local solo existe dentro de su bloque o función.", "Una variable global se ve en todo el programa.", "Conviene evitar las variables globales."],
  sit="Una variable creada dentro de una función no se puede leer desde fuera. ¿Qué concepto lo explica?",
  cod="""const global = "visible en todas partes";
function prueba() {
  const local = "solo existe aquí";
  console.log(global, local);
}
prueba();
console.log(typeof local);     // undefined: local no existe fuera de la función""",
  h="compara una variable global con otra local que no existe fuera de su función",
  pr=("Una variable que solo existe dentro de una función es ___. (5 letras)", "local"),
  pr2=("Una variable visible en todo el programa es ___. (6 letras)", "global"),
  ec="intentar usar fuera de una función una variable local"),
K("Callbacks",
  d="funciones que se pasan como argumento a otra función",
  u="decidir qué hacer cuando otra función termina o encuentra algo",
  mas="En JavaScript las funciones son valores: se pueden guardar en variables y pasar a otras funciones. La función que recibe a la otra la «llama de vuelta» (callback) cuando toca. Es la base de los eventos, los temporizadores y los métodos de arrays.",
  k=["Un callback es una función que se pasa como argumento.", "Las funciones son valores en JavaScript.", "Los eventos y temporizadores usan callbacks."],
  sit="Quieres decirle a una función qué hacer cuando acabe su tarea, pasándole otra función. ¿Qué usas?",
  cod="""function procesar(numero, alTerminar) {
  const resultado = numero * 2;
  alTerminar(resultado);                    // llama de vuelta
}
procesar(21, (r) => console.log("Resultado:", r));   // el callback es la flecha""",
  h="pasa una función como argumento para que se ejecute al terminar el cálculo",
  pr=("Una función que se pasa como argumento a otra se llama ___. (8 letras)", "callback"),
  pr2=("En JavaScript las funciones son ___ que se pueden pasar. (7 letras: valores)", "valores"),
  ec="llamar al callback con paréntesis en lugar de pasarlo"),
K("Recursividad",
  d="técnica en la que una función se llama a sí misma",
  u="resolver problemas que se repiten de forma similar",
  mas="Una función recursiva necesita un caso base (cuándo parar) y un caso recursivo (cómo acercarse al caso base). El factorial de 5 es 5 por el factorial de 4, y así hasta 1. Sin caso base, la función se llama sin fin y da error de pila.",
  k=["Una función recursiva se llama a sí misma.", "Necesita un caso base para detenerse.", "Sin caso base provoca un desbordamiento de pila."],
  sit="Quieres calcular el factorial de un número usando una función que se llama a sí misma. ¿Qué técnica usas?",
  cod="""function factorial(n) {
  if (n <= 1) return 1;            // caso base: aquí se detiene
  return n * factorial(n - 1);     // caso recursivo: se acerca al caso base
}
console.log(factorial(5));         // 120""",
  h="calcula un factorial con una función que se llama a sí misma",
  pr=("La condición que detiene una función recursiva es el caso ___. (4 letras)", "base"),
  pr2=("Una función que se llama a sí misma es ___. (10 letras)", "recursiva"),
  ec="olvidar el caso base y provocar un bucle infinito"),
K("Funciones anónimas",
  d="funciones sin nombre usadas en el mismo lugar donde se escriben",
  u="definir una acción breve directamente donde se necesita",
  mas="function () { ... } o () => ... sin nombre propio. Se usan como callbacks: setTimeout(() => console.log(\"hola\"), 1000). Si la necesitas en varios sitios, dale un nombre. Un nombre también ayuda a leer los mensajes de error.",
  k=["Una función anónima no tiene nombre.", "Se usan mucho como callbacks.", "Si se reutiliza, conviene darle un nombre."],
  sit="Necesitas una función muy corta que solo vas a usar una vez, justo donde la escribes. ¿Qué usas?",
  cod="""const numeros = [1, 2, 3];
const dobles = numeros.map(function (n) {   // función anónima clásica
  return n * 2;
});
const triples = numeros.map((n) => n * 3);  // anónima con flecha
console.log(dobles, triples);""",
  h="usa dos funciones sin nombre para transformar una lista",
  pr=("Una función sin nombre se llama ___. (8 letras: anónima)", "anónima", "anonima"),
  pr2=("Las funciones anónimas se usan mucho como ___. (9 letras: callbacks)", "callbacks", "callback"),
  ec="repetir la misma función anónima en varios sitios"),
K("Funciones de orden superior",
  d="funciones que reciben o devuelven otras funciones",
  u="crear herramientas reutilizables y flexibles",
  mas="map, filter y reduce son de orden superior porque reciben una función. También lo es una función que devuelve otra: function multiplicador(n) { return (x) => x * n; }. Permiten componer comportamientos como piezas de construcción.",
  k=["Una función de orden superior recibe o devuelve funciones.", "map, filter y reduce son funciones de orden superior.", "Permiten componer comportamientos reutilizables."],
  sit="Quieres crear una función que fabrique otras funciones multiplicadoras. ¿Qué tipo de función es?",
  cod="""function multiplicador(n) {
  return (x) => x * n;            // devuelve otra función
}
const doble = multiplicador(2);
const triple = multiplicador(3);
console.log(doble(5), triple(5));   // 10 15""",
  h="crea funciones multiplicadoras a partir de una función que devuelve funciones",
  pr=("Una función que recibe o devuelve funciones es de orden ___. (8 letras: superior)", "superior"),
  pr2=("map y filter reciben como argumento una ___. (7 letras: función)", "función", "funcion"),
  ec="olvidar que la función devuelta guarda el valor de n"),
K("Depurar con console",
  d="técnicas para encontrar errores usando la consola",
  u="descubrir por qué un programa no hace lo esperado",
  mas="console.log muestra valores en el momento; console.table muestra arrays y objetos como tabla; console.error y console.warn resaltan problemas. Rastrea el programa «imprimiendo» los valores clave y comparando lo esperado con lo real.",
  k=["console.log permite comprobar valores durante la ejecución.", "console.table muestra arrays y objetos como tabla.", "Comparar lo esperado con lo real localiza el error."],
  sit="Un cálculo da un resultado distinto al esperado y quieres inspeccionar los valores intermedios. ¿Qué haces?",
  cod="""function promedio(a, b, c) {
  console.log("Entradas:", a, b, c);       // ¿llegan bien los datos?
  const suma = a + b + c;
  console.log("Suma:", suma);              // ¿es la suma esperada?
  return suma / 3;
}
console.log("Resultado:", promedio(6, 8, 10));
console.table([{ nombre: "Ana", nota: 9 }, { nombre: "Luis", nota: 7 }]);""",
  h="imprime valores intermedios y una tabla para depurar un cálculo",
  pr=("La función que muestra arrays y objetos como tabla es console.___. (5 letras)", "table"),
  pr2=("Para resaltar un problema se usa console.___. (5 letras)", "error"),
  ec="cambiar código al azar sin inspeccionar los valores"),
]
