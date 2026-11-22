// Editor de VS Code (Monaco) dentro de Trabajo. Se sirve desde /vendor/monaco (sin CDN).
//
// Qué aporta frente al editor simple: autocompletado e IntelliSense de JavaScript/TypeScript/JSX (también entre los
// archivos del proyecto: ir a la definición, renombrar, errores subrayados), HTML, CSS y JSON; minimapa, varios
// cursores, buscar y reemplazar (Ctrl+F / Ctrl+H), plegado, paleta de comandos del editor (F1) y menús en español.
//
// Cada archivo es un «modelo» con la URI file:///workspace/<ruta>. Los .js/.ts/.jsx/.tsx/.json del proyecto se
// mantienen como modelos aunque no estén abiertos, para que TypeScript entienda los import entre archivos.
// Si Monaco no carga (navegador muy viejo), trabajo.js usa el editor simple de siempre.
import { extension } from "./fs.js";
import { OPCIONES_MONACO } from "./autocompletar.js";
import { definirTemas, guardarTema, temaMonaco } from "./temas.js";

const BASE = "/vendor/monaco/vs";
let promesa = null;
export let monaco = null;
/** Cambia el tema de color de todos los editores (Ctrl+K Ctrl+T). */
export function cambiarTema(id) { guardarTema(id); monaco?.editor.setTheme(temaActual()); }

const LENGUAJES = {
  js: "javascript", mjs: "javascript", cjs: "javascript", jsx: "javascript", ts: "typescript", mts: "typescript", tsx: "typescript",
  html: "html", htm: "html", css: "css", scss: "scss", less: "less", json: "json", md: "markdown", py: "python", java: "java",
  c: "c", h: "c", cpp: "cpp", cc: "cpp", hpp: "cpp", cs: "csharp", go: "go", rs: "rust", php: "php", rb: "ruby", sql: "sql",
  kt: "kotlin", swift: "swift", sh: "shell", bash: "shell", yml: "yaml", yaml: "yaml", xml: "xml", svg: "xml", ini: "ini",
  toml: "ini", dockerfile: "dockerfile", bat: "bat", ps1: "powershell", r: "r", lua: "lua", dart: "dart", vue: "html",
  pl: "perl", pm: "perl", scala: "scala", exs: "elixir", ex: "elixir", jl: "julia", groovy: "java", cr: "ruby", d: "cpp", pas: "pascal",
  zig: "rust", lisp: "clojure", clj: "clojure", fs: "fsharp", ml: "fsharp", hs: "plaintext", nim: "python", R: "r",
};
const NOMBRES = { javascript: "JavaScript", typescript: "TypeScript", html: "HTML", css: "CSS", scss: "SCSS", json: "JSON", markdown: "Markdown", python: "Python",
  java: "Java", c: "C", cpp: "C++", csharp: "C#", go: "Go", rust: "Rust", php: "PHP", ruby: "Ruby", sql: "SQL", kotlin: "Kotlin", swift: "Swift",
  shell: "Shell", yaml: "YAML", xml: "XML", plaintext: "Texto sin formato", lua: "Lua", perl: "Perl", r: "R", scala: "Scala",
  elixir: "Elixir", julia: "Julia", pascal: "Pascal", clojure: "Lisp", fsharp: "OCaml/F#", dockerfile: "Dockerfile" };

export const lenguajeDe = (ruta) => (/(^|\/)Dockerfile$/i.test(ruta) ? "dockerfile" : LENGUAJES[extension(ruta)] ?? "plaintext");
const CODIGO = new Set(["js", "mjs", "cjs", "jsx", "ts", "mts", "tsx", "json"]);
const esCodigo = (ruta) => CODIGO.has(extension(ruta)) || /\.d\.ts$/.test(ruta);
const uriDe = (ruta) => monaco.Uri.parse(`file:///workspace/${ruta.split("/").map(encodeURIComponent).join("/")}`);

