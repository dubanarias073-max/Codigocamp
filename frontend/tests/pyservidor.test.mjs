import { test } from "node:test";
import assert from "node:assert/strict";
import { importsDe, necesitaServidor, archivosParaServidor } from "../js/trabajo/pyservidor.js";

const proyecto = (files) => ({ files, folders: [] });

test("importsDe encuentra los módulos de primer nivel", () => {
  const s = importsDe("import os, sys as s\nfrom cv2 import imread\nimport numpy.linalg\n  from x.y import z\n# import falso");
  assert.deepEqual([...s].sort(), ["cv2", "numpy", "os", "sys", "x"]);
});

test("necesitaServidor sigue los .py locales", () => {
  const py = proyecto({ "app/main.py": "import util\nprint(1)", "app/util.py": "import psutil", "otro.py": "import cv2" });
  assert.equal(necesitaServidor(py, "app/main.py", new Set(["psutil"])), "psutil");
  assert.equal(necesitaServidor(py, "app/main.py", new Set(["cv2"])), null);
  assert.equal(necesitaServidor(py, "app/main.py", new Set()), null);
});

test("un archivo local con el mismo nombre gana al paquete del servidor", () => {
  const py = proyecto({ "main.py": "import psutil", "psutil.py": "x = 1" });
  assert.equal(necesitaServidor(py, "main.py", new Set(["psutil"])), null);
});

test("archivosParaServidor manda primero el programa y deja fuera node_modules", () => {
  const py = proyecto({ "z.txt": "z", "src/main.py": "print(1)", "node_modules/a/i.js": "x", "src/datos.csv": "a,b" });
  const rutas = archivosParaServidor(py, "src/main.py").map((a) => a.ruta);
  assert.equal(rutas[0], "src/main.py");
  assert.ok(rutas.includes("src/datos.csv") && rutas.includes("z.txt"));
  assert.ok(!rutas.some((r) => r.includes("node_modules")));
});
