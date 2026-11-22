// Paquetes de Python instalados con pip de verdad en el servidor (los que el navegador no puede: código en C
// sin versión para Pyodide). Se recuerda qué módulos trae cada uno para saber cuándo un programa tiene que
// ejecutarse en el servidor en vez de en el navegador.
import * as FS from "./fs.js";
import { esMarcador } from "./archivos.js";

export function crearPaquetesServidor(clave) {
  const KEY = `cc_py_servidor:${clave}`;
  const leer = () => { try { const o = JSON.parse(localStorage.getItem(KEY)); return o && typeof o === "object" && !Array.isArray(o) ? o : {}; } catch { return {}; } };
  const guardar = (o) => { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch { /* sin espacio */ } };
  return {
    leer,
    agregar(instalados) { const o = leer(); for (const i of instalados) o[i.paquete] = { version: i.version || "", modulos: i.modulos?.length ? i.modulos : [i.paquete.replace(/-/g, "_")] }; guardar(o); },
    quitar(nombres) { const o = leer(); for (const n of nombres) delete o[n]; guardar(o); },
    tiene: (n) => n in leer(),
    modulos() { const s = new Set(); for (const v of Object.values(leer())) for (const m of v.modulos || []) s.add(m); return s; },
  };
}

const IMPORT = /^[ \t]*(?:from[ \t]+([A-Za-z_][\w]*)[\w.]*[ \t]+import\b|import[ \t]+([^#\n]+))/gm;

/** Módulos de primer nivel que importa un código de Python. */
export function importsDe(codigo) {
  const s = new Set();
  for (const m of codigo.matchAll(IMPORT)) {
    if (m[1]) s.add(m[1]);
    else for (const parte of m[2].split(",")) { const n = parte.trim().split(/[\s.]/)[0]; if (/^[A-Za-z_]\w*$/.test(n)) s.add(n); }
  }
  return s;
}

/** ¿El programa (o los .py del proyecto que importa) usa un paquete que solo está en el servidor? Devuelve su nombre. */
export function necesitaServidor(py, ruta, modulosServidor) {
  if (!modulosServidor.size) return null;
  const vistos = new Set();
  const pendientes = [ruta];
  const dir = FS.carpetaDe(ruta);
  while (pendientes.length) {
    const r = pendientes.pop();
    if (vistos.has(r)) continue;
    vistos.add(r);
    for (const m of importsDe(py.files[r] ?? "")) {
      const local = [FS.unir(dir, `${m}.py`), FS.unir(dir, `${m}/__init__.py`)].find((x) => FS.tieneArchivo(py, x));
      if (local) { pendientes.push(local); continue; }
      if (FS.esCarpeta?.(py, FS.unir(dir, m))) continue;
      if (modulosServidor.has(m)) return m;
    }
  }
  return null;
}

const TEXTO = /\.(py|txt|csv|tsv|json|ya?ml|toml|ini|cfg|env|md|html?|css|js|sql|xml|dat|log)$/i;
/** Archivos de texto del proyecto que se envían al servidor (primero los de la carpeta del programa). */
export function archivosParaServidor(py, ruta, { max = 80, total = 1_800_000 } = {}) {
  const dir = FS.carpetaDe(ruta);
  const todas = Object.keys(py.files).filter((r) => TEXTO.test(r) && !esMarcador(py.files[r]) && !/(^|\/)(node_modules|\.git|venv|\.venv|__pycache__)\//.test(r));
  todas.sort((a, b) => (a === ruta ? -1 : b === ruta ? 1 : (FS.dentroDe(b, dir) || FS.carpetaDe(b) === dir) - (FS.dentroDe(a, dir) || FS.carpetaDe(a) === dir) || a.localeCompare(b)));
  const out = [];
  let suma = 0;
  for (const r of todas) {
    const c = py.files[r];
    if (out.length >= max || suma + c.length > total) break;
    suma += c.length;
    out.push({ ruta: r, contenido: c });
  }
  return out;
}
