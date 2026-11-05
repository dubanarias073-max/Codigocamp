import { RUTAS, XP_TIPO } from "./content/retos.js";
import { correr } from "./retos-motor.js";
import { cargarProgreso, guardarProgreso, rachaActual, registrarActividad, nivelUsuario } from "./progreso.js";
import { iniciarPagina, mostrar } from "./layout.js";

const $ = (id) => document.getElementById(id);
function el(tag, text, cls) {
  const e = document.createElement(tag);
  if (text != null) e.textContent = text;
  if (cls) e.className = cls;
  return e;
}
const pre = (t) => { const p = el("pre", t, "codigo"); return p; };
const norm = (s) => String(s).toLowerCase().trim().replace(/\s+/g, " ");
function barajar(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

let userId = null, prog = null, J = null;
const DESV = [0, 34, 58, 34]; // zigzag del camino de niveles
const TIPOS = {
  opcion: "Elige la respuesta correcta", completar: "Completa", error: "Encuentra el error",
  ordenar: "Ordena los pasos", codigo: "Escribe código", caso: "Caza el bug · pruebas de software",
};

// ---------------- Mapa de rutas ----------------
function pintarMapa() {
  $("stRacha").textContent = rachaActual(prog);
  $("stXp").textContent = prog.xp;
  $("stNivel").textContent = nivelUsuario(prog.xp);
  $("barraNivel").style.width = prog.xp % 100 + "%";

  const cont = $("mapa");
  cont.replaceChildren();
  for (const ruta of RUTAS) {
    const sec = el("section", null, "ruta");
    sec.style.setProperty("--ruta", ruta.color);
    const cab = el("div", null, "ruta-cab");
    cab.append(el("span", ruta.emoji, "ruta-ico"));
    const txt = el("div");
    const titulo = el("h2", ruta.nombre);
    titulo.append(el("span", ruta.dificultad, "dif"));
    txt.append(titulo, el("p", ruta.desc, "note"));
    cab.append(txt);

    const camino = el("div", null, "camino");
    ruta.niveles.forEach((n, i) => {
      const hecho = prog.niveles[n.id];
      const libre = i === 0 || prog.niveles[ruta.niveles[i - 1].id];
      const b = el("button", null, "nodo " + (hecho ? "hecho" : libre ? "libre" : "bloq"));
      b.type = "button";
      b.disabled = !libre;
      b.style.marginLeft = DESV[i % DESV.length] + "px";
      const circ = el("span", hecho ? "✓" : libre ? String(i + 1) : "🔒", "nodo-c");
      const info = el("span", null, "nodo-i");
      info.append(el("span", n.titulo, "nodo-t"));
      const e = hecho ? hecho.estrellas : 0;
      info.append(el("span", "★".repeat(e) + "☆".repeat(3 - e), "estrellas"));
      b.append(circ, info);
      b.onclick = () => jugar(ruta, i);
      camino.append(b);
    });
    sec.append(cab, camino);
    cont.append(sec);
  }
}

// ---------------- Tipos de pregunta ----------------
// Cada render devuelve { obtener(), comprobar(resp), bloquear() }
const RENDER = {
  opcion(q, cont, cambio) {
    if (q.codigo) cont.append(pre(q.codigo));
    let sel = null;
    const lista = el("div", null, "opciones");
    const botones = q.op.map((t, i) => {
      const b = el("button", null, "opcion");
      b.type = "button";
      b.append(el("span", String(i + 1), "tecla"), el("span", t));
      b.onclick = () => { sel = i; botones.forEach((x, j) => x.classList.toggle("sel", j === i)); cambio(); };
      lista.append(b);
      return b;
    });
    cont.append(lista);
    return {
      obtener: () => sel,
      comprobar: async (s) => ({ ok: s === q.ok, correcta: q.op[q.ok] }),
      bloquear: () => botones.forEach((b) => { b.disabled = true; }),
    };
  },

  completar(q, cont, cambio) {
    if (q.codigo) cont.append(pre(q.codigo));
    const inp = el("input", null, "resp");
    inp.placeholder = "Escribe tu respuesta";
    inp.autocomplete = "off";
    inp.spellcheck = false;
    inp.oninput = cambio;
    inp.onkeydown = (e) => { if (e.key === "Enter") $("btnJ").click(); };
    cont.append(inp);
    setTimeout(() => inp.focus(), 0);
    return {
      obtener: () => (inp.value.trim() ? inp.value : null),
      comprobar: async (v) => ({ ok: q.resp.some((r) => norm(r) === norm(v)), correcta: q.resp[0] }),
      bloquear: () => { inp.disabled = true; },
    };
  },

  error(q, cont, cambio) {
    let sel = null;
    const caja = el("div", null, "lineas");
    const botones = q.codigo.split("\n").map((linea, i) => {
      const b = el("button", null, "linea");
      b.type = "button";
      b.append(el("span", String(i + 1), "ln"), el("code", linea || " "));
      b.onclick = () => { sel = i + 1; botones.forEach((x, j) => x.classList.toggle("sel", j === i)); cambio(); };
      caja.append(b);
      return b;
    });
    cont.append(caja);
    return {
      obtener: () => sel,
      comprobar: async (s) => ({ ok: s === q.ok, correcta: "la línea " + q.ok }),
      bloquear: () => botones.forEach((b) => { b.disabled = true; }),
    };
  },

  ordenar(q, cont, cambio) {
    const piezas = q.piezas.map((t, i) => ({ t, id: i }));
    let banco = barajar(piezas);
    for (let n = 0; n < 10 && banco.every((p, i) => p.id === i) && banco.length > 1; n++) banco = barajar(piezas);
    let resp = [];
    const zona = el("div", null, "zona-resp");
    const bancoEl = el("div", null, "banco");
    const chip = (p, fn) => { const b = el("button", p.t, "pieza"); b.type = "button"; b.onclick = fn; return b; };
    const pintar = () => {
      zona.replaceChildren(...resp.map((p) => chip(p, () => { resp = resp.filter((x) => x !== p); banco.push(p); pintar(); cambio(); })));
      bancoEl.replaceChildren(...banco.map((p) => chip(p, () => { banco = banco.filter((x) => x !== p); resp.push(p); pintar(); cambio(); })));
    };
    pintar();
    cont.append(el("p", "Toca las piezas en el orden correcto:", "note"), zona, bancoEl);
    return {
      obtener: () => (resp.length === q.piezas.length ? resp.map((p) => p.t) : null),
      comprobar: async (r) => ({ ok: r.every((t, i) => t === q.piezas[i]), correcta: q.piezas.join("  →  ") }),
      bloquear: () => { zona.classList.add("fija"); bancoEl.classList.add("fija"); zona.querySelectorAll("button").forEach((b) => { b.disabled = true; }); },
    };
  },

  codigo(q, cont, cambio, item) {
    const vis = q.casos.filter((c) => c.v !== false);
    const ej = el("div", null, "ejemplos");
    ej.append(el("p", "Ejemplos (hay además pruebas ocultas):", "note"));
    vis.forEach((c) => ej.append(el("code", `${q.fn}(${c.a.map((x) => JSON.stringify(x)).join(", ")})  →  ${JSON.stringify(c.r)}`)));
    const ta = el("textarea", null, "editor");
    ta.value = item.ultimo ?? q.plantilla;
    ta.spellcheck = false;
    ta.oninput = cambio;
    ta.onkeydown = (e) => { // Tab inserta dos espacios
      if (e.key === "Tab") { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText("  ", s, ta.selectionEnd, "end"); cambio(); }
    };
    cont.append(ej, ta);
    return {
      obtener: () => (ta.value.trim() ? ta.value : null),
      comprobar: async (codigo) => {
        item.ultimo = codigo;
        const r = await correr({ modo: "tests", codigo, fn: q.fn, casos: q.casos });
        if (r.error) return { invalido: true, mensaje: "No pude ejecutar tu código: " + r.error };
        const detalle = r.res.map((x, i) => x.v
          ? { ok: x.ok, texto: x.ok ? `${q.fn}(${x.entrada}) → ${x.got}` : `${q.fn}(${x.entrada}): esperaba ${x.esperado} y obtuve ${x.got}` }
          : { ok: x.ok, texto: x.ok ? "Prueba oculta superada" : "Prueba oculta fallida: piensa en los casos límite" });
        const pasadas = r.res.filter((x) => x.ok).length;
        return { ok: pasadas === r.res.length, titulo: pasadas === r.res.length ? "¡Todas las pruebas superadas!" : `Pruebas superadas: ${pasadas} de ${r.res.length}`, detalle };
      },
      bloquear: () => { ta.disabled = true; },
    };
  },

  caso(q, cont, cambio, item) {
    cont.append(pre(q.defectuosa), el("p", "Escribe los argumentos de entrada separados por comas. Los textos van entre comillas.", "note"));
    const inp = el("input", null, "resp");
    inp.placeholder = 'Ej.: 2024   o   "texto", 5';
    inp.autocomplete = "off";
    inp.spellcheck = false;
    inp.value = item.ultimo ?? "";
    inp.oninput = cambio;
    inp.onkeydown = (e) => { if (e.key === "Enter") $("btnJ").click(); };
    cont.append(inp);
    setTimeout(() => inp.focus(), 0);
    return {
      obtener: () => (inp.value.trim() ? inp.value : null),
      comprobar: async (txt) => {
        item.ultimo = txt;
        let args;
        try { args = JSON.parse("[" + txt + "]"); }
        catch { return { invalido: true, mensaje: 'No entendí los argumentos. Escríbelos como JSON, por ejemplo: 2024  o  "texto", 5' }; }
        const r = await correr({ modo: "caso", defectuosa: q.defectuosa, correcta: q.correcta, fn: q.fn, args });
        if (r.error) return { invalido: true, mensaje: "No pude ejecutar la prueba: " + r.error };
        return {
          ok: r.distinto,
          titulo: r.distinto ? "¡Bug encontrado!" : "Con esa entrada ambas versiones dan lo mismo",
          detalle: [{ ok: r.distinto, texto: `${q.fn}(${txt}) → defectuosa: ${r.defectuosa} · correcta: ${r.correcta}` }],
        };
      },
      bloquear: () => { inp.disabled = true; },
    };
  },
};

// ---------------- Partida ----------------
function jugar(ruta, i) {
  const nivel = ruta.niveles[i];
  J = {
    ruta, i, nivel, total: nivel.preguntas.length,
    cola: nivel.preguntas.map((q) => ({ q, fallada: false })),
    hechas: 0, vidas: 3, fallos: 0, xp: 0, actual: null,
  };
  $("juego").hidden = false;
  document.body.classList.add("jugando");
  pintarPregunta();
}

function cerrarJuego() {
  $("juego").hidden = true;
  document.body.classList.remove("jugando");
  J = null;
  pintarMapa();
}

function barra() {
  $("barraJ").style.width = (J.hechas / J.total) * 100 + "%";
  $("vidas").textContent = "❤️".repeat(J.vidas) + "🖤".repeat(3 - J.vidas);
}

function pintarPregunta() {
  const item = J.cola[0], q = item.q;
  barra();
  const cuerpo = $("cuerpoJ");
  cuerpo.replaceChildren(el("p", TIPOS[q.t], "tipo"), el("h2", q.q, "enun"));
  $("pieJ").hidden = false;
  $("pieJ").className = "pie";
  $("msgJ").replaceChildren();
  const btn = $("btnJ");
  btn.textContent = "Comprobar";
  btn.disabled = true;
  btn.onclick = comprobar;
  const cambio = () => { btn.disabled = J.actual.obtener() === null; };
  J.actual = RENDER[q.t](q, cuerpo, cambio, item);
}

function aviso(texto) {
  const m = $("msgJ");
  m.replaceChildren(el("p", texto, "aviso"));
}

async function comprobar() {
  const r = J.actual, item = J.cola[0], q = item.q;
  const resp = r.obtener();
  if (resp === null) return;
  const btn = $("btnJ");
  btn.disabled = true;
  btn.textContent = "Comprobando…";
  const res = await r.comprobar(resp);
  btn.textContent = "Comprobar";
  if (res.invalido) { aviso(res.mensaje); btn.disabled = false; return; }

  r.bloquear();
  if (res.ok) {
    J.hechas++;
    if (!item.fallada) J.xp += q.xp ?? XP_TIPO[q.t];
    J.cola.shift();
  } else {
    J.vidas--;
    J.fallos++;
    item.fallada = true;
    J.cola.push(J.cola.shift()); // se repite al final
  }
  barra();

  const msg = $("msgJ");
  msg.replaceChildren(el("h3", res.titulo ?? (res.ok ? "¡Correcto!" : "Incorrecto")));
  if (!res.ok && res.correcta) msg.append(el("p", "Respuesta correcta: " + res.correcta));
  if (res.detalle) {
    const ul = el("ul", null, "pruebas");
    res.detalle.forEach((d) => ul.append(el("li", (d.ok ? "✓ " : "✗ ") + d.texto, d.ok ? "bien" : "mal")));
    msg.append(ul);
  }
  msg.append(el("p", q.exp, "exp"));
  $("pieJ").className = "pie " + (res.ok ? "ok" : "mal");
  btn.textContent = "Continuar";
  btn.disabled = false;
  btn.onclick = continuar;
}

function continuar() {
  if (J.vidas === 0) return sinVidas();
  if (J.cola.length === 0) return terminar();
  pintarPregunta();
}

function pantalla(...nodos) {
  $("pieJ").hidden = true;
  $("cuerpoJ").replaceChildren(...nodos);
}

function sinVidas() {
  const { ruta, i } = J;
  const acc = el("div", null, "acciones");
  const reintentar = el("button", "Reintentar nivel", "btn pri lg");
  reintentar.type = "button";
  reintentar.onclick = () => jugar(ruta, i);
  const salir = el("button", "Salir", "btn ghost lg");
  salir.type = "button";
  salir.onclick = cerrarJuego;
  acc.append(reintentar, salir);
  pantalla(el("div", "💔", "gran"), el("h2", "Te quedaste sin vidas", "enun"), el("p", "No pasa nada: repasa el tema y vuelve a intentarlo.", "note"), acc);
}

function terminar() {
  const perfecto = J.fallos === 0;
  const estrellas = perfecto ? 3 : J.fallos <= 2 ? 2 : 1;
  const xpTotal = J.xp + 10 + (perfecto ? 20 : 0);
  const previo = prog.niveles[J.nivel.id];
  prog.niveles[J.nivel.id] = { estrellas: Math.max(previo?.estrellas ?? 0, estrellas) };
  prog.xp += xpTotal;
  registrarActividad(prog);
  guardarProgreso(userId, prog);
  barra();

  const precision = Math.round((J.total / (J.total + J.fallos)) * 100);
  const datos = el("div", null, "resumen");
  const dato = (valor, etiqueta) => { const d = el("div", null, "dato"); d.append(el("b", valor), el("span", etiqueta)); return d; };
  datos.append(dato("+" + xpTotal, "XP"), dato(precision + "%", "precisión"), dato("🔥 " + rachaActual(prog), "días de racha"));

  const acc = el("div", null, "acciones");
  const sigNivel = J.ruta.niveles[J.i + 1];
  const { ruta, i } = J;
  if (sigNivel) {
    const b = el("button", "Siguiente nivel", "btn pri lg");
    b.type = "button";
    b.onclick = () => jugar(ruta, i + 1);
    acc.append(b);
  }
  const volver = el("button", "Volver al mapa", sigNivel ? "btn ghost lg" : "btn pri lg");
  volver.type = "button";
  volver.onclick = cerrarJuego;
  acc.append(volver);

  pantalla(
    el("div", "★".repeat(estrellas) + "☆".repeat(3 - estrellas), "gran estrellas"),
    el("h2", "¡Nivel completado!", "enun"),
    el("p", `${J.ruta.nombre} · ${J.nivel.titulo}`, "note"),
    datos, acc
  );
}

// ---------------- Arranque ----------------
const sesion = await iniciarPagina();
if (sesion.ok) {
  userId = sesion.user?.id ?? null;
  prog = cargarProgreso(userId);
  $("salirJ").onclick = () => { if (confirm("¿Salir del nivel? Perderás el avance de esta partida.")) cerrarJuego(); };
  pintarMapa();
  mostrar();
}
