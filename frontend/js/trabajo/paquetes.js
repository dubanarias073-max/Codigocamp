// Gestores de paquetes de la terminal.
//
//  · pip  -> micropip dentro de Pyodide. Instala paquetes de Python puro desde PyPI y los que Pyodide trae ya
//            compilados (numpy, pandas, matplotlib, scipy, scikit-learn…). Lo instalado se recuerda en este
//            navegador y se reinstala solo la próxima vez que ejecutes Python.
//  · npm  -> mantiene el package.json de verdad (init, install, uninstall, run, start, test, ls). Los paquetes no se
//            descargan a node_modules (el proyecto no tiene espacio para eso): cuando haces `import x from "x"` el
//            ejecutor de Node los carga desde el CDN esm.sh con la versión que dice tu package.json.
import { color } from "./ansi.js";
import * as FS from "./fs.js";
import { dependenciasPip, revisarPip } from "./disponibilidad.js";
import { PAQUETES, PLANTILLAS, VERSIONES_RESPALDO, archivosDePlantilla } from "./plantillas.js";

// ================================================================================= pip ====
const ESPEC_PIP = /^[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[A-Za-z0-9,._-]+\])?(?:(?:==|>=|<=|~=|!=|>|<)[A-Za-z0-9.*+!_-]+(?:,(?:==|>=|<=|~=|!=|>|<)[A-Za-z0-9.*+!_-]+)*)?$/;
const nombreDe = (espec) => espec.replace(/\[.*$/, "").split(/[=<>~!]/)[0].toLowerCase().replace(/[-_.]+/g, "-");
const instaladosEnSesion = new Set();

function explicarErrorPip(mensaje) {
  const m = String(mensaje);
  if (/Can't find a pure Python 3 wheel/i.test(m)) return `${m.split("\n")[0]}\nEse paquete incluye código compilado que no existe para el navegador. Solo se pueden instalar paquetes de Python puro y los que trae Pyodide (numpy, pandas, matplotlib, scipy, scikit-learn…).`;
  if (/Failed to fetch|NetworkError|network/i.test(m)) return "No se pudo conectar con PyPI. Revisa tu conexión.";
  return m.split("\n").filter((l) => !/_pyodide|pyodide\/|\.zip\//.test(l)).join("\n").trim();
}

/** Instala de nuevo lo que la persona instaló antes (una vez por pestaña). Lo usa ejecutarPython. */
export async function restaurarPaquetes({ pyo, lista, out = () => {}, err = () => {} }) {
  const faltan = lista.filter((e) => ESPEC_PIP.test(e) && !instaladosEnSesion.has(nombreDe(e))); // lo guardado en el navegador también se valida
  if (!faltan.length) return;
  out(color.gris(`Instalando paquetes guardados: ${faltan.join(", ")}…\n`));
  let micropip;
  try { await pyo.loadPackage("micropip"); micropip = pyo.pyimport("micropip"); }
  catch (error) { err(`No se pudieron restaurar los paquetes: ${explicarErrorPip(error.message)}\n`); return; }
  for (const e of faltan) {
    try { await instalarTolerante(micropip, e); instaladosEnSesion.add(nombreDe(e)); }
    catch (error) { err(`No se pudo restaurar ${e}: ${explicarErrorPip(error.message).split("\n")[0]}\n`); }
  }
}

/**
 * Instala como pip pero sin rendirse al primer problema (como hace VS Code con un requirements.txt grande):
 *  1. tal cual;  2. sin versión exacta ni extras;  3. el paquete solo y luego cada dependencia aparte,
 *  saltando las que no existen para el navegador (casi siempre opcionales para lo que usa tu código).
 */
export async function instalarTolerante(micropip, espec, { deps = dependenciasPip } = {}) {
  try { await micropip.install(espec); return { instalado: espec }; }
  catch (primero) {
    const simple = espec.replace(/\[.*?\]/, "").split(/[=<>~!]/)[0];
    if (simple !== espec) {
      try { await micropip.install(simple); return { instalado: simple, aviso: `${espec} no está disponible para el navegador; se instaló ${simple} (la versión más parecida).` }; }
      catch { /* se intenta por partes */ }
    }
    try { await micropip.install.callKwargs(simple, { deps: false }); }
    catch { throw primero; }
    const saltadas = [];
    for (const d of await deps(simple)) {
      try { await micropip.install(d); } catch { saltadas.push(d); }
    }
    return { instalado: simple, aviso: saltadas.length ? `${simple} se instaló sin ${saltadas.join(", ")} (no existe${saltadas.length > 1 ? "n" : ""} para el navegador). Si tu código no lo${saltadas.length > 1 ? "s" : ""} importa directamente, funciona igual.` : null };
  }
}

// Lo que en tu PC hace de servidor web: aquí no se instala porque CódigoCamp sirve la app (fastapi dev, uvicorn, flask run).
const SERVIDORES = new Set(["uvicorn", "gunicorn", "uvloop", "httptools", "watchfiles", "hypercorn", "waitress", "daphne", "fastapi-cli", "gevent", "eventlet", "granian"]);
// Solo existen para Windows / macOS o necesitan el sistema: se omiten.
const DEL_SISTEMA = new Set(["pywin32", "pywin32-ctypes", "pypiwin32", "pyobjc", "appnope", "colorama-win", "wmi", "pyinstaller", "pyinstaller-hooks-contrib", "pip", "setuptools", "wheel"]);

/** Limpia una línea de requirements.txt: quita marcadores de entorno («; python_version…»), espacios y hashes. */
export function limpiarRequisito(linea) {
  return linea.replace(/#.*/, "").replace(/\s--hash=\S+/g, "").split(";")[0].replace(/\s+/g, "").trim();
}

/**
 * @param {object} o
 * @param {string[]} o.args       argumentos después de «pip»
 * @param {object} o.proyecto     para -r requirements.txt
 * @param {string} o.cwd
 * @param {()=>Promise<object>} o.cargarPy   devuelve la instancia de Pyodide
 * @param {{leer:()=>string[], guardar:(l:string[])=>void}} o.almacen
 */
export async function ejecutarPip({ args, proyecto, cwd = "", out, err, cargarPy, almacen, revisar = revisarPip }) {
  const [sub, ...resto] = args;
  if (!sub || sub === "help" || sub === "--help") { out("Uso: pip install <paquete>[==versión] | install -r requirements.txt | uninstall <paquete> | list | freeze\n"); return sub ? 0 : 1; }
  if (sub === "--version" || sub === "-V") { out("pip (micropip en Pyodide, CódigoCamp)\n"); return 0; }
  if (!["install", "uninstall", "list", "freeze"].includes(sub)) { err(`pip: orden desconocida «${sub}». Usa: install, uninstall, list o freeze.\n`); return 1; }

  if (sub === "list" || sub === "freeze") {
    const lista = almacen.leer();
    let pyo;
    try { err(color.gris("Cargando Python…\n")); pyo = await cargarPy(); } catch (e) { err(`${e.message}\n`); return 1; }
    const filas = JSON.parse(pyo.runPython("import importlib.metadata as _m, json\njson.dumps(sorted((d.metadata['Name'], d.version) for d in _m.distributions() if d.metadata['Name']))"));
    const propios = new Set(lista.map(nombreDe));
    const enVenv = Boolean(almacen.venv);
    const mostrar = sub === "freeze" ? filas.filter(([n]) => propios.has(nombreDe(n)))
      : enVenv ? [["pip", "24.0"], ...filas.filter(([n]) => propios.has(nombreDe(n)))] : filas;
    out(sub === "freeze" ? mostrar.map(([n, v]) => `${n}==${v}`).join("\n") + (mostrar.length ? "\n" : "")
      : `${"Package".padEnd(28)}Version\n${"-".repeat(28)} ${"-".repeat(10)}\n${mostrar.map(([n, v]) => n.padEnd(28) + v).join("\n")}\n`);
    return 0;
  }

  const especs = [];
  let archivoReq = null;
  for (let i = 0; i < resto.length; i += 1) {
    if (resto[i] === "-r" || resto[i] === "--requirement") { archivoReq = resto[i + 1] ?? ""; i += 1; }
    else if (!resto[i].startsWith("-")) especs.push(resto[i]);
  }
  const omitidos = [];
  if (archivoReq !== null) {
    const leidos = new Set();
    const leer = (nombre, desde) => {
      const ruta = FS.resolver(desde, nombre);
      if (ruta === null || !FS.tieneArchivo(proyecto, ruta)) { err(`ERROR: no se encontró el archivo de requisitos «${nombre}»\n`); return false; }
      if (leidos.has(ruta)) return true;
      leidos.add(ruta);
      for (const cruda of proyecto.files[ruta].split("\n")) {
        const l = cruda.replace(/#.*/, "").trim();
        if (!l) continue;
        const r = /^(?:-r|--requirement)\s*(\S+)/.exec(l);
        if (r) { leer(r[1], FS.carpetaDe(ruta)); continue; }
        if (l.startsWith("-") || /^(git\+|https?:|file:|\.)/.test(l)) { omitidos.push([l, "opción o ruta local (no aplica en el navegador)"]); continue; }
        especs.push(limpiarRequisito(l));
      }
      return true;
    };
    if (!leer(archivoReq, cwd)) return 1;
    out(`Leyendo ${archivoReq}: ${especs.length} paquete${especs.length === 1 ? "" : "s"}\n`);
  }
  if (sub === "install") {
    for (let i = especs.length - 1; i >= 0; i -= 1) {
      const n = nombreDe(especs[i]);
      if (SERVIDORES.has(n)) { omitidos.push([especs[i], "CódigoCamp ya hace de servidor: usa fastapi dev main.py o uvicorn main:app --reload"]); especs.splice(i, 1); }
      else if (DEL_SISTEMA.has(n)) { omitidos.push([especs[i], n === "pip" || n === "setuptools" || n === "wheel" ? "ya viene con Python" : "solo existe para Windows/macOS de escritorio"]); especs.splice(i, 1); }
    }
    for (const [e, motivo] of omitidos.reverse()) out(`${color.gris("○")} ${e} ${color.gris("— " + motivo)}\n`);
    if (!especs.length && omitidos.length) return 0;
  }
  // Conectores de bases de datos: ya vienen con CódigoCamp (los reales usan sockets, que el navegador no tiene).
  const MYSQL = new Set(["pymysql", "mysql-connector-python", "mysql-connector", "mysqlclient", "psycopg2", "psycopg2-binary", "psycopg", "psycopg-binary", "pymongo", "redis", "bson"]);
  const yaIncluidos = especs.filter((e) => MYSQL.has(nombreDe(e)));
  if (yaIncluidos.length) {
    out(`${color.verde("✔")} ${yaIncluidos.join(", ")}: ya incluido en CódigoCamp (conecta con tus bases: MySQL/XAMPP, PostgreSQL, MongoDB, Redis)\n`);
    for (let i = especs.length - 1; i >= 0; i -= 1) if (MYSQL.has(nombreDe(especs[i]))) especs.splice(i, 1);
    if (!especs.length) return 0;
  }
  if (!especs.length) { err(sub === "install" ? "ERROR: indica qué instalar: pip install <paquete>\n" : "ERROR: indica qué desinstalar: pip uninstall <paquete>\n"); return 1; }
  const malos = especs.filter((e) => !ESPEC_PIP.test(e));
  if (malos.length) { err(`ERROR: «${malos[0]}» no es un nombre de paquete válido (se admiten nombres de PyPI con versión opcional: nombre==1.2.3). Las URL y rutas no están permitidas.\n`); return 1; }

  let pyo;
  try {
    err(color.gris("Cargando Python (solo la primera vez, puede tardar unos segundos)…\n"));
    pyo = await cargarPy();
    await pyo.loadPackage("micropip");
  } catch (e) { err(`${e.message}\n`); return 1; }
  const micropip = pyo.pyimport("micropip");
  let guardados = almacen.leer();
  let codigo = 0;
  const fallidos = [];
  const version = (n) => { try { return pyo.runPython(`import importlib.metadata as _m\ntry:\n    _v = _m.version(${JSON.stringify(n)})\nexcept Exception:\n    _v = ""\n_v`); } catch { return ""; } };
  for (const espec of especs) {
    const n = nombreDe(espec);
    try {
      if (sub === "install") {
        const rev = await revisar(n);
        if (!rev.ok) {
          err(`ERROR: ${espec} no se puede instalar en Trabajo: ${rev.motivo}.\n${rev.alternativa ? `  Alternativa: ${rev.alternativa}\n` : ""}`);
          if (rev.existe !== false) err(color.gris("  Trabajo ejecuta Python dentro del navegador. En tu PC (VS Code) sí se instala con pip normal.\n"));
          fallidos.push(espec); codigo = 1; continue;
        }
        out(`Instalando ${espec}…\n`);
        const { instalado, aviso } = await instalarTolerante(micropip, espec);
        if (aviso) out(`${color.amarillo("⚠")} ${aviso}\n`);
        instaladosEnSesion.add(n);
        guardados = [...guardados.filter((g) => nombreDe(g) !== n), instalado];
        out(`${color.verde("✔")} ${instalado}${instalado === espec && version(n) && !espec.includes("==") ? " " + version(n) : ""} instalado\n`);
      } else {
        await micropip.uninstall(n);
        instaladosEnSesion.delete(n);
        guardados = guardados.filter((g) => nombreDe(g) !== n);
        out(`Desinstalado ${n}\n`);
      }
    } catch (error) {
      err(`ERROR: ${espec}: ${explicarErrorPip(error.message)}\n`);
      fallidos.push(espec);
      codigo = 1;
    }
  }
  almacen.guardar(guardados);
  if (sub === "install" && especs.length > 1) {
    const bien = especs.length - fallidos.length;
    out(`\n${color.negrita("Resumen:")} ${color.verde(`${bien} instalado${bien === 1 ? "" : "s"}`)}${omitidos.length ? ` · ${color.gris(`${omitidos.length} omitido${omitidos.length === 1 ? "" : "s"} (no hacen falta aquí)`)}` : ""}${fallidos.length ? ` · ${color.rojo(`${fallidos.length} con error: ${fallidos.join(", ")}`)}` : ""}\n`);
    if (fallidos.length) out(color.gris("Los que fallan suelen tener código en C sin versión para el navegador. Si tu código no los importa, puedes ignorarlos; si los usa, busca una alternativa en Extensiones (Ctrl+Shift+X).\n"));
  }
  if (sub === "install" && codigo === 0) out(color.gris(almacen.venv
    ? `Instalado en el entorno virtual «${almacen.venv.split("/").pop()}» (queda en ${almacen.venv}/lib/python3.12/site-packages/cc-requisitos.txt). pip freeze > requirements.txt lo guarda para compartir.\n`
    : "Los paquetes quedan disponibles al ejecutar python y se reinstalan solos en tu próxima sesión.\n"));
  return codigo;
}

// ================================================================================= npm ====
const NOMBRE_NPM = /^(?:@[a-z0-9][a-z0-9._-]*\/)?[a-z0-9][a-z0-9._-]*$/;
const SEMVER = /^[~^]?\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?$|^latest$|^next$|^[\d.xX*~^<>=| -]+$/;

export function leerPackageJson(py, ruta = "package.json") {
  if (!FS.tieneArchivo(py, ruta)) return null;
  try { const j = JSON.parse(py.files[ruta]); return j && typeof j === "object" && !Array.isArray(j) ? j : null; } catch { return undefined; }
}
const guardarPackageJson = (py, datos, ruta = "package.json") => { const t = JSON.stringify(datos, null, 2) + "\n"; return FS.tieneArchivo(py, ruta) ? FS.escribirArchivo(py, ruta, t) : FS.crearArchivo(py, ruta, t, { padres: FS.carpetaDe(ruta) !== "" }); };

/** Carpeta del package.json más cercano subiendo desde `dir` (como npm), o null si no hay ninguno. */
export function carpetaDelPaquete(py, dir = "") {
  for (let d = dir; ; d = FS.carpetaDe(d)) {
    if (FS.tieneArchivo(py, FS.unir(d, "package.json"))) return d;
    if (d === "") return null;
  }
}

/** Dependencias declaradas -> { nombre: "^1.2.3" } del package.json más cercano a `dir`. */
export function dependenciasDe(py, dir = "") {
  const d = carpetaDelPaquete(py, dir);
  const j = d === null ? null : leerPackageJson(py, FS.unir(d, "package.json"));
  return j ? { ...(j.dependencies || {}), ...(j.devDependencies || {}) } : {};
}

/** URL del CDN para un import «paquete» o «paquete/subruta» según las dependencias. null si no está declarado. */
export function urlDeCdn(deps, especificador) {
  const m = /^((?:@[^/]+\/)?[^/]+)(\/.*)?$/.exec(especificador);
  if (!m || !(m[1] in deps)) return null;
  const version = String(deps[m[1]]).replace(/^[\^~]/, "");
  return `https://esm.sh/${m[1]}@${/^\d/.test(version) ? version : "latest"}${m[2] || ""}`;
}

async function resolverVersion(fetchFn, nombre, rango) {
  const r = await fetchFn(`https://data.jsdelivr.com/v1/package/resolve/npm/${nombre}@${encodeURIComponent(rango || "latest")}`);
  if (r.status === 404) throw Object.assign(new Error(`404 No se encontró «${nombre}${rango ? "@" + rango : ""}» en el registro de npm`), { noEncontrado: true });
  if (!r.ok) throw new Error(`El registro respondió con un error (${r.status}).`);
  const d = await r.json();
  if (!d.version) throw Object.assign(new Error(`404 No se encontró «${nombre}${rango ? "@" + rango : ""}» en el registro de npm`), { noEncontrado: true });
  return d.version;
}

/**
 * @param {object} o  { args, proyecto, cwd, out, err, fetchFn, ejecutar(linea) -> Promise<number>, usuario }
 */
export async function ejecutarNpm({ args, proyecto: py, out, err, cambio = () => {}, fetchFn = (...a) => fetch(...a), ejecutar, nombreProyecto = "mi-proyecto", cwd = "", leerLinea = async () => null }) {
  const [sub, ...resto] = args;
  const alias = { i: "install", add: "install", rm: "uninstall", remove: "uninstall", un: "uninstall", ls: "list", ll: "list", t: "test", tst: "test", "run-script": "run" };
  const orden = alias[sub] ?? sub;
  // npm busca el package.json subiendo desde la carpeta actual; si no hay, trabaja en la carpeta actual.
  if (orden === "create" || (orden === "init" && resto[0] && !resto[0].startsWith("-"))) return crearProyecto({ py, cwd, args: resto, out, err, cambio, fetchFn, leerLinea });
  const dirPkg = carpetaDelPaquete(py, cwd) ?? cwd;
  const rutaPkg = FS.unir(dirPkg, "package.json");
  const ubicacion = `/workspace${dirPkg ? "/" + dirPkg : ""}`;
  const pkg = leerPackageJson(py, rutaPkg);
  if (pkg === undefined && !["init", "--version", "-v", "help", undefined].includes(orden)) { err("npm ERR! package.json no es un JSON válido. Corrígelo o bórralo y ejecuta npm init -y.\n"); return 1; }

  if (orden === undefined || orden === "help" || orden === "--help") { out("Uso: npm init -y | install [paquete[@versión]] | uninstall <paquete> | run <script> | start | test | ls\n"); return 0; }
  if (orden === "--version" || orden === "-v") { out("10.x (npm simulado sobre package.json — CódigoCamp)\n"); return 0; }

  if (orden === "init") {
    if (pkg) { err("npm ERR! ya existe un package.json en esta carpeta.\n"); return 1; }
    const r = guardarPackageJson(py, { name: FS.nombreBase(dirPkg) || nombreProyecto, version: "1.0.0", description: "", main: "index.js", scripts: { test: 'echo "Error: no hay pruebas definidas"' }, license: "ISC" }, rutaPkg);
    if (!r.ok) { err(`npm ERR! ${r.error}\n`); return 1; }
    cambio();
    out(`Wrote to ${ubicacion}/package.json\n`);
    return 0;
  }

  if (orden === "install") {
    const peticiones = resto.filter((x) => !x.startsWith("-"));
    const guardarDev = resto.includes("-D") || resto.includes("--save-dev");
    const base = pkg ?? { name: nombreProyecto, version: "1.0.0", main: "index.js", license: "ISC" };
    if (!peticiones.length) {
      const n = Object.keys(dependenciasDe(py, dirPkg)).length;
      out(n ? `${n} dependencias declaradas. Se cargan desde el CDN cuando haces import (no hace falta node_modules).\n` : "No hay dependencias que instalar. Usa: npm install <paquete>\n");
      return 0;
    }
    const campo = guardarDev ? "devDependencies" : "dependencies";
    const dest = { ...(base[campo] || {}) };
    const agregados = [];
    let codigo = 0;
    for (const p of peticiones) {
      const m = /^(@[^/@]+\/[^/@]+|[^/@]+)(?:@(.+))?$/.exec(p);
      if (!m || !NOMBRE_NPM.test(m[1]) || (m[2] && !SEMVER.test(m[2]))) { err(`npm ERR! «${p}» no es un nombre de paquete válido (ej.: lodash, dayjs@1.11.10, @scope/pkg).\n`); codigo = 1; continue; }
      try {
        const version = await resolverVersion(fetchFn, m[1], m[2]);
        dest[m[1]] = `^${version}`;
        agregados.push(`${m[1]}@${version}`);
      } catch (error) {
        err(`npm ERR! ${error.noEncontrado ? error.message : /fetch|network/i.test(error.message) ? "No se pudo conectar con el registro de npm. Revisa tu conexión." : error.message}\n`);
        codigo = 1;
      }
    }
    if (agregados.length) {
      const r = guardarPackageJson(py, { ...base, [campo]: Object.fromEntries(Object.entries(dest).sort()) }, rutaPkg);
      if (!r.ok) { err(`npm ERR! ${r.error}\n`); return 1; }
      out(agregados.map((a) => `+ ${a}`).join("\n") + `\nañadido a package.json (${agregados.length} ${agregados.length === 1 ? "paquete" : "paquetes"})\n`);
      out(color.gris('Úsalo con import: import x from "paquete". Funciona con node y en la vista previa (también React, Vue, Bootstrap…): se carga desde esm.sh con la versión de tu package.json, sin node_modules.\n'));
      cambio();
    }
    return codigo;
  }

  if (orden === "uninstall") {
    if (!pkg) { err("npm ERR! no hay package.json.\n"); return 1; }
    const nombres = resto.filter((x) => !x.startsWith("-"));
    if (!nombres.length) { err("npm ERR! indica qué desinstalar: npm uninstall <paquete>\n"); return 1; }
    let quitados = 0;
    for (const n of nombres) for (const campo of ["dependencies", "devDependencies"]) if (pkg[campo] && n in pkg[campo]) { delete pkg[campo][n]; quitados += 1; }
    if (!quitados) { out("up to date: no estaba en package.json\n"); return 0; }
    guardarPackageJson(py, pkg, rutaPkg);
    out(`removed ${quitados} ${quitados === 1 ? "paquete" : "paquetes"}\n`);
    cambio();
    return 0;
  }

  if (orden === "list") {
    const deps = dependenciasDe(py, dirPkg);
    out(`${pkg?.name ?? nombreProyecto}@${pkg?.version ?? "1.0.0"} ${ubicacion}\n${Object.entries(deps).map(([n, v], i, a) => `${i === a.length - 1 ? "└──" : "├──"} ${n}@${String(v).replace(/^[\^~]/, "")}`).join("\n")}${Object.keys(deps).length ? "\n" : "(vacío)\n"}`);
    return 0;
  }

  if (orden === "run" || orden === "run-script" || orden === "start" || orden === "test") {
    const nombre = orden === "run" || orden === "run-script" ? resto[0] : orden;
    if (!pkg) { err("npm ERR! no hay package.json. Crea uno con: npm init -y\n"); return 1; }
    let linea = pkg.scripts?.[nombre];
    if (!linea && nombre === "start" && FS.tieneArchivo(py, FS.unir(dirPkg, "server.js"))) linea = "node server.js";
    if (!nombre) { out(`Scripts disponibles:\n${Object.entries(pkg.scripts || {}).map(([k, v]) => `  ${k}\n    ${v}`).join("\n") || "  (ninguno)"}\n`); return 0; }
    if (!linea) { err(`npm ERR! no existe el script «${nombre}» en package.json.${pkg.scripts ? ` Disponibles: ${Object.keys(pkg.scripts).join(", ") || "ninguno"}` : ""}\n`); return 1; }
    out(color.gris(`\n> ${pkg.name ?? nombreProyecto}@${pkg.version ?? "1.0.0"} ${nombre}\n> ${linea}\n\n`));
    return ejecutar(linea);
  }

  err(`npm ERR! «${sub}» no está disponible en esta terminal. Prueba: init, create vite, install, uninstall, run, start, test, ls.\n`);
  return 1;
}

// ======================================================================= npm create vite ====
/**
 * npm create vite@latest [nombre] -- --template react    (también: npm init vite, npx create-vite, npx create-react-app)
 * Crea la carpeta con los archivos de la plantilla y su package.json con las versiones actuales.
 */
export async function crearProyecto({ py, cwd = "", args, out, err, cambio = () => {}, fetchFn = (...a) => fetch(...a), leerLinea = async () => null, herramienta = null }) {
  const lista = args.filter((x) => x !== "--");
  const inicial = herramienta ?? (lista.shift() || "");
  const que = inicial.replace(/@.*$/, "").replace(/^create-/, "");
  if (!["vite", "react-app"].includes(que)) {
    err(`npm ERR! aquí solo está «npm create vite» (plantillas: ${PLANTILLAS.join(", ")}).\n`);
    return 1;
  }
  let plantilla = null;
  const posicionales = [];
  for (let i = 0; i < lista.length; i += 1) {
    if (lista[i] === "--template" || lista[i] === "-t") { plantilla = lista[i + 1] ?? null; i += 1; }
    else if (lista[i].startsWith("--template=")) plantilla = lista[i].slice(11);
    else if (!lista[i].startsWith("-")) posicionales.push(lista[i]);
  }
  if (que === "react-app") {
    out(color.amarillo("create-react-app ya no se mantiene (React recomienda Vite). Se crea el mismo proyecto con Vite + React.\n"));
    plantilla ??= lista.includes("--template") ? plantilla : "react";
    if (plantilla === "typescript") plantilla = "react-ts";
  }
  let nombre = posicionales[0];
  if (!nombre) {
    nombre = ((await leerLinea("Nombre del proyecto: ", {})) || "").trim() || "mi-app";
  }
  if (!plantilla) {
    out(`Plantillas: ${PLANTILLAS.join(", ")}\n`);
    plantilla = ((await leerLinea("Plantilla (react): ", {})) || "").trim() || "react";
  }
  if (!PLANTILLAS.includes(plantilla)) { err(`npm ERR! plantilla «${plantilla}» no disponible. Usa: ${PLANTILLAS.join(", ")}\n`); return 1; }
  const dir = nombre === "." ? cwd : FS.resolver(cwd, nombre);
  if (dir === null || (nombre !== "." && !FS.nombreValido(FS.nombreBase(dir)))) { err("npm ERR! nombre de proyecto no válido (letras sin tilde, números, guion y guion bajo).\n"); return 1; }
  if (FS.tieneArchivo(py, dir) || FS.archivosEn(py, dir).length && dir !== "" || (dir === "" && Object.keys(py.files).length)) {
    err(`npm ERR! la carpeta «${nombre}» no está vacía. Elige otro nombre.\n`);
    return 1;
  }
  out(`\nCreando el proyecto en /workspace${dir ? "/" + dir : ""} (plantilla ${plantilla})…\n`);
  const [deps, dev] = PAQUETES[plantilla];
  const versiones = {};
  let sinRed = false;
  await Promise.all([...deps, ...dev].map(async (n) => {
    try { versiones[n] = await resolverVersion(fetchFn, n, "latest"); } catch { versiones[n] = VERSIONES_RESPALDO[n]; sinRed = true; }
  }));
  const nombrePkg = (dir ? FS.nombreBase(dir) : "mi-app").toLowerCase();
  const pkg = {
    name: nombrePkg, private: true, version: "0.0.0", type: "module",
    scripts: { dev: "vite", build: "vite build", preview: "vite preview" },
    ...(deps.length ? { dependencies: Object.fromEntries(deps.map((n) => [n, `^${versiones[n]}`])) } : {}),
    devDependencies: Object.fromEntries(dev.map((n) => [n, `^${versiones[n]}`])),
  };
  const archivos = { ...archivosDePlantilla(plantilla, nombrePkg), "package.json": JSON.stringify(pkg, null, 2) + "\n" };
  for (const [ruta, texto] of Object.entries(archivos)) {
    const r = FS.crearArchivo(py, FS.unir(dir, ruta), texto, { padres: true });
    if (!r.ok) { err(`npm ERR! ${ruta}: ${r.error}\n`); return 1; }
  }
  cambio();
  if (sinRed) out(color.gris("No se pudo consultar el registro de npm: se usaron versiones conocidas.\n"));
  out(`\n${color.verde("Listo.")} Ahora ejecuta:\n\n${dir && dir !== cwd ? `  cd ${nombre}\n` : ""}  npm run dev\n\n`);
  out(color.gris("npm run dev abre la vista previa. No hace falta npm install: React y las demás librerías se cargan desde esm.sh con las versiones de package.json.\n"));
  return 0;
}

// ============================================================ sugerencias ante errores ====
// Nombre del import → nombre del paquete en pip (cuando no coinciden).
const IMPORT_A_PIP = {
  cv2: "opencv-python", PIL: "Pillow", sklearn: "scikit-learn", yaml: "PyYAML", bs4: "beautifulsoup4", dotenv: "python-dotenv",
  jose: "python-jose", jwt: "PyJWT", multipart: "python-multipart", dateutil: "python-dateutil", docx: "python-docx", pptx: "python-pptx",
  Crypto: "pycryptodome", serial: "pyserial", usb: "pyusb", magic: "python-magic", OpenSSL: "pyOpenSSL", attr: "attrs", git: "GitPython",
  telegram: "python-telegram-bot", discord: "discord.py", google: "google-api-python-client", sqlmodel: "sqlmodel", passlib: "passlib[bcrypt]",
  email_validator: "email-validator", jinja2: "Jinja2", markdown: "Markdown", fitz: "PyMuPDF", skimage: "scikit-image", MySQLdb: "mysqlclient",
};

/** Si `mensaje` es un ModuleNotFoundError, devuelve el texto de ayuda (qué instalar y dónde); si no, null. */
export function sugerenciaPython(mensaje, { py = null, cwd = "", venv = null } = {}) {
  const m = /ModuleNotFoundError: No module named '([\w.]+)'/.exec(String(mensaje));
  if (!m) return null;
  const raiz = m[1].split(".")[0];
  if (["ssl", "_ssl", "hashlib", "_hashlib", "lzma", "_lzma", "sqlite3", "_sqlite3"].includes(raiz)) {
    return `💡 «${raiz.replace(/^_/, "")}» es parte de Python, pero en el navegador se descarga aparte. Trabajo lo carga solo: vuelve a ejecutar (Ctrl+C y otra vez el comando). Si sigue, revisa tu conexión a internet.`;
  }
  if (py && Object.keys(py.files).some((r) => r === `${raiz}.py` || r.endsWith(`/${raiz}.py`) || r.startsWith(`${raiz}/`) || r.includes(`/${raiz}/`))) {
    return `💡 «${raiz}» es un archivo o carpeta de tu proyecto: ejecuta el programa desde la carpeta correcta (cd …) o agrega un __init__.py a la carpeta.`;
  }
  const pip = IMPORT_A_PIP[raiz] ?? raiz.replace(/_/g, "-");
  const req = py && ["requirements.txt", FS.unir(cwd, "requirements.txt")].find((r) => FS.tieneArchivo(py, r) && new RegExp(`^\\s*${pip.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\\\[.*$/, "")}\\b`, "im").test(py.files[r]));
  const donde = venv ? ` en el entorno «${venv}»` : "";
  return `💡 Falta instalar el paquete «${pip}»${donde}. Escribe:  pip install ${pip}` +
    (req ? `\n   Está en ${req}: instala todo con  pip install -r ${req}` : "") +
    "\n   También puedes buscarlo en Extensiones (Ctrl+Shift+X).";
}

/** Igual para Node: «Cannot find module 'x'» o un import de un paquete que no está en package.json. */
export function sugerenciaNode(mensaje) {
  const m = /Cannot find (?:module|package) '([^']+)'|Failed to resolve module specifier "([^"]+)"/.exec(String(mensaje));
  if (!m) return null;
  const nombre = (m[1] || m[2]).startsWith("@") ? (m[1] || m[2]).split("/").slice(0, 2).join("/") : (m[1] || m[2]).split("/")[0];
  if (nombre.startsWith(".") || nombre.startsWith("node:")) return null;
  return `💡 Falta el paquete «${nombre}». Escribe:  npm install ${nombre}   (o búscalo en Extensiones, Ctrl+Shift+X)`;
}
