# CódigoCamp

**CódigoCamp** es una plataforma web interactiva en español para aprender a programar. Combina lecciones teóricas, retos prácticos al estilo Duolingo, un editor tipo VS Code integrado en el navegador (**Trabajo**), un tutor con IA (Gemini), chat en tiempo real entre amigos, cofres y una tienda de recompensas.

- **Backend:** Python (Flask + SQLAlchemy) con MySQL o MariaDB (XAMPP).
- **Frontend:** HTML, CSS y JavaScript puro sin compilación (servido directamente por Flask desde `frontend/`).

---

## Contenido

1. [Requisitos](#1-requisitos)
2. [Instalación paso a paso en local (Windows + XAMPP)](#2-instalación-paso-a-paso-en-local-windows--xampp)
3. [Configuración de variables (`backend/.env`)](#3-configuración-de-variables-backendenv)
4. [Comandos útiles](#4-comandos-útiles)
5. [Qué incluye la plataforma](#5-qué-incluye-la-plataforma)
6. [Trabajo: el editor tipo VS Code](#6-trabajo-el-editor-tipo-vs-code)
7. [Ver el diagrama de la base en MySQL Workbench](#7-ver-el-diagrama-de-la-base-en-mysql-workbench)
8. [Instalar como app y widgets](#8-instalar-como-app-y-widgets)
9. [Estructura del proyecto](#9-estructura-del-proyecto)
10. [Pruebas](#10-pruebas)
11. [Solución de problemas](#11-solución-de-problemas)

> 🚀 **¿Quieres publicarlo en la máquina virtual del SENA con Docker y Tailscale?** Sigue la guía de despliegue en [Readme2.md](Readme2.md).

---

## 1. Requisitos

| Programa | Para qué |
|---|---|
| **Python 3.11 o superior** | Ejecutar el backend (Flask). |
| **XAMPP (MySQL/MariaDB) o MySQL 8** | Almacenar la base de datos `codigocamp`. |
| **MySQL Workbench** *(opcional)* | Visualizar las tablas y generar el diagrama entidad-relación. |
| **Navegador moderno** | Chrome, Edge, Firefox o Safari. |
| **Clave de API de Gemini** *(opcional)* | Habilitar el tutor y el asistente de código ([Google AI Studio](https://aistudio.google.com/apikey)). |

---

## 2. Instalación paso a paso en local (Windows + XAMPP)



### 2.1 Crear la base de datos

1. Abre el panel de control de **XAMPP** y pulsa **Start** en **MySQL**.
2. En **MySQL Workbench**, conéctate a `127.0.0.1` en el puerto `3306` con el usuario `root`.
3. Abre `base de datos/codigocamp.sql` con **File → Open SQL Script** y pulsa el rayo ⚡ (**Execute**).

*(El script crea la base `codigocamp`, todas sus tablas y los 23 cursos. Ejecútalo solo en una instalación nueva; al arrancar Flask posteriormente, actualiza columnas nuevas sin borrar datos).*

### 2.2 Preparar el backend

En una terminal (PowerShell o CMD), dentro de la carpeta del proyecto:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

*(En macOS o Linux, el entorno virtual se activa con `source venv/bin/activate`).*

### 2.3 Configurar `backend/.env`

Crea el archivo `backend/.env` con la configuración local mínima (el resto de opciones está en la [sección 3](#3-configuración-de-variables-backendenv)):

```env
# Base de datos: XAMPP (usuario root sin contraseña)
DATABASE_URL="mysql+pymysql://root:@127.0.0.1:3306/codigocamp?charset=utf8mb4"


# --- IA de CódigoCamp: tutor, página IA y asistente de Trabajo (opcional) ---
GEMINI_API_KEY="<TU_API_KEY_DE_GEMINI>"
GEMINI_MODEL="gemini-3.5-flash-lite"

# --- Correo electrónico con Gmail (opcional, requiere contraseña de aplicación) ---
SMTP_PORT="587"
SMTP_USERNAME="finanbot.sena@gmail.com"
SMTP_APP_PASSWORD="<contraseña_de_aplicación_de_Gmail>"
SMTP_FROM="finanbot.sena@gmail.com"


# --- Iniciar sesión con Google (opcional) ---
GOOGLE_CLIENT_ID="<TU_GOOGLE_CLIENT_ID>.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="<TU_GOOGLE_CLIENT_SECRET>"
GOOGLE_REDIRECT_URI="http://localhost:5000/auth/google/callback/"

# --- Iniciar sesión con GitHub para git push en Trabajo (opcional; sección 6.1) ---
GITHUB_CLIENT_ID="<TU_GITHUB_CLIENT_ID>"
GITHUB_CLIENT_SECRET="<TU_GITHUB_CLIENT_SECRET>"
GITHUB_REDIRECT_URI="http://localhost:5000/auth/github/callback/"

# Direcciones del proyecto: localhost y el túnel, separadas por coma.
# CódigoCamp usa la misma por la que entró cada persona (la primera, en los avisos automáticos).
APP_URL="http://localhost:5000,https://codigocamp.taila41f89.ts.net"
GOOGLE_REDIRECT_URI="http://localhost:5000/auth/google/callback/,https://codigocamp.taila41f89.ts.net/auth/google/callback/"
```

#### Direcciones que hay que registrar en Google Cloud (local)

En <https://console.cloud.google.com/apis/credentials> → tu **ID de cliente de OAuth**:

| Campo | Dirección local |
|---|---|
| **Orígenes autorizados de JavaScript** | `http://localhost:5000` |
| **URI de redireccionamiento autorizados** | `http://localhost:5000/auth/google/callback/` |

#### Dirección que hay que registrar en GitHub (local)

En <https://github.com/settings/developers> → **OAuth Apps** → tu app (ver [sección 6.1](#61-iniciar-sesión-con-github-git-push)):

| Campo | Dirección local |
|---|---|
| **Homepage URL** | `http://localhost:5000` |
| **Authorization callback URL** | `http://localhost:5000/auth/github/callback/` |
| **Enable Device Flow** | ✅ marcado |

> 🔐 **Seguridad:** Escribe las URIs de callback exactamente con la barra `/` al final. Nunca subas el archivo `.env` ni tus claves reales a GitHub.

### 2.4 Cargar las lecciones y los retos

```powershell
flask --app app check-retos
flask --app app seed-retos
```

- `check-retos`: Revisa que todo el contenido de los cursos esté bien estructurado.
- `seed-retos`: Carga en la base las etapas, secciones, lecciones y preguntas de los 23 cursos (tarda alrededor de 1 minuto).

### 2.5 Arrancar en local

```powershell
flask --app app run
```

Abre **<http://localhost:5000/>** en tu navegador, crea tu cuenta y elige un curso.

> Entra siempre por **`http://localhost:5000`** (no `127.0.0.1`), ya que los proveedores OAuth (Google/GitHub) validan la dirección exacta de la sesión.

Para arrancarlo otro día:
1. Enciende **MySQL** en XAMPP.
2. Ejecuta dentro de `backend`: `venv\Scripts\activate` y luego `flask --app app run`.

### 2.6 Actualizar a una versión nueva en local

1. **Copia de seguridad** de `backend/.env` y de la carpeta `backend/almacen_archivos` (ahí se guardan los proyectos de Trabajo de todas las cuentas, **no** están en MySQL).
2. Trae los cambios (`git pull` o descomprime el ZIP nuevo sin sobrescribir `.env` ni `almacen_archivos`).
3. Dentro de `backend`, ejecuta `pip install -r requirements.txt` y `flask --app app sync-retos`.

```powershell
# Copia de seguridad rápida antes de actualizar (desde la carpeta Codigocamp)
Copy-Item backend\.env $HOME\codigocamp.env
Compress-Archive backend\almacen_archivos $HOME\almacen_archivos-respaldo.zip -Force
```

---

## 3. Configuración de variables (`backend/.env`)

| Variable | Valor por defecto | Para qué sirve |
|---|---|---|
| `DEBUG` | `1` | `1` en desarrollo local (HTTP) y `0` en producción (exige HTTPS). |
| `SECRET_KEY` | — | Clave secreta para firmar sesiones. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | `127.0.0.1`, `3306`, `codigocamp`, `root`, vacía | Credenciales individuales de MySQL/MariaDB. |
| `DATABASE_URL` | — | Cadena completa SQLAlchemy (`mysql+pymysql://root:@127.0.0.1:3306/codigocamp?charset=utf8mb4`). |
| `GEMINI_API_KEY` | — | Clave de Google AI Studio para el tutor IA y el editor Trabajo. |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Modelo de Gemini a utilizar. |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | — | Credenciales OAuth 2.0 de Google Cloud para «Continuar con Google». |
| `GOOGLE_REDIRECT_URI` | automático | Callback local (`http://localhost:5000/auth/google/callback/`). |
| `GITHUB_CLIENT_ID` | — | Activa «Iniciar sesión con GitHub» en Trabajo (`git push`, `pull`, `clone`). |
| `GITHUB_CLIENT_SECRET` | — | Opcional: habilita ventana emergente rápida de GitHub (sin secreto usa flujo por código de dispositivo). |
| `GITHUB_REDIRECT_URI` | automático | Callback local (`http://localhost:5000/auth/github/callback/`). |
| `SMTP_USERNAME`, `SMTP_APP_PASSWORD`, `SMTP_FROM` | — | Cuenta Gmail y contraseña de aplicación para envío de correos. |
| `SMTP_PORT`, `SMTP_SERVER` | `587`, automático | Configuración SMTP (`587` TLS o `465` con `SMTP_SSL=1`). |
| `APP_URL` | `http://localhost:5000` | Dirección base usada en los enlaces de correos (recuperar contraseña, avisos de racha). |
| `RECORDATORIOS_AUTO` | `1` | Envía avisos automáticos de racha a las 18:00 y 21:00 (`0` los desactiva). |
| `ALMACEN_ARCHIVOS` | `backend/almacen_archivos` | Carpeta local de fotos de perfil, adjuntos y proyectos de Trabajo. |
| `CUOTA_ARCHIVOS_GB`, `MAX_ARCHIVO_MB` | `10`, `1024` | Cuota máxima por cuenta y tamaño límite por archivo subido. |
| `BD_EXTERNAS` | igual a `DEBUG` | En local (`1`) permite que tus apps en **Trabajo** se conecten a tu MySQL de XAMPP. |
| `BD_HOSTS` | `localhost,127.0.0.1,::1` | Hosts de base de datos permitidos desde Trabajo. |
| `BD_PERMITIR_PROPIA` | `0` | `1` permite abrir la propia base `codigocamp` desde Trabajo (bloqueado por defecto). |
| `TRABAJO_RED` | `1` | Permite que el Python de Trabajo realice peticiones HTTP externas. |
| `PISTON_URL`, `PISTON_KEY` | — | Servidor externo opcional para ejecutar lenguajes compilados (Java, C, C++, Go, Rust). |

*(Si no configuras credenciales SMTP, los correos no fallan: se guardan como archivos `.eml` dentro de `backend/almacen_archivos/correos/` para revisarlos en local).*

---

## 4. Comandos útiles

Ejecútalos dentro de `backend` con el entorno virtual activado (`venv\Scripts\activate`):

| Comando | Qué hace |
|---|---|
| `flask --app app run` | Arranca la plataforma en <http://localhost:5000/>. |
| `flask --app app check-retos` | Revisa la sintaxis y estructura de todos los cursos. |
| `flask --app app seed-retos` | Carga el catálogo inicial de cursos en una base vacía. |
| `flask --app app sync-retos` | Agrega cursos o lecciones nuevas sin perder el progreso existente. |
| `flask --app app seed-retos --reset` | ⚠️ Borra el catálogo y el progreso de niveles, y vuelve a cargar desde cero. |
| `flask --app app migrar-camino` | Adapta el progreso de los usuarios tras cambiar etapas de un curso. |
| `flask --app app reparar-workbench` | Ajusta restricciones para generar el diagrama en MySQL Workbench. |
| `flask --app app recordar-rachas [--nivel 2]` | Envía manualmente los avisos de racha. |
| `flask --app app probar-correo tu@correo.com` | Verifica el envío de correo SMTP. |
| `flask --app app probar-ia` | Verifica la conexión con la API de Gemini. |
| `flask --app app limpiar-archivos` | Limpia del disco archivos huérfanos que ya no se usan. |
| `python herramientas/generar_aprende.py <curso>` | Regenera las lecciones teóricas de un curso desde `retos/conceptos/`. |
| `python herramientas/puente_bd.py` | Puente local para conectar una instancia remota con tu MySQL local. |

---

## 5. Qué incluye la plataforma

### Términos y condiciones
- El onboarding incluye la aceptación obligatoria de **Términos y condiciones** (`frontend/pages/terminos.html`), informando sobre copias de respaldo en Trabajo, uso de IA y reglas de convivencia.
- Si actualizas `data-version="…"` en `terminos.html`, todos los usuarios deberán aceptar la nueva versión al iniciar sesión (se registra en la tabla `terminos_aceptados`).

### 23 Cursos (Aprende e Inicio)
- **Web:** HTML, CSS, JavaScript y TypeScript.
- **Lenguajes:** Python, Java, C#, Kotlin, Swift, PHP, Ruby, Go, Rust, C (9 etapas) y C++ (9 etapas).
- **Datos:** Bases de datos, SQL y NoSQL (MongoDB, Redis, Firestore, Cassandra, Neo4j, DynamoDB, Elasticsearch).
- **Herramientas:** Terminales (Bash, PowerShell, CMD, cron, WSL, SSH), Git, GitHub, Docker y Node.js.

### Cuenta, gamificación e IA
- **Seguridad:** Inicio de sesión con correo o Google, recuperación de clave con tokens de 30 minutos y cierre remoto de sesiones activas en **Configuración → Seguridad**.
- **Motivación:** Rachas diarias, escudos salvarrachas (máx. 2), encargos diarios, cofres de sección y de logro, tienda de cosméticos (temas, marcos, punteros, fondos animados) y perfil personalizable.
- **Social e IA:** Chat entre amigos con envío de archivos (hasta 1 GB) y tutor virtual con Gemini con historial persistente.

---

## 6. Trabajo: el editor tipo VS Code

**Trabajo** es un entorno de desarrollo integrado directamente en el navegador:

| Función | Descripción |
|---|---|
| **Editor Monaco** | Mismo motor de VS Code con múltiples pestañas, búsqueda global (`Ctrl+Shift+F`) y paleta de comandos (`Ctrl+Shift+P`). |
| **Terminal y Git** | Terminal Bash simulada (`ls`, `cd`, `cat`, `python`, `npm`, `pip`, `git`), clonación, ramas, commits, merges y `git push` directo a GitHub. |
| **Entornos y servidores** | Soporte para entornos virtuales (`.venv`), vistas previas de FastAPI/Flask/Django y aplicaciones React + Vite. |
| **Bases de datos** | En local (`DEBUG=1`) se conecta directamente a tu MySQL de XAMPP; si MySQL está apagado, crea automáticamente una base SQLite funcional en `.codigocamp/bd/`. |
| **Asistente IA** | Propone cambios sobre tus archivos de código con vista previa para aceptar o rechazar cada modificación. |

### 6.1 Iniciar sesión con GitHub (`git push`)

1. Ve a **GitHub → Settings → Developer settings → OAuth Apps → New OAuth App**.
   - **Homepage URL:** `http://localhost:5000`
   - **Authorization callback URL:** `http://localhost:5000/auth/github/callback/`
   - Marca la casilla **Enable Device Flow** y guarda.
2. Copia el **Client ID** y genera un **Client secret**.
3. Añádelos en tu `backend/.env` (`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_REDIRECT_URI="http://localhost:5000/auth/github/callback/"`) y reinicia Flask.

---

## 7. Ver el diagrama de la base en MySQL Workbench

1. Abre MySQL Workbench y ve a **Database → Reverse Engineer…** (`Ctrl+R`).
2. Selecciona tu conexión local (`127.0.0.1:3306`), marca el esquema `codigocamp` y avanza hasta **Finish**.
3. Si Workbench se cierra al procesar el esquema de MariaDB, ejecuta `flask --app app reparar-workbench` e inténtalo de nuevo.

---

## 8. Instalar como app y widgets

- **Escritorio (Windows / macOS / Linux):** Abre `http://localhost:5000` en Chrome o Edge y haz clic en el ícono de instalar (`⊕`) en la barra de direcciones.
- **Widgets en Windows 11:** Tras instalar la app con Edge, presiona **Windows + W → `+` → CódigoCamp** para añadir los widgets de racha y meta diaria.
- **Widget flotante / iOS / Android:** Disponible desde **Configuración → App y widgets** usando la misma sesión activa.

---

## 9. Estructura del proyecto

```text
Codigocamp/
├── base de datos/
│   └── codigocamp.sql          # Esquema inicial para MySQL / XAMPP
├── backend/
│   ├── app.py                  # Creación de la app Flask
│   ├── models.py               # Modelos SQLAlchemy
│   ├── comandos.py             # Comandos CLI (seed-retos, sync-retos…)
│   ├── seguridad.py            # Sesiones, CSRF y cabeceras
│   ├── rutas/                  # Endpoints REST (auth, retos, tutor, chat…)
│   ├── servicios/              # Lógica de correo, perfil, tienda, bases externas…
│   ├── retos/                  # Definición de cursos y conceptos
│   ├── herramientas/           # generar_aprende.py y puente_bd.py
│   └── tests/                  # Pruebas unitarias del backend
└── frontend/
    ├── pages/                  # Páginas HTML
    ├── js/                     # Lógica cliente y editor Trabajo
    ├── css/, img/, widgets/    # Estilos, imágenes y widgets
    ├── vendor/                 # Pyodide, Git y SQLite offline
    ├── manifest.webmanifest    # Manifiesto PWA
    └── tests/                  # Pruebas del frontend
```

### Agregar o editar contenido de un curso

```powershell
flask --app app check-retos
python herramientas/generar_aprende.py <curso>
flask --app app sync-retos
```

---

## 10. Pruebas

```powershell
# Backend (desde backend/)
python -m unittest discover -s tests

# Frontend (desde frontend/)
node --test tests/*.test.mjs
```

---

## 11. Solución de problemas

| Problema | Solución |
|---|---|
| `Can't connect to MySQL server` | Enciende **MySQL** en XAMPP y revisa `DATABASE_URL` o `DB_HOST`/`DB_PORT` en `backend/.env`. |
| `Unknown database 'codigocamp'` | Importa `base de datos/codigocamp.sql` en MySQL Workbench. |
| Inicio no muestra lecciones | Ejecuta `flask --app app seed-retos` (o `sync-retos` si la base ya tenía datos). |
| «El tutor todavía no está configurado» | Agrega `GEMINI_API_KEY` en `backend/.env` y reinicia Flask. |
| Error 400 (`redirect_uri_mismatch`) en Google | Verifica que `GOOGLE_REDIRECT_URI` en `.env` y Google Cloud tengan `http://localhost:5000/auth/google/callback/` con la barra `/` al final. |
| No llegan los correos | Ejecuta `flask --app app probar-correo tu@correo.com` y verifica que uses una contraseña de aplicación de Gmail. |
| Workbench se cierra con el diagrama | Ejecuta `flask --app app reparar-workbench`. |
