// Lógica de configuracion.html: cuenta, aprendizaje, apariencia, seguridad (contraseña y dispositivos), correos, instalar la app y sesión.
import { salir, terminarSesionLocal } from "./privacidad.js";
import { iniciar, api, esc, aviso, aplicarTema, aplicarCosmeticos } from "/js/app.js";
import { vistaPrevia } from "/js/cosmeticos.js";
import { estadoInstalacion, instalar } from "/js/pwa.js";
const { user, prog } = await iniciar("configuracion");
const $ = (id) => document.getElementById(id);

// Una sección a la vez (como pestañas), según el #ancla de la dirección.
const SECCIONES = [...document.querySelectorAll(".conf-sec")].map((s) => s.id);
function mostrarSeccion(id, enfocar = false) {
  if (!SECCIONES.includes(id)) id = SECCIONES[0];
  document.querySelectorAll(".conf-sec").forEach((s) => { s.hidden = s.id !== id; });
  document.querySelectorAll(".conf-nav a").forEach((a) => {
    const si = a.dataset.sec === id;
    a.setAttribute("aria-selected", String(si));
    a.tabIndex = si ? 0 : -1;
    if (si && enfocar) a.scrollIntoView({ block: "nearest", inline: "center" });
  });
}
document.querySelectorAll(".conf-nav a").forEach((a) => {
  a.addEventListener("click", (e) => {
    e.preventDefault();
    history.replaceState(null, "", "#" + a.dataset.sec);
    mostrarSeccion(a.dataset.sec, true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});
document.querySelector(".conf-nav").addEventListener("keydown", (e) => {
  if (!["ArrowDown", "ArrowUp", "ArrowLeft", "ArrowRight"].includes(e.key)) return;
  const enlaces = [...document.querySelectorAll(".conf-nav a")];
  const i = enlaces.indexOf(document.activeElement);
  const sig = enlaces[(i + (e.key === "ArrowDown" || e.key === "ArrowRight" ? 1 : -1) + enlaces.length) % enlaces.length];
  e.preventDefault(); sig.focus(); sig.click();
});
addEventListener("hashchange", () => mostrarSeccion(location.hash.slice(1), true));
mostrarSeccion(location.hash.slice(1));

// Instrucciones de instalación: abre las de este dispositivo.
{
  const ua = navigator.userAgent;
  const so = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1) ? "ios"
    : /Android/.test(ua) ? "android" : /CrOS/.test(ua) ? "chromeos" : /Windows/.test(ua) ? "windows" : /Mac OS X/.test(ua) ? "macos" : /Linux/.test(ua) ? "linux" : "";
  for (const lista of ["plataformas", "plataformasWidget"]) {
    const d = so && document.querySelector(`#${lista} details[data-so="${so}"]`);
    if (d) { d.open = true; d.classList.add("tuyo"); d.parentElement.prepend(d); }
  }
}

// Cuenta
$("nombre").value = user.nombre;
$("alias").value = user.alias || "";
$("codigo").textContent = user.codigo || "";
$("correo").textContent = user.email;
$("correoOculto").value = user.email;
$("copiarId").onclick = async () => { try { await navigator.clipboard.writeText(user.codigo); aviso("ID copiado"); } catch { aviso("No se pudo copiar", true); } };
$("fCuenta").onsubmit = async (e) => {
  e.preventDefault();
  try { await api("/api/ajustes/", { nombre: $("nombre").value, alias: $("alias").value }); aviso("Cuenta guardada"); } catch (x) { aviso(x.message, true); }
};

// Aprendizaje
$("meta").value = String(prog.perfil.meta_minutos);
$("curso").innerHTML = (await api("/api/cursos/")).cursos.map((c) => `<option value="${esc(c.slug)}"${c.slug === prog.curso_actual?.slug ? " selected" : ""}>${esc(c.nombre)}</option>`).join("");
$("fAprender").onsubmit = async (e) => {
  e.preventDefault();
  try { await api("/api/ajustes/", { curso: $("curso").value, meta: Number($("meta").value) }); aviso("Guardado"); } catch (x) { aviso(x.message, true); }
};

// Apariencia
$("buscable").checked = user.buscable_correo !== false;
$("buscable").onchange = async () => {
  try { await api("/api/ajustes/", { buscable_correo: $("buscable").checked }); aviso("Guardado"); } catch (x) { aviso(x.message, true); $("buscable").checked = !$("buscable").checked; }
};
document.querySelectorAll("[name=tema]").forEach((r) => {
  r.checked = r.value === (user.tema || "auto");
  r.onchange = async () => { aplicarTema(r.value); try { await api("/api/ajustes/", { tema: r.value }); } catch (x) { aviso(x.message, true); } };
});
const pref = (clave, def) => { try { return localStorage.getItem(clave) ?? def; } catch { return def; } };
$("sonido").checked = pref("cc_sonido", "1") !== "0";
import("/js/temporada.js").then(({ temporadaActiva, activarTemporada, temporadaDe }) => {
  $("temporada").checked = temporadaActiva();
  const t = temporadaDe();
  if (t) $("temporadaTxt").textContent += ` Ahora: ${t.icono} ${t.nombre}`;
  $("temporada").onchange = () => activarTemporada($("temporada").checked);
});
$("sonido").onchange = () => { try { localStorage.setItem("cc_sonido", $("sonido").checked ? "1" : "0"); if ($("sonido").checked) import("/js/sonidos.js").then((m) => m.sonar("premio")); } catch { aviso("No se pudo guardar en este navegador.", true); } };
// Teclado de CódigoCamp (celular)
$("tecladoCC").checked = pref("cc_teclado_propio", "0") === "1";
$("tecladoCC").onchange = async () => {
  const m = await import("/js/teclado-cc.js");
  m.activarTeclado($("tecladoCC").checked);
  if ($("tecladoCC").checked && !matchMedia("(pointer: coarse)").matches) aviso?.("Queda activado: lo verás cuando entres desde tu celular o tableta.");
};
$("tecladoSonido").checked = pref("cc_teclado_sonido", "1") !== "0";
$("tecladoSonido").onchange = () => { try { localStorage.setItem("cc_teclado_sonido", $("tecladoSonido").checked ? "1" : "0"); } catch { /* nada */ } };
$("movimiento").checked = pref("cc_menos_mov", "0") === "1";
$("movimiento").onchange = () => {
  try { localStorage.setItem("cc_menos_mov", $("movimiento").checked ? "1" : "0"); } catch { /* nada */ }
  document.documentElement.classList.toggle("cc-menos-mov", $("movimiento").checked);
  aplicarCosmeticos(user.cosmeticos || {});
};
const TIPOS = { fondo: "Fondo", cursor: "Puntero", tema: "Tema de color", marco: "Marco", efecto: "Efecto", dedo: "Rastro", codi: "Accesorio de Codi" };
async function pintarPuestos() {
  const c = await api("/api/cosmeticos/");
  user.cosmeticos = c.equipados;
  $("puestos").innerHTML = Object.entries(TIPOS).map(([t, n]) => {
    const propios = c.catalogo.filter((x) => x.tuyo && x.tipo === t);
    return `<label class="campo">${n}<select data-tipo="${t}" ${propios.length ? "" : "disabled"}><option value="">${propios.length ? "Ninguno" : "Aún no tienes"}</option>${propios.map((x) => `<option value="${esc(x.clave)}"${c.equipados[t] === x.clave ? " selected" : ""}>${esc(x.nombre)}</option>`).join("")}</select></label>`;
  }).join("");
}
$("puestos").onchange = async (e) => {
  const s = e.target.closest("select[data-tipo]");
  if (!s) return;
  try { const r = await api("/api/cosmeticos/equipar/", { tipo: s.dataset.tipo, clave: s.value || null }); user.cosmeticos = r.equipados; aplicarCosmeticos(r.equipados); aviso("Listo"); } catch (x) { aviso(x.message, true); }
};
$("quitarTodo").onclick = async () => {
  try { for (const t of Object.keys(TIPOS)) await api("/api/cosmeticos/equipar/", { tipo: t, clave: null }); aplicarCosmeticos({}); await pintarPuestos(); aviso("Cosméticos quitados"); } catch (x) { aviso(x.message, true); }
};
pintarPuestos().catch(() => {});

// Seguridad
$("fClave").onsubmit = async (e) => {
  e.preventDefault();
  if ($("claveNueva").value !== $("claveNueva2").value) { aviso("Las contraseñas nuevas no coinciden.", true); return; }
  try {
    await api("/api/auth/password/", { actual: $("claveActual").value, nueva: $("claveNueva").value });
    $("fClave").reset();
    aviso("Contraseña cambiada. Cerramos la sesión en tus otros dispositivos y te enviamos un correo de aviso.");
    pintarSesiones();
  } catch (x) { aviso(x.message, true); }
};
const cuando = (iso) => { const d = new Date(iso); const m = Math.round((Date.now() - d) / 60000); return m < 2 ? "ahora" : m < 60 ? `hace ${m} min` : m < 1440 ? `hace ${Math.round(m / 60)} h` : d.toLocaleDateString("es", { day: "numeric", month: "short", year: "numeric" }); };
try {
  const c = await api("/api/ajustes/correos/");
  $("dispositivos").innerHTML = c.dispositivos.length ? c.dispositivos.map((d, i) => `<li><span class="disp-ic">${/iPhone|Android|iPad/.test(d.nombre) ? "📱" : "💻"}</span><span><b>${esc(d.nombre)}</b>${i === 0 ? ' <em class="actual">este dispositivo</em>' : ""}<small>Último acceso ${cuando(d.ultimo)} · primero ${cuando(d.primero)}</small></span></li>`).join("") : '<li class="nota">Sin registros todavía.</li>';
  document.querySelectorAll("[data-correo]").forEach((x) => {
    x.checked = !!c[x.dataset.correo];
    x.onchange = async () => { try { await api("/api/ajustes/correos/", { [x.dataset.correo]: x.checked }); aviso("Guardado"); } catch (err) { x.checked = !x.checked; aviso(err.message, true); } };
  });
} catch { $("dispositivos").innerHTML = '<li class="nota">No se pudo cargar.</li>'; }

// Sesiones abiertas: cerrar una (en ese dispositivo) o todas, de verdad (el servidor las revoca).
async function pintarSesiones() {
  try {
    const { sesiones } = await api("/api/sesiones/");
    $("sesiones").innerHTML = sesiones.map((x) => `<li><span class="disp-ic">${/iPhone|Android|iPad/.test(x.dispositivo) ? "📱" : "💻"}</span><span><b>${esc(x.dispositivo)}</b>${x.actual ? ' <em class="actual">este dispositivo</em>' : ""}<small>Activa ${cuando(x.ultima)} · entró ${cuando(x.creada)} con ${esc(x.metodo)}${x.ip ? ` · IP ${esc(x.ip)}` : ""}</small></span><button type="button" class="mini ses-cerrar" data-sesion="${x.id}" data-actual="${x.actual}">${x.actual ? "Cerrar aquí" : "Cerrar sesión"}</button></li>`).join("") || '<li class="nota">No hay sesiones abiertas.</li>';
    $("cerrarOtras").disabled = sesiones.length < 2;
  } catch { $("sesiones").innerHTML = '<li class="nota">No se pudo cargar.</li>'; }
}
pintarSesiones();
$("sesiones").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-sesion]");
  if (!b) return;
  const actual = b.dataset.actual === "true";
  if (!confirm(actual ? "¿Cerrar la sesión en este dispositivo?" : "¿Cerrar la sesión en ese dispositivo? Quedará fuera al instante.")) return;
  try {
    const r = await api(`/api/sesiones/${b.dataset.sesion}`, undefined, "DELETE");
    if (r.era_esta) { await terminarSesionLocal(); return; }
    aviso("Listo: ese dispositivo ya no tiene tu sesión.");
    pintarSesiones();
  } catch (x) { aviso(x.message, true); }
});
$("cerrarOtras").onclick = async () => {
  if (!confirm("¿Cerrar la sesión en todos los demás dispositivos? Este seguirá dentro.")) return;
  try { const r = await api("/api/sesiones/cerrar-todas/", { excepto_este: true }); aviso(`Cerramos ${r.cerradas} sesión${r.cerradas === 1 ? "" : "es"}.`); pintarSesiones(); }
  catch (x) { aviso(x.message, true); }
};
const salirDeTodos = async () => {
  if (!confirm("¿Cerrar la sesión en TODOS los dispositivos, incluido este?")) return;
  await salir(api, { todas: true });
};
$("cerrarTodas").onclick = salirDeTodos;
$("salirTodos").onclick = salirDeTodos;

