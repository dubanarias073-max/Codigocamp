// Comandos de bash que completan la terminal de Trabajo: test/[ ], read, break/continue/return, alias, let, shift,
// sort, uniq, cut, tr, sed, awk, seq, sleep, xargs, tee, diff, rev, tac, nl, basename, dirname, du, stat, time,
// bash/sh archivo.sh, nano/vim (abren el editor) y más. Se instalan sobre COMANDOS desde shell.js.
import * as FS from "./fs.js";
import { aritmetica, coincidePatron } from "./bash.js";

const lineasDe = (t) => { const l = t.split("\n"); if (l[l.length - 1] === "") l.pop(); return l; };
const sinOp = (a) => a.filter((x) => !(x.startsWith("-") && x.length > 1));

/** Texto de los archivos dados o de la entrada (tubería). */
function entradaDe(io, nombre, archivos) {
  if (!archivos.length || (archivos.length === 1 && archivos[0] === "-")) return { texto: io.entrada ?? "", ok: true };
  const py = io.py();
  let texto = "", ok = true;
  for (const a of archivos) {
    const r = FS.resolver(io.sesion.cwd, a);
    if (r === null || !FS.tieneArchivo(py, r)) { io.err(`${nombre}: ${a}: No existe el archivo o el directorio\n`); ok = false; continue; }
    texto += py.files[r];
  }
  return { texto, ok };
}

/** Separa opciones con valor: -d ',' -f 2 / -d, / -f2 */
function leerOpciones(a, conValor) {
  const op = {}, libres = [];
  for (let i = 0; i < a.length; i += 1) {
    const x = a[i];
    if (x === "--") { libres.push(...a.slice(i + 1)); break; }
    if (/^-[A-Za-z]/.test(x) && !/^-\d/.test(x)) {
      for (let j = 1; j < x.length; j += 1) {
        const c = x[j];
        if (conValor.includes(c)) { op[c] = j + 1 < x.length ? x.slice(j + 1) : a[++i] ?? ""; break; }
        op[c] = true;
      }
    } else libres.push(x);
  }
  return { op, libres };
}

/** Rango de tr: a-z, [:upper:], \n */
function conjuntoTr(s) {
  s = s.replace(/\[:upper:\]/g, "A-Z").replace(/\[:lower:\]/g, "a-z").replace(/\[:digit:\]/g, "0-9").replace(/\[:space:\]/g, " \t\n\r")
    .replace(/\[:alpha:\]/g, "a-zA-Z").replace(/\[:alnum:\]/g, "a-zA-Z0-9").replace(/\[:punct:\]/g, "!-/:-@[-`{-~");
  s = s.replace(/\\n/g, "\n").replace(/\\t/g, "\t").replace(/\\\\/g, "\\");
  const out = [];
  for (let i = 0; i < s.length; i += 1) {
    if (s[i + 1] === "-" && i + 2 < s.length) {
      for (let c = s.charCodeAt(i); c <= s.charCodeAt(i + 2); c += 1) out.push(String.fromCharCode(c));
      i += 2;
    } else out.push(s[i]);
  }
  return out;
}

/** test / [ ] / [[ ]]: devuelve true/false o lanza error. */
function evaluarTest(args, io) {
  const py = io.py();
  const archivo = (x) => FS.resolver(io.sesion.cwd, x);
  const num = (x) => { if (!/^\s*-?\d+\s*$/.test(x)) throw new Error(`${x}: se esperaba un número entero`); return Number(x); };
  function expr(a) {
    // -o / || (menor precedencia), -a / && , ! , paréntesis
    for (const op of ["-o", "||"]) { const i = a.lastIndexOf(op); if (i > 0) return expr(a.slice(0, i)) || expr(a.slice(i + 1)); }
    for (const op of ["-a", "&&"]) { const i = a.lastIndexOf(op); if (i > 0) return expr(a.slice(0, i)) && expr(a.slice(i + 1)); }
    if (a[0] === "!") return !expr(a.slice(1));
    if (a[0] === "(" && a[a.length - 1] === ")") return expr(a.slice(1, -1));
    if (a.length === 0) return false;
    if (a.length === 1) return a[0] !== "";
    if (a.length === 2) {
      const [op, x] = a;
      const r = archivo(x);
      switch (op) {
        case "-z": return x === "";
        case "-n": return x !== "";
        case "-e": return r !== null && FS.existe(py, r);
        case "-f": return r !== null && FS.tieneArchivo(py, r);
        case "-d": return r !== null && (r === "" || FS.esCarpeta(py, r));
        case "-s": return r !== null && FS.tieneArchivo(py, r) && py.files[r].length > 0;
        case "-r": case "-w": return r !== null && FS.existe(py, r);
        case "-x": return r !== null && (FS.esCarpeta(py, r) || /\.(sh|py|js)$/.test(r) || io.sesion.binarios?.[r] !== undefined);
        default: throw new Error(`${op}: se esperaba un operador unario`);
      }
    }
    if (a.length === 3) {
      const [x, op, y] = a;
      switch (op) {
        case "=": case "==": return coincidePatron(x, y);
        case "!=": return !coincidePatron(x, y);
        case "=~": try { return new RegExp(y).test(x); } catch { return false; }
        case "<": return x < y;
        case ">": return x > y;
        case "-eq": return num(x) === num(y);
        case "-ne": return num(x) !== num(y);
        case "-lt": return num(x) < num(y);
        case "-le": return num(x) <= num(y);
        case "-gt": return num(x) > num(y);
        case "-ge": return num(x) >= num(y);
        default: throw new Error(`${op}: se esperaba un operador binario`);
      }
    }
    throw new Error("demasiados argumentos");
  }
  return expr(args);
}

