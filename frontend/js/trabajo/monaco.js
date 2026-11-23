// Editor de VS Code (Monaco) dentro de Trabajo. Se sirve desde /vendor/monaco (sin CDN).
//
// Qué aporta frente al editor simple: autocompletado e IntelliSense de JavaScript/TypeScript/JSX (también entre los
// archivos del proyecto: ir a la definición, renombrar, errores subrayados), HTML, CSS y JSON; minimapa, varios
// cursores, buscar y reemplazar (Ctrl+F / Ctrl+H), plegado, paleta de comandos del editor (F1) y menús en español.
//
// Cada archivo es un «modelo» con la URI file:///workspace/<ruta>. Los .js/.ts/.jsx/.tsx/.json del proyecto se
// mantienen como modelos aunque no estén abiertos, para que TypeScript entienda los import entre archivos.
const TACTIL = typeof matchMedia === "function" && matchMedia("(pointer: coarse)").matches;
// Si Monaco no carga (navegador muy viejo), trabajo.js usa el editor simple de siempre.
import { extension } from "./fs.js";
import { OPCIONES_MONACO } from "./autocompletar.js";
import { definirTemas, guardarTema, temaMonaco } from "./temas.js";
import { traducirMarcas, vigilar } from "./analisis.js";

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
// Archivos que se mantienen como modelos aunque estén cerrados: así el detector de problemas revisa TODO el proyecto
// (JavaScript/TypeScript con IntelliSense; HTML, CSS, Python, Java, C/C++, PHP… con el analizador de CódigoCamp).
const CODIGO = new Set(["js", "mjs", "cjs", "jsx", "ts", "mts", "tsx", "json", "html", "htm", "css", "scss", "less",
  "py", "java", "c", "h", "cpp", "cc", "hpp", "cs", "go", "rs", "php", "rb", "kt", "swift", "sql"]);
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
    target: ts.ScriptTarget.ESNext ?? 99, module: ts.ModuleKind.ESNext, moduleResolution: ts.ModuleResolutionKind.NodeJs,
    jsx: ts.JsxEmit.ReactJSX, allowJs: true, checkJs: true, allowNonTsExtensions: true, esModuleInterop: true,
    allowImportingTsExtensions: true, noEmit: true, strict: false, skipLibCheck: true, resolveJsonModule: true, isolatedModules: true,
  };
  ts.typescriptDefaults.setCompilerOptions({ ...opciones, strict: true });
  ts.javascriptDefaults.setCompilerOptions(opciones);
  // Paquetes de npm (react, etc.): no hay node_modules, así que no se marcan como error «no se encuentra el módulo».
  const ignorar = [2307, 2792, 7016];
  ts.typescriptDefaults.setDiagnosticsOptions({ diagnosticCodesToIgnore: ignorar });
  // En JavaScript se marcan nombres sin definir, constantes reasignadas, argumentos que faltan… pero no las quejas de
  // tipos de TypeScript (en JS confunden más de lo que ayudan) ni las de Node (require, process, module).
  ts.javascriptDefaults.setDiagnosticsOptions({ diagnosticCodesToIgnore: [...ignorar, 2339, 2345, 2322, 2531, 2532, 2533, 18046, 18047, 18048,
    2362, 2363, 2365, 2367, 2769, 2349, 2351, 2352, 2353, 2355, 2741, 2740, 2739, 2559, 2571, 2580, 2591, 2584, 2686, 7005, 7006, 7031, 7034, 7053,
    80001, 80002, 80004, 80005, 80006, 80007, 7044, 7043, 7045, 7046, 7047, 7048, 7049, 7050, 2550, 2585, 2683, 2695, 2364, 1371, 2614, 2305, 2306] });
  traducirMarcas(m);
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
    if (!esCodigo(ruta) || !esTexto(texto) || texto.length > 1_000_000 || deTerceros(ruta)) continue;
    vivas.add(uriDe(ruta).toString());
    if (!abiertos.get(ruta)) vigilar(monaco, modeloPara(ruta, texto), ruta, { completo: false });
  }
  for (const m of monaco.editor.getModels()) {
    const u = m.uri.toString();
    if (u.startsWith("file:///workspace/") && !vivas.has(u)) {
      const ruta = decodeURIComponent(u.slice("file:///workspace/".length));
      if (!abiertos.get(ruta)) soltarModelo(m);
    }
  }
}

