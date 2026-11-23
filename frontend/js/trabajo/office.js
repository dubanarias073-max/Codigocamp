// Visor de documentos de Office dentro de Trabajo (sin descargarlos ni usar servicios externos):
//  · Word (.docx): mammoth convierte el documento a HTML (títulos, listas, tablas, negrita, imágenes).
//  · Excel (.xlsx): se lee el libro con JSZip y se pinta cada hoja como en Excel (columnas A, B, C…, celdas combinadas,
//    fechas y números con su formato básico). Se muestran los valores guardados (los que calculó Excel).
//  · PowerPoint (.pptx): se dibuja cada diapositiva (textos, imágenes, formas, colores y fondos) a su tamaño real.
// Todo se muestra dentro de un iframe aislado (sandbox sin scripts): un documento no puede ejecutar nada.

const VENDOR = "/vendor/office";
const cargados = new Map();
function cargarScript(src, global) {
  if (globalThis[global]) return Promise.resolve(globalThis[global]);
  if (!cargados.has(src)) {
    cargados.set(src, new Promise((ok, mal) => {
      // Monaco trae un cargador AMD (define): mientras se carga la librería se esconde, para que quede en window
      const amd = globalThis.define;
      globalThis.define = undefined;
      const s = document.createElement("script");
      s.src = src;
      s.onload = () => { globalThis.define = amd; globalThis[global] ? ok(globalThis[global]) : mal(new Error("No se pudo cargar el lector de documentos.")); };
      s.onerror = () => { globalThis.define = amd; cargados.delete(src); mal(new Error("No se pudo cargar el lector de documentos (¿sin conexión?).")); };
      document.head.append(s);
    }));
  }
  return cargados.get(src);
}
const jszip = () => cargarScript(`${VENDOR}/jszip.min.js`, "JSZip");
const mammoth = () => cargarScript(`${VENDOR}/mammoth.browser.min.js`, "mammoth");

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const xml = (t) => new DOMParser().parseFromString(t, "application/xml");
/** Hijos/descendientes por nombre local (sin importar el prefijo a:, p:, w:…). */
const todos = (n, nombre) => (n ? [...n.getElementsByTagNameNS("*", nombre)] : []);
const uno = (n, nombre) => (n ? n.getElementsByTagNameNS("*", nombre)[0] ?? null : null);
const hijos = (n, nombre) => (n ? [...n.children].filter((c) => c.localName === nombre) : []);
const hijo = (n, nombre) => hijos(n, nombre)[0] ?? null;
const attr = (n, nombre) => n?.getAttribute(nombre) ?? n?.getAttributeNS?.("*", nombre) ?? null;
const rid = (n, nombre = "embed") => n?.getAttributeNS("http://schemas.openxmlformats.org/officeDocument/2006/relationships", nombre) ?? n?.getAttribute(`r:${nombre}`) ?? null;

/** Ruta absoluta dentro del zip para un destino relativo de un archivo .rels */
function unirZip(base, destino) {
  if (destino.startsWith("/")) return destino.slice(1);
  const partes = base.split("/").slice(0, -1);
  for (const p of destino.split("/")) { if (p === "..") partes.pop(); else if (p && p !== ".") partes.push(p); }
  return partes.join("/");
}
async function relaciones(zip, ruta) {
  const dir = ruta.split("/").slice(0, -1).join("/");
  const nombre = ruta.split("/").pop();
  const f = zip.file(`${dir ? `${dir}/` : ""}_rels/${nombre}.rels`);
  const mapa = new Map();
  if (!f) return mapa;
  for (const r of todos(xml(await f.async("string")), "Relationship")) mapa.set(attr(r, "Id"), { destino: unirZip(ruta, attr(r, "Target") || ""), tipo: attr(r, "Type") || "", externo: attr(r, "TargetMode") === "External" });
  return mapa;
}
const MIME_IMG = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", bmp: "image/bmp", svg: "image/svg+xml", webp: "image/webp", emf: "image/emf", wmf: "image/wmf", tif: "image/tiff", tiff: "image/tiff" };
async function imagenDe(zip, ruta) {
  const f = zip.file(ruta);
  if (!f) return null;
  const ext = ruta.split(".").pop().toLowerCase();
  if (ext === "emf" || ext === "wmf" || ext === "tif" || ext === "tiff") return null;   // los navegadores no los muestran
  return `data:${MIME_IMG[ext] || "image/png"};base64,${await f.async("base64")}`;
}

