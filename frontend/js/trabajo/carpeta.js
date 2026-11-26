// «Abrir carpeta de mi computador»: sincroniza el proyecto con una carpeta real usando la File System Access API.
//
// Solo existe en Chrome, Edge y Opera de computador (ver soporteCarpeta). En los demás navegadores se usa ZIP.
//
// Cómo sincroniza (en los dos sentidos), comparando cada archivo con la «base» = cómo estaba en la última sincronización:
//   · cambió solo en el computador   → se copia al proyecto (o se borra del proyecto si allí lo borraste)
//   · cambió solo en CódigoCamp       → se escribe en la carpeta (o se borra de la carpeta)
//   · cambió en los dos lados         → gana el computador y la versión de CódigoCamp se guarda como «nombre.conflicto.ext»
// Nunca se tocan los archivos de la carpeta que CódigoCamp no maneja (videos, PDF, nombres con espacios, node_modules…).
// El texto se compara sin BOM y con saltos \n, así un archivo guardado con CRLF no «cambia» solo (sin ping-pong).
import * as FS from "./fs.js";
import { LIMITES_ARCHIVO, TEXTO_EDITABLE, claveContenido, crearMarcador, esMarcador, formatoBytes, leerMarcador } from "./archivos.js";
import { CARPETAS_IGNORADAS, clasificar } from "./importar.js";
import { sha256Blob } from "./sha256.js";

// ------------------------------------------------------------------ soporte del navegador ----
/**
 * ¿Se puede vincular una carpeta aquí? Devuelve { disponible, navegador, motivo?, consejo? } con textos en español.
 * Todo se puede inyectar para probarlo.
 */
export function soporteCarpeta({ win = globalThis, nav = globalThis.navigator } = {}) {
  const ua = nav?.userAgent || "";
  const movil = Boolean(nav?.userAgentData?.mobile) || /Android|iPhone|iPad|iPod|Mobile/i.test(ua) || (/Macintosh/.test(ua) && (nav?.maxTouchPoints || 0) > 1);
  const navegador = nav?.brave ? "Brave" : /Edg\//.test(ua) ? "Edge" : /OPR\/|Opera/.test(ua) ? "Opera" : /Firefox\//.test(ua) ? "Firefox"
    : /Chrome\//.test(ua) ? "Chrome" : /Safari\//.test(ua) ? "Safari" : "este navegador";
  const zip = "Mientras tanto usa «Importar .zip» y «Descargar proyecto (.zip)», o «Subir una carpeta» (una sola vez, sin sincronizar).";
  if (typeof win.showDirectoryPicker === "function") {
    if (win.isSecureContext === false) return { disponible: false, navegador, motivo: "La página no está en HTTPS.", consejo: "El navegador solo permite abrir carpetas en páginas seguras (https:// o http://localhost)." };
    try { if (win.top && win.self !== win.top) return { disponible: false, navegador, motivo: "La página está dentro de un marco.", consejo: "Ábrela en su propia pestaña." }; } catch { return { disponible: false, navegador, motivo: "La página está dentro de un marco.", consejo: "Ábrela en su propia pestaña." }; }
    return { disponible: true, navegador };
  }
  if (movil) return { disponible: false, navegador, motivo: "Los celulares y tabletas no permiten que una página abra carpetas.", consejo: `Funciona en Chrome, Edge u Opera de computador. ${zip}` };
  if (navegador === "Firefox") return { disponible: false, navegador, motivo: "Firefox no permite que las páginas abran carpetas de tu computador (Mozilla decidió no incluir esta función).", consejo: `Usa Chrome, Edge u Opera para esta opción. ${zip}` };
  if (navegador === "Safari") return { disponible: false, navegador, motivo: "Safari no permite que las páginas abran carpetas de tu computador.", consejo: `Usa Chrome, Edge u Opera para esta opción. ${zip}` };
  if (navegador === "Brave") return { disponible: false, navegador, motivo: "Brave trae esta función desactivada por privacidad.", consejo: `Puedes activarla en brave://flags/#file-system-access-api (y reiniciar Brave), o usar Chrome o Edge. ${zip}` };
  if (win.isSecureContext === false) return { disponible: false, navegador, motivo: "La página no está en HTTPS.", consejo: "El navegador solo permite abrir carpetas en páginas seguras (https:// o http://localhost)." };
  return { disponible: false, navegador, motivo: `${navegador === "este navegador" ? "Este navegador" : navegador} no permite abrir carpetas del computador (o es una versión antigua).`, consejo: `Actualízalo o usa Chrome, Edge u Opera. ${zip}` };
}

