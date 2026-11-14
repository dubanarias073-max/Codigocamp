import test from "node:test";
import assert from "node:assert/strict";
import { Almacen, proyectoNuevo, normalizarProyecto, PLANTILLAS } from "../js/trabajo/almacen.js";
import * as FS from "../js/trabajo/fs.js";

const CLAVE = "cc_trabajo_1";
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

class Almacenamiento {
  constructor() { this.d = new Map(); this.lleno = false; }
  getItem(k) { return this.d.has(k) ? this.d.get(k) : null; }
  setItem(k, v) { if (this.lleno) throw new Error("QuotaExceededError"); this.d.set(k, String(v)); }
}

/** Servidor falso con la misma forma que /api/trabajo/ (GET, PUT, marca «actualizado» que cambia en cada PUT). */
class Servidor {
  constructor() { this.proyecto = null; this.n = 0; this.caido = false; this.rechazar = null; this.peticiones = []; }
  get actualizado() { return this.proyecto ? `t${this.n}` : null; }
  fetch = async (url, { method, body }) => {
    this.peticiones.push(method);
    if (this.caido) throw new TypeError("Failed to fetch");
    const resp = (estado, datos) => ({ ok: estado < 400, status: estado, json: async () => datos });
    if (this.rechazar) return resp(this.rechazar, { error: "rechazado" });
    if (method === "GET") return resp(200, { proyecto: this.proyecto, actualizado: this.actualizado });
    this.proyecto = JSON.parse(body); this.n += 1;
    return resp(200, { ok: true, actualizado: this.actualizado });
  };
}

const crear = (srv, almacenamiento, extra = {}) => new Almacen({
  clave: CLAVE, fetchFn: srv.fetch, storage: almacenamiento, csrf: () => "x", retardo: 5, reintento: 10, ...extra,
});

test("usuario nuevo: se crean y suben las plantillas una sola vez", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  const a = crear(srv, ls);
  await a.iniciar();
  assert.deepEqual(Object.keys(a.proyecto.files).sort(), Object.keys(PLANTILLAS).sort());
  assert.equal(a.estado, "guardado");
  assert.deepEqual(Object.keys(srv.proyecto.files).sort(), Object.keys(PLANTILLAS).sort());
  assert.deepEqual(srv.peticiones, ["GET", "PUT"]);
});

test("ESCENARIO B: borrar todos los archivos y recargar deja el proyecto vacío (no vuelven las plantillas)", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  let a = crear(srv, ls);
  await a.iniciar();
  for (const r of Object.keys(a.proyecto.files)) FS.borrar(a.proyecto, r);
  a.cambiar();
  assert.equal(await a.guardarAhora(), true);
  assert.deepEqual(srv.proyecto.files, {});
  // «recarga»: otra instancia con el mismo almacenamiento y el mismo servidor
  a = crear(srv, ls);
  await a.iniciar();
  assert.deepEqual(a.proyecto.files, {});
  // y también desde un navegador limpio (otro dispositivo)
  const b = crear(srv, new Almacenamiento());
  await b.iniciar();
  assert.deepEqual(b.proyecto.files, {});
});

test("ESCENARIOS A y C: cambios locales aún sin subir NO se pierden al recargar rápido", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  let a = crear(srv, ls, { retardo: 10_000 }); // la subida programada tarda: simula cerrar antes de que ocurra
  await a.iniciar();
  FS.borrar(a.proyecto, "script.js");
  a.proyecto.files["index.html"] = "CAMBIO IMPORTANTE";
  a.cambiar();
  clearTimeout(a.temporizador);
  assert.ok(srv.proyecto.files["script.js"] !== undefined, "la nube aún tiene la versión vieja");
  // recarga antes de que se suba
  a = crear(srv, ls);
  await a.iniciar();
  assert.equal(a.proyecto.files["index.html"], "CAMBIO IMPORTANTE");
  assert.equal(FS.tieneArchivo(a.proyecto, "script.js"), false, "el archivo borrado no regresa");
  assert.equal(srv.proyecto.files["index.html"], "CAMBIO IMPORTANTE", "y la cuenta quedó actualizada");
  assert.equal(srv.proyecto.files["script.js"], undefined);
  assert.equal(a.estado, "guardado");
});