// ------------------------------------------------------------------------------------------- Word ----
export async function htmlDocx(bytes) {
  const m = await mammoth();
  const r = await m.convertToHtml({ arrayBuffer: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) }, {
    styleMap: ["p[style-name='Title'] => h1.titulo:fresh", "p[style-name='Título'] => h1.titulo:fresh", "p[style-name='Subtitle'] => p.subtitulo:fresh", "p[style-name='Quote'] => blockquote:fresh", "p[style-name='Cita'] => blockquote:fresh"],
  });
  const avisos = r.messages.filter((x) => x.type === "warning").length;
  return { html: `<article class="docx">${r.value || "<p><i>(El documento está vacío.)</i></p>"}</article>`, nota: avisos ? "Algunos estilos especiales de Word se muestran de forma simple." : "" };
}

// ------------------------------------------------------------------------------------------ Excel ----
const letraCol = (n) => { let s = ""; n++; while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); } return s; };
function celda(ref) {
  const m = /^([A-Z]+)(\d+)$/.exec(ref || "");
  if (!m) return null;
  let c = 0;
  for (const ch of m[1]) c = c * 26 + (ch.charCodeAt(0) - 64);
  return { f: Number(m[2]) - 1, c: c - 1 };
}
const FORMATOS_FECHA = new Set([14, 15, 16, 17, 22, 27, 30, 36, 50, 57]);
function fechaExcel(serial, conHora) {
  const ms = Math.round((serial - 25569) * 86400000);
  const d = new Date(ms);
  if (Number.isNaN(d.getTime())) return String(serial);
  const p = (x) => String(x).padStart(2, "0");
  const fecha = `${p(d.getUTCDate())}/${p(d.getUTCMonth() + 1)}/${d.getUTCFullYear()}`;
  return conHora && (d.getUTCHours() || d.getUTCMinutes()) ? `${fecha} ${p(d.getUTCHours())}:${p(d.getUTCMinutes())}` : fecha;
}
function numero(v, codigo) {
  const n = Number(v);
  if (!Number.isFinite(n)) return v;
  if (/%/.test(codigo || "")) return `${(n * 100).toLocaleString("es", { maximumFractionDigits: (codigo.split(".")[1] || "").replace(/[^0]/g, "").length })}%`;
  const dec = /0\.(0+)/.exec(codigo || "");
  const moneda = /[$€£]/.exec(codigo || "");
  const t = n.toLocaleString("es", dec ? { minimumFractionDigits: dec[1].length, maximumFractionDigits: dec[1].length } : { maximumFractionDigits: 10 });
  return moneda ? `${moneda[0]}${t}` : t;
}

