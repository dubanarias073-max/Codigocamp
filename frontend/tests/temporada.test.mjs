import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

// Se carga sin el import de Codi (que usa rutas del servidor)
const fuente = readFileSync(new URL("../js/temporada.js", import.meta.url), "utf8").replace(/^import .*$/m, "const ponerAccesorioTemporada = () => {};");
const { temporadaDe, TEMPORADAS } = await import(`data:text/javascript,${encodeURIComponent(fuente)}`);
const en = (m, d) => temporadaDe(new Date(2026, m - 1, d))?.id ?? null;

test("cada fecha tiene su temporada", () => {
  assert.equal(en(12, 24), "navidad");
  assert.equal(en(1, 5), "navidad");
  assert.equal(en(12, 31), "anio_nuevo");
  assert.equal(en(1, 1), "anio_nuevo");
  assert.equal(en(10, 31), "halloween");
  assert.equal(en(9, 13), "programador");
  assert.equal(en(9, 16), "amor_amistad");
  assert.equal(en(2, 14), "san_valentin");
  assert.equal(en(7, 1), "vacaciones");
});

test("fuera de temporada no se decora", () => {
  assert.equal(en(11, 22), null);
  assert.equal(en(4, 10), null);
  assert.ok(TEMPORADAS.every((t) => t.colores.acc && t.particulas.length));
});
