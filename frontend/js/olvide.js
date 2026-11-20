// «¿Olvidaste tu contraseña?» en login.html: pide el enlace por correo sin salir de la página.
import { api } from "./auth.js";

const $ = (id) => document.getElementById(id);
const login = document.querySelector(".authbox:not(#cajaOlvide)");
const caja = $("cajaOlvide");
const msg = $("olvideMsg");

function ver(olvide) {
  login.hidden = olvide;
  caja.hidden = !olvide;
  if (olvide) {
    const correo = $("email").value.trim();
    if (correo && !$("emailOlvide").value) $("emailOlvide").value = correo;
    $("emailOlvide").focus();
  } else $("email").focus();
}

$("olvideLink").onclick = (e) => { e.preventDefault(); history.replaceState(null, "", "#olvide"); ver(true); };
$("volverLogin").onclick = (e) => { e.preventDefault(); history.replaceState(null, "", location.pathname); ver(false); };
if (location.hash === "#olvide") ver(true);

$("formOlvide").onsubmit = async (e) => {
  e.preventDefault();
  const email = $("emailOlvide").value.trim().toLowerCase();
  msg.classList.remove("ok-msg");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { msg.textContent = "Escribe un correo válido."; $("emailOlvide").focus(); return; }
  const boton = $("btnOlvide");
  boton.disabled = true; boton.textContent = "Enviando…";
  try {
    const r = await api("/api/auth/olvide/", { email });
    msg.classList.add("ok-msg");
    msg.textContent = r.mensaje;
    boton.textContent = "Enviar otra vez";
    setTimeout(() => { boton.disabled = false; }, 20000);   // evita mandar diez correos seguidos
  } catch (x) {
    msg.textContent = x.message;
    boton.textContent = "Enviarme el enlace";
    boton.disabled = false;
  }
};
