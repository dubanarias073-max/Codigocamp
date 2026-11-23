"""Temas «de referencia» escritos en una sola fila (etiquetas de HTML, propiedades de CSS, métodos de JavaScript…).

Cada fila produce un concepto K completo (sección del camino + lección de Aprende), igual que los escritos a mano:
    R(t, token, d, u, cod, h, ec, mas="", err=None, sit=None)
  t      título único                         («Etiqueta abbr»)
  token  lo que se escribe para usarlo         («abbr»): sale la pregunta de completar
  d, u   definición y para qué sirve (cortas, sin punto final)
  cod    ejemplo con comentarios
  h      qué hace el ejemplo
  ec     error común
  mas    explicación ampliada (opcional: si falta se arma con d, u y h)
  err    (código con error, línea, explicación) para «encuentra el error» (opcional)
  sit    situación real que termina en «¿Qué usarías?» (opcional)
"""
from ..generador import K


def _m(s):
    return s[:1].upper() + s[1:]


def R(t, token, d, u, cod, h, ec, mas="", err=None, sit=None, pista=None):
    mas = mas or f"{_m(d)}. Se usa para {u}. En el ejemplo, {h}."
    k = [f"{t}: {d}.", f"{t} sirve para {u}.", f"Con {t} hay que evitar {ec}."]
    sit = sit or f"En tu proyecto necesitas {u}. ¿Qué usarías?"
    n = len(token)
    pr = (f"{pista or f'Para {u}, escribe'} ___ ({n} {'carácter' if n == 1 else 'caracteres'})", token)
    return K(t, d=d, u=u, mas=mas, k=k, sit=sit, cod=cod, h=h, pr=pr, ec=ec, err=err)


def filas(texto, out=None):
    """Temas de referencia en formato compacto, uno por línea:
        Título ¦ token ¦ qué es ¦ para qué sirve ¦ código (⏎ = salto de línea) ¦ qué hace ¦ error común
    `token` es la respuesta de «completa el espacio». Las líneas vacías o que empiezan con # se ignoran."""
    lista = []
    for n, linea in enumerate(texto.strip().splitlines(), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        partes = [p.strip() for p in linea.split(" ¦ ")]
        if len(partes) != 7:
            raise ValueError(f"Fila {n} con {len(partes)} campos (deben ser 7): {linea[:80]}")
        t, token, d, u, cod, h, ec = partes
        c = R(t, token, d, u, cod.replace("⏎", "\n"), h, ec)
        c["ref"] = True
        c["out"] = out
        lista.append(c)
    return lista
