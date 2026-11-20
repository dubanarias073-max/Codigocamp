import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { ClienteBD, comandoMysql, comandoPuente, opcionesMysql, partirMysql, resultadoMysql, tablaMysql } from "../js/trabajo/bd.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { Shell } from "../js/trabajo/shell.js";

const sinColor = (t) => t.replace(/\x1b\[[0-9;]*m/g, "");
const memoria = () => { const m = new Map(); return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) }; };

test("partirMysql: ; dentro de comillas, comentarios, \\G y DELIMITER", () => {
  const { completas, resto } = partirMysql("SELECT 'a;b', `x;y` FROM t; -- nota ; aquí\nSELECT 2\\G # otro;\nINSERT INTO t VALUES (\"c\\\";\"); /* ; */ SELECT");
  assert.deepEqual(completas.map((c) => c.sql), ["SELECT 'a;b', `x;y` FROM t", "SELECT 2", 'INSERT INTO t VALUES ("c\\";")']);
  assert.equal(completas[1].vertical, true);
  assert.equal(resto.trim(), "SELECT");
  const p = partirMysql("DELIMITER //\nCREATE PROCEDURE p() BEGIN SELECT 1; SELECT 2; END//\nDELIMITER ;\nCALL p();");
  assert.deepEqual(p.completas.map((c) => c.sql), ["CREATE PROCEDURE p() BEGIN SELECT 1; SELECT 2; END", "CALL p()"]);
  assert.equal(p.delimitador, ";");
  // /*! ... */ de los volcados de phpMyAdmin se manda tal cual (MySQL lo entiende)
  assert.deepEqual(partirMysql("/*!40101 SET NAMES utf8mb4 */;").completas.map((c) => c.sql), ["/*!40101 SET NAMES utf8mb4 */"]);
});

test("opcionesMysql: como el cliente real", () => {
  assert.deepEqual((({ host, puerto, usuario, clave, base }) => ({ host, puerto, usuario, clave, base }))(opcionesMysql(["-u", "root", "-psecreta", "-h", "localhost", "-P3307", "finanbot_db"])),
    { host: "localhost", puerto: 3307, usuario: "root", clave: "secreta", base: "finanbot_db" });
  const o = opcionesMysql(["--user=ana", "--database=x", "-e", "SELECT 1", "-p", "-B", "-N"]);
  assert.equal(o.usuario, "ana"); assert.equal(o.base, "x"); assert.equal(o.ejecutar, "SELECT 1"); assert.equal(o.pedirClave, true); assert.equal(o.lote, true); assert.equal(o.encabezados, false);
  assert.match(opcionesMysql(["--rara"]).error, /desconocida/);
});

test("tabla como mysql: números a la derecha, NULL, bytes en hexadecimal, acentos", () => {
  const t = tablaMysql(["id", "nombre", "saldo", "foto"], [[1, "Ana ñ", "1500.50", null], [12, "Luis", "20.00", { $bytes: "ff00" }]]);
  assert.equal(t, [
    "+----+--------+---------+--------+",
    "| id | nombre | saldo   | foto   |",
    "+----+--------+---------+--------+",
    "|  1 | Ana ñ  | 1500.50 | NULL   |",
    "| 12 | Luis   |   20.00 | 0xFF00 |",
    "+----+--------+---------+--------+", ""].join("\n"));
  assert.equal(sinColor(resultadoMysql({ columnas: ["a"], filas: [], segundos: 0 })), "Empty set (0.00 sec)\n\n");
  assert.equal(resultadoMysql({ columnas: null, afectadas: 1, segundos: 0.012 }), "Query OK, 1 row affected (0.01 sec)\n\n");
});

test("cliente: usa el puente si está configurado (con su clave) y si no el servidor (con CSRF)", async () => {
  const pedidos = [];
  const fetchFn = async (url, op) => { pedidos.push({ url, op }); return { ok: true, status: 200, json: async () => ({ activo: true, hosts: [] }) }; };
  const c = new ClienteBD({ fetchFn, almacen: memoria() });
  await c.estado();
  assert.equal(pedidos[0].url, "/api/bd/estado");
  assert.equal(pedidos[0].op.credentials, "same-origin");
  assert.throws(() => c.configurarPuente("ftp://x", "k"), /http/);
  assert.throws(() => c.configurarPuente("http://127.0.0.1:8787", ""), /clave/);
  c.configurarPuente("http://127.0.0.1:8787/", "k1");
  await c.pedir("consulta", { sql: "SELECT 1" });
  assert.equal(pedidos[1].url, "http://127.0.0.1:8787/api/bd/consulta");
  assert.equal(pedidos[1].op.headers.Authorization, "Bearer k1");
  assert.equal(pedidos[1].op.credentials, "omit", "al puente no se le mandan las cookies de CódigoCamp");
  c.quitarPuente();
  await c.estado();
  assert.equal(pedidos[2].url, "/api/bd/estado");
});

