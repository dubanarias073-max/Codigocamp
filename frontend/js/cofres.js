// Los cofres de logro de Recompensas y la animación al abrirlos (temblor, tapa que se abre, rayos de luz y premios que saltan).
import { prepararSonido, sonar, vibrar } from "/js/sonidos.js";
import { api, esc, aviso, actualizarStats, aplicarCosmeticos } from "/js/app.js";
import { iconoSVG } from "/js/iconos.js";
import { vistaPrevia } from "/js/cosmeticos.js";

// Paleta de cada cofre: madera/caja, borde oscuro, bandas de metal, brillo de metal, cerradura, interior (luz al abrir)
const COLORES = {
  madera: { caja: ["#c2783a", "#8a4b1f", "#5c2f12"], bandas: ["#9aa4b2", "#5b6472"], brillo: "#e5e9ef", cerradura: ["#f6c445", "#b7791f"], luz: "#ffd36b", gema: null },
  plata: { caja: ["#e7edf5", "#a8b5c7", "#6b7a90"], bandas: ["#5b6b82", "#334155"], brillo: "#ffffff", cerradura: ["#e2e8f0", "#64748b"], luz: "#e0f2fe", gema: "#60a5fa" },
  oro: { caja: ["#b91c1c", "#7f1d1d", "#450a0a"], bandas: ["#fcd34d", "#b45309"], brillo: "#fff7d1", cerradura: ["#fde68a", "#d97706"], luz: "#ffe58a", gema: "#22c55e" },
  diamante: { caja: ["#a5f3fc", "#22d3ee", "#0e7490"], bandas: ["#e0f2fe", "#38bdf8"], brillo: "#ffffff", cerradura: ["#f0f9ff", "#0ea5e9"], luz: "#cffafe", gema: "#f0abfc" },
  legendario: { caja: ["#a855f7", "#6d28d9", "#3b0764"], bandas: ["#fde047", "#ca8a04"], brillo: "#fffbe6", cerradura: ["#fef08a", "#eab308"], luz: "#f5d0fe", gema: "#f43f5e" },
};
const NOMBRE_COFRE = { madera: "Cofre de madera", plata: "Cofre de plata", oro: "Cofre de oro", diamante: "Cofre de diamante", legendario: "Cofre legendario" };
let nCofre = 0;

