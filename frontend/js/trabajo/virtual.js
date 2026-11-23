// La vista previa como un servidor de desarrollo de verdad (lo que hace Vite en http://localhost:5173 en tu PC).
//
// La vista previa es un <iframe sandbox> sin origen propio (por seguridad: tu código no puede tocar tu cuenta de
// CódigoCamp). Ahí no existen localStorage, cookies ni una dirección real, y `location.href = "/dashboard"`
// sacaba la página a una dirección que no existe: tras iniciar sesión, la app «se quedaba colgada».
// Aquí se le da a la página una DIRECCIÓN VIRTUAL (http://localhost:5173/…) con:
//   · location virtual: location.href/pathname/assign/replace, history.pushState/back, window.top.location
//     (el código de tu proyecto se reescribe para usar __ccLoc / __ccTop en lugar de location)
//   · localStorage, sessionStorage y document.cookie que se conservan entre páginas (por proyecto)
//   · <iframe src="/legacy/…"> y navegación a páginas del backend (proxy de vite.config.js) o del proyecto
// Trabajo (trabajo.js) decide qué mostrar en cada dirección con resolverDestino(), igual que Vite.
import * as FS from "./fs.js";

export const ORIGEN_VIRTUAL = "http://localhost:5173";

// ------------------------------------------------------------------ reescribir `location` en tu código --
/** Aplica `fn` solo al código, no a textos entre comillas, plantillas ni comentarios. */
function fueraDeTextos(codigo, fn) {
  let salida = "", trozo = "", i = 0;
  const n = codigo.length;
  const vaciar = () => { if (trozo) { salida += fn(trozo); trozo = ""; } };
  while (i < n) {
    const c = codigo[i], d = codigo[i + 1];
    if (c === "/" && d === "/") { vaciar(); const f = codigo.indexOf("\n", i); const fin = f < 0 ? n : f; salida += codigo.slice(i, fin); i = fin; continue; }
    if (c === "/" && d === "*") { vaciar(); const f = codigo.indexOf("*/", i + 2); const fin = f < 0 ? n : f + 2; salida += codigo.slice(i, fin); i = fin; continue; }
    if (c === "'" || c === '"' || c === "`") {
      vaciar();
      let j = i + 1;
      while (j < n && codigo[j] !== c) { if (codigo[j] === "\\") j += 1; if (c !== "`" && codigo[j] === "\n") break; j += 1; }
      salida += codigo.slice(i, j + 1); i = j + 1; continue;
    }
    trozo += c; i += 1;
  }
  vaciar();
  return salida;
}

const ARRIBA = /\b(?:window\.|self\.|globalThis\.)?(?:top|parent)\.location\b/g;
const PROPIA = /\b(?:window|self|globalThis|document)\.location\b/g;
// `location` suelto (no `obj.location`, no `useLocation`, no la clave de un objeto `{ location: … }`)
const SUELTA = /(?<![\w$.])location(?![\w$])(?!\s*:(?!:))/g;

/** Cambia location / window.location / top.location por la dirección virtual (__ccLoc / __ccTop). */
export function reescribirUbicacion(codigo) {
  if (!/location/.test(codigo)) return codigo;
  // { location } (desestructurar u objeto abreviado) es una variable o propiedad propia: no se toca.
  const suelta = (t) => t.replace(SUELTA, (m, i) => (/[{,]\s*$/.test(t.slice(Math.max(0, i - 40), i)) && /^\s*[,}=]/.test(t.slice(i + 8, i + 20)) ? m : "__ccLoc"));
  return fueraDeTextos(codigo, (t) => suelta(t.replace(ARRIBA, "__ccTop").replace(PROPIA, "__ccLoc"))
    // window.location = "/x" (asignar la dirección entera) navega: se vuelve __ccLoc.href = "/x"
    .replace(/(?<!\b(?:let|const|var)\s+)\b(__ccLoc|__ccTop)(\s*)=(?![=>])/g, "$1.href$2="));
}

