// Panel de administrador de CódigoCamp (solo ADMIN_EMAIL con la clave ADMIN_CLAVE).
// Navegación por #secciones: resumen, alertas, usuarios, usuario/<id>, cursos, curso/<id>, nivel/<id>, aprende/<slug>,
// tienda, disenar[/<clave>], medallas, bd.
import { api, getUser } from "./auth.js";
import { vistaPrevia, prepararVistas, probarDiseno, registrarDisenos } from "./cosmeticos.js";
import { editarImagen, elegirYEditar } from "./editor-imagen.js";
import { ANIM_MEDALLA, FORMAS_MEDALLA, METALES_MEDALLA, medallaSVG } from "./medalla-especial.js";
import { codiSVG } from "./codi.js";

const $ = (id) => document.getElementById(id);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const fecha = (iso) => (iso ? new Date(iso).toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" }) : "—");
const num = (n) => Number(n || 0).toLocaleString("es-CO");
const vista = $("vista");
const RAREZAS = { comun: "Común", raro: "Raro", epico: "Épico", legendario: "Legendario" };
const TIPOS_COS = { fondo: "Fondos", tema: "Temas", marco: "Marcos", cursor: "Punteros", efecto: "Efectos", dedo: "Rastros", teclado: "Teclados", codi: "Codi" };
const TIPO_UNO = { fondo: "Fondo", tema: "Tema", marco: "Marco", cursor: "Puntero", efecto: "Efecto", dedo: "Rastro", teclado: "Teclado", codi: "Accesorio de Codi", potenciador: "Potenciador", cofre: "Cofre" };

const SECCIONES = [
  { g: "General" }, { id: "resumen", t: "Resumen", i: "📊", tab: 1 }, { id: "alertas", t: "Alertas", i: "🚨", tab: 1, badge: 1 },
  { g: "Comunidad" }, { id: "usuarios", t: "Usuarios", i: "👥", tab: 1 },
  { g: "Contenido" }, { id: "cursos", t: "Cursos, retos y Aprende", corto: "Cursos", i: "🧩", tab: 1 },
  { g: "Tienda" }, { id: "tienda", t: "Artículos de la tienda", corto: "Tienda", i: "🛒", tab: 1 }, { id: "disenar", t: "Diseñar cosmético", i: "🎨" }, { id: "medallas", t: "Medallas", i: "🏅" },
  { g: "Sistema" }, { id: "antivirus", t: "Antivirus", i: "🛡️" }, { id: "bd", t: "Base de datos", i: "🗄️" },
];
const PADRE = { usuario: "usuarios", curso: "cursos", nivel: "cursos", aprende: "cursos", disenar: "tienda" };

// =============================================================================== utilidades de interfaz ====
function toast(msg, error = false) {
  const t = $("toast");
  t.textContent = msg; t.hidden = false; t.classList.toggle("err", error);
  clearTimeout(toast.t); toast.t = setTimeout(() => { t.hidden = true; }, 3400);
}
const fallo = (e) => toast(e?.message || String(e), true);
const gravedad = (g, txt) => `<span class="g g-${esc(g)}">${esc(txt || g)}</span>`;
const impacto = (n) => `<span class="a-impacto" title="Impacto de los últimos 30 días"><i style="--p:${Math.min(100, n)}%"></i>${n}</span>`;
const rareza = (r) => `<span class="a-chip r-${esc(r)}">${esc(RAREZAS[r] || r)}</span>`;
// Codi en el panel: lleva corbatín (es el jefe 😎) y acompaña la carga, los vacíos y la portada
const codiJefe = (animo = "feliz", tam = 64) => codiSVG(animo, { tam, accesorio: "codi_corbatin", titulo: "Codi, tu asistente del panel" });
const cargando = () => { vista.innerHTML = `<div class="a-codi-carga">${codiJefe("pensando", 72)}<span>Buscando la información…</span></div><div class="a-cargando"><i></i><i></i><i></i></div>`; };
const vacio = (emoji, texto) => `<div class="a-vacio"><div class="a-vacio-codi">${codiJefe("pensando", 70)}<b>${emoji}</b></div>${texto}</div>`;
const vacioCodi = (texto, animo = "feliz", boton = "＋ Crear") => `<div class="a-vacio">${codiJefe(animo, 96)}<p>${texto}</p><button class="a-btn pri" type="button" data-codi-accion>${boton}</button></div>`;
const CONSEJOS = [
  "En <b>Diseñar cosmético</b> prueba las plantillas legendarias: un clic y luego ajustas a tu gusto.",
  "Los fondos aceptan <b>GIFs animados</b> y hasta 8 stickers encima. ¡Y lluvia de emojis! 🌧️",
  "Puedo llevar accesorios que diseñes tú: sube una imagen o GIF en <b>Accesorio de Codi</b>. 🎩",
  "Cada parte del puntero se diseña aparte: el normal, el de los enlaces y el del texto. 🖱️",
  "Las medallas pueden tener forma de escudo, corona o engranaje, con cinta, letrero y brillo. 🏅",
  "En <b>Antivirus</b> puedes probar en vivo que el escudo de CódigoCamp detecta las amenazas. 🛡️",
  "Con la «vitrina» un artículo se inclina en 3D, brilla y suelta destellos en la tienda. ✨",
  "Los artículos «Con premios» pueden regalar una medalla especial al comprarlos. 🎁",
];
const interruptor = (name, texto, on = true) => `<label class="a-interruptor"><input type="checkbox" name="${name}" ${on ? "checked" : ""}> ${texto}</label>`;
const campo = (etq, control, extra = "") => `<label class="a-campo ${extra}">${etq}${control}</label>`;
const opciones = (lista, actual) => lista.map(([v, t]) => `<option value="${esc(v)}" ${String(v) === String(actual ?? "") ? "selected" : ""}>${esc(t)}</option>`).join("");

function cabecera(titulo, sub = "", acciones = "", atras = null) {
  $("titulo").textContent = titulo;
  $("subtitulo").textContent = sub;
  $("acciones").innerHTML = acciones;
  $("atras").hidden = !atras;
  $("atras").dataset.ir = atras || "";
  document.title = `${titulo} · Panel de CódigoCamp`;
}

/** Ventana (en el celular sube desde abajo). Devuelve el contenedor para leer el formulario y escuchar botones. */
function hoja({ titulo, cuerpo, pie = "", ancha = false }) {
  const dlg = $("hoja");
  dlg.classList.toggle("ancha", ancha);
  $("hojaCaja").innerHTML = `<div class="a-hoja-cab"><h2>${esc(titulo)}</h2><button type="button" class="a-icono" data-cerrar aria-label="Cerrar">✕</button></div>
    <div class="a-hoja-cuerpo">${cuerpo}</div>${pie ? `<div class="a-hoja-pie">${pie}</div>` : ""}`;
  if (!dlg.open) dlg.showModal();
  $("hojaCaja").querySelector("input,select,textarea")?.focus({ preventScroll: true });
  return $("hojaCaja");
}
const cerrarHoja = () => { if ($("hoja").open) $("hoja").close(); };
$("hoja").addEventListener("click", (e) => { if (e.target === $("hoja") || e.target.closest("[data-cerrar]")) cerrarHoja(); });

function confirmar(texto, { ok = "Sí, continuar", peligro = false, detalle = "" } = {}) {
  return new Promise((listo) => {
    const caja = hoja({ titulo: "¿Seguro?", cuerpo: `<p style="margin:0 0 6px;font-size:15px">${texto}</p>${detalle ? `<p class="a-sub">${detalle}</p>` : ""}`,
      pie: `<button class="a-btn ghost" data-cerrar type="button">Cancelar</button><button class="a-btn ${peligro ? "peligro" : "pri"}" id="hojaOk" type="button">${esc(ok)}</button>` });
    let resp = false;
    caja.querySelector("#hojaOk").addEventListener("click", () => { resp = true; cerrarHoja(); });
    $("hoja").addEventListener("close", () => listo(resp), { once: true });
  });
}

/** Formulario dentro de una hoja: al pulsar el botón principal llama enviar(valores) y cierra si sale bien. */
function hojaForm({ titulo, cuerpo, boton = "Guardar", ancha = false, peligro = false, enviar, alAbrir }) {
  const caja = hoja({ titulo, ancha, cuerpo: `<form id="hojaForm" class="a-form" novalidate>${cuerpo}<p class="a-err" id="hojaErr"></p></form>`,
    pie: `<button class="a-btn ghost" data-cerrar type="button">Cancelar</button><button class="a-btn ${peligro ? "peligro" : "pri"}" type="submit" form="hojaForm">${esc(boton)}</button>` });
  const form = caja.querySelector("#hojaForm");
  alAbrir?.(form);
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = caja.querySelector("[type=submit]");
    btn.disabled = true;
    try { await enviar(valores(form), form); cerrarHoja(); } catch (x) { caja.querySelector("#hojaErr").textContent = x.message; } finally { btn.disabled = false; }
  });
  return form;
}
function valores(form) {
  const o = {};
  for (const el of form.querySelectorAll("[name]")) {
    if (el.type === "checkbox") o[el.name] = el.checked;
    else if (el.type === "radio") { if (el.checked) o[el.name] = el.value; }
    else o[el.name] = el.value;
  }
  return o;
}
const lineas = (t) => String(t || "").split("\n").map((x) => x.trim()).filter(Boolean);

// =============================================================================== acceso y navegación ====
let usuarioAdmin = null;
async function arrancar() {
  const u = await getUser();
  usuarioAdmin = u;
  if (!u || !u.admin) { location.replace("/pages/login.html"); return; }
  let estado;
  try { estado = await api("/api/admin/estado"); } catch { location.replace("/pages/login.html"); return; }
  if (!estado.activo) {
    $("bloqueo").hidden = false;
    if (!estado.configurado) $("errClave").textContent = "Falta poner ADMIN_CLAVE en backend/.env y reiniciar Flask.";
    // Codi se tapa los ojos mientras escribes la clave (no mira 🙈)
    const img = document.querySelector("#formClave > img");
    if (img) img.outerHTML = `<div class="a-clave-codi" id="claveCodi">${codiJefe("saludo", 110)}</div>`;
    const cara = (a) => { const c = $("claveCodi"); if (c) c.innerHTML = codiJefe(a, 110); };
    $("clave").addEventListener("focus", () => cara("tapa"));
    $("clave").addEventListener("blur", () => cara("feliz"));
    $("clave").focus();
    return;
  }
  $("bloqueo").hidden = true;
  $("app").hidden = false;
  const marca = document.querySelector(".a-marca img");
  if (marca) marca.outerHTML = `<span class="a-marca-codi">${codiJefe("feliz", 40)}</span>`;
  prepararVistas();
  pintarMenu();
  route();
  contarAlertas();
  setInterval(contarAlertas, 45000);
}
$("formClave").addEventListener("submit", async (e) => {
  e.preventDefault();
  try { await api("/api/admin/entrar", { clave: $("clave").value }); arrancar(); }
  catch (x) { $("errClave").textContent = x.message; const c = $("claveCodi"); if (c) c.innerHTML = codiJefe("triste", 110); }
});
$("salirAdmin").addEventListener("click", async () => { await api("/api/admin/salir", {}).catch(() => {}); location.href = "/pages/inicio.html"; });
$("abrirMenu").addEventListener("click", () => menu(true));
$("velo").addEventListener("click", () => menu(false));
$("atras").addEventListener("click", () => { if ($("atras").dataset.ir === "<") history.back(); else location.hash = $("atras").dataset.ir; });
function menu(abrir) { $("app").classList.toggle("menu", abrir); $("velo").hidden = !abrir; }

function pintarMenu() {
  $("nav").innerHTML = SECCIONES.map((s) => (s.g ? `<h4>${s.g}</h4>` : `<a href="#${s.id}" data-sec="${s.id}"><i>${s.i}</i>${esc(s.t)}${s.badge ? '<span class="a-badge" data-badge hidden></span>' : ""}</a>`)).join("");
  $("tabbar").innerHTML = SECCIONES.filter((s) => s.tab).map((s) => `<a href="#${s.id}" data-sec="${s.id}"><i>${s.i}</i>${esc(s.corto || s.t)}${s.badge ? '<span class="a-badge" data-badge hidden></span>' : ""}</a>`).join("");
}
async function contarAlertas() {
  try {
    const r = await api("/api/admin/resumen");
    document.querySelectorAll("[data-badge]").forEach((b) => { b.hidden = !r.pendientes; b.textContent = r.pendientes; });
  } catch (e) { if (e?.estado === 404) location.reload(); }
}

const PAGINAS = { resumen, alertas, usuarios, usuario, cursos, curso, nivel, aprende, tienda, disenar, medallas, antivirus, bd };
async function route() {
  menu(false);
  const [sec = "resumen", ...params] = location.hash.slice(1).split("/").map(decodeURIComponent);
  const pagina = PAGINAS[sec] ? sec : "resumen";
  const activa = PADRE[pagina] || pagina;
  document.querySelectorAll("[data-sec]").forEach((a) => a.classList.toggle("on", a.dataset.sec === (pagina === "disenar" ? "disenar" : activa)));
  cerrarHoja();
  vista.onclick = null;   // cada página pone su propio manejador
  cargando();
  window.scrollTo(0, 0);
  try { await PAGINAS[pagina](...params); } catch (e) {
    if (e?.estado === 404 && /no encontrado/i.test(e.message || "")) { location.reload(); return; }
    vista.innerHTML = vacio("⚠️", esc(e?.message || e));
  }
}
addEventListener("hashchange", route);
const recargar = () => route();

// =============================================================================== resumen ====
async function resumen() {
  cabecera("Resumen", "Lo más importante de CódigoCamp de un vistazo", `<button class="a-btn sm" type="button" id="probarCorreo">✉️ <span class="txt">Probar correo</span></button>`);
  const r = await api("/api/admin/resumen");
  const avisos = [];
  if (!r.correo.configurado) avisos.push(`<div class="a-aviso rojo"><span>⚠️</span><div><b>Los correos NO están saliendo.</b><p>Configura <code>SMTP_USERNAME</code>, <code>SMTP_APP_PASSWORD</code> y <code>SMTP_FROM</code> en backend/.env (contraseña de aplicación de Gmail) y reinicia.</p></div></div>`);
  else if (r.correos_fallidos) avisos.push(`<div class="a-aviso nar"><span>⚠️</span><div><b>${r.correos_fallidos} correos de aviso no se pudieron enviar.</b><p>Revisa las alertas y usa «Reenviar correo».</p></div></div>`);
  if (!r.antivirus.activo) avisos.push('<div class="a-aviso rojo"><span>🛡️</span><div><b>El antivirus está APAGADO (ANTIVIRUS=0).</b></div></div>');
  else if (!r.antivirus.clamav) avisos.push('<div class="a-aviso ama"><span>🛡️</span><div><b>ClamAV no está instalado.</b><p>Para detectar los virus conocidos: <code>sudo apt install clamav clamav-daemon</code></p></div></div>');
  const hora = new Date().getHours();
  const saludo = hora < 12 ? "¡Buenos días" : hora < 19 ? "¡Buenas tardes" : "¡Buenas noches";
  const criticas = (r.por_gravedad?.critica || 0) + (r.por_gravedad?.alta || 0);
  const animo = criticas ? "alarma" : r.pendientes ? "pensando" : "celebra";
  const estado = criticas ? `Ojo: hay <b>${criticas} alerta${criticas === 1 ? "" : "s"} grave${criticas === 1 ? "" : "s"}</b> esperando tu decisión. 🚨`
    : r.pendientes ? `Tienes <b>${r.pendientes} alerta${r.pendientes === 1 ? "" : "s"}</b> por revisar, nada grave.` : "Todo tranquilo por aquí: ninguna alerta pendiente. 🎉";
  const consejo = CONSEJOS[Math.floor(Date.now() / 3.6e6) % CONSEJOS.length];
  vista.innerHTML = `<section class="a-codi-hero ${animo}">
      <div class="a-codi-hero-codi">${codiJefe(animo === "celebra" ? "saludo" : animo, 128)}</div>
      <div class="a-codi-globo"><b>${saludo}, ${esc((usuarioAdmin?.nombre || "jefe").split(" ")[0])}!</b><p>${estado}</p>
        <p class="a-codi-dato">⚡ ${num(r.activos_24h)} estudiantes activos hoy · 🆕 ${num(r.nuevos_7d)} nuevos esta semana</p>
        <p class="a-codi-tip">💡 ${consejo}</p>
        <div class="a-codi-acc">${criticas || r.pendientes ? '<a class="a-btn pri sm" href="#alertas">🚨 Ver alertas</a>' : ""}<a class="a-btn sm" href="#disenar">🎨 Diseñar algo</a><a class="a-btn sm" href="#medallas">🏅 Nueva medalla</a><a class="a-btn sm ghost" href="#antivirus">🛡️ Probar antivirus</a></div>
      </div></section>
    ${avisos.join("")}
    <div class="a-kpis">
      <div class="a-kpi"><i>👥</i><b>${num(r.usuarios)}</b><span>usuarios</span></div>
      <div class="a-kpi verde"><i>⚡</i><b>${num(r.activos_24h)}</b><span>activos en 24 h</span></div>
      <div class="a-kpi"><i>🆕</i><b>${num(r.nuevos_7d)}</b><span>nuevos esta semana</span></div>
      <div class="a-kpi ${r.pendientes ? "rojo" : ""}"><i>🚨</i><b>${num(r.pendientes)}</b><span>alertas sin revisar</span></div>
      <div class="a-kpi"><i>⛔</i><b>${num(r.bloqueados)}</b><span>cuentas bloqueadas</span></div>
    </div>
    <section class="a-sec"><div class="a-sec-cab"><h2>Accesos rápidos</h2></div>
      <div class="a-rapidas">
        <a class="a-rapida" href="#disenar"><b>🎨</b><span>Diseñar cosmético<small>Fondos, marcos, temas…</small></span></a>
        <a class="a-rapida" href="#cursos"><b>🧩</b><span>Cursos y retos<small>Lenguajes, retos y Aprende</small></span></a>
        <a class="a-rapida" href="#tienda"><b>🛒</b><span>Tienda<small>Precios y artículos</small></span></a>
        <a class="a-rapida" href="#medallas"><b>🏅</b><span>Medallas<small>Crear y entregar</small></span></a>
      </div></section>
    <section class="a-sec"><div class="a-sec-cab"><h2>Alertas pendientes</h2>
      <div class="a-chips">${Object.entries(r.por_gravedad).map(([g, n]) => gravedad(g, `${{ critica: "Crítica", alta: "Alta", media: "Media", baja: "Baja" }[g]} · ${n}`)).join("")}</div>
      <a class="a-btn sm ghost" href="#alertas">Ver todas →</a></div>
      ${r.incidentes.length ? r.incidentes.map(tarjetaAlerta).join("") : vacio("🎉", "No hay alertas pendientes.")}</section>`;
  $("probarCorreo").addEventListener("click", async (e) => {
    const b = e.currentTarget; b.disabled = true;
    try { toast((await api("/api/admin/correo-prueba", {})).mensaje); } catch (x) { toast(`No salió: ${x.message}`, true); }
    b.disabled = false;
  });
}

