// Panel inferior estilo VS Code: pestañas TERMINAL y CONSOLA, varias terminales, historial, Tab, Ctrl+C...
// La lógica de comandos vive en shell.js; aquí solo hay interfaz.
import { RenderAnsi } from "./ansi.js";
import { rutaAbsoluta } from "./fs.js";
import { enColumnas } from "./shell.js";

const ICONOS = {
  mas: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3v10M3 8h10" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>',
  basura: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 4.5h10M6 4.5V3h4v1.5M4.5 4.5l.6 8.5h5.8l.6-8.5M7 7v4M9 7v4" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>',
  maximizar: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 10l4.5-4.5 4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>',
  restaurar: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 6l4.5 4.5L12.5 6" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>',
  cerrar: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>',
  terminal: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 3.5h11v9h-11zM5 6.5l2 1.5-2 1.5M8.5 10h2.5" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>',
};
export const iconoPanel = (n) => ICONOS[n];

const MAX_LINEAS = 3000;
const MAX_HISTORIAL = 200;
const LARGO_COMUN = (lista) => lista.reduce((a, b) => { let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i += 1; return a.slice(0, i); });

const nombreCorto = (nombre) => (String(nombre || "").trim().split(/\s+/)[0] || "estudiante").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9_-]/g, "") || "estudiante";

class Terminal {
  constructor(panel, numero) {
    this.panel = panel;
    this.numero = numero;
    this.ansi = new RenderAnsi();
    this.actual = null;
    this.entrada = null;
    this.ocupado = false;
    this.cerrada = false;
    this.lectura = null;
    this.indiceHistorial = null;
    this.borrador = "";
    this.ultimoTab = false;
    this.sesion = panel.shell.nuevaSesion({
      out: (t) => this.escribir(t), err: (t) => this.escribir(t),
      limpiar: () => { this.salida.textContent = ""; this.actual = null; },
      cerrar: () => panel.matar(this),
      leerLinea: (texto, opciones) => this.pedirLinea(texto, opciones),
    });
    this.sesion.historial = panel.historial;
    this.raiz = document.createElement("div");
    this.raiz.className = "term";
    this.raiz.tabIndex = 0;
    this.raiz.setAttribute("role", "log");
    this.raiz.setAttribute("aria-label", `Terminal ${numero}`);
    this.medida = document.createElement("span");
    this.medida.className = "term-medida";
    this.medida.textContent = "MMMMMMMMMM";
    this.salida = document.createElement("div");
    this.salida.className = "term-salida";
    this.raiz.append(this.medida, this.salida);
    this.raiz.addEventListener("mouseup", () => { if (!getSelection().toString()) this.enfocar(); });
    this.raiz.addEventListener("keydown", (e) => this.#teclaGeneral(e));
    this.raiz.addEventListener("contextmenu", () => { /* permite copiar/pegar con el menú del navegador */ });
    this.escribir("\x1b[90mTerminal de CódigoCamp · escribe \x1b[0m\x1b[1mhelp\x1b[0m\x1b[90m para ver los comandos.\x1b[0m\n");
    this.#prompt();
  }

  get columnas() {
    const ancho = this.medida.getBoundingClientRect().width / 10;
    return ancho > 0 ? Math.max(20, Math.floor((this.salida.clientWidth || 640) / ancho)) : 80;
  }

  escribir(texto) {
    const partes = String(texto).split("\n");
    partes.forEach((trozo, i) => {
      if (trozo) this.#linea().insertAdjacentHTML("beforeend", this.ansi.render(trozo));
      if (i < partes.length - 1) { this.#linea(); this.actual = null; }
    });
    while (this.salida.childElementCount > MAX_LINEAS) this.salida.firstElementChild.remove();
    this.#bajar();
  }

  #linea() {
    if (!this.actual) {
      this.actual = document.createElement("div");
      this.actual.className = "term-linea";
      this.salida.appendChild(this.actual);
    }
    return this.actual;
  }

  #bajar() {
    if (this.pendiente) return;
    this.pendiente = requestAnimationFrame(() => { this.pendiente = 0; this.raiz.scrollTop = this.raiz.scrollHeight; });
  }

  enfocar() { (this.entrada || this.raiz).focus({ preventScroll: true }); }

