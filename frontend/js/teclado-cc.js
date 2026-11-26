// Teclado de CódigoCamp para el celular: si lo activas en Configuración, reemplaza al teclado del sistema en TODA la
// página (chats, IA, retos, buscadores, el editor y la terminal de Trabajo). Trae letras, números y una capa de símbolos
// de código, y se viste con los teclados que compras en la Tienda.
// (El teclado del sistema —Gboard, Samsung…— no se puede decorar desde una página: por eso existe este.)
const CLAVE = "cc_teclado_propio";
const CAMPOS = [
  "textarea", "[contenteditable='']", "[contenteditable='true']", ".monaco-editor .native-edit-context",
  ...["text", "search", "email", "url", "tel", "password", "number"].map((t) => `input[type='${t}']`), "input:not([type])",
].join(",");

const CAPAS = {
  abc: [
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ñ"],
    ["⇧", "z", "x", "c", "v", "b", "n", "m", "⌫"],
    ["123", "{ }", ",", "espacio", ".", "⏎"],
  ],
  num: [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["-", "/", ":", ";", "(", ")", "$", "&", "@", "\""],
    ["#+=", "'", "?", "!", "_", "=", "+", "*", "⌫"],
    ["abc", "á", ",", "espacio", ".", "⏎"],
  ],
  sim: [
    ["{", "}", "[", "]", "<", ">", "(", ")", "=", ";"],
    ["\\", "|", "`", "~", "^", "%", "#", "&", "*", "/"],
    ["123", "=>", "!=", "==", "&&", "||", "//", "⌫"],
    ["abc", "{ }", ",", "espacio", ".", "⏎"],
  ],
  emoji: [
    ["😀", "😂", "🥹", "😍", "😎", "🤔", "😭", "😡", "👍", "🙏"],
    ["🔥", "✨", "🎉", "💯", "❤️", "💜", "✅", "❌", "⚠️", "💡"],
    ["abc", "🚀", "💻", "🐛", "☕", "👀", "🤖", "⌫"],
    ["123", "😅", ",", "espacio", ".", "⏎"],
  ],
  tildes: [
    ["á", "é", "í", "ó", "ú", "ü", "ñ", "¿", "¡", "°"],
    ["Á", "É", "Í", "Ó", "Ú", "Ü", "Ñ", "€", "£", "·"],
    ["abc", "«", "»", "…", "—", "•", "⌫"],
    ["123", "emoji", ",", "espacio", ".", "⏎"],
  ],
};
// Mantén pulsada una letra para sus variantes (como el teclado del celular)
const VARIANTES = { a: "áàäâ", e: "éèëê", i: "íìïî", o: "óòöô", u: "úüùû", n: "ñ", c: "ç", "?": "¿", "!": "¡", "-": "—_", ".": "…·", "$": "€£¥", "\"": "«»“”" };
// Palabras frecuentes para las sugerencias (además de las que ya escribiste en ese campo o archivo)
const COMUNES = ("de la que el en y a los se del las un por con no una su para es al lo como más pero sus le ya o este sí porque esta entre cuando muy sin sobre también me hasta hay donde quien desde todo nos durante todos uno les ni contra otros ese eso ante ellos e esto mí antes algunos qué unos yo otro otras otra él tanto esa estos mucho quienes nada muchos cual poco ella estar estas algunas algo nosotros mi mis tú te ti tu tus ellas nosotras vosotros vosotras os mío mía hola gracias bien bueno favor código función variable clase objeto lista arreglo ciclo condición error programa proyecto archivo carpeta página botón texto número consola terminal servidor base datos usuario contraseña correo mensaje ejemplo ayuda pregunta respuesta tarea profesor clase "
  + "function const let return import export default class extends console log document querySelector addEventListener async await fetch then catch true false null undefined print def self elif else while for range len input public static void main String int boolean System out println include printf scanf SELECT FROM WHERE INSERT INTO VALUES UPDATE DELETE CREATE TABLE").split(" ").filter(Boolean);

