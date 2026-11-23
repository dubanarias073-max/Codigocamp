// Lógica de ia.html
import { iniciar, api, aviso, esc } from "/js/app.js";
import { sonar } from "/js/sonidos.js";
import { codiSVG } from "/js/codi.js";
import { CSS_ADJUNTOS, crearAdjuntador } from "/js/adjuntar.js";
import { formato } from "/js/formato-ia.js";
const { user, prog } = await iniciar("ia");
document.head.insertAdjacentHTML("beforeend", `<style>${CSS_ADJUNTOS}</style>`);
const $ = (id) => document.getElementById(id);
const CLAVE = "cc_ia_" + (user?.id ?? "x");   // conversación antigua (antes se guardaba solo en este navegador)
const MAX = 12000;
const TACTIL = matchMedia("(pointer: coarse)").matches;   // en el celular Enter hace salto de línea; se envía con la flecha
const scroll = $("scroll");
const abajo = () => { scroll.scrollTop = scroll.scrollHeight; };
// Alto de la barra de abajo del celular, para que la conversación ocupe justo el resto de la pantalla.
{ const inf = $("inf"); const medir = () => document.documentElement.style.setProperty("--alto-inf", `${inf.offsetHeight || 0}px`); new ResizeObserver(medir).observe(inf); medir(); }
const ICO_COPIAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>';
let actual = null;          // { id, titulo, fijada } o null = conversación nueva (se crea al enviar)
let lista = [];
let mensajes = [];

