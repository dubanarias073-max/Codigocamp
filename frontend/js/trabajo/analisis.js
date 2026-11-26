// Detección de errores en vivo para Trabajo (los subrayados rojos/amarillos y el panel Problemas), como VS Code.
//  · JavaScript, TypeScript, CSS y JSON: los revisa Monaco; aquí se traducen sus mensajes al español.
//  · HTML: etiquetas sin cerrar, mal cerradas o que sobran (en el navegador).
//  · Python, Java, C/C++, Go, PHP, Ruby, Bash y Lua: los revisa el servidor sin ejecutar el código (/api/trabajo/analizar/).
import { api } from "/js/app.js";
import { analizarLocal } from "./analisis-local.js";

export { analizarLocal };

const DUENO = "codigocamp";
const EN_SERVIDOR = new Set(["python", "java", "c", "cpp", "go", "php", "ruby", "shell", "lua"]);
const SOLO_LOCAL = new Set(["csharp", "kotlin", "swift", "rust", "dart"]);   // sin revisión en el servidor: solo la local
const vigilados = new WeakMap();   // modelo → { completo, revisar }
// Archivos que no están abiertos: se revisan en el servidor de a uno, con pausas y hasta 60 en cola (nunca miles a la vez)
const cola = [];
let colaCorriendo = false;
function enCola(tarea) {
  if (cola.length >= 60 || cola.includes(tarea)) return;
  cola.push(tarea);
  if (colaCorriendo) return;
  colaCorriendo = true;
  (async () => {
    while (cola.length) {
      const t = cola.shift();
      try { await t(); } catch { /* sigue con el próximo */ }
      await new Promise((ok) => setTimeout(ok, 350));
    }
    colaCorriendo = false;
  })();
}

// ------------------------------------------------------------------------------------------------- HTML ----
const VACIOS = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr", "!doctype"]);
// Etiquetas que el navegador cierra solas (no son error si quedan abiertas)
const AUTOCIERRE = new Set(["p", "li", "dt", "dd", "option", "optgroup", "tr", "td", "th", "thead", "tbody", "tfoot", "rt", "rp", "colgroup", "html", "head", "body"]);

/** Problemas de etiquetas en un HTML: [{linea, columna, fin_columna, mensaje, grave}] */
export function analizarHTML(texto) {
  const problemas = [];
  const pila = [];
  const posDe = (i) => { const antes = texto.slice(0, i); const l = antes.split("\n"); return { linea: l.length, columna: l[l.length - 1].length + 1 }; };
  // Quita comentarios y el contenido de <script>/<style> (manteniendo los saltos de línea para no mover las posiciones)
  const limpio = texto.replace(/<!--[\s\S]*?-->/g, (m) => m.replace(/[^\n]/g, " "))
    .replace(/(<(script|style|textarea|title|xmp)\b(?:"[^"]*"|'[^']*'|[^>])*>)([\s\S]*?)(<\/\2\s*>)/gi, (m, a, _t, c, d) => a + c.replace(/[^\n]/g, " ") + d);
  // Los atributos pueden traer «>» entre comillas (onclick="a > b", :class="…"): se leen respetando las comillas
  const re = /<\/?([a-zA-Z][\w:.-]*|!doctype)(?=[\s/>])(?:"[^"]*"|'[^']*'|[^'">])*?(\/?)>/gi;
  let m;
  while ((m = re.exec(limpio))) {
    const nombre = m[1].toLowerCase();
    const cierre = m[0][1] === "/";
    const p = posDe(m.index);
    if (VACIOS.has(nombre)) {
      if (cierre && nombre !== "!doctype") problemas.push({ ...p, fin_columna: p.columna + m[0].length, mensaje: `<${nombre}> no lleva etiqueta de cierre: quita </${nombre}>`, grave: false });
      continue;
    }
    if (!cierre) { if (!m[2]) pila.push({ nombre, ...p, largo: m[0].length }); continue; }
    const i = pila.map((x) => x.nombre).lastIndexOf(nombre);
    if (i === -1) { problemas.push({ ...p, fin_columna: p.columna + m[0].length, mensaje: `Sobra </${nombre}>: no hay ningún <${nombre}> abierto`, grave: true }); continue; }
    for (const abierta of pila.splice(i).slice(1)) {
      if (!AUTOCIERRE.has(abierta.nombre)) problemas.push({ linea: abierta.linea, columna: abierta.columna, fin_columna: abierta.columna + abierta.largo, mensaje: `<${abierta.nombre}> no se cerró antes de </${nombre}> (línea ${p.linea})`, grave: true });
    }
  }
  for (const abierta of pila) {
    if (!AUTOCIERRE.has(abierta.nombre)) problemas.push({ linea: abierta.linea, columna: abierta.columna, fin_columna: abierta.columna + abierta.largo, mensaje: `Falta cerrar <${abierta.nombre}> (agrega </${abierta.nombre}>)`, grave: true });
  }
  for (const r of limpio.matchAll(/<img\b(?![^>]*\balt=)[^>]*>/gi)) {
    const p = posDe(r.index);
    problemas.push({ ...p, fin_columna: p.columna + 4, mensaje: "A esta imagen le falta alt=\"…\" (texto para quien no la ve)", grave: false });
  }
  return problemas.slice(0, 200);
}

