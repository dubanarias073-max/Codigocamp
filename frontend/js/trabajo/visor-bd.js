// Visor de bases de datos SQLite (.db, .sqlite, .sqlite3, .db3) dentro de Trabajo, como «SQLite Viewer» / DB Browser
// en VS Code: tablas y vistas, datos con edición, estructura, consultas SQL y exportar. Funciona igual con el proyecto
// de la cuenta y con la carpeta de tu equipo (Conector): lee el archivo, trabaja en memoria (sql.js) y guarda de vuelta.
//
// Tiene la forma de VisorArchivo (raiz, ta, mostrar, ocultar, establecer…) para que trabajo.js lo trate igual.
// «especial = true»: no se vuelve a crear cuando el archivo pasa de vacío a guardado (sigue siendo una base).
import { esMarcador, formatoBytes, leerMarcador } from "./archivos.js";
import { nombreBase } from "./fs.js";

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
export const q = (n) => `"${String(n).replace(/"/g, '""')}"`;   // nombre de tabla o columna seguro
const POR_PAGINA = 100;
const MAX_MB = 200;
const MODIFICA = /^\s*(create|insert|update|delete|drop|alter|replace|vacuum|reindex|attach|detach|pragma\s+\w+\s*=|begin|commit|rollback|savepoint|release)\b/i;

const celdaHTML = (v) => (v === null ? '<i class="vbd-null">NULL</i>' : v instanceof Uint8Array ? `<i class="vbd-blob">BLOB · ${formatoBytes(v.length)}</i>`
  : typeof v === "number" ? `<span class="vbd-num">${esc(v)}</span>` : esc(String(v).length > 300 ? String(v).slice(0, 300) + "…" : v));