  #textoPrompt() {
    const py = this.panel.proyecto();
    const g = py.git;
    const rama = g.initialized ? ` \x1b[36m(\x1b[31m${g.branch}\x1b[36m)\x1b[0m` : "";
    const venv = this.sesion.venv ? `\x1b[90m(${this.sesion.venv.split("/").pop()})\x1b[0m ` : "";
    return `${venv}\x1b[32m@${nombreCorto(this.panel.shell.usuario)} \x1b[0m➜ \x1b[1;34m${rutaAbsoluta(this.sesion.cwd)}\x1b[0m${rama} $ `;
  }

  #crearEntrada(contenedor) {
    const input = document.createElement("input");
    input.className = "term-entrada";
    input.type = "text";
    input.spellcheck = false;
    input.autocomplete = "off";
    input.autocapitalize = "off";
    input.setAttribute("aria-label", "Escribe un comando");
    input.addEventListener("keydown", (e) => this.#teclaEntrada(e));
    input.addEventListener("input", () => { this.ultimoTab = false; this.#finBusqueda(); });
    input.addEventListener("paste", (e) => this.#pegar(e));
    contenedor.appendChild(input);
    this.entrada = input;
    this.#bajar();
    input.focus({ preventScroll: true });
    return input;
  }

  #prompt() {
    if (this.actual) this.actual = null;
    const linea = document.createElement("div");
    linea.className = "term-linea term-prompt";
    const ps1 = document.createElement("span");
    ps1.className = "term-ps1";
    // Si el bloque sigue abierto (for … do, if … then, comillas), bash pide el resto con «> »
    ps1.innerHTML = new RenderAnsi().render(this.bloqueAbierto ? "\x1b[90m> \x1b[0m" : this.#textoPrompt());
    linea.appendChild(ps1);
    this.salida.appendChild(linea);
    this.indiceHistorial = null;
    this.#crearEntrada(linea);
  }

  #congelar(texto) {
    const input = this.entrada;
    const span = document.createElement("span");
    span.className = "term-comando";
    span.textContent = texto;
    input.replaceWith(span);
    this.entrada = null;
    this.actual = null;
  }

  /** Lee una línea para un programa en ejecución (readline, input()). Devuelve null si se cierra la entrada (Ctrl+D). */
  pedirLinea(texto, { secreto = false } = {}) {
    return new Promise((resolver) => {
      if (texto) this.escribir(texto);
      // Líneas pegadas de antemano (varias respuestas a la vez): se usan en orden, como en una terminal real.
      if (this.colaLectura?.length && !secreto) { const v = this.colaLectura.shift(); this.#congelarTexto(v); resolver(v); return; }
      this.lectura = { resolver, secreto };
      const input = this.#crearEntrada(this.#linea());
      if (secreto) { input.type = "password"; input.autocomplete = "off"; input.setAttribute("aria-label", "Valor secreto (no se muestra)"); }
    });
  }

  #teclaEntrada(e) {
    const input = this.entrada;
    const ctrl = e.ctrlKey || e.metaKey;
    if (this.lectura) {
      if (e.key === "Enter") { e.preventDefault(); const v = input.value; this.#congelar(this.lectura.secreto ? "" : v); this.escribir("\n"); const { resolver } = this.lectura; this.lectura = null; resolver(v); }
      else if (ctrl && e.key.toLowerCase() === "d" && !input.value) { e.preventDefault(); this.#congelar(""); this.escribir("\n"); const { resolver } = this.lectura; this.lectura = null; resolver(null); }
      else if (ctrl && e.key.toLowerCase() === "c" && input.selectionStart === input.selectionEnd) { e.preventDefault(); this.interrumpir(); }
      return;
    }
    if (e.key === "Enter") { e.preventDefault(); this.#finBusqueda(); void this.#enviar(); return; }
    if (e.key === "ArrowUp" || e.key === "ArrowDown") {
      e.preventDefault();
      const h = this.panel.historial;
      if (!h.length) return;
      if (this.indiceHistorial === null) { if (e.key === "ArrowDown") return; this.borrador = input.value; this.indiceHistorial = h.length; }
      this.indiceHistorial += e.key === "ArrowUp" ? -1 : 1;
      if (this.indiceHistorial < 0) this.indiceHistorial = 0;
      if (this.indiceHistorial >= h.length) { this.indiceHistorial = null; input.value = this.borrador; } else input.value = h[this.indiceHistorial];
      input.setSelectionRange(input.value.length, input.value.length);
      return;
    }
    if (e.key === "Tab") { e.preventDefault(); this.#completar(); return; }
    if (e.key === "Escape" && this.busqueda) { e.preventDefault(); input.value = this.busqueda.texto; this.#finBusqueda(); return; }
    if (!ctrl) return;
    const k = e.key.toLowerCase();
    if (k === "c" && input.selectionStart === input.selectionEnd) { e.preventDefault(); this.bloqueAbierto = ""; this.busqueda = null; this.#congelar(`${input.value}^C`); this.#prompt(); }
    else if (k === "r") {
      // Búsqueda en el historial (como bash): escribe parte de un comando y pulsa Ctrl+R (otra vez = más antiguo)
      e.preventDefault();
      const h = this.panel.historial;
      this.busqueda ??= { texto: input.value, desde: h.length };
      const { texto } = this.busqueda;
      let i = this.busqueda.desde - 1;
      while (i >= 0 && !h[i].includes(texto)) i -= 1;
      if (i >= 0) {
        this.busqueda.desde = i;
        input.value = h[i];
        input.title = `(búsqueda en el historial) «${texto}» — Ctrl+R: más antiguo · Enter: ejecutar · Esc: cancelar`;
        input.classList.add("buscando");
        const pos = h[i].indexOf(texto);
        input.setSelectionRange(pos, pos + texto.length);
      } else input.classList.add("sin-resultado");
    }
    else if (k === "l") { e.preventDefault(); const v = input.value; this.sesion.limpiar(); this.#prompt(); this.entrada.value = v; }
    else if (k === "u") { e.preventDefault(); input.value = input.value.slice(input.selectionStart); input.setSelectionRange(0, 0); }
    else if (k === "a") { e.preventDefault(); input.setSelectionRange(0, 0); }
    else if (k === "e") { e.preventDefault(); input.setSelectionRange(input.value.length, input.value.length); }
    else if (k === "w") { e.preventDefault(); const a = input.value.slice(0, input.selectionStart).replace(/\s*\S*\s*$/, ""); input.value = a + input.value.slice(input.selectionStart); input.setSelectionRange(a.length, a.length); }
    else if (k === "d" && !input.value) { e.preventDefault(); this.panel.matar(this); }
  }

  #teclaGeneral(e) {
    if (!this.ocupado || this.lectura) return;
    const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key.toLowerCase() === "c" && !getSelection().toString()) { e.preventDefault(); this.interrumpir(); }
  }

  interrumpir() {
    if (this.lectura) { const { resolver } = this.lectura; this.lectura = null; if (this.entrada) this.#congelar(this.entrada.value); resolver(null); }
    this.escribir("^C\n");
    this.control?.abort();
  }

  #finBusqueda() {
    if (!this.busqueda) return;
    this.busqueda = null;
    this.entrada?.classList.remove("buscando", "sin-resultado");
    if (this.entrada) this.entrada.title = "";
  }

  #completar() {
    const input = this.entrada;
    const antes = input.value.slice(0, input.selectionStart);
    const { desde, opciones } = this.panel.shell.completar(antes, this.sesion);
    if (!opciones.length) return;
    const parcial = antes.slice(desde);
    const comun = LARGO_COMUN(opciones);
    const despues = input.value.slice(input.selectionStart);
    const poner = (t) => { input.value = antes.slice(0, desde) + t + despues; const p = desde + t.length; input.setSelectionRange(p, p); };
    if (opciones.length === 1) { poner(opciones[0]); return; }
    if (comun.length > parcial.length) { poner(comun); return; }
    if (this.ultimoTab) {
      const copia = this.entrada.value;
      this.#congelar(copia);
      const etiquetas = opciones.map((o) => o.trim());
      this.escribir("\n");
      this.escribir(enColumnas(etiquetas, this.columnas) + "\n");
      this.#prompt();
      this.entrada.value = copia;
      this.ultimoTab = false;
    } else this.ultimoTab = true;
  }

  /** Pegar varias líneas: cada línea es un comando (o una respuesta, si un programa está pidiendo datos). */
  #pegar(e) {
    const texto = e.clipboardData?.getData("text/plain") ?? "";
    if (!/[\r\n]/.test(texto)) return;
    e.preventDefault();
    const input = this.entrada;
    const lineas = texto.replace(/\r\n?/g, "\n").split("\n");
    const ultima = lineas.pop();               // lo que va después del último salto queda escrito, sin ejecutar
    const antes = input.value.slice(0, input.selectionStart);
    const despues = input.value.slice(input.selectionEnd);
    lineas[0] = antes + lineas[0];
    if (this.lectura) {
      const [primera, ...resto] = lineas;
      this.colaLectura = [...(this.colaLectura ?? []), ...resto];
      input.value = primera;
      input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true, cancelable: true }));
      return;
    }
    void this.#enviarVarias(lineas, ultima + despues);
  }

  async #enviarVarias(lineas, resto) {
    for (const linea of lineas) {
      if (this.cerrada || !this.entrada) return;
      this.entrada.value = linea;
      await this.#enviar();
      if (this.control?.signal.aborted) { this.colaLectura = []; break; }
    }
    if (this.entrada && resto) { this.entrada.value = resto; this.entrada.setSelectionRange(resto.length, resto.length); }
  }

  #congelarTexto(v) { this.escribir(v + "\n"); }

  async #enviar() {
    const linea = this.entrada.value;
    this.#congelar(linea);
    const anterior = this.bloqueAbierto ?? "";
    const completo = anterior ? `${anterior}\n${linea}` : linea;
    if (this.panel.shell.incompleta?.(completo)) {
      this.bloqueAbierto = completo;
      if (this.actual) this.actual = null;
      this.#prompt();
      return;
    }
    this.bloqueAbierto = "";
    // En el historial queda en una sola línea (como hace bash): for i in 1 2; do echo $i; done
    const unaLinea = completo.split("\n").reduce((t, l, i) => {
      if (!i) return l;
      const sep = /(\b(do|then|else|in)|[{|]|&&|\|\||\\)\s*$/.test(t) || !t.trim() ? " " : "; ";
      return t.replace(/\\\s*$/, "") + sep + l.trim();
    }, "");
    if (unaLinea.trim()) this.panel.agregarHistorial(unaLinea);
    await this.#correr(completo);
  }

  async #correr(linea) {
    this.ocupado = true;
    this.panel.alOcupado();
    this.control = new AbortController();
    this.sesion.senal = this.control.signal;
    this.raiz.focus({ preventScroll: true });
    let codigo = 0;
    try { codigo = await this.panel.shell.ejecutar(linea, this.sesion); }
    catch (error) { codigo = 1; this.escribir(`Error inesperado: ${error?.message || error}\n`); }
    // Como la terminal de VS Code con Copilot: si un comando falla, se ofrece arreglarlo con la IA
    if (codigo !== 0 && codigo !== 130 && !this.control?.signal.aborted && this.panel.alIA && !/^\s*(false|exit|test|\[)/.test(linea) && !this.cerrada) {
      const fila = document.createElement("div");
      fila.className = "term-linea term-ia";
      const b = document.createElement("button");
      b.type = "button";
      b.className = "term-ia-btn";
      b.textContent = "✨ Arreglar con IA";
      b.title = "La IA explica el error y propone cómo arreglarlo";
      const lineaCmd = linea.split("\n")[0].slice(0, 200);
      b.onclick = () => { b.disabled = true; this.panel.alIA(lineaCmd); };
      fila.append(b);
      this.salida.appendChild(fila);
    }
    if (this.sonarAlTerminar) {   // botón Ejecutar: sonido de «programa terminó bien» o de error
      this.sonarAlTerminar = false;
      import("/js/sonidos.js").then(({ sonar }) => sonar(this.control?.signal.aborted ? "clic" : codigo === 0 ? "programa_ok" : "programa_error")).catch(() => {});
    }
    this.colaLectura = [];
    this.ocupado = false;
    this.panel.alOcupado();
    if (this.cerrada) return;
    if (this.actual) this.actual = null;
    this.#prompt();
  }

  /**
   * Escribe y ejecuta un comando como si la persona lo hubiera tecleado (botón Ejecutar).
   * Si hay un programa corriendo, lo detiene primero (así «Ejecutar» nunca se queda esperando).
   */
  async lanzar(linea) {
    if (this.ocupado) {
      this.interrumpir();
      const limite = Date.now() + 4000;
      while ((this.ocupado || !this.entrada) && Date.now() < limite) await new Promise((r) => setTimeout(r, 25));
      if (this.ocupado || !this.entrada) { this.escribir("\x1b[31mNo se pudo detener el programa anterior. Recarga la página si no responde.\x1b[0m\n"); return false; }
    }
    this.entrada.value = linea;
    this.sonarAlTerminar = true;
    import("/js/sonidos.js").then(({ sonar }) => sonar("ejecutar")).catch(() => {});
    void this.#enviar();
    return true;
  }

  destruir() {
    this.cerrada = true;
    this.control?.abort();
    this.raiz.remove();
  }
}

