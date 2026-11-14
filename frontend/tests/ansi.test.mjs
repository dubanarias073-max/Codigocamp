import test from "node:test";
import assert from "node:assert/strict";
import { RenderAnsi, quitarAnsi, color } from "../js/trabajo/ansi.js";

test("colores, negrita, reinicio y escape de HTML", () => {
  const r = new RenderAnsi();
  assert.equal(r.render("a<b"), "a&lt;b");
  assert.equal(r.render("\x1b[1;34mhola\x1b[0m fin"), '<span class="a-b a-bold">hola</span> fin');
  assert.equal(r.render("\x1b[91mx\x1b[m"), '<span class="a-br">x</span>');
});
test("el estilo se conserva entre trozos", () => {
  const r = new RenderAnsi();
  r.render("\x1b[32m");
  assert.equal(r.render("verde"), '<span class="a-g">verde</span>');
  r.render("\x1b[0m");
  assert.equal(r.render("normal"), "normal");
});
test("quitarAnsi y descarta otras secuencias de control", () => {
  assert.equal(quitarAnsi(color.rojo("x")), "x");
  assert.equal(new RenderAnsi().render("a\x1b[2Kb"), "ab");
});
