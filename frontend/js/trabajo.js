// Trabajo: espacio de trabajo con aspecto y comportamiento de VS Code.
// Este archivo solo conecta las piezas (js/trabajo/*): guardado, explorador, editor, terminal, vista previa y asistente.
import { api, aviso as avisoSimple, iniciar } from "/js/app.js";
import { Almacen } from "/js/trabajo/almacen.js";
import { crearAlmacenamiento } from "/js/trabajo/almacenamiento.js";
import { dialogo, aviso } from "/js/trabajo/dialogos.js";
import { Editor, unidadDeIndentacion } from "/js/trabajo/editor.js";
import { cargarPyodide, crearEjecutores, transpilarModulo } from "/js/trabajo/ejecucion.js";
import { modulosDePagina, proxyDeVite, usaModulos } from "/js/trabajo/modulos.js";
import { Explorador } from "/js/trabajo/explorador.js";
import * as FS from "/js/trabajo/fs.js";
import { clonar, publicar } from "/js/trabajo/github.js";
import { ClienteArchivos, esMarcador } from "/js/trabajo/archivos.js";
import { importarEn } from "/js/trabajo/importar.js";
import { Entradas } from "/js/trabajo/entradas.js";
import { VisorArchivo } from "/js/trabajo/visor.js";
import { EditorMonaco, alCambiarProblemas, cargarMonaco, crearDiff, problemas, sincronizarModelos } from "/js/trabajo/monaco.js";
import { abrirPaleta } from "/js/trabajo/paleta.js";
import { abrirBuscador } from "/js/trabajo/buscar.js";
import { PanelGit } from "/js/trabajo/gitpanel.js";
import { iconoArchivo } from "/js/trabajo/iconos.js";
import { infoLenguaje } from "/js/trabajo/resaltado.js";
import { carpetaDelPaquete, ejecutarNpm, ejecutarPip } from "/js/trabajo/paquetes.js";
import { Shell, comandoParaArchivo } from "/js/trabajo/shell.js";
import { ClienteBD } from "/js/trabajo/bd.js";
import { claveCuenta } from "/js/trabajo/cuenta.js";
import { cargarGitReal } from "/js/trabajo/cargargit.js";
import { SesionGitHub } from "/js/trabajo/sesiongithub.js";
import { PanelExtensiones, faltantesPython } from "/js/trabajo/extensiones.js";
import { almacenDeVenv, listarVenvs } from "/js/trabajo/venv.js";
import { aplicarCambio, contextoProyecto, extraerCambios, validarCambios } from "/js/trabajo/copiloto.js";
import { formato } from "/js/formato-ia.js";
import { CSS_ADJUNTOS, crearAdjuntador } from "/js/adjuntar.js";
import { PanelInferior, iconoPanel } from "/js/trabajo/terminal.js";
import { construirVistaPrevia, paginaPrincipal, paginaQueUsa, paginaRemotaConPuente, resolverEnlace, vistaDeRespuesta } from "/js/trabajo/vista.js";
import { incrustarRecursos, resolverDestino, urlDeArchivo } from "/js/trabajo/virtual.js";
import { alCambiarServidores, marcarCambio, servidores } from "/js/trabajo/servidorpy.js";

// El editor de VS Code (Monaco) empieza a cargar ya, en paralelo con el resto (está en /vendor, sin CDN).
const monacoListo = cargarMonaco().then(() => true, (e) => { console.warn("Se usa el editor simple:", e); return false; });
const { user, prog } = await iniciar("trabajo");
const $ = (id) => document.getElementById(id);
const VISTA = "::vista";
const CUENTA = claveCuenta(user);   // cada cuenta, su propio espacio en este navegador (ver trabajo/cuenta.js)
const STORAGE = `cc_trabajo_${CUENTA}`;
const UI_STORAGE = `cc_trabajo_ui_${CUENTA}`;
const CHAT_STORAGE = `cc_trabajo_chat_${CUENTA}`;
const HIST_STORAGE = `cc_trabajo_hist_${CUENTA}`;
const PIP_STORAGE = `cc_trabajo_pip_${CUENTA}`;

// Los elementos del menú lateral no tienen texto visible aquí (es una barra de iconos): se pone como ayuda.
document.querySelectorAll(".trabajo-app .lado .nav-i").forEach((a) => { const t = a.querySelector(".t")?.textContent.trim(); if (t) { a.title = t; a.setAttribute("aria-label", t); } });

