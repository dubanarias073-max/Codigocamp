// CódigoCamp está solo en español. Este archivo queda para que las páginas que lo cargan sigan funcionando
// y para limpiar la preferencia de idioma que guardaban versiones anteriores.
(function () {
  "use strict";
  try { localStorage.removeItem("cc_idioma"); localStorage.removeItem("cc_idioma_pendiente"); } catch (e) { /* sin almacenamiento */ }
  window.CC_IDIOMA = "es";
  document.documentElement.lang = "es";
  window.ccIdioma = function () {};
  window.ccT = function (s) { return s; };
})();
