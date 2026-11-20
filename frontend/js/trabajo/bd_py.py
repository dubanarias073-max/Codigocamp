# Bases de datos en Trabajo (Python dentro del navegador).
# En el navegador no existen conexiones de red a MySQL/MariaDB/PostgreSQL/MongoDB: no hay sockets.
# Para que tu app Flask, FastAPI o Django funcione igual que en tu PC, aquí se usa una base SQLite REAL
# dentro de tu proyecto (.codigocamp/bd/<nombre>.db) que se guarda con el proyecto:
#   · SQLAlchemy / Flask-SQLAlchemy / SQLModel:   mysql+pymysql://..., postgresql://...  ->  sqlite:///.codigocamp/bd/<base>.db
#   · pymysql, mysql.connector, MySQLdb, flask_mysqldb, psycopg2:  la misma API (cursor, execute, %s, commit...)
#   · pymongo:  mongomock con los datos guardados en .codigocamp/bd/mongo-<base>.json
# Si el proyecto trae un .sql (por ejemplo «base de datos/tienda.sql»), se importa la primera vez.
# En tu PC no cambia nada: este archivo solo existe dentro de CódigoCamp.
import json
import os
import re
import sys
import types

try:   # en Pyodide sqlite3 es un paquete aparte (Trabajo lo carga antes); sin él, solo funciona el puente
    import sqlite3
except ImportError:  # pragma: no cover
    sqlite3 = None

_CC_RAIZ = "/workspace"
_CC_AVISADOS = set()
_CC_MOTORES = {"mysql", "mariadb", "postgresql", "postgres", "mssql", "oracle", "psycopg2", "pymysql"}


def _cc_aviso(clave, texto):
    if clave not in _CC_AVISADOS:
        _CC_AVISADOS.add(clave)
        print(f"\x1b[36mℹ Trabajo:\x1b[0m {texto}", file=sys.stderr)


def _cc_carpeta():
    ruta = os.path.join(_CC_RAIZ, ".codigocamp", "bd")
    os.makedirs(ruta, exist_ok=True)
    return ruta


def _cc_nombre(base):
    base = re.sub(r"[^\w\-]+", "_", str(base or "").strip()) or "base"
    return base[:60]


def ruta_sqlite(base):
    return os.path.join(_cc_carpeta(), _cc_nombre(base) + ".db")


# ----------------------------------------------------------------------------- SQL de MySQL a SQLite --
_QUITAR = [
    r"\bENGINE\s*=\s*\w+", r"\bDEFAULT\s+CHARSET\s*=\s*\w+", r"\b(?:DEFAULT\s+)?CHARACTER\s+SET\s*=?\s*\w+", r"\bCHARSET\s*=\s*\w+",
    r"\bCOLLATE\s*=?\s*\w+", r"\bAUTO_INCREMENT\s*=\s*\d+", r"\bROW_FORMAT\s*=\s*\w+", r"\bUNSIGNED\b", r"\bZEROFILL\b",
    r"\bON\s+UPDATE\s+CURRENT_TIMESTAMP(?:\(\))?", r"\bCOMMENT\s*=?\s*'(?:[^'\\]|\\.)*'", r"/\*!\d+.*?\*/",
]
_NO_OP = re.compile(r"^\s*(?:CREATE\s+(?:DATABASE|SCHEMA)|DROP\s+(?:DATABASE|SCHEMA)|USE\s|SET\s|LOCK\s+TABLES|UNLOCK\s+TABLES|START\s+TRANSACTION|DELIMITER|ALTER\s+DATABASE|GRANT\s|FLUSH\s|COMMIT\s*;?\s*$)", re.I)


def _fuera_de_comillas(sql, funcion):
    """Aplica `funcion` solo a los trozos de SQL que no están entre comillas."""
    partes = re.split(r"('(?:[^'\\]|\\.|'')*'|\"(?:[^\"\\]|\\.)*\")", sql)
    return "".join(p if i % 2 else funcion(p) for i, p in enumerate(partes))