// --------------------------------------------------------------------------------- mensajes en español ----
const ES = [
  [/^Cannot find name '(.+)'\. Did you mean '(.+)'\?$/, "«$1» no está definido. ¿Quisiste decir «$2»?"],
  [/^Cannot find name '(.+)'\.$/, "«$1» no está definido (¿lo escribiste bien o falta declararlo con let/const?)"],
  [/^'(.+)' expected\.$/, "Falta «$1»"],
  [/^Expression expected\.$/, "Se esperaba un valor o una expresión"],
  [/^Identifier expected\.$/, "Se esperaba un nombre"],
  [/^Declaration or statement expected\.$/, "Se esperaba una instrucción (¿sobra una llave o un paréntesis?)"],
  [/^Unterminated string literal\.$/, "Falta cerrar las comillas"],
  [/^Unterminated template literal\.$/, "Falta cerrar la comilla invertida `"],
  [/^Unexpected keyword or identifier\.$/, "Palabra inesperada aquí"],
  [/^Unexpected token\..*$/, "Símbolo inesperado"],
  [/^Cannot assign to '(.+)' because it is a constant\.$/, "«$1» es constante (const): no se puede cambiar; usa let"],
  [/^Cannot redeclare block-scoped variable '(.+)'\.$/, "«$1» ya está declarada"],
  [/^Variable '(.+)' is used before being assigned\.$/, "«$1» se usa antes de darle un valor"],
  [/^Block-scoped variable '(.+)' used before its declaration\.$/, "«$1» se usa antes de declararla"],
  [/^Expected (\d+) arguments?, but got (\d+)\.$/, "Se esperaban $1 argumentos y recibió $2"],
  [/^Property '(.+)' does not exist on type '(.+)'\. Did you mean '(.+)'\?$/, "«$1» no existe en $2. ¿Quisiste decir «$3»?"],
  [/^This condition will always return '(.+)'.*$/, "Esta condición siempre da $1"],
  [/^Unreachable code detected\.$/, "Este código nunca se ejecuta"],
  [/^'(.+)' is declared but its value is never read\.$/, "«$1» se declara pero no se usa"],
  [/^Duplicate identifier '(.+)'\.$/, "«$1» está repetido"],
  [/^Type '(.+)' is not assignable to type '(.+)'\.$/, "Un valor de tipo $1 no se puede guardar donde se espera $2"],
  [/^Argument of type '(.+)' is not assignable to parameter of type '(.+)'\.$/, "Le pasas $1, pero aquí se espera $2"],
  [/^Property '(.+)' does not exist on type '(.+)'\.$/, "«$1» no existe en $2"],
  [/^Property '(.+)' is missing in type '(.+)' but required in type '(.+)'\.$/, "Falta «$1» (es obligatorio en $3)"],
  [/^Object is possibly '(null|undefined)'\.$/, "Esto podría ser $1: revisa antes de usarlo (por ejemplo con ?.)"],
  [/^'(.+)' is possibly '(null|undefined)'\.$/, "«$1» podría ser $2: revisa antes de usarlo"],
  [/^Expected (\d+)-(\d+) arguments, but got (\d+)\.$/, "Se esperaban entre $1 y $2 argumentos y recibió $3"],
  [/^This expression is not callable\..*$/, "Esto no es una función: no se puede llamar con ( )"],
  [/^'(.+)' refers to a value, but is being used as a type here\..*$/, "«$1» es un valor, no un tipo"],
  [/^Parameter '(.+)' implicitly has an? '(.+)' type\.$/, "Al parámetro «$1» le falta el tipo (queda como $2)"],
  [/^Not all code paths return a value\.$/, "No todos los caminos devuelven un valor (return)"],
  [/^An import path can only end with a '\.ts' extension.*$/, "Importa el archivo sin la extensión .ts"],
  [/^Missing semicolon\.?$/, "Falta «;»"],
  [/^Trailing comma$/, "Sobra la coma del final"],
  [/^Property keys must be doublequoted$/, "En JSON las claves van entre comillas dobles"],
  [/^Expected comma$/, "Falta una coma"],
  [/^Colon expected$/, "Falta «:»"],
  [/^Value expected$/, "Falta un valor"],
  [/^End of file expected\.?$/, "Sobra texto al final del archivo"],
  [/^at-rule or selector expected$/, "Se esperaba un selector o una regla @ (¿sobra una «}»?)"],
  [/^colon expected$/, "Falta «:» entre la propiedad y el valor"],
  [/^semi-colon expected$/, "Falta «;»"],
  [/^\{ expected$/, "Falta «{»"],
  [/^\} expected$/, "Falta «}»"],
  [/^property value expected$/, "Falta el valor de la propiedad"],
  [/^Unknown property: '(.+)'$/, "Propiedad desconocida: «$1»"],
  [/^Do not use empty rulesets$/, "Regla vacía: no tiene propiedades"],
];
export function traducir(msg) {
  for (const [re, rep] of ES) if (re.test(msg)) return msg.replace(re, rep);
  return msg;
}

