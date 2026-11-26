// Servidores de Python en Trabajo, como en VS Code: `fastapi dev main.py`, `uvicorn main:app --reload`, `flask --app web run`.
// La app corre en Pyodide y la vista previa le manda las peticiones (incluidas las de /docs de FastAPI y los fetch
// de tu página) a http://127.0.0.1:<puerto>. Con --reload (o fastapi dev / flask --debug) se recarga al guardar.
import { color } from "./ansi.js";
import * as FS from "./fs.js";
import {
  aplicarCambios, binariosParaPython, borrarEnPyodide, cargarPyodide, consolidarBinarios, diferencias,
  cargarStdlibAparte, escribirEnPyodide, generacionFsPy, leerDePyodide, nuevaGeneracionFsPy, RAIZ_PY, STDLIB_APARTE, textoError,
} from "./ejecucion.js";
import { ejecutarPip, restaurarPaquetes, sugerenciaPython } from "./paquetes.js";
import { importsDelProyecto, importsDesde, pipDeImport } from "./extensiones.js";
import { prepararBdPython, usaMongo } from "./bdpython.js";
import { cerrarMysqlEnPython } from "./pymysql.js";

// Los servidores viven en el registro común de puertos (panel PUERTOS, vista previa, Node, PHP…)
import { alCambiarServidores, avisar, cambioProyecto, esperarDetencion, servidores } from "./puertos.js";
export { alCambiarServidores, servidores };
/** Trabajo lo llama en cada cambio del proyecto: los servidores con recarga se actualizan en la siguiente petición. */
export function marcarCambio(origen) { cambioProyecto(origen); }

