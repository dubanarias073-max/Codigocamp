// Errores de ejecución → problemas con archivo y línea
import { test } from "node:test";
import assert from "node:assert/strict";
import { erroresDeSalida, rutaDelProyecto } from "../js/trabajo/errores-salida.js";

const R = ["main.py", "app/utils.py", "index.js", "src/main.rs", "Main.java", "main.c", "web/index.php", "main.go", "x.rb", "Program.cs"];

test("ruta absoluta o relativa → archivo del proyecto", () => {
  assert.equal(rutaDelProyecto("/workspace/app/utils.py", R), "app/utils.py");
  assert.equal(rutaDelProyecto("./main.py", R), "main.py");
  assert.equal(rutaDelProyecto("/usr/lib/python3/json.py", R), null);
});

test("Python: traceback marca la última línea del proyecto", () => {
  const t = 'Traceback (most recent call last):\n  File "/workspace/main.py", line 4, in <module>\n    calcular()\n  File "/workspace/app/utils.py", line 9, in calcular\n    return 1/0\nZeroDivisionError: division by zero\n';
  assert.deepEqual(erroresDeSalida(t, R), [{ ruta: "app/utils.py", linea: 9, mensaje: "ZeroDivisionError: division by zero", grave: true }]);
});

test("Python: error de sintaxis", () => {
  const t = '  File "/workspace/main.py", line 2\n    print("hola"\n         ^\nSyntaxError: \'(\' was never closed\n';
  const e = erroresDeSalida(t, R);
  assert.equal(e[0].linea, 2); assert.match(e[0].mensaje, /SyntaxError/);
});

test("Node: pila de llamadas", () => {
  const t = "/workspace/index.js:3\n  x()\n  ^\n\nReferenceError: x is not defined\n    at Object.<anonymous> (/workspace/index.js:3:3)\n    at node:internal/main\n";
  const e = erroresDeSalida(t, R);
  assert.equal(e.length, 1); assert.equal(e[0].ruta, "index.js"); assert.equal(e[0].linea, 3);
});

test("compiladores: gcc, javac, go, rustc, dotnet", () => {
  const t = [
    "main.c:5:3: error: 'x' undeclared (first use in this function)",
    "main.c:7:1: warning: control reaches end of non-void function",
    "Main.java:4: error: cannot find symbol",
    "./main.go:6:2: undefined: fmtt",
    "error[E0425]: cannot find value `y` in this scope",
    " --> src/main.rs:3:13",
    "Program.cs(10,5): error CS0103: The name 'z' does not exist",
  ].join("\n");
  const e = erroresDeSalida(t, R);
  const de = (r) => e.filter((x) => x.ruta === r);
  assert.equal(de("main.c").length, 2); assert.equal(de("main.c")[1].grave, false);
  assert.equal(de("Main.java")[0].linea, 4);
  assert.equal(de("main.go")[0].mensaje, "undefined: fmtt");
  assert.equal(de("src/main.rs")[0].linea, 3);
  assert.equal(de("Program.cs")[0].linea, 10);
});

test("PHP y Ruby", () => {
  const e = erroresDeSalida("PHP Parse error:  syntax error, unexpected '}' in /workspace/web/index.php on line 8\nx.rb:3:in `saludar': undefined local variable (NameError)\n", R);
  assert.equal(e.find((x) => x.ruta === "web/index.php").linea, 8);
  assert.equal(e.find((x) => x.ruta === "x.rb").linea, 3);
});

test("salida normal no produce problemas", () => {
  assert.deepEqual(erroresDeSalida("Hola mundo\n42\nTodo bien: 3 errores corregidos\n", R), []);
});
