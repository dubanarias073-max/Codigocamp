// Intérprete de comandos de la terminal de Trabajo.
// Es una shell «de verdad» sobre el proyecto: comillas, variables, comodines, pipes (|), encadenado (; && ||)
// y redirecciones (> >>). Los comandos actúan sobre los archivos reales del proyecto (el sistema de archivos virtual).
// No toca el DOM: la terminal le pasa una «sesión» con funciones para escribir y leer.
import { color, quitarAnsi } from "./ansi.js";
import * as FS from "./fs.js";
import { ejecutarGit } from "./git.js";

// ---------------------------------------------------------------- análisis ----
function expandirVariable(linea, i, vars) {
  // linea[i] === "$"
  const resto = linea.slice(i + 1);
  let m = /^\{([A-Za-z_]\w*)\}/.exec(resto) || /^([A-Za-z_]\w*)/.exec(resto);
  if (m) return [vars[m[1]] ?? "", m[0].length + 1];
  if (resto[0] === "?") return [String(vars["?"] ?? 0), 2];
  return ["$", 1];
}

/** Divide una línea en palabras y operadores. Devuelve { tokens } o { error }. */
export function tokenizar(linea, vars = {}) {
  const tokens = [];
  let actual = null;
  const cerrar = () => { if (actual) { tokens.push({ t: "w", v: actual.v, glob: actual.glob }); actual = null; } };
  const anadir = (txt, glob = false) => { actual ??= { v: "", glob: false }; actual.v += txt; if (glob) actual.glob = true; };
  let i = 0;
  while (i < linea.length) {
    const c = linea[i];
    if (c === "'") {
      const j = linea.indexOf("'", i + 1);
      if (j < 0) return { error: "comillas simples sin cerrar" };
      anadir(linea.slice(i + 1, j));
      i = j + 1;
    } else if (c === '"') {
      let j = i + 1;
      let txt = "";
      while (j < linea.length && linea[j] !== '"') {
        if (linea[j] === "\\" && '"\\$`'.includes(linea[j + 1] ?? "\0")) { txt += linea[j + 1]; j += 2; }
        else if (linea[j] === "$") { const [v, largo] = expandirVariable(linea, j, vars); txt += v; j += largo; }
        else { txt += linea[j]; j += 1; }
      }
      if (j >= linea.length) return { error: "comillas dobles sin cerrar" };
      anadir(txt);
      i = j + 1;
    } else if (c === "\\") {
      anadir(linea[i + 1] ?? "");
      i += 2;
    } else if (c === "$") {
      const [v, largo] = expandirVariable(linea, i, vars);
      anadir(v);
      i += largo;
    } else if (/\s/.test(c)) {
      cerrar();
      i += 1;
    } else if (c === "#" && !actual) {
      break;
    } else if (c === "&" || c === "|" || c === ";" || c === ">" || c === "<") {
      cerrar();
      const doble = linea.slice(i, i + 2);
      if (c === "<") return { error: "la redirección de entrada (<) no está disponible" };
      if (doble === "&&" || doble === "||" || doble === ">>") { tokens.push({ t: "op", v: doble }); i += 2; }
      else if (c === "&") return { error: "los procesos en segundo plano (&) no están disponibles" };
      else { tokens.push({ t: "op", v: c }); i += 1; }
    } else {
      anadir(c, c === "*" || c === "?");
      i += 1;
    }
  }
  cerrar();
  return { tokens };
}

/** Agrupa los tokens en [{ conector, etapas: [{ palabras, redir }] }]. */
function analizar(tokens) {
  const lista = [];
  let conector = ";";
  let etapas = [{ palabras: [], redir: null }];
  const vacia = (e) => !e.palabras.length;
  for (let i = 0; i < tokens.length; i += 1) {
    const tk = tokens[i];
    const etapa = etapas[etapas.length - 1];
    if (tk.t === "w") etapa.palabras.push(tk);
    else if (tk.v === "|") {
      if (vacia(etapa)) return { error: "error de sintaxis cerca de «|»" };
      etapas.push({ palabras: [], redir: null });
    } else if (tk.v === ">" || tk.v === ">>") {
      const destino = tokens[i + 1];
      if (!destino || destino.t !== "w") return { error: `error de sintaxis: falta el archivo después de «${tk.v}»` };
      etapa.redir = { anexar: tk.v === ">>", palabra: destino };
      i += 1;
    } else {
      if (vacia(etapa)) return { error: `error de sintaxis cerca de «${tk.v}»` };
      lista.push({ conector, etapas });
      conector = tk.v;
      etapas = [{ palabras: [], redir: null }];
    }
  }
  const ultima = etapas[etapas.length - 1];
  if (vacia(ultima)) {
    if (etapas.length > 1 || ultima.redir || (conector !== ";" && lista.length)) return { error: "error de sintaxis: línea incompleta" };
  } else lista.push({ conector, etapas });
  return { lista };
}

// ------------------------------------------------------------------ utilidades ----
const NO_EXISTE = "No existe el archivo o el directorio";
const sinColor = (t) => quitarAnsi(t);
const largoVisible = (t) => sinColor(t).length;
const nombreDir = (n) => color.azul(n);

/** Acomoda nombres en columnas como hace `ls`. */
export function enColumnas(nombres, ancho = 80) {
  if (!nombres.length) return "";
  const anchos = nombres.map(largoVisible);
  for (let cols = Math.min(nombres.length, Math.max(1, Math.floor(ancho / 3))); cols >= 1; cols -= 1) {
    const filas = Math.ceil(nombres.length / cols);
    const anchoCol = [];
    for (let c = 0; c < cols; c += 1) {
      let max = 0;
      for (let f = 0; f < filas; f += 1) { const k = c * filas + f; if (k < nombres.length) max = Math.max(max, anchos[k]); }
      anchoCol.push(max + 2);
    }
    if (cols > 1 && anchoCol.reduce((a, b) => a + b, 0) - 2 > ancho) continue;
    const lineas = [];
    for (let f = 0; f < filas; f += 1) {
      let linea = "";
      for (let c = 0; c < cols; c += 1) {
        const k = c * filas + f;
        if (k >= nombres.length) continue;
        linea += nombres[k] + (c < cols - 1 ? " ".repeat(anchoCol[c] - anchos[k]) : "");
      }
      lineas.push(linea.trimEnd());
    }
    return lineas.join("\n");
  }
  return nombres.join("\n");
}