const ESTADOS = { 200: "OK", 201: "Created", 202: "Accepted", 204: "No Content", 301: "Moved Permanently", 302: "Found", 303: "See Other", 304: "Not Modified", 307: "Temporary Redirect", 308: "Permanent Redirect", 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 405: "Method Not Allowed", 409: "Conflict", 422: "Unprocessable Entity", 429: "Too Many Requests", 500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable" };
const aB64 = (bytes) => { let s = ""; const u = new Uint8Array(bytes); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode(...u.subarray(i, i + 0x8000)); return btoa(s); };
const deB64 = (t) => Uint8Array.from(atob(t), (c) => c.charCodeAt(0));
const sha256Hex = async (bytes) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map((b) => b.toString(16).padStart(2, "0")).join("");

let codigoServidor = null;
async function fuenteServidor() {
  codigoServidor ??= fetch("/js/trabajo/servidor_py.py").then((r) => { if (!r.ok) throw new Error("no se pudo cargar el servidor de Python"); return r.text(); })
    .catch((e) => { codigoServidor = null; throw e; });
  return codigoServidor;
}

/** Archivo de la app para `fastapi dev` sin argumentos (mismo orden que FastAPI CLI). */
export function buscarArchivoApp(py, cwd = "") {
  for (const c of ["main.py", "app.py", "api.py", "app/main.py", "app/app.py", "api/main.py", "api/app.py"]) {
    const r = FS.unir(cwd, c);
    if (FS.tieneArchivo(py, r)) return r;
  }
  return null;
}

/** De «app/main.py» a { modulo: "app.main", carpeta: "" } si app/ es un paquete (tiene __init__.py), como hace FastAPI CLI. */
export function moduloDeArchivo(py, ruta) {
  let carpeta = FS.carpetaDe(ruta);
  const partes = [FS.nombreBase(ruta).replace(/\.py$/, "")];
  while (carpeta && FS.tieneArchivo(py, FS.unir(carpeta, "__init__.py"))) { partes.unshift(FS.nombreBase(carpeta)); carpeta = FS.carpetaDe(carpeta); }
  return { modulo: partes.join("."), carpeta };
}

const IMPORTA = { fastapi: /^\s*(?:from|import)\s+fastapi\b/m, flask: /^\s*(?:from|import)\s+flask\b/m, starlette: /^\s*(?:from|import)\s+starlette\b/m, django: /^\s*(?:from|import)\s+django\b/m };

/** Qué paquete de pip necesita el servidor (según el comando y lo que importa el código). */
function paqueteNecesario(py, estilo, entrada = null) {
  if (estilo === "flask") return "flask";
  if (estilo === "django") return "django";
  const fuentes = entrada && typeof py.files[entrada] === "string" ? py.files[entrada]
    : Object.entries(py.files).filter(([r]) => r.endsWith(".py")).map(([, t]) => t).join("\n");
  if (estilo.startsWith("fastapi") || IMPORTA.fastapi.test(fuentes)) return "fastapi";
  if (IMPORTA.starlette.test(fuentes)) return "starlette";
  if (IMPORTA.flask.test(fuentes)) return "flask";
  return null;
}

/**
 * Enciende el servidor y no termina hasta Ctrl+C (o hasta que se detiene la terminal).
 * @param {object} o { proyecto, cwd, out, err, senal, leerLinea, cambio, almacenPip, archivos, spec, carpetaModulo, factory, host, puerto, recargar, estilo, abrir(url), archivo }
 */
export async function ejecutarServidorPy(o) {
  const py = o.proyecto;
  const host = o.host || "127.0.0.1";
  const puerto = Number(o.puerto) || (o.estilo === "flask" ? 5000 : 8000);
  const url = `http://${host === "0.0.0.0" ? "127.0.0.1" : host}:${puerto}`;
  const fastapi = o.estilo === "fastapi-dev" || o.estilo === "fastapi-run";
  const linea = (nivel, texto) => (fastapi ? `${color.verde(nivel.padStart(8))}   ${texto}\n` : `${nivel === "ERROR" ? color.rojo(nivel + ":") : color.verde(nivel + ":")}${" ".repeat(Math.max(1, 9 - nivel.length))}${texto}\n`);
  if (servidores.has(puerto)) { o.err(linea("ERROR", `[Errno 98] Address already in use: ya hay un servidor en ${url}. Detén el otro (Ctrl+C) o usa --port ${puerto + 1}`)); return 1; }

  let pyo;
  try {
    o.out(color.gris("Cargando Python (solo la primera vez, puede tardar unos segundos)…\n"));
    pyo = await cargarPyodide();
  } catch (e) { o.err(`${e.message}\n`); return 1; }
  if (o.senal?.aborted) return 130;
  if (o.almacenPip) await restaurarPaquetes({ pyo, lista: o.almacenPip.leer(), out: o.out, err: o.err });

  // Paquetes de Pyodide que importa el proyecto (sqlalchemy, numpy, pydantic…): se cargan solos.
  const todoPy = Object.entries(py.files).filter(([r, t]) => r.endsWith(".py") && t.length < 200_000 && !/(^|\/)(site-packages|\.?venv)\//.test(r)).map(([, t]) => t).join("\n");
  const fuentes = todoPy.replace(/^\s*(?:import|from)\s+(?:pymysql|mysql|MySQLdb|psycopg2?|pymongo|bson|redis|uvicorn|flask_mysqldb)\b.*$/gm, "");
  try { await pyo.loadPackagesFromImports(fuentes); } catch { /* el import dará su propio error */ }
  // ssl, hashlib y sqlite3 vienen aparte en Pyodide y FastAPI/Flask/Django los usan por dentro (anyio importa ssl).
  await cargarStdlibAparte(pyo, undefined, `${fuentes}\n${o.estilo === "django" ? "django" : ""}`);

  // Como VS Code: TODO lo que tu proyecto importa y no está instalado (el framework, sus extensiones, dotenv…),
  // en una sola pregunta. Lo que no existe para el navegador se avisa antes, con alternativa.
  const instalar = async (nombres, motivo) => {
    if (!nombres.length) return true;
    o.err(`${color.rojo("ModuleNotFoundError:")} ${motivo}\n`);
    o.err(`${color.amarillo("→")} Falta instalar ${nombres.map((n) => color.negrita(n)).join(", ")}${o.almacenPip?.venv ? ` en el entorno «${o.almacenPip.venv}»` : ""}:  ${color.cian(`pip install ${nombres.join(" ")}`)}\n`);
    const r = o.leerLinea ? await o.leerLinea(`¿Instalar ${nombres.length > 1 ? "todo" : nombres[0]} ahora? [S/n] `) : "s";
    if (r === null || /^n/i.test(String(r).trim())) return false;
    try { await ejecutarPip({ args: ["install", ...nombres], proyecto: py, cwd: o.cwd, out: o.out, err: o.err, cargarPy: async () => pyo, almacen: o.almacenPip }); }
    catch (e) { o.err(`${color.rojo("ERROR:")} no se pudo instalar (${String(e.message).split("\n").find((l) => /Error|error/.test(l)) || e.message}). ¿Tienes internet?\n`); }
    try { await pyo.loadPackagesFromImports(fuentes); } catch { /* nada */ }
    return true;   // aunque alguno no se pudiera (p. ej. un import opcional), se intenta arrancar: el error real lo dirá Python
  };
  // El archivo de la app que se enciende (no todo el proyecto: otro .py puede usar otro framework).
  const entradaApp = (() => {
    if (o.estilo === "django" || !o.spec) return null;
    const partes = String(o.spec).split(":")[0].split(".").filter(Boolean);
    const base = [o.carpetaModulo || o.cwd || "", ...partes].filter(Boolean).join("/");
    return [`${base}.py`, `${base}/__init__.py`].find((r) => typeof py.files[r] === "string") ?? null;
  })();
  const faltantes = () => {
    const soloCarpeta = (c) => (c ? { files: Object.fromEntries(Object.entries(py.files).filter(([r]) => r.startsWith(c + "/"))), folders: py.folders.filter((f) => f.startsWith(c + "/")) } : py);
    const mods = [...new Set([...(entradaApp ? importsDesde(py, entradaApp) : importsDelProyecto(o.estilo === "django" ? soloCarpeta(o.carpetaModulo) : py)), ...(paqueteNecesario(py, o.estilo, entradaApp) ? [paqueteNecesario(py, o.estilo, entradaApp)] : [])])];
    if (!mods.length) return [];
    const sinInstalar = JSON.parse(pyo.runPython(`import importlib.util as _u, json as _j\n_j.dumps([m for m in ${JSON.stringify(mods)} if _u.find_spec(m) is None])`));
    return [...new Set(sinInstalar.map(pipDeImport))];
  };
  const falta = faltantes();
  if (falta.length) await instalar(falta, falta.length > 1 ? `tu proyecto usa ${falta.length} paquetes que no están instalados` : `No module named '${falta[0]}'`);

  // Bases de datos: tu MySQL/PostgreSQL/MongoDB real por el puente de CódigoCamp o, si no se puede llegar, SQLite.
  let puente = false;
  try {
    puente = await prepararBdPython(pyo, { bd: o.bd ?? null, codigo: o.fuenteBd ?? null });
    if (usaMongo(todoPy) && !pyo.runPython("import importlib.util as _u\n_u.find_spec('mongomock') is not None")) {
      try { await pyo.loadPackage("micropip"); await pyo.pyimport("micropip").install("mongomock"); } catch { /* sin respaldo de MongoDB */ }
    }
  } catch (e) { o.err(color.gris(`(bases de datos: ${e.message})\n`)); }

  // Archivos del proyecto en /workspace (y lo que la app escriba, p. ej. una base SQLite, vuelve al proyecto).
  let antes = null, generacion = 0, firmaPy = "";
  const firma = () => Object.entries(py.files).filter(([r]) => r.endsWith(".py")).map(([r, t]) => `${r}\u0000${t}`).sort().join("\u0001");
  const sincronizar = async () => {
    // Primero se preparan los binarios (es asíncrono) y DESPUÉS se vacía y reescribe /workspace de una sola vez:
    // antes se vaciaba y luego se esperaba, y si en ese momento llegaba una petición, guardarCambios leía la carpeta
    // vacía y creía que el programa había borrado todo el proyecto (se guardaba vacío en la cuenta).
    antes = null;
    const binarios = await binariosParaPython(py, o.archivos);
    generacion = nuevaGeneracionFsPy();
    borrarEnPyodide(pyo);
    escribirEnPyodide(pyo, py, binarios);
    antes = { files: { ...py.files }, folders: [...py.folders] };
  };
  const guardarCambios = async () => {
    if (!antes || generacion !== generacionFsPy) return;
    try {
      const despues = await consolidarBinarios(antes, leerDePyodide(pyo), { subir: o.archivos ? (b, op) => o.archivos.subir(b, op) : null, hash: sha256Hex, err: o.err });
      const cambios = diferencias(antes, despues);
      if (aplicarCambios(py, cambios)) { o.cambio?.({}); antes = { files: { ...py.files }, folders: [...py.folders] }; }
    } catch { /* nada que guardar */ }
  };

  const cwdPy = `${RAIZ_PY}${o.cwd ? "/" + o.cwd : ""}`;
  const dirModulo = `${RAIZ_PY}${o.carpetaModulo ? "/" + o.carpetaModulo : o.cwd ? "/" + o.cwd : ""}`;
  pyo.setStdout({ batched: (s) => o.out(s + "\n") });
  pyo.setStderr({ batched: (s) => o.err(color.rojo(s) + "\n") });
  let srv;
  const cargar = async () => {
    pyo.FS.chdir(cwdPy);
    pyo.runPython(`import sys\nfor _p in (${JSON.stringify(dirModulo)}, ${JSON.stringify(cwdPy)}):\n    if _p not in sys.path: sys.path.insert(0, _p)`);
    const info = JSON.parse(await srv.cargar());
    return info;
  };

  let info;
  try {
    await sincronizar();
    firmaPy = firma();
    pyo.runPython(await fuenteServidor());
    srv = pyo.globals.get("_CCServidor")(RAIZ_PY, o.spec, Boolean(o.factory));
    if (fastapi) {
      const rel = o.archivo || "";
      o.out(`\n ${color.negrita(color.verde("FastAPI"))}   Starting ${o.estilo === "fastapi-dev" ? "development" : "production"} server 🚀\n\n`);
      o.out(`           Searching for package file structure from directories with ${color.cian("__init__.py")} files\n           Importing from ${dirModulo}\n\n`);
      o.out(` ${color.verde("  module")}   🐍 ${rel || o.spec.split(":")[0] + ".py"}\n\n`);
      o.out(` ${color.verde("    code")}   Importing the FastAPI app object from the module with the following code:\n\n           ${color.negrita(`from ${o.spec.split(":")[0]} import ${o.spec.split(":")[1] || "app"}`)}\n\n`);
    }
    if (o.estilo === "flask") o.out(` * Serving Flask app '${o.spec.split(":")[0]}'\n * Debug mode: ${o.recargar ? "on" : "off"}\n`);
    if (o.estilo === "django") o.out("Watching for file changes with StatReloader\nPerforming system checks...\n\n");
    // Si al importar aparece un paquete que no se detectó antes, se ofrece instalarlo y se vuelve a intentar.
    for (let intento = 0; ; intento += 1) {
      try { info = await cargar(); break; }
      catch (e) {
        const m = /No module named '([\w.]+)'/.exec(String(e.message));
        const mod = m?.[1].split(".")[0];
        if (m && intento < 3 && STDLIB_APARTE[mod]) { await cargarStdlibAparte(pyo, [STDLIB_APARTE[mod]]); await sincronizar(); continue; }
        if (!m || intento >= 3 || !mod || FS.tieneArchivo(py, FS.unir(o.cwd, mod + ".py")) || py.folders.some((c) => FS.nombreBase(c) === mod)) throw e;
        if (!(await instalar([pipDeImport(mod)], `No module named '${m[1]}'`))) throw e;
        await sincronizar();
      }
    }
  } catch (e) {
    o.err(textoError(e).split("\n").filter((l) => !/_pyodide|pyodide\/|python3\d+\.zip/.test(l)).join("\n") + "\n");
    const ayuda = sugerenciaPython(textoError(e), { py, cwd: o.cwd, venv: o.almacenPip?.venv ?? null });
    if (ayuda) o.err(color.amarillo(ayuda) + "\n");
    o.err(linea("ERROR", "Error loading ASGI app. Revisa el error de arriba (la última línea dice qué pasó).")
      .replace("ASGI", o.estilo === "flask" ? "Flask" : o.estilo === "django" ? "Django" : "ASGI"));
    try { await guardarCambios(); borrarEnPyodide(pyo); } catch { /* nada */ }
    if (puente) cerrarMysqlEnPython(pyo);
    return 1;
  }

  if (fastapi) {
    o.out(` ${color.verde("     app")}   Using import string: ${color.cian(o.spec)}\n\n`);
    o.out(` ${color.verde("  server")}   Server started at ${color.cian(url)}\n ${color.verde("  server")}   Documentation at ${color.cian(url + "/docs")}\n\n`);
    if (o.estilo === "fastapi-dev") o.out(` ${color.verde("     tip")}   Running in development mode, for production use: ${color.negrita("fastapi run")}\n\n`);
    o.out("           Logs:\n\n");
  }
  if (o.estilo === "django") {
    o.out(`System check identified no issues (0 silenced).\n`);
    if (info.sin_migrar) o.out(`\n${color.rojo(`You have ${info.sin_migrar} unapplied migration(s). Your project may not work properly until you apply the migrations for app(s).`)}\n${color.rojo("Run 'python manage.py migrate' to apply them.")}\n`);
    const f = new Date();
    o.out(`${f.toLocaleDateString("en-US", { month: "long", day: "2-digit", year: "numeric" })} - ${f.toTimeString().slice(0, 8)}\nDjango version ${info.version}, using settings '${info.modulo}'\nStarting development server at ${url}/\nQuit the server with CONTROL-C.\n\n`);
  } else if (o.estilo === "flask") {
    o.out(`${color.rojo(color.negrita("WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead."))}\n * Running on ${url}\n${color.amarillo("Press CTRL+C to quit")}\n`);
    if (o.recargar) o.out(" * Restarting with stat\n * Debugger is active!\n");
  } else {
    if (o.recargar) o.out(linea("INFO", `Will watch for changes in these directories: ['${cwdPy}']`));
    o.out(linea("INFO", `Uvicorn running on ${color.negrita(url)} (Press CTRL+C to quit)`));
    if (o.recargar) o.out(linea("INFO", `Started reloader process [${4000 + puerto % 1000}] using ${color.cian("WatchFiles")}`));
    o.out(linea("INFO", `Started server process [${4100 + puerto % 1000}]`));
    o.out(linea("INFO", "Waiting for application startup."));
    o.out(linea("INFO", "Application startup complete."));
  }
  o.out(color.gris(`  → La vista previa abre ${url}${fastapi ? "/docs" : "/"} · Abre otra terminal (+) para seguir escribiendo comandos · Ctrl+C detiene el servidor\n`));

  // Una petición a la vez (como un solo worker); con recarga, antes de atender mira si cambió el código.
  let cola = Promise.resolve();
  let guardado = 0;
  const registro = {
    url, puerto, tipo: info.tipo, framework: ["FastAPI", "Flask", "Starlette", "Quart", "Litestar", "Django"].includes(info.clase) ? info.clase : `Python ${info.tipo}`, sucio: false,
    pedir: (req) => {
      const tarea = cola.then(async () => {
        if (generacion !== generacionFsPy || registro.sucio) {
          registro.sucio = false;
          const nueva = firma();
          if (o.recargar && nueva !== firmaPy) {
            await guardarCambios();
            await sincronizar();
            const cambiados = Object.keys(py.files).filter((r) => r.endsWith(".py")).filter((r) => antes.files[r] !== undefined).slice(0, 3);
            o.out(o.estilo === "flask" ? ` * Detected change, reloading\n * Restarting with stat\n` : o.estilo === "django" ? `${color.gris("Detected change, reloading.")}\nWatching for file changes with StatReloader\n` : linea("WARNING", `WatchFiles detected changes in ${cambiados.map((c) => `'${c}'`).join(", ") || "the project"}. Reloading...`));
            firmaPy = nueva;
            try { await cargar(); if (o.estilo !== "flask" && o.estilo !== "django") o.out(linea("INFO", "Application startup complete.")); }
            catch (e) {
              o.err(textoError(e).split("\n").filter((l) => !/_pyodide|pyodide\/|python3\d+\.zip/.test(l)).join("\n") + "\n");
              const ayuda = sugerenciaPython(textoError(e), { py, cwd: o.cwd, venv: o.almacenPip?.venv ?? null });
              if (ayuda) o.err(color.amarillo(ayuda) + "\n");
            }
          } else {
            // Plantillas, estáticos o una ejecución de Python en otra terminal: se vuelve a copiar el proyecto.
            await guardarCambios();
            await sincronizar();
          }
        }
        const [ruta, consulta = ""] = String(req.url || "/").split(/\?(.*)/s);
        const cabeceras = [["host", `${host}:${puerto}`], ...(req.headers || [])];
        const cuerpo = req.body ? aB64(req.body) : "";
        let r;
        try { r = JSON.parse(await srv.pedir(req.method || "GET", decodeURIComponent(ruta || "/"), consulta, JSON.stringify(cabeceras), cuerpo)); }
        catch (e) { o.err(textoError(e) + "\n"); r = { status: 500, headers: [["content-type", "text/plain"]], body: btoa("Internal Server Error") }; }
        const texto = `127.0.0.1:52000 - "${(req.method || "GET").toUpperCase()} ${req.url || "/"} HTTP/1.1" `;
        const codigo = r.status >= 500 ? color.rojo(String(r.status)) : r.status >= 400 ? color.amarillo(String(r.status)) : color.verde(String(r.status));
        if (o.estilo === "flask" || o.estilo === "django") {
          const f = new Date();
          o.out(`127.0.0.1 - - [${f.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).replace(/ /g, "/")} ${f.toTimeString().slice(0, 8)}] "${(req.method || "GET").toUpperCase()} ${req.url || "/"} HTTP/1.1" ${r.status} -\n`);
        } else o.out(linea("INFO", texto + codigo + (fastapi ? "" : " " + (ESTADOS[r.status] || ""))));
        if ((req.method || "GET").toUpperCase() !== "GET" && Date.now() - guardado > 300) { guardado = Date.now(); await guardarCambios(); }
        return { status: r.status, headers: r.headers, body: deB64(r.body) };
      });
      cola = tarea.catch(() => {});
      return tarea;
    },
  };
  registro.comando = o.comando || registro.framework;
  servidores.set(puerto, registro);
  avisar();
  o.abrir?.(url + (fastapi ? "/docs" : "/"));

  await esperarDetencion(o.senal, puerto);

  servidores.delete(puerto);
  avisar();
  try { await cola; } catch { /* nada */ }
  if (o.estilo === "flask" || o.estilo === "django") o.out("\n");
  else {
    o.out(linea("INFO", "Shutting down"));
    o.out(linea("INFO", "Waiting for application shutdown."));
  }
  try { await srv.cerrar(); } catch { /* nada */ }
  if (o.estilo !== "flask" && o.estilo !== "django") {
    o.out(linea("INFO", "Application shutdown complete."));
    o.out(linea("INFO", `Finished server process [${4100 + puerto % 1000}]`));
  }
  await guardarCambios();
  if (puente) cerrarMysqlEnPython(pyo);
  try { if (generacion === generacionFsPy) borrarEnPyodide(pyo); srv.destroy?.(); } catch { /* nada */ }
  return 0;
}
