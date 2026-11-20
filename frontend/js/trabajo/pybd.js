// psycopg2 / psycopg (PostgreSQL), pymongo + bson (MongoDB) y redis para el Python del navegador.
// Igual que pymysql.js: misma API que las librerías reales; cada operación viaja por ClienteBD.pedirSync.

const PSYCOPG2 = String.raw`
"""psycopg2 de CódigoCamp: misma API que el real; las consultas van a tu PostgreSQL (servidor de CódigoCamp o puente)."""
import collections as _col
import datetime as _dt
import decimal as _dec
import json as _json
import re as _re

import _cc_mysql_base as _b
from . import errors  # noqa: E402
from .errors import (Error, Warning, InterfaceError, DatabaseError, DataError, OperationalError, IntegrityError,  # noqa: F401
                     InternalError, ProgrammingError, NotSupportedError)

__version__ = "2.9.9 (CódigoCamp)"
apilevel, threadsafety, paramstyle = "2.0", 2, "pyformat"
Column = _col.namedtuple("Column", "name type_code display_size internal_size precision scale null_ok")


def _texto(v):
    return "'" + str(v).replace("'", "''") + "'"


def literal(v):
    if hasattr(v, "getquoted"):
        q = v.getquoted()
        return q.decode() if isinstance(q, bytes) else q
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return f"'{v}'::float" if v != v or v in (float("inf"), float("-inf")) else repr(v)
    if isinstance(v, _dec.Decimal):
        return f"'{v}'::numeric" if not v.is_finite() else str(v)
    if isinstance(v, (bytes, bytearray, memoryview)):
        return "'\\x" + bytes(v).hex() + "'::bytea"
    if isinstance(v, _dt.datetime):
        return _texto(v.isoformat(sep=" ")) + ("::timestamptz" if v.tzinfo else "::timestamp")
    if isinstance(v, _dt.date):
        return _texto(v.isoformat()) + "::date"
    if isinstance(v, _dt.time):
        return _texto(v.isoformat()) + "::time"
    if isinstance(v, _dt.timedelta):
        return _texto(f"{v.total_seconds()} seconds") + "::interval"
    if isinstance(v, list):
        return "ARRAY[" + ",".join(literal(x) for x in v) + "]" if v else "'{}'"
    if isinstance(v, tuple):
        return "(" + ",".join(literal(x) for x in v) + ")"
    if isinstance(v, dict):
        raise ProgrammingError("can't adapt type 'dict' (usa psycopg2.extras.Json(dato))")
    if "\x00" in str(v):
        raise DataError("A string literal cannot contain NUL (0x00) characters.")
    return _texto(v)


def mogrify(sql, args=None):
    if hasattr(sql, "as_string"):
        sql = sql.as_string(None)
    if args is None:
        return sql
    if isinstance(args, dict):
        return sql % {k: literal(v) for k, v in args.items()}
    if not isinstance(args, (list, tuple)):
        raise TypeError("los parámetros deben ser una tupla, una lista o un diccionario")
    return sql % tuple(literal(a) for a in args)


def _convertir(valor, tipo):
    if valor is None:
        return None
    if isinstance(valor, dict) and "$bytes" in valor:
        return memoryview(bytes.fromhex(valor["$bytes"]))
    if isinstance(valor, dict) and "$json" in valor:
        return _json.loads(valor["$json"])
    try:
        if tipo == 1700:
            return _dec.Decimal(valor)
        if tipo in (1114, 1184):
            return _dt.datetime.fromisoformat(valor)
        if tipo == 1082:
            return _dt.date.fromisoformat(valor)
        if tipo in (1083, 1266):
            return _dt.time.fromisoformat(valor)
        if tipo == 1186:
            signo = -1 if str(valor).startswith("-") else 1
            h, m, s = str(valor).lstrip("-").split(":")
            return signo * _dt.timedelta(hours=int(h), minutes=int(m), seconds=float(s))
        if tipo == 17 and isinstance(valor, str):
            return memoryview(valor.encode())
        if tipo in (700, 701) and isinstance(valor, str):
            return float(valor)
    except (ValueError, ArithmeticError):
        return valor
    return valor


class cursor(_b.Cursor):
    def _resultado(self, r):
        super()._resultado(r)
        self.statusmessage = r.get("comando")
        if self.description:
            self.description = tuple(Column(*d) for d in self.description)
        self.lastrowid = None

    @property
    def query(self):
        return getattr(self, "_q", None)

    def execute(self, query, vars=None):
        self._q = mogrify(query, vars).encode()
        super().execute(query, vars)
        return None

    def executemany(self, query, vars_list):
        super().executemany(query, vars_list)
        return None

    def fetchall(self):
        return list(super().fetchall())

    def copy_expert(self, *a, **k):
        raise NotSupportedError("COPY no está disponible en el navegador; usa INSERT.")

    copy_from = copy_to = copy_expert


class connection(_b.Connection):
    _motor = "postgres"
    _mogrify = staticmethod(mogrify)
    _convertir = staticmethod(_convertir)
    _crear_error = staticmethod(errors._crear)

    def __init__(self, dsn=None, connection_factory=None, cursor_factory=None, **kw):
        datos = _dsn(dsn or "")
        datos.update({k: v for k, v in kw.items() if v is not None})
        self.cursor_factory = cursor_factory or cursor
        self.dsn = dsn or " ".join(f"{k}={v}" for k, v in datos.items() if k != "password")
        self.closed = 0
        self.status = 1
        self.notices = []
        super().__init__(host=datos.get("host") or "localhost", user=datos.get("user") or "postgres", password=datos.get("password") or "",
                         database=datos.get("dbname") or datos.get("database") or None, port=int(datos.get("port") or 5432), autocommit=False)
        self.info = type("Info", (), {"dbname": self.db, "user": self.user, "host": self.host, "port": self.port, "server_version": self.server_version})()

    def cursor(self, name=None, cursor_factory=None, **_):
        return (cursor_factory or self.cursor_factory)(self)

    @property
    def autocommit(self):
        return self._autocommit

    @autocommit.setter
    def autocommit(self, valor):
        if bool(valor) != self._autocommit:
            if valor:
                try:
                    self._consulta("COMMIT")
                except Error:
                    pass
            self._autocommit = bool(valor)
            self._reabrir_modo()

    def _reabrir_modo(self):
        # pg8000 decide BEGIN implícito por conexión: se reabre la sesión con el modo nuevo.
        try:
            _b._pedir("cerrar", {"sesion": self._sesion})
        except Error:
            pass
        r = _b._pedir("conectar", {"motor": "postgres", "host": self.host, "puerto": self.port, "usuario": self.user, "clave": self._clave, "base": self.db, "autocommit": self._autocommit}, self._crear_error)
        self._sesion = r["sesion"]

    def set_session(self, isolation_level=None, readonly=None, deferrable=None, autocommit=None):
        if autocommit is not None:
            self.autocommit = autocommit

    def get_dsn_parameters(self):
        return {"user": self.user, "dbname": self.db, "host": self.host, "port": str(self.port)}

    @property
    def server_version_num(self):
        try:
            p = [int(x) for x in _re.findall(r"\d+", self.server_version)[:2]]
            return p[0] * 10000 + (p[1] if len(p) > 1 else 0)
        except Exception:
            return 0

    def close(self):
        super().close()
        self.closed = 1

    def __enter__(self):
        return self

    def __exit__(self, tipo, *a):
        # Como psycopg2: confirma o deshace, pero NO cierra la conexión.
        if tipo is None:
            self.commit()
        else:
            try:
                self.rollback()
            except Error:
                pass


def _dsn(dsn):
    datos = {}
    if dsn.startswith(("postgres://", "postgresql://")):
        from urllib.parse import unquote, urlsplit, parse_qsl
        u = urlsplit(dsn)
        datos.update(host=u.hostname, port=u.port, user=unquote(u.username) if u.username else None,
                     password=unquote(u.password) if u.password else None, dbname=unquote(u.path[1:]) if len(u.path) > 1 else None)
        datos.update(dict(parse_qsl(u.query)))
    else:
        for m in _re.finditer(r"(\w+)\s*=\s*('(?:[^'\\]|\\.)*'|\S+)", dsn):
            v = m.group(2)
            datos[m.group(1)] = v[1:-1].replace("\\'", "'") if v.startswith("'") else v
    return {k: v for k, v in datos.items() if v is not None}


def connect(dsn=None, connection_factory=None, cursor_factory=None, **kwargs):
    if "database" in kwargs and "dbname" not in kwargs:
        kwargs["dbname"] = kwargs.pop("database")
    if "passwd" in kwargs:
        kwargs["password"] = kwargs.pop("passwd")
    c = (connection_factory or connection)(dsn, cursor_factory=cursor_factory, **kwargs)
    return c


Binary = bytes
Date, Time, Timestamp = _dt.date, _dt.time, _dt.datetime
`;
const PSYCOPG2_FIN = "\nfrom . import extensions, extras, sql  # noqa: E402,F401\n";

