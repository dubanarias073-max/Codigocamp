// Entornos virtuales de Python (venv), como en VS Code:
//   python -m venv .venv · virtualenv env · source .venv/bin/activate · .venv\Scripts\activate · deactivate
// El entorno es una carpeta real del proyecto (pyvenv.cfg, bin/, Scripts/, lib/…/site-packages). Sus paquetes se
// guardan en site-packages/cc-requisitos.txt: así viajan con el proyecto y pip install / list / freeze trabajan
// sobre el entorno activo, no sobre el Python global.
import * as FS from "./fs.js";

export const VERSION_PY = "3.12";
const SITE = `lib/python${VERSION_PY}/site-packages`;
const REQ = `${SITE}/cc-requisitos.txt`;
const NOMBRE_VALIDO = /^[A-Za-z0-9._-]{1,60}$/;

const unir = (...p) => p.filter(Boolean).join("/");

/** ¿Es `dir` un entorno virtual? (tiene pyvenv.cfg) */
export function esVenv(py, dir) {
  return dir !== null && FS.tieneArchivo(py, unir(dir, "pyvenv.cfg"));
}

/** Entornos virtuales del proyecto (carpetas con pyvenv.cfg). */
export function listarVenvs(py) {
  return Object.keys(py.files).filter((r) => r === "pyvenv.cfg" || r.endsWith("/pyvenv.cfg")).map((r) => FS.carpetaDe(r));
}

function escribirCon(py, ruta, texto) {
  if (FS.carpetaDe(ruta)) {
    const c = FS.crearCarpeta(py, FS.carpetaDe(ruta), { padres: true });
    if (!c.ok) return c;
  }
  return FS.escribirArchivo(py, ruta, texto);
}

function escribir(py, ruta, texto) {
  const r = escribirCon(py, ruta, texto);
  if (!r.ok) throw new Error(`${ruta}: ${r.error}`);
}

/** Crea el entorno en la carpeta `destino` (relativa a cwd). Devuelve la ruta del proyecto o lanza un Error. */
export function crearVenv(py, cwd, destino, { usuario = "estudiante", conPaquetesSistema = false, limpiar = false } = {}) {
  if (!destino) throw new Error("uso: python -m venv <carpeta>   (por ejemplo: python -m venv .venv)");
  const dir = FS.resolver(cwd, destino.replace(/\\/g, "/").replace(/\/+$/, ""));
  if (dir === null || dir === "") throw new Error(`«${destino}» no es una carpeta válida dentro del proyecto`);
  if (!NOMBRE_VALIDO.test(FS.nombreBase(dir))) throw new Error(`«${FS.nombreBase(dir)}»: usa letras, números, punto, guion o guion bajo`);
  if (FS.tieneArchivo(py, dir)) throw new Error(`«${destino}» ya existe y es un archivo`);
  const yaEra = esVenv(py, dir);
  if (!yaEra && Object.keys(py.files).some((r) => r.startsWith(dir + "/")) && !limpiar) {
    throw new Error(`la carpeta «${destino}» ya tiene archivos y no es un entorno virtual (usa otra carpeta o --clear)`);
  }
  if (limpiar) for (const r of Object.keys(py.files)) if (r.startsWith(dir + "/")) delete py.files[r];
  const abs = FS.rutaAbsoluta(dir);
  const nombre = FS.nombreBase(dir);
  escribir(py, unir(dir, "pyvenv.cfg"), [
    "home = /usr/local/bin",
    `include-system-site-packages = ${conPaquetesSistema ? "true" : "false"}`,
    `version = ${VERSION_PY}.7`,
    `executable = /usr/local/bin/python${VERSION_PY}`,
    `command = /usr/local/bin/python3 -m venv ${abs}`,
    "",
  ].join("\n"));
  // Como Python 3.13: el entorno se ignora solo en Git.
  escribir(py, unir(dir, ".gitignore"), "# Creado por venv; ver https://docs.python.org/3/library/venv.html\n*\n");
  escribir(py, unir(dir, "bin/activate"), `# Este archivo se usa con «source bin/activate» desde bash/zsh. No se ejecuta directamente.
deactivate () {
    PS1="\${_OLD_VIRTUAL_PS1:-}"; export PS1
    unset VIRTUAL_ENV VIRTUAL_ENV_PROMPT
}
VIRTUAL_ENV="${abs}"
export VIRTUAL_ENV
_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
VIRTUAL_ENV_PROMPT="(${nombre}) "
export VIRTUAL_ENV_PROMPT
`);
  escribir(py, unir(dir, "bin/python"), `#!/usr/bin/env python${VERSION_PY}\n# Python ${VERSION_PY} del entorno virtual «${nombre}» (CódigoCamp usa Pyodide en el navegador).\n`);
  escribir(py, unir(dir, "bin/pip"), `#!${abs}/bin/python\n# pip del entorno virtual «${nombre}».\n`);
  escribir(py, unir(dir, "Scripts/activate.bat"), `@echo off\r\nrem Activa el entorno en CMD:  ${nombre}\\Scripts\\activate\r\nset "VIRTUAL_ENV=${abs}"\r\nset "PROMPT=(${nombre}) %PROMPT%"\r\nset "PATH=%VIRTUAL_ENV%\\Scripts;%PATH%"\r\n`);
  escribir(py, unir(dir, "Scripts/Activate.ps1"), `# Activa el entorno en PowerShell:  .\\${nombre}\\Scripts\\Activate.ps1\n$env:VIRTUAL_ENV = "${abs}"\n$env:PATH = "$env:VIRTUAL_ENV\\Scripts;$env:PATH"\nfunction global:prompt { "(${nombre}) PS $($executionContext.SessionState.Path.CurrentLocation)> " }\n`);
  escribir(py, unir(dir, "Scripts/deactivate.bat"), "@echo off\r\nset VIRTUAL_ENV=\r\n");
  if (!FS.tieneArchivo(py, unir(dir, REQ))) escribir(py, unir(dir, REQ), "");
  return { dir, nombre, abs, yaEra };
}

