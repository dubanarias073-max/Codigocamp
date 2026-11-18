// Sistema de archivos virtual del proyecto (Trabajo).
// Todo aquí es lógica pura —sin DOM— para poder usarla desde el explorador, la terminal y las pruebas.
//
// Un proyecto es { files: { "ruta/archivo.js": "texto" }, folders: ["ruta", "ruta/sub"], git: {...} }.
// Las rutas son relativas a la raíz del proyecto (que la terminal muestra como /workspace).
// Las reglas de nombres y los límites repiten los del servidor (backend/rutas/trabajo.py):
// si cambian allá, deben cambiar aquí.

export const RAIZ = "/workspace";
// caracteres: solo el texto editable; los archivos guardados en la cuenta (marcadores) no cuentan.
export const LIMITES = { archivos: 5000, carpetas: 2000, caracteres: 5_000_000, ruta: 400, nombre: 120 };

const NOMBRE = /^[A-Za-z0-9_.-]{1,120}$/;
const PROHIBIDOS = new Set(["__proto__", "prototype", "constructor"]);

export const nombreBase = (ruta) => ruta.slice(ruta.lastIndexOf("/") + 1);
export const carpetaDe = (ruta) => (ruta.includes("/") ? ruta.slice(0, ruta.lastIndexOf("/")) : "");
export const unir = (carpeta, nombre) => (carpeta ? `${carpeta}/${nombre}` : nombre);
export const extension = (ruta) => {
  const n = nombreBase(ruta);
  const i = n.lastIndexOf(".");
  return i === -1 ? "" : n.slice(i + 1).toLowerCase();
};
export const dentroDe = (ruta, carpeta) => carpeta === "" || ruta === carpeta || ruta.startsWith(carpeta + "/");

export function nombreValido(nombre) {
  return typeof nombre === "string" && NOMBRE.test(nombre) && nombre !== "." && nombre !== ".."
    && !PROHIBIDOS.has(nombre.toLowerCase());
}

/** Mensaje en español que explica por qué un nombre no sirve, o null si es válido. */
export function errorDeNombre(nombre) {
  if (typeof nombre !== "string" || !nombre.trim()) return "Escribe un nombre.";
  if (nombre.length > LIMITES.nombre) return `El nombre no puede pasar de ${LIMITES.nombre} caracteres.`;
  if (nombre === "." || nombre === "..") return "Ese nombre no es válido.";
  if (/[\\/]/.test(nombre)) return "El nombre no puede incluir barras (/ o \\).";
  if (/\s/.test(nombre)) return "El nombre no puede tener espacios. Usa guion (-) o guion bajo (_).";
  if (!NOMBRE.test(nombre)) return "Usa solo letras sin tilde, números, punto, guion y guion bajo.";
  if (PROHIBIDOS.has(nombre.toLowerCase())) return "Ese nombre está reservado.";
  return null;
}

export function rutaValida(ruta) {
  return typeof ruta === "string" && ruta.length > 0 && ruta.length <= LIMITES.ruta && ruta.split("/").every(nombreValido);
}

const agregarAncestros = (conjunto, carpeta) => {
  if (!carpeta) return;
  const partes = carpeta.split("/");
  for (let i = 1; i <= partes.length; i += 1) conjunto.add(partes.slice(0, i).join("/"));
};

/** Limpia datos que vengan de fuera (navegador o servidor): descarta rutas inválidas y completa las carpetas padre. */
export function normalizar(crudo) {
  const files = {};
  const origen = crudo && typeof crudo.files === "object" && crudo.files ? crudo.files : {};
  for (const [ruta, texto] of Object.entries(origen)) {
    if (rutaValida(ruta) && typeof texto === "string") files[ruta] = texto;
  }
  const declaradas = Array.isArray(crudo?.folders) ? crudo.folders.filter(rutaValida) : [];
  const carpetas = new Set();
  declaradas.forEach((c) => agregarAncestros(carpetas, c));
  Object.keys(files).forEach((r) => agregarAncestros(carpetas, carpetaDe(r)));
  // Una ruta no puede ser archivo y carpeta a la vez: manda la carpeta (si tiene contenido) y se descarta el archivo.
  for (const ruta of Object.keys(files)) if (carpetas.has(ruta)) delete files[ruta];
  return { files, folders: [...carpetas].sort() };
}

