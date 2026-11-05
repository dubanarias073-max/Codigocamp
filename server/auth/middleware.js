import { verifyToken } from "./crypto.js";
import { findById } from "./store.js";
import { SECRET, COOKIE } from "./config.js";

function parseCookies(header = "") {
  const out = {};
  for (const part of header.split(";")) {
    const i = part.indexOf("=");
    if (i > 0) out[part.slice(0, i).trim()] = decodeURIComponent(part.slice(i + 1).trim());
  }
  return out;
}

// Si hay sesión válida, pone req.user. Si no, sigue como invitado.
export async function attachUser(req, _res, next) {
  try {
    const payload = verifyToken(parseCookies(req.headers.cookie)[COOKIE], SECRET);
    if (payload) {
      const u = await findById(payload.sub);
      if (u) req.user = { id: u.id, nombre: u.nombre, email: u.email };
    }
  } catch { /* invitado */ }
  next();
}
