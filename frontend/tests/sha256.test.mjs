import test from "node:test";
import assert from "node:assert/strict";
import { createHash, randomBytes } from "node:crypto";
import { Sha256, sha256Blob } from "../js/trabajo/sha256.js";

test("SHA-256 por partes coincide con el de node para muchos tamaños y cortes", async () => {
  for (const n of [0, 1, 55, 56, 63, 64, 65, 119, 120, 1000, 100_003]) {
    const d = new Uint8Array(randomBytes(n));
    const esperado = createHash("sha256").update(d).digest("hex");
    const s = new Sha256();
    for (let i = 0; i < n; i += 37) s.actualizar(d.subarray(i, i + 37));
    assert.equal(s.hex(), esperado, `n=${n}`);
    assert.equal(await sha256Blob(new Blob([d])), esperado);
  }
});
