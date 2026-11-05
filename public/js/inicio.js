import { CONCEPTOS, LENGUAJES } from "./content/lenguajes.js";
import { HTML } from "./content/html.js";
import { CSS } from "./content/css.js";
import { BD } from "./content/bd.js";
import { RUTAS } from "./content/retos.js";
import { cargarProgreso, rachaActual, nivelUsuario } from "./progreso.js";
import { iniciarPagina, mostrar } from "./layout.js";

const $ = (id) => document.getElementById(id);
const { ok, user } = await iniciarPagina();

if (ok) {
  $("saludo").textContent = user ? `Hola, ${user.nombre} 👋` : "Hola, invitado 👋";
  $("bannerInvitado").hidden = !!user;

  // Cifras de las tarjetas
  const cuentas = {
    lenguajes: `${LENGUAJES.length} lenguajes · ${CONCEPTOS.length} lecciones cada uno`,
    htmlcss: `${HTML.length + CSS.length} lecciones desde cero`,
    bd: `${BD.length} lecciones de todo tipo`,
  };
  document.querySelectorAll("[data-cuenta]").forEach((e) => { e.textContent = cuentas[e.dataset.cuenta]; });

  // Progreso de retos
  const prog = cargarProgreso(user?.id ?? null);
  const niveles = RUTAS.flatMap((r) => r.niveles.map((n) => ({ ruta: r, nivel: n })));
  const hechos = niveles.filter((x) => prog.niveles[x.nivel.id]).length;
  $("stRacha").textContent = rachaActual(prog);
  $("stXp").textContent = prog.xp;
  $("stNivel").textContent = nivelUsuario(prog.xp);
  $("stRetos").textContent = `${hechos}/${niveles.length}`;
  $("barraNivel").style.width = prog.xp % 100 + "%";

  // Siguiente reto sugerido: primer nivel sin completar
  const siguiente = niveles.find((x) => !prog.niveles[x.nivel.id]);
  $("continuarTxt").textContent = siguiente
    ? `${siguiente.ruta.emoji} ${siguiente.ruta.nombre} · ${siguiente.nivel.titulo}`
    : "¡Has completado todos los niveles! Repítelos para mejorar tus estrellas.";

  mostrar();
}