// ------------------------------------------------------------------ estado de la interfaz ----
const uiGuardada = (() => { try { return JSON.parse(localStorage.getItem(UI_STORAGE)) || null; } catch { return null; } })();
const ui = {
  abiertos: [], activo: null, expandidas: [], panel: false, altoPanel: 260, anchoExp: 260, explorador: true, asistente: null, autoguardado: true,
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
// Con el guardado automático apagado, el texto escrito en los editores NO pasa al proyecto hasta que se guarda (Ctrl+S).
// Aquí se anotan los archivos con texto sin guardar.
const sucios = new Set();
let ultimoEstado = ["iniciando", ""];
const avisosEstado = new Set();
function pintarEstado(estado, mensaje) {
  ultimoEstado = [estado, mensaje];
  mostrarEstado();
}
function mostrarEstado() {
  const [estado, mensaje] = ultimoEstado;
  const el = $("estadoGuardado");
  if (sucios.size) {
    el.textContent = sucios.size === 1 ? "Sin guardar · Ctrl+S" : `${sucios.size} sin guardar · Ctrl+S`;
    el.className = "estado-item guardando";
    el.title = "Hay cambios sin guardar (el guardado automático está desactivado). Clic o Ctrl+S para guardar.";
    return;
  }
  const [texto, clase, ayuda] = textoEstado[estado] ?? textoEstado.guardado;
  el.textContent = texto;
  el.className = `estado-item ${clase}`.trim();
  el.title = mensaje || ayuda;
  if (estado !== "guardado") avisarProblema(estado, mensaje, ayuda);
  $("expNube").textContent = estado === "guardado" ? "CUENTA" : estado === "guardando" || estado === "iniciando" ? "…" : "LOCAL";
  if (estado === "guardado") avisosEstado.clear();
}
function avisarProblema(estado, mensaje, ayuda) {
  if (["sinconexion", "sesion", "error", "errorLocal"].includes(estado) && !avisosEstado.has(estado)) {
    avisosEstado.add(estado);
    aviso(mensaje || ayuda, { tipo: "error", ms: 9000 });
  }
}

// La copia local vive en IndexedDB: cabe un proyecto grande (localStorage solo admite unos 5 MB).
const copiaLocal = await crearAlmacenamiento(STORAGE, { alCambiarFuera: () => almacen.recargarDesdeLocal() });
const almacen = new Almacen({
  clave: STORAGE, storage: copiaLocal,
  alEstado: pintarEstado,
  alRemoto: () => { proyectoCambio({ origen: "remoto" }); entradas?.alCambiarProyecto({ origen: "remoto" }); },
  resolverConflicto: ({ local, nube }) => dialogo({
    titulo: "Hay dos versiones de tu proyecto",
    mensaje: `En este navegador hay cambios que no se llegaron a sincronizar (${local.archivos} archivos), y tu cuenta tiene otra versión distinta (${nube.archivos} archivos).\n\n¿Cuál quieres conservar? La otra se descartará.`,
    botones: [{ texto: "La de este navegador", valor: "local" }, { texto: "La de mi cuenta", valor: "nube" }],
  }),
});
await almacen.iniciar();
const proyecto = () => almacen.proyecto;
const archivos = new ClienteArchivos();
// Se declara antes de usarse: proyectoCambio puede llamarse durante el arranque, antes de crear Entradas.
let entradas = null;
let vistaGit = false;
let vistaExt = false;
let panelExt = null;
let panelGit = null;
let mapaGit = new Map();   // colores de Git del árbol y las pestañas
let temporizadorDecoracion = 0, decorando = false, decorarOtraVez = false;
let tModelos;
let turnoVista = 0; // cada vista previa nueva invalida a las que aún esperaban sus imágenes

// --------------------------------------------------------------------- terminal y shell ----
// Paquetes de Python que la persona instaló con pip: se recuerdan en este navegador y se reinstalan al ejecutar Python.
const almacenPip = {
  leer: () => { try { const l = JSON.parse(localStorage.getItem(PIP_STORAGE)); return Array.isArray(l) ? l.filter((x) => typeof x === "string").slice(0, 40) : []; } catch { return []; } },
  guardar: (lista) => { try { localStorage.setItem(PIP_STORAGE, JSON.stringify(lista.slice(0, 40))); } catch { /* sin espacio: se pierde solo el recordatorio */ } },
};
const bd = new ClienteBD();
// «Iniciar sesión con GitHub» (git push / pull / clone): una sola sesión para la terminal y el panel de Git.
const sesionGitHub = new SesionGitHub({ cuenta: claveCuenta(user), api });
const motorGit = () => cargarGitReal({ usuario: user, archivos, credencial: sesionGitHub });
const ejecutores = crearEjecutores({ api, almacenPip, archivos, bd });
const paquetes = {
  pip: (o) => ejecutarPip({ cargarPy: cargarPyodide, almacen: almacenPip, ...o }),
  npm: (o) => ejecutarNpm({ ...o, nombreProyecto: "mi-proyecto" }),
};
const shell = new Shell({
  proyecto, usuario: user.nombre || "estudiante", ejecutores, github: { publicar, clonar }, credencialGitHub: sesionGitHub, paquetes, bd,
  gitReal: () => motorGit(),
  leerArchivo: (m) => archivos.bytes(m),
  subirArchivo: (d, o) => archivos.subir(d, o),
  importar: (origen, o) => importarEn(proyecto(), origen, {
    ...o, subir: (d, op) => archivos.subir(d, op),
    espacio: async () => { const u = await archivos.consultarUso(); return { libre: Math.max(0, u.limite - u.uso), maxArchivo: u.max_archivo }; },
  }),
  cambio: (info) => proyectoCambio(info),
  abrir: (ruta) => abrir(ruta, { enfocar: false }),
  abrirVista: (ruta) => abrirVista(ruta),
  abrirUrl: (url) => abrirUrlServidor(url),
});
// ---------------------------------------------------------------- celular: una sección a la vez ----
const MOVIL = matchMedia("(max-width: 760px)");
function seccionMovil(cual) {
  $("ide").dataset.movil = cual;
  for (const b of document.querySelectorAll("#movilTabs [data-movil]")) {
    const on = b.dataset.movil === cual;
    b.classList.toggle("on", on);
    b.setAttribute("aria-selected", String(on));
  }
  if (cual === "terminal") { try { if (!panel.abierto) panel.abrir(); } catch { /* aún creándose */ } }
  window.dispatchEvent(new Event("resize")); // el editor recalcula su tamaño
}
$("ide").dataset.movil = "codigo";
document.getElementById("movilTabs").addEventListener("click", (e) => {
  const b = e.target.closest("[data-movil]");
  if (b) seccionMovil(b.dataset.movil);
});
const panel = new PanelInferior({
  raiz: $("terminalPanel"), shell, proyecto, claveHistorial: HIST_STORAGE,
  alOcupado: (corriendo) => pintarEjecutar(corriendo),
  alCambiar: (abierto) => {
    ui.panel = abierto;
    $("terminalPanel").hidden = !abierto;
    $("sashPanel").hidden = !abierto || panel.maximizado;
    $("contenido").classList.toggle("panel-max", abierto && panel.maximizado);
    $("terminalToggle").setAttribute("aria-expanded", String(abierto));
    $("terminalToggle").classList.toggle("activo", abierto);
    if (MOVIL.matches) { if (abierto) seccionMovil("terminal"); else if ($("ide").dataset.movil === "terminal") seccionMovil("codigo"); }
    guardarUI();
  },
});
document.documentElement.style.setProperty("--alto-panel", "260px");
$("ide").style.setProperty("--alto-panel", `${ui.altoPanel}px`);

// -------------------------------------------------------------------------------- editores ----
const editores = new Map();
const usarMonaco = await monacoListo;

function editorPara(ruta) {
  let ed = editores.get(ruta);
  if (ed) return ed;
  const texto = proyecto().files[ruta] ?? "";
  if (esMarcador(texto)) {
    ed = new VisorArchivo({ ruta, texto, url: (m, o) => archivos.url(m, o) });
    editores.set(ruta, ed);
    $("editores").appendChild(ed.raiz);
    return ed;
  }
  ed = new (usarMonaco ? EditorMonaco : Editor)({
    ruta, texto: proyecto().files[ruta] ?? "",
    alCambiar: (texto) => {
      if (ui.autoguardado) { proyecto().files[ruta] = texto; proyectoCambio({ origen: "editor", ruta }); return; }
      if (!sucios.has(ruta)) { sucios.add(ruta); pintarPestanas(); }
      mostrarEstado();
    },
    alCursor: (pos) => { if (ui.activo === ruta) pintarCursor(pos); },
    alAtajo: (accion) => manejarAtajo(accion),
  });
  editores.set(ruta, ed);
  $("editores").appendChild(ed.raiz);
  return ed;
}

function pintarCursor(pos) {
  const ed = editores.get(ui.activo);
  if (!ed) return;
  if (ed.esImagen) { $("posicionCursor").textContent = ""; $("estIndent").textContent = ""; $("lenguajeArchivo").textContent = ed.lenguaje; return; }
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
    const g = mapaGit.get(r);
    return `<div class="pestana${on ? " on" : ""}${sucios.has(r) ? " sucio" : ""}${g ? ` g-${g}` : ""}" role="tab" aria-selected="${on}" tabindex="${on ? 0 : -1}" data-ruta="${r.replace(/"/g, "&quot;")}" title="${r === VISTA ? "Vista previa de la página" : r}">${icono}<span class="nom">${nombre}</span><button type="button" class="cerrar" tabindex="-1" aria-label="Cerrar ${nombre}">${x}</button></div>`;
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
  if (MOVIL.matches && ruta && $("ide").dataset.movil !== "codigo") seccionMovil("codigo");
  pintarPestanas();
  pintarMigas();
  guardarUI();
}

function abrir(ruta, { enfocar = true } = {}) {
  if (!FS.tieneArchivo(proyecto(), ruta)) return;
  if (!ui.abiertos.includes(ruta)) ui.abiertos.push(ruta);
  activar(ruta, { enfocar });
}

async function cerrarPestana(ruta) {
  const i = ui.abiertos.indexOf(ruta);
  if (i < 0) return;
  if (sucios.has(ruta)) {
    const eleccion = await dialogo({
      titulo: `¿Guardar los cambios de «${FS.nombreBase(ruta)}»?`,
      mensaje: "Si no los guardas, se perderán.",
      botones: [{ texto: "Guardar", valor: "guardar" }, { texto: "No guardar", valor: "descartar", peligro: true }, { texto: "Cancelar", valor: "cancelar", cancelar: true }],
    });
    if (eleccion === "cancelar") return;
    if (eleccion === "guardar") guardarArchivos([ruta]); else { sucios.delete(ruta); mostrarEstado(); }
  }
  const j = ui.abiertos.indexOf(ruta);
  if (j < 0) return;
  ui.abiertos.splice(j, 1);
  const ed = editores.get(ruta);
  if (ed) { ed.destruir(); editores.delete(ruta); }
  if (ui.activo === ruta) activar(ui.abiertos[Math.min(j, ui.abiertos.length - 1)] ?? null);
  else { pintarPestanas(); guardarUI(); }
}

// ------------------------------------------------- vista previa de un servidor de Python ----
let urlServidor = null;   // p. ej. http://127.0.0.1:8000/docs mientras la vista muestra un servidor
let turnoServidor = 0;
function abrirUrlServidor(url) {
  urlServidor = url;
  if (!ui.abiertos.includes(VISTA)) ui.abiertos.push(VISTA);
  activar(VISTA);
}
async function pedirAServidor(url, { method = "GET", headers = [], body = null } = {}) {
  const u = new URL(url);
  const srv = servidores.get(Number(u.port || 80));
  if (!srv) throw new Error(`No hay ningún servidor en ${u.host}`);
  return srv.pedir({ method, url: u.pathname + u.search, headers, body });
}
async function mostrarServidor(url, peticion = {}) {
  const turno = ++turnoServidor;
  $("vistaRuta").hidden = true;
  $("vistaUrlForm").hidden = false;
  $("vistaUrl").value = url;
  let actual = url, r, opciones = { headers: [["accept", "text/html,application/json;q=0.9,*/*;q=0.8"]], ...peticion };
  try {
    for (let saltos = 0; saltos < 6; saltos += 1) {
      r = await pedirAServidor(actual, opciones);
      const destino = r.status >= 300 && r.status < 400 && r.headers.find(([k]) => k.toLowerCase() === "location")?.[1];
      if (!destino) break;
      actual = new URL(destino, actual).href;
      if (r.status !== 307 && r.status !== 308) opciones = { headers: opciones.headers };
    }
  } catch (e) {
    if (turno !== turnoServidor) return;
    const u = new URL(url);
    $("vista").srcdoc = `<p style="font:14px system-ui;padding:24px;color:#555"><b>No se puede acceder a ${u.host}</b><br><br>${e.message.replace(/</g, "&lt;")}.<br>Enciende tu API en la terminal: <code>fastapi dev main.py</code>, <code>uvicorn main:app --reload</code> o <code>flask --app app run</code>.</p>`;
    return;
  }
  if (turno !== turnoServidor) return;
  urlServidor = actual;
  $("vistaUrl").value = actual;
  $("vista").srcdoc = vistaDeRespuesta({ url: actual, ...r });
}
$("vistaUrlForm").addEventListener("submit", (e) => {
  e.preventDefault();
  let v = $("vistaUrl").value.trim();
  if (!v) return;
  if (v.startsWith("/")) v = new URL(v, urlServidor || "http://127.0.0.1:8000").href;
  else if (!/^https?:\/\//i.test(v)) v = "http://" + v;
  urlServidor = v;
  mostrarServidor(v);
});
alCambiarServidores((mapa) => {
  const lista = [...mapa.values()];
  $("estServidor").hidden = !lista.length;
  $("estServidor").textContent = lista.map((x) => `${x.framework || "Python"} :${x.puerto}`).join(" · ");
  if (urlServidor && ui.activo === VISTA) mostrarServidor(urlServidor);
});
$("estServidor").onclick = () => {
  const s = [...servidores.values()][0];
  if (s) abrirUrlServidor(s.url + (s.framework === "FastAPI" ? "/docs" : "/"));
};

// ------------------------------------------- dirección virtual de la vista previa (como Vite) ----
// La vista tiene una dirección http://localhost:5173/… (virtual.js): location, history, localStorage y cookies
// funcionan, y aquí se decide qué mostrar en cada dirección: un archivo del proyecto, una página de tu backend
// (proxy de vite.config.js) o el index.html de una app de una sola página.
let urlVirtual = null;      // dirección que muestra la vista (null = la del archivo abierto)
let remotoVista = null;     // { url, servidor } si la vista muestra una página que mandó tu backend
const ALMACEN_VISTA = `cc_trabajo_vista_${CUENTA}`;
let almacenVista = {};
try { almacenVista = JSON.parse(localStorage.getItem(ALMACEN_VISTA) || "{}") || {}; } catch { almacenVista = {}; }
const sesionVista = {};
function raizVista(py, pagina = paginaVista) { return pagina ? (carpetaDelPaquete(py, FS.carpetaDe(pagina)) ?? "") : ""; }
function almacenDe(raiz) {
  const a = (almacenVista[raiz || "/"] ??= { local: {}, cookies: {} });
  return { local: a.local, cookies: a.cookies, sesion: (sesionVista[raiz || "/"] ??= {}) };
}
let tGuardarVista = 0;
function guardarAlmacen(raiz, tipo, datos) {
  if (tipo === "sesion") { sesionVista[raiz || "/"] = datos || {}; return; }
  const a = (almacenVista[raiz || "/"] ??= { local: {}, cookies: {} });
  if (tipo === "local") a.local = datos || {}; else if (tipo === "cookies") a.cookies = datos || {};
  clearTimeout(tGuardarVista);
  tGuardarVista = setTimeout(() => { try { localStorage.setItem(ALMACEN_VISTA, JSON.stringify(almacenVista)); } catch { /* lleno */ } }, 300);
}
function mostrarDireccion(url) {
  try { const u = new URL(url); $("vistaRuta").textContent = `Vista previa · ${u.pathname}${u.search}${u.hash}`; $("vistaRuta").title = url; } catch { /* nada */ }
}
/** Lo que pide la página (un script, una hoja de estilos, una imagen) a una dirección virtual. */
async function obtenerVirtual(py, raiz, proxy, url) {
  const d = resolverDestino(py, raiz, url, proxy);
  if (d.tipo === "archivo" && !d.spa) {
    const t = py.files[d.ruta];
    return typeof t === "string" && !esMarcador(t) ? { tipo: "text/plain", bytes: new TextEncoder().encode(t) } : null;
  }
  if (d.tipo === "remoto") {
    try {
      const r = await pedirAServidor(d.url, { headers: [["accept", "*/*"]] });
      if (r.status >= 400) return null;
      return { tipo: r.headers.find(([k]) => k.toLowerCase() === "content-type")?.[1] || "", bytes: r.body };
    } catch { return null; }
  }
  return null;
}
/** HTML de una página que manda tu backend (con sus scripts y estilos traídos y la dirección virtual). */
async function htmlRemoto(py, raiz, proxy, url, servidorUrl, { hijo = false } = {}) {
  let actual = servidorUrl, r;
  for (let saltos = 0; saltos < 6; saltos += 1) {
    r = await pedirAServidor(actual, { headers: [["accept", "text/html,application/json;q=0.9,*/*;q=0.8"]] });
    const destino = r.status >= 300 && r.status < 400 && r.headers.find(([k]) => k.toLowerCase() === "location")?.[1];
    if (!destino) break;
    actual = new URL(destino, actual).href;
  }
  const tipo = (r.headers.find(([k]) => k.toLowerCase() === "content-type")?.[1] || "").toLowerCase();
  if (!tipo.includes("html")) return vistaDeRespuesta({ url: actual, status: r.status, headers: r.headers, body: r.body });
  const html = await incrustarRecursos(new TextDecoder().decode(r.body), url, (u) => obtenerVirtual(py, raiz, proxy, u));
  return paginaRemotaConPuente(html, { url, almacen: almacenDe(raiz), proxy, hijo });
}
/** HTML para cualquier dirección virtual (la vista entera o un <iframe> de la página). */
async function htmlDeDireccion(url, { hijo = false } = {}) {
  const py = proyecto();
  const raiz = raizVista(py);
  const proxy = proxyDeVite(py, raiz);
  const d = resolverDestino(py, raiz, url, proxy);
  if (d.tipo === "remoto") return htmlRemoto(py, raiz, proxy, url, d.url, { hijo });
  if (d.tipo === "archivo") {
    const mapa = Object.values(py.files).some(esMarcador) ? await archivos.enlaces(py) : new Map();
    let modulos = null;
    if (usaModulos(py, d.ruta)) modulos = await modulosDePagina(py, d.ruta, { transpilar: transpilarModulo, enlaces: mapa });
    return construirVistaPrevia(py, d.ruta, { imagenes: mapa, modulos, proxy, virtual: { url, almacen: almacenDe(raiz), hijo } });
  }
  if (d.tipo === "externo") return `<p style="font:14px system-ui;padding:20px">Página externa: <a href="${d.url}" target="_blank" rel="noopener">${d.url}</a></p>`;
  return `<pre style="font:13px ui-monospace,monospace;padding:20px;color:#b91c1c">Cannot GET ${new URL(url).pathname.replace(/</g, "&lt;")}\n\nNo hay ningún archivo en esa dirección en tu proyecto${proxy.length ? " ni una ruta del proxy de vite.config.js" : ""}.</pre>`;
}
/** La página navegó (location.href = …, un enlace, history): se muestra lo que hay en esa dirección. */
async function navegarVista(url) {
  const py = proyecto();
  const raiz = raizVista(py);
  const proxy = proxyDeVite(py, raiz);
  const d = resolverDestino(py, raiz, url, proxy);
  if (d.tipo === "externo") { window.open(d.url, "_blank", "noopener"); return; }
  urlVirtual = url;
  if (d.tipo === "archivo") { remotoVista = null; paginaVista = d.ruta; renderVista(); return; }
  remotoVista = d;
  const turno = ++turnoVista;
  mostrarDireccion(url);
  try {
    const html = await htmlDeDireccion(url);
    if (turno === turnoVista) $("vista").srcdoc = html;
  } catch (e) {
    if (turno === turnoVista) $("vista").srcdoc = `<p style="font:14px system-ui;padding:24px;color:#555"><b>No se pudo abrir ${new URL(url).pathname}</b><br><br>${String(e.message).replace(/</g, "&lt;")}.<br>¿Está encendido tu backend en otra terminal? (por ejemplo: cd backend && fastapi dev app.py)</p>`;
  }
}

function renderVista() {
  if (urlServidor) { mostrarServidor(urlServidor); return; }
  if (remotoVista && urlVirtual) { navegarVista(urlVirtual); return; }
  $("vistaRuta").hidden = false;
  $("vistaUrlForm").hidden = true;
  guardarArchivos();
  const py = proyecto();
  paginaVista = paginaPrincipal(py, paginaVista);
  if (!paginaVista) {
    $("vista").srcdoc = '<p style="font:14px system-ui;padding:24px;color:#555">Crea un archivo <b>.html</b> (por ejemplo index.html) para ver aquí tu página.</p>';
    $("vistaRuta").textContent = "Vista previa";
    return;
  }
  panel.limpiarConsola();
  $("vistaRuta").textContent = `Vista previa · ${paginaVista}`;
  const turno = ++turnoVista;
  const pagina = paginaVista;
  const hayImagenes = Object.values(py.files).some(esMarcador);
  (async () => {
    const mapa = hayImagenes ? await archivos.enlaces(py) : new Map();
    let modulos = null;
    if (usaModulos(py, pagina)) {
      if (turno === turnoVista) $("vista").srcdoc = '<p style="font:14px system-ui;padding:24px;color:#555">Preparando los módulos (JSX, TypeScript y paquetes)…</p>';
      try {
        modulos = await modulosDePagina(py, pagina, { transpilar: transpilarModulo, enlaces: mapa });
        for (const e of modulos.errores) panel.escribirConsola("error", e);
      } catch (error) {
        panel.escribirConsola("error", `No se pudieron preparar los módulos: ${error.message}`);
      }
    }
    if (turno !== turnoVista) return; // llegó otra vista previa más nueva
    pintarVista(py, pagina, mapa, modulos);
  })();
  pintarMigas();
}

function pintarVista(py, pagina, mapa, modulos = null) {
  try {
    const raiz = raizVista(py, pagina);
    // La dirección virtual es la de la última navegación si sigue apuntando a esta página; si no, la del archivo.
    let url = urlVirtual;
    if (!url || resolverDestino(py, raiz, url, proxyDeVite(py, raiz)).ruta !== pagina) url = urlDeArchivo(raiz, pagina);
    urlVirtual = url;
    mostrarDireccion(url);
    $("vista").srcdoc = construirVistaPrevia(py, pagina, { imagenes: mapa, modulos, proxy: proxyDeVite(py, raiz), virtual: { url, almacen: almacenDe(raiz) } });
  } catch (error) {
    // Nunca una página en blanco sin explicación.
    const msg = String(error?.message || error).replace(/&/g, "&amp;").replace(/</g, "&lt;");
    $("vista").srcdoc = `<p style="font:14px system-ui;padding:24px;color:#b91c1c">No se pudo construir la vista previa: ${msg}</p>`;
    panel.escribirConsola("error", `No se pudo construir la vista previa: ${error?.message || error}`);
  }
}

function abrirVista(preferida = null) {
  urlServidor = null;
  const py = proyecto();
  const pagina = paginaPrincipal(py, preferida);
  if (!pagina) { aviso("Crea un archivo .html (por ejemplo index.html) para ver la vista previa.", { tipo: "error" }); return; }
  paginaVista = pagina;
  remotoVista = null;
  urlVirtual = urlDeArchivo(raizVista(py, pagina), pagina);
  if (!ui.abiertos.includes(VISTA)) ui.abiertos.push(VISTA);
  activar(VISTA);
}

window.addEventListener("message", (e) => {
  const m = e.data;
  if (!m || e.source !== $("vista").contentWindow) return;
  if (m.cc === "consola") panel.escribirConsola(m.nivel, String(m.texto).slice(0, 4000));
  else if (m.cc === "vnav") navegarVista(String(m.url));
  else if (m.cc === "vurl") { urlVirtual = String(m.url); mostrarDireccion(urlVirtual); }
  else if (m.cc === "ls") guardarAlmacen(raizVista(proyecto()), String(m.tipo), m.datos);
  else if (m.cc === "vpagina") {
    // <iframe src="/legacy/…"> o de otra página del proyecto, dentro de la vista
    htmlDeDireccion(String(m.url), { hijo: true })
      .then((html) => e.source.postMessage({ cc: "vpagina-r", id: m.id, html }, "*"))
      .catch((error) => e.source.postMessage({ cc: "vpagina-r", id: m.id, error: `No se pudo cargar ${m.url}: ${error.message}. ¿Está encendido tu backend?` }, "*"));
  }
  else if (m.cc === "google-token") {
    // «Continuar con Google» de tu app en la vista previa: entra con tu cuenta de CódigoCamp (ver red_py.py).
    api("/api/trabajo/google-token", { aud: String(m.aud || "") })
      .then((r) => { e.source.postMessage({ cc: "google-token-r", id: m.id, credential: r.credential }, "*"); panel.escribirConsola("info", `Iniciar con Google (Trabajo): entraste como ${r.email}. En tu PC se usa Google de verdad.`); })
      .catch((error) => e.source.postMessage({ cc: "google-token-r", id: m.id, error: error.message }, "*"));
  }
  else if (m.cc === "http" && (urlServidor || /^https?:/i.test(String(m.url)))) {
    // fetch() / XMLHttpRequest de la página hacia tu API: desde /docs del servidor, o desde tu frontend
    // (npm run dev con el proxy de vite.config.js, o fetch("http://localhost:8000/…")).
    const responder = (datos, transferir = []) => { try { e.source.postMessage({ cc: "http-r", id: m.id, ...datos }, "*", transferir); } catch { /* la vista cambió */ } };
    const destino = new URL(String(m.url), urlServidor ?? undefined);
    pedirAServidor(destino.href, { method: m.method, headers: m.headers, body: m.body?.byteLength ? new Uint8Array(m.body) : null })
      .then((r) => { const b = r.body.slice().buffer; responder({ status: r.status, headers: r.headers, body: b }, [b]); })
      .catch((error) => {
        if (!urlServidor) panel.escribirConsola("error", `${(m.method || "GET").toUpperCase()} ${destino.href} → ${error.message}. Enciende tu backend en otra terminal (por ejemplo: cd backend && fastapi dev app.py).`);
        responder({ error: `Failed to fetch (${error.message})` });
      });
  } else if (m.cc === "ir" && (urlServidor || /^https?:/i.test(String(m.url)))) mostrarServidor(new URL(String(m.url), urlServidor ?? undefined).href);
  else if (m.cc === "form" && (urlServidor || /^https?:/i.test(String(m.url)))) mostrarServidor(new URL(String(m.url), urlServidor ?? undefined).href, { method: m.method, headers: m.headers, body: m.body?.byteLength ? new Uint8Array(m.body) : null });
  else if (m.cc === "nav" && urlServidor) { if (/^https?:/i.test(m.href)) window.open(m.href, "_blank", "noopener"); else mostrarServidor(new URL(String(m.href), urlServidor).href); }
  else if (m.cc === "nav") {
    const destino = resolverEnlace(proyecto(), paginaVista || "", m.href);
    if (destino) { paginaVista = destino; renderVista(); } else panel.escribirConsola("warn", `El enlace «${m.href}» no apunta a ninguna página de tu proyecto.`);
  }
});

function ejecutarActual() {
  guardarArchivos(); // ejecutar siempre usa lo último que escribiste
  const ruta = ui.activo;
  if (ruta === VISTA) { renderVista(); return; }
  if (!ruta) { aviso("Abre un archivo para ejecutarlo.", { tipo: "info" }); return; }
  if (esMarcador(proyecto().files[ruta])) { aviso("Es un archivo (imagen, video, PDF…): no se ejecuta. Úsalo desde tu HTML o CSS y abre la vista previa.", { tipo: "info" }); return; }
  if (/\.(html?|css)$/i.test(ruta)) { abrirVista(/\.html?$/i.test(ruta) ? ruta : null); return; }
  // Un .js que usa una página del proyecto se «ejecuta» abriendo esa página (corre en el navegador, no en Node).
  const pagina = /\.m?js$/i.test(ruta) ? paginaQueUsa(proyecto(), ruta) : null;
  if (pagina) { abrirVista(pagina); return; }
  const comando = comandoParaArchivo(ruta, panel.activa?.sesion.cwd ?? "");
  if (!comando) { aviso(`No sé ejecutar archivos .${FS.extension(ruta) || "sin extensión"}. Los de texto solo se editan.`); return; }
  panel.correr(comando);
}

// ------------------------------------------------------------------- cambios del proyecto ----
function renombrarRutas(de, a) {
  const cambiar = (r) => (r === de ? a : FS.dentroDe(r, de) && r !== VISTA ? a + r.slice(de.length) : r);
  ui.abiertos = ui.abiertos.map(cambiar);
  if (ui.activo) ui.activo = cambiar(ui.activo);
  for (const r of [...sucios]) { const n = cambiar(r); if (n !== r) { sucios.delete(r); sucios.add(n); } }
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
  for (const [ruta, ed] of [...editores]) if (!FS.tieneArchivo(py, ruta)) { ed.destruir(); editores.delete(ruta); sucios.delete(ruta); }
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
  let cambioActivo = reconciliarPestanas();
  // Si un archivo pasó de imagen a texto (o al revés), su editor se vuelve a crear del tipo correcto.
  for (const [ruta, ed] of [...editores]) {
    if (Boolean(ed.esImagen) !== esMarcador(proyecto().files[ruta])) { ed.destruir(); editores.delete(ruta); sucios.delete(ruta); if (ruta === ui.activo) cambioActivo = true; }
  }
  // El texto sin guardar de un editor nunca se pisa con lo que haya en el proyecto.
  if (origen !== "editor") for (const [ruta, ed] of editores) if (!sucios.has(ruta)) ed.establecer(proyecto().files[ruta] ?? "");
  if (cambioActivo || info.movido || origen === "remoto") activar(ui.activo, { enfocar: false });
  else if (origen !== "editor") { explorador.render(); pintarPestanas(); pintarMigas(); }
  if (origen !== "editor") pintarGit();
  programarDecoracionGit(origen === "editor" ? 1500 : 400);
  if (origen !== "ui") marcarCambio();
  programarModelos();
  if (vistaGit && origen !== "editor") panelGit?.render();
  if (vistaExt && origen !== "editor") panelExt?.render();
  if (info.origen === "importar" && info.rutas?.length === 1 && FS.tieneArchivo(proyecto(), info.rutas[0])) abrir(info.rutas[0], { enfocar: false });
  entradas?.alCambiarProyecto(info);
  guardarUI();
}

/** Pasa el texto de los editores (con cambios sin guardar) al proyecto. */
function guardarArchivos(rutas = [...sucios]) {
  let hubo = false;
  for (const ruta of rutas) {
    const ed = editores.get(ruta);
    if (ed && FS.tieneArchivo(proyecto(), ruta)) { proyecto().files[ruta] = ed.leer(); hubo = true; }
    sucios.delete(ruta);
  }
  if (hubo) proyectoCambio({ origen: "editor" });
  pintarPestanas();
  mostrarEstado();
  return hubo;
}

async function guardarAhora() {
  guardarArchivos();
  const ok = await almacen.guardarAhora();
  if (ok) aviso("Proyecto guardado en tu cuenta.", { ms: 2200 });
}

function pintarAutoguardado() {
  const b = $("autoGuardado");
  b.textContent = `Autoguardado: ${ui.autoguardado ? "Sí" : "No"}`;
  b.setAttribute("aria-pressed", String(ui.autoguardado));
  b.classList.toggle("apagado", !ui.autoguardado);
}

function alternarAutoguardado() {
  ui.autoguardado = !ui.autoguardado;
  if (ui.autoguardado) {
    void guardarAhora(); // al volver a activarlo se guarda lo pendiente
    aviso("Autoguardado activado: tus cambios se guardan solos.", { ms: 3500 });
  } else {
    aviso("Autoguardado desactivado. Guarda con Ctrl+S; al ejecutar o abrir la vista previa también se guarda el archivo.", { ms: 6500 });
  }
  pintarAutoguardado();
  guardarUI();
}

// Aviso del navegador al salir con cambios sin guardar
addEventListener("beforeunload", (e) => { if (sucios.size) { e.preventDefault(); e.returnValue = ""; } });

// ------------------------------------------------------------------------------ explorador ----
const explorador = new Explorador({
  raiz: $("arbol"), proyecto, expandidas,
  alAbrir: (ruta) => abrir(ruta),
  alCambiar: proyectoCambio,
  alBorrar: ofrecerDeshacer,
  alAbrirTerminalEn: (carpeta) => panel.correr(`cd ${FS.rutaAbsoluta(carpeta)}`),
  alSoltarArchivos: (o) => entradas.soltados(o),
  alSubirEn: (carpeta) => entradas.subirArchivos(carpeta),
  alDescargar: (ruta) => entradas.descargarArchivo(ruta),
});
entradas = new Entradas({
  proyecto, archivos, usuarioId: CUENTA, botonCarpeta: $("estCarpeta"),
  cambio: (info) => proyectoCambio(info),
  antesDeLeer: () => guardarArchivos(),
});
$("masAcciones").onclick = (e) => { const r = e.currentTarget.getBoundingClientRect(); entradas.menu(r.left, r.bottom + 4); };
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
function pintarEjecutar(corriendo = panel.hayProgramaCorriendo) {
  const b = $("ejecutar");
  b.classList.toggle("detener", corriendo);
  b.innerHTML = corriendo
    ? '<svg viewBox="0 0 16 16" aria-hidden="true" width="12" height="12"><rect x="3" y="3" width="10" height="10" rx="1.5" fill="currentColor"/></svg> Detener'
    : '<svg viewBox="0 0 16 16" aria-hidden="true" width="12" height="12"><path d="M4 2.5v11L13.5 8z" fill="currentColor"/></svg> Ejecutar';
  b.title = corriendo ? "Detener el programa que se está ejecutando" : "Ejecutar el archivo abierto (Ctrl+Enter)";
  b.setAttribute("aria-label", corriendo ? "Detener el programa" : "Ejecutar archivo");
}
$("ejecutar").onclick = () => { if (panel.hayProgramaCorriendo) panel.detener(); else ejecutarActual(); };
$("autoGuardado").onclick = alternarAutoguardado;
$("estadoGuardado").onclick = guardarAhora;
$("vistaPrevia").onclick = () => abrirVista(ui.activo && /\.html?$/i.test(ui.activo) ? ui.activo : paginaVista);
$("vistaRecargar").onclick = renderVista;
$("guardar").onclick = guardarAhora;
$("estRama").onclick = () => panel.correr("git status");
$("terminalToggle").onclick = () => panel.alternar();
$("bienvenida").addEventListener("click", (e) => {
  const a = e.target.closest("[data-accion]")?.dataset.accion;
  if (a === "nuevo-archivo") explorador.nuevo("archivo", "");
  else if (a === "terminal") panel.abrir();
  else if (a === "guardar") guardarAhora();
  else if (a === "importar-zip") entradas.importarZip();
  else if (a === "carpeta") entradas.vincularCarpeta();
  else if (a === "subir") entradas.subirArchivos("");
});

function alternarAsistente(mostrar = $("ide").classList.contains("sin-asistente")) {
  if (MOVIL.matches) { seccionMovil($("ide").dataset.movil === "asistente" ? "codigo" : "asistente"); return; }
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
  const k = e.key.toLowerCase();
  if (e.key === "F1" || (ctrl && e.shiftKey && k === "p")) { e.preventDefault(); manejarAtajo("paleta"); return; }
  if (ctrl && !e.shiftKey && k === "p") { e.preventDefault(); manejarAtajo("abrir-rapido"); return; }
  if (ctrl && e.shiftKey && k === "f") { e.preventDefault(); manejarAtajo("buscar-archivos"); return; }
  if (ctrl && e.shiftKey && k === "g") { e.preventDefault(); manejarAtajo("git"); return; }
  if (ctrl && e.shiftKey && k === "x") { e.preventDefault(); alternarExt(); return; }
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
arrastre($("sashExp"), (e) => fijarAnchoExp(e.clientX - $("explorador").getBoundingClientRect().left), guardarUI);
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
  if (rol === "tutor") formato(d, texto); else d.textContent = texto;
  $("chat").append(d);
  $("chat").scrollTop = $("chat").scrollHeight;
  return d;
}

function pintarChat() {
  $("chat").replaceChildren();
  const curso = prog.curso_actual?.nombre;
  $("cursoAsistente").textContent = curso ? `Tutor de ${curso}` : "Tutor de CódigoCamp";
  burbuja("tutor", `¡Hola${user.nombre ? `, ${user.nombre.split(" ")[0]}` : ""}! Pregúntame sobre tu código. Activa **Editar con IA** y puedo proponer cambios en tus archivos (los revisas y aceptas tú).`);
  historial.forEach((m) => burbuja(m.rol, m.texto));
}

// Copiloto: permiso guardado por cuenta
const CLAVE_COPILOTO = `cc_copiloto_${user.id}`;
try { $("copiloto").checked = localStorage.getItem(CLAVE_COPILOTO) === "1"; } catch { /* sin almacenamiento */ }
$("copiloto").onchange = () => { try { localStorage.setItem(CLAVE_COPILOTO, $("copiloto").checked ? "1" : "0"); } catch { /* nada */ } };
document.head.insertAdjacentHTML("beforeend", `<style>${CSS_ADJUNTOS}</style>`);
const adjIa = crearAdjuntador({ boton: $("clipIa"), entrada: $("archivosIa"), bandeja: $("bandejaIa"), zona: $("asistente"), destino: "ia" });
$("limpiarChat").onclick = () => { historial = []; try { localStorage.removeItem(CHAT_STORAGE); } catch { /* nada */ } pintarChat(); };
$("pregunta").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("preguntar").requestSubmit(); } };