/** Ruta de `hasta` vista desde la carpeta `desde` (ambas relativas a la raíz del proyecto). */
export function relativa(desde, hasta) {
  const a = desde.split("/").filter(Boolean);
  const b = hasta.split("/").filter(Boolean);
  let i = 0;
  while (i < a.length && i < b.length && a[i] === b[i]) i += 1;
  return [...Array(a.length - i).fill(".."), ...b.slice(i)].join("/") || ".";
}

/** Comando que escribe «Ejecutar» para un archivo, o null si se abre en la vista previa. */
export function comandoParaArchivo(ruta, cwd = "") {
  const r = relativa(cwd, ruta);
  const base = FS.nombreBase(ruta).replace(/\.[^.]+$/, "");
  const salida = relativa(cwd, FS.unir(FS.carpetaDe(ruta), base));
  const bin = salida.startsWith("..") ? salida : `./${salida}`;
  switch (FS.extension(ruta)) {
    case "js": case "mjs": case "cjs": return `node ${r}`;
    case "ts": return `ts-node ${r}`;
    case "py": return `python ${r}`;
    case "java": return `java ${r}`;
    case "c": return `gcc ${r} -o ${salida} && ${bin}`;
    case "cpp": case "cc": return `g++ ${r} -o ${salida} && ${bin}`;
    case "cs": return `dotnet run ${r}`;
    case "php": return `php ${r}`;
    case "go": return `go run ${r}`;
    case "rs": return `rustc ${r} -o ${salida} && ${bin}`;
    case "swift": return `swift ${r}`;
    case "kt": return `kotlinc ${r} -include-runtime -d ${salida}.jar && java -jar ${salida}.jar`;
    case "rb": return `ruby ${r}`;
    case "sql": return `sqlite3 ${r}`;
    default: return null;
  }
}

const LENGUAJE_SERVIDOR = { java: "java", c: "c", cpp: "cpp", cc: "cpp", cs: "csharp", php: "php", go: "go", rs: "rust", swift: "swift", kt: "kotlin", rb: "ruby" };
const NO_DISPONIBLE = ["npm", "npx", "pnpm", "yarn", "pip", "pip3", "apt", "apt-get", "brew", "sudo", "curl", "wget", "ssh", "docker", "make", "cmake", "cargo", "composer", "gem", "bundle", "vim", "nano", "vi", "emacs", "chmod", "chown", "kill", "ps", "top", "man"];

export const NOMBRES_COMANDOS = [
  "cat", "cd", "clear", "cls", "code", "cp", "date", "echo", "env", "exit", "export", "find", "gcc", "g++", "gh", "git", "go", "grep", "head", "help",
  "history", "java", "javac", "kotlinc", "ls", "mkdir", "mv", "node", "php", "pwd", "python", "python3", "rm", "rmdir", "ruby", "run", "rustc", "sqlite3",
  "swift", "tail", "tree", "touch", "ts-node", "wc", "whoami", "dotnet", "py", "dir", "type", "ll",
];

const AYUDA = [
  color.negrita("Terminal de CódigoCamp") + " — trabaja sobre los archivos de tu proyecto (/workspace).",
  "",
  color.azul("Archivos") + "   ls  cd  pwd  cat  touch  mkdir  rm  rmdir  mv  cp  tree  find  head  tail  wc  grep  echo  code <archivo>",
  color.azul("Shell") + "      comillas, $VARIABLES, comodines (*.js), pipes ( | ), encadenar ( && ; || ) y redirigir ( > >> )",
  color.azul("Git") + "        git init | status | add | commit -m | log | diff | restore | branch | switch -c | remote | push   (git help)",
  color.azul("Ejecutar") + "   node archivo.js      python archivo.py      ts-node archivo.ts      sqlite3 archivo.sql",
  "            go run · php · ruby · swift · java Archivo.java · gcc/g++ archivo -o prog && ./prog · rustc · kotlinc   (se ejecutan en el servidor)",
  color.azul("Atajos") + "     ↑/↓ historial · Tab completar · Ctrl+C cancelar · Ctrl+L limpiar · Ctrl+D salir",
  "",
  color.gris("No hay sistema operativo real: npm, pip, sudo, curl, editores de terminal, etc. no están disponibles."),
].join("\n");

// ----------------------------------------------------------------------- shell ----
export class Shell {
  /**
   * @param {object} o
   * @param {()=>object} o.proyecto   devuelve el proyecto actual { files, folders, git }
   * @param {(info?:object)=>void} o.cambio   se llama tras modificar archivos o Git
   * @param {string} o.usuario
   * @param {(ruta:string)=>void} o.abrir     abre un archivo en el editor (comando `code`)
   * @param {object} o.ejecutores   { node, python, ts, servidor, sql } (ver ejecucion.js)
   */
  constructor({ proyecto, cambio = () => {}, usuario = "estudiante", abrir = () => {}, ejecutores = {}, ahora = () => new Date() }) {
    Object.assign(this, { proyecto, cambio, usuario, abrir, ejecutores, ahora });
  }

  nuevaSesion(extra = {}) {
    return { cwd: "", anterior: "", historial: [], binarios: {}, vars: { "?": 0 }, columnas: 80, senal: undefined,
      out: () => {}, err: () => {}, leerLinea: async () => null, limpiar: () => {}, cerrar: () => {}, ...extra };
  }

  /** Ejecuta una línea completa. Devuelve el código de salida. */
  async ejecutar(linea, sesion) {
    const vars = { ...sesion.vars, PWD: FS.rutaAbsoluta(sesion.cwd), HOME: FS.RAIZ, USER: this.usuario };
    const lex = tokenizar(linea, vars);
    if (lex.error) { sesion.err(`bash: ${lex.error}\n`); return (sesion.vars["?"] = 2); }
    if (!lex.tokens.length) return sesion.vars["?"];
    const ast = analizar(lex.tokens);
    if (ast.error) { sesion.err(`bash: ${ast.error}\n`); return (sesion.vars["?"] = 2); }
    let codigo = 0;
    for (const { conector, etapas } of ast.lista) {
      if (sesion.senal?.aborted) break;
      if (conector === "&&" && codigo !== 0) continue;
      if (conector === "||" && codigo === 0) continue;
      codigo = await this.#tuberia(etapas, sesion);
      sesion.vars["?"] = codigo;
    }
    return codigo;
  }

