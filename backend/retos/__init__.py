"""Catálogo de retos: un archivo .py por lenguaje dentro de esta carpeta (html.py, css.py, python.py...).

Estructura:  curso -> etapa -> sección -> lección -> preguntas variadas   (ver base.py para escribirlas)

    flask --app app check-retos          -> revisa los archivos y cuenta las preguntas (no usa la base de datos)
    flask --app app seed-retos           -> carga el catálogo en una base vacía
    flask --app app sync-retos           -> actualiza y añade contenido compatible, conservando el progreso
    flask --app app seed-retos --reset   -> borra el catálogo y el progreso, y lo recarga tras editar

Para añadir un lenguaje nuevo: crea su archivo aquí, agrégalo a ORDEN y regístralo en
base de datos/crear_base.sql (tabla `cursos`).
"""
from importlib import import_module

from .base import PREGUNTAS_POR_LECCION, XP_ETAPA

# Mismo `slug` que la tabla `cursos`; el archivo se llama igual (javascript.py, csharp.py...).
ORDEN = ["html", "css", "javascript", "python", "sql", "bd", "typescript", "java", "csharp",
         "kotlin", "swift", "php", "ruby", "go", "rust", "c", "cpp", "terminal", "git", "github", "docker", "node", "nosql", "react", "reactnative", "lua", "r"]

# Retos agregados desde el panel de administrador a una lección del código: van con orden >= ORDEN_ADMIN y la
# sincronización (sync-retos) no los toca. Los retos del código que el administrador edita u oculta quedan marcados
# en la tabla retos_admin y la sincronización tampoco los pisa.
ORDEN_ADMIN = 500


def _marcas_admin(session):
    from models import RetoAdmin
    try:
        return {r.reto_id for r in session.query(RetoAdmin).filter_by(editado=True).all()}
    except Exception:  # noqa: BLE001 - tabla aún no creada
        session.rollback()
        return set()


# Cursos que se crean solos en la tabla `cursos` si faltan (los demás vienen de codigocamp.sql).
CURSOS_NUEVOS = {
    "terminal": dict(nombre="Terminales", tipo="lenguaje", sigla="$_", color="#4ade80", descripcion="Bash, PowerShell y CMD", orden=18),
    "git": dict(nombre="Git", tipo="lenguaje", sigla="GIT", color="#f97316", descripcion="Control de versiones: de cero a avanzado", orden=19),
    "docker": dict(nombre="Docker", tipo="lenguaje", sigla="DK", color="#38bdf8", descripcion="Contenedores para tus apps y bases de datos", orden=20),
    "node": dict(nombre="Node.js", tipo="lenguaje", sigla="NODE", color="#84cc16", descripcion="JavaScript en el servidor: npm, Express y APIs", orden=21),
    "github": dict(nombre="GitHub", tipo="lenguaje", sigla="GH", color="#a78bfa", descripcion="Repositorios, equipo, Actions, Pages y seguridad", orden=22),
    "nosql": dict(nombre="NoSQL", tipo="bd", sigla="NoSQL", color="#22c55e", descripcion="MongoDB, Redis, Firestore, grafos y más", orden=23),
    "react": dict(nombre="React", tipo="lenguaje", sigla="RE", color="#61dafb", descripcion="Interfaces con componentes, hooks, rutas y Next.js", orden=24),
    "reactnative": dict(nombre="React Native", tipo="lenguaje", sigla="RN", color="#38bdf8", descripcion="Apps para Android y iPhone con React y Expo", orden=25),
    "lua": dict(nombre="Lua", tipo="lenguaje", sigla="LUA", color="#818cf8", descripcion="El lenguaje de Roblox y los videojuegos", orden=26),
    "r": dict(nombre="R", tipo="lenguaje", sigla="R", color="#60a5fa", descripcion="Estadística y análisis de datos", orden=27),
}


