// Entradas y salidas del proyecto: subir archivos e imágenes, subir una carpeta, importar/descargar .zip
// y sincronizar con una carpeta del computador. Aquí va toda la parte de interfaz (diálogos, avisos, selectores);
// la lógica está en importar.js, zip.js, archivos.js y carpeta.js (probadas sin navegador).
import { aviso, dialogo, menuContextual } from "./dialogos.js";
import * as FS from "./fs.js";
import { archivosDe, esMarcador, formatoBytes, leerMarcador } from "./archivos.js";
import { importarEn, paraExportar, prepararArchivos, resumenPlan } from "./importar.js";
import { DiscoNavegador, Sincronizador, recuerdo, soporteCarpeta } from "./carpeta.js";
import { DiscoConector } from "./equipo.js";
import { crearZip, leerZip, zipDisponible } from "./zip.js";

const AVISO_IMAGENES = "cc_trabajo_aviso_archivos";
const INTERVALO = 3000;

const reglasArchivos = (uso) => [
  `Cualquier tipo: imágenes, videos, audio, PDF, fuentes, datos… Hasta ${formatoBytes(uso?.max_archivo ?? 1024 ** 3)} por archivo y ${formatoBytes(uso?.limite ?? 10 * 1024 ** 3)} en total por cuenta.`,
  "El código y los textos (hasta 1 MB por archivo y 5 millones de caracteres en total) se pueden editar. Los demás archivos se ven (imágenes, videos, audio, PDF) o se descargan, pero no se editan.",
  "Se guardan en tu cuenta, así que los ves desde cualquier computador. Necesitas conexión para subirlos; los grandes tardan según tu internet.",
  "Subir el mismo archivo dos veces no ocupa más. Cuando borras uno, su espacio se libera aproximadamente una hora después.",
];

const nombresVisibles = (lista, n = 40) => [...lista.slice(0, n).map((o) => `${o.ruta} — ${o.motivo}`), ...(lista.length > n ? [`… y ${lista.length - n} más`] : [])];

export class Entradas {
  /**
   * @param {object} o
   * @param {()=>object} o.proyecto
   * @param {(info:object)=>void} o.cambio          avisar a la página que el proyecto cambió
   * @param {import("./archivos.js").ClienteArchivos} o.archivos
   * @param {number|string} o.usuarioId
   * @param {HTMLElement} o.botonCarpeta            elemento de la barra de estado para la carpeta vinculada
   * @param {()=>void} [o.antesDeLeer]               pasa al proyecto el texto sin guardar de los editores
   * @param {()=>Promise<object|string|null>} [o.elegirOrigen]  ¿dónde está la carpeta? → { equipo, carpeta } | "navegador" | null
   * @param {(equipo:object|null)=>void} [o.alEquipo]  la carpeta abierta es (o deja de ser) la de un equipo con el Conector
   * @param {()=>void} [o.abrirConector]            muestra cómo conectar un equipo
   * @param {object} [o.conector]                   { fsEquipo, listarEquipos } de conector.js
   * @param {(o:{silencioso?:boolean})=>Promise<boolean>} [o.alAntesEquipo]  pasa Trabajo a «trabajar en tu equipo» (sin nube)
   */
  constructor({ proyecto, cambio, archivos, usuarioId, botonCarpeta, antesDeLeer = () => {}, elegirOrigen = null, alEquipo = () => {}, abrirConector = () => {}, conector = null, alAntesEquipo = async () => true }) {
    Object.assign(this, { proyecto, cambio, archivos, botonCarpeta, antesDeLeer, elegirOrigen, alEquipo, abrirConector, conector, alAntesEquipo });
    this.vigilaEquipo = null;
    this.clave = `u${usuarioId}`;
    this.sinc = null;
    this.disco = null;
    this.estadoCarpeta = "ninguna"; // ninguna | ok | permiso | error | sincronizando
    this.temporizador = null;
    this.retraso = null;
    this.guardadoBase = null;
    botonCarpeta.addEventListener("click", (e) => this.#clicCarpeta(e));
    addEventListener("focus", () => this.#programar(0));
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") this.#programar(0); });
  }

  // ------------------------------------------------------------------ menú ----
  menu(x, y) {
    const soporte = soporteCarpeta();
    const items = [
      { texto: "Subir archivos…", fn: () => this.subirArchivos("") },
      { texto: "📎 Documentos (Word, Excel, PowerPoint, PDF)…", fn: () => this.alDocumentos?.() },
      { texto: "Subir una carpeta…", fn: () => this.subirCarpeta("") },
      { texto: "Importar .zip…", fn: () => this.importarZip() },
      { texto: "Descargar proyecto (.zip)", fn: () => this.descargarZip() },
      "-",
    ];
    if (this.sinc?.vinculada || this.estadoCarpeta === "permiso") {
      const nombre = this.disco?.nombre ?? "carpeta";
      if (this.estadoCarpeta === "permiso") items.push({ texto: `Reconectar carpeta «${nombre}»`, fn: () => this.reconectar() });
      else items.push({ texto: `Sincronizar ahora con «${nombre}»`, fn: () => this.sincronizarAhora(true) });
      if (this.disco?.esEquipo && this.itemsEquipo) items.push(...this.itemsEquipo());
      items.push({ texto: this.disco?.esEquipo ? "Cerrar la carpeta del equipo (volver a la nube)" : "Dejar de sincronizar la carpeta", fn: () => this.desvincular() });
    } else items.push({ texto: this.elegirOrigen ? "Abrir carpeta del computador o celular…" : soporte.disponible ? "Abrir carpeta del computador…" : "Abrir carpeta del computador (no disponible aquí)…", fn: () => this.vincularCarpeta() });
    items.push("-", { texto: "Espacio usado…", fn: () => this.mostrarEspacio() });
    menuContextual(x, y, items);
  }

  // --------------------------------------------------------- importar (común) ----
  async #espacio() {
    const u = await this.archivos.consultarUso();
    return { libre: Math.max(0, u.limite - u.uso), maxArchivo: u.max_archivo };
  }

  async #importar(origen, { destino = "", reemplazar = false, quitarRaiz = false } = {}) {
    this.antesDeLeer();
    const hayArchivos = origen.archivos.length > 0;
    const quitar = aviso("Importando…", { ms: 6 * 3600 * 1000 });
    let resultado;
    try {
      resultado = await importarEn(this.proyecto(), origen, {
        destino, reemplazar, quitarRaiz,
        subir: (d, o) => this.archivos.subir(d, o),
        espacio: hayArchivos ? () => this.#espacio() : null,
        progreso: (t) => quitar.actualizar(t),
      });
    } catch (e) {
      quitar();
      await dialogo({ titulo: "No se pudo importar", mensaje: e.message, botones: [{ texto: "Entendido", valor: true, cancelar: true }] });
      return null;
    }
    quitar();
    const { plan, escritos } = resultado;
    const rutas = [...plan.textos.map((t) => t.ruta), ...plan.binarios.map((i) => i.ruta)];
    if (escritos || plan.carpetas.length || reemplazar) this.cambio({ origen: "importar", rutas, destino });
    const detalles = plan.omitidos.length || plan.renombrados.length || plan.comoArchivo.length;
    aviso(resumenPlan(plan, escritos), {
      tipo: escritos ? "info" : "error", ms: detalles ? 14000 : 6000,
      accion: detalles ? { texto: "Ver detalles", fn: () => this.#detalles(plan) } : undefined,
    });
    return resultado;
  }

  #detalles(plan) {
    const lista = [
      ...nombresVisibles(plan.omitidos),
      ...plan.renombrados.slice(0, 20).map((r) => `${r.de} → ${r.a} (renombrado: sin espacios ni tildes)`),
      ...(plan.comoArchivo || []).slice(0, 20).map((r) => `${r}: texto muy grande, guardado completo como archivo (se ve y se descarga, no se edita)`),
    ];
    return dialogo({
      titulo: "Detalles de la importación", ancho: true,
      mensaje: plan.omitidos.length ? `${plan.omitidos.length} ${plan.omitidos.length === 1 ? "archivo no entró" : "archivos no entraron"} al proyecto:` : "Algunos archivos cambiaron:",
      lista,
      nota: "Los nombres solo pueden tener letras sin tilde, números, punto, guion y guion bajo. Límites: 1000 archivos por proyecto, 1 GB por archivo y 10 GB por cuenta.",
      botones: [{ texto: "Cerrar", valor: true, cancelar: true }],
    });
  }

