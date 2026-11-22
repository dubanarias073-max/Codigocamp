// Preguntas iniciales: una pregunta por pantalla, guarda las respuestas y lleva al primer reto.
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var form = $('onb'), main = $('main'), sig = $('sig'), atras = $('atras'), prog = $('progreso'), barra = $('barra');
  var numeroPaso = $('paso-numero');
  var pasos = Array.prototype.slice.call(form.querySelectorAll('.paso'));
  var i = 0;

  var CURSOS = { html: 'HTML', css: 'CSS', bd: 'Bases de datos', javascript: 'JavaScript', python: 'Python', typescript: 'TypeScript',
    java: 'Java', csharp: 'C#', kotlin: 'Kotlin', swift: 'Swift', php: 'PHP', ruby: 'Ruby', go: 'Go', rust: 'Rust', c: 'C', cpp: 'C++',
    terminal: 'Terminales', git: 'Git', github: 'GitHub', docker: 'Docker', node: 'Node.js', nosql: 'NoSQL', react: 'React' };
  // Qué curso recomendar según lo que quiere crear
  var RECOMIENDA = { web: 'html', movil: 'kotlin', juegos: 'csharp', datos: 'python', auto: 'terminal', bd: 'bd' };

  function respondido(p) {
    // Términos: hay que marcar TODAS las casillas obligatorias.
    var obligatorias = p.querySelectorAll('input[required]');
    if (obligatorias.length) return Array.prototype.every.call(obligatorias, function (x) { return x.checked; });
    return !p.querySelector('input') || p.querySelector('input:checked') !== null;
  }

  // El texto de los términos vive en una sola página (terminos.html): se copia aquí.
  var VERSION_TERMINOS = null;
  fetch('/pages/terminos.html', { credentials: 'same-origin' }).then(function (r) { return r.text(); }).then(function (html) {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var art = doc.getElementById('terminosTexto');
    if (!art) throw new Error('sin texto');
    VERSION_TERMINOS = art.getAttribute('data-version');
    var caja = $('terminosCaja');
    caja.replaceChildren(document.importNode(art, true));
    caja.firstElementChild.removeAttribute('id');
  }).catch(function () {
    $('terminosCaja').innerHTML = '<p>No se pudieron cargar los términos aquí. <a href="/pages/terminos.html" target="_blank" rel="noopener">Ábrelos en otra pestaña</a>.</p>';
  });

  function datos() {
    var f = new FormData(form);
    return { rol: f.get('rol'), intereses: f.getAll('intereses'), nivel: f.get('nivel'), curso: f.get('curso'), meta: f.get('meta'),
      terminos: f.getAll('acepta').length === 3 ? (VERSION_TERMINOS || 'actual') : null };
  }

  function marcarRecomendados() {
    var elegidos = datos().intereses.map(function (k) { return RECOMIENDA[k]; });
    form.querySelectorAll('input[name="curso"]').forEach(function (inp) {
      inp.closest('.op').classList.toggle('recomendado', elegidos.indexOf(inp.value) !== -1);
    });
  }

  // ---- Íconos de línea (en vez de emojis) ----
  var ICONOS = {
    estudiante: '<path d="M3 9l9-5 9 5-9 5z"/><path d="M7 11v5c3 2 7 2 10 0v-5"/><path d="M21 9v6"/>',
    cambio: '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 12h18"/>',
    programador: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M10 8l-2 2 2 2M14 8l2 2-2 2"/>',
    curioso: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    web: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    movil: '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    juegos: '<rect x="2" y="7" width="20" height="10" rx="5"/><path d="M7 10v4M5 12h4"/><circle cx="16" cy="11" r="1"/><circle cx="18" cy="13" r="1"/>',
    datos: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    auto: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
    bd: '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    cero: '<path d="M12 21V11"/><path d="M12 11c0-4 3-6 7-6 0 4-3 6-7 6zM12 14c0-3-2-5-6-5 0 3 2 5 6 5z"/>',
    probado: '<path d="M12 21V8"/><path d="M12 8c0-3 2-5 5-5 0 3-2 5-5 5zM12 12c0-3-2-5-5-5 0 3 2 5 5 5zM12 16c0-2 2-4 5-4 0 2-2 4-5 4z"/>',
    basico: '<path d="M12 21v-5"/><path d="M12 16c-5 0-8-3-8-7a8 8 0 0 1 16 0c0 4-3 7-8 7z"/>',
    avanzado: '<path d="M5 19c1-4 3-7 6-9l3 3c-2 3-5 5-9 6z"/><path d="M14 13l6-9-9 6M9 15l-2 2"/>',
    m5: '<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5zM16 10h2a2 2 0 0 1 0 4h-2"/>',
    m10: '<path d="M4 5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4zM20 5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z"/>',
    m15: '<path d="M6 10v4M18 10v4M3 11v2M21 11v2M6 12h12"/>',
    m30: '<path d="M12 3c1 4-2 5-1 8 1.4-1 2-2.2 2-4 4 3 6 6 5 10a7 7 0 0 1-14 0c0-3 2-6 5-8-.3 2.7.2 4.2 1.4 5.2C13 11 14 7 12 3z"/>',
  };
  form.querySelectorAll('.op input').forEach(function (inp) {
    var clave = inp.name === 'meta' ? 'm' + inp.value : inp.value;
    var ico = inp.closest('.op').querySelector('.ico:not(.sigla)');
    if (ico && ICONOS[clave]) ico.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONOS[clave] + '</svg>';
  });

  // ---- Panel: pasos y «perfil.js» que se escribe mientras respondes ----
  var lista = $('pasosLista'), codigo = $('codigoVivo');
  var NOMBRES = { estudiante: 'estudiante', cambio: 'cambio de rumbo', programador: 'ya programa', curioso: 'curiosidad',
    web: 'web', movil: 'apps móviles', juegos: 'videojuegos', datos: 'datos e IA', auto: 'automatizar', bd: 'bases de datos',
    cero: 'desde cero', probado: 'ha probado algo', basico: 'lo básico', avanzado: 'con experiencia' };
  var escribiendo = null;
  function lineas() {
    var d = datos();
    var q = function (v) { return v ? '<s>"' + v + '"</s>' : '<em>null</em>'; };
    return '<b>const</b> yo = {\n' +
      '  rol: ' + q(NOMBRES[d.rol]) + ',\n' +
      '  quiere: [' + (d.intereses.length ? d.intereses.map(function (x) { return '<s>"' + NOMBRES[x] + '"</s>'; }).join(', ') : '') + '],\n' +
      '  nivel: ' + q(NOMBRES[d.nivel]) + ',\n' +
      '  curso: ' + q(CURSOS[d.curso]) + ',\n' +
      '  minutosAlDia: ' + (d.meta ? '<u>' + d.meta + '</u>' : '<em>null</em>') + ',\n' +
      '  aceptaTerminos: ' + (d.terminos ? '<u>true</u>' : '<em>false</em>') + ',\n' +
      '};\n\n<i>// ' + (d.curso ? 'listo para empezar ' + CURSOS[d.curso] : 'completando tu perfil…') + '</i>';
  }
  function pintarPanel() {
    var html = lineas();
    if (escribiendo) clearTimeout(escribiendo);
    codigo.innerHTML = html + '<span class="cursor">▋</span>';
    codigo.classList.remove('pulso'); void codigo.offsetWidth; codigo.classList.add('pulso');
    lista.querySelectorAll('li').forEach(function (li, k) { li.classList.toggle('hecho', k < i); li.classList.toggle('actual', k === i); });
  }
  form.addEventListener('change', pintarPanel);
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'TEXTAREA' || e.ctrlKey || e.metaKey || e.altKey) return;
    var paso = pasos[i];
    if (/^[1-9]$/.test(e.key)) {
      var ops = paso.querySelectorAll('.op input');
      var inp = ops[Number(e.key) - 1];
      if (inp) { inp.checked = inp.type === 'checkbox' ? !inp.checked : true; inp.dispatchEvent(new Event('change', { bubbles: true })); inp.focus(); }
    } else if (e.key === 'Enter' && !sig.disabled && e.target.tagName !== 'BUTTON') { e.preventDefault(); sig.click(); }
    else if (e.key === 'Backspace' && i > 0 && e.target.tagName !== 'INPUT') { atras.click(); }
  });

  function mostrar(n) {
    var antes = i;
    i = n;
    pasos.forEach(function (p) { p.classList.remove('entra-der', 'entra-izq'); });
    pasos[n].classList.add(n >= antes ? 'entra-der' : 'entra-izq');
    pasos.forEach(function (p, k) { p.hidden = k !== n; });
    var pct = Math.round(n / (pasos.length - 1) * 100);
    prog.style.width = pct + '%';
    barra.setAttribute('aria-valuenow', pct);
    numeroPaso.textContent = 'PASO ' + String(n + 1).padStart(2, '0') + ' / ' + String(pasos.length).padStart(2, '0');
    atras.classList.toggle('oculto', n === 0);
    main.classList.toggle('ancho', pasos[n].hasAttribute('data-ancho'));
    var ultimo = n === pasos.length - 1;
    sig.textContent = ultimo ? 'Empezar mi primer reto' : 'Continuar';
    sig.disabled = !respondido(pasos[n]);
    if (pasos[n].dataset.paso === 'curso') marcarRecomendados();
    if (ultimo) {
      var d = datos();
      $('resCurso').textContent = CURSOS[d.curso] || '—';
      $('resMeta').textContent = d.meta ? d.meta + ' min al día' : '—';
    }
    pintarPanel();
    if (ultimo) celebrar();
    window.scrollTo(0, 0);
    var t = pasos[n].querySelector('.burbuja'); if (t) t.focus({ preventScroll: true });
  }

  function celebrar() {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var colores = ['#22d3ee', '#4ade80', '#fbbf24', '#f472b6', '#a78bfa'];
    for (var k = 0; k < 40; k++) {
      var c = document.createElement('span');
      c.className = 'onb-confeti';
      c.style.cssText = 'left:' + Math.random() * 100 + 'vw;background:' + colores[k % 5] + ';animation-delay:' + Math.random() * .5 + 's;transform:rotate(' + Math.random() * 360 + 'deg)';
      document.body.appendChild(c);
      setTimeout(function (x) { x.remove(); }.bind(null, c), 2800);
    }
  }

  function terminar() {
    var d = datos();
    var destino = '/pages/inicio.html?curso=' + encodeURIComponent(d.curso);
    sig.disabled = true;
    fetch('/api/perfil/', { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf(), 'X-Zona-Horaria': (function () { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) { return ''; } })() }, body: JSON.stringify(d) })
      .then(function (r) {
        if (r.status === 401) { location.href = '/pages/login.html'; return; }
        if (r.ok) { location.href = destino; return; }
        return r.json().catch(function () { return {}; }).then(function (e) {
          sig.disabled = false; sig.textContent = e.error ? e.error : 'No se pudo guardar. Inténtalo de nuevo';
        });
      })
      .catch(function () { sig.disabled = false; sig.textContent = 'Sin conexión. Inténtalo de nuevo'; });
  }

  form.addEventListener('change', function () { sig.disabled = !respondido(pasos[i]); });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  sig.addEventListener('click', function () { if (i < pasos.length - 1) mostrar(i + 1); else terminar(); });
  atras.addEventListener('click', function () { if (i > 0) mostrar(i - 1); });

  function csrf() { var m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/); return m ? m[1] : ''; }
  // Pide la cookie csrftoken y comprueba que haya sesión iniciada
  fetch('/api/auth/me/', { credentials: 'same-origin' }).then(function (r) { return r.json(); })
    .then(function (d) { if (!d.user) { location.replace('/pages/login.html'); return; }
      var t = d.user.tema === 'claro' || d.user.tema === 'oscuro' ? d.user.tema : 'auto';
      document.documentElement.setAttribute('data-tema', t);
      try { localStorage.setItem('cc_tema', t); } catch (e) {} }).catch(function () {});

  mostrar(0);
})();
