// Lógica de perfil.html: cabecera con foto (y su marco), insignias, estadísticas, lo que llevas puesto, cofres y cursos.
import { iniciar, api, esc, aviso, fotoDe, aplicarCosmeticos } from "/js/app.js";
import { FONDOS, vistaPrevia } from "/js/cosmeticos.js";
import { iconoSVG } from "/js/iconos.js";
import { svgCofre } from "/js/cofres.js";
document.querySelectorAll("[data-ic]").forEach((el) => { el.innerHTML = iconoSVG(el.dataset.ic, "ic-btn"); });
const { user, prog } = await iniciar("perfil");
import("/js/calendario.js").then((m) => m.montarCalendario(document.getElementById("calendario"))).catch(() => {});
const $ = (id) => document.getElementById(id);
const p = prog.perfil;
const csrf = () => (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";

function cabecera() {
  $("av").innerHTML = fotoDe(user, { tam: 112 });
  $("nom").textContent = user.nombre;
  $("ident").innerHTML = `@${esc(user.alias)} <span>· ID ${esc(user.codigo)}</span>`;
  const f = FONDOS[user.cosmeticos?.fondo];
  $("heroFondo").style.cssText = f ? f.css : "";
  if (f?.canvas) $("heroFondo").classList.add(`cc-prev-${f.canvas}`);
}
cabecera();
$("desde").textContent = "En CódigoCamp desde el " + new Date(user.desde).toLocaleDateString("es", { year: "numeric", month: "long", day: "numeric" });

const lecciones = Object.values(prog.lecciones_hechas).reduce((a, n) => a + n, 0);
const S = [["racha", p.racha_actual, "Racha actual", "días"], ["corona_campeon", p.racha_maxima, "Mejor racha", "días"], ["diamante", p.diamante, "Diamantes", ""],
  ["moneda_xp", p.xp_total, "XP total", ""], ["impulso_xp", p.nivel, "Nivel", ""], ["perfecto", prog.niveles_hechos, "Niveles superados", ""], ["aprende", lecciones, "Lecciones hechas", ""]];
$("stats").innerHTML = S.map(([ic, v, t, u]) => `<div class="stat-p"><span class="stat-ic">${iconoSVG(ic, "stat-icon")}</span><b>${esc(v)}${u ? ` <small>${u}</small>` : ""}</b><small>${t}</small></div>`).join("");

// Insignias: hitos visibles al lado del nombre
// Medallas por niveles (bronce, plata, oro, diamante) en lugar de emojis
const NIVELES_MEDALLA = [["bronce", 1], ["plata", 2], ["oro", 3], ["diamante", 4]];
const medalla = (valor, cortes) => NIVELES_MEDALLA[cortes.filter((c) => valor >= c).length - 1]?.[0] ?? null;
const ins = [
  ["racha", medalla(p.racha_maxima, [3, 7, 30, 100]), `Racha de ${p.racha_maxima} días`],
  ["impulso_xp", medalla(p.xp_total, [100, 500, 2000, 10000]), `${p.xp_total} XP`],
  ["niveles2", medalla(prog.niveles_hechos, [5, 10, 50, 200]), `${prog.niveles_hechos} niveles`],
  ["aprende", medalla(lecciones, [5, 10, 50, 200]), `${lecciones} lecciones`],
].filter(([, m]) => m);
$("insignias").innerHTML = ins.map(([ic, m, t]) => `<span class="insignia med-${m}" title="Medalla de ${m}: ${esc(t)}"><i class="med-ic">${iconoSVG(ic, "med-svg")}</i>${esc(t)}</span>`).join("");

// Lo que llevas puesto
const NOMBRE_TIPO = { fondo: "Fondo", cursor: "Puntero", tema: "Tema", marco: "Marco", efecto: "Efecto", dedo: "Rastro" };
let catalogo = [];
async function pintarPuesto() {
  const c = await api("/api/cosmeticos/");
  catalogo = c.catalogo;
  const eq = c.equipados;
  $("puesto").innerHTML = Object.entries(NOMBRE_TIPO).map(([t, n]) => {
    const item = catalogo.find((x) => x.clave === eq[t]);
    return `<div class="puesto-item"><small>${n}</small>${item ? `<div class="vista vista-${t}" data-prev="${esc(item.clave)}" data-tipo="${t}"></div><b>${esc(item.nombre)}</b>` : `<div class="vista vacia">—</div><b class="sub">Ninguno</b>`}</div>`;
  }).join("");
  $("puesto").querySelectorAll("[data-prev]").forEach((el) => vistaPrevia(el, el.dataset.prev, el.dataset.tipo));
  const mios = catalogo.filter((x) => x.tuyo);
  $("coleccion").innerHTML = mios.length
    ? `<div class="coleccion">${mios.map((i) => `<button type="button" class="obj-col rareza-${esc(i.rareza)}${eq[i.tipo] === i.clave ? " on" : ""}" data-equipar="${esc(i.clave)}" data-tipo="${i.tipo}" title="${eq[i.tipo] === i.clave ? "Quitar" : "Ponérmelo"}"><div class="vista vista-${i.tipo}" data-prev="${esc(i.clave)}" data-tipo="${i.tipo}"></div><small>${esc(i.nombre)}</small><em>${eq[i.tipo] === i.clave ? "Puesto" : NOMBRE_TIPO[i.tipo]}</em></button>`).join("")}</div>`
    : 'Aún no tienes cosméticos. Gana diamantes en <a href="/pages/recompensas.html">Recompensas</a> y consigue los tuyos en la <a href="/pages/tienda.html">tienda</a>.';
  $("coleccion").querySelectorAll("[data-prev]").forEach((el) => vistaPrevia(el, el.dataset.prev, el.dataset.tipo));
}
$("coleccion").onclick = async (e) => {
  const b = e.target.closest("[data-equipar]");
  if (!b) return;
  const tipo = b.dataset.tipo, clave = b.dataset.equipar;
  try {
    const r = await api("/api/cosmeticos/equipar/", { tipo, clave: user.cosmeticos?.[tipo] === clave ? null : clave });
    user.cosmeticos = r.equipados;
    aplicarCosmeticos(r.equipados);
    cabecera();
    await pintarPuesto();
  } catch (x) { aviso(x.message, true); }
};
pintarPuesto().catch(() => {});

// Cofres (resumen)
api("/api/cofres/").then(({ cofres }) => {
  $("cofresP").innerHTML = cofres.map((c) => `<span class="cofre-mini ${c.abierto ? "abierto" : c.listo ? "listo" : ""}" title="${esc(c.nombre)} · ${esc(c.texto)}"><span class="cofre-dib">${svgCofre(c.cofre, { abierto: c.abierto })}</span><small>${esc(c.nombre)}</small></span>`).join("");
}).catch(() => {});

// Cursos
const cursos = (await api("/api/cursos/")).cursos;
const nombres = Object.fromEntries(cursos.map((c) => [c.slug, c.nombre]));
const filas = Object.entries(prog.lecciones_hechas).sort((a, b) => b[1] - a[1]);
const maxL = Math.max(1, ...filas.map(([, n]) => n));
$("cursos").innerHTML = filas.length ? filas.map(([s, n]) => `<div class="curso-p"><b>${esc(nombres[s] || s)}</b><div class="barra"><i style="width:${(n / maxL) * 100}%"></i></div><small>${n} ${n === 1 ? "lección" : "lecciones"}</small></div>`).join("") : '<p class="nota">Todavía no has terminado ninguna lección en <a href="/pages/aprende.html">Aprende</a>.</p>';

/* ===== Foto de perfil: elegir, recortar (cuadrada) y subir ===== */
let img = null, zoom = 1, dx = 0, dy = 0;
const lienzo = $("lienzo"), ctx = lienzo.getContext("2d");
function dibujar(c = ctx, lado = lienzo.width) {
  c.clearRect(0, 0, lado, lado);
  if (!img) return;
  const base = Math.max(lado / img.width, lado / img.height) * zoom;
  const w = img.width * base, h = img.height * base;
  const f = lado / lienzo.width;
  c.drawImage(img, (lado - w) / 2 + dx * f, (lado - h) / 2 + dy * f, w, h);
  if (c === ctx) { c.save(); c.globalCompositeOperation = "destination-in"; c.beginPath(); c.arc(lado / 2, lado / 2, lado / 2, 0, 7); c.fill(); c.restore(); }
}
$("cambiarFoto").onclick = () => $("archivoFoto").click();
$("av").onclick = () => $("archivoFoto").click();
$("archivoFoto").onchange = async () => {
  const f = $("archivoFoto").files[0];
  $("archivoFoto").value = "";
  if (!f) return;
  if (f.size > 20 * 1024 * 1024) { aviso("La imagen pesa más de 20 MB.", true); return; }
  try {
    img = await createImageBitmap(f);
  } catch { aviso("No se pudo leer esa imagen.", true); return; }
  zoom = 1; dx = 0; dy = 0; $("zoom").value = "1";
  $("quitarFoto").hidden = !user.foto;
  dibujar();
  $("recorte").showModal();
};
$("zoom").oninput = () => { zoom = Number($("zoom").value); dibujar(); };
let arrastre = null;
lienzo.onpointerdown = (e) => { arrastre = { x: e.clientX - dx, y: e.clientY - dy }; lienzo.setPointerCapture(e.pointerId); };
lienzo.onpointermove = (e) => { if (!arrastre) return; dx = e.clientX - arrastre.x; dy = e.clientY - arrastre.y; dibujar(); };
lienzo.onpointerup = () => { arrastre = null; };
lienzo.onwheel = (e) => { e.preventDefault(); zoom = Math.min(4, Math.max(1, zoom - e.deltaY / 500)); $("zoom").value = String(zoom); dibujar(); };
$("recorte").addEventListener("close", async () => {
  const v = $("recorte").returnValue;
  if (v === "quitar") {
    try { await fetch("/api/perfil/foto/", { method: "DELETE", headers: { "X-CSRFToken": csrf() }, credentials: "same-origin" }); user.foto = ""; cabecera(); aviso("Foto quitada"); } catch { aviso("No se pudo quitar la foto.", true); }
    return;
  }
  if (v !== "guardar" || !img) return;
  const c = document.createElement("canvas");
  c.width = c.height = 512;
  dibujar(c.getContext("2d"), 512);
  const blob = await new Promise((r) => c.toBlob(r, "image/jpeg", 0.9));
  try {
    const r = await fetch("/api/perfil/foto/", { method: "POST", body: blob, headers: { "Content-Type": "application/octet-stream", "X-CSRFToken": csrf() }, credentials: "same-origin" });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "No se pudo subir la foto.");
    user.foto = j.foto;
    cabecera();
    document.querySelectorAll(".yo-chip .foto-perfil").forEach((el) => { const n = document.createElement("img"); n.src = j.foto; n.className = "foto-perfil"; n.style.cssText = "width:34px;height:34px;border-radius:50%;object-fit:cover;display:block"; el.replaceWith(n); });
    aviso("¡Foto actualizada!");
  } catch (x) { aviso(x.message, true); }
});

