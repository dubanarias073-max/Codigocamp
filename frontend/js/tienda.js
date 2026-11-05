// Lógica de tienda.html
import { iniciar, api, esc, aviso, actualizarStats } from "/js/app.js";
await iniciar("tienda");
const $ = (id) => document.getElementById(id);
const moneda = { diamante: { icono: "💎", nombre: "diamantes" } };
const RAREZA = { comun: "Común", raro: "Raro", epico: "Épico", legendario: "Legendario" };
const COFRES = new Set(["cofre_misterioso", "cofre_legendario"]);
let saldo = {};

function tarjeta(i) {
  const tipo = moneda.diamante;
  const tengo = saldo.diamante ?? 0;
  const falta = i.precio - tengo;
  let boton;
  if (i.tuyo) boton = `<button class="bj" type="button" disabled>✓ En tu colección</button>`;
  else if (falta > 0) boton = `<button class="bj" type="button" disabled>${tipo.icono} ${i.precio} · te faltan ${falta}</button>`;
  else boton = `<button class="bj" type="button" data-c="${esc(i.clave)}">${tipo.icono} ${i.precio} ${tipo.nombre}</button>`;
  const etq = i.permanente ? "Colección" : (COFRES.has(i.clave) ? "Sorpresa" : "Un uso");
  return `<div class="tarjeta producto producto-${esc(i.categoria)} rareza-${esc(i.rareza)}${i.tuyo ? " tuyo" : ""}">
    <span class="producto-rango">${esc(RAREZA[i.rareza] || "Común")}</span>
    <span class="ic">${esc(i.icono)}</span><h3>${esc(i.nombre)}</h3>
    <small>${esc(i.descripcion)}</small>
    <em class="etq-tipo">${etq}</em>${boton}</div>`;
}

async function cargar() {
  const t = await api("/api/tienda/");
  saldo = t.minerales;
  $("saldo-diamante").textContent = t.minerales.diamante;
  $("items").innerHTML = t.items.map(tarjeta).join("");
}

// Lluvia de confeti al comprar
function confeti(emojis) {
  for (let n = 0; n < 26; n++) {
    const s = document.createElement("span");
    s.className = "confeti";
    s.textContent = emojis[n % emojis.length];
    s.style.cssText = `left:${Math.random() * 100}vw;animation-delay:${Math.random() * .5}s;font-size:${18 + Math.random() * 18}px`;
    document.body.appendChild(s);
    setTimeout(() => s.remove(), 2600);
  }
}

function mostrarCofre(item, premio) {
  const caja = $("cofreCaja");
  caja.innerHTML = `<div class="cofre-ic">${esc(item.icono)}</div><h2>${esc(item.nombre)}</h2>
    ${premio ? `<p class="cofre-prem">${esc(premio)}</p>` : `<p class="cofre-prem">¡Ya es tuyo!</p>`}
    <button class="btn pri" type="button" id="cofreOk">¡Genial!</button>`;
  $("cofreFondo").hidden = false;
  $("cofreOk").focus();
  $("cofreOk").onclick = () => { $("cofreFondo").hidden = true; };
}

async function comprar(e) {
  const b = e.target.closest("[data-c]");
  if (!b) return;
  b.disabled = true;
  const item = [...document.querySelectorAll(".producto")].find((x) => x.contains(b));
  const icono = item?.querySelector(".ic")?.textContent || "💎";
  const nombre = item?.querySelector("h3")?.textContent || "";
  try {
    const r = await api("/api/tienda/comprar/", { clave: b.dataset.c });
    confeti([icono, "💎", "✨"]);
    if (r.premio || COFRES.has(b.dataset.c) || item?.classList.contains("rareza-epico") || item?.classList.contains("rareza-legendario")) {
      mostrarCofre({ icono, nombre }, r.premio);
    } else aviso("¡Compra hecha!");
    actualizarStats(await api("/api/progreso/"));
  } catch (x) { aviso(x.message, true); }
  try { await cargar(); } catch (x) { aviso(x.message, true); }
}
$("items").onclick = comprar;
$("cofreFondo").onclick = (e) => { if (e.target.id === "cofreFondo") $("cofreFondo").hidden = true; };
addEventListener("keydown", (e) => { if (e.key === "Escape") $("cofreFondo").hidden = true; });
try { await cargar(); } catch (x) { aviso(x.message, true); }
