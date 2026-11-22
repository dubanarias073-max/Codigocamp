// Módulos ES en la vista previa: lo que hace «npm run dev» de Vite, pero dentro del navegador y sin node_modules.
//
//  · <script type="module" src="/src/main.jsx"> y los import de tus archivos (./App.jsx, ../utils.ts, ./estilos.css,
//    ./datos.json, ./logo.png, /vite.svg) se resuelven dentro del proyecto. .jsx, .tsx y .ts se transpilan con el
//    compilador de TypeScript (JSX automático: react/jsx-runtime, o preact si el proyecto usa Preact).
//  · .vue y .svelte se compilan con el compilador oficial de su versión (compiladores.js), como los plugins de Vite.
//  · import React from "react" (o cualquier paquete) usa la versión de tu package.json desde esm.sh. Todos los paquetes
//    declarados se marcan «external», así hay UNA sola copia de React aunque react-dom también lo importe.
//  · import "bootstrap/dist/css/bootstrap.min.css" carga el CSS del paquete desde jsDelivr.
//  · Un paquete sin instalar o un archivo inexistente produce un error claro en la CONSOLA (como Vite).
// Todo se entrega a la página con un <script type="importmap"> de data: URLs (el iframe aislado no tiene servidor).
import * as FS from "./fs.js";
import { esMarcador, leerMarcador } from "./archivos.js";
import { carpetaDelPaquete, dependenciasDe } from "./paquetes.js";
import { reescribirUbicacion } from "./virtual.js";