let traduciendo = false;
/** Traduce los mensajes de Monaco (TypeScript, CSS, JSON) cada vez que cambian. */
export function traducirMarcas(monaco) {
  monaco.editor.onDidChangeMarkers((uris) => {
    if (traduciendo) return;
    traduciendo = true;
    try {
      for (const uri of uris) {
        const modelo = monaco.editor.getModel(uri);
        if (!modelo) continue;
        const porDueno = new Map();
        for (const k of monaco.editor.getModelMarkers({ resource: uri })) {
          if (k.owner === DUENO) continue;
          const nuevo = traducir(k.message);
          if (!porDueno.has(k.owner)) porDueno.set(k.owner, { cambio: false, lista: [] });
          const g = porDueno.get(k.owner);
          if (nuevo !== k.message) g.cambio = true;
          g.lista.push({ ...k, message: nuevo });
        }
        for (const [dueno, g] of porDueno) if (g.cambio) monaco.editor.setModelMarkers(modelo, dueno, g.lista);
      }
    } finally { traduciendo = false; }
  });
}

// ------------------------------------------------------------------------------------------ vigilancia ----
function aMarcas(monaco, modelo, lista) {
  const n = modelo.getLineCount();
  return (lista || []).map((p) => {
    const linea = Math.min(Math.max(1, p.linea), n);
    const maxCol = modelo.getLineMaxColumn(linea);
    let ini = Math.min(Math.max(1, p.columna || 1), maxCol);
    let fin = Math.min(Math.max(ini + 1, p.fin_columna || ini + 1), maxCol);
    if (fin <= ini) {   // sin columna útil: se subraya la línea entera (sin la sangría)
      ini = modelo.getLineFirstNonWhitespaceColumn(linea) || 1; fin = maxCol;
    }
    return { severity: p.grave ? monaco.MarkerSeverity.Error : monaco.MarkerSeverity.Warning, message: p.mensaje,
      startLineNumber: linea, startColumn: ini, endLineNumber: linea, endColumn: Math.max(fin, ini + 1), source: "CódigoCamp" };
  });
}

