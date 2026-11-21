"""Correos de CódigoCamp: alertas de seguridad (nuevo dispositivo, cambio de contraseña) y recordatorio de racha.

backend/.env:
  MAIL_SERVER=smtp.gmail.com     MAIL_PORT=587     MAIL_TLS=1      (MAIL_SSL=1 para el puerto 465)
  MAIL_USER=tucorreo@gmail.com   MAIL_PASSWORD=<contraseña de aplicación>   MAIL_FROM="CódigoCamp <tucorreo@gmail.com>"
  APP_URL=http://localhost:5000,https://tu-tunel   (enlaces de los correos; varias separadas por coma)
Sin MAIL_SERVER los correos no se envían: se guardan como .eml en ALMACEN_ARCHIVOS/correos/ (para verlos en desarrollo).
Se envían en segundo plano: una petición nunca espera al servidor de correo.
"""
import hashlib
import html
import os
import re
import smtplib
import ssl
import threading
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid, parseaddr
from pathlib import Path

from flask import current_app

from utilidades import direccion_actual, direcciones

COLOR = "#267e86"


def _env(app, *nombres, defecto=""):
    """Primer valor definido entre varios nombres (MAIL_* o SMTP_*, como en otros proyectos)."""
    for n in nombres:
        v = app.config.get(n) or os.getenv(n)
        if v not in (None, ""):
            return str(v).strip()
    return defecto


def _config(app):
    usuario = _env(app, "MAIL_USER", "MAIL_USERNAME", "SMTP_USER", "SMTP_USERNAME", "EMAIL_USER")
    servidor = _env(app, "MAIL_SERVER", "SMTP_SERVER", "SMTP_HOST", "MAIL_HOST", "EMAIL_HOST")
    if not servidor and usuario:   # con solo el usuario y la clave se deduce el servidor de los correos más comunes
        dominio = usuario.rsplit("@", 1)[-1].lower()
        servidor = {"gmail.com": "smtp.gmail.com", "outlook.com": "smtp-mail.outlook.com", "hotmail.com": "smtp-mail.outlook.com",
                    "live.com": "smtp-mail.outlook.com", "yahoo.com": "smtp.mail.yahoo.com", "yahoo.es": "smtp.mail.yahoo.com"}.get(dominio, "")
    puerto = int(_env(app, "MAIL_PORT", "SMTP_PORT", "EMAIL_PORT", defecto="587") or 587)
    ssl_ = _env(app, "MAIL_SSL", "SMTP_SSL", "MAIL_USE_SSL", defecto="1" if puerto == 465 else "0").lower() in ("1", "true", "si", "sí", "yes")
    tls = _env(app, "MAIL_TLS", "SMTP_TLS", "MAIL_USE_TLS", defecto="1").lower() in ("1", "true", "si", "sí", "yes")
    # Las contraseñas de aplicación de Gmail se copian con espacios («abcd efgh ijkl mnop»): se quitan.
    clave = _env(app, "MAIL_PASSWORD", "SMTP_PASSWORD", "SMTP_APP_PASSWORD", "EMAIL_PASSWORD").replace(" ", "")
    de = _env(app, "MAIL_FROM", "SMTP_FROM", "MAIL_DEFAULT_SENDER", "EMAIL_FROM")
    return {
        "servidor": servidor, "puerto": puerto, "tls": tls and not ssl_, "ssl": ssl_, "usuario": usuario, "clave": clave,
        "de": formataddr(("CódigoCamp", de)) if de and "<" not in de else (de or formataddr(("CódigoCamp", usuario or "no-responder@codigocamp.local"))),
        # APP_URL puede tener varias direcciones separadas por coma (localhost y el túnel): se usa la de esta visita.
        "url": direccion_actual(direcciones(_env(app, "APP_URL")) or ["http://127.0.0.1:5000"]),
    }


