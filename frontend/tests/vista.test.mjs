import test from "node:test";
import assert from "node:assert/strict";
import { construirVistaPrevia, paginaPrincipal, resolverEnlace } from "../js/trabajo/vista.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";

const py = (files) => normalizarProyecto({ files });

test("inlinea CSS y JS enlazados (en subcarpetas) y conserva el resto", () => {
  const p = py({ "web/index.html": '<html><head><title>x</title><link rel="stylesheet" href="css/a.css"><link rel="icon" href="x.ico"></head><body><script src="../lib.js"></script><script src="https://cdn/x.js"></script></body></html>', "web/css/a.css": "body{color:red}", "lib.js": "var a=1</script>" });
  const h = construirVistaPrevia(p, "web/index.html");
  assert.match(h, /<style data-archivo="web\/css\/a\.css">\nbody\{color:red\}/);
  assert.match(h, /<script>\nvar a=1<\\\/script>/);
  assert.match(h, /<link rel="icon" href="x\.ico">/);
  assert.match(h, /<script src="https:\/\/cdn\/x\.js"><\/script>/);
  assert.ok(h.indexOf("parent.postMessage") < h.indexOf("<title>"), "el puente va primero");
});

test("compatibilidad: si la página no enlaza nada, se aplican styles.css y script.js", () => {
  const p = py({ "index.html": "<html><head></head><body><h1>x</h1></body></html>", "styles.css": "h1{color:blue}", "script.js": "console.log(1)" });
  const h = construirVistaPrevia(p, "index.html");
  assert.match(h, /<style data-archivo="styles\.css">[\s\S]*h1\{color:blue\}/);
  assert.match(h, /console\.log\(1\)\n<\/script><\/body>/);
});

test("si ya enlaza, no se duplica", () => {
  const p = py({ "index.html": '<head><link rel="stylesheet" href="styles.css"></head><script src="script.js"></script>', "styles.css": "a{}", "script.js": "x()" });
  const h = construirVistaPrevia(p, "index.html");
  assert.equal(h.match(/a\{\}/g).length, 1);
  assert.equal(h.match(/x\(\)/g).length, 1);
});

