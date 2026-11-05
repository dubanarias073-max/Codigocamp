import { initTutor, reiniciar } from "./tutor.js";
import { iniciarPagina, mostrar } from "./layout.js";

if ((await iniciarPagina()).ok) {
  initTutor({
    sugerencias: [
      "¿Por dónde empiezo a aprender a programar?",
      "Explícame qué es una variable con un ejemplo",
      "¿Cuál es la diferencia entre SQL y NoSQL?",
      "Dame un ejercicio de JavaScript para principiantes",
      "¿Cómo centro un div con CSS?",
      "Explícame qué son las pruebas unitarias",
    ],
  });
  document.getElementById("nuevo").onclick = () => {
    if (confirm("¿Empezar una conversación nueva? Se borrará la actual.")) reiniciar();
  };
  document.getElementById("q").focus();
  mostrar();
}
