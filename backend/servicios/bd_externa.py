"""Conexiones a las bases de datos del usuario: MySQL/MariaDB (XAMPP), PostgreSQL, MongoDB y Redis.

Lo usan dos sitios con la misma API:
  · el servidor de CódigoCamp (rutas/bd.py), cuando corre en el mismo PC que las bases;
  · el puente (herramientas/puente_bd.py), un programita que el usuario abre en su PC cuando CódigoCamp está en internet.

Conectores (pip): PyMySQL (MySQL/MariaDB), pg8000 (PostgreSQL), pymongo (MongoDB), redis (Redis).
Si falta uno, el error dice qué instalar. Cada sesión es una conexión abierta, de un dueño, que se cierra sola si no se usa.
"""
import datetime as _dt
import decimal
import ipaddress
import json
import re
import secrets
import threading
import time
import uuid

MAX_SESIONES = 6            # por dueño
INACTIVIDAD = 15 * 60       # segundos sin usarla → se cierra
MAX_FILAS = 10_000          # filas/documentos que se devuelven por consulta
MAX_SQL = 2_000_000         # caracteres por sentencia
HOSTS_LOCALES = ("localhost", "127.0.0.1", "::1")
PUERTOS = {"mysql": 3306, "postgres": 5432, "mongodb": 27017, "redis": 6379}
NOMBRES = {"mysql": "MySQL/MariaDB", "postgres": "PostgreSQL", "mongodb": "MongoDB", "redis": "Redis"}
ALIAS = {"mysql": "mysql", "mariadb": "mysql", "postgres": "postgres", "postgresql": "postgres", "pg": "postgres",
         "mongodb": "mongodb", "mongo": "mongodb", "redis": "redis"}
PISTAS = {
    "mysql": "En XAMPP: abre el Panel de control y pulsa «Start» en MySQL.",
    "postgres": "Inicia PostgreSQL (en Windows: Servicios → postgresql → Iniciar; o desde pgAdmin).",
    "mongodb": "Inicia MongoDB (en Windows: Servicios → MongoDB Server → Iniciar; o «mongod» en una terminal).",
    "redis": "Inicia Redis («redis-server» en una terminal; en Windows con Memurai o WSL).",
}
CONECTORES = {"mysql": "pymysql", "postgres": "pg8000", "mongodb": "pymongo", "redis": "redis"}


class ErrorBD(Exception):
    """Error que se le muestra al usuario tal cual (con el código del motor si lo hay)."""

    def __init__(self, mensaje, codigo=None, estado=400):
        super().__init__(mensaje)
        self.codigo = codigo
        self.estado = estado

    def como_dict(self):
        return {"error": str(self), "codigo": self.codigo}


def host_permitido(host, permitidos):
    """`permitidos`: lista de hosts, IPs o redes (192.168.1.0/24); "*" permite todos."""
    host = (host or "").strip().lower()
    if not host or len(host) > 255:
        return False
    for p in permitidos:
        p = p.strip().lower()
        if not p:
            continue
        if p == "*" or p == host:
            return True
        if "/" in p:
            try:
                if ipaddress.ip_address(host) in ipaddress.ip_network(p, strict=False):
                    return True
            except ValueError:
                pass
    return False


def host_de_uri(uri):
    """Hosts de una URI mongodb:// (para comprobarlos contra la lista permitida). mongodb+srv no se resuelve aquí."""
    m = re.match(r"^mongodb(\+srv)?://(?:[^@/]*@)?([^/?]+)", uri or "")
    if not m:
        return []
    hosts = []
    for h in m.group(2).split(","):
        hosts.append(h[1:h.index("]")] if h.startswith("[") else h.rsplit(":", 1)[0] if h.count(":") == 1 else h)
    return hosts


def _valor(v):
    """Convierte un valor del motor a algo que se pueda mandar en JSON."""
    if v is None or isinstance(v, (bool, int, str)):
        return v
    if isinstance(v, float):
        return v if v == v and v not in (float("inf"), float("-inf")) else str(v)
    if isinstance(v, decimal.Decimal):
        return str(v)
    if isinstance(v, _dt.datetime):
        return v.isoformat(sep=" ")
    if isinstance(v, (_dt.date, _dt.time)):
        return v.isoformat()
    if isinstance(v, _dt.timedelta):
        s = int(v.total_seconds())
        signo, s = ("-" if s < 0 else ""), abs(s)
        return f"{signo}{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"
    if isinstance(v, (bytes, bytearray, memoryview)):
        b = bytes(v)
        try:
            return b.decode("utf-8")
        except UnicodeDecodeError:
            return {"$bytes": b.hex()}
    if isinstance(v, uuid.UUID):
        return str(v)
    if isinstance(v, (list, tuple)):
        return [_valor(x) for x in v]
    if isinstance(v, dict):
        return {"$json": json.dumps(v, ensure_ascii=False, default=str)}
    if isinstance(v, set):
        return ",".join(sorted(map(str, v)))
    return str(v)