// psycopg2: guardamos la clave para poder reabrir la sesión al cambiar autocommit.
const PSYCOPG2_PARCHE = String.raw`
_orig = connection.__init__
def _init(self, dsn=None, connection_factory=None, cursor_factory=None, **kw):
    d = _dsn(dsn or ""); d.update({k: v for k, v in kw.items() if v is not None})
    self._clave = d.get("password") or ""
    _orig(self, dsn, connection_factory, cursor_factory, **kw)
connection.__init__ = _init
`;

const PSYCOPG2_ERRORS = String.raw`
from _cc_mysql_base import Error as _BaseError, Warning  # noqa: F401
import _cc_mysql_base as _b


class Error(_BaseError):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.pgcode = None
        self.pgerror = str(self.msg)
        self.diag = type("Diag", (), {"message_primary": str(self.msg), "sqlstate": None})()

    def __str__(self):
        return str(self.msg)


class InterfaceError(Error): pass
class DatabaseError(Error): pass
class DataError(DatabaseError): pass
class OperationalError(DatabaseError): pass
class IntegrityError(DatabaseError): pass
class InternalError(DatabaseError): pass
class ProgrammingError(DatabaseError): pass
class NotSupportedError(DatabaseError): pass
class TransactionRollbackError(OperationalError): pass
class QueryCanceledError(OperationalError): pass
class UniqueViolation(IntegrityError): pass
class ForeignKeyViolation(IntegrityError): pass
class NotNullViolation(IntegrityError): pass
class CheckViolation(IntegrityError): pass
class UndefinedTable(ProgrammingError): pass
class UndefinedColumn(ProgrammingError): pass
class UndefinedFunction(ProgrammingError): pass
class SyntaxError(ProgrammingError): pass  # noqa: A001
class DuplicateTable(ProgrammingError): pass
class DuplicateDatabase(ProgrammingError): pass
class InvalidCatalogName(OperationalError): pass
class InvalidPassword(OperationalError): pass
class InFailedSqlTransaction(InternalError): pass
class InvalidTextRepresentation(DataError): pass
class DivisionByZero(DataError): pass
class NumericValueOutOfRange(DataError): pass

_POR_CODIGO = {"23505": UniqueViolation, "23503": ForeignKeyViolation, "23502": NotNullViolation, "23514": CheckViolation,
               "42P01": UndefinedTable, "42703": UndefinedColumn, "42883": UndefinedFunction, "42601": SyntaxError,
               "42P07": DuplicateTable, "42P04": DuplicateDatabase, "3D000": InvalidCatalogName, "28P01": InvalidPassword,
               "25P02": InFailedSqlTransaction, "22P02": InvalidTextRepresentation, "22012": DivisionByZero, "22003": NumericValueOutOfRange,
               "40001": TransactionRollbackError, "40P01": TransactionRollbackError, "57014": QueryCanceledError}
_POR_CLASE = {"23": IntegrityError, "42": ProgrammingError, "22": DataError, "08": OperationalError, "28": OperationalError,
              "3D": OperationalError, "53": OperationalError, "57": OperationalError, "40": TransactionRollbackError, "25": InternalError, "XX": InternalError}


def lookup(code):
    return _POR_CODIGO[code]


def _crear(datos):
    codigo, texto = datos.get("codigo"), datos.get("error") or "error"
    texto = texto[len("ERROR:  "):] if texto.startswith("ERROR:  ") else texto
    if isinstance(codigo, str):
        clase = _POR_CODIGO.get(codigo) or _POR_CLASE.get(codigo[:2], DatabaseError)
    else:
        clase = OperationalError
    e = clase(texto + "\n")
    e.pgcode = codigo if isinstance(codigo, str) else None
    e.diag.sqlstate = e.pgcode
    return e
`;

