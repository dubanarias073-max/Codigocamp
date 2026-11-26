"""Deja la base de MySQL/MariaDB lista para el diagrama de MySQL Workbench.

Workbench se cierra al hacer el diagrama (Reverse Engineer / EER) de bases de MariaDB (XAMPP) que tienen
restricciones CHECK; el tipo JSON de MariaDB es LONGTEXT con un CHECK json_valid, así que también cuenta.
Además, una columna llamada `cursor` (palabra reservada) rompe su analizador. Esto lo corrige sin perder datos:
  * quita las restricciones CHECK (los límites los valida la aplicación),
  * convierte las columnas JSON en LONGTEXT (el contenido sigue siendo el mismo texto JSON),
  * renombra cosmeticos_equipados.cursor a puntero.
"""
from sqlalchemy import text

COLUMNAS_JSON = {
    "espacios_trabajo": ("archivos", "carpetas", "git"),
    "retos": ("opciones", "datos"),
    "perfiles": ("intereses",),
}


def _q(nombre):
    return "`" + nombre.replace("`", "``") + "`"


def reparar(engine):
    """Devuelve la lista de cambios hechos (vacía si ya estaba bien o la base no es MySQL/MariaDB)."""
    if engine.dialect.name not in ("mysql", "mariadb"):
        return []
    hechos = []
    with engine.begin() as con:
        base = con.execute(text("SELECT DATABASE()")).scalar()
        tablas = {fila[0] for fila in con.execute(text(
            "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = :b"), {"b": base})}

        # 1. Columnas JSON -> LONGTEXT (en MariaDB esto también borra su CHECK json_valid).
        for tabla, columnas in COLUMNAS_JSON.items():
            if tabla not in tablas:
                continue
            for col, tipo, nulo in con.execute(text(
                    "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = :b AND TABLE_NAME = :t"), {"b": base, "t": tabla}):
                if col in columnas:
                    con.execute(text(f"ALTER TABLE {_q(tabla)} MODIFY {_q(col)} LONGTEXT "
                                     f"{'NULL' if nulo == 'YES' else 'NOT NULL'} COMMENT 'JSON'"))
                    if tipo.lower() == "json":
                        hechos.append(f"{tabla}.{col}: JSON -> LONGTEXT")

        # 2. Restricciones CHECK que queden (de tabla o de columna).
        checks = set()
        for consulta in (
            "SELECT TABLE_NAME, CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA = :b AND CONSTRAINT_TYPE = 'CHECK'",
            "SELECT TABLE_NAME, CONSTRAINT_NAME FROM information_schema.CHECK_CONSTRAINTS "
            "WHERE CONSTRAINT_SCHEMA = :b",
        ):
            try:
                checks.update(tuple(f) for f in con.execute(text(consulta), {"b": base}) if f[0])
            except Exception:  # noqa: BLE001 - CHECK_CONSTRAINTS no tiene TABLE_NAME en MySQL 8
                pass
        for tabla, nombre in sorted(checks):
            try:
                con.execute(text(f"ALTER TABLE {_q(tabla)} DROP CONSTRAINT {_q(nombre)}"))
                hechos.append(f"{tabla}: sin CHECK {nombre}")
            except Exception:  # noqa: BLE001 - p. ej. ya se fue al cambiar la columna
                pass

        # 3. Columna con nombre reservado.
        if "cosmeticos_equipados" in tablas:
            cols = {f[0] for f in con.execute(text(
                "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = :b "
                "AND TABLE_NAME = 'cosmeticos_equipados'"), {"b": base})}
            if "cursor" in cols and "puntero" not in cols:
                con.execute(text("ALTER TABLE cosmeticos_equipados CHANGE `cursor` puntero VARCHAR(30) NULL "
                                 "COMMENT 'Puntero del mouse'"))
                hechos.append("cosmeticos_equipados.cursor -> puntero")

        # 4. Tablas que no están en utf8mb4: tildes, «¿» o emojis se guardaban como «?» (p. ej. títulos de chats de la IA).
        for tabla, cotejo in con.execute(text(
                "SELECT TABLE_NAME, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = :b AND TABLE_TYPE = 'BASE TABLE'"), {"b": base}):
            if cotejo and not str(cotejo).lower().startswith("utf8mb4"):
                try:
                    con.execute(text(f"ALTER TABLE {_q(tabla)} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    hechos.append(f"{tabla}: {cotejo} -> utf8mb4")
                except Exception:  # noqa: BLE001 - p. ej. un índice demasiado largo: se deja como estaba
                    pass
        try:
            con.execute(text(f"ALTER DATABASE {_q(base)} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        except Exception:  # noqa: BLE001 - sin permiso: no pasa nada
            pass
    return hechos


def agregar_columnas(engine, modelos):
    """Agrega a las tablas existentes las columnas nuevas de los modelos (versiones nuevas de CódigoCamp).
    Solo agrega columnas con valor por defecto o que admiten NULL; nunca borra ni cambia nada."""
    from sqlalchemy import inspect
    hechos = []
    insp = inspect(engine)
    with engine.begin() as con:
        for modelo in modelos:
            tabla = modelo.__table__
            if not insp.has_table(tabla.name):
                continue
            existentes = {c["name"] for c in insp.get_columns(tabla.name)}
            for col in tabla.columns:
                if col.name in existentes:
                    continue
                tipo = col.type.compile(dialect=engine.dialect)
                defecto = col.default.arg if col.default is not None and not callable(col.default.arg) else None
                if isinstance(defecto, bool):
                    defecto = int(defecto)
                sql = f"ALTER TABLE {tabla.name} ADD COLUMN {col.name} {tipo}"
                if defecto is not None:
                    sql += f" NOT NULL DEFAULT {defecto!r}" if isinstance(defecto, str) else f" NOT NULL DEFAULT {defecto}"
                else:
                    sql += " NULL"
                con.execute(text(sql))
                hechos.append(f"{tabla.name}.{col.name}")
    return hechos


def migraciones_de_datos(db):
    """Cambios de datos de una sola vez. Devuelve las claves aplicadas ahora."""
    from models import AppliedMigration, Profile
    hechas = []
    if db.session.get(AppliedMigration, "economia_x10") is None:
        # La tienda nueva cuenta en decenas y centenas de diamantes: los que ya tenía cada persona se multiplican por 10.
        Profile.query.update({Profile.diamante: Profile.diamante * 10}, synchronize_session=False)
        db.session.add(AppliedMigration(clave="economia_x10"))
        hechas.append("economia_x10")
    if db.session.get(AppliedMigration, "avatares_svg") is None:
        # Los avatares con emoji pasan a los dibujos nuevos (js/avatares.js); los demás quedan con la inicial.
        from constantes import AVATAR_DE_EMOJI
        for p in Profile.query.filter(Profile.avatar.isnot(None)).all():
            p.avatar = AVATAR_DE_EMOJI.get(p.avatar)
        db.session.add(AppliedMigration(clave="avatares_svg"))
        hechas.append("avatares_svg")
    if db.session.get(AppliedMigration, "quitar_avatares") is None:
        # Los avatares ya no existen: se devuelven los diamantes de cada avatar comprado y nadie queda con avatar.
        from constantes import AVATARES_RETIRADOS
        from models import Purchase, StoreItem
        items = StoreItem.query.filter(StoreItem.clave.in_(list(AVATARES_RETIRADOS))).all()
        ids = {i.id for i in items}
        if ids:
            for compra in Purchase.query.filter(Purchase.articulo_id.in_(list(ids))).all():
                perfil = Profile.query.filter_by(usuario_id=compra.usuario_id).first()
                if perfil and compra.moneda == "diamante":
                    perfil.diamante += compra.precio
            for i in items:
                i.activo = False
        Profile.query.filter(Profile.avatar.isnot(None)).update({Profile.avatar: None}, synchronize_session=False)
        db.session.add(AppliedMigration(clave="quitar_avatares"))
        hechas.append("quitar_avatares")
    if db.session.get(AppliedMigration, "compras_a_coleccion") is None:
        # Cosméticos comprados antes de que existiera la colección: pasan a la colección (desde ahora es lo único que cuenta).
        from cosmeticos import POR_CLAVE
        from models import OwnedCosmetic, Purchase, StoreItem
        ids = {i.id: i.clave for i in StoreItem.query.filter(StoreItem.clave.in_(list(POR_CLAVE))).all()}
        tiene = {(c.usuario_id, c.clave) for c in OwnedCosmetic.query.all()}
        for compra in Purchase.query.filter(Purchase.articulo_id.in_(list(ids))).all() if ids else []:
            par = (compra.usuario_id, ids[compra.articulo_id])
            if par not in tiene:
                db.session.add(OwnedCosmetic(usuario_id=par[0], clave=par[1], origen="tienda"))
                tiene.add(par)
        db.session.add(AppliedMigration(clave="compras_a_coleccion"))
        hechas.append("compras_a_coleccion")
    if db.session.get(AppliedMigration, "ia_sin_duplicados") is None:
        # Cuando la IA fallaba, cada «reintentar» abría una conversación nueva con la misma pregunta: se dejan en una sola.
        borradas = limpiar_conversaciones_repetidas()
        db.session.add(AppliedMigration(clave="ia_sin_duplicados"))
        hechas.append(f"ia_sin_duplicados ({borradas})")
    if hechas:
        db.session.commit()
    return hechas


def limpiar_conversaciones_repetidas(usuario_id=None):
    """Junta las conversaciones con la IA que son la misma pregunta repetida (reintentos que fallaron).
    De cada grupo (misma primera pregunta, creadas con menos de 1 hora de diferencia) se queda la que tenga respuesta y
    más mensajes; se borran las otras solo si son cortas (pregunta sin respuesta o una sola respuesta)."""
    from datetime import timedelta
    from models import AIConversation, db
    q = AIConversation.query
    if usuario_id:
        q = q.filter_by(usuario_id=usuario_id)
    grupos = {}
    for c in q.order_by(AIConversation.usuario_id, AIConversation.creada).all():
        msgs = list(c.mensajes)
        primera = next((m.texto.strip() for m in msgs if m.rol == "yo"), None)
        if primera is None:
            if not msgs:
                db.session.delete(c)   # vacía
            continue
        lista = grupos.setdefault((c.usuario_id, primera), [])
        if lista and (c.creada - lista[-1][-1].creada) <= timedelta(hours=1):
            lista[-1].append(c)
        else:
            lista.append([c])
    borradas = 0
    for lista in grupos.values():
        for grupo in lista:
            if len(grupo) < 2:
                continue
            def valor(c):
                ms = list(c.mensajes)
                return (any(m.rol == "tutor" for m in ms), len(ms), c.actualizada)
            mejor = max(grupo, key=valor)
            for c in grupo:
                if c is not mejor and len(c.mensajes) <= 2 and not c.fijada:
                    db.session.delete(c)
                    borradas += 1
    db.session.flush()
    return borradas