def _falta(motor):
    return ErrorBD(f"Falta el conector de {NOMBRES[motor]} en el servidor/puente: pip install {CONECTORES[motor]}")


def _apagado(motor, host, puerto):
    return f"No se pudo conectar a {NOMBRES[motor]} en {host}:{puerto}. ¿Está encendido? {PISTAS[motor]}"


def _sql_de(datos):
    sql, parametros = datos.get("sql"), datos.get("parametros")
    if not isinstance(sql, str) or not sql.strip():
        raise ErrorBD("La consulta está vacía.")
    if len(sql) > MAX_SQL:
        raise ErrorBD("La consulta es demasiado larga.")
    if parametros is not None and not isinstance(parametros, (list, dict)):
        raise ErrorBD("Los parámetros deben ser una lista o un objeto.")
    return sql, parametros


def _leer_cursor(cur, afectadas):
    columnas = [d[0] for d in cur.description] if cur.description else None
    tipos = [d[1] for d in cur.description] if cur.description else None
    filas, truncado = [], False
    if columnas is not None:
        filas = [[_valor(v) for v in fila] for fila in cur.fetchmany(MAX_FILAS)]
        siguiente = cur.fetchone()
        truncado = siguiente is not None
        while siguiente is not None:
            siguiente = cur.fetchone()
    return {"columnas": columnas, "tipos": tipos, "filas": filas, "truncado": truncado,
            "afectadas": afectadas if columnas is None else len(filas), "avisos": 0, "ultimo_id": None}


# ============================================================================ MySQL ====
_USE = re.compile(r"^\s*use\s", re.I)


class _MySQL:
    motor = "mysql"

    def __init__(self, conectar=None, host="127.0.0.1", puerto=3306, usuario=None, clave="", base=None, autocommit=True, **_):
        try:
            import pymysql
        except ImportError:
            raise _falta("mysql")
        self._pymysql = pymysql
        try:
            self.c = (conectar or pymysql.connect)(
                host=host, port=puerto, user=usuario or "root", password=clave or "", database=base or None,
                charset="utf8mb4", autocommit=bool(autocommit), connect_timeout=5, read_timeout=120, write_timeout=120, local_infile=False)
        except pymysql.err.OperationalError as e:
            codigo = e.args[0] if e.args else None
            texto = e.args[1] if len(e.args) > 1 else str(e)
            if codigo in (2003, 2002):
                texto = _apagado("mysql", host, puerto)
            raise ErrorBD(f"ERROR {codigo}: {texto}" if codigo else texto, codigo)
        except pymysql.err.MySQLError as e:
            raise ErrorBD(str(e))
        v = getattr(self.c, "server_version", "") or ""
        self.version = v.decode("utf-8", "replace") if isinstance(v, bytes) else v
        self.base = base or None

    def consultar(self, datos):
        sql, parametros = _sql_de(datos)
        pymysql = self._pymysql
        try:
            self.c.ping(reconnect=True)
            with self.c.cursor() as cur:
                afectadas = cur.execute(sql, parametros if parametros else None)
                r = _leer_cursor(cur, afectadas)
                r["avisos"] = getattr(self.c, "warning_count", 0) or 0
                r["ultimo_id"] = cur.lastrowid or None
            if _USE.match(sql):
                with self.c.cursor() as cur:
                    cur.execute("SELECT DATABASE()")
                    self.base = cur.fetchone()[0]
        except pymysql.err.MySQLError as e:
            codigo = e.args[0] if e.args and isinstance(e.args[0], int) else None
            texto = e.args[1] if len(e.args) > 1 else str(e)
            raise ErrorBD(f"ERROR {codigo}: {texto}" if codigo else str(texto), codigo)
        except (TypeError, ValueError, KeyError) as e:
            raise ErrorBD(f"Parámetros inválidos para la consulta: {e}")
        return r

    def cerrar(self):
        self.c.close()


