// "react-native" dentro de Aprende: react-native-web + lo que en la web no existe (Alert real y Share).
// Se carga como módulo en el celular simulado de Aprende (ver aprende-rn.js).
export * from "rnw";
import * as RN from "rnw";

function dialogo(titulo, mensaje, botones) {
  const fondo = document.createElement("div");
  fondo.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:99999";
  const caja = document.createElement("div");
  caja.style.cssText = "background:#fff;color:#111;border-radius:14px;min-width:240px;max-width:82%;font-family:system-ui,sans-serif;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.3)";
  const t = document.createElement("div");
  t.style.cssText = "padding:16px 16px 4px;font-weight:700;text-align:center";
  t.textContent = titulo ?? "";
  const m = document.createElement("div");
  m.style.cssText = "padding:0 16px 14px;font-size:14px;text-align:center;color:#444";
  m.textContent = mensaje ?? "";
  const fila = document.createElement("div");
  fila.style.cssText = "display:flex;border-top:1px solid #e5e7eb";
  (botones?.length ? botones : [{ text: "OK" }]).forEach((b, i) => {
    const x = document.createElement("button");
    x.textContent = b.text ?? "OK";
    x.style.cssText = "flex:1;padding:12px;border:0;background:none;font-size:15px;cursor:pointer;" +
      (i ? "border-left:1px solid #e5e7eb;" : "") +
      (b.style === "destructive" ? "color:#dc2626;" : b.style === "cancel" ? "font-weight:700;color:#2563eb;" : "color:#2563eb;");
    x.onclick = () => { fondo.remove(); b.onPress?.(); };
    fila.appendChild(x);
  });
  caja.append(t, m, fila);
  fondo.appendChild(caja);
  document.body.appendChild(fondo);
}

export const Alert = {
  alert: (titulo, mensaje, botones) => dialogo(titulo, mensaje, botones),
  prompt: (titulo, mensaje, alAceptar) => { const r = window.prompt?.(`${titulo}\n${mensaje ?? ""}`); if (r != null) alAceptar?.(r); },
};

export const Share = {
  share: async ({ message, url, title } = {}) => {
    const texto = [message, url].filter(Boolean).join(" ");
    console.log("📤 Compartir: " + texto);
    try { if (navigator.share) await navigator.share({ title, text: message, url }); } catch { /* el usuario canceló */ }
    return { action: "sharedAction" };
  },
  sharedAction: "sharedAction",
  dismissedAction: "dismissedAction",
};

export const Linking = {
  ...RN.Linking,
  openURL: async (url) => { console.log("🔗 Abrir: " + url); if (/^https?:/.test(url)) window.open(url, "_blank"); return true; },
  canOpenURL: async () => true,
};

export const Vibration = { vibrate: (p) => { console.log("📳 Vibración"); try { navigator.vibrate?.(p ?? 300); } catch {} }, cancel: () => {} };
