"""Tutor de IA (Gemini): responde con el contexto del alumno, del archivo y del proyecto abiertos, acepta archivos
adjuntos (imágenes, video, audio, PDF, código… hasta 1 GB) y, en modo copiloto, propone cambios en los archivos
que el alumno revisa y acepta uno por uno en Trabajo.

backend/.env:  GEMINI_API_KEY=...   GEMINI_MODEL=gemini-3.8-flash
Los archivos de más de 8 MB (o de tipos que no van en línea) se suben a la API de archivos de Gemini, que los guarda 48 h.
"""
import base64
import io
import threading
from collections import deque
import json
import re
import secrets
import os
import time
import urllib.error
import urllib.request
from datetime import timedelta, timezone
from pathlib import PurePosixPath

from flask import Blueprint, current_app, jsonify
from flask_login import current_user, login_required

from models import Attachment, TutorUsage, db, utcnow
from rutas.archivos import _ruta
from rutas.adjuntos import tomar
from servicios.perfil import get_profile
from utilidades import api_error, client_ip, json_body, too_many

bp = Blueprint("tutor", __name__)
API = os.environ.get("GEMINI_API_URL", "https://generativelanguage.googleapis.com").rstrip("/")   # solo se cambia para pruebas
# Si el modelo de backend/.env no existe para tu clave (404), se prueban estos en orden.
# También se usan si el modelo está SATURADO (503 «high demand») o sin cuota (429): cada modelo va por separado.
MODELOS_RESPALDO = ("gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite",
                    "gemini-3.1-flash-lite", "gemini-2.5-flash")
_modelo_que_funciona = {}
# El autocompletado solo usa modelos «lite» (rápidos y con cuota aparte): nunca le quita cuota al chat.
RESPALDO_RAPIDO = ("gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite")


def normalizar_modelo(nombre):
    """«Gemini 3.8», «gemini-3.8», «models/gemini-3.8-flash» → «gemini-3.8-flash»."""
    n = str(nombre or "").strip().strip('"').strip("'").lower().removeprefix("models/")
    n = re.sub(r"\s+", "-", n)
    if re.fullmatch(r"(gemini-)?\d+(\.\d+)?", n):          # solo el número: se usa su versión Flash
        n = f"gemini-{n.removeprefix('gemini-')}-flash"
    if n and not n.startswith(("gemini", "gemma", "learnlm")):
        n = "gemini-" + n
    return n or MODELOS_RESPALDO[0]


# ---- Cuota de Gemini -------------------------------------------------------------------------------------
# La clave gratis de Gemini permite pocas peticiones por minuto POR MODELO. Antes el autocompletado de Trabajo
# (texto fantasma) gastaba esa cuota mientras escribías y el chat de la IA respondía «espera un minuto».
# Ahora: (1) si un modelo dice 429 se usa otro modelo (cada uno tiene su propia cuota) y ese se deja descansar;
# (2) el autocompletado usa un modelo «lite» aparte y se detiene solo cuando la cuota está apretada.
_descanso = {}                  # modelo -> momento (monotonic) hasta el que no se usa por 429
_llamadas = deque()             # momentos de las últimas llamadas a Gemini (todas)
_cuota_lock = threading.Lock()


def _anotar_llamada():
    ahora = time.monotonic()
    with _cuota_lock:
        _llamadas.append(ahora)
        while _llamadas and ahora - _llamadas[0] > 60:
            _llamadas.popleft()


def llamadas_ultimo_minuto():
    ahora = time.monotonic()
    with _cuota_lock:
        while _llamadas and ahora - _llamadas[0] > 60:
            _llamadas.popleft()
        return len(_llamadas)


def _espera_sugerida(cuerpo):
    """Gemini dice cuánto esperar («retryDelay»: "17s"); si no, 30 s."""
    m = re.search(r'"retryDelay"\s*:\s*"(\d+(?:\.\d+)?)s"', cuerpo or "")
    return min(120.0, float(m.group(1))) if m else 30.0


def en_descanso(modelo):
    return _descanso.get(normalizar_modelo(modelo), 0) > time.monotonic()


def generar(payload, api_key, modelo, timeout=180, respaldo=True, esperar_max=0):
    """Llama a generateContent. Si el modelo no existe (404) o se le acabó la cuota del minuto (429), prueba los de respaldo.
    esperar_max: segundos que vale la pena esperar si TODOS están sin cuota (el chat espera un poco; el autocompletado no)."""
    modelo = normalizar_modelo(modelo)
    extra = list(respaldo) if isinstance(respaldo, (list, tuple)) else (list(MODELOS_RESPALDO) if respaldo else [])
    candidatos = list(dict.fromkeys([_modelo_que_funciona.get(modelo, modelo)] + [normalizar_modelo(m) for m in extra if m]))
    for intento in range(2):
        ultimo, ultimo_429, espera = None, None, None
        ahora = time.monotonic()
        libres = [m for m in candidatos if _descanso.get(m, 0) <= ahora] or ([] if intento == 0 and esperar_max else candidatos[:1])
        solo_404 = libres[:1] == candidatos[:1]   # ¿se llegó a este modelo solo porque los anteriores no existen?
        for m in libres:
            try:
                _anotar_llamada()
                with _peticion(f"{API}/v1beta/models/{m}:generateContent", payload, {"Content-Type": "application/json", "x-goog-api-key": api_key}, "POST", timeout) as r:
                    datos = json.load(r)
                if solo_404:   # el modelo del .env no existe para esta clave: se recuerda el que sí funciona
                    if m != modelo and _modelo_que_funciona.get(modelo) != m:
                        current_app.logger.warning("El modelo «%s» no está disponible para tu clave; se usó «%s». Pon GEMINI_MODEL=%s en backend/.env.", modelo, m, m)
                    _modelo_que_funciona[modelo] = m
                return datos, m
            except urllib.error.HTTPError as e:
                if e.code == 400 and b"thinking" in payload:
                    cuerpo400 = e.read()[:1500].decode("utf-8", "replace")
                    if "thinking" in cuerpo400.lower():
                        p2 = json.loads(payload)
                        p2.get("generationConfig", {}).pop("thinkingConfig", None)
                        payload = json.dumps(p2).encode()
                        try:
                            _anotar_llamada()
                            with _peticion(f"{API}/v1beta/models/{m}:generateContent", payload, {"Content-Type": "application/json", "x-goog-api-key": api_key}, "POST", timeout) as r:
                                return json.load(r), m
                        except urllib.error.HTTPError as e2:
                            e = e2
                    else:
                        raise urllib.error.HTTPError(e.url, 400, e.msg, e.hdrs, io.BytesIO(cuerpo400.encode()))
                if e.code == 404:
                    ultimo = e
                    if m != modelo:   # un respaldo que no existe para esta clave: no se vuelve a probar en un rato
                        _descanso[m] = time.monotonic() + 3600
                    continue
                if e.code in (429, 500, 502, 503, 504):
                    # 429 = sin cuota; 5xx = Gemini saturado («This model is currently experiencing high demand»).
                    # En los dos casos ese modelo descansa un rato y se usa el siguiente.
                    solo_404 = False
                    cuerpo = e.read()[:2000].decode("utf-8", "replace")
                    current_app.logger.warning("Gemini «%s» respondió %s; se prueba otro modelo.", m, e.code)
                    pausa = _espera_sugerida(cuerpo) if e.code == 429 else 60.0
                    _descanso[m] = time.monotonic() + pausa
                    espera = pausa if espera is None else min(espera, pausa)
                    ultimo_429 = urllib.error.HTTPError(e.url, e.code, e.msg, e.hdrs, io.BytesIO(cuerpo.encode()))
                    continue
                raise
        # Todos sin cuota: si la espera es corta (y quien llama puede esperar), se espera y se reintenta una vez
        if intento == 0 and esperar_max:
            proximo = min((_descanso.get(m, 0) for m in candidatos), default=0) - time.monotonic()
            if 0 < proximo <= esperar_max:
                time.sleep(proximo + 0.3)
                continue
        if ultimo_429 is not None:
            raise ultimo_429
        if ultimo is not None:
            raise ultimo
        break
    raise urllib.error.HTTPError(f"{API}", 429, "Sin cuota", None, io.BytesIO(b"{}"))
EN_LINEA_MAX = 8 * 1024 * 1024
TEXTO_MAX = 300_000
CONTEXTO_MAX = 180_000