function seleccionActual() {
  try { const ed = editores.get(ui.activo)?.editor; const sel = ed?.getSelection?.(); return sel && !sel.isEmpty() ? ed.getModel().getValueInRange(sel) : ""; } catch { return ""; }
}
function salidaTerminal() {
  try { return (document.querySelector("#terminalPanel .term-contenedor")?.innerText || "").slice(-6000); } catch { return ""; }
}

/** Tarjeta con los cambios que propone la IA: ver diferencias, aceptar o rechazar cada archivo, o todos. */
function tarjetaCambios(cambios, resumen, errores) {
  const caja = document.createElement("div");
  caja.className = "msg tutor cambios-ia";
  const estado = new Map(cambios.map((c) => [c.ruta, "pendiente"]));
  const deshacer = [];
  const pintar = () => {
    const pend = [...estado.values()].filter((x) => x === "pendiente").length;
    caja.innerHTML = `<b>✨ La IA propone ${cambios.length} cambio${cambios.length === 1 ? "" : "s"}</b>${resumen ? `<p>${resumen.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]))}</p>` : ""}
      <ul>${cambios.map((c, i) => { const e = estado.get(c.ruta); const tipo = c.accion === "borrar" ? "borrar" : c.nuevo ? "nuevo" : "modificar";
        return `<li class="cambio-${e}"><span class="cambio-tipo t-${tipo}">${tipo === "borrar" ? "D" : tipo === "nuevo" ? "A" : "M"}</span><code title="${c.ruta.replace(/"/g, "&quot;")}">${c.ruta.replace(/</g, "&lt;")}</code>
        ${e === "pendiente" ? `<button type="button" data-i="${i}" data-a="ver" title="Ver diferencias">Ver</button><button type="button" data-i="${i}" data-a="si" class="ok" title="Aceptar">✓</button><button type="button" data-i="${i}" data-a="no" title="Rechazar">✕</button>` : `<em>${e === "aceptado" ? "aplicado" : "rechazado"}</em>`}</li>`; }).join("")}</ul>
      ${errores.length ? `<small class="cambio-errores">${errores.map((x) => x.replace(/</g, "&lt;")).join("<br>")}</small>` : ""}
      <div class="cambios-acc">${pend ? `<button type="button" data-a="todo" class="btn pri sm">Aceptar todo (${pend})</button><button type="button" data-a="nada" class="btn sm">Rechazar todo</button>` : ""}${deshacer.length ? '<button type="button" data-a="deshacer" class="btn sm">↶ Deshacer cambios aplicados</button>' : ""}</div>`;
  };
  const aceptar = async (c) => {
    if (c.accion === "borrar" && !confirm(`¿Borrar ${c.ruta}? La IA propone eliminarlo.`)) return;
    const r = aplicarCambio(proyecto(), c);
    if (!r.ok) { avisoSimple(`${c.ruta}: ${r.error}`, true); return; }
    deshacer.push(r.deshacer);
    estado.set(c.ruta, "aceptado");
    proyectoCambio({ origen: "ia" });
    if (c.accion !== "borrar") abrir(c.ruta);
  };
  caja.onclick = async (e) => {
    const b = e.target.closest("button[data-a]");
    if (!b) return;
    const c = cambios[Number(b.dataset.i)];
    if (b.dataset.a === "ver") verDiff(c.ruta, c.antes ?? "", c.accion === "borrar" ? "" : c.contenido);
    else if (b.dataset.a === "si") await aceptar(c);
    else if (b.dataset.a === "no") estado.set(c.ruta, "rechazado");
    else if (b.dataset.a === "todo") { for (const x of cambios) if (estado.get(x.ruta) === "pendiente") await aceptar(x); }
    else if (b.dataset.a === "nada") { for (const x of cambios) if (estado.get(x.ruta) === "pendiente") estado.set(x.ruta, "rechazado"); }
    else if (b.dataset.a === "deshacer") { while (deshacer.length) deshacer.pop()(); for (const [k, v] of estado) if (v === "aceptado") estado.set(k, "pendiente"); proyectoCambio({ origen: "ia" }); avisoSimple("Cambios deshechos"); }
    pintar();
  };
  pintar();
  return caja;
}

