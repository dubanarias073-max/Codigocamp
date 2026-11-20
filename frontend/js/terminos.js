// Aviso de Términos y condiciones para cuentas que aún no aceptaron la versión vigente
// (cuentas creadas antes de que existieran o cuando el texto cambia). Bloquea la página hasta aceptar.
import { api } from "/js/auth.js";

export async function pedirTerminos() {
  if (!document.querySelector('link[href="/css/terminos.css"]')) {
    const l = document.createElement("link"); l.rel = "stylesheet"; l.href = "/css/terminos.css"; document.head.append(l);
  }
  let articulo = null;
  try {
    const html = await (await fetch("/pages/terminos.html", { credentials: "same-origin" })).text();
    articulo = new DOMParser().parseFromString(html, "text/html").getElementById("terminosTexto");
  } catch { /* sin conexión: queda el enlace */ }
  return new Promise((resolver) => {
    const capa = document.createElement("div");
    capa.className = "terminos-capa";
    capa.setAttribute("role", "dialog");
    capa.setAttribute("aria-modal", "true");
    capa.setAttribute("aria-labelledby", "terminosTit");
    capa.innerHTML = `<div>
      <h2 id="terminosTit">📜 Actualizamos los Términos y condiciones</h2>
      <p class="terminos-alerta"><span aria-hidden="true">⚠️</span><span><b>Tu progreso está a salvo</b> (XP, racha y diamantes quedan en la base de datos), pero <b>tus proyectos de Trabajo no</b>: se pueden perder con las actualizaciones de CódigoCamp. Descárgalos en .zip o súbelos a GitHub.</span></p>
      <div class="terminos-caja" tabindex="0"></div>
      <label><input type="checkbox" data-c><span>Entiendo que debo guardar copia de mis proyectos de Trabajo (pueden perderse con las actualizaciones).</span></label>
      <label><input type="checkbox" data-c><span>Entiendo que la IA puede equivocarse y no compartiré contraseñas ni datos sensibles.</span></label>
      <label><input type="checkbox" data-c><span>Leí y acepto los <a href="/pages/terminos.html" target="_blank" rel="noopener">Términos y condiciones</a>.</span></label>
      <button class="bj" type="button" disabled>Aceptar y continuar</button>
      <p class="terminos-error" role="alert" hidden></p>
    </div>`;
    const caja = capa.querySelector(".terminos-caja");
    if (articulo) { articulo.removeAttribute("id"); caja.append(document.importNode(articulo, true)); }
    else caja.innerHTML = '<p>Léelos en <a href="/pages/terminos.html" target="_blank" rel="noopener">esta página</a>.</p>';
    const boton = capa.querySelector("button");
    const casillas = [...capa.querySelectorAll("[data-c]")];
    casillas.forEach((c) => { c.onchange = () => { boton.disabled = !casillas.every((x) => x.checked); }; });
    boton.onclick = async () => {
      boton.disabled = true;
      try { await api("/api/terminos/aceptar/", { acepto: true }); capa.remove(); document.body.style.overflow = ""; resolver(true); }
      catch (e) { const p = capa.querySelector(".terminos-error"); p.textContent = e.message; p.hidden = false; boton.disabled = false; }
    };
    // La pantalla de carga (body.cargando) tapa todo: se quita para que el aviso se vea.
    document.body.classList.remove("cargando");
    document.body.append(capa);
    document.body.style.overflow = "hidden";
    caja.focus();
  });
}
