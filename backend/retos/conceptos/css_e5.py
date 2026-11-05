"""CSS · Etapa 5: diseño adaptable, variables y efectos."""
from ..generador import K

LISTA = [
K("Media queries",
  d="reglas que se aplican solo si se cumple una condición de pantalla",
  u="cambiar el diseño según el ancho o el tipo de pantalla",
  mas="Se escriben con @media y una condición: @media (max-width: 600px) { ... } aplica lo de dentro solo si la ventana mide 600 px o menos. Es la herramienta principal del diseño responsive.",
  k=["Una media query aplica estilos solo cuando se cumple su condición.", "@media (max-width: 600px) actúa en pantallas de 600 px o menos.", "Las media queries son la base del diseño responsive."],
  sit="Quieres que, en pantallas estrechas, tres columnas pasen a ser una sola. ¿Qué usas?",
  cod="""<style>
  .fila { display: flex; gap: 8px; }
  .fila div { flex: 1; background: #fbbf24; padding: 16px; }
  /* si la ventana mide 500px o menos, se apilan */
  @media (max-width: 500px) { .fila { flex-direction: column; } }
</style>
<div class="fila"><div>1</div><div>2</div><div>3</div></div>""",
  h="apila las columnas cuando la ventana es estrecha",
  pr=("Las media queries se escriben con @___. (5 letras)", "media"),
  pr2=("@media (max-width: 600px) actúa en pantallas de 600 px o ___. (una palabra: más o menos)", "menos"),
  ec="olvidar la etiqueta meta viewport y que no funcionen en el móvil",
  err=("<style>\n  @media (max-width 600px) {\n    p { color: red; }\n  }\n</style>", 2, "Faltan los dos puntos: max-width: 600px.")),
K("Puntos de corte",
  d="anchos de pantalla en los que cambia el diseño",
  u="decidir cuándo adaptar el diseño",
  mas="Valores típicos: 600 px para móviles grandes, 900 px para tabletas y 1200 px para escritorio. No es obligatorio usar esos números: pon el punto de corte donde tu diseño se rompe. Menos puntos de corte significa un CSS más simple.",
  k=["Un punto de corte es el ancho donde cambia el diseño.", "Valores comunes son 600, 900 y 1200 píxeles.", "Es mejor poner el corte donde el diseño empieza a fallar."],
  sit="Quieres decidir a qué ancho de pantalla tu diseño pasa de móvil a tableta. ¿Qué defines?",
  cod="""<style>
  body { background: #dbeafe; }
  @media (min-width: 600px)  { body { background: #bbf7d0; } }   /* tableta */
  @media (min-width: 1000px) { body { background: #fde68a; } }   /* escritorio */
</style>
<p>Cambia el tamaño de la ventana para ver el color del fondo cambiar.</p>""",
  h="cambia el color de fondo en tres anchos de pantalla distintos",
  pr=("Un ancho de pantalla donde cambia el diseño es un punto de ___. (5 letras)", "corte"),
  pr2=("Un valor típico de punto de corte para tabletas es ___ px. (3 dígitos)", "900", "768"),
  ec="usar demasiados puntos de corte"),
K("Mobile first",
  d="enfoque que diseña primero para móvil y amplía después",
  u="empezar por lo esencial y mejorar para pantallas grandes",
  mas="Escribes los estilos base pensando en el móvil y usas min-width para añadir mejoras en pantallas mayores. El CSS queda más corto, porque el móvil no tiene que «deshacer» nada, y obliga a priorizar el contenido.",
  k=["Mobile first empieza diseñando para pantallas pequeñas.", "Se amplía el diseño con media queries de min-width.", "Obliga a decidir qué contenido es lo más importante."],
  sit="Quieres diseñar primero la versión móvil y añadir mejoras solo en pantallas grandes. ¿Qué enfoque aplicas?",
  cod="""<style>
  /* Base (móvil): una columna */
  .rejilla { display: grid; gap: 8px; }
  .rejilla div { background: #a7f3d0; padding: 16px; }
  /* Pantallas grandes: tres columnas */
  @media (min-width: 700px) { .rejilla { grid-template-columns: repeat(3, 1fr); } }
</style>
<div class="rejilla"><div>1</div><div>2</div><div>3</div></div>""",
  h="empieza con una columna y pasa a tres solo en pantallas grandes",
  pr=("En mobile first, las mejoras se añaden con ___-width. (3 letras)", "min"),
  pr2=("Mobile first empieza diseñando para el ___. (5 letras)", "móvil", "movil"),
  ec="diseñar para escritorio y luego intentar encoger todo"),
K("Imágenes adaptables",
  d="técnicas para que las imágenes se ajusten sin deformarse",
  u="mostrar fotos bien en cualquier tamaño de caja",
  mas="max-width: 100% y height: auto evitan que una imagen se salga. Con object-fit: cover la imagen llena la caja recortando lo que sobre, y con contain se ve entera dejando bordes. Así las fotos no se estiran.",
  k=["max-width: 100% evita que una imagen se salga de su contenedor.", "object-fit: cover recorta la imagen para llenar la caja.", "height: auto mantiene la proporción de la imagen."],
  sit="Quieres que una foto llene una caja sin estirarse, aunque se recorte un poco. ¿Qué propiedad usas?",
  cod="""<style>
  .marco { width: 200px; height: 120px; border: 2px solid gray; }
  .marco img { width: 100%; height: 100%; object-fit: cover; }  /* llena la caja sin deformar */
</style>
<div class="marco"><img src="https://picsum.photos/400/300" alt="Foto de ejemplo"></div>""",
  h="llena un marco con una imagen recortándola en vez de estirarla",
  pr=("El valor de object-fit que llena la caja recortando es ___. (5 letras)", "cover"),
  pr2=("Para mantener la proporción, la altura de la imagen vale ___. (4 letras)", "auto"),
  ec="dar ancho y alto fijos a una imagen y deformarla"),
K("Clamp",
  d="función que limita un valor entre un mínimo y un máximo",
  u="crear tamaños fluidos que se adaptan sin saltos",
  mas="clamp(1rem, 4vw, 2rem) elige el valor central pero nunca baja de 1rem ni sube de 2rem. Es perfecta para tipografía fluida: el título crece con la pantalla dentro de unos límites razonables.",
  k=["clamp recibe mínimo, valor ideal y máximo.", "El resultado nunca baja del mínimo ni supera el máximo.", "Es ideal para tipografía que crece con la pantalla."],
  sit="Quieres un título que crezca con la pantalla pero sin ser nunca ni diminuto ni gigante. ¿Qué función usas?",
  cod="""<style>
  h1 {
    /*      mínimo  ideal  máximo */
    font-size: clamp(1.5rem, 6vw, 3rem);
  }
</style>
<h1>Título fluido: cambia el ancho de la ventana</h1>""",
  h="hace que el título crezca con la ventana dentro de unos límites",
  pr=("La función con mínimo, ideal y máximo es ___(). (5 letras)", "clamp"),
  pr2=("El primer valor de clamp es el ___. (6 letras)", "mínimo", "minimo"),
  ec="olvidar el orden mínimo, ideal y máximo"),
K("Variables CSS",
  d="valores con nombre que se definen una vez y se reutilizan",
  u="cambiar colores y medidas de todo el sitio en un solo lugar",
  mas="Se definen con dos guiones, por ejemplo --azul: #2563eb;, normalmente en :root. Se usan con var(--azul). Si cambias el valor en un solo sitio, todo el sitio se actualiza, lo que facilita crear temas.",
  k=["Las variables CSS se definen con dos guiones delante.", "Se usan con la función var().", "Suelen declararse dentro de :root."],
  sit="Quieres cambiar el color principal de todo el sitio modificando un único valor. ¿Qué usas?",
  cod="""<style>
  :root { --principal: #7c3aed; --radio: 12px; }       /* se define una vez */
  .boton { background: var(--principal); border-radius: var(--radio); color: white; padding: 8px 16px; border: 0; }
  h1 { color: var(--principal); }
</style>
<h1>Con variables</h1><button class="boton">Botón</button>""",
  h="reutiliza un color y un radio definidos una sola vez",
  pr=("Una variable CSS empieza con ___ guiones. (un número)", "2", "dos"),
  pr2=("Para usar una variable se escribe ___(--nombre). (3 letras)", "var"),
  ec="olvidar var() y escribir solo el nombre de la variable",
  err=("<style>\n  :root { --color: teal; }\n  p { color: --color; }\n</style>", 3, "Para usar la variable se escribe var(--color), no solo --color.")),
K("Modo oscuro",
  d="tema oscuro activado por la preferencia del sistema",
  u="respetar si la persona prefiere pantallas oscuras",
  mas="La media query @media (prefers-color-scheme: dark) detecta si el sistema está en modo oscuro. Con variables CSS basta con redefinirlas dentro de ella. Cuida que el contraste del texto siga siendo suficiente.",
  k=["prefers-color-scheme detecta el tema del sistema.", "Con variables basta redefinirlas para el modo oscuro.", "En modo oscuro hay que revisar el contraste."],
  sit="Quieres que tu página use colores oscuros si el dispositivo está en modo oscuro. ¿Qué usas?",
  cod="""<style>
  :root { --fondo: #ffffff; --texto: #0f172a; }
  @media (prefers-color-scheme: dark) { :root { --fondo: #0f172a; --texto: #e2e8f0; } }
  body { background: var(--fondo); color: var(--texto); padding: 16px; }
</style>
<p>Cambia el tema de tu sistema y mira qué pasa.</p>""",
  h="cambia el fondo y el texto según el modo claro u oscuro del sistema",
  pr=("La media query del tema se escribe prefers-color-___. (6 letras)", "scheme"),
  pr2=("Para el tema oscuro, prefers-color-scheme vale ___. (4 letras)", "dark"),
  ec="olvidar revisar el contraste en modo oscuro"),
K("Función calc",
  d="función que hace operaciones con medidas distintas",
  u="mezclar unidades como % y px en un mismo valor",
  mas="calc(100% - 200px) resta 200 píxeles al ancho del padre, algo que no se puede hacer con un número fijo. Los operadores + y - necesitan espacio a ambos lados, y se pueden mezclar unidades distintas.",
  k=["calc permite operar con unidades distintas.", "Los operadores + y - necesitan espacios a ambos lados.", "calc(100% - 200px) resta 200 px al ancho disponible."],
  sit="Quieres que una caja ocupe todo el ancho menos 200 píxeles. ¿Qué función usas?",
  cod="""<style>
  .contenido { width: calc(100% - 200px); background: #bfdbfe; padding: 10px; }
  .caja { height: calc(50px + 2rem); background: #fecdd3; }
</style>
<div class="contenido">Ancho: 100% - 200px</div>
<div class="caja">Alto: 50px + 2rem</div>""",
  h="calcula medidas mezclando porcentajes, píxeles y rem",
  pr=("La función que hace operaciones con medidas es ___(). (4 letras)", "calc"),
  pr2=("En calc, los operadores + y - necesitan ___ a los lados. (una palabra)", "espacios"),
  ec="escribir calc(100%-200px) sin espacios"),
K("Transition",
  d="propiedad que anima un cambio de estilo de forma suave",
  u="hacer que hover y otros cambios no sean bruscos",
  mas="transition: background 0.3s ease; indica qué propiedad cambia, cuánto tarda y cómo acelera. Se escribe en el estado normal del elemento, no en :hover. Animar solo color, opacidad y transform es lo más fluido.",
  k=["transition suaviza el paso de un estilo a otro.", "Se escribe en el estado normal del elemento.", "Lleva la propiedad, la duración y el tipo de aceleración."],
  sit="Quieres que el cambio de color de un botón al pasar el mouse sea gradual. ¿Qué propiedad usas?",
  cod="""<style>
  .boton { background: tomato; color: white; padding: 10px 20px; border: 0;
           transition: background 0.4s ease, transform 0.2s; }   /* en el estado normal */
  .boton:hover { background: darkred; transform: scale(1.1); }
</style>
<button class="boton">Pasa el mouse</button>""",
  h="anima suavemente el color y el tamaño de un botón al pasar el mouse",
  pr=("La propiedad que suaviza un cambio de estilo es ___. (10 letras)", "transition"),
  pr2=("La duración de una transición se escribe en ___. (una unidad: segundos)", "s", "segundos"),
  ec="escribir transition dentro de :hover en lugar del estado normal"),
K("Transform",
  d="propiedad que mueve, gira, escala o inclina un elemento",
  u="cambiar la forma o posición visual sin alterar el diseño",
  mas="translate(x, y) mueve, rotate(45deg) gira, scale(1.5) agranda y skew inclina. No modifican el espacio que ocupa el elemento en el flujo y son muy eficientes de animar. Se pueden combinar separándolas con espacios.",
  k=["transform puede mover, girar, escalar e inclinar.", "No cambia el espacio que el elemento ocupa en el flujo.", "Se pueden combinar varias transformaciones en una."],
  sit="Quieres girar una tarjeta 10 grados sin afectar a los demás elementos. ¿Qué propiedad usas?",
  cod="""<style>
  .caja { width: 80px; padding: 20px; margin: 30px; background: #fde68a; text-align: center; }
  .gira   { transform: rotate(15deg); }
  .grande { transform: scale(1.3); }
  .mueve  { transform: translate(40px, 10px); }
</style>
<div class="caja gira">Gira</div><div class="caja grande">Escala</div><div class="caja mueve">Mueve</div>""",
  h="gira, agranda y mueve tres cajas sin cambiar el flujo de la página",
  pr=("La función de transform que gira es ___(). (6 letras)", "rotate"),
  pr2=("La función de transform que agranda es ___(). (5 letras)", "scale"),
  ec="creer que transform empuja a los demás elementos"),
K("Animation y keyframes",
  d="forma de crear animaciones que se repiten con pasos propios",
  u="animar elementos sin esperar a que el usuario haga algo",
  mas="Primero defines los pasos con @keyframes nombre { from {...} to {...} } y luego los aplicas con animation: nombre 2s infinite;. A diferencia de transition, la animación puede empezar sola y repetirse. Respeta a quienes prefieren menos movimiento.",
  k=["@keyframes define los pasos de una animación.", "La propiedad animation aplica los keyframes a un elemento.", "Una animación puede repetirse con infinite."],
  sit="Quieres un icono que lata sin parar sin que nadie lo toque. ¿Qué usas?",
  cod="""<style>
  @keyframes latido { 0% { transform: scale(1); } 50% { transform: scale(1.3); } 100% { transform: scale(1); } }
  .corazon { font-size: 40px; width: 50px; animation: latido 1s infinite; }
  @media (prefers-reduced-motion: reduce) { .corazon { animation: none; } }
</style>
<div class="corazon">❤️</div>""",
  h="hace latir un corazón de forma continua y respeta a quien reduce el movimiento",
  pr=("Los pasos de una animación se definen con @___. (9 letras)", "keyframes"),
  pr2=("Para repetir una animación sin fin se usa el valor ___. (8 letras)", "infinite"),
  ec="olvidar dar nombre a los keyframes o escribirlo distinto"),
K("Gradientes",
  d="fondos que mezclan dos o más colores de forma progresiva",
  u="crear fondos vistosos sin necesidad de imágenes",
  mas="linear-gradient(90deg, rojo, azul) mezcla colores en línea recta con el ángulo que indiques. radial-gradient lo hace desde un punto central. Se usan en background (no en background-color) y pesan mucho menos que una imagen.",
  k=["linear-gradient mezcla colores en línea recta.", "radial-gradient mezcla colores desde un centro.", "Los gradientes se escriben en background, no en background-color."],
  sit="Quieres un fondo que pase del azul al violeta sin usar una imagen. ¿Qué usas?",
  cod="""<style>
  .a { background: linear-gradient(90deg, #38bdf8, #8b5cf6); height: 60px; }
  .b { background: radial-gradient(circle, #fde68a, #f97316); height: 60px; }
</style>
<div class="a"></div><div class="b"></div>""",
  h="pinta una franja con degradado lineal y otra con degradado radial",
  pr=("El degradado en línea recta se escribe ___-gradient. (6 letras)", "linear"),
  pr2=("Un degradado desde un centro es un gradiente ___. (6 letras)", "radial"),
  ec="escribir el gradiente en background-color"),
K("Opacidad y transparencia",
  d="formas de hacer un elemento o color parcialmente transparente",
  u="crear capas translúcidas y atenuar elementos",
  mas="opacity: 0.5 hace transparente todo el elemento, incluido su texto. rgba(0, 0, 0, 0.5) o hsla aplican transparencia solo al color, dejando el texto normal. Usa opacity para atenuar e rgba para fondos translúcidos.",
  k=["opacity afecta a todo el elemento, incluido su texto.", "rgba aplica transparencia solo al color indicado.", "opacity: 0 hace invisible el elemento."],
  sit="Quieres un fondo negro semitransparente que no atenúe el texto de encima. ¿Qué usas?",
  cod="""<style>
  .fondo { background: url(https://picsum.photos/400/150); padding: 30px; }
  .a { background: rgba(0, 0, 0, 0.6); color: white; padding: 10px; }   /* solo el fondo es translúcido */
  .b { opacity: 0.5; background: black; color: white; padding: 10px; }   /* todo es translúcido */
</style>
<div class="fondo"><div class="a">rgba: texto nítido</div><br><div class="b">opacity: texto tenue</div></div>""",
  h="compara un fondo translúcido con rgba y otro con opacity",
  pr=("La propiedad que hace transparente todo un elemento es ___. (7 letras)", "opacity"),
  pr2=("El formato de color con transparencia es ___(r, g, b, a). (4 letras)", "rgba"),
  ec="usar opacity y atenuar también el texto sin querer"),
K("Filtros",
  d="efectos visuales como desenfoque y brillo aplicados con CSS",
  u="retocar imágenes y fondos sin editor",
  mas="filter: blur(4px) desenfoca, grayscale(100%) pasa a blanco y negro y brightness(1.2) aclara. backdrop-filter aplica el efecto a lo que hay detrás del elemento, como un cristal esmerilado.",
  k=["filter aplica efectos como blur y grayscale.", "backdrop-filter afecta a lo que hay detrás del elemento.", "Los filtros se pueden combinar separándolos con espacios."],
  sit="Quieres que una foto se vea en blanco y negro sin editarla. ¿Qué propiedad usas?",
  cod="""<style>
  .foto { width: 160px; height: 100px; object-fit: cover; }
  .bn     { filter: grayscale(100%); }
  .borrosa { filter: blur(3px); }
  .brillo  { filter: brightness(1.3) saturate(1.5); }
</style>
<img class="foto bn" src="https://picsum.photos/200/120" alt="Blanco y negro">
<img class="foto borrosa" src="https://picsum.photos/200/120" alt="Borrosa">
<img class="foto brillo" src="https://picsum.photos/200/120" alt="Brillante">""",
  h="aplica blanco y negro, desenfoque y más brillo a tres imágenes",
  pr=("La propiedad que aplica efectos visuales es ___. (6 letras)", "filter"),
  pr2=("La función de filter que pasa a blanco y negro es ___(). (9 letras)", "grayscale"),
  ec="usar filtros pesados en muchas imágenes y ralentizar la página"),
K("Cursor",
  d="propiedad que cambia el puntero del mouse",
  u="indicar qué elementos se pueden pulsar",
  mas="cursor: pointer muestra la mano en elementos pulsables que no son enlaces. Otros valores: not-allowed (prohibido), text, grab y wait. Un cursor coherente ayuda a entender la interfaz.",
  k=["cursor: pointer muestra la mano sobre elementos pulsables.", "cursor: not-allowed indica que una acción no está permitida.", "Un cursor coherente ayuda a entender la interfaz."],
  sit="Quieres que el puntero se convierta en una mano al pasar sobre una tarjeta pulsable. ¿Qué propiedad usas?",
  cod="""<style>
  .tarjeta { padding: 14px; background: #e0f2fe; margin: 6px; cursor: pointer; }
  .bloqueado { padding: 14px; background: #e5e7eb; margin: 6px; cursor: not-allowed; opacity: .6; }
</style>
<div class="tarjeta">Pulsable (mano)</div>
<div class="bloqueado">No disponible (prohibido)</div>""",
  h="muestra una mano en una tarjeta pulsable y un cursor de prohibido en otra",
  pr=("El valor de cursor que muestra la mano es ___. (7 letras)", "pointer"),
  pr2=("El valor de cursor que indica prohibido es not-___. (7 letras)", "allowed"),
  ec="dejar el cursor normal en elementos pulsables"),
K("Fuentes web",
  d="tipos de letra cargados desde internet",
  u="usar una tipografía que no está instalada en el dispositivo",
  mas="Servicios como Google Fonts ofrecen cientos de fuentes: añades un link en el head y usas el nombre en font-family. También existe @font-face para cargar un archivo propio. Cada fuente añade peso a la página, así que usa pocas.",
  k=["Las fuentes web se descargan desde internet.", "Google Fonts se enlaza desde el head de la página.", "Cada fuente adicional hace más pesada la página."],
  sit="Quieres usar una tipografía especial que los visitantes no tienen instalada. ¿Qué usas?",
  cod="""<link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
<style>
  /* si la fuente no carga, usa cursive */
  h1 { font-family: "Pacifico", cursive; font-size: 2.2rem; }
</style>
<h1>Mi tipografía especial</h1>""",
  h="carga una fuente de Google Fonts y la aplica a un título",
  pr=("La regla para cargar una fuente propia es @font-___. (4 letras)", "face"),
  pr2=("Un servicio gratuito de fuentes web de Google se llama Google ___. (5 letras)", "fonts"),
  ec="cargar muchas fuentes y ralentizar la página"),
K("Aspect-ratio",
  d="propiedad que fija la proporción entre ancho y alto",
  u="mantener cajas o videos con forma constante",
  mas="aspect-ratio: 16 / 9 hace que la altura siga siendo proporcional al ancho. Es ideal para videos, tarjetas e imágenes: reservas el espacio antes de que cargue el contenido y evitas saltos en la página.",
  k=["aspect-ratio mantiene una proporción entre ancho y alto.", "16 / 9 es una proporción típica de video.", "Evita saltos mientras el contenido carga."],
  sit="Quieres que una caja mantenga forma de pantalla panorámica 16 a 9 al cambiar de ancho. ¿Qué propiedad usas?",
  cod="""<style>
  .video { width: 100%; max-width: 320px; aspect-ratio: 16 / 9; background: #1e293b; color: white;
           display: grid; place-items: center; }
  .cuadrado { width: 100px; aspect-ratio: 1; background: #fb923c; }
</style>
<div class="video">16 / 9</div><div class="cuadrado"></div>""",
  h="mantiene una caja en proporción 16 a 9 y otra siempre cuadrada",
  pr=("La propiedad que fija la proporción de una caja es aspect-___. (5 letras)", "ratio"),
  pr2=("Una proporción típica de video panorámico es 16 / ___. (un número)", "9"),
  ec="fijar ancho y alto en píxeles y perder la proporción al redimensionar"),
K("Reset de estilos",
  d="conjunto de reglas que eliminan diferencias entre navegadores",
  u="partir de una base igual en todos los navegadores",
  mas="Cada navegador tiene márgenes y tamaños por defecto distintos. Un reset sencillo pone margin y padding en cero y box-sizing en border-box para todo. Algunas librerías como Normalize.css lo hacen con más cuidado.",
  k=["Un reset elimina las diferencias entre navegadores.", "Un reset básico pone margin y padding en cero.", "Normalize.css es una alternativa más suave."],
  sit="Quieres que tu página se vea igual en todos los navegadores desde la primera regla. ¿Qué escribes?",
  cod="""<style>
  /* Reset básico al principio del archivo */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; line-height: 1.5; }
  img { max-width: 100%; display: block; }
</style>
<h1>Con reset</h1><p>Todo parte del mismo punto.</p>""",
  h="aplica un reset básico para que todos los navegadores partan igual",
  pr=("Un reset básico pone margin y padding en ___. (4 letras)", "cero", "0"),
  pr2=("Una librería que suaviza diferencias entre navegadores se llama ___.css. (9 letras)", "normalize"),
  ec="olvidar volver a poner márgenes tras un reset"),
K("Metodología BEM",
  d="convención para nombrar clases con bloque, elemento y modificador",
  u="mantener ordenado el CSS de proyectos grandes",
  mas="BEM nombra las clases así: bloque (.tarjeta), elemento (.tarjeta__titulo) y modificador (.tarjeta--destacada). Los nombres cuentan qué es cada cosa y a quién pertenece, y evitan choques entre clases de distintos componentes.",
  k=["BEM significa Bloque, Elemento y Modificador.", "Los elementos se escriben con doble guion bajo.", "Los modificadores se escriben con doble guion medio."],
  sit="Quieres nombrar las clases de un componente para que nunca choquen con otras. ¿Qué convención usas?",
  cod="""<style>
  .tarjeta { border: 2px solid #94a3b8; padding: 12px; width: 220px; }
  .tarjeta__titulo { font-size: 1.2rem; margin: 0 0 6px; }
  .tarjeta--destacada { border-color: gold; background: #fef9c3; }
</style>
<div class="tarjeta tarjeta--destacada"><h3 class="tarjeta__titulo">Oferta</h3>Texto de la tarjeta</div>""",
  h="nombra una tarjeta, su título y una variante destacada con BEM",
  pr=("En BEM, «tarjeta» es el ___. (6 letras)", "bloque"),
  pr2=("En BEM, el modificador se escribe con doble ___. (5 letras)", "guion", "guión"),
  ec="mezclar estilos de nombres sin una convención"),
K("Proyecto landing responsive",
  d="página de presentación completa que se adapta a cualquier pantalla",
  u="practicar todo lo aprendido en un proyecto real",
  mas="Para cerrar CSS, crea una landing page: cabecera con menú flex, portada con degradado, rejilla de tarjetas con auto-fit, variables para los colores y hover con transition. Revísala en móvil, tableta y escritorio con el inspector.",
  k=["Una landing page presenta un producto o servicio en una sola página.", "Un buen proyecto final combina flexbox, grid, variables y responsive.", "Hay que probarla en varios tamaños de pantalla."],
  sit="Quieres cerrar el curso con un proyecto que reúna flexbox, grid, variables y diseño adaptable. ¿Qué construyes?",
  cod="""<style>
  :root { --color: #6366f1; }
  * { box-sizing: border-box; margin: 0; }
  body { font-family: system-ui, sans-serif; }
  nav { display: flex; justify-content: space-between; padding: 12px 20px; background: var(--color); color: white; }
  .portada { background: linear-gradient(135deg, var(--color), #ec4899); color: white; padding: 40px 20px; text-align: center; }
  .rejilla { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; padding: 16px; }
  .tarjeta { background: #eef2ff; padding: 16px; border-radius: 12px; transition: transform .2s; }
  .tarjeta:hover { transform: translateY(-4px); }
</style>
<nav><b>MiMarca</b><span>Menú</span></nav>
<section class="portada"><h1>Aprende CSS</h1><p>Diseño adaptable y moderno</p></section>
<div class="rejilla"><div class="tarjeta">Rápido</div><div class="tarjeta">Fácil</div><div class="tarjeta">Responsive</div></div>""",
  h="une menú flex, portada con degradado y tarjetas adaptables con variables",
  pr=("Una página de presentación de un producto se llama landing ___. (4 letras)", "page"),
  pr2=("Las páginas deben probarse en varios ___ de pantalla. (una palabra)", "tamaños", "tamanos"),
  ec="no probar el proyecto en pantallas pequeñas"),
]
