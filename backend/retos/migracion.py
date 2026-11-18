"""Pasa el camino de retos a la estructura nueva SIN perder el progreso de los estudiantes.

    flask --app app migrar-camino

Por qué hace falta: el camino nuevo no repite preguntas, así que cada concepto tiene 2 o 3 lecciones (antes 4) y las
etapas se parten en partes de 45 lecciones como máximo. `sync-retos` se niega a quitar lecciones para proteger el
avance; este comando lo traslada:
  · Cada concepto (sección) se reconoce por su título, que no cambia.
  · Si alguien había hecho k de las 4 lecciones viejas de un concepto, se le marca la misma proporción de las nuevas
    (las 4 → todas; 2 de 4 → la mitad, redondeando hacia arriba), con sus estrellas.
  · El cofre de cada concepto se conserva.
  · El examen (trofeo) de una etapa nueva queda hecho si la persona había aprobado los exámenes de todas las etapas
    viejas de donde salen sus conceptos.
La XP, las rachas y los diamantes no se tocan (viven en el perfil).
"""
import math
from collections import defaultdict


def _foto_progreso(session):
    """Qué completó cada persona, por curso y concepto (título de sección)."""
    from models import CompletedLevel, Level, Section, Stage

    filas = (session.query(CompletedLevel, Level, Section, Stage)
             .join(Level, CompletedLevel.nivel_id == Level.id).join(Section, Level.seccion_id == Section.id)
             .join(Stage, Section.etapa_id == Stage.id).all())
    lecciones_por_seccion = defaultdict(int)
    for (sec_id,) in session.query(Level.seccion_id).filter(Level.tipo == "leccion").all():
        lecciones_por_seccion[sec_id] += 1
    conceptos = defaultdict(lambda: {"hechas": 0, "total": 0, "estrellas": 1, "cofre": None, "fecha": None})
    trofeos = defaultdict(set)   # (usuario, curso) -> títulos de secciones cubiertas por exámenes aprobados
    secciones_de_etapa = defaultdict(list)
    for stage_id, titulo in session.query(Section.etapa_id, Section.titulo).all():
        secciones_de_etapa[stage_id].append(titulo)
    for hecho, nivel, seccion, etapa in filas:
        curso = etapa.curso_id
        clave = (hecho.usuario_id, curso, seccion.titulo)
        c = conceptos[clave]
        if c["fecha"] is None or (hecho.completado_en and hecho.completado_en > c["fecha"]):
            c["fecha"] = hecho.completado_en
        if nivel.tipo == "leccion":
            c["hechas"] += 1
            c["total"] = lecciones_por_seccion[seccion.id]
            c["estrellas"] = max(c["estrellas"], hecho.estrellas)
        elif nivel.tipo == "cofre":
            c["cofre"] = (hecho.estrellas, hecho.veces, hecho.completado_en)
        elif nivel.tipo == "trofeo":
            trofeos[(hecho.usuario_id, curso)].update(secciones_de_etapa[etapa.id])
    return conceptos, trofeos


def migrar_camino(session):
    """Recrea el catálogo con la estructura nueva y traslada el progreso. Devuelve un resumen."""
    from models import Challenge, CompletedLevel, Level, Section, Stage
    from retos import poblar_catalogo

    conceptos, trofeos = _foto_progreso(session)
    personas = {u for u, _c, _t in conceptos}

    # Borrar el catálogo viejo (explícito, por si la base no tiene ON DELETE CASCADE activo).
    ids_niveles = [i for (i,) in session.query(Level.id).all()]
    if ids_niveles:
        session.query(CompletedLevel).filter(CompletedLevel.nivel_id.in_(ids_niveles)).delete(synchronize_session=False)
        session.query(Challenge).filter(Challenge.nivel_id.in_(ids_niveles)).delete(synchronize_session=False)
    session.query(Level).delete(synchronize_session=False)
    session.query(Section).delete(synchronize_session=False)
    session.query(Stage).delete(synchronize_session=False)
    session.commit()
    poblar_catalogo(session)

    restaurados = 0
    for stage in session.query(Stage).order_by(Stage.curso_id, Stage.orden).all():
        titulos = [s.titulo for s in stage.secciones]
        for seccion in stage.secciones:
            niveles = sorted(seccion.niveles, key=lambda n: n.orden)
            lecciones = [n for n in niveles if n.tipo == "leccion"]
            for usuario in personas:
                c = conceptos.get((usuario, stage.curso_id, seccion.titulo))
                if not c:
                    continue
                if c["hechas"]:
                    cuantas = min(len(lecciones), math.ceil(c["hechas"] * len(lecciones) / max(c["total"], c["hechas"], 1)))
                    for nivel in lecciones[:cuantas]:
                        session.add(CompletedLevel(usuario_id=usuario, nivel_id=nivel.id, estrellas=c["estrellas"], veces=1,
                                                   **({"completado_en": c["fecha"]} if c["fecha"] else {})))
                        restaurados += 1
                if c["cofre"]:
                    cofre = next((n for n in niveles if n.tipo == "cofre"), None)
                    if cofre:
                        estrellas, veces, fecha = c["cofre"]
                        session.add(CompletedLevel(usuario_id=usuario, nivel_id=cofre.id, estrellas=estrellas, veces=veces,
                                                   **({"completado_en": fecha} if fecha else {})))
                        restaurados += 1
        trofeo = next((n for s in stage.secciones for n in s.niveles if n.tipo == "trofeo"), None)
        if trofeo:
            for usuario in personas:
                if titulos and set(titulos) <= trofeos.get((usuario, stage.curso_id), set()):
                    session.add(CompletedLevel(usuario_id=usuario, nivel_id=trofeo.id, estrellas=3, veces=1))
                    restaurados += 1
    session.commit()
    return {"personas": len(personas), "niveles_restaurados": restaurados}
