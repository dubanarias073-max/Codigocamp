// Cosméticos de la tienda y los cofres: cómo se ve cada fondo, puntero, tema, marco, efecto y rastro, y cómo se aplican
// en todas las páginas. Todo es original (CSS, SVG y canvas), sin imágenes externas.
const svg = (cuerpo, w = 32, h = 32) => `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 32 32">${cuerpo}</svg>`)}`;
const reducido = () => { try { if (localStorage.getItem("cc_menos_mov") === "1") return true; } catch { /* nada */ } return matchMedia("(prefers-reduced-motion: reduce)").matches; };

// ------------------------------------------------------------------------------------ punteros ----
// Cada puntero es un juego de 3, como los del sistema: normal (flecha), mano (enlaces y botones) y texto (para escribir).
// La mano y la barra de texto se pintan con los colores del puntero y llevan su emblema.
const FLECHA = (r, b, extra = "") => `<path d="M3 3l20 8.5-8.4 2.6L12 23z" fill="${r}" stroke="${b}" stroke-width="1.8" stroke-linejoin="round"/>${extra}`;
export const CURSORES = {
  cursor_cohete: { x: 3, y: 3, c: ["#e5e7eb", "#1f2937", '<path d="M24 25l2 5 2-2-1-3z" fill="#f97316"/>'], svg: '<path d="M4 4l9 3 10 10-4 4L9 11z" fill="#e5e7eb" stroke="#1f2937" stroke-width="1.5" stroke-linejoin="round"/><circle cx="14" cy="13" r="2.2" fill="#38bdf8" stroke="#1f2937"/><path d="M19 21l3 6 3-3-2-5M21 17l6 3-3 3-5-2" fill="#f97316" stroke="#1f2937" stroke-linejoin="round"/>' },
  cursor_espada: { x: 2, y: 2, c: ["#cbd5e1", "#0f172a", '<path d="M25 25h4v4h-4z" fill="#facc15" stroke="#0f172a"/>'], svg: '<path d="M2 2h4v2h2v2h2v2h2v2h2v2h2v2h-2v2h-2v-2h-2v-2H10v-2H8v-2H6V8H4V6H2z" fill="#cbd5e1" stroke="#0f172a" stroke-width="1"/><path d="M16 18h2v-2h2v2h2v2h-2v2h-2v-2h-2z" fill="#a16207" stroke="#0f172a"/><path d="M22 22h4v4h-4z" fill="#facc15" stroke="#0f172a"/>' },
  cursor_varita: { x: 4, y: 4, c: ["#ddd6fe", "#5b21b6", '<path d="M27 22l1 2 2 1-2 1-1 2-1-2-2-1 2-1z" fill="#fde047" stroke="#a16207" stroke-width=".6"/>'], svg: '<path d="M10 10l17 17" stroke="#1f2937" stroke-width="5" stroke-linecap="round"/><path d="M10 10l17 17" stroke="#7c3aed" stroke-width="3" stroke-linecap="round"/><path d="M6 1l1.6 3.4L11 6 7.6 7.6 6 11 4.4 7.6 1 6l3.4-1.6z" fill="#fde047" stroke="#a16207"/>' },
  cursor_lapiz: { x: 2, y: 29, c: ["#fde68a", "#78350f", '<path d="M25 30l1-4 4-4 1 1-4 4z" fill="#f472b6"/>'], svg: '<path d="M3 29l2-7L22 5l5 5L10 27z" fill="#fbbf24" stroke="#1f2937" stroke-width="1.5" stroke-linejoin="round"/><path d="M3 29l2-7 5 5z" fill="#fde68a" stroke="#1f2937" stroke-linejoin="round"/><path d="M19 8l5 5" stroke="#1f2937"/><path d="M22 5l5 5 2-2-5-5z" fill="#f472b6" stroke="#1f2937"/>' },
  cursor_neon: { x: 2, y: 2, c: ["#0e7490", "#22d3ee", ""], svg: '<path d="M3 3l22 9-9 3-3 9z" fill="#0e7490" stroke="#22d3ee" stroke-width="2" stroke-linejoin="round"/><path d="M3 3l22 9-9 3-3 9z" fill="none" stroke="#a5f3fc" stroke-width=".8" stroke-linejoin="round"/>' },
  cursor_gato: { x: 16, y: 16, manoX: 12, c: ["#fda4af", "#9f1239", '<circle cx="27" cy="27" r="2.5" fill="#fda4af" stroke="#9f1239"/>'], svg: '<ellipse cx="16" cy="20" rx="7" ry="6" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="8" cy="11" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="14" cy="7" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="20" cy="7" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="25" cy="11" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/>' },
  cursor_estrella: { x: 4, y: 4, c: ["#fde047", "#a16207", '<path d="M27 22l1.2 2.4 2.6.4-1.9 1.8.5 2.6-2.4-1.3-2.3 1.3.4-2.6-1.9-1.8 2.6-.4z" fill="#fff7"/>'], svg: '<path d="M30 30L11 11" stroke="#fde047" stroke-width="3" stroke-linecap="round" opacity=".5"/><path d="M8 1l2.2 4.6 5 .7-3.6 3.5.9 5L8 12.4 3.5 14.8l.9-5L.8 6.3l5-.7z" fill="#facc15" stroke="#a16207"/>' },
  cursor_corona: { x: 3, y: 3, c: ["#fde68a", "#92400e", '<path d="M22 26l2-4 2 3 2-4 2 5z" fill="#facc15" stroke="#92400e" stroke-width=".8"/>'], svg: '<path d="M3 3l7 18h3z" fill="#e5e7eb" stroke="#1f2937" stroke-width="1.2"/><path d="M13 18l3-8 4 5 3-7 3 7 4-5 1 8z" fill="#facc15" stroke="#92400e" stroke-width="1.2" stroke-linejoin="round"/><rect x="13" y="18" width="17" height="4" rx="1" fill="#f59e0b" stroke="#92400e"/><circle cx="21.5" cy="20" r="1.2" fill="#ef4444"/>' },
  cursor_rayo: { x: 14, y: 2, c: ["#fde047", "#a16207", '<path d="M28 20l-4 5h3l-2 5 5-6h-3l2-4z" fill="#fde047" stroke="#a16207" stroke-width=".6"/>'], svg: '<path d="M18 1L6 18h8l-4 13 16-19h-9l5-11z" fill="#fde047" stroke="#a16207" stroke-width="1.5" stroke-linejoin="round"/><path d="M17 4l-7 11h6" fill="none" stroke="#fff" stroke-width="1.2" opacity=".8"/>' },
  cursor_sable: { x: 2, y: 2, c: ["#a5f3fc", "#0e7490", '<path d="M24 24l6 6" stroke="#22d3ee" stroke-width="3" stroke-linecap="round" opacity=".7"/>'], svg: '<path d="M3 3l17 17" stroke="#22d3ee" stroke-width="6" stroke-linecap="round" opacity=".35"/><path d="M3 3l17 17" stroke="#a5f3fc" stroke-width="3" stroke-linecap="round"/><path d="M3 3l17 17" stroke="#fff" stroke-width="1.2" stroke-linecap="round"/><path d="M19 22l3-3 6 6-3 3z" fill="#64748b" stroke="#0f172a" stroke-width="1.2"/><path d="M20 18l4 4" stroke="#0f172a" stroke-width="2"/>' },
  cursor_diamante: { x: 3, y: 3, c: ["#a5f3fc", "#0e7490", '<circle cx="27" cy="24" r="1.4" fill="#fff"/><circle cx="29" cy="28" r="1" fill="#fff"/>'], svg: '<path d="M3 3l22 10-9 3-3 10z" fill="#a5f3fc" stroke="#0e7490" stroke-width="1.6" stroke-linejoin="round"/><path d="M3 3l13 13M25 13l-9 3M13 26l3-10" stroke="#ecfeff" stroke-width="1" opacity=".9"/><path d="M8 8l4 1-1 4" fill="#fff" opacity=".7"/><circle cx="24" cy="5" r="1.6" fill="#fff"/><circle cx="27" cy="9" r="1" fill="#fff"/>' },
  // nuevos
  cursor_pixel: { x: 2, y: 2, c: ["#f8fafc", "#0f172a", ""], svg: '<path d="M2 2h2v2h2v2h2v2h2v2h2v2h2v2h2v2h-6v2h2v2h2v2h-2v2h-2v-2h-2v-2H8v2H6v2H4v-2H2z" fill="#f8fafc" stroke="#0f172a" stroke-width="1.4" stroke-linejoin="miter"/>' },
  cursor_hoja: { x: 3, y: 3, c: ["#bbf7d0", "#166534", '<path d="M24 30c0-5 2-7 6-8-1 4-3 7-6 8z" fill="#4ade80" stroke="#166534" stroke-width=".8"/>'], svg: '<path d="M3 3c14 0 24 6 24 17-11 2-21-4-24-17z" fill="#4ade80" stroke="#166534" stroke-width="1.6" stroke-linejoin="round"/><path d="M3 3c8 6 13 11 20 16" stroke="#166534" stroke-width="1.2" fill="none"/>' },
  cursor_terminal: { x: 3, y: 3, c: ["#052e16", "#22c55e", '<path d="M22 24l3 2-3 2M26 29h4" stroke="#22c55e" stroke-width="1.4" fill="none"/>'], svg: FLECHA("#052e16", "#22c55e", '<path d="M16 22l4 3-4 3M21 29h7" stroke="#4ade80" stroke-width="2" fill="none" stroke-linecap="round"/>') },
  cursor_fuego: { x: 3, y: 3, c: ["#fdba74", "#9a3412", '<path d="M27 30c-3 0-4-2-3-4 1 1 1 1 2 0 0-2 1-3 2-4 0 2 2 3 2 5s-1 3-3 3z" fill="#f97316"/>'], svg: FLECHA("#fb923c", "#7c2d12", '<path d="M15 30c-4 0-6-3-4-6 1 2 2 2 3 1 0-3 2-5 4-6-1 3 3 4 3 7 0 2-2 4-6 4z" fill="#facc15" stroke="#c2410c" stroke-width="1"/>') },
  cursor_hielo: { x: 3, y: 3, c: ["#e0f2fe", "#0369a1", '<path d="M27 22v8M23.5 24l7 4M30.5 24l-7 4" stroke="#38bdf8" stroke-width="1.2"/>'], svg: FLECHA("#bae6fd", "#0369a1", '<path d="M8 8l5 2M10 13l2-4" stroke="#fff" stroke-width="1.2"/><path d="M22 21v9M18 23l8 5M26 23l-8 5" stroke="#7dd3fc" stroke-width="1.5"/>') },
  cursor_pluma: { x: 2, y: 30, c: ["#f5f5f4", "#44403c", '<circle cx="27" cy="28" r="2" fill="#1e3a8a"/>'], svg: '<path d="M2 30c4-10 10-20 26-28-3 13-13 21-23 24z" fill="#f5f5f4" stroke="#44403c" stroke-width="1.5" stroke-linejoin="round"/><path d="M2 30L22 8" stroke="#44403c" stroke-width="1.2"/><path d="M8 22l4-1M12 17l5-1M16 12l5 0" stroke="#a8a29e" stroke-width="1"/><circle cx="3" cy="29" r="1.6" fill="#1e3a8a"/>' },
  cursor_robot: { x: 3, y: 3, c: ["#cbd5e1", "#334155", '<rect x="23" y="23" width="7" height="7" rx="1.5" fill="#94a3b8" stroke="#334155"/><circle cx="26.5" cy="26.5" r="1.3" fill="#22d3ee"/>'], svg: '<path d="M3 3l9 4-2 2 4 4 2-2 9 9-5 5-9-9 2-2-4-4-2 2z" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" stroke-linejoin="round"/><circle cx="18" cy="18" r="2" fill="#22d3ee" stroke="#334155"/><rect x="21" y="23" width="9" height="7" rx="2" fill="#94a3b8" stroke="#334155" stroke-width="1.3"/>' },
  cursor_arcoiris: { x: 3, y: 3, c: ["url(#ccArco)", "#1f2937", ""], def: '<defs><linearGradient id="ccArco" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f43f5e"/><stop offset=".25" stop-color="#f59e0b"/><stop offset=".5" stop-color="#4ade80"/><stop offset=".75" stop-color="#22d3ee"/><stop offset="1" stop-color="#a855f7"/></linearGradient></defs>', svg: FLECHA("url(#ccArco)", "#1f2937") },
  cursor_galaxia: { x: 3, y: 3, c: ["url(#ccGal)", "#c4b5fd", '<circle cx="27" cy="25" r="1" fill="#fff"/><circle cx="29" cy="29" r=".8" fill="#fff"/><circle cx="25" cy="29" r=".6" fill="#fff"/>'], def: '<defs><radialGradient id="ccGal" cx=".35" cy=".35" r=".8"><stop offset="0" stop-color="#f0abfc"/><stop offset=".45" stop-color="#7c3aed"/><stop offset="1" stop-color="#1e1b4b"/></radialGradient></defs>', svg: FLECHA("url(#ccGal)", "#c4b5fd", '<circle cx="9" cy="8" r=".9" fill="#fff"/><circle cx="14" cy="11" r=".7" fill="#fff"/><circle cx="11" cy="15" r="1" fill="#fff"/><circle cx="17" cy="10" r=".6" fill="#fff"/>') },
  cursor_dragon: { x: 3, y: 3, c: ["#fde68a", "#7f1d1d", '<path d="M24 30l2-6 2 6M27 30l2-5 1 5" fill="#dc2626" stroke="#7f1d1d" stroke-width=".7"/>'], svg: '<path d="M3 3c6 4 14 5 22 3-3 4-4 8-2 12-5-3-9-2-12 2-1-6-4-11-8-17z" fill="#dc2626" stroke="#7f1d1d" stroke-width="1.6" stroke-linejoin="round"/><path d="M3 3l7 7M8 6l3 3M6 9l3 2" stroke="#fde68a" stroke-width="1.3" stroke-linecap="round"/><path d="M14 19l-3 6 4-3 1 6 2-6 3 3-1-6" fill="#facc15" stroke="#a16207" stroke-width="1" stroke-linejoin="round"/>' },
  cursor_shuriken: { x: 16, y: 16, c: ["#cbd5e1", "#1e293b", '<circle cx="27" cy="27" r="2" fill="#94a3b8" stroke="#1e293b"/>'], svg: '<path d="M16 1l3 12 12 3-12 3-3 12-3-12-12-3 12-3z" fill="#cbd5e1" stroke="#1e293b" stroke-width="1.4" stroke-linejoin="round"/><circle cx="16" cy="16" r="3" fill="#1e293b"/><circle cx="16" cy="16" r="1.2" fill="#e2e8f0"/>' },
  cursor_pizza: { x: 3, y: 3, c: ["#fcd34d", "#92400e", '<circle cx="27" cy="26" r="2.2" fill="#dc2626"/>'], svg: '<path d="M3 3l26 9-17 17z" fill="#fcd34d" stroke="#92400e" stroke-width="1.6" stroke-linejoin="round"/><path d="M29 12l-17 17" stroke="#b45309" stroke-width="4" stroke-linecap="round"/><circle cx="12" cy="10" r="2.4" fill="#dc2626"/><circle cx="17" cy="16" r="2.2" fill="#dc2626"/><circle cx="10" cy="18" r="1.8" fill="#dc2626"/><path d="M14 7l1 1M19 12l1 1M8 14l1 1" stroke="#16a34a" stroke-width="1.4"/>' },
  cursor_bug: { x: 3, y: 3, c: ["#86efac", "#14532d", '<circle cx="27" cy="27" r="2.6" fill="#4ade80" stroke="#14532d"/>'], svg: FLECHA("#bbf7d0", "#14532d", '<ellipse cx="22" cy="23" rx="5" ry="6" fill="#4ade80" stroke="#14532d" stroke-width="1.3"/><path d="M22 17v12M17 21l-3-1M17 25l-3 1M27 21l3-1M27 25l3 1M20 17l-2-3M24 17l2-3" stroke="#14532d" stroke-width="1.2" stroke-linecap="round"/><circle cx="20.5" cy="21" r=".9" fill="#14532d"/><circle cx="23.5" cy="21" r=".9" fill="#14532d"/>') },
  cursor_llave: { x: 3, y: 3, c: ["#fde68a", "#92400e", '<circle cx="26" cy="26" r="3" fill="none" stroke="#d97706" stroke-width="2"/>'], svg: '<circle cx="8" cy="8" r="6" fill="#fcd34d" stroke="#92400e" stroke-width="1.6"/><circle cx="8" cy="8" r="2.2" fill="#fff8" stroke="#92400e"/><path d="M12 12l16 16M21 21l3-3M24 24l3-3" stroke="#92400e" stroke-width="4.5" stroke-linecap="round"/><path d="M12 12l16 16M21 21l3-3M24 24l3-3" stroke="#fcd34d" stroke-width="2.4" stroke-linecap="round"/><circle cx="5.5" cy="5.5" r="1.2" fill="#fff"/>' },
  cursor_planeta: { x: 4, y: 4, c: ["#fdba74", "#7c2d12", '<ellipse cx="27" cy="27" rx="4" ry="1.4" fill="none" stroke="#fde68a" stroke-width="1.2"/>'], svg: '<path d="M2 2l9 3-6 6z" fill="#fdba74" stroke="#7c2d12" stroke-width="1.2" stroke-linejoin="round"/><circle cx="19" cy="19" r="8" fill="#fb923c" stroke="#7c2d12" stroke-width="1.4"/><path d="M13 16c3 1 8 1 12 0M12 21c4 1 9 1 13 0" stroke="#fed7aa" stroke-width="1.2" fill="none"/><ellipse cx="19" cy="19" rx="13" ry="4" fill="none" stroke="#fde68a" stroke-width="2" transform="rotate(-20 19 19)"/>' },
  cursor_oro: { x: 3, y: 3, c: ["url(#ccOro)", "#78350f", '<path d="M27 21l1 2.4 2.4 1-2.4 1-1 2.4-1-2.4-2.4-1 2.4-1z" fill="#fff"/>'], def: '<defs><linearGradient id="ccOro" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fef3c7"/><stop offset=".35" stop-color="#fbbf24"/><stop offset=".6" stop-color="#b45309"/><stop offset=".8" stop-color="#fde68a"/><stop offset="1" stop-color="#92400e"/></linearGradient></defs>', svg: FLECHA("url(#ccOro)", "#78350f", '<path d="M7 7l5 2-2 1z" fill="#fff" opacity=".85"/><path d="M24 4l1 2.4 2.4 1-2.4 1-1 2.4-1-2.4-2.4-1 2.4-1z" fill="#fff"/>') },
  cursor_sabio: { x: 3, y: 3, c: ["#fef3c7", "#78350f", '<path d="M24 29h7M27.5 25.5v7" stroke="#7c3aed" stroke-width="1.6"/>'], svg: '<path d="M3 3l20 8.5-8.4 2.6L12 23z" fill="#7c3aed" stroke="#2e1065" stroke-width="1.6" stroke-linejoin="round"/><rect x="15" y="18" width="15" height="11" rx="2" fill="#fef3c7" stroke="#78350f" stroke-width="1.2"/><path d="M18 21.5h9M18 24h9M18 26.5h6" stroke="#a16207" stroke-width="1"/><circle cx="8" cy="7" r="1.2" fill="#fde68a"/>' },
};
const MANO = (r, b, extra) => `<path d="M11.5 3.2c0-1.6 3-1.6 3 0v9.3l1.2-.2V10c0-1.6 2.8-1.6 2.8 0v2.6l1.1-.1v-1.6c0-1.5 2.8-1.5 2.8 0v2l1-.1V12c0-1.5 2.7-1.5 2.7 0v6.4c0 6-3.3 10.3-9.2 10.3-4 0-6-1.8-8-5L4.2 17.6c-.9-1.5 1.3-3 2.4-1.6l4.9 5.4z" fill="${r}" stroke="${b}" stroke-width="1.6" stroke-linejoin="round"/><path d="M14.5 13v5M18.5 13v5M22.4 13.5v4.5" stroke="${b}" stroke-width="1" opacity=".5"/>${extra}`;
const TEXTO = (r, b, extra) => `<path d="M11 3.5h3l2 1.5 2-1.5h3M16 5v22M11 28.5h3l2-1.5 2 1.5h3M13 16h6" fill="none" stroke="${b}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M11 3.5h3l2 1.5 2-1.5h3M16 5v22M11 28.5h3l2-1.5 2 1.5h3M13 16h6" fill="none" stroke="${r}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>${extra}`;
/** Las 3 versiones de un puntero: { normal, mano, texto }, cada una con { url, x, y }. */
export function juegoCursor(clave) {
  const k = CURSORES[clave];
  if (!k) return null;
  const [r, b, extra] = k.c;
  const def = k.def ?? "";
  return {
    normal: { url: svg(def + k.svg), x: k.x, y: k.y },
    mano: { url: svg(def + MANO(r, b, extra)), x: 12, y: 3 },
    texto: { url: svg(def + TEXTO(r, b, extra)), x: 16, y: 16 },
  };
}
export const urlCursor = (clave) => juegoCursor(clave)?.normal.url ?? null;