/** Revisa un modelo cada vez que cambia (con una pausa para no revisar a cada tecla).
 *  completo=false (archivos del proyecto que no están abiertos): solo la revisión local, al instante y sin servidor.
 *  Como VS Code, la revisión completa con el compilador es para los archivos que abres: así un proyecto de miles de
 *  archivos no manda miles de peticiones al servidor (eso trababa todo lo demás, también el Conector). */
export function vigilar(monaco, modelo, ruta, { completo = true } = {}) {
  if (!modelo) return;
  const ya = vigilados.get(modelo);
  if (ya) { if (completo && !ya.completo) { ya.completo = true; ya.revisar(); } return; }
  const lang = modelo.getLanguageId();
  if (lang !== "html" && !EN_SERVIDOR.has(lang) && !SOLO_LOCAL.has(lang)) return;
  const estado = { completo, revisar: () => {} };
  vigilados.set(modelo, estado);
  let t = null, tLocal = null, version = 0, sinServidor = SOLO_LOCAL.has(lang);
  const poner = (lista) => monaco.editor.setModelMarkers(modelo, DUENO, aMarcas(monaco, modelo, lista));
  // 1) al instante y sin conexión: la revisión local
  const local = () => {
    if (modelo.isDisposed()) return null;
    const lista = lang === "html" ? analizarHTML(modelo.getValue()) : analizarLocal(modelo.getValue(), lang);
    poner(lista);
    return lista;
  };
  // 2) cuando hay servidor: la revisión completa (compilador/intérprete sin ejecutar), junto con lo local que no repite
  const revisar = async (deCola = false) => {
    if ((!estado.completo && !deCola) || modelo.isDisposed() || lang === "html" || sinServidor || !navigator.onLine) return;
    const v = ++version;
    const texto = modelo.getValue();
    let lista;
    try {
      const r = await api("/api/trabajo/analizar/", { ruta, lenguaje: lang, codigo: texto });
      if (r.problemas === null) return;   // límite de revisiones: queda la revisión local
      lista = r.problemas || [];
    } catch (e) {
      if (e?.status === 401 || e?.status === 404) sinServidor = true;
      return;   // sin conexión: queda la revisión local
    }
    if (v !== version || modelo.isDisposed() || modelo.getValue() !== texto) return;
    const lineas = new Set(lista.map((p) => p.linea));
    poner([...lista, ...analizarLocal(texto, lang).filter((p) => !lineas.has(p.linea))]);
  };
  estado.revisar = () => { void revisar(); };
  const deFondo = () => revisar(true);
  const completa = () => { if (estado.completo) void revisar(); else enCola(deFondo); };
  modelo.onDidChangeContent(() => {
    clearTimeout(t); clearTimeout(tLocal);
    tLocal = setTimeout(local, lang === "html" ? 400 : 350);
    t = setTimeout(completa, 1100);
  });
  modelo.onWillDispose(() => { clearTimeout(t); clearTimeout(tLocal); const i = cola.indexOf(deFondo); if (i >= 0) cola.splice(i, 1); });
  local();
  completa();
}
