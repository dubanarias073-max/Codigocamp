// Bases de datos del usuario (MySQL/MariaDB, p. ej. el de XAMPP) desde Trabajo.
//
// Dos caminos, con la misma API (/api/bd/estado, conectar, consulta, cerrar):
//   · servidor: CódigoCamp corre en el mismo PC que XAMPP → el servidor conecta a localhost:3306.
//   · puente:   CódigoCamp está en internet → el usuario abre backend/herramientas/puente_bd.py en su PC
//               y lo configura una vez con «bd-puente http://127.0.0.1:8787 <clave>».
//
// Lo usan el comando `mysql` de la terminal y los módulos pymysql / mysql.connector de Python (pedirSync).
import { color } from "./ansi.js";
import * as FS from "./fs.js";
import { leerMarcador } from "./archivos.js";

const CLAVE_PUENTE = "cc-bd-puente";
const csrf = () => (globalThis.document?.cookie?.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";

export class ErrorBD extends Error {
  constructor(mensaje, { codigo = null, estado = 0 } = {}) { super(mensaje); this.codigo = codigo; this.estado = estado; }
}

export class ClienteBD {
  constructor({ fetchFn = (...a) => fetch(...a), almacen = globalThis.localStorage ?? null, base = "", XHR = globalThis.XMLHttpRequest } = {}) {
    this.fetchFn = fetchFn; this.almacen = almacen; this.base = base; this.XHR = XHR;
  }

  // ---- puente ----
  puente() {
    try { const p = JSON.parse(this.almacen?.getItem(CLAVE_PUENTE) || "null"); return p?.url && p?.clave ? p : null; } catch { return null; }
  }
  configurarPuente(url, clave) {
    let u;
    try { u = new URL(url); } catch { throw new ErrorBD("La dirección del puente no es válida (ej.: http://127.0.0.1:8787)."); }
    if (!/^https?:$/.test(u.protocol)) throw new ErrorBD("El puente debe ser http:// o https://.");
    const p = { url: u.origin, clave: String(clave || "").trim() };
    if (!p.clave) throw new ErrorBD("Falta la clave que muestra el puente al abrirlo.");
    try { this.almacen?.setItem(CLAVE_PUENTE, JSON.stringify(p)); } catch { /* sin almacenamiento: dura esta pestaña */ this._puente = p; }
    return p;
  }
  quitarPuente() { try { this.almacen?.removeItem(CLAVE_PUENTE); } catch { /* nada */ } this._puente = null; }

  _destino() {
    const p = this.puente() ?? this._puente ?? null;
    if (p) return { url: `${p.url}/api/bd`, cabeceras: { Authorization: `Bearer ${p.clave}` }, credenciales: "omit", puente: p };
    return { url: `${this.base}/api/bd`, cabeceras: { "X-CSRFToken": csrf() }, credenciales: "same-origin", puente: null };
  }

  _error(estado, datos, destino) {
    if (estado === 401 && destino.puente) return new ErrorBD("La clave del puente no es correcta (o el puente se reinició con otra). Vuelve a escribir: bd-puente <url> <clave>", { estado });
    if (estado === 401) return new ErrorBD("Inicia sesión en CódigoCamp para usar tus bases de datos.", { estado });
    return new ErrorBD(datos?.error || `Error ${estado}`, { codigo: datos?.codigo ?? null, estado });
  }

  _sinConexion(destino) {
    return destino.puente
      ? new ErrorBD(`No se pudo hablar con el puente en ${destino.puente.url}. ¿Está abierto? En tu PC: python backend/herramientas/puente_bd.py`)
      : new ErrorBD("No se pudo hablar con el servidor de CódigoCamp.");
  }

  async estado() {
    const d = this._destino();
    let r;
    try { r = await this.fetchFn(`${d.url}/estado`, { headers: d.cabeceras, credentials: d.credenciales, cache: "no-store" }); }
    catch { throw this._sinConexion(d); }
    const datos = await r.json().catch(() => ({}));
    if (!r.ok) throw this._error(r.status, datos, d);
    return { ...datos, puente: d.puente };
  }

  async pedir(accion, datos) {
    const d = this._destino();
    let r;
    try {
      r = await this.fetchFn(`${d.url}/${accion}`, { method: "POST", headers: { "Content-Type": "application/json", ...d.cabeceras }, credentials: d.credenciales, body: JSON.stringify(datos), cache: "no-store" });
    } catch { throw this._sinConexion(d); }
    const j = await r.json().catch(() => ({}));
    if (!r.ok) {
      if (r.status === 403 && accion === "conectar" && !d.puente && /no permite conectar a bases/.test(j.error || "")) {
        throw new ErrorBD(`${j.error}\nSi tu MySQL está en tu PC y CódigoCamp en internet: abre el puente en tu PC (python backend/herramientas/puente_bd.py) y escribe aquí bd-puente <url> <clave>.`, { estado: 403 });
      }
      throw this._error(r.status, j, d);
    }
    return j;
  }

  /** Igual que pedir() pero síncrono (para Python, que no puede esperar promesas). */
  pedirSync(accion, datos) {
    const d = this._destino();
    const x = new this.XHR();
    x.open("POST", `${d.url}/${accion}`, false);
    x.withCredentials = d.credenciales !== "omit";
    x.setRequestHeader("Content-Type", "application/json");
    for (const [k, v] of Object.entries(d.cabeceras)) x.setRequestHeader(k, v);
    try { x.send(JSON.stringify(datos)); } catch { throw this._sinConexion(d); }
    if (x.status === 0) throw this._sinConexion(d);
    let j = {};
    try { j = JSON.parse(x.responseText || "{}"); } catch { /* respuesta vacía */ }
    if (x.status < 200 || x.status >= 300) throw this._error(x.status, j, d);
    return j;
  }
}

// ---------------- formato como el cliente mysql ----------------
const anchoVisible = (t) => [...t].length;
const celda = (v) => v === null || v === undefined ? "NULL" : typeof v === "object" && v.$bytes !== undefined ? `0x${v.$bytes.toUpperCase()}` : String(v);
const esNumero = (v) => typeof v === "number" || (typeof v === "string" && /^-?\d+(\.\d+)?$/.test(v));

export function tablaMysql(columnas, filas) {
  const textos = filas.map((f) => f.map((v) => celda(v).replace(/\r?\n/g, "\\n")));
  const anchos = columnas.map((c, i) => Math.max(anchoVisible(c), ...textos.map((f) => anchoVisible(f[i]))));
  const borde = `+${anchos.map((a) => "-".repeat(a + 2)).join("+")}+`;
  const rellenar = (t, a, derecha) => derecha ? " ".repeat(a - anchoVisible(t)) + t : t + " ".repeat(a - anchoVisible(t));
  const numericas = columnas.map((_, i) => filas.length > 0 && filas.every((f) => f[i] === null || esNumero(f[i])));
  const linea = (vals, encabezado) => `| ${vals.map((t, i) => rellenar(t, anchos[i], !encabezado && numericas[i])).join(" | ")} |`;
  return [borde, linea(columnas, true), borde, ...textos.map((f) => linea(f, false)), borde].join("\n") + "\n";
}

export function verticalMysql(columnas, filas) {
  const ancho = Math.max(...columnas.map(anchoVisible));
  return filas.map((f, n) => `${"*".repeat(27)} ${n + 1}. row ${"*".repeat(27)}\n${columnas.map((c, i) => `${" ".repeat(ancho - anchoVisible(c))}${c}: ${celda(f[i])}`).join("\n")}\n`).join("");
}

export function tabuladoMysql(columnas, filas, encabezados = true) {
  return [...(encabezados ? [columnas.join("\t")] : []), ...filas.map((f) => f.map(celda).join("\t"))].join("\n") + (filas.length || encabezados ? "\n" : "");
}

const seg = (r) => `(${(r.segundos ?? 0).toFixed(2)} sec)`;
const plural = (n, palabra) => `${n} ${palabra}${n === 1 ? "" : "s"}`;

/** Texto que muestra mysql después de una sentencia. */
export function resultadoMysql(r, { vertical = false, lote = false, encabezados = true } = {}) {
  if (r.columnas) {
    if (lote) return tabuladoMysql(r.columnas, r.filas, encabezados);
    if (!r.filas.length) return `Empty set ${seg(r)}\n\n`;
    const cuerpo = vertical ? verticalMysql(r.columnas, r.filas) : tablaMysql(r.columnas, r.filas);
    return `${cuerpo}${plural(r.filas.length, "row")} in set${r.avisos ? `, ${plural(r.avisos, "warning")}` : ""} ${seg(r)}${r.truncado ? color.amarillo(" — se muestran las primeras filas") : ""}\n\n`;
  }
  if (lote) return "";
  return `Query OK, ${plural(r.afectadas ?? 0, "row")} affected${r.avisos ? `, ${plural(r.avisos, "warning")}` : ""} ${seg(r)}\n\n`;
}

/**
 * Divide un texto SQL en sentencias completas (terminadas en ; o \G), respetando comillas, `identificadores`,
 * comentarios y el comando DELIMITER. Devuelve { completas: [{ sql, vertical }], resto, delimitador }.
 */
export function partirMysql(texto, delimitador = ";") {
  const completas = [];
  let actual = "", i = 0, delim = delimitador;
  const empujar = (vertical = false) => { const sql = actual.trim(); if (sql) completas.push({ sql, vertical }); actual = ""; };
  while (i < texto.length) {
    // DELIMITER al inicio de una línea
    if (!actual.trim()) {
      const m = /^[ \t]*delimiter[ \t]+(\S+)[ \t]*(\r?\n|$)/i.exec(texto.slice(i));
      if (m) { delim = m[1]; i += m[0].length; actual = ""; continue; }
    }
    const c = texto[i], resto = texto.slice(i);
    if (c === "'" || c === '"' || c === "`") {
      let j = i + 1;
      while (j < texto.length && texto[j] !== c) j += texto[j] === "\\" && c !== "`" ? 2 : 1;
      actual += texto.slice(i, j + 1); i = j + 1; continue;
    }
    if (resto.startsWith("-- ") || resto.startsWith("--\n") || c === "#") { const j = texto.indexOf("\n", i); i = j < 0 ? texto.length : j + 1; actual += "\n"; continue; }
    if (resto.startsWith("/*") && !resto.startsWith("/*!")) { const j = texto.indexOf("*/", i + 2); i = j < 0 ? texto.length : j + 2; actual += " "; continue; }
    if (resto.startsWith(delim)) { i += delim.length; empujar(false); continue; }
    if (resto.startsWith("\\G") || resto.startsWith("\\g")) { const v = resto[1] === "G"; i += 2; empujar(v); continue; }
    actual += c; i++;
  }
  return { completas, resto: actual, delimitador: delim };
}

/** Lee las opciones de la línea de comandos de mysql. */
export function opcionesMysql(args) {
  const o = { host: "127.0.0.1", puerto: 3306, usuario: "root", clave: "", pedirClave: false, base: null, ejecutar: null, lote: false, encabezados: true, vertical: false, ayuda: false, version: false };
  const valor = (i, largo) => { const a = args[i]; const eq = a.indexOf("="); if (largo && eq > 0) return [a.slice(eq + 1), i]; return [args[i + 1], i + 1]; };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--help" || a === "-?") o.ayuda = true;
    else if (a === "-V" || a === "--version") o.version = true;
    else if (a === "-B" || a === "--batch") o.lote = true;
    else if (a === "-N" || a === "--skip-column-names") o.encabezados = false;
    else if (a === "-E" || a === "--vertical") o.vertical = true;
    else if (a === "-p" || a === "--password") o.pedirClave = true;
    else if (/^-p./.test(a)) o.clave = a.slice(2);
    else if (a.startsWith("--password=")) o.clave = a.slice(11);
    else if (/^-[uhPDe]$/.test(a) || /^--(user|host|port|database|execute)(=|$)/.test(a)) {
      const [v, j] = valor(i, a.startsWith("--")); i = j;
      const k = a.startsWith("--") ? a.slice(2).split("=")[0] : { u: "user", h: "host", P: "port", D: "database", e: "execute" }[a[1]];
      if (k === "user") o.usuario = v; else if (k === "host") o.host = v; else if (k === "port") o.puerto = Number(v); else if (k === "database") o.base = v; else o.ejecutar = v ?? "";
    } else if (/^-[uhPD]./.test(a)) {
      const v = a.slice(2);
      if (a[1] === "u") o.usuario = v; else if (a[1] === "h") o.host = v; else if (a[1] === "P") o.puerto = Number(v); else o.base = v;
    } else if (a.startsWith("--protocol") || a.startsWith("--default-character-set") || a === "--force" || a === "-f" || a === "-t" || a === "--table") { /* se aceptan y se ignoran */ }
    else if (!a.startsWith("-") && o.base === null) o.base = a;
    else return { ...o, error: `mysql: opción desconocida «${a}»` };
  }
  if (o.host === "localhost") o.host = "localhost";
  return o;
}

