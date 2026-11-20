import test from "node:test";
import assert from "node:assert/strict";
import { Sincronizador, soporteCarpeta, nombreConflicto, valorDeBytes } from "../js/trabajo/carpeta.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { esMarcador, leerMarcador } from "../js/trabajo/archivos.js";

const enc = new TextEncoder();
const dec = new TextDecoder("utf-8", { ignoreBOM: true });
const PNG = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 5, 5, 5]);

/** Disco falso en memoria con la misma forma que DiscoNavegador. */
class DiscoMemoria {
  constructor(archivos = {}) {
    this.f = new Map();
    this.dirs = new Set();
    this.reloj = 1;
    this.lecturas = 0;
    for (const [r, v] of Object.entries(archivos)) this.poner(r, v);
  }
  poner(ruta, v) { this.f.set(ruta, { bytes: typeof v === "string" ? enc.encode(v) : v, modificado: this.reloj++ }); }
  texto(ruta) { return this.f.has(ruta) ? dec.decode(this.f.get(ruta).bytes) : undefined; }
  async listar() {
    const carpetas = new Set(this.dirs);
    for (const r of this.f.keys()) { const p = r.split("/"); for (let i = 1; i < p.length; i += 1) carpetas.add(p.slice(0, i).join("/")); }
    return { archivos: [...this.f].filter(([r]) => !r.split("/").includes("node_modules")).map(([ruta, x]) => ({ ruta, tamano: x.bytes.length, modificado: x.modificado })), carpetas: [...carpetas] };
  }
  async leer(ruta) { this.lecturas += 1; if (!this.f.has(ruta)) throw new Error("no existe"); return this.f.get(ruta).bytes; }
  async abrir(ruta) { this.lecturas += 1; if (!this.f.has(ruta)) throw new Error("no existe"); return new Blob([this.f.get(ruta).bytes]); }
  async escribir(ruta, datos) { this.poner(ruta, datos instanceof Blob ? new Uint8Array(await datos.arrayBuffer()) : datos); const x = this.f.get(ruta); return { tamano: x.bytes.length, modificado: x.modificado }; }
  async crearCarpeta(ruta) { this.dirs.add(ruta); }
  async borrar(ruta) { this.f.delete(ruta); }
}

function montar(files, disco, extra = {}) {
  const py = normalizarProyecto({ files });
  const avisos = [];
  const cambios = [];
  const subidas = [];
  const s = new Sincronizador({
    disco, proyecto: () => py, alCambiar: (i) => cambios.push(i), alAviso: (a) => avisos.push(a),
    subirArchivo: async (d, o) => { subidas.push(o.nombre); const b = d instanceof Blob ? new Uint8Array(await d.arrayBuffer()) : d; return (await valorDeBytes(o.nombre, b.length > 1024 * 1024 ? { blob: new Blob([b]), cabeza: b.slice(0, 64) } : b)).valor; },
    leerArchivo: async () => new Blob([PNG]), ...extra,
  });
  return { py, s, avisos, cambios, subidas };
}

test("soporte: Chrome sí; Firefox, Safari, móvil, Brave y sin HTTPS explican por qué no", () => {
  const ua = { chrome: "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/130.0 Safari/537.36", ff: "Mozilla/5.0 (Windows NT 10.0; rv:132.0) Gecko/20100101 Firefox/132.0",
    safari: "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15", android: "Mozilla/5.0 (Linux; Android 14) Chrome/130.0 Mobile Safari/537.36" };
  const win = (picker, extra = {}) => ({ showDirectoryPicker: picker ? () => {} : undefined, isSecureContext: true, ...extra });
  assert.equal(soporteCarpeta({ win: win(true), nav: { userAgent: ua.chrome } }).disponible, true);
  assert.match(soporteCarpeta({ win: win(false), nav: { userAgent: ua.ff } }).motivo, /Firefox/);
  assert.match(soporteCarpeta({ win: win(false), nav: { userAgent: ua.safari } }).motivo, /Safari/);
  assert.match(soporteCarpeta({ win: win(false), nav: { userAgent: ua.android } }).motivo, /celulares/);
  assert.match(soporteCarpeta({ win: win(false), nav: { userAgent: ua.chrome, brave: {} } }).consejo, /brave:\/\/flags/);
  assert.match(soporteCarpeta({ win: win(true, { isSecureContext: false }), nav: { userAgent: ua.chrome } }).motivo, /HTTPS/);
  assert.match(soporteCarpeta({ win: win(false), nav: { userAgent: ua.ff } }).consejo, /zip/i);
});

