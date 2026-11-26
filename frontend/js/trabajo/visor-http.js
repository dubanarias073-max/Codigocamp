// Cliente HTTP de Trabajo (como Postman / Thunder Client / REST Client de VS Code).
// Cada colección es un archivo .http del proyecto (el mismo formato de la extensión REST Client), así se guarda con tu
// proyecto, va en git y funciona igual con la cuenta y con la carpeta de tu equipo (Conector):
//
//   @base = http://localhost:8000
//   ### Listar usuarios
//   GET {{base}}/usuarios?pagina=1
//   Authorization: Bearer {{token}}
//
//   ### Crear usuario
//   POST {{base}}/usuarios
//   Content-Type: application/json
//
//   {"nombre": "Ana"}
//
// Quién hace la petición (lo decide trabajo.js con enviar()): localhost → tu servidor de Trabajo o tu equipo con el
// Conector; internet → el puente seguro del servidor de CódigoCamp (sin CORS).
import { nombreBase } from "./fs.js";

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
export const METODOS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"];
const RE_PETICION = new RegExp(`^(${METODOS.join("|")})\\s+(\\S+)(?:\\s+HTTP/[\\d.]+)?\\s*$`, "i");
const RE_URL_SOLA = /^(https?:\/\/|\{\{|\/)\S*$/i;

/** Lee un archivo .http → { variables: [{nombre, valor}], peticiones: [{nombre, metodo, url, cabeceras: [{k, v, on}], cuerpo}] } */
export function parsearHttp(texto) {
  const variables = [], peticiones = [];
  const bloques = String(texto ?? "").replace(/\r\n/g, "\n").split(/^###.*$/m);
  const titulos = [...String(texto ?? "").replace(/\r\n/g, "\n").matchAll(/^###[ \t]*(.*)$/gm)].map((m) => m[1].trim());
  bloques.forEach((b, i) => {
    const lineas = b.split("\n");
    let j = 0, nombre = i === 0 ? "" : titulos[i - 1] || "";
    // variables y comentarios antes de la línea de la petición
    for (; j < lineas.length; j++) {
      const l = lineas[j].trim();
      const v = l.match(/^@([\w.-]+)\s*=\s*(.*)$/);
      if (v) { if (!variables.some((x) => x.nombre === v[1])) variables.push({ nombre: v[1], valor: v[2].trim() }); continue; }
      const nom = l.match(/^(?:#|\/\/)\s*@name\s+(.+)$/);
      if (nom) { nombre = nom[1].trim(); continue; }
      if (!l || l.startsWith("#") || l.startsWith("//")) continue;
      break;
    }
    if (j >= lineas.length) return;
    const primera = lineas[j].trim();
    const m = primera.match(RE_PETICION);
    if (!m && !RE_URL_SOLA.test(primera)) return;
    const p = { nombre: nombre || "", metodo: m ? m[1].toUpperCase() : "GET", url: m ? m[2] : primera, cabeceras: [], cuerpo: "" };
    j += 1;
    // líneas «?a=1» o «&b=2» que continúan la URL
    while (j < lineas.length && /^\s*[?&]/.test(lineas[j])) { p.url += lineas[j].trim(); j += 1; }
    for (; j < lineas.length; j++) {
      const l = lineas[j];
      if (!l.trim()) { j += 1; break; }
      const apagada = l.match(/^\s*#\s*([\w-]+)\s*:\s*(.*)$/);
      if (apagada) { p.cabeceras.push({ k: apagada[1], v: apagada[2], on: false }); continue; }
      if (/^\s*(#|\/\/)/.test(l)) continue;
      const c = l.match(/^\s*([^:\s][^:]*):\s?(.*)$/);
      if (c) p.cabeceras.push({ k: c[1].trim(), v: c[2], on: true });
    }
    p.cuerpo = lineas.slice(j).join("\n").replace(/\s+$/, "");
    if (!p.nombre) p.nombre = `${p.metodo} ${p.url.replace(/^https?:\/\/[^/]+/, "").replace(/^\{\{[\w.-]+\}\}/, "") || "/"}`.slice(0, 60);
    peticiones.push(p);
  });
  return { variables, peticiones };
}

/** Escribe la colección otra vez como archivo .http. */
export function serializarHttp({ variables = [], peticiones = [] }) {
  const partes = [];
  if (variables.length) partes.push(variables.filter((v) => v.nombre).map((v) => `@${v.nombre} = ${v.valor}`).join("\n"));
  for (const p of peticiones) {
    const cab = p.cabeceras.filter((c) => c.k.trim()).map((c) => `${c.on === false ? "# " : ""}${c.k.trim()}: ${c.v}`);
    partes.push([`### ${p.nombre || `${p.metodo} ${p.url}`}`, `${p.metodo} ${p.url}`, ...cab, ...(p.cuerpo.trim() ? ["", p.cuerpo.replace(/\s+$/, "")] : [])].join("\n"));
  }
  return partes.join("\n\n") + "\n";
}

/** Reemplaza {{variable}} y las dinámicas {{$timestamp}}, {{$guid}}, {{$randomInt min max}}, {{$isoDate}}. */
export function sustituir(texto, variables) {
  const mapa = new Map(variables.map((v) => [v.nombre, v.valor]));
  return String(texto ?? "").replace(/\{\{\s*([$\w.-]+)(?:\s+(-?\d+)\s+(-?\d+))?\s*\}\}/g, (todo, n, a, b) => {
    if (n === "$timestamp") return String(Math.floor(Date.now() / 1000));
    if (n === "$isoDate") return new Date().toISOString();
    if (n === "$guid" || n === "$uuid") return crypto.randomUUID?.() ?? `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`;
    if (n === "$randomInt") { const x = Number(a ?? 0), y = Number(b ?? 1000); return String(Math.floor(x + Math.random() * (y - x))); }
    return mapa.has(n) ? sustituir(mapa.get(n), variables.filter((v) => v.nombre !== n)) : todo;
  });
}

/** La petición lista para enviar: URL y cabeceras con variables, Content-Type puesto si el cuerpo es JSON. */
export function prepararPeticion(p, variables) {
  const url = sustituir(p.url, variables).trim();
  const cabeceras = p.cabeceras.filter((c) => c.on !== false && c.k.trim()).map((c) => [c.k.trim(), sustituir(c.v, variables)]);
  const cuerpo = METODOS.includes(p.metodo) && !["GET", "HEAD"].includes(p.metodo) ? sustituir(p.cuerpo, variables) : "";
  if (cuerpo && !cabeceras.some(([k]) => k.toLowerCase() === "content-type")) {
    try { JSON.parse(cuerpo); cabeceras.push(["Content-Type", "application/json"]); } catch { cabeceras.push(["Content-Type", "text/plain; charset=utf-8"]); }
  }
  return { metodo: p.metodo, url, cabeceras, cuerpo };
}

/** Comando curl equivalente (para copiar). */
export function comoCurl({ metodo, url, cabeceras, cuerpo }) {
  const s = (t) => `'${String(t).replace(/'/g, "'\\''")}'`;
  return [`curl -X ${metodo} ${s(url)}`, ...cabeceras.map(([k, v]) => `  -H ${s(`${k}: ${v}`)}`), ...(cuerpo ? [`  --data-raw ${s(cuerpo)}`] : [])].join(" \\\n");
}

/** JSON con colores (sin librerías). */
export function jsonBonito(texto) {
  let obj;
  try { obj = JSON.parse(texto); } catch { return null; }
  const json = JSON.stringify(obj, null, 2);
  return esc(json).replace(/(&quot;(?:\\.|[^&\\]|&(?!quot;))*?&quot;)(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g, (m, cadena, dosPuntos, lit) => {
    if (cadena) return dosPuntos ? `<span class="vh-k">${cadena}</span>${dosPuntos}` : `<span class="vh-s">${cadena}</span>`;
    if (lit) return `<span class="vh-l">${m}</span>`;
    return `<span class="vh-n">${m}</span>`;
  });
}

const PLANTILLA = `@base = http://localhost:8000

### Probar que la API responde
GET {{base}}/

### Ejemplo con JSON
POST {{base}}/items
Content-Type: application/json

{
  "nombre": "Lápiz",
  "precio": 1500
}

### API pública de ejemplo
GET https://jsonplaceholder.typicode.com/todos/1
`;
export const plantillaHttp = () => PLANTILLA;

export class VisorHTTP {
  /**
   * @param {{ ruta?: string, titulo?: string, texto: string, guardar: (texto:string) => void, enviar: (peticion) => Promise<object>,
   *           botones?: {texto:string, titulo:string, fn:() => void}[], aviso?: (t:string, tipo?:string) => void }} o
   */
  constructor({ ruta = "", titulo = "", texto, guardar, enviar, botones = [], aviso = () => {} }) {
    Object.assign(this, { ruta, titulo, texto, guardarTexto: guardar, enviarFn: enviar, botones, aviso });
    this.esImagen = true;
    this.especial = true;
    this.raiz = document.createElement("div");
    this.raiz.className = "vhttp";
    this.raiz.tabIndex = 0;
    this.raiz.hidden = true;
    this.ta = this.raiz;
    this.col = parsearHttp(texto);
    if (!this.col.peticiones.length) this.col.peticiones.push({ nombre: "Nueva petición", metodo: "GET", url: "{{base}}/", cabeceras: [], cuerpo: "" });
    this.sel = 0;
    this.pestana = "parametros";
    this.vistaResp = "bonito";
    this.respuestas = new Map();   // índice → respuesta
    this.verificar = true;
    this.#pintar();
    this.raiz.addEventListener("click", (e) => this.#clic(e));
    this.raiz.addEventListener("submit", (e) => { e.preventDefault(); this.#enviar(); });
    this.raiz.addEventListener("input", (e) => this.#entrada(e));
    this.raiz.addEventListener("change", (e) => this.#entrada(e));
    this.raiz.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); this.#enviar(); }
      if (e.target.matches("textarea, input")) e.stopPropagation();
    });
  }

  get lenguaje() { return "HTTP"; }
  leer() { return this.texto; }
  establecer(texto) {
    if (texto === this.texto) return;
    this.texto = texto;
    this.col = parsearHttp(texto);
    if (!this.col.peticiones.length) this.col.peticiones.push({ nombre: "Nueva petición", metodo: "GET", url: "", cabeceras: [], cuerpo: "" });
    this.sel = Math.min(this.sel, this.col.peticiones.length - 1);
    this.#pintar();
  }
  renombrar(ruta) { this.ruta = ruta; this.#pintar(); }
  mostrar() { this.raiz.hidden = false; }
  ocultar() { this.raiz.hidden = true; }
  enfocar() { this.raiz.focus({ preventScroll: true }); }
  irALinea() {}
  destruir() { clearTimeout(this.tGuardar); this.raiz.remove(); }

  get actual() { return this.col.peticiones[this.sel]; }
  #guardar(repintarLista = false) {
    clearTimeout(this.tGuardar);
    this.tGuardar = setTimeout(() => { this.texto = serializarHttp(this.col); this.guardarTexto(this.texto); }, 350);
    if (repintarLista) this.#pintarLista();
  }

  // ------------------------------------------------------------------------------------------- dibujar ----
  #pintar() {
    this.raiz.innerHTML = `<aside class="vh-lado">
        <div class="vh-cab"><b title="${esc(this.titulo || this.ruta)}">⚡ ${esc(this.titulo || nombreBase(this.ruta))}</b><span class="vh-cab-btns">${this.botones.map((b, i) => `<button type="button" class="btn sm ghost" data-boton="${i}" title="${esc(b.titulo)}" aria-label="${esc(b.titulo)}">${esc(b.texto)}</button>`).join("")}</span></div>
        <div class="vh-lista" data-lista></div>
        <button type="button" class="btn sm" data-accion="nueva">＋ Nueva petición</button>
        <details class="vh-vars" ${this.col.variables.length ? "open" : ""}><summary>Variables <small>{{nombre}}</small></summary><div data-vars></div></details>
      </aside>
      <section class="vh-main">
        <form class="vh-linea" data-form>
          <select data-campo="metodo" class="vh-metodo m-${esc(this.actual.metodo)}" aria-label="Método">${METODOS.map((m) => `<option ${m === this.actual.metodo ? "selected" : ""}>${m}</option>`).join("")}</select>
          <input data-campo="url" class="vh-url" value="${esc(this.actual.url)}" placeholder="https://api.ejemplo.com/recurso o {{base}}/ruta" spellcheck="false" aria-label="Dirección">
          <button type="submit" class="btn pri vh-enviar">Enviar ▶</button>
        </form>
        <div class="vh-nombre"><input data-campo="nombre" value="${esc(this.actual.nombre)}" aria-label="Nombre de la petición" placeholder="Nombre de la petición">
          <button type="button" class="btn sm ghost" data-accion="curl" title="Copiar como comando curl">curl</button><button type="button" class="btn sm ghost" data-accion="duplicar" title="Duplicar">⧉</button><button type="button" class="btn sm ghost" data-accion="borrar" title="Borrar petición">🗑</button></div>
        <div class="vh-tabs" role="tablist">${[["parametros", "Parámetros"], ["cabeceras", "Encabezados"], ["cuerpo", "Cuerpo"], ["auth", "Autorización"], ["opciones", "Opciones"]].map(([k, t]) => `<button type="button" role="tab" data-pestana="${k}" class="${this.pestana === k ? "on" : ""}">${t}${k === "cabeceras" && this.actual.cabeceras.length ? ` <small>${this.actual.cabeceras.length}</small>` : ""}</button>`).join("")}</div>
        <div class="vh-panel" data-panel></div>
        <div class="vh-respuesta" data-respuesta></div>
      </section>`;
    this.#pintarLista();
    this.#pintarVars();
    this.#pintarPanel();
    this.#pintarRespuesta();
  }
  #pintarLista() {
    const l = this.raiz.querySelector("[data-lista]");
    if (!l) return;
    l.innerHTML = this.col.peticiones.map((p, i) => { const r = this.respuestas.get(i); return `<button type="button" class="vh-item ${i === this.sel ? "on" : ""}" data-sel="${i}"><span class="vh-m m-${esc(p.metodo)}">${esc(p.metodo)}</span><b>${esc(p.nombre || p.url)}</b>${r ? `<small class="vh-st s${String(r.status || 0)[0]}">${r.status || "✕"}</small>` : ""}</button>`; }).join("");
  }
  #pintarVars() {
    const c = this.raiz.querySelector("[data-vars]");
    if (!c) return;
    c.innerHTML = `${this.col.variables.map((v, i) => `<div class="vh-kv"><input data-var="${i}" data-parte="nombre" value="${esc(v.nombre)}" placeholder="nombre"><input data-var="${i}" data-parte="valor" value="${esc(v.valor)}" placeholder="valor"><button type="button" class="vh-x" data-quitar-var="${i}" aria-label="Quitar">✕</button></div>`).join("")}
      <button type="button" class="btn sm ghost" data-accion="var-nueva">＋ Variable</button>`;
  }
  #kv(lista, tipo) {
    return `<div class="vh-tabla">${lista.map((x, i) => `<div class="vh-kv"><input type="checkbox" data-${tipo}="${i}" data-parte="on" ${x.on !== false ? "checked" : ""} aria-label="Usar"><input data-${tipo}="${i}" data-parte="k" value="${esc(x.k)}" placeholder="${tipo === "par" ? "parámetro" : "Encabezado"}"><input data-${tipo}="${i}" data-parte="v" value="${esc(x.v)}" placeholder="valor"><button type="button" class="vh-x" data-quitar-${tipo}="${i}" aria-label="Quitar">✕</button></div>`).join("")}
      <button type="button" class="btn sm ghost" data-accion="${tipo}-nuevo">＋ ${tipo === "par" ? "Parámetro" : "Encabezado"}</button></div>`;
  }
  #parametros() {
    const url = this.actual.url, i = url.indexOf("?");
    if (i < 0) return [];
    return url.slice(i + 1).split("&").filter(Boolean).map((par) => { const [k, ...v] = par.split("="); return { k: decodeURIComponent(k.replace(/\+/g, " ")), v: decodeURIComponent(v.join("=").replace(/\+/g, " ")), on: true }; });
  }
  #ponerParametros(lista) {
    const base = this.actual.url.split("?")[0];
    const enc = (t) => (/\{\{.*\}\}/.test(t) ? t : encodeURIComponent(t));
    const qs = lista.filter((x) => x.on !== false && x.k).map((x) => `${enc(x.k)}=${enc(x.v)}`).join("&");
    this.actual.url = base + (qs ? `?${qs}` : "");
    const u = this.raiz.querySelector('[data-campo="url"]'); if (u) u.value = this.actual.url;
  }
  #auth() {
    const h = this.actual.cabeceras.find((c) => c.k.toLowerCase() === "authorization" && c.on !== false);
    if (!h) return { tipo: "ninguna" };
    const b = h.v.match(/^Bearer\s+(.*)$/i); if (b) return { tipo: "bearer", token: b[1] };
    const ba = h.v.match(/^Basic\s+(.*)$/i);
    if (ba) { let u = "", c = ""; try { const t = /\{\{/.test(ba[1]) ? ba[1] : atob(ba[1]); [u, ...c] = t.split(":"); c = c.join(":"); } catch { /* nada */ } return { tipo: "basic", usuario: u, clave: c }; }
    return { tipo: "otra", valor: h.v };
  }
  #ponerAuth(a) {
    this.actual.cabeceras = this.actual.cabeceras.filter((c) => c.k.toLowerCase() !== "authorization");
    if (a.tipo === "bearer") this.actual.cabeceras.push({ k: "Authorization", v: `Bearer ${a.token || ""}`, on: true });
    else if (a.tipo === "basic") { const t = `${a.usuario || ""}:${a.clave || ""}`; this.actual.cabeceras.push({ k: "Authorization", v: `Basic ${/\{\{/.test(t) ? t : btoa(unescape(encodeURIComponent(t)))}`, on: true }); }
  }
  #pintarPanel() {
    const c = this.raiz.querySelector("[data-panel]");
    if (!c) return;
    const p = this.actual;
    if (this.pestana === "parametros") c.innerHTML = this.#kv(this.#parametros(), "par") + '<p class="vh-ayuda">Se agregan a la dirección después de «?». Puedes usar {{variables}}.</p>';
    else if (this.pestana === "cabeceras") c.innerHTML = this.#kv(p.cabeceras, "cab") + '<p class="vh-ayuda">Ejemplos: Content-Type: application/json · Accept: application/json. Desmarca uno para dejarlo guardado sin enviarlo.</p>';
    else if (this.pestana === "cuerpo") {
      const sinCuerpo = ["GET", "HEAD"].includes(p.metodo);
      c.innerHTML = `${sinCuerpo ? `<p class="vh-ayuda">Las peticiones ${p.metodo} no llevan cuerpo. Cambia a POST, PUT o PATCH para enviar datos.</p>` : ""}
        <div class="vh-cuerpo-barra"><button type="button" class="btn sm ghost" data-accion="formatear">Dar formato al JSON</button><span class="vh-ayuda" data-json-estado></span></div>
        <textarea class="vh-cuerpo" data-campo="cuerpo" spellcheck="false" placeholder='{"nombre": "Ana"}' ${sinCuerpo ? "disabled" : ""}>${esc(p.cuerpo)}</textarea>`;
      this.#estadoJson();
    } else if (this.pestana === "auth") {
      const a = this.#auth();
      c.innerHTML = `<div class="vh-auth"><label>Tipo <select data-auth="tipo">${[["ninguna", "Sin autorización"], ["bearer", "Bearer Token (JWT)"], ["basic", "Usuario y contraseña (Basic)"]].map(([v, t]) => `<option value="${v}" ${a.tipo === v ? "selected" : ""}>${t}</option>`).join("")}${a.tipo === "otra" ? '<option value="otra" selected>Otra (en Encabezados)</option>' : ""}</select></label>
        ${a.tipo === "bearer" ? `<label>Token <input data-auth="token" value="${esc(a.token)}" placeholder="eyJhbGciOi… o {{token}}" spellcheck="false"></label>` : ""}
        ${a.tipo === "basic" ? `<label>Usuario <input data-auth="usuario" value="${esc(a.usuario)}"></label><label>Contraseña <input data-auth="clave" type="password" value="${esc(a.clave)}"></label>` : ""}
        <p class="vh-ayuda">💡 Guarda el token en una variable (@token = …) para usarlo en todas las peticiones como {{token}}.</p></div>`;
    } else c.innerHTML = `<label class="vh-op"><input type="checkbox" data-verificar ${this.verificar ? "checked" : ""}> Verificar el certificado HTTPS (desactívalo solo para tu servidor de pruebas con certificado propio)</label>
      <p class="vh-ayuda">Quién hace la petición: a <b>localhost</b> → tu servidor encendido en Trabajo o, con la carpeta de tu equipo abierta, tu equipo (Conector). A <b>internet</b> → el servidor de CódigoCamp (como Postman, sin bloqueos CORS). Por seguridad, desde el servidor no se puede llegar a redes internas.</p>`;
  }
  #estadoJson() {
    const e = this.raiz.querySelector("[data-json-estado]");
    if (!e) return;
    const t = this.actual.cuerpo.trim();
    if (!t || /\{\{/.test(t)) { e.textContent = ""; return; }
    try { JSON.parse(t); e.textContent = "✓ JSON válido"; e.className = "vh-ayuda ok"; } catch (x) { e.textContent = t[0] === "{" || t[0] === "[" ? `✕ JSON con error: ${x.message}` : ""; e.className = "vh-ayuda mal"; }
  }
  #pintarRespuesta() {
    const c = this.raiz.querySelector("[data-respuesta]");
    if (!c) return;
    const r = this.respuestas.get(this.sel);
    if (this.enviando === this.sel) { c.innerHTML = '<div class="vh-esperando"><span class="vh-spin"></span>Enviando…</div>'; return; }
    if (!r) { c.innerHTML = '<div class="vh-vacio-caja"><span class="vh-vacio-ico" aria-hidden="true">⚡</span><b>Aquí verás la respuesta</b><p class="vh-ayuda">Escribe la dirección y pulsa <b>Enviar</b> (o Ctrl+Enter). Funciona con tu servidor de Trabajo (localhost), con APIs de internet y, con el Conector, con tu computador.</p></div>'; return; }
    if (r.error) { c.innerHTML = `<div class="vh-error"><b>No hubo respuesta</b><p>${esc(r.error)}</p></div>`; return; }
    const tipo = (r.cabeceras.find(([k]) => k.toLowerCase() === "content-type")?.[1] || "").toLowerCase();
    const texto = r.texto;
    const bonito = /json/.test(tipo) || /^\s*[[{]/.test(texto) ? jsonBonito(texto) : null;
    const esImg = /^image\//.test(tipo), esHtml = /html/.test(tipo);
    const cuerpo = this.vistaResp === "cabeceras"
      ? `<table class="vh-cabs">${r.cabeceras.map(([k, v]) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`).join("")}</table>`
      : this.vistaResp === "vista" && esImg ? `<div class="vh-img"><img src="${r.urlImg}" alt="Imagen de la respuesta"></div>`
        : this.vistaResp === "vista" && esHtml ? `<iframe class="vh-iframe" sandbox="" srcdoc="${esc(texto)}" title="Vista de la respuesta"></iframe>`
          : this.vistaResp === "bonito" && bonito ? `<pre class="vh-pre">${bonito}</pre>` : `<pre class="vh-pre">${esc(texto.length > 400000 ? texto.slice(0, 400000) + "\n… (recortado)" : texto)}</pre>`;
    c.innerHTML = `<div class="vh-resp-cab"><span class="vh-st s${String(r.status)[0]}">${r.status} ${esc(r.razon || "")}</span><span>⏱ ${r.ms} ms</span><span>📦 ${tamano(r.bytes)}</span><span class="vh-via" title="Quién hizo la petición">${esc(r.via)}</span>${r.truncado ? '<span class="vh-ayuda mal">Respuesta recortada (muy grande)</span>' : ""}
        <span class="vh-resp-tabs">${[["bonito", "Bonito"], ["crudo", "Crudo"], ...(esImg || esHtml ? [["vista", "Vista"]] : []), ["cabeceras", `Encabezados ${r.cabeceras.length}`]].map(([k, t]) => `<button type="button" data-vresp="${k}" class="${this.vistaResp === k ? "on" : ""}">${t}</button>`).join("")}
        <button type="button" data-accion="copiar-resp" title="Copiar la respuesta">⧉</button></span></div>${cuerpo}`;
  }

  // -------------------------------------------------------------------------------------- acciones ----
  async #enviar() {
    const i = this.sel;
    const pet = prepararPeticion(this.actual, this.col.variables);
    if (!/^https?:\/\//i.test(pet.url)) { this.respuestas.set(i, { error: /\{\{/.test(pet.url) ? `Falta definir una variable de la dirección: ${pet.url.match(/\{\{[^}]+\}\}/)[0]}` : "La dirección debe empezar con http:// o https://" }); this.#pintarRespuesta(); return; }
    this.enviando = i; this.#pintarRespuesta();
    const inicio = performance.now();
    try {
      const r = await this.enviarFn({ ...pet, verificar: this.verificar });
      const bytes = r.cuerpo instanceof Uint8Array ? r.cuerpo : new Uint8Array(r.cuerpo || []);
      const tipo = (r.cabeceras.find(([k]) => k.toLowerCase() === "content-type")?.[1] || "");
      const viejo = this.respuestas.get(i); if (viejo?.urlImg) URL.revokeObjectURL(viejo.urlImg);
      this.respuestas.set(i, { ...r, bytes: bytes.length, texto: new TextDecoder().decode(bytes), ms: r.ms ?? Math.round(performance.now() - inicio),
        urlImg: /^image\//i.test(tipo) ? URL.createObjectURL(new Blob([bytes], { type: tipo })) : null });
      if (this.vistaResp === "vista" && !/^image\/|html/i.test(tipo)) this.vistaResp = "bonito";
    } catch (e) { this.respuestas.set(i, { error: e.message || String(e) }); }
    this.enviando = null;
    if (this.sel === i) this.#pintarRespuesta();
    this.#pintarLista();
  }
  #clic(e) {
    const t = e.target.closest("[data-boton],[data-sel],[data-pestana],[data-accion],[data-vresp],[data-quitar-par],[data-quitar-cab],[data-quitar-var]");
    if (!t) return;
    if (t.dataset.sel !== undefined) { this.sel = Number(t.dataset.sel); this.#pintar(); return; }
    if (t.dataset.boton !== undefined) { this.botones[Number(t.dataset.boton)]?.fn(); return; }
    if (t.dataset.pestana) { this.pestana = t.dataset.pestana; this.#pintar(); return; }
    if (t.dataset.vresp) { this.vistaResp = t.dataset.vresp; this.#pintarRespuesta(); return; }
    if (t.dataset.quitarPar !== undefined) { const l = this.#parametros(); l.splice(Number(t.dataset.quitarPar), 1); this.#ponerParametros(l); this.#guardar(); this.#pintarPanel(); return; }
    if (t.dataset.quitarCab !== undefined) { this.actual.cabeceras.splice(Number(t.dataset.quitarCab), 1); this.#guardar(); this.#pintar(); return; }
    if (t.dataset.quitarVar !== undefined) { this.col.variables.splice(Number(t.dataset.quitarVar), 1); this.#guardar(); this.#pintarVars(); return; }
    const a = t.dataset.accion;
    if (a === "nueva") { this.col.peticiones.push({ nombre: "Nueva petición", metodo: "GET", url: this.col.variables.some((v) => v.nombre === "base") ? "{{base}}/" : "http://localhost:8000/", cabeceras: [], cuerpo: "" }); this.sel = this.col.peticiones.length - 1; this.#guardar(); this.#pintar(); this.raiz.querySelector('[data-campo="url"]')?.focus(); }
    else if (a === "duplicar") { this.col.peticiones.splice(this.sel + 1, 0, structuredClone({ ...this.actual, nombre: `${this.actual.nombre} (copia)` })); this.sel += 1; this.#guardar(); this.#pintar(); }
    else if (a === "borrar") { if (this.col.peticiones.length > 1) { this.col.peticiones.splice(this.sel, 1); this.respuestas.clear(); this.sel = Math.max(0, this.sel - 1); this.#guardar(); this.#pintar(); } }
    else if (a === "par-nuevo") { const l = this.#parametros(); l.push({ k: "parametro", v: "", on: true }); this.#ponerParametros(l); this.#guardar(); this.#pintarPanel(); }
    else if (a === "cab-nuevo") { this.actual.cabeceras.push({ k: "", v: "", on: true }); this.#guardar(); this.#pintarPanel(); this.raiz.querySelector(`[data-cab="${this.actual.cabeceras.length - 1}"][data-parte="k"]`)?.focus(); }
    else if (a === "var-nueva") { this.col.variables.push({ nombre: this.col.variables.length ? "" : "base", valor: this.col.variables.length ? "" : "http://localhost:8000" }); this.#guardar(); this.#pintarVars(); }
    else if (a === "formatear") { try { this.actual.cuerpo = JSON.stringify(JSON.parse(this.actual.cuerpo), null, 2); this.#guardar(); this.#pintarPanel(); } catch (x) { this.aviso(`El cuerpo no es JSON válido: ${x.message}`, "error"); } }
    else if (a === "curl") navigator.clipboard?.writeText(comoCurl(prepararPeticion(this.actual, this.col.variables))).then(() => this.aviso("Comando curl copiado."));
    else if (a === "copiar-resp") { const r = this.respuestas.get(this.sel); if (r?.texto !== undefined) navigator.clipboard?.writeText(r.texto).then(() => this.aviso("Respuesta copiada.")); }
  }
  #entrada(e) {
    const el = e.target;
    if (e.type === "change" && !el.matches("select, input[type=checkbox]")) return;
    const campo = el.dataset.campo;
    if (campo) {
      this.actual[campo] = el.value;
      if (campo === "metodo") { el.className = `vh-metodo m-${el.value}`; this.#guardar(true); if (this.pestana === "cuerpo") this.#pintarPanel(); return; }
      if (campo === "cuerpo") this.#estadoJson();
      if (campo === "url" && this.pestana === "parametros" && e.type === "input") { clearTimeout(this.tPar); this.tPar = setTimeout(() => { if (document.activeElement === el) { const p = this.raiz.querySelector("[data-panel]"); if (p) p.innerHTML = this.#kv(this.#parametros(), "par") + '<p class="vh-ayuda">Se agregan a la dirección después de «?». Puedes usar {{variables}}.</p>'; } }, 400); }
      this.#guardar(campo === "nombre" || campo === "url"); return;
    }
    if (el.dataset.par !== undefined) { const l = this.#parametros(); const x = l[Number(el.dataset.par)]; if (!x) return; if (el.dataset.parte === "on") x.on = el.checked; else x[el.dataset.parte] = el.value; this.#ponerParametros(el.dataset.parte === "on" && !el.checked ? l.filter((y) => y !== x) : l); this.#guardar(); if (el.dataset.parte === "on") this.#pintarPanel(); return; }
    if (el.dataset.cab !== undefined) { const x = this.actual.cabeceras[Number(el.dataset.cab)]; if (!x) return; if (el.dataset.parte === "on") x.on = el.checked; else x[el.dataset.parte] = el.value; this.#guardar(); return; }
    if (el.dataset.var !== undefined) { const x = this.col.variables[Number(el.dataset.var)]; if (x) { x[el.dataset.parte] = el.value.replace(el.dataset.parte === "nombre" ? /[^\w.-]/g : /\n/g, ""); this.#guardar(); } return; }
    if (el.dataset.auth) {
      const a = { ...this.#auth(), tipo: this.raiz.querySelector('[data-auth="tipo"]').value };
      for (const k of ["token", "usuario", "clave"]) { const i = this.raiz.querySelector(`[data-auth="${k}"]`); if (i) a[k] = i.value; }
      this.#ponerAuth(a); this.#guardar();
      if (el.dataset.auth === "tipo") this.#pintarPanel();
      return;
    }
    if (el.matches("[data-verificar]")) this.verificar = el.checked;
  }
}

function tamano(n) { return n < 1024 ? `${n} B` : n < 1024 * 1024 ? `${(n / 1024).toFixed(1)} KB` : `${(n / 1024 / 1024).toFixed(2)} MB`; }