const PSYCOPG2_EXTENSIONS = String.raw`
import json as _json
ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_SERIALIZABLE = 0, 1, 4
STATUS_READY, STATUS_BEGIN = 1, 2


class AsIs:
    def __init__(self, v):
        self.v = v

    def getquoted(self):
        return str(self.v)


def adapt(v):
    from psycopg2 import literal
    return AsIs(literal(v))


def register_adapter(*a, **k):
    pass


def register_type(*a, **k):
    pass


def quote_ident(nombre, scope=None):
    return '"' + str(nombre).replace('"', '""') + '"'
`;

const PSYCOPG2_EXTRAS = String.raw`
import json as _json
import psycopg2 as _p


class Json:
    def __init__(self, adapted, dumps=None):
        self.adapted, self._dumps = adapted, dumps or _json.dumps

    def getquoted(self):
        return "'" + self._dumps(self.adapted).replace("'", "''") + "'"


class RealDictRow(dict):
    pass


class RealDictCursor(_p.cursor):
    _como_dict = True

    def _resultado(self, r):
        super()._resultado(r)
        self._filas = [RealDictRow(f) for f in self._filas]


class DictRow(list):
    def __init__(self, valores, indices):
        super().__init__(valores)
        self._indices = indices

    def __getitem__(self, k):
        return super().__getitem__(self._indices[k] if isinstance(k, str) else k)

    def keys(self):
        return self._indices.keys()

    def values(self):
        return list(self)

    def items(self):
        return [(k, self[k]) for k in self._indices]

    def get(self, k, d=None):
        return self[k] if k in self._indices else d


class DictCursor(_p.cursor):
    def _resultado(self, r):
        super()._resultado(r)
        if self.description:
            indices = {d.name: i for i, d in enumerate(self.description)}
            self._filas = [DictRow(f, indices) for f in self._filas]


class NamedTupleCursor(_p.cursor):
    def _resultado(self, r):
        super()._resultado(r)
        if self.description:
            from collections import namedtuple
            Fila = namedtuple("Record", [d.name for d in self.description], rename=True)
            self._filas = [Fila(*f) for f in self._filas]


RealDictConnection = DictConnection = NamedTupleConnection = _p.connection


def execute_values(cur, sql, argslist, template=None, page_size=100, fetch=False):
    filas = []
    lista = list(argslist)
    for i in range(0, len(lista), page_size or len(lista) or 1):
        trozo = lista[i:i + (page_size or len(lista))]
        if template:
            valores = ",".join(_p.mogrify(template, a) for a in trozo)
        else:
            valores = ",".join("(" + ",".join(_p.literal(x) for x in (a.values() if isinstance(a, dict) else a)) + ")" for a in trozo)
        cur.execute(sql.replace("%s", valores, 1) if "%s" in sql else sql)
        if fetch:
            filas.extend(cur.fetchall())
    return filas if fetch else None


def execute_batch(cur, sql, argslist, page_size=100):
    cur.executemany(sql, argslist)
`;

const PSYCOPG2_SQL = String.raw`
class Composable:
    def __add__(self, otro):
        return Composed([self, otro])

    def format(self, *args, **kw):
        import re
        partes, i = [], 0
        def rep(m):
            nonlocal i
            if m.group(1):
                v = kw[m.group(1)]
            else:
                v = args[i]; i += 1
            return v.as_string(None) if hasattr(v, "as_string") else str(v)
        return SQL(re.sub(r"\{(\w*)\}", rep, self.as_string(None)))

    def join(self, seq):
        return Composed([x for n, s in enumerate(seq) for x in ([self] if n else []) + [s]])


class SQL(Composable):
    def __init__(self, s):
        self._s = s

    def as_string(self, ctx):
        return self._s


class Identifier(Composable):
    def __init__(self, *nombres):
        self._n = nombres

    def as_string(self, ctx):
        return ".".join('"' + n.replace('"', '""') + '"' for n in self._n)


class Literal(Composable):
    def __init__(self, v):
        self._v = v

    def as_string(self, ctx):
        import psycopg2
        return psycopg2.literal(self._v)


class Placeholder(Composable):
    def __init__(self, nombre=None):
        self._n = nombre

    def as_string(self, ctx):
        return f"%({self._n})s" if self._n else "%s"


class Composed(Composable):
    def __init__(self, partes):
        self._p = list(partes)

    def as_string(self, ctx):
        return "".join(p.as_string(ctx) for p in self._p)
`;

const PSYCOPG3 = String.raw`
"""psycopg (versión 3) de CódigoCamp: lo básico de la API, sobre el mismo PostgreSQL."""
import psycopg2 as _p
from psycopg2.errors import *  # noqa: F401,F403
from psycopg2.errors import Error  # noqa: F401
from . import rows  # noqa: E402


class Cursor(_p.cursor):
    def __init__(self, conexion, row_factory=None):
        super().__init__(conexion)
        self.row_factory = row_factory or conexion.row_factory

    def _resultado(self, r):
        super()._resultado(r)
        if self.row_factory is not None and self.description:
            self._filas = [self.row_factory(self)(f) for f in self._filas]

    def execute(self, query, params=None, **_):
        super().execute(query, params)
        return self

    def __exit__(self, *a):
        self.close()


class Connection(_p.connection):
    def __init__(self, conninfo="", row_factory=None, autocommit=False, **kw):
        self.row_factory = row_factory
        super().__init__(conninfo, **kw)
        if autocommit:
            self.autocommit = True

    @classmethod
    def connect(cls, conninfo="", **kw):
        return connect(conninfo, **kw)

    def cursor(self, name=None, row_factory=None, **_):
        return Cursor(self, row_factory)

    def execute(self, query, params=None, **_):
        return self.cursor().execute(query, params)

    def __exit__(self, tipo, *a):
        try:
            _p.connection.__exit__(self, tipo, *a)
        finally:
            self.close()


def connect(conninfo="", *, row_factory=None, autocommit=False, **kwargs):
    if "database" in kwargs and "dbname" not in kwargs:
        kwargs["dbname"] = kwargs.pop("database")
    return Connection(conninfo, row_factory=row_factory, autocommit=autocommit, **kwargs)
`;

const PSYCOPG3_ROWS = String.raw`
def dict_row(cursor):
    nombres = [d.name for d in cursor.description]
    return lambda valores: dict(zip(nombres, valores))


def tuple_row(cursor):
    return tuple


def namedtuple_row(cursor):
    from collections import namedtuple
    Fila = namedtuple("Row", [d.name for d in cursor.description], rename=True)
    return lambda valores: Fila(*valores)
`;

