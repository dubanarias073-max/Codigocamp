"""CSS · Etapa 3: la caja, el espacio y la posición."""
from ..generador import K

LISTA = [
K("Modelo de caja",
  d="idea de que cada elemento es una caja con capas",
  u="entender cuánto espacio ocupa cada elemento",
  mas="Cada elemento es una caja formada, de dentro hacia fuera, por el contenido, el relleno (padding), el borde (border) y el margen (margin). Para calcular el tamaño real de un elemento hay que sumar todas las capas.",
  k=["Una caja se compone de contenido, relleno, borde y margen.", "El padding está dentro del borde y el margin fuera.", "El tamaño total de una caja suma todas sus capas."],
  sit="Quieres entender por qué una caja de 200 px de ancho ocupa más espacio en pantalla. ¿Qué concepto estudias?",
  cod="""<style>
  .caja {
    width: 200px;           /* contenido */
    padding: 20px;          /* relleno */
    border: 5px solid navy; /* borde */
    margin: 30px;           /* margen */
    background: #dbeafe;
  }
</style>
<div class="caja">Caja con todas sus capas</div>""",
  h="muestra una caja con contenido, relleno, borde y margen",
  pr=("De dentro hacia fuera: contenido, relleno, borde y ___. (6 letras)", "margen", "margin"),
  pr2=("El espacio entre el contenido y el borde se llama ___. (7 letras)", "padding", "relleno"),
  ec="olvidar sumar padding y borde al tamaño de la caja"),
K("Margin",
  d="espacio exterior que separa un elemento de los demás",
  u="dejar aire entre elementos",
  mas="margin: 20px da 20 px por los cuatro lados. Con dos valores (10px 20px) el primero es vertical y el segundo horizontal; con cuatro van en el sentido de las agujas del reloj: arriba, derecha, abajo, izquierda. Los márgenes verticales vecinos pueden fusionarse.",
  k=["El margin es el espacio exterior de un elemento.", "Con cuatro valores el orden es arriba, derecha, abajo, izquierda.", "Los márgenes verticales de vecinos pueden fusionarse."],
  sit="Quieres separar una caja de las que tiene a su alrededor. ¿Qué propiedad usas?",
  cod="""<style>
  .a, .b { background: lightblue; }
  /* margin: arriba derecha abajo izquierda */
  .a { margin: 10px 40px 20px 40px; }
  .b { margin: 0 0 0 80px; }
</style>
<div class="a">Caja A</div>
<div class="b">Caja B</div>""",
  h="coloca dos cajas con márgenes distintos en sus cuatro lados",
  pr=("Con cuatro valores el orden del margin es arriba, derecha, abajo y ___. (9 letras)", "izquierda"),
  pr2=("La propiedad del espacio exterior de un elemento es ___. (6 letras)", "margin"),
  ec="confundir el orden de los cuatro valores"),
K("Padding",
  d="espacio interior entre el contenido y el borde",
  u="dar aire dentro de una caja",
  mas="padding funciona como margin pero hacia dentro. El fondo del elemento sí cubre el padding. Un botón sin padding se ve apretado, y por eso casi todos los botones lo llevan.",
  k=["El padding es el espacio interior de un elemento.", "El color de fondo cubre el área del padding.", "Los botones suelen necesitar padding para verse cómodos."],
  sit="Quieres separar el texto de un botón de sus bordes. ¿Qué propiedad usas?",
  cod="""<style>
  .boton { background: seagreen; color: white; border: none; }
  .sin { padding: 0; }
  .con { padding: 12px 28px; }   /* vertical horizontal */
</style>
<button class="boton sin">Sin padding</button>
<button class="boton con">Con padding</button>""",
  h="compara un botón sin relleno con otro cómodo y espacioso",
  pr=("El espacio entre el contenido y el borde es el ___. (7 letras)", "padding"),
  pr2=("El fondo de un elemento ___ cubre el padding. (sí o no)", "sí", "si"),
  ec="usar margin cuando se quería espacio interior"),
K("Border",
  d="línea que rodea al elemento",
  u="enmarcar cajas, tarjetas y campos",
  mas="Se escribe con tres valores: grosor, estilo y color. Ejemplo: border: 2px solid red;. Los estilos más usados son solid, dashed y dotted. También se puede poner solo un lado con border-bottom.",
  k=["La propiedad border lleva grosor, estilo y color.", "Los estilos más usados son solid, dashed y dotted.", "Se puede aplicar un borde a un solo lado."],
  sit="Quieres dibujar una línea discontinua alrededor de una caja. ¿Qué propiedad usas?",
  cod="""<style>
  .a { border: 3px solid crimson; padding: 8px; }
  .b { border: 3px dashed teal; padding: 8px; }
  /* solo el borde inferior */
  .c { border-bottom: 4px dotted orange; padding: 8px; }
</style>
<p class="a">Continuo</p><p class="b">Discontinuo</p><p class="c">Solo abajo</p>""",
  h="muestra bordes continuo, discontinuo y solo inferior",
  pr=("En border: 2px solid red, «solid» es el ___ del borde. (5 letras)", "estilo"),
  pr2=("La propiedad que dibuja solo el borde inferior es border-___. (6 letras)", "bottom"),
  ec="olvidar el estilo y no ver el borde",
  err=("p {\n  border: 3px red;\n  padding: 10px;\n}", 2, "Falta el estilo del borde (solid, dashed...): sin él no se dibuja.")),
K("Border-radius",
  d="propiedad que redondea las esquinas",
  u="suavizar tarjetas y botones o hacer círculos",
  mas="border-radius: 12px redondea las cuatro esquinas. Con 50% en una caja cuadrada se obtiene un círculo. Se pueden dar valores distintos a cada esquina.",
  k=["border-radius redondea las esquinas de un elemento.", "Con 50% una caja cuadrada se vuelve un círculo.", "Cada esquina puede tener un radio distinto."],
  sit="Quieres convertir una caja cuadrada en un círculo. ¿Qué propiedad usas?",
  cod="""<style>
  .tarjeta { border-radius: 16px; background: #fde68a; padding: 16px; width: 160px; }
  /* 50% en un cuadrado = círculo */
  .circulo { width: 100px; height: 100px; background: tomato; border-radius: 50%; }
</style>
<div class="tarjeta">Esquinas suaves</div>
<div class="circulo"></div>""",
  h="redondea una tarjeta y convierte un cuadrado en círculo",
  pr=("Para un círculo, border-radius vale ___%. (un número)", "50"),
  pr2=("La propiedad que redondea esquinas es border-___. (6 letras)", "radius"),
  ec="aplicar 50% a un rectángulo y obtener una elipse sin querer"),
K("Width y height",
  d="propiedades que fijan el ancho y el alto de un elemento",
  u="controlar el tamaño de cajas e imágenes",
  mas="width y height fijan el tamaño del contenido. Si no pones height, la altura se adapta al contenido, lo cual es casi siempre lo mejor. min-width, max-width, min-height y max-height ponen límites.",
  k=["Width fija el ancho y height fija el alto.", "Sin height, la altura se adapta al contenido.", "Las propiedades max-width y min-width ponen límites."],
  sit="Quieres que una caja mida exactamente 300 píxeles de ancho. ¿Qué propiedad usas?",
  cod="""<style>
  .caja { width: 300px; background: #bbf7d0; padding: 10px; }
  /* la altura se adapta al contenido salvo que la fijes */
  .alta { height: 120px; background: #fecaca; }
</style>
<div class="caja">Ancho fijo, alto automático</div>
<div class="caja alta">Con altura fija</div>""",
  h="muestra una caja de ancho fijo y otra con altura fija",
  pr=("La propiedad que fija el ancho es ___. (5 letras)", "width"),
  pr2=("Si no pones height, la altura se adapta al ___. (9 letras)", "contenido"),
  ec="fijar la altura y que el texto se desborde"),
K("Box-sizing",
  d="propiedad que decide cómo se calcula el tamaño de la caja",
  u="evitar que padding y borde agranden la caja",
  mas="Con content-box (valor por defecto), width solo cuenta el contenido y se suma el padding y el borde. Con box-sizing: border-box, width incluye todo y la caja mide justo lo que escribiste. Casi todos los proyectos lo aplican a todos los elementos.",
  k=["Con border-box, el width incluye padding y borde.", "El valor por defecto es content-box.", "Muchos proyectos aplican border-box a todos los elementos."],
  sit="Quieres que una caja de 200 px mida 200 px aunque tenga padding y borde. ¿Qué propiedad usas?",
  cod="""<style>
  .normal { width: 200px; padding: 20px; border: 5px solid black; background: #fef08a; }
  .borde  { width: 200px; padding: 20px; border: 5px solid black; background: #bae6fd;
            box-sizing: border-box; }
</style>
<div class="normal">content-box: mide 250 px</div>
<div class="borde">border-box: mide 200 px</div>""",
  h="compara una caja que crece con el padding y otra que mantiene su ancho",
  pr=("El valor que incluye padding y borde en el width es ___-box. (6 letras)", "border"),
  pr2=("El valor por defecto de box-sizing es ___-box. (7 letras)", "content"),
  ec="olvidar border-box y ver cajas que se salen del contenedor"),
K("Display",
  d="propiedad que decide cómo se comporta un elemento en el flujo",
  u="cambiar un elemento de bloque a línea o viceversa",
  mas="Los elementos block (div, p, h1) ocupan todo el ancho y empiezan en una línea nueva. Los inline (span, a) solo ocupan su contenido y no aceptan width ni height. inline-block mezcla ambos: va en línea pero acepta tamaño.",
  k=["Los elementos block ocupan todo el ancho disponible.", "Los elementos inline no aceptan width ni height.", "inline-block va en línea pero admite tamaño."],
  sit="Quieres que varios divs se coloquen uno al lado del otro con tamaño propio. ¿Qué valor de display usas?",
  cod="""<style>
  .item { display: inline-block; width: 90px; height: 60px; background: coral; margin: 4px; }
  .bloque { display: block; background: lightgreen; }
</style>
<div class="item">1</div><div class="item">2</div><div class="item">3</div>
<span class="bloque">Un span convertido en bloque</span>""",
  h="coloca tres cajas con tamaño una junto a otra y convierte un span en bloque",
  pr=("El valor de display que mezcla línea y tamaño es inline-___. (5 letras)", "block"),
  pr2=("Un div es, por defecto, un elemento de ___. (5 letras)", "bloque", "block"),
  ec="dar width a un elemento inline y no ver el cambio"),
K("Display none",
  d="valor que oculta un elemento y libera su espacio",
  u="esconder contenido sin borrarlo del HTML",
  mas="display: none hace que el elemento desaparezca y no ocupe espacio. Es distinto de visibility: hidden, que lo oculta pero conserva su hueco. Los lectores de pantalla tampoco leen lo que tiene display: none.",
  k=["display: none oculta el elemento y su espacio.", "visibility: hidden oculta pero mantiene el hueco.", "Un elemento con display: none no se lee en lectores de pantalla."],
  sit="Quieres ocultar un aviso por completo para que ni siquiera ocupe espacio. ¿Qué usas?",
  cod="""<style>
  .oculto  { display: none; }            /* desaparece y no ocupa espacio */
  .invisible { visibility: hidden; }     /* desaparece pero deja el hueco */
</style>
<p>Uno</p>
<p class="oculto">Dos (no ocupa espacio)</p>
<p class="invisible">Tres (deja su hueco)</p>
<p>Cuatro</p>""",
  h="oculta un párrafo sin hueco y otro dejando su hueco",
  pr=("El valor de display que oculta un elemento es ___. (4 letras)", "none"),
  pr2=("La propiedad que oculta pero conserva el espacio es ___: hidden. (10 letras)", "visibility"),
  ec="confundir display none con visibility hidden"),
K("Overflow",
  d="propiedad que decide qué pasa con el contenido que no cabe",
  u="controlar los desbordes de texto o imágenes",
  mas="Si el contenido es más grande que la caja, overflow decide: visible (se sale), hidden (se corta), scroll (muestra barras) o auto (barras solo si hace falta). Ocultar sin avisar puede esconder información importante.",
  k=["overflow decide qué pasa si el contenido no cabe.", "overflow: auto añade barras solo cuando hacen falta.", "overflow: hidden corta lo que sobra."],
  sit="Quieres que una caja pequeña muestre barras de desplazamiento si su texto no cabe. ¿Qué propiedad usas?",
  cod="""<style>
  .caja { width: 180px; height: 70px; border: 2px solid gray; }
  .a { overflow: hidden; }   /* corta lo que sobra */
  .b { overflow: auto; }     /* barra si hace falta */
</style>
<div class="caja a">Mucho texto, mucho texto, mucho texto, mucho texto, mucho texto.</div>
<div class="caja b">Mucho texto, mucho texto, mucho texto, mucho texto, mucho texto.</div>""",
  h="corta el texto sobrante en una caja y añade barra en otra",
  pr=("El valor de overflow que añade barra solo si hace falta es ___. (4 letras)", "auto"),
  pr2=("El valor de overflow que corta lo que sobra es ___. (6 letras)", "hidden"),
  ec="ocultar con hidden información que el usuario necesita"),
K("Centrar con margin auto",
  d="técnica de centrar una caja horizontalmente",
  u="colocar una caja en el centro de su contenedor",
  mas="Para centrar un bloque horizontalmente, dale un ancho y pon margin: 0 auto;. Los márgenes automáticos izquierdo y derecho se reparten el espacio sobrante. Funciona en elementos de bloque con width definido.",
  k=["margin: 0 auto centra una caja de bloque horizontalmente.", "La caja necesita un ancho definido para poder centrarse.", "Los márgenes automáticos se reparten el espacio sobrante."],
  sit="Quieres centrar un bloque de 400 px de ancho en medio de la página. ¿Qué técnica usas?",
  cod="""<style>
  .centrada {
    width: 300px;
    margin: 0 auto;     /* arriba/abajo 0; izquierda/derecha automáticos */
    background: #c7d2fe;
    padding: 12px;
    text-align: center;
  }
</style>
<div class="centrada">Estoy centrada</div>""",
  h="centra horizontalmente una caja de 300 píxeles",
  pr=("Para centrar una caja se usa margin: 0 ___. (4 letras)", "auto"),
  pr2=("Para centrar con margin auto, la caja necesita un ___ definido. (5 letras)", "ancho", "width"),
  ec="olvidar el ancho y no ver centrada la caja"),
K("Max-width",
  d="propiedad que limita el ancho máximo",
  u="evitar que el contenido se estire demasiado en pantallas grandes",
  mas="max-width: 700px deja que la caja se encoja en pantallas pequeñas pero nunca supere 700 px. Para textos largos se recomienda un ancho de unos 60 a 75 caracteres por línea. Con imágenes, max-width: 100% evita que se salgan.",
  k=["max-width limita el ancho máximo de un elemento.", "Un texto largo se lee mejor con líneas de ancho limitado.", "Una imagen con max-width: 100% no se sale de su contenedor."],
  sit="Quieres que tu texto no se estire por toda la pantalla en un monitor grande. ¿Qué propiedad usas?",
  cod="""<style>
  .texto {
    max-width: 500px;      /* nunca más ancho que esto */
    margin: 0 auto;
    background: #f1f5f9;
    padding: 12px;
  }
  img { max-width: 100%; }  /* las imágenes nunca se salen */
</style>
<div class="texto">Este texto se estira hasta 500 px y no más, aunque la pantalla sea enorme.</div>""",
  h="limita a 500 píxeles el ancho de un texto y evita que las imágenes se salgan",
  pr=("La propiedad que limita el ancho máximo es ___-width. (3 letras)", "max"),
  pr2=("Con max-width: 100%, la imagen no se ___ de su contenedor. (una palabra)", "sale"),
  ec="usar width fijo y provocar desplazamiento horizontal en móviles"),
K("Position relative",
  d="posición que desplaza un elemento respecto a su sitio original",
  u="mover un elemento un poco y servir de referencia a otros",
  mas="Con position: relative el elemento sigue ocupando su sitio, pero puedes moverlo con top, left, right y bottom. También es la forma de crear un punto de referencia para los hijos con position absolute.",
  k=["position: relative mueve el elemento respecto a su lugar original.", "El hueco original del elemento se conserva.", "Se usa como referencia para hijos con position absolute."],
  sit="Quieres mover un elemento unos píxeles sin sacarlo del flujo de la página. ¿Qué posición usas?",
  cod="""<style>
  .normal  { background: #fecaca; padding: 10px; }
  .movida  { position: relative; top: 15px; left: 40px; background: #bbf7d0; padding: 10px; }
</style>
<div class="normal">Normal</div>
<div class="movida">Relative: movida 15px abajo y 40px a la derecha</div>
<div class="normal">Otra normal (el hueco se conserva)</div>""",
  h="desplaza una caja respecto a su posición original manteniendo su hueco",
  pr=("La posición que desplaza respecto al lugar original es ___. (8 letras)", "relative"),
  pr2=("Con position relative, el hueco original ___ se conserva. (sí o no)", "sí", "si"),
  ec="creer que relative saca al elemento del flujo"),
K("Position absolute",
  d="posición que saca al elemento del flujo y lo coloca con coordenadas",
  u="colocar un elemento en una esquina de su contenedor",
  mas="Un elemento con position: absolute se posiciona con top, left, right y bottom respecto al antecesor más cercano que tenga position distinta de static. Si no hay ninguno, usa la página. Ya no ocupa espacio en el flujo.",
  k=["position: absolute saca al elemento del flujo normal.", "Se coloca respecto al antecesor posicionado más cercano.", "Se usa con top, right, bottom y left."],
  sit="Quieres pegar una etiqueta «Nuevo» en la esquina superior derecha de una tarjeta. ¿Qué posición usas?",
  cod="""<style>
  .tarjeta { position: relative; width: 200px; height: 100px; background: #e0e7ff; }
  /* absolute se coloca respecto a .tarjeta (que es relative) */
  .etiqueta { position: absolute; top: 8px; right: 8px; background: crimson; color: white; padding: 2px 8px; }
</style>
<div class="tarjeta"><span class="etiqueta">Nuevo</span>Producto</div>""",
  h="pega una etiqueta en la esquina superior derecha de una tarjeta",
  pr=("La posición que usa coordenadas respecto a su antecesor es ___. (8 letras)", "absolute"),
  pr2=("El antecesor de referencia debe tener position ___ (o similar). (8 letras)", "relative"),
  ec="olvidar position relative en el contenedor",
  err=("<style>\n  .caja { position: absolute; top: 10px; }\n  .padre { color: red;\n</style>", 3, "Falta cerrar la llave de la regla .padre antes de </style>.")),
K("Position fixed y sticky",
  d="posiciones que fijan elementos en la ventana al desplazarse",
  u="mantener visibles menús y botones mientras se hace scroll",
  mas="Con fixed el elemento queda clavado a la ventana y no se mueve al hacer scroll (por ejemplo un botón de chat). Con sticky se comporta como relativo hasta llegar a cierto punto y entonces se pega. Es ideal para cabeceras de tablas y menús.",
  k=["position: fixed se mantiene fijo en la ventana.", "position: sticky se pega al llegar a un punto del scroll.", "Los menús que acompañan al desplazarse usan sticky o fixed."],
  sit="Quieres que un menú se quede pegado arriba mientras el usuario baja por la página. ¿Qué posición usas?",
  cod="""<style>
  .menu { position: sticky; top: 0; background: navy; color: white; padding: 10px; }
  .chat { position: fixed; bottom: 16px; right: 16px; background: seagreen; color: white; padding: 10px; }
  .relleno { height: 600px; background: #f1f5f9; }
</style>
<div class="menu">Menú pegajoso</div>
<div class="relleno">Haz scroll</div>
<div class="chat">Chat fijo</div>""",
  h="deja un menú pegado arriba y un botón fijo en la esquina al hacer scroll",
  pr=("La posición que se pega al llegar a cierto punto es ___. (6 letras)", "sticky"),
  pr2=("La posición que queda clavada en la ventana es ___. (5 letras)", "fixed"),
  ec="cubrir contenido importante con un elemento fixed"),
K("Z-index",
  d="propiedad que decide qué elemento queda delante",
  u="ordenar elementos que se superponen",
  mas="Cuando dos elementos se solapan, z-index: un número mayor queda por encima. Solo funciona en elementos con position distinta de static. Evita números gigantes: usa una escala sencilla como 10, 20 y 30.",
  k=["Un z-index mayor queda por encima de uno menor.", "El z-index funciona en elementos posicionados.", "Conviene usar una escala sencilla de valores."],
  sit="Dos cajas se solapan y quieres que una quede delante de la otra. ¿Qué propiedad usas?",
  cod="""<style>
  .caja { position: absolute; width: 100px; height: 80px; }
  .roja { background: tomato; top: 20px; left: 20px; z-index: 1; }
  .azul { background: dodgerblue; top: 50px; left: 60px; z-index: 2; }  /* queda encima */
</style>
<div style="position:relative;height:150px">
  <div class="caja roja">1</div><div class="caja azul">2</div>
</div>""",
  h="superpone dos cajas y deja la azul por delante con un z-index mayor",
  pr=("La propiedad que ordena elementos superpuestos es ___-index. (1 letra)", "z"),
  pr2=("Un z-index mayor queda ___ de uno menor. (encima o debajo)", "encima"),
  ec="usar z-index en un elemento sin position"),
K("Box-shadow",
  d="propiedad que dibuja una sombra alrededor de la caja",
  u="dar profundidad a tarjetas y botones",
  mas="Se escribe con desplazamiento horizontal, vertical, desenfoque y color: box-shadow: 0 4px 10px rgba(0,0,0,0.2);. Una sombra suave da sensación de elevación. Con inset la sombra se dibuja por dentro.",
  k=["box-shadow dibuja una sombra alrededor de la caja.", "Sus valores son desplazamiento, desenfoque y color.", "Una sombra suave da sensación de elevación."],
  sit="Quieres que una tarjeta parezca levantada sobre la página con una sombra. ¿Qué propiedad usas?",
  cod="""<style>
  .tarjeta {
    background: white; padding: 20px; width: 200px; border-radius: 12px;
    /* x  y  desenfoque  color */
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }
  body { background: #e2e8f0; }
</style>
<div class="tarjeta">Tarjeta elevada</div>""",
  h="da una sombra suave a una tarjeta blanca sobre un fondo gris",
  pr=("La propiedad de la sombra de una caja es box-___. (6 letras)", "shadow"),
  pr2=("Una sombra con valor inset se dibuja por ___. (6 letras)", "dentro"),
  ec="usar sombras muy oscuras y duras"),
K("Rem y em",
  d="unidades relativas al tamaño de la letra",
  u="crear tamaños que se adaptan al texto del usuario",
  mas="1 em equivale al tamaño de letra del propio elemento (o de su padre) y 1 rem al tamaño de letra de la raíz (html), normalmente 16 px. Los rem son más predecibles porque no se acumulan al anidar. Con rem, el diseño respeta si la persona agranda el texto del navegador.",
  k=["1 rem es el tamaño de letra del elemento raíz.", "Los em dependen del tamaño de letra del elemento o de su padre.", "Los rem no se acumulan al anidar elementos."],
  sit="Quieres un tamaño que crezca si el usuario aumenta el texto del navegador. ¿Qué unidad eliges?",
  cod="""<style>
  html { font-size: 16px; }          /* 1rem = 16px */
  h1 { font-size: 2rem; }            /* 32px */
  p  { font-size: 1rem; margin-bottom: 1.5rem; }
  .caja { padding: 1rem; background: #fef3c7; }
</style>
<h1>Rem en acción</h1>
<p>Texto de tamaño base.</p>
<div class="caja">Relleno de 1rem</div>""",
  h="define tamaños, márgenes y rellenos con la unidad rem",
  pr=("1rem equivale por defecto a ___ píxeles. (un número)", "16"),
  pr2=("La unidad que depende de la raíz html es ___. (3 letras)", "rem"),
  ec="usar em anidados y ver tamaños que se multiplican"),
K("Porcentajes y vw vh",
  d="unidades que dependen del contenedor o de la ventana",
  u="adaptar tamaños al espacio disponible",
  mas="El % se calcula respecto al elemento padre. vw es el 1 % del ancho de la ventana y vh el 1 % de su alto. Así, height: 100vh ocupa toda la altura visible, algo muy útil en pantallas de bienvenida.",
  k=["El % toma como referencia al elemento padre.", "1vw es el 1 % del ancho de la ventana.", "100vh ocupa toda la altura visible de la ventana."],
  sit="Quieres que una sección ocupe toda la altura de la ventana del navegador. ¿Qué unidad usas?",
  cod="""<style>
  .mitad { width: 50%; background: lightblue; }
  .portada { height: 60vh; background: #fde68a; display: grid; place-items: center; }
</style>
<div class="mitad">50% del padre</div>
<div class="portada">Ocupo el 60% de la altura de la ventana</div>""",
  h="ocupa la mitad del ancho del padre y el 60 % de la altura de la ventana",
  pr=("La unidad del 1 % del alto de la ventana es ___. (2 letras)", "vh"),
  pr2=("El % se calcula respecto al elemento ___. (4 letras)", "padre"),
  ec="usar 100vw y provocar una barra de desplazamiento horizontal"),
K("Imagen de fondo",
  d="propiedades para poner una imagen detrás del contenido",
  u="crear portadas y fondos decorativos",
  mas="background-image: url(...) coloca la imagen. background-size: cover la escala para cubrir todo el espacio y background-position la centra. background-repeat: no-repeat evita que se repita en mosaico. El contenido importante no debería depender solo de la imagen.",
  k=["background-image coloca una imagen de fondo.", "background-size: cover cubre todo el espacio.", "background-repeat: no-repeat evita el mosaico."],
  sit="Quieres que una foto cubra todo el fondo de una cabecera. ¿Qué propiedades usas?",
  cod="""<style>
  .portada {
    height: 160px;
    background-image: linear-gradient(135deg, #38bdf8, #6366f1); /* o url("foto.jpg") */
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    color: white; display: grid; place-items: center; font-size: 1.5rem;
  }
</style>
<div class="portada">Texto sobre la imagen de fondo</div>""",
  h="cubre una cabecera con una imagen de fondo bien ajustada y centrada",
  pr=("El valor de background-size que cubre todo el espacio es ___. (5 letras)", "cover"),
  pr2=("Para evitar el mosaico, background-repeat vale ___. (9 letras con guion)", "no-repeat"),
  ec="poner texto claro sobre una imagen clara"),
]
