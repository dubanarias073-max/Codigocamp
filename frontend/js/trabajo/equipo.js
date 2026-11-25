// La carpeta del computador o celular del estudiante abierta en Trabajo (a través del Conector), sin depender de la
// página: así se prueba con Node. Las llamadas al servidor están en conector.js (fsEquipo).
import { CARPETAS_IGNORADAS } from "./importar.js";

/** Error del equipo con su motivo en español (y si fue un virus, si se desconectó…). */
export class ErrorEquipo extends Error {
  constructor(mensaje, datos = {}) { super(mensaje); Object.assign(this, datos); this.name = datos.desconectado ? "EquipoDesconectado" : "ErrorEquipo"; }
}

export function bytesABase64(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
export function base64ABytes(b64) {
  const s = atob(b64 || "");
  const out = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i);
  return out;
}
const nombreDe = (ruta) => String(ruta || "").replace(/[\\/]+$/, "").split(/[\\/]/).pop() || ruta;

/**
 * Disco con la misma forma que DiscoNavegador (carpeta.js), pero la carpeta está en el computador o celular del
 * estudiante y se maneja a través del Conector. Así el Sincronizador mantiene igual el proyecto y la carpeta.
 */
const PARTE = 8 * 1024 * 1024;

// Rápido al moverte entre carpetas del mismo equipo (proyecto → carpeta de arriba → otra vez el proyecto): lo que ya se
// trajo se recuerda por su ruta completa en el equipo, su tamaño y su fecha; si no cambió, no se vuelve a pedir.
const MEMORIA = new Map();   // "equipo|/ruta/completa" -> { tamano, modificado, b64 }
const MAX_MEMORIA = 96 * 1024 * 1024;
let pesoMemoria = 0;
const unir = (carpeta, ruta) => (String(carpeta || "").replace(/\\/g, "/").replace(/\/+$/, "") + "/" + ruta);
function recordar(clave, valor) {
  const viejo = MEMORIA.get(clave);
  if (viejo) { pesoMemoria -= viejo.b64.length; MEMORIA.delete(clave); }
  if (valor.b64.length > 4 * 1024 * 1024) return;
  MEMORIA.set(clave, valor); pesoMemoria += valor.b64.length;
  for (const [k, v] of MEMORIA) { if (pesoMemoria <= MAX_MEMORIA) break; MEMORIA.delete(k); pesoMemoria -= v.b64.length; }
}

export class DiscoConector {
  /** @param {(equipo, accion, datos) => Promise<object>} fs   fsEquipo de conector.js (o uno falso en las pruebas) */
  constructor(equipo, carpeta, fs) {
    this.fs = (accion, datos) => fs(this.equipo, accion, datos);
    this.equipo = equipo;
    this.carpeta = carpeta;
    this.nombre = nombreDe(carpeta);
    this.esEquipo = true;
    this.alVirus = null;       // (ruta, mensaje) cuando el antivirus del equipo bloquea un archivo
    this.avisados = new Set();
  }

  async listar() {
    const d = await this.fs("listar", { ignorar: [...CARPETAS_IGNORADAS] });
    this.raizReal = typeof d.carpeta === "string" ? d.carpeta : null;   // la carpeta que el equipo listó de verdad (Conector nuevo)
    return { archivos: d.archivos || [], carpetas: d.carpetas || [] };
  }

  /** Trae en pocos viajes los archivos que el Sincronizador va a leer ([{ ruta, tamano }]). */
  async precargar(lista) {
    this.precargados = new Map();
    let lote = [], peso = 0;
    const info = new Map(lista.map((a) => [a.ruta, a]));
    const raiz = this.raizReal;   // sin ella (Conector viejo) no se usa la memoria: nunca se mezclan archivos de otra carpeta
    const clave = (ruta) => `${this.equipo?.id}|${unir(raiz, ruta)}`;
    const pedir = async () => {
      if (!lote.length) return;
      const r = await this.fs("leer_varios", { rutas: lote });
      for (const [ruta, d] of Object.entries(r.archivos || {})) {
        this.precargados.set(ruta, d);
        const a = info.get(ruta);
        if (raiz && r.carpeta === raiz && a && d.b64 !== undefined && a.modificado !== undefined) recordar(clave(ruta), { tamano: a.tamano, modificado: a.modificado, b64: d.b64 });
      }
      lote = []; peso = 0;
    };
    for (const a of lista) {
      const m = raiz ? MEMORIA.get(clave(a.ruta)) : null;
      if (m && m.tamano === a.tamano && m.modificado === a.modificado) { this.precargados.set(a.ruta, { b64: m.b64 }); continue; }
      if (a.tamano > 8 * 1024 * 1024) continue; // los grandes se piden solos
      if (lote.length >= 300 || peso + a.tamano > 8 * 1024 * 1024) await pedir();
      lote.push(a.ruta); peso += a.tamano;
    }
    await pedir();
  }

