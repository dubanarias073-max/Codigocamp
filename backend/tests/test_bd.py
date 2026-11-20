"""Bases de datos externas (MySQL/MariaDB del usuario). Las pruebas con «real» usan un MySQL en 127.0.0.1:3306
(root sin clave, como XAMPP); si no hay ninguno encendido, se saltan."""
import json
import threading
import unittest
import urllib.error
import urllib.request

import pymysql

import utilidades
from app import create_app
from models import db
from rutas import bd as modulo
from servicios.bd_externa import Sesiones, host_permitido


def _hay_mysql():
    try:
        pymysql.connect(host="127.0.0.1", user="root", password="", connect_timeout=1).close()
        return True
    except Exception:
        return False


HAY_MYSQL = _hay_mysql()


class HostsTest(unittest.TestCase):
    def test_hosts_permitidos(self):
        locales = ["localhost", "127.0.0.1", "::1"]
        self.assertTrue(host_permitido("localhost", locales))
        self.assertTrue(host_permitido("LOCALHOST", locales))
        self.assertFalse(host_permitido("10.0.0.5", locales))
        self.assertFalse(host_permitido("169.254.169.254", locales))
        self.assertTrue(host_permitido("192.168.1.40", ["192.168.1.0/24"]))
        self.assertFalse(host_permitido("192.168.2.40", ["192.168.1.0/24"]))
        self.assertTrue(host_permitido("db.ejemplo.com", ["*"]))
        self.assertFalse(host_permitido("", ["*"]))


class RutasBDTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        modulo.SESIONES.cerrar_de(1)
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "test-secret", "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_COOKIE_SECURE": False, "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "BD_EXTERNAS": "1",
        })
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.client.get("/api/auth/me/")
        self.csrf = {"X-CSRFToken": self.client.get_cookie("csrftoken").value}
        r = self.client.post("/api/auth/register/", json={"nombre": "Ana", "email": "ana@example.com", "password": "Clave123"}, headers=self.csrf)
        self.assertEqual(r.status_code, 201)

    def tearDown(self):
        modulo.SESIONES.cerrar_de(1)
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()

    def post(self, accion, datos):
        return self.client.post(f"/api/bd/{accion}", json=datos, headers=self.csrf)

    def test_sin_sesion_o_desactivado_no_se_puede(self):
        self.app.config["BD_EXTERNAS"] = "0"
        self.assertEqual(self.client.get("/api/bd/estado").get_json()["activo"], False)
        self.assertEqual(self.post("conectar", {"host": "127.0.0.1"}).status_code, 403)
        self.client.post("/api/auth/logout/", headers=self.csrf)
        self.assertEqual(self.client.get("/api/bd/estado").status_code, 401)

    def test_no_conecta_a_hosts_no_permitidos_ni_a_la_base_de_codigocamp(self):
        r = self.post("conectar", {"host": "169.254.169.254"})
        self.assertEqual(r.status_code, 403)
        self.assertIn("No se permite", r.get_json()["error"])
        r = self.post("conectar", {"host": "127.0.0.1", "base": "codigocamp"})
        self.assertEqual(r.status_code, 403)
        r = self.post("consulta", {"sesion": "x", "sql": "USE `codigocamp`;"})
        self.assertEqual(r.status_code, 403)

    def test_sesion_desconocida(self):
        r = self.post("consulta", {"sesion": "nada", "sql": "SELECT 1"})
        self.assertEqual(r.status_code, 410)

    @unittest.skipUnless(HAY_MYSQL, "no hay MySQL en 127.0.0.1:3306")
    def test_real_conectar_consultar_insertar_y_errores(self):
        r = self.post("conectar", {"host": "localhost", "usuario": "root", "clave": ""})
        self.assertEqual(r.status_code, 200, r.get_json())
        s = r.get_json()["sesion"]
        q = lambda sql, p=None: self.post("consulta", {"sesion": s, "sql": sql, **({"parametros": p} if p is not None else {})})
        self.assertEqual(q("CREATE DATABASE IF NOT EXISTS cc_prueba").status_code, 200)
        j = q("USE cc_prueba").get_json()
        self.assertEqual(j["base"], "cc_prueba")
        q("DROP TABLE IF EXISTS t")
        q("CREATE TABLE t (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(20), precio DECIMAL(8,2), dia DATE, foto BLOB)")
        j = q("INSERT INTO t (nombre, precio, dia, foto) VALUES (%s, %s, %s, UNHEX('FF00'))", ["Pan ñ", "2.50", "2026-11-19"]).get_json()
        self.assertEqual((j["afectadas"], j["ultimo_id"]), (1, 1))
        j = q("SELECT * FROM t").get_json()
        self.assertEqual(j["columnas"], ["id", "nombre", "precio", "dia", "foto"])
        self.assertEqual(j["filas"], [[1, "Pan ñ", "2.50", "2026-11-19", {"$bytes": "ff00"}]])
        r = q("SELECT * FROM no_existe")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["codigo"], 1146)
        self.assertIn("ERROR 1146", r.get_json()["error"])
        q("DROP DATABASE cc_prueba")
        self.assertTrue(self.post("cerrar", {"sesion": s}).get_json()["cerrada"])
        self.assertEqual(q("SELECT 1").status_code, 410)

    @unittest.skipUnless(HAY_MYSQL, "no hay MySQL en 127.0.0.1:3306")
    def test_real_otro_usuario_no_usa_tu_conexion(self):
        s = self.post("conectar", {"host": "127.0.0.1"}).get_json()["sesion"]
        otro = self.app.test_client()
        otro.get("/api/auth/me/")
        csrf = {"X-CSRFToken": otro.get_cookie("csrftoken").value}
        otro.post("/api/auth/register/", json={"nombre": "Eva", "email": "eva@example.com", "password": "Clave123"}, headers=csrf)
        self.assertEqual(otro.post("/api/bd/consulta", json={"sesion": s, "sql": "SELECT 1"}, headers=csrf).status_code, 410)
        modulo.SESIONES.cerrar_de(2)

    def test_mysql_apagado_da_un_mensaje_claro(self):
        r = self.post("conectar", {"host": "127.0.0.1", "puerto": 1})
        self.assertEqual(r.status_code, 400)
        self.assertIn("XAMPP", r.get_json()["error"])