export const tieneArchivo = (py, ruta) => Object.hasOwn(py.files, ruta);
export const tieneCarpeta = (py, ruta) => ruta === "" || py.folders.includes(ruta);
export const existe = (py, ruta) => tieneArchivo(py, ruta) || tieneCarpeta(py, ruta);
export const esCarpeta = (py, ruta) => ruta !== "" && py.folders.includes(ruta);

const ordenNatural = (a, b) => a.localeCompare(b, "es", { numeric: true, sensitivity: "base" });

/** Nombres (no rutas) de lo que hay directamente dentro de una carpeta, carpetas y archivos por separado. */
export function hijos(py, carpeta = "") {
  const dirs = py.folders.filter((c) => carpetaDe(c) === carpeta).map(nombreBase).sort(ordenNatural);
  const files = Object.keys(py.files).filter((r) => carpetaDe(r) === carpeta).map(nombreBase).sort(ordenNatural);
  return { dirs, files };
}

/** Todos los archivos de una carpeta, a cualquier profundidad (rutas completas, ordenadas). */
export function archivosEn(py, carpeta = "") {
  return Object.keys(py.files).filter((r) => dentroDe(r, carpeta)).sort(ordenNatural);
}

/** Caracteres de texto editable (los marcadores de archivos guardados en la cuenta no cuentan). */
const esMarcadorFs = (t) => t.startsWith("cc") && /^cc(?:img|bin):v1:[a-f0-9]{64}:/.test(t);
export function usoCaracteres(py) {
  let n = 0;
  for (const texto of Object.values(py.files)) if (!esMarcadorFs(texto)) n += texto.length;
  return n;
}

/**
 * Convierte lo que escribió el usuario en una ruta del proyecto (relativa a la raíz).
 * Admite ".", "..", "~" (la raíz), rutas relativas y rutas /workspace/... Devuelve null si queda fuera del proyecto
 * o si algún nombre no es válido.
 */
export function resolver(cwd, entrada) {
  const e = String(entrada ?? "");
  let partes;
  if (e === "" || e === "~") return "";
  if (e.startsWith("~/")) partes = e.slice(2).split("/");
  else if (e === RAIZ || e.startsWith(RAIZ + "/")) partes = e.slice(RAIZ.length).split("/");
  else if (e.startsWith("/")) return null;
  else partes = [...cwd.split("/").filter(Boolean), ...e.split("/")];
  const salida = [];
  for (const parte of partes) {
    if (!parte || parte === ".") continue;
    if (parte === "..") { salida.pop(); continue; }
    if (!nombreValido(parte)) return null;
    salida.push(parte);
  }
  const ruta = salida.join("/");
  return ruta.length > LIMITES.ruta ? null : ruta;
}

/** Cómo se muestra una ruta en la terminal: /workspace, /workspace/src ... */
export const rutaAbsoluta = (ruta) => (ruta ? `${RAIZ}/${ruta}` : RAIZ);

const patronARegExp = (patron) => new RegExp("^" + patron.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, ".") + "$", "i");

/** Expande comodines (* y ?) en el último tramo de la ruta, como hace una shell. Devuelve [] si nada coincide. */
export function expandirComodin(py, cwd, patron) {
  const barra = patron.lastIndexOf("/");
  const dirEscrito = barra === -1 ? "" : patron.slice(0, barra + 1);
  const base = patron.slice(barra + 1);
  const dir = resolver(cwd, dirEscrito || ".");
  if (dir === null || !tieneCarpeta(py, dir)) return [];
  const re = patronARegExp(base);
  const { dirs, files } = hijos(py, dir);
  return [...dirs, ...files]
    .filter((n) => re.test(n) && (base.startsWith(".") || !n.startsWith(".")))
    .map((n) => dirEscrito + n);
}

