// «Buscar en archivos» (Ctrl+Shift+F) y «Reemplazar en archivos», como en VS Code.
// buscarEnProyecto / reemplazarEnProyecto son lógica pura (con pruebas); abrirBuscador es la interfaz.
import { esMarcador } from "./archivos.js";
import { dialogo } from "./dialogos.js";
import * as FS from "./fs.js";

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** Expresión regular de la búsqueda, o { error } si la expresión escrita no es válida. */
export function patron(consulta, { mayusculas = false, palabra = false, regex = false } = {}) {
  if (!consulta) return { error: "vacía" };
  let fuente = regex ? consulta : consulta.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  if (palabra) fuente = `\\b(?:${fuente})\\b`;
  try { return { re: new RegExp(fuente, mayusculas ? "g" : "gi") }; } catch (e) { return { error: `Expresión no válida: ${e.message}` }; }
}

const incluido = (ruta, incluir, excluir) => {
  const prueba = (lista) => lista.split(",").map((x) => x.trim()).filter(Boolean).some((p) => {
    const re = new RegExp("^" + p.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*\*/g, "\u0000").replace(/\*/g, "[^/]*").replace(/\u0000/g, ".*") + "($|/)");
    return re.test(ruta) || re.test(FS.nombreBase(ruta)) || ruta.split("/").some((parte) => re.test(parte));
  });
  return (!incluir || prueba(incluir)) && !(excluir && prueba(excluir));
};

/**
 * Busca en todos los archivos de texto del proyecto.
 * @returns {{ archivos: {ruta, coincidencias: {linea, col, largo, texto}[]}[], total: number, error?: string }}
 */
export function buscarEnProyecto(py, consulta, opciones = {}) {
  const { re, error } = patron(consulta, opciones);
  if (error) return { archivos: [], total: 0, error: error === "vacía" ? undefined : error };
  const archivos = [];
  let total = 0;
  for (const ruta of Object.keys(py.files).sort()) {
    const texto = py.files[ruta];
    if (esMarcador(texto) || !incluido(ruta, opciones.incluir, opciones.excluir ?? "node_modules")) continue;
    const coincidencias = [];
    texto.split("\n").forEach((l, i) => {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(l)) && coincidencias.length < 1000) {
        if (m[0] === "") { re.lastIndex += 1; continue; }
        coincidencias.push({ linea: i + 1, col: m.index + 1, largo: m[0].length, texto: l });
      }
    });
    if (coincidencias.length) { archivos.push({ ruta, coincidencias }); total += coincidencias.length; }
    if (total > 20000) break;
  }
  return { archivos, total };
}

/** Reemplaza en todo el proyecto. Devuelve { cambiados: {ruta: textoAnterior}, total } para poder deshacer. */
export function reemplazarEnProyecto(py, consulta, reemplazo, opciones = {}) {
  const { re, error } = patron(consulta, opciones);
  if (error) return { cambiados: {}, total: 0 };
  const cambiados = {};
  let total = 0;
  for (const { ruta } of buscarEnProyecto(py, consulta, opciones).archivos) {
    const antes = py.files[ruta];
    let n = 0;
    const despues = antes.replace(re, (...args) => { n += 1; return opciones.regex ? args[0].replace(new RegExp(re.source, re.flags.replace("g", "")), reemplazo) : reemplazo; });
    if (despues !== antes) { cambiados[ruta] = antes; py.files[ruta] = despues; total += n; }
  }
  return { cambiados, total };
}

/**
 * Panel de búsqueda. o: { proyecto, abrirEn(ruta, linea, col, largo), alCambiar(info), aviso }
 */
