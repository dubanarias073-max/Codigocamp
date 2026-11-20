// Importar archivos al proyecto (desde un .zip, una carpeta del computador, archivos soltados o un git clone).
// Lógica pura, sin DOM ni red: decide qué entra como texto editable, qué entra como archivo (imagen, video, PDF…),
// qué se renombra y qué se omite (y por qué). Quien la usa sube los archivos (archivos.js) y luego llama a aplicar().
//
// Una entrada es { ruta, bytes } o, para archivos grandes que no conviene cargar en memoria, { ruta, blob, cabeza }.
import * as FS from "./fs.js";
import { LIMITES_ARCHIVO, TEXTO_EDITABLE, esMarcador, formatoBytes, tipoDe } from "./archivos.js";

/** Carpetas que nunca se importan: son de herramientas, se regeneran o pesan demasiado. */
export const CARPETAS_IGNORADAS = new Set([".git", "node_modules", "__MACOSX", "__pycache__", ".venv", "venv", ".idea", ".vs", ".next", ".cache"]);
const ARCHIVOS_IGNORADOS = new Set([".DS_Store", "Thumbs.db", "desktop.ini"]);

/** Convierte un nombre en uno válido: solo cambia lo que Windows no admite («a:b?.txt» → «a_b_.txt»). */
export function limpiarNombre(nombre) {
  if (FS.nombreValido(String(nombre))) return String(nombre); // espacios, tildes, paréntesis, __init__.py… se quedan tal cual
  let n = String(nombre).replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_").trim().replace(/\.+$/, "");
  if (n.length > FS.LIMITES.nombre) {
    const i = n.lastIndexOf(".");
    const ext = i > 0 && n.length - i <= 10 ? n.slice(i) : "";
    n = n.slice(0, FS.LIMITES.nombre - ext.length) + ext;
  }
  if (!n || n === "." || n === ".." || !FS.nombreValido(n)) return null;
  return n;
}

/** { ruta, renombrada } con una ruta válida, { ignorar: true } si es de una carpeta ignorada, o { error }. */
export function limpiarRuta(ruta, { ignorar = true } = {}) {
  const partes = String(ruta).replace(/\\/g, "/").split("/").filter((p) => p && p !== ".");
  if (!partes.length) return { error: "no tiene nombre" };
  if (partes.includes("..")) return { error: "su ruta sale de la carpeta" };
  if (partes[0] === ".git") return { ignorar: true }; // la carpeta interna de Git nunca se importa
  if (ignorar && partes.some((p) => CARPETAS_IGNORADAS.has(p))) return { ignorar: true };
  if (ignorar && ARCHIVOS_IGNORADOS.has(partes[partes.length - 1])) return { ignorar: true };
  const limpias = partes.map(limpiarNombre);
  if (limpias.some((p) => p === null)) return { error: "su nombre no se puede usar" };
  const nueva = limpias.join("/");
  if (nueva.length > FS.LIMITES.ruta) return { error: "su ruta es demasiado larga" };
  return { ruta: nueva, renombrada: nueva !== partes.join("/") };
}

/** Texto como lo guarda el proyecto: sin BOM y con saltos de línea \n (así no hay cambios fantasma al sincronizar). */
export const normalizarTexto = (t) => (t.charCodeAt(0) === 0xfeff ? t.slice(1) : t).replace(/\r\n?/g, "\n");

const decodificador = typeof TextDecoder === "function" ? new TextDecoder("utf-8", { fatal: true }) : null;
const tamanoEntrada = (e) => (e.blob ? e.blob.size : e.bytes.length);

/**
 * Qué es una entrada: { tipo: "texto", texto } | { tipo: "archivo", mime, grande? } | { tipo: "omitir", motivo }.
 * grande = es texto, pero demasiado largo para el editor: se guarda como archivo.
 */
export function clasificar(ruta, entrada, { maxArchivo = LIMITES_ARCHIVO.porArchivo } = {}) {
  const e = entrada instanceof Uint8Array ? { bytes: entrada } : entrada;
  const tamano = tamanoEntrada(e);
  if (tamano > maxArchivo) return { tipo: "omitir", motivo: `pesa ${formatoBytes(tamano)} (máximo ${formatoBytes(maxArchivo)} por archivo)` };
  const cabeza = e.blob ? e.cabeza ?? new Uint8Array(0) : e.bytes.subarray(0, 64);
  const mime = tipoDe(cabeza, ruta);
  if (e.blob || /^(image|video|audio|font)\/|^application\/(pdf|zip)$/.test(mime)) return { tipo: "archivo", mime, grande: e.blob && /^text\/|json/.test(mime) };
  let texto;
  try { texto = decodificador.decode(e.bytes); } catch { return { tipo: "archivo", mime }; }
  if (texto.includes("\u0000")) return { tipo: "archivo", mime };
  if (tamano > TEXTO_EDITABLE) return { tipo: "archivo", mime: mime === "application/octet-stream" ? "text/plain" : mime, grande: true };
  return { tipo: "texto", texto: normalizarTexto(texto) };
}

