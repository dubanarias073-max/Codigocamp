// Lógica de chats.html
import { avatarSVG } from "/js/avatares.js";
import { sonar } from "/js/sonidos.js";
import { iniciar, api, esc, aviso, fotoDe } from "/js/app.js";
import { CSS_ADJUNTOS, crearAdjuntador, htmlAdjuntos } from "/js/adjuntar.js";
await iniciar("chats");
document.head.insertAdjacentHTML("beforeend", `<style>${CSS_ADJUNTOS}</style>`);
const $ = (id) => document.getElementById(id);
let datos, activo = null, ultimo = 0;
let ultimoDia = "", ultimoAutor = null;
const TITULO = document.title;
const TACTIL = matchMedia("(pointer: coarse)").matches;
// Alto de la barra de abajo del celular, para que el chat ocupe justo el resto de la pantalla.
{ const inf = $("inf"); const medir = () => document.documentElement.style.setProperty("--alto-inf", `${inf.offsetHeight || 0}px`); new ResizeObserver(medir).observe(inf); medir(); }
const ini = (n) => esc((n || "?").charAt(0).toUpperCase());
const avatar = (x) => (x.foto || avatarSVG(x.avatar) ? `<span class="c-av c-av-foto">${fotoDe({ ...x, cosmeticos: { marco: x.marco } }, { tam: 38 })}</span>` : `<span class="c-av">${ini(x.nombre)}</span>`);

/* ===== Lista de amigos y solicitudes ===== */
async function cargarLista() {
  const antes = datos?.recibidas?.length ?? null;
  datos = await api("/api/amigos/");
  if (antes !== null && datos.recibidas.length > antes) sonar("notificacion");   // llegó una solicitud de amistad
  if (activo && !datos.amigos.some((a) => a.id === activo)) cerrar();
  $("miCodigo").textContent = datos.yo.codigo;
  $("miAlias").textContent = "@" + datos.yo.alias;
  if (datos.yo.foto) { $("miAv").innerHTML = fotoDe({ ...datos.yo, cosmeticos: { marco: datos.yo.marco } }, { tam: 44 }); $("miAv").classList.add("c-av-foto"); }
  else if (avatarSVG(datos.yo.avatar)) $("miAv").innerHTML = avatarSVG(datos.yo.avatar, 40);
  else $("miAv").textContent = (datos.yo.nombre || "?").charAt(0).toUpperCase();
  const rec = datos.recibidas.map((r) => `<div class="c-fila">${avatar(r)}<span><b>${esc(r.nombre)}</b><small>@${esc(r.alias)}</small></span>
    <span class="c-acc"><button class="btn sm pri" type="button" data-r="${r.id}" data-a="1">Aceptar</button><button class="btn sm" type="button" data-r="${r.id}" data-a="0">No</button></span></div>`).join("");
  const env = datos.enviadas.length ? `<small>Solicitudes enviadas: ${datos.enviadas.map((e) => "@" + esc(e.alias)).join(", ")}</small>` : "";
  $("solicitudes").innerHTML = (rec ? "<h3>Solicitudes</h3>" + rec : "") + env;
  $("amigos").innerHTML = datos.amigos.length
    ? "<h3>Amigos</h3>" + datos.amigos.map((a) => `<button class="c-fila${a.id === activo ? " on" : ""}${a.no_leidos ? " nuevo" : ""}" type="button" data-id="${a.id}">
        ${avatar(a)}<span><b>${esc(a.nombre)}</b><small>${esc(a.ultimo || "@" + a.alias)}</small></span>
        ${a.no_leidos ? `<span class="c-badge">${a.no_leidos}</span>` : ""}</button>`).join("")
    : '<p class="nota">Todavía no tienes amigos. Búscalos arriba por nombre o usuario, o mándales tu enlace de invitación.</p>';
  const total = datos.amigos.reduce((n, a) => n + a.no_leidos, 0) + datos.recibidas.length;
  document.title = total ? `(${total}) ${TITULO}` : TITULO;
}

