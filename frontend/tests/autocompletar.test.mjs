// Autocompletado de Trabajo (como VS Code): sugerencias por lenguaje, Emmet y fragmentos.
import { test } from "node:test";
import assert from "node:assert/strict";
import { coincide, esquemaSql, expandirEmmet, fragmentoAPlano, sugerir } from "../js/trabajo/autocompletar.js";

const etiquetas = (o) => sugerir(o).items.map((x) => x.etiqueta);

test("Python: funciones, módulos, métodos después del punto y alias", () => {
  const r = sugerir({ ext: "py", linea: "pri", documento: "pri" });
  assert.equal(r.prefijo, 3);
  assert.equal(r.items[0].etiqueta, "print");
  assert.equal(r.items[0].insertar, "print($0)");
  assert.ok(etiquetas({ ext: "py", linea: "import ra" }).includes("random"));
  assert.deepEqual(etiquetas({ ext: "py", linea: "x = math.sq", documento: "import math\n" }), ["sqrt"]);
  assert.ok(etiquetas({ ext: "py", linea: "np.ar", documento: "import numpy as np\n" }).includes("array"));
  assert.ok(etiquetas({ ext: "py", linea: "nombre.up" }).includes("upper"));
});

test("Python: sugiere lo que definiste (funciones, variables) y nombres de otros archivos", () => {
  const doc = "def calcular_total(a):\n    pass\n\nprecio_final = 10\n";
  assert.ok(etiquetas({ ext: "py", linea: "calc", documento: doc }).includes("calcular_total"));
  assert.ok(etiquetas({ ext: "py", linea: "precio", documento: doc }).includes("precio_final"));
  const otros = [["utilidades.py", "def formatear_moneda(x):\n    return x\n"]];
  assert.ok(etiquetas({ ext: "py", linea: "formatear", documento: "", ruta: "main.py", archivos: otros }).includes("formatear_moneda"));
  assert.ok(etiquetas({ ext: "py", linea: "from uti", documento: "", ruta: "main.py", archivos: otros }).includes("utilidades"));
});

test("no sugiere dentro de textos ni comentarios, ni lo que ya escribiste", () => {
  assert.deepEqual(etiquetas({ ext: "py", linea: 'print("hola pri' }), []);
  assert.deepEqual(etiquetas({ ext: "py", linea: "# pri" }), []);
  assert.deepEqual(etiquetas({ ext: "js", linea: "// con" }), []);
  assert.ok(!etiquetas({ ext: "py", linea: "precio", documento: "precio = 1\nprecio" }).includes("precio"));
});

test("fragmentos (def, sout, log…) se ofrecen aunque el atajo esté completo", () => {
  const def = sugerir({ ext: "py", linea: "def" }).items.find((x) => x.tipo === "snip");
  assert.equal(def.etiqueta, "def");
  assert.match(def.insertar, /^def \$\{1:nombre\}/);
  assert.equal(sugerir({ ext: "java", linea: "    sout" }).items[0].insertar, "System.out.println(${0});");
  assert.ok(etiquetas({ ext: "js", linea: "log", monaco: true }).includes("log"));
});

test("Java, PHP y C: miembros y palabras clave", () => {
  assert.deepEqual(etiquetas({ ext: "java", linea: "System.out.pr" }), ["print", "printf", "println"]);
  assert.ok(etiquetas({ ext: "php", linea: "$con", documento: "$conexion = 1;" }).includes("$conexion"));
  assert.ok(etiquetas({ ext: "c", linea: "pri" }).includes("printf"));
});

test("con Monaco no se repite el IntelliSense de JavaScript", () => {
  assert.deepEqual(etiquetas({ ext: "js", linea: "console.lo", monaco: true }), []);
  assert.ok(!etiquetas({ ext: "js", linea: "con", monaco: true }).includes("console"));
  // sin Monaco (editor simple) sí
  assert.ok(etiquetas({ ext: "js", linea: "document.que" }).includes("querySelector"));
});

