import test from "node:test";
import assert from "node:assert/strict";
import { ClienteArchivos, leerMarcador } from "../js/trabajo/archivos.js";

test("modo equipo: subir/blob/enlaces no tocan el servidor de la nube", async () => {
  let llamadas = 0;
  const c = new ClienteArchivos({ fetchFn: async () => { llamadas++; throw new Error("no debería llamar"); }, csrf: () => "x", usarXhr: false });
  c.modoLocal(true);
  const png = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 1, 2, 3, 4]);
  const marca = await c.subir(png, { nombre: "logo.png" });
  const m = leerMarcador(marca);
  assert.equal(m.tipo, "image/png");
  assert.equal(m.tamano, png.length);
  const b = await c.blob(marca);
  assert.deepEqual(new Uint8Array(await b.arrayBuffer()), png);
  const enl = await c.enlaces({ files: { "logo.png": marca, "a.txt": "hola" } });
  assert.ok(enl.get(m.hash).startsWith("data:image/png;base64,"));
  assert.equal(llamadas, 0);
  c.modoLocal(false);
  assert.equal(c.local, null);
});
