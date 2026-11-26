// Visor de archivos: ocupa el lugar del editor cuando el archivo abierto no es texto editable
// (imagen, video, audio, PDF o cualquier otro archivo guardado en la cuenta).
// Tiene la misma forma que Editor (raiz, ta, mostrar, ocultar, establecer…) para que trabajo.js lo trate igual.
import { clase, formatoBytes, leerMarcador } from "./archivos.js";
import { extension, nombreBase } from "./fs.js";

const OFFICE = { docx: "Word", doc: "Word", xlsx: "Excel", xlsm: "Excel", xls: "Excel", pptx: "PowerPoint", ppt: "PowerPoint", odt: "Documento", ods: "Hoja de cálculo", odp: "Presentación", rtf: "Documento" };
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export class VisorArchivo {
  /** @param {{ ruta: string, texto: string, url: (marcador:string, o?:object)=>string|null }} o */
  constructor({ ruta, texto, url, preparar = null }) {
    this.preparar = preparar;   // archivos de tu equipo: se leen del disco la primera vez que los abres
    this.esImagen = true; // «no es texto editable» (trabajo.js usa esta marca)
    this.ruta = ruta;
    this.ext = extension(ruta);
    this.url = url;
    this.texto = texto;
    this.raiz = document.createElement("div");
    this.raiz.className = "visor-imagen";
    this.raiz.tabIndex = 0;
    this.raiz.hidden = true;
    this.ta = this.raiz; // trabajo.js le envía eventos de foco al «textarea»
    this.#pintar();
  }

  get lenguaje() { const m = leerMarcador(this.texto); return OFFICE[this.ext] ?? (m ? { imagen: "Imagen", video: "Video", audio: "Audio", pdf: "PDF" }[clase(m.tipo)] ?? "Archivo" : "Archivo"); }
  leer() { return this.texto; }
  establecer(texto) { if (texto !== this.texto) { this.texto = texto; this.#pintar(); } }
  renombrar(ruta) { this.ruta = ruta; this.ext = extension(ruta); this.#pintar(); }
  mostrar() { this.raiz.hidden = false; }
  ocultar() { this.raiz.hidden = true; this.raiz.querySelectorAll("video, audio").forEach((m) => m.pause()); }
  enfocar() { this.raiz.focus({ preventScroll: true }); }
  irALinea() {}
  destruir() { this.raiz.querySelectorAll("video, audio").forEach((m) => { m.pause(); m.removeAttribute("src"); }); this.raiz.remove(); }

  #pintar() {
    const m = leerMarcador(this.texto);
    if (!m) { this.raiz.innerHTML = '<p class="visor-error">Este archivo ya no es un archivo guardado en la cuenta. Ciérralo y vuelve a abrirlo.</p>'; return; }
    const nombre = nombreBase(this.ruta);
    const kAntes = OFFICE[this.ext] ? "documento" : clase(m.tipo);
    const visible = ["imagen", "video", "audio", "pdf", "documento"].includes(kAntes) || /^text\/|json/.test(m.tipo);
    if (this.url(this.texto) === null && this.preparar && !visible) {
      // Programas, comprimidos, binarios…: como en VS Code, no se cargan; se muestran sus datos y se pueden descargar.
      const tipoC = m.tipo.split("/")[1].replace(/^x-/, "").toUpperCase();
      this.raiz.innerHTML = `<div class="visor-generico"><b>${esc(nombre)}</b><span>Archivo binario (${esc(tipoC)}) en tu equipo. No se puede ver como texto, pero puedes ejecutarlo o usarlo desde la terminal.</span></div>
        <div class="visor-info"><span>${esc(tipoC)} · ${formatoBytes(m.tamano)}</span><button type="button" class="btn sm" data-bajar>Descargar</button></div>`;
      this.raiz.querySelector("[data-bajar]").onclick = async (e) => {
        e.target.disabled = true; e.target.textContent = "Preparando…";
        try { await this.preparar(this.texto); const a = document.createElement("a"); a.href = this.url(this.texto); a.download = nombre; a.click(); }
        catch (x) { e.target.textContent = x.message || "No se pudo"; return; }
        e.target.disabled = false; e.target.textContent = "Descargar";
      };
      return;
    }
    if (this.url(this.texto) === null && this.preparar) {
      this.raiz.innerHTML = `<p class="visor-cargando">Abriendo «${esc(nombre)}» desde tu equipo…</p>`;
      const texto = this.texto;
      this.preparar(texto).then(() => { if (this.texto === texto) this.#pintar(); },
        (e) => { if (this.texto === texto) this.raiz.innerHTML = `<p class="visor-error">No se pudo abrir desde tu equipo: ${esc(e.message || "error")}</p>`; });
      return;
    }
    const src = esc(this.url(this.texto));
    const descarga = esc(this.url(this.texto, { descargar: true, nombre }));
    const tipoCorto = m.tipo.split("/")[1].replace(/^x-/, "").toUpperCase();
    const k = OFFICE[this.ext] ? "documento" : clase(m.tipo);
    if (k === "documento") { this.#documento(m, nombre, descarga); return; }
    const etiqueta = { imagen: `<img src="${this.ruta}" alt="">`, video: `<video src="${this.ruta}" controls></video>`, audio: `<audio src="${this.ruta}" controls></audio>`, pdf: `<a href="${this.ruta}">Abrir PDF</a>` }[k];
    const medio = {
      imagen: `<img alt="${esc(nombre)}" src="${src}">`,
      video: `<video controls preload="metadata" src="${src}"></video>`,
      audio: `<audio controls preload="metadata" src="${src}"></audio>`,
      pdf: `<iframe class="visor-pdf" title="${esc(nombre)}" src="${src}"></iframe>`,
    }[k] ?? (/^text\/|json/.test(m.tipo)
      ? `<pre class="visor-texto" aria-label="Contenido de ${esc(nombre)} (solo lectura)">Cargando…</pre>`
      : `<div class="visor-generico"><b>${esc(nombre)}</b><span>Este tipo de archivo no se puede ver aquí${this.preparar ? "" : ", pero está guardado en tu cuenta"}.</span></div>`);
    this.raiz.innerHTML = `${medio}
      <div class="visor-info"><span class="visor-medidas">${k === "imagen" || k === "video" ? "…" : esc(tipoCorto)}</span><span>${esc(tipoCorto)} · ${formatoBytes(m.tamano)}</span>
      ${etiqueta ? `<span>En HTML: <code>${esc(etiqueta)}</code></span>` : ""}
      <a class="btn sm" href="${descarga}" download="${esc(nombre)}">Descargar</a></div>`;
    const medidas = this.raiz.querySelector(".visor-medidas");
    const pre = this.raiz.querySelector(".visor-texto");
    if (pre) {
      // Texto demasiado grande para el editor: se muestra completo, solo para leer (hasta 5 MB en pantalla).
      fetch(this.url(this.texto), { credentials: "same-origin" }).then((r) => (r.ok ? r.blob() : Promise.reject(new Error(r.status))))
        .then(async (b) => { const t = await b.slice(0, 5 * 1024 * 1024).text(); pre.textContent = t + (b.size > 5 * 1024 * 1024 ? "\n\n… (el resto está en el archivo: descárgalo para verlo completo)" : ""); medidas.textContent = "Solo lectura: es demasiado grande para editarlo aquí"; })
        .catch(() => { pre.textContent = "No se pudo cargar el archivo."; });
    }
    const img = this.raiz.querySelector("img");
    const vid = this.raiz.querySelector("video");
    img?.addEventListener("load", () => { medidas.textContent = `${img.naturalWidth} × ${img.naturalHeight} px`; });
    vid?.addEventListener("loadedmetadata", () => { const s = Math.round(vid.duration); medidas.textContent = `${vid.videoWidth} × ${vid.videoHeight} · ${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; });
    for (const el of [img, vid, this.raiz.querySelector("audio")]) {
      el?.addEventListener("error", () => { medidas.outerHTML = '<span class="visor-error">No se pudo cargar: el archivo ya no está en tu cuenta, no hay conexión o el navegador no reproduce este formato.</span>'; });
    }
  }

  /** Word, Excel y PowerPoint: se ven aquí mismo, sin descargarlos (js/trabajo/office.js, en un marco aislado). */
  #documento(m, nombre, descarga) {
    const tipo = OFFICE[this.ext];
    const icono = { Word: "W", Excel: "X", PowerPoint: "P" }[tipo] || "D";
    this.raiz.classList.add("visor-doc");
    this.raiz.innerHTML = `<div class="doc-cab doc-${icono}"><span class="doc-ico">${icono}</span><span class="doc-nombre"><b>${esc(nombre)}</b><small>${esc(tipo)} · ${formatoBytes(m.tamano)} · <span class="doc-nota">Abriendo…</span></small></span>
      <button type="button" class="btn sm" data-doc="completa" title="Ver en pantalla completa">⛶</button><a class="btn sm" href="${descarga}" download="${esc(nombre)}">Descargar</a></div>
      <div class="doc-cuerpo"><div class="doc-cargando"><span class="doc-giro"></span>Preparando la vista previa…</div></div>`;
    const cuerpo = this.raiz.querySelector(".doc-cuerpo");
    const nota = this.raiz.querySelector(".doc-nota");
    this.raiz.querySelector('[data-doc="completa"]').onclick = () => (document.fullscreenElement ? document.exitFullscreen() : cuerpo.requestFullscreen?.())?.catch?.(() => {});
    const yo = this.texto;
    fetch(this.url(this.texto), { credentials: "same-origin" })
      .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error("No se pudo cargar el archivo (¿sin conexión?)."))))
      .then(async (buf) => {
        const { mostrarOffice } = await import("./office.js");
        if (yo !== this.texto) return;
        const r = await mostrarOffice(cuerpo, new Uint8Array(buf), this.ext);
        nota.textContent = r.nota || "Vista previa (solo lectura)";
      })
      .catch((e) => {
        nota.textContent = "Sin vista previa";
        cuerpo.innerHTML = `<div class="visor-generico"><b>${esc(nombre)}</b><span>${esc(e.message || "No se pudo mostrar este documento.")}</span><a class="btn sm" href="${descarga}" download="${esc(nombre)}">Descargar</a></div>`;
      });
  }
}