  #expandir(palabras, sesion) {
    const py = this.proyecto();
    const salida = [];
    for (const p of palabras) {
      if (p.glob) {
        const coinciden = FS.expandirComodin(py, sesion.cwd, p.v);
        salida.push(...(coinciden.length ? coinciden : [p.v]));
      } else salida.push(p.v);
    }
    return salida;
  }

  async #tuberia(etapas, sesion) {
    let entrada = null;
    let codigo = 0;
    for (let i = 0; i < etapas.length; i += 1) {
      const etapa = etapas[i];
      const ultima = i === etapas.length - 1;
      const argv = this.#expandir(etapa.palabras, sesion);
      let buffer = "";
      let destino = null;
      if (etapa.redir) {
        const [d] = this.#expandir([etapa.redir.palabra], sesion);
        const ruta = FS.resolver(sesion.cwd, d);
        if (ruta === null || ruta === "") { sesion.err(`bash: ${d}: ${ruta === "" ? "Es un directorio" : "Ruta fuera del proyecto o con nombre no válido"}\n`); return 1; }
        destino = { ruta, anexar: etapa.redir.anexar, texto: d };
      }
      const alTerminal = ultima && !destino;
      const io = {
        sesion, entrada, py: () => this.proyecto(),
        out: (t) => { if (alTerminal) sesion.out(t); else buffer += t; },
        err: (t) => sesion.err(t),
      };
      codigo = await this.#comando(argv, io);
      if (destino) {
        const r = FS.escribirArchivo(this.proyecto(), destino.ruta, buffer, { anexar: destino.anexar });
        if (!r.ok) { sesion.err(`bash: ${destino.texto}: ${r.error}\n`); codigo = 1; } else this.cambio({ origen: "terminal" });
        buffer = "";
      }
      entrada = buffer;
      if (sesion.senal?.aborted) break;
    }
    return codigo;
  }

  async #comando(argv, io) {
    const [nombre, ...a] = argv;
    if (nombre === undefined) return 0;
    const fn = COMANDOS[nombre];
    try {
      if (fn) return (await fn.call(this, a, io)) ?? 0;
      if (nombre.includes("/")) return await this.#ejecutarBinario(nombre, io);
      if (NO_DISPONIBLE.includes(nombre)) {
        io.err(`${nombre}: no está disponible en esta terminal.\nEs una terminal del navegador (no un sistema operativo): trabaja con tus archivos y ejecuta node, python, git y más. Escribe help.\n`);
        return 127;
      }
      io.err(`bash: ${nombre}: orden no encontrada. Escribe help para ver los comandos.\n`);
      return 127;
    } catch (error) {
      if (error?.name === "AbortError") return 130;
      io.err(`${nombre}: error inesperado: ${error?.message || error}\n`);
      return 1;
    }
  }

  async #ejecutarBinario(nombre, io) {
    const { sesion } = io;
    const ruta = FS.resolver(sesion.cwd, nombre);
    const salida = ruta !== null ? sesion.binarios[ruta] : undefined;
    if (salida === undefined) {
      io.err(`bash: ${nombre}: ${ruta !== null && FS.tieneArchivo(this.proyecto(), ruta) ? "Permiso denegado (no es un programa compilado)" : NO_EXISTE}\n`);
      return ruta !== null && FS.tieneArchivo(this.proyecto(), ruta) ? 126 : 127;
    }
    io.out(salida.texto);
    return salida.codigo;
  }

  // ------------------------------------------------------------ completado ----
  /** Devuelve { desde, opciones } para el texto antes del cursor: `desde` es dónde empieza lo que se reemplaza. */
  completar(textoAntes, sesion) {
    const py = this.proyecto();
    const m = /(\S*)$/.exec(textoAntes);
    const parcial = m[1];
    const desde = textoAntes.length - parcial.length;
    const previas = textoAntes.slice(0, desde).trim().split(/\s+/).filter(Boolean);
    if (!previas.length || /[;|&]\s*$/.test(textoAntes.slice(0, desde))) {
      return { desde, opciones: NOMBRES_COMANDOS.filter((n) => n.startsWith(parcial)).sort().map((n) => `${n} `) };
    }
    if (previas[previas.length - 1] === "git" && previas.length === 1) {
      const subs = ["add", "branch", "checkout", "commit", "config", "diff", "help", "init", "log", "push", "remote", "reset", "restore", "status", "switch"];
      return { desde, opciones: subs.filter((n) => n.startsWith(parcial)).map((n) => `${n} `) };
    }
    const barra = parcial.lastIndexOf("/");
    const dirEscrito = barra === -1 ? "" : parcial.slice(0, barra + 1);
    const base = parcial.slice(barra + 1);
    const dir = FS.resolver(sesion.cwd, dirEscrito || ".");
    if (dir === null || !FS.tieneCarpeta(py, dir)) return { desde, opciones: [] };
    const soloDirs = ["cd", "rmdir"].includes(previas[0]);
    const { dirs, files } = FS.hijos(py, dir);
    const oculto = (n) => n.startsWith(".") && !base.startsWith(".");
    const opciones = [
      ...dirs.filter((n) => n.startsWith(base) && !oculto(n)).map((n) => `${dirEscrito}${n}/`),
      ...(soloDirs ? [] : files.filter((n) => n.startsWith(base) && !oculto(n)).map((n) => `${dirEscrito}${n} `)),
    ];
    return { desde, opciones };
  }
}

// -------------------------------------------------------------------- comandos ----
const sinOpciones = (a) => a.filter((x) => !(x.startsWith("-") && x.length > 1));
const opciones = (a) => a.filter((x) => x.startsWith("-") && x.length > 1).join("").replace(/-/g, "");

function ruta(io, arg) { return FS.resolver(io.sesion.cwd, arg); }

