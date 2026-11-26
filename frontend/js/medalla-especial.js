// Medallas especiales diseñadas en el panel de administrador: forma, metal, colores, centro (emoji o imagen/GIF),
// cinta, letrero, estrellas y animación. Se dibujan igual en el panel y en el perfil del estudiante.

const METALES = {
  oro: ["#fff7c2", "#fbbf24", "#92400e"], plata: ["#ffffff", "#cbd5e1", "#475569"], bronce: ["#fde2c4", "#d97706", "#7c2d12"],
  diamante: ["#ecfeff", "#67e8f9", "#0e7490"], esmeralda: ["#d1fae5", "#10b981", "#064e3b"], rubi: ["#ffe4e6", "#f43f5e", "#881337"],
  obsidiana: ["#94a3b8", "#1e293b", "#020617"],
};
export const FORMAS_MEDALLA = [["circulo", "Círculo"], ["escudo", "Escudo"], ["estrella", "Estrella"], ["hexagono", "Hexágono"], ["rombo", "Diamante"],
  ["engranaje", "Engranaje"], ["corona", "Corona"], ["flor", "Flor"]];
export const METALES_MEDALLA = [["oro", "🥇 Oro"], ["plata", "🥈 Plata"], ["bronce", "🥉 Bronce"], ["diamante", "💎 Diamante"], ["esmeralda", "💚 Esmeralda"],
  ["rubi", "❤️ Rubí"], ["obsidiana", "🖤 Obsidiana"], ["arcoiris", "🌈 Arcoíris"], ["personal", "🎨 Mis colores"]];
export const ANIM_MEDALLA = [["ninguna", "Quieta"], ["brillo", "✨ Brillo que pasa"], ["girar", "🪙 Girar como moneda"], ["latido", "💓 Latido"], ["flotar", "🎈 Flotar"], ["destellos", "🌟 Destellos"]];

const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const hex = (c, d) => (/^#[0-9a-f]{6}$/i.test(c || "") ? c : d);
const img = (u) => (/^\/api\/admin-img\/[a-f0-9]{16,64}\.(?:png|jpe?g|webp|gif)$/.test(u || "") ? u : "");
let n = 0;

function poligono(puntas, R, r, rot = -90, cx = 60, cy = 82) {
  const p = [];
  for (let i = 0; i < puntas * 2; i++) {
    const a = ((rot + (i * 180) / puntas) * Math.PI) / 180, rad = i % 2 ? r : R;
    p.push(`${(cx + rad * Math.cos(a)).toFixed(1)},${(cy + rad * Math.sin(a)).toFixed(1)}`);
  }
  return `<polygon points="${p.join(" ")}"`;
}
const FORMA = {
  circulo: () => '<circle cx="60" cy="82" r="40"',
  escudo: () => '<path d="M22 50Q60 38 98 50V82Q98 112 60 128Q22 112 22 82Z"',
  estrella: () => poligono(5, 50, 27),
  hexagono: () => poligono(3, 44, 44, -90).replace(/points="([^"]+)"/, (m, pts) => { const a = []; for (let i = 0; i < 6; i++) { const t = ((-90 + i * 60) * Math.PI) / 180; a.push(`${(60 + 44 * Math.cos(t)).toFixed(1)},${(82 + 44 * Math.sin(t)).toFixed(1)}`); } return `points="${a.join(" ")}"`; }),
  rombo: () => '<path d="M60 34L104 82L60 130L16 82Z"',
  engranaje: () => poligono(12, 46, 39, -90),
  corona: () => '<path d="M18 118L14 56L38 78L60 44L82 78L106 56L102 118Z"',
  flor: () => '<path d="' + Array.from({ length: 8 }, (_, i) => { const a = (i * 45 * Math.PI) / 180, x = 60 + 26 * Math.cos(a), y = 82 + 26 * Math.sin(a); return `M${(x + 17).toFixed(1)} ${y.toFixed(1)}a17 17 0 1 0-34 0a17 17 0 1 0 34 0`; }).join("") + 'M86 82a26 26 0 1 0-52 0a26 26 0 1 0 52 0"',
};
const CENTRO_R = { estrella: 21, corona: 24, rombo: 24, escudo: 28 };