/* ===== Editar perfil ===== */
const forma = $("formPerfil");
$("fCurso").innerHTML = cursos.map((c) => `<option value="${esc(c.slug)}">${esc(c.nombre)}</option>`).join("");
let guardado = {};
try { guardado = (await api("/api/perfil/")).perfil; } catch {}

function abrirForma(abrir) {
  forma.hidden = !abrir;
  $("editar").setAttribute("aria-expanded", String(abrir));
  if (abrir) {
    $("fNombre").value = user.nombre;
    $("fAlias").value = user.alias || "";
    $("fCurso").value = prog.curso_actual?.slug || guardado.curso || cursos[0]?.slug;
    $("fMeta").value = String(p.meta_minutos);
    $("fRol").value = guardado.rol || "estudiante";
    $("fNivel").value = guardado.nivel || "cero";
    $("fNombre").focus();
  } else cabecera();
}
$("editar").onclick = () => abrirForma(forma.hidden);
$("cancelar").onclick = () => abrirForma(false);
forma.onsubmit = async (e) => {
  e.preventDefault();
  try {
    const r = await api("/api/ajustes/", {
      nombre: $("fNombre").value, alias: $("fAlias").value, curso: $("fCurso").value, meta: Number($("fMeta").value),
      rol: $("fRol").value, nivel: $("fNivel").value,
    });
    Object.assign(user, r.user);
    guardado = { ...guardado, rol: $("fRol").value, nivel: $("fNivel").value, curso: $("fCurso").value };
    forma.hidden = true; $("editar").setAttribute("aria-expanded", "false");
    cabecera();
    const chip = document.querySelector(".yo-chip");   // la foto de la barra lateral también cambia
    if (chip?.firstElementChild) chip.firstElementChild.outerHTML = fotoDe(user, { tam: 34 });
    aviso("Perfil actualizado");
  } catch (x) { aviso(x.message, true); }
};
