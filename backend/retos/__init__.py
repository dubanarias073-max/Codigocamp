"""Catálogo de retos: un archivo .py por lenguaje dentro de esta carpeta (html.py, css.py, python.py...).

Estructura:  curso -> etapa -> sección -> lección -> unas 10 preguntas   (ver base.py para escribirlas)

    flask --app app check-retos          -> revisa los archivos y cuenta las preguntas (no usa la base de datos)
    flask --app app seed-retos           -> carga el catálogo en una base vacía
    flask --app app seed-retos --reset   -> borra el catálogo (y el progreso de niveles) y lo recarga tras editar

Para añadir un lenguaje nuevo: crea su archivo aquí, agrégalo a ORDEN y regístralo en
base de datos/crear_base.sql (tabla `cursos`).
"""
from importlib import import_module

from .base import PREGUNTAS_POR_LECCION, XP_ETAPA

# Mismo `slug` que la tabla `cursos`; el archivo se llama igual (javascript.py, csharp.py...).
ORDEN = ["html", "css", "javascript", "python", "sql", "bd", "typescript", "java", "csharp",
         "kotlin", "swift", "php", "ruby", "go", "rust", "c", "cpp"]


def cargar_cursos():
    """Devuelve {slug: [etapa, ...]} leyendo cada archivo de lenguaje."""
    return {slug: import_module(f"{__name__}.{slug}").ETAPAS for slug in ORDEN}


def resumen(cursos=None):
    """Cuenta etapas, secciones, lecciones y preguntas por curso (para `flask check-retos`)."""
    filas = {}
    for slug, etapas in (cursos or cargar_cursos()).items():
        secciones = [s for e in etapas for s in e["secciones"]]
        lecciones = [l for s in secciones for l in s["lecciones"]]
        filas[slug] = {
            "etapas": len(etapas), "secciones": len(secciones), "lecciones": len(lecciones),
            "preguntas": sum(len(l["retos"]) for l in lecciones),
            "cortas": [l["titulo"] for l in lecciones if len(l["retos"]) < PREGUNTAS_POR_LECCION],
        }
    return filas


TIPOS = {"opcion", "completar", "error", "ordenar", "codigo", "caso"}


def errores_catalogo(cursos=None):
    """Devuelve la lista de problemas que impedirían cargar o jugar los retos."""
    errores = []
    for slug, etapas in (cursos or cargar_cursos()).items():
        if not etapas:
            errores.append(f"{slug}: no tiene etapas")
        for e, etapa in enumerate(etapas, 1):
            if len(etapa["titulo"]) > 80 or len(etapa["descripcion"]) > 160:
                errores.append(f"{slug} etapa {e}: título (80) o descripción (160) demasiado largos")
            if not etapa["secciones"]:
                errores.append(f"{slug} etapa {e}: no tiene secciones")
            for s, seccion in enumerate(etapa["secciones"], 1):
                if len(seccion["titulo"]) > 80 or not seccion["lecciones"]:
                    errores.append(f"{slug} etapa {e} sección {s}: título largo o sin lecciones")
                for l, lec in enumerate(seccion["lecciones"], 1):
                    donde = f"{slug} · {etapa['titulo']} › {seccion['titulo']} › {lec['titulo']}"
                    if len(lec["titulo"]) > 80 or not lec["retos"]:
                        errores.append(f"{donde}: título largo o sin preguntas")
                    for n, r in enumerate(lec["retos"], 1):
                        errores += [f"{donde} #{n}: {m}" for m in _problemas_reto(r)]
    return errores


def _problemas_reto(r):
    if r["tipo"] not in TIPOS:
        return [f"tipo desconocido {r['tipo']!r}"]
    if not r["enunciado"].strip():
        return ["enunciado vacío"]
    if r["tipo"] == "opcion":
        o = r["opciones"]
        if len(o) < 2 or len(set(o)) != len(o):
            return ["las opciones deben ser 2 o más y distintas entre sí"]
        if r["respuesta"] not in o:
            return ["la respuesta no está entre las opciones"]
    elif r["tipo"] == "completar" and not r["respuesta"].strip():
        return ["falta la respuesta"]
    elif r["tipo"] == "error":
        lineas = r["codigo"].split("\n")
        if not r["respuesta"].isdigit() or not 1 <= int(r["respuesta"]) <= len(lineas):
            return ["la línea del error no existe en el código"]
    elif r["tipo"] == "ordenar" and len(r["datos"].get("piezas", [])) < 2:
        return ["faltan piezas para ordenar"]
    return []


