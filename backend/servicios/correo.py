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


def _url_sitio():
    try:
        return _config(current_app._get_current_object())["url"].rstrip("/")
    except Exception:   # sin aplicación (pruebas sueltas)
        return ""


FRASES_CODI = {
    "saludo": "¡Hola! Soy Codi, tu compañero de código 👋", "feliz": "¡Todo en orden por aquí!", "celebra": "¡Lo lograste! 🎉",
    "fuego": "¡Estás en llamas! 🔥", "pensando": "Mmm… déjame revisar esto", "preocupado": "Tu racha te está esperando…",
    "alarma": "¡Corre, tu racha está en peligro!", "triste": "Te extrañé… ¿volvemos?", "dormido": "Zzz… despiértame con una lección",
}


def plantilla(titulo, parrafos, boton=None, pie="", mascota=None, animo="feliz", etiqueta=None, frase=None):
    """Correo con el diseño de CódigoCamp: cabecera oscura con el logo, Codi ANIMADO (GIF: se mueve en Gmail, Outlook y
    el celular) con su globo de diálogo, una «ventana de código» con el mensaje y botón en degradado.
    HTML con tablas y estilos en línea para que se vea bien en todos los clientes de correo."""
    url = _url_sitio()
    if mascota is None and url:
        mascota = f"{url}/img/codi/anim/{animo}.gif"   # GIF animado (frontend/img/codi/anim/); el PNG queda de respaldo
    frase = frase if frase is not None else FRASES_CODI.get(animo, "")
    cuerpo = "".join(f'<p style="margin:0 0 14px;font-size:15px;line-height:1.6;color:#d6def5">{p}</p>' for p in parrafos)
    if boton:
        cuerpo += (f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:24px 0 6px"><tr><td style="border-radius:12px;'
                   f'background:#a3e635;background-image:linear-gradient(135deg,#22d3ee,#a3e635)">'
                   f'<a href="{html.escape(boton[1])}" style="display:inline-block;padding:14px 26px;font-weight:800;font-size:15px;'
                   f'color:#06100f;text-decoration:none;border-radius:12px">{html.escape(boton[0])} &rarr;</a></td></tr></table>')
    logo = (f'<img src="{html.escape(url)}/img/logo-icon.png" width="30" height="30" alt="" style="vertical-align:middle;border:0;margin-right:8px">'
            if url else "")
    img = (f'<img src="{html.escape(mascota)}" width="150" height="150" alt="Codi, la mascota de CódigoCamp" '
           f'style="display:block;width:150px;height:150px;margin:0 auto;border:0">' if mascota else "")
    globo = (f'<td valign="middle" style="padding:0 0 0 4px"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="background:#1b2440;'
             f'border:1px solid #2f3f6b;border-radius:16px 16px 16px 4px;padding:12px 16px;font-size:14px;font-weight:700;line-height:1.4;color:#e2e8f0;'
             f'max-width:240px">{html.escape(frase)}</td></tr></table></td>') if frase and img else ""
    codi = (f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td valign="bottom">{img}</td>{globo}</tr></table>'
            if img else "")
    archivo = html.escape(etiqueta or "mensaje.js")
    return f"""<!doctype html><html lang="es"><head><meta name="color-scheme" content="dark light"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#070b16;font-family:'Segoe UI',Roboto,Arial,sans-serif">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#070b16;background-image:radial-gradient(circle at 50% 0,#1e1b4b,#070b16 60%);padding:26px 12px"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:580px">
<tr><td style="padding:4px 6px 18px;font-family:Consolas,'Courier New',monospace;font-weight:800;font-size:20px;color:#5ef2ff">{logo}codigocamp</td></tr>
<tr><td align="center" style="padding:0 0 4px">{codi}</td></tr>
<tr><td style="background:#0e1426;border:1px solid #243154;border-radius:18px;overflow:hidden">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td style="padding:11px 16px;background:#0a0f1e;border-bottom:1px solid #243154;font-family:Consolas,monospace;font-size:12px;color:#8ea0c9">
    <span style="color:#ff5f57">&#9679;</span> <span style="color:#febc2e">&#9679;</span> <span style="color:#28c840">&#9679;</span>
    &nbsp;&nbsp;<span style="background:#1b2440;color:#a3e635;padding:3px 9px;border-radius:6px">{archivo}</span></td></tr>
  <tr><td style="padding:26px 28px 24px">
    <p style="margin:0 0 6px;font-family:Consolas,monospace;font-size:13px;color:#64748b">// CódigoCamp</p>
    <h1 style="margin:0 0 16px;font-size:22px;line-height:1.3;color:#ffffff">{html.escape(titulo)}</h1>
    {cuerpo}
  </td></tr>
  </table></td></tr>
<tr><td style="padding:18px 8px;font-size:12px;line-height:1.5;color:#7c89ad;text-align:center">{pie or "Recibes este correo por tu cuenta de CódigoCamp. Puedes elegir qué correos recibir en Configuración → Correos."}<br>
  <span style="font-family:Consolas,monospace;color:#3b4a74">&lt;/&gt; Aprende a programar en español</span></td></tr>
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


def smtp_configurado(app=None):
    """¿Los correos salen de verdad? Sin servidor SMTP solo se guardan como .eml en almacen_archivos/correos."""
    cfg = _config(app or current_app._get_current_object())
    return bool(cfg["servidor"] and cfg["usuario"] and cfg["clave"])


def enviar(para, asunto, html_cuerpo, *, esperar=False, al_terminar=None):
    """Envía un correo (en segundo plano salvo esperar=True). Nunca lanza: los fallos quedan en el log.
    al_terminar(estado, detalle) se llama al final (con la app activa): estado = enviado | sin_smtp | error."""
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
        if al_terminar:
            al_terminar("enviado", "")
        return True

    def tarea():
        estado, detalle = "enviado", ""
        try:
            _enviar_ya(cfg, m, carpeta)
            if not cfg["servidor"]:
                estado, detalle = "sin_smtp", "Falta configurar SMTP en backend/.env: el correo solo se guardó en almacen_archivos/correos."
        except Exception as e:  # noqa: BLE001
            estado, detalle = "error", f"{type(e).__name__}: {e}"[:300]
            app.logger.warning("No se pudo enviar el correo «%s» a %s: %s", asunto, para, e)
        if al_terminar:
            try:
                with app.app_context():
                    al_terminar(estado, detalle)
            except Exception as e:  # noqa: BLE001
                app.logger.warning("No se pudo guardar el estado del correo: %s", e)

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
        animo="saludo", etiqueta="bienvenida.js", frase=f"¡Hola {usuario.nombre.split(' ')[0]}! Soy Codi y voy a aprender contigo 👋",
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
        animo="pensando", etiqueta="seguridad.log", frase="Vi un inicio de sesión nuevo… ¿fuiste tú? 🔍"
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
        animo="pensando", etiqueta="contraseña.py", frase="¿Olvidaste tu contraseña? Tranqui, te ayudo 🔑"
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
        animo="celebra", etiqueta="seguridad.log", frase="¡Contraseña nueva lista! Tu cuenta está protegida 🛡️"
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
                                                pie="Puedes desactivar estos avisos en Configuración → Correos.",
                                                animo="alarma" if nivel_u >= 2 else "preocupado", etiqueta="racha.js",
                                                frase=(f"¡Auxilio! Tu llama de {dias} se apaga hoy 🔥" if nivel_u >= 2 else f"¿Practicamos? Llevamos {dias} juntos 🔥")))
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