$("preguntar").onsubmit = async (event) => {
  event.preventDefault();
  const pregunta = $("pregunta").value.trim();
  if ((!pregunta && !adjIa.hay()) || $("enviar").disabled) return;
  $("enviar").disabled = true;
  let adjuntos = [];
  try { adjuntos = await adjIa.listos(); } catch (x) { avisoSimple(x.message, true); $("enviar").disabled = false; return; }
  const nombres = adjIa.adjuntos().map((a) => a.nombre);
  adjIa.limpiar();
  $("pregunta").value = "";
  burbuja("yo", pregunta + (nombres.length ? `\n📎 ${nombres.join(", ")}` : ""));
  const copiloto = $("copiloto").checked;
  const espera = burbuja("tutor", copiloto ? "Revisando tu proyecto…" : "Pensando…");
  const archivo = ui.activo && ui.activo !== VISTA && FS.tieneArchivo(proyecto(), ui.activo) ? ui.activo : null;
  let probs = [];
  try { probs = usarMonaco ? problemas().lista.slice(0, 30).map((x) => `${x.ruta}:${x.linea} ${x.mensaje}`) : []; } catch { /* sin editor */ }
  const contexto = contextoProyecto(proyecto(), { abierto: archivo, abiertos: [...(ui.abiertos || [])], seleccion: seleccionActual(), problemas: probs, terminal: salidaTerminal(), copiloto });
  try {
    const r = await api("/api/tutor/", { mensaje: pregunta, adjuntos, historial: historial.slice(-12), contexto });
    const { texto, cambios, resumen, error } = extraerCambios(r.respuesta);
    formato(espera, texto || (cambios ? "Aquí tienes los cambios:" : r.respuesta));
    if (error) burbuja("tutor", error).classList.add("error");
    if (cambios) {
      const { validos, errores } = validarCambios(cambios, proyecto());
      if (validos.length || errores.length) $("chat").append(tarjetaCambios(validos, resumen, errores));
    }
    historial.push({ rol: "yo", texto: pregunta || "(archivos)" }, { rol: "tutor", texto: (texto || "") + (cambios ? `\n(Propuse cambios en: ${cambios.map((c) => c.ruta).join(", ")})` : "") });
    historial = historial.slice(-16);
    try { localStorage.setItem(CHAT_STORAGE, JSON.stringify(historial)); }
    catch { avisoSimple("El tutor respondió, pero no se pudo guardar el historial en este navegador.", true); }
  } catch (error) {
    espera.textContent = error.message;
    espera.classList.add("error");
    $("pregunta").value = pregunta;
  }
  $("enviar").disabled = false;
  $("chat").scrollTop = $("chat").scrollHeight;
  $("pregunta").focus();
};