def revisar_catalogo():
    """Imprime un resumen y devuelve 0 si todo está bien, 1 si hay errores."""
    cursos = cargar_cursos()
    filas = resumen(cursos)
    print(f"{'curso':<12}{'etapas':>7}{'secc.':>7}{'lecc.':>7}{'preg.':>7}   lecciones con menos de {PREGUNTAS_POR_LECCION} preguntas")
    for slug, f in filas.items():
        print(f"{slug:<12}{f['etapas']:>7}{f['secciones']:>7}{f['lecciones']:>7}{f['preguntas']:>7}   {len(f['cortas'])} de {f['lecciones']}")
    errores = errores_catalogo(cursos)
    for m in errores:
        print("ERROR:", m)
    print("Todo correcto." if not errores else f"{len(errores)} problema(s) por corregir.")
    return 1 if errores else 0


def secciones_del_camino(etapa):
    """Secciones tal como se ven en el camino: cada lección es su propia sección (con su práctica y su cofre).
    En los archivos de lenguaje puedes agrupar lecciones por tema; aquí se separan para tener más secciones."""
    plano = []
    for seccion in etapa["secciones"]:
        if len(seccion["lecciones"]) == 1 or seccion.get("agrupada"):   # agrupada: la sección conserva sus lecciones
            plano.append(seccion)
        else:
            plano += [{"titulo": lec["titulo"], "lecciones": [lec]} for lec in seccion["lecciones"]]
    return plano


def _esperado(cursos):
    etapas = sum(len(c) for c in cursos.values())
    secciones = sum(len(secciones_del_camino(e)) for c in cursos.values() for e in c)
    lecciones = sum(len(s["lecciones"]) for c in cursos.values() for e in c for s in e["secciones"])
    retos = sum(len(l["retos"]) for c in cursos.values() for e in c for s in e["secciones"] for l in s["lecciones"])
    # por sección: lecciones + 1 práctica + 1 cofre; por etapa: 1 trofeo (examen)
    return etapas, secciones, lecciones + secciones * 2 + etapas, retos


def poblar_catalogo(session, reset=False):
    """Carga el catálogo en una base vacía. Devuelve False si ya estaba completo."""
    from models import Challenge, Course, Level, Section, Stage

    cursos = cargar_cursos()
    problemas = errores_catalogo(cursos)
    if problemas:
        raise RuntimeError("Hay errores en los retos; ejecuta `flask --app app check-retos`:\n" + "\n".join(problemas[:10]))

    if reset:
        session.query(Stage).delete(synchronize_session=False)   # ON DELETE CASCADE limpia secciones, niveles y retos
        session.commit()

    esperado = _esperado(cursos)
    existente = (session.query(Stage).count(), session.query(Section).count(),
                 session.query(Level).count(), session.query(Challenge).count())
    if existente == esperado:
        return False
    if any(existente):
        raise RuntimeError("El catálogo está cargado a medias o desactualizado; usa `flask --app app seed-retos --reset`.")

    en_bd = {c.slug: c for c in session.query(Course).all()}
    faltan = sorted(set(cursos) - set(en_bd))
    if faltan:
        raise RuntimeError(f"Estos cursos no están en la tabla `cursos` (ejecuta crear_base.sql): {faltan}")

    for slug, etapas in cursos.items():
        for i, etapa in enumerate(etapas):
            stage = Stage(course=en_bd[slug], orden=i + 1, titulo=etapa["titulo"], descripcion=etapa["descripcion"])
            session.add(stage)
            planas = secciones_del_camino(etapa)
            for j, seccion in enumerate(planas):
                section = Section(etapa=stage, orden=j + 1, titulo=seccion["titulo"])
                session.add(section)
                for k, lec in enumerate(seccion["lecciones"]):
                    level = Level(seccion=section, orden=k + 1, titulo=lec["titulo"], tipo="leccion",
                                  xp=XP_ETAPA[min(i, len(XP_ETAPA) - 1)])
                    session.add(level)
                    for n, reto in enumerate(lec["retos"]):
                        session.add(Challenge(nivel=level, orden=n + 1, **reto))
                n = len(seccion["lecciones"])
                session.add(Level(seccion=section, orden=n + 1, titulo=f"Práctica: {seccion['titulo']}"[:80], tipo="practica", xp=10))
                session.add(Level(seccion=section, orden=n + 2, titulo=f"Cofre: {seccion['titulo']}"[:80], tipo="cofre", xp=0))
                if j == len(planas) - 1:   # al final de la etapa: examen de toda la etapa
                    session.add(Level(seccion=section, orden=n + 3, titulo=f"Examen: {etapa['titulo']}"[:80], tipo="trofeo", xp=30))
    session.commit()
    return True
