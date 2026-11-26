// Medallas del mes (como las de Duolingo): cada mes tiene su diseño, con la temporada de ese mes.
// svgMedalla(numeroDelMes, { tam, ganada }) devuelve el dibujo; las que no tienes se ven en gris con candado.

import { codiSVG } from "/js/codi.js";
import { logo } from "/js/logos.js";

// Insignias estilo Duolingo con Codi disfrazado o logos de programación. Cada MES de cada AÑO tiene la suya:
// el diseño sale de (año, mes), así la medalla de noviembre 2026 no es igual a la de noviembre 2027.
const PALETAS = [
  ["#fde047", "#7c3aed", "#4c1d95"], ["#fda4af", "#e11d48", "#881337"], ["#bae6fd", "#0369a1", "#0c4a6e"], ["#fef08a", "#ca8a04", "#713f12"],
  ["#fed7aa", "#ea580c", "#7c2d12"], ["#a5f3fc", "#7c3aed", "#3b0764"], ["#fecaca", "#dc2626", "#7f1d1d"], ["#d9f99d", "#16a34a", "#14532d"],
  ["#cbd5e1", "#0f172a", "#020617"], ["#99f6e4", "#0d9488", "#134e4a"], ["#f5d0fe", "#c026d3", "#701a75"], ["#c7d2fe", "#4f46e5", "#312e81"],
  ["#fbcfe8", "#db2777", "#831843"], ["#e9d5ff", "#9333ea", "#3b0764"], ["#fde68a", "#2563eb", "#1e3a8a"], ["#bbf7d0", "#059669", "#064e3b"],
];
const CODIS = [
  ["celebra", "codi_corona"], ["feliz", "codi_gafas"], ["pensando", "codi_birrete"], ["celebra", "codi_jetpack"], ["guino", "codi_pirata"],
  ["feliz", "codi_astronauta"], ["fuego", "codi_vikingo"], ["celebra", "codi_mago"], ["feliz", "codi_audifonos"], ["guino", "codi_banda_ninja"],
  ["feliz", "codi_caballero"], ["celebra", "codi_capa"], ["feliz", "codi_vr"], ["guino", "codi_carreras"], ["feliz", "codi_minero"],
  ["celebra", "codi_alas"], ["feliz", "codi_control"], ["pensando", "codi_explorador"], ["fuego", "codi_jefe_final"], ["feliz", "codi_kart"],
  ["ama", "codi_halo"], ["feliz", "codi_gorra"], ["guino", "codi_bigote"], ["feliz", "codi_escudo"],
];
const LOGOS_M = ["python", "javascript", "typescript", "java", "c", "cpp", "csharp", "go", "rust", "swift", "kotlin", "php", "lua", "r", "ruby",
  "html", "css", "sql", "react", "docker", "git", "github", "node", "terminal", "nosql", "reactnative"];
const ADORNOS = ["✦", "{ }", "</>", ">_", "★", "01", "⚡", "#", "λ", "∞", "♦", "✧"];
const FORMAS = ["escudo", "hexagono", "octagono", "gota"];
// Meses con temporada: siempre su tema (Codi disfrazado), pero con disfraz y colores distintos cada año
const TEMPORADA = {
  2: { codis: [["ama", "codi_flor"], ["ama", "codi_halo"], ["guino", "codi_corbatin"]], paletas: [1, 12, 10], adorno: "♥" },
  9: { codis: [["celebra", "codi_birrete"], ["celebra", "codi_gafas"], ["feliz", "codi_audifonos"]], paletas: [7, 3, 9], adorno: "</>" },
  10: { codis: [["guino", "temp_calabaza"], ["espia", "temp_bruja"], ["guino", "codi_capa"]], paletas: [4, 13, 5], adorno: "🦇" },
  12: { codis: [["feliz", "codi_navidad"], ["celebra", "codi_bufanda"], ["feliz", "codi_gorro_lana"]], paletas: [6, 15, 7], adorno: "❄" },
  1: { codis: [["celebra", "codi_corona"], ["celebra", "codi_jetpack"], ["fuego", "codi_corona"]], paletas: [0, 11, 14], adorno: "✦" },
};
const MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const hashDe = (t) => { let h = 2166136261; for (const ch of t) h = Math.imul(h ^ ch.charCodeAt(0), 16777619); return h >>> 0; };

