// Ilustraciones propias de los artículos de la tienda que no se ven solos en una tarjeta: efectos al hacer clic,
// rastros del mouse o del dedo, potenciadores y temas. Cada artículo tiene su escena (SVG dibujado aquí, sin imágenes
// externas). En las tarjetas de efectos y rastros la escena va de fondo y la vista previa sigue siendo interactiva.

let n = 0;
const W = 220, H = 96;
const azar = (s) => { let x = 0; for (const c of s) x = (x * 31 + c.charCodeAt(0)) >>> 0; return () => ((x = (x * 1103515245 + 12345) >>> 0) / 4294967296); };

// --------------------------------------------------------------------------------------- piezas ----
const P = {
  estrella: (x, y, r, c, o = 1) => `<path d="M${x} ${y - r}l${r * .29} ${r * .6} ${r * .66} .1-${r * .48} ${r * .46} .12 ${r * .66}-${r * .59}-${r * .31}-${r * .59} ${r * .31} .12-${r * .66}-${r * .48}-${r * .46} ${r * .66}-.1z" fill="${c}" opacity="${o}"/>`,
  brillo: (x, y, r, c) => `<path d="M${x} ${y - r}Q${x} ${y} ${x + r} ${y}Q${x} ${y} ${x} ${y + r}Q${x} ${y} ${x - r} ${y}Q${x} ${y} ${x} ${y - r}z" fill="${c}"/>`,
  corazon: (x, y, s, c) => `<path transform="translate(${x} ${y}) scale(${s})" d="M0 3C-1-1-6-1-6 3c0 3 6 7 6 7s6-4 6-7c0-4-5-4-6 0z" fill="${c}"/>`,
  burbuja: (x, y, r) => `<circle cx="${x}" cy="${y}" r="${r}" fill="rgba(186,230,253,.35)" stroke="#7dd3fc" stroke-width="1.3"/><circle cx="${x - r * .35}" cy="${y - r * .35}" r="${r * .22}" fill="#fff" opacity=".85"/>`,
  moneda: (x, y, r) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#facc15" stroke="#a16207" stroke-width="1.4"/><circle cx="${x}" cy="${y}" r="${r * .62}" fill="none" stroke="#fde68a" stroke-width="1.2"/><text x="${x}" y="${y + r * .38}" font-size="${r * 1.05}" font-weight="900" text-anchor="middle" fill="#a16207" font-family="system-ui">$</text>`,
  copo: (x, y, r, c = "#e0f2fe") => `<g stroke="${c}" stroke-width="1.6" stroke-linecap="round">${[0, 60, 120].map((a) => `<path transform="rotate(${a} ${x} ${y})" d="M${x} ${y - r}V${y + r}M${x - r * .3} ${y - r * .7}L${x} ${y - r * .45}L${x + r * .3} ${y - r * .7}"/>`).join("")}</g>`,
  hoja: (x, y, s, c, a = 0) => `<g transform="translate(${x} ${y}) rotate(${a}) scale(${s})"><path d="M0-6C5-6 7 0 0 7-7 0-5-6 0-6z" fill="${c}"/><path d="M0-5V7" stroke="rgba(0,0,0,.3)" stroke-width=".8"/></g>`,
  petalo: (x, y, s, a) => `<path transform="translate(${x} ${y}) rotate(${a}) scale(${s})" d="M0-5C3-5 4 0 0 5-4 0-3-5 0-5zM-1-5l1 2 1-2" fill="#fbcfe8" stroke="#f472b6" stroke-width=".6"/>`,
  nota: (x, y, s, c) => `<g transform="translate(${x} ${y}) scale(${s})" fill="${c}"><ellipse cx="0" cy="8" rx="3.2" ry="2.4" transform="rotate(-20 0 8)"/><path d="M2.6 7V-6l7 2v4l-5-1.5V7" /></g>`,
  globo: (x, y, s, c) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0 9q-3 6 1 11" stroke="#94a3b8" fill="none" stroke-width=".9"/><ellipse cx="0" cy="0" rx="7" ry="8.6" fill="${c}"/><path d="M-2 8.4h4L0 10z" fill="${c}"/><ellipse cx="-2.4" cy="-3.4" rx="1.6" ry="2.6" fill="#fff" opacity=".55"/></g>`,
  gota: (x, y, s, c) => `<path transform="translate(${x} ${y}) scale(${s})" d="M0-7C3-2 5 1 5 3.5A5 5 0 0 1-5 3.5C-5 1-3-2 0-7z" fill="${c}"/>`,
  llama: (x, y, s) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0-12C4-6 8-3 6 3 5 7 2 9 0 9-2 9-5 7-6 3-7-1-3-3-3-7-1-5 0-6 0-12z" fill="#f97316"/><path d="M0-4C2-1 4 1 3 4 2 6 1 7 0 7-1 7-3 6-3 4-3 1-1 0 0-4z" fill="#fde047"/></g>`,
  rayo: (x, y, s, c = "#fde047") => `<path transform="translate(${x} ${y}) scale(${s})" d="M3-14-7 2h6L-3 14 8-3H2z" fill="${c}" stroke="#a16207" stroke-width="1" stroke-linejoin="round"/>`,
  cuadro: (x, y, l, c) => `<rect x="${x - l / 2}" y="${y - l / 2}" width="${l}" height="${l}" fill="${c}"/>`,
  orbe: (x, y, r) => `<circle cx="${x}" cy="${y}" r="${r * 1.7}" fill="#4ade80" opacity=".22"/><circle cx="${x}" cy="${y}" r="${r}" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/><text x="${x}" y="${y + r * .36}" font-size="${r * .95}" font-weight="900" text-anchor="middle" fill="#f0fdf4" font-family="system-ui">XP</text>`,
  texto: (x, y, t, s, c, extra = "") => `<text x="${x}" y="${y}" font-size="${s}" font-weight="900" text-anchor="middle" fill="${c}" font-family="ui-monospace,Consolas,monospace" ${extra}>${t}</text>`,
  clic: (x, y) => `<g transform="translate(${x} ${y})"><circle r="15" fill="none" stroke="#fff" stroke-width="1.5" opacity=".55"/><circle r="9" fill="none" stroke="#fff" stroke-width="1.5" opacity=".8"/><path d="M-2-2 10 4 4.5 5.5 2 11z" fill="#fff" stroke="#0f172a" stroke-width="1.3" stroke-linejoin="round"/></g>`,
  dedo: (x, y) => `<g transform="translate(${x} ${y})"><path d="M0 0v-12a2.4 2.4 0 0 1 4.8 0v8l5.6 1.4a3 3 0 0 1 2.2 3.4L11.4 9H1.2L-4 2.5a2 2 0 0 1 3-2.6z" fill="#fde7d4" stroke="#0f172a" stroke-width="1.3" stroke-linejoin="round"/></g>`,
};
const fondo = (id, a, b) => `<defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient></defs><rect width="${W}" height="${H}" fill="url(#${id})"/>`;
/** Partículas alrededor del punto del clic */
function rafaga(clave, pieza, cant = 12, radio = [16, 44]) {
  const r = azar(clave);
  let s = "";
  for (let i = 0; i < cant; i++) {
    const a = (i / cant) * Math.PI * 2 + r() * .5;
    const d = radio[0] + r() * (radio[1] - radio[0]);
    s += pieza(110 + Math.cos(a) * d * 1.6, 48 + Math.sin(a) * d * .9, r, i);
  }
  return s;
}
/** Camino del rastro: de izquierda a derecha con una curva, termina donde está el mouse/dedo */
const CAMINO = "M8 70C40 30 70 78 104 50S160 22 182 40";
function aLoLargo(clave, pieza, cant = 14) {
  const r = azar(clave);
  let s = "";
  for (let i = 0; i < cant; i++) {
    const t = i / (cant - 1);
    // puntos aproximados de la curva (Bezier cúbica a trozos)
    const x = 8 + t * 174;
    const y = t < .55 ? 70 - Math.sin(t / .55 * Math.PI) * 18 + (t / .55) * -20 : 50 - Math.sin((t - .55) / .45 * Math.PI) * 18 - ((t - .55) / .45) * -10 + (r() - .5) * 4;
    s += pieza(x + (r() - .5) * 8, y + (r() - .5) * 12, t, r, i);
  }
  return s;
}
const ARCOIRIS = ["#ef4444", "#f97316", "#facc15", "#22c55e", "#3b82f6", "#a855f7"];

