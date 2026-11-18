# CódigoCamp

Plataforma en español para aprender programación con una ruta de retos, lecciones, práctica diaria, amistades, tutor y tienda de recompensas.

## Estructura

- `frontend/`: páginas, estilos, imágenes y lecciones estáticas.
- `backend/app.py`: aplicación Flask, API JSON y servicio de archivos del frontend.
- `backend/models.py`: modelos y relaciones SQLAlchemy.
- `backend/retos/<lenguaje>.py` (`html.py`, `css.py`, `javascript.py`, `python.py`…): los retos de cada lenguaje, organizados en etapas → secciones → lecciones → preguntas. `base.py` tiene los helpers para escribirlos.
- `backend/retos/__init__.py`: revisa (`flask --app app check-retos`) y carga (`seed-retos`) el catálogo en MySQL.
- `base de datos/`: script SQL para crear el esquema y el catálogo base desde Workbench.

El backend activo es Flask. `backend/db.sqlite3` se conserva sin cambios como respaldo; la aplicación usa MySQL.

## Base de datos en XAMPP + MySQL Workbench

1. Inicia **MySQL** en el panel de XAMPP y conéctate desde Workbench a `127.0.0.1`.
2. Para una instalación nueva, abre `base de datos/codigocamp.sql` en Workbench y pulsa **Execute**. **No lo ejecutes sobre una base existente: elimina esa base.**
3. Si ya tienes la base y quieres conservar sus datos, ejecuta una sola vez `base de datos/migracion_trabajo_google.sql`.
   Para los archivos del espacio de Trabajo (imágenes, videos, PDF…) ejecuta también, una sola vez, `base de datos/migracion_archivos.sql`. Los bytes no van en MySQL sino en `backend/almacen_archivos/` (cópiala junto con la base cuando hagas respaldos).
4. Configura `backend/.env`, activa el entorno virtual y ejecuta `flask --app app seed-retos` desde `backend`.
5. **Si tu base ya tenía el camino anterior** (4 lecciones por sección y preguntas repetidas), ejecuta una vez `flask --app app migrar-camino` desde `backend`: recrea el camino nuevo y traslada lo que cada estudiante había completado. `sync-retos` no sirve para este cambio porque quita lecciones.

El SQL crea la base `codigocamp`, sus tablas y los 17 cursos. El catálogo de retos (etapas, secciones, lecciones y preguntas) se carga con `flask --app app seed-retos`. Tras editar o ampliar contenido, usa `flask --app app sync-retos`: actualiza y agrega niveles compatibles conservando los IDs y el progreso existentes. Si el cambio reordena o elimina niveles, la sincronización se detiene para proteger el avance. **Atención:** `seed-retos --reset` borra el catálogo y el progreso de niveles guardado en esa base; úsalo solo tras hacer una copia de seguridad.

## Arrancar Flask en Windows

Instala los requisitos en `backend`, configura `backend/.env` con las credenciales de MySQL y una `SECRET_KEY` segura, y arranca Flask:
```.env
SECRET_KEY="codigocamp_super_secret_key_2026_production_ready"
JWT_SECRET_KEY="codigocamp_jwt_token_secret_generation_2026"

# URL activa para XAMPP (sin contraseña)
DATABASE_URL="mysql+pymysql://root:@127.0.0.1:3306/codigocamp?charset=utf8mb4"

# Codigocamp IA 
GEMINI_API_KEY="PEGA_AQUI_TU_CLAVE"

SMTP_PORT="587"
SMTP_USERNAME="finanbot.sena@gmail.com"
SMTP_APP_PASSWORD="contraseña de aplicacion(se ve en la cuenta finanbot)"
SMTP_FROM="finanbot.sena@gmail.com"

GOOGLE_CLIENT_ID="315416890012-2odq73aekf5ha1plh684a8adcr3u6ct3.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
GOOGLE_REDIRECT_URI="http://localhost:5000/auth/google/callback/"

```
```powershell
cd backend
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
flask --app app check-retos
flask --app app seed-retos
flask --app app sync-retos

flask --app app run
```

