// Privacidad en navegadores compartidos (colegio, sala de cómputo, familia).
// Trabajo guarda una copia del proyecto y del .git en este navegador para ir rápido; la copia buena está en el
// servidor (tu cuenta). Cuando sales, o cuando entra otra cuenta en este navegador, se borran esas copias:
// así nadie que use el mismo computador puede ver tus repositorios, commits o archivos, ni siquiera con DevTools.
import { claveCuenta } from "./trabajo/cuenta.js";

const ULTIMA = "cc_ultima_cuenta";
// Claves de localStorage con datos de la persona (no ajustes neutros como el tema o el sonido).
const PREFIJOS = ["cc_trabajo_", "cc-git-global-", "cc_ia_", "cc_hechas", "cc_codigos_aprende", "cc_cosm"];
// Bases de IndexedDB: copias del proyecto, carpetas vinculadas y el .git (LightningFS crea «cc-git-…» y «…_lock»).
const BASES_FIJAS = ["codigocamp-proyectos", "codigocamp-carpetas"];
const esBaseDeDatos = (n) => BASES_FIJAS.includes(n) || n.startsWith("cc-git-") || n === "fs" || n === "fs_lock";

function borrarBase(nombre) {
  return new Promise((ok) => {
    try {
      const r = indexedDB.deleteDatabase(nombre);
      r.onsuccess = r.onerror = () => ok();
      r.onblocked = () => ok();   // otra pestaña la tiene abierta: se borra en cuanto la cierre
    } catch { ok(); }
  });
}

/** Borra de este navegador todo lo que Trabajo, Aprende e IA guardan de cualquier cuenta. */
export async function borrarDatosLocales() {
  try {
    for (let i = localStorage.length - 1; i >= 0; i -= 1) {
      const k = localStorage.key(i);
      if (k && PREFIJOS.some((p) => k.startsWith(p))) localStorage.removeItem(k);
    }
    localStorage.removeItem(ULTIMA);
  } catch { /* sin localStorage */ }
  if (typeof indexedDB === "undefined") return;
  let nombres = [...BASES_FIJAS];
  try { if (indexedDB.databases) nombres = (await indexedDB.databases()).map((d) => d.name).filter((n) => n && esBaseDeDatos(n)); }
  catch { /* navegador sin indexedDB.databases(): solo las fijas */ }
  await Promise.all([...new Set([...BASES_FIJAS, ...nombres])].map(borrarBase));
}

/**
 * Llamar al entrar a cualquier página con sesión. Si en este navegador estuvo otra cuenta antes,
 * borra sus copias locales antes de que la página lea nada (las de esta cuenta vuelven desde el servidor).
 */
export async function protegerCuenta(usuario) {
  if (!usuario) return;
  const actual = claveCuenta(usuario);
  let anterior = null;
  try { anterior = localStorage.getItem(ULTIMA); } catch { return; }
  if (anterior !== actual) {
    if (anterior !== null || await hayRestosDeOtros(actual)) await borrarDatosLocales();
    try { localStorage.setItem(ULTIMA, actual); } catch { /* nada */ }
  }
}

// Navegadores que ya tenían datos de antes de esta protección: si hay claves de otra cuenta, se limpian.
// Solo cuentan los datos que llevan la clave de una cuenta (Trabajo y Git); con id viejo o de otra persona, se limpia.
const POR_CUENTA = ["cc_trabajo_", "cc-git-global-"];
async function hayRestosDeOtros(actual) {
  try {
    for (let i = 0; i < localStorage.length; i += 1) {
      const k = localStorage.key(i) || "";
      if (POR_CUENTA.some((p) => k.startsWith(p)) && !k.endsWith(`_${actual}`) && !k.endsWith(`-${actual}`)) return true;
    }
  } catch { /* nada */ }
  try {
    if (indexedDB?.databases) for (const { name } of await indexedDB.databases())
      if (name && (name === "fs" || (name.startsWith("cc-git-") && name !== `cc-git-${actual}` && name !== `cc-git-${actual}_lock`))) return true;
  } catch { /* nada */ }
  return false;
}

/** Cierra la sesión y limpia este navegador. `todas`: también en los demás dispositivos. */
export async function salir(api, { todas = false } = {}) {
  try { await api(todas ? "/api/sesiones/cerrar-todas/" : "/api/auth/logout/", {}); } catch { /* igual salimos */ }
  await borrarDatosLocales();
  location.href = "/pages/login.html";
}
