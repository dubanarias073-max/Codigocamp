import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { ClienteBD } from "../js/trabajo/bd.js";
import { analizarMongo, argumentosRedis, formatoMongo, formatoRedis, leerJs, opcionesPsql, partirPg, tablaPsql } from "../js/trabajo/bdclientes.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { Shell } from "../js/trabajo/shell.js";

const sinColor = (t) => t.replace(/\x1b\[[0-9;]*m/g, "");
const memoria = () => { const m = new Map(); return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) }; };

test("psql: tabla como la real, partir con $$ y opciones/URI", () => {
  assert.equal(tablaPsql(["id", "nombre"], [[1, "Ana"], [10, null]]), " id | nombre\n----+--------\n  1 | Ana\n 10 |\n(2 rows)\n\n");
  const p = partirPg("CREATE FUNCTION f() RETURNS int AS $$ SELECT 1; $$ LANGUAGE sql; SELECT 'a;b'; -- c;\nSELECT \"x;y\"");
  assert.deepEqual(p.completas, ["CREATE FUNCTION f() RETURNS int AS $$ SELECT 1; $$ LANGUAGE sql", "SELECT 'a;b'"]);
  assert.equal(p.resto.trim(), 'SELECT "x;y"');
  const o = opcionesPsql(["postgresql://ana:cl%40ve@localhost:5433/tienda"]);
  assert.deepEqual([o.host, o.puerto, o.usuario, o.clave, o.base], ["localhost", 5433, "ana", "cl@ve", "tienda"]);
  const o2 = opcionesPsql(["-U", "postgres", "-dfinanbot", "-c", "SELECT 1"]);
  assert.deepEqual([o2.usuario, o2.base, o2.comandos], ["postgres", "finanbot", ["SELECT 1"]]);
});

test("mongosh: lee JS relajado y traduce a pymongo", () => {
  assert.deepEqual(leerJs("{ nombre: 'Ana', edad: { $gt: 18 }, _id: ObjectId('64b7f0000000000000000000'), f: ISODate('2026-11-19'), r: /an/i, ok: true, }").valor(),
    { nombre: "Ana", edad: { $gt: 18 }, _id: { $oid: "64b7f0000000000000000000" }, f: { $date: "2026-11-19T00:00:00.000Z" }, r: { $regex: "an", $options: "i" }, ok: true });
  assert.deepEqual(analizarMongo("db.usuarios.find({ activo: true }, { nombre: 1 }).sort({ nombre: -1 }).limit(5);"),
    { op: "find", coleccion: "usuarios", args: [{ activo: true }, { nombre: 1 }], opciones: { sort: { nombre: -1 }, limit: 5 } });
  assert.deepEqual(analizarMongo("db.gastos.updateOne({ a: 1 }, { $set: { b: 2 } }, { upsert: true })").opciones, { upsert: true });
  assert.equal(analizarMongo("db.getCollection('mis gastos').countDocuments()").coleccion, "mis gastos");
  assert.equal(analizarMongo("db.x.find().count()").op, "count_documents");
  assert.equal(analizarMongo("show dbs").op, "list_database_names");
  assert.equal(analizarMongo("use finanbot").base, "finanbot");
  assert.throws(() => analizarMongo("db.x.find({ a: })"), /SyntaxError/);
  assert.throws(() => analizarMongo("while(true){}"), /ReferenceError/);
  assert.equal(formatoMongo([{ _id: { $oid: "abc" }, n: "Ana", v: { $numberDecimal: "1.5" } }]), "[ { _id: ObjectId('abc'), n: 'Ana', v: Decimal128('1.5') } ]");
});

test("redis-cli: argumentos y formato", () => {
  assert.deepEqual(argumentosRedis(`SET "mi clave" 'hola mundo' "a\\nb"`), ["SET", "mi clave", "hola mundo", "a\nb"]);
  assert.equal(formatoRedis("OK"), "OK");
  assert.equal(formatoRedis("hola"), '"hola"');
  assert.equal(formatoRedis(3), "(integer) 3");
  assert.equal(formatoRedis(null), "(nil)");
  assert.equal(formatoRedis(["a", "b"]), '1) "a"\n2) "b"');
  assert.equal(formatoRedis([]), "(empty array)");
});

