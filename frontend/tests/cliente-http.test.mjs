import test from "node:test";
import assert from "node:assert/strict";
import { comoCurl, jsonBonito, parsearHttp, prepararPeticion, serializarHttp, sustituir } from "../js/trabajo/visor-http.js";
import { dividirSQL, q } from "../js/trabajo/visor-bd.js";

const EJEMPLO = `@base = http://localhost:8000
@token = abc123

### Listar usuarios
GET {{base}}/usuarios?pagina=1
Authorization: Bearer {{token}}
# X-Debug: 1

### Crear usuario
POST {{base}}/usuarios
Content-Type: application/json

{
  "nombre": "Ana"
}

###
https://jsonplaceholder.typicode.com/todos/1
`;

test("lee un archivo .http como REST Client de VS Code", () => {
  const c = parsearHttp(EJEMPLO);
  assert.deepEqual(c.variables, [{ nombre: "base", valor: "http://localhost:8000" }, { nombre: "token", valor: "abc123" }]);
  assert.equal(c.peticiones.length, 3);
  const [a, b, d] = c.peticiones;
  assert.deepEqual([a.nombre, a.metodo, a.url], ["Listar usuarios", "GET", "{{base}}/usuarios?pagina=1"]);
  assert.deepEqual(a.cabeceras, [{ k: "Authorization", v: "Bearer {{token}}", on: true }, { k: "X-Debug", v: "1", on: false }]);
  assert.equal(b.cuerpo, '{\n  "nombre": "Ana"\n}');
  assert.deepEqual([d.metodo, d.url], ["GET", "https://jsonplaceholder.typicode.com/todos/1"], "sin método = GET");
});

test("escribir y volver a leer no pierde nada", () => {
  const c = parsearHttp(EJEMPLO);
  const otra = parsearHttp(serializarHttp(c));
  assert.deepEqual(otra.variables, c.variables);
  assert.deepEqual(otra.peticiones.map((p) => [p.metodo, p.url, p.cabeceras, p.cuerpo]), c.peticiones.map((p) => [p.metodo, p.url, p.cabeceras, p.cuerpo]));
});

test("variables, cabeceras apagadas y Content-Type automático", () => {
  const c = parsearHttp(EJEMPLO);
  const p = prepararPeticion(c.peticiones[0], c.variables);
  assert.equal(p.url, "http://localhost:8000/usuarios?pagina=1");
  assert.deepEqual(p.cabeceras, [["Authorization", "Bearer abc123"]], "la cabecera comentada no se envía");
  const post = prepararPeticion({ metodo: "POST", url: "{{base}}/x", cabeceras: [], cuerpo: '{"a":1}' }, c.variables);
  assert.deepEqual(post.cabeceras, [["Content-Type", "application/json"]]);
  assert.equal(prepararPeticion({ metodo: "GET", url: "http://x", cabeceras: [], cuerpo: "ignorado" }, []).cuerpo, "", "GET no lleva cuerpo");
  assert.match(sustituir("{{$timestamp}}", []), /^\d{10}$/);
  assert.equal(sustituir("{{a}}", [{ nombre: "a", valor: "{{b}}" }, { nombre: "b", valor: "2" }]), "2");
  assert.equal(sustituir("{{a}}", [{ nombre: "a", valor: "{{a}}" }]), "{{a}}", "una variable que se nombra a sí misma no se cuelga");
});

test("curl y JSON bonito escapan bien", () => {
  assert.equal(comoCurl({ metodo: "POST", url: "http://x/a", cabeceras: [["A", "it's"]], cuerpo: "{}" }), "curl -X POST 'http://x/a' \\\n  -H 'A: it'\\''s' \\\n  --data-raw '{}'");
  const html = jsonBonito('{"<b>": "<script>", "n": 1, "ok": true}');
  assert.ok(!html.includes("<script>") && !html.includes("<b>"), "nunca mete HTML de la respuesta");
  assert.match(html, /vh-n">1/);
  assert.equal(jsonBonito("no es json"), null);
});

test("SQL: divide sentencias respetando textos, comentarios y triggers", () => {
  assert.deepEqual(dividirSQL("SELECT 1; SELECT ';' -- ; nada\n; INSERT INTO t VALUES('a;b');"), ["SELECT 1", "SELECT ';' -- ; nada", "INSERT INTO t VALUES('a;b')"]);
  const trig = "CREATE TRIGGER t AFTER INSERT ON a BEGIN UPDATE b SET x = 1; DELETE FROM c; END; SELECT 2;";
  assert.deepEqual(dividirSQL(trig), ["CREATE TRIGGER t AFTER INSERT ON a BEGIN UPDATE b SET x = 1; DELETE FROM c; END", "SELECT 2"]);
  assert.deepEqual(dividirSQL("-- solo un comentario"), []);
  assert.equal(q('mi "tabla"'), '"mi ""tabla"""');
});
