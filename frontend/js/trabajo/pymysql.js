// pymysql, mysql.connector y MySQLdb para el Python del navegador (Pyodide).
// Python no puede abrir sockets en el navegador: estos módulos tienen la misma API que los reales y mandan cada
// consulta por ClienteBD.pedirSync (al servidor de CódigoCamp o al puente de tu PC). Así funciona el código de
// siempre:  conexion = pymysql.connect(host="localhost", user="root", password="", database="finanbot_db")

export const BASE_PY = String.raw`
"""Núcleo compartido por pymysql, mysql.connector y MySQLdb en CódigoCamp."""
import datetime as _dt
import decimal as _dec
import json as _json

import _cc_bd

apilevel = "2.0"
threadsafety = 1
paramstyle = "pyformat"


class Warning(Exception):
    pass


class Error(Exception):
    def __init__(self, *args, errno=None, msg=None):
        if errno is None and len(args) >= 2 and isinstance(args[0], int):
            errno, msg = args[0], args[1]
        self.errno = errno
        self.msg = msg if msg is not None else (args[0] if args else "")
        super().__init__(*((errno, self.msg) if errno is not None else (self.msg,)))

    def __str__(self):
        return f"{self.errno}: {self.msg}" if self.errno is not None else str(self.msg)


class InterfaceError(Error): pass
class DatabaseError(Error): pass
class DataError(DatabaseError): pass
class OperationalError(DatabaseError): pass
class IntegrityError(DatabaseError): pass
class InternalError(DatabaseError): pass
class ProgrammingError(DatabaseError): pass
class NotSupportedError(DatabaseError): pass


_INTEGRIDAD = {1062, 1451, 1452, 1048, 1216, 1217, 1364, 3819}
_PROGRAMACION = {1064, 1146, 1054, 1149, 1110, 1113, 1007, 1008, 1050, 1051, 1060, 1061, 1091, 1305}
_DATOS = {1264, 1265, 1366, 1406, 1292}


def _error(datos):
    codigo, texto = datos.get("codigo"), datos.get("error") or "Error de MySQL"
    if isinstance(texto, str) and codigo is not None and texto.startswith(f"ERROR {codigo}: "):
        texto = texto[len(f"ERROR {codigo}: "):]
    clase = IntegrityError if codigo in _INTEGRIDAD else ProgrammingError if codigo in _PROGRAMACION else DataError if codigo in _DATOS else OperationalError
    return clase(codigo, texto) if codigo is not None else clase(texto)


def _pedir(accion, datos, crear=None):
    r = _json.loads(_cc_bd.pedir(accion, _json.dumps(datos)))
    if "__error" in r:
        raise (crear or _error)({"error": r["__error"], "codigo": r.get("codigo")})
    return r


# ---- escapar valores (como pymysql.converters) ----
_ESCAPES = {0: "\\0", 10: "\\n", 13: "\\r", 26: "\\Z", 34: '\\"', 39: "\\'", 92: "\\\\"}


def escape_string(valor):
    return str(valor).translate(_ESCAPES)


def literal(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float, _dec.Decimal)):
        return repr(v) if isinstance(v, float) else str(v)
    if isinstance(v, (bytes, bytearray, memoryview)):
        return "X'" + bytes(v).hex() + "'" if len(v) else "''"
    if isinstance(v, _dt.datetime):
        return "'" + v.isoformat(sep=" ") + "'"
    if isinstance(v, (_dt.date, _dt.time)):
        return "'" + v.isoformat() + "'"
    if isinstance(v, _dt.timedelta):
        s = int(v.total_seconds())
        return f"'{'-' if s < 0 else ''}{abs(s) // 3600:02d}:{abs(s) % 3600 // 60:02d}:{abs(s) % 60:02d}'"
    if isinstance(v, (list, tuple, set, frozenset)):
        return "(" + ",".join(literal(x) for x in v) + ")"
    return "'" + escape_string(v) + "'"


def mogrify(sql, args=None):
    if args is None:
        return sql
    if isinstance(args, dict):
        return sql % {k: literal(v) for k, v in args.items()}
    if not isinstance(args, (list, tuple)):
        args = (args,)
    return sql % tuple(literal(a) for a in args)


# ---- convertir lo que llega (como lo hace pymysql) ----
def _convertir(valor, tipo):
    if valor is None:
        return None
    if isinstance(valor, dict) and "$bytes" in valor:
        return bytes.fromhex(valor["$bytes"])
    if isinstance(valor, dict) and "$json" in valor:
        return _json.loads(valor["$json"])
    try:
        if tipo in (0, 246):
            return _dec.Decimal(valor)
        if tipo in (7, 12):
            return _dt.datetime.fromisoformat(valor) if not str(valor).startswith("0000") else None
        if tipo == 10:
            return _dt.date.fromisoformat(valor) if not str(valor).startswith("0000") else None
        if tipo == 11:
            signo = -1 if str(valor).startswith("-") else 1
            h, m, s = str(valor).lstrip("-").split(":")
            return signo * _dt.timedelta(hours=int(h), minutes=int(m), seconds=float(s))
    except (ValueError, ArithmeticError):
        return valor
    return valor


_abiertas = []


def _cerrar_todas():
    for c in list(_abiertas):
        try:
            c.close()
        except Exception:
            pass


class Cursor:
    _como_dict = False

    def __init__(self, conexion):
        self.connection = conexion
        self.description = None
        self.rowcount = -1
        self.lastrowid = None
        self.arraysize = 1
        self.rownumber = 0
        self._filas = []
        self._cerrado = False

    # DB-API
    def execute(self, query, args=None):
        if self._cerrado:
            raise ProgrammingError("Cursor closed")
        sql = self.connection._mogrify(query, args)
        r = self.connection._consulta(sql)
        self._resultado(r)
        return self.rowcount

    def executemany(self, query, seq_args):
        total = 0
        for args in seq_args:
            total += self.execute(query, args) or 0
        self.rowcount = total
        return total

    def mogrify(self, query, args=None):
        return self.connection._mogrify(query, args)

    def _resultado(self, r):
        self.lastrowid = r.get("ultimo_id") or (0 if r.get("columnas") is None else None)
        if r.get("columnas") is None:
            self.description = None
            self._filas = []
            self.rowcount = r.get("afectadas", 0)
        else:
            tipos = r.get("tipos") or [253] * len(r["columnas"])
            self.description = tuple((c, t, None, None, None, None, True) for c, t in zip(r["columnas"], tipos))
            conv = self.connection._convertir
            filas = [tuple(conv(v, t) for v, t in zip(f, tipos)) for f in r["filas"]]
            self._filas = [dict(zip(r["columnas"], f)) for f in filas] if self._como_dict else filas
            self.rowcount = len(self._filas)
        self.rownumber = 0

    def fetchone(self):
        if self.rownumber >= len(self._filas):
            return None
        fila = self._filas[self.rownumber]
        self.rownumber += 1
        return fila

    def fetchmany(self, size=None):
        n = size or self.arraysize
        filas = self._filas[self.rownumber:self.rownumber + n]
        self.rownumber += len(filas)
        return filas

    def fetchall(self):
        filas = self._filas[self.rownumber:]
        self.rownumber = len(self._filas)
        return filas if self._como_dict else tuple(filas)  # como pymysql: tupla de tuplas

    def scroll(self, value, mode="relative"):
        self.rownumber = value if mode == "absolute" else self.rownumber + value

    def callproc(self, nombre, args=()):
        self.execute(f"CALL {nombre}({','.join(literal(a) for a in args)})")
        return args

    def nextset(self):
        return None

    def setinputsizes(self, *a):
        pass

    def setoutputsizes(self, *a):
        pass

    def close(self):
        self._cerrado = True

    def __iter__(self):
        return iter(self.fetchone, None)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class DictCursor(Cursor):
    _como_dict = True


SSCursor = Cursor
SSDictCursor = DictCursor


class Connection:
    _motor = "mysql"
    _mogrify = staticmethod(mogrify)
    _convertir = staticmethod(_convertir)
    _crear_error = staticmethod(_error)

    def __init__(self, host="localhost", user=None, password="", database=None, port=3306, unix_socket=None, charset="utf8mb4",
                 cursorclass=Cursor, autocommit=False, connect_timeout=10, db=None, passwd=None, **otros):
        self.host = host or "localhost"
        self.port = int(port or 3306)
        self.user = user or "root"
        self.db = database or db
        self.charset = charset
        self.cursorclass = cursorclass
        self._autocommit = bool(autocommit)
        clave = password if password not in (None, "") else (passwd or "")
        r = _pedir("conectar", {"motor": self._motor, "host": self.host, "puerto": self.port, "usuario": self.user, "clave": clave, "base": self.db, "autocommit": self._autocommit}, self._crear_error)
        self._sesion = r["sesion"]
        self.server_version = r.get("version", "")
        self.open = True
        _abiertas.append(self)

    def _consulta(self, sql):
        if not self.open:
            raise InterfaceError(0, "La conexión está cerrada")
        r = _pedir("consulta", {"sesion": self._sesion, "sql": sql}, self._crear_error)
        if r.get("base") is not None:
            self.db = r["base"]
        return r

    def cursor(self, cursor=None, **opciones):
        clase = cursor or self.cursorclass
        return clase(self)

    def commit(self):
        self._consulta("COMMIT")

    def rollback(self):
        self._consulta("ROLLBACK")

    def begin(self):
        self._consulta("BEGIN")

    def autocommit(self, valor):
        self._autocommit = bool(valor)
        self._consulta(f"SET autocommit={1 if valor else 0}")

    def get_autocommit(self):
        return self._autocommit

    def select_db(self, base):
        self._consulta("USE " + chr(96) + str(base).replace(chr(96), chr(96) * 2) + chr(96))

    def ping(self, reconnect=True):
        self._consulta("SELECT 1")
        return True

    def insert_id(self):
        r = self._consulta("SELECT LAST_INSERT_ID()")
        return r["filas"][0][0]

    # ---- lo que usan SQLAlchemy, Flask-SQLAlchemy y SQLModel (dialectos mysql+pymysql / mysql+mysqldb) ----
    def character_set_name(self):
        return (self.charset or "utf8mb4").lower()

    def set_character_set(self, charset, collation=None):
        self.charset = charset

    def get_server_info(self):
        return self.server_version or "8.0.0"

    def get_host_info(self):
        return f"{self.host} via TCP/IP"

    def get_proto_info(self):
        return 10

    def thread_id(self):
        return abs(hash(self._sesion)) % 100000

    def show_warnings(self):
        return ()

    @property
    def encoding(self):
        return "utf8"

    @property
    def server_status(self):
        return 2 if self._autocommit else 0

    def escape(self, v):
        return literal(v)

    def escape_string(self, v):
        return escape_string(v)

    def close(self):
        if self.open:
            self.open = False
            try:
                _pedir("cerrar", {"sesion": self._sesion})
            except Error:
                pass
            if self in _abiertas:
                _abiertas.remove(self)

    def __enter__(self):
        return self

    def __exit__(self, tipo, *a):
        self.close()

    def __del__(self):
        pass
`;

