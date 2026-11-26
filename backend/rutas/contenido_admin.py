"""Contenido editable desde el panel de administrador: cosméticos diseñados, imágenes, cursos (lenguajes), su camino
de retos (etapas → secciones → lecciones → retos) y las lecciones de Aprende.

Reglas para no romper el catálogo del código (backend/retos/*.py, que se sincroniza con `flask sync-retos`):
- Cursos creados en el panel: se editan por completo (estructura y retos).
- Cursos del código: se les pueden AGREGAR retos a sus lecciones (orden >= ORDEN_ADMIN) y editar u ocultar sus retos
  (quedan marcados en retos_admin y la sincronización los respeta). Su estructura (etapas, secciones, niveles) la
  manda el código, porque cambiarla movería el progreso de los estudiantes.
"""
import hashlib
import re
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from sqlalchemy import func

from models import (Challenge, Course, CursoAdmin, CosmeticoAdmin, LeccionAprende, Level, RetoAdmin, Section, Stage, StoreItem,
                    db)
from servicios.admin import requiere_admin
from utilidades import api_error, json_body



def _sin_tildes(texto):
    """«Aro galáctico» → «aro galactico» (para claves internas)."""
    import unicodedata
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


bp = Blueprint("contenido_admin", __name__)

MOTORES = ("web", "js", "py", "sql", "ts", "srv", "ver", "react")
TIPOS_CURSO = ("lenguaje", "web", "bd")
TIPOS_NIVEL = ("leccion", "practica", "cofre", "trofeo")
TIPOS_RETO = ("opcion", "completar", "error", "ordenar", "parejas", "armar")
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


@bp.before_app_request
def _refrescar_catalogo():
    """Cada proceso vuelve a leer los cosméticos y ajustes del panel cada pocos segundos (sin reiniciar el servidor)."""
    if request.path.startswith("/api/"):
        from servicios.catalogo_admin import refrescar
        refrescar()


# ======================================================================================== públicos ====
@bp.get("/api/cosmeticos/disenos/")
def disenos():
    from servicios.catalogo_admin import disenos_publicos
    r = jsonify(disenos=disenos_publicos())
    r.headers["Cache-Control"] = "public, max-age=60"
    return r


@bp.get("/api/aprende/<slug>/")
def aprende_publico(slug):
    filas = LeccionAprende.query.filter_by(curso_slug=slug[:30]).order_by(LeccionAprende.id).all()
    return jsonify(lecciones=[_leccion(x) for x in filas])


def _carpeta_img():
    return Path(current_app.config["ALMACEN_ARCHIVOS"]) / "admin_img"   # imágenes del panel (fondos de la tienda)


@bp.get("/api/admin-img/<nombre>")
def imagen(nombre):
    if not re.fullmatch(r"[a-f0-9]{16,64}\.(?:png|jpe?g|webp|gif)", nombre):
        return api_error("No encontrado.", 404)
    r = send_from_directory(_carpeta_img(), nombre, max_age=31536000)
    r.headers["X-Content-Type-Options"] = "nosniff"
    return r


# ======================================================================================== imágenes ====
FIRMAS = {b"\x89PNG\r\n\x1a\n": "png", b"\xff\xd8\xff": "jpg", b"GIF87a": "gif", b"GIF89a": "gif"}


@bp.post("/api/admin/imagen")
@requiere_admin
def subir_imagen():
    """Imagen para un fondo de la tienda (PNG, JPG, WEBP o GIF de hasta 4 MB). Pasa por el antivirus."""
    datos = request.get_data(cache=False)[: 4 * 1024 * 1024 + 1]
    if len(datos) > 4 * 1024 * 1024:
        return api_error("La imagen pesa más de 4 MB.", 413)
    ext = next((e for f, e in FIRMAS.items() if datos.startswith(f)), None)
    if not ext and datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        ext = "webp"
    if not ext:
        return api_error("Sube una imagen PNG, JPG, WEBP o GIF.")
    carpeta = _carpeta_img()
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"{hashlib.sha256(datos).hexdigest()[:32]}.{ext}"
    destino = carpeta / nombre
    tmp = carpeta / (nombre + ".tmp")
    tmp.write_bytes(datos)
    from servicios.antivirus import revisar_archivo
    motivo = revisar_archivo(str(tmp), f"imagen.{ext}")
    if motivo:
        tmp.unlink(missing_ok=True)
        return api_error(f"🛡️ El antivirus bloqueó la imagen: {motivo}.", 422)
    tmp.replace(destino)
    return jsonify(url=f"/api/admin-img/{nombre}"), 201


