// Ctrl+I en el editor (como el chat en línea de Copilot en VS Code): le pides algo a la IA justo donde está tu código.
// Reescribe la selección (o escribe en el cursor), resalta el cambio y tú decides: Aceptar (Enter) o Descartar (Esc).

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
let abierto = null;

export function abrirChatEnLinea({ editor, monaco, ruta, lenguaje, pedir, instruccion = "" }) {
  abierto?.cerrar();
  const modelo = editor.getModel();
  if (!modelo) return;
  let rango = editor.getSelection();
  if (!rango) return;
  // Sin selección: si la línea tiene código, se trabaja sobre esa línea completa; si está vacía, se escribe en el cursor
  if (rango.isEmpty()) {
    const l = rango.startLineNumber;
    const texto = modelo.getLineContent(l);
    if (texto.trim()) rango = new monaco.Range(l, 1, l, texto.length + 1);
  }
  const original = modelo.getValueInRange(rango);
  const nodo = document.createElement("div");
  nodo.className = "ia-linea";
  let decoraciones = [];
  let aplicado = null;   // rango con el texto nuevo
  // Como VS Code: se abre un espacio entre las líneas (zona) y el recuadro va ahí, sin tapar el código
  nodo.style.position = "absolute";
  const widget = { getId: () => "cc.ia.linea", getDomNode: () => nodo, getPosition: () => null };
  let zona = null;
  const ponerZona = () => {
    const alto = Math.max(56, nodo.offsetHeight + 10);
    editor.changeViewZones((acc) => {
      if (zona !== null) acc.removeZone(zona);
      const hueco = document.createElement("div");
      zona = acc.addZone({ afterLineNumber: Math.max(0, rango.startLineNumber - 1), heightInPx: alto, domNode: hueco,
        onDomNodeTop: (top) => { nodo.style.top = `${top + 4}px`; } });
    });
    nodo.style.left = `${editor.getLayoutInfo().contentLeft}px`;
  };
  const quitarZona = () => { if (zona !== null) editor.changeViewZones((acc) => acc.removeZone(zona)); zona = null; };
  const pintarPregunta = (valor = instruccion, error = "") => {
    nodo.innerHTML = `<form class="ia-linea-form"><span class="ia-linea-ic">✨</span>
      <input type="text" placeholder="${original.trim() ? "¿Qué hago con este código? (explícalo en comentarios, arréglalo, optimízalo…)" : "¿Qué código escribo aquí? (una función que…)"}" value="${esc(valor)}" aria-label="Instrucción para la IA">
      <button type="submit" class="ia-linea-btn pri">Generar</button><button type="button" class="ia-linea-btn" data-x>✕</button></form>
      ${error ? `<div class="ia-linea-error">${esc(error)}</div>` : '<div class="ia-linea-ayuda">Enter genera · Esc cierra · La IA solo cambia lo seleccionado</div>'}`;
    const input = nodo.querySelector("input");
    nodo.querySelector("form").onsubmit = (e) => { e.preventDefault(); generar(input.value.trim()); };
    nodo.querySelector("[data-x]").onclick = () => cerrar();
    input.onkeydown = (e) => { if (e.key === "Escape") { e.preventDefault(); cerrar(); } e.stopPropagation(); };
    ponerZona();
    setTimeout(() => input.focus(), 0);
  };
  const generar = async (texto) => {
    if (!texto) return;
    nodo.innerHTML = `<div class="ia-linea-form cargando"><span class="ia-linea-ic gira">✨</span><span>La IA está escribiendo…</span></div>`;
    ponerZona();
    const total = modelo.getFullModelRange();
    const antes = modelo.getValueInRange(new monaco.Range(1, 1, rango.startLineNumber, rango.startColumn));
    const despues = modelo.getValueInRange(new monaco.Range(rango.endLineNumber, rango.endColumn, total.endLineNumber, total.endColumn));
    try {
      const r = await pedir({ ruta, lenguaje, instruccion: texto, antes, seleccion: original, despues });
      const nuevo = r.texto ?? "";
      editor.pushUndoStop();
      editor.executeEdits("ia", [{ range: rango, text: nuevo, forceMoveMarkers: true }]);
      editor.pushUndoStop();
      const lineas = nuevo.split("\n");
      aplicado = new monaco.Range(rango.startLineNumber, rango.startColumn, rango.startLineNumber + lineas.length - 1,
        lineas.length === 1 ? rango.startColumn + nuevo.length : lineas[lineas.length - 1].length + 1);
      decoraciones = editor.deltaDecorations(decoraciones, [{ range: aplicado, options: { isWholeLine: true, className: "ia-linea-nuevo", linesDecorationsClassName: "ia-linea-margen" } }]);
      nodo.innerHTML = `<div class="ia-linea-form"><span class="ia-linea-ic">✨</span><span class="ia-linea-msg">«${esc(texto.slice(0, 80))}»</span>
        <button type="button" class="ia-linea-btn pri" data-si>Aceptar <kbd>Enter</kbd></button><button type="button" class="ia-linea-btn" data-no>Descartar <kbd>Esc</kbd></button><button type="button" class="ia-linea-btn" data-otra>↻ Otra vez</button></div>`;
      nodo.querySelector("[data-si]").onclick = aceptar;
      nodo.querySelector("[data-no]").onclick = descartar;
      nodo.querySelector("[data-otra]").onclick = () => { descartar(false); pintarPregunta(texto); };
      ponerZona();
      editor.revealRangeInCenterIfOutsideViewport(aplicado);
      nodo.querySelector("[data-si]").focus();
    } catch (e) { pintarPregunta(texto, e.message || "La IA no respondió."); }
  };
  const aceptar = () => { aplicado = null; cerrar(); editor.focus(); import("/js/sonidos.js").then((m) => m.sonar("correcto")).catch(() => {}); };
  const descartar = (y = true) => {
    if (aplicado) {
      editor.executeEdits("ia", [{ range: aplicado, text: original, forceMoveMarkers: true }]);
      editor.pushUndoStop();
      const ls = original.split("\n");
      rango = new monaco.Range(rango.startLineNumber, rango.startColumn, rango.startLineNumber + ls.length - 1, ls.length === 1 ? rango.startColumn + original.length : ls[ls.length - 1].length + 1);
      aplicado = null;
    }
    decoraciones = editor.deltaDecorations(decoraciones, []);
    if (y) { cerrar(); editor.focus(); }
  };
  const teclas = (e) => {
    if (!aplicado) return;
    if (e.key === "Enter") { e.preventDefault(); e.stopPropagation(); aceptar(); }
    else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); descartar(); }
  };
  nodo.addEventListener("keydown", teclas);
  const sub = editor.onKeyDown((e) => { if (aplicado && (e.browserEvent.key === "Escape" || (e.browserEvent.key === "Enter" && (e.ctrlKey || e.metaKey)))) { e.preventDefault(); e.browserEvent.key === "Escape" ? descartar() : aceptar(); } });
  function cerrar() {
    if (aplicado) descartar(false);
    decoraciones = editor.deltaDecorations(decoraciones, []);
    editor.removeOverlayWidget(widget);
    quitarZona();
    sub.dispose();
    abierto = null;
  }
  editor.addOverlayWidget(widget);
  abierto = { cerrar };
  if (instruccion) generar(instruccion); else pintarPregunta();
}