# ======================================================================= PostgreSQL ====
def _etiqueta_pg(sql, filas):
    """La etiqueta que muestra psql después de una orden (INSERT 0 1, UPDATE 2, CREATE TABLE…)."""
    palabras = re.sub(r"--[^\n]*", " ", sql).strip().split()
    if not palabras:
        return ""
    p = palabras[0].upper()
    n = max(filas, 0)
    if p == "INSERT":
        return f"INSERT 0 {n}"
    if p in ("UPDATE", "DELETE", "SELECT", "MOVE", "FETCH", "COPY", "MERGE"):
        return f"{p} {n}"
    if p in ("CREATE", "DROP", "ALTER") and len(palabras) > 1:
        resto = [w.upper() for w in palabras[1:4]]
        for saltar in ("OR", "REPLACE", "UNIQUE", "TEMP", "TEMPORARY", "MATERIALIZED", "UNLOGGED"):
            if resto and resto[0] == saltar:
                resto = resto[1:]
        return f"{p} {resto[0] if resto else ''}".strip()
    return p.rstrip(";")


class _Postgres:
    motor = "postgres"

    def __init__(self, conectar=None, host="127.0.0.1", puerto=5432, usuario=None, clave="", base=None, autocommit=True, **_):
        try:
            import pg8000.dbapi as pg
        except ImportError:
            raise _falta("postgres")
        self._pg = pg
        try:
            self.c = (conectar or pg.connect)(host=host, port=puerto, user=usuario or "postgres", password=clave or None,
                                              database=base or "postgres", timeout=120, application_name="CodigoCamp")
        except pg.DatabaseError as e:
            raise ErrorBD(self._texto(e), self._codigo(e))
        except (pg.InterfaceError, OSError) as e:
            texto = str(e)
            raise ErrorBD(_apagado("postgres", host, puerto) if re.search(r"connect|refused|timed out|unreachable", texto, re.I) else texto)
        self.c.autocommit = bool(autocommit)
        self.base = base or "postgres"
        try:
            cur = self.c.cursor()
            cur.execute("SHOW server_version")
            self.version = cur.fetchone()[0]
        except Exception:
            self.version = ""

    @staticmethod
    def _codigo(e):
        d = e.args[0] if e.args and isinstance(e.args[0], dict) else {}
        return d.get("C")

    @staticmethod
    def _texto(e):
        d = e.args[0] if e.args and isinstance(e.args[0], dict) else None
        if not d:
            return f"ERROR:  {e}"
        texto = f"{d.get('S', 'ERROR')}:  {d.get('M', '')}"
        if d.get("D"):
            texto += f"\nDETAIL:  {d['D']}"
        if d.get("H"):
            texto += f"\nHINT:  {d['H']}"
        return texto

    def consultar(self, datos):
        sql, parametros = _sql_de(datos)
        pg = self._pg
        try:
            cur = self.c.cursor()
            if isinstance(parametros, dict):  # %(nombre)s → %s (pg8000 usa el estilo «format»)
                nombres = re.findall(r"%\((\w+)\)s", sql)
                sql, parametros = re.sub(r"%\((\w+)\)s", "%s", sql), [parametros[n] for n in nombres]
            if parametros:
                cur.execute(sql, parametros)
            else:
                cur.execute(sql)
            r = _leer_cursor(cur, cur.rowcount)
            r["comando"] = _etiqueta_pg(sql, cur.rowcount)
        except pg.DatabaseError as e:
            if self.c.autocommit:
                try:
                    self.c.rollback()
                except Exception:
                    pass
            raise ErrorBD(self._texto(e), self._codigo(e))
        except pg.InterfaceError as e:
            raise ErrorBD(f"ERROR:  {e}")
        except (TypeError, ValueError, KeyError) as e:
            raise ErrorBD(f"Parámetros inválidos para la consulta: {e}")
        return r

    def cerrar(self):
        self.c.close()


# =========================================================================== MongoDB ====
OPERACIONES_COLECCION = {
    "find", "find_one", "insert_one", "insert_many", "update_one", "update_many", "replace_one", "delete_one", "delete_many",
    "count_documents", "estimated_document_count", "aggregate", "distinct", "create_index", "drop_index", "drop_indexes",
    "index_information", "list_indexes", "drop", "find_one_and_update", "find_one_and_delete", "find_one_and_replace", "rename",
}
OPERACIONES_BASE = {"list_collection_names", "drop_database", "create_collection", "drop_collection", "command", "stats"}


