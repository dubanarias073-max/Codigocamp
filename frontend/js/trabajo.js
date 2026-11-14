// Trabajo: espacio de trabajo con aspecto y comportamiento de VS Code.
// Este archivo solo conecta las piezas (js/trabajo/*): guardado, explorador, editor, terminal, vista previa y asistente.
import { api, aviso as avisoSimple, iniciar } from "/js/app.js";
import { Almacen } from "/js/trabajo/almacen.js";
import { dialogo, aviso } from "/js/trabajo/dialogos.js";
import { Editor, unidadDeIndentacion } from "/js/trabajo/editor.js";
import { crearEjecutores } from "/js/trabajo/ejecucion.js";
import { Explorador } from "/js/trabajo/explorador.js";
import * as FS from "/js/trabajo/fs.js";
import { iconoArchivo } from "/js/trabajo/iconos.js";
import { infoLenguaje } from "/js/trabajo/resaltado.js";
import { Shell, comandoParaArchivo } from "/js/trabajo/shell.js";
import { PanelInferior, iconoPanel } from "/js/trabajo/terminal.js";
import { construirVistaPrevia, paginaPrincipal, resolverEnlace } from "/js/trabajo/vista.js";

const { user, prog } = await iniciar("trabajo");
const $ = (id) => document.getElementById(id);
const VISTA = "::vista";
const STORAGE = `cc_trabajo_${user.id}`;
const UI_STORAGE = `cc_trabajo_ui_${user.id}`;
const CHAT_STORAGE = `cc_trabajo_chat_${user.id}`;
const HIST_STORAGE = `cc_trabajo_hist_${user.id}`;

// Los elementos del menú lateral no tienen texto visible aquí (es una barra de iconos): se pone como ayuda.
document.querySelectorAll(".trabajo-app .lado .nav-i").forEach((a) => { const t = a.querySelector(".t")?.textContent.trim(); if (t) { a.title = t; a.setAttribute("aria-label", t); } });

// ------------------------------------------------------------------ estado de la interfaz ----
const uiGuardada = (() => { try { return JSON.parse(localStorage.getItem(UI_STORAGE)) || null; } catch { return null; } })();
const ui = {
  abiertos: [], activo: null, expandidas: [], panel: false, altoPanel: 260, anchoExp: 260, explorador: true, asistente: null,
  ...(uiGuardada || {}),
};
const primeraVisita = !uiGuardada;
const guardarUI = () => {
  ui.expandidas = [...expandidas];
  try { localStorage.setItem(UI_STORAGE, JSON.stringify(ui)); } catch { /* sin espacio: se pierde solo la disposición */ }
};
const expandidas = new Set(Array.isArray(ui.expandidas) ? ui.expandidas : []);

// ------------------------------------------------------------------------------- guardado ----
const textoEstado = {
  iniciando: ["Sincronizando…", "", "Comparando tu proyecto con tu cuenta"],
  guardando: ["Guardando…", "guardando", "Guardando en tu cuenta"],
  guardado: ["✓ Guardado", "", "Guardado en tu cuenta (clic para guardar ahora)"],
  sinconexion: ["⚠ Sin conexión", "problema", "Sin conexión con el servidor. Tu trabajo está a salvo en este navegador y se subirá solo al volver la conexión."],
  sesion: ["⚠ Sesión vencida", "problema", "Tu sesión venció. Recarga la página e inicia sesión de nuevo."],
  error: ["⚠ No se pudo guardar", "problema", "El servidor rechazó el guardado."],
  errorLocal: ["⚠ Sin espacio local", "problema", "No hay espacio para guardar en este navegador."],
};
const avisosEstado = new Set();
function pintarEstado(estado, mensaje) {
  const [texto, clase, ayuda] = textoEstado[estado] ?? textoEstado.guardado;
  const el = $("estadoGuardado");
  el.textContent = texto;
  el.className = `estado-item ${clase}`.trim();
  el.title = mensaje || ayuda;
  $("expNube").textContent = estado === "guardado" ? "CUENTA" : estado === "guardando" || estado === "iniciando" ? "…" : "LOCAL";
  if (["sinconexion", "sesion", "error", "errorLocal"].includes(estado) && !avisosEstado.has(estado)) {
    avisosEstado.add(estado);
    aviso(mensaje || ayuda, { tipo: "error", ms: 9000 });
  }
  if (estado === "guardado") avisosEstado.clear();
}