test("sin <head> igualmente lleva el puente; HTML vacío no rompe", () => {
  assert.match(construirVistaPrevia(py({ "a.html": "<p>x</p>" }), "a.html"), /^<script>\(function/);
  assert.ok(construirVistaPrevia(py({ "a.html": "" }), "a.html").length > 0);
});

test("paginaPrincipal y resolverEnlace", () => {
  const p = py({ "z.html": "", "docs/index.html": "", "index.html": "", "about.html": "", "x.css": "" });
  assert.equal(paginaPrincipal(p), "index.html");
  assert.equal(paginaPrincipal(p, "about.html"), "about.html");
  assert.equal(paginaPrincipal(p, "x.css"), "index.html");
  assert.equal(paginaPrincipal(py({ "b.html": "", "a/c.html": "" })), "b.html");
  assert.equal(paginaPrincipal(py({ "a.js": "" })), null);
  assert.equal(resolverEnlace(p, "docs/index.html", "../about.html"), "about.html");
  assert.equal(resolverEnlace(p, "index.html", "about.html?x=1#y"), "about.html");
  assert.equal(resolverEnlace(p, "index.html", "https://x.com"), null);
  assert.equal(resolverEnlace(p, "index.html", "x.css"), null);
});

test("REGRESIÓN: CSS y JS con $&, $', $` y $$ se insertan tal cual (antes destruían la página y salía en blanco o con código suelto)", () => {
  const css = "a::before{content:'$&'} b::after{content:\"$'\"} i::after{content:'$`'} u::after{content:'$$ $1 $<x>'}";
  const js = "const precio = '$' + 5; const re = /(a)/; 'x'.replace(re, '$1$&'); console.log(`$` + 'ok');";
  const p = py({ "index.html": "<html><head><title>T</title></head><body><h1>Hola</h1></body></html>", "styles.css": css, "script.js": js });
  const h = construirVistaPrevia(p, "index.html");
  assert.ok(h.includes(css), "el CSS aparece completo y sin alterar");
  assert.ok(h.includes(js), "el JS aparece completo y sin alterar");
  assert.equal(h.split("<h1>Hola</h1>").length, 2, "el contenido de la página no se duplicó");
  assert.equal(h.split("<title>T</title>").length, 2, "tampoco el encabezado");
  // lo mismo cuando la página SÍ enlaza los archivos
  const q = py({ "index.html": '<head><link rel="stylesheet" href="styles.css"></head><body><script src="script.js"></script></body>', "styles.css": css, "script.js": js });
  const g = construirVistaPrevia(q, "index.html");
  assert.ok(g.includes(css) && g.includes(js));
  assert.equal(g.split("<head>").length, 2);
});

test("sin </head> ni </body> los archivos por defecto se añaden igual", () => {
  const p = py({ "index.html": "<h1>x</h1>", "styles.css": "h1{content:'$&'}", "script.js": "var a='$\\'';" });
  const h = construirVistaPrevia(p, "index.html");
  assert.ok(h.includes("h1{content:'$&'}") && h.includes("var a='$\\'';"));
  assert.equal(h.split("<h1>x</h1>").length, 2);
});

import { paginaQueUsa } from "../js/trabajo/vista.js";
test("paginaQueUsa: por <script src>, por script.js de siempre, y null si ninguna página lo usa", () => {
  const p = py({ "index.html": '<script src="js/app.js"></script>', "otra.html": '<script src="../x.js"></script>', "js/app.js": "", "x.js": "", "libre.js": "", "web/p.html": "<p>x</p>", "web/script.js": "" });
  assert.equal(paginaQueUsa(p, "js/app.js"), "index.html");
  assert.equal(paginaQueUsa(p, "x.js"), "otra.html", "../ no puede salir del proyecto: se resuelve en la raíz");
  assert.equal(paginaQueUsa(p, "libre.js"), null);
  assert.equal(paginaQueUsa(p, "web/script.js"), "web/p.html", "script.js junto a una página sin scripts");
  const q = py({ "index.html": '<html><script src="otro.js"></script></html>', "script.js": "", "otro.js": "" });
  assert.equal(paginaQueUsa(q, "script.js"), null, "si la página enlaza otro script, script.js ya no se asume");
  assert.equal(paginaQueUsa(q, "otro.js"), "index.html");
  const r = py({ "a.html": '<script src="s.js"></script>', "index.html": '<script src="s.js"></script>', "s.js": "" });
  assert.equal(paginaQueUsa(r, "s.js"), "index.html", "prefiere index.html");
});

test("vista previa con imágenes: atributos, CSS url(), favicon, SVG de texto y img.src desde JS", async () => {
  const { normalizarProyecto } = await import("../js/trabajo/almacen.js");
  const h = "e".repeat(64);
  const py = normalizarProyecto({ files: {
    "index.html": '<html><head><link rel="icon" href="img/logo.png"><link rel="stylesheet" href="css/estilo.css"></head><body><img src="img/logo.png"><img src=\'icono.svg\'><img src="https://x.com/a.png"><script src="js/app.js"></script></body></html>',
    "css/estilo.css": "body { background: url('../img/logo.png') } .x { background: url(nada.png) }",
    "js/app.js": "const i = new Image(); i.src = 'img/logo.png';",
    "img/logo.png": `ccimg:v1:${h}:image/png:10`,
    "icono.svg": "<svg xmlns='http://www.w3.org/2000/svg'/>",
  } });
  const imagenes = new Map([[h, "data:image/png;base64,AAAA"]]); // en la página real es un enlace firmado
  const html = construirVistaPrevia(py, "index.html", { imagenes });
  assert.equal((html.match(/data:image\/png;base64,AAAA/g) || []).length >= 4, true, "img, favicon, css y mapa del JS");
  assert.match(html, /<img src='?"?data:image\/svg\+xml;base64,/);
  assert.match(html, /https:\/\/x\.com\/a\.png/);
  assert.match(html, /url\(nada\.png\)/);
  assert.ok(!html.includes("ccimg:"), "el marcador nunca llega a la página");
  for (const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) assert.doesNotThrow(() => new Function(m[1]), "el script insertado es JavaScript válido");
  const sinImg = construirVistaPrevia(normalizarProyecto({ files: { "index.html": "<p>hola</p>" } }), "index.html");
  assert.ok(!sinImg.includes("MutationObserver"), "sin imágenes no se añade nada");
});

test("vista previa: videos, audio y enlaces a PDF usan los enlaces firmados", async () => {
  const { normalizarProyecto } = await import("../js/trabajo/almacen.js");
  const v = "1".repeat(64); const d = "2".repeat(64);
  const py = normalizarProyecto({ files: {
    "index.html": '<video src="media/clip.mp4" controls></video><audio><source src="media/clip.mp4"></audio><a href="docs/guia.pdf">Guía</a><a href="otra.html">otra</a>',
    "media/clip.mp4": `ccbin:v1:${v}:video/mp4:5000000`, "docs/guia.pdf": `ccbin:v1:${d}:application/pdf:900`, "otra.html": "x",
  } });
  const enlaces = new Map([[v, "http://h/api/trabajo/archivos/p/AAA"], [d, "http://h/api/trabajo/archivos/p/BBB"]]);
  const html = construirVistaPrevia(py, "index.html", { imagenes: enlaces });
  assert.equal((html.match(/p\/AAA/g) || []).length, 2);
  assert.match(html, /<a href="http:\/\/h\/api\/trabajo\/archivos\/p\/BBB" target="_blank" rel="noopener">/);
  assert.match(html, /<a href="otra\.html">/);
});

test("vista previa: rutas a node_modules usan jsDelivr con la versión instalada", async () => {
  const { normalizarProyecto } = await import("../js/trabajo/almacen.js");
  const py = normalizarProyecto({ files: {
    "package.json": JSON.stringify({ dependencies: { bootstrap: "^5.3.3" } }),
    "index.html": '<link rel="stylesheet" href="node_modules/bootstrap/dist/css/bootstrap.min.css"><script src="./node_modules/bootstrap/dist/js/bootstrap.bundle.min.js"></script><script src="node_modules/jquery/dist/jquery.js"></script>',
  } });
  const html = construirVistaPrevia(py, "index.html");
  assert.match(html, /href="https:\/\/cdn\.jsdelivr\.net\/npm\/bootstrap@5\.3\.3\/dist\/css\/bootstrap\.min\.css"/);
  assert.match(html, /src="https:\/\/cdn\.jsdelivr\.net\/npm\/bootstrap@5\.3\.3\/dist\/js\/bootstrap\.bundle\.min\.js"/);
  assert.match(html, /Falta instalar: jquery/);
});
