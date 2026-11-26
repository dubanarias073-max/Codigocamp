"""Panel de administrador: editar usuarios (con correo), quitar faltas, tienda editable (también de fábrica),
cosméticos diseñados, cursos/retos/Aprende creados en el panel y que sync-retos respete todo eso."""
import os
import unittest

from flask import g

import utilidades
from app import create_app
from models import Course, Incidente, Profile, StoreItem, User, db

ADMIN = "dubanarias073@gmail.com"


class Base(unittest.TestCase):
    catalogo = False

    def setUp(self):
        utilidades._RATE_LIMITS.clear()
        import servicios.catalogo_admin as ca
        import servicios.tienda as t
        t._ITEMS_LISTOS = False
        ca._ultimo = 0
        os.environ["ADMIN_CLAVE"] = "ClaveAdmin-123"
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""})
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        if self.catalogo:   # cursos de fábrica (en producción vienen de codigocamp.sql) + su catálogo completo
            from retos import ORDEN, poblar_catalogo
            for i, slug in enumerate(ORDEN):
                if not Course.query.filter_by(slug=slug).first():
                    db.session.add(Course(slug=slug, nombre=slug.title(), tipo="lenguaje", sigla=slug[:4].upper(), color="#4ade80", descripcion="", orden=i, activo=True))
            db.session.commit()
            poblar_catalogo(db.session)
        self.yo = self.cliente(ADMIN, "Cristian")
        self.assertEqual(self.post(self.yo, "/api/admin/entrar", {"clave": "ClaveAdmin-123"}).status_code, 200)
        self.ana = self.cliente("ana@example.com", "Ana")
        self.uid = User.query.filter_by(email="ana@example.com").one().id
        self.app.extensions["correos_enviados"] = []

    def tearDown(self):
        import cosmeticos
        import servicios.catalogo_admin as ca
        import servicios.tienda as t
        t._ITEMS_LISTOS = False
        for k in list(cosmeticos.POR_CLAVE):
            if k.startswith("a_"):
                cosmeticos.POR_CLAVE.pop(k)
        ca._claves_admin = set()
        os.environ.pop("ADMIN_CLAVE", None)
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def cliente(self, email, nombre):
        c = self.app.test_client()
        c.get("/api/auth/me/")
        c.csrf = {"X-CSRFToken": c.get_cookie("csrftoken").value}
        r = c.post("/api/auth/register/", json={"nombre": nombre, "email": email, "password": "Clave123"}, headers=c.csrf)
        self.assertEqual(r.status_code, 201, r.get_json())
        g.pop("_login_user", None)
        return c

    def get(self, c, url):
        g.pop("_login_user", None)
        return c.get(url)

    def post(self, c, url, datos=None, metodo="post"):
        g.pop("_login_user", None)
        return getattr(c, metodo)(url, json=datos if datos is not None else {}, headers=c.csrf)

    def correos(self):
        return [c for c in self.app.extensions["correos_enviados"] if c["para"] == "ana@example.com"]


