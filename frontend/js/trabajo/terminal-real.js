// Terminal REAL de tu computador o celular dentro de Trabajo (como la terminal integrada de VS Code).
// Usa xterm.js (el mismo motor de terminal que VS Code) y una pseudo-terminal en tu equipo (el Conector):
// la shell es la tuya (PowerShell, bash, zsh…), con colores, Tab para completar, historial con ↑, Ctrl+C,
// editores como nano o vim, htop, Python o Node interactivos, git, npm, mkdir, rm… todo de verdad.
import { api } from "/js/app.js";

const VENDOR = "/vendor/xterm";
let cargando = null;
function cargarXterm() {
  if (globalThis.Terminal && globalThis.FitAddon) return Promise.resolve();
  if (cargando) return cargando;
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = `${VENDOR}/xterm.css`;
  document.head.append(css);
  const script = (src) => new Promise((ok, mal) => {
    // Monaco trae un cargador AMD (define): se esconde mientras carga para que xterm quede en window
    const amd = globalThis.define;
    globalThis.define = undefined;
    const s = document.createElement("script");
    s.src = src;
    s.onload = () => { globalThis.define = amd; ok(); };
    s.onerror = () => { globalThis.define = amd; mal(new Error("No se pudo cargar la terminal.")); };
    document.head.append(s);
  });
  cargando = script(`${VENDOR}/xterm.js`).then(() => script(`${VENDOR}/addon-fit.js`)).catch((e) => { cargando = null; throw e; });
  return cargando;
}

const TECLAS = { Tab: "\t", ArrowUp: "\x1b[A", ArrowDown: "\x1b[B", ArrowRight: "\x1b[C", ArrowLeft: "\x1b[D", Escape: "\x1b", "ctrl-c": "\x03", "ctrl-l": "\x0c" };

export class TerminalReal {
  /**
   * @param {object} panel    TerminalPanel
   * @param {number} numero
   * @param {{ real: true, equipo: object, cwd?: string, alFallar?: (t, motivo) => void }} shell
   */
  constructor(panel, numero, shell) {
    Object.assign(this, { panel, numero, shell });
    this.remota = true;
    this.real = true;
    this.ocupado = false;
    this.entrada = null;
    this.sesion = { cwd: shell.cwd || "" };
    this.raiz = document.createElement("div");
    this.raiz.className = "term term-real";
    this.raiz.setAttribute("role", "region");
    this.raiz.setAttribute("aria-label", `Terminal de ${shell.equipo.equipo}`);
    this.pendiente = "";
    this.enviando = Promise.resolve();
    this.cerrada = false;
    this.listo = this.#iniciar().catch((e) => this.#fallo(e.message, { actualizar: Boolean(e.datos?.actualizar) }));
  }

