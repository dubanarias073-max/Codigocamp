// Errores que aparecen al ejecutar (en la terminal) → problemas con archivo y línea, para el panel de problemas
// (⊗ y ⚠ de la barra de abajo) y para subrayarlos en el editor. Entiende Python, Node/JavaScript, PHP, compiladores
// (gcc, g++, javac, go, rustc, tsc, dotnet) y Ruby.

const LIMPIAR = /\x1b\[[0-9;?]*[ -/]*[@-~]/g;   // colores ANSI de la terminal

/** Busca el archivo del proyecto que corresponde a una ruta del mensaje (absoluta, relativa o con file://). */
export function rutaDelProyecto(ruta, rutas) {
  if (!ruta) return null;
  let r = String(ruta).trim().replace(/^file:\/\/\/?/, "/").replace(/\\/g, "/").replace(/^\.\//, "");
  try { r = decodeURIComponent(r); } catch { /* tal cual */ }
  if (rutas.includes(r)) return r;
  const sinBarra = r.replace(/^\/+/, "");
  if (rutas.includes(sinBarra)) return sinBarra;
  // /workspace/x.py, /home/web/proyecto/x.py…: la ruta del proyecto que termine igual (la más larga gana)
  const candidatas = rutas.filter((p) => sinBarra === p || sinBarra.endsWith("/" + p));
  candidatas.sort((a, b) => b.length - a.length);
  return candidatas[0] || null;
}

/**
 * @param {string} texto   lo que mostró la terminal
 * @param {string[]} rutas archivos del proyecto
 * @returns {{ruta: string, linea: number, columna?: number, mensaje: string, grave: boolean}[]}
 */
export function erroresDeSalida(texto, rutas) {
  const t = String(texto || "").replace(LIMPIAR, "").replace(/\r/g, "");
  const lineas = t.split("\n");
  const out = [];
  const agregar = (ruta, linea, mensaje, grave = true, columna) => {
    const r = rutaDelProyecto(ruta, rutas);
    const n = parseInt(linea, 10);
    if (!r || !(n > 0)) return;
    const m = String(mensaje || "Error al ejecutar").trim().slice(0, 300);
    if (out.some((x) => x.ruta === r && x.linea === n && x.mensaje === m)) return;
    out.push({ ruta: r, linea: n, ...(columna ? { columna: parseInt(columna, 10) } : {}), mensaje: m, grave });
  };

  // Python: Traceback … File "x.py", line N … y al final «TipoError: mensaje» (se marca la última línea del proyecto)
  for (let i = 0; i < lineas.length; i++) {
    if (!/^Traceback \(most recent call last\):/.test(lineas[i])) continue;
    let ultimo = null, j = i + 1;
    for (; j < lineas.length; j++) {
      const m = lineas[j].match(/^\s*File "([^"]+)", line (\d+)/);
      if (m) { if (rutaDelProyecto(m[1], rutas)) ultimo = m; continue; }
      if (/^\S/.test(lineas[j]) && /(Error|Exception|Interrupt|Exit)\b/.test(lineas[j])) break;
    }
    if (ultimo) agregar(ultimo[1], ultimo[2], lineas[j] || "Error de Python");
    i = j;
  }
  // Python: errores de sintaxis sin traceback (File "x.py", line N + … + SyntaxError: …)
  for (let i = 0; i < lineas.length; i++) {
    const m = lineas[i].match(/^\s*File "([^"]+)", line (\d+)\s*$/);
    if (!m) continue;
    const fin = lineas.slice(i + 1, i + 6).find((l) => /^(Syntax|Indentation|Tab)Error\b/.test(l));
    if (fin) agregar(m[1], m[2], fin);
  }
  // Node: «/ruta/app.js:12» en la primera línea y el error unas líneas después; o una pila «at … (app.js:12:5)»
  for (let i = 0; i < lineas.length; i++) {
    const m = lineas[i].match(/^(\/?[^\s:()]+\.(?:m?js|cjs|jsx|ts|tsx)):(\d+)\s*$/);
    if (!m) continue;
    const fin = lineas.slice(i + 1, i + 8).find((l) => /^\w*(Error|Exception)\b.*:/.test(l));
    if (fin) agregar(m[1], m[2], fin);
  }
  for (let i = 0; i < lineas.length; i++) {
    const err = lineas[i].match(/^(?:Uncaught )?(\w*Error)(?: \[\w+\])?: (.+)/);
    if (!err) continue;
    for (const l of lineas.slice(i + 1, i + 12)) {
      const s = l.match(/^\s+at (?:.*?\()?((?:file:\/\/)?[^()\s]+?\.(?:m?js|cjs|jsx|ts|tsx)):(\d+):(\d+)\)?\s*$/);
      if (s && rutaDelProyecto(s[1], rutas)) { agregar(s[1], s[2], `${err[1]}: ${err[2]}`, true, s[3]); break; }
    }
  }
  // Compiladores: archivo:línea:col: error|warning: mensaje (gcc, g++, go, tsc con --pretty false, clang…)
  for (const l of lineas) {
    const m = l.match(/^([^\s:][^:]*\.[A-Za-z0-9]+):(\d+)(?::(\d+))?:\s*(fatal error|error|warning|advertencia)\s*:?\s*(.*)$/i)
      || l.match(/^([^\s:][^:]*\.(?:go|py|rb|php|java)):(\d+)(?::(\d+))?:\s+()(.+)$/);
    if (m && !/^\s*at\s/.test(l)) agregar(m[1], m[2], m[5] || m[4], !/warning|advertencia/i.test(m[4]), m[3]);
  }
  // javac: Archivo.java:5: error: … ya entra arriba. tsc / dotnet: archivo(línea,col): error CS0103: mensaje
  for (const l of lineas) {
    const m = l.match(/^([^\s(][^(]*\.(?:ts|tsx|cs|vb|fs))\((\d+),(\d+)\):\s*(error|warning)\s*\w*:\s*(.*)$/i);
    if (m) agregar(m[1], m[2], m[5], m[4].toLowerCase() === "error", m[3]);
  }
  // Rust: error[E0425]: mensaje  →  --> src/main.rs:3:5
  for (let i = 0; i < lineas.length; i++) {
    const m = lineas[i].match(/^(error|warning)(?:\[\w+\])?: (.+)/);
    if (!m) continue;
    const donde = lineas.slice(i + 1, i + 4).map((l) => l.match(/^\s*--> ([^:]+):(\d+):(\d+)/)).find(Boolean);
    if (donde) agregar(donde[1], donde[2], m[2], m[1] === "error", donde[3]);
  }
  // PHP: «PHP Parse error: … in /ruta/x.php on line 3»
  for (const l of lineas) {
    const m = l.match(/(?:PHP )?((?:Parse|Fatal|Warning|Notice|Deprecated)[^:]*?):\s*(.+?) in (\S+\.php)(?::| on line )(\d+)/i);
    if (m) agregar(m[3], m[4], `${m[1]}: ${m[2]}`, !/warning|notice|deprecated/i.test(m[1]));
  }
  // Ruby: x.rb:3:in `metodo': mensaje (NameError)
  for (const l of lineas) {
    const m = l.match(/^([^\s:]+\.rb):(\d+):in [`'][^']*'?: (.+)$/);
    if (m) agregar(m[1], m[2], m[3]);
  }
  return out;
}