class PuenteTest(unittest.TestCase):
    def setUp(self):
        from herramientas.puente_bd import crear_servidor
        self.srv = crear_servidor(puerto=0, clave="secreta", sesiones=Sesiones())
        self.url = f"http://127.0.0.1:{self.srv.server_address[1]}"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def pedir(self, ruta, datos=None, clave="secreta", metodo=None):
        req = urllib.request.Request(self.url + ruta, data=json.dumps(datos).encode() if datos is not None else None, method=metodo,
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {clave}", "Origin": "https://codigocamp.ejemplo"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read() or b"{}"), r.headers
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}"), e.headers

    def test_pide_clave_y_responde_cors_de_red_privada(self):
        estado, _, _ = self.pedir("/api/bd/estado", clave="mala")
        self.assertEqual(estado, 401)
        estado, j, h = self.pedir("/api/bd/estado")
        self.assertEqual((estado, j["activo"]), (200, True))
        estado, _, h = self.pedir("/api/bd/consulta", metodo="OPTIONS")
        self.assertEqual(estado, 204)
        self.assertEqual(h["Access-Control-Allow-Private-Network"], "true")
        self.assertEqual(h["Access-Control-Allow-Origin"], "https://codigocamp.ejemplo")
        self.assertEqual(self.pedir("/api/bd/conectar", {"host": "8.8.8.8"})[0], 403)

    @unittest.skipUnless(HAY_MYSQL, "no hay MySQL en 127.0.0.1:3306")
    def test_real_por_el_puente(self):
        estado, j, _ = self.pedir("/api/bd/conectar", {"usuario": "root"})
        self.assertEqual(estado, 200, j)
        estado, j, _ = self.pedir("/api/bd/consulta", {"sesion": j["sesion"], "sql": "SELECT 1 + 1 AS dos"})
        self.assertEqual((estado, j["columnas"], j["filas"]), (200, ["dos"], [[2]]))


if __name__ == "__main__":
    unittest.main()


def _hay(motor):
    try:
        if motor == "postgres":
            import pg8000.dbapi
            pg8000.dbapi.connect(host="127.0.0.1", user="postgres", password="postgres", timeout=1).close()
        elif motor == "redis":
            import redis
            redis.Redis(socket_connect_timeout=1).ping()
        return True
    except Exception:
        return False


