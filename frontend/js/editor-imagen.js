// Editor de imágenes del panel de administrador: recortar, mover, zoom, girar, voltear, filtros (brillo, contraste,
// saturación, tono, desenfoque, viñeta), forma (cuadro, redondeado, círculo) y contorno brillante. El resultado se
// «hornea» en un PNG/JPG nuevo y se sube a /api/admin/imagen (pasa por el antivirus). La original se guarda aparte
// para poder volver a editar desde cero.

const ESTADO = { zoom: 1, ox: 0, oy: 0, rot: 0, voltear: false, brillo: 100, contraste: 100, saturacion: 100, tono: 0, desenfoque: 0, vineta: 0, forma: "cuadro", radio: 22, contorno: "", grosor: 6 };
const FILTROS = {
  original: ["Original", { brillo: 100, contraste: 100, saturacion: 100, tono: 0, desenfoque: 0, vineta: 0 }],
  vivido: ["Vívido", { brillo: 108, contraste: 115, saturacion: 150, tono: 0, desenfoque: 0, vineta: 10 }],
  neon: ["Neón", { brillo: 112, contraste: 135, saturacion: 200, tono: 0, desenfoque: 0, vineta: 35 }],
  retro: ["Retro", { brillo: 105, contraste: 88, saturacion: 70, tono: -15, desenfoque: 0, vineta: 30 }],
  bn: ["B/N", { brillo: 100, contraste: 120, saturacion: 0, tono: 0, desenfoque: 0, vineta: 20 }],
  frio: ["Frío", { brillo: 102, contraste: 105, saturacion: 90, tono: -25, desenfoque: 0, vineta: 0 }],
  calido: ["Cálido", { brillo: 104, contraste: 104, saturacion: 125, tono: 14, desenfoque: 0, vineta: 0 }],
  sueno: ["Sueño", { brillo: 115, contraste: 85, saturacion: 120, tono: 0, desenfoque: 1, vineta: 25 }],
};
const DESLIZAS = [["zoom", "Zoom", 100, 400, 1], ["brillo", "Brillo", 30, 200, 1], ["contraste", "Contraste", 30, 200, 1], ["saturacion", "Saturación", 0, 300, 1],
  ["tono", "Tono", -180, 180, 1], ["desenfoque", "Desenfoque", 0, 10, 0.5], ["vineta", "Viñeta", 0, 100, 1]];
const CON_FILTRO = typeof CanvasRenderingContext2D !== "undefined" && "filter" in CanvasRenderingContext2D.prototype;

function csrf() { return decodeURIComponent((document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || ""); }

/** Sube una imagen (File o Blob) al panel. Devuelve su URL (/api/admin-img/…). */
export async function subirImagen(blob) {
  if (blob.size > 4 * 1024 * 1024) throw new Error("La imagen pesa más de 4 MB.");
  const r = await fetch("/api/admin/imagen", { method: "POST", body: blob, headers: { "X-CSRFToken": csrf(), "Content-Type": "application/octet-stream" }, credentials: "same-origin" });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || "No se pudo subir la imagen.");
  return j.url;
}

function cargar(src) {
  return new Promise((ok, mal) => { const i = new Image(); i.decoding = "async"; i.onload = () => ok(i); i.onerror = () => mal(new Error("No se pudo abrir la imagen.")); i.src = src; });
}

function camino(ctx, W, H, st, margen) {
  ctx.beginPath();
  if (st.forma === "circulo") ctx.arc(W / 2, H / 2, Math.min(W, H) / 2 - margen, 0, Math.PI * 2);
  else { const r = Math.min(W, H) * (st.radio / 100); ctx.roundRect ? ctx.roundRect(margen, margen, W - 2 * margen, H - 2 * margen, r) : ctx.rect(margen, margen, W - 2 * margen, H - 2 * margen); }
}