def traducir(sql, estilo="mysql"):
    """Traduce lo más común de MySQL/PostgreSQL a SQLite. Devuelve None si la orden no hace falta aquí (USE, SET...)."""
    if _NO_OP.match(sql):
        return None

    def cambiar(t):
        for patron in _QUITAR:
            t = re.sub(patron, "", t, flags=re.I | re.S)
        # id INT AUTO_INCREMENT PRIMARY KEY  /  id SERIAL PRIMARY KEY  ->  id INTEGER PRIMARY KEY AUTOINCREMENT
        t = re.sub(r"(\b[`\"]?\w+[`\"]?\s+)(?:BIG|SMALL|TINY|MEDIUM)?INT(?:EGER)?(?:\s*\(\d+\))?((?:\s+NOT\s+NULL)?)\s+(?:AUTO_INCREMENT\s+PRIMARY\s+KEY|PRIMARY\s+KEY\s+AUTO_INCREMENT)",
                   r"\1INTEGER PRIMARY KEY AUTOINCREMENT", t, flags=re.I)
        t = re.sub(r"(\b[`\"]?\w+[`\"]?\s+)(?:BIG|SMALL)?SERIAL\s+PRIMARY\s+KEY", r"\1INTEGER PRIMARY KEY AUTOINCREMENT", t, flags=re.I)
        t = re.sub(r"(\b[`\"]?\w+[`\"]?\s+)(?:BIG|SMALL)?SERIAL\b", r"\1INTEGER", t, flags=re.I)
        t = re.sub(r"\b(?:BIG|SMALL|TINY|MEDIUM)?INT(?:EGER)?(?:\s*\(\d+\))?((?:\s+NOT\s+NULL)?)\s+AUTO_INCREMENT", r"INTEGER\1", t, flags=re.I)
        t = re.sub(r"\bAUTO_INCREMENT\b", "", t, flags=re.I)
        t = re.sub(r"\bGENERATED\s+(?:ALWAYS|BY\s+DEFAULT)\s+AS\s+IDENTITY", "", t, flags=re.I)
        # Índices dentro de CREATE TABLE (SQLite no los acepta ahí)
        t = re.sub(r",\s*UNIQUE\s+(?:KEY|INDEX)\s+[`\"]?\w+[`\"]?\s*(\([^)]*\))", r", UNIQUE \1", t, flags=re.I)
        t = re.sub(r",\s*(?:FULLTEXT\s+|SPATIAL\s+)?(?:KEY|INDEX)\s+[`\"]?\w+[`\"]?\s*\([^)]*\)", "", t, flags=re.I)
        t = re.sub(r"\bENUM\s*\([^)]*\)", "TEXT", t, flags=re.I)
        t = re.sub(r"\bSET\s*\('[^)]*\)", "TEXT", t, flags=re.I)
        t = re.sub(r"\b(?:TINY|MEDIUM|LONG)TEXT\b", "TEXT", t, flags=re.I)
        t = re.sub(r"\b(?:TINY|MEDIUM|LONG)BLOB\b", "BLOB", t, flags=re.I)
        t = re.sub(r"\bNOW\s*\(\s*\)|\bCURRENT_TIMESTAMP\s*\(\s*\)", "CURRENT_TIMESTAMP", t, flags=re.I)
        t = re.sub(r"\bCURDATE\s*\(\s*\)", "CURRENT_DATE", t, flags=re.I)
        t = re.sub(r"\bINSERT\s+IGNORE\b", "INSERT OR IGNORE", t, flags=re.I)
        t = re.sub(r"\bLIMIT\s+(\d+)\s*,\s*(\d+)", r"LIMIT \2 OFFSET \1", t, flags=re.I)
        t = re.sub(r"::\w+(\[\])?", "", t)   # conversiones de PostgreSQL: '1'::int
        t = re.sub(r"\bILIKE\b", "LIKE", t, flags=re.I)
        t = re.sub(r"\bTRUE\b", "1", t, flags=re.I)
        t = re.sub(r"\bFALSE\b", "0", t, flags=re.I)
        # Marcadores de parámetros: %s -> ?, %(nombre)s -> :nombre
        t = re.sub(r"%\((\w+)\)s", r":\1", t)
        t = t.replace("%s", "?")
        return t

    # Lo que lleva comillas por dentro se cambia antes de separar los textos entre comillas.
    lista = r"\(\s*(?:'(?:[^'\\]|\\.|'')*'\s*,?\s*)+\)"
    sql = re.sub(r"\b(?:ENUM|SET)\s*" + lista, "TEXT", sql, flags=re.I)
    sql = re.sub(r"\bCOMMENT\s*=?\s*'(?:[^'\\]|\\.|'')*'", "", sql, flags=re.I)
    sql = _fuera_de_comillas(sql, cambiar)
    if estilo == "mysql":
        sql = re.sub(r"\\'", "''", sql)   # 'O\'Brien' de MySQL -> 'O''Brien'
    s = sql.strip()
    if re.match(r"^SHOW\s+TABLES", s, re.I):
        return "SELECT name AS Tables_in_base FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    m = re.match(r"^(?:DESCRIBE|DESC|SHOW\s+COLUMNS\s+FROM)\s+[`\"]?(\w+)[`\"]?", s, re.I)
    if m:
        return f"SELECT name AS Field, type AS Type, CASE WHEN \"notnull\" THEN 'NO' ELSE 'YES' END AS \"Null\", CASE WHEN pk THEN 'PRI' ELSE '' END AS \"Key\", dflt_value AS \"Default\" FROM pragma_table_info('{m.group(1)}')"
    return sql


def partir(script):
    """Divide un archivo .sql en órdenes (respeta ; dentro de comillas y quita comentarios)."""
    script = re.sub(r"^\s*--.*$|^\s*#.*$", "", script, flags=re.M)
    ordenes, actual, comilla = [], [], None
    i = 0
    while i < len(script):
        c = script[i]
        if comilla:
            actual.append(c)
            if c == "\\" and i + 1 < len(script):
                actual.append(script[i + 1]); i += 2; continue
            if c == comilla:
                comilla = None
        elif c in "'\"`":
            comilla = c; actual.append(c)
        elif c == ";":
            ordenes.append("".join(actual)); actual = []
        elif script.startswith("/*", i) and not script.startswith("/*!", i):
            fin = script.find("*/", i + 2)
            i = len(script) if fin < 0 else fin + 2
            continue
        else:
            actual.append(c)
        i += 1
    ordenes.append("".join(actual))
    return [o.strip() for o in ordenes if o.strip()]