// ----------------------------------------------------------------------- efectos al hacer clic ----
const EFECTO = {
  efecto_burbujas: ["#0c4a6e", "#0369a1", (k) => rafaga(k, (x, y, r) => P.burbuja(x, y, 3 + r() * 6), 14)],
  efecto_confeti: ["#312e81", "#6d28d9", (k) => rafaga(k, (x, y, r, i) => `<rect x="${x}" y="${y}" width="5" height="8" rx="1" transform="rotate(${r() * 180} ${x} ${y})" fill="${ARCOIRIS[i % 6]}"/>`, 22)],
  efecto_corazones: ["#831843", "#db2777", (k) => rafaga(k, (x, y, r) => P.corazon(x, y, .6 + r() * .7, r() > .5 ? "#fda4af" : "#fff1f2"), 11)],
  efecto_monedas: ["#422006", "#a16207", (k) => rafaga(k, (x, y, r) => P.moneda(x, y, 5 + r() * 4), 10)],
  efecto_rayos: ["#0f172a", "#1e3a8a", (k) => rafaga(k, (x, y, r) => `<path d="M110 48L${(110 + x) / 2 + (r() - .5) * 14} ${(48 + y) / 2 + (r() - .5) * 10}L${x} ${y}" stroke="#67e8f9" stroke-width="1.8" fill="none"/>${P.brillo(x, y, 3, "#e0f2fe")}`, 9)],
  efecto_fuegos: ["#020617", "#1e1b4b", (k) => [[60, 32, "#f472b6"], [110, 26, "#facc15"], [160, 38, "#38bdf8"]].map(([cx, cy, c]) => Array.from({ length: 12 }, (_, i) => { const a = i / 12 * Math.PI * 2; return `<path d="M${cx + Math.cos(a) * 5} ${cy + Math.sin(a) * 5}L${cx + Math.cos(a) * 17} ${cy + Math.sin(a) * 17}" stroke="${c}" stroke-width="2" stroke-linecap="round"/>`; }).join("") + `<circle cx="${cx}" cy="${cy}" r="3" fill="#fff"/><path d="M${cx} ${cy + 20}V${H}" stroke="${c}" stroke-width="1" stroke-dasharray="2 3" opacity=".6"/>`).join("")],
  efecto_rayo: ["#111827", "#312e81", () => `<circle cx="110" cy="48" r="38" fill="#fde047" opacity=".12"/><circle cx="110" cy="48" r="24" fill="none" stroke="#fde047" stroke-width="2" opacity=".5"/>${P.rayo(110, 40, 1.9)}`],
  efecto_powerup: ["#1e1b4b", "#7c3aed", (k) => ARCOIRIS.map((c, i) => `<circle cx="110" cy="48" r="${10 + i * 6}" fill="none" stroke="${c}" stroke-width="2" opacity="${1 - i * .12}"/>`).join("") + rafaga(k, (x, y, r, i) => P.estrella(x, y, 4 + r() * 3, ARCOIRIS[i % 6]), 10, [34, 48]) + P.texto(110, 90, "POWER UP!", 9, "#fde047")],
  efecto_xp: ["#052e16", "#15803d", (k) => rafaga(k, (x, y, r) => P.orbe(x, y, 5 + r() * 3), 9)],
  efecto_critico: ["#450a0a", "#b91c1c", (k) => rafaga(k, (x, y) => P.brillo(x, y, 4, "#fde047"), 10) + P.texto(110, 56, "¡CRÍTICO!", 22, "#fef08a", 'stroke="#7f1d1d" stroke-width="1.2" transform="rotate(-6 110 48)"')],
  efecto_teletransporte: ["#083344", "#0e7490", (k) => `<ellipse cx="110" cy="64" rx="34" ry="9" fill="none" stroke="#67e8f9" stroke-width="2.4"/><ellipse cx="110" cy="64" rx="22" ry="5" fill="#22d3ee" opacity=".35"/>` + rafaga(k, (x, y, r) => P.cuadro(x, y - 8, 3 + r() * 4, r() > .5 ? "#67e8f9" : "#cffafe"), 18, [8, 40])],
  efecto_bloques: ["#292524", "#57534e", (k) => rafaga(k, (x, y, r) => `<rect x="${x}" y="${y}" width="${5 + r() * 6}" height="${5 + r() * 6}" fill="${r() > .5 ? "#a8a29e" : "#78716c"}" stroke="#1c1917" stroke-width="1"/>`, 14) + `<rect x="98" y="38" width="24" height="20" fill="#78716c" stroke="#1c1917" stroke-width="1.5"/><path d="M98 48h24M110 38v10M104 48v10M116 48v10" stroke="#44403c"/>`],
  efecto_combo: ["#1e1b4b", "#be185d", (k) => P.texto(70, 40, "+100", 16, "#fde047") + P.texto(150, 36, "COMBO!", 15, "#f0abfc") + P.texto(112, 72, "x2", 22, "#67e8f9") + P.texto(60, 78, "1UP", 11, "#4ade80") + rafaga(k, (x, y, r) => P.estrella(x, y, 3 + r() * 2, "#fde047"), 7, [40, 52])],
  efecto_estrellas: ["#1e1b4b", "#4338ca", (k) => rafaga(k, (x, y, r) => P.estrella(x, y, 3 + r() * 5, r() > .4 ? "#fde047" : "#fff7ed"), 13)],
  efecto_nieve: ["#0c4a6e", "#38bdf8", (k) => rafaga(k, (x, y, r) => P.copo(x, y, 3 + r() * 4), 12)],
  efecto_codigo: ["#0f172a", "#1e293b", (k) => rafaga(k, (x, y, r, i) => P.texto(x, y, ["{", "}", ";", "0", "1", "&lt;/&gt;", "()", "=&gt;"][i % 8], 9 + r() * 6, ["#4ade80", "#38bdf8", "#f472b6", "#facc15"][i % 4]), 14)],
  efecto_ondas: ["#082f49", "#0284c7", () => [8, 18, 28, 40].map((r, i) => `<ellipse cx="110" cy="52" rx="${r * 1.8}" ry="${r * .6}" fill="none" stroke="#bae6fd" stroke-width="${2.2 - i * .4}" opacity="${1 - i * .2}"/>`).join("") + P.gota(110, 30, 1.4, "#7dd3fc")],
  efecto_emojis: ["#4c1d95", "#db2777", (k) => rafaga(k, (x, y, r, i) => `<text x="${x}" y="${y}" font-size="${11 + r() * 6}" text-anchor="middle">${["🎉", "✨", "🔥", "🚀", "💡", "⭐"][i % 6]}</text>`, 10)],
  efecto_pixeles: ["#111827", "#1f2937", (k) => rafaga(k, (x, y, r, i) => P.cuadro(x, y, 4 + r() * 5, ARCOIRIS[i % 6]), 22, [6, 44])],
  efecto_supernova: ["#020617", "#312e81", (k) => `<circle cx="110" cy="48" r="30" fill="none" stroke="#fde68a" stroke-width="3" opacity=".8"/><circle cx="110" cy="48" r="18" fill="#fef3c7" opacity=".25"/><circle cx="110" cy="48" r="7" fill="#fff"/>` + rafaga(k, (x, y, r) => P.brillo(x, y, 2 + r() * 3, "#fff"), 14, [40, 54])],
  efecto_chispas: ["#1c1917", "#78350f", (k) => rafaga(k, (x, y) => `<path d="M110 48L${x} ${y}" stroke="#fbbf24" stroke-width="1.4" stroke-linecap="round" opacity=".8"/>${P.brillo(x, y, 2.5, "#fef3c7")}`, 16)],
  efecto_estela: ["#1e1b4b", "#3730a3", (k) => aLoLargo(k, (x, y, t, r) => P.estrella(x, y, 2 + t * 4, t > .5 ? "#fde047" : "#c4b5fd", .4 + t * .6), 12)],
  efecto_globos: ["#e0f2fe", "#fce7f3", (k) => rafaga(k, (x, y, r, i) => P.globo(x, y - 6, .7 + r() * .5, ARCOIRIS[i % 6]), 8, [20, 46])],
  efecto_notas: ["#2e1065", "#6d28d9", (k) => rafaga(k, (x, y, r, i) => P.nota(x, y, .8 + r() * .5, ["#f0abfc", "#fde047", "#67e8f9"][i % 3]), 10)],
  efecto_hojas: ["#431407", "#9a3412", (k) => rafaga(k, (x, y, r, i) => P.hoja(x, y, .8 + r() * .6, ["#f97316", "#facc15", "#dc2626", "#a16207"][i % 4], r() * 360), 12)],
  efecto_tinta: ["#f8fafc", "#e2e8f0", (k) => `<path d="M110 32c10 0 18 8 16 16 8 2 6 14-2 14-2 8-12 10-16 4-8 4-16-4-12-10-8-4-4-16 4-14 0-6 4-10 10-10z" fill="#3b82f6"/>` + rafaga(k, (x, y, r, i) => P.gota(x, y, .5 + r() * .5, ["#3b82f6", "#ec4899", "#22c55e", "#f59e0b"][i % 4]), 12, [30, 50])],
  efecto_portal: ["#1e1b4b", "#4c1d95", () => [32, 24, 16, 8].map((r, i) => `<ellipse cx="110" cy="48" rx="${r}" ry="${r * .95}" fill="none" stroke="${["#c084fc", "#a855f7", "#e9d5ff", "#7c3aed"][i]}" stroke-width="3" stroke-dasharray="${r * 1.4} ${r * .6}" transform="rotate(${i * 40} 110 48)"/>`).join("") + '<circle cx="110" cy="48" r="5" fill="#f5f3ff"/>'],
  efecto_meteoro: ["#020617", "#1e293b", (k) => { const r = azar(k); return Array.from({ length: 5 }, (_, i) => { const x = 40 + i * 38 + r() * 10, y = 14 + r() * 40; return `<path d="M${x - 34} ${y - 20}L${x} ${y}" stroke="url(#mt${n})" stroke-width="3" stroke-linecap="round"/><circle cx="${x}" cy="${y}" r="3.4" fill="#fed7aa"/>`; }).join("") + `<defs><linearGradient id="mt${n}"><stop offset="0" stop-color="#f97316" stop-opacity="0"/><stop offset="1" stop-color="#fdba74"/></linearGradient></defs>`; }],
};

