// Temas de color del editor (como «Preferences: Color Theme» de VS Code). Se guardan en este navegador.
const CLAVE = "cc_trabajo_tema_editor";

const t = (tok, fg, extra = {}) => ({ token: tok, foreground: fg.replace("#", ""), ...extra });
const reglas = (c) => [
  t("comment", c.com, { fontStyle: "italic" }), t("keyword", c.key), t("keyword.control", c.key), t("storage", c.key),
  t("string", c.str), t("string.escape", c.esc ?? c.num), t("number", c.num), t("regexp", c.esc ?? c.str),
  t("type", c.tipo), t("type.identifier", c.tipo), t("class", c.tipo), t("interface", c.tipo),
  t("identifier", c.fg), t("variable", c.var ?? c.fg), t("variable.predefined", c.tipo), t("function", c.fn), t("delimiter", c.fg),
  t("tag", c.tag ?? c.key), t("attribute.name", c.attr ?? c.fn), t("attribute.value", c.str), t("metatag", c.key),
  t("constant", c.num), t("operator", c.op ?? c.fg), t("annotation", c.fn), t("predefined", c.fn),
];

export const TEMAS = {
  "codigocamp": { nombre: "CódigoCamp (sigue el tema de la página)" },
  "dark-plus": { nombre: "Dark+ (el oscuro de VS Code)", base: "vs-dark", reglasPropias: [], colores: { "editor.background": "#1e1e1e" } },
  "light-plus": { nombre: "Light+ (el claro de VS Code)", base: "vs", reglasPropias: [], colores: { "editor.background": "#ffffff" } },
  "hc-black": { nombre: "Alto contraste oscuro", base: "hc-black", reglasPropias: [], colores: {} },
  "hc-light": { nombre: "Alto contraste claro", base: "hc-light", reglasPropias: [], colores: {} },
  "monokai": { nombre: "Monokai", base: "vs-dark", c: { fg: "#f8f8f2", com: "#88846f", key: "#f92672", str: "#e6db74", num: "#ae81ff", tipo: "#66d9ef", fn: "#a6e22e", var: "#f8f8f2", tag: "#f92672", attr: "#a6e22e" },
    colores: { "editor.background": "#272822", "editor.foreground": "#f8f8f2", "editor.lineHighlightBackground": "#3e3d32", "editor.selectionBackground": "#49483e", "editorCursor.foreground": "#f8f8f0", "editorLineNumber.foreground": "#90908a" } },
  "dracula": { nombre: "Dracula", base: "vs-dark", c: { fg: "#f8f8f2", com: "#6272a4", key: "#ff79c6", str: "#f1fa8c", num: "#bd93f9", tipo: "#8be9fd", fn: "#50fa7b", tag: "#ff79c6", attr: "#50fa7b" },
    colores: { "editor.background": "#282a36", "editor.foreground": "#f8f8f2", "editor.lineHighlightBackground": "#44475a75", "editor.selectionBackground": "#44475a", "editorCursor.foreground": "#f8f8f2", "editorLineNumber.foreground": "#6272a4" } },
  "one-dark": { nombre: "One Dark Pro", base: "vs-dark", c: { fg: "#abb2bf", com: "#7f848e", key: "#c678dd", str: "#98c379", num: "#d19a66", tipo: "#e5c07b", fn: "#61afef", var: "#e06c75", tag: "#e06c75", attr: "#d19a66" },
    colores: { "editor.background": "#282c34", "editor.foreground": "#abb2bf", "editor.lineHighlightBackground": "#2c313c", "editor.selectionBackground": "#3e4451", "editorCursor.foreground": "#528bff", "editorLineNumber.foreground": "#495162" } },
  "github-dark": { nombre: "GitHub Dark", base: "vs-dark", c: { fg: "#e6edf3", com: "#8b949e", key: "#ff7b72", str: "#a5d6ff", num: "#79c0ff", tipo: "#ffa657", fn: "#d2a8ff", tag: "#7ee787", attr: "#79c0ff" },
    colores: { "editor.background": "#0d1117", "editor.foreground": "#e6edf3", "editor.lineHighlightBackground": "#161b22", "editor.selectionBackground": "#264f78", "editorLineNumber.foreground": "#6e7681" } },
  "github-light": { nombre: "GitHub Light", base: "vs", c: { fg: "#1f2328", com: "#6e7781", key: "#cf222e", str: "#0a3069", num: "#0550ae", tipo: "#953800", fn: "#8250df", tag: "#116329", attr: "#0550ae" },
    colores: { "editor.background": "#ffffff", "editor.foreground": "#1f2328", "editor.lineHighlightBackground": "#f6f8fa", "editor.selectionBackground": "#b6e3ff" } },
  "night-owl": { nombre: "Night Owl", base: "vs-dark", c: { fg: "#d6deeb", com: "#637777", key: "#c792ea", str: "#ecc48d", num: "#f78c6c", tipo: "#ffcb8b", fn: "#82aaff", tag: "#7fdbca", attr: "#addb67" },
    colores: { "editor.background": "#011627", "editor.foreground": "#d6deeb", "editor.lineHighlightBackground": "#0b2942", "editor.selectionBackground": "#1d3b53", "editorLineNumber.foreground": "#4b6479" } },
  "solarized-light": { nombre: "Solarized claro", base: "vs", c: { fg: "#657b83", com: "#93a1a1", key: "#859900", str: "#2aa198", num: "#d33682", tipo: "#b58900", fn: "#268bd2", tag: "#268bd2", attr: "#93a1a1" },
    colores: { "editor.background": "#fdf6e3", "editor.foreground": "#657b83", "editor.lineHighlightBackground": "#eee8d5", "editor.selectionBackground": "#eee8d5" } },
};

export function definirTemas(monaco) {
  for (const [id, x] of Object.entries(TEMAS)) {
    if (!x.base) continue;
    monaco.editor.defineTheme(`cc-${id}`, { base: x.base, inherit: true, rules: x.c ? reglas(x.c) : [], colors: x.colores });
  }
}

export function temaElegido() { try { return localStorage.getItem(CLAVE) || "codigocamp"; } catch { return "codigocamp"; } }
export function guardarTema(id) { try { localStorage.setItem(CLAVE, id); } catch { /* sin espacio */ } }
/** Nombre del tema de Monaco a usar (null = el automático de CódigoCamp). */
export function temaMonaco() { const id = temaElegido(); return TEMAS[id]?.base ? `cc-${id}` : null; }
