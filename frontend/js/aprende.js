// Lógica de aprende.html
import { iniciar, api, elegirCurso, aviso } from "/js/app.js";
import { logo } from "/js/logos.js";
import { LEE_ENTRADA } from "/js/trabajo/entradateclado.js";
const SERVIDOR = new Set(['java', 'c', 'cpp', 'csharp', 'php', 'go', 'rust', 'swift', 'kotlin', 'ruby', 'lua', 'r']);
const avisoEnLinea = new Set();

/* ===== Editor de VS Code (Monaco) en Aprende: colores, autocompletado y atajos. Si no carga, queda el editor simple. ===== */
const IDIOMA_MONACO = { html: 'html', css: 'css', javascript: 'javascript', python: 'python', sql: 'sql', bd: 'sql',
  typescript: 'typescript', java: 'java', c: 'c', cpp: 'cpp', csharp: 'csharp', php: 'php', go: 'go', rust: 'rust',
  swift: 'swift', kotlin: 'kotlin', ruby: 'ruby', terminal: 'shell', git: 'shell', docker: 'dockerfile', node: 'javascript',
  github: 'yaml', nosql: 'javascript', react: 'typescript', reactnative: 'typescript', lua: 'lua', r: 'r' };
let editorMonaco = null;

const { prog } = await iniciar("aprende");

/* Los cursos activos vienen de la API; esta tabla solo define el motor y los alias de archivos. */
const CONFIG = {
  html:       { k: "html", n: "HTML", c: "#f97316", run: "web" },
  css:        { k: "css", n: "CSS", c: "#2dd4bf", run: "web" },
  bd:         { k: "bd", n: "Bases de datos", c: "#f472b6", run: "ver" },
  javascript: { k: "js", n: "JavaScript", c: "#fbbf24", run: "js" },
  python:     { k: "py", n: "Python", c: "#60a5fa", run: "py" },
  sql:        { k: "sql", n: "SQL", c: "#f472b6", run: "sql" },
  typescript: { k: "ts", n: "TypeScript", c: "#38bdf8", run: "ts" },
  java:       { k: "java", n: "Java", c: "#fb923c", run: "srv" },
  c:          { k: "c", n: "C", c: "#94a3b8", run: "srv" },
  cpp:        { k: "cpp", n: "C++", c: "#818cf8", run: "srv" },
  csharp:     { k: "cs", n: "C#", c: "#a78bfa", run: "srv" },
  php:        { k: "php", n: "PHP", c: "#a5b4fc", run: "srv" },
  go:         { k: "go", n: "Go", c: "#22d3ee", run: "srv" },
  rust:       { k: "rs", n: "Rust", c: "#fdba74", run: "srv" },
  swift:      { k: "swift", n: "Swift", c: "#fb7185", run: "srv" },
  kotlin:     { k: "kt", n: "Kotlin", c: "#c084fc", run: "srv" },
  ruby:       { k: "rb", n: "Ruby", c: "#f87171", run: "srv" },
  terminal:   { k: "terminal", n: "Terminales", c: "#4ade80", run: "srv" },
  git:        { k: "git", n: "Git", c: "#f97316", run: "srv" },
  docker:     { k: "docker", n: "Docker", c: "#38bdf8", run: "srv" },
  node:       { k: "node", n: "Node.js", c: "#84cc16", run: "srv" },
  github:     { k: "github", n: "GitHub", c: "#a78bfa", run: "srv" },
  nosql:      { k: "nosql", n: "NoSQL", c: "#22c55e", run: "srv" },
  react:      { k: "react", n: "React", c: "#61dafb", run: "react" },
  reactnative: { k: "reactnative", n: "React Native", c: "#38bdf8", run: "rn" },
  lua:        { k: "lua", n: "Lua", c: "#818cf8", run: "srv" },
  r:          { k: "r", n: "R", c: "#60a5fa", run: "srv" },
};

