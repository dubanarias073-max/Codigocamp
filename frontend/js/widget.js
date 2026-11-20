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
let vista = ["racha", "meta", "calendario"].includes(q.get("w")) ? q.get("w") : (() => { try { return localStorage.getItem("cc-widget-vista") || "racha"; } catch { return "racha"; } })();
let datos = null;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function cargar() {
  $("recargar").disabled = true;
  try {
    const r = await fetch(`/api/widget/${token ? `?t=${encodeURIComponent(token)}` : ""}`, { credentials: token ? "omit" : "same-origin", cache: "no-store" });
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

function pintar() {
  const d = datos;
  if (!d) return;
  $("wg").querySelectorAll(".wg-tabs button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.v === vista)));
  $("vidas").textContent = `❤️ ${d.vidas}  💎 ${d.diamantes}`;
  $("practicar").href = d.url_practicar || "/pages/inicio.html?app=1";
  $("hora").textContent = d.actualizado ? `Actualizado ${d.actualizado}` : "";
  const clase = d.practicado_hoy ? "ok" : d.racha ? "peligro" : "";
  const semana = `<div class="wg-semana">${(d.semana || []).map((s) => `<span class="${s.hoy ? "hoy" : ""}">${esc(s.letra)}<i>${esc(s.icono)}</i></span>`).join("")}</div>`;
  let html;
  if (vista === "meta") {
    html = `<div class="wg-grande"><span class="ic">🎯</span><div><b style="color:var(--txt)">${d.xp_hoy}<span style="font-size:.5em;color:var(--sub)"> / ${d.meta_xp} XP</span></b><small>${d.progreso_hoy}% de tu meta de hoy · 🔥 ${d.racha}</small></div></div>
      <div class="wg-barra" role="progressbar" aria-valuenow="${d.progreso_hoy}" aria-valuemin="0" aria-valuemax="100"><i style="width:${d.progreso_hoy}%"></i></div>`;
  } else if (vista === "calendario") {
    html = `${semana}<p class="wg-sub">Mejor racha: <b>${d.racha_maxima}</b> días · 🧊 ${d.salvarrachas} salvarrachas</p>`;
  } else {
    html = `<div class="wg-grande"><span class="ic">🔥</span><div><b>${d.racha}</b><small>${d.racha === 1 ? "día de racha" : "días de racha"}</small></div></div>${semana}`;
  }
  $("cuerpo").innerHTML = `${html}<p class="wg-estado ${clase}">${esc(d.estado)}</p>`;
}

$("wg").querySelector(".wg-tabs").addEventListener("click", (e) => {
  const b = e.target.closest("[data-v]");
  if (!b) return;
  vista = b.dataset.v;
  try { localStorage.setItem("cc-widget-vista", vista); } catch { /* nada */ }
  pintar();
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
      const pip = await documentPictureInPicture.requestWindow({ width: 330, height: 210 });
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
  window.open(url, "cc-widget", "popup=yes,width=340,height=230");
};

pintar();
cargar();