export class PanelInferior {
  /**
   * @param {object} o
   * @param {HTMLElement} o.raiz     contenedor del panel
   * @param {Shell} o.shell
   * @param {()=>object} o.proyecto
   * @param {Storage} [o.storage] y {string} o.claveHistorial
   * @param {(abierto:boolean)=>void} [o.alCambiar]
   */
  constructor({ raiz, shell, proyecto, claveHistorial, storage = globalThis.localStorage, alCambiar = () => {}, alOcupado = () => {}, alIA = null }) {
    this.alIA = alIA;
    Object.assign(this, { raiz, shell, proyecto, claveHistorial, storage, alCambiar });
    this.alOcupado = () => alOcupado(this.hayProgramaCorriendo);
    this.terminales = [];
    this.activa = null;
    this.contador = 0;
    this.pestana = "terminal";
    this.maximizado = false;
    this.abierto = false;
    try { this.historial = JSON.parse(storage.getItem(claveHistorial) || "[]").filter((h) => typeof h === "string").slice(-MAX_HISTORIAL); } catch { this.historial = []; }

    raiz.classList.add("panel-inf");
    raiz.innerHTML = `
      <div class="panel-cab">
        <div class="panel-tabs" role="tablist" aria-label="Paneles inferiores">
          <button type="button" role="tab" class="panel-tab on" data-tab="terminal" aria-selected="true">TERMINAL</button>
          <button type="button" role="tab" class="panel-tab" data-tab="consola" aria-selected="false">CONSOLA<span class="punto-aviso" hidden></span></button>
        </div>
        <div class="panel-acciones">
          <div class="term-lista" role="tablist" aria-label="Terminales abiertas"></div>
          <button type="button" class="icono-btn" data-acc="nueva" title="Nueva terminal" aria-label="Nueva terminal">${ICONOS.mas}</button>
          <button type="button" class="icono-btn" data-acc="matar" title="Eliminar terminal" aria-label="Eliminar terminal">${ICONOS.basura}</button>
          <button type="button" class="icono-btn" data-acc="max" title="Maximizar panel" aria-label="Maximizar panel">${ICONOS.maximizar}</button>
          <button type="button" class="icono-btn" data-acc="cerrar" title="Cerrar panel (Ctrl+\`)" aria-label="Cerrar panel">${ICONOS.cerrar}</button>
        </div>
      </div>
      <div class="panel-cuerpo">
        <div class="term-contenedor" data-vista="terminal"></div>
        <div class="consola" data-vista="consola" role="log" aria-label="Consola de la vista previa" hidden><p class="consola-vacia">Aquí aparecen los mensajes de console.log y los errores de tu vista previa.</p></div>
      </div>`;
    this.$ = (s) => raiz.querySelector(s);
    this.contenedor = this.$(".term-contenedor");
    this.consolaEl = this.$(".consola");
    this.lista = this.$(".term-lista");
    raiz.addEventListener("click", (e) => {
      const tab = e.target.closest("[data-tab]");
      if (tab) return this.mostrarPestana(tab.dataset.tab);
      const acc = e.target.closest("[data-acc]")?.dataset.acc;
      if (acc === "nueva") this.nueva();
      else if (acc === "matar") (this.pestana === "consola" ? this.limpiarConsola() : this.matar(this.activa));
      else if (acc === "max") this.maximizar();
      else if (acc === "cerrar") this.cerrar();
      const chip = e.target.closest("[data-term]");
      if (chip) { const t = this.terminales.find((x) => x.numero === Number(chip.dataset.term)); if (e.target.closest(".chip-x")) this.matar(t); else this.activar(t); }
    });
  }