const CSS = `.cc-teclado{position:fixed;left:0;right:0;bottom:0;z-index:2147483000;display:grid;gap:6px;padding:6px 4px calc(8px + env(safe-area-inset-bottom,0px));
background:#d1d5db;border-top:1px solid rgba(0,0,0,.12);user-select:none;-webkit-user-select:none;touch-action:manipulation;animation:cct-sube .16s ease-out;font-family:system-ui,sans-serif}
.cc-teclado[hidden]{display:none}@keyframes cct-sube{from{transform:translateY(100%)}}
html[data-tema=oscuro] .cc-teclado,html.oscuro .cc-teclado{background:#1f2937}
.cc-teclado .cct-flechas,.cc-teclado .cct-fila{display:flex;gap:5px;justify-content:center}
.cc-teclado .cct-fila.media{padding:0 5%}
.cc-teclado button{flex:1 1 0;min-width:0;height:46px;padding:0;border:0;border-radius:9px;background:#fff;color:#111827;font:500 21px system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;box-shadow:0 1.5px 0 rgba(0,0,0,.25);cursor:pointer;transition:transform .06s,filter .06s;position:relative;overflow:visible}
.cc-teclado .cct-f{height:34px;font-size:15px;min-width:0;overflow:hidden;white-space:nowrap;padding:0 2px;background:rgba(255,255,255,.75)}
.cc-teclado .cct-espacio{font-size:12px!important;font-weight:600;letter-spacing:.06em;opacity:.95}
.cc-teclado .cct-fila button[data-k="⏎"]{background:var(--tk-enter,#2563eb);color:#fff}
.cct-vista{position:fixed;z-index:2147483002;pointer-events:none;display:grid;place-items:center;min-width:46px;height:58px;padding:0 8px;border-radius:12px;background:#fff;color:#111;font:500 30px system-ui,sans-serif;box-shadow:0 8px 22px rgba(0,0,0,.35);transform:translate(-50%,-100%);animation:cct-pop .09s ease-out}
@keyframes cct-pop{from{transform:translate(-50%,-80%) scale(.7)}}
.cct-chispa{position:fixed;z-index:2147483003;pointer-events:none;width:6px;height:6px;border-radius:50%;animation:cct-chispa .6s ease-out forwards}
@keyframes cct-chispa{to{transform:translate(var(--dx),var(--dy)) scale(.2);opacity:0}}
.cc-teclado .cct-especial{flex:1.45 1 0;font-size:15px;background:#aeb4bd}
.cc-teclado .cct-especial.on,.cc-teclado .cct-f.on{background:#fff;color:#2563eb;box-shadow:inset 0 -3px 0 #2563eb}
.cc-teclado .cct-espacio{flex:4 1 0}
.cc-teclado button.pulsada{transform:scale(.9);filter:brightness(1.2)}
.cc-teclado .cct-sug{display:flex;gap:4px;min-height:30px}.cc-teclado .cct-sug button{flex:1 1 0;height:30px;font-size:15px;font-weight:600;background:transparent;box-shadow:none;border-radius:6px}
.cc-teclado .cct-sug button+button{border-left:1px solid rgba(0,0,0,.15)!important;border-radius:0}
.cc-teclado .cct-pp button{font-size:12.5px}
.cc-teclado .cct-especial.bloq{box-shadow:inset 0 -3px 0 #2563eb}
.cc-teclado [data-k=dictar].on{background:#ef4444;color:#fff;animation:cct-late 1s infinite}@keyframes cct-late{50%{opacity:.6}}
.cc-teclado .cct-var{position:fixed;display:flex;gap:4px;padding:6px;border-radius:10px;background:#fff;box-shadow:0 8px 24px rgba(0,0,0,.3);z-index:2147483001}
.cc-teclado .cct-var button{width:40px;height:44px;flex:none}.cc-teclado .cct-var button.on{background:#2563eb;color:#fff}
body.cc-teclado-abierto{padding-bottom:var(--cct-alto,250px)!important}
body.cc-teclado-abierto .ide-cuerpo{padding-bottom:calc(var(--cct-alto,250px) + 4px)!important}
body.cc-teclado-abierto .inf{display:none!important}`;

const enCelular = () => matchMedia("(pointer: coarse)").matches;
/** Sonido al teclear (se apaga en Configuración, aparte de los demás sonidos). */
export const tecladoSuena = () => { try { return localStorage.getItem("cc_teclado_sonido") !== "0"; } catch { return true; } };
export const tecladoActivo = () => { try { return localStorage.getItem(CLAVE) === "1"; } catch { return false; } };

let nodo = null, capa = "abc", mayus = false, bloqMayus = false, shiftManual = false, ctrlOn = false, ultimoShift = 0, objetivo = null, enviarTerminal = null;

/** Trabajo registra aquí cómo escribir en su terminal (local o del equipo conectado). */
export function registrarTerminal(fn) { enviarTerminal = fn; }

function pintar() {
  if (!nodo) return;
  const filas = CAPAS[capa];
  const extra = capa === "abc" ? [["ñá", "tildes"], ["😀", "emoji"]] : [];
  const codigo = enCodigo();
  const arriba = codigo
    ? [["←", "ArrowLeft"], ["→", "ArrowRight"], ["↑", "ArrowUp"], ["↓", "ArrowDown"], ["Tab", "Tab"], ["Ctrl", "ctrl"], ["Esc", "Escape"], ...(editorActivo() ? [["💡", "sugerir"]] : []), ["📋", "portapapeles"], ["⌄", "cerrar"]]
    : [["←", "ArrowLeft"], ["→", "ArrowRight"], ["↑", "ArrowUp"], ["↓", "ArrowDown"], ["Tab", "Tab"], ["📋", "portapapeles"], ...(dictado ? [["🎤", "dictar"]] : []), ...extra, ["⌄", "cerrar"]];
  const titulos = { ctrl: "Ctrl: toca Ctrl y luego una tecla (Ctrl+S guardar, Ctrl+Z deshacer, Ctrl+/ comentar, Ctrl+⏎ ejecutar…)", Escape: "Esc: cierra sugerencias", sugerir: "Mostrar sugerencias (Ctrl+Espacio)", Tab: "Tab: acepta la sugerencia o sangra" };
  nodo.innerHTML = `<div class="cct-sug" aria-live="polite"></div><div class="cct-flechas">${arriba.map(([t, k]) => `<button type="button" data-k="${k}" class="cct-f${k === "ctrl" && ctrlOn ? " on" : ""}"${titulos[k] ? ` title="${titulos[k]}"` : ""}${k === "cerrar" ? ' aria-label="Cerrar teclado" style="font-size:20px;font-weight:800"' : ""}>${t}</button>`).join("")}</div>` + (verPortapapeles ? `<div class="cct-flechas cct-pp">${[["Seleccionar todo", "todo"], ["Copiar", "copiar"], ["Cortar", "cortar"], ["Pegar", "pegar"], ["Deshacer", "deshacer"]].map(([t, k]) => `<button type="button" data-k="${k}" class="cct-f">${t}</button>`).join("")}</div>` : "") +
    filas.map((fila, nf) => `<div class="cct-fila${capa === "abc" && nf === 1 ? " media" : ""}">${fila.map((k) => {
      const ver = capa === "abc" && (mayus || bloqMayus) && k.length === 1 ? k.toUpperCase() : k;
      const clase = k === "espacio" ? "cct-espacio" : ["⇧", "⌫", "123", "abc", "#+=", "⏎"].includes(k) ? "cct-especial" : "";
      const a = (x) => x.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
      return `<button type="button" class="${clase}${k === "⇧" && (mayus || bloqMayus) ? " on" : ""}${k === "⇧" && bloqMayus ? " bloq" : ""}" data-k="${a(k)}" aria-label="${k === "espacio" ? "espacio" : a(ver)}">${k === "espacio" ? "CódigoCamp" : k === "⏎" ? "↵" : a(ver)}</button>`;
    }).join("")}</div>`).join("");
  document.documentElement.style.setProperty("--cct-alto", `${nodo.offsetHeight || 250}px`);
  sugerir();
}