// --------------------------------------------------------------------------- MongoDB ----
const BSON = String.raw`
"""bson de CódigoCamp: ObjectId, Decimal128 y la conversión a Extended JSON que usa pymongo."""
import base64 as _b64
import binascii as _bin
import datetime as _dt
import decimal as _dec
import os as _os
import re as _re
import struct as _struct
import threading as _th
import time as _time

_contador = [int.from_bytes(_os.urandom(3), "big")]
_lock = _th.Lock()
_aleatorio = _os.urandom(5)


class InvalidId(ValueError):
    pass


class ObjectId:
    __slots__ = ("_id",)

    def __init__(self, oid=None):
        if oid is None:
            with _lock:
                _contador[0] = (_contador[0] + 1) % 0xFFFFFF
                c = _contador[0]
            self._id = _struct.pack(">I", int(_time.time())) + _aleatorio + c.to_bytes(3, "big")
        elif isinstance(oid, ObjectId):
            self._id = oid._id
        elif isinstance(oid, bytes) and len(oid) == 12:
            self._id = oid
        elif isinstance(oid, str) and _re.fullmatch(r"[0-9a-fA-F]{24}", oid):
            self._id = _bin.unhexlify(oid)
        else:
            raise InvalidId(f"{oid!r} is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string")

    @classmethod
    def is_valid(cls, oid):
        try:
            cls(oid)
            return True
        except (InvalidId, TypeError):
            return False

    @property
    def binary(self):
        return self._id

    @property
    def generation_time(self):
        return _dt.datetime.fromtimestamp(_struct.unpack(">I", self._id[:4])[0], _dt.timezone.utc)

    def __str__(self):
        return _bin.hexlify(self._id).decode()

    def __repr__(self):
        return f"ObjectId('{self}')"

    def __eq__(self, otro):
        return isinstance(otro, ObjectId) and otro._id == self._id

    def __lt__(self, otro):
        return self._id < otro._id

    def __hash__(self):
        return hash(self._id)


class Decimal128:
    def __init__(self, valor):
        self._d = _dec.Decimal(str(valor))

    def to_decimal(self):
        return self._d

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return f"Decimal128('{self._d}')"

    def __eq__(self, otro):
        return isinstance(otro, Decimal128) and otro._d == self._d


class Int64(int):
    pass


class Regex:
    def __init__(self, pattern, flags=""):
        self.pattern, self.flags = pattern, flags


class SON(dict):
    pass


def a_ejson(v):
    """Python → Extended JSON (para mandarlo al servidor)."""
    if isinstance(v, ObjectId):
        return {"$oid": str(v)}
    if isinstance(v, _dt.datetime):
        if v.tzinfo:
            v = v.astimezone(_dt.timezone.utc).replace(tzinfo=None)
        return {"$date": v.isoformat(timespec="milliseconds") + "Z"}
    if isinstance(v, _dt.date):
        raise TypeError("documents cannot contain datetime.date; usa datetime.datetime")
    if isinstance(v, Decimal128):
        return {"$numberDecimal": str(v)}
    if isinstance(v, _dec.Decimal):
        raise TypeError("cannot encode object: Decimal; usa bson.Decimal128(valor)")
    if isinstance(v, (bytes, bytearray)):
        return {"$binary": {"base64": _b64.b64encode(bytes(v)).decode(), "subType": "00"}}
    if isinstance(v, _re.Pattern):
        return {"$regularExpression": {"pattern": v.pattern, "options": "i" if v.flags & _re.I else ""}}
    if isinstance(v, Regex):
        return {"$regularExpression": {"pattern": v.pattern, "options": v.flags}}
    if isinstance(v, dict):
        return {str(k): a_ejson(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [a_ejson(x) for x in v]
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return {"$numberDouble": str(v).replace("inf", "Infinity").replace("nan", "NaN")}
    return v


def de_ejson(v):
    """Extended JSON → Python (como lo devuelve pymongo)."""
    if isinstance(v, list):
        return [de_ejson(x) for x in v]
    if not isinstance(v, dict):
        return v
    if len(v) == 1:
        (k, x), = v.items()
        if k == "$oid":
            return ObjectId(x)
        if k == "$date":
            if isinstance(x, dict):
                return _dt.datetime(1970, 1, 1) + _dt.timedelta(milliseconds=int(x["$numberLong"]))
            return _dt.datetime.fromisoformat(x.replace("Z", "+00:00")).astimezone(_dt.timezone.utc).replace(tzinfo=None)
        if k == "$numberDecimal":
            return Decimal128(x)
        if k == "$numberLong":
            return int(x)
        if k == "$numberDouble":
            return float(x.replace("Infinity", "inf"))
        if k == "$binary":
            return _b64.b64decode(x["base64"])
        if k == "$regularExpression":
            return Regex(x["pattern"], x["options"])
        if k == "$uuid":
            import uuid
            return uuid.UUID(x)
    return {k: de_ejson(x) for k, x in v.items()}
`;

const BSON_OBJECTID = "from bson import ObjectId, InvalidId  # noqa: F401\n";
const BSON_ERRORS = "from bson import InvalidId  # noqa: F401\nclass InvalidDocument(ValueError):\n    pass\n";
const BSON_JSON_UTIL = String.raw`
import json as _json
from bson import a_ejson, de_ejson


def dumps(obj, *args, **kwargs):
    kwargs.pop("json_options", None)
    return _json.dumps(a_ejson(obj), *args, **kwargs)


def loads(s, *args, **kwargs):
    kwargs.pop("json_options", None)
    return de_ejson(_json.loads(s, *args, **kwargs))


RELAXED_JSON_OPTIONS = CANONICAL_JSON_OPTIONS = DEFAULT_JSON_OPTIONS = None
`;

