import test from "node:test";
import assert from "node:assert/strict";
import { clonar, interpretarUrlClonar } from "../js/trabajo/github.js";
import { Shell } from "../js/trabajo/shell.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { quitarAnsi } from "../js/trabajo/ansi.js";
import { esMarcador } from "../js/trabajo/archivos.js";

const enc = new TextEncoder();
const PNG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 7, 7];

/** GitHub falso: API REST (repos, commits, trees, blobs) y raw.githubusercontent.com. */
function github({ privado = false, token = "tok", vacio = false, archivos = null, truncado = false, fallos = {} } = {}) {
  const contenido = archivos ?? {
    "README.md": enc.encode("# Hola\r\n"), "src/app.js": enc.encode("console.log(1)\n"), "img/logo.png": new Uint8Array(PNG),
    "node_modules/x/i.js": enc.encode("no"), "video.mp4": new Uint8Array([0, 0, 0, 1]), "Mi Archivo.txt": enc.encode("tilde"),
  };
  const e = { llamadas: [], api: 0, raw: 0 };
  const resp = (status, datos, bytes) => ({ ok: status < 400, status, json: async () => datos, arrayBuffer: async () => bytes?.buffer ?? new ArrayBuffer(0) });
  const autorizado = (h) => !privado || h?.Authorization === `Bearer ${token}`;
  e.fetch = async (url, o = {}) => {
    e.llamadas.push(url);
    if (url.startsWith("https://raw.githubusercontent.com/")) {
      e.raw += 1;
      if (privado) return resp(404, {});
      const ruta = decodeURIComponent(url.split("/").slice(6).join("/"));
      if (fallos[ruta] > 0) { fallos[ruta] -= 1; return resp(429, {}); }
      return contenido[ruta] ? resp(200, null, contenido[ruta]) : resp(404, {});
    }
    e.api += 1;
    if (!autorizado(o.headers)) return resp(404, { message: "Not Found" });
    const r = url.replace("https://api.github.com/repos/ana/proy", "");
    if (r === "") return resp(200, { name: "proy", default_branch: "main", private: privado });
    if (r.startsWith("/commits")) {
      if (vacio) return resp(409, { message: "Git Repository is empty." });
      if (!r.includes("sha=main")) return resp(404, { message: "No commit found" });
      return resp(200, [
        { sha: "abcdef1234567890abcdef1234567890abcdef12", commit: { message: "Segundo commit", author: { date: "2026-02-02T00:00:00Z" }, tree: { sha: "t1" } } },
        { sha: "1234567890abcdef1234567890abcdef12345678", commit: { message: "Inicio", author: { date: "2026-01-01T00:00:00Z" }, tree: { sha: "t0" } } },
      ]);
    }
    if (truncado && r === "/git/trees/t1?recursive=1") return resp(200, { truncated: true, tree: [] });
    if (truncado && r.startsWith("/git/trees/")) {
      const prefijo = r === "/git/trees/t1" ? "" : decodeURIComponent(r.slice("/git/trees/d_".length)) + "/";
      const hijos = new Map();
      for (const [path, b] of Object.entries(contenido)) {
        if (!path.startsWith(prefijo)) continue;
        const resto = path.slice(prefijo.length); const i = resto.indexOf("/");
        if (i < 0) hijos.set(resto, { path: resto, type: "blob", mode: "100644", size: b.length, sha: "s_" + path });
        else hijos.set(resto.slice(0, i), { path: resto.slice(0, i), type: "tree", sha: "d_" + encodeURIComponent(prefijo + resto.slice(0, i)) });
      }
      return resp(200, { truncated: false, tree: [...hijos.values()] });
    }
    if (r === "/git/trees/t1?recursive=1") return resp(200, { truncated: false, tree: [
      { path: "img", type: "tree" }, { path: "lib", type: "commit" },
      ...Object.entries(contenido).map(([path, b]) => ({ path, type: "blob", mode: "100644", size: b.length, sha: "s_" + path })),
    ] });
    if (r.startsWith("/git/blobs/s_")) { const ruta = r.slice("/git/blobs/s_".length); const b = contenido[ruta]; return resp(200, { content: btoa(String.fromCharCode(...b)), encoding: "base64" }); }
    return resp(404, { message: "no simulado " + r });
  };
  return e;
}

function entorno(files, gh, extra = {}) {
  const py = normalizarProyecto({ files });
  const subidas = [];
  const shell = new Shell({
    proyecto: () => py, usuario: "Ana",
    github: { clonar: (o) => clonar({ ...o, fetchFn: gh.fetch }) },
    ...extra,
  });
  const sesion = shell.nuevaSesion();
  let out = "", err = "";
  const lineas = [...(extra.respuestas || [])];
  sesion.out = (t) => { out += t; }; sesion.err = (t) => { err += t; };
  sesion.leerLinea = async () => lineas.shift() ?? null;
  const sh = async (l) => { out = ""; err = ""; const codigo = await shell.ejecutar(l, sesion); return { codigo, out: quitarAnsi(out), err: quitarAnsi(err) }; };
  return { py, sh, shell, subidas };
}