/** El diseño único de un mes de un año. */
export function disenoMedalla(anio, mes) {
  const h = hashDe(`cc-medalla-${anio}-${mes}`);
  const t = TEMPORADA[mes];
  const k = anio % 3;
  const [c1, c2, borde] = PALETAS[t ? t.paletas[k] : h % PALETAS.length];
  const arte = t ? { codi: t.codis[k][0], acc: t.codis[k][1] }
    : (h >>> 4) % 3 === 0 ? { logo: LOGOS_M[(h >>> 6) % LOGOS_M.length] }
      : (() => { const [a, acc] = CODIS[(h >>> 6) % CODIS.length]; return { codi: a, acc }; })();
  return { c1, c2, borde, cinta: c2, arte, adorno: t ? t.adorno : ADORNOS[(h >>> 9) % ADORNOS.length], forma: FORMAS[(h >>> 12) % FORMAS.length] };
}

/** Insignia de la medalla (HTML): escudo con brillo, el arte de ese mes y año, y la cinta con el mes. */
export function svgMedalla(mes, { anio = new Date().getFullYear(), tam = 84, ganada = true, titulo = "" } = {}) {
  const d = disenoMedalla(anio, mes);
  const arte = d.arte.codi ? codiSVG(d.arte.codi, { tam: Math.round(tam * 0.78), animado: false, titulo: "", accesorio: d.arte.acc })
    : logo(d.arte.logo, Math.round(tam * 0.5));
  const nombre = titulo || `Medalla de ${MESES[mes - 1]} ${anio}`;
  return `<span class="cc-ins f-${d.forma}${ganada ? "" : " bloqueada"}" style="--t:${tam}px;--c1:${d.c1};--c2:${d.c2};--bd:${d.borde};--cinta:${d.cinta}" role="img" aria-label="${nombre}${ganada ? "" : " (aún no la tienes)"}">
    <span class="ins-escudo"><span class="ins-brillo"></span><span class="ins-adorno a1">${d.adorno}</span><span class="ins-adorno a2">${d.adorno}</span><span class="ins-arte${d.arte.logo ? " es-logo" : ""}">${arte}</span></span>
    <span class="ins-cinta">${MESES[mes - 1].slice(0, 3)} ${String(anio).slice(2)}</span>${ganada ? "" : '<span class="ins-candado">🔒</span>'}</span>`;
}

/** Fila de medallas para un perfil: las ganadas brillan; con `anio` muestra los 12 meses (los que faltan en gris). */
/** Las medallas empiezan en diciembre de 2026 (el servidor lo dice en «desde»): lo anterior no es de la temporada. */
const DESDE_DEFECTO = { anio: 2026, mes: 12 };
const valorMes = (anio, mes) => anio * 12 + mes;
/** Separa las del año que se muestra en la vitrina de las «de otros años» (incluidas las de antes del lanzamiento). */
export function separarMedallas(medallas, anio, desde = DESDE_DEFECTO) {
  const inicio = valorMes(desde.anio, desde.mes);
  const esDelAnio = (m) => m.anio === anio && valorMes(m.anio, m.numero) >= inicio;
  return { delAnio: medallas.filter(esDelAnio), otras: medallas.filter((m) => !esDelAnio(m)) };
}
export function vitrinaMedallas(medallas, { anio = null, tam = 64, desde = DESDE_DEFECTO } = {}) {
  if (anio) {
    // El año del lanzamiento empieza en el mes de inicio (2026: solo diciembre); los años anteriores no tienen vitrina
    const primero = anio === desde.anio ? desde.mes : anio < desde.anio ? 13 : 1;
    if (primero > 12) return `<p class="nota medallas-vacio">Las medallas del mes empiezan en ${MESES[desde.mes - 1]} de ${desde.anio}.</p>`;
    const del = new Map(separarMedallas(medallas, anio, desde).delAnio.map((m) => [m.numero, m]));
    return `<div class="medallas-vitrina">${Array.from({ length: 13 - primero }, (_, k) => primero - 1 + k).map((i) => {
      const m = del.get(i + 1);
      return `<figure class="md-fig${m ? " ganada" : ""}" title="${m ? `${m.nombre} · ${MESES[i]} ${anio}` : `${MESES[i]} ${anio}: todavía no`}">${svgMedalla(i + 1, { anio, tam, ganada: Boolean(m) })}<figcaption>${MESES[i].slice(0, 3)}</figcaption></figure>`;
    }).join("")}</div>`;
  }
  if (!medallas.length) return '<p class="nota medallas-vacio">Todavía no tiene medallas. Se ganan completando las experiencias del mes en Recompensas → Temporada.</p>';
  return `<div class="medallas-vitrina">${medallas.map((m) => `<figure class="md-fig ganada" title="${m.nombre} · ${m.mes} ${m.anio}">${svgMedalla(m.numero, { anio: m.anio, tam })}<figcaption>${m.mes.slice(0, 3)} ${String(m.anio).slice(2)}</figcaption></figure>`).join("")}</div>`;
}