// ------------------------------------------------ como VS Code: paleta, búsqueda, Git, problemas ----
function programarModelos() { clearTimeout(tModelos); tModelos = setTimeout(() => sincronizarModelos(proyecto(), (t) => !esMarcador(t)), 400); }

function abrirEnLinea(ruta, linea, col = 1, largo = 0) {
  abrir(ruta);
  const ed = editores.get(ruta);
  if (!ed) return;
  if (largo && ed.seleccionar) ed.seleccionar(linea, col, col + largo);
  else ed.irALinea?.(linea, col);
}

const COMANDOS_PALETA = () => [
  { etiqueta: "Archivo: nuevo archivo", accion: () => explorador.nuevo("archivo") },
  { etiqueta: "Archivo: nueva carpeta", accion: () => explorador.nuevo("carpeta") },
  { etiqueta: "Archivo: guardar", atajo: "Ctrl+S", accion: () => guardarAhora() },
  { etiqueta: "Archivo: cerrar el editor", accion: () => ui.activo && cerrarPestana(ui.activo) },
  { etiqueta: "Archivo: subir archivos…", accion: () => entradas.subirArchivos("") },
  { etiqueta: "Archivo: importar .zip…", accion: () => entradas.importarZip() },
  { etiqueta: "Archivo: descargar el proyecto (.zip)", accion: () => entradas.descargarZip() },
  { etiqueta: "Archivo: abrir carpeta del computador…", accion: () => entradas.vincularCarpeta() },
  { etiqueta: "Ir a archivo…", atajo: "Ctrl+P", accion: () => manejarAtajo("abrir-rapido") },
  { etiqueta: "Ir a línea…", atajo: "Ctrl+G", accion: () => abrirPaleta({ inicial: ":", irALinea: (n) => editores.get(ui.activo)?.irALinea?.(n) }) },
  { etiqueta: "Buscar en archivos", atajo: "Ctrl+Shift+F", accion: () => manejarAtajo("buscar-archivos") },
  { etiqueta: "Ver: control de código fuente (Git)", atajo: "Ctrl+Shift+G", accion: () => alternarGit(true) },
  { etiqueta: "Ver: extensiones (librerías y frameworks)", atajo: "Ctrl+Shift+X", accion: () => alternarExt(true) },
  { etiqueta: "Ver: explorador de archivos", atajo: "Ctrl+B", accion: () => { alternarGit(false); alternarExplorador(true); } },
  { etiqueta: "Ver: terminal", atajo: "Ctrl+`", accion: () => panel.alternar() },
  { etiqueta: "Ver: problemas", accion: () => verProblemas() },
  { etiqueta: "Ver: asistente de IA", accion: () => alternarAsistente() },
  { etiqueta: "Ver: vista previa", accion: () => abrirVista(paginaVista) },
  { etiqueta: "Ejecutar el archivo actual", atajo: "Ctrl+Enter", accion: () => ejecutarActual() },
  { etiqueta: "Terminal: nueva app React (npm create vite)", accion: () => { panel.abrir(); panel.correr("npm create vite@latest mi-app -- --template react"); } },
  { etiqueta: "Git: inicializar repositorio", accion: () => panel.correr("git init") },
  { etiqueta: "Git: estado", accion: () => panel.correr("git status") },
  { etiqueta: "Git: publicar (push)", accion: () => panel.correr("git push") },
  { etiqueta: `Preferencias: autoguardado (${ui.autoguardado ? "activado" : "desactivado"})`, accion: () => alternarAutoguardado() },
  ...(usarMonaco ? [{ etiqueta: "Editor: formatear documento", atajo: "Shift+Alt+F", accion: () => editores.get(ui.activo)?.editor?.getAction("editor.action.formatDocument")?.run() },
    { etiqueta: "Editor: todos los comandos del editor…", atajo: "F1 dentro del editor", accion: () => { const ed = editores.get(ui.activo); ed?.enfocar(); ed?.editor?.trigger("paleta", "editor.action.quickCommand", null); } }] : []),
];