// --------------------------------------------------------------------------- utilidades ----
/** Extensiones que nunca son texto editable: con el Conector se dejan en tu equipo y se leen solo cuando las abres. */
const BINARIAS = new Set(("png jpg jpeg gif webp avif bmp ico tif tiff psd ai sketch fig xcf heic mp4 m4v mov webm ogv avi mkv wmv flv mp3 m4a wav ogg oga flac aac " +
  "pdf doc docx xls xlsx ppt pptx odt ods odp rtf ttf otf woff woff2 eot zip rar 7z tar gz tgz bz2 xz zst iso dmg img exe msi dll so dylib bin dat " +
  "o a lib obj pdb class jar war apk aab ipa wasm pyc pyo pyd node sqlite sqlite3 db mdb accdb blend fbx glb obj3d unitypackage ttc keystore jks").split(" "));
export const esBinariaPorNombre = (ruta) => { const i = ruta.lastIndexOf("."); return i > 0 && BINARIAS.has(ruta.slice(i + 1).toLowerCase()); };
const MIME_EXT = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp", avif: "image/avif", bmp: "image/bmp", ico: "image/x-icon",
  mp4: "video/mp4", m4v: "video/mp4", mov: "video/quicktime", webm: "video/webm", mp3: "audio/mpeg", m4a: "audio/mp4", wav: "audio/wav", ogg: "audio/ogg",
  pdf: "application/pdf", ttf: "font/ttf", otf: "font/otf", woff: "font/woff", woff2: "font/woff2", zip: "application/zip" };
const mimeDe = (ruta) => MIME_EXT[ruta.slice(ruta.lastIndexOf(".") + 1).toLowerCase()] || "application/octet-stream";

const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
export async function sha256(bytes) { return hex(await crypto.subtle.digest("SHA-256", bytes)); }
const enc = new TextEncoder();

/**
 * Lo que el proyecto guardaría para este archivo: el texto normalizado, el marcador del archivo binario u { omitir }.
 * entrada: Uint8Array o { blob, cabeza } (los grandes se leen por partes, sin cargarlos enteros).
 */
export async function valorDeBytes(ruta, entrada, { maxArchivo = LIMITES_ARCHIVO.porArchivo } = {}) {
  const e = entrada instanceof Uint8Array ? { bytes: entrada } : entrada;
  const c = clasificar(ruta, e, { maxArchivo });
  if (c.tipo === "texto") return { valor: c.texto };
  if (c.tipo === "omitir") return { omitir: c.motivo };
  const hash = e.bytes ? await sha256(e.bytes) : await sha256Blob(e.blob);
  return { valor: crearMarcador({ hash, tipo: c.mime, tamano: e.bytes ? e.bytes.length : e.blob.size }), bytes: e.bytes };
}

/** Nombre para guardar la versión que perdió un conflicto: app.js → app.conflicto.js (o -2, -3…). */
export function nombreConflicto(py, ruta) {
  const dir = FS.carpetaDe(ruta);
  const n = FS.nombreBase(ruta);
  const i = n.lastIndexOf(".");
  const nombre = i > 0 ? `${n.slice(0, i)}.conflicto${n.slice(i)}` : `${n}.conflicto`;
  return FS.unir(dir, FS.nombreLibre(py, dir, nombre.length > FS.LIMITES.nombre ? `conflicto-${Date.now()}` : nombre));
}

