// Diálogos y avisos del IDE (sin dependencias).
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/**
 * Cuadro modal accesible (<dialog>). botones: [{ texto, valor, peligro?, cancelar? }].
 * Resuelve con el valor del botón pulsado; Esc devuelve el del botón marcado como cancelar.
 */
export function dialogo({ titulo, mensaje = "", botones }) {
  return new Promise((resolver) => {
    const d = document.createElement("dialog");
    d.className = "ide-dialogo";
    d.innerHTML = `<form method="dialog"><h3>${esc(titulo)}</h3>${mensaje ? `<p>${esc(mensaje).replace(/\n/g, "<br>")}</p>` : ""}<div class="ide-dialogo-botones"></div></form>`;
    const caja = d.querySelector(".ide-dialogo-botones");
    const cancelar = botones.find((b) => b.cancelar);
    let valor = cancelar ? cancelar.valor : undefined;
    botones.forEach((b, i) => {
      const el = document.createElement("button");
      el.type = "button";
      el.textContent = b.texto;
      el.className = `ide-boton${b.peligro ? " peligro" : ""}${i === 0 && !b.peligro ? " primario" : ""}`;
      el.addEventListener("click", () => { valor = b.valor; d.close(); });
      caja.appendChild(el);
    });
    d.addEventListener("close", () => { d.remove(); resolver(valor); });
    document.body.appendChild(d);
    d.showModal();
    // Lo destructivo no recibe el foco por defecto: Enter no borra por accidente.
    (caja.querySelector(".ide-boton:not(.peligro)") || caja.firstElementChild).focus();
  });
}

let contenedorAvisos;
/** Aviso temporal abajo a la derecha, con una acción opcional (p. ej. «Deshacer»). */
export function aviso(texto, { accion, ms = 6000, tipo = "info" } = {}) {
  if (!contenedorAvisos) {
    contenedorAvisos = document.createElement("div");
    contenedorAvisos.className = "ide-avisos";
    contenedorAvisos.setAttribute("role", "status");
    contenedorAvisos.setAttribute("aria-live", "polite");
    document.body.appendChild(contenedorAvisos);
  }
  const el = document.createElement("div");
  el.className = `ide-aviso ${tipo}`;
  el.innerHTML = `<span>${esc(texto)}</span>`;
  const quitar = () => el.remove();
  if (accion) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = accion.texto;
    b.addEventListener("click", () => { accion.fn(); quitar(); });
    el.appendChild(b);
  }
  const x = document.createElement("button");
  x.type = "button";
  x.className = "ide-aviso-x";
  x.setAttribute("aria-label", "Cerrar aviso");
  x.textContent = "×";
  x.addEventListener("click", quitar);
  el.appendChild(x);
  contenedorAvisos.appendChild(el);
  while (contenedorAvisos.childElementCount > 4) contenedorAvisos.firstElementChild.remove();
  setTimeout(quitar, ms);
  return quitar;
}

/** Menú contextual. items: [{ texto, atajo?, fn, peligro? } | "-"] */
export function menuContextual(x, y, items) {
  document.querySelectorAll(".ide-menu").forEach((m) => m.remove());
  const m = document.createElement("div");
  m.className = "ide-menu";
  m.setAttribute("role", "menu");
  items.forEach((it) => {
    if (it === "-") { m.insertAdjacentHTML("beforeend", '<div class="sep" role="separator"></div>'); return; }
    const b = document.createElement("button");
    b.type = "button";
    b.setAttribute("role", "menuitem");
    b.className = it.peligro ? "peligro" : "";
    b.innerHTML = `<span>${esc(it.texto)}</span>${it.atajo ? `<kbd>${esc(it.atajo)}</kbd>` : ""}`;
    b.addEventListener("click", () => { cerrar(); it.fn(); });
    m.appendChild(b);
  });
  document.body.appendChild(m);
  const { width, height } = m.getBoundingClientRect();
  m.style.left = `${Math.max(4, Math.min(x, innerWidth - width - 4))}px`;
  m.style.top = `${Math.max(4, Math.min(y, innerHeight - height - 4))}px`;
  const cerrar = () => { m.remove(); document.removeEventListener("pointerdown", fuera, true); document.removeEventListener("keydown", tecla, true); removeEventListener("blur", cerrar); };
  const fuera = (e) => { if (!m.contains(e.target)) cerrar(); };
  const tecla = (e) => {
    const botones = [...m.querySelectorAll("button")];
    const i = botones.indexOf(document.activeElement);
    if (e.key === "Escape") { e.preventDefault(); cerrar(); }
    else if (e.key === "ArrowDown") { e.preventDefault(); botones[(i + 1) % botones.length].focus(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); botones[(i - 1 + botones.length) % botones.length].focus(); }
  };
  document.addEventListener("pointerdown", fuera, true);
  document.addEventListener("keydown", tecla, true);
  addEventListener("blur", cerrar);
  m.querySelector("button")?.focus();
  return cerrar;
}