function cargarScript(src) {
  return new Promise((ok, mal) => {
    const s = document.createElement("script");
    s.src = src;
    s.onload = ok;
    s.onerror = () => mal(new Error(`No se pudo cargar ${src}`));
    document.head.appendChild(s);
  });
}

const temaActual = () => {
  const elegido = temaMonaco();
  if (elegido) return elegido;
  const t = document.documentElement.dataset.tema;
  const oscuro = t === "oscuro" || (t !== "claro" && matchMedia("(prefers-color-scheme: dark)").matches);
  return oscuro ? "codigocamp-oscuro" : "codigocamp-claro";
};

/** Carga Monaco una sola vez. Resuelve con el objeto monaco, o lanza si no se pudo (y entonces se usa el editor simple). */
export function cargarMonaco({ limite = 20000 } = {}) {
  promesa ??= (async () => {
    // Menús en español: el archivo de idioma define variables globales (no es un módulo AMD) y va antes del cargador.
    await cargarScript(`${BASE}/nls/lang/es.js`).catch(() => {});
    await cargarScript(`${BASE}/loader.js`);
    const req = globalThis.require;
    req.config({ paths: { vs: BASE } });
    const m = await Promise.race([
      new Promise((ok, mal) => req(["vs/editor/editor.main"], () => ok(globalThis.monaco), mal)),
      new Promise((_, mal) => setTimeout(() => mal(new Error("Monaco tardó demasiado en cargar")), limite)),
    ]);
    monaco = m;
    configurar(m);
    return m;
  })().catch((e) => { promesa = null; throw e; });
  return promesa;
}

function configurar(m) {
  m.editor.defineTheme("codigocamp-oscuro", { base: "vs-dark", inherit: true, rules: [], colors: { "editor.background": "#0f1424", "editorGutter.background": "#0f1424" } });
  m.editor.defineTheme("codigocamp-claro", { base: "vs", inherit: true, rules: [], colors: {} });
  definirTemas(m);
  m.editor.setTheme(temaActual());
  new MutationObserver(() => m.editor.setTheme(temaActual())).observe(document.documentElement, { attributes: true, attributeFilter: ["data-tema"] });
  matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", () => m.editor.setTheme(temaActual()));
  const ts = m.languages.typescript;
  const opciones = {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext, moduleResolution: ts.ModuleResolutionKind.NodeJs,
    jsx: ts.JsxEmit.ReactJSX, allowJs: true, checkJs: false, allowNonTsExtensions: true, esModuleInterop: true,
    allowImportingTsExtensions: true, noEmit: true, strict: false, skipLibCheck: true, resolveJsonModule: true, isolatedModules: true,
  };
  ts.typescriptDefaults.setCompilerOptions({ ...opciones, strict: true });
  ts.javascriptDefaults.setCompilerOptions(opciones);
  // Paquetes de npm (react, etc.): no hay node_modules, así que no se marcan como error «no se encuentra el módulo».
  const ignorar = [2307, 2792, 7016];
  ts.typescriptDefaults.setDiagnosticsOptions({ diagnosticCodesToIgnore: ignorar });
  ts.javascriptDefaults.setDiagnosticsOptions({ diagnosticCodesToIgnore: ignorar });
  ts.typescriptDefaults.setEagerModelSync(true);
  ts.javascriptDefaults.setEagerModelSync(true);
}

// ------------------------------------------------------------------------ modelos ----
const abiertos = new Map(); // ruta -> cantidad de editores que la muestran

function modeloPara(ruta, texto) {
  const uri = uriDe(ruta);
  let modelo = monaco.editor.getModel(uri);
  if (!modelo) modelo = monaco.editor.createModel(texto, lenguajeDe(ruta), uri);
  else if (modelo.getValue() !== texto && !abiertos.get(ruta)) modelo.setValue(texto);
  return modelo;
}

/**
 * Mantiene un modelo por cada archivo de código del proyecto (para el IntelliSense entre archivos).
 * Los que están abiertos en un editor no se tocan: el editor maneja su propio texto (y lo que no se ha guardado).
 */