/** Script de sed: s/a/b/g, Nd, /re/d, Np (con -n), y/abc/xyz/. Varios separados por ; o -e. */
function compilarSed(script) {
  const ordenes = [];
  let i = 0;
  const leerHasta = (delim) => { let t = ""; while (i < script.length && script[i] !== delim) { if (script[i] === "\\" && script[i + 1] === delim) { t += delim; i += 2; continue; } t += script[i++]; } i += 1; return t; };
  while (i < script.length) {
    while (i < script.length && /[\s;]/.test(script[i])) i += 1;
    if (i >= script.length) break;
    // dirección: N, $, /re/, N,M
    let dir = null;
    const direccion = () => {
      if (/\d/.test(script[i])) { let n = ""; while (/\d/.test(script[i])) n += script[i++]; return { n: Number(n) }; }
      if (script[i] === "$") { i += 1; return { ultima: true }; }
      if (script[i] === "/") { i += 1; return { re: new RegExp(leerHasta("/")) }; }
      return null;
    };
    const d1 = direccion();
    if (d1) { dir = { desde: d1 }; if (script[i] === ",") { i += 1; dir.hasta = direccion(); } }
    const cmd = script[i++];
    if (cmd === "s") {
      const delim = script[i++];
      const patron = leerHasta(delim), reemplazo = leerHasta(delim);
      let banderas = "";
      while (i < script.length && /[gipI0-9]/.test(script[i])) banderas += script[i++];
      ordenes.push({ dir, cmd, re: new RegExp(patron.replace(/\\\(/g, "(").replace(/\\\)/g, ")").replace(/\\\+/g, "+").replace(/\\\?/g, "?"), (banderas.includes("g") ? "g" : "") + (/[iI]/.test(banderas) ? "i" : "")),
        reemplazo: reemplazo.replace(/\\(\d)/g, "$$$1").replace(/&/g, "$$&").replace(/\\n/g, "\n"), imprimir: banderas.includes("p") });
    } else if (cmd === "y") {
      const delim = script[i++];
      const a = leerHasta(delim), b = leerHasta(delim);
      ordenes.push({ dir, cmd, a, b });
    } else if ("dpq".includes(cmd)) ordenes.push({ dir, cmd });
    else if ("aic".includes(cmd)) { let t = ""; if (script[i] === "\\") i += 1; while (i < script.length && script[i] !== ";") t += script[i++]; ordenes.push({ dir, cmd, texto: t.trim() }); }
    else throw new Error(`orden desconocida: «${cmd ?? ""}»`);
  }
  return ordenes;
}
function aplicarSed(texto, ordenes, soloImpresas) {
  const lineas = lineasDe(texto);
  const out = [];
  const activos = new Map();
  const coincide = (d, n, l, total) => d.n !== undefined ? n === d.n : d.ultima ? n === total : d.re.test(l);
  for (let k = 0; k < lineas.length; k += 1) {
    let l = lineas[k];
    const n = k + 1;
    let borrar = false, salir = false;
    const antes = [], despues = [];
    for (const [idx, o] of ordenes.entries()) {
      if (o.dir) {
        if (!o.dir.hasta) { if (!coincide(o.dir.desde, n, l, lineas.length)) continue; }
        else if (activos.get(idx)) { if (coincide(o.dir.hasta, n, l, lineas.length)) activos.delete(idx); }
        else if (coincide(o.dir.desde, n, l, lineas.length)) activos.set(idx, true);
        else continue;
      }
      if (o.cmd === "s") { const nuevo = l.replace(o.re, o.reemplazo); if (o.imprimir && nuevo !== l) out.push(nuevo); l = nuevo; }
      else if (o.cmd === "y") l = [...l].map((c) => { const j = o.a.indexOf(c); return j >= 0 ? o.b[j] ?? c : c; }).join("");
      else if (o.cmd === "d") { borrar = true; break; }
      else if (o.cmd === "p") out.push(l);
      else if (o.cmd === "q") { salir = true; break; }
      else if (o.cmd === "i") antes.push(o.texto);
      else if (o.cmd === "a") despues.push(o.texto);
      else if (o.cmd === "c") { l = o.texto; }
    }
    out.push(...antes);
    if (!borrar && !soloImpresas) out.push(l);
    out.push(...despues);
    if (salir) break;
  }
  return out.length ? out.join("\n") + "\n" : "";
}