function manejarAtajo(accion) {
  if (accion === "guardar") guardarAhora();
  else if (accion === "ejecutar") ejecutarActual();
  else if (accion === "terminal") panel.alternar();
  else if (accion === "explorador") alternarExplorador();
  else if (accion === "git") alternarGit();
  else if (accion === "abrir-rapido" || accion === "paleta") {
    abrirPaleta({
      inicial: accion === "paleta" ? ">" : "",
      archivos: () => Object.keys(proyecto().files).sort().map((r) => ({ etiqueta: r, icono: iconoArchivo(r), accion: () => abrir(r) })),
      comandos: COMANDOS_PALETA,
      irALinea: (n) => editores.get(ui.activo)?.irALinea?.(n),
    });
  } else if (accion === "buscar-archivos") {
    guardarArchivos();
    const ed = editores.get(ui.activo);
    const sel = ed?.editor ? ed.editor.getModel().getValueInRange(ed.editor.getSelection()) : "";
    abrirBuscador({ proyecto, abrirEn: abrirEnLinea, alCambiar: proyectoCambio, aviso, inicial: sel && !sel.includes("\n") ? sel : "" });
  }
}

function pintarProblemas() {
  const b = $("estProblemas");
  if (!usarMonaco) { b.hidden = true; return; }
  const p = problemas();
  b.hidden = false;
  b.innerHTML = `<span class="prob-e">⊗ ${p.errores}</span> <span class="prob-a">⚠ ${p.advertencias}</span>`;
  b.title = p.errores || p.advertencias ? "Problemas que encontró el editor (clic para verlos)" : "Sin problemas";
}

