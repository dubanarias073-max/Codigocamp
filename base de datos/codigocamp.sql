-- =====================================================================
--  CodigoCamp · esquema MySQL / MariaDB (XAMPP) listo para MySQL Workbench
-- =====================================================================
--  Como usarlo
--    1. Inicia MySQL en XAMPP y conectate desde Workbench a 127.0.0.1.
--    2. File > Open SQL Script... > este archivo > Execute (rayo).
--    3. Para ver el diagrama: Database > Reverse Engineer... (Ctrl+R),
--       elige la conexion, marca la base `codigocamp` y termina el asistente.
--       Todas las relaciones aparecen porque cada clave foranea tiene nombre.
--    4. Desde la carpeta backend:  flask --app app seed-retos
--       (carga etapas, secciones, lecciones y preguntas desde backend/retos/*.py)
--
--  Si ya habias creado la base con una version anterior de este archivo,
--  descomenta la siguiente linea UNA VEZ (borra los datos de prueba):
-- =====================================================================
DROP DATABASE IF EXISTS codigocamp;

CREATE DATABASE IF NOT EXISTS codigocamp
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE codigocamp;
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
--  Convenciones
--    * Tablas en plural y en espanol; clave primaria `id`.
--    * Toda clave foranea se llama `<tabla_referenciada>_id` (usuario_id,
--      curso_id...) y su restriccion `fk_<tabla>_<referencia>`.
--    * Cada FK tiene su indice `idx_<tabla>_<columna>`.
--    * Fechas en UTC (DATETIME).
-- ---------------------------------------------------------------------


-- ======================== CUENTAS ====================================

CREATE TABLE usuarios (
  id            INT          NOT NULL AUTO_INCREMENT,
  email         VARCHAR(150) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  nombre        VARCHAR(50)  NOT NULL,
  activo        TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuarios_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Cuentas de acceso';


-- ======================== CATALOGO ===================================

CREATE TABLE cursos (
  id          INT          NOT NULL AUTO_INCREMENT,
  slug        VARCHAR(30)  NOT NULL COMMENT 'Identificador en la URL: html, python...',
  nombre      VARCHAR(40)  NOT NULL,
  tipo        ENUM('web','lenguaje','bd') NOT NULL DEFAULT 'lenguaje',
  sigla       VARCHAR(6)   NOT NULL,
  color       VARCHAR(7)   NOT NULL DEFAULT '#4ade80' COMMENT 'Color hexadecimal',
  descripcion VARCHAR(120) NOT NULL DEFAULT '',
  orden       SMALLINT     NOT NULL DEFAULT 0,
  activo      TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY uq_cursos_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Lenguajes y areas que se pueden estudiar';

CREATE TABLE etapas (
  id          INT          NOT NULL AUTO_INCREMENT,
  curso_id    INT          NOT NULL,
  orden       SMALLINT     NOT NULL,
  titulo      VARCHAR(80)  NOT NULL COMMENT 'Primeros pasos, Fundamentos, Intermedio...',
  descripcion VARCHAR(160) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  UNIQUE KEY uq_etapa_orden (curso_id, orden),
  CONSTRAINT fk_etapas_curso FOREIGN KEY (curso_id)
    REFERENCES cursos (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Etapas de cada curso (como en Duolingo); cada una tiene varias secciones';

CREATE TABLE secciones (
  id       INT         NOT NULL AUTO_INCREMENT,
  etapa_id INT         NOT NULL,
  orden    SMALLINT    NOT NULL,
  titulo   VARCHAR(80) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_seccion_orden (etapa_id, orden),
  CONSTRAINT fk_secciones_etapa FOREIGN KEY (etapa_id)
    REFERENCES etapas (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Secciones de una etapa; cada una tiene varias lecciones y un cofre final';

CREATE TABLE niveles (
  id         INT         NOT NULL AUTO_INCREMENT,
  seccion_id INT         NOT NULL,
  orden      SMALLINT    NOT NULL,
  titulo     VARCHAR(80) NOT NULL,
  tipo       ENUM('leccion','practica','cofre','trofeo') NOT NULL DEFAULT 'leccion'
             COMMENT 'leccion = 10 preguntas; practica = repaso de la seccion; cofre = premio; trofeo = examen de la etapa',
  xp         SMALLINT    NOT NULL DEFAULT 15,
  PRIMARY KEY (id),
  UNIQUE KEY uq_nivel_orden (seccion_id, orden),
  CONSTRAINT fk_niveles_seccion FOREIGN KEY (seccion_id)
    REFERENCES secciones (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Nodos del camino: lecciones, practicas, cofres y trofeos (examen de etapa)';

CREATE TABLE retos (
  id          INT         NOT NULL AUTO_INCREMENT,
  nivel_id    INT         NOT NULL,
  orden       SMALLINT    NOT NULL,
  tipo        VARCHAR(10) NOT NULL DEFAULT 'opcion' COMMENT 'opcion, completar, ordenar, error, codigo, caso',
  enunciado   TEXT        NOT NULL,
  codigo      TEXT        NOT NULL,
  opciones    JSON        NOT NULL,
  respuesta   TEXT        NOT NULL,
  explicacion TEXT        NOT NULL,
  datos       JSON        NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_reto_orden (nivel_id, orden),
  CONSTRAINT fk_retos_nivel FOREIGN KEY (nivel_id)
    REFERENCES niveles (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Preguntas de cada leccion (nivel)';


-- ======================== PERFIL Y PROGRESO ==========================

CREATE TABLE perfiles (
  id                  INT         NOT NULL AUTO_INCREMENT,
  usuario_id          INT         NOT NULL,
  rol                 VARCHAR(12) NOT NULL DEFAULT '',
  intereses           JSON        NOT NULL,
  nivel_previo        VARCHAR(10) NOT NULL DEFAULT '',
  curso_actual_id     INT         NULL,
  meta_minutos        SMALLINT    NOT NULL DEFAULT 10,
  onboarding_completo TINYINT(1)  NOT NULL DEFAULT 0,
  tema                ENUM('auto','claro','oscuro') NOT NULL DEFAULT 'auto'
                      COMMENT 'auto = predeterminado, sigue el tema del dispositivo',
  alias               VARCHAR(20) NULL,
  codigo              VARCHAR(8)  NULL COMMENT 'ID para que te agreguen como amigo',
  avatar              VARCHAR(8)  NULL COMMENT 'Emoji elegido en el perfil',
  xp                  INT         NOT NULL DEFAULT 0 COMMENT 'XP del nivel actual',
  xp_total            INT         NOT NULL DEFAULT 0,
  diamante            INT         NOT NULL DEFAULT 0,
  vidas               SMALLINT    NOT NULL DEFAULT 5,
  vidas_actualizadas  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  salvarrachas        SMALLINT    NOT NULL DEFAULT 0,
  racha_actual        SMALLINT    NOT NULL DEFAULT 0,
  racha_maxima        SMALLINT    NOT NULL DEFAULT 0,
  ultima_actividad    DATE        NULL,
  creado_en           DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_perfiles_usuario (usuario_id),
  UNIQUE KEY uq_perfiles_alias (alias),
  UNIQUE KEY uq_perfiles_codigo (codigo),
  KEY idx_perfiles_curso_actual (curso_actual_id),
  CONSTRAINT fk_perfiles_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_perfiles_curso_actual FOREIGN KEY (curso_actual_id)
    REFERENCES cursos (id) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT ck_perfiles_meta CHECK (meta_minutos IN (5, 10, 15, 30)),
  CONSTRAINT ck_perfiles_vidas CHECK (vidas >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Datos de aprendizaje, monedas y preferencias de cada usuario (1 a 1 con usuarios)';

CREATE TABLE niveles_completados (
  id            INT      NOT NULL AUTO_INCREMENT,
  usuario_id    INT      NOT NULL,
  nivel_id      INT      NOT NULL,
  estrellas     SMALLINT NOT NULL DEFAULT 1,
  veces         SMALLINT NOT NULL DEFAULT 1,
  completado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_nivel_completado (usuario_id, nivel_id),
  KEY idx_niveles_completados_nivel (nivel_id),
  CONSTRAINT fk_niveles_completados_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_niveles_completados_nivel FOREIGN KEY (nivel_id)
    REFERENCES niveles (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT ck_niveles_completados_estrellas CHECK (estrellas BETWEEN 0 AND 3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Niveles que cada usuario ya termino';

CREATE TABLE lecciones_hechas (
  id         INT          NOT NULL AUTO_INCREMENT,
  usuario_id INT          NOT NULL,
  curso_id   INT          NOT NULL,
  leccion    VARCHAR(120) NOT NULL COMMENT 'Clave de la leccion estatica del frontend',
  hecha_en   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_leccion_hecha (usuario_id, curso_id, leccion),
  KEY idx_lecciones_hechas_curso (curso_id),
  CONSTRAINT fk_lecciones_hechas_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_lecciones_hechas_curso FOREIGN KEY (curso_id)
    REFERENCES cursos (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Lecciones de aula completadas';

CREATE TABLE actividad_diaria (
  id         INT      NOT NULL AUTO_INCREMENT,
  usuario_id INT      NOT NULL,
  fecha      DATE     NOT NULL,
  xp         INT      NOT NULL DEFAULT 0,
  niveles    SMALLINT NOT NULL DEFAULT 0,
  perfectos  SMALLINT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_actividad_dia (usuario_id, fecha),
  KEY idx_actividad_diaria_fecha (fecha),
  CONSTRAINT fk_actividad_diaria_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Resumen de XP y niveles por dia';

CREATE TABLE desafios_diarios (
  id         INT         NOT NULL AUTO_INCREMENT,
  usuario_id INT         NOT NULL,
  clave      VARCHAR(30) NOT NULL COMMENT 'xp30, niveles2, perfecto',
  fecha      DATE        NOT NULL,
  creado_en  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_desafio_dia (usuario_id, clave, fecha),
  CONSTRAINT fk_desafios_diarios_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Desafios diarios cuyo premio ya se entrego';

CREATE TABLE puntos_desafio (
  id          INT        NOT NULL AUTO_INCREMENT,
  usuario_id  INT        NOT NULL,
  mes         DATE       NOT NULL COMMENT 'Primer dia del mes',
  puntos      SMALLINT   NOT NULL DEFAULT 0,
  premio_dado TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_puntos_mes (usuario_id, mes),
  CONSTRAINT fk_puntos_desafio_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Puntos del desafio mensual';


-- ======================== TIENDA =====================================

CREATE TABLE articulos_tienda (
  id          INT          NOT NULL AUTO_INCREMENT,
  clave       VARCHAR(30)  NOT NULL,
  nombre      VARCHAR(50)  NOT NULL,
  descripcion VARCHAR(140) NOT NULL,
  icono       VARCHAR(8)   NOT NULL,
  moneda      ENUM('diamante') NOT NULL,
  precio      INT          NOT NULL,
  categoria   ENUM('diamante') NOT NULL,
  orden       SMALLINT     NOT NULL DEFAULT 0,
  activo      TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY uq_articulos_tienda_clave (clave),
  CONSTRAINT ck_articulos_tienda_precio CHECK (precio > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Objetos que se compran con diamantes';

CREATE TABLE compras (
  id          INT      NOT NULL AUTO_INCREMENT,
  usuario_id  INT      NOT NULL,
  articulo_id INT      NOT NULL,
  precio      INT      NOT NULL COMMENT 'Precio pagado en ese momento',
  moneda      ENUM('diamante') NOT NULL,
  creada_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_compras_usuario (usuario_id),
  KEY idx_compras_articulo (articulo_id),
  CONSTRAINT fk_compras_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_compras_articulo FOREIGN KEY (articulo_id)
    REFERENCES articulos_tienda (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Historial de compras';


-- ======================== SOCIAL =====================================

CREATE TABLE amistades (
  id            INT      NOT NULL AUTO_INCREMENT,
  de_usuario_id INT      NOT NULL COMMENT 'Quien envia la solicitud',
  a_usuario_id  INT      NOT NULL COMMENT 'Quien la recibe',
  estado        ENUM('pendiente','aceptada') NOT NULL DEFAULT 'pendiente',
  creada_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_amistad (de_usuario_id, a_usuario_id),
  KEY idx_amistades_a_usuario (a_usuario_id),
  CONSTRAINT fk_amistades_de_usuario FOREIGN KEY (de_usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_amistades_a_usuario FOREIGN KEY (a_usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Solicitudes y amistades entre usuarios';

CREATE TABLE mensajes (
  id          INT          NOT NULL AUTO_INCREMENT,
  amistad_id  INT          NOT NULL,
  autor_id    INT          NOT NULL COMMENT 'Usuario que escribio el mensaje',
  texto       VARCHAR(300) NOT NULL,
  leido       TINYINT(1)   NOT NULL DEFAULT 0,
  creado_en   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_mensajes_amistad (amistad_id),
  KEY idx_mensajes_autor (autor_id),
  CONSTRAINT fk_mensajes_amistad FOREIGN KEY (amistad_id)
    REFERENCES amistades (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_mensajes_autor FOREIGN KEY (autor_id)
    REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Chat entre amigos';


-- ======================== TUTOR IA ===================================

CREATE TABLE uso_tutor (
  id         INT         NOT NULL AUTO_INCREMENT,
  usuario_id INT         NULL COMMENT 'NULL si el usuario fue eliminado',
  ip         VARCHAR(45) NOT NULL,
  creado_en  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_uso_tutor_usuario (usuario_id),
  KEY idx_uso_tutor_ip (ip),
  KEY idx_uso_tutor_creado_en (creado_en),
  CONSTRAINT fk_uso_tutor_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Consultas al tutor, para limitar el uso';


-- ======================== DATOS INICIALES ============================
-- Las cuentas y el progreso empiezan vacios; se crean al registrarse.

INSERT INTO articulos_tienda (id, clave, nombre, descripcion, icono, moneda, precio, categoria, orden, activo) VALUES
  (1, 'vida', 'Una vida', 'Recupera una vida al instante.', '❤️', 'diamante', 1, 'diamante', 1, 1),
  (2, 'vidas_llenas', 'Recarga de vidas', 'Rellena tus vidas hasta cinco.', '💖', 'diamante', 3, 'diamante', 2, 1),
  (3, 'salvarracha', 'Salvarrachas', 'Protege tu racha durante un día sin practicar. Máximo 2.', '🧊', 'diamante', 2, 'diamante', 3, 1),
  (4, 'kit_experto', 'Kit experto', 'Tres vidas y una salvarracha.', '💎', 'diamante', 4, 'diamante', 4, 1);

INSERT INTO cursos (id, slug, nombre, tipo, sigla, color, descripcion, orden, activo) VALUES
  (1, 'html', 'HTML', 'web', 'HTML', '#f97316', 'Estructura de páginas web', 1, 1),
  (2, 'css', 'CSS', 'web', 'CSS', '#2dd4bf', 'Estilos y diseño de páginas', 2, 1),
  (3, 'javascript', 'JavaScript', 'lenguaje', 'JS', '#fbbf24', 'El lenguaje de la web', 3, 1),
  (4, 'python', 'Python', 'lenguaje', 'PY', '#60a5fa', 'Datos, IA y automatización', 4, 1),
  (5, 'sql', 'SQL', 'bd', 'SQL', '#f472b6', 'Consultar y modificar datos', 5, 1),
  (6, 'bd', 'Bases de datos', 'bd', 'BD', '#f472b6', 'SQL, MongoDB, Redis y más', 6, 1),
  (7, 'typescript', 'TypeScript', 'lenguaje', 'TS', '#38bdf8', 'JavaScript con tipos', 7, 1),
  (8, 'java', 'Java', 'lenguaje', 'JV', '#fb923c', 'Apps y sistemas grandes', 8, 1),
  (9, 'csharp', 'C#', 'lenguaje', 'C#', '#a78bfa', 'Videojuegos con Unity', 9, 1),
  (10, 'kotlin', 'Kotlin', 'lenguaje', 'KT', '#c084fc', 'Apps para Android', 10, 1),
  (11, 'swift', 'Swift', 'lenguaje', 'SW', '#fb7185', 'Apps para iPhone', 11, 1),
  (12, 'php', 'PHP', 'lenguaje', 'PHP', '#a5b4fc', 'Páginas con servidor', 12, 1),
  (13, 'ruby', 'Ruby', 'lenguaje', 'RB', '#f87171', 'Código fácil de leer', 13, 1),
  (14, 'go', 'Go', 'lenguaje', 'GO', '#22d3ee', 'Servidores rápidos', 14, 1),
  (15, 'rust', 'Rust', 'lenguaje', 'RS', '#fdba74', 'Rápido y seguro', 15, 1),
  (16, 'c', 'C', 'lenguaje', 'C', '#94a3b8', 'Cerca de la máquina', 16, 1),
  (17, 'cpp', 'C++', 'lenguaje', 'C++', '#818cf8', 'Rendimiento y videojuegos', 17, 1);

-- Siguiente paso, desde la carpeta backend:
--   flask --app app seed-retos