/** Cofre ilustrado (madera con vetas, bandas de metal con remaches, cerradura, gemas y luz interior al abrirse). */
export function svgCofre(tipo, { abierto = false } = {}) {
  const k = COLORES[tipo] ? tipo : "madera";
  const C = COLORES[k];
  const id = `cf${++nCofre}`;
  const remaches = (y) => [22, 98].map((x) => `<circle cx="${x}" cy="${y}" r="2.1" fill="${C.bandas[1]}"/><circle cx="${x - .6}" cy="${y - .6}" r=".8" fill="${C.brillo}"/>`).join("");
  const vetas = k === "madera" ? `<g stroke="#5c2f12" stroke-opacity=".35" stroke-width="1.4" fill="none" stroke-linecap="round">
      <path d="M18 80h84M18 92h84"/><path d="M34 74q6 2 12 0M68 86q8 2 14 0M28 97q5 1.5 10 0M80 75q4 1.5 9 0"/></g>` : "";
  const gemas = C.gema ? `<g><path d="M60 26l5 5-5 6-5-6z" fill="${C.gema}" stroke="#1f2937" stroke-width="1.2"/><path d="M60 26l2.5 5H57.5z" fill="#fff" opacity=".55"/></g>` : "";
  const brillos = k === "legendario" || k === "diamante"
    ? `<g class="cofre-chispas" fill="${C.brillo}"><path d="M10 34l1.6 4 4 1.6-4 1.6-1.6 4-1.6-4-4-1.6 4-1.6z"/><path d="M108 22l1.3 3.2 3.2 1.3-3.2 1.3-1.3 3.2-1.3-3.2-3.2-1.3 3.2-1.3z"/><path d="M112 70l1 2.5 2.5 1-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1z"/></g>` : "";
  return `<svg class="cofre-svg cofre-${k}${abierto ? " abierto" : ""}" viewBox="0 0 120 110" aria-hidden="true">
    <defs>
      <linearGradient id="${id}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.caja[0]}"/><stop offset=".6" stop-color="${C.caja[1]}"/><stop offset="1" stop-color="${C.caja[2]}"/></linearGradient>
      <linearGradient id="${id}t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.caja[0]}"/><stop offset="1" stop-color="${C.caja[1]}"/></linearGradient>
      <linearGradient id="${id}b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.brillo}"/><stop offset=".35" stop-color="${C.bandas[0]}"/><stop offset="1" stop-color="${C.bandas[1]}"/></linearGradient>
      <linearGradient id="${id}k" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${C.cerradura[0]}"/><stop offset="1" stop-color="${C.cerradura[1]}"/></linearGradient>
      <radialGradient id="${id}l" cx=".5" cy=".9" r=".7"><stop offset="0" stop-color="${C.luz}" stop-opacity=".95"/><stop offset=".6" stop-color="${C.luz}" stop-opacity=".35"/><stop offset="1" stop-color="${C.luz}" stop-opacity="0"/></radialGradient>
    </defs>
    <ellipse cx="60" cy="104" rx="50" ry="5" fill="#000" opacity=".25"/>
    ${brillos}
    <g class="cofre-luz"><ellipse cx="60" cy="40" rx="52" ry="42" fill="url(#${id}l)"/>
      <g class="cofre-monedas"><circle cx="44" cy="52" r="6" fill="#fbbf24" stroke="#b45309" stroke-width="1.5"/><circle cx="60" cy="48" r="7" fill="#fde047" stroke="#ca8a04" stroke-width="1.5"/><circle cx="76" cy="52" r="6" fill="#fbbf24" stroke="#b45309" stroke-width="1.5"/>
        <path d="M58 44l2 4 4 .6-3 2.8.8 4-3.8-2-3.8 2 .8-4-3-2.8 4-.6z" fill="#fff" opacity=".6"/></g></g>
    <g class="cofre-cuerpo">
      <path d="M14 56h92v40a8 8 0 0 1-8 8H22a8 8 0 0 1-8-8z" fill="url(#${id}c)" stroke="#1f2937" stroke-width="3" stroke-linejoin="round"/>
      ${vetas}
      <path d="M17 59h86" stroke="#fff" stroke-opacity=".25" stroke-width="3" stroke-linecap="round"/>
      <rect x="14" y="56" width="16" height="48" fill="url(#${id}b)" stroke="#1f2937" stroke-width="2.4" rx="2"/>
      <rect x="90" y="56" width="16" height="48" fill="url(#${id}b)" stroke="#1f2937" stroke-width="2.4" rx="2"/>
      ${remaches(64)}${remaches(96)}
      <g><rect x="47" y="60" width="26" height="30" rx="6" fill="url(#${id}k)" stroke="#1f2937" stroke-width="2.6"/>
        <circle cx="60" cy="72" r="4" fill="#1f2937"/><path d="M58.4 74.5h3.2l1.2 8h-5.6z" fill="#1f2937"/><path d="M50 63h20" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-linecap="round"/></g>
    </g>
    <g class="cofre-tapa">
      <path d="M14 58V40c0-15 20-26 46-26s46 11 46 26v18z" fill="url(#${id}t)" stroke="#1f2937" stroke-width="3" stroke-linejoin="round"/>
      ${k === "madera" ? `<path d="M22 46q38-10 76 0M24 36q36-12 72 0" stroke="#5c2f12" stroke-opacity=".35" stroke-width="1.4" fill="none"/>` : ""}
      <path d="M14 40c0-15 20-26 46-26s46 11 46 26" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="3"/>
      <path d="M14 46h92v10H14z" fill="url(#${id}b)" stroke="#1f2937" stroke-width="2.4"/>
      <path d="M30 18.5V56M90 18.5V56" stroke="url(#${id}b)" stroke-width="12"/><path d="M24 20.5V56M36 16.5V56M84 16.5V56M96 20.5V56" stroke="#1f2937" stroke-width="1.6" opacity=".7"/>
      ${remaches(51)}
      <rect x="51" y="44" width="18" height="15" rx="4" fill="url(#${id}k)" stroke="#1f2937" stroke-width="2.4"/>
      ${gemas}
      <path d="M40 22q20-6 40 0" stroke="#fff" stroke-opacity=".45" stroke-width="2.5" stroke-linecap="round" fill="none"/>
    </g>
  </svg>`;
}

const textoPremio = (p) => [p.diamante && `${p.diamante} diamantes`, p.vidas && `${p.vidas} vidas`, p.salvarrachas && `${p.salvarrachas} salvarrachas`, ...(p.cosmeticos || []).map((c) => c.nombre)].filter(Boolean).join(" · ");

