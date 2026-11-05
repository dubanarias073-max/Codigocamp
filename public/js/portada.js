// Efectos de la portada: la cabecera se rellena al bajar y el menú marca la sección visible.
const bar = document.querySelector(".bar");
const alternar = () => bar.classList.toggle("scrolled", window.scrollY > 24);
alternar();
addEventListener("scroll", alternar, { passive: true });

const enlaces = [...document.querySelectorAll(".nav-links a")];
const secciones = enlaces.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
const obs = new IntersectionObserver(
  (entradas) => entradas.forEach((e) => {
    if (e.isIntersecting) enlaces.forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id));
  }),
  { rootMargin: "-45% 0px -50% 0px" }
);
secciones.forEach((s) => obs.observe(s));
