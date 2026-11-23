// Git de verdad en el navegador (isomorphic-git), como en VS Code: clone con todo el historial, commits, ramas,
// merge, stash, fetch/pull/push a GitHub… Cada repositorio vive en una carpeta del proyecto (o en la raíz).
//
// Dónde está cada cosa:
//   · Los archivos del proyecto siguen en tu cuenta (como siempre). Antes de cada orden se copian al «árbol de
//     trabajo» de Git y después se traen de vuelta los que Git cambió (checkout, pull, merge…).
//   · La carpeta .git vive en este navegador (IndexedDB) y se respalda comprimida en tu cuenta después de cada
//     cambio, así el historial también está en tus otros dispositivos.
//   · Con GitHub se habla a través del servidor de CódigoCamp (/api/git/…), porque GitHub no deja que una página
//     web use su protocolo directamente. El token solo se usa para esa petición y no se guarda.
import { color } from "./ansi.js";
import * as FS from "./fs.js";
import { esMarcador, leerMarcador } from "./archivos.js";
import { diffUnificado } from "./git.js";
import { crc32, crearZip, leerZip } from "./zip.js";

const BIN = "\u0000bin";
const textoOBinario = (bytes) => { const u8 = new Uint8Array(bytes); return comoTexto(u8) ?? `${BIN}${crc32(u8)}:${u8.length}`; };
const quitarColor = (t) => t.replace(/\x1b\[[0-9;]*m/g, "");

const TEXTO_MAX = 1024 * 1024;
const NOMBRE_RAMA = /^(?!.*\.\.)(?!.*\/\/)(?!\/)(?!.*\/$)(?!.*\.lock$)[A-Za-z0-9._/-]{1,120}$/;

const dec = new TextDecoder("utf-8", { fatal: true });
const enc = new TextEncoder();
export const comoTexto = (bytes) => { if (bytes.length > TEXTO_MAX) return null; try { const t = dec.decode(bytes); return t.includes("\u0000") ? null : t; } catch { return null; } };

// Huella rápida de un texto (cyrb53): para saber si un archivo cambió sin guardar su contenido.
function huella(t) {
  let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
  for (let i = 0; i < t.length; i++) { const c = t.charCodeAt(i); h1 = Math.imul(h1 ^ c, 2654435761); h2 = Math.imul(h2 ^ c, 1597334677); }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36) + ":" + t.length;
}
const firma = (v) => (esMarcador(v) ? `#${leerMarcador(v).hash}` : `t${huella(v)}`);
const sha256 = async (bytes) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map((b) => b.toString(16).padStart(2, "0")).join("");

const corto = (oid) => oid.slice(0, 7);
const primera = (m) => (m || "").split("\n")[0];

function fechaGit(ts, tz) {
  // tz de isomorphic-git: minutos al OESTE de UTC (como getTimezoneOffset)
  const d = new Date((ts - tz * 60) * 1000);
  const dias = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const off = -tz, s = off >= 0 ? "+" : "-", a = Math.abs(off);
  const p = (n) => String(n).padStart(2, "0");
  return `${dias[d.getUTCDay()]} ${meses[d.getUTCMonth()]} ${d.getUTCDate()} ${p(d.getUTCHours())}:${p(d.getUTCMinutes())}:${p(d.getUTCSeconds())} ${d.getUTCFullYear()} ${s}${p(Math.floor(a / 60))}${p(a % 60)}`;
}
function hace(ts, ahora = Date.now() / 1000) {
  const s = Math.max(0, Math.round(ahora - ts));
  const [n, u] = s < 60 ? [s, "seconds"] : s < 3600 ? [Math.round(s / 60), "minutes"] : s < 86400 ? [Math.round(s / 3600), "hours"] : s < 2592000 ? [Math.round(s / 86400), "days"] : s < 31536000 ? [Math.round(s / 2592000), "months"] : [Math.round(s / 31536000), "years"];
  return `${n} ${n === 1 ? u.slice(0, -1) : u} ago`;
}

/** Interpreta una fila de statusMatrix → { preparado, sinPreparar } con tipo nuevo|modificado|eliminado|sin */
export function clasificar([, head, work, stage]) {
  let preparado = null, sinPreparar = null;
  if (head === 0 && stage !== 0) preparado = "nuevo";
  else if (head === 1 && stage === 0) preparado = "eliminado";
  else if (head === 1 && (stage === 3 || (stage === 2 && work !== 1))) preparado = "modificado";
  if (stage === 0 && work !== 0 && (head === 0 || head === 1)) sinPreparar = "sin";
  else if (stage !== 0 && work === 0) sinPreparar = "eliminado";
  else if ((stage === 1 && work === 2) || stage === 3) sinPreparar = "modificado";
  if (head === 1 && stage === 0 && work === 0) sinPreparar = null;
  return { preparado, sinPreparar };
}

export class MotorGit {
  /**
   * @param {object} o
   *   git, fs (con .promises), http        isomorphic-git, sistema de archivos y cliente http
   *   corsProxy                             p. ej. "/api/git" (null = directo, para pruebas en Node)
   *   cabeceras()                           cabeceras extra (CSRF)
   *   archivos                              { bytes(marcador) → Uint8Array, subir(bytes,{nombre}) → marcador } (opcional)
   *   autor()                               { name, email } por defecto
   *   ahora()                               Date (pruebas)
   */
  constructor({ git, fs, http, raiz = "/w", corsProxy = "/api/git", cabeceras = () => ({}), archivos = null, autor = () => ({ name: "estudiante", email: "estudiante@codigocamp.local" }), ahora = () => new Date(), claveGlobal = "cc-git-global", credencial = null }) {
    // credencial: SesionGitHub (sesiongithub.js) → «Iniciar sesión con GitHub» en vez de pedir un token en la terminal.
    Object.assign(this, { git, fs, http, corsProxy, cabeceras, archivos, autor, ahora, claveGlobal, credencial });
    this.urlRed = "";
    this.raiz = raiz.replace(/\/$/, "");
    this.cache = `${this.raiz}.cc`;
    this.p = fs.promises;
    this.token = null;
  }

  dirFs(dir) { return dir ? `${this.raiz}/${dir}` : this.raiz; }

  // ------------------------------------------------------------------ utilidades de fs ----
  async existe(ruta) { try { await this.p.stat(ruta); return true; } catch { return false; } }
  async mkdirp(ruta) {
    let acc = "";
    for (const parte of ruta.split("/").filter(Boolean)) { acc += "/" + parte; try { await this.p.mkdir(acc); } catch (e) { if (e.code !== "EEXIST" && !(await this.existe(acc))) throw e; } }
  }
  async borrarArbol(ruta) {
    let st;
    try { st = await this.p.stat(ruta); } catch { return; }
    if (st.isDirectory()) { for (const n of await this.p.readdir(ruta)) await this.borrarArbol(`${ruta}/${n}`); await this.p.rmdir(ruta); }
    else await this.p.unlink(ruta);
  }
  async listar(ruta, rel = "", saltar = (r) => false, salida = []) {
    let nombres;
    try { nombres = await this.p.readdir(ruta); } catch { return salida; }
    for (const n of nombres) {
      const r = rel ? `${rel}/${n}` : n;
      if (saltar(r)) continue;
      const st = await this.p.stat(`${ruta}/${n}`);
      if (st.isDirectory()) await this.listar(`${ruta}/${n}`, r, saltar, salida); else salida.push(r);
    }
    return salida;
  }
  async leerCache(dir) { try { return JSON.parse(await this.p.readFile(`${this.cache}/${encodeURIComponent(dir || "_raiz")}.json`, "utf8")); } catch { return {}; } }
  async guardarCache(dir, c) { await this.mkdirp(this.cache); await this.p.writeFile(`${this.cache}/${encodeURIComponent(dir || "_raiz")}.json`, JSON.stringify(c), "utf8"); }

  // ------------------------------------------------------------------ repositorios del proyecto ----
  repos(py) { return py.git.repos ?? (py.git.repos = {}); }
  /** Carpeta del repositorio que contiene `cwd` (la más interna), o null. */
  raizDe(py, cwd) {
    const candidatos = Object.keys(this.repos(py)).filter((d) => d === "" || cwd === d || cwd.startsWith(d + "/"));
    return candidatos.sort((a, b) => b.length - a.length)[0] ?? null;
  }
  otrosRepos(py, dir) { return Object.keys(this.repos(py)).filter((d) => d !== dir && (dir === "" || d.startsWith(dir + "/"))); }
  dentroDeOtro(py, dir, rel) { const abs = dir ? `${dir}/${rel}` : rel; return this.otrosRepos(py, dir).some((o) => abs === o || abs.startsWith(o + "/")); }

  /** Copia los archivos del proyecto al árbol de trabajo de Git (solo los que cambiaron). */
  async haciaGit(py, dir) {
    const base = this.dirFs(dir);
    await this.mkdirp(base);
    const cache = await this.leerCache(dir);
    const vistos = new Set();
    const prefijo = dir ? dir + "/" : "";
    for (const [ruta, valor] of Object.entries(py.files)) {
      if (prefijo && !ruta.startsWith(prefijo)) continue;
      const rel = ruta.slice(prefijo.length);
      if (rel === ".git" || rel.startsWith(".git/") || this.dentroDeOtro(py, dir, rel)) continue;
      vistos.add(rel);
      const f = firma(valor);
      if (cache[rel] === f && await this.existe(`${base}/${rel}`)) continue;
      let datos = valor;
      if (esMarcador(valor)) {
        if (!this.archivos) continue;
        datos = await this.archivos.bytes(valor);
      }
      await this.mkdirp(`${base}/${FS.carpetaDe(rel)}`);
      await this.p.writeFile(`${base}/${rel}`, datos, typeof datos === "string" ? "utf8" : undefined);
      cache[rel] = f;
    }
    for (const rel of Object.keys(cache)) {
      if (vistos.has(rel)) continue;
      try { await this.p.unlink(`${base}/${rel}`); } catch { /* ya no estaba */ }
      delete cache[rel];
    }
    await this.guardarCache(dir, cache);
  }

  /** Trae al proyecto lo que Git dejó en el árbol de trabajo (después de checkout, pull, merge…). Devuelve si cambió algo. */
  async desdeGit(py, dir, { err = () => {} } = {}) {
    const base = this.dirFs(dir);
    const cache = await this.leerCache(dir);
    const prefijo = dir ? dir + "/" : "";
    const rels = await this.listar(base, "", (r) => r === ".git" || this.dentroDeOtro(py, dir, r));
    const presentes = new Set(rels);
    let cambio = false;
    for (const rel of rels) {
      const ruta = prefijo + rel;
      const bytes = await this.p.readFile(`${base}/${rel}`);
      const u8 = typeof bytes === "string" ? enc.encode(bytes) : new Uint8Array(bytes);
      const texto = comoTexto(u8);
      let valor;
      if (texto !== null) valor = texto;
      else {
        const actual = py.files[ruta];
        const hash = await sha256(u8);
        if (esMarcador(actual) && leerMarcador(actual).hash === hash) valor = actual;
        else if (!this.archivos) { err(`No se pudo traer ${ruta}: los archivos binarios necesitan la sesión iniciada.\n`); continue; }
        else {
          try { valor = await this.archivos.subir(u8, { nombre: ruta }); }
          catch (e) { err(`No se pudo guardar ${ruta}: ${e.message}\n`); continue; }
        }
      }
      cache[rel] = firma(valor);
      if (py.files[ruta] === valor) continue;
      const r = FS.tieneArchivo(py, ruta) ? FS.escribirArchivo(py, ruta, valor) : FS.crearArchivo(py, ruta, valor, { padres: FS.carpetaDe(ruta) !== "" });
      if (r.ok) cambio = true; else err(`${ruta}: ${r.error}\n`);
    }
    for (const ruta of Object.keys(py.files)) {
      if (prefijo && !ruta.startsWith(prefijo)) continue;
      const rel = ruta.slice(prefijo.length);
      if (presentes.has(rel) || this.dentroDeOtro(py, dir, rel)) continue;
      delete py.files[ruta];
      delete cache[rel];
      cambio = true;
    }
    await this.guardarCache(dir, cache);
    return cambio;
  }

