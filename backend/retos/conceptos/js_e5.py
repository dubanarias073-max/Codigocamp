"""JavaScript · Etapa 5: DOM, eventos y asincronía."""
from ..generador import K

LISTA = [
K("querySelector",
  d="método que busca un elemento de la página con un selector CSS",
  u="obtener elementos del DOM para leerlos o cambiarlos",
  mas="document.querySelector(\"#titulo\") devuelve el primer elemento que coincida con el selector CSS (o null si no existe). querySelectorAll devuelve todos. Guarda el resultado en una constante para usarlo varias veces.",
  k=["querySelector usa selectores CSS para buscar elementos.", "querySelector devuelve el primero que coincida.", "querySelectorAll devuelve todos los que coincidan."],
  sit="Quieres obtener el elemento con id «titulo» para cambiarlo desde JavaScript. ¿Qué método usas?",
  cod="""document.body.innerHTML = '<h1 id="titulo">Hola</h1><p class="aviso">Uno</p><p class="aviso">Dos</p>';
const titulo = document.querySelector("#titulo");        // el primero que coincide
const avisos = document.querySelectorAll(".aviso");       // todos los que coinciden
console.log(titulo.textContent, avisos.length);""",
  h="busca un título por su id y cuenta los párrafos con una clase",
  pr=("El método que busca el primer elemento con un selector CSS es document.___(). (13 letras)", "queryselector"),
  pr2=("Para obtener todos los que coinciden se usa querySelector___. (3 letras)", "all"),
  ec="olvidar el # o el punto en el selector"),
K("textContent e innerHTML",
  d="propiedades que leen o cambian el contenido de un elemento",
  u="mostrar texto o HTML nuevo en la página",
  mas="textContent trata todo como texto plano y es seguro. innerHTML interpreta el texto como HTML, lo que permite insertar etiquetas, pero si incluyes datos de un usuario puede permitir ataques (XSS). Usa textContent siempre que no necesites HTML.",
  k=["textContent muestra el contenido como texto plano.", "innerHTML interpreta el contenido como HTML.", "innerHTML con datos de usuarios puede ser peligroso."],
  sit="Quieres mostrar el nombre que escribió un usuario sin que se interprete como HTML. ¿Qué propiedad usas?",
  cod="""document.body.innerHTML = '<p id="a"></p><p id="b"></p>';
const texto = "<b>negrita</b>";
document.querySelector("#a").textContent = texto;   // se ve literalmente: <b>negrita</b>
document.querySelector("#b").innerHTML = texto;     // se interpreta: negrita
console.log(document.querySelector("#a").textContent);
console.log(document.querySelector("#b").innerHTML);""",
  h="muestra el mismo texto como texto literal y como HTML interpretado",
  pr=("La propiedad segura para mostrar texto es ___. (11 letras)", "textcontent"),
  pr2=("La propiedad que interpreta el contenido como HTML es ___. (9 letras)", "innerhtml"),
  ec="usar innerHTML con datos escritos por usuarios"),
K("Atributos y estilos",
  d="formas de cambiar atributos HTML y estilos desde JavaScript",
  u="modificar enlaces, imágenes y apariencia de forma dinámica",
  mas="elemento.setAttribute(\"href\", \"...\") y getAttribute leen o cambian atributos. elemento.style.color = \"red\" cambia estilos en línea, con propiedades en camelCase (backgroundColor, no background-color). Para cambios de estilo más grandes es mejor alternar clases CSS.",
  k=["setAttribute cambia el atributo de un elemento.", "elemento.style cambia estilos en línea.", "Las propiedades de style se escriben en camelCase."],
  sit="Quieres cambiar el color de fondo de un elemento desde el código. ¿Qué usas?",
  cod="""document.body.innerHTML = '<a id="enlace" href="#">Enlace</a>';
const enlace = document.querySelector("#enlace");
enlace.setAttribute("href", "https://ejemplo.com");   // cambia un atributo
enlace.style.backgroundColor = "gold";                // camelCase
enlace.style.fontSize = "24px";
console.log(enlace.getAttribute("href"), enlace.style.backgroundColor);""",
  h="cambia un atributo y dos estilos de un enlace",
  pr=("El método que cambia un atributo es ___(nombre, valor). (12 letras)", "setattribute"),
  pr2=("La propiedad CSS background-color en JavaScript se escribe background___. (5 letras: Color)", "color"),
  ec="escribir background-color con guion en style"),
K("classList",
  d="propiedad que añade, quita o alterna clases de un elemento",
  u="cambiar el aspecto de un elemento con clases CSS",
  mas="classList.add(\"activo\") añade una clase, remove la quita, toggle la alterna (la añade si no está y la quita si está) y contains comprueba si la tiene. Es la forma recomendada de cambiar estilos: el CSS define el aspecto y JavaScript solo decide cuándo.",
  k=["classList.add añade una clase.", "classList.toggle alterna una clase.", "Cambiar clases es mejor que cambiar estilos en línea."],
  sit="Quieres activar y desactivar el modo oscuro alternando una clase de un elemento. ¿Qué método usas?",
  cod="""document.body.innerHTML = '<div id="caja">Hola</div>';
const caja = document.querySelector("#caja");
caja.classList.add("activo");
console.log(caja.classList.contains("activo"));   // true
caja.classList.toggle("activo");                  // la quita porque estaba
console.log(caja.classList.contains("activo"));   // false""",
  h="añade, comprueba y alterna una clase de un elemento",
  pr=("El método que añade o quita una clase según esté o no es classList.___(). (6 letras)", "toggle"),
  pr2=("El método que comprueba si un elemento tiene una clase es classList.___(). (8 letras)", "contains"),
  ec="escribir un punto delante del nombre de la clase en classList"),
K("createElement y append",
  d="métodos para crear elementos nuevos y añadirlos a la página",
  u="generar contenido dinámico, como listas o tarjetas",
  mas="document.createElement(\"li\") crea el elemento en memoria. Después le pones contenido (textContent) y lo añades con padre.append(elemento). Hasta que lo añadas al DOM no se ve. Es más seguro que construir HTML con textos.",
  k=["createElement crea un elemento nuevo.", "append añade un elemento dentro de otro.", "Un elemento no se ve hasta añadirlo al DOM."],
  sit="Quieres añadir un nuevo elemento a una lista desde JavaScript. ¿Qué métodos usas?",
  cod="""document.body.innerHTML = '<ul id="lista"></ul>';
const lista = document.querySelector("#lista");
for (const nombre of ["Ana", "Luis", "Marta"]) {
  const li = document.createElement("li");   // se crea en memoria
  li.textContent = nombre;                   // se le da contenido
  lista.append(li);                          // se añade al DOM
}
console.log(lista.children.length);          // 3""",
  h="crea tres elementos de lista y los añade a la página",
  pr=("El método que crea un elemento nuevo es document.___(). (13 letras)", "createelement"),
  pr2=("El método que añade un elemento dentro de otro es ___(). (6 letras)", "append", "appendchild"),
  ec="crear el elemento y olvidarse de añadirlo a la página"),
K("Eliminar elementos",
  d="métodos para quitar elementos del DOM",
  u="borrar contenido que ya no se necesita",
  mas="elemento.remove() elimina ese elemento de la página. Para vaciar un contenedor se usa contenedor.replaceChildren() o contenedor.textContent = \"\". Los elementos eliminados ya no se ven, pero la variable que los guardaba aún existe en memoria.",
  k=["elemento.remove() elimina un elemento del DOM.", "replaceChildren() vacía un contenedor.", "Una variable puede seguir guardando un elemento ya eliminado."],
  sit="Quieres borrar de la página un elemento concreto. ¿Qué método usas?",
  cod="""document.body.innerHTML = '<ul id="l"><li>Uno</li><li>Dos</li><li>Tres</li></ul>';
const lista = document.querySelector("#l");
lista.firstElementChild.remove();          // quita «Uno»
console.log(lista.children.length);        // 2
lista.replaceChildren();                   // vacía la lista
console.log(lista.children.length);        // 0""",
  h="quita un elemento y luego vacía toda la lista",
  pr=("El método que elimina un elemento del DOM es ___(). (6 letras)", "remove"),
  pr2=("El método que vacía un contenedor es replace___(). (8 letras: Children)", "children"),
  ec="quitar el elemento de una variable creyendo que sale de la página"),
K("addEventListener",
  d="método que ejecuta una función cuando ocurre un evento",
  u="reaccionar a lo que hace la persona en la página",
  mas="elemento.addEventListener(\"click\", funcion) registra la función como respuesta al evento. La función recibe un objeto evento con información. Puedes añadir varios oyentes al mismo evento. No escribas la llamada con paréntesis: pasas la función, no su resultado.",
  k=["addEventListener asocia una función a un evento.", "Se le pasa la función sin paréntesis.", "La función recibe un objeto con información del evento."],
  sit="Quieres ejecutar una función cuando se pulse un botón. ¿Qué método usas?",
  cod="""document.body.innerHTML = '<button id="b">Pulsa</button>';
const boton = document.querySelector("#b");
let veces = 0;
boton.addEventListener("click", () => {       // se pasa la función, sin ejecutarla
  veces++;
  console.log("Pulsado", veces);
});
boton.click();          // simulamos dos pulsaciones
boton.click();""",
  h="cuenta cuántas veces se pulsa un botón",
  pr=("El método que asocia una función a un evento es ___EventListener. (3 letras: add)", "add"),
  pr2=("Al registrar el oyente, la función se pasa sin ___. (paréntesis)", "paréntesis", "parentesis"),
  ec="escribir boton.addEventListener(\"click\", funcion()) y ejecutarla al instante"),
K("Eventos de teclado y entrada",
  d="eventos que avisan al pulsar teclas o escribir en un campo",
  u="reaccionar mientras la persona escribe",
  mas="El evento input se dispara cada vez que cambia el contenido de un campo; change, al salir de él. keydown y keyup avisan al pulsar y soltar teclas, y event.key dice cuál. En un campo, event.target.value da el texto actual.",
  k=["El evento input se dispara cada vez que cambia el texto.", "event.key indica qué tecla se pulsó.", "event.target.value contiene el texto del campo."],
  sit="Quieres mostrar cuántos caracteres lleva escritos una persona mientras escribe. ¿Qué evento usas?",
  cod="""document.body.innerHTML = '<input id="campo"><p id="cuenta"></p>';
const campo = document.querySelector("#campo");
campo.addEventListener("input", (evento) => {
  document.querySelector("#cuenta").textContent = evento.target.value.length;
});
campo.value = "Hola";
campo.dispatchEvent(new Event("input"));    // simulamos escribir
console.log(document.querySelector("#cuenta").textContent);   // 4""",
  h="muestra cuántos caracteres hay en un campo cada vez que cambia",
  pr=("El evento que se dispara cada vez que cambia un campo es ___. (5 letras)", "input"),
  pr2=("La propiedad con el texto actual de un campo es event.target.___. (5 letras)", "value"),
  ec="leer el valor del campo antes de que ocurra el evento"),
K("Formularios y preventDefault",
  d="forma de controlar el envío de un formulario con JavaScript",
  u="validar datos y evitar que la página se recargue",
  mas="El evento submit se dispara al enviar el formulario. Por defecto recarga la página; evento.preventDefault() cancela ese comportamiento para que lo gestiones tú. Después lees los campos con evento.target.elements o con FormData.",
  k=["El evento submit se dispara al enviar un formulario.", "preventDefault cancela el comportamiento por defecto.", "FormData permite leer todos los campos del formulario."],
  sit="Quieres validar un formulario con JavaScript sin que la página se recargue al enviarlo. ¿Qué usas?",
  cod="""document.body.innerHTML = '<form id="f"><input name="nombre" value="Ana"><button>Enviar</button></form>';
const form = document.querySelector("#f");
form.addEventListener("submit", (evento) => {
  evento.preventDefault();                        // evita recargar la página
  const datos = new FormData(form);
  console.log("Nombre:", datos.get("nombre"));
});
form.dispatchEvent(new Event("submit", { cancelable: true }));""",
  h="evita la recarga al enviar un formulario y lee el nombre escrito",
  pr=("El método que cancela el comportamiento por defecto es ___(). (14 letras)", "preventdefault"),
  pr2=("El evento que ocurre al enviar un formulario es ___. (6 letras)", "submit"),
  ec="olvidar preventDefault y ver cómo se recarga la página"),
K("Delegación de eventos",
  d="técnica de escuchar un evento en el padre para todos sus hijos",
  u="manejar muchos elementos, incluso los creados después, con un solo oyente",
  mas="En lugar de añadir un oyente a cada botón de una lista, lo añades al contenedor. El evento «burbujea» desde el hijo hacia el padre, y event.target indica en cuál se hizo clic. Funciona también con elementos añadidos más tarde.",
  k=["La delegación usa un solo oyente en el elemento padre.", "event.target indica el elemento que originó el evento.", "Funciona también con elementos añadidos después."],
  sit="Tienes una lista con muchos botones, algunos creados después, y quieres un solo oyente. ¿Qué técnica usas?",
  cod="""document.body.innerHTML = '<ul id="l"><li>Uno</li><li>Dos</li></ul>';
const lista = document.querySelector("#l");
lista.addEventListener("click", (evento) => {       // un solo oyente en el padre
  if (evento.target.tagName === "LI") console.log("Pulsaste:", evento.target.textContent);
});
const nuevo = document.createElement("li");         // elemento creado después
nuevo.textContent = "Tres";
lista.append(nuevo);
nuevo.click();                                      // también funciona""",
  h="usa un único oyente en la lista, incluso para un elemento añadido después",
  pr=("En la delegación, el oyente se coloca en el elemento ___. (5 letras: padre)", "padre", "contenedor"),
  pr2=("La propiedad que indica el elemento que originó el evento es event.___. (6 letras)", "target"),
  ec="añadir un oyente a cada elemento de una lista enorme"),
K("localStorage",
  d="almacenamiento del navegador que guarda datos de forma permanente",
  u="recordar preferencias y datos entre visitas",
  mas="localStorage.setItem(\"clave\", \"valor\") guarda un texto y getItem lo recupera, incluso tras cerrar el navegador. Solo guarda textos: para objetos usa JSON.stringify y JSON.parse. No es seguro para datos sensibles, porque cualquier script de la página puede leerlos.",
  k=["localStorage guarda datos aunque se cierre el navegador.", "Solo almacena textos.", "No debe usarse para datos sensibles."],
  sit="Quieres recordar el tema elegido por una persona la próxima vez que visite la página. ¿Qué usas?",
  cod="""// En el navegador los datos sobreviven al cerrar la pestaña
const memoria = typeof localStorage !== "undefined" ? localStorage : new Map();
const guardar = (k, v) => (memoria.setItem ? memoria.setItem(k, v) : memoria.set(k, v));
const leer = (k) => (memoria.getItem ? memoria.getItem(k) : memoria.get(k));
guardar("tema", JSON.stringify({ oscuro: true }));        // objeto -> texto
console.log(JSON.parse(leer("tema")).oscuro);             // texto -> objeto""",
  h="guarda y recupera un objeto como texto JSON en el almacenamiento",
  pr=("El método que guarda un dato en localStorage es ___Item. (3 letras: set)", "set"),
  pr2=("localStorage solo guarda ___. (6 letras: textos)", "textos", "strings", "cadenas"),
  ec="guardar objetos directamente sin convertirlos con JSON"),
K("setTimeout y setInterval",
  d="funciones que ejecutan código tras una espera o repetidamente",
  u="retrasar acciones o repetirlas cada cierto tiempo",
  mas="setTimeout(funcion, 1000) ejecuta la función una vez tras 1000 milisegundos. setInterval la repite cada cierto tiempo hasta que la detengas con clearInterval. Ambas devuelven un identificador que se pasa a clearTimeout o clearInterval.",
  k=["setTimeout ejecuta una función una vez tras una espera.", "setInterval la repite cada cierto tiempo.", "clearInterval detiene un setInterval."],
  sit="Quieres mostrar un mensaje a los dos segundos de abrir la página. ¿Qué función usas?",
  cod="""setTimeout(() => console.log("Pasó 1 segundo"), 1000);   // una vez
let n = 0;
const id = setInterval(() => {
  n++;
  console.log("Tic", n);
  if (n === 3) clearInterval(id);                        // se detiene a los 3 tics
}, 300);""",
  h="muestra un mensaje tras una espera y repite tres tics antes de detenerse",
  pr=("La función que ejecuta algo una vez tras una espera es ___. (10 letras)", "settimeout"),
  pr2=("La función que detiene un setInterval es ___. (13 letras)", "clearinterval"),
  ec="olvidar clearInterval y dejar el temporizador funcionando siempre"),
K("Promesas",
  d="objeto que representa un resultado que llegará en el futuro",
  u="manejar tareas lentas sin bloquear el programa",
  mas="Una promesa puede estar pendiente, cumplida (resolve) o rechazada (reject). Con .then() se actúa cuando se cumple, con .catch() cuando falla y con .finally() siempre. Permite encadenar pasos y evita el «callback hell».",
  k=["Una promesa representa un resultado futuro.", ".then() se ejecuta cuando la promesa se cumple.", ".catch() se ejecuta cuando la promesa falla."],
  sit="Una tarea tarda en terminar y quieres actuar cuando acabe, sin detener el resto del programa. ¿Qué usas?",
  cod="""const esperar = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
esperar(300)
  .then(() => console.log("Cumplida"))
  .catch(() => console.log("Falló"))
  .finally(() => console.log("Fin (siempre)"));
console.log("Esto aparece primero");""",
  h="crea una promesa que se cumple tras una espera y muestra los pasos",
  pr=("El método que actúa cuando una promesa se cumple es ___(). (4 letras)", "then"),
  pr2=("El método que actúa cuando una promesa falla es ___(). (5 letras)", "catch"),
  ec="olvidar el catch y dejar los errores sin manejar"),
K("async y await",
  d="sintaxis para escribir código asíncrono como si fuera secuencial",
  u="esperar el resultado de una promesa de forma clara",
  mas="Una función async siempre devuelve una promesa. Dentro, await pausa la función hasta que la promesa se cumple y entrega su valor. Hace que el código se lea de arriba abajo, sin cadenas de then. Solo se puede usar await dentro de una función async (o en módulos).",
  k=["Una función async devuelve siempre una promesa.", "await espera a que una promesa se cumpla.", "await solo se usa dentro de funciones async."],
  sit="Quieres esperar el resultado de una promesa escribiendo el código en orden, sin encadenar then. ¿Qué usas?",
  cod="""const esperar = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function principal() {
  console.log("Empiezo");
  await esperar(300);                   // pausa hasta que se cumpla
  console.log("Pasaron 300 ms");
  return "Terminé";
}
principal().then(console.log);""",
  h="espera una promesa dentro de una función async y muestra los pasos en orden",
  pr=("La palabra que espera a una promesa es ___. (5 letras)", "await"),
  pr2=("Una función que usa await debe declararse ___. (5 letras)", "async"),
  ec="usar await fuera de una función async",
  err=("function cargar() {\n  const dato = await obtener();\n  return dato;\n}", 2, "await solo puede usarse dentro de una función declarada con async.")),
K("fetch",
  d="función que pide datos a un servidor por internet",
  u="obtener información de una API",
  mas="fetch(url) devuelve una promesa con la respuesta. Hay que convertirla con respuesta.json() (otra promesa) para leer el contenido. Comprueba respuesta.ok antes de usar los datos, porque fetch no falla ante un error 404 o 500, solo ante problemas de red.",
  k=["fetch pide datos a una dirección y devuelve una promesa.", "respuesta.json() convierte el cuerpo de la respuesta.", "fetch no rechaza la promesa con un error 404 o 500."],
  sit="Quieres descargar datos de una API para mostrarlos en tu página. ¿Qué función usas?",
  cod="""// Ejemplo ilustrativo: aquí simulamos la respuesta de una API
const fetchFalso = () => Promise.resolve({ ok: true, json: async () => ({ nombre: "Ana", edad: 20 }) });
async function cargar() {
  const respuesta = await fetchFalso("https://api.ejemplo.com/usuario");
  if (!respuesta.ok) throw new Error("Respuesta incorrecta");   // fetch real no falla con 404
  const datos = await respuesta.json();
  console.log(datos.nombre, datos.edad);
}
cargar();""",
  h="simula una petición a una API, comprueba la respuesta y lee sus datos",
  pr=("La función que pide datos por internet es ___(). (5 letras)", "fetch"),
  pr2=("La propiedad que indica si la respuesta fue correcta es respuesta.___. (2 letras)", "ok"),
  ec="usar los datos sin comprobar respuesta.ok"),
K("try, catch y finally",
  d="estructura para capturar errores y seguir ejecutando el programa",
  u="evitar que un error detenga todo el programa",
  mas="El código que puede fallar va en try. Si ocurre un error, se salta a catch(error), donde puedes avisar y recuperarte. finally se ejecuta siempre, haya error o no. throw lanza un error propio. Con async/await, los errores de las promesas también se capturan con try/catch.",
  k=["try contiene el código que puede fallar.", "catch recibe el error y permite manejarlo.", "finally se ejecuta siempre."],
  sit="Quieres que el programa siga funcionando aunque una conversión de datos falle. ¿Qué estructura usas?",
  cod="""function leerJSON(texto) {
  try {
    return JSON.parse(texto);               // puede fallar
  } catch (error) {
    console.log("Error:", error.name);      // SyntaxError
    return null;                            // nos recuperamos
  } finally {
    console.log("Intento terminado");       // se ejecuta siempre
  }
}
console.log(leerJSON('{"a": 1}'));
console.log(leerJSON("esto no es JSON"));""",
  h="captura un error de lectura de JSON y sigue funcionando",
  pr=("El bloque que se ejecuta siempre, haya error o no, es ___. (7 letras)", "finally"),
  pr2=("El bloque que recibe el error se llama ___. (5 letras)", "catch"),
  ec="dejar un catch vacío y esconder los errores"),
K("Módulos import y export",
  d="forma de dividir el código en archivos que comparten partes",
  u="organizar proyectos grandes y evitar nombres repetidos",
  mas="Cada archivo puede exportar funciones o valores con export, y otros los importan con import { sumar } from \"./matematicas.js\". En HTML se carga el archivo con <script type=\"module\">. Cada módulo tiene su propio ámbito, así que no hay choques de nombres.",
  k=["export permite compartir algo desde un archivo.", "import trae lo exportado por otro archivo.", "Cada módulo tiene su propio ámbito."],
  sit="Quieres dividir tu código en varios archivos que se compartan funciones entre sí. ¿Qué usas?",
  cod="""// matematicas.js
//   export function sumar(a, b) { return a + b; }
//   export const PI = 3.1416;
// app.js
//   import { sumar, PI } from "./matematicas.js";
// index.html
//   <script type="module" src="app.js"></script>
const sumar = (a, b) => a + b;     // aquí lo escribimos directamente
console.log(sumar(2, 3));""",
  h="muestra cómo exportar e importar funciones entre archivos",
  pr=("La palabra que comparte algo desde un archivo es ___. (6 letras)", "export"),
  pr2=("La palabra que trae lo compartido por otro archivo es ___. (6 letras)", "import"),
  ec="olvidar type=\"module\" al cargar el script"),
K("Clases",
  d="plantillas para crear objetos con los mismos datos y métodos",
  u="crear muchos objetos parecidos de forma ordenada",
  mas="class Persona { constructor(nombre) { this.nombre = nombre; } saludar() { ... } } define la plantilla. new Persona(\"Ana\") crea un objeto (instancia). El constructor inicializa los datos y los métodos se comparten. extends permite heredar de otra clase.",
  k=["Una clase es una plantilla para crear objetos.", "El constructor inicializa los datos del objeto.", "new crea una instancia de la clase."],
  sit="Quieres crear muchos objetos persona con los mismos datos y métodos a partir de una plantilla. ¿Qué usas?",
  cod="""class Persona {
  constructor(nombre, edad) {       // se ejecuta al crear el objeto
    this.nombre = nombre;
    this.edad = edad;
  }
  saludar() {
    return `Hola, soy ${this.nombre} y tengo ${this.edad}`;
  }
}
const ana = new Persona("Ana", 20);
const luis = new Persona("Luis", 25);
console.log(ana.saludar());
console.log(luis.saludar());""",
  h="define una plantilla Persona y crea dos objetos a partir de ella",
  pr=("La palabra que crea una instancia de una clase es ___. (3 letras)", "new"),
  pr2=("El método especial que inicializa el objeto es el ___. (11 letras)", "constructor"),
  ec="olvidar new al crear el objeto",
  err=("class Persona {\n  constructor(nombre) { this.nombre = nombre; }\n}\nconst ana = Persona(\"Ana\");", 4, "Falta new: se debe crear con new Persona(\"Ana\").")),
K("Burbujeo de eventos",
  d="comportamiento por el que un evento sube del hijo a sus padres",
  u="entender por qué se disparan oyentes de elementos contenedores",
  mas="Cuando haces clic en un botón dentro de un div, el evento se dispara primero en el botón y luego «burbujea» hacia el div y hacia arriba hasta el documento. evento.stopPropagation() detiene ese ascenso. Es la base de la delegación de eventos.",
  k=["Un evento sube desde el elemento hasta sus padres.", "stopPropagation detiene el ascenso del evento.", "El burbujeo hace posible la delegación de eventos."],
  sit="Un clic en un botón también activa el oyente del contenedor que lo rodea. ¿Qué comportamiento lo explica?",
  cod="""document.body.innerHTML = '<div id="padre"><button id="hijo">Clic</button></div>';
document.querySelector("#padre").addEventListener("click", () => console.log("Oyente del padre"));
document.querySelector("#hijo").addEventListener("click", () => console.log("Oyente del hijo"));
document.querySelector("#hijo").click();      // se escribe primero el hijo y luego el padre""",
  h="muestra que un clic en el hijo también llega al padre",
  pr=("El comportamiento por el que un evento sube a los padres se llama ___. (9 letras: burbujeo)", "burbujeo", "bubbling"),
  pr2=("El método que detiene el ascenso del evento es stop___(). (11 letras: Propagation)", "propagation"),
  ec="detener la propagación sin necesidad y romper otros oyentes"),
K("Proyecto: lista de tareas",
  d="aplicación web que reúne DOM, eventos y almacenamiento",
  u="practicar todo lo aprendido en una aplicación real",
  mas="Para cerrar JavaScript, crea una lista de tareas: un formulario para añadir tareas, una lista que se pinta con createElement, botones para marcarlas o borrarlas con delegación de eventos, y localStorage para guardarlas. Divide el código en funciones pequeñas.",
  k=["Una lista de tareas combina DOM, eventos y almacenamiento.", "La delegación de eventos permite gestionar los botones de cada tarea.", "localStorage permite conservar las tareas entre visitas."],
  sit="Quieres cerrar el curso con una aplicación que permita añadir, completar y borrar tareas. ¿Qué construyes?",
  cod="""document.body.innerHTML = '<form id="f"><input id="t" value="Estudiar"><button>Añadir</button></form><ul id="lista"></ul>';
const tareas = [];
const lista = document.querySelector("#lista");
function pintar() {
  lista.replaceChildren();
  tareas.forEach((tarea, i) => {
    const li = document.createElement("li");
    li.textContent = tarea;
    li.dataset.indice = i;
    lista.append(li);
  });
}
document.querySelector("#f").addEventListener("submit", (e) => {
  e.preventDefault();
  tareas.push(document.querySelector("#t").value);
  pintar();
});
document.querySelector("#f").dispatchEvent(new Event("submit", { cancelable: true }));
console.log(lista.children.length, tareas);""",
  h="añade una tarea desde un formulario y la pinta en una lista",
  pr=("Para cerrar el curso conviene hacer un ___ completo. (8 letras)", "proyecto"),
  pr2=("Para que las tareas se conserven al recargar se usa ___. (12 letras)", "localstorage"),
  ec="intentar escribir todo el programa de una sola vez sin dividirlo en funciones"),
]