class UsuariosTest(Base):
    def test_editar_diamantes_avisa_por_correo(self):
        r = self.post(self.yo, f"/api/admin/usuarios/{self.uid}", {"diamante": 750, "racha_actual": 9, "nota": "¡Gracias!"}, "patch")
        self.assertEqual(r.status_code, 200, r.get_json())
        p = Profile.query.filter_by(usuario_id=self.uid).one()
        self.assertEqual((p.diamante, p.racha_actual, p.racha_maxima), (750, 9, 9))
        c = self.correos()[-1]
        self.assertIn("Recibiste 750 diamantes", c["html"])
        self.assertIn("¡Gracias!", c["html"])
        self.assertIn("regalo", c["asunto"])
        # Sin avisar: no hay correo nuevo
        n = len(self.correos())
        self.post(self.yo, f"/api/admin/usuarios/{self.uid}", {"vidas": 2, "avisar": False}, "patch")
        self.assertEqual(len(self.correos()), n)

    def test_alias_repetido_y_valores_fuera_de_rango(self):
        self.post(self.yo, f"/api/admin/usuarios/{self.uid}", {"alias": "anita"}, "patch")
        yo_id = User.query.filter_by(email=ADMIN).one().id
        self.assertEqual(self.post(self.yo, f"/api/admin/usuarios/{yo_id}", {"alias": "anita"}, "patch").status_code, 400)
        self.post(self.yo, f"/api/admin/usuarios/{self.uid}", {"salvarrachas": 99}, "patch")
        self.assertEqual(Profile.query.filter_by(usuario_id=self.uid).one().salvarrachas, 10)

    def test_quitar_faltas(self):
        from servicios.moderacion import registrar
        u = db.session.get(User, self.uid)
        a = registrar(u, "comando", "apaga o reinicia el equipo")
        registrar(u, "comando", "apaga o reinicia el equipo")
        self.assertEqual(self.post(self.yo, f"/api/admin/incidentes/{a.id}", None, "delete").status_code, 200)
        self.assertEqual(Incidente.query.filter_by(usuario_id=self.uid).count(), 1)
        r = self.post(self.yo, f"/api/admin/usuarios/{self.uid}/limpiar-faltas")
        self.assertEqual(r.get_json()["borradas"], 1)
        self.assertIn("Se retiraron tus faltas", self.correos()[-1]["html"])

    def test_regalar_cosmetico_y_medalla_con_correo(self):
        r = self.post(self.yo, f"/api/admin/usuarios/{self.uid}/regalar", {"clave": "fondo_aurora"})
        self.assertEqual(r.status_code, 200, r.get_json())
        self.assertIn("Aurora boreal", self.correos()[-1]["html"])
        self.assertEqual(self.post(self.yo, f"/api/admin/usuarios/{self.uid}/regalar", {"clave": "fondo_aurora"}).status_code, 400)
        m = self.post(self.yo, "/api/admin/medallas", {"nombre": "Cazador de bugs", "icono": "🐞"}).get_json()["medalla"]
        self.post(self.yo, f"/api/admin/usuarios/{self.uid}/medalla", {"medalla_id": m["id"]})
        self.assertIn("Cazador de bugs", self.correos()[-1]["asunto"])
        # Borrar la medalla se la quita
        self.assertEqual(self.post(self.yo, f"/api/admin/medallas/{m['id']}", None, "delete").status_code, 200)
        self.assertEqual(self.get(self.ana, "/api/medallas/").get_json()["especiales"], [])