class _Mongo:
    motor = "mongodb"

    def __init__(self, conectar=None, host="127.0.0.1", puerto=27017, usuario=None, clave="", base=None, uri=None, **_):
        try:
            import pymongo
            from bson import json_util
        except ImportError:
            raise _falta("mongodb")
        self._pymongo, self._json = pymongo, json_util
        opciones = {"serverSelectionTimeoutMS": 4000, "connectTimeoutMS": 4000, "socketTimeoutMS": 120000}
        if uri:
            if not re.match(r"^mongodb(\+srv)?://", uri):
                raise ErrorBD("La dirección debe empezar por mongodb:// o mongodb+srv://")
            self.c = (conectar or pymongo.MongoClient)(uri, **opciones)
        else:
            if usuario:
                opciones.update(username=usuario, password=clave or "")
            self.c = (conectar or pymongo.MongoClient)(host=host, port=puerto, **opciones)
        try:
            self.version = self.c.server_info().get("version", "")
        except pymongo.errors.OperationFailure as e:
            self.c.close()
            raise ErrorBD(f"MongoServerError: {(e.details or {}).get('errmsg') or e}", e.code)
        except pymongo.errors.PyMongoError:
            self.c.close()
            raise ErrorBD(_apagado("mongodb", host if not uri else ",".join(host_de_uri(uri)) or uri, puerto))
        if not base and uri:
            m = re.match(r"^mongodb(?:\+srv)?://[^/]+/([^?]+)", uri)
            base = m.group(1) if m else None
        self.base = base or "test"

    def _resultado(self, v):
        """Resultados de pymongo → algo que se pueda mandar en Extended JSON (con los nombres de mongosh)."""
        p = self._pymongo.results
        if isinstance(v, p.InsertOneResult):
            return {"acknowledged": v.acknowledged, "insertedId": v.inserted_id}
        if isinstance(v, p.InsertManyResult):
            return {"acknowledged": v.acknowledged, "insertedIds": {str(i): x for i, x in enumerate(v.inserted_ids)}}
        if isinstance(v, p.UpdateResult):
            return {"acknowledged": v.acknowledged, "insertedId": v.upserted_id, "matchedCount": v.matched_count,
                    "modifiedCount": v.modified_count, "upsertedCount": 1 if v.upserted_id is not None else 0}
        if isinstance(v, p.DeleteResult):
            return {"acknowledged": v.acknowledged, "deletedCount": v.deleted_count}
        if hasattr(v, "__iter__") and not isinstance(v, (dict, list, str, bytes)):
            docs = []
            for d in v:
                if len(docs) >= MAX_FILAS:
                    break
                docs.append(d)
            return docs
        return v

    def consultar(self, datos):
        pymongo, json_util = self._pymongo, self._json
        op = datos.get("operacion")
        try:
            args = json_util.loads(json.dumps(datos.get("args") or []))
            kwargs = json_util.loads(json.dumps(datos.get("opciones") or {}))
        except (ValueError, TypeError) as e:
            raise ErrorBD(f"Argumentos inválidos: {e}")
        if not isinstance(args, list) or not isinstance(kwargs, dict):
            raise ErrorBD("Argumentos inválidos.")
        base = datos.get("base") or self.base
        if not isinstance(base, str) or not base or len(base) > 64 or re.search(r'[/\\. "$]', base):
            raise ErrorBD("Nombre de base inválido.")
        try:
            if op == "use":
                self.base = base
                valor = f"switched to db {base}"
            elif op == "list_database_names":
                valor = self.c.list_database_names()
            elif op in OPERACIONES_BASE:
                db = self.c[base]
                if op == "drop_database":
                    self.c.drop_database(base)
                    valor = {"ok": 1, "dropped": base}
                elif op == "stats":
                    valor = db.command("dbstats")
                else:
                    valor = getattr(db, op)(*args, **kwargs)
                    if op == "create_collection":
                        valor = {"ok": 1}
            elif op in OPERACIONES_COLECCION:
                nombre = datos.get("coleccion")
                if not isinstance(nombre, str) or not nombre or len(nombre) > 120:
                    raise ErrorBD("Falta el nombre de la colección.")
                col = self.c[base][nombre]
                if op == "find":
                    cur = col.find(*args, **{k: v for k, v in kwargs.items() if k not in ("sort", "limit", "skip")})
                    if kwargs.get("sort"):
                        orden = kwargs["sort"]
                        cur = cur.sort(list(orden.items()) if isinstance(orden, dict) else [tuple(x) if isinstance(x, list) else x for x in orden])
                    if kwargs.get("skip"):
                        cur = cur.skip(int(kwargs["skip"]))
                    cur = cur.limit(min(int(kwargs.get("limit") or MAX_FILAS), MAX_FILAS))
                    valor = list(cur)
                elif op == "drop":
                    col.drop()
                    valor = True
                elif op == "list_indexes":
                    valor = list(col.list_indexes())
                else:
                    if op == "create_index" and args and isinstance(args[0], list):
                        args[0] = [tuple(x) if isinstance(x, list) else x for x in args[0]]
                    if "sort" in kwargs and isinstance(kwargs["sort"], list):
                        kwargs["sort"] = [tuple(x) if isinstance(x, list) else x for x in kwargs["sort"]]
                    if "return_document" in kwargs:
                        kwargs["return_document"] = pymongo.ReturnDocument.AFTER if kwargs["return_document"] else pymongo.ReturnDocument.BEFORE
                    valor = getattr(col, op)(*args, **kwargs)
            else:
                raise ErrorBD(f"Operación de MongoDB no disponible: {op}")
            valor = self._resultado(valor)
        except pymongo.errors.OperationFailure as e:
            raise ErrorBD(f"MongoServerError: {(e.details or {}).get('errmsg') or e}", e.code)
        except pymongo.errors.PyMongoError as e:
            raise ErrorBD(f"MongoError: {e}")
        except (TypeError, ValueError, AttributeError, NotImplementedError) as e:
            raise ErrorBD(f"MongoError: {e}")
        return {"resultado": json.loads(json_util.dumps(valor, json_options=json_util.RELAXED_JSON_OPTIONS))}

    def cerrar(self):
        self.c.close()