export function sincronizarModelos(py, esTexto) {
  if (!monaco) return;
  const vivas = new Set();
  for (const [ruta, texto] of Object.entries(py.files)) {
    if (!esCodigo(ruta) || !esTexto(texto) || texto.length > 1_000_000) continue;
    vivas.add(uriDe(ruta).toString());
    if (!abiertos.get(ruta)) modeloPara(ruta, texto);
  }
  for (const m of monaco.editor.getModels()) {
    const u = m.uri.toString();
    if (u.startsWith("file:///workspace/") && !vivas.has(u)) {
      const ruta = decodeURIComponent(u.slice("file:///workspace/".length));
      if (!abiertos.get(ruta)) m.dispose();
    }
  }
}

/** Errores y advertencias que Monaco encontró en el proyecto: { errores, advertencias, lista:[{ruta, linea, mensaje, grave}] }. */
export function problemas() {
  if (!monaco) return { errores: 0, advertencias: 0, lista: [] };
  const lista = monaco.editor.getModelMarkers({}).filter((k) => k.resource.toString().startsWith("file:///workspace/") && k.severity >= monaco.MarkerSeverity.Warning)
    .map((k) => ({ ruta: decodeURIComponent(k.resource.path.slice("/workspace/".length)), linea: k.startLineNumber, mensaje: k.message, grave: k.severity === monaco.MarkerSeverity.Error }));
  return { errores: lista.filter((p) => p.grave).length, advertencias: lista.filter((p) => !p.grave).length, lista };
}
export const alCambiarProblemas = (fn) => monaco?.editor.onDidChangeMarkers(fn);

