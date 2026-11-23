// Portada: Codi programando como una IA. Teclea código de verdad en el editor (JavaScript, Python, HTML, SQL),
// corre las pruebas y celebra; mientras tanto piensa, giran engranajes y flotan símbolos de código.
import { codiSVG, saltarCodi } from "/js/codi.js";

const PROGRAMAS = [
  { archivo: "script.js", tab2: "index.html", lineas: [
    [["t-c", "// ¿Es par?"]],
    [["t-k", "function "], ["t-f", "esPar"], ["", "(n) {"]],
    [["", "  "], ["t-k", "return "], ["", "n % "], ["t-n", "2"], ["", " === "], ["t-n", "0"], ["", ";"]],
    [["", "}"]],
  ], pruebas: ["esPar(4) → true", "esPar(7) → false"] },
  { archivo: "main.py", tab2: "datos.csv", lineas: [
    [["t-c", "# Promedio de notas"]],
    [["t-k", "def "], ["t-f", "promedio"], ["", "(notas):"]],
    [["", "    "], ["t-k", "return "], ["t-f", "sum"], ["", "(notas) / "], ["t-f", "len"], ["", "(notas)"]],
    [["t-f", "print"], ["", "(promedio(["], ["t-n", "4"], ["", ", "], ["t-n", "5"], ["", ", "], ["t-n", "3"], ["", "]))"]],
  ], pruebas: ["promedio([4, 5, 3]) → 4.0", "Sin errores"] },
  { archivo: "index.html", tab2: "styles.css", lineas: [
    [["t-c", "<!-- Mi primera página -->"]],
    [["t-k", "<h1>"], ["", "Hola, mundo"], ["t-k", "</h1>"]],
    [["t-k", "<button "], ["t-f", "onclick"], ["", "="], ["t-n", "\"saludar()\""], ["t-k", ">"]],
    [["", "  ¡Haz clic!"], ["t-k", "</button>"]],
  ], pruebas: ["Página lista", "Botón funciona"] },
  { archivo: "consulta.sql", tab2: "tienda.db", lineas: [
    [["t-c", "-- Los 3 más vendidos"]],
    [["t-k", "SELECT "], ["", "nombre, ventas"]],
    [["t-k", "FROM "], ["t-f", "productos"]],
    [["t-k", "ORDER BY "], ["", "ventas "], ["t-k", "DESC LIMIT "], ["t-n", "3"], ["", ";"]],
  ], pruebas: ["3 filas", "0,4 ms"] },
];
const SIMBOLOS = ["{ }", "</>", "( )", ";", "01", "=>", "[ ]", "#", "✓", "λ", "&&", "AI"];
const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
const esc = (t) => t.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

