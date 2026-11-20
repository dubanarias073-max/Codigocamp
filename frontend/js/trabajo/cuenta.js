// Clave local de cada cuenta para todo lo que Trabajo guarda en el navegador (copia del proyecto, Git, ajustes).
// No basta con el id: si la base de datos se reinicia, otra persona puede recibir el mismo id en este navegador
// y vería los repositorios y commits de la anterior. Con el correo en la clave, cada cuenta tiene su propio espacio.
function cyrb53(texto, semilla = 7) {
  let h1 = 0xdeadbeef ^ semilla, h2 = 0x41c6ce57 ^ semilla;
  for (let i = 0; i < texto.length; i += 1) {
    const c = texto.charCodeAt(i);
    h1 = Math.imul(h1 ^ c, 2654435761); h2 = Math.imul(h2 ^ c, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36);
}

/** «7_k3j9x2…»: única por cuenta (id + correo), estable entre sesiones. */
export const claveCuenta = (usuario) => `${usuario.id}_${cyrb53(String(usuario.email || "").trim().toLowerCase())}`;
