// Lógica de perfil.html
import { iniciar, api, esc, aviso } from "/js/app.js";
const { user, prog } = await iniciar("perfil");
const $ = (id) => document.getElementById(id);
const p = prog.perfil;
let avatar = user.avatar || "";
function cabecera() {
  $("av").textContent = avatar || user.nombre.charAt(0).toUpperCase();
  $("av").classList.toggle("emoji", !!avatar);
  $("nom").textContent = user.nombre;
  $("ident").textContent = `@${user.alias} · ID ${user.codigo}`;
}
cabecera();
$("desde").textContent = "Estudia con nosotros desde " + new Date(user.desde).toLocaleDateString("es", { year: "numeric", month: "long", day: "numeric" });
const S = [["🔥", p.racha_actual, "Racha actual"], ["🏅", p.racha_maxima, "Mejor racha"],
  ["💎", p.diamante, "Diamantes"],
  ["✨", p.xp_total, "XP total"], ["🎖️", p.nivel, "Nivel"],
  ["🎯", prog.niveles_hechos, "Niveles superados"], ["📚", Object.values(prog.lecciones_hechas).reduce((a, n) => a + n, 0), "Lecciones hechas"]];
$("stats").innerHTML = S.map(([i, v, t]) => `<div class="stat-p"><b>${i} ${esc(v)}</b><small>${t}</small></div>`).join("");
const nombres = Object.fromEntries((await api("/api/cursos/")).cursos.map((c) => [c.slug, c.nombre]));
const filas = Object.entries(prog.lecciones_hechas);
$("cursos").innerHTML = filas.length ? filas.map(([s, n]) => `<p><b>${esc(nombres[s] || s)}</b> · ${n} ${n === 1 ? "lección" : "lecciones"}</p>`).join("") : "Todavía no has terminado ninguna lección en Aprende.";
try {
  const t = await api("/api/tienda/");
  const mios = t.items.filter((i) => i.tuyo);
  $("coleccion").innerHTML = mios.length
    ? `<div class="coleccion">${mios.map((i) => `<span class="obj-col rareza-${esc(i.rareza)}" title="${esc(i.nombre)}">${esc(i.icono)}<small>${esc(i.nombre)}</small></span>`).join("")}</div>`
    : 'Aún no tienes objetos. Gana diamantes en <a href="/pages/recompensas.html">Recompensas</a> y consigue los tuyos en la <a href="/pages/tienda.html">tienda</a>.';
} catch { $("coleccion").textContent = ""; }

/* ===== Editar perfil ===== */
const forma = $("formPerfil");
const cursos = (await api("/api/cursos/")).cursos;
$("fCurso").innerHTML = cursos.map((c) => `<option value="${esc(c.slug)}">${esc(c.nombre)}</option>`).join("");
let guardado = {};
try { guardado = (await api("/api/perfil/")).perfil; } catch {}

async function pintarAvatares() {
  let a = { libres: [], coleccion: [] };
  try { a = await api("/api/avatares/"); } catch {}
  const op = (e, extra = "") => `<button type="button" class="av-op${e === avatar ? " on" : ""}${extra}" data-e="${esc(e)}" role="radio" aria-checked="${e === avatar}" aria-label="Avatar ${esc(e || "inicial")}">${e || user.nombre.charAt(0).toUpperCase()}</button>`;
  $("avatares").innerHTML = op("") + a.libres.map((e) => op(e)).join("") + a.coleccion.map((e) => op(e, " rara")).join("");
}
$("avatares").onclick = (e) => {
  const b = e.target.closest("[data-e]"); if (!b) return;
  avatar = b.dataset.e;
  $("avatares").querySelectorAll(".av-op").forEach((x) => { const on = x === b; x.classList.toggle("on", on); x.setAttribute("aria-checked", on); });
  $("av").textContent = avatar || user.nombre.charAt(0).toUpperCase();
  $("av").classList.toggle("emoji", !!avatar);
};

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
    pintarAvatares();
    $("fNombre").focus();
  } else { avatar = user.avatar || ""; cabecera(); }
}
$("editar").onclick = () => abrirForma(forma.hidden);
$("cancelar").onclick = () => abrirForma(false);
forma.onsubmit = async (e) => {
  e.preventDefault();
  try {
    const r = await api("/api/ajustes/", {
      nombre: $("fNombre").value, alias: $("fAlias").value, curso: $("fCurso").value, meta: Number($("fMeta").value),
      rol: $("fRol").value, nivel: $("fNivel").value, avatar,
    });
    Object.assign(user, r.user);
    guardado = { ...guardado, rol: $("fRol").value, nivel: $("fNivel").value, curso: $("fCurso").value };
    forma.hidden = true; $("editar").setAttribute("aria-expanded", "false");
    cabecera();
    aviso("Perfil actualizado");
  } catch (x) { aviso(x.message, true); }
};