const csvCelda = (v) => { const t = v === null ? "" : v instanceof Uint8Array ? "" : String(v); return /[",\n\r]/.test(t) ? `"${t.replace(/"/g, '""')}"` : t; };
const sqlValor = (v) => (v === null ? "NULL" : typeof v === "number" ? String(v) : v instanceof Uint8Array ? `X'${[...v].map((b) => b.toString(16).padStart(2, "0")).join("")}'` : `'${String(v).replace(/'/g, "''")}'`);

/** Divide un script en sentencias (respeta comillas, comentarios y BEGIN…END de triggers). */
export function dividirSQL(sql) {
  const out = [];
  let actual = "", comilla = null, linea = false, bloque = false, prof = 0;
  for (let i = 0; i < sql.length; i++) {
    const c = sql[i], s2 = sql.slice(i, i + 2);
    if (linea) { actual += c; if (c === "\n") linea = false; continue; }
    if (bloque) { actual += c; if (s2 === "*/") { actual += "/"; i++; bloque = false; } continue; }
    if (comilla) { actual += c; if (c === comilla) comilla = null; continue; }
    if (s2 === "--") { linea = true; actual += c; continue; }
    if (s2 === "/*") { bloque = true; actual += c; continue; }
    if (c === "'" || c === '"' || c === "`" || c === "[") { comilla = c === "[" ? "]" : c; actual += c; continue; }
    if (/[a-z]/i.test(c) && !/[a-z0-9_]/i.test(sql[i - 1] || "")) {
      const palabra = sql.slice(i).match(/^[a-z]+/i)[0].toUpperCase();
      if (palabra === "BEGIN" && /\bCREATE\s+(TEMP\w*\s+)?TRIGGER\b/i.test(actual)) prof += 1;
      else if (palabra === "END" && prof > 0) prof -= 1;
    }
    if (c === ";" && prof === 0) { if (actual.trim()) out.push(actual.trim()); actual = ""; continue; }
    actual += c;
  }
  if (actual.trim() && !/^(--[^\n]*\n?|\s|\/\*[\s\S]*?\*\/)*$/.test(actual)) out.push(actual.trim());
  return out;
}

export class VisorBD {
  /**
   * @param {{ ruta: string, texto: string, cargarSQL: () => Promise<any>, leer: (marcador:string) => Promise<Uint8Array>,
   *           guardar: (bytes:Uint8Array) => Promise<string>, aviso?: (t:string, tipo?:string) => void }} o
   */
  constructor({ ruta, texto, cargarSQL, leer, guardar, aviso = () => {} }) {
    Object.assign(this, { ruta, texto, cargarSQL, leerBytes: leer, guardarBytes: guardar, aviso });
    this.esImagen = true;
    this.especial = true;
    this.raiz = document.createElement("div");
    this.raiz.className = "vbd";
    this.raiz.tabIndex = 0;
    this.raiz.hidden = true;
    this.ta = this.raiz;
    this.db = null;
    this.tabla = null;
    this.vista = "datos";
    this.pagina = 0;
    this.orden = null;      // { col, desc }
    this.filtro = "";
    this.guardado = "ok";   // ok | pendiente | guardando | error
    this.historial = (() => { try { return JSON.parse(localStorage.getItem(`cc-bd-hist:${ruta}`) || "[]"); } catch { return []; } })();
    this.sql = "";
    this.#abrir();
    this.raiz.addEventListener("click", (e) => this.#clic(e));
    this.raiz.addEventListener("dblclick", (e) => this.#dobleClic(e));
    this.raiz.addEventListener("keydown", (e) => this.#tecla(e));
    this.raiz.addEventListener("input", (e) => this.#entrada(e));
  }

  get lenguaje() { return "SQLite"; }
  get ext() { return nombreBase(this.ruta).split(".").pop().toLowerCase(); }
  leer() { return this.texto; }
  establecer(texto) {
    if (texto === this.texto || texto === this.miGuardado) { this.texto = texto; return; }
    this.texto = texto;   // otro (la terminal sqlite3, git…) cambió la base: se vuelve a abrir
    this.#abrir();
  }
  renombrar(ruta) { this.ruta = ruta; this.#pintar(); }
  mostrar() { this.raiz.hidden = false; }
  ocultar() { this.raiz.hidden = true; }
  enfocar() { this.raiz.focus({ preventScroll: true }); }
  irALinea() {}
  destruir() { clearTimeout(this.tGuardar); try { this.db?.close(); } catch { /* nada */ } this.raiz.remove(); }

  // ---------------------------------------------------------------------------------------------- base ----
  async #abrir() {
    const m = leerMarcador(this.texto);
    this.raiz.innerHTML = `<p class="vbd-cargando">Abriendo «${esc(nombreBase(this.ruta))}»…</p>`;
    try {
      if (m && m.tamano > MAX_MB * 1024 * 1024) throw new Error(`pesa ${formatoBytes(m.tamano)}; el visor abre bases de hasta ${MAX_MB} MB (usa sqlite3 en la terminal).`);
      if (this.texto && !esMarcador(this.texto)) throw new Error("es un archivo de texto, no una base SQLite. Para crear tablas desde un script: sqlite3 base.db < script.sql");
      const SQL = await this.cargarSQL();
      const bytes = m ? await this.leerBytes(this.texto) : null;
      try { this.db?.close(); } catch { /* nada */ }
      this.db = bytes ? new SQL.Database(bytes) : new SQL.Database();
      this.db.exec("SELECT count(*) FROM sqlite_master");
      const objs = this.#objetos();
      if (!this.tabla || !objs.some((o) => o.nombre === this.tabla)) this.tabla = objs.find((o) => o.tipo === "table")?.nombre ?? objs[0]?.nombre ?? null;
      if (!this.tabla && this.vista === "datos") this.vista = "sql";
      if (!this.sql) this.sql = this.tabla ? `SELECT * FROM ${q(this.tabla)} LIMIT 50;` : "CREATE TABLE personas (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  nombre TEXT NOT NULL,\n  edad INTEGER\n);\n\nINSERT INTO personas (nombre, edad) VALUES ('Ana', 21), ('Luis', 25);\n\nSELECT * FROM personas;";
      this.#pintar();
    } catch (e) {
      this.db = null;
      this.raiz.innerHTML = `<div class="vbd-error"><b>No se pudo abrir la base de datos</b><p>«${esc(nombreBase(this.ruta))}» ${esc(e.message)}</p></div>`;
    }
  }

  #objetos() {
    const r = this.db.exec("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name");
    return (r[0]?.values || []).map(([nombre, tipo]) => {
      let filas = null;
      try { filas = this.db.exec(`SELECT count(*) FROM ${q(nombre)}`)[0].values[0][0]; } catch { /* vista con error */ }
      return { nombre, tipo, filas };
    });
  }
  #columnas(tabla) { return (this.db.exec(`PRAGMA table_info(${q(tabla)})`)[0]?.values || []).map(([cid, nombre, tipo, notnull, def, pk]) => ({ cid, nombre, tipo, notnull: !!notnull, def, pk })); }
  #esTabla(nombre) { return this.db.exec("SELECT type FROM sqlite_master WHERE name = ?", [nombre])[0]?.values[0]?.[0] === "table"; }
  #sinRowid(tabla) { const sql = this.db.exec("SELECT sql FROM sqlite_master WHERE name = ?", [tabla])[0]?.values[0]?.[0] || ""; return /WITHOUT\s+ROWID/i.test(sql); }

  /** Guarda la base en el proyecto (cuenta o equipo) un momento después del último cambio. */
  #cambio() {
    this.guardado = "pendiente";
    this.#pintarEstado();
    clearTimeout(this.tGuardar);
    this.tGuardar = setTimeout(() => this.#guardar(), 500);
  }
  async #guardar() {
    if (!this.db) return;
    let bytes;
    try { bytes = this.db.export(); }
    catch (e) { this.guardado = "error"; this.#pintarEstado(e.message.includes("transaction") ? "Termina la transacción (COMMIT) para guardar." : e.message); return; }
    this.guardado = "guardando"; this.#pintarEstado();
    try {
      const marcador = await this.guardarBytes(bytes);
      this.miGuardado = marcador;
      this.texto = marcador;
      this.guardado = "ok";
    } catch (e) { this.guardado = "error"; this.#pintarEstado(e.message); return; }
    this.#pintarEstado();
  }

  // ---------------------------------------------------------------------------------------- dibujar ----
  #pintar() {
    if (!this.db) return;
    const objs = this.#objetos();
    const m = leerMarcador(this.texto);
    const filtroObj = (this.buscarObj || "").toLowerCase();
    const lista = objs.filter((o) => !filtroObj || o.nombre.toLowerCase().includes(filtroObj));
    const grupo = (tipo, titulo) => { const xs = lista.filter((o) => o.tipo === tipo); return xs.length ? `<h4>${titulo} <small>${xs.length}</small></h4>${xs.map((o) => `<button type="button" class="vbd-obj ${o.nombre === this.tabla ? "on" : ""}" data-tabla="${esc(o.nombre)}" title="${esc(o.nombre)}"><span>${tipo === "table" ? "▦" : "👁"}</span><b>${esc(o.nombre)}</b><small>${o.filas ?? "?"}</small></button>`).join("")}` : ""; };
    this.raiz.innerHTML = `<aside class="vbd-lado">
        <div class="vbd-cab"><b title="${esc(this.ruta)}">🗄️ ${esc(nombreBase(this.ruta))}</b><small>SQLite · ${m ? formatoBytes(m.tamano) : "nueva"}</small></div>
        <input class="vbd-buscar" data-buscar-obj placeholder="Buscar tabla…" value="${esc(this.buscarObj || "")}" aria-label="Buscar tabla">
        <div class="vbd-objs">${grupo("table", "Tablas") + grupo("view", "Vistas") || '<p class="vbd-vacio">Sin tablas todavía. Crea una en la pestaña SQL.</p>'}</div>
        <button type="button" class="btn sm vbd-nueva" data-accion="nueva-tabla">＋ Nueva tabla</button>
      </aside>
      <section class="vbd-main">
        <div class="vbd-tabs" role="tablist">${[["datos", "Datos"], ["estructura", "Estructura"], ["sql", "SQL"], ["exportar", "Exportar"]].map(([k, t]) => `<button type="button" role="tab" data-vista="${k}" aria-selected="${this.vista === k}" class="${this.vista === k ? "on" : ""}">${t}</button>`).join("")}
          <span class="vbd-estado" data-estado></span></div>
        <div class="vbd-cuerpo" data-cuerpo></div>
      </section>`;
    this.#pintarEstado();
    this.#pintarVista();
  }
  #pintarEstado(detalle = "") {
    const e = this.raiz.querySelector("[data-estado]");
    if (!e) return;
    const t = { ok: "✓ Guardado", pendiente: "● Cambios sin guardar", guardando: "Guardando…", error: `⚠ No se guardó${detalle ? `: ${detalle}` : ""}` }[this.guardado];
    e.textContent = t; e.className = `vbd-estado ${this.guardado}`;
  }
  #pintarVista() {
    const c = this.raiz.querySelector("[data-cuerpo]");
    if (!c) return;
    if (this.vista === "sql") return this.#pintarSQL(c);
    if (this.vista === "exportar") return this.#pintarExportar(c);
    if (!this.tabla) { c.innerHTML = '<p class="vbd-vacio">Esta base no tiene tablas. Ve a <b>SQL</b> o usa <b>＋ Nueva tabla</b>.</p>'; return; }
    if (this.vista === "estructura") return this.#pintarEstructura(c);
    this.#pintarDatos(c);
  }

  #consultaDatos() {
    const cols = this.#columnas(this.tabla);
    const donde = this.filtro ? `WHERE ${cols.map((x) => `CAST(${q(x.nombre)} AS TEXT) LIKE ?`).join(" OR ")}` : "";
    const params = this.filtro ? cols.map(() => `%${this.filtro}%`) : [];
    const orden = this.orden && cols.some((x) => x.nombre === this.orden.col) ? `ORDER BY ${q(this.orden.col)} ${this.orden.desc ? "DESC" : "ASC"}` : "";
    return { cols, donde, params, orden };
  }
  #pintarDatos(c) {
    const esTabla = this.#esTabla(this.tabla);
    const conRowid = esTabla && !this.#sinRowid(this.tabla);
    const { cols, donde, params, orden } = this.#consultaDatos();
    const total = this.db.exec(`SELECT count(*) FROM ${q(this.tabla)} ${donde}`, params)[0].values[0][0];
    const paginas = Math.max(1, Math.ceil(total / POR_PAGINA));
    this.pagina = Math.min(this.pagina, paginas - 1);
    const sel = conRowid ? `rowid AS "__rowid__", *` : "*";
    const r = this.db.exec(`SELECT ${sel} FROM ${q(this.tabla)} ${donde} ${orden} LIMIT ${POR_PAGINA} OFFSET ${this.pagina * POR_PAGINA}`, params)[0];
    const nombres = r ? r.columns : cols.map((x) => x.nombre);
    const filas = r ? r.values : [];
    const vis = conRowid ? nombres.slice(1) : nombres;
    const pk = cols.filter((x) => x.pk).map((x) => x.nombre);
    const editable = esTabla && (conRowid || pk.length);
    const desde = total ? this.pagina * POR_PAGINA + 1 : 0, hasta = Math.min(total, (this.pagina + 1) * POR_PAGINA);
    c.innerHTML = `<div class="vbd-barra">
        <input class="vbd-filtro" data-filtro placeholder="Filtrar en todas las columnas…" value="${esc(this.filtro)}" aria-label="Filtrar filas">
        ${editable ? '<button type="button" class="btn sm" data-accion="fila-nueva">＋ Fila</button>' : `<span class="vbd-nota">${esTabla ? "Tabla sin clave: solo lectura" : "Vista: solo lectura"}</span>`}
        <button type="button" class="btn sm ghost" data-accion="recargar" title="Volver a leer">⟳</button>
        <span class="vbd-pag"><button type="button" class="btn sm ghost" data-accion="pag-ant" ${this.pagina ? "" : "disabled"}>‹</button>${desde}–${hasta} de ${total}<button type="button" class="btn sm ghost" data-accion="pag-sig" ${this.pagina < paginas - 1 ? "" : "disabled"}>›</button></span>
      </div>
      <div class="vbd-grid-caja"><table class="vbd-grid"><thead><tr>${editable ? "<th class=\"vbd-acc\"></th>" : ""}${vis.map((n) => {
        const col = cols.find((x) => x.nombre === n);
        const o = this.orden?.col === n ? (this.orden.desc ? " ▼" : " ▲") : "";
        return `<th data-orden="${esc(n)}" title="${esc(col?.tipo || "")}${col?.pk ? " · clave" : ""}">${col?.pk ? "🔑 " : ""}${esc(n)}<small>${esc(col?.tipo || "")}</small>${o}</th>`;
      }).join("")}</tr></thead>
      <tbody>${filas.map((f) => {
        const id = conRowid ? f[0] : JSON.stringify(pk.map((k) => f[nombres.indexOf(k)]));
        const vals = conRowid ? f.slice(1) : f;
        return `<tr data-id="${esc(id)}">${editable ? '<td class="vbd-acc"><button type="button" class="vbd-borrar" data-accion="borrar-fila" title="Borrar fila" aria-label="Borrar fila">🗑</button></td>' : ""}${vals.map((v, i) => `<td data-col="${esc(vis[i])}" class="${editable && !(v instanceof Uint8Array) ? "ed" : ""}">${celdaHTML(v)}</td>`).join("")}</tr>`;
      }).join("") || `<tr><td colspan="${vis.length + 1}" class="vbd-vacio">${this.filtro ? "Nada coincide con el filtro." : "La tabla está vacía."}</td></tr>`}</tbody></table></div>
      ${editable ? '<p class="vbd-ayuda">Doble clic en una celda para editarla · Enter guarda · Esc cancela · escribe NULL para dejarla vacía</p>' : ""}`;
    this.editable = editable; this.conRowid = conRowid; this.pk = pk;
  }

  #pintarEstructura(c) {
    const cols = this.#columnas(this.tabla);
    const idx = this.db.exec(`PRAGMA index_list(${q(this.tabla)})`)[0]?.values || [];
    const fks = this.db.exec(`PRAGMA foreign_key_list(${q(this.tabla)})`)[0]?.values || [];
    const crear = this.db.exec("SELECT sql FROM sqlite_master WHERE name = ?", [this.tabla])[0]?.values[0]?.[0] || "";
    c.innerHTML = `<div class="vbd-estructura">
      <h3>Columnas</h3><table class="vbd-grid"><thead><tr><th>#</th><th>Nombre</th><th>Tipo</th><th>Clave</th><th>Obligatoria</th><th>Por defecto</th></tr></thead>
      <tbody>${cols.map((x) => `<tr><td>${x.cid}</td><td><b>${esc(x.nombre)}</b></td><td>${esc(x.tipo || "—")}</td><td>${x.pk ? "🔑" : ""}</td><td>${x.notnull ? "Sí" : ""}</td><td>${x.def === null ? "" : esc(x.def)}</td></tr>`).join("")}</tbody></table>
      ${idx.length ? `<h3>Índices</h3><ul>${idx.map((i) => `<li><code>${esc(i[1])}</code>${i[2] ? " · único" : ""}</li>`).join("")}</ul>` : ""}
      ${fks.length ? `<h3>Relaciones (claves foráneas)</h3><ul>${fks.map((f) => `<li><code>${esc(f[3])}</code> → <code>${esc(f[2])}(${esc(f[4])})</code></li>`).join("")}</ul>` : ""}
      <h3>Cómo se creó</h3><pre class="vbd-pre">${esc(crear)}</pre>
      <div class="vbd-fila-btns"><button type="button" class="btn sm" data-accion="copiar-create">Copiar CREATE</button>${this.#esTabla(this.tabla) ? '<button type="button" class="btn sm ghost peligro" data-accion="borrar-tabla">Borrar tabla</button>' : ""}</div></div>`;
  }

  #pintarSQL(c) {
    const ejemplos = this.tabla ? [`SELECT * FROM ${q(this.tabla)} LIMIT 50;`, `SELECT count(*) FROM ${q(this.tabla)};`, `PRAGMA table_info(${q(this.tabla)});`] : [];
    c.innerHTML = `<div class="vbd-sql">
      <textarea class="vbd-sql-ta" data-sql spellcheck="false" aria-label="Consulta SQL">${esc(this.sql)}</textarea>
      <div class="vbd-barra"><button type="button" class="btn sm pri" data-accion="ejecutar">▶ Ejecutar <small>Ctrl+Enter</small></button>
        ${this.historial.length ? `<select class="vbd-hist" data-historial aria-label="Historial"><option value="">Historial…</option>${this.historial.map((h, i) => `<option value="${i}">${esc(h.replace(/\s+/g, " ").slice(0, 70))}</option>`).join("")}</select>` : ""}
        ${ejemplos.map((x) => `<button type="button" class="btn sm ghost vbd-chip" data-ejemplo="${esc(x)}">${esc(x.length > 34 ? x.slice(0, 34) + "…" : x)}</button>`).join("")}</div>
      <div class="vbd-resultados" data-resultados>${this.resultadosHTML || '<p class="vbd-ayuda">Escribe una o varias sentencias (separadas por ;) y pulsa Ejecutar. Los cambios se guardan solos en el archivo.</p>'}</div></div>`;
  }

  #pintarExportar(c) {
    const tablas = this.#objetos();
    c.innerHTML = `<div class="vbd-exportar">
      <label>Tabla o vista <select data-exp-tabla>${tablas.map((t) => `<option ${t.nombre === this.tabla ? "selected" : ""}>${esc(t.nombre)}</option>`).join("")}</select></label>
      <div class="vbd-fila-btns"><button type="button" class="btn sm" data-accion="exp-csv" ${tablas.length ? "" : "disabled"}>⬇ CSV (Excel)</button>
        <button type="button" class="btn sm" data-accion="exp-json" ${tablas.length ? "" : "disabled"}>⬇ JSON</button>
        <button type="button" class="btn sm" data-accion="exp-sql">⬇ Script SQL de toda la base</button>
        <button type="button" class="btn sm" data-accion="exp-db">⬇ Archivo .db</button></div>
      <p class="vbd-ayuda">El script SQL trae las tablas y sus datos: sirve para respaldar o para crear la misma base en MySQL/PostgreSQL (con pequeños ajustes).</p></div>`;
  }

  // ---------------------------------------------------------------------------------------- acciones ----
  #ejecutar() {
    const ta = this.raiz.querySelector("[data-sql]");
    const sel = ta && ta.selectionStart !== ta.selectionEnd ? ta.value.slice(ta.selectionStart, ta.selectionEnd) : null;
    this.sql = ta?.value ?? this.sql;
    const sentencias = dividirSQL(sel ?? this.sql);
    if (!sentencias.length) return;
    const partes = [];
    let modifico = false;
    for (const s of sentencias) {
      const t0 = performance.now();
      try {
        const r = this.db.exec(s);
        const ms = (performance.now() - t0).toFixed(1);
        const cambios = this.db.getRowsModified();
        if (MODIFICA.test(s)) modifico = true;
        if (r.length) {
          for (const res of r) {
            const filas = res.values.slice(0, 1000);
            partes.push(`<div class="vbd-res"><div class="vbd-res-cab">✓ ${res.values.length} fila${res.values.length === 1 ? "" : "s"} · ${ms} ms${res.values.length > 1000 ? " · se muestran 1000" : ""}<code>${esc(s.replace(/\s+/g, " ").slice(0, 80))}</code></div>
              <div class="vbd-grid-caja"><table class="vbd-grid"><thead><tr>${res.columns.map((x) => `<th>${esc(x)}</th>`).join("")}</tr></thead><tbody>${filas.map((f) => `<tr>${f.map((v) => `<td>${celdaHTML(v)}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>`);
          }
        } else partes.push(`<div class="vbd-res ok">✓ ${MODIFICA.test(s) && /^\s*(insert|update|delete|replace)/i.test(s) ? `${cambios} fila${cambios === 1 ? "" : "s"} afectada${cambios === 1 ? "" : "s"}` : "Listo"} · ${ms} ms<code>${esc(s.replace(/\s+/g, " ").slice(0, 80))}</code></div>`);
      } catch (e) {
        partes.push(`<div class="vbd-res error">✕ ${esc(e.message)}<code>${esc(s.replace(/\s+/g, " ").slice(0, 80))}</code></div>`);
        break;
      }
    }
    this.resultadosHTML = partes.join("");
    const texto = (sel ?? this.sql).trim();
    this.historial = [texto, ...this.historial.filter((h) => h !== texto)].slice(0, 25);
    try { localStorage.setItem(`cc-bd-hist:${this.ruta}`, JSON.stringify(this.historial)); } catch { /* sin espacio */ }
    if (modifico) { this.#cambio(); const objs = this.#objetos(); if (!objs.some((o) => o.nombre === this.tabla)) this.tabla = objs[0]?.nombre ?? null; }
    const pos = ta ? [ta.selectionStart, ta.selectionEnd] : null;
    this.#pintar();
    const nueva = this.raiz.querySelector("[data-sql]");
    if (nueva && pos) { nueva.focus(); nueva.setSelectionRange(...pos); }
  }

  #dondeFila(tr) {
    const id = tr.dataset.id;
    if (this.conRowid) return { donde: "rowid = ?", params: [Number(id)] };
    const vals = JSON.parse(id);
    return { donde: this.pk.map((k) => `${q(k)} IS ?`).join(" AND "), params: vals };
  }

  #editarCelda(td) {
    if (!this.editable || td.querySelector("input") || !td.classList.contains("ed")) return;
    const tr = td.closest("tr");
    const col = td.dataset.col;
    const { donde, params } = this.#dondeFila(tr);
    const actual = this.db.exec(`SELECT ${q(col)} FROM ${q(this.tabla)} WHERE ${donde}`, params)[0]?.values[0]?.[0];
    const input = document.createElement("input");
    input.className = "vbd-celda-input";
    input.value = actual === null || actual === undefined ? "" : String(actual);
    input.placeholder = actual === null ? "NULL" : "";
    td.innerHTML = ""; td.appendChild(input); input.focus(); input.select();
    let hecho = false;
    const terminar = (guardar) => {
      if (hecho) return;
      hecho = true;
      if (guardar && input.value !== (actual === null ? "" : String(actual))) {
        const t = input.value;
        const tipo = this.#columnas(this.tabla).find((x) => x.nombre === col)?.tipo.toUpperCase() || "";
        const valor = t === "NULL" ? null : /INT|REAL|FLOA|DOUB|NUM|DEC/.test(tipo) && t.trim() !== "" && !Number.isNaN(Number(t)) ? Number(t) : t;
        try { this.db.run(`UPDATE ${q(this.tabla)} SET ${q(col)} = ? WHERE ${donde}`, [valor, ...params]); this.#cambio(); }
        catch (e) { this.aviso(`No se pudo cambiar: ${e.message}`, "error"); }
      }
      this.#pintarVista();
    };
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); terminar(true); } else if (e.key === "Escape") { e.preventDefault(); terminar(false); } e.stopPropagation(); });
    input.addEventListener("blur", () => terminar(true));
  }

  #descargar(nombre, datos, tipo) {
    const url = URL.createObjectURL(new Blob([datos], { type: tipo }));
    const a = document.createElement("a"); a.href = url; a.download = nombre; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  }
  #volcadoSQL() {
    const out = ["-- Script generado por CódigoCamp", "PRAGMA foreign_keys=OFF;", "BEGIN TRANSACTION;"];
    const objs = this.db.exec("SELECT type, name, sql FROM sqlite_master WHERE sql NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 ELSE 2 END")[0]?.values || [];
    for (const [tipo, nombre, sql] of objs) {
      out.push(`${sql};`);
      if (tipo === "table") for (const fila of this.db.exec(`SELECT * FROM ${q(nombre)}`)[0]?.values || []) out.push(`INSERT INTO ${q(nombre)} VALUES(${fila.map(sqlValor).join(",")});`);
    }
    out.push("COMMIT;");
    return out.join("\n") + "\n";
  }

  #clic(e) {
    const t = e.target.closest("[data-tabla],[data-vista],[data-accion],[data-orden],[data-ejemplo]");
    if (!t || !this.db) return;
    if (t.dataset.tabla) { this.tabla = t.dataset.tabla; this.pagina = 0; this.orden = null; this.filtro = ""; if (this.vista === "sql" || this.vista === "exportar") this.vista = "datos"; this.#pintar(); return; }
    if (t.dataset.vista) { this.vista = t.dataset.vista; this.#pintar(); return; }
    if (t.dataset.orden !== undefined) { const col = t.dataset.orden; this.orden = this.orden?.col === col ? (this.orden.desc ? null : { col, desc: true }) : { col, desc: false }; this.#pintarVista(); return; }
    if (t.dataset.ejemplo) { this.sql = t.dataset.ejemplo; this.#pintar(); this.#ejecutar(); return; }
    const a = t.dataset.accion;
    try {
      if (a === "ejecutar") this.#ejecutar();
      else if (a === "recargar") this.#pintar();
      else if (a === "pag-ant") { this.pagina = Math.max(0, this.pagina - 1); this.#pintarVista(); }
      else if (a === "pag-sig") { this.pagina += 1; this.#pintarVista(); }
      else if (a === "nueva-tabla") { this.vista = "sql"; this.sql = "CREATE TABLE nueva_tabla (\n  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  nombre TEXT NOT NULL,\n  creado TEXT DEFAULT (datetime('now'))\n);"; this.resultadosHTML = ""; this.#pintar(); }
      else if (a === "fila-nueva") {
        const cols = this.#columnas(this.tabla);
        const necesarias = cols.filter((x) => x.notnull && x.def === null && !x.pk);
        this.db.run(necesarias.length ? `INSERT INTO ${q(this.tabla)} (${necesarias.map((x) => q(x.nombre)).join(",")}) VALUES (${necesarias.map((x) => (/INT|REAL|NUM|FLOA|DOUB|DEC/i.test(x.tipo) ? "0" : "''")).join(",")})` : `INSERT INTO ${q(this.tabla)} DEFAULT VALUES`);
        this.#cambio();
        const total = this.db.exec(`SELECT count(*) FROM ${q(this.tabla)}`)[0].values[0][0];
        this.filtro = ""; this.orden = null; this.pagina = Math.max(0, Math.ceil(total / POR_PAGINA) - 1);
        this.#pintar();
      } else if (a === "borrar-fila") {
        const { donde, params } = this.#dondeFila(t.closest("tr"));
        this.db.run(`DELETE FROM ${q(this.tabla)} WHERE ${donde}`, params);
        this.#cambio(); this.#pintar();
      } else if (a === "borrar-tabla") {
        if (!confirm(`¿Borrar la tabla «${this.tabla}» y todos sus datos?`)) return;
        this.db.run(`DROP TABLE ${q(this.tabla)}`); this.tabla = null; this.#cambio();
        this.tabla = this.#objetos()[0]?.nombre ?? null; this.vista = this.tabla ? "datos" : "sql"; this.#pintar();
      } else if (a === "copiar-create") navigator.clipboard?.writeText(this.db.exec("SELECT sql FROM sqlite_master WHERE name = ?", [this.tabla])[0]?.values[0]?.[0] || "").then(() => this.aviso("CREATE copiado."));
      else if (a === "exp-csv" || a === "exp-json") {
        const tabla = this.raiz.querySelector("[data-exp-tabla]").value;
        const r = this.db.exec(`SELECT * FROM ${q(tabla)}`)[0] || { columns: this.#columnas(tabla).map((x) => x.nombre), values: [] };
        if (a === "exp-csv") this.#descargar(`${tabla}.csv`, "﻿" + [r.columns.map(csvCelda).join(","), ...r.values.map((f) => f.map(csvCelda).join(","))].join("\r\n"), "text/csv;charset=utf-8");
        else this.#descargar(`${tabla}.json`, JSON.stringify(r.values.map((f) => Object.fromEntries(r.columns.map((c2, i) => [c2, f[i] instanceof Uint8Array ? null : f[i]]))), null, 2), "application/json");
      } else if (a === "exp-sql") this.#descargar(`${nombreBase(this.ruta).replace(/\.\w+$/, "")}.sql`, this.#volcadoSQL(), "application/sql");
      else if (a === "exp-db") this.#descargar(nombreBase(this.ruta), this.db.export(), "application/vnd.sqlite3");
    } catch (x) { this.aviso(x.message, "error"); }
  }
  #dobleClic(e) { const td = e.target.closest("td.ed"); if (td) this.#editarCelda(td); }
  #tecla(e) {
    if (e.target.matches("[data-sql]")) {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); this.#ejecutar(); return; }
      if (e.key === "Tab" && !e.shiftKey) { e.preventDefault(); const ta = e.target, i = ta.selectionStart; ta.setRangeText("  ", i, ta.selectionEnd, "end"); this.sql = ta.value; }
      e.stopPropagation();   // los atajos del editor no se disparan mientras escribes SQL
    }
  }
  #entrada(e) {
    if (e.target.matches("[data-sql]")) this.sql = e.target.value;
    else if (e.target.matches("[data-filtro]")) { this.filtro = e.target.value; this.pagina = 0; clearTimeout(this.tFiltro); this.tFiltro = setTimeout(() => { const pos = e.target.selectionStart; this.#pintarVista(); const f = this.raiz.querySelector("[data-filtro]"); f?.focus(); f?.setSelectionRange(pos, pos); }, 250); }
    else if (e.target.matches("[data-buscar-obj]")) { this.buscarObj = e.target.value; const pos = e.target.selectionStart; this.#pintar(); const b = this.raiz.querySelector("[data-buscar-obj]"); b?.focus(); b?.setSelectionRange(pos, pos); }
    else if (e.target.matches("[data-historial]") && e.target.value !== "") { this.sql = this.historial[Number(e.target.value)]; this.#pintar(); }
  }
}
