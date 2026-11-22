// Decoración de temporada automática (Navidad, Halloween, Amor y amistad, Día del programador, vacaciones…).
// No toca nada del usuario: sus cosméticos siguen puestos. Los colores de temporada solo se usan si no tiene un tema
// de color puesto, y Codi solo se pone el accesorio de temporada si no lleva otro. Se apaga en Configuración.
import { ponerAccesorioTemporada } from "/js/codi.js";

const md = (m, d) => m * 100 + d;
/** Temporadas por fecha (mes/día del dispositivo). La primera que coincida gana. */
export const TEMPORADAS = [
  { id: "anio_nuevo", nombre: "¡Feliz año nuevo!", icono: "🎆", desde: md(12, 31), hasta: md(1, 1),
    colores: { acc: "#facc15", acc2: "#7c3aed", cy: "#22d3ee" }, particulas: ["✦", "✧", "★", "✺"], tonos: ["#facc15", "#f472b6", "#22d3ee", "#a3e635"],
    guirnalda: "luces", accesorio: "codi_corona" },
  { id: "navidad", nombre: "¡Feliz Navidad!", icono: "🎄", desde: md(12, 1), hasta: md(1, 6),
    colores: { acc: "#ef4444", acc2: "#15803d", cy: "#fde047" }, particulas: ["❄", "❅", "❆", "•"], tonos: ["#ffffff", "#bae6fd", "#93c5fd"],
    guirnalda: "luces", accesorio: "codi_navidad" },
  { id: "san_valentin", nombre: "Semana del amor", icono: "💘", desde: md(2, 10), hasta: md(2, 14),
    colores: { acc: "#f472b6", acc2: "#be185d", cy: "#fda4af" }, particulas: ["♥", "♡", "❤"], tonos: ["#f472b6", "#fb7185", "#fda4af"],
    guirnalda: "banderines", accesorio: "codi_flor" },
  { id: "vacaciones", nombre: "¡Vacaciones de mitad de año!", icono: "🌴", desde: md(6, 15), hasta: md(7, 15),
    colores: { acc: "#fbbf24", acc2: "#0891b2", cy: "#5eead4" }, particulas: ["○", "◦", "·"], tonos: ["#bae6fd", "#ffffff", "#5eead4"], subir: true,
    guirnalda: "banderines", accesorio: "codi_gafas" },
  { id: "programador", nombre: "¡Feliz día del programador!", icono: "💻", desde: md(9, 13), hasta: md(9, 13),
    colores: { acc: "#a3e635", acc2: "#166534", cy: "#22d3ee" }, particulas: ["</>", "{ }", "01", ";", "#"], tonos: ["#a3e635", "#22d3ee", "#facc15"],
    guirnalda: "banderines", accesorio: "codi_gafas" },
  { id: "amor_amistad", nombre: "Mes del amor y la amistad", icono: "💛", desde: md(9, 1), hasta: md(9, 21),
    colores: { acc: "#fb7185", acc2: "#9f1239", cy: "#fcd34d" }, particulas: ["♥", "♡", "✿"], tonos: ["#fb7185", "#fcd34d", "#f9a8d4"],
    guirnalda: "banderines", accesorio: "codi_flor" },
  { id: "halloween", nombre: "¡Halloween!", icono: "🎃", desde: md(10, 15), hasta: md(10, 31),
    colores: { acc: "#f97316", acc2: "#581c87", cy: "#a3e635" }, particulas: ["🦇", "🕸", "✦"], tonos: ["#f97316", "#a855f7", "#e2e8f0"],
    guirnalda: "banderines", accesorio: "temp_bruja" },
];

/** La temporada de una fecha (o null). Para probar: ?temporada=navidad o localStorage cc_temporada_forzar. */
export function temporadaDe(fecha = new Date()) {
  let forzada = null;
  try { forzada = new URLSearchParams(location.search).get("temporada") || localStorage.getItem("cc_temporada_forzar"); } catch { /* sin navegador */ }
  if (forzada) return TEMPORADAS.find((t) => t.id === forzada) || null;
  const hoy = md(fecha.getMonth() + 1, fecha.getDate());
  return TEMPORADAS.find((t) => (t.desde <= t.hasta ? hoy >= t.desde && hoy <= t.hasta : hoy >= t.desde || hoy <= t.hasta)) || null;
}

export const temporadaActiva = () => { try { return localStorage.getItem("cc_temporada") !== "off"; } catch { return true; } };
export function activarTemporada(si) { try { localStorage.setItem("cc_temporada", si ? "on" : "off"); } catch { /* nada */ } aplicarTemporada(); }

function quitar() {
  document.getElementById("cc-temporada")?.remove();
  document.getElementById("cc-temp-estilo")?.remove();
  document.getElementById("cc-temp-chip")?.remove();
  delete document.documentElement.dataset.temporada;
  ponerAccesorioTemporada(null);
}