const AYUDA_MYSQL = `Uso: mysql [opciones] [base]
  -u USUARIO     usuario (por defecto root, como XAMPP)
  -p[CLAVE]      contraseña (sola: te la pide oculta)
  -h HOST        servidor (por defecto 127.0.0.1)   -P PUERTO  (3306)
  -D BASE        base de datos                       -e "SQL"   ejecuta y sale
  -B / -N / -E   salida con tabuladores / sin encabezados / vertical
  mysql -u root mi_base < archivo.sql    ejecuta un archivo (p. ej. para importar tu .sql)
Dentro: USE base;  SHOW TABLES;  source archivo.sql  ·  termina con ; (o \\G para vertical) · exit para salir.
Si CódigoCamp está en internet y tu MySQL en tu PC: abre el puente (bd-puente --ayuda).
`;

/**
 * Comando mysql / mariadb.
 * @param {object} o { args, py, cwd, out, err, leerLinea, entrada, cliente: ClienteBD }
 */
export async function comandoMysql(o) {
  const { out, err, cliente } = o;
  const op = opcionesMysql(o.args);
  if (op.error) { err(`${op.error}\n`); return 2; }
  if (op.ayuda) { out(AYUDA_MYSQL); return 0; }
  if (op.version) { out("mysql  Ver 15.1 (cliente de CódigoCamp para MySQL/MariaDB)\n"); return 0; }
  if (op.pedirClave) op.clave = (await o.leerLinea("Enter password: ", { secreto: true })) ?? "";

  let sesion, base = op.base;
  try {
    const r = await cliente.pedir("conectar", { host: op.host, puerto: op.puerto, usuario: op.usuario, clave: op.clave, base: op.base });
    sesion = r.sesion;
    if (o.entrada === null || o.entrada === undefined) {
      if (op.ejecutar === null) out(`Welcome to the MySQL monitor (cliente de CódigoCamp).\nServer version: ${r.version || "?"} · ${op.usuario}@${op.host}:${op.puerto}${cliente.puente() ? " · por el puente" : ""}\n\nType 'help;' or '\\h' for help. Type 'exit' to quit.\n\n`);
    }
  } catch (e) { err(`${e.message}\n`); return 1; }

  const fuentes = [];
  const leerFuente = (nombre) => {
    const ruta = FS.resolver(o.cwd, nombre.replace(/^['"]|['"]$/g, ""));
    const t = ruta === null ? undefined : o.py.files[ruta];
    if (t === undefined) throw new ErrorBD(`Failed to open file '${nombre}', error: 2`);
    if (leerMarcador(t)) throw new ErrorBD(`'${nombre}' es un archivo binario, no un script SQL.`);
    return t;
  };

  // Ejecuta un trozo de SQL. Devuelve true si todo fue bien. `seguir` = continuar tras un error (consola interactiva).
  let delimitador = ";";
  const ejecutarTexto = async (texto, { seguir = false, final = true } = {}) => {
    const { completas, resto, delimitador: d } = partirMysql(texto + (final ? "\n" : ""), delimitador);
    delimitador = d;
    const lista = [...completas, ...(final && resto.trim() ? [{ sql: resto.trim(), vertical: false }] : [])];
    for (const { sql, vertical } of lista) {
      const ok = await sentencia(sql, vertical);
      if (!ok && !seguir) return false;
    }
    return true;
  };
  const sentencia = async (sql, vertical) => {
    const m = /^(source|\\\.)\s+(.+)$/i.exec(sql);
    if (m) {
      if (fuentes.length > 10) { err("ERROR: demasiados source anidados.\n"); return false; }
      let texto;
      try { texto = leerFuente(m[2].trim()); } catch (e) { err(`ERROR: ${e.message}\n`); return false; }
      fuentes.push(m[2]);
      try { return await ejecutarTexto(texto, { seguir: false }); } finally { fuentes.pop(); }
    }
    try {
      const r = await cliente.pedir("consulta", { sesion, sql });
      if (r.base !== undefined) base = r.base;
      const texto = resultadoMysql(r, { vertical: vertical || op.vertical, lote: op.lote || (o.entrada != null && !op.vertical), encabezados: op.encabezados });
      if (/^use\s/i.test(sql) && !op.lote && o.entrada == null) out("Database changed\n");
      else out(texto);
      return true;
    } catch (e) {
      err(`${e.message}\n`);
      if (e.estado === 410) throw e;
      return false;
    }
  };

  try {
    if (op.ejecutar !== null) return (await ejecutarTexto(op.ejecutar)) ? 0 : 1;
    if (o.entrada !== null && o.entrada !== undefined) return (await ejecutarTexto(o.entrada)) ? 0 : 1;
    let buffer = "";
    for (;;) {
      const linea = await o.leerLinea(buffer ? `${" ".repeat(Math.max(0, `MariaDB [${base ?? "(none)"}]`.length - 3))}-> ` : `MariaDB [${base ?? "(none)"}]> `, {});
      if (linea === null || linea === undefined) break;
      const t = linea.trim();
      if (!buffer) {
        if (/^(exit|quit|\\q)\s*;?$/i.test(t)) { out("Bye\n"); break; }
        if (/^(help|\\h|\?)\s*;?$/i.test(t)) { out(AYUDA_MYSQL); continue; }
        if (/^(clear|\\c)$/i.test(t)) continue;
        if (/^(source|\\\.)\s+\S/i.test(t)) { await sentencia(t.replace(/;\s*$/, ""), false); continue; }
        if (/^use\s+\S+\s*;?$/i.test(t)) { await sentencia(t.replace(/;\s*$/, ""), false); continue; }
        if (!t) continue;
      }
      if (/\\c\s*$/.test(t)) { buffer = ""; continue; }
      buffer += (buffer ? "\n" : "") + linea;
      const { completas, resto, delimitador: d } = partirMysql(buffer, delimitador);
      if (completas.length || d !== delimitador) {
        delimitador = d;
        for (const { sql, vertical } of completas) await sentencia(sql, vertical);
        buffer = resto.trim() ? resto : "";
      }
    }
    return 0;
  } catch (e) {
    if (e.estado === 410) return 1;
    err(`${e.message}\n`); return 1;
  } finally {
    try { await cliente.pedir("cerrar", { sesion }); } catch { /* ya cerrada */ }
  }
}

/** Comando bd-puente: configurar el puente a tu MySQL local. */
export async function comandoPuente(o) {
  const { args, out, err, cliente } = o;
  const [a, b] = args;
  if (!a || a === "--ayuda" || a === "--help" || a === "-h") {
    const p = cliente.puente();
    out(`${p ? `Puente configurado: ${color.verde(p.url)}\n\n` : ""}Conecta Trabajo con las bases de tu PC (MySQL/MariaDB de XAMPP, PostgreSQL, MongoDB, Redis) cuando CódigoCamp está en internet:
  1. En tu PC, con tu base encendida (XAMPP: MySQL en «Start»):  pip install pymysql pg8000 pymongo redis
                                                          python backend/herramientas/puente_bd.py
  2. Copia la línea que muestra y pégala aquí:           bd-puente http://127.0.0.1:8787 <clave>
  3. Listo:  mysql -u root finanbot_db · psql -U postgres · mongosh · redis-cli
            y en Python: pymysql, mysql.connector, psycopg2, pymongo, redis
Otros:  bd-puente probar  ·  bd-puente quitar
(Si CódigoCamp corre en tu mismo PC, no necesitas el puente.)
`);
    return 0;
  }
  if (a === "quitar" || a === "off") { cliente.quitarPuente(); out("Puente quitado. Se usará el servidor de CódigoCamp.\n"); return 0; }
  if (a !== "probar") {
    try { cliente.configurarPuente(a, b); } catch (e) { err(`${e.message}\n`); return 1; }
  }
  try {
    const e = await cliente.estado();
    if (!e.activo) { err("El servidor no permite conectar a bases externas. Abre el puente en tu PC: bd-puente --ayuda\n"); return 1; }
    out(`${color.verde("✔")} ${e.puente ? `Puente listo en ${e.puente.url}` : "El servidor de CódigoCamp puede conectar"} · hosts permitidos: ${(e.hosts || []).join(", ")}\nPrueba: mysql -u root\n`);
    return 0;
  } catch (e) { err(`${e.message}\n`); return 1; }
}