/** awk sencillo: [-F sep] 'BEGIN{…} /re/ || NR>1 {print $1, $3; suma+=$2} END{print suma}'. */
function ejecutarAwk(programa, texto, sep, vars0 = {}) {
  const bloques = [];
  const re = /\s*(BEGIN|END)?\s*([^{]*?)\s*\{([^}]*)\}|\s*([^{]+)$/gy;
  let m;
  let i = 0;
  const p = programa.trim();
  while (i < p.length) {
    re.lastIndex = i;
    m = re.exec(p);
    if (!m || m[0] === "") break;
    if (m[4] !== undefined) bloques.push({ tipo: "", patron: m[4].trim(), accion: "print" });
    else bloques.push({ tipo: m[1] || "", patron: m[2].trim(), accion: m[3].trim() });
    i = re.lastIndex;
  }
  const vars = { ...vars0 };
  const salida = [];
  const campos = (l) => (sep === " " ? l.trim().split(/\s+/).filter(Boolean) : l.split(sep.length === 1 ? sep : new RegExp(sep)));
  let F = [], NR = 0, linea = "";
  const valor = (expr) => {
    expr = expr.trim();
    if (!expr) return "";
    // concatenación por espacios de términos simples
    const partes = expr.match(/"(?:[^"\\]|\\.)*"|\$\(?[^\s,)]+\)?|[^\s"]+/g) || [];
    if (partes.length > 1 && !/[-+*/%]/.test(expr.replace(/"(?:[^"\\]|\\.)*"/g, ""))) return partes.map(valor).join("");
    if (/^"(.*)"$/s.test(expr)) return expr.slice(1, -1).replace(/\\n/g, "\n").replace(/\\t/g, "\t").replace(/\\"/g, '"');
    if (/^\$/.test(expr)) { const k = expr.slice(1).replace(/[()]/g, ""); const n = /^\d+$/.test(k) ? Number(k) : Number(valor(k)); return n === 0 ? linea : F[n - 1] ?? ""; }
    if (expr === "NR") return String(NR);
    if (expr === "NF") return String(F.length);
    if (/^length\((.*)\)$/.test(expr)) return String(valor(/^length\((.*)\)$/.exec(expr)[1]).length);
    if (expr === "length") return String(linea.length);
    if (/^toupper\((.*)\)$/.test(expr)) return valor(/^toupper\((.*)\)$/.exec(expr)[1]).toUpperCase();
    if (/^tolower\((.*)\)$/.test(expr)) return valor(/^tolower\((.*)\)$/.exec(expr)[1]).toLowerCase();
    if (/^[A-Za-z_]\w*$/.test(expr)) return vars[expr] ?? "";
    // aritmética: sustituye campos y variables
    const num = expr.replace(/\$(\d+|NF)/g, (_, k) => { const v = k === "NF" ? F[F.length - 1] : F[Number(k) - 1]; return String(parseFloat(v) || 0); })
      .replace(/\bNR\b/g, String(NR)).replace(/\bNF\b/g, String(F.length))
      .replace(/[A-Za-z_]\w*/g, (n) => String(parseFloat(vars[n]) || 0));
    if (/^[\d\s.+\-*/%()]+$/.test(num)) { try { const r = Function(`"use strict";return (${num})`)(); return Number.isFinite(r) ? String(Math.round(r * 1e6) / 1e6) : "0"; } catch { /* nada */ } }
    return expr;
  };
  const cumple = (patron) => {
    if (!patron) return true;
    const mm = /^!?\/(.*)\/$/.exec(patron);
    if (mm) { const ok = new RegExp(mm[1]).test(linea); return patron.startsWith("!") ? !ok : ok; }
    const c = /^(.+?)\s*(==|!=|>=|<=|>|<|~)\s*(.+)$/.exec(patron);
    if (c) {
      const a = valor(c[1]), b = c[2] === "~" ? c[3].replace(/^\/|\/$/g, "") : valor(c[3]);
      const na = parseFloat(a), nb = parseFloat(b);
      const n = !Number.isNaN(na) && !Number.isNaN(nb);
      switch (c[2]) {
        case "==": return n ? na === nb : a === b; case "!=": return n ? na !== nb : a !== b;
        case ">": return n ? na > nb : a > b; case "<": return n ? na < nb : a < b;
        case ">=": return n ? na >= nb : a >= b; case "<=": return n ? na <= nb : a <= b;
        case "~": return new RegExp(b).test(a);
      }
    }
    return valor(patron) !== "" && valor(patron) !== "0";
  };
  const accion = (acc) => {
    for (const ins of acc.split(/;|\n/).map((x) => x.trim()).filter(Boolean)) {
      let mm;
      if (ins === "print" || ins === "print $0") salida.push(linea);
      else if ((mm = /^printf\s*\(?\s*("(?:[^"\\]|\\.)*")\s*(?:,(.*?))?\)?$/.exec(ins))) {
        const args = (mm[2] ? mm[2].split(",") : []).map(valor);
        let k = 0;
        salida.push({ crudo: valor(mm[1]).replace(/%-?\d*(?:\.\d+)?[sdif]/g, (f) => { const v = args[k++] ?? ""; if (/[df]/.test(f.slice(-1))) { const d = /\.(\d+)/.exec(f); return f.endsWith("d") ? String(Math.trunc(parseFloat(v) || 0)) : (parseFloat(v) || 0).toFixed(d ? Number(d[1]) : 6); } return v; }) });
      } else if ((mm = /^print\s+(.*)$/.exec(ins))) salida.push(mm[1].split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/).map(valor).join(" "));
      else if ((mm = /^([A-Za-z_]\w*)\s*(\+\+|--)$/.exec(ins))) vars[mm[1]] = String((parseFloat(vars[mm[1]]) || 0) + (mm[2] === "++" ? 1 : -1));
      else if ((mm = /^([A-Za-z_]\w*)\s*([-+*/]?=)\s*(.+)$/.exec(ins))) {
        const v = valor(mm[3]);
        const actual = parseFloat(vars[mm[1]]) || 0, nv = parseFloat(v) || 0;
        vars[mm[1]] = mm[2] === "=" ? v : String(mm[2] === "+=" ? actual + nv : mm[2] === "-=" ? actual - nv : mm[2] === "*=" ? actual * nv : actual / nv);
      }
    }
  };
  for (const b of bloques.filter((x) => x.tipo === "BEGIN")) accion(b.accion);
  for (const l of lineasDe(texto)) {
    NR += 1; linea = l; F = campos(l);
    for (const b of bloques.filter((x) => !x.tipo)) if (cumple(b.patron)) accion(b.accion || "print");
  }
  linea = ""; F = [];
  for (const b of bloques.filter((x) => x.tipo === "END")) accion(b.accion);
  return salida.map((x) => (typeof x === "string" ? x + "\n" : x.crudo)).join("");
}

