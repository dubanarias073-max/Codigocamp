import { SYSTEM } from "./prompts.js";

const BASE = process.env.GEMINI_BASE_URL || "https://generativelanguage.googleapis.com/v1beta";

// Envía la conversación a Gemini y va entregando el texto a medida que llega.
export async function* streamTutor(messages, signal) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) throw Object.assign(new Error("Falta GEMINI_API_KEY en el .env"), { status: 500 });
  const model = process.env.GEMINI_MODEL || "gemini-3.6-flash";

  const res = await fetch(
    `${BASE}/models/${encodeURIComponent(model)}:streamGenerateContent?alt=sse`,
    {
      method: "POST",
      signal,
      headers: { "Content-Type": "application/json", "x-goog-api-key": key },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: SYSTEM }] },
        contents: messages.map((m) => ({
          role: m.role === "assistant" ? "model" : "user",
          parts: [{ text: m.content }],
        })),
        generationConfig: { maxOutputTokens: 4096 },
      }),
    }
  );

  if (!res.ok) {
    const detalle = await res.text().catch(() => "");
    throw Object.assign(new Error(`Gemini respondió ${res.status}: ${detalle.slice(0, 300)}`), {
      status: res.status,
    });
  }

  // La respuesta llega como eventos "data: {json}" separados por líneas.
  const dec = new TextDecoder();
  let buf = "";
  for await (const chunk of res.body) {
    buf += dec.decode(chunk, { stream: true });
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trimEnd();
      buf = buf.slice(i + 1);
      if (!line.startsWith("data:")) continue;
      const data = line.slice(5).trim();
      if (!data || data === "[DONE]") continue;
      let j;
      try { j = JSON.parse(data); } catch { continue; }
      const parts = j.candidates?.[0]?.content?.parts ?? [];
      const text = parts.filter((p) => !p.thought).map((p) => p.text ?? "").join("");
      if (text) yield text;
    }
  }
}