class TiendaTest(Base):
    def articulo(self, clave):
        return next(a for a in self.get(self.yo, "/api/admin/tienda").get_json()["articulos"] if a["clave"] == clave)

    def test_editar_precio_de_fabrica_sobrevive_al_reinicio_y_se_restaura(self):
        import servicios.tienda as t
        a = self.articulo("vida")
        r = self.post(self.yo, f"/api/admin/tienda/{a['id']}", {"precio": 3, "nombre": "Vidita", "rareza": "epico"}, "patch")
        self.assertEqual(r.status_code, 200, r.get_json())
        t._ITEMS_LISTOS = False   # «reinicio»: el código vuelve a sincronizar precios…
        items = {i["clave"]: i for i in self.get(self.ana, "/api/tienda/").get_json()["items"]}
        self.assertEqual((items["vida"]["precio"], items["vida"]["nombre"], items["vida"]["rareza"]), (3, "Vidita", "epico"))   # …y se respeta
        self.post(self.yo, f"/api/admin/tienda/{a['id']}/restaurar")
        self.assertEqual(db.session.get(StoreItem, a["id"]).precio, 10)

    def test_eliminar_de_fabrica_lo_oculta_y_creado_se_borra(self):
        import servicios.tienda as t
        a = self.articulo("fondo_bosque")
        self.post(self.yo, f"/api/admin/tienda/{a['id']}", None, "delete")
        t._ITEMS_LISTOS = False
        self.assertNotIn("fondo_bosque", [i["clave"] for i in self.get(self.ana, "/api/tienda/").get_json()["items"]])
        n = self.post(self.yo, "/api/admin/tienda", {"nombre": "Pack", "precio": 0, "xp": 5}).get_json()["articulo"]
        self.post(self.ana, "/api/tienda/comprar/", {"clave": n["clave"]})
        self.assertEqual(self.post(self.yo, f"/api/admin/tienda/{n['id']}", None, "delete").get_json(), {"ok": True, "borrado": True})
        self.assertIsNone(db.session.get(StoreItem, n["id"]))

    def test_cosmetico_disenado_se_vende_se_equipa_y_se_dibuja(self):
        r = self.post(self.yo, "/api/admin/cosmeticos", {"tipo": "fondo", "nombre": "Atardecer neón", "precio": 0, "rareza": "epico",
                                                         "diseno": {"estilo": "aurora", "colores": ["#000000", "#ff00ff", "url(x)"], "animacion": "nieve"}})
        self.assertEqual(r.status_code, 201, r.get_json())
        c = r.get_json()["cosmetico"]
        self.assertEqual(c["diseno"]["colores"], ["#000000", "#ff00ff"], "solo colores #hex")
        items = {i["clave"]: i for i in self.get(self.ana, "/api/tienda/").get_json()["items"]}
        self.assertEqual((items[c["clave"]]["tipo"], items[c["clave"]]["rareza"]), ("fondo", "epico"))
        self.assertEqual(self.post(self.ana, "/api/tienda/comprar/", {"clave": c["clave"]}).status_code, 200)
        self.assertEqual(self.post(self.ana, "/api/cosmeticos/equipar/", {"tipo": "fondo", "clave": c["clave"]}).status_code, 200)
        publicos = self.get(self.ana, "/api/cosmeticos/disenos/").get_json()["disenos"]
        self.assertEqual(publicos[0]["diseno"]["animacion"], "nieve")
        # Editar y luego eliminar: se le quita a quien lo tenía
        self.post(self.yo, f"/api/admin/cosmeticos/{c['id']}", {"precio": 50}, "patch")
        self.assertEqual(StoreItem.query.filter_by(clave=c["clave"]).one().precio, 50)
        self.post(self.yo, f"/api/admin/tienda/{c['articulo_id']}", None, "delete")
        from models import OwnedCosmetic
        self.assertEqual(OwnedCosmetic.query.filter_by(clave=c["clave"]).count(), 0)

    def test_imagen_para_fondo(self):
        png = b"\x89PNG\r\n\x1a\n" + b"\0" * 64
        g.pop("_login_user", None)
        r = self.yo.post("/api/admin/imagen", data=png, headers={**self.yo.csrf, "Content-Type": "application/octet-stream"})
        self.assertEqual(r.status_code, 201, r.get_json())
        url = r.get_json()["url"]
        self.assertEqual(self.get(self.ana, url).data, png)
        g.pop("_login_user", None)
        self.assertEqual(self.yo.post("/api/admin/imagen", data=b"MZ" + b"\0" * 50, headers=self.yo.csrf).status_code, 400)
        self.assertEqual(self.post(self.ana, "/api/admin/imagen").status_code, 404, "solo el administrador")

    def test_disenos_legendarios_con_imagen_y_vitrina_se_filtran(self):
        img = "/api/admin-img/" + "a" * 32 + ".png"
        r = self.post(self.yo, "/api/admin/cosmeticos", {"tipo": "marco", "nombre": "Plasma", "precio": 0, "rareza": "legendario", "diseno": {
            "estilo": "holo", "colores": ["#ff00ff", "#00ffff"], "imagen": img, "fuente": "javascript:alert(1)", "grosor": 99, "orbita": True,
            "vitrina": {"efecto": "inclinar", "aura": "#facc15", "brillo": True, "destellos": 1, "extra": "<script>"}}})
        self.assertEqual(r.status_code, 201, r.get_json())
        d = r.get_json()["cosmetico"]["diseno"]
        self.assertEqual((d["estilo"], d["imagen"], d["grosor"], d["orbita"]), ("holo", img, 10, True))
        self.assertNotIn("fuente", d, "solo imágenes subidas al panel")
        self.assertEqual(d["vitrina"], {"efecto": "inclinar", "aura": "#facc15", "brillo": True, "destellos": True})
        malo = self.post(self.yo, "/api/admin/cosmeticos", {"tipo": "teclado", "nombre": "Malo", "precio": 0, "diseno": {
            "estilo": "x;}body{", "imagen": "https://mal.com/a.png", "vitrina": {"efecto": "girar", "aura": "red"}}}).get_json()["cosmetico"]["diseno"]
        self.assertEqual((malo["estilo"], malo["imagen"], malo["vitrina"]["efecto"], malo["vitrina"]["aura"]), ("plano", "", "girar", ""))
        items = {i["clave"]: i for i in self.get(self.ana, "/api/tienda/").get_json()["items"]}
        self.assertEqual(items[r.get_json()["cosmetico"]["clave"]]["vitrina"]["efecto"], "inclinar", "la tienda recibe la vitrina")

    def test_articulo_con_premios_lleva_imagen_y_vitrina(self):
        img = "/api/admin-img/" + "b" * 32 + ".webp"
        n = self.post(self.yo, "/api/admin/tienda", {"nombre": "Cofre dorado", "precio": 5, "xp": 50, "imagen": img,
                                                      "vitrina": {"efecto": "girar", "aura": "#f59e0b", "brillo": True}}).get_json()["articulo"]
        self.assertEqual((n["extra"]["imagen"], n["extra"]["vitrina"]["efecto"]), (img, "girar"))
        item = next(i for i in self.get(self.ana, "/api/tienda/").get_json()["items"] if i["clave"] == n["clave"])
        self.assertEqual((item["imagen"], item["vitrina"]["aura"]), (img, "#f59e0b"))
        self.post(self.yo, f"/api/admin/tienda/{n['id']}", {"imagen": "../../etc/passwd", "xp": 50}, "patch")
        self.assertEqual(self.articulo(n["clave"])["extra"]["imagen"], "")

    def test_quitar_cosmetico_comprado_desaparece_de_verdad(self):
        a = self.articulo("fondo_bosque")
        db.session.get(Profile, Profile.query.filter_by(usuario_id=self.uid).one().id).diamante = 10000
        db.session.commit()
        self.assertEqual(self.post(self.ana, "/api/tienda/comprar/", {"clave": "fondo_bosque"}).status_code, 200)
        self.post(self.ana, "/api/cosmeticos/equipar/", {"tipo": "fondo", "clave": "fondo_bosque"})
        self.assertEqual(self.post(self.yo, f"/api/admin/usuarios/{self.uid}/quitar-cosmetico", {"clave": "fondo_bosque"}).status_code, 200)
        tienda = {i["clave"]: i for i in self.get(self.ana, "/api/tienda/").get_json()["items"]}
        self.assertFalse(tienda["fondo_bosque"]["tuyo"], "ya no sale como suyo en la tienda")
        c = self.get(self.ana, "/api/cosmeticos/").get_json()
        self.assertFalse(next(x for x in c["catalogo"] if x["clave"] == "fondo_bosque")["tuyo"])
        self.assertNotEqual(c["equipados"].get("fondo"), "fondo_bosque", "y se le quitó de encima")
        self.assertEqual(self.post(self.ana, "/api/tienda/comprar/", {"clave": "fondo_bosque"}).status_code, 200, "puede volver a comprarlo")

    def test_codi_con_imagen_fondo_con_stickers_y_marco_con_insignia(self):
        gif = "/api/admin-img/" + "c" * 32 + ".gif"
        claves = {}
        for tipo, d in (("codi", {"imagen": gif, "capa": "cabeza", "anim": "flotar", "sinAntena": True}),
                        ("fondo", {"estilo": "imagen", "imagen": gif, "movimiento": "zoom", "stickers": [{"imagen": gif, "x": 20, "anim": "girar"}] * 10}),
                        ("marco", {"estilo": "holo", "insignia": {"imagen": gif, "pos": "arriba"}}),
                        ("dedo", {"modo": "mascota", "imagen": gif, "tam": 64})):
            r = self.post(self.yo, "/api/admin/cosmeticos", {"tipo": tipo, "nombre": f"Prueba {tipo}", "precio": 0, "diseno": d})
            self.assertEqual(r.status_code, 201, r.get_json())
            claves[tipo] = r.get_json()["cosmetico"]
        self.assertEqual(len(claves["fondo"]["diseno"]["stickers"]), 8, "máximo 8 stickers")
        self.assertEqual(claves["marco"]["diseno"]["insignia"]["imagen"], gif)
        # El estudiante lo compra y se lo pone (Codi también)
        for tipo, c in claves.items():
            self.assertEqual(self.post(self.ana, "/api/tienda/comprar/", {"clave": c["clave"]}).status_code, 200, tipo)
            self.assertEqual(self.post(self.ana, "/api/cosmeticos/equipar/", {"tipo": tipo, "clave": c["clave"]}).status_code, 200, tipo)
        publicos = {x["clave"]: x for x in self.get(self.ana, "/api/cosmeticos/disenos/").get_json()["disenos"]}
        self.assertEqual(publicos[claves["codi"]["clave"]]["diseno"]["capa"], "cabeza")

    def test_puntero_por_partes_y_medalla_disenada(self):
        r = self.post(self.yo, "/api/admin/cosmeticos", {"tipo": "cursor", "nombre": "Gatito", "precio": 0, "diseno": {"tam": 48, "partes": {
            "normal": {"tipo": "emoji", "emoji": "🐱"}, "mano": {"tipo": "sistema"}, "texto": {"tipo": "imagen", "imagen": "javascript:x"}}}})
        partes = r.get_json()["cosmetico"]["diseno"]["partes"]
        self.assertEqual((partes["normal"]["tipo"], partes["normal"]["emoji"], partes["mano"]["tipo"], partes["texto"]["tipo"]), ("emoji", "🐱", "sistema", "barra"),
                         "solo emoji sin flecha, la mano del sistema y una imagen mala vuelve a la barra")
        gif = "/api/admin-img/" + "d" * 32 + ".gif"
        m = self.post(self.yo, "/api/admin/medallas", {"nombre": "Leyenda", "diseno": {"forma": "corona", "metal": "arcoiris", "centro": "completa", "imagen": gif,
                                                                                         "texto": "<b>Rey</b>", "anim": "destellos", "estrellas": 9}}).get_json()["medalla"]
        self.assertEqual((m["diseno"]["forma"], m["diseno"]["centro"], m["diseno"]["texto"], m["diseno"]["estrellas"]), ("corona", "completa", "bRey/b", 5))
        uid = User.query.filter_by(email="ana@example.com").one().id
        self.post(self.yo, f"/api/admin/usuarios/{uid}/medalla", {"medalla_id": m["id"], "motivo": "Por crack"})
        especiales = self.get(self.ana, "/api/medallas/").get_json()["especiales"]
        self.assertEqual(especiales[0]["diseno"]["imagen"], gif, "el perfil recibe el diseño")


