// Leer y crear archivos .zip sin librerías.
// Descomprime con DecompressionStream("deflate-raw") (Chrome/Edge 80+, Firefox 113+, Safari 16.4+).
// Crea los .zip con CompressionStream si existe; si no, los guarda sin comprimir (también son .zip válidos).

// Todo se descomprime en la memoria del navegador: por eso el tope es 1 GB (para más, usa «Subir una carpeta»).
export const LIMITES_ZIP = { entradas: 5000, porArchivo: 1024 ** 3, total: 1024 ** 3 };

export const zipDisponible = () => typeof DecompressionStream === "function";

let TABLA_CRC;
export function crc32(bytes) {
  if (!TABLA_CRC) {
    TABLA_CRC = new Uint32Array(256);
    for (let n = 0; n < 256; n += 1) {
      let c = n;
      for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      TABLA_CRC[n] = c >>> 0;
    }
  }
  let c = 0xffffffff;
  for (let i = 0; i < bytes.length; i += 1) c = TABLA_CRC[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

async function transformar(bytes, flujo) {
  const s = new Blob([bytes]).stream().pipeThrough(flujo);
  return new Uint8Array(await new Response(s).arrayBuffer());
}

const CP437 = "ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ ";
function decodificarNombre(bytes, utf8) {
  if (utf8) return new TextDecoder().decode(bytes);
  try { return new TextDecoder("utf-8", { fatal: true }).decode(bytes); } // muchos programas usan UTF-8 sin marcarlo
  catch { return [...bytes].map((b) => (b < 128 ? String.fromCharCode(b) : CP437[b - 128])).join(""); }
}

/**
 * Lee un .zip. Devuelve { archivos: [{ ruta, bytes }], carpetas: [ruta], omitidos: [{ ruta, motivo }] }.
 * Lanza Error (en español) si el archivo no es un .zip que se pueda leer.
 */
export async function leerZip(entrada, { limites = LIMITES_ZIP } = {}) {
  const datos = entrada instanceof Uint8Array ? entrada : new Uint8Array(entrada);
  const v = new DataView(datos.buffer, datos.byteOffset, datos.byteLength);
  // Fin del directorio central: está en los últimos 22 bytes + comentario (hasta 64 KB).
  let fin = -1;
  for (let i = datos.length - 22; i >= Math.max(0, datos.length - 22 - 0xffff); i -= 1) {
    if (v.getUint32(i, true) === 0x06054b50) { fin = i; break; }
  }
  if (fin < 0) throw new Error("No parece un archivo .zip (o está dañado).");
  const total = v.getUint16(fin + 10, true);
  let p = v.getUint32(fin + 16, true);
  if (total === 0xffff || p === 0xffffffff) throw new Error("Este .zip usa el formato ZIP64 (archivos enormes), que no está soportado.");
  if (total > limites.entradas) throw new Error(`El .zip tiene ${total} elementos; el máximo es ${limites.entradas}.`);

  const archivos = [];
  const carpetas = [];
  const omitidos = [];
  let acumulado = 0;
  for (let n = 0; n < total; n += 1) {
    if (p + 46 > datos.length || v.getUint32(p, true) !== 0x02014b50) throw new Error("El .zip está dañado (directorio central incompleto).");
    const banderas = v.getUint16(p + 8, true);
    const metodo = v.getUint16(p + 10, true);
    const crc = v.getUint32(p + 16, true);
    const comprimido = v.getUint32(p + 20, true);
    const tamano = v.getUint32(p + 24, true);
    const largoNombre = v.getUint16(p + 28, true);
    const largoExtra = v.getUint16(p + 30, true);
    const largoComentario = v.getUint16(p + 32, true);
    const local = v.getUint32(p + 42, true);
    const ruta = decodificarNombre(datos.subarray(p + 46, p + 46 + largoNombre), (banderas & 0x800) !== 0).replace(/\\/g, "/");
    p += 46 + largoNombre + largoExtra + largoComentario;

    if (ruta.endsWith("/")) { carpetas.push(ruta.replace(/\/+$/, "")); continue; }
    if (banderas & 1) { omitidos.push({ ruta, motivo: "está protegido con contraseña" }); continue; }
    if (metodo !== 0 && metodo !== 8) { omitidos.push({ ruta, motivo: "usa un método de compresión no soportado" }); continue; }
    if (tamano > limites.porArchivo) { omitidos.push({ ruta, motivo: `pesa más de ${Math.round(limites.porArchivo / 1048576)} MB` }); continue; }
    if (acumulado + tamano > limites.total) { omitidos.push({ ruta, motivo: "el .zip pasa de 1 GB descomprimido: súbelo como carpeta" }); continue; }
    if (local + 30 > datos.length || v.getUint32(local, true) !== 0x04034b50) { omitidos.push({ ruta, motivo: "está dañado" }); continue; }
    const inicio = local + 30 + v.getUint16(local + 26, true) + v.getUint16(local + 28, true);
    const crudo = datos.subarray(inicio, inicio + comprimido);
    let bytes;
    try {
      bytes = metodo === 0 ? crudo.slice() : await transformar(crudo, new DecompressionStream("deflate-raw"));
    } catch {
      omitidos.push({ ruta, motivo: zipDisponible() ? "está dañado" : "este navegador no puede descomprimir .zip" });
      continue;
    }
    if (bytes.length !== tamano || crc32(bytes) !== crc) { omitidos.push({ ruta, motivo: "está dañado (no coincide su comprobación)" }); continue; }
    acumulado += bytes.length;
    archivos.push({ ruta, bytes });
  }
  return { archivos, carpetas, omitidos };
}

function fechaDos(d) {
  const hora = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
  const dia = ((Math.max(1980, d.getFullYear()) - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
  return [hora, dia];
}

/**
 * Crea un .zip. archivos: [{ ruta, bytes|blob|texto }], carpetas: [ruta] (para conservar las vacías).
 * Solo se comprime el texto: imágenes, videos y demás ya vienen comprimidos. Devuelve Uint8Array.
 */
export async function crearZip(archivos, { carpetas = [], fecha = new Date(), comprimir = typeof CompressionStream === "function" } = {}) {
  const enc = new TextEncoder();
  const [hora, dia] = fechaDos(fecha);
  const partes = [];
  const central = [];
  let desplazamiento = 0;
  const entradas = [
    ...carpetas.map((c) => ({ ruta: `${c}/`, bytes: new Uint8Array(0), dir: true })),
    ...archivos.map((a) => ({ ruta: a.ruta, bytes: a.bytes, blob: a.blob, texto: a.texto })),
  ];
  for (const e of entradas) {
    if (!e.bytes) e.bytes = e.blob ? new Uint8Array(await e.blob.arrayBuffer()) : enc.encode(e.texto ?? "");
    const nombre = enc.encode(e.ruta);
    const crc = crc32(e.bytes);
    let metodo = 0;
    let cuerpo = e.bytes;
    if (comprimir && !e.dir && e.texto !== undefined && e.bytes.length > 64) {
      const z = await transformar(e.bytes, new CompressionStream("deflate-raw"));
      if (z.length < e.bytes.length) { metodo = 8; cuerpo = z; }
    }
    const cab = new Uint8Array(30 + nombre.length);
    const c = new DataView(cab.buffer);
    c.setUint32(0, 0x04034b50, true); c.setUint16(4, 20, true); c.setUint16(6, 0x800, true); c.setUint16(8, metodo, true);
    c.setUint16(10, hora, true); c.setUint16(12, dia, true); c.setUint32(14, crc, true);
    c.setUint32(18, cuerpo.length, true); c.setUint32(22, e.bytes.length, true); c.setUint16(26, nombre.length, true);
    cab.set(nombre, 30);
    const cen = new Uint8Array(46 + nombre.length);
    const d = new DataView(cen.buffer);
    d.setUint32(0, 0x02014b50, true); d.setUint16(4, 20, true); d.setUint16(6, 20, true); d.setUint16(8, 0x800, true); d.setUint16(10, metodo, true);
    d.setUint16(12, hora, true); d.setUint16(14, dia, true); d.setUint32(16, crc, true);
    d.setUint32(20, cuerpo.length, true); d.setUint32(24, e.bytes.length, true); d.setUint16(28, nombre.length, true);
    d.setUint32(38, e.dir ? 0x10 : 0, true); d.setUint32(42, desplazamiento, true);
    cen.set(nombre, 46);
    partes.push(cab, cuerpo);
    central.push(cen);
    desplazamiento += cab.length + cuerpo.length;
  }
  const largoCentral = central.reduce((s, x) => s + x.length, 0);
  const fin = new Uint8Array(22);
  const f = new DataView(fin.buffer);
  f.setUint32(0, 0x06054b50, true); f.setUint16(8, entradas.length, true); f.setUint16(10, entradas.length, true);
  f.setUint32(12, largoCentral, true); f.setUint32(16, desplazamiento, true);
  const todo = [...partes, ...central, fin];
  const salida = new Uint8Array(todo.reduce((s, x) => s + x.length, 0));
  let i = 0;
  for (const x of todo) { salida.set(x, i); i += x.length; }
  return salida;
}