Abre <http://127.0.0.1:5000/>. Las credenciales de MySQL solo van en `backend/.env`; no las guardes en el repositorio.

## Progreso, retos y monedas

- Los retos se desbloquean en orden. Cada respuesta incorrecta resta una vida y las vidas se regeneran cada 30 minutos hasta cinco.
- XP es experiencia: aumenta el nivel del alumno y **no se usa para comprar**.
- Cada cinco niveles nuevos se entrega un diamante. Los seis desafíos diarios y el desafío mensual también entregan diamantes.
- Los diamantes son la moneda de la tienda; el XP solo sirve para progresar de nivel.
- Tema visual: en **Configuración** puedes elegir *Predeterminado* (sigue el modo claro/oscuro de tu dispositivo), *Claro* u *Oscuro*. Se guarda en `perfiles.tema`.
- El esquema de base de datos está en `base de datos/codigocamp.sql`.

## Arquitectura y edición del contenido

- **Presentación:** `frontend/pages/` contiene las páginas HTML; `frontend/css/` sus estilos; `frontend/js/` la interfaz, las llamadas a la API y los editores. Los ejemplos de Aprende viven en `frontend/js/lecciones/`; `frontend/js/iconos.js` reúne iconos SVG originales para navegación, estadísticas, tienda, misiones y Trabajo.
- **Aplicación y datos:** `backend/app.py` ensambla Flask; `backend/rutas/` contiene endpoints por función; `backend/servicios/` concentra las reglas de negocio; `backend/seguridad.py` configura sesión y protección CSRF; `backend/constantes.py` define monedas, misiones y artículos; `backend/models.py` define las entidades y relaciones SQLAlchemy. `backend/retos/` es el catálogo editable de retos: un archivo por curso, con etapas → secciones → lecciones → preguntas. `backend/retos/base.py` documenta los constructores `O`, `C`, `E`, `ORD` y `reto`.
- **Lecciones generadas:** los cursos se escriben por conceptos en `backend/retos/conceptos/` y se generan a `frontend/js/lecciones/`. La estructura objetivo es 20 conceptos por etapa (100 por curso, 400 niveles de Retos); JavaScript conserva un concepto adicional (101 conceptos, 404 niveles). Desde `backend`, ejecuta `python herramientas/generar_aprende.py` para regenerarlos todos o añade slugs para regenerar solo algunos. No edites a mano un archivo marcado como generado.
- **Lecciones editables al aprender:** el editor permite cambiar cada ejemplo; las modificaciones se guardan automáticamente en el navegador por curso y lección. **Restablecer** recupera el ejemplo original.
- **Trabajo** (`frontend/pages/trabajo.html`, lógica en `frontend/js/trabajo.js` y `frontend/js/trabajo/`): espacio con aspecto y atajos de VS Code (Dark+/Light+ según el tema): explorador con crear/renombrar/eliminar/arrastrar y «Deshacer», pestañas, editor con resaltado de sintaxis, auto-indentado y cierre de pares, vista previa aislada con pestaña CONSOLA, panel de terminal con varias instancias, barra de estado y tutor contextual. **Guardado:** cada cambio se guarda al instante en el navegador y se sube a la cuenta; al abrir nunca gana «la nube» a ciegas (si hay cambios locales pendientes se conservan y se suben; si ambas versiones cambiaron por separado se pregunta). Borrar archivos los borra de verdad (también en la cuenta) y un proyecto vacío sigue vacío. La terminal es una shell real sobre los archivos del proyecto (comillas, variables, comodines, pipes, `&&`/`;`/`||`, redirecciones, historial, Tab, Ctrl+C) con `node`, `ts-node`, `python` (Pyodide) y `sqlite3` en el navegador; Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin y Ruby usan el ejecutor del servidor (`POST /api/run`). **`pip`** usa micropip dentro de Pyodide (paquetes de Python puro y los que trae Pyodide: numpy, pandas…); lo instalado se recuerda en el navegador. **`npm`** mantiene el `package.json` (init, install, uninstall, run, start, test, ls); los paquetes se cargan desde el CDN esm.sh al hacer `import`, no hay `node_modules`. **`git push` es real**: publica el último commit en GitHub con la API REST usando un token personal que cada persona escribe (entrada oculta, solo en memoria de la pestaña, nunca se guarda ni pasa por el servidor); añade/actualiza archivos sin borrar los que ya existan en GitHub. Guardado automático desactivable (botón «Autoguardado» en la barra de estado): sin él, los cambios de texto quedan «sin guardar» hasta Ctrl+S, y ejecutar guarda antes. No hay sistema operativo: `sudo`, `curl`, `ssh`, etc. no existen. El tutor requiere `GEMINI_API_KEY`.
- **Acceso Google**: crea un cliente OAuth de tipo *Aplicación web* en Google Cloud Console, registra el callback indicado arriba y coloca `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` en `backend/.env`. Reinicia Flask. Si no se configuran, el inicio de sesión normal sigue disponible.
- **Validación y carga de retos:** desde `backend`, ejecuta `flask --app app check-retos` antes de cargar el catálogo. Usa `flask --app app seed-retos` para la primera carga y `flask --app app sync-retos` para actualizar o agregar contenido compatible sin borrar el avance. `seed-retos --reset` es destructivo y solo se necesita para reestructuraciones incompatibles.