const PYMYSQL = String.raw`
"""pymysql de CódigoCamp: misma API que PyMySQL; las consultas van a tu MySQL (servidor de CódigoCamp o puente)."""
from _cc_mysql_base import *  # noqa: F401,F403
from _cc_mysql_base import Connection, Cursor, DictCursor, SSCursor, SSDictCursor, Error, escape_string, literal
from _cc_mysql_base import InterfaceError, DatabaseError, DataError, OperationalError, IntegrityError, InternalError, ProgrammingError, NotSupportedError, Warning
from . import constants, cursors, err, converters  # noqa: E402
paramstyle, apilevel, threadsafety = "pyformat", "2.0", 1

__version__ = "1.1.1"
VERSION = (1, 1, 1, "final", 0)
version_info = (1, 4, 6, "final", 0)
MySQLError = Error


def connect(*args, **kwargs):
    return Connection(*args, **kwargs)


Connect = connect


def install_as_MySQLdb():
    import sys
    sys.modules["MySQLdb"] = sys.modules[__name__]
`;

const PYMYSQL_CURSORS = "from _cc_mysql_base import Cursor, DictCursor, SSCursor, SSDictCursor  # noqa: F401\n";
const PYMYSQL_ERR = "from _cc_mysql_base import Error, Warning, InterfaceError, DatabaseError, DataError, OperationalError, IntegrityError, InternalError, ProgrammingError, NotSupportedError  # noqa: F401\nMySQLError = Error\n";
const PYMYSQL_CONSTANTS = "from . import CLIENT, ER, FIELD_TYPE  # noqa: F401\n";
const PYMYSQL_CLIENT = "LONG_PASSWORD = 1\nFOUND_ROWS = 2\nLONG_FLAG = 4\nCONNECT_WITH_DB = 8\nLOCAL_FILES = 128\nPROTOCOL_41 = 512\nTRANSACTIONS = 8192\nSECURE_CONNECTION = 32768\nMULTI_STATEMENTS = 65536\nMULTI_RESULTS = 131072\nPS_MULTI_RESULTS = 262144\nPLUGIN_AUTH = 524288\n";
const PYMYSQL_ER = "DUP_ENTRY = 1062\nNO_SUCH_TABLE = 1146\nPARSE_ERROR = 1064\nBAD_FIELD_ERROR = 1054\nACCESS_DENIED_ERROR = 1045\nBAD_DB_ERROR = 1049\n";
const PYMYSQL_FIELD = "DECIMAL = 0\nTINY = 1\nSHORT = 2\nLONG = 3\nFLOAT = 4\nDOUBLE = 5\nNULL = 6\nTIMESTAMP = 7\nLONGLONG = 8\nINT24 = 9\nDATE = 10\nTIME = 11\nDATETIME = 12\nYEAR = 13\nVARCHAR = 15\nBIT = 16\nJSON = 245\nNEWDECIMAL = 246\nENUM = 247\nSET = 248\nBLOB = 252\nVAR_STRING = 253\nSTRING = 254\n";
const PYMYSQL_CONV = "from _cc_mysql_base import escape_string, literal as escape_item  # noqa: F401\n";

