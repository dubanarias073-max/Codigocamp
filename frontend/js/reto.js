// Lógica de reto.html
import { codiSVG } from "/js/codi.js";
import { aplicarCosmeticos } from "/js/cosmeticos.js";
// El fondo y los cosméticos que compraste también se ven en los retos
try { aplicarCosmeticos(JSON.parse(localStorage.getItem("cc_cosm") || "{}")); } catch { /* sin cosméticos guardados */ }
import { sonar, vibrar } from "/js/sonidos.js";
import { api, getUser } from "/js/auth.js";
import { correr } from "/js/retos-motor.js";
const $ = (id) => document.getElementById(id);
const el = (tag, texto, cls) => { const e = document.createElement(tag); if (texto != null) e.textContent = texto; if (cls) e.className = cls; return e; };
const TIPOS = { opcion: "Elige la respuesta correcta", completar: "Completa", error: "Encuentra el error", ordenar: "Ordena los pasos", codigo: "Escribe código", caso: "Caza el bug · pruebas de software", parejas: "Une las parejas", armar: "Arma la línea con las fichas" };

// Mismo hash que el servidor (FNV-1a de 32 bits): dice si una pareja es correcta sin conocer las parejas.
function fnv1a(texto) {
  let h = 0x811c9dc5;
  for (const b of new TextEncoder().encode(texto)) h = Math.imul(h ^ b, 0x01000193) >>> 0;
  return h.toString(16).padStart(8, "0");
}

const user = await getUser();
if (!user) location.replace("/pages/login.html");
else {
  const t = user.tema === "claro" || user.tema === "oscuro" ? user.tema : "auto";
  document.documentElement.dataset.tema = t;
  try { localStorage.setItem("cc_tema", t); } catch {}
}

// cola: las preguntas falladas vuelven al final hasta acertarlas
let datos, cola = [], total = 0, hechas = 0, fallos = 0, vidas = 0, fase = "preguntar", render = null, ultimoOk = false, enCurso = false;
let sonidoActivo = true, audioContext = null, audioDisponible = Boolean(window.AudioContext || window.webkitAudioContext), animacionRespuesta;
try { sonidoActivo = localStorage.getItem("cc_sonido") !== "0"; } catch {}
sonidoActivo = sonidoActivo && audioDisponible;

function prepararAudio() {
  if (!sonidoActivo || !audioDisponible) return;
  try {
    const AudioCtor = window.AudioContext || window.webkitAudioContext;
    audioContext ||= new AudioCtor();
    const activacion = audioContext.resume();
    if (activacion?.catch) activacion.catch(() => {
      sonidoActivo = false;
      audioDisponible = false;
    });
  } catch {
    sonidoActivo = false;
    audioDisponible = false;
  }
}

function reproducirTono(frecuencia, inicio, duracion, forma, frecuenciaFinal = frecuencia) {
  const oscilador = audioContext.createOscillator();
  const volumen = audioContext.createGain();
  oscilador.type = forma;
  oscilador.frequency.setValueAtTime(frecuencia, inicio);
  oscilador.frequency.exponentialRampToValueAtTime(frecuenciaFinal, inicio + duracion);
  volumen.gain.setValueAtTime(0.0001, inicio);
  volumen.gain.exponentialRampToValueAtTime(0.11, inicio + 0.015);
  volumen.gain.exponentialRampToValueAtTime(0.0001, inicio + duracion);
  oscilador.connect(volumen);
  volumen.connect(audioContext.destination);
  oscilador.start(inicio);
  oscilador.stop(inicio + duracion + 0.02);
}

function reproducirRespuesta(correcta) {
  // Codi (la mascota del menú) reacciona a cada respuesta
  dispatchEvent(new CustomEvent("codi", { detail: correcta
    ? { animo: "celebra", frase: ["¡Correcto! 🎉", "¡Eso es!", "¡Lo tienes!", "¡Muy bien!"][Math.floor(Math.random() * 4)], ms: 2200 }
    : { animo: "preocupado", frase: ["¡Casi! Lee la explicación", "No pasa nada, ¡sigue!", "Uy… revisemos juntos"][Math.floor(Math.random() * 3)], ms: 2600 } }));
  if (sonar(correcta ? "correcto" : "incorrecto")) return;   // sonidos con temática de código (js/sonidos.js)
  if (!sonidoActivo || !audioContext || audioContext.state !== "running") return;
  const ahora = audioContext.currentTime;
  if (correcta) {
    reproducirTono(720, ahora, 0.12, "sine", 880);
    reproducirTono(990, ahora + 0.09, 0.18, "sine", 1320);
  } else {
    reproducirTono(410, ahora, 0.18, "triangle", 300);
    reproducirTono(290, ahora + 0.13, 0.2, "triangle", 190);
  }
}

