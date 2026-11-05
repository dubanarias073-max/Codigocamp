// Funciones de sesión compartidas por todas las páginas.
const $ = (id) => document.getElementById(id);
const GUEST = "cc_guest";

export const isGuest = () => { try { return sessionStorage.getItem(GUEST) === "1"; } catch { return false; } };
export const setGuest = (v) => { try { v ? sessionStorage.setItem(GUEST, "1") : sessionStorage.removeItem(GUEST); } catch {} };

export async function api(path, body) {
  const res = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Error del servidor");
  return data;
}

export async function getUser() {
  try { return (await api("/api/auth/me")).user; } catch { return null; }
}

function btn(texto, clase, onclick) {
  const b = document.createElement("button");
  b.type = "button"; b.className = clase; b.textContent = texto; b.onclick = onclick;
  return b;
}
function enlace(texto, href, clase, tab) {
  const a = document.createElement("a");
  a.href = href; a.className = clase; a.textContent = texto;
  if (tab) a.dataset.tab = tab;
  return a;
}
function texto(t, clase) {
  const s = document.createElement("span");
  s.className = clase; s.textContent = t;
  return s;
}

// Dibuja los botones de la esquina superior derecha según el estado de sesión.
export function pintarBarra(user, { enIndex = false } = {}) {
  const bar = $("userbar");
  if (!bar) return;
  const cerrar = btn("Cerrar sesión", "btn ghost sm", async () => {
    await api("/api/auth/logout", {}).catch(() => {});
    setGuest(false);
    try { sessionStorage.removeItem("cc_chat"); } catch {}
    location.href = "index.html";
  });
  if (user) {
    const hola = texto(`Hola, ${user.nombre}`, "hola");
    bar.replaceChildren(...(enIndex ? [hola, enlace("Ir a mi panel", "inicio.html", "btn pri sm"), cerrar] : [hola, cerrar]));
  } else if (!enIndex && isGuest()) {
    bar.replaceChildren(texto("Modo invitado", "hola"), enlace("Crear cuenta", "registro.html", "btn pri sm"));
  } else {
    bar.replaceChildren(
      enlace("Iniciar sesión", "login.html", "btn ghost sm"),
      enlace("Registrarse", "registro.html", "btn pri sm")
    );
  }
}

// Para las páginas internas: si no hay sesión ni modo invitado, vuelve al inicio.
export async function exigirAcceso() {
  const user = await getUser();
  if (!user && !isGuest()) {
    location.replace("login.html");
    return { ok: false, user: null };
  }
  pintarBarra(user);
  return { ok: true, user };
}
