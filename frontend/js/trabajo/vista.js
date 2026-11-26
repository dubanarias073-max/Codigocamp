// Vista previa de páginas web del proyecto (se muestra en un iframe aislado con sandbox="allow-scripts allow-popups").
import * as FS from "./fs.js";
import { reescribirAtributos, reescribirUbicacion, scriptVirtual } from "./virtual.js";
import { leerMarcador } from "./archivos.js";
import { dependenciasDe } from "./paquetes.js";

// Se inserta al principio de la página: reenvía console.* y errores a la pestaña CONSOLA y avisa de los clics en enlaces.
const PUENTE = `(function(){var P=function(m){try{parent.postMessage(m,"*")}catch(e){}};if(!window.__ccLoc){window.__ccLoc=location;try{window.__ccTop=top.location}catch(e){window.__ccTop=location}}
try{localStorage.length}catch(e){var M=function(){var d={};return{getItem:function(k){return Object.prototype.hasOwnProperty.call(d,k)?d[k]:null},setItem:function(k,v){d[k]=String(v)},removeItem:function(k){delete d[k]},clear:function(){d={}},key:function(i){return Object.keys(d)[i]||null},get length(){return Object.keys(d).length}}};try{Object.defineProperty(window,"localStorage",{value:M(),configurable:true});Object.defineProperty(window,"sessionStorage",{value:M(),configurable:true})}catch(x){}}
["log","info","warn","error","debug"].forEach(function(n){var o=console[n];console[n]=function(){var a=[].slice.call(arguments).map(function(x){try{return typeof x==="string"?x:(x instanceof Error?(x.stack||String(x)):JSON.stringify(x))}catch(e){return String(x)}});P({cc:"consola",nivel:n,texto:a.join(" ")});return o.apply(console,arguments)}});
var sT=0;addEventListener("scroll",function(){clearTimeout(sT);sT=setTimeout(function(){P({cc:"scroll",y:scrollY})},150)},{passive:true});addEventListener("message",function(e){var d=e.data;if(d&&d.cc==="irscroll"){var n=0;(function f(){scrollTo(0,d.y);if(Math.abs(scrollY-d.y)>2&&n++<20)setTimeout(f,50)})()}});
addEventListener("error",function(e){P({cc:"consola",nivel:"error",texto:(e.message||"Error")+(e.lineno?" (línea "+e.lineno+")":"")})});
addEventListener("unhandledrejection",function(e){P({cc:"consola",nivel:"error",texto:"Promesa rechazada: "+((e.reason&&e.reason.message)||e.reason)})});
var EXT=function(h){h=String(h||"").trim();if(/^\\/\\//.test(h))h="https:"+h;else if(/^www\\./i.test(h))h="https://"+h;return /^(https?:|mailto:|tel:)/i.test(h)&&!/^https?:\\/\\/(localhost|127\\.0\\.0\\.1|0\\.0\\.0\\.0)(:|\\/|$)/i.test(h)?h:null};
var wo=window.open;window.open=function(u,n,f){var x=EXT(u);if(x){P({cc:"externo",href:x});return null}return wo.apply(window,arguments)};
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[href]");if(!a)return;var h=a.getAttribute("href");var x=EXT(h);if(x){e.preventDefault();P({cc:"externo",href:x});return}if(window.__ccVirtual)return;if(!h||h.charAt(0)==="#"||/^javascript:/i.test(h))return;
e.preventDefault();P({cc:"nav",href:h})},true);
document.addEventListener("submit",function(e){var f=e.target;var x=f&&EXT(f.getAttribute("action"));if(x&&!/^(mailto|tel):/i.test(x)&&(f.method||"get").toLowerCase()==="get"){e.preventDefault();var q=new URLSearchParams(new FormData(f)).toString();P({cc:"externo",href:x+(q?(x.indexOf("?")<0?"?":"&")+q:"")})}},true)})();`;

