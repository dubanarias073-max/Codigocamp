// Cosméticos de la tienda y los cofres: cómo se ve cada fondo, puntero, tema, marco, efecto y estela del dedo, y cómo se aplican
// en todas las páginas. Todo es original (CSS, SVG y canvas), sin imágenes externas.
const svg = (cuerpo, w = 32, h = 32) => `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 32 32">${cuerpo}</svg>`)}`;
const reducido = () => { try { if (localStorage.getItem("cc_menos_mov") === "1") return true; } catch { /* nada */ } return matchMedia("(prefers-reduced-motion: reduce)").matches; };

// ------------------------------------------------------------------------------------ punteros ----
export const CURSORES = {
  cursor_cohete: { x: 3, y: 3, svg: '<path d="M4 4l9 3 10 10-4 4L9 11z" fill="#e5e7eb" stroke="#1f2937" stroke-width="1.5" stroke-linejoin="round"/><circle cx="14" cy="13" r="2.2" fill="#38bdf8" stroke="#1f2937"/><path d="M19 21l3 6 3-3-2-5M21 17l6 3-3 3-5-2" fill="#f97316" stroke="#1f2937" stroke-linejoin="round"/>' },
  cursor_espada: { x: 2, y: 2, svg: '<path d="M2 2h4v2h2v2h2v2h2v2h2v2h2v2h-2v2h-2v-2h-2v-2H10v-2H8v-2H6V8H4V6H2z" fill="#cbd5e1" stroke="#0f172a" stroke-width="1"/><path d="M16 18h2v-2h2v2h2v2h-2v2h-2v-2h-2z" fill="#a16207" stroke="#0f172a"/><path d="M22 22h4v4h-4z" fill="#facc15" stroke="#0f172a"/>' },
  cursor_varita: { x: 4, y: 4, svg: '<path d="M10 10l17 17" stroke="#1f2937" stroke-width="5" stroke-linecap="round"/><path d="M10 10l17 17" stroke="#7c3aed" stroke-width="3" stroke-linecap="round"/><path d="M6 1l1.6 3.4L11 6 7.6 7.6 6 11 4.4 7.6 1 6l3.4-1.6z" fill="#fde047" stroke="#a16207"/>' },
  cursor_lapiz: { x: 2, y: 29, svg: '<path d="M3 29l2-7L22 5l5 5L10 27z" fill="#fbbf24" stroke="#1f2937" stroke-width="1.5" stroke-linejoin="round"/><path d="M3 29l2-7 5 5z" fill="#fde68a" stroke="#1f2937" stroke-linejoin="round"/><path d="M19 8l5 5" stroke="#1f2937"/><path d="M22 5l5 5 2-2-5-5z" fill="#f472b6" stroke="#1f2937"/>' },
  cursor_neon: { x: 2, y: 2, svg: '<path d="M3 3l22 9-9 3-3 9z" fill="#0e7490" stroke="#22d3ee" stroke-width="2" stroke-linejoin="round"/><path d="M3 3l22 9-9 3-3 9z" fill="none" stroke="#a5f3fc" stroke-width=".8" stroke-linejoin="round"/>' },
  cursor_gato: { x: 16, y: 16, svg: '<ellipse cx="16" cy="20" rx="7" ry="6" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="8" cy="11" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="14" cy="7" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="20" cy="7" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/><circle cx="25" cy="11" r="3" fill="#fda4af" stroke="#9f1239" stroke-width="1.4"/>' },
  cursor_estrella: { x: 4, y: 4, svg: '<path d="M30 30L11 11" stroke="#fde047" stroke-width="3" stroke-linecap="round" opacity=".5"/><path d="M8 1l2.2 4.6 5 .7-3.6 3.5.9 5L8 12.4 3.5 14.8l.9-5L.8 6.3l5-.7z" fill="#facc15" stroke="#a16207"/>' },
  cursor_corona: { x: 3, y: 3, svg: '<path d="M3 3l7 18h3z" fill="#e5e7eb" stroke="#1f2937" stroke-width="1.2"/><path d="M13 18l3-8 4 5 3-7 3 7 4-5 1 8z" fill="#facc15" stroke="#92400e" stroke-width="1.2" stroke-linejoin="round"/><rect x="13" y="18" width="17" height="4" rx="1" fill="#f59e0b" stroke="#92400e"/><circle cx="21.5" cy="20" r="1.2" fill="#ef4444"/>' },
  cursor_rayo: { x: 14, y: 2, svg: '<path d="M18 1L6 18h8l-4 13 16-19h-9l5-11z" fill="#fde047" stroke="#a16207" stroke-width="1.5" stroke-linejoin="round"/><path d="M17 4l-7 11h6" fill="none" stroke="#fff" stroke-width="1.2" opacity=".8"/>' },
  cursor_sable: { x: 2, y: 2, svg: '<path d="M3 3l17 17" stroke="#22d3ee" stroke-width="6" stroke-linecap="round" opacity=".35"/><path d="M3 3l17 17" stroke="#a5f3fc" stroke-width="3" stroke-linecap="round"/><path d="M3 3l17 17" stroke="#fff" stroke-width="1.2" stroke-linecap="round"/><path d="M19 22l3-3 6 6-3 3z" fill="#64748b" stroke="#0f172a" stroke-width="1.2"/><path d="M20 18l4 4" stroke="#0f172a" stroke-width="2"/>' },
  cursor_diamante: { x: 3, y: 3, svg: '<path d="M3 3l22 10-9 3-3 10z" fill="#a5f3fc" stroke="#0e7490" stroke-width="1.6" stroke-linejoin="round"/><path d="M3 3l13 13M25 13l-9 3M13 26l3-10" stroke="#ecfeff" stroke-width="1" opacity=".9"/><path d="M8 8l4 1-1 4" fill="#fff" opacity=".7"/><circle cx="24" cy="5" r="1.6" fill="#fff"/><circle cx="27" cy="9" r="1" fill="#fff"/>' },
};
export const urlCursor = (clave) => (CURSORES[clave] ? svg(CURSORES[clave].svg) : null);

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
  fondo_dragon: { canvas: "brasas", css: "background:radial-gradient(ellipse at 50% 110%,rgba(249,115,22,.55),transparent 60%),radial-gradient(ellipse at 80% 20%,rgba(220,38,38,.35),transparent 50%),linear-gradient(#1c0505,#3b0a0a 60%,#120202)", oscuro: true },
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
html.cc-con-fondo.cc-fondo-oscuro .tarjeta,html.cc-con-fondo.cc-fondo-oscuro .lado,html.cc-con-fondo.cc-fondo-oscuro .der .tarjeta{backdrop-filter:blur(6px)}
.cc-marco{position:relative;display:inline-grid;place-items:center;border-radius:50%;padding:4px;isolation:isolate}
.cc-marco::before{content:"";position:absolute;inset:0;border-radius:50%;z-index:-1}
.cc-marco>*{border-radius:50%}
${Object.entries(MARCOS).map(([k, v]) => `.cc-marco[data-marco="${k}"]::before{${v}}`).join("\n")}
.cc-prev-inicial{display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#0d9488,#4d7c0f);color:#fff;font:800 24px/1 system-ui,sans-serif}
.cc-particula-txt{border-radius:0;white-space:nowrap}
.cc-particula{position:fixed;z-index:9999;pointer-events:none;border-radius:50%;will-change:transform,opacity}
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
  let ancho, alto, cols, gotas, brasas, copos, estrellas, giro = 0, vivo = true, ultimo = 0;
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
  p.style.cssText = `left:${x}px;top:${y}px;width:${tam}px;height:${tam}px;${forma === "estrella" ? `background:none;color:${color};font-size:${tam * 1.6}px;line-height:1` : forma === "burbuja" ? `border:2px solid ${color};background:rgba(255,255,255,.15)` : forma === "cuadro" ? `background:${color};border-radius:2px` : `background:${color};box-shadow:0 0 6px ${color}`}`;
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
  efecto_fuegos: (x, y) => { const c = ["#f43f5e", "#facc15", "#22d3ee", "#a855f7", "#4ade80", "#fb923c"]; const base = c[(Math.random() * c.length) | 0]; for (let i = 0; i < 28; i++) { const a = (i / 28) * Math.PI * 2, d = 70 + Math.random() * 50; particula(x, y, { color: i % 3 ? base : "#fff", tam: 4 + Math.random() * 3, dx: Math.cos(a) * d, dy: Math.sin(a) * d + 20, dur: 900 + Math.random() * 500, forma: "punto" }); } },
};

// ---- estelas del dedo (celular): siguen el dedo al tocar y deslizar la pantalla
const ARCOIRIS = ["#f43f5e", "#f59e0b", "#facc15", "#4ade80", "#22d3ee", "#6366f1", "#d946ef"];
function texto(x, y, ch, { color, tam, dx, dy, dur }) {
  const p = document.createElement("span");
  p.className = "cc-particula cc-particula-txt";
  p.textContent = ch;
  p.style.cssText = `left:${x}px;top:${y}px;color:${color};font:800 ${tam}px/1 ui-monospace,Consolas,monospace;text-shadow:0 0 6px ${color}`;
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
};
function onda(x, y, color) {
  const p = document.createElement("span");
  p.className = "cc-particula";
  p.style.cssText = `left:${x}px;top:${y}px;width:18px;height:18px;border:2px solid ${color};background:none`;
  document.body.appendChild(p);
  p.animate([{ transform: "translate(-50%,-50%) scale(.4)", opacity: .9 }, { transform: "translate(-50%,-50%) scale(2.6)", opacity: 0 }], { duration: 450, easing: "ease-out" }).onfinish = () => p.remove();
}
const COLOR_DEDO = { dedo_tinta: "#3b82f6", dedo_burbujas: "#7dd3fc", dedo_neon: "#22d3ee", dedo_codigo: "#4ade80", dedo_arcoiris: "#f59e0b", dedo_fuego: "#f97316", dedo_galaxia: "#c084fc" };

/**
 * Hace que una estela siga al dedo dentro de «zona» (window en las páginas, la tarjeta en la tienda).
 * soloTactil: en las páginas solo con el dedo o el lápiz (con mouse ya están los punteros y efectos).
 */
export function seguirDedo(zona, clave, { soloTactil = true } = {}) {
  const e = DEDOS[clave];
  if (!e) return () => {};
  let abajo = false, i = 0, ultimo = 0, ux = 0, uy = 0;
  const vale = (ev) => !soloTactil || ev.pointerType === "touch" || ev.pointerType === "pen";
  const bajar = (ev) => { if (!vale(ev)) return; abajo = true; ux = ev.clientX; uy = ev.clientY; onda(ux, uy, COLOR_DEDO[clave]); e.tocar?.(ux, uy); };
  const mover = (ev) => {
    if (zona !== window && !zona.isConnected) { quitar(); return; }   // la tarjeta ya no está (la tienda se volvió a pintar)
    if (!abajo || !vale(ev)) return;
    const t = performance.now();
    if (t - ultimo < 16) return;
    ultimo = t;
    // Rellena el camino si el dedo va rápido, para que la estela no quede con huecos
    const pasos = Math.min(4, Math.max(1, Math.round(Math.hypot(ev.clientX - ux, ev.clientY - uy) / 14)));
    for (let k = 1; k <= pasos; k++) e.mover(ux + (ev.clientX - ux) * k / pasos, uy + (ev.clientY - uy) * k / pasos, i++);
    ux = ev.clientX; uy = ev.clientY;
  };
  const subir = () => { abajo = false; };
  zona.addEventListener("pointerdown", bajar, { passive: true });
  addEventListener("pointermove", mover, { passive: true });
  addEventListener("pointerup", subir, { passive: true });
  addEventListener("pointercancel", subir, { passive: true });
  // Al desplazar la página, el navegador manda pointercancel: se sigue con los eventos táctiles
  const tmover = (ev) => { if (abajo) { const t0 = ev.touches[0]; mover({ clientX: t0.clientX, clientY: t0.clientY, pointerType: "touch" }); } };
  addEventListener("touchmove", tmover, { passive: true });
  addEventListener("touchend", subir, { passive: true });
  const quitar = () => {
    zona.removeEventListener("pointerdown", bajar);
    removeEventListener("pointermove", mover); removeEventListener("pointerup", subir); removeEventListener("pointercancel", subir);
    removeEventListener("touchmove", tmover); removeEventListener("touchend", subir);
  };
  return quitar;
}
let quitarDedo = null;
function activarDedo(clave) {
  quitarDedo?.();
  quitarDedo = null;
  if (!clave || reducido()) return;
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
  const cur = CURSORES[eq.cursor];
  estilo("cc-cosm-cursor", cur ? `html,body,a,button,[role=button],label,select,summary,.bj,.nav-i{cursor:url("${svg(cur.svg)}") ${cur.x} ${cur.y},auto!important}input[type=text],input[type=email],input[type=password],input[type=search],textarea,[contenteditable],.monaco-editor .view-lines{cursor:text!important}` : "");
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
    if (f.canvas) animarCanvas(f.canvas, caja);
    if (reducido()) caja.style.animation = "none";
  }
  // Efecto (clic) y estela del dedo (celular)
  activarEfecto(eq.efecto);
  activarDedo(eq.dedo);
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
    el.style.cursor = `url("${urlCursor(clave)}") ${CURSORES[clave].x} ${CURSORES[clave].y},auto`;
    el.innerHTML = `<img src="${urlCursor(clave)}" alt="" width="48" height="48">`;
  } else if (tipo === "tema" && TEMAS[clave]) {
    const t = TEMAS[clave];
    el.innerHTML = `<span style="background:${t.acc}"></span><span style="background:${t.acc2}"></span><span style="background:${t.cy}"></span>`;
    el.classList.add("cc-prev-tema");
  } else if (tipo === "marco" && MARCOS[clave]) {
    estilo("cc-cosmeticos-base", CSS_BASE);
    el.innerHTML = `<span class="cc-marco" data-marco="${clave}"><span class="cc-prev-cara cc-prev-inicial">A</span></span>`;
  } else if (tipo === "dedo" && DEDOS[clave]) {
    el.innerHTML = '<span class="cc-prev-efecto">Toca y desliza el dedo aquí</span>';
    el.style.touchAction = "none";   // dentro de la tarjeta, deslizar dibuja (no mueve la página)
    el.__quitarDedo?.();
    el.__quitarDedo = seguirDedo(el, clave, { soloTactil: false });
  } else if (tipo === "efecto") {
    el.innerHTML = '<span class="cc-prev-efecto">Haz clic aquí</span>';
    el.onpointerdown = (e) => { const fn = EFECTOS[clave]; if (fn) fn(e.clientX, e.clientY); else for (let i = 0; i < 6; i++) particula(e.clientX, e.clientY, { color: "#facc15", tam: 9, dx: (Math.random() - .5) * 40, dy: 20 + Math.random() * 20, dur: 700, forma: "estrella" }); };
  }
}
