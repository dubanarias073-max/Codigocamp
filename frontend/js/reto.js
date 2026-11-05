// Lógica de reto.html
import { api, getUser } from "/js/auth.js";
import { correr } from "/js/retos-motor.js";
const $ = (id) => document.getElementById(id);
const el = (tag, texto, cls) => { const e = document.createElement(tag); if (texto != null) e.textContent = texto; if (cls) e.className = cls; return e; };
const TIPOS = { opcion: "Elige la respuesta correcta", completar: "Completa", error: "Encuentra el error", ordenar: "Ordena los pasos", codigo: "Escribe código", caso: "Caza el bug · pruebas de software" };

const user = await getUser();
if (!user) location.replace("/pages/login.html");
else {
  const t = user.tema === "claro" || user.tema === "oscuro" ? user.tema : "auto";
  document.documentElement.dataset.tema = t;
  try { localStorage.setItem("cc_tema", t); } catch {}
}

// cola: las preguntas falladas vuelven al final hasta acertarlas
let datos, cola = [], total = 0, hechas = 0, fallos = 0, vidas = 0, fase = "preguntar", render = null, ultimoOk = false, enCurso = false;

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

async function main() {
  try { datos = await api("/api/nivel/" + new URLSearchParams(location.search).get("nivel") + "/"); }
  catch (e) { $("cuerpo").innerHTML = ""; $("cuerpo").append(el("p", e.message, "vacio")); return; }
  vidas = datos.vidas; $("vidas").textContent = vidas;
  if (vidas <= 0) { enCurso = false; $("sinVidas").hidden = false; return; }
  cola = datos.retos.map((q) => ({ q, ultimo: null })); total = cola.length;
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
  const cont = $("cuerpo"); cont.replaceChildren(el("p", TIPOS[q.tipo], "r-tipo"), el("h1", q.enunciado));
  cont.classList.remove("entra"); void cont.offsetWidth; cont.classList.add("entra");   // la pregunta entra con animación
  render = RENDER[q.tipo](q, cont, () => { $("accion").disabled = render.obtener() == null; }, item);
}

function feedback(ok, r, extra) {
  $("pie").className = "r-pie " + (ok ? "bien" : "mal");
  const m = $("mensaje"); m.replaceChildren();
  m.append(el("h2", ok ? "✅ ¡Muy bien!" : (r.correcta ? "❌ Casi. Respuesta correcta: " + r.correcta : "❌ Todavía no")));
  if (extra?.titulo) m.append(el("p", extra.titulo));
  (extra?.detalle || []).forEach((d) => m.append(el("p", (d.ok ? "✓ " : "✗ ") + d.texto, "det")));
  if (r.explicacion) m.append(el("p", r.explicacion));
}

async function comprobar() {
  const valor = render.obtener();
  if (valor == null) return;
  $("accion").disabled = true;
  try {
    let extra = null, cuerpo = { respuesta: valor };
    if (render.local) {
      $("accion").textContent = "Probando…";
      extra = await render.local(valor);
      if (extra.invalido) { feedback(false, {}, { titulo: extra.mensaje }); $("pie").className = "r-pie mal"; $("accion").textContent = "Comprobar"; $("accion").disabled = false; return; }
      cuerpo = { correcto: extra.ok };
    }
    const r = await api(`/api/reto/${cola[0].q.id}/responder/`, cuerpo);
    vidas = r.vidas; $("vidas").textContent = vidas; ultimoOk = r.correcto;
    if (!r.correcto) fallos++;
    render.bloquear(); feedback(r.correcto, r, extra);
    $("accion").textContent = "Continuar"; $("accion").className = "bj" + (r.correcto ? "" : " rojo"); $("accion").disabled = false; fase = "feedback";
  } catch (e) {
    if (/vidas/i.test(e.message)) { enCurso = false; $("sinVidas").hidden = false; }
    else { $("mensaje").textContent = e.message; $("accion").textContent = "Comprobar"; $("accion").disabled = false; }
  }
}

async function continuar() {
  if (vidas <= 0) { enCurso = false; $("sinVidas").hidden = false; return; }
  const item = cola.shift();
  if (ultimoOk) { hechas++; progreso(true); } else cola.push(item);   // la pregunta fallada vuelve al final
  if (cola.length) return mostrar();
  progreso(false); $("pie").hidden = true;
  enCurso = false; history.back();   // quita la entrada extra del historial: ya no hay nada que perder
  try {
    const r = await api(`/api/nivel/${datos.nivel.id}/completar/`, { fallos });
    const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    $("cuerpo").innerHTML = `<div class="fin"><div class="grande">${"⭐".repeat(r.estrellas)}</div><h1>¡Nivel completado!</h1>
      <div class="botin"><div>✨ +${r.xp_ganado} XP</div>${r.minerales_ganados.diamante ? `<div>💎 +${r.minerales_ganados.diamante} diamante</div>` : ""}
        <div>🔥 Racha: ${r.perfil.racha_actual}</div></div>
      ${r.desafios_completados.map((d) => `<div class="tarjeta" style="margin-bottom:12px">🎁 <b>¡Desafío superado!</b> ${esc(d.titulo)}<br><small>Premio: ${esc(d.premio)}</small></div>`).join("")}
      <a class="bj" href="/pages/inicio.html?curso=${datos.curso.slug}">Continuar</a></div>`;
  } catch (e) { $("cuerpo").replaceChildren(el("p", e.message, "vacio")); }
}

$("accion").onclick = () => (fase === "preguntar" ? comprobar() : continuar());
document.addEventListener("keydown", (e) => { if (e.key === "Enter" && e.target.tagName !== "TEXTAREA" && e.target.tagName !== "A" && e.target.tagName !== "BUTTON" && $("confirmarSalida").hidden && !$("accion").disabled && !$("pie").hidden) $("accion").click(); });
main();