/** Igual para atributos onclick="location.href='x.html'" del HTML. */
export function reescribirAtributos(html) {
  return html.replace(/(\son[a-z]+\s*=\s*)(["'])([\s\S]*?)\2/gi, (todo, pre, q, codigo) => (/location/.test(codigo) ? pre + q + reescribirUbicacion(codigo) + q : todo));
}

// --------------------------------------------------------------------------- dirección de una página --
/** Dirección virtual de un archivo del proyecto: «frontend/index.html» con raíz «frontend» → http://localhost:5173/ */
export function urlDeArchivo(raiz, ruta) {
  let rel = raiz && ruta.startsWith(raiz + "/") ? ruta.slice(raiz.length + 1) : raiz ? ruta : ruta;
  if (rel.startsWith("public/")) rel = rel.slice(7);
  if (rel === "index.html") rel = "";
  else if (rel.endsWith("/index.html")) rel = rel.slice(0, -10);
  return `${ORIGEN_VIRTUAL}/${rel.split("/").map(encodeURIComponent).join("/")}`;
}

/**
 * Qué hay en una dirección virtual, como lo decide Vite:
 *   1. el proxy de vite.config.js  → { tipo: "remoto", url: "http://127.0.0.1:8000/legacy/…" }
 *   2. un archivo del proyecto (o de public/) → { tipo: "archivo", ruta }   (carpeta/ → carpeta/index.html; /x → x.html)
 *   3. una app de una sola página (Vite): su index.html → { tipo: "archivo", ruta, spa: true }
 *   4. nada → { tipo: "nada" }
 */
export function resolverDestino(py, raiz, url, proxy = []) {
  const u = new URL(url, ORIGEN_VIRTUAL);
  if (u.origin !== ORIGEN_VIRTUAL) {
    if (/^(localhost|127\.0\.0\.1|0\.0\.0\.0)$/.test(u.hostname) && u.port) return { tipo: "remoto", url: `http://127.0.0.1:${u.port}${u.pathname}${u.search}` };
    return { tipo: "externo", url: u.href };
  }
  let ruta = u.pathname;
  try { ruta = decodeURIComponent(ruta); } catch { /* tal cual */ }
  for (const r of proxy) {
    if (ruta === r.p || ruta.startsWith(r.p.replace(/\/$/, "") + "/") || ruta.startsWith(r.p)) {
      let p = u.pathname;
      if (r.q) { try { p = p.replace(new RegExp(r.q), r.s || ""); } catch { /* regla rara */ } }
      return { tipo: "remoto", url: `${r.d.replace(/^ws/, "http").replace(/\/$/, "")}${p.startsWith("/") ? p : "/" + p}${u.search}` };
    }
  }
  const rel = ruta.replace(/^\/+/, "");
  const bases = [raiz, FS.unir(raiz, "public")];
  const candidatos = [];
  for (const b of bases) {
    const r = FS.unir(b, rel);
    if (!rel || rel.endsWith("/")) candidatos.push(FS.unir(r.replace(/\/+$/, ""), "index.html"));   // carpeta/ → carpeta/index.html
    else { candidatos.push(r); if (!/\.[a-z0-9]+$/i.test(rel)) candidatos.push(`${r}.html`, FS.unir(r, "index.html")); }
  }
  const archivo = candidatos.find((c) => c && FS.tieneArchivo(py, c));
  if (archivo) return { tipo: "archivo", ruta: archivo };
  const indice = FS.unir(raiz, "index.html");
  const esVite = ["vite.config.js", "vite.config.ts", "vite.config.mjs", "vite.config.mts"].some((n) => FS.tieneArchivo(py, FS.unir(raiz, n))) || /"vite"/.test(py.files[FS.unir(raiz, "package.json")] || "");
  if (esVite && FS.tieneArchivo(py, indice) && !/\.[a-z0-9]+$/i.test(rel)) return { tipo: "archivo", ruta: indice, spa: true };
  return { tipo: "nada", ruta };
}

// ------------------------------------------------------------------------ el script de la página --
// Va primero en <head>. V = dirección virtual de esta página; A = { local, sesion, cookies } guardados del proyecto.
const SCRIPT = String.raw`(function(V,A){if(window.__ccLoc)return;window.__ccVirtual=true;
var U=new URL(V),O=U.origin,PILA=[{url:U.href,estado:null}],pos=0,ES_HIJO=!!A.hijo;
function P(m){try{parent.postMessage(m,"*")}catch(e){}}
function abs(u){return new URL(String(u),U.href)}
var ALM={},PEND={};function vaciar(){for(var k in PEND){clearTimeout(PEND[k]);delete PEND[k];P({cc:"ls",tipo:k,datos:ALM[k]})}}
function hacer(d,tipo){d=d||{};ALM[tipo]=d;function g(){clearTimeout(PEND[tipo]);PEND[tipo]=setTimeout(function(){delete PEND[tipo];P({cc:"ls",tipo:tipo,datos:d})},30)}
var s={getItem:function(k){k=String(k);return Object.prototype.hasOwnProperty.call(d,k)?d[k]:null},setItem:function(k,v){d[String(k)]=String(v);g()},removeItem:function(k){delete d[String(k)];g()},clear:function(){for(var k in d)delete d[k];g()},key:function(i){return Object.keys(d)[i]||null}};
Object.defineProperty(s,"length",{get:function(){return Object.keys(d).length}});
return new Proxy(s,{get:function(o,k){if(k in o)return o[k];return typeof k==="string"&&Object.prototype.hasOwnProperty.call(d,k)?d[k]:undefined},set:function(o,k,v){if(k in o)o[k]=v;else{d[String(k)]=String(v);g()}return true},deleteProperty:function(o,k){delete d[k];g();return true},has:function(o,k){return k in o||Object.prototype.hasOwnProperty.call(d,k)},ownKeys:function(){return Object.keys(d)},getOwnPropertyDescriptor:function(o,k){if(Object.prototype.hasOwnProperty.call(d,k))return{value:d[k],enumerable:true,configurable:true,writable:true}}})}
try{Object.defineProperty(window,"localStorage",{value:hacer(A.local,"local"),configurable:true})}catch(e){}
try{Object.defineProperty(window,"sessionStorage",{value:hacer(A.sesion,"sesion"),configurable:true})}catch(e){}
var J=A.cookies||{};ALM.cookies=J;try{Object.defineProperty(document,"cookie",{configurable:true,get:function(){return Object.keys(J).map(function(k){return k+"="+J[k]}).join("; ")},set:function(v){var p=String(v).split(";"),kv=p[0],i=kv.indexOf("=");if(i<0)return;var k=kv.slice(0,i).trim(),val=kv.slice(i+1).trim(),borrar=false;
for(var j=1;j<p.length;j++){var a=p[j].trim().toLowerCase();if(a.indexOf("max-age=")===0&&Number(a.slice(8))<=0)borrar=true;if(a.indexOf("expires=")===0){var f=Date.parse(p[j].trim().slice(8));if(f&&f<Date.now())borrar=true}}
if(borrar)delete J[k];else J[k]=val;P({cc:"ls",tipo:"cookies",datos:J})}})}catch(e){}
function avisarUrl(){if(!ES_HIJO)P({cc:"vurl",url:U.href})}
function ir(u,reemplazar,arriba){var x;try{x=abs(u)}catch(e){return}
if(x.origin!==O&&!/^(localhost|127\.0\.0\.1)$/.test(x.hostname)){window.open(x.href,"_blank","noopener");return}
if(x.origin===O&&x.pathname===U.pathname&&x.search===U.search&&x.hash&&x.hash!==U.hash&&!arriba){var ant=U.href;U=x;PILA[pos].url=U.href;try{dispatchEvent(new HashChangeEvent("hashchange",{oldURL:ant,newURL:U.href}))}catch(e){}avisarUrl();return}
vaciar();P({cc:"vnav",url:x.href,reemplazar:!!reemplazar,arriba:!!arriba})}
function hacerLoc(arriba){var L={assign:function(u){ir(u,false,arriba)},replace:function(u){ir(u,true,arriba)},reload:function(){vaciar();P({cc:"vnav",url:U.href,reemplazar:true,arriba:arriba})},toString:function(){return U.href},valueOf:function(){return this}};
["href","pathname","search","hash","host","hostname","port","origin","protocol"].forEach(function(k){Object.defineProperty(L,k,{enumerable:true,get:function(){return U[k]},set:function(v){if(k==="origin")return;if(k==="href"){ir(v,false,arriba);return}var x=new URL(U.href);x[k]=v;ir(x.href,false,arriba)}})});
Object.defineProperty(L,"ancestorOrigins",{get:function(){return[]}});return L}
window.__ccLoc=hacerLoc(false);window.__ccTop=ES_HIJO?hacerLoc(true):window.__ccLoc;
var H=History.prototype;function cambiar(s,u,r){var x=u==null||u===""?U:abs(u);if(x.origin!==O)throw new DOMException("Failed to execute 'pushState' on 'History': a history state object with URL '"+x.href+"' cannot be created in a document with origin '"+O+"'.","SecurityError");U=x;if(r)PILA[pos]={url:U.href,estado:s};else{PILA=PILA.slice(0,pos+1);PILA.push({url:U.href,estado:s});pos++}avisarUrl()}
H.pushState=function(s,t,u){cambiar(s,u,false)};H.replaceState=function(s,t,u){cambiar(s,u,true)};
H.go=function(n){n=Number(n)||0;if(!n){window.__ccLoc.reload();return}var p=pos+n;if(p<0||p>=PILA.length)return;pos=p;U=new URL(PILA[pos].url);var e=PILA[pos].estado;setTimeout(function(){try{dispatchEvent(new PopStateEvent("popstate",{state:e}))}catch(x){}avisarUrl()},0)};
H.back=function(){this.go(-1)};H.forward=function(){this.go(1)};
try{Object.defineProperty(H,"state",{configurable:true,get:function(){return PILA[pos].estado}});Object.defineProperty(H,"length",{configurable:true,get:function(){return PILA.length}})}catch(e){}
addEventListener("click",function(e){if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;var a=e.target.closest&&e.target.closest("a[href]");if(!a||a.hasAttribute("download"))return;var h=a.getAttribute("href");if(!h||h.charAt(0)==="#"&&h.length<2||/^(mailto:|tel:|javascript:)/i.test(h))return;e.preventDefault();var t=(a.getAttribute("target")||"").toLowerCase();ir(h,false,t==="_top"||t==="_parent")});
if(window.navigation&&navigation.addEventListener)navigation.addEventListener("navigate",function(e){if(!e.cancelable||e.hashChange||e.downloadRequest||e.formData)return;try{var d=new URL(e.destination.url);if(d.protocol==="about:"||d.protocol==="data:"||d.protocol==="blob:"||d.protocol==="javascript:")return;e.preventDefault();ir(d.origin===location.origin?O+d.pathname+d.search+d.hash:d.href)}catch(x){}});
function pedirPagina(u,cb){var id="p"+Math.random().toString(36).slice(2);function f(e){var m=e.data;if(!m||m.cc!=="vpagina-r"||m.id!==id)return;removeEventListener("message",f);cb(m)}addEventListener("message",f);P({cc:"vpagina",id:id,url:u})}
function marco(el,u){if(u==null||u===""||/^(about:|data:|blob:|javascript:)/i.test(String(u)))return false;var x;try{x=abs(u)}catch(e){return false}if(x.origin!==O&&!/^(localhost|127\.0\.0\.1)$/.test(x.hostname))return false;
el.setAttribute("data-cc-src",x.href);pedirPagina(x.href,function(m){if(m.html!=null)el.srcdoc=m.html;else el.srcdoc="<p style='font:13px system-ui;color:#b91c1c;padding:12px'>"+String(m.error||"No se pudo cargar "+x.href).replace(/</g,"&lt;")+"</p>"});return true}
var DI=Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype,"src");
Object.defineProperty(HTMLIFrameElement.prototype,"src",{configurable:true,get:function(){return this.getAttribute("data-cc-src")||DI.get.call(this)},set:function(v){if(!marco(this,v))DI.set.call(this,v)}});
var SA=Element.prototype.setAttribute;Element.prototype.setAttribute=function(n,v){if(this instanceof HTMLIFrameElement&&String(n).toLowerCase()==="src"&&marco(this,v))return;return SA.call(this,n,v)};
function revisar(raiz){var fs=raiz.querySelectorAll?raiz.querySelectorAll("iframe[src]:not([data-cc-src])"):[];if(raiz.tagName==="IFRAME"&&raiz.getAttribute("src")&&!raiz.getAttribute("data-cc-src"))fs=[raiz];for(var i=0;i<fs.length;i++)marco(fs[i],fs[i].getAttribute("src"))}
new MutationObserver(function(ms){ms.forEach(function(m){m.addedNodes.forEach(function(n){if(n.nodeType===1)revisar(n)})})}).observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener("DOMContentLoaded",function(){revisar(document)});
var R={},rn=0;addEventListener("message",function(e){var m=e.data;if(!m||typeof m.cc!=="string")return;
if(e.source===parent){if(R[m.id]){var d=R[m.id];delete R[m.id];var c=Object.assign({},m);c.id=d.id;try{d.w.postMessage(c,"*")}catch(x){}}return}
var fs=document.getElementsByTagName("iframe"),el=null;for(var i=0;i<fs.length;i++)if(fs[i].contentWindow===e.source){el=fs[i];break}if(!el)return;
if(m.cc==="vnav"){if(m.arriba)ir(m.url,m.reemplazar,ES_HIJO);else marco(el,m.url);return}if(m.cc==="vurl")return;
if(m.cc==="ls"&&ALM[m.tipo]){var dd=ALM[m.tipo],nn=m.datos||{};if(PEND[m.tipo]){clearTimeout(PEND[m.tipo]);delete PEND[m.tipo]}for(var q in dd)if(!(q in nn))delete dd[q];for(var q2 in nn)dd[q2]=nn[q2]}
if(m.id!==undefined&&/^(http|google-token|vpagina)$/.test(m.cc)){var k="r"+(++rn)+Math.random().toString(36).slice(2,6);R[k]={w:e.source,id:m.id};var c2=Object.assign({},m);c2.id=k;P(c2);return}
P(m)});
avisarUrl();
})(%V%,%A%);`;

/** Script de la dirección virtual para una página. `almacen` = { local, sesion, cookies }; `hijo` = página dentro de un iframe. */
export function scriptVirtual(url, almacen = {}, { hijo = false } = {}) {
  const datos = { local: almacen.local || {}, sesion: almacen.sesion || {}, cookies: almacen.cookies || {}, hijo };
  return SCRIPT.replace("%V%", JSON.stringify(url)).replace("%A%", JSON.stringify(datos).replace(/</g, "\\u003c"));
}

// ------------------------------------------------- páginas que vienen del backend (proxy de Vite) --
const escAttr = (t) => String(t).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
const aB64 = (bytes) => { let s = ""; const u = new Uint8Array(bytes); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode(...u.subarray(i, i + 0x8000)); return btoa(s); };

/**
 * HTML que mandó tu backend (por ejemplo /legacy/pages/dashboard.html): sus <script src>, <link rel=stylesheet> e <img>
 * de la misma app se traen (por el proxy o del proyecto) y se meten en la página, porque la vista previa no tiene un
 * servidor al que pedirlos. `obtener(urlVirtual)` → { tipo, bytes } | null.
 */
export async function incrustarRecursos(html, urlPagina, obtener) {
  const propia = (ref) => {
    if (!ref || /^(data:|blob:|javascript:|#)/i.test(ref)) return null;
    try { const u = new URL(ref, urlPagina); return u.origin === ORIGEN_VIRTUAL ? u.href : null; } catch { return null; }
  };
  const texto = (b) => new TextDecoder().decode(b);
  const reemplazos = [];
  for (const m of html.matchAll(/<script\b([^>]*)\bsrc\s*=\s*["']([^"']+)["']([^>]*)>\s*<\/script>/gi)) {
    const url = propia(m[2]);
    if (!url) continue;
    reemplazos.push(obtener(url).then((r) => [m[0], r ? `<script${m[1].replace(/\bdefer\b|\basync\b/gi, "")}${m[3]} data-archivo="${escAttr(url)}">\n${reescribirUbicacion(texto(r.bytes)).replace(/<\/script/gi, "<\\/script")}\n</script>` : m[0]]));
  }
  for (const m of html.matchAll(/<link\b[^>]*>/gi)) {
    if (!/rel\s*=\s*["']?stylesheet/i.test(m[0])) continue;
    const href = /href\s*=\s*["']([^"']+)["']/i.exec(m[0])?.[1];
    const url = propia(href);
    if (!url) continue;
    reemplazos.push(obtener(url).then((r) => [m[0], r ? `<style data-archivo="${escAttr(url)}">\n${texto(r.bytes).replace(/<\/style/gi, "<\\/style")}\n</style>` : m[0]]));
  }
  for (const m of html.matchAll(/<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["'][^>]*>/gi)) {
    const url = propia(m[1]);
    if (!url) continue;
    reemplazos.push(obtener(url).then((r) => [m[0], r ? m[0].replace(m[1], `data:${r.tipo || "image/png"};base64,${aB64(r.bytes)}`) : m[0]]));
  }
  let salida = html;
  for (const [antes, despues] of await Promise.all(reemplazos)) salida = salida.split(antes).join(despues);
  // Scripts escritos dentro de la página y onclick="location.href=…"
  salida = salida.replace(/<script\b(?![^>]*\bsrc\s*=)([^>]*)>([\s\S]*?)<\/script>/gi, (todo, attrs, cuerpo) => (/type\s*=\s*["']?(?:application\/json|text\/template|importmap)/i.test(attrs) ? todo : `<script${attrs}>${reescribirUbicacion(cuerpo)}</script>`));
  return reescribirAtributos(salida);
}
