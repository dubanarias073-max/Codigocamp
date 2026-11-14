// Resaltado de sintaxis ligero (sin dependencias). resaltar(texto, extension) devuelve HTML con <span class="t-...">.
// El texto devuelto contiene EXACTAMENTE los mismos caracteres que el original (solo se envuelven en spans),
// porque se dibuja debajo del <textarea> y ambos deben alinearse.

export const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const span = (cls, texto) => (texto === "" ? "" : cls ? `<span class="${cls}">${esc(texto)}</span>` : esc(texto));
const FIN = "(?![\\s\\S])"; // fin real del texto (con la bandera m, $ coincide en cada línea)
const palabras = (lista) => `\\b(?:${lista.trim().split(/\s+/).join("|")})\\b`;

/** Construye una función texto -> html a partir de reglas [{re, cls}] (cls puede ser una lista, una por grupo de captura). */
function tokenizador(reglas, flags = "") {
  const partes = [];
  const mapa = [];
  let grupo = 1;
  for (const r of reglas) {
    const n = new RegExp(`${r.re}|`).exec("").length - 1;
    partes.push(`(${r.re})`);
    mapa.push({ idx: grupo, n, cls: r.cls });
    grupo += 1 + n;
  }
  const re = new RegExp(partes.join("|"), `gm${flags}`);
  return (texto) => {
    let html = "";
    let ultimo = 0;
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(texto))) {
      if (m[0] === "") { re.lastIndex += 1; continue; }
      if (m.index > ultimo) html += esc(texto.slice(ultimo, m.index));
      const regla = mapa.find((r) => m[r.idx] !== undefined);
      if (Array.isArray(regla.cls)) {
        for (let k = 0; k < regla.n; k += 1) html += span(regla.cls[k], m[regla.idx + 1 + k] ?? "");
      } else {
        html += span(regla.cls, m[regla.idx]);
      }
      ultimo = m.index + m[0].length;
    }
    return html + esc(texto.slice(ultimo));
  };
}

const COM_C = String.raw`\/\/[^\n]*|\/\*[\s\S]*?(?:\*\/|${FIN})`;
const STR_DOBLE = String.raw`"(?:\\.|[^"\\\n])*"?`;
const STR_SIMPLE = String.raw`'(?:\\.|[^'\\\n])*'?`;
const CHAR_C = String.raw`'(?:\\[^\n]{1,10}?|[^'\\\n])'`;
const NUM = String.raw`\b(?:0[xX][\da-fA-F_]+|0[bB][01_]+|\d[\d_]*\.?\d*(?:[eE][+-]?\d+)?[fFlLuUn]*)\b|\.\d+\b`;
const LLAMADA = String.raw`\b[A-Za-z_$][\w$]*(?=\s*\()`;
const TIPO = String.raw`\b[A-Z][A-Za-z0-9_$]*\b`;

const JS_KW = "break case catch class const continue debugger default delete do else export extends finally for function if import in instanceof let new of return static super switch throw try typeof var void while with yield async await";
const TS_KW = "interface type enum implements public private protected readonly abstract namespace declare keyof as is infer satisfies";
const JS_LIT = "true false null undefined NaN Infinity this";

const js = (extra = "") => tokenizador([
  { re: COM_C, cls: "t-c" },
  { re: String.raw`${STR_DOBLE}|${STR_SIMPLE}|` + "`(?:\\\\[\\s\\S]|[^`\\\\])*`?", cls: "t-s" },
  { re: NUM, cls: "t-n" },
  { re: palabras(JS_KW + " " + extra), cls: "t-k" },
  { re: palabras(JS_LIT), cls: "t-l" },
  { re: LLAMADA, cls: "t-f" },
  { re: TIPO, cls: "t-t" },
]);