const PYMONGO = String.raw`
"""pymongo de CódigoCamp: misma API que el real; las operaciones van a tu MongoDB (servidor de CódigoCamp o puente)."""
import json as _json
from urllib.parse import quote_plus as _q

import _cc_bd
from bson import ObjectId, a_ejson, de_ejson  # noqa: F401
from . import errors, results  # noqa: E402
from .errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError, OperationFailure, DuplicateKeyError, WriteError, ConfigurationError  # noqa: F401
from .results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult

version = __version__ = "4.6.0 (CódigoCamp)"
ASCENDING, DESCENDING, GEO2D, GEOSPHERE, HASHED, TEXT = 1, -1, "2d", "2dsphere", "hashed", "text"
_abiertas = []


class ReturnDocument:
    BEFORE = False
    AFTER = True


def _pedir(accion, datos):
    r = _json.loads(_cc_bd.pedir(accion, _json.dumps(datos)))
    if "__error" in r:
        texto, codigo = r["__error"] or "", r.get("codigo")
        if accion == "conectar":
            raise ServerSelectionTimeoutError(texto)
        if codigo == 11000:
            raise DuplicateKeyError(texto.replace("MongoServerError: ", ""), codigo)
        if texto.startswith("MongoServerError: "):
            raise OperationFailure(texto[len("MongoServerError: "):], codigo)
        raise PyMongoError(texto)
    return r


def _cerrar_todas():
    for c in list(_abiertas):
        c.close()


def _orden(clave, direccion=None):
    if isinstance(clave, str):
        return [[clave, direccion if direccion is not None else ASCENDING]]
    if isinstance(clave, dict):
        return [[k, v] for k, v in clave.items()]
    return [[k, v] for k, v in clave]


class Cursor:
    def __init__(self, coleccion, filtro, proyeccion, opciones):
        self._col, self._filtro, self._proy, self._op = coleccion, filtro, proyeccion, dict(opciones)
        self._docs = None
        self._i = 0

    def _ejecutar(self):
        if self._docs is None:
            args = [self._filtro or {}] + ([self._proy] if self._proy is not None else [])
            self._docs = self._col._op("find", args, self._op)
        return self._docs

    def sort(self, clave, direccion=None):
        self._op["sort"] = _orden(clave, direccion)
        return self

    def limit(self, n):
        if n:
            self._op["limit"] = int(n)
        return self

    def skip(self, n):
        self._op["skip"] = int(n)
        return self

    def batch_size(self, n):
        return self

    def hint(self, *a):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        docs = self._ejecutar()
        if self._i >= len(docs):
            raise StopIteration
        self._i += 1
        return docs[self._i - 1]

    next = __next__

    def to_list(self, length=None):
        docs = self._ejecutar()[self._i:]
        return docs if length is None else docs[:length]

    def clone(self):
        return Cursor(self._col, self._filtro, self._proy, self._op)

    def rewind(self):
        self._i = 0
        return self

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def __getitem__(self, i):
        return self._ejecutar()[i]


class CommandCursor(list):
    def next(self):
        return self.pop(0)

    def close(self):
        pass

    def to_list(self, length=None):
        return list(self) if length is None else list(self)[:length]


class Collection:
    def __init__(self, database, name):
        self.database, self.name = database, name
        self.full_name = f"{database.name}.{name}"

    def __getattr__(self, n):
        if n.startswith("_"):
            raise AttributeError(n)
        return Collection(self.database, f"{self.name}.{n}")

    def __getitem__(self, n):
        return Collection(self.database, f"{self.name}.{n}")

    def __repr__(self):
        return f"Collection({self.database!r}, '{self.name}')"

    def __eq__(self, otro):
        return isinstance(otro, Collection) and otro.full_name == self.full_name

    def _op(self, operacion, args=(), opciones=None):
        r = self.database.client._consulta({"operacion": operacion, "base": self.database.name, "coleccion": self.name,
                                            "args": a_ejson(list(args)), "opciones": a_ejson(opciones or {})})
        return de_ejson(r["resultado"])

    @staticmethod
    def _kw(kw):
        return {k: (_orden(v) if k == "sort" else v) for k, v in kw.items() if k not in ("session", "comment", "bypass_document_validation") and v is not None}

    def insert_one(self, document, **kw):
        if "_id" not in document:
            document["_id"] = ObjectId()
        r = self._op("insert_one", [document])
        return InsertOneResult(r.get("insertedId", document["_id"]), True)

    def insert_many(self, documents, ordered=True, **kw):
        documents = list(documents)
        for d in documents:
            if "_id" not in d:
                d["_id"] = ObjectId()
        self._op("insert_many", [documents], {"ordered": ordered})
        return InsertManyResult([d["_id"] for d in documents], True)

    def find(self, filter=None, projection=None, skip=0, limit=0, sort=None, **kw):
        op = {}
        if sort:
            op["sort"] = _orden(sort)
        if skip:
            op["skip"] = skip
        if limit:
            op["limit"] = limit
        return Cursor(self, filter, projection, op)

    def find_one(self, filter=None, *args, **kw):
        if filter is not None and not isinstance(filter, dict):
            filter = {"_id": filter}
        docs = self.find(filter, *args, **kw).limit(1).to_list()
        return docs[0] if docs else None

    def _actualizar(self, op, filtro, cambio, kw):
        r = self._op(op, [filtro, cambio], self._kw(kw))
        return UpdateResult(r, True)

    def update_one(self, filter, update, upsert=False, **kw):
        return self._actualizar("update_one", filter, update, {**kw, "upsert": upsert})

    def update_many(self, filter, update, upsert=False, **kw):
        return self._actualizar("update_many", filter, update, {**kw, "upsert": upsert})

    def replace_one(self, filter, replacement, upsert=False, **kw):
        return self._actualizar("replace_one", filter, replacement, {**kw, "upsert": upsert})

    def delete_one(self, filter, **kw):
        return DeleteResult(self._op("delete_one", [filter]), True)

    def delete_many(self, filter, **kw):
        return DeleteResult(self._op("delete_many", [filter]), True)

    def count_documents(self, filter, **kw):
        return self._op("count_documents", [filter], self._kw(kw))

    def estimated_document_count(self, **kw):
        return self._op("estimated_document_count")

    def aggregate(self, pipeline, **kw):
        return CommandCursor(self._op("aggregate", [list(pipeline)], self._kw({k: v for k, v in kw.items() if k == "allowDiskUse"})))

    def distinct(self, key, filter=None, **kw):
        return self._op("distinct", [key] + ([filter] if filter else []))

    def create_index(self, keys, **kw):
        return self._op("create_index", [_orden(keys)], self._kw(kw))

    def create_indexes(self, indexes):
        return [self.create_index(i.document["key"], **{k: v for k, v in i.document.items() if k != "key"}) for i in indexes]

    def drop_index(self, index_or_name):
        return self._op("drop_index", [index_or_name if isinstance(index_or_name, str) else _orden(index_or_name)])

    def drop_indexes(self):
        return self._op("drop_indexes")

    def index_information(self):
        return self._op("index_information")

    def list_indexes(self):
        return CommandCursor(self._op("list_indexes"))

    def drop(self):
        self._op("drop")

    def rename(self, new_name, **kw):
        return self._op("rename", [new_name], kw)

    def find_one_and_update(self, filter, update, projection=None, sort=None, upsert=False, return_document=ReturnDocument.BEFORE, **kw):
        return self._op("find_one_and_update", [filter, update], self._kw({"projection": projection, "sort": sort, "upsert": upsert, "return_document": return_document}))

    def find_one_and_replace(self, filter, replacement, projection=None, sort=None, upsert=False, return_document=ReturnDocument.BEFORE, **kw):
        return self._op("find_one_and_replace", [filter, replacement], self._kw({"projection": projection, "sort": sort, "upsert": upsert, "return_document": return_document}))

    def find_one_and_delete(self, filter, projection=None, sort=None, **kw):
        return self._op("find_one_and_delete", [filter], self._kw({"projection": projection, "sort": sort}))

    def bulk_write(self, requests, ordered=True, **kw):
        for r in requests:
            r._ejecutar(self)
        return results.BulkWriteResult(len(requests))


class Database:
    def __init__(self, client, name):
        self.client, self.name = client, name

    def __getattr__(self, n):
        if n.startswith("_"):
            raise AttributeError(n)
        return Collection(self, n)

    def __getitem__(self, n):
        return Collection(self, n)

    def get_collection(self, n, **kw):
        return Collection(self, n)

    def __repr__(self):
        return f"Database(MongoClient(...), '{self.name}')"

    def _op(self, operacion, args=(), opciones=None):
        r = self.client._consulta({"operacion": operacion, "base": self.name, "args": a_ejson(list(args)), "opciones": a_ejson(opciones or {})})
        return de_ejson(r["resultado"])

    def list_collection_names(self, **kw):
        return self._op("list_collection_names")

    def create_collection(self, name, **kw):
        self._op("create_collection", [name])
        return Collection(self, name)

    def drop_collection(self, name, **kw):
        return self._op("drop_collection", [name if isinstance(name, str) else name.name])

    def command(self, command, value=1, **kw):
        if isinstance(command, str):
            command = {command: value, **kw}
        return self._op("command", [command])


class MongoClient:
    HOST, PORT = "localhost", 27017

    def __init__(self, host=None, port=None, document_class=dict, tz_aware=False, connect=True, **kw):
        host = host or "localhost"
        if isinstance(host, (list, tuple)):
            host = ",".join(host)
        if host.startswith(("mongodb://", "mongodb+srv://")):
            uri = host
        else:
            usuario, clave = kw.get("username"), kw.get("password")
            auth = f"{_q(usuario)}:{_q(clave or '')}@" if usuario else ""
            fuente = f"?authSource={kw.get('authSource') or 'admin'}" if usuario else ""
            uri = f"mongodb://{auth}{host}:{port or 27017}/{fuente}"
        r = _pedir("conectar", {"motor": "mongodb", "uri": uri})
        self._sesion, self._base = r["sesion"], r.get("base")
        self.address = (host.split("//")[-1].split("@")[-1].split("/")[0].split(":")[0], int(port or 27017))
        self._abierta = True
        _abiertas.append(self)

    def _consulta(self, datos):
        if not self._abierta:
            raise errors.InvalidOperation("Cannot use MongoClient after close")
        return _pedir("consulta", {"sesion": self._sesion, **datos})

    def __getattr__(self, n):
        if n.startswith("_"):
            raise AttributeError(n)
        return Database(self, n)

    def __getitem__(self, n):
        return Database(self, n)

    def get_database(self, name=None, **kw):
        return Database(self, name or self._base or "test")

    def get_default_database(self, default=None, **kw):
        nombre = self._base if self._base and self._base != "test" else default
        if not nombre:
            raise ConfigurationError("No default database name defined or provided.")
        return Database(self, nombre)

    def list_database_names(self, **kw):
        return de_ejson(self._consulta({"operacion": "list_database_names"})["resultado"])

    def drop_database(self, name, **kw):
        self._consulta({"operacion": "drop_database", "base": name if isinstance(name, str) else name.name})

    def server_info(self):
        return Database(self, "admin").command("buildinfo")

    def start_session(self, **kw):
        raise errors.InvalidOperation("Las sesiones/transacciones no están disponibles en el navegador.")

    def close(self):
        if self._abierta:
            self._abierta = False
            try:
                _pedir("cerrar", {"sesion": self._sesion})
            except PyMongoError:
                pass
            if self in _abiertas:
                _abiertas.remove(self)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class _Escritura:
    def __init__(self, op, *args, **kw):
        self.op, self.args, self.kw = op, args, kw

    def _ejecutar(self, col):
        getattr(col, self.op)(*self.args, **self.kw)


def InsertOne(document):
    return _Escritura("insert_one", document)


def UpdateOne(filter, update, upsert=False):
    return _Escritura("update_one", filter, update, upsert=upsert)


def UpdateMany(filter, update, upsert=False):
    return _Escritura("update_many", filter, update, upsert=upsert)


def ReplaceOne(filter, replacement, upsert=False):
    return _Escritura("replace_one", filter, replacement, upsert=upsert)


def DeleteOne(filter):
    return _Escritura("delete_one", filter)


def DeleteMany(filter):
    return _Escritura("delete_many", filter)


class IndexModel:
    def __init__(self, keys, **kw):
        self.document = {"key": keys, **kw}
`;