// =============================================================================== alertas ====
function tarjetaAlerta(i, { enFicha = false } = {}) {
  const u = i.usuario || {};
  const tipo = { archivo: "📁 Archivo", comando: "⌨️ Comando", enlace: "🔗 Enlace", codigo: "🧬 Código", manual: "✋ Manual" }[i.tipo] || i.tipo;
  const correo = { enviado: ["verde", "✉️ correo enviado"], sin_smtp: ["rojo", "correo NO salió (falta SMTP)"], error: ["rojo", "correo falló"], limite: ["nar", "correo omitido (límite)"], pendiente: ["", "enviando correo…"] }[i.correo_estado] || ["", ""];
  return `<article class="a-alerta g-${esc(i.gravedad)}" data-incidente="${i.id}">
    <div class="a-alerta-cab">${gravedad(i.gravedad, `${i.gravedad_txt} · ${i.puntos} pts`)}<b>${esc(tipo)}</b>
      <span class="a-chip">${esc(i.estado)}</span>${correo[1] ? `<span class="a-chip ${correo[0]}" title="${esc(i.correo_detalle || "")}">${esc(correo[1])}</span>` : ""}
      <span class="a-sub">${esc(i.origen)} · ${fecha(i.creado)}</span></div>
    ${enFicha ? "" : `<div><a href="#usuario/${u.id}"><b>${esc(u.nombre)}</b></a> <span class="a-sub" style="display:inline">${esc(u.email)}</span> · ${impacto(u.impacto || 0)}${u.activo === false ? ' <span class="a-chip rojo">bloqueado</span>' : ""}</div>`}
    <div><b>${esc(i.motivo)}</b></div>
    ${i.evidencia ? `<code>${esc(i.evidencia)}</code>` : ""}
    ${i.explicacion ? `<div class="a-sub">⚖️ ${esc(i.explicacion)}</div>` : ""}
    ${i.correo_detalle && i.correo_estado !== "enviado" ? `<div class="a-err">${esc(i.correo_detalle)}</div>` : ""}
    <div class="a-sub">💡 ${esc(i.recomendacion)}</div>
    <div class="a-acc">
      ${i.estado === "pendiente" ? `<button class="a-btn sm" type="button" data-dec="ignorar">Ignorar</button><button class="a-btn sm" type="button" data-dec="advertir">✉️ Advertir</button>${u.activo !== false ? '<button class="a-btn sm peligro" type="button" data-dec="bloquear">⛔ Bloquear</button>' : ""}` : ""}
      ${!["enviado", "pendiente"].includes(i.correo_estado) ? '<button class="a-btn sm" type="button" data-dec="reenviar">🔁 Reenviar correo</button>' : ""}
      <button class="a-btn sm ghost" type="button" data-dec="quitar">🗑 Quitar falta</button>
    </div></article>`;
}
/** Botones de las alertas (en Alertas, Resumen y la ficha del usuario). */
async function accionAlerta(boton, despues) {
  const id = boton.closest("[data-incidente]").dataset.incidente;
  const dec = boton.dataset.dec;
  if (dec === "quitar") {
    if (!(await confirmar("¿Quitar esta falta?", { ok: "Quitar falta", detalle: "Ya no contará en el impacto de la persona." }))) return;
    await api(`/api/admin/incidentes/${id}`, null, "DELETE"); toast("Falta quitada."); return despues();
  }
  if (dec === "advertir") {
    return hojaForm({ titulo: "Advertir otra vez", boton: "Enviar advertencia", cuerpo: campo("Mensaje para la persona (opcional)", '<textarea name="mensaje" placeholder="Explica qué no debe volver a hacer"></textarea>'),
      enviar: async (v) => { await api(`/api/admin/incidentes/${id}`, { decision: "advertir", mensaje: v.mensaje }); toast("Advertencia enviada."); despues(); } });
  }
  if (dec === "bloquear") {
    return hojaForm({ titulo: "Bloquear la cuenta", boton: "Bloquear", peligro: true,
      cuerpo: `<p class="a-sub" style="margin-bottom:12px">Se cierran sus sesiones en todos sus dispositivos y le llega un correo con el motivo.</p>${campo("Motivo del bloqueo", '<textarea name="motivo">Subir o ejecutar contenido malicioso en CódigoCamp</textarea>')}`,
      enviar: async (v) => { await api(`/api/admin/incidentes/${id}`, { decision: "bloquear", motivo: v.motivo }); toast("Cuenta bloqueada."); despues(); } });
  }
  await api(`/api/admin/incidentes/${id}`, { decision: dec });
  toast(dec === "reenviar" ? "Correo reenviado." : "Listo.");
  despues();
}

async function alertas(estado = "pendiente") {
  cabecera("Alertas de seguridad", "Lo que bloqueó el escudo. Nada se bloquea solo: tú decides.");
  const r = await api(`/api/admin/incidentes?estado=${encodeURIComponent(estado)}`);
  const filtros = [["pendiente", "Pendientes"], ["advertido", "Advertidas"], ["bloqueado", "Bloqueadas"], ["ignorado", "Ignoradas"], ["todos", "Todas"]];
  vista.innerHTML = `<div class="a-herr"><div class="a-seg" id="filtroAl">${filtros.map(([v, t]) => `<button type="button" data-v="${v}" class="${v === estado ? "on" : ""}">${t}</button>`).join("")}</div></div>
    <div id="listaAl">${r.incidentes.length ? r.incidentes.map((i) => tarjetaAlerta(i)).join("") : vacio("🛡️", "No hay alertas aquí.")}</div>`;
  $("filtroAl").addEventListener("click", (e) => { const b = e.target.closest("[data-v]"); if (b) location.hash = `alertas/${b.dataset.v}`; });
}

// =============================================================================== usuarios ====
const inicial = (n) => esc((n || "?").trim().charAt(0).toUpperCase());
async function usuarios(q = "", pagina = "1", filtro = "") {
  pagina = Number(pagina) || 1;
  cabecera("Usuarios", "Busca una cuenta para ver y editar su perfil");
  const r = await api(`/api/admin/usuarios?q=${encodeURIComponent(q)}&pagina=${pagina}&filtro=${encodeURIComponent(filtro)}`);
  const ir = (qq, pp, ff) => { location.hash = `usuarios/${encodeURIComponent(qq)}/${pp}/${encodeURIComponent(ff)}`; };
  vista.innerHTML = `<form class="a-herr" id="buscarU"><div class="a-buscar"><input id="qU" type="search" placeholder="Nombre, correo o alias" value="${esc(q)}" enterkeyhint="search"></div>
      <div class="a-seg" id="filtroU"><button type="button" data-f="" class="${!filtro ? "on" : ""}">Todos (${filtro ? "…" : r.total})</button><button type="button" data-f="bloqueados" class="${filtro ? "on" : ""}">Bloqueados</button></div></form>
    <div class="a-usuarios">${r.usuarios.map((u) => `<button type="button" class="a-usuario" data-ir="usuario/${u.id}">
      <span class="a-avatar">${inicial(u.nombre)}</span>
      <span class="a-usuario-dat"><b>${esc(u.nombre)}${u.admin ? " 🛡️" : ""}</b><span>${esc(u.email)}${u.alias ? ` · @${esc(u.alias)}` : ""}</span></span>
      <span class="a-usuario-num"><span>Nv <b>${u.nivel}</b></span><span>💎 <b>${num(u.diamante)}</b></span><span>🔥 <b>${u.racha}</b></span>${impacto(u.impacto)}
        ${u.bloqueado ? '<span class="a-chip rojo">bloqueado</span>' : '<span class="a-chip verde">activo</span>'}</span></button>`).join("") || vacio("🔍", "No se encontró a nadie.")}</div>
    <div class="a-paginas">${pagina > 1 ? '<button class="a-btn sm" id="pAnt" type="button">← Anterior</button>' : ""}<span class="a-sub">Página ${pagina} de ${Math.max(1, Math.ceil(r.total / 50))}</span>${pagina * 50 < r.total ? '<button class="a-btn sm" id="pSig" type="button">Siguiente →</button>' : ""}</div>`;
  $("buscarU").addEventListener("submit", (e) => { e.preventDefault(); ir($("qU").value.trim(), 1, filtro); });
  $("filtroU").addEventListener("click", (e) => { const b = e.target.closest("[data-f]"); if (b) ir(q, 1, b.dataset.f); });
  $("pAnt")?.addEventListener("click", () => ir(q, pagina - 1, filtro));
  $("pSig")?.addEventListener("click", () => ir(q, pagina + 1, filtro));
}

let catalogoCos = null;
const traerCatalogo = async () => (catalogoCos ??= await api("/api/admin/cosmeticos"));

async function usuario(id, pestana = "cuenta") {
  const [r, { medallas: ms }] = await Promise.all([api(`/api/admin/usuarios/${id}`), api("/api/admin/medallas")]);
  const u = r.usuario, p = r.perfil || {};
  cabecera(u.nombre, u.email, "", "usuarios");
  const pestanas = [["cuenta", "✏️ Cuenta"], ["regalos", "🎁 Regalos"], ["seguridad", `🛡️ Seguridad${r.incidentes.length ? ` (${r.incidentes.length})` : ""}`], ["actividad", "🕒 Actividad"], ["datos", "🗂️ Datos"]];
  const numero = (name, valor, rapidos = []) => `<div class="a-numero"><button type="button" data-paso="-1">−</button><input type="number" inputmode="numeric" name="${name}" value="${valor ?? 0}" min="0"><button type="button" data-paso="1">+</button></div>
    ${rapidos.length ? `<div class="a-rapidos">${rapidos.map((n) => `<button type="button" class="a-btn sm ghost" data-suma="${n}">+${num(n)}</button>`).join("")}</div>` : ""}`;
  let cuerpo = "";
  if (pestana === "cuenta") {
    cuerpo = `<form id="formCuenta" class="a-tarjeta" novalidate>
      <div class="a-campos">
        ${campo("Nombre", `<input name="nombre" value="${esc(u.nombre)}" maxlength="80">`)}
        ${campo("Alias", `<input name="alias" value="${esc(p.alias || "")}" maxlength="20" placeholder="sin alias">`)}
        ${campo("💎 Diamantes", numero("diamante", p.diamante, [50, 100, 500, 1000]))}
        ${campo("⚡ XP total", numero("xp_total", p.xp_total, [50, 100, 500]))}
        ${campo("❤️ Vidas", numero("vidas", p.vidas))}
        ${campo("🧊 Salvarrachas (máx. 10)", numero("salvarrachas", p.salvarrachas))}
        ${campo("🔥 Racha actual (días)", numero("racha_actual", p.racha_actual))}
        ${campo("🏆 Racha máxima", numero("racha_maxima", p.racha_maxima))}
        ${campo("Mensaje para la persona (opcional)", '<textarea name="nota" placeholder="Ej.: ¡Gracias por reportar el error! Aquí tienes un regalo."></textarea>', "todo")}
        <div class="todo">${interruptor("avisar", "Avisarle por correo lo que cambió («🎁 Recibiste 500 diamantes»…)")}</div>
      </div>
      <p class="a-err" id="errCuenta"></p>
      <div style="display:flex;justify-content:flex-end;margin-top:8px"><button class="a-btn pri" type="submit">Guardar cambios</button></div></form>`;
  } else if (pestana === "regalos") {
    const cat = await traerCatalogo();
    const propios = new Set(r.cosmeticos);
    const porClave = Object.fromEntries(cat.catalogo.map((c) => [c.clave, c]));
    cuerpo = `<div class="a-rejilla">
      <section class="a-tarjeta"><div class="a-sec-cab"><h2>🏅 Medallas especiales</h2></div>
        <div class="a-lista">${r.medallas_especiales.map((m) => `<div class="a-fila"><span>${esc(m.icono)} <b>${esc(m.nombre)}</b> <small>${esc(m.motivo || "")}</small></span><button class="a-btn sm ghost" type="button" data-quitar-medalla="${m.id}">Quitar</button></div>`).join("") || '<p class="a-sub">Todavía no tiene medallas especiales.</p>'}</div>
        <form id="formMedalla" class="a-campos" style="margin-top:12px">
          ${campo("Dar medalla", `<select name="medalla_id" required><option value="">Elige una medalla…</option>${ms.filter((m) => m.activa).map((m) => `<option value="${m.id}">${esc(m.icono)} ${esc(m.nombre)}</option>`).join("")}</select>`)}
          ${campo("Motivo (opcional)", '<input name="motivo" maxlength="160" placeholder="Por reportar un error">')}
          <div class="todo" style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap">${interruptor("avisar", "Avisar por correo")}<button class="a-btn pri sm" type="submit">🏅 Dar medalla</button></div>
        </form>${ms.length ? "" : '<p class="a-sub">Crea medallas en <a href="#medallas">Medallas</a>.</p>'}</section>
      <section class="a-tarjeta"><div class="a-sec-cab"><h2>🎨 Cosméticos (${propios.size})</h2></div>
        <form id="formRegalo" class="a-campos">
          ${campo("Regalar cosmético", `<select name="clave" required><option value="">Elige un cosmético…</option>${Object.entries(TIPOS_COS).map(([t, n]) => `<optgroup label="${n}">${cat.catalogo.filter((c) => c.tipo === t && !propios.has(c.clave)).map((c) => `<option value="${esc(c.clave)}">${esc(c.nombre)} · ${esc(RAREZAS[c.rareza] || c.rareza)}</option>`).join("")}</optgroup>`).join("")}</select>`, "todo")}
          ${campo("Mensaje (opcional)", '<input name="nota" maxlength="300" placeholder="¡Feliz cumpleaños!">', "todo")}
          <div class="todo" style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap">${interruptor("avisar", "Avisar por correo")}<button class="a-btn pri sm" type="submit">🎁 Regalar</button></div>
        </form>
        <div class="a-lista" style="margin-top:12px;max-height:320px;overflow:auto">${r.cosmeticos.map((k) => `<div class="a-fila"><span><b>${esc(porClave[k]?.nombre || k)}</b> <small>${esc(TIPO_UNO[porClave[k]?.tipo] || "")}</small></span><button class="a-btn sm ghost" type="button" data-quitar-cos="${esc(k)}">Quitar</button></div>`).join("") || '<p class="a-sub">No tiene cosméticos.</p>'}</div>
      </section></div>`;
  } else if (pestana === "seguridad") {
    cuerpo = `<section class="a-tarjeta"><div class="a-sec-cab"><h2>Estado de la cuenta</h2>${impacto(u.impacto)}</div>
        ${r.bloqueo ? `<div class="a-aviso rojo"><span>⛔</span><div><b>Bloqueada desde ${fecha(r.bloqueo.desde)}</b><p>${esc(r.bloqueo.motivo || "Sin motivo")}</p></div></div>` : '<p class="a-sub" style="margin-bottom:12px">La cuenta está activa.</p>'}
        <div class="a-chips" style="gap:8px">
          ${u.admin ? '<span class="a-chip mor">Tu cuenta de administrador</span>' : u.bloqueado ? '<button class="a-btn ok" type="button" data-acc="desbloquear">✅ Desbloquear</button>' : '<button class="a-btn peligro" type="button" data-acc="bloquear">⛔ Bloquear</button>'}
          <button class="a-btn" type="button" data-acc="advertir">✉️ Advertir por correo</button>
          ${r.incidentes.length ? '<button class="a-btn" type="button" data-acc="limpiar">🧹 Quitar todas las faltas</button>' : ""}
        </div></section>
      <section class="a-sec"><div class="a-sec-cab"><h2>Faltas (${r.incidentes.length})</h2></div>${r.incidentes.map((i) => tarjetaAlerta(i, { enFicha: true })).join("") || vacio("✅", "Sin faltas.")}</section>`;
  } else if (pestana === "actividad") {
    cuerpo = `<section class="a-sec"><div class="a-sec-cab"><h2>Sesiones</h2></div><div class="a-tabla-w"><table class="a-tabla"><thead><tr><th>Dispositivo</th><th>IP</th><th>Método</th><th>Última vez</th><th></th></tr></thead><tbody>
        ${r.sesiones.map((s) => `<tr><td>${esc(s.dispositivo)}</td><td>${esc(s.ip)}</td><td>${esc(s.metodo)}</td><td>${fecha(s.ultima)}</td><td>${s.revocada ? '<span class="a-chip">cerrada</span>' : '<span class="a-chip verde">abierta</span>'}</td></tr>`).join("") || '<tr><td colspan="5" class="a-sub">Sin sesiones.</td></tr>'}</tbody></table></div></section>
      <section class="a-sec"><div class="a-sec-cab"><h2>Compras</h2></div><div class="a-lista">${r.compras.map((c) => `<div class="a-fila"><span><b>${esc(c.articulo)}</b></span><small>${num(c.precio)} 💎 · ${fecha(c.fecha)}</small></div>`).join("") || '<p class="a-sub">Sin compras.</p>'}</div></section>
      <section class="a-sec"><div class="a-sec-cab"><h2>Medallas del mes</h2></div><div class="a-chips">${r.medallas_mes.map((c) => `<span class="a-chip">${esc(c)}</span>`).join("") || '<span class="a-sub">Ninguna.</span>'}</div></section>`;
  } else {
    const datos = (o) => `<div class="a-datos">${Object.entries(o || {}).map(([k, v]) => `<div><span>${esc(k)}</span><b>${esc(typeof v === "object" && v !== null ? JSON.stringify(v) : v ?? "—")}</b></div>`).join("")}</div>`;
    cuerpo = `<section class="a-tarjeta"><div class="a-sec-cab"><h2>Cuenta</h2></div>${datos(r.cuenta)}</section><section class="a-tarjeta a-sec"><div class="a-sec-cab"><h2>Perfil</h2></div>${datos(r.perfil)}</section>`;
  }
  vista.innerHTML = `<div class="a-ficha-cab"><span class="a-avatar grande">${inicial(u.nombre)}</span><div><h2>${esc(u.nombre)} ${u.admin ? "🛡️" : ""}</h2>
      <div class="a-mini-stats"><span class="a-chip">Nivel ${u.nivel}</span><span class="a-chip cian">💎 ${num(u.diamante)}</span><span class="a-chip nar">🔥 ${u.racha} días</span>${u.alias ? `<span class="a-chip">@${esc(u.alias)}</span>` : ""}${u.google ? '<span class="a-chip">Google</span>' : ""}${u.bloqueado ? '<span class="a-chip rojo">bloqueado</span>' : ""}</div></div></div>
    <div class="a-tabs">${pestanas.map(([k, t]) => `<button type="button" data-tab="${k}" class="${k === pestana ? "on" : ""}">${t}</button>`).join("")}</div>${cuerpo}`;

  vista.querySelector(".a-tabs").addEventListener("click", (e) => { const b = e.target.closest("[data-tab]"); if (b) location.hash = `usuario/${id}/${b.dataset.tab}`; });
  const otraVez = () => usuario(id, pestana).catch(fallo);
  // Cuenta
  $("formCuenta")?.addEventListener("click", (e) => {
    const paso = e.target.closest("[data-paso],[data-suma]");
    if (!paso) return;
    const input = paso.closest(".a-campo").querySelector("input[type=number]");
    input.value = Math.max(0, Number(input.value || 0) + Number(paso.dataset.paso || paso.dataset.suma));
  });
  $("formCuenta")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const v = valores(e.target);
    try {
      const res = await api(`/api/admin/usuarios/${id}`, v, "PATCH");
      toast(res.cambios ? `Guardado.${res.correo ? " ✉️ Le enviamos un correo con los cambios." : ""}` : "No había cambios.");
      otraVez();
    } catch (x) { $("errCuenta").textContent = x.message; }
  });
  // Regalos
  $("formMedalla")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    try { await api(`/api/admin/usuarios/${id}/medalla`, valores(e.target)); toast("🏅 Medalla entregada."); otraVez(); } catch (x) { fallo(x); }
  });
  $("formRegalo")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    try { await api(`/api/admin/usuarios/${id}/regalar`, valores(e.target)); toast("🎁 Regalo enviado."); otraVez(); } catch (x) { fallo(x); }
  });
  vista.onclick = async (e) => {
    const qm = e.target.closest("[data-quitar-medalla]"), qc = e.target.closest("[data-quitar-cos]"), acc = e.target.closest("[data-acc]"), dec = e.target.closest("[data-dec]");
    try {
      if (qm) { await api(`/api/admin/usuarios/${id}/quitar-medalla`, { medalla_id: qm.dataset.quitarMedalla }); toast("Medalla quitada."); otraVez(); }
      else if (qc) { if (await confirmar("¿Quitarle este cosmético?")) { await api(`/api/admin/usuarios/${id}/quitar-cosmetico`, { clave: qc.dataset.quitarCos }); toast("Cosmético quitado."); otraVez(); } }
      else if (dec) await accionAlerta(dec, otraVez);
      else if (acc?.dataset.acc === "bloquear") {
        hojaForm({ titulo: `Bloquear a ${u.nombre}`, boton: "Bloquear cuenta", peligro: true, cuerpo: `<p class="a-sub" style="margin-bottom:12px">Se cierran sus sesiones y le llega un correo con el motivo.</p>${campo("Motivo", '<textarea name="motivo" required></textarea>')}`,
          enviar: async (v) => { await api(`/api/admin/usuarios/${id}/bloquear`, v); toast("Cuenta bloqueada."); otraVez(); } });
      } else if (acc?.dataset.acc === "desbloquear") {
        hojaForm({ titulo: `Desbloquear a ${u.nombre}`, boton: "Desbloquear", cuerpo: `${campo("Mensaje (opcional)", '<textarea name="nota"></textarea>')}${interruptor("avisar", "Avisarle por correo")}`,
          enviar: async (v) => { await api(`/api/admin/usuarios/${id}/desbloquear`, v); toast("Cuenta desbloqueada."); otraVez(); } });
      } else if (acc?.dataset.acc === "advertir") {
        hojaForm({ titulo: "Advertencia por correo", boton: "Enviar advertencia", cuerpo: `${campo("Mensaje", '<textarea name="mensaje" required placeholder="Qué hizo y por qué no está permitido"></textarea>')}
          ${campo("Gravedad", `<select name="gravedad">${opciones([["baja", "Baja"], ["media", "Media"], ["alta", "Alta"], ["critica", "Crítica"]], "media")}</select>`)}`,
          enviar: async (v) => { await api(`/api/admin/usuarios/${id}/advertir`, v); toast("Advertencia enviada."); otraVez(); } });
      } else if (acc?.dataset.acc === "limpiar") {
        hojaForm({ titulo: "Quitar todas las faltas", boton: "Quitar faltas", cuerpo: `<p class="a-sub" style="margin-bottom:12px">Se borran sus ${r.incidentes.length} faltas y su impacto vuelve a 0.</p>${interruptor("avisar", "Avisarle por correo que se retiraron")}`,
          enviar: async (v) => { await api(`/api/admin/usuarios/${id}/limpiar-faltas`, v); toast("Faltas retiradas."); otraVez(); } });
      }
    } catch (x) { fallo(x); }
  };
}