// --------------------------------------------------------------------------- rastros del mouse ----
const linea = (c, w, extra = "") => `<path d="${CAMINO}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" ${extra}/>`;
const DEDO = {
  dedo_cola_cometa: ["#0f172a", "#1e3a8a", (k) => linea("#bfdbfe", 7, 'opacity=".25"') + linea("#e0f2fe", 3) + aLoLargo(k, (x, y) => P.brillo(x, y, 2, "#fff"), 8)],
  dedo_estela_arcoiris: ["#1e1b4b", "#312e81", () => ARCOIRIS.map((c, i) => `<path d="${CAMINO}" transform="translate(0 ${(i - 2.5) * 3})" fill="none" stroke="${c}" stroke-width="3" stroke-linecap="square"/>`).join("")],
  dedo_turbo: ["#1c1917", "#44403c", (k) => aLoLargo(k, (x, y, t, r) => P.cuadro(x, y, 3 + t * 6, t > .7 ? "#fde047" : t > .4 ? "#f97316" : "#78716c"), 18)],
  dedo_orbes: ["#052e16", "#14532d", (k) => aLoLargo(k, (x, y, t) => P.orbe(x, y, 2 + t * 4), 8)],
  dedo_tinta: ["#f1f5f9", "#e2e8f0", (k) => linea("#2563eb", 4, 'opacity=".75"') + aLoLargo(k, (x, y, t) => P.gota(x, y + 8, .4 + t * .4, "#1d4ed8"), 7)],
  dedo_burbujas: ["#0c4a6e", "#0369a1", (k) => aLoLargo(k, (x, y, t, r) => P.burbuja(x, y - t * 8, 2 + r() * 5), 11)],
  dedo_neon: ["#020617", "#0f172a", () => linea("#22d3ee", 9, 'opacity=".2"') + linea("#22d3ee", 4, 'opacity=".5"') + linea("#ecfeff", 1.6)],
  dedo_codigo: ["#0f172a", "#1e293b", (k) => aLoLargo(k, (x, y, t, r, i) => P.texto(x, y, ["{", "}", ";", "1", "0", "&lt;/&gt;"][i % 6], 8 + t * 6, ["#4ade80", "#38bdf8", "#f472b6"][i % 3]), 14)],
  dedo_arcoiris: ["#ecfeff", "#fdf4ff", () => `<defs><linearGradient id="ac${n}">${ARCOIRIS.map((c, i) => `<stop offset="${i / 5}" stop-color="${c}"/>`).join("")}</linearGradient></defs>` + linea(`url(#ac${n})`, 8)],
  dedo_fuego: ["#1c0a05", "#431407", (k) => aLoLargo(k, (x, y, t) => P.llama(x, y, .3 + t * .7), 9)],
  dedo_galaxia: ["#020617", "#3b0764", (k) => linea("#a855f7", 10, 'opacity=".25"') + aLoLargo(k, (x, y, t, r) => (r() > .5 ? P.estrella(x, y, 1.5 + r() * 3, "#fde68a") : `<circle cx="${x}" cy="${y}" r="${1 + r() * 2}" fill="${r() > .5 ? "#c4b5fd" : "#f0abfc"}"/>`), 24)],
  dedo_estrellas: ["#1e1b4b", "#312e81", (k) => aLoLargo(k, (x, y, t) => P.estrella(x, y, 2 + t * 4, "#fde047"), 10)],
  dedo_nieve: ["#0c4a6e", "#0284c7", (k) => aLoLargo(k, (x, y, t) => P.copo(x, y, 2 + t * 4), 9)],
  dedo_corazones: ["#4c0519", "#9f1239", (k) => aLoLargo(k, (x, y, t) => P.corazon(x, y - 3, .35 + t * .5, "#fda4af"), 9)],
  dedo_pixeles: ["#111827", "#1f2937", (k) => aLoLargo(k, (x, y, t, r, i) => P.cuadro(x, y, 3 + t * 5, ARCOIRIS[i % 6]), 18)],
  dedo_rayo: ["#0f172a", "#172554", () => `<path d="M8 70 30 52 44 64 66 40 82 56 104 34 120 50 142 28 160 44 182 30" fill="none" stroke="#fde047" stroke-width="5" opacity=".25" stroke-linejoin="round"/><path d="M8 70 30 52 44 64 66 40 82 56 104 34 120 50 142 28 160 44 182 30" fill="none" stroke="#fef9c3" stroke-width="2" stroke-linejoin="round"/>`],
  dedo_sakura: ["#fdf2f8", "#fce7f3", (k) => aLoLargo(k, (x, y, t, r) => P.petalo(x, y, .7 + t * .6, r() * 360), 12)],
  dedo_cometa: ["#020617", "#172554", (k) => linea("#93c5fd", 4, 'opacity=".5" stroke-dasharray="2 5"') + aLoLargo(k, (x, y, t) => P.estrella(x, y, 1.5 + t * 3, "#e0f2fe"), 7) + '<circle cx="182" cy="40" r="7" fill="#e0f2fe"/><circle cx="182" cy="40" r="12" fill="#93c5fd" opacity=".3"/>'],
  dedo_hojas: ["#fff7ed", "#ffedd5", (k) => aLoLargo(k, (x, y, t, r, i) => P.hoja(x, y, .6 + t * .5, ["#f97316", "#dc2626", "#ca8a04"][i % 3], r() * 360), 10)],
  dedo_notas: ["#2e1065", "#581c87", (k) => aLoLargo(k, (x, y, t, r, i) => P.nota(x, y - 6, .5 + t * .5, ["#f0abfc", "#fde047"][i % 2]), 8)],
  dedo_confeti: ["#1e1b4b", "#4c1d95", (k) => aLoLargo(k, (x, y, t, r, i) => `<rect x="${x}" y="${y}" width="4" height="7" rx="1" transform="rotate(${r() * 180} ${x} ${y})" fill="${ARCOIRIS[i % 6]}"/>`, 18)],
  dedo_luciernagas: ["#022c22", "#064e3b", (k) => aLoLargo(k, (x, y, t, r) => `<circle cx="${x}" cy="${y - 8 + r() * 16}" r="${5 + r() * 3}" fill="#fde047" opacity=".18"/><circle cx="${x}" cy="${y - 8 + r() * 16}" r="1.8" fill="#fef9c3"/>`, 11)],
  dedo_humo: ["#f8fafc", "#e2e8f0", (k) => aLoLargo(k, (x, y, t, r, i) => `<circle cx="${x}" cy="${y}" r="${5 + t * 9}" fill="${["#c4b5fd", "#f9a8d4", "#93c5fd", "#86efac"][i % 4]}" opacity="${.25 + t * .35}"/>`, 10)],
  dedo_dragon: ["#1c0a05", "#7c2d12", (k) => linea("#f59e0b", 8, 'opacity=".3"') + aLoLargo(k, (x, y, t, r) => (r() > .5 ? P.llama(x, y, .25 + t * .4) : `<path transform="translate(${x} ${y}) rotate(${r() * 90})" d="M0-4 4 0 0 4-4 0z" fill="#fbbf24" stroke="#78350f" stroke-width=".6"/>`), 14)],
  dedo_mito: ["#1e1b4b", "#581c87", (k) => linea("#facc15", 6, 'opacity=".2"') + aLoLargo(k, (x, y, t, r, i) => P.texto(x, y, ["ᚠ", "ᚱ", "✦", "ᛟ", "ᚨ"][i % 5], 9 + t * 7, i % 2 ? "#fde68a" : "#e9d5ff"), 9)],
};