const $ = (id) => document.getElementById(id);
const ed = $('ed'), out = $('out');
const TXT_INICIAL = 'Pulsa «Ejecutar» (o Ctrl + Enter) para ver el resultado.';
const ALIAS = { javascript: 'js', python: 'py', typescript: 'ts', csharp: 'cs', rust: 'rs', kotlin: 'kt', ruby: 'rb', htmlcss: 'html' };
let cursos = [];
try { cursos = (await api("/api/cursos/")).cursos || []; }
catch { aviso("No se pudo cargar el catálogo de cursos. Se mostrarán los cursos disponibles en esta versión.", true); }
if (!cursos.length) cursos = Object.entries(CONFIG).map(([slug, curso]) => ({ slug, nombre: curso.n, sigla: curso.k }));
const LEC = Object.create(null);
cursos.forEach((curso) => {
  if (!/^[a-z0-9_-]+$/.test(curso.slug || "")) return;
  const config = CONFIG[curso.slug] || {};
  const clave = config.k || curso.slug;
  const color = /^#[\da-f]{6}$/i.test(curso.color || "") ? curso.color : config.c || "#4ade80";
  LEC[clave] = { n: curso.nombre || config.n || curso.slug, i: curso.sigla || config.k || curso.slug.toUpperCase(),
    c: color, run: curso.motor || config.run || "srv", f: curso.slug, l: [] };   // motor: cursos creados en el panel
});
const hash = location.hash.slice(1);
// Sin #lenguaje en la dirección, se abre el curso que elegiste (el mismo que ves en Inicio).
const claveDe = (slug) => Object.keys(LEC).find((k) => LEC[k].f === slug);
const cursoInicial = Object.hasOwn(LEC, hash) ? hash : (ALIAS[hash] || claveDe(prog.curso_actual?.slug) || 'js');
let lang = LEC[cursoInicial] ? cursoInicial : Object.keys(LEC)[0];
let idx = 0;
let hechas = {};
let codigosEditados = {};
try { hechas = JSON.parse(localStorage.getItem('cc_hechas')) || {}; } catch {}
try { codigosEditados = JSON.parse(localStorage.getItem('cc_codigos_aprende')) || {}; } catch {}
const guardar = () => { try { localStorage.setItem('cc_hechas', JSON.stringify(hechas)); } catch {} };
const guardarCodigo = () => { try { localStorage.setItem('cc_codigos_aprende', JSON.stringify(codigosEditados)); } catch {} };
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ===== Selector de lenguajes (se dibuja siempre, aunque falle la carga) ===== */
function pintarLangs() {
  $('langs').innerHTML = Object.entries(LEC).map(([k, v]) =>
    `<button type="button" class="lg${k === lang ? ' on' : ''}" data-k="${k}" style="--c:${v.c}" aria-pressed="${k === lang}">${logo(v.f, 20)}${v.n}</button>`).join('');
  // En celular los lenguajes van en una tira: se centra el elegido (sin mover la página)
  const tira = $('langs'), on = tira.querySelector('.on');
  if (on && tira.scrollWidth > tira.clientWidth) tira.scrollLeft = on.offsetLeft - (tira.clientWidth - on.offsetWidth) / 2;
}

/** Primera lección que aún no has hecho (si ya hiciste todas, la última). */
function primeraPendiente(k) {
  const total = LEC[k].l.length, hs = new Set(hechas[k] || []);
  for (let i = 0; i < total; i++) if (!hs.has(i)) return i;
  return Math.max(0, total - 1);
}
/** Lo que hiciste en otro dispositivo (o antes de borrar los datos del navegador) también cuenta. */
async function traerHechas(k) {
  try {
    const { hechas: titulos = [] } = await api(`/api/progreso/lecciones/${encodeURIComponent(LEC[k].f)}/`);
    if (!titulos.length) return;
    const set = new Set(titulos);
    const mias = new Set(hechas[k] || []);
    LEC[k].l.forEach((y, i) => { if (set.has(y[0])) mias.add(i); });
    hechas[k] = [...mias].sort((a, b) => a - b);
    guardar();
  } catch { /* sin conexión: queda lo guardado en este navegador */ }
}

/** Aplica lo del panel: oculta originales, reemplaza por título y pone las nuevas en su posición (o al final). */
function mezclarLecciones(base, panel) {
  const ocultas = new Set(panel.filter((x) => x.oculta && x.reemplaza).map((x) => x.reemplaza));
  const reemplazos = new Map(panel.filter((x) => !x.oculta && x.reemplaza).map((x) => [x.reemplaza, x]));
  const lista = base.filter((o) => !ocultas.has(o.t)).map((o) => reemplazos.get(o.t) || o);
  for (const x of panel.filter((y) => !y.reemplaza && !y.oculta)) lista.splice(Math.min(x.posicion ?? lista.length, lista.length), 0, x);
  return lista;
}

async function abrir(k, i = null) {
  lang = k; idx = i ?? 0;
  pintarLangs();
  const C = LEC[k];
  $('rutaTit').textContent = 'Lecciones de ' + C.n;
  if (!C.l.length) {
    // Lecciones del código (lecciones/<curso>.js) + las del panel de administrador (nuevas, reemplazos y ocultas)
    const [base, panel] = await Promise.all([
      import('/js/lecciones/' + C.f + '.js').then((m) => m.default).catch(() => null),
      api(`/api/aprende/${encodeURIComponent(C.f)}/`).then((r) => r.lecciones || []).catch(() => []),
    ]);
    const lista = mezclarLecciones(base || [], panel);
    if (!lista.length) {
      $('pasos').innerHTML = '';
      $('teoria').textContent = base === null && !panel.length ? 'Todavía no hay lecciones de ' + C.n + '.' : 'No se pudieron cargar las lecciones de ' + C.n + '.';
      return;
    }
    C.l = lista.map((o) => [o.t, o.x, o.p || [], o.c, o.m, o.r, o.e, o.u, o.h, o.q, o.a, o.f]);
    if (C.run === 'srv' && !SAL) { try { SAL = (await import('/js/lecciones/salidas.js')).default; } catch { SAL = {}; } }
    if (lang !== k) return;            // el usuario cambió de lenguaje mientras cargaba
  }
  if (i === null) {
    await traerHechas(k);
    if (lang !== k) return;
    idx = primeraPendiente(k);          // se abre donde vas: la primera lección que te falta
  }
  pintar();
  if (i === null) document.querySelector('#pasos button.on')?.scrollIntoView({ block: 'nearest' });
}