// --------------------------------------------------------------------------------------- temas ----
export const TEMAS = {
  tema_oceano: { acc: "#38bdf8", acc2: "#0284c7", cy: "#22d3ee" },
  tema_neon: { acc: "#e879f9", acc2: "#a21caf", cy: "#818cf8" },
  tema_bosque: { acc: "#86efac", acc2: "#15803d", cy: "#5eead4" },
  tema_atardecer: { acc: "#fb923c", acc2: "#c2410c", cy: "#f472b6" },
  tema_oro: { acc: "#fcd34d", acc2: "#b45309", cy: "#fde68a" },
  tema_cyberpunk: { acc: "#fde047", acc2: "#db2777", cy: "#f0abfc" },
  tema_hielo: { acc: "#bae6fd", acc2: "#0369a1", cy: "#e0f2fe" },
  tema_lava: { acc: "#f87171", acc2: "#b91c1c", cy: "#fdba74" },
  tema_galaxia: { acc: "#c084fc", acc2: "#7e22ce", cy: "#67e8f9" },
  tema_menta: { acc: "#6ee7b7", acc2: "#047857", cy: "#99f6e4" },
  tema_cereza: { acc: "#fb7185", acc2: "#be123c", cy: "#fda4af" },
  tema_lavanda: { acc: "#c4b5fd", acc2: "#6d28d9", cy: "#ddd6fe" },
  tema_cafe: { acc: "#d6a77a", acc2: "#7c4a21", cy: "#f5deb3" },
  tema_sakura: { acc: "#f9a8d4", acc2: "#db2777", cy: "#fbcfe8" },
  tema_matrix: { acc: "#4ade80", acc2: "#15803d", cy: "#86efac" },
  tema_vaporwave: { acc: "#f472b6", acc2: "#0d9488", cy: "#5eead4" },
  tema_esmeralda: { acc: "#34d399", acc2: "#065f46", cy: "#fcd34d" },
  tema_coral: { acc: "#fb7185", acc2: "#e11d48", cy: "#2dd4bf" },
  tema_limon: { acc: "#facc15", acc2: "#a16207", cy: "#86efac" },
  tema_turquesa: { acc: "#2dd4bf", acc2: "#0f766e", cy: "#38bdf8" },
  tema_rubi: { acc: "#f43f5e", acc2: "#9f1239", cy: "#f9a8d4" },
  tema_noche_polar: { acc: "#7dd3fc", acc2: "#1e40af", cy: "#6ee7b7" },
  tema_aurora: { acc: "#4ade80", acc2: "#7c3aed", cy: "#22d3ee" },
  tema_aprendiz: { acc: "#a3e635", acc2: "#3f6212", cy: "#fde047" },
  tema_mito: { acc: "#f0abfc", acc2: "#a16207", cy: "#fde68a" },
};

