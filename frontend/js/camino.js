// Camino de lecciones dibujado como CÓDIGO del lenguaje elegido:
//   HTML -> etiquetas <ol><li>…   Python -> def … leccion("…")   SQL -> INSERT INTO …   etc.
// Cada lección es una línea clicable: hecha (✓ ★★★), actual (▶ EMPEZAR) o bloqueada (comentada).
import { esc } from "/js/app.js";
import { logo } from "/js/logos.js";

// Tipos de token: k palabra clave · s texto · f función · c comentario · t etiqueta · a atributo · p símbolo · x normal
const sl = (t) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "seccion";
const pascal = (t) => sl(t).split("_").map((w) => w[0].toUpperCase() + w.slice(1)).join("");
const str = (t) => ["s", `"${t.replace(/"/g, "'")}"`];

// Familia de llaves: function nombre() { leccion("..."); }
const llaves = (ext, com, abre, fin = "", cierra = [["p", "}"]], cab = null, nombre = sl) => ({
  ext, com, cab, nombre,
  abre: (s) => abre(nombre(s)),
  leccion: (t) => [["f", "leccion"], ["p", "("], str(t), ["p", ")" + fin]],
  cofre: () => [["k", "return"], ["x", " "], ["f", "cofre"], ["p", "()" + fin]],
  cierra,
});

const LENG = {
  python: { ext: "py", com: "# ", sangria: "    ",
    abre: (s) => [["k", "def"], ["x", " "], ["f", sl(s)], ["p", "():"]],
    leccion: (t) => [["f", "leccion"], ["p", "("], str(t), ["p", ")"]],
    cofre: () => [["k", "return"], ["x", " "], ["f", "cofre"], ["p", "()"]], cierra: null },
  ruby: { ext: "rb", com: "# ", sangria: "  ",
    abre: (s) => [["k", "def"], ["x", " "], ["f", sl(s)]],
    leccion: (t) => [["f", "leccion"], ["x", " "], str(t)],
    cofre: () => [["f", "cofre"]], cierra: [["k", "end"]] },
  javascript: llaves("js", "// ", (n) => [["k", "async function"], ["x", " "], ["f", n], ["p", "() {"]], ";"),
  typescript: llaves("ts", "// ", (n) => [["k", "function"], ["x", " "], ["f", n], ["p", "(): "], ["k", "void"], ["p", " {"]], ";"),
  java: llaves("java", "// ", (n) => [["k", "void"], ["x", " "], ["f", n], ["p", "() {"]], ";"),
  csharp: llaves("cs", "// ", (n) => [["k", "void"], ["x", " "], ["f", n], ["p", "() {"]], ";", undefined, null, pascal),
  kotlin: llaves("kt", "// ", (n) => [["k", "fun"], ["x", " "], ["f", n], ["p", "() {"]]),
  swift: llaves("swift", "// ", (n) => [["k", "func"], ["x", " "], ["f", n], ["p", "() {"]]),
  php: llaves("php", "// ", (n) => [["k", "function"], ["x", " "], ["f", n], ["p", "() {"]], ";", undefined, [["t", "<?php"]]),
  go: llaves("go", "// ", (n) => [["k", "func"], ["x", " "], ["f", n], ["p", "() {"]]),
  rust: llaves("rs", "// ", (n) => [["k", "fn"], ["x", " "], ["f", n], ["p", "() {"]], ";"),
  c: llaves("c", "// ", (n) => [["k", "void"], ["x", " "], ["f", n], ["p", "(void) {"]], ";"),
  cpp: llaves("cpp", "// ", (n) => [["k", "void"], ["x", " "], ["f", n], ["p", "() {"]], ";"),
  html: { ext: "html", com: ["<!-- ", " -->"], sangria: "  ",
    abre: (s) => [["t", "<ol"], ["x", " "], ["a", "class"], ["p", "="], ["s", `"${sl(s)}"`], ["t", ">"]],
    leccion: (t) => [["t", "<li>"], ["x", t], ["t", "</li>"]],
    cofre: () => [["t", "<li"], ["x", " "], ["a", "class"], ["p", "="], ["s", '"cofre"'], ["t", ">"], ["x", "🎁"], ["t", "</li>"]],
    cierra: [["t", "</ol>"]] },
  css: { ext: "css", com: ["/* ", " */"], sangria: "  ",
    abre: (s) => [["a", "." + sl(s).replace(/_/g, "-")], ["x", " "], ["p", "{"]],
    leccion: (t) => [["a", "leccion"], ["p", ": "], str(t), ["p", ";"]],
    cofre: () => [["a", "cofre"], ["p", ": "], ["k", "abierto"], ["p", ";"]], cierra: [["p", "}"]] },
  sql: { ext: "sql", com: "-- ", sangria: "  ", lista: true,
    abre: () => [["k", "INSERT INTO"], ["x", " "], ["f", "camino"], ["p", " ("], ["a", "leccion"], ["p", ") "], ["k", "VALUES"]],
    leccion: (t, ult) => [["p", "("], ["s", `'${t.replace(/'/g, "''")}'`], ["p", ult ? ");" : "),"]],
    cofre: (ult) => [["p", "("], ["s", "'🎁 cofre'"], ["p", ult ? ");" : "),"]], cierra: null },
  bd: { ext: "js", com: "// ", sangria: "  ",
    abre: () => [["x", "db."], ["f", "camino"], ["x", "."], ["f", "insertMany"], ["p", "(["]],
    leccion: (t) => [["p", "{ "], ["a", "leccion"], ["p", ": "], str(t), ["p", " },"]],
    cofre: () => [["p", "{ "], ["a", "cofre"], ["p", ": "], ["k", "true"], ["p", " },"]], cierra: [["p", "]);"]] },
};

