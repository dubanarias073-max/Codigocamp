"""JavaScript · Etapa 4: arrays y objetos."""
from ..generador import K

LISTA = [
K("Arrays",
  d="lista ordenada de valores guardados en una sola variable",
  u="manejar muchos datos relacionados a la vez",
  mas="Se escriben entre corchetes y separados por comas: [\"Ana\", \"Luis\"]. Cada elemento tiene una posición (índice) que empieza en 0. La propiedad length da cuántos elementos hay. Un array puede mezclar tipos, aunque lo habitual es que todos sean del mismo.",
  k=["Un array se escribe entre corchetes.", "Los índices de un array empiezan en 0.", "La propiedad length indica cuántos elementos tiene."],
  sit="Quieres guardar cinco nombres de alumnos en una sola variable. ¿Qué estructura usas?",
  cod="""const alumnos = ["Ana", "Luis", "Marta"];
console.log(alumnos[0]);         // Ana (el primero es el 0)
console.log(alumnos.length);     // 3
console.log(alumnos[alumnos.length - 1]);   // Marta (el último)""",
  h="muestra el primer elemento, la cantidad y el último de una lista",
  pr=("Un array se escribe entre ___. (corchetes)", "corchetes", "[]"),
  pr2=("El primer elemento de un array está en el índice ___. (un número)", "0", "cero"),
  ec="pedir el elemento en la posición length en lugar de length - 1"),
K("Añadir y quitar elementos",
  d="métodos que modifican los extremos de un array",
  u="agregar o eliminar elementos de una lista",
  mas="push añade al final y pop quita el último. unshift añade al principio y shift quita el primero. Todos modifican el array original. push y unshift devuelven la nueva longitud; pop y shift devuelven el elemento quitado.",
  k=["push añade un elemento al final.", "pop quita y devuelve el último elemento.", "unshift añade al principio y shift quita el primero."],
  sit="Quieres añadir un nombre al final de una lista ya creada. ¿Qué método usas?",
  cod="""const cola = ["Ana", "Luis"];
cola.push("Marta");               // final: Ana, Luis, Marta
cola.unshift("Pablo");            // principio: Pablo, Ana, Luis, Marta
const salio = cola.shift();       // quita y devuelve el primero
cola.pop();                       // quita el último
console.log(salio, cola);""",
  h="añade y quita elementos por los dos extremos de una lista",
  pr=("El método que añade un elemento al final es ___. (4 letras)", "push"),
  pr2=("El método que quita el primer elemento es ___. (5 letras)", "shift"),
  ec="confundir pop (final) con shift (principio)"),
K("Recorrer con for...of",
  d="bucle que recorre los elementos de un array uno a uno",
  u="procesar cada elemento sin manejar índices",
  mas="for (const x of lista) { ... } da en cada vuelta un elemento. Es más claro que el for clásico cuando no necesitas la posición. Para tener el índice también usa lista.entries() o el for clásico.",
  k=["for...of recorre cada elemento de un array.", "No hace falta manejar índices.", "Funciona con arrays, textos y otros iterables."],
  sit="Quieres mostrar cada nombre de una lista sin preocuparte por los índices. ¿Qué bucle usas?",
  cod="""const frutas = ["manzana", "pera", "uva"];
for (const fruta of frutas) {       // fruta toma cada elemento
  console.log("Me gusta la " + fruta);
}
for (const [i, fruta] of frutas.entries()) {   // con índice
  console.log(i, fruta);
}""",
  h="recorre una lista mostrando sus elementos, primero solos y luego con su índice",
  pr=("Para recorrer los elementos de un array se usa for...___. (2 letras)", "of"),
  pr2=("for...of ___ necesita manejar índices. (sí o no)", "no"),
  ec="usar for...in con arrays y recibir los índices como texto"),
K("forEach",
  d="método que ejecuta una función por cada elemento del array",
  u="aplicar una acción a todos los elementos",
  mas="lista.forEach((elemento, indice) => { ... }) llama a la función una vez por elemento. No devuelve nada y no se puede detener con break. Para transformar datos se prefiere map, y para filtrar, filter.",
  k=["forEach ejecuta una función por cada elemento.", "forEach no devuelve un array nuevo.", "No se puede detener con break."],
  sit="Quieres ejecutar una acción para cada elemento de una lista sin crear otra lista. ¿Qué método usas?",
  cod="""const notas = [7, 9, 5];
notas.forEach((nota, i) => {
  console.log(`Examen ${i + 1}: ${nota}`);
});
// forEach no devuelve nada
console.log(notas.forEach((n) => n));   // undefined""",
  h="muestra cada nota con su número de examen y comprueba que forEach no devuelve nada",
  pr=("El método que ejecuta una función por elemento es ___. (7 letras)", "foreach"),
  pr2=("forEach devuelve ___. (9 letras)", "undefined"),
  ec="usar forEach esperando un array nuevo con resultados"),
K("map",
  d="método que transforma cada elemento y devuelve un array nuevo",
  u="convertir una lista en otra del mismo tamaño",
  mas="lista.map((x) => x * 2) crea un array nuevo con el resultado de aplicar la función a cada elemento. No modifica el original. Se usa para pasar de precios a precios con IVA o de objetos a sus nombres.",
  k=["map devuelve un array nuevo del mismo tamaño.", "map no modifica el array original.", "Cada elemento se transforma con la función dada."],
  sit="Quieres obtener una lista con el doble de cada número de otra lista, sin modificarla. ¿Qué método usas?",
  cod="""const numeros = [1, 2, 3, 4];
const dobles = numeros.map((n) => n * 2);
console.log(dobles);        // [2, 4, 6, 8]
console.log(numeros);       // [1, 2, 3, 4] sigue igual
const nombres = [{ nombre: "Ana" }, { nombre: "Luis" }].map((p) => p.nombre);
console.log(nombres);""",
  h="duplica los números de una lista y extrae nombres de una lista de objetos",
  pr=("El método que transforma cada elemento en uno nuevo es ___. (3 letras)", "map"),
  pr2=("map devuelve un array ___. (5 letras: nuevo)", "nuevo"),
  ec="olvidar el return en map con llaves"),
K("filter",
  d="método que devuelve un array con los elementos que cumplen una condición",
  u="quedarse solo con ciertos elementos",
  mas="lista.filter((x) => x > 5) devuelve un array nuevo con los elementos para los que la función devolvió true. El array resultante puede tener menos elementos que el original. No modifica la lista inicial.",
  k=["filter devuelve los elementos que cumplen la condición.", "El array resultante puede ser más corto.", "filter no modifica el array original."],
  sit="Quieres quedarte solo con las notas aprobadas de una lista. ¿Qué método usas?",
  cod="""const notas = [4, 7, 9, 3, 6];
const aprobadas = notas.filter((n) => n >= 5);
console.log(aprobadas);       // [7, 9, 6]
console.log(notas.length, aprobadas.length);   // 5 3""",
  h="se queda solo con las notas aprobadas de una lista",
  pr=("El método que conserva solo los elementos que cumplen una condición es ___. (6 letras)", "filter"),
  pr2=("La función de filter debe devolver ___ o false. (4 letras)", "true"),
  ec="usar map cuando se quería filtrar"),
K("reduce",
  d="método que combina todos los elementos en un único valor",
  u="sumar, contar o acumular resultados",
  mas="lista.reduce((acumulado, actual) => acumulado + actual, 0) recorre la lista guardando un acumulador. El segundo argumento (0) es el valor inicial. Sirve para sumas, promedios, máximos o para construir un objeto.",
  k=["reduce combina todos los elementos en un solo valor.", "Usa un acumulador y un valor inicial.", "Sirve para sumas y recuentos."],
  sit="Quieres sumar todos los precios de un carrito en un solo número. ¿Qué método usas?",
  cod="""const precios = [10, 20, 5];
const total = precios.reduce((acumulado, precio) => acumulado + precio, 0);
console.log(total);           // 35
const maximo = precios.reduce((m, p) => (p > m ? p : m), precios[0]);
console.log(maximo);          // 20""",
  h="suma una lista de precios y encuentra el mayor con reduce",
  pr=("El método que reduce una lista a un solo valor es ___. (6 letras)", "reduce"),
  pr2=("El segundo argumento de reduce es el valor ___. (7 letras: inicial)", "inicial"),
  ec="olvidar el valor inicial en listas vacías"),
K("find e includes",
  d="métodos que buscan un elemento dentro de un array",
  u="saber si algo existe y obtenerlo",
  mas="find devuelve el primer elemento que cumpla la condición (o undefined). findIndex devuelve su posición (o -1). includes devuelve true o false según si el valor existe. indexOf devuelve la posición de un valor concreto.",
  k=["find devuelve el primer elemento que cumple la condición.", "includes devuelve true o false.", "findIndex devuelve -1 si no encuentra nada."],
  sit="Quieres comprobar si una lista de invitados contiene a «Ana». ¿Qué método usas?",
  cod="""const invitados = ["Ana", "Luis", "Marta"];
console.log(invitados.includes("Ana"));                  // true
console.log(invitados.indexOf("Marta"));                 // 2
const usuarios = [{ id: 1, nombre: "Ana" }, { id: 2, nombre: "Luis" }];
console.log(usuarios.find((u) => u.id === 2));           // { id: 2, nombre: 'Luis' }
console.log(usuarios.findIndex((u) => u.id === 99));     // -1""",
  h="busca un valor, una posición y un objeto dentro de listas",
  pr=("El método que devuelve true o false según si existe un valor es ___. (8 letras)", "includes"),
  pr2=("findIndex devuelve ___ si no encuentra nada. (2 caracteres)", "-1"),
  ec="usar == para comparar objetos dentro de includes"),
K("sort",
  d="método que ordena los elementos de un array",
  u="mostrar listas de menor a mayor o por texto",
  mas="sort ordena el array original. Atención: por defecto ordena como texto, así que [10, 9, 1] queda [1, 10, 9]. Para números hay que pasar una función: sort((a, b) => a - b) para ascendente. Para copiar antes de ordenar, usa [...lista].sort().",
  k=["sort modifica el array original.", "Por defecto, sort ordena como si fueran textos.", "Para ordenar números hay que usar (a, b) => a - b."],
  sit="Quieres ordenar números de menor a mayor correctamente. ¿Qué escribes?",
  cod="""const numeros = [10, 9, 1, 100];
console.log([...numeros].sort());                 // [1, 10, 100, 9] ¡como texto!
console.log([...numeros].sort((a, b) => a - b));  // [1, 9, 10, 100]
console.log([...numeros].sort((a, b) => b - a));  // de mayor a menor""",
  h="compara el orden de texto con el orden numérico correcto",
  pr=("Para ordenar números de menor a mayor se usa sort((a, b) => a ___ b). (un carácter)", "-"),
  pr2=("sort ordena por defecto como si fueran ___. (6 letras: textos)", "textos", "strings", "cadenas"),
  ec="ordenar números sin pasar una función de comparación"),
K("slice y splice",
  d="métodos para extraer o modificar una parte del array",
  u="copiar fragmentos o insertar y eliminar en el medio",
  mas="slice(inicio, fin) devuelve una copia de un fragmento sin modificar el array (el fin no se incluye). splice(inicio, cuantos, ...nuevos) sí modifica el original: borra y/o inserta elementos. Se confunden con frecuencia: slice copia y splice cambia.",
  k=["slice devuelve un fragmento sin modificar el original.", "splice modifica el array original.", "En slice, el índice final no se incluye."],
  sit="Quieres copiar solo los tres primeros elementos de una lista sin tocarla. ¿Qué método usas?",
  cod="""const letras = ["a", "b", "c", "d", "e"];
console.log(letras.slice(0, 3));       // ["a", "b", "c"]; letras no cambia
const copia = [...letras];
copia.splice(1, 2);                    // borra 2 elementos desde la posición 1
console.log(copia);                    // ["a", "d", "e"]
copia.splice(1, 0, "X");               // inserta sin borrar
console.log(copia);""",
  h="copia un fragmento de una lista y modifica otra insertando y borrando",
  pr=("El método que copia un fragmento sin modificar es ___. (5 letras)", "slice"),
  pr2=("El método que borra o inserta modificando el original es ___. (6 letras)", "splice"),
  ec="usar splice creyendo que no modifica el array"),
K("Spread y rest",
  d="operador ... que expande o agrupa elementos",
  u="copiar arrays, unirlos y recibir argumentos variables",
  mas="[...a, ...b] une dos arrays en uno nuevo y {...obj} copia un objeto. En la definición de una función, function sumar(...numeros) recoge todos los argumentos en un array (rest). Es una copia superficial: los objetos internos se comparten.",
  k=["Spread expande los elementos de un array u objeto.", "Rest agrupa los argumentos sobrantes en un array.", "La copia con spread es superficial."],
  sit="Quieres unir dos arrays en uno nuevo sin modificar los originales. ¿Qué operador usas?",
  cod="""const a = [1, 2], b = [3, 4];
console.log([...a, ...b, 5]);              // [1, 2, 3, 4, 5]
const persona = { nombre: "Ana", edad: 20 };
console.log({ ...persona, edad: 21 });     // copia y cambia un valor
function sumar(...numeros) {               // rest: recoge todos los argumentos
  return numeros.reduce((s, n) => s + n, 0);
}
console.log(sumar(1, 2, 3, 4));""",
  h="une arrays, copia un objeto cambiando un valor y suma argumentos variables",
  pr=("El operador que expande elementos se escribe con ___ puntos. (un número)", "3", "tres"),
  pr2=("En function f(...args), los argumentos se agrupan en un ___. (5 letras)", "array", "arreglo"),
  ec="creer que el spread copia también los objetos internos"),
K("Objetos",
  d="colección de pares clave-valor que describe una cosa",
  u="agrupar datos relacionados de una misma entidad",
  mas="Se escriben entre llaves: { nombre: \"Ana\", edad: 20 }. Cada propiedad tiene un nombre (clave) y un valor. Se accede con punto (persona.nombre) o con corchetes (persona[\"nombre\"]). Un objeto puede contener cualquier tipo, incluso otros objetos o funciones.",
  k=["Un objeto se escribe entre llaves con pares clave-valor.", "Se accede a una propiedad con punto o con corchetes.", "Un objeto puede contener otros objetos."],
  sit="Quieres guardar nombre, edad y ciudad de una persona en una sola variable. ¿Qué usas?",
  cod="""const persona = {
  nombre: "Ana",
  edad: 20,
  ciudad: "Lima",
};
console.log(persona.nombre);             // con punto
console.log(persona["ciudad"]);          // con corchetes
persona.edad = 21;                       // modificar
persona.correo = "ana@correo.com";       // añadir
console.log(persona);""",
  h="crea un objeto persona y lee, cambia y añade propiedades",
  pr=("Un objeto se escribe entre ___. (llaves)", "llaves", "{}"),
  pr2=("Cada propiedad de un objeto es un par clave y ___. (5 letras)", "valor"),
  ec="olvidar la coma entre propiedades"),
K("Métodos de objetos",
  d="funciones guardadas como propiedades de un objeto",
  u="darle acciones a los datos del objeto",
  mas="Un método es una función dentro de un objeto: { saludar() { ... } }. Dentro, this se refiere al propio objeto, así que this.nombre lee su propiedad. Cuidado: las funciones flecha no tienen this propio y no sirven como métodos.",
  k=["Un método es una función guardada en un objeto.", "Dentro de un método, this apunta al objeto.", "Las funciones flecha no son buenas como métodos."],
  sit="Quieres que un objeto persona tenga una acción para presentarse usando sus propios datos. ¿Qué defines?",
  cod="""const persona = {
  nombre: "Ana",
  presentarse() {
    return `Hola, soy ${this.nombre}`;    // this = el propio objeto
  },
};
console.log(persona.presentarse());""",
  h="define un método que usa this para leer los datos de su objeto",
  pr=("Dentro de un método, la palabra que se refiere al propio objeto es ___. (4 letras)", "this"),
  pr2=("Una función guardada dentro de un objeto es un ___. (6 letras: método)", "método", "metodo"),
  ec="usar una función flecha como método y perder this"),
K("Desestructuración",
  d="forma corta de extraer valores de arrays u objetos",
  u="sacar varias propiedades a variables en una línea",
  mas="const { nombre, edad } = persona crea las variables nombre y edad con los valores de esas propiedades. Con arrays, const [a, b] = lista toma por posición. Se pueden dar valores por defecto y renombrar: { nombre: n = \"sin nombre\" }.",
  k=["La desestructuración extrae valores en variables.", "Con objetos se usan llaves y con arrays corchetes.", "Se pueden dar valores por defecto."],
  sit="Quieres sacar nombre y edad de un objeto a dos variables en una sola línea. ¿Qué técnica usas?",
  cod="""const persona = { nombre: "Ana", edad: 20, ciudad: "Lima" };
const { nombre, edad } = persona;            // objeto: por nombre
console.log(nombre, edad);
const [primero, segundo] = ["rojo", "verde", "azul"];   // array: por posición
console.log(primero, segundo);
const { pais = "sin país" } = persona;       // valor por defecto
console.log(pais);""",
  h="extrae propiedades de un objeto y elementos de un array en variables",
  pr=("Con objetos, la desestructuración usa ___. (llaves)", "llaves", "{}"),
  pr2=("Con arrays, la desestructuración toma los valores por ___. (8 letras: posición)", "posición", "posicion"),
  ec="usar corchetes al desestructurar un objeto"),
K("Object.keys y entries",
  d="funciones que obtienen las claves y valores de un objeto",
  u="recorrer las propiedades de un objeto",
  mas="Object.keys(obj) devuelve un array con las claves, Object.values(obj) con los valores y Object.entries(obj) con pares [clave, valor]. Combinadas con for...of o forEach permiten recorrer cualquier objeto.",
  k=["Object.keys devuelve un array con las claves.", "Object.values devuelve un array con los valores.", "Object.entries devuelve pares clave-valor."],
  sit="Quieres recorrer todas las propiedades de un objeto para mostrarlas. ¿Qué funciones usas?",
  cod="""const precios = { pan: 1.2, leche: 0.9, huevos: 2.5 };
console.log(Object.keys(precios));      // ["pan", "leche", "huevos"]
console.log(Object.values(precios));    // [1.2, 0.9, 2.5]
for (const [producto, precio] of Object.entries(precios)) {
  console.log(`${producto}: ${precio}`);
}""",
  h="obtiene claves y valores de un objeto y los recorre en pares",
  pr=("La función que devuelve las claves de un objeto es Object.___(). (4 letras)", "keys"),
  pr2=("La función que devuelve pares clave-valor es Object.___(). (7 letras)", "entries"),
  ec="intentar recorrer un objeto con for...of sin entries"),
K("Encadenamiento opcional",
  d="operador ?. que evita errores al leer propiedades inexistentes",
  u="acceder a datos anidados que pueden no existir",
  mas="persona.direccion.calle falla si direccion es undefined. Con persona.direccion?.calle se devuelve undefined en lugar de error. El operador ?? da un valor por defecto solo cuando el resultado es null o undefined: persona.direccion?.calle ?? \"sin calle\".",
  k=["?. devuelve undefined si la propiedad intermedia no existe.", "?? da un valor por defecto si el resultado es null o undefined.", "Evita errores al leer datos anidados."],
  sit="Quieres leer la calle de una dirección que puede no existir sin que el programa falle. ¿Qué usas?",
  cod="""const persona = { nombre: "Ana" };          // no tiene dirección
// console.log(persona.direccion.calle);       // ¡daría error!
console.log(persona.direccion?.calle);         // undefined, sin error
console.log(persona.direccion?.calle ?? "sin calle");   // valor por defecto""",
  h="lee una propiedad anidada que no existe sin provocar un error",
  pr=("El operador de encadenamiento opcional se escribe ___. (2 caracteres)", "?."),
  pr2=("El operador que da un valor por defecto si hay null o undefined es ___. (2 caracteres)", "??"),
  ec="leer propiedades anidadas sin comprobar si existen"),
K("Arrays de objetos",
  d="listas donde cada elemento es un objeto",
  u="representar tablas de datos como usuarios o productos",
  mas="Es la estructura de datos más habitual en las aplicaciones: [{ id: 1, nombre: \"Ana\" }, { id: 2, nombre: \"Luis\" }]. Se combinan map, filter, find y sort para consultarla, como si fuera una base de datos pequeña.",
  k=["Un array de objetos representa una tabla de datos.", "Se consulta con map, filter, find y sort.", "Es la estructura de datos más habitual en las aplicaciones."],
  sit="Quieres guardar varios alumnos, cada uno con nombre y nota, y consultarlos. ¿Qué estructura usas?",
  cod="""const alumnos = [
  { nombre: "Ana", nota: 9 },
  { nombre: "Luis", nota: 5 },
  { nombre: "Marta", nota: 8 },
];
const aprobados = alumnos.filter((a) => a.nota >= 6).map((a) => a.nombre);
console.log(aprobados);                                      // ["Ana", "Marta"]
console.log(alumnos.find((a) => a.nombre === "Luis").nota);  // 5""",
  h="filtra y consulta una lista de alumnos con nombre y nota",
  pr=("Una lista de objetos es un array de ___. (8 letras)", "objetos"),
  pr2=("Para quedarte con los aprobados de una lista usas el método ___. (6 letras)", "filter"),
  ec="olvidar la propiedad al leer un valor del objeto"),
K("JSON",
  d="formato de texto para guardar e intercambiar datos",
  u="enviar datos entre programas y guardarlos",
  mas="JSON parece un objeto de JavaScript, pero es texto: las claves van entre comillas dobles y no admite funciones ni comentarios. JSON.stringify(objeto) lo convierte en texto y JSON.parse(texto) vuelve a convertirlo en objeto. Es el formato estándar de las API.",
  k=["JSON es un formato de texto para intercambiar datos.", "JSON.stringify convierte un objeto en texto.", "JSON.parse convierte un texto JSON en objeto."],
  sit="Quieres convertir un objeto en texto para guardarlo o enviarlo por internet. ¿Qué usas?",
  cod="""const persona = { nombre: "Ana", edad: 20 };
const texto = JSON.stringify(persona);      // objeto -> texto
console.log(texto);                         // {"nombre":"Ana","edad":20}
const vuelta = JSON.parse(texto);           // texto -> objeto
console.log(vuelta.nombre);
console.log(typeof texto, typeof vuelta);""",
  h="convierte un objeto en texto JSON y lo recupera",
  pr=("La función que convierte un objeto en texto JSON es JSON.___(). (9 letras)", "stringify"),
  pr2=("La función que convierte texto JSON en objeto es JSON.___(). (5 letras)", "parse"),
  ec="usar comillas simples en un JSON y recibir un error",
  err=("const texto = \"{'nombre': 'Ana'}\";\nconst obj = JSON.parse(texto);\nconsole.log(obj.nombre);", 2, "JSON exige comillas dobles en claves y textos: {\"nombre\": \"Ana\"}.")),
K("Copiar y comparar",
  d="diferencia entre copiar un valor y copiar una referencia",
  u="evitar cambios inesperados al copiar objetos y arrays",
  mas="Los números y textos se copian por valor. Los objetos y arrays se guardan por referencia: b = a no crea una copia, ambas variables apuntan al mismo objeto. Para copiar usa spread o structuredClone. Dos objetos distintos con el mismo contenido no son === entre sí.",
  k=["Los objetos se asignan por referencia, no por valor.", "b = a no crea una copia independiente de un objeto.", "Dos objetos con el mismo contenido no son iguales con ===."],
  sit="Al cambiar una copia de un array cambia también el original. ¿Qué concepto lo explica?",
  cod="""const a = [1, 2, 3];
const b = a;                  // NO es una copia: apunta al mismo array
b.push(4);
console.log(a);               // [1, 2, 3, 4]
const c = [...a];             // copia real
c.push(5);
console.log(a.length, c.length);
console.log([1] === [1]);     // false""",
  h="muestra que asignar no copia y que spread sí crea una copia",
  pr=("Los objetos se asignan por ___. (10 letras: referencia)", "referencia"),
  pr2=("Para copiar un array se puede usar el operador ___. (6 letras: spread)", "spread", "..."),
  ec="creer que b = a copia un array"),
K("Set y Map",
  d="colecciones modernas para valores únicos y pares clave-valor",
  u="quitar duplicados y asociar claves de cualquier tipo",
  mas="Un Set guarda valores sin repetir: new Set([1, 1, 2]) tiene dos elementos. Un Map asocia claves de cualquier tipo con valores, y recuerda el orden de inserción. [...new Set(lista)] es el truco clásico para quitar duplicados.",
  k=["Un Set no admite valores repetidos.", "Un Map asocia claves con valores de cualquier tipo.", "[...new Set(lista)] elimina duplicados."],
  sit="Quieres quitar los valores repetidos de una lista. ¿Qué estructura usas?",
  cod="""const repetidos = [1, 2, 2, 3, 3, 3];
const unicos = [...new Set(repetidos)];      // sin duplicados
console.log(unicos);                         // [1, 2, 3]
const edades = new Map();
edades.set("Ana", 20).set("Luis", 25);
console.log(edades.get("Ana"), edades.size); // 20 2""",
  h="elimina duplicados con un Set y guarda pares en un Map",
  pr=("La estructura que no admite valores repetidos es el ___. (3 letras)", "set"),
  pr2=("La estructura que asocia claves y valores de cualquier tipo es el ___. (3 letras)", "map"),
  ec="usar un array y comprobar duplicados a mano"),
K("Proyecto: lista de compras",
  d="programa que reúne arrays, objetos y funciones",
  u="practicar lo aprendido en un caso completo",
  mas="Para cerrar este bloque, crea una lista de compras: un array de objetos con nombre, precio y cantidad; una función que añade productos, otra que calcula el total y otra que muestra el resumen. Usa map, filter y reduce.",
  k=["Un proyecto pequeño combina arrays, objetos y funciones.", "reduce sirve para calcular el total del carrito.", "Dividir en funciones hace el programa más claro."],
  sit="Quieres cerrar este bloque con un programa que gestione una lista de compras con totales. ¿Qué construyes?",
  cod="""const carrito = [];
function agregar(nombre, precio, cantidad = 1) {
  carrito.push({ nombre, precio, cantidad });
}
function total() {
  return carrito.reduce((suma, p) => suma + p.precio * p.cantidad, 0);
}
agregar("Pan", 1.2, 2);
agregar("Leche", 0.9);
console.log(carrito.map((p) => `${p.nombre} x${p.cantidad}`));
console.log("Total:", total().toFixed(2));""",
  h="gestiona un carrito con funciones para añadir productos y calcular el total",
  pr=("El método que suma los precios del carrito es ___. (6 letras)", "reduce"),
  pr2=("Un carrito de la compra suele ser un array de ___. (8 letras)", "objetos"),
  ec="repetir el cálculo del total en varios sitios en lugar de usar una función"),
]
