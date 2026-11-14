import test from "node:test";
import assert from "node:assert/strict";
import { aplicarCambios, diferencias } from "../js/trabajo/ejecucion.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";

test("aplicarCambios crea (con carpetas), modifica y borra lo que hizo el programa", () => {
  const py = normalizarProyecto({ files: { "a.txt": "1", "viejo.txt": "x", "d/x.txt": "y" } });
  const hubo = aplicarCambios(py, { files: { "a.txt": "2", "salida/r.txt": "nuevo", "viejo.txt": null }, folders: ["salida"], carpetasBorradas: ["d"] });
  assert.equal(hubo, true);
  assert.equal(py.files["a.txt"], "2");
  assert.equal(py.files["salida/r.txt"], "nuevo");
  assert.ok(!("viejo.txt" in py.files) && !("d/x.txt" in py.files));
  assert.ok(py.folders.includes("salida") && !py.folders.includes("d"));
});

test("aplicarCambios ignora rutas inválidas y no marca cambio si no hubo", () => {
  const py = normalizarProyecto({ files: { "a.txt": "1" } });
  assert.equal(aplicarCambios(py, { files: { "../x": "mal", "con espacio.txt": "mal" }, folders: [] }), false);
  assert.deepEqual(Object.keys(py.files), ["a.txt"]);
  assert.equal(aplicarCambios(py, { files: {}, folders: [] }), false);
});

test("diferencias (Python): detecta archivos nuevos, cambiados, borrados y carpetas", () => {
  const antes = { files: { "a.py": "1", "b.py": "2", "d/c.py": "3" }, folders: ["d"] };
  const despues = { files: { "a.py": "1", "b.py": "cambiado", "nuevo.txt": "n" }, folders: ["salida"] };
  assert.deepEqual(diferencias(antes, despues), {
    files: { "b.py": "cambiado", "nuevo.txt": "n", "d/c.py": null }, folders: ["salida"], carpetasBorradas: ["d"],
  });
  assert.deepEqual(diferencias(antes, antes), { files: {}, folders: [], carpetasBorradas: [] });
});