def _archivos_sql(base):
    """Los .sql del proyecto, primero el que crea o usa esta base."""
    encontrados = []
    for carpeta, dirs, archivos in os.walk(_CC_RAIZ):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".codigocamp", "venv", ".venv", "env", "__pycache__", "site-packages"}]
        for a in archivos:
            if a.lower().endswith(".sql"):
                ruta = os.path.join(carpeta, a)
                try:
                    with open(ruta, encoding="utf-8", errors="replace") as f:
                        texto = f.read(2_000_000)
                except OSError:
                    continue
                if re.search(r"CREATE\s+TABLE", texto, re.I):
                    nombre = _cc_nombre(base).lower()
                    puntos = 2 if re.search(rf"(?:CREATE\s+DATABASE|USE)\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?{re.escape(nombre)}[`\"]?", texto, re.I) else 1 if nombre in a.lower() else 0
                    encontrados.append((puntos, ruta, texto))
    encontrados.sort(key=lambda x: -x[0])
    return encontrados


def importar_sql(con, base, estilo="mysql"):
    """Primera vez que se crea la base: ejecuta el .sql del proyecto (tablas y datos), traducido a SQLite."""
    archivos = _archivos_sql(base)
    if not archivos:
        return
    puntos, ruta, texto = archivos[0]
    if puntos == 0 and len(archivos) > 1:
        return   # varios .sql y ninguno coincide con el nombre: mejor no adivinar
    ok = fallos = 0
    primer_error = ""
    con.execute("PRAGMA foreign_keys=OFF")
    for orden in partir(texto):
        t = traducir(orden, estilo)
        if not t:
            continue
        try:
            con.execute(t); ok += 1
        except sqlite3.Error as e:
            fallos += 1
            primer_error = primer_error or f"{e} en: {orden[:90]}"
    con.commit()
    con.execute("PRAGMA foreign_keys=ON")
    rel = os.path.relpath(ruta, _CC_RAIZ)
    _cc_aviso("sql:" + rel, f"importé {rel} en la base «{base}» ({ok} órdenes" + (f", {fallos} no se pudieron: {primer_error}" if fallos else "") + ").")


def abrir_sqlite(base, estilo="mysql", motor="MySQL", desde=""):
    if sqlite3 is None:
        raise OperationalError(2003, f"No se pudo conectar a {motor} y SQLite no está disponible en este navegador.")
    ruta = ruta_sqlite(base)
    nueva = not os.path.exists(ruta)
    con = sqlite3.connect(ruta, check_same_thread=False)
    con.execute("PRAGMA foreign_keys=ON")
    if nueva:
        _cc_aviso("bd:" + _cc_nombre(base), f"tu app usa {motor}{' (' + desde + ')' if desde else ''}. En el navegador no hay conexión a servidores de base de datos, "
                  f"así que uso una base SQLite real en .codigocamp/bd/{_cc_nombre(base)}.db (se guarda con tu proyecto). En tu PC seguirá usando {motor}.")
        importar_sql(con, base, estilo)
    return con


# ---------------------------------------------------------------- DB-API compatible (pymysql, mysql.connector, psycopg2) --
class Error(Exception):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class OperationalError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class DataError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass


class InternalError(DatabaseError):
    pass


def _convertir_error(e):
    texto = str(e)
    if isinstance(e, sqlite3.IntegrityError):
        codigo = 1062 if "UNIQUE" in texto else 1452 if "FOREIGN KEY" in texto else 1048
        return IntegrityError(codigo, texto)
    if isinstance(e, sqlite3.OperationalError):
        if "no such table" in texto:
            return ProgrammingError(1146, texto.replace("no such table", "Table doesn't exist") + "  (Trabajo: crea la tabla o agrega tu .sql al proyecto)")
        if "syntax error" in texto:
            return ProgrammingError(1064, texto)
        return OperationalError(1054 if "no such column" in texto else 2000, texto)
    return DatabaseError(texto)


class Cursor:
    def __init__(self, conexion, dict_=False, nombrado=False):
        self.connection = conexion
        self._c = conexion._con.cursor()
        self.dict = dict_
        self.nombrado = nombrado
        self.description = None
        self.rowcount = -1
        self.lastrowid = None
        self.arraysize = 1
        self._filas = None

    # --- con with ---
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __iter__(self):
        while True:
            fila = self.fetchone()
            if fila is None:
                return
            yield fila

    def _adaptar(self, params):
        if params is None:
            return ()
        if isinstance(params, dict):
            return params
        if not isinstance(params, (list, tuple)):
            return (params,)
        return tuple(params)

    def execute(self, sql, params=None, multi=False):
        if isinstance(sql, bytes):
            sql = sql.decode()
        ordenes = partir(sql) if (multi or sql.count(";") > 1) and params is None else [sql]
        for orden in ordenes:
            t = traducir(orden, self.connection._estilo)
            if t is None:
                self.description, self.rowcount = None, 0
                continue
            try:
                self._c.execute(t, self._adaptar(params))
            except sqlite3.Error as e:
                raise _convertir_error(e) from None
            self.description = self._c.description
            self.rowcount = self._c.rowcount
            self.lastrowid = self._c.lastrowid
            self._filas = None
        if self.connection.autocommit_activo:
            self.connection._con.commit()
        return self.rowcount

    def executemany(self, sql, seq):
        t = traducir(sql, self.connection._estilo)
        try:
            self._c.executemany(t, [self._adaptar(p) for p in seq])
        except sqlite3.Error as e:
            raise _convertir_error(e) from None
        self.rowcount = self._c.rowcount
        self.lastrowid = self._c.lastrowid
        return self.rowcount

    def _forma(self, fila):
        if fila is None or not self.dict:
            return fila
        return {d[0]: v for d, v in zip(self.description or [], fila)}

    def fetchone(self):
        return self._forma(self._c.fetchone())

    def fetchall(self):
        return [self._forma(f) for f in self._c.fetchall()]

    def fetchmany(self, n=None):
        return [self._forma(f) for f in self._c.fetchmany(n or self.arraysize)]

    def callproc(self, *a, **k):
        raise NotSupportedError("Los procedimientos almacenados (CALL) no existen en Trabajo; escribe la consulta en Python.")

    def scroll(self, *a, **k):
        raise NotSupportedError("scroll() no está disponible en Trabajo.")

    def close(self):
        try:
            self._c.close()
        except Exception:  # noqa: BLE001
            pass

    @property
    def column_names(self):   # mysql.connector
        return tuple(d[0] for d in self.description or [])

    @property
    def with_rows(self):      # mysql.connector
        return bool(self.description)


