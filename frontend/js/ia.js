// Lógica de ia.html
import { iniciar, api, aviso, esc } from "/js/app.js";
import { CSS_ADJUNTOS, crearAdjuntador } from "/js/adjuntar.js";
import { formato } from "/js/formato-ia.js";
const { user, prog } = await iniciar("ia");
document.head.insertAdjacentHTML("beforeend", `<style>${CSS_ADJUNTOS}</style>`);
const $ = (id) => document.getElementById(id);
const CLAVE = "cc_ia_" + (user?.id ?? "x");   // conversación antigua (antes se guardaba solo en este navegador)
const MAX = 12000;
let actual = null;          // { id, titulo, fijada } o null = conversación nueva (se crea al enviar)
let lista = [];
let mensajes = [];

function burbuja(rol, texto, archivos = []) {
  const d = document.createElement("div");
  d.className = "msg " + rol;
  if (rol === "tutor") formato(d, texto); else d.textContent = texto;
  if (archivos.length) d.insertAdjacentHTML("beforeend", `<div class="ia-adj">${archivos.map((a) => (a.vista ? `<img src="${esc(a.vista)}" alt="${esc(a.nombre)}">` : `<span>📄 ${esc(a.nombre)}</span>`)).join("")}</div>`);
  $("log").appendChild(d); $("log").scrollTop = $("log").scrollHeight;
  return d;
}
function pintarHistorial() {
  $("log").replaceChildren();
  const nombre = (user?.nombre || "").split(" ")[0];
  if (!mensajes.length) burbuja("tutor", `¡Hola${nombre ? ", " + nombre : ""}! Soy tu tutor${prog.curso_actual ? " de " + prog.curso_actual.nombre : ""}. ¿Qué quieres aprender hoy?`);
  mensajes.forEach((m) => burbuja(m.rol, m.texto, (m.archivos || []).map((n) => ({ nombre: n }))));
  $("tituloConv").textContent = actual?.titulo || "Conversación nueva";
  $("cabBtns").hidden = !actual;
  $("sug").hidden = Boolean(mensajes.length);
}

