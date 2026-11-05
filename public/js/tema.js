// Tema claro / oscuro. Por defecto: oscuro (como el logo). Se recuerda la elección.
// Se carga en el <head> para que no parpadee al abrir la página.
(function () {
  var KEY = "cc_tema", raiz = document.documentElement;
  try { var g = localStorage.getItem(KEY); if (g === "dark" || g === "light") raiz.setAttribute("data-theme", g); } catch (e) {}

  function actual() { return raiz.getAttribute("data-theme") || "dark"; }
  function pintar() {
    var b = document.getElementById("temaBtn");
    if (!b) return;
    var oscuro = actual() === "dark";
    b.textContent = oscuro ? "☀️" : "🌙";
    b.setAttribute("aria-label", oscuro ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
    b.title = oscuro ? "Tema claro" : "Tema oscuro";
  }
  document.addEventListener("DOMContentLoaded", function () {
    var b = document.getElementById("temaBtn");
    if (!b) return;
    pintar();
    b.addEventListener("click", function () {
      var nuevo = actual() === "dark" ? "light" : "dark";
      raiz.setAttribute("data-theme", nuevo);
      try { localStorage.setItem(KEY, nuevo); } catch (e) {}
      pintar();
    });
  });
})();