class DictCursor(Cursor):
    def __init__(self, conexion):
        super().__init__(conexion, dict_=True)


class Conexion:
    def __init__(self, base, estilo="mysql", motor="MySQL", desde="", dict_por_defecto=False, autocommit=False):
        self._estilo = estilo
        self._con = abrir_sqlite(base, estilo, motor, desde)
        self._dict = dict_por_defecto
        self.autocommit_activo = bool(autocommit)
        self.open = True
        self.database = base

    def __enter__(self):
        return self

    def __exit__(self, tipo, *a):
        if tipo is None:
            self.commit()
        else:
            self.rollback()

    def cursor(self, cursor=None, dictionary=False, buffered=None, cursor_factory=None, named_tuple=False, prepared=None, **k):
        clase = cursor or cursor_factory
        if clase is not None and isinstance(clase, type) and issubclass(clase, Cursor):
            return clase(self)
        es_dict = dictionary or self._dict or (clase is not None and "dict" in getattr(clase, "__name__", "").lower())
        return Cursor(self, dict_=es_dict)

    def commit(self):
        self._con.commit()

    def rollback(self):
        self._con.rollback()

    def close(self):
        if self.open:
            try:
                self._con.commit()
            finally:
                self._con.close()
                self.open = False

    def autocommit(self, valor=True):   # pymysql: conn.autocommit(True)
        self.autocommit_activo = bool(valor)

    def ping(self, reconnect=True):
        return True

    def is_connected(self):              # mysql.connector
        return self.open

    def select_db(self, base):
        self.close()
        self.__init__(base, self._estilo)

    def begin(self):
        pass

    @property
    def server_version(self):
        return "8.0.0-codigocamp-sqlite"

    def get_server_info(self):
        return self.server_version


def _base_de(kw, dsn=None):
    base = kw.get("database") or kw.get("db") or kw.get("dbname")
    if not base and dsn:
        m = re.search(r"dbname\s*=\s*(\w+)", dsn) or re.search(r"/(\w+)(?:\?|$)", dsn)
        base = m.group(1) if m else None
    return base or "base"


