// Pantalla de carga estilo Matrix: lluvia de código mientras la página tiene <body class="cargando">.
// Es un script clásico (sin módulos) para que aparezca al instante. Se quita sola cuando la página quita «cargando»
// Si algo falla mientras carga, o tarda más de 15 s, explica qué pasó y ofrece «Reparar». Respeta «reducir movimiento».
(function () {
  if (window.__ccCarga) return;
  window.__ccCarga = true;
  var estilo = document.createElement("style");
  estilo.textContent =
    "#cc-carga{position:fixed;inset:0;z-index:2147483000;background:#010a04;display:grid;place-items:center;transition:opacity .35s ease}" +
    "#cc-carga.fuera{opacity:0;pointer-events:none}" +
    "#cc-carga canvas{position:absolute;inset:0;width:100%;height:100%}" +
    "#cc-carga .cc-carga-txt{position:relative;font:700 15px ui-monospace,Consolas,monospace;color:#bbf7d0;letter-spacing:.18em;text-shadow:0 0 12px #22c55e;padding:14px 22px;border:1px solid rgba(34,197,94,.5);border-radius:12px;background:rgba(1,10,4,.75)}" +
    "#cc-carga .cc-carga-txt b{color:#4ade80}" +
    "#cc-carga .cc-carga-txt i{display:inline-block;width:.6em;animation:cc-cursor 1s steps(1) infinite;font-style:normal}" +
    "@keyframes cc-cursor{50%{opacity:0}}" +
    "body.cargando>*:not(#cc-carga):not(#cc-ayuda-carga){visibility:hidden}";
  document.head.appendChild(estilo);

  function iniciar() {
    var body = document.body;
    if (!body || !body.classList.contains("cargando")) return;
    var caja = document.createElement("div");
    caja.id = "cc-carga";
    caja.setAttribute("role", "status");
    caja.setAttribute("aria-label", "Cargando");
    var c = document.createElement("canvas");
    var txt = document.createElement("div");
    txt.className = "cc-carga-txt";
    txt.innerHTML = "&gt; <b>codigocamp</b> cargando<i>_</i>";
    caja.appendChild(c);
    caja.appendChild(txt);
    body.appendChild(caja);
    var ctx = c.getContext("2d"), dpr = Math.min(2, window.devicePixelRatio || 1), ancho, alto, cols, gotas, fs = 16 * dpr, vivo = true, ultimo = 0;
    var letras = "01<>/{}[]=+;:()$#&*アイウエオカキクケコサシスセソ";
    function tamano() { ancho = c.width = innerWidth * dpr; alto = c.height = innerHeight * dpr; cols = Math.ceil(ancho / fs); gotas = []; for (var i = 0; i < cols; i++) gotas.push(Math.random() * -40); }
    tamano();
    addEventListener("resize", tamano);
    var quieto = matchMedia("(prefers-reduced-motion: reduce)").matches;
    try { if (localStorage.getItem("cc_menos_mov") === "1") quieto = true; } catch (e) {}
    function paso(t) {
      if (!vivo) return;
      requestAnimationFrame(paso);
      if (t - ultimo < 45) return;
      ultimo = t;
      ctx.fillStyle = "rgba(1,10,4,.14)";
      ctx.fillRect(0, 0, ancho, alto);
      ctx.font = fs + "px ui-monospace,Consolas,monospace";
      for (var i = 0; i < cols; i++) {
        ctx.fillStyle = Math.random() < .05 ? "#ecfdf5" : "#22c55e";
        ctx.fillText(letras[(Math.random() * letras.length) | 0], i * fs, gotas[i] * fs);
        if (gotas[i] * fs > alto && Math.random() > .97) gotas[i] = 0; else gotas[i]++;
      }
    }
    if (!quieto) requestAnimationFrame(paso);
    function quitar() {
      if (!vivo) return;
      vivo = false;
      obs.disconnect();
      caja.classList.add("fuera");
      setTimeout(function () { caja.remove(); removeEventListener("resize", tamano); }, 400);
    }
    var obs = new MutationObserver(function () { if (!body.classList.contains("cargando")) quitar(); });
    obs.observe(body, { attributes: true, attributeFilter: ["class"] });

    setTimeout(function () { if (vivo && body.classList.contains("cargando")) ayudaDeCarga([]); }, 15000);
  }
  if (document.body) iniciar(); else document.addEventListener("DOMContentLoaded", iniciar);

  // ---- Nunca colgado en silencio ----
  // Si falla un archivo de la página (lo típico tras una actualización: el navegador mezcla archivos guardados de la
  // versión anterior con los nuevos) o la carga tarda demasiado, se explica qué pasó y se ofrece «Reparar».
  var errores = [], puesto = false;
  var FATAL = /does not provide an export|Failed to fetch dynamically imported module|Importing a module script failed|error loading dynamically imported module|SyntaxError|is not defined|Cannot find module|No se pudo cargar \/js\//i;
  function anotar(texto) {
    texto = String(texto || "").slice(0, 300);
    if (!texto) return;
    errores.push(texto);
    if (FATAL.test(texto)) setTimeout(function () { ayudaDeCarga(errores); }, 800);
  }
  addEventListener("error", function (e) {
    var t = e.target;
    if (t && t !== window && (t.src || t.href)) { if (/\/(js|css)\//.test(t.src || t.href)) anotar("No se pudo cargar " + (t.src || t.href).replace(location.origin, "")); return; }
    anotar(e.message);
  }, true);
  addEventListener("unhandledrejection", function (e) { var r = e.reason; anotar(r && (r.message || r)); });

  function reparar() {
    var tareas = [];
    try { if (navigator.serviceWorker) tareas.push(navigator.serviceWorker.getRegistrations().then(function (rs) { return Promise.all(rs.map(function (r) { return r.unregister(); })); })); } catch (e) {}
    try { if (window.caches) tareas.push(caches.keys().then(function (ks) { return Promise.all(ks.map(function (k) { return caches.delete(k); })); })); } catch (e) {}
    Promise.all(tareas).catch(function () {}).then(function () { location.reload(); });
  }

  function ayudaDeCarga(lista) {
    if (puesto || !document.body) return;
    puesto = true;
    var fondo = document.createElement("div");
    fondo.id = "cc-ayuda-carga";
    fondo.setAttribute("role", "alertdialog");
    fondo.style.cssText = "position:fixed;inset:0;z-index:2147483646;display:grid;place-items:center;background:rgba(1,10,4,.86)";
    var detalle = lista.length ? "<pre style='white-space:pre-wrap;max-height:130px;overflow:auto;margin:10px 0;padding:8px;border-radius:8px;background:#04170b;color:#fca5a5;font:12px ui-monospace,monospace'>" +
      lista.slice(0, 4).map(function (t) { return t.replace(/&/g, "&amp;").replace(/</g, "&lt;"); }).join("\n") + "</pre>" : "";
    fondo.innerHTML = "<div style='max-width:520px;margin:0 18px;padding:20px 22px;border:1px solid rgba(34,197,94,.5);border-radius:14px;background:#010a04;color:#d1fae5;font:14px/1.5 system-ui,sans-serif'>" +
      "<b style='font-size:16px;color:#4ade80'>" + (lista.length ? "Esta página no terminó de cargar" : "Está tardando más de lo normal") + "</b>" +
      "<p style='margin:8px 0 0'>" + (lista.length ? "Casi siempre es porque el navegador guardó archivos de una versión anterior de CódigoCamp. «Reparar» los borra y vuelve a cargar. Tu cuenta y tus proyectos no se pierden." : "Puede ser la conexión. Si no avanza, «Reparar» borra los archivos guardados de versiones anteriores y vuelve a cargar.") + "</p>" + detalle +
      "<div style='display:flex;gap:10px;flex-wrap:wrap;margin-top:12px'><button type='button' data-cc='reparar' style='padding:9px 14px;border:0;border-radius:9px;background:#22c55e;color:#012;font-weight:700;cursor:pointer'>Reparar y recargar</button>" +
      "<button type='button' data-cc='recargar' style='padding:9px 14px;border:1px solid #2f855a;border-radius:9px;background:transparent;color:#d1fae5;cursor:pointer'>Recargar</button>" +
      "<button type='button' data-cc='cerrar' style='padding:9px 14px;border:1px solid #2f855a;border-radius:9px;background:transparent;color:#d1fae5;cursor:pointer'>Cerrar</button></div></div>";
    fondo.onclick = function (e) {
      var b = e.target.closest && e.target.closest("[data-cc]");
      if (!b) return;
      var a = b.getAttribute("data-cc");
      if (a === "recargar") location.reload();
      else if (a === "reparar") reparar();
      else { fondo.remove(); document.body.classList.remove("cargando"); var c = document.getElementById("cc-carga"); if (c) c.remove(); }
    };
    document.body.appendChild(fondo);
  }
  window.ccAyudaDeCarga = ayudaDeCarga;
})();
