import test from "node:test";
import assert from "node:assert/strict";
import { resaltar, infoLenguaje, esc } from "../js/trabajo/resaltado.js";

const sinEtiquetas = (h) => h.replace(/<[^>]+>/g, "").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const EXT = ["html","css","js","ts","json","py","java","c","cpp","cs","go","rs","swift","kt","php","rb","sql","md","sh","yml","txt","desconocida"];

test("conserva exactamente el texto original en todos los lenguajes (muestras reales)", () => {
  const muestras = {
    html: '<!doctype html>\n<html lang="es"><head><style>a{color:#fff;margin:0 auto}</style></head>\n<body class=x id="a"><!-- c --><script>const a = "x"; // hi\nconsole.log(a)</script><br/><img src=a.png></body></html>',
    css: '@media (max-width:600px){.a:hover>#b{color:rgb(1,2,3)!important;margin:-1.5em}}\n/* c */ a::before{content:"x"}',
    js: 'const f = (a, b) => `x${a}`; class A extends B { static x = 1 } // c\n/* m */ if (a) { return 0x1F }',
    py: 'def f(x):\n    """doc\n    mas"""\n    return f"{x}" # c\n@dec\nclass A: pass',
    json: '{"a": [1, 2.5e3, true, null], "b": {"c": "d"}}',
    c: '#include <stdio.h>\nint main(void){ char c = \'\\n\'; printf("hola"); return 0; }',
    php: '<?php $x = "a"; echo $x; # c\n?>',
    sql: "SELECT * FROM t WHERE a = 'it''s' -- c\n;",
    md: "# Titulo\n- item **bold** `code` [l](u)\n```js\ncode\n```",
  };
  for (const [ext, texto] of Object.entries(muestras)) assert.equal(sinEtiquetas(resaltar(texto, ext)), texto, ext);
});

test("conserva el texto con entradas aleatorias o rotas (no desalinea nunca)", () => {
  const alfabeto = ["<", ">", "/", '"', "'", "`", "{", "}", "(", ")", "#", "\n", " ", "a", "b", "1", "-", "*", "@", ":", ";", "!", "=", "&", "\\", "/*", "*/", "<!--", "-->", "def ", "<script>", "</script>", "<style>", "/*", '"""'];
  let semilla = 7;
  const azar = (n) => { semilla = (semilla * 1103515245 + 12345) & 0x7fffffff; return semilla % n; };
  for (let ronda = 0; ronda < 300; ronda += 1) {
    const texto = Array.from({ length: 1 + azar(60) }, () => alfabeto[azar(alfabeto.length)]).join("");
    for (const ext of EXT) assert.equal(sinEtiquetas(resaltar(texto, ext)), texto, `${ext}: ${JSON.stringify(texto)}`);
  }
});

test("colorea lo esperado", () => {
  assert.match(resaltar("const x = 1;", "js"), /<span class="t-k">const<\/span>/);
  assert.match(resaltar("// hola", "js"), /<span class="t-c">\/\/ hola<\/span>/);
  assert.match(resaltar('"a<b"', "js"), /&lt;/);
  assert.match(resaltar("def hola():", "py"), /t-k">def<\/span> <span class="t-f">hola/);
  assert.match(resaltar('<a href="x">', "html"), /t-tag">a<.*t-at">href<.*t-s">"x"/);
  assert.match(resaltar("a { color: red; }", "css"), /t-tag">a<.*t-pr">color<.*t-v">red/);
  assert.match(resaltar('{"k": 1}', "json"), /t-pr">"k"/);
  assert.match(resaltar("<style>p{color:blue}</style>", "html"), /t-pr">color/);
});

test("no inyecta HTML desde el contenido", () => {
  const h = resaltar('<img src=x onerror="alert(1)"><script>"</script><b>"</b>', "html");
  assert.ok(!/<img|<script|<b>/.test(h.replace(/<span[^>]*>|<\/span>/g, "")));
  assert.equal(esc("<&>"), "&lt;&amp;&gt;");
});

test("infoLenguaje y límites", () => {
  assert.equal(infoLenguaje("py").nombre, "Python");
  assert.equal(infoLenguaje("zzz").nombre, "Texto sin formato");
  assert.equal(resaltar("x".repeat(250_000), "js"), "x".repeat(250_000));
});
