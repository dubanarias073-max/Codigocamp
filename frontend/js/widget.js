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
let vista = ["racha", "hoy", "reto", "calendario"].includes(q.get("w")) ? q.get("w") : q.get("w") === "meta" ? "hoy" : (() => { try { const v = localStorage.getItem("cc-widget-vista"); return ["racha", "hoy", "reto", "calendario"].includes(v) ? v : "racha"; } catch { return "racha"; } })();
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

/* ===== Codi, la mascota: cambia de ánimo según tu racha (como el búho de Duolingo) ===== */
const FRASES = {
  feliz: ["¡Bien hecho! Tu racha está a salvo 💪", "¡Hoy cumpliste! Nos vemos mañana", "¡Qué crack! Ya practicaste hoy"],
  fuego: ["¡Estás en llamas! 🔥", "¡Racha imparable! Sigue así", "Nadie te para 🚀"],
  preocupado: ["¿Practicamos un ratito hoy?", "Tu racha te está esperando 👀", "5 minutos y listo, ¿vamos?"],
  alarma: ["¡Tu racha está en peligro! 😱", "¡Corre! Se acaba el día", "¡No dejes que se apague tu racha!"],
  dormido: ["Zzz… despiértame con una lección", "Empieza una racha hoy ✨", "¿Hoy empezamos? Yo te acompaño"],
};
function codi(animo) {
  const ojos = animo === "dormido" ? `<path d="M30 46q5 4 10 0M56 46q5 4 10 0" class="cd-linea"/>`
    : animo === "alarma" ? `<circle cx="35" cy="45" r="6" class="cd-ojo"/><circle cx="61" cy="45" r="6" class="cd-ojo"/><circle cx="35" cy="45" r="2.5" class="cd-pupila"/><circle cx="61" cy="45" r="2.5" class="cd-pupila"/>`
    : `<circle cx="35" cy="45" r="5" class="cd-ojo"/><circle cx="61" cy="45" r="5" class="cd-ojo"/><circle cx="36.5" cy="44" r="2.2" class="cd-pupila"/><circle cx="62.5" cy="44" r="2.2" class="cd-pupila"/>`;
  const boca = { feliz: `<path d="M38 60q10 10 20 0" class="cd-linea"/>`, fuego: `<path d="M36 58q12 14 24 0z" class="cd-boca"/>`,
    preocupado: `<path d="M39 64q9-6 18 0" class="cd-linea"/>`, alarma: `<ellipse cx="48" cy="63" rx="6" ry="7" class="cd-boca"/>`, dormido: `<path d="M42 62h12" class="cd-linea"/>` }[animo];
  const extra = { fuego: `<path class="cd-llama" d="M48 2c8 10 14 14 10 24-2 5-7 7-10 7s-9-2-11-8c-2-7 3-11 5-15 1 4 3 6 5 6-2-5-1-9 1-14z"/>`,
    dormido: `<text x="74" y="20" class="cd-z">z</text><text x="82" y="10" class="cd-z cd-z2">z</text>`,
    preocupado: `<path class="cd-gota" d="M78 30c3 5 4 7 4 9a4 4 0 0 1-8 0c0-2 1-4 4-9z"/>`,
    alarma: `<text x="76" y="24" class="cd-excl">!</text>`, feliz: `<path class="cd-brillo" d="M80 18l2 5 5 2-5 2-2 5-2-5-5-2 5-2z"/>` }[animo];
  return `<svg class="codi cd-${animo}" viewBox="0 0 96 96" aria-hidden="true">${extra}
    <rect x="14" y="20" width="68" height="62" rx="26" class="cd-cuerpo"/><path d="M14 52h-6M82 52h6" class="cd-linea"/>
    <text x="48" y="31" class="cd-tag">&lt;/&gt;</text>${ojos}${boca}
    <ellipse cx="27" cy="57" rx="5" ry="3" class="cd-mejilla"/><ellipse cx="69" cy="57" rx="5" ry="3" class="cd-mejilla"/></svg>`;
}
const frase = (animo) => { const l = FRASES[animo] || FRASES.feliz; return l[Math.floor(Date.now() / 600000) % l.length]; };
const ccT = (t) => (window.ccT ? window.ccT(t) : t);

function cuentaAtras(seg) {
  const h = Math.floor(seg / 3600), m = Math.floor((seg % 3600) / 60);
  return `${h}h ${String(m).padStart(2, "0")}m`;
}
let base = 0, segBase = 0;
setInterval(() => {   // la cuenta atrás avanza sola cada 30 s
  const el = $("wg").querySelector("[data-cuenta]");
  if (el && segBase) el.textContent = cuentaAtras(Math.max(0, segBase - (Date.now() - base) / 1000));
}, 30000);

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
  const semana = `<div class="wg-semana">${(d.semana || []).map((s, i) => `<span class="${s.hoy ? "hoy" : ""} ${s.estado || ""}">${esc(window.CC_IDIOMA === "en" ? "MTWTFSS"[i] : s.letra)}<i>${s.estado === "hecho" ? "🔥" : esc(s.icono)}</i></span>`).join("")}</div>`;
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
  } else if (vista === "calendario") {
    html = `${semana}<p class="wg-sub">Mejor racha: <b>${d.racha_maxima}</b> días · 🧊 ${d.salvarrachas} salvarrachas</p>`;
  } else {
    const peligro = !d.practicado_hoy && d.racha > 0;
    html = `<div class="wg-codi">${codi(animo)}<div class="wg-globo"><b class="wg-num">${d.racha}<small> ${d.racha === 1 ? "día de racha" : "días de racha"}</small></b>
      <span>${esc(frase(animo))}</span>${peligro ? `<span class="wg-cuenta">⏳ <b data-cuenta>${cuentaAtras(segBase)}</b></span>` : ""}</div></div>${semana}`;
  }
  $("cuerpo").innerHTML = vista === "racha" || vista === "reto" ? html : `${html}<p class="wg-estado ${clase}">${esc(d.estado)}</p>`;
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

const VISTAS = ["racha", "hoy", "reto", "calendario"];
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
