// Comunicación con la API Flask (misma dirección, así que las cookies funcionan solas).
const csrf = () => (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";

// api(url) hace GET; api(url, datos) hace POST con JSON. Lanza Error con el mensaje del servidor.
export async function api(url, datos) {
  const r = await fetch(url, {
    method: datos === undefined ? "GET" : "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
    body: datos === undefined ? undefined : JSON.stringify(datos),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || "No se pudo conectar con el servidor.");
  return d;
}

// Devuelve el usuario con sesión iniciada, o null. También deja lista la cookie csrftoken.
export async function getUser() {
  try { return (await api("/api/auth/me/")).user; } catch { return null; }
}

export const setGuest = (v) => { try { localStorage.setItem("cc_guest", v ? "1" : ""); } catch {} };
export const isGuest = () => { try { return localStorage.getItem("cc_guest") === "1"; } catch { return false; } };