/* ---- Sugerencias de palabras (como la barra de arriba del teclado del celular) ---- */
function palabraActual() {
  const ed = editorActivo();
  if (ed) { const p = ed.getPosition(); const w = p && ed.getModel().getWordUntilPosition(p); return w?.word || ""; }
  const el = objetivo;
  if (!el || el.isContentEditable || typeof el.value !== "string") return "";
  let a; try { a = el.selectionStart; } catch { a = el.value.length; }
  return (el.value.slice(0, a ?? el.value.length).match(/[\p{L}\p{N}_]+$/u) || [""])[0];
}
function textoDelCampo() {
  const ed = editorActivo();
  if (ed) return ed.getModel().getValue().slice(0, 200000);
  return objetivo?.value ?? objetivo?.textContent ?? "";
}
function sugerir() {
  const caja = nodo?.querySelector(".cct-sug");
  if (!caja) return;
  const p = palabraActual();
  if (!p || editorActivo()) { caja.innerHTML = ""; return; }
  const bajo = p.toLowerCase();
  const propias = new Set(textoDelCampo().match(/[\p{L}\p{N}_]{3,}/gu) || []);
  const lista = [...new Set([...propias, ...COMUNES])].filter((w) => w.length > p.length && w.toLowerCase().startsWith(bajo)).slice(0, 3);
  caja.innerHTML = lista.map((w) => `<button type="button" data-sug="${w.replace(/"/g, "&quot;")}">${w.replace(/</g, "&lt;")}</button>`).join("");
}
function completar(palabra) {
  const p = palabraActual();
  const resto = palabra.slice(p.length) + " ";
  const ed = editorActivo();
  if (ed) { ed.trigger("cc-teclado", "type", { text: resto.trimEnd() }); return; }
  escribirEnCampo(objetivo, resto, null);
}

/* ---- Portapapeles, deshacer y dictado por voz (lo que hace el teclado del celular) ---- */
let verPortapapeles = false;
const Reconocimiento = globalThis.SpeechRecognition || globalThis.webkitSpeechRecognition;
const dictado = Boolean(Reconocimiento);
let escuchando = null;
function textoElegido() {
  const ed = editorActivo();
  if (ed) return ed.getModel().getValueInRange(ed.getSelection());
  try { return objetivo.value.slice(objetivo.selectionStart, objetivo.selectionEnd); } catch { return String(getSelection() || ""); }
}
async function portapapeles(k) {
  const ed = editorActivo();
  if (k === "todo") { if (ed) ed.setSelection(ed.getModel().getFullModelRange()); else objetivo?.select?.(); return; }
  if (k === "deshacer") { if (ed) ed.trigger("cc-teclado", "undo", null); else document.execCommand("undo"); return; }
  if (k === "copiar" || k === "cortar") {
    const t = textoElegido();
    if (!t) return;
    try { await navigator.clipboard.writeText(t); } catch { return; }
    if (k === "cortar") { if (ed) ed.executeEdits("cc-teclado", [{ range: ed.getSelection(), text: "" }]); else escribirEnCampo(objetivo, "", "Backspace"); }
    return;
  }
  if (k === "pegar") {
    let t = "";
    try { t = await navigator.clipboard.readText(); } catch { return; }
    if (!t) return;
    if (ed) ed.trigger("cc-teclado", "type", { text: t }); else escribirEnCampo(objetivo, t, null);
  }
}
function dictar() {
  if (escuchando) { escuchando.stop(); return; }
  const r = new Reconocimiento();
  r.lang = document.documentElement.lang?.startsWith("en") ? "en-US" : "es-CO";
  r.interimResults = false;
  r.onresult = (e) => { const t = [...e.results].map((x) => x[0].transcript).join(" "); const ed = editorActivo(); if (ed) ed.trigger("cc-teclado", "type", { text: t }); else escribirEnCampo(objetivo, t, null); };
  r.onend = () => { escuchando = null; nodo?.querySelector("[data-k=dictar]")?.classList.remove("on"); };
  escuchando = r;
  nodo.querySelector("[data-k=dictar]")?.classList.add("on");
  try { r.start(); } catch { escuchando = null; }
}

