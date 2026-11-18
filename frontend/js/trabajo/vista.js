// Vista previa de páginas web del proyecto (se muestra en un iframe aislado con sandbox="allow-scripts allow-popups").
import * as FS from "./fs.js";
import { leerMarcador } from "./archivos.js";
import { dependenciasDe } from "./paquetes.js";

// Se inserta al principio de la página: reenvía console.* y errores a la pestaña CONSOLA y avisa de los clics en enlaces.
const PUENTE = `(function(){var P=function(m){try{parent.postMessage(m,"*")}catch(e){}};
try{localStorage.length}catch(e){var M=function(){var d={};return{getItem:function(k){return Object.prototype.hasOwnProperty.call(d,k)?d[k]:null},setItem:function(k,v){d[k]=String(v)},removeItem:function(k){delete d[k]},clear:function(){d={}},key:function(i){return Object.keys(d)[i]||null},get length(){return Object.keys(d).length}}};try{Object.defineProperty(window,"localStorage",{value:M(),configurable:true});Object.defineProperty(window,"sessionStorage",{value:M(),configurable:true})}catch(x){}}
["log","info","warn","error","debug"].forEach(function(n){var o=console[n];console[n]=function(){var a=[].slice.call(arguments).map(function(x){try{return typeof x==="string"?x:(x instanceof Error?(x.stack||String(x)):JSON.stringify(x))}catch(e){return String(x)}});P({cc:"consola",nivel:n,texto:a.join(" ")});return o.apply(console,arguments)}});
addEventListener("error",function(e){P({cc:"consola",nivel:"error",texto:(e.message||"Error")+(e.lineno?" (línea "+e.lineno+")":"")})});
addEventListener("unhandledrejection",function(e){P({cc:"consola",nivel:"error",texto:"Promesa rechazada: "+((e.reason&&e.reason.message)||e.reason)})});
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[href]");if(!a)return;var h=a.getAttribute("href");if(!h||h.charAt(0)==="#"||/^(mailto:|tel:|javascript:)/i.test(h))return;
if(/^https?:/i.test(h)){e.preventDefault();window.open(h,"_blank","noopener");return}e.preventDefault();P({cc:"nav",href:h})},true)})();`;