export function abrirBuscador({ proyecto, abrirEn, alCambiar, aviso, inicial = "" }) {
  document.querySelector(".buscador")?.remove();
  const d = document.createElement("dialog");
  d.className = "ide-dialogo buscador";
  d.innerHTML = `<form method="dialog" class="buscador-form">
    <h3>Buscar en archivos</h3>
    <div class="buscador-fila"><input name="q" placeholder="Buscar" spellcheck="false" autocomplete="off" aria-label="Texto a buscar">
      <button type="button" class="opcion" data-op="mayusculas" title="Distinguir mayúsculas (Alt+C)" aria-pressed="false">Aa</button>
      <button type="button" class="opcion" data-op="palabra" title="Palabra completa (Alt+W)" aria-pressed="false">ab</button>
      <button type="button" class="opcion" data-op="regex" title="Expresión regular (Alt+R)" aria-pressed="false">.*</button></div>
    <div class="buscador-fila"><input name="r" placeholder="Reemplazar" spellcheck="false" autocomplete="off" aria-label="Reemplazar por">
      <button type="button" class="ide-boton" data-accion="reemplazar">Reemplazar todo</button></div>
    <details><summary>Archivos que se incluyen o excluyen</summary>
      <div class="buscador-fila"><input name="inc" placeholder="Incluir (ej.: src, *.js)" aria-label="Archivos a incluir"><input name="exc" value="node_modules" placeholder="Excluir" aria-label="Archivos a excluir"></div></details>
    <p class="buscador-resumen" role="status"></p>
    <div class="buscador-resultados"></div>
    <div class="ide-dialogo-botones"><button type="button" class="ide-boton" data-accion="cerrar">Cerrar</button></div></form>`;
  document.body.appendChild(d);
  const f = d.querySelector("form");
  const ops = { mayusculas: false, palabra: false, regex: false };
  const resultados = d.querySelector(".buscador-resultados");
  const resumen = d.querySelector(".buscador-resumen");
  const opciones = () => ({ ...ops, incluir: f.inc.value, excluir: f.exc.value });
  let ultimo = null;
  const pintar = () => {
    const r = buscarEnProyecto(proyecto(), f.q.value, opciones());
    ultimo = r;
    resumen.textContent = r.error ?? (f.q.value ? `${r.total} ${r.total === 1 ? "resultado" : "resultados"} en ${r.archivos.length} ${r.archivos.length === 1 ? "archivo" : "archivos"}` : "");
    resultados.innerHTML = r.archivos.slice(0, 200).map((a) => `<div class="buscador-archivo"><div class="buscador-ruta">${esc(a.ruta)} <span>${a.coincidencias.length}</span></div>${a.coincidencias.slice(0, 50).map((c, k) => {
      const ini = Math.max(0, c.col - 1 - 40);
      const trozo = c.texto.slice(ini, c.col - 1 + c.largo + 60);
      const p = c.col - 1 - ini;
      return `<button type="button" class="buscador-linea" data-ruta="${esc(a.ruta)}" data-k="${k}"><span class="num">${c.linea}</span>${esc(trozo.slice(0, p).trimStart())}<mark>${esc(trozo.slice(p, p + c.largo))}</mark>${esc(trozo.slice(p + c.largo))}</button>`;
    }).join("")}</div>`).join("");
  };
  let t;
  f.addEventListener("input", () => { clearTimeout(t); t = setTimeout(pintar, 120); });
  d.addEventListener("click", async (e) => {
    const op = e.target.closest(".opcion");
    if (op) { ops[op.dataset.op] = !ops[op.dataset.op]; op.setAttribute("aria-pressed", String(ops[op.dataset.op])); pintar(); return; }
    const l = e.target.closest(".buscador-linea");
    if (l) {
      const a = ultimo.archivos.find((x) => x.ruta === l.dataset.ruta);
      const c = a.coincidencias[Number(l.dataset.k)];
      d.close();
      abrirEn(a.ruta, c.linea, c.col, c.largo);
      return;
    }
    const acc = e.target.closest("[data-accion]")?.dataset.accion;
    if (acc === "cerrar") d.close();
    if (acc === "reemplazar" && f.q.value) {
      const r = buscarEnProyecto(proyecto(), f.q.value, opciones());
      if (!r.total) return;
      const ok = await dialogo({ titulo: "¿Reemplazar en todos los archivos?", mensaje: `Se cambiarán ${r.total} coincidencias en ${r.archivos.length} archivos por «${f.r.value}».`, botones: [{ texto: "Reemplazar", valor: true, peligro: true }, { texto: "Cancelar", valor: false, cancelar: true }] });
      if (!ok) return;
      const py = proyecto();
      const { cambiados, total } = reemplazarEnProyecto(py, f.q.value, f.r.value, opciones());
      alCambiar({ origen: "buscar" });
      aviso(`${total} reemplazos en ${Object.keys(cambiados).length} archivos.`, { ms: 10000, accion: { texto: "Deshacer", fn: () => { Object.assign(proyecto().files, cambiados); alCambiar({ origen: "buscar" }); } } });
      pintar();
    }
  });
  d.addEventListener("keydown", (e) => {
    if (!e.altKey) return;
    const k = { c: "mayusculas", w: "palabra", r: "regex" }[e.key.toLowerCase()];
    if (k) { e.preventDefault(); d.querySelector(`[data-op="${k}"]`).click(); }
  });
  d.addEventListener("close", () => d.remove());
  d.showModal();
  f.q.value = inicial;
  f.q.focus();
  if (inicial) pintar();
}