const almacen = new Almacen({
  clave: STORAGE,
  alEstado: pintarEstado,
  alRemoto: () => proyectoCambio({ origen: "remoto" }),
  resolverConflicto: ({ local, nube }) => dialogo({
    titulo: "Hay dos versiones de tu proyecto",
    mensaje: `En este navegador hay cambios que no se llegaron a sincronizar (${local.archivos} archivos), y tu cuenta tiene otra versión distinta (${nube.archivos} archivos).\n\n¿Cuál quieres conservar? La otra se descartará.`,
    botones: [{ texto: "La de este navegador", valor: "local" }, { texto: "La de mi cuenta", valor: "nube" }],
  }),
});
await almacen.iniciar();
const proyecto = () => almacen.proyecto;

// --------------------------------------------------------------------- terminal y shell ----
const ejecutores = crearEjecutores({ api });
const shell = new Shell({
  proyecto, usuario: user.nombre || "estudiante", ejecutores,
  cambio: (info) => proyectoCambio(info),
  abrir: (ruta) => abrir(ruta, { enfocar: false }),
});
const panel = new PanelInferior({
  raiz: $("terminalPanel"), shell, proyecto, claveHistorial: HIST_STORAGE,
  alCambiar: (abierto) => {
    ui.panel = abierto;
    $("terminalPanel").hidden = !abierto;
    $("sashPanel").hidden = !abierto || panel.maximizado;
    $("contenido").classList.toggle("panel-max", abierto && panel.maximizado);
    $("terminalToggle").setAttribute("aria-expanded", String(abierto));
    $("terminalToggle").classList.toggle("activo", abierto);
    guardarUI();
  },
});
document.documentElement.style.setProperty("--alto-panel", "260px");
$("ide").style.setProperty("--alto-panel", `${ui.altoPanel}px`);

// -------------------------------------------------------------------------------- editores ----
const editores = new Map();

function editorPara(ruta) {
  let ed = editores.get(ruta);
  if (ed) return ed;
  ed = new Editor({
    ruta, texto: proyecto().files[ruta] ?? "",
    alCambiar: (texto) => { proyecto().files[ruta] = texto; proyectoCambio({ origen: "editor", ruta }); },
    alCursor: (pos) => { if (ui.activo === ruta) pintarCursor(pos); },
    alAtajo: (accion) => { if (accion === "guardar") guardarAhora(); else ejecutarActual(); },
  });
  editores.set(ruta, ed);
  $("editores").appendChild(ed.raiz);
  return ed;
}

function pintarCursor(pos) {
  const ed = editores.get(ui.activo);
  if (!ed) return;
  $("posicionCursor").textContent = `Ln ${pos.linea}, Col ${pos.col}${pos.seleccion ? ` (${pos.seleccion} sel.)` : ""}`;
  const u = unidadDeIndentacion(ed.ext);
  $("estIndent").textContent = u === "\t" ? "Tabulaciones: 4" : `Espacios: ${u.length}`;
  $("lenguajeArchivo").textContent = ed.lenguaje;
}

// -------------------------------------------------------------------------- pestañas y vista ----
const esArchivoAbierto = (r) => r !== VISTA;

function pintarPestanas() {
  const x = iconoPanel("cerrar");
  $("pestanas").innerHTML = ui.abiertos.map((r) => {
    const on = r === ui.activo;
    const nombre = r === VISTA ? "Vista previa" : FS.nombreBase(r);
    const icono = r === VISTA ? '<svg class="ico-vista" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 8S4 3.5 8 3.5 14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8z" fill="none" stroke="currentColor" stroke-width="1.1"/><circle cx="8" cy="8" r="2" fill="none" stroke="currentColor" stroke-width="1.1"/></svg>' : iconoArchivo(r);
    return `<div class="pestana${on ? " on" : ""}" role="tab" aria-selected="${on}" tabindex="${on ? 0 : -1}" data-ruta="${r.replace(/"/g, "&quot;")}" title="${r === VISTA ? "Vista previa de la página" : r}">${icono}<span class="nom">${nombre}</span><button type="button" class="cerrar" tabindex="-1" aria-label="Cerrar ${nombre}">${x}</button></div>`;
  }).join("");
  $("pestanas").querySelector(".pestana.on")?.scrollIntoView({ block: "nearest", inline: "nearest" });
}

function pintarMigas() {
  const r = ui.activo;
  if (!r) { $("migas").innerHTML = ""; return; }
  const partes = r === VISTA ? ["mi-proyecto", paginaVista || "Vista previa"] : ["mi-proyecto", ...r.split("/")];
  $("migas").innerHTML = partes.map((p, i) => `<span class="${i === partes.length - 1 ? "ultima" : ""}">${p.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</span>`).join("");
}