def plantilla(titulo, parrafos, boton=None, pie=""):
    """HTML sencillo y compatible con los clientes de correo (tablas y estilos en línea)."""
    cuerpo = "".join(f'<p style="margin:0 0 14px;font-size:15px;line-height:1.55;color:#2b3338">{p}</p>' for p in parrafos)
    if boton:
        cuerpo += (f'<p style="margin:22px 0"><a href="{html.escape(boton[1])}" style="background:{COLOR};color:#fff;text-decoration:none;'
                   f'padding:12px 22px;border-radius:10px;font-weight:700;display:inline-block">{html.escape(boton[0])}</a></p>')
    return f"""<!doctype html><html lang="es"><body style="margin:0;background:#f4f2eb;font-family:Segoe UI,Arial,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2eb;padding:28px 12px"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fffefa;border:1px solid #d9d5c9;border-radius:16px">
<tr><td style="padding:22px 28px;border-bottom:1px solid #ece9df;font-weight:800;font-size:18px;color:{COLOR}">&lt;/&gt; codigocamp</td></tr>
<tr><td style="padding:26px 28px"><h1 style="margin:0 0 16px;font-size:21px;color:#1f262c">{html.escape(titulo)}</h1>{cuerpo}</td></tr>
<tr><td style="padding:16px 28px;border-top:1px solid #ece9df;font-size:12px;color:#737a7e">{pie or "Recibes este correo por tu cuenta de CódigoCamp. Puedes elegir qué correos recibir en Configuración → Correos."}</td></tr>
</table></td></tr></table></body></html>"""


def _a_texto(h):
    t = re.sub(r"<(br|/p|/h1|/tr)[^>]*>", "\n", h)
    t = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>([^<]+)</a>', r"\2: \1", t)
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def _enviar_ya(cfg, mensaje, carpeta):
    if not cfg["servidor"]:
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / f"{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}.eml").write_bytes(bytes(mensaje))
        return
    contexto = ssl.create_default_context()
    if cfg["ssl"]:
        servidor = smtplib.SMTP_SSL(cfg["servidor"], cfg["puerto"], context=contexto, timeout=20)
    else:
        servidor = smtplib.SMTP(cfg["servidor"], cfg["puerto"], timeout=20)
        if cfg["tls"]:
            servidor.starttls(context=contexto)
    with servidor:
        if cfg["usuario"]:
            servidor.login(cfg["usuario"], cfg["clave"])
        servidor.send_message(mensaje)


def enviar(para, asunto, html_cuerpo, *, esperar=False):
    """Envía un correo (en segundo plano salvo esperar=True). Nunca lanza: los fallos quedan en el log."""
    app = current_app._get_current_object()
    cfg = _config(app)
    m = EmailMessage()
    m["Subject"] = asunto
    m["From"] = cfg["de"]
    m["To"] = para
    # Cabeceras que miran los filtros de spam: fecha, Message-ID con el dominio real del remitente y cómo darse de baja.
    remitente = parseaddr(cfg["de"])[1] or cfg["usuario"]
    dominio = remitente.rsplit("@", 1)[-1] if "@" in remitente else "localhost"
    m["Date"] = formatdate(localtime=True)
    m["Message-ID"] = make_msgid(domain=dominio)
    if remitente:
        m["Reply-To"] = remitente
        m["List-Unsubscribe"] = f"<mailto:{remitente}?subject=Baja%20de%20avisos>, <{cfg['url']}/pages/configuracion.html#correos>"
    m.set_content(_a_texto(html_cuerpo))
    m.add_alternative(html_cuerpo, subtype="html")
    carpeta = Path(app.config.get("ALMACEN_ARCHIVOS") or "almacen_archivos") / "correos"
    enviados = app.extensions.setdefault("correos_enviados", [])
    if app.config.get("TESTING"):
        enviados.append({"para": para, "asunto": asunto, "html": html_cuerpo})
        return True

    def tarea():
        try:
            _enviar_ya(cfg, m, carpeta)
        except Exception as e:  # noqa: BLE001
            app.logger.warning("No se pudo enviar el correo «%s» a %s: %s", asunto, para, e)

    if esperar:
        tarea()
    else:
        threading.Thread(target=tarea, daemon=True).start()
    return True


# ------------------------------------------------------------------------- dispositivos ----
_NAVEGADORES = [("Edg/", "Edge"), ("OPR/", "Opera"), ("SamsungBrowser", "Samsung Internet"), ("Firefox/", "Firefox"), ("CriOS", "Chrome"), ("Chrome/", "Chrome"), ("Safari/", "Safari")]
_SISTEMAS = [("Windows", "Windows"), ("Android", "Android"), ("iPhone", "iPhone"), ("iPad", "iPad"), ("Mac OS X", "macOS"), ("CrOS", "ChromeOS"), ("Linux", "Linux")]


