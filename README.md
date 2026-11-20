# CódigoCamp

**CódigoCamp** es una plataforma web interactiva en español para aprender a programar. Combina lecciones teóricas, retos prácticos al estilo Duolingo, un editor tipo VS Code integrado en el navegador (**Trabajo**), un tutor con IA (Gemini), chat en tiempo real entre amigos, cofres y una tienda de recompensas.

- **Backend:** Python (Flask + SQLAlchemy) con MySQL o MariaDB.
- **Frontend:** HTML, CSS y JavaScript puro (servido directamente por Flask desde `frontend/`).

---

## Contenido

1. [Requisitos](#1-requisitos)
2. [Instalación en local (Windows + XAMPP)](#2-instalación-en-local-windows--xampp)
3. [Variables de entorno (`backend/.env`)](#3-variables-de-entorno-backendenv)
4. [Comandos útiles de administración](#4-comandos-útiles-de-administración)
5. [Funcionalidades principales](#5-funcionalidades-principales)
6. [Trabajo: el editor tipo VS Code](#6-trabajo-el-editor-tipo-vs-code)
7. [Diagrama de base de datos en MySQL Workbench](#7-diagrama-de-base-de-datos-en-mysql-workbench)
8. [Instalar como aplicación (PWA) y widgets](#8-instalar-como-aplicación-pwa-y-widgets)
9. [Estructura del proyecto](#9-estructura-del-proyecto)
10. [Ejecución de pruebas](#10-ejecución-de-pruebas)
11. [Solución de problemas](#11-solución-de-problemas)

> 🚀 **¿Vas a desplegar en el servidor del SENA con Tailscale?** Sigue la guía en [Readme2.md](Readme2.md).

---

## 1. Requisitos

| Herramienta | Propósito |
|---|---|
| **Python 3.11+** | Ejecutar el servidor backend en Flask. |
| **XAMPP (MySQL/MariaDB) o MySQL 8.4** | Almacenar la base de datos `codigocamp`. |
| **MySQL Workbench** *(opcional)* | Visualizar tablas y generar el diagrama entidad-relación. |
| **Navegador moderno** | Chrome, Edge, Firefox o Safari. |
| **API Key de Gemini** *(opcional)* | Habilitar el tutor y el asistente de código ([Google AI Studio](https://aistudio.google.com/apikey)). |

---

## 2. Instalación en local (Windows + XAMPP)

### 2.1 Crear la base de datos

1. Abre el panel de control de **XAMPP** e inicia el módulo **MySQL**.
2. Abre **MySQL Workbench** y conéctate a `127.0.0.1` en el puerto `3306` con el usuario `root`.
3. Abre el archivo `base de datos/codigocamp.sql` (**File → Open SQL Script**) y ejecútalo con el ícono del rayo ⚡ (**Execute**).

*(Este paso solo se hace la primera vez. Al iniciar Flask posteriormente, el sistema actualiza columnas nuevas automáticamente sin borrar datos).*

### 2.2 Preparar el entorno virtual

Abre una terminal dentro de la carpeta del proyecto:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

*(En Linux o macOS, activa el entorno con `source venv/bin/activate`).*

### 2.3 Configurar `backend/.env`

Crea un archivo llamado `.env` dentro de `backend/` (puedes usar `backend/.env.example` como base):

```env
# --- Base de datos (XAMPP por defecto) ---
DATABASE_URL="mysql+pymysql://root:@127.0.0.1:3306/codigocamp?charset=utf8mb4"

# --- Inteligencia Artificial (opcional) ---
GEMINI_API_KEY="<TU_API_KEY_DE_GEMINI>"
GEMINI_MODEL="gemini-3.5-flash-lite"

# --- Correo electrónico con Gmail (opcional, requiere contraseña de aplicación) ---
SMTP_PORT="587"
SMTP_USERNAME="<tu_correo@gmail.com>"
SMTP_APP_PASSWORD="<tu_contraseña_de_aplicación>"
SMTP_FROM="<tu_correo@gmail.com>"

# --- Inicio de sesión con Google (opcional) ---
GOOGLE_CLIENT_ID="<TU_GOOGLE_CLIENT_ID>"
GOOGLE_CLIENT_SECRET="<TU_GOOGLE_CLIENT_SECRET>"

# --- URLs permitidas (separadas por coma si usas túnel) ---
APP_URL="http://localhost:5000"
GOOGLE_REDIRECT_URI="http://localhost:5000/auth/google/callback/"
```

#### Configuración en Google Cloud Console (si usas login con Google)

En [Google Cloud Console → Credenciales](https://console.cloud.google.com/apis/credentials), dentro de tu **ID de cliente OAuth 2.0**:

| Campo | URL exacta a registrar |
|---|---|
| **Orígenes de JavaScript autorizados** | `http://localhost:5000` |
| **URI de redireccionamiento autorizados** | `http://localhost:5000/auth/google/callback/` |

> ⚠️ **Importante:** La URI de redireccionamiento debe terminar exactamente con la barra `/`. Además, nunca subas el archivo `.env` ni tus claves reales a GitHub.

### 2.4 Poblar los cursos y retos

```powershell
flask --app app check-retos
flask --app app seed-retos
```

- `check-retos`: Valida la integridad de los ejercicios.
- `seed-retos`: Carga las etapas, lecciones y retos de los 23 cursos (tarda ~1 minuto).

### 2.5 Arrancar el servidor

```powershell
flask --app app run
```

Abre **<http://localhost:5000/>** en tu navegador. *(Usa `localhost` y no `127.0.0.1` para que la sesión de Google OAuth coincida con la URL autorizada).*

---

## 3. Variables de entorno (`backend/.env`)

| Variable | Por defecto | Descripción |
|---|---|---|
| `DEBUG` | `1` | `1` en local, `0` en producción (activa cookies seguras HTTPS). |
| `SECRET_KEY` | — | Clave secreta para firmar sesiones (obligatoria en producción). |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | `127.0.0.1`, `3306`, `codigocamp`, `root`, `""` | Credenciales individuales de MySQL (alternativa a `DATABASE_URL`). |
| `DATABASE_URL` | — | Cadena de conexión completa SQLAlchemy (`mysql+pymysql://...`). |
| `GEMINI_API_KEY` | — | Clave de API de Google AI Studio para el tutor y editor IA. |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Modelo de Gemini a utilizar. |
| `GOOGLE_CLIENT_ID` / `SECRET` | — | Credenciales OAuth 2.0 para «Iniciar sesión con Google». |
| `GOOGLE_REDIRECT_URI` | automático | URIs de callback registradas en Google Cloud, separadas por coma. |
| `SMTP_USERNAME`, `SMTP_APP_PASSWORD`, `SMTP_FROM` | — | Configuración de correo saliente (si se omite, los correos se guardan como `.eml` en `almacen_archivos/correos/`). |
| `APP_URL` | `http://127.0.0.1:5000` | URLs base para enlaces en correos (recuperar clave, avisos de racha). |
| `PROXY_CONFIABLE` | `0` | Cambiar a `1` cuando se usa detrás de Tailscale o Nginx para detectar HTTPS e IP real. |
| `RECORDATORIOS_AUTO` | `1` | Activa (`1`) o desactiva (`0`) los correos automáticos de racha a las 18:00 y 21:00. |
| `ALMACEN_ARCHIVOS` | `backend/almacen_archivos` | Directorio de fotos de perfil, adjuntos de chat y proyectos de Trabajo. |
| `CUOTA_ARCHIVOS_GB` / `MAX_ARCHIVO_MB` | `10` / `1024` | Límites de almacenamiento por usuario y tamaño por archivo. |
| `BD_EXTERNAS` | igual a `DEBUG` | Permite conectar proyectos de **Trabajo** a bases de datos reales del servidor. |
| `PISTON_URL` / `PISTON_KEY` | — | Endpoint opcional para compilar lenguajes externos (Java, C, C++, Go, Rust). |

---

## 4. Comandos útiles de administración

Ejecutar dentro de `backend/` con el entorno virtual activado:

| Comando | Acción |
|---|---|
| `flask --app app run` | Inicia el servidor web en modo desarrollo. |
| `flask --app app check-retos` | Verifica que no haya errores de sintaxis en los cursos. |
| `flask --app app seed-retos` | Carga el catálogo inicial de cursos en una base vacía. |
| `flask --app app sync-retos` | Agrega cursos o lecciones nuevas sin borrar el progreso de los usuarios. |
| `flask --app app seed-retos --reset` | ⚠️ Reinicia por completo el catálogo y borra el progreso de niveles. |
| `flask --app app migrar-camino` | Adapta el progreso de los usuarios tras reestructurar etapas de un curso. |
| `flask --app app reparar-workbench` | Ajusta restricciones para generar el diagrama en MySQL Workbench. |
| `flask --app app recordar-rachas [--nivel 2]` | Fuerza el envío manual de notificaciones de racha. |
| `flask --app app probar-correo correo@ejemplo.com` | Envía un correo de prueba para validar SMTP. |
| `flask --app app probar-ia` | Valida la conexión y cuota de `GEMINI_API_KEY`. |
| `flask --app app limpiar-archivos` | Elimina archivos huérfanos del disco. |
| `python herramientas/generar_aprende.py <curso>` | Regenera las lecciones teóricas de un curso específico. |
| `python herramientas/puente_bd.py` | Conecta una instancia remota de CódigoCamp con bases de datos locales. |

---

## 5. Funcionalidades principales

- **23 Cursos completos:** HTML, CSS, JavaScript, TypeScript, Python, Java, C#, Kotlin, Swift, PHP, Ruby, Go, Rust, C, C++, SQL, Bases de Datos, NoSQL (MongoDB, Redis, etc.), Terminales, Git, GitHub, Docker y Node.js.
- **Seguridad y sesiones:** Registro tradicional o con Google OAuth, recuperación de contraseña con tokens de 30 minutos, gestión activa de dispositivos conectados y limpieza automática de datos locales al cerrar sesión.
- **Gamificación:** Sistema de rachas diarias, escudos salvarrachas (máx. 2), encargos diarios, cofres de recompensa, tienda de cosméticos (temas, marcos, cursores, fondos animados) y perfil personalizable.
- **Social e IA:** Chat entre amigos con envío de archivos (hasta 1 GB) y tutor virtual impulsado por Gemini con historial de conversaciones.

---

## 6. Trabajo: el editor tipo VS Code

El módulo **Trabajo** ofrece un entorno de desarrollo completo en el navegador:

- **Editor Monaco:** Resaltado de sintaxis, múltiples pestañas, búsqueda global (`Ctrl+Shift+F`) y paleta de comandos (`Ctrl+Shift+P`).
- **Terminal y Git:** Comandos Bash simulados, control de versiones (`clone`, `commit`, `branch`, `merge`, `pull`, `push`) e indicadores visuales de estado (`M`, `U`, `!`).
- **Ejecución:** Soporte para Python en navegador (Pyodide), Vite/React, vistas previas de FastAPI/Flask y respaldo automático en SQLite (`.codigocamp/bd/`) si no hay conexión a MySQL.

---

## 7. Diagrama de base de datos en MySQL Workbench

1. En MySQL Workbench, selecciona **Database → Reverse Engineer…** (`Ctrl+R`).
2. Elige tu conexión local, selecciona el esquema `codigocamp` y avanza hasta **Finish**.
3. Si Workbench presenta cierres inesperados, ejecuta `flask --app app reparar-workbench` y repite el proceso.

---

## 8. Instalar como aplicación (PWA) y widgets

CódigoCamp puede instalarse como aplicación de escritorio o móvil (requiere HTTPS en producción o `localhost` en desarrollo):

- **Windows / Linux (Chrome o Edge):** Haz clic en el ícono de instalar (`⊕`) en la barra de direcciones.
- **macOS (Safari 17+):** **Archivo → Agregar al Dock**.
- **Android / iOS:** Menú del navegador → **Instalar aplicación** o **Agregar a pantalla de inicio**.
- **Widgets en Windows 11:** Presiona `Win + W` y añade los widgets de *Tu racha*, *Meta de hoy* y *Calendario*.

---

## 9. Estructura del proyecto

```text
Codigocamp/
├── base de datos/
│   └── codigocamp.sql          # Esquema SQL inicial
├── backend/
│   ├── app.py                  # Punto de entrada Flask
│   ├── models.py               # Modelos ORM (SQLAlchemy)
│   ├── comandos.py             # Comandos CLI de Flask
│   ├── seguridad.py            # Autenticación, CSRF y sesiones
│   ├── rutas/                  # Endpoints de la API REST
│   ├── servicios/              # Lógica de negocio (correo, IA, tienda, etc.)
│   ├── retos/                  # Definición de cursos y ejercicios
│   ├── herramientas/           # Scripts auxiliares
│   ├── .env.example            # Plantilla segura de variables de entorno
│   └── tests/                  # Pruebas unitarias del backend
└── frontend/
    ├── pages/                  # Vistas HTML
    ├── js/                     # Lógica cliente y editor Trabajo
    ├── css/, img/, widgets/    # Recursos estáticos
    ├── manifest.webmanifest    # Configuración PWA
    └── tests/                  # Pruebas del frontend
```

---

## 10. Ejecución de pruebas

```powershell
# Pruebas del backend (desde backend/)
python -m unittest discover -s tests

# Pruebas del frontend (desde frontend/)
node --test tests/*.test.mjs
```

---

## 11. Solución de problemas

| Síntoma / Error | Causa | Solución |
|---|---|---|
| `Can't connect to MySQL server` | Servicio apagado o puerto incorrecto | Inicia MySQL y verifica `DB_HOST` y `DB_PORT` en `.env`. |
| `Access denied for user 'codigocamp'@'172.17.0.1'` | Usuario sin permisos desde red Docker | Otorga permisos a `'codigocamp'@'%'` en MySQL (ver [Readme2.md](Readme2.md#33-asegurar-permisos-del-usuario-codigocamp)). |
| `Error 400: redirect_uri_mismatch` | URL de callback distinta en Google Cloud | Verifica que `GOOGLE_REDIRECT_URI` y Google Cloud tengan la misma URL con `/` al final. |
| Inicio sin cursos | Base de datos recién creada sin datos | Ejecuta `flask --app app seed-retos`. |
| Tutor IA deshabilitado | Falta clave de Gemini | Configura `GEMINI_API_KEY` en `.env` y reinicia Flask. |
