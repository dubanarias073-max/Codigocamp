// Panel «Extensiones» (Ctrl+Shift+X), como el de VS Code pero para librerías y frameworks: busca en npm y PyPI,
// muestra lo instalado y lo recomendado, e instala/desinstala con un clic (ejecuta npm/pip en la terminal).
import * as FS from "./fs.js";
import { revisarPip } from "./disponibilidad.js";

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const NOMBRE_NPM = /^(@[a-z0-9][\w.-]*\/)?[a-z0-9][\w.-]*$/i;
const NOMBRE_PIP = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;

export const PLANTILLAS = [
  { id: "react", nombre: "React + Vite", desc: "Componentes con JSX, useState, Vite. Lo más usado para páginas web modernas.", cmd: "npm create vite@latest mi-app -- --template react" },
  { id: "react-ts", nombre: "React + TypeScript", desc: "React con tipos (TSX). Errores de tipos en el editor como en VS Code.", cmd: "npm create vite@latest mi-app -- --template react-ts" },
  { id: "preact", nombre: "Preact + Vite", desc: "Como React pero de 3 KB.", cmd: "npm create vite@latest mi-app -- --template preact" },
  { id: "vanilla", nombre: "JavaScript + Vite", desc: "HTML, CSS y JS con módulos, sin framework.", cmd: "npm create vite@latest mi-app -- --template vanilla" },
  { id: "vanilla-ts", nombre: "TypeScript + Vite", desc: "TypeScript puro con módulos.", cmd: "npm create vite@latest mi-app -- --template vanilla-ts" },
  { id: "vue", nombre: "Vue + Vite", desc: "Componentes .vue con plantillas fáciles de leer (ref, v-for, @click).", cmd: "npm create vite@latest mi-app -- --template vue" },
  { id: "svelte", nombre: "Svelte + Vite", desc: "Componentes .svelte que compilan a JavaScript pequeño y rápido.", cmd: "npm create vite@latest mi-app -- --template svelte" },
];

export const RECOMENDADOS = {
  npm: [
    ["react", "Interfaces con componentes"], ["react-dom", "React para el navegador"], ["preact", "React en 3 KB"], ["vue", "Framework progresivo"],
    ["bootstrap", "Estilos y componentes listos"], ["tailwindcss", "CSS con clases utilitarias"], ["axios", "Peticiones HTTP"], ["lodash", "Utilidades para datos"],
    ["dayjs", "Fechas fáciles"], ["chart.js", "Gráficas"], ["three", "3D con WebGL"], ["gsap", "Animaciones"], ["zod", "Validar datos"], ["uuid", "Identificadores únicos"],
    ["canvas-confetti", "Confeti"], ["marked", "Markdown a HTML"], ["sweetalert2", "Alertas bonitas"], ["leaflet", "Mapas"], ["animate.css", "Animaciones CSS"], ["@fortawesome/fontawesome-free", "Íconos"],
  ],
  pip: [
    ["fastapi", "APIs rápidas con Python (fastapi dev main.py)"], ["flask", "Páginas y APIs web (flask --app app run)"], ["sqlalchemy", "Bases de datos con ORM"],
    ["pydantic", "Validar datos"], ["requests", "Peticiones HTTP"], ["httpx", "Peticiones HTTP (también async)"], ["jinja2", "Plantillas HTML"], ["python-dotenv", "Leer archivos .env"],
    ["numpy", "Cálculo numérico"], ["pandas", "Tablas de datos"], ["matplotlib", "Gráficas"], ["scipy", "Ciencia"], ["scikit-learn", "Machine learning"],
    ["sympy", "Álgebra simbólica"], ["pillow", "Imágenes"], ["beautifulsoup4", "Leer HTML"], ["pyyaml", "YAML"], ["rich", "Terminal con colores"],
    ["networkx", "Grafos"], ["regex", "Expresiones regulares"], ["openpyxl", "Excel"], ["faker", "Datos falsos para pruebas"],
  ],
};
// Ya incluidos en CódigoCamp: se muestran como instalados.
export const INCLUIDOS_PIP = ["pymysql", "mysql-connector-python", "psycopg2", "psycopg", "pymongo", "redis", "sqlite3"];

