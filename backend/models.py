from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)



import json as _json
from sqlalchemy.dialects.mysql import LONGTEXT as _LONGTEXT
from sqlalchemy.types import Text as _Text, TypeDecorator as _TypeDecorator


class TextoJSON(_TypeDecorator):
    """JSON guardado como LONGTEXT. Evita el tipo JSON (que en MariaDB/XAMPP agrega un CHECK json_valid)
    porque MySQL Workbench se cierra al hacer el diagrama de tablas con esos CHECK."""
    impl = _Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(_LONGTEXT() if dialect.name in ("mysql", "mariadb") else _Text())

    def process_bind_param(self, value, dialect):
        return None if value is None else _json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    def process_result_value(self, value, dialect):
        if value is None or value == "":
            return value if value is None else None
        if isinstance(value, (dict, list)):
            return value
        return _json.loads(value)

class User(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def get_id(self):
        # «usuario:sesión»: así cada inicio de sesión se puede cerrar desde otro dispositivo (seguridad.py).
        sid = getattr(self, "_sid", None)
        return f"{self.id}:{sid}" if sid else str(self.id)


class UserWorkspace(db.Model):
    __tablename__ = "espacios_trabajo"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    archivos = db.Column(TextoJSON, nullable=False, default=dict)
    carpetas = db.Column(TextoJSON, nullable=False, default=list)
    git = db.Column(TextoJSON, nullable=False, default=dict)
    actualizado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    # Clave del enlace «en vivo» (/live/<clave>/…), como Live Server: null = apagado. Se puede cambiar para cortar el acceso.
    live_clave = db.Column(db.String(24), nullable=True, index=True)


class WorkspaceFile(db.Model):
    """Archivo binario del espacio de trabajo (imagen, video, PDF…). Los bytes viven en disco
    (ALMACEN_ARCHIVOS/<usuario>/<hash[:2]>/<hash>); aquí solo sus datos. El proyecto lo referencia con un
    «marcador» de texto (ccbin:v1:<hash>:<tipo>:<bytes>), así mover, copiar o versionar con Git no duplica datos."""
    __tablename__ = "archivos_trabajo"
    __table_args__ = (db.UniqueConstraint("usuario_id", "hash", name="uq_archivos_trabajo_usuario_hash"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    hash = db.Column(db.String(64), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    tamano = db.Column(db.BigInteger, nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Course(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(40), nullable=False)
    tipo = db.Column(db.Enum("web", "lenguaje", "bd", name="tipo_curso"), nullable=False, default="lenguaje")
    sigla = db.Column(db.String(6), nullable=False)
    color = db.Column(db.String(7), nullable=False, default="#4ade80")
    descripcion = db.Column(db.String(120), nullable=False, default="")
    orden = db.Column(db.SmallInteger, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    etapas = db.relationship("Stage", back_populates="course", cascade="all, delete-orphan", order_by="Stage.orden")


class Profile(db.Model):
    __tablename__ = "perfiles"
    ROLES = {"estudiante", "cambio", "programador", "curioso"}
    NIVELES = {"cero", "probado", "basico", "avanzado"}
    IDIOMAS = {"es"}
    TEMAS = {"auto", "claro", "oscuro"}  # auto = predeterminado (sigue el tema del dispositivo)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE", name="fk_perfiles_usuario"), unique=True, nullable=False)
    rol = db.Column(db.String(12), nullable=False, default="")
    intereses = db.Column(TextoJSON, nullable=False, default=list)
    nivel_previo = db.Column(db.String(10), nullable=False, default="")
    curso_actual_id = db.Column(db.Integer, db.ForeignKey("cursos.id", ondelete="SET NULL", onupdate="CASCADE", name="fk_perfiles_curso_actual"), nullable=True)
    meta_minutos = db.Column(db.SmallInteger, nullable=False, default=10)
    zona_horaria = db.Column(db.String(64), nullable=True)  # la detecta el dispositivo (p. ej. America/Bogota)
    onboarding_completo = db.Column(db.Boolean, nullable=False, default=False)
    tema = db.Column(db.Enum("auto", "claro", "oscuro", name="tema"), nullable=False, default="auto")
    idioma = db.Column(db.String(2), nullable=False, default="es", server_default="es")   # la app es solo en español (columna conservada por compatibilidad)
    buscable_correo = db.Column(db.Boolean, nullable=False, default=True, server_default="1")   # tus contactos te encuentran por tu correo
    alias = db.Column(db.String(20), unique=True, nullable=True)
    codigo = db.Column(db.String(8), unique=True, nullable=True)
    avatar = db.Column(db.String(8), nullable=True)  # emoji elegido en el perfil (vacío = inicial del nombre)
    xp = db.Column(db.Integer, nullable=False, default=0)
    xp_total = db.Column(db.Integer, nullable=False, default=0)
    diamante = db.Column(db.Integer, nullable=False, default=0)
    vidas = db.Column(db.SmallInteger, nullable=False, default=5)
    vidas_actualizadas = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    salvarrachas = db.Column(db.SmallInteger, nullable=False, default=0)
    racha_actual = db.Column(db.SmallInteger, nullable=False, default=0)
    racha_maxima = db.Column(db.SmallInteger, nullable=False, default=0)
    ultima_actividad = db.Column(db.Date, nullable=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="profile")
    curso_actual = db.relationship("Course")

    @property
    def nivel(self):
        return 1 + self.xp_total // 100


class Stage(db.Model):
    """Etapa de un curso (Primeros pasos, Fundamentos...). Contiene secciones."""
    __tablename__ = "etapas"
    __table_args__ = (db.UniqueConstraint("curso_id", "orden", name="uq_etapa_orden"),)

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id", ondelete="CASCADE", onupdate="CASCADE", name="fk_etapas_curso"), nullable=False)
    orden = db.Column(db.SmallInteger, nullable=False)
    titulo = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(160), nullable=False, default="")
    course = db.relationship("Course", back_populates="etapas")
    secciones = db.relationship("Section", back_populates="etapa", cascade="all, delete-orphan", order_by="Section.orden")


class Section(db.Model):
    """Sección de una etapa (Tablas, Formularios...). Contiene lecciones."""
    __tablename__ = "secciones"
    __table_args__ = (db.UniqueConstraint("etapa_id", "orden", name="uq_seccion_orden"),)

    id = db.Column(db.Integer, primary_key=True)
    etapa_id = db.Column(db.Integer, db.ForeignKey("etapas.id", ondelete="CASCADE", onupdate="CASCADE", name="fk_secciones_etapa"), nullable=False)
    orden = db.Column(db.SmallInteger, nullable=False)
    titulo = db.Column(db.String(80), nullable=False)
    etapa = db.relationship("Stage", back_populates="secciones")
    niveles = db.relationship("Level", back_populates="seccion", cascade="all, delete-orphan", order_by="Level.orden")


class Level(db.Model):
    """Nodo del camino: lección con preguntas, práctica, cofre o trofeo de etapa."""
    __tablename__ = "niveles"
    __table_args__ = (db.UniqueConstraint("seccion_id", "orden", name="uq_nivel_orden"),)

    id = db.Column(db.Integer, primary_key=True)
    seccion_id = db.Column(db.Integer, db.ForeignKey("secciones.id", ondelete="CASCADE", onupdate="CASCADE", name="fk_niveles_seccion"), nullable=False)
    orden = db.Column(db.SmallInteger, nullable=False)
    titulo = db.Column(db.String(80), nullable=False)
    tipo = db.Column(db.Enum("leccion", "practica", "cofre", "trofeo", name="tipo_nivel"), nullable=False, default="leccion")
    xp = db.Column(db.SmallInteger, nullable=False, default=15)
    seccion = db.relationship("Section", back_populates="niveles")
    retos = db.relationship("Challenge", back_populates="nivel", cascade="all, delete-orphan", order_by="Challenge.orden")


class Challenge(db.Model):
    __tablename__ = "retos"
    __table_args__ = (db.UniqueConstraint("nivel_id", "orden", name="uq_reto_orden"),)

    id = db.Column(db.Integer, primary_key=True)
    nivel_id = db.Column(db.Integer, db.ForeignKey("niveles.id", ondelete="CASCADE"), nullable=False)
    orden = db.Column(db.SmallInteger, nullable=False)
    tipo = db.Column(db.String(10), nullable=False, default="opcion")
    enunciado = db.Column(db.Text, nullable=False)
    codigo = db.Column(db.Text, nullable=False, default="")
    opciones = db.Column(TextoJSON, nullable=False, default=list)
    respuesta = db.Column(db.Text, nullable=False, default="")
    explicacion = db.Column(db.Text, nullable=False, default="")
    datos = db.Column(TextoJSON, nullable=False, default=dict)
    nivel = db.relationship("Level", back_populates="retos")


class CompletedLevel(db.Model):
    __tablename__ = "niveles_completados"
    __table_args__ = (db.UniqueConstraint("usuario_id", "nivel_id", name="uq_nivel_completado"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nivel_id = db.Column(db.Integer, db.ForeignKey("niveles.id", ondelete="CASCADE"), nullable=False)
    estrellas = db.Column(db.SmallInteger, nullable=False, default=1)
    veces = db.Column(db.SmallInteger, nullable=False, default=1)
    completado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    nivel = db.relationship("Level")


class LessonDone(db.Model):
    __tablename__ = "lecciones_hechas"
    __table_args__ = (db.UniqueConstraint("usuario_id", "curso_id", "leccion", name="uq_leccion_hecha"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    leccion = db.Column(db.String(120), nullable=False)
    hecha_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    curso = db.relationship("Course")


class DailyActivity(db.Model):
    __tablename__ = "actividad_diaria"
    __table_args__ = (db.UniqueConstraint("usuario_id", "fecha", name="uq_actividad_dia"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha = db.Column(db.Date, nullable=False, index=True)
    xp = db.Column(db.Integer, nullable=False, default=0)
    niveles = db.Column(db.SmallInteger, nullable=False, default=0)
    perfectos = db.Column(db.SmallInteger, nullable=False, default=0)
    lecciones = db.Column(db.SmallInteger, nullable=False, default=0)      # lecciones de Aprende
    mensajes = db.Column(db.SmallInteger, nullable=False, default=0)       # mensajes en Chats
    ia = db.Column(db.SmallInteger, nullable=False, default=0)             # preguntas al tutor de IA
    ejecuciones = db.Column(db.SmallInteger, nullable=False, default=0)    # veces que ejecutó código en Trabajo
    salvada = db.Column(db.Boolean, nullable=False, default=False)         # día sin práctica que cubrió un salvarrachas


class StreakReward(db.Model):
    """Premios de racha ya entregados (cada 10 días, semana perfecta, mes perfecto): así no se dan dos veces."""
    __tablename__ = "premios_racha"
    __table_args__ = (db.UniqueConstraint("usuario_id", "clave", name="uq_premio_racha"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    clave = db.Column(db.String(40), nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class DailyChallenge(db.Model):
    __tablename__ = "desafios_diarios"
    __table_args__ = (db.UniqueConstraint("usuario_id", "clave", "fecha", name="uq_desafio_dia"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    clave = db.Column(db.String(30), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class MonthChallenge(db.Model):
    __tablename__ = "puntos_desafio"
    __table_args__ = (db.UniqueConstraint("usuario_id", "mes", name="uq_puntos_mes"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    mes = db.Column(db.Date, nullable=False)
    puntos = db.Column(db.SmallInteger, nullable=False, default=0)
    premio_dado = db.Column(db.Boolean, nullable=False, default=False)


# Nota: las enumeraciones de moneda siguen admitiendo 'cobre' y 'hierro' solo para poder leer compras antiguas.
# Hoy toda la tienda se paga con diamantes.
class StoreItem(db.Model):
    __tablename__ = "articulos_tienda"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(140), nullable=False)
    icono = db.Column(db.String(8), nullable=False)
    moneda = db.Column(db.Enum("cobre", "hierro", "diamante", name="moneda"), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.Enum("cobre", "hierro", "diamante", name="categoria_articulo"), nullable=False)
    orden = db.Column(db.SmallInteger, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)


class Purchase(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    articulo_id = db.Column(db.Integer, db.ForeignKey("articulos_tienda.id", ondelete="RESTRICT"), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    moneda = db.Column(db.Enum("cobre", "hierro", "diamante", name="moneda"), nullable=False)
    creada_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    articulo = db.relationship("StoreItem")


class Friendship(db.Model):
    __tablename__ = "amistades"
    __table_args__ = (db.UniqueConstraint("de_usuario_id", "a_usuario_id", name="uq_amistad"),)

    id = db.Column(db.Integer, primary_key=True)
    de_usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    a_usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    estado = db.Column(db.Enum("pendiente", "aceptada", name="estado_amistad"), nullable=False, default="pendiente")
    creada_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    de_usuario = db.relationship("User", foreign_keys=[de_usuario_id])
    a_usuario = db.relationship("User", foreign_keys=[a_usuario_id])
    mensajes = db.relationship("Message", back_populates="amistad", cascade="all, delete-orphan", order_by="Message.id")


class Message(db.Model):
    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    amistad_id = db.Column(db.Integer, db.ForeignKey("amistades.id", ondelete="CASCADE"), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    texto = db.Column(db.String(300), nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    # Eliminado por quien lo mandó («Eliminar para todos»): el texto y los adjuntos se borran de verdad
    borrado_en = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    amistad = db.relationship("Friendship", back_populates="mensajes")
    autor = db.relationship("User")


class ChatBorrado(db.Model):
    """«Eliminar chat» solo para quien lo pide (borrado lógico por usuario, como un arreglo deletedBy): esa persona deja
    de ver los mensajes hasta `hasta_mensaje_id`; la otra conserva todo su historial. Si la conversación sigue, los
    mensajes nuevos sí aparecen. Cuando las dos personas borraron, esos mensajes se eliminan de verdad."""
    __tablename__ = "chats_borrados"
    __table_args__ = (db.UniqueConstraint("usuario_id", "amistad_id", name="uq_chat_borrado"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    amistad_id = db.Column(db.Integer, db.ForeignKey("amistades.id", ondelete="CASCADE"), nullable=False, index=True)
    hasta_mensaje_id = db.Column(db.Integer, nullable=False, default=0)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class TutorUsage(db.Model):
    __tablename__ = "uso_tutor"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    ip = db.Column(db.String(45), nullable=False, index=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)


class KnownDevice(db.Model):
    """Navegadores/dispositivos desde los que la persona ya inició sesión (para avisar por correo de uno nuevo)."""
    __tablename__ = "dispositivos_conocidos"
    __table_args__ = (db.UniqueConstraint("usuario_id", "huella", name="uq_dispositivos_usuario_huella"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    huella = db.Column(db.String(64), nullable=False)
    nombre = db.Column(db.String(120), nullable=False, default="")
    ip = db.Column(db.String(45), nullable=False, default="")
    primero = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    ultimo = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class EmailSettings(db.Model):
    """Qué correos quiere recibir cada persona."""
    __tablename__ = "ajustes_correo"

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    seguridad = db.Column(db.Boolean, nullable=False, default=True)   # nuevo dispositivo, cambio de contraseña
    racha = db.Column(db.Boolean, nullable=False, default=True)       # recordatorio para no perder la racha
    novedades = db.Column(db.Boolean, nullable=False, default=False)
    ultimo_recordatorio = db.Column(db.Date, nullable=True)
    nivel_recordatorio = db.Column(db.SmallInteger, nullable=False, default=0)  # 1 = aviso de la tarde, 2 = última oportunidad


class OwnedCosmetic(db.Model):
    """Cosméticos de cada persona (comprados en la tienda o ganados en un cofre)."""
    __tablename__ = "cosmeticos_propios"
    __table_args__ = (db.UniqueConstraint("usuario_id", "clave", name="uq_cosmetico_usuario"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    clave = db.Column(db.String(30), nullable=False)
    origen = db.Column(db.String(12), nullable=False, default="tienda")  # tienda | cofre
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class EquippedCosmetics(db.Model):
    """Lo que cada persona tiene puesto: un cosmético por tipo (o ninguno)."""
    __tablename__ = "cosmeticos_equipados"

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    fondo = db.Column(db.String(30), nullable=True)
    cursor = db.Column("puntero", db.String(30), nullable=True)  # «cursor» es palabra reservada de MySQL
    tema = db.Column(db.String(30), nullable=True)
    marco = db.Column(db.String(30), nullable=True)
    efecto = db.Column(db.String(30), nullable=True)
    dedo = db.Column(db.String(30), nullable=True)  # estela del dedo (celular)
    codi = db.Column(db.String(30), nullable=True)  # accesorio de Codi, la mascota


class OpenedChest(db.Model):
    """Cofres de recompensas ya abiertos."""
    __tablename__ = "cofres_abiertos"
    __table_args__ = (db.UniqueConstraint("usuario_id", "clave", name="uq_cofre_usuario"),)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    clave = db.Column(db.String(30), nullable=False)
    abierto_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class ProfilePhoto(db.Model):
    """Foto de perfil subida por la persona (los bytes, en disco: ALMACEN_ARCHIVOS/<usuario>/foto-<hash>.<ext>)."""
    __tablename__ = "fotos_perfil"

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    hash = db.Column(db.String(64), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    actualizada_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Attachment(db.Model):
    """Archivo adjunto a un mensaje de chat o a una pregunta a la IA. Los bytes son los del almacén de la cuenta
    (archivos_trabajo): adjuntar no duplica nada y lo adjuntado no se borra al limpiar el proyecto."""
    __tablename__ = "adjuntos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    mensaje_id = db.Column(db.Integer, db.ForeignKey("mensajes.id", ondelete="CASCADE"), nullable=True, index=True)
    destino = db.Column(db.String(8), nullable=False, default="chat")  # chat | ia
    hash = db.Column(db.String(64), nullable=False)
    nombre = db.Column(db.String(160), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    tamano = db.Column(db.BigInteger, nullable=False)
    gemini_uri = db.Column(db.String(300), nullable=True)      # archivo subido a la IA (caduca a las 48 h)
    gemini_expira = db.Column(db.DateTime(timezone=True), nullable=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class AppliedMigration(db.Model):
    """Cambios de datos que se aplican una sola vez al actualizar CódigoCamp (p. ej. la nueva economía de diamantes)."""
    __tablename__ = "migraciones"

    clave = db.Column(db.String(40), primary_key=True)
    hecha_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class UserSession(db.Model):
    """Cada inicio de sesión (un navegador o la app en un dispositivo). Si se revoca, ese dispositivo queda fuera."""
    __tablename__ = "sesiones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)   # SHA-256 del identificador (el original solo está en la cookie)
    dispositivo = db.Column(db.String(120), nullable=False, default="")
    ip = db.Column(db.String(45), nullable=False, default="")
    metodo = db.Column(db.String(20), nullable=False, default="contraseña")
    creada = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    ultima = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    revocada = db.Column(db.Boolean, nullable=False, default=False)


class AIConversation(db.Model):
    """Conversación guardada con la IA (como el historial de chats de Claude o ChatGPT)."""
    __tablename__ = "conversaciones_ia"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    titulo = db.Column(db.String(120), nullable=False, default="Conversación nueva")
    fijada = db.Column(db.Boolean, nullable=False, default=False)
    creada = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    actualizada = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    mensajes = db.relationship("AIMessage", back_populates="conversacion", cascade="all, delete-orphan", order_by="AIMessage.id")


class AIMessage(db.Model):
    __tablename__ = "mensajes_ia"

    id = db.Column(db.Integer, primary_key=True)
    conversacion_id = db.Column(db.Integer, db.ForeignKey("conversaciones_ia.id", ondelete="CASCADE"), nullable=False, index=True)
    rol = db.Column(db.String(6), nullable=False)   # yo | tutor
    texto = db.Column(db.Text().with_variant(_LONGTEXT(), "mysql"), nullable=False)
    archivos = db.Column(TextoJSON, nullable=False, default=list)   # nombres de los archivos adjuntos
    creado = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    conversacion = db.relationship("AIConversation", back_populates="mensajes")



class TermsAcceptance(db.Model):
    """Qué versión de los Términos y condiciones aceptó cada persona (onboarding o aviso de la app), cuándo y desde qué IP."""
    __tablename__ = "terminos_aceptados"

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE", name="fk_terminos_usuario"), primary_key=True)
    version = db.Column(db.String(20), nullable=False)
    aceptado = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    ip = db.Column(db.String(45), nullable=False, default="")


class AppLoginCode(db.Model):
    """Código de un solo uso para volver a la app de Android después de entrar con Google en el navegador del celular.
    Google no deja iniciar sesión dentro de una app (WebView): se entra en el navegador y este código pasa la sesión a la app."""
    __tablename__ = "codigos_app"

    id = db.Column(db.Integer, primary_key=True)
    codigo_hash = db.Column(db.String(64), nullable=False, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE", name="fk_codigos_app_usuario"), nullable=False, index=True)
    nuevo = db.Column(db.Boolean, nullable=False, default=False)
    creado = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    usado = db.Column(db.Boolean, nullable=False, default=False)
    # sha256 del secreto que guarda la app mientras espera (así entra aunque el navegador no logre volver a la app)
    espera_hash = db.Column(db.String(64), nullable=True, index=True)


class Traduccion(db.Model):
    """Textos de CódigoCamp traducidos por la IA (retos, lecciones, avisos): se traducen una sola vez y se reutilizan."""
    __tablename__ = "traducciones"
    __table_args__ = (db.UniqueConstraint("idioma", "huella", name="uq_traduccion"),)

    id = db.Column(db.Integer, primary_key=True)
    idioma = db.Column(db.String(5), nullable=False)
    huella = db.Column(db.String(40), nullable=False)   # sha1 del texto original
    original = db.Column(db.Text, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Conector(db.Model):
    """Un computador o celular que su dueño conectó a Trabajo con el Conector de CódigoCamp (codigocamp-conector.py).
    Mientras el programa está abierto en ese equipo, la terminal de Trabajo ejecuta comandos de verdad en la carpeta que
    la persona eligió. Solo se guarda la huella del token (el token completo lo tiene únicamente el equipo)."""
    __tablename__ = "conectores"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE", name="fk_conectores_usuario"), nullable=False, index=True)
    token_hash = db.Column(db.String(64), nullable=False, unique=True)
    equipo = db.Column(db.String(80), nullable=False, default="Mi equipo")
    sistema = db.Column(db.String(40), nullable=False, default="")
    carpeta = db.Column(db.String(400), nullable=False, default="")
    creado = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    ultimo = db.Column(db.DateTime(timezone=True), nullable=True)
