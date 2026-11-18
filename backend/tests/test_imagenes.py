import unittest
from datetime import datetime, timedelta, timezone

import utilidades
from app import create_app
from models import WorkspaceImage, db
from rutas import imagenes as modulo

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 40
JPG = b"\xff\xd8\xff\xe0" + b"\x01" * 40
GIF = b"GIF89a" + b"\x02" * 20
WEBP = b"RIFF\x10\x00\x00\x00WEBPVP8 " + b"\x03" * 20


class ImagenesAPITest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        self.app = create_app({
            "TESTING": True, "SECRET_KEY": "test-secret", "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SESSION_COOKIE_SECURE": False, "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "",
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

    def _cuenta(self, email):
        client = self.app.test_client()
        client.get("/api/auth/me/")
        client.csrf = {"X-CSRFToken": client.get_cookie("csrftoken").value}
        r = client.post("/api/auth/register/", json={"nombre": "Ana", "email": email, "password": "Clave123"}, headers=client.csrf)
        self.assertEqual(r.status_code, 201)
        return client

    def _subir(self, datos, client=None):
        client = client or self.client
        return client.post("/api/trabajo/imagenes/", data=datos, headers={**client.csrf, "Content-Type": "application/octet-stream"})

    def test_sube_reconoce_por_firma_y_sirve_solo_al_dueno(self):
        for datos, tipo in ((PNG, "image/png"), (JPG, "image/jpeg"), (GIF, "image/gif"), (WEBP, "image/webp")):
            r = self._subir(datos)
            self.assertEqual(r.status_code, 201, tipo)
            cuerpo = r.get_json()
            self.assertEqual(cuerpo["tipo"], tipo)
            self.assertTrue(cuerpo["marcador"].startswith(f"ccimg:v1:{cuerpo['hash']}:{tipo}:"))
        huella = self._subir(PNG).get_json()["hash"]
        lectura = self.client.get(f"/api/trabajo/imagenes/{huella}")
        self.assertEqual(lectura.status_code, 200)
        self.assertEqual(lectura.data, PNG)
        self.assertEqual(lectura.mimetype, "image/png")
        self.assertIn("sandbox", lectura.headers["Content-Security-Policy"])
        self.assertEqual(lectura.headers["X-Content-Type-Options"], "nosniff")

        otra = self._cuenta("otra@example.com")
        self.assertEqual(otra.get(f"/api/trabajo/imagenes/{huella}").status_code, 404)

    def test_sin_sesion_no_hay_imagenes(self):
        app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False})
        with app.app_context():
            db.create_all()
            anonimo = app.test_client()
            self.assertEqual(anonimo.get("/api/trabajo/imagenes/" + "a" * 64).status_code, 401)
            self.assertEqual(anonimo.get("/api/trabajo/imagenes/").status_code, 401)
            db.drop_all()
            db.session.remove()
            db.engine.dispose()

    def test_rechaza_lo_que_no_es_imagen_svg_y_sin_csrf(self):
        self.assertEqual(self._subir(b"<svg onload=alert(1)></svg>").status_code, 415)
        self.assertEqual(self._subir(b"MZ\x90\x00 ejecutable").status_code, 415)
        self.assertEqual(self._subir(b"").status_code, 400)
        r = self.client.post("/api/trabajo/imagenes/", data=PNG)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.get("/api/trabajo/imagenes/../../etc").status_code, 404)

    def test_limite_por_imagen_y_por_cuenta_sin_duplicar(self):
        grande = PNG + b"\x00" * modulo.MAX_IMAGEN
        self.assertEqual(self._subir(grande).status_code, 413)
        self.assertEqual(self._subir(PNG).status_code, 201)
        self.assertEqual(self._subir(PNG).status_code, 201)
        self.assertEqual(WorkspaceImage.query.count(), 1)  # la misma imagen no ocupa dos veces

        original = modulo.MAX_CUENTA
        modulo.MAX_CUENTA = len(PNG) + len(JPG)
        try:
            self.assertEqual(self._subir(JPG).status_code, 201)
            r = self._subir(GIF)
            self.assertEqual(r.status_code, 413)
            self.assertIn("20 MB", r.get_json()["error"])
            listado = self.client.get("/api/trabajo/imagenes/").get_json()
            self.assertEqual(listado["uso"], len(PNG) + len(JPG))
            self.assertEqual(len(listado["imagenes"]), 2)
        finally:
            modulo.MAX_CUENTA = original

    def test_limite_de_subidas_por_minuto(self):
        codigos = [self._subir(PNG + bytes([i % 256, i // 256])).status_code for i in range(61)]
        self.assertEqual(codigos[:60], [201] * 60)
        self.assertEqual(codigos[60], 429)

    def test_guardar_el_proyecto_borra_las_huerfanas_viejas_pero_no_las_recientes_ni_las_usadas(self):
        usada = self._subir(PNG).get_json()
        vieja = self._subir(JPG).get_json()
        reciente = self._subir(GIF).get_json()
        en_commit = self._subir(WEBP).get_json()
        hace_dos_horas = datetime.now(timezone.utc) - timedelta(hours=2)
        WorkspaceImage.query.filter(WorkspaceImage.hash.in_([usada["hash"], vieja["hash"], en_commit["hash"]])).update(
            {"creado_en": hace_dos_horas}, synchronize_session=False)
        db.session.commit()
        proyecto = {
            "files": {"img/logo.png": usada["marcador"], "index.html": "<img src='img/logo.png'>"},
            "folders": ["img"],
            "git": {"initialized": True, "committed": {"viejo.webp": en_commit["marcador"]}},
        }
        self.assertEqual(self.client.put("/api/trabajo/", json=proyecto, headers=self.client.csrf).status_code, 200)
        quedan = {i.hash for i in WorkspaceImage.query.all()}
        self.assertEqual(quedan, {usada["hash"], reciente["hash"], en_commit["hash"]})

    def test_sin_espacio_libera_huerfanas_antes_de_rechazar(self):
        vieja = self._subir(PNG).get_json()
        WorkspaceImage.query.filter_by(hash=vieja["hash"]).update(
            {"creado_en": datetime.now(timezone.utc) - timedelta(hours=3)}, synchronize_session=False)
        db.session.commit()
        self.client.put("/api/trabajo/", json={"files": {}, "folders": [], "git": {}}, headers=self.client.csrf)
        # La limpieza al guardar ya la quitó; ahora una cuenta con cupo justo para una sola imagen.
        self.assertEqual(WorkspaceImage.query.count(), 0)
        original = modulo.MAX_CUENTA
        modulo.MAX_CUENTA = len(JPG)
        try:
            self.assertEqual(self._subir(JPG).status_code, 201)
        finally:
            modulo.MAX_CUENTA = original

    def test_marcadores_falsos_no_cuentan_como_usados(self):
        texto = "ccimg:v1:" + "a" * 64 + ":image/svg+xml:10"
        self.assertEqual(modulo.hashes_usados({"x": texto, "y": "hola"}, {}), set())
        bueno = "ccimg:v1:" + "b" * 64 + ":image/png:10"
        self.assertEqual(modulo.hashes_usados({"x": bueno}, {"committed": "no-dict"}), {"b" * 64})


if __name__ == "__main__":
    unittest.main()