# ======================================================================================== cosméticos ====
def _cosmetico(c):
    item = StoreItem.query.filter_by(clave=c.clave).first()
    return {"id": c.id, "clave": c.clave, "tipo": c.tipo, "nombre": c.nombre, "descripcion": c.descripcion, "precio": c.precio,
            "rareza": c.rareza, "diseno": c.diseno or {}, "activo": c.activo, "articulo_id": item.id if item else None}


@bp.get("/api/admin/cosmeticos")
@requiere_admin
def cosmeticos_admin():
    """Cosméticos diseñados en el panel + el catálogo de fábrica (para regalar y editar precios)."""
    from cosmeticos import POR_CLAVE
    from servicios.catalogo_admin import ANIMACIONES_FONDO, ESTILOS_FONDO, FORMAS, TIPOS_DISENABLES
    return jsonify(disenados=[_cosmetico(c) for c in CosmeticoAdmin.query.order_by(CosmeticoAdmin.id.desc()).all()],
                   catalogo=[{"clave": c["clave"], "tipo": c["tipo"], "nombre": c["nombre"], "rareza": c["rareza"]} for c in POR_CLAVE.values()],
                   opciones={"tipos": TIPOS_DISENABLES, "animaciones": ANIMACIONES_FONDO, "estilos": ESTILOS_FONDO, "formas": FORMAS})


def _datos_cosmetico(data, tipo):
    from servicios.catalogo_admin import RAREZAS, limpiar_diseno
    nombre = " ".join(str(data.get("nombre", "")).split())
    if not 2 <= len(nombre) <= 50:
        return None, "El nombre debe tener entre 2 y 50 caracteres."
    try:
        precio = int(data.get("precio"))
    except (TypeError, ValueError):
        return None, "Precio no válido."
    if not 0 <= precio <= 1_000_000:
        return None, "El precio debe estar entre 0 y 1.000.000 diamantes."
    return {"nombre": nombre, "descripcion": " ".join(str(data.get("descripcion", "")).split())[:200] or nombre, "precio": precio,
            "rareza": data.get("rareza") if data.get("rareza") in RAREZAS else "comun",
            "diseno": limpiar_diseno(tipo, data.get("diseno")), "activo": bool(data.get("activo", True))}, None


@bp.post("/api/admin/cosmeticos")
@requiere_admin
def crear_cosmetico():
    from servicios.catalogo_admin import TIPOS_DISENABLES, refrescar
    data = json_body()
    if isinstance(data, tuple):
        return data
    tipo = data.get("tipo")
    if tipo not in TIPOS_DISENABLES:
        return api_error("Tipo de cosmético no válido.")
    campos, error = _datos_cosmetico(data, tipo)
    if error:
        return api_error(error)
    base = re.sub(r"[^a-z0-9]+", "_", _sin_tildes(campos["nombre"])).strip("_")[:18] or tipo
    clave, n = f"a_{base}", 1
    while StoreItem.query.filter_by(clave=clave).first() or CosmeticoAdmin.query.filter_by(clave=clave).first():
        n += 1
        clave = f"a_{base[:15]}_{n}"
    c = CosmeticoAdmin(clave=clave, tipo=tipo, **campos)
    db.session.add(c)
    orden = min((db.session.query(func.max(StoreItem.orden)).scalar() or 0) + 1, 32000)
    db.session.add(StoreItem(clave=clave, nombre=c.nombre, descripcion=c.descripcion, icono=tipo, moneda="diamante", precio=c.precio,
                             categoria="diamante", orden=orden, activo=c.activo))
    db.session.commit()
    refrescar(forzar=True)
    return jsonify(cosmetico=_cosmetico(c)), 201