/** diff de líneas (LCS) con formato unificado sencillo. */
function diffLineas(a, b, nombreA, nombreB) {
  const A = lineasDe(a), B = lineasDe(b);
  const n = A.length, m = B.length;
  if (n * m > 4_000_000) return `Los archivos ${nombreA} y ${nombreB} son distintos (demasiado grandes para mostrar el detalle)\n`;
  const t = Array.from({ length: n + 1 }, () => new Uint32Array(m + 1));
  for (let i = n - 1; i >= 0; i -= 1) for (let j = m - 1; j >= 0; j -= 1) t[i][j] = A[i] === B[j] ? t[i + 1][j + 1] + 1 : Math.max(t[i + 1][j], t[i][j + 1]);
  const out = [`\x1b[1m--- ${nombreA}\x1b[0m`, `\x1b[1m+++ ${nombreB}\x1b[0m`];
  let i = 0, j = 0;
  while (i < n || j < m) {
    if (i < n && j < m && A[i] === B[j]) { out.push(`  ${A[i]}`); i += 1; j += 1; }
    else if (j < m && (i >= n || t[i][j + 1] >= t[i + 1][j])) { out.push(`\x1b[32m+ ${B[j]}\x1b[0m`); j += 1; }
    else { out.push(`\x1b[31m- ${A[i]}\x1b[0m`); i += 1; }
  }
  return out.join("\n") + "\n";
}