const PYMONGO_ERRORS = String.raw`
class PyMongoError(Exception):
    pass


class ConfigurationError(PyMongoError): pass
class InvalidOperation(PyMongoError): pass
class ConnectionFailure(PyMongoError): pass
class ServerSelectionTimeoutError(ConnectionFailure): pass
class AutoReconnect(ConnectionFailure): pass
class NetworkTimeout(AutoReconnect): pass


class OperationFailure(PyMongoError):
    def __init__(self, error, code=None, details=None):
        super().__init__(error)
        self.code = code
        self.details = details or {"errmsg": error, "code": code}

    @property
    def codeName(self):
        return None


class WriteError(OperationFailure): pass
class DuplicateKeyError(WriteError): pass
class BulkWriteError(OperationFailure): pass
class CollectionInvalid(PyMongoError): pass
`;

const PYMONGO_RESULTS = String.raw`
class InsertOneResult:
    def __init__(self, inserted_id, acknowledged=True):
        self.inserted_id, self.acknowledged = inserted_id, acknowledged

    def __repr__(self):
        return f"InsertOneResult({self.inserted_id!r}, acknowledged={self.acknowledged})"


class InsertManyResult:
    def __init__(self, inserted_ids, acknowledged=True):
        self.inserted_ids, self.acknowledged = inserted_ids, acknowledged

    def __repr__(self):
        return f"InsertManyResult({self.inserted_ids!r}, acknowledged={self.acknowledged})"


class UpdateResult:
    def __init__(self, raw, acknowledged=True):
        self.raw_result, self.acknowledged = raw, acknowledged
        self.matched_count = raw.get("matchedCount", 0)
        self.modified_count = raw.get("modifiedCount", 0)
        self.upserted_id = raw.get("insertedId")

    def __repr__(self):
        return f"UpdateResult({{'n': {self.matched_count}, 'nModified': {self.modified_count}, 'ok': 1.0, 'updatedExisting': {self.matched_count > 0}}}, acknowledged={self.acknowledged})"


class DeleteResult:
    def __init__(self, raw, acknowledged=True):
        self.raw_result, self.acknowledged = raw, acknowledged
        self.deleted_count = raw.get("deletedCount", 0)

    def __repr__(self):
        return f"DeleteResult({{'n': {self.deleted_count}, 'ok': 1.0}}, acknowledged={self.acknowledged})"


class BulkWriteResult:
    def __init__(self, n):
        self.acknowledged = True
        self.n = n
`;

