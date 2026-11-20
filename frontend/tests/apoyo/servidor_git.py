"""Servidor Git smart-HTTP mínimo para las pruebas (usa `git http-backend`). Uso: python servidor_git.py <carpeta> <puerto>"""
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RAIZ, PUERTO = sys.argv[1], int(sys.argv[2])


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _cgi(self):
        ruta, _, consulta = self.path.partition("?")
        cuerpo = self.rfile.read(int(self.headers.get("Content-Length") or 0)) if self.command == "POST" else b""
        env = {**os.environ, "GIT_PROJECT_ROOT": RAIZ, "GIT_HTTP_EXPORT_ALL": "1", "PATH_INFO": ruta, "QUERY_STRING": consulta,
               "REQUEST_METHOD": self.command, "CONTENT_TYPE": self.headers.get("Content-Type", ""), "CONTENT_LENGTH": str(len(cuerpo)),
               "REMOTE_USER": "prueba", "REMOTE_ADDR": "127.0.0.1", "GIT_PROTOCOL": self.headers.get("Git-Protocol", "")}
        p = subprocess.run(["git", "http-backend"], input=cuerpo, env=env, capture_output=True)
        cab, _, datos = p.stdout.partition(b"\r\n\r\n")
        estado = 200
        cabeceras = []
        for linea in cab.decode().split("\r\n"):
            if not linea:
                continue
            k, _, v = linea.partition(": ")
            if k.lower() == "status":
                estado = int(v.split()[0])
            else:
                cabeceras.append((k, v))
        self.send_response(estado)
        for k, v in cabeceras:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    do_GET = do_POST = _cgi


print("listo", flush=True)
ThreadingHTTPServer(("127.0.0.1", PUERTO), Manejador).serve_forever()