/** Si todo cuelga de una sola carpeta (típico de los .zip de GitHub: repo-main/...), devuelve su nombre. */
export function raizComun(rutas) {
  if (!rutas.length) return null;
  const primera = rutas[0].split("/")[0];
  return rutas.every((r) => r.startsWith(primera + "/")) ? primera : null;
}

/**
 * Decide qué entra en el proyecto.
 * @param {object} py   proyecto actual
 * @param {{ archivos: object[], carpetas?: string[], omitidos?: {ruta,motivo}[] }} origen
 * @param {object} o
 * @param {string} [o.destino]           carpeta del proyecto donde se ponen (por defecto la raíz)
 * @param {boolean} [o.reemplazar]       borrar antes todo el proyecto
 * @param {boolean} [o.quitarRaiz]       quitar la carpeta común (repo-main/)
 * @param {number} [o.espacioArchivos]   bytes libres para archivos en la cuenta
 * @param {number} [o.maxArchivo]        máximo por archivo
 */
export function planificar(py, origen, { destino = "", reemplazar = false, quitarRaiz = true, espacioArchivos = LIMITES_ARCHIVO.porCuenta, maxArchivo = LIMITES_ARCHIVO.porArchivo,
  ignorar = true, textoComoArchivo = false } = {}) {
  const plan = { textos: [], binarios: [], carpetas: [], omitidos: [...(origen.omitidos || [])], renombrados: [], reemplazados: [], comoArchivo: [], ignorados: 0, raiz: null, destino, reemplazar };
  let entradas = origen.archivos.map((a) => ({ ...a, original: a.ruta }));
  let carpetas = [...(origen.carpetas || [])];
  const raiz = quitarRaiz ? raizComun([...entradas.map((e) => e.ruta), ...carpetas.filter((c) => c.includes("/"))]) : null;
  if (raiz && entradas.length) {
    plan.raiz = raiz;
    entradas = entradas.map((e) => ({ ...e, ruta: e.ruta.slice(raiz.length + 1) }));
    carpetas = carpetas.map((c) => (c === raiz ? "" : c.startsWith(raiz + "/") ? c.slice(raiz.length + 1) : c)).filter(Boolean);
  }

  const actuales = reemplazar ? {} : { ...py.files };
  const carpetasActuales = new Set(reemplazar ? [] : py.folders);
  let cuenta = Object.keys(actuales).length;
  let caracteres = Object.values(actuales).reduce((s, t) => s + (esMarcador(t) ? 0 : t.length), 0);
  let bytesArchivos = 0;
  const vistas = new Set();
  const nuevasCarpetas = new Set();
  const agregarCarpeta = (c) => { for (let x = c; x; x = FS.carpetaDe(x)) nuevasCarpetas.add(x); };
  const prefijosArchivos = new Set(Object.keys(actuales));

  const ponerEn = (ruta) => FS.unir(destino, ruta);
  for (const c of carpetas) {
    const l = limpiarRuta(c);
    if (l.ruta) { const r = ponerEn(l.ruta); if (r.length <= FS.LIMITES.ruta) agregarCarpeta(r); }
  }

  entradas.sort((a, b) => a.ruta.localeCompare(b.ruta));
  for (const e of entradas) {
    const l = limpiarRuta(e.ruta, { ignorar });
    if (l.ignorar) { plan.ignorados += 1; continue; }
    if (l.error) { plan.omitidos.push({ ruta: e.original, motivo: l.error }); continue; }
    const ruta = ponerEn(l.ruta);
    if (ruta.length > FS.LIMITES.ruta) { plan.omitidos.push({ ruta: e.original, motivo: "su ruta es demasiado larga" }); continue; }
    if (vistas.has(ruta)) { plan.omitidos.push({ ruta: e.original, motivo: `su nombre limpio (${ruta}) choca con otro archivo` }); continue; }
    const padres = [];
    for (let x = FS.carpetaDe(ruta); x; x = FS.carpetaDe(x)) padres.push(x);
    const choca = carpetasActuales.has(ruta) || nuevasCarpetas.has(ruta) || padres.some((x) => prefijosArchivos.has(x) || vistas.has(x))
      || [...vistas].some((v) => v.startsWith(ruta + "/"));
    if (choca) { plan.omitidos.push({ ruta: e.original, motivo: "ya hay una carpeta o un archivo con ese nombre" }); continue; }
    let c = clasificar(ruta, e, { maxArchivo });
    if (c.tipo === "omitir") { plan.omitidos.push({ ruta: e.original, motivo: c.motivo }); continue; }
    const previo = Object.hasOwn(actuales, ruta) ? actuales[ruta] : null;
    const largoPrevio = previo === null || esMarcador(previo) ? 0 : previo.length;
    // Texto que ya no cabe como editable: se guarda completo como archivo de la cuenta (se ve y se descarga).
    if (c.tipo === "texto" && textoComoArchivo && caracteres - largoPrevio + c.texto.length > FS.LIMITES.caracteres) {
      c = { tipo: "archivo", mime: tipoDe(e.bytes.subarray(0, 64), ruta) === "application/octet-stream" ? "text/plain" : tipoDe(e.bytes.subarray(0, 64), ruta), grande: true };
    }
    const nuevoLargo = c.tipo === "texto" ? c.texto.length : 0;
    const tamano = tamanoEntrada(e);
    if (previo === null && cuenta + 1 > FS.LIMITES.archivos) { plan.omitidos.push({ ruta: e.original, motivo: `no cabe: el proyecto admite ${FS.LIMITES.archivos} archivos` }); continue; }
    if (caracteres - largoPrevio + nuevoLargo > FS.LIMITES.caracteres) { plan.omitidos.push({ ruta: e.original, motivo: "no cabe: se llenaría el espacio de texto editable del proyecto (5 millones de caracteres)" }); continue; }
    if (c.tipo === "archivo" && bytesArchivos + tamano > espacioArchivos) { plan.omitidos.push({ ruta: e.original, motivo: `no cabe: quedan ${formatoBytes(Math.max(0, espacioArchivos - bytesArchivos))} libres en tu cuenta` }); continue; }
    vistas.add(ruta);
    if (previo === null) cuenta += 1; else plan.reemplazados.push(ruta);
    caracteres += nuevoLargo - largoPrevio;
    if (l.renombrada) plan.renombrados.push({ de: e.original, a: ruta });
    agregarCarpeta(FS.carpetaDe(ruta));
    if (c.tipo === "texto") plan.textos.push({ ruta, texto: c.texto });
    else {
      plan.binarios.push({ ruta, datos: e.blob ?? e.bytes, tipo: c.mime, tamano });
      bytesArchivos += tamano;
      if (c.grande) plan.comoArchivo.push(ruta);
    }
  }
  const totalCarpetas = new Set([...carpetasActuales, ...nuevasCarpetas]).size;
  if (totalCarpetas > FS.LIMITES.carpetas) plan.error = `Quedarían ${totalCarpetas} carpetas y el proyecto admite ${FS.LIMITES.carpetas}.`;
  plan.carpetas = [...nuevasCarpetas].sort();
  plan.bytesArchivos = bytesArchivos;
  return plan;
}