// Mismas fórmulas que los filtros CSS (brightness, contrast, saturate, hue-rotate) para navegadores sin ctx.filter
function filtrarPixeles(ctx, W, H, st) {
  const datos = ctx.getImageData(0, 0, W, H), p = datos.data;
  const b = st.brillo / 100, c = st.contraste / 100, s = st.saturacion / 100, a = (st.tono * Math.PI) / 180, cs = Math.cos(a), sn = Math.sin(a);
  const S = [0.213 + 0.787 * s, 0.715 - 0.715 * s, 0.072 - 0.072 * s, 0.213 - 0.213 * s, 0.715 + 0.285 * s, 0.072 - 0.072 * s, 0.213 - 0.213 * s, 0.715 - 0.715 * s, 0.072 + 0.928 * s];
  const T = [0.213 + cs * 0.787 - sn * 0.213, 0.715 - cs * 0.715 - sn * 0.715, 0.072 - cs * 0.072 + sn * 0.928, 0.213 - cs * 0.213 + sn * 0.143, 0.715 + cs * 0.285 + sn * 0.14, 0.072 - cs * 0.072 - sn * 0.283, 0.213 - cs * 0.213 - sn * 0.787, 0.715 - cs * 0.715 + sn * 0.715, 0.072 + cs * 0.928 + sn * 0.072];
  const lim = (v) => (v < 0 ? 0 : v > 255 ? 255 : v);
  for (let i = 0; i < p.length; i += 4) {
    let r = lim(lim(p[i] * b) * c + 128 * (1 - c)), g = lim(lim(p[i + 1] * b) * c + 128 * (1 - c)), bl = lim(lim(p[i + 2] * b) * c + 128 * (1 - c));
    let r2 = lim(S[0] * r + S[1] * g + S[2] * bl), g2 = lim(S[3] * r + S[4] * g + S[5] * bl), b2 = lim(S[6] * r + S[7] * g + S[8] * bl);
    p[i] = lim(T[0] * r2 + T[1] * g2 + T[2] * b2); p[i + 1] = lim(T[3] * r2 + T[4] * g2 + T[5] * b2); p[i + 2] = lim(T[6] * r2 + T[7] * g2 + T[8] * b2);
  }
  ctx.putImageData(datos, 0, 0);
}

