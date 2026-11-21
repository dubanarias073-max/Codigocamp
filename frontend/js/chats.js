// Lógica de chats.html
import { avatarSVG } from "/js/avatares.js";
import { iniciar, api, esc, aviso, fotoDe } from "/js/app.js";
import { CSS_ADJUNTOS, crearAdjuntador, htmlAdjuntos } from "/js/adjuntar.js";
await iniciar("chats");
document.head.insertAdjacentHTML("beforeend", `<style>${CSS_ADJUNTOS}</style>`);
const $ = (id) => document.getElementById(id);
let datos, activo = null, ultimo = 0;
let ultimoDia = "", ultimoAutor = null;
const TITULO = document.title;
const TACTIL = matchMedia("(pointer: coarse)").matches;
// Alto de la barra de abajo del celular, para que el chat ocupe justo el resto de la pantalla.
{ const inf = $("inf"); const medir = () => document.documentElement.style.setProperty("--alto-inf", `${inf.offsetHeight || 0}px`); new ResizeObserver(medir).observe(inf); medir(); }
const ini = (n) => esc((n || "?").charAt(0).toUpperCase());
const avatar = (x) => (x.foto || avatarSVG(x.avatar) ? `<span class="c-av c-av-foto">${fotoDe({ ...x, cosmeticos: { marco: x.marco } }, { tam: 38 })}</span>` : `<span class="c-av">${ini(x.nombre)}</span>`);

/* ===== Lista de amigos y solicitudes ===== */
async function cargarLista() {
  datos = await api("/api/amigos/");
  if (activo && !datos.amigos.some((a) => a.id === activo)) cerrar();
  $("miCodigo").textContent = datos.yo.codigo;
  $("miAlias").textContent = "@" + datos.yo.alias;
  if (datos.yo.foto) { $("miAv").innerHTML = fotoDe({ ...datos.yo, cosmeticos: { marco: datos.yo.marco } }, { tam: 44 }); $("miAv").classList.add("c-av-foto"); }
  else if (avatarSVG(datos.yo.avatar)) $("miAv").innerHTML = avatarSVG(datos.yo.avatar, 40);
  else $("miAv").textContent = (datos.yo.nombre || "?").charAt(0).toUpperCase();
  const rec = datos.recibidas.map((r) => `<div class="c-fila">${avatar(r)}<span><b>${esc(r.nombre)}</b><small>@${esc(r.alias)}</small></span>
    <span class="c-acc"><button class="btn sm pri" type="button" data-r="${r.id}" data-a="1">Aceptar</button><button class="btn sm" type="button" data-r="${r.id}" data-a="0">No</button></span></div>`).join("");
  const env = datos.enviadas.length ? `<small>Solicitudes enviadas: ${datos.enviadas.map((e) => "@" + esc(e.alias)).join(", ")}</small>` : "";
  $("solicitudes").innerHTML = (rec ? "<h3>Solicitudes</h3>" + rec : "") + env;
  $("amigos").innerHTML = datos.amigos.length
    ? "<h3>Amigos</h3>" + datos.amigos.map((a) => `<button class="c-fila${a.id === activo ? " on" : ""}${a.no_leidos ? " nuevo" : ""}" type="button" data-id="${a.id}">
        ${avatar(a)}<span><b>${esc(a.nombre)}</b><small>${esc(a.ultimo || "@" + a.alias)}</small></span>
        ${a.no_leidos ? `<span class="c-badge">${a.no_leidos}</span>` : ""}</button>`).join("")
    : '<p class="nota">Todavía no tienes amigos. Búscalos arriba por nombre o usuario, o mándales tu enlace de invitación.</p>';
  const total = datos.amigos.reduce((n, a) => n + a.no_leidos, 0) + datos.recibidas.length;
  document.title = total ? `(${total}) ${TITULO}` : TITULO;
}

