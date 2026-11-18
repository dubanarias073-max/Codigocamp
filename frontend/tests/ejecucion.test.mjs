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

// ---- Pyodide: sistema de archivos falso que se comporta como Emscripten (readdir/stat lanzan si no existe) ----
import { borrarEnPyodide, escribirEnPyodide, leerDePyodide } from "../js/trabajo/ejecucion.js";
function fsEmscripten() {
  const nodos = new Map([["/", { dir: true }]]);
  const falta = (p) => Object.assign(new Error(`ENOENT: ${p}`), { name: "ErrnoError" });
  const hijos = (p) => [...nodos.keys()].filter((k) => k !== p && k.startsWith(p === "/" ? "/" : p + "/") && !k.slice(p === "/" ? 1 : p.length + 1).includes("/"));
  const FS = {
    stat: (p) => { if (!nodos.has(p)) throw falta(p); return { mode: nodos.get(p).dir ? 1 : 2 }; },
    isDir: (m) => m === 1,
    mkdir: (p) => { if (nodos.has(p)) throw new Error("EEXIST"); if (!nodos.has(p.slice(0, p.lastIndexOf("/")) || "/")) throw falta(p); nodos.set(p, { dir: true }); },
    readdir: (p) => { if (!nodos.has(p)) throw falta(p); return [".", "..", ...hijos(p).map((k) => k.slice(k.lastIndexOf("/") + 1))]; },
    writeFile: (p, t) => nodos.set(p, { dir: false, t }),
    readFile: (p) => { if (!nodos.has(p)) throw falta(p); return nodos.get(p).t; },
    unlink: (p) => { if (!nodos.has(p)) throw falta(p); nodos.delete(p); },
    rmdir: (p) => { if (hijos(p).length) throw new Error("ENOTEMPTY"); nodos.delete(p); },
  };
  return { pyo: { FS }, nodos };
}

test("PYTHON, primera ejecución: /workspace aún no existe y no debe fallar (antes lanzaba ENOENT y Python nunca arrancaba)", () => {
  const { pyo, nodos } = fsEmscripten();
  assert.doesNotThrow(() => borrarEnPyodide(pyo));
  assert.ok(nodos.has("/workspace"));
  const py = normalizarProyecto({ files: { "main.py": "print(1)", "pkg/util.py": "x = 2" } });
  escribirEnPyodide(pyo, py);
  assert.equal(nodos.get("/workspace/pkg/util.py").t, "x = 2");
  const leido = leerDePyodide(pyo);
  assert.deepEqual(leido.files, { "main.py": "print(1)", "pkg/util.py": "x = 2" });
  assert.deepEqual(leido.folders, ["pkg"]);
});

test("PYTHON: ejecutar varias veces seguidas (vaciar, escribir, leer, vaciar) y leer sin /workspace no rompe", () => {
  const { pyo, nodos } = fsEmscripten();
  assert.deepEqual(leerDePyodide(pyo), { files: {}, folders: [] });
  const py = normalizarProyecto({ files: { "a.py": "1", "d/b.py": "2" } });
  for (let i = 0; i < 3; i += 1) {
    borrarEnPyodide(pyo); escribirEnPyodide(pyo, py);
    nodos.set("/workspace/salida.txt", { dir: false, t: `vuelta ${i}` });
    assert.equal(leerDePyodide(pyo).files["salida.txt"], `vuelta ${i}`);
  }
  borrarEnPyodide(pyo);
  assert.deepEqual(leerDePyodide(pyo), { files: {}, folders: [] });
});
