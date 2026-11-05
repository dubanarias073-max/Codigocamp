// Lógica de chats.html
import { iniciar, api, esc, aviso } from "/js/app.js";
await iniciar("chats");
const $ = (id) => document.getElementById(id);
let datos, activo = null, ultimo = 0;
const TITULO = document.title;
const ini = (n) => esc((n || "?").charAt(0).toUpperCase());
const avatar = (x) => `<span class="c-av${x.avatar ? " emoji" : ""}">${x.avatar ? esc(x.avatar) : ini(x.nombre)}</span>`;

/* ===== Lista de amigos y solicitudes ===== */
async function cargarLista() {
  datos = await api("/api/amigos/");
  if (activo && !datos.amigos.some((a) => a.id === activo)) cerrar();
  $("miCodigo").textContent = datos.yo.codigo;
  $("miAlias").textContent = "@" + datos.yo.alias;
  $("miAv").textContent = datos.yo.avatar || (datos.yo.nombre || "?").charAt(0).toUpperCase();
  $("miAv").classList.toggle("emoji", !!datos.yo.avatar);
  const rec = datos.recibidas.map((r) => `<div class="c-fila">${avatar(r)}<span><b>${esc(r.nombre)}</b><small>@${esc(r.alias)}</small></span>
    <span class="c-acc"><button class="btn sm pri" type="button" data-r="${r.id}" data-a="1">Aceptar</button><button class="btn sm" type="button" data-r="${r.id}" data-a="0">No</button></span></div>`).join("");
  const env = datos.enviadas.length ? `<small>Solicitudes enviadas: ${datos.enviadas.map((e) => "@" + esc(e.alias)).join(", ")}</small>` : "";
  $("solicitudes").innerHTML = (rec ? "<h3>Solicitudes</h3>" + rec : "") + env;
  $("amigos").innerHTML = datos.amigos.length
    ? "<h3>Amigos</h3>" + datos.amigos.map((a) => `<button class="c-fila${a.id === activo ? " on" : ""}" type="button" data-id="${a.id}">
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
function pintar(ms) {
  const log = $("log");
  const abajo = log.scrollHeight - log.scrollTop - log.clientHeight < 60;
  for (const m of ms) {
    const d = document.createElement("div");
    d.className = "cm" + (m.yo ? " yo" : "");
    d.append(contenido(m.texto));
    const h = document.createElement("small"); h.textContent = m.hora; d.append(h);
    log.appendChild(d); ultimo = m.id;
  }
  if (abajo || !ms.length) log.scrollTop = log.scrollHeight;
}

async function abrir(id) {
  activo = id; ultimo = 0;
  $("log").innerHTML = "";
  $("vacio").hidden = true; ["cab", "log", "fMsg", "emojis"].forEach((x) => { $(x).hidden = false; });
  const amigo = datos.amigos.find((a) => a.id === id);
  $("cNombre").textContent = amigo ? `${amigo.avatar || ""} ${amigo.nombre} · @${amigo.alias}`.trim() : "";
  $("cg").classList.add("en-chat");
  try {
    const ms = (await api(`/api/chat/${id}/`)).mensajes;
    if (!ms.length) { const v = document.createElement("p"); v.className = "nota c-saludo"; v.textContent = "Aún no hay mensajes. ¡Saluda y empiecen a practicar juntos!"; $("log").append(v); }
    else pintar(ms);
  } catch (e) { aviso(e.message, true); }
  cargarLista().catch(() => {});
  $("texto").focus();
}
function cerrar() {
  activo = null;
  $("vacio").hidden = false; ["cab", "log", "fMsg", "emojis"].forEach((x) => { $(x).hidden = true; });
  $("cg").classList.remove("en-chat");
}

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
$("volver").onclick = cerrar;
$("quitar").onclick = async () => {
  if (!activo || !confirm("¿Quitar a este amigo? Se borrará la conversación.")) return;
  try { await api(`/api/amigos/${activo}/quitar/`, {}); cerrar(); cargarLista(); } catch (x) { aviso(x.message, true); }
};
$("emojis").innerHTML = ["👍", "😂", "🎉", "🔥", "💻", "🤔", "❓", "🙌"].map((e) => `<button type="button" class="btn sm" aria-label="Insertar ${e}">${e}</button>`).join("");
$("emojis").onclick = (e) => {
  const b = e.target.closest("button"); if (!b) return;
  const t = $("texto"); t.setRangeText(b.textContent, t.selectionStart, t.selectionEnd, "end"); t.focus();
};
$("fMsg").onsubmit = async (e) => {
  e.preventDefault();
  const texto = $("texto").value.trim();
  if (!texto || !activo) return;
  try {
    const r = await api(`/api/chat/${activo}/?despues=${ultimo}`, { texto });
    $("texto").value = "";
    $("log").querySelector(".c-saludo")?.remove();
    pintar(r.mensajes);
  } catch (x) { aviso(x.message, true); }
};

await cargarLista();
// Enlace de invitación: /pages/chats.html?agregar=CODIGO
const invitado = new URLSearchParams(location.search).get("agregar");
if (invitado) { history.replaceState(null, "", location.pathname); if (invitado.toUpperCase() !== datos.yo.codigo) await agregar(invitado); }
setInterval(async () => { if (!document.hidden && activo) { try { const ms = (await api(`/api/chat/${activo}/?despues=${ultimo}`)).mensajes; if (ms.length) $("log").querySelector(".c-saludo")?.remove(); pintar(ms); } catch {} } }, 4000);
setInterval(() => { if (!document.hidden) cargarLista().catch(() => {}); }, 15000);