  // ------------------------------------------------------------------ respaldo del .git en la cuenta ----
  async respaldar(py, dir, { err = () => {} } = {}) {
    if (!this.archivos) return false;
    const gitdir = `${this.dirFs(dir)}/.git`;
    const rels = await this.listar(gitdir);
    if (rels.length > 4900) { err(color.amarillo(`(El historial de ${dir || "este repositorio"} tiene demasiados archivos para respaldarlo; queda solo en este navegador y en el remoto.)\n`)); return false; }
    const entradas = [];
    for (const rel of rels) entradas.push({ ruta: rel, bytes: new Uint8Array(await this.p.readFile(`${gitdir}/${rel}`)) });
    const zip = await crearZip(entradas, { fecha: new Date(0) });
    const previo = leerMarcador(this.repos(py)[dir]?.respaldo || "");
    if (previo && previo.hash === await sha256(zip)) return false;
    try {
      const marcador = await this.archivos.subir(zip, { nombre: `${dir || "proyecto"}.git.zip` });
      const info = this.repos(py)[dir] ?? (this.repos(py)[dir] = { remote: "", respaldo: "", rama: "" });
      if (info.respaldo === marcador) return false;
      info.respaldo = marcador;
      return true;
    } catch (e) { err(color.amarillo(`(No se pudo respaldar el historial en tu cuenta: ${e.message})\n`)); return false; }
  }

  /** Si este navegador no tiene el .git del repositorio, lo recupera del respaldo o del remoto. */
  async asegurarGit(py, dir, { out = () => {}, err = () => {} } = {}) {
    const gitdir = `${this.dirFs(dir)}/.git`;
    if (await this.existe(`${gitdir}/HEAD`)) return true;
    const info = this.repos(py)[dir] ?? {};
    await this.mkdirp(this.dirFs(dir));
    if (info.respaldo && this.archivos) {
      try {
        const { archivos } = await leerZip(await this.archivos.bytes(info.respaldo), { limites: { entradas: 5000, porArchivo: 1024 ** 3, total: 2 * 1024 ** 3 } });
        for (const a of archivos) { await this.mkdirp(`${gitdir}/${FS.carpetaDe(a.ruta)}`); await this.p.writeFile(`${gitdir}/${a.ruta}`, a.bytes); }
        out(color.gris(`(Historial de Git recuperado de tu cuenta.)\n`));
        await this.haciaGit(py, dir);
        return true;
      } catch (e) { err(color.amarillo(`(No se pudo leer el respaldo del historial: ${e.message})\n`)); }
    }
    if (info.remote) {
      out(color.gris(`Este navegador no tenía el historial: se descarga de ${info.remote}…\n`));
      const d = this.dirFs(dir);
      await this.git.init({ fs: this.fs, dir: d, defaultBranch: info.rama || "main" });
      await this.git.addRemote({ fs: this.fs, dir: d, remote: "origin", url: info.remote, force: true });
      await this.git.fetch({ ...this.red(), dir: d, remote: "origin", tags: true });
      const rama = info.rama || "main";
      try {
        const oid = await this.git.resolveRef({ fs: this.fs, dir: d, ref: `refs/remotes/origin/${rama}` });
        await this.git.writeRef({ fs: this.fs, dir: d, ref: `refs/heads/${rama}`, value: oid, force: true });
        await this.git.setConfig({ fs: this.fs, dir: d, path: `branch.${rama}.remote`, value: "origin" });
        await this.git.setConfig({ fs: this.fs, dir: d, path: `branch.${rama}.merge`, value: `refs/heads/${rama}` });
        await this.haciaGit(py, dir);
        for (const f of await this.git.listFiles({ fs: this.fs, dir: d, ref: rama })) await this.git.resetIndex({ fs: this.fs, dir: d, filepath: f });
      } catch { /* remoto vacío */ }
      return true;
    }
    return false;
  }

  // ------------------------------------------------------------------ red ----
  red() {
    return {
      fs: this.fs, http: this.http, corsProxy: this.corsProxy || undefined, headers: this.cabeceras(),
      onAuth: (url) => { const t = this.tokenPara(url || this.urlRed); return t ? { username: "x-access-token", password: t } : { cancel: true }; },
      onAuthFailure: (url) => { this.olvidarToken(url || this.urlRed); return { cancel: true }; },
    };
  }

  async autorDe(d) {
    const name = await this.git.getConfig({ fs: this.fs, dir: d, path: "user.name" }).catch(() => null);
    const email = await this.git.getConfig({ fs: this.fs, dir: d, path: "user.email" }).catch(() => null);
    const def = this.autor();
    return { name: name || def.name, email: email || def.email, timestamp: Math.floor(this.ahora().getTime() / 1000), timezoneOffset: this.ahora().getTimezoneOffset() };
  }

  async estado(py, dir) {
    const d = this.dirFs(dir);
    const filas = await this.git.statusMatrix({ fs: this.fs, dir: d, filter: (f) => !this.dentroDeOtro(py, dir, f) });
    const preparados = [], sinPreparar = [], sinSeguimiento = [];
    for (const fila of filas) {
      const { preparado, sinPreparar: sp } = clasificar(fila);
      if (preparado) preparados.push({ ruta: fila[0], tipo: preparado });
      if (sp === "sin") sinSeguimiento.push(fila[0]); else if (sp) sinPreparar.push({ ruta: fila[0], tipo: sp });
    }
    let conflictos = [];
    try { conflictos = JSON.parse(await this.p.readFile(`${d}/.git/CC_CONFLICTOS`, "utf8")); } catch { /* sin merge pendiente */ }
    return { preparados, sinPreparar, sinSeguimiento, conflictos };
  }

  async decoraciones(d) {
    const mapa = new Map();
    const poner = (oid, nombre) => { if (!mapa.has(oid)) mapa.set(oid, []); mapa.get(oid).push(nombre); };
    const actual = await this.git.currentBranch({ fs: this.fs, dir: d }).catch(() => null);
    let headOid = null;
    try { headOid = await this.git.resolveRef({ fs: this.fs, dir: d, ref: "HEAD" }); } catch { /* sin commits */ }
    for (const b of await this.git.listBranches({ fs: this.fs, dir: d })) {
      try { const oid = await this.git.resolveRef({ fs: this.fs, dir: d, ref: `refs/heads/${b}` }); poner(oid, b === actual ? color.cian(color.negrita(`HEAD -> ${color.verde(b)}`)) : color.verde(b)); } catch { /* rama rota */ }
    }
    if (!actual && headOid) poner(headOid, color.cian(color.negrita("HEAD")));
    for (const r of await this.git.listRemotes({ fs: this.fs, dir: d })) {
      for (const b of await this.git.listBranches({ fs: this.fs, dir: d, remote: r.remote }).catch(() => [])) {
        if (b === "HEAD") continue;
        try { poner(await this.git.resolveRef({ fs: this.fs, dir: d, ref: `refs/remotes/${r.remote}/${b}` }), color.rojo(`${r.remote}/${b}`)); } catch { /* nada */ }
      }
    }
    for (const t of await this.git.listTags({ fs: this.fs, dir: d }).catch(() => [])) {
      try { let oid = await this.git.resolveRef({ fs: this.fs, dir: d, ref: `refs/tags/${t}` }); try { const tag = await this.git.readTag({ fs: this.fs, dir: d, oid }); oid = tag.tag.object; } catch { /* ligero */ } poner(oid, color.amarillo(`tag: ${t}`)); } catch { /* nada */ }
    }
    return mapa;
  }

  // ------------------------------------------------------------------ diff ----
  async textoEn(d, oid, ruta) {
    try { const { blob } = await this.git.readBlob({ fs: this.fs, dir: d, oid, filepath: ruta }); return textoOBinario(blob); } catch { return null; }
  }
  async textoIndice(d, ruta) {
    // El índice: si el archivo está preparado con contenido distinto, isomorphic-git no expone el blob directamente:
    // se usa walk(STAGE).
    let r = null;
    await this.git.walk({ fs: this.fs, dir: d, trees: [this.git.STAGE()], map: async (f, [e]) => {
      if (f === ".") return true;
      if (!ruta.startsWith(f) ) return null;
      if (f === ruta && e) { const oid = await e.oid(); const { blob } = await this.git.readBlob({ fs: this.fs, dir: d, oid }); r = textoOBinario(blob); }
      return f === ruta ? null : true;
    } });
    return r;
  }
  async textoTrabajo(d, ruta) { try { return textoOBinario(await this.p.readFile(`${d}/${ruta}`)); } catch { return null; } }
  formatoDiff(ruta, a, b) {
    if (a === b) return "";
    if (a?.startsWith(BIN) || b?.startsWith(BIN)) return `${color.negrita(`diff --git a/${ruta} b/${ruta}`)}\nBinary files ${a === null ? "/dev/null" : "a/" + ruta} and ${b === null ? "/dev/null" : "b/" + ruta} differ`;
    const sinFinal = (t) => (t === null ? null : t.replace(/\n$/, ""));
    return diffUnificado(ruta, sinFinal(a), sinFinal(b));
  }

  async diffCommits(d, oidA, oidB) {
    const partes = [];
    const arboles = [oidA ? this.git.TREE({ ref: oidA }) : null, this.git.TREE({ ref: oidB })].filter(Boolean);
    await this.git.walk({ fs: this.fs, dir: d, trees: oidA ? arboles : [this.git.TREE({ ref: oidB })], map: async (f, entradas) => {
      if (f === ".") return true;
      const [a, b] = oidA ? entradas : [null, entradas[0]];
      const ta = a ? await a.type() : null, tb = b ? await b.type() : null;
      if (ta === "tree" || tb === "tree") return true;
      const oa = a ? await a.oid() : null, ob = b ? await b.oid() : null;
      if (oa === ob) return null;
      const txt = async (e) => { if (!e) return null; return textoOBinario(await e.content()); };
      partes.push(this.formatoDiff(f, await txt(a), await txt(b)));
      return null;
    } });
    return partes.filter(Boolean).join("\n");
  }

