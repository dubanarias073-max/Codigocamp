import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import utilidades
from app import create_app
from models import WorkspaceFile, db
from rutas import archivos as modulo

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 40
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x05" * 100
PDF = b"%PDF-1.7\n" + b"\x06" * 50
EXE = b"MZ\x90\x00" + b"\x07" * 30
SVG = b"<svg onload=alert(1)></svg>"


class ArchivosAPITest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.dir = tempfile.mkdtemp()
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "test-secret", "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_COOKIE_SECURE": False, "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "",
            "ALMACEN_ARCHIVOS": self.dir, "CUOTA_ARCHIVOS": 10_000, "MAX_ARCHIVO": 4_000,
        })
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.client = self._cuenta("ana@example.com")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()
        utilidades._RATE_LIMITS.clear()
        shutil.rmtree(self.dir, ignore_errors=True)

    def _cuenta(self, email):
        client = self.app.test_client()
        client.get("/api/auth/me/")
        client.csrf = {"X-CSRFToken": client.get_cookie("csrftoken").value}
        r = client.post("/api/auth/register/", json={"nombre": "Ana", "email": email, "password": "Clave123"}, headers=client.csrf)
        self.assertEqual(r.status_code, 201)
        return client

    def _subir(self, datos, nombre="", client=None):
        client = client or self.client
        return client.post(f"/api/trabajo/archivos/?nombre={nombre}", data=datos, headers={**client.csrf, "Content-Type": "application/octet-stream"})

    def test_cualquier_tipo_se_guarda_en_disco_y_solo_lo_inofensivo_se_muestra(self):
        casos = [(PNG, "a.png", "image/png", True), (MP4, "v.mp4", "video/mp4", True), (PDF, "d.pdf", "application/pdf", True),
                 (b"\x00\x01binario", "x.bin", "application/octet-stream", False), (SVG, "s.svg", "application/octet-stream", False),
                 (b"col1,col2\n1,2\n", "datos.csv", "text/csv", True)]
        for datos, nombre, tipo, en_navegador in casos:
            r = self._subir(datos, nombre)
            self.assertEqual(r.status_code, 201, nombre)
            j = r.get_json()
            self.assertEqual(j["tipo"], tipo, nombre)
            self.assertEqual(j["marcador"], f"ccbin:v1:{j['hash']}:{tipo}:{len(datos)}")
            ruta = Path(self.dir) / "1" / j["hash"][:2] / j["hash"]
            self.assertEqual(ruta.read_bytes(), datos, "los bytes están en disco")
            lectura = self.client.get(f"/api/trabajo/archivos/{j['hash']}")
            self.assertEqual(lectura.status_code, 200)
            self.assertEqual(lectura.data, datos)
            self.assertEqual(lectura.headers["X-Content-Type-Options"], "nosniff")
            if en_navegador:
                self.assertNotIn("attachment", lectura.headers.get("Content-Disposition", ""), nombre)

            else:
                self.assertEqual(lectura.mimetype, "application/octet-stream", nombre)
                self.assertIn("attachment", lectura.headers["Content-Disposition"], nombre)
            lectura.close()
        self.assertEqual(WorkspaceFile.query.count(), len(casos))

    def test_el_antivirus_bloquea_programas_y_no_los_guarda(self):
        for datos, nombre in [(EXE, "x.exe"), (EXE, "tarea.pdf"), (b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$" + b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*", "nota.txt")]:
            r = self._subir(datos, nombre)
            self.assertEqual(r.status_code, 422, nombre)
            self.assertIn("🛡️", r.get_json()["error"])
        self.assertEqual(WorkspaceFile.query.count(), 0)
        self.assertEqual([p for p in Path(self.dir).rglob("*") if p.is_file()], [])

    def test_rango_para_videos_y_descarga_forzada(self):
        huella = self._subir(MP4, "v.mp4").get_json()["hash"]
        parcial = self.client.get(f"/api/trabajo/archivos/{huella}", headers={"Range": "bytes=0-9"})
        self.assertEqual(parcial.status_code, 206)
        self.assertEqual(parcial.data, MP4[:10])
        parcial.close()
        d = self.client.get(f"/api/trabajo/archivos/{huella}?descargar=1&nombre=mi video.mp4")
        self.assertIn("attachment", d.headers["Content-Disposition"])
        self.assertIn("mi_video.mp4", d.headers["Content-Disposition"])
        d.close()

    def test_privado_por_cuenta_y_enlaces_firmados(self):
        huella = self._subir(PNG, "a.png").get_json()["hash"]
        enlaces = self.client.post("/api/trabajo/archivos/enlaces/", json={"hashes": [huella, "z" * 64]}, headers=self.client.csrf).get_json()["enlaces"]
        self.assertEqual(list(enlaces), [huella])
        ruta = enlaces[huella].replace("http://localhost", "")
        anonimo = self.app.test_client()
        r = anonimo.get(ruta)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, PNG)
        r.close()
        self.assertEqual(anonimo.get(ruta[:-3] + "xyz").status_code, 404, "firma alterada")
        otra = self._cuenta("otra@example.com")
        self.assertEqual(otra.get(f"/api/trabajo/archivos/{huella}").status_code, 404)
        enlaces = otra.post("/api/trabajo/archivos/enlaces/", json={"hashes": [huella]}, headers=otra.csrf).get_json()["enlaces"]
        self.assertEqual(enlaces, {}, "no hay enlaces para archivos ajenos")

    def test_limites_por_archivo_por_cuenta_y_sin_duplicar(self):
        self.assertEqual(self._subir(b"\x01" * 4_001).status_code, 413)
        self.assertEqual(self._subir(b"").status_code, 400)
        self.assertEqual(self._subir(PNG).status_code, 201)
        self.assertEqual(self._subir(PNG).status_code, 201)
        self.assertEqual(WorkspaceFile.query.count(), 1, "el mismo archivo no ocupa dos veces")
        for i in range(2):
            self.assertEqual(self._subir(bytes([i + 10]) * 4_000).status_code, 201)
        r = self._subir(b"\x09" * 3_000)
        self.assertEqual(r.status_code, 413)
        self.assertIn("No queda espacio", r.get_json()["error"])
        listado = self.client.get("/api/trabajo/archivos/").get_json()
        self.assertEqual(listado["uso"], len(PNG) + 8_000)
        self.assertEqual(listado["limite"], 10_000)
        self.assertEqual(listado["max_archivo"], 4_000)
        self.assertEqual(sorted(p.name for p in Path(self.dir).rglob(".subida-*")), [], "no quedan temporales")

    def test_sin_csrf_y_sin_sesion(self):
        self.assertEqual(self.client.post("/api/trabajo/archivos/", data=PNG).status_code, 403)
        self.assertEqual(self.client.get("/api/trabajo/archivos/../../etc").status_code, 404)

    def test_sin_sesion(self):
        app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False, "ALMACEN_ARCHIVOS": self.dir})
        with app.app_context():
            db.create_all()
            anonimo = app.test_client()
            self.assertEqual(anonimo.get("/api/trabajo/archivos/" + "a" * 64).status_code, 401)
            self.assertEqual(anonimo.get("/api/trabajo/archivos/").status_code, 401)
            db.drop_all()
            db.session.remove()
            db.engine.dispose()

    def test_guardar_borra_huerfanos_viejos_de_la_base_y_del_disco(self):
        usado = self._subir(PNG, "a.png").get_json()
        viejo = self._subir(MP4, "v.mp4").get_json()
        reciente = self._subir(PDF, "d.pdf").get_json()
        en_commit = self._subir(b"\x00\x01binario", "x.bin").get_json()
        antiguo = self._subir(b"ccimg-legado", "l.bin").get_json()
        hace = datetime.now(timezone.utc) - timedelta(hours=2)
        WorkspaceFile.query.filter(WorkspaceFile.hash != reciente["hash"]).update({"creado_en": hace}, synchronize_session=False)
        db.session.commit()
        legado = f"ccimg:v1:{antiguo['hash']}:image/png:12"  # marcadores de la versión anterior siguen valiendo
        proyecto = {"files": {"img/a.png": usado["marcador"], "b.png": legado}, "folders": ["img"],
                    "git": {"initialized": True, "committed": {"x.bin": en_commit["marcador"]}}}
        self.assertEqual(self.client.put("/api/trabajo/", json=proyecto, headers=self.client.csrf).status_code, 200)
        quedan = {i.hash for i in WorkspaceFile.query.all()}
        self.assertEqual(quedan, {usado["hash"], reciente["hash"], en_commit["hash"], antiguo["hash"]})
        self.assertFalse((Path(self.dir) / "1" / viejo["hash"][:2] / viejo["hash"]).exists())

    def test_limpiar_disco_quita_lo_que_no_esta_en_la_base(self):
        usado = self._subir(PNG).get_json()["hash"]
        suelto = Path(self.dir) / "1" / "ab" / ("ab" + "c" * 62)
        suelto.parent.mkdir(parents=True, exist_ok=True)
        suelto.write_bytes(b"x")
        self.assertEqual(modulo.limpiar_disco(self.app), 1)
        self.assertTrue((Path(self.dir) / "1" / usado[:2] / usado).exists())

    def test_tipo_de(self):
        self.assertEqual(modulo.tipo_de(b"RIFF\x00\x00\x00\x00WAVEfmt", "x"), "audio/wav")
        self.assertEqual(modulo.tipo_de(b"ID3\x04", "c.mp3"), "audio/mpeg")
        self.assertEqual(modulo.tipo_de(b"\x00\x00\x00\x18ftypM4A ", "c.m4a"), "audio/mp4")
        self.assertEqual(modulo.tipo_de(b"\x1a\x45\xdf\xa3", "v.webm"), "video/webm")
        self.assertEqual(modulo.tipo_de(b"wOF2", "f"), "font/woff2")
        self.assertEqual(modulo.tipo_de(b"\x00\x01", "fuente.ttf"), "font/ttf")
        self.assertEqual(modulo.tipo_de(b"<html>", "pagina.html"), "application/octet-stream")


if __name__ == "__main__":
    unittest.main()
