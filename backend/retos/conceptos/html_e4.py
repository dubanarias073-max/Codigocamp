"""HTML · Etapa 4: tablas y formularios."""
from ..generador import K

LISTA = [
K("Tabla",
  d="etiqueta que organiza datos en filas y columnas",
  u="mostrar datos como horarios, precios o resultados",
  mas="Una tabla se construye con <table>. Dentro se escriben filas y en cada fila, celdas. Las tablas son para datos, no para diseñar la página: para el diseño se usa CSS.",
  k=["La etiqueta table crea una tabla de datos.", "Una tabla se compone de filas y celdas.", "Las tablas no deben usarse para diseñar la página."],
  sit="Quieres mostrar un horario con días en columnas y horas en filas. ¿Qué estructura usas?",
  cod="""<!-- table envuelve toda la tabla -->
<table border="1">
  <tr><td>Lunes</td><td>Matemáticas</td></tr>
  <tr><td>Martes</td><td>Historia</td></tr>
</table>""",
  h="dibuja una tabla de dos filas con día y materia",
  pr=("La etiqueta que crea una tabla es ___. (5 letras)", "table", "<table>"),
  pr2=("Las tablas sirven para mostrar ___, no para diseñar. (una palabra)", "datos"),
  ec="usar tablas para colocar el diseño de la página",
  err=("<table>\n  <td>Lunes</td><td>Mates</td>\n</table>", 2, "Las celdas td deben ir dentro de una fila tr.")),
K("Filas y celdas",
  d="etiquetas tr para filas y td para celdas",
  u="colocar cada dato en su lugar de la tabla",
  mas="Cada <tr> es una fila horizontal. Dentro de ella cada <td> es una celda con un dato. Todas las filas deberían tener el mismo número de celdas para que la tabla quede ordenada.",
  k=["La etiqueta tr crea una fila.", "La etiqueta td crea una celda de datos.", "Las celdas td van dentro de las filas tr."],
  sit="Quieres añadir una fila nueva con tres datos a una tabla. ¿Qué etiquetas escribes?",
  cod="""<table border="1">
  <!-- tr: una fila; td: una celda dentro de la fila -->
  <tr>
    <td>Ana</td>
    <td>20 años</td>
    <td>Lima</td>
  </tr>
</table>""",
  h="crea una fila con tres celdas de datos",
  pr=("La etiqueta de una fila de tabla es ___. (2 letras)", "tr", "<tr>"),
  pr2=("La etiqueta de una celda de datos es ___. (2 letras)", "td", "<td>"),
  ec="escribir un número distinto de celdas en cada fila"),
K("Encabezados th",
  d="celdas especiales que titulan una columna o fila",
  u="indicar qué significa cada columna",
  mas="<th> funciona como td, pero indica que la celda es un título. Se muestra en negrita y centrado, y los lectores de pantalla la anuncian como encabezado. Normalmente van en la primera fila.",
  k=["La etiqueta th crea una celda de encabezado.", "Los encabezados suelen mostrarse en negrita y centrados.", "Los lectores de pantalla anuncian th como títulos."],
  sit="Quieres que la primera fila diga «Nombre» y «Edad» como títulos de columna. ¿Qué etiqueta usas?",
  cod="""<table border="1">
  <tr>
    <!-- th: celdas de título -->
    <th>Nombre</th>
    <th>Edad</th>
  </tr>
  <tr><td>Ana</td><td>20</td></tr>
</table>""",
  h="pone títulos de columna en la primera fila de la tabla",
  pr=("La celda de encabezado se escribe con la etiqueta ___. (2 letras)", "th", "<th>"),
  pr2=("Los encabezados th suelen mostrarse en ___. (una palabra)", "negrita"),
  ec="usar td con negrita en vez de th"),
K("Thead, tbody y tfoot",
  d="etiquetas que dividen la tabla en cabecera, cuerpo y pie",
  u="ordenar tablas grandes por secciones con significado",
  mas="<thead> agrupa las filas de títulos, <tbody> las de datos y <tfoot> las de totales. No cambian el aspecto por sí solas, pero dan estructura a la tabla y permiten dar estilo por separado con CSS.",
  k=["La etiqueta thead agrupa la cabecera de la tabla.", "La etiqueta tbody agrupa las filas de datos.", "La etiqueta tfoot agrupa el pie de la tabla."],
  sit="Quieres separar en tu tabla la fila de títulos, las filas de datos y la fila de totales. ¿Qué etiquetas usas?",
  cod="""<table border="1">
  <thead><tr><th>Producto</th><th>Precio</th></tr></thead>
  <tbody>
    <tr><td>Café</td><td>5</td></tr>
    <tr><td>Té</td><td>4</td></tr>
  </tbody>
  <tfoot><tr><td>Total</td><td>9</td></tr></tfoot>
</table>""",
  h="divide la tabla en cabecera, cuerpo y pie con totales",
  pr=("La etiqueta del pie de una tabla es ___. (5 letras)", "tfoot", "<tfoot>"),
  pr2=("La etiqueta que agrupa las filas de datos es ___. (5 letras)", "tbody", "<tbody>"),
  ec="mezclar filas de datos dentro de thead"),
K("Caption",
  d="título descriptivo de una tabla",
  u="explicar de qué trata una tabla",
  mas="<caption> va como primer hijo de table y se muestra encima. Ayuda a todos a saber qué contiene la tabla, y a los lectores de pantalla a anunciarla antes de leer los datos.",
  k=["La etiqueta caption pone título a una tabla.", "El caption va dentro de table, antes de las filas.", "Ayuda a los lectores de pantalla a describir la tabla."],
  sit="Quieres que tu tabla tenga un título visible, como «Notas del trimestre». ¿Qué etiqueta usas?",
  cod="""<table border="1">
  <!-- caption: título de la tabla, primero dentro de table -->
  <caption>Notas del primer trimestre</caption>
  <tr><th>Materia</th><th>Nota</th></tr>
  <tr><td>Lengua</td><td>8</td></tr>
</table>""",
  h="pone un título visible sobre la tabla de notas",
  pr=("La etiqueta que da título a una tabla es ___. (7 letras)", "caption", "<caption>"),
  pr2=("El caption va como primer elemento dentro de ___. (5 letras)", "table", "<table>"),
  ec="escribir el título en un p suelto y no en caption"),
K("Colspan y rowspan",
  d="atributos que unen celdas de varias columnas o filas",
  u="crear celdas más grandes que ocupen varios huecos",
  mas="colspan=\"2\" hace que una celda ocupe dos columnas y rowspan=\"2\" dos filas. Al unir celdas, debes escribir menos celdas en esa fila (o en las siguientes) para que los totales coincidan.",
  k=["El atributo colspan une celdas de varias columnas.", "El atributo rowspan une celdas de varias filas.", "Al unir celdas hay que escribir menos celdas en esa fila."],
  sit="Quieres que una celda de título abarque dos columnas de la tabla. ¿Qué atributo usas?",
  cod="""<table border="1">
  <tr>
    <!-- colspan="2": esta celda ocupa dos columnas -->
    <th colspan="2">Resultados</th>
  </tr>
  <tr><td>Ana</td><td>9</td></tr>
</table>""",
  h="hace que el título ocupe el ancho de dos columnas",
  pr=("El atributo que une celdas en horizontal es ___. (7 letras)", "colspan"),
  pr2=("El atributo que une celdas en vertical es ___. (7 letras)", "rowspan"),
  ec="olvidar quitar celdas sobrantes al usar colspan"),
K("Formulario form",
  d="etiqueta que agrupa los campos que el usuario rellena",
  u="recoger datos como registros, búsquedas y contactos",
  mas="Todo formulario va dentro de <form>. Dentro se colocan los campos (input, select, textarea) y un botón para enviar. Sin form, los campos existen pero no se pueden enviar juntos.",
  k=["La etiqueta form agrupa los campos de un formulario.", "Un formulario necesita un botón para enviar los datos.", "Los campos deben estar dentro de la etiqueta form."],
  sit="Quieres crear un formulario de contacto con varios campos y un botón. ¿Qué etiqueta lo envuelve todo?",
  cod="""<!-- form agrupa los campos y el botón -->
<form>
  <input type="text" name="nombre">
  <button type="submit">Enviar</button>
</form>""",
  h="agrupa un campo de nombre y un botón de envío en un formulario",
  pr=("La etiqueta que envuelve un formulario es ___. (4 letras)", "form", "<form>"),
  pr2=("Un formulario necesita un botón para ___ los datos. (una palabra)", "enviar"),
  ec="colocar los campos fuera de la etiqueta form",
  err=("<form>\n  <input type=\"text\" name=\"nombre\">\n</form>\n<button type=\"submit\">Enviar</button>", 4, "El botón de envío quedó fuera del form, así que no enviará los datos.")),
K("Action y method",
  d="atributos que dicen a dónde y cómo se envía el formulario",
  u="decidir el destino y la forma de enviar los datos",
  mas="action contiene la dirección que recibirá los datos. method puede ser GET (los datos van visibles en la dirección, ideal para búsquedas) o POST (van ocultos, para contraseñas y registros). Un formulario sin backend no guarda nada por sí solo.",
  k=["El atributo action indica dónde se envían los datos.", "El método GET muestra los datos en la dirección.", "El método POST oculta los datos y se usa para registros."],
  sit="Quieres enviar una contraseña sin que se vea en la dirección del navegador. ¿Qué método eliges?",
  cod="""<!-- action: destino; method: cómo viajan los datos -->
<form action="/registro" method="post">
  <input type="password" name="clave">
  <button>Registrarme</button>
</form>""",
  h="envía una contraseña por el método post a la ruta de registro",
  pr=("El método que no muestra los datos en la dirección es ___. (4 letras)", "post"),
  pr2=("El atributo que indica a dónde van los datos es ___. (6 letras)", "action"),
  ec="enviar contraseñas con el método get"),
K("Input de texto",
  d="campo de una línea para escribir texto",
  u="pedir nombres, ciudades o cualquier dato corto",
  mas="<input type=\"text\"> crea un campo de una línea. Es la etiqueta de formulario más usada; no lleva cierre. Con el atributo type cambias el tipo de campo, y por defecto es text.",
  k=["La etiqueta input crea campos de formulario.", "Con type=\"text\" se escribe texto de una línea.", "La etiqueta input no lleva cierre."],
  sit="Quieres un campo donde el visitante escriba su nombre en una sola línea. ¿Qué usas?",
  cod="""<form>
  <!-- type="text": una línea de texto; name: nombre del dato -->
  <input type="text" name="nombre" id="nombre">
</form>""",
  h="crea un campo de una línea para escribir el nombre",
  pr=("El tipo de input para texto de una línea es ___. (4 letras)", "text"),
  pr2=("La etiqueta input ___ lleva etiqueta de cierre. (sí o no)", "no"),
  ec="olvidar el atributo type y el name"),
K("Label",
  d="etiqueta de texto que se asocia a un campo",
  u="indicar qué debe escribirse en cada campo",
  mas="Un <label for=\"nombre\"> se conecta con el campo cuyo id es nombre. Al pulsar el texto, el cursor entra en el campo, y los lectores de pantalla lo anuncian. Es obligatorio para formularios accesibles.",
  k=["El label describe un campo del formulario.", "El atributo for del label coincide con el id del campo.", "Pulsar el label coloca el cursor en el campo."],
  sit="Quieres que al pulsar el texto «Correo» el cursor entre en su campo. ¿Qué usas?",
  cod="""<!-- for coincide con el id del input -->
<label for="correo">Correo:</label>
<input type="email" id="correo" name="correo">""",
  h="conecta el texto «Correo» con su campo mediante for e id",
  pr=("El atributo for de un label debe coincidir con el ___ del campo. (2 letras)", "id"),
  pr2=("La etiqueta que describe un campo es ___. (5 letras)", "label", "<label>"),
  ec="usar un for que no coincide con ningún id",
  err=("<label for=\"nombre\">Nombre</label>\n<input type=\"text\" id=\"nom\">", 2, "El id del campo debe ser igual al for del label (nombre).")),
K("Tipos de input",
  d="valores de type que cambian el campo",
  u="pedir datos concretos con ayuda del navegador",
  mas="Además de text existen email, password (oculta los caracteres), number, date, tel, url y color. Cada uno abre el teclado adecuado en el móvil y valida un poco los datos.",
  k=["El tipo email espera una dirección de correo.", "El tipo password oculta lo que se escribe.", "El tipo number solo acepta números."],
  sit="Quieres un campo que oculte lo que el usuario escribe. ¿Qué tipo de input usas?",
  cod="""<!-- Cada type cambia el campo -->
<input type="email"    name="correo">
<input type="password" name="clave">
<input type="number"   name="edad" min="0" max="120">
<input type="date"     name="nacimiento">""",
  h="muestra campos de correo, contraseña, número y fecha",
  pr=("El tipo de input que oculta lo escrito es ___. (8 letras)", "password"),
  pr2=("El tipo de input para elegir una fecha es ___. (4 letras)", "date"),
  ec="usar type=\"text\" para contraseñas"),
K("Atributo name",
  d="nombre con el que viaja el dato del campo",
  u="identificar cada dato recibido por el servidor",
  mas="Cuando se envía el formulario, el servidor recibe pares nombre=valor. Sin name, el campo no se envía. Por eso cada campo debe tener name, además de id si se usa con label.",
  k=["El atributo name identifica el dato al enviarlo.", "Un campo sin name no se envía.", "No confundas name con id: tienen funciones distintas."],
  sit="Un campo no llega al servidor al enviar el formulario porque le falta el nombre del dato. ¿Qué atributo falta?",
  cod="""<form action="/contacto" method="post">
  <!-- name: el servidor recibe nombre=Ana -->
  <input type="text" name="nombre">
  <!-- sin name este dato no se enviaría -->
  <button type="submit">Enviar</button>
</form>""",
  h="asigna un nombre al campo para que el dato se envíe",
  pr=("Un campo que no tiene ___ no se envía. (4 letras)", "name"),
  pr2=("Al enviar, el servidor recibe pares nombre=___. (una palabra)", "valor"),
  ec="olvidar name y creer que el campo se enviará"),
K("Checkbox",
  d="casilla que se marca o se desmarca",
  u="permitir elegir una o varias opciones",
  mas="<input type=\"checkbox\"> crea una casilla independiente. Se pueden marcar varias a la vez. Con el atributo checked aparece marcada desde el inicio. Va acompañada de un label.",
  k=["Los checkbox permiten marcar varias opciones a la vez.", "El atributo checked deja la casilla marcada desde el principio.", "Cada checkbox debe llevar su label."],
  sit="Quieres que el usuario pueda marcar varios intereses a la vez. ¿Qué campo usas?",
  cod="""<!-- Cada casilla es independiente -->
<label><input type="checkbox" name="interes" value="web" checked> Web</label>
<label><input type="checkbox" name="interes" value="datos"> Datos</label>
<label><input type="checkbox" name="interes" value="juegos"> Juegos</label>""",
  h="ofrece tres casillas, con la primera marcada desde el inicio",
  pr=("El tipo de input para casillas marcables es ___. (8 letras)", "checkbox"),
  pr2=("El atributo que deja una casilla marcada al inicio es ___. (7 letras)", "checked"),
  ec="usar checkbox cuando solo se debe elegir una opción"),
K("Radio",
  d="botón redondo para elegir una sola opción de un grupo",
  u="obligar a elegir una única respuesta",
  mas="Los <input type=\"radio\"> comparten el mismo name para formar un grupo. Al marcar uno, se desmarca el anterior. Cada opción lleva un value distinto.",
  k=["En un grupo de radios solo se puede marcar una opción.", "Los radios del mismo grupo comparten el atributo name.", "Cada radio tiene su propio value."],
  sit="Quieres que el usuario elija solo una talla: S, M o L. ¿Qué campo usas?",
  cod="""<!-- mismo name = un solo grupo: se elige una opción -->
<label><input type="radio" name="talla" value="s"> S</label>
<label><input type="radio" name="talla" value="m" checked> M</label>
<label><input type="radio" name="talla" value="l"> L</label>""",
  h="ofrece tres tallas de las que solo se puede elegir una",
  pr=("El tipo de input para elegir una única opción es ___. (5 letras)", "radio"),
  pr2=("Los radios de un mismo grupo comparten el atributo ___. (4 letras)", "name"),
  ec="darle a cada radio un name distinto",
  err=("<input type=\"radio\" name=\"talla\" value=\"s\"> S\n<input type=\"radio\" name=\"tamano\" value=\"m\"> M\n<input type=\"radio\" name=\"talla\" value=\"l\"> L", 2, "Para formar un grupo, el name debe ser el mismo en los tres radios.")),
K("Select y option",
  d="lista desplegable para elegir una opción",
  u="ofrecer muchas opciones sin ocupar espacio",
  mas="<select> es la lista desplegable y cada <option> es una opción. El value de la option es lo que se envía y el texto es lo que se ve. Es ideal para países o ciudades.",
  k=["La etiqueta select crea una lista desplegable.", "Cada opción se escribe en una etiqueta option.", "El value de la option es el dato que se envía."],
  sit="Quieres que el usuario elija su país de una lista desplegable. ¿Qué etiquetas usas?",
  cod="""<label for="pais">País:</label>
<!-- select es la lista; option, cada elemento -->
<select id="pais" name="pais">
  <option value="pe">Perú</option>
  <option value="mx">México</option>
  <option value="co">Colombia</option>
</select>""",
  h="muestra una lista desplegable con tres países",
  pr=("La etiqueta de cada opción de una lista desplegable es ___. (6 letras)", "option", "<option>"),
  pr2=("La lista desplegable se crea con la etiqueta ___. (6 letras)", "select", "<select>"),
  ec="escribir las opciones fuera de la etiqueta select"),
K("Textarea",
  d="campo de varias líneas para texto largo",
  u="recoger mensajes, comentarios o descripciones",
  mas="<textarea> permite escribir muchas líneas. Se le dan filas y columnas con rows y cols, o se ajusta con CSS. A diferencia de input, sí tiene etiqueta de cierre y su contenido inicial va entre las etiquetas.",
  k=["La etiqueta textarea crea un campo de varias líneas.", "El textarea sí lleva etiqueta de cierre.", "Los atributos rows y cols controlan su tamaño."],
  sit="Quieres un cuadro donde el visitante escriba un mensaje largo. ¿Qué campo usas?",
  cod="""<label for="msg">Mensaje:</label>
<!-- rows: altura en líneas; cols: ancho en caracteres -->
<textarea id="msg" name="mensaje" rows="4" cols="40">Escribe aquí...</textarea>""",
  h="crea un cuadro de varias líneas con un texto inicial",
  pr=("El campo para mensajes de varias líneas es ___. (8 letras)", "textarea", "<textarea>"),
  pr2=("El atributo que fija la altura de un textarea en líneas es ___. (4 letras)", "rows"),
  ec="usar input type=\"text\" para mensajes largos"),
K("Botones",
  d="elemento que ejecuta una acción al pulsarlo",
  u="enviar, borrar o activar acciones del formulario",
  mas="<button type=\"submit\"> envía el formulario, type=\"reset\" lo vacía y type=\"button\" no hace nada por sí solo (se usa con JavaScript). Si no indicas type dentro de un form, el botón envía.",
  k=["Un button con type=\"submit\" envía el formulario.", "Un button con type=\"reset\" vacía los campos.", "Sin type, un botón dentro de un form envía los datos."],
  sit="Quieres un botón que borre todos los campos del formulario. ¿Qué type usas?",
  cod="""<form>
  <input type="text" name="nombre">
  <!-- submit envía; reset vacía; button solo hace algo con JavaScript -->
  <button type="submit">Enviar</button>
  <button type="reset">Borrar todo</button>
</form>""",
  h="añade un botón que envía y otro que vacía los campos",
  pr=("El type de button que envía el formulario es ___. (6 letras)", "submit"),
  pr2=("El type de button que vacía los campos es ___. (5 letras)", "reset"),
  ec="pulsar un button sin type dentro de un form sin querer enviar"),
K("Placeholder",
  d="texto de ayuda gris dentro de un campo vacío",
  u="mostrar un ejemplo de lo que se debe escribir",
  mas="El atributo placeholder muestra un texto tenue que desaparece al escribir. Sirve de ejemplo, como «nombre@correo.com», pero no sustituye al label porque desaparece y puede tener poco contraste.",
  k=["El placeholder muestra una pista dentro del campo vacío.", "El placeholder desaparece cuando se escribe.", "El placeholder no sustituye al label."],
  sit="Quieres mostrar «nombre@correo.com» en gris dentro del campo vacío como ejemplo. ¿Qué atributo usas?",
  cod="""<label for="correo">Correo:</label>
<!-- placeholder: pista que desaparece al escribir -->
<input type="email" id="correo" name="correo" placeholder="nombre@correo.com">""",
  h="muestra un ejemplo de correo en gris dentro del campo vacío",
  pr=("El atributo que muestra una pista gris dentro del campo es ___. (11 letras)", "placeholder"),
  pr2=("El placeholder ___ sustituye al label. (no)", "no"),
  ec="usar solo placeholder y quitar el label"),
K("Required y validación",
  d="atributos que exigen datos válidos antes de enviar",
  u="evitar formularios vacíos o con datos mal escritos",
  mas="required impide enviar un campo vacío. Con type=\"email\" el navegador comprueba el formato. También existen minlength, maxlength, min, max y pattern. Es una ayuda para el usuario, pero el servidor siempre debe volver a validar.",
  k=["El atributo required impide enviar un campo vacío.", "El navegador valida el formato de los campos email.", "La validación del navegador no sustituye a la del servidor."],
  sit="Quieres que el formulario no se envíe si el campo del correo está vacío. ¿Qué atributo añades?",
  cod="""<form>
  <!-- required: no se envía vacío; type="email": revisa el formato -->
  <input type="email" name="correo" required>
  <!-- minlength: mínimo de caracteres -->
  <input type="password" name="clave" minlength="8" required>
  <button>Enviar</button>
</form>""",
  h="exige un correo válido y una contraseña de al menos ocho caracteres",
  pr=("El atributo que impide enviar un campo vacío es ___. (8 letras)", "required"),
  pr2=("El atributo que fija un mínimo de caracteres es ___. (9 letras)", "minlength"),
  ec="confiar solo en la validación del navegador"),
K("Fieldset y legend",
  d="etiquetas que agrupan campos relacionados con un título",
  u="ordenar formularios largos en bloques con nombre",
  mas="<fieldset> dibuja un recuadro alrededor de campos relacionados y <legend> le pone título. Además de verse ordenado, ayuda a los lectores de pantalla a entender el grupo, sobre todo con radios y casillas.",
  k=["La etiqueta fieldset agrupa campos relacionados.", "La etiqueta legend es el título del grupo.", "El legend va dentro del fieldset."],
  sit="Quieres agrupar los campos de dirección bajo el título «Envío». ¿Qué etiquetas usas?",
  cod="""<fieldset>
  <!-- legend: título del recuadro -->
  <legend>Datos de envío</legend>
  <label for="calle">Calle:</label>
  <input type="text" id="calle" name="calle">
  <label for="ciudad">Ciudad:</label>
  <input type="text" id="ciudad" name="ciudad">
</fieldset>""",
  h="agrupa los campos de dirección en un recuadro con título",
  pr=("El título de un grupo de campos se escribe en la etiqueta ___. (6 letras)", "legend", "<legend>"),
  pr2=("La etiqueta que agrupa campos relacionados es ___. (8 letras)", "fieldset", "<fieldset>"),
  ec="escribir el legend fuera del fieldset"),
]
