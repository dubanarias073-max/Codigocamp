"""Moderación: cada vez que el escudo de CódigoCamp bloquea algo (archivo con virus, comando peligroso, enlace
malicioso, código dañino que se iba a ejecutar en el servidor) se registra un INCIDENTE con su gravedad y su
JUSTIFICACIÓN, se le envía un correo a la persona explicando qué se detectó y por qué es una infracción, y aparece en el
panel del administrador, que decide si ignorarlo, advertir otra vez o bloquear la cuenta. Nada se bloquea solo.

Gravedad (puntos de impacto):  baja 10 · media 30 · alta 60 · crítica 90
Si la persona reincide (3 o más incidentes en 7 días) la gravedad sube un nivel; con 6 o más, dos niveles.
El IMPACTO de una cuenta es la suma de puntos de sus incidentes de los últimos 30 días (máximo 100).

Correos: uno por cada infracción (con un tope de MAX_CORREOS_HORA por persona para que un script no llene su bandeja ni
haga que Gmail bloquee el remitente). El panel muestra si cada correo salió de verdad, falló o faltaba configurar SMTP.
"""
import html
from datetime import timedelta, timezone

from flask import current_app, has_request_context

NIVELES = ["baja", "media", "alta", "critica"]
PUNTOS = {"baja": 10, "media": 30, "alta": 60, "critica": 90}
ETIQUETAS = {"baja": "Baja", "media": "Media", "alta": "Alta", "critica": "Crítica"}
RECOMENDACION = {
    "baja": "Probablemente un error sin mala intención. Puedes ignorarlo.",
    "media": "Vigila la cuenta. Si se repite, adviértele.",
    "alta": "Acción claramente peligrosa. Recomendado: advertir y vigilar; bloquear si reincide.",
    "critica": "Intento malicioso (virus, robo de claves, control remoto, secuestro de datos, minería). Recomendado: bloquear.",
}
SIGNIFICA = {
    "baja": "Puede haber sido un error. No es grave, pero ten cuidado.",
    "media": "Es una acción riesgosa. Si se repite, tu cuenta puede ser bloqueada.",
    "alta": "Es una acción peligrosa. Una más y tu cuenta puede ser bloqueada.",
    "critica": "Es un intento de daño o de ataque. El administrador puede bloquear tu cuenta por esto.",
}
MAX_CORREOS_HORA = 20

# (palabras del motivo, gravedad): la primera que coincide manda
_REGLAS = {
    "archivo": [
        (("firma de un virus", "firma de virus", "antivirus encontró"), "critica"),
        (("bomba zip", "se infla"), "alta"),
        (("programa de windows", "programa de linux", "programa de macos", "programas compilados", "hay un programa"), "alta"),
        (("doble extensión", "invierte el texto"), "alta"),
        (("macros",), "media"),
        (("pueden instalar virus",), "media"),
        (("programa ",), "alta"),   # código malicioso dentro de un archivo de texto
    ],
    "comando": [
        (("control remoto", "contraseñas o claves", "minero", "copias de seguridad", "desactiva el antivirus", "oculto (codificado)", "ocultar rastros"), "critica"),
        (("borra el sistema", "todo el disco", "formatea", "sobre un disco", "bomba fork", "borra o formatea", "borra una unidad", "permisos de todo el sistema", "usuarios del equipo"), "alta"),
        (("carpetas del sistema", "script de internet", "enlace"), "media"),
        (("apaga o reinicia",), "baja"),
    ],
    "codigo": [
        (("control remoto", "criptomonedas", "contraseñas", "claves secretas", "secuestro", "minero", "copias de seguridad", "desactiva el antivirus"), "critica"),
        ((), "alta"),
    ],
    "enlace": [
        (("malware", "virus", "phishing", "suplant", "robar", "estafa"), "alta"),
        ((), "media"),
    ],
}

