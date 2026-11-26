"""Mezcla lo que el administrador crea o cambia en el panel con el catálogo que vive en el código.

- Cosméticos diseñados en el panel (tabla cosmeticos_admin, claves «a_…»): se agregan a cosmeticos.POR_CLAVE, a los
  permanentes y a las rarezas, así compras, equipar, perfiles y cofres los tratan igual que a los de fábrica.
- Ajustes de artículos (tabla ajustes_tienda): precio, nombre, descripción, rareza u «ocultar» de cualquier artículo,
  también de los de fábrica. Se aplican encima de constantes.py / cosmeticos.py.

Cada proceso del servidor (gunicorn puede tener varios) vuelve a leer la base como máximo cada REFRESCO segundos, así
un cambio en el panel llega a todos sin reiniciar.
"""
import re
import time

REFRESCO = 15
RAREZAS = ("comun", "raro", "epico", "legendario")
TIPOS_DISENABLES = ("fondo", "tema", "marco", "cursor", "efecto", "dedo", "teclado", "codi")
ANIMACIONES_FONDO = ("ninguna", "aurora", "nieve", "luciernagas", "lluvia", "burbujas", "sakura", "fugaces", "matrix", "hiper", "nebulosa", "agujero")
ESTILOS_FONDO = ("lineal", "diagonal", "radial", "aurora", "imagen")
FORMAS = ("punto", "estrella", "burbuja", "cuadro", "corazon", "moneda", "pixel", "emoji", "imagen", "texto", "onda")
CAPAS_FONDO = ("ninguna", "vineta", "rejilla", "estrellas", "escaneo", "brillo")
ESTILOS_MARCO = ("aro", "neon", "holo", "fuego", "imagen")
ESTILOS_TECLADO = ("plano", "3d", "neon", "cristal", "arcoiris")
EFECTOS_VITRINA = ("ninguno", "inclinar", "flotar", "girar", "latido")
MODOS_IMAGEN = ("cubrir", "mosaico", "centrar")
MOVIMIENTOS = ("ninguno", "zoom", "paneo", "flotar", "latido")
ANIM_STICKER = ("ninguna", "flotar", "girar", "latido", "rebotar", "balanceo", "parpadeo", "cruzar", "caer", "orbitar")
POS_INSIGNIA = ("arriba", "abajo", "derecha", "izquierda")
CAPAS_CODI = ("cabeza", "cara", "cuello", "atras", "frente")
MAX_STICKERS = 8
TIPOS_PARTE = ("flecha", "emoji", "flecha_emoji", "forma", "imagen", "mano", "barra", "sistema")
FORMAS_CURSOR = ("circulo", "mira", "estrella", "corazon", "rombo", "punto", "rayo")
PUNTAS = ("esquina", "centro")
LLUVIAS = ("ninguna", "cae", "sube", "flota", "remolino")
FUENTES = ("sistema", "redondeada", "mono", "manuscrita", "pixel", "elegante")
ANIM_MEDALLA = ("ninguna", "brillo", "girar", "latido", "flotar", "destellos")
FORMAS_MEDALLA = ("circulo", "escudo", "estrella", "hexagono", "rombo", "engranaje", "corona", "flor")
METALES = ("oro", "plata", "bronce", "diamante", "esmeralda", "rubi", "arcoiris", "obsidiana", "personal")
CINTAS = ("ninguna", "v", "doble", "laurel")
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_IMG = re.compile(r"^/api/admin-img/[a-f0-9]{16,64}\.(?:png|jpe?g|webp|gif)$")

_ultimo = 0.0
_claves_admin = set()


def _color(v, defecto):
    v = str(v or "").strip()
    return v if _HEX.match(v) else defecto


def _emoji(v, defecto=""):
    v = str(v or "").strip()[:8]
    return "" if re.search(r"[<>{};\"'\\`]", v) else (v or defecto)


def _img(v):
    v = str(v or "")
    return v if _IMG.match(v) else ""


def _num(v, defecto, menor, mayor):
    try:
        return max(menor, min(mayor, int(v)))
    except (TypeError, ValueError):
        return defecto


