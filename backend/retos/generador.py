"""Genera, a partir de CONCEPTOS, el camino de retos (Inicio) y las lecciones de Aprende.

Cada concepto se escribe una sola vez con la función K(...). De él salen:
  · una SECCIÓN del camino con 5 lecciones de retos (qué es, para qué sirve, en código, errores, repaso)
  · una lección de Aprende (explicación, para qué sirve, puntos clave, código comentado, error común)

Las opciones falsas de las preguntas son los datos de OTROS conceptos de la misma etapa, así que cada
concepto debe tener una definición (d), un uso (u), un error común (ec) y un título (t) distintos de los demás.

    flask --app app check-retos                    -> revisa los retos
    python herramientas/generar_aprende.py         -> vuelve a crear frontend/js/lecciones/<lenguaje>.js
"""
from .base import C, E, O, ORD, etapa, leccion


def K(t, d, u, mas, k, sit, cod, h, pr, ec, err=None, r=None, pr2=None):
    """Un concepto.
    t    título corto y único ("Etiqueta p")
    d    definición corta, sin punto final ("Lenguaje que describe el contenido de una página")
    u    para qué sirve, corto, sin punto final ("Mostrar texto en párrafos")
    mas  explicación ampliada para Aprende (2 a 4 frases)
    k    3 puntos clave: frases ciertas que mencionan el concepto
    sit  situación real que termina en «¿Qué usarías?» (la respuesta es este concepto)
    cod  código de ejemplo con comentarios de una línea que lo explican
    h    qué hace el código, corto, sin punto final
    pr   (pregunta, respuesta válida, otra válida...) para completar
    ec   error común, corto, sin punto final
    err  (código con un error, línea del error, explicación) para «encuentra el error» (opcional)
    r    «Ahora tú» para Aprende (opcional; si falta se usa la pregunta de pr)
    pr2  segunda pregunta para completar (opcional; úsala en conceptos con código)
    """
    return dict(t=t, d=d, u=u, mas=mas, k=list(k), sit=sit, cod=cod, h=h, pr=tuple(pr), ec=ec, err=err, r=r, pr2=tuple(pr2) if pr2 else None)


def _mayus(s):
    return s[:1].upper() + s[1:]


def _sin_pregunta(sit):
    """Quita la última frase «¿Qué usarías?» de la situación."""
    i = sit.rfind("¿")
    return sit[:i].strip() if i > 0 else sit


def _vecinos(i, n, desp):
    """Índices de otros conceptos de la misma etapa, repartidos (no los más cercanos, que se parecen más)."""
    res = []
    for d in desp:
        j = (i + d) % n
        while j == i or j in res:
            j = (j + 1) % n
        res.append(j)
    return res


A, B, Cc = (3, 7, 11), (5, 9, 13), (2, 6, 15)


# ---- preguntas (cada una recibe el concepto c y la lista de distractores vs) ----
def q_que(c, vs):
    return O(f"¿Qué es «{c['t']}»?", _mayus(c["d"]), *[_mayus(v["d"]) for v in vs], explicacion=f"{c['t']}: {c['d']}.")


def q_nombre(c, vs):
    return O(f"¿Qué concepto se describe así? «{_mayus(c['d'])}»", c["t"], *[v["t"] for v in vs], explicacion=f"Es {c['t']}: {c['d']}.")


def q_uso(c, vs):
    return O(f"¿Para qué sirve «{c['t']}»?", _mayus(c["u"]), *[_mayus(v["u"]) for v in vs], explicacion=f"{c['t']} sirve para: {c['u']}.")


def q_uso_nombre(c, vs):
    return O(f"Necesitas esto: «{_mayus(c['u'])}». ¿Qué concepto encaja?", c["t"], *[v["t"] for v in vs], explicacion=f"{c['t']} sirve para: {c['u']}.")


def q_cuando(c, vs):
    return O(c["sit"], c["t"], *[v["t"] for v in vs], explicacion=f"{c['t']}: {c['d']}.")


_FRASES_CIERTA = ("¿Cuál de estas ideas es cierta sobre «{t}»?", "Elige la afirmación correcta sobre «{t}»:", "¿Qué afirmación sobre «{t}» es verdadera?")


def q_cierta(c, vs, n=1):
    """Una idea cierta de c (k[n]) frente a ideas de otros conceptos."""
    return O(_FRASES_CIERTA[n].format(t=c["t"]), c["k"][n], *[v["k"][(n + 1) % 3] for v in vs])


def q_situacion(c, vs):
    return O(f"¿En cuál de estas situaciones usarías «{c['t']}»?", _sin_pregunta(c["sit"]), *[_sin_pregunta(v["sit"]) for v in vs],
             explicacion=f"{c['t']}: {c['u']}.")


def q_falsa(c, vs):
    return O(f"¿Cuál de estas frases NO es cierta sobre «{c['t']}»?", vs[0]["k"][0], *c["k"],
             explicacion="Esa frase habla de otro concepto distinto.")


def q_codigo_hace(c, vs):
    return O("¿Qué hace este código?", _mayus(c["h"]), *[_mayus(v["h"]) for v in vs], codigo=c["cod"])