function animarRespuesta(correcta) {
  document.body.classList.remove("respuesta-correcta", "respuesta-incorrecta");
  void document.body.offsetWidth;
  document.body.classList.add(correcta ? "respuesta-correcta" : "respuesta-incorrecta");
  clearTimeout(animacionRespuesta);
  animacionRespuesta = setTimeout(() => document.body.classList.remove("respuesta-correcta", "respuesta-incorrecta"), 700);
}

// Barra de progreso animada + contador "3/10". `pulso` hace brillar la barra cuando avanza.
function progreso(pulso) {
  const pct = total ? Math.round(hechas / total * 100) : 0;
  $("prog").style.width = pct + "%"; $("barra").setAttribute("aria-valuenow", pct);
  $("cuenta").textContent = hechas + "/" + total;
  if (pulso) { $("barra").classList.remove("pulso"); void $("barra").offsetWidth; $("barra").classList.add("pulso"); }
}

// Salir de la lección: se pregunta antes de perder el avance.
function pedirSalida() { if (!enCurso) { location.href = "/pages/inicio.html"; return; } $("confirmarSalida").hidden = false; $("seguir").focus(); }
function seguirAprendiendo() { $("confirmarSalida").hidden = true; $("salir").focus(); }
$("salir").onclick = pedirSalida;
$("seguir").onclick = seguirAprendiendo;
$("salirYa").onclick = (e) => { e.preventDefault(); enCurso = false; location.href = datos ? "/pages/inicio.html?curso=" + datos.curso.slug : "/pages/inicio.html"; };
window.addEventListener("beforeunload", (e) => { if (enCurso && hechas > 0) { e.preventDefault(); e.returnValue = ""; } });
history.pushState({ leccion: true }, "");   // el botón Atrás también pregunta
window.addEventListener("popstate", () => { if (enCurso) { history.pushState({ leccion: true }, ""); pedirSalida(); } });
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (!$("confirmarSalida").hidden) seguirAprendiendo(); else if (enCurso) pedirSalida();
});

