// Cuando compartes algo con CódigoCamp (desde otra app del celular o de Windows), se le pregunta a la IA.
(function () {
  var q = new URLSearchParams(location.search);
  var partes = [q.get("titulo"), q.get("texto"), q.get("enlace")].filter(function (x) { return x && x.trim(); });
  var texto = partes.join("\n").slice(0, 4000);
  location.replace(texto ? "/pages/ia.html?q=" + encodeURIComponent("Explícame esto:\n" + texto) : "/pages/inicio.html?app=1");
})();