// ----------------------------------------------------------------------------- Redis ----
const REDIS = String.raw`
"""redis de CódigoCamp: misma API que redis-py (lo más usado); los comandos van a tu Redis."""
import json as _json

import _cc_bd
from . import exceptions  # noqa: E402
from .exceptions import RedisError, ConnectionError, ResponseError, AuthenticationError, TimeoutError, DataError  # noqa: F401,A004

__version__ = "5.0.1 (CódigoCamp)"
_abiertas = []


def _cerrar_todas():
    for c in list(_abiertas):
        c.close()


def _desde(v, decodificar):
    if isinstance(v, dict) and "$bytes" in v:
        return bytes.fromhex(v["$bytes"])
    if isinstance(v, list):
        return [_desde(x, decodificar) for x in v]
    if isinstance(v, str):
        return v if decodificar else v.encode()
    return v


class Redis:
    def __init__(self, host="localhost", port=6379, db=0, password=None, username=None, decode_responses=False, socket_timeout=None,
                 socket_connect_timeout=None, ssl=False, encoding="utf-8", **kw):
        self.host, self.port, self.db, self._clave, self._usuario = host, int(port), int(db or 0), password, username
        self.decode_responses = decode_responses
        self._sesion = None
        self.connection_pool = self

    @classmethod
    def from_url(cls, url, **kw):
        from urllib.parse import urlsplit, unquote
        u = urlsplit(url)
        return cls(host=u.hostname or "localhost", port=u.port or 6379, db=int(u.path[1:] or 0) if u.path[1:].isdigit() else 0,
                   password=unquote(u.password) if u.password else None, username=unquote(u.username) if u.username else None, **kw)

    def _conectar(self):
        r = _json.loads(_cc_bd.pedir("conectar", _json.dumps({"motor": "redis", "host": self.host, "puerto": self.port, "usuario": self._usuario,
                                                                   "clave": self._clave or "", "base": self.db})))
        if "__error" in r:
            texto = r["__error"] or ""
            raise (AuthenticationError if "auth" in texto.lower() or "WRONGPASS" in texto else ConnectionError)(texto)
        self._sesion = r["sesion"]
        _abiertas.append(self)

    def execute_command(self, *args, **opciones):
        if self._sesion is None:
            self._conectar()
        datos = []
        for a in args:
            if isinstance(a, bytes):
                a = a.decode("utf-8", "surrogateescape")
            elif isinstance(a, bool) or not isinstance(a, (str, int, float)):
                raise DataError(f"Invalid input of type: '{type(a).__name__}'. Convert to a bytes, string, int or float first.")
            datos.append(a)
        r = _json.loads(_cc_bd.pedir("consulta", _json.dumps({"sesion": self._sesion, "comando": datos})))
        if "__error" in r:
            texto = (r["__error"] or "").replace("(error) ", "")
            if r.get("codigo") == 2013 or "se cerró" in texto:
                self._sesion = None
                raise ConnectionError(texto)
            raise ResponseError(texto)
        return _desde(r["resultado"], self.decode_responses)

    # ---- helpers con la forma de redis-py ----
    def _ok(self, v):
        return v in ("OK", b"OK")

    def ping(self, **kw):
        return self.execute_command("PING") in ("PONG", b"PONG")

    def set(self, name, value, ex=None, px=None, nx=False, xx=False, keepttl=False, get=False, exat=None, pxat=None):
        a = ["SET", name, value]
        if ex is not None:
            a += ["EX", int(ex.total_seconds()) if hasattr(ex, "total_seconds") else ex]
        if px is not None:
            a += ["PX", px]
        if exat is not None:
            a += ["EXAT", exat]
        if pxat is not None:
            a += ["PXAT", pxat]
        if nx:
            a.append("NX")
        if xx:
            a.append("XX")
        if keepttl:
            a.append("KEEPTTL")
        if get:
            a.append("GET")
            return self.execute_command(*a)
        r = self.execute_command(*a)
        return True if self._ok(r) else None

    def setex(self, name, time, value):
        return self._ok(self.execute_command("SETEX", name, int(time.total_seconds()) if hasattr(time, "total_seconds") else time, value))

    def setnx(self, name, value):
        return bool(self.execute_command("SETNX", name, value))

    def mset(self, mapping):
        return self._ok(self.execute_command("MSET", *[x for kv in mapping.items() for x in kv]))

    def mget(self, keys, *args):
        return self.execute_command("MGET", *((list(keys) if isinstance(keys, (list, tuple)) else [keys]) + list(args)))

    def delete(self, *names):
        return self.execute_command("DEL", *names)

    def exists(self, *names):
        return self.execute_command("EXISTS", *names)

    def expire(self, name, time, **kw):
        return bool(self.execute_command("EXPIRE", name, int(time.total_seconds()) if hasattr(time, "total_seconds") else time))

    def keys(self, pattern="*"):
        return self.execute_command("KEYS", pattern)

    def scan_iter(self, match=None, count=None, _type=None):
        cursor = "0"
        while True:
            a = ["SCAN", cursor] + (["MATCH", match] if match else []) + (["COUNT", count] if count else []) + (["TYPE", _type] if _type else [])
            cursor, claves = self.execute_command(*a)
            cursor = cursor.decode() if isinstance(cursor, bytes) else cursor
            yield from claves
            if cursor == "0":
                break

    def incrbyfloat(self, name, amount=1.0):
        return float(self.execute_command("INCRBYFLOAT", name, amount))

    def incr(self, name, amount=1):
        return self.execute_command("INCRBY", name, amount)

    def decr(self, name, amount=1):
        return self.execute_command("DECRBY", name, amount)

    def hset(self, name, key=None, value=None, mapping=None, items=None):
        a = []
        if key is not None:
            a += [key, value]
        if mapping:
            a += [x for kv in mapping.items() for x in kv]
        if items:
            a += list(items)
        return self.execute_command("HSET", name, *a)

    def hmset(self, name, mapping):
        return self._ok(self.execute_command("HMSET", name, *[x for kv in mapping.items() for x in kv]))

    def hgetall(self, name):
        v = self.execute_command("HGETALL", name)
        return dict(zip(v[::2], v[1::2]))

    def hmget(self, name, keys, *args):
        return self.execute_command("HMGET", name, *((list(keys) if isinstance(keys, (list, tuple)) else [keys]) + list(args)))

    def hexists(self, name, key):
        return bool(self.execute_command("HEXISTS", name, key))

    def sismember(self, name, value):
        return bool(self.execute_command("SISMEMBER", name, value))

    def smembers(self, name):
        return set(self.execute_command("SMEMBERS", name))

    def zadd(self, name, mapping, nx=False, xx=False, ch=False, incr=False, gt=False, lt=False):
        a = [o for o, s in (("NX", nx), ("XX", xx), ("GT", gt), ("LT", lt), ("CH", ch), ("INCR", incr)) if s]
        return self.execute_command("ZADD", name, *a, *[x for k, v in mapping.items() for x in (v, k)])

    def zrange(self, name, start, end, desc=False, withscores=False, score_cast_func=float, **kw):
        a = ["ZRANGE", name, start, end] + (["REV"] if desc else []) + (["WITHSCORES"] if withscores else [])
        v = self.execute_command(*a)
        return [(v[i], score_cast_func(v[i + 1])) for i in range(0, len(v), 2)] if withscores else v

    def zscore(self, name, value):
        v = self.execute_command("ZSCORE", name, value)
        return float(v) if v is not None else None

    def flushdb(self, asynchronous=False):
        return self._ok(self.execute_command("FLUSHDB"))

    def info(self, section=None):
        texto = self.execute_command("INFO", *([section] if section else []))
        texto = texto.decode() if isinstance(texto, bytes) else texto
        datos = {}
        for linea in texto.splitlines():
            if ":" in linea and not linea.startswith("#"):
                k, v = linea.split(":", 1)
                datos[k] = int(v) if v.isdigit() else v
        return datos

    def pipeline(self, transaction=True):
        return Pipeline(self)

    def pubsub(self, **kw):
        raise RedisError("Pub/Sub no está disponible en el navegador.")

    def close(self):
        if self._sesion:
            try:
                _cc_bd.pedir("cerrar", _json.dumps({"sesion": self._sesion}))
            except Exception:
                pass
            self._sesion = None
        if self in _abiertas:
            _abiertas.remove(self)

    disconnect = close

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def __getattr__(self, nombre):
        if nombre.startswith("_"):
            raise AttributeError(nombre)
        comando = nombre.upper().split("_")
        return lambda *args, **kw: self.execute_command(*comando, *args)


StrictRedis = Redis


class Pipeline:
    def __init__(self, r):
        self._r, self._cola = r, []

    def __getattr__(self, nombre):
        metodo = getattr(self._r, nombre)
        def encolar(*a, **k):
            self._cola.append((metodo, a, k))
            return self
        return encolar

    def execute(self, raise_on_error=True):
        cola, self._cola = self._cola, []
        return [m(*a, **k) for m, a, k in cola]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self._cola = []


def from_url(url, **kw):
    return Redis.from_url(url, **kw)
`;

