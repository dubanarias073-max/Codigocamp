from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")


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
    TEMAS = {"auto", "claro", "oscuro"}  # auto = predeterminado (sigue el tema del dispositivo)

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE", name="fk_perfiles_usuario"), unique=True, nullable=False)
    rol = db.Column(db.String(12), nullable=False, default="")
    intereses = db.Column(db.JSON, nullable=False, default=list)
    nivel_previo = db.Column(db.String(10), nullable=False, default="")
    curso_actual_id = db.Column(db.Integer, db.ForeignKey("cursos.id", ondelete="SET NULL", onupdate="CASCADE", name="fk_perfiles_curso_actual"), nullable=True)
    meta_minutos = db.Column(db.SmallInteger, nullable=False, default=10)
    onboarding_completo = db.Column(db.Boolean, nullable=False, default=False)
    tema = db.Column(db.Enum("auto", "claro", "oscuro", name="tema"), nullable=False, default="auto")
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
    """Nodo del camino: lección (10 preguntas), práctica (repaso de la sección), cofre o trofeo (examen de la etapa)."""
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
    opciones = db.Column(db.JSON, nullable=False, default=list)
    respuesta = db.Column(db.Text, nullable=False, default="")
    explicacion = db.Column(db.Text, nullable=False, default="")
    datos = db.Column(db.JSON, nullable=False, default=dict)
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
    amistad = db.relationship("Friendship", back_populates="mensajes")
    autor = db.relationship("User")


class TutorUsage(db.Model):
    __tablename__ = "uso_tutor"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    ip = db.Column(db.String(45), nullable=False, index=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
