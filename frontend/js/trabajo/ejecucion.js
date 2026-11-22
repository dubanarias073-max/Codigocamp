// Ejecutores de código para la terminal. Todo corre en el navegador de la persona salvo los lenguajes compilados,
// que usan el ejecutor del servidor (POST /api/run, el mismo de la página Aprende).
//
//  · JavaScript  -> un Worker propio (se puede cancelar con Ctrl+C aunque haya un bucle infinito).
//  · TypeScript  -> se transpila en el navegador y corre igual que JavaScript.
//  · Python      -> Pyodide (se descarga la primera vez), igual que en Aprende.
//  · SQL         -> sql.js (SQLite en el navegador), igual que en Aprende.
import { color } from "./ansi.js";
import * as FS from "./fs.js";
import { leerMarcador } from "./archivos.js";
import { cerrarMysqlEnPython, instalarMysqlEnPython } from "./pymysql.js";
import { dependenciasDe, restaurarPaquetes, sugerenciaNode, sugerenciaPython, urlDeCdn } from "./paquetes.js";

const MAX_SALIDA = 200_000;
const TIEMPO_MAXIMO = 120_000;
const BUILTINS = ["fs", "path", "util", "os", "events", "readline", "readline/promises", "assert", "fs/promises", "timers/promises"];