MIME_IA = {
    "image/png", "image/jpeg", "image/webp", "image/heic", "image/heif", "image/gif",
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/aiff", "audio/aac", "audio/ogg", "audio/flac", "audio/webm", "audio/mp4",
    "video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo", "video/x-flv", "video/webm", "video/x-ms-wmv", "video/3gpp",
    "application/pdf",
}
EXT_TEXTO = {
    "txt", "md", "markdown", "csv", "tsv", "json", "xml", "yml", "yaml", "toml", "ini", "cfg", "env", "log", "sql", "html", "htm", "css", "scss", "sass", "less",
    "js", "mjs", "cjs", "jsx", "ts", "tsx", "vue", "svelte", "py", "ipynb", "java", "kt", "kts", "c", "h", "cpp", "hpp", "cc", "cs", "go", "rs", "rb", "php", "swift",
    "dart", "lua", "r", "pl", "sh", "bash", "zsh", "ps1", "bat", "cmd", "dockerfile", "gitignore", "gradle", "properties", "svg",
}

SISTEMA = """Eres el tutor y copiloto de programación de CódigoCamp, una plataforma en español para aprender a programar.
Eres un experto senior en todo el desarrollo de software: lenguajes (HTML, CSS, JavaScript, TypeScript, Python, Java, C, C++, C#, PHP,
Go, Rust, Kotlin, Swift, Ruby, Dart, SQL…), frameworks (React, Vue, Angular, Svelte, Node, Express, Next.js, Flask, Django, FastAPI,
Spring, Laravel, .NET), bases de datos SQL y NoSQL (MySQL/MariaDB, PostgreSQL, SQLite, SQL Server, MongoDB, Redis, Firebase),
terminales (Bash, PowerShell, CMD, zsh), Git y GitHub, Docker, despliegue, seguridad, pruebas, estructuras de datos, algoritmos y buenas prácticas.

Cómo respondes:
- Siempre en español, claro y amable. Adapta la profundidad al nivel del alumno: más simple si empieza, más técnico si tiene experiencia.
- Ve al grano. Primero la respuesta o la causa del error; después el porqué, en pocas frases.
- Código en bloques ``` con el lenguaje. Código correcto, completo para lo que se pide y que funcione en CódigoCamp (Trabajo ejecuta en el navegador:
  JS/TS, Python con Pyodide, SQL con SQLite y las bases del alumno con mysql/psql/mongosh/redis-cli; React con Vite en la vista previa).
- Si hay un error, explica la causa concreta (línea, variable) y cómo arreglarlo.
- Si el error es porque falta instalar algo (ModuleNotFoundError, Cannot find module, «command not found» de un framework), di exactamente qué
  escribir en la terminal (pip install …, pip install -r requirements.txt, npm install …) o que lo instale desde Extensiones (Ctrl+Shift+X).
  Si usa un entorno virtual, recuérdale activarlo antes (source .venv/bin/activate o .venv\\Scripts\\activate).
- En Trabajo funcionan: python -m venv .venv, fastapi dev main.py, uvicorn main:app --reload, flask --app app run --debug
  (la vista previa abre http://127.0.0.1:8000/docs). uvicorn, gunicorn y uvloop no hace falta instalarlos: CódigoCamp hace de servidor.
- Si es un reto o ejercicio de clase, da primero una pista y ofrece la solución si la pide.
- Si te pasan archivos (imágenes, capturas, PDF, video, audio, código), analízalos y refiérete a ellos por su nombre.
- Si no sabes algo con seguridad, dilo. No inventes funciones ni librerías.
- Antes de responder, revisa mentalmente que el código compile y haga lo que se pidió (imports, nombres, tipos, casos vacíos).
  Si cambias un archivo, conserva lo que ya funcionaba y no borres código que no se pidió quitar.
- Si la pregunta es ambigua, elige la interpretación más probable según el código y el curso del alumno y dilo en una frase.
- Si te escribe en Trabajo conectado a su equipo, los comandos y rutas son los de SU sistema (Windows usa PowerShell; macOS y Linux, bash/zsh).
- Usa listas cortas con guiones; evita tablas grandes y títulos largos.
- Si la pregunta no tiene que ver con programación, tecnología o estudio, explica amablemente que eres el tutor de programación.
- Si preguntan cómo usar CódigoCamp (dónde está algo, cómo se hace, por qué no funciona), usa la guía de abajo y di la ruta exacta
  (por ejemplo «Trabajo → Terminal», «Tienda → Fondos», «Configuración → Apariencia»).

GUÍA DE CÓDIGOCAMP (todo lo que la plataforma puede hacer; úsala para ayudar al alumno a usarla):
- Inicio: la ruta del curso elegido (etapas → secciones → niveles de retos). Cada nivel da XP; cada 100 XP sube un nivel. Racha = días
  seguidos practicando (los salvarrachas la protegen un día). Salvarrachas: en la tienda y
  cofres del camino el tope es 2, pero cada 10 días seguidos de racha se gana +1 aunque pases de 2 (hasta 10). Tienda: además de fondos, punteros, temas, marcos,
  efectos y rastros, hay «Accesorios de Codi» (gorra, gafas pixel, audífonos, corona, sombrero de mago, capa, casco vikingo,
  birrete, casco de astronauta…) que la mascota lleva puestos en toda la página. Semana perfecta
  (lunes a domingo sin usar salvarrachas): cofre de oro con 250 diamantes, 100 XP y 1 salvarrachas. Mes perfecto (todo el mes sin
  perder la racha ni usar salvarrachas): cofre legendario con 2000 diamantes, 600 XP, 10 vidas y 3 salvarrachas. Vidas: se pierde una al fallar un reto y se recuperan con el tiempo.
  El curso se cambia arriba en «Mi curso».
- Recompensas: encargos de hoy (misiones diarias con diamantes), cofres de logro (se abren al cumplir metas) y el desafío del mes.
- Aprende: 25 cursos con lecciones (HTML, CSS, JavaScript, Python, SQL, Bases de datos, TypeScript, Java, C#, Kotlin, Swift, PHP, Ruby,
  Go, Rust, C, C++, Terminales, Git, Docker, Node.js, GitHub, NoSQL, React, React Native). React Native se ve en un celular simulado (react-native-web con Expo y
  React Navigation simulados); para el celular real se usa Expo Go con «expo start» en Trabajo. HTML tiene 220 temas (cada etiqueta,
  input, atributo, ARIA, metadatos y SEO). Cada lección trae teoría, código editable con el editor
  profesional (colores, autocompletado, Ctrl+Enter ejecuta) y un reto «Ahora tú». Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin y Ruby se
  ejecutan de verdad; si el programa lee del teclado aparece la caja «⌨️ Entrada del teclado» (un dato por línea).
- Trabajo (el editor profesional de CódigoCamp; nunca lo compares con otros editores ni nombres VS Code): explorador de archivos, pestañas, editor Monaco, búsqueda (Ctrl+Shift+F), paleta (Ctrl+Shift+P), panel de Git
  (commit, ramas, push/pull a GitHub con «Iniciar sesión con GitHub»), Extensiones (Ctrl+Shift+X, paquetes de pip y npm), vista previa
  en vivo como Live Server (al lado o en pestaña, tamaños de celular/tableta), copiloto de IA que propone cambios que el alumno acepta,
  y proyectos Vite con npm create vite@latest mi-app -- --template vanilla | vanilla-ts | react | react-ts | preact | vue | svelte.
  · Botón Ejecutar (Ctrl+Enter): HTML/CSS → vista previa; JS → node; TS → ts-node; Python; SQL; .jsx/.tsx → muestra el componente React
    en la vista previa (crea vista-Nombre.html si no hay página); Java, C, C++, C#, PHP, Go, Rust, Swift, Kotlin, Ruby → se compilan y
    ejecutan en el servidor (o en línea con Wandbox / Kotlin Playground y, de respaldo, Compiler Explorer); también Lua, Perl, R, Scala,
    Haskell, Elixir, Julia, Groovy, Crystal, Nim, OCaml, D, Pascal, Zig, Common Lisp y Bash (comandos lua, perl, Rscript, scala,
    runghc, elixir, julia, groovy, crystal run, nim r, ocaml, rdmd, fpc, zig run, sbcl); Dockerfile → docker build +
    docker run; compose.yaml → docker compose up -d.
  · Archivos nuevos de cualquiera de esos lenguajes, .sh, Dockerfile y compose.yaml vienen con un ejemplo que funciona.
  · Atajos: Ctrl+P ir a archivo, Ctrl+Shift+P comandos, Ctrl+, ajustes del editor (letra, tabulación, ajuste de línea, minimapa,
    números de línea, formatear al guardar…), Ctrl+K Ctrl+S lista de atajos, Ctrl+\\ dividir el editor, Ctrl+K Z modo zen (Esc sale),
    Ctrl+ / Ctrl− / Ctrl 0 tamaño de letra, Alt+Z ajuste de línea, Ctrl+Shift+O ir a símbolo, F12 definición, F2 renombrar, Ctrl+D
    multicursor, Alt+↑/↓ mover línea, Shift+Alt+F formatear, reabrir pestaña cerrada (paleta), Ctrl+K Ctrl+T temas de color
    (Dark+, Light+, Monokai, Dracula, One Dark Pro, GitHub, Night Owl, Solarized, alto contraste), Ctrl+Shift+V vista previa de
    Markdown, clic derecho en las pestañas (cerrar otras / a la derecha / todas, copiar ruta, dividir, mostrar en el explorador).
  · Servidores de desarrollo en Trabajo (panel PUERTOS junto a TERMINAL y CONSOLA; se abren en la vista previa):
    node server.js con Express o http (express, cors, body-parser, dotenv, morgan, express.static, Router, res.render con EJS),
    nodemon / node --watch (se reinicia al guardar), npm start / npm run dev / yarn / pnpm, php -S localhost:8000 (PHP real con
    sesiones), python -m http.server, npx serve, http-server, live-server, FastAPI/Flask/Django, y npx expo start (Expo con Expo
    Snack: vista web y QR para Expo Go en el celular). Next.js, Angular (ng serve), Nuxt, Astro, Laravel (php artisan serve),
    Rails, Spring Boot, Go y .NET web corren en Docker si el servidor lo tiene activo (DOCKER_TRABAJO=1).
  · Problemas: ⊗ errores y ⚠ advertencias de todo el proyecto y de lo que falla al ejecutar; los archivos dañados se ven en rojo;
    clic en ⊗/⚠ o Ctrl+Shift+M abre el panel PROBLEMAS.
  · Tu computador o celular (Conector): menú ⋯ → «Abrir carpeta del computador o celular…» o botón 🖥 de la terminal → descargas
    codigocamp-conector.py, lo abres con el código y confirmas con tu PIN/huella/contraseña. Eliges una carpeta de tu equipo y
    Trabajo la usa como editor de escritorio: lo guardado se escribe allá, lo que cambia allá aparece aquí; la terminal
    «🖥 equipo», ▶ Ejecutar y el panel de Git usan lo instalado en tu equipo. Nunca abre carpetas del sistema; el antivirus
    del equipo (Defender o ClamAV) revisa lo que entra, sale o se ejecuta.
  · Seguridad: los enlaces de virus o estafas nunca se abren (ni aceptando); los dudosos piden confirmación. Los archivos
    subidos pasan por un antivirus. Si un estudiante pregunta por qué se bloqueó algo, explícale el motivo con calma.
  · IA en Trabajo: Ctrl+I pide un cambio en el código seleccionado (o escribe en el cursor) y se acepta con Enter o
    se descarta con Esc; clic derecho en el editor → ✨ explicar, arreglar errores, mejorar, comentar/documentar, escribir pruebas;
    💡 bombilla (Ctrl+.) en cada error subrayado → «Arreglar con IA» o «Explicar este error»; en la terminal, si un comando falla,
    aparece «✨ Arreglar con IA»; en Git, «✨ Mensaje con IA» escribe el mensaje del commit; sugerencias en gris mientras escribes
    (Tab acepta); y el chat del Asistente con «Editar con IA» propone cambios en varios archivos que el alumno acepta o rechaza.
  · En Aprende, si el código da error aparece «✨ Explícame este error (IA)»; en los retos, «🤖 ¿Por qué?».
  · Terminal (Ctrl+Ñ o Ctrl+` la abre/cierra; Ctrl+Shift+Ñ terminal nueva; Ctrl+R busca en el historial): bash con ls, cd, cat,
    mkdir, rm, mv, cp, grep, find, head, tail, wc, echo, printf, sort, uniq, cut, tr, sed (también -i), awk, seq, rev, tac, nl, tee, diff,
    xargs, basename, dirname, du, stat, time, sleep, cal; variables (X=5), export, alias, read, test/[ ]/[[ ]], for/while/until/if/case,
    for ((i=0;i<5;i++)), funciones f() { …; } con $1 $# $@ y return, $((aritmética)), $(comando), ${var^^} ${var:-x} ${#var},
    scripts: bash archivo.sh, ./archivo.sh (chmod +x opcional) y source; tuberías |, && ; ||, redirecciones > >> <.
    Los bloques se pueden escribir en varias líneas (aparece «>» hasta cerrar con done/fi). Se pueden pegar varias líneas.
    nano/vim archivo abren el archivo en el editor. Si un programa pide datos (input(),
    Scanner, cin, scanf…), la terminal los pide con «»» (un dato por línea, línea vacía para ejecutar) o se pueden pasar con
    printf 'Ana\\n17\\n' | python programa.py.
  · Python: corre en el navegador (Pyodide). pip install y pip install -r requirements.txt instalan todo lo posible en el navegador; los
    paquetes con código en C que el navegador no soporta (opencv, psutil, mysqlclient, tensorflow…) se instalan solos con pip de verdad en el
    servidor, y los programas que los importan se ejecutan allí automáticamente. venv: python -m venv .venv y source .venv/bin/activate.
    Servidores: fastapi dev main.py, uvicorn main:app --reload, flask --app app run --debug, python manage.py runserver (Django).
  · Node: npm init, npm install <paquete>, npm run <script>, npm create vite@latest app -- --template react (o vue, svelte, preact).
  · Bases de datos: sqlite3, y con el «puente» las del alumno: mysql -u root (MySQL/XAMPP), psql, mongosh, redis-cli.
  · Docker de verdad (con el Docker del servidor o Docker Desktop si CódigoCamp corre en su PC): docker build -t app ., docker run --rm app,
    docker run -d -p 8080:80 app (se abre en http://localhost:8080), docker run -v ./:/app …, docker ps -a, images, logs, exec, stop, rm,
    rmi, pull, docker compose up -d | ps | logs | exec | down. Cada alumno solo ve sus contenedores; no se permite --privileged, la red del
    host ni montar carpetas fuera del proyecto. Si sale «Docker no está instalado / no está encendido», debe instalar o abrir Docker Desktop.
  · No existen en la terminal: sudo, apt, curl, wget, ssh, ni editores de terminal (vim, nano).
- Codi es la mascota de CódigoCamp: un robot con cabeza de visor, orejas en forma de { }, antena que se vuelve llama con la racha y
  torso de base de datos. Cambia de ánimo (feliz, en llamas, preocupado, en alarma, dormido…) según la racha y la hora.
- Reloj del día: cuenta regresiva de las horas que quedan para salvar la racha (en rojo con menos de 3 horas). Está en la tarjeta de
  racha, en el chip ⏳ de arriba (celular) y en los widgets. También se envían correos de aviso.
- Widgets: Android (app CódigoCamp → mantener pulsada la pantalla de inicio → Widgets → CódigoCamp: Tu racha, Reloj del día, Codi,
  Meta de hoy), Windows 11 (Windows+W: Tu racha, Reloj del día, Meta de hoy, Calendario), iPhone/iPad/Mac con Scriptable (parámetro
  racha, reloj, meta o calendario, también en la pantalla de bloqueo) y el widget flotante (📌) en cualquier computador.
  Se configuran en Configuración → App y widgets.
- En el celular CódigoCamp se usa en vertical (la app se bloquea en vertical; en el navegador Codi pide girar el teléfono).
- Tutor de IA (esta página): conversaciones guardadas, adjuntar imágenes, PDF, audio, video y código.
- Chats: agregar amigos por nombre, @usuario o ID (o desde los contactos del teléfono), enlace de invitación, mensajes con `código`,
  emojis, adjuntos (hasta 1 GB), eliminar mensajes para todos. Tocar la foto o el nombre del amigo (o ⋮ → Ver perfil) muestra su perfil:
  nivel, racha, retos por curso, lecciones, actividad de la semana y los cosméticos que tiene puestos.
- Tienda: con diamantes se compran fondos animados, punteros (normal, mano y texto), temas de color, marcos de foto, efectos al hacer
  clic, rastros del mouse o del dedo y potenciadores. «Probar» muestra la vista previa antes de comprar. Los fondos se ven detrás de todas
  las páginas con los paneles semitransparentes.
- Perfil: foto de perfil, lo que lleva puesto, cofres, cursos y su colección. Configuración: cuenta, aprendizaje (curso, meta diaria),
  apariencia (tema claro/oscuro/automático, cosméticos), seguridad (sesiones y dispositivos), correos y app/widgets."""

