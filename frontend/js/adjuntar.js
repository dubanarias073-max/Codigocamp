// Adjuntar archivos (fotos, videos, audio, PDF, código, cualquier archivo; hasta 1 GB cada uno) en Chats y en la IA.
// Botón 📎, arrastrar y soltar, o pegar (Ctrl+V) una imagen. Se suben con progreso al almacén de la cuenta.
import { ClienteArchivos, formatoBytes } from "/js/trabajo/archivos.js";
import { api, esc, aviso } from "/js/app.js";

const cliente = new ClienteArchivos();
const ICONO = { imagen: "🖼️", video: "🎬", audio: "🎵", pdf: "📕", archivo: "📄" };
const MAX = 10;

/**
 * @param {object} o { boton, entrada (input file), bandeja (div para las fichas), zona (donde se puede soltar/pegar), destino: "chat"|"ia" }
 * @returns {{ ids(): number[], listos(): Promise<number[]>, limpiar(), hay(): boolean, adjuntos(): object[] }}
 */
export function crearAdjuntador({ boton, entrada, bandeja, zona, destino }) {
  let lista = [];
  const pintar = () => {
    bandeja.hidden = !lista.length;
    bandeja.innerHTML = lista.map((x, i) => `<span class="adj-ficha${x.error ? " error" : x.listo ? "" : " subiendo"}" title="${esc(x.nombre)}">
      ${x.vista ? `<img src="${x.vista}" alt="">` : `<span class="adj-ic">${ICONO[x.clase] || "📄"}</span>`}
      <span class="adj-txt"><b>${esc(x.nombre)}</b><small>${x.error ? esc(x.error) : x.listo ? formatoBytes(x.tamano) : `Subiendo ${Math.round(x.progreso * 100)}%`}</small></span>
      ${!x.listo && !x.error ? `<i class="adj-barra" style="width:${Math.round(x.progreso * 100)}%"></i>` : ""}
      <button type="button" class="adj-quitar" data-i="${i}" aria-label="Quitar ${esc(x.nombre)}">×</button></span>`).join("");
  };
  const clase = (t) => (t.startsWith("image/") ? "imagen" : t.startsWith("video/") ? "video" : t.startsWith("audio/") ? "audio" : t === "application/pdf" ? "pdf" : "archivo");
  async function agregar(archivos) {
    for (const f of archivos) {
      if (lista.length >= MAX) { aviso(`Máximo ${MAX} archivos por mensaje.`, true); break; }
      const x = { nombre: f.name || "imagen.png", tamano: f.size, clase: clase(f.type || ""), progreso: 0, listo: false, vista: f.type?.startsWith("image/") && f.size < 30e6 ? URL.createObjectURL(f) : null };
      lista.push(x);
      pintar();
      x.promesa = (async () => {
        try {
          const marcador = await cliente.subir(f, { nombre: x.nombre, progreso: (p) => { x.progreso = p; pintar(); } });
          const r = await api("/api/adjuntos/", { marcador, nombre: x.nombre, destino });
          Object.assign(x, { id: r.adjunto.id, listo: true, clase: r.adjunto.clase });
        } catch (e) { x.error = e.message; }
        pintar();
      })();
    }
  }
  boton.onclick = () => entrada.click();
  entrada.onchange = () => { agregar([...entrada.files]); entrada.value = ""; };
  zona.addEventListener("dragover", (e) => { if (e.dataTransfer?.types?.includes("Files")) { e.preventDefault(); zona.classList.add("adj-soltar"); } });
  zona.addEventListener("dragleave", () => zona.classList.remove("adj-soltar"));
  zona.addEventListener("drop", (e) => { zona.classList.remove("adj-soltar"); if (e.dataTransfer?.files?.length) { e.preventDefault(); agregar([...e.dataTransfer.files]); } });
  zona.addEventListener("paste", (e) => { const f = [...(e.clipboardData?.files || [])]; if (f.length) { e.preventDefault(); agregar(f); } });
  bandeja.onclick = (e) => { const b = e.target.closest("[data-i]"); if (b) { const [x] = lista.splice(Number(b.dataset.i), 1); if (x?.vista) URL.revokeObjectURL(x.vista); pintar(); } };
  pintar();
  return {
    hay: () => lista.length > 0,
    adjuntos: () => lista.filter((x) => x.listo).map((x) => ({ nombre: x.nombre, clase: x.clase, vista: x.vista })),
    async listos() {
      await Promise.all(lista.map((x) => x.promesa));
      if (lista.some((x) => x.error)) throw new Error("Algún archivo no se pudo subir. Quítalo (×) o vuelve a intentarlo.");
      return lista.map((x) => x.id);
    },
    limpiar() { lista.forEach((x) => x.vista && URL.revokeObjectURL(x.vista)); lista = []; pintar(); },
  };
}