def describir_dispositivo(agente):
    agente = agente or ""
    nav = next((n for k, n in _NAVEGADORES if k in agente), "Navegador")
    so = next((n for k, n in _SISTEMAS if k in agente), "otro sistema")
    return f"{nav} en {so}"


def huella_dispositivo(agente, ip):
    """Mismo navegador y sistema desde la misma red (/24 o /48) = mismo dispositivo. No identifica a la persona."""
    return huella_de(describir_dispositivo(agente), ip)


def huella_de(descripcion, ip):
    """Huella a partir de la descripción ya guardada («Chrome en Android») y la IP (la usa cerrar sesión)."""
    red = ip or ""
    if ":" in red:
        red = ":".join(red.split(":")[:3])
    else:
        red = ".".join(red.split(".")[:3])
    return hashlib.sha256(f"{descripcion}|{red}".encode()).hexdigest()


def olvidar_dispositivos(usuario_id, *, sesiones=None):
    """Tras «cerrar sesión en este dispositivo / en ese / en todos»: esos dispositivos dejan de ser conocidos,
    así al volver a entrar llega el correo «Nuevo inicio de sesión». sesiones=None → todos los de la persona."""
    from models import KnownDevice, db
    q = KnownDevice.query.filter_by(usuario_id=usuario_id)
    if sesiones is not None:
        huellas = {huella_de(x.dispositivo or "", x.ip) for x in sesiones}
        if not huellas:
            return 0
        q = q.filter(KnownDevice.huella.in_(list(huellas)))
    n = q.delete(synchronize_session=False)
    db.session.commit()
    return n


def ajustes_de(usuario):
    from models import EmailSettings, db
    a = db.session.get(EmailSettings, usuario.id)
    if a is None:
        a = EmailSettings(usuario_id=usuario.id, seguridad=True, racha=True, novedades=False)
        db.session.add(a)
    return a


def _cuando(usuario, momento):
    """«21/11/2026 07:43 (-05)»: la hora en la zona horaria de la persona (la detecta su dispositivo)."""
    from servicios.zona import zona
    local = momento.astimezone(zona(getattr(usuario, "profile", None)))
    return f"{local:%d/%m/%Y %H:%M} ({local.tzname()})"


def bienvenida(usuario, agente, ip, metodo="contraseña"):
    """Correo al crear la cuenta (siempre, aunque sea el primer dispositivo): confirma el registro y desde dónde."""
    cfg = _config(current_app)
    ahora = datetime.now(timezone.utc)
    nombre = html.escape(usuario.nombre.split(" ")[0])
    enviar(usuario.email, "¡Bienvenido a CódigoCamp! Tu cuenta está lista", plantilla(
        f"¡Hola {usuario.nombre.split(' ')[0]}, tu cuenta está lista!",
        [f"Te registraste en CódigoCamp con <b>{html.escape(usuario.email)}</b>.",
         f"Dispositivo: <b>{html.escape(describir_dispositivo(agente))}</b><br>IP {html.escape(ip or 'desconocida')} · {_cuando(usuario, ahora)} · con {html.escape(metodo)}",
         "Practica unos minutos cada día para mantener tu 🔥 racha: te avisaremos por correo si estás a punto de perderla.",
         f"{nombre}, <b>si no fuiste tú</b> quien creó esta cuenta, escríbenos o cambia la contraseña desde Configuración → Seguridad."],
        ("Empezar a aprender", f"{cfg['url']}/pages/inicio.html"),
    ))
    return True