const enCodigo = () => Boolean(objetivo?.closest?.(".monaco-editor, #terminalPanel"));
/** Estado del editor (¿está abierta la lista de sugerencias? ¿hay una sugerencia gris del copiloto?). */
function contexto(ed, clave) { try { return Boolean(ed._contextKeyService?.getContextKeyValue(clave)); } catch { return false; } }

/** Ctrl + tecla, como en el teclado de la computadora. En el editor se usan las acciones de VS Code; si no, el atajo de la página. */
function combinacion(k, ed) {
  const letra = k === "espacio" ? " " : k === "⏎" ? "Enter" : k === "⌫" ? "Backspace" : k.length === 1 ? k.toLowerCase() : k;
  if (ed) {
    const accion = { z: "undo", y: "redo", a: "editor.action.selectAll", "/": "editor.action.commentLine", d: "editor.action.addSelectionToNextFindMatch",
      f: "actions.find", h: "editor.action.startFindReplaceAction", " ": "editor.action.triggerSuggest", ".": "editor.action.quickFix", "]": "editor.action.indentLines", "[": "editor.action.outdentLines",
      ArrowLeft: "cursorWordLeft", ArrowRight: contexto(ed, "inlineSuggestionVisible") ? "editor.action.inlineSuggest.acceptNextWord" : "cursorWordRight", Backspace: "deleteWordLeft",
      ArrowUp: "scrollLineUp", ArrowDown: "scrollLineDown", g: "editor.action.gotoLine" }[letra];
    if (accion) { ed.focus(); ed.trigger("cc-teclado", accion, null); return; }
    if (letra === "c" || letra === "x" || letra === "v") { void portapapeles({ c: "copiar", x: "cortar", v: "pegar" }[letra]); return; }
  }
  if (objetivo?.closest?.("#terminalPanel") && enviarTerminal && /^[a-z]$/.test(letra)) { enviarTerminal(`ctrl-${letra}`); return; }
  if (!ed && (letra === "z" || letra === "a" || letra === "c" || letra === "x" || letra === "v")) { void portapapeles({ z: "deshacer", a: "todo", c: "copiar", x: "cortar", v: "pegar" }[letra]); return; }
  // El resto (Ctrl+S guardar, Ctrl+⏎ ejecutar, Ctrl+P buscar archivo…): el atajo de la página, como si fuera el teclado físico
  const destino = objetivo && document.contains(objetivo) ? objetivo : document.activeElement || document.body;
  const code = /^[a-z]$/.test(letra) ? `Key${letra.toUpperCase()}` : letra === "Enter" ? "Enter" : letra === " " ? "Space" : letra === "/" ? "Slash" : "";
  destino.dispatchEvent(new KeyboardEvent("keydown", { key: letra, code, ctrlKey: true, bubbles: true, cancelable: true }));
}

function editorActivo() {
  const m = globalThis.monaco;
  if (!m || !objetivo?.closest?.(".monaco-editor")) return null;
  return m.editor.getEditors().find((e) => e.getDomNode()?.contains(objetivo)) || null;
}

/** Cuántas unidades ocupa el último carácter visible (un emoji 👍🏽 o ❤️ son varias): borrar uno no lo deja roto. */
const segmentador = globalThis.Intl?.Segmenter ? new Intl.Segmenter("es", { granularity: "grapheme" }) : null;
function largoUltimoCaracter(texto) {
  if (!texto) return 0;
  if (segmentador) { let ultimo = ""; for (const { segment } of segmentador.segment(texto.slice(-16))) ultimo = segment; return ultimo.length || 1; }
  const c = texto.codePointAt(texto.length - 2);
  return c > 0xffff ? 2 : 1;
}

/** ¿Es un campo de texto «humano»? (chats, IA, comentarios). En código, terminal, correos y claves no se corrige nada. */
function campoDeTexto(el) {
  if (!el || el.isContentEditable === undefined) return false;
  if (el.closest?.(".monaco-editor, #terminalPanel, .term-contenedor")) return false;
  if (el.getAttribute?.("autocapitalize") === "off" || el.getAttribute?.("autocorrect") === "off" || el.spellcheck === false && el.tagName !== "TEXTAREA") return false;
  if (el.tagName === "INPUT" && !["text", "search", ""].includes(el.type)) return false;
  return el.tagName === "TEXTAREA" || el.tagName === "INPUT" || el.isContentEditable;
}
function textoAntesDelCursor(el) {
  if (!el) return "";
  if (el.isContentEditable) { const s = getSelection(); if (!s?.rangeCount) return ""; const r = s.getRangeAt(0).cloneRange(); r.selectNodeContents(el); r.setEnd(s.anchorNode, s.anchorOffset); return r.toString(); }
  try { return el.value.slice(0, el.selectionStart ?? el.value.length); } catch { return el.value ?? ""; }
}
/** Como Gboard: mayúscula sola al empezar y después de «. », «? », «! » o un salto de línea. */
function mayusculaAutomatica() {
  if (bloqMayus || capa !== "abc" || editorActivo() || !campoDeTexto(objetivo)) return;
  const antes = textoAntesDelCursor(objetivo);
  const toca = !antes.trim() || /[.!?¡¿]\s+$/.test(antes) || /\n\s*$/.test(antes);
  if (toca !== mayus) { mayus = toca; pintar(); }
}