const python = tokenizador([
  { re: "#[^\\n]*", cls: "t-c" },
  { re: String.raw`[rRbBuUfF]{0,2}(?:"""[\s\S]*?(?:"""|${FIN})|'''[\s\S]*?(?:'''|${FIN}))`, cls: "t-s" },
  { re: String.raw`[rRbBuUfF]{0,2}(?:${STR_DOBLE}|${STR_SIMPLE})`, cls: "t-s" },
  { re: String.raw`@[A-Za-z_][\w.]*`, cls: "t-d" },
  { re: String.raw`\b(def)(\s+)([A-Za-z_]\w*)`, cls: ["t-k", "", "t-f"] },
  { re: String.raw`\b(class)(\s+)([A-Za-z_]\w*)`, cls: ["t-k", "", "t-t"] },
  { re: NUM, cls: "t-n" },
  { re: palabras("and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield match case"), cls: "t-k" },
  { re: palabras("True False None self cls"), cls: "t-l" },
  { re: LLAMADA, cls: "t-f" },
  { re: TIPO, cls: "t-t" },
]);

function clike({ kw, tipos = "", lit = "true false null", hash = false, triple = false, char = true, extra = [] }) {
  return tokenizador([
    { re: COM_C + (hash ? "|#[^\\n]*" : ""), cls: "t-c" },
    ...(triple ? [{ re: String.raw`"""[\s\S]*?(?:"""|${FIN})`, cls: "t-s" }] : []),
    ...extra,
    { re: char ? `${STR_DOBLE}|${CHAR_C}` : `${STR_DOBLE}|${STR_SIMPLE}`, cls: "t-s" },
    { re: NUM, cls: "t-n" },
    { re: palabras(kw), cls: "t-k" },
    ...(tipos ? [{ re: palabras(tipos), cls: "t-t" }] : []),
    { re: palabras(lit), cls: "t-l" },
    { re: LLAMADA, cls: "t-f" },
    { re: TIPO, cls: "t-t" },
  ]);
}

const PREPROC = { re: String.raw`^([ \t]*#[ \t]*\w+)([ \t]*)(<[^>\n]+>)?`, cls: ["t-p", "", "t-s"] };
const C_TIPOS = "int char float double void long short unsigned signed size_t bool string auto";
const lenguajesClike = {
  c: clike({ kw: "if else for while do switch case break continue return goto sizeof struct union enum typedef static const extern volatile register inline default", tipos: C_TIPOS, lit: "NULL true false", extra: [PREPROC] }),
  cpp: clike({ kw: "if else for while do switch case break continue return goto sizeof struct union enum typedef static const extern volatile inline default class public private protected virtual namespace using template typename new delete try catch throw this operator override final explicit constexpr nullptr", tipos: C_TIPOS + " vector map set string", lit: "NULL true false nullptr", extra: [PREPROC] }),
  java: clike({ kw: "abstract assert break case catch class continue default do else enum extends final finally for if implements import instanceof interface native new package private protected public return static strictfp super switch synchronized this throw throws transient try volatile while var record", tipos: "int long short byte float double boolean char void String", triple: true }),
  cs: clike({ kw: "abstract as base break case catch class const continue default delegate do else enum event explicit extern finally fixed for foreach goto if implicit in interface internal is lock namespace new operator out override params private protected public readonly ref return sealed sizeof static struct switch this throw try typeof unchecked unsafe using var virtual volatile while async await get set", tipos: "int long short byte float double decimal bool char void string object", triple: true, extra: [PREPROC] }),
  go: clike({ kw: "break case chan const continue default defer else fallthrough for func go goto if import interface map package range return select struct switch type var", tipos: "int int8 int16 int32 int64 uint uint8 uint16 uint32 uint64 float32 float64 string bool byte rune error any", lit: "true false nil iota", extra: [{ re: "`[^`]*`?", cls: "t-s" }] }),
  rs: clike({ kw: "as async await break const continue crate dyn else enum extern fn for if impl in let loop match mod move mut pub ref return self Self static struct super trait type unsafe use where while", tipos: "i8 i16 i32 i64 i128 isize u8 u16 u32 u64 u128 usize f32 f64 bool char str String Vec Option Result Box", lit: "true false None Some Ok Err", extra: [{ re: String.raw`\b[a-z_]\w*!(?=[\s(\[{])`, cls: "t-f" }] }),
  swift: clike({ kw: "associatedtype break case catch class continue default defer deinit do else enum extension fallthrough fileprivate for func guard if import in init inout internal is let open operator private protocol public repeat rethrows return self static struct subscript super switch throw throws try typealias var where while async await", tipos: "Int Double Float String Bool Character Array Dictionary Set Optional Any", lit: "true false nil", triple: true }),
  kt: clike({ kw: "as break class continue do else for fun if in interface is object package return super this throw try typealias val var when while by catch constructor delegate dynamic field file finally get import init param property receiver set setparam where abstract annotation companion const crossinline data enum expect external final infix inline inner internal lateinit noinline open operator out override private protected public reified sealed suspend tailrec vararg", tipos: "Int Long Short Byte Float Double Boolean Char String Unit Any Nothing List Map Set", lit: "true false null", triple: true }),
  php: clike({
    kw: "abstract and array as break callable case catch class clone const continue declare default do echo else elseif empty enddeclare endfor endforeach endif endswitch endwhile extends final finally fn for foreach function global goto if implements include include_once instanceof insteadof interface isset list match namespace new or print private protected public require require_once return static switch throw trait try unset use var while xor yield",
    lit: "true false null TRUE FALSE NULL", hash: true, char: false,
    extra: [{ re: String.raw`<\?php|<\?=|\?>`, cls: "t-p" }, { re: String.raw`\$[A-Za-z_]\w*`, cls: "t-v" }],
  }),
};

