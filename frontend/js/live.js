// Página «en vivo» (/live/<clave>/…), como Live Server pero desde cualquier navegador o celular.
// Arma la página con el MISMO motor que la vista previa de Trabajo (React/JSX, TypeScript, módulos, paquetes de npm,
// Vite, imágenes), la pone en un <iframe> aislado (sin acceso a la sesión de CódigoCamp) y se recarga sola cuando
// guardas en Trabajo, sin perder dónde ibas.
import * as FS from "/js/trabajo/fs.js";
import { leerMarcador } from "/js/trabajo/archivos.js";
import { carpetaDelPaquete } from "/js/trabajo/paquetes.js";
import { construirVistaPrevia, paginaPrincipal, resolverEnlace } from "/js/trabajo/vista.js";
import { modulosDePagina, proxyDeVite, usaModulos } from "/js/trabajo/modulos.js";
import { resolverDestino, urlDeArchivo } from "/js/trabajo/virtual.js";

const $ = (id) => document.getElementById(id);
const partes = location.pathname.split("/");          // ["", "live", clave, ...ruta]
const clave = partes[2];
const BASE = `/live/${clave}`;
let marco = $("ccVista");
const estado = $("ccEstado");
const CLAVE_ALMACEN = `cc-live-${clave}`;

let py = null;
let version = null;
let pagina = null;
let urlVirtual = null;
let turno = 0;
const scroll = { pagina: null, y: 0 };

// localStorage / cookies de TU página: se guardan en este navegador (no en CódigoCamp).
const almacen = (() => {
  try { const a = JSON.parse(localStorage.getItem(CLAVE_ALMACEN) || "{}"); return { local: a.local || {}, cookies: a.cookies || {}, sesion: {} }; }
  catch { return { local: {}, cookies: {}, sesion: {} }; }
})();
const guardarAlmacen = () => { try { localStorage.setItem(CLAVE_ALMACEN, JSON.stringify({ local: almacen.local, cookies: almacen.cookies })); } catch { /* sin espacio */ } };

const rutaDeUrl = () => {
  let r = location.pathname.split("/").slice(3).join("/");
  try { r = decodeURIComponent(r); } catch { /* tal cual */ }
  return r;
};
const raizDe = (p) => (p ? carpetaDelPaquete(py, FS.carpetaDe(p)) ?? "" : "");
const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");

async function cargarProyecto() {
  const r = await fetch(`${BASE}/__cc_proyecto`, { cache: "no-store", credentials: "omit" });
  if (r.status === 404) throw new Error("Este enlace ya no funciona. Pídele a quien te lo pasó el enlace nuevo.");
  if (!r.ok) throw new Error(`El servidor respondió ${r.status}.`);
  const j = await r.json();
  py = { files: j.files || {}, folders: j.folders || [] };
  version = j.v;
}

/** Qué página corresponde a la dirección: archivo exacto, carpeta/ → index.html, /x → x.html. */
function paginaDeRuta(ruta) {
  const limpia = ruta.replace(/^\/+/, "");
  const candidatos = !limpia || limpia.endsWith("/") ? [FS.unir(limpia, "index.html")] : [limpia, `${limpia}.html`, FS.unir(limpia, "index.html")];
  return candidatos.find((c) => FS.tieneArchivo(py, c) && /\.html?$/i.test(c)) ?? paginaPrincipal(py, null);
}

function mapaDeArchivos() {
  const m = new Map();
  for (const t of Object.values(py.files)) { const x = leerMarcador(t); if (x) m.set(x.hash, `${location.origin}${BASE}/__cc_bin/${x.hash}`); }
  return m;
}

/** Pone el HTML en un iframe NUEVO: cambiar srcdoc agregaría pasos al historial y «atrás» no volvería a la página anterior. */
function ponerHTML(html, y = 0) {
  const nuevo = marco.cloneNode(false);
  if (y > 0) nuevo.addEventListener("load", () => { try { nuevo.contentWindow.postMessage({ cc: "irscroll", y }, "*"); } catch { /* cambió */ } }, { once: true });
  nuevo.srcdoc = html;
  marco.replaceWith(nuevo);
  marco = nuevo;
}

function mostrarMensaje(html) {
  ponerHTML(`<!doctype html><meta charset="utf-8"><body style="font:15px system-ui;padding:28px;max-width:680px;color:#334155;line-height:1.5">${html}</body>`);
}

