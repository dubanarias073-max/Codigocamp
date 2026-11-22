// Sugerencias de la IA mientras escribes (texto fantasma gris, como GitHub Copilot en VS Code).
//  · Aparecen solas cuando dejas de escribir medio segundo. Tab las acepta; Esc o seguir escribiendo las descarta.
//  · Alt + ] / Alt + [ : siguiente / anterior (las de Monaco). Ctrl + → acepta palabra por palabra.
//  · Se activan o desactivan con «Copiloto» en la barra de estado (se recuerda en este navegador).
const CLAVE = "cc_copiloto_linea";
const ESPERA_MS = 550;

export const copilotoActivo = () => { try { return localStorage.getItem(CLAVE) !== "0"; } catch { return true; } };
export const activarCopiloto = (si) => { try { localStorage.setItem(CLAVE, si ? "1" : "0"); } catch { /* nada */ } };

/** ¿Vale la pena pedir una sugerencia aquí? (no a mitad de una palabra ni con el archivo vacío). */
export function convienePedir(antes, despues) {
  if (!antes.trim() || antes.length < 8) return false;
  const restoLinea = despues.split("\n", 1)[0];
  // Solo al final de la línea o antes de cierres como ) ] } " ; (no a mitad de una palabra ni de código ya escrito)
  return /^[\s)\]}"'`;,>]*$/.test(restoLinea);
}

/**
 * Registra el proveedor de sugerencias en línea para todos los lenguajes.
 * @param {object} monaco
 * @param {{ pedir: (datos: object) => Promise<{texto: string}>, otrosArchivos?: (ruta: string) => {ruta: string, texto: string}[] }} op
 */
export function registrarCopilotoEnLinea(monaco, { pedir, otrosArchivos = () => [] }) {
  let ultimo = { clave: "", texto: "" };
  // Tab acepta la sugerencia aunque empiece con sangría (Monaco, por defecto, indentaría en ese caso)
  try {
    monaco.editor.addKeybindingRule?.({ keybinding: monaco.KeyCode.Tab, command: "editor.action.inlineSuggest.commit", when: "inlineSuggestionVisible && !editorReadonly && !suggestWidgetVisible" });
  } catch { /* Monaco viejo */ }
  return monaco.languages.registerInlineCompletionsProvider({ pattern: "**" }, {
    async provideInlineCompletions(modelo, pos, contexto, cancelar) {
      if (!copilotoActivo() || modelo.getValueLength() > 400_000) return { items: [] };
      const total = modelo.getFullModelRange();
      const antes = modelo.getValueInRange({ startLineNumber: 1, startColumn: 1, endLineNumber: pos.lineNumber, endColumn: pos.column });
      const despues = modelo.getValueInRange({ startLineNumber: pos.lineNumber, startColumn: pos.column, endLineNumber: total.endLineNumber, endColumn: total.endColumn });
      const manual = contexto?.triggerKind === 1;   // Alt+\ o el comando «Sugerencia en línea»
      if (!manual && !convienePedir(antes, despues)) return { items: [] };
      const clave = antes.slice(-400) + "\u0000" + despues.slice(0, 80);
      let texto;
      if (ultimo.clave === clave) texto = ultimo.texto;
      else {
        await new Promise((ok) => setTimeout(ok, manual ? 0 : ESPERA_MS));
        if (cancelar?.isCancellationRequested) return { items: [] };
        const ruta = decodeURIComponent(modelo.uri.path.replace(/^\/workspace\//, ""));
        try {
          const r = await pedir({ antes: antes.slice(-6000), despues: despues.slice(0, 2000), ruta, lenguaje: modelo.getLanguageId(), otros: otrosArchivos(ruta) });
          texto = r?.texto || "";
        } catch { texto = ""; }
        if (cancelar?.isCancellationRequested) return { items: [] };
        ultimo = { clave, texto };
      }
      if (!texto) return { items: [] };
      // La sugerencia cubre la línea desde el inicio: así, si empieza con sangría, Tab la acepta en vez de indentar.
      const linea = modelo.getLineContent(pos.lineNumber).slice(0, pos.column - 1);
      let insertar = linea + texto;
      if (/^\s*$/.test(linea) && /^[ \t]/.test(texto)) {
        const propia = texto.match(/^[ \t]*/)[0];
        insertar = propia.length >= linea.length ? texto : linea + texto.trimStart();
      }
      return { items: [{ insertText: insertar, range: new monaco.Range(pos.lineNumber, 1, pos.lineNumber, pos.column) }] };
    },
    freeInlineCompletions() {},
    disposeInlineCompletions() {},
  });
}

/** Archivos vecinos que ayudan a la IA (mismo tipo o importados), recortados. */
export function vecinos(archivos, ruta, max = 3) {
  const ext = ruta.split(".").pop();
  const texto = archivos[ruta] || "";
  return Object.entries(archivos)
    .filter(([r, t]) => r !== ruta && typeof t === "string" && t.length < 60_000 && !r.startsWith(".") && !/node_modules|\.min\./.test(r))
    .map(([r, t]) => ({ r, t, puntos: (texto.includes(r.split("/").pop().replace(/\.\w+$/, "")) ? 3 : 0) + (r.split(".").pop() === ext ? 1 : 0) }))
    .filter((x) => x.puntos > 0)
    .sort((a, b) => b.puntos - a.puntos)
    .slice(0, max)
    .map(({ r, t }) => ({ ruta: r, texto: t.slice(0, 3000) }));
}