def _parte_cursor(p, defecto):
    """Cada parte del puntero (normal, sobre enlaces, sobre texto) se diseña por separado."""
    p = p if isinstance(p, dict) else {}
    tipo = p.get("tipo") if p.get("tipo") in TIPOS_PARTE else defecto
    if tipo == "imagen" and not _img(p.get("imagen")):
        tipo = defecto
    return {"tipo": tipo, "c1": _color(p.get("c1"), "#ffffff"), "c2": _color(p.get("c2"), "#0f172a"), "emoji": _emoji(p.get("emoji"), "⭐"),
            "imagen": _img(p.get("imagen")), "forma": p.get("forma") if p.get("forma") in FORMAS_CURSOR else "estrella",
            "punta": p.get("punta") if p.get("punta") in PUNTAS else ("centro" if tipo in ("emoji", "forma") else "esquina")}


def _emojis(v, maximo=8):
    """Varios emojis o palabras cortas separados por espacio (para lluvias y clics)."""
    partes = [str(x)[:14] for x in str(v or "").split() if x.strip()][:maximo]
    limpio = [re.sub(r"[<>&\"'`\\]", "", x) for x in partes]
    return " ".join(x for x in limpio if x)


def limpiar_medalla(d):
    """Diseño de una medalla especial (todo de listas cerradas, colores #hex e imágenes del panel)."""
    d = d if isinstance(d, dict) else {}
    texto = re.sub(r"[<>&\"'`\\]", "", str(d.get("texto") or ""))[:16]
    return {"forma": d.get("forma") if d.get("forma") in FORMAS_MEDALLA else "circulo",
            "metal": d.get("metal") if d.get("metal") in METALES else "oro",
            "c1": _color(d.get("c1"), "#c4ff3d"), "c2": _color(d.get("c2"), "#0ea5e9"),
            "centro": d.get("centro") if d.get("centro") in ("imagen", "completa") and _img(d.get("imagen")) else "emoji",
            "emoji": _emoji(d.get("emoji"), "🏅"), "imagen": _img(d.get("imagen")),
            "cinta": d.get("cinta") if d.get("cinta") in CINTAS else "v",
            "cinta1": _color(d.get("cinta1"), "#ef4444"), "cinta2": _color(d.get("cinta2"), "#2563eb"),
            "texto": texto, "anim": d.get("anim") if d.get("anim") in ANIM_MEDALLA else "brillo", "aura": bool(d.get("aura", True)),
            "estrellas": _num(d.get("estrellas"), 0, 0, 5)}


def _insignia(v):
    v = v if isinstance(v, dict) else {}
    if not _img(v.get("imagen")):
        return None
    return {"imagen": _img(v.get("imagen")), "pos": v.get("pos") if v.get("pos") in POS_INSIGNIA else "arriba",
            "tam": _num(v.get("tam"), 45, 15, 90), "anim": v.get("anim") if v.get("anim") in ANIM_STICKER else "ninguna"}


def limpiar_vitrina(v):
    """Cómo se presenta el artículo en la tienda: movimiento 3D, aura de color, brillo holográfico y destellos."""
    v = v if isinstance(v, dict) else {}
    aura = str(v.get("aura") or "")
    return {"efecto": v.get("efecto") if v.get("efecto") in EFECTOS_VITRINA else "ninguno",
            "aura": aura if _HEX.match(aura) else "", "brillo": bool(v.get("brillo")), "destellos": bool(v.get("destellos"))}


def limpiar_diseno(tipo, d):
    """Solo valores seguros (colores #hex, listas cerradas, números, imágenes subidas al panel): termina dentro de CSS y SVG."""
    d = d if isinstance(d, dict) else {}
    limpio = _limpiar_tipo(tipo, d)
    if limpio:
        limpio["vitrina"] = limpiar_vitrina(d.get("vitrina"))
        fuente = _img(d.get("fuente"))   # la imagen original, para volver a editarla desde cero
        if fuente and limpio.get("imagen"):
            limpio["fuente"] = fuente
    return limpio