const CODIGO = new Set(["js", "mjs", "cjs", "jsx", "ts", "tsx", "mts"]);
const EXTENSIONES = ["", ".js", ".jsx", ".ts", ".tsx", ".mjs", "/index.js", "/index.jsx", "/index.ts", "/index.tsx"];
const ESPECIFICADOR = /(\bimport\s*(?:[\w$*{}\s,]+?\s*from\s*)?|\bexport\s*(?:[\w$*{}\s,]+?\s*from\s*)|\bimport\s*\(\s*)(["'])([^"'\n]+)\2/g;

const pareceJsx = (t) => /<\/?[A-Za-z][\w.]*(\s[^<>]*)?\/?>|<>|<\/>/.test(t) && /return\s*\(?\s*<|=>\s*\(?\s*<|render\s*\(\s*</.test(t);
const dataJs = (codigo) => `data:text/javascript;charset=utf-8,${encodeURIComponent(codigo)}`;
const moduloError = (mensaje) => dataJs(`const e = new Error(${JSON.stringify(mensaje)}); console.error(e.message); throw e;`);
const b64 = (t) => { const b = new TextEncoder().encode(t); let s = ""; for (let i = 0; i < b.length; i += 0x8000) s += String.fromCharCode(...b.subarray(i, i + 0x8000)); return btoa(s); };

/** ¿La página usa módulos (script type="module")? Si no, la vista previa funciona como siempre. */
export function usaModulos(py, rutaHtml) {
  return /<script\b[^>]*\btype\s*=\s*["']?module/i.test(py.files[rutaHtml] ?? "");
}

/** Resuelve "/x", "./x" o "../x" a un archivo del proyecto, como Vite (raíz = carpeta del package.json, y public/). */
export function resolverRuta(py, desdeDir, ref, raiz) {
  let limpio = ref.split(/[?#]/)[0];
  try { limpio = decodeURIComponent(limpio); } catch { /* se usa tal cual */ }
  const bases = limpio.startsWith("/") ? [FS.resolver(raiz, "." + limpio), FS.resolver(FS.unir(raiz, "public"), "." + limpio)] : [FS.resolver(desdeDir, limpio)];
  for (const base of bases) {
    if (base === null) continue;
    for (const ext of EXTENSIONES) {
      const r = base + ext;
      if (r && FS.tieneArchivo(py, r)) return r;
    }
  }
  return null;
}

/** Alias de vite.config.js (resolve.alias): { "@": "src", "~": "src/assets" } con rutas relativas a la raíz. */
export function aliasDeVite(py, raiz) {
  const ruta = ["vite.config.js", "vite.config.ts", "vite.config.mjs", "vite.config.mts"].map((n) => FS.unir(raiz, n)).find((r) => FS.tieneArchivo(py, r));
  if (!ruta) return {};
  const texto = py.files[ruta];
  const i = texto.search(/\balias\s*:/);
  if (i < 0) return {};
  // Bloque del alias: desde «alias:» hasta su llave o corchete de cierre.
  const ini = texto.slice(i).search(/[{[]/) + i;
  let prof = 0;
  let fin = ini;
  for (; fin < texto.length; fin += 1) {
    if ("{[".includes(texto[fin])) prof += 1;
    else if ("}]".includes(texto[fin]) && --prof === 0) break;
  }
  const bloque = texto.slice(ini, fin + 1);
  const salida = {};
  const destino = (v) => v.replace(/^\.\//, "").replace(/^\//, "").replace(/\/$/, "");
  // '@': path.resolve(__dirname, './src') · '@': fileURLToPath(new URL('./src', import.meta.url)) · '@': '/src'
  for (const m of bloque.matchAll(/['"]?([@~#$\w./-]+)['"]?\s*:\s*(?:[\w.]+\(\s*(?:__dirname\s*,\s*|new URL\(\s*)?)?['"]([^'"]+)['"]/g)) salida[m[1]] = destino(m[2]);
  // { find: '@', replacement: '/src' }
  for (const m of bloque.matchAll(/find\s*:\s*['"]([^'"]+)['"][\s\S]*?replacement\s*:\s*(?:[\w.]+\(\s*(?:__dirname\s*,\s*|new URL\(\s*)?)?['"]([^'"]+)['"]/g)) salida[m[1]] = destino(m[2]);
  return salida;
}

/** Bloque `{ … }` que sigue a «clave:» en un texto (llaves balanceadas, sin contar las de dentro de comillas). */
function bloqueDe(texto, clave) {
  const i = texto.search(new RegExp(`\\b${clave}\\s*:\\s*\\{`));
  if (i < 0) return null;
  const ini = texto.indexOf("{", i);
  let prof = 0, comilla = null;
  for (let j = ini; j < texto.length; j += 1) {
    const c = texto[j];
    if (comilla) { if (c === "\\") j += 1; else if (c === comilla) comilla = null; continue; }
    if (c === "'" || c === '"' || c === "`") comilla = c;
    else if (c === "{") prof += 1;
    else if (c === "}" && --prof === 0) return texto.slice(ini, j + 1);
  }
  return null;
}

/**
 * server.proxy de vite.config.js, como lo usa «npm run dev»:
 *   proxy: { '/api': 'http://127.0.0.1:8000', '/img': { target: 'http://localhost:8000', rewrite: (p) => p.replace(/^\/img/, '') } }
 * → [{ p: "/api", d: "http://127.0.0.1:8000" }, { p: "/img", d: "http://localhost:8000", q: "^\\/img", s: "" }]
 */
export function proxyDeVite(py, raiz) {
  const ruta = ["vite.config.js", "vite.config.ts", "vite.config.mjs", "vite.config.mts"].map((n) => FS.unir(raiz, n)).find((r) => FS.tieneArchivo(py, r));
  if (!ruta) return [];
  const texto = py.files[ruta].replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/.*$/gm, "$1");
  const bloque = bloqueDe(bloqueDe(texto, "server") ?? "", "proxy");
  if (!bloque) return [];
  const reglas = [];
  const interior = bloque.slice(1, -1);
  // Entradas de primer nivel: 'clave': 'url'   o   'clave': { target: 'url', rewrite: … }
  const re = /(['"`])([^'"`]+)\1\s*:\s*(?:(['"`])([^'"`]+)\3|\{)/g;
  let m;
  while ((m = re.exec(interior))) {
    const prefijo = m[2];
    if (m[4] !== undefined) { reglas.push({ p: prefijo, d: m[4] }); continue; }
    const sub = bloqueDe(interior.slice(m.index), m[0].slice(0, m[0].lastIndexOf(":")).trim().replace(/^(['"`])|(['"`])$/g, "")) ?? bloqueDe("x:" + interior.slice(m.index + m[0].length - 1), "x");
    const objetivo = /target\s*:\s*(['"`])([^'"`]+)\1/.exec(sub || "")?.[2];
    if (!objetivo) continue;
    const regla = { p: prefijo, d: objetivo };
    const rw = /rewrite\s*:[^]*?\.replace\(\s*\/((?:\\.|[^/])+)\/[gimsuy]*\s*,\s*(['"`])([^'"`]*)\2\s*\)/.exec(sub || "");
    if (rw) { regla.q = rw[1]; regla.s = rw[3]; }
    reglas.push(regla);
    re.lastIndex = m.index + m[0].length + (sub ? sub.length - 1 : 0);
  }
  return reglas.sort((a, b) => b.p.length - a.p.length);   // como Vite: la más específica primero
}

/** Variables de entorno como Vite: import.meta.env con las VITE_* de .env, .env.local, .env.development… */
export function entornoDeVite(py, raiz) {
  const env = { MODE: "development", DEV: true, PROD: false, SSR: false, BASE_URL: "/" };
  for (const nombre of [".env", ".env.local", ".env.development", ".env.development.local"]) {
    const t = py.files[FS.unir(raiz, nombre)];
    if (typeof t !== "string") continue;
    for (const linea of t.split("\n")) {
      const m = /^\s*(?:export\s+)?([A-Za-z_][\w]*)\s*=\s*(.*?)\s*$/.exec(linea);
      if (!m || !m[1].startsWith("VITE_")) continue; // como Vite: solo las VITE_* llegan al navegador
      let v = m[2];
      const entreComillas = /^(["'])(.*?)\1/.exec(v);
      v = entreComillas ? entreComillas[2] : v.replace(/\s+#.*$/, "");
      env[m[1]] = v;
    }
  }
  return env;
}

/** CSS Modules: .boton → .boton_ab12 y el módulo exporta { boton: "boton_ab12" }. */
export function cssModulo(css, ruta) {
  let h = 0;
  for (const c of ruta) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  const sufijo = h.toString(36).slice(0, 5);
  const clases = {};
  const sinComentarios = css.replace(/\/\*[\s\S]*?\*\//g, "");
  const nuevo = sinComentarios.replace(/(url\([^)]*\)|"[^"]*"|'[^']*')|\.(-?[_a-zA-Z][\w-]*)/g, (todo, literal, clase, pos, total) => {
    if (literal) return literal;
    const antes = total.slice(0, pos);
    const dentroDeBloque = (antes.match(/{/g) || []).length > (antes.match(/}/g) || []).length && !/@media|@supports/.test(antes.slice(antes.lastIndexOf("{") - 40));
    if (dentroDeBloque && /:\s*[^;{}]*$/.test(antes)) return todo; // valores como 0.5em o .5s
    clases[clase] ??= `${clase}_${sufijo}`;
    return `.${clases[clase]}`;
  });
  return { css: nuevo, clases };
}

/** URL del CDN para un paquete declarado. */
function urlPaquete(deps, nombre, subruta) {
  const version = String(deps[nombre]).replace(/^[\^~=v]/, "");
  const v = /^\d+(\.\d+){0,2}([-+][\w.]+)?$/.test(version) ? version : "latest";
  if (/\.css$/i.test(subruta)) return { css: `https://cdn.jsdelivr.net/npm/${nombre}@${v}${subruta}` };
  const externos = Object.keys(deps).filter((d) => d !== nombre && !d.startsWith("@types/"));
  return { js: `https://esm.sh/${nombre}@${v}${subruta}${externos.length ? `?external=${externos.join(",")}` : ""}` };
}

/**
 * Prepara los módulos de una página.
 * @param {object} py
 * @param {string} rutaHtml
 * @param {object} o
 * @param {(codigo, ruta, opciones)=>Promise<string>} o.transpilar   JSX/TS → JS (ver transpilarModulo en ejecucion.js)
 * @param {Map<string,string>} [o.enlaces]   hash → URL de los archivos de la cuenta (imágenes, videos…)
 * @returns {Promise<{ importmap: object, entrada: (ref)=>string|null, reescribir: (codigo)=>string, errores: string[] }>}
 */
export async function prepararModulos(py, rutaHtml, { transpilar, enlaces = new Map() }) {
  const dirHtml = FS.carpetaDe(rutaHtml);
  const raiz = carpetaDelPaquete(py, dirHtml) ?? dirHtml;
  const deps = dependenciasDe(py, dirHtml);
  const alias = aliasDeVite(py, raiz);
  const env = entornoDeVite(py, raiz);
  const prologo = `const __ccEnv = ${JSON.stringify(env)};\n`;
  const jsxImportSource = "preact" in deps && !("react" in deps) ? "preact" : "react";
  const imports = {};
  const errores = [];
  const hechos = new Set();
  const pendientes = [];

  const especificadorDe = (ref, desde) => {
    if (/^(https?:|data:|blob:)/i.test(ref)) return ref;
    for (const [clave, dir] of Object.entries(alias)) {
      if (ref === clave || ref.startsWith(clave + "/")) { ref = `/${dir}${ref.slice(clave.length)}`; break; }
    }
    if (ref.startsWith(".") || ref.startsWith("/")) {
      const r = resolverRuta(py, FS.carpetaDe(desde), ref, raiz);
      if (!r) {
        const clave = `@cc-falta/${desde}/${ref}`;
        imports[clave] = moduloError(`No se encontró «${ref}» (importado desde ${desde}). Revisa el nombre y la carpeta.`);
        errores.push(`${desde}: no se encontró «${ref}»`);
        return clave;
      }
      const clave = `@cc/${r}`;
      if (!hechos.has(r)) { hechos.add(r); pendientes.push(r); }
      return clave;
    }
    const m = /^((?:@[^/]+\/)?[^/]+)(\/.*)?$/.exec(ref);
    if (!m) return ref;
    const [, nombre, subruta = ""] = m;
    if (!(nombre in deps)) {
      if (!imports[ref]) {
        imports[ref] = moduloError(`El paquete «${nombre}» no está instalado. Ejecuta en la terminal: npm install ${nombre}`);
        errores.push(`El paquete «${nombre}» no está instalado. Ejecuta: npm install ${nombre}`);
      }
      return ref;
    }
    if (!imports[ref]) {
      const u = urlPaquete(deps, nombre, subruta);
      imports[ref] = u.js ?? dataJs(`const l = document.createElement("link"); l.rel = "stylesheet"; l.href = ${JSON.stringify(u.css)}; document.head.appendChild(l);`);
    }
    return ref;
  };

  const reescribirDesde = (codigo, desde) => codigo.replace(ESPECIFICADOR, (todo, antes, comilla, ref) => `${antes}${comilla}${especificadorDe(ref, desde)}${comilla}`);

  const moduloDe = async (ruta) => {
    const texto = py.files[ruta];
    const ext = FS.extension(ruta);
    const m = leerMarcador(texto);
    if (m) {
      const url = enlaces.get(m.hash);
      return url ? dataJs(`export default ${JSON.stringify(url)};`) : moduloError(`No se pudo cargar ${ruta} (¿sin conexión?).`);
    }
    if (ext === "css") {
      const esModulo = /\.module\.css$/i.test(ruta);
      const css0 = texto.replace(/url\(\s*(?:"([^"]*)"|'([^']*)'|([^)'"]*?))\s*\)/gi, (todo, a, b, c) => {
        const r = resolverRuta(py, FS.carpetaDe(ruta), (a ?? b ?? c ?? "").trim(), raiz);
        const mm = r ? leerMarcador(py.files[r]) : null;
        if (mm && enlaces.get(mm.hash)) return `url(${enlaces.get(mm.hash)})`;
        if (r && FS.extension(r) === "svg" && !esMarcador(py.files[r])) return `url(data:image/svg+xml;base64,${b64(py.files[r])})`;
        return todo;
      });
      const { css, clases } = esModulo ? cssModulo(css0, ruta) : { css: css0, clases: null };
      return dataJs(`const s = document.createElement("style"); s.dataset.archivo = ${JSON.stringify(ruta)}; s.textContent = ${JSON.stringify(css)}; document.head.appendChild(s); export default ${JSON.stringify(clases ?? css)};`);
    }
    if (ext === "json") {
      try { return dataJs(`export default ${JSON.stringify(JSON.parse(texto))};`); } catch (e) { return moduloError(`${ruta} no es un JSON válido: ${e.message}`); }
    }
    if (ext === "svg") return dataJs(`export default ${JSON.stringify(`data:image/svg+xml;base64,${b64(texto)}`)};`);
    if (ext === "vue" || ext === "svelte") {   // componentes de Vue y Svelte: se compilan con su compilador oficial
      try {
        const C = await import("./compiladores.js");
        let codigo = ext === "vue" ? await C.compilarVue(texto, ruta, deps, transpilar) : await C.compilarSvelte(texto, ruta, deps);
        codigo = reescribirUbicacion(codigo.replace(/\bimport\.meta\.env\b/g, "__ccEnv"));
        return dataJs((codigo.includes("__ccEnv") ? prologo : "") + reescribirDesde(codigo, ruta) + `\n//# sourceURL=${ruta}`);
      } catch (e) {
        const msg = /Failed to fetch|import/i.test(e.message) && !/\n/.test(e.message) ? `No se pudo descargar el compilador de ${ext === "vue" ? "Vue" : "Svelte"} (¿sin conexión?)` : e.message;
        errores.push(`${ruta}: ${msg}`);
        return moduloError(`Error en ${ruta}: ${msg}`);
      }
    }
    if (!CODIGO.has(ext)) return dataJs(`export default ${JSON.stringify(texto)};`);
    let codigo = texto;
    if (["jsx", "tsx", "ts", "mts"].includes(ext) || pareceJsx(texto)) {
      try { codigo = await transpilar(texto, ruta, { jsxImportSource }); }
      catch (e) { errores.push(`${ruta}: ${e.message}`); return moduloError(`Error de sintaxis en ${ruta}: ${e.message}`); }
    }
    // El JSX automático importa react/jsx-runtime: necesita el paquete declarado.
    // import.meta.env y process.env.NODE_ENV como en Vite.
    codigo = codigo.replace(/\bimport\.meta\.env\b/g, "__ccEnv").replace(/\bprocess\.env\.NODE_ENV\b/g, '"development"');
    codigo = reescribirUbicacion(codigo);   // location → dirección virtual de la vista previa (virtual.js)
    const usaEnv = codigo.includes("__ccEnv");
    return dataJs((usaEnv ? prologo : "") + reescribirDesde(codigo, ruta) + `\n//# sourceURL=${ruta}`);
  };

  const procesar = async () => {
    while (pendientes.length) {
      const ruta = pendientes.shift();
      imports[`@cc/${ruta}`] = await moduloDe(ruta);
    }
  };

  return {
    importmap: { imports },
    errores,
    /** Para <script type="module" src="..."> de la página: devuelve el especificador a importar. */
    entrada: (ref) => especificadorDe(ref, rutaHtml),
    /** Para <script type="module"> con código dentro de la página. */
    reescribir: (codigo) => { const c = reescribirUbicacion(codigo.replace(/\bimport\.meta\.env\b/g, "__ccEnv")); return (c.includes("__ccEnv") ? prologo : "") + reescribirDesde(c, rutaHtml); },
    /** Termina de preparar los módulos pedidos por entrada()/reescribir(). */
    terminar: procesar,
  };
}

const SCRIPT_MODULO = /<script\b([^>]*\btype\s*=\s*["']?module["']?[^>]*)>([\s\S]*?)<\/script>/gi;

/**
 * Todo lo que la vista previa necesita para los módulos de una página:
 * { importmap, srcs: Map(src → especificador), inlines: Map(código → código reescrito), errores }.
 */
export async function modulosDePagina(py, rutaHtml, o) {
  const m = await prepararModulos(py, rutaHtml, o);
  const srcs = new Map();
  const inlines = new Map();
  for (const [, attrs, cuerpo] of (py.files[rutaHtml] ?? "").matchAll(SCRIPT_MODULO)) {
    const src = (/\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(attrs) || []).slice(1).find((x) => x !== undefined);
    if (src !== undefined) srcs.set(src, m.entrada(src));
    else if (cuerpo.trim()) inlines.set(cuerpo, m.reescribir(cuerpo));
  }
  await m.terminar();
  return { importmap: m.importmap, srcs, inlines, errores: m.errores };
}
