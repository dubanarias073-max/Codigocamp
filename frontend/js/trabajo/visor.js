// Visor de archivos: ocupa el lugar del editor cuando el archivo abierto no es texto editable
// (imagen, video, audio, PDF o cualquier otro archivo guardado en la cuenta).
// Tiene la misma forma que Editor (raiz, ta, mostrar, ocultar, establecer…) para que trabajo.js lo trate igual.
import { clase, formatoBytes, leerMarcador } from "./archivos.js";
import { extension, nombreBase } from "./fs.js";

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export class VisorArchivo {
  /** @param {{ ruta: string, texto: string, url: (marcador:string, o?:object)=>string|null }} o */
  constructor({ ruta, texto, url }) {
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

  get lenguaje() { const m = leerMarcador(this.texto); return m ? { imagen: "Imagen", video: "Video", audio: "Audio", pdf: "PDF" }[clase(m.tipo)] ?? "Archivo" : "Archivo"; }
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
    const src = esc(this.url(this.texto));
    const descarga = esc(this.url(this.texto, { descargar: true, nombre }));
    const tipoCorto = m.tipo.split("/")[1].replace(/^x-/, "").toUpperCase();
    const k = clase(m.tipo);
    const etiqueta = { imagen: `<img src="${this.ruta}" alt="">`, video: `<video src="${this.ruta}" controls></video>`, audio: `<audio src="${this.ruta}" controls></audio>`, pdf: `<a href="${this.ruta}">Abrir PDF</a>` }[k];
    const medio = {
      imagen: `<img alt="${esc(nombre)}" src="${src}">`,
      video: `<video controls preload="metadata" src="${src}"></video>`,
      audio: `<audio controls preload="metadata" src="${src}"></audio>`,
      pdf: `<iframe class="visor-pdf" title="${esc(nombre)}" src="${src}"></iframe>`,
    }[k] ?? (/^text\/|json/.test(m.tipo)
      ? `<pre class="visor-texto" aria-label="Contenido de ${esc(nombre)} (solo lectura)">Cargando…</pre>`
      : `<div class="visor-generico"><b>${esc(nombre)}</b><span>Este tipo de archivo no se puede ver aquí, pero está guardado en tu cuenta.</span></div>`);
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
}
