"""CSS · Etapa 1: qué es CSS (casi todo teoría)."""
from ..generador import K

LISTA = [
K("Qué es CSS",
  d="lenguaje que da estilo y aspecto a las páginas web",
  u="cambiar colores, tamaños y posición de lo escrito en HTML",
  mas="CSS significa Cascading Style Sheets (hojas de estilo en cascada). HTML dice qué hay en la página y CSS dice cómo se ve. Con unas pocas líneas puedes cambiar toda la apariencia de un sitio.",
  k=["CSS da estilo a las páginas web.", "CSS significa Cascading Style Sheets.", "HTML dice qué hay y CSS dice cómo se ve."],
  sit="Quieres cambiar el color y el tamaño de los textos de tu página sin tocar su contenido. ¿Qué lenguaje usas?",
  cod="""<style>
  /* CSS: cómo se ve */
  h1 { color: tomato; }
</style>
<!-- HTML: qué hay -->
<h1>Hola, CSS</h1>""",
  h="pinta de rojo un título que escribió HTML",
  pr=("CSS significa Cascading Style ___. (una palabra)", "sheets"),
  pr2=("El lenguaje que dice cómo se ve una página es ___. (3 letras)", "css"),
  ec="intentar dar color a la página usando solo HTML"),
K("Separar estructura y estilo",
  d="idea de escribir el contenido en HTML y el aspecto en CSS",
  u="cambiar el diseño sin reescribir el contenido",
  mas="Si el color de los títulos está escrito en cada etiqueta, cambiarlo exige tocar cientos de líneas. Con CSS cambias una sola regla y toda la web se actualiza. Es la razón de ser de las hojas de estilo.",
  k=["Separar contenido y estilo permite cambiar el diseño en un solo lugar.", "El contenido vive en HTML y el aspecto en CSS.", "Una regla CSS puede afectar a cientos de elementos."],
  sit="Quieres cambiar el color de todos los títulos del sitio modificando un solo sitio. ¿Qué principio aplicas?",
  cod="""<style>
  /* Una regla cambia TODOS los títulos de la página */
  h2 { color: seagreen; }
</style>
<h2>Primer título</h2>
<h2>Segundo título</h2>
<h2>Tercer título</h2>""",
  h="cambia el color de tres títulos con una sola regla",
  pr=("El contenido se escribe en HTML y el aspecto en ___. (3 letras)", "css"),
  pr2=("Con CSS, una sola regla puede cambiar ___ elementos. (una palabra: pocos o muchos)", "muchos"),
  ec="escribir el estilo repetido en cada etiqueta"),
K("CSS en línea",
  d="estilo escrito con el atributo style en una etiqueta",
  u="dar un estilo rápido a un único elemento",
  mas="Se escribe así: <p style=\"color: red;\">. Es rápido, pero mezcla estructura y estilo y no se puede reutilizar. Úsalo solo para pruebas o casos muy puntuales.",
  k=["El CSS en línea se escribe en el atributo style.", "El CSS en línea afecta solo a ese elemento.", "El CSS en línea mezcla estructura y estilo."],
  sit="Quieres probar un color rápido en un único párrafo escribiéndolo dentro de su etiqueta. ¿Qué usas?",
  cod="""<!-- style en la propia etiqueta: afecta solo a este párrafo -->
<p style="color: crimson; font-size: 22px;">Texto con CSS en línea</p>
<p>Este párrafo no cambia.</p>""",
  h="da estilo solo al primer párrafo desde su propia etiqueta",
  pr=("El CSS en línea se escribe en el atributo ___. (5 letras)", "style"),
  pr2=("El CSS en línea afecta solo a ese ___. (una palabra)", "elemento"),
  ec="usar CSS en línea para todo el sitio"),
K("CSS interno",
  d="estilos escritos en una etiqueta style dentro de la página",
  u="dar estilos a una sola página sin archivos extra",
  mas="Se escribe una etiqueta <style> en el head con reglas dentro. Sirve para toda esa página, pero no se comparte con otras. Es cómodo para pruebas y ejemplos, como los de CódigoCamp.",
  k=["El CSS interno va dentro de una etiqueta style.", "El CSS interno afecta a toda esa página.", "El CSS interno no se comparte entre páginas distintas."],
  sit="Quieres dar estilo a toda una página desde el mismo archivo HTML. ¿Qué usas?",
  cod="""<head>
  <!-- style en el head: afecta a toda esta página -->
  <style>
    p { color: navy; }
  </style>
</head>
<body><p>Uno</p><p>Dos</p></body>""",
  h="pinta de azul todos los párrafos de la página con una etiqueta style",
  pr=("El CSS interno se escribe dentro de la etiqueta ___. (5 letras)", "style", "<style>"),
  pr2=("El CSS interno suele escribirse dentro del ___. (4 letras)", "head"),
  ec="repetir el mismo bloque style en cada página"),
K("CSS externo",
  d="estilos guardados en un archivo .css aparte",
  u="compartir los mismos estilos entre muchas páginas",
  mas="Los estilos se guardan en un archivo como estilos.css y se enlazan en el head con <link rel=\"stylesheet\" href=\"estilos.css\">. Es la forma recomendada, porque todas las páginas comparten el mismo archivo y se mantiene limpio.",
  k=["El CSS externo se guarda en un archivo con extensión .css.", "Se conecta con link rel=\"stylesheet\" en el head.", "Es la forma recomendada de aplicar estilos."],
  sit="Quieres que cinco páginas compartan los mismos estilos desde un único archivo. ¿Qué usas?",
  cod="""<head>
  <!-- conecta el archivo estilos.css con esta página -->
  <link rel="stylesheet" href="estilos.css">
</head>
<!-- Dentro de estilos.css habría reglas como:  p { color: teal; } -->""",
  h="conecta un archivo externo de estilos desde el head",
  pr=("Un archivo de estilos termina en ___. (4 caracteres)", ".css", "css"),
  pr2=("El archivo CSS se conecta con la etiqueta ___. (4 letras)", "link", "<link>"),
  ec="olvidar la ruta correcta del archivo .css",
  err=("<head>\n  <style rel=\"stylesheet\" href=\"estilos.css\">\n</head>", 2, "Para enlazar un archivo externo se usa la etiqueta link, no style.")),
K("Regla CSS",
  d="bloque completo con un selector y sus declaraciones",
  u="decir qué elementos cambian y cómo",
  mas="Una regla se escribe así: selector { propiedad: valor; }. El selector elige a qué elementos se aplica y entre llaves van las declaraciones. Un archivo CSS es simplemente una lista de reglas.",
  k=["Una regla CSS tiene un selector y llaves con declaraciones.", "Las declaraciones van entre llaves { }.", "Un archivo CSS es una lista de reglas."],
  sit="Escribes «p { color: red; }». ¿Cómo se llama todo ese bloque?",
  cod="""<style>
  /* selector { declaraciones } = una regla */
  p {
    color: purple;
    font-size: 20px;
  }
</style>
<p>Mira cómo cambia</p>""",
  h="define una regla que pinta de morado un párrafo y agranda su letra",
  pr=("Las declaraciones de una regla se escriben entre ___. (llaves, con { })", "{}", "llaves"),
  pr2=("Una regla CSS empieza con un ___. (una palabra)", "selector"),
  ec="olvidar cerrar la llave de la regla",
  err=("p {\n  color: red;\n\nh1 {\n  color: blue;\n}", 3, "Falta cerrar la llave de la regla de p antes de empezar la siguiente.")),
K("Selector",
  d="parte de la regla que elige a qué elementos se aplica",
  u="escoger los elementos que van a cambiar",
  mas="El selector más sencillo es el nombre de una etiqueta (p, h1). También hay selectores de clase (.aviso) y de id (#menu). Un selector puede elegir uno o muchos elementos a la vez.",
  k=["El selector elige los elementos que reciben el estilo.", "Un selector puede ser el nombre de una etiqueta.", "Un selector puede elegir muchos elementos a la vez."],
  sit="Quieres elegir todos los títulos h2 para darles estilo. ¿Qué parte de la regla escribes?",
  cod="""<style>
  /* h2 es el selector: elige todos los h2 */
  h2 { color: darkorange; }
</style>
<h2>Uno</h2>
<h2>Dos</h2>
<p>Este no cambia</p>""",
  h="elige todos los h2 para pintarlos, dejando el p sin cambios",
  pr=("En la regla «h2 { color: red; }», h2 es el ___. (8 letras)", "selector"),
  pr2=("Un selector puede elegir uno o ___ elementos. (una palabra)", "muchos", "varios"),
  ec="escribir mal el nombre de la etiqueta del selector"),
K("Propiedad y valor",
  d="par que dice qué se cambia y a qué",
  u="definir cada detalle del estilo de un elemento",
  mas="La propiedad es lo que cambias (color, font-size) y el valor es el nuevo ajuste (red, 20px). Se escriben separados por dos puntos, y la declaración termina con punto y coma.",
  k=["La propiedad indica qué característica se cambia.", "El valor indica cómo queda esa característica.", "Propiedad y valor se separan con dos puntos."],
  sit="En «color: red», quieres nombrar la parte «red». ¿Cómo se llama?",
  cod="""<style>
  p {
    /* propiedad: valor; */
    color: seagreen;
    font-size: 24px;
  }
</style>
<p>Propiedad y valor en acción</p>""",
  h="cambia dos propiedades del párrafo con sus valores",
  pr=("En «color: red;», «red» es el ___. (5 letras)", "valor"),
  pr2=("Propiedad y valor se separan con ___. (dos puntos, con :)", ":", "dos puntos"),
  ec="olvidar los dos puntos entre propiedad y valor",
  err=("p {\n  color red;\n  font-size: 20px;\n}", 2, "Falta el signo : entre la propiedad color y el valor red.")),
K("Declaración",
  d="una propiedad con su valor terminada en punto y coma",
  u="añadir un ajuste de estilo concreto",
  mas="Cada declaración termina en punto y coma. Puedes escribir las que quieras dentro de una regla, una por línea. Olvidar el punto y coma es de los errores más comunes: rompe esa línea y la siguiente.",
  k=["Una declaración termina con punto y coma.", "Una regla puede contener muchas declaraciones.", "Olvidar el punto y coma rompe la declaración siguiente."],
  sit="Quieres añadir un ajuste más, como el tamaño de la letra, dentro de una regla ya escrita. ¿Qué agregas?",
  cod="""<style>
  h1 {
    color: royalblue;       /* 1.ª declaración */
    text-align: center;     /* 2.ª declaración */
    font-size: 40px;        /* 3.ª declaración */
  }
</style>
<h1>Tres declaraciones</h1>""",
  h="aplica tres declaraciones seguidas al título",
  pr=("Cada declaración termina con ___. (punto y coma)", ";", "punto y coma"),
  pr2=("Una regla puede tener ___ declaraciones. (una palabra: pocas o muchas)", "muchas", "varias"),
  ec="olvidar el punto y coma al final de la línea",
  err=("p {\n  color: red\n  font-size: 20px;\n}", 2, "Falta el punto y coma al final de color: red.")),
K("Comentarios CSS",
  d="notas entre /* y */ que el navegador ignora",
  u="explicar o desactivar partes del CSS",
  mas="Un comentario CSS empieza con /* y termina con */, y puede ocupar varias líneas. Es distinto del comentario de HTML (<!-- -->). Sirve para explicar reglas o para desactivar temporalmente una línea al probar.",
  k=["Los comentarios CSS empiezan con /* y terminan con */.", "El navegador ignora los comentarios CSS.", "Los comentarios CSS no son iguales a los de HTML."],
  sit="Quieres dejar una nota en tu hoja de estilos que el navegador ignore. ¿Qué escribes?",
  cod="""<style>
  /* Este comentario explica la regla de abajo */
  p { color: teal; }
  /* font-size: 40px;  <- línea desactivada por ahora */
</style>
<p>Los comentarios no se ven</p>""",
  h="deja una nota y una línea desactivada que el navegador ignora",
  pr=("Un comentario CSS termina con ___. (2 caracteres)", "*/"),
  pr2=("Un comentario CSS empieza con ___. (2 caracteres)", "/*"),
  ec="usar <!-- --> para comentar dentro del CSS"),
K("Cascada",
  d="regla que decide cuál estilo gana cuando hay varios",
  u="resolver contradicciones entre reglas",
  mas="Si dos reglas dan colores distintos al mismo elemento, gana la más específica, y si tienen igual fuerza, gana la que se escribió después. Por eso la C de CSS es de «cascading»: los estilos caen en orden.",
  k=["Si hay empate de fuerza, gana la regla escrita al final.", "La cascada decide qué regla se aplica en un conflicto.", "El orden de las reglas importa en CSS."],
  sit="Dos reglas con la misma fuerza dan colores distintos al mismo párrafo. ¿Qué mecanismo decide cuál gana?",
  cod="""<style>
  p { color: red; }
  /* Se escribe después con igual fuerza: gana la última */
  p { color: blue; }
</style>
<p>¿De qué color me ves?</p>""",
  h="muestra que la última de dos reglas iguales es la que se aplica",
  pr=("Con igual fuerza, gana la regla escrita al ___. (5 letras: final o inicio)", "final"),
  pr2=("El mecanismo que decide qué estilo gana se llama ___. (7 letras)", "cascada"),
  ec="cambiar una regla y no ver efecto porque otra posterior la anula"),
K("Herencia",
  d="mecanismo por el que los hijos reciben estilos del padre",
  u="aplicar un estilo a muchos elementos desde el contenedor",
  mas="Algunas propiedades, como color o font-family, pasan de un elemento a sus hijos. Si pones color en body, casi todo el texto lo tomará. Otras propiedades, como borde o margen, no se heredan.",
  k=["Los elementos hijos heredan algunas propiedades del padre.", "El color y la fuente se heredan.", "Los bordes y márgenes no se heredan."],
  sit="Quieres que el color puesto en el body llegue a todos los textos de la página sin repetirlo. ¿Qué aprovechas?",
  cod="""<style>
  /* color se hereda: lo reciben los hijos del div */
  div { color: darkgreen; border: 2px solid darkgreen; }
</style>
<div>
  Texto del padre
  <p>Texto del hijo (hereda el color, pero no el borde)</p>
</div>""",
  h="muestra que el hijo hereda el color pero no el borde",
  pr=("El color de texto se ___ de padres a hijos. (una palabra)", "hereda"),
  pr2=("El borde de un elemento ___ se hereda. (no)", "no"),
  ec="esperar que el borde del padre pase a los hijos"),
K("Especificidad",
  d="peso que tiene cada selector al competir",
  u="saber qué regla se impone cuando hay conflicto",
  mas="Un selector de id pesa más que uno de clase, y uno de clase pesa más que uno de etiqueta: #menu gana a .menu y este gana a div. El estilo en línea pesa aún más. Entenderlo evita tener que usar !important.",
  k=["Un selector de id tiene más peso que uno de clase.", "Un selector de clase tiene más peso que uno de etiqueta.", "El estilo en línea pesa más que los selectores."],
  sit="Una regla de clase y otra de etiqueta chocan sobre el color de un mismo elemento. ¿Qué concepto decide cuál gana?",
  cod="""<style>
  p { color: red; }          /* etiqueta: peso bajo */
  .aviso { color: green; }   /* clase: peso medio */
</style>
<!-- gana .aviso aunque p esté escrita antes -->
<p class="aviso">Este texto es verde</p>""",
  h="demuestra que la regla de clase gana a la de etiqueta",
  pr=("Pesa más un selector de ___ que uno de clase. (2 letras)", "id"),
  pr2=("Pesa más una clase que una ___. (una palabra)", "etiqueta"),
  ec="usar !important para resolver cualquier conflicto"),
K("Estilos por defecto",
  d="aspecto que el navegador da a las etiquetas sin CSS",
  u="entender por qué una página sin CSS ya tiene formato",
  mas="El navegador tiene su propia hoja de estilos: los h1 salen grandes y en negrita, los enlaces azules y subrayados. Tus reglas sobrescriben estos valores. Algunos desarrolladores usan un «reset» para empezar desde cero.",
  k=["Cada navegador aplica estilos por defecto a las etiquetas.", "Tus reglas sobrescriben los estilos por defecto.", "Un reset parte de cero para evitar diferencias entre navegadores."],
  sit="Notas que un título sin CSS ya sale grande y en negrita. ¿De dónde viene ese aspecto?",
  cod="""<style>
  /* Sin esta regla el enlace sería azul y subrayado por defecto */
  a { color: inherit; text-decoration: none; }
</style>
<h1>Un h1 ya sale grande por defecto</h1>
<a href="#">Enlace sin su estilo original</a>""",
  h="quita el color y el subrayado que el navegador pone por defecto a los enlaces",
  pr=("Un enlace sin CSS se ve ___ y subrayado. (una palabra: color)", "azul"),
  pr2=("Empezar con todos los estilos en cero se llama hacer un ___. (5 letras)", "reset"),
  ec="creer que la página sin CSS no tiene ningún estilo"),
K("Estilos con el inspector",
  d="panel del navegador que muestra y edita el CSS de un elemento",
  u="probar y entender estilos en una página en vivo",
  mas="Con clic derecho e Inspeccionar ves qué reglas afectan a un elemento, cuáles se tacharon por perder en la cascada y puedes cambiar valores al instante. Los cambios son temporales: al recargar desaparecen.",
  k=["El inspector muestra las reglas CSS de cada elemento.", "Las reglas que pierden en la cascada aparecen tachadas.", "Los cambios hechos en el inspector son temporales."],
  sit="Quieres ver por qué un párrafo no cambia de color y probar valores sin guardar nada. ¿Qué abres?",
  cod="""<style>
  /* Abre el inspector (F12) sobre este texto y cambia el color */
  p { color: slateblue; font-size: 24px; }
</style>
<p>Inspecciona este párrafo con F12</p>""",
  h="deja un párrafo para practicar con el inspector y cambiar sus estilos",
  pr=("El inspector se abre con la tecla ___. (3 caracteres)", "f12"),
  pr2=("Una regla que pierde en la cascada aparece ___ en el inspector. (una palabra)", "tachada"),
  ec="creer que los cambios del inspector se guardan"),
K("Unidades de medida",
  d="tipos de medida usados en CSS para tamaños",
  u="elegir tamaños fijos o flexibles",
  mas="px es un tamaño fijo en píxeles. % depende del elemento padre, em y rem dependen del tamaño de la letra, y vw y vh dependen del tamaño de la ventana. Cada una sirve para algo distinto; las irás usando en las siguientes etapas.",
  k=["El px es una unidad fija en píxeles.", "El % depende del tamaño del elemento padre.", "Las unidades vw y vh dependen del tamaño de la ventana."],
  sit="Quieres que un tamaño dependa de la ventana del navegador y no sea fijo. ¿Qué tipo de unidades usas?",
  cod="""<style>
  /* px: fijo   %: depende del padre   vw: ancho de la ventana */
  .a { width: 200px; background: lightblue; }
  .b { width: 50%;   background: lightgreen; }
  .c { width: 30vw;  background: khaki; }
</style>
<div class="a">px</div><div class="b">%</div><div class="c">vw</div>""",
  h="compara tres cajas con unidades fija, relativa al padre y relativa a la ventana",
  pr=("La unidad que depende del ancho de la ventana se escribe ___. (2 letras)", "vw"),
  pr2=("La unidad fija en píxeles se escribe ___. (2 letras)", "px"),
  ec="usar solo px para todo y perder flexibilidad"),
K("Colores en CSS",
  d="formas de escribir un color: nombre, hexadecimal, rgb y hsl",
  u="dar a cada elemento el color exacto que quieres",
  mas="Hay nombres como tomato, códigos hexadecimales como #ff6347, rgb(255, 99, 71) y hsl(9, 100%, 64%). Todas representan colores; el hexadecimal es el más habitual en diseño.",
  k=["Un color puede escribirse como nombre, hexadecimal, rgb o hsl.", "Un color hexadecimal empieza con #.", "Hay unos 140 colores con nombre en CSS."],
  sit="Un diseñador te da un código de color como #ff6347. ¿Qué formato es?",
  cod="""<style>
  /* Los cuatro dan casi el mismo tono */
  .a { background: tomato; }
  .b { background: #ff6347; }
  .c { background: rgb(255, 99, 71); }
  .d { background: hsl(9, 100%, 64%); }
</style>
<p class="a">nombre</p><p class="b">hex</p><p class="c">rgb</p><p class="d">hsl</p>""",
  h="pinta cuatro párrafos con el mismo color escrito de cuatro maneras",
  pr=("Un color hexadecimal empieza con el símbolo ___. (un carácter)", "#"),
  pr2=("«tomato» y «blue» son colores escritos como ___. (una palabra)", "nombre", "nombres"),
  ec="olvidar el # de un color hexadecimal",
  err=("p {\n  color: ff6347;\n  font-size: 18px;\n}", 2, "Un color hexadecimal debe empezar con #: #ff6347.")),
K("Compatibilidad",
  d="comprobar si un navegador admite una función de CSS",
  u="evitar que una propiedad nueva falle en algunos usuarios",
  mas="No todos los navegadores admiten al mismo tiempo las propiedades más nuevas. El sitio caniuse.com muestra qué navegadores soportan cada función. Si el navegador no entiende una propiedad, simplemente la ignora y sigue con la siguiente.",
  k=["Un navegador ignora las propiedades CSS que no entiende.", "El sitio caniuse.com muestra la compatibilidad de cada función.", "Conviene probar el CSS en más de un navegador."],
  sit="Quieres saber si una propiedad nueva funciona en Safari antes de usarla. ¿Qué consultas?",
  cod="""<style>
  /* Primero un valor que todos entienden; después el moderno */
  .caja {
    background: gray;
    background: linear-gradient(red, orange);
  }
</style>
<div class="caja" style="height:60px">Respaldo para navegadores antiguos</div>""",
  h="deja un color de respaldo antes de un degradado moderno",
  pr=("El sitio para comprobar la compatibilidad de CSS se llama can I ___. (3 letras)", "use"),
  pr2=("Si un navegador no entiende una propiedad, la ___. (una palabra)", "ignora"),
  ec="usar una función nueva sin comprobar si funciona en todos"),
K("Nombres de clases",
  d="forma ordenada de nombrar las clases de CSS",
  u="escribir clases que se entiendan y se puedan reutilizar",
  mas="Usa minúsculas, guiones y nombres que describan función, no aspecto: .boton-principal en lugar de .azul-grande. Así, si el botón cambia de azul a verde, el nombre sigue teniendo sentido.",
  k=["Los nombres de clase se escriben en minúsculas con guiones.", "Un buen nombre describe la función, no el color.", "Evita espacios y tildes en los nombres de clase."],
  sit="Quieres un nombre de clase que siga valiendo aunque cambie el color del botón. ¿Qué cuidas?",
  cod="""<style>
  /* Mal: describe el aspecto */
  .azul-grande { background: dodgerblue; }
  /* Bien: describe la función */
  .boton-principal { background: dodgerblue; color: white; padding: 8px 16px; }
</style>
<button class="boton-principal">Comprar</button>""",
  h="compara un nombre de clase por aspecto con otro por función",
  pr=("Una clase se escribe en el CSS con un ___ delante. (punto)", ".", "punto"),
  pr2=("En los nombres de clase, las palabras se separan con ___. (guion)", "-", "guion", "guiones"),
  ec="nombrar una clase por su color y luego cambiar el color"),
K("Cómo practicar CSS",
  d="costumbre de experimentar con estilos cambiando valores",
  u="entender CSS probando y viendo el resultado al instante",
  mas="CSS se aprende cambiando valores y viendo qué pasa. Prueba un color, un tamaño, rompe algo a propósito. Reproduce diseños de sitios que te gusten e inspecciónalos. Diez minutos al día valen más que una tarde entera.",
  k=["CSS se aprende cambiando valores y observando el resultado.", "Reproducir diseños que te gustan es una gran práctica.", "Practicar poco cada día es mejor que mucho de golpe."],
  sit="Quieres aprender CSS de forma rápida y sin frustrarte. ¿Qué haces?",
  cod="""<style>
  /* Reto: cambia los colores, el tamaño y el borde, y mira qué pasa */
  .tarjeta {
    background: #fef3c7;
    border: 3px dashed #f59e0b;
    padding: 16px;
    border-radius: 12px;
  }
</style>
<div class="tarjeta">Mi primera tarjeta con estilo propio</div>""",
  h="ofrece una tarjeta para practicar cambiando colores, borde y esquinas",
  pr=("CSS se aprende cambiando ___ y mirando el resultado. (una palabra)", "valores"),
  pr2=("Practicar cada ___ es mejor que estudiar de golpe. (una palabra)", "día", "dia"),
  ec="leer sobre CSS sin escribir nunca estilos"),
]
