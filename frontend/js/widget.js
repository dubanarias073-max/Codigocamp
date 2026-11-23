// pages/widget.html: el widget de CódigoCamp en cualquier sistema.
//  · Con la sesión de CódigoCamp (misma página) o con el enlace privado ?t=… (apps de widgets, otros navegadores).
//  · 📌 «Widget flotante»: ventana pequeña siempre encima (Chrome/Edge en Windows, macOS, Linux y ChromeOS).
//  · Se actualiza solo cada 5 minutos y al volver a la ventana.
// Referencias guardadas: en el widget flotante los elementos se mudan a otra ventana y getElementById ya no los vería.
const nodos = {};
const $ = (id) => (nodos[id] ??= document.getElementById(id));
["wg", "cuerpo", "vidas", "practicar", "hora", "flotar", "recargar"].forEach($);
const q = new URLSearchParams(location.search);
// Con la sesión del navegador (cookie) no hace falta token; ?t=… solo lo usan las apps de widgets.
const token = q.get("t") || "";
if (q.get("tema") !== "oscuro") document.documentElement.classList.add("auto");
const VISTAS_OK = ["racha", "reloj", "hoy", "reto", "calendario"];
let vista = VISTAS_OK.includes(q.get("w")) ? q.get("w") : q.get("w") === "meta" ? "hoy" : (() => { try { const v = localStorage.getItem("cc-widget-vista"); return VISTAS_OK.includes(v) ? v : "racha"; } catch { return "racha"; } })();
let datos = null;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function cargar() {
  $("recargar").disabled = true;
  try {
    const r = await fetch(`/api/widget/${token ? `?t=${encodeURIComponent(token)}` : ""}`, { credentials: token ? "omit" : "same-origin", cache: "no-store", headers: { "X-Zona-Horaria": Intl.DateTimeFormat().resolvedOptions().timeZone || "" } });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(d.error || `Error ${r.status}`), { estado: r.status });
    datos = d;
    try { localStorage.setItem("cc-widget-ultimo", JSON.stringify(d)); } catch { /* nada */ }
    pintar();
  } catch (e) {
    if (!datos) { try { datos = JSON.parse(localStorage.getItem("cc-widget-ultimo") || "null"); } catch { /* nada */ } }
    if (datos && e.estado !== 401) { pintar(); $("hora").textContent = `Sin conexión · ${datos.actualizado || ""}`; }
    else $("cuerpo").innerHTML = `<p class="wg-error">${e.estado === 401
      ? "Tu sesión se cerró. <a href=\"/pages/login.html\" target=\"_blank\">Inicia sesión en CódigoCamp</a> y este widget vuelve a funcionar."
      : `No se pudo cargar: ${esc(e.message)}`}</p>`;
  } finally { $("recargar").disabled = false; }
}

/* ===== Codi, la mascota (js/codi.js): cambia de ánimo según tu racha y la hora (como el búho de Duolingo) ===== */
import { codiSVG, fraseDe } from "/js/codi.js";
const codi = (animo) => codiSVG(animo, { tam: 92 });
const frase = (animo) => fraseDe(animo);
const ccT = (t) => (window.ccT ? window.ccT(t) : t);

const TRES_HORAS = 3 * 3600;
function cuentaAtras(seg, conSegundos = false) {
  seg = Math.max(0, Math.floor(seg));
  const h = Math.floor(seg / 3600), m = Math.floor((seg % 3600) / 60), x = seg % 60;
  return conSegundos ? `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(x).padStart(2, "0")}` : `${h}h ${String(m).padStart(2, "0")}m`;
}
let base = 0, segBase = 0;
const quedan = () => Math.max(0, segBase - (Date.now() - base) / 1000);
setInterval(() => {   // el cronómetro avanza solo cada segundo
  const raiz = $("wg");
  const seg = quedan();
  for (const el of raiz.querySelectorAll("[data-cuenta]")) el.textContent = cuentaAtras(seg, el.dataset.cuenta === "s");
  const urgente = seg <= TRES_HORAS && !datos?.practicado_hoy;
  raiz.classList.toggle("urgente", urgente);
  const barra = raiz.querySelector("[data-dia]");
  if (barra) barra.style.width = `${Math.min(100, (1 - seg / 86400) * 100)}%`;
  if (segBase && seg <= 0) { segBase = 0; cargar(); }   // empezó otro día
}, 1000);

