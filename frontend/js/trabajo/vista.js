// Vista previa de páginas web del proyecto (se muestra en un iframe aislado con sandbox="allow-scripts allow-popups").
import * as FS from "./fs.js";

// Se inserta al principio de la página: reenvía console.* y errores a la pestaña CONSOLA y avisa de los clics en enlaces.
const PUENTE = `(function(){var P=function(m){try{parent.postMessage(m,"*")}catch(e){}};
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

export function construirVistaPrevia(py, rutaHtml) {
  let html = py.files[rutaHtml] ?? "";
  const dir = FS.carpetaDe(rutaHtml);
  let tieneCSS = false;
  let tieneJS = false;
  html = html.replace(/<link\b[^>]*>/gi, (etiqueta) => {
    if (!/rel\s*=\s*["']?stylesheet/i.test(etiqueta)) return etiqueta;
    tieneCSS = true;
    const r = rutaLocal(py, dir, atributo(etiqueta, "href"));
    return r ? `<style data-archivo="${r}">\n${py.files[r].replace(/<\/style/gi, "<\\/style")}\n</style>` : etiqueta;
  });
  html = html.replace(/<script\b[^>]*\bsrc\s*=[^>]*>\s*<\/script>/gi, (etiqueta) => {
    tieneJS = true;
    const r = rutaLocal(py, dir, atributo(etiqueta, "src"));
    if (!r) return etiqueta;
    const apertura = sinAtributo(etiqueta.slice(0, etiqueta.indexOf(">") + 1), "src");
    return `${apertura}\n${py.files[r].replace(/<\/script/gi, "<\\/script")}\n</script>`;
  });
  // Compatibilidad: páginas que no enlazan nada reciben styles.css y script.js de su carpeta, como antes.
  const css = FS.unir(dir, "styles.css");
  const js = FS.unir(dir, "script.js");
  if (!tieneCSS && FS.tieneArchivo(py, css)) html = html.replace(/<\/head>/i, `<style data-archivo="${css}">\n${py.files[css].replace(/<\/style/gi, "<\\/style")}\n</style></head>`) || html;
  if (!tieneCSS && FS.tieneArchivo(py, css) && !html.includes(`data-archivo="${css}"`)) html = `<style>${py.files[css]}</style>${html}`;
  if (!tieneJS && FS.tieneArchivo(py, js)) {
    const bloque = `<script>\n${py.files[js].replace(/<\/script/gi, "<\\/script")}\n</script>`;
    html = /<\/body>/i.test(html) ? html.replace(/<\/body>/i, `${bloque}</body>`) : html + bloque;
  }
  const puente = `<script>${PUENTE}</script>`;
  return /<head[^>]*>/i.test(html) ? html.replace(/<head[^>]*>/i, (m) => `${m}${puente}`) : puente + html;
}
