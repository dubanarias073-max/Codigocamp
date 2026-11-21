// Editor de código de Trabajo. Un <textarea> real (con deshacer/rehacer nativo, selección, IME, móvil...)
// y, justo debajo, una capa <pre> con el mismo texto coloreado. Cada archivo abierto tiene su propia instancia,
// así el historial de deshacer no se mezcla entre archivos.
import { extension } from "./fs.js";
import { infoLenguaje, resaltar } from "./resaltado.js";
import { fragmentoAPlano, sugerir } from "./autocompletar.js";

const PARES = { "(": ")", "[": "]", "{": "}", '"': '"', "'": "'", "`": "`" };
const CIERRES = new Set([")", "]", "}", '"', "'", "`"]);
const SIN_PARES = new Set(["txt", "md", "env", "gitignore", "csv", ""]);
const COMENTARIO = {
  js: ["//"], mjs: ["//"], cjs: ["//"], jsx: ["//"], ts: ["//"], tsx: ["//"], java: ["//"], c: ["//"], h: ["//"], cpp: ["//"], cc: ["//"], cs: ["//"],
  go: ["//"], rs: ["//"], swift: ["//"], kt: ["//"], php: ["//"], py: ["#"], rb: ["#"], sh: ["#"], yml: ["#"], yaml: ["#"], toml: ["#"], sql: ["--"], env: ["#"],
  css: ["/*", "*/"], scss: ["/*", "*/"], html: ["<!--", "-->"], htm: ["<!--", "-->"], md: ["<!--", "-->"], svg: ["<!--", "-->"], xml: ["<!--", "-->"],
};

export const unidadDeIndentacion = (ext) => (ext === "go" ? "\t" : ["py", "java", "c", "cpp", "cc", "h", "cs", "php", "rs", "kt", "swift", "sql"].includes(ext) ? "    " : "  ");

/** Inserta texto conservando el historial de deshacer del navegador. */
function insertar(ta, texto) {
  ta.focus();
  if (!document.execCommand("insertText", false, texto)) {
    ta.setRangeText(texto, ta.selectionStart, ta.selectionEnd, "end");
    ta.dispatchEvent(new Event("input", { bubbles: true }));
  }
}
function reemplazar(ta, desde, hasta, texto) {
  ta.setSelectionRange(desde, hasta);
  insertar(ta, texto);
}