function pintarGit() {
  const g = proyecto().git;
  $("estRama").hidden = !g.initialized;
  $("estRamaNombre").textContent = g.branch;
}

let paginaVista = null;

function activar(ruta, { enfocar = true } = {}) {
  for (const ed of editores.values()) if (!ed.raiz.hidden) ed.ocultar();
  ui.activo = ruta;
  $("panelVista").hidden = ruta !== VISTA;
  $("bienvenida").hidden = ruta !== null;
  if (ruta === VISTA) renderVista();
  else if (ruta) {
    const ed = editorPara(ruta);
    ed.mostrar();
    if (enfocar) ed.enfocar();
    pintarCursor({ linea: 1, col: 1, seleccion: 0 });
    ed.ta.dispatchEvent(new Event("focus"));
  }
  if (ruta === null || ruta === VISTA) {
    $("posicionCursor").textContent = "";
    $("lenguajeArchivo").textContent = ruta === VISTA ? "HTML" : "";
    $("estIndent").textContent = "";
  }
  explorador.marcarActivo(ruta && esArchivoAbierto(ruta) ? ruta : null);
  pintarPestanas();
  pintarMigas();
  guardarUI();
}

function abrir(ruta, { enfocar = true } = {}) {
  if (!FS.tieneArchivo(proyecto(), ruta)) return;
  if (!ui.abiertos.includes(ruta)) ui.abiertos.push(ruta);
  activar(ruta, { enfocar });
}

function cerrarPestana(ruta) {
  const i = ui.abiertos.indexOf(ruta);
  if (i < 0) return;
  ui.abiertos.splice(i, 1);
  const ed = editores.get(ruta);
  if (ed) { ed.destruir(); editores.delete(ruta); }
  if (ui.activo === ruta) activar(ui.abiertos[Math.min(i, ui.abiertos.length - 1)] ?? null);
  else { pintarPestanas(); guardarUI(); }
}

function renderVista() {
  const py = proyecto();
  paginaVista = paginaPrincipal(py, paginaVista);
  if (!paginaVista) {
    $("vista").srcdoc = '<p style="font:14px system-ui;padding:24px;color:#555">Crea un archivo <b>.html</b> (por ejemplo index.html) para ver aquí tu página.</p>';
    $("vistaRuta").textContent = "Vista previa";
    return;
  }
  panel.limpiarConsola();
  $("vistaRuta").textContent = `Vista previa · ${paginaVista}`;
  $("vista").srcdoc = construirVistaPrevia(py, paginaVista);
  pintarMigas();
}

function abrirVista(preferida = null) {
  const py = proyecto();
  const pagina = paginaPrincipal(py, preferida);
  if (!pagina) { aviso("Crea un archivo .html (por ejemplo index.html) para ver la vista previa.", { tipo: "error" }); return; }
  paginaVista = pagina;
  if (!ui.abiertos.includes(VISTA)) ui.abiertos.push(VISTA);
  activar(VISTA);
}

window.addEventListener("message", (e) => {
  const m = e.data;
  if (!m || e.source !== $("vista").contentWindow) return;
  if (m.cc === "consola") panel.escribirConsola(m.nivel, String(m.texto).slice(0, 4000));
  else if (m.cc === "nav") {
    const destino = resolverEnlace(proyecto(), paginaVista || "", m.href);
    if (destino) { paginaVista = destino; renderVista(); } else panel.escribirConsola("warn", `El enlace «${m.href}» no apunta a ninguna página de tu proyecto.`);
  }
});

function ejecutarActual() {
  const ruta = ui.activo;
  if (ruta === VISTA) { renderVista(); return; }
  if (!ruta) { aviso("Abre un archivo para ejecutarlo.", { tipo: "info" }); return; }
  if (/\.(html?|css)$/i.test(ruta)) { abrirVista(/\.html?$/i.test(ruta) ? ruta : null); return; }
  const comando = comandoParaArchivo(ruta, panel.activa?.sesion.cwd ?? "");
  if (!comando) { aviso(`No sé ejecutar archivos .${FS.extension(ruta) || "sin extensión"}. Los de texto solo se editan.`); return; }
  panel.correr(comando);
}