def q_codigo_concepto(c, vs):
    return O("¿Qué concepto se practica en este código?", c["t"], *[v["t"] for v in vs], codigo=c["cod"])


def q_codigo_lee(c, vs):
    return O("Lee el código con calma. ¿Cuál de estas descripciones es correcta?", _mayus(c["h"]), *[_mayus(v["h"]) for v in vs],
             codigo=c["cod"], explicacion=f"El código {c['h']}.")


def q_completar(c, segunda=False):
    p = c["pr2"] if segunda else c["pr"]
    return C(p[0], *p[1:], explicacion=f"Respuesta: {p[1]}.") if p else None


def q_error(c):
    e = c["err"]
    return E("Encuentra la línea con el error", e[0], e[1], e[2])


def q_ec(c, vs):
    return O(f"¿Cuál es un error común con «{c['t']}»?", _mayus(c["ec"]), *[_mayus(v["ec"]) for v in vs])


def q_ec_nombre(c, vs):
    return O(f"Este error es típico: «{_mayus(c['ec'])}». ¿Con qué concepto ocurre?", c["t"], *[v["t"] for v in vs])


def _lineas_orden(c):
    ls = [l.strip() for l in c["cod"].split("\n") if l.strip()
          and not l.strip().startswith(("<!--", "/*", "-- ", "//", "# "))]
    return ls if 3 <= len(ls) <= 6 and len(set(ls)) == len(ls) else None


def q_orden(c):
    ls = _lineas_orden(c)
    return ORD("Ordena las líneas para formar el código", *ls) if ls else None


def _limpia(lista):
    return [q for q in lista if q is not None]


def _lecciones(i, lista, previos):
    """Las 5 lecciones de un concepto. `previos` son conceptos ya vistos (de esta etapa o la anterior) para el repaso."""
    c, n = lista[i], len(lista)
    va, vb, vc = ([lista[j] for j in _vecinos(i, n, d)] for d in (A, B, Cc))
    t = c["t"]
    l1 = leccion(f"{t}: qué es",
                 q_que(c, va), q_nombre(c, vb), q_cierta(c, va, 1), q_falsa(c, vb), q_uso(c, vc), q_cierta(c, vc, 2))
    l2 = leccion(f"{t}: para qué sirve",
                 q_uso_nombre(c, va), q_cuando(c, vb), q_situacion(c, vc), q_cierta(c, vb, 0))
    l3 = leccion(f"{t}: en código",
                 *_limpia([q_codigo_hace(c, va), q_codigo_concepto(c, vb), q_codigo_lee(c, vc), q_completar(c), q_orden(c)]))
    l4 = leccion(f"{t}: errores y práctica",
                 *_limpia([q_error(c) if c["err"] else None, q_ec(c, va), q_ec_nombre(c, vb), q_falsa(c, va),
                           q_completar(c, True)]))
    # Repaso: 3 preguntas de conceptos anteriores (repetidas a propósito) y 3 de este
    rep = []
    for p, mk in zip(previos[:3], (q_que, q_cuando, q_nombre)):
        pl, pi = p
        rep.append(mk(pl[pi], [pl[j] for j in _vecinos(pi, len(pl), A)]))
    extras = [q_cierta(c, va, 0), q_ec(c, vb), q_codigo_concepto(c, vb)]
    while len(rep) < 3:                 # los primeros conceptos aún no tienen nada que repasar
        rep.append(extras.pop(0))
    l5 = leccion(f"Repaso de {t}",
                 *rep, q_uso_nombre(c, vc), q_situacion(c, va), q_codigo_concepto(c, vc))
    return [l1, l2, l3, l4, l5]


def construir_etapas(etapas_conceptos):
    """etapas_conceptos = [(titulo, descripcion, [K, K, ...]), ...]  ->  lista de etapas para ETAPAS."""
    etapas, historial = [], []   # historial: conceptos anteriores como (lista_de_su_etapa, índice)
    for titulo, desc, lista in etapas_conceptos:
        secciones = []
        for i, c in enumerate(lista):
            previos = [historial[-k] for k in (1, 3, 5) if len(historial) >= k]
            sec = {"titulo": c["t"], "lecciones": _lecciones(i, lista, previos), "agrupada": True}
            secciones.append(sec)
            historial.append((lista, i))
        e = etapa(titulo, desc, *secciones)
        etapas.append(e)
    return etapas


# ---- Aprende ----


def lecciones_aprende(etapas_conceptos, editable=True):
    out = []
    for titulo, _desc, lista in etapas_conceptos:
        for c in lista:
            e = _mayus(c["ec"]) + "."
            if c["err"]:
                e += " " + c["err"][2]
            out.append({
                "m": titulo, "t": c["t"],
                "x": f"{_mayus(c['d'])}.\n\n{c['mas']}",
                "u": f"{_mayus(c['u'])}.\n\n{_sin_pregunta(c['sit'])}",
                "p": c["k"], "c": c["cod"], "h": _mayus(c["h"]) + ".",
                "r": c["r"] or (("Cambia el código del ejemplo y mira qué pasa. Reto: " if editable else "Reto mental: ") + c["pr"][0]), "e": e,
            })
    return out