// ---------- De verdad, por el puente ----------
const aqui = path.dirname(fileURLToPath(import.meta.url));
const backend = path.resolve(aqui, "../../backend");
const py = (codigo) => spawnSync("python3", ["-c", codigo]).status === 0;
const hayPg = py("import pg8000.dbapi as p; p.connect(host='127.0.0.1', user='postgres', password='postgres', timeout=1).close()");
const hayRedis = py("import redis; redis.Redis(socket_connect_timeout=1).ping()");
const hayMock = py("import mongomock");

async function conPuente(fn) {
  // Puente real; MongoDB se simula con mongomock (no hay servidor Mongo en las pruebas).
  const script = `
import sys; sys.path.insert(0, ${JSON.stringify(backend)})
from herramientas.puente_bd import crear_servidor
from servicios.bd_externa import Sesiones
try:
    import mongomock
    _c = mongomock.MongoClient(); _c.server_info = lambda: {"version": "7.0.0", "versionArray": [7, 0, 0, 0]}
    con = {"mongodb": lambda *a, **k: _c}
except ImportError:
    con = {}
s = crear_servidor(8798, "k", sesiones=Sesiones(conectores=con)); print("listo", flush=True); s.serve_forever()`;
  const proc = spawn("python3", ["-c", script], { stdio: ["ignore", "pipe", "pipe"] });
  await new Promise((ok, mal) => { proc.stdout.on("data", (d) => String(d).includes("listo") && ok()); proc.on("exit", () => mal(new Error("el puente no arrancó"))); });
  const c = new ClienteBD({ fetchFn: fetch, almacen: memoria() });
  c.configurarPuente("http://127.0.0.1:8798", "k");
  const proyecto = normalizarProyecto({ files: { "esquema.sql": "DROP TABLE IF EXISTS cc_prod;\nCREATE TABLE cc_prod (id SERIAL PRIMARY KEY, nombre TEXT NOT NULL, precio NUMERIC(8,2));\nINSERT INTO cc_prod (nombre, precio) VALUES ('Pan', 2.5), ('Leche', 3.2);\n", "datos.js": "db.gastos.insertMany([{ concepto: 'Bus', valor: 2950 }, { concepto: 'Café', valor: 4500 }])\n" } });
  const shell = new Shell({ proyecto: () => proyecto, bd: c });
  const correr = async (linea, lineas = []) => {
    let salida = "", errores = "";
    const sesion = shell.nuevaSesion({ out: (t) => { salida += t; }, err: (t) => { errores += t; }, leerLinea: async () => lineas.shift() ?? null });
    const codigo = await shell.ejecutar(linea, sesion);
    return { codigo, salida: sinColor(salida), errores: sinColor(errores) };
  };
  try { await fn(correr); } finally { proc.kill(); }
}

test("REAL: psql contra PostgreSQL", { skip: !hayPg && "no hay PostgreSQL" }, async () => {
  await conPuente(async (correr) => {
    let r = await correr("psql -U postgres -f esquema.sql", []);
    assert.equal(r.codigo, 2, "sin clave falla (como psql: código 2)");
    r = await correr("psql postgresql://postgres:postgres@127.0.0.1/postgres -f esquema.sql");
    assert.equal(r.codigo, 0, r.errores);
    assert.match(r.salida, /CREATE TABLE\nINSERT 0 2/);
    r = await correr("psql -U postgres -W", ["postgres", "\\dt", "SELECT nombre, precio", "FROM cc_prod ORDER BY id;", "\\d cc_prod", "\\x", "SELECT 1 AS uno;", "SELECT * FROM nada;", "\\q"]);
    assert.match(r.salida, /cc_prod/);
    assert.match(r.salida, / nombre \| precio\n--------\+--------\n Pan    \|   2\.50\n Leche  \|   3\.20\n\(2 rows\)/);
    assert.match(r.salida, /not null/);
    assert.match(r.salida, /-\[ RECORD 1 \]/);
    assert.match(r.errores, /ERROR:  relation "nada" does not exist/);
    r = await correr("psql postgresql://postgres:postgres@127.0.0.1/postgres -c 'DROP TABLE cc_prod'");
    assert.match(r.salida, /DROP TABLE/);
  });
});

