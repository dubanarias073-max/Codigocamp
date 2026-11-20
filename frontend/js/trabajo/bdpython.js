// Bases de datos, internet, correo y Google para el Python del navegador (servidores Flask/FastAPI/Django y `python archivo.py`).
// 1. Con el puente de CódigoCamp (ClienteBD), pymysql / mysql.connector / psycopg2 / pymongo van a tu servidor real
//    (el MySQL de XAMPP, por ejemplo) y SQLAlchemy usa ese mismo camino.
// 2. Si no se puede llegar a tu servidor, cada conexión pasa sola a una base SQLite real dentro del proyecto
//    (.codigocamp/bd/<base>.db) e importa tu .sql la primera vez. Así la app arranca siempre (ver bd_py.py).
import { instalarMysqlEnPython } from "./pymysql.js";

const fuentes = new Map();
const cargarFuente = (fetchFn, archivo = "bd_py.py") => {
  if (!fuentes.has(archivo)) {
    fuentes.set(archivo, fetchFn(`/js/trabajo/${archivo}`)
      .then((r) => { if (!r.ok) throw new Error(`no se pudo cargar ${archivo}`); return r.text(); })
      .catch((e) => { fuentes.delete(archivo); throw e; }));
  }
  return fuentes.get(archivo);
};

const csrf = () => (globalThis.document?.cookie?.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
/** Petición síncrona a /api/trabajo/<accion> (Python no puede esperar promesas). Devuelve el JSON en texto. */
export function pedirRedSync(accion, datos, XHR = globalThis.XMLHttpRequest) {
  const x = new XHR();
  x.open("POST", `/api/trabajo/${accion}`, false);
  x.setRequestHeader("Content-Type", "application/json");
  x.setRequestHeader("X-CSRFToken", csrf());
  try { x.send(datos); } catch { return JSON.stringify({ __error: "No se pudo hablar con el servidor de CódigoCamp (¿sin internet?).", estado: 0 }); }
  if (x.status >= 200 && x.status < 300) return x.responseText || "{}";
  let j = {};
  try { j = JSON.parse(x.responseText || "{}"); } catch { /* nada */ }
  return JSON.stringify({ __error: j.error || `Error ${x.status} de CódigoCamp`, estado: x.status });
}

/**
 * Deja listos `preparar_bd(raiz)` y `guardar_mongo()` en el Python global.
 * @returns {Promise<boolean>} true si se usa el puente a tu servidor real.
 */
export async function prepararBdPython(pyo, { bd = null, fetchFn = (...a) => fetch(...a), codigo = null } = {}) {
  const src = codigo ?? await cargarFuente(fetchFn);
  try { await pyo.loadPackage("sqlite3"); } catch { /* sin SQLite: solo el puente a tu servidor */ }
  let puente = false;
  if (bd) {
    try { instalarMysqlEnPython(pyo, bd); puente = true; } catch { puente = false; }
  }
  // Internet, correo y Google (red_py.py): requests/httpx/urllib, smtplib y google-auth pasan por CódigoCamp.
  let red = "";
  try { red = await cargarFuente(fetchFn, "red_py.py"); } catch { red = ""; }
  try { pyo.registerJsModule("_cc_red", { pedir: (accion, datos) => pedirRedSync(String(accion), String(datos)) }); } catch { /* nada */ }
  pyo.globals.set("_cc_bd_fuente", src);
  pyo.globals.set("_cc_red_fuente", red);
  pyo.runPython(`import sys, types
_m = types.ModuleType("_cc_bdpy")
exec(compile(_cc_bd_fuente, "bd_py.py", "exec"), _m.__dict__)
sys.modules["_cc_bdpy"] = _m
_r = None
if _cc_red_fuente:
    _r = types.ModuleType("_cc_redpy")
    exec(compile(_cc_red_fuente, "red_py.py", "exec"), _r.__dict__)
    sys.modules["_cc_redpy"] = _r
def preparar_bd(r, _p=${puente ? "True" : "False"}, _m=_m, _r=_r):
    _m.preparar(r, puente=_p)
    if _r is not None:
        _r.activar()
guardar_mongo = _m.guardar_mongo
del _cc_bd_fuente, _cc_red_fuente`);
  return puente;
}

/** ¿El proyecto usa MongoDB? (para instalar antes el respaldo mongomock, que es Python puro) */
export const usaMongo = (fuentes) => /^\s*(?:from|import)\s+(?:pymongo|bson|mongoengine)\b/m.test(fuentes);
