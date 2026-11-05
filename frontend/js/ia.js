// Lógica de ia.html
import { iniciar, api, aviso } from "/js/app.js";
const { user, prog } = await iniciar("ia");
const $ = (id) => document.getElementById(id);
const CLAVE = "cc_ia_" + (user?.id ?? "x");
const MAX = 3500;
let historial = [];
try { historial = JSON.parse(localStorage.getItem(CLAVE)) || []; } catch {}
const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(historial.slice(-20))); } catch {} };

/* ===== Mostrar respuestas con formato (sin HTML inseguro) ===== */
function enLinea(padre, texto) {
  texto.split(/(`[^`\n]+`|\*\*[^*\n]+\*\*)/).forEach((t) => {
    if (!t) return;
    if (t.length > 2 && t[0] === "`" && t.at(-1) === "`") { const c = document.createElement("code"); c.textContent = t.slice(1, -1); padre.append(c); }
    else if (t.length > 4 && t.startsWith("**") && t.endsWith("**")) { const b = document.createElement("strong"); b.textContent = t.slice(2, -2); padre.append(b); }
    else padre.append(document.createTextNode(t));
  });
}
function formato(destino, texto) {
  destino.replaceChildren();
  const partes = texto.split(/```/);
  partes.forEach((trozo, i) => {
    if (i % 2) {                                       // bloque de código
      const nl = trozo.indexOf("\n");
      const lang = nl > -1 && /^[\w+#.-]{0,15}$/.test(trozo.slice(0, nl).trim()) ? trozo.slice(0, nl).trim() : "";
      const codigo = (lang || nl === 0 ? trozo.slice(nl + 1) : trozo).replace(/\n$/, "");
      const caja = document.createElement("div"); caja.className = "bloque";
      const cab = document.createElement("div"); cab.className = "bloque-cab";
      const et = document.createElement("span"); et.textContent = lang || "código";
      const b = document.createElement("button"); b.type = "button"; b.className = "btn sm"; b.textContent = "Copiar";
      b.onclick = () => navigator.clipboard?.writeText(codigo).then(() => aviso("Código copiado")).catch(() => aviso("No se pudo copiar", true));
      cab.append(et, b);
      const pre = document.createElement("pre"); const c = document.createElement("code"); c.textContent = codigo; pre.append(c);
      caja.append(cab, pre); destino.append(caja);
      return;
    }
    let lista = null;
    trozo.split("\n").forEach((linea) => {
      const li = linea.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)$/);
      if (li) {
        if (!lista) { lista = document.createElement(/^\s*\d/.test(linea) ? "ol" : "ul"); destino.append(lista); }
        const e = document.createElement("li"); enLinea(e, li[1]); lista.append(e);
      } else {
        lista = null;
        if (!linea.trim()) return;
        const p = document.createElement("p"); enLinea(p, linea.replace(/^#+\s*/, "")); destino.append(p);
      }
    });
  });
}

function burbuja(rol, texto) {
  const d = document.createElement("div");
  d.className = "msg " + rol;
  if (rol === "tutor") formato(d, texto); else d.textContent = texto;
  $("log").appendChild(d); $("log").scrollTop = $("log").scrollHeight;
  return d;
}
function pintarHistorial() {
  $("log").replaceChildren();
  const nombre = (user?.nombre || "").split(" ")[0];
  burbuja("tutor", `¡Hola${nombre ? ", " + nombre : ""}! Soy tu tutor${prog.curso_actual ? " de " + prog.curso_actual.nombre : ""}. ¿Qué quieres aprender hoy?`);
  historial.forEach((m) => burbuja(m.rol, m.texto));
}
pintarHistorial();

/* ===== Sugerencias según el curso ===== */
const curso = prog.curso_actual?.nombre;
const SUG = [curso ? `Explícame lo más importante de ${curso}` : "Explícame qué es una variable", "Revisa mi código", "Dame un ejercicio fácil", "¿Qué error es este y cómo lo arreglo?"];
$("sug").innerHTML = SUG.map((s) => `<button type="button"></button>`).join("");
$("sug").querySelectorAll("button").forEach((b, i) => { b.textContent = SUG[i]; });
$("sug").onclick = (e) => { if (e.target.matches("button")) { $("q").value = e.target.textContent; actualizar(); $("q").focus(); } };

/* ===== Escribir y enviar ===== */
const actualizar = () => { $("cuenta").textContent = `${$("q").value.length} / ${MAX}`; };
$("q").oninput = actualizar;
$("codigo").onclick = () => { const q = $("q"); q.setRangeText("```\n\n```", q.selectionStart, q.selectionEnd, "end"); q.setSelectionRange(q.selectionEnd - 4, q.selectionEnd - 4); q.focus(); actualizar(); };
$("nueva").onclick = () => { if (!historial.length || confirm("¿Borrar esta conversación?")) { historial = []; guardar(); pintarHistorial(); } };
$("q").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("f").requestSubmit(); } };
$("f").onsubmit = async (e) => {
  e.preventDefault();
  const t = $("q").value.trim();
  if (!t || $("enviar").disabled) return;
  $("q").value = ""; actualizar();
  $("enviar").disabled = true;
  burbuja("yo", t);
  const espera = burbuja("tutor", "Pensando…");
  try {
    const r = await api("/api/tutor/", { mensaje: t, historial: historial.slice(-10) });
    formato(espera, r.respuesta);
    historial.push({ rol: "yo", texto: t }, { rol: "tutor", texto: r.respuesta });
    guardar();
  } catch (x) {
    espera.textContent = x.message; espera.classList.add("error");
    $("q").value = t; actualizar();                 // no pierdes lo que escribiste
  }
  $("enviar").disabled = false; $("log").scrollTop = $("log").scrollHeight; $("q").focus();
};
