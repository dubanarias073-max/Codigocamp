// Imágenes del proyecto.
//
// El proyecto solo guarda texto, así que una imagen vive en dos partes:
//  · en el proyecto, un «marcador» de texto en la ruta del archivo:  ccimg:v1:<sha256>:<tipo>:<bytes>
//  · en la cuenta (servidor), los bytes, guardados por su huella SHA-256 (backend/rutas/imagenes.py).
// Como el marcador es texto, mover, copiar, borrar, deshacer y Git funcionan igual que con cualquier archivo.
// Los límites repiten los del servidor: si cambian allá, deben cambiar aquí.

export const LIMITES_IMAGEN = { porImagen: 5 * 1024 * 1024, porCuenta: 20 * 1024 * 1024 };
export const EXT_IMAGEN = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp" };

const MARCADOR = /^ccimg:v1:([a-f0-9]{64}):(image\/(?:png|jpeg|gif|webp)):(\d{1,9})$/;

export const esMarcador = (texto) => typeof texto === "string" && texto.startsWith("ccimg:") && MARCADOR.test(texto);
export function leerMarcador(texto) {
  const m = typeof texto === "string" ? MARCADOR.exec(texto) : null;
  return m ? { hash: m[1], tipo: m[2], tamano: Number(m[3]) } : null;
}
export const crearMarcador = ({ hash, tipo, tamano }) => `ccimg:v1:${hash}:${tipo}:${tamano}`;

/** Tipo según los primeros bytes (igual que el servidor), o null si no es PNG/JPEG/GIF/WebP. */
export function tipoImagen(bytes) {
  const b = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  const empieza = (...f) => f.every((v, i) => b[i] === v);
  if (empieza(0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a)) return "image/png";
  if (empieza(0xff, 0xd8, 0xff)) return "image/jpeg";
  if (empieza(0x47, 0x49, 0x46, 0x38) && (b[4] === 0x37 || b[4] === 0x39) && b[5] === 0x61) return "image/gif";
  if (b.length >= 12 && empieza(0x52, 0x49, 0x46, 0x46) && b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50) return "image/webp";
  return null;
}

export const formatoBytes = (n) => (n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1048576).toFixed(1)} MB`);

/** Rutas de las imágenes del proyecto y lo que ocupan (contando cada imagen una sola vez). */
export function imagenesDe(py) {
  const rutas = [];
  const unicas = new Map();
  for (const [ruta, texto] of Object.entries(py.files)) {
    const m = leerMarcador(texto);
    if (!m) continue;
    rutas.push(ruta);
    unicas.set(m.hash, m.tamano);
  }
  return { rutas, bytes: [...unicas.values()].reduce((a, b) => a + b, 0) };
}

function base64(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
export const dataUrl = (tipo, bytes) => `data:${tipo};base64,${base64(bytes)}`;

const leerCsrf = () => (typeof document === "undefined" ? "" : (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "");

/** Habla con /api/trabajo/imagenes/. Guarda en memoria los bytes ya descargados. */
export class ClienteImagenes {
  constructor({ fetchFn = (...a) => fetch(...a), csrf = leerCsrf } = {}) {
    Object.assign(this, { fetchFn, csrf });
    this.cache = new Map(); // hash -> Promise<Uint8Array>
    this.uso = null; // { uso, limite, max_imagen } según la última respuesta del servidor
  }

  async #json(r) {
    const datos = await r.json().catch(() => ({}));
    if (!r.ok) {
      const e = new Error(datos.error || (r.status === 401 ? "Tu sesión venció: recarga la página." : `El servidor respondió ${r.status}.`));
      e.estado = r.status;
      throw e;
    }
    return datos;
  }

  /** Sube los bytes de una imagen y devuelve su marcador. Lanza Error con mensaje en español si no se puede. */
  async subir(bytes) {
    const datos = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
    if (!tipoImagen(datos)) throw new Error("Solo se aceptan imágenes PNG, JPG, GIF o WebP.");
    if (datos.length > LIMITES_IMAGEN.porImagen) throw new Error(`Pesa ${formatoBytes(datos.length)}: el máximo por imagen es 5 MB.`);
    let r;
    try {
      r = await this.fetchFn("/api/trabajo/imagenes/", {
        method: "POST", credentials: "same-origin", body: datos,
        headers: { "Content-Type": "application/octet-stream", "X-CSRFToken": this.csrf() },
      });
    } catch {
      throw new Error("Sin conexión con el servidor: las imágenes necesitan internet para subirse.");
    }
    const j = await this.#json(r);
    this.uso = { uso: j.uso, limite: j.limite, max_imagen: j.max_imagen };
    this.cache.set(j.hash, Promise.resolve(datos));
    return j.marcador;
  }

  async consultarUso() {
    const j = await this.#json(await this.fetchFn("/api/trabajo/imagenes/", { credentials: "same-origin" }));
    this.uso = { uso: j.uso, limite: j.limite, max_imagen: j.max_imagen };
    return this.uso;
  }

  /** Bytes de una imagen (desde la memoria o el servidor). */
  bytes(marcador) {
    const m = leerMarcador(marcador);
    if (!m) return Promise.reject(new Error("No es una imagen."));
    if (!this.cache.has(m.hash)) {
      const p = this.fetchFn(`/api/trabajo/imagenes/${m.hash}`, { credentials: "same-origin" }).then(async (r) => {
        if (!r.ok) throw new Error(r.status === 404 ? "La imagen ya no está en tu cuenta." : `No se pudo descargar la imagen (${r.status}).`);
        return new Uint8Array(await r.arrayBuffer());
      });
      p.catch(() => this.cache.delete(m.hash));
      this.cache.set(m.hash, p);
    }
    return this.cache.get(m.hash);
  }

  /** URL utilizable en la página principal (no en la vista previa aislada, que no envía la sesión). */
  url(marcador) {
    const m = leerMarcador(marcador);
    return m ? `/api/trabajo/imagenes/${m.hash}` : null;
  }

  /** data: URL de cada imagen del proyecto (para la vista previa). Las que fallan se omiten. */
  async dataUrls(py) {
    const salida = new Map();
    await Promise.all(Object.values(py.files).filter(esMarcador).map(async (t) => {
      const m = leerMarcador(t);
      if (salida.has(m.hash)) return;
      try { salida.set(m.hash, dataUrl(m.tipo, await this.bytes(t))); } catch { /* se verá como imagen rota */ }
    }));
    return salida;
  }
}