const fallo = (error) => ({ ok: false, error });
const bien = (extra = {}) => ({ ok: true, ...extra });

function comprobarDestino(py, ruta, { padres = false } = {}) {
  if (ruta === "") return fallo("Esa ruta no es válida.");
  if (!rutaValida(ruta)) return fallo("El nombre no es válido: usa letras sin tilde, números, punto, guion y guion bajo (sin espacios).");
  if (existe(py, ruta)) return fallo("Ya existe un archivo o carpeta con ese nombre.");
  const padre = carpetaDe(ruta);
  if (tieneArchivo(py, padre)) return fallo(`«${padre}» es un archivo, no una carpeta.`);
  if (!tieneCarpeta(py, padre) && !padres) return fallo("La carpeta de destino no existe.");
  return null;
}

export function crearCarpeta(py, ruta, { padres = false } = {}) {
  if (padres && existe(py, ruta) && esCarpeta(py, ruta)) return bien({ creada: false });
  const problema = comprobarDestino(py, ruta, { padres });
  if (problema) return problema;
  const nuevas = new Set();
  agregarAncestros(nuevas, ruta);
  const faltan = [...nuevas].filter((c) => !py.folders.includes(c));
  if (faltan.some((c) => tieneArchivo(py, c))) return fallo("Una parte de la ruta es un archivo, no una carpeta.");
  if (py.folders.length + faltan.length > LIMITES.carpetas) return fallo(`Se alcanzó el límite de ${LIMITES.carpetas} carpetas.`);
  py.folders.push(...faltan);
  py.folders.sort();
  return bien({ creada: true });
}

export function crearArchivo(py, ruta, contenido = "", { padres = false } = {}) {
  const problema = comprobarDestino(py, ruta, { padres });
  if (problema) return problema;
  if (Object.keys(py.files).length >= LIMITES.archivos) return fallo(`Se alcanzó el límite de ${LIMITES.archivos} archivos.`);
  if (!esMarcadorFs(contenido) && usoCaracteres(py) + contenido.length > LIMITES.caracteres) return fallo("El proyecto superaría el límite de almacenamiento.");
  if (padres) {
    const r = crearCarpeta(py, carpetaDe(ruta), { padres: true });
    if (!r.ok) return r;
  }
  py.files[ruta] = contenido;
  return bien();
}

/** Escribe (crea o reemplaza) un archivo; la carpeta que lo contiene debe existir. Lo usan las redirecciones > y >>. */
export function escribirArchivo(py, ruta, texto, { anexar = false } = {}) {
  if (!rutaValida(ruta)) return fallo("El nombre no es válido: usa letras sin tilde, números, punto, guion y guion bajo.");
  if (esCarpeta(py, ruta)) return fallo("Es una carpeta.");
  const padre = carpetaDe(ruta);
  if (tieneArchivo(py, padre)) return fallo(`«${padre}» es un archivo, no una carpeta.`);
  if (!tieneCarpeta(py, padre)) return fallo("No existe el archivo o el directorio.");
  if (!tieneArchivo(py, ruta)) return crearArchivo(py, ruta, texto);
  const nuevo = anexar ? py.files[ruta] + texto : texto;
  if (!esMarcadorFs(nuevo) && usoCaracteres(py) - (esMarcadorFs(py.files[ruta]) ? 0 : py.files[ruta].length) + nuevo.length > LIMITES.caracteres) return fallo("El proyecto superaría el límite de almacenamiento.");
  py.files[ruta] = nuevo;
  return bien();
}