def _limpiar_tipo(tipo, d):
    colores = [c for c in (d.get("colores") or []) if isinstance(c, str) and _HEX.match(c)][:6]
    if tipo == "fondo":
        img = str(d.get("imagen") or "")
        stickers = []
        for st in (d.get("stickers") or [])[:MAX_STICKERS] if isinstance(d.get("stickers"), list) else []:
            if isinstance(st, dict) and _img(st.get("imagen")):
                stickers.append({"imagen": _img(st.get("imagen")), "x": _num(st.get("x"), 50, 0, 100), "y": _num(st.get("y"), 50, 0, 100),
                                 "tam": _num(st.get("tam"), 20, 2, 80), "anim": st.get("anim") if st.get("anim") in ANIM_STICKER else "flotar",
                                 "opacidad": _num(st.get("opacidad"), 100, 10, 100), "girar": _num(st.get("girar"), 0, -180, 180)})
        return {"estilo": d.get("estilo") if d.get("estilo") in ESTILOS_FONDO else "lineal",
                "modo": d.get("modo") if d.get("modo") in MODOS_IMAGEN else "cubrir", "mosaico": _num(d.get("mosaico"), 160, 24, 800),
                "movimiento": d.get("movimiento") if d.get("movimiento") in MOVIMIENTOS else "ninguno",
                "desenfoque": _num(d.get("desenfoque"), 0, 0, 20), "stickers": stickers,
                "lluvia": d.get("lluvia") if d.get("lluvia") in LLUVIAS else "ninguna", "lluvia_emojis": _emojis(d.get("lluvia_emojis")) or "⭐ ✨",
                "lluvia_cantidad": _num(d.get("lluvia_cantidad"), 18, 4, 40),
                "colores": (colores or ["#0f172a", "#1e3a8a"])[:4],
                "imagen": img if _IMG.match(img) else "",
                "animacion": d.get("animacion") if d.get("animacion") in ANIMACIONES_FONDO else "ninguna",
                "capa": d.get("capa") if d.get("capa") in CAPAS_FONDO else "ninguna",
                "oscurecer": _num(d.get("oscurecer"), 0, 0, 80),
                "oscuro": bool(d.get("oscuro", True))}
    if tipo == "tema":
        return {"acc": _color(d.get("acc"), "#22c55e"), "acc2": _color(d.get("acc2"), "#15803d"), "cy": _color(d.get("cy"), "#22d3ee"),
                "fuente": d.get("fuente") if d.get("fuente") in FUENTES else "sistema", "neon": bool(d.get("neon")), "fluir": bool(d.get("fluir"))}
    if tipo == "marco":
        try:
            vel = max(1, min(10, int(d.get("velocidad") or 4)))
        except (TypeError, ValueError):
            vel = 4
        return {"colores": colores if len(colores) >= 2 else ["#22d3ee", "#a855f7"], "gira": bool(d.get("gira", True)),
                "velocidad": vel, "brillo": bool(d.get("brillo", True)),
                "estilo": d.get("estilo") if d.get("estilo") in ESTILOS_MARCO else "aro", "imagen": _img(d.get("imagen")),
                "grosor": _num(d.get("grosor"), 4, 2, 10), "orbita": bool(d.get("orbita")), "pulso": bool(d.get("pulso")),
                "insignia": _insignia(d.get("insignia"))}
    if tipo == "cursor":
        viejo = {"normal": {"tipo": "imagen" if _img(d.get("imagen")) else "flecha_emoji", "emoji": d.get("emoji"), "c1": d.get("c1"), "c2": d.get("c2"),
                            "imagen": d.get("imagen"), "punta": "centro" if d.get("centro") else "esquina"}}
        partes = d.get("partes") if isinstance(d.get("partes"), dict) else viejo
        defecto = {"normal": "flecha", "mano": "mano", "texto": "barra"}
        return {"tam": _num(d.get("tam"), 32, 24, 64),
                "partes": {k: _parte_cursor(partes.get(k), defecto[k]) for k in ("normal", "mano", "texto")}}
    if tipo == "codi":
        return {"imagen": _img(d.get("imagen")), "capa": d.get("capa") if d.get("capa") in CAPAS_CODI else "cabeza",
                "x": _num(d.get("x"), 100, 0, 200), "y": _num(d.get("y"), 40, -40, 220), "tam": _num(d.get("tam"), 90, 10, 220),
                "girar": _num(d.get("girar"), 0, -180, 180), "anim": d.get("anim") if d.get("anim") in ANIM_STICKER else "ninguna",
                "sinAntena": bool(d.get("sinAntena"))}
    if tipo in ("efecto", "dedo"):
        try:
            cantidad = max(3, min(20, int(d.get("cantidad") or 8)))
        except (TypeError, ValueError):
            cantidad = 8
        return {"forma": d.get("forma") if d.get("forma") in FORMAS else "punto", "emoji": _emoji(d.get("emoji"), "✨"),
                "colores": colores or ["#facc15", "#22d3ee", "#a855f7"], "cantidad": cantidad, "imagen": _img(d.get("imagen")),
                "tam": _num(d.get("tam"), 24, 12, 160), "modo": "mascota" if tipo == "dedo" and d.get("modo") == "mascota" else "particulas",
                "emojis": _emojis(d.get("emojis")), "palabras": _emojis(d.get("palabras"), 10) or "+1 ¡Bien! 💯"}
    if tipo == "teclado":
        return {"bg": _color(d.get("bg"), "#1e293b"), "fg": _color(d.get("fg"), "#e2e8f0"), "borde": _color(d.get("borde"), "#334155"),
                "enter": _color(d.get("enter"), "#6366f1"), "fondo": _color(d.get("fondo"), "#0f172a"),
                "estilo": d.get("estilo") if d.get("estilo") in ESTILOS_TECLADO else "plano", "imagen": _img(d.get("imagen")),
                "chispas": bool(d.get("chispas"))}
    return {}


