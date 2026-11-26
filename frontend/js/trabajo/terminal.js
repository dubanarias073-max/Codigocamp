// Panel inferior estilo VS Code: pestañas TERMINAL y CONSOLA, varias terminales, historial, Tab, Ctrl+C...
// La lógica de comandos vive en shell.js; aquí solo hay interfaz.
import { TerminalReal } from "./terminal-real.js";
import { RenderAnsi } from "./ansi.js";
import { alCambiarServidores, detenerServidor, servidores } from "./puertos.js";
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
  /** @param {object} [shell] otro intérprete (la terminal «Mi equipo» usa ShellRemoto: comandos en tu computador o celular) */
  constructor(panel, numero, shell = null) {
    this.panel = panel;
    this.shell = shell || panel.shell;
    this.remota = Boolean(shell?.remoto);
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
    this.sesion = this.shell.nuevaSesion({
      out: (t) => this.escribir(t), err: (t) => this.escribir(t),
      limpiar: () => { this.salida.textContent = ""; this.actual = null; },
      cerrar: () => panel.matar(this),
      leerLinea: (texto, opciones) => this.pedirLinea(texto, opciones),
      cancelarLectura: () => this.cancelarLectura(),
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
    if (this.remota) this.escribir(`\x1b[35m🖥 Conectado a ${this.shell.equipo.equipo}\x1b[0m\x1b[90m · los comandos corren de verdad en tu equipo con tus permisos (empiezan en ${this.shell.equipo.carpeta || "la carpeta del Conector"}). Revisa lo que ejecutas: aquí nada se bloquea.\x1b[0m\n`);
    else this.escribir("\x1b[90mTerminal de CódigoCamp · escribe \x1b[0m\x1b[1mhelp\x1b[0m\x1b[90m para ver los comandos.\x1b[0m\n");
    this.#prompt();
  }

  get columnas() {
    const ancho = this.medida.getBoundingClientRect().width / 10;
    return ancho > 0 ? Math.max(20, Math.floor((this.salida.clientWidth || 640) / ancho)) : 80;
  }

  escribir(texto) {
    if (this.captura !== null && this.captura !== undefined && this.captura.length < 200000) this.captura += String(texto);
    // Terminal «Mi equipo»: la caja para escribir queda siempre al final, después de lo que va llegando
    const pendiente = this.remota && this.lectura && this.entrada ? this.entrada : null;
    const conFoco = pendiente && document.activeElement === pendiente;
    if (pendiente) pendiente.remove();
    const partes = String(texto).split("\n");
    partes.forEach((trozo, i) => {
      if (trozo) this.#linea().insertAdjacentHTML("beforeend", this.ansi.render(trozo));
      if (i < partes.length - 1) { this.#linea(); this.actual = null; }
    });
    if (pendiente) { this.#linea().appendChild(pendiente); if (conFoco) pendiente.focus({ preventScroll: true }); }
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
    if (this.remota) return this.shell.prompt(this.sesion);
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

  /** Cancela una lectura pendiente (el programa remoto terminó mientras esperaba lo que ibas a escribir). */
  cancelarLectura() {
    if (!this.lectura) return;
    const { resolver } = this.lectura;
    this.lectura = null;
    this.entrada?.remove();
    this.entrada = null;
    resolver(null);
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
    const { desde, opciones } = this.shell.completar(antes, this.sesion);
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
    if (this.shell.incompleta?.(completo)) {
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
    this.captura = "";   // lo que muestre el comando: de ahí salen los problemas de ejecución (⊗ y ⚠ de la barra)
    try { codigo = await this.shell.ejecutar(linea, this.sesion); }
    catch (error) { codigo = 1; this.escribir(`Error inesperado: ${error?.message || error}\n`); }
    try { this.panel.alSalida?.(this.captura, codigo, linea); } catch { /* nada */ }
    this.captura = null;
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

const TECLAS = [["Tab", "Tab", "Tab: completar"], ["ctrl-c", "Ctrl+C", "Ctrl+C: detener"], ["ArrowUp", "↑", "Comando anterior"], ["ArrowDown", "↓", "Comando siguiente"],
  ["ArrowLeft", "←", "Mover a la izquierda"], ["ArrowRight", "→", "Mover a la derecha"], ["Escape", "Esc", "Escape"], ["-", "-", "Guion"], ["/", "/", "Barra"],
  ["|", "|", "Tubería"], ["~", "~", "Carpeta personal"], ["ctrl-l", "Limpiar", "Limpiar pantalla (Ctrl+L)"]];

export class PanelInferior {
  /**
   * @param {object} o
   * @param {HTMLElement} o.raiz     contenedor del panel
   * @param {Shell} o.shell
   * @param {()=>object} o.proyecto
   * @param {Storage} [o.storage] y {string} o.claveHistorial
   * @param {(abierto:boolean)=>void} [o.alCambiar]
   */
  constructor({ raiz, shell, proyecto, claveHistorial, storage = globalThis.localStorage, alCambiar = () => {}, alOcupado = () => {}, alIA = null, alPuerto = null, alSalida = null }) {
    this.alIA = alIA;
    this.alSalida = alSalida;
    this.alPuerto = alPuerto;
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
          <button type="button" role="tab" class="panel-tab" data-tab="problemas" aria-selected="false">PROBLEMAS<span class="cuenta-problemas" hidden></span></button>
          <button type="button" role="tab" class="panel-tab on" data-tab="terminal" aria-selected="true">TERMINAL</button>
          <button type="button" role="tab" class="panel-tab" data-tab="consola" aria-selected="false">CONSOLA<span class="punto-aviso" hidden></span></button>
          <button type="button" role="tab" class="panel-tab" data-tab="puertos" aria-selected="false">PUERTOS<span class="cuenta-puertos" hidden></span></button>
        </div>
        <div class="panel-acciones">
          <span class="term-equipo" hidden><svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><rect x="1.5" y="2.5" width="13" height="8.5" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M5.5 13.5h5M8 11v2.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg><b></b></span>
          <button type="button" class="icono-btn" data-acc="nueva" title="Nueva terminal" aria-label="Nueva terminal">${ICONOS.mas}</button>
          <button type="button" class="icono-btn btn-equipo" data-acc="equipo" title="Terminal en mi computador o celular (Conector)" aria-label="Terminal en mi equipo"><svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><rect x="1.5" y="2.5" width="13" height="8.5" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M5.5 13.5h5M8 11v2.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><path d="m4.5 5.5 2 1.5-2 1.5M8 8.5h3" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg></button>
          <button type="button" class="icono-btn" data-acc="matar" title="Eliminar terminal" aria-label="Eliminar terminal">${ICONOS.basura}</button>
          <button type="button" class="icono-btn" data-acc="max" title="Maximizar panel" aria-label="Maximizar panel">${ICONOS.maximizar}</button>
          <button type="button" class="icono-btn" data-acc="cerrar" title="Cerrar panel (Ctrl+\`)" aria-label="Cerrar panel">${ICONOS.cerrar}</button>
        </div>
      </div>
      <div class="panel-cuerpo">
        <div class="term-zona" data-vista="terminal"><div class="term-contenedor"></div><div class="term-lista" role="tablist" aria-label="Terminales abiertas" hidden></div></div>
        <div class="consola" data-vista="consola" role="log" aria-label="Consola de la vista previa" hidden><p class="consola-vacia">Aquí aparecen los mensajes de console.log y los errores de tu vista previa.</p></div>
        <div class="puertos" data-vista="puertos" hidden></div>
        <div class="problemas-lista" data-vista="problemas" role="list" aria-label="Problemas del proyecto" hidden></div>
      </div>
      <div class="term-teclas" role="toolbar" aria-label="Teclas de la terminal">${TECLAS.map(([k, t, d]) => `<button type="button" data-tecla="${k}" title="${d}" aria-label="${d}">${t}</button>`).join("")}</div>`;
    this.$ = (s) => raiz.querySelector(s);
    this.contenedor = this.$(".term-contenedor");
    this.consolaEl = this.$(".consola");
    this.lista = this.$(".term-lista");
    this.puertosEl = this.$(".puertos");
    this.problemasEl = this.$(".problemas-lista");
    this.problemasEl.addEventListener("click", (e) => {
      const f = e.target.closest("[data-prob]");
      if (f) this.alIrAProblema?.(f.dataset.ruta, Number(f.dataset.linea));
      const g = e.target.closest("[data-grupo]");
      if (g && !f) g.parentElement.classList.toggle("plegado");
    });
    // Teclas que el teclado del celular no tiene (Tab, Ctrl+C, flechas…). pointerdown evita que se cierre el teclado.
    const teclas = this.$(".term-teclas");
    teclas.addEventListener("pointerdown", (e) => { if (e.target.closest("[data-tecla]")) e.preventDefault(); });
    teclas.addEventListener("click", (e) => { const b = e.target.closest("[data-tecla]"); if (b) this.tecla(b.dataset.tecla); });
    alCambiarServidores(() => this.pintarPuertos());
    this.pintarPuertos();
    raiz.addEventListener("click", (e) => {
      const tab = e.target.closest("[data-tab]");
      if (tab) return this.mostrarPestana(tab.dataset.tab);
      const sv = e.target.closest("[data-serv]");
      if (sv) return this.alServicio?.(sv.dataset);
      const pb = e.target.closest("[data-puerto-acc]");
      if (pb) return this.accionPuerto(pb.dataset.puertoAcc, Number(pb.closest("[data-puerto]").dataset.puerto));
      const acc = e.target.closest("[data-acc]")?.dataset.acc;
      if (acc === "nueva") this.nueva();
      else if (acc === "equipo") this.alEquipo?.();
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
    this.$(".term-zona").hidden = nombre !== "terminal";
    this.consolaEl.hidden = nombre !== "consola";
    this.puertosEl.hidden = nombre !== "puertos";
    this.problemasEl.hidden = nombre !== "problemas";
    if (nombre === "puertos") this.alVerPuertos?.();
    this.$(".term-equipo").hidden = nombre !== "terminal" || !this.hayEquipo;
    this.$('[data-acc="nueva"]').hidden = nombre !== "terminal";
    this.$('[data-acc="equipo"]').hidden = nombre !== "terminal";
    const borrar = this.$('[data-acc="matar"]');
    borrar.title = borrar.ariaLabel = nombre === "consola" ? "Limpiar consola" : "Eliminar terminal";
    borrar.hidden = nombre === "problemas" || nombre === "puertos";
    if (nombre === "consola") this.$(".punto-aviso").hidden = true;
    else requestAnimationFrame(() => this.activa?.enfocar());
  }

  /**
   * Panel PROBLEMAS: errores (⊗) y advertencias (⚠) de todo el proyecto, agrupados por archivo.
   * Clic en uno → abre el archivo en esa línea.
   * @param {{errores:number, advertencias:number, lista:{ruta, linea, mensaje, grave}[]}} p
   */
  pintarProblemas(p) {
    const cuenta = this.$(".cuenta-problemas");
    const n = p.errores + p.advertencias;
    cuenta.hidden = !n; cuenta.textContent = String(n);
    cuenta.classList.toggle("hay-errores", p.errores > 0);
    const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
    if (!n) { this.problemasEl.innerHTML = '<div class="problemas-vacio">✓ No se encontraron problemas en el proyecto.</div>'; return; }
    const grupos = new Map();
    for (const x of [...p.lista].sort((a, b) => a.ruta.localeCompare(b.ruta) || b.grave - a.grave || a.linea - b.linea)) {
      if (!grupos.has(x.ruta)) grupos.set(x.ruta, []);
      grupos.get(x.ruta).push(x);
    }
    this.problemasEl.innerHTML = [...grupos].map(([ruta, xs]) => `<div class="prob-grupo">
      <button type="button" class="prob-archivo" data-grupo><span class="prob-flecha">▾</span><b>${esc(ruta.split("/").pop())}</b><small>${esc(ruta)}</small><span class="prob-n">${xs.length}</span></button>
      ${xs.map((x) => `<button type="button" class="prob-fila ${x.grave ? "grave" : "advierte"}" role="listitem" data-prob data-ruta="${esc(x.ruta)}" data-linea="${x.linea}">
        <span class="prob-ic" aria-label="${x.grave ? "Error" : "Advertencia"}">${x.grave ? "⊗" : "⚠"}</span><span class="prob-msg">${esc(x.mensaje)}</span><small>[Ln ${x.linea}]</small></button>`).join("")}
    </div>`).join("");
  }

  /** Panel PUERTOS (como VS Code): cada servidor encendido, con su dirección, quién lo corre y acciones. */
  /** Servicios del computador o celular conectado (XAMPP, MySQL, MongoDB…), arriba de los puertos de CódigoCamp. */
  ponerServiciosEquipo(html) { this.htmlEquipo = html; this.pintarPuertos(); }

  pintarPuertos() {
    const lista = [...servidores.values()].sort((a, b) => a.puerto - b.puerto);
    const cuenta = this.$(".cuenta-puertos");
    cuenta.hidden = !lista.length; cuenta.textContent = String(lista.length);
    const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const origen = (x) => (x.framework === "Expo" ? "Expo Snack" : x.externo ? "Docker (servidor)" : x.framework === "PHP" ? "Servidor de CódigoCamp" : "Navegador");
    const equipo = this.htmlEquipo || "";
    if (!lista.length) {
      this.puertosEl.innerHTML = `${equipo}<div class="puertos-vacio"><b>No hay puertos abiertos</b><p>Enciende un servidor en la terminal y aparece aquí:</p>
        <ul><li><code>node server.js</code> · <code>nodemon app.js</code> · <code>npm run dev</code> (Express, Vite)</li><li><code>fastapi dev main.py</code> · <code>flask --app app run</code> · <code>python manage.py runserver</code></li>
        <li><code>php -S localhost:8000</code> · <code>python -m http.server</code> · <code>npx serve</code> · <code>live-server</code></li><li><code>npx expo start</code> (web y celular) · <code>next dev</code>, <code>ng serve</code>, <code>php artisan serve</code> (con Docker)</li></ul></div>`;
      return;
    }
    this.puertosEl.innerHTML = `${equipo}<table class="puertos-tabla"><thead><tr><th>Puerto</th><th>Dirección local</th><th>Proceso</th><th>Origen</th><th></th></tr></thead><tbody>${lista.map((x) => `
      <tr data-puerto="${x.puerto}"><td><span class="puerto-punto"></span>${x.puerto}</td>
      <td><button type="button" class="puerto-url" data-puerto-acc="vista" title="Abrir en la vista previa">localhost:${x.puerto}</button></td>
      <td title="${esc(x.comando || x.framework)}"><b>${esc(x.framework || "")}</b> <span class="puerto-cmd">${esc(x.comando && x.comando !== x.framework ? x.comando : "")}</span></td>
      <td>${esc(origen(x))}</td>
      <td class="puerto-acc"><span class="puerto-botones"><button type="button" class="icono-btn" data-puerto-acc="vista" title="Abrir en la vista previa">🌐</button>
        <button type="button" class="icono-btn" data-puerto-acc="pestana" title="${x.externo ? "Abrir en el navegador" : "Abrir en una pestaña del editor"}">↗</button>
        ${x.celular ? '<button type="button" class="icono-btn" data-puerto-acc="celular" title="Abrir en el celular (Expo Go)">📱</button>' : ""}
        <button type="button" class="icono-btn" data-puerto-acc="copiar" title="Copiar la dirección">📋</button>
        <button type="button" class="icono-btn" data-puerto-acc="detener" title="Detener el servidor">⏹</button></span></td></tr>`).join("")}</tbody></table>`;
  }

  accionPuerto(acc, puerto) {
    const x = servidores.get(puerto);
    if (!x) return;
    if (acc === "detener") { detenerServidor(puerto); return; }
    if (acc === "copiar") { navigator.clipboard?.writeText(x.externo && !x.celular ? x.externo : `http://localhost:${puerto}`).catch(() => {}); return; }
    if (acc === "celular") { window.open(x.celular, "_blank", "noopener"); return; }
    this.alPuerto?.(acc, x);
  }

  /** @param {object} [shell] ShellRemoto para una terminal «Mi equipo» */
  nueva(shell = null) {
    // Con un equipo conectado, toda terminal nueva (+, Ctrl+Ñ, ▶…) es de ese equipo; sin equipo, la de CódigoCamp
    if (shell === null && this.porDefecto) shell = this.porDefecto();
    this.contador += 1;
    const t = shell?.real ? new TerminalReal(this, this.contador, shell) : new Terminal(this, this.contador, shell);
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

  /** Nombre de la pestaña, como en VS Code: «bash 1», «PowerShell 2» (con el equipo al pasar el mouse). */
  #nombre(t) {
    const mismos = this.terminales.filter((x) => Boolean(x.remota) === Boolean(t.remota) && (!t.remota || x.shell.equipo.id === t.shell.equipo.id));
    const n = mismos.indexOf(t) + 1;
    const so = t.remota ? t.shell.equipo.sistema || "" : "";
    const base = !t.remota ? "bash" : /windows/i.test(so) ? (t.real ? "PowerShell" : "cmd") : /android/i.test(so) ? "Termux" : /mac/i.test(so) ? "zsh" : "bash";
    return mismos.length > 1 ? `${base} ${n}` : base;
  }

  #pintarLista() {
    const esc = (x) => String(x).replace(/[<&"]/g, (c) => ({ "<": "&lt;", "&": "&amp;", '"': "&quot;" }[c]));
    const equipo = this.terminales.find((t) => t.remota)?.shell.equipo;
    this.raiz.classList.toggle("con-equipo-term", Boolean(equipo));
    const titulo = this.$(".term-equipo");
    this.hayEquipo = Boolean(equipo);
    titulo.hidden = !equipo || (this.pestana && this.pestana !== "terminal");
    if (equipo) { titulo.querySelector("b").textContent = equipo.equipo; titulo.title = `Terminales de ${equipo.equipo}${equipo.carpeta ? ` · ${equipo.carpeta}` : ""}`; }
    this.lista.hidden = this.terminales.length < 2;
    this.lista.innerHTML = this.terminales.length < 2 ? "" : this.terminales.map((t) => {
      const nombre = this.#nombre(t);
      const ayuda = t.remota ? `${nombre} en ${t.shell.equipo.equipo}${t.real ? "" : " (terminal simple: actualiza el Conector para la completa)"}` : `${nombre} de CódigoCamp`;
      return `<span class="term-chip${t === this.activa ? " on" : ""}${t.remota ? " de-equipo" : ""}" role="tab" aria-selected="${t === this.activa}" data-term="${t.numero}" tabindex="0" title="${esc(ayuda)}">${ICONOS.terminal}<span class="term-chip-nombre">${esc(nombre)}</span>${t.remota && !t.real ? '<i class="term-chip-simple">simple</i>' : ""}<button type="button" class="chip-x" aria-label="Cerrar ${esc(nombre)}">${ICONOS.cerrar}</button></span>`;
    }).join("");
    this.lista.querySelector(".term-chip.on")?.scrollIntoView?.({ block: "nearest", inline: "nearest" });
  }

  get hayProgramaCorriendo() { return this.terminales.some((t) => t.ocupado); }

  /** Detiene lo que esté corriendo en cualquier terminal (botón Detener). */
  detener() { this.terminales.filter((t) => t.ocupado).forEach((t) => t.interrumpir()); }

  /** Pulsa una tecla especial en la terminal activa (barra de teclas del celular). */
  tecla(k) {
    if (this.pestana !== "terminal") this.mostrarPestana("terminal");
    const t = this.activa ?? this.nueva();
    if (t.real) { t.tecla(k); return; }
    const input = t.entrada;
    const pulsar = (el, key, ctrlKey = false) => el.dispatchEvent(new KeyboardEvent("keydown", { key, ctrlKey, bubbles: true, cancelable: true }));
    if (k === "ctrl-c") { if (input) pulsar(input, "c", true); else pulsar(t.raiz, "c", true); return; }
    if (!input) return;
    input.focus({ preventScroll: true });
    if (/^ctrl-[a-z]$/.test(k)) pulsar(input, k.slice(5), true);
    else if (["Tab", "ArrowUp", "ArrowDown", "Escape", "Enter"].includes(k)) pulsar(input, k);
    else if (k === "Backspace") {
      const a = input.selectionStart ?? input.value.length, b = input.selectionEnd ?? a;
      if (a === b && a > 0) input.setRangeText("", a - 1, a, "end"); else if (a !== b) input.setRangeText("", a, b, "end");
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
    else if (k === "ArrowLeft" || k === "ArrowRight") {
      const p = Math.max(0, Math.min(input.value.length, input.selectionStart + (k === "ArrowLeft" ? -1 : 1)));
      input.setSelectionRange(p, p);
    } else {
      const a = input.selectionStart ?? input.value.length;
      input.setRangeText(k, a, input.selectionEnd ?? a, "end");
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }

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
