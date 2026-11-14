"""Genera, a partir de CONCEPTOS, el camino de retos (Inicio) y las lecciones de Aprende.

Cada concepto se escribe una sola vez con la función K(...). De él salen:
  · una SECCIÓN del camino con 4 lecciones de retos (concepto, uso, código y errores/práctica)
  · una lección de Aprende (explicación, para qué sirve, puntos clave, código comentado, error común)

Las preguntas de cada lección deben variar en objetivo y respuesta; las lecciones posteriores también
recuperan conceptos ya vistos. Las opciones falsas salen de otros conceptos de la misma etapa.

    flask --app app check-retos                    -> revisa los retos
    python herramientas/generar_aprende.py         -> vuelve a crear frontend/js/lecciones/<lenguaje>.js
"""
from .base import C, E, O, ORD, etapa, leccion


def K(t, d, u, mas, k, sit, cod, h, pr, ec, err=None, r=None, pr2=None, out=None):
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
    out  salida esperada del código (solo lenguajes que no corren en el navegador; C y C++ se calculan solos compilando)
    """
    return dict(t=t, d=d, u=u, mas=mas, k=list(k), sit=sit, cod=cod, h=h, pr=tuple(pr), ec=ec, err=err, r=r, out=out,
                pr2=tuple(pr2) if pr2 else (f"Completa: un error común con «{t}» es ___.", ec))
    # Si falta pr2, se comprueba el error común, no se vuelve a preguntar la definición del concepto.


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


def q_situacion_completar(c):
    return C(c["sit"], c["t"], explicacion=f"En esa situación encaja «{c['t']}»: {c['u']}.")


_FRASES_CIERTA = ("¿Cuál de estas ideas es cierta sobre «{t}»?", "Elige la afirmación correcta sobre «{t}»:", "¿Qué afirmación sobre «{t}» es verdadera?")


def q_cierta(c, vs, n=1):
    """Una idea cierta de c (k[n]) frente a ideas de otros conceptos."""
    return O(_FRASES_CIERTA[n].format(t=c["t"]), c["k"][n], *[v["k"][(n + 1) % 3] for v in vs],
             explicacion=c["k"][n])


def q_situacion(c, vs):
    return O(f"¿En cuál de estas situaciones usarías «{c['t']}»?", _sin_pregunta(c["sit"]), *[_sin_pregunta(v["sit"]) for v in vs],
             explicacion=f"{c['t']}: {c['u']}.")


def q_falsa(c, vs):
    return O(f"¿Cuál de estas frases NO es cierta sobre «{c['t']}»?", vs[0]["k"][0], *c["k"],
             explicacion=f"Esa afirmación describe «{vs[0]['t']}», no «{c['t']}».")


def q_codigo_hace(c, vs):
    return O("¿Qué hace este código?", _mayus(c["h"]), *[_mayus(v["h"]) for v in vs], codigo=c["cod"],
             explicacion=f"El código {c['h']}.")


def q_codigo_concepto(c, vs):
    return O("¿Qué concepto se practica en este código?", c["t"], *[v["t"] for v in vs], codigo=c["cod"],
             explicacion=f"El ejemplo practica «{c['t']}»: {c['h']}.")


def q_codigo_concepto_escribir(c):
    return C("Escribe el concepto que se practica en este código.", c["t"], codigo=c["cod"],
             explicacion=f"El ejemplo practica «{c['t']}»: {c['h']}.")


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
    return O(f"¿Cuál es un error común con «{c['t']}»?", _mayus(c["ec"]), *[_mayus(v["ec"]) for v in vs],
             explicacion=f"Un error frecuente es {_mayus(c['ec'])}.")


def q_ec_nombre(c, vs):
    return O(f"Este error es típico: «{_mayus(c['ec'])}». ¿Con qué concepto ocurre?", c["t"], *[v["t"] for v in vs],
             explicacion=f"Se relaciona con «{c['t']}»: {c['ec']}.")


def _lineas_orden(c):
    ls = [l.strip() for l in c["cod"].split("\n") if l.strip()
          and not l.strip().startswith(("<!--", "/*", "-- ", "//", "# "))]
    return ls if 3 <= len(ls) <= 6 and len(set(ls)) == len(ls) else None


def q_orden(c):
    ls = _lineas_orden(c)
    return ORD("Ordena las líneas para formar el código", *ls,
               explicacion=f"En este orden, el código {c['h']}.") if ls else None


def _limpia(lista):
    return [q for q in lista if q is not None]


def _respuesta_claves(pregunta):
    if pregunta["tipo"] not in {"opcion", "completar"}:
        return set()
    return {" ".join(respuesta.casefold().split()) for respuesta in pregunta["respuesta"].split("|") if respuesta.strip()}


def _distintas(preguntas, minimo=4, maximo=5):
    """Evita volver a preguntar lo mismo con otra redacción dentro de una lección."""
    elegidas, enunciados, respuestas = [], set(), set()
    for pregunta in preguntas:
        if pregunta is None:
            continue
        enunciado = " ".join(pregunta["enunciado"].casefold().split())
        claves = _respuesta_claves(pregunta)
        if enunciado in enunciados or (claves and claves.intersection(respuestas)):
            continue
        elegidas.append(pregunta)
        enunciados.add(enunciado)
        respuestas.update(claves)
        if len(elegidas) == maximo:
            break
    if len(elegidas) < minimo:
        raise ValueError(f"Una lección generada necesita al menos {minimo} preguntas distintas; solo hay {len(elegidas)}.")
    return elegidas


def _pregunta_anterior(previos, indice):
    if indice >= len(previos):
        return None
    lista, i = previos[indice]
    concepto = lista[i]
    funcion = (q_cuando, q_nombre, q_que)[indice]
    return funcion(concepto, [lista[j] for j in _vecinos(i, len(lista), A)])


def _lecciones(i, lista, previos, repaso=False):
    """Las cuatro lecciones de un concepto mezclan comprensión, uso, código y errores."""
    c, n = lista[i], len(lista)
    va, vb, vc = ([lista[j] for j in _vecinos(i, n, d)] for d in (A, B, Cc))
    t = c["t"]
    l1 = leccion(f"{t}: qué es", *_distintas([
        q_completar(c), q_que(c, va), q_cierta(c, va, 0), q_cierta(c, vb, 1),
        q_uso(c, vc), q_cuando(c, vb), q_falsa(c, vc),
    ]))
    l2 = leccion(f"{t}: para qué sirve", *_distintas([
        q_uso(c, va), q_situacion_completar(c), q_codigo_hace(c, vc), _pregunta_anterior(previos, 0),
        q_cierta(c, vc, 2), q_falsa(c, vb),
    ]))
    l3 = leccion(f"{t}: en código", *_distintas([
        q_orden(c), q_codigo_hace(c, va), q_codigo_concepto_escribir(c), _pregunta_anterior(previos, 1),
        q_cierta(c, va, 2), q_uso(c, vc), q_cuando(c, vb), q_que(c, va),
    ]))
    l4 = leccion(f"{t}: errores y práctica", *_distintas([
        q_completar(c, True), q_error(c) if c["err"] else None, q_falsa(c, vb), _pregunta_anterior(previos, 2),
        q_ec(c, va), q_uso(c, vc), q_codigo_lee(c, vb), q_cierta(c, vc, 1),
    ]))
    if not repaso:                      # cursos sin repaso: solo las 4 lecciones del concepto
        return [l1, l2, l3, l4]
    # Repaso: tres preguntas sobre conceptos anteriores y tres sobre el actual.
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


def construir_etapas(etapas_conceptos, repaso=False):
    """etapas_conceptos = [(titulo, descripcion, [K, K, ...]), ...]  ->  lista de etapas para ETAPAS.
    repaso=False quita la lección «Repaso de …» de cada sección (y __init__.CON_REPASO decide si hay «Práctica de repaso»; ningún curso lo lleva)."""
    etapas, historial = [], []   # historial: conceptos anteriores como (lista_de_su_etapa, índice)
    for titulo, desc, lista in etapas_conceptos:
        secciones = []
        for i, c in enumerate(lista):
            previos = [historial[-k] for k in (1, 3, 5) if len(historial) >= k]
            sec = {"titulo": c["t"], "lecciones": _lecciones(i, lista, previos, repaso), "agrupada": True}
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