export async function htmlXlsx(bytes, { maxFilas = 3000, maxCols = 80 } = {}) {
  const zip = await (await jszip()).loadAsync(bytes);
  const libro = zip.file("xl/workbook.xml");
  if (!libro) throw new Error("No parece un libro de Excel (.xlsx).");
  const rels = await relaciones(zip, "xl/workbook.xml");
  const compartidos = [];
  const ss = zip.file("xl/sharedStrings.xml");
  if (ss) for (const si of todos(xml(await ss.async("string")), "si")) compartidos.push(todos(si, "t").filter((t) => t.parentNode.localName !== "rPh").map((t) => t.textContent).join(""));
  // estilos: qué celdas son fechas, porcentajes, moneda…
  const formatos = [];
  const codigos = new Map([[1, "0"], [2, "0.00"], [3, "#,##0"], [4, "#,##0.00"], [9, "0%"], [10, "0.00%"], [11, "0.00E+00"]]);   // los de fábrica de Excel
  const est = zip.file("xl/styles.xml");
  if (est) {
    const d = xml(await est.async("string"));
    for (const nf of todos(d, "numFmt")) codigos.set(Number(attr(nf, "numFmtId")), attr(nf, "formatCode") || "");
    const xfs = uno(d, "cellXfs");
    for (const xf of hijos(xfs, "xf")) {
      const id = Number(attr(xf, "numFmtId") || 0);
      const codigo = codigos.get(id) || "";
      formatos.push({ id, codigo, fecha: FORMATOS_FECHA.has(id) || (id >= 164 && /(^|[^"\\])[dmyhs]/i.test(codigo.replace(/"[^"]*"/g, "").replace(/\[[^\]]*\]/g, ""))),
        negrita: false, alinear: attr(hijo(xf, "alignment"), "horizontal") });
    }
    const fuentes = hijos(uno(d, "fonts"), "font");
    hijos(xfs, "xf").forEach((xf, i) => { const f = fuentes[Number(attr(xf, "fontId") || 0)]; if (f && hijo(f, "b")) formatos[i].negrita = true; });
  }
  const hojas = [];
  for (const h of todos(xml(await libro.async("string")), "sheet")) {
    const r = rels.get(rid(h, "id"));
    if (!r || attr(h, "state") === "hidden" || attr(h, "state") === "veryHidden") continue;
    const archivo = zip.file(r.destino);
    if (!archivo) continue;
    const d = xml(await archivo.async("string"));
    const filas = new Map();
    let maxF = -1, maxC = -1, cortada = false;
    for (const fila of todos(d, "row")) {
      for (const c of hijos(fila, "c")) {
        const pos = celda(attr(c, "r"));
        if (!pos) continue;
        if (pos.f >= maxFilas || pos.c >= maxCols) { cortada = true; continue; }
        const t = attr(c, "t");
        const v = hijo(c, "v")?.textContent ?? "";
        const estilo = formatos[Number(attr(c, "s") || 0)] || {};
        let texto = "", tipo = "texto";
        if (t === "s") texto = compartidos[Number(v)] ?? "";
        else if (t === "inlineStr") texto = todos(hijo(c, "is"), "t").map((x) => x.textContent).join("");
        else if (t === "b") { texto = v === "1" ? "VERDADERO" : "FALSO"; tipo = "logico"; }
        else if (t === "e") { texto = v; tipo = "error"; }
        else if (t === "str") texto = v;
        else if (v === "" && hijo(c, "f")) { texto = `=${hijo(c, "f").textContent}`; tipo = "formula"; }   // sin valor guardado: se muestra la fórmula
        else if (v !== "") { tipo = "numero"; texto = estilo.fecha ? fechaExcel(Number(v), /[hs]/i.test(estilo.codigo)) : numero(v, estilo.codigo); }
        if (texto === "" && !hijo(c, "f")) continue;
        if (!filas.has(pos.f)) filas.set(pos.f, new Map());
        filas.get(pos.f).set(pos.c, { texto, tipo, negrita: estilo.negrita, alinear: estilo.alinear, formula: hijo(c, "f")?.textContent || "" });
        maxF = Math.max(maxF, pos.f); maxC = Math.max(maxC, pos.c);
      }
    }
    const anchos = new Map();
    for (const col of todos(d, "col")) for (let i = Number(attr(col, "min")) - 1; i < Math.min(Number(attr(col, "max")), maxCols); i++) anchos.set(i, Math.min(500, Math.round(Number(attr(col, "width") || 8.43) * 7 + 5)));
    const ocultas = new Set();
    const combinadas = new Map();
    for (const mc of todos(d, "mergeCell")) {
      const [a, b] = (attr(mc, "ref") || "").split(":").map(celda);
      if (!a || !b) continue;
      combinadas.set(`${a.f},${a.c}`, { filas: b.f - a.f + 1, cols: b.c - a.c + 1 });
      for (let f = a.f; f <= b.f; f++) for (let c = a.c; c <= b.c; c++) if (f !== a.f || c !== a.c) ocultas.add(`${f},${c}`);
    }
    const nCols = Math.max(maxC + 1, 6), nFilas = Math.max(maxF + 1, 12);
    let html = `<table class="xlsx"><colgroup><col class="xl-num">${Array.from({ length: nCols }, (_, c) => `<col style="width:${anchos.get(c) || 72}px">`).join("")}</colgroup>`;
    html += `<thead><tr><th class="xl-esquina"></th>${Array.from({ length: nCols }, (_, c) => `<th>${letraCol(c)}</th>`).join("")}</tr></thead><tbody>`;
    for (let f = 0; f < nFilas; f++) {
      html += `<tr><th>${f + 1}</th>`;
      for (let c = 0; c < nCols; c++) {
        const k = `${f},${c}`;
        if (ocultas.has(k)) continue;
        const x = filas.get(f)?.get(c);
        const comb = combinadas.get(k);
        const clases = [x?.tipo === "numero" ? "n" : "", x?.tipo === "error" ? "e" : "", x?.tipo === "formula" ? "fx" : "", x?.negrita ? "b" : "", x?.alinear ? `a-${x.alinear}` : ""].filter(Boolean).join(" ");
        html += `<td${comb ? ` rowspan="${comb.filas}" colspan="${comb.cols}"` : ""}${clases ? ` class="${clases}"` : ""}${x?.formula ? ` title="=${esc(x.formula)}"` : ""}>${esc(x?.texto ?? "")}</td>`;
      }
      html += "</tr>";
    }
    html += "</tbody></table>";
    hojas.push({ nombre: attr(h, "name") || `Hoja ${hojas.length + 1}`, html, cortada });
  }
  if (!hojas.length) throw new Error("El libro no tiene hojas visibles.");
  // Pestañas de hojas sin JavaScript (el visor no ejecuta scripts): radios + etiquetas, como en Excel abajo
  const radios = hojas.map((_, i) => `<input type="radio" name="hoja" id="h${i}" ${i ? "" : "checked"}>`).join("");
  const etiquetas = hojas.map((h, i) => `<label for="h${i}">${esc(h.nombre)}</label>`).join("");
  const cuerpos = hojas.map((h, i) => `<section class="hoja" data-i="${i}">${h.html}${h.cortada ? `<p class="corte">Se muestran las primeras ${maxFilas} filas y ${maxCols} columnas.</p>` : ""}</section>`).join("");
  const reglas = hojas.map((_, i) => `#h${i}:checked~.hojas .hoja[data-i="${i}"]{display:block}#h${i}:checked~.pestanas label[for="h${i}"]{background:#fff;color:#166534;border-color:#cbd5e1;font-weight:700;box-shadow:inset 0 3px #16a34a}`).join("");
  return { html: `<style>${reglas}</style><div class="libro">${radios}<div class="hojas">${cuerpos}</div><nav class="pestanas">${etiquetas}</nav></div>`, nota: hojas.length > 1 ? `${hojas.length} hojas: cámbialas con las pestañas de abajo.` : "" };
}