let respondida = null;   // {id, elegida}
function pintar() {
  const d = datos;
  if (!d) return;
  $("wg").dataset.vista = vista;
  $("wg").querySelectorAll(".wg-tabs button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.v === vista)));
  $("vidas").textContent = `❤️ ${d.vidas}  💎 ${d.diamantes}`;
  $("practicar").href = d.url_practicar || "/pages/inicio.html?app=1";
  $("hora").textContent = d.actualizado ? `Actualizado ${d.actualizado}` : "";
  const clase = d.practicado_hoy ? "ok" : d.racha ? "peligro" : "";
  const animo = d.animo || (d.practicado_hoy ? "feliz" : d.racha ? "preocupado" : "dormido");
  const semana = `<div class="wg-semana">${(d.semana || []).map((s, i) => `<span class="${s.hoy ? "hoy" : ""} ${s.estado || ""}">${esc(s.letra)}<i>${s.estado === "hecho" ? "🔥" : esc(s.icono)}</i></span>`).join("")}</div>`;
  base = Date.now(); segBase = d.segundos_restantes || 0;
  let html;
  if (vista === "hoy") {
    const enc = d.encargos || [];
    html = `<div class="wg-meta"><span>🎯 <b>${d.xp_hoy}</b> / ${d.meta_xp} XP</span><small>${d.progreso_hoy}%</small></div>
      <div class="wg-barra" role="progressbar" aria-valuenow="${d.progreso_hoy}" aria-valuemin="0" aria-valuemax="100"><i style="width:${d.progreso_hoy}%"></i></div>
      <ul class="wg-encargos">${enc.map((e) => `<li class="${e.completado ? "listo" : ""}"><span class="wg-check">${e.completado ? "✓" : ""}</span><span class="wg-et">${esc(e.titulo)}</span><small>${e.progreso}/${e.meta}</small></li>`).join("")}</ul>
      <a class="wg-mas" href="${esc(d.url_cofres || "/pages/recompensas.html")}" target="_blank" rel="noopener">${d.encargos_hechos || 0}/${enc.length} encargos · Ver cofres →</a>`;
  } else if (vista === "reto") {
    const p = d.pregunta;
    if (!p) html = `<p class="wg-sub">Elige un curso en CódigoCamp para tener retos rápidos aquí.</p>`;
    else {
      const r = respondida?.id === p.id ? respondida : null;
      html = `<p class="wg-preg">${esc(p.enunciado)}</p>${p.codigo ? `<pre class="wg-cod">${esc(p.codigo)}</pre>` : ""}
        <div class="wg-ops">${p.opciones.map((o, i) => `<button type="button" data-op="${i}" ${r ? "disabled" : ""} class="${r ? (o === p.respuesta ? "bien" : r.elegida === i ? "mal" : "") : ""}">${esc(o)}</button>`).join("")}</div>
        ${r ? `<p class="wg-fb ${p.opciones[r.elegida] === p.respuesta ? "ok" : "no"}">${p.opciones[r.elegida] === p.respuesta ? "✅ ¡Correcto!" : "❌ Casi"}${p.explicacion ? " · " + esc(p.explicacion) : ""}</p>` : `<p class="wg-sub">Reto rápido de repaso · cambia cada 30 min</p>`}`;
    }
  } else if (vista === "reloj") {
    const seg = segBase;
    const urg = seg <= TRES_HORAS && !d.practicado_hoy;
    const titulo = d.practicado_hoy ? "Tu racha está a salvo hoy" : d.racha ? `Te quedan para salvar tu racha de ${d.racha}` : "Te quedan para empezar tu racha";
    html = `<div class="wg-reloj ${d.practicado_hoy ? "ok" : urg ? "rojo" : ""}">
        <div class="wg-reloj-codi">${codi(d.practicado_hoy ? (d.racha >= 7 ? "fuego" : "feliz") : urg ? "alarma" : d.racha ? "preocupado" : "dormido")}</div>
        <div><small>${esc(titulo)}</small><b class="wg-reloj-num" data-cuenta="s">${cuentaAtras(seg, true)}</b>
        <div class="wg-reloj-barra"><i data-dia style="width:${Math.min(100, (1 - seg / 86400) * 100)}%"></i></div>
        <small class="wg-reloj-pie">${d.practicado_hoy ? "✅ Ya practicaste hoy. Mañana empieza otro día." : urg ? "🔴 ¡Menos de 3 horas! Haz una lección ya." : "⏳ El día termina a medianoche (tu hora)."}</small></div></div>`;
  } else if (vista === "calendario") {
    html = `${semana}<p class="wg-sub">Mejor racha: <b>${d.racha_maxima}</b> días · 🧊 ${d.salvarrachas} salvarrachas</p>`;
  } else {
    const peligro = !d.practicado_hoy && d.racha > 0;
    html = `<div class="wg-codi">${codi(animo)}<div class="wg-globo"><b class="wg-num">${d.racha}<small> ${d.racha === 1 ? "día de racha" : "días de racha"}</small></b>
      <span>${esc(frase(animo))}</span>${peligro ? `<span class="wg-cuenta ${segBase <= TRES_HORAS ? "rojo" : ""}">⏳ <b data-cuenta>${cuentaAtras(segBase)}</b> para salvarla</span>` : ""}</div></div>${semana}`;
  }
  $("wg").classList.toggle("urgente", segBase <= TRES_HORAS && !d.practicado_hoy);
  $("cuerpo").innerHTML = vista === "racha" || vista === "reto" || vista === "reloj" ? html : `${html}<p class="wg-estado ${clase}">${esc(d.estado)}</p>`;
}

$("cuerpo").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-op]");
  if (!b || !datos?.pregunta) return;
  const p = datos.pregunta, i = Number(b.dataset.op);
  respondida = { id: p.id, elegida: i };
  const bien = p.opciones[i] === p.respuesta;
  try { const { sonar } = await import("/js/sonidos.js"); sonar(bien ? "correcto" : "incorrecto"); } catch { /* sin sonido */ }
  try { navigator.vibrate?.(bien ? 30 : [40, 60, 40]); } catch { /* nada */ }
  pintar();
});

