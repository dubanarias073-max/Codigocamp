// Cada import con nombre existe como export en su módulo (si falta uno, la página entera no carga: pasó con Perfil y FONDOS)
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs"; import path from "node:path"; import { fileURLToPath } from "node:url";
const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
test("todos los import { … } apuntan a exports que existen", () => {
const archivos = [];
(function rec(d) { for (const f of fs.readdirSync(d)) { const r = path.join(d, f); if (f === "vendor" || f === "node_modules") continue; if (fs.statSync(r).isDirectory()) rec(r); else if (/\.(m?js)$/.test(f)) archivos.push(r); } })(path.join(raiz, "js"));
const exportsDe = new Map();
const leerExports = (r) => {
  if (exportsDe.has(r)) return exportsDe.get(r);
  const s = fs.readFileSync(r, "utf8"); const set = new Set();
  for (const m of s.matchAll(/^export\s+(?:async\s+)?(?:function\*?|const|let|var|class)\s+([\w$]+)/gm)) set.add(m[1]);
  for (const m of s.matchAll(/^export\s*\{([^}]+)\}/gm)) for (const x of m[1].split(",")) set.add(x.trim().split(/\s+as\s+/).pop());
  if (/^export\s+default/m.test(s)) set.add("default");
  for (const m of s.matchAll(/^export\s*\*\s*from/gm)) set.add("*");
  exportsDe.set(r, set); return set;
};
const malos = [];
for (const a of archivos) {
  const s = fs.readFileSync(a, "utf8");
  for (const m of s.matchAll(/import\s*\{([^}]+)\}\s*from\s*["']([^"']+)["']/g)) {
    let ruta = m[2]; if (!ruta.endsWith(".js")) continue;
    const destino = ruta.startsWith("/") ? path.join(raiz, ruta) : path.resolve(path.dirname(a), ruta);
    if (!fs.existsSync(destino)) { malos.push(`falta ${ruta} (en ${path.relative(raiz, a)})`); continue; }
    const ex = leerExports(destino); if (ex.has("*")) continue;
    for (const n of m[1].split(",").map((x) => x.trim().split(/\s+as\s+/)[0]).filter(Boolean)) if (!ex.has(n)) malos.push(`${path.relative(raiz, a)}: ${ruta} no exporta «${n}»`);
  }
}
assert.ok(archivos.length > 50);
  assert.deepEqual(malos, []);
});