export function montarEscena(vis) {
  const ventana = vis?.querySelector(".ventana");
  const code = ventana?.querySelector(".ed-code");
  if (!ventana || !code) return;
  vis.classList.add("con-codi");
  const escena = document.createElement("div");
  escena.className = "codi-escena";
  escena.setAttribute("aria-hidden", "true");
  escena.innerHTML = `
    <div class="ce-engranes"><span class="ce-eng g1">⚙</span><span class="ce-eng g2">⚙</span></div>
    <div class="ce-burbuja" id="ceBurbuja">Pensando…</div>
    <div class="ce-codi" id="ceCodi">${codiSVG("pensando", { tam: 150 })}</div>
    <svg class="ce-laptop" viewBox="0 0 160 70"><defs><linearGradient id="ceLap" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#334155"/><stop offset="1" stop-color="#0f172a"/></linearGradient></defs>
      <path d="M22 4h116a6 6 0 0 1 6 6v40H16V10a6 6 0 0 1 6-6z" fill="url(#ceLap)" stroke="#5ef2ff" stroke-opacity=".5" stroke-width="2"/>
      <circle cx="80" cy="27" r="9" fill="none" stroke="#5ef2ff" stroke-width="2.5" stroke-opacity=".8"/><path d="M76 27l3 3 6-6" stroke="#a3e635" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <path d="M4 50h152l-8 14H12z" fill="#1e293b" stroke="#5ef2ff" stroke-opacity=".4" stroke-width="2"/>
      <g fill="#475569"><rect x="24" y="54" width="112" height="3" rx="1.5"/><rect x="34" y="59" width="92" height="3" rx="1.5"/></g></svg>
    <span class="ce-mano izq"></span><span class="ce-mano der"></span>
    <div class="ce-simbolos" id="ceSimb"></div>`;
  vis.appendChild(escena);
  const tab = ventana.querySelector(".ed-tab.on"), tab2 = ventana.querySelectorAll(".ed-tab")[1];
  const pruebas = ventana.querySelector(".ed-test"), res = ventana.querySelector(".ed-res");
  const burbuja = escena.querySelector("#ceBurbuja"), codiEl = escena.querySelector("#ceCodi"), simb = escena.querySelector("#ceSimb");
  const animo = (a) => { codiEl.innerHTML = codiSVG(a, { tam: 150 }); };
  const decir = (t) => { burbuja.textContent = t; burbuja.classList.remove("sale"); void burbuja.offsetWidth; burbuja.classList.add("sale"); };
  const soltarSimbolo = () => {
    const s = document.createElement("span");
    s.textContent = SIMBOLOS[Math.floor(Math.random() * SIMBOLOS.length)];
    s.style.left = `${10 + Math.random() * 80}%`;
    s.style.setProperty("--dx", `${(Math.random() - 0.5) * 60}px`);
    s.style.color = ["#5ef2ff", "#a3e635", "#f472b6", "#facc15", "#c084fc"][Math.floor(Math.random() * 5)];
    simb.appendChild(s);
    setTimeout(() => s.remove(), 2600);
  };
  if (reducido) { animo("feliz"); return; }
  let simbolos = null;
  (async () => {
    let n = 0;
    while (document.body.contains(escena)) {
      const prog = PROGRAMAS[n++ % PROGRAMAS.length];
      if (tab) tab.textContent = prog.archivo;
      if (tab2) tab2.textContent = prog.tab2;
      pruebas.hidden = true; res.classList.remove("ok");
      code.innerHTML = '<span class="cursor"></span>';
      animo("pensando"); decir(["Pensando…", "Analizando el problema…", "Diseñando la solución…", "Escribiendo código…"][n % 4]);
      escena.classList.add("tecleando");
      simbolos = setInterval(soltarSimbolo, 420);
      await esperar(700);
      let html = "";
      for (const linea of prog.lineas) {
        for (const [clase, texto] of linea) {
          for (let i = 1; i <= texto.length; i++) {
            const parcial = esc(texto.slice(0, i));
            code.innerHTML = html + (clase ? `<span class="${clase}">${parcial}</span>` : parcial) + '<span class="cursor"></span>';
            await esperar(texto[i - 1] === " " ? 20 : 38 + Math.random() * 45);
          }
          html += clase ? `<span class="${clase}">${esc(texto)}</span>` : esc(texto);
        }
        html += "\n";
        await esperar(160);
      }
      escena.classList.remove("tecleando"); clearInterval(simbolos);
      decir("Ejecutando pruebas…"); escena.classList.add("compilando");
      await esperar(900);
      escena.classList.remove("compilando");
      pruebas.innerHTML = prog.pruebas.map((p) => `<p><span class="t-ok">✓</span> ${esc(p)}</p>`).join("");
      pruebas.hidden = false; res.classList.add("ok");
      animo("celebra"); decir(["¡Funciona! 🎉", "¡Todas las pruebas pasan!", "¡Listo y sin errores!", "¡Código perfecto!"][n % 4]);
      saltarCodi?.(codiEl.querySelector("svg"));
      for (let i = 0; i < 8; i++) setTimeout(soltarSimbolo, i * 60);
      await esperar(2600);
    }
  })();
}

montarEscena(document.querySelector(".portada-vis"));