class AntivirusPanelTest(Base):
    def test_estado_y_autoprueba(self):
        e = self.get(self.yo, "/api/admin/antivirus").get_json()
        self.assertTrue(e["activo"]); self.assertGreaterEqual(e["huellas"], 4); self.assertIn("activo", e["clamav"])
        r = self.post(self.yo, "/api/admin/antivirus/probar").get_json()
        self.assertEqual((r["detectadas"], r["falsos_positivos"]), (r["total_peligrosas"], 0))
        self.assertEqual(Incidente.query.count(), 0, "la prueba no registra faltas")
        self.assertEqual(self.post(self.ana, "/api/admin/antivirus/probar").status_code, 404, "solo el administrador")


class CursosPanelTest(Base):
    def test_crear_lenguaje_con_camino_retos_y_aprende(self):
        r = self.post(self.yo, "/api/admin/cursos", {"slug": "dart", "nombre": "Dart", "sigla": "DART", "color": "#00b4ab", "activo": True})
        self.assertEqual(r.status_code, 201, r.get_json())
        cid = r.get_json()["curso"]["id"]
        cursos = {c["slug"]: c for c in self.get(self.ana, "/api/cursos/").get_json()["cursos"]}
        self.assertEqual(cursos["dart"]["motor"], "ver")
        arbol = self.get(self.yo, f"/api/admin/cursos/{cid}/arbol").get_json()
        self.assertTrue(arbol["editable"])
        sid = arbol["etapas"][0]["secciones"][0]["id"]
        nid = self.post(self.yo, f"/api/admin/secciones/{sid}/niveles", {"titulo": "Variables"}).get_json()["id"]
        malo = self.post(self.yo, f"/api/admin/niveles/{nid}/retos", {"tipo": "opcion", "enunciado": "¿?", "opciones": ["a", "b"], "respuesta": "c", "explicacion": "x"})
        self.assertEqual(malo.status_code, 400)
        self.assertIn("respuesta no está entre las opciones", malo.get_json()["error"])
        ok = self.post(self.yo, f"/api/admin/niveles/{nid}/retos", {"tipo": "opcion", "enunciado": "¿Cómo se declara?", "opciones": ["var x", "x :="],
                                                                       "respuesta": "var x", "explicacion": "Dart usa var."})
        self.assertEqual(ok.status_code, 201, ok.get_json())
        self.post(self.yo, f"/api/admin/niveles/{nid}/retos", {"tipo": "parejas", "enunciado": "Une", "datos": {"pares": [["a", "1"], ["b", "2"], ["c", "3"]]}})
        # El estudiante lo juega
        nivel = self.get(self.ana, f"/api/nivel/{nid}/")
        self.assertEqual(nivel.status_code, 200, nivel.get_json())
        self.assertEqual(len(nivel.get_json()["retos"]), 2)
        # Aprende: lección nueva del panel
        self.post(self.yo, "/api/admin/aprende/dart", {"t": "Hola Dart", "x": "Dart es…", "p": ["uno", "dos"], "c": "void main(){}"})
        lec = self.get(self.ana, "/api/aprende/dart/").get_json()["lecciones"]
        self.assertEqual((lec[0]["t"], lec[0]["p"]), ("Hola Dart", ["uno", "dos"]))
        # Borrar el curso entero
        self.assertEqual(self.post(self.yo, f"/api/admin/cursos/{cid}", None, "delete").get_json()["borrado"], True)
        self.assertIsNone(Course.query.filter_by(slug="dart").first())

    def test_aprende_reemplazar_y_ocultar_original(self):
        db.session.add(Course(slug="python", nombre="Python", tipo="lenguaje", sigla="PY", color="#60a5fa", descripcion="", orden=1, activo=True))
        db.session.commit()
        self.post(self.yo, "/api/admin/aprende/python", {"reemplaza": "Qué es Python", "t": "Qué es Python (nuevo)", "x": "Otra explicación"})
        self.post(self.yo, "/api/admin/aprende/python", {"reemplaza": "Variables", "oculta": True})
        lec = self.get(self.ana, "/api/aprende/python/").get_json()["lecciones"]
        self.assertEqual({(x["reemplaza"], x["oculta"]) for x in lec}, {("Qué es Python", False), ("Variables", True)})


