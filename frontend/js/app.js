// Estructura común de las páginas con sesión: barra lateral, panel de estadísticas y barra inferior (móvil).
import { protegerCuenta } from "./privacidad.js";
import { avatarSVG } from "/js/avatares.js";
import { api, getUser } from "/js/auth.js";
import { iconoSVG } from "/js/iconos.js";
import { aplicarCosmeticos, conMarco, cosmeticosGuardados } from "/js/cosmeticos.js";
import "/js/pwa.js";
export { api };
export { aplicarCosmeticos, conMarco };

// Se pinta al instante lo último que la persona tenía puesto (fondo, puntero…); al llegar sus datos se actualiza.
try { aplicarCosmeticos(cosmeticosGuardados()); } catch { /* sin almacenamiento */ }

// Guarda el curso elegido en el perfil: Inicio y Aprende usan siempre el mismo.
export const elegirCurso = (slug) => api("/api/ajustes/", { curso: slug });

export const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const NAV = [["inicio", "inicio", "Inicio"], ["recompensas", "recompensas", "Recompensas"], ["chats", "chats", "Chats"], ["aprende", "aprende", "Aprende"], ["trabajo", "trabajo", "Trabajo"], ["ia", "ia", "IA"]];
const MAS = [["tienda", "tienda", "Tienda"], ["perfil", "perfil", "Perfil"], ["configuracion", "configuracion", "Configuración"]];
const url = (p) => `/pages/${p}.html`;
const parar = () => new Promise(() => {}); // detiene la página mientras el navegador cambia de dirección
const $ = (id) => document.getElementById(id);

// Temas: "auto" (predeterminado, sigue al dispositivo), "claro" y "oscuro".
export function aplicarTema(tema) {
  const t = tema === "claro" || tema === "oscuro" ? tema : "auto";
  document.documentElement.dataset.tema = t;
  try { localStorage.setItem("cc_tema", t); } catch {}
}

/** Foto de perfil (o avatar/inicial) con el marco que la persona tenga puesto. */
export function fotoDe(u, { tam = 40, marco = u?.cosmeticos?.marco } = {}) {
  const inicial = esc((u?.nombre || "?").charAt(0).toUpperCase());
  const dentro = u?.foto
    ? `<img class="foto-perfil" src="${esc(u.foto)}" alt="" width="${tam}" height="${tam}" style="width:${tam}px;height:${tam}px;object-fit:cover;border-radius:50%;display:block">`
    : avatarSVG(u?.avatar, tam) ? `<span class="foto-perfil foto-avatar" style="width:${tam}px;height:${tam}px">${avatarSVG(u.avatar, tam)}</span>`
    : `<span class="foto-perfil foto-inicial" style="width:${tam}px;height:${tam}px;font-size:${Math.round(tam * .45)}px">${inicial}</span>`;
  return conMarco(dentro, marco);
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
  return `<span class="chip mineral-diamante" title="Diamantes: se ganan en Recompensas y se gastan en la tienda">${iconoSVG("diamante", "stat-icon")} <b data-s="diamante">${p.diamante}</b></span>
    <span class="chip" title="Experiencia total, no se gasta">${iconoSVG("moneda_xp", "stat-icon")} <b data-s="xp_total">${p.xp_total}</b></span>
    <span class="chip" title="Racha de días">${iconoSVG("racha", "stat-icon")} <b data-s="racha_actual">${p.racha_actual}</b></span>
    <a class="chip chip-salva" href="/pages/tienda.html#potenciador" title="Salvarrachas: si un día no practicas, se gasta uno solo y tu racha no se pierde. Tienes ${p.salvarrachas} de 2. Se consiguen en la tienda y en los cofres.">${iconoSVG("salvarrachas", "stat-icon")} <b data-s="salvarrachas">${p.salvarrachas}</b><small>/2</small></a>
    <span class="chip" title="Vidas">${iconoSVG("vidas", "stat-icon")} <b data-s="vidas">${p.vidas}</b></span>`;
};

// Actualiza los números de las estadísticas sin recargar (después de comprar o completar un reto).
export function actualizarStats(pr) {
  document.querySelectorAll("[data-s]").forEach((el) => { if (pr.perfil[el.dataset.s] !== undefined) el.textContent = pr.perfil[el.dataset.s]; });
}

