// Íconos ilustrados de CódigoCamp: premios, monedas, racha, vidas, potenciadores y artículos de la tienda.
// Son dibujos a todo color (degradados, brillos y contorno) en vez de líneas: se ven como pequeñas imágenes a
// cualquier tamaño y en tema claro u oscuro. iconoSVG() de iconos.js los usa cuando existe un dibujo aquí.
// Cada función recibe un prefijo único para los ids de sus degradados (puede haber muchos en la misma página).

const T = "#1f2937";   // contorno
const lin = (id, a, b, x2 = 0, y2 = 1) => `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
const rad = (id, a, b) => `<radialGradient id="${id}" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></radialGradient>`;
const chispa = (x, y, r, c = "#fff") => `<path d="M${x} ${y - r}l${r * .28} ${r * .72} ${r * .72} ${r * .28}-${r * .72} ${r * .28}-${r * .28} ${r * .72}-${r * .28}-${r * .72}-${r * .72}-${r * .28} ${r * .72}-${r * .28}z" fill="${c}"/>`;

const moneda = (i, a, b, c, simbolo) => `<defs>${rad(`${i}m`, a, b)}</defs>
  <circle cx="32" cy="34" r="25" fill="${c}" stroke="${T}" stroke-width="2.5"/>
  <circle cx="32" cy="31" r="25" fill="url(#${i}m)" stroke="${T}" stroke-width="2.5"/>
  <circle cx="32" cy="31" r="18.5" fill="none" stroke="${c}" stroke-width="2.5" opacity=".8"/>
  ${simbolo}
  <path d="M15 22a19 19 0 0 1 12-9" stroke="#fff" stroke-width="3.5" stroke-linecap="round" fill="none" opacity=".7"/>
  ${chispa(50, 14, 5)}`;

const xp = (i, n, a, b) => `<defs>${lin(`${i}x`, a, b)}</defs>
  <path d="M32 4l7.5 15.5L56 22l-12 11.5L47 50 32 42 17 50l3-16.5L8 22l16.5-2.5z" fill="url(#${i}x)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M32 10l5 10.5" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".6"/>
  <rect x="14" y="40" width="36" height="17" rx="8.5" fill="#111827" stroke="${T}" stroke-width="2"/>
  <text x="32" y="53" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" font-weight="900" fill="#fde047">${n}</text>`;

const escudo = (i, a, b, centro) => `<defs>${lin(`${i}s`, a, b)}</defs>
  <path d="M32 4L10 11v17c0 15 9.5 26.5 22 31 12.5-4.5 22-16 22-31V11z" fill="url(#${i}s)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M32 9L15 14.5V28c0 11.5 7 20.5 17 24.5" fill="none" stroke="#fff" stroke-width="2.5" opacity=".45" stroke-linecap="round"/>
  ${centro}`;