/** Dibuja la imagen editada en un lienzo W×H. */
function dibujar(lienzo, img, st, fondo) {
  const W = lienzo.width, H = lienzo.height, ctx = lienzo.getContext("2d", { willReadFrequently: !CON_FILTRO });
  ctx.save();
  ctx.clearRect(0, 0, W, H);
  if (fondo) { ctx.fillStyle = fondo; ctx.fillRect(0, 0, W, H); }
  const margen = st.forma !== "cuadro" && st.contorno ? st.grosor * (W / 256) + 4 : 0;
  if (st.forma !== "cuadro") { camino(ctx, W, H, st, margen); ctx.clip(); }
  const girada = st.rot % 180 !== 0;
  const sw = girada ? img.height : img.width, sh = girada ? img.width : img.height;
  const esc = Math.max(W / sw, H / sh) * st.zoom;
  if (CON_FILTRO) ctx.filter = `brightness(${st.brillo}%) contrast(${st.contraste}%) saturate(${st.saturacion}%) hue-rotate(${st.tono}deg)${st.desenfoque ? ` blur(${st.desenfoque * (W / 400)}px)` : ""}`;
  ctx.translate(W / 2 + st.ox * W, H / 2 + st.oy * H);
  ctx.rotate((st.rot * Math.PI) / 180);
  ctx.scale(st.voltear ? -1 : 1, 1);
  ctx.drawImage(img, (-img.width * esc) / 2, (-img.height * esc) / 2, img.width * esc, img.height * esc);
  ctx.restore();
  if (!CON_FILTRO && (st.brillo !== 100 || st.contraste !== 100 || st.saturacion !== 100 || st.tono !== 0)) filtrarPixeles(ctx, W, H, st);
  if (st.vineta > 0) {
    ctx.save();
    ctx.globalCompositeOperation = "source-atop";
    const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.25, W / 2, H / 2, Math.hypot(W, H) / 2);
    g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, `rgba(0,0,0,${(st.vineta / 100) * 0.85})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.restore();
  }
  if (st.forma !== "cuadro" && st.contorno) {   // contorno brillante (como los cosméticos legendarios)
    ctx.save();
    camino(ctx, W, H, st, margen);
    ctx.lineWidth = st.grosor * (W / 256);
    ctx.strokeStyle = st.contorno; ctx.shadowColor = st.contorno; ctx.shadowBlur = st.grosor * 2.2 * (W / 256);
    ctx.stroke(); ctx.shadowBlur = 0; ctx.lineWidth = Math.max(1, ctx.lineWidth / 3); ctx.strokeStyle = "rgba(255,255,255,.85)"; ctx.stroke();
    ctx.restore();
  }
}

let dlg = null;
/**
 * Abre el editor. src: URL de la imagen original (ya subida). Devuelve la URL de la imagen editada, o null si se cancela.
 * opciones: { titulo, salida: [ancho, alto], formato: "png" | "jpg", formas: true para dejar elegir círculo/redondeado, forma }
 */
export async function editarImagen(src, { titulo = "Editar imagen", salida = [512, 512], formato = "png", formas = false, forma = "cuadro" } = {}) {
  const img = await cargar(src);
  const st = { ...ESTADO, forma };
  const [W, H] = salida;
  const animada = /\.(?:gif|webp)$/i.test(src);
  const escala = Math.min(1, 560 / Math.max(W, H));
  dlg?.remove();
  dlg = document.createElement("dialog");
  dlg.className = "a-hoja ancha ei";
  const desliza = ([k, t, min, max, paso]) => `<label class="ei-desliza"><span>${t} <b data-v="${k}"></b></span><input type="range" data-k="${k}" min="${min}" max="${max}" step="${paso}"></label>`;
  dlg.innerHTML = `<div class="a-hoja-caja"><div class="a-hoja-cab"><h2></h2><button type="button" class="a-icono" data-x aria-label="Cerrar">✕</button></div>
    <div class="a-hoja-cuerpo"><div class="ei-cuerpo">
      <div class="ei-lienzo-caja"><canvas class="ei-lienzo" width="${Math.round(W * escala)}" height="${Math.round(H * escala)}"></canvas>
        <small class="a-sub">Arrastra para mover · ${W}×${H} px</small>
        <div class="ei-botones"><button type="button" class="a-btn sm" data-a="rot">↻ Girar</button><button type="button" class="a-btn sm" data-a="voltear">⇋ Voltear</button><button type="button" class="a-btn sm ghost" data-a="centrar">⌖ Centrar</button><button type="button" class="a-btn sm ghost" data-a="reiniciar">Reiniciar</button></div></div>
      <div class="ei-controles">
        <div class="ei-filtros">${Object.entries(FILTROS).map(([k, [t]]) => `<button type="button" data-f="${k}"><canvas width="64" height="64"></canvas><span>${t}</span></button>`).join("")}</div>
        ${DESLIZAS.map(desliza).join("")}
        ${formas ? `<div class="ei-fila"><span>Forma</span><div class="a-seg" data-seg="forma">${[["cuadro", "◻ Cuadro"], ["redondo", "▢ Redondeada"], ["circulo", "◯ Círculo"]].map(([v, t]) => `<button type="button" data-v="${v}">${t}</button>`).join("")}</div></div>
          <label class="ei-desliza" data-solo="redondo"><span>Esquinas <b data-v="radio"></b></span><input type="range" data-k="radio" min="4" max="50" step="1"></label>
          <div class="ei-fila" data-solo="forma"><span>Contorno brillante</span><label class="ei-color"><input type="checkbox" data-a="contorno"> <input type="color" data-k="contorno" value="#facc15"></label></div>
          <label class="ei-desliza" data-solo="contorno"><span>Grosor <b data-v="grosor"></b></span><input type="range" data-k="grosor" min="2" max="16" step="1"></label>` : ""}
      </div></div><p class="a-err" data-err></p></div>
    <div class="a-hoja-pie">${animada ? '<small class="a-sub" style="flex:1;min-width:200px">Es un GIF o WEBP: si lo editas queda quieto. Para que siga animado usa «Usar tal cual».</small>' : ""}<button type="button" class="a-btn ghost" data-x>Cancelar</button>
      <button type="button" class="a-btn ${animada ? "" : "pri"}" data-a="listo">${animada ? "Usar editada (sin animación)" : "Usar imagen"}</button>${animada ? '<button type="button" class="a-btn pri" data-a="tal">▶ Usar tal cual (animada)</button>' : ""}</div></div>`;
  dlg.querySelector("h2").textContent = titulo;
  document.body.append(dlg);
  const lienzo = dlg.querySelector(".ei-lienzo");
  // Miniaturas de los filtros
  dlg.querySelectorAll("[data-f]").forEach((b) => { dibujar(b.querySelector("canvas"), img, { ...ESTADO, ...FILTROS[b.dataset.f][1] }); });
  let cuadro = 0;
  const pintar = () => {
    cancelAnimationFrame(cuadro);
    cuadro = requestAnimationFrame(() => dibujar(lienzo, img, st));
    dlg.querySelectorAll("[data-k]").forEach((el) => {
      const v = st[el.dataset.k];
      if (el.type === "range") el.value = el.dataset.k === "zoom" ? Math.round(v * 100) : v;
      else if (el.type === "color" && v) el.value = v;
    });
    dlg.querySelectorAll("[data-v]").forEach((el) => { const k = el.dataset.v; el.textContent = k === "zoom" ? `${Math.round(st.zoom * 100)}%` : k === "tono" ? `${st.tono}°` : k === "desenfoque" || k === "grosor" ? st[k] : `${st[k]}%`; });
    dlg.querySelectorAll("[data-seg=forma] [data-v]").forEach((b) => b.classList.toggle("on", b.dataset.v === st.forma));
    dlg.querySelectorAll("[data-solo]").forEach((el) => { const s = el.dataset.solo; el.hidden = s === "redondo" ? st.forma !== "redondo" : s === "forma" ? st.forma === "cuadro" : !(st.forma !== "cuadro" && st.contorno); });
    const chk = dlg.querySelector("[data-a=contorno]"); if (chk) chk.checked = Boolean(st.contorno);
  };
  pintar();
  dlg.addEventListener("input", (e) => {
    const k = e.target.dataset.k;
    if (!k) { if (e.target.dataset.a === "contorno") { st.contorno = e.target.checked ? dlg.querySelector("input[type=color][data-k=contorno]").value : ""; pintar(); } return; }
    if (e.target.type === "color") { st.contorno = e.target.value; dlg.querySelector("[data-a=contorno]").checked = true; }
    else st[k] = k === "zoom" ? Number(e.target.value) / 100 : Number(e.target.value);
    pintar();
  });
  // Arrastrar para mover (mouse y dedo); la rueda hace zoom
  let previo = null;
  lienzo.addEventListener("pointerdown", (e) => { previo = { x: e.clientX, y: e.clientY }; lienzo.setPointerCapture(e.pointerId); });
  lienzo.addEventListener("pointermove", (e) => {
    if (!previo) return;
    const r = lienzo.getBoundingClientRect();
    st.ox += (e.clientX - previo.x) / r.width; st.oy += (e.clientY - previo.y) / r.height;
    previo = { x: e.clientX, y: e.clientY }; pintar();
  });
  lienzo.addEventListener("pointerup", () => { previo = null; });
  lienzo.addEventListener("pointercancel", () => { previo = null; });
  lienzo.addEventListener("wheel", (e) => { e.preventDefault(); st.zoom = Math.max(1, Math.min(4, st.zoom * (e.deltaY < 0 ? 1.08 : 0.93))); pintar(); }, { passive: false });
  return new Promise((listo) => {
    let resultado = null;
    dlg.addEventListener("close", () => { dlg.remove(); dlg = null; listo(resultado); }, { once: true });
    dlg.addEventListener("click", async (e) => {
      if (e.target === dlg || e.target.closest("[data-x]")) { dlg.close(); return; }
      const f = e.target.closest("[data-f]");
      if (f) { Object.assign(st, FILTROS[f.dataset.f][1]); pintar(); return; }
      const s = e.target.closest("[data-seg=forma] [data-v]");
      if (s) { st.forma = s.dataset.v; pintar(); return; }
      const a = e.target.closest("[data-a]")?.dataset.a;
      if (a === "rot") st.rot = (st.rot + 90) % 360;
      else if (a === "voltear") st.voltear = !st.voltear;
      else if (a === "centrar") { st.ox = 0; st.oy = 0; st.zoom = 1; }
      else if (a === "reiniciar") Object.assign(st, { ...ESTADO, forma: st.forma });
      else if (a === "tal") { resultado = src; dlg.close(); return; }
      else if (a === "listo") {
        const btn = e.target.closest("button"); btn.disabled = true; btn.textContent = "Subiendo…";
        try {
          const final = document.createElement("canvas"); final.width = W; final.height = H;
          dibujar(final, img, st, formato === "jpg" ? "#000000" : "");
          const blob = await new Promise((ok) => final.toBlob(ok, formato === "jpg" ? "image/jpeg" : "image/png", 0.9));
          resultado = await subirImagen(blob);
          dlg.close();
        } catch (x) { dlg.querySelector("[data-err]").textContent = x.message; btn.disabled = false; btn.textContent = animada ? "Usar editada (sin animación)" : "Usar imagen"; }
        return;
      } else return;
      pintar();
    });
    dlg.showModal();
  });
}

/** Elige un archivo, sube la original y abre el editor. Devuelve { imagen, fuente } o null. */
export async function elegirYEditar(archivo, opciones) {
  if (!archivo) return null;
  if (archivo.size > 4 * 1024 * 1024) throw new Error("La imagen pesa más de 4 MB.");
  const fuente = await subirImagen(archivo);
  const imagen = await editarImagen(fuente, opciones);
  return imagen ? { imagen, fuente } : null;
}
