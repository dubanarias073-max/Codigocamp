// Preguntas iniciales: una pregunta por pantalla, guarda las respuestas y lleva al primer reto.
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var form = $('onb'), main = $('main'), sig = $('sig'), atras = $('atras'), prog = $('progreso'), barra = $('barra');
  var numeroPaso = $('paso-numero');
  var pasos = Array.prototype.slice.call(form.querySelectorAll('.paso'));
  var i = 0;

  var CURSOS = { html: 'HTML', css: 'CSS', bd: 'Bases de datos', javascript: 'JavaScript', python: 'Python', typescript: 'TypeScript',
    java: 'Java', csharp: 'C#', kotlin: 'Kotlin', swift: 'Swift', php: 'PHP', ruby: 'Ruby', go: 'Go', rust: 'Rust', c: 'C', cpp: 'C++' };
  // Qué curso recomendar según lo que quiere crear
  var RECOMIENDA = { web: 'html', movil: 'kotlin', juegos: 'csharp', datos: 'python', auto: 'python', bd: 'bd' };

  function respondido(p) {
    return !p.querySelector('input') || p.querySelector('input:checked') !== null;
  }

  function datos() {
    var f = new FormData(form);
    return { rol: f.get('rol'), intereses: f.getAll('intereses'), nivel: f.get('nivel'), curso: f.get('curso'), meta: f.get('meta') };
  }

  function marcarRecomendados() {
    var elegidos = datos().intereses.map(function (k) { return RECOMIENDA[k]; });
    form.querySelectorAll('input[name="curso"]').forEach(function (inp) {
      inp.closest('.op').classList.toggle('recomendado', elegidos.indexOf(inp.value) !== -1);
    });
  }

  function mostrar(n) {
    i = n;
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
    window.scrollTo(0, 0);
    var t = pasos[n].querySelector('.burbuja'); if (t) t.focus({ preventScroll: true });
  }

  function terminar() {
    var d = datos();
    var destino = '/pages/inicio.html?curso=' + encodeURIComponent(d.curso);
    sig.disabled = true;
    fetch('/api/perfil/', { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() }, body: JSON.stringify(d) })
      .then(function (r) {
        if (r.status === 401) { location.href = '/pages/login.html'; return; }
        if (r.ok) { location.href = destino; return; }
        sig.disabled = false; sig.textContent = 'No se pudo guardar. Inténtalo de nuevo';
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
