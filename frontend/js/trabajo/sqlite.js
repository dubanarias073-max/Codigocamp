// sqlite3 en la terminal, como el de verdad (motor: sql.js, SQLite compilado a WebAssembly).
//
//   sqlite3 tienda.db                     abre (o crea) la base y entra a la consola  sqlite>
//   sqlite3 tienda.db "SELECT * FROM t"   ejecuta y sale
//   sqlite3 tienda.db < esquema.sql       ejecuta un script (también: .read esquema.sql)
//   sqlite3 script.sql                    ejecuta el script en una base temporal (como antes)
//
// La base .db es un archivo del proyecto guardado en tu cuenta: los cambios se guardan al momento, la puedes
// descargar, abrir con DB Browser for SQLite o usar desde Python (import sqlite3).
import { color } from "./ansi.js";
import { esMarcador } from "./archivos.js";
import * as FS from "./fs.js";

const MODIFICA = /^\s*(create|insert|update|delete|drop|alter|replace|vacuum|reindex|attach|detach|pragma\s+\w+\s*=|begin|commit|rollback|savepoint|release)\b/i;
export const EXT_BASE = new Set(["db", "sqlite", "sqlite3", "db3"]);

const texto = (v) => (v === null ? "NULL" : v instanceof Uint8Array ? `<blob ${v.length} B>` : String(v));
const ancho = (s) => [...s].length;