COPILOTO = """
MODO COPILOTO ACTIVADO: el alumno te dio permiso para proponer cambios en los archivos de su proyecto de Trabajo.

ANTES DE CAMBIAR NADA, analiza el archivo: lee el contenido actual que tienes arriba y ubica EXACTAMENTE las líneas que
hay que tocar. Tu trabajo es un cambio QUIRÚRGICO:
- Cambia SOLO lo que el alumno pidió o el error que hay que arreglar. Nada más.
- NO cambies diseño, estilos, colores, clases, textos, nombres de variables, estructura, orden, comentarios, formato,
  indentación ni comillas de lo que no tiene que ver con el pedido. NO «mejores», «limpies» ni «modernices» nada que no se pidió.
- Si el pedido es «arregla la contraseña del login», solo se toca lo de la contraseña: el resto del HTML/CSS queda idéntico.
- Si hay que tocar varios sitios, haz una edición pequeña por cada sitio.

Explica en 1 a 3 frases qué vas a cambiar y por qué, y AL FINAL agrega exactamente un bloque así:
```cc-cambios
{"resumen": "qué cambia, en una frase", "cambios": [
  {"accion": "editar", "ruta": "carpeta/archivo.ext", "ediciones": [
     {"buscar": "texto EXACTO que hoy está en el archivo (unas pocas líneas completas, copiadas tal cual)", "reemplazar": "cómo deben quedar esas líneas"}
  ]},
  {"accion": "crear", "ruta": "carpeta/nuevo.ext", "contenido": "contenido completo del archivo NUEVO"},
  {"accion": "borrar", "ruta": "archivo/que/sobra.ext"}
]}
```
Reglas del bloque:
- Para archivos que YA existen usa SIEMPRE «editar». «buscar» debe copiarse carácter por carácter del archivo actual (mismos espacios,
  tabulaciones y saltos de línea), incluir solo las líneas necesarias más 1 o 2 líneas vecinas para que sea único en el archivo,
  y no repetirse. Si hay que agregar algo nuevo, usa como «buscar» la línea junto a la que va y ponla también en «reemplazar».
- «crear» solo para archivos que no existen. Nunca reescribas un archivo existente completo, salvo que el alumno lo pida con esas palabras
  (en ese caso usa {"accion": "escribir", "ruta": ..., "contenido": ...}).
- JSON válido (escapa comillas y saltos de línea como \\n). Rutas relativas al proyecto como aparecen en la lista. Nada se aplica sin que
  el alumno lo acepte.
Si solo pregunta o no hace falta cambiar archivos, NO incluyas el bloque."""