export const CSS_MEDALLAS = `
.cc-ins{position:relative;display:inline-grid;place-items:center;width:var(--t);height:calc(var(--t)*1.12);flex:none}
.ins-escudo{position:relative;display:grid;place-items:center;width:100%;height:calc(var(--t)*1.02);overflow:hidden;
  clip-path:polygon(50% 0,93% 18%,93% 70%,50% 100%,7% 70%,7% 18%);background:linear-gradient(160deg,var(--c1),var(--c2));
  box-shadow:inset 0 0 0 calc(var(--t)*.06) var(--bd)}
.ins-escudo::after{content:"";position:absolute;inset:calc(var(--t)*.06);clip-path:inherit;border:0;
  background:radial-gradient(circle at 50% 35%,rgba(255,255,255,.35),transparent 60%);pointer-events:none}
.ins-brillo{position:absolute;inset:-40%;background:linear-gradient(115deg,transparent 40%,rgba(255,255,255,.55) 50%,transparent 60%);transform:translateX(-60%)}
.cc-ins:not(.bloqueada):hover .ins-brillo,.medalla-nueva .ins-brillo{animation:insBrillo 1.4s ease-in-out}
@keyframes insBrillo{to{transform:translateX(60%)}}
.ins-arte{position:relative;z-index:1;display:grid;place-items:center;margin-top:calc(var(--t)*-.04);filter:drop-shadow(0 3px 2px rgba(0,0,0,.25))}
.ins-arte svg{display:block}
.ins-arte.es-logo{width:calc(var(--t)*.62);height:calc(var(--t)*.62);border-radius:50%;background:rgba(255,255,255,.9);box-shadow:0 0 0 calc(var(--t)*.03) var(--bd)}
.ins-adorno{position:absolute;z-index:1;font:900 calc(var(--t)*.14) system-ui,sans-serif;color:#fff;opacity:.85;text-shadow:0 1px 2px rgba(0,0,0,.3)}
.ins-adorno.a1{top:18%;left:16%}.ins-adorno.a2{top:24%;right:14%;transform:scale(.8)}
.ins-cinta{position:absolute;z-index:2;bottom:calc(var(--t)*.02);left:50%;transform:translateX(-50%);padding:calc(var(--t)*.03) calc(var(--t)*.12);
  border-radius:calc(var(--t)*.06);background:var(--cinta);color:#fff;font:900 calc(var(--t)*.13) system-ui,sans-serif;text-transform:uppercase;letter-spacing:.04em;
  box-shadow:0 2px 0 var(--bd),0 3px 6px rgba(0,0,0,.25);white-space:nowrap}
.cc-ins.f-hexagono .ins-escudo{clip-path:polygon(50% 0,95% 25%,95% 75%,50% 100%,5% 75%,5% 25%)}
.cc-ins.f-octagono .ins-escudo{clip-path:polygon(30% 0,70% 0,100% 30%,100% 70%,70% 100%,30% 100%,0 70%,0 30%)}
.cc-ins.f-gota .ins-escudo{clip-path:none;border-radius:50% 50% 46% 46%/42% 42% 58% 58%}
.cc-ins.bloqueada .ins-escudo,.cc-ins.bloqueada .ins-cinta{filter:grayscale(1) brightness(1.1);opacity:.55}
.ins-candado{position:absolute;z-index:3;font-size:calc(var(--t)*.26);top:38%}
.medallas-vitrina{display:flex;flex-wrap:wrap;gap:10px 8px}
.medallas-vitrina .md-fig{margin:0;display:grid;justify-items:center;gap:2px;width:72px}
.medallas-vitrina figcaption{font:700 11px system-ui,sans-serif;color:var(--sub);text-transform:capitalize}
.medallas-vitrina .md-fig.ganada .cc-ins{filter:drop-shadow(0 4px 8px rgba(0,0,0,.25));transition:transform .2s}
.medallas-vitrina .md-fig.ganada:hover .cc-ins{transform:translateY(-3px) rotate(-4deg)}
.medallas-vacio{margin:0}
@media (prefers-reduced-motion:no-preference){.medalla-nueva .cc-ins{animation:medallaBrilla 1.6s ease-in-out infinite}}
@keyframes medallaBrilla{50%{filter:drop-shadow(0 0 14px #facc15) brightness(1.15);transform:scale(1.05)}}`;
export function estilosMedallas() {
  if (typeof document === "undefined" || document.getElementById("cc-medallas-css")) return;
  const s = document.createElement("style"); s.id = "cc-medallas-css"; s.textContent = CSS_MEDALLAS; document.head.appendChild(s);
}
