// Lógica de tienda.html: cosméticos (fondos, punteros, temas, marcos, efectos) con vista previa en vivo, potenciadores y tu colección.
import { iniciar, api, esc, aviso, actualizarStats, aplicarCosmeticos } from "/js/app.js";
import { sonar } from "/js/sonidos.js";
import { iconoSVG } from "/js/iconos.js";
import { vistaPrevia } from "/js/cosmeticos.js";
import { escenaArticulo } from "/js/escenas-tienda.js";
const { user } = await iniciar("tienda");
const $ = (id) => document.getElementById(id);
const RAREZA = { comun: "Común", raro: "Raro", epico: "Épico", legendario: "Legendario" };
const COSMETICO = new Set(["fondo", "cursor", "tema", "marco", "efecto", "dedo", "codi"]);
const TACTIL = matchMedia("(pointer: coarse)").matches;
const AYUDA = {
  fondo: "El fondo se ve detrás de todas las páginas. Prueba cómo queda con «Probar».",
  cursor: TACTIL ? "Los punteros se ven cuando usas mouse (en el computador). Cada uno trae 3: normal, mano (enlaces y botones) y texto (para escribir). En el celular prueba los «Rastros»." : "Cada puntero trae 3: normal, mano (enlaces y botones) y texto (para escribir). Pasa el mouse por cada uno para probarlo.",
  tema: "Cambia el color de botones, barras y enlaces en todo CódigoCamp.",
  marco: "Un aro alrededor de tu foto de perfil: se ve en tu perfil, en los chats y en la barra lateral.",
  efecto: "Haz clic en la vista previa para ver el efecto.",
  dedo: "Rastros: siguen tu mouse en el computador y tu dedo en el celular (también mientras desplazas la pantalla). Pruébalos moviendo el mouse o deslizando el dedo sobre cada tarjeta.",
  codi: "Viste a Codi, la mascota: el accesorio que te pongas lo lleva en el menú, en los retos, en el ícono de IA y en toda la página. Pulsa «Probar» para verlo en vivo.",
  potenciador: "Vidas, salvarrachas, XP y cofres sorpresa.",
  coleccion: "Todo lo que tienes. Ponte o quítate cada cosmético cuando quieras. Los exclusivos salen de los cofres de Recompensas.",
};
let saldo = 0, items = [], equipados = { ...(user.cosmeticos || {}) }, catalogo = [], tab = "fondo", probando = null;
{ const h = location.hash.slice(1); if (h && document.querySelector(`#tabs [data-t="${CSS.escape(h)}"]`)) tab = h; }   // /tienda.html#potenciador

function boton(i) {
  const iconoMoneda = iconoSVG("diamante", "icono-moneda");
  if (COSMETICO.has(i.tipo) && i.tuyo) {
    const puesto = equipados[i.tipo] === i.clave;
    return `<button class="bj${puesto ? " puesto" : ""}" type="button" data-equipar="${esc(i.clave)}" data-tipo="${i.tipo}">${puesto ? `${iconoSVG("check", "btn-ic")} Puesto · quitar` : "Ponérmelo"}</button>`;
  }
  if (i.tuyo) return `<button class="bj" type="button" disabled>${iconoSVG("check", "btn-ic")} En tu colección</button>`;
  if (i.exclusivo) return `<button class="bj" type="button" disabled>${iconoSVG("cofre", "btn-ic")} Solo en cofres</button>`;
  const falta = i.precio - saldo;
  if (falta > 0) return `<button class="bj" type="button" disabled>${iconoMoneda} ${i.precio} · te faltan ${falta}</button>`;
  return `<button class="bj" type="button" data-c="${esc(i.clave)}">${iconoMoneda} ${i.precio} diamantes</button>`;
}

