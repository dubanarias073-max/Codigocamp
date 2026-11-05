import { CONCEPTOS, LENGUAJES } from "./content/lenguajes.js";
import { HTML } from "./content/html.js";
import { CSS } from "./content/css.js";
import { BD } from "./content/bd.js";
import { RUTAS } from "./content/retos.js";
import { getUser, setGuest, pintarBarra } from "./auth.js";

const $ = (id) => document.getElementById(id);

// Cifras de la portada (se calculan solas al añadir contenido)
const stats = {
  lecciones: CONCEPTOS.length * LENGUAJES.length + HTML.length + CSS.length + BD.length,
  lenguajes: LENGUAJES.length,
  retos: RUTAS.reduce((n, r) => n + r.niveles.reduce((m, v) => m + v.preguntas.length, 0), 0),
};
document.querySelectorAll("[data-stat]").forEach((e) => { e.textContent = stats[e.dataset.stat]; });

// Entrar como invitado (el registro y el inicio de sesión viven en registro.html y login.html)
const entrarInvitado = () => { setGuest(true); location.href = "inicio.html"; };
$("guestBtn").onclick = entrarInvitado;
$("heroGuest").onclick = entrarInvitado;

// Estado de sesión
const user = await getUser();
pintarBarra(user, { enIndex: true });
if (user) {
  $("accesoForm").hidden = true;
  $("accesoYa").hidden = false;
  $("yaNombre").textContent = user.nombre;
  const pri = $("heroPri");
  pri.textContent = "Ir a mi panel";
  pri.href = "inicio.html";
  $("heroGuest").hidden = true;
}