def asegurar_cursos(session):
    """Crea en la tabla `cursos` los cursos nuevos que falten. Devuelve los slugs creados."""
    from models import Course
    existentes = {c.slug: c for c in session.query(Course).all()}
    creados, cambios = [], False
    for slug, datos in CURSOS_NUEVOS.items():
        if slug not in existentes:
            session.add(Course(slug=slug, activo=True, **datos))
            creados.append(slug)
        else:   # nombre y descripción siguen a este archivo (p. ej. «Git y GitHub» pasó a «Git» al crear el curso GitHub)
            c = existentes[slug]
            from models import CursoAdmin
            marca = session.get(CursoAdmin, c.id)
            if marca and marca.editado:   # el administrador lo editó en el panel: se respetan sus textos
                continue
            for campo in ("nombre", "descripcion", "sigla", "color"):
                if getattr(c, campo) != datos[campo]:
                    setattr(c, campo, datos[campo]); cambios = True
    if creados or cambios:
        session.commit()
    return creados


def _cargar_curso(session, course, slug, etapas, desde=0):
    """Carga las etapas (desde la número `desde`, contando desde 0) con sus secciones, niveles y retos."""
    from models import Challenge, Level, Section, Stage
    for i, etapa in enumerate(etapas):
        if i < desde:
            continue
        stage = Stage(course=course, orden=i + 1, titulo=etapa["titulo"], descripcion=etapa["descripcion"])
        session.add(stage)
        planas = secciones_del_camino(etapa)
        for j, seccion in enumerate(planas):
            section = Section(etapa=stage, orden=j + 1, titulo=seccion["titulo"])
            session.add(section)
            specs = _especificaciones_niveles(slug, i, etapa, seccion, j + 1, len(planas))
            for k, spec in enumerate(specs, 1):
                level = Level(seccion=section, orden=k, titulo=spec["titulo"], tipo=spec["tipo"], xp=spec["xp"])
                session.add(level)
                for n, reto in enumerate(spec["retos"], 1):
                    session.add(Challenge(nivel=level, orden=n, **reto))

# Cursos cuyo camino SÍ lleva repaso (ninguno por ahora). Para activarlo en uno: añade su slug y pasa repaso=True a construir_etapas.
CON_REPASO = set()   # ningún curso lleva repaso (ni lección «Repaso de …» ni nodo «Práctica de repaso»)


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


TIPOS = {"opcion", "completar", "error", "ordenar", "codigo", "caso", "parejas", "armar"}


def errores_catalogo(cursos=None):
    """Devuelve la lista de problemas que impedirían cargar o jugar los retos."""
    errores = []
    for slug, etapas in (cursos or cargar_cursos()).items():
        vistos = {}
        for etapa in etapas:
            for seccion in etapa["secciones"]:
                for lec in seccion["lecciones"]:
                    for r in lec["retos"]:
                        clave = (" ".join(r["enunciado"].casefold().split()), r["codigo"], tuple(r["datos"].get("piezas", [])),
                                 tuple(map(tuple, r["datos"].get("pares", []))), tuple(r["datos"].get("solucion", [])))
                        if clave in vistos:
                            errores.append(f"{slug} · {seccion['titulo']} › {lec['titulo']}: repite una pregunta de «{vistos[clave]}» (ninguna pregunta se repite en el curso)")
                        vistos.setdefault(clave, seccion["titulo"])
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
                if not seccion.get("un_tipo") and len({r["tipo"] for lec in seccion["lecciones"] for r in lec["retos"]}) < 2:
                    errores.append(f"{slug} etapa {e} sección {s}: necesita más de un tipo de pregunta")
                for l, lec in enumerate(seccion["lecciones"], 1):
                    donde = f"{slug} · {etapa['titulo']} › {seccion['titulo']} › {lec['titulo']}"
                    if len(lec["titulo"]) > 80 or not lec["retos"]:
                        errores.append(f"{donde}: título largo o sin preguntas")
                    if len(lec["retos"]) < PREGUNTAS_POR_LECCION:
                        errores.append(f"{donde}: tiene menos de {PREGUNTAS_POR_LECCION} preguntas")
                    enunciados, respuestas = {}, {}

                    for n, r in enumerate(lec["retos"], 1):
                        prefijo = f"{donde} #{n}"
                        errores += [f"{prefijo}: {m}" for m in _problemas_reto(r)]
                        enunciado = " ".join(r["enunciado"].casefold().split()) + "|" + r["codigo"] + "|" + str(r["datos"].get("pares", ""))
                        if enunciado in enunciados:
                            errores.append(f"{prefijo}: repite el enunciado de la pregunta #{enunciados[enunciado]}")
                        else:
                            enunciados[enunciado] = n
                        if r["tipo"] in {"opcion", "completar"}:
                            for respuesta in r["respuesta"].split("|"):
                                clave = " ".join(respuesta.casefold().split())
                                if not clave:
                                    continue
                                if clave in respuestas:
                                    errores.append(f"{prefijo}: repite la respuesta correcta de la pregunta #{respuestas[clave]}")
                                else:
                                    respuestas[clave] = n
    return errores