@bp.patch("/api/admin/cosmeticos/<int:cid>")
@requiere_admin
def editar_cosmetico(cid):
    from servicios.catalogo_admin import refrescar
    data = json_body()
    if isinstance(data, tuple):
        return data
    c = db.session.get(CosmeticoAdmin, cid)
    if not c:
        return api_error("Ese cosmético no existe.", 404)
    campos, error = _datos_cosmetico({**_cosmetico(c), **data}, c.tipo)
    if error:
        return api_error(error)
    for k, v in campos.items():
        setattr(c, k, v)
    item = StoreItem.query.filter_by(clave=c.clave).first()
    if item:
        item.nombre, item.descripcion, item.precio, item.activo = c.nombre, c.descripcion, c.precio, c.activo
    db.session.commit()
    refrescar(forzar=True)
    return jsonify(cosmetico=_cosmetico(c))


# ======================================================================================== cursos ====
def _codigo_slugs():
    from retos import ORDEN
    return set(ORDEN)


def _curso(c, codigo=None):
    codigo = codigo if codigo is not None else _codigo_slugs()
    marca = db.session.get(CursoAdmin, c.id)
    etapas = Stage.query.filter_by(curso_id=c.id).count()
    niveles = db.session.query(func.count(Level.id)).join(Section).join(Stage).filter(Stage.curso_id == c.id).scalar() or 0
    retos = db.session.query(func.count(Challenge.id)).join(Level).join(Section).join(Stage).filter(Stage.curso_id == c.id).scalar() or 0
    return {"id": c.id, "slug": c.slug, "nombre": c.nombre, "sigla": c.sigla, "color": c.color, "tipo": c.tipo, "descripcion": c.descripcion,
            "orden": c.orden, "activo": c.activo, "origen": "codigo" if c.slug in codigo else "panel",
            "motor": marca.motor if marca else None, "editado": bool(marca and marca.editado),
            "etapas": etapas, "niveles": niveles, "retos": retos,
            "lecciones_aprende": LeccionAprende.query.filter_by(curso_slug=c.slug).count()}


@bp.get("/api/admin/cursos")
@requiere_admin
def cursos():
    codigo = _codigo_slugs()
    return jsonify(cursos=[_curso(c, codigo) for c in Course.query.order_by(Course.orden, Course.nombre).all()],
                   motores=MOTORES, tipos=TIPOS_CURSO)


def _datos_curso(data, nuevo):
    out = {}
    if nuevo or "nombre" in data:
        nombre = " ".join(str(data.get("nombre", "")).split())
        if not 1 <= len(nombre) <= 40:
            return None, "El nombre debe tener entre 1 y 40 caracteres."
        out["nombre"] = nombre
    if nuevo or "sigla" in data:
        sigla = str(data.get("sigla", "")).strip()[:6]
        if not sigla:
            return None, "Escribe una sigla corta (por ejemplo PY o JS)."
        out["sigla"] = sigla
    if "color" in data or nuevo:
        out["color"] = data.get("color") if _HEX.match(str(data.get("color", ""))) else "#4ade80"
    if "descripcion" in data or nuevo:
        out["descripcion"] = " ".join(str(data.get("descripcion", "")).split())[:120]
    if "tipo" in data or nuevo:
        out["tipo"] = data.get("tipo") if data.get("tipo") in TIPOS_CURSO else "lenguaje"
    if "orden" in data:
        try:
            out["orden"] = max(0, min(999, int(data["orden"])))
        except (TypeError, ValueError):
            pass
    if "activo" in data:
        out["activo"] = bool(data["activo"])
    return out, None