// Cada tipo devuelve { obtener(), bloquear(), local?(valor) }. Si tiene local, el navegador evalúa la respuesta.
const RENDER = {
  opcion(q, cont, cambio) {
    if (q.codigo) cont.append(el("pre", q.codigo, "cod"));
    let sel = null; const botones = q.opciones.map((t, i) => {
      const b = el("button", t, "opc"); b.type = "button";
      b.onclick = () => { sel = t; botones.forEach((x) => x.classList.toggle("sel", x === b)); cambio(); }; cont.append(b); return b; });
    return { obtener: () => sel, bloquear: () => botones.forEach((b) => { b.disabled = true; }) };
  },
  completar(q, cont, cambio) {
    if (q.codigo) cont.append(el("pre", q.codigo, "cod"));
    const inp = el("input", null, "r-in"); inp.placeholder = "Escribe tu respuesta"; inp.autocomplete = "off"; inp.spellcheck = false; inp.oninput = cambio;
    cont.append(inp); setTimeout(() => inp.focus(), 0);
    return { obtener: () => (inp.value.trim() ? inp.value : null), bloquear: () => { inp.disabled = true; } };
  },
  error(q, cont, cambio) {
    let sel = null; const caja = el("div", null, "lineas");
    const botones = q.codigo.split("\n").map((linea, i) => {
      const b = el("button", null, "linea"); b.type = "button"; b.append(el("span", String(i + 1), "ln"), el("code", linea || " "));
      b.onclick = () => { sel = i + 1; botones.forEach((x, j) => x.classList.toggle("sel", j === i)); cambio(); }; caja.append(b); return b; });
    cont.append(caja);
    return { obtener: () => sel, bloquear: () => botones.forEach((b) => { b.disabled = true; }) };
  },
  ordenar(q, cont, cambio) {
    let banco = q.piezas.map((t, i) => ({ t, i })), resp = [];
    const zona = el("div", null, "zona-resp"), bancoEl = el("div", null, "banco");
    const chip = (p, fn) => { const b = el("button", p.t, "pieza"); b.type = "button"; b.onclick = fn; return b; };
    const pintar = () => {
      zona.replaceChildren(...resp.map((p) => chip(p, () => { resp = resp.filter((x) => x !== p); banco.push(p); pintar(); cambio(); })));
      bancoEl.replaceChildren(...banco.map((p) => chip(p, () => { banco = banco.filter((x) => x !== p); resp.push(p); pintar(); cambio(); })));
    };
    pintar(); cont.append(el("p", "Toca las piezas en el orden correcto:", "nota"), zona, bancoEl);
    return { obtener: () => (resp.length === q.piezas.length ? resp.map((p) => p.t) : null),
      bloquear: () => { zona.classList.add("fija"); bancoEl.classList.add("fija"); cont.querySelectorAll("button").forEach((b) => { b.disabled = true; }); } };
  },
  parejas(q, cont, cambio) {
    // Como Duolingo: tocas uno de la izquierda y uno de la derecha. Bien: quedan en verde. Mal: tiemblan y cuenta un error.
    const sellos = new Set(q.sellos);
    const unidas = [];
    let fallos = 0, elegido = null;
    const tablero = el("div", null, "parejas");
    const colI = el("div", null, "par-col"), colD = el("div", null, "par-col");
    const aviso = el("p", "", "par-aviso");
    const boton = (x, lado) => {
      const b = el("button", x.t, "par"); b.type = "button"; b.dataset.lado = lado; b.dataset.id = x.id;
      b.onclick = () => {
        if (b.classList.contains("hecha")) return;
        if (!elegido || elegido.dataset.lado === lado) {
          tablero.querySelectorAll(".par.sel").forEach((y) => y.classList.remove("sel"));
          elegido = b; b.classList.add("sel"); sonar("toque"); return;
        }
        const [iz, de] = lado === "d" ? [elegido, b] : [b, elegido];
        elegido.classList.remove("sel"); elegido = null;
        if (sellos.has(fnv1a(`${q.sal}|${iz.dataset.id}|${de.dataset.id}`))) {
          unidas.push([Number(iz.dataset.id), de.dataset.id]);
          for (const y of [iz, de]) { y.classList.add("hecha"); y.disabled = true; }
          sonar("pareja"); vibrar(12);
          if (unidas.length === q.izq.length) cambio();
        } else {
          fallos += 1;
          for (const y of [iz, de]) { y.classList.remove("mal"); void y.offsetWidth; y.classList.add("mal"); setTimeout(() => y.classList.remove("mal"), 600); }
          sonar("pareja_mal"); vibrar([20, 30, 20]);
          const quedan = (q.tolerancia || 0) - fallos;
          aviso.textContent = quedan < 0 ? "Esa no era: esta vez cuenta como error. Termina de unirlas y lee la explicación."
            : quedan === 0 ? "Esa no era. Cuidado: otro error y cuenta como fallo." : `Esa no era. Puedes equivocarte ${quedan} vez más.`;
        }
      };
      return b;
    };
    q.izq.forEach((x) => colI.append(boton(x, "i")));
    q.der.forEach((x) => colD.append(boton(x, "d")));
    tablero.append(colI, colD);
    cont.append(tablero, aviso);
    return { obtener: () => (unidas.length === q.izq.length ? { pares: unidas, fallos } : null),
      bloquear: () => tablero.querySelectorAll("button").forEach((b) => { b.disabled = true; }) };
  },
  armar(q, cont, cambio) {
    // Banco de fichas (como Duolingo): tocas las fichas en orden para armar la línea que falta. Algunas sobran.
    if (q.codigo) {
      const pre = el("pre", null, "cod");
      q.codigo.split("▁▁▁").forEach((parte, i, todas) => {
        pre.append(document.createTextNode(parte));
        if (i < todas.length - 1) { const h = el("span", "", "hueco-cod"); h.id = "huecoArmar"; pre.append(h); }
      });
      cont.append(pre);
    }
    let banco = q.fichas.map((t, i) => ({ t, i })), resp = [];
    const zona = el("div", null, "zona-resp zona-armar"), bancoEl = el("div", null, "banco");
    const chip = (p, fn) => { const b = el("button", p.t, "pieza ficha"); b.type = "button"; b.onclick = () => { sonar("toque"); fn(); }; return b; };
    const pintar = () => {
      zona.replaceChildren(...resp.map((p) => chip(p, () => { resp = resp.filter((x) => x !== p); banco.push(p); banco.sort((a, b) => a.i - b.i); pintar(); cambio(); })));
      bancoEl.replaceChildren(...banco.map((p) => chip(p, () => { banco = banco.filter((x) => x !== p); resp.push(p); pintar(); cambio(); })));
      const h = cont.querySelector("#huecoArmar");
      if (h) h.textContent = resp.length ? resp.map((p) => p.t).join(" ") : "▁▁▁";
    };
    pintar(); cont.append(el("p", "Toca las fichas en orden (algunas sobran):", "nota"), zona, bancoEl);
    return { obtener: () => (resp.length ? resp.map((p) => p.t) : null),
      bloquear: () => { zona.classList.add("fija"); bancoEl.classList.add("fija"); cont.querySelectorAll("button").forEach((b) => { b.disabled = true; }); } };
  },
  codigo(q, cont, cambio, item) {
    const ej = el("div", null, "ejemplos"); ej.append(el("p", "Ejemplos (hay además pruebas ocultas):", "nota"));
    q.casos.filter((c) => c.v !== false).forEach((c) => ej.append(el("code", `${q.fn}(${c.a.map((x) => JSON.stringify(x)).join(", ")})  →  ${JSON.stringify(c.r)}`)));
    const ta = el("textarea", null, "editor"); ta.value = item.ultimo ?? q.plantilla; ta.spellcheck = false; ta.oninput = cambio;
    ta.onkeydown = (e) => { if (e.key === "Tab") { e.preventDefault(); ta.setRangeText("  ", ta.selectionStart, ta.selectionEnd, "end"); cambio(); } };
    cont.append(ej, ta);
    return { obtener: () => (ta.value.trim() ? ta.value : null), bloquear: () => { ta.disabled = true; },
      async local(codigo) {
        item.ultimo = codigo;
        const r = await correr({ modo: "tests", codigo, fn: q.fn, casos: q.casos });
        if (r.error) return { invalido: true, mensaje: "No pude ejecutar tu código: " + r.error };
        const detalle = r.res.map((x) => x.v ? { ok: x.ok, texto: x.ok ? `${q.fn}(${x.entrada}) → ${x.got}` : `${q.fn}(${x.entrada}): esperaba ${x.esperado} y obtuve ${x.got}` }
          : { ok: x.ok, texto: x.ok ? "Prueba oculta superada" : "Prueba oculta fallida: piensa en los casos límite" });
        const pasadas = r.res.filter((x) => x.ok).length;
        return { ok: pasadas === r.res.length, titulo: pasadas === r.res.length ? "¡Todas las pruebas superadas!" : `Pruebas superadas: ${pasadas} de ${r.res.length}`, detalle };
      } };
  },
  caso(q, cont, cambio, item) {
    cont.append(el("pre", q.defectuosa, "cod"), el("p", "Escribe los argumentos de entrada separados por comas. Los textos van entre comillas.", "nota"));
    const inp = el("input", null, "r-in"); inp.placeholder = 'Ej.: 2024   o   "texto", 5'; inp.autocomplete = "off"; inp.spellcheck = false; inp.value = item.ultimo ?? ""; inp.oninput = cambio;
    cont.append(inp); setTimeout(() => inp.focus(), 0);
    return { obtener: () => (inp.value.trim() ? inp.value : null), bloquear: () => { inp.disabled = true; },
      async local(txt) {
        item.ultimo = txt; let args;
        try { args = JSON.parse("[" + txt + "]"); } catch { return { invalido: true, mensaje: 'No entendí los argumentos. Escríbelos como JSON, por ejemplo: 2024  o  "texto", 5' }; }
        const r = await correr({ modo: "caso", defectuosa: q.defectuosa, correcta: q.correcta, fn: q.fn, args });
        if (r.error) return { invalido: true, mensaje: "No pude ejecutar la prueba: " + r.error };
        return { ok: r.distinto, titulo: r.distinto ? "¡Bug encontrado!" : "Con esa entrada ambas versiones dan lo mismo",
          detalle: [{ ok: r.distinto, texto: `${q.fn}(${txt}) → defectuosa: ${r.defectuosa} · correcta: ${r.correcta}` }] };
      } };
  },
};