/** Cierra el modelo de un archivo que ya no está (otro proyecto, se borró…) junto con sus marcas de error:
 *  Monaco guarda las marcas aunque el modelo se cierre y quedarían en Problemas. */
function soltarModelo(m) {
  for (const dueno of new Set(monaco.editor.getModelMarkers({ resource: m.uri }).map((k) => k.owner))) monaco.editor.setModelMarkers(m, dueno, []);
  m.dispose();
}

/** Código de librerías (node_modules, vendor, dist, venv, .min.js…): como en VS Code, sus errores no son tuyos y no
 *  van a Problemas (si abres uno de esos archivos, se revisa igual mientras está abierto). */
const TERCEROS = /(^|\/)(node_modules|bower_components|vendor|dist|build|out|coverage|\.next|\.nuxt|\.venv|venv|env|site-packages|__pycache__|target|\.gradle|\.git)\//;
export const deTerceros = (ruta) => TERCEROS.test(ruta) || /\.min\.(js|css)$|\.bundle\.js$|-bundle\.js$/i.test(ruta);

/** Errores y advertencias que Monaco encontró en el proyecto: { errores, advertencias, lista:[{ruta, linea, mensaje, grave}] }. */
export function problemas() {
  if (!monaco) return { errores: 0, advertencias: 0, lista: [] };
  // Solo los archivos del proyecto abierto (con modelo vivo): nunca marcas viejas de otro proyecto o de un archivo borrado
  const lista = monaco.editor.getModelMarkers({}).filter((k) => k.resource.toString().startsWith("file:///workspace/") && k.severity >= monaco.MarkerSeverity.Warning && monaco.editor.getModel(k.resource))
    .map((k) => ({ ruta: decodeURIComponent(k.resource.path.slice("/workspace/".length)), linea: k.startLineNumber, mensaje: k.message, grave: k.severity === monaco.MarkerSeverity.Error }));
  return { errores: lista.filter((p) => p.grave).length, advertencias: lista.filter((p) => !p.grave).length, lista };
}
export const alCambiarProblemas = (fn) => monaco?.editor.onDidChangeMarkers(fn);

/**
 * Errores que salieron al ejecutar (Python, Node, compiladores…): se subrayan en su archivo y suman en ⊗ / ⚠.
 * Cada ejecución reemplaza las marcas de la anterior; al editar el archivo marcado, su marca se quita.
 * @param {{ruta, linea, columna?, mensaje, grave}[]} lista
 * @param {(ruta:string)=>string|null} textoDe  texto del archivo (para crear el modelo si estaba cerrado)
 */
