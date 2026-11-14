// Explorador de archivos: árbol con crear / renombrar en línea, eliminar, mover arrastrando y menú contextual.
import { dialogo, menuContextual } from "./dialogos.js";
import * as FS from "./fs.js";
import { chevron, iconoArchivo, iconoCarpeta } from "./iconos.js";

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export class Explorador {
  /**
   * @param {object} o
   * @param {HTMLElement} o.raiz
   * @param {()=>object} o.proyecto
   * @param {Set<string>} o.expandidas   carpetas abiertas (se comparte para poder guardarlas)
   * @param {(ruta:string)=>void} o.alAbrir
   * @param {(info:object)=>void} o.alCambiar   { origen, borrado?, movido?: [de, a], creado? }
   * @param {(ruta:string, eliminado:object)=>void} o.alBorrar   para ofrecer «Deshacer»
   * @param {(ruta:string)=>void} o.alAbrirTerminalEn
   */
  constructor({ raiz, proyecto, expandidas, alAbrir, alCambiar, alBorrar, alAbrirTerminalEn }) {
    Object.assign(this, { raiz, proyecto, expandidas, alAbrir, alCambiar, alBorrar, alAbrirTerminalEn });
    this.seleccion = null;
    this.activo = null;
    this.edicion = null;
    raiz.tabIndex = 0;
    raiz.setAttribute("role", "tree");
    raiz.setAttribute("aria-label", "Archivos del proyecto");
    raiz.addEventListener("click", (e) => this.#clic(e));
    raiz.addEventListener("contextmenu", (e) => this.#menu(e));
    raiz.addEventListener("keydown", (e) => this.#tecla(e));
    raiz.addEventListener("dragstart", (e) => { const f = e.target.closest(".fila"); if (!f || this.edicion) return e.preventDefault(); e.dataTransfer.setData("text/plain", f.dataset.ruta); e.dataTransfer.effectAllowed = "move"; });
    raiz.addEventListener("dragover", (e) => this.#arrastrarSobre(e));
    raiz.addEventListener("dragleave", (e) => { if (!raiz.contains(e.relatedTarget)) this.#limpiarDestino(); });
    raiz.addEventListener("drop", (e) => this.#soltar(e));
  }

  // ---------------------------------------------------------------- dibujo ----
  #filas() {
    const py = this.proyecto();
    const filas = [];
    const recorrer = (carpeta, nivel) => {
      const { dirs, files } = FS.hijos(py, carpeta);
      const nuevo = this.edicion && this.edicion.modo !== "renombrar" && this.edicion.padre === carpeta ? { tipo: "edicion", nivel, ruta: "" } : null;
      if (nuevo && this.edicion.modo === "carpeta") filas.push(nuevo);
      for (const d of dirs) {
        const ruta = FS.unir(carpeta, d);
        const abierta = this.expandidas.has(ruta);
        filas.push({ tipo: "dir", nombre: d, ruta, nivel, abierta });
        if (abierta) recorrer(ruta, nivel + 1);
      }
      if (nuevo && this.edicion.modo === "archivo") filas.push(nuevo);
      for (const f of files) filas.push({ tipo: "archivo", nombre: f, ruta: FS.unir(carpeta, f), nivel });
    };
    recorrer("", 0);
    return filas;
  }

  render() {
    const py = this.proyecto();
    const filas = this.#filas();
    if (this.seleccion && !FS.existe(py, this.seleccion)) this.seleccion = null;
    const html = filas.map((f) => {
      if (f.tipo === "edicion") return this.#filaEdicion(f.nivel, "", this.edicion.modo === "carpeta");
      if (this.edicion?.modo === "renombrar" && this.edicion.ruta === f.ruta) return this.#filaEdicion(f.nivel, f.nombre, f.tipo === "dir");
      const clases = ["fila", f.tipo === "dir" ? "dir" : "", f.ruta === this.seleccion ? "sel" : "", f.ruta === this.activo ? "activo" : ""].filter(Boolean).join(" ");
      const icono = f.tipo === "dir" ? `${chevron}${iconoCarpeta(f.abierta)}` : `<span class="chev-vacio"></span>${iconoArchivo(f.ruta)}`;
      return `<div class="${clases}" role="treeitem" aria-level="${f.nivel + 1}" ${f.tipo === "dir" ? `aria-expanded="${f.abierta}"` : ""} aria-selected="${f.ruta === this.seleccion}" data-ruta="${esc(f.ruta)}" data-tipo="${f.tipo}" draggable="true" style="--n:${f.nivel}" title="${esc(f.ruta)}">${icono}<span class="nom">${esc(f.nombre)}</span></div>`;
    }).join("");
    this.raiz.innerHTML = html || '<p class="arbol-vacio">No hay archivos.<br>Usa los botones de arriba para crear uno.</p>';
    this.raiz.classList.toggle("vacio", !html);
    if (this.edicion) {
      const input = this.raiz.querySelector(".fila-input");
      if (input) {
        input.focus();
        const punto = input.value.lastIndexOf(".");
        input.setSelectionRange(0, this.edicion.modo === "renombrar" && punto > 0 ? punto : input.value.length);
      }
    }
  }

  #filaEdicion(nivel, valor, esDir) {
    const icono = esDir ? `${chevron}${iconoCarpeta(false)}` : `<span class="chev-vacio"></span>${iconoArchivo(valor || "archivo.txt")}`;
    return `<div class="fila edicion" style="--n:${nivel}">${icono}<input class="fila-input" value="${esc(valor)}" spellcheck="false" autocomplete="off" aria-label="${this.edicion.modo === "renombrar" ? "Nuevo nombre" : esDir ? "Nombre de la carpeta" : "Nombre del archivo"}"><div class="fila-error" role="alert" hidden></div></div>`;
  }

  // -------------------------------------------------------------- selección ----
  seleccionar(ruta, { desplazar = true } = {}) {
    this.seleccion = ruta;
    this.render();
    if (desplazar) this.raiz.querySelector(".fila.sel")?.scrollIntoView({ block: "nearest" });
  }

  marcarActivo(ruta) {
    this.activo = ruta;
    if (ruta) {
      // Abre las carpetas que contienen el archivo para que se vea en el árbol.
      for (let c = FS.carpetaDe(ruta); c; c = FS.carpetaDe(c)) this.expandidas.add(c);
      this.seleccion = ruta;
    }
    this.render();
  }

  /** Carpeta donde se crearía algo nuevo según lo seleccionado. */
  carpetaDestino() {
    const py = this.proyecto();
    const s = this.seleccion;
    if (!s) return "";
    return FS.esCarpeta(py, s) ? s : FS.carpetaDe(s);
  }

  #clic(e) {
    if (this.edicion) return;
    const fila = e.target.closest(".fila");
    if (!fila) { this.seleccion = null; this.render(); return; }
    const { ruta, tipo } = fila.dataset;
    this.seleccion = ruta;
    if (tipo === "dir") {
      if (this.expandidas.has(ruta)) this.expandidas.delete(ruta); else this.expandidas.add(ruta);
      this.alCambiar({ origen: "ui" });
      this.render();
    } else {
      this.render();
      this.alAbrir(ruta);
    }
    this.raiz.focus({ preventScroll: true });
  }

  // ---------------------------------------------------------------- teclado ----
  #tecla(e) {
    if (this.edicion) return;
    const py = this.proyecto();
    const filas = [...this.raiz.querySelectorAll(".fila[data-ruta]")].map((f) => ({ ruta: f.dataset.ruta, tipo: f.dataset.tipo }));
    const i = filas.findIndex((f) => f.ruta === this.seleccion);
    const actual = filas[i];
    const mover = (n) => { if (filas[n]) this.seleccionar(filas[n].ruta); };
    if (e.key === "ArrowDown") { e.preventDefault(); mover(i < 0 ? 0 : i + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); mover(i < 0 ? 0 : i - 1); }
    else if (e.key === "Home") { e.preventDefault(); mover(0); }
    else if (e.key === "End") { e.preventDefault(); mover(filas.length - 1); }
    else if (e.key === "ArrowRight" && actual?.tipo === "dir") {
      e.preventDefault();
      if (!this.expandidas.has(actual.ruta)) { this.expandidas.add(actual.ruta); this.alCambiar({ origen: "ui" }); this.render(); } else mover(i + 1);
    } else if (e.key === "ArrowLeft" && actual) {
      e.preventDefault();
      if (actual.tipo === "dir" && this.expandidas.has(actual.ruta)) { this.expandidas.delete(actual.ruta); this.alCambiar({ origen: "ui" }); this.render(); }
      else if (FS.carpetaDe(actual.ruta)) this.seleccionar(FS.carpetaDe(actual.ruta));
    } else if (e.key === "Enter" && actual) {
      e.preventDefault();
      if (actual.tipo === "dir") { if (this.expandidas.has(actual.ruta)) this.expandidas.delete(actual.ruta); else this.expandidas.add(actual.ruta); this.alCambiar({ origen: "ui" }); this.render(); } else this.alAbrir(actual.ruta);
    } else if (e.key === "F2" && actual) { e.preventDefault(); this.renombrar(actual.ruta); }
    else if ((e.key === "Delete" || (e.key === "Backspace" && e.metaKey)) && actual && FS.existe(py, actual.ruta)) { e.preventDefault(); void this.eliminar(actual.ruta); }
  }

  // ----------------------------------------------------------- menú contextual ----
  #menu(e) {
    e.preventDefault();
    const fila = e.target.closest(".fila[data-ruta]");
    const ruta = fila?.dataset.ruta ?? null;
    if (ruta) this.seleccionar(ruta, { desplazar: false });
    else { this.seleccion = null; this.render(); }
    const py = this.proyecto();
    const carpeta = ruta ? (FS.esCarpeta(py, ruta) ? ruta : FS.carpetaDe(ruta)) : "";
    const items = [
      { texto: "Nuevo archivo", fn: () => this.nuevo("archivo", carpeta) },
      { texto: "Nueva carpeta", fn: () => this.nuevo("carpeta", carpeta) },
    ];
    if (ruta) {
      items.push("-",
        { texto: "Abrir en la terminal", fn: () => this.alAbrirTerminalEn(carpeta) },
        { texto: "Copiar ruta relativa", fn: () => navigator.clipboard?.writeText(ruta).catch(() => {}) },
        "-",
        { texto: "Renombrar", atajo: "F2", fn: () => this.renombrar(ruta) },
        { texto: "Eliminar", atajo: "Supr", peligro: true, fn: () => this.eliminar(ruta) });
    }
    menuContextual(e.clientX, e.clientY, items);
  }

  // --------------------------------------------------------- crear / renombrar ----
  nuevo(modo, carpeta = this.carpetaDestino()) {
    for (let c = carpeta; c; c = FS.carpetaDe(c)) this.expandidas.add(c);
    this.edicion = { modo, padre: carpeta };
    this.render();
    this.#enlazarEdicion();
  }

  renombrar(ruta) {
    if (!ruta || !FS.existe(this.proyecto(), ruta)) return;
    this.edicion = { modo: "renombrar", ruta };
    this.render();
    this.#enlazarEdicion();
  }

  #enlazarEdicion() {
    const input = this.raiz.querySelector(".fila-input");
    if (!input) return;
    const error = this.raiz.querySelector(".fila-error");
    const py = this.proyecto();
    const edicion = this.edicion;
    const destino = (nombre) => (edicion.modo === "renombrar" ? FS.unir(FS.carpetaDe(edicion.ruta), nombre) : FS.unir(edicion.padre, nombre));
    const problema = (nombre) => {
      if (!nombre) return null;
      const m = FS.errorDeNombre(nombre);
      if (m) return m;
      const ruta = destino(nombre);
      if (ruta !== edicion.ruta && FS.existe(py, ruta)) return `Ya existe «${nombre}» en esta carpeta.`;
      return null;
    };
    let terminado = false;
    const cancelar = () => { if (terminado) return; terminado = true; this.edicion = null; this.render(); this.raiz.focus({ preventScroll: true }); };
    const aceptar = () => {
      if (terminado) return;
      const nombre = input.value.trim();
      if (!nombre || (edicion.modo === "renombrar" && nombre === FS.nombreBase(edicion.ruta))) return cancelar();
      const m = problema(nombre);
      if (m) { error.textContent = m; error.hidden = false; input.classList.add("invalido"); input.focus(); return; }
      terminado = true;
      const ruta = destino(nombre);
      let r;
      if (edicion.modo === "renombrar") r = FS.mover(py, edicion.ruta, ruta);
      else if (edicion.modo === "carpeta") r = FS.crearCarpeta(py, ruta);
      else r = FS.crearArchivo(py, ruta, "");
      this.edicion = null;
      if (!r.ok) { this.render(); this.alCambiar({ origen: "aviso", error: r.error }); return; }
      if (edicion.modo === "renombrar") {
        if (this.expandidas.has(edicion.ruta)) { this.expandidas.delete(edicion.ruta); this.expandidas.add(ruta); }
        for (const c of [...this.expandidas]) if (FS.dentroDe(c, edicion.ruta) && c !== edicion.ruta) { this.expandidas.delete(c); this.expandidas.add(ruta + c.slice(edicion.ruta.length)); }
        this.seleccion = ruta;
        this.alCambiar({ origen: "explorador", movido: [edicion.ruta, ruta] });
      } else {
        if (edicion.modo === "carpeta") this.expandidas.add(ruta);
        this.seleccion = ruta;
        this.alCambiar({ origen: "explorador", creado: ruta });
      }
      this.render();
      if (edicion.modo === "archivo") this.alAbrir(ruta);
      else this.raiz.focus({ preventScroll: true });
    };
    input.addEventListener("input", () => { const m = problema(input.value.trim()); error.hidden = !m; error.textContent = m || ""; input.classList.toggle("invalido", Boolean(m)); });
    input.addEventListener("keydown", (e) => {
      e.stopPropagation();
      if (e.key === "Enter") { e.preventDefault(); aceptar(); }
      else if (e.key === "Escape") { e.preventDefault(); cancelar(); }
    });
    input.addEventListener("blur", () => { setTimeout(() => { if (!terminado && !input.classList.contains("invalido")) { if (input.value.trim()) aceptar(); else cancelar(); } else if (!terminado && input.classList.contains("invalido")) cancelar(); }, 0); });
  }

  // ------------------------------------------------------------------ borrar ----
  async eliminar(ruta) {
    const py = this.proyecto();
    if (!FS.existe(py, ruta)) return false;
    const esDir = FS.esCarpeta(py, ruta);
    const n = FS.archivosEn(py, ruta).length;
    const ok = await dialogo({
      titulo: `¿Eliminar «${FS.nombreBase(ruta)}»?`,
      mensaje: esDir ? (n ? `Se eliminará la carpeta y ${n === 1 ? "el archivo que contiene" : `los ${n} archivos que contiene`}.` : "Se eliminará la carpeta vacía.") : "Se eliminará el archivo.",
      botones: [{ texto: "Eliminar", valor: true, peligro: true }, { texto: "Cancelar", valor: false, cancelar: true }],
    });
    this.raiz.focus({ preventScroll: true });
    if (!ok) return false;
    const r = FS.borrar(py, ruta);
    if (!r.ok) { this.alCambiar({ origen: "aviso", error: r.error }); return false; }
    for (const c of [...this.expandidas]) if (FS.dentroDe(c, ruta)) this.expandidas.delete(c);
    this.seleccion = null;
    this.alBorrar(ruta, r.eliminado);
    this.alCambiar({ origen: "explorador", borrado: ruta });
    this.render();
    return true;
  }

  // --------------------------------------------------------- arrastrar y soltar ----
  #destinoDe(e) {
    const f = e.target.closest(".fila[data-ruta]");
    if (!f) return "";
    return f.dataset.tipo === "dir" ? f.dataset.ruta : FS.carpetaDe(f.dataset.ruta);
  }

  #limpiarDestino() { this.raiz.querySelectorAll(".destino").forEach((x) => x.classList.remove("destino")); this.raiz.classList.remove("destino-raiz"); }

  #arrastrarSobre(e) {
    if (!e.dataTransfer.types.includes("text/plain")) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    this.#limpiarDestino();
    const f = e.target.closest(".fila[data-ruta]");
    const dir = this.#destinoDe(e);
    if (!f || dir === "") this.raiz.classList.add("destino-raiz");
    else (f.dataset.tipo === "dir" ? f : this.raiz.querySelector(`.fila[data-ruta="${CSS.escape(dir)}"]`))?.classList.add("destino");
  }

  #soltar(e) {
    e.preventDefault();
    this.#limpiarDestino();
    const origen = e.dataTransfer.getData("text/plain");
    const py = this.proyecto();
    if (!origen || !FS.existe(py, origen)) return;
    const dir = this.#destinoDe(e);
    if (FS.carpetaDe(origen) === dir) return;
    const destino = FS.unir(dir, FS.nombreBase(origen));
    const r = FS.mover(py, origen, destino);
    if (!r.ok) { this.alCambiar({ origen: "aviso", error: r.error }); return; }
    if (dir) this.expandidas.add(dir);
    this.seleccion = destino;
    this.alCambiar({ origen: "explorador", movido: [origen, destino] });
    this.render();
  }
}