  agregarHistorial(linea) {
    if (this.historial[this.historial.length - 1] !== linea) this.historial.push(linea);
    this.historial.splice(0, Math.max(0, this.historial.length - MAX_HISTORIAL));
    try { this.storage.setItem(this.claveHistorial, JSON.stringify(this.historial)); } catch { /* sin espacio: el historial queda en memoria */ }
  }

  abrir({ enfocar = true } = {}) {
    if (!this.abierto) { this.abierto = true; this.raiz.hidden = false; this.alCambiar(true); }
    if (this.pestana === "terminal" && !this.terminales.length) this.nueva();
    if (enfocar && this.pestana === "terminal") requestAnimationFrame(() => this.activa?.enfocar());
  }

  cerrar() {
    this.abierto = false;
    this.raiz.hidden = true;
    this.maximizado = false;
    this.alCambiar(false);
  }

  alternar() { if (this.abierto) this.cerrar(); else this.abrir(); }

  maximizar() {
    this.maximizado = !this.maximizado;
    this.raiz.classList.toggle("maximizado", this.maximizado);
    const b = this.$('[data-acc="max"]');
    b.innerHTML = this.maximizado ? ICONOS.restaurar : ICONOS.maximizar;
    b.title = b.ariaLabel = this.maximizado ? "Restaurar tamaño del panel" : "Maximizar panel";
    this.alCambiar(this.abierto);
  }

