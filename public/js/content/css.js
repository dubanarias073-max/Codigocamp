// Curso: CSS desde cero. Los ejemplos incluyen su HTML para poder probarlos.
const r = String.raw;

export const CSS = [
{ t: "¿Qué es CSS y cómo se añade?",
  d: "CSS (Cascading Style Sheets) controla el aspecto de una página: colores, tipografías, tamaños y posición. HTML pone el contenido y CSS lo hace bonito. Hay tres formas de añadirlo; la recomendada es un archivo externo.",
  p: ["En línea: atributo style en la etiqueta (solo para pruebas)", "Interno: etiqueta <style> dentro del <head>", "Externo: <link rel=\"stylesheet\" href=\"estilos.css\"> (la mejor opción)", "Una regla CSS tiene selector { propiedad: valor; }"],
  live: true,
  c: r`<style>
  h1 {
    color: tomato;
    font-family: sans-serif;
  }
</style>

<h1>Hola CSS</h1>
<p style="color: gray;">Este párrafo tiene estilo en línea.</p>` },

{ t: "Selectores",
  d: "Un selector elige a qué elementos se aplica una regla. Puedes seleccionar por etiqueta, por clase (.), por id (#), por relación o por estado.",
  p: ["p { } → todas las etiquetas p", ".nota { } → todos los elementos con class=\"nota\"", "#titulo { } → el elemento con id=\"titulo\"", "a:hover { } → cuando el ratón está encima", "nav a { } → enlaces dentro de un nav"],
  live: true,
  c: r`<style>
  p { color: #333; }
  .nota { background: #fde68a; padding: 8px; }
  #titulo { color: royalblue; }
  a:hover { color: tomato; }
  ul li { margin: 4px 0; }
</style>

<h1 id="titulo">Selectores</h1>
<p>Párrafo normal</p>
<p class="nota">Párrafo con clase nota</p>
<ul><li>Uno</li><li>Dos</li></ul>
<a href="#">Pasa el ratón</a>` },

{ t: "Colores, texto y fuentes",
  d: "Puedes dar color con nombres (red), hexadecimal (#ff5733), rgb() o hsl(). Para el texto controlas la fuente, el tamaño, el grosor y la alineación.",
  p: ["color es el color del texto y background el del fondo", "font-family define la fuente; incluye siempre una alternativa", "font-size admite px, rem y em", "line-height mejora la lectura; text-align alinea"],
  live: true,
  c: r`<style>
  body { font-family: Georgia, serif; background: #f5f0e6; }
  h1 { color: #d9531e; text-align: center; }
  p {
    font-size: 1.1rem;
    line-height: 1.6;
    color: hsl(220, 20%, 25%);
  }
  .gran { font-size: 2rem; font-weight: bold; }
</style>

<h1>Texto con estilo</h1>
<p>Un párrafo cómodo de leer.</p>
<p class="gran">Texto grande y en negrita</p>` },

{ t: "El modelo de caja",
  d: "Todo elemento HTML es una caja con cuatro capas: contenido, relleno (padding), borde (border) y margen (margin). Entenderlo es la clave para controlar espacios y tamaños.",
  p: ["padding: espacio entre el contenido y el borde", "margin: espacio fuera del borde", "border: grosor, estilo y color", "box-sizing: border-box hace que width incluya padding y borde"],
  live: true,
  c: r`<style>
  * { box-sizing: border-box; }
  .caja {
    width: 220px;
    padding: 20px;
    border: 4px solid royalblue;
    margin: 16px;
    background: #e0ecff;
    border-radius: 12px;
  }
</style>

<div class="caja">Una caja con padding, borde y margen.</div>
<div class="caja">Otra caja igual.</div>` },

{ t: "Display y posición",
  d: "La propiedad display decide cómo se comporta un elemento: en bloque (ocupa todo el ancho), en línea (se coloca junto al texto) o en línea-bloque. La propiedad position permite colocar elementos con precisión.",
  p: ["block: ocupa toda la línea; inline: fluye con el texto", "inline-block: en línea pero admite ancho y alto", "position: relative / absolute / fixed / sticky", "display: none oculta el elemento"],
  live: true,
  c: r`<style>
  .bloque { display: block; background: #cfe8ff; margin: 4px 0; }
  .linea  { display: inline-block; background: #ffd6c9; padding: 6px; }
  .padre  { position: relative; height: 80px; background: #eee; }
  .hijo   { position: absolute; top: 10px; right: 10px;
            background: tomato; color: white; padding: 6px; }
</style>

<div class="bloque">Soy un bloque</div>
<span class="linea">En línea</span> <span class="linea">En línea</span>
<div class="padre"><div class="hijo">Esquina</div></div>` },

{ t: "Flexbox",
  d: "Flexbox ordena elementos en una fila o en una columna de forma flexible. Es la herramienta ideal para menús, tarjetas y centrar contenido.",
  p: ["display: flex activa el modo flexible en el contenedor", "justify-content alinea en el eje principal; align-items en el cruzado", "gap separa los elementos", "flex-direction: column apila en vertical; flex-wrap permite varias líneas"],
  live: true,
  c: r`<style>
  .fila {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    height: 120px;
    background: #f1f5f9;
    padding: 12px;
  }
  .item { background: royalblue; color: white; padding: 16px; border-radius: 8px; }
</style>

<div class="fila">
  <div class="item">1</div>
  <div class="item">2</div>
  <div class="item">3</div>
</div>` },

{ t: "Grid",
  d: "CSS Grid organiza elementos en filas y columnas a la vez. Es perfecto para el diseño completo de una página o para galerías.",
  p: ["display: grid activa la cuadrícula", "grid-template-columns define las columnas; fr es una fracción del espacio", "repeat(3, 1fr) crea 3 columnas iguales", "gap separa filas y columnas"],
  live: true,
  c: r`<style>
  .galeria {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .celda {
    background: #d9531e;
    color: white;
    padding: 24px;
    text-align: center;
    border-radius: 8px;
  }
  .ancha { grid-column: span 2; background: #1f6feb; }
</style>

<div class="galeria">
  <div class="celda">1</div>
  <div class="celda ancha">2 (ocupa dos columnas)</div>
  <div class="celda">3</div>
  <div class="celda">4</div>
  <div class="celda">5</div>
</div>` },

{ t: "Diseño responsive",
  d: "Un diseño responsive se adapta a cualquier pantalla: móvil, tableta o computador. Se logra con unidades flexibles y con media queries, que aplican estilos solo cuando se cumple una condición.",
  p: ["Añade <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> en el head", "Usa %, rem y max-width en vez de píxeles fijos", "@media (max-width: 600px) { … } afecta a pantallas pequeñas", "Diseña primero para móvil y luego amplía"],
  live: true,
  c: r`<style>
  .tarjetas { display: grid; gap: 10px; grid-template-columns: repeat(3, 1fr); }
  .t { background: #cfe8ff; padding: 20px; border-radius: 8px; text-align: center; }

  @media (max-width: 500px) {
    .tarjetas { grid-template-columns: 1fr; }
    .t { background: #ffd6c9; }
  }
</style>

<p>Reduce el ancho de la ventana (o usa el modo móvil del navegador) para ver el cambio.</p>
<div class="tarjetas">
  <div class="t">A</div><div class="t">B</div><div class="t">C</div>
</div>` },

{ t: "Transiciones, sombras y animaciones",
  d: "CSS permite animar sin JavaScript. Las transiciones suavizan un cambio (por ejemplo, al pasar el ratón) y las animaciones con @keyframes crean movimientos propios.",
  p: ["transition: propiedad duración; suaviza el cambio", "transform: scale(), rotate(), translate()", "box-shadow añade sombras", "@keyframes + animation crean animaciones en bucle"],
  live: true,
  c: r`<style>
  .boton {
    background: #d9531e; color: white; border: 0;
    padding: 12px 20px; border-radius: 10px; font-size: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,.25);
    transition: transform .2s, background .2s;
    cursor: pointer;
  }
  .boton:hover { transform: scale(1.1); background: #b8430f; }

  .pelota {
    width: 40px; height: 40px; border-radius: 50%;
    background: royalblue; margin-top: 20px;
    animation: rebote 1s ease-in-out infinite alternate;
  }
  @keyframes rebote { to { transform: translateY(60px); } }
</style>

<button class="boton">Pasa el ratón</button>
<div class="pelota"></div>` },

{ t: "Proyecto: tarjeta de perfil",
  d: "Combina selectores, modelo de caja, flexbox y transiciones para crear una tarjeta de perfil moderna. Cambia colores, textos y tamaños hasta que sea tuya.",
  p: ["Centra la tarjeta con flexbox en el body", "Usa border-radius y box-shadow para darle profundidad", "Añade un efecto hover con transition", "Pídele al tutor que te sugiera mejoras de diseño"],
  live: true,
  c: r`<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; min-height: 100vh;
    display: flex; justify-content: center; align-items: center;
    background: linear-gradient(135deg, #fde68a, #fca5a5);
    font-family: system-ui, sans-serif;
  }
  .tarjeta {
    width: 260px; padding: 24px; text-align: center;
    background: white; border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,.2);
    transition: transform .25s;
  }
  .tarjeta:hover { transform: translateY(-6px); }
  .avatar {
    width: 80px; height: 80px; margin: 0 auto 12px;
    border-radius: 50%; background: #d9531e; color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem;
  }
  h2 { margin: 0 0 4px; }
  p { margin: 0 0 16px; color: #666; }
  a { background: #1f6feb; color: white; padding: 8px 16px;
      border-radius: 999px; text-decoration: none; }
</style>

<div class="tarjeta">
  <div class="avatar">A</div>
  <h2>Ana López</h2>
  <p>Desarrolladora web</p>
  <a href="#">Contactar</a>
</div>` },
];
