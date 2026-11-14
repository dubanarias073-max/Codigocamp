"""Tutor de IA: envía la pregunta a Gemini y devuelve la respuesta."""
import json
import urllib.request
from datetime import timedelta

from flask import Blueprint, current_app, jsonify
from flask_login import current_user

from models import TutorUsage, db, utcnow
from servicios.perfil import get_profile
from utilidades import api_error, client_ip, json_body

bp = Blueprint("tutor", __name__)


@bp.post("/api/tutor/")
def tutor():
    data = json_body()
    if isinstance(data, tuple):
        return data
    message = str(data.get("mensaje", "")).strip()
    if not message or len(message) > 3500:
        return api_error("Escribe una pregunta de hasta 3500 caracteres.")
    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key:
        return api_error("El tutor todavía no está configurado.", 503)
    now = utcnow()
    since = now - timedelta(minutes=1)
    if current_user.is_authenticated:
        used = TutorUsage.query.filter(TutorUsage.usuario_id == current_user.id, TutorUsage.creado_en >= since).count()
        maximum = 20
    else:
        used = TutorUsage.query.filter(
            TutorUsage.usuario_id.is_(None), TutorUsage.ip == client_ip(), TutorUsage.creado_en >= since,
        ).count()
        maximum = 6
    if used >= maximum:
        return api_error("Has hecho muchas preguntas seguidas. Espera un minuto.", 429)
    db.session.add(TutorUsage(usuario_id=current_user.id if current_user.is_authenticated else None, ip=client_ip()))
    db.session.commit()
    history = data.get("historial") if isinstance(data.get("historial"), list) else []
    contents = [{
        "role": "model" if item.get("rol") == "tutor" else "user",
        "parts": [{"text": str(item.get("texto", ""))[:3500]}],
    } for item in history[-10:] if isinstance(item, dict)]
    contents.append({"role": "user", "parts": [{"text": message}]})
    perfil_tutor = get_profile(current_user) if current_user.is_authenticated else None
    contexto = ""
    if perfil_tutor:
        niveles = {"cero": "empieza desde cero", "probado": "ha probado algo", "basico": "sabe lo básico", "avanzado": "tiene experiencia"}
        partes = [f"Se llama {current_user.nombre.split()[0]}."]
        if perfil_tutor.curso_actual:
            partes.append(f"Estudia {perfil_tutor.curso_actual.nombre} en CódigoCamp.")
        if perfil_tutor.nivel_previo in niveles:
            partes.append(f"Su nivel: {niveles[perfil_tutor.nivel_previo]}.")
        contexto = " Datos del alumno: " + " ".join(partes) + " Adapta la explicación a su nivel y usa ejemplos de su curso cuando sea posible."
    system_prompt = (
        "Eres el tutor de CódigoCamp. Responde siempre en español, con frases cortas y amables. "
        "Explica código, corrige errores con su causa y propone un ejercicio pequeño. Ayudas con HTML, CSS, "
        "JavaScript, TypeScript, Python, Java, C, C++, C#, PHP, SQL, Go, Rust, Swift, Kotlin, Ruby y bases de datos. "
        "Si la pregunta no es sobre programación, explica que solo puedes ayudar con eso. No des la solución completa "
        "de un reto sin antes ofrecer una pista. Formato: usa bloques de código con ``` y el nombre del lenguaje, "
        "listas cortas con guiones y evita tablas y títulos largos. Si el alumno quiere hablar con otras personas, "
        "recuérdale que puede agregar amigos en la sección Chats." + contexto
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_app.config['GEMINI_MODEL']}:generateContent"
    payload = json.dumps({"systemInstruction": {"parts": [{"text": system_prompt}]}, "contents": contents,
                          "generationConfig": {"temperature": 0.6, "maxOutputTokens": 1500}}).encode()
    outbound = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    try:
        with urllib.request.urlopen(outbound, timeout=30) as response:
            result = json.load(response)
        answer = "".join(part.get("text", "") for part in result["candidates"][0]["content"]["parts"]).strip()
        if not answer:
            raise ValueError("respuesta vacía")
    except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError):
        current_app.logger.exception("No se pudo completar la solicitud al tutor de IA.")
        return api_error("El tutor no pudo responder ahora. Inténtalo de nuevo.", 502)
    return jsonify(respuesta=answer)