const ruby = tokenizador([
  { re: "#[^\\n]*", cls: "t-c" },
  { re: `${STR_DOBLE}|${STR_SIMPLE}`, cls: "t-s" },
  { re: String.raw`:[A-Za-z_]\w*[?!]?`, cls: "t-n" },
  { re: String.raw`@@?[A-Za-z_]\w*|\$\w+`, cls: "t-v" },
  { re: String.raw`\b(def)(\s+)([A-Za-z_]\w*[?!=]?)`, cls: ["t-k", "", "t-f"] },
  { re: NUM, cls: "t-n" },
  { re: palabras("alias and begin break case class def defined? do else elsif end ensure for if in module next nil not or redo rescue retry return self super then undef unless until when while yield require require_relative puts print attr_accessor attr_reader attr_writer"), cls: "t-k" },
  { re: palabras("true false nil"), cls: "t-l" },
  { re: TIPO, cls: "t-t" },
]);

const sql = tokenizador([
  { re: String.raw`--[^\n]*|\/\*[\s\S]*?(?:\*\/|${FIN})`, cls: "t-c" },
  { re: String.raw`'(?:''|[^'])*'?`, cls: "t-s" },
  { re: NUM, cls: "t-n" },
  { re: palabras("select from where and or not in is null like between join inner left right outer full cross on as group by order having limit offset insert into values update set delete create table alter drop add column index view database primary key foreign references unique default check constraint distinct union all exists case when then else end asc desc if begin commit rollback transaction truncate"), cls: "t-k" },
  { re: palabras("int integer bigint smallint tinyint varchar char text date datetime timestamp time float double decimal numeric boolean bool blob serial"), cls: "t-t" },
  { re: LLAMADA, cls: "t-f" },
], "i");

const shell = tokenizador([
  { re: "#[^\\n]*", cls: "t-c" },
  { re: `${STR_DOBLE}|${STR_SIMPLE}`, cls: "t-s" },
  { re: String.raw`\$(?:\{[^}\n]*\}|[A-Za-z_]\w*|[@#?*$!0-9])`, cls: "t-v" },
  { re: String.raw`\B-{1,2}[A-Za-z][\w-]*`, cls: "t-n" },
  { re: palabras("if then else elif fi for while until do done case esac function in select return exit export local source alias unset"), cls: "t-k" },
  { re: palabras("echo cd ls cat grep mkdir rm cp mv touch git node python npm pwd clear"), cls: "t-f" },
]);

const json = tokenizador([
  { re: String.raw`"(?:\\.|[^"\\\n])*"(?=\s*:)`, cls: "t-pr" },
  { re: STR_DOBLE, cls: "t-s" },
  { re: String.raw`-?\b\d+\.?\d*(?:[eE][+-]?\d+)?\b`, cls: "t-n" },
  { re: palabras("true false null"), cls: "t-k" },
]);