class CursosFabricaTest(Base):
    catalogo = True

    def test_retos_del_panel_y_editados_sobreviven_a_sync_retos(self):
        from models import Challenge, Level, RetoAdmin, Section, Stage
        from retos import sincronizar_catalogo
        py = Course.query.filter_by(slug="python").one()
        nivel = Level.query.join(Section).join(Stage).filter(Stage.curso_id == py.id, Level.tipo == "leccion").first()
        arbol = self.get(self.yo, f"/api/admin/cursos/{py.id}/arbol").get_json()
        self.assertFalse(arbol["editable"])
        self.assertEqual(self.post(self.yo, f"/api/admin/cursos/{py.id}/etapas", {"titulo": "x"}).status_code, 403)
        original = sorted(nivel.retos, key=lambda r: r.orden)[0]
        self.post(self.yo, f"/api/admin/retos/{original.id}", {"tipo": "completar", "enunciado": "Editado", "respuesta": "print", "explicacion": "x"}, "patch")
        segundo = sorted(nivel.retos, key=lambda r: r.orden)[1]
        self.assertTrue(self.post(self.yo, f"/api/admin/retos/{segundo.id}", None, "delete").get_json()["oculto"])
        nuevo = self.post(self.yo, f"/api/admin/niveles/{nivel.id}/retos", {"tipo": "completar", "enunciado": "Mío", "respuesta": "x", "explicacion": "y"}).get_json()["id"]
        self.assertGreaterEqual(db.session.get(Challenge, nuevo).orden, 500)
        sincronizar_catalogo(db.session)   # lo que corre `flask sync-retos`
        db.session.expire_all()
        self.assertEqual(db.session.get(Challenge, original.id).enunciado, "Editado")
        self.assertIsNotNone(db.session.get(Challenge, nuevo))
        self.assertTrue(db.session.get(RetoAdmin, segundo.id).oculto)
        # El estudiante no ve el oculto y sí ve el nuevo
        from servicios.retos import level_challenges
        ids = {c.id for c in level_challenges(db.session.get(Level, nivel.id))}
        self.assertIn(nuevo, ids)
        self.assertNotIn(segundo.id, ids)
        # seed-retos sigue viendo el catálogo completo (no cuenta lo del panel)
        from retos import poblar_catalogo
        self.assertFalse(poblar_catalogo(db.session))
        # Editar el nombre de un curso de fábrica se respeta en la sincronización
        self.post(self.yo, f"/api/admin/cursos/{py.id}", {"descripcion": "Mi descripción"}, "patch")
        sincronizar_catalogo(db.session)
        self.assertEqual(db.session.get(Course, py.id).descripcion, "Mi descripción")


if __name__ == "__main__":
    unittest.main()