test("si la cuenta cambió en otro dispositivo y aquí no hay nada pendiente, gana la cuenta", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  const a = crear(srv, ls);
  await a.iniciar();
  const otro = crear(srv, new Almacenamiento());
  await otro.iniciar();
  otro.proyecto.files["nuevo.txt"] = "desde el otro equipo";
  otro.cambiar(); await otro.guardarAhora();
  const a2 = crear(srv, ls);
  await a2.iniciar();
  assert.equal(a2.proyecto.files["nuevo.txt"], "desde el otro equipo");
  assert.equal(a2.sucio, false);
});

test("conflicto real (cambió la cuenta Y hay pendientes locales): se pregunta y se respeta la elección", async () => {
  for (const eleccion of ["local", "nube"]) {
    const srv = new Servidor(), ls = new Almacenamiento();
    const a = crear(srv, ls, { retardo: 10_000 });
    await a.iniciar();
    const otro = crear(srv, new Almacenamiento());
    await otro.iniciar();
    otro.proyecto.files["nube.txt"] = "N";
    otro.cambiar(); await otro.guardarAhora();
    a.proyecto.files["local.txt"] = "L"; a.cambiar(); clearTimeout(a.temporizador);
    let pregunta = null;
    const a2 = crear(srv, ls, { resolverConflicto: async (i) => { pregunta = i; return eleccion; } });
    await a2.iniciar();
    assert.ok(pregunta && pregunta.local.archivos && pregunta.nube.archivos, "se mostró la comparación");
    if (eleccion === "local") { assert.ok(a2.proyecto.files["local.txt"]); assert.equal(a2.proyecto.files["nube.txt"], undefined); assert.ok(srv.proyecto.files["local.txt"]); }
    else { assert.ok(a2.proyecto.files["nube.txt"]); assert.equal(a2.proyecto.files["local.txt"], undefined); }
    assert.equal(a2.estado, "guardado");
  }
});

test("sin conexión al abrir: se trabaja con lo local, y al volver la red se reconcilia y sube", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  const a = crear(srv, ls);
  await a.iniciar();
  srv.caido = true;
  const b = crear(srv, ls, { reintento: 10 });
  await b.iniciar();
  assert.equal(b.estado, "sinconexion");
  assert.equal(Object.keys(b.proyecto.files).length, 3);
  b.proyecto.files["offline.txt"] = "hecho sin red";
  b.cambiar();
  await dormir(30);
  assert.equal(b.estado, "sinconexion");
  srv.caido = false;
  await dormir(60);
  assert.equal(b.estado, "guardado");
  assert.equal(srv.proyecto.files["offline.txt"], "hecho sin red");
});

test("sin conexión y sin copia local: no se inventan archivos ni se sube nada hasta poder comparar", async () => {
  const srv = new Servidor(); srv.caido = true;
  const a = crear(srv, new Almacenamiento());
  await a.iniciar();
  assert.equal(a.estado, "sinconexion");
  assert.equal(a.sucio, false, "las plantillas por defecto no cuentan como trabajo pendiente");
});

test("cambios mientras se sube provocan otra subida (no se pierde el último cambio)", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  let a, primera = false;
  a = crear(srv, ls, { fetchFn: async (url, op) => {
    if (op.method === "PUT" && primera) { primera = false; a.proyecto.files["tarde.txt"] = "x"; a.cambiar(); }
    return srv.fetch(url, op);
  } });
  await a.iniciar();
  primera = true;
  a.proyecto.files["a.txt"] = "1"; a.cambiar();
  await a.guardarAhora();
  await dormir(40);
  assert.equal(srv.proyecto.files["tarde.txt"], "x");
  assert.equal(a.sucio, false);
});

