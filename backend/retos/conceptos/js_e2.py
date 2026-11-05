"""JavaScript · Etapa 2: variables, tipos y operadores."""
from ..generador import K

LISTA = [
K("let",
  d="palabra que declara una variable cuyo valor puede cambiar",
  u="guardar datos que se modificarán durante el programa",
  mas="let crea una variable con alcance de bloque: solo existe dentro de las llaves donde se declaró. Puedes reasignarle valores, pero no declararla dos veces con el mismo nombre en el mismo bloque. Es la opción para contadores y datos que cambian.",
  k=["let declara una variable cuyo valor puede cambiar.", "Una variable let solo existe dentro de su bloque.", "No se puede declarar dos veces el mismo let en un bloque."],
  sit="Quieres un contador que empieza en 0 y aumenta durante el programa. ¿Qué palabra usas para declararlo?",
  cod="""let puntos = 0;            // se declara con let
console.log(puntos);       // 0
puntos = puntos + 10;      // se puede cambiar
console.log(puntos);       // 10""",
  h="declara un contador y cambia su valor",
  pr=("Para declarar una variable que cambiará usamos la palabra ___. (3 letras)", "let"),
  pr2=("Una variable let solo existe dentro de su ___. (5 letras: bloque)", "bloque"),
  ec="declarar dos veces la misma variable con let",
  err=("let puntos = 0;\nlet puntos = 5;\nconsole.log(puntos);", 2, "No se puede declarar otra vez puntos con let; basta con asignarle un valor nuevo.")),
K("const",
  d="palabra que declara una constante que no se reasigna",
  u="guardar datos que no deben cambiar",
  mas="const exige un valor al declararla y no permite reasignarlo. Es la opción por defecto en JavaScript moderno: usa const siempre y cambia a let solo si necesitas reasignar. Ojo: un array o un objeto const sí puede modificar su contenido, aunque no ser reasignado.",
  k=["const declara una variable que no se reasigna.", "Una constante debe tener un valor al declararla.", "Un objeto declarado con const sí puede cambiar su contenido."],
  sit="Quieres guardar el valor de PI, que nunca debe cambiar. ¿Qué palabra usas?",
  cod="""const PI = 3.1416;               // no se podrá reasignar
console.log(PI);
try {
  PI = 3;                        // intento de cambiarla
} catch (error) {
  console.log(error.name);       // TypeError
}""",
  h="intenta cambiar una constante y muestra el error que produce",
  pr=("Para declarar un valor que no se reasigna usamos ___. (5 letras)", "const"),
  pr2=("Al reasignar una constante ocurre un ___Error. (4 letras: Type)", "type"),
  ec="usar let para todo cuando bastaba const",
  err=("const edad = 20;\nedad = 21;\nconsole.log(edad);", 2, "Una constante no puede reasignarse: habría que declarar edad con let.")),
K("var",
  d="forma antigua de declarar variables con alcance de función",
  u="entender código antiguo y evitar sus problemas",
  mas="Antes de 2015 solo existía var. Su alcance es la función entera (no el bloque) y permite redeclarar la variable, lo que provoca errores difíciles de ver. Se «eleva» (hoisting) al principio del alcance, con valor undefined. Hoy se prefieren let y const.",
  k=["var tiene alcance de función, no de bloque.", "var permite declarar dos veces el mismo nombre.", "Hoy se prefieren let y const."],
  sit="Lees un código antiguo que declara variables con una palabra que hoy se evita. ¿Cuál es?",
  cod="""if (true) {
  var a = "visible fuera del bloque";
  let b = "solo dentro del bloque";
}
console.log(a);                      // funciona
console.log(typeof b);               // undefined: b no existe aquí""",
  h="compara una variable var, visible fuera del bloque, con una let que no lo es",
  pr=("La forma antigua de declarar variables es ___. (3 letras)", "var"),
  pr2=("var tiene alcance de ___. (7 letras: función)", "función", "funcion"),
  ec="usar var por costumbre y provocar variables que se filtran"),
K("Nombres de variables",
  d="reglas y convenciones para escribir identificadores",
  u="que el código se lea y se entienda con facilidad",
  mas="Pueden contener letras, números, _ y $, pero no empezar por número ni usar palabras reservadas como let o function. JavaScript distingue mayúsculas de minúsculas: edad y Edad son distintas. La convención es camelCase: nombreCompleto, edadMinima. Elige nombres que expliquen su contenido.",
  k=["Un nombre de variable no puede empezar con un número.", "JavaScript distingue entre mayúsculas y minúsculas.", "La convención habitual es camelCase."],
  sit="Quieres nombrar una variable de varias palabras con el estilo habitual de JavaScript. ¿Qué convención usas?",
  cod="""const nombreCompleto = "Ana Pérez";    // camelCase
const edadMinima = 18;
let Total = 1;
let total = 2;                          // distinta de Total
console.log(nombreCompleto, edadMinima, Total, total);""",
  h="usa camelCase y muestra que mayúsculas y minúsculas son nombres distintos",
  pr=("El estilo nombreCompleto, con mayúscula en cada palabra nueva, se llama ___Case. (5 letras: camel)", "camel"),
  pr2=("Un nombre de variable no puede empezar con un ___. (6 letras: número)", "número", "numero"),
  ec="usar nombres como x1 o dato sin significado",
  err=("let 2edad = 20;\nconsole.log(2edad);", 1, "Un nombre de variable no puede empezar con un número.")),
K("Strings",
  d="tipo de dato para guardar texto entre comillas",
  u="trabajar con nombres, frases y mensajes",
  mas="Un string se escribe entre comillas simples, dobles o invertidas. Cada carácter tiene una posición que empieza en 0: «Hola»[0] es «H». La propiedad length da el número de caracteres. Los strings son inmutables: sus métodos devuelven un texto nuevo.",
  k=["Un string se escribe entre comillas.", "La primera posición de un texto es la 0.", "La propiedad length indica cuántos caracteres tiene."],
  sit="Quieres guardar el nombre «Ana» como un dato de texto. ¿Qué tipo usas?",
  cod="""const saludo = "Hola, mundo";
console.log(saludo.length);      // 11 caracteres
console.log(saludo[0]);          // H (la primera posición es 0)
console.log(saludo.toUpperCase());   // devuelve un texto nuevo""",
  h="mide un texto, toma su primera letra y lo pasa a mayúsculas",
  pr=("La propiedad que da el número de caracteres es ___. (6 letras)", "length"),
  pr2=("La primera posición de un texto es la ___. (un número)", "0", "cero"),
  ec="creer que la primera letra está en la posición 1"),
K("Numbers",
  d="tipo de dato para guardar números enteros y decimales",
  u="hacer cálculos matemáticos",
  mas="En JavaScript todos los números son del mismo tipo: number, tanto enteros (5) como decimales (3.14). Se escriben sin comillas. Los decimales usan punto, no coma. Existen valores especiales como Infinity y NaN.",
  k=["JavaScript usa un único tipo number para enteros y decimales.", "Los decimales se escriben con punto.", "Los números no llevan comillas."],
  sit="Quieres guardar el precio 4.5 para poder hacer cálculos con él. ¿Qué tipo usas?",
  cod="""const entero = 42;
const decimal = 3.14;       // punto decimal, no coma
console.log(entero + decimal);
console.log(typeof entero, typeof decimal);   // ambos son number""",
  h="suma un entero y un decimal y muestra que ambos son del mismo tipo",
  pr=("Los decimales en JavaScript se escriben con ___ decimal. (5 letras: punto)", "punto"),
  pr2=("El tipo de dato de enteros y decimales es ___. (6 letras)", "number"),
  ec="escribir un decimal con coma"),
K("Booleanos",
  d="tipo de dato con solo dos valores: true o false",
  u="tomar decisiones según una condición",
  mas="true y false se escriben sin comillas y en minúscula. Aparecen como resultado de comparaciones (5 > 3 es true) y controlan las decisiones del programa. «true» entre comillas sería un texto, no un booleano.",
  k=["Un booleano solo puede ser true o false.", "Las comparaciones devuelven booleanos.", "true entre comillas es un texto, no un booleano."],
  sit="Quieres guardar si un usuario ha iniciado sesión (sí o no). ¿Qué tipo usas?",
  cod="""const mayorDeEdad = 20 >= 18;      // el resultado es true
const premium = false;
console.log(mayorDeEdad, premium);
console.log(typeof mayorDeEdad);   // boolean""",
  h="obtiene un booleano de una comparación y guarda otro directamente",
  pr=("Los dos valores de un booleano son true y ___. (5 letras)", "false"),
  pr2=("Una comparación devuelve un valor ___. (7 letras)", "booleano", "boolean"),
  ec="escribir True con mayúscula inicial"),
K("null y undefined",
  d="dos valores especiales que representan la ausencia de dato",
  u="distinguir «no asignado» de «vacío a propósito»",
  mas="undefined es lo que tiene una variable declarada pero sin valor. null es un vacío que asignas tú a propósito para indicar «aquí no hay nada». Ambos son falsy. Comprueba con === null o === undefined, o usa ?? para dar un valor por defecto.",
  k=["undefined significa que la variable no tiene valor asignado.", "null es un vacío asignado a propósito.", "Ambos valores se consideran falsy."],
  sit="Declaraste una variable pero todavía no le diste ningún valor. ¿Qué valor contiene?",
  cod="""let sinValor;                  // declarada pero sin asignar
console.log(sinValor);          // undefined
const vacio = null;             // vacío puesto a propósito
console.log(vacio);             // null
console.log(typeof sinValor, typeof vacio);""",
  h="compara una variable sin valor con un vacío asignado a propósito",
  pr=("Una variable declarada sin valor contiene ___. (9 letras)", "undefined"),
  pr2=("El vacío asignado a propósito se escribe ___. (4 letras)", "null"),
  ec="confundir null con undefined"),
K("typeof",
  d="operador que devuelve el tipo de un dato",
  u="comprobar de qué tipo es un valor",
  mas="typeof 5 da \"number\", typeof \"a\" da \"string\" y typeof true da \"boolean\". Curiosidad: typeof null da \"object\" (un error histórico del lenguaje) y typeof de una función da \"function\". Es útil para validar datos antes de usarlos.",
  k=["typeof devuelve el tipo de un valor como texto.", "typeof null devuelve «object» por un error histórico.", "typeof de una función devuelve «function»."],
  sit="Quieres saber de qué tipo es una variable antes de operar con ella. ¿Qué operador usas?",
  cod="""console.log(typeof 5);               // number
console.log(typeof "hola");          // string
console.log(typeof true);            // boolean
console.log(typeof undefined);       // undefined
console.log(typeof null);            // object (error histórico)
console.log(typeof function () {});  // function""",
  h="muestra el tipo de seis valores distintos, incluido el curioso caso de null",
  pr=("El operador que devuelve el tipo de un valor es ___. (6 letras)", "typeof"),
  pr2=("typeof null devuelve el texto «___». (6 letras: object)", "object"),
  ec="olvidar que typeof null es object"),
K("Operadores aritméticos",
  d="símbolos para sumar, restar, multiplicar, dividir y más",
  u="hacer cálculos con números",
  mas="+ suma, - resta, * multiplica, / divide, % da el resto de una división y ** eleva a una potencia. La multiplicación y la división se evalúan antes que la suma y la resta; usa paréntesis para cambiar el orden. El resto (%) sirve, por ejemplo, para saber si un número es par.",
  k=["El operador % devuelve el resto de una división.", "El operador ** eleva a una potencia.", "Los paréntesis cambian el orden de las operaciones."],
  sit="Quieres saber si un número es par comprobando el resto de dividirlo entre 2. ¿Qué operador usas?",
  cod="""console.log(7 + 3, 7 - 3, 7 * 3);
console.log(7 / 2);          // 3.5
console.log(7 % 2);          // 1 (resto)
console.log(2 ** 3);         // 8
console.log((2 + 3) * 4);    // 20 (los paréntesis mandan)""",
  h="muestra los operadores aritméticos y el efecto de los paréntesis",
  pr=("El operador que da el resto de una división es ___. (un carácter)", "%"),
  pr2=("El operador que eleva a una potencia es ___. (2 caracteres)", "**"),
  ec="olvidar que * y / se calculan antes que + y -"),
K("Asignación compuesta",
  d="operadores que modifican una variable a partir de su valor actual",
  u="escribir más corto operaciones como contar o acumular",
  mas="x += 5 equivale a x = x + 5. Existen -=, *=, /= y %=. Para sumar o restar uno hay ++ y --. Son muy comunes en bucles y contadores.",
  k=["x += 5 equivale a x = x + 5.", "++ aumenta una variable en uno.", "Los operadores compuestos acortan el código."],
  sit="Quieres sumar 10 a una variable de puntos escribiendo lo menos posible. ¿Qué operador usas?",
  cod="""let puntos = 10;
puntos += 5;       // 15
puntos *= 2;       // 30
puntos -= 10;      // 20
puntos++;          // 21
console.log(puntos);""",
  h="modifica una variable con cuatro operadores compuestos distintos",
  pr=("Escribe el operador que suma y asigna a la vez (2 caracteres).", "+="),
  pr2=("El operador que aumenta en uno una variable es ___. (2 caracteres)", "++"),
  ec="escribir =+ en lugar de +="),
K("Igualdad estricta",
  d="comparación con === que revisa valor y tipo",
  u="comparar sin conversiones sorpresa",
  mas="== convierte los tipos antes de comparar y da resultados extraños: 5 == \"5\" es true. === compara valor y tipo: 5 === \"5\" es false. Usa siempre === y !== salvo que sepas muy bien por qué usar ==.",
  k=["=== compara valor y tipo.", "== convierte los tipos antes de comparar.", "Se recomienda usar siempre === y !==."],
  sit="Quieres comparar 5 con «5» sin que JavaScript los convierta. ¿Qué operador usas?",
  cod="""console.log(5 == "5");      // true  (convierte el texto)
console.log(5 === "5");     // false (distinto tipo)
console.log(5 !== "5");     // true
console.log(0 == false);    // true  (¡sorpresa!)
console.log(0 === false);   // false""",
  h="compara igualdad con conversión y sin ella para ver las diferencias",
  pr=("El operador de igualdad estricta es ___. (3 caracteres)", "==="),
  pr2=("La desigualdad estricta se escribe ___. (3 caracteres)", "!=="),
  ec="usar == y sufrir conversiones inesperadas",
  err=("const a = 5;\nconst b = \"5\";\nif (a = b) console.log(\"iguales\");", 3, "Se usó = (asignación) en vez de === (comparación).")),
K("Operadores lógicos",
  d="operadores que combinan valores booleanos",
  u="tomar decisiones con varias condiciones",
  mas="&& (y) es true si ambas condiciones son true. || (o) es true si al menos una lo es. ! (no) invierte el valor. Evalúan de izquierda a derecha y se detienen en cuanto conocen el resultado (cortocircuito).",
  k=["&& exige que se cumplan las dos condiciones.", "|| exige que se cumpla al menos una.", "! invierte un valor booleano."],
  sit="Quieres comprobar que alguien es mayor de edad y además tiene entrada. ¿Qué operador usas?",
  cod="""const edad = 20;
const tieneEntrada = true;
console.log(edad >= 18 && tieneEntrada);   // true: se cumplen las dos
console.log(edad < 18 || tieneEntrada);    // true: basta con una
console.log(!tieneEntrada);                // false: invierte""",
  h="combina condiciones con y, o y no",
  pr=("El operador lógico «y» es ___. (2 caracteres)", "&&"),
  pr2=("El operador lógico «o» es ___. (2 caracteres)", "||"),
  ec="usar & en lugar de &&"),
K("Plantillas de texto",
  d="textos entre comillas invertidas que incluyen valores con ${}",
  u="construir frases con variables de forma clara",
  mas="Con comillas invertidas puedes escribir `Hola, ${nombre}` y JavaScript reemplaza ${nombre} por su valor. Dentro de ${} puedes poner cualquier expresión. Además, permiten escribir texto en varias líneas sin símbolos especiales.",
  k=["Las plantillas de texto usan comillas invertidas.", "${expresión} inserta un valor dentro del texto.", "Permiten escribir texto de varias líneas."],
  sit="Quieres construir la frase «Hola, Ana, tienes 20 años» insertando variables sin concatenar con +. ¿Qué usas?",
  cod="""const nombre = "Ana";
const edad = 20;
console.log(`Hola, ${nombre}, tienes ${edad} años`);
console.log(`El año que viene tendrás ${edad + 1}`);   // admite expresiones""",
  h="inserta variables y un cálculo dentro de una frase",
  pr=("Las plantillas de texto se escriben entre comillas ___. (9 letras: invertidas)", "invertidas"),
  pr2=("Dentro de una plantilla, los valores se insertan con ${___}. (una palabra: expresión)", "expresión", "expresion", "variable"),
  ec="usar comillas normales y esperar que ${} funcione"),
K("Conversión de tipos",
  d="cambiar un dato de un tipo a otro",
  u="operar con números que llegan como texto",
  mas="Number(\"42\") convierte texto en número, String(42) convierte un número en texto y parseInt o parseFloat extraen números de textos. Los datos que llegan de formularios son siempre texto, así que hay que convertirlos antes de calcular.",
  k=["Number() convierte un texto en número.", "String() convierte un valor en texto.", "Los datos de un formulario llegan siempre como texto."],
  sit="Recibes «42» como texto desde un formulario y necesitas sumarle 1. ¿Qué haces primero?",
  cod="""const texto = "42";
console.log(texto + 1);              // "421" (concatena)
console.log(Number(texto) + 1);      // 43 (suma de verdad)
console.log(String(7) + "!");        // "7!"
console.log(parseInt("15 años"));    // 15""",
  h="compara concatenar con sumar tras convertir el texto a número",
  pr=("La función que convierte un texto en número es ___(). (6 letras)", "number"),
  pr2=("«42» + 1 en JavaScript da «___». (3 caracteres)", "421"),
  ec="sumar el valor de un formulario sin convertirlo a número"),
K("NaN",
  d="valor especial que significa «no es un número»",
  u="detectar cálculos con datos inválidos",
  mas="NaN aparece cuando una operación numérica no tiene sentido: Number(\"hola\") o 0/0. Curiosamente, typeof NaN es \"number\" y NaN no es igual ni a sí mismo. Para detectarlo usa Number.isNaN(valor).",
  k=["NaN aparece cuando una operación numérica no es válida.", "NaN no es igual a sí mismo.", "Se detecta con Number.isNaN()."],
  sit="Una conversión de «hola» a número da un resultado que significa «no es un número». ¿Qué valor es?",
  cod="""const r = Number("hola");
console.log(r);                  // NaN
console.log(r === NaN);          // false (NaN no es igual a nada)
console.log(Number.isNaN(r));    // true  (la forma correcta de detectarlo)
console.log(typeof NaN);         // number""",
  h="provoca un NaN y lo detecta con la comprobación correcta",
  pr=("La función para detectar NaN es Number.is___(). (3 letras)", "nan"),
  pr2=("NaN significa Not a ___. (6 letras: Number)", "number"),
  ec="comparar con === NaN para detectarlo"),
K("Objeto Math",
  d="objeto con funciones y constantes matemáticas",
  u="redondear, elegir mínimos y máximos o generar azar",
  mas="Math.round redondea al entero más cercano, Math.floor hacia abajo y Math.ceil hacia arriba. Math.max y Math.min devuelven el mayor y menor. Math.random da un decimal aleatorio entre 0 y 1: multiplicado y redondeado sirve para dados o sorteos.",
  k=["Math.round redondea al entero más cercano.", "Math.random devuelve un número entre 0 y 1.", "Math.max devuelve el mayor de varios números."],
  sit="Quieres simular una tirada de dado de 1 a 6. ¿Qué objeto usas?",
  cod="""console.log(Math.round(4.6), Math.floor(4.6), Math.ceil(4.2));   // 5 4 5
console.log(Math.max(3, 9, 5), Math.min(3, 9, 5));                // 9 3
const dado = Math.floor(Math.random() * 6) + 1;                   // 1 a 6
console.log(dado >= 1 && dado <= 6);""",
  h="redondea de tres maneras, busca máximos y mínimos y simula un dado",
  pr=("La función que devuelve un número aleatorio es Math.___(). (6 letras)", "random"),
  pr2=("La función que redondea hacia abajo es Math.___(). (5 letras)", "floor"),
  ec="olvidar que Math.random nunca llega a 1"),
K("Métodos de string",
  d="funciones propias de los textos para transformarlos o buscar en ellos",
  u="limpiar, buscar y cambiar textos",
  mas="toUpperCase y toLowerCase cambian las letras; trim quita espacios sobrantes; includes comprueba si contiene un texto; replace sustituye; slice extrae un fragmento; split divide el texto en un array. Todos devuelven un resultado nuevo sin modificar el original.",
  k=["trim elimina los espacios del principio y del final.", "includes comprueba si un texto contiene otro.", "Los métodos de string no modifican el original."],
  sit="Quieres quitar los espacios sobrantes del principio y del final de lo que escribió el usuario. ¿Qué método usas?",
  cod="""const frase = "  Aprendo JavaScript  ";
console.log(frase.trim());                 // sin espacios en los extremos
console.log(frase.includes("Java"));       // true
console.log(frase.replace("Aprendo", "Disfruto").trim());
console.log("a,b,c".split(","));           // ["a", "b", "c"]
console.log("JavaScript".slice(0, 4));     // Java""",
  h="limpia, busca, reemplaza, divide y recorta un texto",
  pr=("El método que quita espacios de los extremos es ___. (4 letras)", "trim"),
  pr2=("El método que divide un texto en un array es ___. (5 letras)", "split"),
  ec="creer que replace modifica el texto original"),
K("Truthy y falsy",
  d="valores que se comportan como verdadero o falso en una condición",
  u="escribir condiciones más cortas",
  mas="Los valores falsy son false, 0, \"\" (texto vacío), null, undefined y NaN. Todo lo demás es truthy, incluidos \"0\", [] y {}. Por eso if (nombre) es verdadero si hay un nombre escrito. Con !! conviertes cualquier valor a booleano.",
  k=["0, texto vacío, null, undefined y NaN son falsy.", "Un array vacío es truthy.", "!! convierte cualquier valor en un booleano."],
  sit="Quieres saber si una variable de texto contiene algo, sin escribir una comparación larga. ¿Qué concepto aprovechas?",
  cod="""console.log(Boolean(0), Boolean(""), Boolean(null));      // falsy: false false false
console.log(Boolean("0"), Boolean([]), Boolean({}));      // truthy: true true true
const nombre = "";
if (!nombre) console.log("No escribiste tu nombre");""",
  h="muestra qué valores se consideran falsos y cuáles verdaderos",
  pr=("El valor 0 se considera ___. (5 letras: falsy)", "falsy", "falso"),
  pr2=("Un array vacío se considera ___. (6 letras: truthy)", "truthy", "verdadero"),
  ec="pensar que un array vacío es falsy"),
K("Operador ternario",
  d="forma corta de elegir entre dos valores según una condición",
  u="escribir un if simple en una sola línea",
  mas="Se escribe condición ? valorSiVerdadero : valorSiFalso. Es perfecto para asignar un valor u mostrar un texto según una condición sencilla. Si la lógica se complica, es mejor un if normal.",
  k=["El operador ternario tiene la forma condición ? a : b.", "Devuelve un valor, no solo ejecuta código.", "Para lógica complicada es mejor un if normal."],
  sit="Quieres guardar «Adulto» o «Menor» según la edad escribiendo solo una línea. ¿Qué usas?",
  cod="""const edad = 16;
const etiqueta = edad >= 18 ? "Adulto" : "Menor";
console.log(etiqueta);                          // Menor
console.log(`Tienes ${edad} años: ${edad >= 18 ? "puedes votar" : "aún no votas"}`);""",
  h="elige un texto según la edad con una expresión de una línea",
  pr=("El operador ternario se escribe condición ? a ___ b. (un carácter)", ":"),
  pr2=("El ternario es una forma corta de un ___. (2 letras: if)", "if"),
  ec="anidar muchos ternarios hasta que nadie lo entienda"),
]
