// restablecer.html: llega desde el enlace del correo (?t=...). Comprueba el enlace y guarda la nueva contraseña.
import { api } from "./auth.js";

const $ = (id) => document.getElementById(id);
const token = new URLSearchParams(location.search).get("t") || "";
history.replaceState(null, "", location.pathname);   // el enlace no queda en el historial ni se comparte por error
const err = $("autherr");
document.body.classList.remove("cargando");

const fallo = (m) => { err.textContent = m; $("pedirOtro").hidden = false; $("formAcceso").hidden = true; $("paraQuien").textContent = "No se puede usar este enlace."; };

document.querySelectorAll(".pw-ver").forEach((b) => {
  const campo = b.parentElement.querySelector("input");
  b.onclick = () => {
    const ver = campo.type === "password";
    campo.type = $("password2").type = ver ? "text" : "password";
    b.setAttribute("aria-pressed", String(ver));
    b.querySelector(".ojo").toggleAttribute("hidden", ver);
    b.querySelector(".ojo-x").toggleAttribute("hidden", !ver);
  };
});

if (!token) fallo("Abre el enlace completo que te llegó al correo.");
else {
  try {
    const r = await api("/api/auth/restablecer/validar/", { token });
    $("paraQuien").innerHTML = `Para la cuenta <b></b>. El enlace vence ${r.minutos} minutos después de pedirlo.`;
    $("paraQuien").querySelector("b").textContent = r.email;
    $("formAcceso").hidden = false;
    $("password").focus();
  } catch (x) { fallo(x.message); }
}

$("formAcceso").onsubmit = async (e) => {
  e.preventDefault();
  const p = $("password").value, p2 = $("password2").value;
  err.textContent = "";
  if (p.length < 6 || !/[A-Z]/.test(p) || !/\d/.test(p)) { err.textContent = "Mínimo 6 caracteres, una mayúscula y un número."; $("password").focus(); return; }
  if (p !== p2) { err.textContent = "Las dos contraseñas no coinciden."; $("password2").focus(); return; }
  const b = $("btnGuardar"); b.disabled = true; b.textContent = "Guardando…";
  try {
    await api("/api/auth/restablecer/", { token, password: p });
    $("formAcceso").hidden = true;
    $("paraQuien").innerHTML = "<b>¡Listo! Tu contraseña cambió.</b> Por seguridad cerramos tu sesión en todos los dispositivos. Ya puedes entrar con la nueva.";
    err.innerHTML = '<a class="btn pri" href="/pages/login.html">Iniciar sesión</a>';
    err.classList.add("ok-msg");
  } catch (x) { err.textContent = x.message; b.disabled = false; b.textContent = "Guardar contraseña"; }
};
