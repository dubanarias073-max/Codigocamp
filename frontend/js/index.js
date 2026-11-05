// Lógica de index.html
// Al bajar, la barra recibe la clase "scrolled" (fondo sólido) igual que en login y registro
(function () {
  var barra = document.querySelector('.bar');
  function revisar() { barra.classList.toggle('scrolled', window.scrollY > 10); }
  revisar();
  window.addEventListener('scroll', revisar, { passive: true });
})();
