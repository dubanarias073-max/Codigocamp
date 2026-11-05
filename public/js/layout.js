// Cabecera común de las páginas internas: pide sesión (o invitado) y dibuja el menú.
import { exigirAcceso } from "./auth.js";

const NAV = [
  ["inicio", "🏠 Inicio", "inicio.html"],
  ["lenguajes", "💻 Lenguajes", "lenguajes.html"],
  ["htmlcss", "🌐 HTML y CSS", "html-css.html"],
  ["bd", "🗄️ Bases de datos", "bases-de-datos.html"],
  ["retos", "🏆 Retos", "retos.html"],
  ["chat", "🤖 Chat IA", "aprende.html"],
];

export async function iniciarPagina() {
  const { ok, user } = await exigirAcceso();
  if (!ok) return { ok: false, user: null };
  const activa = document.body.dataset.pagina;
  const nav = document.getElementById("nav");
  for (const [id, texto, href] of NAV) {
    const a = document.createElement("a");
    a.href = href;
    a.textContent = texto;
    if (id === activa) { a.className = "on"; a.setAttribute("aria-current", "page"); }
    nav.appendChild(a);
  }
  return { ok: true, user };
}

export const mostrar = () => document.body.classList.remove("cargando");