# ============================================================================= Redis ====
REDIS_PROHIBIDOS = {"MONITOR", "SUBSCRIBE", "PSUBSCRIBE", "SSUBSCRIBE", "SYNC", "PSYNC", "SHUTDOWN", "DEBUG", "REPLICAOF", "SLAVEOF"}


class _Redis:
    motor = "redis"

    def __init__(self, conectar=None, host="127.0.0.1", puerto=6379, usuario=None, clave="", base=None, **_):
        try:
            import redis
        except ImportError:
            raise _falta("redis")
        self._redis = redis
        try:
            numero = int(base or 0)
        except ValueError:
            raise ErrorBD("En Redis la base es un número (0, 1, 2…).")
        self.c = (conectar or redis.Redis)(host=host, port=puerto, username=usuario or None, password=clave or None, db=numero,
                                            socket_connect_timeout=4, socket_timeout=120)
        try:
            self.version = self.c.info("server").get("redis_version", "")
            try:
                self.c.response_callbacks.clear()  # respuestas tal cual las da Redis (como redis-cli)
            except AttributeError:
                pass
        except redis.AuthenticationError as e:
            raise ErrorBD(f"(error) {e}")
        except redis.ConnectionError:
            raise ErrorBD(_apagado("redis", host, puerto))
        self.base = str(numero)

    @staticmethod
    def _convertir(v):
        if isinstance(v, bytes):
            try:
                return v.decode("utf-8")
            except UnicodeDecodeError:
                return {"$bytes": v.hex()}
        if isinstance(v, (list, tuple, set)):
            return [_Redis._convertir(x) for x in v]
        if isinstance(v, dict):
            return [_Redis._convertir(x) for par in v.items() for x in par]
        if v is True:
            return "OK"
        if isinstance(v, float):
            return str(v)
        return v

    def consultar(self, datos):
        comando = datos.get("comando")
        if not isinstance(comando, list) or not comando or not all(isinstance(x, (str, int, float)) for x in comando):
            raise ErrorBD("(error) Comando vacío.")
        nombre = str(comando[0]).upper()
        if nombre in REDIS_PROHIBIDOS:
            raise ErrorBD(f"(error) {nombre} no está disponible desde CódigoCamp.")
        try:
            valor = self.c.execute_command(*[str(x) for x in comando])
            if nombre == "SELECT" and len(comando) > 1:
                self.base = str(comando[1])
        except self._redis.RedisError as e:
            raise ErrorBD(f"(error) {e}")
        return {"resultado": self._convertir(valor)}

    def cerrar(self):
        self.c.close()