function verProblemas() {
  const p = problemas();
  abrirPaleta({
    titulo: p.lista.length ? "Problemas: elige uno para ir a esa línea" : "No hay problemas en los archivos abiertos o de código",
    lista: p.lista.map((x) => ({ etiqueta: `${x.grave ? "⊗" : "⚠"} ${x.mensaje}`, detalle: `${x.ruta}:${x.linea}`, accion: () => abrirEnLinea(x.ruta, x.linea) })),
  });
}

function verDiff(ruta, antes, despues) {
  if (!usarMonaco) { panel.correr(`git diff ${ruta}`); return; }
  const d = document.createElement("dialog");
  d.className = "ide-dialogo dialogo-diff";
  d.innerHTML = `<form method="dialog"><h3>${ruta.replace(/&/g, "&amp;").replace(/</g, "&lt;")} <small>último commit ↔ ahora</small></h3><div class="diff-caja"></div><div class="ide-dialogo-botones"><button class="ide-boton" value="abrir">Abrir archivo</button><button class="ide-boton primario" value="cerrar">Cerrar</button></div></form>`;
  document.body.appendChild(d);
  d.showModal();
  const cerrar = crearDiff(d.querySelector(".diff-caja"), ruta, antes, despues);
  d.addEventListener("close", () => { cerrar(); d.remove(); if (d.returnValue === "abrir" && FS.tieneArchivo(proyecto(), ruta)) abrir(ruta); });
}

