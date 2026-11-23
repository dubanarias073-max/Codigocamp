// Archivos binarios del proyecto (imágenes, videos, audio, PDF, fuentes, datos grandes…).
//
// El proyecto solo guarda texto, así que un archivo binario vive en dos partes:
//  · en el proyecto, un «marcador» de texto en la ruta del archivo:  ccbin:v1:<sha256>:<tipo>:<bytes>
//    (los marcadores ccimg:v1:… de la versión anterior siguen funcionando)
//  · en la cuenta (disco del servidor), los bytes, guardados por su huella SHA-256 (backend/rutas/archivos.py).
// Como el marcador es texto, mover, copiar, borrar, deshacer y Git funcionan igual que con cualquier archivo.
// Los límites reales los manda el servidor (backend/.env); estos son los de fábrica.

export const LIMITES_ARCHIVO = { porArchivo: 1024 ** 3, porCuenta: 10 * 1024 ** 3 };
/** Un archivo de texto más grande que esto se guarda como archivo (se ve y se descarga, pero no se edita). */
export const TEXTO_EDITABLE = 1024 * 1024;

const MARCADOR = /^cc(?:img|bin):v1:([a-f0-9]{64}):([a-z]+\/[a-z0-9.+-]{1,90}):(\d{1,13})$/;

export const esMarcador = (texto) => typeof texto === "string" && texto.startsWith("cc") && MARCADOR.test(texto);
export function leerMarcador(texto) {
  const m = typeof texto === "string" ? MARCADOR.exec(texto) : null;
  return m ? { hash: m[1], tipo: m[2], tamano: Number(m[3]) } : null;
}
export const crearMarcador = ({ hash, tipo, tamano }) => `ccbin:v1:${hash}:${tipo}:${tamano}`;
/** Dos valores del proyecto con el mismo contenido (para marcadores basta la huella: el tipo puede variar). */
export const claveContenido = (v) => { const m = leerMarcador(v); return m ? `#${m.hash}` : v; };

const POR_EXTENSION = {
  png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp", avif: "image/avif", bmp: "image/bmp", ico: "image/x-icon",
  mp4: "video/mp4", m4v: "video/mp4", mov: "video/quicktime", webm: "video/webm", ogv: "video/ogg", mp3: "audio/mpeg", m4a: "audio/mp4", wav: "audio/wav",
  ogg: "audio/ogg", oga: "audio/ogg", pdf: "application/pdf", ttf: "font/ttf", otf: "font/otf", woff: "font/woff", woff2: "font/woff2",
  zip: "application/zip", txt: "text/plain", csv: "text/csv", json: "application/json",
  // Documentos de Office y OpenDocument (se ven en Trabajo con el visor de documentos)
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  doc: "application/msword",
  xls: "application/vnd.ms-excel",
  ppt: "application/vnd.ms-powerpoint",
  odt: "application/vnd.oasis.opendocument.text",
  ods: "application/vnd.oasis.opendocument.spreadsheet",
  odp: "application/vnd.oasis.opendocument.presentation",
  rtf: "application/rtf",
};

/** Tipo MIME por los primeros bytes o la extensión (la misma regla que el servidor). */
export function tipoDe(cabeza, nombre = "") {
  const b = cabeza instanceof Uint8Array ? cabeza : new Uint8Array(cabeza);
  const ext = nombre.includes(".") ? nombre.slice(nombre.lastIndexOf(".") + 1).toLowerCase() : "";
  const empieza = (...f) => f.every((v, i) => b[i] === v);
  const texto = (i, s) => [...s].every((c, k) => b[i + k] === c.charCodeAt(0));
  if (empieza(0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a)) return "image/png";
  if (empieza(0xff, 0xd8, 0xff)) return "image/jpeg";
  if (texto(0, "GIF87a") || texto(0, "GIF89a")) return "image/gif";
  if (texto(0, "RIFF") && texto(8, "WEBP")) return "image/webp";
  if (texto(0, "RIFF") && texto(8, "WAVE")) return "audio/wav";
  if (texto(0, "%PDF-")) return "application/pdf";
  if (b.length >= 12 && texto(4, "ftyp")) return ext === "m4a" ? "audio/mp4" : texto(8, "qt  ") ? "video/quicktime" : "video/mp4";
  if (empieza(0x1a, 0x45, 0xdf, 0xa3)) return "video/webm";
  if (texto(0, "OggS")) return ext === "ogv" ? "video/ogg" : "audio/ogg";
  if (texto(0, "ID3") || (b[0] === 0xff && [0xfb, 0xf3, 0xf2].includes(b[1]))) return "audio/mpeg";
  if (texto(0, "wOF2")) return "font/woff2";
  if (texto(0, "wOFF")) return "font/woff";
  return POR_EXTENSION[ext] ?? "application/octet-stream";
}
export const tipoImagen = (bytes) => { const t = tipoDe(bytes); return t.startsWith("image/") ? t : null; };

