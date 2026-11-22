// Ajustes del editor de Trabajo (como «Settings» de VS Code): se guardan en este navegador y se aplican al instante
// a todos los editores abiertos (también al editor dividido).
const CLAVE = "cc_trabajo_ajustes";

export const PREDETERMINADOS = {
  fontSize: 14,
  tabSize: "auto",          // auto = 4 en Python/Java/C#…, 2 en web
  wordWrap: "auto",         // auto = solo en Markdown y texto
  minimap: "auto",          // auto = solo en pantallas anchas
  lineNumbers: "on",
  formatOnSave: false,
  stickyScroll: true,
  renderWhitespace: "selection",
  cursorBlinking: "smooth",
  fontLigatures: true,
  bracketPairs: true,
  autoClosing: true,
  mouseWheelZoom: true,
};

export function leerAjustes(storage = globalThis.localStorage) {
  try { return { ...PREDETERMINADOS, ...JSON.parse(storage?.getItem(CLAVE) || "{}") }; } catch { return { ...PREDETERMINADOS }; }
}

export function guardarAjustes(a, storage = globalThis.localStorage) {
  try { storage?.setItem(CLAVE, JSON.stringify(a)); } catch { /* sin espacio */ }
}

const CUATRO = new Set(["py", "java", "cs", "kt", "scala", "php", "rs", "swift", "c", "cpp", "h", "hpp", "cc", "pas", "d", "zig", "hs", "nim", "pl", "groovy"]);

