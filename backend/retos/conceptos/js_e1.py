"""JavaScript · Etapa 1: qué es JavaScript (casi todo teoría)."""
from ..generador import K

LISTA = [
K("Qué es JavaScript",
  d="lenguaje de programación que da vida a las páginas web",
  u="añadir comportamiento e interacción a una página",
  mas="HTML pone la estructura y CSS el estilo; JavaScript hace que la página reaccione: abrir menús, validar formularios, mostrar mensajes o actualizar datos sin recargar. Es el único lenguaje que todos los navegadores entienden de forma nativa.",
  k=["JavaScript añade comportamiento a las páginas web.", "Todos los navegadores entienden JavaScript.", "JavaScript es un lenguaje de programación, a diferencia de HTML."],
  sit="Quieres que un botón de tu página muestre un mensaje al pulsarlo. ¿Qué lenguaje usas?",
  cod="""// JavaScript puede ejecutar acciones
console.log("¡Hola desde JavaScript!");
console.log(2 + 3);""",
  h="muestra un saludo y una suma en la consola",
  pr=("El lenguaje que da comportamiento a las páginas web es ___. (10 letras)", "javascript"),
  pr2=("HTML da la estructura, CSS el estilo y JavaScript el ___. (14 letras: comportamiento)", "comportamiento"),
  ec="creer que JavaScript solo sirve para validar formularios"),
K("Para qué sirve JavaScript",
  d="lista de usos reales del lenguaje en la web y fuera de ella",
  u="saber qué se puede construir aprendiendo JavaScript",
  mas="Con JavaScript se hacen páginas interactivas, aplicaciones web como Gmail, juegos en el navegador, servidores con Node.js, aplicaciones móviles y de escritorio, e incluso robots. Es uno de los lenguajes más usados del mundo.",
  k=["JavaScript se usa en el navegador y también en servidores.", "Con JavaScript se pueden crear juegos y aplicaciones.", "Es uno de los lenguajes más usados del mundo."],
  sit="Te preguntas si lo que aprendas con este lenguaje te permitirá hacer apps, juegos y servidores. ¿Qué analizas?",
  cod="""// Ejemplos de lo que se puede construir
const usos = ["páginas interactivas", "juegos", "servidores", "apps móviles"];
console.log("Con JavaScript puedes hacer:");
for (const uso of usos) console.log("- " + uso);""",
  h="lista cuatro cosas que se pueden construir con el lenguaje",
  pr=("Con JavaScript se pueden crear páginas, juegos y ___ web. (una palabra: aplicaciones)", "aplicaciones", "apps"),
  pr2=("El entorno que permite crear servidores con JavaScript se llama ___. (7 letras con punto)", "node.js", "nodejs", "node"),
  ec="pensar que JavaScript solo sirve para animaciones"),
K("JavaScript y Java",
  d="dos lenguajes distintos con nombres parecidos",
  u="evitar confusiones al buscar información",
  mas="No tienen relación. JavaScript se llamó así por una estrategia de marketing en los años 90, cuando Java era muy popular. Se diferencian en cómo se escriben, dónde se ejecutan y para qué se usan. Si buscas ayuda, escribe siempre «JavaScript» completo.",
  k=["JavaScript y Java son lenguajes distintos.", "El nombre parecido fue una decisión de marketing.", "Al buscar ayuda hay que escribir JavaScript completo."],
  sit="Alguien te dice que JavaScript es una versión simplificada de Java. ¿Qué confusión es esa?",
  cod="""// JavaScript (este lenguaje)
console.log("Soy JavaScript");
// Java es otro lenguaje con otra sintaxis:
// System.out.println("Soy Java");""",
  h="muestra un mensaje en JavaScript y deja comentada la forma de hacerlo en Java",
  pr=("JavaScript y ___ son lenguajes distintos. (4 letras)", "java"),
  pr2=("El nombre parecido de ambos fue una decisión de ___. (9 letras)", "marketing", "mercadotecnia"),
  ec="creer que aprender Java es lo mismo que aprender JavaScript"),
K("ECMAScript",
  d="estándar que define cómo debe funcionar JavaScript",
  u="garantizar que el lenguaje funcione igual en todos los navegadores",
  mas="ECMAScript (ES) es la especificación oficial y JavaScript es su implementación más conocida. Cada año sale una versión: ES6 (2015) trajo let, const y las funciones flecha, y por eso se habla de «JavaScript moderno». Los navegadores adoptan las novedades poco a poco.",
  k=["ECMAScript es el estándar que define JavaScript.", "ES6 (2015) introdujo let, const y las funciones flecha.", "Cada año aparece una nueva versión del estándar."],
  sit="Quieres nombrar al estándar oficial que define las reglas de JavaScript. ¿Cuál es?",
  cod="""// Novedades de ES6 (2015) que usaremos siempre
const saludo = "Hola";                  // const y let vienen de ES6
const doble = (n) => n * 2;             // función flecha, también de ES6
console.log(saludo, doble(21));""",
  h="usa dos novedades de ES6: const y una función flecha",
  pr=("El estándar que define JavaScript se llama ___Script. (3 letras)", "ecma"),
  pr2=("La versión de 2015 que modernizó el lenguaje es ES___. (un número)", "6"),
  ec="creer que ES6 y JavaScript son lenguajes distintos"),
K("Navegador y consola",
  d="entorno donde se ejecuta JavaScript y se ven sus mensajes",
  u="probar código y ver errores mientras programas",
  mas="Todos los navegadores traen un motor de JavaScript (V8 en Chrome, SpiderMonkey en Firefox). Con F12 abres las herramientas de desarrollo y, en la pestaña Consola, puedes escribir código al instante y ver los mensajes de console.log y los errores.",
  k=["El navegador incluye un motor que ejecuta JavaScript.", "La consola se abre con F12.", "En la consola se ven los mensajes y los errores del código."],
  sit="Quieres escribir una línea de JavaScript y ver su resultado al instante en el navegador. ¿Dónde lo haces?",
  cod="""// Pega esto en la consola del navegador (F12)
console.log("Esto aparece en la consola");
console.error("Así se ve un mensaje de error");
console.warn("Y así una advertencia");""",
  h="muestra un mensaje normal, un error y una advertencia en la consola",
  pr=("La consola se abre con la tecla ___. (3 caracteres)", "f12"),
  pr2=("El motor de JavaScript de Chrome se llama ___. (2 caracteres)", "v8"),
  ec="programar sin mirar nunca los errores de la consola"),
K("Node.js",
  d="entorno que ejecuta JavaScript fuera del navegador",
  u="crear servidores, herramientas y scripts con JavaScript",
  mas="Node.js usa el mismo motor V8 de Chrome pero sin página web: sirve para programas en la terminal, servidores y herramientas. Con él, un mismo lenguaje sirve para el cliente y el servidor. Incluye npm, el mayor repositorio de librerías.",
  k=["Node.js ejecuta JavaScript fuera del navegador.", "Node.js incluye npm para instalar librerías.", "Con Node.js se pueden crear servidores."],
  sit="Quieres ejecutar JavaScript en tu computadora sin abrir ningún navegador. ¿Qué usas?",
  cod="""// Guarda esto como hola.js y ejecútalo en la terminal con: node hola.js
console.log("Hola desde Node.js");
console.log("Versión de JavaScript lista:", typeof console);""",
  h="muestra mensajes ejecutados por Node.js sin navegador",
  pr=("El entorno que ejecuta JavaScript fuera del navegador es ___.js. (4 letras)", "node"),
  pr2=("El gestor de paquetes de Node.js se llama ___. (3 letras)", "npm"),
  ec="creer que JavaScript solo funciona dentro de un navegador"),
K("Script en HTML",
  d="etiqueta script que incluye código JavaScript en una página",
  u="ejecutar JavaScript cuando se abre la página",
  mas="El código se escribe entre <script> y </script>. Suele ir al final del body para que el HTML ya exista cuando se ejecute. El navegador lee la página de arriba abajo y ejecuta cada script al encontrarlo.",
  k=["La etiqueta script incluye código JavaScript en una página.", "Suele colocarse al final del body.", "El navegador ejecuta el script al encontrarlo."],
  sit="Quieres escribir código JavaScript dentro de tu archivo HTML. ¿Qué etiqueta usas?",
  cod="""<h1 id="titulo">Hola</h1>
<script>
  // este código se ejecuta al abrir la página
  document.getElementById("titulo").textContent = "Cambiado con JavaScript";
</script>""",
  h="cambia el texto del título desde un script dentro del HTML",
  pr=("El código JavaScript en HTML se escribe dentro de la etiqueta ___. (6 letras)", "script", "<script>"),
  pr2=("Un script suele colocarse al ___ del body. (5 letras)", "final"),
  ec="poner el script antes del HTML que necesita y recibir errores"),
K("Archivo .js externo",
  d="archivo aparte que contiene solo código JavaScript",
  u="separar el código de la página y reutilizarlo",
  mas="Se guarda con extensión .js y se enlaza con <script src=\"app.js\"></script>. Mantiene el HTML limpio, permite usar el mismo código en varias páginas y el navegador lo guarda en caché. Es la forma recomendada de organizar el código.",
  k=["Un archivo externo de JavaScript termina en .js.", "Se enlaza con script y el atributo src.", "Es la forma recomendada de organizar el código."],
  sit="Quieres usar el mismo código JavaScript en cinco páginas distintas. ¿Qué haces?",
  cod="""<!-- index.html -->
<script src="js/app.js" defer></script>

// js/app.js contendría:
// console.log("Archivo externo cargado");""",
  h="enlaza un archivo JavaScript externo desde el HTML",
  pr=("Un archivo de JavaScript termina en ___. (3 caracteres con punto)", ".js", "js"),
  pr2=("El atributo de script con la ruta del archivo es ___. (3 letras)", "src"),
  ec="olvidar la ruta correcta del archivo .js"),
K("Instrucciones y punto y coma",
  d="cada orden del programa, que suele terminar con punto y coma",
  u="separar las órdenes que el programa ejecuta en secuencia",
  mas="Un programa es una lista de instrucciones que se ejecutan de arriba abajo, una tras otra. Conviene terminar cada una con punto y coma. JavaScript puede insertarlo por ti, pero depender de eso causa errores sutiles.",
  k=["Las instrucciones se ejecutan en orden, de arriba abajo.", "Conviene terminar cada instrucción con punto y coma.", "El orden de las instrucciones cambia el resultado."],
  sit="Quieres que dos órdenes se ejecuten una tras otra, separadas con el símbolo adecuado. ¿Qué usas?",
  cod="""console.log("Primero");
console.log("Segundo");
console.log("Tercero");
// El orden importa: se ejecutan de arriba abajo""",
  h="ejecuta tres instrucciones en orden, una tras otra",
  pr=("Cada instrucción termina convenientemente con ___. (punto y coma)", ";", "punto y coma"),
  pr2=("Las instrucciones se ejecutan de arriba hacia ___. (5 letras)", "abajo"),
  ec="escribir dos instrucciones en la misma línea sin separarlas"),
K("Comentarios en JavaScript",
  d="notas en el código que el programa ignora",
  u="explicar el código y desactivar líneas",
  mas="Un comentario de una línea empieza con //. Uno de varias líneas va entre /* y */. Sirven para explicar el porqué de un código, no para repetir lo evidente. También se usan para desactivar líneas mientras pruebas.",
  k=["Los comentarios de una línea empiezan con //.", "Los comentarios de varias líneas van entre /* y */.", "El programa ignora los comentarios."],
  sit="Quieres dejar una nota en el código que el programa no ejecute. ¿Qué escribes?",
  cod="""// Esto es un comentario de una línea
console.log("Esto sí se ejecuta");
/* Un comentario
   de varias líneas */
// console.log("Esta línea está desactivada");""",
  h="ejecuta solo una línea y deja el resto comentado o desactivado",
  pr=("Un comentario de una línea empieza con ___. (2 caracteres)", "//"),
  pr2=("Un comentario de varias líneas empieza con ___. (2 caracteres)", "/*"),
  ec="comentar lo obvio en lugar de explicar el porqué"),
K("console.log",
  d="instrucción que muestra información en la consola",
  u="ver valores y comprobar qué hace el programa",
  mas="console.log(valor) escribe en la consola lo que le pases: textos, números, resultados de operaciones. Puedes pasarle varios valores separados por comas. Es tu mejor herramienta para depurar: «imprime» el valor para ver qué contiene.",
  k=["console.log muestra valores en la consola.", "Acepta varios valores separados por comas.", "Es la herramienta más usada para depurar."],
  sit="Quieres ver en la consola el resultado de una operación para comprobar tu código. ¿Qué usas?",
  cod="""console.log("Hola");                 // un texto
console.log(7 * 6);                  // el resultado de una operación
console.log("Resultado:", 7 * 6);    // varios valores a la vez""",
  h="muestra un texto, un cálculo y ambos juntos",
  pr=("La instrucción que muestra algo en la consola es console.___. (3 letras)", "log"),
  pr2=("Los valores de console.log se separan con ___. (una coma)", ",", "coma", "comas"),
  ec="olvidar los paréntesis de console.log",
  err=("console.log(\"Hola\");\nconsole.log \"Adiós\";", 2, "Falta el paréntesis: console.log(\"Adiós\");")),
K("Alert y prompt",
  d="ventanas del navegador para avisar o pedir un dato",
  u="interactuar con la persona de forma muy sencilla",
  mas="alert(\"texto\") muestra un aviso con un botón. prompt(\"pregunta\") abre una ventana para escribir y devuelve lo escrito. Son útiles para aprender, pero en proyectos reales se prefieren elementos de la propia página, porque estas ventanas bloquean todo.",
  k=["alert muestra una ventana de aviso.", "prompt pide un dato y devuelve el texto escrito.", "Estas ventanas bloquean la página mientras están abiertas."],
  sit="Quieres preguntar el nombre al visitante con una ventana sencilla del navegador. ¿Qué usas?",
  cod="""// Estas funciones solo existen en el navegador
// alert("¡Bienvenida!");
// const nombre = prompt("¿Cómo te llamas?");
// console.log("Hola, " + nombre);
console.log("alert avisa y prompt pregunta");""",
  h="explica cómo avisar y preguntar con ventanas del navegador",
  pr=("La función que muestra un aviso en una ventana es ___. (5 letras)", "alert"),
  pr2=("La función que pide un dato al usuario es ___. (6 letras)", "prompt"),
  ec="usar alert por todas partes en un proyecto real"),
K("Qué es una variable",
  d="espacio con nombre donde se guarda un dato",
  u="recordar valores para usarlos más tarde",
  mas="Imagina una caja con una etiqueta: la etiqueta es el nombre de la variable y lo que hay dentro es su valor. Puedes cambiar el contenido de la caja, y usar su nombre en lugar del valor cada vez que lo necesites. En el siguiente bloque aprenderás a crearlas.",
  k=["Una variable guarda un dato con un nombre.", "El valor de una variable puede cambiar.", "Se usa el nombre de la variable en lugar del valor."],
  sit="Quieres guardar la edad de una persona para usarla en varios sitios del programa. ¿Qué necesitas?",
  cod="""let edad = 20;              // guardamos 20 con el nombre «edad»
console.log(edad);          // usamos el nombre
edad = 21;                  // cambiamos el valor
console.log(edad);""",
  h="guarda una edad, la muestra y la cambia",
  pr=("Una variable guarda un ___ con un nombre. (4 letras)", "dato", "valor"),
  pr2=("El valor de una variable puede ___. (7 letras: cambiar)", "cambiar"),
  ec="escribir el valor en todas partes en lugar de usar una variable"),
K("Qué es un tipo de dato",
  d="clase de valor que puede guardar una variable",
  u="saber qué operaciones se pueden hacer con un dato",
  mas="Los textos (string), los números (number) y los verdaderos o falsos (boolean) son tipos distintos. No se comportan igual: puedes multiplicar números, pero no textos. Saber de qué tipo es un dato evita muchos errores.",
  k=["Los principales tipos son texto, número y booleano.", "Cada tipo permite operaciones distintas.", "Conocer el tipo de un dato evita errores."],
  sit="Quieres distinguir si un dato es un texto, un número o un verdadero/falso. ¿Qué concepto necesitas?",
  cod="""console.log(typeof "Hola");     // string
console.log(typeof 42);         // number
console.log(typeof true);       // boolean""",
  h="muestra el tipo de un texto, un número y un booleano",
  pr=("Los tres tipos básicos son string, number y ___. (7 letras)", "boolean", "booleano"),
  pr2=("El operador que indica el tipo de un dato es ___. (6 letras)", "typeof"),
  ec="intentar multiplicar textos como si fueran números"),
K("Qué es una función",
  d="bloque de código con nombre que se puede ejecutar cuando se quiera",
  u="no repetir código y organizar el programa",
  mas="Una función agrupa varias instrucciones bajo un nombre. La defines una vez y la «llamas» cuantas veces necesites. Puede recibir datos (parámetros) y devolver un resultado. Es como una receta que usas siempre que quieras.",
  k=["Una función agrupa instrucciones bajo un nombre.", "Se define una vez y se llama muchas veces.", "Puede recibir datos y devolver un resultado."],
  sit="Quieres escribir un saludo una vez y usarlo diez veces sin copiar el código. ¿Qué creas?",
  cod="""function saludar() {
  console.log("¡Hola!");
}
saludar();      // primera llamada
saludar();      // segunda llamada""",
  h="define un saludo una vez y lo ejecuta dos veces",
  pr=("Un bloque de código con nombre que se puede ejecutar varias veces es una ___. (7 letras)", "función", "funcion"),
  pr2=("Ejecutar una función se llama ___ a la función. (7 letras: llamar)", "llamar"),
  ec="copiar y pegar el mismo código en lugar de crear una función"),
K("Qué es un evento",
  d="algo que ocurre en la página y a lo que se puede responder",
  u="hacer que la página reaccione a lo que hace la persona",
  mas="Un clic, pulsar una tecla, enviar un formulario, escribir en un campo o cargar la página son eventos. Con JavaScript «escuchas» un evento y ejecutas una función cuando ocurre. Es la base de toda la interactividad.",
  k=["Un clic o una pulsación de tecla son eventos.", "Se escucha un evento y se ejecuta una función al ocurrir.", "Los eventos son la base de la interactividad."],
  sit="Quieres ejecutar un código justo cuando la persona pulsa un botón. ¿Qué escuchas?",
  cod="""// Los eventos solo existen en el navegador; así se escucharía un clic:
// boton.addEventListener("click", () => console.log("¡Clic!"));
console.log("Evento = algo que ocurre, y una función que responde");""",
  h="explica cómo se escucharía un clic para ejecutar una función",
  pr=("Pulsar un botón es un ___ de clic. (6 letras: evento)", "evento"),
  pr2=("El evento que se produce al pulsar es el ___. (4 letras)", "click", "clic"),
  ec="intentar leer el valor de un campo antes de que ocurra el evento"),
K("Qué es el DOM",
  d="representación de la página como árbol de elementos manipulable",
  u="leer y cambiar el contenido de la página con código",
  mas="El navegador convierte tu HTML en un árbol de objetos llamado DOM (Document Object Model). JavaScript puede leer ese árbol, cambiar textos y estilos, añadir o quitar elementos. El objeto document es la puerta de entrada.",
  k=["El DOM es el árbol de elementos de la página.", "JavaScript puede modificar el DOM.", "El objeto document es la entrada al DOM."],
  sit="Quieres cambiar el texto de un título de la página con código. ¿Qué manipulas?",
  cod="""<h1 id="t">Título original</h1>
<script>
  const t = document.getElementById("t");   // el DOM nos da el elemento
  t.textContent = "Título cambiado";        // cambiamos su texto
  console.log(t.textContent);
</script>""",
  h="busca un título en el DOM y le cambia el texto",
  pr=("Las siglas de Document Object Model son ___. (3 letras)", "dom"),
  pr2=("La puerta de entrada al DOM es el objeto ___. (8 letras)", "document"),
  ec="confundir el DOM con el código HTML original"),
K("Interpretado y compilado",
  d="dos formas de convertir el código en algo que la máquina ejecuta",
  u="entender cuándo se detecta cada error",
  mas="Un lenguaje compilado se traduce entero antes de ejecutarse. JavaScript es interpretado (con compilación justo a tiempo): el motor lo traduce mientras corre. Por eso, muchos errores solo aparecen al ejecutar la línea que los contiene.",
  k=["JavaScript se interpreta mientras se ejecuta.", "Los lenguajes compilados se traducen antes de ejecutarse.", "Muchos errores de JavaScript aparecen solo al ejecutar la línea."],
  sit="Notas que un error en tu código solo aparece al ejecutar justo esa línea. ¿Qué característica del lenguaje lo explica?",
  cod="""console.log("Esta línea se ejecuta bien");
// La siguiente tiene un error pero no se detecta hasta llegar a ella:
// console.log(variableInexistente);
console.log("Fin del programa");""",
  h="ejecuta líneas en orden y deja comentada una que fallaría al llegar a ella",
  pr=("JavaScript se ___ mientras se ejecuta. (9 letras: interpreta)", "interpreta"),
  pr2=("Un lenguaje que se traduce entero antes de ejecutarse es ___. (9 letras)", "compilado"),
  ec="creer que el error se detecta antes de ejecutar el programa"),
K("Errores y consola",
  d="mensajes que indican qué falló y en qué línea",
  u="encontrar y corregir fallos del código",
  mas="Un error de sintaxis (falta un paréntesis) impide que el programa arranque. Un error en ejecución (usar una variable que no existe) lo detiene al llegar a esa línea. La consola indica el tipo de error, el mensaje y el número de línea: léelo siempre entero.",
  k=["La consola indica el tipo de error y la línea.", "Los errores de sintaxis impiden que el programa arranque.", "Hay que leer el mensaje de error completo."],
  sit="Tu programa se detiene y ves un mensaje rojo con una línea indicada. ¿Qué debes leer?",
  cod="""try {
  console.log(noExiste);          // esta variable no existe
} catch (error) {
  console.log("Tipo:", error.name);          // ReferenceError
  console.log("Mensaje:", error.message);    // dice qué falló
}""",
  h="captura un error y muestra su tipo y su mensaje",
  pr=("El error por usar una variable que no existe es un ___Error. (9 letras: Reference)", "reference"),
  pr2=("Un error de ___ ocurre cuando falta un paréntesis o una llave. (9 letras)", "sintaxis"),
  ec="ignorar el mensaje de error y cambiar código al azar"),
K("Cómo practicar JavaScript",
  d="costumbre de escribir y probar código a diario",
  u="aprender más rápido y fijar lo estudiado",
  mas="Programar se aprende programando. Escribe cada ejemplo, cambia valores, rompe el código a propósito y arréglalo. Mini-proyectos como una calculadora o una lista de tareas enseñan más que leer teoría. Practica un poco cada día.",
  k=["Programar se aprende escribiendo código.", "Los mini-proyectos enseñan mucho.", "Practicar un poco cada día es mejor que mucho de golpe."],
  sit="Quieres aprender JavaScript de verdad y no solo memorizarlo. ¿Qué haces?",
  cod="""// Reto: cambia los valores y observa el resultado
const nombre = "Ana";
const edad = 20;
console.log("Me llamo " + nombre + " y tengo " + edad + " años");
// Ahora añade una variable «ciudad» y muéstrala""",
  h="une un nombre y una edad en una frase y deja un reto para ampliarla",
  pr=("Programar se aprende ___. (10 letras: programando)", "programando", "practicando", "escribiendo"),
  pr2=("Practicar un poco cada ___ es mejor que mucho de golpe. (3 letras)", "día", "dia"),
  ec="leer teoría sin escribir nunca código"),
]
