import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
import { Shell } from "../js/trabajo/shell.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { quitarAnsi } from "../js/trabajo/ansi.js";
import { formatear, sentencias } from "../js/trabajo/sqlite.js";
import { esMarcador } from "../js/trabajo/archivos.js";

const initSqlJs = createRequire(import.meta.url)("/tmp/tsdep/node_modules/sql.js");
const SQL = await initSqlJs();

function entorno(files = {}, respuestas = []) {
  const py = normalizarProyecto({ files });
  const nube = new Map();
  const shell = new Shell({
    proyecto: () => py, ejecutores: { cargarSQL: async () => SQL },
    subirArchivo: async (bytes) => { const h = createHash("sha256").update(bytes).digest("hex"); nube.set(h, new Uint8Array(bytes)); return `ccbin:v1:${h}:application/octet-stream:${bytes.length}`; },
    leerArchivo: async (m) => nube.get(m.split(":")[2]),
  });
  const s = shell.nuevaSesion();
  let out = "", err = "";
  const cola = [...respuestas];
  s.out = (t) => { out += t; }; s.err = (t) => { err += t; };
  s.leerLinea = async () => (cola.length ? cola.shift() : null);
  const sh = async (l, r = []) => { out = ""; err = ""; cola.push(...r); const codigo = await shell.ejecutar(l, s); return { codigo, out: quitarAnsi(out), err: quitarAnsi(err) }; };
  return { py, sh, nube };
}

test("formatear y dividir sentencias", () => {
  assert.equal(formatear(["id", "nombre"], [[1, "Ana"], [10, null]]), "+----+--------+\n| id | nombre |\n+----+--------+\n|  1 | Ana    |\n| 10 | NULL   |\n+----+--------+\n");
  assert.equal(formatear(["a"], [["x,y"]], { modo: "csv" }), 'a\n"x,y"\n');
  const r = sentencias("CREATE TABLE t(a); -- comentario ;\nINSERT INTO t VALUES('a;b');\nSELECT");
  assert.deepEqual(r.completas, ["CREATE TABLE t(a);", "INSERT INTO t VALUES('a;b');"]);
  assert.equal(r.resto, "SELECT");
});

test("sqlite3 tienda.db: consola interactiva, la base se guarda en la cuenta y se puede reabrir", async () => {
  const { sh, py } = entorno();
  const r = await sh("sqlite3 tienda.db", ["CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL);", "INSERT INTO productos (nombre, precio)", "VALUES ('Pan', 2.5), ('Leche', 3);", ".tables", "SELECT * FROM productos;", ".quit"]);
  assert.equal(r.codigo, 0, r.err);
  assert.match(r.out, /productos/);
  assert.match(r.out, /\| Pan    \| +2\.5 \|/);
  assert.ok(esMarcador(py.files["tienda.db"]), "la base es un archivo guardado en la cuenta");
  const r2 = await sh('sqlite3 tienda.db "SELECT count(*) AS n FROM productos"');
  assert.match(r2.out, /\| 2 \|/);
});

test("sqlite3 base.db < script.sql, .read, .schema, .dump, .mode y errores claros", async () => {
  const { sh, py } = entorno({ "esquema.sql": "CREATE TABLE a (x INTEGER, y TEXT);\nINSERT INTO a VALUES (1, 'uno'), (2, 'dos');\n", "notas.txt": "hola" });
  assert.equal((await sh("sqlite3 datos.db < esquema.sql")).codigo, 0);
  assert.match((await sh('sqlite3 datos.db ".schema a"')).out, /CREATE TABLE a/);
  assert.match((await sh('sqlite3 datos.db ".mode csv" "SELECT * FROM a"')).out, /x,y\n1,uno\n2,dos/);
  assert.match((await sh('sqlite3 datos.db ".dump"')).out, /INSERT INTO "a" VALUES\(1,'uno'\);/);
  assert.match((await sh('sqlite3 datos.db "SELECT * FROM nada"')).err, /no such table: nada/);
  assert.match((await sh("sqlite3 notas.txt")).err, /no es una base de datos/);
  const r = await sh("sqlite3 otra.db", [".read esquema.sql", "SELECT y FROM a WHERE x = 2;"]);
  assert.match(r.out, /dos/);
  assert.match((await sh("sqlite3 esquema.sql")).out, /Consulta|^$/m, "un .sql suelto se ejecuta en memoria como antes");
  assert.ok(!("esquema.db" in py.files));
});

test("la redirección < funciona con cualquier comando", async () => {
  const { sh } = entorno({ "a.txt": "uno\ndos\ntres\n" });
  assert.equal((await sh("wc -l < a.txt")).out.trim(), "3");
  assert.match((await sh("cat < nada.txt")).err, /No existe/);
});
