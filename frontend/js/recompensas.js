// Lógica de recompensas.html
import { iniciar, api, esc } from "/js/app.js";
import { iconoSVG } from "/js/iconos.js";
import { activarCofres, svgCofre } from "/js/cofres.js";
import { estilosMedallas, separarMedallas, svgMedalla, vitrinaMedallas } from "/js/medallas.js";
await iniciar("recompensas");
activarCofres().catch(() => {});
const $ = (id) => document.getElementById(id);
async function cargar() {
  const d = await api("/api/desafios/");
  const m = d.mes;
  pintarMedalla(d.medalla);
  $("mesTitulo").textContent = "Desafío de " + m.nombre;
  $("mesDias").textContent = `${m.dias_restantes} ${m.dias_restantes === 1 ? "DÍA" : "DÍAS"}`;
  $("mesBarra").style.width = (m.puntos / m.meta * 100) + "%";
  // Como Duolingo: la barra del mes se llena con los encargos que superas cada día
  const hechos = Math.round(m.puntos / 5), totalEnc = Math.round(m.meta / 5);
  $("mesTexto").textContent = `${hechos} / ${totalEnc} encargos`;
  if ($("mesMeta")) $("mesMeta").textContent = `Supera ${totalEnc} encargos este mes`;
  $("mesNota").textContent = m.completado ? `¡Desafío superado! Recibiste ${m.premio}.` : `Cada encargo de hoy que superes llena la barra del mes. Premio: ${m.premio}.`;
  $("horas").textContent = `${d.horas_restantes}H RESTANTES`;
  $("dailyCount").textContent = String(d.hoy.length).padStart(2, "0");
  $("rsHoy").textContent = `${d.hoy.filter((x) => x.completado).length}/${d.hoy.length}`;
  $("rsMes").textContent = `${Math.round(m.puntos / 5)}/${Math.round(m.meta / 5)}`;
  // Orden: los que están por cumplirse primero, los cumplidos al final.
  d.hoy.sort((a, b) => (a.completado - b.completado) || (b.progreso / b.meta - a.progreso / a.meta));
  $("hoy").innerHTML = d.hoy.map((x, i) => `<article class="d-item${x.completado ? " completado" : ""}">
    <div class="d-index">${String(i + 1).padStart(2, "0")}</div>
    <div class="d-icon">${x.completado ? '<span aria-hidden="true">✓</span>' : iconoSVG(x.clave, "d-icon-svg")}</div>
    <div class="d-content"><div class="d-title-row"><h3>${esc(x.titulo)}</h3><span>${x.completado ? "COMPLETADO" : "ENCARGO ACTIVO"}</span></div>
      <div class="d-progress-line"><div class="pbar" role="progressbar" aria-valuemin="0" aria-valuemax="${x.meta}" aria-valuenow="${x.progreso}" aria-label="Progreso: ${esc(x.titulo)}"><i style="width:${x.progreso / x.meta * 100}%"></i></div><small>${x.progreso} / ${x.meta}</small></div>
    </div><div class="d-reward d-cofre${x.completado ? " abierto" : x.progreso >= x.meta ? " listo" : ""}"><div class="cofre-mini">${svgCofre(x.cofre || "madera", { abierto: x.completado })}</div><b>${iconoSVG("diamante", "icono-moneda")} ${esc(x.premio)}</b><small>${x.completado ? "COFRE ABIERTO" : "COFRE"}</small></div></article>`).join("");
}
// ----- Medalla del mes y sus experiencias (como Duolingo)
function pintarMedalla(m) {
  if (!m) return;
  if (m.antes_de_inicio) {   // las medallas empiezan el 1 de diciembre de 2026: se muestra la primera que viene
    const p = m.proxima;
    $("mdArte").innerHTML = `<div class="medalla-por-ganar">${svgMedalla(p.numero, { anio: p.anio, tam: 96, ganada: true })}</div>`;
    $("t-medalla").textContent = `${p.nombre} · ${p.mes}`;
    $("mdSub").textContent = `¡Las medallas del mes empiezan el 1 de ${p.mes} de ${p.anio}! La primera es «${p.nombre}» (temporada: ${p.temporada}). Ese día aparecerán sus experiencias.`;
    $("mdExps").innerHTML = "";
    $("mdPremio").innerHTML = `Al ganarla: <b>${esc(reward(m.premio))}</b>`;
    $("mdXpMes").textContent = `${m.xp_mes} XP en ${m.mes}`;
    $("mdHitos").innerHTML = hitos(m.hitos_xp, m.xp_mes, "XP");
    $("encHitos").innerHTML = hitos(m.hitos_encargos, m.encargos_mes, "encargos");
    return;
  }
  // La del mes en curso se ve a todo color (como en Duolingo): es la que estás por ganar
  $("mdArte").innerHTML = `<div class="${m.ganada ? "medalla-nueva" : "medalla-por-ganar"}">${svgMedalla(m.numero, { anio: m.anio, tam: 96, ganada: true })}</div>`;
  $("t-medalla").textContent = `${m.nombre} · ${m.mes}`;
  $("mdSub").textContent = m.ganada ? `¡La ganaste! Ya está en tu perfil y la ven tus amigos. Temporada: ${m.temporada}.`
    : `Temporada: ${m.temporada}. Completa las ${m.experiencias.length} experiencias del mes para ganarla; quedará para siempre en tu perfil.`;
  $("mdExps").innerHTML = m.experiencias.map((e) => `<article class="md-exp${e.completada ? " hecha" : ""}">
    <span class="md-ico" aria-hidden="true">${e.completada ? "✓" : esc(e.icono)}</span>
    <div><h3>${esc(e.titulo)}</h3><div class="pbar" role="progressbar" aria-valuemin="0" aria-valuemax="${e.meta}" aria-valuenow="${e.progreso}" aria-label="${esc(e.titulo)}"><i style="width:${(e.progreso / e.meta) * 100}%"></i></div>
      <small>${e.progreso} / ${e.meta} · ${e.completada ? "¡Completada!" : `Premio: ${esc(e.premio_texto)}`}</small></div></article>`).join("");
  $("mdXpMes").textContent = `${m.xp_mes} XP en ${m.mes}`;
  $("mdHitos").innerHTML = hitos(m.hitos_xp, m.xp_mes, "XP");
  $("encHitos").innerHTML = hitos(m.hitos_encargos, m.encargos_mes, "encargos");
  const hechas = m.experiencias.filter((e) => e.completada).length;
  $("mdPremio").innerHTML = m.ganada ? "🏅 Medalla ganada" : `${hechas}/${m.experiencias.length} experiencias · Al ganar la medalla: <b>${esc(reward(m.premio))}</b>`;
}
/** Barra con cofres en cada tramo (XP o encargos del mes). */
function hitos(lista, valor, unidad) {
  const tope = lista[lista.length - 1].meta;
  return `<div class="md-hitos-barra"><i style="width:${Math.min(100, (valor / tope) * 100)}%"></i></div>` + lista.map((h) => `<div class="md-hito${h.completado ? " hecho" : ""}" style="left:${(h.meta / tope) * 100}%">
    <span class="cofre-mini">${svgCofre(h.cofre, { abierto: h.completado })}</span><b>${h.meta} ${unidad}</b><small>${esc(h.premio_texto)}</small></div>`).join("");
}
const reward = (p) => Object.entries(p).map(([k, v]) => `+${v} ${{ diamante: "diamantes", xp: "XP", vidas: "vidas", salvarrachas: "salvarrachas" }[k] || k}`).join(" · ");
async function cargarColeccion() {
  try {
    const { medallas, desde } = await api("/api/medallas/");
    const anio = new Date().getFullYear();
    $("mdAnio").textContent = anio;
    const otras = separarMedallas(medallas, anio, desde).otras;
    $("mdVitrina").innerHTML = vitrinaMedallas(medallas, { anio, tam: 58, desde })
      + (otras.length ? `<h3 style="margin:14px 0 6px;font-size:14px">Años anteriores</h3>${vitrinaMedallas(otras, { tam: 50 })}` : "");
  } catch { /* sin conexión */ }
}
estilosMedallas();
cargarColeccion();
document.addEventListener("cc-cofre-abierto", cargarColeccion);

cargar();
document.addEventListener("visibilitychange", () => { if (!document.hidden) cargar(); });
document.addEventListener("cc-cofre-abierto", () => cargar());


// Pestañas
const mostrarRc = (cual) => {
  document.querySelectorAll(".rc-tab").forEach((t) => { const on = t.dataset.rc === cual; t.classList.toggle("on", on); t.setAttribute("aria-selected", String(on)); });
  document.querySelectorAll(".rc-panel").forEach((p) => { p.hidden = p.dataset.panel !== cual; });
};
document.querySelector(".rc-tabs").onclick = (e) => { const t = e.target.closest("[data-rc]"); if (t) { mostrarRc(t.dataset.rc); history.replaceState(null, "", "#" + t.dataset.rc); } };
if (["hoy", "logros", "temporada"].includes(location.hash.slice(1))) mostrarRc(location.hash.slice(1));
