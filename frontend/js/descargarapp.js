// Botón «Descargar la app para Android» en la portada (index.html: cabecera y bajo los botones principales). Solo aparece si el APK está en
// frontend/descargas/CodigoCamp.apk y si NO estás ya dentro de la app.
const enApp = () => !!window.CodigoCampApp || /CodigoCampApp\//.test(navigator.userAgent);
const esAndroid = /Android/i.test(navigator.userAgent);
const esIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
const mb = (n) => (n / 1048576).toFixed(1).replace(".", ",");
const ROBOT = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M17.6 9.48l1.84-3.18a.38.38 0 0 0-.66-.38l-1.86 3.22a11.4 11.4 0 0 0-9.84 0L5.22 5.92a.38.38 0 0 0-.66.38L6.4 9.48A10.8 10.8 0 0 0 1 18h22a10.8 10.8 0 0 0-5.4-8.52zM7 15.25a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5zm10 0a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5z"/></svg>';

export async function montarBotonApp(contenedor, { compacto = false, barra = false } = {}) {
  if (!contenedor || enApp()) return;
  const CERRADA = "cc_barra_app_cerrada";
  if (barra) { try { if (localStorage.getItem(CERRADA) === "1") return; } catch { /* nada */ } }
  let info;
  try { info = await (await fetch("/api/app/", { cache: "no-cache" })).json(); } catch { return; }
  if (barra) {   // franja fina bajo la cabecera de Inicio, con ✕ para no volver a verla
    if (!info?.android) return;
    contenedor.innerHTML = `<a class="barra-app" href="${info.url}?v=${info.version}" download="CodigoCamp.apk">${ROBOT}<span><b>Descarga la app para Android</b> · con widget de racha</span></a><button type="button" class="barra-app-x" aria-label="No mostrar más">✕</button>`;
    contenedor.querySelector(".barra-app-x").onclick = () => { contenedor.hidden = true; try { localStorage.setItem(CERRADA, "1"); } catch { /* nada */ } };
    contenedor.hidden = false;
    return;
  }
  if (!info?.android) {
    if (esIOS && !compacto) contenedor.innerHTML = '<p class="app-ios">📱 En iPhone: abre esta página en Safari → <b>Compartir</b> → <b>Agregar a inicio</b>.</p>';
    return;
  }
  contenedor.innerHTML = `<a class="btn-app${esAndroid ? " destacado" : ""}${compacto ? " compacto" : ""}" href="${info.url}?v=${info.version}" download="CodigoCamp.apk">
      ${ROBOT}<span><b>Descargar la app para Android</b><small>CódigoCamp + widget de racha · ${mb(info.tam)} MB</small></span></a>
    ${compacto ? "" : `<details class="app-ayuda"><summary>¿Cómo se instala?</summary><ol>
      <li>Descarga <b>CodigoCamp.apk</b> y ábrelo (en Descargas o en la notificación).</li>
      <li>Si Android pregunta, permite <b>instalar apps de esta fuente</b> (es seguro: no viene de la Play Store).</li>
      <li>Abre CódigoCamp e inicia sesión. Para el widget: mantén pulsada la pantalla de inicio → <b>Widgets</b> → <b>CódigoCamp</b>.</li>
      <li>¿Tenías «CódigoCamp Widget»? Desinstálalo: ahora todo viene en esta app.</li></ol></details>`}`;
  contenedor.hidden = false;
}

export async function montarCabecera(el) {
  if (!el || enApp()) return;
  let info;
  try { info = await (await fetch("/api/app/", { cache: "no-cache" })).json(); } catch { return; }
  if (!info?.android) return;
  el.innerHTML = `<a class="app-cab" href="#app" title="Descargar la app para Android">${ROBOT}<span>App</span></a>`;
  el.querySelector("a").onclick = (e) => { e.preventDefault(); const d = document.getElementById("app"); d?.scrollIntoView({ behavior: "smooth", block: "center" }); d?.querySelector(".btn-app")?.focus(); };
  el.hidden = false;
}

for (const el of document.querySelectorAll("[data-descargar-app]")) {
  const modo = el.dataset.descargarApp;
  if (modo === "cabecera") montarCabecera(el);
  else montarBotonApp(el, { compacto: modo === "compacto", barra: modo === "barra" });
}