const atributo = (etiqueta, nombre) => {
  const m = new RegExp(`\\s${nombre}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, "i").exec(etiqueta);
  return m ? (m[1] ?? m[2] ?? m[3]) : null;
};
const sinAtributo = (etiqueta, nombre) => etiqueta.replace(new RegExp(`\\s${nombre}\\s*=\\s*(?:"[^"]*"|'[^']*'|[^\\s>]+)`, "i"), "");
const rutaLocal = (py, dir, ref) => {
  if (!ref || /^([a-z][a-z0-9+.-]*:|\/\/|#|data:)/i.test(ref)) return null;
  let limpia = ref.split(/[?#]/)[0];
  try { limpia = decodeURIComponent(limpia); } catch { /* «%» suelto: se usa tal cual */ }
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

// Como el aviso rojo de Vite: si una librería (react, vue…) no se pudo descargar o un módulo no carga, la vista previa
// lo explica en vez de quedarse en blanco.
const CAPA_ERRORES_MODULOS = `(function(){var hecho=false;function mostrar(t,d){if(hecho)return;hecho=true;var f=function(){var c=document.createElement("div");c.id="cc-capa-error";c.setAttribute("role","alert");c.style.cssText="position:fixed;inset:0;z-index:2147483647;display:flex;align-items:flex-start;justify-content:center;padding:24px;background:rgba(15,23,42,.72);font:14px/1.5 system-ui,sans-serif;overflow:auto";
var b=document.createElement("div");b.style.cssText="max-width:640px;width:100%;padding:18px 20px;border-radius:14px;background:#1e1b2e;color:#fde2e2;border-top:5px solid #ef4444;box-shadow:0 20px 50px rgba(0,0,0,.5)";
var h=document.createElement("b");h.textContent=t;h.style.cssText="display:block;font-size:16px;color:#fca5a5;margin-bottom:6px";var p=document.createElement("pre");p.textContent=d;p.style.cssText="white-space:pre-wrap;margin:0 0 10px;font:13px ui-monospace,Consolas,monospace;color:#fde2e2";
var x=document.createElement("button");x.textContent="Cerrar";x.style.cssText="padding:6px 14px;border:0;border-radius:8px;background:#ef4444;color:#fff;font-weight:700;cursor:pointer";x.onclick=function(){c.remove()};b.appendChild(h);b.appendChild(p);b.appendChild(x);c.appendChild(b);(document.body||document.documentElement).appendChild(c)};document.body?f():addEventListener("DOMContentLoaded",f)}
function red(m){return /Failed to fetch dynamically imported module|error loading dynamically imported module|Importing a module script failed|esm\\.sh/i.test(m)}
addEventListener("error",function(e){var t=e.target;if(t&&t.tagName==="SCRIPT"&&t.type==="module"){mostrar("No se pudo cargar "+(t.getAttribute("src")||"un script"),"Revisa que el archivo exista y que no tenga errores. Si usa librerías (react, vue…), se descargan de internet: revisa tu conexión.");return}var m=String(e.message||"");if(red(m))mostrar("No se pudo descargar una librería","Las librerías como react, vue o svelte se descargan de internet (esm.sh) al abrir la página.\\nRevisa tu conexión: algunas redes de colegio o empresa bloquean esm.sh.\\n\\n"+m)},true);
addEventListener("unhandledrejection",function(e){var m=String(e.reason&&(e.reason.message||e.reason)||"");if(red(m))mostrar("No se pudo descargar una librería","Las librerías como react, vue o svelte se descargan de internet (esm.sh) al abrir la página.\\nRevisa tu conexión: algunas redes de colegio o empresa bloquean esm.sh.\\n\\n"+m)});})();`;

const PUENTE_IMAGENES = `(function(M,D){if(!Object.keys(M).length)return;var R=function(ref){if(!ref||/^([a-z][a-z0-9+.-]*:|\\/\\/|#)/i.test(ref))return null;var p=(D?D.split("/"):[]),s=ref.split(/[?#]/)[0].split("/");if(ref.charAt(0)==="/")p=[];for(var i=0;i<s.length;i++){if(!s[i]||s[i]===".")continue;if(s[i]==="..")p.pop();else p.push(s[i])}return M[p.join("/")]||null};
var F=function(el){if(!el||el.nodeType!==1)return;["src","poster"].forEach(function(a){var v=el.getAttribute&&el.getAttribute(a),u=R(v);if(u&&v!==u)el.setAttribute(a,u)});if(el.style&&el.style.backgroundImage){el.style.backgroundImage=el.style.backgroundImage.replace(/url\\(["']?([^"')]+)["']?\\)/g,function(t,r){var u=R(r);return u?"url("+u+")":t})}};
new MutationObserver(function(ms){ms.forEach(function(m){if(m.type==="attributes")F(m.target);else m.addedNodes.forEach(function(n){F(n);if(n.querySelectorAll)n.querySelectorAll("[src],[poster],[style]").forEach(F)})})}).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:["src","poster","style"]});
try{var d=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,"src");Object.defineProperty(HTMLImageElement.prototype,"src",{configurable:true,get:d.get,set:function(v){d.set.call(this,R(String(v))||v)}})}catch(e){}})`;

export function construirVistaPrevia(py, rutaHtml, { imagenes = new Map(), modulos = null, proxy = [], virtual = null } = {}) {
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
  html = html.replace(/<script\b[^>]*\bsrc\s*=\s*["']https:\/\/accounts\.google\.com\/gsi\/client[^"']*["'][^>]*>\s*<\/script>/gi, "");
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
  if (virtual) {
    // Dirección virtual: location/history/localStorage/cookies como en un servidor de desarrollo (virtual.js).
    html = html.replace(/<script\b(?![^>]*\btype\s*=\s*["']?(?:module|importmap|application\/json|text\/template))([^>]*)>([\s\S]*?)<\/script>/gi, (todo, attrs, cuerpo) => `<script${attrs}>${reescribirUbicacion(cuerpo)}</script>`);
    html = reescribirAtributos(html);
  }
  const inicio = virtual ? scriptVirtual(virtual.url, virtual.almacen, { hijo: virtual.hijo }) : "";
  const puente = `<script>${inicio}${PUENTE}${modulos ? CAPA_ERRORES_MODULOS : ""}${Object.keys(mapaJs).length ? `${PUENTE_IMAGENES}(${JSON.stringify(mapaJs).replace(/</g, "\\u003c")},${JSON.stringify(dir)});` : ""}${puenteDeProyecto(proxy)}</script>${mapaImport}`;
  return /<head[^>]*>/i.test(html) ? html.replace(/<head[^>]*>/i, (m) => `${m}${puente}`) : puente + html;
}

// ================================================================ servidores (FastAPI, Flask…) ====
// Dentro de la vista previa, fetch(), los enlaces y los formularios hacia http://127.0.0.1:<puerto> se mandan a
// Trabajo, que se los pasa a la app de Python (servidorpy.js) y devuelve la respuesta. Así funcionan /docs de FastAPI,
// los «Try it out», las plantillas de Flask y el JavaScript de tu frontend que llama a tu API.
const PUENTE_HTTP = `(function(O,B){var n=0,E={};
addEventListener("message",function(e){var m=e.data;if(!m||m.cc!=="http-r"||!E[m.id])return;var p=E[m.id];delete E[m.id];if(m.error){p[1](new TypeError(m.error));return}var sin=m.status===204||m.status===304||m.status<200;p[0](new Response(sin?null:m.body,{status:m.status,statusText:m.statusText||"",headers:m.headers}))});
function L(u){try{var x=new URL(u,B);return x.origin===O?x:null}catch(e){return null}}
function pedir(r,x){return r.arrayBuffer().then(function(b){return new Promise(function(ok,no){var id=++n;E[id]=[ok,no];var hs=[];r.headers.forEach(function(v,k){hs.push([k,v])});parent.postMessage({cc:"http",id:id,method:r.method,url:x.href,headers:hs,body:b},"*",[b])})})}
var F=window.fetch;window.fetch=function(i,init){var u=(i&&i.url)||String(i);var x=L(u);if(!x)return F.apply(this,arguments);var r=new Request(typeof i==="string"||i instanceof URL?x.href:i,init);return pedir(r,x)};
var X=window.XMLHttpRequest;window.XMLHttpRequest=function(){var real=new X(),s=this,loc=null,h=new Headers(),m="GET",ev={};var props=["readyState","status","statusText","response","responseText","responseURL","responseType","timeout","withCredentials","upload"];
props.forEach(function(p){Object.defineProperty(s,p,{get:function(){return loc?loc[p]:real[p]},set:function(v){if(loc)loc[p]=v;else real[p]=v}})});
["onload","onerror","onreadystatechange","onloadend","onprogress","onabort","ontimeout"].forEach(function(p){Object.defineProperty(s,p,{get:function(){return ev[p]},set:function(f){ev[p]=f;real[p]=f}})});
s.open=function(mt,u){m=mt;var x=L(u);if(x){loc={readyState:1,status:0,statusText:"",response:"",responseText:"",responseURL:x.href,responseType:"",x:x}}else real.open.apply(real,arguments)};
s.setRequestHeader=function(k,v){if(loc)h.append(k,v);else real.setRequestHeader(k,v)};
s.getResponseHeader=function(k){return loc?(loc.h&&loc.h.get(k)):real.getResponseHeader(k)};s.getAllResponseHeaders=function(){if(!loc)return real.getAllResponseHeaders();var t="";loc.h&&loc.h.forEach(function(v,k){t+=k+": "+v+"\\r\\n"});return t};
s.addEventListener=function(t,f){if(!loc)return real.addEventListener(t,f);ev["on"+t]=f};s.abort=function(){if(!loc)real.abort()};s.overrideMimeType=function(){};
s.send=function(b){if(!loc)return real.send(b);var r=new Request(loc.x.href,{method:m,headers:h,body:m==="GET"||m==="HEAD"?undefined:b});pedir(r,loc.x).then(function(res){loc.status=res.status;loc.statusText=res.statusText;loc.h=res.headers;return loc.responseType==="arraybuffer"?res.arrayBuffer():loc.responseType==="blob"?res.blob():res.text()}).then(function(d){loc.response=d;if(typeof d==="string"){loc.responseText=d;if(loc.responseType==="json"){try{loc.response=JSON.parse(d)}catch(e){loc.response=null}}}loc.readyState=4;ev.onreadystatechange&&ev.onreadystatechange.call(s);ev.onload&&ev.onload.call(s,{target:s});ev.onloadend&&ev.onloadend.call(s,{target:s})},function(){loc.readyState=4;ev.onerror&&ev.onerror.call(s,{target:s})})}};
document.addEventListener("click",function(e){if(window.__ccVirtual)return;var a=e.target.closest&&e.target.closest("a[href]");if(!a)return;var h=a.getAttribute("href");if(!h||h.charAt(0)==="#"||/^(mailto:|tel:|javascript:)/i.test(h))return;var x=L(h);if(!x)return;e.preventDefault();e.stopImmediatePropagation();parent.postMessage({cc:"ir",url:x.href},"*")},true);
document.addEventListener("submit",function(e){var f=e.target;var x=L(f.getAttribute("action")||B);if(!x)return;e.preventDefault();var m=(f.getAttribute("method")||"GET").toUpperCase();var d=new FormData(f);if(e.submitter&&e.submitter.name)d.append(e.submitter.name,e.submitter.value);
if(m==="GET"){x.search=new URLSearchParams(d).toString();parent.postMessage({cc:"ir",url:x.href},"*");return}var multi=(f.getAttribute("enctype")||"").indexOf("multipart")>=0;var r=new Request(x.href,{method:m,body:multi?d:new URLSearchParams(d)});r.arrayBuffer().then(function(b){var hs=[];r.headers.forEach(function(v,k){hs.push([k,v])});parent.postMessage({cc:"form",method:m,url:x.href,headers:hs,body:b},"*",[b])})},true);
})(%O%,%B%);`;

const L_PROYECTO = 'function L(u){var x;try{x=new URL(u,window.__ccLoc?window.__ccLoc.href:B)}catch(e){return null}var R=%R%;if(x.origin===O){for(var i=0;i<R.length;i++){var r=R[i];if(x.pathname===r.p||x.pathname.indexOf(r.p.replace(/\\/$/,"")+"/")===0||x.pathname.indexOf(r.p)===0){var p=x.pathname;if(r.q){try{p=p.replace(new RegExp(r.q),r.s||"")}catch(e){}}var d=r.d.replace(/^ws/,"http").replace(/\\/$/,"");try{return new URL(d+(p.charAt(0)==="/"?p:"/"+p)+x.search)}catch(e){return null}}}return null}if(/^(localhost|127\\.0\\.0\\.1|0\\.0\\.0\\.0|\\[::1\\])$/.test(x.hostname)&&x.port){return new URL("http://127.0.0.1:"+x.port+x.pathname+x.search)}return null}';

/**
 * Puente de red para las páginas del proyecto (la vista previa de «npm run dev» o de un index.html):
 *  · lo que tu vite.config.js manda por server.proxy (fetch("/api/…") → http://127.0.0.1:8000/api/…)
 *  · y cualquier fetch/XHR a http://localhost:<puerto> o http://127.0.0.1:<puerto>
 * van al servidor de Python que corre en Trabajo (FastAPI, Flask…), como hace Vite con tu backend en el PC.
 */
// «Iniciar con Google» (Google Identity Services) en la vista previa: el botón real de Google no funciona dentro de
// la vista (no tiene un origen propio que registrar en Google Cloud). Se cambia por uno que entra con tu cuenta de
// CódigoCamp: tu callback recibe un credential que tu backend en Trabajo acepta como de Google (red_py.py).
export const PUENTE_GOOGLE = "(function(){var G={cid:null,cb:null};\nfunction token(ok,no){var id=Math.random().toString(36).slice(2);function f(e){var m=e.data;if(!m||m.cc!==\"google-token-r\"||m.id!==id)return;removeEventListener(\"message\",f);if(m.error)no(m.error);else ok(m)}addEventListener(\"message\",f);parent.postMessage({cc:\"google-token\",id:id,aud:G.cid||\"\"},\"*\")}\nfunction entrar(){token(function(m){if(G.cb)G.cb({credential:m.credential,select_by:\"btn\",clientId:G.cid})},function(e){console.error(\"Iniciar con Google (Trabajo): \"+e)})}\nfunction boton(el,o){if(!el)return;o=o||{};el.innerHTML=\"\";var b=document.createElement(\"button\");b.type=\"button\";b.title=\"En Trabajo, Google entra con tu cuenta de C\u00f3digoCamp (la de tu PC usa Google de verdad)\";\nb.innerHTML='<span style=\"display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:#fff;color:#4285f4;font:700 14px Arial\">G</span><span>'+(o.text===\"signup_with\"?\"Registrarse\":o.text===\"signin_with\"?\"Iniciar sesi\u00f3n\":\"Continuar\")+' con Google</span>';\nb.style.cssText=\"display:inline-flex;align-items:center;gap:10px;min-width:\"+(o.width?o.width+\"px\":\"220px\")+\";justify-content:center;padding:9px 14px;border:1px solid #dadce0;border-radius:\"+(o.shape===\"pill\"?\"999px\":\"6px\")+\";background:\"+(o.theme===\"filled_black\"?\"#202124;color:#fff\":o.theme===\"filled_blue\"?\"#1a73e8;color:#fff\":\"#fff;color:#3c4043\")+\";font:500 14px Arial,sans-serif;cursor:pointer\";\nb.onclick=entrar;el.appendChild(b)}\nvar id={initialize:function(c){c=c||{};G.cid=c.client_id||G.cid;G.cb=c.callback||G.cb},renderButton:boton,prompt:function(n){if(n)try{n({isNotDisplayed:function(){return true},isSkippedMoment:function(){return true},getNotDisplayedReason:function(){return\"trabajo\"}})}catch(e){}},cancel:function(){},disableAutoSelect:function(){},storeCredential:function(){},revoke:function(h,d){if(d)d({successful:true})}};\nwindow.google=window.google||{};window.google.accounts=window.google.accounts||{};window.google.accounts.id=id;\nvar GSI=/^https:\\/\\/accounts\\.google\\.com\\/gsi\\/client/;var D=Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype,\"src\");\nObject.defineProperty(HTMLScriptElement.prototype,\"src\",{configurable:true,get:D.get,set:function(v){return D.set.call(this,GSI.test(String(v))?\"data:text/javascript,\":v)}});\nvar SA=Element.prototype.setAttribute;Element.prototype.setAttribute=function(n,v){if(this instanceof HTMLScriptElement&&String(n).toLowerCase()===\"src\"&&GSI.test(String(v)))v=\"data:text/javascript,\";return SA.call(this,n,v)};\naddEventListener(\"DOMContentLoaded\",function(){var c=document.getElementById(\"g_id_onload\");if(c){G.cid=c.getAttribute(\"data-client_id\")||G.cid;var n=c.getAttribute(\"data-callback\");if(n)G.cb=function(r){if(typeof window[n]===\"function\")window[n](r)}}var bs=document.querySelectorAll(\".g_id_signin\");for(var i=0;i<bs.length;i++)boton(bs[i],{text:bs[i].getAttribute(\"data-text\"),shape:bs[i].getAttribute(\"data-shape\"),theme:bs[i].getAttribute(\"data-theme\")});if(typeof window.onGoogleLibraryLoad===\"function\")window.onGoogleLibraryLoad()});\n})();";

export function puenteDeProyecto(reglas = []) {
  const codigo = PUENTE_GOOGLE + PUENTE_HTTP.replace("function L(u){try{var x=new URL(u,B);return x.origin===O?x:null}catch(e){return null}}", L_PROYECTO.replace("%R%", JSON.stringify(reglas).replace(/</g, "\\u003c")))
    .replace("%O%", JSON.stringify("http://localhost:5173")).replace("%B%", JSON.stringify("http://localhost:5173/"));
  return codigo;
}

const escHtml = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/** Página de la vista previa para una respuesta del servidor (HTML con el puente; JSON o texto, legibles). */
export function vistaDeRespuesta({ url, status, headers, body }) {
  const destino = new URL(url);
  const tipo = (headers.find(([k]) => k.toLowerCase() === "content-type")?.[1] || "").toLowerCase();
  const texto = () => new TextDecoder().decode(body);
  const puente = `<script>${PUENTE}${PUENTE_HTTP.replace("%O%", JSON.stringify(destino.origin)).replace("%B%", JSON.stringify(destino.href))}</script>`;
  if (tipo.includes("html")) {
    // /docs y /redoc de FastAPI piden «/openapi.json»: se vuelve absoluta para que llegue al servidor.
    let html = texto().replace(/(["'])\/openapi\.json\1/g, `$1${destino.origin}/openapi.json$1`).replace(/(["'])\/docs\/oauth2-redirect\1/g, `$1${destino.origin}/docs/oauth2-redirect$1`);
    const cabeza = `<base href="${escHtml(destino.href)}">${puente}`;
    return /<head[^>]*>/i.test(html) ? html.replace(/<head[^>]*>/i, (m) => m + cabeza) : cabeza + html;
  }
  const estilo = `<style>body{margin:0;font:13px/1.55 ui-monospace,Consolas,monospace;background:#fff;color:#1f2328}header{position:sticky;top:0;padding:8px 14px;background:#f6f8fa;border-bottom:1px solid #d0d7de;font:600 12px system-ui;color:#57606a}pre{margin:0;padding:14px;white-space:pre-wrap;word-break:break-word}.k{color:#0550ae}.s{color:#0a3069}.n{color:#953800}.b{color:#cf222e}@media(prefers-color-scheme:dark){body{background:#0d1117;color:#e6edf3}header{background:#161b22;border-color:#30363d;color:#8b949e}.k{color:#79c0ff}.s{color:#a5d6ff}.n{color:#ffa657}.b{color:#ff7b72}}</style>`;
  const cab = `<header>${status} · ${escHtml(tipo || "sin tipo")} · ${escHtml(destino.pathname + destino.search)}</header>`;
  if (tipo.includes("json")) {
    let bonito;
    try { bonito = JSON.stringify(JSON.parse(texto()), null, 2); } catch { bonito = texto(); }
    const coloreado = escHtml(bonito).replace(/("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)/gi,
      (m, cadena, dos, lit, num) => cadena ? `<span class="${dos ? "k" : "s"}">${cadena}</span>${dos || ""}` : lit ? `<span class="b">${lit}</span>` : `<span class="n">${num}</span>`);
    return `<!doctype html><meta charset="utf-8">${estilo}${puente}${cab}<pre>${coloreado}</pre>`;
  }
  if (tipo.startsWith("image/")) {
    let s = ""; for (let i = 0; i < body.length; i += 0x8000) s += String.fromCharCode(...body.subarray(i, i + 0x8000));
    return `<!doctype html>${estilo}${cab}<p style="padding:14px"><img alt="" style="max-width:100%" src="data:${escHtml(tipo)};base64,${btoa(s)}"></p>`;
  }
  return `<!doctype html><meta charset="utf-8">${estilo}${puente}${cab}<pre>${escHtml(texto() || "(respuesta vacía)")}</pre>`;
}


/** Página HTML que vino del backend (por el proxy de Vite) mostrada con la dirección virtual. */
export function paginaRemotaConPuente(html, { url, almacen, proxy = [], hijo = false }) {
  const cabeza = `<script>${scriptVirtual(url, almacen, { hijo })}${PUENTE}${puenteDeProyecto(proxy)}</script>`;
  return /<head[^>]*>/i.test(html) ? html.replace(/<head[^>]*>/i, (m) => m + cabeza) : cabeza + html;
}
