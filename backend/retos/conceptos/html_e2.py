"""HTML · Etapa 2: estructura de la página y texto."""
from ..generador import K

LISTA = [
K("DOCTYPE",
  d="primera línea que avisa al navegador de que usa HTML5",
  u="activar el modo estándar del navegador",
  mas="Se escribe como <!DOCTYPE html> y va siempre en la primera línea. Sin ella, algunos navegadores usan un modo antiguo y la página puede verse distinta. No es una etiqueta normal: no tiene cierre.",
  k=["El DOCTYPE va en la primera línea del archivo.", "El DOCTYPE no es una etiqueta con cierre.", "Sin el DOCTYPE el navegador puede usar un modo antiguo."],
  sit="Quieres que el navegador sepa desde la primera línea que tu página usa HTML5. ¿Qué escribes?",
  cod="""<!-- Siempre va en la primera línea -->
<!DOCTYPE html>
<html lang="es">
<body>
  <p>Con DOCTYPE el navegador usa el modo estándar</p>
</body>
</html>""",
  h="declara el tipo de documento al inicio de la página",
  pr=("Escribe la primera línea de toda página HTML5 (con < y >).", "<!DOCTYPE html>"),
  pr2=("La declaración que va antes de <html> se llama ___. (una palabra)", "doctype"),
  ec="escribir contenido antes del DOCTYPE",
  err=("<p>Hola</p>\n<!DOCTYPE html>\n<html lang=\"es\">\n</html>", 2, "El DOCTYPE debe ser la primera línea del archivo, antes de cualquier contenido.")),
K("Etiqueta html",
  d="elemento raíz que contiene toda la página",
  u="envolver el resto de elementos y declarar el idioma",
  mas="Todo el contenido de la página va dentro de <html> y </html>. Se le añade el atributo lang para indicar el idioma, por ejemplo lang=\"es\". Dentro solo hay dos hijos: head y body.",
  k=["La etiqueta html envuelve todo el contenido de la página.", "El atributo lang de html indica el idioma.", "Dentro de html solo van head y body."],
  sit="Necesitas el elemento que rodea a toda la página y declara que está en español. ¿Cuál es?",
  cod="""<!DOCTYPE html>
<!-- lang="es" declara que la página está en español -->
<html lang="es">
  <head><title>Idioma</title></head>
  <body><p>Hola</p></body>
</html>""",
  h="envuelve la página en html y declara que está en español",
  pr=("Para indicar el idioma, html lleva el atributo ___. (una palabra)", "lang"),
  pr2=("La etiqueta que contiene toda la página es ___. (una palabra)", "html", "<html>"),
  ec="olvidar el atributo lang en html",
  err=("<html lang=\"es\">\n  <head><title>Hola</title></head>\n  <p>Suelto</p>\n  <body></body>\n</html>", 3, "Dentro de html solo pueden ir head y body: el párrafo está suelto.")),
K("Head",
  d="parte de la página con datos que no se ven",
  u="guardar título, codificación y enlaces a estilos",
  mas="El head (cabeza) contiene información sobre la página, no contenido visible: el título de la pestaña, la codificación de caracteres, los enlaces a hojas de estilo y más. Va antes que el body.",
  k=["El head guarda información sobre la página.", "El contenido del head no aparece en la página.", "El head va antes del body."],
  sit="Quieres guardar el título de la pestaña y la codificación sin que se vean en la página. ¿Dónde lo pones?",
  cod="""<html lang="es">
  <!-- head: datos de la página, no se ven -->
  <head>
    <meta charset="utf-8">
    <title>Mi sitio</title>
  </head>
  <body><p>Esto sí se ve</p></body>
</html>""",
  h="guarda título y codificación en el head, fuera del contenido visible",
  pr=("El título y la codificación se guardan dentro de la etiqueta ___. (una palabra)", "head", "<head>"),
  pr2=("El head va ___ del body. (antes o después)", "antes"),
  ec="poner texto visible dentro del head"),
K("Body",
  d="parte de la página con todo lo que se ve",
  u="mostrar el contenido visible: texto, imágenes y enlaces",
  mas="Todo lo que el usuario ve (títulos, párrafos, imágenes, formularios) va dentro de <body>. Solo existe un body por página y se escribe después del head.",
  k=["El body contiene todo el contenido visible.", "Solo puede haber un body por página.", "El body va después del head."],
  sit="Quieres colocar los títulos, párrafos e imágenes que el visitante verá. ¿Dónde los escribes?",
  cod="""<html lang="es">
  <head><title>Body</title></head>
  <!-- body: todo lo que el visitante ve -->
  <body>
    <h1>Bienvenido</h1>
    <p>Este texto aparece en la página.</p>
  </body>
</html>""",
  h="coloca el título y el párrafo visibles dentro del body",
  pr=("El contenido que se ve en la página va dentro de la etiqueta ___. (una palabra)", "body", "<body>"),
  pr2=("¿Cuántos body puede tener una página? (un número)", "1", "uno"),
  ec="escribir contenido visible fuera del body",
  err=("<html lang=\"es\">\n<head><title>Hola</title></head>\n<body>\n<h1>Título</h1>\n</body>\n<p>Fuera del body</p>\n</html>", 6, "El párrafo quedó fuera del body: todo el contenido visible debe ir dentro.")),
K("Title",
  d="título de la página que aparece en la pestaña",
  u="nombrar la pestaña y ayudar a buscadores y favoritos",
  mas="La etiqueta <title> va dentro del head y es obligatoria. Se muestra en la pestaña del navegador, en los favoritos y como enlace en los resultados de búsqueda. Conviene que sea claro y distinto en cada página.",
  k=["El title va dentro del head.", "El title se muestra en la pestaña del navegador.", "Cada página debería tener un title distinto."],
  sit="Quieres cambiar el nombre que aparece en la pestaña del navegador. ¿Qué etiqueta editas?",
  cod="""<head>
  <meta charset="utf-8">
  <!-- Este texto se ve en la pestaña -->
  <title>Recetas de la abuela</title>
</head>""",
  h="pone nombre a la pestaña del navegador",
  pr=("El nombre de la pestaña se escribe dentro de la etiqueta ___. (una palabra)", "title", "<title>"),
  pr2=("La etiqueta title se escribe dentro de ___. (una palabra)", "head", "<head>"),
  ec="dejar la página sin title o con «Documento sin título»"),
K("Meta charset",
  d="declaración del juego de caracteres de la página",
  u="mostrar bien tildes, eñes y emojis",
  mas="La línea <meta charset=\"utf-8\"> le dice al navegador cómo leer los caracteres. Con UTF-8 se ven bien la ñ, las tildes y los emojis. Si la olvidas, puedes ver símbolos raros como Ã±.",
  k=["Meta charset utf-8 permite ver tildes, eñes y emojis.", "Meta charset va en el head.", "Sin meta charset pueden aparecer símbolos extraños."],
  sit="Tu página muestra símbolos raros en lugar de la ñ y las tildes. ¿Qué te falta?",
  cod="""<head>
  <!-- utf-8: tildes, eñes y emojis se ven bien -->
  <meta charset="utf-8">
  <title>Acentuación</title>
</head>
<body><p>Canción, niño y 🎉</p></body>""",
  h="declara utf-8 para ver bien tildes, eñes y emojis",
  pr=("Para ver bien las tildes se usa la codificación ___-8. (3 letras)", "utf"),
  pr2=("<meta charset=\"utf-8\"> se escribe dentro del ___. (una palabra)", "head"),
  ec="olvidar meta charset y ver letras raras",
  err=("<head>\n  <meta charset=utf-8>\n  <title>Hola</title>\n</head>", 2, "El valor de charset debe ir entre comillas: charset=\"utf-8\".")),
K("Meta description",
  d="resumen corto de la página para los buscadores",
  u="mejorar el texto que aparece en los resultados de búsqueda",
  mas="Se escribe en el head como <meta name=\"description\" content=\"...\">. Google suele mostrarla bajo el título en los resultados. Una buena descripción tiene una o dos frases claras, de unos 150 caracteres.",
  k=["Meta description resume la página para los buscadores.", "Meta description se escribe en el head.", "Una descripción clara anima a hacer clic en el resultado."],
  sit="Quieres controlar el resumen que muestra Google bajo el título de tu página. ¿Qué agregas?",
  cod="""<head>
  <title>Pastelería Luna</title>
  <!-- name dice qué dato es; content es el resumen -->
  <meta name="description" content="Tartas y galletas artesanales hechas cada mañana en Lima.">
</head>""",
  h="añade un resumen de la página pensado para los buscadores",
  pr=("En <meta name=\"description\" content=\"...\">, el resumen va dentro del atributo ___. (una palabra)", "content"),
  pr2=("Un buen resumen de página suele tener unos 150 ___. (una palabra)", "caracteres"),
  ec="copiar la misma descripción en todas las páginas"),
K("Títulos h1 a h6",
  d="seis niveles de títulos, de más a menos importante",
  u="organizar el contenido en títulos y subtítulos",
  mas="h1 es el título principal y h6 el menos importante. No sirven para dar tamaño al texto: sirven para dar estructura. Conviene un solo h1 por página y no saltarse niveles (de h2 a h4, por ejemplo).",
  k=["h1 es el título más importante y h6 el menos importante.", "Conviene usar un solo h1 por página.", "Los títulos se usan para dar estructura, no solo tamaño."],
  sit="Quieres un título principal y, debajo, subtítulos jerarquizados. ¿Qué etiquetas usas?",
  cod="""<!-- h1: título principal (solo uno por página) -->
<h1>Guía de viaje</h1>
<!-- h2: sección principal -->
<h2>Qué ver</h2>
<!-- h3: subsección dentro de h2 -->
<h3>Museos</h3>""",
  h="crea un título principal, una sección y una subsección",
  pr=("El título más importante de la página usa la etiqueta ___. (2 caracteres)", "h1"),
  pr2=("¿Cuántos niveles de títulos existen en HTML? (un número)", "6", "seis"),
  ec="usar h3 solo porque se ve más pequeño",
  err=("<h1>Mi blog</h1>\n<h2>Recetas</h3>\n<p>Texto</p>", 2, "El h2 se cerró con </h3>: la etiqueta de cierre debe ser </h2>.")),
K("Párrafo",
  d="bloque de texto separado por espacio arriba y abajo",
  u="mostrar texto en párrafos",
  mas="La etiqueta <p> crea un párrafo. El navegador deja un espacio antes y después. Si escribes muchos espacios o saltos de línea en el código, el navegador los junta en uno solo.",
  k=["La etiqueta p crea un párrafo de texto.", "El navegador junta los espacios repetidos del código en uno solo.", "Cada párrafo necesita su propia etiqueta p."],
  sit="Quieres escribir dos bloques de texto separados por un pequeño espacio. ¿Qué etiqueta usas para cada uno?",
  cod="""<!-- Cada <p> es un párrafo distinto -->
<p>Este es el primer párrafo.</p>
<p>Este es el segundo.
Aunque lo escriba en dos líneas,     se ve junto.</p>""",
  h="crea dos párrafos; el segundo ignora el salto y los espacios extra",
  pr=("La etiqueta de un párrafo es ___. (una letra)", "p", "<p>"),
  pr2=("El navegador junta los espacios repetidos en ___. (un número)", "1", "uno"),
  ec="pulsar Enter varias veces esperando más espacio",
  err=("<p>Primer párrafo</p>\n<p>Segundo párrafo<p>\n<p>Tercero</p>", 2, "El segundo párrafo se cerró con <p> en lugar de </p>.")),
K("Salto de línea br",
  d="etiqueta que corta la línea sin abrir otro párrafo",
  u="escribir direcciones, versos o líneas cortas",
  mas="La etiqueta <br> no tiene cierre. Sirve para saltar de línea dentro de un mismo párrafo, por ejemplo en una dirección postal o en un poema. No la uses para separar bloques: para eso están los párrafos.",
  k=["La etiqueta br hace un salto de línea.", "La etiqueta br no lleva etiqueta de cierre.", "Para separar bloques de texto es mejor usar párrafos."],
  sit="Quieres escribir una dirección en dos líneas dentro del mismo párrafo. ¿Qué usas?",
  cod="""<p>
  Calle Los Olivos 123<!-- br corta aquí la línea -->
  <br>
  Lima, Perú
</p>""",
  h="parte una dirección en dos líneas dentro de un mismo párrafo",
  pr=("Escribe la etiqueta que hace un salto de línea (con < y >).", "<br>", "<br/>", "<br />"),
  pr2=("La etiqueta br ___ lleva etiqueta de cierre. (sí o no)", "no"),
  ec="usar varios br seguidos para crear espacio"),
K("Línea horizontal hr",
  d="línea que separa temas dentro de la página",
  u="dividir visualmente dos bloques de contenido",
  mas="La etiqueta <hr> dibuja una línea de lado a lado. Significa un cambio de tema, así que úsala para separar contenidos distintos. Igual que br, no lleva etiqueta de cierre.",
  k=["La etiqueta hr dibuja una línea horizontal.", "La etiqueta hr marca un cambio de tema.", "La etiqueta hr no lleva cierre."],
  sit="Quieres dibujar una línea que separe el final de un tema del comienzo de otro. ¿Qué etiqueta usas?",
  cod="""<h2>Capítulo 1</h2>
<p>Fin del primer tema.</p>
<!-- hr dibuja la línea divisoria -->
<hr>
<h2>Capítulo 2</h2>
<p>Empieza otro tema.</p>""",
  h="separa dos capítulos con una línea horizontal",
  pr=("Escribe la etiqueta que dibuja una línea horizontal (con < y >).", "<hr>", "<hr/>", "<hr />"),
  pr2=("La etiqueta hr marca un cambio de ___. (una palabra)", "tema"),
  ec="usar hr solo como adorno en lugar de CSS"),
K("Strong",
  d="etiqueta para texto de mucha importancia",
  u="destacar una idea importante, que suele verse en negrita",
  mas="<strong> indica que el texto es importante; los navegadores lo muestran en negrita. Los lectores de pantalla lo leen con más fuerza. Para solo poner negrita sin significado especial, se usaría CSS.",
  k=["La etiqueta strong marca texto de mucha importancia.", "Los navegadores muestran strong en negrita.", "Strong aporta significado, no solo aspecto."],
  sit="Quieres resaltar una advertencia muy importante dentro de una frase. ¿Qué etiqueta usas?",
  cod="""<p>
  Antes de empezar,
  <!-- strong: importante, se ve en negrita -->
  <strong>guarda tu trabajo</strong>.
</p>""",
  h="resalta como importante la frase «guarda tu trabajo»",
  pr=("Para marcar texto importante usamos la etiqueta ___. (una palabra)", "strong", "<strong>"),
  pr2=("Los navegadores muestran strong en ___. (una palabra)", "negrita"),
  ec="usar strong en frases enteras hasta que nada destaque"),
K("Em",
  d="etiqueta para dar énfasis a una palabra",
  u="cambiar el sentido de una frase con énfasis",
  mas="<em> marca énfasis, como cuando pronuncias una palabra con más intensidad. Se muestra en cursiva. No es lo mismo que strong: em cambia el tono de la frase, strong marca importancia.",
  k=["La etiqueta em marca énfasis en una palabra.", "Los navegadores muestran em en cursiva.", "Em cambia el tono de la frase, mientras strong marca importancia."],
  sit="Quieres enfatizar solo una palabra, como cuando la dices con más intensidad. ¿Qué etiqueta usas?",
  cod="""<!-- Cambiar la palabra enfatizada cambia el sentido -->
<p>Yo <em>nunca</em> dije eso.</p>
<p>Yo nunca dije <em>eso</em>.</p>""",
  h="enfatiza una palabra distinta en cada frase para cambiar su sentido",
  pr=("Para dar énfasis (cursiva) usamos la etiqueta ___. (2 letras)", "em", "<em>"),
  pr2=("Los navegadores muestran em en ___. (una palabra)", "cursiva"),
  ec="usar em solo para poner cursiva por estilo"),
K("Lista desordenada",
  d="lista de elementos sin orden, con viñetas",
  u="mostrar ideas que no siguen un orden",
  mas="Se escribe con <ul> y dentro un <li> por cada elemento. Las viñetas son solo el aspecto por defecto; con CSS se pueden cambiar. Úsala cuando el orden no importa, como una lista de ingredientes.",
  k=["La etiqueta ul crea una lista con viñetas.", "Cada elemento de la lista va en una etiqueta li.", "Se usa cuando el orden de los elementos no importa."],
  sit="Quieres mostrar ingredientes de una receta sin importar su orden. ¿Qué lista usas?",
  cod="""<!-- ul agrupa los elementos; li es cada viñeta -->
<ul>
  <li>Harina</li>
  <li>Huevos</li>
  <li>Azúcar</li>
</ul>""",
  h="muestra tres ingredientes con viñetas",
  pr=("La lista con viñetas se crea con la etiqueta ___. (2 letras)", "ul", "<ul>"),
  pr2=("Cada elemento de una lista se escribe en una etiqueta ___. (2 letras)", "li", "<li>"),
  ec="escribir li fuera de ul o de ol",
  err=("<ul>\n  <li>Harina</li>\n  <p>Huevos</p>\n  <li>Azúcar</li>\n</ul>", 3, "Dentro de ul solo deben ir elementos li; el p está fuera de lugar.")),
K("Lista ordenada",
  d="lista de elementos numerados en orden",
  u="mostrar pasos que deben seguir una secuencia",
  mas="Se escribe con <ol> y cada paso va en un <li>. El navegador numera solo. Puedes cambiar el número inicial con start o el estilo (letras, romanos) con type. Sirve para recetas, instrucciones y rankings.",
  k=["La etiqueta ol crea una lista numerada.", "El navegador numera los elementos li automáticamente.", "Se usa cuando el orden de los pasos importa."],
  sit="Quieres explicar los pasos de una receta que deben hacerse en orden. ¿Qué lista usas?",
  cod="""<!-- ol numera solo: 1, 2, 3... -->
<ol>
  <li>Mezcla los ingredientes</li>
  <li>Hornea 30 minutos</li>
  <li>Deja enfriar</li>
</ol>""",
  h="muestra tres pasos numerados automáticamente",
  pr=("La lista numerada se crea con la etiqueta ___. (2 letras)", "ol", "<ol>"),
  pr2=("El atributo que cambia el número inicial de una ol es ___. (una palabra)", "start"),
  ec="escribir los números a mano dentro de cada li"),
K("Listas anidadas",
  d="lista colocada dentro de un elemento de otra lista",
  u="mostrar categorías con subcategorías",
  mas="Para anidar, escribe la lista interna dentro del <li> que la contiene, antes de cerrarlo. Es la forma de construir índices y menús con varios niveles. Un error frecuente es poner la lista interna fuera del li.",
  k=["Una lista anidada se escribe dentro de un li de la lista principal.", "Las listas anidadas sirven para mostrar niveles y subniveles.", "Se pueden mezclar ul y ol al anidar."],
  sit="Quieres mostrar frutas y, dentro de «Frutas», una sublista de cítricos. ¿Qué haces?",
  cod="""<ul>
  <li>Frutas
    <!-- la lista interna va DENTRO del li -->
    <ul>
      <li>Naranja</li>
      <li>Limón</li>
    </ul>
  </li>
  <li>Verduras</li>
</ul>""",
  h="coloca una sublista de cítricos dentro del elemento «Frutas»",
  pr=("Una lista anidada se escribe dentro de un elemento ___. (2 letras)", "li", "<li>"),
  pr2=("Una lista dentro de otra lista se llama lista ___. (una palabra)", "anidada"),
  ec="poner la lista interna fuera de un li",
  err=("<ul>\n  <li>Frutas</li>\n  <ul>\n    <li>Naranja</li>\n  </ul>\n</ul>", 3, "La lista interna debe ir dentro del li «Frutas», no después de cerrarlo.")),
K("Cita blockquote",
  d="bloque que contiene una cita de otra fuente",
  u="mostrar citas textuales de otras personas",
  mas="<blockquote> se usa para citas largas de otra persona o libro. Suele mostrarse con sangría. Para citas cortas dentro de una frase existe la etiqueta <q>. El atributo cite puede guardar la dirección de la fuente.",
  k=["La etiqueta blockquote contiene una cita larga.", "La etiqueta q sirve para citas cortas dentro de una frase.", "El atributo cite guarda la fuente de la cita."],
  sit="Quieres mostrar un párrafo entero copiado de un libro, indicando que es una cita. ¿Qué etiqueta usas?",
  cod="""<!-- blockquote: cita larga, suele verse con sangría -->
<blockquote cite="https://es.wikipedia.org">
  <p>La web es para todos.</p>
</blockquote>
<!-- q: cita corta dentro de una frase -->
<p>Como dijo ella: <q>practica cada día</q>.</p>""",
  h="muestra una cita larga y otra corta dentro de una frase",
  pr=("Para una cita larga usamos la etiqueta ___. (una palabra)", "blockquote", "<blockquote>"),
  pr2=("Para una cita corta dentro de una frase usamos la etiqueta ___. (una letra)", "q", "<q>"),
  ec="usar blockquote solo para sangrar un texto"),
K("Pre y code",
  d="etiquetas para mostrar código respetando espacios",
  u="enseñar fragmentos de código en la página",
  mas="<code> marca un trozo de código dentro de una frase. <pre> conserva espacios y saltos de línea tal como los escribes. Se usan juntas para mostrar bloques de código: <pre><code>...</code></pre>.",
  k=["La etiqueta code marca un fragmento de código.", "La etiqueta pre respeta los espacios y saltos de línea.", "Para bloques de código se combinan pre y code."],
  sit="Quieres mostrar un fragmento de código con su sangría exacta en tu página. ¿Qué usas?",
  cod="""<!-- code dentro de una frase -->
<p>Usa <code>console.log()</code> para mostrar datos.</p>
<!-- pre conserva los espacios y saltos -->
<pre><code>function saludar() {
  return "Hola";
}</code></pre>""",
  h="muestra código en una frase y un bloque con su sangría original",
  pr=("La etiqueta que conserva los espacios y saltos de línea es ___. (3 letras)", "pre", "<pre>"),
  pr2=("La etiqueta que marca un fragmento de código es ___. (4 letras)", "code", "<code>"),
  ec="pegar código en un p y perder su sangría"),
K("Entidades HTML",
  d="códigos que escriben caracteres especiales",
  u="mostrar símbolos como <, > y & sin romper el código",
  mas="Los símbolos < y > forman las etiquetas, así que para mostrarlos como texto se escriben &lt; y &gt;. Para el & se usa &amp;. También existe &copy; para ©. Cada entidad empieza con & y termina con ;.",
  k=["Las entidades empiezan con & y terminan con ;.", "&lt; muestra el símbolo < como texto.", "&amp; muestra el símbolo & como texto."],
  sit="Quieres que en pantalla se vea el texto «<p>» sin que el navegador lo tome como etiqueta. ¿Qué usas?",
  cod="""<!-- &lt; se ve como <  y  &gt; se ve como > -->
<p>La etiqueta &lt;p&gt; crea un párrafo.</p>
<!-- &amp; se ve como & -->
<p>Pan &amp; mantequilla</p>
<!-- &copy; se ve como © -->
<p>&copy; 2026 Mi sitio</p>""",
  h="muestra símbolos especiales como texto sin que se confundan con etiquetas",
  pr=("La entidad que muestra el símbolo < es &___; (2 letras)", "lt"),
  pr2=("Las entidades empiezan con & y terminan con ___. (un carácter)", ";"),
  ec="escribir < directamente y romper la página"),
K("Sub y sup",
  d="etiquetas para texto en subíndice y superíndice",
  u="escribir fórmulas y exponentes",
  mas="<sub> baja el texto (como en H₂O) y <sup> lo sube (como en 5²). Se usan en química, matemáticas y notas al pie. Fíjate en que sup significa superíndice, es decir, arriba.",
  k=["La etiqueta sub escribe texto por debajo de la línea.", "La etiqueta sup escribe texto por encima de la línea.", "Se usan para fórmulas, exponentes y notas."],
  sit="Quieres escribir la fórmula del agua con el 2 pequeño y bajo. ¿Qué etiqueta usas?",
  cod="""<!-- sub: texto bajo, como en H2O -->
<p>Agua: H<sub>2</sub>O</p>
<!-- sup: texto alto, como en un exponente -->
<p>Área: 5<sup>2</sup> = 25</p>""",
  h="escribe una fórmula química con subíndice y un exponente con superíndice",
  pr=("Para un exponente, como el 2 de 5², usamos la etiqueta ___. (3 letras)", "sup", "<sup>"),
  pr2=("Para el 2 de H₂O usamos la etiqueta ___. (3 letras)", "sub", "<sub>"),
  ec="confundir sub con sup al escribir fórmulas"),
]