test("REAL: redis-cli contra Redis", { skip: !hayRedis && "no hay Redis" }, async () => {
  await conPuente(async (correr) => {
    let r = await correr("redis-cli SET cc:saludo 'hola mundo'");
    assert.equal(r.salida, "OK\n");
    r = await correr("redis-cli", ["GET cc:saludo", "RPUSH cc:l a b", "LRANGE cc:l 0 -1", "GET cc:nada", "DEL cc:saludo cc:l", "COMANDOMALO", "exit"]);
    assert.equal(r.salida, '"hola mundo"\n(integer) 2\n1) "a"\n2) "b"\n(nil)\n(integer) 2\n' + r.salida.split("\n").slice(6).join("\n"));
    assert.match(r.salida, /\(error\) .*unknown command/i);
  });
});

test("mongosh por el puente (MongoDB simulado)", { skip: !hayMock && "falta mongomock" }, async () => {
  await conPuente(async (correr) => {
    let r = await correr('mongosh "mongodb://127.0.0.1:27017/finanbot" datos.js');
    assert.equal(r.codigo, 0, r.errores);
    assert.match(r.salida, /acknowledged: true/);
    r = await correr("mongosh finanbot", ["show collections", "db.gastos.find({ valor: { $gt: 3000 } }, { _id: 0 })", "db.gastos.countDocuments()", "db.gastos.updateOne(", "  { concepto: 'Bus' },", "  { $set: { valor: 3000 } })", "db.gastos.aggregate([{ $group: { _id: null, total: { $sum: '$valor' } } }])", "db.gastos.noExiste()", "use otra", "db", "exit"]);
    assert.match(r.salida, /^gastos$/m);
    assert.match(r.salida, /\[ \{ concepto: 'Café', valor: 4500 \} \]/);
    assert.match(r.salida, /^2$/m);
    assert.match(r.salida, /modifiedCount: 1/);
    assert.match(r.salida, /total: 7500/);
    assert.match(r.errores, /is not a function/);
    assert.match(r.salida, /switched to db otra\notra/);
  });
});

