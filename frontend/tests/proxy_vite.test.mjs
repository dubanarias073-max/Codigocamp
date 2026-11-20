import test from "node:test";
import assert from "node:assert/strict";
import { proxyDeVite } from "../js/trabajo/modulos.js";
import { puenteDeProyecto } from "../js/trabajo/vista.js";

test("lee server.proxy de vite.config.js (texto y objeto con rewrite)", () => {
  const py = { folders: [], files: {
    "frontend/vite.config.js": "export default defineConfig({ server: { allowedHosts: true, // o ['.trycloudflare.com']\n proxy: { '/api': 'http://127.0.0.1:8000', '/legacy': 'http://127.0.0.1:8000' } } })",
    "b/vite.config.ts": "export default { server: { proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true, rewrite: (p) => p.replace(/^\\/api/, '') } } } }",
  } };
  assert.deepEqual(proxyDeVite(py, "frontend").map((r) => [r.p, r.d]).sort(), [["/api", "http://127.0.0.1:8000"], ["/legacy", "http://127.0.0.1:8000"]]);
  assert.deepEqual(proxyDeVite(py, "b"), [{ p: "/api", d: "http://localhost:8000", q: "^\\/api", s: "" }]);
  assert.deepEqual(proxyDeVite(py, "sin-config"), []);
});

test("el puente de la vista previa lleva las reglas y no rompe con caracteres raros", () => {
  const js = puenteDeProyecto([{ p: "/api", d: "http://127.0.0.1:8000" }]);
  assert.match(js, /"\/api"/);
  assert.doesNotThrow(() => new Function(js));
});