def registrar_inicio(usuario, agente, ip, *, metodo="contraseña", nuevo_usuario=False):
    """Guarda el dispositivo. En el registro envía la bienvenida; después avisa de cada dispositivo nuevo."""
    from models import KnownDevice, db
    ahora = datetime.now(timezone.utc)
    huella = huella_dispositivo(agente, ip)
    d = KnownDevice.query.filter_by(usuario_id=usuario.id, huella=huella).first()
    if d:
        d.ultimo, d.ip = ahora, (ip or "")[:45]
        db.session.commit()
        return False
    # «Primer dispositivo» = la primera vez que la cuenta inicia sesión (no «no quedan dispositivos conocidos»,
    # que pasa también después de «cerrar sesión en todos»: ahí SÍ debe llegar el correo).
    from models import UserSession
    primero = UserSession.query.filter_by(usuario_id=usuario.id).count() <= 1
    db.session.add(KnownDevice(usuario_id=usuario.id, huella=huella, nombre=describir_dispositivo(agente)[:120], ip=(ip or "")[:45], primero=ahora, ultimo=ahora))
    ajustes = ajustes_de(usuario)
    db.session.commit()
    if nuevo_usuario:
        bienvenida(usuario, agente, ip, metodo)
        return True
    if primero or not ajustes.seguridad:
        return False
    cfg = _config(current_app)
    nombre = html.escape(usuario.nombre.split(" ")[0])
    enviar(usuario.email, "Nuevo inicio de sesión en tu cuenta de CódigoCamp", plantilla(
        "Nuevo inicio de sesión",
        [f"Hola {nombre}, alguien inició sesión en tu cuenta desde un dispositivo nuevo:",
         f"<b>{html.escape(describir_dispositivo(agente))}</b><br>IP {html.escape(ip or 'desconocida')} · {_cuando(usuario, ahora)} · con {html.escape(metodo)}",
         "Si fuiste tú, no tienes que hacer nada.",
         "<b>Si no fuiste tú</b>, cambia tu contraseña ahora: así se cierra el acceso de quien la tenga."],
        ("Cambiar mi contraseña", f"{cfg['url']}/pages/configuracion.html#seguridad"),
    ))
    return True


def enlace_restablecer(usuario, enlace, agente, ip, minutos):
    """«¿Olvidaste tu contraseña?»: siempre se envía (es una petición de la persona, no un aviso opcional)."""
    primer = html.escape(usuario.nombre.split(" ")[0])
    sin_clave = " Entras con Google: con este enlace también puedes crear una contraseña para entrar con tu correo." if usuario.google_id else ""
    enviar(usuario.email, "Restablece tu contraseña de CódigoCamp", plantilla(
        "Restablece tu contraseña",
        [f"Hola {primer}, alguien (ojalá tú) pidió cambiar la contraseña de <b>{html.escape(usuario.email)}</b>.{sin_clave}",
         f"El enlace sirve <b>una sola vez</b> y vence en <b>{minutos} minutos</b>.",
         f"Pedido desde <b>{html.escape(describir_dispositivo(agente))}</b> (IP {html.escape(ip or 'desconocida')}).",
         "Si no fuiste tú, ignora este correo: tu contraseña no cambia y nadie puede entrar sin este enlace."],
        ("Crear nueva contraseña", enlace),
        pie="Por seguridad, nunca te pediremos tu contraseña por correo.",
    ))
    return True


def avisar_cambio_clave(usuario, agente, ip):
    if not ajustes_de(usuario).seguridad:
        return False
    cfg = _config(current_app)
    ahora = datetime.now(timezone.utc)
    enviar(usuario.email, "Tu contraseña de CódigoCamp cambió", plantilla(
        "Tu contraseña cambió",
        [f"Hola {html.escape(usuario.nombre.split(' ')[0])}, la contraseña de tu cuenta se cambió el {ahora:%d/%m/%Y a las %H:%M} UTC desde <b>{html.escape(describir_dispositivo(agente))}</b> (IP {html.escape(ip or 'desconocida')}).",
         "Si fuiste tú, todo está bien.",
         "<b>Si no fuiste tú</b>, entra con Google o escríbenos de inmediato: alguien más podría tener acceso a tu correo."],
        ("Revisar mi cuenta", f"{cfg['url']}/pages/configuracion.html#seguridad"),
    ))
    return True