/* ===== Mensajes: `texto` entre comillas invertidas se muestra como código ===== */
function contenido(texto) {
  const frag = document.createDocumentFragment();
  texto.split(/(`[^`]+`)/).forEach((t) => {
    if (!t) return;
    if (t.length > 2 && t[0] === "`" && t.at(-1) === "`") { const c = document.createElement("code"); c.textContent = t.slice(1, -1); frag.append(c); }
    else frag.append(document.createTextNode(t));
  });
  return frag;
}
function llenarBurbuja(d, m) {
  d.replaceChildren();
  d.classList.toggle("borrado", Boolean(m.borrado));
  if (m.borrado) {
    d.classList.remove("solo-adj");
    const t = document.createElement("i");
    t.textContent = m.yo ? "🚫 Eliminaste este mensaje" : "🚫 Se eliminó este mensaje";
    d.append(t);
  } else {
    if (m.texto) d.append(contenido(m.texto));
    if (m.adjuntos?.length) d.insertAdjacentHTML("beforeend", htmlAdjuntos(m.adjuntos));
    if (m.yo) d.insertAdjacentHTML("beforeend", '<button type="button" class="cm-mas" aria-label="Opciones del mensaje" title="Opciones">⋯</button>');
  }
  const h = document.createElement("small"); h.className = "cm-hora"; h.textContent = m.hora; d.append(h);
  d._m = m;
}
/** Quita de la pantalla los mensajes que se eliminaron (también los que eliminó la otra persona). */
function aplicarBorrados(ids = []) {
  for (const id of ids) {
    const d = $("log").querySelector(`.cm[data-id="${id}"]`);
    if (d && !d.classList.contains("borrado")) llenarBurbuja(d, { ...d._m, borrado: true, texto: "", adjuntos: [] });
  }
}
// Menú de un mensaje tuyo: ⋯ (o mantener pulsado en el celular) → Copiar / Eliminar para todos
function menuMensaje(d, x, y) {
  document.getElementById("cmMenu")?.remove();
  const m = d._m;
  if (!m || m.borrado || !m.yo) return;
  const menu = document.createElement("div");
  menu.id = "cmMenu"; menu.className = "cm-menu"; menu.setAttribute("role", "menu");
  menu.innerHTML = `${m.texto ? '<button type="button" role="menuitem" data-a="copiar">📋 Copiar</button>' : ""}<button type="button" role="menuitem" data-a="borrar" class="peligro">🗑 Eliminar para todos</button>`;
  document.body.append(menu);
  const r = menu.getBoundingClientRect();
  menu.style.left = `${Math.max(8, Math.min(x - r.width, innerWidth - r.width - 8))}px`;
  menu.style.top = `${Math.max(8, Math.min(y, innerHeight - r.height - 8))}px`;
  menu.onclick = async (e) => {
    const a = e.target.closest("[data-a]")?.dataset.a;
    menu.remove();
    if (a === "copiar") navigator.clipboard?.writeText(m.texto).then(() => aviso("Mensaje copiado")).catch(() => {});
    if (a === "borrar") {
      if (!confirm("¿Eliminar este mensaje para todos? Tu amigo dejará de verlo.")) return;
      try { const r2 = await api(`/api/chat/${activo}/${m.id}/`, undefined, "DELETE"); llenarBurbuja(d, r2.mensaje); cargarLista().catch(() => {}); }
      catch (x) { aviso(x.message, true); }
    }
  };
  setTimeout(() => addEventListener("pointerdown", function fuera(e) { if (!menu.contains(e.target)) { menu.remove(); removeEventListener("pointerdown", fuera); } }), 0);
}
$("log").addEventListener("click", (e) => {
  const b = e.target.closest(".cm-mas");
  if (b) { const r = b.getBoundingClientRect(); menuMensaje(b.closest(".cm"), r.right, r.bottom + 4); }
});
{
  let t = 0;
  $("log").addEventListener("touchstart", (e) => {
    const d = e.target.closest(".cm.yo:not(.borrado)");
    if (!d || e.touches.length > 1) return;
    const { clientX: x, clientY: y } = e.touches[0];
    t = setTimeout(() => { navigator.vibrate?.(15); menuMensaje(d, x, y); }, 500);
  }, { passive: true });
  for (const ev of ["touchmove", "touchend", "touchcancel"]) $("log").addEventListener(ev, () => clearTimeout(t), { passive: true });
  $("log").addEventListener("contextmenu", (e) => { const d = e.target.closest(".cm.yo:not(.borrado)"); if (d) { e.preventDefault(); menuMensaje(d, e.clientX, e.clientY); } });
}

function nombreDia(fecha) {
  const d = new Date(fecha);
  if (Number.isNaN(d.getTime())) return "";
  const hoy = new Date(); hoy.setHours(0, 0, 0, 0);
  const dias = Math.round((hoy - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
  if (dias === 0) return "Hoy";
  if (dias === 1) return "Ayer";
  return d.toLocaleDateString("es", { weekday: dias < 7 ? "long" : undefined, day: "numeric", month: "long", year: d.getFullYear() !== hoy.getFullYear() ? "numeric" : undefined });
}
function pintar(ms, { forzar = false } = {}) {
  const log = $("log");
  const abajo = forzar || log.scrollHeight - log.scrollTop - log.clientHeight < 80;
  for (const m of ms) {
    const dia = m.fecha ? nombreDia(m.fecha) : "";
    if (dia && dia !== ultimoDia) {
      const sep = document.createElement("div"); sep.className = "c-dia"; sep.textContent = dia; log.appendChild(sep);
      ultimoDia = dia; ultimoAutor = null;
    }
    const d = document.createElement("div");
    d.className = "cm" + (m.yo ? " yo" : "") + (ultimoAutor === m.yo ? " seguido" : "") + (m.adjuntos?.length && !m.texto ? " solo-adj" : "");
    d.dataset.id = m.id;
    llenarBurbuja(d, m);
    log.appendChild(d); ultimo = m.id; ultimoAutor = m.yo;
  }
  if (abajo || !ms.length) log.scrollTop = log.scrollHeight;
}

async function abrir(id) {
  activo = id; ultimo = 0; ultimoDia = ""; ultimoAutor = null;
  $("log").innerHTML = "";
  $("vacio").hidden = true; ["cab", "log", "fMsg"].forEach((x) => { $(x).hidden = false; });
  mostrarEmojis(false); menu(false);
  const amigo = datos.amigos.find((a) => a.id === id);
  $("cNombre").textContent = amigo?.nombre ?? "";
  $("cAlias").textContent = amigo ? `@${amigo.alias}` : "";
  $("cAv").outerHTML = amigo ? avatar(amigo).replace('class="c-av', 'id="cAv" class="c-av') : '<span class="c-av" id="cAv"></span>';
  $("cg").classList.add("en-chat");
  listaChats(false);
  document.body.classList.add("en-chat");
  if (!new URLSearchParams(location.search).has("con")) history.pushState({ chat: id }, "", `?con=${id}`);
  try {
    const ms = (await api(`/api/chat/${id}/`)).mensajes;
    if (!ms.length) { const v = document.createElement("p"); v.className = "nota c-saludo"; v.textContent = "Aún no hay mensajes. ¡Saluda y empiecen a practicar juntos!"; $("log").append(v); }
    else pintar(ms, { forzar: true });
  } catch (e) { aviso(e.message, true); }
  cargarLista().catch(() => {});
  if (!TACTIL) $("texto").focus();
}
function cerrar() {
  activo = null;
  $("vacio").hidden = false; ["cab", "log", "fMsg"].forEach((x) => { $(x).hidden = true; });
  mostrarEmojis(false); menu(false);
  $("cg").classList.remove("en-chat");
  document.body.classList.remove("en-chat");
  if (new URLSearchParams(location.search).has("con")) history.replaceState(null, "", location.pathname);
  cargarLista().catch(() => {});
}
// El botón «atrás» del celular vuelve a la lista en vez de salir de Chats.
addEventListener("popstate", () => { if (activo) cerrar(); });
function mostrarEmojis(si) { $("emojis").hidden = !si; $("verEmojis").setAttribute("aria-expanded", String(si)); }
function menu(si) { $("cMenu").hidden = !si; $("cMas").setAttribute("aria-expanded", String(si)); }
$("verEmojis").onclick = () => mostrarEmojis($("emojis").hidden);
$("cMas").onclick = (e) => { e.stopPropagation(); menu($("cMenu").hidden); };

/* ===== Perfil del amigo: toca su foto o su nombre arriba del chat (o ⋮ → Ver perfil) ===== */
const NOMBRE_TIPO = { marco: "Marco", fondo: "Fondo", tema: "Tema", cursor: "Puntero", efecto: "Efecto al hacer clic", dedo: "Rastro" };
const RAREZA = { comun: "Común", raro: "Raro", epico: "Épico", legendario: "Legendario", mitico: "Mítico" };
const fecha = (iso) => iso ? new Date(iso + "T12:00:00").toLocaleDateString("es", { day: "numeric", month: "long", year: "numeric" }) : "—";
async function abrirPerfil() {
  if (!activo) return;
  menu(false);
  const dlg = $("dlgPerfil"), c = $("pfCuerpo");
  c.innerHTML = '<p class="nota">Cargando perfil…</p>';
  dlg.showModal();
  let p;
  try { p = await api(`/api/amigos/${activo}/perfil/`); }
  catch (x) { c.innerHTML = `<p class="nota">${esc(x.message)}</p>`; return; }
  const max = Math.max(1, ...p.semana.map((d) => d.xp));
  const dias = ["D", "L", "M", "M", "J", "V", "S"];
  const foto = fotoDe({ foto: p.foto, avatar: p.avatar, nombre: p.nombre, cosmeticos: { marco: p.equipados.marco?.clave } }, { tam: 84 });
  const barra = (v, t, color) => `<span class="pf-barra"><i style="width:${t ? Math.min(100, Math.round(v * 100 / t)) : 0}%;${color ? `background:${esc(color)}` : ""}"></i></span>`;
  c.innerHTML = `
    <section class="pf-top">
      <span class="pf-foto">${foto}</span>
      <div><h3 id="pfNombre">${esc(p.nombre)}</h3><small>@${esc(p.alias || "")} · ID ${esc(p.codigo || "")}</small>
        <div class="pf-chips">
          <span class="pf-chip">⭐ Nivel ${p.nivel}</span>
          <span class="pf-chip${p.racha_actual ? " fuego" : ""}">🔥 ${p.racha_actual} día${p.racha_actual === 1 ? "" : "s"} de racha</span>
          ${p.activo_hoy ? '<span class="pf-chip ok">✅ Practicó hoy</span>' : ""}
        </div></div>
    </section>
    <div class="pf-xp"><small>${p.xp_nivel}/100 XP para el nivel ${p.nivel + 1} · ${p.xp_total} XP en total</small>${barra(p.xp_nivel, 100)}</div>
    <section class="pf-stats">
      <div><b>${p.niveles_completados}</b><small>niveles de retos</small></div>
      <div><b>${p.estrellas}</b><small>estrellas</small></div>
      <div><b>${p.lecciones_total}</b><small>lecciones en Aprende</small></div>
      <div><b>${p.racha_maxima}</b><small>mejor racha</small></div>
      <div><b>${p.cosmeticos_total}</b><small>cosméticos</small></div>
    </section>
    ${p.curso_actual ? `<p class="pf-curso">Está aprendiendo <b style="color:${esc(p.curso_actual.color)}">${esc(p.curso_actual.nombre)}</b></p>` : ""}
    <section><h4>Esta semana</h4><div class="pf-semana">${p.semana.map((d) => `<span title="${d.xp} XP"><i style="height:${Math.round(d.xp * 100 / max)}%"></i><small>${dias[new Date(d.dia + "T12:00:00").getDay()]}</small></span>`).join("")}</div></section>
    ${p.cursos.length ? `<section><h4>Retos por curso</h4>${p.cursos.map((k) => `<div class="pf-fila"><span>${esc(k.nombre)}</span><small>${k.niveles}/${k.total} · ⭐ ${k.estrellas}</small>${barra(k.niveles, k.total, k.color)}</div>`).join("")}</section>` : ""}
    ${p.lecciones.length ? `<section><h4>Lecciones de Aprende</h4><div class="pf-tags">${p.lecciones.map((l) => `<span style="--c:${esc(l.color)}">${esc(l.nombre)} · ${l.hechas}</span>`).join("")}</div></section>` : ""}
    <section><h4>Lo que tiene puesto</h4><div class="pf-cosm">${Object.entries(NOMBRE_TIPO).map(([t, n]) => {
      const e = p.equipados[t];
      return `<div class="pf-c${e ? "" : " vacio"}"><span class="pf-prev" data-tipo="${t}" data-clave="${e ? esc(e.clave) : ""}"></span><small>${n}</small><b>${e ? esc(e.nombre) : "—"}</b>${e ? `<em class="r-${esc(e.rareza)}">${RAREZA[e.rareza] ?? esc(e.rareza)}</em>` : ""}</div>`;
    }).join("")}</div></section>
    ${p.intereses?.length ? `<section><h4>Le interesa</h4><div class="pf-tags">${p.intereses.map((i) => `<span>${esc(i)}</span>`).join("")}</div></section>` : ""}
    <p class="pf-fechas">En CódigoCamp desde el ${fecha(p.miembro_desde)} · Amigos desde el ${fecha(p.amigos_desde)}</p>
    <button class="btn pri pf-escribir" type="button" id="pfEscribir">💬 Escribirle</button>`;
  try {
    const { vistaPrevia } = await import("/js/cosmeticos.js");
    for (const el of c.querySelectorAll(".pf-prev[data-clave]:not([data-clave=''])")) { try { vistaPrevia(el, el.dataset.clave, el.dataset.tipo); } catch { /* sin vista previa */ } }
  } catch { /* sin vistas previas */ }
  $("pfEscribir").onclick = () => { dlg.close(); $("texto").focus(); };
}
$("verPerfil").onclick = abrirPerfil;
$("cab").addEventListener("click", (e) => { if (e.target.closest("#cAv, .c-cab-txt")) abrirPerfil(); });
$("dlgPerfilCerrar").onclick = () => $("dlgPerfil").close();
$("dlgPerfil").addEventListener("click", (e) => { if (e.target === e.currentTarget) e.currentTarget.close(); });
addEventListener("click", (e) => { if (!e.target.closest("#cMenu")) menu(false); });

/* ===== Buscar personas ===== */
let temporizador, busqueda = 0;
async function agregar(quien) {
  try {
    const r = await api("/api/amigos/agregar/", { usuario: quien });
    $("quien").value = ""; $("resultados").innerHTML = "";
    aviso(r.estado === "aceptada" ? `¡Ahora eres amigo de ${r.nombre}!` : `Solicitud enviada a ${r.nombre}`);
    cargarLista();
  } catch (x) { aviso(x.message, true); }
}
const ETQ = { amigo: "Ya son amigos", enviada: "Solicitud enviada", recibida: "Te envió solicitud" };
$("quien").oninput = () => {
  clearTimeout(temporizador);
  const q = $("quien").value.trim().replace(/^@/, "");
  if (q.length < 2) { $("resultados").innerHTML = ""; return; }
  temporizador = setTimeout(async () => {
    const n = ++busqueda;
    try {
      const { resultados } = await api(`/api/usuarios/buscar/?q=${encodeURIComponent(q)}`);
      if (n !== busqueda) return;
      $("resultados").innerHTML = resultados.length
        ? resultados.map((p) => `<div class="c-fila">${avatar(p)}<span><b>${esc(p.nombre)}</b><small>@${esc(p.alias)}</small></span>
            <span class="c-acc">${p.relacion === "amigo" || p.relacion === "enviada" ? `<small>${ETQ[p.relacion]}</small>` : `<button class="btn sm pri" type="button" data-u="${esc(p.alias)}">${p.relacion === "recibida" ? "Aceptar" : "Agregar"}</button>`}</span></div>`).join("")
        : '<p class="nota">Nadie coincide. Prueba con su ID o su @usuario exacto.</p>';
    } catch (x) { $("resultados").innerHTML = `<p class="nota">${esc(x.message)}</p>`; }
  }, 300);
};
$("resultados").onclick = (e) => { const b = e.target.closest("[data-u]"); if (b) agregar(b.dataset.u); };
$("fAgregar").onsubmit = (e) => { e.preventDefault(); const q = $("quien").value.trim(); if (q) agregar(q); };

/* ===== Resto de eventos ===== */
$("amigos").onclick = (e) => { const b = e.target.closest("[data-id]"); if (b) abrir(Number(b.dataset.id)); };
$("solicitudes").onclick = async (e) => {
  const b = e.target.closest("[data-r]");
  if (!b) return;
  try { await api(`/api/amigos/${b.dataset.r}/responder/`, { aceptar: b.dataset.a === "1" }); aviso(b.dataset.a === "1" ? "¡Ahora son amigos!" : "Solicitud rechazada"); }
  catch (x) { aviso(x.message, true); }
  cargarLista();
};
const copiar = (texto, ok) => navigator.clipboard?.writeText(texto).then(() => aviso(ok)).catch(() => aviso(texto));
$("copiar").onclick = () => copiar(datos.yo.codigo, "ID copiado");
const enlaceInvitacion = () => `${location.origin}/pages/chats.html?agregar=${datos.yo.codigo}`;
$("invitar").onclick = async () => {
  const url = enlaceInvitacion();
  if (navigator.share && TACTIL) {   // en el celular: el menú de compartir (WhatsApp, SMS, correo…)
    try { await navigator.share({ title: "CódigoCamp", text: "¡Aprende a programar conmigo en CódigoCamp! Agrégame:", url }); return; }
    catch (x) { if (x.name === "AbortError") return; }
  }
  copiar(url, "Enlace copiado: mándalo a quien quieras invitar");
};

/* ===== Contactos del teléfono ===== */
$("contactos").onclick = async () => {
  const m = await import("/js/contactos.js");
  const dlg = $("dlgContactos"), cuerpo = $("dlgContCuerpo");
  dlg.showModal();
  if (!m.puedeLeerContactos()) {
    cuerpo.innerHTML = `<p class="nota">Tu navegador no permite elegir contactos. Copia tu enlace de invitación y compártelo.</p>
      <button class="c-btn pri" type="button" data-copiar-inv>📋 Copiar enlace de invitación</button>`;
    return;
  }
  cuerpo.innerHTML = `<p class="nota">Cargando…</p>`;
  try {
    const lista = await m.leerContactos();
    const { encontrados, otros } = await m.cruzarContactos(lista, api);
    const enlace = enlaceInvitacion();
    const fila = (x) => `<li class="ct-fila">${avatar(x)}<span class="ct-txt"><b>${esc(x.nombre)}</b><small>@${esc(x.alias)}${x.contacto && x.contacto !== x.nombre ? " · " + esc(x.contacto) : ""}</small></span>
      ${x.relacion === "amigo" ? `<span class="ct-ok">✓ Amigos</span>` : x.relacion === "enviada" ? `<span class="ct-ok">Solicitud enviada</span>`
        : `<button class="c-btn pri" type="button" data-agregar-ct="${esc(x.alias)}">${x.relacion === "recibida" ? "Aceptar solicitud" : "Agregar amigo"}</button>`}</li>`;
    const invitar = (c, i) => { const e = m.enlacesInvitacion(c, enlace);
      return `<li class="ct-fila"><span class="c-av">${esc((c.nombre || "?").charAt(0).toUpperCase())}</span><span class="ct-txt"><b>${esc(c.nombre || (c.tel || c.email || [])[0] || "")}</b><small>${esc((c.tel || [])[0] || (c.email || [])[0] || "")}</small></span>
        <span class="ct-inv">${e.whatsapp ? `<a class="c-btn" href="${e.whatsapp}" ${window.CodigoCampApp ? "" : 'target="_blank" rel="noopener"'} title="Invitar por WhatsApp">WhatsApp</a>` : ""}${e.sms ? `<a class="c-btn" href="${e.sms}" title="Invitar por mensaje">SMS</a>` : ""}${e.correo ? `<a class="c-btn" href="${e.correo}" title="Invitar por correo">Correo</a>` : ""}</span></li>`; };
    cuerpo.innerHTML = (encontrados.length ? `<h3>Ya está en CódigoCamp (${encontrados.length})</h3><ul class="ct-lista">${encontrados.map(fila).join("")}</ul>`
      : `<p class="nota">Ninguno de esos contactos está en CódigoCamp todavía. ¡Invítalos!</p>`)
      + (otros.length ? `<h3>Invitar (${otros.length})</h3><ul class="ct-lista">${otros.slice(0, 300).map(invitar).join("")}</ul>` : "");
  } catch (x) {
    if (x.name === "AbortError" || x.name === "InvalidStateError") { dlg.close(); return; }
    cuerpo.innerHTML = `<p class="nota">${esc(x.message)}</p><button class="c-btn pri" type="button" data-copiar-inv>📋 Copiar enlace de invitación</button>`;
  }
};
$("dlgContCerrar").onclick = () => $("dlgContactos").close();
$("dlgContactos").onclick = async (e) => {
  if (e.target === e.currentTarget) return e.currentTarget.close();   // clic fuera del panel
  if (e.target.closest("[data-copiar-inv]")) return copiar(enlaceInvitacion(), "Enlace copiado: mándalo a quien quieras invitar");
  const b = e.target.closest("[data-agregar-ct]");
  if (b) { b.disabled = true; await agregar(b.dataset.agregarCt); b.replaceWith(Object.assign(document.createElement("span"), { className: "ct-ok", textContent: "✓ Listo" })); }
};
$("volver").onclick = () => { if (history.state?.chat) history.back(); else cerrar(); };
// Eliminar chat: desaparece solo de tu vista; tu amigo conserva toda la conversación.
$("borrarChat").onclick = async () => {
  menu(false);
  if (!activo) return;
  const amigo = datos.amigos.find((a) => a.id === activo);
  if (!confirm(`¿Eliminar el chat con ${amigo?.nombre ?? "este amigo"}?\n\nSe borra solo para ti: ${amigo?.nombre ?? "tu amigo"} seguirá viendo la conversación. Si te vuelve a escribir, verás los mensajes nuevos.`)) return;
  try {
    await api(`/api/chat/${activo}/`, undefined, "DELETE");
    $("log").innerHTML = '<p class="nota c-saludo">Eliminaste este chat de tu vista. Los mensajes nuevos aparecerán aquí.</p>';
    ultimo = 0; ultimoDia = ""; ultimoAutor = null;
    aviso("Chat eliminado solo para ti");
    cargarLista().catch(() => {});
  } catch (x) { aviso(x.message, true); }
};
$("quitar").onclick = async () => {
  menu(false);
  if (!activo || !confirm("¿Quitar a este amigo? Se borrará la conversación.")) return;
  try { await api(`/api/amigos/${activo}/quitar/`, {}); cerrar(); cargarLista(); } catch (x) { aviso(x.message, true); }
};
$("emojis").innerHTML = ["👍", "😂", "🎉", "🔥", "💻", "🤔", "❓", "🙌"].map((e) => `<button type="button" class="btn sm" aria-label="Insertar ${e}">${e}</button>`).join("");
$("emojis").onclick = (e) => {
  const b = e.target.closest("button"); if (!b) return;
  const t = $("texto"); t.setRangeText(b.textContent, t.selectionStart, t.selectionEnd, "end"); t.focus();
  actualizarEnviar();
};
const actualizarEnviar = () => { $("fMsg").querySelector("[type=submit]").disabled = !$("texto").value.trim() && !adj.hay(); };
$("texto").addEventListener("input", actualizarEnviar);
const adj = crearAdjuntador({ boton: $("clip"), entrada: $("archivosMsg"), bandeja: $("bandeja"), zona: document.querySelector(".c-conv"), destino: "chat" });
$("fMsg").onsubmit = async (e) => {
  e.preventDefault();
  const texto = $("texto").value.trim();
  if ((!texto && !adj.hay()) || !activo) return;
  const boton = $("fMsg").querySelector("[type=submit]");
  boton.disabled = true;
  try {
    const adjuntos = await adj.listos();
    const r = await api(`/api/chat/${activo}/?despues=${ultimo}`, { texto, adjuntos });
    if (r.desafios_completados?.length) import("/js/cofres.js").then((m) => m.avisarPremios(r.desafios_completados)).catch(() => {});
    adj.limpiar();
    $("texto").value = "";
    $("log").querySelector(".c-saludo")?.remove();
    mostrarEmojis(false);
    pintar(r.mensajes, { forzar: true });
    sonar("enviar");
  } catch (x) { aviso(x.message, true); }
  actualizarEnviar();
  if (!TACTIL) $("texto").focus();
};
new MutationObserver(() => actualizarEnviar()).observe($("bandeja"), { childList: true });
actualizarEnviar();

await cargarLista();
// Enlace de invitación: /pages/chats.html?agregar=CODIGO
const invitado = new URLSearchParams(location.search).get("agregar");
if (invitado) { history.replaceState(null, "", location.pathname); if (invitado.toUpperCase() !== datos.yo.codigo) await agregar(invitado); }
{ const con = Number(new URLSearchParams(location.search).get("con")); if (con && datos.amigos.some((a) => a.id === con)) abrir(con); else if (con) history.replaceState(null, "", location.pathname); }
setInterval(async () => { if (!document.hidden && activo) { try { const r = await api(`/api/chat/${activo}/?despues=${ultimo}`); if (r.mensajes.length) $("log").querySelector(".c-saludo")?.remove(); if (r.mensajes.some((m) => !m.yo)) sonar("recibir"); pintar(r.mensajes); aplicarBorrados(r.borrados); } catch {} } }, 4000);
setInterval(() => { if (!document.hidden) cargarLista().catch(() => {}); }, 15000);

// PC: la lista de chats es un menú hamburguesa (en el celular la lista es la pantalla principal)
function listaChats(abrir) {
  const pc = matchMedia("(min-width: 761px)").matches;
  const si = pc && abrir;
  $("cg").classList.toggle("lista-abierta", si);
  $("cVelo").hidden = !si;
  $("verAmigos").setAttribute("aria-expanded", String(si));
  if (si) setTimeout(() => $("quien")?.focus({ preventScroll: true }), 230);
}
$("verAmigos").onclick = () => listaChats(!$("cg").classList.contains("lista-abierta"));
$("verAmigos2").onclick = () => listaChats(true);
$("cerrarAmigos").onclick = () => listaChats(false);
$("cVelo").onclick = () => listaChats(false);
addEventListener("keydown", (e) => { if (e.key === "Escape") listaChats(false); });
if (!new URLSearchParams(location.search).has("con")) listaChats(true);