  async leer(ruta) {
    const pre = this.precargados?.get(ruta);
    if (pre) {
      this.precargados.delete(ruta);
      if (pre.b64 !== undefined) return base64ABytes(pre.b64);
      if (pre.virus && !this.avisados.has(ruta)) { this.avisados.add(ruta); this.alVirus?.(ruta, pre.error); }
      throw new ErrorEquipo(pre.error || "No se pudo leer", pre);
    }
    try { return base64ABytes((await this.fs("leer", { ruta })).b64); }
    catch (e) {
      if (e.virus && !this.avisados.has(ruta)) { this.avisados.add(ruta); this.alVirus?.(ruta, e.message); }
      throw e;
    }
  }

  /** Archivo completo como Blob; los grandes (hasta 1 GB) llegan por partes de 8 MB. */
  async abrir(ruta) {
    try { return new Blob([await this.leer(ruta)]); }
    catch (e) { if (!e.grande) throw e; }
    const partes = [];
    let desde = 0;
    for (;;) {
      let r;
      try { r = await this.fs("leer_parte", { ruta, desde }); }
      catch (e) { if (e.virus && !this.avisados.has(ruta)) { this.avisados.add(ruta); this.alVirus?.(ruta, e.message); } throw e; }
      const b = base64ABytes(r.b64);
      partes.push(b);
      desde += b.length;
      this.alProgreso?.(ruta, desde, r.total);
      if (r.fin || !b.length) break;
    }
    return new Blob(partes);
  }

  async escribir(ruta, datos) {
    const blob = datos instanceof Blob ? datos : new Blob([datos]);
    if (blob.size <= PARTE) {
      const r = await this.fs("escribir", { ruta, b64: bytesABase64(new Uint8Array(await blob.arrayBuffer())) });
      return { tamano: r.tamano, modificado: r.modificado };
    }
    // Grande: por partes (el archivo se arma en un temporal del equipo y se reemplaza al final)
    let r = null;
    for (let desde = 0; desde < blob.size; desde += PARTE) {
      const trozo = new Uint8Array(await blob.slice(desde, desde + PARTE).arrayBuffer());
      r = await this.fs("escribir_parte", { ruta, desde, b64: bytesABase64(trozo), fin: desde + PARTE >= blob.size });
      this.alProgreso?.(ruta, Math.min(blob.size, desde + PARTE), blob.size);
    }
    return { tamano: r.tamano, modificado: r.modificado };
  }

  async crearCarpeta(ruta) { await this.fs("carpeta", { ruta }); }
  async borrar(ruta) { await this.fs("borrar", { ruta }); }
  async permiso() { return "granted"; }
}

/**
 * «git status --porcelain=v1 -b -z» → { rama, seguimiento, adelante, atras, cambios: [{ ruta, x, y, de? }] }.
 * x = estado en el área de preparación, y = en la carpeta («?» = sin seguimiento).
 */
export function leerEstadoGit(salida) {
  const partes = String(salida || "").split("\0");
  const r = { rama: "", seguimiento: "", adelante: 0, atras: 0, cambios: [] };
  for (let i = 0; i < partes.length; i++) {
    const p = partes[i];
    if (!p) continue;
    if (p.startsWith("## ")) {
      const cab = p.slice(3);
      const m = /^(?:No commits yet on |Initial commit on |No hay commits todavía en )?([^.\s]+(?:\.(?!\.)[^.\s]+)*)(?:\.\.\.(\S+))?(?: \[(.*)\])?/.exec(cab);
      if (m) {
        r.rama = m[1];
        r.seguimiento = m[2] || "";
        const ad = /(?:ahead|adelante) (\d+)/.exec(m[3] || ""); const at = /(?:behind|detrás) (\d+)/.exec(m[3] || "");
        r.adelante = ad ? Number(ad[1]) : 0; r.atras = at ? Number(at[1]) : 0;
      }
      continue;
    }
    const x = p[0], y = p[1], ruta = p.slice(3);
    const c = { ruta, x, y };
    if (x === "R" || x === "C") c.de = partes[++i];
    r.cambios.push(c);
  }
  return r;
}
export const memoriaEquipo = () => ({ archivos: MEMORIA.size, peso: pesoMemoria, ejemplo: [...MEMORIA.keys()][0] });
