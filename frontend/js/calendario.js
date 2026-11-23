// Calendario de racha (como el de Duolingo): días practicados del mes, racha actual, mejor racha y salvarrachas.
// montarCalendario(elemento) dibuja todo dentro de ese elemento. Se usa en Perfil.
import { api } from "/js/app.js";

const desplazar = (f, dd) => { const t = new Date(f + "T12:00:00"); t.setDate(t.getDate() + dd); return t.toISOString().slice(0, 10); };

export function montarCalendario(raiz) {
  raiz.innerHTML = `<div class="d-cab"><div><p class="misiones-kicker">RACHA</p><h2>Calendario de racha</h2></div>
    <div class="cal-nav"><button type="button" class="mini-btn" data-cal="-1" aria-label="Mes anterior">‹</button><b data-cal-mes></b><button type="button" class="mini-btn" data-cal="1" aria-label="Mes siguiente">›</button></div></div>
    <div class="cal-resumen" data-cal-resumen></div><div class="cal" data-cal-dias role="grid" aria-label="Días practicados"></div>
    <p class="cal-leyenda"><span class="cal-muestra"></span> Practicaste · <span class="cal-muestra hoy"></span> Hoy</p>`;
  const $ = (s) => raiz.querySelector(s);
  const mes = new Date(); mes.setDate(1);
  async function pintar() {
    const clave = `${mes.getFullYear()}-${String(mes.getMonth() + 1).padStart(2, "0")}`;
    let d;
    try { d = await api(`/api/racha/calendario/?mes=${clave}`); } catch { $("[data-cal-dias]").innerHTML = '<p class="nota">No se pudo cargar el calendario.</p>'; return; }
    const nombre = mes.toLocaleDateString("es", { month: "long", year: "numeric" });
    $("[data-cal-mes]").textContent = nombre.charAt(0).toUpperCase() + nombre.slice(1);
    raiz.querySelector('[data-cal="1"]').disabled = d.es_mes_actual;
    $("[data-cal-resumen]").innerHTML = `<div class="cal-dato fuego"><b>${d.racha_actual}</b><small>racha actual</small></div><div class="cal-dato"><b>${d.racha_maxima}</b><small>mejor racha</small></div><div class="cal-dato"><b>${d.dias_mes}</b><small>días este mes</small></div><div class="cal-dato hielo"><b>${d.salvarrachas}</b><small>salvarrachas</small></div>`;
    const dias = new Map(d.dias.map((x) => [x.fecha, x]));
    const total = new Date(mes.getFullYear(), mes.getMonth() + 1, 0).getDate();
    const hueco = (mes.getDay() + 6) % 7;   // la semana empieza el lunes
    let html = ["L", "M", "M", "J", "V", "S", "D"].map((x) => `<span class="cal-cab">${x}</span>`).join("") + "<span></span>".repeat(hueco);
    for (let n = 1; n <= total; n += 1) {
      const f = `${clave}-${String(n).padStart(2, "0")}`;
      const x = dias.get(f);
      const cls = ["cal-dia", x ? "hecho" : "", x?.en_racha ? "racha" : "", f === d.hoy ? "hoy" : "", f > d.hoy ? "futuro" : "",
        x && dias.has(desplazar(f, -1)) && (hueco + n - 1) % 7 ? "une-izq" : "", x && dias.has(desplazar(f, 1)) && (hueco + n) % 7 ? "une-der" : ""].filter(Boolean).join(" ");
      html += `<span class="${cls}" role="gridcell" title="${f}${x ? ` · ${x.xp} XP · ${x.niveles} nivel${x.niveles === 1 ? "" : "es"}` : f < d.hoy ? " · sin práctica" : ""}">${x ? '<i aria-hidden="true">🔥</i>' : ""}<b>${n}</b></span>`;
    }
    $("[data-cal-dias]").innerHTML = html;
  }
  raiz.addEventListener("click", (e) => { const b = e.target.closest("[data-cal]"); if (b) { mes.setMonth(mes.getMonth() + Number(b.dataset.cal)); pintar(); } });
  pintar();
  return { recargar: pintar };
}