test("mysql sin servidor ni puente: explica qué hacer", async () => {
  const fetchFn = async () => { throw new TypeError("Failed to fetch"); };
  const c = new ClienteBD({ fetchFn, almacen: memoria() });
  c.configurarPuente("http://127.0.0.1:9", "x");
  let err = "";
  const codigo = await comandoMysql({ args: ["-u", "root"], py: normalizarProyecto({}), cwd: "", out: () => {}, err: (t) => { err += t; }, leerLinea: async () => null, cliente: c });
  assert.equal(codigo, 1);
  assert.match(err, /puente_bd\.py/);
});

// ---------- De verdad: el puente de Python + un MySQL/MariaDB en 127.0.0.1:3306 (como XAMPP) ----------
const aqui = path.dirname(fileURLToPath(import.meta.url));
const backend = path.resolve(aqui, "../../backend");
const hayMysql = spawnSync("python3", ["-c", "import pymysql; pymysql.connect(host='127.0.0.1', user='root', password='', connect_timeout=1).close()"]).status === 0;

async function conPuente(fn) {
  const clave = "clave-de-prueba";
  const proc = spawn("python3", [path.join(backend, "herramientas/puente_bd.py"), "--puerto", "8799", "--clave", clave], { stdio: ["ignore", "pipe", "pipe"] });
  await new Promise((ok, mal) => { proc.stdout.on("data", (d) => String(d).includes("listo") && ok()); proc.on("exit", () => mal(new Error("el puente no arrancó"))); });
  try { await fn(`http://127.0.0.1:8799`, clave); } finally { proc.kill(); }
}

test("REAL: mysql -u root con el puente: crear base, importar un .sql con <, consultar, source, errores", { skip: !hayMysql && "no hay MySQL en 127.0.0.1:3306" }, async () => {
  await conPuente(async (url, clave) => {
    const c = new ClienteBD({ fetchFn: fetch, almacen: memoria() });
    let out = "";
    assert.equal(await comandoPuente({ args: [url, clave], out: (t) => { out += t; }, err: (t) => { out += t; }, cliente: c }), 0);
    assert.match(sinColor(out), /Puente listo/);

    const py = normalizarProyecto({ files: {
      "Mysql(base de datos)/finanbot_db.sql": "-- Volcado de phpMyAdmin\n/*!40101 SET NAMES utf8mb4 */;\nDROP DATABASE IF EXISTS cc_finanbot;\nCREATE DATABASE cc_finanbot;\nUSE cc_finanbot;\nCREATE TABLE gastos (id INT AUTO_INCREMENT PRIMARY KEY, concepto VARCHAR(40), valor DECIMAL(10,2));\nINSERT INTO gastos (concepto, valor) VALUES ('Café; con leche', 4500), ('Bus', 2950.5);\n",
      "consultas.sql": "SELECT COUNT(*) AS n FROM gastos;",
    } });
    const shell = new Shell({ proyecto: () => py, bd: c });
    const correr = async (linea, lineas = []) => {
      let salida = "", errores = "";
      const sesion = shell.nuevaSesion({ out: (t) => { salida += t; }, err: (t) => { errores += t; }, leerLinea: async () => lineas.shift() ?? null });
      const codigo = await shell.ejecutar(linea, sesion);
      return { codigo, salida: sinColor(salida), errores: sinColor(errores) };
    };
    let r = await correr('mysql -u root < "Mysql(base de datos)/finanbot_db.sql"');
    assert.equal(r.codigo, 0, r.errores);
    r = await correr('mysql -u root cc_finanbot -e "SELECT concepto, valor FROM gastos ORDER BY id"');
    assert.equal(r.codigo, 0, r.errores);
    assert.match(r.salida, /\| Café; con leche \| 4500\.00 \|/);
    assert.match(r.salida, /2 rows in set/);
    // Consola interactiva
    r = await correr("mysql -u root", ["USE cc_finanbot;", "SELECT *", "FROM gastos WHERE valor > 3000;", "source consultas.sql", "SELECT * FROM no_existe;", "INSERT INTO gastos (concepto, valor) VALUES ('Pan', 1)\\G", "exit"]);
    assert.match(r.salida, /Welcome to the MySQL monitor/);
    assert.match(r.salida, /Database changed/);
    assert.match(r.salida, /1 row in set/);
    assert.match(r.salida, /\|\s+n \|\n\+-+\+\n\|\s+2 \|/);
    assert.match(r.errores, /ERROR 1146.*no_existe/);
    assert.match(r.salida, /Query OK, 1 row affected/);
    assert.match(r.salida, /Bye/);
    r = await correr("mysql -u root -h 8.8.8.8");
    assert.equal(r.codigo, 1);
    assert.match(r.errores, /no permite conectar/);
    r = await correr("mysql -u root -P 1");
    assert.match(r.errores, /XAMPP/);
    r = await correr("mysql -u root -e 'DROP DATABASE cc_finanbot'");
    assert.equal(r.codigo, 0, r.errores);
  });
});

