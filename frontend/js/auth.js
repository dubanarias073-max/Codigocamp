// Comunicación con la API Flask (misma dirección, así que las cookies funcionan solas).
const csrf = () => (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
// Zona horaria del dispositivo (p. ej. «America/Bogota»): el servidor cuenta «hoy», la racha y las horas con ella.
export const zonaHoraria = () => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch { return ""; } };

// api(url) hace GET; api(url, datos) hace POST con JSON. Lanza Error con el mensaje del servidor.
export async function api(url, datos, metodo) {
  const r = await fetch(url, {
    method: metodo || (datos === undefined ? "GET" : "POST"),
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrf(), "X-Zona-Horaria": zonaHoraria() },
    body: datos === undefined ? undefined : JSON.stringify(datos),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(d.error || "No se pudo conectar con el servidor."), { estado: r.status, datos: d });
  return d;
}

/** Como api(), pero la respuesta de la IA llega EN VIVO, palabra por palabra: alTexto(textoHastaAhora) en cada trozo.
 *  Devuelve el mismo objeto que api() al terminar. Si el servidor responde de una vez (JSON), funciona igual. */
export async function apiEnVivo(url, datos, alTexto = () => {}, alEvento = () => {}) {
  const r = await fetch(url, {
    method: "POST", credentials: "same-origin",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream", "X-CSRFToken": csrf(), "X-Zona-Horaria": zonaHoraria() },
    body: JSON.stringify({ ...datos, stream: true }),
  });
  if (!(r.headers.get("content-type") || "").includes("event-stream") || !r.body) {
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(d.error || "No se pudo conectar con el servidor."), { estado: r.status, datos: d });
    if (d.respuesta) alTexto(d.respuesta);
    return d;
  }
  const lector = r.body.getReader();   // funciona en todos los navegadores (también Safari viejo y celulares)
  const dec = new TextDecoder();
  let resto = "", texto = "", fin = null;
  for (;;) {
    const { value, done } = await lector.read();
    if (done) break;
    resto += dec.decode(value, { stream: true });
    let i;
    while ((i = resto.indexOf("\n\n")) >= 0) {
      const bloque = resto.slice(0, i); resto = resto.slice(i + 2);
      if (!bloque.startsWith("data:")) continue;
      let ev; try { ev = JSON.parse(bloque.slice(5)); } catch { continue; }
      if (ev.error) throw Object.assign(new Error(ev.error), { servidor: true });
      if (ev.conv) alEvento(ev);   // p. ej. la conversación ya quedó guardada (llega antes que la respuesta)
      if (ev.t) { texto += ev.t; alTexto(texto); }
      if (ev.fin) fin = ev;
    }
  }
  if (!fin) { if (texto) return { respuesta: texto }; throw new Error("La respuesta se cortó. Inténtalo de nuevo."); }
  return fin;
}

// Devuelve el usuario con sesión iniciada, o null. También deja lista la cookie csrftoken.
export async function getUser() {
  try { return (await api("/api/auth/me/")).user; } catch { return null; }
}

export const setGuest = (v) => { try { localStorage.setItem("cc_guest", v ? "1" : ""); } catch {} };
export const isGuest = () => { try { return localStorage.getItem("cc_guest") === "1"; } catch { return false; } };