/**
 * Escribe el plan en el proyecto. marcadores: Map ruta → marcador de los archivos ya subidos
 * (los que no estén se dan por omitidos). Devuelve cuántos archivos se escribieron.
 */
export function aplicar(py, plan, marcadores = new Map()) {
  const files = plan.reemplazar ? {} : { ...py.files };
  for (const { ruta, texto } of plan.textos) files[ruta] = texto;
  let n = plan.textos.length;
  for (const { ruta } of plan.binarios) {
    const m = marcadores.get(ruta);
    if (m) { files[ruta] = m; n += 1; }
  }
  const limpio = FS.normalizar({ files, folders: [...(plan.reemplazar ? [] : py.folders), ...plan.carpetas] });
  py.files = limpio.files;
  py.folders = limpio.folders;
  return n;
}

/** Resumen legible de un plan ya aplicado, para la terminal o un aviso. */
export function resumenPlan(plan, escritos) {
  const partes = [`${escritos} ${escritos === 1 ? "archivo importado" : "archivos importados"}`];
  if (plan.bytesArchivos) partes.push(`${formatoBytes(plan.bytesArchivos)} en archivos`);
  if (plan.reemplazados.length) partes.push(`${plan.reemplazados.length} reemplazados`);
  if (plan.renombrados.length) partes.push(`${plan.renombrados.length} renombrados`);
  if (plan.omitidos.length) partes.push(`${plan.omitidos.length} omitidos`);
  if (plan.ignorados) partes.push(`${plan.ignorados} de carpetas como .git o node_modules ignorados`);
  return partes.join(" · ");
}

