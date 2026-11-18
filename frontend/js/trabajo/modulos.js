// Módulos ES en la vista previa: lo que hace «npm run dev» de Vite, pero dentro del navegador y sin node_modules.
//
//  · <script type="module" src="/src/main.jsx"> y los import de tus archivos (./App.jsx, ../utils.ts, ./estilos.css,
//    ./datos.json, ./logo.png, /vite.svg) se resuelven dentro del proyecto. .jsx, .tsx y .ts se transpilan con el
//    compilador de TypeScript (JSX automático: react/jsx-runtime, o preact si el proyecto usa Preact).
//  · import React from "react" (o cualquier paquete) usa la versión de tu package.json desde esm.sh. Todos los paquetes
//    declarados se marcan «external», así hay UNA sola copia de React aunque react-dom también lo importe.
//  · import "bootstrap/dist/css/bootstrap.min.css" carga el CSS del paquete desde jsDelivr.
//  · Un paquete sin instalar o un archivo inexistente produce un error claro en la CONSOLA (como Vite).
// Todo se entrega a la página con un <script type="importmap"> de data: URLs (el iframe aislado no tiene servidor).
import * as FS from "./fs.js";
import { esMarcador, leerMarcador } from "./archivos.js";
import { carpetaDelPaquete, dependenciasDe } from "./paquetes.js";

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
  const limpio = ref.split(/[?#]/)[0];
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
  const jsxImportSource = "preact" in deps && !("react" in deps) ? "preact" : "react";
  const imports = {};
  const errores = [];
  const hechos = new Set();
  const pendientes = [];

  const especificadorDe = (ref, desde) => {
    if (/^(https?:|data:|blob:)/i.test(ref)) return ref;
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
      const css = texto.replace(/url\(\s*(?:"([^"]*)"|'([^']*)'|([^)'"]*?))\s*\)/gi, (todo, a, b, c) => {
        const r = resolverRuta(py, FS.carpetaDe(ruta), (a ?? b ?? c ?? "").trim(), raiz);
        const mm = r ? leerMarcador(py.files[r]) : null;
        if (mm && enlaces.get(mm.hash)) return `url(${enlaces.get(mm.hash)})`;
        if (r && FS.extension(r) === "svg" && !esMarcador(py.files[r])) return `url(data:image/svg+xml;base64,${b64(py.files[r])})`;
        return todo;
      });
      return dataJs(`const s = document.createElement("style"); s.dataset.archivo = ${JSON.stringify(ruta)}; s.textContent = ${JSON.stringify(css)}; document.head.appendChild(s); export default ${JSON.stringify(css)};`);
    }
    if (ext === "json") {
      try { return dataJs(`export default ${JSON.stringify(JSON.parse(texto))};`); } catch (e) { return moduloError(`${ruta} no es un JSON válido: ${e.message}`); }
    }
    if (ext === "svg") return dataJs(`export default ${JSON.stringify(`data:image/svg+xml;base64,${b64(texto)}`)};`);
    if (!CODIGO.has(ext)) return dataJs(`export default ${JSON.stringify(texto)};`);
    let codigo = texto;
    if (["jsx", "tsx", "ts", "mts"].includes(ext) || pareceJsx(texto)) {
      try { codigo = await transpilar(texto, ruta, { jsxImportSource }); }
      catch (e) { errores.push(`${ruta}: ${e.message}`); return moduloError(`Error de sintaxis en ${ruta}: ${e.message}`); }
    }
    // El JSX automático importa react/jsx-runtime: necesita el paquete declarado.
    return dataJs(reescribirDesde(codigo, ruta) + `\n//# sourceURL=${ruta}`);
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
    reescribir: (codigo) => reescribirDesde(codigo, rutaHtml),
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