test("error 400 del servidor no entra en bucle de reintentos y deja el trabajo local", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  const a = crear(srv, ls);
  await a.iniciar();
  srv.rechazar = 400;
  a.proyecto.files["x.txt"] = "1"; a.cambiar();
  await a.guardarAhora();
  assert.equal(a.estado, "error");
  const n = srv.peticiones.length;
  await dormir(50);
  assert.equal(srv.peticiones.length, n, "no reintenta");
  assert.equal(JSON.parse(ls.getItem(CLAVE)).sucio, true);
});

test("sesión vencida (401) se avisa y no se pierde nada", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  const a = crear(srv, ls);
  await a.iniciar();
  srv.rechazar = 401;
  a.proyecto.files["x.txt"] = "1"; a.cambiar();
  await a.guardarAhora();
  assert.equal(a.estado, "sesion");
  assert.equal(JSON.parse(ls.getItem(CLAVE)).proyecto.files["x.txt"], "1");
});

test("formato local anterior (sin versión) con cambios distintos a la cuenta pregunta; si son iguales no", async () => {
  const srv = new Servidor(); srv.proyecto = normalizarProyecto({ files: { "a.txt": "nube" } }); srv.n = 3;
  const ls = new Almacenamiento();
  ls.setItem(CLAVE, JSON.stringify({ files: { "a.txt": "navegador" }, folders: [], git: {} }));
  let preguntas = 0;
  const a = crear(srv, ls, { resolverConflicto: async () => { preguntas += 1; return "local"; } });
  await a.iniciar();
  assert.equal(preguntas, 1);
  assert.equal(srv.proyecto.files["a.txt"], "navegador");
  // iguales: no pregunta
  const srv2 = new Servidor(); srv2.proyecto = normalizarProyecto({ files: { "a.txt": "igual" } }); srv2.n = 1;
  const ls2 = new Almacenamiento();
  ls2.setItem(CLAVE, JSON.stringify({ files: { "a.txt": "igual" }, folders: [], git: {} }));
  const b = crear(srv2, ls2, { resolverConflicto: async () => { throw new Error("no debía preguntar"); } });
  await b.iniciar();
  assert.equal(b.sucio, false);
});

test("otra pestaña: recargarDesdeLocal adopta su versión y avisa a la interfaz", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  let avisos = 0;
  const a = crear(srv, ls, { alRemoto: () => { avisos += 1; } });
  await a.iniciar();
  const b = crear(srv, ls);
  await b.iniciar();
  b.proyecto.files["de-b.txt"] = "1"; b.cambiar();
  assert.equal(a.recargarDesdeLocal(), true);
  assert.equal(a.proyecto.files["de-b.txt"], "1");
  assert.equal(avisos, 1);
  assert.equal(a.recargarDesdeLocal(), false);
});

test("sin espacio en el navegador se avisa", async () => {
  const srv = new Servidor(), ls = new Almacenamiento();
  const estados = [];
  const a = crear(srv, ls, { alEstado: (e) => estados.push(e) });
  await a.iniciar();
  ls.lleno = true;
  a.proyecto.files["x.txt"] = "1"; a.cambiar();
  assert.ok(estados.includes("errorLocal"));
});

test("normalizarProyecto descarta basura y conserva Git válido", () => {
  const py = normalizarProyecto({
    files: { "a.js": "1", "../x": "2" }, folders: ["src"],
    git: { initialized: true, branch: "feature/x", staged: ["a.js", "a.js"], tracked: ["a.js"], committed: { "a.js": "1" },
      commits: [{ hash: "abc1234", message: "m", date: "2026-01-01" }, { hash: "ZZZ", message: "mal", date: "x" }], remote: "https://github.com/u/r.git", branches: { main: "abc1234", "mala rama": "x" } },
  });
  assert.deepEqual(Object.keys(py.files), ["a.js"]);
  assert.equal(py.git.branch, "feature/x");
  assert.deepEqual(py.git.staged, ["a.js"]);
  assert.equal(py.git.commits.length, 1);
  assert.deepEqual(py.git.branches, { main: "abc1234" });
});
