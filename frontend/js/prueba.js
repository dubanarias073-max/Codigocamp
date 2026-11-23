// Prueba de CódigoCamp (antes de registrarse): 4 secciones con retos variados para conocer tu nivel.
// Al final te dice tu nivel y te lleva a crear la cuenta; el nivel queda guardado para el registro (cc_prueba_nivel).
import { codiSVG, saltarCodi } from "/js/codi.js";
import { prepararSonido, sonar, vibrar } from "/js/sonidos.js";

const T = (s) => (window.ccT ? window.ccT(s) : s);
const SECCIONES = [
  { titulo: "Lógica", icono: "🧠", sub: "Sin código: solo piensa como programador", retos: [
    { tipo: "elegir", pregunta: "¿Qué número sigue? 2, 4, 8, 16, …", opciones: ["18", "24", "32", "20"], ok: 2, porque: "Cada número es el doble del anterior: 16 × 2 = 32." },
    { tipo: "elegir", pregunta: "Si llueve llevo paraguas. Hoy NO llevo paraguas. ¿Qué sabemos?", opciones: ["Que llueve", "Que no llueve", "Nada", "Que hace sol"], ok: 1, porque: "Si lloviera, llevaría paraguas. Como no lo llevo, no llueve." },
    { tipo: "elegir", pregunta: "Una receta dice: «repite 3 veces: agrega 2 huevos». ¿Cuántos huevos usas?", opciones: ["2", "3", "5", "6"], ok: 3, porque: "Un bucle: 3 repeticiones × 2 huevos = 6." },
  ] },
  { titulo: "Leer código", icono: "👀", sub: "¿Qué muestra el programa?", retos: [
    { tipo: "salida", lenguaje: "Python", codigo: "x = 5\nx = x + 3\nprint(x)", opciones: ["5", "8", "x + 3", "53"], ok: 1, porque: "x empieza en 5 y luego se le suma 3: queda 8." },
    { tipo: "salida", lenguaje: "JavaScript", codigo: "let nombre = \"Ana\";\nconsole.log(\"Hola \" + nombre);", opciones: ["Hola nombre", "Hola Ana", "\"Hola\" Ana", "Error"], ok: 1, porque: "El + une los textos: «Hola » + «Ana»." },
    { tipo: "salida", lenguaje: "Python", codigo: "for i in range(3):\n    print(i)", opciones: ["1 2 3", "0 1 2", "0 1 2 3", "3"], ok: 1, porque: "range(3) cuenta desde 0 y se detiene antes del 3." },
  ] },
  { titulo: "Completar", icono: "🧩", sub: "Elige la pieza que falta", retos: [
    { tipo: "completar", lenguaje: "Python", antes: "if edad ", despues: " 18:\n    print(\"Eres mayor de edad\")", opciones: [">=", "=", "+", "=>"], ok: 0, porque: "«>=» compara «mayor o igual». Un solo «=» asigna, no compara." },
    { tipo: "completar", lenguaje: "HTML", antes: "<", despues: ">Mi página</h1>", opciones: ["h1", "title", "p", "/h1"], ok: 0, porque: "Una etiqueta se abre <h1> y se cierra </h1> con el mismo nombre." },
    { tipo: "completar", lenguaje: "JavaScript", antes: "const frutas = [\"🍎\", \"🍌\"];\nconsole.log(frutas", despues: ");  // 🍎", opciones: ["[0]", "[1]", ".0", "(0)"], ok: 0, porque: "Las listas empiezan en la posición 0: frutas[0] es 🍎." },
  ] },
  { titulo: "Reto final", icono: "🏆", sub: "Ordena y depura como un pro", retos: [
    { tipo: "ordenar", lenguaje: "Python", pregunta: "Ordena las líneas para saludar 3 veces", lineas: ["for i in range(3):", "    print(\"¡Hola!\")", "print(\"Listo\")"], porque: "Primero el bucle, luego lo que se repite (con sangría) y al final lo que va después." },
    { tipo: "error", lenguaje: "JavaScript", pregunta: "Toca la línea que tiene el error", lineas: ["let total = 0;", "for (let i = 1; i <= 3; i++) {", "  total = total + i", "}", "console.log(\"Total: \" total);"], ok: 4, porque: "Falta el + para unir el texto con la variable: \"Total: \" + total." },
    { tipo: "elegir", pregunta: "¿Para qué sirve una función?", opciones: ["Para guardar un solo número", "Para agrupar código y reutilizarlo", "Para cambiar el color de la página", "Para borrar variables"], ok: 1, porque: "Una función agrupa instrucciones con un nombre para usarlas cuantas veces quieras." },
  ] },
];
const NIVELES = [
  { id: "cero", min: 0, titulo: "Empiezas desde cero", icono: "🌱", texto: "¡Perfecto para empezar! Te llevamos paso a paso desde lo más básico." },
  { id: "probado", min: 4, titulo: "Ya has probado algo", icono: "🌿", texto: "Tienes buena lógica. Repasamos lo básico rápido y avanzamos." },
  { id: "basico", min: 7, titulo: "Sabes lo básico", icono: "🌳", texto: "¡Muy bien! Saltamos lo más fácil y vamos directo a retos de tu nivel." },
  { id: "avanzado", min: 10, titulo: "Tienes experiencia", icono: "🚀", texto: "¡Impresionante! Te esperan retos avanzados, Trabajo, tu editor profesional, y la IA." },
];