// Colores de Git en el árbol y las pestañas (como VS Code): amarillo M = modificado, verde U = nuevo, rojo ! = conflicto.
function programarDecoracionGit(ms = 400) {
  clearTimeout(temporizadorDecoracion);
  temporizadorDecoracion = setTimeout(decorarGit, ms);
}
/** Lo instalado con pip: en el Python global y en los entornos virtuales del proyecto. */
function paquetesInstalados() {
  const py = proyecto();
  return [...almacenPip.leer(), ...listarVenvs(py).flatMap((d) => almacenDeVenv(py, d).leer())];
}
function actualizarFaltantes() {
  let n = 0;
  try { n = faltantesPython(proyecto(), paquetesInstalados()).length; } catch { /* nada */ }
  $("numExt").hidden = !n;
  $("numExt").textContent = String(n);
  $("verExtensiones").title = n ? `Extensiones: a tu proyecto le faltan ${n} paquete${n === 1 ? "" : "s"} de Python (Ctrl+Shift+X)` : "Extensiones: librerías y frameworks (Ctrl+Shift+X)";
  return n;
}
async function decorarGit() {
  actualizarFaltantes();
  if (decorando) { decorarOtraVez = true; return; }
  const py = proyecto();
  const dirs = Object.keys(py.git?.repos || {});
  if (!dirs.length) { if (mapaGit.size) { mapaGit = new Map(); $("numGit").hidden = true; explorador.decorarGit(mapaGit); pintarPestanas(); } return; }
  decorando = true;
  try {
    const motor = await motorGit();
    const mapa = new Map();
    for (const dir of dirs) {
      try {
        await motor.asegurarGit(py, dir);
        await motor.haciaGit(py, dir);
        const { preparados, sinPreparar, sinSeguimiento, conflictos } = await motor.estado(py, dir);
        const ruta = (r) => (dir ? `${dir}/${r}` : r);
        for (const c of preparados) if (c.tipo !== "eliminado") mapa.set(ruta(c.ruta), c.tipo === "nuevo" ? "A" : "M");
        for (const r of sinSeguimiento) mapa.set(ruta(r), "U");
        for (const c of sinPreparar) if (c.tipo !== "eliminado") mapa.set(ruta(c.ruta), "M");
        for (const r of conflictos) mapa.set(ruta(r), "C");
      } catch { /* repositorio sin respaldo todavía: se intenta en el próximo cambio */ }
    }
    mapaGit = mapa;
    $("numGit").hidden = !mapa.size;
    $("numGit").textContent = String(mapa.size);
    explorador.decorarGit(mapa);
    pintarPestanas();
  } catch { /* Git no se pudo cargar (sin conexión la primera vez) */ }
  finally {
    decorando = false;
    if (decorarOtraVez) { decorarOtraVez = false; programarDecoracionGit(300); }
  }
}

panelGit = new PanelGit({
  raiz: $("panelGit"), proyecto, usuario: user.nombre || "estudiante", aviso,
  motor: () => motorGit(),
  elegir: (titulo, opciones) => new Promise((ok) => abrirPaleta({ titulo, lista: opciones.map((o) => ({ etiqueta: o.texto, accion: () => ok(o.valor) })) })),
  alCambiar: (info) => proyectoCambio(info),
  correr: (c) => { panel.abrir(); panel.correr(c); },
  verDiff, abrir: (r) => abrir(r),
  pedir: async (titulo, ejemplo) => { const v = prompt(`${titulo}\nEjemplo: ${ejemplo}`); return v ? v.trim() : null; },
});
panelExt = new PanelExtensiones({
  raiz: $("panelExt"), proyecto, aviso,
  cwd: () => panel.activa?.sesion.cwd ?? "",
  pip: () => paquetesInstalados(),
  correr: (c) => { panel.abrir(); panel.correr(c); },
});
/** Barra lateral: archivos, control de código fuente (Git) o extensiones, como en VS Code. */
function vistaLateral(cual) {
  vistaGit = cual === "git"; vistaExt = cual === "ext";
  if (cual !== "archivos") alternarExplorador(true);
  $("arbol").hidden = cual !== "archivos";
  $("panelGit").hidden = !vistaGit;
  $("panelExt").hidden = !vistaExt;
  $("expTituloSeccion").textContent = vistaGit ? "Control de código fuente" : vistaExt ? "Extensiones" : "Mi proyecto";
  for (const [id, on] of [["verArchivos", cual === "archivos"], ["verGit", vistaGit], ["verExtensiones", vistaExt]]) { $(id).classList.toggle("activo", on); $(id).setAttribute("aria-pressed", String(on)); }
  if (vistaGit) panelGit.render();
  if (vistaExt) {
    if (actualizarFaltantes() && !FS.tieneArchivo(proyecto(), "package.json")) panelExt.tipo = "pip";
    panelExt.enfocar = true; panelExt.render();
  }
}
function alternarGit(mostrar = !vistaGit) { vistaLateral(mostrar ? "git" : "archivos"); }
function alternarExt(mostrar = !vistaExt) { vistaLateral(mostrar ? "ext" : "archivos"); }
$("verGit").onclick = () => alternarGit();
$("verArchivos").onclick = () => vistaLateral("archivos");
$("verExtensiones").onclick = () => alternarExt();
$("buscarArchivos").onclick = () => manejarAtajo("buscar-archivos");
$("abrirRapido").onclick = () => manejarAtajo("abrir-rapido");
$("estProblemas").onclick = verProblemas;

// ------------------------------------------------------------------------------- arranque ----
fijarAnchoExp(ui.anchoExp);
pintarAutoguardado();
alternarExplorador(ui.explorador !== false);
alternarAsistente(ui.asistente === null ? innerWidth >= 1440 : Boolean(ui.asistente));
pintarChat();
pintarGit();
explorador.render();
sincronizarModelos(proyecto(), (t) => !esMarcador(t));
pintarProblemas();
alCambiarProblemas(() => { clearTimeout(pintarProblemas.t); pintarProblemas.t = setTimeout(pintarProblemas, 250); });

const py0 = proyecto();
ui.abiertos = ui.abiertos.filter((r) => r === VISTA ? Boolean(paginaPrincipal(py0)) : FS.tieneArchivo(py0, r));
if (ui.activo !== null && !ui.abiertos.includes(ui.activo)) ui.activo = ui.abiertos[0] ?? null;
if (primeraVisita && !ui.abiertos.length) {
  const inicial = FS.tieneArchivo(py0, "index.html") ? "index.html" : Object.keys(py0.files).sort()[0];
  if (inicial) { ui.abiertos = [inicial]; ui.activo = inicial; }
}
if (ui.abiertos.includes(VISTA)) paginaVista = paginaPrincipal(py0);
activar(ui.activo, { enfocar: false });
programarDecoracionGit(900);
if (ui.panel) panel.abrir({ enfocar: false });
void entradas.iniciar();
