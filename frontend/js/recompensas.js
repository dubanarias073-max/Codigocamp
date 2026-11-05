// Lógica de recompensas.html
import { iniciar, api, esc } from "/js/app.js";
await iniciar("recompensas");
const $ = (id) => document.getElementById(id);
async function cargar() {
  const d = await api("/api/desafios/");
  const m = d.mes;
  $("mesTitulo").textContent = "Desafío de " + m.nombre;
  $("mesDias").textContent = `⏱ ${m.dias_restantes} ${m.dias_restantes === 1 ? "DÍA" : "DÍAS"}`;
  $("mesBarra").style.width = (m.puntos / m.meta * 100) + "%";
  $("mesTexto").textContent = `${m.puntos} / ${m.meta}`;
  $("mesNota").textContent = m.completado ? `¡Desafío superado! Recibiste 💎 ${m.premio}.` : `Cada desafío del día que superes suma 5 puntos. Premio: 💎 ${m.premio}.`;
  $("horas").textContent = `⏱ ${d.horas_restantes}H`;
  $("hoy").innerHTML = d.hoy.map((x, i) => `<article class="d-item${x.completado ? " completado" : ""}">
    <div class="d-index">${String(i + 1).padStart(2, "0")}</div>
    <div class="d-icon">${x.completado ? "✓" : x.icono}</div>
    <div class="d-content"><div class="d-title-row"><h3>${esc(x.titulo)}</h3><span>${x.completado ? "COMPLETADO" : "ENCARGO ACTIVO"}</span></div>
      <div class="d-progress-line"><div class="pbar"><i style="width:${x.progreso / x.meta * 100}%"></i></div><small>${x.progreso} / ${x.meta}</small></div>
    </div><div class="d-reward"><small>BOTÍN</small><b>💎 ${esc(x.premio)}</b></div></article>`).join("");
}
cargar();
document.addEventListener("visibilitychange", () => { if (!document.hidden) cargar(); });