function tarjeta(c) {
  const pct = Math.round((c.progreso / c.meta) * 100);
  return `<article class="cofre-card cofre-${c.cofre}${c.abierto ? " abierto" : c.listo ? " listo" : ""}">
    <div class="cofre-arte">${svgCofre(c.cofre, { abierto: c.abierto })}</div>
    <h3>${esc(c.nombre)}</h3><p>${esc(c.texto)}</p>
    ${c.abierto ? `<p class="cofre-ok">✓ Abierto · ${esc(textoPremio(c.premio))}</p>`
      : `<div class="pbar"><i style="width:${pct}%"></i></div><small>${c.progreso} / ${c.meta}</small>
         ${c.listo ? `<button class="bj" type="button" data-abrir="${esc(c.clave)}">¡Abrir cofre!</button>` : `<small class="cofre-pista">Premio: ${esc(textoPremio(c.premio))}</small>`}`}
  </article>`;
}

export async function cargarCofres() {
  const { cofres } = await api("/api/cofres/");
  // Orden: listos para abrir, luego los más avanzados y al final los ya abiertos.
  const orden = [...cofres].sort((a, b) => (b.listo && !b.abierto) - (a.listo && !a.abierto) || a.abierto - b.abierto || (b.progreso / b.meta) - (a.progreso / a.meta));
  document.getElementById("cofres").innerHTML = orden.map(tarjeta).join("");
  const listos = cofres.filter((c) => c.listo && !c.abierto).length;
  const r = document.getElementById("rsListos"); if (r) r.textContent = String(listos);
  const b = document.getElementById("badgeLogros"); if (b) { b.hidden = !listos; b.textContent = String(listos); }
  document.getElementById("cofresCuenta").textContent = `${cofres.filter((c) => c.abierto).length}/${cofres.length}`;
  return cofres;
}

function confeti(n = 60) {
  const colores = ["#55d8ff", "#9d75ff", "#ffcb68", "#ff6e9c", "#72e0a3"];
  for (let i = 0; i < n; i++) {
    const s = document.createElement("span");
    s.className = "confeti";
    s.style.cssText = `--confeti-color:${colores[i % colores.length]};left:${Math.random() * 100}vw;animation-delay:${Math.random() * .6}s;--confeti-tamano:${5 + Math.random() * 9}px`;
    document.body.appendChild(s);
    setTimeout(() => s.remove(), 3000);
  }
}
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

/** Crea (si hace falta) la capa donde se abre un cofre: así también funciona dentro de una lección. */
function capa() {
  let fondo = document.getElementById("abrirFondo");
  if (!fondo) {
    fondo = document.createElement("div");
    fondo.className = "abrir-fondo"; fondo.id = "abrirFondo"; fondo.hidden = true;
    fondo.innerHTML = '<div class="abrir-caja" id="abrirCaja" role="dialog" aria-modal="true" aria-label="Abriendo cofre"></div>';
    document.body.appendChild(fondo);
    fondo.onclick = (e) => { if (e.target === fondo && fondo.querySelector("#cerrarCofre")) fondo.querySelector("#cerrarCofre").click(); };
    addEventListener("keydown", (e) => { if (e.key === "Escape" && !fondo.hidden && fondo.querySelector("#cerrarCofre")) fondo.querySelector("#cerrarCofre").click(); });
  }
  return { fondo, caja: fondo.querySelector("#abrirCaja") };
}

/**
 * Muestra un cofre que se abre al tocarlo (temblor, tapa, rayos, confeti y los premios saltando), como en Duolingo.
 * @param {{tipo:string, titulo?:string, subtitulo?:string, obtener:()=>Promise<object>}} o   obtener devuelve el premio
 * @returns {Promise<object|null>} el premio, cuando la persona cierra la ventana
 */