  /** Abre el selector de archivos del sistema. Resuelve con [] si se cancela (en navegadores que lo informan). */
  #elegir({ multiple = true, accept = "", carpeta = false } = {}) {
    return new Promise((resolver) => {
      const input = document.createElement("input");
      input.type = "file";
      input.multiple = multiple;
      if (accept) input.accept = accept;
      if (carpeta) input.webkitdirectory = true;
      input.style.display = "none";
      input.addEventListener("change", () => { resolver([...input.files]); input.remove(); });
      input.addEventListener("cancel", () => { resolver([]); input.remove(); });
      document.body.appendChild(input);
      input.click();
    });
  }

  #leerFiles(files) {
    return prepararArchivos(files.map((f) => ({ ruta: f.webkitRelativePath || f.name, archivo: f })));
  }

  async #avisoImagenesUnaVez() {
    try { if (localStorage.getItem(AVISO_IMAGENES)) return true; } catch { /* sin almacenamiento: se muestra siempre */ }
    let uso = this.archivos.uso;
    try { uso = await this.archivos.consultarUso(); } catch { /* sin conexión: se avisará al subir */ }
    const ok = await dialogo({
      titulo: "Subir archivos",
      mensaje: uso ? `Usas ${formatoBytes(uso.uso)} de ${formatoBytes(uso.limite)} en tu cuenta.` : "Los archivos se guardan en tu cuenta:",
      lista: reglasArchivos(uso),
      nota: "Los nombres con espacios o tildes se arreglan solos (por ejemplo «Mi foto.png» → «Mi-foto.png»). No cierres la pestaña mientras se suben.",
      botones: [{ texto: "Elegir archivos", valor: true }, { texto: "Cancelar", valor: false, cancelar: true }],
    });
    if (ok) try { localStorage.setItem(AVISO_IMAGENES, "1"); } catch { /* sin almacenamiento */ }
    return ok;
  }

  // --------------------------------------------------------------- subir ----
  async subirArchivos(destino = "") {
    if (!(await this.#avisoImagenesUnaVez())) return;
    const files = await this.#elegir({ multiple: true });
    if (!files.length) return;
    await this.#importar({ archivos: await this.#leerFiles(files) }, { destino });
  }

  /** Documentos de Office y PDF: van a la carpeta «documentos» y se pueden ver en Trabajo sin descargarlos. */
  async subirDocumentos(destino = "documentos") {
    const files = await this.#elegir({ multiple: true, accept: ".docx,.xlsx,.xlsm,.pptx,.pdf,.doc,.xls,.ppt,.odt,.ods,.odp,.rtf,.csv,.txt,.md" });
    if (!files.length) return [];
    const leidos = await this.#leerFiles(files);
    await this.#importar({ archivos: leidos }, { destino });
    return leidos.map((a) => `${destino}/${a.ruta}`);
  }

  async subirCarpeta(destino = "") {
    if (!("webkitdirectory" in document.createElement("input"))) {
      await dialogo({ titulo: "Este navegador no permite subir carpetas", mensaje: "Los celulares y algunos navegadores solo dejan elegir archivos sueltos.", lista: ["Comprime la carpeta en un .zip y usa «Importar .zip».", "O elige los archivos uno por uno con «Subir archivos o imágenes»."], botones: [{ texto: "Entendido", valor: true, cancelar: true }] });
      return;
    }
    const ok = await dialogo({
      titulo: "Subir una carpeta",
      mensaje: "Se copia una sola vez: los cambios que hagas después en tu computador no se sincronizan.",
      lista: [
        "Funciona en todos los navegadores de computador. El navegador te preguntará si quieres subir los archivos: es normal.",
        "Se ignoran .git, node_modules, __pycache__ y similares.",
        `Límites: ${FS.LIMITES.archivos} archivos por proyecto, 1 GB por archivo y 10 GB por cuenta.`,
        ...(soporteCarpeta().disponible ? ["¿Quieres que se mantenga sincronizada? Usa «Abrir carpeta del computador»."] : []),
      ],
      botones: [{ texto: "Elegir carpeta", valor: true }, { texto: "Cancelar", valor: false, cancelar: true }],
    });
    if (!ok) return;
    const files = await this.#elegir({ carpeta: true });
    if (!files.length) return;
    await this.#importar({ archivos: await this.#leerFiles(files) }, { destino });
  }

  /** Archivos y carpetas soltados sobre el explorador. */
  async soltados({ entradas, archivos, destino }) {
    const leidos = [];
    const carpetas = [];
    const leerEntrada = async (entrada, prefijo) => {
      const ruta = prefijo ? `${prefijo}/${entrada.name}` : entrada.name;
      if (entrada.isFile) {
        const f = await new Promise((ok, mal) => entrada.file(ok, mal));
        leidos.push(...(await prepararArchivos([{ ruta, archivo: f }])));
      } else if (entrada.isDirectory) {
        if (leidos.length > 5000) return;
        carpetas.push(ruta);
        const lector = entrada.createReader();
        for (;;) {
          const lote = await new Promise((ok, mal) => lector.readEntries(ok, mal));
          if (!lote.length) break;
          for (const hijo of lote) await leerEntrada(hijo, ruta);
        }
      }
    };
    try {
      if (entradas.length) for (const e of entradas) await leerEntrada(e, "");
      else leidos.push(...(await this.#leerFiles(archivos)));
    } catch {
      aviso("No se pudieron leer algunos archivos soltados.", { tipo: "error" });
    }
    if (!leidos.length && !carpetas.length) return;
    await this.#importar({ archivos: leidos, carpetas }, { destino });
  }

  // ------------------------------------------------------------------ zip ----
  async importarZip() {
    if (!zipDisponible()) {
      await dialogo({ titulo: "Este navegador no puede abrir .zip", mensaje: "Hace falta una versión más reciente.", lista: ["Chrome o Edge 80 o más reciente", "Firefox 113 o más reciente", "Safari 16.4 o más reciente (iPhone/iPad con iOS 16.4+)"], nota: "Mientras tanto puedes descomprimir el .zip en tu computador y usar «Subir una carpeta».", botones: [{ texto: "Entendido", valor: true, cancelar: true }] });
      return;
    }
    const [archivo] = await this.#elegir({ multiple: false, accept: ".zip,application/zip,application/x-zip-compressed" });
    if (!archivo) return;
    if (archivo.size > 1024 ** 3) { aviso(`El .zip pesa ${formatoBytes(archivo.size)}; el máximo es 1 GB (se abre en la memoria del navegador). Descomprímelo y usa «Subir una carpeta».`, { tipo: "error", ms: 12000 }); return; }
    let contenido;
    try { contenido = await leerZip(new Uint8Array(await archivo.arrayBuffer())); }
    catch (e) { await dialogo({ titulo: "No se pudo abrir el .zip", mensaje: e.message, botones: [{ texto: "Entendido", valor: true, cancelar: true }] }); return; }
    const py = this.proyecto();
    const nActual = Object.keys(py.files).length;
    const modo = await dialogo({
      titulo: `Importar «${archivo.name}»`,
      mensaje: `Trae ${contenido.archivos.length} ${contenido.archivos.length === 1 ? "archivo" : "archivos"}. ¿Cómo quieres importarlo?`,
      lista: [
        "Agregar: se suma a tu proyecto. Si hay un archivo con el mismo nombre, se reemplaza.",
        `Reemplazar: tu proyecto queda igual al .zip (se quitan tus ${nActual} archivos actuales).`,
        "Si todo viene dentro de una carpeta (como los .zip de GitHub), se usa su contenido.",
      ],
      nota: "Imágenes, videos, PDF y demás archivos se suben a tu cuenta (hasta 1 GB cada uno). Un .zip de más de 1 GB descomprimido conviene subirlo como carpeta.",
      botones: [{ texto: "Agregar", valor: "agregar" }, { texto: "Reemplazar todo", valor: "reemplazar", peligro: true }, { texto: "Cancelar", valor: null, cancelar: true }],
    });
    if (!modo) return;
    if (modo === "reemplazar" && nActual && !(await this.#confirmarReemplazo(nActual))) return;
    await this.#importar(contenido, { reemplazar: modo === "reemplazar", quitarRaiz: true });
  }

  async #confirmarReemplazo(n) {
    const r = await dialogo({
      titulo: "¿Reemplazar todo el proyecto?",
      mensaje: `Se quitarán tus ${n} archivos actuales. Si los necesitas, descarga antes una copia.`,
      botones: [{ texto: "Descargar copia primero", valor: "copia" }, { texto: "Reemplazar", valor: "si", peligro: true }, { texto: "Cancelar", valor: "no", cancelar: true }],
    });
    if (r === "copia") { const ok = await this.descargarZip(); return ok && this.#confirmarReemplazo(n); }
    return r === "si";
  }

  async descargarZip() {
    this.antesDeLeer();
    const py = this.proyecto();
    if (!Object.keys(py.files).length && !py.folders.length) { aviso("El proyecto está vacío: no hay nada que descargar."); return false; }
    const quitar = aviso("Preparando el .zip…", { ms: 3600 * 1000 });
    try {
      const { archivos, carpetas, fallidas, grandes } = await paraExportar(py, (m) => this.archivos.blob(m), { esMarcador, leerMarcador });
      const zip = await crearZip(archivos, { carpetas });
      const fecha = new Date().toISOString().slice(0, 10);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([zip], { type: "application/zip" }));
      a.download = `mi-proyecto-${fecha}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 60000);
      quitar();
      if (grandes.length) aviso(`El .zip se arma en la memoria del navegador y tiene un tope de 1 GB: ${grandes.length} ${grandes.length === 1 ? "archivo grande quedó" : "archivos grandes quedaron"} fuera (${grandes.slice(0, 3).join(", ")}${grandes.length > 3 ? "…" : ""}). Descárgalos uno por uno con clic derecho → Descargar.`, { tipo: "error", ms: 20000 });
      if (fallidas.length) aviso(`Se descargó, pero ${fallidas.length} ${fallidas.length === 1 ? "archivo no se pudo incluir" : "archivos no se pudieron incluir"} (¿sin conexión?): ${fallidas.slice(0, 3).join(", ")}`, { tipo: "error", ms: 12000 });
      else aviso(`Descargado: ${archivos.length} archivos (${formatoBytes(zip.length)}).`, { ms: 4000 });
      return true;
    } catch (e) {
      quitar();
      aviso(`No se pudo crear el .zip: ${e.message}`, { tipo: "error" });
      return false;
    }
  }

  /** Descarga un solo archivo del proyecto (texto o archivo de la cuenta). */
  async descargarArchivo(ruta) {
    const texto = this.proyecto().files[ruta];
    if (texto === undefined) return;
    const a = document.createElement("a");
    a.download = FS.nombreBase(ruta);
    if (esMarcador(texto)) await this.archivos.asegurar?.(texto);
    a.href = esMarcador(texto) ? this.archivos.url(texto, { descargar: true, nombre: FS.nombreBase(ruta) }) : URL.createObjectURL(new Blob([texto], { type: "text/plain;charset=utf-8" }));
    document.body.appendChild(a);
    a.click();
    a.remove();
    if (a.href.startsWith("blob:")) setTimeout(() => URL.revokeObjectURL(a.href), 30000);
  }

  // ---------------------------------------------------------------- espacio ----
  async mostrarEspacio() {
    const py = this.proyecto();
    const bin = archivosDe(py);
    let cuenta = "no se pudo consultar (¿sin conexión?)";
    let max = "1 GB";
    try { const u = await this.archivos.consultarUso(); cuenta = `${formatoBytes(u.uso)} de ${formatoBytes(u.limite)} (${Math.round((u.uso / u.limite) * 100)} %)`; max = formatoBytes(u.max_archivo); } catch { /* se muestra el aviso */ }
    const n = Object.keys(py.files).length;
    if (!FS.hayLimites()) {
      await dialogo({
        titulo: "Espacio del proyecto",
        lista: [`Archivos: ${n.toLocaleString("es")}`, `Carpetas: ${py.folders.length.toLocaleString("es")}`],
        nota: "Estás trabajando en la carpeta de tu equipo: no hay límites de la cuenta ni se usa tu espacio de CódigoCamp. El único límite es tu disco.",
        botones: [{ texto: "Cerrar", valor: true, cancelar: true }],
      });
      return;
    }
    await dialogo({
      titulo: "Espacio del proyecto",
      lista: [
        `Archivos: ${n} de ${FS.LIMITES.archivos} (${bin.rutas.length} guardados en la cuenta: imágenes, videos…)`,
        `Carpetas: ${py.folders.length} de ${FS.LIMITES.carpetas}`,
        `Texto: ${FS.usoCaracteres(py).toLocaleString("es")} de ${FS.LIMITES.caracteres.toLocaleString("es")} caracteres`,
        `Espacio de archivos en tu cuenta: ${cuenta} · máximo ${max} por archivo`,
      ],
      nota: "El texto editable tiene su propio límite porque se guarda también en este navegador. El espacio de un archivo borrado se libera aproximadamente una hora después de guardar.",
      botones: [{ texto: "Cerrar", valor: true, cancelar: true }],
    });
  }

  // ------------------------------------------------------ carpeta del computador ----
  async #explicarNoDisponible(soporte) {
    const r = await dialogo({
      titulo: "Abrir carpeta no está disponible aquí",
      mensaje: soporte.motivo,
      lista: [soporte.consejo].filter(Boolean),
      nota: "Navegadores compatibles: Chrome, Edge y Opera en computador (Windows, macOS, Linux o ChromeOS).",
      botones: [{ texto: "Importar .zip", valor: "zip" }, { texto: "Subir una carpeta", valor: "carpeta" }, { texto: "Cerrar", valor: null, cancelar: true }],
    });
    if (r === "zip") this.importarZip();
    else if (r === "carpeta") this.subirCarpeta("");
  }

  /** La carpeta abierta es la de un equipo conectado (terminal y Git reales): { id, equipo, sistema, carpeta } o null. */
  get equipo() { return this.disco?.esEquipo && this.sinc?.vinculada ? { ...this.disco.equipo, carpeta: this.disco.carpeta } : null; }

  async vincularCarpeta() {
    if (this.elegirOrigen) {
      const r = await this.elegirOrigen();
      if (!r) return;
      if (r.equipo) { await this.vincularEquipo(r.equipo, r.carpeta); return; }
    }
    const soporte = soporteCarpeta();
    if (!soporte.disponible) { await this.#explicarNoDisponible(soporte); return; }
    const seguir = await dialogo({
      titulo: "Abrir una carpeta de tu computador", ancho: true,
      mensaje: `Tu proyecto y la carpeta se mantendrán iguales: lo que cambies en CódigoCamp se guarda en la carpeta, y lo que cambies con otro programa (por ejemplo otro editor) aparece aquí.`,
      avisos: [
        `Solo funciona en Chrome, Edge y Opera de computador (estás usando ${soporte.navegador}). En Firefox, Safari y celulares usa ZIP.`,
        "El navegador pedirá permiso cada vez que abras la página. En Chrome puedes elegir «Permitir en cada visita» para no repetirlo.",
        "Si usas un computador del colegio o del SENA, la carpeta queda en ESE computador. Tu cuenta igual guarda una copia del proyecto, así que en otro equipo lo verás, pero sin la carpeta.",
        "No abras la misma carpeta en dos pestañas a la vez.",
      ],
      lista: [
        "Crea una carpeta para el proyecto: el navegador no deja abrir Escritorio, Documentos ni carpetas del sistema.",
        "Se sincroniza cualquier archivo de hasta 1 GB (los nombres pueden tener espacios y tildes). node_modules, .git, venv y similares se quedan en tu carpeta sin tocarse.",
        `Límites: ${FS.LIMITES.archivos} archivos por proyecto y 10 GB por cuenta. Los archivos grandes tardan en subir la primera vez.`,
        "Si el mismo archivo cambia en los dos lados, se queda la versión del computador y la de CódigoCamp se guarda como «nombre.conflicto.ext».",
      ],
      botones: [{ texto: "Elegir carpeta", valor: true }, { texto: "Cancelar", valor: false, cancelar: true }],
    });
    if (!seguir) return;
    let handle;
    try { handle = await showDirectoryPicker({ id: "codigocamp", mode: "readwrite" }); }
    catch (e) {
      if (e?.name !== "AbortError") aviso(`No se pudo abrir la carpeta: ${e.message}`, { tipo: "error" });
      return;
    }
    const disco = new DiscoNavegador(handle);
    if ((await disco.permiso(true)) !== "granted") { aviso("Sin permiso para escribir en esa carpeta: no se puede sincronizar.", { tipo: "error" }); return; }
    await this.#empezar(disco);
  }

  /** Abre como proyecto una carpeta del computador o celular conectado con el Conector (ya elegida en ese equipo). */
  async vincularEquipo(equipo, carpeta) {
    if (this.sinc?.vinculada) { this.#detener(); this.sinc.desvincular(); this.sinc = null; }
    // Desde aquí se trabaja directo en el equipo: el proyecto de la nube queda guardado y vuelve al cerrar la carpeta
    if (!(await this.alAntesEquipo({ equipo, carpeta }))) return;
    const disco = this.#discoEquipo(equipo, carpeta);
    if (await this.#empezar(disco)) this.alEquipo({ ...equipo, carpeta });
    else { this.#detener(); this.sinc = null; this.disco = null; this.alEquipo(null, "cerrar"); }
  }

  #discoEquipo(equipo, carpeta) {
    const d = new DiscoConector({ id: equipo.id, equipo: equipo.equipo, sistema: equipo.sistema }, carpeta, this.conector.fsEquipo);
    d.alVirus = (ruta, mensaje) => aviso(mensaje, { tipo: "error", ms: 15000 });
    return d;
  }

  /** Primera sincronización con una carpeta (del navegador o del equipo). true si quedó vinculada. */
  async #empezar(disco, { silencioso = false } = {}) {
    const handle = { name: disco.nombre };
    let enCarpeta;
    try { enCarpeta = (await disco.listar()).archivos.length; }
    catch (e) { aviso(`No se pudo leer la carpeta: ${e.message}`, { tipo: "error" }); return false; }
    this.antesDeLeer();
    const nProyecto = Object.keys(this.proyecto().files).length;
    let modo = "combinar";
    if (enCarpeta && nProyecto) {
      modo = await dialogo({
        titulo: `La carpeta «${handle.name}» ya tiene archivos`,
        mensaje: `Tiene ${enCarpeta} ${enCarpeta === 1 ? "archivo" : "archivos"} y tu proyecto tiene ${nProyecto}. ¿Qué hacemos al empezar?`,
        lista: [
          "Usar la carpeta: el proyecto pasa a ser igual a la carpeta (se quitan los archivos actuales del proyecto).",
          "Combinar: tu proyecto se escribe en la carpeta (si hay un archivo con el mismo nombre, gana el del proyecto) y lo que solo esté en la carpeta entra al proyecto.",
        ],
        botones: [{ texto: "Usar la carpeta", valor: "carpeta" }, { texto: "Combinar", valor: "combinar" }, { texto: "Cancelar", valor: null, cancelar: true }],
      });
      if (!modo) return false;
      if (modo === "carpeta" && !(await this.#confirmarReemplazo(nProyecto))) return false;
    } else if (enCarpeta) modo = "carpeta";
    await this.#conectar(disco, null);
    const quitar = aviso(disco.esEquipo ? `Abriendo «${disco.nombre}» de ${disco.equipo.equipo}…` : "Sincronizando la carpeta por primera vez (los archivos grandes tardan en subir)…", { ms: 6 * 3600 * 1000 });
    try {
      const r = await this.sinc.vincular(modo);
      quitar();
      const omit = [...r.omitidos].map(([ruta, motivo]) => ({ ruta, motivo }));
      if (!(silencioso && !omit.length)) aviso(disco.esEquipo ? `«${handle.name}» abierta desde tu equipo${omit.length ? ` · ${omit.length} archivos muy grandes se ven solo en la terminal` : ""}.` : `Carpeta «${handle.name}» vinculada${r.traidos ? ` · ${r.traidos} archivos traídos` : ""}${omit.length ? ` · ${omit.length} se quedan solo en la carpeta` : ""}.`, {
        ms: 9000, accion: omit.length ? { texto: "Ver cuáles", fn: () => this.#detalles({ omitidos: omit, renombrados: [] }) } : undefined,
      });
      this.#pintarCarpeta("ok");
      return true;
    } catch (e) {
      quitar();
      this.#fallo(e);
      return false;
    }
  }

  /** Al cargar la página: si había una carpeta vinculada, se retoma (o se pide reconectarla). */
  async iniciar() {
    const guardado = await recuerdo.leer(this.clave);
    if (guardado?.equipo && this.conector) { await this.#retomarEquipo(guardado); return; }
    if (!soporteCarpeta().disponible) return;
    if (!guardado?.handle) return;
    const disco = new DiscoNavegador(guardado.handle);
    let permiso = "prompt";
    try { permiso = await disco.permiso(false); } catch { /* se pide luego */ }
    await this.#conectar(disco, guardado.base || {}, guardado.cache || null);
    if (permiso === "granted") { this.#pintarCarpeta("ok"); this.#programar(0); }
    else {
      this.#pintarCarpeta("permiso");
      aviso(`Para seguir sincronizando la carpeta «${disco.nombre}», el navegador necesita tu permiso otra vez.`, { ms: 15000, accion: { texto: "Reconectar", fn: () => this.reconectar() } });
    }
  }

  /** Al volver a Trabajo: la carpeta del equipo sigue abierta si su Conector está encendido (si no, se espera a que vuelva). */
  async #retomarEquipo(g) {
    // Al volver a Trabajo se empieza de cero con la carpeta del equipo (manda la carpeta: nunca se toca la nube)
    this.disco = this.#discoEquipo(g.equipo, g.carpeta);
    // Al recargar, el Conector puede tardar un instante en aparecer «en línea» (red lenta, el equipo se estaba
    // reconectando…): se insiste unos segundos antes de rendirse, en vez de soltar el equipo a la primera.
    let eq = null, quitar = null;
    for (let intento = 0; intento < 14; intento++) {
      let lista = null;
      try { lista = await this.conector.listarEquipos(); } catch { /* red: se reintenta */ }
      if (lista) {
        eq = lista.find((e) => e.id === g.equipo.id) || null;
        if (!eq) { quitar?.(); this.disco = null; await recuerdo.borrar(this.clave); return; } // lo desconectaste
        if (eq.en_linea) break;
      }
      if (intento === 1) quitar = aviso(`Reconectando con ${g.equipo.equipo}…`, { ms: 60000 });
      await new Promise((ok) => setTimeout(ok, 1500));
    }
    quitar?.();
    if (eq?.en_linea && await this.#raizEquipo(eq, g.carpeta) && await this.alAntesEquipo({ equipo: eq, carpeta: g.carpeta, silencioso: true })) {
      if (await this.#empezar(this.disco, { silencioso: true })) { this.alEquipo({ ...eq, carpeta: g.carpeta }, "retomar"); return; }
      this.alEquipo(null, "cerrar");
    }
    void this.#soltarEquipo();
  }

  /** Pide al Conector que use esta carpeta (si se cerró, al abrirlo vuelve a la última). */
  async #raizEquipo(eq, carpeta) {
    if ((eq.carpeta || "") === carpeta) return true;
    try { await this.conector.fsEquipo(eq, "raiz", { ruta: carpeta }); return true; }
    catch (e) { aviso(`No se pudo abrir «${this.disco?.nombre}» en ${eq.equipo}: ${e.message}`, { tipo: "error", ms: 12000 }); return false; }
  }

  /** El equipo está apagado o sin el Conector: se avisa y, en cuanto vuelve, se sigue solo. */
  /** El equipo se desconectó (o no está conectado): se suelta todo lo del equipo y Trabajo vuelve al proyecto guardado
   *  en CódigoCamp. Para seguir en el equipo, se abre su carpeta otra vez cuando el Conector esté abierto. */
  async #soltarEquipo() {
    this.#detener();
    clearInterval(this.vigilaEquipo);
    this.vigilaEquipo = null;
    const nombre = this.disco?.equipo?.equipo;
    this.sinc?.desvincular?.();
    this.sinc = null;
    this.disco = null;
    await recuerdo.borrar(this.clave).catch?.(() => {});
    this.#pintarCarpeta("ninguna");
    this.alEquipo(null, "desconectado", nombre);
  }

  async #conectar(disco, base, cache = null) {
    this.#detener();
    this.disco = disco;
    let maxArchivo;
    if (!disco.esEquipo) try { maxArchivo = (await this.archivos.consultarUso()).max_archivo; } catch { /* se usa el de fábrica */ }   // tu equipo no usa la cuenta
    this.sinc = new Sincronizador({
      disco, base, cache, ...(maxArchivo ? { maxArchivo } : {}),
      proyecto: () => this.proyecto(), // solo lo guardado: con el autoguardado apagado, lo no guardado no viaja
      alCambiar: (info) => this.cambio(info),
      subirArchivo: (d, o) => this.archivos.subir(d, o),
      leerArchivo: (m) => this.archivos.blob(m),
      ...(disco.esEquipo && this.archivos.registrarEquipo ? { registrarEquipo: (m, cargar, parte) => this.archivos.registrarEquipo(m, cargar, parte) } : {}),
      guardarBase: (b, c) => this.#guardarBase(b, c),
      alAviso: (a) => this.#avisoSinc(a),
    });
    // Carpetas enormes: si revisar la carpeta tarda, se revisa con menos frecuencia (tu equipo no se calienta)
    this.temporizador = setInterval(() => {
      if (document.visibilityState !== "visible") return;
      const d = this.disco;
      if (d?.duracionListar && Date.now() - (d.finListar || 0) < d.duracionListar * 4) return;
      this.#programar(0);
    }, INTERVALO);
  }

  #guardarBase(base, cache) {
    clearTimeout(this.guardadoBase);
    this.guardadoBase = setTimeout(() => {
      if (!this.disco) return;
      const donde = this.disco.esEquipo ? { equipo: this.disco.equipo, carpeta: this.disco.carpeta } : { handle: this.disco.raiz };
      recuerdo.guardar(this.clave, { ...donde, base, cache, nombre: this.disco.nombre });
    }, 300);
  }

  #avisoSinc(a) {
    if (a.tipo === "conflicto") aviso(`«${a.ruta}» cambió en los dos lados: quedó la versión del computador${a.copia ? ` y la tuya está en «${a.copia}»` : ""}.`, { ms: 12000, tipo: "error" });
    else if (a.tipo === "no-cabe") aviso(`«${a.ruta}» se queda solo en la carpeta: ${a.motivo}.`, { ms: 9000, tipo: "error" });
    else if (a.tipo === "omitido") aviso(`«${a.ruta}»: ${a.motivo}.`, { ms: 9000, tipo: "error" });
    else aviso(`No se pudo sincronizar «${a.ruta}»: ${a.motivo}`, { ms: 9000, tipo: "error" });
  }

  async reconectar() {
    if (!this.disco) return;
    if (this.disco.esEquipo) {
      const eq = (await this.conector.listarEquipos()).find((e) => e.id === this.disco.equipo.id);
      if (!eq?.en_linea) {
        void this.#soltarEquipo();
        return;
      }
      if (!(await this.#raizEquipo(eq, this.disco.carpeta))) return;
      if (!this.sinc) {   // la página empezó sin el equipo: se entra a trabajar en el equipo desde cero
        if (!(await this.alAntesEquipo({ equipo: eq, carpeta: this.disco.carpeta, silencioso: true }))) return;
        if (!(await this.#empezar(this.disco))) { this.alEquipo(null, "cerrar"); return; }
      } else if (!this.temporizador) await this.#conectar(this.disco, this.sinc.base || {}, Object.fromEntries(this.sinc.cacheDisco));
      this.#pintarCarpeta("ok");
      this.alEquipo({ ...eq, carpeta: this.disco.carpeta });
      await this.sincronizarAhora(false);
      return;
    }
    try {
      if ((await this.disco.permiso(true)) !== "granted") { aviso("Sin permiso no se puede sincronizar la carpeta.", { tipo: "error" }); return; }
    } catch (e) { this.#fallo(e); return; }
    if (!this.temporizador) await this.#conectar(this.disco, this.sinc?.base || {}, this.sinc ? Object.fromEntries(this.sinc.cacheDisco) : null);
    this.#pintarCarpeta("ok");
    await this.sincronizarAhora(true);
  }

  async sincronizarAhora(avisar = false) {
    if (!this.sinc?.vinculada || this.estadoCarpeta === "permiso") return;
    try {
      this.#pintarCarpeta("sincronizando");
      const r = await this.sinc.sincronizar();
      this.#pintarCarpeta("ok");
      if (avisar && r) {
        const n = r.alProyecto.length + r.alDisco.length + r.borradosDisco.length + r.borradosProyecto.length;
        aviso(n ? `Sincronizado: ${r.alProyecto.length + r.borradosProyecto.length} cambios traídos y ${r.alDisco.length + r.borradosDisco.length} enviados.` : "La carpeta y el proyecto ya están iguales.", { ms: 3500 });
      }
    } catch (e) { this.#fallo(e); }
  }

  #fallo(e) {
    this.#detener();
    if (!this.disco) return;   // ya se soltó la carpeta (llegó tarde el error de otra sincronización)
    const nombre = this.disco.nombre ?? "la carpeta";
    if (this.disco.esEquipo && (e?.desconectado || /desconect|no está conectado/i.test(e?.message || ""))) {
      void this.#soltarEquipo();
      return;
    }
    if (e?.name === "NotAllowedError" || e?.name === "SecurityError") {
      this.#pintarCarpeta("permiso");
      aviso(`El navegador retiró el permiso para «${nombre}».`, { tipo: "error", ms: 15000, accion: { texto: "Reconectar", fn: () => this.reconectar() } });
    } else if (e?.name === "NotFoundError") {
      this.#pintarCarpeta("error");
      aviso(`No se encuentra la carpeta «${nombre}» (¿se movió o se borró?). Tu proyecto sigue a salvo en tu cuenta.`, { tipo: "error", ms: 15000, accion: { texto: "Elegir otra", fn: () => this.vincularCarpeta() } });
    } else {
      this.#pintarCarpeta("error");
      aviso(`Se detuvo la sincronización con «${nombre}»: ${e?.message || e}`, { tipo: "error", ms: 15000, accion: { texto: "Reintentar", fn: () => this.reconectar() } });
    }
  }

  #detener() {
    clearInterval(this.temporizador);
    clearTimeout(this.retraso);
    this.temporizador = null;
  }

  async desvincular() {
    const equipo = this.disco?.esEquipo;
    const ok = await dialogo(equipo ? {
      titulo: "¿Cerrar la carpeta de tu equipo?",
      mensaje: "No se borra nada: tus archivos se quedan en tu equipo. Trabajo vuelve a tu proyecto de la nube, tal como lo dejaste.",
      botones: [{ texto: "Cerrar y volver a la nube", valor: true }, { texto: "Cancelar", valor: false, cancelar: true }],
    } : {
      titulo: "¿Dejar de sincronizar la carpeta?",
      mensaje: "No se borra nada: tus archivos se quedan en la carpeta y en tu proyecto. Solo dejarán de copiarse los cambios.",
      botones: [{ texto: "Dejar de sincronizar", valor: true }, { texto: "Cancelar", valor: false, cancelar: true }],
    });
    if (!ok) return;
    this.#detener();
    clearInterval(this.vigilaEquipo);
    const eraEquipo = this.disco?.esEquipo;
    this.sinc?.desvincular();
    this.sinc = null;
    this.disco = null;
    await recuerdo.borrar(this.clave);
    this.#pintarCarpeta("ninguna");
    if (eraEquipo) this.alEquipo(null, "cerrar");
  }

  /** La página avisa de cada cambio del proyecto: se sincroniza poco después. */
  alCambiarProyecto(info = {}) {
    if (info.origen === "carpeta" || info.origen === "ui") return;
    this.#programar(this.disco?.esEquipo ? 250 : 700);   // con tu equipo (Conector) el viaje es corto: se copia casi al instante
  }

  #programar(ms) {
    if (!this.sinc?.vinculada || !this.temporizador || this.estadoCarpeta === "permiso" || this.estadoCarpeta === "error") return;
    clearTimeout(this.retraso);
    this.retraso = setTimeout(() => this.sincronizarAhora(false), ms);
  }

  #pintarCarpeta(estado) {
    if (estado === "sincronizando" && this.estadoCarpeta !== "ok") return;
    if (estado !== "sincronizando") this.estadoCarpeta = estado;
    const b = this.botonCarpeta;
    b.hidden = estado === "ninguna";
    const nombre = this.disco?.nombre ?? "";
    const eq = this.disco?.esEquipo ? this.disco.equipo.equipo : null;
    b.textContent = eq ? (estado === "permiso" ? `🖥 ${eq} · ${nombre} · desconectado` : `🖥 ${eq} · ${nombre}`)
      : estado === "permiso" ? `Carpeta · ${nombre} · reconectar` : `Carpeta · ${nombre}`;
    b.className = `estado-item ${estado === "ok" || estado === "sincronizando" ? "carpeta-ok" : estado === "permiso" ? "carpeta-aviso" : "carpeta-error"}`;
    const hora = this.sinc?.ultima ? ` Última sincronización: ${this.sinc.ultima.toLocaleTimeString("es")}.` : "";
    b.title = eq && estado === "permiso" ? `«${eq}» no está conectado. Abre el Conector en ese equipo y sigue solo.`
      : eq && estado !== "error" ? `Carpeta «${this.disco.carpeta}» de ${eq}: lo que guardas aquí se guarda allá y lo que cambias allá (terminal, git, otro editor) aparece aquí.${this.sinc?.ultima ? ` Última vez: ${this.sinc.ultima.toLocaleTimeString("es")}.` : ""}`
      : estado === "permiso" ? "Clic para dar permiso otra vez y seguir sincronizando."
      : estado === "error" ? "La sincronización se detuvo. Clic para ver opciones."
        : `Sincronizado con la carpeta «${nombre}» de tu computador.${hora} Clic para opciones.`;
  }

  #clicCarpeta(e) {
    if (this.estadoCarpeta === "permiso") { this.reconectar(); return; }
    const r = e.currentTarget.getBoundingClientRect();
    menuContextual(r.left, r.top - 8, [
      { texto: "Sincronizar ahora", fn: () => (this.estadoCarpeta === "error" ? this.reconectar() : this.sincronizarAhora(true)) },
      { texto: "Abrir otra carpeta…", fn: () => this.vincularCarpeta() },
      "-",
      { texto: "Dejar de sincronizar", fn: () => this.desvincular() },
    ]);
  }
}