export async function iniciar(activa) {
  const user = await getUser();
  if (!user) { location.replace(url("login")); await parar(); }
  await protegerCuenta(user);   // si antes estuvo otra cuenta en este navegador, se borran sus copias locales
  if (!user.onboarding) { location.replace(url("onboarding")); await parar(); }
  aplicarTema(user.tema);
  aplicarCosmeticos(user.cosmeticos || {});
  const [prog, mis] = await Promise.all([api("/api/progreso/"), api("/api/desafios/").catch(() => ({ hoy: [] }))]);
  const p = prog.perfil;

  const item = ([k, ic, t]) => `<a class="nav-i${k === activa ? " on" : ""}" href="${url(k)}"><span class="ic">${iconoSVG(ic, "nav-icon")}</span><span class="t">${t}</span></a>`;
  $("lado").innerHTML = `<a class="logo-app" href="${url("inicio")}"><img src="/img/logo-icon.png" alt="" width="34" height="34" onerror="this.remove()"><span>codigocamp</span></a>`
    + NAV.map(item).join("") + '<p class="grupo">Más</p>' + MAS.map(item).join("")
    + `<a class="yo-chip" href="${url("perfil")}" title="Tu perfil">${fotoDe(user, { tam: 34 })}<span><b>${esc(user.nombre.split(" ")[0])}</b><small>@${esc(user.alias || "")}</small></span></a>`;

  const m = mis.hoy.find((x) => !x.completado);
  const der = $("der");
  if (der) der.innerHTML = `<div class="tarjeta stats-der">${chips(prog)}</div>
    <div class="tarjeta"><h3>Nivel ${p.nivel}</h3><div class="barra"><i style="width:${p.xp_nivel}%"></i></div><small>${p.xp_nivel}/100 XP para el siguiente nivel</small></div>
    <div class="tarjeta"><h3>Tu curso</h3><p>${prog.curso_actual ? esc(prog.curso_actual.nombre) : "Elige un curso en Configuración"}</p>
      <a class="bj" href="${url("inicio")}">Practicar</a></div>
    ${m ? `<div class="tarjeta"><h3>${iconoSVG(m.clave, "mini-mission-icon")} ${esc(m.titulo)}</h3><div class="barra"><i style="width:${m.progreso / m.meta * 100}%"></i></div>
      <small>${m.progreso}/${m.meta} · Premio: ${esc(m.premio)}</small><p><a href="${url("recompensas")}">Ver desafíos</a></p></div>` : ""}`;

  // Widget de racha de la semana (como el de Duolingo), en la columna derecha de todas las páginas.
  if (der) api("/api/widget/").then((w) => {
    der.insertAdjacentHTML("afterbegin", `<a class="tarjeta widget-racha${w.practicado_hoy ? " hecho" : w.racha ? " peligro" : ""}" href="${url("perfil")}#calendario" title="Calendario de racha">
      <div class="wr-cab"><span class="wr-fuego" aria-hidden="true">${iconoSVG("racha", "wr-svg")}</span><div><b>${w.racha}</b><small>día${w.racha === 1 ? "" : "s"} de racha</small></div><span class="wr-hielo" title="Salvarrachas: protegen tu racha si un día no practicas">${iconoSVG("salvarrachas", "wr-mini")} ${w.salvarrachas ?? 0}/2</span></div>
      <div class="wr-semana">${w.semana.map((d) => `<span class="${d.icono === "🔥" ? "si" : ""}${d.hoy ? " hoy" : ""}"><small>${d.letra}</small><i>${d.icono === "🔥" ? iconoSVG("racha", "wr-dia") : ""}</i></span>`).join("")}</div>
      <small class="wr-estado">${esc(w.estado)}</small></a>`);
  }).catch(() => {});

  $("inf").innerHTML = NAV.map(([k, ic, t]) => `<a class="inf-i${k === activa ? " on" : ""}" href="${url(k)}" aria-label="${t}">${iconoSVG(ic, "nav-icon")}</a>`).join("")
    + `<button class="inf-i" id="masBtn" type="button" aria-label="Más">${iconoSVG("configuracion", "nav-icon")}</button>
       <div class="mas" id="masMenu" hidden>${MAS.map(item).join("")}</div>`;
  $("masBtn").onclick = () => { $("masMenu").hidden = !$("masMenu").hidden; };

  $("contenido").insertAdjacentHTML("afterbegin", `<div class="tope">${chips(prog)}</div>`);
  document.body.classList.remove("cargando");
  return { user, prog };
}