function pintar() {
  const L = LEC[lang], x = L.l[idx], hs = hechas[lang] || [];
  const q = ($('buscar').value || '').trim().toLowerCase();

  // Agrupa las lecciones por módulo (respetando el filtro de búsqueda)
  const tot = {}, hec = {}, mods = [];
  L.l.forEach((y, i) => {
    tot[y[4]] = (tot[y[4]] || 0) + 1;
    if (hs.includes(i)) hec[y[4]] = (hec[y[4]] || 0) + 1;
  });
  L.l.forEach((y, i) => {
    if (q && !(y[0] + ' ' + y[4] + ' ' + y[1]).toLowerCase().includes(q)) return;
    let m = mods[mods.length - 1];
    if (!m || m.n !== y[4]) { m = { n: y[4], items: [] }; mods.push(m); }
    const ok = hs.includes(i);
    m.items.push(`<li><button type="button" data-i="${i}" class="${i === idx ? 'on' : ''}${ok ? ' ok' : ''}"${i === idx ? ' aria-current="true"' : ''}><span>${ok ? '✓' : i + 1}</span>${esc(y[0])}</button></li>`);
  });

  $('pasos').innerHTML = mods.length
    ? mods.map((m) =>
        `<details${q || m.n === x[4] ? ' open' : ''}><summary>${esc(m.n)} <small>${hec[m.n] || 0}/${tot[m.n]}</small></summary><ol class="pasos">${m.items.join('')}</ol></details>`).join('')
    : '<p class="vacio-b">Ninguna lección coincide.</p>';

  const pct = Math.round(hs.length / L.l.length * 100);
  $('progBar').style.width = pct + '%';
  $('prog').setAttribute('aria-valuenow', pct);
  $('progTxt').textContent = hs.length + ' de ' + L.l.length + ' lecciones hechas';

  const t = $('teoria');
  t.style.setProperty('--c', L.c);
  const leer = sinCodigo(L, x);
  $('lab').hidden = leer;
  t.innerHTML =
    `<span class="etq">${esc(L.n)} · ${esc(x[4])} · lección ${idx + 1} de ${L.l.length}</span>` +
    `<h1>${esc(x[0])}</h1>` +
    (x[7] ? '<h2>¿Qué es?</h2>' : '') + parrafos(x[1]) +
    (x[7] ? '<h2>¿Para qué sirve?</h2>' + parrafos(x[7]) : '') +
    `<h2>Puntos clave</h2><ul>${x[2].map((p) => `<li>${esc(p)}</li>`).join('')}</ul>` +
    (leer
      ? `<h2>${L.run === 'ver' ? 'Mira el ejemplo' : 'Para recordar'}</h2>${x[8] ? `<p>${esc(x[8])}</p>` : ''}<div class="cod-ver"><button type="button" class="btn soft sm cod-copiar">Copiar</button><pre><code>${esc(x[3])}</code></pre></div>`
      : x[8] ? `<h2>Mira el código</h2><p>${esc(x[8])} Los comentarios del código te explican cada parte.</p>` : '') +
    (x[11] && x[2].length >= 2 ? quizError(x) : x[6] ? `<div class="nota-e"><b>⚠️ Error común</b><p>${esc(x[6])}</p></div>` : '') +
    (x[9] && x[10] ? retoVivo(x, L, leer) : x[5] ? `<div class="nota-r"><b>🎯 Ahora tú</b><p>${esc(x[5])}</p></div>` : '') +
    `<a class="practicar" href="/pages/inicio.html?curso=${encodeURIComponent(L.f)}">Practicar ${esc(L.n)} con retos →</a>`;

  const claveCodigo = lang + ':' + idx;
  ed.value = typeof codigosEditados[claveCodigo] === 'string' ? codigosEditados[claveCodigo] : x[3];
  $('entrada').value = '';
  mostrarEntrada();
  out.className = ''; out.textContent = TXT_INICIAL;
  $('modo').textContent = L.run === 'srv' ? 'Muestra el resultado esperado'
    : L.run === 'web' ? 'Se ve al instante'
    : L.run === 'ver' ? 'Ejemplos para copiar'
    : L.run === 'react' ? 'Se ve al instante (React 19)'
    : L.run === 'rn' ? 'Se ve en un celular simulado'
    : 'Se ejecuta en tu navegador';
  $('vista').hidden = true; $('vista').removeAttribute('srcdoc'); out.hidden = false;
  $('prev').disabled = idx === 0;
  $('next').textContent = idx === L.l.length - 1 ? 'Marcar como hecha y terminar' : 'Marcar como hecha y seguir';
  history.replaceState(null, '', '#' + lang);
  // Entrada animada de la lección (cada parte aparece un poco después de la anterior)
  t.classList.remove('entra'); void t.offsetWidth; t.classList.add('entra');
  [...t.children].forEach((h, n) => h.style.setProperty('--n', Math.min(n, 14)));
  activarInteractivos(t, x);
}