const markdown = tokenizador([
  { re: "^```[\\s\\S]*?(?:^```|" + FIN + ")", cls: "t-s" },
  { re: "^#{1,6}[ \\t][^\\n]*", cls: "t-h" },
  { re: "`[^`\\n]+`", cls: "t-s" },
  { re: String.raw`\*\*[^*\n]+\*\*|__[^_\n]+__`, cls: "t-b" },
  { re: String.raw`\[[^\]\n]+\]\([^)\n]+\)`, cls: "t-f" },
  { re: String.raw`^[ \t]*(?:[-*+]|\d+\.)[ \t]`, cls: "t-k" },
]);

const config = tokenizador([
  { re: "#[^\\n]*|;[^\\n]*", cls: "t-c" },
  { re: `${STR_DOBLE}|${STR_SIMPLE}`, cls: "t-s" },
  { re: String.raw`^[ \t-]*[\w.\-/]+(?=[ \t]*[:=])`, cls: "t-pr" },
  { re: NUM, cls: "t-n" },
  { re: palabras("true false null yes no on off"), cls: "t-k" },
]);

// ---- CSS: necesita saber si estamos en un selector o dentro de un bloque { } ----
const CSS_RE = {
  sel: /\/\*[\s\S]*?(?:\*\/|(?![\s\S]))|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?|@[\w-]+|#[\w-]+|\.[\w-]+|::?[\w-]+(?:\([^)\n]*\))?|[A-Za-z][\w-]*|\d+(?:\.\d+)?%?|[{};]|[\s\S]/y,
  dec: /\/\*[\s\S]*?(?:\*\/|(?![\s\S]))|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?|#[\da-fA-F]{3,8}\b|!important|-?\d*\.?\d+(?:[a-zA-Z%]+)?|-{0,2}[A-Za-z_][\w-]*|[{};:]|[\s\S]/y,
};
const AT_CONTENEDOR = new Set(["@media", "@supports", "@keyframes", "@layer", "@container", "@document", "@-webkit-keyframes", "@scope"]);

