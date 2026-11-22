// Lo que hace que la terminal se sienta como bash de verdad:
//  · Estructuras: for … in …; do …; done · for ((i=0; i<5; i++)) · while / until · if / elif / else / fi
//    · case … in … esac · funciones nombre() { …; }
//  · Expansiones: $((aritmética)), $(comando) y `comando`, $1…$9 $# $@ $*
//  · ¿La línea está incompleta? (para pedir más con «>» como bash)
// Todo es puro (sin DOM): la shell lo usa en Shell.ejecutar.

const ABREN = new Set(["for", "while", "until", "if", "case", "select"]);
const CIERRAN = { done: ["for", "while", "until", "select"], fi: ["if"], esac: ["case"] };

/** Recorre el texto marcando qué partes están entre comillas. Llama f(i, c, enComillas, enSimples). */
function recorrer(texto, f) {
  let simples = false, dobles = false;
  for (let i = 0; i < texto.length; i += 1) {
    const c = texto[i];
    if (!simples && c === "\\") { f(i, c, true, false); i += 1; continue; }
    if (!dobles && c === "'") { simples = !simples; f(i, c, true, true); continue; }
    if (!simples && c === '"') { dobles = !dobles; f(i, c, true, false); continue; }
    if (f(i, c, simples || dobles, simples) === false) return { simples, dobles, cortado: true };
  }
  return { simples, dobles };
}

/** Palabras «de control» (fuera de comillas) con su posición. */
function palabrasControl(texto) {
  const out = [];
  let ini = -1, inicioComando = true, prev = "";
  const cerrar = (fin) => {
    if (ini < 0) return;
    const w = texto.slice(ini, fin);
    out.push({ w, ini, fin, inicioComando: inicioComando });
    inicioComando = ["do", "then", "else", "elif", "in", "{", "!", "time"].includes(w);
    ini = -1;
  };
  recorrer(texto, (i, c, comillas) => {
    if (comillas) { if (ini < 0) ini = i; return; }
    if (/\s/.test(c)) { cerrar(i); if (c === "\n") inicioComando = true; return; }
    if (c === ";" || c === "&" || c === "|" || c === "(" || c === ")") {
      cerrar(i);
      if (c === ")" && prev === "(") { /* nombre() */ }
      inicioComando = true;
      out.push({ w: c, ini: i, fin: i + 1, op: true });
      prev = c;
      return;
    }
    if (ini < 0) ini = i;
    prev = c;
  });
  cerrar(texto.length);
  return out;
}

/** Profundidad de bloques abiertos (for/while/if/case/{ }) al final del texto. */
function profundidad(texto) {
  let d = 0, llaves = 0;
  for (const p of palabrasControl(texto)) {
    if (p.op) continue;
    if (p.inicioComando && ABREN.has(p.w)) d += 1;
    else if (p.inicioComando && CIERRAN[p.w]) d -= 1;
    else if (p.w === "{" && p.inicioComando) llaves += 1;
    else if (p.w === "}" && p.inicioComando) llaves -= 1;
  }
  return d + llaves;
}

