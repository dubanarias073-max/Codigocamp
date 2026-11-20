// Copiloto de Trabajo (como Copilot en VS Code): la IA ve tu proyecto y, si lo permites, propone cambios en tus
// archivos. Nada se aplica solo: ves las diferencias de cada archivo y aceptas o rechazas uno por uno (o todos).
import * as FS from "./fs.js";
import { esMarcador } from "./archivos.js";

export const MAX_CAMBIOS = 40;
const MAX_CONTENIDO = 1024 * 1024;
const PRESUPUESTO = 150_000; // caracteres de proyecto que se mandan como contexto

/** Separa la respuesta de la IA del bloque ```cc-cambios```. Devuelve { texto, cambios, resumen, error }. */
export function extraerCambios(respuesta) {
  const m = /```cc-cambios\s*\n([\s\S]*?)\n```/.exec(respuesta || "");
  if (!m) return { texto: respuesta, cambios: null };
  const texto = (respuesta.slice(0, m.index) + respuesta.slice(m.index + m[0].length)).trim();
  let datos;
  try { datos = JSON.parse(m[1]); } catch (e) { return { texto, cambios: null, error: "La IA propuso cambios pero en un formato que no se pudo leer. Pídele que lo intente otra vez." }; }
  const lista = Array.isArray(datos) ? datos : datos?.cambios;
  if (!Array.isArray(lista)) return { texto, cambios: null, error: "La propuesta de cambios no tiene archivos." };
  return { texto, cambios: lista, resumen: typeof datos?.resumen === "string" ? datos.resumen.slice(0, 300) : "" };
}

/** Valida los cambios contra el proyecto. Devuelve { validos: [{accion, ruta, contenido, antes, nuevo}], errores: [texto] } */
export function validarCambios(cambios, py) {
  const validos = [], errores = [];
  const vistos = new Set();
  for (const c of (cambios || []).slice(0, MAX_CAMBIOS)) {
    const cruda = typeof c?.ruta === "string" ? c.ruta.replace(/^\/?workspace\//, "").replace(/^\.\//, "") : "";
    const ruta = cruda && !cruda.split("/").includes("..") ? FS.resolver("", cruda) : null;
    if (!ruta || ruta.split("/").includes(".git")) { errores.push(`Ruta no válida: ${String(c?.ruta).slice(0, 80)}`); continue; }
    if (vistos.has(ruta)) { errores.push(`${ruta} aparece dos veces`); continue; }
    vistos.add(ruta);
    const antes = py.files[ruta];
    if (c.accion === "borrar") {
      if (antes === undefined) { errores.push(`${ruta} no existe (no hace falta borrarlo)`); continue; }
      validos.push({ accion: "borrar", ruta, antes, nuevo: false });
    } else if (c.accion === "escribir" || c.accion === "crear" || c.accion === "modificar") {
      if (typeof c.contenido !== "string") { errores.push(`${ruta}: falta el contenido`); continue; }
      if (c.contenido.length > MAX_CONTENIDO) { errores.push(`${ruta}: el contenido es demasiado grande`); continue; }
      if (esMarcador(antes)) { errores.push(`${ruta} es un archivo binario (imagen, video…); la IA no puede reescribirlo`); continue; }
      if (FS.esCarpeta(py, ruta)) { errores.push(`${ruta} es una carpeta`); continue; }
      if (antes === c.contenido) continue;
      validos.push({ accion: "escribir", ruta, contenido: c.contenido, antes: antes ?? null, nuevo: antes === undefined });
    } else errores.push(`${ruta}: acción desconocida «${String(c?.accion).slice(0, 20)}»`);
  }
  if ((cambios || []).length > MAX_CAMBIOS) errores.push(`Solo se revisan los primeros ${MAX_CAMBIOS} archivos.`);
  return { validos, errores };
}

/** Aplica un cambio validado. Devuelve { ok, error, deshacer() } */
export function aplicarCambio(py, c) {
  if (c.accion === "borrar") {
    const antes = py.files[c.ruta];
    const r = FS.borrar ? FS.borrar(py, c.ruta) : (delete py.files[c.ruta], { ok: true });
    return { ...r, deshacer: () => { if (antes !== undefined) FS.crearArchivo(py, c.ruta, antes, { padres: FS.carpetaDe(c.ruta) !== "" }); } };
  }
  const antes = py.files[c.ruta];
  const r = antes !== undefined ? FS.escribirArchivo(py, c.ruta, c.contenido) : FS.crearArchivo(py, c.ruta, c.contenido, { padres: FS.carpetaDe(c.ruta) !== "" });
  return { ...r, deshacer: () => { if (antes === undefined) delete py.files[c.ruta]; else FS.escribirArchivo(py, c.ruta, antes); } };
}

/**
 * Contexto del proyecto para la IA: el archivo abierto, la selección, la lista de archivos y (en modo copiloto) el
 * contenido de los archivos de texto más relevantes, hasta un presupuesto.
 */
export function contextoProyecto(py, { abierto = null, abiertos = [], seleccion = "", problemas = [], terminal = "", copiloto = false } = {}) {
  const textos = Object.entries(py.files).filter(([r, t]) => !esMarcador(t) && !/(^|\/)(node_modules|\.git|dist|build|__pycache__)\//.test(r) && !/package-lock\.json$|\.min\.(js|css)$|\.map$/.test(r));
  const ctx = {
    pagina: "Trabajo (espacio de código tipo VS Code)",
    archivos: Object.keys(py.files).filter((r) => !/(^|\/)(node_modules|\.git)\//.test(r)).sort().slice(0, 500),
    copiloto,
  };
  if (abierto && py.files[abierto] !== undefined) ctx.archivo = { ruta: abierto, contenido: esMarcador(py.files[abierto]) ? "(archivo binario: imagen, video, PDF…)" : py.files[abierto].slice(0, 80_000) };
  if (seleccion) ctx.seleccion = seleccion.slice(0, 20_000);
  if (problemas.length) ctx.problemas = problemas.slice(0, 40);
  if (terminal) ctx.terminal = terminal.slice(-6000);
  if (copiloto) {
    let usado = ctx.archivo?.contenido.length ?? 0;
    const carpeta = abierto ? FS.carpetaDe(abierto) : "";
    const prioridad = (r) => (abiertos.includes(r) ? 0 : carpeta && FS.carpetaDe(r) === carpeta ? 1 : /(^|\/)(package\.json|vite\.config\.[jt]s|index\.html|requirements\.txt|README\.md)$/i.test(r) ? 2 : 3);
    ctx.extra = [];
    for (const [r, t] of textos.filter(([r]) => r !== abierto).sort((a, b) => prioridad(a[0]) - prioridad(b[0]) || a[1].length - b[1].length)) {
      if (usado + t.length > PRESUPUESTO || ctx.extra.length >= 30) continue;
      ctx.extra.push({ ruta: r, contenido: t });
      usado += t.length;
    }
  }
  return ctx;
}