def _problemas_reto(r):
    if r["tipo"] not in TIPOS:
        return [f"tipo desconocido {r['tipo']!r}"]
    if not r["enunciado"].strip():
        return ["enunciado vacío"]
    if r["tipo"] in {"opcion", "completar", "error", "ordenar"} and not r["explicacion"].strip():
        return ["falta explicar la respuesta correcta"]
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
    elif r["tipo"] == "parejas":
        pares = r["datos"].get("pares", [])
        if len(pares) < 3 or len({a for a, _ in pares}) != len(pares) or len({b for _, b in pares}) != len(pares):
            return ["las parejas deben ser 3 o más, sin repetir textos"]
    elif r["tipo"] == "armar":
        sol, trampas = r["datos"].get("solucion", []), r["datos"].get("trampas", [])
        if len(sol) < 2 or "▁▁▁" not in r["codigo"]:
            return ["la línea para armar necesita 2 fichas o más y el hueco ▁▁▁ en el código"]
        if set(trampas) & set(sol):
            return ["una ficha trampa también está en la solución"]
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


def _especificaciones_niveles(slug, orden_etapa, etapa, seccion, orden_seccion, total_secciones):
    """Produce el mismo orden de niveles para cargar un catálogo nuevo o sincronizarlo."""
    xp = XP_ETAPA[min(orden_etapa, len(XP_ETAPA) - 1)]
    niveles = [{"titulo": lec["titulo"], "tipo": "leccion", "xp": xp, "retos": lec["retos"]}
               for lec in seccion["lecciones"]]
    if slug in CON_REPASO:
        niveles.append({"titulo": f"Práctica: {seccion['titulo']}"[:80], "tipo": "practica", "xp": 10, "retos": []})
    niveles.append({"titulo": f"Cofre: {seccion['titulo']}"[:80], "tipo": "cofre", "xp": 0, "retos": []})
    if orden_seccion == total_secciones:
        niveles.append({"titulo": f"Examen: {etapa['titulo']}"[:80], "tipo": "trofeo", "xp": 30, "retos": []})
    return niveles