test("SQL: tablas y columnas de los CREATE TABLE del proyecto", () => {
  const doc = "CREATE TABLE IF NOT EXISTS `usuarios` (\n  id INT AUTO_INCREMENT,\n  nombre VARCHAR(50),\n  precio DECIMAL(10,2),\n  PRIMARY KEY (id)\n);";
  const t = esquemaSql([["base.sql", doc]]);
  assert.deepEqual([...t.get("usuarios")], ["id", "nombre", "precio"]);
  assert.equal(sugerir({ ext: "sql", linea: "SELECT * FROM us", documento: doc }).items[0].etiqueta, "usuarios");
  assert.deepEqual(etiquetas({ ext: "sql", linea: "SELECT usuarios.", documento: doc }).slice(0, 3), ["id", "nombre", "precio"]);
  assert.ok(etiquetas({ ext: "sql", linea: "sel" }).includes("SELECT"));   // no distingue mayúsculas
});

test("Emmet en HTML", () => {
  assert.equal(expandirEmmet("ul>li*2"), "<ul>\n\t<li>${1}</li>\n\t<li>${2}</li>\n</ul>");
  assert.equal(expandirEmmet("div.caja#principal"), '<div id="principal" class="caja">${1}</div>');
  assert.equal(expandirEmmet("ul.lista>li.item$*2{Elemento $}"), '<ul class="lista">\n\t<li class="item1">Elemento 1</li>\n\t<li class="item2">Elemento 2</li>\n</ul>$0');
  assert.equal(expandirEmmet("input[type=email name=correo]"), '<input type="email" name="correo">$0');
  assert.equal(expandirEmmet("img"), '<img src="${1}" alt="${2}">');
  assert.equal(expandirEmmet("nav>a*2+p"), '<nav>\n\t<a href="${1}">${2}</a>\n\t<a href="${3}">${4}</a>\n\t<p>${5}</p>\n</nav>');
  assert.equal(expandirEmmet("Hola"), null);          // no es una etiqueta
  assert.equal(expandirEmmet("ul>"), null);           // a medias
  // «!» da la página completa; mientras escribes «ul>li*» se sigue ofreciendo lo que ya se puede expandir
  assert.match(sugerir({ ext: "html", linea: "!", monaco: true }).items[0].insertar, /^<!DOCTYPE html>/);
  assert.equal(sugerir({ ext: "html", linea: "  ul>li*", monaco: true }).items[0].etiqueta, "ul>li*");
  // dentro de una etiqueta no estorba (ahí sugiere Monaco), ni en medio de un texto normal
  assert.deepEqual(etiquetas({ ext: "html", linea: '<a hre', monaco: true }), []);
  assert.deepEqual(etiquetas({ ext: "html", linea: "Hola mundo p", monaco: true }), []);
});

test("fragmento a texto plano para el editor simple (selecciona el primer marcador)", () => {
  assert.deepEqual(fragmentoAPlano("def ${1:nombre}(${2}):\n\t${0:pass}", "    "), { texto: "def nombre():\n    pass", desde: 4, hasta: 10 });
  const f = fragmentoAPlano("for (let ${1:i} = 0; ${1:i} < n; ${1:i}++) {\n\t$0\n}", "  ", "  ");
  assert.equal(f.texto, "for (let i = 0; i < n; i++) {\n    \n  }");
  assert.deepEqual([f.desde, f.hasta], [9, 10]);
  assert.equal(fragmentoAPlano("\\$conexion = 1;$0").texto, "$conexion = 1;");
});

test("coincide: prefijo o letras en orden, como VS Code", () => {
  assert.ok(coincide("print", "pri"));
  assert.ok(coincide("print", "pt"));
  assert.ok(!coincide("print", "tp"));
  assert.ok(!coincide("print", "print"));
  assert.ok(coincide("def", "def", true, true));
});