test("REAL (Python): psycopg2, psycopg, pymongo y redis de CódigoCamp", { skip: !(hayPg && hayRedis && hayMock) && "faltan servidores" }, async () => {
  const { MODULOS_MYSQL } = await import("../js/trabajo/pymysql.js");
  const { MODULOS_BD } = await import("../js/trabajo/pybd.js");
  const fs = await import("node:fs");
  const os = await import("node:os");
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ccpybd-"));
  for (const [ruta, codigo] of Object.entries({ ...MODULOS_MYSQL, ...MODULOS_BD })) { fs.mkdirSync(path.dirname(path.join(dir, ruta)), { recursive: true }); fs.writeFileSync(path.join(dir, ruta), codigo); }
  fs.writeFileSync(path.join(dir, "_cc_bd.py"), `import json, urllib.request, urllib.error
def pedir(accion, datos):
    req = urllib.request.Request("http://127.0.0.1:8798/api/bd/" + accion, data=datos.encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer k"})
    try:
        with urllib.request.urlopen(req) as r: return r.read().decode()
    except urllib.error.HTTPError as e:
        j = json.loads(e.read() or b"{}"); return json.dumps({"__error": j.get("error"), "codigo": j.get("codigo")})
`);
  const programa = String.raw`
import datetime, decimal
import psycopg2, psycopg2.extras, psycopg2.errors
from psycopg2 import sql
c = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="postgres")
cur = c.cursor()
cur.execute("DROP TABLE IF EXISTS cc_py")
cur.execute("CREATE TABLE cc_py (id SERIAL PRIMARY KEY, nombre TEXT UNIQUE, precio NUMERIC(8,2), dia DATE, datos JSONB, foto BYTEA, tags TEXT[])")
cur.execute("INSERT INTO cc_py (nombre, precio, dia, datos, foto, tags) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            ("O'Brien \\ ñ", decimal.Decimal("9.99"), datetime.date(2026, 11, 19), psycopg2.extras.Json({"a": [1, 2]}), b"\x00\xff", ["x", "y"]))
print("id", cur.fetchone()[0])
c.commit()
cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cur.execute("SELECT * FROM cc_py WHERE nombre = %(n)s", {"n": "O'Brien \\ ñ"})
f = cur.fetchone()
assert f["precio"] == decimal.Decimal("9.99") and f["dia"] == datetime.date(2026, 11, 19), f
assert f["datos"] == {"a": [1, 2]} and bytes(f["foto"]) == b"\x00\xff" and f["tags"] == ["x", "y"], f
print("desc", cur.description[0].name)
try:
    cur.execute("INSERT INTO cc_py (nombre) VALUES ('O''Brien \\ ñ')")
except psycopg2.errors.UniqueViolation as e:
    print("unico", e.pgcode)
c.rollback()
with c:
    with c.cursor() as k:
        k.execute(sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier("cc_py")))
        print("cuenta", k.fetchone()[0])
try:
    c.cursor().execute("SELECT * FROM no_existe")
except psycopg2.errors.UndefinedTable as e:
    print("tabla", "no_existe" in str(e))
c.rollback()
c.autocommit = True
c.cursor().execute("DROP TABLE cc_py")
c.close()

import psycopg
from psycopg.rows import dict_row
with psycopg.connect("host=localhost dbname=postgres user=postgres password=postgres", row_factory=dict_row) as c3:
    print("v3", c3.execute("SELECT 1 + 1 AS dos").fetchone())

import pymongo
from bson import ObjectId
cli = pymongo.MongoClient("mongodb://localhost:27017/")
db = cli.finanbot
r = db.gastos.insert_one({"concepto": "Bus", "valor": 2950, "fecha": datetime.datetime(2026, 11, 19, 8, 0)})
assert isinstance(r.inserted_id, ObjectId)
db.gastos.insert_many([{"concepto": "Café", "valor": 4500}, {"concepto": "Pan", "valor": 1200}])
print("mongo", [d["concepto"] for d in db.gastos.find({"valor": {"$gt": 2000}}).sort("valor", pymongo.DESCENDING)])
d = db["gastos"].find_one({"_id": r.inserted_id})
assert d["fecha"] == datetime.datetime(2026, 11, 19, 8, 0) and d["_id"] == r.inserted_id, d
print("upd", db.gastos.update_many({}, {"$inc": {"valor": 1}}).modified_count, db.gastos.count_documents({}))
print("agg", list(db.gastos.aggregate([{"$group": {"_id": None, "t": {"$sum": "$valor"}}}]))[0]["t"])
print("del", db.gastos.delete_many({"valor": {"$lt": 2000}}).deleted_count, cli.finanbot.list_collection_names())
cli.close()

import redis
rr = redis.Redis(host="localhost", decode_responses=True)
assert rr.ping()
assert rr.set("cc:py", "hola", ex=60) is True
rr.hset("cc:h", mapping={"a": "1", "b": "2"})
print("redis", rr.get("cc:py"), rr.hgetall("cc:h"), rr.incr("cc:n"), rr.exists("cc:py"), rr.ttl("cc:py") > 0)
rb = redis.Redis()
print("bytes", rb.get("cc:py"))
rr.delete("cc:py", "cc:h", "cc:n")
try:
    rr.execute_command("NOEXISTE")
except redis.ResponseError as e:
    print("rerr", "unknown" in str(e).lower())
`;
  await conPuente(async () => {
    const r = spawnSync("python3", ["-c", programa], { cwd: dir, env: { ...process.env, PYTHONPATH: dir }, encoding: "utf8" });
    assert.equal(r.status, 0, r.stderr + r.stdout);
    for (const esperado of [/id 1/, /desc id/, /unico 23505/, /cuenta 1/, /tabla True/, /v3 \{'dos': 2\}/, /mongo \['Café', 'Bus'\]/, /upd 3 3/, /agg 8653/, /del 1 \['gastos'\]/, /redis hola \{'a': '1', 'b': '2'\} 1 1 True/, /bytes b'hola'/, /rerr True/]) assert.match(r.stdout, esperado);
  });
  fs.rmSync(dir, { recursive: true, force: true });
});