function leerArchivos(io, nombre, args) {
  const py = io.py();
  const partes = [];
  let ok = true;
  for (const arg of args) {
    const r = ruta(io, arg);
    if (r === null) { io.err(`${nombre}: ${arg}: ${NO_EXISTE}\n`); ok = false; }
    else if (FS.esCarpeta(py, r) || r === "") { io.err(`${nombre}: ${arg}: Es un directorio\n`); ok = false; }
    else if (!FS.tieneArchivo(py, r)) { io.err(`${nombre}: ${arg}: ${NO_EXISTE}\n`); ok = false; }
    else partes.push({ nombre: arg, ruta: r, texto: py.files[r] });
  }
  return { partes, ok };
}

const lineasDe = (t) => { const l = t.split("\n"); if (l[l.length - 1] === "") l.pop(); return l; };

function destinoFinal(py, io, fuente, destArg) {
  const d = ruta(io, destArg);
  if (d === null) return null;
  return FS.esCarpeta(py, d) || d === "" ? FS.unir(d, FS.nombreBase(fuente)) : d;
}

const COMANDOS = {
  help(a, io) { io.out(AYUDA + "\n"); },
  clear(a, io) { io.sesion.limpiar(); },
  cls(a, io) { io.sesion.limpiar(); },
  exit(a, io) { io.sesion.cerrar(); },
  pwd(a, io) { io.out(FS.rutaAbsoluta(io.sesion.cwd) + "\n"); },
  whoami(a, io) { io.out(this.usuario + "\n"); },
  date(a, io) { io.out(this.ahora().toLocaleString("es", { dateStyle: "full", timeStyle: "medium" }) + "\n"); },
  history(a, io) { io.out(io.sesion.historial.map((h, i) => `${String(i + 1).padStart(5)}  ${h}`).join("\n") + (io.sesion.historial.length ? "\n" : "")); },
  env(a, io) { io.out(Object.entries({ USER: this.usuario, HOME: FS.RAIZ, PWD: FS.rutaAbsoluta(io.sesion.cwd), ...io.sesion.vars }).filter(([k]) => k !== "?").map(([k, v]) => `${k}=${v}`).join("\n") + "\n"); },
  export(a, io) {
    for (const x of a) {
      const m = /^([A-Za-z_]\w*)=(.*)$/.exec(x);
      if (!m) { io.err(`export: «${x}»: usa NOMBRE=valor\n`); return 1; }
      io.sesion.vars[m[1]] = m[2];
    }
  },
  echo(a, io) {
    let nueva = true;
    let interpretar = false;
    while (a[0] === "-n" || a[0] === "-e" || a[0] === "-ne" || a[0] === "-en") {
      if (a[0].includes("n")) nueva = false;
      if (a[0].includes("e")) interpretar = true;
      a = a.slice(1);
    }
    let t = a.join(" ");
    if (interpretar) t = t.replace(/\\n/g, "\n").replace(/\\t/g, "\t").replace(/\\\\/g, "\\");
    io.out(t + (nueva ? "\n" : ""));
  },
  cd(a, io) {
    const { sesion } = io;
    const py = io.py();
    const arg = a[0] === "-" ? sesion.anterior : (a[0] ?? "");
    const r = ruta(io, arg);
    if (r === null || (r !== "" && !FS.tieneCarpeta(py, r))) {
      io.err(`bash: cd: ${a[0]}: ${r !== null && FS.tieneArchivo(py, r) ? "No es un directorio" : NO_EXISTE}\n`);
      return 1;
    }
    sesion.anterior = sesion.cwd;
    sesion.cwd = r;
    if (a[0] === "-") io.out(FS.rutaAbsoluta(r) + "\n");
  },
  ls(a, io) {
    const op = opciones(a);
    const todos = op.includes("a") || op.includes("A");
    const largo = op.includes("l");
    const uno = op.includes("1");
    const py = io.py();
    const destinos = sinOpciones(a);
    if (!destinos.length) destinos.push(".");
    let codigo = 0;
    const bloques = [];
    const lineaLarga = (nombre, esDir, tam) => `${esDir ? "d" : "-"}rw${esDir ? "x" : "-"}r-${esDir ? "x" : "-"}r-${esDir ? "x" : "-"} ${this.usuario} ${String(tam).padStart(7)} ${esDir ? nombreDir(nombre) : nombre}`;
    for (const d of destinos) {
      const r = ruta(io, d);
      if (r === null || !FS.existe(py, r)) { io.err(`ls: no se puede acceder a '${d}': ${NO_EXISTE}\n`); codigo = 2; continue; }
      if (FS.tieneArchivo(py, r)) { bloques.push({ titulo: null, texto: largo ? lineaLarga(FS.nombreBase(r), false, py.files[r].length) : d }); continue; }
      const { dirs, files } = FS.hijos(py, r);
      const visibles = (n) => todos || !n.startsWith(".");
      const entradas = [...dirs.filter(visibles).map((n) => ({ n, dir: true })), ...files.filter(visibles).map((n) => ({ n, dir: false }))];
      let texto;
      if (largo) texto = [`total ${entradas.length}`, ...entradas.map((e) => lineaLarga(e.n, e.dir, e.dir ? 4096 : py.files[FS.unir(r, e.n)].length))].join("\n");
      else if (uno) texto = entradas.map((e) => (e.dir ? nombreDir(e.n) : e.n)).join("\n");
      else texto = enColumnas([...(todos ? [color.azul("."), color.azul("..")] : []), ...entradas.map((e) => (e.dir ? nombreDir(e.n) : e.n))], io.sesion.columnas);
      bloques.push({ titulo: destinos.length > 1 ? d : null, texto });
    }
    bloques.sort((x, y) => (x.titulo === null ? 0 : 1) - (y.titulo === null ? 0 : 1));
    io.out(bloques.map((b) => (b.titulo ? `${b.titulo}:\n` : "") + b.texto).filter((t) => t !== "").join("\n\n") + (bloques.some((b) => b.texto !== "") ? "\n" : ""));
    return codigo;
  },
  cat(a, io) {
    const numerar = opciones(a).includes("n");
    const archivos = sinOpciones(a);
    let texto = "";
    let ok = true;
    if (!archivos.length) texto = io.entrada ?? "";
    else { const r = leerArchivos(io, "cat", archivos); ok = r.ok; texto = r.partes.map((p) => p.texto).join(""); }
    if (numerar) texto = lineasDe(texto).map((l, i) => `${String(i + 1).padStart(6)}\t${l}`).join("\n") + (texto ? "\n" : "");
    io.out(texto + (texto && !texto.endsWith("\n") ? "\n" : ""));
    return ok ? 0 : 1;
  },
  touch(a, io) {
    const py = io.py();
    let codigo = 0;
    for (const arg of sinOpciones(a)) {
      const r = ruta(io, arg);
      if (r === null || r === "") { io.err(`touch: no se puede efectuar «touch» sobre '${arg}': Nombre no válido (usa letras sin tilde, números, punto, guion y guion bajo)\n`); codigo = 1; continue; }
      if (FS.existe(py, r)) continue;
      const res = FS.crearArchivo(py, r, "");
      if (!res.ok) { io.err(`touch: '${arg}': ${res.error}\n`); codigo = 1; } else this.cambio({ origen: "terminal" });
    }
    if (!sinOpciones(a).length) { io.err("touch: falta un archivo\n"); return 1; }
    return codigo;
  },
  mkdir(a, io) {
    const py = io.py();
    const padres = opciones(a).includes("p");
    const dirs = sinOpciones(a);
    if (!dirs.length) { io.err("mkdir: falta un operando\n"); return 1; }
    let codigo = 0;
    for (const arg of dirs) {
      const r = ruta(io, arg);
      if (r === null || r === "") { io.err(`mkdir: no se puede crear el directorio '${arg}': Nombre no válido\n`); codigo = 1; continue; }
      const res = FS.crearCarpeta(py, r, { padres });
      if (!res.ok) {
        io.err(`mkdir: no se puede crear el directorio '${arg}': ${res.error === "Ya existe un archivo o carpeta con ese nombre." ? "El fichero ya existe" : res.error === "La carpeta de destino no existe." ? NO_EXISTE + " (usa -p para crear las carpetas intermedias)" : res.error}\n`);
        codigo = 1;
      } else this.cambio({ origen: "terminal" });
    }
    return codigo;
  },
  rm(a, io) {
    const py = io.py();
    const op = opciones(a);
    const recursivo = /[rR]/.test(op);
    const forzar = op.includes("f");
    const objetivos = sinOpciones(a);
    if (!objetivos.length) { if (!forzar) io.err("rm: falta un operando\n"); return forzar ? 0 : 1; }
    let codigo = 0;
    for (const arg of objetivos) {
      const r = ruta(io, arg);
      if (arg === "." || arg === ".." || arg.endsWith("/.") || arg.endsWith("/..") || r === "") { io.err(`rm: no se puede borrar '${arg}': es la carpeta raíz o una referencia a ella\n`); codigo = 1; continue; }
      if (r === null) { io.err(`rm: no se puede borrar '${arg}': está fuera del proyecto o el nombre no es válido\n`); codigo = 1; continue; }
      if (!FS.existe(py, r)) { if (!forzar) { io.err(`rm: no se puede borrar '${arg}': ${NO_EXISTE}\n`); codigo = 1; } continue; }
      if (FS.esCarpeta(py, r) && !recursivo) { io.err(`rm: no se puede borrar '${arg}': Es un directorio (usa -r)\n`); codigo = 1; continue; }
      const res = FS.borrar(py, r);
      if (FS.dentroDe(io.sesion.cwd, r)) io.sesion.cwd = FS.carpetaDe(r);
      this.cambio({ origen: "terminal", borrado: r, eliminado: res.eliminado });
    }
    return codigo;
  },
  rmdir(a, io) {
    const py = io.py();
    let codigo = 0;
    for (const arg of sinOpciones(a)) {
      const r = ruta(io, arg);
      if (r === null || !FS.esCarpeta(py, r)) { io.err(`rmdir: fallo al borrar '${arg}': ${r !== null && FS.tieneArchivo(py, r) ? "No es un directorio" : NO_EXISTE}\n`); codigo = 1; }
      else if (FS.archivosEn(py, r).length || py.folders.some((c) => c !== r && FS.dentroDe(c, r))) { io.err(`rmdir: fallo al borrar '${arg}': El directorio no está vacío\n`); codigo = 1; }
      else { FS.borrar(py, r); if (FS.dentroDe(io.sesion.cwd, r)) io.sesion.cwd = FS.carpetaDe(r); this.cambio({ origen: "terminal", borrado: r }); }
    }
    return codigo;
  },
  mv(a, io) {
    const py = io.py();
    const args = sinOpciones(a);
    if (args.length < 2) { io.err("mv: falta el archivo de destino\n"); return 1; }
    const fuentes = args.slice(0, -1);
    const destArg = args[args.length - 1];
    const dest = ruta(io, destArg);
    if (fuentes.length > 1 && !(dest !== null && (FS.esCarpeta(py, dest) || dest === ""))) { io.err(`mv: el objetivo '${destArg}' no es un directorio\n`); return 1; }
    let codigo = 0;
    for (const f of fuentes) {
      const r = ruta(io, f);
      if (r === null || r === "" || !FS.existe(py, r)) { io.err(`mv: no se puede efectuar 'stat' sobre '${f}': ${NO_EXISTE}\n`); codigo = 1; continue; }
      const fin = destinoFinal(py, io, r, destArg);
      if (fin === null) { io.err(`mv: destino no válido '${destArg}'\n`); codigo = 1; continue; }
      const res = FS.mover(py, r, fin);
      if (!res.ok) { io.err(`mv: no se puede mover '${f}' a '${destArg}': ${res.error}\n`); codigo = 1; continue; }
      if (FS.dentroDe(io.sesion.cwd, r)) io.sesion.cwd = fin + io.sesion.cwd.slice(r.length);
      this.cambio({ origen: "terminal", movido: [r, fin] });
    }
    return codigo;
  },
  cp(a, io) {
    const py = io.py();
    const recursivo = /[rR]/.test(opciones(a));
    const args = sinOpciones(a);
    if (args.length < 2) { io.err("cp: falta el archivo de destino\n"); return 1; }
    const destArg = args[args.length - 1];
    const dest = ruta(io, destArg);
    const fuentes = args.slice(0, -1);
    if (fuentes.length > 1 && !(dest !== null && (FS.esCarpeta(py, dest) || dest === ""))) { io.err(`cp: el objetivo '${destArg}' no es un directorio\n`); return 1; }
    let codigo = 0;
    for (const f of fuentes) {
      const r = ruta(io, f);
      if (r === null || r === "" || !FS.existe(py, r)) { io.err(`cp: no se puede efectuar 'stat' sobre '${f}': ${NO_EXISTE}\n`); codigo = 1; continue; }
      const fin = destinoFinal(py, io, r, destArg);
      const res = fin === null ? { ok: false, error: "destino no válido" } : FS.copiar(py, r, fin, { recursivo });
      if (!res.ok) { io.err(`cp: no se puede copiar '${f}' a '${destArg}': ${res.error}\n`); codigo = 1; } else this.cambio({ origen: "terminal" });
    }
    return codigo;
  },
  head(a, io) { return cabezaCola.call(this, a, io, true); },
  tail(a, io) { return cabezaCola.call(this, a, io, false); },
  wc(a, io) {
    const op = opciones(a);
    const archivos = sinOpciones(a);
    const fuentes = archivos.length ? leerArchivos(io, "wc", archivos) : { partes: [{ nombre: "", texto: io.entrada ?? "" }], ok: true };
    const cuenta = (t) => ({ l: (t.match(/\n/g) || []).length, p: (t.trim() ? t.trim().split(/\s+/).length : 0), c: new TextEncoder().encode(t).length });
    const cols = (op ? ["l", "w", "c"].filter((k) => op.includes(k === "w" ? "w" : k)) : ["l", "w", "c"]).map((k) => (k === "w" ? "p" : k));
    let total = { l: 0, p: 0, c: 0 };
    for (const p of fuentes.partes) {
      const c = cuenta(p.texto);
      total = { l: total.l + c.l, p: total.p + c.p, c: total.c + c.c };
      io.out(cols.map((k) => String(c[k]).padStart(6)).join("") + (p.nombre ? ` ${p.nombre}` : "") + "\n");
    }
    if (fuentes.partes.length > 1) io.out(cols.map((k) => String(total[k]).padStart(6)).join("") + " total\n");
    return fuentes.ok ? 0 : 1;
  },
  grep(a, io) {
    const op = opciones(a);
    const [patron, ...archivos] = sinOpciones(a);
    if (patron === undefined) { io.err("Uso: grep [-inrvcl] patrón [archivo...]\n"); return 2; }
    let re;
    try { re = new RegExp(op.includes("F") ? patron.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") : patron, op.includes("i") ? "gi" : "g"); }
    catch { io.err(`grep: expresión regular no válida: ${patron}\n`); return 2; }
    const py = io.py();
    let fuentes = [];
    const recursivo = /[rR]/.test(op);
    if (!archivos.length && !recursivo) fuentes = [{ nombre: "(entrada estándar)", texto: io.entrada ?? "" }];
    else {
      const objetivos = archivos.length ? archivos : ["."];
      for (const o of objetivos) {
        const r = ruta(io, o);
        if (r === null || !FS.existe(py, r)) { io.err(`grep: ${o}: ${NO_EXISTE}\n`); continue; }
        if (FS.tieneArchivo(py, r)) fuentes.push({ nombre: o, texto: py.files[r] });
        else if (recursivo) FS.archivosEn(py, r).forEach((f) => fuentes.push({ nombre: relativa(io.sesion.cwd, f), texto: py.files[f] }));
        else io.err(`grep: ${o}: Es un directorio\n`);
      }
    }
    const prefijo = fuentes.length > 1 || recursivo;
    let hubo = false;
    for (const f of fuentes) {
      const coincide = [];
      lineasDe(f.texto).forEach((l, i) => { re.lastIndex = 0; if (re.test(l) !== op.includes("v")) coincide.push([i + 1, l]); });
      if (!coincide.length) continue;
      hubo = true;
      if (op.includes("l")) { io.out(f.nombre + "\n"); continue; }
      if (op.includes("c")) { io.out((prefijo ? `${f.nombre}:` : "") + coincide.length + "\n"); continue; }
      for (const [n, l] of coincide) {
        re.lastIndex = 0;
        const marcada = op.includes("v") ? l : l.replace(re, (m) => `\x1b[1;31m${m}\x1b[0m`);
        io.out(`${prefijo ? color.magenta(f.nombre) + ":" : ""}${op.includes("n") ? color.verde(String(n)) + ":" : ""}${marcada}\n`);
      }
    }
    return hubo ? 0 : 1;
  },
  tree(a, io) {
    const py = io.py();
    const r = ruta(io, sinOpciones(a)[0] ?? ".");
    if (r === null || !FS.tieneCarpeta(py, r)) { io.err(`tree: ${a[0]}: ${NO_EXISTE}\n`); return 1; }
    const todos = opciones(a).includes("a");
    let nd = 0;
    let nf = 0;
    const lineas = [nombreDir(sinOpciones(a)[0] ?? ".")];
    const rec = (carpeta, prefijo) => {
      const { dirs, files } = FS.hijos(py, carpeta);
      const items = [...dirs.map((n) => ({ n, dir: true })), ...files.map((n) => ({ n, dir: false }))].filter((e) => todos || !e.n.startsWith("."));
      items.forEach((e, i) => {
        const ultimo = i === items.length - 1;
        lineas.push(`${prefijo}${ultimo ? "└── " : "├── "}${e.dir ? nombreDir(e.n) : e.n}`);
        if (e.dir) { nd += 1; rec(FS.unir(carpeta, e.n), prefijo + (ultimo ? "    " : "│   ")); } else nf += 1;
      });
    };
    rec(r, "");
    io.out(lineas.join("\n") + `\n\n${nd} ${nd === 1 ? "directorio" : "directorios"}, ${nf} ${nf === 1 ? "archivo" : "archivos"}\n`);
  },
  find(a, io) {
    const py = io.py();
    const iN = a.indexOf("-name");
    const iT = a.indexOf("-type");
    const patron = iN >= 0 ? a[iN + 1] : null;
    const tipo = iT >= 0 ? a[iT + 1] : null;
    const inicio = a[0] && !a[0].startsWith("-") ? a[0] : ".";
    const r = ruta(io, inicio);
    if (r === null || !FS.existe(py, r)) { io.err(`find: '${inicio}': ${NO_EXISTE}\n`); return 1; }
    const re = patron ? new RegExp("^" + patron.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, ".") + "$") : null;
    const entradas = [
      ...(r === "" ? [{ ruta: "", dir: true }] : []),
      ...py.folders.filter((c) => FS.dentroDe(c, r)).map((c) => ({ ruta: c, dir: true })),
      ...Object.keys(py.files).filter((f) => FS.dentroDe(f, r)).map((f) => ({ ruta: f, dir: false })),
    ].filter((e) => (!re || re.test(FS.nombreBase(e.ruta))) && (!tipo || (tipo === "d") === e.dir)).sort((x, y) => x.ruta.localeCompare(y.ruta));
    const mostrar = (p) => (p === r ? inicio : inicio === "." ? "./" + relativa(io.sesion.cwd, p).replace(/^\.\//, "") : relativa(io.sesion.cwd, p));
    io.out(entradas.map((e) => mostrar(e.ruta)).join("\n") + (entradas.length ? "\n" : ""));
  },
  code(a, io) {
    const py = io.py();
    for (const arg of sinOpciones(a)) {
      const r = ruta(io, arg);
      if (r === null || r === "") continue;
      if (FS.tieneArchivo(py, r)) this.abrir(r);
      else if (FS.esCarpeta(py, r)) io.err(`code: '${arg}' es una carpeta; ábrela en el explorador.\n`);
      else {
        const res = FS.crearArchivo(py, r, "");
        if (!res.ok) { io.err(`code: ${res.error}\n`); return 1; }
        this.cambio({ origen: "terminal" });
        this.abrir(r);
      }
    }
  },
  gh(a, io) { io.err("GitHub CLI (gh) no está conectado en esta terminal. Para practicar el flujo usa git; para publicar de verdad usa Git y gh en tu computadora (cli.github.com/manual).\n"); return 1; },
  git(a, io) {
    const r = ejecutarGit(io.py(), a, { cwd: io.sesion.cwd, usuario: this.usuario, ahora: this.ahora });
    if (r.salida) (r.error ? io.err : io.out)(r.salida + "\n");
    if (r.cambio) this.cambio({ origen: "git" });
    return r.error ? 1 : 0;
  },
};
COMANDOS.dir = COMANDOS.ls;
COMANDOS.ll = function ll(a, io) { return COMANDOS.ls.call(this, ["-l", ...a], io); };
COMANDOS.type = COMANDOS.cat;

function cabezaCola(a, io, cabeza) {
  let n = 10;
  const resto = [];
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] === "-n" && /^\d+$/.test(a[i + 1] || "")) { n = Number(a[i + 1]); i += 1; }
    else if (/^-\d+$/.test(a[i])) n = Number(a[i].slice(1));
    else resto.push(a[i]);
  }
  const archivos = sinOpciones(resto);
  const fuentes = archivos.length ? leerArchivos(io, cabeza ? "head" : "tail", archivos) : { partes: [{ nombre: "", texto: io.entrada ?? "" }], ok: true };
  fuentes.partes.forEach((p, idx) => {
    const l = lineasDe(p.texto);
    if (fuentes.partes.length > 1) io.out(`${idx ? "\n" : ""}==> ${p.nombre} <==\n`);
    const tramo = cabeza ? l.slice(0, n) : l.slice(Math.max(0, l.length - n));
    io.out(tramo.join("\n") + (tramo.length ? "\n" : ""));
  });
  return fuentes.ok ? 0 : 1;
}