async function pintar({ conservarScroll = false } = {}) {
  const mio = ++turno;
  if (!pagina) {
    const lista = Object.keys(py.files).filter((r) => /\.html?$/i.test(r));
    mostrarMensaje(lista.length ? `<h2>No hay una página en esta dirección</h2><p>Páginas del proyecto:</p><ul>${lista.map((r) => `<li><a href="${BASE}/${r.split("/").map(encodeURIComponent).join("/")}" target="_top">${esc(r)}</a></li>`).join("")}</ul>`
      : "<h2>Este proyecto aún no tiene páginas</h2><p>Crea un archivo <b>index.html</b> en Trabajo y guárdalo.</p>");
    $("ccCarga").hidden = true;
    return;
  }
  const raiz = raizDe(pagina);
  const proxy = proxyDeVite(py, raiz);
  const mapa = mapaDeArchivos();
  let modulos = null;
  if (usaModulos(py, pagina)) {
    try {
      const { transpilarModulo } = await import("/js/trabajo/ejecucion.js");
      modulos = await modulosDePagina(py, pagina, { transpilar: transpilarModulo, enlaces: mapa });
      for (const e of modulos.errores) console.error(e);
    } catch (error) { console.error(`No se pudieron preparar los módulos: ${error.message}`); }
  }
  if (mio !== turno) return;
  if (!urlVirtual || resolverDestino(py, raiz, urlVirtual, proxy).ruta !== pagina) urlVirtual = urlDeArchivo(raiz, pagina);
  const y = conservarScroll && scroll.pagina === pagina ? scroll.y : 0;
  if (!y) scroll.y = 0;
  try {
    ponerHTML(construirVistaPrevia(py, pagina, { imagenes: mapa, modulos, proxy, virtual: { url: urlVirtual, almacen } }), y);
  } catch (error) {
    mostrarMensaje(`<h2 style="color:#b91c1c">No se pudo armar la página</h2><pre style="white-space:pre-wrap">${esc(error.message || error)}</pre>`);
  }
  scroll.pagina = pagina;
  $("ccCarga").hidden = true;
}

function ir(ruta, { reemplazar = false, url = null } = {}) {
  pagina = ruta;
  urlVirtual = url;
  const destino = `${BASE}/${ruta === "index.html" ? "" : ruta.split("/").map(encodeURIComponent).join("/")}`;
  if (location.pathname !== destino) history[reemplazar ? "replaceState" : "pushState"]({ pagina: ruta }, "", destino);
  pintar();
}

/* ===== Enlaces externos de la página compartida (https://, www., wa.me, mailto:…) =====
 * Antes no hacían nada: la página está aislada y el aviso «externo» no se atendía aquí.
 * Ahora se revisan (virus y estafas se bloquean y NUNCA se abren) y se abren en una pestaña nueva. */
const escE = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function tarjetaEnlace(html, botones = []) {
  document.getElementById("ccEnlace")?.remove();
  const d = document.createElement("div");
  d.id = "ccEnlace";
  d.setAttribute("role", "dialog");
  d.style.cssText = "position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:20;width:min(440px,calc(100vw - 24px));box-sizing:border-box;padding:14px 16px;border-radius:14px;background:#0f172a;color:#e2e8f0;font:14px/1.45 system-ui,sans-serif;box-shadow:0 14px 40px rgba(0,0,0,.35)";
  d.innerHTML = html + `<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:10px;flex-wrap:wrap">${botones.map(([id, t, pri]) =>
    `<button type="button" data-b="${id}" style="padding:8px 14px;border-radius:10px;border:0;cursor:pointer;font:700 13px system-ui;${pri ? "background:#22c55e;color:#052e16" : "background:#334155;color:#e2e8f0"}">${t}</button>`).join("")}</div>`;
  document.body.appendChild(d);
  return new Promise((ok) => { d.onclick = (e) => { const b = e.target.closest("[data-b]"); if (b) { d.remove(); ok(b.dataset.b); } }; });
}
function abrirPestana(href) {
  if (window.CodigoCampApp?.abrirFuera) { try { window.CodigoCampApp.abrirFuera(href); return true; } catch { /* sigue */ } }
  const w = window.open(href, "_blank");
  if (w) { try { w.opener = null; } catch { /* nada */ } return true; }
  return false;
}
async function abrirExterno(href) {
  let u;
  try { u = new URL(/^www\./i.test(href) ? "https://" + href : href); } catch { return; }
  if (/^(mailto|tel):$/.test(u.protocol)) { location.href = u.href; return; }
  if (!/^https?:$/.test(u.protocol)) return;
  let r;
  try {
    const resp = await fetch(`${BASE}/__cc_enlace`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: u.href }) });
    r = await resp.json();
  } catch { r = { nivel: "advertencia", motivo: "No se pudo revisar este enlace ahora mismo." }; }
  const sitio = `<b style="word-break:break-all">${escE(u.hostname)}</b>`;
  if (r.nivel === "bloqueado") {
    await tarjetaEnlace(`<b>🛡️ Enlace bloqueado</b><p style="margin:6px 0 0">CódigoCamp no abrirá ${sitio} porque puede dañar tu equipo o robar tus datos. ${escE(r.motivo || "")}</p>`, [["ok", "Entendido"]]);
    return;
  }
  if (r.nivel === "advertencia") {
    const v = await tarjetaEnlace(`<b>⚠️ Revisa este enlace</b><p style="margin:6px 0 0">Vas a abrir ${sitio}. ${escE(r.motivo || "")}</p>`, [["no", "No abrir"], ["si", "Abrir de todos modos"]]);
    if (v === "si" && !abrirPestana(u.href)) location.assign(u.href);
    return;
  }
  // Seguro: se abre al instante; si el navegador bloqueó la ventana nueva, un toque más la abre
  if (abrirPestana(u.href)) return;
  const v = await tarjetaEnlace(`<b>Enlace externo</b><p style="margin:6px 0 0">Esta página quiere abrir ${sitio}.</p>`, [["no", "Cancelar"], ["si", "Abrir ↗", true]]);
  if (v === "si" && !abrirPestana(u.href)) location.assign(u.href);
}