// App
function pintarInstalar() {
  const e = estadoInstalacion();
  $("instalar").hidden = !e.puede;
  $("instalarAyuda").innerHTML = e.instalada ? "✓ Ya estás usando la app instalada." : e.puede ? "" : e.ayuda;
}
pintarInstalar();
addEventListener("cc-instalable", pintarInstalar);
$("instalar").onclick = async () => { await instalar(); pintarInstalar(); };

// Widgets en cualquier sistema: usan la sesión que ya está abierta (siguen funcionando hasta que se cierre sesión).
{
  let enlaces = null;
  const pedir = async () => (enlaces ??= await api("/api/widget/conectar/"));
  const enLaApp = !!window.CodigoCampApp;
  pedir().then((e) => {
    // El botón de la app solo aparece si el APK está en frontend/descargas/ (y no si ya estás en la app)
    $("wgApk").hidden = !e.apk || enLaApp;
    if (enLaApp) $("wgEstado").textContent = "✓ Estás en la app: el widget de Android ya usa esta sesión.";
  }).catch((x) => { $("wgEstado").textContent = x.message; });
  $("wgCopiar").onclick = async () => {
    try { const e = await pedir(); await navigator.clipboard.writeText(e.pagina); aviso("Enlace del widget copiado"); }
    catch (x) { aviso(x.message || "No se pudo copiar", true); }
  };
  $("wgFlotante").onclick = () => window.open("/pages/widget.html?mini=1", "cc-widget", "popup=yes,width=340,height=230");
}

// Sesión
$("salir").onclick = () => salir(api);
if (location.hash) document.querySelector(location.hash)?.scrollIntoView();