/* ===== Lección interactiva: «¿Cuál es el error común?» y el reto para completar ===== */
// Orden estable por lección (no cambia al volver a pintar), distinto entre lecciones
const barajar = (lista, semilla) => lista.map((v, i) => [((semilla + 1) * 2654435761 + i * 40503) % 1000, v]).sort((a, b) => a[0] - b[0]).map((p) => p[1]);
const normal = (s) => String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[\s"'`();]/g, '').replace(/\(\)$/, '');
const sonarA = (n) => import('/js/sonidos.js').then((m) => m.sonar(n)).catch(() => {});
const codi = (animo, frase) => import('/js/mascota.js').then((m) => m.codiReacciona(animo, frase, 2600)).catch(() => {});

function quizError(x) {
  const ops = barajar([[x[11], 1], [x[2][0], 0], [x[2][1], 0]], idx + lang.length);
  return `<div class="quiz-e" data-quiz><b>🕵️ ¿Detectas el error común?</b><p class="quiz-sub">Dos frases son ciertas. Toca la que es un <em>error</em> que comete mucha gente.</p>` +
    `<div class="quiz-ops">${ops.map(([t, ok]) => `<button type="button" class="quiz-op" data-ok="${ok}">${esc(t)}</button>`).join('')}</div>` +
    `<div class="nota-e quiz-expl" hidden><b>⚠️ Error común</b><p>${esc(x[6])}</p></div></div>`;
}

/** Lecciones donde no hay nada que ejecutar: cursos «para leer» (Bases de datos) o ejemplos que son solo comentarios. */
function sinCodigo(L, x) {
  if (L.run === 'ver') return true;
  return String(x[3] || '').split('\n').every((s) => !s.trim() || /^\s*(#|\/\/|--|<!--|\/\*|\*)/.test(s));
}

function retoVivo(x, L, leer = false) {
  const partes = String(x[9]).split('___');
  const pista = esc(partes.slice(1).join('___'));
  const ancho = Math.max(4, Math.min(18, String(x[10]).length + 1));
  const intro = /^(Cambia el código|Reto mental)/.test(x[5] || '') ? (leer ? 'Piénsalo y completa:' : 'Cambia el código de abajo y mira qué pasa. Luego completa:') : esc(x[5]);
  return `<form class="nota-r reto-vivo" data-reto autocomplete="off"><b>🎯 Ahora tú</b><p>${intro}</p>` +
    `<p class="reto-frase">${esc(partes[0])}${partes.length > 1 ? `<input class="reto-in" aria-label="Tu respuesta" style="--ch:${ancho}ch" spellcheck="false" autocapitalize="off">${pista}` : `</p><p><input class="reto-in" aria-label="Tu respuesta" style="--ch:${ancho}ch" spellcheck="false" autocapitalize="off">`}</p>` +
    `<div class="reto-acc"><button class="btn pri sm" type="submit">Comprobar</button><button class="btn ghost sm reto-pista" type="button" hidden>💡 Pista</button><span class="reto-res" aria-live="polite"></span></div></form>`;
}

function activarInteractivos(t, x) {
  const copiar = t.querySelector('.cod-copiar');
  if (copiar) copiar.onclick = async () => {
    try { await navigator.clipboard.writeText(x[3]); copiar.textContent = '¡Copiado! ✔'; sonarA('clic'); }
    catch { copiar.textContent = 'No se pudo copiar'; }
    setTimeout(() => { copiar.textContent = 'Copiar'; }, 1600);
  };
  const quiz = t.querySelector('[data-quiz]');
  if (quiz) quiz.onclick = (e) => {
    const b = e.target.closest('.quiz-op'); if (!b || quiz.classList.contains('resuelto')) return;
    if (b.dataset.ok === '1') {
      b.classList.add('bien'); quiz.classList.add('resuelto'); sonarA('correcto');
      quiz.querySelectorAll('.quiz-op').forEach((o) => { o.disabled = true; });
      quiz.querySelector('.quiz-expl').hidden = false;
      codi('asombro', '¡Ojo de detective! 🕵️');
    } else {
      b.classList.add('mal'); b.disabled = true; sonarA('incorrecto');
      b.title = 'Esta frase es cierta';
    }
  };
  const f = t.querySelector('[data-reto]'); if (!f) return;
  const inp = f.querySelector('.reto-in'), res = f.querySelector('.reto-res'), btnP = f.querySelector('.reto-pista');
  const resp = String(x[10]); let fallos = 0, pistas = 0;
  inp.oninput = () => { inp.classList.remove('mal'); res.textContent = ''; };
  btnP.onclick = () => {
    pistas++;
    if (pistas >= 3 || pistas >= resp.length) { inp.value = resp; res.textContent = 'Esta era la respuesta. ¡La próxima sale sola!'; btnP.hidden = true; return; }
    inp.value = resp.slice(0, pistas); inp.focus();
    res.textContent = `Empieza por «${resp.slice(0, pistas)}»…`;
  };
  f.onsubmit = (e) => {
    e.preventDefault();
    if (!inp.value.trim()) { inp.focus(); return; }
    if (normal(inp.value) === normal(resp)) {
      f.classList.add('resuelto'); inp.classList.add('bien'); inp.readOnly = true; btnP.hidden = true;
      f.querySelector('[type=submit]').disabled = true;
      res.textContent = pistas ? '¡Bien! ✔' : ['¡Exacto! ✔', '¡Perfecto! ✔', '¡Lo tienes! ✔'][idx % 3];
      sonarA('correcto'); codi(pistas ? 'feliz' : 'baila', pistas ? '¡Bien hecho!' : '¡A la primera! 🎉');
      if (!pistas) import('/js/cofres.js').then((m) => m.confeti?.(28)).catch(() => {});
      $('next').classList.add('late');
    } else {
      fallos++; sonarA('incorrecto');
      inp.classList.remove('mal'); void inp.offsetWidth; inp.classList.add('mal');
      res.textContent = fallos === 1 ? 'Casi… vuelve a leer el ejemplo.' : 'Todavía no. Puedes pedir una pista.';
      if (fallos >= 2) btnP.hidden = false;
    }
  };
}

/* ===== Eventos ===== */
$('langs').onclick = async (e) => {
  const b = e.target.closest('[data-k]'); if (!b) return;
  try { await elegirCurso(LEC[b.dataset.k].f); } catch {}   // queda guardado como tu curso actual
  abrir(b.dataset.k);
};
$('buscar').oninput = () => { if (LEC[lang].l.length) pintar(); };
$('pasos').onclick = (e) => { const b = e.target.closest('[data-i]'); if (b) { idx = +b.dataset.i; pintar(); } };
$('prev').onclick = () => { if (idx > 0) { idx--; pintar(); } };
$('next').onclick = () => {
  (hechas[lang] ||= []);
  if (!hechas[lang].includes(idx)) hechas[lang].push(idx);
  guardar();
  import('/js/sonidos.js').then((m) => m.sonar('premio')).catch(() => {});
  api('/api/progreso/leccion/', { curso: LEC[lang].f, leccion: LEC[lang].l[idx][0] })
    .then((r) => import('/js/cofres.js').then((m) => m.abrirPremiosNuevos(r?.desafios_completados || [])))
    .catch(() => {});
  // Sigue con la siguiente que te falte (si la siguiente ya la habías hecho, se la salta)
  const total = LEC[lang].l.length, hs = new Set(hechas[lang]);
  let sig = idx + 1;
  while (sig < total && hs.has(sig)) sig++;
  if (sig >= total) sig = primeraPendiente(lang);
  const modulo = LEC[lang].l[idx][4];
  const delModulo = LEC[lang].l.map((y, i) => [y[4], i]).filter(([m]) => m === modulo);
  if (hs.size >= total) { sig = idx; aviso(`¡Terminaste todas las lecciones de ${LEC[lang].n}! 🎉`); import('/js/cofres.js').then((m) => m.confeti?.(90)).catch(() => {}); codi('baila', '¡Curso completo! 🏆'); }
  else if (delModulo.every(([, i]) => hs.has(i))) { aviso(`¡Módulo «${modulo}» completo! ✨`); import('/js/cofres.js').then((m) => m.confeti?.(50)).catch(() => {}); codi('asombro', '¡Módulo terminado!'); }
  else codi('feliz', ['¡Una más! 💪', '¡Vas muy bien!', '¡Sigue así!', '¡Bien hecho!'][hs.size % 4]);
  $('next').classList.remove('late');
  idx = sig;
  pintar();
  scrollTo({ top: 0, behavior: 'smooth' });
};
$('reset').onclick = () => {
  delete codigosEditados[lang + ':' + idx];
  guardarCodigo();
  ed.value = LEC[lang].l[idx][3];
  out.textContent = TXT_INICIAL;
  out.className = '';
};
ed.addEventListener('input', () => {
  codigosEditados[lang + ':' + idx] = ed.value;
  guardarCodigo();
  mostrarEntrada();
});
ed.onkeydown = (e) => {
  if (e.key === 'Tab') { e.preventDefault(); const s = ed.selectionStart; ed.setRangeText('  ', s, ed.selectionEnd, 'end'); }
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); ejecutar(); }
};
$('run').onclick = ejecutar;
// Alt + ← / → para moverte entre lecciones
addEventListener('keydown', (e) => {
  if (!e.altKey || e.ctrlKey || e.metaKey) return;
  if (e.key === 'ArrowRight' && LEC[lang].l.length && idx < LEC[lang].l.length - 1) { e.preventDefault(); idx++; pintar(); }
  if (e.key === 'ArrowLeft' && idx > 0) { e.preventDefault(); idx--; pintar(); }
});

/* ===== Ejecutores ===== */
const cargar = (u) => new Promise((ok, ko) => {
  const s = document.createElement('script'); s.src = u; s.onload = ok;
  s.onerror = () => ko(new Error('No se pudo descargar el motor. Revisa tu conexión.'));
  document.head.appendChild(s);
});
let pyo, SQL, SAL;
const parrafos = (t) => String(t).split('\n\n').map((p) => `<p>${esc(p)}</p>`).join('');
const correrJS = (code) => RUN._js(code);
const RUN = {
  // Bases de datos distintas de SQL: ejemplos para leer y copiar en tu propia herramienta
  ver: async () => ['Estos son ejemplos para leer y copiar. Pruébalos en tu propia herramienta (MySQL, MongoDB, Redis…).', 0],

  // HTML y CSS: se ven en un recuadro aislado
  web: async (code) => { const v = $('vista'); v.srcdoc = code; v.hidden = false; out.hidden = true; return ['', 0]; },

  // React: JSX/TSX se transpila en el navegador y se dibuja en un recuadro aislado (librerías desde esm.sh)
  async react(code) {
    const { transpilarModulo } = await import('/js/trabajo/ejecucion.js');
    const js = await transpilarModulo(prepararReact(code), 'App.tsx');
    const v = $('vista'); v.srcdoc = paginaReact(js); v.hidden = false; out.hidden = true;
    return ['', 0];
  },

  // React Native: se dibuja en un celular simulado (react-native-web + Expo y React Navigation simulados)
  async rn(code) {
    const { prepararRN, paginaRN, MENSAJE_FRAGMENTO } = await import('/js/aprende-rn.js');
    const listo = prepararRN(code);
    if (!listo) return [MENSAJE_FRAGMENTO, 0];
    const { transpilarModulo } = await import('/js/trabajo/ejecucion.js');
    const js = await transpilarModulo(listo, 'App.tsx');
    const v = $('vista'); v.srcdoc = await paginaRN(js); v.hidden = false; out.hidden = true;
    return ['', 0];
  },

  // JavaScript: en un iframe aislado, sin acceso a la página
  js: (code) => correrJS(code),

  // TypeScript: se compila en el navegador y luego corre como JavaScript
  async ts(code) {
    if (!window.ts) await cargar('https://cdnjs.cloudflare.com/ajax/libs/typescript/5.4.5/typescript.min.js');
    const r = window.ts.transpileModule(code, { reportDiagnostics: true, compilerOptions: { target: 'ES2020', module: 'None' } });
    const errs = (r.diagnostics || []).filter((d) => d.category === 1);
    if (errs.length) return [errs.map((d) => window.ts.flattenDiagnosticMessageText(d.messageText, '\n')).join('\n'), 1];
    return correrJS(r.outputText);
  },

  _js: (code) => new Promise((ok) => {
    const f = document.createElement('iframe'); f.sandbox = 'allow-scripts'; f.hidden = true;
    const fin = (t, e) => { removeEventListener('message', rec); clearTimeout(tm); f.remove(); ok([t, e]); };
    const rec = (ev) => { if (ev.source === f.contentWindow && ev.data?.cc) fin(ev.data.t, ev.data.e); };
    const tm = setTimeout(() => fin('Tiempo agotado: ¿hay un bucle infinito?', 1), 4000);
    addEventListener('message', rec);
    f.srcdoc = '<script>const L=[];let E=0;const fmt=(a)=>a.map(x=>typeof x==="object"?JSON.stringify(x):String(x)).join(" ");' +
      'console.log=(...a)=>L.push(fmt(a));console.error=console.log;' +
      'try{new Function(' + JSON.stringify(code).replace(/</g, '\\u003c') + ')()}catch(e){L.push("Error: "+e.message);E=1}' +
      'setTimeout(()=>parent.postMessage({cc:1,t:L.join("\\n"),e:E},"*"),300)<\/script>';
    document.body.appendChild(f);
  }),

  // Python: Pyodide (se descarga la primera vez)
  async py(code) {
    if (!pyo) { await cargar('https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js'); pyo = await loadPyodide(); }
    let t = '', e = 0;
    pyo.setStdout({ batched: (s) => (t += s + '\n') });
    pyo.setStderr({ batched: (s) => (t += s + '\n') });
    try { await pyo.runPythonAsync(code); }
    catch (x) { t += String(x.message).trim().split('\n').slice(-3).join('\n'); e = 1; }
    return [t, e];
  },

  // SQL: SQLite en el navegador con una tabla de práctica
  async sql(code) {
    if (!SQL) {
      await cargar('https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.js');
      SQL = await initSqlJs({ locateFile: (f) => 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/' + f });
    }
    const db = new SQL.Database();
    db.run("CREATE TABLE alumnos(id INTEGER PRIMARY KEY,nombre TEXT,curso TEXT,nota REAL);INSERT INTO alumnos VALUES(1,'Ana','HTML',9.1),(2,'Luis','Python',6.4),(3,'Marta','SQL',8.2),(4,'Pablo','Python',7.5),(5,'Sara','HTML',5.8);"
      + "CREATE TABLE instructores(id INTEGER PRIMARY KEY,nombre TEXT);INSERT INTO instructores VALUES(1,'Carla'),(2,'Diego');"
      + "CREATE TABLE cursos(id INTEGER PRIMARY KEY,titulo TEXT,instructor_id INTEGER);INSERT INTO cursos VALUES(1,'HTML',1),(2,'Python',2),(3,'SQL',1),(4,'Rust',2);"
      + "CREATE TABLE alumnos2(id INTEGER PRIMARY KEY,nombre TEXT,curso_id INTEGER);INSERT INTO alumnos2 VALUES(1,'Ana',1),(2,'Luis',2),(3,'Marta',3),(4,'Pablo',2),(5,'Sara',NULL);"
      + "CREATE TABLE tallas(talla TEXT);INSERT INTO tallas VALUES('S'),('M'),('L');CREATE TABLE colores(color TEXT);INSERT INTO colores VALUES('rojo'),('azul');"
      + "CREATE TABLE empleados(id INTEGER PRIMARY KEY,nombre TEXT,jefe_id INTEGER);INSERT INTO empleados VALUES(1,'Rosa',NULL),(2,'Iván',1),(3,'Noé',1);");
    try {
      const rs = db.exec(code);
      if (!rs.length) return ['Consulta ejecutada. No devolvió filas.', 0];
      return [rs.map((r) => [r.columns.join(' | '), ...r.values.map((v) => v.join(' | '))].join('\n')).join('\n\n'), 0];
    } catch (x) { return [x.message, 1]; }
    finally { db.close(); }
  },

  // Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin y Ruby: si el código es el de la lección se muestra
  // su resultado esperado; si lo cambiaste, se intenta ejecutar en el servidor (si tiene el lenguaje instalado).
  async srv(code, k) {
    const L = LEC[k];
    const sal = SAL?.[L.f]?.[idx];
    const entrada = $('entradaCaja').hidden ? '' : $('entrada').value;
    if (sal != null && code.trim() === L.l[idx][3].trim() && !entrada) return [sal, 0];
    if (!SERVIDOR.has(L.f)) return ['Estos ejemplos se practican en Trabajo → Terminal (o en tu propio equipo). Pulsa «Restablecer» para ver el resultado esperado de la lección.', 0];
    try {
      const d = await api('/api/run', { lenguaje: L.f, codigo: code, entrada });
      let texto = d.salida || '';
      if (d.donde === 'en_linea' && !avisoEnLinea.has(L.f)) { avisoEnLinea.add(L.f); texto += '\n\n(Compilado en línea porque el servidor no tiene ' + L.n + ' instalado. No pongas contraseñas en el código.)'; }
      return [texto, !!d.error];
    } catch (x) { throw new Error(x.message); }
  }
};


function mostrarEntrada() {
  const L = LEC[lang];
  const caja = $('entradaCaja');
  if (!L || L.run !== 'srv' || !SERVIDOR.has(L.f)) { caja.hidden = true; return; }
  const lee = LEE_ENTRADA[L.f]?.test(ed.value);
  caja.hidden = !lee;
  if (lee && !$('entrada').value) caja.open = true;
}
async function mejorarEditor() {
  try {
    const M = await import('/js/trabajo/monaco.js');
    const monaco = await M.cargarMonaco({ limite: 15000 });
    try {
      for (const d of [monaco.languages.typescript.typescriptDefaults, monaco.languages.typescript.javascriptDefaults]) {
        d.setDiagnosticsOptions({ noSemanticValidation: true, noSyntaxValidation: false });
      }
    } catch { /* sin servicio de TypeScript */ }
    const t = document.documentElement.dataset.tema;
    const oscuro = t === 'oscuro' || (t !== 'claro' && matchMedia('(prefers-color-scheme: dark)').matches);
    const caja = $('edMonaco');
    caja.hidden = false;
    const editor = monaco.editor.create(caja, {
      value: ed.value, language: IDIOMA_MONACO[lang] || 'plaintext', theme: oscuro ? 'codigocamp-oscuro' : 'codigocamp-claro',
      automaticLayout: true, minimap: { enabled: false }, fontSize: 14, lineNumbers: 'on', scrollBeyondLastLine: false,
      wordWrap: 'on', tabSize: 4, renderLineHighlight: 'line', bracketPairColorization: { enabled: true },
      quickSuggestions: true, padding: { top: 10, bottom: 10 }, scrollbar: { alwaysConsumeMouseWheel: false },
    });
    const valor = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value');
    let desdeMonaco = false;
    Object.defineProperty(ed, 'value', {
      configurable: true,
      get() { return valor.get.call(ed); },
      set(v) {
        valor.set.call(ed, v);
        if (desdeMonaco) return;
        monaco.editor.setModelLanguage(editor.getModel(), IDIOMA_MONACO[lang] || 'plaintext');
        if (editor.getValue() !== v) editor.setValue(v);
        mostrarEntrada();
      },
    });
    editor.onDidChangeModelContent(() => {
      desdeMonaco = true; ed.value = editor.getValue(); desdeMonaco = false;
      ed.dispatchEvent(new Event('input'));
    });
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => ejecutar());
    const alto = () => { caja.style.height = Math.min(560, Math.max(220, editor.getContentHeight() + 4)) + 'px'; editor.layout(); };
    editor.onDidContentSizeChange(alto); alto();
    ed.hidden = true;
    editorMonaco = editor;
  } catch { $('edMonaco').hidden = true; ed.hidden = false; }
}

/* ===== React en Aprende ===== */
const RV = '19.1.0';
const EXT = '?external=react,react-dom';
const MAPA_REACT = {
  'react': `https://esm.sh/react@${RV}`,
  'react/': `https://esm.sh/react@${RV}/`,
  'react-dom': `https://esm.sh/react-dom@${RV}?external=react`,
  'react-dom/client': `https://esm.sh/react-dom@${RV}/client?external=react`,
  'react-router-dom': `https://esm.sh/react-router-dom@7.6.0${EXT},react-router`,
  'react-router': `https://esm.sh/react-router@7.6.0${EXT}`,
  'zustand': `https://esm.sh/zustand@5.0.5?external=react`,
  '@tanstack/react-query': `https://esm.sh/@tanstack/react-query@5.80.0?external=react`,
  'react-hook-form': `https://esm.sh/react-hook-form@7.57.0?external=react`,
  'react-error-boundary': `https://esm.sh/react-error-boundary@6.0.0?external=react`,
  'axios': 'https://esm.sh/axios@1.9.0',
};

/** Ajusta el código de la lección para el recuadro: rutas en memoria y dibujo automático de <App />. */
export function prepararReact(code) {
  // En el recuadro no hay barra de direcciones: BrowserRouter se cambia por MemoryRouter (mismas rutas y enlaces)
  let c = code.replace(/import\s*\{([^}]*)\}\s*from\s*(["'])react-router(-dom)?\2/g, (todo, nombres) =>
    todo.replace(nombres, nombres.replace(/\bBrowserRouter\b(?!\s+as)/, 'MemoryRouter as BrowserRouter')));
  const dibuja = /createRoot\s*\(|ReactDOM\.render\s*\(|hydrateRoot\s*\(/.test(c);
  if (!dibuja) {
    if (!/\b(function|const|let|class)\s+App\b/.test(c)) throw new Error('Define un componente llamado App para verlo (por ejemplo: function App() { return <h1>Hola</h1>; }).');
    c += '\nimport { createRoot as __ccRaiz } from "react-dom/client";\n__ccRaiz(document.getElementById("root"), { onCaughtError: (e) => console.log("ℹ️ Un Error Boundary atrapó: " + (e?.message ?? e)) }).render(<App />);\n';
  }
  return c;
}

function paginaReact(js) {
  const mapa = JSON.stringify({ imports: MAPA_REACT });
  const consola = `<script>(()=>{const caja=()=>document.getElementById("cc-consola");const fmt=a=>a.map(x=>{if(x instanceof Error)return x.message;try{return typeof x==="object"?JSON.stringify(x):String(x)}catch{return String(x)}}).join(" ");` +
    `try{localStorage.length}catch{const m=new Map();const ls={getItem:k=>m.has(String(k))?m.get(String(k)):null,setItem:(k,v)=>m.set(String(k),String(v)),removeItem:k=>m.delete(String(k)),clear:()=>m.clear(),key:i=>[...m.keys()][i]??null,get length(){return m.size}};Object.defineProperty(window,"localStorage",{value:ls});Object.defineProperty(window,"sessionStorage",{value:ls})}` +
    `` +
    `const poner=(t,err)=>{const c=caja();if(!c)return;c.hidden=false;const l=document.createElement("div");l.textContent=t;if(err)l.className="e";c.appendChild(l)};` +
    `const log=console.log.bind(console);console.log=(...a)=>{log(...a);poner(fmt(a))};const er=console.error.bind(console);console.error=(...a)=>{er(...a);if(!/^Warning:|The above error occurred|Consider adding an error boundary/.test(String(a[0])))poner(fmt(a),1)};` +
    `addEventListener("error",e=>poner("Error: "+(e.message||e.error),1));addEventListener("unhandledrejection",e=>poner("Error: "+(e.reason?.message||e.reason),1));})()<\/script>`;
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">` +
    `<style>body{font-family:system-ui,sans-serif;margin:12px;color:#111}#cc-consola{font:12px ui-monospace,monospace;background:#0f172a;color:#e2e8f0;padding:6px 8px;border-radius:8px;margin-top:14px;max-height:140px;overflow:auto}#cc-consola::before{content:"Consola";display:block;color:#94a3b8;margin-bottom:2px}#cc-consola .e{color:#fca5a5}</style>` +
    `<script type="importmap">${mapa}<\/script>${consola}</head><body><div id="root"></div><div id="cc-consola" hidden></div>` +
    `<script type="module">${js.replace(/<\/script/gi, '<\\/script')}<\/script></body></html>`;
}

async function ejecutar() {
  const b = $('run');
  b.disabled = true; $('vista').hidden = true; out.hidden = false; out.className = ''; out.textContent = 'Ejecutando…';
  try {
    const [t, e] = await RUN[LEC[lang].run](ed.value, lang);
    out.className = e ? 'err' : '';
    out.textContent = t.trim() || '(el programa no mostró nada)';
  } catch (x) {
    out.className = 'err'; out.textContent = x.message;
  }
  b.disabled = false;
  // ¿Error? Codi (el tutor de IA) lo explica con tu código y la salida
  import('/js/sonidos.js').then((m) => m.sonar(out.className === 'err' ? 'programa_error' : 'programa_ok')).catch(() => {});
  if (out.className === 'err') {
    const L = LEC[lang];
    const preg = `Estoy en la lección «${L.l[idx][0]}» de ${L.n}. Mi código da este error:\n\n${out.textContent.slice(0, 1500)}\n\nMi código:\n${ed.value.slice(0, 4000)}\n\nExplícame en palabras simples qué está mal y cómo arreglarlo.`;
    const a = document.createElement('a');
    a.className = 'btn-ia-error';
    a.href = `/pages/ia.html?q=${encodeURIComponent(preg)}`;
    a.target = '_blank'; a.rel = 'noopener';
    a.textContent = '✨ Explícame este error (IA)';
    out.append(document.createElement('br'), a);
  }
}

/* ===== Ocultar / mostrar el panel izquierdo (se recuerda la elección) ===== */
const aula = document.querySelector('.aula');
function panel(cerrado, usuario) {
  aula.classList.toggle('sin-ruta', cerrado);
  $('rutaCerrar').setAttribute('aria-expanded', String(!cerrado));
  $('rutaAbrir').setAttribute('aria-expanded', String(!cerrado));
  try { localStorage.setItem('cc_ruta_cerrada', cerrado ? '1' : '0'); } catch {}
  if (usuario) (cerrado ? $('rutaAbrir') : $('rutaCerrar')).focus();
}
$('rutaCerrar').onclick = () => panel(true, true);
$('rutaAbrir').onclick = () => panel(false, true);
try { if (localStorage.getItem('cc_ruta_cerrada') === '1') panel(true, false); } catch {}

document.body.classList.remove('cargando');
abrir(lang);

mejorarEditor();