/** HTML para mostrar los adjuntos de un mensaje (imágenes y videos se ven ahí mismo). */
export function htmlAdjuntos(adjuntos = []) {
  if (!adjuntos.length) return "";
  return `<div class="adj-msg">${adjuntos.map((a) => {
    const url = esc(a.url);
    if (a.clase === "imagen") return `<a class="adj-img" href="${url}" target="_blank" rel="noopener"><img src="${url}" alt="${esc(a.nombre)}" loading="lazy"></a>`;
    if (a.clase === "video") return `<video class="adj-video" src="${url}" controls preload="metadata"></video>`;
    if (a.clase === "audio") return `<audio class="adj-audio" src="${url}" controls preload="metadata"></audio>`;
    return `<a class="adj-arch" href="${url}?descargar=1" download="${esc(a.nombre)}"><span>${ICONO[a.clase] || "📄"}</span><span><b>${esc(a.nombre)}</b><small>${formatoBytes(a.tamano)} · descargar</small></span></a>`;
  }).join("")}</div>`;
}

export const CSS_ADJUNTOS = `
.adj-bandeja{display:flex;flex-wrap:wrap;gap:8px;padding:8px 0}
.adj-bandeja[hidden]{display:none}
.adj-ficha{position:relative;display:flex;align-items:center;gap:8px;max-width:240px;padding:6px 30px 6px 6px;border:1px solid var(--borde);border-radius:12px;background:var(--panel2);overflow:hidden}
.adj-ficha img{width:40px;height:40px;object-fit:cover;border-radius:8px}
.adj-ic{width:40px;height:40px;display:grid;place-items:center;font-size:22px}
.adj-txt{display:grid;min-width:0}.adj-txt b{font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.adj-txt small{font-size:11px;color:var(--sub)}
.adj-ficha.error{border-color:var(--rojo)}.adj-ficha.error small{color:var(--rojo)}
.adj-barra{position:absolute;left:0;bottom:0;height:3px;background:var(--acc);transition:width .2s}
.adj-quitar{position:absolute;right:4px;top:4px;width:22px;height:22px;border:0;border-radius:50%;background:rgba(0,0,0,.15);color:inherit;cursor:pointer;font-weight:800}
.adj-clip{display:grid;place-items:center;min-width:42px;border:1px solid var(--borde);border-radius:12px;background:var(--panel2);font-size:18px;cursor:pointer;color:inherit}
.adj-soltar{outline:3px dashed var(--acc);outline-offset:4px}
.adj-msg{display:grid;gap:6px;margin-top:6px}
.adj-img img{display:block;max-width:min(320px,100%);max-height:320px;border-radius:12px;object-fit:cover}
.adj-video{max-width:min(360px,100%);border-radius:12px;background:#000}
.adj-audio{max-width:100%}
.adj-arch{display:flex;align-items:center;gap:10px;padding:8px 12px;border:1px solid var(--borde);border-radius:12px;background:var(--panel);color:inherit;text-decoration:none}
.adj-arch span:first-child{font-size:24px}.adj-arch span:last-child{display:grid}.adj-arch small{color:var(--sub)}
`;