function css(texto) {
  const pila = [];
  let html = "";
  let i = 0;
  let trasDosPuntos = false;
  let arroba = "";
  while (i < texto.length) {
    const re = pila[pila.length - 1] === "d" ? CSS_RE.dec : CSS_RE.sel;
    re.lastIndex = i;
    const m = re.exec(texto);
    const t = m[0];
    i += t.length;
    const dec = re === CSS_RE.dec;
    if (t.startsWith("/*")) html += span("t-c", t);
    else if (t[0] === '"' || t[0] === "'") html += span("t-s", t);
    else if (t === "{") {
      pila.push(dec || !AT_CONTENEDOR.has(arroba) ? "d" : "c");
      arroba = ""; trasDosPuntos = false; html += "{";
    } else if (t === "}") { pila.pop(); trasDosPuntos = false; html += "}"; }
    else if (t === ";") { trasDosPuntos = false; arroba = dec ? arroba : ""; html += ";"; }
    else if (dec && t === ":") { trasDosPuntos = true; html += ":"; }
    else if (!dec && t[0] === "@") { arroba = t; html += span("t-k", t); }
    else if (!dec && t[0] === "#") html += span("t-id", t);
    else if (!dec && t[0] === ".") html += span("t-cl", t);
    else if (!dec && t[0] === ":") html += span("t-pse", t);
    else if (!dec && /^[A-Za-z]/.test(t)) html += arroba ? span("t-v", t) : span("t-tag", t);
    else if (t === "!important") html += span("t-k", t);
    else if (/^#[\da-fA-F]{3,8}$/.test(t) || /^-?\d*\.?\d+[a-zA-Z%]*$/.test(t)) html += span("t-n", t);
    else if (dec && /^-{0,2}[A-Za-z_]/.test(t)) {
      const sigue = texto[i] === "(";
      html += trasDosPuntos ? span(sigue ? "t-f" : "t-v", t) : span("t-pr", t);
    } else html += esc(t);
  }
  return html;
}

// ---- HTML ----
const ATRIBUTOS = /([^\s=\/"'<>]+)(\s*=\s*)?("[^"]*"?|'[^']*'?|[^\s"'=<>`]+)?/g;

function atributos(texto) {
  let html = "";
  let ultimo = 0;
  ATRIBUTOS.lastIndex = 0;
  let m;
  while ((m = ATRIBUTOS.exec(texto))) {
    if (m[0] === "") { ATRIBUTOS.lastIndex += 1; continue; }
    html += esc(texto.slice(ultimo, m.index)) + span("t-at", m[1]) + esc(m[2] ?? "") + span("t-s", m[3] ?? "");
    ultimo = m.index + m[0].length;
  }
  return html + esc(texto.slice(ultimo));
}

const jsPlano = js();
const tsPlano = js(TS_KW);

function html(texto) {
  const re = /<!--[\s\S]*?(?:-->|(?![\s\S]))|<![A-Za-z][^>]*>?|<(\/?)([A-Za-z][\w:-]*)((?:"[^"]*"|'[^']*'|[^'">])*)(>?)/g;
  let salida = "";
  let ultimo = 0;
  let m;
  while ((m = re.exec(texto))) {
    salida += esc(texto.slice(ultimo, m.index));
    ultimo = m.index + m[0].length;
    if (m[0].startsWith("<!--")) { salida += span("t-c", m[0]); continue; }
    if (m[0].startsWith("<!")) { salida += span("t-p", m[0]); continue; }
    const [, cierre, nombre, attrs, fin] = m;
    salida += esc("<" + cierre) + span("t-tag", nombre) + atributos(attrs) + esc(fin);
    const bajo = nombre.toLowerCase();
    if (!cierre && fin && !attrs.trimEnd().endsWith("/") && (bajo === "script" || bajo === "style")) {
      const cierreIdx = texto.toLowerCase().indexOf(`</${bajo}`, ultimo);
      const hasta = cierreIdx === -1 ? texto.length : cierreIdx;
      const interior = texto.slice(ultimo, hasta);
      salida += bajo === "script" ? (/type\s*=\s*["']?(?:text\/(?!javascript)|application\/(?:ld\+)?json)/i.test(attrs) ? esc(interior) : jsPlano(interior)) : css(interior);
      ultimo = hasta;
      re.lastIndex = hasta;
    }
  }
  return salida + esc(texto.slice(ultimo));
}

const TABLA = {
  html: ["HTML", html], htm: ["HTML", html], vue: ["Vue", html], svg: ["SVG", html], xml: ["XML", html],
  css: ["CSS", css], scss: ["SCSS", css],
  js: ["JavaScript", jsPlano], mjs: ["JavaScript", jsPlano], cjs: ["JavaScript", jsPlano], jsx: ["JavaScript React", jsPlano],
  ts: ["TypeScript", tsPlano], tsx: ["TypeScript React", tsPlano],
  json: ["JSON", json], py: ["Python", python],
  java: ["Java", lenguajesClike.java], c: ["C", lenguajesClike.c], h: ["C", lenguajesClike.c], cpp: ["C++", lenguajesClike.cpp],
  cc: ["C++", lenguajesClike.cpp], hpp: ["C++", lenguajesClike.cpp], cs: ["C#", lenguajesClike.cs], go: ["Go", lenguajesClike.go],
  rs: ["Rust", lenguajesClike.rs], swift: ["Swift", lenguajesClike.swift], kt: ["Kotlin", lenguajesClike.kt], php: ["PHP", lenguajesClike.php],
  rb: ["Ruby", ruby], sql: ["SQL", sql], md: ["Markdown", markdown], sh: ["Shell Script", shell], bash: ["Shell Script", shell],
  yml: ["YAML", config], yaml: ["YAML", config], toml: ["TOML", config], ini: ["INI", config], env: ["Variables de entorno", config],
  gitignore: ["Ignorar Git", config], txt: ["Texto sin formato", null],
};

export function infoLenguaje(extension) {
  const e = TABLA[extension];
  return { nombre: e ? e[0] : "Texto sin formato", resaltable: Boolean(e && e[1]) };
}

export const LIMITE_RESALTADO = 200_000;

/** HTML con spans de color. Si no hay resaltado para la extensión (o el texto es enorme) devuelve el texto escapado. */
export function resaltar(texto, extension) {
  const f = TABLA[extension]?.[1];
  if (!f || texto.length > LIMITE_RESALTADO) return esc(texto);
  try { return f(texto); } catch { return esc(texto); }
}