// ------------------------------------------- potenciadores (los cofres conservan su diseño de cofre) ----
const POTENCIADOR = {
  impulso_xp: () => fondo(`f${n}`, "#1e1b4b", "#4338ca") + `<circle cx="110" cy="48" r="34" fill="#facc15" opacity=".15"/><circle cx="110" cy="48" r="24" fill="#fde047" stroke="#a16207" stroke-width="2"/>${P.rayo(110, 47, 1.25, "#fff7cc")}` + P.orbe(48, 34, 9) + P.orbe(172, 58, 11) + P.orbe(66, 72, 6) + P.texto(172, 26, "+60 XP", 12, "#bef264"),
  // Los básicos también tienen su escena (antes salía un cuadro genérico en vida, vidas llenas, salvarrachas y kit)
  vida: () => fondo(`f${n}`, "#4c0519", "#e11d48") + `<circle cx="110" cy="48" r="30" fill="#fff" opacity=".12"/>` + P.corazon(110, 46, 1.9, "#fff1f2") + P.corazon(110, 46, 1.45, "#f43f5e")
    + P.brillo(150, 26, 6, "#fff") + P.brillo(68, 70, 5, "#fecdd3") + P.texto(168, 78, "+1", 15, "#fff1f2"),
  vidas_llenas: () => fondo(`f${n}`, "#831843", "#f472b6") + [0, 1, 2, 3, 4].map((i) => P.corazon(46 + i * 32, 48 + (i % 2 ? 6 : -6), 1.05, ["#fff1f2", "#fecdd3", "#fda4af", "#fecdd3", "#fff1f2"][i])).join("")
    + `<rect x="40" y="74" width="140" height="8" rx="4" fill="#fff" opacity=".25"/><rect x="40" y="74" width="140" height="8" rx="4" fill="#fff" opacity=".85"/>` + P.texto(110, 20, "¡LLENAS!", 12, "#fff"),
  salvarracha: () => fondo(`f${n}`, "#0c4a6e", "#38bdf8") + `<path d="M110 12 82 22v22c0 18 12 32 28 38 16-6 28-20 28-38V22z" fill="#e0f2fe" stroke="#0369a1" stroke-width="3"/>`
    + `<path d="M110 30c6 8 10 13 10 20a10 10 0 0 1-20 0c0-4 2-7 4-9 0 4 2 6 4 6-1-6 0-11 2-17z" fill="#f97316"/><path d="M110 44c3 4 4 6 4 8a4 4 0 0 1-8 0c0-2 2-5 4-8z" fill="#fde047"/>`
    + P.copo(50, 34, 9, "#e0f2fe") + P.copo(172, 62, 11, "#bae6fd") + P.copo(160, 24, 7, "#fff") + P.texto(52, 80, "racha ok", 11, "#e0f2fe"),
  kit_experto: () => fondo(`f${n}`, "#14532d", "#22c55e") + `<rect x="76" y="30" width="68" height="48" rx="8" fill="#f0fdf4" stroke="#166534" stroke-width="2.5"/><rect x="98" y="22" width="24" height="10" rx="3" fill="none" stroke="#166534" stroke-width="2.5"/>`
    + `<rect x="104" y="42" width="12" height="26" rx="2" fill="#16a34a"/><rect x="97" y="49" width="26" height="12" rx="2" fill="#16a34a"/>`
    + P.estrella(52, 36, 9, "#fde047") + P.estrella(170, 60, 11, "#fef08a") + P.texto(170, 26, "PRO", 12, "#dcfce7"),
  mega_vidas: () => fondo(`f${n}`, "#500724", "#be185d") + `<rect x="88" y="18" width="44" height="66" rx="9" fill="#fdf2f8" stroke="#831843" stroke-width="2.5"/><rect x="102" y="12" width="16" height="8" rx="2" fill="#831843"/>` + [0, 1, 2, 3].map((i) => `<rect x="93" y="${66 - i * 14}" width="34" height="11" rx="3" fill="${["#f43f5e", "#fb7185", "#fda4af", "#fecdd3"][i]}"/>`).join("") + P.corazon(110, 36, 1, "#fff") + P.corazon(52, 40, .9, "#fda4af") + P.corazon(170, 56, 1.1, "#fecdd3") + P.texto(168, 30, "x10", 13, "#fff1f2"),
};