// ------------------------------------------------------------------- cambios del proyecto ----
function renombrarRutas(de, a) {
  const cambiar = (r) => (r === de ? a : FS.dentroDe(r, de) && r !== VISTA ? a + r.slice(de.length) : r);
  ui.abiertos = ui.abiertos.map(cambiar);
  if (ui.activo) ui.activo = cambiar(ui.activo);
  for (const [ruta, ed] of [...editores]) {
    const nueva = cambiar(ruta);
    if (nueva !== ruta) { editores.delete(ruta); editores.set(nueva, ed); ed.renombrar(nueva); }
  }
  for (const c of [...expandidas]) { const n = cambiar(c); if (n !== c) { expandidas.delete(c); expandidas.add(n); } }
  if (paginaVista) paginaVista = cambiar(paginaVista);
}

function reconciliarPestanas() {
  const py = proyecto();
  const antes = ui.activo;
  ui.abiertos = ui.abiertos.filter((r) => r === VISTA || FS.tieneArchivo(py, r));
  for (const [ruta, ed] of [...editores]) if (!FS.tieneArchivo(py, ruta)) { ed.destruir(); editores.delete(ruta); }
  for (const c of [...expandidas]) if (!FS.esCarpeta(py, c)) expandidas.delete(c);
  if (ui.activo !== null && !ui.abiertos.includes(ui.activo)) ui.activo = ui.abiertos[ui.abiertos.length - 1] ?? null;
  return antes !== ui.activo;
}

function ofrecerDeshacer(ruta, eliminado) {
  aviso(`Se eliminó «${FS.nombreBase(ruta)}».`, {
    ms: 9000,
    accion: {
      texto: "Deshacer",
      fn: () => {
        FS.restaurar(proyecto(), eliminado);
        // Se deja visible lo restaurado: se abren la carpeta y sus padres.
        for (let c = FS.esCarpeta(proyecto(), ruta) ? ruta : FS.carpetaDe(ruta); c; c = FS.carpetaDe(c)) expandidas.add(c);
        proyectoCambio({ origen: "explorador", restaurado: ruta });
        explorador.seleccionar(ruta);
      },
    },
  });
}

/** Punto único por el que pasa todo cambio del proyecto (editor, explorador, terminal, git, ejecución). */
function proyectoCambio(info = {}) {
  const { origen } = info;
  if (origen === "aviso") { aviso(info.error, { tipo: "error" }); return; }
  if (origen === "ui") { guardarUI(); return; }
  if (origen !== "remoto") almacen.cambiar();
  if (info.movido) renombrarRutas(info.movido[0], info.movido[1]);
  if (info.eliminado && origen === "terminal") ofrecerDeshacer(info.borrado, info.eliminado);
  const cambioActivo = reconciliarPestanas();
  if (origen !== "editor") for (const [ruta, ed] of editores) ed.establecer(proyecto().files[ruta] ?? "");
  if (cambioActivo || info.movido || origen === "remoto") activar(ui.activo, { enfocar: false });
  else if (origen !== "editor") { explorador.render(); pintarPestanas(); pintarMigas(); }
  if (origen !== "editor") pintarGit();
  guardarUI();
}

async function guardarAhora() {
  const ok = await almacen.guardarAhora();
  if (ok) aviso("Proyecto guardado en tu cuenta.", { ms: 2200 });
}

// ------------------------------------------------------------------------------ explorador ----
const explorador = new Explorador({
  raiz: $("arbol"), proyecto, expandidas,
  alAbrir: (ruta) => abrir(ruta),
  alCambiar: proyectoCambio,
  alBorrar: ofrecerDeshacer,
  alAbrirTerminalEn: (carpeta) => panel.correr(`cd ${FS.rutaAbsoluta(carpeta)}`),
});
$("nuevoArchivo").onclick = () => explorador.nuevo("archivo");
$("nuevaCarpeta").onclick = () => explorador.nuevo("carpeta");
$("colapsarTodo").onclick = () => { expandidas.clear(); explorador.render(); guardarUI(); };

