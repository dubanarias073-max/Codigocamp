import test from "node:test";
import assert from "node:assert/strict";
import { buscarEnProyecto, reemplazarEnProyecto, patron } from "../js/trabajo/buscar.js";
import { puntuar, filtrar } from "../js/trabajo/paleta.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { ejecutarGit, calcularEstado } from "../js/trabajo/git.js";

test("puntuar/filtrar: búsqueda difusa como Ctrl+P (prefiere el nombre del archivo y letras seguidas)", () => {
  assert.equal(puntuar("src/App.jsx", "xyz"), null);
  assert.ok(puntuar("src/App.jsx", "apjs"));
  const r = filtrar([{ etiqueta: "src/components/Boton.jsx" }, { etiqueta: "src/App.jsx" }, { etiqueta: "apps/legacy/index.js" }], "app");
  assert.equal(r[0].etiqueta, "src/App.jsx");
  assert.equal(filtrar([{ etiqueta: "a" }], "").length, 1);
});

test("buscar en archivos: texto, mayúsculas, palabra completa, regex, incluir/excluir y archivos binarios", () => {
  const py = normalizarProyecto({ files: {
    "src/a.js": "const total = 1;\nconsole.log(Total);\nlet totales = 2;",
    "src/b.py": "total = 3",
    "node_modules/x/i.js": "total",
    "img.png": "ccbin:v1:" + "a".repeat(64) + ":image/png:10",
  } });
  assert.equal(buscarEnProyecto(py, "total").total, 4, "sin mayúsculas, sin node_modules");
  assert.equal(buscarEnProyecto(py, "total", { mayusculas: true }).total, 3);
  assert.equal(buscarEnProyecto(py, "total", { palabra: true }).total, 3);
  assert.equal(buscarEnProyecto(py, "tota\\w+", { regex: true }).total, 4);
  assert.deepEqual(buscarEnProyecto(py, "total", { incluir: "*.py" }).archivos.map((a) => a.ruta), ["src/b.py"]);
  assert.equal(buscarEnProyecto(py, "total", { excluir: "" }).archivos.length, 3);
  const c = buscarEnProyecto(py, "Total", { mayusculas: true }).archivos[0].coincidencias[0];
  assert.deepEqual([c.linea, c.col, c.largo], [2, 13, 5]);
  assert.match(patron("(", { regex: true }).error, /no válida/);
});

test("reemplazar en archivos y deshacer", () => {
  const py = normalizarProyecto({ files: { "a.js": "var x = 1; var y = 2;", "b.js": "var z;" } });
  const { cambiados, total } = reemplazarEnProyecto(py, "var", "let", { palabra: true });
  assert.equal(total, 3);
  assert.equal(py.files["a.js"], "let x = 1; let y = 2;");
  Object.assign(py.files, cambiados);
  assert.equal(py.files["b.js"], "var z;");
  reemplazarEnProyecto(py, "(\\w) = (\\d)", "$2 = $1", { regex: true });
  assert.equal(py.files["a.js"], "var 1 = x; var 2 = y;", "grupos de la expresión regular");
});

test("órdenes de Git que usa el panel: add, restore --staged (uno y todos), restore y commit", () => {
  const py = normalizarProyecto({ files: { "a.txt": "1", "b.txt": "2" } });
  ejecutarGit(py, ["init"]);
  ejecutarGit(py, ["add", "."]);
  assert.equal(ejecutarGit(py, ["commit", "-m", "inicio"]).error, false);
  py.files["a.txt"] = "cambiado";
  py.files["c.txt"] = "nuevo";
  ejecutarGit(py, ["add", "."]);
  assert.equal(calcularEstado(py).preparados.length, 2);
  ejecutarGit(py, ["restore", "--staged", "c.txt"]);
  assert.equal(calcularEstado(py).preparados.length, 1);
  ejecutarGit(py, ["restore", "--staged", "."]);
  assert.equal(calcularEstado(py).preparados.length, 0);
  ejecutarGit(py, ["restore", "a.txt"]);
  assert.equal(py.files["a.txt"], "1", "descartar vuelve al último commit");
});
