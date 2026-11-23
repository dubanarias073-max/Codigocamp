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

// Devuelve el usuario con sesión iniciada, o null. También deja lista la cookie csrftoken.
export async function getUser() {
  try { return (await api("/api/auth/me/")).user; } catch { return null; }
}

export const setGuest = (v) => { try { localStorage.setItem("cc_guest", v ? "1" : ""); } catch {} };
export const isGuest = () => { try { return localStorage.getItem("cc_guest") === "1"; } catch { return false; } };
