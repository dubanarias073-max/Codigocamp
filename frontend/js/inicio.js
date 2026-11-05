// Lógica de inicio.html: camino por etapas y secciones, cabecera fija, selector de curso y pantalla de etapas
import { iniciar, api, esc, aviso, elegirCurso } from "/js/app.js";
import { logo } from "/js/logos.js";
import { pintarSeccion } from "/js/camino.js";

const { prog } = await iniciar("inicio");
const $ = (id) => document.getElementById(id);
const cont = $("camino"), banner = $("banner"), cabecera = $("cabecera");
const cursos = (await api("/api/cursos/")).cursos;
let actual = new URLSearchParams(location.search).get("curso") || prog.curso_actual?.slug || "python";
if (!cursos.some((c) => c.slug === actual)) actual = cursos[0].slug;
let ruta = null, secciones = [];

const infoCurso = (slug = actual) => cursos.find((c) => c.slug === slug);
// El curso que ves es el curso guardado: Inicio y Aprende comparten la misma elección.
const marcarTarjeta = (slug) => {
  const nombre = infoCurso(slug)?.nombre || "";
  [...document.querySelectorAll("#der .tarjeta")].find((t) => t.querySelector("h3")?.textContent === "Tu curso")?.querySelector("p")?.replaceChildren(nombre);
};
if (actual !== prog.curso_actual?.slug) { elegirCurso(actual).catch(() => {}); marcarTarjeta(actual); }

// Color de texto con mejor contraste sobre el color del curso
const tinta = (hex) => {
  const n = parseInt(hex.replace("#", ""), 16);
  const [r, g, b] = [n >> 16, (n >> 8) & 255, n & 255].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });
  const L = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return 1.05 / (L + 0.05) > (L + 0.05) / 0.056 ? "#ffffff" : "#0b1020";
};

/* ---------- cabecera: curso actual y progreso ---------- */
function pintarCabecera() {
  const c = infoCurso();
  $("cursoLogo").innerHTML = logo(actual, 36);
  $("cursoNombre").textContent = c?.nombre || "";
  document.title = `${c?.nombre || "Inicio"} · CódigoCamp`;
}

/* ---------- camino ---------- */
async function cargar() {
  pintarCabecera();
  const info = infoCurso();
  try {
    ruta = await api("/api/ruta/?curso=" + actual);
    if (!ruta.etapas.length) throw new Error("vacio");
    const color = ruta.curso.color;
    let n = 0;   // número de sección seguido a lo largo de todo el curso
    cont.innerHTML = ruta.etapas.map((e) => `<div class="etapa-div" id="etapa-${e.orden}" style="--c:${color}"><div>
        <small>ETAPA ${e.orden} DE ${ruta.etapas.length}</small><b>${esc(e.titulo)}</b><em>${esc(e.descripcion)}</em></div></div>`
      + e.secciones.map((s) => { n++; return `<div class="seccion" data-etapa="${e.orden}" data-num="${n}" data-titulo="${esc(s.titulo)}">
        <h3 class="seccion-tit"><small>SECCIÓN ${n}</small>${esc(s.titulo)}</h3>${pintarSeccion(actual, s, n, color)}</div>`; }).join("")).join("");
    banner.style.setProperty("--ban", color);
    banner.style.setProperty("--ban-ink", tinta(color));
    banner.hidden = false;
    secciones = [...cont.querySelectorAll(".seccion")];
    const lecs = ruta.etapas.flatMap((e) => e.secciones.flatMap((s) => s.niveles)).filter((x) => x.tipo === "leccion");
    $("topProg").textContent = `${lecs.filter((x) => x.estado === "hecho").length}/${lecs.length} lecciones`;
    document.querySelector(".cl.actual")?.scrollIntoView({ block: "center" });
    sincronizarBanner();
  } catch {
    banner.hidden = true; secciones = []; $("topProg").textContent = "";
    cont.innerHTML = `<div class="vacio"><p style="font-size:48px;margin:0">🚧</p><h2>Los retos de ${esc(info?.nombre || "este curso")} llegan pronto</h2>
      <p>Mientras tanto, estudia sus lecciones o prueba otro curso.</p>
      <a class="bj" href="/pages/aprende.html#${actual}">Ir a las lecciones</a></div>`;
  }
}

// El banner de arriba siempre dice en qué etapa y sección vas viendo
function sincronizarBanner() {
  if (!secciones.length) return;
  // activa = la última sección cuyo inicio ya llegó cerca de la cabecera (o la última si estás al final)
  const limite = cabecera.getBoundingClientRect().bottom + 40;
  let act = secciones[0];
  for (const s of secciones) {
    const previo = s.previousElementSibling;   // el separador "ETAPA n" cuenta como inicio de su primera sección
    const ref = previo?.classList.contains("etapa-div") ? previo : s;
    if (ref.getBoundingClientRect().top <= limite) act = s; else break;
  }
  if (innerHeight + scrollY >= document.documentElement.scrollHeight - 4) act = secciones[secciones.length - 1];
  $("banEtapa").textContent = `ETAPA ${act.dataset.etapa}, SECCIÓN ${act.dataset.num}`;
  $("banTitulo").textContent = act.dataset.titulo;
}
let esperando = false;
addEventListener("scroll", () => { if (!esperando) { esperando = true; requestAnimationFrame(() => { esperando = false; sincronizarBanner(); }); } }, { passive: true });
addEventListener("resize", sincronizarBanner);

