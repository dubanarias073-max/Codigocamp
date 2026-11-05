-- =====================================================================
-- CódigoCamp · Base de datos
-- Ejecuta este script completo en MySQL Workbench (MySQL/MariaDB de XAMPP).
-- Se puede ejecutar varias veces sin romper nada (usa IF NOT EXISTS).
-- No crea usuarios ni contraseñas: la app entra con "root" sin contraseña
-- (XAMPP por defecto). Solo para desarrollo local.
-- =====================================================================
Drop database IF EXISTS codigocamp;
CREATE DATABASE  codigocamp
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE codigocamp;

-- ---------------------------------------------------------------------
-- 1. USUARIOS (registro e inicio de sesión)
--    El correo es único sin distinguir mayúsculas (por el collation).
--    Guarda siempre el hash de bcrypt, nunca la contraseña.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
  id             INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nombre         VARCHAR(50)   NOT NULL,
  email          VARCHAR(254)  NOT NULL,
  password_hash  VARCHAR(255)  NOT NULL,
  activo         TINYINT(1)    NOT NULL DEFAULT 1,
  creado_en      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso  TIMESTAMP     NULL DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuarios_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 2. PROGRESO (XP, nivel, vidas y racha) · una fila por usuario
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS progreso_usuario (
  usuario_id        INT UNSIGNED      NOT NULL,
  xp                INT UNSIGNED      NOT NULL DEFAULT 0,
  nivel             SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  vidas             TINYINT UNSIGNED  NOT NULL DEFAULT 5,
  racha_actual      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  racha_maxima      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  ultima_actividad  DATE              NULL DEFAULT NULL,
  PRIMARY KEY (usuario_id),
  CONSTRAINT fk_progreso_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 3. LECCIONES VISTAS
--    El contenido de las lecciones vive en los archivos de la web, así que
--    aquí solo se guarda una clave de texto (por ejemplo "python", "css-flexbox").
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lecciones_vistas (
  usuario_id  INT UNSIGNED  NOT NULL,
  leccion     VARCHAR(80)   NOT NULL,
  visto_en    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, leccion),
  CONSTRAINT fk_lecciones_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 4. RETOS COMPLETADOS
--    Un reto solo se completa una vez por usuario: evita ganar XP repetido.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS retos_completados (
  usuario_id     INT UNSIGNED      NOT NULL,
  reto           VARCHAR(80)       NOT NULL,
  xp_ganado      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  intentos       SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  completado_en  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, reto),
  CONSTRAINT fk_retos_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 5. USO DEL TUTOR (control de costos y límite por minuto)
--    No guarda el texto de las conversaciones (privacidad, RNF-11).
--    usuario_id es NULL para invitados; en ese caso se usa la IP.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS uso_tutor (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario_id  INT UNSIGNED    NULL DEFAULT NULL,
  ip          VARCHAR(45)     NOT NULL,
  creado_en   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_uso_usuario_fecha (usuario_id, creado_en),
  KEY idx_uso_ip_fecha (ip, creado_en),
  CONSTRAINT fk_uso_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comprobación rápida: debe listar las 5 tablas.
SHOW TABLES;