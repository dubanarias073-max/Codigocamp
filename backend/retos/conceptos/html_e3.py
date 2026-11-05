"""HTML · Etapa 3: enlaces, imágenes y multimedia."""
from ..generador import K

LISTA = [
K("Enlaces con a",
  d="etiqueta que crea un enlace a otra página",
  u="llevar al visitante a otra página o recurso",
  mas="La etiqueta <a> (de anchor) crea un enlace. El atributo href contiene el destino y el texto entre las etiquetas es lo que se ve y se pulsa. Por defecto el texto aparece azul y subrayado.",
  k=["La etiqueta a crea un enlace.", "El atributo href indica el destino del enlace.", "El texto dentro de la etiqueta a es lo que el visitante pulsa."],
  sit="Quieres que una frase lleve a otra página al hacer clic. ¿Qué etiqueta usas?",
  cod="""<!-- href: destino; el texto entre las etiquetas es el que se pulsa -->
<a href="https://www.wikipedia.org">Visita Wikipedia</a>""",
  h="crea un enlace con texto pulsable que lleva a Wikipedia",
  pr=("La etiqueta que crea un enlace es ___. (una letra)", "a", "<a>"),
  pr2=("El atributo que contiene el destino del enlace es ___. (4 letras)", "href"),
  ec="escribir src en lugar de href en un enlace",
  err=("<p>Visita</p>\n<a src=\"https://www.ejemplo.com\">Mi sitio</a>", 2, "Un enlace usa href, no src, para indicar el destino.")),
K("Rutas relativas y absolutas",
  d="dos formas de escribir la dirección de un archivo",
  u="enlazar páginas propias o de otros sitios",
  mas="Una ruta absoluta lleva la dirección completa (https://sitio.com/pagina.html). Una ruta relativa parte de donde está tu archivo: contacto.html está en la misma carpeta, img/foto.jpg dentro de la carpeta img y ../index.html sube una carpeta. Para tu propio sitio se prefieren las relativas.",
  k=["Una ruta absoluta incluye la dirección completa con https.", "Una ruta relativa parte de la carpeta del archivo actual.", "Con ../ se sube una carpeta."],
  sit="Quieres enlazar otra página de tu propio sitio que está en la misma carpeta, sin escribir toda la dirección. ¿Qué tipo de ruta usas?",
  cod="""<!-- relativa: misma carpeta -->
<a href="contacto.html">Contacto</a>
<!-- relativa: sube una carpeta -->
<a href="../index.html">Inicio</a>
<!-- absoluta: dirección completa de otro sitio -->
<a href="https://www.wikipedia.org">Wikipedia</a>""",
  h="muestra dos rutas relativas a páginas propias y una ruta absoluta",
  pr=("¿Qué símbolos se escriben para subir una carpeta? (3 caracteres)", "../"),
  pr2=("La ruta que incluye https y el dominio completo es la ruta ___. (una palabra)", "absoluta"),
  ec="escribir rutas con la carpeta de tu computadora (C:\\...)"),
K("Anclas internas",
  d="enlaces que saltan a un punto de la misma página",
  u="moverse rápido por páginas largas",
  mas="Primero se pone un id a la parte de destino, por ejemplo <h2 id=\"precios\">. Luego se enlaza con href=\"#precios\". Al hacer clic, la página se desplaza hasta ese elemento. Es la base de los índices en páginas largas.",
  k=["Un ancla interna usa href con el símbolo # y un id.", "El id del destino no lleva el símbolo # al escribirlo.", "Las anclas sirven para saltar dentro de la misma página."],
  sit="Quieres un enlace «Ir a precios» que baje hasta esa sección de la misma página. ¿Qué usas?",
  cod="""<!-- El enlace apunta al id con # -->
<a href="#precios">Ir a precios</a>
<p>... mucho contenido ...</p>
<!-- El destino tiene ese id (sin #) -->
<h2 id="precios">Precios</h2>""",
  h="enlaza con una sección de la misma página usando un id",
  pr=("Para saltar al elemento con id=\"info\", el href vale ___. (con #)", "#info"),
  pr2=("El símbolo que indica un ancla en el href es ___. (un carácter)", "#"),
  ec="escribir # también en el id del destino"),
K("Target y rel",
  d="atributos para abrir enlaces en otra pestaña con seguridad",
  u="abrir enlaces externos sin perder la página actual",
  mas="target=\"_blank\" abre el enlace en una pestaña nueva. Conviene añadir rel=\"noopener noreferrer\" para que la otra página no pueda controlar la tuya. Úsalo solo cuando tenga sentido, porque abrir pestañas sin avisar puede molestar.",
  k=["target=\"_blank\" abre el enlace en una pestaña nueva.", "rel=\"noopener\" protege la página que abre el enlace.", "No conviene abrir todos los enlaces en pestañas nuevas."],
  sit="Quieres que un enlace externo se abra en una pestaña nueva de forma segura. ¿Qué atributos añades?",
  cod="""<!-- _blank = pestaña nueva; rel protege tu página -->
<a href="https://www.wikipedia.org" target="_blank" rel="noopener noreferrer">
  Wikipedia (se abre en otra pestaña)
</a>""",
  h="abre un enlace externo en una pestaña nueva con protección",
  pr=("El valor de target que abre una pestaña nueva es ___. (con guion bajo)", "_blank"),
  pr2=("Para proteger la página, target=\"_blank\" se acompaña de rel=\"___ noreferrer\". (una palabra)", "noopener"),
  ec="usar target=\"_blank\" sin rel"),
K("Mailto y tel",
  d="enlaces que abren el correo o el teléfono",
  u="permitir escribir o llamar con un solo toque",
  mas="Un enlace con href=\"mailto:alguien@correo.com\" abre el programa de correo con la dirección ya escrita. Con href=\"tel:+51999888777\" el teléfono propone llamar. En el teléfono, tel es muy útil; en computadora puede no hacer nada.",
  k=["mailto: abre el programa de correo.", "tel: permite llamar desde el teléfono.", "El número de tel: se escribe sin espacios ni guiones."],
  sit="Quieres que al tocar tu número en el móvil se inicie una llamada. ¿Qué tipo de enlace usas?",
  cod="""<!-- mailto: abre el correo con la dirección ya puesta -->
<a href="mailto:hola@ejemplo.com">Escríbenos</a>
<!-- tel: marca el número en el teléfono -->
<a href="tel:+51999888777">Llámanos</a>""",
  h="crea un enlace para escribir un correo y otro para llamar",
  pr=("El prefijo del enlace para abrir el correo es ___:. (6 letras)", "mailto"),
  pr2=("El prefijo del enlace para llamar es ___:. (3 letras)", "tel"),
  ec="dejar espacios dentro del número de tel:"),
K("Atributo download",
  d="atributo que descarga el archivo en lugar de abrirlo",
  u="ofrecer PDFs, imágenes u otros archivos para guardar",
  mas="Añade download a un enlace y el navegador guardará el archivo en vez de mostrarlo. Puedes darle un nombre: download=\"catalogo.pdf\". Funciona con archivos de tu propio sitio.",
  k=["El atributo download hace que el navegador descargue el archivo.", "Puede llevar un nombre de archivo como valor.", "Funciona con archivos de tu propio sitio."],
  sit="Quieres que un enlace descargue un PDF directamente al hacer clic. ¿Qué atributo añades?",
  cod="""<!-- download guarda el archivo en vez de abrirlo -->
<a href="docs/catalogo.pdf" download>Descargar catálogo</a>
<!-- con nombre de archivo propuesto -->
<a href="docs/catalogo.pdf" download="catalogo-2026.pdf">Descargar con otro nombre</a>""",
  h="ofrece un PDF para descargar, con y sin nombre propuesto",
  pr=("El atributo que descarga el archivo se llama ___. (8 letras)", "download"),
  pr2=("download funciona con archivos del propio ___. (una palabra)", "sitio"),
  ec="esperar que download funcione con cualquier sitio externo"),
K("Imagen img",
  d="etiqueta que muestra una imagen",
  u="insertar fotos, dibujos e iconos en la página",
  mas="La etiqueta <img> no tiene cierre. El atributo src indica dónde está el archivo y alt describe la imagen con palabras. Si el archivo no se encuentra, aparece el texto alternativo en su lugar.",
  k=["La etiqueta img muestra una imagen.", "El atributo src indica la ruta del archivo de la imagen.", "La etiqueta img no necesita etiqueta de cierre."],
  sit="Quieres mostrar una foto guardada en tu carpeta de imágenes. ¿Qué etiqueta usas?",
  cod="""<!-- src: dónde está la imagen; alt: su descripción -->
<img src="img/playa.jpg" alt="Playa con palmeras al atardecer">""",
  h="muestra una foto desde la carpeta img con su descripción",
  pr=("La etiqueta que muestra una imagen es ___. (3 letras)", "img", "<img>"),
  pr2=("El atributo de img con la ruta del archivo es ___. (3 letras)", "src"),
  ec="usar una ruta que no coincide con la carpeta real",
  err=("<p>Mi foto</p>\n<img href=\"img/foto.jpg\" alt=\"Yo\">", 2, "Una imagen usa src, no href, para indicar el archivo.")),
K("Texto alternativo alt",
  d="descripción en texto de una imagen",
  u="que todos entiendan la imagen aunque no puedan verla",
  mas="El alt lo leen los lectores de pantalla, se muestra si la imagen falla y lo usan los buscadores. Debe describir lo importante de la imagen, no decir «imagen de…». Si la imagen es solo decoración, se deja vacío: alt=\"\".",
  k=["El alt describe la imagen para quien no puede verla.", "El alt se muestra si la imagen no carga.", "Las imágenes decorativas llevan alt vacío."],
  sit="Quieres que una persona ciega sepa qué muestra la foto de tu página. ¿Qué atributo escribes?",
  cod="""<!-- Describe lo importante de la imagen -->
<img src="perro.jpg" alt="Perro labrador corriendo en la nieve">
<!-- Imagen solo decorativa: alt vacío -->
<img src="adorno.png" alt="">""",
  h="describe una imagen informativa y deja vacío el texto de una decorativa",
  pr=("El atributo con la descripción de una imagen es ___. (3 letras)", "alt"),
  pr2=("En una imagen solo decorativa, el alt se deja ___. (una palabra)", "vacío", "vacio"),
  ec="escribir «imagen» o el nombre del archivo como alt",
  err=("<img src=\"gato.jpg\" alt=gato dormido>", 1, "El valor del alt con espacios debe ir entre comillas: alt=\"gato dormido\".")),
K("Ancho y alto de imagen",
  d="atributos width y height que fijan el tamaño de una imagen",
  u="reservar espacio y controlar el tamaño de una imagen",
  mas="Con width=\"300\" height=\"200\" indicas el tamaño en píxeles. Si el navegador conoce el tamaño antes de cargar, evita que la página salte cuando aparece la imagen. Para no deformarla, mantén la proporción original.",
  k=["Los atributos width y height fijan el tamaño de la imagen en píxeles.", "Indicar el tamaño evita saltos mientras la imagen carga.", "Conviene mantener la proporción para no deformar la imagen."],
  sit="Quieres reservar el espacio de una imagen para que la página no salte al cargarla. ¿Qué atributos agregas?",
  cod="""<!-- width y height en píxeles: la página reserva el espacio -->
<img src="img/logo.png" alt="Logo de la tienda" width="200" height="80">""",
  h="muestra un logo con un tamaño fijo de 200 por 80 píxeles",
  pr=("El atributo que fija el ancho de una imagen es ___. (5 letras)", "width"),
  pr2=("El atributo que fija el alto de una imagen es ___. (6 letras)", "height"),
  ec="cambiar solo el ancho y deformar la imagen"),
K("Formatos de imagen",
  d="tipos de archivo de imagen y su mejor uso",
  u="elegir la imagen más ligera y adecuada",
  mas="JPG sirve para fotos y pesa poco. PNG admite transparencia y es ideal para logos. GIF guarda animaciones simples. SVG es un dibujo vectorial que no se pixela al ampliar. WebP es moderno y suele pesar menos que JPG y PNG.",
  k=["JPG es adecuado para fotografías.", "PNG admite fondos transparentes.", "SVG se ve nítido a cualquier tamaño."],
  sit="Necesitas un logo con fondo transparente que se vea nítido. ¿Qué formatos eliges?",
  cod="""<!-- JPG: fotos; PNG: transparencia; SVG: dibujo vectorial -->
<img src="foto.jpg" alt="Paisaje de montaña">
<img src="logo.png" alt="Logo con fondo transparente">
<img src="icono.svg" alt="Icono de casa">""",
  h="usa un formato distinto según sea foto, logo o icono",
  pr=("El formato que admite fondo transparente y es ideal para logos es ___. (3 letras)", "png"),
  pr2=("El formato vectorial que no se pixela al ampliar es ___. (3 letras)", "svg"),
  ec="subir fotos enormes sin comprimir"),
K("Figure y figcaption",
  d="par de etiquetas para una imagen con pie de foto",
  u="asociar una imagen con su descripción visible",
  mas="<figure> agrupa un contenido (imagen, gráfico, código) y <figcaption> escribe su pie. A diferencia del alt, que no se ve, el figcaption se muestra debajo de la imagen. Tiene significado: dice que ambos elementos van juntos.",
  k=["La etiqueta figure agrupa un contenido con su pie.", "La etiqueta figcaption escribe el pie visible.", "El figcaption va dentro de figure."],
  sit="Quieres una foto con una frase visible debajo, ligada a ella por significado. ¿Qué etiquetas usas?",
  cod="""<figure>
  <img src="img/volcan.jpg" alt="Volcán humeando al amanecer">
  <!-- figcaption: texto visible debajo de la imagen -->
  <figcaption>El volcán al amanecer, 2025.</figcaption>
</figure>""",
  h="muestra una foto con un pie de foto visible, unidos por significado",
  pr=("El pie de foto se escribe en la etiqueta ___. (10 letras)", "figcaption", "<figcaption>"),
  pr2=("La etiqueta que agrupa imagen y pie es ___. (6 letras)", "figure", "<figure>"),
  ec="escribir figcaption fuera de figure",
  err=("<figure>\n  <img src=\"mar.jpg\" alt=\"Mar\">\n</figure>\n<figcaption>El mar</figcaption>", 4, "El figcaption debe ir dentro del figure, no después de cerrarlo.")),
K("Picture y srcset",
  d="forma de ofrecer varias versiones de una imagen",
  u="cargar la imagen más adecuada según la pantalla",
  mas="Con srcset indicas varios archivos de distinto tamaño y el navegador elige el mejor. Con <picture> y varias etiquetas <source> puedes ofrecer otro formato (WebP) o una imagen distinta para móvil. La etiqueta img final es la de respaldo.",
  k=["Srcset ofrece varias versiones de una misma imagen.", "La etiqueta picture permite elegir imagen según formato o pantalla.", "La etiqueta img dentro de picture es la imagen de respaldo."],
  sit="Quieres servir una imagen pequeña en móvil y una grande en computadora. ¿Qué usas?",
  cod="""<picture>
  <!-- Si la pantalla mide 600px o menos, usa la pequeña -->
  <source media="(max-width: 600px)" srcset="img/portada-movil.jpg">
  <!-- Imagen de respaldo y para pantallas grandes -->
  <img src="img/portada-grande.jpg" alt="Portada del sitio">
</picture>""",
  h="elige una portada pequeña en móvil y una grande en las demás pantallas",
  pr=("La etiqueta que agrupa varias fuentes de imagen es ___. (7 letras)", "picture", "<picture>"),
  pr2=("El atributo que lista varias versiones de una imagen es ___. (6 letras)", "srcset"),
  ec="olvidar la etiqueta img de respaldo dentro de picture"),
K("Carga diferida",
  d="atributo loading que pospone la carga de imágenes",
  u="acelerar la página cargando solo lo que se ve",
  mas="Con loading=\"lazy\" el navegador descarga la imagen solo cuando el visitante se acerca a ella al desplazarse. La página inicial carga más rápido y se gasta menos internet. No lo uses en la imagen principal que aparece arriba.",
  k=["loading=\"lazy\" retrasa la descarga de la imagen.", "Mejora la velocidad de carga de la página.", "No conviene usarlo en la imagen principal de arriba."],
  sit="Quieres que las imágenes de abajo solo se descarguen cuando el visitante llegue a ellas. ¿Qué atributo usas?",
  cod="""<!-- La imagen principal carga de inmediato -->
<img src="img/portada.jpg" alt="Portada">
<!-- Esta se descarga solo al acercarse -->
<img src="img/galeria-10.jpg" alt="Foto 10 de la galería" loading="lazy">""",
  h="carga al instante la portada y retrasa una foto de la galería",
  pr=("El valor de loading que retrasa la carga de la imagen es ___. (4 letras)", "lazy"),
  pr2=("El atributo que activa la carga diferida se llama ___. (7 letras)", "loading"),
  ec="aplicar lazy a la imagen principal de la página"),
K("Favicon",
  d="icono pequeño que aparece en la pestaña del navegador",
  u="identificar tu sitio entre muchas pestañas",
  mas="Se añade en el head con <link rel=\"icon\" href=\"favicon.png\">. Es un ícono pequeño (16 o 32 píxeles) que también se ve en favoritos. Un sitio sin favicon se ve menos profesional.",
  k=["El favicon es el ícono de la pestaña del navegador.", "Se declara en el head con link rel=\"icon\".", "También aparece en la lista de favoritos."],
  sit="Quieres que tu sitio muestre un iconito propio en la pestaña. ¿Qué agregas?",
  cod="""<head>
  <title>Mi sitio</title>
  <!-- rel="icon": este archivo es el icono de la pestaña -->
  <link rel="icon" href="img/favicon.png">
</head>""",
  h="declara un icono propio para la pestaña del navegador",
  pr=("El valor de rel para el icono de la pestaña es ___. (4 letras)", "icon"),
  pr2=("El favicon se declara dentro de ___. (una palabra)", "head", "<head>"),
  ec="poner el favicon en el body"),
K("Video",
  d="etiqueta que inserta un video propio en la página",
  u="reproducir videos sin depender de otro sitio",
  mas="<video src=\"clip.mp4\" controls> muestra un reproductor. El atributo controls añade los botones de reproducir y pausar. Puedes escribir texto dentro por si el navegador no lo admite. Evita autoplay con sonido porque molesta.",
  k=["La etiqueta video inserta un reproductor de video.", "El atributo controls muestra los botones de control.", "Conviene evitar el autoplay con sonido."],
  sit="Quieres reproducir un video guardado en tu sitio con botones de pausa. ¿Qué etiqueta usas?",
  cod="""<!-- controls muestra los botones de reproducir y pausar -->
<video src="media/clase1.mp4" controls width="400">
  Tu navegador no admite video.
</video>""",
  h="muestra un reproductor con botones para un video del sitio",
  pr=("La etiqueta para insertar video es ___. (5 letras)", "video", "<video>"),
  pr2=("El atributo que muestra los botones del reproductor es ___. (8 letras)", "controls"),
  ec="olvidar controls y dejar el video sin botones"),
K("Audio",
  d="etiqueta que inserta sonido o música",
  u="reproducir música, podcasts o efectos",
  mas="<audio src=\"cancion.mp3\" controls> muestra un reproductor de audio. Funciona igual que video: controls añade los botones. Los formatos más compatibles son MP3 y OGG.",
  k=["La etiqueta audio inserta un reproductor de sonido.", "El atributo controls muestra el reproductor.", "MP3 es un formato de audio muy compatible."],
  sit="Quieres añadir un podcast con botones de reproducir y pausar. ¿Qué etiqueta usas?",
  cod="""<!-- controls: barra con play, pausa y volumen -->
<audio src="media/podcast1.mp3" controls>
  Tu navegador no admite audio.
</audio>""",
  h="muestra un reproductor de audio para un podcast",
  pr=("La etiqueta para insertar audio es ___. (5 letras)", "audio", "<audio>"),
  pr2=("Un formato de audio muy compatible es ___. (3 caracteres)", "mp3"),
  ec="usar autoplay de música sin que el usuario lo pida"),
K("Iframe",
  d="marco que muestra otra página dentro de la tuya",
  u="insertar mapas, videos de YouTube u otros contenidos externos",
  mas="Con <iframe src=\"...\"> se incrusta una página dentro de otra. Así se añaden mapas de Google o videos de YouTube. Siempre incluye title para accesibilidad y usa solo sitios de confianza.",
  k=["La etiqueta iframe incrusta otra página dentro de la tuya.", "Se usa para mapas y videos de otros sitios.", "Un iframe debe llevar title por accesibilidad."],
  sit="Quieres mostrar un mapa de otro sitio dentro de tu página. ¿Qué etiqueta usas?",
  cod="""<!-- iframe: una ventana a otra página dentro de la tuya -->
<iframe src="https://www.openstreetmap.org/export/embed.html"
        width="400" height="250"
        title="Mapa de nuestra ubicación"></iframe>""",
  h="incrusta un mapa externo con su título descriptivo",
  pr=("La etiqueta que incrusta otra página es ___. (6 letras)", "iframe", "<iframe>"),
  pr2=("Un iframe debe llevar el atributo ___ para accesibilidad. (5 letras)", "title"),
  ec="incrustar sitios que no son de confianza"),
K("Imagen como enlace",
  d="imagen colocada dentro de una etiqueta a",
  u="hacer que una imagen se pueda pulsar",
  mas="Para que una imagen lleve a algún sitio, escribe la etiqueta img dentro de la etiqueta a. El alt describe a dónde lleva el enlace, no solo la imagen. Es habitual en logos que vuelven al inicio.",
  k=["Una imagen enlazada va dentro de una etiqueta a.", "El alt de una imagen enlazada debe indicar el destino.", "Los logos suelen enlazar a la página de inicio."],
  sit="Quieres que al pulsar el logo se vuelva a la página de inicio. ¿Qué haces?",
  cod="""<!-- La imagen va dentro del enlace -->
<a href="index.html">
  <img src="img/logo.png" alt="Ir al inicio de Mi Tienda" width="120">
</a>""",
  h="hace que el logo lleve a la página de inicio al pulsarlo",
  pr=("Para enlazar una imagen, la etiqueta img va dentro de la etiqueta ___. (una letra)", "a", "<a>"),
  pr2=("El alt de un logo enlazado debe decir a dónde ___. (una palabra)", "lleva"),
  ec="dejar vacío el alt de una imagen que es enlace"),
K("Texto de enlace claro",
  d="texto de enlace que explica a dónde lleva",
  u="que los enlaces se entiendan solos",
  mas="Evita «haz clic aquí» o «más». Los lectores de pantalla pueden leer solo la lista de enlaces, y «aquí» no dice nada. Escribe texto como «Descargar la guía de HTML (PDF)». También ayuda al posicionamiento en buscadores.",
  k=["Un texto de enlace claro dice a dónde lleva.", "«Haz clic aquí» es un texto de enlace poco útil.", "Los lectores de pantalla pueden leer los enlaces por separado."],
  sit="Quieres que un lector de pantalla entienda un enlace aunque lo lea fuera de contexto. ¿Qué cuidas?",
  cod="""<!-- Poco claro: no dice a dónde lleva -->
<a href="guia.pdf">Haz clic aquí</a>
<!-- Claro: se entiende solo -->
<a href="guia.pdf">Descargar la guía de HTML (PDF)</a>""",
  h="compara un texto de enlace vago con uno que explica el destino",
  pr=("Un texto de enlace poco útil es «haz clic ___». (una palabra)", "aquí", "aqui"),
  pr2=("El texto de enlace debe explicar a dónde ___. (una palabra)", "lleva"),
  ec="usar «aquí» o «más» como texto de todos los enlaces"),
K("Carpetas del sitio",
  d="forma ordenada de guardar los archivos del sitio",
  u="encontrar y enlazar archivos sin confusión",
  mas="Un sitio sencillo tiene index.html en la raíz y carpetas como img (imágenes), css (estilos) y js (scripts). Usa nombres en minúsculas, sin espacios ni tildes. Así las rutas relativas son cortas y fáciles de recordar.",
  k=["La página principal suele llamarse index.html.", "Es buena idea guardar las imágenes en una carpeta img.", "Los nombres de archivo no deberían tener espacios ni tildes."],
  sit="Quieres organizar tus archivos con carpetas para imágenes, estilos y scripts. ¿Qué haces?",
  cod="""<!-- Estructura recomendada:
     mi-sitio/
       index.html
       contacto.html
       img/logo.png
       css/estilos.css  -->
<img src="img/logo.png" alt="Logo">
<a href="contacto.html">Contacto</a>""",
  h="usa rutas cortas gracias a una estructura de carpetas ordenada",
  pr=("La página principal de un sitio suele llamarse ___.html. (5 letras)", "index"),
  pr2=("Un buen nombre de archivo no lleva espacios ni ___. (una palabra)", "tildes", "acentos"),
  ec="usar nombres con espacios y mayúsculas mezcladas"),
]
