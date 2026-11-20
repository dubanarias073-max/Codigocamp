# Internet, correo y Google para el Python de Trabajo (Pyodide, sin sockets).
# Tu código usa las mismas librerías que en tu PC; aquí cada operación se la pide a CódigoCamp (rutas/trabajored.py):
#   · requests, httpx y urllib.request  -> POST /api/trabajo/http   (Gemini, APIs, las llaves de Google…)
#   · smtplib.SMTP / SMTP_SSL           -> POST /api/trabajo/smtp   (tus correos, con tu cuenta del .env)
#   · google.oauth2.id_token            -> acepta el «Iniciar con Google» de la vista previa de Trabajo
# En tu PC no cambia nada: este archivo solo existe dentro de CódigoCamp.
import base64
import io
import json
import sys

LOCALES = ("localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]")


def _aviso(texto):
    print(f"\x1b[36mℹ Trabajo:\x1b[0m {texto}", file=sys.stderr)


def _pedir(accion, datos):
    import _cc_red
    r = json.loads(_cc_red.pedir(accion, json.dumps(datos)))
    if "__error" in r:
        raise _ErrorPuente(r["__error"], r.get("estado", 0))
    return r


class _ErrorPuente(Exception):
    def __init__(self, mensaje, estado=0):
        super().__init__(mensaje)
        self.estado = estado


def _host(url):
    from urllib.parse import urlsplit
    return (urlsplit(url).hostname or "").lower()


def _http(metodo, url, cabeceras, cuerpo, timeout=None, seguir=True):
    """Hace la petición por CódigoCamp. Devuelve (status, motivo, cabeceras[[k,v]], bytes, url_final)."""
    if _host(url) in LOCALES:
        raise ConnectionRefusedError(f"[Errno 111] Connection refused: {url}. En Trabajo tu backend no puede llamarse a sí mismo "
                                     "por localhost; llama a la función directamente o prueba desde la vista previa.")
    if isinstance(cuerpo, str):
        cuerpo = cuerpo.encode()
    elif cuerpo is not None and not isinstance(cuerpo, (bytes, bytearray)):
        cuerpo = b"".join(x if isinstance(x, bytes) else str(x).encode() for x in cuerpo)
    if isinstance(timeout, (tuple, list)):
        timeout = max([t for t in timeout if isinstance(t, (int, float))] or [30])
    if not isinstance(timeout, (int, float)):   # urllib usa un objeto centinela como «sin límite»
        timeout = None
    r = _pedir("http", {"metodo": metodo, "url": url, "cabeceras": [[str(k), str(v)] for k, v in cabeceras],
                        "cuerpo": base64.b64encode(bytes(cuerpo or b"")).decode(), "timeout": timeout or 30, "seguir": seguir})
    if r.get("error") == "timeout":
        raise TimeoutError(r.get("detalle") or "timed out")
    if r.get("error"):
        raise ConnectionError(r.get("detalle") or "No se pudo conectar")
    return r["status"], r.get("motivo", ""), r.get("cabeceras", []), base64.b64decode(r.get("cuerpo") or ""), r.get("url") or url


# ------------------------------------------------------------------------------------------- requests --
def _parchar_requests():
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from requests.structures import CaseInsensitiveDict
        from requests.utils import get_encoding_from_headers
    except Exception:  # noqa: BLE001
        return
    if getattr(HTTPAdapter.send, "_cc", False):
        return

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        try:
            status, motivo, cab, cuerpo, url = _http(request.method, request.url, request.headers.items(), request.body, timeout, seguir=False)
        except TimeoutError as e:
            raise requests.exceptions.Timeout(str(e), request=request) from None
        except (ConnectionError, ConnectionRefusedError, _ErrorPuente) as e:
            raise requests.exceptions.ConnectionError(str(e), request=request) from None
        r = requests.Response()
        r.status_code, r.reason, r.url, r.request, r.connection = status, motivo, url, request, self
        r.headers = CaseInsensitiveDict({k: v for k, v in cab})
        r.encoding = get_encoding_from_headers(r.headers)
        r._content = cuerpo
        r.raw = io.BytesIO(cuerpo)
        return r

    send._cc = True
    HTTPAdapter.send = send