// -------------------------------------------------------------------------------------- fondos ----
const CIRCUITO = svg('<g fill="none" stroke="#22d3ee" stroke-opacity=".35" stroke-width="1"><path d="M0 8h10l4 4h18M8 0v6M22 12v10l4 4h6M0 24h8l3-3"/><circle cx="8" cy="7" r="1.5"/><circle cx="22" cy="22" r="1.5"/><circle cx="11" cy="21" r="1.5"/></g>', 32, 32);
const OLAS = (c, o) => svg(`<path d="M0 20 Q8 14 16 20 T32 20 V32 H0z" fill="${c}" fill-opacity="${o}"/>`, 32, 32);
export const FONDOS = {
  fondo_aurora: { css: "background:radial-gradient(60% 50% at 20% 20%,rgba(74,222,128,.35),transparent 70%),radial-gradient(50% 45% at 80% 30%,rgba(56,189,248,.32),transparent 70%),radial-gradient(60% 50% at 50% 85%,rgba(192,132,252,.3),transparent 70%),#020617;background-size:200% 200%;animation:cc-aurora 18s ease-in-out infinite alternate", oscuro: true },
  fondo_galaxia: { css: "background:radial-gradient(1px 1px at 10% 20%,#fff,transparent),radial-gradient(1px 1px at 30% 70%,#fff,transparent),radial-gradient(1.5px 1.5px at 55% 35%,#fff,transparent),radial-gradient(1px 1px at 75% 80%,#fff,transparent),radial-gradient(1.5px 1.5px at 90% 15%,#fff,transparent),radial-gradient(1px 1px at 45% 90%,#fff,transparent),radial-gradient(ellipse at 70% 40%,rgba(147,51,234,.45),transparent 60%),radial-gradient(ellipse at 20% 80%,rgba(37,99,235,.4),transparent 55%),#05010f;background-size:220px 220px,300px 300px,260px 260px,340px 340px,280px 280px,200px 200px,100% 100%,100% 100%,100% 100%;animation:cc-titilar 6s ease-in-out infinite alternate", oscuro: true },
  fondo_matrix: { canvas: "matrix", css: "background:#010a04", oscuro: true },
  fondo_synthwave: { css: "background:linear-gradient(transparent 58%,rgba(236,72,153,.0) 58%),repeating-linear-gradient(90deg,rgba(236,72,153,.55) 0 2px,transparent 2px 60px) 0 62%/100% 38% no-repeat,repeating-linear-gradient(0deg,rgba(236,72,153,.55) 0 2px,transparent 2px 34px) 0 100%/100% 38% no-repeat,radial-gradient(circle at 50% 58%,#fde047 0,#f97316 9%,#db2777 15%,transparent 16%),linear-gradient(#1e0b3a 0%,#4c1d95 45%,#be185d 58%,#0f0524 58%);animation:cc-grid 3s linear infinite", oscuro: true },
  fondo_oceano: { css: `background:url("${OLAS("#38bdf8", ".18")}") 0 100%/160px 120px repeat-x,url("${OLAS("#0ea5e9", ".22")}") 40px 100%/220px 160px repeat-x,linear-gradient(#0c4a6e,#082f49 60%,#031525);animation:cc-olas 14s linear infinite`, oscuro: true },
  fondo_circuito: { css: `background:url("${CIRCUITO}") 0 0/64px 64px,radial-gradient(ellipse at 50% 0,#0f3b3a,#031413 70%)`, oscuro: true },
  fondo_atardecer: { css: "background:linear-gradient(160deg,#fde68a 0%,#fb923c 35%,#f43f5e 70%,#7c3aed 100%)" },
  fondo_bosque: { css: "background:radial-gradient(ellipse at 20% 0,rgba(187,247,208,.9),transparent 60%),linear-gradient(170deg,#dcfce7,#86efac 45%,#166534)" },
  fondo_cuadricula: { css: "background:linear-gradient(rgba(34,211,238,.25) 1px,transparent 1px) 0 0/40px 40px,linear-gradient(90deg,rgba(34,211,238,.25) 1px,transparent 1px) 0 0/40px 40px,radial-gradient(ellipse at 50% 30%,#0b2545,#020617 70%);animation:cc-cuadricula 8s linear infinite", oscuro: true },
  fondo_nieve: { canvas: "nieve", css: "background:radial-gradient(ellipse at 50% 120%,#1e3a8a,transparent 60%),linear-gradient(#020617,#0f172a 55%,#1e293b)", oscuro: true },
  fondo_luciernagas: { canvas: "luciernagas", css: "background:radial-gradient(ellipse at 50% 100%,#14532d,transparent 65%),linear-gradient(#020a05,#052e16 70%,#022c22)", oscuro: true },
  fondo_ciudad: { css: `background:url("${svg('<g fill="#0b0221"><rect x="0" y="14" width="5" height="18"/><rect x="6" y="8" width="6" height="24"/><rect x="13" y="17" width="4" height="15"/><rect x="18" y="5" width="7" height="27"/><rect x="26" y="12" width="6" height="20"/></g><g fill="#facc15" opacity=".8"><rect x="7.5" y="11" width="1" height="1"/><rect x="9.5" y="15" width="1" height="1"/><rect x="20" y="8" width="1" height="1"/><rect x="22" y="13" width="1" height="1"/><rect x="20" y="19" width="1" height="1"/><rect x="28" y="16" width="1" height="1"/><rect x="1.5" y="18" width="1" height="1"/><rect x="14" y="21" width="1" height="1"/></g><g fill="#f0abfc" opacity=".7"><rect x="23" y="24" width="1" height="1"/><rect x="8" y="22" width="1" height="1"/><rect x="29" y="25" width="1" height="1"/></g>', 32, 32)}") 0 100%/220px 220px repeat-x,radial-gradient(circle at 75% 30%,rgba(244,114,182,.55),transparent 25%),linear-gradient(#1e0b3b,#4c1d95 55%,#be185d)`, oscuro: true },
  fondo_hiperespacio: { canvas: "hiper", css: "background:radial-gradient(circle at 50% 50%,#1e1b4b,#020617 70%)", oscuro: true },
  fondo_agujero_negro: { canvas: "agujero", css: "background:radial-gradient(circle at 50% 50%,#000 6%,#7c2d12 12%,#f59e0b 15%,#4c1d95 30%,#020617 65%)", oscuro: true },
  fondo_cuaderno: { css: "background:linear-gradient(90deg,transparent 58px,rgba(239,68,68,.55) 58px 60px,transparent 60px),repeating-linear-gradient(#fffdf5 0 27px,rgba(59,130,246,.35) 27px 28px),#fffdf5" },
  fondo_plano: { css: "background:linear-gradient(rgba(255,255,255,.22) 1px,transparent 1px) 0 0/100px 100px,linear-gradient(90deg,rgba(255,255,255,.22) 1px,transparent 1px) 0 0/100px 100px,linear-gradient(rgba(255,255,255,.1) 1px,transparent 1px) 0 0/20px 20px,linear-gradient(90deg,rgba(255,255,255,.1) 1px,transparent 1px) 0 0/20px 20px,#1d4ed8", oscuro: true },
  fondo_pixel: { css: `background:url("${svg('<g shape-rendering="crispEdges"><rect x="4" y="6" width="8" height="2" fill="#fff"/><rect x="2" y="8" width="12" height="2" fill="#fff"/><rect x="20" y="3" width="6" height="2" fill="#fff"/><rect x="18" y="5" width="10" height="2" fill="#fff"/></g>', 32, 32)}") 0 0/192px 192px,linear-gradient(transparent 82%,#4ade80 82% 86%,#16a34a 86% 90%,#a16207 90%),#60a5fa;image-rendering:pixelated` },
  fondo_terminal: { css: "background:repeating-linear-gradient(rgba(0,0,0,.25) 0 1px,transparent 1px 3px),radial-gradient(ellipse at 50% 45%,#064e3b,#022c22 60%,#010b08);animation:cc-titilar 4s ease-in-out infinite alternate", oscuro: true },
  fondo_vaporwave: { css: "background:repeating-linear-gradient(90deg,rgba(94,234,212,.45) 0 2px,transparent 2px 64px) 0 100%/100% 42% no-repeat,repeating-linear-gradient(0deg,rgba(94,234,212,.45) 0 2px,transparent 2px 30px) 0 100%/100% 42% no-repeat,radial-gradient(circle at 50% 56%,#fde68a 0,#f472b6 11%,transparent 12%),linear-gradient(#2e1065,#be185d 56%,#1e0a3c 58%);animation:cc-grid 4s linear infinite", oscuro: true },
  fondo_lluvia: { canvas: "lluvia", css: "background:radial-gradient(ellipse at 50% 120%,#1e3a8a,transparent 60%),linear-gradient(#020617,#0f172a 60%,#111827)", oscuro: true },
  fondo_burbujas: { canvas: "burbujas", css: "background:radial-gradient(ellipse at 50% -10%,rgba(125,211,252,.4),transparent 60%),linear-gradient(#0369a1,#0c4a6e 55%,#082f49)", oscuro: true },
  fondo_fugaces: { canvas: "fugaces", css: "background:radial-gradient(1px 1px at 12% 18%,#fff,transparent),radial-gradient(1px 1px at 38% 62%,#fff,transparent),radial-gradient(1.5px 1.5px at 64% 28%,#fff,transparent),radial-gradient(1px 1px at 82% 74%,#fff,transparent),radial-gradient(1px 1px at 52% 88%,#fff,transparent),linear-gradient(#020617,#0b1440 70%,#1e1b4b);background-size:240px 240px,300px 300px,270px 270px,330px 330px,210px 210px,100% 100%", oscuro: true },
  fondo_sakura: { canvas: "sakura", css: "background:radial-gradient(ellipse at 20% 0,rgba(251,207,232,.9),transparent 55%),linear-gradient(170deg,#fdf2f8,#fbcfe8 50%,#f9a8d4)" },
  fondo_nebulosa: { canvas: "nebulosa", css: "background:#03010d", oscuro: true },
  fondo_dragon: { canvas: "brasas", css: "background:radial-gradient(ellipse at 50% 110%,rgba(249,115,22,.55),transparent 60%),radial-gradient(ellipse at 80% 20%,rgba(220,38,38,.35),transparent 50%),linear-gradient(#1c0505,#3b0a0a 60%,#120202)", oscuro: true },
  fondo_sol_retro: { css: "background:linear-gradient(transparent 62%,rgba(236,72,153,.0) 62%),repeating-linear-gradient(90deg,transparent 0 58px,rgba(236,72,153,.55) 58px 60px),repeating-linear-gradient(0deg,transparent 0 38px,rgba(236,72,153,.55) 38px 40px),radial-gradient(circle at 50% 62%,#fde047 0 9%,#fb923c 9.5% 13%,transparent 13.5%),linear-gradient(#1e1036 0%,#4c1d95 45%,#be185d 62%,#0f0524 62.2%);background-size:100% 100%,100% 38%,100% 38%,100% 100%,100% 100%;background-position:0 0,0 100%,0 100%,0 0,0 0;background-repeat:no-repeat;animation:cc-grid 2.4s linear infinite", oscuro: true },
  fondo_noche_campo: { css: "background:radial-gradient(3px 3px at 12% 30%,#fde047,transparent),radial-gradient(2px 2px at 30% 60%,#fef08a,transparent),radial-gradient(3px 3px at 52% 22%,#fde047,transparent),radial-gradient(2px 2px at 70% 70%,#fef08a,transparent),radial-gradient(3px 3px at 86% 40%,#fde047,transparent),radial-gradient(2px 2px at 44% 82%,#fde047,transparent),linear-gradient(180deg,#020617 0%,#052e16 70%,#022c22 100%);background-size:240px 240px,310px 310px,270px 270px,330px 330px,290px 290px,260px 260px,100% 100%;animation:cc-titilar 3.5s ease-in-out infinite alternate", oscuro: true },
  fondo_papel_cuadros: { css: "background:linear-gradient(rgba(59,130,246,.22) 1px,transparent 1px) 0 0/22px 22px,linear-gradient(90deg,rgba(59,130,246,.22) 1px,transparent 1px) 0 0/22px 22px,#fbfdff" },
  fondo_crt: { css: "background:repeating-linear-gradient(0deg,rgba(0,0,0,.35) 0 1px,transparent 1px 3px),radial-gradient(ellipse at center,#064e3b 0%,#022c22 70%,#000 100%);animation:cc-titilar 4s ease-in-out infinite alternate", oscuro: true },
  fondo_nebulosa_rosa: { css: "background:radial-gradient(1px 1px at 15% 25%,#fff,transparent),radial-gradient(1.5px 1.5px at 65% 15%,#fff,transparent),radial-gradient(1px 1px at 80% 75%,#fff,transparent),radial-gradient(1px 1px at 35% 85%,#fff,transparent),radial-gradient(45% 40% at 30% 40%,rgba(236,72,153,.55),transparent 70%),radial-gradient(40% 45% at 70% 60%,rgba(139,92,246,.55),transparent 70%),radial-gradient(35% 30% at 55% 30%,rgba(56,189,248,.35),transparent 70%),#0b0418;background-size:250px 250px,320px 320px,280px 280px,300px 300px,200% 200%,200% 200%,200% 200%,100% 100%;animation:cc-aurora 22s ease-in-out infinite alternate", oscuro: true },
  fondo_oceano_profundo: { css: "background:radial-gradient(4px 4px at 20% 80%,rgba(255,255,255,.5),transparent),radial-gradient(3px 3px at 60% 90%,rgba(255,255,255,.4),transparent),radial-gradient(5px 5px at 80% 70%,rgba(255,255,255,.35),transparent),repeating-linear-gradient(100deg,transparent 0 80px,rgba(125,211,252,.08) 80px 120px),linear-gradient(180deg,#0e7490 0%,#0c4a6e 35%,#082f49 70%,#020617 100%);background-size:200px 300px,260px 360px,300px 420px,200% 100%,100% 100%;animation:cc-olas 14s linear infinite", oscuro: true },
  fondo_aurora_polar: { css: "background:radial-gradient(70% 40% at 30% 25%,rgba(52,211,153,.55),transparent 70%),radial-gradient(60% 35% at 70% 20%,rgba(34,211,238,.45),transparent 70%),radial-gradient(50% 30% at 50% 35%,rgba(167,139,250,.4),transparent 70%),linear-gradient(180deg,#020617 0%,#0f172a 60%,#e2e8f0 60.3%,#cbd5e1 100%);background-size:200% 200%,200% 200%,200% 200%,100% 100%;animation:cc-aurora 12s ease-in-out infinite alternate", oscuro: true },
};