  mostrarPestana(nombre) {
    this.pestana = nombre;
    this.raiz.querySelectorAll(".panel-tab").forEach((b) => { const on = b.dataset.tab === nombre; b.classList.toggle("on", on); b.ariaSelected = String(on); });
    this.contenedor.hidden = nombre !== "terminal";
    this.consolaEl.hidden = nombre !== "consola";
    this.lista.hidden = nombre !== "terminal";
    this.$('[data-acc="nueva"]').hidden = nombre !== "terminal";
    const borrar = this.$('[data-acc="matar"]');
    borrar.title = borrar.ariaLabel = nombre === "consola" ? "Limpiar consola" : "Eliminar terminal";
    if (nombre === "consola") this.$(".punto-aviso").hidden = true;
    else requestAnimationFrame(() => this.activa?.enfocar());
  }

  nueva() {
    this.contador += 1;
    const t = new Terminal(this, this.contador);
    this.terminales.push(t);
    this.contenedor.appendChild(t.raiz);
    this.activar(t);
    this.mostrarPestana("terminal");
    if (!this.abierto) this.abrir();
    return t;
  }

  activar(t) {
    this.activa = t;
    this.terminales.forEach((x) => x.raiz.classList.toggle("activa", x === t));
    this.#pintarLista();
    t?.enfocar();
  }