  // ------------------------------------------------------------------ la orden git ----
  /**
   * @param {object} io { py, cwd, out, err, leerLinea, cambio() }
   * @returns {Promise<number>} código de salida
   */
  async ejecutar(args, io) {
    const { py, out, err } = io;
    const [orden, ...resto] = args;
    const sinRepo = ["init", "clone", "--version", "version", "help", "--help", "config"];
    if (!orden || orden === "help" || orden === "--help") { out(AYUDA); return 0; }
    if (orden === "--version" || orden === "version") { out("git version 2.45.0 (isomorphic-git, CódigoCamp)\n"); return 0; }
    if (orden === "init") return this.init(resto, io);
    if (orden === "clone") return this.clonar(resto, io);
    let dir = this.raizDe(py, io.cwd);
    if (dir === null && py.git.initialized && orden !== "config") dir = await this.migrar(py, io);
    if (dir === null) {
      if (orden === "config" && resto.includes("--global")) return this.config(null, resto, io);
      err("fatal: not a git repository (or any of the parent directories): .git\nEjecuta primero: git init   o   git clone <url>\n");
      return 128;
    }
    if (!sinRepo.includes(orden) || orden === "config") {
      try { if (!(await this.asegurarGit(py, dir, io))) { err("fatal: no se encontró el historial de este repositorio (.git).\n"); return 128; } }
      catch (e) { err(`fatal: ${this.mensaje(e)}\n`); return 128; }
    }
    const d = this.dirFs(dir);
    const ctx = { ...io, dir, d };
    try {
      await this.haciaGit(py, dir);
      if (orden === "stash" || orden === "cherry-pick") {
        // Estas órdenes leen el autor de .git/config: se completa con el de CódigoCamp si falta.
        const a2 = await this.autorDe(d);
        if (!(await this.git.getConfig({ fs: this.fs, dir: d, path: "user.name" }).catch(() => null))) await this.git.setConfig({ fs: this.fs, dir: d, path: "user.name", value: a2.name });
        if (!(await this.git.getConfig({ fs: this.fs, dir: d, path: "user.email" }).catch(() => null))) await this.git.setConfig({ fs: this.fs, dir: d, path: "user.email", value: a2.email });
      }
      const r = await this.orden(orden, resto, ctx);
      return r ?? 0;
    } catch (e) {
      err(`${e.code === "NotFoundError" ? "fatal: " : "error: "}${this.mensaje(e)}\n`);
      return e.code === "NotFoundError" ? 128 : 1;
    }
  }

  mensaje(e) {
    const m = e?.message || String(e);
    switch (e?.code) {
      case "CheckoutConflictError": return `Your local changes to the following files would be overwritten by checkout:\n\t${(e.data?.filepaths || []).join("\n\t")}\nPlease commit your changes or stash them before you switch branches.`;
      case "MergeNotSupportedError": return "Ese merge no se puede hacer automáticamente aquí.";
      case "MergeConflictError": return `Automatic merge failed; fix conflicts and then commit the result.\n${(e.data?.filepaths || []).map((f) => `CONFLICT (content): Merge conflict in ${f}`).join("\n")}`;
      case "FastForwardError": return "Not possible to fast-forward, aborting. Usa git pull (sin --ff-only) o git merge.";
      case "PushRejectedError": return `failed to push some refs\nhint: Updates were rejected because the remote contains work that you do not have locally.\nhint: Haz primero git pull y vuelve a intentar git push.`;
      case "HttpError": {
        const s = e.data?.statusCode;
        if (s === 403 && this.credencial?.usuario) return `Permission denied (403): tu cuenta de GitHub @${this.credencial.usuario} no puede escribir en ese repositorio.\nRevisa que el repositorio sea tuyo (o que te hayan dado acceso) y, si es de una organización, que la organización haya autorizado a CódigoCamp.`;
        if (s === 401) return "Authentication failed (401): GitHub rechazó la sesión o el token. Vuelve a intentarlo: se te pedirá iniciar sesión otra vez.";
        if (s === 403) return "Authentication failed (403). El token no tiene permiso de escritura («Contents: Read and write») sobre ese repositorio.";
        if (s === 404) return "repository not found (¿la URL es correcta? ¿es privado? entonces necesitas un token).";
        return `HTTP ${s} ${e.data?.statusMessage || ""}`.trim();
      }
      case "UserCanceledError": return "Authentication failed: hace falta iniciar sesión en GitHub (o un token).";
      case "NotFoundError": return m.replace(/^Could not find /, "no se encontró ");
      case "AlreadyExistsError": return m;
      default: return m;
    }
  }

  /** Token para esa URL: la sesión de GitHub (solo github.com) o el token escrito a mano en esta pestaña. */
  tokenPara(url) { return this.credencial?.tokenPara(url) || this.token; }
  olvidarToken(url) { if (this.credencial?.tokenPara(url)) this.credencial.invalidar(); else this.token = null; }

  async pedirToken(io, motivo = "", url = this.urlRed) {
    if (this.credencial && /github\.com/i.test(url || "")) {
      io.out(color.gris("Iniciando sesión en GitHub… (se abrió un cuadro en la pantalla)\n"));
      const t = await this.credencial.obtener({ motivo: `${motivo}${url ? `Repositorio: ${url}` : ""}`.trim() || undefined });
      if (t) io.out(`${color.verde("✔")} Sesión iniciada en GitHub como ${color.azul("@" + (this.credencial.usuario || "?"))}\n`);
      return t;
    }
    io.out(color.gris(`${motivo}Necesitas un token personal de GitHub (github.com/settings/tokens) con permiso «Contents: Read and write».\nSe escribe oculto, solo se usa en esta pestaña y NO se guarda.\n`));
    const t = (await io.leerLinea("Token de GitHub: ", { secreto: true }))?.trim();
    if (!t) return null;
    if (/\s/.test(t)) { io.err("Ese token no es válido (no puede tener espacios).\n"); return null; }
    this.token = t;
    return t;
  }

  /** Ejecuta una operación de red; si pide autenticación, pide el token y la repite una vez. */
  async conRed(io, fn, { siempreToken = false, url = "" } = {}) {
    this.urlRed = url || "";
    if (siempreToken && !this.tokenPara(url) && !(await this.pedirToken(io, "", url))) throw Object.assign(new Error("Authentication failed: hace falta iniciar sesión en GitHub."), { code: "x" });
    try { return await fn(); }
    catch (e) {
      const s = e.data?.statusCode;
      const sinPermiso = e.code === "UserCanceledError" || (e.code === "HttpError" && (s === 401 || s === 403 || s === 404));
      if (sinPermiso && !this.tokenPara(url)) {
        if (!(await this.pedirToken(io, "El repositorio pidió autenticación (o es privado). ", url))) throw e;
        return fn();
      }
      // 401 = sesión o token vencido/revocado: se olvida y se pide iniciar sesión otra vez (una sola vez).
      // 403 con la sesión de GitHub = la cuenta es válida pero no tiene permiso en ESE repositorio: no se cierra la sesión.
      if (e.code === "HttpError" && (s === 401 || s === 403) && this.tokenPara(url)) {
        const eraSesion = Boolean(this.credencial?.tokenPara(url));
        if (s === 401 || !eraSesion) this.olvidarToken(url);
        if (eraSesion && s === 401 && (await this.pedirToken(io, "GitHub rechazó la sesión guardada (venció o la revocaste). ", url))) return fn();
      }
      throw e;
    }
  }

  async urlDeRemoto(d, remoto) {
    try { return (await this.git.listRemotes({ fs: this.fs, dir: d })).find((r) => r.remote === remoto)?.url || ""; } catch { return ""; }
  }

  progreso(io) {
    let ultima = "";
    const fases = { "Counting objects": "Contando objetos", "Compressing objects": "Comprimiendo objetos", "Receiving objects": "Recibiendo objetos", "Resolving deltas": "Resolviendo deltas", "Analyzing workdir": "Analizando archivos", "Updating workdir": "Actualizando archivos" };
    return ({ phase, loaded, total }) => {
      const pct = total ? Math.floor((loaded / total) * 100) : null;
      const linea = `${fases[phase] || phase}: ${pct !== null ? `${pct}% (${loaded}/${total})` : loaded}`;
      const clave = `${phase}:${pct !== null ? Math.floor(pct / 25) : ""}`;
      if (clave !== ultima) { ultima = clave; io.out(color.gris(linea + "\n")); }
    };
  }

  async terminarCambios(ctx, { trabajo = true, historial = true } = {}) {
    const { py, dir } = ctx;
    let cambio = false;
    if (trabajo) cambio = (await this.desdeGit(py, dir, ctx)) || cambio;
    if (historial) {
      const d = this.dirFs(dir);
      const info = this.repos(py)[dir] ?? (this.repos(py)[dir] = { remote: "", respaldo: "", rama: "" });
      info.rama = (await this.git.currentBranch({ fs: this.fs, dir: d }).catch(() => null)) || info.rama || "";
      info.remote = (await this.git.listRemotes({ fs: this.fs, dir: d }).catch(() => [])).find((r) => r.remote === "origin")?.url || "";
      cambio = (await this.respaldar(py, dir, ctx)) || cambio;
      cambio = true;
    }
    if (cambio) ctx.cambio?.();
  }

  async migrar(py, io) {
    // Proyectos con el Git anterior de CódigoCamp (sin historial real): se crea un repositorio de verdad con su último commit.
    const g = py.git;
    const d = this.dirFs("");
    io.out(color.gris("Actualizando Git de este proyecto a Git real…\n"));
    this.repos(py)[""] = { remote: g.remote || "", respaldo: "", rama: g.branch || "main" };
    await this.git.init({ fs: this.fs, dir: d, defaultBranch: g.branch || "main" });
    if (g.remote) await this.git.addRemote({ fs: this.fs, dir: d, remote: "origin", url: g.remote, force: true });
    if (g.commits.length) {
      await this.mkdirp(d);
      for (const [ruta, valor] of Object.entries(g.committed)) {
        const datos = esMarcador(valor) ? (this.archivos ? await this.archivos.bytes(valor) : null) : valor;
        if (datos === null) continue;
        await this.mkdirp(`${d}/${FS.carpetaDe(ruta)}`);
        await this.p.writeFile(`${d}/${ruta}`, datos, typeof datos === "string" ? "utf8" : undefined);
        await this.git.add({ fs: this.fs, dir: d, filepath: ruta });
      }
      await this.git.commit({ fs: this.fs, dir: d, message: `${g.commits[0].message}\n\n(Historial anterior de CódigoCamp: ${g.commits.length} commits)`, author: await this.autorDe(d) });
      await this.guardarCache("", {});
    }
    Object.assign(g, { initialized: false, staged: [], tracked: [], committed: {}, commits: [], branches: {}, remote: "" });
    io.cambio?.();
    return "";
  }

  // ------------------------------------------------------------------ órdenes ----
  async init(args, io) {
    const { py, out, err } = io;
    let rama = "main";
    const pos = [];
    for (let i = 0; i < args.length; i++) {
      if (args[i] === "-b" || args[i] === "--initial-branch") rama = args[++i] ?? "main";
      else if (args[i].startsWith("--initial-branch=")) rama = args[i].slice(17);
      else if (!args[i].startsWith("-")) pos.push(args[i]);
    }
    if (!NOMBRE_RAMA.test(rama)) { err(`fatal: invalid initial branch name: '${rama}'\n`); return 128; }
    const dir = FS.resolver(io.cwd, pos[0] ?? ".");
    if (dir === null) { err("fatal: ruta no válida\n"); return 128; }
    if (FS.tieneArchivo(py, dir)) { err(`fatal: '${pos[0]}' ya existe y no es una carpeta\n`); return 128; }
    const existente = this.repos(py)[dir];
    const d = this.dirFs(dir);
    if (existente && await this.existe(`${d}/.git/HEAD`)) { out(`Reinitialized existing Git repository in /workspace/${dir ? dir + "/" : ""}.git/\n`); return 0; }
    const padre = this.raizDe(py, dir);
    if (dir && !FS.esCarpeta(py, dir)) FS.crearCarpeta(py, dir, { padres: true });
    await this.mkdirp(d);
    await this.git.init({ fs: this.fs, dir: d, defaultBranch: rama });
    this.repos(py)[dir] = { remote: "", respaldo: "", rama };
    if (py.git.initialized && dir === "") Object.assign(py.git, { initialized: false, staged: [], tracked: [], committed: {}, commits: [], branches: {} });
    out(`Initialized empty Git repository in /workspace/${dir ? dir + "/" : ""}.git/\n`);
    if (padre !== null && padre !== dir) out(color.gris(`(Queda dentro del repositorio de ${padre || "la raíz"}, como un repositorio anidado.)\n`));
    await this.terminarCambios({ ...io, dir, d }, { trabajo: false });
    return 0;
  }

