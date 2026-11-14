// Convierte texto con secuencias ANSI (colores de la terminal) en HTML seguro. Conserva el estilo entre llamadas,
// así que una misma instancia sirve para una salida que llega en trozos.
import { esc } from "./resaltado.js";

const C = { 0: "n", 1: "r", 2: "g", 3: "y", 4: "b", 5: "m", 6: "c", 7: "w" };
export const quitarAnsi = (t) => String(t).replace(/\x1b\[[0-9;]*m/g, "");

export class RenderAnsi {
  constructor() { this.reiniciar(); }
  reiniciar() { this.s = { fg: "", bg: "", bold: false, neg: false, dim: false, it: false, sub: false }; }
  #clases() {
    const { fg, bg, bold, neg, dim, it, sub } = this.s;
    return [fg && `a-${fg}`, bg && `a-bg-${bg}`, bold && "a-bold", neg && "a-neg", dim && "a-dim", it && "a-it", sub && "a-sub"].filter(Boolean).join(" ");
  }
  #aplicar(codigos) {
    const s = this.s;
    for (const k of codigos.length ? codigos : [0]) {
      if (k === 0) this.reiniciar();
      else if (k === 1) s.bold = true;
      else if (k === 2) s.dim = true;
      else if (k === 3) s.it = true;
      else if (k === 4) s.sub = true;
      else if (k === 7) s.neg = true;
      else if (k === 22) { s.dim = false; s.bold = false; }
      else if (k === 23) s.it = false;
      else if (k === 24) s.sub = false;
      else if (k === 27) s.neg = false;
      else if (k >= 30 && k <= 37) s.fg = C[k - 30];
      else if (k === 39) s.fg = "";
      else if (k >= 40 && k <= 47) s.bg = C[k - 40];
      else if (k === 49) s.bg = "";
      else if (k >= 90 && k <= 97) s.fg = `b${C[k - 90]}`;
    }
  }
  /** Texto con ANSI -> HTML. \n se deja tal cual (la terminal lo trata aparte). */
  render(texto) {
    let html = "";
    let ultimo = 0;
    const re = /\x1b\[([0-9;]*)m/g;
    const poner = (t) => {
      if (!t) return;
      const c = this.#clases();
      html += c ? `<span class="${c}">${esc(t)}</span>` : esc(t);
    };
    let m;
    while ((m = re.exec(texto))) {
      poner(texto.slice(ultimo, m.index));
      this.#aplicar(m[1] === "" ? [] : m[1].split(";").map(Number));
      ultimo = m.index + m[0].length;
    }
    poner(texto.slice(ultimo).replace(/\x1b\[[0-9;?]*[A-Za-z]/g, ""));
    return html;
  }
}

export const color = {
  rojo: (t) => `\x1b[31m${t}\x1b[0m`, verde: (t) => `\x1b[32m${t}\x1b[0m`, amarillo: (t) => `\x1b[33m${t}\x1b[0m`,
  azul: (t) => `\x1b[1;34m${t}\x1b[0m`, cian: (t) => `\x1b[36m${t}\x1b[0m`, magenta: (t) => `\x1b[35m${t}\x1b[0m`,
  gris: (t) => `\x1b[90m${t}\x1b[0m`, negrita: (t) => `\x1b[1m${t}\x1b[0m`,
};
