// Estructura común de las páginas con sesión: barra lateral, panel de estadísticas y barra inferior (móvil).
import { api, getUser } from "/js/auth.js";
export { api };

// Guarda el curso elegido en el perfil: Inicio y Aprende usan siempre el mismo.
export const elegirCurso = (slug) => api("/api/ajustes/", { curso: slug });

export const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const NAV = [["inicio", "🏠", "Inicio"], ["recompensas", "🎁", "Recompensas"], ["chats", "💬", "Chats"], ["aprende", "📚", "Aprende"], ["ia", "🤖", "IA"]];
const MAS = [["tienda", "🛒", "Tienda"], ["perfil", "👤", "Perfil"], ["configuracion", "⚙️", "Configuración"]];
const url = (p) => `/pages/${p}.html`;
const parar = () => new Promise(() => {}); // detiene la página mientras el navegador cambia de dirección
const $ = (id) => document.getElementById(id);

// Temas: "auto" (predeterminado, sigue al dispositivo), "claro" y "oscuro".
export function aplicarTema(tema) {
  const t = tema === "claro" || tema === "oscuro" ? tema : "auto";
  document.documentElement.dataset.tema = t;
  try { localStorage.setItem("cc_tema", t); } catch {}
}

export function aviso(texto, error = false) {
  const d = document.createElement("div");
  d.className = "aviso" + (error ? " error" : "");
  d.textContent = texto;
  document.body.appendChild(d);
  setTimeout(() => d.remove(), 3000);
}

const chips = (pr) => {
  const p = pr.perfil;
  return `<span class="chip mineral-diamante" title="Diamantes: se ganan en Recompensas y se gastan en la tienda">💎 <b data-s="diamante">${p.diamante}</b></span>
    <span class="chip" title="Experiencia total, no se gasta">✨ <b data-s="xp_total">${p.xp_total}</b></span>
    <span class="chip" title="Racha de días">🔥 <b data-s="racha_actual">${p.racha_actual}</b></span>
    <span class="chip" title="Vidas">❤️ <b data-s="vidas">${p.vidas}</b></span>`;
};

// Actualiza los números de las estadísticas sin recargar (después de comprar o completar un reto).
export function actualizarStats(pr) {
  document.querySelectorAll("[data-s]").forEach((el) => { if (pr.perfil[el.dataset.s] !== undefined) el.textContent = pr.perfil[el.dataset.s]; });
}

export async function iniciar(activa) {
  const user = await getUser();
  if (!user) { location.replace(url("login")); await parar(); }
  if (!user.onboarding) { location.replace(url("onboarding")); await parar(); }
  aplicarTema(user.tema);
  const [prog, mis] = await Promise.all([api("/api/progreso/"), api("/api/desafios/").catch(() => ({ hoy: [] }))]);
  const p = prog.perfil;

  const item = ([k, ic, t]) => `<a class="nav-i${k === activa ? " on" : ""}" href="${url(k)}"><span class="ic">${ic}</span><span class="t">${t}</span></a>`;
  $("lado").innerHTML = `<a class="logo-app" href="${url("inicio")}"><img src="/img/logo-icon.png" alt="" width="34" height="34" onerror="this.remove()"><span>codigocamp</span></a>`
    + NAV.map(item).join("") + '<p class="grupo">Más</p>' + MAS.map(item).join("");

  const m = mis.hoy.find((x) => !x.completado);
  $("der").innerHTML = `<div class="tarjeta stats-der">${chips(prog)}</div>
    <div class="tarjeta"><h3>Nivel ${p.nivel}</h3><div class="barra"><i style="width:${p.xp_nivel}%"></i></div><small>${p.xp_nivel}/100 XP para el siguiente nivel</small></div>
    <div class="tarjeta"><h3>Tu curso</h3><p>${prog.curso_actual ? esc(prog.curso_actual.nombre) : "Elige un curso en Configuración"}</p>
      <a class="bj" href="${url("inicio")}">Practicar</a></div>
    ${m ? `<div class="tarjeta"><h3>${m.icono} ${esc(m.titulo)}</h3><div class="barra"><i style="width:${m.progreso / m.meta * 100}%"></i></div>
      <small>${m.progreso}/${m.meta} · Premio: ${esc(m.premio)}</small><p><a href="${url("recompensas")}">Ver desafíos</a></p></div>` : ""}`;

  $("inf").innerHTML = NAV.map(([k, ic, t]) => `<a class="inf-i${k === activa ? " on" : ""}" href="${url(k)}" aria-label="${t}">${ic}</a>`).join("")
    + `<button class="inf-i" id="masBtn" type="button" aria-label="Más">⋯</button>
       <div class="mas" id="masMenu" hidden>${MAS.map(item).join("")}</div>`;
  $("masBtn").onclick = () => { $("masMenu").hidden = !$("masMenu").hidden; };

  $("contenido").insertAdjacentHTML("afterbegin", `<div class="tope">${chips(prog)}</div>`);
  document.body.classList.remove("cargando");
  return { user, prog };
}