  async clonar(args, io) {
    const { py, out, err } = io;
    let rama, profundidad, unaRama = false;
    const pos = [];
    for (let i = 0; i < args.length; i++) {
      const x = args[i];
      if (x === "-b" || x === "--branch") rama = args[++i];
      else if (x.startsWith("--branch=")) rama = x.slice(9);
      else if (x === "--depth") profundidad = Number(args[++i]);
      else if (x.startsWith("--depth=")) profundidad = Number(x.slice(8));
      else if (x === "--single-branch") unaRama = true;
      else if (x === "-o" || x === "--origin" || x === "--filter" || x === "-c" || x === "--config") i++;
      else if (!x.startsWith("-")) pos.push(x);
    }
    const [urlDada, carpeta] = pos;
    if (!urlDada) { err("usage: git clone <url> [carpeta]\n  ej.: git clone https://github.com/usuario/repositorio.git\n"); return 129; }
    let url = urlDada.trim();
    if (/^[\w.-]+\/[\w.-]+$/.test(url)) url = `https://github.com/${url}`;
    const m = /^https:\/\/([^/]+)\/(.+?)(?:\.git)?\/?$/.exec(url);
    if (!m) { err(`fatal: '${urlDada}' no es una URL https:// de un repositorio (ej.: https://github.com/usuario/repo.git)\n`); return 128; }
    if (rama !== undefined && !NOMBRE_RAMA.test(rama)) { err(`fatal: '${rama}' no es un nombre de rama válido.\n`); return 128; }
    const nombre = m[2].split("/").pop();
    const dir = FS.resolver(io.cwd, carpeta ?? nombre);
    if (dir === null) { err(`fatal: '${carpeta ?? nombre}' no es un nombre de carpeta válido aquí.\n`); return 128; }
    if (FS.tieneArchivo(py, dir)) { err(`fatal: destination path '${carpeta ?? nombre}' already exists and is not a directory.\n`); return 128; }
    const ocupado = dir === "" ? Object.keys(py.files).length > 0 : FS.archivosEn(py, dir).length > 0;
    if (ocupado) {
      err(`fatal: destination path '${carpeta ?? nombre}' already exists and is not an empty directory.\n`);
      if (dir === "") err(color.gris("Para clonar en la raíz el proyecto debe estar vacío. O clónalo en una carpeta: git clone <url>\n"));
      return 128;
    }
    const d = this.dirFs(dir);
    await this.borrarArbol(d === this.raiz ? `${this.raiz}/.git` : d);
    await this.guardarCache(dir, {});
    await this.mkdirp(d);
    out(`Cloning into '${carpeta ?? (dir === "" ? "." : nombre)}'...\n`);
    const urlGit = url.endsWith(".git") ? url : `${url}.git`;
    try {
      await this.conRed(io, () => this.git.clone({ ...this.red(), dir: d, url: urlGit, ref: rama, singleBranch: unaRama, depth: profundidad || undefined, onProgress: this.progreso(io), noTags: false }), { url: urlGit });
    } catch (e) {
      await this.borrarArbol(d === this.raiz ? `${this.raiz}/.git` : d);
      err(`fatal: ${this.mensaje(e)}\n`);
      return 128;
    }
    if (dir && !FS.esCarpeta(py, dir)) FS.crearCarpeta(py, dir, { padres: true });
    this.repos(py)[dir] = { remote: urlGit, respaldo: "", rama: "" };
    const ctx = { ...io, dir, d };
    await this.terminarCambios(ctx);
    const commits = await this.git.log({ fs: this.fs, dir: d }).catch(() => []);
    const ramas = await this.git.listBranches({ fs: this.fs, dir: d, remote: "origin" }).catch(() => []);
    out(`${color.verde("✔")} ${Object.keys(py.files).filter((r) => !dir || r.startsWith(dir + "/")).length} archivos · ${commits.length} commits${profundidad ? " (historial recortado con --depth)" : ""} · ${ramas.filter((b) => b !== "HEAD").length} ramas en origin · rama ${this.repos(py)[dir].rama}\n`);
    if (dir) out(color.gris(`Entra con: cd ${carpeta ?? nombre}\n`));
    return 0;
  }

  async config(ctx, args, io) {
    const global = args.includes("--global");
    const a = args.filter((x) => !x.startsWith("--") || x === "--list" || x === "--unset");
    const lista = a.includes("--list") || args.includes("-l");
    const almacen = globalThis.localStorage;
    if (global) {
      const leer = () => { try { return JSON.parse(almacen?.getItem(this.claveGlobal) || "{}"); } catch { return {}; } };
      const datos = leer();
      if (lista) { io.out(Object.entries(datos).map(([k, v]) => `${k}=${v}`).join("\n") + (Object.keys(datos).length ? "\n" : "")); return 0; }
      const [clave, valor] = a.filter((x) => x !== "--unset");
      if (!clave) { io.err("usage: git config --global <clave> [valor]\n"); return 129; }
      if (args.includes("--unset")) delete datos[clave]; else if (valor === undefined) { if (datos[clave] === undefined) return 1; io.out(`${datos[clave]}\n`); return 0; } else datos[clave] = valor;
      try { almacen?.setItem(this.claveGlobal, JSON.stringify(datos)); } catch { /* sin almacenamiento */ }
      return 0;
    }
    const { d } = ctx;
    if (lista) {
      const claves = ["user.name", "user.email", "core.bare", "remote.origin.url", "init.defaultbranch"];
      for (const k of claves) { const v = await this.git.getConfig({ fs: this.fs, dir: d, path: k }).catch(() => undefined); if (v !== undefined) io.out(`${k}=${v}\n`); }
      return 0;
    }
    const [clave, valor] = a.filter((x) => x !== "--unset" && x !== "--local");
    if (!clave) { io.err("usage: git config <clave> [valor]\n"); return 129; }
    if (args.includes("--unset")) { await this.git.setConfig({ fs: this.fs, dir: d, path: clave, value: undefined }); }
    else if (valor === undefined) {
      const v = await this.git.getConfig({ fs: this.fs, dir: d, path: clave });
      if (v === undefined) return 1;
      io.out(`${v}\n`); return 0;
    } else await this.git.setConfig({ fs: this.fs, dir: d, path: clave, value: valor });
    await this.terminarCambios(ctx, { trabajo: false });
    return 0;
  }

  async rutasDe(ctx, lista) {
    // Convierte rutas de la línea de órdenes (relativas al cwd) en rutas dentro del repositorio.
    const { py, dir, cwd } = ctx;
    const salida = [];
    for (const x of lista) {
      const abs = FS.resolver(cwd, x);
      if (abs === null) continue;
      const rel = dir ? (abs === dir ? "." : abs.startsWith(dir + "/") ? abs.slice(dir.length + 1) : null) : (abs === "" ? "." : abs);
      if (rel === null) throw new Error(`fatal: ${x}: '${x}' is outside repository`);
      salida.push(rel);
    }
    return salida;
  }

