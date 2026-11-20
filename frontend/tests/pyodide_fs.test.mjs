// Con el Python real del navegador (Pyodide incluido en vendor/): ejecutar o arrancar un servidor dos veces
// seguidas desde una subcarpeta (cd backend && fastapi dev app.py) no debe fallar con «[object Object]» (EBUSY).
import test from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const vendor = fileURLToPath(new URL("../vendor/pyodide/", import.meta.url));

test("se puede volver a copiar el proyecto aunque Python esté dentro de una subcarpeta", { skip: !existsSync(vendor + "pyodide.asm.wasm"), timeout: 120000 }, async () => {
  await import(vendor + "pyodide.js");
  const pyo = await globalThis.loadPyodide({ indexURL: vendor });
  const { borrarEnPyodide, escribirEnPyodide, textoError } = await import("../js/trabajo/ejecucion.js");
  const py = { files: { "Finanbot/backend/app.py": "x = 1" }, folders: ["Finanbot", "Finanbot/backend"] };
  borrarEnPyodide(pyo); escribirEnPyodide(pyo, py);
  pyo.FS.chdir("/workspace/Finanbot/backend");          // como deja un servidor arrancado en backend/
  borrarEnPyodide(pyo); escribirEnPyodide(pyo, py);     // segunda vez: antes daba EBUSY
  assert.equal(pyo.FS.readFile("/workspace/Finanbot/backend/app.py", { encoding: "utf8" }), "x = 1");
  let error;
  try { pyo.FS.readFile("/no/existe"); } catch (e) { error = e; }
  assert.match(textoError(error), /OSError: \[Errno 2\] No such file or directory/);
});