# Justificación: por qué cada cosa es una infracción (va en el correo y en el panel)
_POR_QUE = [
    ("archivo", ("firma de un virus", "firma de virus", "antivirus encontró"), "El archivo contiene un virus conocido. Si se guardara, podría infectar el servidor de CódigoCamp y los equipos de quienes lo descarguen (por ejemplo, tus amigos en el chat)."),
    ("archivo", ("bomba zip", "se infla"), "Es un comprimido hecho para inflarse hasta llenar el disco del servidor (bomba zip) y dejar la plataforma sin servicio."),
    ("archivo", ("doble extensión", "invierte el texto"), "El nombre del archivo disfraza un programa como si fuera una foto o un documento, un truco usado para engañar a las personas y hacerles ejecutar virus."),
    ("archivo", ("programa de", "programas compilados", "hay un programa", "pueden instalar virus"), "Es un programa ejecutable. CódigoCamp no permite subir programas porque pueden instalar virus en el equipo de quien los abra."),
    ("archivo", ("macros",), "Los documentos de Office con macros son una de las formas más usadas para esconder virus."),
    ("comando", ("control remoto",), "El comando le daría a otra persona el control remoto del equipo."),
    ("comando", ("contraseñas o claves",), "El comando intenta leer contraseñas o llaves privadas: es un intento de robo de información."),
    ("comando", ("desactiva el antivirus",), "Desactivar el antivirus o el firewall deja el equipo expuesto a ataques."),
    ("comando", ("copias de seguridad", "ocultar rastros"), "Borrar copias de seguridad o registros del sistema es típico de virus de secuestro de datos y de quien quiere ocultar un ataque."),
    ("comando", ("minero",), "Minar criptomonedas usa los recursos del equipo en beneficio de otra persona."),
    ("comando", ("oculto",), "Ejecutar comandos codificados es una técnica típica de virus para que nadie vea lo que hacen."),
    ("comando", ("borra", "formatea", "disco", "bomba fork", "permisos", "usuarios", "sistema"), "El comando puede destruir el sistema, borrar información o dejar el equipo sin funcionar."),
    ("comando", ("script de internet",), "Descargar y ejecutar al instante un script de un sitio desconocido es la forma más común de instalar virus."),
    ("comando", ("apaga o reinicia",), "Apagar o reiniciar el equipo desde CódigoCamp puede hacer perder el trabajo abierto."),
    ("enlace", (), "El enlace aparece en listas de sitios peligrosos (estafas, robo de contraseñas o descarga de virus). Abrirlo o compartirlo desde CódigoCamp pone en riesgo tu cuenta y la de otras personas."),
]
REGLA = "Los Términos y condiciones de CódigoCamp (sección 8, «Seguridad y sanciones») prohíben subir virus o programas maliciosos, ejecutar comandos o programas dañinos y usar enlaces peligrosos."


def clasificar(tipo, motivo):
    texto = (motivo or "").lower()
    for palabras, nivel in _REGLAS.get(tipo, []):
        if not palabras or any(p in texto for p in palabras):
            return nivel
    return "media"


def justificar(tipo, motivo):
    texto = (motivo or "").lower()
    for t, palabras, porque in _POR_QUE:
        if t == tipo and (not palabras or any(p in texto for p in palabras)):
            return porque
    return "La acción puede dañar CódigoCamp, a otros estudiantes o tu propio equipo."


def _subir(nivel, pasos):
    return NIVELES[min(len(NIVELES) - 1, NIVELES.index(nivel) + pasos)]


def impacto_de(usuario_id):
    from sqlalchemy import func

    from models import Incidente, db, utcnow
    total = db.session.query(func.coalesce(func.sum(Incidente.puntos), 0)).filter(
        Incidente.usuario_id == usuario_id, Incidente.creado_en >= utcnow() - timedelta(days=30), Incidente.estado != "ignorado").scalar()
    return min(100, int(total or 0))


def registrar(usuario, tipo, motivo, *, evidencia="", origen="", gravedad=None, explicacion=None):
    """Guarda el incidente, manda el correo con la justificación y lo deja pendiente en el panel. Nunca lanza ni impide
    que la ruta responda (el bloqueo ya ocurrió antes)."""
    try:
        return _registrar(usuario, tipo, motivo, evidencia, origen, gravedad, explicacion)
    except Exception as e:  # noqa: BLE001
        from models import db
        db.session.rollback()
        current_app.logger.warning("No se pudo registrar el incidente: %s", e)
        return None


def _registrar(usuario, tipo, motivo, evidencia, origen, gravedad, explicacion):
    from models import Incidente, db, utcnow
    from utilidades import client_ip
    if usuario is None or not getattr(usuario, "id", None):
        return None
    recientes = Incidente.query.filter(Incidente.usuario_id == usuario.id, Incidente.creado_en >= utcnow() - timedelta(days=7)).count()
    nivel = gravedad if gravedad in PUNTOS else clasificar(tipo, motivo)
    if recientes >= 6:
        nivel = _subir(nivel, 2)
    elif recientes >= 3:
        nivel = _subir(nivel, 1)
    inc = Incidente(usuario_id=usuario.id, tipo=tipo[:20], gravedad=nivel, puntos=PUNTOS[nivel], motivo=str(motivo or "")[:300],
                    explicacion=(explicacion or justificar(tipo, motivo))[:400], evidencia=str(evidencia or "")[:400],
                    origen=origen[:60], ip=(client_ip() if has_request_context() else "")[:45])
    db.session.add(inc)
    db.session.commit()
    enviados_hora = Incidente.query.filter(Incidente.usuario_id == usuario.id, Incidente.correo_estado.in_(("enviado", "sin_smtp", "pendiente")),
                                           Incidente.id != inc.id, Incidente.creado_en >= utcnow() - timedelta(hours=1)).count()
    if enviados_hora >= MAX_CORREOS_HORA:
        inc.correo_estado, inc.correo_detalle = "limite", f"No se envió: ya recibió {MAX_CORREOS_HORA} avisos en la última hora."
        db.session.commit()
    else:
        enviar_aviso(usuario, inc)
    return inc