const $ = (id) => document.getElementById(id);
const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const todos = SECCIONES.flatMap((s, si) => s.retos.map((r, ri) => ({ ...r, si, ri })));
let i = 0, aciertos = 0, porSeccion = SECCIONES.map(() => 0), elegido = null, orden = [];

function codi(animo, frase) {
  $("pCodi").innerHTML = codiSVG(animo, { tam: 92 });
  if (frase) { const b = $("pBurbuja"); b.textContent = T(frase); b.classList.remove("sale"); void b.offsetWidth; b.classList.add("sale"); }
}

function pintarProgreso() {
  $("pBarra").style.width = `${(i / todos.length) * 100}%`;
  $("pSecciones").innerHTML = SECCIONES.map((s, k) => {
    const r = todos[i]; const actual = r && r.si === k; const hecha = !r || r.si > k;
    return `<li class="${actual ? "on" : ""}${hecha ? " hecha" : ""}"><span>${s.icono}</span><b>${esc(T(s.titulo))}</b></li>`;
  }).join("");
}

function pintarReto() {
  const r = todos[i];
  pintarProgreso();
  elegido = null; orden = [];
  const sec = SECCIONES[r.si];
  if (r.ri === 0) { codi("saludo", `Sección ${r.si + 1}: ${sec.titulo}. ${sec.sub}`); sonar("arranque"); }
  else codi("pensando", ["Tómate tu tiempo…", "Tú puedes 💪", "Piensa como la computadora", "Lee con calma"][i % 4]);
  let cuerpo = "";
  const codigo = (txt) => `<pre class="p-codigo"><span class="p-leng">${esc(r.lenguaje || "")}</span>${esc(txt)}</pre>`;
  if (r.tipo === "elegir" || r.tipo === "salida") {
    cuerpo = `<h2>${esc(T(r.pregunta || "¿Qué muestra este programa?"))}</h2>${r.codigo ? codigo(r.codigo) : ""}
      <div class="p-ops">${r.opciones.map((o, k) => `<button type="button" class="p-op" data-k="${k}"><kbd>${k + 1}</kbd>${esc(T(o))}</button>`).join("")}</div>`;
  } else if (r.tipo === "completar") {
    cuerpo = `<h2>${esc(T("Completa el código"))}</h2><pre class="p-codigo"><span class="p-leng">${esc(r.lenguaje)}</span>${esc(r.antes)}<span class="p-hueco" id="pHueco">___</span>${esc(r.despues)}</pre>
      <div class="p-ops fichas">${r.opciones.map((o, k) => `<button type="button" class="p-op ficha" data-k="${k}">${esc(o)}</button>`).join("")}</div>`;
  } else if (r.tipo === "ordenar") {
    const mezcla = r.lineas.map((t, k) => ({ t, k })).sort(() => Math.random() - 0.5);
    if (mezcla.every((x, k) => x.k === k)) mezcla.reverse();
    cuerpo = `<h2>${esc(T(r.pregunta))}</h2><pre class="p-codigo p-armado" id="pArmado"><span class="p-leng">${esc(r.lenguaje)}</span><span class="p-vacio">${esc(T("Toca las líneas en orden ↓"))}</span></pre>
      <div class="p-ops lineas">${mezcla.map((x) => `<button type="button" class="p-op linea" data-k="${x.k}"><code>${esc(x.t)}</code></button>`).join("")}</div>`;
  } else if (r.tipo === "error") {
    cuerpo = `<h2>${esc(T(r.pregunta))}</h2><div class="p-codigo p-lineas"><span class="p-leng">${esc(r.lenguaje)}</span>${r.lineas.map((t, k) => `<button type="button" class="p-op p-ln" data-k="${k}"><i>${k + 1}</i><code>${esc(t)}</code></button>`).join("")}</div>`;
  }
  $("pReto").innerHTML = `<p class="p-sec">${sec.icono} ${esc(T(sec.titulo))} · ${r.ri + 1}/${sec.retos.length}</p>${cuerpo}`;
  $("pReto").classList.remove("entra"); void $("pReto").offsetWidth; $("pReto").classList.add("entra");
  $("pPie").className = "p-pie"; $("pMsg").innerHTML = "";
  $("pComprobar").textContent = T("Comprobar"); $("pComprobar").disabled = true; $("pComprobar").dataset.fase = "comprobar";
  $("pSaltar").hidden = false;
}