// Examen para «Saltar aquí» (?salto=seccion:12 o etapa:3): cada pregunta sale una vez, no gasta vidas y hay un máximo de errores
const SALTO = (new URLSearchParams(location.search).get("salto") || "").match(/^(seccion|etapa):(\d+)$/);
let examen = null;

async function main() {
  const idNivel = new URLSearchParams(location.search).get("nivel");
  if (!SALTO && !/^\d+$/.test(idNivel || "")) { location.replace("aprende.html"); return; }
  try { datos = await api(SALTO ? `/api/salto/${SALTO[1]}/${SALTO[2]}/` : "/api/nivel/" + idNivel + "/"); examen = datos.examen || null; }
  catch (e) { $("cuerpo").innerHTML = ""; $("cuerpo").append(el("p", e.message, "vacio")); return; }
  vidas = datos.vidas; $("vidas").textContent = vidas;
  if (/^#[0-9a-f]{6}$/i.test(datos.curso.color || "")) {
    document.documentElement.style.setProperty("--curso", datos.curso.color);
  }
  if (vidas <= 0 && !examen) { enCurso = false; $("sinVidas").hidden = false; return; }
  cola = datos.retos.map((q) => ({ q, ultimo: null })); total = cola.length;
  if (examen) {   // aviso al empezar: qué es y cuántos errores se permiten
    const caja = document.querySelector(".r-vidas");
    if (caja) { caja.title = "Errores del examen (máximo permitido)"; caja.innerHTML = '<span id="vidas"></span>'; }
    $("vidas").textContent = `✗ 0/${examen.tolerancia}`;
    const av = el("div", "", "examen-aviso");
    av.append(el("b", "⏩ Examen para saltar"), el("span", `${examen.total} preguntas de todo lo anterior a ${examen.objetivo}. Puedes fallar hasta ${examen.tolerancia}. No gasta vidas.`));
    av.style.cssText = "position:relative;z-index:2;display:grid;gap:4px;width:min(680px,calc(100% - 32px));margin:10px auto 0;padding:12px 14px;border:2px solid var(--curso,#58cc02);border-radius:16px;background:color-mix(in srgb,var(--curso,#58cc02) 10%,transparent);font-size:14px";
    $("cuerpo").before(av);
    setTimeout(() => av.remove(), 9000);
  }
  document.title = datos.nivel.titulo + " · CódigoCamp";
  enCurso = total > 0; progreso(false);
  $("pie").hidden = false; mostrar();
}