def _guardar_estado(incidente_id):
    def guardar(estado, detalle):
        from models import Incidente, db
        inc = db.session.get(Incidente, incidente_id)
        if inc:
            inc.correo_estado, inc.correo_detalle = estado, (detalle or "")[:300]
            inc.correo_enviado = estado == "enviado"
            db.session.commit()
    return guardar


def enviar_aviso(usuario, inc, mensaje=None):
    """Correo de infracción con la justificación completa. El resultado (enviado / sin SMTP / error) se guarda en el incidente."""
    from servicios.correo import enviar
    asunto, cuerpo = correo_infraccion(usuario, inc, mensaje)
    inc.correo_estado = "pendiente"
    from models import db
    db.session.commit()
    enviar(usuario.email, asunto, cuerpo, al_terminar=_guardar_estado(inc.id))


def _desactivar(texto):
    """Los enlaces peligrosos van «desactivados» en el correo (hxxp://sitio[.]com) para que nadie los abra por error."""
    return texto.replace("http", "hxxp").replace(".", "[.]")


def _hora_local(usuario, momento):
    from zoneinfo import ZoneInfo

    from models import Profile
    p = Profile.query.filter_by(usuario_id=usuario.id).first()
    try:
        zona = ZoneInfo((p.zona_horaria if p and p.zona_horaria else None) or "America/Bogota")
    except Exception:  # noqa: BLE001
        zona = ZoneInfo("America/Bogota")
    m = momento if momento.tzinfo else momento.replace(tzinfo=timezone.utc)
    return m.astimezone(zona).strftime("%d/%m/%Y a las %I:%M %p")


ACCION = {"archivo": "subir un archivo peligroso", "comando": "ejecutar un comando peligroso", "enlace": "usar un enlace peligroso",
          "codigo": "ejecutar un programa dañino en el servidor", "manual": "incumplir las normas de CódigoCamp"}
QUE_ES = {"archivo": "Archivo", "comando": "Comando", "enlace": "Enlace", "codigo": "Código"}


def correo_infraccion(usuario, inc=None, mensaje=None):
    """(asunto, html). Siempre incluye: qué se detectó, dónde y cuándo, POR QUÉ es una infracción, la gravedad y qué pasa ahora."""
    from servicios.correo import _config, plantilla
    e = html.escape
    nombre = e((usuario.nombre or "").split(" ")[0] or "hola")
    if inc is None or inc.tipo == "manual":
        parrafos = [f"Hola {nombre}, el administrador de CódigoCamp te envía una <b>advertencia</b> por incumplir las normas de la plataforma."]
        texto = mensaje or (inc.motivo if inc else "")
        if texto:
            parrafos.append(f"<b>Motivo de la advertencia:</b> {e(texto)}")
        if inc:
            parrafos.append(f"<b>Gravedad:</b> {ETIQUETAS[inc.gravedad]}. {SIGNIFICA[inc.gravedad]}")
        parrafos.append(f"<b>Norma que se incumplió:</b> {REGLA} También prohíben el acoso, los insultos, el spam y hacerse pasar por otra persona.")
    else:
        cuando = _hora_local(usuario, inc.creado_en)
        evid = inc.evidencia
        if inc.tipo == "enlace":
            evid = _desactivar(evid)
        parrafos = [
            f"Hola {nombre}, el sistema de seguridad de CódigoCamp <b>bloqueó</b> un intento de <b>{ACCION.get(inc.tipo, 'acción peligrosa')}</b> desde tu cuenta.",
            f"<b>Qué detectamos:</b> {e(inc.motivo[:1].upper() + inc.motivo[1:])}.",
            f"<b>Dónde y cuándo:</b> {e(inc.origen or 'CódigoCamp')}, el {cuando} (IP {e(inc.ip or 'desconocida')}).",
        ]
        if evid:
            parrafos.append(f'<b>{QUE_ES.get(inc.tipo, "Detalle")}:</b><br><code style="display:block;margin-top:6px;padding:10px 12px;border-radius:8px;'
                            f'background:#070b16;color:#ffd0da;font-family:Consolas,monospace;font-size:13px;white-space:pre-wrap;word-break:break-all">{e(evid[:300])}</code>')
        parrafos += [
            f"<b>Por qué es una infracción:</b> {e(inc.explicacion or justificar(inc.tipo, inc.motivo))} {REGLA}",
            f"<b>Gravedad:</b> {ETIQUETAS[inc.gravedad]}. {SIGNIFICA[inc.gravedad]}",
            "<b>Qué pasa ahora:</b> la acción se bloqueó y no causó ningún daño. El administrador de CódigoCamp revisará lo ocurrido y decidirá si "
            "tu cuenta sigue activa o se bloquea.",
        ]
        if mensaje:
            parrafos.append(f"<b>Mensaje del administrador:</b> «{e(mensaje)}»")
    parrafos.append("¿Fue un error (por ejemplo, un archivo de una tarea o un ejemplo de clase)? <b>Responde a este correo explicando qué pasó</b> "
                    "y el administrador lo tendrá en cuenta.")
    url = _config(current_app)["url"]
    asunto = f"⚠️ Infracción de seguridad en tu cuenta de CódigoCamp ({ETIQUETAS[inc.gravedad]})" if inc else "⚠️ Advertencia del administrador de CódigoCamp"
    return asunto, plantilla("Aviso de infracción", parrafos, ("Leer las normas de CódigoCamp", f"{url}/pages/terminos.html"),
                             pie="Este es un aviso de seguridad obligatorio de tu cuenta de CódigoCamp: no se puede desactivar.",
                             animo="preocupado", etiqueta="seguridad.log", frase="Ojo con eso… 🛡️")


