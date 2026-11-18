// Copia local del proyecto en IndexedDB (cientos de MB) en lugar de localStorage (unos 5 MB por sitio).
// Ofrece la misma interfaz que localStorage (getItem / setItem / removeItem) para que Almacen no cambie:
// se lee todo al abrir la página y cada escritura va a la memoria al instante y a IndexedDB poco después.
// Las demás pestañas se enteran por BroadcastChannel (el evento «storage» solo existe para localStorage).

const BD = "codigocamp-proyectos";

function abrir() {
  return new Promise((ok, mal) => {
    const r = indexedDB.open(BD, 1);
    r.onupgradeneeded = () => r.result.createObjectStore("copias");
    r.onsuccess = () => ok(r.result);
    r.onerror = () => mal(r.error);
  });
}

function operar(bd, modo, fn) {
  return new Promise((ok, mal) => {
    const tx = bd.transaction("copias", modo);
    const req = fn(tx.objectStore("copias"));
    tx.oncomplete = () => ok(req?.result);
    tx.onerror = () => mal(tx.error);
    tx.onabort = () => mal(tx.error);
  });
}

/**
 * @param {string} clave  la clave de este usuario
 * @param {object} o
 * @param {()=>void} [o.alCambiarFuera]  otra pestaña escribió una versión nueva
 * @returns {Promise<{getItem, setItem, removeItem, esperar: ()=>Promise<void>}>}
 */
export async function crearAlmacenamiento(clave, { alCambiarFuera = () => {} } = {}) {
  let bd = null;
  try { bd = await abrir(); } catch { return globalThis.localStorage; } // sin IndexedDB (modo privado antiguo): como antes
  const cache = new Map();
  try {
    const valor = await operar(bd, "readonly", (s) => s.get(clave));
    if (typeof valor === "string") cache.set(clave, valor);
    else {
      // Primera vez: se trae la copia que había en localStorage y se libera ese espacio.
      const viejo = globalThis.localStorage?.getItem(clave);
      if (viejo) { cache.set(clave, viejo); await operar(bd, "readwrite", (s) => s.put(viejo, clave)); globalThis.localStorage.removeItem(clave); }
    }
  } catch { /* se empieza sin copia local */ }

  const canal = typeof BroadcastChannel === "function" ? new BroadcastChannel(`cc-proyecto-${clave}`) : null;
  const yo = Math.random().toString(36).slice(2);
  canal?.addEventListener("message", async (e) => {
    if (e.data?.de === yo) return;
    try { const v = await operar(bd, "readonly", (s) => s.get(clave)); if (typeof v === "string") cache.set(clave, v); } catch { return; }
    alCambiarFuera();
  });

  let cola = Promise.resolve();
  return {
    getItem: (k) => (cache.has(k) ? cache.get(k) : null),
    setItem: (k, v) => {
      cache.set(k, String(v));
      cola = cola.then(() => operar(bd, "readwrite", (s) => s.put(cache.get(k), k))).then(() => canal?.postMessage({ de: yo })).catch(() => {});
    },
    removeItem: (k) => { cache.delete(k); cola = cola.then(() => operar(bd, "readwrite", (s) => s.delete(k))).catch(() => {}); },
    esperar: () => cola,
  };
}

/** Comprime con gzip (para subir proyectos grandes rápido). Devuelve null si el navegador no puede. */
export async function gzip(texto) {
  if (typeof CompressionStream !== "function") return null;
  const flujo = new Blob([texto]).stream().pipeThrough(new CompressionStream("gzip"));
  return new Uint8Array(await new Response(flujo).arrayBuffer());
}
