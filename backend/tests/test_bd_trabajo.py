"""Bases de datos en Trabajo: traducción MySQL→SQLite, conectores de respaldo, .sql del proyecto y bloqueo de SQL peligroso."""
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

RUTA_BD_PY = Path(__file__).resolve().parents[2] / "frontend" / "js" / "trabajo" / "bd_py.py"


def cargar_bd_py():
    m = types.ModuleType("_cc_bdpy_prueba")
    exec(compile(RUTA_BD_PY.read_text(encoding="utf-8"), "bd_py.py", "exec"), m.__dict__)
    return m


class TraduccionTest(unittest.TestCase):
    def setUp(self):
        self.bd = cargar_bd_py()

    def test_crear_tabla_de_phpmyadmin(self):
        t = self.bd.traducir("CREATE TABLE `u` (`id` int(11) NOT NULL AUTO_INCREMENT, `rol` enum('a','b') DEFAULT 'a', PRIMARY KEY (`id`), "
                             "UNIQUE KEY `x` (`rol`), KEY `k` (`rol`)) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COMMENT='hola'")
        self.assertNotIn("AUTO_INCREMENT", t); self.assertNotIn("ENGINE", t); self.assertNotIn("enum", t.lower()); self.assertNotIn("KEY `k`", t)
        self.assertIn("UNIQUE (`rol`)", t)

    def test_parametros_y_varios(self):
        self.assertEqual(self.bd.traducir("SELECT * FROM t WHERE a=%s AND b=%(n)s LIMIT 5, 10"), "SELECT * FROM t WHERE a=? AND b=:n LIMIT 10 OFFSET 5")
        self.assertIsNone(self.bd.traducir("USE tienda"))
        self.assertIsNone(self.bd.traducir("SET FOREIGN_KEY_CHECKS=0"))
        self.assertIn("'%s'", self.bd.traducir("SELECT '%s'"))   # dentro de comillas no se toca

    def test_partir_respeta_comillas(self):
        self.assertEqual(len(self.bd.partir("INSERT INTO t VALUES ('a;b'); -- comentario\nSELECT 1;")), 2)


class RespaldoSQLiteTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.bd = cargar_bd_py()
        self.antes = {k: sys.modules.get(k) for k in ("pymysql", "pymysql.cursors", "mysql", "mysql.connector", "MySQLdb", "psycopg2", "flask_mysqldb", "pymysql.err")}

    def tearDown(self):
        for k, v in self.antes.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_pymysql_y_mysql_connector_sin_servidor(self):
        Path(self.dir, "base de datos").mkdir()
        Path(self.dir, "base de datos", "tienda.sql").write_text(
            "CREATE DATABASE tienda; USE tienda;\nCREATE TABLE p (id INT AUTO_INCREMENT PRIMARY KEY, n VARCHAR(9)) ENGINE=InnoDB;\nINSERT INTO p (n) VALUES ('O\\'Neil'),('Ana');", encoding="utf-8")
        self.bd.preparar(self.dir, puente=False)
        import pymysql
        c = pymysql.connect(host="localhost", user="root", password="", database="tienda", cursorclass=pymysql.cursors.DictCursor)
        with c.cursor() as cur:
            cur.execute("SELECT n FROM p ORDER BY id")
            self.assertEqual([f["n"] for f in cur.fetchall()], ["O'Neil", "Ana"])   # se importó el .sql
            cur.execute("INSERT INTO p (n) VALUES (%s)", ("Luis",))
            self.assertEqual(cur.lastrowid, 3)
        c.commit(); c.close()
        import mysql.connector
        c2 = mysql.connector.connect(host="127.0.0.1", user="root", password="x", database="tienda")
        cur = c2.cursor(dictionary=True); cur.execute("SELECT COUNT(*) AS n FROM p")
        self.assertEqual(cur.fetchone()["n"], 3)
        self.assertTrue(Path(self.dir, ".codigocamp", "bd", "tienda.db").exists())
        with self.assertRaises(pymysql.err.IntegrityError):
            cur.execute("CREATE TABLE u (e VARCHAR(9) UNIQUE)"); cur.execute("INSERT INTO u VALUES ('a')"); cur.execute("INSERT INTO u VALUES ('a')")

    def test_sqlalchemy_con_url_de_mysql(self):
        try:
            import sqlalchemy  # noqa: F401
        except ImportError:
            self.skipTest("sin SQLAlchemy")
        self.bd.preparar(self.dir, puente=False)
        self.bd._parchar_sqlalchemy()
        from sqlalchemy import Column, Integer, String, create_engine
        from sqlalchemy.dialects.mysql import LONGTEXT
        from sqlalchemy.orm import Session, declarative_base
        e = create_engine("mysql+pymysql://root:@localhost:3306/clientes", pool_size=5)
        self.assertEqual(e.dialect.name, "sqlite")
        Base = declarative_base()

        class C(Base):
            __tablename__ = "c"
            id = Column(Integer, primary_key=True)
            n = Column(String(9))
            notas = Column(LONGTEXT)

        Base.metadata.create_all(e)
        with Session(e) as s:
            s.add(C(n="Ana", notas="x")); s.commit()
            self.assertEqual(s.query(C).count(), 1)