const html = (tokens) => tokens.map(([t, x]) => `<span class="tk-${t}">${esc(x)}</span>`).join("");
const plano = (tokens) => tokens.map(([, x]) => x).join("");
const comentar = (com, txt) => (Array.isArray(com) ? com[0] + txt + com[1] : com + txt);

/** HTML del "archivo de código" de una sección. nivel = {id,titulo,tipo,estado,estrellas} */
export function pintarSeccion(slug, seccion, numero, color) {
  const L = LENG[slug] || LENG.javascript;
  const hechos = seccion.niveles.filter((n) => n.estado === "hecho").length;
  const filas = [];
  let n = 0;
  const fija = (tokens, sangria = "") => filas.push(`<div class="cl cl-fija"><span class="cl-n">${++n}</span><span class="cl-g"></span><span class="cl-c">${esc(sangria)}${html(tokens)}</span></div>`);
  if (L.cab) fija(L.cab);
  fija(L.abre(seccion.titulo));
  const sg = L.sangria || "  ";
  seccion.niveles.forEach((nv, i) => {
    const ultimo = i === seccion.niveles.length - 1;
    const tokens = nv.tipo === "cofre" ? L.cofre(ultimo)
      : nv.tipo === "practica" ? L.leccion("🏋️ Práctica de repaso", ultimo)
      : nv.tipo === "trofeo" ? L.leccion("🏆 Examen de la etapa", ultimo)
      : L.leccion(nv.titulo, ultimo);
    const bloqueado = nv.estado === "bloqueado";
    const texto = bloqueado ? `<span class="tk-c">${esc(sg + comentar(L.com, plano(tokens)))}</span>` : esc(sg) + html(tokens);
    const marca = nv.estado === "hecho" ? (nv.tipo === "cofre" ? "🎁" : "★".repeat(nv.estrellas || 1)) : nv.estado === "actual" ? "▶ EMPEZAR" : "🔒";
    filas.push(`<button type="button" class="cl ${nv.estado} ${nv.tipo}" data-id="${nv.id}" data-tipo="${nv.tipo}" data-estado="${nv.estado}" aria-label="${esc(nv.titulo)}${bloqueado ? " (bloqueada)" : ""}">
      <span class="cl-n">${++n}</span><span class="cl-g"></span>
      <span class="cl-c">${texto}${nv.estado === "actual" ? '<i class="cursor"></i>' : ""}</span><span class="cl-s">${marca}</span></button>`);
  });
  if (L.cierra) fija(L.cierra);
  const archivo = `${(L.nombre || sl)(seccion.titulo)}.${L.ext}`;
  return `<div class="cod-win" style="--c:${color}">
    <div class="cod-bar"><span class="pto r"></span><span class="pto a"></span><span class="pto v"></span>
      <span class="cod-tab">${logo(slug, 16)}${esc(archivo)}</span><span class="cod-prog">SECCIÓN ${numero} · ${hechos}/${seccion.niveles.length}</span></div>
    <div class="cod-cuerpo">${filas.join("")}</div></div>`;
}