## Mejoras de interfaz y juego

- La tienda usa iconos SVG propios, tarjetas con realce visual y una animación de compra sin emojis.
- Recompensas muestra seis encargos diarios; cada uno acredita diamantes automáticamente y suma al desafío mensual.
- Los iconos de navegación, estadísticas, tienda y misiones son SVG originales, sin depender de imágenes externas.
- Las respuestas de los retos producen una animación de acierto/error y tonos breves generados localmente con Web Audio (estilo conexión/desconexión USB). El interruptor de sonido está en **Configuración** y guarda la preferencia en este navegador; no se descargan efectos de sonido.
- El reto toma el color de su curso y respeta la preferencia de movimiento reducido del sistema.

El catálogo tiene 17 cursos y `check-retos` valida opciones, explicaciones, variedad de tipos y que no se repitan las respuestas correctas dentro de una lección. Aprende carga dinámicamente los cursos activos desde la API; Go, Kotlin, PHP, Ruby, Rust y Swift ahora tienen 100 lecciones de Aprende y 400 niveles de Retos cada uno.

## Configuración opcional

- `GEMINI_API_KEY`: activa el tutor de IA.
- `GEMINI_MODEL`: cambia el modelo, por defecto `gemini-2.5-flash`.
- `DATABASE_URL`: permite reemplazar las variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y, opcionalmente, `GOOGLE_REDIRECT_URI`: habilitan el inicio de sesión con Google. No guardes estas credenciales en Git.

En **Trabajo**, los archivos web (HTML/CSS y los .js que usa una página) se ejecutan en la vista previa y el resto de lenguajes desde la terminal (botón Ejecutar o Ctrl+Enter; mientras corre un programa el botón pasa a «Detener»). Python, TypeScript y SQL descargan su motor (Pyodide, TypeScript, sql.js) desde un CDN la primera vez que se usan, igual que Aprende. Las pruebas del módulo: `node --test frontend/tests/*.test.mjs` (lógica del IDE, sin dependencias) y `python -m unittest tests.test_trabajo` desde `backend/`.

- **Aprende** (`frontend/js/lecciones/<lenguaje>.js`): cada lección tiene explicación, puntos clave, código que se ejecuta, y opcionalmente `r` (“Ahora tú”) y `e` (“Error común”).
- **Repaso**: ningún curso lleva lecciones «Repaso de …» ni nodos «Práctica de repaso» (`CON_REPASO` vacío en `backend/retos/__init__.py`; `construir_etapas(..., repaso=False)` por defecto). Tras cambiarlo ejecuta `flask --app app seed-retos --reset`.
- **Cursos con conceptos (5 etapas × 20 conceptos)**: los 17 lenguajes y temas del catálogo. `generar_aprende.py` crea Aprende desde esos mismos conceptos y guarda las salidas deterministas en `salidas.js`; para C y C++ compila y ejecuta cada ejemplo (si uno no compila, se detiene).


## Trabajo: archivos, ZIP, carpeta del computador y git clone