def _crear_modulos():
    """Módulos falsos (pero funcionales) con el nombre de los conectores reales."""
    errores = dict(Error=Error, InterfaceError=InterfaceError, DatabaseError=DatabaseError, OperationalError=OperationalError,
                   IntegrityError=IntegrityError, ProgrammingError=ProgrammingError, DataError=DataError,
                   NotSupportedError=NotSupportedError, InternalError=InternalError, MySQLError=Error, Warning=Warning)

    # pymysql
    pm = types.ModuleType("pymysql")
    pm.__dict__.update(errores)
    pm.err = types.ModuleType("pymysql.err"); pm.err.__dict__.update(errores)
    pm.cursors = types.ModuleType("pymysql.cursors")
    pm.cursors.Cursor, pm.cursors.DictCursor, pm.cursors.SSCursor, pm.cursors.SSDictCursor = Cursor, DictCursor, Cursor, DictCursor

    def pm_connect(*a, **kw):
        base = _base_de(kw)
        return Conexion(base, "mysql", "MySQL", f"{kw.get('host', 'localhost')}/{base}", dict_por_defecto=kw.get("cursorclass") is DictCursor, autocommit=kw.get("autocommit", False))

    pm.connect = pm.Connect = pm.Connection = pm_connect
    pm.paramstyle, pm.apilevel, pm.threadsafety, pm.version_info, pm.__version__ = "pyformat", "2.0", 1, (1, 4, 6, "final", 0), "1.1.0"
    pm.escape_string = lambda s: str(s).replace("\\", "\\\\").replace("'", "\\'")

    def install_as_MySQLdb():
        sys.modules["MySQLdb"] = mysqldb
        sys.modules["MySQLdb.cursors"] = mysqldb.cursors

    pm.install_as_MySQLdb = install_as_MySQLdb

    # MySQLdb (mysqlclient)
    mysqldb = types.ModuleType("MySQLdb")
    mysqldb.__dict__.update(errores)
    mysqldb.cursors = pm.cursors
    mysqldb.connect = mysqldb.Connect = mysqldb.Connection = lambda *a, **kw: pm_connect(**{**kw, "database": kw.get("db") or kw.get("database")})
    mysqldb._mysql = types.ModuleType("MySQLdb._mysql")

    # mysql.connector
    my = types.ModuleType("mysql")
    mc = types.ModuleType("mysql.connector")
    mc.__dict__.update(errores)
    mc.errors = types.ModuleType("mysql.connector.errors"); mc.errors.__dict__.update(errores)
    mc.errorcode = types.SimpleNamespace(ER_ACCESS_DENIED_ERROR=1045, ER_BAD_DB_ERROR=1049, ER_DUP_ENTRY=1062, ER_NO_SUCH_TABLE=1146)

    def mc_connect(*a, **kw):
        base = _base_de(kw)
        return Conexion(base, "mysql", "MySQL", f"{kw.get('host', 'localhost')}/{base}", autocommit=kw.get("autocommit", False))

    mc.connect = mc.Connect = mc_connect
    mc.MySQLConnection = mc.CMySQLConnection = Conexion
    mc.pooling = types.ModuleType("mysql.connector.pooling")

    class MySQLConnectionPool:
        def __init__(self, pool_name=None, pool_size=5, **kw):
            self.kw = kw

        def get_connection(self):
            return mc_connect(**self.kw)

    mc.pooling.MySQLConnectionPool = MySQLConnectionPool
    my.connector = mc

    # psycopg2
    pg = types.ModuleType("psycopg2")
    pg.__dict__.update(errores)
    pg.extras = types.ModuleType("psycopg2.extras")

    class RealDictCursor(DictCursor):
        pass

    pg.extras.RealDictCursor = pg.extras.DictCursor = RealDictCursor
    pg.errors = types.ModuleType("psycopg2.errors"); pg.errors.__dict__.update(errores)
    pg.errors.UniqueViolation = IntegrityError

    def pg_connect(dsn=None, **kw):
        base = _base_de(kw, dsn)
        c = Conexion(base, "postgres", "PostgreSQL", f"{kw.get('host', 'localhost')}/{base}")
        if kw.get("cursor_factory"):
            c._dict = True
        return c

    pg.connect = pg_connect
    pg.paramstyle = "pyformat"
    pg.sql = types.ModuleType("psycopg2.sql")
    pg.sql.SQL = pg.sql.Identifier = pg.sql.Literal = str

    # flask_mysqldb (MySQL(app); mysql.connection.cursor())
    fm = types.ModuleType("flask_mysqldb")

    class MySQL:
        def __init__(self, app=None):
            self.app = app
            self._con = None
            if app is not None:
                self.init_app(app)

        def init_app(self, app):
            self.app = app
            app.teardown_appcontext(self._cerrar)

        def _cerrar(self, *_):
            pass   # la misma conexión sirve para todas las peticiones (no hay hilos)

        @property
        def connection(self):
            if self._con is None or not getattr(self._con, "open", True):
                cfg = self.app.config if self.app is not None else {}
                pm = sys.modules.get("pymysql")
                dicc = cfg.get("MYSQL_CURSORCLASS") == "DictCursor"
                self._con = pm.connect(host=cfg.get("MYSQL_HOST", "localhost"), user=cfg.get("MYSQL_USER", "root"),
                                       password=cfg.get("MYSQL_PASSWORD", ""), database=cfg.get("MYSQL_DB") or cfg.get("MYSQL_DATABASE"),
                                       port=int(cfg.get("MYSQL_PORT", 3306) or 3306), **({"cursorclass": pm.cursors.DictCursor} if dicc else {}))
            return self._con

    fm.MySQL = MySQL

    return {"pymysql": pm, "pymysql.err": pm.err, "pymysql.cursors": pm.cursors, "MySQLdb": mysqldb, "MySQLdb.cursors": mysqldb.cursors,
            "MySQLdb._mysql": mysqldb._mysql, "mysql": my, "mysql.connector": mc, "mysql.connector.errors": mc.errors, "mysql.connector.pooling": mc.pooling,
            "psycopg2": pg, "psycopg2.extras": pg.extras, "psycopg2.errors": pg.errors, "psycopg2.sql": pg.sql, "flask_mysqldb": fm}


