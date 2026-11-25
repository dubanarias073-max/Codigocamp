"""Retos más difíciles y tipo Duolingo: unir parejas, armar la línea con fichas y completar el código."""
import unittest

from retos import cargar_cursos, errores_catalogo, secciones_del_camino
from retos.generador import _fichas, _regalada
from servicios.retos import fnv1a

CURSOS = cargar_cursos()


def preguntas(etapas):
    return [r for e in etapas for s in e["secciones"] for l in s["lecciones"] for r in l["retos"]]


class GeneradorTest(unittest.TestCase):
    def test_catalogo_valido_y_con_ejercicios_nuevos(self):
        self.assertEqual(errores_catalogo(CURSOS), [])
        tipos = {r["tipo"] for r in preguntas(CURSOS["python"])}
        self.assertTrue({"parejas", "armar", "opcion", "completar"} <= tipos)

    def test_la_dificultad_sube_a_lo_largo_del_curso(self):
        etapas = CURSOS["python"]
        por_leccion = lambda e: sum(len(l["retos"]) for s in e["secciones"] for l in s["lecciones"]) / sum(len(s["lecciones"]) for s in e["secciones"])
        self.assertLess(por_leccion(etapas[0]), por_leccion(etapas[-1]))
        pares = lambda e: max((len(r["datos"]["pares"]) for r in preguntas([e]) if r["tipo"] == "parejas"), default=0)
        self.assertLess(pares(etapas[0]), pares(etapas[-1]))
        pistas = lambda e: sum("letras)" in r["enunciado"] or "caracteres)" in r["enunciado"] for r in preguntas([e]))
        self.assertEqual(pistas(etapas[-1]), 0)

    def test_casi_ninguna_opcion_multiple_regala_la_respuesta(self):
        opciones = [r for r in preguntas(CURSOS["python"]) if r["tipo"] == "opcion"]
        self.assertLess(sum(_regalada(r) for r in opciones) / len(opciones), 0.08)

    def test_fichas_de_codigo(self):
        self.assertEqual(_fichas('git log -S "x" --oneline'), ["git", "log", "-S", '"x"', "--oneline"])
        self.assertEqual(_fichas("color: #fff;"), ["color", ":", "#fff", ";"])
        self.assertEqual(_fichas("print(n)"), ["print", "(", "n", ")"])

    def test_ninguna_ficha_trampa_esta_en_la_solucion(self):
        for r in preguntas(CURSOS["javascript"]):
            if r["tipo"] == "armar":
                self.assertFalse(set(r["datos"]["trampas"]) & set(r["datos"]["solucion"]))
                self.assertIn("▁▁▁", r["codigo"])

    def test_hash_igual_al_del_navegador(self):
        self.assertEqual(fnv1a("abc"), "1a47e90b")   # el mismo valor que da js/reto.js


class ResponderTest(unittest.TestCase):
    def setUp(self):
        from app import create_app
        from models import db, Challenge, Course, Level, Section, Stage
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "SESSION_COOKIE_SECURE": False,
                               "GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": "", "ALMACEN_ARCHIVOS": "/tmp/cc-test-duolingo"})
        self.ctx = self.app.app_context(); self.ctx.push()
        db.create_all()
        curso = Course(slug="py", nombre="Py", tipo="lenguaje", sigla="PY", color="#3776ab", orden=1)
        etapa = Stage(course=curso, orden=1, titulo="E", descripcion="d")
        sec = Section(etapa=etapa, orden=1, titulo="S")
        nivel = Level(seccion=sec, orden=1, titulo="L", tipo="leccion", xp=10)
        self.par = Challenge(nivel=nivel, orden=1, tipo="parejas", enunciado="Une", explicacion="x",
                             datos={"pares": [["a", "1"], ["b", "2"], ["c", "3"]]})
        self.arm = Challenge(nivel=nivel, orden=2, tipo="armar", enunciado="Arma", codigo="▁▁▁", respuesta="print ( n )", explicacion="x",
                             datos={"solucion": ["print", "(", "n", ")"], "trampas": ["max"]})
        db.session.add_all([curso, self.par, self.arm]); db.session.commit()
        self.c = self.app.test_client(); self.c.environ_base.update(HTTP_USER_AGENT="Mozilla/5.0 Chrome/120")
        self.c.get("/api/auth/me/")
        self.h = {"X-CSRFToken": self.c.get_cookie("csrftoken").value}
        self.c.post("/api/auth/register/", json={"nombre": "Ana R", "email": "a@b.co", "password": "Clave123"}, headers=self.h)
        self.nivel = nivel.id

    def tearDown(self):
        from models import db
        db.session.remove(); db.drop_all(); self.ctx.pop()

    def test_parejas_y_armar(self):
        d = self.c.get(f"/api/nivel/{self.nivel}/").get_json()
        q = next(r for r in d["retos"] if r["tipo"] == "parejas")
        self.assertNotIn("pares", q)                                # no viajan las respuestas
        texto_der = {x["t"]: x["id"] for x in q["der"]}
        bien = [[0, texto_der["1"]], [1, texto_der["2"]], [2, texto_der["3"]]]
        self.assertTrue(all(fnv1a(f"{q['sal']}|{i}|{did}") in q["sellos"] for i, did in bien))
        r = lambda cid, resp: self.c.post(f"/api/reto/{cid}/responder/", json={"respuesta": resp}, headers=self.h).get_json()
        self.assertTrue(r(self.par.id, {"pares": bien, "fallos": 0})["correcto"])
        self.assertFalse(r(self.par.id, {"pares": bien, "fallos": 1})["correcto"])     # con 3 parejas no se permite fallar
        self.assertFalse(r(self.par.id, {"pares": [[0, texto_der["2"]], [1, texto_der["1"]], [2, texto_der["3"]]], "fallos": 0})["correcto"])
        a = next(x for x in d["retos"] if x["tipo"] == "armar")
        self.assertEqual(sorted(a["fichas"]), sorted(["print", "(", "n", ")", "max"]))
        self.assertTrue(r(self.arm.id, ["print", "(", "n", ")"])["correcto"])
        self.assertFalse(r(self.arm.id, ["print", "(", "max", ")"])["correcto"])
