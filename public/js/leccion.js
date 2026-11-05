import { CONCEPTOS, LENGUAJES } from "./content/lenguajes.js";
import { HTML } from "./content/html.js";
import { CSS } from "./content/css.js";
import { BD } from "./content/bd.js";
import { initLab, loadInLab, getCode, getModeLabel } from "./lab.js";
import { initTutor, ask } from "./tutor.js";
import { iniciarPagina, mostrar } from "./layout.js";

// Una misma plantilla sirve para las tres páginas de lecciones (según data-pagina del <body>)
const PAGINAS = {
  lenguajes: { lab: true, cursos: [{ etiqueta: "Lenguajes", lenguajes: true }] },
  htmlcss: { lab: true, cursos: [
    { etiqueta: "HTML", titulo: "HTML desde cero", lecciones: HTML },
    { etiqueta: "CSS", titulo: "CSS desde cero", lecciones: CSS },
  ] },
  bd: { lab: false, cursos: [{ etiqueta: "Bases de datos", titulo: "Bases de datos de todo tipo", lecciones: BD }] },
};
const cfg = PAGINAS[document.body.dataset.pagina];
let cur = 0, leng = 0, les = 0;

const $ = (id) => document.getElementById(id);
function el(tag, text, cls) {
  const e = document.createElement(tag);
  if (text != null) e.textContent = text;
  if (cls) e.className = cls;
  return e;
}
function boton(text, cls, onclick) {
  const b = el("button", text, cls);
  b.type = "button";
  b.onclick = onclick;
  return b;
}

// --- Panel derecho: laboratorio / tutor ---
function panel(cual, desplazar = false) {
  const lab = cual === "lab" && cfg.lab;
  $("paneLab").hidden = !lab;
  $("paneTutor").hidden = lab;
  $("tabLab").classList.toggle("on", lab);
  $("tabTutor").classList.toggle("on", !lab);
  if (desplazar && window.matchMedia("(max-width: 1099px)").matches)
    $("panel").scrollIntoView({ behavior: "smooth", block: "start" });
}
const preguntar = (texto) => { panel("tutor", true); ask(texto); };

function lecciones() {
  const c = cfg.cursos[cur];
  if (c.lenguajes) {
    const L = LENGUAJES[leng];
    return CONCEPTOS.map((k, i) => ({
      t: k.t, d: k.d, p: k.p, c: L.c[i],
      live: L.run === "js", modo: "js", lang: L.n,
      intro: L.d, extra: i === 0 ? "Cómo ejecutarlo: " + L.ej : null,
    }));
  }
  return c.lecciones.map((l) => ({ ...l, modo: "html", lang: c.etiqueta }));
}

function irA(nuevoCurso, nuevaLeng = leng, nuevaLec = 0) {
  cur = nuevoCurso; leng = nuevaLeng; les = nuevaLec;
  pintar();
}

function pintar() {
  const curso = cfg.cursos[cur];

  // Selector de curso (HTML | CSS)
  const sel = $("cursoSel");
  sel.hidden = cfg.cursos.length < 2;
  sel.replaceChildren();
  if (cfg.cursos.length > 1)
    cfg.cursos.forEach((c, i) => sel.appendChild(boton(c.etiqueta, i === cur ? "on" : "", () => irA(i, leng, 0))));

  // Selector de lenguaje
  $("langsWrap").hidden = !curso.lenguajes;
  $("langSel").value = String(leng);
  $("sideTitle").textContent = curso.lenguajes ? "Lecciones de " + LENGUAJES[leng].n : curso.titulo;

  const lista = lecciones();
  const steps = $("steps");
  steps.replaceChildren();
  lista.forEach((l, i) => {
    const b = boton("", "step" + (i === les ? " on" : ""), () => irA(cur, leng, i));
    b.append(el("span", String(i + 1), "num"), el("span", l.t));
    steps.appendChild(b);
  });
  const activo = steps.children[les];
  if (activo && steps.scrollWidth > steps.clientWidth)
    steps.scrollLeft = activo.offsetLeft - (steps.clientWidth - activo.offsetWidth) / 2;

  pintarLeccion(lista[les], lista.length);
}

function pintarLeccion(l, total) {
  const curso = cfg.cursos[cur];
  const ul = el("ul", null, "points");
  l.p.forEach((x) => ul.appendChild(el("li", x)));
  const pre = el("pre");
  pre.textContent = l.c;

  const acciones = el("div", null, "row");
  if (l.live && cfg.lab)
    acciones.appendChild(boton("▶ Probar en el laboratorio", "btn pri", () => { loadInLab(l.c, l.modo); panel("lab", true); }));
  acciones.appendChild(boton("Explícame este código", "btn soft",
    () => preguntar(`Explícame línea por línea este código de ${l.lang} (lección «${l.t}»):\n${l.c}`)));
  acciones.appendChild(boton("Ponme un ejercicio", "btn soft",
    () => preguntar(`Dame un ejercicio práctico sobre «${l.t}» (${l.lang}) para principiantes, sin la solución todavía.`)));

  const pager = el("div", null, "pager");
  const ant = boton("← Anterior", "btn soft", () => irA(cur, leng, les - 1));
  const sig = boton("Siguiente →", "btn pri", () => irA(cur, leng, les + 1));
  ant.disabled = les === 0;
  sig.disabled = les === total - 1;
  pager.append(ant, el("span", `Lección ${les + 1} de ${total}`, "note"), sig);

  const partes = [el("p", curso.etiqueta + (curso.lenguajes ? " · " + LENGUAJES[leng].n : ""), "crumb"), el("h2", l.t)];
  if (l.intro) partes.push(el("p", l.intro, "note"));
  partes.push(el("p", l.d), el("h3", "Lo esencial"), ul, el("h3", "Ejemplo"), pre);
  if (l.extra) partes.push(el("p", l.extra, "note"));
  partes.push(acciones, pager);
  $("lesson").replaceChildren(...partes);
}

// --- Arranque ---
if ((await iniciarPagina()).ok) {
  LENGUAJES.forEach((l, i) => {
    const o = el("option", l.n);
    o.value = String(i);
    $("langSel").appendChild(o);
  });
  $("langSel").onchange = (e) => irA(0, Number(e.target.value), les);

  if (cfg.lab) {
    $("tabLab").onclick = () => panel("lab");
    $("fix").onclick = () => preguntar(`Revisa mi código (${getModeLabel()}), dime si hay errores y cómo mejorarlo:\n${getCode()}`);
    initLab(HTML[0].c);
  } else {
    $("tabLab").hidden = true; // las bases de datos no se ejecutan en el navegador
  }
  $("tabTutor").onclick = () => panel("tutor");
  initTutor();

  if (location.hash === "#css") cur = 1; // html-css.html#css abre CSS directamente
  pintar();
  panel(cfg.lab ? "lab" : "tutor");
  mostrar();
}
