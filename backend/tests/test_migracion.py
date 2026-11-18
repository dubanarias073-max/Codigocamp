import tempfile
import unittest

from app import create_app
from models import CompletedLevel, Course, Level, Section, Stage, User, db
from retos import ORDEN, cargar_cursos
from retos.migracion import migrar_camino


class MigracionCaminoTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "x", "SQLALCHEMY_DATABASE_URI": "sqlite://", "ALMACEN_ARCHIVOS": tempfile.mkdtemp()})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        for i, slug in enumerate(ORDEN, 1):
            db.session.add(Course(id=i, slug=slug, nombre=slug, sigla=slug[:4].upper()))
        db.session.add(User(id=1, email="a@a.co", password_hash="x", nombre="Ana"))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    def _viejo(self):
        """Camino al estilo anterior: etapa con «Internet» (4 lecciones + cofre) y «La web», más su examen."""
        etapa = Stage(curso_id=1, orden=1, titulo="La web y qué es HTML", descripcion="")
        niveles = {}
        for j, titulo in enumerate(["Internet", "La web"], 1):
            sec = Section(etapa=etapa, orden=j, titulo=titulo)
            for k in range(1, 5):
                niveles[(titulo, k)] = Level(seccion=sec, orden=k, titulo=f"{titulo} {k}", tipo="leccion", xp=15)
            niveles[(titulo, "cofre")] = Level(seccion=sec, orden=5, titulo=f"Cofre: {titulo}", tipo="cofre", xp=0)
        niveles["trofeo"] = Level(seccion=sec, orden=6, titulo="Examen", tipo="trofeo", xp=30)
        db.session.add(etapa)
        db.session.commit()
        return niveles

    def test_traslada_lecciones_cofres_y_examen(self):
        n = self._viejo()
        for clave, estrellas in (((("Internet", 1)), 3), (("Internet", 2), 2), (("Internet", "cofre"), 1), (("La web", 1), 1),
                                 (("La web", 2), 1), (("La web", 3), 1), (("La web", 4), 1), ("trofeo", 3)):
            db.session.add(CompletedLevel(usuario_id=1, nivel_id=n[clave].id, estrellas=estrellas))
        db.session.commit()
        r = migrar_camino(db.session)
        self.assertEqual(r["personas"], 1)
        nuevo = cargar_cursos()
        self.assertEqual(Stage.query.count(), sum(len(e) for e in nuevo.values()))

        def hechas(titulo, tipo="leccion"):
            sec = Section.query.join(Stage).filter(Stage.curso_id == 1, Section.titulo == titulo).one()
            todas = [l for l in sec.niveles if l.tipo == tipo]
            ok = {c.nivel_id for c in CompletedLevel.query.filter_by(usuario_id=1)}
            return sum(1 for l in todas if l.id in ok), len(todas)

        hechas_internet, total_internet = hechas("Internet")
        self.assertEqual(hechas_internet, -(-2 * total_internet // 4), "2 de 4 → la mitad (hacia arriba)")
        self.assertEqual(hechas("La web")[0], hechas("La web")[1], "todas")
        self.assertEqual(hechas("Internet", "cofre"), (1, 1))
        self.assertEqual(hechas("La web", "cofre")[0], 0)
        primera = Stage.query.filter_by(curso_id=1, orden=1).one()
        trofeo = next(l for s in primera.secciones for l in s.niveles if l.tipo == "trofeo")
        self.assertIsNone(CompletedLevel.query.filter_by(usuario_id=1, nivel_id=trofeo.id).first(),
                          "la etapa nueva tiene conceptos que nunca se examinaron")
        estrellas = {c.estrellas for c in CompletedLevel.query.filter_by(usuario_id=1)}
        self.assertIn(3, estrellas)
        self.assertEqual(Level.query.filter_by(tipo="leccion").count(), sum(len(s["lecciones"]) for e in nuevo.values() for et in e for s in et["secciones"]))


if __name__ == "__main__":
    unittest.main()
