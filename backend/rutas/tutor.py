"""Tutor de IA (Gemini): responde con el contexto del alumno, del archivo y del proyecto abiertos, acepta archivos
adjuntos (imágenes, video, audio, PDF, código… hasta 1 GB) y, en modo copiloto, propone cambios en los archivos
que el alumno revisa y acepta uno por uno en Trabajo.

backend/.env:  GEMINI_API_KEY=...   GEMINI_MODEL=gemini-3.8-flash
Los archivos de más de 8 MB (o de tipos que no van en línea) se suben a la API de archivos de Gemini, que los guarda 48 h.
"""
import base64
import json
import re
import os
import time
import urllib.error
import urllib.request
from datetime import timedelta, timezone
from pathlib import PurePosixPath

from flask import Blueprint, current_app, jsonify
from flask_login import current_user

from models import Attachment, TutorUsage, db, utcnow
from rutas.archivos import _ruta
from rutas.adjuntos import tomar
from servicios.perfil import get_profile
from utilidades import api_error, client_ip, json_body

bp = Blueprint("tutor", __name__)
API = "https://generativelanguage.googleapis.com"
# Si el modelo de backend/.env no existe para tu clave (404), se prueban estos en orden.
MODELOS_RESPALDO = ("gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash")
_modelo_que_funciona = {}


def normalizar_modelo(nombre):
    """«Gemini 3.8», «gemini-3.8», «models/gemini-3.8-flash» → «gemini-3.8-flash»."""
    n = str(nombre or "").strip().strip('"').strip("'").lower().removeprefix("models/")
    n = re.sub(r"\s+", "-", n)
    if re.fullmatch(r"(gemini-)?\d+(\.\d+)?", n):          # solo el número: se usa su versión Flash
        n = f"gemini-{n.removeprefix('gemini-')}-flash"
    if n and not n.startswith(("gemini", "gemma", "learnlm")):
        n = "gemini-" + n
    return n or MODELOS_RESPALDO[0]


def generar(payload, api_key, modelo, timeout=180):
    """Llama a generateContent; si Gemini dice 404 (modelo inexistente para esta clave), prueba los de respaldo."""
    modelo = normalizar_modelo(modelo)
    candidatos = [_modelo_que_funciona.get(modelo, modelo)] + [m for m in MODELOS_RESPALDO if m != modelo]
    ultimo = None
    for m in dict.fromkeys(candidatos):
        try:
            with _peticion(f"{API}/v1beta/models/{m}:generateContent", payload, {"Content-Type": "application/json", "x-goog-api-key": api_key}, "POST", timeout) as r:
                datos = json.load(r)
            if m != modelo:
                current_app.logger.warning("El modelo «%s» no está disponible para tu clave; se usó «%s». Pon GEMINI_MODEL=%s en backend/.env.", modelo, m, m)
            _modelo_que_funciona[modelo] = m
            return datos, m
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            ultimo = e
    raise ultimo
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
- En Trabajo funcionan como en VS Code: python -m venv .venv, fastapi dev main.py, uvicorn main:app --reload, flask --app app run --debug
  (la vista previa abre http://127.0.0.1:8000/docs). uvicorn, gunicorn y uvloop no hace falta instalarlos: CódigoCamp hace de servidor.
- Si es un reto o ejercicio de clase, da primero una pista y ofrece la solución si la pide.
- Si te pasan archivos (imágenes, capturas, PDF, video, audio, código), analízalos y refiérete a ellos por su nombre.
- Si no sabes algo con seguridad, dilo. No inventes funciones ni librerías.
- Usa listas cortas con guiones; evita tablas grandes y títulos largos.
- Si la pregunta no tiene que ver con programación, tecnología o estudio, explica amablemente que eres el tutor de programación."""

COPILOTO = """
MODO COPILOTO ACTIVADO: el alumno te dio permiso para proponer cambios en los archivos de su proyecto de Trabajo.
Cuando pida crear, modificar, arreglar o borrar archivos, explica brevemente qué vas a cambiar y AL FINAL agrega exactamente un bloque así:
```cc-cambios
{"resumen": "qué cambia, en una frase", "cambios": [
  {"accion": "escribir", "ruta": "carpeta/archivo.ext", "contenido": "EL CONTENIDO COMPLETO Y FINAL DEL ARCHIVO"},
  {"accion": "borrar", "ruta": "archivo/que/sobra.ext"}
]}
```
Reglas del bloque: JSON válido (escapa comillas y saltos de línea como \\n), rutas relativas al proyecto como aparecen en la lista, siempre el
contenido COMPLETO de cada archivo que escribas (no fragmentos ni «...»), solo los archivos necesarios. Nada se aplica sin que el alumno lo acepte.
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


def explicar_error_gemini(codigo, cuerpo, modelo):
    """Mensaje claro según lo que respondió Gemini (para saber qué corregir en backend/.env)."""
    texto = cuerpo.lower()
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
        return api_error("El tutor todavía no está configurado (falta GEMINI_API_KEY en backend/.env).", 503)
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
    db.session.add(TutorUsage(usuario_id=usuario.id if usuario else None, ip=client_ip()))
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
        history = [{"rol": m.rol, "texto": m.texto} for m in conv.mensajes[-16:]]
    contents = [{"role": "model" if item.get("rol") == "tutor" else "user", "parts": [{"text": str(item.get("texto", ""))[:12000] or "…"}]}
                for item in history[-16:] if isinstance(item, dict)]
    partes = _partes_adjuntos(adjuntos, api_key) if adjuntos else []
    partes.append({"text": message or "Analiza los archivos adjuntos."})
    contents.append({"role": "user", "parts": partes})
    db.session.commit()  # guarda las URI de Gemini de los adjuntos grandes

    ctx = data.get("contexto") if isinstance(data.get("contexto"), dict) else {}
    copiloto = bool(ctx.get("copiloto")) and usuario is not None
    sistema = SISTEMA + (_contexto_alumno() if usuario else "") + _contexto_trabajo(ctx) + (COPILOTO if copiloto else "")
    modelo = current_app.config["GEMINI_MODEL"]
    payload = json.dumps({
        "systemInstruction": {"parts": [{"text": sistema}]}, "contents": contents,
        "generationConfig": {"temperature": 0.4 if copiloto else 0.6, "maxOutputTokens": 16384 if copiloto else 8192},
    }).encode()
    try:
        result, modelo = generar(payload, api_key, modelo)
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
        from rutas.conversaciones import guardar_intercambio
        guardar_intercambio(conv, message, [a.nombre for a in adjuntos], answer)
        return jsonify(respuesta=answer, copiloto=copiloto, conversacion={"id": conv.id, "titulo": conv.titulo})
    return jsonify(respuesta=answer, copiloto=copiloto)