// ------------------------------------------------------------------------------------- PowerPoint ----
const EMU = 12700;   // 1 punto = 12700 EMU
async function tema(zip, rutaMaestro) {
  const colores = { dk1: "000000", lt1: "FFFFFF", dk2: "1F497D", lt2: "EEECE1", accent1: "4F81BD", accent2: "C0504D", accent3: "9BBB59", accent4: "8064A2", accent5: "4BACC6", accent6: "F79646", hlink: "0000FF", folHlink: "800080" };
  const rels = await relaciones(zip, rutaMaestro);
  const t = [...rels.values()].find((r) => r.tipo.endsWith("/theme"));
  const f = t && zip.file(t.destino);
  if (f) {
    const esquema = uno(xml(await f.async("string")), "clrScheme");
    for (const c of esquema ? [...esquema.children] : []) {
      const v = attr(uno(c, "srgbClr"), "val") || attr(uno(c, "sysClr"), "lastClr");
      if (v) colores[c.localName] = v;
    }
  }
  return colores;
}
function color(n, colores) {
  if (!n) return null;
  const s = uno(n, "srgbClr"), e = uno(n, "schemeClr"), sys = uno(n, "sysClr");
  let hex = s ? attr(s, "val") : e ? colores[{ tx1: "dk1", bg1: "lt1", tx2: "dk2", bg2: "lt2" }[attr(e, "val")] || attr(e, "val")] : sys ? attr(sys, "lastClr") : null;
  if (!hex) return null;
  const base = s || e || sys;
  let [r, g, b] = [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const lum = hijo(base, "lumMod"), off = hijo(base, "lumOff"), tint = hijo(base, "tint"), shade = hijo(base, "shade");
  if (lum || off) { const m = Number(attr(lum, "val") || 100000) / 100000, o = Number(attr(off, "val") || 0) / 100000; [r, g, b] = [r, g, b].map((x) => Math.round(Math.min(255, x * m + 255 * o))); }
  if (tint) { const t = Number(attr(tint, "val")) / 100000; [r, g, b] = [r, g, b].map((x) => Math.round(x * t + 255 * (1 - t))); }
  if (shade) { const t = Number(attr(shade, "val")) / 100000; [r, g, b] = [r, g, b].map((x) => Math.round(x * t)); }
  const alfa = hijo(base, "alpha");
  return alfa ? `rgba(${r},${g},${b},${Number(attr(alfa, "val")) / 100000})` : `rgb(${r},${g},${b})`;
}
/** Posición y tamaño de un placeholder heredado de la plantilla o el patrón (type/idx). */
function lugaresDe(doc) {
  const m = new Map();
  for (const sp of todos(doc, "sp")) {
    const ph = uno(sp, "ph");
    const x = uno(hijo(sp, "spPr"), "xfrm");
    if (!ph || !x) continue;
    const caja = cajaDe(x);
    const tipo = attr(ph, "type") || "body", idx = attr(ph, "idx");
    if (idx != null && !m.has(`i${idx}`)) m.set(`i${idx}`, caja);
    if (!m.has(`t${tipo}`)) m.set(`t${tipo}`, caja);
  }
  return m;
}
function cajaDe(xfrm) {
  const off = hijo(xfrm, "off"), ext = hijo(xfrm, "ext");
  return { x: Number(attr(off, "x") || 0), y: Number(attr(off, "y") || 0), w: Number(attr(ext, "cx") || 0), h: Number(attr(ext, "cy") || 0), rot: Number(attr(xfrm, "rot") || 0) / 60000 };
}
function textoHTML(txBody, colores, tipoPh) {
  if (!txBody) return "";
  const porDefecto = tipoPh === "title" || tipoPh === "ctrTitle" ? 40 : tipoPh === "subTitle" ? 24 : 18;
  const parrafos = hijos(txBody, "p").map((p) => {
    const pPr = hijo(p, "pPr");
    const alinear = { ctr: "center", r: "right", just: "justify", l: "left" }[attr(pPr, "algn")] || (tipoPh === "ctrTitle" || tipoPh === "subTitle" ? "center" : "");
    const nivel = Number(attr(pPr, "lvl") || 0);
    const vineta = hijo(pPr, "buChar") ? attr(hijo(pPr, "buChar"), "char") : hijo(pPr, "buAutoNum") ? "•" : hijo(pPr, "buNone") ? null : tipoPh === "body" || tipoPh === "obj" ? "•" : null;
    let html = "";
    let tam = porDefecto;
    for (const r of [...p.children]) {
      if (r.localName === "br") { html += "<br>"; continue; }
      if (r.localName !== "r" && r.localName !== "fld") continue;
      const rPr = hijo(r, "rPr");
      const sz = attr(rPr, "sz");
      if (sz) tam = Number(sz) / 100;
      const c = color(hijo(rPr, "solidFill"), colores);
      const estilo = [sz ? `font-size:${Number(sz) / 100}pt` : "", attr(rPr, "b") === "1" ? "font-weight:700" : "", attr(rPr, "i") === "1" ? "font-style:italic" : "",
        attr(rPr, "u") && attr(rPr, "u") !== "none" ? "text-decoration:underline" : "", c ? `color:${c}` : "", hijo(rPr, "latin") ? `font-family:'${esc(attr(hijo(rPr, "latin"), "typeface"))}',sans-serif` : ""].filter(Boolean).join(";");
      html += `<span${estilo ? ` style="${estilo}"` : ""}>${esc(hijo(r, "t")?.textContent ?? "")}</span>`;
    }
    if (!html) return `<p style="margin:0;font-size:${tam}pt">&nbsp;</p>`;
    return `<p style="margin:0 0 .25em ${nivel * 1.2 + (vineta ? 1.1 : 0)}em;font-size:${porDefecto}pt;${alinear ? `text-align:${alinear};` : ""}${vineta ? "text-indent:-1.1em;" : ""}">${vineta ? `<span style="display:inline-block;width:1.1em;text-indent:0">${esc(vineta)}</span>` : ""}${html}</p>`;
  });
  const bodyPr = hijo(txBody, "bodyPr");
  const vertical = { ctr: "center", b: "flex-end" }[attr(bodyPr, "anchor")] || (tipoPh === "ctrTitle" || tipoPh === "title" ? "center" : "flex-start");
  return `<div class="txt" style="justify-content:${vertical}">${parrafos.join("")}</div>`;
}
async function formas(zip, nodo, rutaDiap, rels, colores, lugares, ancho, alto, grupo = null) {
  let html = "";
  for (const el of [...nodo.children]) {
    const tipo = el.localName;
    if (tipo === "grpSp") {
      const x = uno(hijo(el, "grpSpPr"), "xfrm");
      if (!x) { html += await formas(zip, el, rutaDiap, rels, colores, lugares, ancho, alto, grupo); continue; }
      const caja = cajaDe(x), chOff = hijo(x, "chOff"), chExt = hijo(x, "chExt");
      const g = { ...caja, cx: Number(attr(chOff, "x") || 0), cy: Number(attr(chOff, "y") || 0), cw: Number(attr(chExt, "cx") || caja.w) || 1, ch: Number(attr(chExt, "cy") || caja.h) || 1, padre: grupo };
      html += await formas(zip, el, rutaDiap, rels, colores, lugares, ancho, alto, g);
      continue;
    }
    if (!["sp", "pic", "cxnSp", "graphicFrame"].includes(tipo)) continue;
    const spPr = hijo(el, "spPr") || hijo(el, "grpSpPr");
    const ph = uno(hijo(el, "nvSpPr") || hijo(el, "nvPicPr") || el, "ph");
    const tipoPh = ph ? attr(ph, "type") || "body" : null;
    let caja = uno(spPr, "xfrm") ? cajaDe(uno(spPr, "xfrm")) : tipo === "graphicFrame" && hijo(el, "xfrm") ? cajaDe(hijo(el, "xfrm")) : null;
    if (!caja && ph) caja = lugares.get(`i${attr(ph, "idx")}`) || lugares.get(`t${tipoPh}`) || (tipoPh === "ctrTitle" ? lugares.get("ttitle") : null) || (tipoPh === "subTitle" ? lugares.get("tbody") : null);
    if (!caja) continue;
    // dentro de un grupo, las coordenadas son del grupo
    for (let g = grupo; g; g = g.padre) caja = { ...caja, x: g.x + ((caja.x - g.cx) * g.w) / g.cw, y: g.y + ((caja.y - g.cy) * g.h) / g.ch, w: (caja.w * g.w) / g.cw, h: (caja.h * g.h) / g.ch };
    const pos = `left:${(caja.x / ancho) * 100}%;top:${(caja.y / alto) * 100}%;width:${(caja.w / ancho) * 100}%;height:${(caja.h / alto) * 100}%;${caja.rot ? `transform:rotate(${caja.rot}deg);` : ""}`;
    if (tipo === "pic") {
      const r = rels.get(rid(uno(el, "blip")));
      const src = r && !r.externo ? await imagenDe(zip, r.destino) : null;
      html += src ? `<img class="fig" style="${pos}" src="${src}" alt="">` : `<div class="fig sin-img" style="${pos}">imagen</div>`;
      continue;
    }
    if (tipo === "graphicFrame") {
      const tabla = uno(el, "tbl");
      if (tabla) {
        const filas = hijos(tabla, "tr").map((tr) => `<tr>${hijos(tr, "tc").map((tc) => `<td>${hijos(uno(tc, "txBody"), "p").map((p) => esc(todos(p, "t").map((t) => t.textContent).join(""))).join("<br>")}</td>`).join("")}</tr>`).join("");
        html += `<div class="fig" style="${pos}"><table class="ptabla">${filas}</table></div>`;
      } else html += `<div class="fig sin-img" style="${pos}">gráfico</div>`;
      continue;
    }
    const relleno = hijo(spPr, "noFill") ? null : color(hijo(spPr, "solidFill"), colores);
    const ln = hijo(spPr, "ln");
    const borde = ln && !hijo(ln, "noFill") ? color(hijo(ln, "solidFill"), colores) : null;
    const geo = attr(hijo(spPr, "prstGeom"), "prst");
    const radio = geo === "ellipse" ? "50%" : geo === "roundRect" ? "12%" : "0";
    const estilo = `${pos}${relleno ? `background:${relleno};` : ""}${borde ? `border:${Math.max(1, Number(attr(ln, "w") || 12700) / EMU)}pt solid ${borde};` : ""}border-radius:${radio};`;
    html += `<div class="fig" style="${estilo}">${textoHTML(hijo(el, "txBody"), colores, tipoPh)}</div>`;
  }
  return html;
}
async function fondoDe(zip, docs, colores, rels) {
  for (const d of docs) {
    const bg = uno(d, "bg");
    if (!bg) continue;
    const c = color(uno(bg, "solidFill"), colores);
    if (c) return `background:${c};`;
    const blip = uno(bg, "blip");
    if (blip && rels) { const r = rels.get(rid(blip)); const src = r ? await imagenDe(zip, r.destino) : null; if (src) return `background:url('${src}') center/cover;`; }
    const grad = uno(bg, "gradFill");
    if (grad) { const cs = todos(grad, "gs").map((g) => color(g, colores)).filter(Boolean); if (cs.length) return `background:linear-gradient(${cs.join(",")});`; }
  }
  return "background:#fff;";
}

export async function htmlPptx(bytes, { max = 200 } = {}) {
  const zip = await (await jszip()).loadAsync(bytes);
  const pres = zip.file("ppt/presentation.xml");
  if (!pres) throw new Error("No parece una presentación de PowerPoint (.pptx).");
  const doc = xml(await pres.async("string"));
  const sz = uno(doc, "sldSz");
  const ancho = Number(attr(sz, "cx") || 9144000), alto = Number(attr(sz, "cy") || 6858000);
  const rels = await relaciones(zip, "ppt/presentation.xml");
  const rutas = todos(doc, "sldId").map((s) => rels.get(rid(s, "id"))?.destino).filter(Boolean);
  const diapositivas = [];
  for (const ruta of rutas.slice(0, max)) {
    const f = zip.file(ruta);
    if (!f) continue;
    const d = xml(await f.async("string"));
    const r = await relaciones(zip, ruta);
    const plantilla = [...r.values()].find((x) => x.tipo.endsWith("/slideLayout"));
    const docPlantilla = plantilla && zip.file(plantilla.destino) ? xml(await zip.file(plantilla.destino).async("string")) : null;
    const relsPlantilla = plantilla ? await relaciones(zip, plantilla.destino) : new Map();
    const maestro = [...relsPlantilla.values()].find((x) => x.tipo.endsWith("/slideMaster"));
    const docMaestro = maestro && zip.file(maestro.destino) ? xml(await zip.file(maestro.destino).async("string")) : null;
    const colores = await tema(zip, maestro?.destino || "ppt/slideMasters/slideMaster1.xml");
    const lugares = new Map([...(docMaestro ? lugaresDe(docMaestro) : new Map()), ...(docPlantilla ? lugaresDe(docPlantilla) : new Map())]);
    const fondo = await fondoDe(zip, [d, docPlantilla, docMaestro].filter(Boolean), colores, r);
    const arbol = uno(d, "spTree");
    const contenido = arbol ? await formas(zip, arbol, ruta, r, colores, lugares, ancho, alto) : "";
    // notas del orador
    const notas = [...r.values()].find((x) => x.tipo.endsWith("/notesSlide"));
    let textoNotas = "";
    if (notas && zip.file(notas.destino)) {
      const dn = xml(await zip.file(notas.destino).async("string"));
      textoNotas = todos(dn, "sp").filter((sp) => attr(uno(sp, "ph"), "type") === "body").map((sp) => hijos(uno(sp, "txBody"), "p").map((p) => todos(p, "t").map((t) => t.textContent).join("")).join("\n")).join("\n").trim();
    }
    diapositivas.push(`<figure class="diapo"><div class="lienzo" style="aspect-ratio:${ancho}/${alto};${fondo}"><div class="escala" style="--ancho:${ancho / EMU}">${contenido}</div></div><figcaption>${diapositivas.length + 1} / ${rutas.length}${textoNotas ? ` · <span class="notas">Notas: ${esc(textoNotas)}</span>` : ""}</figcaption></figure>`);
  }
  return { html: `<div class="presentacion">${diapositivas.join("")}</div>`, nota: `${rutas.length} diapositiva${rutas.length === 1 ? "" : "s"}${rutas.length > max ? ` (se muestran las primeras ${max})` : ""}.`, ancho: ancho / EMU };
}

// -------------------------------------------------------------------------- todo junto en un iframe ----
const CSS = `
*{box-sizing:border-box}html,body{margin:0;background:#e5e7eb;color:#111827;font:15px/1.5 Calibri,Carlito,"Segoe UI",system-ui,sans-serif}
.docx{max-width:816px;min-height:1056px;margin:24px auto;padding:72px 84px;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.18);border-radius:2px;font-size:11pt;line-height:1.55;overflow-wrap:anywhere}
.docx h1{font-size:20pt;margin:.6em 0 .3em;color:#1f3864}.docx h1.titulo{font-size:28pt;color:#111827}.docx h2{font-size:16pt;color:#2f5496}.docx h3{font-size:13pt;color:#1f3763}
.docx p{margin:0 0 .6em}.docx .subtitulo{color:#475569;font-size:14pt}.docx img{max-width:100%;height:auto}.docx blockquote{margin:.6em 0;padding:.2em 1em;border-left:4px solid #94a3b8;color:#334155}
.docx table{border-collapse:collapse;margin:.6em 0;width:100%}.docx td,.docx th{border:1px solid #94a3b8;padding:4px 8px;vertical-align:top}
.libro{display:flex;flex-direction:column;height:100vh}.libro>input{display:none}
.libro .hojas{flex:1;min-height:0;overflow:auto;background:#fff}.hoja{display:none}
.pestanas{display:flex;gap:2px;overflow-x:auto;padding:0 8px;background:#e5e7eb;border-top:1px solid #cbd5e1}
.pestanas label{padding:7px 16px;border:1px solid transparent;border-top:0;border-radius:0 0 8px 8px;background:#f1f5f9;color:#334155;font:600 13px system-ui;cursor:pointer;white-space:nowrap}
.xlsx{border-collapse:collapse;table-layout:fixed;font:13px Calibri,Carlito,Arial,sans-serif;background:#fff}
.xlsx th{position:sticky;top:0;z-index:2;background:#f3f4f6;color:#475569;font-weight:500;border:1px solid #d1d5db;padding:2px 4px;text-align:center}
.xlsx tbody th{position:sticky;left:0;z-index:1;min-width:40px}.xlsx .xl-esquina{left:0;z-index:3}.xlsx col.xl-num{width:44px}
.xlsx td{border:1px solid #e5e7eb;padding:2px 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;height:21px}
.xlsx td.n{text-align:right}.xlsx td.fx{color:#64748b;font-style:italic}.xlsx td.e{color:#b91c1c}.xlsx td.b{font-weight:700}.xlsx td.a-center{text-align:center}.xlsx td.a-right{text-align:right}.xlsx td.a-left{text-align:left}
.corte{padding:8px 12px;color:#64748b;font:13px system-ui}
.presentacion{display:grid;gap:22px;padding:22px;justify-items:center}
.diapo{margin:0;width:min(100%,960px)}.lienzo{position:relative;width:100%;overflow:hidden;box-shadow:0 3px 14px rgba(0,0,0,.22);border-radius:4px;container-type:inline-size}
.escala{position:absolute;inset:0;--pt:calc(100cqw / var(--ancho));font-size:calc(var(--pt) * 18)}
.fig{position:absolute;overflow:hidden;display:flex}.fig.sin-img{align-items:center;justify-content:center;background:#f1f5f9;color:#94a3b8;font:12px system-ui;border:1px dashed #cbd5e1}
img.fig{object-fit:fill}
.txt{display:flex;flex-direction:column;width:100%;height:100%;padding:.4em .6em;font-size:1em;line-height:1.2;overflow:hidden}
.ptabla{border-collapse:collapse;width:100%;height:100%;font-size:.8em}.ptabla td{border:1px solid #94a3b8;padding:.2em .4em;background:#fff}
figcaption{margin-top:6px;color:#475569;font:12.5px system-ui;text-align:center}.notas{color:#64748b}
`;

/** Pinta el documento en el contenedor (un iframe aislado). Devuelve { nota } o lanza un error con el motivo. */
export async function mostrarOffice(contenedor, bytes, ext) {
  ext = ext.toLowerCase();
  if (["doc", "xls", "ppt"].includes(ext)) throw new Error(`Los archivos .${ext} son del formato antiguo de Office. Ábrelo y guárdalo como .${ext}x para verlo aquí.`);
  if (["odt", "ods", "odp", "rtf"].includes(ext)) throw new Error(`Por ahora la vista previa es para Word (.docx), Excel (.xlsx) y PowerPoint (.pptx). Guarda el archivo .${ext} en uno de esos formatos.`);
  const r = ext === "docx" ? await htmlDocx(bytes) : ext === "xlsx" || ext === "xlsm" ? await htmlXlsx(bytes) : ext === "pptx" ? await htmlPptx(bytes) : null;
  if (!r) throw new Error("Este documento no tiene vista previa.");
  const marco = document.createElement("iframe");
  marco.className = "visor-office";
  marco.title = "Vista previa del documento";
  marco.setAttribute("sandbox", "");   // sin scripts, sin formularios, sin ventanas: solo se muestra
  // Las pt de PowerPoint se escalan al ancho de la diapositiva: 1pt de la diapositiva = var(--pt) en pantalla
  const html = ext === "pptx" ? r.html.replace(/font-size:([\d.]+)pt/g, (_, n) => `font-size:calc(var(--pt) * ${Number(n)})`) : r.html;
  marco.srcdoc = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>${CSS}</style></head><body>${html}</body></html>`;
  contenedor.replaceChildren(marco);
  return { nota: r.nota };
}