# ---------------------------------------------------------------------------------------------- httpx --
def _parchar_httpx():
    try:
        import httpx
    except Exception:  # noqa: BLE001
        return
    if getattr(httpx.HTTPTransport.handle_request, "_cc", False):
        return

    def _respuesta(request, cuerpo_req, timeout):
        try:
            status, motivo, cab, cuerpo, _ = _http(request.method, str(request.url), request.headers.multi_items(), cuerpo_req, timeout, seguir=False)
        except TimeoutError as e:
            raise httpx.ReadTimeout(str(e), request=request) from None
        except (ConnectionError, ConnectionRefusedError, _ErrorPuente) as e:
            raise httpx.ConnectError(str(e), request=request) from None
        return httpx.Response(status, headers=cab, content=cuerpo, request=request)

    def _espera(request):
        t = (request.extensions or {}).get("timeout") or {}
        return max([v for v in t.values() if v] or [30]) if isinstance(t, dict) else 30

    def handle_request(self, request):
        return _respuesta(request, request.read(), _espera(request))

    async def handle_async_request(self, request):
        return _respuesta(request, await request.aread(), _espera(request))

    handle_request._cc = True
    httpx.HTTPTransport.handle_request = handle_request
    httpx.AsyncHTTPTransport.handle_async_request = handle_async_request


# ------------------------------------------------------------------------------------- urllib.request --
def _parchar_urllib():
    import http.client
    import urllib.request
    import urllib.response
    if getattr(urllib.request, "_cc", False):
        return

    class _Manejador(urllib.request.BaseHandler):
        handler_order = 100

        def _abrir(self, req):
            try:
                status, motivo, cab, cuerpo, url = _http(req.get_method(), req.full_url, req.header_items(), req.data, req.timeout)
            except TimeoutError as e:
                raise urllib.error.URLError(e) from None
            except (ConnectionError, _ErrorPuente) as e:
                raise urllib.error.URLError(str(e)) from None
            crudo = "".join(f"{k}: {v}\r\n" for k, v in cab).encode("latin-1", "replace") + b"\r\n"
            r = urllib.response.addinfourl(io.BytesIO(cuerpo), http.client.parse_headers(io.BytesIO(crudo)), url, status)
            r.msg = motivo
            return r

        http_open = _abrir
        https_open = _abrir

    import urllib.error  # noqa: F401
    urllib.request.install_opener(urllib.request.build_opener(_Manejador))
    urllib.request._cc = True


# -------------------------------------------------------------------------------------------- smtplib --
def _parchar_smtplib():
    import smtplib
    if getattr(smtplib.SMTP, "_cc", False):
        return
    Original = smtplib.SMTP

    class SMTP(Original):
        """smtplib.SMTP de Trabajo: misma API; el correo lo envía CódigoCamp con tu cuenta."""
        _cc = True
        _modo_ssl = False

        def __init__(self, host="", port=0, local_hostname=None, timeout=None, source_address=None, **kw):
            self.host, self.port = host, port
            self._tls, self._usuario, self._clave = False, None, None
            self.local_hostname = local_hostname or "codigocamp"
            self.timeout, self.source_address, self.debuglevel = timeout, source_address, 0
            self.ehlo_resp = self.helo_resp = None
            self.esmtp_features, self.does_esmtp, self.command_encoding = {}, True, "ascii"
            self.sock = None
            if host:
                self.connect(host, port)

        def connect(self, host="localhost", port=0, source_address=None):
            if not port and ":" in host:
                host, port = host.rsplit(":", 1)
            self.host, self.port = host, int(port or (465 if self._modo_ssl else 25))
            if self.host.lower() in LOCALES:
                raise ConnectionRefusedError(111, f"Connection refused: {self.host}:{self.port} (en Trabajo no hay servidor de correo local; usa el de Gmail u otro proveedor)")
            return 220, b"CodigoCamp ESMTP"

        def ehlo(self, name=""):
            self.ehlo_resp = b"codigocamp"
            self.esmtp_features = {"size": "10485760", "8bitmime": "", "auth": " LOGIN PLAIN", "starttls": "", "smtputf8": ""}
            return 250, self.ehlo_resp

        def helo(self, name=""):
            self.helo_resp = b"codigocamp"
            return 250, self.helo_resp

        def starttls(self, *a, **k):
            self._tls = True
            return 220, b"Ready to start TLS"

        def login(self, user, password, *, initial_response_ok=True):
            self._usuario, self._clave = user, password
            return 235, b"Accepted (se comprueba al enviar)"

        def sendmail(self, from_addr, to_addrs, msg, mail_options=(), rcpt_options=()):
            if isinstance(to_addrs, str):
                to_addrs = [to_addrs]
            if isinstance(msg, str):
                msg = smtplib._fix_eols(msg).encode("utf-8")
            modo = "ssl" if self._modo_ssl else "starttls" if self._tls else "plano"
            try:
                r = _pedir("smtp", {"host": self.host, "puerto": self.port, "modo": modo, "usuario": self._usuario or "", "clave": self._clave or "",
                                    "de": from_addr, "para": list(to_addrs), "mensaje": base64.b64encode(bytes(msg)).decode()})
            except _ErrorPuente as e:
                raise smtplib.SMTPException(str(e)) from None
            if r.get("error") == "auth":
                raise smtplib.SMTPAuthenticationError(r.get("codigo") or 535, (r.get("detalle") or "Usuario o contraseña incorrectos").encode())
            if r.get("error") == "destinatarios":
                raise smtplib.SMTPRecipientsRefused({a: (550, b"rechazado") for a in to_addrs})
            if r.get("error"):
                raise smtplib.SMTPException(r.get("detalle") or "No se pudo enviar el correo")
            _aviso(f"correo enviado a {', '.join(to_addrs)} por {self.host} (con {self._usuario}).")
            return {k: (v[0], str(v[1]).encode()) for k, v in (r.get("rechazados") or {}).items()}

        def docmd(self, cmd, args=""):
            return (221, b"Bye") if str(cmd).upper() == "QUIT" else (250, b"OK")

        def noop(self):
            return 250, b"OK"

        def rset(self):
            return 250, b"OK"

        def quit(self):
            return 221, b"Bye"

        def close(self):
            self.sock = None

    class SMTP_SSL(SMTP):
        _modo_ssl = True

        def __init__(self, host="", port=0, local_hostname=None, keyfile=None, certfile=None, timeout=None, source_address=None, context=None, **kw):
            super().__init__(host, port, local_hostname, timeout, source_address)

    smtplib.SMTP, smtplib.SMTP_SSL = SMTP, SMTP_SSL


