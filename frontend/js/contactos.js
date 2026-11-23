// Contactos del teléfono → quién ya está en CódigoCamp y a quién invitar.
//  · App de Android: pide el permiso de contactos (puente CodigoCampApp.pedirContactos).
//  · Chrome en Android: selector de contactos del sistema (navigator.contacts.select).
// Privacidad: al servidor solo llega el sha256 de cada correo; nombres y teléfonos nunca salen del dispositivo.
import { Sha256 } from "./trabajo/sha256.js";

const enApp = () => typeof window.CodigoCampApp?.pedirContactos === "function";
const enNavegador = () => "contacts" in navigator && "select" in (navigator.contacts || {});

export const puedeLeerContactos = () => enApp() || enNavegador();

/** Huella de un correo (en minúsculas y sin espacios), igual que la calcula el servidor. */
export function huellaCorreo(correo) {
  const s = new Sha256();
  s.actualizar(new TextEncoder().encode(String(correo).trim().toLowerCase()));
  return s.hex();
}

/** Devuelve [{ nombre, email: [], tel: [] }] o lanza un Error con un mensaje para mostrar. */
export function leerContactos() {
  if (enApp()) {
    return new Promise((ok, ko) => {
      const fin = setTimeout(() => { window.ccContactosApp = null; ko(new Error("El teléfono no respondió. Inténtalo otra vez.")); }, 60000);
      window.ccContactosApp = (r) => {
        clearTimeout(fin); window.ccContactosApp = null;
        if (r && r.error) ko(new Error(r.error === "permiso" ? "Sin permiso para ver tus contactos. Puedes darlo en Ajustes del teléfono → Apps → CódigoCamp → Permisos." : r.error));
        else ok(Array.isArray(r) ? r : []);
      };
      window.CodigoCampApp.pedirContactos();
    });
  }
  if (enNavegador()) {
    return navigator.contacts.select(["name", "email", "tel"], { multiple: true })
      .then((lista) => lista.map((c) => ({ nombre: (c.name || [])[0] || "", email: c.email || [], tel: c.tel || [] })));
  }
  return Promise.reject(new Error("Tu navegador no permite elegir contactos. Copia tu enlace de invitación y compártelo."));
}

const sinTildes = (t) => String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, " ").trim();
const digitos = (t) => String(t || "").replace(/\D/g, "");

/** El teléfono guarda a la misma persona varias veces (cuenta de Google, SIM, WhatsApp…): se juntan en una sola,
 *  por mismo número (últimos 10 dígitos), mismo correo o mismo nombre. */
export function unirContactos(lista) {
  const grupos = [];
  const indice = new Map();   // clave → grupo
  for (const c of lista || []) {
    const tels = [...new Set((c.tel || []).map(digitos).filter((t) => t.length >= 7))];
    const correos = [...new Set((c.email || []).map((e) => String(e).trim().toLowerCase()).filter((e) => e.includes("@")))];
    const nombre = String(c.nombre || "").trim();
    const claves = [...tels.map((t) => "t:" + t.slice(-10)), ...correos.map((e) => "e:" + e), ...(nombre ? ["n:" + sinTildes(nombre)] : [])];
    let g = claves.map((k) => indice.get(k)).find(Boolean);
    if (!g) { g = { nombre, tel: [], email: [], _t: new Set(), _e: new Set() }; grupos.push(g); }
    if (!g.nombre && nombre) g.nombre = nombre;
    for (const t of c.tel || []) { const k = digitos(t).slice(-10); if (k.length >= 7 && !g._t.has(k)) { g._t.add(k); g.tel.push(String(t).trim()); } }
    for (const e of correos) if (!g._e.has(e)) { g._e.add(e); g.email.push(e); }
    for (const k of claves) indice.set(k, g);
  }
  return grupos.filter((g) => g.nombre || g.tel.length || g.email.length).map(({ _t, _e, ...g }) => g)
    .sort((a, b) => sinTildes(a.nombre).localeCompare(sinTildes(b.nombre)));
}

/** Código de país según el idioma/región del teléfono (para números guardados sin +). */
const PAISES = { CO: "57", MX: "52", AR: "54", CL: "56", PE: "51", EC: "593", VE: "58", ES: "34", US: "1", BO: "591", PY: "595", UY: "598",
  GT: "502", CR: "506", PA: "507", DO: "1", HN: "504", SV: "503", NI: "505", CU: "53", PR: "1", BR: "55" };
function codigoPais() {
  for (const l of [...(navigator.languages || []), navigator.language]) {
    const r = /-([A-Z]{2})$/i.exec(l || ""); if (r && PAISES[r[1].toUpperCase()]) return PAISES[r[1].toUpperCase()];
  }
  return "57";
}
/** Número en formato internacional sin + (lo que pide WhatsApp): "300 123 4567" → "573001234567". */
export function telInternacional(tel, pais = codigoPais()) {
  const crudo = String(tel || "").trim();
  let d = digitos(crudo);
  if (!d) return "";
  if (crudo.startsWith("+")) return d;
  if (d.startsWith("00")) return d.slice(2);
  d = d.replace(/^0+/, "");
  return d.startsWith(pais) && d.length > 10 ? d : pais + d;
}

/** Busca en el servidor cuáles contactos tienen cuenta. Devuelve { encontrados: [...], otros: [...] }. */
export async function cruzarContactos(contactos, api) {
  contactos = unirContactos(contactos);
  const porHuella = new Map();
  for (const c of contactos) for (const e of c.email || []) if (/@/.test(e)) porHuella.set(huellaCorreo(e), c);
  let resultados = [];
  if (porHuella.size) resultados = (await api("/api/amigos/contactos/", { hashes: [...porHuella.keys()].slice(0, 1000) })).resultados || [];
  const conCuenta = new Set(resultados.map((r) => porHuella.get(r.hash)));
  const vistos = new Set();   // la misma cuenta puede salir por varios correos del contacto
  const encontrados = resultados.filter((r) => !vistos.has(r.alias) && vistos.add(r.alias)).map((r) => ({ ...r, contacto: porHuella.get(r.hash)?.nombre || "" }));
  const otros = contactos.filter((c) => !conCuenta.has(c) && ((c.tel || []).length || (c.email || []).length));
  return { encontrados, otros };
}

/** Enlaces para invitar a un contacto: SMS, WhatsApp y correo. */
export function enlacesInvitacion(contacto, enlace) {
  const texto = `¡Aprende a programar conmigo en CódigoCamp! Agrégame aquí: ${enlace}`;
  const tel = (contacto.tel || [])[0];
  const intl = tel ? telInternacional(tel) : "";
  const correo = (contacto.email || [])[0];
  // iOS usa «&body=» y Android «?body=»
  const ios = /iPhone|iPad|iPod/.test(navigator.userAgent || "");
  return {
    sms: intl ? `sms:+${intl}${ios ? "&" : "?"}body=${encodeURIComponent(texto)}` : null,
    whatsapp: intl ? `https://wa.me/${intl}?text=${encodeURIComponent(texto)}` : null,
    correo: correo ? `mailto:${correo}?subject=${encodeURIComponent("Te invito a CódigoCamp")}&body=${encodeURIComponent(texto)}` : null,
    texto,
  };
}