function mostrar() {
  const item = cola[0], q = item.q;
  fase = "preguntar";
  progreso(false);
  $("pie").className = "r-pie"; $("mensaje").replaceChildren();
  $("accion").textContent = "Comprobar"; $("accion").className = "bj"; $("accion").disabled = true;
  const cont = $("cuerpo");
  // Como en Duolingo: Codi te «dice» la pregunta en un globo
  const enunciado = document.createElement("div");
  enunciado.className = "r-enunciado";
  enunciado.innerHTML = `<span class="r-codi-preg">${codiSVG(hechas === 0 ? "saludo" : fallos > 2 ? "preocupado" : "pensando", { tam: 84 })}</span>`;
  enunciado.append(el("h1", q.enunciado));
  cont.replaceChildren(el("p", TIPOS[q.tipo], "r-tipo"), enunciado);
  cont.classList.remove("entra"); void cont.offsetWidth; cont.classList.add("entra");   // la pregunta entra con animación
  render = RENDER[q.tipo](q, cont, () => { $("accion").disabled = render.obtener() == null; }, item);
  window.scrollTo({ top: 0 });
}

const tipoDe = () => cola[0]?.q?.tipo;
function feedback(ok, r, extra) {
  $("pie").className = "r-pie " + (ok ? "bien" : "mal");
  const m = $("mensaje"); m.replaceChildren();
  const codi = document.createElement("span");
  codi.className = "r-codi";
  codi.innerHTML = codiSVG(ok ? "celebra" : (vidas <= 1 ? "alarma" : "triste"), { tam: 72 });
  m.append(codi);
  m.append(el("h2", ok ? "✅ ¡Muy bien!" : tipoDe() === "parejas" ? "❌ Te equivocaste al unir más de lo permitido" : (r.correcta ? "❌ Casi. Respuesta correcta: " + r.correcta : "❌ Todavía no")));
  if (extra?.titulo) m.append(el("p", extra.titulo));
  (extra?.detalle || []).forEach((d) => m.append(el("p", (d.ok ? "✓ " : "✗ ") + d.texto, "det")));
  const tipoActual = cola[0]?.q?.tipo;
  if (r.explicacion && !(ok && tipoActual === "parejas")) { const ex = el("p", "", "r-porque"); ex.append(el("b", "Por qué: "), document.createTextNode(r.explicacion)); m.append(ex); }
  // «¿Por qué?»: Codi (la IA) explica con más detalle, también por qué tu respuesta no era la correcta
  const reto = cola[0]?.q;
  if (reto?.id) {
    const b = el("button", "🤖 ¿Por qué? Explícamelo mejor", "r-porque-btn");
    b.type = "button";
    b.onclick = async () => {
      b.disabled = true;
      const caja = el("div", "", "r-porque-ia");
      caja.innerHTML = `<span class="r-porque-codi">${codiSVG("pensando", { tam: 44 })}</span><span>Codi está pensando…</span>`;
      b.replaceWith(caja);
      try {
        const d = await api(`/api/reto/${reto.id}/porque/`, { respuesta: ultimaRespuesta });
        caja.innerHTML = `<span class="r-porque-codi">${codiSVG(ok ? "feliz" : "saludo", { tam: 44 })}</span>`;
        const t = el("p", "");
        t.innerHTML = String(d.texto || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/\n/g, "<br>");
        if (!d.ia) {   // sin IA en el servidor: se ofrece seguir la conversación con el tutor
          const preg = `Explícame por qué en este reto la respuesta correcta es «${r.correcta}»${ultimaRespuesta != null && !ok ? ` y no «${Array.isArray(ultimaRespuesta) ? ultimaRespuesta.join(" ") : ultimaRespuesta}»` : ""}: ${reto.enunciado}`;
          t.innerHTML = `<a href="/pages/ia.html?q=${encodeURIComponent(preg)}" target="_blank" rel="noopener">Pregúntale a Codi en el tutor de IA →</a>`;
        }
        caja.append(t);
      } catch (x) { caja.lastChild.textContent = x.message; }
    };
    m.append(b);
  }
}