const DUENO_EJECUCION = "ejecucion";
export function marcarEjecucion(lista, textoDe) {
  if (!monaco) return;
  for (const m of monaco.editor.getModels()) monaco.editor.setModelMarkers(m, DUENO_EJECUCION, []);
  const porRuta = new Map();
  for (const p of lista) { if (!porRuta.has(p.ruta)) porRuta.set(p.ruta, []); porRuta.get(p.ruta).push(p); }
  for (const [ruta, ps] of porRuta) {
    let modelo = monaco.editor.getModel(uriDe(ruta));
    if (!modelo) { const t = textoDe(ruta); if (typeof t !== "string") continue; modelo = modeloPara(ruta, t); }
    const n = modelo.getLineCount();
    monaco.editor.setModelMarkers(modelo, DUENO_EJECUCION, ps.map((p) => {
      const l = Math.min(Math.max(1, p.linea), n);
      const ini = p.columna ? Math.min(p.columna, modelo.getLineMaxColumn(l)) : (modelo.getLineFirstNonWhitespaceColumn(l) || 1);
      return { severity: p.grave ? monaco.MarkerSeverity.Error : monaco.MarkerSeverity.Warning, message: `${p.mensaje} (al ejecutar)`,
        startLineNumber: l, startColumn: ini, endLineNumber: l, endColumn: Math.max(modelo.getLineMaxColumn(l), ini + 1), source: "Ejecución" };
    }));
    if (!marcadosEjecucion.has(modelo)) {
      marcadosEjecucion.add(modelo);
      modelo.onDidChangeContent(() => { if (monaco.editor.getModelMarkers({ resource: modelo.uri, owner: DUENO_EJECUCION }).length) monaco.editor.setModelMarkers(modelo, DUENO_EJECUCION, []); });
    }
  }
}
const marcadosEjecucion = new WeakSet();

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
    vigilar(monaco, this.modelo, ruta);   // errores de Python, Java, C/C++, HTML… mientras escribes
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
    if (TACTIL) this.#barraTactil();
    this.#lenteErrores();
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

  /** Como la extensión Error Lens: el mensaje del error se ve al final de su línea (en el celular no hay «pasar el mouse»). */
  #lenteErrores() {
    const deco = this.editor.createDecorationsCollection();
    const pintar = () => {
      const modelo = this.editor.getModel();
      if (!modelo || modelo.isDisposed()) return deco.clear();
      const porLinea = new Map();
      for (const m of monaco.editor.getModelMarkers({ resource: modelo.uri })) {
        if (m.severity < monaco.MarkerSeverity.Warning) continue;
        const x = porLinea.get(m.startLineNumber);
        if (!x || m.severity > x.severity) porLinea.set(m.startLineNumber, m);
      }
      this.erroresLinea = [...porLinea.values()].sort((a, b) => a.startLineNumber - b.startLineNumber);
      pintarMovil?.();
      deco.set([...porLinea.values()].slice(0, 150).map((m) => {
        const error = m.severity === monaco.MarkerSeverity.Error;
        const fin = modelo.getLineMaxColumn(Math.min(m.startLineNumber, modelo.getLineCount()));
        const texto = m.message.split("\n")[0];
        return {
          range: new monaco.Range(m.startLineNumber, fin, m.startLineNumber, fin),
          options: { showIfCollapsed: true, linesDecorationsClassName: error ? "lente-marca-error" : "lente-marca-aviso",
            after: { content: `  ${error ? "⊗" : "⚠"} ${texto.length > 110 ? `${texto.slice(0, 107)}…` : texto}`, inlineClassName: error ? "lente-error" : "lente-aviso", cursorStops: monaco.editor.InjectedTextCursorStops?.None } },
        };
      }));
    };
    // Celular: el error de la línea donde estás (o el primero) se lee completo arriba del código; ‹ › salta entre errores
    let pintarMovil = null;
    if (TACTIL) {
      const ed = this.editor;
      const nodo = document.createElement("div");
      nodo.className = "ed-error-movil";
      nodo.hidden = true;
      nodo.innerHTML = '<button type="button" data-e="-1" aria-label="Error anterior">‹</button><span role="status" aria-live="polite"></span><button type="button" data-e="1" aria-label="Error siguiente">›</button>';
      nodo.addEventListener("pointerdown", (e) => { if (e.target.closest("button")) e.preventDefault(); });
      const ir = (paso) => {
        const lista = this.erroresLinea || [];
        if (!lista.length) return;
        const actual = ed.getPosition()?.lineNumber ?? 0;
        const sig = paso > 0 ? lista.find((m) => m.startLineNumber > actual) ?? lista[0] : [...lista].reverse().find((m) => m.startLineNumber < actual) ?? lista[lista.length - 1];
        ed.setPosition({ lineNumber: sig.startLineNumber, column: sig.startColumn });
        ed.revealLineInCenterIfOutsideViewport(sig.startLineNumber);
      };
      nodo.addEventListener("click", (e) => { const b = e.target.closest("[data-e]"); if (b) ir(Number(b.dataset.e)); else ir(0); });
      ed.addOverlayWidget({ getId: () => "cc.error.movil", getDomNode: () => nodo, getPosition: () => null });
      pintarMovil = () => {
        const lista = this.erroresLinea || [];
        nodo.hidden = !lista.length;
        if (!lista.length) return;
        const linea = ed.getPosition()?.lineNumber ?? 0;
        const m = lista.find((x) => x.startLineNumber === linea) ?? lista[0];
        const error = m.severity === monaco.MarkerSeverity.Error;
        nodo.classList.toggle("aviso", !error);
        nodo.querySelector("span").textContent = `${error ? "⊗" : "⚠"} Línea ${m.startLineNumber}: ${m.message.split("\n")[0]}${lista.length > 1 ? `  (${lista.indexOf(m) + 1}/${lista.length})` : ""}`;
        const l = ed.getLayoutInfo();
        nodo.style.width = `${l.width - 26}px`;
        nodo.style.top = `${Math.max(4, l.height - 54 - (nodo.offsetHeight || 46) - 8)}px`;   // justo encima de la barra táctil
      };
      ed.onDidChangeCursorPosition(() => pintarMovil());
      ed.onDidLayoutChange(() => pintarMovil());
    }
    let t = null;
    const programar = () => { clearTimeout(t); t = setTimeout(pintar, 120); };
    const sub = monaco.editor.onDidChangeMarkers((uris) => { const u = this.editor.getModel()?.uri.toString(); if (uris.some((x) => x.toString() === u)) programar(); });
    this.editor.onDidChangeModel(programar);
    this.editor.onDidDispose(() => { sub.dispose(); clearTimeout(t); });
    programar();
  }

  get lenguaje() { return NOMBRES[lenguajeDe(this.ruta)] ?? lenguajeDe(this.ruta); }

  /** Celular y tableta: Monaco casi no deja seleccionar con el dedo, así que hay una barra con selección por líneas,
   *  copiar/cortar/pegar y la IA; y tocar o arrastrar sobre los números de línea selecciona esas líneas. */
  #barraTactil() {
    const ed = this.editor;
    const lineas = () => {
      const s = ed.getSelection();
      let fin = s.endLineNumber;
      if (s.endColumn === 1 && fin > s.startLineNumber) fin--;   // la selección termina al inicio de la línea siguiente
      return [s.startLineNumber, fin];
    };
    const elegir = (a, b) => {
      const m = this.modelo, n = m.getLineCount();
      a = Math.max(1, Math.min(n, a)); b = Math.max(1, Math.min(n, b));
      const [x, y] = a <= b ? [a, b] : [b, a];
      ed.setSelection(new monaco.Selection(x, 1, y, m.getLineMaxColumn(y)));
      ed.revealLinesInCenterIfOutsideViewport(x, y);
    };
    const avisar = (t) => { nodo.dataset.aviso = t; clearTimeout(this._av); this._av = setTimeout(() => { delete nodo.dataset.aviso; }, 1400); };
    const texto = () => this.modelo.getValueInRange(ed.getSelection());
    const acciones = {
      linea: () => { const [a, b] = lineas(); elegir(a, b); },
      arriba: () => { const [a, b] = lineas(); elegir(a - 1, b); },
      abajo: () => { const [a, b] = lineas(); elegir(a, b + 1); },
      menos: () => { const [a, b] = lineas(); elegir(a, Math.max(a, b - 1)); },
      palabra: () => { const p = ed.getPosition(); const w = this.modelo.getWordAtPosition(p); if (w) ed.setSelection(new monaco.Selection(p.lineNumber, w.startColumn, p.lineNumber, w.endColumn)); },
      todo: () => ed.setSelection(this.modelo.getFullModelRange()),
      copiar: async () => { const t = texto(); if (!t) return avisar("Selecciona algo primero"); try { await navigator.clipboard.writeText(t); avisar("Copiado ✓"); } catch { avisar("No se pudo copiar"); } },
      cortar: async () => { const t = texto(); if (!t) return avisar("Selecciona algo primero"); try { await navigator.clipboard.writeText(t); ed.executeEdits("cortar", [{ range: ed.getSelection(), text: "" }]); avisar("Cortado ✓"); } catch { avisar("No se pudo cortar"); } },
      pegar: async () => { try { const t = await navigator.clipboard.readText(); ed.executeEdits("pegar", [{ range: ed.getSelection(), text: t, forceMoveMarkers: true }]); ed.focus(); } catch { avisar("Mantén pulsado el editor → Pegar"); } },
      deshacer: () => ed.trigger("barra", "undo"),
      rehacer: () => ed.trigger("barra", "redo"),
      sangria: () => ed.trigger("barra", "editor.action.indentLines"),
      comentar: () => ed.trigger("barra", "editor.action.commentLine"),
      ia: () => this.alAtajo("ia-menu"),
    };
    const B = (id, ic, t) => `<button type="button" data-a="${id}" title="${t}" aria-label="${t}">${ic}<small>${t}</small></button>`;
    const nodo = document.createElement("div");
    nodo.className = "ed-tactil";
    nodo.setAttribute("role", "toolbar");
    nodo.setAttribute("aria-label", "Selección y acciones del código");
    nodo.innerHTML = B("ia", "✨", "IA") + B("linea", "▤", "Línea") + B("arriba", "⤒", "+ arriba") + B("abajo", "⤓", "+ abajo") + B("menos", "⊖", "− línea")
      + B("palabra", "ab", "Palabra") + B("todo", "⬚", "Todo") + B("copiar", "⧉", "Copiar") + B("cortar", "✂", "Cortar") + B("pegar", "📋", "Pegar")
      + B("comentar", "//", "Comentar") + B("sangria", "⇥", "Sangría") + B("deshacer", "↶", "Deshacer") + B("rehacer", "↷", "Rehacer");
    // pointerdown + preventDefault: el editor no pierde el foco ni se cierra el teclado
    nodo.addEventListener("pointerdown", (e) => { if (e.target.closest("button")) e.preventDefault(); });
    nodo.addEventListener("click", (e) => { const b = e.target.closest("button[data-a]"); if (b) acciones[b.dataset.a]?.(); });
    const widget = { getId: () => "cc.barra.tactil", getDomNode: () => nodo, getPosition: () => null };
    ed.addOverlayWidget(widget);
    const ubicar = () => { const l = ed.getLayoutInfo(); nodo.style.top = `${Math.max(0, l.height - 54)}px`; nodo.style.width = `${l.width - 12}px`; };
    ed.onDidLayoutChange(ubicar); ubicar();
    ed.updateOptions({ padding: { top: 8, bottom: 60 }, scrollBeyondLastLine: true });
    // Tocar / arrastrar sobre los números de línea
    let ancla = null;
    const enMargen = (t) => t && (t.type === monaco.editor.MouseTargetType.GUTTER_LINE_NUMBERS || t.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN || t.type === monaco.editor.MouseTargetType.GUTTER_LINE_DECORATIONS);
    ed.onMouseDown((e) => { if (enMargen(e.target) && e.target.position) { ancla = e.target.position.lineNumber; elegir(ancla, ancla); } });
    ed.onMouseMove((e) => { if (ancla && e.target.position && (e.event.buttons & 1 || e.event.browserEvent?.pointerType === "touch")) elegir(ancla, e.target.position.lineNumber); });
    ed.onMouseUp(() => { ancla = null; });
  }

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
