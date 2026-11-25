// Enlaces seguros: antes de abrir un enlace externo (de tus páginas en Trabajo, de un chat o de la IA), CódigoCamp
// lo revisa (backend/servicios/seguridad_enlaces.py). Si es de virus o estafa se BLOQUEA y no se puede abrir de
// ninguna forma; si es dudoso, se avisa y decides tú. Los enlaces revisados no se guardan en ninguna parte.
import { api } from "/js/auth.js";

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

export async function revisarEnlace(url) {
  try { return await api("/api/seguridad/enlace", { url }); }
  catch { return { nivel: "advertencia", motivo: "No se pudo revisar este enlace ahora mismo." }; }
}

function ventana({ titulo, html, botones }) {
  return new Promise((resolver) => {
    document.querySelector(".cc-enlace-dlg")?.remove();
    const fondo = document.createElement("div");
    fondo.className = "cc-enlace-dlg";
    fondo.style.cssText = "position:fixed;inset:0;z-index:100000;display:grid;place-items:center;background:rgba(2,6,23,.6);backdrop-filter:blur(3px);padding:16px";
    fondo.innerHTML = `<div role="alertdialog" aria-modal="true" style="width:min(440px,94vw);padding:22px;border-radius:18px;background:var(--panel,#0f172a);color:var(--txt,#e5e7eb);border:1px solid var(--borde,#334155);box-shadow:0 24px 60px rgba(0,0,0,.45);font:15px/1.5 system-ui,sans-serif">
      <h3 style="margin:0 0 8px;font-size:18px">${titulo}</h3>${html}
      <div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap;margin-top:16px">${botones.map(([v, t, p], i) => `<button type="button" data-v="${v}" style="padding:9px 16px;border-radius:10px;font:700 14px system-ui;cursor:pointer;${p === "peligro" ? "background:none;border:1px solid #f59e0b;color:#f59e0b" : i === botones.length - 1 ? "background:#22d3ee;border:0;color:#04131a" : "background:none;border:1px solid var(--borde,#334155);color:inherit"}">${t}</button>`).join("")}</div></div>`;
    const cerrar = (v) => { fondo.remove(); removeEventListener("keydown", tecla, true); resolver(v); };
    const tecla = (e) => { if (e.key === "Escape") { e.stopPropagation(); cerrar("cancelar"); } };
    fondo.addEventListener("click", (e) => { const b = e.target.closest("[data-v]"); if (b) cerrar(b.dataset.v); else if (e.target === fondo) cerrar("cancelar"); });
    addEventListener("keydown", tecla, true);
    document.body.appendChild(fondo);
    fondo.querySelector("button:last-child")?.focus();
  });
}

/**
 * Revisa y, si se puede, abre el enlace en una pestaña nueva.
 * @param {string} url
 * @param {{ abrir?: (url:string) => void }} [o]  cómo abrirlo (por defecto window.open; en la app de Android, abrirFuera)
 * @returns {Promise<boolean>} true si se abrió
 */
/** Abre en una pestaña nueva sin dejarle a esa página acceso a CódigoCamp. false si el navegador la bloqueó. */
export function abrirPestana(x) {
  const w = window.open(x, "_blank");
  if (!w) return false;
  try { w.opener = null; } catch { /* nada */ }
  return true;
}

export async function abrirSeguro(url, { abrir } = {}) {
  let u;
  try { u = new URL(url, location.href); } catch { return false; }
  const href = u.href;
  if (/^(mailto|tel):$/.test(u.protocol)) { location.href = href; return true; }
  const r = await revisarEnlace(href);
  const abrirYa = abrir || ((x) => {
    if (window.CodigoCampApp?.abrirFuera) { try { window.CodigoCampApp.abrirFuera(x); return; } catch { /* sigue */ } }
    // OJO: window.open(…, "noopener") SIEMPRE devuelve null, aunque sí abra la pestaña. Antes eso hacía que además se
    // abriera el enlace en la misma pestaña de CódigoCamp (dos veces). Se abre sin «noopener» y se corta el vínculo.
    if (abrirPestana(x)) return;
    // El navegador bloqueó la ventana nueva: un toque más la abre (nunca se sale de CódigoCamp)
    ventana({ titulo: "Abrir enlace", html: `<p style="margin:0">Tu navegador bloqueó la pestaña nueva. Toca «Abrir» para ir a <b style="word-break:break-all">${esc(new URL(x).hostname)}</b>.</p>`,
      botones: [["abrir", "Abrir ↗"], ["cancelar", "Cancelar"]] }).then((v) => { if (v === "abrir") abrirPestana(x); });
  });
  if (r.nivel === "bloqueado") {
    import("/js/sonidos.js").then((m) => m.sonar("incorrecto")).catch(() => {});
    await ventana({
      titulo: "🛡️ Enlace bloqueado",
      html: `<p style="margin:0 0 8px">CódigoCamp no abrirá <b style="word-break:break-all">${esc(u.hostname || href)}</b> porque puede dañar tu equipo o robar tus datos.</p>
        <p style="margin:0 0 8px;padding:10px 12px;border-radius:10px;background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.4)">${esc(r.motivo)}</p>
        <p style="margin:0;font-size:13px;opacity:.75">Por tu seguridad este bloqueo no se puede saltar. Si te lo envió alguien, no lo abras en otro navegador.</p>`,
      botones: [["ok", "Entendido"]],
    });
    return false;
  }
  if (r.nivel === "advertencia") {
    const v = await ventana({
      titulo: "⚠️ Revisa este enlace",
      html: `<p style="margin:0 0 8px">Vas a abrir <b style="word-break:break-all">${esc(href.length > 120 ? href.slice(0, 120) + "…" : href)}</b></p>
        <p style="margin:0;padding:10px 12px;border-radius:10px;background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.45)">${esc(r.motivo)}</p>`,
      botones: [["abrir", "Abrir de todos modos", "peligro"], ["cancelar", "No abrir"]],
    });
    if (v !== "abrir") return false;
  }
  abrirYa(href);
  return true;
}

/** Todos los enlaces externos de la página pasan por la revisión (chats, IA, perfiles…). */
export function protegerEnlaces(raiz = document) {
  raiz.addEventListener("click", (e) => {
    if (e.defaultPrevented || e.button > 1) return;
    const a = e.target.closest?.("a[href]");
    if (!a || a.hasAttribute("download") || a.dataset.sinRevisar !== undefined) return;
    let u;
    try { u = new URL(a.getAttribute("href"), location.href); } catch { return; }
    if (!/^https?:$/.test(u.protocol) || u.origin === location.origin) return;
    e.preventDefault();
    abrirSeguro(u.href);
  }, true);
}
