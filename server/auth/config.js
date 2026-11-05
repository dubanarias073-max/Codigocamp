import crypto from "node:crypto";

export const isProd = process.env.NODE_ENV === "production";

let secret = process.env.SESSION_SECRET;
if (!secret) {
  if (isProd) {
    console.error("Falta SESSION_SECRET en producción.");
    process.exit(1);
  }
  secret = crypto.randomBytes(32).toString("hex");
  console.warn("Aviso: SESSION_SECRET no definido. Las sesiones se cerrarán al reiniciar el servidor.");
}
export const SECRET = secret;
export const COOKIE = "cc_session";
export const SESSION_DAYS = 7;