let estilos = false;
function ponerEstilos() {
  if (estilos || typeof document === "undefined") return;
  estilos = true;
  const st = document.createElement("style");
  st.textContent = `.mde{overflow:visible}.mde-cuerpo{transform-box:view-box;transform-origin:60px 82px}
.mde-girar .mde-cuerpo{animation:mde-gira 4.5s linear infinite}.mde-latido .mde-cuerpo{animation:mde-late 1.8s ease-in-out infinite}
.mde-flotar{animation:mde-flota 3.2s ease-in-out infinite}.mde-brillo .mde-barrido{animation:mde-barre 3.2s ease-in-out infinite}
.mde-chispa{transform-box:fill-box;transform-origin:center;animation:mde-chispa 2.2s ease-in-out infinite}
@keyframes mde-gira{0%{transform:scaleX(1)}25%{transform:scaleX(.05)}50%{transform:scaleX(-1)}75%{transform:scaleX(.05)}100%{transform:scaleX(1)}}
@keyframes mde-late{50%{transform:scale(1.07)}}@keyframes mde-flota{50%{transform:translateY(-5px)}}
@keyframes mde-barre{0%,20%{transform:translateX(-140px)}70%,100%{transform:translateX(140px)}}
@keyframes mde-chispa{0%,100%{opacity:0;transform:scale(.3)}50%{opacity:1;transform:scale(1)}}
@media (prefers-reduced-motion:reduce){.mde *,.mde{animation:none!important}}`;
  document.head.append(st);
}