test("vincular «carpeta»: el proyecto pasa a ser la carpeta; omite lo que no maneja sin tocarlo", async () => {
  const disco = new DiscoMemoria({ "index.html": "﻿<h1>Hola</h1>\r\n", "img/logo.png": PNG, "Mi foto.png": PNG, "raro?.png": PNG, "enorme.bin": new Uint8Array(3000), "node_modules/a.js": "x" });
  const { py, s, subidas } = montar({ "viejo.txt": "se va" }, disco, { maxArchivo: 2000 });
  const r = await s.vincular("carpeta");
  assert.deepEqual(Object.keys(py.files).sort(), ["Mi foto.png", "img/logo.png", "index.html"]);
  assert.equal(py.files["index.html"], "<h1>Hola</h1>\n");
  assert.ok(esMarcador(py.files["img/logo.png"]));
  assert.equal(subidas.length, 2);
  assert.ok(r.omitidos.has("raro?.png") && r.omitidos.has("enorme.bin"));
  assert.ok("Mi foto.png" in py.files, "los espacios ya se admiten");
  assert.equal(disco.texto("index.html"), "﻿<h1>Hola</h1>\r\n", "no se reescribe el archivo del computador");
  // Sin cambios: una vuelta no hace nada (sin ping-pong por BOM/CRLF) y no vuelve a leer archivos.
  const lecturas = disco.lecturas;
  const v = await s.sincronizar();
  assert.deepEqual([v.alProyecto, v.alDisco, v.conflictos], [[], [], []]);
  assert.equal(disco.lecturas, lecturas);
});

test("vincular «combinar»: escribe el proyecto en la carpeta y trae lo que solo estaba allá", async () => {
  const disco = new DiscoMemoria({ "notas.md": "de la carpeta", "index.html": "versión del disco" });
  const { py, s } = montar({ "index.html": "versión del proyecto", "img/a.png": (await valorDeBytes("a.png", PNG)).valor }, disco);
  await s.vincular("combinar");
  assert.equal(disco.texto("index.html"), "versión del proyecto");
  assert.deepEqual([...disco.f.get("img/a.png").bytes], [...PNG]);
  assert.equal(py.files["notas.md"], "de la carpeta");
});

test("cambios en un solo lado viajan al otro, incluidos los borrados", async () => {
  const disco = new DiscoMemoria({ "a.txt": "1", "b.txt": "2" });
  const { py, s, cambios } = montar({}, disco);
  await s.vincular("carpeta");
  disco.poner("a.txt", "1 editado en VS Code");
  disco.poner("nuevo/c.txt", "3");
  disco.f.delete("b.txt");
  let r = await s.sincronizar();
  assert.deepEqual(r.alProyecto.sort(), ["a.txt", "nuevo/c.txt"]);
  assert.deepEqual(r.borradosProyecto, ["b.txt"]);
  assert.equal(py.files["a.txt"], "1 editado en VS Code");
  assert.ok(!("b.txt" in py.files) && py.folders.includes("nuevo"));
  assert.equal(cambios.at(-1).origen, "carpeta");

  py.files["a.txt"] = "editado en CódigoCamp";
  py.files["d.txt"] = "nuevo aquí";
  delete py.files["nuevo/c.txt"];
  r = await s.sincronizar();
  assert.deepEqual(r.alDisco.sort(), ["a.txt", "d.txt"]);
  assert.deepEqual(r.borradosDisco, ["nuevo/c.txt"]);
  assert.equal(disco.texto("a.txt"), "editado en CódigoCamp");
  assert.ok(!disco.f.has("nuevo/c.txt"));
  assert.deepEqual(await s.sincronizar().then((x) => [x.alDisco, x.alProyecto]), [[], []], "estable");
});

test("conflicto: gana el computador y la versión de CódigoCamp queda como .conflicto", async () => {
  const disco = new DiscoMemoria({ "app.js": "base" });
  const { py, s, avisos } = montar({}, disco);
  await s.vincular("carpeta");
  disco.poner("app.js", "computador");
  py.files["app.js"] = "codigocamp";
  const r = await s.sincronizar();
  assert.deepEqual(r.conflictos, [{ ruta: "app.js", copia: "app.conflicto.js" }]);
  assert.equal(py.files["app.js"], "computador");
  assert.equal(py.files["app.conflicto.js"], "codigocamp");
  assert.equal(avisos[0].tipo, "conflicto");
  await s.sincronizar();
  assert.equal(disco.texto("app.conflicto.js"), "codigocamp", "la copia también llega a la carpeta");
  // Borrado en un lado + editado en el otro: se conserva lo editado.
  disco.f.delete("app.js");
  py.files["app.js"] = "editado";
  await s.sincronizar();
  assert.equal(disco.texto("app.js"), "editado");
  assert.equal(nombreConflicto(py, "app.js"), "app.conflicto-2.js");
});

