"""CSS · Etapa 2: selectores, texto y color."""
from ..generador import K

LISTA = [
K("Selector de clase",
  d="selector con punto que elige elementos con esa clase",
  u="dar el mismo estilo a elementos distintos",
  mas="Se escribe .nombre en CSS y class=\"nombre\" en HTML. Varios elementos pueden compartir clase, y un elemento puede tener varias. Es el selector más usado porque es reutilizable.",
  k=["El selector de clase empieza con un punto.", "Varios elementos pueden compartir la misma clase.", "Un elemento puede tener varias clases a la vez."],
  sit="Quieres dar el mismo fondo amarillo a un párrafo y a un div distintos. ¿Qué selector usas?",
  cod="""<style>
  /* el punto indica que es una clase */
  .aviso { background: #fef08a; padding: 8px; border-radius: 6px; }
</style>
<p class="aviso">Párrafo con aviso</p>
<div class="aviso">Div con aviso</div>
<p>Sin aviso</p>""",
  h="da el mismo fondo amarillo a un párrafo y a un div usando una clase",
  pr=("Una clase se escribe en CSS con un ___ delante. (punto)", ".", "punto"),
  pr2=("En HTML, la clase se asigna con el atributo ___. (5 letras)", "class"),
  ec="olvidar el punto delante del nombre de la clase",
  err=("<style>\n  aviso { background: gold; }\n</style>\n<p class=\"aviso\">Hola</p>", 2, "Falta el punto: para una clase se escribe .aviso, no aviso.")),
K("Selector de id",
  d="selector con almohadilla que elige un elemento único",
  u="dar estilo a un elemento concreto de la página",
  mas="Se escribe #nombre en CSS y id=\"nombre\" en HTML. Como cada id es único, el selector elige un solo elemento. Tiene más peso que una clase, así que conviene usarlo poco.",
  k=["El selector de id empieza con el símbolo #.", "Un id debe aparecer solo una vez en la página.", "El selector de id pesa más que el de clase."],
  sit="Quieres dar estilo solo a la cabecera principal, que existe una única vez. ¿Qué selector usas?",
  cod="""<style>
  /* # indica que es un id: elige un solo elemento */
  #principal { color: white; background: navy; padding: 12px; }
</style>
<h1 id="principal">Título único</h1>
<h1>Otro título normal</h1>""",
  h="pinta solo el título con id principal con fondo azul oscuro",
  pr=("Un id se escribe en CSS con el símbolo ___ delante. (un carácter)", "#"),
  pr2=("Un id debe ser ___ en la página. (una palabra)", "único", "unico"),
  ec="usar el mismo id en varios elementos"),
K("Selector universal",
  d="selector asterisco que elige todos los elementos",
  u="aplicar un estilo base a toda la página",
  mas="El asterisco * elige absolutamente todo. Es habitual en los «resets» para quitar márgenes y rellenos por defecto. Úsalo con cuidado: afecta a todo y puede ser más lento en páginas enormes.",
  k=["El selector universal se escribe con un asterisco.", "El selector universal elige todos los elementos.", "Es habitual usarlo para resetear márgenes."],
  sit="Quieres quitar los márgenes por defecto de todos los elementos a la vez. ¿Qué selector usas?",
  cod="""<style>
  /* * elige TODOS los elementos */
  * { margin: 0; padding: 0; box-sizing: border-box; }
  h1 { background: gold; }
</style>
<h1>Sin márgenes por defecto</h1>
<p>Todo queda pegado al borde</p>""",
  h="quita márgenes y rellenos de todos los elementos con un solo selector",
  pr=("El selector universal se escribe con el símbolo ___. (un carácter)", "*"),
  pr2=("El selector universal elige ___ los elementos. (una palabra)", "todos"),
  ec="usar * para dar colores y afectar a toda la página sin querer"),
K("Agrupar selectores",
  d="varios selectores separados por comas que comparten reglas",
  u="evitar repetir el mismo estilo en varias reglas",
  mas="Si h1, h2 y h3 deben ser del mismo color, escribe h1, h2, h3 { color: navy; }. Las comas significan «y». Olvidar una coma cambia el significado de la regla.",
  k=["Los selectores agrupados se separan con comas.", "Agrupar evita repetir las mismas declaraciones.", "La coma entre selectores significa «y»."],
  sit="Quieres que h1, h2 y h3 compartan el mismo color sin escribir tres reglas. ¿Qué haces?",
  cod="""<style>
  /* las comas agrupan: vale para h1, h2 y h3 */
  h1, h2, h3 { color: darkcyan; font-family: Georgia, serif; }
</style>
<h1>Título</h1><h2>Subtítulo</h2><h3>Apartado</h3>""",
  h="da la misma fuente y color a tres niveles de título con una sola regla",
  pr=("Los selectores agrupados se separan con ___. (una coma)", ",", "coma", "comas"),
  pr2=("Agrupar sirve para no ___ las declaraciones. (una palabra)", "repetir"),
  ec="olvidar la coma entre selectores agrupados"),
K("Selector descendiente",
  d="selector con espacio que elige elementos dentro de otros",
  u="dar estilo solo a los elementos que están dentro de un contenedor",
  mas="Se escribe con un espacio entre selectores: nav a elige los enlaces que están dentro de un nav, a cualquier nivel. Así puedes dar estilo distinto a los enlaces del menú y a los del texto.",
  k=["El selector descendiente se escribe con un espacio.", "Elige elementos dentro de otro, a cualquier profundidad.", "Permite estilos distintos según el contenedor."],
  sit="Quieres colorear solo los enlaces que están dentro del menú nav. ¿Qué selector usas?",
  cod="""<style>
  /* el espacio: enlaces DENTRO de nav */
  nav a { color: crimson; font-weight: bold; }
</style>
<nav><a href="#">Inicio</a> <a href="#">Cursos</a></nav>
<p>Un <a href="#">enlace del texto</a> no cambia</p>""",
  h="pinta de rojo solo los enlaces del menú, no los del texto",
  pr=("En «nav a», el selector elige los enlaces ___ de nav. (una palabra)", "dentro"),
  pr2=("El selector descendiente separa sus partes con un ___. (una palabra)", "espacio"),
  ec="poner coma en lugar de espacio y cambiar el significado"),
K("Selector hijo directo",
  d="selector con > que elige solo los hijos inmediatos",
  u="ser más preciso que con el selector descendiente",
  mas="ul > li elige solo los li que son hijos directos de ul, no los que están dentro de sublistas. El símbolo > evita que el estilo se filtre a niveles más profundos.",
  k=["El selector hijo usa el símbolo >.", "Elige solo hijos inmediatos del elemento.", "No afecta a los nietos ni a niveles más profundos."],
  sit="Quieres estilar solo los li del primer nivel de una lista, no los de sublistas. ¿Qué selector usas?",
  cod="""<style>
  /* > : solo hijos directos */
  ul > li { color: darkred; }
</style>
<ul>
  <li>Nivel 1
    <ul><li>Nivel 2 (no cambia)</li></ul>
  </li>
</ul>""",
  h="pinta solo los elementos del primer nivel de la lista",
  pr=("El símbolo del selector de hijo directo es ___. (un carácter)", ">"),
  pr2=("El selector hijo no afecta a los ___ del elemento. (una palabra: hijos de los hijos)", "nietos"),
  ec="usar > esperando que llegue a todos los niveles"),
K("Selector de hermano",
  d="selector con + que elige el elemento que sigue justo después",
  u="estilar el elemento que va inmediatamente tras otro",
  mas="h2 + p elige el párrafo que va justo después de un h2 y que comparte padre con él. Es útil para destacar el primer párrafo tras un título. Existe también ~, que elige todos los hermanos siguientes.",
  k=["El selector + elige el hermano inmediato siguiente.", "Los dos elementos deben compartir el mismo padre.", "El selector ~ elige todos los hermanos siguientes."],
  sit="Quieres destacar solo el párrafo que va justo después de cada título h2. ¿Qué selector usas?",
  cod="""<style>
  /* + : el p que viene justo después de un h2 */
  h2 + p { font-size: 20px; font-style: italic; }
</style>
<h2>Título</h2>
<p>Este párrafo se destaca</p>
<p>Este no</p>""",
  h="destaca solo el primer párrafo que sigue a un título",
  pr=("El símbolo del selector de hermano adyacente es ___. (un carácter)", "+"),
  pr2=("Para elegir todos los hermanos siguientes se usa el símbolo ___. (un carácter)", "~"),
  ec="esperar que + afecte a todos los párrafos siguientes"),
K("Selectores de atributo",
  d="selectores entre corchetes que eligen según un atributo",
  u="estilar elementos por su atributo sin añadir clases",
  mas="a[target=\"_blank\"] elige los enlaces con ese atributo. input[type=\"email\"] elige solo los campos de correo. También puedes usar [href^=\"https\"] (empieza por) o [href$=\".pdf\"] (termina en).",
  k=["Los selectores de atributo se escriben entre corchetes.", "Permiten elegir elementos según el valor de un atributo.", "Con ^= se elige lo que empieza por un texto."],
  sit="Quieres estilar solo los enlaces que apuntan a archivos PDF. ¿Qué selector usas?",
  cod="""<style>
  /* [atributo$=".pdf"]: termina en .pdf */
  a[href$=".pdf"] { color: crimson; font-weight: bold; }
  input[type="email"] { background: #eff6ff; }
</style>
<a href="guia.pdf">Guía PDF</a> <a href="inicio.html">Inicio</a>
<input type="email" placeholder="correo">""",
  h="destaca los enlaces a PDF y los campos de correo según su atributo",
  pr=("Los selectores de atributo se escriben entre ___. (corchetes)", "[]", "corchetes"),
  pr2=("Para elegir lo que termina en .pdf se usa el operador ___=. (un carácter)", "$"),
  ec="olvidar las comillas del valor del atributo"),
K("Pseudoclase hover",
  d="estado que se activa al pasar el mouse por encima",
  u="dar respuesta visual al pasar el cursor",
  mas="a:hover se aplica solo mientras el mouse está sobre el enlace. Se usa para cambiar color, fondo o sombra. Combinada con transition (que verás más adelante) da cambios suaves.",
  k=["La pseudoclase hover actúa cuando el mouse está encima.", "Las pseudoclases se escriben con dos puntos.", "El hover es muy usado en botones y enlaces."],
  sit="Quieres que un botón cambie de color mientras el mouse pasa por encima. ¿Qué usas?",
  cod="""<style>
  .boton { background: steelblue; color: white; padding: 10px 18px; border: none; }
  /* :hover solo se aplica mientras el mouse está encima */
  .boton:hover { background: darkblue; }
</style>
<button class="boton">Pasa el mouse</button>""",
  h="oscurece el botón mientras el mouse está encima",
  pr=("La pseudoclase del mouse encima se escribe :___. (5 letras)", "hover"),
  pr2=("Las pseudoclases empiezan con ___. (dos puntos, con :)", ":", "dos puntos"),
  ec="usar hover en pantallas táctiles como única señal",
  err=("a {\n  color: blue;\n}\na::hover {\n  color: red;\n}", 4, "Hover es una pseudoclase y lleva un solo signo de dos puntos: a:hover.")),
K("Pseudoclase focus",
  d="estado de un campo o botón seleccionado con teclado o clic",
  u="mostrar dónde está el cursor o el foco",
  mas="input:focus se aplica cuando el campo está activo. Es clave para la accesibilidad: quien navega con teclado necesita ver dónde está. Nunca quites el contorno sin poner una alternativa visible.",
  k=["La pseudoclase focus actúa cuando un elemento está seleccionado.", "Es fundamental para quien navega con el teclado.", "No conviene quitar el contorno de foco sin sustituirlo."],
  sit="Quieres que un campo de texto se resalte cuando el usuario lo selecciona. ¿Qué usas?",
  cod="""<style>
  input { padding: 8px; border: 2px solid #cbd5e1; }
  /* :focus se aplica cuando el campo está activo */
  input:focus { border-color: dodgerblue; outline: none; box-shadow: 0 0 6px dodgerblue; }
</style>
<input placeholder="Haz clic aquí o pulsa Tab">""",
  h="resalta con un borde azul el campo que está activo",
  pr=("La pseudoclase de un campo activo se escribe :___. (5 letras)", "focus"),
  pr2=("Quien navega con ___ necesita ver el foco. (una palabra)", "teclado"),
  ec="quitar el contorno de foco sin poner nada en su lugar"),
K("First-child y nth-child",
  d="pseudoclases que eligen hijos según su posición",
  u="estilar el primero, el último o filas alternas",
  mas=":first-child elige el primer hijo y :last-child el último. :nth-child(2) elige el segundo y :nth-child(even) los pares. Es la forma clásica de hacer tablas con filas alternadas de color.",
  k=["La pseudoclase first-child elige el primer hijo.", "La expresión nth-child(even) elige los hijos pares.", "Sirve para filas alternadas de tablas y listas."],
  sit="Quieres pintar de gris las filas pares de una lista. ¿Qué pseudoclase usas?",
  cod="""<style>
  /* even: los pares (2.º, 4.º...) */
  li:nth-child(even) { background: #e2e8f0; }
  /* el primero en negrita */
  li:first-child { font-weight: bold; }
</style>
<ul><li>Uno</li><li>Dos</li><li>Tres</li><li>Cuatro</li></ul>""",
  h="alterna el fondo de los elementos pares y pone en negrita el primero",
  pr=("Para elegir los hijos pares se usa nth-child(___). (4 letras)", "even"),
  pr2=("La pseudoclase que elige el primer hijo es :first-___. (5 letras)", "child"),
  ec="contar desde cero en lugar de desde uno"),
K("Before y after",
  d="pseudoelementos que añaden contenido antes o después",
  u="añadir adornos o iconos sin tocar el HTML",
  mas="Con ::before y ::after se inserta contenido generado mediante la propiedad content. Se usan para iconos, comillas o decoraciones. Llevan dos signos de dos puntos, a diferencia de las pseudoclases. El contenido no se puede seleccionar.",
  k=["Los pseudoelementos se escriben con dos signos de dos puntos.", "La propiedad content define el texto que se inserta.", "El contenido generado no forma parte del HTML."],
  sit="Quieres añadir una flecha antes de cada enlace sin cambiar el HTML. ¿Qué usas?",
  cod="""<style>
  /* ::before inserta contenido antes del elemento */
  a::before { content: "→ "; color: tomato; }
  /* ::after lo inserta después */
  a::after { content: " ✓"; }
</style>
<a href="#">Seguir leyendo</a>""",
  h="añade una flecha antes y una marca después de un enlace sin tocar el HTML",
  pr=("La propiedad que define el texto de ::before es ___. (7 letras)", "content"),
  pr2=("Los pseudoelementos se escriben con ___ signos de dos puntos. (un número)", "2", "dos"),
  ec="olvidar la propiedad content y no ver nada"),
K("Propiedad color",
  d="propiedad que cambia el color del texto",
  u="dar color a letras y enlaces",
  mas="color afecta al texto (y al borde si no tiene otro color). Acepta nombres, hexadecimales, rgb y hsl. Se hereda: lo que pongas en el body llega a casi todos los textos. Cuida el contraste con el fondo.",
  k=["La propiedad color cambia el color del texto.", "El color del texto se hereda de padres a hijos.", "Hay que cuidar el contraste con el fondo."],
  sit="Quieres cambiar el color de las letras de un título. ¿Qué propiedad usas?",
  cod="""<style>
  /* color: color del TEXTO; se hereda en los hijos */
  body { color: #1e293b; }
  h1 { color: tomato; }
</style>
<h1>Título rojo</h1>
<p>Texto con el color del body</p>""",
  h="cambia el color del texto de la página y de un título",
  pr=("La propiedad que cambia el color de las letras es ___. (5 letras)", "color"),
  pr2=("El color del texto se ___ de padres a hijos. (una palabra)", "hereda"),
  ec="usar color de texto muy parecido al fondo"),
K("Background-color",
  d="propiedad que da color de fondo a un elemento",
  u="colorear el fondo de cajas, botones y páginas",
  mas="background-color pinta el fondo del área del elemento (contenido, relleno y borde). Si no se indica, el fondo es transparente. Combínalo con un color de texto que contraste.",
  k=["La propiedad background-color pinta el fondo.", "Por defecto el fondo de los elementos es transparente.", "Hay que elegir un texto que contraste con el fondo."],
  sit="Quieres dar un fondo azul claro a una caja. ¿Qué propiedad usas?",
  cod="""<style>
  .caja {
    background-color: #dbeafe;   /* fondo azul claro */
    color: #1e3a8a;              /* texto azul oscuro: buen contraste */
    padding: 16px;
  }
</style>
<div class="caja">Caja con fondo de color</div>""",
  h="pinta una caja con fondo claro y texto oscuro que contrasta",
  pr=("La propiedad del color de fondo es background-___. (5 letras)", "color"),
  pr2=("El fondo por defecto de un elemento es ___. (una palabra)", "transparente"),
  ec="poner texto claro sobre un fondo claro"),
K("Font-family",
  d="propiedad que elige el tipo de letra",
  u="definir la tipografía del texto",
  mas="Se escribe una lista de fuentes por orden de preferencia terminada en una familia genérica: font-family: Georgia, serif;. Si el navegador no tiene la primera, usa la siguiente. Los nombres con espacios van entre comillas.",
  k=["La propiedad font-family elige el tipo de letra.", "Se escribe una lista de fuentes de respaldo.", "Los nombres con espacios van entre comillas."],
  sit="Quieres cambiar el tipo de letra de un párrafo y dejar una fuente de respaldo. ¿Qué propiedad usas?",
  cod="""<style>
  /* Si no existe Georgia, usa cualquier fuente serif */
  h1 { font-family: Georgia, "Times New Roman", serif; }
  p  { font-family: Arial, Helvetica, sans-serif; }
</style>
<h1>Título con serifa</h1>
<p>Párrafo sin serifa</p>""",
  h="elige una fuente con serifa para el título y otra sin serifa para el párrafo",
  pr=("La propiedad que elige el tipo de letra es font-___. (6 letras)", "family"),
  pr2=("La última fuente de la lista suele ser una familia ___, como serif. (7 letras)", "genérica", "generica"),
  ec="usar una sola fuente sin respaldo"),
K("Font-size",
  d="propiedad que fija el tamaño de la letra",
  u="hacer el texto más grande o más pequeño",
  mas="font-size admite px, em, rem y porcentajes. Lo más recomendable es usar rem para respetar el tamaño que cada persona ha configurado en su navegador. Un texto principal por debajo de 16 px (1 rem) cuesta leer.",
  k=["La propiedad font-size cambia el tamaño de la letra.", "La unidad rem respeta el tamaño configurado por el usuario.", "El texto principal debería medir al menos 16 px."],
  sit="Quieres agrandar la letra de un párrafo. ¿Qué propiedad usas?",
  cod="""<style>
  p  { font-size: 1rem; }     /* tamaño normal */
  h1 { font-size: 2.5rem; }   /* 2,5 veces el normal */
  small { font-size: 0.8rem; }
</style>
<h1>Grande</h1><p>Normal</p><small>Pequeño</small>""",
  h="da tres tamaños distintos de letra con la unidad rem",
  pr=("La propiedad que cambia el tamaño de la letra es font-___. (4 letras)", "size"),
  pr2=("Una unidad que respeta el tamaño configurado por el usuario es ___. (3 letras)", "rem"),
  ec="usar letras demasiado pequeñas para el texto principal"),
K("Font-weight y font-style",
  d="propiedades que controlan negrita y cursiva",
  u="destacar texto con peso o inclinación",
  mas="font-weight va de 100 (fino) a 900 (muy grueso); 400 es normal y 700 es negrita (bold). font-style: italic pone cursiva. Ayudan a crear jerarquía visual sin cambiar de fuente.",
  k=["font-weight: bold es lo mismo que 700.", "font-style: italic pone el texto en cursiva.", "El valor 400 equivale al peso normal."],
  sit="Quieres un texto en cursiva y otro en negrita sin usar etiquetas HTML. ¿Qué propiedades usas?",
  cod="""<style>
  .negrita { font-weight: 700; }
  .cursiva { font-style: italic; }
  .fino    { font-weight: 300; }
</style>
<p class="negrita">Negrita</p>
<p class="cursiva">Cursiva</p>
<p class="fino">Fino</p>""",
  h="aplica negrita, cursiva y peso fino con tres clases",
  pr=("La propiedad que pone el texto en negrita se llama font-___. (6 letras)", "weight"),
  pr2=("Para cursiva, font-style vale ___. (6 letras)", "italic"),
  ec="usar font-weight: 1000 y esperar un efecto mayor"),
K("Line-height",
  d="propiedad que controla la altura entre líneas de texto",
  u="hacer los párrafos más fáciles de leer",
  mas="line-height: 1.5 significa 1,5 veces el tamaño de la letra. Un valor entre 1.4 y 1.7 hace que los párrafos respiren. Se recomienda escribirlo sin unidades para que se adapte al tamaño de letra.",
  k=["La propiedad line-height controla el espacio entre líneas.", "Un valor entre 1.4 y 1.7 mejora la lectura.", "Se recomienda escribir line-height sin unidad."],
  sit="Quieres que las líneas de un párrafo largo tengan más aire entre sí. ¿Qué propiedad usas?",
  cod="""<style>
  .apretado { line-height: 1; }
  .comodo   { line-height: 1.6; }  /* sin unidad: se adapta al tamaño de letra */
</style>
<p class="apretado">Texto con líneas muy pegadas entre sí, difícil de leer cuando hay muchas.</p>
<p class="comodo">Texto con líneas más separadas, mucho más cómodo de leer.</p>""",
  h="compara un párrafo con líneas pegadas y otro con interlineado cómodo",
  pr=("La propiedad del espacio entre líneas es ___-height. (4 letras)", "line"),
  pr2=("Un buen valor de line-height para párrafos es 1.___. (un número entre 4 y 7)", "5", "6", "4", "7"),
  ec="dejar el interlineado en 1 en textos largos"),
K("Text-align y text-decoration",
  d="propiedades que alinean el texto y lo subrayan o tachan",
  u="centrar títulos y quitar subrayados de enlaces",
  mas="text-align acepta left, center, right y justify. text-decoration acepta underline, line-through y none; con none se quita el subrayado de los enlaces. Alinea a la izquierda los textos largos: el texto centrado cuesta más leer.",
  k=["text-align: center centra el texto horizontalmente.", "text-decoration: none quita el subrayado de un enlace.", "Los textos largos se leen mejor alineados a la izquierda."],
  sit="Quieres centrar un título y quitar el subrayado de un enlace. ¿Qué propiedades usas?",
  cod="""<style>
  h1 { text-align: center; }
  a  { text-decoration: none; }
  .tachado { text-decoration: line-through; color: gray; }
</style>
<h1>Título centrado</h1>
<a href="#">Enlace sin subrayado</a>
<p class="tachado">Precio anterior: 50 €</p>""",
  h="centra un título, quita el subrayado de un enlace y tacha un precio",
  pr=("Para centrar el texto, text-align vale ___. (6 letras)", "center"),
  pr2=("Para quitar el subrayado, text-decoration vale ___. (4 letras)", "none"),
  ec="centrar párrafos largos y dificultar su lectura"),
K("Texto: espaciado y mayúsculas",
  d="propiedades que cambian el espacio entre letras y las mayúsculas",
  u="dar personalidad a títulos y etiquetas",
  mas="letter-spacing añade espacio entre letras y word-spacing entre palabras. text-transform cambia a uppercase (mayúsculas), lowercase (minúsculas) o capitalize (primera letra). La transformación no cambia el HTML, solo lo que se ve.",
  k=["letter-spacing cambia el espacio entre letras.", "text-transform: uppercase muestra el texto en mayúsculas.", "text-transform no modifica el texto original del HTML."],
  sit="Quieres mostrar un título en mayúsculas con letras algo separadas sin reescribirlo. ¿Qué propiedades usas?",
  cod="""<style>
  h2 { text-transform: uppercase; letter-spacing: 3px; }
  .nombre { text-transform: capitalize; }
</style>
<h2>Menú del día</h2>
<p class="nombre">ana pérez gómez</p>""",
  h="muestra un título en mayúsculas separadas y un nombre con inicial capital",
  pr=("La propiedad que cambia a mayúsculas o minúsculas es text-___. (9 letras)", "transform"),
  pr2=("Para escribir todo en mayúsculas, text-transform vale ___. (9 letras)", "uppercase"),
  ec="escribir el texto en mayúsculas en el HTML en lugar de usar CSS"),
]