// -------------------------------------------------------------------------------------- marcos ----
export const MARCOS = {
  marco_neon: "box-shadow:0 0 0 3px #22d3ee,0 0 14px 4px rgba(34,211,238,.7)",
  marco_arcoiris: "background:conic-gradient(#f43f5e,#f59e0b,#84cc16,#22d3ee,#6366f1,#d946ef,#f43f5e) ;animation:cc-rot 4s linear infinite",
  marco_oro: "background:linear-gradient(135deg,#fde68a,#b45309 40%,#fef3c7 55%,#92400e);box-shadow:0 0 12px rgba(251,191,36,.6)",
  marco_fuego: "background:conic-gradient(from 0deg,#7f1d1d,#ef4444,#f97316,#fde047,#f97316,#ef4444,#7f1d1d);box-shadow:0 0 16px rgba(249,115,22,.8);animation:cc-rot 2.2s linear infinite",
  marco_codigo: "background:repeating-conic-gradient(#22c55e 0 12deg,transparent 12deg 24deg);box-shadow:0 0 10px rgba(34,197,94,.6);animation:cc-rot 8s steps(30) infinite",
  marco_hielo: "background:conic-gradient(#e0f2fe,#7dd3fc,#f0f9ff,#38bdf8,#e0f2fe);box-shadow:0 0 14px rgba(125,211,252,.8),inset 0 0 6px #fff;animation:cc-rot 9s linear infinite",
  marco_plasma: "background:conic-gradient(#f0abfc,#6366f1,#22d3ee,#a3e635,#f0abfc);filter:saturate(1.6);box-shadow:0 0 22px 6px rgba(99,102,241,.7);animation:cc-rot 1.6s linear infinite",
  marco_diamante: "background:conic-gradient(#ecfeff,#67e8f9 10%,#fff 20%,#a5f3fc 35%,#e0f2fe 50%,#22d3ee 65%,#fff 80%,#ecfeff);box-shadow:0 0 26px 6px rgba(165,243,252,.85),0 0 4px 1px #fff;animation:cc-rot 5s linear infinite",
  marco_legendario: "background:conic-gradient(#facc15,#a855f7,#22d3ee,#facc15);box-shadow:0 0 20px 4px rgba(168,85,247,.7),0 0 6px 2px rgba(250,204,21,.9);animation:cc-rot 3s linear infinite",
  marco_menta: "background:#6ee7b7;box-shadow:0 0 0 2px #047857",
  marco_cereza: "background:#fb7185;box-shadow:0 0 0 2px #9f1239",
  marco_pixel: "background:repeating-conic-gradient(#f43f5e 0 30deg,#facc15 30deg 60deg,#22d3ee 60deg 90deg,#4ade80 90deg 120deg);animation:cc-rot 6s steps(12) infinite",
  marco_oceano: "background:conic-gradient(#0c4a6e,#38bdf8,#e0f2fe,#0ea5e9,#0c4a6e);box-shadow:0 0 10px rgba(56,189,248,.6);animation:cc-rot 6s linear infinite",
  marco_rayo: "background:repeating-conic-gradient(#fde047 0 14deg,#1f2937 14deg 22deg);box-shadow:0 0 14px rgba(253,224,71,.8);animation:cc-rot 1.2s steps(6) infinite",
  marco_sakura: "background:conic-gradient(#fdf2f8,#f9a8d4,#fff,#f472b6,#fdf2f8);box-shadow:0 0 12px rgba(244,114,182,.6);animation:cc-rot 7s linear infinite",
  marco_galaxia: "background:conic-gradient(from 90deg,#1e1b4b,#7c3aed,#f0abfc,#22d3ee,#1e1b4b);box-shadow:0 0 22px 5px rgba(124,58,237,.65);animation:cc-rot 3.5s linear infinite",
  marco_sol: "background:conic-gradient(#fef3c7,#f59e0b,#fde047,#ea580c,#fef3c7);box-shadow:0 0 26px 8px rgba(245,158,11,.75),0 0 6px 2px #fff7;animation:cc-rot 2.5s linear infinite",
  marco_retro8: "background:conic-gradient(#f43f5e 0 25%,#facc15 0 50%,#4ade80 0 75%,#22d3ee 0);animation:cc-rot 6s steps(8) infinite",
  marco_petalos: "background:repeating-conic-gradient(#f9a8d4 0 20deg,#fdf2f8 20deg 30deg,#f472b6 30deg 45deg);box-shadow:0 0 10px rgba(244,114,182,.55);animation:cc-rot 10s linear infinite",
  marco_cyber: "background:repeating-conic-gradient(#f0abfc 0 8deg,transparent 8deg 16deg,#fde047 16deg 22deg,transparent 22deg 40deg);box-shadow:0 0 12px rgba(240,171,252,.7);animation:cc-rot 3s steps(12) infinite",
  marco_esmeralda: "background:conic-gradient(#064e3b,#34d399,#ecfdf5,#10b981,#065f46,#6ee7b7,#064e3b);box-shadow:0 0 12px rgba(16,185,129,.6),inset 0 0 4px #fff;animation:cc-rot 7s linear infinite",
  marco_lava: "background:conic-gradient(#1c1917,#dc2626,#1c1917,#f97316,#1c1917,#facc15,#1c1917);box-shadow:0 0 16px rgba(220,38,38,.75);animation:cc-rot 5s linear infinite",
  marco_aurora: "background:conic-gradient(#4ade80,#22d3ee,#a78bfa,#f0abfc,#22d3ee,#4ade80);box-shadow:0 0 18px rgba(74,222,128,.55),0 0 30px rgba(167,139,250,.35);animation:cc-rot 6s linear infinite",
  marco_estelar: "background:radial-gradient(circle at 20% 20%,#fff 0 6%,transparent 7%),radial-gradient(circle at 80% 30%,#fff 0 5%,transparent 6%),radial-gradient(circle at 40% 85%,#fff 0 5%,transparent 6%),conic-gradient(#1e1b4b,#6366f1,#1e1b4b,#a855f7,#1e1b4b);box-shadow:0 0 14px rgba(129,140,248,.7);animation:cc-rot 9s linear infinite",
  marco_cristal: "background:conic-gradient(#ecfeff,#a5f3fc,#f0abfc,#ecfeff,#bae6fd,#fde68a,#ecfeff);box-shadow:0 0 16px rgba(165,243,252,.9),inset 0 0 6px #fff;animation:cc-rot 4s linear infinite",
};

const CSS_BASE = `
@keyframes cc-aurora{0%{background-position:0% 0%}100%{background-position:100% 100%}}
@keyframes cc-titilar{0%{filter:brightness(.85)}100%{filter:brightness(1.15)}}
@keyframes cc-grid{to{background-position:0 0,0 62%,0 calc(100% + 34px),0 0,0 0}}
@keyframes cc-olas{to{background-position:160px 100%,-180px 100%,0 0}}
@keyframes cc-cuadricula{to{background-position:0 40px,40px 0,0 0}}
@keyframes cc-rot{to{transform:rotate(360deg)}}
#cc-fondo{position:fixed;inset:0;z-index:-1;pointer-events:none}
#cc-fondo canvas{width:100%;height:100%;display:block}
html.cc-con-fondo body{background:transparent!important}
#cc-fondo::after{content:"";position:absolute;inset:0;background:var(--cc-velo,transparent)}
html.cc-con-fondo :is(.tarjeta,.lado,.inf,.cab,header,nav,aside,.ruta,.teoria,.explorador,.asistente,.editor-tarjeta,.ide-barra,.ide-estado,.lab,.panel,.chat,.pe-cab,.r-pie){-webkit-backdrop-filter:blur(8px) saturate(1.25);backdrop-filter:blur(8px) saturate(1.25)}
html.cc-con-fondo :is(dialog,[role=dialog],[role=menu],[role=listbox],.ide-dialogo,.ide-menu,.ide-avisos,.ide-aviso,.modal,.menu,.toast,.aviso,select option){--panel:var(--cc-panel-solido)!important;--panel2:var(--cc-panel2-solido)!important;--surf:var(--cc-surf-solido)!important;--bg:var(--cc-bg-solido)!important}
.cc-marco{position:relative;display:inline-grid;place-items:center;border-radius:50%;padding:4px;isolation:isolate}
.cc-marco::before{content:"";position:absolute;inset:0;border-radius:50%;z-index:-1}
.cc-marco>*{border-radius:50%}
${Object.entries(MARCOS).map(([k, v]) => `.cc-marco[data-marco="${k}"]::before{${v}}`).join("\n")}
.cc-prev-inicial{display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#0d9488,#4d7c0f);color:#fff;font:800 24px/1 system-ui,sans-serif}
.cc-particula-txt{border-radius:0;white-space:nowrap}
.cc-particula{position:fixed;z-index:9999;pointer-events:none;border-radius:50%;will-change:transform,opacity}
.cc-prev-cursores{display:flex!important;align-items:center;justify-content:center;gap:10px}
.cc-prev-cur{display:grid;justify-items:center;gap:2px;padding:6px 8px;border-radius:10px;background:rgba(255,255,255,.08)}
.cc-prev-cur small{font-size:10.5px;font-weight:700;opacity:.75}
@media (prefers-reduced-motion:reduce){#cc-fondo,#cc-fondo *{animation:none!important}}
`;

function estilo(id, css) {
  let s = document.getElementById(id);
  if (!s) { s = document.createElement("style"); s.id = id; document.head.appendChild(s); }
  s.textContent = css;
}

