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

/** Busca en el servidor cuáles contactos tienen cuenta. Devuelve { encontrados: [...], otros: [...] }. */
export async function cruzarContactos(contactos, api) {
  const porHuella = new Map();
  for (const c of contactos) for (const e of c.email || []) if (/@/.test(e)) porHuella.set(huellaCorreo(e), c);
  let resultados = [];
  if (porHuella.size) resultados = (await api("/api/amigos/contactos/", { hashes: [...porHuella.keys()].slice(0, 1000) })).resultados || [];
  const conCuenta = new Set(resultados.map((r) => porHuella.get(r.hash)));
  const encontrados = resultados.map((r) => ({ ...r, contacto: porHuella.get(r.hash)?.nombre || "" }));
  const otros = contactos.filter((c) => !conCuenta.has(c) && ((c.tel || []).length || (c.email || []).length));
  return { encontrados, otros };
}

/** Enlaces para invitar a un contacto: SMS, WhatsApp y correo. */
export function enlacesInvitacion(contacto, enlace) {
  const texto = `¡Aprende a programar conmigo en CódigoCamp! Agrégame aquí: ${enlace}`;
  const tel = (contacto.tel || [])[0]?.replace(/[^\d+]/g, "");
  const correo = (contacto.email || [])[0];
  return {
    sms: tel ? `sms:${tel}?body=${encodeURIComponent(texto)}` : null,
    whatsapp: tel ? `https://wa.me/${tel.replace(/^\+/, "")}?text=${encodeURIComponent(texto)}` : null,
    correo: correo ? `mailto:${correo}?subject=${encodeURIComponent("Te invito a CódigoCamp")}&body=${encodeURIComponent(texto)}` : null,
    texto,
  };
}