def sincronizar_catalogo(session):
    """Actualiza el contenido y admite expansiones aditivas conservando el progreso existente."""
    from models import Challenge, Course, Level, Section

    cursos = cargar_cursos()
    problemas = errores_catalogo(cursos)
    if problemas:
        raise RuntimeError("Hay errores en los retos; ejecuta `flask --app app check-retos`:\n" + "\n".join(problemas[:10]))

    asegurar_cursos(session)
    en_bd = {curso.slug: curso for curso in session.query(Course).all()}
    faltan = sorted(set(cursos) - set(en_bd))
    if faltan:
        raise RuntimeError(f"Faltan cursos en la base de datos: {faltan}")

    # Cursos nuevos (sin etapas todavía): se cargan enteros, no hay progreso que proteger.
    nuevos = [slug for slug in cursos if not list(en_bd[slug].etapas)]
    for slug in nuevos:
        _cargar_curso(session, en_bd[slug], slug, cursos[slug])
    if nuevos:
        session.commit()
        en_bd = {curso.slug: curso for curso in session.query(Course).all()}

    # Cursos que ganaron etapas nuevas al final (p. ej. de 3 a 5): se agregan sin tocar el progreso de las existentes.
    ampliados = []
    for slug, etapas in cursos.items():
        if slug in nuevos:
            continue
        actuales = sorted(en_bd[slug].etapas, key=lambda e: e.orden)
        if len(actuales) < len(etapas) and all(e.titulo == etapas[i]["titulo"] for i, e in enumerate(actuales)):
            _cargar_curso(session, en_bd[slug], slug, etapas, desde=len(actuales))
            ampliados.append(slug)
    if ampliados:
        session.commit()
        en_bd = {curso.slug: curso for curso in session.query(Course).all()}

    planes = []
    for slug, etapas in cursos.items():
        if slug in nuevos:
            continue
        db_etapas = list(en_bd[slug].etapas)
        if len(db_etapas) != len(etapas):
            raise RuntimeError(f"{slug}: cambió la cantidad de etapas; no se sincronizó para proteger el progreso. Si el camino cambió de estructura, usa `flask --app app migrar-camino` (traslada el progreso).")
        for i, (etapa, db_etapa) in enumerate(zip(etapas, db_etapas)):
            planas = secciones_del_camino(etapa)
            db_secciones = list(db_etapa.secciones)
            if db_etapa.orden != i + 1 or len(db_secciones) > len(planas):
                raise RuntimeError(f"{slug} etapa {i + 1}: cambió la estructura; no se sincronizó para proteger el progreso. Si el camino cambió de estructura, usa `flask --app app migrar-camino` (traslada el progreso).")
            expandiendo_secciones = len(db_secciones) < len(planas)
            plan_etapa = {"slug": slug, "etapa": etapa, "db_etapa": db_etapa, "secciones": []}
            for j, seccion in enumerate(planas, 1):
                specs = _especificaciones_niveles(slug, i, etapa, seccion, j, len(planas))
                db_seccion = db_secciones[j - 1] if j <= len(db_secciones) else None
                if db_seccion and (db_seccion.orden != j or
                                   (expandiendo_secciones and db_seccion.titulo != seccion["titulo"])):
                    raise RuntimeError(f"{slug} sección {j}: no coincide con la ruta actual; no se sincronizó para proteger el progreso. Si el camino cambió de estructura, usa `flask --app app migrar-camino` (traslada el progreso).")

                niveles = [None] * len(specs)
                if db_seccion:
                    por_tipo = {}
                    for db_nivel in db_seccion.niveles:
                        if db_nivel.tipo != "trofeo":
                            por_tipo.setdefault(db_nivel.tipo, []).append(db_nivel)
                    esperados = {}
                    for spec in specs:
                        if spec["tipo"] != "trofeo":
                            esperados[spec["tipo"]] = esperados.get(spec["tipo"], 0) + 1
                    if any(len(niveles_tipo) > esperados.get(tipo, 0) for tipo, niveles_tipo in por_tipo.items()):
                        raise RuntimeError(f"{slug} sección {j}: se quitarían niveles existentes; no se sincronizó para proteger el progreso. Si el camino cambió de estructura, usa `flask --app app migrar-camino` (traslada el progreso).")
                    if len(db_seccion.niveles) < len(specs) and db_seccion.titulo != seccion["titulo"]:
                        raise RuntimeError(f"{slug} sección {j}: el título debe coincidir para agregar niveles sin reasignar el progreso.")
                    usados = {}
                    for k, spec in enumerate(specs):
                        if spec["tipo"] == "trofeo":
                            continue
                        n = usados.get(spec["tipo"], 0)
                        disponibles = por_tipo.get(spec["tipo"], [])
                        if n < len(disponibles):
                            niveles[k] = disponibles[n]
                        usados[spec["tipo"]] = n + 1
                plan_etapa["secciones"].append({
                    "seccion": seccion, "db_seccion": db_seccion, "specs": specs, "niveles": niveles,
                })

            trofeos_actuales = [
                nivel for db_seccion in db_secciones for nivel in db_seccion.niveles
                if nivel.tipo == "trofeo"
            ]
            trofeos_objetivo = [
                (plan_seccion, k) for plan_seccion in plan_etapa["secciones"]
                for k, spec in enumerate(plan_seccion["specs"]) if spec["tipo"] == "trofeo"
            ]
            if len(trofeos_actuales) > len(trofeos_objetivo):
                raise RuntimeError(f"{slug} etapa {i + 1}: se quitarían trofeos; no se sincronizó para proteger el progreso. Si el camino cambió de estructura, usa `flask --app app migrar-camino` (traslada el progreso).")
            for nivel, (plan_seccion, k) in zip(trofeos_actuales, trofeos_objetivo):
                plan_seccion["niveles"][k] = nivel
            planes.append(plan_etapa)

    cambio = bool(nuevos or ampliados)   # cursos nuevos o etapas agregadas al final también son cambios
    editados = _marcas_admin(session)
    try:
        for plan_etapa in planes:
            etapa = plan_etapa["etapa"]
            db_etapa = plan_etapa["db_etapa"]
            for campo, valor in (("titulo", etapa["titulo"]), ("descripcion", etapa["descripcion"])):
                if getattr(db_etapa, campo) != valor:
                    setattr(db_etapa, campo, valor)
                    cambio = True
            for orden_seccion, plan_seccion in enumerate(plan_etapa["secciones"], 1):
                if plan_seccion["db_seccion"] is None:
                    plan_seccion["db_seccion"] = Section(
                        etapa=db_etapa, orden=orden_seccion,
                        titulo=plan_seccion["seccion"]["titulo"],
                    )
                    session.add(plan_seccion["db_seccion"])
                    cambio = True
        session.flush()

        for plan_etapa in planes:
            for plan_seccion in plan_etapa["secciones"]:
                db_seccion = plan_seccion["db_seccion"]
                db_niveles = list(db_seccion.niveles)
                if any(nivel is not None and (
                    nivel.orden != k + 1 or nivel.seccion_id != db_seccion.id
                ) for k, nivel in enumerate(plan_seccion["niveles"])):
                    mayor = max([nivel.orden for nivel in db_niveles] +
                                [len(plan_seccion["specs"]), 0])
                    inicio_temporal = mayor + len(db_niveles) + 1
                    if inicio_temporal + len(db_niveles) > 32767:
                        raise RuntimeError("No hay espacio temporal para reordenar niveles sin perder sus IDs.")
                    for n, nivel in enumerate(db_niveles):
                        nivel.orden = inicio_temporal + n
                    session.flush()

                seccion = plan_seccion["seccion"]
                if db_seccion.titulo != seccion["titulo"]:
                    db_seccion.titulo = seccion["titulo"]
                    cambio = True
                for k, spec in enumerate(plan_seccion["specs"], 1):
                    db_nivel = plan_seccion["niveles"][k - 1]
                    if db_nivel is None:
                        db_nivel = Level(
                            seccion=db_seccion, orden=k, titulo=spec["titulo"],
                            tipo=spec["tipo"], xp=spec["xp"],
                        )
                        session.add(db_nivel)
                        cambio = True
                        for n, reto in enumerate(spec["retos"], 1):
                            session.add(Challenge(nivel=db_nivel, orden=n, **reto))
                        continue
                    if db_nivel.seccion_id != db_seccion.id:
                        db_nivel.seccion = db_seccion
                        cambio = True
                    for campo, valor in (("orden", k), ("titulo", spec["titulo"]), ("tipo", spec["tipo"]), ("xp", spec["xp"])):
                        if getattr(db_nivel, campo) != valor:
                            setattr(db_nivel, campo, valor)
                            cambio = True
                    db_retos = [r for r in db_nivel.retos if r.orden < ORDEN_ADMIN]   # los del panel no se tocan
                    for n, reto in enumerate(spec["retos"], 1):
                        if n <= len(db_retos):
                            db_reto = db_retos[n - 1]
                            for campo, valor in ({} if db_reto.id in editados else reto).items():
                                if getattr(db_reto, campo) != valor:
                                    setattr(db_reto, campo, valor)
                                    cambio = True
                            if db_reto.orden != n:
                                db_reto.orden = n
                                cambio = True
                        else:
                            session.add(Challenge(nivel=db_nivel, orden=n, **reto))
                            cambio = True
                    for db_reto in db_retos[len(spec["retos"]):]:
                        session.delete(db_reto)
                        cambio = True
        if cambio:
            session.commit()
        return cambio
    except Exception:
        session.rollback()
        raise