# ------------------------------------------------------------------------------------- SQLAlchemy --
def _parchar_sqlalchemy():
    try:
        import sqlalchemy
        from sqlalchemy.engine import create as _crear
        from sqlalchemy.engine.url import make_url
    except Exception:  # noqa: BLE001 - la app no usa SQLAlchemy
        return
    if getattr(_crear.create_engine, "_cc", False):
        return
    original = _crear.create_engine
    QUITAR = {"pool_size", "max_overflow", "pool_timeout", "pool_recycle", "pool_use_lifo", "isolation_level", "server_side_cursors"}

    def create_engine(url, *a, **kw):
        try:
            u = make_url(url)
            motor = u.get_backend_name()
        except Exception:  # noqa: BLE001
            return original(url, *a, **kw)
        if motor not in _CC_MOTORES:
            return original(url, *a, **kw)
        base = u.database or "base"
        nombre = {"postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mssql": "SQL Server", "oracle": "Oracle"}.get(motor, "MySQL")
        estilo = "postgres" if nombre == "PostgreSQL" else "mysql"
        if _CC_PUENTE and nombre == "MySQL":
            clave = ("MySQL", u.host or "localhost", base)
            if clave not in _CC_SIN_SERVIDOR:
                try:
                    import _cc_mysql_base as _b
                    prueba = _b.Connection(host=u.host or "localhost", user=u.username or "root", password=u.password or "", database=u.database, port=u.port or 3306)
                    prueba.close()
                    real = u.set(drivername="mysql+pymysql")   # el pymysql de CódigoCamp habla con tu MySQL real
                    _cc_aviso(f"real:{clave}", f"conectado a tu MySQL real ({u.host or 'localhost'}/{base}) a través de CódigoCamp.")
                    kw.pop("connect_args", None)
                    return original(real, *a, **kw)
                except Exception as e:  # noqa: BLE001
                    if not _es_de_conexion(e):
                        raise
                    _CC_SIN_SERVIDOR[clave] = _motivo(e)
            _cc_aviso(f"respaldo:{clave}", f"no pude usar tu MySQL en {u.host or 'localhost'} ({_CC_SIN_SERVIDOR[clave]}). "
                      f"Para que tu app funcione igual, uso SQLite en .codigocamp/bd/{_cc_nombre(base)}.db.")
        ruta = ruta_sqlite(base)
        if not os.path.exists(ruta):
            abrir_sqlite(base, estilo, nombre, f"{u.host or 'localhost'}{':' + str(u.port) if u.port else ''}/{base}").close()
        kw = {k: v for k, v in kw.items() if k not in QUITAR}
        kw.pop("connect_args", None)
        return original(f"sqlite:///{ruta}", *a, **kw)

    create_engine._cc = True
    _crear.create_engine = create_engine
    sqlalchemy.create_engine = create_engine
    import sqlalchemy.engine as _eng
    _eng.create_engine = create_engine
    # Tipos propios de MySQL/PostgreSQL que el compilador de SQLite no conoce.
    try:
        from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
        equivalentes = {"LONGTEXT": "TEXT", "MEDIUMTEXT": "TEXT", "TINYTEXT": "TEXT", "TINYINT": "INTEGER", "MEDIUMINT": "INTEGER", "YEAR": "INTEGER",
                        "BIT": "INTEGER", "SET": "TEXT", "LONGBLOB": "BLOB", "MEDIUMBLOB": "BLOB", "TINYBLOB": "BLOB", "UUID": "CHAR(36)", "INET": "TEXT",
                        "CIDR": "TEXT", "MONEY": "NUMERIC", "BYTEA": "BLOB", "JSONB": "JSON", "ARRAY": "JSON", "INTERVAL": "TEXT", "TSVECTOR": "TEXT", "CITEXT": "TEXT", "DOUBLE_PRECISION": "REAL"}
        for nombre, tipo in equivalentes.items():
            if not hasattr(SQLiteTypeCompiler, f"visit_{nombre}"):
                setattr(SQLiteTypeCompiler, f"visit_{nombre}", lambda self, type_, _t=tipo, **kw: _t)
    except Exception:  # noqa: BLE001
        pass


# ---------------------------------------------------------------------------------------- MongoDB --
def _mongo_disponible():
    try:
        import mongomock  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return False


_CC_MONGO = []


def _crear_pymongo():
    import mongomock
    from mongomock import ObjectId

    class MongoClient(mongomock.MongoClient):
        def __init__(self, host=None, *a, **kw):
            super().__init__()
            self._cc_desde = str(host or "mongodb://localhost:27017")
            _cc_aviso("mongo", "tu app usa MongoDB. En el navegador no hay conexión a servidores, así que uso una base en memoria compatible "
                      "(mongomock) que se guarda en .codigocamp/bd/mongo-<base>.json. En tu PC seguirá usando MongoDB o Atlas.")
            _CC_MONGO.append(self)
            self._cc_cargar()

        def _cc_cargar(self):
            carpeta = _cc_carpeta()
            for archivo in os.listdir(carpeta):
                if archivo.startswith("mongo-") and archivo.endswith(".json"):
                    base = archivo[6:-5]
                    try:
                        with open(os.path.join(carpeta, archivo), encoding="utf-8") as f:
                            datos = json.load(f, object_hook=_desde_json)
                    except Exception:  # noqa: BLE001
                        continue
                    for col, docs in datos.items():
                        if docs and self[base][col].estimated_document_count() == 0:
                            self[base][col].insert_many(docs)

        def get_default_database(self, default=None, **k):
            m = re.search(r"/(\w+)(?:\?|$)", self._cc_desde.split("@")[-1])
            return self[(m.group(1) if m else None) or default or "test"]

    pym = types.ModuleType("pymongo")
    pym.MongoClient = MongoClient
    pym.ASCENDING, pym.DESCENDING, pym.TEXT = 1, -1, "text"
    pym.ReturnDocument = mongomock.ReturnDocument if hasattr(mongomock, "ReturnDocument") else types.SimpleNamespace(BEFORE=False, AFTER=True)
    pym.errors = types.ModuleType("pymongo.errors")
    for nombre in ("DuplicateKeyError", "OperationFailure", "PyMongoError", "ConnectionFailure", "ServerSelectionTimeoutError", "InvalidOperation", "BulkWriteError"):
        setattr(pym.errors, nombre, getattr(mongomock, nombre, Exception))
    pym.collection = types.ModuleType("pymongo.collection"); pym.collection.Collection = mongomock.Collection
    pym.database = types.ModuleType("pymongo.database"); pym.database.Database = mongomock.Database
    pym.server_api = types.ModuleType("pymongo.server_api"); pym.server_api.ServerApi = lambda *a, **k: None
    pym.results = types.ModuleType("pymongo.results")
    bson = types.ModuleType("bson"); bson.ObjectId = ObjectId
    bson.objectid = types.ModuleType("bson.objectid"); bson.objectid.ObjectId = ObjectId
    bson.errors = types.ModuleType("bson.errors"); bson.errors.InvalidId = getattr(mongomock, "InvalidId", ValueError)
    bson.json_util = types.ModuleType("bson.json_util")
    bson.json_util.dumps = lambda o, **k: json.dumps(o, default=_a_json, **k)
    bson.json_util.loads = lambda s, **k: json.loads(s, object_hook=_desde_json)
    return {"pymongo": pym, "pymongo.errors": pym.errors, "pymongo.collection": pym.collection, "pymongo.database": pym.database,
            "pymongo.server_api": pym.server_api, "pymongo.results": pym.results, "bson": bson, "bson.objectid": bson.objectid,
            "bson.errors": bson.errors, "bson.json_util": bson.json_util}


