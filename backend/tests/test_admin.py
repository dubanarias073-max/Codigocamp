"""Panel de administrador: solo ADMIN_EMAIL con ADMIN_CLAVE; incidentes con gravedad, correo de advertencia y bloqueo manual."""
import os
import unittest

from flask import g

import utilidades
from app import create_app
from models import Incidente, User, db
from servicios.antivirus import EICAR

ADMIN = "dubanarias073@gmail.com"


class AdminTest(unittest.TestCase):
    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        os.environ["ADMIN_CLAVE"] = "ClaveAdmin-123"
        os.environ.pop("ADMIN_EMAIL", None)
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        import servicios.tienda as t
        t._ITEMS_LISTOS = False

    def tearDown(self):
        import servicios.tienda as t
        t._ITEMS_LISTOS = False   # cada prueba usa una base nueva
        os.environ.pop("ADMIN_CLAVE", None)
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def cliente(self, email, nombre="Ana", registrar=True):
        c = self.app.test_client()
        c.get("/api/auth/me/")
        c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        if registrar:
            r = c.post("/api/auth/register/", json={"nombre": nombre, "email": email, "password": "Clave123"}, headers=c.csrf)
            self.assertEqual(r.status_code, 201, r.get_json())
        g.pop("_login_user", None)
        return c

    def get(self, c, url):
        g.pop("_login_user", None)
        return c.get(url)

    def post(self, c, url, datos=None, metodo="post"):
        g.pop("_login_user", None)
        return getattr(c, metodo)(url, json=datos or {}, headers=c.csrf)

    def admin(self):
        a = self.cliente(ADMIN, "Cristian")
        self.assertEqual(self.post(a, "/api/admin/entrar", {"clave": "ClaveAdmin-123"}).status_code, 200)
        return a

    def test_solo_el_correo_admin_ve_la_opcion_y_necesita_la_clave(self):
        ana = self.cliente("ana@example.com")
        self.assertNotIn("admin", self.get(ana, "/api/auth/me/").get_json()["user"])
        self.assertEqual(self.get(ana, "/api/admin/estado").status_code, 404)
        self.assertEqual(self.post(ana, "/api/admin/entrar", {"clave": "ClaveAdmin-123"}).status_code, 404)
        self.assertEqual(self.get(ana, "/api/admin/usuarios").status_code, 404)

        yo = self.cliente(ADMIN, "Cristian")
        r = self.post(yo, "/api/auth/login/", {"email": ADMIN.upper(), "password": "Clave123"}).get_json()
        self.assertTrue(r["user"]["admin"])
        self.assertEqual(self.get(yo, "/api/admin/usuarios").status_code, 404, "sin la clave no entra")
        self.assertEqual(self.post(yo, "/api/admin/entrar", {"clave": "mala"}).status_code, 403)
        self.assertEqual(self.post(yo, "/api/admin/entrar", {"clave": "ClaveAdmin-123"}).status_code, 200)
        self.assertEqual(self.get(yo, "/api/admin/usuarios").get_json()["total"], 2)
        self.post(yo, "/api/admin/salir")
        self.assertEqual(self.get(yo, "/api/admin/usuarios").status_code, 404)

    def test_sin_clave_configurada_el_panel_esta_apagado(self):
        os.environ.pop("ADMIN_CLAVE")
        yo = self.cliente(ADMIN)
        self.assertEqual(self.post(yo, "/api/admin/entrar", {"clave": ""}).status_code, 409)

    def test_virus_crea_incidente_avisa_por_correo_y_el_admin_bloquea(self):
        ana = self.cliente("ana@example.com")
        g.pop("_login_user", None)
        r = ana.post("/api/trabajo/archivos/?nombre=tarea.txt", data=b"hola " + EICAR, headers={**ana.csrf, "Content-Type": "application/octet-stream"})
        self.assertEqual(r.status_code, 422)
        inc = Incidente.query.one()
        self.assertEqual((inc.tipo, inc.gravedad, inc.estado), ("archivo", "critica", "pendiente"))
        correos = self.app.extensions["correos_enviados"]
        self.assertTrue(any(c["para"] == "ana@example.com" and "Infracción" in c["asunto"] and "Por qué es una infracción" in c["html"] for c in correos))

        yo = self.admin()
        lista = self.get(yo, "/api/admin/incidentes").get_json()["incidentes"]
        self.assertEqual(lista[0]["usuario"]["impacto"], 90)
        self.assertEqual(self.post(yo, f"/api/admin/incidentes/{inc.id}", {"decision": "bloquear", "motivo": "Virus"}).status_code, 200)
        self.assertFalse(db.session.get(User, inc.usuario_id).activo)
        self.assertIsNone(self.get(ana, "/api/auth/me/").get_json()["user"], "sus sesiones se cerraron")
        r = self.post(self.cliente("x@x.com", registrar=False), "/api/auth/login/", {"email": "ana@example.com", "password": "Clave123"})
        self.assertEqual(r.status_code, 403)
        self.assertIn("bloqueada", r.get_json()["error"])
        uid = inc.usuario_id
        self.post(yo, f"/api/admin/usuarios/{uid}/desbloquear")
        self.assertTrue(db.session.get(User, uid).activo)

    def test_reincidencia_sube_la_gravedad(self):
        from servicios.moderacion import registrar
        u = User(nombre="Leo", email="leo@example.com", password_hash="x"); db.session.add(u); db.session.commit()
        niveles = [registrar(u, "comando", "apaga o reinicia el equipo").gravedad for _ in range(7)]
        self.assertEqual(niveles[0], "baja")
        self.assertEqual(niveles[3], "media")
        self.assertEqual(niveles[6], "alta")
        self.assertEqual(sum(1 for c in self.app.extensions["correos_enviados"] if c["para"] == "leo@example.com"), 7, "un correo por infracción")

    def test_no_se_puede_bloquear_al_admin(self):
        yo = self.admin()
        uid = User.query.filter_by(email=ADMIN).one().id
        self.assertEqual(self.post(yo, f"/api/admin/usuarios/{uid}/bloquear", {"motivo": "x"}).status_code, 400)

    def test_tablas_ocultan_secretos(self):
        self.cliente("ana@example.com")
        yo = self.admin()
        nombres = {t["nombre"] for t in self.get(yo, "/api/admin/tablas").get_json()["tablas"]}
        self.assertTrue({"usuarios", "perfiles", "incidentes", "medallas_especiales"} <= nombres)
        filas = self.get(yo, "/api/admin/tablas/usuarios?q=example.com").get_json()["filas"]
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["password_hash"], "••• oculto")
        self.assertEqual(self.get(yo, "/api/admin/tablas/nada").status_code, 404)

    def test_crear_medalla_y_articulo_que_la_da(self):
        yo = self.admin()
        m = self.post(yo, "/api/admin/medallas", {"nombre": "Cazador de bugs", "icono": "🐞"}).get_json()["medalla"]
        a = self.post(yo, "/api/admin/tienda", {"nombre": "Insignia bug", "precio": 0, "xp": 10, "medalla_id": m["id"]}).get_json()["articulo"]
        self.assertTrue(a["clave"].startswith("x_") and a["extra"]["permanente"])
        ana = self.cliente("ana@example.com")
        items = self.get(ana, "/api/tienda/").get_json()["items"]
        self.assertTrue(any(i["clave"] == a["clave"] and i["especial"] for i in items))
        self.assertEqual(self.post(ana, "/api/tienda/comprar/", {"clave": a["clave"]}).status_code, 200)
        self.assertEqual(self.post(ana, "/api/tienda/comprar/", {"clave": a["clave"]}).status_code, 400, "solo una vez")
        esp = self.get(ana, "/api/medallas/").get_json()["especiales"]
        self.assertEqual([e["nombre"] for e in esp], ["Cazador de bugs"])
        # Ocultar el artículo
        self.post(yo, f"/api/admin/tienda/{a['id']}", {"activo": False}, metodo="patch")
        self.assertFalse(any(i["clave"] == a["clave"] for i in self.get(ana, "/api/tienda/").get_json()["items"]))


if __name__ == "__main__":
    unittest.main()
