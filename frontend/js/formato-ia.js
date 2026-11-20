// Da formato a las respuestas de la IA (párrafos, listas, `código` y bloques con botón Copiar) sin usar HTML inseguro.
import { aviso } from "/js/app.js";

/* ===== Mostrar respuestas con formato (sin HTML inseguro) ===== */
function enLinea(padre, texto) {
  texto.split(/(`[^`\n]+`|\*\*[^*\n]+\*\*)/).forEach((t) => {
    if (!t) return;
    if (t.length > 2 && t[0] === "`" && t.at(-1) === "`") { const c = document.createElement("code"); c.textContent = t.slice(1, -1); padre.append(c); }
    else if (t.length > 4 && t.startsWith("**") && t.endsWith("**")) { const b = document.createElement("strong"); b.textContent = t.slice(2, -2); padre.append(b); }
    else padre.append(document.createTextNode(t));
  });
}
export function formato(destino, texto) {
  destino.replaceChildren();
  const partes = texto.split(/```/);
  partes.forEach((trozo, i) => {
    if (i % 2) {                                       // bloque de código
      const nl = trozo.indexOf("\n");
      const lang = nl > -1 && /^[\w+#.-]{0,15}$/.test(trozo.slice(0, nl).trim()) ? trozo.slice(0, nl).trim() : "";
      const codigo = (lang || nl === 0 ? trozo.slice(nl + 1) : trozo).replace(/\n$/, "");
      const caja = document.createElement("div"); caja.className = "bloque";
      const cab = document.createElement("div"); cab.className = "bloque-cab";
      const et = document.createElement("span"); et.textContent = lang || "código";
      const b = document.createElement("button"); b.type = "button"; b.className = "btn sm"; b.textContent = "Copiar";
      b.onclick = () => navigator.clipboard?.writeText(codigo).then(() => aviso("Código copiado")).catch(() => aviso("No se pudo copiar", true));
      cab.append(et, b);
      const pre = document.createElement("pre"); const c = document.createElement("code"); c.textContent = codigo; pre.append(c);
      caja.append(cab, pre); destino.append(caja);
      return;
    }
    let lista = null;
    trozo.split("\n").forEach((linea) => {
      const li = linea.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)$/);
      if (li) {
        if (!lista) { lista = document.createElement(/^\s*\d/.test(linea) ? "ol" : "ul"); destino.append(lista); }
        const e = document.createElement("li"); enLinea(e, li[1]); lista.append(e);
      } else {
        lista = null;
        if (!linea.trim()) return;
        const p = document.createElement("p"); enLinea(p, linea.replace(/^#+\s*/, "")); destino.append(p);
      }
    });
  });
}