  async #iniciar() {
    await cargarXterm();
    const estilo = getComputedStyle(this.panel.raiz);
    const fondo = estilo.getPropertyValue("--term-fondo").trim() || "#0b1220";
    this.term = new globalThis.Terminal({
      fontFamily: "'Cascadia Code', 'Fira Code', Consolas, 'Courier New', monospace", fontSize: matchMedia("(max-width: 760px)").matches ? 13 : 14,
      cursorBlink: true, scrollback: 8000, allowProposedApi: true, convertEol: false, macOptionIsMeta: true,
      theme: { background: fondo, foreground: "#e2e8f0", cursor: "#4ade80", selectionBackground: "rgba(74,222,128,.35)",
        black: "#1e293b", red: "#f87171", green: "#4ade80", yellow: "#facc15", blue: "#60a5fa", magenta: "#c084fc", cyan: "#22d3ee", white: "#e2e8f0",
        brightBlack: "#64748b", brightRed: "#fca5a5", brightGreen: "#86efac", brightYellow: "#fde68a", brightBlue: "#93c5fd", brightMagenta: "#d8b4fe", brightCyan: "#67e8f9", brightWhite: "#ffffff" },
    });
    this.ajuste = new globalThis.FitAddon.FitAddon();
    this.term.loadAddon(this.ajuste);
    this.term.open(this.raiz);
    // Ctrl+C con texto seleccionado copia (como VS Code); sin selección, interrumpe el programa
    this.term.attachCustomKeyEventHandler((e) => {
      if (e.type === "keydown" && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "c" && this.term.hasSelection()) {
        navigator.clipboard?.writeText(this.term.getSelection()).catch(() => {});
        return false;
      }
      if (e.type === "keydown" && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "v") return true;   // el navegador pega
      return true;
    });
    this.raiz.addEventListener("contextmenu", (e) => {   // clic derecho: copia lo seleccionado o pega (como Windows Terminal)
      e.preventDefault();
      if (this.term.hasSelection()) { navigator.clipboard?.writeText(this.term.getSelection()); this.term.clearSelection(); }
      else navigator.clipboard?.readText().then((t) => t && this.escribir(t)).catch(() => {});
    });
    this.#ajustar();
    new ResizeObserver(() => this.#ajustar()).observe(this.raiz);
    const eq = this.shell.equipo;
    this.term.write(`\x1b[90mConectando con la terminal de ${eq.equipo}…\x1b[0m\r\n`);
    const r = await api(`/api/conector/${eq.id}/terminal`, { cols: this.term.cols, rows: this.term.rows, cwd: this.sesion.cwd });
    this.orden = r.orden;
    this.term.onData((d) => this.escribir(d));
    this.term.onResize(({ cols, rows }) => { if (this.orden && !this.cerrada) this.#mandar("tam", { cols, rows }); });
    // Un Conector viejo no entiende «terminal completa» y no contesta nada: a los 12 s se usa la terminal simple
    this.sinRespuesta = setTimeout(() => {
      if (this.cerrada || this.respondio) return;
      api(`/api/conector/orden/${this.orden}/detener`, {}).catch(() => {});
      this.#fallo(`${eq.equipo} no respondió a la terminal completa (¿Conector desactualizado?)`, { actualizar: true });
    }, 12000);
    this.pos = 0;
    this.primera = true;
    if (!(await this.#abrirCanal())) void this.#leer();   // sin WebSocket: la salida llega por consultas HTTP
  }

  /** Canal WebSocket con el servidor: lo que escribes va y la salida vuelve al instante (una sola conexión).
   *  Si no se puede abrir (servidor sin flask-sock, proxy…), false y se usa HTTP. */
  #abrirCanal() {
    if (typeof WebSocket !== "function" || this.sinCanal) return Promise.resolve(false);
    return new Promise((ok) => {
      let abierto = false, listo = false;
      const fin = (v) => { if (!listo) { listo = true; clearTimeout(espera); ok(v); } };
      let ws;
      try { ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/conector/orden/${this.orden}/ws?desde=${this.pos}`); }
      catch { fin(false); return; }
      const espera = setTimeout(() => { try { ws.close(); } catch { /* nada */ } fin(false); }, 4000);
      ws.onopen = () => { abierto = true; this.canal = ws; fin(true); };
      ws.onmessage = (e) => { let r; try { r = JSON.parse(e.data); } catch { return; } this.#recibir(r); };
      ws.onclose = () => {
        if (this.canal === ws) this.canal = null;
        if (!abierto) { this.sinCanal = true; fin(false); return; }
        if (!this.cerrada) void this.#leer();   // se cortó el canal: se sigue por HTTP desde donde iba
      };
      ws.onerror = () => { if (!abierto) { this.sinCanal = true; fin(false); } };
    });
  }

  /** Manda teclas, tamaño o detener: por el canal si está abierto, si no por HTTP (en orden). */
  #mandar(accion, datos = {}) {
    if (this.canal?.readyState === 1) { this.canal.send(JSON.stringify({ a: accion, ...datos })); return; }
    this.enviando = this.enviando.then(() => api(`/api/conector/orden/${this.orden}/${accion}`, datos)).catch(() => {});
  }

  /** Lo que llega de tu equipo (por el canal o por HTTP). */
  #recibir(r) {
    if (r.error && !r.texto) { this.term.write(`\r\n\x1b[31m${r.error}\x1b[0m\r\n`); this.cerrada = true; return; }
    if (this.primera && r.texto) { this.term.write("\x1b[2K\r"); this.primera = false; this.respondio = true; clearTimeout(this.sinRespuesta); }
    if (r.texto) this.term.write(r.texto);
    if (typeof r.desde === "number") this.pos = r.desde;
    if (r.texto && this.panel.alSalidaReal) { clearTimeout(this.trasSalida); this.trasSalida = setTimeout(() => this.panel.alSalidaReal?.(this), 450); }
    if (r.fin) {
      this.cerrada = true;
      try { this.canal?.close(); } catch { /* nada */ }
      if (r.datos?.sin_pty) { this.#fallo(String(r.texto || "").trim().replace(/^No se pudo abrir la terminal real:\s*/, "")); return; }
      this.term.write("\r\n\x1b[90mPulsa + para abrir otra terminal.\x1b[0m\r\n");
    }
  }

  #ajustar() {
    if (!this.term || !this.raiz.isConnected || this.raiz.offsetParent === null) return;
    try { this.ajuste.fit(); } catch { /* aún sin tamaño */ }
  }

  async #leer() {
    if (this.leyendo) return;
    this.leyendo = true;
    try {
      while (!this.cerrada && !this.canal) {
        let r;
        try { r = await api(`/api/conector/orden/${this.orden}?desde=${this.pos}`); }
        catch (e) { this.term.write(`\r\n\x1b[31m${e.message}\x1b[0m\r\n`); this.cerrada = true; break; }
        this.#recibir(r);
      }
    } finally { this.leyendo = false; }
  }

  #fallo(motivo, extra = {}) {
    if (this.fallo) return;
    this.fallo = true;
    this.cerrada = true;
    clearTimeout(this.sinRespuesta);
    if (this.shell.alFallar) { this.shell.alFallar(this, motivo, extra); return; }
    if (this.term) this.term.write(`\r\n\x1b[31m${motivo}\x1b[0m\r\n`);
    else this.raiz.textContent = motivo;
  }

  /** Lo que escribes va a tu equipo tal cual (se juntan las teclas muy seguidas y se mandan en orden). */
  escribir(texto) {
    if (this.cerrada || !this.orden) return;
    this.pendiente += texto;
    if (this.programado) return;
    this.programado = true;
    setTimeout(() => {
      this.programado = false;
      const t = this.pendiente;
      this.pendiente = "";
      if (!t) return;
      if (/[\r\n]/.test(t)) { clearTimeout(this.trasEnter); this.trasEnter = setTimeout(() => this.panel.alComandoReal?.(this), 600); }
      this.#mandar("entrada", { texto: t });
    }, this.canal ? 0 : 12);
  }

  enfocar() { requestAnimationFrame(() => { this.#ajustar(); this.term?.focus(); }); }
  /** Ejecuta una línea (▶ Ejecutar, Git, servicios…) como si la escribieras y pulsaras Enter. */
  async lanzar(linea) { await this.listo; this.escribir(`${linea}\r`); }
  interrumpir() { this.escribir("\x03"); }
  tecla(k) { this.escribir(TECLAS[k] ?? k); this.term?.focus(); }
  destruir() {
    this.cerrada = true;
    clearTimeout(this.sinRespuesta);
    if (this.orden) api(`/api/conector/orden/${this.orden}/detener`, {}).catch(() => {});
    try { this.canal?.close(); } catch { /* nada */ }
    clearTimeout(this.trasSalida);
    this.term?.dispose();
    this.raiz.remove();
  }
}
