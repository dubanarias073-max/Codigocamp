// Registro de puertos de Trabajo, como el panel PUERTOS de VS Code.
// Cada servidor que se enciende (FastAPI/Flask/Django, Node/Express, PHP, servidores estáticos, Expo, contenedores
// de Docker…) se registra aquí con su puerto; la vista previa le manda las peticiones a http://localhost:<puerto>.
//   registro = { puerto, url, framework, comando?, pedir?(req) → {status, headers, body}, externo?: "https://…",
//                detener?(), inicio }

/** Servidores encendidos: puerto → registro */
export const servidores = new Map();
const oyentes = new Set();
export const alCambiarServidores = (fn) => { oyentes.add(fn); return () => oyentes.delete(fn); };
export const avisar = () => oyentes.forEach((fn) => { try { fn(servidores); } catch { /* nada */ } });

/** Registra un servidor (si el puerto estaba ocupado, devuelve false: «EADDRINUSE»). */
export function registrarServidor(puerto, datos) {
  puerto = Number(puerto);
  if (servidores.has(puerto)) return false;
  servidores.set(puerto, { puerto, url: `http://localhost:${puerto}`, inicio: Date.now(), ...datos });
  avisar();
  return true;
}
export function quitarServidor(puerto, registro) {
  puerto = Number(puerto);
  if (registro && servidores.get(puerto) !== registro) return;
  if (servidores.delete(puerto)) avisar();
}
/** Detiene el servidor de un puerto (como «Detener» en el panel PUERTOS o Ctrl+C en su terminal). */
export function detenerServidor(puerto) {
  const s = servidores.get(Number(puerto));
  if (!s) return false;
  try { s.detener?.(); } catch { /* nada */ }
  quitarServidor(puerto, s);
  return true;
}
export function puertoLibre(desde = 3000) {
  let p = Number(desde) || 3000;
  while (servidores.has(p)) p += 1;
  return p;
}

// Cambios del proyecto (los usan nodemon / node --watch / servidores con recarga)
const alCambio = new Set();
export const alCambiarProyecto = (fn) => { alCambio.add(fn); return () => alCambio.delete(fn); };
export function cambioProyecto(origen) { for (const s of servidores.values()) s.sucio = true; alCambio.forEach((fn) => { try { fn(origen); } catch { /* nada */ } }); }

/** Espera hasta Ctrl+C (o hasta que se detenga desde el panel PUERTOS). */
export function esperarDetencion(senal, puerto) {
  return new Promise((listo) => {
    const s = servidores.get(Number(puerto));
    if (s) { const antes = s.detener; s.detener = () => { try { antes?.(); } catch { /* nada */ } listo(); }; }
    if (!senal) return;
    if (senal.aborted) listo(); else senal.addEventListener("abort", listo, { once: true });
  });
}