const atributo = (etiqueta, nombre) => {
  const m = new RegExp(`\\s${nombre}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, "i").exec(etiqueta);
  return m ? (m[1] ?? m[2] ?? m[3]) : null;
};
const sinAtributo = (etiqueta, nombre) => etiqueta.replace(new RegExp(`\\s${nombre}\\s*=\\s*(?:"[^"]*"|'[^']*'|[^\\s>]+)`, "i"), "");
const rutaLocal = (py, dir, ref) => {
  if (!ref || /^([a-z][a-z0-9+.-]*:|\/\/|#|data:)/i.test(ref)) return null;
  const limpia = ref.split(/[?#]/)[0];
  const r = FS.resolver(dir, limpia);
  return r !== null && FS.tieneArchivo(py, r) ? r : null;
};

/** Convierte un enlace de la página (href) en la ruta de otro HTML del proyecto, o null. */
export function resolverEnlace(py, rutaActual, href) {
  const r = rutaLocal(py, FS.carpetaDe(rutaActual), href);
  return r && /\.html?$/i.test(r) ? r : null;
}

/** Ruta del HTML que se abre por defecto: el de la carpeta de `preferida`, index.html o el primero que haya. */
export function paginaPrincipal(py, preferida = null) {
  if (preferida && /\.html?$/i.test(preferida) && FS.tieneArchivo(py, preferida)) return preferida;
  const htmls = Object.keys(py.files).filter((r) => /\.html?$/i.test(r)).sort((a, b) => a.split("/").length - b.split("/").length || a.localeCompare(b));
  return htmls.find((r) => FS.nombreBase(r).toLowerCase() === "index.html") ?? htmls[0] ?? null;
}

/** Inserta `texto` justo antes de la primera coincidencia de `patron` (sin interpretar nada del texto). null si no hay. */
function insertarAntes(html, patron, texto) {
  const m = patron.exec(html);
  return m ? html.slice(0, m.index) + texto + html.slice(m.index) : null;
}

/** Página HTML del proyecto que carga este archivo .js (por <script src> o, como siempre, script.js junto a una página sin scripts). */
export function paginaQueUsa(py, rutaJs) {
  const principal = paginaPrincipal(py);
  const htmls = Object.keys(py.files).filter((r) => /\.html?$/i.test(r)).sort((a, b) => (a === principal ? -1 : b === principal ? 1 : a.localeCompare(b)));
  for (const h of htmls) {
    const dir = FS.carpetaDe(h);
    let enlazaAlgo = false;
    for (const m of py.files[h].matchAll(/<script\b[^>]*\bsrc\s*=[^>]*>/gi)) {
      enlazaAlgo = true;
      if (rutaLocal(py, dir, atributo(m[0], "src")) === rutaJs) return h;
    }
    if (!enlazaAlgo && FS.unir(dir, "script.js") === rutaJs) return h;
  }
  return null;
}

// ---- archivos (imágenes, videos, audio, PDF, fuentes…) ----
// La vista previa es un iframe aislado que no envía la sesión de la cuenta: los archivos se cargan con enlaces
// temporales firmados (mapa hash → URL que da ClienteArchivos.enlaces). Los .svg de texto se incrustan como data: URL.
const b64Texto = (t) => { const b = new TextEncoder().encode(t); let s = ""; for (let i = 0; i < b.length; i += 0x8000) s += String.fromCharCode(...b.subarray(i, i + 0x8000)); return btoa(s); };

/** URL del archivo del proyecto al que apunta `ref` (desde la carpeta `dir`), o null. */
export function urlImagen(py, dir, ref, imagenes) {
  const r = rutaLocal(py, dir, ref);
  if (!r) return null;
  const m = leerMarcador(py.files[r]);
  if (m) return imagenes.get(m.hash) ?? null;
  if (FS.extension(r) === "svg") return `data:image/svg+xml;base64,${b64Texto(py.files[r])}`;
  return null;
}

const ATRIBUTO_IMAGEN = /(\s(?:src|poster|data-src|data)\s*=\s*)(?:"([^"]*)"|'([^']*)'|([^\s>"']+))/gi;
const URL_CSS = /url\(\s*(?:"([^"]*)"|'([^']*)'|([^)'"]*?))\s*\)/gi;

/** Cambia src="img/a.png" y url(img/a.png) por la imagen incrustada. */
export function incrustarImagenes(py, dir, texto, imagenes, { html = true } = {}) {
  let t = texto.replace(URL_CSS, (todo, a, b, c) => { const u = urlImagen(py, dir, (a ?? b ?? c ?? "").trim(), imagenes); return u ? `url(${u})` : todo; }); // sin comillas: así no rompe un style="…" ni un style='…'
  if (html) {
    t = t.replace(ATRIBUTO_IMAGEN, (todo, pre, a, b, c) => { const u = urlImagen(py, dir, a ?? b ?? c, imagenes); return u ? `${pre}"${u}"` : todo; });
    t = t.replace(/(<link\b[^>]*\brel\s*=\s*["']?(?:icon|shortcut icon|apple-touch-icon)[^>]*>)/gi, (etiqueta) => {
      const u = urlImagen(py, dir, atributo(etiqueta, "href"), imagenes);
      return u ? etiqueta.replace(/(\shref\s*=\s*)(?:"[^"]*"|'[^']*'|[^\s>]+)/i, `$1"${u}"`) : etiqueta;
    });
    // Enlaces a archivos (un PDF, un video…): se abren en otra pestaña.
    t = t.replace(/<a\b[^>]*>/gi, (etiqueta) => {
      const u = urlImagen(py, dir, atributo(etiqueta, "href"), imagenes);
      if (!u || u.startsWith("data:")) return etiqueta;
      return etiqueta.replace(/(\shref\s*=\s*)(?:"[^"]*"|'[^']*'|[^\s>]+)/i, `$1"${u}" target="_blank" rel="noopener"`);
    });
  }
  return t;
}

/** Imágenes que el JavaScript de la página nombra (p. ej. img.src = "img/gato.png"): se arreglan mientras la página corre. */
function imagenesParaJs(py, dir, scripts, imagenes) {
  const mapa = {};
  for (const [ruta, texto] of Object.entries(py.files)) {
    const nombre = FS.nombreBase(ruta);
    if (!scripts.some((s) => s.includes(nombre))) continue;
    const m = leerMarcador(texto);
    const url = m ? imagenes.get(m.hash) : FS.extension(ruta) === "svg" ? `data:image/svg+xml;base64,${b64Texto(texto)}` : null;
    if (url) mapa[ruta] = url;
  }
  return mapa;
}

const PUENTE_IMAGENES = `(function(M,D){if(!Object.keys(M).length)return;var R=function(ref){if(!ref||/^([a-z][a-z0-9+.-]*:|\\/\\/|#)/i.test(ref))return null;var p=(D?D.split("/"):[]),s=ref.split(/[?#]/)[0].split("/");if(ref.charAt(0)==="/")p=[];for(var i=0;i<s.length;i++){if(!s[i]||s[i]===".")continue;if(s[i]==="..")p.pop();else p.push(s[i])}return M[p.join("/")]||null};
var F=function(el){if(!el||el.nodeType!==1)return;["src","poster"].forEach(function(a){var v=el.getAttribute&&el.getAttribute(a),u=R(v);if(u&&v!==u)el.setAttribute(a,u)});if(el.style&&el.style.backgroundImage){el.style.backgroundImage=el.style.backgroundImage.replace(/url\\(["']?([^"')]+)["']?\\)/g,function(t,r){var u=R(r);return u?"url("+u+")":t})}};
new MutationObserver(function(ms){ms.forEach(function(m){if(m.type==="attributes")F(m.target);else m.addedNodes.forEach(function(n){F(n);if(n.querySelectorAll)n.querySelectorAll("[src],[poster],[style]").forEach(F)})})}).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:["src","poster","style"]});
try{var d=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,"src");Object.defineProperty(HTMLImageElement.prototype,"src",{configurable:true,get:d.get,set:function(v){d.set.call(this,R(String(v))||v)}})}catch(e){}})`;

export function construirVistaPrevia(py, rutaHtml, { imagenes = new Map(), modulos = null } = {}) {
  let html = py.files[rutaHtml] ?? "";
  // <link href="node_modules/bootstrap/..."> y <script src="node_modules/...">: no hay node_modules, se usa jsDelivr
  // con la versión instalada (npm install bootstrap). Si el paquete no está en package.json se avisa en la consola.
  const deps = dependenciasDe(py, FS.carpetaDe(rutaHtml));
  const faltantes = new Set();
  html = html.replace(/(\s(?:src|href)\s*=\s*)(["'])(?:\.{0,2}\/)*node_modules\/((?:@[^/"']+\/)?[^/"']+)(\/[^"']*)?\2/gi, (todo, pre, q, nombre, resto = "") => {
    if (!(nombre in deps)) { faltantes.add(nombre); return todo; }
    const v = String(deps[nombre]).replace(/^[\^~=v]/, "");
    return `${pre}${q}https://cdn.jsdelivr.net/npm/${nombre}@${/^\d/.test(v) ? v : "latest"}${resto}${q}`;
  });
  if (faltantes.size) html = `<script>console.error(${JSON.stringify(`Falta instalar: ${[...faltantes].join(", ")}. Ejecuta: npm install ${[...faltantes].join(" ")}`)})</script>` + html;
  // Módulos (React, Vite…): cada <script type="module"> importa desde el import map que preparó modulos.js.
  if (modulos) {
    html = html.replace(/<script\b([^>]*\btype\s*=\s*["']?module["']?[^>]*)>([\s\S]*?)<\/script>/gi, (todo, attrs, cuerpo) => {
      const src = (/\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(attrs) || []).slice(1).find((x) => x !== undefined);
      const codigo = src !== undefined ? `import ${JSON.stringify(modulos.srcs.get(src) ?? src)};` : (modulos.inlines.get(cuerpo) ?? cuerpo);
      return `<script type="module">${codigo.replace(/<\/script/gi, "<\\/script")}</script>`;
    });
  }
  const dir = FS.carpetaDe(rutaHtml);
  let tieneCSS = false;
  let tieneJS = false;
  if (modulos && (modulos.srcs.size || modulos.inlines.size)) tieneJS = true; // ya tiene sus scripts: no se agrega script.js
  const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]);
  html = incrustarImagenes(py, dir, html, imagenes);
  html = html.replace(/<link\b[^>]*>/gi, (etiqueta) => {
    if (!/rel\s*=\s*["']?stylesheet/i.test(etiqueta)) return etiqueta;
    tieneCSS = true;
    const r = rutaLocal(py, dir, atributo(etiqueta, "href"));
    return r ? `<style data-archivo="${r}">\n${incrustarImagenes(py, FS.carpetaDe(r), py.files[r], imagenes, { html: false }).replace(/<\/style/gi, "<\\/style")}\n</style>` : etiqueta;
  });
  html = html.replace(/<script\b[^>]*\bsrc\s*=[^>]*>\s*<\/script>/gi, (etiqueta) => {
    tieneJS = true;
    const r = rutaLocal(py, dir, atributo(etiqueta, "src"));
    if (!r) return etiqueta;
    scripts.push(py.files[r]);
    const apertura = sinAtributo(etiqueta.slice(0, etiqueta.indexOf(">") + 1), "src");
    return `${apertura}\n${py.files[r].replace(/<\/script/gi, "<\\/script")}\n</script>`;
  });
  // Compatibilidad: páginas que no enlazan nada reciben styles.css y script.js de su carpeta, como antes.
  // OJO: el contenido del usuario nunca se pasa como texto de reemplazo a String.replace, porque JavaScript interpreta en él
  // secuencias como $&, $' o $` y destruiría la página (por ejemplo con '$' + precio). Se inserta cortando y uniendo.
  const css = FS.unir(dir, "styles.css");
  const js = FS.unir(dir, "script.js");
  if (!tieneCSS && FS.tieneArchivo(py, css)) {
    const estilo = `<style data-archivo="${css}">\n${incrustarImagenes(py, dir, py.files[css], imagenes, { html: false }).replace(/<\/style/gi, "<\\/style")}\n</style>`;
    html = insertarAntes(html, /<\/head>/i, estilo) ?? estilo + html;
  }
  if (!tieneJS && FS.tieneArchivo(py, js)) {
    scripts.push(py.files[js]);
    const bloque = `<script>\n${py.files[js].replace(/<\/script/gi, "<\\/script")}\n</script>`;
    html = insertarAntes(html, /<\/body>/i, bloque) ?? html + bloque;
  }
  const mapaJs = imagenesParaJs(py, dir, scripts, imagenes);
  const mapaImport = modulos ? `<script type="importmap">${JSON.stringify(modulos.importmap).replace(/</g, "\\u003c")}</script>` : "";
  const puente = `<script>${PUENTE}${Object.keys(mapaJs).length ? `${PUENTE_IMAGENES}(${JSON.stringify(mapaJs).replace(/</g, "\\u003c")},${JSON.stringify(dir)});` : ""}</script>${mapaImport}`;
  return /<head[^>]*>/i.test(html) ? html.replace(/<head[^>]*>/i, (m) => `${m}${puente}`) : puente + html;
}
