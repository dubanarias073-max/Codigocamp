// Paleta al estilo de VS Code: Ctrl+P (abrir archivo), Ctrl+Shift+P / F1 (comandos), «>» cambia a comandos y
// «:» salta a una línea. Lógica de búsqueda pura (puntuar) + una pequeña interfaz accesible.
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/**
 * Puntuación «difusa» como la de VS Code: todas las letras de la consulta deben aparecer en orden.
 * Suma más si van seguidas, si empiezan palabra o si están en el nombre del archivo (no en la carpeta).
 * Devuelve null si no coincide, o { puntos, marcas: [índices] }.
 */
export function puntuar(texto, consulta) {
  const q = consulta.toLowerCase().replace(/\s+/g, "");
  if (!q) return { puntos: 0, marcas: [] };
  const t = texto.toLowerCase();
  const inicioNombre = texto.lastIndexOf("/") + 1;
  let puntos = 0;
  let j = 0;
  let anterior = -2;
  const marcas = [];
  for (let i = 0; i < t.length && j < q.length; i += 1) {
    if (t[i] !== q[j]) continue;
    let p = 1;
    if (i === anterior + 1) p += 5;
    if (i === 0 || "/._- ".includes(texto[i - 1]) || (texto[i] >= "A" && texto[i] <= "Z")) p += 4;
    if (i >= inicioNombre) p += 2;
    puntos += p;
    marcas.push(i);
    anterior = i;
    j += 1;
  }
  if (j < q.length) return null;
  return { puntos: puntos - texto.length * 0.05, marcas };
}

const resaltar = (texto, marcas) => {
  const m = new Set(marcas);
  return [...texto].map((c, i) => (m.has(i) ? `<b>${esc(c)}</b>` : esc(c))).join("");
};

/**
 * Abre la paleta.
 * @param {object} o
 * @param {string} [o.inicial]   texto inicial («>» para comandos)
 * @param {()=>{etiqueta, detalle?, accion, atajo?}[]} o.archivos
 * @param {()=>{etiqueta, detalle?, accion, atajo?}[]} o.comandos
 * @param {(linea:number)=>void} [o.irALinea]
 * @param {string} [o.titulo]  para listas fijas (por ejemplo, problemas)
 * @param {{etiqueta, detalle?, accion}[]} [o.lista]
 */
export function abrirPaleta({ inicial = "", archivos = () => [], comandos = () => [], irALinea = null, titulo = null, lista = null }) {
  document.querySelector(".paleta-fondo")?.remove();
  const fondo = document.createElement("div");
  fondo.className = "paleta-fondo";
  fondo.innerHTML = `<div class="paleta" role="dialog" aria-label="${esc(titulo || "Paleta")}">
    <input class="paleta-entrada" spellcheck="false" autocomplete="off" aria-label="Buscar" placeholder="${esc(titulo || "Busca un archivo por nombre · escribe > para comandos · : para ir a una línea")}">
    <div class="paleta-lista" role="listbox"></div></div>`;
  document.body.appendChild(fondo);
  const entrada = fondo.querySelector("input");
  const caja = fondo.querySelector(".paleta-lista");
  entrada.value = inicial;
  let items = [];
  let sel = 0;
  const cerrar = () => { fondo.remove(); };
  const pintar = () => {
    const v = entrada.value;
    if (lista) items = filtrar(lista, v);
    else if (v.startsWith(">")) items = filtrar(comandos(), v.slice(1));
    else if (v.startsWith(":") && irALinea) {
      const n = parseInt(v.slice(1), 10);
      items = Number.isFinite(n) ? [{ etiqueta: `Ir a la línea ${n}`, accion: () => irALinea(n), marcas: [] }] : [{ etiqueta: "Escribe el número de línea", accion: () => {}, marcas: [] }];
    } else items = filtrar(archivos(), v);
    sel = Math.min(sel, Math.max(0, items.length - 1));
    caja.innerHTML = items.length
      ? items.slice(0, 80).map((it, i) => `<div class="paleta-item${i === sel ? " on" : ""}" role="option" aria-selected="${i === sel}" data-i="${i}">
          <span class="paleta-etiqueta">${it.icono ?? ""}${resaltar(it.etiqueta, it.marcas || [])}</span>${it.detalle ? `<span class="paleta-detalle">${esc(it.detalle)}</span>` : ""}${it.atajo ? `<kbd>${esc(it.atajo)}</kbd>` : ""}</div>`).join("")
      : '<div class="paleta-vacia">Sin resultados</div>';
    caja.querySelector(".on")?.scrollIntoView({ block: "nearest" });
  };
  const elegir = (i) => { const it = items[i]; if (!it) return; cerrar(); it.accion(); };
  entrada.addEventListener("input", () => { sel = 0; pintar(); });
  entrada.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(items.length - 1, sel + 1); pintar(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(0, sel - 1); pintar(); }
    else if (e.key === "Enter") { e.preventDefault(); elegir(sel); }
    else if (e.key === "Escape") { e.preventDefault(); cerrar(); }
  });
  caja.addEventListener("click", (e) => { const f = e.target.closest(".paleta-item"); if (f) elegir(Number(f.dataset.i)); });
  fondo.addEventListener("pointerdown", (e) => { if (e.target === fondo) cerrar(); });
  pintar();
  entrada.focus();
  entrada.setSelectionRange(entrada.value.length, entrada.value.length);
  return cerrar;
}

export function filtrar(lista, consulta) {
  const q = consulta.trim();
  if (!q) return lista.map((it) => ({ ...it, marcas: [] }));
  return lista.map((it) => { const r = puntuar(it.etiqueta, q); return r ? { ...it, ...r } : null; })
    .filter(Boolean).sort((a, b) => b.puntos - a.puntos);
}