/** Escribe en un campo normal (input, textarea o contenteditable) como lo haría el teclado. */
function escribirEnCampo(el, texto, nombre) {
  if (!el || !document.contains(el)) return;
  if (el.isContentEditable) {
    if (nombre === "Backspace") document.execCommand("delete");
    else if (nombre === "Enter") document.execCommand("insertLineBreak");
    else if (texto) document.execCommand("insertText", false, texto);
    return;
  }
  const tecla = (key) => el.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true, cancelable: true }));
  if (nombre === "Enter") {
    const seguir = tecla("Enter");
    if (!seguir) return;   // la página ya lo manejó (enviar mensaje, buscar…)
    if (el.tagName === "TEXTAREA") texto = "\n";
    else { if (el.form) el.form.requestSubmit?.(); return; }
  }
  if (nombre && nombre !== "Enter" && nombre !== "Backspace") {
    if (!tecla(nombre)) return;
    if (nombre === "ArrowLeft" || nombre === "ArrowRight") {
      try { const p = Math.max(0, Math.min(el.value.length, el.selectionStart + (nombre === "ArrowLeft" ? -1 : 1))); el.setSelectionRange(p, p); } catch { /* type=number */ }
    }
    return;
  }
  let a, b;
  try { a = el.selectionStart; b = el.selectionEnd; } catch { a = b = null; }
  if (a === null || a === undefined) {   // number, email: sin cursor; se trabaja al final
    if (el.type === "number" && texto && !/^[\d.,+\-eE]+$/.test(texto)) return;   // en un campo de números solo entran números
    el.value = nombre === "Backspace" ? el.value.slice(0, el.value.length - largoUltimoCaracter(el.value)) : el.value + texto;
  } else if (nombre === "Backspace") {
    if (a === b && a > 0) el.setRangeText("", a - largoUltimoCaracter(el.value.slice(0, a)), a, "end"); else if (a !== b) el.setRangeText("", a, b, "end"); else return;
  } else {
    if (el.maxLength > 0 && el.value.length >= el.maxLength && a === b) return;
    el.setRangeText(texto, a, b, "end");
  }
  el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: nombre === "Backspace" ? "deleteContentBackward" : "insertText", data: texto || null }));
}