@bp.post("/api/admin/cursos")
@requiere_admin
def crear_curso():
    """Lenguaje nuevo: aparece en Aprende (con sus lecciones del panel) y en el camino de retos."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    slug = str(data.get("slug", "")).strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_-]{1,29}", slug):
        return api_error("El identificador debe ir en minúsculas, sin espacios (por ejemplo «dart» o «flutter»).")
    if Course.query.filter_by(slug=slug).first() or slug in _codigo_slugs():
        return api_error("Ya existe un curso con ese identificador.")
    campos, error = _datos_curso(data, True)
    if error:
        return api_error(error)
    campos.setdefault("orden", min(999, (db.session.query(func.max(Course.orden)).scalar() or 0) + 1))
    campos["activo"] = bool(data.get("activo", True))
    c = Course(slug=slug, **campos)
    db.session.add(c)
    db.session.flush()
    db.session.add(CursoAdmin(curso_id=c.id, motor=data.get("motor") if data.get("motor") in MOTORES else "ver", creado=True, editado=True))
    if data.get("estructura", True):   # primera etapa y sección listas para empezar a crear lecciones
        etapa = Stage(curso_id=c.id, orden=1, titulo="Primeros pasos", descripcion=f"Lo básico de {c.nombre}")
        db.session.add(etapa)
        db.session.flush()
        db.session.add(Section(etapa_id=etapa.id, orden=1, titulo="Introducción"))
    db.session.commit()
    return jsonify(curso=_curso(c)), 201


@bp.patch("/api/admin/cursos/<int:cid>")
@requiere_admin
def editar_curso(cid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    c = db.session.get(Course, cid)
    if not c:
        return api_error("Ese curso no existe.", 404)
    campos, error = _datos_curso(data, False)
    if error:
        return api_error(error)
    for k, v in campos.items():
        setattr(c, k, v)
    marca = db.session.get(CursoAdmin, c.id) or CursoAdmin(curso_id=c.id, creado=False)
    marca.editado = True
    if data.get("motor") in MOTORES:
        marca.motor = data["motor"]
    db.session.add(marca)
    db.session.commit()
    return jsonify(curso=_curso(c))


@bp.delete("/api/admin/cursos/<int:cid>")
@requiere_admin
def borrar_curso(cid):
    c = db.session.get(Course, cid)
    if not c:
        return api_error("Ese curso no existe.", 404)
    if c.slug in _codigo_slugs():
        c.activo = False   # los del código no se borran (el progreso de los estudiantes vive ahí): se ocultan
        db.session.commit()
        return jsonify(ok=True, oculto=True)
    from models import Profile
    Profile.query.filter_by(curso_actual_id=c.id).update({Profile.curso_actual_id: None})
    LeccionAprende.query.filter_by(curso_slug=c.slug).delete()
    db.session.delete(c)   # CASCADE: etapas, secciones, niveles, retos y progreso de ese curso
    db.session.commit()
    return jsonify(ok=True, borrado=True)


# ---------------------------------------------------------------------------------------- estructura ----
def _del_panel(curso_id):
    c = db.session.get(Course, curso_id)
    return bool(c) and c.slug not in _codigo_slugs()


NO_ESTRUCTURA = ("La estructura de los cursos de fábrica la define el código (cambiarla movería el progreso de los estudiantes). "
                 "Aquí puedes agregar, editar u ocultar retos en sus lecciones, o crear un curso nuevo.")


@bp.get("/api/admin/cursos/<int:cid>/arbol")
@requiere_admin
def arbol(cid):
    c = db.session.get(Course, cid)
    if not c:
        return api_error("Ese curso no existe.", 404)
    ocultos = {r.reto_id for r in RetoAdmin.query.filter_by(oculto=True).all()}
    etapas = []
    for e in Stage.query.filter_by(curso_id=cid).order_by(Stage.orden).all():
        secciones = []
        for s in Section.query.filter_by(etapa_id=e.id).order_by(Section.orden).all():
            niveles = [{"id": n.id, "titulo": n.titulo, "tipo": n.tipo, "xp": n.xp,
                        "retos": sum(1 for r in n.retos if r.id not in ocultos)}
                       for n in Level.query.filter_by(seccion_id=s.id).order_by(Level.orden).all()]
            secciones.append({"id": s.id, "titulo": s.titulo, "orden": s.orden, "niveles": niveles})
        etapas.append({"id": e.id, "titulo": e.titulo, "descripcion": e.descripcion, "orden": e.orden, "secciones": secciones})
    return jsonify(curso=_curso(c), etapas=etapas, editable=_del_panel(cid))


def _siguiente(modelo, campo, valor):
    return (db.session.query(func.max(modelo.orden)).filter(getattr(modelo, campo) == valor).scalar() or 0) + 1


def _titulo(data, maximo=80):
    t = " ".join(str(data.get("titulo", "")).split())[:maximo]
    return t if t else None


@bp.post("/api/admin/cursos/<int:cid>/etapas")
@requiere_admin
def crear_etapa(cid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    if not _del_panel(cid):
        return api_error(NO_ESTRUCTURA, 403)
    t = _titulo(data)
    if not t:
        return api_error("Escribe el título de la etapa.")
    e = Stage(curso_id=cid, orden=_siguiente(Stage, "curso_id", cid), titulo=t, descripcion=str(data.get("descripcion", "")).strip()[:160])
    db.session.add(e)
    db.session.flush()
    db.session.add(Section(etapa_id=e.id, orden=1, titulo=str(data.get("seccion", "")).strip()[:80] or "Sección 1"))
    db.session.commit()
    return jsonify(ok=True, id=e.id), 201


@bp.post("/api/admin/etapas/<int:eid>/secciones")
@requiere_admin
def crear_seccion(eid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    e = db.session.get(Stage, eid)
    if not e or not _del_panel(e.curso_id):
        return api_error(NO_ESTRUCTURA, 403)
    t = _titulo(data)
    if not t:
        return api_error("Escribe el título de la sección.")
    s = Section(etapa_id=eid, orden=_siguiente(Section, "etapa_id", eid), titulo=t)
    db.session.add(s)
    db.session.commit()
    return jsonify(ok=True, id=s.id), 201


@bp.post("/api/admin/secciones/<int:sid>/niveles")
@requiere_admin
def crear_nivel(sid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    s = db.session.get(Section, sid)
    if not s or not _del_panel(s.etapa.curso_id):
        return api_error(NO_ESTRUCTURA, 403)
    t = _titulo(data)
    if not t:
        return api_error("Escribe el título de la lección.")
    try:
        xp = max(1, min(200, int(data.get("xp") or 15)))
    except (TypeError, ValueError):
        xp = 15
    n = Level(seccion_id=sid, orden=_siguiente(Level, "seccion_id", sid), titulo=t,
              tipo=data.get("tipo") if data.get("tipo") in TIPOS_NIVEL else "leccion", xp=xp)
    db.session.add(n)
    db.session.commit()
    return jsonify(ok=True, id=n.id), 201


_MODELOS = {"etapas": Stage, "secciones": Section, "niveles": Level}


def _curso_de(obj):
    if isinstance(obj, Stage):
        return obj.curso_id
    if isinstance(obj, Section):
        return obj.etapa.curso_id
    return obj.seccion.etapa.curso_id


@bp.patch("/api/admin/estructura/<tipo>/<int:oid>")
@requiere_admin
def editar_parte(tipo, oid):
    modelo = _MODELOS.get(tipo)
    if not modelo:
        return api_error("No encontrado.", 404)
    data = json_body()
    if isinstance(data, tuple):
        return data
    obj = db.session.get(modelo, oid)
    if not obj or not _del_panel(_curso_de(obj)):
        return api_error(NO_ESTRUCTURA, 403)
    t = _titulo(data)
    if t:
        obj.titulo = t
    if tipo == "etapas" and "descripcion" in data:
        obj.descripcion = str(data["descripcion"]).strip()[:160]
    if tipo == "niveles":
        if data.get("tipo") in TIPOS_NIVEL:
            obj.tipo = data["tipo"]
        if "xp" in data:
            try:
                obj.xp = max(1, min(200, int(data["xp"])))
            except (TypeError, ValueError):
                pass
    db.session.commit()
    return jsonify(ok=True)


@bp.delete("/api/admin/estructura/<tipo>/<int:oid>")
@requiere_admin
def borrar_parte(tipo, oid):
    modelo = _MODELOS.get(tipo)
    if not modelo:
        return api_error("No encontrado.", 404)
    obj = db.session.get(modelo, oid)
    if not obj or not _del_panel(_curso_de(obj)):
        return api_error(NO_ESTRUCTURA, 403)
    db.session.delete(obj)
    db.session.commit()
    return jsonify(ok=True)


# ---------------------------------------------------------------------------------------- retos ----
def _reto(r, marcas, codigo):
    from retos import ORDEN_ADMIN
    m = marcas.get(r.id)
    del_codigo = codigo and r.orden < ORDEN_ADMIN
    return {"id": r.id, "orden": r.orden, "tipo": r.tipo, "enunciado": r.enunciado, "codigo": r.codigo, "opciones": r.opciones or [],
            "respuesta": r.respuesta, "explicacion": r.explicacion, "datos": r.datos or {},
            "origen": "codigo" if del_codigo else "panel", "editado": bool(m and m.editado), "oculto": bool(m and m.oculto)}


@bp.get("/api/admin/niveles/<int:nid>/retos")
@requiere_admin
def retos_de(nid):
    n = db.session.get(Level, nid)
    if not n:
        return api_error("Esa lección no existe.", 404)
    codigo = not _del_panel(n.seccion.etapa.curso_id)
    marcas = {m.reto_id: m for m in RetoAdmin.query.filter(RetoAdmin.reto_id.in_([r.id for r in n.retos])).all()}
    return jsonify(nivel={"id": n.id, "titulo": n.titulo, "tipo": n.tipo}, tipos=TIPOS_RETO,
                   retos=[_reto(r, marcas, codigo) for r in n.retos])


def _limpiar_reto(data):
    """Valida igual que el catálogo del código (retos/__init__.py) para que el reto funcione en la app."""
    from retos import _problemas_reto
    tipo = data.get("tipo")
    if tipo not in TIPOS_RETO:
        return None, "Tipo de reto no válido."
    texto = lambda k, m=4000: str(data.get(k) or "").strip()[:m]   # noqa: E731
    lista = lambda v: [str(x).strip()[:300] for x in (v or []) if str(x).strip()][:20] if isinstance(v, list) else []   # noqa: E731
    datos = data.get("datos") if isinstance(data.get("datos"), dict) else {}
    r = {"tipo": tipo, "enunciado": texto("enunciado"), "codigo": texto("codigo", 8000), "opciones": lista(data.get("opciones")),
         "respuesta": texto("respuesta", 500), "explicacion": texto("explicacion", 2000), "datos": {}}
    if tipo == "ordenar":
        r["datos"] = {"piezas": lista(datos.get("piezas"))}
    elif tipo == "parejas":
        pares = [[str(a).strip()[:200], str(b).strip()[:200]] for a, b in (p for p in (datos.get("pares") or []) if isinstance(p, list) and len(p) == 2)
                 if str(a).strip() and str(b).strip()][:10]
        r["datos"] = {"pares": pares}
    elif tipo == "armar":
        r["datos"] = {"solucion": lista(datos.get("solucion")), "trampas": lista(datos.get("trampas"))}
    if tipo != "opcion":
        r["opciones"] = []
    problemas = _problemas_reto(r)
    if problemas:
        return None, "El reto no es válido: " + "; ".join(problemas) + "."
    return r, None


@bp.post("/api/admin/niveles/<int:nid>/retos")
@requiere_admin
def crear_reto(nid):
    from retos import ORDEN_ADMIN
    data = json_body()
    if isinstance(data, tuple):
        return data
    n = db.session.get(Level, nid)
    if not n:
        return api_error("Esa lección no existe.", 404)
    if n.tipo != "leccion":
        return api_error("Las prácticas, cofres y exámenes toman sus preguntas de las lecciones: agrega retos a una lección.")
    r, error = _limpiar_reto(data)
    if error:
        return api_error(error)
    mayor = db.session.query(func.max(Challenge.orden)).filter(Challenge.nivel_id == nid).scalar() or 0
    orden = mayor + 1 if _del_panel(n.seccion.etapa.curso_id) else max(ORDEN_ADMIN, mayor + 1)
    c = Challenge(nivel_id=nid, orden=orden, **r)
    db.session.add(c)
    db.session.commit()
    return jsonify(ok=True, id=c.id), 201


@bp.patch("/api/admin/retos/<int:rid>")
@requiere_admin
def editar_reto(rid):
    from retos import ORDEN_ADMIN
    data = json_body()
    if isinstance(data, tuple):
        return data
    c = db.session.get(Challenge, rid)
    if not c:
        return api_error("Ese reto no existe.", 404)
    r, error = _limpiar_reto(data)
    if error:
        return api_error(error)
    for k, v in r.items():
        setattr(c, k, v)
    if c.orden < ORDEN_ADMIN and not _del_panel(c.nivel.seccion.etapa.curso_id):
        m = db.session.get(RetoAdmin, rid) or RetoAdmin(reto_id=rid)
        m.editado = True
        db.session.add(m)
    db.session.commit()
    return jsonify(ok=True)


@bp.delete("/api/admin/retos/<int:rid>")
@requiere_admin
def borrar_reto(rid):
    from retos import ORDEN_ADMIN
    c = db.session.get(Challenge, rid)
    if not c:
        return api_error("Ese reto no existe.", 404)
    if c.orden < ORDEN_ADMIN and not _del_panel(c.nivel.seccion.etapa.curso_id):
        m = db.session.get(RetoAdmin, rid) or RetoAdmin(reto_id=rid)
        m.oculto = True   # del código: se oculta (la sincronización lo volvería a crear) y se puede restaurar
        db.session.add(m)
        db.session.commit()
        return jsonify(ok=True, oculto=True)
    db.session.delete(c)
    db.session.commit()
    return jsonify(ok=True, borrado=True)


@bp.post("/api/admin/retos/<int:rid>/restaurar")
@requiere_admin
def restaurar_reto(rid):
    """Reto del código: se vuelve a mostrar y, si lo editaste, recupera su texto original en el próximo sync-retos."""
    RetoAdmin.query.filter_by(reto_id=rid).delete()
    db.session.commit()
    return jsonify(ok=True)


# ---------------------------------------------------------------------------------------- Aprende ----
CAMPOS_LECCION = {"t": 120, "m": 80, "x": 4000, "u": 2000, "c": 6000, "h": 1000, "r": 1000, "e": 1000, "q": 500, "a": 200, "f": 300}


def _leccion(x):
    return {"id": x.id, "curso": x.curso_slug, "posicion": x.posicion, "reemplaza": x.reemplaza, "oculta": x.oculta, **(x.datos or {})}


def _datos_leccion(data):
    d = {k: str(data.get(k) or "").strip()[:m] for k, m in CAMPOS_LECCION.items()}
    d["p"] = [str(p).strip()[:300] for p in (data.get("p") or []) if str(p).strip()][:12] if isinstance(data.get("p"), list) else []
    return d


@bp.get("/api/admin/aprende/<slug>")
@requiere_admin
def aprende_admin(slug):
    return jsonify(lecciones=[_leccion(x) for x in LeccionAprende.query.filter_by(curso_slug=slug[:30]).order_by(LeccionAprende.id).all()])


@bp.post("/api/admin/aprende/<slug>")
@requiere_admin
def crear_leccion(slug):
    """Lección nueva, reemplazo de una original (reemplaza = su título) u ocultar una original (oculta = true)."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    if not Course.query.filter_by(slug=slug).first():
        return api_error("Ese curso no existe.", 404)
    reemplaza = str(data.get("reemplaza") or "").strip()[:120] or None
    oculta = bool(data.get("oculta"))
    d = _datos_leccion(data)
    if not oculta and not d["t"]:
        return api_error("Escribe el título de la lección.")
    if reemplaza:
        LeccionAprende.query.filter_by(curso_slug=slug, reemplaza=reemplaza).delete()
    try:
        pos = None if data.get("posicion") in (None, "") else max(0, min(999, int(data["posicion"])))
    except (TypeError, ValueError):
        pos = None
    x = LeccionAprende(curso_slug=slug, reemplaza=reemplaza, oculta=oculta, posicion=pos, datos=d)
    db.session.add(x)
    db.session.commit()
    return jsonify(leccion=_leccion(x)), 201


@bp.patch("/api/admin/aprende/leccion/<int:lid>")
@requiere_admin
def editar_leccion(lid):
    data = json_body()
    if isinstance(data, tuple):
        return data
    x = db.session.get(LeccionAprende, lid)
    if not x:
        return api_error("Esa lección no existe.", 404)
    d = _datos_leccion({**(x.datos or {}), **data})
    if not x.oculta and not d["t"]:
        return api_error("Escribe el título de la lección.")
    x.datos = d
    if "posicion" in data:
        try:
            x.posicion = None if data["posicion"] in (None, "") else max(0, min(999, int(data["posicion"])))
        except (TypeError, ValueError):
            pass
    db.session.commit()
    return jsonify(leccion=_leccion(x))


@bp.delete("/api/admin/aprende/leccion/<int:lid>")
@requiere_admin
def borrar_leccion(lid):
    """Borra una lección del panel (si era un reemplazo u ocultaba una original, la original vuelve)."""
    LeccionAprende.query.filter_by(id=lid).delete()
    db.session.commit()
    return jsonify(ok=True)