/** Opciones de Monaco para un archivo según los ajustes. */
export function opcionesMonaco(a, ext = "") {
  return {
    fontSize: a.fontSize,
    tabSize: a.tabSize === "auto" ? (CUATRO.has(ext) ? 4 : 2) : Number(a.tabSize),
    wordWrap: a.wordWrap === "auto" ? (["md", "txt"].includes(ext) ? "on" : "off") : a.wordWrap,
    minimap: { enabled: a.minimap === "auto" ? innerWidth > 1500 : !!a.minimap },
    lineNumbers: a.lineNumbers,
    stickyScroll: { enabled: !!a.stickyScroll },
    renderWhitespace: a.renderWhitespace,
    cursorBlinking: a.cursorBlinking,
    fontLigatures: !!a.fontLigatures,
    bracketPairColorization: { enabled: !!a.bracketPairs },
    guides: { bracketPairs: !!a.bracketPairs, indentation: true },
    autoClosingBrackets: a.autoClosing ? "languageDefined" : "never",
    autoClosingQuotes: a.autoClosing ? "languageDefined" : "never",
    mouseWheelZoom: !!a.mouseWheelZoom,
  };
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/** Diálogo de ajustes. alCambiar(ajustes) se llama en cada cambio (se ve al instante). */
export function abrirDialogoAjustes(ajustes, alCambiar) {
  document.querySelector(".ide-ajustes")?.remove();
  const d = document.createElement("dialog");
  d.className = "ide-dialogo ancho ide-ajustes";
  const sel = (k, opciones) => `<select data-k="${k}">${opciones.map(([v, t]) => `<option value="${esc(v)}"${String(ajustes[k]) === String(v) ? " selected" : ""}>${esc(t)}</option>`).join("")}</select>`;
  const chk = (k) => `<input type="checkbox" data-k="${k}"${ajustes[k] ? " checked" : ""}>`;
  d.innerHTML = `<form method="dialog">
    <h3>⚙️ Ajustes del editor</h3>
    <p class="ide-dialogo-nota">Se guardan en este navegador y se aplican al instante. Atajo: <kbd>Ctrl</kbd>+<kbd>,</kbd></p>
    <div class="ajustes-lista">
      <label><span><b>Tamaño de letra</b><small>También con Ctrl + / Ctrl − / Ctrl 0 o Ctrl + rueda del mouse</small></span>
        <input type="number" min="9" max="32" step="1" data-k="fontSize" value="${esc(ajustes.fontSize)}"></label>
      <label><span><b>Tabulación</b><small>Espacios por nivel de sangría</small></span>${sel("tabSize", [["auto", "Automática según el lenguaje"], [2, "2 espacios"], [4, "4 espacios"], [8, "8 espacios"]])}</label>
      <label><span><b>Ajuste de línea</b><small>Partir las líneas largas (Alt+Z)</small></span>${sel("wordWrap", [["auto", "Solo en Markdown y texto"], ["on", "Siempre"], ["off", "Nunca"]])}</label>
      <label><span><b>Minimapa</b><small>Vista en miniatura a la derecha</small></span>${sel("minimap", [["auto", "En pantallas anchas"], ["true", "Siempre"], ["false", "Nunca"]])}</label>
      <label><span><b>Números de línea</b></span>${sel("lineNumbers", [["on", "Normales"], ["relative", "Relativos"], ["off", "Ocultos"]])}</label>
      <label><span><b>Espacios en blanco</b><small>Mostrar puntos donde hay espacios</small></span>${sel("renderWhitespace", [["selection", "Solo en la selección"], ["boundary", "Al inicio y final"], ["all", "Todos"], ["none", "Nunca"]])}</label>
      <label><span><b>Cursor</b></span>${sel("cursorBlinking", [["smooth", "Parpadeo suave"], ["blink", "Parpadeo"], ["phase", "Fase"], ["expand", "Expandir"], ["solid", "Fijo"]])}</label>
      <label><span><b>Formatear al guardar</b><small>Ordena el código con Ctrl+S (JS, TS, HTML, CSS, JSON)</small></span>${chk("formatOnSave")}</label>
      <label><span><b>Encabezados fijos</b><small>La función o clase actual queda arriba al hacer scroll</small></span>${chk("stickyScroll")}</label>
      <label><span><b>Colores de corchetes</b><small>Cada par de ( ) [ ] { } con su color</small></span>${chk("bracketPairs")}</label>
      <label><span><b>Cerrar automáticamente</b><small>Al escribir ( [ { " se agrega el cierre</small></span>${chk("autoClosing")}</label>
      <label><span><b>Ligaduras</b><small>=&gt; y != se ven como un símbolo (si la letra lo permite)</small></span>${chk("fontLigatures")}</label>
      <label><span><b>Zoom con la rueda</b><small>Ctrl + rueda del mouse cambia el tamaño</small></span>${chk("mouseWheelZoom")}</label>
    </div>
    <div class="ide-dialogo-botones"><button type="button" data-restablecer>Restablecer</button><button value="ok" class="primario">Listo</button></div>
  </form>`;
  const leer = (el) => {
    const k = el.dataset.k;
    if (el.type === "checkbox") return el.checked;
    if (k === "fontSize") return Math.min(32, Math.max(9, Number(el.value) || 14));
    if (k === "minimap") return el.value === "auto" ? "auto" : el.value === "true";
    if (k === "tabSize") return el.value === "auto" ? "auto" : Number(el.value);
    return el.value;
  };
  d.addEventListener("input", (e) => { const el = e.target.closest("[data-k]"); if (!el) return; ajustes[el.dataset.k] = leer(el); alCambiar({ ...ajustes }); });
  d.addEventListener("change", (e) => { const el = e.target.closest("[data-k]"); if (!el) return; ajustes[el.dataset.k] = leer(el); alCambiar({ ...ajustes }); });
  d.querySelector("[data-restablecer]").onclick = () => { Object.assign(ajustes, PREDETERMINADOS); alCambiar({ ...ajustes }); d.close(); abrirDialogoAjustes(ajustes, alCambiar); };
  d.addEventListener("close", () => d.remove());
  document.body.appendChild(d);
  d.showModal();
}

export const ATAJOS = [
  ["General", [["Ctrl+Shift+P o F1", "Paleta de comandos"], ["Ctrl+P", "Ir a un archivo"], ["Ctrl+,", "Ajustes del editor"], ["Ctrl+K Ctrl+S", "Atajos de teclado (esta ventana)"], ["Ctrl+Shift+F", "Buscar en todos los archivos"]]],
  ["Ver", [["Ctrl+B", "Mostrar/ocultar el explorador"], ["Ctrl+Ñ o Ctrl+`", "Mostrar/ocultar la terminal"], ["Ctrl+Shift+Ñ", "Terminal nueva"], ["Ctrl+Shift+G", "Git"], ["Ctrl+Shift+X", "Extensiones"], ["Ctrl+\\", "Dividir el editor"], ["Ctrl+K Z", "Modo zen (Esc para salir)"], ["Ctrl + / Ctrl − / Ctrl 0", "Tamaño de letra"]]],
  ["Archivos", [["Ctrl+S", "Guardar"], ["Ctrl+Enter", "Ejecutar el archivo"], ["Ctrl+W", "Cerrar la pestaña"], ["Ctrl+Shift+T", "Reabrir la pestaña cerrada"], ["Ctrl+Tab", "Siguiente pestaña"]]],
  ["Editor", [["Ctrl+F / Ctrl+H", "Buscar / reemplazar"], ["Ctrl+G", "Ir a la línea"], ["Ctrl+Shift+O", "Ir a un símbolo (función, clase…)"], ["F12", "Ir a la definición"], ["F2", "Renombrar símbolo"], ["Ctrl+D", "Seleccionar la siguiente coincidencia"], ["Alt+Clic", "Agregar cursor"], ["Ctrl+Alt+↑/↓", "Cursor arriba/abajo"], ["Alt+↑/↓", "Mover línea"], ["Shift+Alt+↑/↓", "Copiar línea"], ["Ctrl+Shift+K", "Borrar línea"], ["Ctrl+/", "Comentar línea"], ["Shift+Alt+F", "Formatear documento"], ["Alt+Z", "Ajuste de línea"], ["Ctrl+Espacio", "Sugerencias"], ["Ctrl+.", "Arreglos rápidos"]]],
  ["Terminal", [["↑/↓", "Historial"], ["Ctrl+R", "Buscar en el historial"], ["Tab", "Completar"], ["Ctrl+C", "Detener"], ["Ctrl+L", "Limpiar"], ["Ctrl+A / Ctrl+E", "Inicio / fin de la línea"], ["Ctrl+U / Ctrl+K / Ctrl+W", "Borrar antes / después / palabra"]]],
];

export function abrirDialogoAtajos() {
  document.querySelector(".ide-atajos")?.remove();
  const d = document.createElement("dialog");
  d.className = "ide-dialogo ancho ide-atajos";
  d.innerHTML = `<form method="dialog"><h3>⌨️ Atajos de teclado</h3><input type="search" placeholder="Buscar un atajo…" class="atajos-buscar" aria-label="Buscar un atajo">
    <div class="atajos-lista">${ATAJOS.map(([g, l]) => `<section><h4>${esc(g)}</h4>${l.map(([k, t]) => `<div class="atajo"><span>${esc(t)}</span><kbd>${esc(k)}</kbd></div>`).join("")}</section>`).join("")}</div>
    <div class="ide-dialogo-botones"><button value="ok" class="primario">Cerrar</button></div></form>`;
  d.querySelector(".atajos-buscar").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    for (const a of d.querySelectorAll(".atajo")) a.hidden = q && !a.textContent.toLowerCase().includes(q);
  });
  d.addEventListener("close", () => d.remove());
  document.body.appendChild(d);
  d.showModal();
}
