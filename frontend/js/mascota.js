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
  "¿Por qué los programadores confunden Halloween con Navidad? Porque OCT 31 = DEC 25 🎃🎄",
  "Le pregunté a mi código si estaba bien. Me respondió: undefined.",
  "¿Cómo se despide un programador? —return; 👋",
  "El código que escribí ayer: obra maestra. El código que escribí hace un año: ¿quién escribió esto? 😱",
  "¿Por qué el HTML se fue de vacaciones? Necesitaba un <break> ☀️",
  "CSS es fácil. Es como montar en bicicleta… que está en llamas… y tú también. 🔥",
  "Un bug es una función que nadie pidió. 🐛",
  "¿Qué hace un programador en la playa? Busca la arena… perdón, el array. 🏖️",
  "¿Por qué JavaScript es tan dramático? Porque todo lo convierte en «true» 🎭",
  "Git: el único lugar donde «commitment» no da miedo. 💍",
  "¿Sabes por qué el teclado del programador está tan limpio? Porque usa Ctrl+Z para todo.",
  "Me pidieron que centrara un div. Sigo en eso desde 2019. 🫠",
  "¿Cuántos programadores se necesitan para cambiar un bombillo? Ninguno, es un problema de hardware 💡",
  "Mi relación con los punto y coma es complicada; a veces los olvido;",
  "Si tu código funciona a la primera, revisa: algo está mal. 🤨",
  "¿Por qué el bucle se fue al psicólogo? Porque no podía salir de sus problemas. 🔁",
  "Un programador va al súper: «trae una leche; si hay huevos, trae 6». Volvió con 6 leches. 🥛",
  "Estoy en una relación seria con Stack Overflow. 💘",
  "¿Qué le dijo el 0 al 8? ¡Qué bonito cinturón! 😄",
  "Le di un abrazo a mi computador. Ahora tiene «afecto secundario».",
  "¿Por qué Python no discute? Porque respeta la indentación de los demás. 🐍",
  "Mi código no tiene bugs, tiene «funciones sorpresa». 🎁",
  "¿Cómo llama un programador a su perro? Ruff… digo, Rust 🦀",
  "Hoy no hice deploy en viernes. Soy una persona feliz. 😌",
  "El mejor lenguaje de programación es el que te deja dormir. 😴",
];
const CONSEJOS = [
  "Consejo: lee el mensaje de error completo, casi siempre te dice la línea exacta.",
  "Consejo: guarda seguido con Ctrl+S y haz commits pequeños.",
  "Consejo: ponle nombres claros a tus variables, tu yo del futuro te lo agradecerá.",
  "Consejo: si te atascas, explícale el problema a alguien (o a mí) en voz alta.",
  "Consejo: practica 10 minutos diarios, vale más que 3 horas una vez al mes.",
  "Consejo: Ctrl+Shift+P abre todos los comandos de Trabajo.",
  "Consejo: prueba tu código con casos raros: vacío, negativo, muy grande.",
  "Consejo: console.log() y print() son tus mejores amigos para entender qué pasa.",
  "Consejo: divide los problemas grandes en pasitos pequeños. Así se programa todo.",
  "Consejo: Ctrl+P te lleva a cualquier archivo en Trabajo en un segundo.",
  "Consejo: si un reto se te complica, mira el ejemplo de la lección en Aprende.",
  "Consejo: descansa la vista cada 30 minutos: mira algo lejano 20 segundos.",
  "Consejo: los errores no son fracasos, son pistas. Cada error te enseña algo.",
  "Consejo: escribe comentarios que expliquen el «por qué», no el «qué».",
  "Consejo: antes de copiar código, entiéndelo línea por línea.",
  "Consejo: en Trabajo, Ctrl+I le pide a la IA que edite el código seleccionado.",
  "Consejo: la indentación ordenada hace que encuentres los errores más rápido.",
];
const ANIMOS = [
  "¡Vas muy bien! Cada línea de código cuenta 💪", "Recuerda: todos los expertos fueron principiantes.", "¡Hoy es un gran día para aprender algo nuevo!",
  "Un poquito cada día te lleva muy lejos 🚀", "Si te equivocas, ¡perfecto! Así se aprende.", "Estoy orgulloso de lo que estás logrando 💙",
  "¿Una lección más? ¡Tú puedes!", "Tu racha te está esperando 🔥", "Paso a paso se programa el mundo.",
];
/** Frases según la página y la hora (Codi «sabe» dónde estás) */
function fraseDeContexto() {
  const h = new Date().getHours();
  const saludo = h < 6 ? "¿Programando de madrugada? ¡Eres imparable! 🌙" : h < 12 ? "¡Buenos días! ☀️ ¿Aprendemos algo?" : h < 19 ? "¡Buenas tardes! ¿Le damos al código? 💻" : "¡Buenas noches! Un ratico de código antes de dormir 🌙";
  const pag = location.pathname.split("/").pop().replace(".html", "");
  const porPagina = {
    trabajo: ["Aquí se construyen cosas reales. ¿Qué vas a crear hoy? 🛠️", "Tip: Ctrl+Enter ejecuta el archivo abierto ▶️"],
    aprende: ["¡Hora de aprender! Lee el ejemplo y luego intenta el reto 🎯", "Cada lección te acerca a ser crack 📚"],
    reto: ["¡Concéntrate! Tú sabes esto 🧠", "Lee bien la pregunta: la respuesta está ahí 👀"],
    tienda: ["¿Me compras un accesorio? 👉👈", "Los teclados legendarios se mueven… ¡míralos! ✨"],
    chats: ["Programar con amigos es el doble de divertido 💬"],
    ia: ["Pregúntame lo que quieras, incluso lo «tonto». No hay preguntas tontas 🤖"],
    perfil: ["¡Mira todo lo que has logrado! 🏆"],
    recompensas: ["¡Cofres! Mis favoritos 🎁"],
    inicio: [saludo],
  };
  return azar([saludo, ...(porPagina[pag] || [])]);
}
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