const VISTAS = VISTAS_OK;
const cambiarVista = (v) => { vista = v; try { localStorage.setItem("cc-widget-vista", vista); } catch { /* nada */ } pintar(); };
$("wg").querySelector(".wg-tabs").addEventListener("click", (e) => {
  const b = e.target.closest("[data-v]");
  if (b) cambiarVista(b.dataset.v);
});
// Deslizar con el dedo (o flechas del teclado) para cambiar de vista
let x0 = null;
$("cuerpo").addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
$("cuerpo").addEventListener("touchend", (e) => {
  if (x0 == null) return;
  const dx = e.changedTouches[0].clientX - x0; x0 = null;
  if (Math.abs(dx) < 45) return;
  const i = VISTAS.indexOf(vista);
  cambiarVista(VISTAS[(i + (dx < 0 ? 1 : VISTAS.length - 1)) % VISTAS.length]);
}, { passive: true });
addEventListener("keydown", (e) => {
  if (e.key !== "ArrowRight" && e.key !== "ArrowLeft" || e.target.closest?.("input,textarea")) return;
  const i = VISTAS.indexOf(vista);
  cambiarVista(VISTAS[(i + (e.key === "ArrowRight" ? 1 : VISTAS.length - 1)) % VISTAS.length]);
});
$("recargar").onclick = cargar;
addEventListener("visibilitychange", () => { if (!document.hidden) cargar(); });
setInterval(cargar, 5 * 60 * 1000);

// ---- 📌 widget flotante (siempre encima) ----
const enVentanaPropia = q.get("mini") === "1" || window.opener || matchMedia("(display-mode: standalone)").matches;
if ("documentPictureInPicture" in window || !enVentanaPropia) $("flotar").hidden = false;
$("flotar").onclick = async () => {
  if ("documentPictureInPicture" in window) {
    try {
      const pip = await documentPictureInPicture.requestWindow({ width: 360, height: 290 });
      for (const hoja of document.styleSheets) {
        try { const s = pip.document.createElement("style"); s.textContent = [...hoja.cssRules].map((r) => r.cssText).join("\n"); pip.document.head.append(s); }
        catch { const l = pip.document.createElement("link"); l.rel = "stylesheet"; l.href = hoja.href; pip.document.head.append(l); }
      }
      pip.document.documentElement.className = document.documentElement.className;
      const raiz = $("wg");
      pip.document.body.append(raiz);
      $("flotar").hidden = true;
      pip.addEventListener("pagehide", () => { document.body.append(raiz); $("flotar").hidden = false; });
      return;
    } catch { /* sin permiso: ventana normal */ }
  }
  const url = new URL(location.href);
  url.searchParams.set("mini", "1");
  window.open(url, "cc-widget", "popup=yes,width=370,height=310");
};

pintar();
cargar();
