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
2. Abre `base de datos/crear_base.sql` en Workbench y pulsa **Execute**.
3. Configura `backend/.env`, activa el entorno virtual y ejecuta `flask --app app seed-retos` desde `backend`.

El SQL crea la base `codigocamp`, las 17 tablas, sus relaciones, los 17 cursos y los artículos de la tienda. El catálogo de retos (etapas, secciones, lecciones y preguntas) se carga con `flask --app app seed-retos`; tras editar los archivos de `backend/camp/datos/` usa `seed-retos --reset`.

## Arrancar Flask en Windows

Instala los requisitos en `backend`, configura `backend/.env` con las credenciales de MySQL y una `SECRET_KEY` segura, y arranca Flask:
```.env
DEBUG=1
SECRET_KEY=replace-with-a-long-random-secret

# MySQL de XAMPP (WorkBench administra el mismo servidor; no instala otro).
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=codigocamp
DB_USER=root
DB_PASSWORD=

# Opcional: usar una URI completa en vez de las variables anteriores.
# DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/codigocamp?charset=utf8mb4

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

```
```powershell
cd backend
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
flask --app app check-retos
flask --app app seed-retos

flask --app app run
```

Abre <http://127.0.0.1:5000/>. Las credenciales de MySQL solo van en `backend/.env`; no las guardes en el repositorio.

## Progreso, retos y monedas

- Los retos se desbloquean en orden. Cada respuesta incorrecta resta una vida y las vidas se regeneran cada 30 minutos hasta cinco.
- XP es experiencia: aumenta el nivel del alumno y **no se usa para comprar**.
- Cada nivel nuevo entrega 10 cobres; cada cinco niveles completados se entrega un hierro.
- Los desafíos diarios entregan cobre o hierro. Completar 60 puntos del desafío mensual entrega dos diamantes.
- Cobre compra objetos básicos, hierro objetos intermedios y diamante el paquete premium. La tienda solo permite comprar con esos minerales.
- Tema visual: en **Configuración** puedes elegir *Predeterminado* (sigue el modo claro/oscuro de tu dispositivo), *Claro* u *Oscuro*. Se guarda en `perfiles.tema`.
- Para el detalle de instalación, consulta `base de datos/README.md`.

## Configuración opcional

- `GEMINI_API_KEY`: activa el tutor de IA.
- `GEMINI_MODEL`: cambia el modelo, por defecto `gemini-2.5-flash`.
- `DATABASE_URL`: permite reemplazar las variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`.

El ejecutor de código no está habilitado en el servidor; los ejercicios que ya existen siguen usando el evaluador aislado del navegador.

- **Aprende** (`frontend/js/lecciones/<lenguaje>.js`): cada lección tiene explicación, puntos clave, código que se ejecuta, y opcionalmente `r` (“Ahora tú”) y `e` (“Error común”).