def _esperado(cursos):
    etapas = sum(len(c) for c in cursos.values())
    secciones = sum(len(secciones_del_camino(e)) for c in cursos.values() for e in c)
    lecciones = sum(len(s["lecciones"]) for c in cursos.values() for e in c for s in e["secciones"])
    retos = sum(len(l["retos"]) for c in cursos.values() for e in c for s in e["secciones"] for l in s["lecciones"])
    # por sección: lecciones + 1 cofre (+ 1 práctica si el curso lleva repaso); por etapa: 1 trofeo (examen)
    practicas = sum(len(secciones_del_camino(e)) for slug, c in cursos.items() if slug in CON_REPASO for e in c)
    return etapas, secciones, lecciones + secciones + practicas + etapas, retos


def poblar_catalogo(session, reset=False):
    """Carga el catálogo en una base vacía. Devuelve False si ya estaba completo."""
    from models import Challenge, Course, Level, Section, Stage

    cursos = cargar_cursos()
    problemas = errores_catalogo(cursos)
    if problemas:
        raise RuntimeError("Hay errores en los retos; ejecuta `flask --app app check-retos`:\n" + "\n".join(problemas[:10]))

    if reset:   # solo los cursos del código: los creados en el panel de administrador se conservan
        ids = [c.id for c in session.query(Course).filter(Course.slug.in_(list(cursos))).all()]
        session.query(Stage).filter(Stage.curso_id.in_(ids)).delete(synchronize_session=False)   # CASCADE limpia el resto
        session.commit()

    esperado = _esperado(cursos)
    # Solo cuenta lo del código: los cursos creados en el panel y los retos agregados en el panel no son «catálogo»
    codigo = session.query(Course.id).filter(Course.slug.in_(list(cursos)))
    etapas_q = session.query(Stage).filter(Stage.curso_id.in_(codigo))
    secciones_q = session.query(Section).join(Stage).filter(Stage.curso_id.in_(codigo))
    niveles_q = session.query(Level).join(Section).join(Stage).filter(Stage.curso_id.in_(codigo))
    retos_q = session.query(Challenge).join(Level).join(Section).join(Stage).filter(Stage.curso_id.in_(codigo), Challenge.orden < ORDEN_ADMIN)
    existente = (etapas_q.count(), secciones_q.count(), niveles_q.count(), retos_q.count())
    if existente == esperado:
        return False
    if any(existente):
        raise RuntimeError("El catálogo está cargado a medias o desactualizado; prueba `flask --app app sync-retos`. `seed-retos --reset` borra el progreso.")

    asegurar_cursos(session)
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
                specs = _especificaciones_niveles(slug, i, etapa, seccion, j + 1, len(planas))
                for k, spec in enumerate(specs, 1):
                    level = Level(seccion=section, orden=k, titulo=spec["titulo"], tipo=spec["tipo"], xp=spec["xp"])
                    session.add(level)
                    for n, reto in enumerate(spec["retos"], 1):
                        session.add(Challenge(nivel=level, orden=n, **reto))
    session.commit()
    return True