function enviar(k) {
  try { navigator.vibrate?.(k === "⌫" || k === "⏎" ? 10 : 6); } catch { /* nada */ }
  // Sonido de tecla: distinto para letras, espacio, borrar y Enter, y según el teclado de la Tienda que tengas puesto
  const tipoSonido = k === "espacio" ? "espacio" : k === "⌫" ? "borrar" : k === "⏎" ? "enter" : "letra";
  if (tecladoSuena()) import("/js/sonidos.js").then((m) => m.sonarTecla(tipoSonido, document.documentElement.dataset.teclado || "normal")).catch(() => {});
  if (k === "cerrar") { ocultar(); objetivo?.blur?.(); return; }
  if (k === "ctrl") { ctrlOn = !ctrlOn; pintar(); return; }
  if (ctrlOn && !["⇧", "123", "abc", "#+=", "tildes", "emoji", "portapapeles"].includes(k)) { ctrlOn = false; pintar(); combinacion(k, editorActivo()); return; }
  if (k === "sugerir") { const e2 = editorActivo(); if (e2) { e2.focus(); e2.trigger("cc-teclado", "editor.action.triggerSuggest", null); } return; }
  if (k === "⇧") {   // dos toques seguidos: BLOQ MAYÚS
    const ahora = Date.now();
    if (bloqMayus) { bloqMayus = false; mayus = false; } else if (mayus && ahora - ultimoShift < 350) { bloqMayus = true; } else mayus = !mayus;
    shiftManual = true;
    ultimoShift = ahora; pintar(); return;
  }
  if (k === "123" || k === "abc" || k === "#+=" || k === "tildes" || k === "emoji") { capa = { "123": "num", abc: "abc", "#+=": "sim", tildes: "tildes", emoji: "emoji" }[k]; pintar(); return; }
  if (k === "portapapeles") { verPortapapeles = !verPortapapeles; pintar(); mostrar(); return; }
  if (["todo", "copiar", "cortar", "pegar", "deshacer"].includes(k)) { void portapapeles(k).then(sugerir); return; }
  if (k === "dictar") { dictar(); return; }
  if (k === "espacio" && (capa === "num" || capa === "emoji")) { capa = "abc"; pintar(); }   // como Gboard: tras el espacio vuelven las letras
  let texto = k === "espacio" ? " " : k === "⏎" ? "\n" : k;
  const nombre = { "⌫": "Backspace", "⏎": "Enter" }[k] || (/^(Arrow\w+|Tab|Escape)$/.test(k) ? k : null);
  // La página pudo vaciar el campo (p. ej. al enviar un mensaje): la mayúscula automática se decide justo antes de la letra,
  // salvo que hayas tocado ⇧ a mano.
  if (!shiftManual && !nombre && texto.length === 1 && /\p{L}/u.test(texto)) mayusculaAutomatica();
  if (capa === "abc" && (mayus || bloqMayus) && texto.length === 1 && !nombre) { texto = texto.toUpperCase(); if (!bloqMayus) { mayus = false; pintar(); } }
  if (!nombre) shiftManual = false;
  const ed = editorActivo();
  if (ed) {
    if (k === "{ }") {   // { } con el cursor en medio (Monaco a veces cierra la llave solo y a veces no, p. ej. en .txt)
      ed.trigger("cc-teclado", "type", { text: "{" });
      const pos = ed.getPosition(), linea = ed.getModel().getLineContent(pos.lineNumber);
      if (linea[pos.column - 1] !== "}") { ed.executeEdits("cc-teclado", [{ range: new globalThis.monaco.Range(pos.lineNumber, pos.column, pos.lineNumber, pos.column), text: "}" }]); ed.setPosition(pos); }
      return;
    }
    // Como en VS Code: con la lista de sugerencias abierta, ⏎ y Tab la aceptan, ↑ ↓ la recorren y Esc la cierra;
    // con una sugerencia gris del copiloto, Tab la acepta y Esc la descarta.
    const lista = contexto(ed, "suggestWidgetVisible"), gris = contexto(ed, "inlineSuggestionVisible");
    if (lista && (nombre === "Enter" || nombre === "Tab")) ed.trigger("cc-teclado", "acceptSelectedSuggestion", null);
    else if (lista && (nombre === "ArrowUp" || nombre === "ArrowDown")) ed.trigger("cc-teclado", nombre === "ArrowUp" ? "selectPrevSuggestion" : "selectNextSuggestion", null);
    else if (gris && nombre === "Tab") ed.trigger("cc-teclado", "editor.action.inlineSuggest.commit", null);
    else if (nombre === "Escape") { if (lista) ed.trigger("cc-teclado", "hideSuggestWidget", null); else if (gris) ed.trigger("cc-teclado", "editor.action.inlineSuggest.hide", null); else ed.trigger("cc-teclado", "cancelSelection", null); }
    else if (nombre === "Backspace") ed.trigger("cc-teclado", "deleteLeft", null);
    else if (nombre === "Tab") ed.trigger("cc-teclado", "tab", null);
    else if (nombre?.startsWith("Arrow")) ed.trigger("cc-teclado", { ArrowLeft: "cursorLeft", ArrowRight: "cursorRight", ArrowUp: "cursorUp", ArrowDown: "cursorDown" }[nombre], null);
    else ed.trigger("cc-teclado", "type", { text: texto });
    return;
  }
  if (objetivo?.closest?.("#terminalPanel") && enviarTerminal) { enviarTerminal(nombre || (k === "{ }" ? "{" : texto)); return; }
  if (k === "{ }") {
    escribirEnCampo(objetivo, "{}", null);
    try { const p = objetivo.selectionStart - 1; objetivo.setSelectionRange(p, p); } catch { /* contenteditable */ }
    return;
  }
  // Como Gboard: dos espacios seguidos después de una palabra ponen punto y espacio
  if (k === "espacio" && campoDeTexto(objetivo) && !objetivo.isContentEditable && /[\p{L}\p{N}] $/u.test(textoAntesDelCursor(objetivo))) {
    escribirEnCampo(objetivo, "", "Backspace");
    escribirEnCampo(objetivo, ". ", null);
    mayusculaAutomatica();
    return;
  }
  escribirEnCampo(objetivo, nombre ? "" : texto, nombre);
  mayusculaAutomatica();
}

const enviarYSugerir = (k) => { enviar(k); setTimeout(sugerir, 0); };