export function instalarComandos(COMANDOS) {
  const C = COMANDOS;

  C.test = function test(a, io) {
    try { return evaluarTest(a, io) ? 0 : 1; } catch (e) { io.err(`test: ${e.message}\n`); return 2; }
  };
  C["["] = function corchete(a, io) {
    if (a[a.length - 1] !== "]") { io.err("[: falta «]»\n"); return 2; }
    return C.test(a.slice(0, -1), io);
  };
  C["[["] = function dobleCorchete(a, io) {
    if (a[a.length - 1] !== "]]") { io.err("[[: falta «]]»\n"); return 2; }
    return C.test(a.slice(0, -1), io);
  };
  C.let = function letCmd(a, io) {
    let r = "0";
    try { for (const e of a) r = aritmetica(e, io.sesion.vars); } catch (e) { io.err(`let: ${e.message}\n`); return 1; }
    return r !== "0" ? 0 : 1;
  };
  C.expr = function exprCmd(a, io) {
    try { const r = aritmetica(a.join(" ").replace(/\\\*/g, "*"), { ...io.sesion.vars }); io.out(r + "\n"); return r === "0" ? 1 : 0; }
    catch (e) { io.err(`expr: ${e.message}\n`); return 2; }
  };
  C.break = function romper(a, io) { io.sesion.control = { tipo: "break", n: Math.max(1, Number(a[0]) || 1) }; return 0; };
  C.continue = function seguir(a, io) { io.sesion.control = { tipo: "continue", n: Math.max(1, Number(a[0]) || 1) }; return 0; };
  C.return = function volver(a, io) { const codigo = Number(a[0] ?? io.sesion.vars["?"] ?? 0) || 0; io.sesion.control = { tipo: "return", codigo }; return codigo; };
  const salirOriginal = C.exit;
  C.exit = function salir(a, io) {
    const codigo = Number(a[0] ?? io.sesion.vars["?"] ?? 0) || 0;
    if (io.sesion.vars["0"] !== undefined && io.sesion.vars["0"] !== "bash") { io.sesion.control = { tipo: "exit", codigo }; return codigo; }
    return salirOriginal.call(this, a, io);
  };
  C.shift = function shift(a, io) {
    const v = io.sesion.vars, n = Number(a[0] ?? 1) || 1, total = Number(v["#"] ?? 0);
    for (let i = 1; i <= 20; i += 1) { const x = v[String(i + n)]; if (x === undefined || i + n > total) delete v[String(i)]; else v[String(i)] = x; }
    v["#"] = String(Math.max(0, total - n));
    return 0;
  };
  C.local = C.declare = C.typeset = C.readonly = function local(a, io) {
    for (const x of a.filter((y) => !y.startsWith("-"))) { const i = x.indexOf("="); if (i > 0) io.sesion.vars[x.slice(0, i)] = x.slice(i + 1); else io.sesion.vars[x] ??= ""; }
    return 0;
  };
  C.unset = function unset(a, io) { for (const x of a.filter((y) => !y.startsWith("-"))) { delete io.sesion.vars[x]; delete io.sesion.funciones?.[x]; } return 0; };
  C.alias = function alias(a, io) {
    io.sesion.alias ??= {};
    if (!a.length) { for (const [k, v] of Object.entries(io.sesion.alias)) io.out(`alias ${k}='${v}'\n`); return 0; }
    for (const x of a) {
      const i = x.indexOf("=");
      if (i < 0) { if (io.sesion.alias[x] === undefined) { io.err(`alias: ${x}: no se encontró\n`); return 1; } io.out(`alias ${x}='${io.sesion.alias[x]}'\n`); }
      else io.sesion.alias[x.slice(0, i)] = x.slice(i + 1);
    }
    return 0;
  };
  C.unalias = function unalias(a, io) { for (const x of a) delete io.sesion.alias?.[x]; return 0; };
  C.read = async function read(a, io) {
    const { op, libres } = leerOpciones(a, "pdn");
    const nombres = libres.length ? libres : ["REPLY"];
    let linea;
    if (io.entrada !== null && io.entrada !== undefined) {
      const ls = lineasDe(io.entrada);
      if (!ls.length) return 1;
      linea = ls[0];
    } else {
      linea = await io.sesion.leerLinea(typeof op.p === "string" ? op.p : "", { secreto: !!op.s });
      if (linea === null) return 1;
    }
    const partes = op.r ? linea.split(/\s+/) : linea.replace(/\\(.)/g, "$1").trim().split(/\s+/);
    nombres.forEach((n, i) => { io.sesion.vars[n] = i === nombres.length - 1 ? partes.slice(i).join(" ") : partes[i] ?? ""; });
    return 0;
  };
  C.seq = function seq(a, io) {
    const { op, libres } = leerOpciones(a, "s");
    const n = libres.map(Number);
    if (!n.length || n.some(Number.isNaN)) { io.err("Uso: seq [inicio [paso]] fin\n"); return 1; }
    const [ini, paso, fin] = n.length === 1 ? [1, 1, n[0]] : n.length === 2 ? [n[0], 1, n[1]] : n;
    if (!paso) { io.err("seq: el paso no puede ser 0\n"); return 1; }
    const out = [];
    for (let x = ini; paso > 0 ? x <= fin : x >= fin; x += paso) { out.push(String(Math.round(x * 1e9) / 1e9)); if (out.length > 1_000_000) break; }
    io.out(out.join(typeof op.s === "string" ? op.s : "\n") + "\n");
    return 0;
  };
  C.sleep = async function dormir(a, io) {
    const s = a.reduce((t, x) => t + (parseFloat(x) || 0) * ({ m: 60, h: 3600 }[x.slice(-1)] ?? 1), 0);
    await new Promise((r) => { const t = setTimeout(r, Math.min(s, 3600) * 1000); io.sesion.senal?.addEventListener?.("abort", () => { clearTimeout(t); r(); }, { once: true }); });
    return io.sesion.senal?.aborted ? 130 : 0;
  };
  C.sort = function sort(a, io) {
    const { op, libres } = leerOpciones(a, "tko");
    const { texto, ok } = entradaDe(io, "sort", libres);
    let ls = lineasDe(texto);
    const col = op.k ? Number(String(op.k).split(",")[0]) - 1 : -1;
    const clave = (l) => { let v = col >= 0 ? (typeof op.t === "string" ? l.split(op.t) : l.trim().split(/\s+/))[col] ?? "" : l; if (op.f) v = v.toLowerCase(); return v; };
    ls.sort((x, y) => {
      const a1 = clave(x), b1 = clave(y);
      if (op.n || op.h) { const na = parseFloat(a1) || 0, nb = parseFloat(b1) || 0; if (na !== nb) return na - nb; }
      return a1 < b1 ? -1 : a1 > b1 ? 1 : 0;
    });
    if (op.r) ls.reverse();
    if (op.u) ls = ls.filter((l, i) => i === 0 || clave(l) !== clave(ls[i - 1]));
    const salida = ls.length ? ls.join("\n") + "\n" : "";
    if (typeof op.o === "string") { const r = FS.escribirArchivo(io.py(), FS.resolver(io.sesion.cwd, op.o), salida); if (r.ok) this.cambio({ origen: "terminal" }); }
    else io.out(salida);
    return ok ? 0 : 2;
  };
  C.uniq = function uniq(a, io) {
    const { op, libres } = leerOpciones(a, "");
    const { texto, ok } = entradaDe(io, "uniq", libres);
    const grupos = [];
    for (const l of lineasDe(texto)) {
      const k = op.i ? l.toLowerCase() : l;
      if (grupos.length && grupos[grupos.length - 1].k === k) grupos[grupos.length - 1].n += 1;
      else grupos.push({ k, l, n: 1 });
    }
    for (const g of grupos) {
      if (op.d && g.n < 2) continue;
      if (op.u && g.n > 1) continue;
      io.out((op.c ? `${String(g.n).padStart(7)} ` : "") + g.l + "\n");
    }
    return ok ? 0 : 1;
  };
  C.cut = function cut(a, io) {
    const { op, libres } = leerOpciones(a, "dfc");
    const { texto, ok } = entradaDe(io, "cut", libres);
    const rango = (spec) => {
      const set = new Set();
      for (const p of String(spec).split(",")) {
        const [x, y] = p.split("-");
        const ini = x === "" ? 1 : Number(x), fin = p.includes("-") ? (y === "" ? 9999 : Number(y)) : ini;
        for (let i = ini; i <= Math.min(fin, 9999); i += 1) set.add(i);
      }
      return [...set].sort((m, n) => m - n);
    };
    if (!op.f && !op.c) { io.err("cut: debes indicar -f (campos) o -c (caracteres)\nEjemplo: cut -d ',' -f 2 datos.csv\n"); return 1; }
    const sep = typeof op.d === "string" ? op.d : "\t";
    for (const l of lineasDe(texto)) {
      if (op.c) { const r = rango(op.c); io.out(r.map((i) => l[i - 1] ?? "").join("") + "\n"); continue; }
      const campos = l.split(sep);
      if (campos.length === 1 && op.s) continue;
      io.out((campos.length === 1 ? l : rango(op.f).filter((i) => i <= campos.length).map((i) => campos[i - 1]).join(sep)) + "\n");
    }
    return ok ? 0 : 1;
  };
  C.tr = function tr(a, io) {
    const { op, libres } = leerOpciones(a, "");
    const texto = io.entrada ?? "";
    if (!libres.length) { io.err("Uso: tr [-d|-s] conjunto1 [conjunto2]\nEjemplo: echo hola | tr a-z A-Z\n"); return 1; }
    const s1 = conjuntoTr(libres[0]);
    let out = texto;
    if (op.d) out = [...out].filter((c) => !s1.includes(c)).join("");
    else if (libres[1] !== undefined) {
      const s2 = conjuntoTr(libres[1]);
      out = [...out].map((c) => { const i = s1.indexOf(c); return i < 0 ? c : s2[Math.min(i, s2.length - 1)]; }).join("");
    }
    if (op.s) { const set = conjuntoTr(libres[libres.length - 1]); out = out.replace(/(.)\1+/gs, (m, c) => (set.includes(c) ? c : m)); }
    io.out(out);
    return 0;
  };
  C.sed = function sed(a, io) {
    const scripts = [];
    let enSitio = false, soloImpresas = false;
    const archivos = [];
    for (let i = 0; i < a.length; i += 1) {
      const x = a[i];
      if (x === "-e") scripts.push(a[++i] ?? "");
      else if (x === "-i" || x.startsWith("-i")) enSitio = true;
      else if (x === "-n") soloImpresas = true;
      else if (x === "-E" || x === "-r") { /* expresiones extendidas: ya son las de JavaScript */ }
      else if (/^-[nEri]+$/.test(x)) { if (x.includes("n")) soloImpresas = true; if (x.includes("i")) enSitio = true; }
      else if (!scripts.length) scripts.push(x);
      else archivos.push(x);
    }
    if (!scripts.length) { io.err("Uso: sed 's/viejo/nuevo/g' [archivo]\n"); return 1; }
    let ordenes;
    try { ordenes = compilarSed(scripts.join(";")); } catch (e) { io.err(`sed: ${e.message}\n`); return 1; }
    if (enSitio) {
      const py = io.py();
      for (const f of archivos) {
        const r = FS.resolver(io.sesion.cwd, f);
        if (r === null || !FS.tieneArchivo(py, r)) { io.err(`sed: no se puede leer ${f}: No existe el archivo\n`); return 2; }
        FS.escribirArchivo(py, r, aplicarSed(py.files[r], ordenes, soloImpresas));
      }
      this.cambio({ origen: "terminal" });
      return 0;
    }
    const { texto, ok } = entradaDe(io, "sed", archivos);
    io.out(aplicarSed(texto, ordenes, soloImpresas));
    return ok ? 0 : 2;
  };
  C.awk = function awk(a, io) {
    const { op, libres } = leerOpciones(a, "Fv");
    const [programa, ...archivos] = libres;
    if (!programa) { io.err("Uso: awk [-F sep] '{print $1}' [archivo]\n"); return 1; }
    const vars = {};
    if (typeof op.v === "string") { const [k, ...v] = op.v.split("="); vars[k] = v.join("="); }
    const { texto, ok } = entradaDe(io, "awk", archivos);
    try { io.out(ejecutarAwk(programa, texto, typeof op.F === "string" ? op.F.replace(/\\t/g, "\t") : " ", vars)); }
    catch (e) { io.err(`awk: ${e.message}\n`); return 2; }
    return ok ? 0 : 2;
  };
  C.rev = function rev(a, io) { const { texto, ok } = entradaDe(io, "rev", sinOp(a)); for (const l of lineasDe(texto)) io.out([...l].reverse().join("") + "\n"); return ok ? 0 : 1; };
  C.tac = function tac(a, io) { const { texto, ok } = entradaDe(io, "tac", sinOp(a)); const l = lineasDe(texto).reverse(); io.out(l.length ? l.join("\n") + "\n" : ""); return ok ? 0 : 1; };
  C.nl = function nl(a, io) { const { texto, ok } = entradaDe(io, "nl", sinOp(a)); let n = 0; for (const l of lineasDe(texto)) io.out(l.trim() ? `${String(++n).padStart(6)}\t${l}\n` : "\n"); return ok ? 0 : 1; };
  C.basename = function basename(a, io) { if (!a[0]) { io.err("basename: falta un operando\n"); return 1; } let b = a[0].replace(/\/+$/, "").split("/").pop(); if (a[1] && b.endsWith(a[1])) b = b.slice(0, -a[1].length); io.out(b + "\n"); return 0; };
  C.dirname = function dirname(a, io) { if (!a[0]) { io.err("dirname: falta un operando\n"); return 1; } const s = a[0].replace(/\/+$/, ""); io.out((s.includes("/") ? s.slice(0, s.lastIndexOf("/")) || "/" : ".") + "\n"); return 0; };
  C.tee = function tee(a, io) {
    const { op, libres } = leerOpciones(a, "");
    const texto = io.entrada ?? "";
    for (const f of libres) {
      const r = FS.resolver(io.sesion.cwd, f);
      const res = r === null ? { ok: false, error: "ruta no válida" } : FS.escribirArchivo(io.py(), r, texto, { anexar: !!op.a });
      if (!res.ok) io.err(`tee: ${f}: ${res.error}\n`);
    }
    if (libres.length) this.cambio({ origen: "terminal" });
    io.out(texto);
    return 0;
  };
  C.diff = function diff(a, io) {
    const [x, y] = sinOp(a);
    if (!x || !y) { io.err("Uso: diff archivo1 archivo2\n"); return 2; }
    const py = io.py();
    const ra = FS.resolver(io.sesion.cwd, x), rb = FS.resolver(io.sesion.cwd, y);
    if (ra === null || !FS.tieneArchivo(py, ra)) { io.err(`diff: ${x}: No existe el archivo\n`); return 2; }
    if (rb === null || !FS.tieneArchivo(py, rb)) { io.err(`diff: ${y}: No existe el archivo\n`); return 2; }
    if (py.files[ra] === py.files[rb]) return 0;
    io.out(diffLineas(py.files[ra], py.files[rb], x, y));
    return 1;
  };
  C.xargs = async function xargs(a, io) {
    const { op, libres } = leerOpciones(a, "nI");
    const palabras = (io.entrada ?? "").split(typeof op.I === "string" ? /\n/ : /\s+/).filter(Boolean);
    const cmd = libres.length ? libres : ["echo"];
    const q = (s) => `'${s.replace(/'/g, "'\\''")}'`;
    let codigo = 0;
    if (typeof op.I === "string") {
      for (const w of palabras) codigo = await this.ejecutar(cmd.map((c) => q(c.split(op.I).join(w))).join(" "), Object.assign(Object.create(io.sesion), { out: io.out, err: io.err }));
      return codigo;
    }
    const n = Number(op.n) || palabras.length || 1;
    for (let i = 0; i < Math.max(1, palabras.length); i += n) {
      codigo = await this.ejecutar([...cmd, ...palabras.slice(i, i + n)].map(q).join(" "), Object.assign(Object.create(io.sesion), { out: io.out, err: io.err }));
    }
    return codigo;
  };
  C.time = async function tiempo(a, io) {
    const t0 = performance.now();
    const q = (s) => `'${s.replace(/'/g, "'\\''")}'`;
    const codigo = a.length ? await this.ejecutar(a.map(q).join(" "), Object.assign(Object.create(io.sesion), { out: io.out, err: io.err })) : 0;
    const s = (performance.now() - t0) / 1000;
    io.err(`\nreal\t${Math.floor(s / 60)}m${(s % 60).toFixed(3)}s\n`);
    return codigo;
  };
  C.yes = function yes(a, io) { io.out(Array(1000).fill(a.join(" ") || "y").join("\n") + "\n"); return 0; };
  C.du = function du(a, io) {
    const py = io.py();
    const objetivos = sinOp(a).length ? sinOp(a) : ["."];
    const humano = a.some((x) => /^-\w*h/.test(x));
    const fmt = (b) => (humano ? (b < 1024 ? `${b}B` : b < 1048576 ? `${(b / 1024).toFixed(1)}K` : `${(b / 1048576).toFixed(1)}M`) : String(Math.ceil(b / 1024)));
    for (const o of objetivos) {
      const r = FS.resolver(io.sesion.cwd, o);
      if (r === null || !FS.existe(py, r)) { io.err(`du: ${o}: No existe el archivo o el directorio\n`); continue; }
      const archivos = FS.tieneArchivo(py, r) ? [r] : FS.archivosEn(py, r);
      const total = archivos.reduce((t, f) => t + new TextEncoder().encode(py.files[f] ?? "").length, 0);
      io.out(`${fmt(total)}\t${o}\n`);
    }
    return 0;
  };
  C.stat = function stat(a, io) {
    const py = io.py();
    for (const o of sinOp(a)) {
      const r = FS.resolver(io.sesion.cwd, o);
      if (r === null || !FS.existe(py, r)) { io.err(`stat: ${o}: No existe el archivo\n`); return 1; }
      const archivo = FS.tieneArchivo(py, r);
      io.out(`  Archivo: ${o}\n   Tamaño: ${archivo ? new TextEncoder().encode(py.files[r]).length : 0} bytes\n     Tipo: ${archivo ? "archivo normal" : "directorio"}\n`);
    }
    return 0;
  };
  C.chmod = function chmod(a, io) {
    if (sinOp(a).length < 2) { io.err("Uso: chmod +x archivo.sh\n"); return 1; }
    return 0;   // en tu proyecto todos los .sh ya se pueden ejecutar con ./archivo.sh
  };
  C.bash = C.sh = C.zsh = async function bash(a, io) {
    if (a[0] === "-c") return this.ejecutar(a[1] ?? "", Object.assign(Object.create(io.sesion), { out: io.out, err: io.err, control: null }));
    const libres = a.filter((x) => !/^-[a-z]$/.test(x));
    if (!libres.length) { io.out("Ya estás en bash 🙂 (escribe comandos directamente)\n"); return 0; }
    const r = FS.resolver(io.sesion.cwd, libres[0]);
    if (r === null || !FS.tieneArchivo(io.py(), r)) { io.err(`bash: ${libres[0]}: No existe el archivo o el directorio\n`); return 127; }
    return this.correrScript(r, libres.slice(1), io);
  };
  const abrirEditor = function abrir(a, io) {
    if (!a.length) { io.err("Indica el archivo: nano archivo.txt (se abre en el editor de Trabajo)\n"); return 1; }
    return C.code.call(this, a.filter((x) => !x.startsWith("-") && !x.startsWith("+")), io);
  };
  for (const n of ["nano", "vim", "vi", "nvim", "emacs", "notepad", "gedit", "subl", "open", "start", "xdg-open", "explorer"]) C[n] = abrirEditor;
  C.less = C.more = C.bat = function paginar(a, io) { return C.cat.call(this, a.filter((x) => !x.startsWith("-")), io); };
  C.man = function man(a, io) {
    if (!a[0]) { io.err("¿Qué manual quieres ver? Ejemplo: man ls\n"); return 1; }
    io.out(`${a[0]}: escribe «help» para ver lo que hace cada comando de esta terminal, o pregúntale a la IA (Ctrl+I).\n`);
    return 0;
  };
  C.ps = function ps(a, io) { io.out("  PID TTY          TIME CMD\n    1 pts/0    00:00:00 bash\n"); return 0; };
  C.kill = function kill(a, io) { io.err("kill: no hay procesos en segundo plano en esta terminal (detén un programa con Ctrl+C)\n"); return 1; };
  C.uname = function uname(a, io) { io.out(a.includes("-a") ? "CodigoCamp 1.0 navegador x86_64 GNU/Linux\n" : "Linux\n"); return 0; };
  C.hostname = function hostname(a, io) { io.out("codigocamp\n"); return 0; };
  C.cal = function cal(a, io) {
    const h = new Date(), y = h.getFullYear(), m = h.getMonth();
    const nombre = h.toLocaleString("es", { month: "long" });
    const dias = new Date(y, m + 1, 0).getDate(), ini = (new Date(y, m, 1).getDay() + 6) % 7;
    let t = `   ${nombre} ${y}\nlu ma mi ju vi sá do\n` + "   ".repeat(ini);
    for (let d = 1; d <= dias; d += 1) { const s = String(d).padStart(2); t += d === h.getDate() ? `\x1b[7m${s}\x1b[0m` : s; t += (ini + d) % 7 === 0 ? "\n" : " "; }
    io.out(t.trimEnd() + "\n");
    return 0;
  };
  C.history = ((viejo) => function history(a, io) {
    if (a[0] === "-c") { io.sesion.historial.length = 0; io.sesion.borrarHistorial?.(); return 0; }
    return viejo.call(this, a, io);
  })(C.history);
}
