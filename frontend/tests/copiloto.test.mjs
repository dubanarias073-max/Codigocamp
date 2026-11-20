import { test } from "node:test";
import assert from "node:assert/strict";
import { aplicarCambio, contextoProyecto, extraerCambios, validarCambios } from "../js/trabajo/copiloto.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";

test("extraer el bloque cc-cambios de la respuesta", () => {
  const r = 'Agrego el botón.\n```cc-cambios\n{"resumen": "Modo oscuro", "cambios": [{"accion": "escribir", "ruta": "css/estilos.css", "contenido": "body{}\\n"}]}\n```\nListo.';
  const x = extraerCambios(r);
  assert.equal(x.texto, "Agrego el botón.\n\nListo.");
  assert.equal(x.resumen, "Modo oscuro");
  assert.equal(x.cambios[0].ruta, "css/estilos.css");
  assert.equal(extraerCambios("Solo explico").cambios, null);
  assert.match(extraerCambios("```cc-cambios\n{roto\n```").error, /formato/);
});

test("validar y aplicar cambios (con deshacer)", () => {
  const py = normalizarProyecto({ files: { "index.html": "<h1>Hola</h1>", "logo.png": "ccbin:v1:" + "a".repeat(64) + ":image/png:10", "viejo.js": "x" } });
  const { validos, errores } = validarCambios([
    { accion: "escribir", ruta: "index.html", contenido: "<h1>Hola mundo</h1>" },
    { accion: "escribir", ruta: "js/nuevo.js", contenido: "console.log(1)" },
    { accion: "borrar", ruta: "viejo.js" },
    { accion: "escribir", ruta: "logo.png", contenido: "x" },
    { accion: "escribir", ruta: "../fuera.txt", contenido: "x" },
    { accion: "escribir", ruta: ".git/config", contenido: "x" },
    { accion: "borrar", ruta: "no-existe.txt" },
  ], py);
  assert.deepEqual(validos.map((v) => [v.accion, v.ruta, v.nuevo]), [["escribir", "index.html", false], ["escribir", "js/nuevo.js", true], ["borrar", "viejo.js", false]]);
  assert.equal(errores.length, 4);
  const hechos = validos.map((c) => aplicarCambio(py, c));
  assert.ok(hechos.every((h) => h.ok));
  assert.equal(py.files["index.html"], "<h1>Hola mundo</h1>");
  assert.equal(py.files["js/nuevo.js"], "console.log(1)");
  assert.equal(py.files["viejo.js"], undefined);
  hechos.reverse().forEach((h) => h.deshacer());
  assert.equal(py.files["index.html"], "<h1>Hola</h1>");
  assert.equal(py.files["js/nuevo.js"], undefined);
  assert.equal(py.files["viejo.js"], "x");
});

test("contexto del proyecto para la IA (con presupuesto)", () => {
  const py = normalizarProyecto({ files: { "src/App.jsx": "export default 1", "src/main.jsx": "import App", "package.json": "{}", "node_modules/x/i.js": "no", "img.png": "ccbin:v1:" + "b".repeat(64) + ":image/png:3" } });
  const c = contextoProyecto(py, { abierto: "src/App.jsx", copiloto: true });
  assert.equal(c.archivo.ruta, "src/App.jsx");
  assert.ok(c.archivos.includes("img.png") && !c.archivos.some((r) => r.startsWith("node_modules")));
  assert.deepEqual(c.extra.map((e) => e.ruta), ["src/main.jsx", "package.json"]);
  assert.equal(contextoProyecto(py, { abierto: "src/App.jsx" }).extra, undefined, "sin copiloto no se manda el resto del proyecto");
});