| Función | Navegadores | Notas |
|---|---|---|
| Subir archivos (botón ⋯ o soltar sobre la lista de archivos) | Todos | Cualquier tipo. **1 GB por archivo y 10 GB por cuenta** (configurable en `backend/.env`). Se suben en streaming y con progreso. |
| Subir una carpeta (una sola vez) | Todos los de computador | No sincroniza. Ignora `.git`, `node_modules`, `__pycache__`… |
| Importar / descargar `.zip` | Chrome/Edge 80+, Firefox 113+, Safari 16.4+ | Hasta 1 GB (el .zip se arma en la memoria del navegador). Lo que no cabe se descarga con clic derecho → Descargar. |
| Abrir carpeta del computador (sincroniza en los dos sentidos) | Solo Chrome, Edge y Opera de computador | Pide permiso en cada visita; la carpeta queda en ese computador. En conflicto gana el computador y la otra versión queda como `nombre.conflicto.ext`. |
| `git clone <url> [carpeta]` / `git clone <url> .` | Todos | Solo GitHub por HTTPS. Trae **todos** los archivos de la última versión (no el historial), reintenta descargas que fallen y completa la lista en repos enormes. Con `.` en un proyecto vacío activa Git con los últimos 20 commits y el remoto. |
| React, Vite y librerías | Todos | `npm create vite@latest mi-app -- --template react` (también `react-ts`, `vanilla`, `vanilla-ts`, `preact`), `cd mi-app`, `npm run dev`. JSX/TSX se transpilan en el navegador y `import` de paquetes usa la versión de `package.json` desde esm.sh (una sola copia de React). `npm install bootstrap` y `import "bootstrap/dist/css/bootstrap.min.css"` o `<link href="node_modules/...">` también funcionan. |

- **Texto editable vs. archivos:** el código y los textos de hasta 1 MB por archivo se editan; entre todos admiten 5 millones de caracteres. El proyecto se guarda comprimido en `ALMACEN_ARCHIVOS/<usuario>/proyecto.json` (no en MySQL) y su copia local en IndexedDB. Si un texto ya no cabe, se guarda completo como archivo de la cuenta (se ve y se descarga). Lo demás —imágenes, videos, audio, PDF, fuentes— se guarda en la cuenta. Un proyecto admite 5000 archivos, 2000 carpetas, nombres de 120 caracteres y rutas de 400.
- **Cómo se guarda:** en el proyecto queda un «marcador» (`ccbin:v1:<sha256>:<tipo>:<bytes>`) y los bytes van a `ALMACEN_ARCHIVOS/<usuario>/<hash>`, con su lista en la tabla `archivos_trabajo`. Mover, copiar, deshacer y Git funcionan igual que con cualquier archivo, y `git push` publica el archivo real (GitHub no acepta más de 100 MB por archivo: esos se avisan y no se envían).
- **Seguridad:** solo imágenes, video, audio, PDF, fuentes y texto plano se muestran en el navegador; HTML, SVG, ejecutables y el resto se sirven como descarga. La vista previa usa enlaces firmados que caducan a las 6 horas.
- **Limpieza:** lo que el proyecto ya no usa se borra solo una hora después de guardar. `flask --app app limpiar-archivos` quita del disco lo que quedó de cuentas eliminadas o subidas interrumpidas.
- **Capacidad del servidor:** 10 GB por cuenta es el tope, no lo que se reserva; aun así, con muchas cuentas llenas el disco se acaba. El servidor rechaza subidas si quedaría menos de 1 GB libre.

## Retos sin preguntas repetidas

Cada concepto de `backend/retos/conceptos/` aporta 9 a 12 datos distintos (definición, uso, 3 ideas clave, situación, código, completar, error común…). El generador (`backend/retos/generador.py`) pregunta cada dato **una sola vez en todo el curso** y descarta cualquier pregunta cuyo dato o respuesta ya apareció, aunque esté con otras palabras. Con eso arma 2 o 3 lecciones por concepto, y las etapas se parten en partes de **45 lecciones como máximo**. `flask --app app check-retos` rechaza un catálogo que repita una pregunta.