// ---- animaciones con canvas (fondo de código y brasas)
let pararCanvas = null;
function animarCanvas(tipo, caja) {
  pararCanvas?.();
  const c = document.createElement("canvas");
  caja.appendChild(c);
  const ctx = c.getContext("2d");
  let ancho, alto, cols, gotas, brasas, copos, estrellas, meteoros = [], giro = 0, vivo = true, ultimo = 0;
  const dpr = devicePixelRatio;
  const tamano = () => {
    ancho = c.width = innerWidth * devicePixelRatio; alto = c.height = innerHeight * devicePixelRatio;
    cols = Math.ceil(ancho / (16 * devicePixelRatio)); gotas = Array.from({ length: cols }, () => Math.random() * -alto / 16);
    copos = Array.from({ length: 140 }, () => ({ x: Math.random() * ancho, y: Math.random() * alto, r: (1 + Math.random() * 3) * devicePixelRatio, v: (.3 + Math.random() * 1.1) * devicePixelRatio, f: Math.random() * 6 }));
    estrellas = Array.from({ length: 260 }, () => ({ x: (Math.random() - .5) * ancho, y: (Math.random() - .5) * alto, z: Math.random() * ancho }));
    brasas = Array.from({ length: 70 }, () => ({ x: Math.random() * ancho, y: alto + Math.random() * alto, v: .4 + Math.random() * 1.4, r: (1 + Math.random() * 2.5) * devicePixelRatio, f: Math.random() * 6 }));
  };
  tamano();
  addEventListener("resize", tamano);
  const letras = "01<>/{}[]=+;:()アイウエオカキクケコ$#&*";
  const paso = (t) => {
    if (!vivo) return;
    requestAnimationFrame(paso);
    if (t - ultimo < (tipo === "matrix" ? 60 : 33) || document.hidden) return;
    ultimo = t;
    if (tipo === "matrix") {
      const fs = 16 * devicePixelRatio;
      ctx.fillStyle = "rgba(1,10,4,.12)"; ctx.fillRect(0, 0, ancho, alto);
      ctx.font = `${fs}px ui-monospace,Consolas,monospace`;
      for (let i = 0; i < cols; i++) {
        const y = gotas[i] * fs;
        ctx.fillStyle = Math.random() < .04 ? "#d1fae5" : "#22c55e";
        ctx.fillText(letras[(Math.random() * letras.length) | 0], i * fs, y);
        if (y > alto && Math.random() > .975) gotas[i] = 0; else gotas[i] += 1;
      }
    } else if (tipo === "nieve" || tipo === "luciernagas") {
      ctx.clearRect(0, 0, ancho, alto);
      const luz = tipo === "luciernagas";
      for (const c of copos.slice(0, luz ? 70 : 140)) {
        c.f += .03;
        if (luz) { c.x += Math.cos(c.f) * .7 * devicePixelRatio; c.y += Math.sin(c.f * .7) * .5 * devicePixelRatio; }
        else { c.y += c.v; c.x += Math.sin(c.f) * .5; if (c.y > alto + 5) { c.y = -5; c.x = Math.random() * ancho; } }
        const a = luz ? .35 + .65 * Math.abs(Math.sin(c.f * 1.7)) : .85;
        if (luz) { const g = ctx.createRadialGradient(c.x, c.y, 0, c.x, c.y, c.r * 5); g.addColorStop(0, `rgba(253,224,71,${a})`); g.addColorStop(1, "rgba(253,224,71,0)"); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(c.x, c.y, c.r * 5, 0, 7); ctx.fill(); }
        else { ctx.fillStyle = `rgba(255,255,255,${a})`; ctx.beginPath(); ctx.arc(c.x, c.y, c.r, 0, 7); ctx.fill(); }
      }
    } else if (tipo === "hiper") {
      ctx.fillStyle = "rgba(2,6,23,.35)"; ctx.fillRect(0, 0, ancho, alto);
      const cx = ancho / 2, cy = alto / 2;
      for (const e of estrellas) {
        const pz = e.z; e.z -= 14 * devicePixelRatio;
        if (e.z < 1) { e.x = (Math.random() - .5) * ancho; e.y = (Math.random() - .5) * alto; e.z = ancho; continue; }
        const k = 260 * devicePixelRatio, x1 = cx + e.x / pz * k, y1 = cy + e.y / pz * k, x2 = cx + e.x / e.z * k, y2 = cy + e.y / e.z * k;
        ctx.strokeStyle = `rgba(${180 + (1 - e.z / ancho) * 75 | 0},${200 + (1 - e.z / ancho) * 55 | 0},255,${1 - e.z / ancho})`;
        ctx.lineWidth = (1 - e.z / ancho) * 2.5 * devicePixelRatio; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      }
    } else if (tipo === "lluvia") {
      ctx.clearRect(0, 0, ancho, alto);
      ctx.strokeStyle = "rgba(186,230,253,.5)"; ctx.lineWidth = 1.2 * dpr;
      ctx.beginPath();
      for (const c of copos) {
        c.y += c.v * 9; c.x -= c.v * 1.4;
        if (c.y > alto) { c.y = -20 * dpr; c.x = Math.random() * ancho * 1.2; }
        ctx.moveTo(c.x, c.y); ctx.lineTo(c.x - 2 * dpr, c.y + 10 * dpr + c.r * 3);
      }
      ctx.stroke();
    } else if (tipo === "burbujas") {
      ctx.clearRect(0, 0, ancho, alto);
      for (const c of copos.slice(0, 60)) {
        c.y -= c.v * 1.1; c.f += .02; c.x += Math.sin(c.f) * .6 * dpr;
        if (c.y < -20 * dpr) { c.y = alto + 20 * dpr; c.x = Math.random() * ancho; }
        ctx.strokeStyle = "rgba(224,242,254,.55)"; ctx.lineWidth = 1.2 * dpr;
        ctx.beginPath(); ctx.arc(c.x, c.y, c.r * 2.6, 0, 7); ctx.stroke();
        ctx.fillStyle = "rgba(255,255,255,.45)"; ctx.beginPath(); ctx.arc(c.x - c.r, c.y - c.r, c.r * .6, 0, 7); ctx.fill();
      }
    } else if (tipo === "sakura") {
      ctx.clearRect(0, 0, ancho, alto);
      for (const c of copos.slice(0, 70)) {
        c.y += c.v * .9; c.f += .03; c.x += Math.sin(c.f) * 1.1 * dpr;
        if (c.y > alto + 10 * dpr) { c.y = -10 * dpr; c.x = Math.random() * ancho; }
        ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(c.f);
        ctx.fillStyle = c.r > 2.5 * dpr ? "rgba(244,114,182,.85)" : "rgba(251,207,232,.95)";
        ctx.beginPath(); ctx.ellipse(0, 0, c.r * 2.2, c.r * 1.3, 0, 0, 7); ctx.fill(); ctx.restore();
      }
    } else if (tipo === "fugaces") {
      ctx.clearRect(0, 0, ancho, alto);
      if (Math.random() < .035 && meteoros.length < 4) meteoros.push({ x: Math.random() * ancho, y: Math.random() * alto * .45, vx: -(9 + Math.random() * 7) * dpr, vy: (4 + Math.random() * 3) * dpr, vida: 1 });
      for (const m of meteoros) {
        m.x += m.vx; m.y += m.vy; m.vida -= .018;
        const g = ctx.createLinearGradient(m.x, m.y, m.x - m.vx * 9, m.y - m.vy * 9);
        g.addColorStop(0, `rgba(255,255,255,${m.vida})`); g.addColorStop(1, "rgba(165,243,252,0)");
        ctx.strokeStyle = g; ctx.lineWidth = 2 * dpr; ctx.beginPath(); ctx.moveTo(m.x, m.y); ctx.lineTo(m.x - m.vx * 9, m.y - m.vy * 9); ctx.stroke();
      }
      meteoros = meteoros.filter((m) => m.vida > 0 && m.x > -100);
      for (const e of estrellas.slice(0, 90)) { e.z -= 3; if (e.z < 0) e.z = ancho; const a = .3 + .7 * Math.abs(Math.sin(e.z / 90)); ctx.fillStyle = `rgba(255,255,255,${a})`; ctx.fillRect(ancho / 2 + e.x, alto / 2 + e.y, 1.4 * dpr, 1.4 * dpr); }
    } else if (tipo === "nebulosa") {
      giro += .004;
      ctx.fillStyle = "rgba(3,1,13,.18)"; ctx.fillRect(0, 0, ancho, alto);
      const nubes = [["168,85,247", .3, .35], ["34,211,238", .7, .4], ["244,114,182", .5, .7], ["99,102,241", .2, .75], ["250,204,21", .8, .8]];
      nubes.forEach(([col, px, py], k) => {
        const x = ancho * (px + Math.sin(giro + k) * .06), y = alto * (py + Math.cos(giro * 1.3 + k) * .05), r = Math.max(ancho, alto) * (.28 + .05 * Math.sin(giro * 2 + k));
        const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(${col},.10)`); g.addColorStop(1, `rgba(${col},0)`);
        ctx.fillStyle = g; ctx.fillRect(0, 0, ancho, alto);
      });
      for (const e of estrellas.slice(0, 160)) { const a = .4 + .6 * Math.abs(Math.sin(giro * 6 + e.z)); ctx.fillStyle = `rgba(255,255,255,${a})`; ctx.fillRect(ancho / 2 + e.x, alto / 2 + e.y, 1.2 * dpr, 1.2 * dpr); }
    } else if (tipo === "agujero") {
      ctx.fillStyle = "rgba(2,6,23,.25)"; ctx.fillRect(0, 0, ancho, alto);
      const cx = ancho / 2, cy = alto / 2; giro += .012;
      for (let i = 0; i < 160; i++) {
        const r = (60 + (i * 7 % 480)) * devicePixelRatio, a = giro * (900 / (r / devicePixelRatio + 40)) + i * 2.4;
        const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r * .42;
        const t = Math.min(1, 140 * devicePixelRatio / r);
        ctx.fillStyle = `rgba(${250},${150 + 90 * t | 0},${60 + 160 * (1 - t) | 0},${.25 + .6 * t})`; ctx.beginPath(); ctx.arc(x, y, (1 + 2.5 * t) * devicePixelRatio, 0, 7); ctx.fill();
      }
      ctx.fillStyle = "#000"; ctx.beginPath(); ctx.arc(cx, cy, 52 * devicePixelRatio, 0, 7); ctx.fill();
    } else {
      ctx.clearRect(0, 0, ancho, alto);
      for (const b of brasas) {
        b.y -= b.v * devicePixelRatio; b.x += Math.sin((b.y / 40) + b.f) * .6;
        if (b.y < -10) { b.y = alto + 10; b.x = Math.random() * ancho; }
        const a = Math.max(0, Math.min(1, b.y / alto));
        ctx.fillStyle = `rgba(${250},${120 + 100 * a | 0},${30},${.25 + .6 * a})`;
        ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, 7); ctx.fill();
      }
    }
  };
  if (!reducido()) requestAnimationFrame(paso);
  pararCanvas = () => { vivo = false; removeEventListener("resize", tamano); c.remove(); pararCanvas = null; };
}

// ---- efectos al hacer clic / mover el mouse
let quitarEfecto = null;
function particula(x, y, { color, tam, dx, dy, dur, forma }) {
  const p = document.createElement("span");
  p.className = "cc-particula";
  p.style.cssText = `left:${x}px;top:${y}px;width:${tam}px;height:${tam}px;${forma === "estrella" ? `background:none;color:${color};font-size:${tam * 1.6}px;line-height:1` : forma === "burbuja" ? `border:2px solid ${color};background:rgba(255,255,255,.15)` : forma === "cuadro" ? `background:${color};border-radius:2px` : forma === "pixel" ? `background:${color};border-radius:0;box-shadow:none` : `background:${color};box-shadow:0 0 6px ${color}`}`;
  if (forma === "estrella") p.textContent = "✦";
  if (forma === "corazon") { p.textContent = "♥"; p.style.background = "none"; p.style.color = color; p.style.fontSize = `${tam * 1.5}px`; p.style.lineHeight = "1"; }
  if (forma === "moneda") { p.style.background = `radial-gradient(circle at 35% 30%,#fef3c7,${color} 45%,#b45309)`; p.style.border = "1px solid #92400e"; }
  document.body.appendChild(p);
  p.animate([{ transform: "translate(-50%,-50%) scale(1)", opacity: 1 }, { transform: `translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) scale(${forma === "burbuja" ? 1.6 : .4}) rotate(${forma === "cuadro" ? 540 : 0}deg)`, opacity: 0 }], { duration: dur, easing: "cubic-bezier(.2,.7,.3,1)" }).onfinish = () => p.remove();
}
export const EFECTOS = {
  efecto_burbujas: (x, y) => { for (let i = 0; i < 6; i++) particula(x, y, { color: "#7dd3fc", tam: 8 + Math.random() * 12, dx: (Math.random() - .5) * 60, dy: -40 - Math.random() * 70, dur: 900 + Math.random() * 500, forma: "burbuja" }); },
  efecto_confeti: (x, y) => { const c = ["#f43f5e", "#f59e0b", "#84cc16", "#22d3ee", "#a855f7"]; for (let i = 0; i < 14; i++) particula(x, y, { color: c[i % 5], tam: 6 + Math.random() * 5, dx: (Math.random() - .5) * 180, dy: (Math.random() - .7) * 160, dur: 900 + Math.random() * 400, forma: "cuadro" }); },
  efecto_chispas: (x, y) => { for (let i = 0; i < 10; i++) { const a = (i / 10) * Math.PI * 2; particula(x, y, { color: "#fde047", tam: 4, dx: Math.cos(a) * 50, dy: Math.sin(a) * 50, dur: 500, forma: "punto" }); } },
  efecto_estela: null, // se maneja con el movimiento del mouse
  efecto_corazones: (x, y) => { for (let i = 0; i < 7; i++) particula(x, y, { color: ["#f43f5e", "#ec4899", "#fb7185"][i % 3], tam: 11 + Math.random() * 8, dx: (Math.random() - .5) * 90, dy: -50 - Math.random() * 80, dur: 1000 + Math.random() * 400, forma: "corazon" }); },
  efecto_monedas: (x, y) => { for (let i = 0; i < 9; i++) particula(x, y, { color: "#fbbf24", tam: 12, dx: (Math.random() - .5) * 140, dy: -60 - Math.random() * 90, dur: 900 + Math.random() * 300, forma: "moneda" }); },
  efecto_rayos: (x, y) => { for (let i = 0; i < 12; i++) { const a = Math.random() * Math.PI * 2, d = 30 + Math.random() * 60; particula(x, y, { color: i % 2 ? "#a5f3fc" : "#fde047", tam: 3 + Math.random() * 3, dx: Math.cos(a) * d, dy: Math.sin(a) * d, dur: 260 + Math.random() * 200, forma: "punto" }); } },
  efecto_estrellas: (x, y) => { for (let i = 0; i < 8; i++) particula(x, y, { color: i % 2 ? "#facc15" : "#fde68a", tam: 8 + Math.random() * 5, dx: (Math.random() - .5) * 90, dy: (Math.random() - .5) * 90, dur: 800, forma: "estrella" }); },
  efecto_nieve: (x, y) => { for (let i = 0; i < 7; i++) texto(x, y, "❄", { color: i % 2 ? "#e0f2fe" : "#7dd3fc", tam: 12 + Math.random() * 10, dx: (Math.random() - .5) * 90, dy: 30 + Math.random() * 60, dur: 1300 }); },
  efecto_codigo: (x, y) => { const t = ["{ }", "</>", "01", ";", "=>", "()", "[ ]", "#"]; for (let i = 0; i < 9; i++) { const a = (i / 9) * Math.PI * 2; texto(x, y, t[i % t.length], { color: ["#4ade80", "#22d3ee", "#facc15"][i % 3], tam: 13, dx: Math.cos(a) * 70, dy: Math.sin(a) * 70, dur: 800 }); } },
  efecto_ondas: (x, y) => { [0, 140, 280].forEach((d, k) => setTimeout(() => onda(x, y, ["#38bdf8", "#7dd3fc", "#bae6fd"][k], 3.6 + k), d)); },
  efecto_emojis: (x, y) => { const e = ["🎉", "✨", "🔥", "🚀", "💯", "⭐"]; for (let i = 0; i < 7; i++) texto(x, y, e[(Math.random() * e.length) | 0], { color: "transparent", tam: 18 + Math.random() * 8, dx: (Math.random() - .5) * 140, dy: -50 - Math.random() * 90, dur: 1100, emoji: true }); },
  efecto_pixeles: (x, y) => { const c = ["#f43f5e", "#facc15", "#4ade80", "#22d3ee", "#a855f7", "#fb923c"]; for (let i = 0; i < 20; i++) { const a = Math.random() * Math.PI * 2, d = 30 + Math.random() * 80; particula(x, y, { color: c[i % c.length], tam: 6, dx: Math.cos(a) * d, dy: Math.sin(a) * d + 20, dur: 700 + Math.random() * 300, forma: "pixel" }); } },
  efecto_supernova: (x, y) => { onda(x, y, "#fde68a", 6); setTimeout(() => onda(x, y, "#c084fc", 8), 90); for (let i = 0; i < 24; i++) { const a = (i / 24) * Math.PI * 2; particula(x, y, { color: i % 2 ? "#fff" : "#f0abfc", tam: i % 3 ? 4 : 9, dx: Math.cos(a) * 110, dy: Math.sin(a) * 110, dur: 1000, forma: i % 3 ? "punto" : "estrella" }); } },
  efecto_fuegos: (x, y) => { const c = ["#f43f5e", "#facc15", "#22d3ee", "#a855f7", "#4ade80", "#fb923c"]; const base = c[(Math.random() * c.length) | 0]; for (let i = 0; i < 28; i++) { const a = (i / 28) * Math.PI * 2, d = 70 + Math.random() * 50; particula(x, y, { color: i % 3 ? base : "#fff", tam: 4 + Math.random() * 3, dx: Math.cos(a) * d, dy: Math.sin(a) * d + 20, dur: 900 + Math.random() * 500, forma: "punto" }); } },
  efecto_globos: (x, y) => { const c = ["#f43f5e", "#facc15", "#4ade80", "#38bdf8", "#a855f7"]; for (let i = 0; i < 5; i++) particula(x, y, { color: c[i], tam: 18 + Math.random() * 8, dx: (Math.random() - .5) * 120, dy: -120 - Math.random() * 80, dur: 1600 + Math.random() * 400, forma: "burbuja" }); },
  efecto_notas: (x, y) => { const n = ["♪", "♫", "♬", "♩", "𝄞"]; for (let i = 0; i < 8; i++) { const a = (i / 8) * Math.PI * 2; texto(x, y, n[i % n.length], { color: ["#a855f7", "#22d3ee", "#f472b6", "#facc15"][i % 4], tam: 16 + Math.random() * 6, dx: Math.cos(a) * 70, dy: Math.sin(a) * 70 - 20, dur: 1000, girar: 30 }); } },
  efecto_hojas: (x, y) => { for (let i = 0; i < 9; i++) texto(x, y, ["🍂", "🍁"][i % 2], { color: "transparent", tam: 16 + Math.random() * 8, dx: 40 + Math.random() * 110, dy: -30 + Math.random() * 90, dur: 1300, girar: 300, emoji: true }); },
  efecto_tinta: (x, y) => { const c = ["#2563eb", "#db2777", "#16a34a", "#f59e0b"][(Math.random() * 4) | 0]; particula(x, y, { color: c, tam: 26, dx: 0, dy: 0, dur: 700, forma: "punto" }); for (let i = 0; i < 12; i++) { const a = Math.random() * Math.PI * 2, d = 20 + Math.random() * 50; particula(x, y, { color: c, tam: 4 + Math.random() * 7, dx: Math.cos(a) * d, dy: Math.sin(a) * d, dur: 650, forma: "punto" }); } },
  efecto_portal: (x, y) => { onda(x, y, "#a855f7", 4); setTimeout(() => onda(x, y, "#22d3ee", 3), 120); setTimeout(() => onda(x, y, "#f0abfc", 2), 240); for (let i = 0; i < 16; i++) { const a = (i / 16) * Math.PI * 2; particula(x + Math.cos(a) * 60, y + Math.sin(a) * 60, { color: i % 2 ? "#a855f7" : "#22d3ee", tam: 5, dx: -Math.cos(a) * 60, dy: -Math.sin(a) * 60, dur: 600, forma: "punto" }); } },
  efecto_meteoro: (x, y) => { for (let k = 0; k < 4; k++) setTimeout(() => { const ox = x - 160 - Math.random() * 60, oy = y - 160 - Math.random() * 60; for (let i = 0; i < 8; i++) particula(ox + i * 20, oy + i * 20, { color: i > 5 ? "#fff" : "#fb923c", tam: 3 + i, dx: 160 - i * 20, dy: 160 - i * 20, dur: 420, forma: "punto" }); setTimeout(() => { onda(x + (k - 1.5) * 30, y, "#fdba74", 2.5); for (let i = 0; i < 10; i++) { const a = Math.random() * Math.PI * 2; particula(x + (k - 1.5) * 30, y, { color: ["#facc15", "#fb923c", "#fff"][i % 3], tam: 4, dx: Math.cos(a) * 45, dy: Math.sin(a) * 45, dur: 500, forma: "punto" }); } }, 400); }, k * 110); },
};

// ---- rastros: siguen el mouse (computador) y el dedo (celular, también al desplazar)
const ARCOIRIS = ["#f43f5e", "#f59e0b", "#facc15", "#4ade80", "#22d3ee", "#6366f1", "#d946ef"];
function texto(x, y, ch, { color, tam, dx, dy, dur, emoji = false, girar = 0 }) {
  const p = document.createElement("span");
  p.className = "cc-particula cc-particula-txt";
  p.textContent = ch;
  p.style.cssText = emoji ? `left:${x}px;top:${y}px;font:${tam}px/1 system-ui,"Segoe UI Emoji","Apple Color Emoji",sans-serif` : `left:${x}px;top:${y}px;color:${color};font:800 ${tam}px/1 ui-monospace,Consolas,monospace;text-shadow:0 0 6px ${color}`;
  if (girar) { document.body.appendChild(p); p.animate([{ transform: "translate(-50%,-50%) rotate(0)", opacity: 1 }, { transform: `translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) rotate(${girar}deg)`, opacity: 0 }], { duration: dur, easing: "ease-out" }).onfinish = () => p.remove(); return; }
  document.body.appendChild(p);
  p.animate([{ transform: "translate(-50%,-50%)", opacity: 1 }, { transform: `translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px))`, opacity: 0 }], { duration: dur, easing: "ease-out" }).onfinish = () => p.remove();
}
/** Cada estela: mover(x, y, i) se llama mientras el dedo se desliza; tocar(x, y) al apoyar el dedo. */
export const DEDOS = {
  dedo_tinta: { mover: (x, y) => particula(x, y, { color: "#3b82f6", tam: 7 + Math.random() * 6, dx: (Math.random() - .5) * 6, dy: 10 + Math.random() * 10, dur: 700, forma: "punto" }) },
  dedo_burbujas: { mover: (x, y, i) => { if (i % 2) particula(x, y, { color: "#7dd3fc", tam: 8 + Math.random() * 12, dx: (Math.random() - .5) * 30, dy: -40 - Math.random() * 50, dur: 1000, forma: "burbuja" }); } },
  dedo_neon: { mover: (x, y) => particula(x, y, { color: "#22d3ee", tam: 9, dx: 0, dy: 0, dur: 520, forma: "punto" }) },
  dedo_codigo: { mover: (x, y, i) => { if (i % 2 === 0) texto(x, y, ["{", "}", "<", "/>", "0", "1", ";", "()", "=>"][(Math.random() * 9) | 0], { color: i % 4 ? "#4ade80" : "#a3e635", tam: 13 + Math.random() * 5, dx: (Math.random() - .5) * 20, dy: 30 + Math.random() * 30, dur: 900 }); } },
  dedo_arcoiris: { mover: (x, y, i) => particula(x, y, { color: ARCOIRIS[i % ARCOIRIS.length], tam: 12, dx: 0, dy: 4, dur: 650, forma: "punto" }) },
  dedo_fuego: { mover: (x, y) => { for (let k = 0; k < 2; k++) particula(x + (Math.random() - .5) * 8, y, { color: ["#f97316", "#facc15", "#ef4444"][(Math.random() * 3) | 0], tam: 6 + Math.random() * 7, dx: (Math.random() - .5) * 18, dy: -30 - Math.random() * 40, dur: 600 + Math.random() * 300, forma: "punto" }); } },
  dedo_galaxia: {
    mover: (x, y, i) => { particula(x, y, { color: ["#c084fc", "#67e8f9", "#f0abfc", "#fde68a"][i % 4], tam: 4 + Math.random() * 4, dx: (Math.random() - .5) * 26, dy: (Math.random() - .5) * 26, dur: 800, forma: "punto" }); if (i % 3 === 0) particula(x, y, { color: "#fff", tam: 9, dx: (Math.random() - .5) * 30, dy: (Math.random() - .5) * 30, dur: 900, forma: "estrella" }); },
    tocar: (x, y) => { for (let k = 0; k < 10; k++) { const a = (k / 10) * Math.PI * 2; particula(x, y, { color: k % 2 ? "#c084fc" : "#67e8f9", tam: 4, dx: Math.cos(a) * 40, dy: Math.sin(a) * 40, dur: 600, forma: "punto" }); } },
  },
  dedo_estrellas: { mover: (x, y, i) => { if (i % 2 === 0) particula(x, y, { color: i % 4 ? "#facc15" : "#fde68a", tam: 8 + Math.random() * 5, dx: (Math.random() - .5) * 20, dy: 20 + Math.random() * 25, dur: 800, forma: "estrella" }); } },
  dedo_nieve: { mover: (x, y, i) => { if (i % 3 === 0) texto(x, y, "❄", { color: "#e0f2fe", tam: 11 + Math.random() * 9, dx: (Math.random() - .5) * 26, dy: 30 + Math.random() * 30, dur: 1400, girar: 180 }); } },
  dedo_corazones: { mover: (x, y, i) => { if (i % 3 === 0) particula(x, y, { color: ["#f43f5e", "#ec4899", "#fb7185"][i % 3], tam: 10 + Math.random() * 6, dx: (Math.random() - .5) * 24, dy: -30 - Math.random() * 30, dur: 1000, forma: "corazon" }); } },
  dedo_pixeles: { mover: (x, y, i) => particula(x + (Math.random() - .5) * 10, y + (Math.random() - .5) * 10, { color: ["#f43f5e", "#facc15", "#4ade80", "#22d3ee", "#a855f7"][i % 5], tam: 7, dx: 0, dy: 12, dur: 600, forma: "pixel" }) },
  dedo_rayo: { mover: (x, y, i) => { particula(x, y, { color: "#fde047", tam: 5, dx: 0, dy: 0, dur: 300, forma: "punto" }); if (i % 2 === 0) { const a = Math.random() * Math.PI * 2; particula(x, y, { color: i % 4 ? "#a5f3fc" : "#fde047", tam: 3, dx: Math.cos(a) * 30, dy: Math.sin(a) * 30, dur: 300, forma: "punto" }); } } },
  dedo_sakura: { mover: (x, y, i) => { if (i % 2 === 0) texto(x, y, "❀", { color: i % 4 ? "#f9a8d4" : "#f472b6", tam: 13 + Math.random() * 7, dx: (Math.random() - .5) * 40, dy: 30 + Math.random() * 40, dur: 1300, girar: 240 }); } },
  dedo_cometa: {
    mover: (x, y, i) => { particula(x, y, { color: "#e0f2fe", tam: 14, dx: 0, dy: 0, dur: 420, forma: "punto" }); particula(x, y, { color: "#38bdf8", tam: 8, dx: (Math.random() - .5) * 8, dy: (Math.random() - .5) * 8, dur: 700, forma: "punto" }); if (i % 3 === 0) particula(x, y, { color: "#fff", tam: 8, dx: (Math.random() - .5) * 50, dy: (Math.random() - .5) * 50, dur: 700, forma: "estrella" }); },
    tocar: (x, y) => onda(x, y, "#7dd3fc", 3),
  },
  dedo_hojas: { mover: (x, y, i) => { if (i % 3 === 0) texto(x, y, ["🍂", "🍁"][i % 2], { color: "transparent", tam: 14 + Math.random() * 6, dx: (Math.random() - .3) * 40, dy: 40 + Math.random() * 40, dur: 1400, girar: 260, emoji: true }); } },
  dedo_notas: { mover: (x, y, i) => { if (i % 3 === 0) texto(x, y, ["♪", "♫", "♬", "♩"][i % 4], { color: ["#a855f7", "#22d3ee", "#f472b6"][i % 3], tam: 15 + Math.random() * 6, dx: (Math.random() - .5) * 30, dy: -30 - Math.random() * 30, dur: 1100, girar: 25 }); } },
  dedo_confeti: { mover: (x, y, i) => particula(x, y, { color: ["#f43f5e", "#facc15", "#4ade80", "#38bdf8", "#a855f7"][i % 5], tam: 5 + Math.random() * 4, dx: (Math.random() - .5) * 40, dy: 30 + Math.random() * 40, dur: 900, forma: "cuadro" }) },
  dedo_luciernagas: { mover: (x, y, i) => { if (i % 2 === 0) particula(x + (Math.random() - .5) * 20, y + (Math.random() - .5) * 20, { color: "#fde047", tam: 4 + Math.random() * 3, dx: (Math.random() - .5) * 40, dy: (Math.random() - .5) * 40, dur: 1600 + Math.random() * 600, forma: "punto" }); } },
  dedo_humo: { mover: (x, y, i) => { if (i % 2 === 0) particula(x, y, { color: ["rgba(244,114,182,.45)", "rgba(56,189,248,.45)", "rgba(167,139,250,.45)"][i % 3], tam: 18 + Math.random() * 14, dx: (Math.random() - .5) * 30, dy: -25 - Math.random() * 20, dur: 1300, forma: "punto" }); } },
  dedo_dragon: {
    mover: (x, y, i) => { for (let k = 0; k < 2; k++) particula(x + (Math.random() - .5) * 10, y, { color: ["#dc2626", "#f97316", "#facc15"][(Math.random() * 3) | 0], tam: 7 + Math.random() * 8, dx: (Math.random() - .5) * 26, dy: -36 - Math.random() * 40, dur: 650 + Math.random() * 300, forma: "punto" }); if (i % 3 === 0) particula(x, y, { color: "#fde68a", tam: 9, dx: (Math.random() - .5) * 50, dy: (Math.random() - .5) * 50, dur: 800, forma: "estrella" }); },
    tocar: (x, y) => { onda(x, y, "#f97316", 3.2); for (let k = 0; k < 12; k++) { const a = (k / 12) * Math.PI * 2; particula(x, y, { color: k % 2 ? "#facc15" : "#dc2626", tam: 6, dx: Math.cos(a) * 50, dy: Math.sin(a) * 50, dur: 600, forma: "punto" }); } },
  },
  dedo_mito: {
    mover: (x, y, i) => { particula(x, y, { color: ARCOIRIS[i % ARCOIRIS.length], tam: 10, dx: 0, dy: 0, dur: 600, forma: "punto" }); if (i % 2 === 0) particula(x, y, { color: "#fff", tam: 8 + Math.random() * 5, dx: (Math.random() - .5) * 50, dy: (Math.random() - .5) * 50, dur: 900, forma: "estrella" }); if (i % 5 === 0) texto(x, y, "✦", { color: "#fde68a", tam: 18, dx: 0, dy: -40, dur: 1000, girar: 180 }); },
    tocar: (x, y) => { onda(x, y, "#f0abfc", 3.5); setTimeout(() => onda(x, y, "#fde68a", 2.5), 120); },
  },
};
function onda(x, y, color, escala = 2.6) {
  const p = document.createElement("span");
  p.className = "cc-particula";
  p.style.cssText = `left:${x}px;top:${y}px;width:18px;height:18px;border:2px solid ${color};background:none`;
  document.body.appendChild(p);
  p.animate([{ transform: "translate(-50%,-50%) scale(.4)", opacity: .9 }, { transform: `translate(-50%,-50%) scale(${escala})`, opacity: 0 }], { duration: 450, easing: "ease-out" }).onfinish = () => p.remove();
}
const COLOR_DEDO = { dedo_tinta: "#3b82f6", dedo_burbujas: "#7dd3fc", dedo_neon: "#22d3ee", dedo_codigo: "#4ade80", dedo_arcoiris: "#f59e0b", dedo_fuego: "#f97316", dedo_galaxia: "#c084fc",
  dedo_estrellas: "#facc15", dedo_nieve: "#bae6fd", dedo_corazones: "#f43f5e", dedo_pixeles: "#a855f7", dedo_rayo: "#fde047", dedo_sakura: "#f472b6", dedo_cometa: "#38bdf8",
  dedo_hojas: "#f97316", dedo_notas: "#a855f7", dedo_confeti: "#f43f5e", dedo_luciernagas: "#fde047", dedo_humo: "#a78bfa", dedo_dragon: "#f97316", dedo_mito: "#f0abfc" };

/**
 * Rastro: sigue al mouse (en el computador, solo con moverlo) y al dedo (en el celular, también mientras desplazas
 * la pantalla). zona: window en las páginas, o la tarjeta de la tienda para probarlo.
 * Con el dedo se usan eventos táctiles (touchstart/touchmove), no pointer: al desplazar, el navegador cancela el
 * «pointer» (pointercancel) y antes el rastro se cortaba; touchmove sigue llegando mientras la página se mueve.
 */
export function seguirDedo(zona, clave) {
  const e = DEDOS[clave];
  if (!e) return () => {};
  const enZona = zona !== window;
  let tocando = false, i = 0, ultimo = 0, ux = null, uy = null, tMouse = 0;
  const pintar = (x, y, max) => {
    if (ux === null) { ux = x; uy = y; e.mover(x, y, i++); return; }
    const pasos = Math.min(max, Math.max(1, Math.round(Math.hypot(x - ux, y - uy) / 14)));
    for (let k = 1; k <= pasos; k++) e.mover(ux + (x - ux) * k / pasos, uy + (y - uy) * k / pasos, i++);
    ux = x; uy = y;
  };
  const viva = () => { if (enZona && !zona.isConnected) { quitar(); return false; } return true; };
  // ---- mouse (y lápiz): basta con mover
  const mouse = (ev) => {
    if (ev.pointerType === "touch" || !viva()) return;
    const t = performance.now();
    if (t - ultimo < 22) return;
    if (t - tMouse > 160) ux = null;          // volvió a mover después de un rato: empieza de nuevo (sin línea larga)
    ultimo = tMouse = t;
    pintar(ev.clientX, ev.clientY, 3);
  };
  const salir = () => { ux = null; };
  // ---- dedo
  // Mientras la pantalla se desplaza, Chrome en Android manda touchmove solo cada ~200 ms (el rastro se veía
  // cortado). El desplazamiento sí llega en cada cuadro: el dedo está donde estaba MENOS lo que se movió el contenido.
  let fx = 0, fy = 0;
  const marcas = new Map();   // elemento que se desplaza -> [scrollTop, scrollLeft] cuando se vio el dedo
  const pos = (el) => (el === document || el === document.scrollingElement || el === document.documentElement ? [scrollY, scrollX] : [el.scrollTop, el.scrollLeft]);
  const marcar = (desde) => {
    marcas.clear();
    marcas.set(document, pos(document));
    for (let el = desde; el && el !== document.body && el.nodeType === 1; el = el.parentElement) {
      if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) marcas.set(el, pos(el));
    }
  };
  const inicio = (ev) => {
    if (!viva()) return;
    const p = ev.touches[0];
    tocando = true; ux = fx = p.clientX; uy = fy = p.clientY;
    marcar(ev.target);
    onda(ux, uy, COLOR_DEDO[clave]); e.tocar?.(ux, uy);
  };
  const movido = (ev) => {
    if (!tocando || !viva()) return;
    const p = ev.touches[0];
    if (!p) return;
    fx = p.clientX; fy = p.clientY;
    for (const el of marcas.keys()) marcas.set(el, pos(el));
    const t = performance.now();
    if (t - ultimo < 16) return;
    ultimo = t;
    pintar(fx, fy, 4);
  };
  const desplazado = (ev) => {
    if (!tocando || ux === null || !viva()) return;
    const el = ev.target === document || ev.target === window ? document : ev.target;
    const antes = marcas.get(el);
    const ahora = pos(el);
    marcas.set(el, ahora);
    if (!antes) return;
    const dy = ahora[0] - antes[0], dx = ahora[1] - antes[1];
    if (!dx && !dy) return;
    fx = Math.max(0, Math.min(innerWidth, fx - dx));
    fy = Math.max(0, Math.min(innerHeight, fy - dy));
    const t = performance.now();
    if (t - ultimo < 16) return;
    ultimo = t;
    pintar(fx, fy, 4);
  };
  const fin = (ev) => { if (!ev.touches?.length) { tocando = false; ux = null; marcas.clear(); } };
  zona.addEventListener("pointermove", mouse, { passive: true });
  if (enZona) zona.addEventListener("pointerleave", salir, { passive: true });
  zona.addEventListener("touchstart", inicio, { passive: true });
  addEventListener("touchmove", movido, { passive: true });
  addEventListener("touchend", fin, { passive: true });
  addEventListener("touchcancel", fin, { passive: true });
  document.addEventListener("scroll", desplazado, { capture: true, passive: true });
  const quitar = () => {
    document.removeEventListener("scroll", desplazado, { capture: true });
    zona.removeEventListener("pointermove", mouse); zona.removeEventListener("pointerleave", salir); zona.removeEventListener("touchstart", inicio);
    removeEventListener("touchmove", movido); removeEventListener("touchend", fin); removeEventListener("touchcancel", fin);
  };
  return quitar;
}
let quitarDedo = null;
function activarDedo(clave) {
  quitarDedo?.();
  quitarDedo = null;
  // El rastro lo eligió la persona: se muestra aunque el celular tenga «quitar animaciones» (eso apagaba el rastro sin
  // explicación). Solo se apaga con «Menos movimiento» de Configuración de CódigoCamp.
  let menos = false;
  try { menos = localStorage.getItem("cc_menos_mov") === "1"; } catch { /* nada */ }
  if (!clave || menos) return;
  quitarDedo = seguirDedo(window, clave);
}

function activarEfecto(clave) {
  quitarEfecto?.();
  quitarEfecto = null;
  if (!clave || reducido()) return;
  if (clave === "efecto_estela") {
    let ultimo = 0;
    const mover = (e) => { const t = performance.now(); if (t - ultimo < 35) return; ultimo = t; particula(e.clientX, e.clientY, { color: ["#facc15", "#a855f7", "#22d3ee"][(t / 35 | 0) % 3], tam: 9, dx: (Math.random() - .5) * 20, dy: 14 + Math.random() * 16, dur: 700, forma: "estrella" }); };
    addEventListener("pointermove", mover, { passive: true });
    quitarEfecto = () => removeEventListener("pointermove", mover);
    return;
  }
  const fn = EFECTOS[clave];
  if (!fn) return;
  const clic = (e) => { if (e.button === 0) fn(e.clientX, e.clientY); };
  addEventListener("pointerdown", clic, { passive: true });
  quitarEfecto = () => removeEventListener("pointerdown", clic);
}

/** HTML de una foto o avatar con su marco: <span class="cc-marco" data-marco="…">contenido</span> */
export const conMarco = (contenido, marco) => (marco && MARCOS[marco] ? `<span class="cc-marco" data-marco="${marco}">${contenido}</span>` : contenido);

/** Aplica en la página lo que la persona tiene puesto. opciones.fondo=false para no tocar el fondo (p. ej. en Trabajo). */
export function aplicarCosmeticos(eq = {}, { fondo = true } = {}) {
  estilo("cc-cosmeticos-base", CSS_BASE);
  const html = document.documentElement;
  try { localStorage.setItem("cc_cosm", JSON.stringify(eq)); } catch { /* sin almacenamiento */ }
  // Tema de color
  const t = TEMAS[eq.tema];
  estilo("cc-cosm-tema", t ? `:root,:root body,:root[data-tema] body{--acc:${t.acc}!important;--acc2:${t.acc2}!important;--cy:${t.cy}!important}` : "");
  // Puntero
  const j = juegoCursor(eq.cursor);
  const c = (v, respaldo) => `url("${v.url}") ${v.x} ${v.y},${respaldo}!important`;
  estilo("cc-cosm-cursor", j ? `html,body{cursor:${c(j.normal, "auto")}}
a,a *,button,button *,[role=button],[role=tab],[role=menuitem],label,select,summary,.bj,.nav-i,.inf-i,[onclick],[data-t],input[type=checkbox],input[type=radio],input[type=submit],input[type=button]{cursor:${c(j.mano, "pointer")}}
input:not([type=checkbox]):not([type=radio]):not([type=submit]):not([type=button]):not([type=range]):not([type=color]),textarea,[contenteditable=true],[contenteditable=""],.monaco-editor .view-lines,.monaco-editor .view-line,.ed-ta,.xterm{cursor:${c(j.texto, "text")}}` : "");
  // Fondo
  pararCanvas?.();
  document.getElementById("cc-fondo")?.remove();
  html.classList.remove("cc-con-fondo", "cc-fondo-oscuro");
  const f = fondo && FONDOS[eq.fondo];
  if (f) {
    const caja = document.createElement("div");
    caja.id = "cc-fondo";
    caja.setAttribute("aria-hidden", "true");
    caja.style.cssText = f.css;
    document.body.prepend(caja);
    html.classList.add("cc-con-fondo");
    if (f.oscuro) html.classList.add("cc-fondo-oscuro");
    veloFondo();
    if (f.canvas) animarCanvas(f.canvas, caja);
    if (reducido()) caja.style.animation = "none";
  }
  // Efecto (clic) y estela del dedo (celular)
  activarEfecto(eq.efecto);
  activarDedo(eq.dedo);
}

/* Con un fondo comprado los paneles se vuelven translúcidos (se ve el fondo) pero conservan
   suficiente color para leer bien. Menús, diálogos, editor y terminal siguen opacos. */
const ALFA = { panel: 56, panel2: 62, surf: 56, surf2: 56, surf3: 56, "lado-bg": 50, bg: 30, "chip-bg": 66, "campo-bg": 80,
  "unidad-bg": 52, "sec-bg": 64, "inf-bg": 60, "pie-bg": 66, "guia-bg": 64, "pieza-bg": 70, "nodo-bg": 74, "caja-bg": 58,
  "mix-a": 58, "mix-b": 58, "mes-b-bg": 64, "lab-top": 70, "onb-form-bg": 74 };
const PRIMER_COLOR = /#[0-9a-f]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|color\([^)]*\)/i;
let observadorTema = null;
function luminancia(color) {
  const c = document.createElement("canvas").getContext("2d");
  if (!c) return 0;
  c.fillStyle = "#000"; c.fillStyle = color; c.fillRect(0, 0, 1, 1);
  const [r, g, b] = c.getImageData(0, 0, 1, 1).data;
  return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
}
function veloFondo() {
  const html = document.documentElement;
  estilo("cc-cosm-velo", "");
  if (!html.classList.contains("cc-con-fondo")) return;
  const cs = getComputedStyle(document.body);
  const v = (n) => cs.getPropertyValue("--" + n).trim();
  const base = v("panel") || "#0d1b1a";
  const solido = { panel: base, panel2: v("panel2") || base, surf: v("surf") || base, bg: v("bg") || base };
  const reglas = [];
  for (const [n, a] of Object.entries(ALFA)) {
    let val = v(n);
    if (!val) continue;
    if (/gradient\(/.test(val)) val = (val.replace(/radial-gradient\([^()]*(\([^()]*\)[^()]*)*\),?/g, "").match(PRIMER_COLOR) || [base])[0];
    reglas.push(`--${n}:color-mix(in srgb,${val} ${a}%,transparent)!important`);
  }
  for (const [n, val] of Object.entries(solido)) reglas.push(`--cc-${n}-solido:${val}`);
  reglas.push("--body-img:none!important");
  // Tema claro + fondo oscuro (o al revés): el texto que va directo sobre el fondo no se leería → velo más fuerte.
  const temaOscuro = luminancia(solido.bg) < 0.4;
  const fondoOscuro = html.classList.contains("cc-fondo-oscuro");
  reglas.push(`--cc-velo:color-mix(in srgb,${solido.bg} ${temaOscuro === fondoOscuro ? 10 : 42}%,transparent)`);
  estilo("cc-cosm-velo", `html.cc-con-fondo body,html.cc-con-fondo .trabajo-app{${reglas.join(";")}}`);
  if (!observadorTema) {
    observadorTema = new MutationObserver(() => veloFondo());
    observadorTema.observe(html, { attributes: true, attributeFilter: ["data-tema"] });
    matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", () => veloFondo());
  }
}

/** Lo último que se aplicó (para pintarlo al instante mientras carga la página). */
export function cosmeticosGuardados() { try { return JSON.parse(localStorage.getItem("cc_cosm") || "{}"); } catch { return {}; } }

/** Vista previa de un cosmético dentro de un elemento (tarjetas de la tienda). */
export function vistaPrevia(el, clave, tipo) {
  if (tipo === "fondo" && FONDOS[clave]) {
    el.style.cssText += `;${FONDOS[clave].css}`;
    if (FONDOS[clave].canvas === "matrix") el.style.backgroundImage = `repeating-linear-gradient(90deg,transparent 0 10px,rgba(34,197,94,.0) 10px 12px),linear-gradient(rgba(34,197,94,.0),rgba(34,197,94,.0))`;
    if (FONDOS[clave].canvas) el.classList.add(`cc-prev-${FONDOS[clave].canvas}`);
  } else if (tipo === "cursor" && CURSORES[clave]) {
    // Los 3 del juego: pasa el mouse por cada uno para probarlo
    const j = juegoCursor(clave);
    el.classList.add("cc-prev-cursores");
    el.innerHTML = [["normal", "Normal"], ["mano", "Enlaces"], ["texto", "Texto"]].map(([k, t]) => `<span class="cc-prev-cur" data-k="${k}" style="cursor:url('${j[k].url}') ${j[k].x} ${j[k].y},auto"><img src="${j[k].url}" alt="" width="40" height="40"><small>${t}</small></span>`).join("");
  } else if (tipo === "tema" && TEMAS[clave]) {
    const t = TEMAS[clave];
    el.innerHTML = `<span style="background:${t.acc}"></span><span style="background:${t.acc2}"></span><span style="background:${t.cy}"></span>`;
    el.classList.add("cc-prev-tema");
  } else if (tipo === "marco" && MARCOS[clave]) {
    estilo("cc-cosmeticos-base", CSS_BASE);
    el.innerHTML = `<span class="cc-marco" data-marco="${clave}"><span class="cc-prev-cara cc-prev-inicial">A</span></span>`;
  } else if (tipo === "dedo" && DEDOS[clave]) {
    el.innerHTML = `<span class="cc-prev-efecto">${matchMedia("(pointer: coarse)").matches ? "Toca y desliza el dedo aquí" : "Mueve el mouse aquí"}</span>`;
    el.style.touchAction = "none";   // dentro de la tarjeta, deslizar dibuja (no mueve la página)
    el.__quitarDedo?.();
    el.__quitarDedo = seguirDedo(el, clave);
  } else if (tipo === "efecto") {
    el.innerHTML = '<span class="cc-prev-efecto">Haz clic aquí</span>';
    el.onpointerdown = (e) => { const fn = EFECTOS[clave]; if (fn) fn(e.clientX, e.clientY); else for (let i = 0; i < 6; i++) particula(e.clientX, e.clientY, { color: "#facc15", tam: 9, dx: (Math.random() - .5) * 40, dy: 20 + Math.random() * 20, dur: 700, forma: "estrella" }); };
  }
}