test("interpretarUrlClonar", () => {
  assert.deepEqual(interpretarUrlClonar("https://github.com/ana/proy.git"), { owner: "ana", repo: "proy" });
  assert.deepEqual(interpretarUrlClonar("github.com/ana/proy"), { owner: "ana", repo: "proy" });
  assert.match(interpretarUrlClonar("git@github.com:ana/proy.git").error, /SSH/);
  assert.match(interpretarUrlClonar("https://gitlab.com/ana/proy").error, /GitHub/);
});

test("clonar: pocas consultas a la API, archivos por raw, ignora y omite con motivo", async () => {
  const gh = github();
  const r = await clonar({ url: "https://github.com/ana/proy", fetchFn: gh.fetch });
  assert.equal(gh.api, 3);
  assert.equal(r.rama, "main");
  assert.deepEqual(r.commits.map((c) => c.hash), ["abcdef1", "1234567"]);
  assert.deepEqual(r.archivos.map((a) => a.ruta).sort(), ["Mi Archivo.txt", "README.md", "img/logo.png", "node_modules/x/i.js", "src/app.js", "video.mp4"], "trae TODO lo del repositorio");
  assert.equal(r.ignorados, 0);
  const grande = await clonar({ url: "https://github.com/ana/proy", fetchFn: github().fetch, maxBytes: 5 });
  assert.ok(grande.omitidos.some((o) => o.ruta === "README.md" && /MB/.test(o.motivo)), "lo que pasa del máximo no se descarga");
  assert.ok(r.omitidos.some((o) => o.ruta === "lib" && /submódulo/.test(o.motivo)));
});

test("git clone en carpeta: copia sin historial y no toca el Git del proyecto", async () => {
  const gh = github();
  const { py, sh } = entorno({ "index.html": "x" }, gh, { importar: undefined });
  const r = await sh("git clone https://github.com/ana/proy.git");
  assert.equal(r.codigo, 0, r.err);
  assert.equal(py.files["proy/README.md"], "# Hola\n");
  assert.ok("proy/Mi Archivo.txt" in py.files);
  assert.ok(!("proy/img/logo.png" in py.files), "sin cuenta no hay imágenes");
  assert.match(r.out, /sin historial/);
  assert.match(r.out, /img\/logo\.png — los archivos que no son texto solo se guardan/);
  assert.equal(py.git.initialized, false);
  assert.match((await sh("git clone https://github.com/ana/proy.git")).err, /no es un directorio vacío/);
});

test("git clone . en proyecto vacío: activa Git con commits, remoto y archivos seguidos; las imágenes se suben", async () => {
  const gh = github();
  const py = normalizarProyecto({ files: {} });
  const { importarEn } = await import("../js/trabajo/importar.js");
  const shell = new Shell({ proyecto: () => py, github: { clonar: (o) => clonar({ ...o, fetchFn: gh.fetch }) },
    importar: (origen, o) => importarEn(py, origen, { ...o, subir: async (b) => { subidas.push(b); return "ccimg:v1:" + "c".repeat(64) + ":image/png:10"; } }) });
  const subidas = [];
  const s = shell.nuevaSesion(); let out = ""; s.out = (t) => { out += t; }; s.err = (t) => { out += t; };
  assert.equal(await shell.ejecutar("git clone https://github.com/ana/proy.git .", s), 0, out);
  const g = py.git;
  assert.equal(subidas.length, 2, "imagen y video");
  assert.ok(esMarcador(py.files["img/logo.png"]));
  assert.equal(g.initialized, true);
  assert.equal(g.remote, "https://github.com/ana/proy.git");
  assert.equal(g.branch, "main");
  assert.deepEqual(g.branches, { main: "abcdef1" });
  assert.equal(g.commits[0].message, "Segundo commit");
  assert.deepEqual(g.committed, py.files);
  assert.deepEqual([...g.tracked].sort(), Object.keys(py.files).sort());
  out = "";
  await shell.ejecutar("git status", s);
  assert.match(quitarAnsi(out), /nada para hacer commit|limpio|nada que/i);
});

test("git clone: errores (raíz ocupada, repositorio con commits, URL SSH, sin argumentos, rama inexistente, vacío)", async () => {
  const gh = github();
  const { sh, py } = entorno({ "a.txt": "x" }, gh);
  assert.match((await sh("git clone https://github.com/ana/proy.git .")).err, /no es un directorio vacío[\s\S]*rm -r/);
  assert.match((await sh("git clone git@github.com:ana/proy.git")).err, /SSH/);
  assert.equal((await sh("git clone")).codigo, 129);
  assert.match((await sh("git clone -b nada https://github.com/ana/proy.git otra")).err, /rama «nada» no existe/);
  assert.match((await sh("git clone https://github.com/ana/proy.git a.txt")).err, /no es un directorio/);
  const v = entorno({}, github({ vacio: true }));
  const r = await v.sh("git clone https://github.com/ana/proy.git .");
  assert.equal(r.codigo, 0);
  assert.match(r.out, /repositorio vacío/);
  assert.equal(v.py.git.remote, "https://github.com/ana/proy.git");
  void py;
});