export class Editor {
  /**
   * @param {object} o
   * @param {string} o.ruta @param {string} o.texto
   * @param {(texto:string)=>void} o.alCambiar  se llama en cada edición de la persona
   * @param {(pos:{linea:number,col:number,seleccion:number})=>void} o.alCursor
   * @param {(accion:string)=>void} o.alAtajo   "guardar" | "ejecutar"
   */
  constructor({ ruta, texto, alCambiar, alCursor, alAtajo, archivos = () => ({}) }) {
    Object.assign(this, { alCambiar, alCursor, alAtajo, archivos });
    this.sug = null;
    this.ruta = ruta;
    this.ext = extension(ruta);
    this.lineas = 0;
    this.vista = { top: 0, left: 0, a: 0, b: 0 };
    this.raiz = document.createElement("div");
    this.raiz.className = "ed";
    this.raiz.hidden = true;
    this.raiz.innerHTML = `
      <div class="ed-gutter" aria-hidden="true"><div class="ed-numeros"></div><div class="ed-num-activo"></div></div>
      <div class="ed-area">
        <div class="ed-linea-activa"></div>
        <pre class="ed-hl" aria-hidden="true"><code></code></pre>
        <textarea class="ed-ta" spellcheck="false" wrap="off" autocapitalize="off" autocomplete="off" autocorrect="off"></textarea>
        <ul class="ed-sug" role="listbox" aria-label="Sugerencias" hidden></ul>
      </div>`;
    this.$ = (s) => this.raiz.querySelector(s);
    this.ta = this.$(".ed-ta");
    this.codigo = this.$(".ed-hl code");
    this.hl = this.$(".ed-hl");
    this.numeros = this.$(".ed-numeros");
    this.numActivo = this.$(".ed-num-activo");
    this.lineaActiva = this.$(".ed-linea-activa");
    this.ta.setAttribute("aria-label", `Editor de ${ruta}`);
    this.ta.value = texto;
    this.menu = this.$(".ed-sug");
    this.ta.addEventListener("input", (e) => { this.#pintar(); this.alCambiar(this.ta.value); this.#cursor(); this.#trasEscribir(e); });
    this.ta.addEventListener("keydown", (e) => { if (!this.#teclaSugerencias(e)) this.#tecla(e); });
    // Teclados de celular que no mandan la tecla Enter: llega como «insertLineBreak».
    this.ta.addEventListener("beforeinput", (e) => { if (this.sug && (e.inputType === "insertLineBreak" || e.inputType === "insertParagraph")) { e.preventDefault(); this.#aceptar(this.sug.sel); } });
    this.ta.addEventListener("scroll", () => { this.#sincronizar(); this.#cerrarSugerencias(); });
    this.ta.addEventListener("blur", () => setTimeout(() => { if (document.activeElement !== this.ta) this.#cerrarSugerencias(); }, 120));
    this.ta.addEventListener("pointerdown", () => this.#cerrarSugerencias());
    // Tocar una sugerencia la inserta (sin quitar el foco del editor, para que no se cierre el teclado del celular).
    this.menu.addEventListener("pointerdown", (e) => e.preventDefault());
    this.menu.addEventListener("click", (e) => { const li = e.target.closest("[data-i]"); if (li) this.#aceptar(Number(li.dataset.i)); });
    this.ta.addEventListener("focus", () => this.#cursor());
    this.alSeleccion = () => { if (document.activeElement === this.ta) this.#cursor(); };
    document.addEventListener("selectionchange", this.alSeleccion);
    this.ro = new ResizeObserver(() => this.#sincronizar());
    this.ro.observe(this.ta);
    this.#pintar();
  }

  leer() { return this.ta.value; }

  /** Cambio que viene de fuera (terminal, otra pestaña...). Pierde el historial de deshacer de este archivo. */
  establecer(texto) {
    if (texto === this.ta.value) return;
    const { selectionStart: a, selectionEnd: b } = this.ta;
    this.ta.value = texto;
    this.ta.setSelectionRange(Math.min(a, texto.length), Math.min(b, texto.length));
    this.#pintar();
    this.#cursor();
  }

  renombrar(ruta) {
    this.ruta = ruta;
    const ext = extension(ruta);
    this.ta.setAttribute("aria-label", `Editor de ${ruta}`);
    if (ext !== this.ext) { this.ext = ext; this.#pintar(); }
  }

  get lenguaje() { return infoLenguaje(this.ext).nombre; }

  mostrar() {
    this.raiz.hidden = false;
    this.ta.scrollTop = this.vista.top;
    this.ta.scrollLeft = this.vista.left;
    this.ta.setSelectionRange(this.vista.a, this.vista.b);
    this.#sincronizar();
    this.#cursor();
  }

  ocultar() {
    this.vista = { top: this.ta.scrollTop, left: this.ta.scrollLeft, a: this.ta.selectionStart, b: this.ta.selectionEnd };
    this.raiz.hidden = true;
  }

  enfocar() { this.ta.focus({ preventScroll: true }); }

  irALinea(linea) {
    const v = this.ta.value;
    let pos = 0;
    for (let i = 1; i < linea; i += 1) { const n = v.indexOf("\n", pos); if (n < 0) break; pos = n + 1; }
    this.ta.setSelectionRange(pos, pos);
    this.enfocar();
  }

  // ---- sugerencias (autocompletado) ----
  #trasEscribir(e) {
    if (this.insertando) return;
    const escribio = e.inputType === "insertText" || e.inputType === "insertCompositionText";
    const borro = e.inputType?.startsWith("delete");
    if ((escribio && /[\w.$!#>*]$/.test(e.data ?? "")) || (borro && this.sug)) this.#sugerir();
    else this.#cerrarSugerencias();
  }

  #sugerir() {
    const { value: v, selectionStart: a, selectionEnd: b } = this.ta;
    if (a !== b) { this.#cerrarSugerencias(); return; }
    const inicio = v.lastIndexOf("\n", a - 1) + 1;
    let archivos = [];
    try { archivos = Object.entries(this.archivos() ?? {}); } catch { /* sin proyecto */ }
    const { prefijo, items } = sugerir({ ext: this.ext, linea: v.slice(inicio, a), documento: v.length > 600_000 ? "" : v, ruta: this.ruta, archivos });
    if (!items.length) { this.#cerrarSugerencias(); return; }
    this.sug = { items: items.slice(0, 60), sel: 0, prefijo };
    const ICONO = { kw: "🔑", fn: "ƒ", metodo: "ƒ", var: "𝑥", clase: "◆", mod: "📦", snip: "⧉", emmet: "⧉", prop: "•", palabra: "abc", tabla: "▦", columna: "▤", tipo: "T" };
    this.menu.innerHTML = this.sug.items.map((x, i) => `<li role="option" data-i="${i}" class="t-${x.tipo}"><i>${ICONO[x.tipo] ?? "•"}</i><b></b><small></small></li>`).join("");
    this.menu.querySelectorAll("li").forEach((li, i) => {
      li.querySelector("b").textContent = this.sug.items[i].etiqueta;
      li.querySelector("small").textContent = this.sug.items[i].detalle ?? "";
    });
    this.menu.hidden = false;
    this.#marcar();
    this.#ubicarMenu(inicio, a);
  }

  #ubicarMenu(inicio, a) {
    const cs = getComputedStyle(this.ta);
    const alto = parseFloat(getComputedStyle(this.raiz).getPropertyValue("--ed-lh")) || 21;
    this.ctx ??= document.createElement("canvas").getContext("2d");
    this.ctx.font = `${cs.fontSize} ${cs.fontFamily}`;
    const ancho = this.ctx.measureText("M").width || 8.4;
    const tab = Number(cs.tabSize) || 4;
    let col = 0;
    for (const ch of this.ta.value.slice(inicio, a - this.sug.prefijo)) col = ch === "\t" ? col + tab - (col % tab) : col + 1;
    const linea = this.ta.value.slice(0, a).split("\n").length;
    const area = this.ta.getBoundingClientRect();
    let x = parseFloat(cs.paddingLeft) + col * ancho - this.ta.scrollLeft;
    let y = parseFloat(cs.paddingTop) + linea * alto - this.ta.scrollTop + 2;
    const w = Math.min(340, area.width - 8);
    x = Math.max(4, Math.min(x - 26, area.width - w - 4));
    const h = this.menu.offsetHeight || 200;
    if (y + h > area.height && y - alto - h > 0) y = y - alto - h - 4;
    Object.assign(this.menu.style, { left: `${x}px`, top: `${y}px`, width: `${w}px` });
  }

  #marcar() {
    this.menu.querySelectorAll("li").forEach((li, i) => { li.classList.toggle("on", i === this.sug.sel); li.setAttribute("aria-selected", String(i === this.sug.sel)); });
    this.menu.querySelector("li.on")?.scrollIntoView({ block: "nearest" });
  }

  #cerrarSugerencias() {
    if (!this.sug) return;
    this.sug = null;
    this.menu.hidden = true;
    this.menu.replaceChildren();
  }

  /** Teclas con la lista abierta: ↑ ↓ eligen, Enter o Tab insertan, Esc cierra. Devuelve true si la usó. */
  #teclaSugerencias(e) {
    if (!this.sug || e.altKey || e.ctrlKey || e.metaKey) return false;
    const n = this.sug.items.length;
    if (e.key === "ArrowDown") { this.sug.sel = (this.sug.sel + 1) % n; this.#marcar(); }
    else if (e.key === "ArrowUp") { this.sug.sel = (this.sug.sel - 1 + n) % n; this.#marcar(); }
    else if (e.key === "Enter" || e.key === "Tab") this.#aceptar(this.sug.sel);
    else if (e.key === "Escape") this.#cerrarSugerencias();
    else return false;
    e.preventDefault();
    return true;
  }

  #aceptar(i) {
    const it = this.sug?.items[i];
    if (!it) return;
    const { prefijo } = this.sug;
    this.#cerrarSugerencias();
    const { value: v, selectionStart: a } = this.ta;
    const inicio = v.lastIndexOf("\n", a - 1) + 1;
    const sangria = /^[ \t]*/.exec(v.slice(inicio, a))[0];
    const desde = a - prefijo;
    this.insertando = true;
    try {
      if (it.snippet) {
        const f = fragmentoAPlano(it.insertar, unidadDeIndentacion(this.ext), sangria);
        reemplazar(this.ta, desde, a, f.texto);
        this.ta.setSelectionRange(desde + f.desde, desde + f.hasta);
      } else reemplazar(this.ta, desde, a, it.insertar);
    } finally { this.insertando = false; }
    this.#cursor();
  }

  destruir() {
    document.removeEventListener("selectionchange", this.alSeleccion);
    this.ro.disconnect();
    this.raiz.remove();
  }

  // ---- dibujo ----
  #pintar() {
    const texto = this.ta.value;
    this.codigo.innerHTML = `${resaltar(texto, this.ext)}\n `;
    let n = 1;
    for (let i = texto.indexOf("\n"); i !== -1; i = texto.indexOf("\n", i + 1)) n += 1;
    if (n !== this.lineas) {
      this.lineas = n;
      let s = "";
      for (let i = 1; i <= n; i += 1) s += `${i}\n`;
      this.numeros.textContent = s.slice(0, -1);
      this.raiz.style.setProperty("--digitos", String(Math.max(3, String(n).length)));
    }
    this.#sincronizar();
  }

  #sincronizar() {
    const { scrollTop, scrollLeft } = this.ta;
    this.hl.scrollTop = scrollTop;
    this.hl.scrollLeft = scrollLeft;
    this.numeros.style.transform = `translateY(${-scrollTop}px)`;
    this.#posicionarLineaActiva();
  }

  #posicion() {
    const { value, selectionStart, selectionEnd } = this.ta;
    let linea = 1;
    let inicio = 0;
    for (let i = value.indexOf("\n"); i !== -1 && i < selectionStart; i = value.indexOf("\n", i + 1)) { linea += 1; inicio = i + 1; }
    return { linea, col: selectionStart - inicio + 1, seleccion: selectionEnd - selectionStart };
  }

  #posicionarLineaActiva() {
    const { linea, seleccion } = this.#posicion();
    const alto = parseFloat(getComputedStyle(this.raiz).getPropertyValue("--ed-lh")) || 21;
    const pad = parseFloat(getComputedStyle(this.raiz).getPropertyValue("--ed-pad")) || 8;
    const y = pad + (linea - 1) * alto - this.ta.scrollTop;
    this.lineaActiva.style.transform = `translateY(${y}px)`;
    this.lineaActiva.hidden = seleccion > 0;
    this.numActivo.style.transform = `translateY(${y}px)`;
    this.numActivo.textContent = String(linea);
  }

  #cursor() {
    this.#posicionarLineaActiva();
    this.alCursor(this.#posicion());
  }

  // ---- teclado ----
  #tecla(e) {
    const ta = this.ta;
    const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key.toLowerCase() === "s") { e.preventDefault(); this.alAtajo("guardar"); return; }
    if ((ctrl && e.key === "Enter") || e.key === "F5") { e.preventDefault(); this.alAtajo("ejecutar"); return; }
    if (ctrl && e.key === "/") { e.preventDefault(); this.#comentar(); return; }
    if (e.altKey || (ctrl && e.key !== "/")) return;
    const unidad = unidadDeIndentacion(this.ext);
    const { value: v, selectionStart: a, selectionEnd: b } = ta;

    if (e.key === "Tab") {
      e.preventDefault();
      if (e.shiftKey || v.slice(a, b).includes("\n")) this.#indentarLineas(e.shiftKey ? -1 : 1, unidad);
      else insertar(ta, unidad);
      return;
    }
    if (e.key === "Enter") {
      e.preventDefault();
      const inicioLinea = v.lastIndexOf("\n", a - 1) + 1;
      const linea = v.slice(inicioLinea, a);
      const sangria = /^[ \t]*/.exec(linea)[0];
      const antes = v[a - 1];
      const despues = v[b];
      const abreBloque = /[{(\[]\s*$/.test(linea) || (this.ext === "py" && /:\s*$/.test(linea));
      const entreLlaves = a === b && PARES[antes] === despues && "{([".includes(antes);
      const entreEtiquetas = a === b && ["html", "htm", "vue", "svg", "xml"].includes(this.ext) && /<[A-Za-z][^<>]*>$/.test(linea) && v.startsWith("</", b);
      if (entreLlaves || entreEtiquetas) {
        insertar(ta, `\n${sangria}${unidad}\n${sangria}`);
        const p = a + 1 + sangria.length + unidad.length;
        ta.setSelectionRange(p, p);
      } else insertar(ta, `\n${sangria}${abreBloque ? unidad : ""}`);
      return;
    }
    if (e.key === "Backspace" && a === b && a > 0 && PARES[v[a - 1]] === v[a] && !SIN_PARES.has(this.ext)) {
      e.preventDefault();
      reemplazar(ta, a - 1, a + 1, "");
      return;
    }
    if (SIN_PARES.has(this.ext) || e.key.length !== 1) return;
    const c = e.key;
    if (c in PARES) {
      if (a !== b) { e.preventDefault(); const sel = v.slice(a, b); insertar(ta, c + sel + PARES[c]); ta.setSelectionRange(a + 1, a + 1 + sel.length); return; }
      const previo = v[a - 1] ?? "";
      const siguiente = v[a] ?? "";
      const esComilla = c === '"' || c === "'" || c === "`";
      if (esComilla && siguiente === c) { e.preventDefault(); ta.setSelectionRange(a + 1, a + 1); return; }
      const podemos = esComilla ? !/[\w]/.test(previo) && !/[\w]/.test(siguiente) : siguiente === "" || /[\s)\]}>,;]/.test(siguiente);
      if (podemos) { e.preventDefault(); insertar(ta, c + PARES[c]); ta.setSelectionRange(a + 1, a + 1); }
      return;
    }
    if (CIERRES.has(c) && a === b && v[a] === c) { e.preventDefault(); ta.setSelectionRange(a + 1, a + 1); }
  }

  #bloqueDeLineas() {
    const { value: v, selectionStart: a, selectionEnd: b } = this.ta;
    const inicio = v.lastIndexOf("\n", a - 1) + 1;
    let fin = b > a && v[b - 1] === "\n" ? b - 1 : b;
    const nl = v.indexOf("\n", fin);
    fin = nl === -1 ? v.length : nl;
    return { inicio, fin, texto: v.slice(inicio, fin), a, b };
  }

  #indentarLineas(direccion, unidad) {
    const { inicio, fin, texto, a, b } = this.#bloqueDeLineas();
    const lineas = texto.split("\n");
    let deltaPrimera = 0;
    let deltaTotal = 0;
    const nuevas = lineas.map((l, i) => {
      let r = l;
      if (direccion > 0) { r = l.trim() ? unidad + l : l; }
      else if (l.startsWith(unidad)) r = l.slice(unidad.length);
      else if (l.startsWith("\t")) r = l.slice(1);
      else r = l.replace(/^ {1,4}/, "");
      const d = r.length - l.length;
      if (i === 0) deltaPrimera = d;
      deltaTotal += d;
      return r;
    });
    reemplazar(this.ta, inicio, fin, nuevas.join("\n"));
    this.ta.setSelectionRange(Math.max(inicio, a + deltaPrimera), b + deltaTotal);
  }

  #comentar() {
    const marca = COMENTARIO[this.ext];
    if (!marca) return;
    const [abre, cierra] = marca;
    const { inicio, fin, texto, a, b } = this.#bloqueDeLineas();
    const lineas = texto.split("\n");
    const conTexto = lineas.filter((l) => l.trim());
    if (!conTexto.length) return;
    const yaComentadas = conTexto.every((l) => { const t = l.trim(); return t.startsWith(abre) && (!cierra || t.endsWith(cierra)); });
    const sangriaMin = Math.min(...conTexto.map((l) => /^[ \t]*/.exec(l)[0].length));
    let deltaPrimera = 0;
    let deltaTotal = 0;
    const nuevas = lineas.map((l, i) => {
      let r = l;
      if (l.trim()) {
        if (yaComentadas) {
          const s = /^[ \t]*/.exec(l)[0];
          let cuerpo = l.slice(s.length).slice(abre.length);
          if (cuerpo.startsWith(" ")) cuerpo = cuerpo.slice(1);
          if (cierra) { cuerpo = cuerpo.slice(0, cuerpo.lastIndexOf(cierra)); if (cuerpo.endsWith(" ")) cuerpo = cuerpo.slice(0, -1); }
          r = s + cuerpo;
        } else r = `${l.slice(0, sangriaMin)}${abre} ${l.slice(sangriaMin)}${cierra ? ` ${cierra}` : ""}`;
      }
      const d = r.length - l.length;
      if (i === 0) deltaPrimera = d;
      deltaTotal += d;
      return r;
    });
    reemplazar(this.ta, inicio, fin, nuevas.join("\n"));
    this.ta.setSelectionRange(Math.max(inicio, a + deltaPrimera), b + deltaTotal);
  }
}