// =============================================================================== cursos ====
let datosCursos = null;
async function cursos() {
  cabecera("Cursos, retos y Aprende", "Crea lenguajes, retos y lecciones", `<button class="a-btn pri sm" type="button" id="nuevoCurso">＋ <span class="txt">Nuevo lenguaje</span></button>`);
  datosCursos = await api("/api/admin/cursos");
  const tarjeta = (c) => `<button type="button" class="a-curso ${c.activo ? "" : "inactivo"}" data-ir="curso/${c.id}">
    <span class="a-sigla" style="--c:${esc(c.color)}">${esc(c.sigla)}</span>
    <span><b>${esc(c.nombre)}</b><p>${esc(c.descripcion || "Sin descripción")}</p>
      <span class="a-chips">${c.origen === "panel" ? '<span class="a-chip verde">Creado en el panel</span>' : '<span class="a-chip">De fábrica</span>'}${c.activo ? "" : '<span class="a-chip rojo">oculto</span>'}
        <span class="a-chip cian">${c.niveles} niveles</span><span class="a-chip">${c.retos} retos</span>${c.lecciones_aprende ? `<span class="a-chip mor">${c.lecciones_aprende} en Aprende</span>` : ""}</span></span></button>`;
  const panel = datosCursos.cursos.filter((c) => c.origen === "panel"), fabrica = datosCursos.cursos.filter((c) => c.origen !== "panel");
  vista.innerHTML = `${panel.length ? `<section class="a-sec"><div class="a-sec-cab"><h2>Creados por ti</h2></div><div class="a-rejilla">${panel.map(tarjeta).join("")}</div></section>` : ""}
    <section class="a-sec"><div class="a-sec-cab"><h2>De fábrica (${fabrica.length})</h2><span class="a-sub">Agrega, edita u oculta sus retos y lecciones</span></div><div class="a-rejilla">${fabrica.map(tarjeta).join("")}</div></section>`;
  $("nuevoCurso").addEventListener("click", () => formCurso());
}
function formCurso(c = null) {
  const motores = [["ver", "Solo ver el código (lenguajes nuevos)"], ["web", "HTML/CSS en vivo"], ["js", "JavaScript en el navegador"], ["py", "Python en el navegador"], ["sql", "SQL en el navegador"], ["ts", "TypeScript"], ["react", "React"], ["srv", "En el servidor (solo lenguajes de fábrica)"]];
  hojaForm({ titulo: c ? `Editar ${c.nombre}` : "Nuevo lenguaje", boton: c ? "Guardar" : "Crear lenguaje",
    cuerpo: `<div class="a-campos">
      ${c ? "" : campo("Identificador", '<input name="slug" required maxlength="30" placeholder="dart" pattern="[a-z][a-z0-9_-]+"><small>Minúsculas y sin espacios. No se puede cambiar después.</small>', "todo")}
      ${campo("Nombre", `<input name="nombre" required maxlength="40" value="${esc(c?.nombre || "")}" placeholder="Dart">`)}
      ${campo("Sigla", `<input name="sigla" required maxlength="6" value="${esc(c?.sigla || "")}" placeholder="DART">`)}
      ${campo("Color", `<input type="color" name="color" value="${esc(c?.color || "#4ade80")}">`)}
      ${campo("Tipo", `<select name="tipo">${opciones([["lenguaje", "Lenguaje"], ["web", "Web"], ["bd", "Base de datos"]], c?.tipo || "lenguaje")}</select>`)}
      ${campo("Cómo se ejecuta en Aprende", `<select name="motor">${opciones(motores, c?.motor || (c && c.origen !== "panel" ? "" : "ver"))}${c && !c.motor ? '<option value="" selected>Como viene de fábrica</option>' : ""}</select>`, "todo")}
      ${campo("Descripción", `<input name="descripcion" maxlength="120" value="${esc(c?.descripcion || "")}" placeholder="Apps para Android y iPhone con Flutter">`, "todo")}
      ${c ? campo("Orden en la lista", `<input type="number" name="orden" value="${c.orden}" min="0" max="999">`) : ""}
      <div class="todo">${interruptor("activo", "Visible para los estudiantes", c ? c.activo : true)}</div>
      ${c && c.origen !== "panel" ? '<p class="a-sub todo">Es un curso de fábrica: tus cambios de nombre y textos se respetan aunque se sincronice el catálogo.</p>' : ""}</div>`,
    enviar: async (v) => {
      if (!v.motor) delete v.motor;
      if (c) { await api(`/api/admin/cursos/${c.id}`, v, "PATCH"); toast("Curso guardado."); recargar(); }
      else { const r = await api("/api/admin/cursos", v); toast("¡Lenguaje creado! Ya aparece en Aprende y en Retos."); location.hash = `curso/${r.curso.id}`; }
    } });
}

async function curso(id) {
  const r = await api(`/api/admin/cursos/${id}/arbol`);
  const c = r.curso, ed = r.editable;
  cabecera(c.nombre, c.origen === "panel" ? "Creado en el panel · edítalo por completo" : "De fábrica · agrega, edita u oculta retos", `<a class="a-btn sm" href="#aprende/${encodeURIComponent(c.slug)}">📖 <span class="txt">Aprende</span></a><button class="a-btn sm" type="button" id="editarCurso">✏️ <span class="txt">Editar</span></button>`, "cursos");
  const tipoNivel = { leccion: ["📘", "Lección"], practica: ["🔁", "Práctica"], cofre: ["🎁", "Cofre"], trofeo: ["🏆", "Examen"] };
  vista.innerHTML = `<div class="a-ficha-cab"><span class="a-sigla" style="--c:${esc(c.color)};width:58px;height:58px">${esc(c.sigla)}</span><div><h2>${esc(c.nombre)}</h2>
      <div class="a-mini-stats">${c.origen === "panel" ? '<span class="a-chip verde">Creado en el panel</span>' : '<span class="a-chip">De fábrica</span>'}${c.activo ? '<span class="a-chip verde">visible</span>' : '<span class="a-chip rojo">oculto</span>'}<span class="a-chip cian">${c.niveles} niveles · ${c.retos} retos</span><span class="a-chip">/${esc(c.slug)}</span></div></div></div>
    ${ed ? "" : '<div class="a-aviso"><span>ℹ️</span><div><b>Curso de fábrica</b><p>Sus etapas y lecciones las define el código (cambiarlas movería el progreso de los estudiantes). Entra a una lección para agregar, editar u ocultar sus retos. Para un camino propio, crea un lenguaje nuevo.</p></div></div>'}
    <div class="a-sec-cab"><h2>Camino de retos</h2>${ed ? '<button class="a-btn sm pri" type="button" data-nuevo="etapa">＋ Etapa</button>' : ""}</div>
    <div class="a-arbol">${r.etapas.map((e) => `<section class="a-etapa"><div class="a-etapa-cab"><h3>Etapa ${e.orden} · ${esc(e.titulo)}</h3>${ed ? `<button class="a-btn sm ghost" type="button" data-editar="etapas/${e.id}" data-titulo="${esc(e.titulo)}">✏️</button><button class="a-btn sm ghost" type="button" data-borrar="etapas/${e.id}">🗑</button>` : ""}</div>
      ${e.secciones.map((s) => `<div class="a-seccion"><div class="a-seccion-cab"><h4>${esc(s.titulo)}</h4>${ed ? `<button class="a-btn sm ghost" type="button" data-editar="secciones/${s.id}" data-titulo="${esc(s.titulo)}">✏️</button><button class="a-btn sm ghost" type="button" data-borrar="secciones/${s.id}">🗑</button><button class="a-btn sm" type="button" data-nuevo="nivel" data-id="${s.id}">＋ Lección</button>` : ""}</div>
        <div class="a-niveles">${s.niveles.map((n) => `<button type="button" class="a-nivel" data-ir="nivel/${n.id}"><em>${tipoNivel[n.tipo]?.[0] || "📘"}</em><span>${esc(n.titulo)}</span>${n.tipo === "leccion" ? `<span class="a-chip">${n.retos} retos</span>` : `<span class="a-chip">${tipoNivel[n.tipo]?.[1] || n.tipo}</span>`}<span class="a-sub">›</span></button>`).join("") || '<p class="a-sub">Sin lecciones todavía.</p>'}</div></div>`).join("")}
      ${ed ? `<div class="a-seccion"><button class="a-btn sm ghost" type="button" data-nuevo="seccion" data-id="${e.id}">＋ Sección</button></div>` : ""}</section>`).join("") || vacio("🧩", "Este curso no tiene etapas todavía.")}</div>
    <section class="a-sec a-tarjeta"><div class="a-sec-cab"><h2>Zona de cuidado</h2></div>
      ${c.origen === "panel" ? '<button class="a-btn peligro" type="button" id="borrarCurso">🗑 Borrar curso (y el progreso de este curso)</button>' : `<button class="a-btn ${c.activo ? "peligro" : "ok"}" type="button" id="ocultarCurso">${c.activo ? "🙈 Ocultar curso" : "👁 Mostrar curso"}</button>`}</section>`;
  $("editarCurso").addEventListener("click", () => formCurso(c));
  $("borrarCurso")?.addEventListener("click", async () => {
    if (!(await confirmar(`¿Borrar «${c.nombre}»?`, { peligro: true, ok: "Borrar curso", detalle: "Se borran sus etapas, retos, lecciones de Aprende y el progreso de los estudiantes en este curso." }))) return;
    await api(`/api/admin/cursos/${id}`, null, "DELETE").catch(fallo); toast("Curso borrado."); location.hash = "cursos";
  });
  $("ocultarCurso")?.addEventListener("click", async () => { await api(`/api/admin/cursos/${id}`, { activo: !c.activo }, "PATCH").catch(fallo); recargar(); });
  vista.onclick = async (e) => {
    const nuevo = e.target.closest("[data-nuevo]"), editar = e.target.closest("[data-editar]"), borrar = e.target.closest("[data-borrar]");
    if (nuevo?.dataset.nuevo === "etapa") hojaForm({ titulo: "Nueva etapa", boton: "Crear etapa", cuerpo: `<div class="a-campos">${campo("Título", '<input name="titulo" required maxlength="80" placeholder="Fundamentos">', "todo")}${campo("Descripción", '<input name="descripcion" maxlength="160">', "todo")}${campo("Primera sección", '<input name="seccion" maxlength="80" placeholder="Sección 1">', "todo")}</div>`,
      enviar: async (v) => { await api(`/api/admin/cursos/${id}/etapas`, v); toast("Etapa creada."); recargar(); } });
    else if (nuevo?.dataset.nuevo === "seccion") hojaForm({ titulo: "Nueva sección", boton: "Crear sección", cuerpo: campo("Título", '<input name="titulo" required maxlength="80" placeholder="Variables">'),
      enviar: async (v) => { await api(`/api/admin/etapas/${nuevo.dataset.id}/secciones`, v); toast("Sección creada."); recargar(); } });
    else if (nuevo?.dataset.nuevo === "nivel") hojaForm({ titulo: "Nueva lección", boton: "Crear lección", cuerpo: `<div class="a-campos">${campo("Título", '<input name="titulo" required maxlength="80" placeholder="Tu primera variable">', "todo")}
        ${campo("Tipo", `<select name="tipo">${opciones([["leccion", "📘 Lección (con sus retos)"], ["practica", "🔁 Práctica (repasa lo visto)"], ["cofre", "🎁 Cofre"], ["trofeo", "🏆 Examen de la etapa"]], "leccion")}</select>`)}
        ${campo("XP al completarla", '<input type="number" name="xp" value="15" min="1" max="200">')}</div>`,
      enviar: async (v) => { const res = await api(`/api/admin/secciones/${nuevo.dataset.id}/niveles`, v); toast("Lección creada. Ahora agrégale retos."); if (v.tipo === "leccion") location.hash = `nivel/${res.id}`; else recargar(); } });
    else if (editar) hojaForm({ titulo: "Cambiar título", cuerpo: campo("Título", `<input name="titulo" required maxlength="80" value="${esc(editar.dataset.titulo)}">`),
      enviar: async (v) => { await api(`/api/admin/estructura/${editar.dataset.editar}`, v, "PATCH"); toast("Guardado."); recargar(); } });
    else if (borrar) {
      if (!(await confirmar("¿Borrar esta parte del camino?", { peligro: true, ok: "Borrar", detalle: "Se borra con todo lo que tiene dentro (lecciones y retos) y el progreso de esas lecciones." }))) return;
      await api(`/api/admin/estructura/${borrar.dataset.borrar}`, null, "DELETE").then(() => { toast("Borrado."); recargar(); }).catch(fallo);
    }
  };
}

// ------------------------------------------------------------------------------- retos de una lección ----
const TIPOS_RETO = { opcion: "Opción múltiple", completar: "Completar", error: "Encontrar el error", ordenar: "Ordenar", parejas: "Unir parejas", armar: "Armar la línea" };
async function nivel(id) {
  const r = await api(`/api/admin/niveles/${id}/retos`);
  const n = r.nivel, esLeccion = n.tipo === "leccion";
  cabecera(n.titulo, esLeccion ? `${r.retos.length} retos` : "Toma sus preguntas de las lecciones", esLeccion ? '<button class="a-btn pri sm" type="button" id="nuevoReto">＋ <span class="txt">Nuevo reto</span></button>' : "", "<");
  const tarjeta = (x) => `<article class="a-reto ${x.oculto ? "oculto" : ""}" data-reto="${x.id}">
    <div class="a-reto-cab"><span class="a-chip cian">${esc(TIPOS_RETO[x.tipo] || x.tipo)}</span>${x.origen === "panel" ? '<span class="a-chip verde">Tuyo</span>' : '<span class="a-chip">De fábrica</span>'}${x.editado ? '<span class="a-chip ama">editado</span>' : ""}${x.oculto ? '<span class="a-chip rojo">oculto</span>' : ""}</div>
    <b>${esc(x.enunciado)}</b>${x.codigo ? `<pre>${esc(x.codigo)}</pre>` : ""}
    ${x.tipo === "opcion" ? `<ul>${x.opciones.map((o) => `<li class="${o === x.respuesta ? "bien" : ""}">${esc(o)}${o === x.respuesta ? " ✓" : ""}</li>`).join("")}</ul>` : ""}
    ${x.tipo === "completar" ? `<span class="a-sub">Respuesta: <b>${esc(x.respuesta.split("|").join(" · "))}</b></span>` : ""}
    ${x.tipo === "error" ? `<span class="a-sub">Error en la línea <b>${esc(x.respuesta)}</b></span>` : ""}
    ${x.tipo === "ordenar" ? `<ul>${(x.datos.piezas || []).map((o) => `<li>${esc(o)}</li>`).join("")}</ul>` : ""}
    ${x.tipo === "parejas" ? `<ul>${(x.datos.pares || []).map(([a, b]) => `<li>${esc(a)} → ${esc(b)}</li>`).join("")}</ul>` : ""}
    ${x.tipo === "armar" ? `<span class="a-sub">Solución: <b>${esc((x.datos.solucion || []).join(" "))}</b>${x.datos.trampas?.length ? ` · trampas: ${esc(x.datos.trampas.join(", "))}` : ""}</span>` : ""}
    ${x.explicacion ? `<span class="a-sub">💡 ${esc(x.explicacion)}</span>` : ""}
    <div class="a-chips" style="gap:6px">${TIPOS_RETO[x.tipo] ? '<button class="a-btn sm" type="button" data-r="editar">✏️ Editar</button>' : '<span class="a-sub">Este tipo se edita en el código.</span>'}
      ${x.oculto || x.editado ? '<button class="a-btn sm ok" type="button" data-r="restaurar">↩️ Restaurar original</button>' : ""}
      ${x.oculto ? "" : `<button class="a-btn sm ghost" type="button" data-r="borrar">${x.origen === "panel" ? "🗑 Borrar" : "🙈 Ocultar"}</button>`}</div></article>`;
  vista.innerHTML = esLeccion ? `<div class="a-lista" style="gap:10px">${r.retos.map(tarjeta).join("") || vacio("🧩", "Esta lección aún no tiene retos. Crea el primero.")}</div>`
    : vacio("🔁", "Las prácticas, cofres y exámenes toman sus preguntas de las lecciones de la etapa. Agrega retos a las lecciones.");
  $("nuevoReto")?.addEventListener("click", () => formReto(id));
  vista.onclick = async (e) => {
    const b = e.target.closest("[data-r]");
    if (!b) return;
    const x = r.retos.find((y) => String(y.id) === b.closest("[data-reto]").dataset.reto);
    try {
      if (b.dataset.r === "editar") formReto(id, x);
      else if (b.dataset.r === "restaurar") { await api(`/api/admin/retos/${x.id}/restaurar`, {}); toast(x.editado ? "Se mostrará el texto original en la próxima sincronización." : "Reto visible otra vez."); recargar(); }
      else if (await confirmar(x.origen === "panel" ? "¿Borrar este reto?" : "¿Ocultar este reto de fábrica?", { peligro: x.origen === "panel", ok: x.origen === "panel" ? "Borrar" : "Ocultar", detalle: x.origen === "panel" ? "" : "Se puede restaurar cuando quieras." })) {
        await api(`/api/admin/retos/${x.id}`, null, "DELETE"); toast("Listo."); recargar();
      }
    } catch (y) { fallo(y); }
  };
}

function formReto(nivelId, x = null) {
  let tipo = x?.tipo || "opcion";
  const d = x?.datos || {};
  const filaOpcion = (texto = "", bien = false) => `<div class="a-opcion"><input type="radio" name="correcta" ${bien ? "checked" : ""} title="Respuesta correcta"><input data-op value="${esc(texto)}" placeholder="Opción"><button type="button" class="a-icono" data-quitar-op aria-label="Quitar">✕</button></div>`;
  const campos = {
    opcion: () => `${campo("Opciones (marca la correcta)", `<div class="a-lista" id="ops">${(x?.tipo === "opcion" ? x.opciones : ["", "", ""]).map((o) => filaOpcion(o, x?.respuesta === o && !!o)).join("")}</div><button type="button" class="a-btn sm ghost" id="masOp" style="justify-self:start">＋ Opción</button>`, "todo")}`,
    completar: () => campo("Respuestas aceptadas", `<input name="respuesta" value="${esc(x?.tipo === "completar" ? x.respuesta : "")}" placeholder="print|print()"><small>Separa varias respuestas válidas con |. En el código usa ___ para el hueco.</small>`, "todo"),
    error: () => campo("Número de la línea con el error", `<input type="number" name="respuesta" min="1" value="${esc(x?.tipo === "error" ? x.respuesta : "1")}">`),
    ordenar: () => campo("Piezas en el orden correcto (una por línea)", `<textarea name="piezas" class="codigo">${esc((d.piezas || []).join("\n"))}</textarea>`, "todo"),
    parejas: () => campo("Parejas (una por línea: izquierda = derecha)", `<textarea name="pares">${esc((d.pares || []).map(([a, b]) => `${a} = ${b}`).join("\n"))}</textarea><small>Mínimo 3, sin repetir textos.</small>`, "todo"),
    armar: () => `${campo("Fichas de la solución (en orden, una por línea)", `<textarea name="solucion" class="codigo">${esc((d.solucion || []).join("\n"))}</textarea><small>En el código pon ▁▁▁ donde va la línea a armar.</small>`, "todo")}${campo("Fichas trampa (una por línea)", `<textarea name="trampas" class="codigo">${esc((d.trampas || []).join("\n"))}</textarea>`, "todo")}`,
  };
  const pintar = (form) => {
    form.querySelector("#camposTipo").innerHTML = campos[tipo]();
    form.querySelectorAll("#segTipo button").forEach((b) => b.classList.toggle("on", b.dataset.t === tipo));
  };
  hojaForm({ titulo: x ? "Editar reto" : "Nuevo reto", boton: x ? "Guardar reto" : "Crear reto", ancha: true,
    cuerpo: `${x ? "" : `<div class="a-seg" id="segTipo" style="margin-bottom:14px">${Object.entries(TIPOS_RETO).map(([k, t]) => `<button type="button" data-t="${k}">${t}</button>`).join("")}</div>`}
      <div class="a-campos">${campo("Enunciado (la pregunta)", `<textarea name="enunciado" required>${esc(x?.enunciado || "")}</textarea>`, "todo")}
      ${campo("Código (opcional)", `<textarea name="codigo" class="codigo" spellcheck="false">${esc(x?.codigo || "")}</textarea>`, "todo")}
      <div class="todo a-campos" id="camposTipo"></div>
      ${campo("Explicación de la respuesta correcta", `<textarea name="explicacion">${esc(x?.explicacion || "")}</textarea>`, "todo")}</div>`,
    alAbrir: (form) => {
      pintar(form);
      form.addEventListener("click", (e) => {
        const t = e.target.closest("#segTipo [data-t]");
        if (t) { tipo = t.dataset.t; pintar(form); }
        if (e.target.closest("#masOp")) form.querySelector("#ops").insertAdjacentHTML("beforeend", filaOpcion());
        if (e.target.closest("[data-quitar-op]")) e.target.closest(".a-opcion").remove();
      });
    },
    enviar: async (v, form) => {
      const reto = { tipo, enunciado: v.enunciado, codigo: v.codigo, explicacion: v.explicacion, opciones: [], respuesta: "", datos: {} };
      if (tipo === "opcion") {
        const filas = [...form.querySelectorAll(".a-opcion")];
        reto.opciones = filas.map((f) => f.querySelector("[data-op]").value.trim()).filter(Boolean);
        const marcada = filas.find((f) => f.querySelector("[type=radio]").checked);
        reto.respuesta = marcada ? marcada.querySelector("[data-op]").value.trim() : "";
        if (!reto.respuesta) throw new Error("Marca cuál es la opción correcta.");
      } else if (tipo === "completar" || tipo === "error") reto.respuesta = v.respuesta;
      else if (tipo === "ordenar") reto.datos = { piezas: lineas(v.piezas) };
      else if (tipo === "parejas") reto.datos = { pares: lineas(v.pares).map((l) => l.split("=").map((s) => s.trim())).filter((p) => p.length === 2 && p[0] && p[1]) };
      else if (tipo === "armar") reto.datos = { solucion: lineas(v.solucion), trampas: lineas(v.trampas) };
      if (x) await api(`/api/admin/retos/${x.id}`, reto, "PATCH"); else await api(`/api/admin/niveles/${nivelId}/retos`, reto);
      toast(x ? "Reto guardado." : "Reto creado.");
      recargar();
    } });
}

// ------------------------------------------------------------------------------- Aprende ----
const CAMPOS_LEC = [["t", "Título", "input"], ["m", "Módulo o etapa", "input"], ["x", "¿Qué es?", "textarea"], ["u", "¿Para qué sirve?", "textarea"],
  ["p", "Puntos clave (uno por línea)", "lista"], ["c", "Código de ejemplo", "codigo"], ["h", "¿Qué hace el ejemplo?", "textarea"], ["r", "Ahora tú (práctica)", "textarea"],
  ["e", "Error común", "textarea"], ["q", "Reto rápido (pregunta)", "input"], ["a", "Respuesta del reto", "input"]];
async function aprende(slug) {
  const { cursos: lista } = datosCursos || await api("/api/admin/cursos");
  const c = lista.find((x) => x.slug === slug);
  if (!c) throw new Error("Ese curso no existe.");
  const [base, { lecciones: panel }] = await Promise.all([import(`/js/lecciones/${slug}.js`).then((m) => m.default).catch(() => []), api(`/api/admin/aprende/${encodeURIComponent(slug)}`)]);
  cabecera(`Aprende · ${c.nombre}`, `${base.length} lecciones de fábrica · ${panel.filter((p) => !p.reemplaza).length} tuyas`, `<a class="a-btn sm ghost" href="/pages/aprende.html#${encodeURIComponent(slug)}" target="_blank" rel="noopener">👁 <span class="txt">Ver</span></a><button class="a-btn pri sm" type="button" id="nuevaLec">＋ <span class="txt">Nueva lección</span></button>`, `curso/${c.id}`);
  const ocultas = new Map(panel.filter((x) => x.oculta && x.reemplaza).map((x) => [x.reemplaza, x]));
  const reemplazos = new Map(panel.filter((x) => !x.oculta && x.reemplaza).map((x) => [x.reemplaza, x]));
  // Lista como la verá el estudiante (las ocultas se muestran apagadas para poder restaurarlas)
  const filas = base.map((o) => ({ original: o, panel: reemplazos.get(o.t) || ocultas.get(o.t) || null, oculta: ocultas.has(o.t) }));
  for (const x of panel.filter((y) => !y.reemplaza && !y.oculta)) {
    const visibles = filas.filter((f) => !f.oculta);
    const destino = Math.min(x.posicion ?? visibles.length, visibles.length);
    const antes = visibles[destino];
    filas.splice(antes ? filas.indexOf(antes) : filas.length, 0, { nueva: x });
  }
  let n = 0;
  vista.innerHTML = `<div class="a-aviso"><span>📖</span><div><b>Lecciones de teoría de ${esc(c.nombre)}</b><p>Edita las de fábrica (tu versión las reemplaza), ocúltalas o crea nuevas en la posición que quieras.</p></div></div>
    <div class="a-lista" style="gap:8px">${filas.map((f, i) => {
      const lec = f.nueva || (f.panel && !f.oculta ? f.panel : f.original);
      const chip = f.nueva ? '<span class="a-chip verde">Nueva</span>' : f.oculta ? '<span class="a-chip rojo">Oculta</span>' : f.panel ? '<span class="a-chip ama">Editada</span>' : "";
      return `<div class="a-leccion ${f.oculta ? "oculta" : ""}" data-i="${i}"><span class="n">${f.oculta ? "–" : ++n}</span><span><b>${esc(lec.t)}</b><small>${esc(lec.m || "")}</small></span>${chip}
        <span class="a-acc">${f.oculta ? '<button class="a-btn sm ok" type="button" data-l="mostrar">👁 Mostrar</button>' : '<button class="a-btn sm" type="button" data-l="editar">✏️</button>'}
        ${f.nueva ? '<button class="a-btn sm ghost" type="button" data-l="borrar">🗑</button>' : f.oculta ? "" : f.panel ? '<button class="a-btn sm ghost" type="button" data-l="original" title="Volver a la original">↩️</button><button class="a-btn sm ghost" type="button" data-l="ocultar">🙈</button>' : '<button class="a-btn sm ghost" type="button" data-l="ocultar" title="Ocultar">🙈</button>'}</span></div>`;
    }).join("") || vacio("📖", "Este lenguaje aún no tiene lecciones. Crea la primera.")}</div>`;
  const visiblesTitulos = filas.filter((f) => !f.oculta).map((f) => (f.nueva || f.panel || f.original).t);
  $("nuevaLec").addEventListener("click", () => formLeccion(slug, null, { posiciones: visiblesTitulos }));
  vista.onclick = async (e) => {
    const b = e.target.closest("[data-l]");
    if (!b) return;
    const f = filas[Number(b.closest("[data-i]").dataset.i)];
    try {
      if (b.dataset.l === "editar") formLeccion(slug, f.nueva || f.panel || null, { original: f.nueva ? null : f.original });
      else if (b.dataset.l === "ocultar") { if (f.panel) await api(`/api/admin/aprende/leccion/${f.panel.id}`, null, "DELETE"); await api(`/api/admin/aprende/${encodeURIComponent(slug)}`, { reemplaza: f.original.t, oculta: true }); toast("Lección oculta."); recargar(); }
      else if (b.dataset.l === "mostrar" || b.dataset.l === "original") { await api(`/api/admin/aprende/leccion/${f.panel.id}`, null, "DELETE"); toast(b.dataset.l === "original" ? "Volvió la lección original." : "Lección visible."); recargar(); }
      else if (b.dataset.l === "borrar" && await confirmar("¿Borrar esta lección?", { peligro: true, ok: "Borrar" })) { await api(`/api/admin/aprende/leccion/${f.nueva.id}`, null, "DELETE"); toast("Lección borrada."); recargar(); }
    } catch (y) { fallo(y); }
  };
}
function formLeccion(slug, x, { original = null, posiciones = null } = {}) {
  const base = x || original || {};
  hojaForm({ titulo: x ? "Editar lección" : original ? "Editar lección de fábrica" : "Nueva lección", boton: "Guardar lección", ancha: true,
    cuerpo: `${original && !x ? '<p class="a-sub" style="margin-bottom:12px">Tu versión reemplaza a la original (puedes volver a ella cuando quieras).</p>' : ""}<div class="a-campos">
      ${posiciones ? campo("Posición", `<select name="posicion"><option value="">Al final</option>${posiciones.map((t, i) => `<option value="${i}">Antes de «${esc(t)}»</option>`).join("")}</select>`, "todo") : ""}
      ${CAMPOS_LEC.map(([k, t, tipo]) => campo(t, tipo === "input" ? `<input name="${k}" value="${esc(base[k] || "")}" ${k === "t" ? "required maxlength=\"120\"" : ""}>`
        : tipo === "lista" ? `<textarea name="${k}">${esc((base[k] || []).join("\n"))}</textarea>`
        : `<textarea name="${k}" ${tipo === "codigo" ? 'class="codigo" spellcheck="false"' : ""}>${esc(base[k] || "")}</textarea>`, ["x", "u", "c", "p", "h", "r", "e"].includes(k) ? "todo" : "")).join("")}</div>`,
    enviar: async (v) => {
      v.p = lineas(v.p);
      if (x) await api(`/api/admin/aprende/leccion/${x.id}`, v, "PATCH");
      else await api(`/api/admin/aprende/${encodeURIComponent(slug)}`, { ...v, reemplaza: original?.t || null });
      toast("Lección guardada."); recargar();
    } });
}

// =============================================================================== tienda ====
let vigia = null;
function vistasPerezosas(raiz) {
  vigia?.disconnect();
  vigia = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { vigia.unobserve(e.target); const el = e.target; try { vistaPrevia(el, el.dataset.prev, el.dataset.tipo); } catch { /* nada */ } } }), { rootMargin: "200px" });
  raiz.querySelectorAll("[data-prev]").forEach((el) => vigia.observe(el));
}
async function tienda(filtro = "todos", q = "") {
  cabecera("Artículos de la tienda", "Precios, nombres, rarezas y visibilidad de todo", `<a class="a-btn sm" href="#disenar">🎨 <span class="txt">Diseñar</span></a><button class="a-btn pri sm" type="button" id="nuevoArt">＋ <span class="txt">Con premios</span></button>`);
  const [{ articulos }, { medallas: ms }, cat] = await Promise.all([api("/api/admin/tienda"), api("/api/admin/medallas"), traerCatalogo()]);
  registrarDisenos(cat.disenados.map((d) => ({ clave: d.clave, tipo: d.tipo, diseno: d.diseno })));
  const filtros = [["todos", "Todos"], ...Object.entries(TIPOS_COS), ["potenciador", "Potenciadores"], ["panel", "Creados por ti"], ["ocultos", "Ocultos"]];
  const pasa = (a) => (filtro === "todos" ? !a.oculto : filtro === "ocultos" ? !a.activo || a.oculto : filtro === "panel" ? a.origen !== "fabrica"
    : filtro === "potenciador" ? !TIPOS_COS[a.tipo] : a.tipo === filtro) && (!q || `${a.nombre} ${a.descripcion} ${a.clave}`.toLowerCase().includes(q.toLowerCase()));
  const lista = articulos.filter(pasa);
  const origen = { fabrica: "", panel: '<span class="a-chip verde">Con premios</span>', diseno: '<span class="a-chip verde">Diseñado</span>' };
  vista.innerHTML = `<div class="a-herr"><div class="a-buscar"><input id="qT" type="search" placeholder="Buscar artículo" value="${esc(q)}"></div></div>
    <div class="a-seg" id="filtroT" style="margin-bottom:14px">${filtros.map(([v, t]) => `<button type="button" data-v="${v}" class="${v === filtro ? "on" : ""}">${t}</button>`).join("")}</div>
    <div class="a-articulos">${lista.map((a) => `<article class="a-articulo ${a.activo ? "" : "apagado"}" data-art="${a.id}">
      ${TIPOS_COS[a.tipo] && a.tipo !== "codi" ? `<div class="vista" data-prev="${esc(a.clave)}" data-tipo="${esc(a.tipo)}"></div>` : a.extra?.imagen ? `<div class="a-articulo-ico"><img src="${esc(a.extra.imagen)}" alt="" style="width:76px;height:76px;object-fit:contain"></div>` : `<div class="a-articulo-ico">${esc(TIPOS_COS[a.tipo] ? "🤖" : a.icono || "🎁")}</div>`}
      <div class="a-articulo-cuerpo"><b>${esc(a.nombre)}</b><div class="a-chips">${rareza(a.rareza)}<span class="a-chip">${esc(TIPO_UNO[a.tipo] || a.tipo)}</span>${origen[a.origen]}${a.ajustado ? '<span class="a-chip ama">editado</span>' : ""}${a.activo ? "" : '<span class="a-chip rojo">oculto</span>'}</div>
        <p>${esc(a.descripcion)}</p><div style="display:flex;justify-content:space-between;gap:8px"><span class="a-precio">💎 ${num(a.precio)}</span><span class="a-sub" style="font-size:12.5px">${a.vendidos} vendidos</span></div></div>
      <div class="a-articulo-pie"><button class="a-btn sm" type="button" data-a="editar">✏️ Editar</button>
        <button class="a-btn sm ghost" type="button" data-a="visible">${a.activo ? "🙈" : "👁"}</button>
        ${a.origen === "fabrica" ? (a.ajustado || a.oculto ? '<button class="a-btn sm ghost" type="button" data-a="restaurar" title="Volver a los valores de fábrica">↩️</button>' : "") : '<button class="a-btn sm ghost" type="button" data-a="borrar" title="Eliminar">🗑</button>'}</div></article>`).join("") || vacio("🛒", "No hay artículos con ese filtro.")}</div>`;
  vistasPerezosas(vista);
  $("filtroT").addEventListener("click", (e) => { const b = e.target.closest("[data-v]"); if (b) location.hash = `tienda/${b.dataset.v}/${encodeURIComponent(q)}`; });
  $("qT").addEventListener("change", (e) => { location.hash = `tienda/${filtro}/${encodeURIComponent(e.target.value.trim())}`; });
  $("nuevoArt").addEventListener("click", () => formArticulo(null, ms));
  vista.onclick = async (e) => {
    const b = e.target.closest("[data-a]");
    if (!b) return;
    const a = articulos.find((x) => String(x.id) === b.closest("[data-art]").dataset.art);
    try {
      if (b.dataset.a === "editar") formArticulo(a, ms);
      else if (b.dataset.a === "visible") { await api(`/api/admin/tienda/${a.id}`, { activo: !a.activo }, "PATCH"); toast(a.activo ? "Oculto de la tienda." : "Visible en la tienda."); recargar(); }
      else if (b.dataset.a === "restaurar") { await api(`/api/admin/tienda/${a.id}/restaurar`, {}); toast("Volvió a los valores de fábrica."); recargar(); }
      else if (b.dataset.a === "borrar" && await confirmar(`¿Eliminar «${a.nombre}»?`, { peligro: true, ok: "Eliminar", detalle: a.origen === "diseno" ? "Se quita también a quienes lo tenían." : "Quien ya lo compró conserva lo que recibió." })) {
        await api(`/api/admin/tienda/${a.id}`, null, "DELETE"); catalogoCos = null; toast("Eliminado."); recargar();
      }
    } catch (y) { fallo(y); }
  };
}
function formArticulo(a, ms) {
  const premios = !a || a.origen === "panel";
  const ex = a?.extra || {};
  hojaForm({ titulo: a ? `Editar «${a.nombre}»` : "Nuevo artículo con premios", boton: a ? "Guardar" : "Crear artículo",
    cuerpo: `${a?.origen === "fabrica" ? '<p class="a-sub" style="margin-bottom:12px">Artículo de fábrica: tus cambios se guardan encima del código y puedes volver a los originales con ↩️.</p>' : ""}
      ${a?.origen === "diseno" ? `<p style="margin:0 0 12px"><a class="a-btn sm" href="#disenar/${esc(a.clave)}">🎨 Editar su diseño</a></p>` : ""}
      <div class="a-campos">
      ${campo("Nombre", `<input name="nombre" required maxlength="60" value="${esc(a?.nombre || "")}">`)}
      ${campo("Precio (💎)", `<input type="number" name="precio" min="0" max="1000000" value="${a?.precio ?? 100}">`)}
      ${campo("Rareza", `<select name="rareza">${opciones(Object.entries(RAREZAS), a?.rareza || "comun")}</select>`)}
      ${premios ? campo("Ícono (emoji)", `<input name="icono" maxlength="8" value="${esc(a?.icono || "🎁")}">`) : ""}
      ${campo("Descripción", `<textarea name="descripcion" maxlength="200">${esc(a?.descripcion || "")}</textarea>`, "todo")}
      ${premios ? `${campo("Da XP", `<input type="number" name="xp" min="0" value="${ex.xp || 0}">`)}${campo("Da vidas", `<input type="number" name="vidas" min="0" value="${ex.vidas || 0}">`)}
        ${campo("Da salvarrachas", `<input type="number" name="salvarrachas" min="0" value="${ex.salvarrachas || 0}">`)}
        ${campo("Da medalla", `<select name="medalla_id"><option value="">Ninguna</option>${ms.map((m) => `<option value="${m.id}" ${ex.medalla_id === m.id ? "selected" : ""}>${esc(m.icono)} ${esc(m.nombre)}</option>`).join("")}</select>`)}
        <div class="todo">${interruptor("permanente", "Solo se compra una vez", !!ex.permanente)}</div>` : ""}
      <div class="todo">${interruptor("activo", "Visible en la tienda", a ? a.activo : true)}</div></div>
      ${premios ? `<h3 style="margin:16px 0 10px;font-size:15px">Imagen y vitrina</h3><div class="a-campos" id="artImg"></div><div class="a-campos" id="artVit" style="margin-top:8px"></div>
        <div style="max-width:260px;margin:14px auto 0" id="artPrev"></div>` : ""}`,
    alAbrir: (form) => {
      if (!premios) return;
      const est = { imagen: ex.imagen || "", fuente: "", vitrina: { ...VIT_DEF, ...(ex.vitrina || {}) } };
      const previa = () => {
        const v = valores(form);
        const caja = form.querySelector("#artPrev");
        caja.innerHTML = `<div class="vit-card" data-base="rareza-${esc(v.rareza)}"><span class="producto-rango">${esc(RAREZAS[v.rareza] || "")}</span>
          <div class="vista ${est.imagen ? "vista-img" : ""}">${est.imagen ? `<img class="producto-img" src="${esc(est.imagen)}" alt="">` : `<span style="font-size:54px;line-height:130px">${esc(v.icono || "🎁")}</span>`}</div>
          <h3>${esc(v.nombre || "Sin nombre")}</h3><span class="vit-precio">💎 ${num(v.precio)}</span></div>`;
        adornarVitrina(caja.querySelector(".vit-card"), est.vitrina);
      };
      const pintar = () => {
        form.querySelector("#artImg").innerHTML = bloqueImagen(est.imagen, { texto: "Imagen (en vez del emoji)" });
        form.querySelector("#artVit").innerHTML = controlesVitrina(est.vitrina);
        previa();
      };
      form.__extra = est;
      pintar();
      form.addEventListener("click", async (e) => {
        const pa = e.target.closest("[data-parte] [data-v]");
    if (pa) { parteSel = pa.dataset.v; pintar(); return; }
    const ps = e.target.closest("[data-pseg] [data-v]");
    if (ps) { d.partes[parteSel][ps.closest("[data-pseg]").dataset.pseg] = ps.dataset.v; pintar(); return; }
    const vs = e.target.closest("[data-vseg] [data-v]");
        if (vs) { est.vitrina.efecto = vs.dataset.v; pintar(); }
        if (e.target.closest("[data-editar-img]")) { const u = await editarImagen(est.fuente || est.imagen, IMG_TIPO.articulo).catch((x) => { fallo(x); return null; }); if (u) { est.imagen = u; pintar(); } }
        if (e.target.closest("[data-quitar-img]")) { est.imagen = ""; est.fuente = ""; pintar(); }
      });
      form.addEventListener("input", (e) => {
        const k = e.target.dataset.vit;
        if (k === "aura_on") est.vitrina.aura = e.target.checked ? form.querySelector("[data-vit=aura]").value : "";
        else if (k === "aura") { est.vitrina.aura = e.target.value; form.querySelector("[data-vit=aura_on]").checked = true; }
        else if (k) est.vitrina[k] = e.target.checked;
        previa();
      });
      form.addEventListener("change", async (e) => {
        if (!e.target.matches("[data-subir]") || !e.target.files[0]) return;
        try { const r = await elegirYEditar(e.target.files[0], IMG_TIPO.articulo); if (r) { est.imagen = r.imagen; est.fuente = r.fuente; pintar(); } } catch (x) { fallo(x); }
        e.target.value = "";
      });
    },
    enviar: async (v, form) => {
      if (form.__extra) { v.imagen = form.__extra.imagen; v.vitrina = form.__extra.vitrina; }
      if (a) await api(`/api/admin/tienda/${a.id}`, v, "PATCH"); else await api("/api/admin/tienda", v);
      toast(a ? "Artículo guardado." : "Artículo creado."); recargar();
    } });
}

// =============================================================================== diseñador de cosméticos ====
const VIT_DEF = { efecto: "ninguno", aura: "", brillo: false, destellos: false };
const DIS_DEF = {
  fondo: { estilo: "aurora", colores: ["#0b1026", "#7c3aed", "#22d3ee"], imagen: "", animacion: "nieve", capa: "ninguna", oscurecer: 0, oscuro: true,
    modo: "cubrir", movil: "completa", mosaico: 160, movimiento: "ninguno", desenfoque: 0, stickers: [], lluvia: "ninguna", lluvia_emojis: "⭐ ✨ 💜", lluvia_cantidad: 18 },
  tema: { acc: "#f472b6", acc2: "#be185d", cy: "#38bdf8", fuente: "sistema", neon: false, fluir: false },
  marco: { estilo: "aro", colores: ["#22d3ee", "#a855f7", "#f472b6"], gira: true, velocidad: 5, brillo: true, imagen: "", grosor: 4, orbita: false, pulso: false, insignia: null },
  cursor: { tam: 32, partes: {
    normal: { tipo: "flecha_emoji", c1: "#ffffff", c2: "#0f172a", emoji: "🚀", forma: "estrella", punta: "esquina", imagen: "" },
    mano: { tipo: "mano", c1: "#ffffff", c2: "#0f172a", emoji: "👆", forma: "estrella", punta: "esquina", imagen: "" },
    texto: { tipo: "barra", c1: "#ffffff", c2: "#0f172a", emoji: "✏️", forma: "estrella", punta: "centro", imagen: "" } } },
  efecto: { forma: "estrella", emoji: "✨", emojis: "", palabras: "+1 ¡Bien! 💯", colores: ["#facc15", "#22d3ee", "#a855f7"], cantidad: 10, imagen: "", tam: 28 },
  dedo: { forma: "punto", emoji: "⭐", emojis: "", palabras: "✨", colores: ["#22d3ee", "#a855f7"], cantidad: 8, imagen: "", tam: 22, modo: "particulas" },
  teclado: { estilo: "plano", bg: "#1e293b", fg: "#e2e8f0", borde: "#334155", enter: "#6366f1", fondo: "#0f172a", imagen: "", chispas: false },
  codi: { imagen: "", capa: "cabeza", x: 100, y: 40, tam: 90, girar: 0, anim: "ninguna", sinAntena: false },
};
const ANIMS = [["ninguna", "Quieta"], ["flotar", "Flotar"], ["girar", "Girar"], ["latido", "Latido"], ["rebotar", "Rebotar"], ["balanceo", "Balanceo"], ["parpadeo", "Parpadeo"], ["cruzar", "Cruzar la pantalla"], ["caer", "Caer como lluvia"], ["orbitar", "Dar vueltas (órbita)"]];
// Plantillas «legendarias»: un clic y queda un diseño completo (luego se ajusta lo que quieras)
const LEG = { efecto: "inclinar", brillo: true, destellos: true };
const PLANTILLAS = {
  fondo: [
    ["Nebulosa viva", ["#05010f", "#7c3aed", "#ec4899", "#22d3ee"], { estilo: "aurora", animacion: "nebulosa", capa: "estrellas", oscuro: true, vitrina: { ...LEG, aura: "#a855f7" } }],
    ["Synthwave", ["#12002b", "#5b21b6", "#f472b6"], { estilo: "lineal", animacion: "fugaces", capa: "rejilla", oscuro: true, vitrina: { ...LEG, aura: "#f472b6" } }],
    ["Hiperespacio", ["#000000", "#0c4a6e", "#38bdf8"], { estilo: "radial", animacion: "hiper", capa: "vineta", oscuro: true, vitrina: { ...LEG, aura: "#38bdf8" } }],
    ["Código Matrix", ["#000000", "#052e16", "#22c55e"], { estilo: "lineal", animacion: "matrix", capa: "escaneo", oscuro: true, vitrina: { efecto: "flotar", aura: "#22c55e", brillo: true, destellos: false } }],
    ["Agujero negro", ["#000000", "#1e1b4b", "#f59e0b"], { estilo: "radial", animacion: "agujero", capa: "brillo", oscuro: true, vitrina: { ...LEG, aura: "#f59e0b" } }],
    ["Lluvia de código", ["#020617", "#0f172a", "#38bdf8"], { estilo: "lineal", animacion: "ninguna", capa: "vineta", lluvia: "cae", lluvia_emojis: "0 1 </> {} ; ( ) =>", lluvia_cantidad: 30, oscuro: true, vitrina: { efecto: "flotar", aura: "#38bdf8", brillo: true, destellos: false } }],
    ["Fiesta de pizza", ["#7c2d12", "#ea580c", "#fde047"], { estilo: "diagonal", animacion: "ninguna", capa: "ninguna", lluvia: "remolino", lluvia_emojis: "🍕 🧀 🍅", lluvia_cantidad: 16, oscuro: true, vitrina: { efecto: "latido", aura: "#fde047", brillo: true, destellos: true } }],
    ["Burbujas mágicas", ["#0c4a6e", "#7c3aed", "#f0abfc"], { estilo: "aurora", animacion: "ninguna", capa: "brillo", lluvia: "sube", lluvia_emojis: "🫧 ✨ 💜 🦄", lluvia_cantidad: 22, oscuro: true, vitrina: { ...LEG, aura: "#f0abfc" } }],
  ],
  tema: [
    ["Arcade", ["#f43f5e", "#22d3ee", "#facc15"], { acc: "#f43f5e", acc2: "#9f1239", cy: "#22d3ee", fuente: "pixel", neon: true, fluir: true, vitrina: { ...LEG, aura: "#f43f5e" } }],
    ["Cuaderno", ["#2563eb", "#93c5fd", "#fbbf24"], { acc: "#2563eb", acc2: "#1e3a8a", cy: "#f59e0b", fuente: "manuscrita", neon: false, fluir: false, vitrina: { efecto: "flotar", aura: "", brillo: false, destellos: false } }],
    ["Hacker", ["#22c55e", "#14532d", "#a3e635"], { acc: "#22c55e", acc2: "#14532d", cy: "#a3e635", fuente: "mono", neon: true, fluir: false, vitrina: { efecto: "inclinar", aura: "#22c55e", brillo: true, destellos: false } }],
    ["Realeza", ["#a855f7", "#f59e0b", "#fde68a"], { acc: "#a855f7", acc2: "#581c87", cy: "#f59e0b", fuente: "elegante", neon: false, fluir: true, vitrina: { ...LEG, aura: "#f59e0b" } }],
  ],
  marco: [
    ["Plasma", ["#f0abfc", "#6366f1", "#22d3ee", "#a3e635"], { estilo: "holo", gira: true, velocidad: 8, brillo: true, grosor: 5, orbita: true, pulso: false, vitrina: { ...LEG, aura: "#6366f1" } }],
    ["Neón cian", ["#22d3ee", "#a855f7"], { estilo: "neon", gira: false, velocidad: 4, brillo: true, grosor: 3, orbita: false, pulso: true, vitrina: { efecto: "latido", aura: "#22d3ee", brillo: true, destellos: false } }],
    ["Fuego azul", ["#0ea5e9", "#2563eb", "#e0f2fe"], { estilo: "fuego", gira: true, velocidad: 9, brillo: true, grosor: 5, orbita: false, pulso: false, vitrina: { ...LEG, aura: "#0ea5e9" } }],
    ["Diamante", ["#ecfeff", "#67e8f9", "#ffffff", "#a5f3fc"], { estilo: "aro", gira: true, velocidad: 6, brillo: true, grosor: 5, orbita: true, pulso: true, vitrina: { ...LEG, aura: "#a5f3fc" } }],
    ["Oro del jefe", ["#78350f", "#f59e0b", "#fde68a", "#d97706"], { estilo: "holo", gira: true, velocidad: 5, brillo: true, grosor: 6, orbita: true, pulso: true, vitrina: { ...LEG, aura: "#f59e0b" } }],
  ],
  teclado: [
    ["Teclas 3D", ["#334155"], { estilo: "3d", bg: "#334155", fg: "#f8fafc", borde: "#0f172a", enter: "#22c55e", fondo: "#0b1120", chispas: true, vitrina: { efecto: "inclinar", aura: "", brillo: true, destellos: false } }],
    ["Neón", ["#0f172a"], { estilo: "neon", bg: "#0f172a", fg: "#67e8f9", borde: "#22d3ee", enter: "#f472b6", fondo: "#020617", chispas: true, vitrina: { ...LEG, aura: "#22d3ee" } }],
    ["Cristal", ["#e0f2fe"], { estilo: "cristal", bg: "#e0f2fe", fg: "#0f172a", borde: "#bae6fd", enter: "#38bdf8", fondo: "#1e3a8a", chispas: false, vitrina: { efecto: "flotar", aura: "#bae6fd", brillo: true, destellos: false } }],
    ["Arcoíris", ["#ffffff"], { estilo: "arcoiris", bg: "#1e293b", fg: "#ffffff", borde: "#ffffff", enter: "#facc15", fondo: "#0f172a", chispas: true, vitrina: { ...LEG, aura: "#f472b6" } }],
  ],
  efecto: [
    ["Fuegos artificiales", ["#f43f5e", "#facc15", "#22d3ee", "#a855f7", "#84cc16"], { forma: "estrella", cantidad: 18, vitrina: { ...LEG, aura: "#facc15" } }],
    ["Lluvia de monedas", ["#facc15", "#f59e0b"], { forma: "moneda", cantidad: 14, vitrina: { efecto: "latido", aura: "#f59e0b", brillo: true, destellos: true } }],
    ["Corazones", ["#f43f5e", "#f472b6", "#fda4af"], { forma: "corazon", cantidad: 12, vitrina: { efecto: "flotar", aura: "#f472b6", brillo: true, destellos: false } }],
    ["Palabras de ánimo", ["#facc15", "#22d3ee", "#f472b6"], { forma: "texto", palabras: "+1 ¡Bien! 💯 ¡Crack! ¡Eso!", cantidad: 9, vitrina: { efecto: "latido", aura: "#facc15", brillo: true, destellos: false } }],
    ["Onda neón", ["#22d3ee", "#a855f7", "#f472b6"], { forma: "onda", cantidad: 3, vitrina: { efecto: "inclinar", aura: "#22d3ee", brillo: true, destellos: false } }],
    ["Explosión de emojis", ["#facc15"], { forma: "emoji", emojis: "🎉 🚀 💥 ⭐ 🔥", cantidad: 14, vitrina: { ...LEG, aura: "#f97316" } }],
  ],
  dedo: [
    ["Polvo de estrellas", ["#e0f2fe", "#a78bfa", "#fde047"], { forma: "estrella", vitrina: { ...LEG, aura: "#a78bfa" } }],
    ["Píxeles arcoíris", ["#f43f5e", "#f59e0b", "#84cc16", "#22d3ee", "#a855f7"], { forma: "pixel", vitrina: { efecto: "inclinar", aura: "#22d3ee", brillo: true, destellos: false } }],
  ],
};
const NOMBRES_ANIM = { ninguna: "Sin animación", aurora: "Aurora (se mueve el degradado)", nieve: "Nieve", luciernagas: "Luciérnagas", lluvia: "Lluvia", burbujas: "Burbujas", sakura: "Pétalos de sakura", fugaces: "Estrellas fugaces", matrix: "Lluvia de código", hiper: "Hiperespacio", nebulosa: "Nebulosa", agujero: "Agujero negro" };
const NOMBRES_FORMA = { punto: "Puntos de luz", estrella: "Estrellas", burbuja: "Burbujas", cuadro: "Confeti", corazon: "Corazones", moneda: "Monedas", pixel: "Píxeles", emoji: "Emojis", imagen: "Tu imagen o GIF", texto: "Palabras (+1, ¡Bien!, 💯…)", onda: "Onda expansiva" };
const NOMBRES_CAPA = { ninguna: "Ninguna", vineta: "Viñeta (bordes oscuros)", rejilla: "Rejilla synthwave", estrellas: "Cielo estrellado", escaneo: "Líneas de pantalla retro", brillo: "Resplandor arriba" };
const NOMBRES_VIT = [["ninguno", "Quieto"], ["inclinar", "🧊 Inclinar 3D"], ["flotar", "🎈 Flotar"], ["girar", "🪙 Girar 3D"], ["latido", "💓 Latido"]];
// Tamaño y formato de la imagen que se usa en cada tipo
const IMG_TIPO = {
  fondo: { titulo: "Imagen de fondo", salida: [1600, 1000], formato: "jpg" },
  marco: { titulo: "Imagen del aro", salida: [256, 256], formas: true, forma: "circulo" },
  cursor: { titulo: "Imagen del puntero", salida: [48, 48], formas: true },
  efecto: { titulo: "Imagen de las partículas", salida: [96, 96], formas: true },
  dedo: { titulo: "Imagen del rastro", salida: [96, 96], formas: true },
  teclado: { titulo: "Imagen detrás del teclado", salida: [1200, 520], formato: "jpg" },
  articulo: { titulo: "Imagen del artículo", salida: [320, 320], formas: true, forma: "redondo" },
  sticker: { titulo: "Sticker o GIF para el fondo", salida: [512, 512], formas: true },
  insignia: { titulo: "Insignia del marco", salida: [256, 256], formas: true },
  codi: { titulo: "Accesorio de Codi", salida: [400, 400], formas: true },
  mascota: { titulo: "Mascota que sigue al mouse", salida: [256, 256], formas: true },
};

/** Clases de la vitrina (las mismas que usa la tienda). */
function clasesVitrina(v = {}) {
  const c = [];
  if (v.efecto && v.efecto !== "ninguno") c.push(`vit-${v.efecto}`, ...(v.efecto === "inclinar" && matchMedia("(pointer: coarse)").matches ? ["vit-balanceo"] : []));
  if (/^#[0-9a-f]{6}$/i.test(v.aura || "")) c.push("vit-aura");
  if (v.brillo) c.push("vit-brillo");
  if (v.destellos) c.push("vit-destellos");
  return c;
}
function adornarVitrina(card, v = {}) {
  card.className = `vit-card ${card.dataset.base || ""} ${clasesVitrina(v).join(" ")}`;
  card.style.setProperty("--vit-aura", /^#[0-9a-f]{6}$/i.test(v.aura || "") ? v.aura : "");
  card.querySelectorAll(".vit-destello").forEach((x) => x.remove());
  if (v.destellos) for (let i = 0; i < 6; i++) { const s = document.createElement("span"); s.className = "vit-destello"; s.style.cssText = `left:${8 + i * 15}%;bottom:${8 + (i % 3) * 14}%;animation-delay:${(i * 0.42).toFixed(2)}s`; card.append(s); }
  card.onpointermove = v.efecto === "inclinar" ? (e) => { if (e.pointerType !== "mouse") return; const r = card.getBoundingClientRect(); card.style.setProperty("--ry", `${((e.clientX - r.left) / r.width - 0.5) * 22}deg`); card.style.setProperty("--rx", `${(0.5 - (e.clientY - r.top) / r.height) * 18}deg`); } : null;
  card.onpointerleave = () => { card.style.removeProperty("--rx"); card.style.removeProperty("--ry"); };
}
/** Controles de la vitrina (cómo se presenta en la tienda). */
function controlesVitrina(v) {
  return `${campo("Movimiento en la tienda", `<div class="a-seg" data-vseg="efecto">${NOMBRES_VIT.map(([k, t]) => `<button type="button" data-v="${k}" class="${v.efecto === k ? "on" : ""}">${t}</button>`).join("")}</div>`, "todo")}
    <div class="a-interruptor-color"><label class="a-interruptor"><input type="checkbox" data-vit="aura_on" ${v.aura ? "checked" : ""}> Aura de color</label><input type="color" data-vit="aura" value="${esc(v.aura || "#facc15")}"></div>
    <div>${`<label class="a-interruptor"><input type="checkbox" data-vit="brillo" ${v.brillo ? "checked" : ""}> Brillo holográfico</label>`}</div>
    <div>${`<label class="a-interruptor"><input type="checkbox" data-vit="destellos" ${v.destellos ? "checked" : ""}> Destellos que suben</label>`}</div>`;
}
/** Bloque para subir, editar o quitar una imagen. */
function bloqueImagen(url, { redondo = false, texto = "Imagen", clave = "imagen", ayuda = "PNG, JPG, WEBP o GIF animado · hasta 4 MB · se recorta y se ajusta en el editor" } = {}) {
  return campo(texto, `<div class="a-subir">${url ? `<img src="${esc(url)}" alt=""${redondo ? ' class="redondo"' : ""}>` : ""}
    <label class="a-btn sm">📤 ${url ? "Cambiar" : "Subir"}<input type="file" data-subir="${clave}" accept="image/png,image/jpeg,image/webp,image/gif" hidden></label>
    ${url ? `<button type="button" class="a-btn sm" data-editar-img="${clave}">✏️ Editar</button><button type="button" class="a-btn sm ghost" data-quitar-img="${clave}">Quitar</button>` : ""}
    <small>${ayuda}</small></div>`, "todo");
}

async function disenar(clave = "") {
  catalogoCos = null;
  const cat = await traerCatalogo();
  registrarDisenos(cat.disenados.map((d) => ({ clave: d.clave, tipo: d.tipo, diseno: d.diseno })));
  const actual = cat.disenados.find((d) => d.clave === clave) || null;
  let tipo = actual?.tipo || "fondo";
  const nuevo = (t, base = {}) => ({ ...structuredClone(DIS_DEF[t]), ...structuredClone(base), vitrina: { ...VIT_DEF, ...(base.vitrina || {}) } });
  let d = nuevo(tipo, actual?.diseno);
  let parteSel = "normal";
  cabecera(actual ? `Diseño: ${actual.nombre}` : "Diseñar cosmético", "Fondos, temas, marcos, punteros, efectos, rastros y teclados · con imágenes, 3D y efectos legendarios", "", actual ? "tienda" : null);
  const colores = (lista, min, max) => `<div class="a-colores" id="colores">${lista.map((c, i) => `<label>${i + 1}<input type="color" data-color="${i}" value="${esc(c)}"></label>`).join("")}
      ${lista.length < max ? '<button type="button" class="a-btn sm ghost" data-mas-color>＋</button>' : ""}${lista.length > min ? '<button type="button" class="a-btn sm ghost" data-menos-color>−</button>' : ""}</div>`;
  const color = (k, t) => campo(t, `<input type="color" data-k="${k}" value="${esc(d[k])}">`);
  const seg = (k, lista) => `<div class="a-seg" data-seg="${k}">${lista.map(([v, t]) => `<button type="button" data-v="${v}" class="${d[k] === v ? "on" : ""}">${t}</button>`).join("")}</div>`;
  const toggle = (k, t) => `<div><label class="a-interruptor"><input type="checkbox" data-b="${k}" ${d[k] ? "checked" : ""}> ${t}</label></div>`;
  const plantillas = () => (PLANTILLAS[tipo] ? campo("✨ Plantillas legendarias (un clic y luego ajustas)", `<div class="a-plantillas">${PLANTILLAS[tipo].map(([n, c], i) => `<button type="button" data-plantilla="${i}"><i style="background:conic-gradient(${[...c, c[0]].join(",")})"></i>${esc(n)}</button>`).join("")}</div>`, "todo") : "");
  const panelTipo = () => {
    if (tipo === "fondo") return `${plantillas()}${campo("Estilo", seg("estilo", [["lineal", "Vertical"], ["diagonal", "Diagonal"], ["radial", "Círculo"], ["aurora", "Aurora"], ["imagen", "🖼 Imagen"]]), "todo")}
      ${d.estilo === "imagen" ? `${bloqueImagen(d.imagen, { texto: "Imagen o GIF de fondo" })}
        ${d.imagen ? `${campo("Cómo se pone", seg("modo", [["cubrir", "Cubrir todo"], ["mosaico", "Mosaico"], ["centrar", "Centrada"]]), "todo")}
        ${d.modo !== "mosaico" ? campo("📱 En el celular (pantalla vertical)", seg("movil", [["completa", "Imagen completa"], ["recortar", "Recortar para llenar"]]), "todo") : ""}
        ${d.modo === "mosaico" ? campo(`Tamaño del mosaico (${d.mosaico}px)`, `<input type="range" min="24" max="800" data-k="mosaico" value="${d.mosaico}">`) : ""}
        ${campo("Movimiento de la imagen", `<select data-k="movimiento">${opciones([["ninguno", "Quieta"], ["zoom", "Zoom lento (efecto cine)"], ["paneo", "Paneo de lado a lado"], ["flotar", "Flotar"], ["latido", "Latido"]], d.movimiento)}</select>`)}
        ${campo(`Desenfoque (${d.desenfoque}px)`, `<input type="range" min="0" max="20" data-k="desenfoque" value="${d.desenfoque}">`)}` : ""}` : ""}
      ${campo(d.estilo === "imagen" ? "Color de respaldo" : "Colores", colores(d.colores, d.estilo === "imagen" ? 1 : 2, 4), "todo")}
      ${campo("Animación encima", `<select data-k="animacion">${opciones(Object.entries(NOMBRES_ANIM), d.animacion)}</select>`)}
      ${campo("Capa decorativa", `<select data-k="capa">${opciones(Object.entries(NOMBRES_CAPA), d.capa)}</select>`)}
      ${campo(`Oscurecer (${d.oscurecer}%) · ayuda a leer encima de imágenes claras`, `<input type="range" min="0" max="80" data-k="oscurecer" value="${d.oscurecer}">`, "todo")}
      ${toggle("oscuro", "Fondo oscuro (texto claro)")}
      ${campo("🌧️ Lluvia de emojis o palabras", `<select data-k="lluvia">${opciones([["ninguna", "Sin lluvia"], ["cae", "Caen del cielo"], ["sube", "Suben como burbujas"], ["flota", "Flotan en su sitio"], ["remolino", "Remolino"]], d.lluvia)}</select>`)}
      ${d.lluvia !== "ninguna" ? `${campo("Qué cae (emojis o palabras separados por espacio)", `<input data-k="lluvia_emojis" maxlength="80" value="${esc(d.lluvia_emojis)}" placeholder="🍕 🐱 </> 1 0">`)}
        ${campo(`Cantidad (${d.lluvia_cantidad})`, `<input type="range" min="4" max="40" data-k="lluvia_cantidad" value="${d.lluvia_cantidad}">`, "todo")}` : ""}
      ${campo(`✨ Stickers y GIFs encima del fondo (${d.stickers.length}/8)`, `<div class="a-stickers">${d.stickers.map((x, i) => `<div class="a-sticker">
          <img src="${esc(x.imagen)}" alt=""><div class="a-campos">
          ${campo(`Izquierda ↔ (${x.x}%)`, `<input type="range" min="0" max="100" data-st="${i}" data-sk="x" value="${x.x}">`)}${campo(`Arriba ↕ (${x.y}%)`, `<input type="range" min="0" max="100" data-st="${i}" data-sk="y" value="${x.y}">`)}
          ${campo(`Tamaño (${x.tam}%)`, `<input type="range" min="2" max="80" data-st="${i}" data-sk="tam" value="${x.tam}">`)}${campo(`Giro (${x.girar}°)`, `<input type="range" min="-180" max="180" data-st="${i}" data-sk="girar" value="${x.girar}">`)}
          ${campo(`Opacidad (${x.opacidad}%)`, `<input type="range" min="10" max="100" data-st="${i}" data-sk="opacidad" value="${x.opacidad}">`)}${campo("Animación", `<select data-st="${i}" data-sk="anim">${opciones(ANIMS, x.anim)}</select>`)}
          </div><div class="a-sticker-acc"><button type="button" class="a-btn sm" data-editar-img="sticker:${i}">✏️</button><button type="button" class="a-btn sm" data-dup-st="${i}" title="Duplicar">⧉</button><button type="button" class="a-btn sm ghost" data-quitar-img="sticker:${i}">🗑</button></div></div>`).join("")}
        ${d.stickers.length < 8 ? '<label class="a-btn sm">＋ Agregar imagen o GIF<input type="file" data-subir="sticker" accept="image/png,image/jpeg,image/webp,image/gif" hidden></label>' : ""}
        <small class="a-sub">Pon estrellas, personajes, logos o GIFs animados donde quieras: se ven en todas las páginas del estudiante.</small></div>`, "todo")}`;
    if (tipo === "codi") return `${bloqueImagen(d.imagen, { texto: "Imagen o GIF del accesorio (sombrero, gafas, alas, mascota…)", clave: "imagen" })}
      ${campo("Dónde va", seg("capa", [["cabeza", "🎩 Cabeza"], ["cara", "🕶️ Cara"], ["cuello", "🧣 Cuello"], ["atras", "🪽 Detrás"], ["frente", "🛹 Al frente"]]), "todo")}
      ${campo(`Izquierda ↔ (${d.x})`, `<input type="range" min="0" max="200" data-k="x" value="${d.x}">`)}${campo(`Arriba ↕ (${d.y})`, `<input type="range" min="-40" max="220" data-k="y" value="${d.y}">`)}
      ${campo(`Tamaño (${d.tam})`, `<input type="range" min="10" max="220" data-k="tam" value="${d.tam}">`)}${campo(`Giro (${d.girar}°)`, `<input type="range" min="-180" max="180" data-k="girar" value="${d.girar}">`)}
      ${campo("Animación", `<select data-k="anim">${opciones(ANIMS, d.anim)}</select>`)}${toggle("sinAntena", "Quitar la antena de Codi (para sombreros)")}`;
    if (tipo === "tema") return `${plantillas()}${color("acc", "Color principal")}${color("acc2", "Color oscuro")}${color("cy", "Color de acento")}
      ${campo("Tipo de letra", `<select data-k="fuente">${opciones([["sistema", "La de siempre"], ["redondeada", "Redondeada (amigable)"], ["mono", "De programador"], ["manuscrita", "Manuscrita"], ["pixel", "Pixel (videojuego)"], ["elegante", "Elegante"]], d.fuente)}</select>`)}
      ${toggle("neon", "Brillo neón en botones y títulos")}${toggle("fluir", "Degradado que se mueve en botones y barras (como los legendarios)")}`;
    if (tipo === "marco") return `${plantillas()}${campo("Estilo del aro", seg("estilo", [["aro", "Aro"], ["neon", "Neón"], ["holo", "Holográfico"], ["fuego", "Fuego"], ["imagen", "🖼 Imagen"]]), "todo")}
      ${d.estilo === "imagen" ? bloqueImagen(d.imagen, { redondo: true, texto: "Imagen del aro (se ve alrededor de la foto)" }) : ""}
      ${d.estilo !== "imagen" || d.brillo ? campo(d.estilo === "imagen" ? "Color del brillo" : "Colores del aro", colores(d.colores, 2, 6), "todo") : ""}
      ${toggle("gira", "Que gire")}${toggle("brillo", "Que brille")}${toggle("orbita", "Chispas en órbita")}${toggle("pulso", "Que lata (pulso de luz)")}
      ${campo(`Velocidad de giro (${d.velocidad})`, `<input type="range" min="1" max="10" data-k="velocidad" value="${d.velocidad}">`)}
      ${campo(`Grosor del aro (${d.grosor}px)`, `<input type="range" min="2" max="10" data-k="grosor" value="${d.grosor}">`)}
      ${bloqueImagen(d.insignia?.imagen || "", { texto: "👑 Insignia pegada al aro (imagen o GIF: corona, emblema, mascota…)", clave: "insignia" })}
      ${d.insignia ? `${campo("Posición", `<div class="a-seg" data-iseg="pos">${[["arriba", "Arriba"], ["abajo", "Abajo"], ["derecha", "Derecha"], ["izquierda", "Izquierda"]].map(([v, t]) => `<button type="button" data-v="${v}" class="${d.insignia.pos === v ? "on" : ""}">${t}</button>`).join("")}</div>`, "todo")}
        ${campo(`Tamaño (${d.insignia.tam}%)`, `<input type="range" min="15" max="90" data-ik="tam" value="${d.insignia.tam}">`)}${campo("Animación", `<select data-ik="anim">${opciones(ANIMS.slice(0, 4), d.insignia.anim)}</select>`)}` : ""}`;
    if (tipo === "cursor") {
      const p = d.partes[parteSel];
      const tipos = [["flecha", "➤ Flecha"], ["emoji", "😀 Solo emoji"], ["flecha_emoji", "➤😀 Flecha + emoji"], ["forma", "⭐ Forma"], ["imagen", "🖼 Imagen"], ["mano", "👆 Mano"], ["barra", "𝙸 Barra de texto"], ["sistema", "💻 La normal del equipo"]];
      const usaColor = ["flecha", "flecha_emoji", "forma", "mano", "barra"].includes(p.tipo);
      return `${campo("Cada parte del puntero se diseña por separado", `<div class="a-seg" data-parte>${[["normal", "🖱️ Normal"], ["mano", "👆 Sobre botones y enlaces"], ["texto", "✏️ Sobre texto"]].map(([k, t]) => `<button type="button" data-v="${k}" class="${parteSel === k ? "on" : ""}">${t}</button>`).join("")}</div>`, "todo")}
        ${campo("Qué se ve", `<div class="a-seg a-seg-envuelve" data-pseg="tipo">${tipos.map(([v, t]) => `<button type="button" data-v="${v}" class="${p.tipo === v ? "on" : ""}">${t}</button>`).join("")}</div>`, "todo")}
        ${["emoji", "flecha_emoji"].includes(p.tipo) ? campo("Emoji", `<input data-pk="emoji" maxlength="8" value="${esc(p.emoji)}">`) : ""}
        ${p.tipo === "forma" ? campo("Forma", `<select data-pk="forma">${opciones([["estrella", "Estrella"], ["corazon", "Corazón"], ["circulo", "Bolita"], ["mira", "Mira"], ["rombo", "Diamante"], ["punto", "Punto con aro"], ["rayo", "Rayo"]], p.forma)}</select>`) : ""}
        ${p.tipo === "imagen" ? bloqueImagen(p.imagen, { texto: "Imagen del puntero (PNG con fondo transparente queda mejor)", clave: `parte:${parteSel}` }) : ""}
        ${usaColor ? `${campo("Relleno", `<input type="color" data-pk="c1" value="${esc(p.c1)}">`)}${campo("Borde", `<input type="color" data-pk="c2" value="${esc(p.c2)}">`)}` : ""}
        ${["emoji", "forma", "imagen", "mano"].includes(p.tipo) ? campo("¿Dónde está la punta?", `<div class="a-seg" data-pseg="punta">${[["esquina", "↖ Esquina"], ["centro", "⊙ Centro"]].map(([v, t]) => `<button type="button" data-v="${v}" class="${p.punta === v ? "on" : ""}">${t}</button>`).join("")}</div>`) : ""}
        ${campo(`Tamaño del puntero (${d.tam}px)`, `<input type="range" min="24" max="64" step="4" data-k="tam" value="${d.tam}">`, "todo")}
        <small class="a-sub todo">Pasa el mouse por la vista previa para probar cada parte. Los GIF se ven quietos en el puntero (los navegadores no animan punteros): para algo animado usa un Rastro «mascota».</small>`;
    }
    if (tipo === "dedo" && d.modo === "mascota") return `${campo("Tipo de rastro", seg("modo", [["particulas", "✨ Partículas"], ["mascota", "🐾 Mascota que te sigue"]]), "todo")}
      ${bloqueImagen(d.imagen, { texto: "Imagen o GIF de la mascota (sigue al mouse y al dedo)", clave: "imagen" })}
      ${campo(`Tamaño (${d.tam}px)`, `<input type="range" min="16" max="160" data-k="tam" value="${d.tam}">`, "todo")}`;
    if (tipo === "efecto" || tipo === "dedo") return `${tipo === "dedo" ? campo("Tipo de rastro", seg("modo", [["particulas", "✨ Partículas"], ["mascota", "🐾 Mascota que te sigue"]]), "todo") : ""}${plantillas()}${campo("Partículas", `<select data-k="forma">${opciones(Object.entries(NOMBRES_FORMA), d.forma)}</select>`)}
      ${d.forma === "emoji" ? campo("Emojis (uno o varios separados por espacio: salen al azar)", `<input data-k="emojis" maxlength="80" value="${esc(d.emojis || d.emoji)}" placeholder="🎉 ⭐ 💥 🚀">`, "todo") : ""}
      ${d.forma === "texto" ? campo("Palabras (separadas por espacio)", `<input data-k="palabras" maxlength="100" value="${esc(d.palabras)}" placeholder="+1 ¡Bien! 💯 Crack">`, "todo") : ""}
      ${d.forma === "imagen" ? `${bloqueImagen(d.imagen, { texto: "Imagen de cada partícula" })}${campo(`Tamaño (${d.tam}px)`, `<input type="range" min="12" max="64" data-k="tam" value="${d.tam}">`)}` : ""}
      ${!["emoji", "imagen"].includes(d.forma) ? campo(d.forma === "texto" ? "Colores de las palabras" : "Colores", colores(d.colores, 1, 6), "todo") : ""}
      ${tipo === "efecto" ? campo(`Cantidad por clic (${d.cantidad})`, `<input type="range" min="3" max="20" data-k="cantidad" value="${d.cantidad}">`, "todo") : ""}`;
    if (tipo === "teclado") return `${plantillas()}${campo("Estilo de las teclas", seg("estilo", [["plano", "Plano"], ["3d", "🧊 3D"], ["neon", "Neón"], ["cristal", "Cristal"], ["arcoiris", "🌈 Arcoíris"]]), "todo")}
      ${color("bg", "Teclas")}${color("fg", "Letras")}${color("borde", d.estilo === "neon" ? "Luz neón" : "Borde")}${color("enter", "Tecla Enter")}${color("fondo", "Fondo del teclado")}
      ${toggle("chispas", "Chispas al teclear")}${bloqueImagen(d.imagen, { texto: "Imagen detrás del teclado (opcional)" })}`;
    return "";
  };
  vista.innerHTML = `<div class="a-disenador">
    <form id="formDis" class="a-tarjeta" novalidate>
      ${actual ? "" : `<div class="a-seg" id="segCos" style="margin-bottom:14px">${Object.keys(DIS_DEF).map((t) => `<button type="button" data-t="${t}" class="${t === tipo ? "on" : ""}">${TIPO_UNO[t]}</button>`).join("")}</div>`}
      <div class="a-campos">
        ${campo("Nombre", `<input name="nombre" required maxlength="50" value="${esc(actual?.nombre || "")}" placeholder="Atardecer neón">`)}
        ${campo("Precio (💎)", `<input type="number" name="precio" min="0" max="1000000" value="${actual?.precio ?? 300}">`)}
        ${campo("Rareza", `<select name="rareza">${opciones(Object.entries(RAREZAS), actual?.rareza || "raro")}</select>`)}
        <div style="align-self:end">${interruptor("activo", "A la venta", actual ? actual.activo : true)}</div>
        ${campo("Descripción", `<input name="descripcion" maxlength="200" value="${esc(actual?.descripcion || "")}" placeholder="Lo que verá el estudiante en la tienda">`, "todo")}
      </div>
      <h3 style="margin:18px 0 10px;font-size:15px">Diseño</h3>
      <div class="a-campos" id="panelTipo"></div>
      <h3 style="margin:18px 0 10px;font-size:15px">Vitrina en la tienda</h3>
      <div class="a-campos" id="panelVit"></div>
      <p class="a-err" id="errDis"></p>
      <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px;flex-wrap:wrap">${actual ? '<a class="a-btn ghost" href="#disenar">＋ Diseñar otro</a>' : ""}<button class="a-btn pri" type="submit">${actual ? "Guardar diseño" : "Crear y poner a la venta"}</button></div>
    </form>
    <div class="a-prev-caja"><div class="a-tarjeta" style="padding:12px"><div class="a-sec-cab" style="margin-bottom:10px"><h2 style="font-size:14px">Vista previa</h2><span class="a-sub" style="font-size:12px">Así se verá en la tienda</span></div><div id="previa"></div></div></div>
  </div>
  <section class="a-sec"><div class="a-sec-cab"><h2>Tus diseños (${cat.disenados.length})</h2></div>
    <div class="a-articulos">${cat.disenados.map((c) => `<article class="a-articulo ${c.activo ? "" : "apagado"}"><div class="vista" data-prev="${esc(c.clave)}" data-tipo="${esc(c.tipo)}"></div>
      <div class="a-articulo-cuerpo"><b>${esc(c.nombre)}</b><div class="a-chips">${rareza(c.rareza)}<span class="a-chip">${esc(TIPO_UNO[c.tipo])}</span></div><span class="a-precio">💎 ${num(c.precio)}</span></div>
      <div class="a-articulo-pie"><a class="a-btn sm" href="#disenar/${esc(c.clave)}">✏️ Editar</a></div></article>`).join("") || vacio("🎨", "Todavía no has diseñado cosméticos.")}</div></section>`;
  const form = $("formDis");
  if (tipo === "cursor" && !d.partes?.normal) d = nuevo("cursor");   // diseños viejos (flecha + emoji) pasan a partes
  const limpio = () => { const x = structuredClone(d); if (!x.imagen) delete x.fuente; return x; };
  const previa = () => {
    probarDiseno({ clave: "a_vista_previa", tipo, diseno: limpio() });
    const v = valores(form);
    const caja = $("previa");
    caja.innerHTML = `<div class="vit-card" data-base="rareza-${esc(v.rareza)}"><span class="producto-rango">${esc(RAREZAS[v.rareza] || "")}</span>
      ${tipo === "marco" ? '<div class="a-prev-marco"><div class="vista" style="border:0;background:none;height:auto"></div></div>' : '<div class="vista"></div>'}
      <h3>${esc(v.nombre || "Sin nombre")}</h3><small>${esc(v.descripcion || TIPO_UNO[tipo])}</small><span class="vit-precio">💎 ${num(v.precio)} diamantes</span></div>`;
    const el = caja.querySelector(".vista");
    try { vistaPrevia(el, "a_vista_previa", tipo); } catch { /* nada */ }
    adornarVitrina(caja.querySelector(".vit-card"), d.vitrina);
    // Fondos: así se verá en un celular (pantalla vertical), para acomodar imagen y stickers también ahí.
    if (tipo === "fondo") {
      caja.insertAdjacentHTML("beforeend", '<div class="a-prev-movil" aria-label="Vista en celular"><div class="a-prev-movil-pantalla"><div class="vista"></div></div><small>📱 Así se ve en el celular</small></div>');
      try { vistaPrevia(caja.querySelector(".a-prev-movil .vista"), "a_vista_previa", tipo); } catch { /* nada */ }
    }
  };
  const pintar = () => { $("panelTipo").innerHTML = panelTipo(); $("panelVit").innerHTML = controlesVitrina(d.vitrina); previa(); };
  pintar();
  vistasPerezosas(vista);
  // Imágenes: «imagen» (la principal), «insignia» (marco), «sticker» (agregar uno) o «sticker:3» (uno de la lista)
  const opcionesImg = (clave) => (clave.startsWith("parte:") ? { titulo: "Imagen del puntero", salida: [64, 64], formas: true } : clave.startsWith("sticker") ? IMG_TIPO.sticker : clave === "insignia" ? IMG_TIPO.insignia
    : tipo === "codi" ? IMG_TIPO.codi : tipo === "dedo" && d.modo === "mascota" ? IMG_TIPO.mascota : IMG_TIPO[tipo]);
  const ponerImg = (clave, url, fuente) => {
    if (clave === "imagen") { d.imagen = url; if (fuente) d.fuente = fuente; }
    else if (clave === "insignia") d.insignia = { pos: "arriba", tam: 45, anim: "ninguna", ...(d.insignia || {}), imagen: url };
    else if (clave === "sticker") d.stickers.push({ imagen: url, x: 50, y: 30, tam: 18, anim: "flotar", opacidad: 100, girar: 0 });
    else if (clave.startsWith("sticker:")) d.stickers[Number(clave.split(":")[1])].imagen = url;
    else if (clave.startsWith("parte:")) d.partes[clave.split(":")[1]].imagen = url;
  };
  const imgDe = (clave) => (clave === "imagen" ? d.fuente || d.imagen : clave === "insignia" ? d.insignia?.imagen
    : clave.startsWith("parte:") ? d.partes[clave.split(":")[1]].imagen : d.stickers[Number(clave.split(":")[1])]?.imagen);
  const editar = async (clave) => {
    const url = await editarImagen(imgDe(clave), opcionesImg(clave)).catch((x) => { fallo(x); return null; });
    if (url) { ponerImg(clave, url); pintar(); toast("Imagen lista."); }
  };
  form.addEventListener("click", async (e) => {
    const t = e.target.closest("#segCos [data-t]");
    if (t) { tipo = t.dataset.t; d = nuevo(tipo); parteSel = "normal"; form.querySelectorAll("#segCos button").forEach((b) => b.classList.toggle("on", b === t)); pintar(); return; }
    const p = e.target.closest("[data-plantilla]");
    if (p) {
      const [n, c, extra] = PLANTILLAS[tipo][Number(p.dataset.plantilla)];
      d = nuevo(tipo, { ...d, ...structuredClone(extra), ...(["teclado", "tema"].includes(tipo) ? {} : { colores: [...c] }), imagen: extra.estilo === "imagen" ? d.imagen : d.imagen && tipo === "teclado" ? d.imagen : "" });
      if (!form.nombre.value) form.nombre.value = n;
      if (extra.vitrina?.destellos) form.rareza.value = "legendario";
      pintar(); return;
    }
    const pa = e.target.closest("[data-parte] [data-v]");
    if (pa) { parteSel = pa.dataset.v; pintar(); return; }
    const ps = e.target.closest("[data-pseg] [data-v]");
    if (ps) { d.partes[parteSel][ps.closest("[data-pseg]").dataset.pseg] = ps.dataset.v; pintar(); return; }
    const vs = e.target.closest("[data-vseg] [data-v]");
    if (vs) { d.vitrina.efecto = vs.dataset.v; pintar(); return; }
    const s = e.target.closest("[data-seg] [data-v]");
    if (s) { d[s.closest("[data-seg]").dataset.seg] = s.dataset.v; if (tipo === "fondo" && s.dataset.v === "imagen" && d.colores.length > 1) d.colores = d.colores.slice(0, 1); pintar(); return; }
    if (e.target.closest("[data-mas-color]")) { d.colores.push(d.colores.at(-1) || "#ffffff"); pintar(); }
    if (e.target.closest("[data-menos-color]")) { d.colores.pop(); pintar(); }
    const ed = e.target.closest("[data-editar-img]");
    if (ed) editar(ed.dataset.editarImg);
    const qu = e.target.closest("[data-quitar-img]");
    if (qu) {
      const k = qu.dataset.quitarImg;
      if (k === "imagen") { d.imagen = ""; delete d.fuente; } else if (k === "insignia") d.insignia = null;
      else if (k.startsWith("parte:")) { const p = d.partes[k.split(":")[1]]; p.imagen = ""; p.tipo = "flecha"; } else d.stickers.splice(Number(k.split(":")[1]), 1);
      pintar();
    }
    const du = e.target.closest("[data-dup-st]");
    if (du && d.stickers.length < 8) { const o = d.stickers[Number(du.dataset.dupSt)]; d.stickers.push({ ...o, x: Math.min(100, o.x + 12), y: Math.min(100, o.y + 8) }); pintar(); }
    const is = e.target.closest("[data-iseg] [data-v]");
    if (is && d.insignia) { d.insignia.pos = is.dataset.v; pintar(); }
  });
  form.addEventListener("input", (e) => {
    const el = e.target;
    if (el.dataset.color !== undefined) d.colores[Number(el.dataset.color)] = el.value;
    else if (el.dataset.k) d[el.dataset.k] = el.type === "range" ? Number(el.value) : el.value;
    else if (el.dataset.b) d[el.dataset.b] = el.checked;
    else if (el.dataset.pk) { d.partes[parteSel][el.dataset.pk] = el.value; previa(); if (el.tagName === "SELECT") pintar(); return; }
    else if (el.dataset.st !== undefined) { const x = d.stickers[Number(el.dataset.st)]; x[el.dataset.sk] = el.tagName === "SELECT" ? el.value : Number(el.value); const l = el.closest("label"); if (l && el.type === "range") l.firstChild.textContent = l.firstChild.textContent.replace(/\(.*\)/, `(${el.value}${["x", "y", "tam", "opacidad"].includes(el.dataset.sk) ? "%" : "°"})`); previa(); return; }
    else if (el.dataset.ik && d.insignia) { d.insignia[el.dataset.ik] = el.tagName === "SELECT" ? el.value : Number(el.value); previa(); return; }
    else if (el.dataset.vit) {
      const k = el.dataset.vit;
      if (k === "aura_on") d.vitrina.aura = el.checked ? form.querySelector("[data-vit=aura]").value : "";
      else if (k === "aura") { d.vitrina.aura = el.value; form.querySelector("[data-vit=aura_on]").checked = true; }
      else d.vitrina[k] = el.checked;
    } else if (["nombre", "precio", "descripcion", "rareza"].includes(el.name)) { previa(); return; }
    else return;
    if (el.type === "range" || el.tagName === "SELECT" || el.type === "checkbox") pintar(); else previa();
  });
  form.addEventListener("change", async (e) => {
    if (!e.target.matches("[data-subir]") || !e.target.files[0]) return;
    const clave = e.target.dataset.subir || "imagen";
    try {
      const r = await elegirYEditar(e.target.files[0], opcionesImg(clave));
      if (r) { ponerImg(clave, r.imagen, r.fuente); pintar(); toast("Imagen lista."); }
    } catch (x) { fallo(x); }
    e.target.value = "";
  });
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const v = { ...valores(form), tipo, diseno: limpio() };
    try {
      const r = actual ? await api(`/api/admin/cosmeticos/${actual.id}`, v, "PATCH") : await api("/api/admin/cosmeticos", v);
      catalogoCos = null;
      toast(actual ? "Diseño guardado." : "¡Creado! Ya está a la venta en la tienda.");
      if (actual) recargar(); else location.hash = `disenar/${r.cosmetico.clave}`;
    } catch (x) { $("errDis").textContent = x.message; }
  });
}

// =============================================================================== medallas ====
const MED_DEF = { forma: "circulo", metal: "oro", c1: "#c4ff3d", c2: "#0ea5e9", centro: "emoji", emoji: "🏅", imagen: "", cinta: "v", cinta1: "#ef4444", cinta2: "#2563eb", texto: "", anim: "brillo", aura: true, estrellas: 0 };
const MED_PLANTILLAS = [
  ["Campeón dorado", { forma: "estrella", metal: "oro", c1: "#fde047", c2: "#b45309", emoji: "🏆", cinta: "v", cinta1: "#dc2626", cinta2: "#f59e0b", texto: "Campeón", anim: "brillo", aura: true, estrellas: 3 }],
  ["Cazador de bugs", { forma: "escudo", metal: "esmeralda", c1: "#86efac", c2: "#14532d", emoji: "🐛", cinta: "doble", cinta1: "#16a34a", cinta2: "#facc15", texto: "Bug hunter", anim: "latido", aura: true, estrellas: 0 }],
  ["Leyenda diamante", { forma: "rombo", metal: "diamante", c1: "#a5f3fc", c2: "#1e3a8a", emoji: "💎", cinta: "laurel", texto: "Leyenda", anim: "destellos", aura: true, estrellas: 5 }],
  ["Racha de fuego", { forma: "circulo", metal: "rubi", c1: "#fb923c", c2: "#7f1d1d", emoji: "🔥", cinta: "v", cinta1: "#f97316", cinta2: "#7f1d1d", texto: "100 días", anim: "girar", aura: true, estrellas: 0 }],
  ["Ingeniero", { forma: "engranaje", metal: "plata", c1: "#cbd5e1", c2: "#334155", emoji: "⚙️", cinta: "doble", cinta1: "#334155", cinta2: "#38bdf8", texto: "Maestro", anim: "girar", aura: false, estrellas: 2 }],
  ["Realeza", { forma: "corona", metal: "arcoiris", c1: "#f0abfc", c2: "#6d28d9", emoji: "👑", cinta: "laurel", texto: "Rey del código", anim: "flotar", aura: true, estrellas: 3 }],
];
async function medallas() {
  cabecera("Medallas especiales", "Diséñalas a tu gusto y entrégalas desde la ficha de un usuario o con un artículo de la tienda", '<button class="a-btn pri sm" type="button" id="nuevaMed">＋ <span class="txt">Nueva medalla</span></button>');
  const { medallas: ms } = await api("/api/admin/medallas");
  vista.innerHTML = ms.length ? `<div class="a-medallas">${ms.map((m) => `<article class="a-med ${m.activa ? "" : "apagado"}" data-med="${m.id}">
      <div class="a-med-dibujo">${medallaSVG(m, 92)}</div><b>${esc(m.nombre)}</b><small>${esc(m.descripcion || "Sin descripción")}</small>
      <span class="a-chip">${m.otorgadas} entregada${m.otorgadas === 1 ? "" : "s"}</span>
      <div class="a-med-pie"><button class="a-btn sm" type="button" data-m="editar">✏️ Editar</button><button class="a-btn sm ghost" type="button" data-m="activa" title="${m.activa ? "Ocultar" : "Activar"}">${m.activa ? "🙈" : "👁"}</button><button class="a-btn sm ghost" type="button" data-m="borrar" title="Borrar">🗑</button></div></article>`).join("")}</div>`
    : vacioCodi("Todavía no has creado medallas. ¡Diseña la primera, yo la estreno! 🏅", "saludo");
  const form = (m = null) => {
    const d = { ...MED_DEF, ...(m?.diseno || (m ? { emoji: m.icono, c1: m.color } : {})) };
    const seg = (k, lista) => `<div class="a-seg a-seg-envuelve" data-mseg="${k}">${lista.map(([v, t]) => `<button type="button" data-v="${v}" class="${d[k] === v ? "on" : ""}">${t}</button>`).join("")}</div>`;
    const controles = () => `${m ? "" : campo("✨ Plantillas (un clic y luego ajustas)", `<div class="a-plantillas">${MED_PLANTILLAS.map(([t, x], i) => `<button type="button" data-mplant="${i}">${medallaSVG({ diseno: { ...MED_DEF, ...x, anim: "ninguna" } }, 40)}${esc(t)}</button>`).join("")}</div>`, "todo")}
      ${campo("Forma", seg("forma", FORMAS_MEDALLA), "todo")}${campo("Metal del borde", seg("metal", METALES_MEDALLA), "todo")}
      ${campo("Color de adentro", `<input type="color" data-mk="c1" value="${esc(d.c1)}">`)}${campo("Color de adentro (sombra)", `<input type="color" data-mk="c2" value="${esc(d.c2)}">`)}
      ${campo("En el centro", seg("centro", [["emoji", "😀 Emoji"], ["imagen", "🖼 Imagen o GIF en el centro"], ["completa", "🖼 Imagen o GIF en toda la medalla"]]), "todo")}
      ${d.centro !== "emoji" ? bloqueImagen(d.imagen, { texto: "Imagen o GIF (los GIF se mueven en la medalla)", clave: "medalla", redondo: d.centro === "imagen" }) : campo("Emoji", `<input data-mk="emoji" maxlength="8" value="${esc(d.emoji)}">`)}
      ${campo("Cinta", seg("cinta", [["ninguna", "Sin cinta"], ["v", "🎗️ En V"], ["doble", "Rayada"], ["laurel", "🌿 Laureles"]]), "todo")}
      ${d.cinta === "v" || d.cinta === "doble" ? `${campo("Color de la cinta 1", `<input type="color" data-mk="cinta1" value="${esc(d.cinta1)}">`)}${campo("Color de la cinta 2", `<input type="color" data-mk="cinta2" value="${esc(d.cinta2)}">`)}` : ""}
      ${campo("Letrero (opcional)", `<input data-mk="texto" maxlength="16" value="${esc(d.texto)}" placeholder="Campeón">`)}
      ${campo(`Estrellas arriba (${d.estrellas})`, `<input type="range" min="0" max="5" data-mk="estrellas" value="${d.estrellas}">`)}
      ${campo("Animación", seg("anim", ANIM_MEDALLA), "todo")}
      <div class="todo"><label class="a-interruptor"><input type="checkbox" data-mk="aura" ${d.aura ? "checked" : ""}> Aura de luz alrededor</label></div>`;
    hojaForm({ titulo: m ? "Editar medalla" : "Nueva medalla", boton: m ? "Guardar" : "Crear medalla", ancha: true,
      cuerpo: `<div class="a-med-editor"><div class="a-med-vista"><div id="medVista"></div><small class="a-sub">Así la verá el estudiante en su perfil</small></div>
        <div><div class="a-campos">${campo("Nombre", `<input name="nombre" required maxlength="50" value="${esc(m?.nombre || "")}" placeholder="Cazador de bugs">`)}
          ${campo("Descripción", `<input name="descripcion" maxlength="160" value="${esc(m?.descripcion || "")}" placeholder="Por reportar un error de la plataforma">`)}
          <div class="todo">${interruptor("activa", "Activa", m ? m.activa : true)}</div></div>
          <h3 style="margin:16px 0 10px;font-size:15px">Diseño</h3><div class="a-campos" id="medCtrl"></div></div></div>`,
      alAbrir: (f) => {
        const pintarVista = () => { f.querySelector("#medVista").innerHTML = medallaSVG({ nombre: f.nombre.value, diseno: d }, 170); };
        const pintar = () => { f.querySelector("#medCtrl").innerHTML = controles(); pintarVista(); };
        f.__diseno = d;
        pintar();
        f.addEventListener("click", async (e) => {
          const pl = e.target.closest("[data-mplant]");
          if (pl) { const [t, x] = MED_PLANTILLAS[Number(pl.dataset.mplant)]; Object.assign(d, MED_DEF, x); if (!f.nombre.value) f.nombre.value = t; pintar(); return; }
          const sg = e.target.closest("[data-mseg] [data-v]");
          if (sg) { d[sg.closest("[data-mseg]").dataset.mseg] = sg.dataset.v; pintar(); return; }
          if (e.target.closest("[data-editar-img=medalla]")) { const u = await editarImagen(d.imagen, { titulo: "Imagen de la medalla", salida: [256, 256], formas: true, forma: d.centro === "imagen" ? "circulo" : "cuadro" }).catch((x) => { fallo(x); return null; }); if (u) { d.imagen = u; pintar(); } }
          if (e.target.closest("[data-quitar-img=medalla]")) { d.imagen = ""; d.centro = "emoji"; pintar(); }
        });
        f.addEventListener("input", (e) => {
          const k = e.target.dataset.mk;
          if (k) { d[k] = e.target.type === "checkbox" ? e.target.checked : e.target.type === "range" ? Number(e.target.value) : e.target.value; if (e.target.type === "range") pintar(); else pintarVista(); }
          else if (e.target.name === "nombre") pintarVista();
        });
        f.addEventListener("change", async (e) => {
          if (!e.target.matches("[data-subir=medalla]") || !e.target.files[0]) return;
          try { const r = await elegirYEditar(e.target.files[0], { titulo: "Imagen de la medalla", salida: [256, 256], formas: true, forma: d.centro === "imagen" ? "circulo" : "cuadro" }); if (r) { d.imagen = r.imagen; pintar(); } } catch (x) { fallo(x); }
          e.target.value = "";
        });
      },
      enviar: async (v, f) => {
        v.diseno = f.__diseno;
        if (m) await api(`/api/admin/medallas/${m.id}`, v, "PATCH"); else await api("/api/admin/medallas", v);
        toast("Medalla guardada."); recargar();
      } });
  };
  $("nuevaMed").addEventListener("click", () => form());
  vista.onclick = async (e) => {
    if (e.target.closest("[data-codi-accion]")) { form(); return; }
    const b = e.target.closest("[data-m]");
    if (!b) return;
    const m = ms.find((x) => String(x.id) === b.closest("[data-med]").dataset.med);
    try {
      if (b.dataset.m === "editar") form(m);
      else if (b.dataset.m === "activa") { await api(`/api/admin/medallas/${m.id}`, { activa: !m.activa }, "PATCH"); recargar(); }
      else if (await confirmar(`¿Borrar la medalla «${m.nombre}»?`, { peligro: true, ok: "Borrar", detalle: m.otorgadas ? `Se le quitará a ${m.otorgadas} persona${m.otorgadas === 1 ? "" : "s"}.` : "" })) {
        await api(`/api/admin/medallas/${m.id}`, null, "DELETE"); toast("Medalla borrada."); recargar();
      }
    } catch (y) { fallo(y); }
  };
}

// =============================================================================== base de datos ====
// =============================================================================== antivirus ====
const GRAV = { critica: ["Crítica", "rojo"], alta: ["Alta", "nar"], media: ["Media", "ama"], baja: ["Baja", "cian"] };
async function antivirus() {
  cabecera("Antivirus de CódigoCamp", "Revisa todo lo que llega al servidor: subidas, lo que se escribe en Trabajo, adjuntos de chats e IA y el código que se ejecuta",
    '<button class="a-btn pri sm" type="button" id="probarAv">🧪 <span class="txt">Probar antivirus</span></button>');
  const e = await api("/api/admin/antivirus");
  const capas = [
    ["🧬", "Firmas de virus conocidos", `${num(e.huellas)} huellas SHA-256 + firma EICAR. Aprende sola cada virus crítico que bloquea.`, true],
    ["🦠", "Motor ClamAV", e.clamav.activo ? `Activo (${esc(e.clamav.modo)}) · ${esc(e.clamav.version)}` : "No instalado en este servidor: instálalo para sumar más de 8 millones de firmas de virus reales.", e.clamav.activo],
    ["🎭", "Archivos disfrazados", "Programas (.exe, Linux, macOS), accesos directos .lnk y scripts escondidos en imágenes o documentos.", true],
    ["📄", "Documentos peligrosos", "PDF con JavaScript o que abren programas, macros de Office, plantillas remotas, DDE y RTF con exploits.", true],
    ["🗜️", "Comprimidos", "Revisa por dentro cada archivo, bombas zip y zips con contraseña.", true],
    ["💻", "Código malicioso", "Shell reversa, webshells, ladrones de contraseñas, ransomware, keyloggers, mineros, persistencia, descargadores, ataques DoS, phishing.", true],
    ["⌨️", "Órdenes peligrosas", "En scripts .sh/.bat/.ps1 línea por línea y en lo que se ejecuta: borrar el sistema, desactivar el antivirus, borrar copias de seguridad…", true],
  ];
  vista.innerHTML = `<div class="a-kpis">
      <div class="a-kpi ${e.activo ? "verde" : "rojo"}"><i>🛡️</i><b>${e.activo ? "Activo" : "Apagado"}</b><span>${e.activo ? "protegiendo el servidor" : "ANTIVIRUS=0 en el .env"}</span></div>
      <div class="a-kpi"><i>🧬</i><b>${num(e.huellas)}</b><span>huellas de virus</span></div>
      <div class="a-kpi ${e.clamav.activo ? "verde" : ""}"><i>🦠</i><b>${e.clamav.activo ? "Sí" : "No"}</b><span>ClamAV</span></div>
      <div class="a-kpi"><i>🚫</i><b>${num(e.bloqueos_30d)}</b><span>bloqueos en 30 días</span></div>
    </div>
    <section class="a-sec"><div class="a-sec-cab"><h2>Capas de protección</h2></div>
      <div class="a-capas">${capas.map(([i, t, d, on]) => `<div class="a-capa ${on ? "" : "off"}"><span>${i}</span><div><b>${t}</b><small>${d}</small></div><em class="a-chip ${on ? "verde" : "ama"}">${on ? "Activa" : "Opcional"}</em></div>`).join("")}</div>
    </section>
    <section class="a-sec" id="avPrueba"><div class="a-sec-cab"><h2>Prueba en vivo</h2></div>
      <p class="a-sub">«Probar antivirus» pasa por el motor real decenas de amenazas de prueba inofensivas (imitan virus reales por dentro) y código normal de estudiantes que NO debe bloquearse. No registra faltas ni envía correos.</p></section>`;
  $("probarAv").addEventListener("click", async (ev) => {
    const b = ev.currentTarget; b.disabled = true; b.innerHTML = "⏳ <span class=\"txt\">Probando…</span>";
    try {
      const r = await api("/api/admin/antivirus/probar", {});
      const fila = (x) => `<div class="a-av-fila ${x.ok ? "ok" : "mal"}"><span class="a-av-ic">${x.ok ? "✅" : "❌"}</span>
        <div><b>${esc(x.nombre)}</b> <small>${esc(x.que || "código normal de estudiante")}</small><br><small class="a-sub">${x.detectado ? `🛡️ ${esc(x.motivo)}` : "Pasó sin problema"} · ${x.ms} ms</small></div>
        ${x.gravedad ? `<em class="a-chip ${GRAV[x.gravedad]?.[1] || ""}">${GRAV[x.gravedad]?.[0] || esc(x.gravedad)}</em>` : ""}</div>`;
      const bien = r.detectadas === r.total_peligrosas && !r.falsos_positivos;
      $("avPrueba").innerHTML = `<div class="a-sec-cab"><h2>Prueba en vivo</h2></div>
        <div class="a-kpis"><div class="a-kpi ${r.detectadas === r.total_peligrosas ? "verde" : "rojo"}"><i>🎯</i><b>${r.detectadas}/${r.total_peligrosas}</b><span>amenazas detectadas</span></div>
          <div class="a-kpi ${r.falsos_positivos ? "rojo" : "verde"}"><i>👌</i><b>${r.falsos_positivos}/${r.total_normales}</b><span>falsos positivos</span></div></div>
        <p class="a-sub" style="margin:12px 0">${bien ? "✅ El antivirus atrapó todas las amenazas y no bloqueó nada del código normal." : "⚠️ Revisa las filas en rojo."}</p>
        <h3 style="font-size:15px;margin:14px 0 8px">Amenazas (deben bloquearse)</h3><div class="a-av-lista">${r.resultados.filter((x) => x.peligrosa).map(fila).join("")}</div>
        <h3 style="font-size:15px;margin:18px 0 8px">Código normal (no debe bloquearse)</h3><div class="a-av-lista">${r.resultados.filter((x) => !x.peligrosa).map(fila).join("")}</div>`;
      toast(bien ? "Antivirus funcionando: todas las amenazas bloqueadas." : "La prueba encontró problemas.", !bien);
    } catch (x) { fallo(x); } finally { b.disabled = false; b.innerHTML = "🧪 <span class=\"txt\">Probar otra vez</span>"; }
  });
}

async function bd(nombre = "", pagina = "1", q = "") {
  pagina = Number(pagina) || 1;
  cabecera("Base de datos", "Solo lectura · contraseñas, tokens y chats privados ocultos");
  const { tablas } = await api("/api/admin/tablas");
  nombre = nombre || "usuarios";
  const r = await api(`/api/admin/tablas/${encodeURIComponent(nombre)}?pagina=${pagina}&q=${encodeURIComponent(q)}`);
  const ir = (n, p, qq) => { location.hash = `bd/${encodeURIComponent(n)}/${p}/${encodeURIComponent(qq)}`; };
  vista.innerHTML = `<div class="a-tablas-lista">${tablas.map((t) => `<button type="button" data-tabla="${esc(t.nombre)}" class="${t.nombre === nombre ? "on" : ""}">${esc(t.nombre)}<small>${t.filas ?? "—"}</small></button>`).join("")}</div>
    <form class="a-herr" id="buscarT"><div class="a-buscar"><input id="qBD" type="search" placeholder="Buscar en ${esc(nombre)}" value="${esc(q)}"></div><span class="a-sub">${num(r.total)} filas</span></form>
    <div class="a-tabla-w"><table class="a-tabla"><thead><tr>${r.columnas.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead>
      <tbody>${r.filas.map((f) => `<tr>${r.columnas.map((c) => `<td class="${String(f[c] ?? "").length > 40 ? "ancho" : ""}">${esc(f[c] ?? "—")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
    <div class="a-paginas">${pagina > 1 ? '<button class="a-btn sm" id="tAnt" type="button">← Anterior</button>' : ""}<span class="a-sub">Página ${pagina}</span>${pagina * r.por_pagina < r.total ? '<button class="a-btn sm" id="tSig" type="button">Siguiente →</button>' : ""}</div>`;
  vista.querySelector(".a-tablas-lista").addEventListener("click", (e) => { const b = e.target.closest("[data-tabla]"); if (b) ir(b.dataset.tabla, 1, ""); });
  vista.querySelector(".a-tablas-lista .on")?.scrollIntoView({ inline: "center", block: "nearest" });
  $("buscarT").addEventListener("submit", (e) => { e.preventDefault(); ir(nombre, 1, $("qBD").value.trim()); });
  $("tAnt")?.addEventListener("click", () => ir(nombre, pagina - 1, q));
  $("tSig")?.addEventListener("click", () => ir(nombre, pagina + 1, q));
}

// Navegación con data-ir (tarjetas que son botones) y alertas en Resumen/Alertas
document.addEventListener("click", (e) => {
  const ir = e.target.closest("[data-ir]");
  if (ir) {
    const control = e.target.closest("button,a,input,select,textarea,label");
    if (!control || control === ir) { location.hash = ir.dataset.ir; return; }
  }
  const dec = e.target.closest("[data-dec]");
  if (dec && !location.hash.startsWith("#usuario/")) accionAlerta(dec, recargar).catch(fallo);
});

arrancar();
