// Revisión de errores sin servidor ni conexión (celular sin internet ni Conector).
import { test } from "node:test";
import assert from "node:assert/strict";
import { analizarLocal } from "../js/trabajo/analisis-local.js";

const msgs = (t, l) => analizarLocal(t, l).map((p) => `${p.linea}:${p.mensaje}`);

test("Python: varios errores a la vez (paréntesis, corchetes y «:»)", () => {
  const m = msgs('def saludo(nombre)\n    print("hola" + nombre\nx = [1, 2\n', "python");
  assert.ok(m.some((x) => x.startsWith("1:Falta «:»")));
  assert.ok(m.some((x) => x.startsWith("2:Falta cerrar este «(»")));
  assert.ok(m.some((x) => x.startsWith("3:Falta cerrar este «[»")));
});

test("Python: sangría y comillas", () => {
  assert.deepEqual(msgs('if x > 1:\nprint("a")\n', "python"), ["2:Falta sangría: esta línea va dentro del if de la línea 1 (agrega 4 espacios)"]);
  assert.deepEqual(msgs('t = "sin cerrar\n', "python"), ['1:Falta cerrar las comillas "']);
});

test("Python correcto no marca nada (listas en varias líneas, lambda, textos largos, comentarios)", () => {
  const ok = 'datos = [\n  1,\n  2,\n]\nif (a and\n    b):\n    pass\nf = lambda y: y\ns = """(\n"""\n# print((\nclass A:\n    def b(self): return {"x": 1}\n';
  assert.deepEqual(msgs(ok, "python"), []);
});

test("Java y C: llaves y paréntesis (sin contar los que están en textos o comentarios)", () => {
  assert.ok(msgs('class A {\n  void m() {\n    System.out.println("hola";\n  }\n', "java").length >= 1);
  assert.deepEqual(msgs("int main() { char c = '}'; /* { */ printf(\"%d\\n\", 1); return 0; }\n", "c"), []);
  assert.deepEqual(msgs("int x = 1;\n}\n", "c"), ["2:Sobra «}»: no hay ninguna llave abierta"]);
});