export const clase = (tipo) => (tipo.startsWith("image/") ? "imagen" : tipo.startsWith("video/") ? "video" : tipo.startsWith("audio/") ? "audio" : tipo === "application/pdf" ? "pdf"
  : /officedocument|msword|ms-excel|ms-powerpoint|opendocument|rtf/.test(tipo) ? "documento" : "otro");

export function formatoBytes(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 ** 2) return `${(n / 1024).toFixed(0)} KB`;
  if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1)} MB`;
  return `${(n / 1024 ** 3).toFixed(2)} GB`;
}

/** Rutas de los archivos binarios del proyecto y lo que ocupan (cada contenido se cuenta una vez). */
export function archivosDe(py) {
  const rutas = [];
  const unicos = new Map();
  for (const [ruta, texto] of Object.entries(py.files)) {
    const m = leerMarcador(texto);
    if (!m) continue;
    rutas.push(ruta);
    unicos.set(m.hash, m.tamano);
  }
  return { rutas, bytes: [...unicos.values()].reduce((a, b) => a + b, 0) };
}

const leerCsrf = () => (typeof document === "undefined" ? "" : (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "");
const tamanoDe = (d) => (d instanceof Blob ? d.size : d.byteLength);

/** Habla con /api/trabajo/archivos/. */
/** Blob → data:URL sin FileReader (por partes, para no reventar la pila con archivos de varios MB). */
async function aDataUrl(blob) {
  const b = new Uint8Array(await blob.arrayBuffer());
  let bin = "";
  for (let i = 0; i < b.length; i += 0x8000) bin += String.fromCharCode.apply(null, b.subarray(i, i + 0x8000));
  return `data:${blob.type || "application/octet-stream"};base64,${btoa(bin)}`;
}

export class ClienteArchivos {
  constructor({ fetchFn = (...a) => fetch(...a), csrf = leerCsrf, usarXhr = typeof XMLHttpRequest === "function", reintentos = 8, pausa = 2000 } = {}) {
    Object.assign(this, { fetchFn, csrf, usarXhr, reintentos, pausa });
    this.cache = new Map(); // hash -> Promise<Blob> (solo archivos pequeños)
    this.enlacesCache = new Map(); // hash -> { url, vence }
    this.uso = null; // { uso, limite, max_archivo }
  }

  #esperar(intento) { return new Promise((ok) => setTimeout(ok, Math.min(30000, this.pausa * intento))); }

  get maxArchivo() { return this.uso?.max_archivo ?? LIMITES_ARCHIVO.porArchivo; }

  async #json(r) {
    const datos = await r.json().catch(() => ({}));
    if (!r.ok) {
      const e = new Error(datos.error || (r.status === 401 ? "Tu sesión venció: recarga la página." : r.status === 413 ? "El archivo es demasiado grande." : r.status >= 500 ? `Error del servidor (${r.status}). Si acabas de actualizar CódigoCamp, reinicia Flask; si sigue, revisa la terminal donde corre.` : `El servidor respondió ${r.status}.`));
      e.estado = r.status;
      throw e;
    }
    return datos;
  }

  #enviarXhr(url, datos, progreso) {
    return new Promise((ok, mal) => {
      const x = new XMLHttpRequest();
      x.open("POST", url);
      x.setRequestHeader("Content-Type", "application/octet-stream");
      x.setRequestHeader("X-CSRFToken", this.csrf());
      x.upload.onprogress = (e) => { if (e.lengthComputable) progreso(e.loaded / e.total); };
      x.onload = () => ok({ ok: x.status < 400, status: x.status, json: async () => JSON.parse(x.responseText || "{}") });
      x.onerror = () => mal(new TypeError("red"));
      x.send(datos);
    });
  }

  /**
   * Sube un archivo (Uint8Array o Blob/File: un File de 1 GB no se carga en memoria) y devuelve su marcador.
   * @param {{ nombre?: string, progreso?: (fraccion:number)=>void }} [o]
   */
  /** Con la carpeta de tu equipo abierta, los archivos (imágenes, videos…) quedan en la memoria de esta pestaña y en
   *  tu equipo: no se suben a tu cuenta. */
  modoLocal(si) {
    if (si) { this.local = this.local || new Map(); return; }
    for (const x of this.local?.values() || []) if (x.url) URL.revokeObjectURL(x.url);
    this.local = null;
  }

  async #subirLocal(datos, nombre) {
    const blob = datos instanceof Blob ? datos : new Blob([datos]);
    const cabeza = new Uint8Array(await blob.slice(0, 64).arrayBuffer());
    const huella = blob.size <= 256 * 1024 * 1024 ? await crypto.subtle.digest("SHA-256", await blob.arrayBuffer())
      : await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`${nombre}:${blob.size}:${Math.random()}`));
    const hash = [...new Uint8Array(huella)].map((b) => b.toString(16).padStart(2, "0")).join("");
    const tipo = tipoDe(cabeza, nombre);
    this.local.set(hash, { blob: new Blob([blob], { type: tipo }) });
    return crearMarcador({ hash, tipo, tamano: blob.size });
  }

  async subir(datos, { nombre = "", progreso = () => {} } = {}) {
    if (this.local) return this.#subirLocal(datos, nombre);
    const tamano = tamanoDe(datos);
    if (!tamano) throw new Error("El archivo está vacío.");
    if (tamano > this.maxArchivo) throw new Error(`Pesa ${formatoBytes(tamano)}: el máximo por archivo es ${formatoBytes(this.maxArchivo)}.`);
    const url = `/api/trabajo/archivos/?nombre=${encodeURIComponent(nombre.split("/").pop() || "")}`;
    let r;
    for (let intento = 1; ; intento += 1) {
      try {
        r = this.usarXhr ? await this.#enviarXhr(url, datos, progreso)
          : await this.fetchFn(url, { method: "POST", credentials: "same-origin", body: datos, headers: { "Content-Type": "application/octet-stream", "X-CSRFToken": this.csrf() } });
      } catch {
        if (intento < this.reintentos) { await this.#esperar(intento); continue; }
        throw new Error("Sin conexión con el servidor: los archivos necesitan internet para subirse.");
      }
      // Demasiadas subidas seguidas o un corte del servidor: se espera y se reintenta (no se pierde el archivo).
      if ((r.status === 429 || r.status === 502 || r.status === 503) && intento < this.reintentos) { await this.#esperar(intento); continue; }
      break;
    }
    const j = await this.#json(r);
    this.uso = { uso: j.uso, limite: j.limite, max_archivo: j.max_archivo };
    if (tamano <= 20 * 1024 * 1024) this.cache.set(j.hash, Promise.resolve(datos instanceof Blob ? datos : new Blob([datos])));
    return j.marcador;
  }

  async consultarUso() {
    const j = await this.#json(await this.fetchFn("/api/trabajo/archivos/", { credentials: "same-origin" }));
    this.uso = { uso: j.uso, limite: j.limite, max_archivo: j.max_archivo };
    return this.uso;
  }

  /** Contenido de un archivo como Blob (los grandes, el navegador los guarda en disco, no en memoria). */
  blob(marcador) {
    const m = leerMarcador(marcador);
    if (!m) return Promise.reject(new Error("No es un archivo guardado en la cuenta."));
    if (this.local?.has(m.hash)) return Promise.resolve(this.local.get(m.hash).blob);
    if (this.cache.has(m.hash)) return this.cache.get(m.hash);
    const p = this.fetchFn(`/api/trabajo/archivos/${m.hash}`, { credentials: "same-origin" }).then(async (r) => {
      if (!r.ok) throw new Error(r.status === 404 ? "El archivo ya no está en tu cuenta." : `No se pudo descargar (${r.status}).`);
      return r.blob();
    });
    if (m.tamano <= 20 * 1024 * 1024) { this.cache.set(m.hash, p); p.catch(() => this.cache.delete(m.hash)); }
    return p;
  }

  async bytes(marcador) { return new Uint8Array(await (await this.blob(marcador)).arrayBuffer()); }

  /** URL para la página principal (usa la sesión). */
  url(marcador, { descargar = false, nombre = "" } = {}) {
    const m = leerMarcador(marcador);
    if (!m) return null;
    const x = this.local?.get(m.hash);
    if (x) { x.url ||= URL.createObjectURL(x.blob); return x.url; }
    const q = new URLSearchParams();
    if (descargar) q.set("descargar", "1");
    if (nombre) q.set("nombre", nombre);
    return `/api/trabajo/archivos/${m.hash}${q.size ? `?${q}` : ""}`;
  }

  /** Enlaces temporales para la vista previa aislada (que no envía la sesión). Map hash → URL. */
  async enlaces(py) {
    if (this.local) {   // vista previa con archivos de tu equipo: se pasan como data: (la vista previa está aislada)
      const m = new Map();
      for (const x of Object.values(py.files).map(leerMarcador).filter(Boolean)) {
        const l = this.local.get(x.hash);
        if (l && !m.has(x.hash)) m.set(x.hash, l.blob.size <= 12 * 1024 * 1024 ? await aDataUrl(l.blob) : (l.url ||= URL.createObjectURL(l.blob)));
      }
      return m;
    }
    const ahora = Date.now();
    const hashes = [...new Set(Object.values(py.files).map(leerMarcador).filter(Boolean).map((m) => m.hash))];
    const faltan = hashes.filter((h) => !(this.enlacesCache.get(h)?.vence > ahora));
    if (faltan.length) {
      try {
        const r = await this.fetchFn("/api/trabajo/archivos/enlaces/", {
          method: "POST", credentials: "same-origin", body: JSON.stringify({ hashes: faltan }),
          headers: { "Content-Type": "application/json", "X-CSRFToken": this.csrf() },
        });
        const j = await this.#json(r);
        const vence = ahora + (j.vigencia - 600) * 1000;
        for (const [h, url] of Object.entries(j.enlaces)) this.enlacesCache.set(h, { url, vence });
      } catch { /* sin conexión: se verán rotos */ }
    }
    return new Map(hashes.filter((h) => this.enlacesCache.has(h)).map((h) => [h, this.enlacesCache.get(h).url]));
  }
}
