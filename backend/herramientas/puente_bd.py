"""Puente de CódigoCamp para tus bases de datos locales: MySQL/MariaDB (XAMPP, WAMP, Laragon…), PostgreSQL, MongoDB y Redis.

Úsalo cuando CódigoCamp está en internet y tu MySQL está en tu PC. (Si CódigoCamp corre en tu mismo PC, no hace falta.)

    pip install pymysql pg8000 pymongo redis      (solo los de las bases que uses)
    python puente_bd.py                  # escucha en http://127.0.0.1:8787 y muestra una clave
    python puente_bd.py --puerto 9000 --clave miclave --hosts localhost,192.168.1.0/24

Luego, en la terminal de Trabajo:   bd-puente http://127.0.0.1:8787 <clave>
y ya funcionan  mysql -u root finanbot_db, psql -U postgres, mongosh, redis-cli  y en Python pymysql, psycopg2, pymongo, redis.

Seguridad: solo escucha en tu PC (127.0.0.1), pide la clave en cada petición y por defecto solo conecta a
bases de tu propio PC. Ciérralo (Ctrl+C) cuando termines.
"""
import argparse
import hmac
import json
import os
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from servicios.bd_externa import HOSTS_LOCALES, Sesiones, host_de_uri, host_permitido, peticion  # noqa: E402

MAX_CUERPO = 4 * 1024 * 1024


def crear_servidor(puerto=8787, clave=None, hosts=HOSTS_LOCALES, origenes=("*",), escuchar="127.0.0.1", sesiones=None):
    clave = clave or secrets.token_urlsafe(16)
    sesiones = sesiones or Sesiones()

    class Manejador(BaseHTTPRequestHandler):
        server_version = "PuenteCodigoCamp/1"

        def log_message(self, formato, *args):  # silencioso: no imprimir consultas ni claves
            pass

        def _cors(self):
            origen = self.headers.get("Origin", "")
            if "*" in origenes:
                self.send_header("Access-Control-Allow-Origin", origen or "*")
            elif origen in origenes:
                self.send_header("Access-Control-Allow-Origin", origen)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Max-Age", "600")

        def _json(self, datos, estado=200):
            cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
            self.send_response(estado)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)

        def _autorizado(self):
            dado = self.headers.get("Authorization", "")
            return hmac.compare_digest(dado.encode(), f"Bearer {clave}".encode())

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            if self.path.split("?")[0] != "/api/bd/estado":
                return self._json({"error": "No existe."}, 404)
            if not self._autorizado():
                return self._json({"error": "Clave del puente incorrecta."}, 401)
            return self._json({"activo": True, "hosts": list(hosts), "puente": True})

        def do_POST(self):
            ruta = self.path.split("?")[0]
            if not ruta.startswith("/api/bd/"):
                return self._json({"error": "No existe."}, 404)
            if not self._autorizado():
                return self._json({"error": "Clave del puente incorrecta."}, 401)
            try:
                largo = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                largo = -1
            if largo < 0 or largo > MAX_CUERPO:
                return self._json({"error": "Petición demasiado grande."}, 413)
            try:
                datos = json.loads(self.rfile.read(largo) or b"{}")
            except ValueError:
                return self._json({"error": "JSON inválido."}, 400)
            if not isinstance(datos, dict):
                return self._json({"error": "JSON inválido."}, 400)
            accion = ruta[len("/api/bd/"):]
            if accion == "conectar":
                destinos = host_de_uri(datos["uri"]) if datos.get("uri") else [datos.get("host") or "127.0.0.1"]
                malo = next((h for h in destinos if not host_permitido(h, hosts)), None) if destinos else "(dirección inválida)"
                if malo:
                    return self._json({"error": f"El puente no permite conectar a «{malo}» (usa --hosts)."}, 403)
            respuesta, estado = peticion(sesiones, "puente", accion, datos)
            return self._json(respuesta, estado)

    servidor = ThreadingHTTPServer((escuchar, puerto), Manejador)
    servidor.daemon_threads = True
    servidor.clave = clave
    return servidor


def main(argv=None):
    p = argparse.ArgumentParser(description="Puente de CódigoCamp para tu MySQL/MariaDB local.")
    p.add_argument("--puerto", type=int, default=8787)
    p.add_argument("--clave", default=os.getenv("PUENTE_CLAVE"))
    p.add_argument("--hosts", default=",".join(HOSTS_LOCALES), help="a qué MySQL puede conectar (coma; acepta redes o *)")
    p.add_argument("--origenes", default="*", help="sitios que pueden usarlo (coma), p. ej. https://codigocamp.com")
    a = p.parse_args(argv)
    servidor = crear_servidor(a.puerto, a.clave, [h for h in a.hosts.split(",") if h], [o for o in a.origenes.split(",") if o])
    print("Puente de CódigoCamp listo.")
    print(f"En la terminal de Trabajo escribe:\n\n    bd-puente http://127.0.0.1:{a.puerto} {servidor.clave}\n")
    print("Ctrl+C para cerrarlo.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nPuente cerrado.")


if __name__ == "__main__":
    main()