def _a_json(o):
    import datetime
    if type(o).__name__ == "ObjectId":
        return {"$oid": str(o)}
    if isinstance(o, (datetime.datetime, datetime.date)):
        return {"$date": o.isoformat()}
    return str(o)


def _desde_json(d):
    if set(d) == {"$oid"}:
        from mongomock import ObjectId
        return ObjectId(d["$oid"])
    if set(d) == {"$date"}:
        import datetime
        return datetime.datetime.fromisoformat(d["$date"])
    return d


def guardar_mongo():
    """Escribe lo que hay en las bases de MongoDB emuladas (se llama tras cada cambio y al detener el servidor)."""
    for cliente in _CC_MONGO:
        try:
            for base in cliente.list_database_names():
                datos = {col: list(cliente[base][col].find({})) for col in cliente[base].list_collection_names()}
                with open(os.path.join(_cc_carpeta(), f"mongo-{_cc_nombre(base)}.json"), "w", encoding="utf-8") as f:
                    json.dump(datos, f, default=_a_json, ensure_ascii=False)
        except Exception:  # noqa: BLE001
            pass


# ------------------------------------------------------------------------------------------ activar --
_CC_PUENTE = False
_CC_SIN_SERVIDOR = {}   # (motor, host, base) -> motivo: ya se sabe que no conecta, se va directo a SQLite


def _es_de_conexion(e):
    """¿El error es por no poder llegar al servidor (y no por tu SQL)?"""
    codigo = getattr(e, "errno", None)
    if codigo is None and getattr(e, "args", None) and isinstance(e.args[0], int):
        codigo = e.args[0]
    if codigo in (1044, 1045, 1049, 2002, 2003, 2005, 2006, 2013, 2059):
        return True
    return bool(re.search(r"No se pudo hablar|no permite conectar|No se permite conectar|Inicia sesión|Can't connect|Unknown database|Access denied|timed out|refused", str(e), re.I))


def _motivo(e):
    t = str(e)
    if re.search(r"Unknown database|1049", t):
        return "esa base no existe en tu servidor (créala en phpMyAdmin o importa tu .sql)"
    if re.search(r"Access denied|1045", t):
        return "usuario o contraseña incorrectos para tu servidor"
    if re.search(r"no permite conectar|No se permite conectar", t):
        return "este CódigoCamp no puede conectar a ese servidor (usa el puente: bd-puente)"
    return "el servidor no responde (¿XAMPP/MySQL está encendido?)"


def _con_respaldo(real, motor, estilo, base_de, host_de):
    """connect() que intenta tu servidor real (por el puente de CódigoCamp) y, si no se puede llegar, usa SQLite."""
    def connect(*a, **kw):
        base, host = base_de(a, kw), host_de(a, kw)
        clave = (motor, host, base)
        if clave not in _CC_SIN_SERVIDOR:
            try:
                return real(*a, **kw)
            except Exception as e:  # noqa: BLE001
                if not _es_de_conexion(e):
                    raise
                _CC_SIN_SERVIDOR[clave] = _motivo(e)
        _cc_aviso(f"respaldo:{clave}", f"no pude usar tu {motor} en {host} ({_CC_SIN_SERVIDOR[clave]}). "
                  f"Para que tu app funcione igual, uso SQLite en .codigocamp/bd/{_cc_nombre(base)}.db.")
        dicc = kw.get("cursorclass") is not None and "dict" in getattr(kw.get("cursorclass"), "__name__", "").lower()
        c = Conexion(base, estilo, motor, f"{host}/{base}", dict_por_defecto=dicc or bool(kw.get("cursor_factory")), autocommit=kw.get("autocommit", False))
        return c
    connect._cc = True
    return connect


def _usar_errores_del_puente():
    """La copia SQLite lanza las mismas clases de error que el pymysql del puente (para que tus except funcionen)."""
    try:
        import _cc_mysql_base as b
    except Exception:  # noqa: BLE001
        return
    g = globals()
    for nombre in ("Error", "InterfaceError", "DatabaseError", "OperationalError", "IntegrityError", "ProgrammingError", "DataError", "NotSupportedError", "InternalError"):
        if hasattr(b, nombre):
            g[nombre] = getattr(b, nombre)


