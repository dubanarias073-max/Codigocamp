# Servidor de desarrollo de CódigoCamp para FastAPI / Starlette (ASGI) y Flask / Django (WSGI) dentro de Pyodide.
# Hace lo mismo que uvicorn y «flask run», pero las peticiones llegan desde la vista previa del navegador
# (no hay sockets): JavaScript llama a _cc_srv.pedir(...) y recibe la respuesta en JSON.
import asyncio
import base64
import importlib
import inspect
import io
import json
import os
import sys
import traceback


def _cc_sin_hilos():
    """En el navegador no hay hilos: lo que FastAPI/Starlette mandan al «threadpool» se ejecuta directamente."""
    try:
        import anyio.to_thread as _t

        async def _directo(func, *args, **kwargs):
            return func(*args)

        _t.run_sync = _directo
    except Exception:  # anyio no instalado: es una app WSGI
        pass


class _CCServidor:
    def __init__(self, raiz, spec, factory=False):
        self.raiz = os.path.abspath(raiz)
        self.spec = spec
        self.factory = factory
        self.app = None
        self.wsgi = False
        self.estado = {}
        self._lifespan = None

    # ------------------------------------------------------------------ carga / recarga --
    def _olvidar_modulos(self):
        django = self.spec.startswith("django:")
        for nombre, m in list(sys.modules.items()):
            archivo = getattr(m, "__file__", None) or ""
            # Django no se puede «configurar» dos veces: al recargar se vuelve a importar entero.
            if (archivo and os.path.abspath(archivo).startswith(self.raiz + os.sep)) or (django and nombre.split(".")[0] == "django"):
                del sys.modules[nombre]
        importlib.invalidate_caches()

    @staticmethod
    def _buscar_app(modulo):
        for nombre in ("app", "application", "api", "server"):
            if hasattr(modulo, nombre):
                return getattr(modulo, nombre), nombre
        for nombre, valor in vars(modulo).items():
            tipo = type(valor).__name__
            if tipo in ("FastAPI", "Starlette", "Flask", "Quart", "Litestar", "WSGIHandler", "ASGIHandler"):
                return valor, nombre
        for nombre in ("create_app", "make_app"):
            if callable(getattr(modulo, nombre, None)):
                return getattr(modulo, nombre)(), nombre + "()"
        raise RuntimeError("no encontré la app: crea una variable «app» (app = FastAPI() o app = Flask(__name__)) o indica modulo:variable")

    async def cargar(self):
        await self.cerrar()
        self._olvidar_modulos()
        _cc_sin_hilos()
        if "preparar_bd" in globals():
            preparar_bd(self.raiz)   # MySQL/PostgreSQL/MongoDB -> bases que funcionan en el navegador (bd_py.py)
        if self.spec.startswith("django:"):
            return self._cargar_django(self.spec.split(":", 1)[1])
        modulo, _, atributo = self.spec.partition(":")
        m = importlib.import_module(modulo)
        if atributo:
            valor = m
            for parte in atributo.replace("()", "").split("."):
                if not hasattr(valor, parte):
                    raise RuntimeError(f'Attribute "{atributo}" not found in module "{modulo}".')
                valor = getattr(valor, parte)
            app = valor() if (self.factory or atributo.endswith("()")) else valor
            nombre = atributo
        else:
            app, nombre = self._buscar_app(m)
        self.wsgi = hasattr(app, "wsgi_app") or type(app).__name__ == "WSGIHandler" or not self._es_asgi(app)
        self.app = app
        if not self.wsgi:
            await self._arrancar()
        return json.dumps({"modulo": modulo, "variable": nombre, "tipo": "WSGI" if self.wsgi else "ASGI", "clase": type(app).__name__})

    def _cargar_django(self, ajustes):
        """python manage.py runserver: la app WSGI de Django y, con DEBUG, también sus archivos estáticos (el admin con estilos)."""
        os.environ["DJANGO_SETTINGS_MODULE"] = ajustes
        import django
        from django.conf import settings
        from django.core.wsgi import get_wsgi_application
        app = get_wsgi_application()
        if settings.DEBUG and "django.contrib.staticfiles" in settings.INSTALLED_APPS:
            from django.contrib.staticfiles.handlers import StaticFilesHandler
            app = StaticFilesHandler(app)
        try:
            from django.core.management import call_command
            from io import StringIO
            salida = StringIO()
            call_command("check", stdout=salida, stderr=salida)
        except Exception as e:  # noqa: BLE001 - check muestra el problema, como runserver
            print(str(e), file=sys.stderr)
        self.app, self.wsgi = app, True
        sin_migrar = ""
        try:
            from django.db import connection
            from django.db.migrations.executor import MigrationExecutor
            pendientes = MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
            if pendientes:
                sin_migrar = str(len(pendientes))
        except Exception:  # noqa: BLE001
            pass
        return json.dumps({"modulo": ajustes, "variable": "application", "tipo": "WSGI", "clase": "Django", "version": django.get_version(), "sin_migrar": sin_migrar})

    @staticmethod
    def _es_asgi(app):
        llamar = app if inspect.isfunction(app) or inspect.ismethod(app) else getattr(app, "__call__", None)
        if llamar is None:
            return False
        if inspect.iscoroutinefunction(llamar):
            return True
        try:
            return len(inspect.signature(llamar).parameters) == 3
        except (TypeError, ValueError):
            return True

    # ------------------------------------------------------------------ lifespan (ASGI) --
    async def _arrancar(self):
        rx, tx = asyncio.Queue(), asyncio.Queue()
        scope = {"type": "lifespan", "asgi": {"version": "3.0", "spec_version": "2.0"}, "state": {}}
        self.estado = scope["state"]

        async def correr():
            try:
                await self.app(scope, rx.get, tx.put)
            except BaseException as e:  # noqa: BLE001 - la app no maneja lifespan
                await tx.put({"type": "_sin_lifespan", "error": repr(e)})

        self._lifespan = (asyncio.ensure_future(correr()), rx, tx)
        await rx.put({"type": "lifespan.startup"})
        m = await tx.get()
        if m["type"] == "lifespan.startup.failed":
            raise RuntimeError(m.get("message") or "Application startup failed. Exiting.")
        if m["type"] == "_sin_lifespan":
            self._lifespan = None

    async def cerrar(self):
        if self._lifespan:
            tarea, rx, tx = self._lifespan
            self._lifespan = None
            await rx.put({"type": "lifespan.shutdown"})
            try:
                await asyncio.wait_for(tx.get(), 10)
            except Exception:  # noqa: BLE001
                pass
            tarea.cancel()
        if "guardar_mongo" in globals():
            guardar_mongo()

    # ------------------------------------------------------------------------ peticiones --
    async def pedir(self, metodo, ruta, consulta, cabeceras_json, cuerpo_b64):
        cabeceras = json.loads(cabeceras_json)
        cuerpo = base64.b64decode(cuerpo_b64) if cuerpo_b64 else b""
        try:
            if self.wsgi:
                r = self._pedir_wsgi(metodo, ruta, consulta, cabeceras, cuerpo)
            else:
                r = await self._pedir_asgi(metodo, ruta, consulta, cabeceras, cuerpo)
        except BaseException:  # noqa: BLE001
            texto = traceback.format_exc()
            print("ERROR:    Exception in ASGI application\n" + texto, file=sys.stderr)
            r = (500, [["content-type", "text/plain; charset=utf-8"]], b"Internal Server Error")
        estado, cab, datos = r
        if metodo.upper() != "GET" and "guardar_mongo" in globals():
            guardar_mongo()
        return json.dumps({"status": estado, "headers": cab, "body": base64.b64encode(datos).decode()})

    async def _pedir_asgi(self, metodo, ruta, consulta, cabeceras, cuerpo):
        scope = {
            "type": "http", "asgi": {"version": "3.0", "spec_version": "2.3"}, "http_version": "1.1",
            "method": metodo.upper(), "scheme": "http", "path": ruta, "raw_path": ruta.encode(),
            "query_string": consulta.encode(), "root_path": "",
            "headers": [(k.lower().encode("latin-1"), str(v).encode("latin-1")) for k, v in cabeceras],
            "client": ("127.0.0.1", 52000), "server": ("127.0.0.1", 8000), "state": dict(self.estado),
        }
        enviado = False

        async def receive():
            nonlocal enviado
            if not enviado:
                enviado = True
                return {"type": "http.request", "body": cuerpo, "more_body": False}
            await asyncio.sleep(3600)
            return {"type": "http.disconnect"}

        salida = {"status": 500, "headers": [], "body": bytearray()}

        async def send(m):
            if m["type"] == "http.response.start":
                salida["status"] = m["status"]
                salida["headers"] = [[k.decode("latin-1"), v.decode("latin-1")] for k, v in m.get("headers", [])]
            elif m["type"] == "http.response.body":
                salida["body"] += m.get("body", b"")

        await self.app(scope, receive, send)
        return salida["status"], salida["headers"], bytes(salida["body"])

    def _pedir_wsgi(self, metodo, ruta, consulta, cabeceras, cuerpo):
        environ = {
            "REQUEST_METHOD": metodo.upper(), "SCRIPT_NAME": "", "PATH_INFO": ruta, "QUERY_STRING": consulta,
            "SERVER_NAME": "127.0.0.1", "SERVER_PORT": "5000", "SERVER_PROTOCOL": "HTTP/1.1", "REMOTE_ADDR": "127.0.0.1",
            "wsgi.version": (1, 0), "wsgi.url_scheme": "http", "wsgi.input": io.BytesIO(cuerpo), "wsgi.errors": sys.stderr,
            "wsgi.multithread": False, "wsgi.multiprocess": False, "wsgi.run_once": False, "CONTENT_LENGTH": str(len(cuerpo)),
        }
        for k, v in cabeceras:
            clave = k.upper().replace("-", "_")
            if clave == "CONTENT_TYPE":
                environ["CONTENT_TYPE"] = v
            elif clave != "CONTENT_LENGTH":
                environ["HTTP_" + clave] = v
        estado = {}

        def start_response(status, headers, exc_info=None):
            estado["status"] = int(status.split(" ", 1)[0])
            estado["headers"] = [[k, v] for k, v in headers]

        resultado = self.app(environ, start_response)
        try:
            datos = b"".join(resultado)
        finally:
            if hasattr(resultado, "close"):
                resultado.close()
        return estado.get("status", 500), estado.get("headers", []), datos
