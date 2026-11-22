// Estructura común de las páginas con sesión: barra lateral, panel de estadísticas y barra inferior (móvil).
import { protegerCuenta } from "./privacidad.js";
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

/** Foto de perfil (o inicial) con el marco que la persona tenga puesto. */
export function fotoDe(u, { tam = 40, marco = u?.cosmeticos?.marco } = {}) {
  const inicial = esc((u?.nombre || "?").charAt(0).toUpperCase());
  const dentro = u?.foto
    ? `<img class="foto-perfil" src="${esc(u.foto)}" alt="" width="${tam}" height="${tam}" style="width:${tam}px;height:${tam}px;object-fit:cover;border-radius:50%;display:block">`
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
    <a class="chip chip-salva" href="/pages/tienda.html#potenciador" title="Salvarrachas: si un día no practicas, se gasta uno solo y tu racha no se pierde. Tienes ${p.salvarrachas}. En la tienda puedes tener hasta 2; cada 10 días de racha ganas uno más (aunque pases de 2).">${iconoSVG("salvarrachas", "stat-icon")} <b data-s="salvarrachas">${p.salvarrachas}</b></a>
    <span class="chip" title="Vidas">${iconoSVG("vidas", "stat-icon")} <b data-s="vidas">${p.vidas}</b></span>`;
};

// Actualiza los números de las estadísticas sin recargar (después de comprar o completar un reto).
export function actualizarStats(pr) {
  document.querySelectorAll("[data-s]").forEach((el) => { if (pr.perfil[el.dataset.s] !== undefined) el.textContent = pr.perfil[el.dataset.s]; });
}

export async function iniciar(activa) {
  const user = await getUser();
  if (!user) { try { window.CodigoCampApp?.desconectarWidget(); } catch { /* fuera de la app */ } location.replace(url("login")); await parar(); }
  await protegerCuenta(user);   // si antes estuvo otra cuenta en este navegador, se borran sus copias locales
  if (!user.onboarding) { location.replace(url("onboarding")); await parar(); }
  aplicarTema(user.tema);
  // Idioma de la interfaz: el de la cuenta manda (así se ve igual en todos tus dispositivos)
  let pendiente = false;
  try { pendiente = localStorage.getItem("cc_idioma_pendiente") === "1"; localStorage.removeItem("cc_idioma_pendiente"); } catch { /* nada */ }
  if (pendiente && user.idioma !== window.CC_IDIOMA) { user.idioma = window.CC_IDIOMA; api("/api/ajustes/", { idioma: window.CC_IDIOMA }).catch(() => {}); }
  if (user.idioma && user.idioma !== (window.CC_IDIOMA || "es")) {
    window.ccIdioma?.(user.idioma);
    if (!sessionStorage.getItem("cc_idioma_recarga")) { sessionStorage.setItem("cc_idioma_recarga", "1"); location.reload(); await parar(); }
  } else { try { sessionStorage.removeItem("cc_idioma_recarga"); } catch { /* nada */ } }
  // Cuentas antiguas o términos actualizados: hay que aceptarlos antes de seguir.
  if (user.terminos === false) await (await import("/js/terminos.js")).pedirTerminos();
  // Dentro de la app de Android: el widget queda conectado a esta sesión.
  if (window.CodigoCampApp) import("/js/appnativa.js").then((m) => m.sincronizarWidgetApp(api)).catch(() => {});
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
    <div class="tarjeta" data-tarjeta="curso"><h3>Tu curso</h3><p>${prog.curso_actual ? esc(prog.curso_actual.nombre) : "Elige un curso en Configuración"}</p>
      <a class="bj" href="${url("inicio")}">Practicar</a></div>
    ${m ? `<div class="tarjeta"><h3>${iconoSVG(m.clave, "mini-mission-icon")} ${esc(m.titulo)}</h3><div class="barra"><i style="width:${m.progreso / m.meta * 100}%"></i></div>
      <small>${m.progreso}/${m.meta} · Premio: ${esc(m.premio)}</small><p><a href="${url("recompensas")}">Ver desafíos</a></p></div>` : ""}`;

  // Widget de racha de la semana (como el de Duolingo), con Codi y el reloj del día, en la columna derecha de todas las páginas.
  api("/api/widget/").then(async (w) => {
    const { codiSVG, fraseDe } = await import("/js/codi.js");
    const fin = Date.now() + (w.segundos_restantes || 0) * 1000;
    // Codi, el compañero, en todas las páginas: en el menú (computador) y arriba (celular). Tocarlo abre el tutor de IA.
    const animo = w.animo || "saludo";
    document.querySelector(".yo-chip")?.insertAdjacentHTML("beforebegin", `<a class="codi-lado" href="${url("ia")}" title="Codi · pregúntale al tutor de IA">
      <span class="codi-lado-img">${codiSVG(animo, { tam: 64 })}</span><span class="codi-lado-globo">${esc(fraseDe(animo))}</span></a>`);
    const lado = document.getElementById("lado");
    const compacto = () => document.querySelector(".codi-lado")?.classList.toggle("compacto", (lado?.offsetWidth || 0) < 170);
    compacto(); addEventListener("resize", compacto);
    document.querySelector(".tope")?.insertAdjacentHTML("afterbegin", `<a class="codi-tope" href="${url("ia")}" title="Codi · pregúntale al tutor de IA" aria-label="Codi: pregúntale al tutor de IA">${codiSVG(animo, { tam: 36, animado: false })}</a>`);
    if (der) der.insertAdjacentHTML("afterbegin", `<a class="tarjeta widget-racha${w.practicado_hoy ? " hecho" : w.racha ? " peligro" : ""}" href="${url("perfil")}#calendario" title="Calendario de racha">
      <div class="wr-cab"><span class="wr-codi">${codiSVG(w.animo || "feliz", { tam: 58 })}</span><div><b>${w.racha}</b><small>día${w.racha === 1 ? "" : "s"} de racha</small></div><span class="wr-hielo" title="Salvarrachas: protegen tu racha si un día no practicas">${iconoSVG("salvarrachas", "wr-mini")} ${w.salvarrachas ?? 0}</span></div>
      <div class="wr-reloj" data-reloj><span>${w.practicado_hoy ? "✅ Racha a salvo · el día termina en" : "⏳ Te quedan hoy"}</span><b data-reloj-num>--:--:--</b></div>
      <div class="wr-semana">${w.semana.map((d, i) => `<span class="${d.icono === "🔥" ? "si" : ""}${d.hoy ? " hoy" : ""}"><small>${window.CC_IDIOMA === "en" ? "MTWTFSS"[i] : d.letra}</small><i>${d.icono === "🔥" ? iconoSVG("racha", "wr-dia") : ""}</i></span>`).join("")}</div>
      <small class="wr-estado">${esc(w.estado)}</small>
      <div class="wr-metas"><span title="Cada 10 días seguidos de racha ganas un salvarrachas (puedes tener más de 2)">🎁 ${w.dias_para_salvarrachas ?? 10} día${w.dias_para_salvarrachas === 1 ? "" : "s"} para +1 salvarrachas</span>
        <span title="Practica de lunes a domingo sin usar salvarrachas: cofre de oro. Todo el mes sin fallar: cofre legendario">⭐ Semana perfecta ${w.semana_dias ?? 0}/7</span></div></a>`);
    if (!w.practicado_hoy) document.querySelector(".tope")?.insertAdjacentHTML("beforeend", `<a class="chip chip-reloj" data-reloj href="${url("inicio")}" title="Horas que te quedan hoy para practicar">⏳ <b data-reloj-num>--:--</b></a>`);
    const tic = () => {
      const seg = Math.max(0, Math.round((fin - Date.now()) / 1000));
      const h = Math.floor(seg / 3600), m = Math.floor(seg % 3600 / 60), x = seg % 60;
      const dos = (n) => String(n).padStart(2, "0");
      const rojo = !w.practicado_hoy && seg <= 3 * 3600;
      for (const el of document.querySelectorAll("[data-reloj]")) {
        el.classList.toggle("rojo", rojo);
        const num = el.querySelector("[data-reloj-num]");
        if (num) num.textContent = el.classList.contains("chip") ? `${h}h ${dos(m)}m` : `${dos(h)}:${dos(m)}:${dos(x)}`;
      }
      document.querySelector(".widget-racha")?.classList.toggle("urgente", rojo);
      if (seg === 0) clearInterval(reloj);
    };
    const reloj = setInterval(tic, 1000);
    tic();
  }).catch(() => {});

  $("inf").innerHTML = NAV.map(([k, ic, t]) => `<a class="inf-i${k === activa ? " on" : ""}" href="${url(k)}" aria-label="${t}">${iconoSVG(ic, "nav-icon")}</a>`).join("")
    + `<button class="inf-i" id="masBtn" type="button" aria-label="Más">${iconoSVG("configuracion", "nav-icon")}</button>
       <div class="mas" id="masMenu" hidden>${MAS.map(item).join("")}</div>`;
  $("masBtn").onclick = () => { $("masMenu").hidden = !$("masMenu").hidden; };

  $("contenido").insertAdjacentHTML("afterbegin", `<div class="tope">${chips(prog)}</div>`);
  document.body.classList.remove("cargando");
  return { user, prog };
}
