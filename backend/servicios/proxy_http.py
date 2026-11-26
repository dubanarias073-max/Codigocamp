"""Cliente HTTP de Trabajo (tipo Postman / Thunder Client): hace la petición a una API PÚBLICA de internet desde el
servidor de CódigoCamp, sin las restricciones CORS del navegador.

Seguridad (para que nadie lo use para atacar el servidor o la red interna, «SSRF»):
- Solo http:// y https://, sin usuario:clave en la URL.
- El nombre se resuelve UNA vez y se rechaza si alguna dirección es privada, local, de la nube (169.254.x),
  reservada o multicast (IPv4 e IPv6). La conexión se hace a esa misma IP (no se puede cambiar el DNS a mitad de
  camino: «DNS rebinding»), con el nombre real para el certificado TLS.
- Las redirecciones se siguen a mano (máx. 5) y cada salto se vuelve a revisar.
- Límites: 2 MB de cuerpo enviado, 10 MB de respuesta, 25 s de espera. Las cabeceras de salto no se reenvían y
  nunca viajan las cookies ni la sesión de CódigoCamp.
"""
import http.client
import ipaddress
import socket
import ssl
import time
from urllib.parse import urljoin, urlsplit

METODOS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
MAX_CUERPO = 2 * 1024 * 1024
MAX_RESPUESTA = 10 * 1024 * 1024
ESPERA = 25
MAX_SALTOS = 5
# Cabeceras que no se reenvían (de salto o que el servidor pone solo)
QUITAR = {"host", "connection", "keep-alive", "proxy-authorization", "proxy-connection", "te", "trailer", "transfer-encoding", "upgrade",
          "content-length"}


class ErrorProxy(Exception):
    pass


def _ip_permitida(ip):
    try:
        d = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if d.version == 6 and d.ipv4_mapped:
        d = d.ipv4_mapped
    return not (d.is_private or d.is_loopback or d.is_link_local or d.is_multicast or d.is_reserved or d.is_unspecified
                or (d.version == 4 and d in ipaddress.ip_network("100.64.0.0/10"))   # red compartida de proveedores (CGNAT)
                or (d.version == 6 and d in ipaddress.ip_network("64:ff9b::/96")))   # NAT64 (podría apuntar a una IP privada)


def resolver(nombre, puerto):
    """Devuelve la IP a la que se va a conectar (la primera permitida) o lanza ErrorProxy."""
    try:
        infos = socket.getaddrinfo(nombre, puerto, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise ErrorProxy(f"No se encontró el sitio «{nombre}» (revisa la dirección).")
    ips = [i[4][0] for i in infos]
    if not ips:
        raise ErrorProxy(f"No se encontró el sitio «{nombre}».")
    malas = [ip for ip in ips if not _ip_permitida(ip)]
    if malas:
        raise ErrorProxy(f"«{nombre}» apunta a una dirección interna ({malas[0]}). Las peticiones a tu propio equipo o a tu red "
                         "se hacen con tu servidor de Trabajo encendido o con el Conector.")
    return ips[0]


class _HTTPS(http.client.HTTPSConnection):
    """Conecta a la IP ya revisada pero valida el certificado con el nombre real del sitio."""

    def __init__(self, ip, nombre, puerto, contexto):
        super().__init__(nombre, puerto, timeout=ESPERA, context=contexto)
        self._ip, self._nombre, self._ctx = ip, nombre, contexto

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), ESPERA)
        self.sock = self._ctx.wrap_socket(sock, server_hostname=self._nombre)


class _HTTP(http.client.HTTPConnection):
    def __init__(self, ip, nombre, puerto):
        super().__init__(nombre, puerto, timeout=ESPERA)
        self._ip = ip

    def connect(self):
        self.sock = socket.create_connection((self._ip, self.port), ESPERA)


def _validar_url(url):
    partes = urlsplit(url)
    if partes.scheme not in ("http", "https"):
        raise ErrorProxy("La dirección debe empezar con http:// o https://")
    if not partes.hostname:
        raise ErrorProxy("Falta el sitio en la dirección.")
    if partes.username or partes.password:
        raise ErrorProxy("No pongas usuario y contraseña dentro de la dirección: usa la pestaña «Autorización».")
    return partes


def pedir(metodo, url, cabeceras=(), cuerpo=b"", verificar_tls=True, revisar=None):
    """revisar(url) -> mensaje o None: filtro extra (enlaces peligrosos) que se aplica también a cada redirección."""
    """Hace la petición y devuelve {status, razon, cabeceras: [[k, v]], cuerpo: bytes, ms, url, truncado}."""
    metodo = str(metodo or "GET").upper()
    if metodo not in METODOS:
        raise ErrorProxy("Método no válido.")
    cuerpo = cuerpo or b""
    if len(cuerpo) > MAX_CUERPO:
        raise ErrorProxy("El cuerpo de la petición pasa de 2 MB.")
    limpias = [(str(k).strip()[:200], str(v)[:8000]) for k, v in cabeceras if str(k).strip() and str(k).strip().lower() not in QUITAR
               and "\n" not in str(k) + str(v) and "\r" not in str(k) + str(v)][:100]
    inicio = time.monotonic()
    actual, met, datos = url, metodo, cuerpo
    for _ in range(MAX_SALTOS + 1):
        partes = _validar_url(actual)
        if revisar and (motivo := revisar(actual)):
            raise ErrorProxy(motivo)
        puerto = partes.port or (443 if partes.scheme == "https" else 80)
        ip = resolver(partes.hostname, puerto)
        if partes.scheme == "https":
            ctx = ssl.create_default_context()
            if not verificar_tls:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            con = _HTTPS(ip, partes.hostname, puerto, ctx)
        else:
            con = _HTTP(ip, partes.hostname, puerto)
        ruta = (partes.path or "/") + (f"?{partes.query}" if partes.query else "")
        try:
            con.putrequest(met, ruta, skip_accept_encoding=True)
            nombres = {k.lower() for k, _ in limpias}
            if "user-agent" not in nombres:
                con.putheader("User-Agent", "CodigoCamp-Trabajo/1.0")
            if "accept" not in nombres:
                con.putheader("Accept", "*/*")
            for k, v in limpias:
                con.putheader(k, v)
            if datos or met in ("POST", "PUT", "PATCH"):
                con.putheader("Content-Length", str(len(datos)))
            con.endheaders(datos or None)
            r = con.getresponse()
            leido = r.read(MAX_RESPUESTA + 1)
        except ssl.SSLError as e:
            raise ErrorProxy(f"Falló la conexión segura (TLS): {e.reason or e}. Si es tu servidor de pruebas, desactiva «Verificar certificado».")
        except (socket.timeout, TimeoutError):
            raise ErrorProxy(f"El sitio no respondió en {ESPERA} segundos.")
        except (ConnectionError, OSError, http.client.HTTPException) as e:
            raise ErrorProxy(f"No se pudo conectar con {partes.hostname}: {e}")
        finally:
            con.close()
        destino = r.getheader("Location")
        if r.status in (301, 302, 303, 307, 308) and destino:
            actual = urljoin(actual, destino)
            if r.status == 303 or (r.status in (301, 302) and met == "POST"):
                met, datos = "GET", b""
            continue
        return {"status": r.status, "razon": r.reason, "cabeceras": [[k, v] for k, v in r.getheaders()][:200],
                "cuerpo": leido[:MAX_RESPUESTA], "truncado": len(leido) > MAX_RESPUESTA, "ms": round((time.monotonic() - inicio) * 1000), "url": actual}
    raise ErrorProxy("Demasiadas redirecciones.")