/** Escena de un artículo (o null si ese tipo ya se ve solo, como Codi, fondos, marcos o punteros). */
export function escenaArticulo(clave, tipo, extra = {}) {
  n++;
  let cuerpo = null;
  if (tipo === "efecto" && EFECTO[clave]) { const [a, b, f] = EFECTO[clave]; cuerpo = fondo(`f${n}`, a, b) + f(clave) + P.clic(110, 48); }
  else if (tipo === "dedo" && DEDO[clave]) { const [a, b, f] = DEDO[clave]; cuerpo = fondo(`f${n}`, a, b) + f(clave) + P.dedo(186, 48); }
  else if (POTENCIADOR[clave]) cuerpo = POTENCIADOR[clave]();
  else if (tipo === "tema" && extra.tema) {
    // Mini ventana de CódigoCamp pintada con el tema: barra, menú, tarjeta y botones
    const { acc, acc2, cy } = extra.tema;
    cuerpo = `<rect width="${W}" height="${H}" fill="#f8fafc"/><rect x="10" y="8" width="200" height="80" rx="8" fill="#fff" stroke="#e2e8f0"/>
      <rect x="10" y="8" width="200" height="14" rx="8" fill="${acc}"/><rect x="10" y="16" width="200" height="6" fill="${acc}"/>
      <circle cx="19" cy="15" r="2.2" fill="#fff" opacity=".8"/><circle cx="26" cy="15" r="2.2" fill="#fff" opacity=".6"/>
      <rect x="16" y="28" width="38" height="54" rx="5" fill="${acc}" opacity=".12"/>${[0, 1, 2, 3].map((i) => `<rect x="21" y="${34 + i * 11}" width="${i ? 24 : 28}" height="5" rx="2.5" fill="${i ? "#94a3b8" : acc}" opacity="${i ? .55 : 1}"/>`).join("")}
      <rect x="62" y="28" width="140" height="30" rx="6" fill="${cy}" opacity=".16"/><rect x="70" y="35" width="70" height="6" rx="3" fill="#334155"/><rect x="70" y="45" width="100" height="5" rx="2.5" fill="#94a3b8"/>
      <rect x="62" y="64" width="54" height="16" rx="8" fill="${acc}"/><rect x="72" y="70" width="34" height="4" rx="2" fill="#fff"/>
      <rect x="122" y="64" width="44" height="16" rx="8" fill="${acc2}"/><rect x="171" y="64" width="31" height="16" rx="8" fill="none" stroke="${cy}" stroke-width="2"/>
      <circle cx="186" cy="40" r="9" fill="${acc2}"/><path d="m182 40 3 3 5-6" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  }
  if (!cuerpo) return null;
  return `<svg class="escena-articulo" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">${cuerpo}</svg>`;
}

export const CLAVES_CON_ESCENA = { efecto: Object.keys(EFECTO), dedo: Object.keys(DEDO), potenciador: Object.keys(POTENCIADOR) };