def correo_bloqueo(usuario, motivo, incidente=None):
    from servicios.correo import enviar, plantilla
    e = html.escape
    nombre = e((usuario.nombre or "").split(" ")[0] or "hola")
    parrafos = [f"Hola {nombre}, tu cuenta de CódigoCamp fue <b>bloqueada</b> por incumplir las normas de la plataforma. Tus sesiones se cerraron en todos tus dispositivos."]
    parrafos.append(f"<b>Motivo del bloqueo:</b> {e(motivo or 'incumplimiento de las normas de seguridad')}")
    if incidente is not None and incidente.tipo != "manual":
        parrafos.append(f"<b>Infracción que lo causó:</b> {e(incidente.motivo)} ({ETIQUETAS[incidente.gravedad].lower()}), el {_hora_local(usuario, incidente.creado_en)}.")
        parrafos.append(f"<b>Por qué es una infracción:</b> {e(incidente.explicacion or justificar(incidente.tipo, incidente.motivo))}")
    parrafos.append(f"<b>Norma incumplida:</b> {REGLA}")
    parrafos.append("Si crees que es un error, <b>responde a este correo</b> explicando lo que pasó para pedir una revisión.")
    return bool(enviar(usuario.email, "⛔ Tu cuenta de CódigoCamp fue bloqueada", plantilla(
        "Cuenta bloqueada", parrafos, pie="Aviso de seguridad obligatorio de tu cuenta de CódigoCamp.", animo="triste", etiqueta="cuenta.log", frase="")))


def frenar_codigo(codigo=None, archivos=None, *, origen, comando=None):
    """Para las rutas que EJECUTAN código en el servidor: si el programa (o la orden) es dañino, registra la infracción
    (correo + panel) y devuelve la respuesta de error lista; si está bien, None."""
    from flask_login import current_user

    from servicios.codigo_malicioso import revisar_proyecto
    from servicios.comandos_peligrosos import revisar_comando
    from utilidades import api_error
    if comando:
        motivo = revisar_comando(comando)
        if motivo:
            registrar(current_user, "comando", motivo, evidencia=comando[:400], origen=origen)
            return api_error(f"🛡️ CódigoCamp bloqueó esta orden porque {motivo}. Te enviamos un correo con el detalle.", 403)
    h = revisar_proyecto(codigo, archivos)
    if not h:
        return None
    evid = (f"{h['archivo']}: " if h.get("archivo") else "") + (h.get("fragmento") or "")
    registrar(current_user, "codigo", h["motivo"], evidencia=evid, origen=origen, gravedad=h["gravedad"], explicacion=h["explicacion"])
    return api_error(f"🛡️ CódigoCamp no ejecutó tu programa porque {h['motivo']}{' (en ' + h['archivo'] + ')' if h.get('archivo') else ''}. "
                     "Te enviamos un correo con el detalle.", 403)