const CONECTOR = String.raw`
"""mysql.connector de CódigoCamp: misma API que mysql-connector-python; las consultas van a tu MySQL."""
import _cc_mysql_base as _b
from _cc_mysql_base import Error, Warning, InterfaceError, DatabaseError, DataError, OperationalError, IntegrityError, InternalError, ProgrammingError, NotSupportedError  # noqa: F401
from . import errors, errorcode  # noqa: F401,E402

__version__ = "8.0.33"
apilevel, threadsafety, paramstyle = "2.0", 1, "pyformat"


class MySQLCursor(_b.Cursor):
    @property
    def column_names(self):
        return tuple(d[0] for d in self.description) if self.description else ()

    @property
    def with_rows(self):
        return self.description is not None

    @property
    def statement(self):
        return getattr(self, "_ultimo", None)

    def execute(self, operation, params=None, multi=False):
        self._ultimo = _b.mogrify(operation, params)
        if multi:
            from _cc_mysql_base import _pedir  # noqa: F401
            raise NotSupportedError("multi=True no está disponible; ejecuta cada sentencia por separado.")
        super().execute(operation, params)
        return None

    def fetchall(self):
        if self.description is None:
            raise InterfaceError(-1, "No result set to fetch from.")
        return list(super().fetchall())


class MySQLCursorDict(MySQLCursor):
    _como_dict = True


class MySQLCursorNamedTuple(MySQLCursor):
    def _resultado(self, r):
        super()._resultado(r)
        if self.description:
            from collections import namedtuple
            Fila = namedtuple("Row", [d[0] for d in self.description], rename=True)
            self._filas = [Fila(*f) for f in self._filas]


class MySQLConnection(_b.Connection):
    def __init__(self, **kw):
        kw.setdefault("host", "127.0.0.1")
        kw.pop("auth_plugin", None)
        kw.pop("use_pure", None)
        kw.pop("raise_on_warnings", None)
        kw.pop("buffered", None)
        kw.pop("pool_name", None)
        kw.pop("pool_size", None)
        if "passwd" in kw and "password" not in kw:
            kw["password"] = kw.pop("passwd")
        super().__init__(**kw)
        self.database = self.db

    def cursor(self, buffered=None, raw=None, prepared=None, cursor_class=None, dictionary=None, named_tuple=None):
        if cursor_class:
            return cursor_class(self)
        if dictionary:
            return MySQLCursorDict(self)
        if named_tuple:
            return MySQLCursorNamedTuple(self)
        return MySQLCursor(self)

    def is_connected(self):
        return self.open

    def reconnect(self, attempts=1, delay=0):
        return None

    def start_transaction(self, **kw):
        self.begin()

    @property
    def autocommit(self):
        return self._autocommit

    @autocommit.setter
    def autocommit(self, valor):
        _b.Connection.autocommit(self, valor)

    def get_server_info(self):
        return self.server_version

    def cmd_query(self, sql):
        return self._consulta(sql)

    def disconnect(self):
        self.close()


def connect(*args, **kwargs):
    if args:
        raise TypeError("Usa argumentos con nombre: mysql.connector.connect(host=..., user=..., password=..., database=...)")
    return MySQLConnection(**kwargs)


Connect = connect
`;

