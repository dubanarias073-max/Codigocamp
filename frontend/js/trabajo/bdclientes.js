// Clientes de terminal para PostgreSQL (psql), MongoDB (mongosh) y Redis (redis-cli), con la salida de los reales.
// Usan ClienteBD (servidor de CódigoCamp o puente del PC del usuario), igual que mysql.
import { color } from "./ansi.js";
import * as FS from "./fs.js";
import { leerMarcador } from "./archivos.js";
import { ErrorBD } from "./bd.js";

const celda = (v) => v === null || v === undefined ? "" : typeof v === "object" ? (v.$json ?? (v.$bytes !== undefined ? `\\x${v.$bytes}` : Array.isArray(v) ? `{${v.map((x) => celda(x)).join(",")}}` : JSON.stringify(v))) : typeof v === "boolean" ? (v ? "t" : "f") : String(v);
const largo = (t) => [...t].length;
const esNum = (v) => typeof v === "number" || (typeof v === "string" && /^-?\d+(\.\d+)?$/.test(v));

function leerScript(o, nombre) {
  const ruta = FS.resolver(o.cwd, String(nombre).replace(/^['"]|['"]$/g, ""));
  const t = ruta === null ? undefined : o.py.files[ruta];
  if (t === undefined) throw new ErrorBD(`${nombre}: No such file or directory`);
  if (leerMarcador(t)) throw new ErrorBD(`${nombre}: es un archivo binario`);
  return t;
}

// ================================================================================ psql ====
export function tablaPsql(columnas, filas) {
  const textos = filas.map((f) => f.map((v) => celda(v)));
  const anchos = columnas.map((c, i) => Math.max(largo(c), ...textos.map((f) => Math.max(...f[i].split("\n").map(largo)))));
  const numericas = columnas.map((_, i) => filas.length > 0 && filas.every((f) => f[i] === null || esNum(f[i])));
  const centrar = (t, a) => { const libre = a - largo(t); const izq = Math.floor(libre / 2); return " ".repeat(izq) + t + " ".repeat(libre - izq); };
  const pad = (t, a, der) => der ? " ".repeat(a - largo(t)) + t : t + " ".repeat(a - largo(t));
  const lineas = [` ${columnas.map((c, i) => centrar(c, anchos[i])).join(" | ")} `.replace(/\s+$/, ""), anchos.map((a) => "-".repeat(a + 2)).join("+")];
  for (const f of textos) lineas.push(` ${f.map((t, i) => pad(t, anchos[i], numericas[i])).join(" | ")}`.replace(/\s+$/, ""));
  lineas.push(`(${filas.length} ${filas.length === 1 ? "row" : "rows"})`);
  return lineas.join("\n") + "\n\n";
}

export function expandidoPsql(columnas, filas) {
  const ancho = Math.max(...columnas.map(largo));
  return filas.map((f, n) => `-[ RECORD ${n + 1} ]${"-".repeat(Math.max(1, ancho - 8))}+------\n${columnas.map((c, i) => `${c.padEnd(ancho)} | ${celda(f[i])}`).join("\n")}`).join("\n") + "\n\n";
}

/** Divide SQL de PostgreSQL en sentencias: respeta 'cadenas', "identificadores", $$cuerpos$$ y comentarios. */
export function partirPg(texto) {
  const completas = [];
  let actual = "", i = 0;
  while (i < texto.length) {
    const c = texto[i], resto = texto.slice(i);
    if (c === "'" || c === '"') { let j = i + 1; while (j < texto.length && !(texto[j] === c && texto[j + 1] !== c)) j += texto[j] === c ? 2 : 1; actual += texto.slice(i, j + 1); i = j + 1; continue; }
    const dolar = /^\$([A-Za-z_]\w*)?\$/.exec(resto);
    if (dolar) { const fin = texto.indexOf(dolar[0], i + dolar[0].length); const j = fin < 0 ? texto.length : fin + dolar[0].length; actual += texto.slice(i, j); i = j; continue; }
    if (resto.startsWith("--")) { const j = texto.indexOf("\n", i); i = j < 0 ? texto.length : j + 1; actual += "\n"; continue; }
    if (resto.startsWith("/*")) { const j = texto.indexOf("*/", i + 2); i = j < 0 ? texto.length : j + 2; actual += " "; continue; }
    if (c === ";") { if (actual.trim()) completas.push(actual.trim()); actual = ""; i++; continue; }
    actual += c; i++;
  }
  return { completas, resto: actual };
}

export function opcionesPsql(args, entorno = {}) {
  const o = { host: entorno.PGHOST || "127.0.0.1", puerto: Number(entorno.PGPORT) || 5432, usuario: entorno.PGUSER || "postgres", clave: entorno.PGPASSWORD || "", base: entorno.PGDATABASE || null, comandos: [], archivo: null, pedirClave: false, expandido: false, sinAlinear: false, tuplas: false, ayuda: false, version: false };
  const posicionales = [];
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    const [k, v] = a.startsWith("--") && a.includes("=") ? [a.slice(0, a.indexOf("=")), a.slice(a.indexOf("=") + 1)] : [a, undefined];
    const sig = () => v ?? args[++i];
    if (k === "--help" || k === "-?") o.ayuda = true;
    else if (k === "-V" || k === "--version") o.version = true;
    else if (k === "-h" || k === "--host") o.host = sig();
    else if (k === "-p" || k === "--port") o.puerto = Number(sig());
    else if (k === "-U" || k === "--username") o.usuario = sig();
    else if (k === "-d" || k === "--dbname") posicionales.unshift(sig());
    else if (k === "-c" || k === "--command") o.comandos.push(sig());
    else if (k === "-f" || k === "--file") o.archivo = sig();
    else if (k === "-W" || k === "--password") o.pedirClave = true;
    else if (k === "-w" || k === "--no-password") { /* nada */ }
    else if (k === "-x" || k === "--expanded") o.expandido = true;
    else if (k === "-A" || k === "--no-align") o.sinAlinear = true;
    else if (k === "-t" || k === "--tuples-only") o.tuplas = true;
    else if (/^-[hpUdcf]./.test(a)) { args.splice(i + 1, 0, a.slice(2)); args[i] = a.slice(0, 2); i--; }
    else if (a.startsWith("-")) return { ...o, error: `psql: error: opción inválida «${a}»` };
    else posicionales.push(a);
  }
  const [primero, segundo] = posicionales;
  if (primero && /^postgres(ql)?:\/\//.test(primero)) {
    try {
      const u = new URL(primero.replace(/^postgres(ql)?:/, "http:"));
      o.host = decodeURIComponent(u.hostname || o.host).replace(/^\[|\]$/g, ""); o.puerto = Number(u.port) || o.puerto;
      if (u.username) o.usuario = decodeURIComponent(u.username);
      if (u.password) o.clave = decodeURIComponent(u.password);
      if (u.pathname.length > 1) o.base = decodeURIComponent(u.pathname.slice(1));
    } catch { return { ...o, error: "psql: error: la dirección postgresql:// no es válida" }; }
  } else {
    if (primero) o.base = primero;
    if (segundo) o.usuario = segundo;
  }
  if (!o.base) o.base = o.usuario;
  return o;
}

const AYUDA_PSQL = `psql es el cliente de PostgreSQL.
Uso: psql [-h HOST] [-p PUERTO] [-U USUARIO] [-d BASE] [-c "SQL"] [-f archivo.sql] [-W]
     psql postgresql://usuario:clave@localhost:5432/base
Dentro:  \\l bases · \\c base · \\dt tablas · \\d tabla · \\dn esquemas · \\du roles · \\x expandido · \\i archivo.sql · \\q salir
Termina cada sentencia con ;   Por defecto usuario postgres en 127.0.0.1:5432.
`;

const META_SQL = {
  l: "SELECT d.datname AS \"Name\", pg_catalog.pg_get_userbyid(d.datdba) AS \"Owner\", pg_catalog.pg_encoding_to_char(d.encoding) AS \"Encoding\" FROM pg_catalog.pg_database d WHERE NOT d.datistemplate ORDER BY 1",
  dt: "SELECT n.nspname AS \"Schema\", c.relname AS \"Name\", 'table' AS \"Type\", pg_catalog.pg_get_userbyid(c.relowner) AS \"Owner\" FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind IN ('r','p') AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_toast' ORDER BY 1,2",
  dv: "SELECT table_schema AS \"Schema\", table_name AS \"Name\", 'view' AS \"Type\" FROM information_schema.views WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2",
  dn: "SELECT n.nspname AS \"Name\", pg_catalog.pg_get_userbyid(n.nspowner) AS \"Owner\" FROM pg_catalog.pg_namespace n WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema' ORDER BY 1",
  du: "SELECT r.rolname AS \"Role name\", CASE WHEN r.rolsuper THEN 'Superuser' ELSE '' END AS \"Attributes\" FROM pg_catalog.pg_roles r WHERE r.rolname !~ '^pg_' ORDER BY 1",
  df: "SELECT n.nspname AS \"Schema\", p.proname AS \"Name\", pg_catalog.pg_get_function_result(p.oid) AS \"Result data type\" FROM pg_catalog.pg_proc p JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2",
  di: "SELECT schemaname AS \"Schema\", indexname AS \"Name\", tablename AS \"Table\" FROM pg_catalog.pg_indexes WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2",
};
const literalPg = (t) => `'${String(t).replace(/'/g, "''")}'`;

export async function comandoPsql(o) {
  const { out, err, cliente } = o;
  const op = opcionesPsql([...o.args], o.entorno || {});
  if (op.error) { err(`${op.error}\n`); return 2; }
  if (op.ayuda) { out(AYUDA_PSQL); return 0; }
  if (op.version) { out("psql (PostgreSQL) 16 — cliente de CódigoCamp\n"); return 0; }
  if (op.pedirClave) op.clave = (await o.leerLinea(`Password for user ${op.usuario}: `, { secreto: true })) ?? "";

  let sesion, base, version;
  const conectar = async (nuevaBase) => {
    const r = await cliente.pedir("conectar", { motor: "postgres", host: op.host, puerto: op.puerto, usuario: op.usuario, clave: op.clave, base: nuevaBase });
    if (sesion) { try { await cliente.pedir("cerrar", { sesion }); } catch { /* nada */ } }
    sesion = r.sesion; base = r.base; version = r.version;
  };
  try { await conectar(op.base); } catch (e) { err(`psql: error: ${e.message}\n`); return 2; }
  const interactivo = !op.comandos.length && !op.archivo && (o.entrada === null || o.entrada === undefined);
  if (interactivo) out(`psql (16, server ${version}) — cliente de CódigoCamp${cliente.puente() ? " · por el puente" : ""}\nType "help" for help.\n\n`);
  let expandido = op.expandido;

  const mostrar = (r) => {
    if (r.columnas) {
      if (op.tuplas || op.sinAlinear) { out(r.filas.map((f) => f.map(celda).join(op.sinAlinear ? "|" : " | ")).join("\n") + (r.filas.length ? "\n" : "")); return; }
      out(expandido && r.filas.length ? expandidoPsql(r.columnas, r.filas) : tablaPsql(r.columnas, r.filas));
      if (r.truncado) out(color.amarillo("(se muestran las primeras filas)\n"));
    } else if (r.comando) out(`${r.comando}\n`);
  };
  const sql = async (texto) => {
    try { const r = await cliente.pedir("consulta", { sesion, sql: texto }); mostrar(r); return true; }
    catch (e) { err(`${e.message}\n`); if (e.estado === 410) throw e; return false; }
  };
  const meta = async (linea) => {
    const [orden, ...args] = linea.slice(1).trim().split(/\s+/);
    const arg = args.join(" ");
    if (["q", "quit"].includes(orden)) return "salir";
    if (orden === "?" || orden === "h") { out(AYUDA_PSQL); return true; }
    if (orden === "x") { expandido = arg ? arg === "on" : !expandido; out(`Expanded display is ${expandido ? "on" : "off"}.\n`); return true; }
    if (orden === "c" || orden === "connect") {
      if (!arg) { out(`You are connected to database "${base}" as user "${op.usuario}" on host "${op.host}" at port "${op.puerto}".\n`); return true; }
      try { await conectar(arg.replace(/^"|"$/g, "")); out(`You are now connected to database "${base}" as user "${op.usuario}".\n`); return true; }
      catch (e) { err(`connection to server failed: ${e.message}\nPrevious connection kept\n`); return false; }
    }
    if (orden === "i" || orden === "ir") {
      let texto; try { texto = leerScript(o, arg); } catch (e) { err(`${e.message}\n`); return false; }
      return ejecutarTexto(texto);
    }
    if (orden === "conninfo") { out(`You are connected to database "${base}" as user "${op.usuario}" on host "${op.host}" at port "${op.puerto}".\n`); return true; }
    if (orden === "d" && arg) {
      const [esquema, tabla] = arg.includes(".") ? arg.split(".") : ["public", arg];
      return sql(`SELECT column_name AS "Column", data_type AS "Type", CASE WHEN is_nullable = 'NO' THEN 'not null' ELSE '' END AS "Nullable", COALESCE(column_default, '') AS "Default" FROM information_schema.columns WHERE table_schema = ${literalPg(esquema)} AND table_name = ${literalPg(tabla)} ORDER BY ordinal_position`);
    }
    const clave = orden.replace(/\+$/, "");
    if (META_SQL[clave === "d" ? "dt" : clave]) return sql(META_SQL[clave === "d" ? "dt" : clave]);
    err(`invalid command \\${orden}\nTry \\? for help.\n`);
    return false;
  };
  const ejecutarTexto = async (texto) => {
    let ok = true, buffer = "";
    for (const linea of texto.split("\n")) {
      if (!buffer.trim() && linea.trim().startsWith("\\")) { const r = await meta(linea.trim()); if (r === "salir") return true; ok = r && ok; continue; }
      buffer += linea + "\n";
      const { completas, resto } = partirPg(buffer);
      for (const s of completas) ok = (await sql(s)) && ok;
      buffer = resto;
    }
    if (buffer.trim()) ok = (await sql(buffer.trim())) && ok;
    return ok;
  };

  try {
    if (op.comandos.length) { let ok = true; for (const c of op.comandos) ok = (c.trim().startsWith("\\") ? (await meta(c.trim())) !== false : await ejecutarTexto(c)) && ok; return ok ? 0 : 1; }
    if (op.archivo) { let t; try { t = leerScript(o, op.archivo); } catch (e) { err(`psql: error: ${e.message}\n`); return 1; } return (await ejecutarTexto(t)) ? 0 : 3; }
    if (o.entrada !== null && o.entrada !== undefined) return (await ejecutarTexto(o.entrada)) ? 0 : 3;
    let buffer = "";
    for (;;) {
      const linea = await o.leerLinea(`${base}${buffer ? "-" : "="}# `, {});
      if (linea === null || linea === undefined) break;
      const t = linea.trim();
      if (!buffer && (t === "exit" || t === "quit")) break;
      if (!buffer && t === "help") { out(AYUDA_PSQL); continue; }
      if (!buffer.trim() && t.startsWith("\\")) { if ((await meta(t)) === "salir") break; continue; }
      buffer += linea + "\n";
      const { completas, resto } = partirPg(buffer);
      for (const s of completas) await sql(s);
      buffer = completas.length && !resto.trim() ? "" : resto;
    }
    return 0;
  } catch (e) { if (e.estado !== 410) err(`${e.message}\n`); return 2; }
  finally { try { await cliente.pedir("cerrar", { sesion }); } catch { /* ya cerrada */ } }
}

// ============================================================================= mongosh ====
/** Lee un literal de JavaScript al estilo de mongosh y lo convierte en Extended JSON. */
export function leerJs(texto) {
  let i = 0;
  const err = (m) => { throw new ErrorBD(`SyntaxError: ${m} (posición ${i + 1})`); };
  const blanco = () => { for (;;) { while (/\s/.test(texto[i] ?? "")) i++; if (texto.startsWith("//", i)) { while (i < texto.length && texto[i] !== "\n") i++; continue; } if (texto.startsWith("/*", i)) { const j = texto.indexOf("*/", i); i = j < 0 ? texto.length : j + 2; continue; } break; } };
  const cadena = () => {
    const q = texto[i++]; let s = "";
    while (i < texto.length && texto[i] !== q) {
      if (texto[i] === "\\") { const n = texto[++i]; s += { n: "\n", t: "\t", r: "\r", b: "\b", f: "\f", v: "\v", 0: "\0" }[n] ?? (n === "u" ? String.fromCharCode(parseInt(texto.slice(i + 1, (i += 4) + 1), 16)) : n); i++; }
      else s += texto[i++];
    }
    if (texto[i] !== q) err("cadena sin cerrar");
    i++; return s;
  };
  const ident = () => { const m = /^[A-Za-z_$][\w$]*/.exec(texto.slice(i)); if (!m) err("se esperaba un valor"); i += m[0].length; return m[0]; };
  const argumentos = () => { blanco(); if (texto[i] !== "(") err("se esperaba ("); i++; const a = []; blanco(); while (texto[i] !== ")") { a.push(valor()); blanco(); if (texto[i] === ",") { i++; blanco(); } else if (texto[i] !== ")") err("se esperaba , o )"); } i++; return a; };
  const valor = () => {
    blanco();
    const c = texto[i];
    if (c === "{") {
      i++; const obj = {}; blanco();
      while (texto[i] !== "}") {
        if (i >= texto.length) err("falta }");
        const k = texto[i] === "'" || texto[i] === '"' ? cadena() : /\d/.test(texto[i]) ? String(numero()) : ident();
        blanco(); if (texto[i] !== ":") err("se esperaba :"); i++;
        obj[k] = valor(); blanco();
        if (texto[i] === ",") { i++; blanco(); } else if (texto[i] !== "}") err("se esperaba , o }");
      }
      i++; return obj;
    }
    if (c === "[") { i++; const arr = []; blanco(); while (texto[i] !== "]") { if (i >= texto.length) err("falta ]"); arr.push(valor()); blanco(); if (texto[i] === ",") { i++; blanco(); } else if (texto[i] !== "]") err("se esperaba , o ]"); } i++; return arr; }
    if (c === "'" || c === '"' || c === "`") return cadena();
    if (c === "/") { const m = /^\/((?:\\.|[^/\\\n])+)\/([gimsuy]*)/.exec(texto.slice(i)); if (!m) err("expresión regular inválida"); i += m[0].length; return { $regex: m[1], $options: m[2] }; }
    if (/[-+\d.]/.test(c)) return numero();
    let nombre = ident();
    if (nombre === "new") { blanco(); nombre = ident(); }
    if (nombre === "true") return true;
    if (nombre === "false") return false;
    if (nombre === "null" || nombre === "undefined") return null;
    if (nombre === "Infinity") return { $numberDouble: "Infinity" };
    const a = argumentos();
    switch (nombre) {
      case "ObjectId": return a.length ? { $oid: String(a[0]) } : { $oid: nuevoObjectId() };
      case "ISODate": case "Date": return { $date: a.length ? new Date(a[0]).toISOString() : new Date().toISOString() };
      case "NumberDecimal": case "Decimal128": return { $numberDecimal: String(a[0]) };
      case "NumberLong": case "Long": return { $numberLong: String(a[0]) };
      case "NumberInt": case "Int32": return Number(a[0]) | 0;
      case "Double": return Number(a[0]);
      case "UUID": return { $uuid: String(a[0]) };
      case "RegExp": return { $regex: String(a[0]), $options: String(a[1] ?? "") };
      default: return err(`función desconocida ${nombre}()`);
    }
  };
  const numero = () => { const m = /^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?/.exec(texto.slice(i)); if (!m) err("número inválido"); i += m[0].length; return Number(m[0]); };
  const lista = () => argumentos();
  return { valor, lista, get pos() { return i; }, set pos(v) { i = v; }, blanco, ident, texto };
}

function nuevoObjectId() {
  const t = Math.floor(Date.now() / 1000).toString(16).padStart(8, "0");
  return t + [...crypto.getRandomValues(new Uint8Array(8))].map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** Analiza una orden de mongosh: db.col.metodo(args).sort(...).limit(n) … */
export function analizarMongo(linea) {
  const t = linea.trim().replace(/;\s*$/, "");
  let m;
  if ((m = /^show\s+(dbs|databases)$/i.exec(t))) return { op: "list_database_names", mostrar: "dbs" };
  if ((m = /^show\s+(collections|tables)$/i.exec(t))) return { op: "list_collection_names", mostrar: "lista" };
  if ((m = /^use\s+(\S+)$/i.exec(t))) return { op: "use", base: m[1] };
  if (t === "db") return { op: "db" };
  if (!t.startsWith("db.") && !t.startsWith("db[")) throw new ErrorBD(`ReferenceError: ${t.split(/[\s.(]/)[0]} is not defined (en esta consola solo funcionan show, use y db.<colección>.<método>())`);
  const p = leerJs(t);
  p.pos = 2;
  let coleccion = null, metodo = null;
  const sig = () => { p.blanco(); if (p.texto[p.pos] === "[") { p.pos++; const v = p.valor(); p.blanco(); p.pos++; return { nombre: String(v), llamada: false }; } if (p.texto[p.pos] !== ".") return null; p.pos++; const n = p.ident(); return { nombre: n }; };
  const primero = p.texto[p.pos] === "[" ? (p.pos++, (() => { const v = p.valor(); p.blanco(); p.pos++; return String(v); })()) : (p.pos++, p.ident());
  p.blanco();
  if (p.texto[p.pos] === "(") { metodo = primero; }
  else if (primero === "getCollection" || primero === "getSiblingDB") { /* no llega aquí */ }
  else coleccion = primero;
  let args = [];
  if (metodo) args = p.lista();
  else {
    const s = sig();
    if (!s) throw new ErrorBD(`Escribe un método: db.${coleccion}.find()`);
    metodo = s.nombre; args = p.lista();
  }
  if (metodo === "getCollection") { coleccion = String(args[0]); const s = sig(); metodo = s?.nombre; args = s ? p.lista() : []; if (!metodo) throw new ErrorBD("Escribe un método después de getCollection()"); }
  const cadena = [];
  for (;;) { const s = sig(); if (!s) break; cadena.push({ metodo: s.nombre, args: p.lista() }); }
  p.blanco();
  if (p.pos < p.texto.length) throw new ErrorBD(`SyntaxError: sobra «${p.texto.slice(p.pos, p.pos + 20)}»`);
  return traducirMongo(coleccion, metodo, args, cadena);
}

const CAMEL = { findOne: "find_one", insertOne: "insert_one", insertMany: "insert_many", updateOne: "update_one", updateMany: "update_many", replaceOne: "replace_one", deleteOne: "delete_one", deleteMany: "delete_many", countDocuments: "count_documents", estimatedDocumentCount: "estimated_document_count", createIndex: "create_index", dropIndex: "drop_index", dropIndexes: "drop_indexes", getIndexes: "list_indexes", findOneAndUpdate: "find_one_and_update", findOneAndDelete: "find_one_and_delete", findOneAndReplace: "find_one_and_replace", renameCollection: "rename", aggregate: "aggregate", distinct: "distinct", drop: "drop", find: "find" };
const OPC_ESCRITURA = (o = {}) => { const k = {}; if (o.upsert !== undefined) k.upsert = Boolean(o.upsert); if (o.arrayFilters) k.array_filters = o.arrayFilters; if (o.projection) k.projection = o.projection; if (o.sort) k.sort = Object.entries(o.sort); if (o.returnDocument) k.return_document = o.returnDocument === "after"; if (o.unique !== undefined) k.unique = Boolean(o.unique); if (o.name) k.name = o.name; return k; };

function traducirMongo(coleccion, metodo, args, cadena) {
  if (!coleccion) {
    const base = { dropDatabase: "drop_database", getCollectionNames: "list_collection_names", createCollection: "create_collection", stats: "stats" }[metodo];
    if (!base) throw new ErrorBD(`TypeError: db.${metodo} is not a function`);
    return { op: base, args: metodo === "createCollection" ? [String(args[0])] : [], mostrar: metodo === "getCollectionNames" ? "valor" : undefined };
  }
  let op = CAMEL[metodo] ?? (metodo === "count" ? "count_documents" : metodo === "insert" ? (Array.isArray(args[0]) ? "insert_many" : "insert_one") : metodo === "remove" ? "delete_many" : metodo === "update" ? "update_one" : null);
  if (!op) throw new ErrorBD(`TypeError: db.${coleccion}.${metodo} is not a function`);
  const r = { op, coleccion, args: [], opciones: {} };
  if (op === "find" || op === "find_one") { r.args = [args[0] ?? {}, ...(args[1] ? [args[1]] : [])]; }
  else if (op === "count_documents") r.args = [args[0] ?? {}];
  else if (op === "create_index") { r.args = [Object.entries(args[0] ?? {})]; Object.assign(r.opciones, OPC_ESCRITURA(args[1])); }
  else if (["update_one", "update_many", "replace_one", "find_one_and_update", "find_one_and_replace"].includes(op)) { r.args = [args[0] ?? {}, args[1] ?? {}]; Object.assign(r.opciones, OPC_ESCRITURA(args[2])); }
  else if (op === "find_one_and_delete") { r.args = [args[0] ?? {}]; Object.assign(r.opciones, OPC_ESCRITURA(args[1])); }
  else if (op === "distinct") r.args = [String(args[0]), ...(args[1] ? [args[1]] : [])];
  else if (op === "aggregate") r.args = [args[0] ?? []];
  else if (op === "rename") r.args = [String(args[0])];
  else r.args = args;
  for (const c of cadena) {
    if (c.metodo === "sort") r.opciones.sort = c.args[0];
    else if (c.metodo === "limit") r.opciones.limit = Number(c.args[0]);
    else if (c.metodo === "skip") r.opciones.skip = Number(c.args[0]);
    else if (c.metodo === "count" || c.metodo === "countDocuments") { r.op = "count_documents"; r.args = [r.args[0] ?? {}]; r.opciones = {}; }
    else if (c.metodo === "projection") r.args[1] = c.args[0];
    else if (["pretty", "toArray", "batchSize", "hint", "explain"].includes(c.metodo)) { /* sin efecto */ }
    else throw new ErrorBD(`TypeError: ${c.metodo} is not a function`);
  }
  return r;
}

// Formato de mongosh: { _id: ObjectId('…'), nombre: 'Ana' }
const claveJs = (k) => /^[A-Za-z_$][\w$]*$/.test(k) ? k : `'${k.replace(/'/g, "\\'")}'`;
export function formatoMongo(v, sangria = 0) {
  const esp = "  ".repeat(sangria + 1), fin = "  ".repeat(sangria);
  if (v === null) return "null";
  if (typeof v === "string") return `'${v.replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, "\\n")}'`;
  if (typeof v !== "object") return String(v);
  if (Array.isArray(v)) {
    if (!v.length) return "[]";
    const partes = v.map((x) => formatoMongo(x, sangria + 1));
    const linea = `[ ${partes.join(", ")} ]`;
    return linea.length <= 72 && !linea.includes("\n") ? linea : `[\n${partes.map((x) => esp + x).join(",\n")}\n${fin}]`;
  }
  const k = Object.keys(v);
  if (k.length === 1) {
    if (k[0] === "$oid") return `ObjectId('${v.$oid}')`;
    if (k[0] === "$date") return `ISODate('${typeof v.$date === "string" ? v.$date : v.$date?.$numberLong ? new Date(Number(v.$date.$numberLong)).toISOString() : v.$date}')`;
    if (k[0] === "$numberDecimal") return `Decimal128('${v.$numberDecimal}')`;
    if (k[0] === "$numberLong") return `Long('${v.$numberLong}')`;
    if (k[0] === "$numberDouble") return v.$numberDouble;
    if (k[0] === "$uuid") return `UUID('${v.$uuid}')`;
  }
  if (k.length === 2 && v.$regularExpression) return `/${v.$regularExpression.pattern}/${v.$regularExpression.options}`;
  if (!k.length) return "{}";
  const partes = k.map((c) => `${claveJs(c)}: ${formatoMongo(v[c], sangria + 1)}`);
  const linea = `{ ${partes.join(", ")} }`;
  return linea.length <= 72 && !linea.includes("\n") ? linea : `{\n${partes.map((x) => esp + x).join(",\n")}\n${fin}}`;
}

export function opcionesMongo(args) {
  const o = { uri: null, host: "127.0.0.1", puerto: 27017, usuario: null, clave: null, authDb: null, base: null, eval: null, archivos: [], quiet: false, ayuda: false, version: false, pedirClave: false };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    const [k, v] = a.startsWith("--") && a.includes("=") ? [a.slice(0, a.indexOf("=")), a.slice(a.indexOf("=") + 1)] : [a, undefined];
    const sig = () => v ?? args[++i];
    if (k === "--help" || k === "-h") o.ayuda = true;
    else if (k === "--version") o.version = true;
    else if (k === "--host") o.host = sig();
    else if (k === "--port") o.puerto = Number(sig());
    else if (k === "-u" || k === "--username") o.usuario = sig();
    else if (k === "-p" || k === "--password") { const s = v ?? (args[i + 1] && !args[i + 1].startsWith("-") ? args[++i] : undefined); if (s === undefined) o.pedirClave = true; else o.clave = s; }
    else if (k === "--authenticationDatabase") o.authDb = sig();
    else if (k === "--eval") o.eval = sig();
    else if (k === "--quiet" || k === "--nodb" || k === "--norc") o.quiet = true;
    else if (a.startsWith("-")) return { ...o, error: `MongoshInvalidInputError: opción desconocida ${a}` };
    else if (/^mongodb(\+srv)?:\/\//.test(a)) o.uri = a;
    else if (/\.js$/.test(a)) o.archivos.push(a);
    else if (/^[\w.-]+:\d+\/\w+$/.test(a)) { const [hp, b] = a.split("/"); const [h, p] = hp.split(":"); Object.assign(o, { host: h, puerto: Number(p), base: b }); }
    else o.base = a;
  }
  return o;
}

const AYUDA_MONGO = `mongosh — consola de MongoDB (cliente de CódigoCamp)
Uso: mongosh                              (mongodb://127.0.0.1:27017/test)
     mongosh "mongodb://localhost:27017/finanbot"     mongosh finanbot
     mongosh --host H --port P -u usuario -p clave --authenticationDatabase admin
     mongosh finanbot --eval "db.usuarios.find()"     mongosh finanbot script.js
Dentro: show dbs · use base · show collections · db.col.find({ edad: { $gt: 18 } }).sort({ nombre: 1 }).limit(5)
        insertOne/insertMany · updateOne/updateMany · deleteOne/deleteMany · countDocuments · aggregate([...]) · distinct
        createIndex · getIndexes · drop · db.dropDatabase() · exit
`;

const equilibrado = (t) => {
  let n = 0, q = null;
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (q) { if (c === "\\") i++; else if (c === q) q = null; continue; }
    if (c === "'" || c === '"' || c === "`") q = c;
    else if ("({[".includes(c)) n++;
    else if (")}]".includes(c)) n--;
  }
  return n <= 0 && !q;
};

export async function comandoMongo(o) {
  const { out, err, cliente } = o;
  const op = opcionesMongo(o.args);
  if (op.error) { err(`${op.error}\n`); return 1; }
  if (op.ayuda) { out(AYUDA_MONGO); return 0; }
  if (op.version) { out("2.3.0 (cliente de CódigoCamp)\n"); return 0; }
  if (op.pedirClave) op.clave = (await o.leerLinea("Enter password: ", { secreto: true })) ?? "";
  let uri = op.uri;
  if (!uri) {
    const auth = op.usuario ? `${encodeURIComponent(op.usuario)}:${encodeURIComponent(op.clave ?? "")}@` : "";
    uri = `mongodb://${auth}${op.host.includes(":") ? `[${op.host}]` : op.host}:${op.puerto}/${op.base ?? "test"}${op.usuario ? `?authSource=${encodeURIComponent(op.authDb || "admin")}` : ""}`;
  }
  let sesion, base;
  try {
    const r = await cliente.pedir("conectar", { motor: "mongodb", uri, base: op.uri ? op.base : null });
    sesion = r.sesion; base = r.base;
    if (!op.eval && !op.archivos.length && o.entrada == null && !op.quiet) out(`Current Mongosh Log ID: ${nuevoObjectId()}\nConnecting to:\t\t${color.verde(uri.replace(/\/\/[^@/]*@/, "//<credenciales>@"))}\nUsing MongoDB:\t\t${r.version}\nUsing Mongosh:\t\t2.3.0 (CódigoCamp${cliente.puente() ? " · puente" : ""})\n\n`);
  } catch (e) { err(`MongoNetworkError: ${e.message}\n`); return 1; }

  const una = async (texto) => {
    const t = texto.trim().replace(/;\s*$/, "");
    if (!t) return true;
    if (/^(exit|quit)(\(\))?$/.test(t)) return "salir";
    if (/^help(\(\))?$/.test(t)) { out(AYUDA_MONGO); return true; }
    if (/^(it|print\(.*\))$/.test(t)) { out(color.gris(t === "it" ? "no hay más resultados\n" : `${t.slice(6, -1)}\n`)); return true; }
    let orden;
    try { orden = analizarMongo(t); } catch (e) { err(`${color.rojo(e.message)}\n`); return false; }
    if (orden.op === "db") { out(`${base}\n`); return true; }
    try {
      const r = await cliente.pedir("consulta", { sesion, base: orden.base ?? base, operacion: orden.op, coleccion: orden.coleccion, args: orden.args ?? [], opciones: orden.opciones ?? {} });
      base = r.base ?? base;
      const v = r.resultado;
      if (orden.op === "use") out(`${v}\n`);
      else if (orden.mostrar === "dbs") out(v.map((n) => n).join("\n") + "\n");
      else if (orden.mostrar === "lista") out(v.length ? v.join("\n") + "\n" : "");
      else if (orden.op === "drop") out(`${v}\n`);
      else if (Array.isArray(v) && orden.op === "find" && v.length === 0) { /* mongosh no muestra nada */ }
      else out(`${formatoMongo(v)}\n`);
      return true;
    } catch (e) { err(`${color.rojo(e.message)}\n`); if (e.estado === 410) throw e; return false; }
  };
  const ejecutarTexto = async (texto) => {
    let ok = true, buffer = "";
    for (const linea of texto.split("\n")) {
      buffer += (buffer ? "\n" : "") + linea;
      if (!equilibrado(buffer)) continue;
      for (const parte of buffer.split(/;\s*(?=\S)/)) { const r = await una(parte); if (r === "salir") return ok; ok = r && ok; }
      buffer = "";
    }
    if (buffer.trim()) ok = (await una(buffer)) && ok;
    return ok;
  };
  try {
    if (op.eval !== null) return (await ejecutarTexto(op.eval)) ? 0 : 1;
    if (op.archivos.length) { let ok = true; for (const a of op.archivos) { try { ok = (await ejecutarTexto(leerScript(o, a))) && ok; } catch (e) { err(`${e.message}\n`); ok = false; } } return ok ? 0 : 1; }
    if (o.entrada !== null && o.entrada !== undefined) return (await ejecutarTexto(o.entrada)) ? 0 : 1;
    let buffer = "";
    for (;;) {
      const linea = await o.leerLinea(buffer ? "... " : `${base}> `, {});
      if (linea === null || linea === undefined) break;
      buffer += (buffer ? "\n" : "") + linea;
      if (!equilibrado(buffer)) continue;
      const r = await una(buffer);
      buffer = "";
      if (r === "salir") break;
    }
    return 0;
  } catch (e) { if (e.estado !== 410) err(`${e.message}\n`); return 1; }
  finally { try { await cliente.pedir("cerrar", { sesion }); } catch { /* ya cerrada */ } }
}

// =========================================================================== redis-cli ====
/** Parte una línea de redis-cli en argumentos ("con espacios", 'así', \x00). */
export function argumentosRedis(linea) {
  const args = []; let i = 0;
  while (i < linea.length) {
    while (linea[i] === " " || linea[i] === "\t") i++;
    if (i >= linea.length) break;
    let a = "";
    if (linea[i] === '"' || linea[i] === "'") {
      const q = linea[i++];
      while (i < linea.length && linea[i] !== q) {
        if (linea[i] === "\\" && q === '"') { const n = linea[++i]; if (n === "x") { a += String.fromCharCode(parseInt(linea.slice(i + 1, i + 3), 16)); i += 3; continue; } a += { n: "\n", r: "\r", t: "\t", b: "\b", a: "\x07" }[n] ?? n; i++; }
        else a += linea[i++];
      }
      if (linea[i] !== q) throw new ErrorBD("Invalid argument(s)");
      i++;
    } else while (i < linea.length && linea[i] !== " " && linea[i] !== "\t") a += linea[i++];
    args.push(a);
  }
  return args;
}

const ESTADO_REDIS = new Set(["OK", "PONG", "QUEUED"]);
export function formatoRedis(v, nivel = 0) {
  if (v === null || v === undefined) return "(nil)";
  if (typeof v === "number") return `(integer) ${v}`;
  if (typeof v === "object" && v.$bytes !== undefined) return `"${v.$bytes.replace(/../g, (h) => `\\x${h}`)}"`;
  if (Array.isArray(v)) {
    if (!v.length) return "(empty array)";
    const ancho = String(v.length).length;
    return v.map((x, i) => `${" ".repeat(i ? nivel * (ancho + 2) : 0)}${String(i + 1).padStart(ancho)}) ${formatoRedis(x, nivel + 1)}`).join("\n");
  }
  if (ESTADO_REDIS.has(v)) return v;
  return JSON.stringify(String(v)).replace(/\\u00([0-9a-f]{2})/g, "\\x$1");
}

export async function comandoRedis(o) {
  const { out, err, cliente } = o;
  const op = { host: "127.0.0.1", puerto: 6379, clave: "", usuario: null, base: 0 };
  const resto = [];
  const a = o.args;
  for (let i = 0; i < a.length; i++) {
    if (a[i] === "-h") op.host = a[++i];
    else if (a[i] === "-p") op.puerto = Number(a[++i]);
    else if (a[i] === "-a" || a[i] === "--pass") op.clave = a[++i];
    else if (a[i] === "--user") op.usuario = a[++i];
    else if (a[i] === "-n") op.base = Number(a[++i]);
    else if (a[i] === "-u") { try { const u = new URL(a[++i].replace(/^rediss?:/, "http:")); op.host = u.hostname; op.puerto = Number(u.port) || 6379; op.clave = decodeURIComponent(u.password || ""); op.usuario = u.username ? decodeURIComponent(u.username) : null; op.base = Number(u.pathname.slice(1)) || 0; } catch { err("Invalid URI\n"); return 1; } }
    else if (a[i] === "--version" || a[i] === "-v") { out("redis-cli 7 (cliente de CódigoCamp)\n"); return 0; }
    else if (a[i] === "--help") { out("Uso: redis-cli [-h host] [-p puerto] [-a clave] [-n base] [comando [args…]]\nSin comando abre la consola. Ej.: redis-cli SET saludo hola · redis-cli GET saludo\n"); return 0; }
    else if (a[i] === "--no-auth-warning" || a[i] === "--raw") { /* nada */ }
    else { resto.push(...a.slice(i)); break; }
  }
  let sesion, base = String(op.base);
  try { const r = await cliente.pedir("conectar", { motor: "redis", host: op.host, puerto: op.puerto, usuario: op.usuario, clave: op.clave, base: op.base }); sesion = r.sesion; }
  catch (e) { err(`Could not connect to Redis at ${op.host}:${op.puerto}: ${e.message}\n`); return 1; }
  const ejecutar = async (args) => {
    try { const r = await cliente.pedir("consulta", { sesion, comando: args }); base = r.base ?? base; out(`${formatoRedis(r.resultado)}\n`); return true; }
    catch (e) { out(`${e.message}\n`); if (e.estado === 410) throw e; return false; }
  };
  const prompt = () => `${op.host}:${op.puerto}${base !== "0" ? `[${base}]` : ""}> `;
  try {
    if (resto.length) return (await ejecutar(resto)) ? 0 : 1;
    if (o.entrada !== null && o.entrada !== undefined) { let ok = true; for (const l of o.entrada.split("\n")) { if (!l.trim()) continue; ok = (await ejecutar(argumentosRedis(l))) && ok; } return ok ? 0 : 1; }
    for (;;) {
      const linea = await o.leerLinea(prompt(), {});
      if (linea === null || linea === undefined) break;
      let args;
      try { args = argumentosRedis(linea); } catch (e) { out(`${e.message}\n`); continue; }
      if (!args.length) continue;
      if (/^(exit|quit)$/i.test(args[0])) break;
      if (/^help$/i.test(args[0])) { out("Escribe comandos de Redis: SET clave valor · GET clave · KEYS * · HSET h campo valor · HGETALL h · LPUSH l a · LRANGE l 0 -1 · DEL clave · exit\n"); continue; }
      if (/^clear$/i.test(args[0])) continue;
      await ejecutar(args);
    }
    return 0;
  } catch (e) { if (e.estado !== 410) err(`${e.message}\n`); return 1; }
  finally { try { await cliente.pedir("cerrar", { sesion }); } catch { /* ya cerrada */ } }
}
