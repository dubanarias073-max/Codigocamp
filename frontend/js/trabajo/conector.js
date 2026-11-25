// Terminal «Mi equipo»: los comandos se ejecutan DE VERDAD en tu computador o celular, a través del Conector de
// CódigoCamp (frontend/descargas/codigocamp-conector.py) que abres tú en ese equipo. Ver backend/rutas/conector.py.
// La salida llega en vivo; lo que escribes mientras un programa corre va a su entrada (input(), Scanner, readline…)
// y Ctrl+C lo detiene. Sin el Conector abierto, nada de esto funciona: tú decides cuándo está conectado.
import { api } from "/js/app.js";
import { ErrorEquipo } from "./equipo.js";

const pausa = (ms) => new Promise((r) => setTimeout(r, ms));

/** Une una ruta relativa a la carpeta del equipo (siempre con «/», sin salirse de ella). */
export function unirRuta(cwd, destino) {
  const partes = (destino.startsWith("/") || destino.startsWith("~") ? [] : String(cwd || "").split("/")).filter(Boolean);
  for (const p of String(destino).replace(/\\/g, "/").replace(/^~\/?/, "").split("/")) {
    if (!p || p === ".") continue;
    if (p === "..") partes.pop(); else partes.push(p);
  }
  return partes.join("/");
}

export class ShellRemoto {
  /** @param {{id:number, equipo:string, sistema:string, carpeta:string}} equipo */
  constructor(equipo) {
    this.equipo = equipo;
    this.usuario = equipo.equipo;
    this.remoto = true;
    this.windows = /windows/i.test(equipo.sistema || "");
  }

  nuevaSesion(extra = {}) {
    return { cwd: "", anterior: "", historial: [], vars: { "?": 0 }, columnas: 100, senal: undefined,
      out: () => {}, err: () => {}, leerLinea: async () => null, limpiar: () => {}, cerrar: () => {}, ...extra };
  }

  incompleta() { return false; }
  completar() { return { desde: 0, opciones: [] }; }

  /** Texto del prompt: equipo ➜ carpeta $ */
  prompt(sesion) {
    const base = (this.equipo.carpeta || "").replace(/\\/g, "/").split("/").filter(Boolean).pop() || "carpeta";
    return `\x1b[35m🖥 ${this.equipo.equipo} \x1b[0m➜ \x1b[1;34m${base}${sesion.cwd ? "/" + sesion.cwd : ""}\x1b[0m ${this.windows ? ">" : "$"} `;
  }

