// Curso: HTML desde cero. live: true -> botón "Probar en el laboratorio".
const r = String.raw;

export const HTML = [
{ t: "¿Qué es HTML? Estructura básica",
  d: "HTML (HyperText Markup Language) describe el contenido de una página con etiquetas. No es un lenguaje de programación: es un lenguaje de marcado que le dice al navegador qué es cada cosa (título, párrafo, imagen…). Todos los documentos HTML comparten la misma estructura base.",
  p: ["<!DOCTYPE html> indica que es HTML5", "<head> guarda información de la página (título, codificación)", "<body> contiene todo lo que se ve en pantalla", "Guarda tu archivo como index.html y ábrelo en el navegador"],
  live: true,
  c: r`<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Mi primera página</title>
</head>
<body>
  <h1>¡Hola, mundo!</h1>
</body>
</html>` },

{ t: "Títulos, párrafos y texto",
  d: "Los títulos van de <h1> (el más importante) a <h6>. El texto normal va en párrafos <p>. Con etiquetas de énfasis puedes resaltar partes del texto.",
  p: ["Usa un solo <h1> por página", "<strong> = negrita con importancia, <em> = cursiva con énfasis", "<br> salta de línea y <hr> dibuja una línea separadora", "Las etiquetas se abren <p> y se cierran </p>"],
  live: true,
  c: r`<h1>Mi blog de código</h1>
<h2>Primeros pasos</h2>
<p>Aprender HTML es <strong>fácil</strong> y <em>divertido</em>.</p>
<hr>
<p>Primera línea<br>Segunda línea</p>` },

{ t: "Enlaces e imágenes",
  d: "Los enlaces <a> conectan páginas entre sí. Las imágenes <img> insertan fotos y gráficos. Ambos usan atributos, que dan información extra a la etiqueta.",
  p: ["href indica a dónde lleva el enlace", "target=\"_blank\" abre el enlace en una pestaña nueva", "src es la ruta de la imagen y alt su descripción (importante para accesibilidad)", "<img> no necesita etiqueta de cierre"],
  live: true,
  c: r`<a href="https://developer.mozilla.org" target="_blank">Documentación de MDN</a>

<p>
  <img src="https://placehold.co/300x120" alt="Imagen de ejemplo">
</p>` },

{ t: "Listas",
  d: "Las listas ordenan la información. Las listas con viñetas usan <ul>, las numeradas <ol>, y cada elemento va dentro de un <li>.",
  p: ["<ul> = lista sin orden (viñetas)", "<ol> = lista ordenada (números)", "Puedes anidar listas dentro de un <li>"],
  live: true,
  c: r`<h3>Lenguajes que quiero aprender</h3>
<ul>
  <li>HTML</li>
  <li>CSS</li>
  <li>JavaScript
    <ol>
      <li>Variables</li>
      <li>Funciones</li>
    </ol>
  </li>
</ul>` },

{ t: "Tablas",
  d: "Las tablas muestran datos en filas y columnas. Se usan para información tabular, no para maquetar la página.",
  p: ["<table> es la tabla y <tr> cada fila", "<th> es una celda de encabezado y <td> una celda de datos", "colspan y rowspan unen celdas", "<thead> y <tbody> separan cabecera y cuerpo"],
  live: true,
  c: r`<table border="1" cellpadding="6">
  <thead>
    <tr><th>Lenguaje</th><th>Año</th></tr>
  </thead>
  <tbody>
    <tr><td>Python</td><td>1991</td></tr>
    <tr><td>JavaScript</td><td>1995</td></tr>
  </tbody>
</table>` },

{ t: "Formularios",
  d: "Los formularios recogen datos del usuario: texto, correos, opciones, archivos… Cada campo se asocia con una etiqueta <label> para que sea accesible.",
  p: ["<input type=\"...\"> cambia según el dato: text, email, password, number, checkbox, radio", "<select> crea una lista desplegable y <textarea> un campo de texto largo", "required obliga a rellenar el campo", "El atributo action indica a dónde se envían los datos"],
  live: true,
  c: r`<form>
  <label>Nombre: <input type="text" name="nombre" required></label><br><br>
  <label>Correo: <input type="email" name="correo"></label><br><br>
  <label>Nivel:
    <select name="nivel">
      <option>Principiante</option>
      <option>Intermedio</option>
    </select>
  </label><br><br>
  <label><input type="checkbox"> Acepto las condiciones</label><br><br>
  <button type="submit">Enviar</button>
</form>` },

{ t: "Atributos, id y class",
  d: "Los atributos añaden información a cualquier etiqueta. Dos son fundamentales: id (identificador único) y class (grupo reutilizable). Más adelante CSS los usará para dar estilo. <div> y <span> son contenedores genéricos.",
  p: ["id debe ser único en la página", "class puede repetirse en muchos elementos", "<div> es un bloque; <span> es en línea", "title muestra un texto al pasar el ratón"],
  live: true,
  c: r`<div id="cabecera" class="caja">
  <p class="destacado" title="Texto de ayuda">Pasa el ratón por aquí</p>
  <p>Una palabra <span class="destacado">resaltada</span> dentro de un párrafo.</p>
</div>` },

{ t: "Etiquetas semánticas",
  d: "Las etiquetas semánticas describen el significado de cada zona de la página. Ayudan al SEO, a la accesibilidad y a que tu código sea más claro que con tantos <div>.",
  p: ["<header> y <footer>: cabecera y pie", "<nav>: menú de navegación", "<main>: contenido principal (uno por página)", "<section>, <article>, <aside>: bloques de contenido"],
  live: true,
  c: r`<header>
  <h1>Mi sitio</h1>
  <nav><a href="#">Inicio</a> | <a href="#">Cursos</a></nav>
</header>
<main>
  <article>
    <h2>Artículo de ejemplo</h2>
    <p>Contenido del artículo.</p>
  </article>
  <aside>Un dato curioso</aside>
</main>
<footer>© 2026 Mi sitio</footer>` },

{ t: "Elementos útiles: desplegables, progreso y multimedia",
  d: "HTML incluye elementos interactivos sin necesidad de programar: bloques que se despliegan, barras de progreso y reproductores de audio y vídeo.",
  p: ["<details> y <summary> crean un bloque desplegable", "<progress> y <meter> muestran avances y medidas", "<video controls src=\"...\"> y <audio controls src=\"...\"> reproducen archivos", "Siempre incluye controls para que el usuario pueda manejarlos"],
  live: true,
  c: r`<details>
  <summary>¿Qué es HTML?</summary>
  <p>El lenguaje que da estructura a las páginas web.</p>
</details>

<p>Progreso del curso:</p>
<progress value="60" max="100"></progress>

<!-- Con un archivo propio:
<video controls width="320" src="mi-video.mp4"></video>
<audio controls src="mi-audio.mp3"></audio>
-->` },

{ t: "Proyecto: tu página personal",
  d: "Pon en práctica todo lo aprendido: una página con cabecera, presentación, lista de intereses, tabla y formulario de contacto. Cámbiala con tus datos y guárdala como index.html.",
  p: ["Usa etiquetas semánticas", "Añade al menos un enlace y una lista", "Prueba a añadir una imagen con su alt", "Cuando termines, pídele al tutor que revise tu código"],
  live: true,
  c: r`<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Sobre mí</title>
</head>
<body>
  <header>
    <h1>Hola, soy Ana</h1>
    <nav><a href="#intereses">Intereses</a> | <a href="#contacto">Contacto</a></nav>
  </header>
  <main>
    <section>
      <h2>Presentación</h2>
      <p>Estudio programación y me encanta la <strong>web</strong>.</p>
    </section>
    <section id="intereses">
      <h2>Intereses</h2>
      <ul><li>Videojuegos</li><li>Música</li><li>Diseño web</li></ul>
    </section>
    <section id="contacto">
      <h2>Contacto</h2>
      <form>
        <label>Mensaje:<br><textarea rows="3" cols="30"></textarea></label><br>
        <button>Enviar</button>
      </form>
    </section>
  </main>
  <footer><p>© 2026 Ana</p></footer>
</body>
</html>` },
];