/** Si `orden` es un script de activación (source .venv/bin/activate, .venv\Scripts\activate, Activate.ps1…), devuelve la carpeta del entorno. */
export function rutaActivacion(orden, py, cwd) {
  if (!orden) return null;
  // La terminal quita las «\» de Windows: .venv\Scripts\activate llega como .venvScriptsactivate.
  let t = orden.replace(/\\/g, "/").replace(/^\.\//, "");
  let m = /^(.*?)\/?(?:bin|Scripts)\/(?:activate|Activate\.ps1|activate\.bat|activate\.fish|activate\.csh)$/i.exec(t);
  if (!m) {
    const sinBarras = /^(.*?)Scripts(?:activate|Activate\.ps1|activate\.bat)$/i.exec(t);
    if (!sinBarras) return null;
    // «.\venv\Scripts\activate» → «.venvScriptsactivate»: prueba con y sin el punto inicial.
    const candidatos = [sinBarras[1], sinBarras[1].replace(/^\./, "")];
    for (const c of candidatos) { const d = FS.resolver(cwd, c); if (d && esVenv(py, d)) return d; }
    return null;
  }
  const d = FS.resolver(cwd, m[1] || ".");
  return d !== null && esVenv(py, d) ? d : null;
}

/** Almacén de paquetes del entorno (mismo formato que el global: lista de «nombre==versión»). */
export function almacenDeVenv(py, dir, cambio = () => {}) {
  const ruta = unir(dir, REQ);
  return {
    leer: () => String(py.files[ruta] ?? "").split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#")),
    guardar: (lista) => {
      const r = escribirCon(py, ruta, lista.join("\n") + (lista.length ? "\n" : ""));
      if (r.ok) cambio();
    },
    venv: dir,
  };
}

/** Activa el entorno en la sesión de la terminal (prompt «(.venv)», VIRTUAL_ENV, PATH). */
export function activar(sesion, dir) {
  if (sesion.venv && sesion.venv !== dir) desactivar(sesion);
  sesion.venv = dir;
  sesion.vars.VIRTUAL_ENV = FS.rutaAbsoluta(dir);
  sesion.vars.VIRTUAL_ENV_PROMPT = `(${FS.nombreBase(dir)}) `;
  if (sesion.vars._OLD_VIRTUAL_PATH === undefined) sesion.vars._OLD_VIRTUAL_PATH = sesion.vars.PATH ?? "/usr/local/bin:/usr/bin:/bin";
  sesion.vars.PATH = `${sesion.vars.VIRTUAL_ENV}/bin:${sesion.vars._OLD_VIRTUAL_PATH}`;
}

export function desactivar(sesion) {
  if (!sesion.venv) return false;
  sesion.venv = null;
  if (sesion.vars._OLD_VIRTUAL_PATH !== undefined) sesion.vars.PATH = sesion.vars._OLD_VIRTUAL_PATH;
  for (const k of ["VIRTUAL_ENV", "VIRTUAL_ENV_PROMPT", "_OLD_VIRTUAL_PATH"]) delete sesion.vars[k];
  return true;
}