  async ejecutar(linea, sesion) {
    const l = linea.trim();
    if (!l) return 0;
    if (/^(clear|cls)$/.test(l)) { sesion.limpiar(); return 0; }
    if (/^exit$/.test(l)) { sesion.cerrar(); return 0; }
    // cd: cada comando corre en su propio proceso, así que la carpeta actual la recuerda Trabajo (y se comprueba en el equipo)
    const cd = l.match(/^cd(?:\s+(?:\/d\s+)?([^&|;<>`$]+))?$/i);   // solo «cd carpeta» (lo compuesto corre tal cual en el equipo)
    if (cd) {
      const destino = (cd[1] || "").trim().replace(/^["']|["']$/g, "");
      const nueva = destino ? unirRuta(sesion.cwd, destino) : "";
      const prueba = this.windows ? `cd /d "${nueva || "."}"` : `cd "${nueva || "."}"`;
      const codigo = await this.#correr(prueba, { ...sesion, cwd: "", out: () => {} });
      if (codigo !== 0) { sesion.err(`cd: ${destino}: no existe esa carpeta\n`); return 1; }
      sesion.cwd = nueva;
      return 0;
    }
    return this.#correr(linea, sesion);
  }

  async #correr(linea, sesion) {
    let orden;
    try {
      ({ orden } = await api(`/api/conector/${this.equipo.id}/ejecutar`, { linea, cwd: sesion.cwd, columnas: sesion.columnas || 100 }));
    } catch (e) {
      sesion.err(`\x1b[31m${e.message}\x1b[0m\n`);
      return 1;
    }
    let detenido = false;
    const detener = () => { if (!detenido) { detenido = true; api(`/api/conector/orden/${orden}/detener`, {}).catch(() => {}); } };
    sesion.senal?.addEventListener("abort", detener, { once: true });
    // Lo que escribes mientras corre va a la entrada del programa
    let leyendo = true;
    (async () => {
      while (leyendo) {
        const v = await sesion.leerLinea("");
        if (!leyendo) break;
        if (v === null) { detener(); break; }
        api(`/api/conector/orden/${orden}/entrada`, { texto: v + "\n" }).catch(() => {});
      }
    })();
    let desde = 0, fallos = 0, codigo = 0;
    for (;;) {
      let r;
      try {
        r = await api(`/api/conector/orden/${orden}?desde=${desde}`);
        fallos = 0;
      } catch (e) {
        if (++fallos > 4) { sesion.err(`\n\x1b[31m${e.message}\x1b[0m\n`); codigo = 1; break; }
        await pausa(800 * fallos);
        continue;
      }
      if (r.texto) sesion.out(r.texto.replace(/\r\n/g, "\n"));
      desde = r.desde;
      if (r.fin) { codigo = r.codigo ?? 0; break; }
    }
    leyendo = false;
    sesion.cancelarLectura?.();
    return detenido && codigo !== 0 ? 130 : codigo;
  }
}

/** Equipos conectados de esta cuenta. */
/** Nombre del archivo del Conector: lleva la versión (codigocamp-conector-v3.py) para que nunca abras uno anterior que
 *  quedó en Descargas (el navegador guardaría el nuevo como «codigocamp-conector (1).py»). */
export let archivoConector = "codigocamp-conector-v5.py";
export async function listarEquipos() {
  try {
    const r = await api("/api/conector/");
    if (r.archivo) archivoConector = r.archivo;
    return r.equipos || [];
  } catch { return []; }
}

/** Espera una orden hasta que termine y devuelve { texto, codigo, datos }. */
export async function esperarOrden(orden) {
  let desde = 0, texto = "";
  for (;;) {
    const r = await api(`/api/conector/orden/${orden}?desde=${desde}`);
    texto += r.texto || "";
    desde = r.desde;
    if (r.fin) return { texto, codigo: r.codigo, datos: r.datos };
  }
}

/** Copia los archivos del proyecto de Trabajo a la carpeta del equipo. */
export async function enviarProyecto(equipo, archivos) {
  const { orden } = await api(`/api/conector/${equipo.id}/enviar`, { archivos });
  return esperarOrden(orden);
}

/** Lee los archivos de la carpeta del equipo (texto o «ccb64:…» para binarios). */
export async function traerCarpeta(equipo) {
  const { orden } = await api(`/api/conector/${equipo.id}/traer`, {});
  return esperarOrden(orden);
}

// ----------------------------------------------------- carpeta del equipo abierta en Trabajo (como un editor) ----
export { DiscoConector, ErrorEquipo, leerEstadoGit, bytesABase64, base64ABytes } from "./equipo.js";

/** Una operación de archivos o Git en el equipo. Devuelve los datos que respondió el Conector. */
export async function fsEquipo(equipo, accion, datos = {}) {
  let orden, resultado;
  try { ({ orden, resultado } = await api(`/api/conector/${equipo.id}/fs`, { accion, ...datos })); }
  catch (e) { throw new ErrorEquipo(e.message, { desconectado: /no está conectado|409/.test(e.message) || e.status === 409 }); }
  // El servidor ya suele traer la respuesta en la misma petición; si tardó más, se espera como antes
  const r = resultado ? { texto: resultado.texto || "", codigo: resultado.codigo, datos: resultado.datos } : await esperarOrden(orden);
  if (r.codigo === 255) throw new ErrorEquipo(`«${equipo.equipo}» se desconectó. Abre el Conector otra vez.`, { desconectado: true });
  if (r.codigo !== 0) throw new ErrorEquipo(r.datos?.error || r.texto.trim() || "El equipo no pudo hacerlo.", r.datos || {});
  return r.datos || {};
}

/** Git real del equipo (sin pasar por una shell). Devuelve { codigo, salida, error }. */
export function gitEquipo(equipo, args, cwd = "") {
  return fsEquipo(equipo, "git", { args, cwd });
}

