import { Router } from "express";
import { streamTutor } from "../gemini.js";

const router = Router();

function validar(messages) {
  if (!Array.isArray(messages) || messages.length < 1 || messages.length > 20) return false;
  const ok = messages.every(
    (m) =>
      m && ["user", "assistant"].includes(m.role) &&
      typeof m.content === "string" && m.content.trim().length > 0 && m.content.length <= 4000
  );
  return ok && messages[0].role === "user" && messages.at(-1).role === "user";
}

router.post("/", async (req, res) => {
  const { messages } = req.body ?? {};
  if (!validar(messages)) {
    return res.status(400).json({ error: "Mensaje inválido." });
  }

  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.setHeader("Cache-Control", "no-cache");

  const ac = new AbortController();
  res.on("close", () => ac.abort());

  try {
    const limpios = messages.map(({ role, content }) => ({ role, content }));
    for await (const texto of streamTutor(limpios, ac.signal)) res.write(texto);
    res.end();
  } catch (err) {
    if (ac.signal.aborted) return;
    console.error("Error del tutor:", err.message);
    if (res.headersSent) return res.end();
    if (err.status === 429)
      return res.status(429).json({ error: "El tutor está saturado o llegaste al límite gratuito de Gemini. Prueba en un minuto." });
    res.status(502).json({ error: "El tutor no está disponible ahora." });
  }
});

export default router;