class MotoresTest(unittest.TestCase):
    def setUp(self):
        self.s = Sesiones()

    def tearDown(self):
        self.s.cerrar_de("yo")

    @unittest.skipUnless(_hay("postgres"), "no hay PostgreSQL en 127.0.0.1:5432")
    def test_postgres_real(self):
        r = self.s.abrir("yo", "postgres", usuario="postgres", clave="postgres")
        self.assertEqual(r["motor"], "postgres")
        q = lambda sql, p=None: self.s.consultar("yo", r["sesion"], {"sql": sql, "parametros": p})
        q("DROP TABLE IF EXISTS cc_t")
        self.assertEqual(q("CREATE TABLE cc_t (id SERIAL PRIMARY KEY, nombre TEXT, datos JSONB, precio NUMERIC(8,2))")["comando"], "CREATE TABLE")
        j = q("INSERT INTO cc_t (nombre, datos, precio) VALUES (%s, %s, %s), ('b', NULL, 1)", ["Ana ñ", '{"a": 1}', "2.50"])
        self.assertEqual((j["comando"], j["afectadas"]), ("INSERT 0 2", 2))
        j = q("SELECT id, nombre, datos, precio FROM cc_t ORDER BY id")
        self.assertEqual(j["columnas"], ["id", "nombre", "datos", "precio"])
        self.assertEqual(j["filas"][0], [1, "Ana ñ", {"$json": '{"a": 1}'}, "2.50"])
        with self.assertRaises(Exception) as e:
            q("SELECT * FROM no_existe")
        self.assertIn('relation "no_existe" does not exist', str(e.exception))
        self.assertEqual(e.exception.codigo, "42P01")
        self.assertEqual(q("SELECT 1 AS uno")["filas"], [[1]], "tras un error la conexión sigue usable")
        q("DROP TABLE cc_t")

    @unittest.skipUnless(_hay("redis"), "no hay Redis en 127.0.0.1:6379")
    def test_redis_real(self):
        r = self.s.abrir("yo", "redis")
        q = lambda *c: self.s.consultar("yo", r["sesion"], {"comando": list(c)})["resultado"]
        self.assertEqual(q("SET", "cc:clave", "hola ñ"), "OK")
        self.assertEqual(q("GET", "cc:clave"), "hola ñ")
        self.assertEqual(q("RPUSH", "cc:lista", "a", "b"), 2)
        self.assertEqual(q("LRANGE", "cc:lista", 0, -1), ["a", "b"])
        self.assertEqual(q("DEL", "cc:clave", "cc:lista"), 2)
        with self.assertRaises(Exception) as e:
            q("MONITOR")
        self.assertIn("no está disponible", str(e.exception))
        with self.assertRaises(Exception) as e:
            q("NOEXISTE")
        self.assertIn("(error)", str(e.exception))

    def test_mongodb(self):
        import mongomock
        cliente = mongomock.MongoClient()
        cliente.server_info = lambda: {"version": "7.0.0", "versionArray": [7, 0, 0, 0]}
        s = Sesiones(conectores={"mongodb": lambda *a, **k: cliente})
        r = s.abrir("yo", "mongodb", uri="mongodb://localhost:27017/finanbot")
        self.assertEqual(r["base"], "finanbot")
        q = lambda op, col=None, *args, **op2: s.consultar("yo", r["sesion"], {"operacion": op, "coleccion": col, "args": list(args), "opciones": op2})["resultado"]
        ins = q("insert_many", "gastos", [{"concepto": "Bus", "valor": 2950, "fecha": {"$date": "2026-11-19T00:00:00Z"}}, {"concepto": "Café", "valor": 4500}])
        self.assertTrue(ins["acknowledged"])
        self.assertIn("$oid", ins["insertedIds"]["0"])
        docs = q("find", "gastos", {"valor": {"$gt": 3000}})
        self.assertEqual([d["concepto"] for d in docs], ["Café"])
        self.assertEqual(q("find", "gastos", {}, sort={"valor": -1}, limit=1)[0]["concepto"], "Café")
        self.assertEqual(q("find_one", "gastos", {"concepto": "Bus"})["fecha"], {"$date": "2026-11-19T00:00:00Z"})
        self.assertEqual(q("update_one", "gastos", {"concepto": "Bus"}, {"$set": {"valor": 3000}})["modifiedCount"], 1)
        self.assertEqual(q("count_documents", "gastos", {}), 2)
        self.assertEqual(q("aggregate", "gastos", [{"$group": {"_id": None, "total": {"$sum": "$valor"}}}])[0]["total"], 7500)
        self.assertEqual(q("list_collection_names"), ["gastos"])
        self.assertEqual(q("delete_many", "gastos", {})["deletedCount"], 2)
        with self.assertRaises(Exception):
            q("__class__", "gastos")
        s.cerrar_de("yo")
