"""HTML · Etapa 5: semántica y buenas prácticas."""
from ..generador import K

LISTA = [
K("HTML semántico",
  d="uso de etiquetas cuyo nombre indica su significado",
  u="dar sentido a la página para personas, buscadores y lectores de pantalla",
  mas="Una etiqueta semántica dice qué es su contenido: header es una cabecera, nav es navegación y footer un pie. Es mejor que llenar todo de div, porque los buscadores y los lectores de pantalla entienden la estructura sin ayuda.",
  k=["El HTML semántico usa etiquetas que describen su contenido.", "Las etiquetas semánticas ayudan a buscadores y lectores de pantalla.", "Es preferible usar header, nav o footer antes que muchos div."],
  sit="Quieres que un buscador entienda qué parte de tu página es la cabecera y cuál el pie. ¿Qué tipo de HTML escribes?",
  cod="""<!-- Semántico: cada etiqueta dice qué es -->
<header>Mi sitio</header>
<main>Contenido principal</main>
<footer>© 2026</footer>
<!-- No semántico: div no dice nada -->
<div>Mi sitio</div>""",
  h="compara etiquetas que describen su contenido con un div sin significado",
  pr=("El HTML que usa etiquetas con significado se llama ___. (una palabra)", "semántico", "semantico"),
  pr2=("Una etiqueta como div ___ dice qué contiene. (no)", "no"),
  ec="usar div para todo aunque exista una etiqueta semántica"),
K("Header",
  d="etiqueta de la cabecera de una página o sección",
  u="agrupar el logo, el título y la navegación de arriba",
  mas="<header> suele contener el logo, el título del sitio y a veces el menú. Una página puede tener un header principal y, además, cabeceras dentro de artículos o secciones. No confundirlo con head, que va dentro de html.",
  k=["La etiqueta header agrupa la cabecera visible.", "Header no es lo mismo que head.", "Un header suele contener el logo y el título."],
  sit="Quieres agrupar arriba el logo y el título del sitio. ¿Qué etiqueta semántica usas?",
  cod="""<body>
  <!-- header: cabecera visible (distinta de head) -->
  <header>
    <img src="img/logo.png" alt="Logo de Mi Tienda" width="60">
    <h1>Mi Tienda</h1>
  </header>
</body>""",
  h="agrupa logo y título en la cabecera visible de la página",
  pr=("La cabecera visible de la página usa la etiqueta ___. (6 letras)", "header", "<header>"),
  pr2=("La etiqueta head (sin r) va dentro de ___. (4 letras)", "html", "<html>"),
  ec="confundir header con head",
  err=("<head>\n  <img src=\"logo.png\" alt=\"Logo\">\n  <h1>Mi Tienda</h1>\n</head>", 2, "El logo y el título visibles van en header dentro del body, no en head.")),
K("Nav",
  d="etiqueta para el bloque de enlaces de navegación",
  u="agrupar el menú principal del sitio",
  mas="<nav> contiene los enlaces más importantes para moverse por el sitio. Se escribe normalmente con una lista de enlaces dentro. No todos los grupos de enlaces son nav: solo los principales.",
  k=["La etiqueta nav agrupa los enlaces de navegación principal.", "Dentro de nav suele haber una lista de enlaces.", "Los lectores de pantalla permiten saltar directamente a la nav."],
  sit="Quieres agrupar el menú con Inicio, Cursos y Contacto. ¿Qué etiqueta semántica usas?",
  cod="""<!-- nav: el menú principal -->
<nav>
  <ul>
    <li><a href="index.html">Inicio</a></li>
    <li><a href="cursos.html">Cursos</a></li>
    <li><a href="contacto.html">Contacto</a></li>
  </ul>
</nav>""",
  h="crea un menú de tres enlaces dentro de una nav",
  pr=("La etiqueta del menú de navegación principal es ___. (3 letras)", "nav", "<nav>"),
  pr2=("Dentro de nav los enlaces suelen ir en una ___. (una palabra)", "lista"),
  ec="envolver en nav cada enlace suelto de la página"),
K("Main",
  d="contenido principal y único de cada página",
  u="señalar la parte esencial de la página",
  mas="<main> contiene lo que hace única a esa página, sin repetir cabecera, menú ni pie. Solo debe haber uno visible por página. Permite a los lectores de pantalla saltar directamente al contenido.",
  k=["La etiqueta main contiene el contenido principal de la página.", "Solo debe haber un main visible por página.", "El main no incluye la cabecera ni el pie repetidos."],
  sit="Quieres marcar la parte única de cada página, sin menú ni pie. ¿Qué etiqueta usas?",
  cod="""<header>Mi sitio</header>
<nav>Menú</nav>
<!-- main: solo el contenido propio de esta página -->
<main>
  <h1>Sobre nosotros</h1>
  <p>Somos un equipo de tres personas.</p>
</main>
<footer>© 2026</footer>""",
  h="marca el contenido propio de la página entre cabecera y pie",
  pr=("La etiqueta del contenido principal de la página es ___. (4 letras)", "main", "<main>"),
  pr2=("Debe haber solo ___ main visible por página. (un número)", "1", "uno"),
  ec="usar varios main en la misma página"),
K("Section",
  d="sección temática de la página, normalmente con título",
  u="dividir el contenido en partes con un tema propio",
  mas="<section> agrupa contenido de un mismo tema y casi siempre lleva su propio título (h2, h3…). Si solo necesitas un contenedor para dar estilo, usa div: section es para dividir por significado.",
  k=["La etiqueta section agrupa contenido de un mismo tema.", "Una section normalmente lleva su propio título.", "Para contenedores sin significado se usa div."],
  sit="Quieres dividir tu página en partes temáticas, cada una con su título. ¿Qué etiqueta usas?",
  cod="""<main>
  <!-- cada section trata un tema distinto y lleva título -->
  <section>
    <h2>Servicios</h2>
    <p>Diseño y desarrollo web.</p>
  </section>
  <section>
    <h2>Contacto</h2>
    <p>Escríbenos cuando quieras.</p>
  </section>
</main>""",
  h="divide el contenido principal en dos secciones con su título",
  pr=("La etiqueta que agrupa contenido por tema es ___. (7 letras)", "section", "<section>"),
  pr2=("Una section casi siempre lleva su propio ___. (6 letras)", "título", "titulo"),
  ec="usar section como si fuera un div cualquiera"),
K("Article",
  d="contenido completo e independiente que tiene sentido por sí solo",
  u="publicar entradas de blog, noticias o tarjetas de producto",
  mas="Un <article> se podría copiar a otro sitio y seguiría entendiéndose: una noticia, un comentario o una entrada de blog. Cada artículo suele llevar su título y puede tener su propia cabecera y pie.",
  k=["La etiqueta article contiene contenido independiente.", "Una noticia o entrada de blog es un buen article.", "Un article puede tener su propio header."],
  sit="Quieres publicar una noticia que podría leerse sola, aparte del resto de la página. ¿Qué etiqueta usas?",
  cod="""<!-- article: se entiende por sí solo -->
<article>
  <header>
    <h2>Abre la nueva biblioteca</h2>
    <p>Publicado el 5 de marzo</p>
  </header>
  <p>Desde hoy, la biblioteca abre de lunes a sábado.</p>
</article>""",
  h="publica una noticia completa con cabecera propia",
  pr=("Una noticia independiente se escribe en la etiqueta ___. (7 letras)", "article", "<article>"),
  pr2=("Un article se entiende por ___ solo. (una palabra)", "sí", "si"),
  ec="usar article para contenido que depende del resto"),
K("Aside",
  d="contenido complementario relacionado con lo principal",
  u="mostrar notas laterales, anuncios o enlaces relacionados",
  mas="<aside> contiene información que acompaña al contenido principal, pero que no es esencial: una barra lateral, un dato curioso o enlaces relacionados. Si lo quitaras, el contenido principal seguiría teniendo sentido.",
  k=["La etiqueta aside contiene contenido complementario.", "El contenido de un aside no es esencial para entender lo principal.", "Una barra lateral es un uso típico de aside."],
  sit="Quieres añadir un cuadro lateral con enlaces relacionados con el artículo. ¿Qué etiqueta usas?",
  cod="""<main>
  <article><h2>Cómo plantar tomates</h2><p>...</p></article>
  <!-- aside: ayuda extra, no es lo principal -->
  <aside>
    <h3>También te puede interesar</h3>
    <a href="riego.html">Guía de riego</a>
  </aside>
</main>""",
  h="añade una barra lateral con un enlace relacionado junto a un artículo",
  pr=("El contenido lateral o complementario usa la etiqueta ___. (5 letras)", "aside", "<aside>"),
  pr2=("Un aside no es ___ para entender lo principal. (una palabra)", "esencial"),
  ec="meter en aside contenido imprescindible"),
K("Footer",
  d="etiqueta del pie de una página o sección",
  u="agrupar autoría, contacto y enlaces legales al final",
  mas="<footer> va al final y suele contener los derechos de autor, el correo de contacto y enlaces como «Privacidad». Igual que header, puede usarse en la página y también dentro de artículos o secciones.",
  k=["La etiqueta footer agrupa el pie de la página.", "El pie suele incluir derechos de autor y contacto.", "Un footer también puede estar dentro de un article."],
  sit="Quieres un bloque final con los derechos de autor y el correo de contacto. ¿Qué etiqueta usas?",
  cod="""<main>...</main>
<!-- footer: el pie de la página -->
<footer>
  <p>&copy; 2026 Mi Tienda. Todos los derechos reservados.</p>
  <a href="mailto:hola@mitienda.com">Contacto</a>
</footer>""",
  h="cierra la página con derechos de autor y un enlace de contacto",
  pr=("El pie de la página usa la etiqueta ___. (6 letras)", "footer", "<footer>"),
  pr2=("El footer suele incluir los derechos de ___. (5 letras)", "autor"),
  ec="olvidar el pie con la información de contacto"),
K("Div y span",
  d="contenedores genéricos sin significado propio",
  u="agrupar elementos para darles estilo o comportamiento",
  mas="<div> es un contenedor de bloque (ocupa todo el ancho) y <span> es de línea (solo ocupa su contenido). No tienen significado, así que úsalos solo cuando no exista una etiqueta semántica adecuada.",
  k=["La etiqueta div es un contenedor genérico de bloque.", "La etiqueta span es un contenedor genérico dentro de una línea.", "Div y span no aportan significado al contenido."],
  sit="Quieres envolver una palabra dentro de una frase solo para pintarla de otro color. ¿Qué etiqueta usas?",
  cod="""<!-- div: bloque que agrupa varias cosas -->
<div class="tarjeta">
  <h3>Oferta</h3>
  <!-- span: solo envuelve parte de la línea -->
  <p>Precio: <span class="rojo">20 €</span></p>
</div>""",
  h="agrupa una tarjeta en un div y resalta un precio con un span",
  pr=("El contenedor genérico que se usa dentro de una línea es ___. (4 letras)", "span", "<span>"),
  pr2=("El contenedor genérico de bloque es ___. (3 letras)", "div", "<div>"),
  ec="usar div cuando existe una etiqueta semántica mejor"),
K("Atributo id",
  d="identificador único de un elemento",
  u="enlazar, estilar o encontrar un elemento concreto",
  mas="El id debe ser único en toda la página y no puede tener espacios. Se usa para anclas (#id), para el for de los label y para seleccionar ese elemento con CSS o JavaScript. Dos elementos no deben compartir id.",
  k=["El atributo id debe ser único en la página.", "El valor de un id no lleva espacios.", "Un id sirve para anclas, label y selección en CSS o JavaScript."],
  sit="Quieres identificar un único elemento para saltar a él con un enlace. ¿Qué atributo usas?",
  cod="""<!-- id: único en toda la página -->
<h2 id="contacto">Contacto</h2>
<!-- se puede enlazar con #contacto -->
<a href="#contacto">Ir a contacto</a>""",
  h="da un id único a un título y lo enlaza con una ancla",
  pr=("El atributo que identifica de forma única un elemento es ___. (2 letras)", "id"),
  pr2=("Un id ___ puede repetirse en la página. (no)", "no"),
  ec="repetir el mismo id en varios elementos",
  err=("<p id=\"aviso\">Uno</p>\n<p id=\"aviso\">Dos</p>", 2, "El id aviso ya se usó en la línea anterior: cada id debe ser único.")),
K("Atributo class",
  d="nombre de grupo que pueden compartir varios elementos",
  u="aplicar el mismo estilo a muchos elementos",
  mas="Varios elementos pueden tener la misma clase, y un elemento puede tener varias clases separadas por espacios (class=\"boton grande\"). Es la herramienta principal para dar estilo con CSS.",
  k=["Varios elementos pueden compartir la misma class.", "Un elemento puede tener varias clases separadas por espacios.", "Las clases son la forma habitual de aplicar estilos con CSS."],
  sit="Quieres que varias tarjetas distintas compartan el mismo estilo. ¿Qué atributo usas?",
  cod="""<!-- las tres comparten la clase "tarjeta" -->
<div class="tarjeta">Uno</div>
<div class="tarjeta">Dos</div>
<!-- dos clases a la vez: tarjeta y destacada -->
<div class="tarjeta destacada">Tres</div>""",
  h="aplica la misma clase a tres tarjetas y una clase extra a la última",
  pr=("El atributo que permite compartir un nombre entre varios elementos es ___. (5 letras)", "class"),
  pr2=("Varias clases en un elemento se separan con un ___. (una palabra)", "espacio"),
  ec="usar id donde convenía una clase reutilizable"),
K("Atributos data",
  d="atributos propios que guardan datos en el elemento",
  u="guardar información para usarla con JavaScript",
  mas="Cualquier atributo que empiece con data- es válido: data-precio=\"20\", data-id=\"7\". No se ven en la página, pero JavaScript puede leerlos. Sirven para guardar datos sin inventar atributos que no existen.",
  k=["Los atributos data- guardan datos propios en un elemento.", "Los atributos data- no se ven en la página.", "JavaScript puede leer los atributos data-."],
  sit="Quieres guardar el precio de un producto dentro de su botón para usarlo después con JavaScript. ¿Qué usas?",
  cod="""<!-- data-*: datos propios, invisibles en la página -->
<button data-producto="camiseta" data-precio="20">
  Añadir al carrito
</button>""",
  h="guarda el nombre y el precio de un producto dentro del botón",
  pr=("Los atributos propios empiezan siempre con ___-. (4 letras)", "data"),
  pr2=("Los atributos data- se leen con ___. (una palabra)", "javascript"),
  ec="inventar atributos sin el prefijo data-"),
K("Jerarquía de títulos",
  d="orden lógico de h1 a h6 sin saltos de nivel",
  u="organizar el contenido como un índice entendible",
  mas="Piensa en los títulos como un esquema: h1 es el título del libro, h2 los capítulos, h3 los apartados. No saltes de h2 a h4 ni uses h4 solo por su tamaño. Los lectores de pantalla navegan por los títulos.",
  k=["Los títulos deben seguir un orden lógico sin saltos de nivel.", "Conviene un único h1 que resuma la página.", "Los lectores de pantalla navegan usando los títulos."],
  sit="Quieres que tu esquema de títulos sea lógico: título, capítulos y apartados sin saltos. ¿Qué cuidas?",
  cod="""<h1>Guía de jardinería</h1>
<h2>Plantas de interior</h2>
<h3>Cactus</h3>
<h3>Helechos</h3>
<!-- siguiente capítulo: vuelve a h2 -->
<h2>Plantas de exterior</h2>""",
  h="organiza un esquema de capítulos y apartados con títulos sin saltos",
  pr=("Tras un h2, el siguiente nivel lógico de subtítulo es ___. (2 caracteres)", "h3"),
  pr2=("Conviene un único ___ por página. (2 caracteres)", "h1"),
  ec="saltar de h2 a h5 por el tamaño del texto",
  err=("<h1>Guía</h1>\n<h2>Plantas</h2>\n<h5>Cactus</h5>", 3, "Se saltó de h2 a h5: lo lógico era usar h3.")),
K("ARIA básico",
  d="atributos aria que añaden información para lectores de pantalla",
  u="describir elementos cuando HTML solo no basta",
  mas="aria-label da un nombre a un elemento sin texto visible, como un botón con solo un icono. La primera regla de ARIA es no usarla si ya existe una etiqueta HTML adecuada: un button siempre será mejor que un div con aria.",
  k=["El atributo aria-label da un nombre accesible a un elemento.", "Si existe una etiqueta HTML adecuada, no hace falta ARIA.", "ARIA ayuda sobre todo a los lectores de pantalla."],
  sit="Un botón solo muestra una lupa y un lector de pantalla no sabe qué hace. ¿Qué atributo le añades?",
  cod="""<!-- El icono no tiene texto: aria-label lo describe -->
<button type="button" aria-label="Buscar">🔍</button>
<!-- Mejor un button real que un div con aria -->""",
  h="da nombre accesible a un botón que solo muestra una lupa",
  pr=("El atributo que da nombre accesible a un elemento sin texto es aria-___. (5 letras)", "label"),
  pr2=("La etiqueta correcta para un botón es ___. (6 letras)", "button", "<button>"),
  ec="usar aria para arreglar etiquetas mal elegidas"),
K("Details y summary",
  d="bloque desplegable creado solo con HTML",
  u="mostrar y ocultar contenido sin JavaScript",
  mas="<details> crea un bloque cerrado y <summary> es la línea visible que se pulsa para abrirlo. Es ideal para preguntas frecuentes. Con el atributo open aparece abierto desde el inicio.",
  k=["La etiqueta details crea un bloque desplegable.", "La etiqueta summary es el texto que se pulsa.", "El atributo open muestra el bloque abierto al inicio."],
  sit="Quieres una pregunta frecuente cuya respuesta se muestre al pulsarla, sin JavaScript. ¿Qué etiquetas usas?",
  cod="""<!-- summary se ve siempre; el resto se despliega al pulsar -->
<details>
  <summary>¿Cómo cambio mi contraseña?</summary>
  <p>Entra en Ajustes y pulsa «Cambiar contraseña».</p>
</details>""",
  h="oculta una respuesta que se despliega al pulsar la pregunta",
  pr=("La etiqueta del texto que se pulsa para desplegar es ___. (7 letras)", "summary", "<summary>"),
  pr2=("El atributo que muestra details abierto al inicio es ___. (4 letras)", "open"),
  ec="escribir summary fuera de details"),
K("Title y hidden",
  d="atributos globales para tooltips y para ocultar",
  u="mostrar ayudas emergentes y esconder elementos",
  mas="El atributo title muestra un pequeño texto al pasar el mouse. hidden oculta un elemento por completo, como si no existiera. Estos atributos globales se pueden usar en cualquier etiqueta; no confundas el atributo title con la etiqueta title del head.",
  k=["El atributo title muestra un texto al pasar el mouse.", "El atributo hidden oculta un elemento.", "El atributo title no es lo mismo que la etiqueta title."],
  sit="Quieres ocultar un párrafo temporalmente sin borrarlo del código. ¿Qué atributo usas?",
  cod="""<!-- title: texto al pasar el mouse -->
<abbr title="HyperText Markup Language">HTML</abbr>
<!-- hidden: el navegador no lo muestra -->
<p hidden>Este párrafo no se ve.</p>""",
  h="muestra una ayuda al pasar el mouse y oculta un párrafo",
  pr=("El atributo que oculta un elemento es ___. (6 letras)", "hidden"),
  pr2=("El atributo que muestra una ayuda al pasar el mouse es ___. (5 letras)", "title"),
  ec="confundir el atributo title con la etiqueta title"),
K("Validar HTML",
  d="comprobar que el código sigue las reglas",
  u="detectar etiquetas sin cerrar y errores antes de publicar",
  mas="El validador del W3C (validator.w3.org) revisa tu HTML y señala errores como etiquetas sin cerrar o atributos mal escritos. Un código válido se comporta de forma más predecible en todos los navegadores. Hazlo antes de publicar.",
  k=["Validar HTML sirve para encontrar errores de escritura.", "El W3C ofrece un validador gratuito.", "Conviene validar el código antes de publicar."],
  sit="Quieres encontrar etiquetas sin cerrar antes de publicar tu página. ¿Qué haces?",
  cod="""<!-- Este código tiene dos errores que un validador encontraría -->
<!DOCTYPE html>
<html lang="es">
<head><title>Prueba</title></head>
<body>
  <p>Texto sin cerrar
  <img src="foto.jpg">
</body>
</html>""",
  h="contiene un párrafo sin cerrar y una imagen sin alt que un validador señalaría",
  pr=("El organismo que ofrece un validador de HTML es el W3___. (una letra)", "c"),
  pr2=("Conviene validar el código ___ de publicar. (una palabra)", "antes"),
  ec="publicar la página sin revisar el código"),
K("Indentación y orden",
  d="forma de escribir el código con sangrías y limpieza",
  u="leer y mantener el código con facilidad",
  mas="Cada elemento hijo se escribe un nivel más a la derecha (2 o 4 espacios). Así se ve qué está dentro de qué. Usa minúsculas, cierra todas las etiquetas y deja comentarios solo donde ayuden. Un código ordenado ahorra horas de errores.",
  k=["La indentación muestra qué elementos están dentro de otros.", "Las etiquetas se escriben en minúsculas por convención.", "Un código ordenado es más fácil de corregir."],
  sit="Quieres que cualquier persona vea de un vistazo qué elemento está dentro de cuál. ¿Qué cuidas?",
  cod="""<ul>
  <li>Cada hijo va un nivel a la derecha
    <ul>
      <li>Y así sucesivamente</li>
    </ul>
  </li>
</ul>""",
  h="muestra con sangrías qué elementos están dentro de cuáles",
  pr=("Los hijos de un elemento se escriben un nivel más a la ___. (una palabra)", "derecha"),
  pr2=("Por convención, las etiquetas se escriben en ___. (una palabra)", "minúsculas", "minusculas"),
  ec="escribir todo el código en una sola línea"),
K("Enlazar CSS y JS",
  d="forma de conectar tu HTML con archivos de estilos y scripts",
  u="separar estructura, estilo y comportamiento en archivos",
  mas="Los estilos se enlazan en el head con <link rel=\"stylesheet\" href=\"css/estilos.css\">. Los scripts se enlazan con <script src=\"js/app.js\"></script>, normalmente al final del body o con defer. Separar archivos hace el sitio más ordenado.",
  k=["Los estilos se enlazan con link rel=\"stylesheet\" en el head.", "Los scripts se enlazan con script src.", "El atributo defer carga el script sin bloquear la página."],
  sit="Quieres conectar tu página con un archivo de estilos y otro de JavaScript. ¿Qué etiquetas usas?",
  cod="""<head>
  <title>Mi sitio</title>
  <!-- link: conecta el archivo de estilos -->
  <link rel="stylesheet" href="css/estilos.css">
  <!-- script con defer: se ejecuta cuando la página está lista -->
  <script src="js/app.js" defer></script>
</head>""",
  h="conecta un archivo de estilos y un script desde el head",
  pr=("El valor de rel para enlazar una hoja de estilos es ___. (10 letras)", "stylesheet"),
  pr2=("El atributo que retrasa el script hasta que la página carga es ___. (5 letras)", "defer"),
  ec="escribir mal la ruta del archivo CSS o JS",
  err=("<head>\n  <link rel=\"stylesheet\" src=\"css/estilos.css\">\n</head>", 2, "El link usa href, no src, para indicar el archivo.")),
K("Proyecto página personal",
  d="página completa que reúne todo lo aprendido",
  u="practicar la estructura de una página real",
  mas="Para cerrar HTML, crea una página sobre ti: cabecera con tu nombre, menú, una sección «Sobre mí» con foto, una lista de aficiones, una tabla de horarios y un formulario de contacto. Es el primer proyecto de tu portafolio.",
  k=["Un proyecto completo combina estructura, texto, enlaces, imágenes y formularios.", "Una página personal es un buen primer proyecto de portafolio.", "Practicar con un proyecto real fija lo aprendido."],
  sit="Quieres practicar todo lo aprendido creando una página sobre ti. ¿Qué construyes?",
  cod="""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ana Pérez · Portafolio</title>
</head>
<body>
  <header><h1>Ana Pérez</h1><nav><a href="#sobre-mi">Sobre mí</a></nav></header>
  <main>
    <section id="sobre-mi">
      <h2>Sobre mí</h2>
      <img src="img/ana.jpg" alt="Retrato de Ana sonriendo" width="150">
      <p>Estudio programación y me encanta el diseño.</p>
      <ul><li>Dibujar</li><li>Correr</li></ul>
    </section>
  </main>
  <footer>&copy; 2026 Ana Pérez</footer>
</body>
</html>""",
  h="une cabecera, menú, sección con foto, lista y pie en una página completa",
  pr=("Una página personal para mostrar tu trabajo es un ___. (una palabra)", "portafolio", "portfolio"),
  pr2=("Para cerrar HTML conviene hacer un ___ completo. (una palabra)", "proyecto"),
  ec="intentar hacer el proyecto perfecto antes de publicarlo"),
]