// Lo que pide la página: navegar a otra página del proyecto, guardar su localStorage, su scroll…
addEventListener("message", (e) => {
  if (e.source !== marco.contentWindow) return;
  const m = e.data;
  if (!m || typeof m !== "object") return;
  if (m.cc === "scroll") { scroll.pagina = pagina; scroll.y = Number(m.y) || 0; }
  else if (m.cc === "ls") {
    const t = String(m.tipo);
    if (t === "local") almacen.local = m.datos || {};
    else if (t === "cookies") almacen.cookies = m.datos || {};
    else if (t === "sesion") almacen.sesion = m.datos || {};
    guardarAlmacen();
  } else if (m.cc === "vnav" || m.cc === "vurl") {
    const raiz = raizDe(pagina);
    const d = resolverDestino(py, raiz, String(m.url), proxyDeVite(py, raiz));
    if (d.tipo === "archivo") { if (m.cc === "vnav") ir(d.ruta, { url: String(m.url) }); else urlVirtual = String(m.url); }
    else if (d.tipo === "externo" && m.cc === "vnav") abrirExterno(d.url);
    else if (m.cc === "vnav") mostrarMensaje(d.tipo === "remoto"
      ? `<h2>Esta parte necesita tu backend</h2><p>La dirección <code>${esc(m.url)}</code> va a un servidor (Flask, FastAPI, Express…). Ese servidor corre en Trabajo: ábrela desde la vista previa de Trabajo.</p><p><a href="${BASE}/" target="_top">← Volver al inicio</a></p>`
      : `<h2>Cannot GET ${esc(new URL(String(m.url)).pathname)}</h2><p>No hay ningún archivo en esa dirección del proyecto.</p><p><a href="${BASE}/" target="_top">← Volver al inicio</a></p>`);
  } else if (m.cc === "nav") {
    const destino = resolverEnlace(py, pagina || "", String(m.href || ""));
    if (destino) ir(destino);
    else if (/^https?:/i.test(String(m.href))) abrirExterno(String(m.href));
  } else if (m.cc === "externo") {
    abrirExterno(String(m.href || ""));
  } else if (m.cc === "http") {
    // fetch() a un backend: en el navegador no hay uno corriendo (ese corre en Trabajo)
    try { e.source.postMessage({ cc: "http-r", id: m.id, error: "Failed to fetch (tu backend corre en Trabajo, no en este enlace)" }, "*"); } catch { /* nada */ }
  } else if (m.cc === "vpagina") {
    const raiz = raizDe(pagina);
    const d = resolverDestino(py, raiz, String(m.url), proxyDeVite(py, raiz));
    const html = d.tipo === "archivo" ? construirVistaPrevia(py, d.ruta, { imagenes: mapaDeArchivos(), proxy: [], virtual: { url: String(m.url), almacen, hijo: true } }) : null;
    try { e.source.postMessage(html ? { cc: "vpagina-r", id: m.id, html } : { cc: "vpagina-r", id: m.id, error: `No se pudo cargar ${m.url}` }, "*"); } catch { /* nada */ }
  }
});
addEventListener("popstate", () => { pagina = paginaDeRuta(rutaDeUrl()); urlVirtual = null; pintar(); });

// En vivo: pregunta cada segundo y medio si guardaste algo nuevo
let fallos = 0;
async function vigilar() {
  try {
    const r = await fetch(`${BASE}/__cc_version`, { cache: "no-store", credentials: "omit" });
    if (r.status === 404) { estado.classList.add("error"); estado.querySelector("span").textContent = "Este enlace ya no funciona"; return; }
    const { v } = await r.json();
    fallos = 0;
    estado.classList.remove("error");
    if (v && v !== version) {
      await cargarProyecto();
      if (!FS.tieneArchivo(py, pagina || "")) pagina = paginaDeRuta(rutaDeUrl());
      await pintar({ conservarScroll: true });
    }
  } catch { fallos += 1; if (fallos > 3) estado.classList.add("error"); }
  setTimeout(vigilar, document.hidden ? 4000 : fallos > 5 ? 6000 : 1500);
}

estado.addEventListener("click", () => estado.classList.toggle("chico"));
setTimeout(() => estado.classList.add("chico"), 4000);

try {
  await cargarProyecto();
  pagina = paginaDeRuta(rutaDeUrl());
  if (pagina) history.replaceState({ pagina }, "", location.pathname);
  await pintar();
  document.title = `${pagina || "Vista en vivo"} · CódigoCamp`;
  setTimeout(vigilar, 1500);
} catch (error) {
  $("ccCarga").hidden = true;
  estado.classList.add("error");
  mostrarMensaje(`<h2>No se pudo abrir la página</h2><p>${esc(error.message)}</p>`);
}