// ------------------------------------------------------------------------ editor ----
export class EditorMonaco {
  /**
   * Misma forma que Editor (editor.js).
   * @param {{ ruta, texto, alCambiar, alCursor, alAtajo }} o   alAtajo: "guardar" | "ejecutar" | "abrir-rapido" | "buscar-archivos" | "paleta" | "terminal"
   */
  constructor({ ruta, texto, alCambiar, alCursor, alAtajo }) {
    Object.assign(this, { alCambiar, alCursor, alAtajo });
    this.ruta = ruta;
    this.ext = extension(ruta);
    this.raiz = document.createElement("div");
    this.raiz.className = "ed ed-monaco";
    this.raiz.hidden = true;
    this.ta = this.raiz; // trabajo.js le envía eventos de foco
    this.aplicando = false;
    abiertos.set(ruta, (abiertos.get(ruta) || 0) + 1);
    this.modelo = modeloPara(ruta, texto);
    if (this.modelo.getValue() !== texto) this.modelo.setValue(texto);
    this.editor = monaco.editor.create(this.raiz, {
      model: this.modelo, automaticLayout: true, fontSize: 14, fontFamily: "'Cascadia Code', 'Fira Code', Consolas, 'Courier New', monospace",
      fontLigatures: true, minimap: { enabled: innerWidth > 1500 }, tabSize: this.ext === "py" || this.ext === "java" ? 4 : 2, insertSpaces: this.ext !== "go",
      wordWrap: ["md", "txt"].includes(this.ext) ? "on" : "off", renderWhitespace: "selection", smoothScrolling: true, cursorSmoothCaretAnimation: "on",
      bracketPairColorization: { enabled: true }, guides: { bracketPairs: true, indentation: true }, stickyScroll: { enabled: true },
      linkedEditing: true, formatOnPaste: false, scrollBeyondLastLine: false, padding: { top: 8 }, "semanticHighlighting.enabled": true,
      accessibilitySupport: "auto", ariaLabel: `Editor de ${ruta}`,
      ...OPCIONES_MONACO,
    });
    this.modelo.onDidChangeContent(() => { if (!this.aplicando) this.alCambiar(this.modelo.getValue()); });
    this.editor.onDidChangeCursorSelection(() => this.#cursor());
    this.editor.onDidFocusEditorText(() => this.#cursor());
    const K = monaco.KeyMod;
    const C = monaco.KeyCode;
    this.editor.addCommand(K.CtrlCmd | C.KeyS, () => this.alAtajo("guardar"));
    this.editor.addCommand(K.CtrlCmd | C.Enter, () => this.alAtajo("ejecutar"));
    this.editor.addCommand(K.CtrlCmd | C.KeyP, () => this.alAtajo("abrir-rapido"));
    this.editor.addCommand(K.CtrlCmd | K.Shift | C.KeyF, () => this.alAtajo("buscar-archivos"));
    this.editor.addCommand(K.CtrlCmd | K.Shift | C.KeyP, () => this.alAtajo("paleta"));
    this.editor.addCommand(K.CtrlCmd | C.Backquote, () => this.alAtajo("terminal"));
    this.editor.addCommand(K.CtrlCmd | C.KeyJ, () => this.alAtajo("terminal"));
    this.editor.addCommand(K.CtrlCmd | K.Shift | C.Backquote, () => this.alAtajo("nueva-terminal"));
    // Ctrl+Ñ (teclado en español): Monaco no siempre la reconoce como tecla propia, así que se mira la tecla escrita
    this.editor.onKeyDown((ev) => {
      const b = ev.browserEvent;
      if ((b.ctrlKey || b.metaKey) && !b.altKey && (b.key.toLowerCase() === "ñ" || b.code === "Semicolon")) {
        ev.preventDefault(); ev.stopPropagation();
        this.alAtajo(b.shiftKey ? "nueva-terminal" : "terminal");
      }
    });
    this.editor.addCommand(K.CtrlCmd | C.KeyB, () => this.alAtajo("explorador"));
    this.editor.addCommand(K.CtrlCmd | K.Shift | C.KeyG, () => this.alAtajo("git"));
    // Como VS Code: ajustes, dividir, zen, atajos, zoom, ajuste de línea, reabrir pestaña
    this.editor.addCommand(K.CtrlCmd | C.Comma, () => this.alAtajo("ajustes"));
    this.editor.addCommand(K.CtrlCmd | C.Backslash, () => this.alAtajo("dividir"));
    this.editor.addCommand(monaco.KeyMod.chord(K.CtrlCmd | C.KeyK, C.KeyZ), () => this.alAtajo("zen"));
    this.editor.addCommand(monaco.KeyMod.chord(K.CtrlCmd | C.KeyK, K.CtrlCmd | C.KeyS), () => this.alAtajo("atajos"));
    this.editor.addCommand(K.CtrlCmd | C.Equal, () => this.alAtajo("zoom+"));
    this.editor.addCommand(K.CtrlCmd | C.Minus, () => this.alAtajo("zoom-"));
    this.editor.addCommand(K.CtrlCmd | C.Digit0, () => this.alAtajo("zoom0"));
    this.editor.addCommand(K.Alt | C.KeyZ, () => this.alAtajo("ajuste-linea"));
    this.editor.addCommand(K.CtrlCmd | K.Shift | C.KeyT, () => this.alAtajo("reabrir"));
    this.editor.addCommand(monaco.KeyMod.chord(K.CtrlCmd | C.KeyK, K.CtrlCmd | C.KeyT), () => this.alAtajo("tema"));
    this.editor.addCommand(K.CtrlCmd | K.Shift | C.KeyV, () => this.alAtajo("markdown"));
    // IA como Copilot: Ctrl+I en el código y opciones en el menú del clic derecho
    const ia = [
      ["ia-linea", "✨ IA: pedir un cambio aquí…", [K.CtrlCmd | C.KeyI]],
      ["ia-explicar", "✨ IA: explicar este código", []],
      ["ia-arreglar", "✨ IA: arreglar errores", []],
      ["ia-mejorar", "✨ IA: mejorar / refactorizar", []],
      ["ia-comentar", "✨ IA: agregar comentarios y documentación", []],
      ["ia-pruebas", "✨ IA: escribir pruebas", []],
      ["ia-chat", "✨ IA: preguntar en el chat sobre esto", [K.CtrlCmd | K.Shift | C.KeyI]],
    ];
    ia.forEach(([id, label, keybindings], i) => this.editor.addAction({ id: `cc.${id}`, label, keybindings, contextMenuGroupId: "0_ia", contextMenuOrder: i + 1, run: () => this.alAtajo(id) }));
  }

  get lenguaje() { return NOMBRES[lenguajeDe(this.ruta)] ?? lenguajeDe(this.ruta); }

  #cursor() {
    const p = this.editor.getPosition();
    const sel = this.editor.getSelection();
    if (!p) return;
    this.alCursor({ linea: p.lineNumber, col: p.column, seleccion: sel ? this.modelo.getValueInRange(sel).length : 0 });
  }

  leer() { return this.modelo.getValue(); }

  /** Pone un texto que vino de fuera (terminal, git, otra pestaña) conservando deshacer y la posición. */
  establecer(texto) {
    if (texto === this.modelo.getValue()) return;
    this.aplicando = true;
    this.editor.pushUndoStop();
    this.modelo.pushEditOperations([], [{ range: this.modelo.getFullModelRange(), text: texto }], () => null);
    this.editor.pushUndoStop();
    this.aplicando = false;
  }

  renombrar(ruta) {
    const texto = this.modelo.getValue();
    const vista = this.editor.saveViewState();
    this.#soltar();
    this.ruta = ruta;
    this.ext = extension(ruta);
    abiertos.set(ruta, (abiertos.get(ruta) || 0) + 1);
    const nuevo = modeloPara(ruta, texto);
    if (nuevo.getValue() !== texto) nuevo.setValue(texto);
    this.modelo = nuevo;
    this.editor.setModel(nuevo);
    if (vista) this.editor.restoreViewState(vista);
    nuevo.onDidChangeContent(() => { if (!this.aplicando) this.alCambiar(nuevo.getValue()); });
  }

  mostrar() { this.raiz.hidden = false; requestAnimationFrame(() => this.editor.layout()); }
  ocultar() { this.raiz.hidden = true; }
  enfocar() { this.editor.focus(); }

  irALinea(linea, col = 1) {
    this.editor.revealLineInCenter(linea);
    this.editor.setPosition({ lineNumber: linea, column: col });
    this.editor.focus();
  }

  /** Selecciona un tramo (para los resultados de «Buscar en archivos»). */
  seleccionar(linea, desde, hasta) {
    this.editor.revealLineInCenter(linea);
    this.editor.setSelection(new monaco.Range(linea, desde, linea, hasta));
    this.editor.focus();
  }

  #soltar() {
    const n = (abiertos.get(this.ruta) || 1) - 1;
    if (n > 0) abiertos.set(this.ruta, n);
    else {
      abiertos.delete(this.ruta);
      if (!esCodigo(this.ruta)) this.modelo.dispose(); // los de código se quedan para el IntelliSense
    }
  }

  destruir() {
    this.editor.dispose();
    this.#soltar();
    this.raiz.remove();
  }
}

/** Editor de diferencias (como «Ver cambios» de VS Code) dentro de un contenedor. Devuelve una función para cerrarlo. */
export function crearDiff(contenedor, ruta, antes, despues) {
  const lenguaje = lenguajeDe(ruta);
  const a = monaco.editor.createModel(antes, lenguaje);
  const b = monaco.editor.createModel(despues, lenguaje);
  const diff = monaco.editor.createDiffEditor(contenedor, { automaticLayout: true, readOnly: true, renderSideBySide: innerWidth > 900, originalEditable: false, minimap: { enabled: false } });
  diff.setModel({ original: a, modified: b });
  return () => { diff.dispose(); a.dispose(); b.dispose(); };
}