// ------------------------------------------------------------------ eventos de la página ----
$("pestanas").addEventListener("click", (e) => {
  const tab = e.target.closest(".pestana");
  if (!tab) return;
  if (e.target.closest(".cerrar")) cerrarPestana(tab.dataset.ruta);
  else if (tab.dataset.ruta !== ui.activo) activar(tab.dataset.ruta);
});
$("pestanas").addEventListener("auxclick", (e) => { const tab = e.target.closest(".pestana"); if (tab && e.button === 1) { e.preventDefault(); cerrarPestana(tab.dataset.ruta); } });
$("pestanas").addEventListener("keydown", (e) => {
  const tab = e.target.closest(".pestana");
  if (!tab) return;
  const i = ui.abiertos.indexOf(tab.dataset.ruta);
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); activar(tab.dataset.ruta); }
  else if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); const n = ui.abiertos[(i + (e.key === "ArrowRight" ? 1 : -1) + ui.abiertos.length) % ui.abiertos.length]; activar(n, { enfocar: false }); $("pestanas").querySelector(".pestana.on")?.focus(); }
  else if (e.key === "Delete") cerrarPestana(tab.dataset.ruta);
});
$("ejecutar").onclick = ejecutarActual;
$("vistaPrevia").onclick = () => abrirVista(ui.activo && /\.html?$/i.test(ui.activo) ? ui.activo : paginaVista);
$("vistaRecargar").onclick = renderVista;
$("guardar").onclick = guardarAhora;
$("estadoGuardado").onclick = guardarAhora;
$("estRama").onclick = () => panel.correr("git status");
$("terminalToggle").onclick = () => panel.alternar();
$("bienvenida").addEventListener("click", (e) => {
  const a = e.target.closest("[data-accion]")?.dataset.accion;
  if (a === "nuevo-archivo") explorador.nuevo("archivo", "");
  else if (a === "terminal") panel.abrir();
  else if (a === "guardar") guardarAhora();
});

function alternarAsistente(mostrar = $("ide").classList.contains("sin-asistente")) {
  $("ide").classList.toggle("sin-asistente", !mostrar);
  $("asistenteToggle").setAttribute("aria-expanded", String(mostrar));
  ui.asistente = mostrar;
  guardarUI();
}
function alternarExplorador(mostrar = $("ide").classList.contains("sin-explorador")) {
  $("ide").classList.toggle("sin-explorador", !mostrar);
  ui.explorador = mostrar;
  guardarUI();
}
$("asistenteToggle").onclick = () => alternarAsistente();

document.addEventListener("keydown", (e) => {
  const ctrl = e.ctrlKey || e.metaKey;
  if (ctrl && (e.key === "`" || e.key.toLowerCase() === "j")) { e.preventDefault(); panel.alternar(); }
  else if (ctrl && e.key.toLowerCase() === "b") { e.preventDefault(); alternarExplorador(); }
  else if (ctrl && e.key.toLowerCase() === "s") { e.preventDefault(); guardarAhora(); }
});

// Divisores arrastrables (explorador y panel inferior)
function arrastre(sash, mover, terminar) {
  sash.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    sash.setPointerCapture(e.pointerId);
    sash.classList.add("arrastrando");
    document.body.style.userSelect = "none";
    const alMover = (ev) => mover(ev);
    const fin = () => {
      sash.removeEventListener("pointermove", alMover);
      sash.classList.remove("arrastrando");
      document.body.style.userSelect = "";
      terminar();
    };
    sash.addEventListener("pointermove", alMover);
    sash.addEventListener("pointerup", fin, { once: true });
    sash.addEventListener("pointercancel", fin, { once: true });
  });
}
const limitar = (v, a, b) => Math.max(a, Math.min(b, v));
const fijarAnchoExp = (w) => { ui.anchoExp = limitar(Math.round(w), 160, 520); $("ide").style.setProperty("--w-exp", `${ui.anchoExp}px`); };
const fijarAltoPanel = (h) => { const max = $("contenido").getBoundingClientRect().height - 120; ui.altoPanel = limitar(Math.round(h), 90, Math.max(120, max)); $("ide").style.setProperty("--alto-panel", `${ui.altoPanel}px`); };
arrastre($("sashExp"), (e) => fijarAnchoExp(e.clientX - $("ide").getBoundingClientRect().left - 56), guardarUI);
arrastre($("sashPanel"), (e) => fijarAltoPanel($("contenido").getBoundingClientRect().bottom - e.clientY), guardarUI);
$("sashExp").addEventListener("keydown", (e) => { if (e.key === "ArrowLeft" || e.key === "ArrowRight") { e.preventDefault(); fijarAnchoExp(ui.anchoExp + (e.key === "ArrowRight" ? 16 : -16)); guardarUI(); } });
$("sashPanel").addEventListener("keydown", (e) => { if (e.key === "ArrowUp" || e.key === "ArrowDown") { e.preventDefault(); fijarAltoPanel(ui.altoPanel + (e.key === "ArrowUp" ? 24 : -24)); guardarUI(); } });
$("sashPanel").addEventListener("dblclick", () => { fijarAltoPanel(260); guardarUI(); });

