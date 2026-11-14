// Git didáctico sobre el proyecto. Es una simulación: el historial vive en la cuenta de la persona y «push» no envía nada.
// Lógica pura: recibe el proyecto { files, folders, git } y devuelve texto (con colores ANSI) y si algo cambió.
import { color } from "./ansi.js";
import { archivosEn, carpetaDe, dentroDe, esCarpeta, resolver, tieneArchivo } from "./fs.js";

const RAMA = /^[A-Za-z0-9._/-]{1,80}$/;
const URL_GITHUB = /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(?:\.git)?$/;
const FALTA_INIT = "fatal: no es un repositorio git (ni ninguno de los directorios superiores): .git\nEjecuta primero: git init";

const salida = (texto, extra = {}) => ({ salida: texto, error: false, cambio: false, ...extra });
const fallo = (texto) => ({ salida: texto, error: true, cambio: false });

// ---- .gitignore (patrones simples: nombre, carpeta/, *.ext, /ruta) ----
function aRegExp(patron) {
  return patron.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, "[^/]*").replace(/\?/g, "[^/]");
}
export function crearIgnorador(py) {
  const reglas = (py.files[".gitignore"] || "").split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#") && !l.startsWith("!"))
    .map((l) => {
      const soloCarpeta = l.endsWith("/");
      const anclado = l.startsWith("/") || l.replace(/\/$/, "").includes("/");
      const cuerpo = aRegExp(l.replace(/^\//, "").replace(/\/$/, ""));
      return { soloCarpeta, re: new RegExp(`^${cuerpo}$`), anclado };
    });
  return (ruta) => {
    const partes = ruta.split("/");
    return reglas.some((r) => {
      if (r.anclado) {
        return partes.some((_, i) => {
          const prefijo = partes.slice(0, i + 1).join("/");
          const esUltimo = i === partes.length - 1;
          return r.re.test(prefijo) && (!r.soloCarpeta || !esUltimo);
        });
      }
      return partes.some((p, i) => r.re.test(p) && (!r.soloCarpeta || i < partes.length - 1));
    });
  };
}

// ---- estado ----
export function calcularEstado(py) {
  const g = py.git;
  const staged = new Set(g.staged);
  const tracked = new Set(g.tracked);
  const C = g.committed;
  const preparados = [];
  const sinPreparar = [];
  for (const ruta of [...staged].sort()) {
    const existe = tieneArchivo(py, ruta);
    if (existe && !(ruta in C)) preparados.push({ ruta, tipo: "nuevo" });
    else if (existe && C[ruta] !== py.files[ruta]) preparados.push({ ruta, tipo: "modificado" });
    else if (!existe && ruta in C) preparados.push({ ruta, tipo: "eliminado" });
  }
  for (const ruta of [...tracked].sort()) {
    if (staged.has(ruta) || !(ruta in C)) continue;
    if (!tieneArchivo(py, ruta)) sinPreparar.push({ ruta, tipo: "eliminado" });
    else if (C[ruta] !== py.files[ruta]) sinPreparar.push({ ruta, tipo: "modificado" });
  }
  const ignorado = crearIgnorador(py);
  const sinSeguimiento = Object.keys(py.files).filter((r) => !tracked.has(r) && !staged.has(r) && !ignorado(r)).sort();
  return { preparados, sinPreparar, sinSeguimiento, ignorado };
}

/** Agrupa archivos sin seguimiento: si una carpeta no tiene nada seguido, se muestra «carpeta/». */
function agruparSinSeguimiento(py, rutas) {
  const seguidas = [...py.git.tracked, ...py.git.staged];
  const salida = new Set();
  for (const r of rutas) {
    const partes = r.split("/");
    let mostrado = r;
    for (let i = 1; i < partes.length; i += 1) {
      const dir = partes.slice(0, i).join("/");
      if (!seguidas.some((s) => dentroDe(s, dir))) { mostrado = dir + "/"; break; }
    }
    salida.add(mostrado);
  }
  return [...salida].sort();
}

const ETIQUETA = { nuevo: "archivo nuevo:", modificado: "modificado:   ", eliminado: "eliminado:    " };

function textoEstado(py) {
  const g = py.git;
  const { preparados, sinPreparar, sinSeguimiento } = calcularEstado(py);
  const lineas = [`En la rama ${g.branch}`];
  if (!g.commits.length) lineas.push("", "Aún no hay commits");
  if (preparados.length) {
    lineas.push("", "Cambios a ser confirmados:", '  (usa "git restore --staged <archivo>..." para sacarlos del área de preparación)');
    preparados.forEach((c) => lineas.push(color.verde(`\t${ETIQUETA[c.tipo]} ${c.ruta}`)));
  }
  if (sinPreparar.length) {
    lineas.push("", "Cambios no preparados para el commit:", '  (usa "git add <archivo>..." para actualizar lo que se confirmará)',
      '  (usa "git restore <archivo>..." para descartar los cambios del directorio de trabajo)');
    sinPreparar.forEach((c) => lineas.push(color.rojo(`\t${ETIQUETA[c.tipo]} ${c.ruta}`)));
  }
  if (sinSeguimiento.length) {
    lineas.push("", "Archivos sin seguimiento:", '  (usa "git add <archivo>..." para incluirlo en lo que se confirmará)');
    agruparSinSeguimiento(py, sinSeguimiento).forEach((r) => lineas.push(color.rojo(`\t${r}`)));
  }
  lineas.push("");
  if (!preparados.length && !sinPreparar.length && !sinSeguimiento.length) lineas.push("nada para hacer commit, el árbol de trabajo está limpio");
  else if (!preparados.length) lineas.push(sinPreparar.length ? 'sin cambios agregados al commit (usa "git add" o "git commit -a")' : 'no hay nada agregado al commit pero hay archivos sin seguimiento (usa "git add" para hacerles seguimiento)');
  return lineas.join("\n");
}

// ---- diff ----
export function diffLineas(a, b) {
  const A = a === "" ? [] : a.split("\n");
  const B = b === "" ? [] : b.split("\n");
  let ini = 0;
  while (ini < A.length && ini < B.length && A[ini] === B[ini]) ini += 1;
  let finA = A.length;
  let finB = B.length;
  while (finA > ini && finB > ini && A[finA - 1] === B[finB - 1]) { finA -= 1; finB -= 1; }
  const ma = A.slice(ini, finA);
  const mb = B.slice(ini, finB);
  const ops = A.slice(0, ini).map((t) => ({ op: " ", t }));
  if (ma.length * mb.length > 4_000_000) {
    ma.forEach((t) => ops.push({ op: "-", t }));
    mb.forEach((t) => ops.push({ op: "+", t }));
  } else {
    const n = ma.length;
    const m = mb.length;
    const L = Array.from({ length: n + 1 }, () => new Uint32Array(m + 1));
    for (let i = n - 1; i >= 0; i -= 1) for (let j = m - 1; j >= 0; j -= 1) L[i][j] = ma[i] === mb[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
    let i = 0;
    let j = 0;
    while (i < n && j < m) {
      if (ma[i] === mb[j]) { ops.push({ op: " ", t: ma[i] }); i += 1; j += 1; }
      else if (L[i + 1][j] >= L[i][j + 1]) { ops.push({ op: "-", t: ma[i] }); i += 1; }
      else { ops.push({ op: "+", t: mb[j] }); j += 1; }
    }
    for (; i < n; i += 1) ops.push({ op: "-", t: ma[i] });
    for (; j < m; j += 1) ops.push({ op: "+", t: mb[j] });
  }
  A.slice(finA).forEach((t) => ops.push({ op: " ", t }));
  return ops;
}

function diffUnificado(ruta, antes, despues) {
  const ops = diffLineas(antes ?? "", despues ?? "");
  if (!ops.some((o) => o.op !== " ")) return "";
  const cab = [color.negrita(`diff --git a/${ruta} b/${ruta}`)];
  if (antes === null) cab.push(color.negrita("archivo nuevo"));
  if (despues === null) cab.push(color.negrita("archivo eliminado"));
  cab.push(color.negrita(`--- ${antes === null ? "/dev/null" : "a/" + ruta}`), color.negrita(`+++ ${despues === null ? "/dev/null" : "b/" + ruta}`));
  const CONTEXTO = 3;
  const cambiados = ops.map((o, i) => (o.op !== " " ? i : -1)).filter((i) => i >= 0);
  const bloques = [];
  for (const i of cambiados) {
    const ultimo = bloques[bloques.length - 1];
    if (ultimo && i - ultimo.fin <= CONTEXTO * 2 + 1) ultimo.fin = i;
    else bloques.push({ ini: i, fin: i });
  }
  const cuerpo = [];
  for (const b of bloques) {
    const desde = Math.max(0, b.ini - CONTEXTO);
    const hasta = Math.min(ops.length - 1, b.fin + CONTEXTO);
    const tramo = ops.slice(desde, hasta + 1);
    const l1 = ops.slice(0, desde).filter((o) => o.op !== "+").length + 1;
    const l2 = ops.slice(0, desde).filter((o) => o.op !== "-").length + 1;
    const n1 = tramo.filter((o) => o.op !== "+").length;
    const n2 = tramo.filter((o) => o.op !== "-").length;
    cuerpo.push(color.cian(`@@ -${l1},${n1} +${l2},${n2} @@`));
    tramo.forEach((o) => cuerpo.push(o.op === "-" ? color.rojo(`-${o.t}`) : o.op === "+" ? color.verde(`+${o.t}`) : ` ${o.t}`));
  }
  return [...cab, ...cuerpo].join("\n");
}

const hashAleatorio = () => {
  const bytes = new Uint8Array(4);
  (globalThis.crypto || { getRandomValues: (b) => b.map(() => Math.floor(Math.random() * 256)) }).getRandomValues(bytes);
  return [...bytes].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 7);
};

const punta = (g) => g.commits[0]?.hash ?? "";

/**
 * Ejecuta «git <args>». opciones: { cwd, usuario, ahora(), hash() } (los dos últimos existen para las pruebas).
 * Devuelve { salida, error, cambio } — cambio indica que se modificó el proyecto y hay que guardar.
 */
export function ejecutarGit(py, args, { cwd = "", usuario = "estudiante", ahora = () => new Date(), hash = hashAleatorio } = {}) {
  const g = py.git;
  const [sub, ...resto] = args;
  const banderas = resto.filter((a) => a.startsWith("-"));
  const posicionales = resto.filter((a) => !a.startsWith("-"));
  const tiene = (...nombres) => nombres.some((n) => banderas.includes(n));

  if (sub === undefined || sub === "help" || sub === "--help" || sub === "-h") {
    return salida([
      "Comandos de Git disponibles en esta práctica:",
      "  git init                       crear el repositorio",
      "  git status                     ver qué cambió",
      "  git add <archivo|.>            preparar cambios",
      '  git commit -m "mensaje"        guardar los cambios preparados (-a: incluye los ya seguidos)',
      "  git log [--oneline]            historial",
      "  git diff [--staged] [archivo]  ver las diferencias",
      "  git restore [--staged] <arch>  descartar cambios / sacar de preparación",
      "  git branch | switch -c <rama>  ramas",
      "  git remote add origin <URL>    configurar GitHub (práctica)",
      "  git push -u origin main        simulado: no envía nada",
    ].join("\n"));
  }
  if (sub === "--version" || sub === "version") return salida("git version 2.45.0 (simulado en CódigoCamp)");
  if (sub === "init") {
    const ya = g.initialized;
    g.initialized = true;
    return salida(`${ya ? "Reinicializado el" : "Inicializado un"} repositorio Git vacío en /workspace/.git/`, { cambio: !ya });
  }
  if (sub === "config") {
    if (tiene("--list", "-l")) return salida(`user.name=${usuario}\nuser.email=${usuario.toLowerCase().replace(/\s+/g, ".")}@codigocamp.local`);
    return salida(posicionales.length === 1 ? (posicionales[0] === "user.name" ? usuario : "") : "");
  }
  if (!g.initialized) return fallo(FALTA_INIT);

  switch (sub) {
    case "status": return salida(textoEstado(py));

    case "add": {
      if (!posicionales.length && !tiene("-A", "--all", "-u")) return fallo("No se indicó qué agregar. ¿Querías decir «git add .»?");
      const { ignorado } = calcularEstado(py);
      let candidatos;
      if (posicionales.includes(".") || tiene("-A", "--all") || (tiene("-u") && !posicionales.length)) {
        const base = posicionales.includes(".") ? cwd : "";
        candidatos = [...new Set([...Object.keys(py.files), ...g.tracked])].filter((r) => dentroDe(r, base) && (g.tracked.includes(r) || !ignorado(r)));
        if (tiene("-u")) candidatos = candidatos.filter((r) => g.tracked.includes(r));
      } else {
        candidatos = [];
        for (const arg of posicionales) {
          const ruta = resolver(cwd, arg);
          if (ruta === null) return fallo(`fatal: la ruta '${arg}' está fuera del repositorio`);
          const dentro = esCarpeta(py, ruta) || ruta === "" ? archivosEn(py, ruta) : [];
          const lista = tieneArchivo(py, ruta) ? [ruta] : [...dentro, ...g.tracked.filter((t) => dentroDe(t, ruta) && !tieneArchivo(py, t))];
          if (!lista.length) return fallo(`fatal: la ruta '${arg}' no coincide con ningún archivo`);
          if (tieneArchivo(py, ruta) && ignorado(ruta) && !g.tracked.includes(ruta)) return fallo(`Las siguientes rutas se ignoran por .gitignore: ${ruta}`);
          candidatos.push(...lista.filter((r) => g.tracked.includes(r) || !ignorado(r)));
        }
      }
      // Solo se prepara lo que realmente cambia (como Git: agregar un archivo sin cambios no hace nada).
      const C = g.committed;
      const cambios = candidatos.filter((r) => (tieneArchivo(py, r) ? C[r] !== py.files[r] : r in C));
      cambios.forEach((r) => { if (!g.staged.includes(r)) g.staged.push(r); if (!g.tracked.includes(r)) g.tracked.push(r); });
      return salida("", { cambio: cambios.length > 0 });
    }

    case "restore": case "reset": {
      const soloPreparacion = sub === "reset" || tiene("--staged", "-S");
      const objetivos = posicionales.length ? posicionales : (soloPreparacion ? ["."] : []);
      if (!objetivos.length) return fallo("Indica qué restaurar: git restore <archivo>");
      const rutas = [];
      for (const arg of objetivos) {
        const ruta = resolver(cwd, arg);
        if (ruta === null) return fallo(`error: la ruta '${arg}' está fuera del repositorio`);
        const coincidencias = [...new Set([...Object.keys(py.files), ...g.tracked, ...g.staged])].filter((r) => dentroDe(r, ruta));
        if (!coincidencias.length) return fallo(`error: la ruta '${arg}' no coincide con ningún archivo conocido por git`);
        rutas.push(...coincidencias);
      }
      if (soloPreparacion) {
        g.staged = g.staged.filter((r) => !rutas.includes(r));
        return salida("", { cambio: true });
      }
      for (const r of rutas) {
        if (!(r in g.committed)) return fallo(`error: la ruta '${r}' no está en ningún commit; no hay nada que restaurar`);
        py.files[r] = g.committed[r];
        g.staged = g.staged.filter((s) => s !== r);
      }
      const nuevas = new Set(py.folders);
      rutas.forEach((r) => { for (let c = carpetaDe(r); c; c = carpetaDe(c)) nuevas.add(c); });
      py.folders = [...nuevas].sort();
      return salida("", { cambio: true });
    }

    case "commit": {
      const mensajes = [];
      for (let i = 0; i < resto.length; i += 1) {
        if (resto[i] === "-m" || resto[i] === "--message") { if (resto[i + 1] !== undefined) mensajes.push(resto[i + 1]); i += 1; }
        else if (/^-[a-z]*m$/.test(resto[i])) { if (resto[i + 1] !== undefined) mensajes.push(resto[i + 1]); i += 1; }
        else if (resto[i].startsWith("-m") && resto[i].length > 2) mensajes.push(resto[i].slice(2));
        else if (resto[i].startsWith("--message=")) mensajes.push(resto[i].slice(10));
      }
      const mensaje = mensajes.join("\n\n").trim().slice(0, 200);
      const todo = resto.some((a) => /^-[a-z]*a[a-z]*$/.test(a) && !a.startsWith("--")) || tiene("--all");
      if (!mensaje) return fallo('Abortando el commit: escribe un mensaje con -m. Por ejemplo: git commit -m "Describe tu cambio"');
      if (todo) {
        for (const r of g.tracked) {
          const existe = tieneArchivo(py, r);
          if ((existe && g.committed[r] !== py.files[r] && r in g.committed) || (!existe && r in g.committed)) if (!g.staged.includes(r)) g.staged.push(r);
        }
      }
      const { preparados } = calcularEstado(py);
      if (!preparados.length) return fallo(`En la rama ${g.branch}\nno hay nada para confirmar. Prepara cambios con «git add» primero.`);
      const primero = !g.commits.length;
      let id = hash();
      while (g.commits.some((c) => c.hash === id)) id = hash();
      for (const { ruta, tipo } of preparados) {
        if (tipo === "eliminado") { delete g.committed[ruta]; g.tracked = g.tracked.filter((t) => t !== ruta); }
        else g.committed[ruta] = py.files[ruta];
      }
      g.staged = [];
      g.commits.unshift({ hash: id, message: mensaje, date: ahora().toISOString() });
      g.commits = g.commits.slice(0, 100);
      g.branches[g.branch] = id;
      const nuevos = preparados.filter((c) => c.tipo === "nuevo");
      const lineas = [`[${g.branch}${primero ? " (commit-raíz)" : ""} ${id}] ${mensaje.split("\n")[0]}`,
        ` ${preparados.length} ${preparados.length === 1 ? "archivo cambiado" : "archivos cambiados"}`,
        ...nuevos.map((c) => ` modo de creación 100644 ${c.ruta}`),
        ...preparados.filter((c) => c.tipo === "eliminado").map((c) => ` borrar modo 100644 ${c.ruta}`)];
      return salida(lineas.join("\n"), { cambio: true });
    }

    case "log": {
      if (!g.commits.length) return fallo(`fatal: tu rama actual '${g.branch}' aún no tiene commits`);
      let limite = g.commits.length;
      const iN = resto.indexOf("-n");
      if (iN >= 0 && /^\d+$/.test(resto[iN + 1] || "")) limite = Number(resto[iN + 1]);
      const corto = resto.find((a) => /^-\d+$/.test(a));
      if (corto) limite = Number(corto.slice(1));
      const lista = g.commits.slice(0, Math.max(1, limite));
      const marca = (i) => (i === 0 ? ` ${color.amarillo("(")}${color.cian("HEAD -> ")}${color.verde(g.branch)}${color.amarillo(")")}` : "");
      if (tiene("--oneline")) return salida(lista.map((c, i) => `${color.amarillo(c.hash)}${marca(i)} ${c.message.split("\n")[0]}`).join("\n"));
      const autor = `${usuario} <${usuario.toLowerCase().replace(/\s+/g, ".")}@codigocamp.local>`;
      return salida(lista.map((c, i) => [
        `${color.amarillo("commit " + c.hash)}${marca(i)}`, `Author: ${autor}`,
        `Date:   ${new Date(c.date).toLocaleString("es")}`, "", ...c.message.split("\n").map((l) => `    ${l}`),
      ].join("\n")).join("\n\n"));
    }

    case "diff": {
      const preparado = tiene("--staged", "--cached");
      const filtro = posicionales.length ? posicionales.map((a) => resolver(cwd, a)) : [""];
      if (filtro.includes(null)) return fallo("fatal: ruta fuera del repositorio");
      const { preparados, sinPreparar } = calcularEstado(py);
      const lista = (preparado ? preparados : sinPreparar).filter((c) => filtro.some((f) => dentroDe(c.ruta, f)));
      const partes = lista.map((c) => diffUnificado(c.ruta, c.tipo === "nuevo" ? null : g.committed[c.ruta], c.tipo === "eliminado" ? null : py.files[c.ruta])).filter(Boolean);
      return salida(partes.join("\n"));
    }

    case "branch": {
      const nombres = posicionales;
      const borrar = tiene("-d", "-D", "--delete");
      const todas = () => [...new Set([g.branch, ...Object.keys(g.branches)])].sort();
      if (!nombres.length) return salida(todas().map((b) => (b === g.branch ? color.verde(`* ${b}`) : `  ${b}`)).join("\n"));
      const nombre = nombres[0];
      if (!RAMA.test(nombre)) return fallo(`fatal: '${nombre}' no es un nombre de rama válido`);
      if (borrar) {
        if (nombre === g.branch) return fallo(`error: no se puede eliminar la rama '${nombre}' porque estás en ella`);
        if (!(nombre in g.branches)) return fallo(`error: no se encontró la rama '${nombre}'`);
        delete g.branches[nombre];
        return salida(`Rama ${nombre} eliminada`, { cambio: true });
      }
      if (nombre === g.branch || nombre in g.branches) return fallo(`fatal: la rama '${nombre}' ya existe`);
      if (!g.commits.length) return fallo("fatal: no se puede crear una rama sin commits todavía. Haz un commit primero.");
      g.branches[nombre] = punta(g);
      return salida("", { cambio: true });
    }

    case "switch": case "checkout": {
      const crear = tiene("-c", "-b", "-C", "-B", "--create");
      const nombre = posicionales[0];
      if (!nombre) return fallo(`fatal: indica la rama: git ${sub} ${crear ? "-" + (sub === "switch" ? "c" : "b") + " " : ""}<rama>`);
      if (!RAMA.test(nombre)) return fallo(`fatal: '${nombre}' no es un nombre de rama válido`);
      if (crear) {
        if (nombre === g.branch || nombre in g.branches) return fallo(`fatal: la rama '${nombre}' ya existe`);
        g.branches[g.branch] = punta(g);
        g.branches[nombre] = punta(g);
        g.branch = nombre;
        return salida(`Cambiado a nueva rama '${nombre}'`, { cambio: true });
      }
      if (nombre === g.branch) return salida(`Ya estás en '${nombre}'`);
      if (!(nombre in g.branches)) return fallo(`fatal: la rama '${nombre}' no existe. Para crearla: git switch -c ${nombre}`);
      if (g.branches[nombre] !== punta(g)) {
        return fallo(`En esta práctica solo puedes cambiar entre ramas que apuntan al mismo commit.\nLa rama '${nombre}' tiene otro historial y aquí no se puede reconstruir.`);
      }
      g.branches[g.branch] = punta(g);
      g.branch = nombre;
      return salida(`Cambiado a la rama '${nombre}'`, { cambio: true });
    }

    case "remote": {
      const [accion, nombre, url] = posicionales.length ? posicionales : [""];
      if (!posicionales.length || tiene("-v", "--verbose")) {
        return salida(g.remote ? (tiene("-v", "--verbose") ? `origin\t${g.remote} (fetch)\norigin\t${g.remote} (push)` : "origin") : "");
      }
      if (accion === "add") {
        if (nombre !== "origin") return fallo("En esta práctica el remoto se llama origin: git remote add origin <URL>");
        if (!URL_GITHUB.test(url || "")) return fallo("Usa una URL de GitHub como https://github.com/usuario/repositorio.git");
        if (g.remote) return fallo("error: el remoto origin ya existe.");
        g.remote = url;
        return salida("", { cambio: true });
      }
      if (accion === "remove" || accion === "rm") {
        if (nombre !== "origin" || !g.remote) return fallo("error: no existe el remoto " + (nombre || ""));
        g.remote = "";
        return salida("", { cambio: true });
      }
      return fallo("Subcomando de remote no disponible. Prueba: git remote add origin <URL> | git remote -v");
    }

    case "push": {
      if (!g.remote) return fallo("fatal: no hay un destino configurado.\nPrimero: git remote add origin https://github.com/usuario/repositorio.git");
      if (!g.commits.length) return fallo("error: no hay nada que enviar: aún no hay commits.");
      return salida(`Simulación: no se envió nada a ${g.remote}.\nEn tu computadora real, este mismo comando publicaría ${g.commits.length} commit(s) de la rama ${g.branch}.\n` + color.gris("(CódigoCamp no se conecta a GitHub.)"));
    }

    case "merge": case "pull": case "fetch": case "clone": case "rebase": case "stash": case "tag": case "cherry-pick": case "revert":
      return fallo(`git ${sub} no está disponible en esta práctica. Aquí puedes ensayar: init, status, add, commit, log, diff, restore, branch, switch y remote.`);
    default:
      return fallo(`git: '${sub}' no es un comando de git en esta práctica. Escribe «git help».`);
  }
}