test("límites: lo que no cabe se queda en la carpeta, avisa una sola vez y no se borra", async () => {
  const archivos = Object.fromEntries(Array.from({ length: 5001 }, (_, i) => [`f${String(i).padStart(4, "0")}.txt`, "x"]));
  const disco = new DiscoMemoria(archivos);
  const { py, s, avisos } = montar({}, disco);
  await s.vincular("carpeta");
  assert.equal(Object.keys(py.files).length, 5000);
  assert.equal(avisos.filter((a) => a.tipo === "no-cabe").length, 1);
  await s.sincronizar();
  await s.sincronizar();
  assert.equal(avisos.filter((a) => a.tipo === "no-cabe").length, 1, "no repite el aviso");
  assert.ok(disco.f.has("f5000.txt"), "no se borra del computador");
});

test("archivo omitido en la carpeta con el mismo nombre que uno del proyecto: no se sobrescribe ninguno", async () => {
  const disco = new DiscoMemoria({ "datos.bin": new Uint8Array(3000) });
  const { py, s, avisos } = montar({ "datos.bin": "texto del proyecto" }, disco, { maxArchivo: 2000 });
  await s.vincular("combinar");
  assert.equal(disco.f.get("datos.bin").bytes.length, 3000);
  assert.equal(py.files["datos.bin"], "texto del proyecto");
  assert.equal(avisos[0].tipo, "omitido");
  await s.sincronizar();
  assert.equal(disco.f.get("datos.bin").bytes.length, 3000);
});

test("sincronizar mientras otra vuelta corre la repite al final (no se pierden cambios)", async () => {
  const disco = new DiscoMemoria({ "a.txt": "1" });
  const { py, s } = montar({}, disco);
  await s.vincular("carpeta");
  const p1 = s.sincronizar();
  py.files["a.txt"] = "2";
  const p2 = s.sincronizar();
  assert.equal(p1, p2);
  await p2;
  assert.equal(disco.texto("a.txt"), "2");
  assert.equal(leerMarcador("nada"), null);
});

test("archivos grandes: se leen por partes, se suben como Blob y la huella no se recalcula si no cambiaron (ni tras recargar)", async () => {
  const video = new Uint8Array(500_000); video.set([0, 0, 0, 0x18, 0x66, 0x74, 0x79, 0x70, 0x6d, 0x70, 0x34, 0x32]);
  for (let i = 12; i < video.length; i += 1) video[i] = i % 251;
  const disco = new DiscoMemoria({ "media/clip.mp4": video, "datos.csv": "a,b\n".repeat(300_000) });
  const guardado = {};
  const { py, s, subidas } = montar({}, disco, { guardarBase: (b, c) => { guardado.base = b; guardado.cache = c; } });
  await s.vincular("carpeta");
  const m = leerMarcador(py.files["media/clip.mp4"]);
  assert.deepEqual([m.tipo, m.tamano], ["video/mp4", 500_000]);
  assert.equal(leerMarcador(py.files["datos.csv"]).tipo, "text/csv", "el texto grande entra como archivo");
  assert.deepEqual(subidas.sort(), ["datos.csv", "media/clip.mp4"]);
  const lecturas = disco.lecturas;
  const s2 = new Sincronizador({ disco, proyecto: () => py, base: guardado.base, cache: guardado.cache, subirArchivo: async () => { throw new Error("no debía subir"); } });
  const r = await s2.sincronizar();
  assert.deepEqual([r.alProyecto, r.alDisco, r.conflictos], [[], [], []]);
  assert.equal(disco.lecturas, lecturas, "no se releyó el video");
});

test("mismo contenido con otro tipo en el marcador no provoca subidas en bucle", async () => {
  const disco = new DiscoMemoria({ "a.png": PNG });
  const { py, s } = montar({}, disco, { subirArchivo: async (d) => { const v = (await valorDeBytes("a.png", d instanceof Blob ? new Uint8Array(await d.arrayBuffer()) : d)).valor; return v.replace("image/png", "application/octet-stream"); } });
  await s.vincular("carpeta");
  assert.match(py.files["a.png"], /octet-stream/);
  const r = await s.sincronizar();
  assert.deepEqual([r.alProyecto, r.alDisco], [[], []]);
});