export const ILUSTRADOS = {
  diamante: (i) => `<defs>${lin(`${i}a`, "#a5f3fc", "#0891b2")}${lin(`${i}b`, "#67e8f9", "#155e75")}</defs>
    <path d="M18 8h28l12 15-26 34L6 23z" fill="url(#${i}a)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M6 23h52L32 57z" fill="url(#${i}b)"/>
    <path d="M18 8l6 15h16l6-15M24 23l8 34 8-34" fill="none" stroke="${T}" stroke-width="1.6" stroke-linejoin="round" opacity=".55"/>
    <path d="M6 23h52" stroke="${T}" stroke-width="2"/>
    <path d="M20 11l-7 10" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/>
    ${chispa(52, 9, 6)}${chispa(10, 44, 4, "#cffafe")}`,
  moneda_xp: (i) => moneda(i, "#fde68a", "#f59e0b", "#b45309",
    `<text x="32" y="40" text-anchor="middle" font-family="system-ui,sans-serif" font-size="22" font-weight="900" fill="#92400e">$</text>`),
  racha: (i) => `<defs>${lin(`${i}f`, "#fde047", "#ef4444")}${lin(`${i}n`, "#fff7ad", "#fb923c")}</defs>
    <path d="M34 3c3 10-6 13-3 21 3-2.5 5-6 4.5-10C46 21 52 30 50 41c-2 11-9.5 18-18 18S13 52 13 42c0-9 5-15.5 13-21.5-1 6.5 1 10.5 4 12.5C33 26 37.5 15 34 3z" fill="url(#${i}f)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M32 33c6 4.5 8 10 6 15-1.5 4-4 6-6 6s-5-2-6.5-6C24 43 26 37.5 32 33z" fill="url(#${i}n)"/>
    <path d="M22 30c-3 3.5-4.5 7-4.5 11" stroke="#fff" stroke-width="3" stroke-linecap="round" fill="none" opacity=".55"/>`,
  vidas: (i) => `<defs>${lin(`${i}h`, "#fb7185", "#be123c")}</defs>
    <path d="M32 56S6 41 6 22A13 13 0 0 1 32 15a13 13 0 0 1 26 7c0 19-26 34-26 34z" fill="url(#${i}h)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M14 20a7 7 0 0 1 8-6" stroke="#fff" stroke-width="3.5" stroke-linecap="round" fill="none" opacity=".75"/>
    <path d="M17 32h7l3.5-6 5 12 3-6h6" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`,
  mega_vidas: (i) => `<defs>${lin(`${i}p`, "#f9a8d4", "#db2777")}${lin(`${i}l`, "#fecdd3", "#fb7185")}</defs>
    <rect x="20" y="4" width="24" height="8" rx="3" fill="#94a3b8" stroke="${T}" stroke-width="2.5"/>
    <path d="M17 12h30v5c5 4 7 9 7 15v18a8 8 0 0 1-8 8H18a8 8 0 0 1-8-8V32c0-6 2-11 7-15z" fill="url(#${i}p)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M14 34h36v14a5 5 0 0 1-5 5H19a5 5 0 0 1-5-5z" fill="url(#${i}l)" opacity=".9"/>
    <path d="M32 49s-9-5-9-11a4.5 4.5 0 0 1 9-2 4.5 4.5 0 0 1 9 2c0 6-9 11-9 11z" fill="#be123c" stroke="${T}" stroke-width="1.8"/>
    <path d="M16 22c-2 3-2.5 6-2.5 9" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".6"/>`,
  impulso_xp: (i) => `<defs>${lin(`${i}r`, "#fef08a", "#f59e0b")}</defs>
    <circle cx="32" cy="32" r="27" fill="#312e81" stroke="${T}" stroke-width="2.5"/>
    <circle cx="32" cy="32" r="22" fill="none" stroke="#818cf8" stroke-width="2" stroke-dasharray="3 4"/>
    <path d="M36 8L16 36h13l-4 20 21-29H33z" fill="url(#${i}r)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M34 15l-9 13" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>`,
  salvarrachas: (i) => escudo(i, "#bae6fd", "#0284c7",
    `<path d="M32 18v24M21.5 24l21 12M42.5 24l-21 12" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>
     <path d="M32 18l-3 3m3-3l3 3M32 42l-3-3m3 3l3-3" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
     ${chispa(48, 12, 5)}`),
  cofre: (i) => cofreMini(i, ["#c2783a", "#8a4b1f"], ["#e5e9ef", "#7c8796"], "#f6c445"),
  cofre_misterioso: (i) => cofreMini(i, ["#7c3aed", "#3b0764"], ["#c4b5fd", "#6d28d9"], "#f0abfc", `<text x="32" y="42" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" font-weight="900" fill="#fff">?</text>`),
  cofre_legendario: (i) => cofreMini(i, ["#a855f7", "#4c1d95"], ["#fef08a", "#ca8a04"], "#fde047", "", true),
  xp15: (i) => xp(i, "+15", "#fde047", "#f97316"),
  xp30: (i) => xp(i, "+30", "#86efac", "#16a34a"),
  xp60: (i) => xp(i, "+60", "#c4b5fd", "#7c3aed"),
  niveles2: (i) => `<defs>${lin(`${i}g`, "#5eead4", "#0f766e")}</defs>
    <path d="M32 4l24 13.5v29L32 60 8 46.5v-29z" fill="url(#${i}g)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M32 10l18 10" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".5"/>
    <path d="M24 34l8-8 8 8M24 42l8-8 8 8" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`,
  niveles4: (i) => `<defs>${lin(`${i}g`, "#fde68a", "#d97706")}</defs>
    <path d="M32 4l24 13.5v29L32 60 8 46.5v-29z" fill="url(#${i}g)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M32 10l18 10" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".5"/>
    <path d="M22 26l8-8 8 8M22 34l8-8 8 8M22 42l8-8 8 8M22 50l8-8 8 8" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="translate(2 -4)"/>`,
  perfecto: (i) => `<defs>${lin(`${i}v`, "#86efac", "#15803d")}</defs>
    <circle cx="32" cy="32" r="27" fill="url(#${i}v)" stroke="${T}" stroke-width="2.5"/>
    <path d="M19 33l9 9 18-20" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    <path d="M14 22a20 20 0 0 1 10-9" stroke="#fff" stroke-width="3" stroke-linecap="round" fill="none" opacity=".55"/>${chispa(52, 12, 5, "#fde047")}`,
  perfectos3: (i) => `<defs>${lin(`${i}v`, "#86efac", "#15803d")}${lin(`${i}o`, "#fde68a", "#d97706")}</defs>
    <circle cx="20" cy="38" r="13" fill="url(#${i}v)" stroke="${T}" stroke-width="2.2"/><circle cx="44" cy="38" r="13" fill="url(#${i}v)" stroke="${T}" stroke-width="2.2"/>
    <circle cx="32" cy="22" r="15" fill="url(#${i}o)" stroke="${T}" stroke-width="2.4"/>
    <path d="M25 22l5 5 9-10" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    <path d="M14 38l4 4 8-8M38 38l4 4 8-8" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`,
  check: (i) => ILUSTRADOS.perfecto(i),
  corona_campeon: (i) => `<defs>${lin(`${i}c`, "#fef08a", "#d97706")}</defs>
    <path d="M6 20l14 11 12-22 12 22 14-11-5 33H11z" fill="url(#${i}c)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <rect x="11" y="47" width="42" height="8" rx="2" fill="#b45309" stroke="${T}" stroke-width="2.2"/>
    <circle cx="32" cy="36" r="4.5" fill="#ef4444" stroke="${T}" stroke-width="1.8"/><circle cx="19" cy="39" r="3" fill="#3b82f6" stroke="${T}" stroke-width="1.6"/><circle cx="45" cy="39" r="3" fill="#22c55e" stroke="${T}" stroke-width="1.6"/>
    <circle cx="6" cy="20" r="3.5" fill="#fde047" stroke="${T}" stroke-width="1.8"/><circle cx="32" cy="9" r="3.5" fill="#fde047" stroke="${T}" stroke-width="1.8"/><circle cx="58" cy="20" r="3.5" fill="#fde047" stroke="${T}" stroke-width="1.8"/>`,
  titulo_leyenda: (i) => `<defs>${lin(`${i}e`, "#fde68a", "#f59e0b")}</defs>
    <path d="M10 40l-6 12h12l4 6 6-12z" fill="#dc2626" stroke="${T}" stroke-width="2"/><path d="M54 40l6 12H48l-4 6-6-12z" fill="#dc2626" stroke="${T}" stroke-width="2"/>
    <path d="M32 4l7.6 15.4L56 21.8 44 33.4 46.8 50 32 42.2 17.2 50 20 33.4 8 21.8l16.4-2.4z" fill="url(#${i}e)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M32 12l4 8" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>`,
  candado: (i) => `<defs>${lin(`${i}k`, "#fde68a", "#d97706")}</defs>
    <path d="M20 28v-8a12 12 0 0 1 24 0v8" fill="none" stroke="#94a3b8" stroke-width="6"/><path d="M20 28v-8a12 12 0 0 1 24 0v8" fill="none" stroke="${T}" stroke-width="1.6" opacity=".4"/>
    <rect x="12" y="27" width="40" height="31" rx="7" fill="url(#${i}k)" stroke="${T}" stroke-width="2.5"/>
    <circle cx="32" cy="40" r="4.5" fill="${T}"/><path d="M30.5 43h3l1 7h-5z" fill="${T}"/><path d="M16 32h32" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".5"/>`,
  calendario: (i) => `<defs>${lin(`${i}c`, "#f87171", "#b91c1c")}</defs>
    <rect x="8" y="10" width="48" height="46" rx="8" fill="#fff" stroke="${T}" stroke-width="2.5"/>
    <path d="M8 18a8 8 0 0 1 8-8h32a8 8 0 0 1 8 8v8H8z" fill="url(#${i}c)" stroke="${T}" stroke-width="2.5"/>
    <rect x="18" y="4" width="5" height="12" rx="2.5" fill="#94a3b8" stroke="${T}" stroke-width="2"/><rect x="41" y="4" width="5" height="12" rx="2.5" fill="#94a3b8" stroke="${T}" stroke-width="2"/>
    <g fill="#cbd5e1"><rect x="15" y="32" width="8" height="7" rx="2"/><rect x="28" y="32" width="8" height="7" rx="2"/><rect x="15" y="43" width="8" height="7" rx="2"/><rect x="28" y="43" width="8" height="7" rx="2"/></g>
    <rect x="41" y="32" width="8" height="7" rx="2" fill="#f97316"/><rect x="41" y="43" width="8" height="7" rx="2" fill="#22c55e"/>`,
  potenciador: (i) => ILUSTRADOS.impulso_xp(i),
  gafas_pro: (i) => `<defs>${lin(`${i}l`, "#67e8f9", "#7c3aed", 1, 1)}</defs>
    <path d="M4 26h56" stroke="${T}" stroke-width="4" stroke-linecap="round"/>
    <path d="M6 24h22v6c0 7-5 12-11 12S6 37 6 30zM36 24h22v6c0 7-5 12-11 12s-11-5-11-12z" fill="url(#${i}l)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M10 28l6-3M40 28l6-3" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>`,
  marco_dorado: (i) => `<defs>${lin(`${i}o`, "#fde68a", "#b45309", 1, 1)}</defs>
    <rect x="6" y="6" width="52" height="52" rx="10" fill="url(#${i}o)" stroke="${T}" stroke-width="2.5"/>
    <rect x="15" y="15" width="34" height="34" rx="6" fill="#1e293b" stroke="${T}" stroke-width="2"/>
    <circle cx="32" cy="29" r="7" fill="#94a3b8"/><path d="M20 47c2-7 7-10 12-10s10 3 12 10" fill="#94a3b8"/>
    ${chispa(52, 10, 5)}${chispa(10, 52, 4)}`,
  estela_cohete: (i) => `<defs>${lin(`${i}c`, "#f1f5f9", "#94a3b8", 1, 1)}${lin(`${i}f`, "#fde047", "#ef4444")}</defs>
    <path d="M14 50c-4 0-8-4-8-4s2 8 8 10c3-4 3-6 0-6z" fill="url(#${i}f)"/>
    <path d="M40 8c10-3 16-2 16-2s1 6-2 16L34 42l-12-12z" fill="url(#${i}c)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <circle cx="42" cy="22" r="5" fill="#38bdf8" stroke="${T}" stroke-width="2.2"/>
    <path d="M22 30l-10 2-4 8 12-2M34 42l-2 10-8 4 2-12" fill="#ef4444" stroke="${T}" stroke-width="2.2" stroke-linejoin="round"/>
    <path d="M24 40l-12 12" stroke="url(#${i}f)" stroke-width="7" stroke-linecap="round"/>`,
  aura_neon: (i) => `<defs><radialGradient id="${i}a" cx=".5" cy=".5" r=".5"><stop offset=".45" stop-color="#22d3ee" stop-opacity="0"/><stop offset=".75" stop-color="#a855f7" stop-opacity=".9"/><stop offset="1" stop-color="#a855f7" stop-opacity="0"/></radialGradient></defs>
    <circle cx="32" cy="32" r="30" fill="url(#${i}a)"/><circle cx="32" cy="32" r="16" fill="#1e293b" stroke="#22d3ee" stroke-width="3"/>
    <circle cx="27" cy="30" r="2.5" fill="#22d3ee"/><circle cx="37" cy="30" r="2.5" fill="#22d3ee"/><path d="M26 37q6 4 12 0" stroke="#22d3ee" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    ${chispa(52, 10, 5, "#f0abfc")}${chispa(12, 50, 4, "#67e8f9")}`,
  mascota_dragon: (i) => `<defs>${lin(`${i}d`, "#86efac", "#15803d")}</defs>
    <path d="M10 22l10 6-2-12 10 8 2-14 8 14 8-6-2 12 10-4-6 10" fill="#facc15" stroke="${T}" stroke-width="2" stroke-linejoin="round"/>
    <ellipse cx="32" cy="38" rx="20" ry="18" fill="url(#${i}d)" stroke="${T}" stroke-width="2.5"/>
    <ellipse cx="32" cy="46" rx="10" ry="6" fill="#bbf7d0" stroke="${T}" stroke-width="1.8"/>
    <circle cx="24" cy="34" r="4" fill="#fff" stroke="${T}" stroke-width="1.6"/><circle cx="40" cy="34" r="4" fill="#fff" stroke="${T}" stroke-width="1.6"/>
    <circle cx="25" cy="34" r="2" fill="${T}"/><circle cx="41" cy="34" r="2" fill="${T}"/><circle cx="29" cy="46" r="1.3" fill="${T}"/><circle cx="35" cy="46" r="1.3" fill="${T}"/>`,
  fondo: (i) => `<defs>${lin(`${i}c`, "#7dd3fc", "#c4b5fd")}</defs>
    <rect x="6" y="10" width="52" height="44" rx="8" fill="url(#${i}c)" stroke="${T}" stroke-width="2.5"/>
    <circle cx="44" cy="23" r="5" fill="#fde047" stroke="${T}" stroke-width="1.8"/>
    <path d="M6 46l14-16 10 11 8-8 20 18v3a8 8 0 0 1-8 8H14a8 8 0 0 1-8-8z" fill="#22c55e" stroke="${T}" stroke-width="2.2" stroke-linejoin="round"/>`,
  cursor: (i) => `<defs>${lin(`${i}c`, "#ffffff", "#cbd5e1")}</defs>
    <path d="M14 6l34 20-15 4-8 14z" fill="url(#${i}c)" stroke="${T}" stroke-width="2.8" stroke-linejoin="round"/>
    <path d="M33 30l12 16" stroke="${T}" stroke-width="5" stroke-linecap="round"/><path d="M33 30l12 16" stroke="#a855f7" stroke-width="2" stroke-linecap="round"/>
    ${chispa(50, 50, 6, "#f0abfc")}`,
  tema: (i) => `<defs>${lin(`${i}p`, "#fde68a", "#d97706")}</defs>
    <path d="M32 6C16 6 6 17 6 30c0 14 12 26 26 26 4 0 6-3 6-6 0-4-3-5-3-8 0-2.5 2-4 4.5-4H46c7 0 12-5 12-12C58 15 46 6 32 6z" fill="url(#${i}p)" stroke="${T}" stroke-width="2.5"/>
    <circle cx="18" cy="30" r="4.5" fill="#ef4444" stroke="${T}" stroke-width="1.6"/><circle cx="24" cy="17" r="4.5" fill="#3b82f6" stroke="${T}" stroke-width="1.6"/>
    <circle cx="38" cy="15" r="4.5" fill="#22c55e" stroke="${T}" stroke-width="1.6"/><circle cx="47" cy="25" r="4.5" fill="#a855f7" stroke="${T}" stroke-width="1.6"/>`,
  marco: (i) => `<defs>${lin(`${i}m`, "#c4b5fd", "#7c3aed", 1, 1)}</defs>
    <circle cx="32" cy="32" r="27" fill="url(#${i}m)" stroke="${T}" stroke-width="2.5"/><circle cx="32" cy="32" r="18" fill="#1e293b" stroke="${T}" stroke-width="2"/>
    <circle cx="32" cy="28" r="6" fill="#94a3b8"/><path d="M21 45c2-6 6-8 11-8s9 2 11 8" fill="#94a3b8"/>${chispa(52, 10, 5)}`,
  efecto: (i) => `<defs>${lin(`${i}e`, "#f0abfc", "#7c3aed")}</defs>
    ${chispa(32, 32, 26, `url(#${i}e)`)}${chispa(50, 12, 7, "#fde047")}${chispa(12, 50, 6, "#67e8f9")}${chispa(52, 50, 4, "#86efac")}`,
  dedo: (i) => `<defs>${lin(`${i}t`, "#334155", "#0f172a")}</defs>
    <rect x="14" y="4" width="36" height="56" rx="8" fill="url(#${i}t)" stroke="${T}" stroke-width="2.5"/>
    <rect x="18" y="10" width="28" height="40" rx="3" fill="#38bdf8"/><circle cx="32" cy="55" r="2.5" fill="#94a3b8"/>
    <circle cx="32" cy="30" r="6" fill="#fff" opacity=".9"/><circle cx="32" cy="30" r="11" fill="none" stroke="#fff" stroke-width="2" opacity=".6"/>`,
  avatar: (i) => `<defs>${lin(`${i}a`, "#fde68a", "#f59e0b")}</defs>
    <circle cx="32" cy="32" r="27" fill="url(#${i}a)" stroke="${T}" stroke-width="2.5"/>
    <circle cx="23" cy="28" r="4" fill="${T}"/><circle cx="41" cy="28" r="4" fill="${T}"/><circle cx="24.5" cy="26.5" r="1.4" fill="#fff"/><circle cx="42.5" cy="26.5" r="1.4" fill="#fff"/>
    <path d="M21 39q11 10 22 0" stroke="${T}" stroke-width="3" stroke-linecap="round" fill="none"/><ellipse cx="16" cy="37" rx="4" ry="2.5" fill="#fb7185" opacity=".6"/><ellipse cx="48" cy="37" rx="4" ry="2.5" fill="#fb7185" opacity=".6"/>`,
  coleccion: (i) => `<defs>${lin(`${i}b`, "#fca5a5", "#dc2626")}</defs>
    <path d="M10 22h44l-4 34H14z" fill="url(#${i}b)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M22 22v-6a10 10 0 0 1 20 0v6" fill="none" stroke="${T}" stroke-width="3"/>
    <path d="M12 30h40" stroke="#fff" stroke-width="2.5" opacity=".5"/>${chispa(32, 42, 8, "#fde047")}`,
};

function cofreMini(i, caja, metal, cerradura, extra = "", legendario = false) {
  return `<defs>${lin(`${i}c`, caja[0], caja[1])}${lin(`${i}b`, metal[0], metal[1])}</defs>
    ${legendario ? `<circle cx="32" cy="34" r="30" fill="${caja[0]}" opacity=".18"/>` : ""}
    <path d="M6 30h52v20a6 6 0 0 1-6 6H12a6 6 0 0 1-6-6z" fill="url(#${i}c)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M6 30V22c0-9 11.6-15 26-15s26 6 26 15v8z" fill="url(#${i}c)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <path d="M6 27h52v6H6z" fill="url(#${i}b)" stroke="${T}" stroke-width="2"/>
    <path d="M15 9.5V56M49 9.5V56" stroke="url(#${i}b)" stroke-width="6"/>
    <rect x="25" y="26" width="14" height="17" rx="3.5" fill="${cerradura}" stroke="${T}" stroke-width="2.2"/><circle cx="32" cy="33" r="2.2" fill="${T}"/><path d="M31 34.5h2l.6 4.5h-3.2z" fill="${T}"/>
    <path d="M12 18q20-9 40 0" stroke="#fff" stroke-width="2.5" stroke-linecap="round" fill="none" opacity=".4"/>
    ${extra}${legendario ? `${chispa(56, 8, 6, "#fde047")}${chispa(8, 12, 4, "#f0abfc")}` : ""}`;
}

// Íconos de los encargos del día (recompensas.js y la columna derecha)
const terminal = (i, texto, color) => `<defs>${lin(`${i}t`, "#334155", "#0f172a")}</defs>
  <rect x="5" y="9" width="54" height="46" rx="8" fill="url(#${i}t)" stroke="${T}" stroke-width="2.5"/>
  <path d="M5 18a9 9 0 0 1 9-9h36a9 9 0 0 1 9 9v2H5z" fill="#475569"/><circle cx="12" cy="15" r="2" fill="#f87171"/><circle cx="18" cy="15" r="2" fill="#fbbf24"/><circle cx="24" cy="15" r="2" fill="#4ade80"/>
  <path d="M14 30l7 5-7 5" stroke="${color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <text x="40" y="46" text-anchor="middle" font-family="ui-monospace,Consolas,monospace" font-size="13" font-weight="900" fill="${color}">${texto}</text>`;
const libro = (i, n, a, b) => `<defs>${lin(`${i}l`, a, b)}</defs>
  <path d="M6 14c9-4 18-3 26 2v40c-8-5-17-6-26-2z" fill="url(#${i}l)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M58 14c-9-4-18-3-26 2v40c8-5 17-6 26-2z" fill="url(#${i}l)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M12 24c5-1.5 10-1 14 1M12 31c5-1.5 10-1 14 1M38 25c4-2 9-2.5 14-1M38 32c4-2 9-2.5 14-1" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".7"/>
  ${n ? `<circle cx="50" cy="48" r="10" fill="#22c55e" stroke="${T}" stroke-width="2.2"/><text x="50" y="52.5" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" font-weight="900" fill="#fff">${n}</text>` : ""}`;
const burbuja = (i, n) => `<defs>${lin(`${i}b`, "#7dd3fc", "#2563eb")}</defs>
  <path d="M8 12h48a4 4 0 0 1 4 4v26a4 4 0 0 1-4 4H26L14 56V46H8a4 4 0 0 1-4-4V16a4 4 0 0 1 4-4z" fill="url(#${i}b)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
  <circle cx="20" cy="29" r="3.5" fill="#fff"/><circle cx="32" cy="29" r="3.5" fill="#fff"/><circle cx="44" cy="29" r="3.5" fill="#fff"/>
  ${n ? `<circle cx="54" cy="12" r="9" fill="#ef4444" stroke="${T}" stroke-width="2"/><text x="54" y="16" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" font-weight="900" fill="#fff">${n}</text>` : ""}`;
const robot = (i, n) => `<defs>${lin(`${i}r`, "#5ef2ff", "#2f4677")}</defs>
  <path d="M32 6v8" stroke="${T}" stroke-width="3"/><circle cx="32" cy="6" r="4" fill="#b8ff3c" stroke="${T}" stroke-width="2"/>
  <rect x="8" y="14" width="48" height="40" rx="16" fill="#1b2b52" stroke="url(#${i}r)" stroke-width="3"/>
  <rect x="15" y="22" width="34" height="22" rx="10" fill="#08142a"/><rect x="21" y="27" width="6" height="10" rx="3" fill="#5ef2ff"/><rect x="37" y="27" width="6" height="10" rx="3" fill="#5ef2ff"/>
  ${n ? `<circle cx="54" cy="50" r="9" fill="#a855f7" stroke="${T}" stroke-width="2"/><text x="54" y="54" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" font-weight="900" fill="#fff">${n}</text>` : ""}`;
Object.assign(ILUSTRADOS, {
  codigo1: (i) => terminal(i, "1", "#4ade80"),
  codigo5: (i) => terminal(i, "×5", "#fbbf24"),
  lecciones1: (i) => libro(i, "1", "#fda4af", "#e11d48"),
  lecciones2: (i) => libro(i, "2", "#93c5fd", "#2563eb"),
  lecciones3: (i) => libro(i, "3", "#c4b5fd", "#7c3aed"),
  lecciones5: (i) => libro(i, "5", "#fde68a", "#d97706"),
  estudioso: (i) => libro(i, "", "#86efac", "#15803d") + chispa(52, 10, 6, "#fde047"),
  mensajes1: (i) => burbuja(i, ""),
  mensajes5: (i) => burbuja(i, "5"),
  ia1: (i) => robot(i, ""),
  ia3: (i) => robot(i, "3"),
  perfectos2: (i) => ILUSTRADOS.perfectos3(i),
  niveles5: (i) => ILUSTRADOS.niveles4(i),
  combo: (i) => `<defs>${lin(`${i}c`, "#fde047", "#f97316")}</defs>
    <path d="M36 4L14 36h14l-4 24 26-34H35z" fill="url(#${i}c)" stroke="${T}" stroke-width="2.5" stroke-linejoin="round"/>
    <text x="50" y="58" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" font-weight="900" fill="#ef4444" stroke="#fff" stroke-width=".6">x3</text>`,
  maraton: (i) => `<defs>${lin(`${i}m`, "#fca5a5", "#dc2626")}</defs>
    <circle cx="32" cy="34" r="24" fill="#fff" stroke="${T}" stroke-width="2.5"/><circle cx="32" cy="34" r="19" fill="none" stroke="url(#${i}m)" stroke-width="5" stroke-dasharray="90 30" stroke-linecap="round"/>
    <rect x="27" y="4" width="10" height="6" rx="2" fill="#94a3b8" stroke="${T}" stroke-width="2"/><path d="M32 34V22M32 34l8 5" stroke="${T}" stroke-width="3" stroke-linecap="round"/>`,
});