const CONECTOR_ERRORS = "from _cc_mysql_base import Error, Warning, InterfaceError, DatabaseError, DataError, OperationalError, IntegrityError, InternalError, ProgrammingError, NotSupportedError  # noqa: F401\n";
const CONECTOR_CODIGOS = "ER_ACCESS_DENIED_ERROR = 1045\nER_BAD_DB_ERROR = 1049\nER_NO_SUCH_TABLE = 1146\nER_DUP_ENTRY = 1062\nER_PARSE_ERROR = 1064\nER_BAD_FIELD_ERROR = 1054\nCR_CONN_HOST_ERROR = 2003\n";

/** Archivos Python (ruta relativa → código) de los módulos. */
export const MODULOS_MYSQL = {
  "_cc_mysql_base.py": BASE_PY,
  "pymysql/__init__.py": PYMYSQL,
  "pymysql/cursors.py": PYMYSQL_CURSORS,
  "pymysql/err.py": PYMYSQL_ERR,
  "pymysql/converters.py": PYMYSQL_CONV,
  "pymysql/constants/__init__.py": PYMYSQL_CONSTANTS,
  "pymysql/constants/CLIENT.py": PYMYSQL_CLIENT,
  "pymysql/constants/ER.py": PYMYSQL_ER,
  "pymysql/constants/FIELD_TYPE.py": PYMYSQL_FIELD,
  "mysql/__init__.py": "",
  "mysql/connector/__init__.py": CONECTOR,
  "mysql/connector/errors.py": CONECTOR_ERRORS,
  "mysql/connector/errorcode.py": CONECTOR_CODIGOS,
  "MySQLdb/__init__.py": "from pymysql import *  # noqa\nfrom pymysql import connect, Connect, Error, cursors  # noqa\nconnect = connect\n",
  "MySQLdb/cursors.py": "from _cc_mysql_base import Cursor, DictCursor, SSCursor, SSDictCursor  # noqa\n",
};

