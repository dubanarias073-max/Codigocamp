import crypto from "node:crypto";

// Contraseñas: scrypt con sal aleatoria (incluido en Node, sin dependencias).
const scrypt = (pw, salt) =>
  new Promise((res, rej) =>
    crypto.scrypt(pw, salt, 64, { N: 16384, r: 8, p: 1 }, (e, k) => (e ? rej(e) : res(k)))
  );

export async function hashPassword(pw) {
  const salt = crypto.randomBytes(16);
  const key = await scrypt(pw, salt);
  return `${salt.toString("hex")}:${key.toString("hex")}`;
}

export async function verifyPassword(pw, stored) {
  const [s, k] = String(stored).split(":");
  if (!s || !k) return false;
  const key = await scrypt(pw, Buffer.from(s, "hex"));
  const known = Buffer.from(k, "hex");
  return key.length === known.length && crypto.timingSafeEqual(key, known);
}

// Sesión: token firmado con HMAC (cuerpo.firma), con caducidad.
export function signToken(payload, secret, ttlSec) {
  const body = Buffer.from(
    JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + ttlSec })
  ).toString("base64url");
  const sig = crypto.createHmac("sha256", secret).update(body).digest("base64url");
  return `${body}.${sig}`;
}

export function verifyToken(token, secret) {
  if (typeof token !== "string") return null;
  const [body, sig] = token.split(".");
  if (!body || !sig) return null;
  const expected = crypto.createHmac("sha256", secret).update(body).digest("base64url");
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try {
    const p = JSON.parse(Buffer.from(body, "base64url").toString());
    return p.exp > Math.floor(Date.now() / 1000) ? p : null;
  } catch {
    return null;
  }
}