class SQLPeligrosoTest(unittest.TestCase):
    def test_bloqueos(self):
        from app import create_app
        from rutas.bd import problema_sql
        app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        with app.app_context():
            for q in ("SELECT * FROM codigocamp.usuarios", "select * from `codigocamp` . `sesiones`", "USE codigocamp",
                      "SELECT 1 INTO OUTFILE '/x.php'", "SELECT LOAD_FILE('/etc/passwd')", "PREPARE s FROM @q", "GRANT ALL ON *.* TO x",
                      "select * from mysql.user", "SET GLOBAL general_log=1", "/* x */ SELECT * FROM codigocamp.usuarios"):
                self.assertIsNotNone(problema_sql(q), q)
            for q in ("SELECT * FROM tienda.usuario", "CREATE TABLE codigo (id int)", "INSERT INTO t VALUES (1)", "SHOW DATABASES"):
                self.assertIsNone(problema_sql(q), q)


if __name__ == "__main__":
    unittest.main()


class PuenteSoloLocalTest(unittest.TestCase):
    """Nadie desde otro computador (o por el túnel) puede usar el MySQL del servidor: podría borrar cualquier base."""

    def setUp(self):
        import utilidades
        from app import create_app
        from models import db
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "BD_EXTERNAS": "1", "ALMACEN_ARCHIVOS": tempfile.mkdtemp()})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()

    def tearDown(self):
        from models import db
        db.session.remove(); db.drop_all(); self.ctx.pop()

    def cliente(self, ip, email):
        from flask import g
        c = self.app.test_client(); c.environ_base["REMOTE_ADDR"] = ip
        g.pop("_login_user", None); c.get("/api/auth/me/")
        h = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        g.pop("_login_user", None)
        c.post("/api/auth/register/", json={"nombre": "Prueba", "email": email, "password": "Clave123"}, headers=h)
        return c, h

    def test_remoto_bloqueado_local_permitido(self):
        from flask import g
        lejos, h = self.cliente("181.50.10.20", "lejos@example.com")
        g.pop("_login_user", None)
        self.assertFalse(lejos.get("/api/bd/estado").get_json()["activo"])
        g.pop("_login_user", None)
        r = lejos.post("/api/bd/consulta", json={"sesion": "x", "sql": "DROP DATABASE finanbot_db"}, headers=h)
        self.assertEqual(r.status_code, 403); self.assertIn("no permite conectar", r.get_json()["error"])
        cerca, h2 = self.cliente("127.0.0.1", "cerca@example.com")
        g.pop("_login_user", None)
        self.assertTrue(cerca.get("/api/bd/estado").get_json()["activo"])
        self.app.config["BD_USUARIOS"] = "lejos@example.com"
        g.pop("_login_user", None)
        self.assertTrue(lejos.get("/api/bd/estado").get_json()["activo"])   # cuenta autorizada desde cualquier lugar
        g.pop("_login_user", None)
        self.assertFalse(cerca.get("/api/bd/estado").get_json()["activo"])  # con lista, solo los de la lista
