"""Correos que recibe una persona cuando el administrador le cambia algo: diamantes, XP, vidas, racha, medallas,
cosméticos regalados, faltas retiradas… Cada correo dice qué cambió y, si el administrador escribió una nota, la incluye."""
import html

from flask import current_app


def _num(n):
    return f"{n:,}".replace(",", ".")


def lineas_cambios(antes, despues):
    """Frases amables a partir de los valores antes/después ({campo: valor})."""
    lineas = []
    regalo = False

    def delta(campo, unidad, emoji_mas, emoji_menos, nombre=None):
        nonlocal regalo
        a, d = antes.get(campo), despues.get(campo)
        if a is None or d is None or a == d:
            return
        n = d - a
        if n > 0:
            regalo = True
            lineas.append(f"{emoji_mas} <b>Recibiste {_num(n)} {unidad}</b>. Ahora tienes {_num(d)}.")
        else:
            lineas.append(f"{emoji_menos} Se ajustaron tus {nombre or unidad}: se descontaron {_num(-n)}. Ahora tienes {_num(d)}.")

    delta("diamante", "diamantes", "💎", "💎")
    delta("xp_total", "XP", "⚡", "⚡", "puntos de experiencia")
    delta("vidas", "vidas", "❤️", "❤️")
    delta("salvarrachas", "salvarrachas", "🧊", "🧊")
    if antes.get("racha_actual") is not None and antes.get("racha_actual") != despues.get("racha_actual"):
        d = despues["racha_actual"]
        regalo = regalo or d > antes["racha_actual"]
        lineas.append(f"🔥 Tu racha quedó en <b>{_num(d)} {'día' if d == 1 else 'días'}</b>.")
    for campo, nombre in (("nombre", "nombre"), ("alias", "alias")):
        if antes.get(campo) != despues.get(campo) and despues.get(campo) is not None:
            lineas.append(f"✏️ Tu {nombre} en CódigoCamp ahora es <b>{html.escape(str(despues[campo]))}</b>.")
    return lineas, regalo


def correo_cambios(usuario, lineas, *, nota="", regalo=False, asunto=None):
    """Envía el aviso (si no hay líneas no envía nada). Devuelve True si se mandó."""
    if not lineas:
        return False
    from servicios.correo import _config, enviar, plantilla
    nombre = html.escape((usuario.nombre or "").split(" ")[0] or "hola")
    parrafos = [f"Hola {nombre}, el equipo de CódigoCamp hizo {'un regalo' if regalo else 'cambios'} en tu cuenta:"]
    parrafos += lineas
    if nota:
        parrafos.append(f"<b>Mensaje del administrador:</b> «{html.escape(nota)}»")
    parrafos.append("¡Sigue aprendiendo! 🚀" if regalo else "Si tienes dudas, responde a este correo.")
    url = _config(current_app)["url"]
    asunto = asunto or ("🎁 ¡Recibiste un regalo en CódigoCamp!" if regalo else "Novedades en tu cuenta de CódigoCamp")
    return bool(enviar(usuario.email, asunto, plantilla(
        "¡Tienes un regalo!" if regalo else "Cambios en tu cuenta", parrafos, ("Abrir CódigoCamp", f"{url}/pages/inicio.html"),
        pie="Te escribimos porque el administrador de CódigoCamp actualizó tu cuenta.",
        animo="celebra" if regalo else "saludo", etiqueta="cuenta.log", frase="¡Para ti! 🎉" if regalo else "")))