test("REAL: pymysql, mysql.connector y MySQLdb de CódigoCamp (ejecutados en Python) contra tu MySQL", { skip: !hayMysql && "no hay MySQL en 127.0.0.1:3306" }, async () => {
  const { MODULOS_MYSQL } = await import("../js/trabajo/pymysql.js");
  const fs = await import("node:fs");
  const os = await import("node:os");
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "ccmysql-"));
  for (const [ruta, codigo] of Object.entries(MODULOS_MYSQL)) { fs.mkdirSync(path.dirname(path.join(dir, ruta)), { recursive: true }); fs.writeFileSync(path.join(dir, ruta), codigo); }
  await conPuente(async (url, clave) => {
    // _cc_bd falso: hace lo mismo que ClienteBD.pedirSync, pero desde CPython
    fs.writeFileSync(path.join(dir, "_cc_bd.py"), `import json, urllib.request, urllib.error
def pedir(accion, datos):
    req = urllib.request.Request("${url}/api/bd/" + accion, data=datos.encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer ${clave}"})
    try:
        with urllib.request.urlopen(req) as r: return r.read().decode()
    except urllib.error.HTTPError as e:
        j = json.loads(e.read() or b"{}"); return json.dumps({"__error": j.get("error"), "codigo": j.get("codigo")})
`);
    const programa = String.raw`
import datetime, decimal
import pymysql, pymysql.cursors
c = pymysql.connect(host="localhost", user="root", password="", charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
with c.cursor() as cur:
    cur.execute("CREATE DATABASE IF NOT EXISTS cc_py")
c.select_db("cc_py")
with c.cursor() as cur:
    cur.execute("DROP TABLE IF EXISTS mov")
    cur.execute("CREATE TABLE mov (id INT AUTO_INCREMENT PRIMARY KEY, txt VARCHAR(50) UNIQUE, valor DECIMAL(10,2), dia DATE, hora DATETIME, dato BLOB)")
    n = cur.executemany("INSERT INTO mov (txt, valor, dia, hora, dato) VALUES (%s, %s, %s, %s, %s)", [
        ("O'Brien \"x\" \\ ñ", decimal.Decimal("10.50"), datetime.date(2026, 11, 19), datetime.datetime(2026, 11, 19, 8, 30), b"\x00\xff"),
        ("Bus", 2950, None, None, None)])
    assert n == 2, n
    print("lastrowid", cur.lastrowid)
c.commit()
with c.cursor() as cur:
    cur.execute("SELECT * FROM mov WHERE valor > %(minimo)s ORDER BY id", {"minimo": 5})
    filas = cur.fetchall()
    f = filas[0]
    assert f["txt"] == "O'Brien \"x\" \\ ñ", f
    assert f["valor"] == decimal.Decimal("10.50") and f["dia"] == datetime.date(2026, 11, 19) and f["hora"] == datetime.datetime(2026, 11, 19, 8, 30), f
    assert f["dato"] == b"\x00\xff", f
    print("filas", len(filas))
try:
    with c.cursor() as cur:
        cur.execute("INSERT INTO mov (txt) VALUES ('Bus')")
except pymysql.err.IntegrityError as e:
    print("integridad", e.args[0])
# sin commit no se guarda (como el pymysql real)
with c.cursor() as cur:
    cur.execute("INSERT INTO mov (txt) VALUES ('sin commit')")
c.rollback()
c.close()

import mysql.connector
cn = mysql.connector.connect(host="localhost", user="root", password="", database="cc_py")
assert cn.is_connected()
cur = cn.cursor(dictionary=True)
cur.execute("SELECT COUNT(*) AS n FROM mov")
print("conector", cur.fetchone()["n"])
cur = cn.cursor()
cur.execute("SELECT txt FROM mov ORDER BY id")
print("columnas", cur.column_names, [t for (t,) in cur])
try:
    cur.execute("SELECT * FROM no_hay")
except mysql.connector.Error as e:
    print("error", e.errno)
cn.close()

import MySQLdb
m = MySQLdb.connect(host="127.0.0.1", user="root", passwd="", db="cc_py")
cu = m.cursor(); cu.execute("DROP DATABASE cc_py"); m.close()
try:
    pymysql.connect(host="127.0.0.1", port=1, user="root")
except pymysql.err.OperationalError as e:
    print("apagado", "XAMPP" in str(e))
`;
    const r = spawnSync("python3", ["-c", programa], { cwd: dir, env: { ...process.env, PYTHONPATH: dir }, encoding: "utf8" });
    assert.equal(r.status, 0, r.stderr + r.stdout);
    assert.match(r.stdout, /filas 2/);
    assert.match(r.stdout, /integridad 1062/);
    assert.match(r.stdout, /conector 2/, "el INSERT sin commit se deshizo");
    assert.match(r.stdout, /columnas \('txt',\) \["O'Brien \\"x\\" \\\\ ñ", 'Bus'\]|columnas \('txt',\) \[/);
    assert.match(r.stdout, /error 1146/);
    assert.match(r.stdout, /apagado True/);
  });
  fs.rmSync(dir, { recursive: true, force: true });
});