def _limite(usuario):
    since = utcnow() - timedelta(minutes=1)
    if usuario:
        return TutorUsage.query.filter(TutorUsage.usuario_id == usuario.id, TutorUsage.creado_en >= since).count() >= 20
    return TutorUsage.query.filter(TutorUsage.usuario_id.is_(None), TutorUsage.ip == client_ip(), TutorUsage.creado_en >= since).count() >= 6


def _contexto_alumno():
    p = get_profile(current_user)
    niveles = {"cero": "empieza desde cero", "probado": "ha probado algo", "basico": "sabe lo básico", "avanzado": "tiene experiencia"}
    partes = [f"Se llama {current_user.nombre.split()[0]}."]
    if p.curso_actual:
        partes.append(f"Estudia {p.curso_actual.nombre} en CódigoCamp.")
    if p.nivel_previo in niveles:
        partes.append(f"Su nivel: {niveles[p.nivel_previo]}.")
    partes.append(f"Lleva {p.xp_total} XP y una racha de {p.racha_actual} días.")
    return "\n\nDatos del alumno: " + " ".join(partes)


def _contexto_trabajo(ctx):
    """Contexto que manda Trabajo: archivo abierto, selección, lista de archivos, otros archivos, problemas y terminal."""
    if not isinstance(ctx, dict):
        return ""
    trozos, total = [], 0

    def agregar(texto):
        nonlocal total
        if total >= CONTEXTO_MAX:
            return
        texto = texto[: CONTEXTO_MAX - total]
        total += len(texto)
        trozos.append(texto)

    pagina = str(ctx.get("pagina") or "")[:40]
    if pagina:
        agregar(f"\n\nEl alumno te escribe desde: {pagina}.")
    archivos = ctx.get("archivos")
    if isinstance(archivos, list) and archivos:
        lista = [str(a)[:300] for a in archivos[:500]]
        agregar("\nArchivos del proyecto:\n" + "\n".join(f"- {r}" for r in lista))
    abierto = ctx.get("archivo")
    if isinstance(abierto, dict) and abierto.get("ruta"):
        agregar(f"\n\nArchivo abierto: {str(abierto['ruta'])[:300]}\n```\n{str(abierto.get('contenido', ''))[:80_000]}\n```")
    sel = ctx.get("seleccion")
    if isinstance(sel, str) and sel.strip():
        agregar(f"\nTexto seleccionado por el alumno:\n```\n{sel[:20_000]}\n```")
    for extra in (ctx.get("extra") or [])[:30]:
        if isinstance(extra, dict) and extra.get("ruta"):
            agregar(f"\n\nOtro archivo del proyecto: {str(extra['ruta'])[:300]}\n```\n{str(extra.get('contenido', ''))[:40_000]}\n```")
    problemas = ctx.get("problemas")
    if isinstance(problemas, list) and problemas:
        agregar("\n\nProblemas que marca el editor:\n" + "\n".join(f"- {str(x)[:300]}" for x in problemas[:40]))
    terminal = ctx.get("terminal")
    if isinstance(terminal, str) and terminal.strip():
        agregar(f"\n\nÚltima salida de la terminal:\n```\n{terminal[-6000:]}\n```")
    return "".join(trozos)


# ------------------------------------------------------------------------- adjuntos → Gemini ----
def _peticion(url, datos=None, cabeceras=None, metodo=None, timeout=120):
    req = urllib.request.Request(url, data=datos, headers=cabeceras or {}, method=metodo)
    return urllib.request.urlopen(req, timeout=timeout)


def _subir_a_gemini(a, ruta, clave):
    """Sube un archivo a la API de archivos de Gemini (resumable) y espera a que esté listo. Devuelve su URI."""
    expira = a.gemini_expira
    if expira is not None and expira.tzinfo is None:
        expira = expira.replace(tzinfo=timezone.utc)
    if a.gemini_uri and expira and expira > utcnow() + timedelta(hours=1):
        return a.gemini_uri
    tam = os.path.getsize(ruta)
    inicio = _peticion(f"{API}/upload/v1beta/files", json.dumps({"file": {"display_name": a.nombre[:120]}}).encode(), {
        "x-goog-api-key": clave, "X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(tam), "X-Goog-Upload-Header-Content-Type": a.tipo, "Content-Type": "application/json",
    }, "POST", 60)
    destino = inicio.headers.get("X-Goog-Upload-URL")
    inicio.close()
    if not destino:
        raise RuntimeError("la IA no aceptó el archivo")
    with open(ruta, "rb") as f:
        r = _peticion(destino, f, {"Content-Length": str(tam), "X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize"}, "POST", 3600)
        info = json.load(r)["file"]
    nombre, estado = info["name"], info.get("state")
    for _ in range(90):  # video y audio se procesan antes de usarse (hasta ~3 min)
        if estado != "PROCESSING":
            break
        time.sleep(2)
        with _peticion(f"{API}/v1beta/{nombre}", cabeceras={"x-goog-api-key": clave}, timeout=30) as r:
            info = json.load(r)
            estado = info.get("state")
    if estado == "FAILED":
        raise RuntimeError("la IA no pudo procesar el archivo")
    a.gemini_uri = info["uri"]
    a.gemini_expira = utcnow() + timedelta(hours=46)
    return a.gemini_uri