function tarjeta(i) {
  const cos = COSMETICO.has(i.tipo);
  return `<div class="tarjeta producto rareza-${esc(i.rareza)}${i.tuyo ? " tuyo" : ""}${cos ? " cosmetico" : ""}" data-clave="${esc(i.clave)}" data-tipo="${esc(i.tipo)}">
    <span class="producto-rango">${esc(RAREZA[i.rareza] || "Común")}</span>
    ${cos ? `<div class="vista vista-${i.tipo}" data-prev="${esc(i.clave)}"></div>` : (escenaArticulo(i.clave, "potenciador") ? `<div class="vista vista-potenciador cc-prev-escena">${escenaArticulo(i.clave, "potenciador")}</div>` : `<span class="ic ic-${esc(i.rareza)}">${iconoSVG(i.clave, "producto-icon")}</span>`)}
    <h3>${esc(i.nombre)}</h3><small>${esc(i.descripcion)}</small>
    ${cos && !["cursor", "efecto", "dedo"].includes(i.tipo) ? `<button type="button" class="probar" data-probar="${esc(i.clave)}" data-tipo="${i.tipo}">${probando?.clave === i.clave ? "Dejar de probar" : "Probar"}</button>` : ""}
    ${boton(i)}</div>`;
}

document.querySelectorAll("#tabs [data-ic]").forEach((el) => { el.innerHTML = iconoSVG(el.dataset.ic, "tab-svg"); });
// Lo más caro (y bacano) primero dentro de cada pestaña.
const ORDEN_RAREZA = { legendario: 0, epico: 1, raro: 2, comun: 3 };
const porValor = (a, b) => (ORDEN_RAREZA[a.rareza] ?? 4) - (ORDEN_RAREZA[b.rareza] ?? 4) || (b.precio || 0) - (a.precio || 0);
function pintar() {
  document.querySelectorAll("#tabs [data-t]").forEach((b) => { b.classList.toggle("on", b.dataset.t === tab); b.setAttribute("aria-selected", b.dataset.t === tab); });
  $("ayudaTab").textContent = AYUDA[tab];
  let lista;
  if (tab === "coleccion") lista = catalogo.filter((c) => c.tuyo);
  else if (tab === "potenciador") lista = items.filter((i) => i.tipo === "potenciador" || i.tipo === "cofre");
  else {
    const enTienda = items.filter((i) => i.tipo === tab);
    const exclusivos = catalogo.filter((c) => c.tipo === tab && c.exclusivo).map((c) => ({ ...c, tipo: c.tipo }));
    lista = [...enTienda, ...exclusivos];
  }
  if (tab !== "coleccion") lista.sort(porValor);
  $("items").innerHTML = lista.length ? lista.map(tarjeta).join("") : '<p class="nota">Aún no tienes cosméticos. ¡Compra el primero o abre un cofre en Recompensas!</p>';
  $("items").querySelectorAll("[data-prev]").forEach((el) => vistaPrevia(el, el.dataset.prev, el.closest(".producto").dataset.tipo));
}

async function cargar() {
  const [t, c] = await Promise.all([api("/api/tienda/"), api("/api/cosmeticos/")]);
  saldo = t.minerales.diamante;
  equipados = c.equipados;
  catalogo = c.catalogo;
  const tuyos = new Set(catalogo.filter((x) => x.tuyo).map((x) => x.clave));
  items = t.items.map((i) => ({ ...i, tuyo: i.tuyo || tuyos.has(i.clave) }));
  $("iconoSaldo").innerHTML = iconoSVG("diamante", "icono-moneda");
  $("saldo-diamante").textContent = saldo;
  pintar();
}

function confeti() {
  const colores = ["#55d8ff", "#9d75ff", "#ffcb68", "#ff6e9c", "#72e0a3"];
  for (let n = 0; n < 26; n++) {
    const s = document.createElement("span");
    s.className = "confeti";
    s.style.cssText = `--confeti-color:${colores[n % colores.length]};left:${Math.random() * 100}vw;animation-delay:${Math.random() * .5}s;--confeti-tamano:${5 + Math.random() * 8}px`;
    document.body.appendChild(s);
    setTimeout(() => s.remove(), 2600);
  }
}