let ultimaRespuesta = null;
async function comprobar() {
  const valor = render.obtener();
  if (valor == null) return;
  ultimaRespuesta = valor;
  $("accion").disabled = true;
  prepararAudio();
  try {
    let extra = null, cuerpo = { respuesta: valor };
    if (render.local) {
      $("accion").textContent = "Probando…";
      extra = await render.local(valor);
      if (extra.invalido) { feedback(false, {}, { titulo: extra.mensaje }); $("pie").className = "r-pie mal"; $("accion").textContent = "Comprobar"; $("accion").disabled = false; return; }
      cuerpo = { correcto: extra.ok };
    }
    const r = await api(`/api/reto/${cola[0].q.id}/responder/${examen ? "?salto=1" : ""}`, cuerpo);
    ultimoOk = r.correcto;
    if (examen) $("vidas").textContent = `✗ ${fallos + (r.correcto ? 0 : 1)}/${examen.tolerancia}`;
    else { vidas = r.vidas; $("vidas").textContent = vidas; }
    reproducirRespuesta(ultimoOk);
    animarRespuesta(ultimoOk);
    if (!r.correcto) fallos++;
    render.bloquear(); feedback(r.correcto, r, extra);
    $("accion").textContent = "Continuar"; $("accion").className = "bj" + (r.correcto ? "" : " rojo"); $("accion").disabled = false; fase = "feedback";
    $("mensaje").scrollTop = 0; $("accion").focus({ preventScroll: true }); $("pie").scrollIntoView({ block: "end", behavior: "smooth" });
  } catch (e) {
    if (/vidas/i.test(e.message)) { enCurso = false; $("sinVidas").hidden = false; }
    else { $("mensaje").textContent = e.message; $("accion").textContent = "Comprobar"; $("accion").disabled = false; }
  }
}