# ------------------------------------------------------------------- «Iniciar con Google» (google-auth) --
def _parchar_google():
    try:
        from google.oauth2 import id_token as idt
    except Exception:  # noqa: BLE001
        return
    if getattr(idt.verify_token, "_cc", False):
        return
    original_token, original_oauth2 = idt.verify_token, idt.verify_oauth2_token

    def _de_trabajo(token):
        try:
            cabeza = token.split(".")[0] if isinstance(token, str) else token.decode().split(".")[0]
            return json.loads(base64.urlsafe_b64decode(cabeza + "=" * (-len(cabeza) % 4))).get("kid") == "codigocamp-trabajo"
        except Exception:  # noqa: BLE001
            return False

    def _verificar(token, audience):
        aud = audience if isinstance(audience, str) else (audience[0] if isinstance(audience, (list, tuple)) and audience else None)
        try:
            return _pedir("google-token/verificar", {"token": token if isinstance(token, str) else token.decode(), "aud": aud})["reclamos"]
        except _ErrorPuente as e:
            raise ValueError(str(e)) from None

    def verify_token(id_token, request=None, audience=None, *a, **k):
        return _verificar(id_token, audience) if _de_trabajo(id_token) else original_token(id_token, request, audience, *a, **k)

    def verify_oauth2_token(id_token, request=None, audience=None, *a, **k):
        return _verificar(id_token, audience) if _de_trabajo(id_token) else original_oauth2(id_token, request, audience, *a, **k)

    verify_token._cc = True
    idt.verify_token, idt.verify_oauth2_token = verify_token, verify_oauth2_token


# ------------------------------------------------------------------------------------------ activar --
_GANCHOS = {"requests": _parchar_requests, "httpx": _parchar_httpx, "google.oauth2.id_token": _parchar_google}


def activar():
    """Se llama antes de importar tu app o de ejecutar tu archivo."""
    _parchar_urllib()
    _parchar_smtplib()
    for parche in _GANCHOS.values():
        parche()
    import importlib.abc
    import importlib.machinery

    class _GanchoRed(importlib.abc.MetaPathFinder):
        def find_spec(self, nombre, ruta=None, objetivo=None):
            parche = _GANCHOS.get(nombre)
            if parche is None or nombre in sys.modules:
                return None
            spec = importlib.machinery.PathFinder.find_spec(nombre, ruta)
            if spec and spec.loader and hasattr(spec.loader, "exec_module"):
                cargar = spec.loader.exec_module

                def exec_module(modulo, _cargar=cargar, _parche=parche):
                    _cargar(modulo)
                    _parche()

                spec.loader.exec_module = exec_module
            return spec

    sys.meta_path[:] = [g for g in sys.meta_path if type(g).__name__ != "_GanchoRed"]
    sys.meta_path.insert(0, _GanchoRed())
