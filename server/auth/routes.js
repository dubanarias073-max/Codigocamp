import { Router } from "express";
import rateLimit from "express-rate-limit";
import { hashPassword, verifyPassword, signToken } from "./crypto.js";
import { findByEmail, createUser } from "./store.js";
import { SECRET, COOKIE, SESSION_DAYS, isProd } from "./config.js";

const router = Router();

const limiter = rateLimit({
  windowMs: 15 * 60_000,
  limit: 15,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Demasiados intentos. Espera unos minutos." },
});

const cookieOpts = { httpOnly: true, sameSite: "lax", secure: isProd, path: "/" };

function iniciarSesion(res, user) {
  const token = signToken({ sub: user.id }, SECRET, SESSION_DAYS * 86400);
  res.cookie(COOKIE, token, { ...cookieOpts, maxAge: SESSION_DAYS * 86400 * 1000 });
}

const publico = (u) => ({ id: u.id, nombre: u.nombre, email: u.email });
const emailOk = (e) => e.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);

// Contraseña: mínimo 6 caracteres, una mayúscula y un número (máximo 100).
// Debe coincidir con las reglas de public/js/acceso.js y registro.html.
const passwordOk = (p) => p.length >= 6 && p.length <= 100 && /[A-Z]/.test(p) && /\d/.test(p);

router.post("/register", limiter, async (req, res) => {
  const nombre = String(req.body?.nombre ?? "").trim();
  const email = String(req.body?.email ?? "").trim().toLowerCase();
  const password = String(req.body?.password ?? "");

  if (nombre.length < 2 || nombre.length > 50)
    return res.status(400).json({ error: "El nombre debe tener entre 2 y 50 caracteres." });
  if (!emailOk(email)) return res.status(400).json({ error: "Correo electrónico no válido." });
  if (!passwordOk(password))
    return res.status(400).json({
      error: "La contraseña debe tener mínimo 6 caracteres, una mayúscula y un número.",
    });

  try {
    const user = await createUser({ nombre, email, passwordHash: await hashPassword(password) });
    iniciarSesion(res, user);
    res.status(201).json({ user: publico(user) });
  } catch (e) {
    if (e.message === "EMAIL_EXISTS")
      return res.status(409).json({ error: "Ese correo ya está registrado." });
    console.error("Error al registrar:", e.code || e.message);
    res.status(500).json({ error: "No se pudo crear la cuenta." });
  }
});

router.post("/login", limiter, async (req, res) => {
  try {
    const email = String(req.body?.email ?? "").trim().toLowerCase();
    const password = String(req.body?.password ?? "");
    // Evita gastar CPU cifrando textos enormes
    if (!email || !password || password.length > 100)
      return res.status(401).json({ error: "Correo o contraseña incorrectos." });
    const user = await findByEmail(email);
    // Mismo mensaje y mismo trabajo si el correo no existe (no revela qué correos hay).
    const ok = user
      ? await verifyPassword(password, user.passwordHash)
      : (await hashPassword(password), false);
    if (!ok) return res.status(401).json({ error: "Correo o contraseña incorrectos." });
    iniciarSesion(res, user);
    res.json({ user: publico(user) });
  } catch (e) {
    console.error("Error al iniciar sesión:", e.code || e.message);
    res.status(500).json({ error: "No se pudo iniciar sesión." });
  }
});

router.post("/logout", (_req, res) => {
  res.clearCookie(COOKIE, cookieOpts);
  res.json({ ok: true });
});

router.get("/me", (req, res) => {
  res.json({ user: req.user ?? null });
});

export default router;