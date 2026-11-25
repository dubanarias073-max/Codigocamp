// Lógica de registro.html: usa el formulario compartido de login y registro (js/acceso-form.js)
// y Codi, que acompaña mientras creas la cuenta: saluda, dice tu nombre, se tapa los ojos con la contraseña…
import "/js/acceso-form.js";
import { codiSVG } from "/js/codi.js";
import { sonar } from "/js/sonidos.js";

const $ = (id) => document.getElementById(id);
const fig = $("regCodiFig"), globo = $("regGlobo"), form = $("formAcceso");
let animo = "", volver = 0, ultimaFrase = "", ocupadoHasta = 0;

function poner(a, frase, { sonido = null, ms = 0 } = {}) {
  if (a !== animo) { fig.innerHTML = codiSVG(a, { tam: 112, accesorio: null }); animo = a; }
  if (frase && frase !== ultimaFrase) {
    ultimaFrase = frase;
    globo.textContent = frase;
    globo.classList.remove("habla"); void globo.offsetWidth; globo.classList.add("habla");
  }
  if (sonido) sonar(sonido);
  clearTimeout(volver);
  if (ms) { ocupadoHasta = Date.now() + ms; volver = setTimeout(() => estadoSegunFoco(), ms); }
}

const nombreCorto = () => (form.elements.nombre.value.trim().split(/\s+/)[0] || "").slice(0, 20);
const reglasOk = () => { const p = form.elements.password.value; return p.length >= 6 && /[A-Z]/.test(p) && /\d/.test(p); };

function estadoSegunFoco() {
  const f = document.activeElement;
  if (f === form.elements.password || f === form.elements.password2) {
    const visible = f.type === "text";
    poner(visible ? "espia" : "tapa", visible ? "¡Ups! Solo una miradita 👀" : "No estoy mirando 🙈 Tu contraseña es solo tuya.");
  } else if (f === form.elements.email) poner("pensando", "Anoto tu correo… allí te llegan los avisos de tu racha.");
  else if (f === form.elements.nombre) poner(nombreCorto() ? "feliz" : "saludo", nombreCorto() ? `¡Mucho gusto, ${nombreCorto()}!` : "¿Cómo te llamas?");
  else poner(nombreCorto() ? "guino" : "saludo", nombreCorto() ? `¡Vamos, ${nombreCorto()}! Ya casi.` : "¡Hola! Soy Codi. ¿Creamos tu cuenta?");
}

poner("saludo", "¡Hola! Soy Codi. ¿Creamos tu cuenta?");
form.addEventListener("focusin", (e) => {
  if (e.target === form.elements.password || e.target === form.elements.password2) sonar("codi_tapa");
  estadoSegunFoco();
});
form.addEventListener("focusout", () => setTimeout(() => { if (Date.now() >= ocupadoHasta) estadoSegunFoco(); }, 0));
let saludado = false;
form.elements.nombre.addEventListener("input", () => {
  if (nombreCorto().length >= 2 && !saludado) { saludado = true; poner("ama", `¡Mucho gusto, ${nombreCorto()}! 💙`, { sonido: "codi_hola", ms: 1800 }); return; }
  if (!nombreCorto()) saludado = false;
  estadoSegunFoco();
});
let reglasAntes = false;
form.elements.password.addEventListener("input", () => {
  const ok = reglasOk();
  if (ok && !reglasAntes) poner("celebra", "¡Contraseña fuerte! 💪", { sonido: "codi_feliz", ms: 1600 });
  reglasAntes = ok;
});
form.elements.password2.addEventListener("input", () => {
  const p1 = form.elements.password.value, p2 = form.elements.password2.value;
  if (p2 && p1 === p2 && p2.length >= 6) poner("guino", "¡Coinciden! 😉", { sonido: "codi_guino", ms: 1500 });
});
// Los ojitos de mostrar la contraseña: Codi espía o se vuelve a tapar
document.querySelectorAll(".pw-ver").forEach((b) => b.addEventListener("click", () => setTimeout(estadoSegunFoco, 0)));
// Si el formulario muestra un error, Codi se preocupa; al enviar, celebra
new MutationObserver(() => { if ($("autherr").textContent.trim()) poner("preocupado", "Uy, revisemos eso juntos 👇", { sonido: "pareja_mal", ms: 3500 }); })
  .observe($("autherr"), { childList: true, characterData: true, subtree: true });
form.addEventListener("submit", () => { if (form.checkValidity()) poner("celebra", "¡Bienvenido a CódigoCamp! 🎉", { sonido: "arranque" }); });
// Tocar a Codi
const toques = [["asombro", "¡Wow! ¡Me tocaste!", "codi_wow"], ["baila", "¡A bailar mientras te registras! 🎶", "codi_baile"], ["guino", "Psst… es gratis 😉", "codi_guino"], ["ama", "¡Ya te quiero! 💙", "codi_amor"]];
let n = 0;
fig.addEventListener("click", () => { const [a, f, so] = toques[n++ % toques.length]; poner(a, f, { sonido: so, ms: 2600 }); });

// En el celular, al bajar por el formulario Codi se ve pequeño y flotando arriba (para que lo veas mientras escribes)
const caja = $("regCodi"), hueco = document.createElement("div");
hueco.className = "reg-codi-hueco";
caja.before(hueco);
new IntersectionObserver(([e]) => {
  const flotar = !e.isIntersecting && e.boundingClientRect.top < 0 && matchMedia("(max-width: 860px)").matches;
  if (flotar === caja.classList.contains("flotando")) return;
  hueco.style.height = flotar ? `${caja.offsetHeight}px` : "0";
  caja.classList.toggle("flotando", flotar);
  // un contenedor animado (transform) haría que «fixed» se mueva con él: mientras flota, Codi vive en <body>
  if (flotar) document.body.append(caja); else hueco.after(caja);
}, { rootMargin: "-70px 0px 0px 0px" }).observe(hueco);
