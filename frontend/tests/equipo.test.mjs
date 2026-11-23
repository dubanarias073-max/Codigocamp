// La carpeta del computador o celular abierta en Trabajo con el Conector: disco por el Conector, estado de Git del equipo.
import { test } from "node:test";
import assert from "node:assert/strict";
import { DiscoConector, base64ABytes, bytesABase64, leerEstadoGit } from "../js/trabajo/equipo.js";
import { clasificarCambios } from "../js/trabajo/gitequipo.js";
import { Sincronizador } from "../js/trabajo/carpeta.js";

/** Un equipo falso: guarda los archivos en memoria y responde como el Conector. */
function equipoFalso(inicial = {}) {
  const archivos = new Map(Object.entries(inicial).map(([r, t]) => [r, { bytes: new TextEncoder().encode(t), modificado: 1 }]));
  let reloj = 10;
  const llamadas = [];
  const fs = async (_eq, accion, d) => {
    llamadas.push(accion);
    if (accion === "listar") return { archivos: [...archivos].map(([ruta, a]) => ({ ruta, tamano: a.bytes.length, modificado: a.modificado })), carpetas: [] };
    if (accion === "leer_varios") return { archivos: Object.fromEntries(d.rutas.map((r) => [r, r.includes("virus") ? { error: "🛡️ virus", virus: true } : { b64: bytesABase64(archivos.get(r).bytes) }])) };
    if (accion === "leer") return { b64: bytesABase64(archivos.get(d.ruta).bytes) };
    if (accion === "escribir") { archivos.set(d.ruta, { bytes: base64ABytes(d.b64), modificado: ++reloj }); return { tamano: archivos.get(d.ruta).bytes.length, modificado: reloj }; }
    if (accion === "borrar") { archivos.delete(d.ruta); return {}; }
    if (accion === "leer_parte") { const b = archivos.get(d.ruta).bytes; const p = b.slice(d.desde, d.desde + 8 * 1024 * 1024); return { b64: bytesABase64(p), total: b.length, fin: d.desde + p.length >= b.length }; }
    if (accion === "escribir_parte") { const prev = d.desde ? archivos.get(d.ruta + ".tmp") : new Uint8Array(0); const nuevo = new Uint8Array(prev.length + base64ABytes(d.b64).length); nuevo.set(prev); nuevo.set(base64ABytes(d.b64), prev.length); if (d.fin) { archivos.set(d.ruta, { bytes: nuevo, modificado: ++reloj }); return { tamano: nuevo.length, modificado: reloj }; } archivos.set(d.ruta + ".tmp", nuevo); return {}; }
    return {};
  };
  return { archivos, fs, llamadas, texto: (r) => new TextDecoder().decode(archivos.get(r).bytes) };
}

test("base64 de ida y vuelta (también binarios grandes)", () => {
  const b = new Uint8Array(200000).map((_, i) => i % 256);
  assert.deepEqual(base64ABytes(bytesABase64(b)), b);
});

test("abrir la carpeta del equipo: el proyecto queda igual y se lee en pocos viajes", async () => {
  const eq = equipoFalso({ "main.py": "print(1)\n", "src/a.js": "x\n", "virus.bin": "malo" });
  const disco = new DiscoConector({ id: 1, equipo: "PC" }, "/home/ana/demo", eq.fs);
  const avisos = [];
  disco.alVirus = (ruta) => avisos.push(ruta);
  let py = { files: {}, folders: [] };
  const s = new Sincronizador({ disco, proyecto: () => py });
  await s.vincular("carpeta");
  assert.deepEqual(Object.keys(py.files).sort(), ["main.py", "src/a.js"]);
  assert.deepEqual(avisos, ["virus.bin"]);   // el antivirus del equipo lo bloqueó: no entra al proyecto
  assert.equal(eq.llamadas.filter((x) => x === "leer").length, 0);
  // editar en CódigoCamp → se guarda en el equipo
  py.files["main.py"] = "print(2)\n";
  await s.sincronizar();
  assert.equal(eq.texto("main.py"), "print(2)\n");
  // un comando en el equipo crea un archivo → aparece en el proyecto
  eq.archivos.set("nuevo.txt", { bytes: new TextEncoder().encode("hola"), modificado: 99 });
  await s.sincronizar();
  assert.equal(py.files["nuevo.txt"], "hola");
});

test("estado de Git del equipo con letras como un editor", () => {
  const e = leerEstadoGit("## main...origin/main [ahead 1]\0M  listo.py\0 M cambiado.js\0?? nuevo.css\0UU choque.txt\0R  b.js\0a.js\0");
  assert.equal(e.rama, "main"); assert.equal(e.adelante, 1);
  const c = clasificarCambios(e.cambios);
  assert.deepEqual(c.preparados.map((x) => x.ruta + x.letra), ["listo.pyM", "b.jsR"]);
  assert.deepEqual(c.sinPreparar.map((x) => x.ruta + x.letra), ["cambiado.jsM", "nuevo.cssU"]);
  assert.deepEqual(c.conflictos.map((x) => x.ruta), ["choque.txt"]);
  assert.equal(c.mapa.get("nuevo.css"), "U");
  // el repositorio empieza más arriba que la carpeta abierta
  const sub = clasificarCambios(leerEstadoGit("## main\0 M web/app.js\0 M otro/x.js\0").cambios, "web/");
  assert.deepEqual(sub.sinPreparar.map((x) => x.ruta), ["app.js"]);
});

test("archivos grandes (más de 8 MB) viajan por partes, sin límite de 25 MB", async () => {
  const eq = equipoFalso();
  const disco = new DiscoConector({ id: 1, equipo: "PC" }, "/home/ana/demo", async (e, accion, d) => {
    if (accion === "leer") { const b = eq.archivos.get(d.ruta)?.bytes; if (b && b.length > 1024) { const err = new Error("grande"); err.grande = true; throw err; } }
    return eq.fs(e, accion, d);
  });
  const grande = new Uint8Array(20 * 1024 * 1024).map((_, i) => i % 251);
  const r = await disco.escribir("video.mp4", new Blob([grande]));
  assert.equal(r.tamano, grande.length);
  assert.equal(eq.llamadas.filter((x) => x === "escribir_parte").length, 3);
  const vuelta = new Uint8Array(await (await disco.abrir("video.mp4")).arrayBuffer());
  assert.equal(vuelta.length, grande.length);
  assert.equal(vuelta[12345678], grande[12345678]);
});
