const log = document.getElementById("log");
const st = document.getElementById("st");
const btn = document.getElementById("b");
const entrada = document.getElementById("q");
const KEY = "cc_chat"; // la conversación se conserva al cambiar de página
const MAX = 4000;      // límite de caracteres por mensaje (el servidor lo comprueba también)
const BIENVENIDA = "¡Hola! Soy tu tutor de programación. Pregúntame sobre cualquier lenguaje, HTML, CSS o bases de datos. Pega tu código si quieres que lo revise.";

let history = [];
let busy = false;

const guardar = () => { try { sessionStorage.setItem(KEY, JSON.stringify(history)); } catch { /* sin almacenamiento */ } };
function cargar() {
  try {
    const d = JSON.parse(sessionStorage.getItem(KEY));
    if (Array.isArray(d)) {
      const ok = d.filter((m) => m && ["user", "assistant"].includes(m.role) && typeof m.content === "string");
      if (ok.length && ok.at(-1).role === "user") ok.pop(); // se cortó a mitad de una respuesta
      return ok;
    }
  } catch { /* sin datos */ }
  return [];
}

function add(text, kind) {
  const d = document.createElement("div");
  d.className = "m " + kind;
  d.textContent = text; // textContent: evita inyección de HTML
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
  return d;
}

// El servidor admite como máximo 20 mensajes y debe empezar y terminar en "user"
function ventana() {
  const v = history.slice(-19);
  while (v.length && v[0].role !== "user") v.shift();
  return v;
}

const ajustarAltura = () => {
  if (entrada.tagName !== "TEXTAREA") return;
  entrada.style.height = "auto";
  entrada.style.height = Math.min(entrada.scrollHeight, 160) + "px";
};

export async function ask(text) {
  text = text.trim();
  if (busy || !text) return;
  if (text.length > MAX) { st.textContent = `Tu mensaje es demasiado largo (máximo ${MAX} caracteres).`; return; }
  busy = true;
  btn.disabled = true;
  st.textContent = "";
  add(text, "u");
  const el = add("Pensando…", "a");
  history.push({ role: "user", content: text });

  try {
    const res = await fetch("/api/tutor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: ventana() }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || "Error del servidor");
    }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let full = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      full += dec.decode(value, { stream: true });
      el.textContent = full;
      log.scrollTop = log.scrollHeight;
    }
    if (!full) throw new Error("Respuesta vacía");
    history.push({ role: "assistant", content: full });
  } catch (e) {
    el.textContent = "No pude responder ahora. " + e.message;
    history.pop();
  }
  guardar();
  busy = false;
  btn.disabled = false;
}

export function reiniciar() {
  history = [];
  guardar();
  log.replaceChildren();
  add(BIENVENIDA, "a");
  st.textContent = "";
}

export function initTutor({ sugerencias = ["¿Por dónde empiezo?", "Diferencia entre HTML y CSS", "Crea un plan de estudio de 30 días"] } = {}) {
  history = cargar();
  if (history.length) history.forEach((m) => add(m.content, m.role === "user" ? "u" : "a"));
  else add(BIENVENIDA, "a");

  const chips = document.getElementById("chips");
  if (chips) sugerencias.forEach((t) => {
    const c = document.createElement("button");
    c.className = "chip";
    c.type = "button";
    c.textContent = t;
    c.onclick = () => ask(t);
    chips.appendChild(c);
  });

  const form = document.getElementById("f");
  form.onsubmit = (e) => {
    e.preventDefault();
    const v = entrada.value;
    entrada.value = "";
    ajustarAltura();
    ask(v);
  };
  // Enter envía; Shift + Enter hace salto de línea (útil para pegar código)
  entrada.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); }
  });
  entrada.addEventListener("input", ajustarAltura);
}
