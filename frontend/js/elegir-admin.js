// Solo para la cuenta del administrador: después de entrar elige si va al panel de administrador o a su cuenta normal.
// El resto de personas nunca ve esto (el servidor solo marca «admin» en la cuenta de ADMIN_EMAIL).
import { api } from "./auth.js";

const destinoUsuario = (u) => (u.onboarding ? "/pages/inicio.html" : "/pages/onboarding.html");

export function mostrarEleccion(user) {
  document.body.classList.remove("cargando");
  document.querySelectorAll(".authbox").forEach((c) => { c.hidden = true; });
  document.getElementById("cajaAdmin")?.remove();
  const caja = document.createElement("div");
  caja.className = "card authbox";
  caja.id = "cajaAdmin";
  caja.innerHTML = `
    <h2>¿Cómo quieres entrar?</h2>
    <p class="note">Hola, <b></b>. Esta opción solo aparece en tu cuenta.</p>
    <div style="display:grid;gap:12px;margin:18px 0 6px">
      <button type="button" class="btn pri" id="comoUsuario">👤 Entrar como usuario</button>
      <button type="button" class="btn ghost" id="comoAdmin">🛡️ Entrar como administrador</button>
    </div>
    <form id="formAdmin" class="authform" novalidate style="display:none">
      <label for="claveAdmin">Clave de administrador
        <input type="password" id="claveAdmin" autocomplete="off" required placeholder="La clave ADMIN_CLAVE de tu .env">
      </label>
      <button class="btn pri" type="submit">Abrir el panel</button>
    </form>
    <p class="err" id="errAdmin" role="alert" aria-live="assertive"></p>`;
  caja.querySelector(".note b").textContent = (user.nombre || "").split(" ")[0] || user.email;
  const cont = document.querySelector(".acceso-in") || document.querySelector("main") || document.body;
  cont.append(caja);
  const err = caja.querySelector("#errAdmin");
  const form = caja.querySelector("#formAdmin");
  caja.querySelector("#comoUsuario").addEventListener("click", () => { location.href = destinoUsuario(user); });
  caja.querySelector("#comoAdmin").addEventListener("click", async () => {
    err.textContent = "";
    try {
      const e = await api("/api/admin/estado");
      if (e.activo) { location.href = "/pages/admin.html"; return; }
      if (!e.configurado) { err.textContent = "Falta poner ADMIN_CLAVE en backend/.env y reiniciar Flask."; return; }
    } catch (e2) { err.textContent = e2.message; return; }
    form.style.display = "";
    form.querySelector("input").focus();
  });
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    err.textContent = "";
    const boton = form.querySelector("[type=submit]");
    boton.disabled = true;
    try {
      await api("/api/admin/entrar", { clave: form.querySelector("input").value });
      location.href = "/pages/admin.html";
    } catch (e2) {
      err.textContent = e2.message;
      boton.disabled = false;
    }
  });
}