/** Pone (o quita) la decoración de la temporada actual. Se puede llamar las veces que sea. */
export function aplicarTemporada() {
  if (typeof document === "undefined") return null;
  quitar();
  const t = temporadaActiva() ? temporadaDe() : null;
  if (!t) return null;
  const html = document.documentElement;
  html.dataset.temporada = t.id;
  let cosm = {};
  try { cosm = JSON.parse(localStorage.getItem("cc_cosm") || "{}"); } catch { /* nada */ }
  const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const c = t.colores;
  const bombillas = t.guirnalda === "luces"
    ? `repeating-linear-gradient(90deg,transparent 0 14px,${c.acc} 14px 22px,transparent 22px 44px,${c.cy} 44px 52px,transparent 52px 74px,${c.acc2} 74px 82px,transparent 82px 96px)`
    : `repeating-linear-gradient(90deg,${c.acc} 0 22px,${c.cy} 22px 44px,${c.acc2} 44px 66px)`;
  const estilo = document.createElement("style");
  estilo.id = "cc-temp-estilo";
  estilo.textContent = `
${cosm.tema ? "" : `:root,:root body,:root[data-tema] body{--acc:${c.acc}!important;--acc2:${c.acc2}!important;--cy:${c.cy}!important}`}
${cosm.fondo ? "" : `html:not(.cc-con-fondo) body{background-image:radial-gradient(60% 40% at 0 0,color-mix(in srgb,${c.acc} 16%,transparent),transparent 70%),radial-gradient(50% 40% at 100% 0,color-mix(in srgb,${c.acc2} 14%,transparent),transparent 70%),radial-gradient(70% 45% at 50% 100%,color-mix(in srgb,${c.cy} 12%,transparent),transparent 70%)!important;background-attachment:fixed}`}
.logo-app+.cc-temp-chip{margin:-4px 0 12px 10px;align-self:flex-start}
#cc-temporada{position:fixed;inset:0;z-index:9990;pointer-events:none;overflow:hidden}
#cc-temporada .cc-guirnalda{position:absolute;left:0;right:0;top:0;height:12px;background:${bombillas};
  ${t.guirnalda === "luces" ? `-webkit-mask:radial-gradient(circle at 50% 45%,#000 4px,transparent 4.5px) 0 0/30px 12px;mask:radial-gradient(circle at 50% 45%,#000 4px,transparent 4.5px) 0 0/30px 12px;filter:drop-shadow(0 0 4px ${c.acc})${reducido ? "" : ";animation:cc-titila 1.6s steps(2) infinite"}`
    : `-webkit-mask:conic-gradient(from 135deg at 50% 0,#000 90deg,transparent 0) 0 0/22px 12px;mask:conic-gradient(from 135deg at 50% 0,#000 90deg,transparent 0) 0 0/22px 12px;opacity:.9`}}
#cc-temporada .cc-guirnalda::before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:color-mix(in srgb,${c.acc2} 70%,#000)}
#cc-temporada i{position:absolute;top:-30px;font-style:normal;font-weight:800;opacity:.8;text-shadow:0 0 6px currentColor,0 0 2px rgba(15,23,42,.45);animation:cc-cae linear infinite}
#cc-temporada i.sube{top:auto;bottom:-30px;animation-name:cc-sube}
@keyframes cc-cae{to{transform:translate(var(--dx),110vh) rotate(var(--giro))}}
@keyframes cc-sube{to{transform:translate(var(--dx),-110vh)}}
@keyframes cc-titila{50%{filter:drop-shadow(0 0 7px ${c.cy}) brightness(1.4)}}
.cc-temp-chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:800;color:var(--txt);
  background:color-mix(in srgb,${c.acc} 22%,transparent);border:1px solid color-mix(in srgb,${c.acc} 55%,transparent);white-space:nowrap}
@media (max-width:700px){.cc-temp-chip span{display:none}}
${reducido ? "#cc-temporada i{display:none}" : ""}`;
  document.head.appendChild(estilo);
  const capa = document.createElement("div");
  capa.id = "cc-temporada";
  capa.setAttribute("aria-hidden", "true");
  const n = innerWidth < 700 ? 12 : 22;
  let piezas = "";
  for (let i = 0; i < n; i++) {
    const ch = t.particulas[i % t.particulas.length], col = t.tonos[i % t.tonos.length];
    const tam = 10 + Math.random() * 14, dur = 9 + Math.random() * 12, ret = -Math.random() * dur;
    piezas += `<i class="${t.subir ? "sube" : ""}" style="left:${Math.random() * 100}%;color:${col};font-size:${tam}px;animation-duration:${dur}s;animation-delay:${ret}s;--dx:${(Math.random() - .5) * 120}px;--giro:${Math.round((Math.random() - .5) * 360)}deg">${ch}</i>`;
  }
  capa.innerHTML = `<div class="cc-guirnalda"></div>${piezas}`;
  document.body.appendChild(capa);
  if (!cosm.codi && t.accesorio) ponerAccesorioTemporada(t.accesorio);
  const ponerChip = () => {
    if (document.getElementById("cc-temp-chip")) return true;
    // En el computador va debajo del logo; en el celular (donde se ve la barra de arriba), en la barra
    const tope = document.querySelector(".tope");
    const visible = tope && getComputedStyle(tope).display !== "none";
    const logo = document.querySelector(".logo-app");
    const chip = `<span class="cc-temp-chip" id="cc-temp-chip" title="Decoración de temporada (se quita en Configuración)">${t.icono}<span>${t.nombre}</span></span>`;
    if (visible) tope.insertAdjacentHTML("beforeend", chip);
    else if (logo && logo.offsetWidth > 120) logo.insertAdjacentHTML("afterend", chip);
    else return false;
    return true;
  };
  if (!ponerChip()) setTimeout(ponerChip, 1500);
  return t;
}