// Guardado al cerrar, al volver la red y entre pestañas
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") almacen.volcarAlSalir(); });
addEventListener("pagehide", () => almacen.volcarAlSalir());
addEventListener("online", () => { if (almacen.sucio || almacen.estado === "sinconexion") void almacen.guardarAhora(); });
addEventListener("storage", (e) => { if (e.key === STORAGE) almacen.recargarDesdeLocal(); });

// ---------------------------------------------------------------------------- asistente IA ----
let historial = [];
try {
  const guardado = JSON.parse(localStorage.getItem(CHAT_STORAGE));
  if (Array.isArray(guardado)) historial = guardado.filter((x) => x && ["yo", "tutor"].includes(x.rol) && typeof x.texto === "string").slice(-16);
} catch { /* historial ilegible: se empieza de cero */ }

function burbuja(rol, texto) {
  const d = document.createElement("div");
  d.className = `msg ${rol}`;
  d.textContent = texto;
  $("chat").append(d);
  $("chat").scrollTop = $("chat").scrollHeight;
  return d;
}

function pintarChat() {
  $("chat").replaceChildren();
  const curso = prog.curso_actual?.nombre;
  $("cursoAsistente").textContent = curso ? `Tutor de ${curso}` : "Tutor de CódigoCamp";
  burbuja("tutor", `¡Hola${user.nombre ? `, ${user.nombre.split(" ")[0]}` : ""}! Abre un archivo y cuéntame qué quieres resolver.`);
  historial.forEach((m) => burbuja(m.rol, m.texto));
}

$("preguntar").onsubmit = async (event) => {
  event.preventDefault();
  const pregunta = $("pregunta").value.trim();
  if (!pregunta || $("enviar").disabled) return;
  $("pregunta").value = "";
  burbuja("yo", pregunta);
  const espera = burbuja("tutor", "Revisando el archivo…");
  $("enviar").disabled = true;
  const archivo = ui.activo && ui.activo !== VISTA && FS.tieneArchivo(proyecto(), ui.activo) ? ui.activo : null;
  const ext = archivo ? FS.extension(archivo) : "";
  const codigo = archivo ? proyecto().files[archivo].slice(0, 2400) : "";
  const mensaje = `Estoy trabajando en ${archivo || "un proyecto nuevo"}${ext ? ` (${infoLenguaje(ext).nombre})` : ""}.\nSolicitud: ${pregunta}\n\nCódigo actual:\n\`\`\`${ext}\n${codigo}\n\`\`\``;
  try {
    const r = await api("/api/tutor/", { mensaje, historial: historial.slice(-10) });
    espera.textContent = r.respuesta;
    historial.push({ rol: "yo", texto: pregunta }, { rol: "tutor", texto: r.respuesta });
    historial = historial.slice(-16);
    try { localStorage.setItem(CHAT_STORAGE, JSON.stringify(historial)); }
    catch { avisoSimple("El tutor respondió, pero no se pudo guardar el historial en este navegador.", true); }
  } catch (error) {
    espera.textContent = error.message;
    espera.classList.add("error");
  }
  $("enviar").disabled = false;
  $("chat").scrollTop = $("chat").scrollHeight;
  $("pregunta").focus();
};

// ------------------------------------------------------------------------------- arranque ----
fijarAnchoExp(ui.anchoExp);
alternarExplorador(ui.explorador !== false);
alternarAsistente(ui.asistente === null ? innerWidth >= 1280 : Boolean(ui.asistente));
pintarChat();
pintarGit();
explorador.render();

const py0 = proyecto();
ui.abiertos = ui.abiertos.filter((r) => r === VISTA ? Boolean(paginaPrincipal(py0)) : FS.tieneArchivo(py0, r));
if (ui.activo !== null && !ui.abiertos.includes(ui.activo)) ui.activo = ui.abiertos[0] ?? null;
if (primeraVisita && !ui.abiertos.length) {
  const inicial = FS.tieneArchivo(py0, "index.html") ? "index.html" : Object.keys(py0.files).sort()[0];
  if (inicial) { ui.abiertos = [inicial]; ui.activo = inicial; }
}
if (ui.abiertos.includes(VISTA)) paginaVista = paginaPrincipal(py0);
activar(ui.activo, { enfocar: false });
if (ui.panel) panel.abrir({ enfocar: false });