/** Agrega un mensaje. Devuelve el elemento donde va el texto (para cambiarlo cuando llega la respuesta). */
function burbuja(rol, texto, archivos = [], { pensando = false } = {}) {
  const d = document.createElement("div");
  d.className = `msg ${rol}${pensando ? " pensando" : ""}`;
  let cuerpo = d;
  if (rol === "tutor") {
    d.innerHTML = `<div class="msg-av" aria-hidden="true">${codiSVG("feliz", { tam: 30, animado: false })}</div><div class="msg-cuerpo"></div>
      <div class="msg-acc"><button type="button" class="ia-ico" data-copiar title="Copiar respuesta" aria-label="Copiar respuesta">${ICO_COPIAR}</button></div>`;
    cuerpo = d.querySelector(".msg-cuerpo");
    if (pensando) cuerpo.innerHTML = `<span class="ia-pensando" aria-hidden="true"><i></i><i></i><i></i></span><span class="ia-espera"></span>`, cuerpo.querySelector(".ia-espera").textContent = texto;
    else formato(cuerpo, texto);
  } else d.textContent = texto;
  if (archivos.length) d.insertAdjacentHTML("beforeend", `<div class="ia-adj">${archivos.map((a) => (a.vista ? `<img src="${esc(a.vista)}" alt="${esc(a.nombre)}">` : `<span>📄 ${esc(a.nombre)}</span>`)).join("")}</div>`);
  $("log").appendChild(d);
  abajo();
  return cuerpo;
}
$("log").addEventListener("click", (e) => {
  const b = e.target.closest("[data-copiar]");
  if (!b) return;
  const texto = b.closest(".msg").querySelector(".msg-cuerpo").innerText;
  navigator.clipboard?.writeText(texto).then(() => aviso("Respuesta copiada")).catch(() => aviso("No se pudo copiar", true));
});
function vacia(si) { $("ia").classList.toggle("vacia", si); }
function pintarHistorial() {
  $("log").replaceChildren();
  mensajes.forEach((m) => burbuja(m.rol, m.texto, (m.archivos || []).map((n) => ({ nombre: n }))));
  vacia(!mensajes.length);
  $("tituloConv").textContent = actual?.titulo || "Conversación nueva";
  $("cabBtns").hidden = !actual;
  $("masConv").hidden = !actual;
  abajo();
}
{
  const nombre = (user?.nombre || "").split(" ")[0];
  $("saludo").textContent = `¿En qué te ayudo hoy${nombre ? `, ${nombre}` : ""}?`;
  $("saludoSub").textContent = prog.curso_actual ? `Soy tu tutor de ${prog.curso_actual.nombre}. Pregunta, pega tu código o adjunta una captura.` : "Pregunta lo que quieras, pega tu código o adjunta una captura.";
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
  cerrarLista();
  if (!TACTIL) $("q").focus();
}
function nuevaConv() {
  actual = null; mensajes = [];
  history.replaceState(null, "", location.pathname);
  pintarHistorial(); pintarLista();
  cerrarLista();
  if (!TACTIL) $("q").focus();
}
function cerrarLista() { $("iaLista").classList.remove("abierta"); $("velo").hidden = true; $("verLista").setAttribute("aria-expanded", "false"); }
$("convs").onclick = (e) => { const b = e.target.closest("[data-id]"); if (b) abrirConv(Number(b.dataset.id)); };
let tBuscar = 0;
$("buscarConv").oninput = () => { clearTimeout(tBuscar); tBuscar = setTimeout(cargarLista, 250); };
$("verLista").onclick = () => { $("iaLista").classList.add("abierta"); $("velo").hidden = false; $("verLista").setAttribute("aria-expanded", "true"); };
$("velo").onclick = cerrarLista;
$("cerrarLista").onclick = cerrarLista;
$("nuevaCab").onclick = () => nuevaConv();
addEventListener("keydown", (e) => { if (e.key === "Escape") cerrarLista(); });
$("masConv").onclick = (e) => { e.stopPropagation(); const a = $("cabBtns").classList.toggle("abierto"); $("masConv").setAttribute("aria-expanded", String(a)); };
addEventListener("click", (e) => { if (!e.target.closest("#cabBtns")) { $("cabBtns").classList.remove("abierto"); $("masConv").setAttribute("aria-expanded", "false"); } });
$("cabBtns").onclick = async (e) => {
  const b = e.target.closest("[data-conv]");
  if (!b || !actual) return;
  $("cabBtns").classList.remove("abierto");
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
// ?q=… (por ejemplo desde «¿Por qué?» de un reto): deja la pregunta escrita para enviarla
{ const q = new URLSearchParams(location.search).get("q"); if (q) { const t = document.getElementById("q"); t.value = q.slice(0, 4000); t.dispatchEvent(new Event("input")); t.focus(); } }

/* ===== Sugerencias según el curso ===== */
const curso = prog.curso_actual?.nombre;
const SUG = [curso ? `Explícame lo más importante de ${curso}` : "Explícame qué es una variable", "Revisa mi código", "Dame un ejercicio fácil", "¿Qué error es este y cómo lo arreglo?", "Explícame esta captura de pantalla", "¿Cómo conecto mi app con MySQL de XAMPP?"];
$("sug").innerHTML = SUG.map(() => `<button type="button"></button>`).join("");
$("sug").querySelectorAll("button").forEach((b, i) => { b.textContent = SUG[i]; });
$("sug").onclick = (e) => { if (e.target.matches("button")) { $("q").value = e.target.textContent; actualizar(); $("q").focus(); } };

/* ===== Escribir y enviar ===== */
function actualizar() {
  const q = $("q");
  q.style.height = "auto";
  q.style.height = `${Math.min(q.scrollHeight, 220)}px`;
  const n = q.value.length;
  $("cuenta").hidden = n < MAX * 0.8;
  $("cuenta").textContent = `${n} / ${MAX}`;
  $("cuenta").classList.toggle("casi", n >= MAX * 0.95);
  $("enviar").disabled = enviando || (!q.value.trim() && !adj?.hay());
}
let enviando = false;
let adj = null;
$("q").oninput = actualizar;
$("q").placeholder = TACTIL ? "Escribe tu pregunta…" : "Escribe tu pregunta… (Enter envía · Shift + Enter, salto de línea)";
$("codigo").onclick = () => { const q = $("q"); q.setRangeText("```\n\n```", q.selectionStart, q.selectionEnd, "end"); q.setSelectionRange(q.selectionEnd - 4, q.selectionEnd - 4); q.focus(); actualizar(); };
$("nueva").onclick = nuevaConv;
$("q").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey && !TACTIL && !e.isComposing) { e.preventDefault(); $("f").requestSubmit(); } };
adj = crearAdjuntador({ boton: $("clip"), entrada: $("archivosIa"), bandeja: $("bandeja"), zona: $("ia"), destino: "ia" });
new MutationObserver(actualizar).observe($("bandeja"), { childList: true });
$("f").onsubmit = async (e) => {
  e.preventDefault();
  const t = $("q").value.trim();
  if ((!t && !adj.hay()) || enviando) return;
  enviando = true; actualizar();
  let adjuntos = [];
  const archivos = adj.adjuntos();
  try { adjuntos = await adj.listos(); } catch (x) { aviso(x.message, true); enviando = false; actualizar(); return; }
  $("q").value = ""; actualizar();
  vacia(false);
  burbuja("yo", t || "(archivos)", adj.adjuntos());
  adj.limpiar();
  sonar("enviar");
  const espera = burbuja("tutor", adjuntos.length ? "Revisando tus archivos…" : "", [], { pensando: true });
  try {
    const r = await api("/api/tutor/", { mensaje: t, adjuntos, ...(actual ? { conversacion_id: actual.id } : { guardar: true }), contexto: { pagina: "IA" } });
    espera.closest(".msg").classList.remove("pensando");
    formato(espera, r.respuesta);
    sonar("ia");
    mensajes.push({ rol: "yo", texto: t || "(archivos)", archivos: archivos.map((a) => a.nombre) }, { rol: "tutor", texto: r.respuesta });
    if (r.conversacion) {
      const nueva = !actual;
      actual = { id: r.conversacion.id, titulo: r.conversacion.titulo, fijada: actual?.fijada || false };
      if (nueva) history.replaceState(null, "", `?c=${actual.id}`);
      $("tituloConv").textContent = actual.titulo; $("cabBtns").hidden = false; $("masConv").hidden = false;
      cargarLista();
    }
  } catch (x) {
    espera.closest(".msg").classList.remove("pensando");
    espera.textContent = x.message; espera.classList.add("error");
    $("q").value = t;                 // no pierdes lo que escribiste
  }
  enviando = false; actualizar(); abajo();
  if (!TACTIL) $("q").focus();
};
actualizar();

// Codi en vivo en la bienvenida (con el accesorio que tenga puesto)
{ const c = document.getElementById("iaCodi"); if (c) c.innerHTML = codiSVG("saludo", { tam: 110 }); }