// ------------------------------------------------------- ejecutar programas ----
function archivoAEjecutar(shell, io, nombre, arg, extensiones) {
  const py = io.py();
  if (!arg) { io.err(`${nombre}: indica un archivo. Ejemplo: ${nombre} archivo.${extensiones[0]}\n`); return null; }
  const r = ruta(io, arg);
  if (r === null || !FS.tieneArchivo(py, r)) { io.err(`${nombre}: no se puede abrir el archivo '${arg}': ${NO_EXISTE}\n`); return null; }
  return { ruta: r, codigo: py.files[r] };
}

function contexto(shell, io) {
  const { sesion } = io;
  return {
    senal: sesion.senal, out: io.out, err: io.err, leerLinea: sesion.leerLinea, cwd: sesion.cwd,
    proyecto: shell.proyecto(), cambio: (info) => shell.cambio({ origen: "ejecucion", ...info }),
  };
}

async function ejecutorNo(io, que) {
  io.err(`${que} no está disponible en este entorno.\n`);
  return 1;
}

COMANDOS.node = async function node(a, io) {
  const ej = this.ejecutores.node;
  if (!ej) return ejecutorNo(io, "node");
  if (a[0] === "--version" || a[0] === "-v") { io.out("v22 (ejecutado en el navegador por CódigoCamp)\n"); return 0; }
  if (a[0] === "-e" || a[0] === "-p") return ej({ ...contexto(this, io), ruta: "[eval]", codigo: a[1] ?? "", args: [], imprimir: a[0] === "-p" });
  if (!a.length) { io.err("node: el modo interactivo (REPL) no está disponible. Ejecuta un archivo: node archivo.js\n"); return 1; }
  const f = archivoAEjecutar(this, io, "node", a[0], ["js"]);
  return f ? ej({ ...contexto(this, io), ruta: f.ruta, codigo: f.codigo, args: a.slice(1) }) : 1;
};
COMANDOS["ts-node"] = async function tsNode(a, io) {
  const ej = this.ejecutores.ts;
  if (!ej) return ejecutorNo(io, "ts-node");
  const f = archivoAEjecutar(this, io, "ts-node", a[0], ["ts"]);
  return f ? ej({ ...contexto(this, io), ruta: f.ruta, codigo: f.codigo, args: a.slice(1) }) : 1;
};
COMANDOS.python = async function python(a, io) {
  const ej = this.ejecutores.python;
  if (!ej) return ejecutorNo(io, "python");
  if (a[0] === "--version" || a[0] === "-V") { io.out("Python 3.12 (Pyodide, en el navegador)\n"); return 0; }
  if (a[0] === "-c") return ej({ ...contexto(this, io), ruta: "<cadena>", codigo: a[1] ?? "", args: [] });
  if (!a.length) { io.err("python: el modo interactivo (REPL) no está disponible. Ejecuta un archivo: python archivo.py\n"); return 1; }
  const f = archivoAEjecutar(this, io, "python", a[0], ["py"]);
  return f ? ej({ ...contexto(this, io), ruta: f.ruta, codigo: f.codigo, args: a.slice(1) }) : 1;
};
COMANDOS.python3 = COMANDOS.python;
COMANDOS.py = COMANDOS.python;
COMANDOS.sqlite3 = async function sqlite3(a, io) {
  const ej = this.ejecutores.sql;
  if (!ej) return ejecutorNo(io, "sqlite3");
  const f = archivoAEjecutar(this, io, "sqlite3", a[0], ["sql"]);
  return f ? ej({ ...contexto(this, io), ruta: f.ruta, codigo: f.codigo }) : 1;
};