function seleccionar(btn) {
  const r = todos[i];
  if ($("pComprobar").dataset.fase !== "comprobar") return;
  sonar("clic");
  if (r.tipo === "ordenar") {
    if (btn.disabled) return;
    btn.disabled = true; orden.push(Number(btn.dataset.k));
    const arm = $("pArmado");
    arm.querySelector(".p-vacio")?.remove();
    arm.insertAdjacentHTML("beforeend", `<span class="p-puesta">${esc(r.lineas[Number(btn.dataset.k)])}\n</span>`);
    $("pComprobar").disabled = orden.length !== r.lineas.length;
    return;
  }
  document.querySelectorAll(".p-op.sel").forEach((b) => b.classList.remove("sel"));
  btn.classList.add("sel"); elegido = Number(btn.dataset.k);
  if (r.tipo === "completar") $("pHueco").textContent = r.opciones[elegido];
  $("pComprobar").disabled = false;
}

function comprobar(saltado = false) {
  const r = todos[i];
  const bien = !saltado && (r.tipo === "ordenar" ? orden.every((k, n) => k === n) : elegido === r.ok);
  if (bien) { aciertos++; porSeccion[r.si]++; }
  document.querySelectorAll(".p-op").forEach((b) => { b.disabled = true; });
  if (r.tipo !== "ordenar") document.querySelector(`.p-op[data-k="${r.ok}"]`)?.classList.add("ok");
  if (!bien && elegido !== null && r.tipo !== "ordenar") document.querySelector(`.p-op[data-k="${elegido}"]`)?.classList.add("mal");
  $("pPie").className = `p-pie ${bien ? "bien" : "mal"}`;
  $("pMsg").innerHTML = `<b>${bien ? T(["¡Correcto!", "¡Excelente!", "¡Así se hace!", "¡Bien pensado!"][i % 4]) : saltado ? T("Sin problema, lo aprenderás") : T("Casi…")}</b><span>${esc(T(r.porque))}</span>`;
  codi(bien ? "celebra" : saltado ? "feliz" : "triste", bien ? "¡Eso es! 🎉" : "¡Tranqui, para eso estás aquí!");
  if (bien) { sonar("correcto"); saltarCodi?.($("pCodi").querySelector("svg")); vibrar(15); } else { sonar(saltado ? "clic" : "incorrecto"); vibrar([30, 40, 30]); }
  $("pComprobar").textContent = i === todos.length - 1 ? T("Ver mi resultado") : T("Continuar");
  $("pComprobar").disabled = false; $("pComprobar").dataset.fase = "seguir"; $("pSaltar").hidden = true;
}