/* ===== Mensajes: `texto` entre comillas invertidas se muestra como código ===== */
function contenido(texto) {
  const frag = document.createDocumentFragment();
  texto.split(/(`[^`]+`)/).forEach((t) => {
    if (!t) return;
    if (t.length > 2 && t[0] === "`" && t.at(-1) === "`") { const c = document.createElement("code"); c.textContent = t.slice(1, -1); frag.append(c); }
    else frag.append(document.createTextNode(t));
  });
  return frag;
}
function nombreDia(fecha) {
  const d = new Date(fecha);
  if (Number.isNaN(d.getTime())) return "";
  const hoy = new Date(); hoy.setHours(0, 0, 0, 0);
  const dias = Math.round((hoy - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
  if (dias === 0) return "Hoy";
  if (dias === 1) return "Ayer";
  return d.toLocaleDateString("es", { weekday: dias < 7 ? "long" : undefined, day: "numeric", month: "long", year: d.getFullYear() !== hoy.getFullYear() ? "numeric" : undefined });
}
function pintar(ms, { forzar = false } = {}) {
  const log = $("log");
  const abajo = forzar || log.scrollHeight - log.scrollTop - log.clientHeight < 80;
  for (const m of ms) {
    const dia = m.fecha ? nombreDia(m.fecha) : "";
    if (dia && dia !== ultimoDia) {
      const sep = document.createElement("div"); sep.className = "c-dia"; sep.textContent = dia; log.appendChild(sep);
      ultimoDia = dia; ultimoAutor = null;
    }
    const d = document.createElement("div");
    d.className = "cm" + (m.yo ? " yo" : "") + (ultimoAutor === m.yo ? " seguido" : "") + (m.adjuntos?.length && !m.texto ? " solo-adj" : "");
    if (m.texto) d.append(contenido(m.texto));
    if (m.adjuntos?.length) d.insertAdjacentHTML("beforeend", htmlAdjuntos(m.adjuntos));
    const h = document.createElement("small"); h.className = "cm-hora"; h.textContent = m.hora; d.append(h);
    log.appendChild(d); ultimo = m.id; ultimoAutor = m.yo;
  }
  if (abajo || !ms.length) log.scrollTop = log.scrollHeight;
}

async function abrir(id) {
  activo = id; ultimo = 0; ultimoDia = ""; ultimoAutor = null;
  $("log").innerHTML = "";
  $("vacio").hidden = true; ["cab", "log", "fMsg"].forEach((x) => { $(x).hidden = false; });
  mostrarEmojis(false); menu(false);
  const amigo = datos.amigos.find((a) => a.id === id);
  $("cNombre").textContent = amigo?.nombre ?? "";
  $("cAlias").textContent = amigo ? `@${amigo.alias}` : "";
  $("cAv").outerHTML = amigo ? avatar(amigo).replace('class="c-av', 'id="cAv" class="c-av') : '<span class="c-av" id="cAv"></span>';
  $("cg").classList.add("en-chat");
  document.body.classList.add("en-chat");
  if (!new URLSearchParams(location.search).has("con")) history.pushState({ chat: id }, "", `?con=${id}`);
  try {
    const ms = (await api(`/api/chat/${id}/`)).mensajes;
    if (!ms.length) { const v = document.createElement("p"); v.className = "nota c-saludo"; v.textContent = "Aún no hay mensajes. ¡Saluda y empiecen a practicar juntos!"; $("log").append(v); }
    else pintar(ms, { forzar: true });
  } catch (e) { aviso(e.message, true); }
  cargarLista().catch(() => {});
  if (!TACTIL) $("texto").focus();
}
function cerrar() {
  activo = null;
  $("vacio").hidden = false; ["cab", "log", "fMsg"].forEach((x) => { $(x).hidden = true; });
  mostrarEmojis(false); menu(false);
  $("cg").classList.remove("en-chat");
  document.body.classList.remove("en-chat");
  if (new URLSearchParams(location.search).has("con")) history.replaceState(null, "", location.pathname);
  cargarLista().catch(() => {});
}
// El botón «atrás» del celular vuelve a la lista en vez de salir de Chats.
addEventListener("popstate", () => { if (activo) cerrar(); });
function mostrarEmojis(si) { $("emojis").hidden = !si; $("verEmojis").setAttribute("aria-expanded", String(si)); }
function menu(si) { $("cMenu").hidden = !si; $("cMas").setAttribute("aria-expanded", String(si)); }
$("verEmojis").onclick = () => mostrarEmojis($("emojis").hidden);
$("cMas").onclick = (e) => { e.stopPropagation(); menu($("cMenu").hidden); };
addEventListener("click", (e) => { if (!e.target.closest("#cMenu")) menu(false); });

/* ===== Buscar personas ===== */
let temporizador, busqueda = 0;
async function agregar(quien) {
  try {
    const r = await api("/api/amigos/agregar/", { usuario: quien });
    $("quien").value = ""; $("resultados").innerHTML = "";
    aviso(r.estado === "aceptada" ? `¡Ahora eres amigo de ${r.nombre}!` : `Solicitud enviada a ${r.nombre}`);
    cargarLista();
  } catch (x) { aviso(x.message, true); }
}
const ETQ = { amigo: "Ya son amigos", enviada: "Solicitud enviada", recibida: "Te envió solicitud" };
$("quien").oninput = () => {
  clearTimeout(temporizador);
  const q = $("quien").value.trim().replace(/^@/, "");
  if (q.length < 2) { $("resultados").innerHTML = ""; return; }
  temporizador = setTimeout(async () => {
    const n = ++busqueda;
    try {
      const { resultados } = await api(`/api/usuarios/buscar/?q=${encodeURIComponent(q)}`);
      if (n !== busqueda) return;
      $("resultados").innerHTML = resultados.length
        ? resultados.map((p) => `<div class="c-fila">${avatar(p)}<span><b>${esc(p.nombre)}</b><small>@${esc(p.alias)}</small></span>
            <span class="c-acc">${p.relacion === "amigo" || p.relacion === "enviada" ? `<small>${ETQ[p.relacion]}</small>` : `<button class="btn sm pri" type="button" data-u="${esc(p.alias)}">${p.relacion === "recibida" ? "Aceptar" : "Agregar"}</button>`}</span></div>`).join("")
        : '<p class="nota">Nadie coincide. Prueba con su ID o su @usuario exacto.</p>';
    } catch (x) { $("resultados").innerHTML = `<p class="nota">${esc(x.message)}</p>`; }
  }, 300);
};
$("resultados").onclick = (e) => { const b = e.target.closest("[data-u]"); if (b) agregar(b.dataset.u); };
$("fAgregar").onsubmit = (e) => { e.preventDefault(); const q = $("quien").value.trim(); if (q) agregar(q); };

/* ===== Resto de eventos ===== */
$("amigos").onclick = (e) => { const b = e.target.closest("[data-id]"); if (b) abrir(Number(b.dataset.id)); };
$("solicitudes").onclick = async (e) => {
  const b = e.target.closest("[data-r]");
  if (!b) return;
  try { await api(`/api/amigos/${b.dataset.r}/responder/`, { aceptar: b.dataset.a === "1" }); aviso(b.dataset.a === "1" ? "¡Ahora son amigos!" : "Solicitud rechazada"); }
  catch (x) { aviso(x.message, true); }
  cargarLista();
};
const copiar = (texto, ok) => navigator.clipboard?.writeText(texto).then(() => aviso(ok)).catch(() => aviso(texto));
$("copiar").onclick = () => copiar(datos.yo.codigo, "ID copiado");
$("invitar").onclick = () => copiar(`${location.origin}/pages/chats.html?agregar=${datos.yo.codigo}`, "Enlace copiado: mándalo a quien quieras invitar");
$("volver").onclick = () => { if (history.state?.chat) history.back(); else cerrar(); };
$("quitar").onclick = async () => {
  menu(false);
  if (!activo || !confirm("¿Quitar a este amigo? Se borrará la conversación.")) return;
  try { await api(`/api/amigos/${activo}/quitar/`, {}); cerrar(); cargarLista(); } catch (x) { aviso(x.message, true); }
};
$("emojis").innerHTML = ["👍", "😂", "🎉", "🔥", "💻", "🤔", "❓", "🙌"].map((e) => `<button type="button" class="btn sm" aria-label="Insertar ${e}">${e}</button>`).join("");
$("emojis").onclick = (e) => {
  const b = e.target.closest("button"); if (!b) return;
  const t = $("texto"); t.setRangeText(b.textContent, t.selectionStart, t.selectionEnd, "end"); t.focus();
  actualizarEnviar();
};
const actualizarEnviar = () => { $("fMsg").querySelector("[type=submit]").disabled = !$("texto").value.trim() && !adj.hay(); };
$("texto").addEventListener("input", actualizarEnviar);
const adj = crearAdjuntador({ boton: $("clip"), entrada: $("archivosMsg"), bandeja: $("bandeja"), zona: document.querySelector(".c-conv"), destino: "chat" });
$("fMsg").onsubmit = async (e) => {
  e.preventDefault();
  const texto = $("texto").value.trim();
  if ((!texto && !adj.hay()) || !activo) return;
  const boton = $("fMsg").querySelector("[type=submit]");
  boton.disabled = true;
  try {
    const adjuntos = await adj.listos();
    const r = await api(`/api/chat/${activo}/?despues=${ultimo}`, { texto, adjuntos });
    adj.limpiar();
    $("texto").value = "";
    $("log").querySelector(".c-saludo")?.remove();
    mostrarEmojis(false);
    pintar(r.mensajes, { forzar: true });
  } catch (x) { aviso(x.message, true); }
  actualizarEnviar();
  if (!TACTIL) $("texto").focus();
};
new MutationObserver(() => actualizarEnviar()).observe($("bandeja"), { childList: true });
actualizarEnviar();

await cargarLista();
// Enlace de invitación: /pages/chats.html?agregar=CODIGO
const invitado = new URLSearchParams(location.search).get("agregar");
if (invitado) { history.replaceState(null, "", location.pathname); if (invitado.toUpperCase() !== datos.yo.codigo) await agregar(invitado); }
{ const con = Number(new URLSearchParams(location.search).get("con")); if (con && datos.amigos.some((a) => a.id === con)) abrir(con); else if (con) history.replaceState(null, "", location.pathname); }
setInterval(async () => { if (!document.hidden && activo) { try { const ms = (await api(`/api/chat/${activo}/?despues=${ultimo}`)).mensajes; if (ms.length) $("log").querySelector(".c-saludo")?.remove(); pintar(ms); } catch {} } }, 4000);
setInterval(() => { if (!document.hidden) cargarLista().catch(() => {}); }, 15000);
