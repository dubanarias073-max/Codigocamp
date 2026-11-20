// Lógica de recompensas.html
import { iniciar, api, esc } from "/js/app.js";
import { iconoSVG } from "/js/iconos.js";
import { activarCofres, svgCofre } from "/js/cofres.js";
await iniciar("recompensas");
activarCofres().catch(() => {});
const $ = (id) => document.getElementById(id);
async function cargar() {
  const d = await api("/api/desafios/");
  const m = d.mes;
  $("mesTitulo").textContent = "Desafío de " + m.nombre;
  $("mesDias").textContent = `${m.dias_restantes} ${m.dias_restantes === 1 ? "DÍA" : "DÍAS"}`;
  $("mesBarra").style.width = (m.puntos / m.meta * 100) + "%";
  $("mesTexto").textContent = `${m.puntos} / ${m.meta}`;
  $("mesNota").textContent = m.completado ? `¡Desafío superado! Recibiste ${m.premio}.` : `Cada desafío del día que superes suma 5 puntos. Premio: ${m.premio}.`;
  $("horas").textContent = `${d.horas_restantes}H RESTANTES`;
  $("dailyCount").textContent = String(d.hoy.length).padStart(2, "0");
  $("rsHoy").textContent = `${d.hoy.filter((x) => x.completado).length}/${d.hoy.length}`;
  $("rsMes").textContent = `${m.puntos}/${m.meta}`;
  // Orden: los que están por cumplirse primero, los cumplidos al final.
  d.hoy.sort((a, b) => (a.completado - b.completado) || (b.progreso / b.meta - a.progreso / a.meta));
  $("hoy").innerHTML = d.hoy.map((x, i) => `<article class="d-item${x.completado ? " completado" : ""}">
    <div class="d-index">${String(i + 1).padStart(2, "0")}</div>
    <div class="d-icon">${x.completado ? '<span aria-hidden="true">✓</span>' : iconoSVG(x.clave, "d-icon-svg")}</div>
    <div class="d-content"><div class="d-title-row"><h3>${esc(x.titulo)}</h3><span>${x.completado ? "COMPLETADO" : "ENCARGO ACTIVO"}</span></div>
      <div class="d-progress-line"><div class="pbar" role="progressbar" aria-valuemin="0" aria-valuemax="${x.meta}" aria-valuenow="${x.progreso}" aria-label="Progreso: ${esc(x.titulo)}"><i style="width:${x.progreso / x.meta * 100}%"></i></div><small>${x.progreso} / ${x.meta}</small></div>
    </div><div class="d-reward d-cofre${x.completado ? " abierto" : x.progreso >= x.meta ? " listo" : ""}"><div class="cofre-mini">${svgCofre(x.cofre || "madera", { abierto: x.completado })}</div><b>${iconoSVG("diamante", "icono-moneda")} ${esc(x.premio)}</b><small>${x.completado ? "COFRE ABIERTO" : "COFRE"}</small></div></article>`).join("");
}
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