def _partes_adjuntos(adjuntos, clave):
    partes, avisos = [], []
    for a in adjuntos:
        ruta = _ruta(a.usuario_id, a.hash)
        if not ruta.exists():
            avisos.append(f"(El archivo «{a.nombre}» ya no está disponible.)")
            continue
        ext = PurePosixPath(a.nombre.lower()).suffix.lstrip(".") or a.nombre.lower()
        try:
            if ext in EXT_TEXTO or a.tipo.startswith("text/") or a.tipo == "application/json":
                datos = ruta.read_bytes()[:TEXTO_MAX]
                texto = datos.decode("utf-8", "replace")
                corte = " (recortado)" if a.tamano > TEXTO_MAX else ""
                partes.append({"text": f"Archivo adjunto «{a.nombre}»{corte}:\n```{ext}\n{texto}\n```"})
            elif a.tipo in MIME_IA:
                if a.tamano <= EN_LINEA_MAX:
                    partes.append({"text": f"Archivo adjunto «{a.nombre}»:"})
                    partes.append({"inline_data": {"mime_type": a.tipo, "data": base64.b64encode(ruta.read_bytes()).decode()}})
                else:
                    uri = _subir_a_gemini(a, ruta, clave)
                    partes.append({"text": f"Archivo adjunto «{a.nombre}»:"})
                    partes.append({"file_data": {"mime_type": a.tipo, "file_uri": uri}})
            else:
                avisos.append(f"(Adjuntó «{a.nombre}», {a.tipo}, {a.tamano} bytes: ese tipo de archivo no se puede leer; responde con lo que se sabe por su nombre.)")
        except (urllib.error.URLError, RuntimeError, KeyError, OSError, TimeoutError) as e:
            current_app.logger.warning("No se pudo pasar %s a la IA: %s", a.nombre, e)
            avisos.append(f"(No se pudo leer «{a.nombre}».)")
    if avisos:
        partes.append({"text": "\n".join(avisos)})
    return partes


def explicar_error_gemini(codigo, cuerpo, modelo, *, tecnico=False):
    """Mensaje según lo que respondió Gemini. Al estudiante se le muestra un mensaje amable;
    el detalle técnico (qué corregir en backend/.env) queda en el registro del servidor y en `flask probar-ia`."""
    if not tecnico:
        try:
            current_app.logger.warning("IA: %s", explicar_error_gemini(codigo, cuerpo, modelo, tecnico=True))
        except Exception:
            pass
        if codigo == 429:
            return "Codi está atendiendo a mucha gente ahora mismo. Inténtalo de nuevo en un minuto."
        if codigo in (500, 502, 503, 504):
            return "Los servidores de Gemini (la IA de Google) están saturados ahora mismo. Ya probé con otros modelos; inténtalo en un minuto."
        return "Codi no pudo responder en este momento. Inténtalo de nuevo en un rato."
    texto = cuerpo.lower()
    if codigo in (500, 502, 503, 504):
        return f"Gemini está saturado (error {codigo}, «high demand»). Es temporal y del lado de Google; mientras tanto se usan otros modelos."
    if codigo == 429:
        return "La IA está muy ocupada o se acabó la cuota gratis de tu clave de Gemini por ahora. Inténtalo en un minuto."
    if codigo == 404 or "not found" in texto:
        return (f"Gemini no encontró el modelo «{modelo}» ni los de respaldo (error 404). En backend/.env pon el nombre exacto, "
                "por ejemplo GEMINI_MODEL=gemini-3.8-flash, y reinicia Flask.")
    if "api key not valid" in texto or "api_key_invalid" in texto or codigo in (401, 403):
        return "La clave de Gemini no es válida o no tiene permiso (revisa GEMINI_API_KEY en backend/.env, sin espacios, y reinicia Flask)."
    if "location is not supported" in texto or "user location" in texto:
        return "Gemini no está disponible desde tu ubicación o red para esta clave."
    return f"El tutor no pudo responder (Gemini respondió {codigo}). Inténtalo de nuevo."


@bp.post("/api/tutor/")
def tutor():
    data = json_body()
    if isinstance(data, tuple):
        return data
    message = str(data.get("mensaje", "")).strip()
    ids = data.get("adjuntos") or []
    if (not message and not ids) or len(message) > 12000:
        return api_error("Escribe una pregunta de hasta 12 000 caracteres (o adjunta un archivo).")
    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key:
        return api_error("Codi todavía no está disponible. Vuelve a intentarlo más tarde.", 503)
    usuario = current_user if current_user.is_authenticated else None
    if ids and not usuario:
        return api_error("Inicia sesión para enviar archivos a la IA.", 401)
    if _limite(usuario):
        return api_error("Has hecho muchas preguntas seguidas. Espera un minuto.", 429)
    adjuntos = []
    if ids:
        try:
            adjuntos = tomar(ids, "ia")
        except ValueError as e:
            return api_error(str(e))
    premios = []
    db.session.add(TutorUsage(usuario_id=usuario.id if usuario else None, ip=client_ip()))
    if usuario:
        from servicios.perfil import contar_actividad, get_profile
        premios = contar_actividad(get_profile(usuario), "ia")
    db.session.commit()

    history = data.get("historial") if isinstance(data.get("historial"), list) else []
    # Conversaciones guardadas: con conversacion_id (o guardar=true) el historial lo pone el servidor y se guarda la respuesta.
    conv = None
    if usuario and (data.get("conversacion_id") or data.get("guardar")):
        from rutas.conversaciones import propia
        from models import AIConversation
        conv = propia(data.get("conversacion_id")) if data.get("conversacion_id") else None
        if conv is None:   # no existe (se borró o es de otra cuenta): se empieza una nueva en lugar de fallar
            conv = AIConversation(usuario_id=usuario.id)
            db.session.add(conv)
            db.session.flush()
        previos = list(conv.mensajes)
        pregunta = message or "(archivos)"
        # La misma pregunta otra vez (reintento, doble clic o la red la mandó dos veces): nunca se repite en la conversación.
        if previos and previos[-1].rol == "yo" and previos[-1].texto == pregunta:
            previos = previos[:-1]
        elif (data.get("reintento") and len(previos) >= 2 and previos[-1].rol == "tutor" and previos[-2].rol == "yo"
              and previos[-2].texto == pregunta and _reciente(previos[-1].creado)):
            # Ya se respondió mientras la conexión estaba cortada: se devuelve esa respuesta sin volver a preguntarle a Gemini
            return _respuesta_guardada(conv, previos[-1].texto, premios, bool(data.get("stream")))
        else:
            from rutas.conversaciones import guardar_pregunta
            guardar_pregunta(conv, message, [a.nombre for a in adjuntos])
        history = [{"rol": m.rol, "texto": m.texto} for m in previos[-16:]]
    contents = [{"role": "model" if item.get("rol") == "tutor" else "user", "parts": [{"text": str(item.get("texto", ""))[:12000] or "…"}]}
                for item in history[-16:] if isinstance(item, dict)]
    partes = _partes_adjuntos(adjuntos, api_key) if adjuntos else []
    partes.append({"text": message or "Analiza los archivos adjuntos."})
    contents.append({"role": "user", "parts": partes})
    db.session.commit()  # guarda las URI de Gemini de los adjuntos grandes

    ctx = data.get("contexto") if isinstance(data.get("contexto"), dict) else {}
    copiloto = bool(ctx.get("copiloto")) and usuario is not None
    sistema = _con_idioma(SISTEMA + (_contexto_alumno() if usuario else "") + _contexto_trabajo(ctx) + (COPILOTO if copiloto else ""))
    modelo = current_app.config["GEMINI_MODEL"]
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": sistema}]}, "contents": contents,
        # Rápido e inteligente: piensa poco en preguntas simples y más en errores, código y cambios grandes
        "generationConfig": {"temperature": 0.15 if copiloto else 0.6, "maxOutputTokens": 16384 if copiloto else 8192,
                             "thinkingConfig": {"thinkingLevel": nivel_pensar(message, copiloto, len(adjuntos or []),
                                                                              len(ctx.get("archivos") or []) if isinstance(ctx.get("archivos"), (list, dict)) else 0)}},
    }).encode()
    if data.get("stream") and not copiloto:
        # Al generador se le pasa solo el id: la sesión de la base de esta petición se cierra cuando la vista termina
        # (en el servidor real), así que el objeto conv ya no sirve dentro de la respuesta en vivo.
        info = {"id": conv.id, "titulo": conv.titulo} if conv is not None else None
        return _responder_en_vivo(payload, api_key, modelo, info, message, adjuntos, premios)
    try:
        result, modelo = generar(payload, api_key, modelo, esperar_max=12)
        cand = result["candidates"][0]
        answer = "".join(part.get("text", "") for part in cand.get("content", {}).get("parts", []) if not part.get("thought")).strip()
        if not answer:
            raise ValueError(cand.get("finishReason", "respuesta vacía"))
    except urllib.error.HTTPError as e:
        cuerpo = e.read()[:800].decode("utf-8", "replace")
        current_app.logger.warning("Gemini respondió %s: %s", e.code, cuerpo)
        return api_error(explicar_error_gemini(e.code, cuerpo, modelo), 429 if e.code == 429 else 502)
    except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError):
        current_app.logger.exception("No se pudo completar la solicitud al tutor de IA.")
        return api_error("El tutor no pudo responder ahora. Inténtalo de nuevo.", 502)
    if conv is not None:
        from rutas.conversaciones import guardar_respuesta
        guardar_respuesta(conv, answer)
        return jsonify(respuesta=answer, copiloto=copiloto, conversacion={"id": conv.id, "titulo": conv.titulo}, desafios_completados=premios)
    return jsonify(respuesta=answer, copiloto=copiloto, desafios_completados=premios)


