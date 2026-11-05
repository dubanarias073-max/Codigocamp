// Aplica el tema guardado ANTES de que se pinte la página (evita el parpadeo).
// Valores: "auto" (predeterminado, sigue al dispositivo), "claro" y "oscuro".
(function () {
  var t = "auto";
  try { t = localStorage.getItem("cc_tema") || "auto"; } catch (e) {}
  if (t !== "claro" && t !== "oscuro") t = "auto";
  document.documentElement.setAttribute("data-tema", t);
})();
