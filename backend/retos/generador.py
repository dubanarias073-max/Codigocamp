"""Genera, a partir de CONCEPTOS, el camino de retos (Inicio) y las lecciones de Aprende.

Cada concepto se escribe una sola vez con la función K(...). De él salen:
  · una SECCIÓN del camino con hasta 3 lecciones de retos, sin preguntas repetidas ni parecidas en todo el curso
  · una lección de Aprende (explicación, para qué sirve, puntos clave, código comentado, error común)

Ninguna pregunta del curso se repite ni se parece a otra (ver construir_etapas). Las opciones falsas salen de otros
conceptos de la misma etapa.

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


# ---- armado del camino: cada dato se pregunta UNA vez en todo el curso ----
#
# Un concepto aporta unos 9 a 12 «datos» distintos (definición, uso, 3 ideas clave, situación, código, completar,
# segundo completar, error común y, a veces, «encuentra el error»). Cada dato produce una sola pregunta en todo el
# curso. Además se descarta cualquier pregunta cuyo dato o respuesta ya apareció en el curso, aunque sea con otras
# palabras (se comparan las palabras importantes): así no hay preguntas repetidas ni parecidas.
# Con esas preguntas se arman hasta 3 lecciones por concepto, y cada etapa se parte para no pasar de 45 lecciones.

MAX_LECCIONES_ETAPA = 45
LECCIONES_POR_CONCEPTO = 3
_VACIAS = set("""a al algo ante antes asi aun cada como con contra cual cuando de del desde donde dos el ella ellas ellos en
entre era es esa ese eso esta este esto estos estas fue ha hace hay la las le lo los mas me mi muy no nos o otra otro para
pero poco por que se sea ser si sin sobre solo su sus tambien te tiene todo tu un una uno unos unas usa usar y ya cosa
forma manera sirve sirven permite permiten puede pueden""".split())


def _sin_tildes(texto):
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFD", texto) if unicodedata.category(ch) != "Mn")


def _palabras(texto):
    """Palabras importantes de un texto (sin tildes, sin palabras vacías)."""
    import re
    t = _sin_tildes(str(texto).casefold())
    return frozenset(w for w in re.findall(r"[a-z0-9_#+.<>/-]+", t) if w.strip(".-/") and w not in _VACIAS and len(w) > 1)


def _clave(texto):
    return " ".join(_sin_tildes(str(texto).casefold()).replace("¿", "").replace("?", "").split()).strip(" .")


class _Registro:
    """Lo ya preguntado en un curso: enunciados, respuestas y «datos» (para detectar preguntas parecidas)."""

    def __init__(self):
        self.enunciados, self.respuestas, self.datos, self.indice = set(), set(), [], {}

    def parecido(self, palabras):
        if len(palabras) < 2:
            return False
        candidatos = set()
        for w in palabras:
            candidatos.update(self.indice.get(w, ()))
        for i in candidatos:
            otro = self.datos[i]
            comunes = len(palabras & otro)
            if comunes / len(palabras | otro) >= 0.5 or (min(len(palabras), len(otro)) >= 3 and comunes / min(len(palabras), len(otro)) >= 0.8):
                return True
        return False

    def admite(self, pregunta, dato):
        enunciado = _clave(pregunta["enunciado"]) + "|" + pregunta["codigo"] + "|" + "\n".join(pregunta["datos"].get("piezas", []))
        respuestas = {_clave(r) for r in pregunta["respuesta"].split("|") if r.strip()} if pregunta["tipo"] in {"opcion", "completar"} else set()
        if enunciado in self.enunciados or respuestas & self.respuestas:
            return False
        palabras = _palabras(dato)
        if self.parecido(palabras):
            return False
        self.enunciados.add(enunciado)
        self.respuestas |= respuestas
        i = len(self.datos)
        self.datos.append(palabras)
        for w in palabras:
            self.indice.setdefault(w, []).append(i)
        return True


def _completo(p):
    """El dato de una pregunta para completar: la frase con la respuesta puesta."""
    import re
    frase = re.sub(r"\([^)]*\)\s*$", "", p[0]).strip()
    return frase.replace("___", p[1])


def _candidatas(i, lista):
    """(pregunta, dato) de un concepto, una por dato y en orden de prioridad (variando el tipo de pregunta)."""
    c, n = lista[i], len(lista)
    va, vb, vc = ([lista[j] for j in _vecinos(i, n, d)] for d in (A, B, Cc))
    ordenable = _lineas_orden(c) is not None
    codigo = q_orden(c) if ordenable and i % 2 else q_codigo_hace(c, vb)
    pr2_real = not c["pr2"][0].startswith("Completa: un error común")
    sale = [
        (q_completar(c), _completo(c["pr"])),
        (q_que(c, va), c["d"]),
        ({**q_cuando(c, vb), "_situacion": q_situacion_completar(c)}, _sin_pregunta(c["sit"])),
        (codigo, c["h"]),
        (q_uso(c, vc), c["u"]),
        (q_cierta(c, vb, 0), c["k"][0]),
        (q_error(c) if c["err"] else None, c["err"][2] if c["err"] else ""),
        (q_ec(c, va), c["ec"]),
        (q_completar(c, True) if pr2_real else None, _completo(c["pr2"]) if pr2_real else ""),
        (q_cierta(c, vc, 1), c["k"][1]),
        (q_cierta(c, va, 2), c["k"][2]),
    ]
    return [(q, dato) for q, dato in sale if q is not None]


def _repartir(preguntas, maximo=LECCIONES_POR_CONCEPTO):
    """Reparte las preguntas en lecciones de 3 o más (hasta `maximo`). Primero se reparten las de escribir, ordenar o
    encontrar el error, para que cada lección mezcle tipos; si una queda solo con opción múltiple, su pregunta de
    «situación» pasa a escribirse (mismo dato, otra forma de responder)."""
    n_lecciones = max(1, min(maximo, len(preguntas) // 3))
    lecciones = [[] for _ in range(n_lecciones)]
    activas = [q for q in preguntas if q["tipo"] != "opcion"]
    resto = [q for q in preguntas if q["tipo"] == "opcion"]
    for k, q in enumerate(activas):
        lecciones[k % n_lecciones].append(q)
    for q in resto:
        min(lecciones, key=len).append(q)
    for lec in lecciones:
        if all(q["tipo"] == "opcion" for q in lec):
            for k, q in enumerate(lec):
                if q.get("_situacion"):
                    lec[k] = q["_situacion"]
                    break
    for lec in lecciones:
        for k, q in enumerate(lec):
            lec[k] = {clave: v for clave, v in q.items() if clave != "_situacion"}
    return lecciones


def construir_etapas(etapas_conceptos, repaso=False):
    """etapas_conceptos = [(titulo, descripcion, [K, K, ...]), ...]  ->  lista de etapas para ETAPAS.
    Cada concepto es una sección con hasta 3 lecciones; ninguna pregunta del curso se repite ni se parece a otra.
    Las etapas largas se parten en partes de 45 lecciones como máximo. (`repaso` ya no se usa: repasar era repetir.)"""
    registro = _Registro()
    etapas = []
    for titulo, desc, lista in etapas_conceptos:
        secciones = []
        for i, c in enumerate(lista):
            elegidas = [q for q, dato in _candidatas(i, lista) if registro.admite(q, dato)]
            if len(elegidas) < 3:
                # Casi todo lo de este concepto ya se preguntó en otro: se completa con lo menos parecido que quede.
                for q, _dato in _candidatas(i, lista):
                    if len(elegidas) >= 3:
                        break
                    if q not in elegidas and registro.admite(q, ""):
                        elegidas.append(q)
            if not elegidas:
                continue
            if all(q["tipo"] == "opcion" for q in elegidas):
                # Sección solo de opción múltiple: una pregunta pasa a escribirse.
                con_sit = next((k for k, q in enumerate(elegidas) if q.get("_situacion")), None)
                if con_sit is not None:
                    elegidas[con_sit] = elegidas[con_sit]["_situacion"]
                else:
                    for extra in (q_orden(c), q_codigo_concepto_escribir(c), q_situacion_completar(c)):
                        if extra is not None and registro.admite(extra, ""):
                            elegidas.append(extra)
                            break
            partes = _repartir(elegidas)
            n = len(partes)
            lecciones = [leccion((f"{c['t']} · práctica {k + 1} de {n}" if n > 1 else f"{c['t']} · práctica")[:80], *qs) for k, qs in enumerate(partes)]
            # Si no se pudo variar el tipo sin repetir una respuesta, se prefiere no repetir (y se marca para el validador).
            un_tipo = len({q["tipo"] for qs in partes for q in qs}) < 2
            secciones.append({"titulo": c["t"], "lecciones": lecciones, "agrupada": True, **({"un_tipo": True} if un_tipo else {})})
        # Partir la etapa para que ninguna tenga más de MAX_LECCIONES_ETAPA lecciones.
        grupos, actual, cuenta = [], [], 0
        for sec in secciones:
            if actual and cuenta + len(sec["lecciones"]) > MAX_LECCIONES_ETAPA:
                grupos.append(actual)
                actual, cuenta = [], 0
            actual.append(sec)
            cuenta += len(sec["lecciones"])
        if actual:
            grupos.append(actual)
        if len(grupos) > 1:  # partes parejas en vez de una grande y una pequeña
            import math
            por_parte = math.ceil(len(secciones) / len(grupos))
            grupos = [secciones[k:k + por_parte] for k in range(0, len(secciones), por_parte)]
        for k, grupo in enumerate(grupos, 1):
            nombre = titulo if len(grupos) == 1 else f"{titulo} · parte {k} de {len(grupos)}"
            etapas.append(etapa(nombre[:80], desc, *grupo))
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