async function enServidor(shell, io, lenguaje, f, { guardarComo, nombreBin } = {}) {
  const ej = shell.ejecutores.servidor;
  if (!ej) return ejecutorNo(io, "La ejecución en servidor");
  io.err(color.gris(`Ejecutando ${lenguaje} en el servidor…\n`));
  const { salida, error } = await ej({ lenguaje, codigo: f.codigo, senal: io.sesion.senal });
  const texto = salida && !salida.endsWith("\n") ? salida + "\n" : salida || "";
  if (guardarComo) {
    // Compilar y ejecutar ocurren juntos en el servidor: se guarda el resultado y se muestra al lanzar el programa.
    io.sesion.binarios[guardarComo] = { texto, codigo: error ? 1 : 0 };
    return 0;
  }
  (error ? io.err : io.out)(texto);
  return error ? 1 : 0;
}

const compilador = (nombre, lenguaje, extensiones, { porDefecto = "a.out" } = {}) => async function compilar(a, io) {
  const iO = a.indexOf("-o");
  const salida = iO >= 0 ? a[iO + 1] : null;
  const fuente = a.find((x, i) => !x.startsWith("-") && a[i - 1] !== "-o" && extensiones.includes(FS.extension(x)));
  const f = archivoAEjecutar(this, io, nombre, fuente, extensiones);
  if (!f) return 1;
  const destino = ruta(io, salida ?? porDefecto);
  return enServidor(this, io, lenguaje, f, { guardarComo: destino ?? FS.unir(io.sesion.cwd, porDefecto) });
};
COMANDOS.gcc = compilador("gcc", "c", ["c"]);
COMANDOS.cc = COMANDOS.gcc;
COMANDOS["g++"] = compilador("g++", "cpp", ["cpp", "cc", "cxx"]);
COMANDOS.rustc = compilador("rustc", "rust", ["rs"], { porDefecto: "main" });
COMANDOS.kotlinc = async function kotlinc(a, io) {
  const fuente = a.find((x) => FS.extension(x) === "kt");
  const f = archivoAEjecutar(this, io, "kotlinc", fuente, ["kt"]);
  if (!f) return 1;
  const iD = a.indexOf("-d");
  const jar = iD >= 0 ? ruta(io, a[iD + 1]) : ruta(io, FS.nombreBase(f.ruta).replace(/\.kt$/, ".jar"));
  return enServidor(this, io, "kotlin", f, { guardarComo: `jar:${jar}` });
};
COMANDOS.javac = async function javac(a, io) {
  const fuente = a.find((x) => FS.extension(x) === "java");
  const f = archivoAEjecutar(this, io, "javac", fuente, ["java"]);
  if (!f) return 1;
  const clase = /public\s+(?:final\s+|abstract\s+)*(?:class|interface|enum|record)\s+(\w+)/.exec(f.codigo)?.[1] ?? FS.nombreBase(f.ruta).replace(/\.java$/, "");
  return enServidor(this, io, "java", f, { guardarComo: `clase:${clase}` });
};
COMANDOS.java = async function java(a, io) {
  if (a[0] === "-jar") {
    const jar = ruta(io, a[1] ?? "");
    const guardado = io.sesion.binarios[`jar:${jar}`];
    if (!guardado) { io.err(`Error: no se puede acceder al archivo jar ${a[1] ?? ""}. Compílalo primero con kotlinc.\n`); return 1; }
    io.out(guardado.texto);
    return guardado.codigo;
  }
  const arg = a.find((x) => !x.startsWith("-"));
  if (arg && FS.extension(arg) === "java") {
    const f = archivoAEjecutar(this, io, "java", arg, ["java"]);
    return f ? enServidor(this, io, "java", f) : 1;
  }
  const guardado = arg ? io.sesion.binarios[`clase:${arg}`] : null;
  if (!guardado) { io.err(`Error: no se ha encontrado o cargado la clase principal ${arg ?? ""}.\nUsa «java Archivo.java» o compila antes con javac Archivo.java\n`); return 1; }
  io.out(guardado.texto);
  return guardado.codigo;
};
const interpretado = (nombre, lenguaje, ext, previo = null) => async function interpretar(a, io) {
  const args = previo ? (a[0] === previo ? a.slice(1) : null) : a;
  if (args === null) { io.err(`${nombre}: solo se admite «${nombre} ${previo} archivo.${ext}»\n`); return 1; }
  const f = archivoAEjecutar(this, io, nombre, args[0], [ext]);
  return f ? enServidor(this, io, lenguaje, f) : 1;
};
COMANDOS.php = interpretado("php", "php", "php");
COMANDOS.ruby = interpretado("ruby", "ruby", "rb");
COMANDOS.swift = interpretado("swift", "swift", "swift");
COMANDOS.go = interpretado("go", "go", "go", "run");
COMANDOS.dotnet = interpretado("dotnet", "csharp", "cs", "run");

COMANDOS.run = async function run(a, io) {
  const f = archivoAEjecutar(this, io, "run", a[0], ["js"]);
  if (!f) return 1;
  const linea = comandoParaArchivo(f.ruta, io.sesion.cwd);
  if (!linea) { io.err(`run: no sé ejecutar archivos .${FS.extension(f.ruta)}. Los archivos HTML/CSS se ven con «Vista previa».\n`); return 1; }
  io.out(color.gris(`$ ${linea}\n`));
  return this.ejecutar(linea, io.sesion);
};
