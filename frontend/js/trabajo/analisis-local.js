// ----------------------------------------------------------- revisión local (sin servidor ni conexión) ----
// Funciona en el celular aunque no haya internet ni Conector: paréntesis, corchetes y llaves sin cerrar o que sobran,
// comillas sin cerrar y, en Python, «:» que falta y sangría. El servidor (cuando responde) revisa más a fondo.
const COMENTARIO = { python: ["#"], ruby: ["#"], shell: ["#"], lua: ["--"], php: ["//", "#"], java: ["//"], c: ["//"], cpp: ["//"], go: ["//"], csharp: ["//"], kotlin: ["//"], swift: ["//"], rust: ["//"], dart: ["//"] };
const BLOQUE = { java: ["/*", "*/"], c: ["/*", "*/"], cpp: ["/*", "*/"], go: ["/*", "*/"], php: ["/*", "*/"], csharp: ["/*", "*/"], kotlin: ["/*", "*/"], swift: ["/*", "*/"], rust: ["/*", "*/"], dart: ["/*", "*/"], lua: ["--[[", "]]"] };
const PAR = { "(": ")", "[": "]", "{": "}" };
const CIERRA = { ")": "(", "]": "[", "}": "{" };
const NINGUNO = { "(": "ningún paréntesis abierto", "[": "ningún corchete abierto", "{": "ninguna llave abierta" };

/** Problemas que se ven sin ejecutar ni pedir nada al servidor: [{linea, columna, fin_columna, mensaje, grave}] */
export function analizarLocal(texto, lang) {
  const problemas = [];
  const lineas = String(texto).split("\n");
  const com = COMENTARIO[lang] || ["//"];
  const bloque = BLOQUE[lang];
  const triple = lang === "python";
  const pila = [];
  let enBloque = false, enTriple = null, enPlantilla = false;
  const sinCodigo = [];   // cada línea sin cadenas ni comentarios (para la revisión de Python)
  for (let n = 0; n < lineas.length; n++) {
    const l = lineas[n];
    let limpio = "";
    let i = 0;
    while (i < l.length) {
      if (enBloque) { const f = l.indexOf(bloque[1], i); if (f === -1) { i = l.length; break; } i = f + bloque[1].length; enBloque = false; continue; }
      if (enTriple) { const f = l.indexOf(enTriple, i); if (f === -1) { i = l.length; break; } i = f + 3; enTriple = null; limpio += '""'; continue; }
      if (enPlantilla) { const f = l.indexOf("`", i); if (f === -1) { i = l.length; break; } i = f + 1; enPlantilla = false; continue; }
      const c = l[i];
      if (bloque && l.startsWith(bloque[0], i)) { enBloque = true; i += bloque[0].length; continue; }
      if (com.some((x) => l.startsWith(x, i))) break;
      if (triple && (l.startsWith('"""', i) || l.startsWith("'''", i))) { enTriple = l.slice(i, i + 3); i += 3; continue; }
      if (c === "`" && (lang === "go" || lang === "shell")) { enPlantilla = true; i++; continue; }
      if (c === '"' || (c === "'" && lang !== "rust")) {
        if (c === "'" && ["c", "cpp", "java", "csharp", "kotlin"].includes(lang) && l[i + 2] === "'") { limpio += "' '"; i += 3; continue; }
        let j = i + 1;
        while (j < l.length && l[j] !== c) j += l[j] === "\\" ? 2 : 1;
        if (j >= l.length && lang !== "shell" && lang !== "ruby" && lang !== "php" && !(lang === "python" && /\\$/.test(l))) {
          problemas.push({ linea: n + 1, columna: i + 1, fin_columna: l.length + 1, mensaje: `Falta cerrar las comillas ${c}`, grave: true });
          i = l.length; break;
        }
        limpio += c + c; i = j + 1; continue;
      }
      if (PAR[c]) pila.push({ c, linea: n + 1, columna: i + 1 });
      else if (CIERRA[c]) {
        const tope = pila[pila.length - 1];
        if (!tope) problemas.push({ linea: n + 1, columna: i + 1, fin_columna: i + 2, mensaje: `Sobra «${c}»: no hay ${NINGUNO[CIERRA[c]]}`, grave: true });
        else if (tope.c !== CIERRA[c]) {
          problemas.push({ linea: n + 1, columna: i + 1, fin_columna: i + 2, mensaje: `Se esperaba «${PAR[tope.c]}» (para cerrar el «${tope.c}» de la línea ${tope.linea}) pero hay «${c}»`, grave: true });
          pila.pop();
        } else pila.pop();
      }
      limpio += c; i++;
    }
    sinCodigo.push(limpio);
  }
  for (const a of pila.slice(-5)) problemas.push({ linea: a.linea, columna: a.columna, fin_columna: a.columna + 1, mensaje: `Falta cerrar este «${a.c}» (agrega «${PAR[a.c]}»)`, grave: true });
  if (enTriple) problemas.push({ linea: lineas.length, columna: 1, fin_columna: 2, mensaje: `Falta cerrar el texto de varias líneas (${enTriple})`, grave: true });
  if (lang === "python") problemas.push(...revisarPython(lineas, sinCodigo));
  return problemas.slice(0, 200);
}

const BLOQUE_PY = /^\s*(?:async\s+)?(def|class|if|elif|else|for|while|try|except|finally|with|match|case)\b/;
function revisarPython(lineas, sinCodigo) {
  const problemas = [];
  let abiertos = 0, inicio = -1;
  const sangria = (l) => l.match(/^[ \t]*/)[0].replace(/\t/g, "    ").length;
  for (let n = 0; n < sinCodigo.length; n++) {
    const l = sinCodigo[n];
    if (abiertos === 0) inicio = n;
    for (const c of l) { if (PAR[c]) abiertos++; else if (CIERRA[c]) abiertos = Math.max(0, abiertos - 1); }
    if (abiertos > 0 || /\\\s*$/.test(l)) continue;   // la instrucción sigue en la línea siguiente
    const primera = sinCodigo[inicio];
    const m = BLOQUE_PY.exec(primera);
    if (m && m[1] !== "match" && m[1] !== "case") {
      const fin = l.trimEnd();
      if (!fin.endsWith(":") && !/:\s*\S/.test(fin.replace(/^\s*\w+/, "").replace(/\b(lambda)\b[^:]*:/g, ""))) {
        problemas.push({ linea: n + 1, columna: Math.max(1, fin.length), fin_columna: fin.length + 1, mensaje: `Falta «:» al final de la línea (después de ${m[1]})`, grave: true });
      } else if (fin.endsWith(":")) {
        // la siguiente línea con código debe tener más sangría
        let k = n + 1;
        while (k < lineas.length && !lineas[k].trim()) k++;
        if (k < lineas.length && sangria(lineas[k]) <= sangria(lineas[inicio]) && !lineas[k].trim().startsWith("#")) {
          problemas.push({ linea: k + 1, columna: 1, fin_columna: lineas[k].length + 1, mensaje: `Falta sangría: esta línea va dentro del ${m[1]} de la línea ${inicio + 1} (agrega 4 espacios)`, grave: true });
        }
      }
    }
    if (/^ +\t|^\t+ /.test(lineas[n])) problemas.push({ linea: n + 1, columna: 1, fin_columna: 2, mensaje: "Mezclas espacios y tabulaciones en la sangría", grave: false });
  }
  return problemas;
}

