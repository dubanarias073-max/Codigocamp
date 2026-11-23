// Instalar CódigoCamp como app (Windows, macOS, Linux, ChromeOS, Android, iPhone/iPad) y registrar el service worker.
let aviso = null;
let instalada = matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;

if ("serviceWorker" in navigator && location.protocol !== "file:") {
  // Cuando una versión nueva de CódigoCamp toma el control, se recarga una vez: así nunca se mezclan archivos
  // de dos versiones (la causa típica de una página que se queda «cargando» tras una actualización).
  const habiaControl = Boolean(navigator.serviceWorker.controller);
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!habiaControl) return;
    try { if (sessionStorage.getItem("cc_recargado_sw")) return; sessionStorage.setItem("cc_recargado_sw", "1"); } catch { /* nada */ }
    location.reload();
  });
  addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).then(async (reg) => {
      // Mantiene fresco el widget de racha (si el navegador lo permite).
      try { if (reg.periodicSync) await reg.periodicSync.register("widget-racha", { minInterval: 30 * 60 * 1000 }); } catch { /* sin permiso */ }
      reg.active?.postMessage("actualizar-widget");
    }).catch(() => { /* sin service worker: la página funciona igual */ });
  });
}

addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  aviso = e;
  dispatchEvent(new Event("cc-instalable"));
});
addEventListener("appinstalled", () => { instalada = true; aviso = null; dispatchEvent(new Event("cc-instalable")); });

const ua = navigator.userAgent;
const esIOS = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
const esSafariMac = /Macintosh/.test(ua) && /Safari/.test(ua) && !/Chrome|Chromium|Edg|Firefox/.test(ua);
const esFirefox = /Firefox/.test(ua);

/** Sin HTTPS ningún sistema deja instalar la app (solo funciona en https:// o en localhost). */
export const sinHttps = () => typeof isSecureContext !== "undefined" && !isSecureContext;

export function estadoInstalacion() {
  if (instalada) return { instalada: true, puede: false };
  if (aviso) return { puede: true };
  if (sinHttps()) return { puede: false, https: true, ayuda: `⚠️ Estás entrando por <b>${location.protocol}//${location.host}</b> (sin candado 🔒). Windows, Android, iPhone y Mac <b>solo instalan apps desde una dirección https://</b>. Quien administra CódigoCamp debe publicarlo con HTTPS (un dominio con certificado, o un túnel como <i>Cloudflare Tunnel</i> o <i>ngrok</i>); después de eso aparece el botón Instalar en todos los dispositivos.` };
  let ayuda;
  if (esIOS) ayuda = "En iPhone/iPad (Safari): toca <b>Compartir</b> <span aria-hidden=\"true\">⬆️</span> y luego <b>Agregar a pantalla de inicio</b>.";
  else if (esSafariMac) ayuda = "En Safari para Mac: menú <b>Archivo → Agregar al Dock</b>.";
  else if (esFirefox && /Android/.test(ua)) ayuda = "En Firefox para Android: menú <b>⋮ → Instalar</b>.";
  else if (esFirefox) ayuda = "Firefox de computador no instala apps web: abre CódigoCamp en Chrome o Edge y pulsa el ícono de instalar de la barra de direcciones.";
  else ayuda = "Busca el ícono <b>Instalar</b> (⊕) en la barra de direcciones, o el menú <b>⋮ → Instalar CódigoCamp</b> / <b>Agregar a la pantalla principal</b>. Si no aparece, recarga la página.";
  return { puede: false, ayuda };
}

export async function instalar() {
  if (!aviso) return false;
  aviso.prompt();
  const { outcome } = await aviso.userChoice;
  aviso = null;
  if (outcome === "accepted") instalada = true;
  return outcome === "accepted";
}