// ------------------------------------------------------------------------ discos ----
/** Disco real: una carpeta abierta con showDirectoryPicker(). */
export class DiscoNavegador {
  constructor(raiz) { this.raiz = raiz; this.nombre = raiz.name; }

  async #carpeta(ruta, crear = false) {
    let h = this.raiz;
    for (const parte of ruta.split("/").filter(Boolean)) h = await h.getDirectoryHandle(parte, { create: crear });
    return h;
  }

  /** [{ ruta, tamano, modificado }] de todos los archivos (sin entrar en carpetas ignoradas). Las carpetas, en `carpetas`. */
  async listar({ maximo = 5000 } = {}) {
    const archivos = [];
    const carpetas = [];
    const recorrer = async (h, prefijo) => {
      for await (const [nombre, hijo] of h.entries()) {
        if (archivos.length >= maximo) return;
        const ruta = prefijo ? `${prefijo}/${nombre}` : nombre;
        if (hijo.kind === "directory") {
          if (CARPETAS_IGNORADAS.has(nombre)) continue;
          carpetas.push(ruta);
          await recorrer(hijo, ruta);
        } else {
          try { const f = await hijo.getFile(); archivos.push({ ruta, tamano: f.size, modificado: f.lastModified }); } catch { /* bloqueado por otro programa: se intenta en la próxima vuelta */ }
        }
      }
    };
    await recorrer(this.raiz, "");
    return { archivos, carpetas };
  }

  /** El archivo como File (Blob): el navegador lo lee del disco cuando hace falta, sin cargarlo en memoria. */
  async abrir(ruta) {
    const h = await (await this.#carpeta(FS.carpetaDe(ruta))).getFileHandle(FS.nombreBase(ruta));
    return h.getFile();
  }

  async leer(ruta) { return new Uint8Array(await (await this.abrir(ruta)).arrayBuffer()); }

  async escribir(ruta, datos) {
    const h = await (await this.#carpeta(FS.carpetaDe(ruta), true)).getFileHandle(FS.nombreBase(ruta), { create: true });
    const w = await h.createWritable();
    try { await w.write(datos); await w.close(); } catch (e) { try { await w.abort(); } catch { /* ya cerrado */ } throw e; }
    const f = await h.getFile();
    return { tamano: f.size, modificado: f.lastModified };
  }

  async crearCarpeta(ruta) { await this.#carpeta(ruta, true); }

  async borrar(ruta) {
    const padre = await this.#carpeta(FS.carpetaDe(ruta));
    await padre.removeEntry(FS.nombreBase(ruta));
    // Si la carpeta quedó vacía, también se quita (sin recursive: si tiene algo, falla y se deja).
    for (let c = FS.carpetaDe(ruta); c; c = FS.carpetaDe(c)) {
      try { await (await this.#carpeta(FS.carpetaDe(c))).removeEntry(FS.nombreBase(c)); } catch { break; }
    }
  }

  async permiso(pedir = false) {
    const o = { mode: "readwrite" };
    if (typeof this.raiz.queryPermission !== "function") return "granted";
    const estado = await this.raiz.queryPermission(o);
    if (estado === "granted" || !pedir) return estado;
    return this.raiz.requestPermission(o);
  }
}

// ---------------------------------------------------------------------- sincronizador ----
export class Sincronizador {
  /**
   * @param {object} o
   * @param {object} o.disco             DiscoNavegador o uno falso con la misma forma
   * @param {()=>object} o.proyecto
   * @param {(info:object)=>void} o.alCambiar      el proyecto cambió por la carpeta ({ origen: "carpeta", rutas })
   * @param {(datos, {nombre})=>Promise<string>} [o.subirArchivo]   sube bytes o un Blob y devuelve el marcador
   * @param {(marcador)=>Promise<Blob>} [o.leerArchivo]
   * @param {(base:object, cache:object)=>void} [o.guardarBase]  para recordar la base (y las huellas ya calculadas) entre visitas
   * @param {(evento:object)=>void} [o.alAviso]   conflictos, archivos que no caben, errores
   */
  constructor({ disco, proyecto, alCambiar = () => {}, subirArchivo = null, leerArchivo = null, guardarBase = () => {}, alAviso = () => {}, base = null, cache = null,
    maxArchivo = LIMITES_ARCHIVO.porArchivo, registrarEquipo = null }) {
    Object.assign(this, { disco, proyecto, alCambiar, subirArchivo, leerArchivo, guardarBase, alAviso, maxArchivo, registrarEquipo });
    // Con el Conector (tu equipo): sin límites de la cuenta y los binarios no se leen ni se suben, se quedan en tu disco.
    this.enEquipo = Boolean(disco?.esEquipo && registrarEquipo);
    if (this.enEquipo) this.maxArchivo = Infinity;
    this.base = base ? { ...base } : null; // ruta -> valor (texto o marcador) en la última sincronización
    // ruta -> { tamano, modificado, valor?, omitir? }: así no se vuelve a leer (ni a calcular la huella de) lo que no cambió.
    this.cacheDisco = new Map(Object.entries(cache || {}).filter(([, c]) => c && typeof c === "object"));
    this.rechazados = new Map(); // ruta -> valor del disco que no cupo (para no repetir el aviso)
    this.omitidosDisco = new Map(); // ruta -> motivo
    this.ocupado = null;
    this.pendiente = false;
    this.ultima = null;
  }

  get vinculada() { return this.base !== null; }

  /** Lee la carpeta: Map ruta → { valor, bytes? } de lo que el proyecto puede guardar. */
  async #leerDisco() {
    this.#medida = null;   // el proyecto pudo cambiar desde la última vuelta
    const { archivos, carpetas } = await this.disco.listar();
    const salida = new Map();
    const omitidos = new Map();
    const vistos = new Set();
    // Discos lentos (la carpeta de otro equipo por el Conector) traen de una vez todo lo que hay que leer en esta vuelta.
    const perezoso = (a) => this.enEquipo && (a.tamano > TEXTO_EDITABLE || esBinariaPorNombre(a.ruta));
    if (this.disco.precargar) {
      const faltan = archivos.filter((a) => { const c = this.cacheDisco.get(a.ruta); return FS.rutaValida(a.ruta) && a.tamano <= this.maxArchivo && !perezoso(a) && (!c || c.tamano !== a.tamano || c.modificado !== a.modificado); });
      if (faltan.length) await this.disco.precargar(faltan);
    }
    for (const a of archivos) {
      vistos.add(a.ruta);
      if (!FS.rutaValida(a.ruta)) { omitidos.set(a.ruta, "su nombre tiene caracteres que no se admiten (\\ / : * ? \" < > |) o la ruta es demasiado larga"); continue; }
      let c = this.cacheDisco.get(a.ruta);
      if (!c || c.tamano !== a.tamano || c.modificado !== a.modificado) {
        if (a.tamano > this.maxArchivo) c = { tamano: a.tamano, modificado: a.modificado, omitir: `pesa ${formatoBytes(a.tamano)} (máximo ${formatoBytes(this.maxArchivo)} por archivo)` };
        else if (perezoso(a)) {
          // Imágenes, videos, programas, archivos enormes…: no se leen ni se suben. Su marcador sale del nombre, el tamaño y
          // la fecha; los bytes se piden a tu equipo solo cuando abres el archivo.
          const hash = await sha256(enc.encode(`equipo\0${this.disco.equipo?.id}\0${this.disco.raizReal || this.disco.carpeta}\0${a.ruta}\0${a.tamano}\0${a.modificado}`));
          c = { tamano: a.tamano, modificado: a.modificado, valor: crearMarcador({ hash, tipo: esBinariaPorNombre(a.ruta) ? mimeDe(a.ruta) : "text/plain", tamano: a.tamano }), equipo: true };
        } else {
          let entrada;
          try {
            if (a.tamano <= TEXTO_EDITABLE) entrada = await this.disco.leer(a.ruta);
            else { const blob = await this.disco.abrir(a.ruta); entrada = { blob, cabeza: new Uint8Array(await blob.slice(0, 64).arrayBuffer()) }; }
          } catch { continue; } // en uso por otro programa: próxima vuelta
          const v = await valorDeBytes(a.ruta, entrada, { maxArchivo: this.maxArchivo });
          c = { tamano: a.tamano, modificado: a.modificado, valor: v.valor, omitir: v.omitir, bytes: v.bytes };
        }
        this.cacheDisco.set(a.ruta, c);
      }
      if (c.equipo && this.enEquipo) { const ruta = a.ruta; this.registrarEquipo(c.valor, () => this.disco.abrir(ruta), this.disco.parte ? (desde, largo) => this.disco.parte(ruta, desde, largo) : null); }
      if (c.omitir) omitidos.set(a.ruta, c.omitir); else salida.set(a.ruta, c);
    }
    for (const r of [...this.cacheDisco.keys()]) if (!vistos.has(r)) this.cacheDisco.delete(r);
    this.omitidosDisco = omitidos;
    return { archivos: salida, carpetas: carpetas.filter(FS.rutaValida), omitidos };
  }

  async #escribirDisco(ruta, valor) {
    let datos;
    if (esMarcador(valor)) {
      if (!this.leerArchivo) throw new Error("no se pueden descargar archivos");
      datos = await this.leerArchivo(valor);
    } else datos = enc.encode(valor);
    const st = await this.disco.escribir(ruta, datos);
    this.cacheDisco.set(ruta, { tamano: st.tamano, modificado: st.modificado, valor });
  }

  /** Pone en el proyecto lo que vino del disco, respetando los límites. Devuelve false si no cupo. */
  /** Medidas del proyecto (cuántos archivos, cuánto texto, qué carpetas) calculadas UNA vez por vuelta y luego
   *  actualizadas archivo por archivo. Antes se recalculaban por cada archivo: con miles de archivos tardaba segundos. */
  #medida = null;
  #medir(py) {
    const m = this.#medida;
    if (m && m.py === py && m.files === py.files && m.folders === py.folders) return m;
    let caracteres = 0;
    for (const t of Object.values(py.files)) if (!(t.startsWith("cc") && /^cc(?:img|bin):v1:[a-f0-9]{64}:/.test(t))) caracteres += t.length;
    return (this.#medida = { py, files: py.files, folders: py.folders, cuenta: Object.keys(py.files).length, caracteres, carpetas: new Set(py.folders) });
  }

  async #ponerEnProyecto(py, ruta, d) {
    const m = this.#medir(py);
    const previo = py.files[ruta];
    const esMarca = (t) => typeof t === "string" && t.startsWith("cc") && /^cc(?:img|bin):v1:[a-f0-9]{64}:/.test(t);
    const largo = (t) => (t === undefined || esMarca(t) ? 0 : t.length);
    const cuenta = m.cuenta + (previo === undefined ? 1 : 0);
    const caracteres = m.caracteres - largo(previo) + largo(d.valor);
    let choca = ruta !== "" && m.carpetas.has(ruta);
    for (let c = FS.carpetaDe(ruta); c && !choca; c = FS.carpetaDe(c)) if (py.files[c] !== undefined) choca = true;
    let motivo = null;
    if (choca) motivo = "en el proyecto hay una carpeta o un archivo que choca con ese nombre";
    else if (this.enEquipo) { /* tu equipo: sin límites de la cuenta */ }
    else if (cuenta > FS.LIMITES.archivos) motivo = `el proyecto admite ${FS.LIMITES.archivos} archivos`;
    else if (caracteres > FS.LIMITES.caracteres) motivo = "se llenaría el espacio de texto editable del proyecto (5 millones de caracteres)";
    let valor = d.valor;
    if (!motivo && d.equipo && this.enEquipo) { /* se queda en tu equipo: no se sube a ningún lado */ }
    else if (!motivo && esMarcador(valor) && claveContenido(previo) !== claveContenido(valor)) {
      if (!this.subirArchivo) motivo = "no se pueden subir archivos";
      else {
        try { valor = await this.subirArchivo(d.bytes ?? await this.disco.abrir(ruta), { nombre: ruta }); }
        catch (e) { motivo = e.message; }
      }
    } else if (esMarcador(valor) && previo !== undefined && claveContenido(previo) === claveContenido(valor)) valor = previo;
    if (motivo) {
      if (this.rechazados.get(ruta) !== d.valor) this.alAviso({ tipo: "no-cabe", ruta, motivo });
      this.rechazados.set(ruta, d.valor);
      return false;
    }
    this.rechazados.delete(ruta);
    m.caracteres += largo(valor) - largo(previo);
    if (previo === undefined) m.cuenta++;
    py.files[ruta] = valor;
    let nuevas = false;
    for (let c = FS.carpetaDe(ruta); c; c = FS.carpetaDe(c)) if (!m.carpetas.has(c)) { m.carpetas.add(c); py.folders.push(c); nuevas = true; }
    if (nuevas) py.folders.sort();
    return true;
  }

  /**
   * Primera sincronización.
   * modo "carpeta": el proyecto pasa a ser una copia de la carpeta (lo del proyecto se reemplaza).
   * modo "combinar": el proyecto se escribe en la carpeta (gana el proyecto si hay el mismo archivo) y lo demás de la carpeta entra al proyecto.
   */
  async vincular(modo) {
    const py = this.proyecto();
    const disco = await this.#leerDisco();
    const cambiadas = [];
    if (modo === "carpeta") {
      py.files = {};
      py.folders = [];
      this.base = {};
      for (const [ruta, d] of [...disco.archivos].sort(([a], [b]) => a.localeCompare(b))) {
        if (await this.#ponerEnProyecto(py, ruta, d)) { this.base[ruta] = d.valor; cambiadas.push(ruta); }
      }
      const carpetas = new Set(py.folders);
      disco.carpetas.forEach((c) => { if (carpetas.size < FS.LIMITES.carpetas) for (let x = c; x; x = FS.carpetaDe(x)) carpetas.add(x); });
      py.folders = [...carpetas].sort();
    } else {
      this.base = {};
      for (const ruta of Object.keys(py.files).sort()) {
        if (disco.omitidos.has(ruta)) { this.alAviso({ tipo: "omitido", ruta, motivo: `en tu carpeta ya hay un «${ruta}» que CódigoCamp no puede manejar; no se sobrescribió` }); continue; }
        await this.#escribirDisco(ruta, py.files[ruta]);
        this.base[ruta] = py.files[ruta];
      }
      for (const c of py.folders) await this.disco.crearCarpeta(c);
      for (const [ruta, d] of disco.archivos) {
        if (ruta in py.files) continue;
        if (await this.#ponerEnProyecto(py, ruta, d)) { this.base[ruta] = d.valor; cambiadas.push(ruta); }
      }
    }
    this.guardarBase(this.base, this.#cacheSerializable());
    this.ultima = new Date();
    this.alCambiar({ origen: "carpeta", rutas: cambiadas, completo: true });
    return { traidos: cambiadas.length, omitidos: disco.omitidos };
  }

  /** Una vuelta de sincronización. Si ya hay una en curso, se repite al terminar. */
  sincronizar() {
    if (!this.vinculada) return Promise.resolve(null);
    if (this.ocupado) { this.pendiente = true; return this.ocupado; }
    this.ocupado = (async () => {
      try {
        let r;
        do { this.pendiente = false; r = await this.#vuelta(); } while (this.pendiente);
        return r;
      } finally { this.ocupado = null; }
    })();
    return this.ocupado;
  }

  async #vuelta() {
    const disco = await this.#leerDisco();
    const py = this.proyecto();
    const base = this.base;
    const rutas = new Set([...disco.archivos.keys(), ...Object.keys(py.files), ...Object.keys(base)]);
    const res = { alProyecto: [], alDisco: [], borradosProyecto: [], borradosDisco: [], conflictos: [] };
    for (const ruta of [...rutas].sort()) {
      if (disco.omitidos.has(ruta)) continue; // la carpeta tiene ahí algo que no manejamos: no se toca nada
      const d = disco.archivos.get(ruta);
      const pv = Object.hasOwn(py.files, ruta) ? py.files[ruta] : undefined;
      const bv = Object.hasOwn(base, ruta) ? base[ruta] : undefined;
      // Se compara el contenido: dos marcadores con la misma huella son el mismo archivo aunque digan otro tipo.
      const igual = (x, y) => (x === undefined || y === undefined ? x === y : claveContenido(x) === claveContenido(y));
      const dv = d?.valor;
      if (igual(dv, pv)) { if (dv === undefined) delete base[ruta]; else base[ruta] = pv; continue; }
      if (!igual(dv, bv) && igual(pv, bv)) {
        // Cambió solo en el computador.
        if (dv === undefined) { delete py.files[ruta]; delete base[ruta]; res.borradosProyecto.push(ruta); }
        else if (await this.#ponerEnProyecto(py, ruta, d)) { base[ruta] = py.files[ruta]; res.alProyecto.push(ruta); }
      } else if (!igual(pv, bv) && igual(dv, bv)) {
        // Cambió solo en CódigoCamp.
        try {
          if (pv === undefined) { await this.disco.borrar(ruta); this.cacheDisco.delete(ruta); delete base[ruta]; res.borradosDisco.push(ruta); }
          else { await this.#escribirDisco(ruta, pv); base[ruta] = pv; res.alDisco.push(ruta); }
        } catch (e) { this.alAviso({ tipo: "error", ruta, motivo: e.message || String(e) }); }
      } else {
        // Cambió en los dos lados (o es nuevo en ambos con distinto contenido).
        if (dv === undefined) { // borrado en el computador, editado aquí: se conserva la edición
          try { await this.#escribirDisco(ruta, pv); base[ruta] = pv; res.alDisco.push(ruta); } catch (e) { this.alAviso({ tipo: "error", ruta, motivo: e.message }); }
        } else if (pv === undefined) { // borrado aquí, editado en el computador: se recupera
          if (await this.#ponerEnProyecto(py, ruta, d)) { base[ruta] = py.files[ruta]; res.alProyecto.push(ruta); }
        } else {
          const copia = nombreConflicto(py, ruta);
          const r = FS.crearArchivo(py, copia, pv);
          if (await this.#ponerEnProyecto(py, ruta, d)) {
            base[ruta] = py.files[ruta];
            res.conflictos.push({ ruta, copia: r.ok ? copia : null });
            this.alAviso({ tipo: "conflicto", ruta, copia: r.ok ? copia : null });
          } else if (r.ok) delete py.files[copia];
        }
      }
    }
    // Carpetas (también las VACÍAS): las que creas o borras en la terminal del equipo aparecen o se van del explorador,
    // y las que creas aquí se crean allá. Antes solo se veían las carpetas que tenían algún archivo.
    let cambioCarpetas = false;
    {
      const enDisco = new Set(disco.carpetas);
      const enPy = new Set(py.folders);
      if (!this.baseCarpetas) this.baseCarpetas = new Set([...enDisco].filter((c) => enPy.has(c)));
      const baseC = this.baseCarpetas;
      for (const c of enDisco) {
        if (baseC.has(c) || enPy.has(c) || enPy.size >= FS.LIMITES.carpetas) continue;
        for (let x = c; x && !enPy.has(x); x = FS.carpetaDe(x)) enPy.add(x);
        cambioCarpetas = true;
      }
      for (const c of baseC) {
        if (enDisco.has(c) || !enPy.has(c)) continue;
        const ocupada = Object.keys(py.files).some((r) => FS.dentroDe(r, c)) || [...enDisco].some((x) => FS.dentroDe(x, c));
        if (!ocupada) { enPy.delete(c); for (const x of [...enPy]) if (FS.dentroDe(x, c) && !enDisco.has(x)) enPy.delete(x); cambioCarpetas = true; }
      }
      for (const c of [...enPy].sort()) {
        if (enDisco.has(c) || baseC.has(c)) continue;
        try { await this.disco.crearCarpeta(c); enDisco.add(c); } catch { /* sin permiso: se intenta en la próxima vuelta */ }
      }
      if (cambioCarpetas) py.folders = [...enPy].sort();
      this.baseCarpetas = new Set([...enDisco].filter((c) => enPy.has(c)));
    }
    const huboProyecto = res.alProyecto.length || res.borradosProyecto.length || res.conflictos.length || cambioCarpetas;
    if (res.borradosProyecto.length) {
      // Quita del proyecto las carpetas que quedaron vacías por borrar en el computador (si tampoco existen allá).
      const enDisco = new Set(disco.carpetas);
      py.folders = py.folders.filter((c) => enDisco.has(c) || Object.keys(py.files).some((r) => FS.dentroDe(r, c)));
    }
    this.guardarBase(base, this.#cacheSerializable());
    this.ultima = new Date();
    if (huboProyecto) this.alCambiar({ origen: "carpeta", rutas: [...res.alProyecto, ...res.borradosProyecto, ...res.conflictos.map((c) => c.copia).filter(Boolean)] });
    return res;
  }

  #cacheSerializable() {
    const o = {};
    for (const [r, c] of this.cacheDisco) o[r] = { tamano: c.tamano, modificado: c.modificado, valor: c.valor, omitir: c.omitir };
    return o;
  }

  desvincular() { this.base = null; this.baseCarpetas = null; this.cacheDisco.clear(); this.rechazados.clear(); }
}

// ------------------------------------------------------------------ recordar la carpeta ----
// La carpeta (su «handle») y la base se guardan en IndexedDB de este navegador. Al volver, el navegador
// vuelve a pedir permiso (salvo que hayas elegido «Permitir en cada visita» en Chrome).
const BD = "codigocamp-carpetas";
function abrirBD() {
  return new Promise((ok, mal) => {
    const r = indexedDB.open(BD, 1);
    r.onupgradeneeded = () => r.result.createObjectStore("vinculos");
    r.onsuccess = () => ok(r.result);
    r.onerror = () => mal(r.error);
  });
}
async function operar(modo, fn) {
  const bd = await abrirBD();
  try {
    return await new Promise((ok, mal) => {
      const tx = bd.transaction("vinculos", modo);
      const req = fn(tx.objectStore("vinculos"));
      tx.oncomplete = () => ok(req?.result);
      tx.onerror = () => mal(tx.error);
    });
  } finally { bd.close(); }
}
export const recuerdo = {
  leer: (clave) => operar("readonly", (s) => s.get(clave)).catch(() => null),
  guardar: (clave, valor) => operar("readwrite", (s) => s.put(valor, clave)).catch(() => null),
  borrar: (clave) => operar("readwrite", (s) => s.delete(clave)).catch(() => null),
};

export { leerMarcador };