import { MODULOS_BD } from "./pybd.js";

export const DIR_MYSQL = "/home/pyodide/.cc_mysql";

/** Instala los módulos en el Python del navegador y los conecta con `cliente` (ClienteBD). */
export function instalarMysqlEnPython(pyo, cliente) {
  const sis = pyo.FS;
  const asegurar = (dir) => { let acc = ""; for (const p of dir.split("/").filter(Boolean)) { acc += "/" + p; try { sis.mkdir(acc); } catch { /* ya existe */ } } };
  for (const [ruta, codigo] of Object.entries({ ...MODULOS_MYSQL, ...MODULOS_BD })) {
    const completa = `${DIR_MYSQL}/${ruta}`;
    asegurar(completa.slice(0, completa.lastIndexOf("/")));
    sis.writeFile(completa, codigo);
  }
  pyo.registerJsModule("_cc_bd", {
    pedir: (accion, datos) => {
      try { return JSON.stringify(cliente.pedirSync(accion, JSON.parse(datos))); }
      catch (e) { return JSON.stringify({ __error: e.message, codigo: e.codigo ?? (e.estado === 410 ? 2013 : 2003) }); }
    },
  });
  pyo.runPython(`import sys\nif ${JSON.stringify(DIR_MYSQL)} in sys.path: sys.path.remove(${JSON.stringify(DIR_MYSQL)})\nsys.path.insert(0, ${JSON.stringify(DIR_MYSQL)})\nfor _m in [m for m in sys.modules if m.split('.')[0] in ('pymysql', 'mysql', 'MySQLdb', '_cc_mysql_base', 'psycopg2', 'psycopg', 'pymongo', 'bson', 'redis')]: del sys.modules[_m]`);
}

/** Cierra las conexiones que el programa dejó abiertas. */
export function cerrarMysqlEnPython(pyo) {
  try { pyo.runPython("import sys\nfor _n in ('_cc_mysql_base', 'pymongo', 'redis'):\n    _m = sys.modules.get(_n)\n    if _m and hasattr(_m, '_cerrar_todas'): _m._cerrar_todas()"); } catch { /* nada */ }
}

