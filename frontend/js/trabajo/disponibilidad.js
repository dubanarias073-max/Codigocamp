// ¿Se puede instalar este paquete de Python en Trabajo?
// Trabajo ejecuta Python en el navegador (Pyodide). Ahí funcionan:
//   · los ~300 paquetes que Pyodide ya trae compilados (numpy, pandas, scipy, scikit-learn, cryptography, bcrypt…)
//   · cualquier paquete de Python puro de PyPI (los que publican una rueda «py3-none-any»)
// No funcionan los que solo traen código en C/Rust compilado para Windows/Linux/macOS (torch, psutil, mysqlclient…).
// Esto se consulta ANTES de instalar, para decirlo claro y proponer una alternativa en vez de un error largo.

const normalizar = (n) => String(n).toLowerCase().replace(/[-_.]+/g, "-");

// Alternativas que sí funcionan en CódigoCamp.
export const ALTERNATIVAS = {
  "mysqlclient": "pymysql (ya incluido: import pymysql)",
  "mysql-connector": "mysql-connector-python (ya incluido)",
  "psycopg2-binary": "psycopg2 (ya incluido)",
  "psycopg-binary": "psycopg (ya incluido)",
  "pyodbc": "pymysql o psycopg2 (ya incluidos)",
  "cx-oracle": "pymysql o psycopg2 (ya incluidos)",
  "oracledb": "pymysql o psycopg2 (ya incluidos)",
  "torch": "scikit-learn (incluido) para aprendizaje automático en el navegador",
  "tensorflow": "scikit-learn (incluido) para aprendizaje automático en el navegador",
  "keras": "scikit-learn (incluido)",
  "numba": "numpy (incluido)",
  "psutil": "no hace falta en el navegador; quítalo si tu código no lo importa",
  "uvloop": "no hace falta: CódigoCamp ya sirve tu app",
  "grpcio": "requests o httpx (peticiones HTTP)",
  "selenium": "requests + beautifulsoup4 para leer páginas",
  "playwright": "requests + beautifulsoup4 para leer páginas",
  "pyqt5": "una página web con Flask o FastAPI (las ventanas de escritorio no existen en el navegador)",
  "pyqt6": "una página web con Flask o FastAPI",
  "pyside6": "una página web con Flask o FastAPI",
  "kivy": "pygame-ce (incluido) o una página web",
  "pygame": "pygame-ce (incluido: pip install pygame-ce)",
  "opencv-contrib-python": "opencv-python (incluido)",
  "opencv-python-headless": "opencv-python (incluido)",
  "pandas-profiling": "pandas (incluido)",
};

let lockPromesa = null;
/** Nombres de los paquetes que Pyodide trae listos (del pyodide-lock.json incluido en /vendor). */
export function paquetesPyodide(fetchFn = (...a) => fetch(...a)) {
  lockPromesa ??= fetchFn("/vendor/pyodide/pyodide-lock.json")
    .then((r) => (r.ok ? r.json() : { packages: {} }))
    .then((j) => new Set(Object.keys(j.packages || {}).map(normalizar)))
    .catch(() => { lockPromesa = null; return new Set(); });
  return lockPromesa;
}

/** Decide con los datos de PyPI (respuesta de /pypi/<n>/json). Exportada para las pruebas. */
export function decidirPorPyPI(json) {
  const archivos = json?.urls || [];
  const ruedas = archivos.filter((a) => /\.whl$/i.test(a.filename || ""));
  if (ruedas.some((a) => /-none-any\.whl$/i.test(a.filename))) return { ok: true, como: "Python puro" };
  if (ruedas.some((a) => /(emscripten|pyodide)/i.test(a.filename))) return { ok: true, como: "rueda para navegador" };
  if (!archivos.length) return { ok: false, motivo: "no publica archivos para instalar" };
  if (!ruedas.length) return { ok: false, motivo: "solo publica el código fuente (hay que compilarlo) y el navegador no puede compilar" };
  return { ok: false, motivo: "tiene código compilado (C/C++/Rust) solo para Windows, Linux o macOS, no para el navegador" };
}

const cache = new Map();
/**
 * @returns {Promise<{ok:boolean, como?:string, motivo?:string, alternativa?:string, existe?:boolean}>}
 */
export function revisarPip(nombre, fetchFn = (...a) => fetch(...a)) {
  const n = normalizar(nombre);
  if (!cache.has(n)) {
    cache.set(n, (async () => {
      const alternativa = ALTERNATIVAS[n];
      if ((await paquetesPyodide(fetchFn)).has(n)) return { ok: true, como: "incluido en Python del navegador" };
      let r;
      try { r = await fetchFn(`https://pypi.org/pypi/${encodeURIComponent(n)}/json`); }
      catch { cache.delete(n); return { ok: true, como: "sin comprobar (sin conexión)" }; }   // sin red: se deja intentar
      if (r.status === 404) return { ok: false, existe: false, motivo: "no existe en PyPI (revisa el nombre)", alternativa };
      if (!r.ok) { cache.delete(n); return { ok: true, como: "sin comprobar" }; }
      const d = decidirPorPyPI(await r.json());
      return d.ok ? d : { ...d, alternativa };
    })());
  }
  return cache.get(n);
}

/** Dependencias obligatorias (sin «extras» opcionales) según PyPI, para instalarlas una por una. */
export async function dependenciasPip(nombre, fetchFn = (...a) => fetch(...a)) {
  try {
    const r = await fetchFn(`https://pypi.org/pypi/${encodeURIComponent(normalizar(nombre))}/json`);
    if (!r.ok) return [];
    const req = (await r.json()).info?.requires_dist || [];
    return req.filter((x) => !/extra\s*==/.test(x) && !/sys_platform\s*==\s*["'](win32|darwin)/.test(x) && !/platform_system\s*==\s*["'](Windows|Darwin)/.test(x))
      .map((x) => x.split(";")[0].trim().split(/[\s(<>=!~[]/)[0]).filter(Boolean);
  } catch { return []; }
}

export function _limpiarCache() { cache.clear(); lockPromesa = null; }