/** Resultado como tabla: modos table (+--+), box (┌─┐), column, list (a|b), csv, markdown, json. */
export function formatear(columnas, filas, { modo = "table", encabezados = true } = {}) {
  const celdas = filas.map((f) => f.map(texto));
  if (modo === "json") return JSON.stringify(filas.map((f) => Object.fromEntries(columnas.map((c, i) => [c, f[i] instanceof Uint8Array ? texto(f[i]) : f[i]]))), null, 1) + "\n";
  if (modo === "csv") {
    const q = (s) => (/[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);
    return [...(encabezados ? [columnas.map(q).join(",")] : []), ...celdas.map((f) => f.map(q).join(","))].join("\n") + "\n";
  }
  if (modo === "list") return [...(encabezados ? [columnas.join("|")] : []), ...celdas.map((f) => f.join("|"))].join("\n") + "\n";
  const w = columnas.map((c, i) => Math.max(encabezados ? ancho(c) : 0, ...celdas.map((f) => ancho(f[i])), 1));
  const pad = (s, i) => s + " ".repeat(w[i] - ancho(s));
  const numerica = columnas.map((_, i) => filas.length > 0 && filas.every((f) => f[i] === null || typeof f[i] === "number"));
  const celda = (s, i) => (numerica[i] ? " ".repeat(w[i] - ancho(s)) + s : pad(s, i));
  if (modo === "markdown") {
    return [`| ${columnas.map(pad).join(" | ")} |`, `|${w.map((n, i) => (numerica[i] ? "-".repeat(n + 1) + ":" : "-".repeat(n + 2))).join("|")}|`, ...celdas.map((f) => `| ${f.map(celda).join(" | ")} |`)].join("\n") + "\n";
  }
  if (modo === "column") return [...(encabezados ? [columnas.map(pad).join("  "), w.map((n) => "-".repeat(n)).join("  ")] : []), ...celdas.map((f) => f.map(celda).join("  "))].join("\n") + "\n";
  const [h, v, a, b, c, d, e, f2, g] = modo === "box" ? ["─", "│", "┌", "┬", "┐", "├", "┼", "┤", "└┴┘"] : ["-", "|", "+", "+", "+", "+", "+", "+", "+++"];
  const linea = (i, m, fin) => i + w.map((n) => h.repeat(n + 2)).join(m) + fin;
  return [linea(a, b, c), ...(encabezados ? [`${v} ${columnas.map(pad).join(` ${v} `)} ${v}`, linea(d, e, f2)] : []), ...celdas.map((fila) => `${v} ${fila.map(celda).join(` ${v} `)} ${v}`),
    linea(g[0], g[1], g[2])].join("\n") + "\n";
}

/** Divide un script en sentencias completas (respeta comillas, comentarios y BEGIN…END de triggers). */
export function sentencias(sql) {
  const salida = [];
  let actual = "";
  let comilla = null;
  let profundidad = 0;
  for (let i = 0; i < sql.length; i += 1) {
    const ch = sql[i];
    if (comilla) { actual += ch; if (ch === comilla) comilla = null; continue; }
    if (ch === "-" && sql[i + 1] === "-") { const fin = sql.indexOf("\n", i); i = fin < 0 ? sql.length : fin; actual += "\n"; continue; }
    if (ch === "/" && sql[i + 1] === "*") { const fin = sql.indexOf("*/", i + 2); i = fin < 0 ? sql.length : fin + 1; continue; }
    if (ch === "'" || ch === '"' || ch === "`") { comilla = ch; actual += ch; continue; }
    actual += ch;
    if (/\bBEGIN\s*$/i.test(actual) && /CREATE\s+TRIGGER/i.test(actual)) profundidad += 1;
    if (/\bEND\s*$/i.test(actual) && profundidad) profundidad -= 1;
    if (ch === ";" && !profundidad) { if (actual.trim() !== ";") salida.push(actual.trim()); actual = ""; }
  }
  return { completas: salida, resto: actual.trim() };
}

/**
 * Ejecuta el comando sqlite3.
 * @param {object} o  { args, py, cwd, out, err, leerLinea, entrada, SQL, leerArchivo(marcador)→Uint8Array, subirArchivo(bytes,{nombre})→marcador, cambio() }
 */
export async function comandoSqlite(o) {
  const { args, py, cwd, out, err, SQL } = o;
  const posicionales = args.filter((x) => !x.startsWith("-"));
  const estado = { modo: args.includes("-csv") ? "csv" : args.includes("-json") ? "json" : args.includes("-box") ? "box" : args.includes("-line") || args.includes("-list") ? "list" : "table", encabezados: !args.includes("-noheader") };
  const [primero, ...extra] = posicionales;
  let ruta = null;
  let db;
  if (primero) {
    ruta = FS.resolver(cwd, primero);
    if (ruta === null || ruta === "") { err(`Error: no se puede abrir «${primero}»\n`); return 1; }
    const actual = py.files[ruta];
    if (FS.extension(ruta) === "sql" && typeof actual === "string" && !esMarcador(actual)) {
      // Compatibilidad: «sqlite3 script.sql» ejecuta el script en una base temporal.
      db = new SQL.Database();
      try { return ejecutar(db, actual, estado, o) ? 0 : 1; } finally { db.close(); }
    }
    if (FS.esCarpeta(py, ruta)) { err(`Error: «${primero}» es una carpeta\n`); return 1; }
    if (actual !== undefined && !esMarcador(actual)) {
      if (actual.length) { err(`Error: «${primero}» no es una base de datos SQLite (es un archivo de texto). Para ejecutar un script: sqlite3 base.db < ${primero}\n`); return 1; }
    }
    try {
      db = esMarcador(actual) ? new SQL.Database(await o.leerArchivo(actual)) : new SQL.Database();
      db.exec("SELECT count(*) FROM sqlite_master");
    } catch (e) { err(`Error: «${primero}» no es una base de datos SQLite (${e.message})\n`); db?.close(); return 1; }
  } else db = new SQL.Database();

  let pendiente = false;
  const guardar = async () => {
    if (!ruta || !pendiente) return true;
    if (!o.subirArchivo) { err("Error: no se pudo guardar la base (sin sesión).\n"); return false; }
    try {
      const marcador = await o.subirArchivo(db.export(), { nombre: ruta });
      const r = FS.tieneArchivo(py, ruta) ? FS.escribirArchivo(py, ruta, marcador) : FS.crearArchivo(py, ruta, marcador, { padres: true });
      if (!r.ok) { err(`Error al guardar ${ruta}: ${r.error}\n`); return false; }
      pendiente = false;
      o.cambio?.();
      return true;
    } catch (e) { err(`Error al guardar ${ruta}: ${e.message}\n`); return false; }
  };
  const correr = async (sql) => { const ok = ejecutar(db, sql, estado, o, () => { pendiente = true; }); await guardar(); return ok; };

  try {
    if (extra.length) { let ok = true; for (const x of extra) ok = (await correr(x)) && ok; return ok ? 0 : 1; }
    if (o.entrada !== null && o.entrada !== undefined) return (await correr(o.entrada)) ? 0 : 1;
    // Consola interactiva
    out(`SQLite version 3 (sql.js) · ${ruta ? `base: ${ruta}${esMarcador(py.files[ruta] ?? "") ? "" : " (nueva)"}` : "base temporal en memoria"}\nEscribe ${color.amarillo(".help")} para ver los comandos y ${color.amarillo(".quit")} para salir. Termina cada sentencia con ;\n`);
    let buffer = "";
    for (;;) {
      const linea = await o.leerLinea(buffer ? "   ...> " : "sqlite> ", {});
      if (linea === null || linea === undefined) break;
      if (!buffer && linea.trim().startsWith(".")) {
        if (/^\.(quit|exit|q)\b/.test(linea.trim())) break;
        await correr(linea.trim());
        continue;
      }
      buffer += (buffer ? "\n" : "") + linea;
      const { completas, resto } = sentencias(buffer);
      if (completas.length) { await correr(completas.join("\n")); buffer = resto; }
    }
    return 0;
  } finally {
    await guardar();
    db.close();
  }
}

/** Ejecuta SQL o un comando punto. Devuelve true si no hubo errores. */
function ejecutar(db, entrada, estado, o, alModificar = () => {}) {
  const { out, err, py, cwd } = o;
  const t = entrada.trim();
  if (t.startsWith(".")) return punto(db, t, estado, o, alModificar);
  const { completas, resto } = sentencias(t);
  const lista = [...completas, ...(resto ? [resto] : [])];
  for (const s of lista) {
    if (s.startsWith(".")) { if (!punto(db, s, estado, o, alModificar)) return false; continue; }
    try {
      const antes = db.exec("SELECT total_changes()")[0].values[0][0];
      const rs = db.exec(s);
      const despues = db.exec("SELECT total_changes()")[0].values[0][0];
      if (despues !== antes || MODIFICA.test(s)) alModificar();
      for (const r of rs) out(formatear(r.columns, r.values, estado));
    } catch (e) {
      err(`${color.rojo("Error:")} ${e.message}\n`);
      return false;
    }
  }
  void py; void cwd;
  return true;
}

function punto(db, linea, estado, o, alModificar) {
  const { out, err, py, cwd } = o;
  const [cmd, ...a] = linea.split(/\s+/);
  const unaCol = (sql) => db.exec(sql)[0]?.values.map((v) => v[0]) ?? [];
  switch (cmd) {
    case ".help":
      out([".tables [patrón]      lista las tablas", ".schema [tabla]      muestra el CREATE de las tablas", ".indexes [tabla]     lista los índices",
        ".mode MODO           table, box, column, list, csv, markdown, json", ".headers on|off      encabezados de columna", ".read archivo.sql    ejecuta un script del proyecto",
        ".dump [tabla]        copia de la base como SQL", ".databases           bases abiertas", ".quit                salir"].join("\n") + "\n");
      return true;
    case ".tables": {
      const nombres = unaCol(`SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ${a[0] ? `AND name LIKE '${a[0].replace(/'/g, "''")}'` : ""} ORDER BY name`);
      out(nombres.length ? nombres.join("  ") + "\n" : "");
      return true;
    }
    case ".schema": {
      const sqls = unaCol(`SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ${a[0] ? `AND tbl_name = '${a[0].replace(/'/g, "''")}'` : ""} ORDER BY type DESC, name`);
      out(sqls.map((x) => `${x};`).join("\n") + (sqls.length ? "\n" : ""));
      return true;
    }
    case ".indexes": case ".indices":
      out(unaCol(`SELECT name FROM sqlite_master WHERE type = 'index' ${a[0] ? `AND tbl_name = '${a[0].replace(/'/g, "''")}'` : ""}`).join("  ") + "\n");
      return true;
    case ".mode":
      if (!["table", "box", "column", "list", "csv", "markdown", "json"].includes(a[0])) { err("Modos: table, box, column, list, csv, markdown, json\n"); return false; }
      estado.modo = a[0];
      return true;
    case ".headers": estado.encabezados = a[0] !== "off"; return true;
    case ".databases": out("main: " + (o.ruta || "(memoria)") + "\n"); return true;
    case ".read": {
      const r = FS.resolver(cwd, a.join(" ").replace(/^["']|["']$/g, ""));
      if (r === null || !FS.tieneArchivo(py, r) || esMarcador(py.files[r])) { err(`Error: no se puede abrir «${a.join(" ")}»\n`); return false; }
      return ejecutar(db, py.files[r], estado, o, alModificar);
    }
    case ".dump": {
      const tablas = db.exec(`SELECT name, sql FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ${a[0] ? `AND name = '${a[0].replace(/'/g, "''")}'` : ""}`)[0]?.values ?? [];
      const lineas = ["PRAGMA foreign_keys=OFF;", "BEGIN TRANSACTION;"];
      for (const [nombre, sql] of tablas) {
        lineas.push(`${sql};`);
        const r = db.exec(`SELECT * FROM "${nombre.replace(/"/g, '""')}"`)[0];
        for (const f of r?.values ?? []) lineas.push(`INSERT INTO "${nombre}" VALUES(${f.map((v) => (v === null ? "NULL" : typeof v === "number" ? v : v instanceof Uint8Array ? `X'${[...v].map((b) => b.toString(16).padStart(2, "0")).join("")}'` : `'${String(v).replace(/'/g, "''")}'`)).join(",")});`);
      }
      for (const [sql] of db.exec("SELECT sql FROM sqlite_master WHERE type IN ('index','trigger','view') AND sql IS NOT NULL")[0]?.values ?? []) lineas.push(`${sql};`);
      lineas.push("COMMIT;");
      out(lineas.join("\n") + "\n");
      return true;
    }
    default:
      err(`Error: comando desconocido «${cmd}». Escribe .help\n`);
      return false;
  }
}