/* ---------- panel de cursos ---------- */
const panel = $("panelCursos"), panelCont = $("panelCont"), selector = $("cursoSel");
function pintarPanel() {
  const info = infoCurso();
  const mis = cursos.filter((c) => c.slug === actual || (c.hechas || 0) > 0);
  const nuevos = cursos.filter((c) => !mis.includes(c));
  const ficha = (c) => `<button type="button" class="curso-tile${c.slug === actual ? " on" : ""}" data-slug="${c.slug}" style="--c:${c.color}" aria-pressed="${c.slug === actual}">${logo(c.slug, 56)}<span>${esc(c.nombre)}</span></button>`;
  const hechas = info.hechas || 0, total = info.lecciones || 0, pct = total ? Math.round(hechas / total * 100) : 0;
  panelCont.innerHTML = `<h3>Mis cursos</h3><div class="tiles">${mis.map(ficha).join("")}</div>
    <div class="card-avance"><div class="av-fila"><b>${hechas}</b><div class="pbar-g"><i style="width:${pct}%"></i></div><b>${total}</b></div>
      <p>Tu avance en ${esc(info.nombre)}: ${hechas} de ${total} lecciones</p>
      <button type="button" class="link-etapas" id="panelEtapas">VER ETAPAS</button></div>
    ${nuevos.length ? `<h3>Nuevos cursos</h3><div class="tiles">${nuevos.map(ficha).join("")}</div>` : ""}`;
}
function abrirPanel() { pintarPanel(); panel.hidden = false; selector.setAttribute("aria-expanded", "true"); panelCont.querySelector(".curso-tile.on")?.focus(); }
function cerrarPanel() { if (panel.hidden) return; panel.hidden = true; selector.setAttribute("aria-expanded", "false"); selector.focus(); }
selector.onclick = () => (panel.hidden ? abrirPanel() : cerrarPanel());
panel.onclick = async (e) => {
  if (e.target === panel) return cerrarPanel();
  if (e.target.closest("#panelEtapas")) { cerrarPanel(); return abrirEtapas(); }
  const b = e.target.closest("[data-slug]");
  if (!b) return;
  if (b.dataset.slug !== actual) {
    actual = b.dataset.slug;
    history.replaceState(null, "", "?curso=" + actual);
    marcarTarjeta(actual);
    try { await elegirCurso(actual); } catch (x) { aviso(x.message, true); }
    await cargar();
    scrollTo({ top: 0 });
    document.querySelector(".cl.actual")?.scrollIntoView({ block: "center" });
  }
  cerrarPanel();
};

/* ---------- pantalla de etapas ---------- */
const pantalla = $("pantallaEtapas");
function pintarEtapas() {
  if (!ruta) return;
  $("etapasTit").textContent = `Curso de ${ruta.curso.nombre}`;
  $("etapasLista").innerHTML = ruta.etapas.map((e) => {
    const nodos = e.secciones.flatMap((s) => s.niveles);
    const hechos = nodos.filter((x) => x.estado === "hecho").length, pct = nodos.length ? Math.round(hechos / nodos.length * 100) : 0;
    const esta = nodos.some((x) => x.estado === "actual");
    const lecs = nodos.filter((x) => x.tipo === "leccion").length;
    return `<button type="button" class="et-card${esta ? " actual" : ""}" data-etapa="${e.orden}" style="--c:${ruta.curso.color}">
      <div class="et-fila"><b>Etapa ${e.orden}</b><span class="et-chip">${esc(e.titulo)}</span></div>
      <div class="et-barra" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}"><i style="width:${pct}%"></i></div>
      <p class="et-nota">${e.secciones.length} secciones · ${lecs} lecciones · ${pct}% completado</p></button>`;
  }).join("");
}
function abrirEtapas() { pintarEtapas(); pantalla.hidden = false; document.body.style.overflow = "hidden"; $("cerrarEtapas").focus(); }
function cerrarEtapas() { if (pantalla.hidden) return; pantalla.hidden = true; document.body.style.overflow = ""; $("verEtapas").focus(); }
$("verEtapas").onclick = abrirEtapas;
$("cerrarEtapas").onclick = cerrarEtapas;
$("etapasLista").onclick = (e) => {
  const b = e.target.closest("[data-etapa]");
  if (!b) return;
  cerrarEtapas();
  document.getElementById("etapa-" + b.dataset.etapa)?.scrollIntoView({ behavior: "smooth", block: "start" });
};
addEventListener("keydown", (e) => { if (e.key === "Escape") { if (!pantalla.hidden) cerrarEtapas(); else cerrarPanel(); } });

/* ---------- clics en el camino ---------- */
cont.onclick = async (e) => {
  const b = e.target.closest("button.cl");
  if (!b) return;
  if (b.dataset.estado === "bloqueado") { b.classList.add("sacudir"); setTimeout(() => b.classList.remove("sacudir"), 400); aviso("Completa la lección anterior primero.", true); return; }
  if (b.dataset.tipo === "cofre") {
    if (b.dataset.estado === "hecho") return aviso("Ya abriste este cofre.");
    try {
      const r = await api(`/api/nivel/${b.dataset.id}/completar/`, { fallos: 0 });
      const gema = r.minerales_ganados.diamante ? ` · +${r.minerales_ganados.diamante} 💎` : "";
      aviso(`¡Cofre abierto! +${r.xp_ganado} XP${gema}`);
      setTimeout(() => location.reload(), 900);
    } catch (x) { aviso(x.message, true); }
    return;
  }
  location.href = "/pages/reto.html?nivel=" + b.dataset.id;
};
await cargar();