/** Borra un archivo o una carpeta con todo su contenido. Devuelve lo borrado para poder deshacerlo. */
export function borrar(py, ruta) {
  if (ruta === "") return fallo("No se puede eliminar la raíz del proyecto.");
  if (!existe(py, ruta)) return fallo("No existe.");
  const eliminado = { files: {}, folders: [] };
  for (const r of Object.keys(py.files)) {
    if (dentroDe(r, ruta)) { eliminado.files[r] = py.files[r]; delete py.files[r]; }
  }
  eliminado.folders = py.folders.filter((c) => dentroDe(c, ruta));
  py.folders = py.folders.filter((c) => !dentroDe(c, ruta));
  return bien({ eliminado });
}

/** Vuelve a poner lo que devolvió borrar(). */
export function restaurar(py, eliminado) {
  Object.assign(py.files, eliminado.files);
  const carpetas = new Set(py.folders);
  eliminado.folders.forEach((c) => carpetas.add(c));
  Object.keys(eliminado.files).forEach((r) => agregarAncestros(carpetas, carpetaDe(r)));
  py.folders = [...carpetas].sort();
}

/** Mueve o renombra un archivo o carpeta a una ruta final que aún no existe. */
export function mover(py, de, a) {
  if (de === "" || a === "") return fallo("Esa ruta no es válida.");
  if (!existe(py, de)) return fallo("No existe el origen.");
  if (de === a) return bien();
  if (esCarpeta(py, de) && dentroDe(a, de)) return fallo("No se puede mover una carpeta dentro de sí misma.");
  const problema = comprobarDestino(py, a);
  if (problema) return problema;
  if (tieneArchivo(py, de)) {
    py.files[a] = py.files[de];
    delete py.files[de];
    return bien();
  }
  const cambiar = (r) => a + r.slice(de.length);
  for (const r of Object.keys(py.files)) {
    if (dentroDe(r, de)) { py.files[cambiar(r)] = py.files[r]; delete py.files[r]; }
  }
  py.folders = py.folders.map((c) => (dentroDe(c, de) ? cambiar(c) : c)).sort();
  return bien();
}

/** Copia un archivo o (con recursivo) una carpeta a una ruta final que aún no existe. */
export function copiar(py, de, a, { recursivo = false } = {}) {
  if (de === "" || a === "") return fallo("Esa ruta no es válida.");
  if (!existe(py, de)) return fallo("No existe el origen.");
  if (esCarpeta(py, de)) {
    if (!recursivo) return fallo("Es una carpeta (usa -r para copiarla).");
    if (dentroDe(a, de)) return fallo("No se puede copiar una carpeta dentro de sí misma.");
  }
  const problema = comprobarDestino(py, a);
  if (problema) return problema;
  const archivos = archivosEn(py, de);
  if (Object.keys(py.files).length + archivos.length > LIMITES.archivos) return fallo(`Se alcanzó el límite de ${LIMITES.archivos} archivos.`);
  const extra = archivos.reduce((s, r) => s + (esMarcadorFs(py.files[r]) ? 0 : py.files[r].length), 0);
  if (usoCaracteres(py) + extra > LIMITES.caracteres) return fallo("El proyecto superaría el límite de almacenamiento.");
  if (tieneArchivo(py, de)) {
    py.files[a] = py.files[de];
    return bien();
  }
  const nuevas = new Set(py.folders);
  py.folders.filter((c) => dentroDe(c, de)).forEach((c) => nuevas.add(a + c.slice(de.length)));
  archivos.forEach((r) => { py.files[a + r.slice(de.length)] = py.files[r]; });
  py.folders = [...nuevas].sort();
  return bien();
}

/** Un nombre que no choque con nada: "copia.js" -> "copia-2.js". */
export function nombreLibre(py, carpeta, nombre) {
  if (!existe(py, unir(carpeta, nombre))) return nombre;
  const i = nombre.lastIndexOf(".");
  const [raiz, ext] = i > 0 ? [nombre.slice(0, i), nombre.slice(i)] : [nombre, ""];
  for (let n = 2; n < 1000; n += 1) {
    const candidato = `${raiz}-${n}${ext}`;
    if (!existe(py, unir(carpeta, candidato))) return candidato;
  }
  return nombre;
}