/**
 * Convierte File/Blob del navegador en entradas: los pequeños se leen enteros (pueden ser texto editable);
 * los grandes se quedan como Blob (se suben directo, sin pasar por la memoria).
 */
export async function prepararArchivos(lista) {
  return Promise.all(lista.map(async ({ ruta, archivo }) => (archivo.size > TEXTO_EDITABLE
    ? { ruta, blob: archivo, cabeza: new Uint8Array(await archivo.slice(0, 64).arrayBuffer()) }
    : { ruta, bytes: new Uint8Array(await archivo.arrayBuffer()) })));
}

/**
 * Planifica, sube los archivos y aplica, todo en uno.
 * @param {object} o
 * @param {(datos, {nombre, progreso})=>Promise<string>} [o.subir]   sube un archivo y devuelve su marcador (sin él, se omiten)
 * @param {()=>Promise<{libre:number, maxArchivo:number}>} [o.espacio]
 * @param {(texto:string)=>void} [o.progreso]
 * @returns {Promise<{ plan: object, escritos: number }>}
 */
export async function importarEn(py, origen, { destino = "", reemplazar = false, quitarRaiz = true, subir = null, espacio = null, progreso = () => {}, ignorar = true } = {}) {
  let libre = 0;
  let maxArchivo = LIMITES_ARCHIVO.porArchivo;
  if (subir) {
    // Si no se pudo consultar el espacio, no se asume «0 libres»: el servidor decide al subir cada archivo y dice el motivo real.
    try { const e = espacio ? await espacio() : { libre: Infinity }; libre = e.libre; maxArchivo = e.maxArchivo ?? maxArchivo; } catch { libre = Infinity; }
  }
  const plan = planificar(py, origen, { destino, reemplazar, quitarRaiz, espacioArchivos: subir ? libre : Infinity, maxArchivo, ignorar, textoComoArchivo: Boolean(subir) });
  if (plan.error) throw new Error(plan.error);
  const marcadores = new Map();
  if (!subir) {
    for (const b of plan.binarios) plan.omitidos.push({ ruta: b.ruta, motivo: "los archivos que no son texto solo se guardan con sesión iniciada" });
  } else {
    let i = 0;
    for (const b of plan.binarios) {
      i += 1;
      const cabecera = `Subiendo archivos ${i}/${plan.binarios.length}: ${FS.nombreBase(b.ruta)} (${formatoBytes(b.tamano)})`;
      progreso(cabecera);
      try { marcadores.set(b.ruta, await subir(b.datos, { nombre: b.ruta, progreso: (f) => progreso(`${cabecera} · ${Math.round(f * 100)} %`) })); }
      catch (e) { plan.omitidos.push({ ruta: b.ruta, motivo: e.message || "no se pudo subir" }); }
    }
  }
  const escritos = aplicar(py, plan, marcadores);
  return { plan, escritos };
}

/**
 * Archivos del proyecto listos para un .zip (que se arma en la memoria del navegador, así que tiene tope).
 * leerBlob(marcador) → Promise<Blob>. Las que no se puedan descargar van en `fallidas`; las que no caben, en `grandes`.
 */
export async function paraExportar(py, leerBlob, { esMarcador, leerMarcador, maximo = 1024 ** 3 }) {
  const archivos = [];
  const fallidas = [];
  const grandes = [];
  let total = 0;
  const rutas = Object.keys(py.files).sort();
  for (const ruta of rutas) if (!esMarcador(py.files[ruta])) { archivos.push({ ruta, texto: py.files[ruta] }); total += py.files[ruta].length; }
  const binarias = rutas.filter((r) => esMarcador(py.files[r])).sort((a, b) => leerMarcador(py.files[a]).tamano - leerMarcador(py.files[b]).tamano);
  for (const ruta of binarias) {
    const t = leerMarcador(py.files[ruta]).tamano;
    if (total + t > maximo) { grandes.push(ruta); continue; }
    try { archivos.push({ ruta, blob: await leerBlob(py.files[ruta]) }); total += t; } catch { fallidas.push(ruta); }
  }
  archivos.sort((a, b) => a.ruta.localeCompare(b.ruta));
  const conArchivos = new Set(Object.keys(py.files).map(FS.carpetaDe));
  const vacias = py.folders.filter((c) => ![...conArchivos].some((x) => FS.dentroDe(x, c)));
  return { archivos, carpetas: vacias, fallidas, grandes, total };
}