/* ===== Lista de conversaciones (como en Claude: hoy, ayer, 7 días, anteriores) ===== */
function grupoDe(iso, fijada) {
  if (fijada) return "Fijadas";
  const d = new Date(iso), hoy = new Date(); hoy.setHours(0, 0, 0, 0);
  const dias = Math.floor((hoy - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
  return dias <= 0 ? "Hoy" : dias === 1 ? "Ayer" : dias < 7 ? "Últimos 7 días" : dias < 30 ? "Últimos 30 días" : "Anteriores";
}
function pintarLista() {
  let html = "", grupo = "";
  for (const c of lista) {
    const g = grupoDe(c.actualizada, c.fijada);
    if (g !== grupo) { html += `<p class="ia-grupo">${g}</p>`; grupo = g; }
    html += `<button type="button" class="ia-conv${actual?.id === c.id ? " on" : ""}" data-id="${c.id}" title="${esc(c.titulo)}">${c.fijada ? '<i class="pin" aria-label="Fijada">📌</i>' : ""}<span>${esc(c.titulo)}</span></button>`;
  }
  $("convs").innerHTML = html || `<p class="nota">${$("buscarConv").value ? "No hay chats con ese texto." : "Aún no tienes conversaciones. Escribe tu primera pregunta."}</p>`;
}
async function cargarLista() {
  try { lista = (await api(`/api/ia/conversaciones/?q=${encodeURIComponent($("buscarConv").value.trim())}`)).conversaciones; }
  catch { lista = []; }
  pintarLista();
}
async function abrirConv(id, { empujar = true } = {}) {
  try {
    const { conversacion } = await api(`/api/ia/conversaciones/${id}`);
    actual = { id: conversacion.id, titulo: conversacion.titulo, fijada: conversacion.fijada };
    mensajes = conversacion.mensajes;
    if (empujar) history.replaceState(null, "", `?c=${id}`);
  } catch { actual = null; mensajes = []; history.replaceState(null, "", location.pathname); }   // ya no existe: conversación nueva
  pintarHistorial(); pintarLista();
  $("iaLista").classList.remove("abierta");
  $("q").focus();
}
function nuevaConv() {
  actual = null; mensajes = [];
  history.replaceState(null, "", location.pathname);
  pintarHistorial(); pintarLista();
  $("iaLista").classList.remove("abierta");
  $("q").focus();
}
$("convs").onclick = (e) => { const b = e.target.closest("[data-id]"); if (b) abrirConv(Number(b.dataset.id)); };
let tBuscar = 0;
$("buscarConv").oninput = () => { clearTimeout(tBuscar); tBuscar = setTimeout(cargarLista, 250); };
$("verLista").onclick = () => { const abierta = $("iaLista").classList.toggle("abierta"); $("verLista").setAttribute("aria-expanded", String(abierta)); };
$("cabBtns").onclick = async (e) => {
  const b = e.target.closest("[data-conv]");
  if (!b || !actual) return;
  try {
    if (b.dataset.conv === "renombrar") {
      const t = prompt("Nuevo nombre de la conversación:", actual.titulo);
      if (!t || !t.trim()) return;
      actual.titulo = (await api(`/api/ia/conversaciones/${actual.id}`, { titulo: t.trim() }, "PATCH")).conversacion.titulo;
    } else if (b.dataset.conv === "fijar") {
      actual.fijada = (await api(`/api/ia/conversaciones/${actual.id}`, { fijada: !actual.fijada }, "PATCH")).conversacion.fijada;
      aviso(actual.fijada ? "Conversación fijada" : "Conversación desfijada");
    } else if (b.dataset.conv === "borrar") {
      if (!confirm(`¿Borrar «${actual.titulo}»? No se puede deshacer.`)) return;
      await api(`/api/ia/conversaciones/${actual.id}`, undefined, "DELETE");
      nuevaConv();
    }
  } catch (x) { aviso(x.message, true); }
  $("tituloConv").textContent = actual?.titulo || "Conversación nueva";
  cargarLista();
};

// Lo que estaba guardado solo en este navegador pasa a tu cuenta (una vez).
try {
  const viejo = JSON.parse(localStorage.getItem(CLAVE) || "[]");
  if (Array.isArray(viejo) && viejo.length) {
    const { conversacion } = await api("/api/ia/conversaciones/", { titulo: viejo.find((m) => m.rol === "yo")?.texto || "Conversación anterior", mensajes: viejo });
    localStorage.removeItem(CLAVE);
    if (!new URLSearchParams(location.search).get("c")) history.replaceState(null, "", `?c=${conversacion.id}`);
  }
} catch { /* se intenta la próxima vez */ }
await cargarLista();
{ const c = Number(new URLSearchParams(location.search).get("c")); if (c) await abrirConv(c, { empujar: false }); else pintarHistorial(); }

/* ===== Sugerencias según el curso ===== */
const curso = prog.curso_actual?.nombre;
const SUG = [curso ? `Explícame lo más importante de ${curso}` : "Explícame qué es una variable", "Revisa mi código", "Dame un ejercicio fácil", "¿Qué error es este y cómo lo arreglo?", "Explícame esta captura de pantalla", "¿Cómo conecto mi app con MySQL de XAMPP?"];
$("sug").innerHTML = SUG.map((s) => `<button type="button"></button>`).join("");
$("sug").querySelectorAll("button").forEach((b, i) => { b.textContent = SUG[i]; });
$("sug").onclick = (e) => { if (e.target.matches("button")) { $("q").value = e.target.textContent; actualizar(); $("q").focus(); } };

/* ===== Escribir y enviar ===== */
const actualizar = () => { $("cuenta").textContent = `${$("q").value.length} / ${MAX}`; };
$("q").oninput = actualizar;
$("codigo").onclick = () => { const q = $("q"); q.setRangeText("```\n\n```", q.selectionStart, q.selectionEnd, "end"); q.setSelectionRange(q.selectionEnd - 4, q.selectionEnd - 4); q.focus(); actualizar(); };
$("nueva").onclick = nuevaConv;
$("q").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("f").requestSubmit(); } };
const adj = crearAdjuntador({ boton: $("clip"), entrada: $("archivosIa"), bandeja: $("bandeja"), zona: document.querySelector(".ia"), destino: "ia" });
$("f").onsubmit = async (e) => {
  e.preventDefault();
  const t = $("q").value.trim();
  if ((!t && !adj.hay()) || $("enviar").disabled) return;
  $("enviar").disabled = true;
  let adjuntos = [];
  const archivos = adj.adjuntos();
  try { adjuntos = await adj.listos(); } catch (x) { aviso(x.message, true); $("enviar").disabled = false; return; }
  $("q").value = ""; actualizar();
  if (!mensajes.length) $("log").replaceChildren();
  $("sug").hidden = true;
  burbuja("yo", t || "(archivos)", adj.adjuntos());
  adj.limpiar();
  const espera = burbuja("tutor", adjuntos.length ? "Revisando tus archivos…" : "Pensando…");
  try {
    const r = await api("/api/tutor/", { mensaje: t, adjuntos, ...(actual ? { conversacion_id: actual.id } : { guardar: true }), contexto: { pagina: "IA" } });
    formato(espera, r.respuesta);
    mensajes.push({ rol: "yo", texto: t || "(archivos)", archivos: archivos.map((a) => a.nombre) }, { rol: "tutor", texto: r.respuesta });
    if (r.conversacion) {
      const nueva = !actual;
      actual = { id: r.conversacion.id, titulo: r.conversacion.titulo, fijada: actual?.fijada || false };
      if (nueva) history.replaceState(null, "", `?c=${actual.id}`);
      $("tituloConv").textContent = actual.titulo; $("cabBtns").hidden = false;
      cargarLista();
    }
  } catch (x) {
    espera.textContent = x.message; espera.classList.add("error");
    $("q").value = t; actualizar();                 // no pierdes lo que escribiste
  }
  $("enviar").disabled = false; $("log").scrollTop = $("log").scrollHeight; $("q").focus();
};
