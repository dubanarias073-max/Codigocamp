/* Codi como mascota interactiva (menú lateral de todas las páginas y Trabajo).
   · Te sigue con la mirada cuando mueves el mouse.
   · Tócalo: reacciona (salta, se ríe, gira, te cuenta un chiste o un consejo). Tócalo varias veces seguidas: ¡baila!
   · Acarícialo (deja el mouse o el dedo encima): suelta corazones.
   · Si no haces nada por un rato se duerme; cuando vuelves, se despierta y te saluda.
   · Mantén pulsado (o doble clic): menú con acciones (hablar con Codi, bailar, chiste, consejo, dormir).
   · Reacciona a lo que pasa en la app: window.dispatchEvent(new CustomEvent("codi", { detail: { animo, frase, ms } })).
     Trabajo lo usa al ejecutar (celebra si salió bien, se preocupa si hay errores) y los retos al acertar o fallar. */
import { codiSVG, fraseDe } from "/js/codi.js";

const CHISTES = [
  "¿Por qué el programador dejó su trabajo? Porque no le daban arrays 🙃",
  "Hay 10 tipos de personas: las que entienden binario y las que no.",
  "Mi código funciona y no sé por qué. Mi código no funciona y no sé por qué. 🤷",
  "¿Qué le dijo un bit al otro? Nos vemos en el bus.",
  "Un SQL entra a un bar, se acerca a dos mesas y pregunta: ¿puedo hacer JOIN?",
  "Programar es 10 % escribir código y 90 % entender por qué no funciona.",
  "¿Cuál es el animal favorito de un programador? ¡El Python! 🐍",
  "Mi café y yo tenemos algo en común: los dos somos Java ☕",
];
const CONSEJOS = [
  "Consejo: lee el mensaje de error completo, casi siempre te dice la línea exacta.",
  "Consejo: guarda seguido con Ctrl+S y haz commits pequeños.",
  "Consejo: ponle nombres claros a tus variables, tu yo del futuro te lo agradecerá.",
  "Consejo: si te atascas, explícale el problema a alguien (o a mí) en voz alta.",
  "Consejo: practica 10 minutos diarios, vale más que 3 horas una vez al mes.",
  "Consejo: Ctrl+Shift+P abre todos los comandos de Trabajo.",
  "Consejo: prueba tu código con casos raros: vacío, negativo, muy grande.",
];
const REACCIONES = [
  { animo: "celebra", frase: "¡Jiji, eso da cosquillas!", sonido: "codi_risa", clase: "m-salta" },
  { animo: "saludo", frase: "¡Hola! ¿Programamos algo?", sonido: "boop", clase: "m-saluda" },
  { animo: "feliz", frase: "¡Bip bup! Estoy listo", sonido: "boop", clase: "m-gira" },
  { animo: "pensando", frase: null, sonido: "boop", clase: "m-inclina", tipo: "consejo" },
  { animo: "celebra", frase: null, sonido: "codi_risa", clase: "m-salta", tipo: "chiste" },
  { animo: "guino", frase: "Psst… tú puedes con todo 😉", sonido: "codi_guino", clase: "m-saluda" },
  { animo: "asombro", frase: "¡Wow! ¿Ya viste todo lo que has aprendido?", sonido: "codi_wow", clase: "m-salta" },
  { animo: "ama", frase: "¡Me encanta programar contigo! 💙", sonido: "codi_amor", clase: "m-saluda" },
  { animo: "espia", frase: "¿Qué estás programando? 👀", sonido: "codi_tapa", clase: "m-inclina" },
];
const azar = (l) => l[Math.floor(Math.random() * l.length)];
const reducido = () => matchMedia("(prefers-reduced-motion: reduce)").matches || document.documentElement.classList.contains("menos-movimiento");
const sonar = (n) => import("/js/sonidos.js").then((m) => m.sonar(n)).catch(() => {});