def _reciente(fecha, minutos=15):
    if fecha is None:
        return False
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    return utcnow() - fecha <= timedelta(minutes=minutos)


def _respuesta_guardada(conv, texto, premios, stream):
    """Respuesta que ya estaba guardada (llegó mientras la conexión estaba cortada)."""
    info = {"id": conv.id, "titulo": conv.titulo}
    if not stream:
        return jsonify(respuesta=texto, copiloto=False, conversacion=info, desafios_completados=premios)
    from flask import Response

    def eventos():
        for d in ({"conv": info}, {"t": texto}, {"fin": True, "respuesta": texto, "copiloto": False, "desafios_completados": premios, "conversacion": info}):
            yield f"data: {json.dumps(d, ensure_ascii=False)}\n\n"
    return Response(eventos(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _trozos_gemini(payload, api_key, modelo):
    """Pide la respuesta a Gemini EN VIVO (streamGenerateContent): devuelve los trozos de texto según llegan."""
    m = _modelo_que_funciona.get(modelo, modelo)
    if _descanso.get(m, 0) > time.monotonic():
        raise urllib.error.URLError("modelo en descanso")
    _anotar_llamada()
    r = _peticion(f"{API}/v1beta/models/{m}:streamGenerateContent?alt=sse", payload, {"Content-Type": "application/json", "x-goog-api-key": api_key}, "POST", 120)
    with r:
        for linea in r:
            linea = linea.decode("utf-8", "replace").strip()
            if not linea.startswith("data:"):
                continue
            try:
                d = json.loads(linea[5:])
                partes = d["candidates"][0].get("content", {}).get("parts", [])
            except (ValueError, KeyError, IndexError):
                continue
            texto = "".join(p.get("text", "") for p in partes if not p.get("thought"))
            if texto:
                yield texto


def _guardar_respuesta_id(conv_id, texto):
    """Guarda la respuesta buscando la conversación de nuevo (sirve dentro de la respuesta en vivo)."""
    from models import AIConversation
    from rutas.conversaciones import guardar_respuesta
    try:
        conv = db.session.get(AIConversation, conv_id)
        if conv is not None:
            guardar_respuesta(conv, texto)
    except Exception:  # noqa: BLE001
        db.session.rollback()
        raise


def _responder_en_vivo(payload, api_key, modelo, conv, message, adjuntos, premios):
    """conv: {"id", "titulo"} de la conversación guardada (o None)."""
    """La respuesta llega palabra por palabra (como en las apps de chat): se siente instantánea aunque Gemini tarde.
    Si el modelo principal falla antes de empezar, se usan los de respaldo (respuesta completa de una vez)."""
    from flask import Response, stream_with_context

    def evento(**d):
        return f"data: {json.dumps(d, ensure_ascii=False)}\n\n"

    def generar_eventos():
        texto = ""
        trozos = None
        desconectado = False
        try:
            if conv is not None:   # el navegador sabe enseguida en qué conversación quedó (aunque luego se corte)
                yield evento(conv=conv)
            try:
                trozos = _trozos_gemini(payload, api_key, modelo)
                for trozo in trozos:
                    texto += trozo
                    yield evento(t=trozo)
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:   # HTTPError incluido
                if texto:
                    current_app.logger.warning("La respuesta en vivo se cortó: %s", e)
                else:
                    current_app.logger.warning("Respuesta en vivo no disponible (%s): se usa la respuesta completa.", e)
            if not texto.strip():
                # El modo en vivo falló o no trajo texto: se pide la respuesta completa (con modelos de respaldo)
                result, _ = generar(payload, api_key, modelo, esperar_max=12)
                cand = result["candidates"][0]
                texto = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought")).strip()
                if not texto:
                    raise ValueError(cand.get("finishReason", "respuesta vacía"))
                yield evento(t=texto)
            texto = texto.strip()
            if not texto:
                raise ValueError("respuesta vacía")
            fin = {"fin": True, "respuesta": texto, "copiloto": False, "desafios_completados": premios}
            if conv is not None:
                _guardar_respuesta_id(conv["id"], texto)
                fin["conversacion"] = conv
                texto = ""   # ya quedó guardada
            yield evento(**fin)
        except GeneratorExit:
            # La persona cerró la página, bloqueó el celular o se cayó la red: se termina de recibir la respuesta de Gemini
            # y se guarda igual (la verá al volver, en cualquier dispositivo).
            desconectado = True
        except urllib.error.HTTPError as e:
            cuerpo = e.read()[:800].decode("utf-8", "replace")
            current_app.logger.warning("Gemini respondió %s: %s", e.code, cuerpo)
            yield evento(error=explicar_error_gemini(e.code, cuerpo, modelo))
        except Exception:   # noqa: BLE001 — cualquier fallo se le explica a la persona
            current_app.logger.exception("No se pudo completar la respuesta en vivo.")
            yield evento(error="El tutor no pudo responder ahora. Inténtalo de nuevo.")
        finally:
            if desconectado and conv is not None:
                try:
                    if trozos is None:   # se fue antes de empezar: se pide la respuesta completa
                        result, _ = generar(payload, api_key, modelo, esperar_max=12)
                        texto = "".join(p.get("text", "") for p in result["candidates"][0].get("content", {}).get("parts", []) if not p.get("thought"))
                    else:
                        for trozo in trozos:
                            texto += trozo
                except Exception:   # noqa: BLE001
                    pass
            if desconectado and conv is not None and texto.strip():
                try:
                    _guardar_respuesta_id(conv["id"], texto.strip())
                except Exception:   # noqa: BLE001
                    db.session.rollback()

    return Response(stream_with_context(generar_eventos()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


_PIENSA = re.compile(r"```|traceback|error|exception|bug|falla|no funciona|no sirve|por ?qu[eé]|arregl|optimiz|refactor|algoritm|complejidad|"
                     r"diferencia entre|compar|dise[ñn]a|arquitect|seguridad|migr|base de datos|consulta|regex|recursi", re.I)


def nivel_pensar(mensaje, copiloto=False, adjuntos=0, archivos_ctx=0):
    """Cuánto «piensa» la IA: poco en preguntas simples (responde al instante) y más en errores, código y diseño."""
    m = mensaje or ""
    if copiloto:
        return "high" if len(m) > 400 or archivos_ctx > 6 or re.search(r"todo el proyecto|refactor|migra|arquitect", m, re.I) else "medium"
    if adjuntos or len(m) > 600 or _PIENSA.search(m):
        return "medium"
    if len(m) < 80 and "\n" not in m:
        return "minimal"
    return "low"


COMPLETAR = """Eres un motor de autocompletado de código como GitHub Copilot, dentro del editor de CódigoCamp.
Recibes el archivo con el cursor marcado como <CURSOR>. Devuelve SOLO el texto que va exactamente en el cursor:
sin explicaciones, sin ``` ni repetir lo que ya está antes o después del cursor.
- Completa la línea actual y, si es natural, unas pocas líneas más (máximo 12) siguiendo el estilo y la indentación del archivo.
- Usa los nombres de variables, funciones e imports que ya existen en el archivo y en los otros archivos que te paso.
- Si el código ya está completo en ese punto o no sabes qué sigue, devuelve una cadena vacía.
- Comentarios en español, como el resto de CódigoCamp."""


@bp.post("/api/tutor/completar/")
@login_required
def completar():
    """Sugerencias en línea (texto fantasma) mientras escribes en Trabajo. Tab las acepta."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    antes, despues = str(data.get("antes", ""))[-6000:], str(data.get("despues", ""))[:2000]
    if not antes.strip():
        return jsonify(texto="")
    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key:
        return api_error("La ayuda de Codi no está disponible ahora.", 503)
    if too_many(f"completar:{current_user.id}", 20, 60):   # como mucho 1 cada 3 s escribiendo seguido
        return jsonify(texto="", espera=True)
    # El chat tiene prioridad: si en el último minuto ya hubo muchas llamadas, el texto fantasma descansa
    if llamadas_ultimo_minuto() >= current_app.config.get("IA_RESERVA_CHAT", 25):
        return jsonify(texto="", espera=True)
    modelo_rapido = current_app.config.get("GEMINI_MODEL_RAPIDO") or "gemini-3.5-flash-lite"
    if en_descanso(modelo_rapido):
        return jsonify(texto="", espera=True)
    ruta, lenguaje = str(data.get("ruta", ""))[:200], str(data.get("lenguaje", ""))[:30]
    otros = ""
    for o in (data.get("otros") or [])[:4]:
        if isinstance(o, dict):
            otros += f"\n--- {str(o.get('ruta', ''))[:200]} ---\n{str(o.get('texto', ''))[:3000]}\n"
    prompt = (f"Archivo: {ruta} ({lenguaje})\n" + (f"Otros archivos del proyecto:{otros}\n" if otros else "")
              + f"--- {ruta} ---\n{antes}<CURSOR>{despues}")
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": COMPLETAR}]}, "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 400, "thinkingConfig": {"thinkingLevel": "minimal"}},
    }).encode()
    try:
        result, _ = generar(payload, api_key, modelo_rapido, timeout=20, respaldo=RESPALDO_RAPIDO)
        cand = result["candidates"][0]
        texto = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
    except urllib.error.HTTPError as e:
        if e.code == 400:   # modelos sin thinkingConfig: se reintenta sin él
            try:
                p2 = json.loads(payload); p2["generationConfig"].pop("thinkingConfig", None)
                result, _ = generar(json.dumps(p2).encode(), api_key, modelo_rapido, timeout=20, respaldo=RESPALDO_RAPIDO)
                texto = "".join(p.get("text", "") for p in result["candidates"][0].get("content", {}).get("parts", []) if not p.get("thought"))
            except Exception:
                return jsonify(texto="")
        else:
            return jsonify(texto="")
    except Exception:
        return jsonify(texto="")
    return jsonify(texto=limpiar_sugerencia(texto, antes, despues))


def limpiar_sugerencia(texto, antes, despues):
    """Quita cercas ```, el marcador y lo que la IA repitió del texto de antes o de después del cursor."""
    t = texto.replace("<CURSOR>", "")
    m = re.match(r"^\s*```[\w+-]*\n([\s\S]*?)\n?```\s*$", t)
    if m:
        t = m.group(1)
    linea = antes.rsplit("\n", 1)[-1]
    if linea.strip() and t.startswith(linea):      # repitió la línea ya escrita
        t = t[len(linea):]
    sig = despues.split("\n", 1)[0]
    if sig.strip() and t.rstrip().endswith(sig.strip()):   # repitió lo que ya está después
        t = t.rstrip()[: -len(sig.strip())]
    lineas = t.split("\n")[:12]
    return "\n".join(lineas).rstrip() if len(lineas) > 1 else lineas[0]


def _en_ingles():
    """¿La cuenta usa CódigoCamp en inglés? Entonces la IA responde en inglés."""
    try:
        from flask_login import current_user
        from models import Profile
        if not current_user.is_authenticated:
            return False
        p = Profile.query.filter_by(usuario_id=current_user.id).first()
        return bool(p and p.idioma == "en")
    except Exception:
        return False


IDIOMA_EN = ("\n\nIMPORTANT: the student uses CódigoCamp in ENGLISH. Answer ONLY in clear, friendly English "
             "(code comments and commit messages in English too). Keep the names CódigoCamp and Codi.")


def _con_idioma(sistema):
    return sistema + (IDIOMA_EN if _en_ingles() else "")


PORQUE = """Eres Codi, el tutor de CódigoCamp. Explica en español, SIMPLE y CORTO (1 o 2 frases, máximo 40 palabras), POR QUÉ
la respuesta correcta es la correcta: la idea de fondo, con palabras fáciles. NO repitas la pregunta ni la respuesta (el alumno ya
las ve) ni la «explicación guardada». Si el alumno respondió otra cosa, di en pocas palabras por qué eso no era. Sin títulos, sin
listas, sin saludar. Usa `código` para nombres de código."""


@bp.post("/api/reto/<int:reto_id>/porque/")
@login_required
def porque_reto(reto_id):
    """«¿Por qué?» en los retos: la IA explica la respuesta correcta (y el error del alumno si lo hubo)."""
    from models import Challenge
    reto = db.session.get(Challenge, reto_id)
    if not reto:
        return api_error("No encontramos ese reto.", 404)
    data = json_body()
    if isinstance(data, tuple):
        return data
    respuesta_alumno = data.get("respuesta")
    if isinstance(respuesta_alumno, dict):   # unir parejas: no hace falta mandar las parejas del alumno
        respuesta_alumno = f"(se equivocó {respuesta_alumno.get('fallos', 0)} vez/veces al unir)"
    elif isinstance(respuesta_alumno, list):
        respuesta_alumno = (" " if reto.tipo == "armar" else " → ").join(map(str, respuesta_alumno))
    respuesta_alumno = str(respuesta_alumno or "")[:500]
    correcta = reto.respuesta.split("|")[0] if reto.tipo == "completar" else reto.respuesta
    if reto.tipo == "error":
        correcta = f"la línea {reto.respuesta}"
    elif reto.tipo == "ordenar":
        correcta = " → ".join((reto.datos or {}).get("piezas", []))
    elif reto.tipo == "parejas":
        correcta = "; ".join(f"{a} → {b}" for a, b in (reto.datos or {}).get("pares", []))
    elif reto.tipo == "armar":
        correcta = " ".join((reto.datos or {}).get("solucion", []))
    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key or too_many(f"porque:{current_user.id}", 15, 60):
        return jsonify(texto=reto.explicacion or f"La respuesta correcta es «{correcta}».", ia=False)
    prompt = (f"Reto ({reto.tipo}): {reto.enunciado}\n" + (f"Código:\n```\n{reto.codigo}\n```\n" if reto.codigo else "")
              + (f"Opciones: {' | '.join(map(str, reto.opciones or []))}\n" if reto.opciones else "")
              + f"Respuesta correcta: {correcta}\nExplicación guardada: {reto.explicacion}\n"
              + (f"El alumno respondió: {respuesta_alumno}\n" if respuesta_alumno else ""))
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": _con_idioma(PORQUE)}]}, "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 350},
    }).encode()
    try:
        result, _ = generar(payload, api_key, current_app.config["GEMINI_MODEL"], timeout=25)
        texto = "".join(p.get("text", "") for p in result["candidates"][0].get("content", {}).get("parts", []) if not p.get("thought")).strip()
    except Exception:
        texto = ""
    return jsonify(texto=texto or reto.explicacion, ia=bool(texto))


EDITAR = """Eres el copiloto de código de CódigoCamp («Ctrl+I» en Trabajo). Te dan un archivo con una SELECCIÓN
(o un cursor) y una instrucción del alumno. Devuelve SOLO el código que debe ir en lugar de la selección (o insertarse en el
cursor): sin explicaciones, sin ``` y sin repetir lo que está antes o después. Respeta la sangría, el estilo y el lenguaje del
archivo. Cambia solo lo pedido. Si la instrucción pide comentarios o documentación, escríbelos en español."""

COMMIT = """Escribe UN mensaje de commit de git en español para estos cambios: una primera línea de máximo 60 caracteres en
imperativo («Agrega…», «Corrige…»), y si hace falta una línea en blanco y 1 a 3 viñetas cortas con «- ». Solo el mensaje."""


def _texto_gemini(prompt, sistema, tokens=1500, temperatura=0.2, timeout=40):
    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key:
        raise ValueError("La IA no está configurada en este servidor (falta GEMINI_API_KEY en backend/.env).")
    payload = json.dumps({"systemInstruction": {"parts": [{"text": sistema}]}, "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                          "generationConfig": {"temperature": temperatura, "maxOutputTokens": tokens}}).encode()
    result, _ = generar(payload, api_key, current_app.config["GEMINI_MODEL"], timeout=timeout, esperar_max=8)
    return "".join(p.get("text", "") for p in result["candidates"][0].get("content", {}).get("parts", []) if not p.get("thought"))


def sin_cercas(texto):
    t = texto.strip("\n")
    m = re.match(r"^\s*```[\w+#.-]*\n([\s\S]*?)\n?```\s*$", t)
    return m.group(1) if m else t


@bp.post("/api/tutor/editar/")
@login_required
def editar_en_linea():
    """Ctrl+I en Trabajo: reescribe la selección (o escribe en el cursor) según la instrucción."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    instruccion = str(data.get("instruccion", "")).strip()[:2000]
    if not instruccion:
        return api_error("Escribe qué quieres que haga la IA.")
    if too_many(f"editar:{current_user.id}", 20, 60):
        return api_error("Vas muy rápido. Espera unos segundos.", 429)
    ruta, lenguaje = str(data.get("ruta", ""))[:200], str(data.get("lenguaje", ""))[:30]
    antes, sel, despues = str(data.get("antes", ""))[-8000:], str(data.get("seleccion", ""))[:20000], str(data.get("despues", ""))[:4000]
    prompt = (f"Archivo: {ruta} ({lenguaje})\nInstrucción: {instruccion}\n\n--- antes ---\n{antes}\n--- SELECCIÓN"
              f"{' (vacía: escribe en el cursor)' if not sel else ''} ---\n{sel}\n--- después ---\n{despues}")
    try:
        texto = _texto_gemini(prompt, _con_idioma(EDITAR), tokens=4000)
    except ValueError as e:
        return api_error(str(e), 503)
    except Exception:
        current_app.logger.exception("Falló Ctrl+I")
        return api_error("La IA no respondió. Inténtalo de nuevo.", 502)
    return jsonify(texto=sin_cercas(texto))


@bp.post("/api/tutor/commit/")
@login_required
def mensaje_commit():
    """Mensaje de commit escrito por la IA a partir de las diferencias."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    diff = str(data.get("diff", ""))[:30000]
    if not diff.strip():
        return api_error("No hay cambios para describir.")
    if too_many(f"commit:{current_user.id}", 10, 60):
        return api_error("Vas muy rápido. Espera unos segundos.", 429)
    try:
        texto = _texto_gemini(diff, _con_idioma(COMMIT), tokens=300, temperatura=0.3, timeout=25)
    except ValueError as e:
        return api_error(str(e), 503)
    except Exception:
        return api_error("La IA no respondió. Inténtalo de nuevo.", 502)
    return jsonify(texto=sin_cercas(texto).strip().strip('"'))


# ------------------------------------------------------------------------------ Codi piensa ----
CODI_PIENSA = """Eres Codi, la mascota robot de CódigoCamp (una app para aprender a programar, en español de Colombia).
Tienes personalidad propia: curioso, divertido, cariñoso, un poco travieso, amante del código y de los bits. Piensas por ti
mismo: comentas lo que ves (la hora, la página, el progreso de la persona), te inventas ocurrencias, preguntas cosas,
cuentas chistes NUEVOS sobre programación y das consejos útiles. Nunca repites frases hechas ni las que ya dijiste.
Responde SOLO con un JSON: {"frase": "...", "animo": "..."}
- frase: máximo 140 caracteres, natural, cercana, puedes usar 1 emoji. Sin comillas extra ni markdown.
- animo: uno de feliz, celebra, pensando, saludo, guino, ama, asombro, baila, espia, preocupado, triste, fuego.
Nunca pidas datos personales, nunca hables de temas para adultos, violencia o política. Si te escriben algo inapropiado,
cambia el tema con gracia hacia programar."""
ANIMOS_CODI = {"feliz", "celebra", "pensando", "saludo", "guino", "ama", "asombro", "baila", "espia", "preocupado", "triste", "fuego"}
MOTIVOS_CODI = {
    "toque": "La persona te acaba de tocar/hacer clic. Reacciona con algo espontáneo y distinto.",
    "saludo": "La persona acaba de entrar a esta página. Salúdala comentando algo de su contexto.",
    "vida": "Llevas un rato quieto en la pantalla. Di un pensamiento tuyo, curioso o gracioso, sin interrumpir mucho.",
    "chiste": "Cuenta un chiste corto y original de programación (nuevo, no de los típicos).",
    "consejo": "Da un consejo concreto y útil para aprender a programar, según lo que esté haciendo.",
    "animo": "Dale ánimo según su progreso real (racha, XP de hoy, encargos que le faltan).",
    "charla": "La persona te escribió el mensaje de abajo. Respóndele como Codi, corto y con personalidad.",
    "pensar": "Te preguntaron «¿qué estás pensando?». Cuenta qué piensas tú ahora mismo, como un personaje con vida propia.",
}


def _contexto_codi(usuario, pagina):
    from datetime import datetime
    partes = [f"Página: {pagina or 'inicio'}.", f"Hora local aproximada: {datetime.now():%H:%M}."]
    if usuario:
        try:
            from servicios.perfil import actividad_de_hoy, encargos_del_dia, get_profile, progreso_encargo
            p = get_profile(usuario)
            from servicios.zona import ahora_de
            partes[1] = f"Hora de la persona: {ahora_de(p):%H:%M}."
            hoy = actividad_de_hoy(p)
            faltan = [e["titulo"] for e in encargos_del_dia(usuario.id, hoy.fecha) if progreso_encargo(e, hoy) < e["meta"]][:3]
            partes.append(f"Se llama {usuario.nombre.split()[0]}. Nivel {p.nivel}, racha de {p.racha_actual} días, {hoy.xp} XP hoy, "
                          f"{hoy.niveles} niveles y {hoy.lecciones} lecciones hoy, {p.vidas} vidas.")
            if p.curso_actual:
                partes.append(f"Está aprendiendo {p.curso_actual.nombre}.")
            if faltan:
                partes.append("Encargos de hoy que le faltan: " + "; ".join(faltan) + ".")
        except Exception:  # noqa: BLE001 — el contexto es opcional
            pass
    return " ".join(partes)


@bp.post("/api/codi/pensar/")
def codi_pensar():
    """Codi piensa por sí mismo: cada frase la crea la IA en el momento (con el contexto de la persona). Si la IA no está
    disponible, el navegador usa sus frases de siempre."""
    data = json_body()
    if isinstance(data, tuple):
        return data
    api_key = current_app.config.get("GEMINI_API_KEY")
    usuario = current_user if current_user.is_authenticated else None
    quien = f"u{usuario.id}" if usuario else f"ip{client_ip()}"
    if not api_key:
        return api_error("Codi está pensando en silencio.", 503)
    if too_many(f"codi:{quien}", 20 if usuario else 6, 60):
        return api_error("Codi necesita un respiro.", 429)
    motivo = str(data.get("motivo") or "toque")
    if motivo not in MOTIVOS_CODI:
        motivo = "toque"
    mensaje = str(data.get("mensaje") or "")[:300]
    if motivo == "charla" and not mensaje.strip():
        return api_error("Escríbele algo a Codi.")
    dichas = [str(x)[:160] for x in (data.get("dichas") or [])][-8:]
    texto = (f"{MOTIVOS_CODI[motivo]}\nContexto: {_contexto_codi(usuario, str(data.get('pagina') or '')[:40])}\n"
             + (f"Mensaje de la persona: «{mensaje}»\n" if motivo == "charla" else "")
             + (f"NO repitas ni parafrasees estas frases que ya dijiste: {' | '.join(dichas)}\n" if dichas else "")
             + f"Semilla de variedad: {secrets.token_hex(3)}")
    modelo_rapido = current_app.config.get("GEMINI_MODEL_RAPIDO") or "gemini-3.5-flash-lite"
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": CODI_PIENSA}]},
        "contents": [{"role": "user", "parts": [{"text": texto}]}],
        "generationConfig": {"temperature": 1.1, "maxOutputTokens": 200, "responseMimeType": "application/json",
                             "thinkingConfig": {"thinkingLevel": "minimal"}},
    }).encode()
    try:
        result, _ = generar(payload, api_key, modelo_rapido, timeout=12, respaldo=RESPALDO_RAPIDO)
        crudo = "".join(p.get("text", "") for p in result["candidates"][0].get("content", {}).get("parts", []) if not p.get("thought"))
        d = json.loads(crudo[crudo.find("{"): crudo.rfind("}") + 1])
        frase = re.sub(r"\s+", " ", str(d.get("frase") or "")).strip()[:180]
        if not frase:
            raise ValueError("vacía")
    except Exception:  # noqa: BLE001 — Codi nunca rompe la página
        return api_error("Codi se quedó sin ideas por un momento.", 502)
    animo = str(d.get("animo") or "feliz")
    db.session.rollback()   # el contexto no guarda nada
    return jsonify(frase=frase, animo=animo if animo in ANIMOS_CODI else "feliz")