/** SVG de una medalla especial. m: { nombre, icono, color, diseno } (sin diseño se dibuja la clásica con ícono y color). */
export function medallaSVG(m = {}, tam = 64) {
  ponerEstilos();
  const d = m.diseno || { forma: "circulo", metal: "oro", c1: hex(m.color, "#c4ff3d"), c2: "#0f172a", centro: "emoji", emoji: m.icono || "🏅", cinta: "v", cinta1: "#ef4444", cinta2: "#2563eb", texto: "", anim: "ninguna", aura: false, estrellas: 0 };
  const id = `mde${++n}`;
  const c1 = hex(d.c1, "#c4ff3d"), c2 = hex(d.c2, "#0ea5e9");
  const metal = d.metal === "personal" ? [`color-mix(in srgb,${c1} 40%,#fff)`, c1, c2] : METALES[d.metal] || METALES.oro;
  const forma = (FORMA[d.forma] || FORMA.circulo)();
  const rc = CENTRO_R[d.forma] || 30;
  const defs = `<defs>
    ${d.metal === "arcoiris" ? `<linearGradient id="${id}m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f43f5e"/><stop offset=".2" stop-color="#f59e0b"/><stop offset=".4" stop-color="#84cc16"/><stop offset=".6" stop-color="#22d3ee"/><stop offset=".8" stop-color="#6366f1"/><stop offset="1" stop-color="#d946ef"/></linearGradient>`
      : `<linearGradient id="${id}m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${metal[0]}"/><stop offset=".45" stop-color="${metal[1]}"/><stop offset=".75" stop-color="${metal[2]}"/><stop offset="1" stop-color="${metal[1]}"/></linearGradient>`}
    <radialGradient id="${id}f" cx=".4" cy=".35" r=".75"><stop offset="0" stop-color="color-mix(in srgb,${c1} 55%,#fff)"/><stop offset=".55" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></radialGradient>
    <linearGradient id="${id}b" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <clipPath id="${id}c">${forma}/></clipPath>
    <clipPath id="${id}i"><circle cx="60" cy="82" r="${rc - 3}"/></clipPath>
    ${d.aura ? `<filter id="${id}g" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="${c1}" flood-opacity=".85"/></filter>` : ""}
  </defs>`;
  const k1 = hex(d.cinta1, "#ef4444"), k2 = hex(d.cinta2, "#2563eb");
  const cinta = d.cinta === "v" ? `<path d="M34 0H54L66 46H46Z" fill="${k1}"/><path d="M86 0H66L54 46H74Z" fill="${k2}"/><path d="M40 0h6l12 44h-6z" fill="#fff" opacity=".35"/>`
    : d.cinta === "doble" ? `<path d="M38 0h44v48H38z" fill="${k1}"/><path d="M48 0h8v48h-8zM64 0h8v48h-8z" fill="${k2}"/><path d="M38 48h44l-6 6H44z" fill="#000" opacity=".25"/>`
      : d.cinta === "laurel" ? Array.from({ length: 14 }, (_, i) => { const lado = i < 7 ? -1 : 1, j = i % 7, a = ((lado < 0 ? 200 - j * 16 : -20 + j * 16) * Math.PI) / 180;
        const x = 60 + 54 * Math.cos(a), y = 86 + 54 * Math.sin(a); return `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="9" ry="4.5" fill="#22c55e" stroke="#14532d" stroke-width="1.2" transform="rotate(${((a * 180) / Math.PI + 90 * lado).toFixed(0)} ${x.toFixed(1)} ${y.toFixed(1)})"/>`; }).join("") : "";
  const completa = d.centro === "completa" && img(d.imagen);
  const centro = completa ? "" : d.centro === "imagen" && img(d.imagen)
    ? `<image href="${img(d.imagen)}" x="${60 - rc + 3}" y="${82 - rc + 3}" width="${(rc - 3) * 2}" height="${(rc - 3) * 2}" clip-path="url(#${id}i)" preserveAspectRatio="xMidYMid slice"/>`
    : `<text x="60" y="${82 + rc * 0.36}" font-size="${rc * 1.05}" text-anchor="middle" font-family="system-ui,'Segoe UI Emoji','Apple Color Emoji',sans-serif">${esc(d.emoji || m.icono || "🏅")}</text>`;
  const nEstrellas = Math.min(5, d.estrellas || 0);
  const estrellas = Array.from({ length: nEstrellas }, (_, i) => {
    const t = (((-90 + (i - (nEstrellas - 1) / 2) * 22) * Math.PI) / 180), x = 60 + 56 * Math.cos(t), y = 86 + 56 * Math.sin(t);
    return `<path d="M${x} ${y - 6}l1.8 4 4.2.4-3.2 2.8 1 4.2-3.8-2.2-3.8 2.2 1-4.2-3.2-2.8 4.2-.4z" fill="#fde047" stroke="#a16207" stroke-width=".8"/>`;
  }).join("");
  const letrero = d.texto ? `<g><path d="M10 120h100l-8 9 8 9H10l8-9z" fill="${k1}" stroke="#000" stroke-opacity=".25"/><path d="M16 118h88v18H16z" fill="url(#${id}m)"/><text x="60" y="131" font-size="${d.texto.length > 11 ? 8.5 : 10}" font-weight="900" text-anchor="middle" fill="#1f2937" font-family="system-ui,sans-serif" letter-spacing=".5">${esc(d.texto).toUpperCase()}</text></g>` : "";
  const chispas = d.anim === "destellos" ? [[18, 40, 0], [102, 46, .6], [12, 104, 1.1], [108, 108, 1.6], [60, 22, .3]].map(([x, y, r]) => `<path class="mde-chispa" style="animation-delay:${r}s" d="M${x} ${y - 6}l1.6 4.4 4.4 1.6-4.4 1.6-1.6 4.4-1.6-4.4-4.4-1.6 4.4-1.6z" fill="#fff"/>`).join("") : "";
  return `<svg class="mde mde-${esc(d.anim || "ninguna")}" viewBox="0 0 120 150" width="${tam}" height="${Math.round(tam * 1.25)}" role="img" aria-label="${esc(m.nombre || "Medalla")}" xmlns="http://www.w3.org/2000/svg">${defs}
    ${cinta}
    <g class="mde-cuerpo"${d.aura ? ` filter="url(#${id}g)"` : ""}>
      ${forma} fill="url(#${id}m)"/>
      <g clip-path="url(#${id}c)" transform="translate(60 82) scale(.84) translate(-60 -82)">${forma} fill="url(#${id}f)"/>${completa ? `<image href="${completa}" x="10" y="28" width="100" height="108" preserveAspectRatio="xMidYMid slice"/>` : ""}</g>
      ${forma} fill="none" stroke="#000" stroke-opacity=".18" stroke-width="1.2"/>
      ${centro}
      ${d.anim === "brillo" ? `<g clip-path="url(#${id}c)"><rect class="mde-barrido" x="20" y="20" width="40" height="130" fill="url(#${id}b)" transform="skewX(-20)"/></g>` : ""}
    </g>
    ${estrellas}${letrero}${chispas}
  </svg>`;
}