export function mostrarCofre({ tipo = "madera", titulo, subtitulo = "", obtener }) {
  const { fondo, caja } = capa();
  return new Promise((terminar) => {
    caja.innerHTML = `<p class="abrir-titulo">${esc(titulo || NOMBRE_COFRE[tipo] || "Cofre")}</p>${subtitulo ? `<p class="abrir-sub">${esc(subtitulo)}</p>` : ""}<div class="abrir-escena"><div class="rayos"></div>${svgCofre(tipo)}</div>
      <p class="abrir-pista">Toca el cofre para abrirlo</p><div class="premios" id="premios"></div><div class="abrir-btns" id="abrirBtns"></div>`;
    fondo.hidden = false;
    const escena = caja.querySelector(".abrir-escena");
    let tocado = false;
    const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const cerrar = (premio) => { fondo.hidden = true; terminar(premio); };
    const iniciar = async () => {
      if (tocado) return;
      tocado = true;
      prepararSonido();
      caja.querySelector(".abrir-pista").textContent = "…";
      let r;
      const pedido = Promise.resolve().then(obtener).then((x) => { r = x; }, (e) => { r = { error: e.message }; });
      if (!reducido) { escena.classList.add("temblar"); await espera(1100); }
      await pedido;
      if (r?.error) { cerrar(null); aviso(r.error, true); return; }
      escena.classList.remove("temblar");
      escena.classList.add("abrir");
      sonar("cofre"); vibrar([15, 30, 50]);
      caja.querySelector(".cofre-svg").classList.add("abierto");
      confeti();
      caja.querySelector(".abrir-pista").textContent = "¡Conseguiste!";
      const p = r.premio || r;
      const lista = [
        ...(p.diamante ? [`<div class="premio">${iconoSVG("diamante", "premio-ic")}<b>+${p.diamante}</b><small>diamantes</small></div>`] : []),
        ...(p.xp ? [`<div class="premio"><span class="premio-ic premio-xp">XP</span><b>+${p.xp}</b><small>XP</small></div>`] : []),
        ...(p.vidas ? [`<div class="premio">${iconoSVG("vidas", "premio-ic")}<b>+${p.vidas}</b><small>vidas</small></div>`] : []),
        ...(p.salvarrachas ? [`<div class="premio">${iconoSVG("racha", "premio-ic")}<b>+${p.salvarrachas}</b><small>salvarrachas</small></div>`] : []),
        ...(p.cosmeticos || []).map((x) => `<div class="premio premio-cos rareza-${x.rareza}"><div class="vista vista-${x.tipo}" data-prev="${esc(x.clave)}" data-tipo="${x.tipo}"></div><b>${esc(x.nombre)}</b><small>exclusivo · ${esc(x.tipo)}</small></div>`),
      ];
      const cont = caja.querySelector("#premios");
      for (const [i, h] of lista.entries()) {
        await espera(reducido ? 0 : 280);
        cont.insertAdjacentHTML("beforeend", h);
        const el = cont.lastElementChild;
        sonar(/rareza-(legendario|epico)/.test(h) ? "legendario" : "premio");
        el.style.animationDelay = `${i * 40}ms`;
        const prev = el.querySelector("[data-prev]");
        if (prev) vistaPrevia(prev, prev.dataset.prev, prev.dataset.tipo);
      }
      const cos = p.cosmeticos?.[0];
      caja.querySelector("#abrirBtns").innerHTML = `${cos ? `<button class="bj" type="button" id="ponerYa">Ponerme «${esc(cos.nombre)}»</button>` : ""}<button class="bj gris" type="button" id="cerrarCofre">¡Genial!</button>`;
      caja.querySelector("#cerrarCofre").onclick = () => cerrar(p);
      caja.querySelector("#cerrarCofre").focus();
      if (cos) caja.querySelector("#ponerYa").onclick = async () => {
        try { const e = await api("/api/cosmeticos/equipar/", { tipo: cos.tipo, clave: cos.clave }); aplicarCosmeticos(e.equipados); aviso("¡Puesto!"); } catch (x) { aviso(x.message, true); }
        cerrar(p);
      };
      if (r.perfil) actualizarStats(r);
    };
    escena.onclick = iniciar;
    escena.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") iniciar(); };
    escena.tabIndex = 0;
    escena.focus();
  });
}

/** Abre un cofre de logro (los 10 de Recompensas) pidiéndoselo al servidor. */
export function abrirCofreLogro(c) {
  return mostrarCofre({ tipo: c.cofre, titulo: NOMBRE_COFRE[c.cofre], subtitulo: `${c.nombre} · ${c.texto}`, obtener: () => api("/api/cofres/abrir/", { clave: c.clave }) });
}

/**
 * Tras una lección o un reto: abre ahí mismo los cofres de los encargos que se acaban de cumplir (su premio ya se
 * acreditó) y los cofres de logro que quedaron listos. Devuelve cuántos se abrieron.
 */
export async function abrirPremiosNuevos(desafios = []) {
  let n = 0;
  for (const d of desafios) {
    await mostrarCofre({ tipo: d.cofre || "madera", titulo: d.encabezado || "¡Encargo cumplido!", subtitulo: d.titulo, obtener: async () => d.datos || {} });
    n += 1;
  }
  try {
    const { cofres } = await api("/api/cofres/");
    for (const c of cofres.filter((x) => x.listo && !x.abierto)) { await abrirCofreLogro(c); n += 1; }
  } catch { /* sin conexión: se abren luego en Recompensas */ }
  return n;
}

export function activarCofres() {
  let cofres = [];
  const recargar = async () => { cofres = await cargarCofres(); };
  document.getElementById("cofres").onclick = async (e) => {
    const b = e.target.closest("[data-abrir]");
    if (!b) return;
    const c = cofres.find((x) => x.clave === b.dataset.abrir);
    if (c) { await abrirCofreLogro(c); await recargar(); document.dispatchEvent(new CustomEvent("cc-cofre-abierto")); }
  };
  capa();
  return recargar();
}