def _activar_puente():
    _usar_errores_del_puente()
    base_kw = lambda a, kw: kw.get("database") or kw.get("db") or kw.get("dbname") or (a[3] if len(a) > 3 else None) or "base"   # noqa: E731
    host_kw = lambda a, kw: kw.get("host") or (a[0] if a else None) or "localhost"   # noqa: E731
    for nombre, motor in (("pymysql", "MySQL"), ("MySQLdb", "MySQL"), ("mysql.connector", "MySQL")):
        try:
            m = __import__(nombre, fromlist=["connect"])
        except Exception:  # noqa: BLE001
            continue
        if not getattr(m.connect, "_cc", False):
            m.connect = m.Connect = _con_respaldo(m.connect, motor, "mysql", base_kw, host_kw)
    try:
        import psycopg2 as pg
        if not getattr(pg.connect, "_cc", False):
            pg.connect = _con_respaldo(pg.connect, "PostgreSQL", "postgres", lambda a, kw: _base_de(kw, a[0] if a else kw.get("dsn")), host_kw)
    except Exception:  # noqa: BLE001
        pass
    # MongoDB: el del puente; si no conecta (p. ej. Atlas no está permitido), mongomock con los datos en el proyecto.
    try:
        import pymongo as pm
        if not getattr(pm.MongoClient, "_cc", False) and _mongo_disponible():
            Real = pm.MongoClient
            Respaldo = _crear_pymongo()["pymongo"].MongoClient

            def MongoClient(host=None, *a, **kw):
                try:
                    return Real(host, *a, **kw)
                except Exception as e:  # noqa: BLE001
                    _cc_aviso("mongo-respaldo", f"no pude conectar a MongoDB ({str(e)[:120]}).")
                    return Respaldo(host, *a, **kw)

            MongoClient._cc = True
            pm.MongoClient = MongoClient
    except Exception:  # noqa: BLE001
        pass


def preparar(raiz="/workspace", puente=False):
    """Se llama antes de importar tu app (y antes de cada `python archivo.py`).
    puente=True: los conectores de CódigoCamp (pymysql, mysql.connector, psycopg2, pymongo) ya están cargados y van a tu
    servidor real; si no se puede llegar a él, cada conexión pasa sola a SQLite. puente=False: SQLite directamente."""
    global _CC_RAIZ, _CC_PUENTE
    _CC_RAIZ = os.path.abspath(raiz)
    _CC_PUENTE = bool(puente)
    modulos = _crear_modulos()
    if _CC_PUENTE:
        sys.modules["flask_mysqldb"] = modulos["flask_mysqldb"]
        _activar_puente()
    else:
        for nombre, modulo in modulos.items():
            sys.modules[nombre] = modulo
        if _mongo_disponible():
            for nombre, modulo in _crear_pymongo().items():
                sys.modules[nombre] = modulo
    _parchar_sqlalchemy()
    _parchar_django()
    # Si SQLAlchemy o Django se importan después (los importa tu app), se parchan en ese momento.
    import importlib.abc
    import importlib.machinery

    class _Gancho(importlib.abc.MetaPathFinder):
        def find_spec(self, nombre, ruta=None, objetivo=None):
            parche = _GANCHOS.get(nombre)
            if parche is None or nombre in sys.modules:
                return None
            spec = importlib.machinery.PathFinder.find_spec(nombre, ruta)
            if spec and spec.loader and not getattr(spec.loader, "_cc", False):
                cargar = spec.loader.exec_module

                def exec_module(modulo, _cargar=cargar, _parche=parche):
                    _cargar(modulo)
                    _parche()

                spec.loader.exec_module = exec_module
            return spec

    sys.meta_path[:] = [g for g in sys.meta_path if type(g).__name__ != "_Gancho"]
    sys.meta_path.insert(0, _Gancho())


# ---------------------------------------------------------------------------------------- Django --
def _parchar_django():
    """settings.py con ENGINE mysql/postgresql: en el navegador se usa sqlite3 (con aviso); en tu PC no cambia nada."""
    try:
        import django.conf as dc
    except Exception:  # noqa: BLE001
        return
    if getattr(dc.LazySettings._setup, "_cc", False):
        return
    original = dc.LazySettings._setup

    def _setup(self, name=None):
        original(self, name)
        for alias, cfg in (getattr(self._wrapped, "DATABASES", None) or {}).items():
            motor = str(cfg.get("ENGINE", ""))
            if any(x in motor for x in ("mysql", "postgresql", "oracle", "mssql")):
                nombre = cfg.get("NAME") or alias
                cfg.clear()
                cfg.update({"ENGINE": "django.db.backends.sqlite3", "NAME": ruta_sqlite(nombre)})
                _cc_aviso("django:" + alias, f"settings.py usa {motor.rsplit('.', 1)[-1]} para «{alias}». En el navegador uso SQLite en "
                          f".codigocamp/bd/{_cc_nombre(nombre)}.db (corre «python manage.py migrate» para crear las tablas). En tu PC no cambia nada.")
            elif "sqlite3" in motor and cfg.get("NAME") and not os.path.isabs(str(cfg["NAME"])):
                cfg["NAME"] = os.path.join(_CC_RAIZ, str(cfg["NAME"]))

    _setup._cc = True
    dc.LazySettings._setup = _setup


_GANCHOS = {"sqlalchemy": _parchar_sqlalchemy, "django": _parchar_django}