/** ¿Falta algo para que la línea esté completa? (comillas abiertas, bloque sin cerrar, termina en | && || \). */
export function incompleta(texto) {
  const r = recorrer(texto, () => {});
  if (r.simples || r.dobles) return true;
  if (/\\\s*$/.test(texto)) return true;
  if (/(\|\||&&|\|)\s*$/.test(texto.replace(/#[^\n'"]*$/, ""))) return true;
  return profundidad(texto) > 0;
}

/** Divide en sentencias de primer nivel (por ; y saltos de línea), sin cortar dentro de bloques ni comillas. */
export function sentencias(texto) {
  const out = [];
  let d = 0, llaves = 0, desde = 0, parens = 0;
  const marcas = palabrasControl(texto);
  for (const p of marcas) {
    if (p.op) {
      if (p.w === "(") parens += 1;
      else if (p.w === ")") parens -= 1;
      else if (p.w === ";" && d === 0 && llaves === 0 && parens <= 0 && texto[p.ini + 1] !== ";") { out.push(texto.slice(desde, p.ini)); desde = p.fin; }
      continue;
    }
    if (p.inicioComando && ABREN.has(p.w)) d += 1;
    else if (p.inicioComando && CIERRAN[p.w]) d -= 1;
    else if (p.w === "{" && p.inicioComando) llaves += 1;
    else if (p.w === "}" && p.inicioComando) llaves -= 1;
  }
  out.push(texto.slice(desde));
  // Los saltos de línea también separan (fuera de bloques)
  const final = [];
  for (const s of out) {
    let d2 = 0, ll = 0, ini = 0;
    const lineas = [];
    const marc = palabrasControl(s);
    const cortes = [];
    recorrer(s, (i, c, comillas) => { if (!comillas && c === "\n") cortes.push(i); });
    let k = 0;
    for (const corte of cortes) {
      while (k < marc.length && marc[k].ini < corte) {
        const p = marc[k++];
        if (p.op) continue;
        if (p.inicioComando && ABREN.has(p.w)) d2 += 1;
        else if (p.inicioComando && CIERRAN[p.w]) d2 -= 1;
        else if (p.w === "{" && p.inicioComando) ll += 1;
        else if (p.w === "}" && p.inicioComando) ll -= 1;
      }
      if (d2 === 0 && ll === 0) { lineas.push(s.slice(ini, corte)); ini = corte + 1; }
    }
    lineas.push(s.slice(ini));
    final.push(...lineas);
  }
  return final.map((x) => x.trim()).filter((x) => x && !x.startsWith("#"));
}

/** Busca la palabra de control `w` de primer nivel (dentro de la sentencia) a partir de `desde`. */
function buscar(texto, palabras, desde = 0) {
  let d = 0;
  for (const p of palabrasControl(texto)) {
    if (p.ini < desde || p.op) continue;
    if (d === 0 && palabras.includes(p.w) && p.inicioComando) return p;
    if (p.inicioComando && ABREN.has(p.w)) d += 1;
    else if (p.inicioComando && CIERRAN[p.w]) d -= 1;
  }
  return null;
}

const limpiar = (s) => s.trim().replace(/^;+|;+$/g, "").trim();

/** Qué tipo de sentencia es. */
export function analizar(s) {
  const t = s.trim();
  let m;
  if ((m = /^([A-Za-z_][\w-]*)\s*\(\)\s*\{([\s\S]*)\}\s*$/.exec(t)) || (m = /^function\s+([A-Za-z_][\w-]*)\s*(?:\(\))?\s*\{([\s\S]*)\}\s*$/.exec(t))) {
    return { tipo: "funcion", nombre: m[1], cuerpo: limpiar(m[2]) };
  }
  if ((m = /^\{([\s\S]*)\}\s*$/.exec(t))) return { tipo: "grupo", cuerpo: limpiar(m[1]) };
  if ((m = /^for\s*\(\((.*?)\)\)\s*;?\s*do\b([\s\S]*)\bdone\s*$/.exec(t))) {
    const [ini, cond, paso] = m[1].split(";").map((x) => x.trim());
    return { tipo: "forc", ini, cond, paso, cuerpo: limpiar(m[2]) };
  }
  if (/^for\s/.test(t)) {
    const hacer = buscar(t, ["do"], 3);
    if (!hacer || !/\bdone\s*$/.test(t)) return { tipo: "error", error: "for: falta «do … done»" };
    const cab = t.slice(3, hacer.ini).trim().replace(/;\s*$/, "");
    const mm = /^([A-Za-z_]\w*)(?:\s+in\s+([\s\S]*))?$/.exec(cab);
    if (!mm) return { tipo: "error", error: "for: usa «for x in a b c; do …; done»" };
    return { tipo: "for", variable: mm[1], lista: mm[2] ?? '"$@"', cuerpo: limpiar(t.slice(hacer.fin, t.lastIndexOf("done"))) };
  }
  if ((m = /^(while|until)\s/.exec(t))) {
    const hacer = buscar(t, ["do"], m[1].length);
    if (!hacer || !/\bdone\s*$/.test(t)) return { tipo: "error", error: `${m[1]}: falta «do … done»` };
    return { tipo: m[1], cond: limpiar(t.slice(m[1].length, hacer.ini)), cuerpo: limpiar(t.slice(hacer.fin, t.lastIndexOf("done"))) };
  }
  if (/^if\s/.test(t)) {
    if (!/\bfi\s*$/.test(t)) return { tipo: "error", error: "if: falta «fi»" };
    const ramas = [];
    let pos = 2, cond = null, otro = null;
    for (;;) {
      const entonces = buscar(t, ["then"], pos);
      if (!entonces) return { tipo: "error", error: "if: falta «then»" };
      cond = limpiar(t.slice(pos, entonces.ini));
      const sig = buscar(t, ["elif", "else", "fi"], entonces.fin);
      if (!sig) return { tipo: "error", error: "if: falta «fi»" };
      ramas.push({ cond, cuerpo: limpiar(t.slice(entonces.fin, sig.ini)) });
      if (sig.w === "elif") { pos = sig.fin; continue; }
      if (sig.w === "else") { const fin = t.lastIndexOf("fi"); otro = limpiar(t.slice(sig.fin, fin)); }
      break;
    }
    return { tipo: "if", ramas, otro };
  }
  if ((m = /^case\s+([\s\S]+?)\s+in\b([\s\S]*)\besac\s*$/.exec(t))) {
    const casos = [];
    for (const bloque of m[2].split(/;;/)) {
      const b = bloque.trim();
      if (!b) continue;
      const mm = /^\(?([^)]*)\)([\s\S]*)$/.exec(b);
      if (mm) casos.push({ patrones: mm[1].split("|").map((x) => x.trim()), cuerpo: limpiar(mm[2]) });
    }
    return { tipo: "case", palabra: m[1], casos };
  }
  if ((m = /^\(\(([\s\S]*)\)\)$/.exec(t))) return { tipo: "aritmetica", expr: m[1] };
  return { tipo: "simple", texto: t };
}

/** ¿Un patrón de case/[[ == ]] (con * ? [..]) coincide? */
export function coincidePatron(texto, patron) {
  const re = "^" + patron.replace(/[.+^${}()|\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, ".") + "$";
  try { return new RegExp(re).test(texto); } catch { return texto === patron; }
}

// ------------------------------------------------------------ aritmética $(( )) ----
/** Evalúa aritmética entera de bash (con asignaciones: i++, x+=2, y=x*3). vars se modifica. */
export function aritmetica(expr, vars) {
  const toks = [];
  const re = /\s*(?:(\d+)|([A-Za-z_]\w*)|(\*\*=?|<<=?|>>=?|\+\+|--|[-+*/%&|^]=|==|!=|<=|>=|&&|\|\||[-+*/%<>=!~&|^?:(),]))/y;
  let m;
  re.lastIndex = 0;
  const limpio = expr.trim();
  while (re.lastIndex < limpio.length) {
    m = re.exec(limpio);
    if (!m) throw new Error(`error de sintaxis en la expresión: «${limpio.slice(re.lastIndex)}»`);
    if (m[1]) toks.push({ n: BigInt(m[1]) });
    else if (m[2]) toks.push({ id: m[2] });
    else toks.push({ op: m[3] });
  }
  let i = 0;
  const ver = () => toks[i];
  const tomar = (op) => { if (ver()?.op === op) { i += 1; return true; } return false; };
  const leer = (id) => { const v = String(vars[id] ?? "0").trim(); return /^-?\d+$/.test(v) ? BigInt(v) : 0n; };
  const N = (b) => (b ? 1n : 0n);
  const PREC = [["||"], ["&&"], ["|"], ["^"], ["&"], ["==", "!="], ["<", "<=", ">", ">="], ["<<", ">>"], ["+", "-"], ["*", "/", "%"]];
  const binario = (a, op, b) => {
    switch (op) {
      case "+": return a + b; case "-": return a - b; case "*": return a * b;
      case "/": if (b === 0n) throw new Error("división por cero"); return a / b;
      case "%": if (b === 0n) throw new Error("división por cero"); return a % b;
      case "**": return b < 0n ? 0n : a ** b;
      case "<": return N(a < b); case "<=": return N(a <= b); case ">": return N(a > b); case ">=": return N(a >= b);
      case "==": return N(a === b); case "!=": return N(a !== b);
      case "&&": return N(a !== 0n && b !== 0n); case "||": return N(a !== 0n || b !== 0n);
      case "&": return a & b; case "|": return a | b; case "^": return a ^ b; case "<<": return a << b; case ">>": return a >> b;
      default: throw new Error(`operador desconocido ${op}`);
    }
  };
  function primario() {
    const t = ver();
    if (!t) throw new Error("expresión incompleta");
    if (t.op === "(") { i += 1; const v = coma(); if (!tomar(")")) throw new Error("falta «)»"); return v; }
    if (t.op === "-" || t.op === "+" || t.op === "!" || t.op === "~") { i += 1; const v = unario(); return t.op === "-" ? -v : t.op === "+" ? v : t.op === "!" ? N(v === 0n) : ~v; }
    if (t.op === "++" || t.op === "--") { i += 1; const id = ver()?.id; if (!id) throw new Error(`${t.op} necesita una variable`); i += 1; const v = leer(id) + (t.op === "++" ? 1n : -1n); vars[id] = String(v); return v; }
    if (t.n !== undefined) { i += 1; return t.n; }
    if (t.id) {
      i += 1;
      if (ver()?.op === "++" || ver()?.op === "--") { const op = toks[i++].op; const v = leer(t.id); vars[t.id] = String(v + (op === "++" ? 1n : -1n)); return v; }
      return leer(t.id);
    }
    throw new Error(`error de sintaxis cerca de «${t.op}»`);
  }
  function unario() { return potencia(); }
  function potencia() { const a = primario(); if (tomar("**")) return binario(a, "**", unario()); return a; }
  function nivel(n) {
    if (n >= PREC.length) return potencia();
    let a = nivel(n + 1);
    for (;;) {
      const op = ver()?.op;
      if (!op || !PREC[n].includes(op)) return a;
      i += 1;
      a = binario(a, op, nivel(n + 1));
    }
  }
  function ternario() {
    const c = nivel(0);
    if (tomar("?")) { const a = asignacion(); if (!tomar(":")) throw new Error("falta «:»"); const b = asignacion(); return c !== 0n ? a : b; }
    return c;
  }
  function asignacion() {
    const t = ver(), sig = toks[i + 1];
    if (t?.id && sig?.op && /^(=|\+=|-=|\*=|\/=|%=|\*\*=|<<=|>>=|&=|\|=|\^=)$/.test(sig.op)) {
      i += 2;
      const v = asignacion();
      const r = sig.op === "=" ? v : binario(leer(t.id), sig.op.slice(0, -1), v);
      vars[t.id] = String(r);
      return r;
    }
    return ternario();
  }
  function coma() { let v = asignacion(); while (tomar(",")) v = asignacion(); return v; }
  if (!toks.length) return "0";
  const v = coma();
  if (i < toks.length) throw new Error(`error de sintaxis cerca de «${toks[i].op ?? toks[i].id ?? toks[i].n}»`);
  return String(v);
}

/** Busca el cierre de $( … ) o $(( … )) teniendo en cuenta comillas y paréntesis anidados. */
function cierre(texto, desde, doble) {
  let d = doble ? 2 : 1;
  let i = desde;
  let simples = false, dobles = false;
  while (i < texto.length) {
    const c = texto[i];
    if (c === "\\" && !simples) { i += 2; continue; }
    if (c === "'" && !dobles) simples = !simples;
    else if (c === '"' && !simples) dobles = !dobles;
    else if (!simples && !dobles) {
      if (c === "(") d += 1;
      else if (c === ")") { d -= 1; if (d === 0) return i; }
    }
    i += 1;
  }
  return -1;
}

const ESCAPAR_FUERA = /[\\'"$`;&|<>()#*?\[\]{}]/g;
const ESCAPAR_DENTRO = /[\\"$`]/g;

/**
 * Expande $((…)), $(…), `…` y $1…$9/$#/$@/$* antes de que la shell divida la línea en palabras.
 * correr(cmd) → Promise<string> con la salida del comando (subshell).
 */
export async function expandirLinea(linea, vars, correr) {
  let out = "";
  let simples = false, dobles = false;
  for (let i = 0; i < linea.length; i += 1) {
    const c = linea[i];
    if (c === "\\" && !simples) { out += c + (linea[i + 1] ?? ""); i += 1; continue; }
    if (c === "'" && !dobles) { simples = !simples; out += c; continue; }
    if (c === '"' && !simples) { dobles = !dobles; out += c; continue; }
    if (simples) { out += c; continue; }
    const esc = (t) => t.replace(dobles ? ESCAPAR_DENTRO : ESCAPAR_FUERA, "\\$&");
    if (c === "$" && linea.startsWith("$((", i)) {
      const j = cierre(linea, i + 3, true);
      if (j > 0 && linea[j - 1] === ")") {
        const dentro = await expandirLinea(linea.slice(i + 3, j - 1), vars, correr);
        out += aritmetica(dentro.replace(/\$\{?([A-Za-z_]\w*)\}?/g, (_, n) => vars[n] ?? "0").replace(/\\(.)/g, "$1"), vars);
        i = j;
        continue;
      }
    }
    if (c === "$" && linea[i + 1] === "(") {
      const j = cierre(linea, i + 2, false);
      if (j < 0) throw new Error("falta «)» en $( … )");
      const r = (await correr(linea.slice(i + 2, j))).replace(/\n+$/, "");
      out += esc(r);
      i = j;
      continue;
    }
    if (c === "`") {
      const j = linea.indexOf("`", i + 1);
      if (j < 0) throw new Error("comilla invertida (`) sin cerrar");
      const r = (await correr(linea.slice(i + 1, j))).replace(/\n+$/, "");
      out += esc(r);
      i = j;
      continue;
    }
    if (c === "$" && /[0-9#@*$]/.test(linea[i + 1] ?? "")) {
      const k = linea[i + 1];
      const pos = Number(vars["#"] ?? 0);
      const args = Array.from({ length: pos }, (_, n) => vars[String(n + 1)] ?? "");
      let v;
      if (k === "#") v = String(pos);
      else if (k === "$") v = "4242";
      else if (k === "@" || k === "*") {
        if (k === "@" && dobles) { out += args.map((x) => x.replace(ESCAPAR_DENTRO, "\\$&")).join('" "'); i += 1; continue; }
        v = args.join(" ");
      } else v = vars[k] ?? "";
      out += esc(v);
      i += 1;
      continue;
    }
    if (c === "$" && linea[i + 1] === "{") {
      // ${#var}, ${var:-defecto}, ${var:=x}, ${var#pre}, ${var%suf}, ${var/a/b}, ${var^^}, ${var,,}
      const j = linea.indexOf("}", i + 2);
      if (j > 0) {
        const dentro = linea.slice(i + 2, j);
        const r = parametro(dentro, vars);
        if (r !== null) { out += esc(r); i = j; continue; }
      }
    }
    out += c;
  }
  return out;
}

function parametro(d, vars) {
  let m;
  if ((m = /^#([A-Za-z_]\w*)$/.exec(d))) return String((vars[m[1]] ?? "").length);
  if ((m = /^([A-Za-z_]\w*|\d)(:?[-=+?])(.*)$/.exec(d))) {
    const v = vars[m[1]];
    const vacio = m[2].startsWith(":") ? !v : v === undefined;
    const op = m[2].slice(-1);
    if (op === "-") return vacio ? m[3] : v;
    if (op === "=") { if (vacio) vars[m[1]] = m[3]; return vars[m[1]]; }
    if (op === "+") return vacio ? "" : m[3];
    return vacio ? "" : v;
  }
  if ((m = /^([A-Za-z_]\w*):(-?\d+)(?::(\d+))?$/.exec(d))) {
    const v = vars[m[1]] ?? "";
    const ini = Number(m[2]) < 0 ? Math.max(0, v.length + Number(m[2])) : Number(m[2]);
    return m[3] !== undefined ? v.substr(ini, Number(m[3])) : v.slice(ini);
  }
  if ((m = /^([A-Za-z_]\w*)(\^\^|,,|\^|,)$/.exec(d))) {
    const v = vars[m[1]] ?? "";
    return m[2] === "^^" ? v.toUpperCase() : m[2] === ",," ? v.toLowerCase() : m[2] === "^" ? v.charAt(0).toUpperCase() + v.slice(1) : v.charAt(0).toLowerCase() + v.slice(1);
  }
  if ((m = /^([A-Za-z_]\w*)(##?|%%?)(.+)$/.exec(d))) {
    const v = vars[m[1]] ?? "";
    const pat = m[3].replace(/[.+^${}()|\\]/g, "\\$&").replace(/\?/g, ".").replace(/\*/g, m[2].length === 2 ? ".*" : ".*?");
    const re = m[2][0] === "#" ? new RegExp("^" + pat) : new RegExp(pat + "$");
    if (m[2] === "%") { for (let k = v.length; k >= 0; k -= 1) if (new RegExp("^" + pat + "$").test(v.slice(k))) return v.slice(0, k); return v; }
    return v.replace(re, "");
  }
  if ((m = /^([A-Za-z_]\w*)\/(\/?)([^/]*)\/(.*)$/.exec(d))) {
    const v = vars[m[1]] ?? "";
    return m[2] ? v.split(m[3]).join(m[4]) : v.replace(m[3], m[4]);
  }
  if ((m = /^([A-Za-z_]\w*)$/.exec(d))) return vars[m[1]] ?? "";
  return null;
}
