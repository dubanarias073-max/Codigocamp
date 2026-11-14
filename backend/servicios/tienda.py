"""Lógica de la tienda: crea los artículos de diamantes en la base la primera vez que se usa."""
from models import StoreItem, db
from constantes import ARTICULOS_DIAMANTE, BASICOS_DIAMANTE
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
    orden = 10
    for a in ARTICULOS_DIAMANTE:
        orden += 1
        if a["clave"] not in existentes:
            db.session.add(StoreItem(clave=a["clave"], nombre=a["nombre"], descripcion=a["descripcion"], icono=a["icono"],
                                     moneda="diamante", precio=a["precio"], categoria="diamante", orden=orden, activo=True))
    try:
        db.session.commit()
        _ITEMS_LISTOS = True
    except SQLAlchemyError:
        db.session.rollback()
        raise
