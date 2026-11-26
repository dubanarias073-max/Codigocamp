"""Lógica de la tienda: crea los artículos de diamantes en la base la primera vez que se usa."""
from models import StoreItem, db
from constantes import ARTICULOS_DIAMANTE, BASICOS_DIAMANTE, COSMETICOS_TIENDA
from sqlalchemy.exc import SQLAlchemyError


_ITEMS_LISTOS = False


def asegurar_articulos():
    """Crea en la base los artículos de diamante que falten (una vez por arranque del servidor)."""
    global _ITEMS_LISTOS
    if _ITEMS_LISTOS:
        return
    existentes = {i.clave for i in StoreItem.query.all()}
    for i in StoreItem.query.filter(StoreItem.clave.in_(list(BASICOS_DIAMANTE))).all():   # antes costaban cobre/hierro
        i.moneda, i.categoria, i.precio = "diamante", "diamante", BASICOS_DIAMANTE[i.clave]
    # Los precios siguen siempre a constantes.py / cosmeticos.py (si cambian, se actualizan en la base).
    precios = {a["clave"]: a["precio"] for a in ARTICULOS_DIAMANTE} | {c["clave"]: c["precio"] for c in COSMETICOS_TIENDA}
    datos = {a["clave"]: a for a in ARTICULOS_DIAMANTE} | {c["clave"]: {**c, "icono": c["tipo"]} for c in COSMETICOS_TIENDA}
    for i in StoreItem.query.filter(StoreItem.clave.in_(list(precios))).all():
        if i.precio != precios[i.clave]:
            i.precio = precios[i.clave]
        if i.clave in datos:   # nombre, descripción e ícono también siguen a constantes.py / cosmeticos.py
            for campo in ("nombre", "descripcion", "icono"):
                if getattr(i, campo) != datos[i.clave][campo]:
                    setattr(i, campo, datos[i.clave][campo])
    from cosmeticos import RETIRADOS
    for i in StoreItem.query.filter(StoreItem.clave.in_(list(RETIRADOS)), StoreItem.activo.is_(True)).all():
        i.activo = False   # se quitó de la tienda
    # Los básicos (vida, recarga, salvarrachas, kit) también se crean si la base no los trae (antes solo venían del .sql)
    basicos = [("vida", "Una vida", "Recupera una vida al instante.", "❤️"), ("vidas_llenas", "Recarga de vidas", "Rellena tus vidas hasta cinco.", "💖"),
               ("salvarracha", "Salvarrachas", "Protege tu racha durante un día sin practicar. Máximo 2.", "🧊"), ("kit_experto", "Kit experto", "Tres vidas y una salvarracha.", "💎")]
    for orden_b, (clave, nombre, desc, icono) in enumerate(basicos, start=1):
        if clave not in existentes:
            db.session.add(StoreItem(clave=clave, nombre=nombre, descripcion=desc, icono=icono, moneda="diamante",
                                     precio=BASICOS_DIAMANTE[clave], categoria="diamante", orden=orden_b, activo=True))
    orden = 10
    for a in ARTICULOS_DIAMANTE:
        orden += 1
        if a["clave"] not in existentes:
            db.session.add(StoreItem(clave=a["clave"], nombre=a["nombre"], descripcion=a["descripcion"], icono=a["icono"],
                                     moneda="diamante", precio=a["precio"], categoria="diamante", orden=orden, activo=True))
    for c in COSMETICOS_TIENDA:
        orden += 1
        if c["clave"] not in existentes:
            db.session.add(StoreItem(clave=c["clave"], nombre=c["nombre"], descripcion=c["descripcion"], icono=c["tipo"],
                                     moneda="diamante", precio=c["precio"], categoria="diamante", orden=orden, activo=True))
    db.session.flush()
    from servicios.catalogo_admin import aplicar_ajustes
    aplicar_ajustes()   # precios, nombres y ocultos que cambió el administrador en el panel
    try:
        db.session.commit()
        _ITEMS_LISTOS = True
    except SQLAlchemyError:
        db.session.rollback()
        raise