// ----- Codi piensa por sí mismo: sus frases las crea la IA en el momento, con lo que estás haciendo.
// Se guardan un par «pensadas» de antemano para que responda al instante; si la IA no está, usa sus frases de siempre.
const PIENSA = { dichas: [], listas: {}, pidiendo: {}, apagada: 0 };
const paginaActual = () => (location.pathname.split("/").pop() || "inicio").replace(".html", "");
export async function codiPiensa(motivo, mensaje = "") {
  if (Date.now() < PIENSA.apagada) return null;
  try {
    const csrf = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
    const r = await fetch("/api/codi/pensar/", {
      method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ motivo, mensaje, pagina: paginaActual(), dichas: PIENSA.dichas.slice(-8) }),
    });
    if (r.status === 503) PIENSA.apagada = Date.now() + 10 * 60 * 1000;      // sin IA en este servidor: frases de siempre
    else if (r.status === 429 || r.status >= 500) PIENSA.apagada = Date.now() + 60 * 1000;
    if (!r.ok) return null;
    const d = await r.json();
    if (!d.frase) return null;
    PIENSA.dichas.push(d.frase);
    return d;
  } catch { return null; }
}
/** Una frase ya pensada (al instante) y deja otra pensándose para la próxima. */
function pensada(motivo) {
  const lista = (PIENSA.listas[motivo] ||= []);
  const d = lista.shift() || null;
  if (lista.length < 1 && !PIENSA.pidiendo[motivo]) {
    PIENSA.pidiendo[motivo] = true;
    codiPiensa(motivo).then((x) => { if (x) lista.push(x); }).finally(() => { PIENSA.pidiendo[motivo] = false; });
  }
  return d;
}
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
    raiz.classList.remove("m-salta", "m-gira", "m-saluda", "m-inclina", "m-baila", "m-temblor", "m-mira", "m-saltito", "m-estira");
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
  // ----- vida propia (como la mascota de Duolingo): respira, mira a los lados, da saltitos y a veces te habla
  raiz.classList.add("m-respira");
  const PEQUENAS = [["m-mira", null], ["m-saltito", null], ["m-saluda", null], ["m-estira", null], ["m-saltito", () => azar(ANIMOS)], ["m-mira", () => azar(CONSEJOS)]];
  const vida = setInterval(() => {
    if (dormido || reducido() || document.visibilityState !== "visible" || raiz.matches(":hover")) return;
    if (Date.now() - ultimaActividad < 4000 || Math.random() < 0.45) return;
    const [clase, frase] = azar(PEQUENAS);
    animar(clase);
    if (Math.random() < 0.3) {   // a veces dice lo que está pensando (inventado por la IA en el momento)
      const ia = pensada("vida");
      if (ia) { decir(ia.frase, 6000); return; }
    }
    if (frase && Math.random() < 0.35) decir(frase(), 5000);
  }, 9000);
  try {
    const clave = `cc_codi_hola_${location.pathname}`;
    if (!sessionStorage.getItem(clave)) {
      sessionStorage.setItem(clave, "1");
      const saludoIA = codiPiensa("saludo");
      setTimeout(async () => {
        const ia = await Promise.race([saludoIA, new Promise((ok) => setTimeout(() => ok(null), 2500))]);
        if (!dormido) { pintar(ia?.animo || "saludo"); decir(ia?.frase || fraseDeContexto(), 6000); animar("m-saltito"); clearTimeout(volver); volver = setTimeout(() => pintar(base), 2600); }
      }, 1500);
    }
  } catch { /* sin almacenamiento */ }
  pensada("toque"); setTimeout(() => pensada("vida"), 4000);   // deja frases pensadas para responder al instante
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
    const ia = Math.random() < 0.75 ? pensada(r.tipo === "chiste" ? "chiste" : r.tipo === "consejo" ? "consejo" : "toque") : null;
    if (ia) { reaccionar(ia.animo, ia.frase, 5200, r.clase); return; }
    const frase = r.tipo === "chiste" ? azar(CHISTES) : r.tipo === "consejo" ? azar(CONSEJOS) : (Math.random() < 0.25 ? azar(ANIMOS) : r.frase);
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
      ["💭", "¿Qué estás pensando?", () => pensarEnVoz("pensar")],
      ["🗨️", "Charlar con Codi aquí", charlar],
      ["😂", "Cuéntame un chiste", () => { sonar("codi_risa"); pensarEnVoz("chiste", () => azar(CHISTES), "m-salta"); }],
      ["💡", "Dame un consejo", () => { sonar("boop"); pensarEnVoz("consejo", () => azar(CONSEJOS), "m-inclina"); }],
      ["💪", "Dame ánimo", () => pensarEnVoz("animo", () => azar(ANIMOS))],
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
  /** Codi «piensa» (se ve pensando) y dice lo que se le ocurrió; si no hay IA, usa una de sus frases. */
  async function pensarEnVoz(motivo, respaldo = () => azar(ANIMOS), clase = "m-saluda") {
    pintar("pensando"); decir("…", 8000);
    const ia = pensada(motivo) || await codiPiensa(motivo);
    reaccionar(ia?.animo || "feliz", ia?.frase || respaldo(), 6500, clase);
  }
  /** Una burbuja para escribirle a Codi sin salir de la página. */
  function charlar() {
    document.querySelector(".m-charla")?.remove();
    const c = document.createElement("form");
    c.className = "m-charla";
    c.innerHTML = '<input maxlength="300" placeholder="Escríbele a Codi…" aria-label="Escríbele a Codi" autocomplete="off"><button type="submit" aria-label="Enviar">➤</button><button type="button" data-x aria-label="Cerrar">✕</button>';
    document.body.appendChild(c);
    const r = raiz.getBoundingClientRect();
    c.style.left = `${Math.min(innerWidth - c.offsetWidth - 8, Math.max(8, r.left))}px`;
    c.style.top = `${r.top - c.offsetHeight - 10 > 8 ? r.top - c.offsetHeight - 10 : r.bottom + 10}px`;
    const inp = c.querySelector("input");
    inp.focus();
    c.querySelector("[data-x]").onclick = () => c.remove();
    c.onsubmit = async (e) => {
      e.preventDefault();
      const t = inp.value.trim();
      if (!t) return;
      inp.value = ""; inp.disabled = true;
      pintar("pensando"); decir("…", 8000);
      const ia = await codiPiensa("charla", t);
      inp.disabled = false; inp.focus();
      reaccionar(ia?.animo || "feliz", ia?.frase || "Uy, se me cruzaron los cables 🤖 ¿Me lo repites?", 8000, "m-saluda");
    };
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
      clearInterval(reloj); clearInterval(vida); clearTimeout(volver); cerrarMenu();
      removeEventListener("pointermove", alMover); removeEventListener("codi", alEvento);
      removeEventListener("keydown", actividad); removeEventListener("scroll", actividad);
    },
  };
}

/** Atajo para que cualquier parte de la app haga reaccionar a Codi. */
export function codiReacciona(animo, frase, ms) {
  dispatchEvent(new CustomEvent("codi", { detail: { animo, frase, ms } }));
}