  async orden(orden, a, ctx) {
    const { py, out, err, d, dir } = ctx;
    const g = this.git, fs = this.fs;
    switch (orden) {
      case "status": {
        const corto = a.includes("-s") || a.includes("--short") || a.includes("--porcelain");
        const rama = await g.currentBranch({ fs, dir: d }).catch(() => null);
        const { preparados, sinPreparar, sinSeguimiento, conflictos } = await this.estado(py, dir);
        const L = { nuevo: "A", modificado: "M", eliminado: "D" };
        if (corto) {
          const mapa = new Map();
          for (const p of preparados) mapa.set(p.ruta, [L[p.tipo], " "]);
          for (const p of sinPreparar) mapa.set(p.ruta, [(mapa.get(p.ruta) || [" "])[0], L[p.tipo]]);
          for (const r of sinSeguimiento) mapa.set(r, ["?", "?"]);
          for (const [r, [x, y]] of [...mapa].sort()) out(`${x === "?" ? color.rojo("??") : color.verde(x) + color.rojo(y)} ${r}\n`);
          return 0;
        }
        out(rama ? `On branch ${rama}\n` : `HEAD detached\n`);
        let headOk = true;
        try { await g.resolveRef({ fs, dir: d, ref: "HEAD" }); } catch { headOk = false; out("\nNo commits yet\n"); }
        if (headOk && rama) {
          const seg = await this.seguimiento(d, rama);
          if (seg) out(seg + "\n");
        }
        if (conflictos.length) out(`\nYou have unmerged paths.\n  (fix conflicts and run "git commit")\n\nUnmerged paths:\n${conflictos.map((f) => color.rojo(`\tboth modified:   ${f}`)).join("\n")}\n`);
        const ETQ = { nuevo: "new file:   ", modificado: "modified:   ", eliminado: "deleted:    " };
        if (preparados.length) out(`\nChanges to be committed:\n  (use "git restore --staged <file>..." to unstage)\n${preparados.map((p) => color.verde(`\t${ETQ[p.tipo]}${p.ruta}`)).join("\n")}\n`);
        if (sinPreparar.length) out(`\nChanges not staged for commit:\n  (use "git add <file>..." to update what will be committed)\n  (use "git restore <file>..." to discard changes in working directory)\n${sinPreparar.map((p) => color.rojo(`\t${ETQ[p.tipo]}${p.ruta}`)).join("\n")}\n`);
        if (sinSeguimiento.length) out(`\nUntracked files:\n  (use "git add <file>..." to include in what will be committed)\n${sinSeguimiento.map((r) => color.rojo(`\t${r}`)).join("\n")}\n`);
        if (!preparados.length && !sinPreparar.length && !sinSeguimiento.length) out(`\n${headOk ? "nothing to commit, working tree clean" : 'nothing to commit (create/copy files and use "git add" to track)'}\n`);
        else if (!preparados.length) out(`\n${sinPreparar.length ? 'no changes added to commit (use "git add" and/or "git commit -a")' : 'nothing added to commit but untracked files present (use "git add" to track)'}\n`);
        return 0;
      }
      case "add": {
        const todo = a.includes("-A") || a.includes("--all") || a.includes(".");
        const rutas = await this.rutasDe(ctx, a.filter((x) => !x.startsWith("-")));
        if (!rutas.length && !todo) { err("Nothing specified, nothing added.\nhint: Maybe you wanted to say 'git add .'?\n"); return 0; }
        const filas = await g.statusMatrix({ fs, dir: d, filter: (f) => !this.dentroDeOtro(py, dir, f) });
        const dentro = (f) => todo || rutas.some((r) => r === "." || f === r || f.startsWith(r.replace(/\/$/, "") + "/"));
        let n = 0;
        for (const [f, head, work, stage] of filas) {
          if (!dentro(f)) continue;
          if (work === 0 && stage !== 0) { await g.remove({ fs, dir: d, filepath: f }); n++; }
          else if (work !== 0 && !(head === 1 && work === 1 && stage === 1) && stage !== 2) { await g.add({ fs, dir: d, filepath: f }); n++; }
        }
        if (!todo) for (const r of rutas) if (r !== "." && !filas.some(([f]) => f === r || f.startsWith(r + "/")) && !(await this.existe(`${d}/${r}`))) { err(`fatal: pathspec '${r}' did not match any files\n`); return 128; }
        await this.terminarCambios(ctx, { trabajo: false });
        return 0;
      }
      case "rm": {
        const cached = a.includes("--cached");
        const rutas = await this.rutasDe(ctx, a.filter((x) => !x.startsWith("-")));
        if (!rutas.length) { err("usage: git rm [--cached] [-r] <file>...\n"); return 129; }
        const seguidos = await g.listFiles({ fs, dir: d });
        for (const r of rutas) {
          const lista = seguidos.filter((f) => f === r || f.startsWith(r + "/"));
          if (!lista.length) { err(`fatal: pathspec '${r}' did not match any files\n`); return 128; }
          if (lista.length > 1 && !a.includes("-r")) { err(`fatal: not removing '${r}' recursively without -r\n`); return 128; }
          for (const f of lista) { await g.remove({ fs, dir: d, filepath: f }); if (!cached) { try { await this.p.unlink(`${d}/${f}`); } catch { /* ya no estaba */ } } out(`rm '${f}'\n`); }
        }
        await this.terminarCambios(ctx, { trabajo: !cached });
        return 0;
      }
      case "mv": {
        const [de, a2] = await this.rutasDe(ctx, a.filter((x) => !x.startsWith("-")));
        if (!de || !a2) { err("usage: git mv <origen> <destino>\n"); return 129; }
        await this.mkdirp(`${d}/${FS.carpetaDe(a2)}`);
        await this.p.rename(`${d}/${de}`, `${d}/${a2}`);
        await g.remove({ fs, dir: d, filepath: de });
        await g.add({ fs, dir: d, filepath: a2 });
        await this.terminarCambios(ctx);
        return 0;
      }
      case "commit": {
        let mensaje = null, todo = false, enmendar = false, vacio = false;
        for (let i = 0; i < a.length; i++) {
          const x = a[i];
          if (x === "-m" || x === "--message") mensaje = (mensaje ? mensaje + "\n\n" : "") + (a[++i] ?? "");
          else if (x.startsWith("--message=")) mensaje = x.slice(10);
          else if (x === "-a" || x === "--all") todo = true;
          else if (x === "-am" || x === "-ma") { todo = true; mensaje = a[++i] ?? ""; }
          else if (x === "--amend") enmendar = true;
          else if (x === "--allow-empty") vacio = true;
          else if (x === "--no-edit") { /* nada */ }
        }
        if (todo) {
          for (const [f, head, work, stage] of await g.statusMatrix({ fs, dir: d })) {
            if (head === 1 && work === 0 && stage !== 0) await g.remove({ fs, dir: d, filepath: f });
            else if (head === 1 && work === 2) await g.add({ fs, dir: d, filepath: f });
          }
        }
        let padre;
        let mergeHead = null;
        try { mergeHead = (await this.p.readFile(`${d}/.git/MERGE_HEAD`, "utf8")).trim(); } catch { /* no hay merge pendiente */ }
        const { preparados } = await this.estado(py, dir);
        let anterior = null;
        try { anterior = await g.resolveRef({ fs, dir: d, ref: "HEAD" }); } catch { /* primer commit */ }
        if (enmendar) {
          if (!anterior) { err("fatal: You have nothing to amend.\n"); return 128; }
          const c = await g.readCommit({ fs, dir: d, oid: anterior });
          padre = c.commit.parent;
          if (mensaje === null) mensaje = c.commit.message.trim();
        } else if (!preparados.length && !vacio && !mergeHead) {
          const e = await this.estado(py, dir);
          const rama = await g.currentBranch({ fs, dir: d }).catch(() => "main");
          out(`On branch ${rama}\n${e.sinPreparar.length ? 'no changes added to commit (use "git add" and/or "git commit -a")' : e.sinSeguimiento.length ? 'nothing added to commit but untracked files present (use "git add" to track)' : "nothing to commit, working tree clean"}\n`);
          return 1;
        }
        if (mensaje === null) {
          mensaje = (await ctx.leerLinea("Mensaje del commit: ", {}))?.trim() || "";
          if (!mensaje) { err("Aborting commit due to empty commit message.\n"); return 1; }
        }
        if (!mensaje.trim()) { err("Aborting commit due to empty commit message.\n"); return 1; }
        const conflictos = (await this.estado(py, dir)).conflictos;
        if (conflictos.length) {
          for (const f of conflictos) { const t = await this.textoTrabajo(d, f); if (t && /^<<<<<<< /m.test(t)) { err(`error: Committing is not possible because you have unmerged files.\nhint: Fix them up in the work tree (${f} todavía tiene marcas <<<<<<<), then use 'git add <file>'.\n`); return 128; } }
        }
        const autor = await this.autorDe(d);
        if (mergeHead && anterior) padre = [anterior, mergeHead];
        const oid = await g.commit({ fs, dir: d, message: mensaje, author: autor, ...(padre ? { parent: padre } : {}) });
        if (mergeHead) { await this.p.unlink(`${d}/.git/MERGE_HEAD`).catch(() => {}); await this.p.unlink(`${d}/.git/CC_CONFLICTOS`).catch(() => {}); }
        const rama = await g.currentBranch({ fs, dir: d }).catch(() => null);
        const cambios = await this.diffCommits(d, enmendar ? (padre?.[0] ?? null) : anterior, oid);
        const plano = quitarColor(cambios);
        const nArch = (plano.match(/^diff --git/gm) || []).length;
        const mas = (plano.match(/^\+(?!\+\+ )/gm) || []).length, menos = (plano.match(/^-(?!-- )/gm) || []).length;
        out(`[${rama || "HEAD desacoplado"}${anterior ? "" : " (root-commit)"} ${corto(oid)}] ${primera(mensaje)}\n ${nArch} file${nArch === 1 ? "" : "s"} changed, ${mas} insertion${mas === 1 ? "" : "s"}(+), ${menos} deletion${menos === 1 ? "" : "s"}(-)\n`);
        await this.terminarCambios(ctx, { trabajo: false });
        return 0;
      }
      case "log": {
        let n, oneline = false, grafo = false, todas = false, ref = "HEAD", ruta = null, stat = false, autorF = null;
        for (let i = 0; i < a.length; i++) {
          const x = a[i];
          if (x === "--oneline") oneline = true;
          else if (x === "--graph") grafo = true;
          else if (x === "--all") todas = true;
          else if (x === "--stat") stat = true;
          else if (x === "-n" || x === "--max-count") n = Number(a[++i]);
          else if (/^-\d+$/.test(x)) n = Number(x.slice(1));
          else if (x.startsWith("--max-count=")) n = Number(x.slice(12));
          else if (x.startsWith("--author=")) autorF = x.slice(9).toLowerCase();
          else if (x === "--") { ruta = a[i + 1]; break; }
          else if (x === "--decorate" || x.startsWith("--pretty") || x.startsWith("--format")) { if (x.includes("oneline")) oneline = true; }
          else if (!x.startsWith("-")) ref = x;
        }
        let commits;
        try {
          if (todas) {
            const vistos = new Map();
            const refs = [...(await g.listBranches({ fs, dir: d })).map((b) => `refs/heads/${b}`)];
            for (const r of await g.listRemotes({ fs, dir: d })) for (const b of await g.listBranches({ fs, dir: d, remote: r.remote })) if (b !== "HEAD") refs.push(`refs/remotes/${r.remote}/${b}`);
            for (const r of refs) for (const c of await g.log({ fs, dir: d, ref: r })) vistos.set(c.oid, c);
            commits = [...vistos.values()].sort((x, y) => y.commit.committer.timestamp - x.commit.committer.timestamp);
          } else commits = await g.log({ fs, dir: d, ref, ...(ruta ? { filepath: (await this.rutasDe(ctx, [ruta]))[0] } : {}) });
        } catch (e) {
          if (e.code === "NotFoundError" && ref === "HEAD") { err(`fatal: your current branch '${await g.currentBranch({ fs, dir: d }).catch(() => "main")}' does not have any commits yet\n`); return 128; }
          throw e;
        }
        if (autorF) commits = commits.filter((c) => `${c.commit.author.name} ${c.commit.author.email}`.toLowerCase().includes(autorF));
        if (n) commits = commits.slice(0, n);
        const deco = await this.decoraciones(d);
        const dec = (oid) => (deco.get(oid) ? ` ${color.amarillo("(")}${deco.get(oid).join(color.amarillo(", "))}${color.amarillo(")")}` : "");
        const pre = grafo ? "* " : "";
        const lineas = [];
        for (const c of commits) {
          if (oneline) { lineas.push(`${pre}${color.amarillo(corto(c.oid))}${dec(c.oid)} ${primera(c.commit.message)}`); continue; }
          const au = c.commit.author;
          lineas.push(`${pre}${color.amarillo(`commit ${c.oid}`)}${dec(c.oid)}`);
          if (c.commit.parent.length > 1) lineas.push(`${grafo ? "| " : ""}Merge: ${c.commit.parent.map(corto).join(" ")}`);
          lineas.push(`${grafo ? "| " : ""}Author: ${au.name} <${au.email}>`, `${grafo ? "| " : ""}Date:   ${fechaGit(au.timestamp, au.timezoneOffset)}`, grafo ? "|" : "");
          for (const l of c.commit.message.trimEnd().split("\n")) lineas.push(`${grafo ? "| " : ""}    ${l}`);
          if (stat) {
            const diff = await this.diffCommits(d, c.commit.parent[0] ?? null, c.oid);
            const archivos = [...quitarColor(diff).matchAll(/diff --git a\/(\S+)/g)].map((m) => m[1]);
            if (archivos.length) lineas.push("", ...archivos.map((f) => ` ${f}`), ` ${archivos.length} file${archivos.length === 1 ? "" : "s"} changed`);
          }
          lineas.push(grafo ? "|" : "");
        }
        out(lineas.join("\n") + (lineas.length ? "\n" : ""));
        return 0;
      }
      case "show": {
        const ref = a.find((x) => !x.startsWith("-")) || "HEAD";
        if (ref.includes(":")) {
          const [r, ruta] = ref.split(":");
          const oid = await g.resolveRef({ fs, dir: d, ref: r || "HEAD" }).catch(() => g.expandOid({ fs, dir: d, oid: r }));
          const t = await this.textoEn(d, oid, ruta);
          if (t === null) { err(`fatal: path '${ruta}' does not exist in '${r}'\n`); return 128; }
          out(t.startsWith(BIN) ? "(archivo binario)\n" : t + (t.endsWith("\n") ? "" : "\n"));
          return 0;
        }
        const oid = await this.resolver(d, ref);
        const c = await g.readCommit({ fs, dir: d, oid });
        const au = c.commit.author;
        const deco = await this.decoraciones(d);
        out(`${color.amarillo(`commit ${oid}`)}${deco.get(oid) ? ` (${deco.get(oid).join(", ")})` : ""}\nAuthor: ${au.name} <${au.email}>\nDate:   ${fechaGit(au.timestamp, au.timezoneOffset)}\n\n${c.commit.message.trimEnd().split("\n").map((l) => "    " + l).join("\n")}\n\n`);
        if (!a.includes("--no-patch") && !a.includes("-s")) out((await this.diffCommits(d, c.commit.parent[0] ?? null, oid)) + "\n");
        return 0;
      }
      case "diff": {
        const preparado = a.includes("--staged") || a.includes("--cached");
        const nombres = a.includes("--name-only");
        const refs = a.filter((x) => !x.startsWith("-"));
        const corte = a.indexOf("--");
        const rutas = corte >= 0 ? await this.rutasDe(ctx, a.slice(corte + 1)) : [];
        const sel = (f) => !rutas.length || rutas.some((r) => r === "." || f === r || f.startsWith(r + "/"));
        if (refs.length && corte < 0) {
          const [x, y] = refs.length === 1 && refs[0].includes("..") ? refs[0].split("..") : refs;
          const ox = await this.resolver(d, x);
          if (y) { const t = await this.diffCommits(d, ox, await this.resolver(d, y)); out(t ? t + "\n" : ""); return 0; }
          // diff <commit> → contra el árbol de trabajo
          const partes = [];
          for (const [f, , work] of await g.statusMatrix({ fs, dir: d, ref: ox })) {
            const antes = await this.textoEn(d, ox, f), despues = work === 0 ? null : await this.textoTrabajo(d, f);
            if (antes !== despues) partes.push(this.formatoDiff(f, antes, despues));
          }
          out(partes.filter(Boolean).join("\n") + (partes.length ? "\n" : ""));
          return 0;
        }
        let head = null;
        try { head = await g.resolveRef({ fs, dir: d, ref: "HEAD" }); } catch { /* sin commits */ }
        const partes = [];
        for (const fila of await g.statusMatrix({ fs, dir: d })) {
          const [f, h, w, s] = fila;
          if (!sel(f)) continue;
          if (preparado) {
            if (!((h === 0 && s !== 0) || (h === 1 && s === 0) || (h === 1 && (s === 2 || s === 3)))) continue;
            const antes = h ? await this.textoEn(d, head, f) : null;
            const despues = s === 0 ? null : s === 2 ? await this.textoTrabajo(d, f) : await this.textoIndice(d, f);
            partes.push(nombres ? f : this.formatoDiff(f, antes, despues));
          } else {
            if (s === 0 || !((s === 1 && w === 2) || s === 3 || w === 0)) continue;
            const antes = s === 1 ? await this.textoEn(d, head, f) : await this.textoIndice(d, f);
            const despues = w === 0 ? null : await this.textoTrabajo(d, f);
            partes.push(nombres ? f : this.formatoDiff(f, antes, despues));
          }
        }
        const t = partes.filter(Boolean).join("\n");
        out(t ? t + "\n" : "");
        return 0;
      }
      case "branch": {
        const del = a.includes("-d") || a.includes("-D") || a.includes("--delete");
        const mover = a.includes("-m") || a.includes("-M") || a.includes("--move");
        const todas = a.includes("-a") || a.includes("--all"), remotas = a.includes("-r") || a.includes("--remotes");
        const pos = a.filter((x) => !x.startsWith("-"));
        const actual = await g.currentBranch({ fs, dir: d }).catch(() => null);
        if (a.includes("--show-current")) { out(`${actual ?? ""}\n`); return 0; }
        if (del) {
          for (const b of pos) {
            if (b === actual) { err(`error: Cannot delete branch '${b}' checked out at '/workspace/${dir}'\n`); return 1; }
            const oid = await g.resolveRef({ fs, dir: d, ref: `refs/heads/${b}` }).catch(() => null);
            if (!oid) { err(`error: branch '${b}' not found.\n`); return 1; }
            if (!a.includes("-D")) {
              const head = await g.resolveRef({ fs, dir: d, ref: "HEAD" });
              const unida = head === oid || await g.isDescendent({ fs, dir: d, oid: head, ancestor: oid }).catch(() => false);
              if (!unida) { err(`error: The branch '${b}' is not fully merged.\nIf you are sure you want to delete it, run 'git branch -D ${b}'.\n`); return 1; }
            }
            await g.deleteBranch({ fs, dir: d, ref: b });
            out(`Deleted branch ${b} (was ${corto(oid)}).\n`);
          }
          await this.terminarCambios(ctx, { trabajo: false });
          return 0;
        }
        if (mover) {
          const [viejo, nuevo] = pos.length === 1 ? [actual, pos[0]] : pos;
          if (!NOMBRE_RAMA.test(nuevo || "")) { err(`fatal: '${nuevo}' is not a valid branch name\n`); return 128; }
          await g.renameBranch({ fs, dir: d, oldref: viejo, ref: nuevo, checkout: viejo === actual });
          await this.terminarCambios(ctx, { trabajo: false });
          return 0;
        }
        if (pos.length) {
          const [nombre, desde] = pos;
          if (!NOMBRE_RAMA.test(nombre)) { err(`fatal: '${nombre}' is not a valid branch name\n`); return 128; }
          if ((await g.listBranches({ fs, dir: d })).includes(nombre)) { err(`fatal: a branch named '${nombre}' already exists\n`); return 128; }
          const oid = desde ? await this.resolver(d, desde) : undefined;
          await g.branch({ fs, dir: d, ref: nombre, checkout: false, ...(oid ? { object: oid } : {}) });
          await this.terminarCambios(ctx, { trabajo: false });
          return 0;
        }
        const lineas = [];
        if (!remotas) for (const b of (await g.listBranches({ fs, dir: d })).sort()) lineas.push(b === actual ? `* ${color.verde(b)}` : `  ${b}`);
        if (todas || remotas) for (const r of await g.listRemotes({ fs, dir: d })) for (const b of (await g.listBranches({ fs, dir: d, remote: r.remote })).sort()) if (b !== "HEAD") lineas.push(`  ${color.rojo(`${todas ? "remotes/" : ""}${r.remote}/${b}`)}`);
        out(lineas.join("\n") + (lineas.length ? "\n" : ""));
        return 0;
      }
      case "checkout":
      case "switch": {
        const crear = a.includes("-b") || a.includes("-B") || a.includes("-c") || a.includes("-C") || a.includes("--create");
        const forzar = a.includes("-f") || a.includes("--force") || a.includes("--discard-changes");
        const corte = a.indexOf("--");
        if (orden === "checkout" && corte >= 0) {
          const ref = a.slice(0, corte).find((x) => !x.startsWith("-")) || "HEAD";
          return this.restaurar(ctx, await this.rutasDe(ctx, a.slice(corte + 1)), { ref });
        }
        const pos = a.filter((x) => !x.startsWith("-"));
        const [nombre, desde] = pos;
        if (!nombre) { err(`usage: git ${orden} ${orden === "switch" ? "[-c] " : "[-b] "}<branch>\n`); return 129; }
        if (crear) {
          if (!NOMBRE_RAMA.test(nombre)) { err(`fatal: '${nombre}' is not a valid branch name\n`); return 128; }
          const oid = desde ? await this.resolver(d, desde) : undefined;
          await g.branch({ fs, dir: d, ref: nombre, checkout: !oid, force: a.includes("-B") || a.includes("-C"), ...(oid ? { object: oid } : {}) });
          if (oid) await g.checkout({ fs, dir: d, ref: nombre });
          out(`Switched to a new branch '${nombre}'\n`);
          await this.terminarCambios(ctx);
          return 0;
        }
        const locales = await g.listBranches({ fs, dir: d });
        if (!locales.includes(nombre)) {
          const remota = (await g.listBranches({ fs, dir: d, remote: "origin" }).catch(() => [])).includes(nombre);
          if (!remota) {
            // ¿Es un archivo? (git checkout archivo)
            if (orden === "checkout" && (await this.existe(`${d}/${(await this.rutasDe(ctx, [nombre]))[0]}`))) return this.restaurar(ctx, await this.rutasDe(ctx, [nombre]), { ref: "HEAD" });
            if (orden === "checkout") {
              const oid = await this.resolver(d, nombre).catch(() => null);
              if (oid) { await g.checkout({ fs, dir: d, ref: oid, force: forzar }); out(`Note: switching to '${nombre}'.\n\nYou are in 'detached HEAD' state.\nHEAD is now at ${corto(oid)} ${primera((await g.readCommit({ fs, dir: d, oid })).commit.message)}\n`); await this.terminarCambios(ctx); return 0; }
            }
            err(`error: pathspec '${nombre}' did not match any file(s) known to git\n`);
            return 1;
          }
          const oid = await g.resolveRef({ fs, dir: d, ref: `refs/remotes/origin/${nombre}` });
          await g.branch({ fs, dir: d, ref: nombre, object: oid });
          await g.setConfig({ fs, dir: d, path: `branch.${nombre}.remote`, value: "origin" });
          await g.setConfig({ fs, dir: d, path: `branch.${nombre}.merge`, value: `refs/heads/${nombre}` });
          await g.checkout({ fs, dir: d, ref: nombre, force: forzar });
          out(`branch '${nombre}' set up to track 'origin/${nombre}'.\nSwitched to a new branch '${nombre}'\n`);
          await this.terminarCambios(ctx);
          return 0;
        }
        const actual = await g.currentBranch({ fs, dir: d }).catch(() => null);
        if (actual === nombre) { out(`Already on '${nombre}'\n`); return 0; }
        await g.checkout({ fs, dir: d, ref: nombre, force: forzar });
        out(`Switched to branch '${nombre}'\n`);
        await this.terminarCambios(ctx);
        return 0;
      }
      case "restore": {
        const staged = a.includes("--staged") || a.includes("-S");
        const desde = (a.find((x) => x.startsWith("--source=")) || "").slice(9) || "HEAD";
        const rutas = await this.rutasDe(ctx, a.filter((x) => !x.startsWith("-")));
        if (!rutas.length) { err("fatal: you must specify path(s) to restore\n"); return 128; }
        if (staged) {
          const filas = await g.statusMatrix({ fs, dir: d });
          for (const [f] of filas) if (rutas.some((r) => r === "." || f === r || f.startsWith(r + "/"))) await g.resetIndex({ fs, dir: d, filepath: f });
          await this.terminarCambios(ctx, { trabajo: false });
          return 0;
        }
        return this.restaurar(ctx, rutas, { ref: desde });
      }
      case "reset": {
        const modo = a.includes("--hard") ? "hard" : a.includes("--soft") ? "soft" : "mixed";
        const corte = a.indexOf("--");
        const pos = a.filter((x) => !x.startsWith("-"));
        // git reset <ruta> → sacar del índice
        if (corte >= 0 || (pos.length && !(await this.resolver(d, pos[0]).catch(() => null)))) {
          const rutas = await this.rutasDe(ctx, corte >= 0 ? a.slice(corte + 1) : pos);
          for (const [f] of await g.statusMatrix({ fs, dir: d })) if (rutas.some((r) => r === "." || f === r || f.startsWith(r + "/"))) await g.resetIndex({ fs, dir: d, filepath: f });
          await this.terminarCambios(ctx, { trabajo: false });
          return 0;
        }
        const destino = await this.resolver(d, pos[0] || "HEAD");
        const rama = await g.currentBranch({ fs, dir: d, fullname: true }).catch(() => null);
        const antes = await g.resolveRef({ fs, dir: d, ref: "HEAD" }).catch(() => null);
        if (rama) await g.writeRef({ fs, dir: d, ref: rama, value: destino, force: true }); else await g.writeRef({ fs, dir: d, ref: "HEAD", value: destino, force: true });
        if (antes) await this.p.writeFile(`${d}/.git/ORIG_HEAD`, antes + "\n", "utf8").catch(() => {});
        if (modo !== "soft") {
          const archivos = new Set([...(await g.listFiles({ fs, dir: d, ref: destino })), ...(await g.listFiles({ fs, dir: d }))]);
          for (const f of archivos) await g.resetIndex({ fs, dir: d, filepath: f, ref: destino });
        }
        if (modo === "hard") {
          await g.checkout({ fs, dir: d, ref: rama ? rama.replace(/^refs\/heads\//, "") : destino, force: true });
          // checkout no borra los archivos seguidos que ya no están en el destino:
          const enDestino = new Set(await g.listFiles({ fs, dir: d, ref: destino }));
          for (const [f, h, w, s] of await g.statusMatrix({ fs, dir: d })) if (!enDestino.has(f) && s === 0 && h === 0 && antes && (await this.textoEn(d, antes, f)) !== null) await this.p.unlink(`${d}/${f}`).catch(() => {});
          const c = await g.readCommit({ fs, dir: d, oid: destino });
          out(`HEAD is now at ${corto(destino)} ${primera(c.commit.message)}\n`);
        } else if (modo === "mixed") {
          const e = await this.estado(py, dir);
          if (e.sinPreparar.length) out(`Unstaged changes after reset:\n${e.sinPreparar.map((p) => `${p.tipo === "eliminado" ? "D" : "M"}\t${p.ruta}`).join("\n")}\n`);
        }
        await this.terminarCambios(ctx, { trabajo: modo === "hard" });
        return 0;
      }
      case "merge": {
        if (a.includes("--abort")) {
          await this.p.unlink(`${d}/.git/MERGE_HEAD`).catch(() => {}); await this.p.unlink(`${d}/.git/CC_CONFLICTOS`).catch(() => {});
          await g.checkout({ fs, dir: d, ref: await g.currentBranch({ fs, dir: d }), force: true });
          await this.terminarCambios(ctx);
          return 0;
        }
        const otra = a.find((x) => !x.startsWith("-"));
        if (!otra) { err("usage: git merge <branch>\n"); return 129; }
        const actual = await g.currentBranch({ fs, dir: d });
        const msg = a.includes("-m") ? a[a.indexOf("-m") + 1] : undefined;
        return this.unir(ctx, actual, otra, { soloFF: a.includes("--ff-only"), sinFF: a.includes("--no-ff"), mensaje: msg });
      }
      case "fetch": {
        const remoto = a.find((x) => !x.startsWith("-")) || "origin";
        await this.conRed(ctx, () => g.fetch({ ...this.red(), dir: d, remote: remoto, tags: true, prune: a.includes("--prune") || a.includes("-p"), onProgress: this.progreso(ctx) }), { url: await this.urlDeRemoto(d, remoto) });
        out(color.gris(`From ${(await g.listRemotes({ fs, dir: d })).find((r) => r.remote === remoto)?.url ?? remoto}\n`));
        await this.terminarCambios(ctx, { trabajo: false });
        return 0;
      }
      case "pull": {
        const pos = a.filter((x) => !x.startsWith("-"));
        const remoto = pos[0] || "origin";
        const actual = await g.currentBranch({ fs, dir: d });
        if (!actual) { err("fatal: You are not currently on a branch.\n"); return 128; }
        const ramaRemota = pos[1] || (await g.getConfig({ fs, dir: d, path: `branch.${actual}.merge` }).catch(() => null))?.replace(/^refs\/heads\//, "") || actual;
        await this.conRed(ctx, () => g.fetch({ ...this.red(), dir: d, remote: remoto, ref: ramaRemota, singleBranch: true, tags: true, onProgress: this.progreso(ctx) }), { url: await this.urlDeRemoto(d, remoto) });
        return this.unir(ctx, actual, `${remoto}/${ramaRemota}`, { soloFF: a.includes("--ff-only"), desdePull: true });
      }
      case "push": {
        const pos = a.filter((x) => !x.startsWith("-"));
        const remoto = pos[0] || "origin";
        const actual = await g.currentBranch({ fs, dir: d });
        let ref = pos[1] || actual;
        let destino = ref;
        if (ref?.includes(":")) [ref, destino] = ref.split(":");
        const remotos = await g.listRemotes({ fs, dir: d });
        const url = remotos.find((r) => r.remote === remoto)?.url;
        if (!url) { err(`fatal: '${remoto}' does not appear to be a git repository\nAgrega uno con: git remote add origin https://github.com/usuario/repo.git\n`); return 128; }
        if (!pos.length && !(await g.getConfig({ fs, dir: d, path: `branch.${actual}.remote` }).catch(() => null)) && !a.includes("-u") && !a.includes("--set-upstream")) {
          out(color.gris(`(La rama ${actual} aún no sigue a ninguna rama remota: se publica en ${remoto}/${actual}, como git push -u ${remoto} ${actual}.)\n`));
        }
        let r;
        try {
          r = await this.conRed(ctx, () => g.push({ ...this.red(), dir: d, remote: remoto, ref, remoteRef: destino, force: a.includes("--force") || a.includes("-f"), onProgress: this.progreso(ctx) }), { siempreToken: true, url });
        } catch (e) {
          if (e.code === "x") { err("error: push cancelado: no se inició sesión en GitHub.\n"); return 1; }
          throw e;
        }
        if (a.includes("--tags")) for (const t of await g.listTags({ fs, dir: d })) await g.push({ ...this.red(), dir: d, remote: remoto, ref: t }).catch(() => {});
        if (r?.ok === false || (r?.refs && Object.values(r.refs).some((x) => !x.ok))) { err(`error: failed to push some refs to '${url}'\n${Object.entries(r.refs || {}).map(([k, v]) => v.ok ? "" : ` ! [rejected] ${k} (${v.error})`).filter(Boolean).join("\n")}\n`); return 1; }
        await g.setConfig({ fs, dir: d, path: `branch.${actual}.remote`, value: remoto });
        await g.setConfig({ fs, dir: d, path: `branch.${actual}.merge`, value: `refs/heads/${destino}` });
        out(`To ${url}\n   ${color.verde("✔")} ${ref} -> ${destino}\n`);
        await this.terminarCambios(ctx, { trabajo: false });
        return 0;
      }
      case "remote": {
        const [sub, ...r] = a;
        if (!sub || sub === "-v" || sub === "--verbose") {
          for (const x of await g.listRemotes({ fs, dir: d })) out(sub ? `${x.remote}\t${x.url} (fetch)\n${x.remote}\t${x.url} (push)\n` : `${x.remote}\n`);
          return 0;
        }
        if (sub === "add") {
          const [nombre, url] = r;
          if (!nombre || !url) { err("usage: git remote add <name> <url>\n"); return 129; }
          if (!/^https:\/\/\S+$/.test(url)) { err("fatal: en CódigoCamp los remotos deben ser https:// (ej.: https://github.com/usuario/repo.git)\n"); return 128; }
          if ((await g.listRemotes({ fs, dir: d })).some((x) => x.remote === nombre)) { err(`error: remote ${nombre} already exists.\n`); return 3; }
          await g.addRemote({ fs, dir: d, remote: nombre, url });
        } else if (sub === "remove" || sub === "rm") {
          if (!(await g.listRemotes({ fs, dir: d })).some((x) => x.remote === r[0])) { err(`error: No such remote: '${r[0]}'\n`); return 2; }
          await g.deleteRemote({ fs, dir: d, remote: r[0] });
        } else if (sub === "set-url") {
          const [nombre, url] = r;
          if (!/^https:\/\/\S+$/.test(url || "")) { err("fatal: la URL debe ser https://\n"); return 128; }
          await g.addRemote({ fs, dir: d, remote: nombre, url, force: true });
        } else if (sub === "get-url") {
          const x = (await g.listRemotes({ fs, dir: d })).find((y) => y.remote === r[0]);
          if (!x) { err(`error: No such remote '${r[0]}'\n`); return 2; }
          out(`${x.url}\n`); return 0;
        } else if (sub === "rename") {
          const x = (await g.listRemotes({ fs, dir: d })).find((y) => y.remote === r[0]);
          if (!x) { err(`error: No such remote: '${r[0]}'\n`); return 2; }
          await g.deleteRemote({ fs, dir: d, remote: r[0] }); await g.addRemote({ fs, dir: d, remote: r[1], url: x.url });
        } else { err(`error: Unknown subcommand: ${sub}\n`); return 129; }
        await this.terminarCambios(ctx, { trabajo: false });
        return 0;
      }
      case "config": return this.config(ctx, a, ctx);
      case "tag": {
        const del = a.includes("-d") || a.includes("--delete");
        const anotada = a.includes("-a") || a.includes("-m");
        const msg = a.includes("-m") ? a[a.indexOf("-m") + 1] : null;
        const pos = a.filter((x, i) => !x.startsWith("-") && a[i - 1] !== "-m");
        if (!pos.length) { const t = await g.listTags({ fs, dir: d }); out(t.sort().join("\n") + (t.length ? "\n" : "")); return 0; }
        if (del) { for (const t of pos) { await g.deleteTag({ fs, dir: d, ref: t }); out(`Deleted tag '${t}'\n`); } }
        else {
          const [nombre, ref] = pos;
          const oid = ref ? await this.resolver(d, ref) : undefined;
          if (anotada) await g.annotatedTag({ fs, dir: d, ref: nombre, message: msg || nombre, tagger: await this.autorDe(d), ...(oid ? { object: oid } : {}) });
          else await g.tag({ fs, dir: d, ref: nombre, ...(oid ? { object: oid } : {}) });
        }
        await this.terminarCambios(ctx, { trabajo: false });
        return 0;
      }
      case "stash": {
        const sub = a[0] && !a[0].startsWith("-") ? a[0] : "push";
        const op = { push: "push", save: "push", pop: "pop", apply: "apply", drop: "drop", list: "list", clear: "clear", show: "list" }[sub];
        if (!op) { err(`error: unknown subcommand: ${sub}\n`); return 129; }
        const msg = a.includes("-m") ? a[a.indexOf("-m") + 1] : "";
        if (op === "push") {
          const e = await this.estado(py, dir);
          if (!e.preparados.length && !e.sinPreparar.length) { out("No local changes to save\n"); return 0; }
        }
        const r = await g.stash({ fs, dir: d, op, message: msg });
        if (op === "list") { out((Array.isArray(r) ? r : []).map((x, i) => `stash@{${i}}: ${x}`).join("\n") + (r?.length ? "\n" : "")); return 0; }
        if (op === "push") out(`Saved working directory and index state ${msg ? `On ${await g.currentBranch({ fs, dir: d })}: ${msg}` : `WIP on ${await g.currentBranch({ fs, dir: d })}`}\n`);
        if (op === "pop" || op === "apply") out("Cambios del stash aplicados.\n");
        if (op === "drop") out("Dropped stash@{0}\n");
        await this.terminarCambios(ctx, { trabajo: op !== "drop" && op !== "clear" });
        return 0;
      }
      case "cherry-pick": {
        const ref = a.find((x) => !x.startsWith("-"));
        if (!ref) { err("usage: git cherry-pick <commit>\n"); return 129; }
        if (typeof g.cherryPick !== "function") { err("cherry-pick no está disponible en esta versión.\n"); return 1; }
        const oid = await this.resolver(d, ref);
        const nuevo = await g.cherryPick({ fs, dir: d, oid, committer: await this.autorDe(d) });
        out(`[${await g.currentBranch({ fs, dir: d })} ${corto(typeof nuevo === "string" ? nuevo : await g.resolveRef({ fs, dir: d, ref: "HEAD" }))}] ${primera((await g.readCommit({ fs, dir: d, oid })).commit.message)}\n`);
        await this.terminarCambios(ctx);
        return 0;
      }
      case "revert": {
        const ref = a.find((x) => !x.startsWith("-"));
        if (!ref) { err("usage: git revert <commit>\n"); return 129; }
        return this.revertir(ctx, ref);
      }
      case "clean": {
        if (!a.some((x) => /^-\w*[fn]/.test(x))) { err("fatal: clean.requireForce defaults to true and neither -i, -n, nor -f given; refusing to clean\n"); return 128; }
        const simular = a.some((x) => /^-\w*n/.test(x));
        const { sinSeguimiento } = await this.estado(py, dir);
        for (const f of sinSeguimiento) { out(`${simular ? "Would remove" : "Removing"} ${f}\n`); if (!simular) await this.p.unlink(`${d}/${f}`).catch(() => {}); }
        if (!simular) await this.terminarCambios(ctx, { historial: false });
        return 0;
      }
      case "ls-files": { const l = await g.listFiles({ fs, dir: d }); out(l.join("\n") + (l.length ? "\n" : "")); return 0; }
      case "rev-parse": {
        if (a.includes("--show-toplevel")) { out(`/workspace${dir ? "/" + dir : ""}\n`); return 0; }
        if (a.includes("--abbrev-ref")) { out(`${(await g.currentBranch({ fs, dir: d })) || "HEAD"}\n`); return 0; }
        if (a.includes("--is-inside-work-tree")) { out("true\n"); return 0; }
        const ref = a.find((x) => !x.startsWith("-")) || "HEAD";
        const oid = await this.resolver(d, ref);
        out(`${a.includes("--short") ? corto(oid) : oid}\n`);
        return 0;
      }
      case "blame": {
        const [ruta] = await this.rutasDe(ctx, a.filter((x) => !x.startsWith("-")));
        if (!ruta) { err("usage: git blame <file>\n"); return 129; }
        const commits = await g.log({ fs, dir: d, filepath: ruta });
        const ult = commits[0];
        const t = await this.textoEn(d, ult.oid, ruta);
        out((t || "").split("\n").map((l, i) => `${color.amarillo(corto(ult.oid))} (${ult.commit.author.name.padEnd(12).slice(0, 12)} ${i + 1}) ${l}`).join("\n") + "\n" + color.gris(`(último commit que tocó el archivo: ${hace(ult.commit.author.timestamp)})\n`));
        return 0;
      }
      case "rebase": case "bisect": case "submodule": case "worktree": case "gc": case "reflog": case "am": case "apply": case "format-patch":
        err(`git ${orden}: no está disponible en el navegador. Usa merge (en vez de rebase) o hazlo en tu computador y luego git pull.\n`);
        return 1;
      default:
        err(`git: '${orden}' is not a git command. See 'git help'.\n`);
        return 1;
    }
  }

  async resolver(d, ref) {
    const g = this.git, fs = this.fs;
    const m = /^(.+?)((?:[~^]\d*)+)$/.exec(ref);
    const base = m ? m[1] : ref;
    let oid;
    try { oid = await g.resolveRef({ fs, dir: d, ref: base }); }
    catch {
      try { oid = await g.resolveRef({ fs, dir: d, ref: `refs/remotes/${base}` }); }
      catch { oid = await g.expandOid({ fs, dir: d, oid: base }).catch(() => { throw Object.assign(new Error(`ambiguous argument '${ref}': unknown revision or path not in the working tree.`), { code: "NotFoundError" }); }); }
    }
    try { const tag = await g.readTag({ fs, dir: d, oid }); oid = tag.tag.object; } catch { /* no es etiqueta anotada */ }
    if (m) for (const p of m[2].matchAll(/([~^])(\d*)/g)) {
      const n = p[2] === "" ? 1 : Number(p[2]);
      if (p[1] === "^") { const c = await g.readCommit({ fs, dir: d, oid }); oid = c.commit.parent[n - 1]; }
      else for (let i = 0; i < n; i++) { const c = await g.readCommit({ fs, dir: d, oid }); oid = c.commit.parent[0]; }
      if (!oid) throw Object.assign(new Error(`ambiguous argument '${ref}': unknown revision`), { code: "NotFoundError" });
    }
    return oid;
  }

  async seguimiento(d, rama) {
    const g = this.git, fs = this.fs;
    const remoto = await g.getConfig({ fs, dir: d, path: `branch.${rama}.remote` }).catch(() => null);
    const merge = await g.getConfig({ fs, dir: d, path: `branch.${rama}.merge` }).catch(() => null);
    if (!remoto || !merge) return "";
    const nombre = `${remoto}/${merge.replace(/^refs\/heads\//, "")}`;
    let local, otra;
    try { local = await g.resolveRef({ fs, dir: d, ref: "HEAD" }); otra = await g.resolveRef({ fs, dir: d, ref: `refs/remotes/${nombre}` }); } catch { return `Your branch is based on '${nombre}', but the upstream is gone.`; }
    if (local === otra) return `Your branch is up to date with '${nombre}'.`;
    const delante = (await g.log({ fs, dir: d, ref: local })).findIndex((c) => c.oid === otra);
    if (delante > 0) return `Your branch is ahead of '${nombre}' by ${delante} commit${delante === 1 ? "" : "s"}.\n  (use "git push" to publish your local commits)`;
    const detras = (await g.log({ fs, dir: d, ref: otra })).findIndex((c) => c.oid === local);
    if (detras > 0) return `Your branch is behind '${nombre}' by ${detras} commit${detras === 1 ? "" : "s"}, and can be fast-forwarded.\n  (use "git pull" to update your local branch)`;
    return `Your branch and '${nombre}' have diverged.\n  (use "git pull" to merge the remote branch into yours)`;
  }

  async restaurar(ctx, rutas, { ref = "HEAD" } = {}) {
    const { d } = ctx;
    const oid = await this.resolver(d, ref);
    const enRef = await this.git.listFiles({ fs: this.fs, dir: d, ref: oid });
    const elegidos = enRef.filter((f) => rutas.some((r) => r === "." || f === r || f.startsWith(r + "/")));
    if (!elegidos.length) { ctx.err(`error: pathspec '${rutas.join(" ")}' did not match any file(s) known to git\n`); return 1; }
    for (const f of elegidos) {
      const { blob } = await this.git.readBlob({ fs: this.fs, dir: d, oid, filepath: f });
      await this.mkdirp(`${d}/${FS.carpetaDe(f)}`);
      await this.p.writeFile(`${d}/${f}`, blob);
    }
    await this.terminarCambios(ctx, { historial: false });
    return 0;
  }

  async unir(ctx, actual, otra, { soloFF = false, sinFF = false, mensaje, desdePull = false } = {}) {
    const { d, out, err, py, dir } = ctx;
    const g = this.git, fs = this.fs;
    const oidOtra = await this.resolver(d, otra);
    const oidActual = await g.resolveRef({ fs, dir: d, ref: "HEAD" }).catch(() => null);
    const e = await this.estado(py, dir);
    if (e.preparados.length || e.sinPreparar.length) {
      err(`error: Your local changes to the following files would be overwritten by merge:\n\t${[...e.preparados, ...e.sinPreparar].map((x) => x.ruta).join("\n\t")}\nPlease commit your changes or stash them before you merge.\nAborting\n`);
      return 1;
    }
    if (oidActual === oidOtra || (oidActual && await g.isDescendent({ fs, dir: d, oid: oidActual, ancestor: oidOtra }).catch(() => false))) { out("Already up to date.\n"); return 0; }
    let r;
    try {
      r = await g.merge({ fs, dir: d, ours: actual, theirs: oidOtra, fastForward: !sinFF, fastForwardOnly: soloFF, author: await this.autorDe(d), message: mensaje || `Merge ${desdePull ? "branch" : "branch"} '${otra}'${desdePull ? "" : ` into ${actual}`}`, abortOnConflict: false });
    } catch (e2) {
      if (e2.code === "MergeConflictError") {
        const archivos = e2.data?.filepaths || [];
        await this.p.writeFile(`${d}/.git/MERGE_HEAD`, oidOtra + "\n", "utf8");
        await this.p.writeFile(`${d}/.git/CC_CONFLICTOS`, JSON.stringify(archivos), "utf8");
        // isomorphic-git deja los archivos con marcas de conflicto en el índice: se pasan al árbol de trabajo.
        for (const f of archivos) {
          let contenido = null;
          await g.walk({ fs, dir: d, trees: [g.STAGE()], map: async (p, [entrada]) => { if (p === f && entrada) contenido = await entrada.content?.() ?? null; return p === "." || f.startsWith(p + "/") ? true : null; } }).catch(() => {});
          if (contenido) await this.p.writeFile(`${d}/${f}`, contenido);
        }
        out(`Auto-merging\n${archivos.map((f) => `CONFLICT (content): Merge conflict in ${f}`).join("\n")}\nAutomatic merge failed; fix conflicts and then commit the result.\n`);
        await this.terminarCambios(ctx);
        return 1;
      }
      throw e2;
    }
    await g.checkout({ fs, dir: d, ref: actual, force: true });
    const nuevo = await g.resolveRef({ fs, dir: d, ref: "HEAD" });
    const diff = await this.diffCommits(d, oidActual, nuevo);
    const archivos = [...quitarColor(diff).matchAll(/diff --git a\/(\S+)/g)].map((m) => m[1]);
    out(r.fastForward ? `Updating ${corto(oidActual || "0000000")}..${corto(nuevo)}\nFast-forward\n` : `Merge made by the 'ort' strategy.\n`);
    out(`${archivos.map((f) => ` ${f}`).join("\n")}${archivos.length ? "\n" : ""} ${archivos.length} file${archivos.length === 1 ? "" : "s"} changed\n`);
    await this.terminarCambios(ctx);
    return 0;
  }

  async revertir(ctx, ref) {
    const { d, out, py, dir } = ctx;
    const g = this.git, fs = this.fs;
    const oid = await this.resolver(d, ref);
    const c = await g.readCommit({ fs, dir: d, oid });
    const padre = c.commit.parent[0];
    if (!padre) { ctx.err("error: no se puede revertir el primer commit.\n"); return 1; }
    const e = await this.estado(py, dir);
    if (e.preparados.length || e.sinPreparar.length) { ctx.err("error: your local changes would be overwritten by revert.\nhint: commit your changes or stash them to proceed.\n"); return 1; }
    // Revertir = aplicar al árbol actual el cambio inverso de ese commit (archivo por archivo).
    await g.walk({ fs, dir: d, trees: [g.TREE({ ref: padre }), g.TREE({ ref: oid })], map: async (f, [a, b]) => {
      if (f === ".") return true;
      const ta = a ? await a.type() : null, tb = b ? await b.type() : null;
      if (ta === "tree" || tb === "tree") return true;
      const oa = a ? await a.oid() : null, ob = b ? await b.oid() : null;
      if (oa === ob) return null;
      if (!a) { await this.p.unlink(`${d}/${f}`).catch(() => {}); await g.remove({ fs, dir: d, filepath: f }); }
      else { await this.mkdirp(`${d}/${FS.carpetaDe(f)}`); await this.p.writeFile(`${d}/${f}`, await a.content()); await g.add({ fs, dir: d, filepath: f }); }
      return null;
    } });
    const nuevo = await g.commit({ fs, dir: d, message: `Revert "${primera(c.commit.message)}"\n\nThis reverts commit ${oid}.`, author: await this.autorDe(d) });
    out(`[${await g.currentBranch({ fs, dir: d })} ${corto(nuevo)}] Revert "${primera(c.commit.message)}"\n`);
    await this.terminarCambios(ctx);
    return 0;
  }
}

const AYUDA = `usage: git <command> [<args>]   (Git real, como en VS Code; el historial se respalda en tu cuenta)

empezar        init · clone <url> [carpeta] [--depth N] [-b rama]
cambios        status [-s] · add <archivo|.> · rm [--cached] · mv · restore [--staged] · diff [--staged] · clean -f
historial      commit -m "mensaje" [-a] [--amend] · log [--oneline] [--graph] [--all] [-n N] · show [commit] · blame · revert · cherry-pick
ramas          branch [-a] [-d] [-m] · switch [-c] <rama> · checkout [-b] <rama> · merge <rama> [--abort] · stash [pop|list|drop]
GitHub         remote add origin <url> · fetch · pull · push [-u] [origin rama] [--force] · tag [-a] · config user.name "Tu Nombre"
deshacer       reset [--soft|--hard] [HEAD~1] · restore <archivo> · revert <commit>
Para push (o un repositorio privado) se abre «Iniciar sesión con GitHub». También: gh auth login · gh auth status · gh auth logout.
`;
