// Aprende interactivo: cada lección trae su reto (con respuesta) y el error común para el quiz.
import test from "node:test";
import assert from "node:assert/strict";
import { readdirSync } from "node:fs";

const dir = new URL("../js/lecciones/", import.meta.url);
const archivos = readdirSync(dir).filter((f) => f.endsWith(".js") && f !== "salidas.js");

test("todas las lecciones tienen reto con respuesta y error común", async () => {
  let total = 0;
  for (const f of archivos) {
    const lecciones = (await import(new URL(f, dir))).default;
    for (const l of lecciones) {
      total++;
      assert.ok(l.q && String(l.a).trim(), `${f}: «${l.t}» sin reto o sin respuesta`);
      assert.ok(l.f && l.p.length >= 2, `${f}: «${l.t}» sin error común o puntos clave`);
      assert.ok(!l.p.includes(l.f), `${f}: «${l.t}» el error común no puede ser un punto clave`);
    }
  }
  assert.ok(total > 3000);
});