  matar(t) {
    if (!t) return;
    t.destruir();
    this.terminales = this.terminales.filter((x) => x !== t);
    if (this.activa === t) this.activa = this.terminales[this.terminales.length - 1] ?? null;
    if (!this.terminales.length) { this.cerrar(); return; }
    this.activar(this.activa);
  }

  #pintarLista() {
    this.lista.innerHTML = this.terminales.length < 2 ? "" : this.terminales.map((t) => `<span class="term-chip${t === this.activa ? " on" : ""}" role="tab" data-term="${t.numero}" tabindex="0">${ICONOS.terminal}<span>bash ${t.numero}</span><button type="button" class="chip-x" aria-label="Cerrar terminal ${t.numero}">${ICONOS.cerrar}</button></span>`).join("");
  }

  get hayProgramaCorriendo() { return this.terminales.some((t) => t.ocupado); }

  /** Detiene lo que esté corriendo en cualquier terminal (botón Detener). */
  detener() { this.terminales.filter((t) => t.ocupado).forEach((t) => t.interrumpir()); }

  /** Escribe y ejecuta un comando en la terminal activa (crea una si hace falta). */
  correr(linea) {
    this.abrir({ enfocar: false });
    this.mostrarPestana("terminal");
    const t = this.activa ?? this.nueva();
    return t.lanzar(linea);
  }

  // ---- consola de la vista previa ----
  escribirConsola(nivel, texto) {
    this.consolaEl.querySelector(".consola-vacia")?.remove();
    const l = document.createElement("div");
    l.className = `consola-linea nivel-${nivel}`;
    l.textContent = texto;
    this.consolaEl.appendChild(l);
    while (this.consolaEl.childElementCount > 500) this.consolaEl.firstElementChild.remove();
    this.consolaEl.scrollTop = this.consolaEl.scrollHeight;
    if (this.pestana !== "consola" || !this.abierto) this.$(".punto-aviso").hidden = false;
  }

  limpiarConsola() {
    this.consolaEl.innerHTML = '<p class="consola-vacia">Aquí aparecen los mensajes de console.log y los errores de tu vista previa.</p>';
    this.$(".punto-aviso").hidden = true;
  }
}