function mostrarCofre(clave, nombre, premio, cosmetico) {
  const caja = $("cofreCaja");
  caja.innerHTML = `<div class="cofre-ic">${cosmetico ? `<div class="vista vista-${cosmetico}" id="cofrePrev"></div>` : iconoSVG(clave, "producto-icon")}</div><h2>${esc(nombre)}</h2>
    <p class="cofre-prem">${premio ? esc(premio) : "¡Ya es tuyo!"}</p>
    <div class="cofre-btns">${cosmetico ? `<button class="btn pri" type="button" id="cofrePoner">Ponérmelo ya</button>` : ""}<button class="btn" type="button" id="cofreOk">¡Genial!</button></div>`;
  if (cosmetico) vistaPrevia($("cofrePrev"), clave, cosmetico);
  $("cofreFondo").hidden = false;
  $("cofreOk").focus();
  $("cofreOk").onclick = () => { $("cofreFondo").hidden = true; };
  if (cosmetico) $("cofrePoner").onclick = async () => { $("cofreFondo").hidden = true; await equipar(clave, cosmetico, true); };
}

async function equipar(clave, tipo, poner) {
  try {
    const r = await api("/api/cosmeticos/equipar/", { tipo, clave: poner ? clave : null });
    equipados = r.equipados;
    probando = null;
    aplicarCosmeticos(equipados);
    sonar(poner ? "equipar" : "clic");
    aviso(poner ? "¡Listo! Ya lo tienes puesto en todo CódigoCamp." : "Quitado.");
    pintar();
  } catch (x) { aviso(x.message, true); }
}

$("items").onclick = async (e) => {
  const pr = e.target.closest("[data-probar]");
  if (pr) {
    const { probar: clave, tipo } = pr.dataset;
    if (probando?.clave === clave) { probando = null; aplicarCosmeticos(equipados); }
    else { probando = { clave, tipo }; aplicarCosmeticos({ ...equipados, [tipo]: clave }); aviso("Vista previa: así se vería. Vuelve a pulsar para dejar de probar."); }
    pintar();
    return;
  }
  const eq = e.target.closest("[data-equipar]");
  if (eq) return equipar(eq.dataset.equipar, eq.dataset.tipo, equipados[eq.dataset.tipo] !== eq.dataset.equipar);
  const b = e.target.closest("[data-c]");
  if (!b) return;
  b.disabled = true;
  const card = b.closest(".producto");
  const nombre = card?.querySelector("h3")?.textContent || "";
  try {
    const r = await api("/api/tienda/comprar/", { clave: b.dataset.c });
    import("/js/sonidos.js").then(({ sonar }) => sonar("moneda")).catch(() => {});
    confeti();
    const tipo = card?.dataset.tipo;
    if (COSMETICO.has(tipo)) mostrarCofre(b.dataset.c, nombre, "¡Nuevo cosmético en tu colección!", tipo);
    else if (r.premio || card?.classList.contains("rareza-epico") || card?.classList.contains("rareza-legendario")) mostrarCofre(b.dataset.c, nombre, r.premio);
    else aviso("¡Compra hecha!");
    actualizarStats(await api("/api/progreso/"));
  } catch (x) { aviso(x.message, true); }
  try { await cargar(); } catch (x) { aviso(x.message, true); }
};
$("tabs").onclick = (e) => { const b = e.target.closest("[data-t]"); if (!b) return; tab = b.dataset.t; if (probando) { probando = null; aplicarCosmeticos(equipados); } pintar(); };
$("cofreFondo").onclick = (e) => { if (e.target.id === "cofreFondo") $("cofreFondo").hidden = true; };
addEventListener("keydown", (e) => { if (e.key === "Escape") $("cofreFondo").hidden = true; });
addEventListener("pagehide", () => { if (probando) aplicarCosmeticos(equipados); });
try { await cargar(); } catch (x) { aviso(x.message, true); }