test("git clone privado: pide token una vez, lo usa con la API de blobs y lo recuerda en memoria", async () => {
  const gh = github({ privado: true });
  const { sh, py, shell } = entorno({}, gh, { respuestas: ["tok"] });
  const r = await sh("git clone https://github.com/ana/proy.git codigo");
  assert.equal(r.codigo, 0, r.err);
  assert.equal(py.files["codigo/src/app.js"], "console.log(1)\n");
  assert.equal(gh.raw, 0);
  assert.equal(shell.tokenGitHub, "tok");
  const sinToken = entorno({}, github({ privado: true }), { respuestas: [""] });
  assert.match((await sinToken.sh("git clone https://github.com/ana/proy.git")).err, /privado/);
});

test("clon completo: lista recortada por GitHub, reintentos de descarga y enlaces simbólicos", async () => {
  const gh = github({ truncado: true, fallos: { "src/app.js": 2 } });
  const r = await clonar({ url: "https://github.com/ana/proy", fetchFn: gh.fetch, pausa: 1 });
  assert.deepEqual(r.archivos.map((a) => a.ruta).sort(), ["Mi Archivo.txt", "README.md", "img/logo.png", "node_modules/x/i.js", "src/app.js", "video.mp4"]);
  assert.deepEqual(r.omitidos.filter((o) => o.ruta !== "lib"), [], "nada se pierde aunque la descarga falle dos veces");
  const conEnlace = github({ archivos: { "a.txt": enc.encode("a"), "enlace": enc.encode("a.txt") } });
  const r2 = await clonar({ url: "https://github.com/ana/proy", fetchFn: conEnlace.fetch, pausa: 1 });
  assert.ok(r2.archivos.some((a) => a.ruta === "enlace"));
});

test("git clone completo en el proyecto: node_modules y carpetas de herramientas también se traen", async () => {
  const gh = github();
  const py = normalizarProyecto({ files: {} });
  const { importarEn } = await import("../js/trabajo/importar.js");
  const shell = new Shell({ proyecto: () => py, github: { clonar: (o) => clonar({ ...o, fetchFn: gh.fetch, pausa: 1 }) },
    importar: (origen, o) => importarEn(py, origen, { ...o, subir: async () => "ccbin:v1:" + "c".repeat(64) + ":image/png:10" }) });
  const s = shell.nuevaSesion(); let out = ""; s.out = (t) => { out += t; }; s.err = (t) => { out += t; };
  assert.equal(await shell.ejecutar("git clone https://github.com/ana/proy.git .", s), 0, out);
  assert.ok("node_modules/x/i.js" in py.files);
  assert.ok("Mi Archivo.txt" in py.files);
  assert.doesNotMatch(quitarAnsi(out), /no se trajeron/);
});

test("caso Finanbot: 98 archivos y 1,6 millones de caracteres llegan TODOS, editables y con __init__.py intacto", async () => {
  const archivos = {};
  for (let i = 0; i < 90; i += 1) archivos[`backend/routes/ruta_${i}.py`] = enc.encode(`# ruta ${i}\n` + "def f():\n    return 1\n".repeat(800));
  for (const p of ["backend/__init__.py", "backend/application/__init__.py", "backend/application/services/__init__.py", "backend/presentation/__init__.py"]) archivos[p] = enc.encode("");
  archivos["frontend/package-lock.json"] = enc.encode(JSON.stringify({ x: "y".repeat(400_000) }));
  archivos["README.md"] = enc.encode("# Finanbot\n"); archivos[".gitignore"] = enc.encode("venv/\n"); archivos[".env.example"] = enc.encode("A=1\n");
  const gh = github({ archivos });
  const py = normalizarProyecto({ files: { "index.html": "x" } });
  const { importarEn } = await import("../js/trabajo/importar.js");
  const shell = new Shell({ proyecto: () => py, github: { clonar: (o) => clonar({ ...o, fetchFn: gh.fetch, pausa: 1 }) },
    importar: (origen, o) => importarEn(py, origen, { ...o, subir: async () => { throw new Error("no debía subir nada"); } }) });
  const s = shell.nuevaSesion(); let out = ""; s.out = (t) => { out += t; }; s.err = (t) => { out += t; };
  assert.equal(await shell.ejecutar("git clone https://github.com/ana/proy.git Finanbot", s), 0, out);
  const clonados = Object.keys(py.files).filter((r) => r.startsWith("Finanbot/"));
  assert.equal(clonados.length, Object.keys(archivos).length, quitarAnsi(out));
  assert.equal(py.files["Finanbot/backend/application/__init__.py"], "");
  assert.ok(!Object.values(py.files).some((t) => t.startsWith("ccbin:")), "todo es texto editable");
  assert.doesNotMatch(quitarAnsi(out), /no se trajeron|renombrado/);
});