// ===================================================================================================
//  Entorno de ejecución de Node. Esta función se serializa con toString() y corre DENTRO del Worker,
//  así que no puede usar nada de fuera: todo lo que necesita va en CC (datos) o está definido aquí.
// ===================================================================================================
export function runtimeNode(CC) {
  const enviar = (m) => self.postMessage(m);
  const nativo = { setTimeout: self.setTimeout.bind(self), clearTimeout: self.clearTimeout.bind(self), setInterval: self.setInterval.bind(self), clearInterval: self.clearInterval.bind(self), fetch: self.fetch ? self.fetch.bind(self) : null };
  const RAIZ = "/workspace";
  const archivos = Object.assign(Object.create(null), CC.files);
  const original = new Set(Object.keys(archivos));
  const carpetas = new Set(CC.folders);
  const cambios = { files: Object.create(null), folders: [] };
  let terminado = false;
  let pendientesE_S = 0;
  const EXIT = { salida: true };
  const temporizadores = new Set();
  let enviado = 0;
  const escribir = (canal, texto) => {
    if (enviado > 200000) return;
    enviado += texto.length;
    if (enviado > 200000) texto = texto.slice(0, texto.length - (enviado - 200000)) + "\n… (salida recortada)\n";
    enviar({ t: canal, s: texto });
  };

  // ---- inspección de valores (parecida a util.inspect de Node) ----
  const identificador = /^[A-Za-z_$][\w$]*$/;
  const comillas = (s) => "'" + s.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, "\\n") + "'";
  function inspeccionar(v, profundidad = 2, vistos = [], sangria = 0, nivel = 0) {
    const t = typeof v;
    if (v === null) return "null";
    if (v === undefined) return "undefined";
    if (t === "string") return nivel === 0 ? v : comillas(v);
    if (t === "number") return Object.is(v, -0) ? "-0" : String(v);
    if (t === "bigint") return v + "n";
    if (t === "boolean") return String(v);
    if (t === "symbol") return v.toString();
    if (t === "function") {
      const nombre = v.name;
      const esClase = /^class\b/.test(Function.prototype.toString.call(v));
      return esClase ? `[class ${nombre || "(anonymous)"}]` : nombre ? `[Function: ${nombre}]` : "[Function (anonymous)]";
    }
    if (vistos.includes(v)) return "[Circular *1]";
    if (v instanceof Error) {
      const lineas = String(v.stack || `${v.name}: ${v.message}`).split("\n").filter((l, i) => i === 0 || !/blob:|runtimeNode|<anonymous>:\d+:\d+\)?$/.test(l) || l.includes(RAIZ));
      const extra = Object.keys(v).length && nivel < profundidad + 1 ? " " + inspeccionarObjeto(v, profundidad, vistos, sangria, nivel, true) : "";
      return lineas.join("\n") + extra;
    }
    if (v instanceof Date) return isNaN(v) ? "Invalid Date" : v.toISOString();
    if (v instanceof RegExp) return String(v);
    if (typeof Promise !== "undefined" && v instanceof Promise) return "Promise { <estado desconocido> }";
    if (nivel > profundidad) return Array.isArray(v) ? "[Array]" : `[${v.constructor?.name || "Object"}]`;
    vistos = [...vistos, v];
    let partes;
    let abre = "{";
    let cierra = "}";
    let prefijo = "";
    if (Array.isArray(v)) {
      abre = "["; cierra = "]";
      partes = v.slice(0, 100).map((x) => inspeccionar(x, profundidad, vistos, sangria + 2, nivel + 1));
      if (v.length > 100) partes.push(`... ${v.length - 100} more item${v.length - 100 > 1 ? "s" : ""}`);
      const extras = Object.keys(v).filter((k) => !/^\d+$/.test(k));
      extras.forEach((k) => partes.push(`${k}: ${inspeccionar(v[k], profundidad, vistos, sangria + 2, nivel + 1)}`));
    } else if (v instanceof Map) {
      prefijo = `Map(${v.size}) `;
      partes = [...v].map(([k, x]) => `${inspeccionar(k, profundidad, vistos, sangria + 2, nivel + 1)} => ${inspeccionar(x, profundidad, vistos, sangria + 2, nivel + 1)}`);
    } else if (v instanceof Set) {
      prefijo = `Set(${v.size}) `;
      partes = [...v].map((x) => inspeccionar(x, profundidad, vistos, sangria + 2, nivel + 1));
    } else {
      return inspeccionarObjeto(v, profundidad, vistos, sangria, nivel, false);
    }
    return componer(prefijo, abre, cierra, partes, sangria);
  }
  function inspeccionarObjeto(v, profundidad, vistos, sangria, nivel, soloExtras) {
    const proto = Object.getPrototypeOf(v);
    const nombre = soloExtras ? "" : proto === null ? "[Object: null prototype]" : v.constructor && v.constructor.name !== "Object" ? v.constructor.name : "";
    const claves = [...Object.keys(v), ...Object.getOwnPropertySymbols(v).filter((s) => Object.prototype.propertyIsEnumerable.call(v, s))];
    const partes = claves.map((k) => {
      const nombreClave = typeof k === "symbol" ? `[${k.toString()}]` : identificador.test(k) ? k : comillas(k);
      const d = Object.getOwnPropertyDescriptor(v, k);
      const valor = d && (d.get || d.set) ? (d.get && d.set ? "[Getter/Setter]" : d.get ? "[Getter]" : "[Setter]") : inspeccionar(v[k], profundidad, [...vistos], sangria + 2, nivel + 1);
      return `${nombreClave}: ${valor}`;
    });
    return componer(nombre ? nombre + " " : "", "{", "}", partes, sangria, soloExtras);
  }
  function componer(prefijo, abre, cierra, partes, sangria) {
    if (!partes.length) return `${prefijo}${abre}${cierra}`;
    const largo = partes.reduce((s, p) => s + p.length + 2, 0) + prefijo.length + sangria;
    if (largo <= 72 && !partes.some((p) => p.includes("\n"))) return `${prefijo}${abre} ${partes.join(", ")} ${cierra}`;
    const pad = " ".repeat(sangria + 2);
    return `${prefijo}${abre}\n${partes.map((p) => pad + p).join(",\n")}\n${" ".repeat(sangria)}${cierra}`;
  }
  const formatear = (args) => {
    if (!args.length) return "";
    let [primero, ...resto] = args;
    let salida = "";
    if (typeof primero === "string" && /%[sdifjoOc%]/.test(primero)) {
      salida = primero.replace(/%([sdifjoOc%])/g, (m, f) => {
        if (f === "%") return "%";
        if (!resto.length) return m;
        const a = resto.shift();
        if (f === "s") return typeof a === "string" ? a : typeof a === "object" && a !== null ? inspeccionar(a, 1, [], 0, 1) : String(a);
        if (f === "d" || f === "i") return typeof a === "bigint" ? a + "n" : String(f === "i" ? parseInt(a, 10) : Number(a));
        if (f === "f") return String(parseFloat(a));
        if (f === "j") { try { return JSON.stringify(a); } catch { return "[Circular]"; } }
        if (f === "c") return "";
        return inspeccionar(a, 4, [], 0, 1);
      });
    } else salida = inspeccionar(primero);
    return [salida, ...resto.map((a) => inspeccionar(a))].join(" ");
  };

  // ---- consola ----
  let sangriaGrupo = "";
  const conGrupo = (t) => (sangriaGrupo ? t.split("\n").map((l) => sangriaGrupo + l).join("\n") : t);
  const contadores = {};
  const tiempos = {};
  const consola = {
    log: (...a) => escribir("out", conGrupo(formatear(a)) + "\n"),
    error: (...a) => escribir("err", conGrupo(formatear(a)) + "\n"),
    dir: (v, o) => escribir("out", conGrupo(inspeccionar(v, o?.depth ?? 2, [], 0, 1)) + "\n"),
    assert: (c, ...a) => { if (!c) escribir("err", "Assertion failed" + (a.length ? ": " + formatear(a) : "") + "\n"); },
    group: (...a) => { if (a.length) consola.log(...a); sangriaGrupo += "  "; },
    groupEnd: () => { sangriaGrupo = sangriaGrupo.slice(2); },
    count: (e = "default") => { contadores[e] = (contadores[e] || 0) + 1; consola.log(`${e}: ${contadores[e]}`); },
    countReset: (e = "default") => { contadores[e] = 0; },
    time: (e = "default") => { tiempos[e] = performance.now(); },
    timeEnd: (e = "default") => { if (e in tiempos) { consola.log(`${e}: ${(performance.now() - tiempos[e]).toFixed(3)}ms`); delete tiempos[e]; } },
    timeLog: (e = "default", ...a) => { if (e in tiempos) consola.log(`${e}: ${(performance.now() - tiempos[e]).toFixed(3)}ms`, ...a); },
    trace: (...a) => escribir("err", "Trace: " + formatear(a) + "\n"),
    table: (datos) => {
      if (datos === null || typeof datos !== "object") return consola.log(datos);
      const filas = Array.isArray(datos) ? datos.map((v, i) => [String(i), v]) : Object.entries(datos);
      const cols = [];
      const celdas = filas.map(([k, v]) => {
        const fila = { "(index)": k };
        if (v !== null && typeof v === "object") Object.keys(v).forEach((c) => { if (!cols.includes(c)) cols.push(c); fila[c] = inspeccionar(v[c], 0, [], 0, 1); });
        else { if (!cols.includes("Values")) cols.push("Values"); fila.Values = inspeccionar(v, 0, [], 0, 1); }
        return fila;
      });
      const todas = ["(index)", ...cols];
      const anchos = todas.map((c) => Math.max(c.length, ...celdas.map((f) => String(f[c] ?? "").length)) + 2);
      const centrar = (t, w) => { const sob = w - t.length; const i = Math.floor(sob / 2); return " ".repeat(i) + t + " ".repeat(sob - i); };
      const linea = (a, b, c) => a + anchos.map((w) => "─".repeat(w)).join(b) + c;
      consola.log([linea("┌", "┬", "┐"), "│" + todas.map((c, i) => centrar(c, anchos[i])).join("│") + "│", linea("├", "┼", "┤"),
        ...celdas.map((f) => "│" + todas.map((c, i) => centrar(String(f[c] ?? ""), anchos[i])).join("│") + "│"), linea("└", "┴", "┘")].join("\n"));
    },
  };
  consola.info = consola.debug = consola.log;
  consola.warn = consola.error;
  self.console = consola;

  // ---- rutas y archivos virtuales ----
  const rutaNode = (() => {
    const normalizar = (p) => {
      const abs = p.startsWith("/");
      const partes = [];
      for (const s of p.split("/")) { if (!s || s === ".") continue; if (s === "..") { if (partes.length && partes[partes.length - 1] !== "..") partes.pop(); else if (!abs) partes.push(".."); } else partes.push(s); }
      return (abs ? "/" : "") + partes.join("/") || (abs ? "/" : ".");
    };
    const resolver = (...a) => { let r = ""; for (let i = a.length - 1; i >= 0 && !r.startsWith("/"); i -= 1) if (a[i]) r = a[i] + (r ? "/" + r : ""); if (!r.startsWith("/")) r = RAIZ + (CC.cwd ? "/" + CC.cwd : "") + (r ? "/" + r : ""); return normalizar(r); };
    const ext = (p) => { const b = p.split("/").pop(); const i = b.lastIndexOf("."); return i > 0 ? b.slice(i) : ""; };
    return {
      sep: "/", delimiter: ":", normalize: normalizar, resolve: resolver, join: (...a) => normalizar(a.filter(Boolean).join("/") || "."),
      basename: (p, e) => { const b = p.replace(/\/+$/, "").split("/").pop(); return e && b.endsWith(e) ? b.slice(0, -e.length) : b; },
      dirname: (p) => { const i = p.replace(/\/+$/, "").lastIndexOf("/"); return i < 0 ? "." : i === 0 ? "/" : p.slice(0, i); },
      extname: ext, isAbsolute: (p) => p.startsWith("/"),
      relative: (a, b) => { const x = resolver(a).split("/").filter(Boolean); const y = resolver(b).split("/").filter(Boolean); let i = 0; while (i < x.length && i < y.length && x[i] === y[i]) i += 1; return [...Array(x.length - i).fill(".."), ...y.slice(i)].join("/"); },
      parse: (p) => { const base = p.split("/").pop(); const e = ext(p); return { root: p.startsWith("/") ? "/" : "", dir: p.includes("/") ? p.slice(0, p.lastIndexOf("/")) : "", base, ext: e, name: e ? base.slice(0, -e.length) : base }; },
    };
  })();
  const aInterna = (p) => { const a = rutaNode.resolve(String(p)); return a === RAIZ ? "" : a.startsWith(RAIZ + "/") ? a.slice(RAIZ.length + 1) : null; };
  const errorFs = (codigo, sys, p) => { const e = new Error(`${codigo}: ${sys}, ${p}`); e.code = codigo; e.path = p; e.errno = codigo === "ENOENT" ? -2 : -17; return e; };
  const esCarpeta = (r) => r === "" || carpetas.has(r);
  const asegurarPadres = (r) => { const partes = r.split("/").slice(0, -1); for (let i = 1; i <= partes.length; i += 1) { const c = partes.slice(0, i).join("/"); if (!carpetas.has(c)) { carpetas.add(c); cambios.folders.push(c); } } };
  const fsSync = {
    existsSync: (p) => { const r = aInterna(p); return r !== null && (r in archivos || esCarpeta(r)); },
    readFileSync: (p, o) => { const r = aInterna(p); if (r === null || !(r in archivos)) throw errorFs("ENOENT", "no such file or directory, open", p); return archivos[r]; },
    writeFileSync: (p, d) => { const r = aInterna(p); if (r === null || r === "") throw errorFs("EACCES", "permission denied, open", p); if (esCarpeta(r)) throw errorFs("EISDIR", "illegal operation on a directory, open", p); asegurarPadres(r); archivos[r] = String(d); cambios.files[r] = archivos[r]; },
    appendFileSync: (p, d) => { const r = aInterna(p); fsSync.writeFileSync(p, (r in archivos ? archivos[r] : "") + String(d)); },
    readdirSync: (p) => { const r = aInterna(p); if (r === null || !esCarpeta(r)) throw errorFs("ENOENT", "no such file or directory, scandir", p); const pre = r ? r + "/" : ""; const n = new Set(); [...Object.keys(archivos), ...carpetas].forEach((x) => { if (x.startsWith(pre) && x !== r) n.add(x.slice(pre.length).split("/")[0]); }); return [...n].sort(); },
    mkdirSync: (p, o) => { const r = aInterna(p); if (r === null || r === "") return; if (r in archivos || (carpetas.has(r) && !(o && o.recursive))) throw errorFs("EEXIST", "file already exists, mkdir", p); const padre = r.split("/").slice(0, -1).join("/"); if (!(o && o.recursive) && !esCarpeta(padre)) throw errorFs("ENOENT", "no such file or directory, mkdir", p); asegurarPadres(r + "/x"); if (!carpetas.has(r)) { carpetas.add(r); cambios.folders.push(r); } },
    unlinkSync: (p) => { const r = aInterna(p); if (r === null || !(r in archivos)) throw errorFs("ENOENT", "no such file or directory, unlink", p); delete archivos[r]; cambios.files[r] = null; },
    rmSync: (p, o) => { const r = aInterna(p); if (r === null || r === "") return; if (r in archivos) return fsSync.unlinkSync(p); if (carpetas.has(r)) { if (!(o && o.recursive)) throw errorFs("EISDIR", "illegal operation on a directory, rm", p); Object.keys(archivos).filter((x) => x.startsWith(r + "/")).forEach((x) => { delete archivos[x]; cambios.files[x] = null; }); [...carpetas].filter((c) => c === r || c.startsWith(r + "/")).forEach((c) => carpetas.delete(c)); cambios.folders = cambios.folders.filter((c) => carpetas.has(c)); cambios.carpetasBorradas = [...(cambios.carpetasBorradas || []), r]; } else if (!(o && o.force)) throw errorFs("ENOENT", "no such file or directory, rm", p); },
    renameSync: (a, b) => { const x = aInterna(a); if (x === null || !(x in archivos)) throw errorFs("ENOENT", "no such file or directory, rename", a); const t = archivos[x]; fsSync.unlinkSync(a); fsSync.writeFileSync(b, t); },
    copyFileSync: (a, b) => fsSync.writeFileSync(b, fsSync.readFileSync(a)),
    statSync: (p) => { const r = aInterna(p); if (r === null || !(r in archivos || esCarpeta(r))) throw errorFs("ENOENT", "no such file or directory, stat", p); const dir = esCarpeta(r); return { isFile: () => !dir, isDirectory: () => dir, size: dir ? 4096 : archivos[r].length }; },
  };
  const prometer = (f) => (...a) => new Promise((ok, ko) => { try { ok(f(...a)); } catch (e) { ko(e); } });
  const fsPromesas = Object.fromEntries(["readFile", "writeFile", "appendFile", "readdir", "mkdir", "unlink", "rm", "rename", "copyFile", "stat"].map((n) => [n, prometer(fsSync[n + "Sync"])]));
  fsPromesas.access = prometer((p) => { if (!fsSync.existsSync(p)) throw errorFs("ENOENT", "no such file or directory, access", p); });
  const fsModulo = { ...fsSync, promises: fsPromesas };
  ["readFile", "writeFile", "appendFile", "readdir", "mkdir", "unlink", "rename", "copyFile", "stat"].forEach((n) => {
    fsModulo[n] = (...a) => { const cb = a.pop(); try { const r = fsSync[n + "Sync"](...a); nativo.setTimeout(() => cb(null, r), 0); } catch (e) { nativo.setTimeout(() => cb(e), 0); } };
  });

  // ---- temporizadores (se cuentan para saber cuándo termina el programa, como hace Node) ----
  const fatal = (e) => {
    if (e === EXIT || terminado) return;
    escribir("err", "Uncaught " + (e instanceof Error ? inspeccionar(e) : "Error: " + formatear([e])) + "\n");
    terminar(1);
  };
  const revisar = () => {
    if (terminado || temporizadores.size || pendientesE_S) return;
    // Pequeña espera: deja que lleguen los «unhandledrejection» antes de dar el programa por terminado.
    nativo.setTimeout(() => { if (!terminado && !temporizadores.size && !pendientesE_S) terminar(process.exitCode || 0); }, 20);
  };
  const crearTemporizador = (repetir) => (fn, ms, ...a) => {
    if (typeof fn !== "function") throw new TypeError("El primer argumento debe ser una función");
    const obj = { id: 0, ref() { return this; }, unref() { return this; }, hasRef: () => true, refresh() { return this; }, [Symbol.toPrimitive]() { return this.id; } };
    const correr = () => { if (!repetir) temporizadores.delete(obj); try { fn(...a); } catch (e) { fatal(e); } revisar(); };
    obj.id = repetir ? nativo.setInterval(correr, ms) : nativo.setTimeout(correr, ms);
    temporizadores.add(obj);
    return obj;
  };
  const limpiar = (obj) => {
    const t = typeof obj === "object" && obj ? obj : [...temporizadores].find((x) => x.id === obj);
    if (!t) return;
    nativo.clearTimeout(t.id); nativo.clearInterval(t.id); temporizadores.delete(t); revisar();
  };
  self.setTimeout = crearTemporizador(false);
  self.setInterval = crearTemporizador(true);
  self.setImmediate = (fn, ...a) => self.setTimeout(fn, 0, ...a);
  self.clearTimeout = self.clearInterval = self.clearImmediate = limpiar;
  if (nativo.fetch) {
    self.fetch = (...a) => { pendientesE_S += 1; return nativo.fetch(...a).finally(() => { pendientesE_S -= 1; revisar(); }); };
  }

  // ---- entrada (readline): la terminal pide la línea y la devuelve ----
  const esperaLinea = [];
  const leer = (texto) => { pendientesE_S += 1; return new Promise((ok) => { esperaLinea.push(ok); enviar({ t: "leer", prompt: texto }); }); };
  self.addEventListener("message", (ev) => {
    if (ev.data && ev.data.t === "linea") { const ok = esperaLinea.shift(); if (ok) { pendientesE_S -= 1; ok(ev.data.valor); revisar(); } }
  });
  const crearInterfaz = (prometida) => (opciones) => {
    const eventos = {};
    let abierta = true;
    let promptTxt = "> ";
    let bucle = false;
    const emitir = (n, ...a) => (eventos[n] || []).slice().forEach((f) => f(...a));
    const cerrar = () => { if (abierta) { abierta = false; emitir("close"); } };
    const iniciarBucle = async () => {
      if (bucle) return;
      bucle = true;
      while (abierta) { const l = await leer(promptTxt); if (l === null) { cerrar(); break; } emitir("line", l); }
    };
    const rl = {
      question: prometida ? (q) => (abierta ? leer(q).then((v) => { if (v === null) cerrar(); return v ?? ""; }) : Promise.resolve("")) : (q, cb) => { if (abierta) leer(q).then((v) => { if (v === null) cerrar(); else cb(v); }); },
      on(n, f) { (eventos[n] = eventos[n] || []).push(f); if (n === "line") nativo.setTimeout(iniciarBucle, 0); return rl; },
      once(n, f) { const g = (...a) => { eventos[n] = eventos[n].filter((x) => x !== g); f(...a); }; return rl.on(n, g); },
      setPrompt: (p) => { promptTxt = p; }, prompt: () => { if (!bucle) iniciarBucle(); }, close: cerrar, write: () => {}, pause: () => rl, resume: () => rl,
      [Symbol.asyncIterator]: async function* () { while (abierta) { const l = await leer(""); if (l === null) { cerrar(); return; } yield l; } },
    };
    return rl;
  };

  // ---- módulos integrados mínimos ----
  class EventEmitter {
    constructor() { this._e = {}; }
    on(n, f) { (this._e[n] = this._e[n] || []).push(f); return this; }
    addListener(n, f) { return this.on(n, f); }
    prependListener(n, f) { (this._e[n] = this._e[n] || []).unshift(f); return this; }
    once(n, f) { const g = (...a) => { this.off(n, g); f.apply(this, a); }; g.original = f; return this.on(n, g); }
    off(n, f) { this._e[n] = (this._e[n] || []).filter((x) => x !== f && x.original !== f); return this; }
    removeListener(n, f) { return this.off(n, f); }
    removeAllListeners(n) { if (n) delete this._e[n]; else this._e = {}; return this; }
    emit(n, ...a) { const l = (this._e[n] || []).slice(); if (n === "error" && !l.length) throw a[0] instanceof Error ? a[0] : new Error("Unhandled error. " + formatear(a)); l.forEach((f) => f.apply(this, a)); return l.length > 0; }
    listenerCount(n) { return (this._e[n] || []).length; }
    listeners(n) { return (this._e[n] || []).map((f) => f.original || f); }
    eventNames() { return Object.keys(this._e).filter((k) => this._e[k].length); }
    setMaxListeners() { return this; }
  }
  EventEmitter.EventEmitter = EventEmitter;
  class AssertionError extends Error { constructor(m) { super(m); this.name = "AssertionError"; this.code = "ERR_ASSERTION"; } }
  const iguales = (a, b) => { try { return JSON.stringify(a) === JSON.stringify(b) && (typeof a === typeof b); } catch { return false; } };
  const assert = (v, m) => { if (!v) throw new AssertionError(m || "The expression evaluated to a falsy value"); };
  Object.assign(assert, {
    ok: assert, AssertionError,
    equal: (a, b, m) => { if (a != b) throw new AssertionError(m || `${inspeccionar(a, 2, [], 0, 1)} == ${inspeccionar(b, 2, [], 0, 1)}`); },
    notEqual: (a, b, m) => { if (a == b) throw new AssertionError(m || `${inspeccionar(a, 2, [], 0, 1)} != ${inspeccionar(b, 2, [], 0, 1)}`); },
    strictEqual: (a, b, m) => { if (!Object.is(a, b)) throw new AssertionError(m || `Expected values to be strictly equal:\n\n${inspeccionar(a, 2, [], 0, 1)} !== ${inspeccionar(b, 2, [], 0, 1)}`); },
    notStrictEqual: (a, b, m) => { if (Object.is(a, b)) throw new AssertionError(m || "Expected \"actual\" to be strictly unequal to: " + inspeccionar(b, 2, [], 0, 1)); },
    deepStrictEqual: (a, b, m) => { if (!iguales(a, b)) throw new AssertionError(m || "Expected values to be strictly deep-equal:\n" + inspeccionar(a, 4, [], 0, 1) + "\n\nshould equal\n\n" + inspeccionar(b, 4, [], 0, 1)); },
    deepEqual: (a, b, m) => assert.deepStrictEqual(a, b, m),
    throws: (f, _e, m) => { try { f(); } catch { return; } throw new AssertionError(m || "Missing expected exception."); },
    fail: (m) => { throw new AssertionError(m || "Failed"); },
  });
  assert.strict = assert;
  const util = {
    inspect: (v, o) => inspeccionar(v, typeof o === "object" && o ? (o.depth === null ? 99 : o.depth ?? 2) : 2, [], 0, 1),
    format: (...a) => formatear(a), promisify: (f) => (...a) => new Promise((ok, ko) => f(...a, (e, r) => (e ? ko(e) : ok(r)))),
    isDeepStrictEqual: iguales, inherits: (c, s) => { Object.setPrototypeOf(c.prototype, s.prototype); }, types: { isPromise: (x) => x instanceof Promise },
  };
  const builtins = {
    fs: fsModulo, "fs/promises": fsPromesas, path: rutaNode, util, events: EventEmitter, assert, "assert/strict": assert,
    os: { EOL: "\n", platform: () => "linux", homedir: () => RAIZ, tmpdir: () => "/tmp", cpus: () => [], type: () => "Linux", arch: () => "x64", hostname: () => "codigocamp" },
    readline: { createInterface: crearInterfaz(false), promises: { createInterface: crearInterfaz(true) } },
    "readline/promises": { createInterface: crearInterfaz(true) },
    "timers/promises": { setTimeout: (ms, v) => new Promise((ok) => self.setTimeout(() => ok(v), ms)) },
  };
  const requerirIntegrado = (n) => { const k = String(n).replace(/^node:/, ""); return k in builtins ? builtins[k] : undefined; };
  self.__cc_require = (n) => { const m = requerirIntegrado(n); if (m === undefined) throw new Error(`Cannot find module '${n}'`); return m; };

  // ---- process ----
  const inicio = performance.now();
  const procesoEventos = new EventEmitter();
  const proceso = Object.assign(procesoEventos, {
    argv: ["/usr/local/bin/node", RAIZ + "/" + (CC.main === "[eval]" ? "" : CC.main), ...CC.args], env: {}, platform: "linux", arch: "x64", pid: 1, version: "v22.0.0", versions: { node: "22.0.0", navegador: "CódigoCamp" },
    exitCode: undefined, cwd: () => RAIZ + (CC.cwd ? "/" + CC.cwd : ""), uptime: () => (performance.now() - inicio) / 1000,
    exit: (c) => { if (c !== undefined) proceso.exitCode = c; throw EXIT; }, memoryUsage: () => ({ rss: 0, heapTotal: 0, heapUsed: 0 }),
    nextTick: (f, ...a) => queueMicrotask(() => { try { f(...a); } catch (e) { fatal(e); } }),
    hrtime: Object.assign((p) => { const t = performance.now(); const s = Math.floor(t / 1000); const n = Math.floor((t % 1000) * 1e6); return p ? [s - p[0], n - p[1]] : [s, n]; }, { bigint: () => BigInt(Math.floor(performance.now() * 1e6)) }),
    stdout: { write: (t) => { escribir("out", String(t)); return true; }, isTTY: false, columns: 80 }, stderr: { write: (t) => { escribir("err", String(t)); return true; }, isTTY: false },
    stdin: { isTTY: false, on() {}, setEncoding() {} },
  });
  self.process = proceso;
  self.global = self;
  self.require = undefined;

  // ---- require / módulos CommonJS entre archivos del proyecto ----
  const cache = Object.create(null);
  const candidatos = (r) => [r, r + ".js", r + ".cjs", r + ".json", r + ".ts", r + "/index.js", r + "/index.ts", r + "/index.json"];
  function cargarModulo(ruta, codigo) {
    const modulo = { exports: {}, id: ruta, filename: RAIZ + "/" + ruta, loaded: false };
    cache[ruta] = modulo;
    if (ruta.endsWith(".json")) { try { modulo.exports = JSON.parse(codigo); } catch (e) { throw new SyntaxError(`${ruta}: ${e.message}`); } return modulo; }
    const dir = ruta.includes("/") ? ruta.slice(0, ruta.lastIndexOf("/")) : "";
    const req = (n) => requerir(n, dir);
    req.cache = cache; req.resolve = (n) => n;
    const cuerpo = codigo.replace(/^#!.*/, "");
    const f = (0, eval)(`(function (exports, require, module, __filename, __dirname) {${cuerpo}\n})\n//# sourceURL=${RAIZ}/${ruta}`);
    f.call(modulo.exports, modulo.exports, req, modulo, RAIZ + "/" + ruta, RAIZ + (dir ? "/" + dir : ""));
    modulo.loaded = true;
    return modulo;
  }
  function requerir(nombre, desdeDir) {
    const integrado = requerirIntegrado(nombre);
    if (integrado !== undefined) return integrado;
    if (!/^(\.{1,2}\/|\.{1,2}$|\/)/.test(nombre)) {
      const e = new Error(`Cannot find module '${nombre}'\nrequire() solo funciona con tus archivos (./archivo) y los módulos fs, path, util, os, events, readline y assert.\nLos paquetes de npm se usan con import desde un archivo .mjs después de «npm install ${nombre}»: import x from "${nombre}".`);
      e.code = "MODULE_NOT_FOUND"; throw e;
    }
    const base = nombre.startsWith("/") ? aInterna(nombre) : aInterna(rutaNode.join(RAIZ, desdeDir, nombre));
    const hallado = base === null ? undefined : candidatos(base).find((c) => c in archivos && !esCarpeta(c));
    if (hallado === undefined) { const e = new Error(`Cannot find module '${nombre}'`); e.code = "MODULE_NOT_FOUND"; throw e; }
    return (cache[hallado] || cargarModulo(hallado, archivos[hallado])).exports;
  }

  function terminar(codigo) {
    if (terminado) return;
    try { procesoEventos.emit("exit", codigo); } catch { /* el programa ya terminó */ }
    terminado = true;
    enviar({ t: "fin", codigo, cambios, creadas: Object.keys(archivos).filter((r) => !original.has(r)) });
  }
  self.__cc_terminar = terminar;
  self.addEventListener("unhandledrejection", (ev) => { ev.preventDefault(); fatal(ev.reason); });
  self.addEventListener("error", (ev) => { ev.preventDefault(); fatal(ev.error || new Error(ev.message)); });
  self.__cc_fin_main = () => revisar();

  if (!CC.esm) {
    try {
      if (CC.main === "[eval]") {
        const r = (0, eval)(CC.codigo + `\n//# sourceURL=[eval]`);
        if (CC.imprimir) consola.log(r);
      } else {
        cargarModulo(CC.main, archivos[CC.main]);
      }
    } catch (e) { if (e !== EXIT) fatal(e); else terminar(proceso.exitCode || 0); }
    if (!terminado) revisar();
  }
}

