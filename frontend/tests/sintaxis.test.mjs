// Ningún módulo del navegador tiene errores de sintaxis (uno solo deja la página en blanco)
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs"; import path from "node:path"; import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "js");
test("todos los módulos de js/ compilan", () => {
  const archivos = [];
  (function rec(d) { for (const f of fs.readdirSync(d)) { const r = path.join(d, f); if (f === "vendor" || f === "lecciones") continue; if (fs.statSync(r).isDirectory()) rec(r); else if (/\.m?js$/.test(f)) archivos.push(r); } })(raiz);
  const malos = [];
  for (const a of archivos) {
    const s = fs.readFileSync(a, "utf8");
    if (!/^\s*(import|export)\b/m.test(s)) continue;   // scripts clásicos (i18n.js, tema.js…) no son módulos
    const r = spawnSync(process.execPath, ["--experimental-default-type=module", "--check", a], { encoding: "utf8" });
    if (r.status) malos.push(path.relative(raiz, a) + ": " + (r.stderr.split("\n").find((l) => /Error/.test(l)) || "error"));
  }
  assert.deepEqual(malos, []);
});