async function continuar() {
  if (examen) return continuarExamen();
  if (vidas <= 0) { enCurso = false; $("sinVidas").hidden = false; return; }
  const item = cola.shift();
  if (ultimoOk) { hechas++; progreso(true); } else cola.push(item);   // la pregunta fallada vuelve al final
  if (cola.length) return mostrar();
  progreso(false); $("pie").hidden = true;
  enCurso = false; history.back();   // quita la entrada extra del historial: ya no hay nada que perder
  try {
    const r = await api(`/api/nivel/${datos.nivel.id}/completar/`, { fallos });
    const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    sonar("leccion"); vibrar([30, 60, 30]);
    $("cuerpo").innerHTML = `<div class="fin"><div class="fin-codi">${codiSVG("celebra", { tam: 150 })}</div><div class="grande">${"⭐".repeat(r.estrellas)}</div><h1>¡Nivel completado!</h1>
      ${r.racha_hoy ? `<div class="racha-hoy" role="status"><div class="racha-fuego racha-codi" aria-hidden="true">${codiSVG("fuego", { tam: 76 })}</div><div class="racha-num"><b>${r.perfil.racha_actual}</b><span>${r.perfil.racha_actual === 1 ? "día de racha" : "días de racha"}</span></div><p>${r.perfil.racha_actual > (r.racha_antes || 0) ? "¡Hiciste la racha de hoy!" : "¡Empezaste una racha nueva!"}</p></div>` : ""}
      <div class="botin"><div>✨ +${r.xp_ganado} XP</div>${r.minerales_ganados.diamante ? `<div>💎 +${r.minerales_ganados.diamante} diamante</div>` : ""}
        <div>🔥 Racha: ${r.perfil.racha_actual}</div></div>
      ${r.desafios_completados.map((d) => `<div class="tarjeta" style="margin-bottom:12px">🎁 <b>${esc(d.encabezado || "¡Desafío superado!")}</b> ${esc(d.titulo)}<br><small>Premio: ${esc(d.premio)}</small></div>`).join("")}
      <a class="bj" href="/pages/inicio.html?curso=${datos.curso.slug}">Continuar</a></div>`;
    // Como en Duolingo: los cofres de lo que acabas de cumplir se abren aquí mismo.
    if (r.racha_hoy) { sonar("racha", 0.85); setTimeout(() => vibrar([20, 40, 60]), 850); }
    import("/js/cofres.js").then((m) => m.abrirPremiosNuevos(r.desafios_completados || [])).catch(() => {});
    try { navigator.serviceWorker?.controller?.postMessage("actualizar-widget"); } catch { /* sin service worker */ }
  } catch (e) { $("cuerpo").replaceChildren(el("p", e.message, "vacio")); }
}

/** Examen de salto: cada pregunta una vez; si pasas el máximo de errores, termina. */
async function continuarExamen() {
  cola.shift(); hechas++; progreso(true);
  const reprobado = fallos > examen.tolerancia;
  if (cola.length && !reprobado) return mostrar();
  progreso(false); $("pie").hidden = true;
  enCurso = false; history.back();
  const volver = `/pages/inicio.html?curso=${datos.curso.slug}`;
  try {
    const r = await api("/api/salto/terminar/", {});
    if (r.aprobado) {
      sonar("leccion"); vibrar([30, 60, 30]);
      $("cuerpo").innerHTML = `<div class="fin"><div class="fin-codi">${codiSVG("celebra", { tam: 150 })}</div><h1>¡Aprobaste el examen!</h1>
        <p>Saltaste a ${String(r.objetivo).replace(/[&<>]/g, "")}. Se marcaron ${r.desbloqueados} niveles anteriores como hechos.</p>
        <div class="botin"><div>✨ +${r.xp_ganado} XP</div><div>✗ ${r.errores} de ${r.tolerancia} errores permitidos</div></div>
        <a class="bj" href="${volver}">Seguir desde ahí</a></div>`;
      import("/js/cofres.js").then((m) => m.abrirPremiosNuevos(r.desafios_completados || [])).catch(() => {});
    } else {
      $("cuerpo").innerHTML = `<div class="fin"><div class="fin-codi">${codiSVG("triste", { tam: 150 })}</div><h1>Esta vez no</h1>
        <p>Tuviste ${r.errores} errores y el máximo era ${r.tolerancia}. Repasa las lecciones anteriores y vuelve a intentarlo cuando quieras: no perdiste vidas.</p>
        <a class="bj" href="${volver}">Volver al camino</a></div>`;
    }
  } catch (e) { $("cuerpo").replaceChildren(el("p", e.message, "vacio")); }
}

$("accion").onclick = () => (fase === "preguntar" ? comprobar() : continuar());
document.addEventListener("keydown", (e) => { if (e.key === "Enter" && e.target.tagName !== "TEXTAREA" && e.target.tagName !== "A" && e.target.tagName !== "BUTTON" && $("confirmarSalida").hidden && !$("accion").disabled && !$("pie").hidden) $("accion").click(); });
main();