def recordar_rachas(hoy=None, nivel=None):
    """Avisa a quien tiene racha y aún no practicó hoy de que la perderá a medianoche (SU medianoche: la hora de cada
    persona sale de la zona horaria de su dispositivo). nivel 1 = aviso de la tarde (RECORDATORIO_HORA, 18 h);
    nivel 2 = «última oportunidad» (RECORDATORIO_HORA_FINAL, 21 h). Sin nivel, se elige por la hora local de cada uno.
    Cada nivel se envía una sola vez al día. Flask lo ejecuta solo (iniciar_programador); también: flask --app app recordar-rachas."""
    from models import EmailSettings, Profile, User, db
    from servicios.zona import ahora_de
    hora1 = int(os.getenv("RECORDATORIO_HORA", "18"))
    hora2 = int(os.getenv("RECORDATORIO_HORA_FINAL", "21"))
    cfg = _config(current_app)
    enviados = 0
    consulta = (db.session.query(User, Profile).join(Profile, Profile.usuario_id == User.id)
                .filter(User.activo.is_(True), Profile.racha_actual > 0, Profile.ultima_actividad.isnot(None)))
    for usuario, perfil in consulta:
        ahora = ahora_de(perfil)
        hoy_u = hoy or ahora.date()
        # Con una fecha dada (comando o pruebas) y sin nivel, es el aviso de la tarde.
        nivel_u = nivel or (1 if hoy else 2 if ahora.hour >= hora2 else 1 if ahora.hour >= hora1 else 0)
        if not nivel_u or perfil.ultima_actividad >= hoy_u:
            continue
        if (hoy_u - perfil.ultima_actividad).days != 1:
            continue  # la racha ya se perdió (o se salvará con un salvarrachas): no se insiste
        ajustes = db.session.get(EmailSettings, usuario.id) or ajustes_de(usuario)
        ya = (ajustes.nivel_recordatorio or 1) if ajustes.ultimo_recordatorio == hoy_u else 0
        if not ajustes.racha or ya >= nivel_u:
            continue
        ajustes.ultimo_recordatorio, ajustes.nivel_recordatorio = hoy_u, nivel_u
        n = perfil.racha_actual
        dias = f"{n} día{'s' if n != 1 else ''}"
        primer = html.escape(usuario.nombre.split(" ")[0])
        salvar = (f"Tienes {perfil.salvarrachas} salvarrachas: si no entras hoy se gastará uno, pero mejor no arriesgarse."
                  if perfil.salvarrachas else "No tienes salvarrachas: si hoy no practicas, tu racha vuelve a 0.")
        if nivel_u >= 2:
            asunto = f"Últimas horas: tu racha de {dias} se pierde a medianoche"
            titulo = f"¡Tu racha de {dias} está a punto de apagarse!"
            parrafos = [f"{primer}, hoy no has entrado a CódigoCamp y <b>a medianoche perderás tu racha de {dias}</b>.",
                        f"Solo necesitas una lección o un reto ({perfil.meta_minutos} minutos) para salvarla.", salvar]
        else:
            asunto = f"{usuario.nombre.split(' ')[0]}, si no entras hoy perderás tu racha de {dias}"
            titulo = f"No pierdas tu racha de {dias}"
            parrafos = [f"Hola {primer}, hoy todavía no practicaste. <b>Si se te olvida entrar, perderás tu racha de {dias}.</b>",
                        f"Te bastan {perfil.meta_minutos} minutos: una lección o un reto y tu racha sigue viva.", salvar]
        enviar(usuario.email, asunto, plantilla(titulo, parrafos, ("Salvar mi racha", f"{cfg['url']}/pages/inicio.html"),
                                                pie="Puedes desactivar estos avisos en Configuración → Correos."))
        enviados += 1
    db.session.commit()
    return enviados


# ------------------------------------------------------------------ programador automático ----
def iniciar_programador(app):
    """Hilo que envía los avisos de racha sin cron: nivel 1 a las RECORDATORIO_HORA (18 por defecto) y nivel 2 a las
    RECORDATORIO_HORA_FINAL (21), en la hora local de CADA persona (zona horaria de su dispositivo). RECORDATORIOS_AUTO=0 lo desactiva. Si corren varios procesos,
    cada aviso se envía igual una sola vez porque se marca en ajustes_correo."""
    if app.config.get("TESTING") or os.getenv("RECORDATORIOS_AUTO", "1") != "1":
        return None
    if app.debug and os.getenv("WERKZEUG_RUN_MAIN") not in (None, "true"):
        return None
    parar = threading.Event()

    def bucle():
        while not parar.wait(300):          # revisa cada 5 minutos
            try:
                with app.app_context():
                    n = recordar_rachas()   # cada persona según la hora de SU zona horaria
                    if n:
                        app.logger.info("Avisos de racha enviados: %s", n)
            except Exception as e:  # noqa: BLE001 - p. ej. MySQL apagado; se reintenta en 5 minutos
                app.logger.warning("No se pudieron enviar los avisos de racha: %s", e)

    hilo = threading.Thread(target=bucle, name="avisos-racha", daemon=True)
    hilo.start()
    app.extensions["programador_correos"] = parar
    return hilo