// Módulos que ya trae Python (no se instalan con pip).
const STDLIB = new Set("abc argparse array ast asyncio base64 binascii bisect builtins calendar cmath collections colorsys concurrent configparser contextlib copy csv ctypes dataclasses datetime decimal difflib dis email enum errno fnmatch fractions functools gc getpass glob gzip hashlib heapq hmac html http importlib inspect io ipaddress itertools json keyword locale logging lzma math mimetypes multiprocessing numbers operator os pathlib pickle platform pprint queue random re sched secrets select shlex shutil signal socket sqlite3 ssl stat statistics string struct subprocess sys tempfile textwrap threading time timeit tkinter token tokenize traceback types typing unicodedata unittest urllib uuid warnings weakref xml zipfile zlib zoneinfo __future__ getopt webbrowser wsgiref turtle".split(" "));
export const IMPORT_A_PIP = {
  cv2: "opencv-python", PIL: "pillow", sklearn: "scikit-learn", yaml: "pyyaml", bs4: "beautifulsoup4", dotenv: "python-dotenv", jose: "python-jose",
  jwt: "pyjwt", multipart: "python-multipart", dateutil: "python-dateutil", docx: "python-docx", decouple: "python-decouple",
  flask_sqlalchemy: "flask-sqlalchemy", flask_cors: "flask-cors", flask_login: "flask-login", flask_wtf: "flask-wtf", flask_bcrypt: "flask-bcrypt",
  flask_migrate: "flask-migrate", flask_jwt_extended: "flask-jwt-extended", flask_mail: "flask-mail", flask_restful: "flask-restful",
  flask_marshmallow: "flask-marshmallow", flask_session: "flask-session", flask_limiter: "flask-limiter", flask_socketio: "flask-socketio",
  pydantic_settings: "pydantic-settings", email_validator: "email-validator", passlib: "passlib", rest_framework: "djangorestframework",
  corsheaders: "django-cors-headers", crispy_forms: "django-crispy-forms", mongoengine: "mongoengine", sqlmodel: "sqlmodel",
};
// Conectores que CódigoCamp ya trae (van a tu servidor por el puente o, si no se puede, a SQLite / mongomock).
export const EMULADOS_PY = ["pymysql", "mysql", "MySQLdb", "psycopg2", "psycopg", "pymongo", "bson", "redis", "flask_mysqldb", "uvicorn", "micropip", "pyodide", "js"];
const nombrePip = (e) => e.replace(/\[.*$/, "").split(/[=<>~!;\s]/)[0].toLowerCase().replace(/[-_.]+/g, "-");

/**
 * Paquetes de Python que tu proyecto necesita y no están instalados: los de requirements.txt y los que importa tu código.
 * Devuelve [{ nombre, motivo }] (como la recomendación de extensiones de VS Code al abrir un proyecto).
 */
export function faltantesPython(py, instalados = []) {
  const ya = new Set([...instalados.map(nombrePip), ...INCLUIDOS_PIP]);
  const salida = new Map();
  for (const [ruta, texto] of Object.entries(py.files)) {
    if (/(^|\/)requirements[^/]*\.txt$/.test(ruta) && !ruta.includes("site-packages")) {
      for (const l of texto.split("\n")) {
        const limpio = l.replace(/#.*/, "").trim();
        if (!limpio || limpio.startsWith("-") || /^(git\+|https?:|\.)/.test(limpio)) continue;
        const n = nombrePip(limpio);
        if (n && !ya.has(n) && !["uvicorn", "gunicorn", "uvloop", "httptools", "watchfiles", "pip", "setuptools", "wheel", "pywin32"].includes(n)) salida.set(n, { nombre: n, motivo: `en ${ruta}` });
      }
    }
  }
  const propios = new Set(Object.keys(py.files).filter((r) => r.endsWith(".py")).map((r) => FS.nombreBase(r).replace(/\.py$/, "")));
  for (const c of py.folders) propios.add(FS.nombreBase(c));
  for (const [ruta, texto] of Object.entries(py.files)) {
    if (!ruta.endsWith(".py") || ruta.includes("site-packages") || texto.length > 300_000) continue;
    for (const m of texto.matchAll(/^\s*(?:from\s+([A-Za-z_][\w]*)[\w.]*\s+import|import\s+([A-Za-z_][\w]*))/gm)) {
      const mod = m[1] || m[2];
      if (STDLIB.has(mod) || propios.has(mod) || EMULADOS_PY.includes(mod)) continue;
      const n = nombrePip(IMPORT_A_PIP[mod] ?? mod);
      if (!ya.has(n) && !salida.has(n)) salida.set(n, { nombre: n, motivo: `lo importa ${ruta}` });
    }
  }
  return [...salida.values()];
}

/** Módulos de terceros que importa tu código (sin la biblioteca estándar, tus archivos ni los conectores incluidos). */
export function importsDelProyecto(py) {
  const propios = new Set(Object.keys(py.files).filter((r) => r.endsWith(".py")).map((r) => FS.nombreBase(r).replace(/\.py$/, "")));
  for (const c of py.folders) propios.add(FS.nombreBase(c));
  const mods = new Set();
  for (const [ruta, texto] of Object.entries(py.files)) {
    if (!ruta.endsWith(".py") || /(^|\/)(site-packages|\.?venv|env|node_modules)\//.test(ruta) || texto.length > 300_000) continue;
    for (const m of texto.matchAll(/^[ \t]*(?:from\s+([A-Za-z_]\w*)[\w.]*\s+import|import\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*))/gm)) {
      for (const mod of (m[1] ? [m[1]] : m[2].split(/\s*,\s*/).map((x) => x.split(".")[0]))) {
        if (!STDLIB.has(mod) && !propios.has(mod) && !EMULADOS_PY.includes(mod)) mods.add(mod);
      }
    }
  }
  return [...mods];
}

/**
 * Como importsDelProyecto, pero solo de los archivos que de verdad usa la app que enciendes: el archivo de
 * entrada y los módulos tuyos que importa (siguiendo sus imports). Así `flask --app app run` no pide instalar
 * FastAPI porque otro archivo del proyecto lo use. Si no se encuentra la entrada, revisa todo el proyecto.
 */
export function importsDesde(py, entrada) {
  if (!entrada || typeof py.files[entrada] !== "string") return importsDelProyecto(py);
  const esPy = (r) => typeof py.files[r] === "string" && r.endsWith(".py");
  const resolver = (base, partes) => {
    const r = [base, ...partes].filter(Boolean).join("/");
    return [`${r}.py`, `${r}/__init__.py`].find(esPy) ?? null;
  };
  const raizEntrada = FS.carpetaDe(entrada);
  const vistos = new Set(), pendientes = [entrada], externos = new Set();
  while (pendientes.length && vistos.size < 400) {
    const ruta = pendientes.pop();
    if (vistos.has(ruta)) continue;
    vistos.add(ruta);
    const texto = py.files[ruta];
    if (texto.length > 300_000) continue;
    const carpeta = FS.carpetaDe(ruta);
    for (const m of texto.matchAll(/^[ \t]*(?:from\s+(\.*)([A-Za-z_][\w.]*)?\s+import[ \t]+([\w \t,()*]+)|import[ \t]+([A-Za-z_][\w.]*(?:[ \t]+as[ \t]+\w+)?(?:[ \t]*,[ \t]*[A-Za-z_][\w.]*(?:[ \t]+as[ \t]+\w+)?)*))/gm)) {
      const candidatos = [];
      if (m[4]) for (const x of m[4].split(/\s*,\s*/)) candidatos.push({ puntos: "", mod: x.split(/\s+as\s+/)[0].trim(), nombres: [] });
      else candidatos.push({ puntos: m[1] || "", mod: m[2] || "", nombres: (m[3] || "").replace(/[()]/g, "").split(",").map((x) => x.trim().split(/\s+/)[0]).filter(Boolean) });
      for (const { puntos, mod, nombres } of candidatos) {
        const partes = mod ? mod.split(".") : [];
        let encontrado = null;
        if (puntos) {
          let base = carpeta;
          for (let i = 1; i < puntos.length; i += 1) base = FS.carpetaDe(base);
          encontrado = partes.length ? resolver(base, partes) : null;
          for (const n of nombres) { const r = resolver(base, [...partes, n]); if (r) pendientes.push(r); }
          if (encontrado) pendientes.push(encontrado);
          continue;   // un import relativo siempre es tuyo
        }
        for (const base of new Set([raizEntrada, "", carpeta])) {
          encontrado = resolver(base, partes);
          if (encontrado) {
            pendientes.push(encontrado);
            for (const n of nombres) { const r = resolver(base, [...partes, n]); if (r) pendientes.push(r); }
            break;
          }
        }
        const primero = partes[0];
        if (!encontrado && primero && !STDLIB.has(primero) && !EMULADOS_PY.includes(primero)
            && !py.folders.some((c) => FS.nombreBase(c) === primero)) externos.add(primero);
      }
    }
  }
  return [...externos];
}

/** De un módulo importado (flask_sqlalchemy) al nombre de pip (flask-sqlalchemy). */
export const pipDeImport = (mod) => nombrePip(IMPORT_A_PIP[mod] ?? mod);

/** Lee package.json (de la carpeta del proyecto activa) y devuelve { ruta, deps: { nombre: versión }, dev } */
export function paqueteNpm(py, carpeta = "") {
  const ruta = carpeta ? `${carpeta}/package.json` : "package.json";
  try {
    const j = JSON.parse(py.files[ruta] ?? "null");
    return j ? { ruta, deps: j.dependencies || {}, dev: j.devDependencies || {} } : { ruta: null, deps: {}, dev: {} };
  } catch { return { ruta, deps: {}, dev: {}, roto: true }; }
}

export async function buscarNpm(texto, fetchFn = fetch) {
  const r = await fetchFn(`https://registry.npmjs.org/-/v1/search?text=${encodeURIComponent(texto)}&size=20`);
  if (!r.ok) throw new Error(`npm respondió ${r.status}`);
  const j = await r.json();
  return (j.objects || []).map((o) => ({ nombre: o.package.name, version: o.package.version, desc: o.package.description || "", autor: o.package.publisher?.username || "", descargas: o.downloads?.weekly ?? null }));
}

export async function buscarPip(texto, fetchFn = fetch) {
  // PyPI no tiene buscador con CORS: se consulta el nombre exacto (y variantes comunes).
  const nombres = [...new Set([texto.trim(), texto.trim().toLowerCase().replace(/\s+/g, "-"), `py${texto.trim().toLowerCase()}`])].filter((n) => NOMBRE_PIP.test(n));
  const salida = [];
  for (const n of nombres) {
    try {
      const r = await fetchFn(`https://pypi.org/pypi/${encodeURIComponent(n)}/json`);
      if (!r.ok) continue;
      const j = await r.json();
      salida.push({ nombre: j.info.name, version: j.info.version, desc: j.info.summary || "", autor: j.info.author || "" });
    } catch { /* sin red */ }
  }
  return salida;
}

export class PanelExtensiones {
  /** @param {object} o { raiz, proyecto, cwd(): carpeta actual, pip(): lista instalada, correr(cmd), aviso, fetchFn } */
  constructor(o) {
    Object.assign(this, { fetchFn: (...a) => fetch(...a), ...o });
    this.tipo = "npm";
    this.resultados = null;
    this.revision = new Map();   // nombre pip -> { ok, motivo, alternativa } (se consulta una vez)
    this.raiz.addEventListener("click", (e) => this.#clic(e));
    this.raiz.addEventListener("input", (e) => { if (e.target.name === "buscar") { clearTimeout(this.t); this.t = setTimeout(() => this.#buscar(e.target.value), 350); } });
  }

  carpetaNpm() {
    // La carpeta con package.json más cercana a la terminal (como npm).
    const py = this.proyecto();
    let c = this.cwd?.() ?? "";
    for (;;) { if (FS.tieneArchivo(py, c ? `${c}/package.json` : "package.json")) return c; if (!c) return ""; c = FS.carpetaDe(c); }
  }

  async #buscar(texto) {
    texto = texto.trim();
    if (!texto) { this.resultados = null; return this.render(); }
    this.resultados = "cargando";
    this.render();
    try { this.resultados = this.tipo === "npm" ? await buscarNpm(texto, this.fetchFn) : await buscarPip(texto, this.fetchFn); }
    catch (e) { this.resultados = { error: e.message }; }
    this.render();
  }

  /** Estado de un paquete pip para el navegador; lo pide la primera vez y vuelve a pintar al saberlo. */
  #revision(nombre) {
    const n = nombre.toLowerCase();
    if (!this.revision.has(n)) {
      this.revision.set(n, null);
      revisarPip(n, this.fetchFn).then((r) => { this.revision.set(n, r); clearTimeout(this.tRev); this.tRev = setTimeout(() => this.render(), 120); });
    }
    return this.revision.get(n);
  }

  render() {
    const py = this.proyecto();
    const carpeta = this.carpetaNpm();
    const npm = paqueteNpm(py, carpeta);
    const pip = new Set([...(this.pip?.() ?? []).map((x) => x.split(/[=<>]/)[0].toLowerCase()), ...INCLUIDOS_PIP]);
    const instalado = (n) => (this.tipo === "npm" ? (npm.deps[n] ?? npm.dev[n]) : pip.has(n.toLowerCase()) ? "✓" : null);
    const valorBuscar = this.raiz.querySelector("[name=buscar]")?.value ?? "";
    const item = (x) => {
      const v = instalado(x.nombre);
      const rev = this.tipo === "pip" && !v ? this.#revision(x.nombre) : null;
      return `<div class="ext-item"><div class="ext-ico">${esc((x.nombre.replace(/^@[^/]+\//, "")[0] || "?").toUpperCase())}</div>
        <div class="ext-info"><div class="ext-nombre"><b>${esc(x.nombre)}</b>${x.version ? ` <small>${esc(x.version)}</small>` : ""}</div>
        <div class="ext-desc">${esc(x.desc)}</div>${x.autor || x.descargas ? `<div class="ext-meta">${esc(x.autor)}${x.descargas ? ` · ${Number(x.descargas).toLocaleString()} descargas/semana` : ""}</div>` : ""}
        ${rev && !rev.ok ? `<div class="ext-no">No funciona en el navegador: ${esc(rev.motivo)}.${rev.alternativa ? ` Usa: <b>${esc(rev.alternativa)}</b>` : ""}</div>` : ""}</div>
        <div class="ext-btns">${v ? `<span class="ext-ok" title="Instalado">${esc(v === "✓" ? "Instalado" : v)}</span>${INCLUIDOS_PIP.includes(x.nombre) ? "" : `<button type="button" class="btn sm" data-accion="quitar" data-nombre="${esc(x.nombre)}">Desinstalar</button>`}`
          : rev && !rev.ok ? `<button type="button" class="btn sm" disabled title="${esc(rev.motivo)}">No disponible</button>`
          : `<button type="button" class="btn pri sm" data-accion="instalar" data-nombre="${esc(x.nombre)}">Instalar</button>`}</div></div>`;
    };
    let cuerpo;
    if (this.resultados === "cargando") cuerpo = '<p class="git-nota">Buscando…</p>';
    else if (this.resultados?.error) cuerpo = `<p class="git-nota">No se pudo buscar: ${esc(this.resultados.error)}</p>`;
    else if (Array.isArray(this.resultados)) cuerpo = this.resultados.length ? this.resultados.map(item).join("") : `<p class="git-nota">Sin resultados${this.tipo === "pip" ? " (en PyPI escribe el nombre exacto del paquete)" : ""}.</p>`;
    else {
      const faltan = this.tipo === "pip" ? faltantesPython(py, this.pip?.() ?? []) : [];
      const reqs = Object.keys(py.files).filter((r) => /(^|\/)requirements\.txt$/.test(r) && !r.includes("site-packages"));
      const bloqueFaltan = faltan.length ? `<div class="git-titulo ext-faltan">Tu proyecto los necesita <span>${faltan.length}</span></div>
        ${reqs.length ? `<div class="ext-item"><div class="ext-ico">R</div><div class="ext-info"><div class="ext-nombre"><b>Instalar todo</b></div><div class="ext-desc">pip install -r ${esc(reqs[0])}</div></div><div class="ext-btns"><button type="button" class="btn pri sm" data-accion="requisitos" data-ruta="${esc(reqs[0])}">Instalar</button></div></div>` : ""}
        ${!reqs.length && faltan.length > 1 ? `<div class="ext-item"><div class="ext-ico">+</div><div class="ext-info"><div class="ext-nombre"><b>Instalar todos</b></div><div class="ext-desc">pip install ${esc(faltan.map((f) => f.nombre).join(" "))}</div></div><div class="ext-btns"><button type="button" class="btn pri sm" data-accion="todos" data-nombres="${esc(faltan.map((f) => f.nombre).join(" "))}">Instalar</button></div></div>` : ""}
        ${faltan.map((f) => item({ nombre: f.nombre, desc: f.motivo })).join("")}` : "";
      const inst = this.tipo === "npm" ? Object.entries({ ...npm.deps, ...npm.dev }).map(([n, v]) => ({ nombre: n, version: v, desc: npm.dev[n] ? "devDependency" : "" }))
        : [...pip].filter((n) => !INCLUIDOS_PIP.includes(n)).map((n) => ({ nombre: n, desc: "" }));
      cuerpo = `${bloqueFaltan}${this.tipo === "npm" ? `<div class="git-titulo">Crear proyecto (frameworks)</div>${PLANTILLAS.map((p) => `<div class="ext-item"><div class="ext-ico">+</div><div class="ext-info"><div class="ext-nombre"><b>${esc(p.nombre)}</b></div><div class="ext-desc">${esc(p.desc)}</div></div><div class="ext-btns"><button type="button" class="btn sm" data-accion="plantilla" data-cmd="${esc(p.cmd)}">Crear</button></div></div>`).join("")}` : ""}
        <div class="git-titulo">Instalados ${this.tipo === "npm" ? `<small>${esc(npm.ruta ?? "(sin package.json)")}</small>` : ""} <span>${inst.length}</span></div>
        ${inst.length ? inst.map(item).join("") : `<p class="git-nota">${this.tipo === "npm" ? "Aún no hay dependencias. Instala una o crea un proyecto." : "Aún no instalaste paquetes. Las bases de datos (pymysql, psycopg2, pymongo, redis, sqlite3) ya vienen incluidas."}</p>`}
        <div class="git-titulo">Recomendados</div>${RECOMENDADOS[this.tipo].map(([n, d]) => item({ nombre: n, desc: d })).join("")}`;
    }
    this.raiz.innerHTML = `<div class="ext-tabs" role="tablist"><button type="button" role="tab" class="ext-tab${this.tipo === "npm" ? " on" : ""}" data-accion="tipo" data-tipo="npm">npm (JavaScript)</button><button type="button" role="tab" class="ext-tab${this.tipo === "pip" ? " on" : ""}" data-accion="tipo" data-tipo="pip">pip (Python)</button></div>
      <input type="search" name="buscar" class="ext-buscar" placeholder="${this.tipo === "npm" ? "Buscar en npm (ej.: react, chart.js, axios)" : "Nombre en PyPI (ej.: numpy, pandas)"}" value="${esc(valorBuscar)}" aria-label="Buscar librerías" autocomplete="off">
      <div class="ext-lista">${cuerpo}</div>`;
    const campo = this.raiz.querySelector("[name=buscar]");
    if (document.activeElement === document.body || this.enfocar) { campo.focus(); campo.setSelectionRange(campo.value.length, campo.value.length); this.enfocar = false; }
  }

  #clic(e) {
    const b = e.target.closest("[data-accion]");
    if (!b) return;
    const n = b.dataset.nombre;
    const cd = () => { const c = this.carpetaNpm(); return c ? `cd /workspace/${c} && ` : "cd /workspace && "; };
    if (b.dataset.accion === "tipo") { this.tipo = b.dataset.tipo; this.resultados = null; this.enfocar = true; const c = this.raiz.querySelector("[name=buscar]"); if (c) c.value = ""; return this.render(); }
    if (b.dataset.accion === "instalar") {
      if (this.tipo === "npm" ? !NOMBRE_NPM.test(n) : !NOMBRE_PIP.test(n)) return;
      this.correr(this.tipo === "npm" ? `${cd()}npm install ${n}` : `pip install ${n}`);
    } else if (b.dataset.accion === "quitar") this.correr(this.tipo === "npm" ? `${cd()}npm uninstall ${n}` : `pip uninstall ${n}`);
    else if (b.dataset.accion === "todos") { const ns = b.dataset.nombres.split(" ").filter((x) => NOMBRE_PIP.test(x)); if (ns.length) this.correr(`pip install ${ns.join(" ")}`); }
    else if (b.dataset.accion === "plantilla") this.correr(`cd /workspace && ${b.dataset.cmd}`);
    else if (b.dataset.accion === "requisitos") { const r = b.dataset.ruta; const c = FS.carpetaDe(r); this.correr(`cd /workspace${c ? "/" + c : ""} && pip install -r ${FS.nombreBase(r)}`); }
    setTimeout(() => this.render(), 1500);
  }
}
