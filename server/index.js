import express from "express";
import rateLimit from "express-rate-limit";
import path from "node:path";
import { fileURLToPath } from "node:url";
import tutor from "./routes/tutor.js";
import auth from "./auth/routes.js";
import { attachUser } from "./auth/middleware.js";
import { pool } from "./auth/db.js";

// Comprobar la conexión con MySQL antes de arrancar
try {
  await pool.query("SELECT 1");
} catch (e) {
  console.error(
    `No se pudo conectar a MySQL (${e.code}).\n` +
    "1) ¿Está iniciado MySQL en el panel de XAMPP?\n" +
    "2) ¿Ejecutaste sql/schema.sql en Workbench?\n" +
    "3) Si tu .env tiene DB_USER o DB_PASSWORD, bórralos: con XAMPP por defecto no hacen falta."
  );
  process.exit(1);
}
if (!process.env.GEMINI_API_KEY) console.warn("Aviso: falta GEMINI_API_KEY en el .env; el tutor no responderá.");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.set("trust proxy", 1); // necesario detrás de Render, Railway, etc.
app.use(express.json({ limit: "100kb" }));
app.use(attachUser);

app.use("/api/auth", auth);

// Invitados: pocas preguntas por minuto (por IP). Registrados: más (por cuenta).
const comunes = { windowMs: 60_000, standardHeaders: true, legacyHeaders: false };
const guestLimiter = rateLimit({
  ...comunes, limit: 6, skip: (req) => !!req.user,
  message: { error: "Límite de invitado alcanzado. Regístrate gratis para hacer más preguntas." },
});
const userLimiter = rateLimit({
  ...comunes, limit: 20, skip: (req) => !req.user,
  keyGenerator: (req) => String(req.user.id),
  message: { error: "Demasiadas preguntas. Espera un minuto." },
});

app.use("/api/tutor", guestLimiter, userLimiter, tutor);
app.use(express.static(path.join(__dirname, "..", "public")));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`CódigoCamp en http://localhost:${PORT}`));