function resultado() {
  const nivel = [...NIVELES].reverse().find((n) => aciertos >= n.min);
  try { localStorage.setItem("cc_prueba_nivel", nivel.id); localStorage.setItem("cc_prueba", JSON.stringify({ aciertos, total: todos.length, porSeccion, fecha: Date.now() })); } catch { /* nada */ }
  $("pBarra").style.width = "100%";
  $("pSecciones").innerHTML = SECCIONES.map((s, k) => `<li class="hecha"><span>${s.icono}</span><b>${esc(T(s.titulo))}</b></li>`).join("");
  document.body.classList.add("p-final");
  $("pReto").innerHTML = `<div class="p-resultado">
      <div class="p-nivel">${nivel.icono}</div>
      <h2>${esc(T(nivel.titulo))}</h2>
      <p class="p-puntos"><b>${aciertos}</b> / ${todos.length} ${esc(T("retos correctos"))}</p>
      <ul class="p-desglose">${SECCIONES.map((s, k) => `<li><span>${s.icono} ${esc(T(s.titulo))}</span><b>${porSeccion[k]}/${s.retos.length}</b><i style="--p:${(porSeccion[k] / s.retos.length) * 100}%"></i></li>`).join("")}</ul>
      <p>${esc(T(nivel.texto))}</p>
      <a class="btn grad p-crear" href="/pages/registro.html?nivel=${nivel.id}">${esc(T("Crear mi cuenta gratis y guardar mi nivel"))}</a>
      <a class="p-otra" href="/pages/login.html">${esc(T("Ya tengo cuenta"))}</a>
    </div>`;
  $("pReto").classList.remove("entra"); void $("pReto").offsetWidth; $("pReto").classList.add("entra");
  $("pPie").hidden = true;
  codi("celebra", aciertos >= 7 ? "¡Eres un crack! 🚀" : "¡Buen comienzo! Vamos juntos 💪");
  sonar(aciertos >= 10 ? "legendario" : aciertos >= 7 ? "premio" : "leccion");
  const conf = $("pConfeti");
  for (let k = 0; k < 40; k++) {
    const c = document.createElement("i");
    c.style.cssText = `left:${Math.random() * 100}%;background:hsl(${Math.random() * 360} 90% 60%);animation-delay:${Math.random() * 0.6}s;--dx:${(Math.random() - 0.5) * 200}px`;
    conf.appendChild(c);
  }
}

$("pReto").addEventListener("click", (e) => { const b = e.target.closest(".p-op"); if (b) seleccionar(b); });
$("pComprobar").onclick = () => {
  prepararSonido();
  if ($("pComprobar").dataset.fase === "comprobar") return comprobar();
  i++;
  if (i >= todos.length) resultado(); else pintarReto();
};
$("pSaltar").onclick = () => { prepararSonido(); comprobar(true); };
addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !$("pComprobar").disabled && !$("pPie").hidden) { e.preventDefault(); $("pComprobar").click(); return; }
  const n = Number(e.key);
  if (n >= 1 && n <= 9) { const b = document.querySelectorAll(".p-op:not(:disabled)")[n - 1]; if (b) seleccionar(b); }
});
document.addEventListener("pointerdown", prepararSonido, { once: true });
codi("saludo", "¡Hola! Soy Codi. Veamos qué tanto sabes: no hay respuestas malas 😉");
setTimeout(pintarReto, 50);