/**
 * @param {HTMLElement} raiz        contenedor de Codi (se reemplaza su contenido)
 * @param {{ animo?: string, tam?: number, globo?: HTMLElement|null, urlIA?: string, alHablar?: () => void }} o
 */
export function activarMascota(raiz, { animo = "saludo", tam = 64, globo = null, urlIA = "/pages/ia.html", alHablar = null } = {}) {
  if (!raiz || raiz.dataset.mascota) return null;
  raiz.dataset.mascota = "1";
  raiz.classList.add("mascota");
  raiz.setAttribute("role", "button");
  raiz.tabIndex = 0;
  raiz.setAttribute("aria-label", "Codi, tu mascota. Tócalo para jugar; mantén pulsado para ver más opciones");
  const base = animo;
  let actual = null, volver = null, dormido = false, ultimaActividad = Date.now(), toques = 0, tToques = null, caricia = null;

  const pintar = (a) => {
    if (a === actual) return;
    actual = a;
    raiz.innerHTML = codiSVG(a, { tam, titulo: "Codi" });
  };
  const decir = (texto, ms = 4200) => {
    if (!globo || !texto) return;
    globo.textContent = texto;
    globo.classList.remove("m-globo-nuevo"); void globo.offsetWidth; globo.classList.add("m-globo-nuevo");
    clearTimeout(globo._t);
    globo._t = setTimeout(() => { if (!dormido) globo.textContent = fraseDe(base); }, ms);
  };
  const animar = (clase) => {
    if (reducido() || !clase) return;
    raiz.classList.remove("m-salta", "m-gira", "m-saluda", "m-inclina", "m-baila", "m-temblor");
    void raiz.offsetWidth;
    raiz.classList.add(clase);
    setTimeout(() => raiz.classList.remove(clase), clase === "m-baila" ? 2600 : 900);
  };
  const reaccionar = (a, frase, ms = 3500, clase = "m-salta") => {
    despertar(false);
    pintar(a);
    if (frase) decir(frase, ms + 600);
    animar(clase);
    clearTimeout(volver);
    volver = setTimeout(() => pintar(base), ms);
  };

  // ----- mirada que sigue al cursor
  let rafMirada = 0;
  const mirar = (x, y) => {
    if (dormido || reducido()) return;
    cancelAnimationFrame(rafMirada);
    rafMirada = requestAnimationFrame(() => {
      const ojo = raiz.querySelector(".cdx-mirada");
      if (!ojo) return;
      const r = raiz.getBoundingClientRect();
      const dx = x - (r.left + r.width / 2), dy = y - (r.top + r.height * 0.45);
      const d = Math.hypot(dx, dy) || 1;
      const k = Math.min(1, d / 260);
      ojo.style.transform = `translate(${(dx / d) * 7 * k}px, ${(dy / d) * 5 * k}px)`;
    });
  };
  const alMover = (e) => { actividad(); mirar(e.clientX, e.clientY); };
  addEventListener("pointermove", alMover, { passive: true });

  // ----- sueño por inactividad
  const actividad = () => { ultimaActividad = Date.now(); if (dormido) despertar(true); };
  const despertar = (saludar) => {
    if (!dormido) return;
    dormido = false;
    raiz.classList.remove("m-dormido");
    if (saludar) { sonar("codi_despierta"); reaccionar("saludo", azar(["¡Ah! Me quedé dormido 😅", "¡Volviste! Te estaba esperando", "¿Seguimos programando?"]), 3000, "m-salta"); }
  };
  const dormir = () => {
    if (dormido) return;
    dormido = true;
    clearTimeout(volver);
    pintar("dormido");
    raiz.classList.add("m-dormido");
    decir("Zzz… muévete o tócame para despertarme", 60000);
    sonar("codi_bostezo");
  };
  const reloj = setInterval(() => { if (!dormido && Date.now() - ultimaActividad > 3 * 60 * 1000 && document.visibilityState === "visible") dormir(); }, 15000);
  addEventListener("keydown", actividad, { passive: true });
  addEventListener("scroll", actividad, { passive: true });

  // ----- tocar, tocar varias veces (bailar), mantener pulsado (menú) y acariciar
  let tPulsar = null, pulsoLargo = false;
  raiz.addEventListener("pointerdown", (e) => {
    pulsoLargo = false;
    tPulsar = setTimeout(() => { pulsoLargo = true; abrirMenu(); }, 550);
    if (e.pointerType === "touch") empezarCaricia();
  });
  const soltar = () => { clearTimeout(tPulsar); terminarCaricia(); };
  raiz.addEventListener("pointerup", soltar);
  raiz.addEventListener("pointerleave", soltar);
  raiz.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") empezarCaricia(); });
  raiz.addEventListener("contextmenu", (e) => { e.preventDefault(); abrirMenu(); });
  raiz.addEventListener("dblclick", (e) => { e.preventDefault(); abrirMenu(); });
  const tocar = () => {
    actividad();
    toques++;
    clearTimeout(tToques);
    tToques = setTimeout(() => { toques = 0; }, 1200);
    if (toques >= 4) { toques = 0; bailar(); return; }
    const r = azar(REACCIONES);
    sonar(r.sonido);
    const frase = r.tipo === "chiste" ? azar(CHISTES) : r.tipo === "consejo" ? azar(CONSEJOS) : r.frase;
    reaccionar(r.animo, frase, r.tipo ? 5200 : 2600, r.clase);
  };
  raiz.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); if (!pulsoLargo) tocar(); });
  raiz.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); tocar(); }
    if (e.key === "ContextMenu" || (e.shiftKey && e.key === "F10")) { e.preventDefault(); abrirMenu(); }
  });

  function empezarCaricia() {
    clearTimeout(caricia);
    caricia = setTimeout(() => {
      if (dormido) return;
      sonar("codi_feliz");
      corazones();
      reaccionar("feliz", azar(["¡Me encantan los mimos!", "Bip… bup… feliz 🥰"]), 2600, "m-saluda");
    }, 900);
  }
  function terminarCaricia() { clearTimeout(caricia); }

  function corazones(n = 5) {
    if (reducido()) return;
    const r = raiz.getBoundingClientRect();
    for (let i = 0; i < n; i++) {
      const c = document.createElement("span");
      c.className = "m-corazon";
      c.textContent = azar(["💙", "💚", "💜", "✨"]);
      c.style.left = `${r.left + r.width * (0.25 + Math.random() * 0.5)}px`;
      c.style.top = `${r.top + r.height * 0.2}px`;
      c.style.animationDelay = `${i * 0.12}s`;
      c.style.setProperty("--dx", `${(Math.random() - 0.5) * 50}px`);
      document.body.appendChild(c);
      setTimeout(() => c.remove(), 2200);
    }
  }
  function bailar() {
    sonar("codi_baile");
    reaccionar("baila", azar(["¡A bailar! 🕺", "¡Modo fiesta activado! 🎉", "Bip bip bup, ¡qué ritmo!"]), 3200, "m-baila");
    corazones(3);
  }

  function abrirMenu() {
    cerrarMenu();
    actividad();
    sonar("abrir");
    const m = document.createElement("div");
    m.className = "m-menu";
    m.setAttribute("role", "menu");
    const ops = [
      ["💬", "Hablar con Codi", () => (alHablar ? alHablar() : (location.href = urlIA))],
      ["🕺", "¡Baila!", bailar],
      ["😂", "Cuéntame un chiste", () => { sonar("codi_risa"); reaccionar("celebra", azar(CHISTES), 6000, "m-salta"); }],
      ["💡", "Dame un consejo", () => { sonar("boop"); reaccionar("pensando", azar(CONSEJOS), 6000, "m-inclina"); }],
      ["💙", "Acariciar", () => { sonar("codi_amor"); corazones(); reaccionar("ama", "¡Gracias! Eres lo máximo 💙", 2800, "m-saluda"); }],
      ["😉", "Guíñame un ojo", () => { sonar("codi_guino"); reaccionar("guino", azar(["😉 Te guardo el secreto", "Tú puedes, crack 😉", "Esto queda entre nosotros"]), 2600, "m-saluda"); }],
      ["🙈", "Juguemos a esconderse", () => { sonar("codi_tapa"); reaccionar("tapa", "1, 2, 3… ¡no estoy mirando! 🙈", 1800, "m-inclina"); setTimeout(() => { sonar("codi_wow"); reaccionar("espia", "¡Te encontré! 👀", 2200, "m-salta"); }, 1900); }],
      ["😴", "A dormir", dormir],
    ];
    m.innerHTML = ops.map(([ic, t], i) => `<button type="button" role="menuitem" data-i="${i}"><span>${ic}</span>${t}</button>`).join("");
    document.body.appendChild(m);
    const r = raiz.getBoundingClientRect();
    const alto = m.offsetHeight, ancho = m.offsetWidth;
    m.style.left = `${Math.min(innerWidth - ancho - 8, Math.max(8, r.left))}px`;
    m.style.top = `${r.top - alto - 8 > 8 ? r.top - alto - 8 : Math.min(innerHeight - alto - 8, r.bottom + 8)}px`;
    m.querySelector("button")?.focus();
    m.addEventListener("click", (e) => { const b = e.target.closest("[data-i]"); if (!b) return; cerrarMenu(); ops[Number(b.dataset.i)][2](); });
    m.addEventListener("keydown", (e) => {
      const bs = [...m.querySelectorAll("button")], i = bs.indexOf(document.activeElement);
      if (e.key === "Escape") { cerrarMenu(); raiz.focus(); }
      if (e.key === "ArrowDown") { e.preventDefault(); bs[(i + 1) % bs.length].focus(); }
      if (e.key === "ArrowUp") { e.preventDefault(); bs[(i - 1 + bs.length) % bs.length].focus(); }
    });
    setTimeout(() => addEventListener("pointerdown", fueraMenu, true), 0);
  }
  function fueraMenu(e) { if (!e.target.closest(".m-menu")) cerrarMenu(); }
  function cerrarMenu() { document.querySelectorAll(".m-menu").forEach((x) => x.remove()); removeEventListener("pointerdown", fueraMenu, true); }

  // ----- reacciones a lo que pasa en la app
  const alEvento = (e) => {
    const d = e.detail || {};
    if (d.animo === "celebra") corazones(3);
    reaccionar(d.animo || "feliz", d.frase || fraseDe(d.animo || "feliz", Date.now()), d.ms || 3500, d.animo === "alarma" || d.animo === "preocupado" ? "m-temblor" : "m-salta");
  };
  addEventListener("codi", alEvento);

  // saludo según la hora del día (solo la primera vez en esta pestaña)
  pintar(base);
  try {
    if (!sessionStorage.getItem("cc_codi_saludo")) {
      sessionStorage.setItem("cc_codi_saludo", "1");
      const h = new Date().getHours();
      setTimeout(() => reaccionar("saludo", h < 12 ? "¡Buenos días! ☀️ ¿Aprendemos algo hoy?" : h < 19 ? "¡Buenas tardes! ¿Le damos al código?" : "¡Buenas noches! 🌙 Un ratito de código y a dormir", 4200, "m-saluda"), 900);
    }
  } catch { /* sin almacenamiento */ }

  return {
    reaccionar, decir, dormir,
    destruir() {
      clearInterval(reloj); clearTimeout(volver); cerrarMenu();
      removeEventListener("pointermove", alMover); removeEventListener("codi", alEvento);
      removeEventListener("keydown", actividad); removeEventListener("scroll", actividad);
    },
  };
}

/** Atajo para que cualquier parte de la app haga reaccionar a Codi. */
export function codiReacciona(animo, frase, ms) {
  dispatchEvent(new CustomEvent("codi", { detail: { animo, frase, ms } }));
}
