// Retos tipo Duolingo. Tipos de pregunta:
//  opcion    -> elegir una respuesta       { q, codigo?, op:[], ok:índice, exp }
//  completar -> escribir una respuesta     { q, codigo?, resp:[aceptadas], exp }
//  error     -> elegir la línea con error  { q, codigo, ok:nºLínea(desde 1), exp }
//  ordenar   -> ordenar piezas             { q, piezas:[en orden correcto], exp }
//  codigo    -> escribir una función       { q, fn, plantilla, casos:[{a:[args], r:resultado, v:false = oculta}], exp }
//  caso      -> encontrar un caso de prueba que revele un bug { q, fn, defectuosa, correcta, exp }
const r = String.raw;

export const XP_TIPO = { opcion: 10, completar: 10, error: 10, ordenar: 10, codigo: 15, caso: 15 };

export const RUTAS = [
{ id: "base", nombre: "Fundamentos", dificultad: "Fácil", emoji: "🌱", color: "#12915a",
  desc: "Variables, condicionales, bucles, HTML y CSS.",
  niveles: [
  { id: "base1", titulo: "Variables y tipos", preguntas: [
    { t: "opcion", q: "¿Qué hace este código de JavaScript?", codigo: r`let edad = 25;`,
      op: ["Guarda el número 25 en una variable llamada edad", "Imprime 25 en pantalla", "Compara edad con 25", "Borra la variable edad"], ok: 0,
      exp: "let declara una variable y el signo = le asigna un valor." },
    { t: "opcion", q: "¿Cuál de estos valores es de tipo texto (string)?",
      op: [r`42`, r`true`, r`"hola"`, r`3.14`], ok: 2, exp: "Los textos van entre comillas." },
    { t: "completar", q: "Completa: para declarar una constante en JavaScript se usa la palabra…", codigo: r`___ PI = 3.14;`,
      resp: ["const"], exp: "const declara un valor que no se puede reasignar." },
    { t: "opcion", q: "¿Qué valor tiene esMayor?", codigo: r`let edad = 20;
let esMayor = edad >= 18;`,
      op: ["true", "false", "18", "undefined"], ok: 0, exp: "20 >= 18 es verdadero, así que la comparación devuelve true." },
    { t: "ordenar", q: "Ordena las piezas para formar una variable correcta",
      piezas: ["let", "nombre", "=", r`"Ana"`, ";"], exp: "Palabra clave, nombre, signo igual, valor y punto y coma." },
  ] },
  { id: "base2", titulo: "Condicionales y bucles", preguntas: [
    { t: "opcion", q: "¿Qué imprime este código?", codigo: r`let nota = 4;
if (nota >= 5) {
  console.log("Aprobado");
} else {
  console.log("Suspenso");
}`, op: ["Aprobado", "Suspenso", "Nada", "Da error"], ok: 1, exp: "4 no es mayor ni igual que 5, así que se ejecuta el else." },
    { t: "opcion", q: "¿Qué imprime este bucle?", codigo: r`for (let i = 1; i <= 3; i++) {
  console.log(i);
}`, op: ["1, 2, 3", "0, 1, 2", "1, 2, 3, 4", "3, 2, 1"], ok: 0, exp: "i empieza en 1 y el bucle se repite mientras i <= 3." },
    { t: "completar", q: "¿Cuántas veces se ejecuta este bucle? (escribe un número)", codigo: r`for (let i = 0; i < 5; i++) { ... }`,
      resp: ["5", "cinco"], exp: "i toma los valores 0, 1, 2, 3 y 4: son cinco vueltas." },
    { t: "error", q: "Una de estas líneas impide que el programa funcione. ¿Cuál?", codigo: r`let total = 0;
for (let i = 1; i <= 3; i++) {
  total = total + i
  console.log("Suma: " + total;
}`, ok: 4, exp: "A la línea 4 le falta cerrar el paréntesis. (El punto y coma que falta en la línea 3 es opcional en JavaScript.)" },
    { t: "opcion", q: "¿Cuál de estos es un bucle infinito?",
      op: [r`for (let i = 0; i < 3; i++) {}`, r`while (true) { }`, r`let i = 0; while (i < 3) { i++; }`, r`for (let i = 3; i > 0; i--) {}`], ok: 1,
      exp: "while (true) nunca deja de cumplir su condición." },
  ] },
  { id: "base3", titulo: "HTML y CSS básico", preguntas: [
    { t: "opcion", q: "¿Qué etiqueta crea el título principal visible de una página?", op: ["<p>", "<h1>", "<head>", "<br>"], ok: 1,
      exp: "<h1> es el encabezado de mayor importancia." },
    { t: "completar", q: "En CSS, la propiedad que cambia el color del texto se llama…", codigo: r`p { ___: tomato; }`,
      resp: ["color"], exp: "color cambia el texto; background cambia el fondo." },
    { t: "opcion", q: "¿Qué hace padding?", codigo: r`.caja { margin: 10px; padding: 20px; }`,
      op: ["Espacio entre el contenido y el borde", "Espacio fuera del borde", "Grosor del borde", "Color de fondo"], ok: 0,
      exp: "padding es el relleno interior; margin es el espacio exterior." },
    { t: "ordenar", q: "Ordena las piezas para crear un enlace",
      piezas: [r`<a`, r`href="https://example.com">`, "Visitar", r`</a>`], exp: "Se abre la etiqueta con su atributo, luego va el texto y se cierra." },
    { t: "error", q: "¿Qué línea tiene el error?", codigo: r`<ul>
  <li>HTML</li>
  <li>CSS</li
  <li>JavaScript</li>
</ul>`, ok: 3, exp: "A la etiqueta de cierre </li de la línea 3 le falta el símbolo >." },
  ] },
] },

{ id: "logica", nombre: "Lógica y código", dificultad: "Medio", emoji: "⚡", color: "#0b7f9e",
  desc: "Funciones, listas, depuración y SQL. Aquí ya escribes código.",
  niveles: [
  { id: "logica1", titulo: "Funciones y listas", preguntas: [
    { t: "opcion", q: "¿Qué imprime este código?", codigo: r`function doble(x) {
  return x * 2;
}
console.log(doble(4));`, op: ["8", "4", "doble", "undefined"], ok: 0, exp: "doble(4) devuelve 4 * 2 = 8." },
    { t: "opcion", q: "¿Qué imprime este código?", codigo: r`const frutas = ["manzana", "pera", "uva"];
console.log(frutas[1]);`, op: ["manzana", "pera", "uva", "undefined"], ok: 1, exp: "Los índices empiezan en 0, así que frutas[1] es el segundo elemento." },
    { t: "opcion", q: "¿Qué imprime este código?", codigo: r`const n = [1, 2, 3];
n.push(4);
console.log(n.length);`, op: ["3", "4", "5", "undefined"], ok: 1, exp: "push añade un elemento al final, así que la lista pasa a tener 4." },
    { t: "codigo", q: "Escribe la función esPar(n): devuelve true si n es par y false si no.", fn: "esPar",
      plantilla: "function esPar(n) {\n  // tu código aquí\n}",
      casos: [{ a: [2], r: true }, { a: [7], r: false }, { a: [0], r: true, v: false }, { a: [-4], r: true, v: false }, { a: [-3], r: false, v: false }],
      exp: "Un número es par si el resto de dividirlo entre 2 es 0. Ojo con los negativos: -3 % 2 vale -1, no 1." },
    { t: "codigo", q: "Escribe sumaLista(numeros): devuelve la suma de todos los números de la lista (0 si está vacía).", fn: "sumaLista",
      plantilla: "function sumaLista(numeros) {\n  // tu código aquí\n}",
      casos: [{ a: [[1, 2, 3]], r: 6 }, { a: [[]], r: 0 }, { a: [[5]], r: 5, v: false }, { a: [[-1, 1]], r: 0, v: false }],
      exp: "Recorre la lista con un bucle e ir acumulando en una variable que empiece en 0." },
  ] },
  { id: "logica2", titulo: "Depurar: encuentra el error", preguntas: [
    { t: "error", q: "Esta función debería devolver el promedio de dos números. ¿Qué línea tiene el bug?", codigo: r`function promedio(a, b) {
  let suma = a + b;
  return suma / 3;
}
console.log(promedio(4, 6));`, ok: 3, exp: "El promedio de dos números se calcula dividiendo entre 2, no entre 3." },
    { t: "error", q: "Debería imprimir cada color una sola vez, pero imprime también undefined. ¿Qué línea falla?", codigo: r`const colores = ["rojo", "verde", "azul"];
for (let i = 0; i <= colores.length; i++) {
  console.log(colores[i]);
}`, ok: 2, exp: "Con <= el bucle da una vuelta de más (índice 3, que no existe). Debe ser i < colores.length: es el clásico error «off by one»." },
    { t: "error", q: "Siempre entra en el if, aunque la edad sea 17. ¿Qué línea tiene el bug?", codigo: r`let edad = 17;
if (edad = 18) {
  console.log("Eres mayor de edad");
}`, ok: 2, exp: "= asigna un valor y da 18 (verdadero). Para comparar se usa === o >=." },
    { t: "opcion", q: "Este código imprime NaN. ¿Por qué?", codigo: r`let precio = "10";
let cantidad = "tres";
console.log(precio * cantidad);`,
      op: ["Porque «tres» no se puede convertir a número", "Porque falta un punto y coma", "Porque * solo funciona con enteros", "Porque precio es una constante"], ok: 0,
      exp: "NaN significa «Not a Number»: aparece cuando una operación numérica no tiene sentido." },
    { t: "opcion", q: "Al encontrar un error que no entiendes, ¿cuál es la mejor primera acción?",
      op: ["Leer el mensaje de error y ver en qué línea ocurre", "Borrar todo el código y empezar de nuevo", "Cambiar cosas al azar hasta que funcione", "Ignorar el error si el programa arranca"], ok: 0,
      exp: "El mensaje de error suele indicar qué falla y dónde." },
  ] },
  { id: "logica3", titulo: "Bases de datos y SQL", preguntas: [
    { t: "opcion", q: "¿Qué instrucción SQL se usa para leer datos?", op: ["SELECT", "INSERT", "UPDATE", "DROP"], ok: 0,
      exp: "SELECT consulta datos; INSERT añade, UPDATE modifica y DROP elimina tablas." },
    { t: "completar", q: "Completa la consulta para leer la tabla estudiantes:", codigo: r`SELECT * ___ estudiantes;`,
      resp: ["from"], exp: "FROM indica de qué tabla se leen los datos." },
    { t: "opcion", q: "¿Para qué sirve la cláusula WHERE?",
      op: ["Filtrar las filas que cumplen una condición", "Ordenar los resultados", "Unir dos tablas", "Borrar la tabla"], ok: 0,
      exp: "WHERE deja pasar solo las filas que cumplen la condición." },
    { t: "opcion", q: "¿Qué tipo de base de datos es MongoDB?", op: ["Documental", "Relacional", "De grafos", "Clave-valor"], ok: 0,
      exp: "MongoDB guarda documentos con forma de JSON." },
    { t: "opcion", q: "¿Qué base de datos elegirías para una caché ultrarrápida de sesiones de usuario?",
      op: ["Redis", "Neo4j", "Cassandra", "MySQL con muchos JOIN"], ok: 0,
      exp: "Redis trabaja en memoria con pares clave-valor: perfecto para cachés y sesiones." },
  ] },
] },

{ id: "pruebas", nombre: "Pruebas de software", dificultad: "Difícil", emoji: "🧪", color: "#7c3aed",
  desc: "Tipos de pruebas, casos límite, TDD y código que debe superar pruebas ocultas.",
  niveles: [
  { id: "pruebas1", titulo: "Conceptos de testing", preguntas: [
    { t: "opcion", q: "¿Qué tipo de prueba verifica una sola función o método de forma aislada?",
      op: ["Prueba unitaria", "Prueba de integración", "Prueba de aceptación", "Prueba de carga"], ok: 0,
      exp: "Las pruebas unitarias son las más pequeñas y rápidas: una pieza, aislada." },
    { t: "opcion", q: "Comprobar que el módulo de pagos y el de pedidos funcionan bien JUNTOS es una prueba de…",
      op: ["Integración", "Unitaria", "Regresión", "Usabilidad"], ok: 0,
      exp: "Las pruebas de integración verifican la comunicación entre componentes." },
    { t: "opcion", q: "Tras corregir un bug, vuelves a ejecutar las pruebas anteriores para comprobar que no rompiste nada. Eso es una prueba de…",
      op: ["Regresión", "Carga", "Usabilidad", "Exploración"], ok: 0,
      exp: "La regresión detecta que un cambio nuevo estropee algo que ya funcionaba." },
    { t: "opcion", q: "¿Qué mide una prueba de carga?",
      op: ["Cómo se comporta el sistema con muchos usuarios a la vez", "Si el diseño es bonito", "Si hay errores de sintaxis", "Si la base de datos está normalizada"], ok: 0,
      exp: "Las pruebas de carga simulan mucho tráfico para ver el rendimiento y los límites." },
    { t: "ordenar", q: "Ordena las fases del patrón Arrange-Act-Assert",
      piezas: ["Arrange: preparar los datos", "Act: ejecutar lo que se prueba", "Assert: comprobar el resultado"],
      exp: "Preparar, actuar y comprobar: así se estructura una prueba clara." },
  ] },
  { id: "pruebas2", titulo: "Diseñar casos de prueba", preguntas: [
    { t: "opcion", q: "Un campo acepta edades de 18 a 65. Según el análisis de valores límite, ¿qué conjunto es más útil?",
      op: ["17, 18, 65, 66", "20, 30, 40, 50", "1, 2, 3, 4", "18, 30, 100, 200"], ok: 0,
      exp: "Los errores se esconden en los bordes: justo dentro y justo fuera de cada límite." },
    { t: "opcion", q: "Un campo acepta enteros del 1 al 100. ¿Qué particiones de equivalencia tiene?",
      op: ["Menores que 1, de 1 a 100 y mayores que 100", "Solo una: los números", "Dos: pares e impares", "Cien: una por cada número"], ok: 0,
      exp: "Se prueba un representante de cada grupo que el programa trata igual." },
    { t: "caso", q: "Esta función dice si un año es bisiesto, pero tiene un bug. Escribe un año (entrada) para el que dé un resultado distinto al correcto.", fn: "esBisiesto",
      defectuosa: r`function esBisiesto(anio) {
  return anio % 4 === 0;
}`,
      correcta: r`function esBisiesto(anio) {
  return (anio % 4 === 0 && anio % 100 !== 0) || anio % 400 === 0;
}`,
      exp: "1900 y 2100 son divisibles entre 4 pero NO son bisiestos: los años de siglo solo lo son si se dividen entre 400." },
    { t: "caso", q: "Una web permite votar a partir de 18 años, pero esta función falla en un caso. ¿Qué edad lo demuestra?", fn: "puedeVotar",
      defectuosa: r`function puedeVotar(edad) {
  return edad > 18;
}`,
      correcta: r`function puedeVotar(edad) {
  return edad >= 18;
}`,
      exp: "Es un valor límite: con exactamente 18 años la función defectuosa responde false." },
    { t: "opcion", q: "Vas a probar dividir(a, b). ¿Qué caso de prueba NO puede faltar?",
      op: ["b = 0", "a = 1 y b = 1 solamente", "a igual a b siempre", "Solo números positivos grandes"], ok: 0,
      exp: "Dividir entre cero es el caso límite clásico: hay que decidir y probar qué debe pasar." },
  ] },
  { id: "pruebas3", titulo: "Escribe código que pase las pruebas", preguntas: [
    { t: "codigo", q: "Escribe esPalindromo(texto): true si se lee igual al revés, ignorando mayúsculas y espacios.", fn: "esPalindromo",
      plantilla: "function esPalindromo(texto) {\n  // tu código aquí\n}",
      casos: [{ a: ["ana"], r: true }, { a: ["hola"], r: false }, { a: ["Ana"], r: true, v: false }, { a: [""], r: true, v: false }, { a: ["Anita lava la tina"], r: true, v: false }, { a: ["casa"], r: false, v: false }],
      exp: "Pasa el texto a minúsculas, quita los espacios y compáralo con su versión invertida." },
    { t: "codigo", q: "Escribe maximo(numeros): devuelve el mayor de la lista, o null si la lista está vacía.", fn: "maximo",
      plantilla: "function maximo(numeros) {\n  // tu código aquí\n}",
      casos: [{ a: [[3, 9, 2]], r: 9 }, { a: [[-5, -2, -9]], r: -2 }, { a: [[]], r: null, v: false }, { a: [[7]], r: 7, v: false }],
      exp: "Si empiezas con un máximo de 0, fallarás con listas de negativos. Empieza con el primer elemento y trata la lista vacía aparte." },
    { t: "codigo", q: "Escribe fizzBuzz(n): devuelve \"FizzBuzz\" si n es múltiplo de 3 y de 5, \"Fizz\" si lo es de 3, \"Buzz\" si lo es de 5; en otro caso devuelve n.", fn: "fizzBuzz",
      plantilla: "function fizzBuzz(n) {\n  // tu código aquí\n}",
      casos: [{ a: [3], r: "Fizz" }, { a: [5], r: "Buzz" }, { a: [15], r: "FizzBuzz" }, { a: [7], r: 7, v: false }, { a: [30], r: "FizzBuzz", v: false }, { a: [9], r: "Fizz", v: false }, { a: [10], r: "Buzz", v: false }],
      exp: "Comprueba primero el caso doble (múltiplo de 3 y de 5); si no, 15 caería en el primer if." },
    { t: "codigo", q: "Escribe contarVocales(texto): cuenta las vocales a, e, i, o, u (mayúsculas o minúsculas, sin tildes).", fn: "contarVocales",
      plantilla: "function contarVocales(texto) {\n  // tu código aquí\n}",
      casos: [{ a: ["hola"], r: 2 }, { a: ["AEIOU"], r: 5 }, { a: ["xyz"], r: 0, v: false }, { a: [""], r: 0, v: false }, { a: ["Programar"], r: 3, v: false }],
      exp: "Pasa el texto a minúsculas y cuenta las letras que estén en «aeiou»." },
    { t: "opcion", q: "Tu función pasa 3 pruebas, pero falla con una lista vacía que no probaste. ¿Qué lección te deja?",
      op: ["Probar solo el caso feliz no basta: hay que probar casos límite", "La lista vacía no es una entrada válida", "Las pruebas no sirven para nada", "Hay que borrar la función"], ok: 0,
      exp: "Los casos límite (vacío, cero, negativos, enormes) son donde más bugs aparecen." },
  ] },
  { id: "pruebas4", titulo: "Calidad y depuración", preguntas: [
    { t: "opcion", q: "En TDD (desarrollo guiado por pruebas), ¿cuál es el orden correcto?",
      op: ["Escribir una prueba que falla, escribir el código mínimo para pasarla y refactorizar", "Escribir todo el código y probar al final", "Refactorizar, escribir código y probar", "Probar a mano y entregar"], ok: 0,
      exp: "Es el ciclo rojo, verde, refactor." },
    { t: "opcion", q: "Un mock (doble de prueba) sirve principalmente para…",
      op: ["Simular una dependencia (API, base de datos) y aislar lo que pruebas", "Acelerar el procesador", "Cifrar contraseñas", "Generar datos reales de producción"], ok: 0,
      exp: "Permite probar tu código sin depender de servicios externos lentos o inestables." },
    { t: "opcion", q: "Una cobertura de código del 100 % significa que…",
      op: ["Todas las líneas se ejecutaron en las pruebas, pero eso no garantiza que no haya bugs", "El programa no tiene ningún error", "Todas las pruebas son perfectas", "El código es muy rápido"], ok: 0,
      exp: "Cubrir una línea no es lo mismo que comprobar que hace lo correcto." },
    { t: "ordenar", q: "Ordena el ciclo de corrección de un bug",
      piezas: ["Reproducir el error", "Encontrar la causa", "Corregir el código", "Ejecutar las pruebas de regresión"],
      exp: "Si no puedes reproducirlo no puedes asegurar que lo arreglaste." },
    { t: "caso", q: "Esta función cuenta las palabras de un texto, pero falla en algunos casos. Escribe un texto (entre comillas) que lo demuestre.", fn: "contarPalabras",
      defectuosa: r`function contarPalabras(texto) {
  return texto.split(" ").length;
}`,
      correcta: r`function contarPalabras(texto) {
  const limpio = texto.trim();
  return limpio === "" ? 0 : limpio.split(/\s+/).length;
}`,
      exp: "Con el texto vacío, o con espacios dobles como \"hola  mundo\", la versión defectuosa cuenta de más." },
  ] },
] },
];
