"""CSS · Etapa 4: Flexbox y Grid."""
from ..generador import K

LISTA = [
K("Flexbox",
  d="sistema de CSS para alinear elementos en una fila o columna",
  u="ordenar elementos en una dimensión con facilidad",
  mas="Pones display: flex en el contenedor y sus hijos directos pasan a ser elementos flexibles. Se colocan en fila, se reparten el espacio y se alinean con pocas propiedades. Es la herramienta ideal para menús, barras y tarjetas en línea.",
  k=["Flexbox se activa con display: flex en el contenedor.", "Los hijos directos del contenedor se vuelven elementos flexibles.", "Flexbox organiza los elementos en una sola dimensión."],
  sit="Quieres colocar tres cajas en fila de forma sencilla. ¿Qué sistema de CSS usas?",
  cod="""<style>
  .fila { display: flex; gap: 10px; }      /* contenedor flex */
  .fila div { background: #a5b4fc; padding: 20px; }
</style>
<div class="fila"><div>1</div><div>2</div><div>3</div></div>""",
  h="coloca tres cajas en una fila usando un contenedor flexible",
  pr=("Flexbox se activa con display: ___. (4 letras)", "flex"),
  pr2=("Los elementos flexibles son los ___ directos del contenedor. (5 letras)", "hijos"),
  ec="aplicar display flex a los hijos en vez de al contenedor",
  err=("<style>\n  .caja { background: pink; }\n  .caja div { display: flex; }\n</style>", 3, "display: flex debe ir en el contenedor (.caja), no en sus hijos.")),
K("Flex-direction",
  d="propiedad que define si los elementos van en fila o en columna",
  u="cambiar la dirección principal del contenedor flex",
  mas="row (por defecto) coloca en fila de izquierda a derecha, column los apila de arriba a abajo, y row-reverse y column-reverse invierten el orden. Al cambiarla, el eje principal y el secundario se intercambian.",
  k=["flex-direction: column apila los elementos de arriba a abajo.", "El valor por defecto es row.", "Cambiar la dirección intercambia los ejes principal y secundario."],
  sit="Quieres que los elementos de un contenedor flex se apilen uno debajo de otro. ¿Qué propiedad usas?",
  cod="""<style>
  .columna { display: flex; flex-direction: column; gap: 8px; width: 160px; }
  .columna div { background: #fda4af; padding: 12px; }
</style>
<div class="columna"><div>Arriba</div><div>Medio</div><div>Abajo</div></div>""",
  h="apila tres cajas verticalmente cambiando la dirección del contenedor",
  pr=("El valor de flex-direction que apila elementos es ___. (6 letras)", "column"),
  pr2=("El valor por defecto de flex-direction es ___. (3 letras)", "row"),
  ec="olvidar que al cambiar la dirección cambian los ejes"),
K("Justify-content",
  d="propiedad que reparte los elementos en el eje principal",
  u="alinear o distribuir elementos a lo largo de la fila",
  mas="Valores habituales: flex-start (al inicio), center (al centro), flex-end (al final), space-between (espacio entre ellos) y space-around o space-evenly. Con filas, actúa en horizontal; con columnas, en vertical.",
  k=["justify-content actúa sobre el eje principal.", "space-between reparte el espacio sobrante entre los elementos.", "center agrupa los elementos en el centro del eje."],
  sit="Quieres separar al máximo tres botones dentro de una barra, con el primero a la izquierda y el último a la derecha. ¿Qué valor usas?",
  cod="""<style>
  .barra { display: flex; justify-content: space-between; background: #e2e8f0; padding: 8px; }
  .barra span { background: #6366f1; color: white; padding: 6px 12px; }
</style>
<div class="barra"><span>Izq</span><span>Centro</span><span>Der</span></div>""",
  h="reparte tres elementos de lado a lado con espacio entre ellos",
  pr=("El valor que reparte espacio entre los elementos es space-___. (7 letras)", "between"),
  pr2=("justify-content actúa sobre el eje ___. (9 letras)", "principal"),
  ec="usar justify-content esperando que alinee en vertical con filas"),
K("Align-items",
  d="propiedad que alinea los elementos en el eje secundario",
  u="centrar o estirar elementos en vertical dentro de una fila",
  mas="En una fila, align-items controla la alineación vertical: flex-start, center, flex-end, stretch (por defecto, estira) o baseline. Si el contenedor tiene altura, align-items: center centra los hijos verticalmente.",
  k=["align-items actúa sobre el eje secundario.", "El valor por defecto es stretch.", "align-items: center centra los elementos en el eje secundario."],
  sit="Quieres centrar verticalmente los elementos de una fila con altura fija. ¿Qué propiedad usas?",
  cod="""<style>
  .fila { display: flex; align-items: center; height: 120px; background: #fef9c3; gap: 8px; }
  .fila div { background: #f59e0b; padding: 10px; }
  .alto { height: 70px; }
</style>
<div class="fila"><div>Bajo</div><div class="alto">Alto</div><div>Bajo</div></div>""",
  h="centra verticalmente cajas de distinta altura dentro de una fila",
  pr=("La propiedad que alinea en el eje secundario es align-___. (5 letras)", "items"),
  pr2=("El valor por defecto de align-items es ___. (7 letras)", "stretch"),
  ec="confundir justify-content con align-items"),
K("Flex-wrap",
  d="propiedad que permite pasar a otra línea cuando no caben",
  u="evitar que los elementos se aprieten o se salgan",
  mas="Por defecto, flex-wrap vale nowrap y todos los elementos intentan caber en una línea, encogiéndose. Con flex-wrap: wrap, los que no caben saltan a la línea siguiente. Es clave para tarjetas que se adaptan al ancho.",
  k=["flex-wrap: wrap permite que los elementos pasen a otra línea.", "El valor por defecto es nowrap.", "Con wrap, los elementos no se encogen hasta el límite."],
  sit="Quieres que las tarjetas que no caben en una fila pasen a la siguiente línea. ¿Qué propiedad usas?",
  cod="""<style>
  .lista { display: flex; flex-wrap: wrap; gap: 10px; width: 330px; }
  .lista div { width: 100px; padding: 16px; background: #86efac; }
</style>
<div class="lista"><div>1</div><div>2</div><div>3</div><div>4</div><div>5</div></div>""",
  h="deja que cinco tarjetas pasen a una segunda línea cuando no caben",
  pr=("El valor de flex-wrap que permite varias líneas es ___. (4 letras)", "wrap"),
  pr2=("El valor por defecto de flex-wrap es ___. (6 letras)", "nowrap"),
  ec="olvidar wrap y ver elementos aplastados"),
K("Gap",
  d="propiedad que añade espacio entre elementos flex o grid",
  u="separar elementos sin usar márgenes",
  mas="gap: 16px separa todos los hijos entre sí, sin añadir espacio en los bordes del contenedor. Existe row-gap y column-gap para controlar cada dirección. Es más limpio que poner margin a cada elemento.",
  k=["gap añade espacio entre los elementos hijos.", "gap no añade espacio en los bordes del contenedor.", "Existen row-gap y column-gap para cada dirección."],
  sit="Quieres separar los elementos de un contenedor sin añadir márgenes a cada uno. ¿Qué propiedad usas?",
  cod="""<style>
  .fila { display: flex; gap: 24px; }           /* espacio entre elementos */
  .fila div { background: #7dd3fc; padding: 14px; }
</style>
<div class="fila"><div>A</div><div>B</div><div>C</div></div>""",
  h="separa tres cajas con 24 píxeles de espacio entre ellas",
  pr=("La propiedad que añade espacio entre hijos de flex o grid es ___. (3 letras)", "gap"),
  pr2=("La propiedad del espacio entre columnas es ___-gap. (6 letras)", "column"),
  ec="usar margin en cada hijo cuando bastaba con gap"),
K("Flex-grow",
  d="propiedad que permite a un elemento ocupar el espacio libre",
  u="hacer que un elemento se estire y llene lo que sobra",
  mas="flex-grow: 1 reparte el espacio sobrante entre los elementos que lo tengan. Si uno tiene 2 y otro 1, el primero recibe el doble. Un campo de búsqueda con flex-grow: 1 ocupa todo lo que deja libre el botón.",
  k=["flex-grow reparte el espacio libre entre los elementos.", "Un elemento con valor 2 recibe el doble que otro con valor 1.", "Por defecto flex-grow vale 0."],
  sit="Quieres que un campo de búsqueda ocupe todo el espacio que sobra junto a un botón. ¿Qué propiedad usas?",
  cod="""<style>
  .buscador { display: flex; gap: 8px; }
  .buscador input { flex-grow: 1; padding: 8px; }   /* ocupa el espacio libre */
</style>
<div class="buscador"><input placeholder="Buscar..."><button>Ir</button></div>""",
  h="estira el campo de búsqueda para llenar el espacio junto al botón",
  pr=("La propiedad que ocupa el espacio libre es flex-___. (4 letras)", "grow"),
  pr2=("El valor por defecto de flex-grow es ___. (un número)", "0", "cero"),
  ec="dar flex-grow a todos los elementos y no ver diferencias"),
K("Flex abreviado",
  d="propiedad que combina crecer, encoger y base en una línea",
  u="controlar el tamaño de un elemento flex de forma compacta",
  mas="flex: 1 equivale a crecer 1, encoger 1 y base 0: reparte el espacio por igual. flex: 0 0 200px fija un tamaño de 200 px sin crecer ni encoger. flex-shrink controla cuánto se encoge y flex-basis el tamaño de partida.",
  k=["flex: 1 reparte el espacio de forma equitativa.", "flex-basis define el tamaño inicial del elemento.", "flex-shrink controla cuánto se encoge un elemento."],
  sit="Quieres tres columnas del mismo ancho que se repartan todo el espacio. ¿Qué valor de flex usas?",
  cod="""<style>
  .fila { display: flex; gap: 8px; }
  .fila div { flex: 1; background: #fbcfe8; padding: 14px; text-align: center; }
  .fila .fija { flex: 0 0 120px; background: #f9a8d4; }
</style>
<div class="fila"><div>1</div><div>2</div><div class="fija">Fija 120px</div></div>""",
  h="reparte el espacio por igual y fija una columna a 120 píxeles",
  pr=("Para repartir el espacio por igual entre hijos se usa flex: ___. (un número)", "1"),
  pr2=("La propiedad del tamaño inicial de un elemento flex es flex-___. (5 letras)", "basis"),
  ec="olvidar que flex: 1 deja la base en cero"),
K("Align-self",
  d="propiedad que alinea un solo elemento en el eje secundario",
  u="romper la alineación del grupo en un único hijo",
  mas="Mientras align-items actúa sobre todos los hijos desde el contenedor, align-self se pone en un hijo y cambia solo su alineación. Acepta los mismos valores: flex-start, center, flex-end o stretch.",
  k=["align-self alinea a un solo elemento.", "align-self sustituye a align-items para ese hijo.", "Se escribe en el hijo, no en el contenedor."],
  sit="Quieres que solo uno de los elementos de una fila se alinee abajo. ¿Qué propiedad usas?",
  cod="""<style>
  .fila { display: flex; align-items: flex-start; height: 110px; background: #ddd6fe; gap: 8px; }
  .fila div { background: #7c3aed; color: white; padding: 10px; }
  .abajo { align-self: flex-end; }    /* solo este baja */
</style>
<div class="fila"><div>Arriba</div><div class="abajo">Abajo</div><div>Arriba</div></div>""",
  h="baja un único elemento al fondo de la fila mientras los demás quedan arriba",
  pr=("La propiedad que alinea a un solo hijo es align-___. (4 letras)", "self"),
  pr2=("align-self se escribe en el ___, no en el contenedor. (4 letras)", "hijo"),
  ec="escribir align-self en el contenedor"),
K("Order",
  d="propiedad que cambia el orden visual de los elementos flex",
  u="reordenar elementos sin tocar el HTML",
  mas="Por defecto todos los elementos tienen order: 0 y siguen el orden del HTML. Con order: -1 un elemento pasa al principio y con order: 1 al final. Úsalo con cuidado: el orden de lectura con teclado sigue el del HTML.",
  k=["order cambia el orden visual de los elementos.", "Todos los elementos parten con order: 0.", "El orden de tabulación sigue siendo el del HTML."],
  sit="Quieres que el último elemento se muestre primero sin reescribir el HTML. ¿Qué propiedad usas?",
  cod="""<style>
  .fila { display: flex; gap: 8px; }
  .fila div { background: #fde68a; padding: 12px; }
  .fila .ultimo { order: -1; background: #fb923c; }   /* pasa al principio */
</style>
<div class="fila"><div>A</div><div>B</div><div class="ultimo">C (primero)</div></div>""",
  h="muestra el tercer elemento al principio sin cambiar el HTML",
  pr=("La propiedad que cambia el orden visual es ___. (5 letras)", "order"),
  pr2=("Para pasar un elemento al principio se usa order: ___. (un número negativo)", "-1"),
  ec="reordenar con order y olvidar el orden del teclado"),
K("Centrar con flexbox",
  d="técnica que centra un elemento en horizontal y vertical",
  u="centrar cualquier cosa dentro de su contenedor",
  mas="Con display: flex, justify-content: center y align-items: center el contenido queda exactamente en el centro. El contenedor necesita altura para que se note el centrado vertical. Es la solución clásica a «¿cómo centro un div?».",
  k=["Para centrar con flex se usan justify-content y align-items en center.", "El contenedor necesita altura para centrar en vertical.", "Es la forma moderna de centrar un elemento."],
  sit="Quieres centrar un mensaje justo en el medio de una caja, en horizontal y vertical. ¿Qué técnica usas?",
  cod="""<style>
  .caja {
    display: flex; justify-content: center; align-items: center;
    height: 140px; background: #bfdbfe;
  }
</style>
<div class="caja"><p>Centrado total</p></div>""",
  h="centra un texto en el medio exacto de una caja",
  pr=("Para centrar en el eje principal se usa justify-content: ___. (6 letras)", "center"),
  pr2=("Para centrar en el eje secundario se usa align-items: ___. (6 letras)", "center"),
  ec="olvidar dar altura al contenedor"),
K("Barra de navegación",
  d="menú horizontal construido con flexbox",
  u="crear el menú principal de una página",
  mas="Una barra clásica es un nav con una lista ul en display: flex. Se quitan las viñetas con list-style: none, se separan con gap y se alinean con justify-content. Se puede añadir el logo a la izquierda y los enlaces a la derecha.",
  k=["Una barra de navegación suele ser una lista con display: flex.", "Las viñetas se quitan con list-style: none.", "justify-content separa el logo de los enlaces."],
  sit="Quieres construir un menú horizontal con el logo a la izquierda y los enlaces a la derecha. ¿Qué técnica usas?",
  cod="""<style>
  nav { display: flex; justify-content: space-between; align-items: center; background: #1e293b; padding: 10px 20px; }
  nav ul { display: flex; gap: 16px; list-style: none; margin: 0; padding: 0; }
  nav a, nav b { color: white; text-decoration: none; }
</style>
<nav><b>MiLogo</b><ul><li><a href="#">Inicio</a></li><li><a href="#">Cursos</a></li></ul></nav>""",
  h="construye una barra con el logo a la izquierda y los enlaces a la derecha",
  pr=("La propiedad que quita las viñetas de una lista es list-style: ___. (4 letras)", "none"),
  pr2=("Para separar el logo de los enlaces se usa justify-content: space-___. (7 letras)", "between"),
  ec="olvidar quitar las viñetas y el margen de la lista"),
K("Grid",
  d="sistema de CSS para organizar elementos en filas y columnas",
  u="crear diseños en dos dimensiones",
  mas="Con display: grid el contenedor se convierte en una cuadrícula. A diferencia de flexbox, que trabaja en una dirección, grid controla filas y columnas a la vez. Es ideal para el diseño general de una página o galerías.",
  k=["Grid se activa con display: grid en el contenedor.", "Grid organiza elementos en filas y columnas a la vez.", "Flexbox es de una dimensión y grid de dos."],
  sit="Quieres organizar elementos en una cuadrícula de filas y columnas. ¿Qué sistema usas?",
  cod="""<style>
  .cuadricula { display: grid; grid-template-columns: 100px 100px 100px; gap: 8px; }
  .cuadricula div { background: #6ee7b7; padding: 16px; text-align: center; }
</style>
<div class="cuadricula"><div>1</div><div>2</div><div>3</div><div>4</div><div>5</div><div>6</div></div>""",
  h="coloca seis elementos en una cuadrícula de tres columnas",
  pr=("Grid se activa con display: ___. (4 letras)", "grid"),
  pr2=("Grid trabaja en ___ dimensiones. (un número)", "2", "dos"),
  ec="usar grid cuando bastaba flexbox, o viceversa"),
K("Columnas de grid",
  d="propiedad que define las columnas de la cuadrícula",
  u="decidir cuántas columnas hay y qué ancho tienen",
  mas="grid-template-columns: 200px 1fr 1fr crea tres columnas: una fija y dos que se reparten el resto. La función repeat() evita repetir: repeat(3, 1fr) son tres columnas iguales. Los elementos se colocan solos por filas.",
  k=["grid-template-columns define las columnas de la cuadrícula.", "repeat(3, 1fr) crea tres columnas iguales.", "Los elementos se colocan automáticamente en las celdas."],
  sit="Quieres una cuadrícula de tres columnas iguales sin repetir valores. ¿Qué escribes?",
  cod="""<style>
  .tres { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .tres div { background: #fcd34d; padding: 20px; text-align: center; }
</style>
<div class="tres"><div>1</div><div>2</div><div>3</div><div>4</div><div>5</div></div>""",
  h="crea tres columnas iguales con la función repeat",
  pr=("La propiedad que define las columnas es grid-template-___. (7 letras)", "columns"),
  pr2=("La función que evita repetir valores es ___(). (6 letras)", "repeat"),
  ec="olvidar repeat y escribir mal el número de columnas"),
K("Unidad fr",
  d="unidad que reparte el espacio libre en fracciones",
  u="repartir el ancho disponible entre columnas de grid",
  mas="1fr significa una fracción del espacio libre. 1fr 2fr reparte un tercio y dos tercios. Se puede mezclar con medidas fijas: 200px 1fr deja 200 px a la primera y todo lo demás a la segunda.",
  k=["La unidad fr reparte el espacio libre en fracciones.", "2fr recibe el doble de espacio que 1fr.", "Se puede combinar fr con medidas fijas como px."],
  sit="Quieres una columna lateral de 200 px y otra que ocupe todo el resto. ¿Qué escribes?",
  cod="""<style>
  .pagina { display: grid; grid-template-columns: 200px 1fr; gap: 10px; }
  .menu { background: #fca5a5; padding: 12px; }
  .contenido { background: #bbf7d0; padding: 12px; }
</style>
<div class="pagina"><div class="menu">Menú 200px</div><div class="contenido">Contenido: ocupa el resto</div></div>""",
  h="fija un menú de 200 píxeles y deja que el contenido ocupe lo que sobra",
  pr=("La unidad que reparte el espacio libre en fracciones es ___. (2 letras)", "fr"),
  pr2=("Una columna 2fr recibe el ___ que una 1fr. (una palabra)", "doble"),
  ec="creer que fr es una unidad fija como px"),
K("Filas de grid",
  d="propiedad que define el alto de las filas de la cuadrícula",
  u="controlar la altura de cada fila",
  mas="grid-template-rows funciona como las columnas pero en vertical. Si no la defines, las filas se crean solas con la altura de su contenido; grid-auto-rows permite fijar la altura de las filas automáticas.",
  k=["grid-template-rows define la altura de las filas.", "Sin definirla, las filas se crean según su contenido.", "grid-auto-rows fija la altura de las filas automáticas."],
  sit="Quieres que la primera fila mida 80 px y la segunda se adapte al resto. ¿Qué propiedad usas?",
  cod="""<style>
  .rejilla { display: grid; grid-template-rows: 80px 1fr; height: 200px; gap: 8px; }
  .rejilla div { background: #a5f3fc; padding: 10px; }
</style>
<div class="rejilla"><div>Fila de 80px</div><div>Ocupa el resto</div></div>""",
  h="define una fila fija de 80 píxeles y otra que ocupa el resto de la altura",
  pr=("La propiedad que define el alto de las filas es grid-template-___. (4 letras)", "rows"),
  pr2=("La propiedad que fija la altura de filas automáticas es grid-auto-___. (4 letras)", "rows"),
  ec="olvidar dar altura al contenedor al usar fr en las filas"),
K("Espacios en grid",
  d="uso de gap para separar celdas de la cuadrícula",
  u="dejar espacio uniforme entre filas y columnas",
  mas="En grid, gap: 10px 20px da 10 px entre filas y 20 px entre columnas. Si pones un solo valor se aplica a ambos. No añade espacio en los bordes exteriores, de modo que la cuadrícula queda alineada con el contenedor.",
  k=["En grid, gap separa filas y columnas.", "Con dos valores, el primero es entre filas y el segundo entre columnas.", "El gap no añade espacio en los bordes exteriores."],
  sit="Quieres 10 px entre filas y 30 px entre columnas de una cuadrícula. ¿Qué escribes?",
  cod="""<style>
  .g { display: grid; grid-template-columns: repeat(3, 80px); gap: 10px 30px; }  /* filas | columnas */
  .g div { background: #c4b5fd; padding: 12px; text-align: center; }
</style>
<div class="g"><div>1</div><div>2</div><div>3</div><div>4</div><div>5</div><div>6</div></div>""",
  h="separa 10 píxeles entre filas y 30 entre columnas de una cuadrícula",
  pr=("Con gap: 10px 30px, el primer valor es entre ___. (5 letras)", "filas"),
  pr2=("En grid, un solo valor de gap se aplica a ___. (una palabra: ambos o ninguno)", "ambos"),
  ec="confundir el orden de los dos valores de gap"),
K("Grid-column y grid-row",
  d="propiedades que hacen que un elemento ocupe varias celdas",
  u="crear elementos destacados que abarcan filas o columnas",
  mas="grid-column: span 2 hace que el elemento ocupe dos columnas, y grid-row: span 2 dos filas. También se puede indicar la posición con líneas: grid-column: 1 / 3. Las líneas de la cuadrícula se numeran desde 1.",
  k=["grid-column: span 2 ocupa dos columnas.", "Las líneas de la cuadrícula se numeran desde 1.", "grid-row: span 2 ocupa dos filas."],
  sit="Quieres que una tarjeta destacada ocupe dos columnas de la cuadrícula. ¿Qué propiedad usas?",
  cod="""<style>
  .g { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .g div { background: #fda4af; padding: 14px; text-align: center; }
  .g .ancha { grid-column: span 2; background: #fb7185; }
</style>
<div class="g"><div class="ancha">Ocupa 2 columnas</div><div>2</div><div>3</div><div>4</div><div>5</div></div>""",
  h="hace que un elemento destacado ocupe dos columnas de la cuadrícula",
  pr=("Para ocupar dos columnas se escribe grid-column: ___ 2. (4 letras)", "span"),
  pr2=("Las líneas de la cuadrícula se numeran desde el ___. (un número)", "1", "uno"),
  ec="empezar a contar las líneas desde cero"),
K("Áreas de grid",
  d="forma de dibujar el diseño con nombres de zonas",
  u="definir el diseño de una página de forma visual",
  mas="Con grid-template-areas escribes el diseño como un dibujo con palabras, y a cada elemento le das un nombre con grid-area. Es muy legible para diseños típicos: cabecera, menú, contenido y pie.",
  k=["grid-template-areas dibuja el diseño con nombres.", "grid-area asigna un nombre de zona a cada elemento.", "Es ideal para el diseño general de una página."],
  sit="Quieres describir el diseño de la página (cabecera, menú, contenido y pie) como un dibujo con nombres. ¿Qué usas?",
  cod="""<style>
  .pagina { display: grid; gap: 6px; grid-template-columns: 100px 1fr;
    grid-template-areas: "cab cab" "menu cont" "pie pie"; }
  .cab { grid-area: cab; background: #93c5fd; } .menu { grid-area: menu; background: #fca5a5; }
  .cont { grid-area: cont; background: #86efac; } .pie { grid-area: pie; background: #fde68a; }
  .pagina div { padding: 12px; }
</style>
<div class="pagina"><div class="cab">Cabecera</div><div class="menu">Menú</div><div class="cont">Contenido</div><div class="pie">Pie</div></div>""",
  h="dibuja con nombres un diseño con cabecera, menú, contenido y pie",
  pr=("La propiedad que dibuja el diseño con nombres es grid-template-___. (5 letras)", "areas"),
  pr2=("La propiedad que asigna un nombre de zona a un elemento es grid-___. (4 letras)", "area"),
  ec="escribir un área con forma que no es rectangular"),
K("Auto-fit y minmax",
  d="funciones que crean columnas adaptables sin media queries",
  u="hacer galerías que se reorganizan según el ancho disponible",
  mas="repeat(auto-fit, minmax(200px, 1fr)) crea tantas columnas de al menos 200 px como quepan, y se estiran para llenar el espacio. Cuando se estrecha la pantalla, las columnas bajan solas. Es el truco clave para tarjetas responsive.",
  k=["minmax define un tamaño mínimo y uno máximo.", "auto-fit crea tantas columnas como quepan.", "Permite diseños adaptables sin usar media queries."],
  sit="Quieres una galería que muestre más o menos columnas según el ancho de pantalla sin escribir media queries. ¿Qué escribes?",
  cod="""<style>
  .galeria { display: grid; gap: 10px;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); }
  .galeria div { background: #67e8f9; padding: 24px; text-align: center; }
</style>
<div class="galeria"><div>1</div><div>2</div><div>3</div><div>4</div><div>5</div><div>6</div></div>""",
  h="crea una galería cuyas columnas se adaptan al ancho disponible",
  pr=("La función que define un tamaño mínimo y máximo es ___(). (6 letras)", "minmax"),
  pr2=("El valor que crea tantas columnas como quepan es auto-___. (3 letras)", "fit"),
  ec="usar un mínimo mayor que el ancho de pantallas pequeñas"),
]