// ===================================================================================================
//  Lado de la página: prepara el Worker, reenvía la salida y aplica los cambios a los archivos.
// ===================================================================================================
const esModulo = (codigo) => /^\s*(?:import\s+(?:[\w*${'"]|\{)|export\s+(?:default|const|let|var|function|class|async|\{|\*))/m.test(codigo);

function transformarImportIntegrado(clausula, modulo) {
  const limpia = clausula.trim().replace(/\s+/g, " ");
  const req = `__cc_require(${JSON.stringify(modulo)})`;
  let m;
  if ((m = /^\* as (\w+)$/.exec(limpia))) return `const ${m[1]} = ${req};`;
  if ((m = /^(\w+)$/.exec(limpia))) return `const ${m[1]} = ${req};`;
  if ((m = /^(?:(\w+)\s*,\s*)?\{([^}]*)\}$/.exec(limpia))) {
    const nombres = m[2].split(",").map((s) => s.trim()).filter(Boolean).map((s) => s.replace(/^(\w+)\s+as\s+(\w+)$/, "$1: $2")).join(", ");
    return `const { ${nombres} } = ${req};${m[1] ? ` const ${m[1]} = ${req};` : ""}`;
  }
  return null;
}

/** Reescribe los import de un módulo ES: archivos del proyecto -> blob URL; módulos integrados -> __cc_require. */
async function prepararModulo(ruta, codigo, py, urls, enCurso, deps) {
  const dir = FS.carpetaDe(ruta);
  const re = /\b(import|export)(\s*[\w*${},\s]*?\s*from\s*|\s*)(["'])([^"'\n]+)\3/g;
  let resultado = "";
  let ultimo = 0;
  let m;
  while ((m = re.exec(codigo))) {
    const [todo, palabra, clausula, comilla, spec] = m;
    let reemplazo;
    const nombre = spec.replace(/^node:/, "");
    if (BUILTINS.includes(nombre)) {
      const t = palabra === "import" && clausula.trim() ? transformarImportIntegrado(clausula.replace(/\s*from\s*$/, ""), nombre) : (palabra === "import" ? "" : null);
      if (t === null) throw new Error(`No se puede usar «export ... from "${spec}"» con módulos integrados.`);
      reemplazo = t;
    } else if (/^\.{1,2}\//.test(spec)) {
      const destino = FS.resolver(dir, spec);
      const real = destino === null ? undefined : [destino, destino + ".js", destino + ".mjs", destino + "/index.js"].find((c) => FS.tieneArchivo(py, c));
      if (real === undefined) throw new Error(`No se encontró el módulo '${spec}' (importado desde ${ruta}).`);
      if (enCurso.includes(real)) throw new Error(`Dependencia circular entre módulos (${[...enCurso, real].join(" → ")}): no se puede ejecutar así aquí.`);
      if (!urls.has(real)) urls.set(real, await construirModulo(real, py.files[real], py, urls, [...enCurso, ruta], "", deps));
      reemplazo = `${palabra}${clausula}${comilla}${urls.get(real)}${comilla}`;
    } else if (/^https:\/\//.test(spec)) {
      reemplazo = todo; // import directo desde una URL (CDN): lo resuelve el navegador
    } else {
      const url = urlDeCdn(deps, spec);
      if (!url) throw new Error(`No se encontró el paquete '${spec}'. Instálalo primero con: npm install ${spec.split("/")[0].startsWith("@") ? spec.split("/").slice(0, 2).join("/") : spec.split("/")[0]}`);
      reemplazo = `${palabra}${clausula}${comilla}${url}${comilla}`;
    }
    resultado += codigo.slice(ultimo, m.index) + reemplazo;
    ultimo = m.index + todo.length;
  }
  return resultado + codigo.slice(ultimo);
}

async function construirModulo(ruta, codigo, py, urls, enCurso, prefijo = "", deps = {}) {
  const texto = await prepararModulo(ruta, codigo, py, urls, enCurso, deps);
  const fuente = `${prefijo}${texto}\n;globalThis.__cc_fin_main && globalThis.__cc_fin_main();\n//# sourceURL=/workspace/${ruta}`;
  return URL.createObjectURL(new Blob([fuente], { type: "text/javascript" }));
}

/** Aplica al proyecto lo que el programa escribió con fs. */
export function aplicarCambios(py, cambios) {
  let huboCambios = false;
  for (const c of cambios.carpetasBorradas || []) if (FS.existe(py, c)) { FS.borrar(py, c); huboCambios = true; }
  for (const c of cambios.folders || []) if (!FS.esCarpeta(py, c) && FS.crearCarpeta(py, c, { padres: true }).ok) huboCambios = true;
  for (const [ruta, texto] of Object.entries(cambios.files || {})) {
    if (texto === null) { if (FS.existe(py, ruta)) { FS.borrar(py, ruta); huboCambios = true; } continue; }
    const r = FS.tieneArchivo(py, ruta) ? FS.escribirArchivo(py, ruta, texto) : FS.crearArchivo(py, ruta, texto, { padres: true });
    if (r.ok) huboCambios = true;
  }
  return huboCambios;
}

/**
 * Ejecuta JavaScript en un Worker. Devuelve el código de salida.
 * @param {object} o  { ruta, codigo, args, cwd, proyecto, out, err, leerLinea, senal, cambio, imprimir, archivos? }
 */
export async function ejecutarNode(o) {
  const py = o.proyecto;
  const archivos = o.archivos || py.files;
  const esm = o.ruta !== "[eval]" && esModulo(o.codigo);
  const CC = { files: archivos, folders: py.folders, main: o.ruta, args: o.args || [], cwd: o.cwd || "", esm, codigo: o.ruta === "[eval]" ? o.codigo : undefined, imprimir: Boolean(o.imprimir) };
  const urls = new Map();
  let worker;
  let urlScript;
  try {
    const preludio = `(${runtimeNode.toString()})(${JSON.stringify(CC)});`;
    if (esm) {
      const urlPreludio = URL.createObjectURL(new Blob([preludio], { type: "text/javascript" }));
      urls.set("::preludio", urlPreludio);
      urlScript = await construirModulo(o.ruta, o.codigo, { ...py, files: archivos }, urls, [], `import ${JSON.stringify(urlPreludio)};`, dependenciasDe(py));
      worker = new Worker(urlScript, { type: "module" });
    } else {
      urlScript = URL.createObjectURL(new Blob([preludio], { type: "text/javascript" }));
      worker = new Worker(urlScript);
    }
  } catch (error) {
    o.err(`${error.message}\n`);
    return 1;
  }
  const limpiarUrls = () => { [urlScript, ...urls.values()].forEach((u) => { try { URL.revokeObjectURL(u); } catch { /* nada */ } }); };
  return new Promise((resolver) => {
    let hecho = false;
    let textoErr = "";
    const terminar = (codigo, mensaje) => {
      if (hecho) return;
      hecho = true;
      clearTimeout(limite);
      worker.terminate();
      limpiarUrls();
      if (mensaje) o.err(mensaje);
      if (codigo === 1 && /\b(document|window|alert|navigator|localStorage|sessionStorage|location) is not defined/.test(textoErr)) {
        o.err(color.gris("Pista: ese código es de navegador (usa document/window…) y Node no lo tiene. Para verlo funcionar, abre la vista previa de tu página HTML.\n"));
      }
      const ayuda = codigo === 1 ? sugerenciaNode(textoErr + (mensaje || "")) : null;
      if (ayuda) o.err(color.amarillo(ayuda) + "\n");
      resolver(codigo);
    };
    const limite = setTimeout(() => terminar(124, `\n${color.rojo("Tiempo máximo agotado")} (2 minutos): se detuvo el programa.\n`), TIEMPO_MAXIMO);
    o.senal?.addEventListener("abort", () => terminar(130), { once: true });
    worker.onmessage = async (ev) => {
      const m = ev.data;
      if (m.t === "out") o.out(m.s);
      else if (m.t === "err") { textoErr = (textoErr + m.s).slice(-2000); o.err(m.s); }
      else if (m.t === "leer") {
        const valor = await o.leerLinea(m.prompt);
        if (!hecho) worker.postMessage({ t: "linea", valor });
      } else if (m.t === "fin") {
        if (aplicarCambios(py, m.cambios)) o.cambio?.({});
        terminar(m.codigo);
      }
    };
    worker.onerror = (ev) => terminar(1, `${ev.message || "Error al iniciar el programa"}\n`);
  });
}

// ---------------------------------------------------------------------------- TypeScript ----
// El cargador AMD del editor (Monaco) define `define.amd`: los motores UMD (Pyodide, sql.js…) se registrarían como
// módulos AMD en vez de crear su variable global. Mientras se carga un motor se oculta esa marca.
let cargasUmd = 0;
export const cargarScript = (url) => new Promise((ok, ko) => {
  const s = document.createElement("script");
  const def = globalThis.define;
  const amd = def?.amd;
  if (def && amd) { cargasUmd += 1; def.amd = undefined; }
  const fin = () => { if (def && amd && --cargasUmd === 0) def.amd = amd; };
  s.src = url;
  s.onload = () => { fin(); ok(); };
  s.onerror = () => { fin(); s.remove(); ko(new Error("No se pudo descargar el motor. Revisa tu conexión.")); };
  document.head.appendChild(s);
});

/** Compilador de TypeScript: la copia incluida en CódigoCamp y, si faltara, el CDN. */
async function cargarTypeScript() {
  if (globalThis.ts) return;
  try { await cargarScript("/vendor/typescript/typescript.min.js"); } catch { /* se intenta el CDN */ }
  if (!globalThis.ts) await cargarScript("https://cdnjs.cloudflare.com/ajax/libs/typescript/5.4.5/typescript.min.js");
}

/** JSX / TSX / TypeScript → módulo ES para la vista previa (JSX automático: react/jsx-runtime o preact/jsx-runtime). */
export async function transpilarModulo(codigo, ruta, { jsxImportSource = "react" } = {}) {
  await cargarTypeScript();
  const ts = globalThis.ts;
  const nombre = /\.(m?js|cjs)$/.test(ruta) ? ruta.replace(/\.(m?js|cjs)$/, ".jsx") : ruta; // un .js con JSX se trata como .jsx
  const r = ts.transpileModule(codigo, {
    fileName: nombre, reportDiagnostics: true,
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX, jsxImportSource, verbatimModuleSyntax: false, isolatedModules: true },
  });
  const errores = (r.diagnostics || []).filter((d) => d.category === 1);
  if (errores.length) {
    const d = errores[0];
    const linea = d.file && d.start !== undefined ? ` (línea ${d.file.getLineAndCharacterOfPosition(d.start).line + 1})` : "";
    throw new Error(ts.flattenDiagnosticMessageText(d.messageText, "\n") + linea);
  }
  return r.outputText;
}

/** Transpila un archivo TypeScript a CommonJS con el compilador oficial (se descarga la primera vez). */
export async function transpilarTS(codigo) {
  await cargarTypeScript();
  const ts = globalThis.ts;
  const r = ts.transpileModule(codigo, { reportDiagnostics: true, compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS } });
  const errores = (r.diagnostics || []).filter((d) => d.category === 1);
  if (errores.length) throw new Error(errores.map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n")).join("\n"));
  return r.outputText;
}

export async function ejecutarTS(o) {
  const archivos = { ...o.proyecto.files };
  try {
    o.out?.(color.gris("Compilando TypeScript…\n"));
    for (const r of Object.keys(archivos)) if (/\.tsx?$/.test(r)) archivos[r] = await transpilarTS(archivos[r]);
  } catch (error) {
    o.err(`${error.message}\n`);
    return 1;
  }
  return ejecutarNode({ ...o, archivos, codigo: archivos[o.ruta] });
}

// ------------------------------------------------------------------------------- Python ----
let pyodidePromesa = null;
export const cargarPyodide = () => {
  pyodidePromesa ??= (async () => {
    // Python base incluido en CódigoCamp (/vendor/pyodide); los paquetes extra (numpy, sqlite3, micropip…) se bajan del CDN al usarlos.
    let indexURL = "/vendor/pyodide/";
    if (!globalThis.loadPyodide) {
      try { await cargarScript(indexURL + "pyodide.js"); }
      catch { indexURL = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/"; await cargarScript(indexURL + "pyodide.js"); }
    }
    try { return await globalThis.loadPyodide({ indexURL }); }
    catch (e) {
      if (indexURL.startsWith("https:")) throw e;
      return globalThis.loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/" });
    }
  })().catch((error) => { pyodidePromesa = null; throw error; });
  return pyodidePromesa;
};

export const RAIZ_PY = "/workspace";
/** Sube cada vez que un programa de Python reescribe /workspace (los servidores de servidorpy.js lo vuelven a sincronizar). */
export let generacionFsPy = 0;
export const nuevaGeneracionFsPy = () => { generacionFsPy += 1; return generacionFsPy; };

/** Escribe el proyecto en /workspace de Python. Los archivos de la cuenta que vienen en `binarios` van con sus bytes reales. */
export function escribirEnPyodide(pyo, py, binarios = new Map()) {
  const { FS: sis } = pyo;
  const asegurar = (dir) => { let acc = ""; for (const p of dir.split("/").filter(Boolean)) { acc += "/" + p; try { sis.mkdir(acc); } catch { /* ya existe */ } } };
  asegurar(RAIZ_PY);
  py.folders.forEach((c) => asegurar(`${RAIZ_PY}/${c}`));
  for (const [ruta, texto] of Object.entries(py.files)) { asegurar(`${RAIZ_PY}/${FS.carpetaDe(ruta)}`); sis.writeFile(`${RAIZ_PY}/${ruta}`, binarios.get(ruta) ?? texto); }
}

// Archivos binarios que Python recibe con sus bytes (bases SQLite, imágenes, Excel, CSV grandes…). Tope por si la cuenta es enorme.
const PARA_PYTHON = new Set(["db", "sqlite", "sqlite3", "db3", "png", "jpg", "jpeg", "gif", "webp", "bmp", "csv", "tsv", "json", "xlsx", "xls", "parquet", "npy", "npz", "pkl", "txt", "wav", "mp3", "pdf", "zip"]);
const MAX_PYTHON = { porArchivo: 50 * 1024 * 1024, total: 200 * 1024 * 1024 };

/** Bytes de los archivos de la cuenta que se le pasan a Python (Map ruta → Uint8Array). */
export async function binariosParaPython(py, archivos) {
  const salida = new Map();
  if (!archivos) return salida;
  let total = 0;
  for (const [ruta, texto] of Object.entries(py.files)) {
    const m = leerMarcador(texto);
    if (!m || !PARA_PYTHON.has(FS.extension(ruta)) || m.tamano > MAX_PYTHON.porArchivo || total + m.tamano > MAX_PYTHON.total) continue;
    try { salida.set(ruta, await archivos.bytes(texto)); total += m.tamano; } catch { /* sin conexión: Python verá el marcador */ }
  }
  return salida;
}

const decodificadorEstricto = new TextDecoder("utf-8", { fatal: true });
/** Texto si los bytes son UTF-8 sin NUL; si no, null (es binario). */
export function comoTexto(bytes) {
  try { const t = decodificadorEstricto.decode(bytes); return t.includes("\u0000") ? null : t; } catch { return null; }
}

/**
 * Los binarios que dejó Python: los que no cambiaron conservan su marcador; los nuevos o cambiados se suben a la cuenta.
 * Escribe el resultado en `despues.files` (para que diferencias() los trate como cualquier archivo).
 */
export async function consolidarBinarios(antes, despues, { subir, hash, err = () => {} }) {
  for (const [ruta, bytes] of despues.binarios) {
    const previo = leerMarcador(antes.files[ruta]);
    if (previo && previo.tamano === bytes.length && previo.hash === await hash(bytes)) { despues.files[ruta] = antes.files[ruta]; continue; }
    if (!subir) { err(`No se pudo guardar ${ruta}: los archivos binarios necesitan la sesión iniciada.\n`); if (antes.files[ruta] !== undefined) despues.files[ruta] = antes.files[ruta]; continue; }
    try { despues.files[ruta] = await subir(bytes, { nombre: ruta }); }
    catch (e) { err(`No se pudo guardar ${ruta}: ${e.message}\n`); if (antes.files[ruta] !== undefined) despues.files[ruta] = antes.files[ruta]; }
  }
  return despues;
}

const sha256Hex = async (bytes) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map((b) => b.toString(16).padStart(2, "0")).join("");

export function leerDePyodide(pyo) {
  const { FS: sis } = pyo;
  const salida = { files: {}, folders: [] };
  Object.defineProperty(salida, "binarios", { value: new Map(), enumerable: false });
  if (!existeEnPyodide(sis, RAIZ_PY)) return salida;
  const recorrer = (dir) => {
    for (const nombre of sis.readdir(dir)) {
      if (nombre === "." || nombre === "..") continue;
      const ruta = `${dir}/${nombre}`;
      const rel = ruta.slice(RAIZ_PY.length + 1);
      if (nombre === "__pycache__" || nombre.endsWith(".pyc")) continue;
      if (sis.isDir(sis.stat(ruta).mode)) { salida.folders.push(rel); recorrer(ruta); } else {
        try {
          const bytes = sis.readFile(ruta);
          const t = typeof bytes === "string" ? bytes : comoTexto(bytes);
          if (t === null) salida.binarios.set(rel, bytes); else salida.files[rel] = t;
        } catch { /* ilegible: se ignora */ }
      }
    }
  };
  recorrer(RAIZ_PY);
  return salida;
}

const existeEnPyodide = (sis, ruta) => { try { sis.stat(ruta); return true; } catch { return false; } };

/** Vacía /workspace. La primera vez la carpeta aún no existe (readdir fallaría): en ese caso se crea. */
export function borrarEnPyodide(pyo, dir = RAIZ_PY, raiz = true) {
  const { FS: sis } = pyo;
  // Python no puede borrar la carpeta en la que está parado (EBUSY): tras `cd backend` o un servidor en backend/,
  // la siguiente ejecución fallaba con «[object Object]». Primero se sale a la raíz.
  if (raiz) { try { const actual = sis.cwd(); if (actual === dir || actual.startsWith(dir + "/")) sis.chdir("/"); } catch { /* nada */ } }
  if (raiz && !existeEnPyodide(sis, dir)) { sis.mkdir(dir); return; }
  for (const nombre of sis.readdir(dir)) {
    if (nombre === "." || nombre === "..") continue;
    const ruta = `${dir}/${nombre}`;
    if (sis.isDir(sis.stat(ruta).mode)) { borrarEnPyodide(pyo, ruta, false); sis.rmdir(ruta); } else sis.unlink(ruta);
  }
  if (raiz) return;
}

/** Diferencias entre el proyecto y lo que dejó el programa Python (para aplicarlas con aplicarCambios). */
export function diferencias(antes, despues) {
  const cambios = { files: {}, folders: [], carpetasBorradas: [] };
  for (const [r, t] of Object.entries(despues.files)) if (antes.files[r] !== t) cambios.files[r] = t;
  for (const r of Object.keys(antes.files)) if (!(r in despues.files)) cambios.files[r] = null;
  for (const c of despues.folders) if (!antes.folders.includes(c)) cambios.folders.push(c);
  for (const c of antes.folders) if (!despues.folders.includes(c)) cambios.carpetasBorradas.push(c);
  return cambios;
}

// Números de error de Pyodide/Emscripten (WASI), con su equivalente de Linux para que el mensaje se parezca al de tu PC.
const ERRNO = { 2: [13, "Permission denied"], 10: [16, "Device or resource busy"], 20: [17, "File exists"], 28: [22, "Invalid argument"], 31: [21, "Is a directory"],
  37: [36, "File name too long"], 44: [2, "No such file or directory"], 51: [28, "No space left on device"], 54: [20, "Not a directory"], 55: [39, "Directory not empty"], 63: [1, "Operation not permitted"] };
/** Texto legible de cualquier error (los del sistema de archivos de Pyodide no traen .message y salían como «[object Object]»). */
export function textoError(e) {
  if (e && typeof e === "object" && typeof e.errno === "number" && !e.message) {
    const [n, texto] = ERRNO[e.errno] || [e.errno, "error del sistema de archivos"];
    return `OSError: [Errno ${n}] ${texto}`;
  }
  if (e && typeof e.message === "string" && e.message) return e.message;
  if (e && typeof e === "object") { try { return JSON.stringify(e); } catch { /* nada */ } }
  return String(e);
}

// Partes de la biblioteca estándar que Pyodide trae aparte. Las importan los frameworks por dentro (anyio importa ssl,
// Werkzeug usa hashlib para las contraseñas), aunque tu código no las importe: se cargan antes de ejecutar.
export const STDLIB_APARTE = { ssl: "ssl", _ssl: "ssl", hashlib: "hashlib", _hashlib: "hashlib", lzma: "lzma", _lzma: "lzma", sqlite3: "sqlite3", _sqlite3: "sqlite3", _pydecimal: "pydecimal", pydoc_data: "pydoc-data" };
const USA_RED_O_CIFRADO = /^\s*(?:from|import)\s+(?:requests|httpx|urllib3|aiohttp|fastapi|starlette|anyio|flask|werkzeug|jwt|jose|passlib|bcrypt|smtplib|ssl|hashlib|hmac|secrets|email|http|urllib|django|sqlalchemy|sqlmodel|pydantic|dotenv|itsdangerous|authlib|google)\b/m;
/** Carga ssl, hashlib y sqlite3 de Pyodide (una vez). Sin red o sin ellos, sigue: el error real lo dirá Python. */
export async function cargarStdlibAparte(pyo, nombres = ["ssl", "hashlib", "sqlite3"]) {
  try { await pyo.loadPackage(nombres); } catch { /* nada */ }
}

const limpiarTraza = (mensaje) => String(mensaje).split("\n").filter((l) => !/_pyodide|pyodide\/|python3\d+\.zip/.test(l)).join("\n").trim();

export async function ejecutarPython(o) {
  let pyo;
  try {
    if (!pyodidePromesa) o.out(color.gris("Cargando Python (solo la primera vez, puede tardar unos segundos)…\n"));
    pyo = await cargarPyodide();
  } catch (error) { o.err(`${error.message}\n`); return 1; }
  if (o.senal?.aborted) return 130;
  if (o.almacenPip) await restaurarPaquetes({ pyo, lista: o.almacenPip.leer(), out: o.out, err: o.err });
  // Paquetes de Pyodide que importa el programa (o sus módulos), p. ej. sqlite3, numpy. pymysql y mysql.connector vienen de CódigoCamp.
  const fuentesPy = [o.codigo, ...Object.entries(o.proyecto.files).filter(([r, t]) => r.endsWith(".py") && t.length < 200_000).map(([, t]) => t)].join("\n")
    .replace(/^\s*(?:import|from)\s+(?:pymysql|mysql|MySQLdb|psycopg2?|pymongo|bson|redis)\b.*$/gm, "");
  try { await pyo.loadPackagesFromImports(fuentesPy); } catch { /* si falta un paquete, Python mostrará su propio error */ }
  if (USA_RED_O_CIFRADO.test(fuentesPy)) await cargarStdlibAparte(pyo);
  // Bases de datos: tu servidor real por el puente o, si no se puede llegar, SQLite en el proyecto (bdpython.js).
  let conBd = false;
  if (/^\s*(?:from|import)\s+(?:pymysql|mysql|MySQLdb|psycopg2?|pymongo|bson|redis|sqlalchemy|sqlmodel|flask_sqlalchemy|flask_mysqldb|django|requests|httpx|urllib|smtplib|email|google|openai|anthropic|fastapi|flask|aiohttp)\b/m.test(fuentesPy + "\n" + o.codigo)) {
    try {
      const { prepararBdPython } = await import("./bdpython.js");
      await prepararBdPython(pyo, { bd: o.bd ?? null });
      conBd = true;
    } catch (e) {
      if (o.bd) { try { instalarMysqlEnPython(pyo, o.bd); } catch { /* nada */ } }
      o.err(color.gris(`(bases de datos: ${e.message})\n`));
    }
  }
  const py = o.proyecto;
  const antes = { files: { ...py.files }, folders: [...py.folders] };
  const binarios = await binariosParaPython(py, o.archivos);
  let codigo = 0;
  try {
    nuevaGeneracionFsPy();
    borrarEnPyodide(pyo);
    escribirEnPyodide(pyo, py, binarios);
    const cwd = `${RAIZ_PY}${o.cwd ? "/" + o.cwd : ""}`;
    pyo.FS.chdir(cwd);
    pyo.setStdout({ batched: (s) => o.out(s + "\n") });
    pyo.setStderr({ batched: (s) => o.err(s + "\n") });
    // Lo escrito en la terminal antes de ejecutar (o pegado, o «echo … | python»): una línea por cada input().
    const lineas = typeof o.entrada === "string" ? o.entrada.replace(/\r\n?/g, "\n").split("\n") : null;
    if (lineas && lineas[lineas.length - 1] === "") lineas.pop();
    pyo.setStdin({ stdin: () => {
      if (lineas) return lineas.length ? lineas.shift() : undefined;
      const r = globalThis.prompt?.("Entrada para input():");
      if (r === null || r === undefined) return undefined;
      o.out(r + "\n");
      return r;
    } });
    pyo.runPython(`import sys\nfor _p in (${JSON.stringify(cwd)}, ${JSON.stringify(RAIZ_PY)}):\n    if _p not in sys.path: sys.path.insert(0, _p)\nsys.argv = ${JSON.stringify([o.ruta === "<cadena>" ? "-c" : FS.nombreBase(o.ruta), ...(o.args || [])])}`);
    if (conBd) pyo.runPython(`preparar_bd(${JSON.stringify(RAIZ_PY)})`);
    await pyo.runPythonAsync(o.codigo, { filename: o.ruta === "<cadena>" ? "<cadena>" : `${RAIZ_PY}/${o.ruta}` });
  } catch (error) {
    o.err(limpiarTraza(textoError(error)) + "\n");
    const ayuda = sugerenciaPython(textoError(error), { py, cwd: o.cwd, venv: o.almacenPip?.venv ?? null });
    if (ayuda) o.err(color.amarillo(ayuda) + "\n");
    codigo = 1;
  } finally {
    if (conBd) { try { pyo.runPython("guardar_mongo()"); } catch { /* nada */ } }   // antes de copiar los archivos al proyecto
    try {
      const despues = await consolidarBinarios(antes, leerDePyodide(pyo), { subir: o.archivos ? (b, op) => o.archivos.subir(b, op) : null, hash: sha256Hex, err: o.err });
      if (aplicarCambios(py, diferencias(antes, despues))) o.cambio?.({});
      borrarEnPyodide(pyo);
    } catch { /* el programa no dejó nada que guardar */ }
    if (o.bd) cerrarMysqlEnPython(pyo);
  }
  return codigo;
}

// ------------------------------------------------------------------------------------ SQL ----
let SQL;
/** Motor SQLite (sql.js): copia incluida en CódigoCamp; si faltara, el CDN. */
export async function cargarSQL() {
  if (SQL) return SQL;
  let base = "/vendor/sqljs/";
  try { await cargarScript(base + "sql-wasm.js"); } catch { base = "https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/"; await cargarScript(base + "sql-wasm.js"); }
  SQL = await globalThis.initSqlJs({ locateFile: (f) => base + f });
  return SQL;
}

export async function ejecutarSQL(o) {
  try { await cargarSQL(); } catch (error) { o.err(`${error.message}\n`); return 1; }
  const db = new SQL.Database();
  try {
    const rs = db.exec(o.codigo);
    if (!rs.length) o.out(color.gris("Consulta ejecutada. No devolvió filas.\n"));
    o.out(rs.map((r) => [r.columns.join(" | "), ...r.values.map((v) => v.map((x) => (x === null ? "NULL" : x)).join(" | "))].join("\n")).join("\n\n") + (rs.length ? "\n" : ""));
    return 0;
  } catch (error) { o.err(`Error: ${error.message}\n`); return 1; } finally { db.close(); }
}

/** Los ejecutores que usa el shell. `api` es la función de llamadas al servidor (js/auth.js). */
export function crearEjecutores({ api, almacenPip = null, archivos = null, bd = null }) {
  return {
    node: ejecutarNode,
    ts: ejecutarTS,
    python: (o) => ejecutarPython({ ...o, almacenPip: o.almacenPip ?? almacenPip, archivos, bd }),
    servidorPy: async (o) => (await import("./servidorpy.js")).ejecutarServidorPy({ ...o, almacenPip: o.almacenPip ?? almacenPip, archivos, bd }),
    sql: ejecutarSQL,
    cargarSQL,
    async docker({ args, archivos = null, entrada = "", cwd = "" }) {
      try {
        const d = await api("/api/docker", { args, archivos, entrada, cwd, proyecto: "mi-proyecto" });
        return { salida: d.salida || "", error: Boolean(d.error), puertos: d.puertos || [] };
      } catch (error) {
        return { salida: error.message, error: true, puertos: [] };
      }
    },
    async pythonServidor({ ruta, archivos, entrada = "", args = [] }) {
      try {
        const d = await api("/api/python/run", { ruta, archivos, entrada, args });
        return { salida: d.salida || "", error: Boolean(d.error) };
      } catch (error) {
        return { salida: error.message, error: true };
      }
    },
    async servidor({ lenguaje, codigo, entrada = "", archivos = [] }) {
      let reloj;
      const limite = new Promise((resolver) => { reloj = setTimeout(() => resolver({ salida: "El servidor tardó demasiado en responder (los compiladores en línea a veces van lentos). Inténtalo de nuevo.", error: true }), 75_000); });
      try {
        const d = await Promise.race([api("/api/run", { lenguaje, codigo, entrada, archivos }), limite]);
        return { salida: d.salida || "", error: Boolean(d.error), donde: d.donde || "" };
      } catch (error) {
        return { salida: error.message, error: true };
      } finally {
        clearTimeout(reloj);
      }
    },
  };
}
