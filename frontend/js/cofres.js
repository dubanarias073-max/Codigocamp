// Los 10 cofres de Recompensas y la animación al abrirlos (temblor, tapa que se abre, rayos de luz y premios que saltan).
import { api, esc, aviso, actualizarStats, aplicarCosmeticos } from "/js/app.js";
import { iconoSVG } from "/js/iconos.js";
import { vistaPrevia } from "/js/cosmeticos.js";

const COLORES = {
  madera: ["#a16207", "#713f12", "#facc15"], plata: ["#cbd5e1", "#64748b", "#e2e8f0"], oro: ["#fbbf24", "#b45309", "#fef3c7"],
  diamante: ["#67e8f9", "#0e7490", "#ecfeff"], legendario: ["#c084fc", "#6b21a8", "#fde047"],
};
const NOMBRE_COFRE = { madera: "Cofre de madera", plata: "Cofre de plata", oro: "Cofre de oro", diamante: "Cofre de diamante", legendario: "Cofre legendario" };

export function svgCofre(tipo, { abierto = false } = {}) {
  const [c, o, b] = COLORES[tipo] || COLORES.madera;
  return `<svg class="cofre-svg${abierto ? " abierto" : ""}" viewBox="0 0 120 110" aria-hidden="true">
    <defs><linearGradient id="g-${tipo}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c}"/><stop offset="1" stop-color="${o}"/></linearGradient></defs>
    <g class="cofre-cuerpo"><rect x="14" y="52" width="92" height="50" rx="8" fill="url(#g-${tipo})" stroke="#1f2937" stroke-width="3"/>
      <rect x="14" y="66" width="92" height="7" fill="${b}" opacity=".55"/><rect x="50" y="58" width="20" height="24" rx="4" fill="${b}" stroke="#1f2937" stroke-width="3"/><circle cx="60" cy="70" r="3" fill="#1f2937"/></g>
    <g class="cofre-tapa"><path d="M14 54 V40 a46 26 0 0 1 92 0 V54z" fill="url(#g-${tipo})" stroke="#1f2937" stroke-width="3" stroke-linejoin="round"/>
      <path d="M22 44 a38 20 0 0 1 76 0" fill="none" stroke="${b}" stroke-width="4" opacity=".6"/><rect x="50" y="40" width="20" height="14" rx="3" fill="${b}" stroke="#1f2937" stroke-width="3"/></g>
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
  document.getElementById("cofresCuenta").textContent = `${cofres.filter((c) => c.abierto).length}/10`;
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
      caja.querySelector(".abrir-pista").textContent = "…";
      let r;
      const pedido = Promise.resolve().then(obtener).then((x) => { r = x; }, (e) => { r = { error: e.message }; });
      if (!reducido) { escena.classList.add("temblar"); await espera(1100); }
      await pedido;
      if (r?.error) { cerrar(null); aviso(r.error, true); return; }
      escena.classList.remove("temblar");
      escena.classList.add("abrir");
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
    await mostrarCofre({ tipo: d.cofre || "madera", titulo: "¡Encargo cumplido!", subtitulo: d.titulo, obtener: async () => d.datos || {} });
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