/** Como el teclado del celular: la letra que tocas se ve en grande encima de tu dedo. */
function vistaTecla(b) {
  if (!b.closest(".cct-fila") || b.textContent.length > 2 || ["⇧", "⌫", "↵"].includes(b.textContent)) return;
  const r = b.getBoundingClientRect(), v = document.createElement("div");
  v.className = "cct-vista";
  v.textContent = b.textContent;
  const est = getComputedStyle(b);
  v.style.background = est.backgroundImage !== "none" ? est.backgroundImage : est.backgroundColor;
  v.style.color = est.color;
  v.style.left = `${r.left + r.width / 2}px`;
  v.style.top = `${r.top - 6}px`;
  document.body.appendChild(v);
  setTimeout(() => v.remove(), 170);
}
let coloresChispa = undefined;
/** Teclados épicos y legendarios: chispas de colores al tocar. */
async function chispas(b) {
  const clave = document.documentElement.dataset.teclado;
  if (!clave || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (coloresChispa?.clave !== clave) {
    try { const m = await import("/js/cosmeticos.js"); coloresChispa = { clave, lista: m.chispasTeclado(clave) }; } catch { return; }
  }
  if (!coloresChispa.lista) return;
  const r = b.getBoundingClientRect();
  for (let i = 0; i < 7; i++) {
    const c = document.createElement("span");
    c.className = "cct-chispa";
    c.style.background = coloresChispa.lista[i % coloresChispa.lista.length];
    c.style.boxShadow = `0 0 6px ${c.style.background}`;
    c.style.left = `${r.left + r.width / 2}px`;
    c.style.top = `${r.top + r.height / 2}px`;
    const ang = Math.random() * Math.PI * 2, d = 18 + Math.random() * 26;
    c.style.setProperty("--dx", `${Math.cos(ang) * d}px`);
    c.style.setProperty("--dy", `${Math.sin(ang) * d - 10}px`);
    document.body.appendChild(c);
    setTimeout(() => c.remove(), 650);
  }
}

function mostrar() {
  if (!nodo) return;
  const estaba = !nodo.hidden;
  nodo.hidden = false;
  document.body.classList.add("cc-teclado-abierto");
  document.documentElement.style.setProperty("--cct-alto", `${nodo.offsetHeight}px`);
  if (!estaba) dispatchEvent(new Event("resize"));
  // El campo queda a la vista (no tapado por el teclado)
  setTimeout(() => {
    const r = objetivo?.getBoundingClientRect?.();
    if (r && !objetivo.closest(".monaco-editor") && r.bottom > innerHeight - nodo.offsetHeight - 8) objetivo.scrollIntoView({ block: "center", behavior: "smooth" });
  }, 60);
}
function ocultar() {
  if (!nodo || nodo.hidden) return;
  nodo.hidden = true;
  document.body.classList.remove("cc-teclado-abierto");
  dispatchEvent(new Event("resize"));
}

/** Pone o quita inputmode="none" (sin teclado del sistema) en los campos de la página. */
function marcar(el, on) {
  if (on) {
    if (el.dataset.ccIm === undefined) el.dataset.ccIm = el.getAttribute("inputmode") ?? "";
    el.setAttribute("inputmode", "none");
    el.setAttribute("virtualkeyboardpolicy", "manual");   // Chrome: no abre el teclado del sistema al tocar
  } else if (el.dataset.ccIm !== undefined) {
    if (el.dataset.ccIm) el.setAttribute("inputmode", el.dataset.ccIm); else el.removeAttribute("inputmode");
    el.removeAttribute("virtualkeyboardpolicy");
    delete el.dataset.ccIm;
  }
}
const marcarTodos = (on) => document.querySelectorAll(CAMPOS).forEach((el) => marcar(el, on));

export function activarTeclado(on) {
  try { localStorage.setItem(CLAVE, on ? "1" : "0"); } catch { /* nada */ }
  if (on) iniciarTecladoCC();
  marcarTodos(on);
  if (!on) ocultar();
  else if (document.activeElement?.matches?.(CAMPOS)) { objetivo = document.activeElement; mostrar(); }
  document.dispatchEvent(new CustomEvent("cc-teclado", { detail: { activo: on } }));
}

/** Prepara el teclado (una vez por página). Solo en celulares y tabletas. */
export function iniciarTecladoCC() {
  if (nodo || !enCelular()) return;
  const st = document.createElement("style");
  st.id = "cc-teclado-css";
  st.textContent = CSS;
  document.head.appendChild(st);
  nodo = document.createElement("div");
  nodo.className = "cc-teclado";
  nodo.hidden = true;
  nodo.setAttribute("role", "group");
  nodo.setAttribute("aria-label", "Teclado de CódigoCamp");
  document.body.appendChild(nodo);
  pintar();
  // Como el teclado del celular: al APOYAR el dedo solo se ve la tecla en grande; se escribe al SOLTAR (si deslizas a
  // otra tecla, se escribe esa). Mantener pulsado abre las variantes (á, ñ, ¿…) y se elige deslizando o tocando.
  // Borrar y las flechas sí actúan al apoyar y se repiten mientras sigues pulsando. preventDefault: el campo no pierde el foco.
  const REPITE = (k) => k === "⌫" || k.startsWith("Arrow");
  let repetir = null, largo = null, activa = null;
  const teclaEn = (x, y) => { const el = document.elementFromPoint(x, y); return el && nodo.contains(el) ? el.closest("button[data-k], button[data-var]") : null; };
  const marcarVariante = (x, y) => { const caja = nodo.querySelector(".cct-var"); if (!caja) return null; let elegida = null; for (const v of caja.querySelectorAll("button")) { const r = v.getBoundingClientRect(); const dentro = x >= r.left - 4 && x <= r.right + 4 && y >= r.top - 30 && y <= r.bottom + 60; v.classList.toggle("on", dentro); if (dentro) elegida = v; } return elegida; };
  nodo.addEventListener("pointerdown", (e) => {
    const s2 = e.target.closest("button[data-sug]");
    if (s2) { e.preventDefault(); completar(s2.dataset.sug); setTimeout(() => { sugerir(); mayusculaAutomatica(); }, 0); return; }
    const v = e.target.closest("button[data-var]");
    if (v) { e.preventDefault(); nodo.querySelector(".cct-var")?.remove(); enviarYSugerir(v.dataset.var); activa = null; return; }
    const b = e.target.closest("button[data-k]"); if (!b) return;
    e.preventDefault();
    try { nodo.setPointerCapture?.(e.pointerId); } catch { /* nada */ }
    nodo.querySelector(".cct-var")?.remove();
    b.classList.add("pulsada");
    vistaTecla(b);
    const k = b.dataset.k;
    activa = { k, b, conVariantes: false };
    if (REPITE(k)) {   // borrar y flechas: al apoyar, y se repite como un teclado de verdad
      void chispas(b);
      enviarYSugerir(k);
      activa.hecha = true;
      repetir = setTimeout(function rep() { enviarYSugerir(k); repetir = setTimeout(rep, 60); }, 420);
      return;
    }
    const base = k.toLowerCase();
    if (VARIANTES[base]) {
      clearTimeout(largo);
      largo = setTimeout(() => {
        if (!activa || activa.b !== b) return;
        nodo.querySelector(".cct-var")?.remove();
        const r = b.getBoundingClientRect(), caja = document.createElement("div");
        caja.className = "cct-var";
        const may = capa === "abc" && (mayus || bloqMayus);
        caja.innerHTML = [k, ...VARIANTES[base]].map((x) => (may ? x.toUpperCase() : x)).map((x) => `<button type="button" data-var="${x.replace(/"/g, "&quot;")}">${x.replace(/</g, "&lt;")}</button>`).join("");
        caja.style.left = `${Math.max(4, Math.min(r.left - 20, innerWidth - 44 * (VARIANTES[base].length + 1) - 12))}px`;
        caja.style.bottom = `${innerHeight - r.top + 6}px`;
        nodo.appendChild(caja);
        activa.conVariantes = true;
        try { navigator.vibrate?.(8); } catch { /* nada */ }
      }, 380);
    }
  });
  nodo.addEventListener("pointermove", (e) => {
    if (!activa || activa.hecha) return;
    if (activa.conVariantes) { marcarVariante(e.clientX, e.clientY); return; }
    const t = teclaEn(e.clientX, e.clientY);
    if (t && t !== activa.b && t.dataset.k) {   // deslizó a otra tecla: esa es la que se escribirá
      activa.b.classList.remove("pulsada");
      clearTimeout(largo);
      activa = { k: t.dataset.k, b: t, conVariantes: false };
      t.classList.add("pulsada");
    }
  });
  const soltar = (e, cancelar = false) => {
    clearTimeout(repetir); clearTimeout(largo); repetir = null;
    const a = activa; activa = null;
    nodo.querySelectorAll(".pulsada").forEach((x) => x.classList.remove("pulsada"));
    if (!a || a.hecha || cancelar) { nodo.querySelector(".cct-var")?.remove(); return; }
    let k = a.k;
    if (a.conVariantes) {
      const elegida = e && marcarVariante(e.clientX, e.clientY);
      nodo.querySelector(".cct-var")?.remove();
      if (elegida) { void chispas(a.b); enviarYSugerir(elegida.dataset.var); return; }
      // Soltó sin elegir: las variantes quedan abiertas para tocar una (o cualquier otra tecla las cierra)
      const r = a.b.getBoundingClientRect(), caja = document.createElement("div");
      caja.className = "cct-var";
      const may = capa === "abc" && (mayus || bloqMayus);
      caja.innerHTML = [k, ...VARIANTES[k.toLowerCase()]].map((x) => (may ? x.toUpperCase() : x)).map((x) => `<button type="button" data-var="${x.replace(/"/g, "&quot;")}">${x.replace(/</g, "&lt;")}</button>`).join("");
      caja.style.left = `${Math.max(4, Math.min(r.left - 20, innerWidth - 44 * (VARIANTES[k.toLowerCase()].length + 1) - 12))}px`;
      caja.style.bottom = `${innerHeight - r.top + 6}px`;
      nodo.appendChild(caja);
      return;
    }
    void chispas(a.b);
    enviarYSugerir(k);
  };
  nodo.addEventListener("pointerup", (e) => soltar(e));
  nodo.addEventListener("pointercancel", (e) => soltar(e, true));
  nodo.addEventListener("mousedown", (e) => e.preventDefault());
  document.addEventListener("pointerdown", (e) => {
    if (!tecladoActivo()) return;
    const c = e.target.closest?.(CAMPOS) || e.target.closest?.(".monaco-editor")?.querySelector(".native-edit-context, textarea");
    if (c) marcar(c, true);
  }, true);
  document.addEventListener("selectionchange", () => { if (nodo && !nodo.hidden) sugerir(); });
  document.addEventListener("focusin", (e) => {
    if (!tecladoActivo()) return;
    if (e.target.matches?.(CAMPOS) && !e.target.readOnly && !e.target.disabled) {
      marcar(e.target, true);
      if (objetivo !== e.target && capa !== "abc") { capa = "abc"; mayus = false; pintar(); }   // campo nuevo: empieza en letras
      const antes = enCodigo();
      objetivo = e.target;
      if (antes !== enCodigo()) { ctrlOn = false; pintar(); }
      mostrar(); sugerir(); mayusculaAutomatica();
    }
    else if (!nodo.contains(e.target)) ocultar();
  });
  document.addEventListener("focusout", () => {
    setTimeout(() => { if (tecladoActivo() && !document.activeElement?.matches?.(CAMPOS)) ocultar(); }, 150);
  });
  // Campos nuevos (otro archivo, un diálogo, otra terminal): también sin teclado del sistema
  let pendiente = false;
  new MutationObserver(() => {
    if (pendiente || !tecladoActivo()) return;
    pendiente = true;
    setTimeout(() => { pendiente = false; marcarTodos(true); }, 300);
  }).observe(document.body, { childList: true, subtree: true });
  if (tecladoActivo()) marcarTodos(true);
}