def refrescar(forzar=False):
    """Vuelve a leer cosméticos y ajustes del panel (como máximo cada REFRESCO segundos por proceso)."""
    global _ultimo, _claves_admin
    ahora = time.monotonic()
    if not forzar and ahora - _ultimo < REFRESCO:
        return
    _ultimo = ahora
    import constantes
    import cosmeticos
    from models import AjusteArticulo, CosmeticoAdmin, db
    try:
        filas = CosmeticoAdmin.query.all()
        ajustes = AjusteArticulo.query.all()
    except Exception:  # noqa: BLE001 - tablas aún no creadas
        db.session.rollback()
        return
    for k in _claves_admin:
        cosmeticos.POR_CLAVE.pop(k, None)
    _claves_admin = set()
    for c in filas:
        info = {"clave": c.clave, "tipo": c.tipo, "nombre": c.nombre, "precio": c.precio, "rareza": c.rareza,
                "descripcion": c.descripcion, "admin": True, "diseno": c.diseno or {}}
        cosmeticos.POR_CLAVE[c.clave] = info
        constantes.PERMANENTES.add(c.clave)
        constantes.RAREZA[c.clave] = c.rareza
        _claves_admin.add(c.clave)
    for a in ajustes:
        if a.rareza in RAREZAS:
            constantes.RAREZA[a.clave] = a.rareza
            if a.clave in cosmeticos.POR_CLAVE:
                cosmeticos.POR_CLAVE[a.clave] = {**cosmeticos.POR_CLAVE[a.clave], "rareza": a.rareza}
        for campo in ("nombre", "precio", "descripcion"):
            valor = getattr(a, campo)
            if valor is not None and a.clave in cosmeticos.POR_CLAVE:
                cosmeticos.POR_CLAVE[a.clave] = {**cosmeticos.POR_CLAVE[a.clave], campo: valor}


def aplicar_ajustes():
    """Pone en articulos_tienda los precios/nombres/ocultos del panel (después de sincronizar con el código)."""
    from models import AjusteArticulo, StoreItem
    ajustes = {a.clave: a for a in AjusteArticulo.query.all()}
    if not ajustes:
        return
    for item in StoreItem.query.filter(StoreItem.clave.in_(list(ajustes))).all():
        a = ajustes[item.clave]
        for campo in ("precio", "nombre", "descripcion"):
            valor = getattr(a, campo)
            if valor is not None and getattr(item, campo) != valor:
                setattr(item, campo, valor)
        if a.oculto and item.activo:
            item.activo = False


def disenos_publicos():
    """Lo que el navegador necesita para dibujar los cosméticos del panel (cualquier página los puede mostrar)."""
    from models import CosmeticoAdmin
    return [{"clave": c.clave, "tipo": c.tipo, "nombre": c.nombre, "rareza": c.rareza, "diseno": c.diseno or {}}
            for c in CosmeticoAdmin.query.order_by(CosmeticoAdmin.id).all()]
