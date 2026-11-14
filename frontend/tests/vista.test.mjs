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
