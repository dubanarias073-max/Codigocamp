import { pool } from "./db.js";

// Convierte una fila de MySQL al formato que usa el resto del código.
const aUsuario = (r) =>
  r ? { id: r.id, nombre: r.nombre, email: r.email, passwordHash: r.password_hash } : null;

export async function findByEmail(email) {
  const [rows] = await pool.execute(
    "SELECT id, nombre, email, password_hash FROM usuarios WHERE email = ? LIMIT 1",
    [email]
  );
  return aUsuario(rows[0]);
}

export async function findById(id) {
  const [rows] = await pool.execute(
    "SELECT id, nombre, email, password_hash FROM usuarios WHERE id = ? LIMIT 1",
    [id]
  );
  return aUsuario(rows[0]);
}

export async function createUser({ nombre, email, passwordHash }) {
  try {
    const [r] = await pool.execute(
      "INSERT INTO usuarios (nombre, email, password_hash) VALUES (?, ?, ?)",
      [nombre, email, passwordHash]
    );
    return { id: r.insertId, nombre, email, passwordHash };
  } catch (e) {
    if (e.code === "ER_DUP_ENTRY") throw new Error("EMAIL_EXISTS");
    throw e;
  }
}