const REDIS_EXC = String.raw`
class RedisError(Exception): pass
class ConnectionError(RedisError): pass  # noqa: A001
class TimeoutError(RedisError): pass  # noqa: A001
class AuthenticationError(ConnectionError): pass
class ResponseError(RedisError): pass
class DataError(RedisError): pass
class WatchError(RedisError): pass
`;

export const MODULOS_BD = {
  "psycopg2/__init__.py": PSYCOPG2 + PSYCOPG2_PARCHE + PSYCOPG2_FIN,
  "psycopg2/errors.py": PSYCOPG2_ERRORS,
  "psycopg2/extensions.py": PSYCOPG2_EXTENSIONS,
  "psycopg2/extras.py": PSYCOPG2_EXTRAS,
  "psycopg2/sql.py": PSYCOPG2_SQL,
  "psycopg/__init__.py": PSYCOPG3,
  "psycopg/rows.py": PSYCOPG3_ROWS,
  "bson/__init__.py": BSON,
  "bson/objectid.py": BSON_OBJECTID,
  "bson/errors.py": BSON_ERRORS,
  "bson/json_util.py": BSON_JSON_UTIL,
  "bson/decimal128.py": "from bson import Decimal128  # noqa: F401\n",
  "pymongo/__init__.py": PYMONGO,
  "pymongo/errors.py": PYMONGO_ERRORS,
  "pymongo/results.py": PYMONGO_RESULTS,
  "pymongo/collection.py": "from pymongo import Collection, ReturnDocument  # noqa: F401\n",
  "pymongo/database.py": "from pymongo import Database  # noqa: F401\n",
  "pymongo/cursor.py": "from pymongo import Cursor  # noqa: F401\n",
  "pymongo/mongo_client.py": "from pymongo import MongoClient  # noqa: F401\n",
  "redis/__init__.py": REDIS,
  "redis/exceptions.py": REDIS_EXC,
};