MOTORES = {"mysql": _MySQL, "postgres": _Postgres, "mongodb": _Mongo, "redis": _Redis}


# ========================================================================== sesiones ====
class Sesiones:
    def __init__(self, conectores=None):
        self._conectores = conectores or {}  # motor → función de conexión (para pruebas)
        self._sesiones = {}
        self._lock = threading.Lock()

    def _limpiar(self):
        ahora = time.monotonic()
        with self._lock:
            viejas = [k for k, s in self._sesiones.items() if ahora - s["uso"] > INACTIVIDAD]
            cerrar = [self._sesiones.pop(k) for k in viejas]
        for s in cerrar:
            try:
                s["conexion"].cerrar()
            except Exception:
                pass

    def abrir(self, dueno, motor="mysql", host="127.0.0.1", puerto=None, usuario=None, clave="", base=None, autocommit=True, uri=None):
        motor = ALIAS.get(str(motor or "mysql").lower())
        if not motor:
            raise ErrorBD("Motor desconocido. Usa: mysql, mariadb, postgres, mongodb o redis.")
        self._limpiar()
        with self._lock:
            if sum(1 for s in self._sesiones.values() if s["dueno"] == dueno) >= MAX_SESIONES:
                raise ErrorBD(f"Ya tienes {MAX_SESIONES} conexiones abiertas. Cierra alguna (exit) e inténtalo otra vez.", estado=429)
        try:
            puerto = int(puerto or PUERTOS[motor])
        except (TypeError, ValueError):
            raise ErrorBD("El puerto debe ser un número.")
        if not 1 <= puerto <= 65535:
            raise ErrorBD("El puerto debe estar entre 1 y 65535.")
        conexion = MOTORES[motor](conectar=self._conectores.get(motor), host=host, puerto=puerto, usuario=usuario, clave=clave,
                                  base=base, autocommit=autocommit, uri=uri)
        clave_sesion = secrets.token_urlsafe(18)
        with self._lock:
            self._sesiones[clave_sesion] = {"dueno": dueno, "conexion": conexion, "uso": time.monotonic(), "lock": threading.Lock()}
        return {"sesion": clave_sesion, "motor": motor, "version": conexion.version, "base": conexion.base}

    def _sesion(self, dueno, clave):
        with self._lock:
            s = self._sesiones.get(clave or "")
        if not s or s["dueno"] != dueno:
            raise ErrorBD("La conexión se cerró (o pasó mucho tiempo sin usarla). Vuelve a conectarte.", estado=410)
        return s

    def motor_de(self, dueno, clave):
        try:
            return self._sesion(dueno, clave)["conexion"].motor
        except ErrorBD:
            return None

    def cerrar(self, dueno, clave):
        with self._lock:
            s = self._sesiones.get(clave or "")
            if not s or s["dueno"] != dueno:
                return False
            del self._sesiones[clave]
        try:
            s["conexion"].cerrar()
        except Exception:
            pass
        return True

    def cerrar_de(self, dueno):
        with self._lock:
            claves = [k for k, s in self._sesiones.items() if s["dueno"] == dueno]
        for k in claves:
            self.cerrar(dueno, k)

    def consultar(self, dueno, clave, datos):
        s = self._sesion(dueno, clave)
        with s["lock"]:
            s["uso"] = time.monotonic()
            inicio = time.perf_counter()
            r = s["conexion"].consultar(datos)
            r["segundos"] = round(time.perf_counter() - inicio, 3)
            r["base"] = s["conexion"].base
        return r


def peticion(sesiones, dueno, accion, datos):
    """Despacha una petición de la API (igual para el servidor y el puente). Devuelve (dict, estado)."""
    try:
        if accion == "conectar":
            return sesiones.abrir(dueno, datos.get("motor") or "mysql", datos.get("host") or "127.0.0.1", datos.get("puerto"),
                                  datos.get("usuario") or None, datos.get("clave") or "", datos.get("base") or None,
                                  datos.get("autocommit", True), datos.get("uri") or None), 200
        if accion == "consulta":
            return sesiones.consultar(dueno, datos.get("sesion"), datos), 200
        if accion == "cerrar":
            return {"cerrada": sesiones.cerrar(dueno, datos.get("sesion"))}, 200
        return {"error": "Acción desconocida."}, 404
    except ErrorBD as e:
        return e.como_dict(), e.estado
