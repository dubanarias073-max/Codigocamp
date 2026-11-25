"""Genera, a partir de CONCEPTOS, el camino de retos (Inicio) y las lecciones de Aprende.

Cada concepto se escribe una sola vez con la función K(...). De él salen:
  · una SECCIÓN del camino con hasta 3 lecciones de retos, sin preguntas repetidas ni parecidas en todo el curso
  · una lección de Aprende (explicación, para qué sirve, puntos clave, código comentado, error común)

Ninguna pregunta del curso se repite ni se parece a otra (ver construir_etapas). Las opciones falsas salen de otros
conceptos de la misma etapa.

    flask --app app check-retos                    -> revisa los retos
    python herramientas/generar_aprende.py         -> vuelve a crear frontend/js/lecciones/<lenguaje>.js
"""
import re
from .base import ARM, C, E, O, ORD, PAR, etapa, leccion


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
             explicacion=f"{_nombre(c['t'])}: {c['d'].rstrip('.')}. Las otras frases son de otros temas.")


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


def _nombre(t):
    """«Qué es Python» → «Python» (algunos conceptos se titulan como pregunta)."""
    t = re.sub(r"^\s*¿?\s*(qu[ée] es|qu[ée] son|para qu[ée] sirve[n]?)\s+", "", t, flags=re.I).rstrip("?").strip()
    return t[:1].upper() + t[1:]


def _frase_completa(frase, palabra):
    completa = re.sub(r"\s*\([^()]*\)\s*$", "", frase)
    completa = re.sub(r"_{2,}", lambda _m: palabra, completa, count=1)
    return completa.strip()


def q_completar(c, segunda=False):
    p = c["pr2"] if segunda else c["pr"]
    if not p:
        return None
    # Simple y sin repetir la respuesta (ya se ve arriba): solo la razón.
    porque = f"{_nombre(c['t'])}: {c['d'].rstrip('.')}." if c.get("d") else f"La frase completa es: «{_frase_completa(p[0], p[1]).rstrip('.')}»."
    return C(p[0], *p[1:], explicacion=porque)


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


from functools import lru_cache


@lru_cache(maxsize=200_000)
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


def _candidatas(i, lista, vecinos=None):
    """(pregunta, dato) de un concepto, una por dato y en orden de prioridad (variando el tipo de pregunta).
    `vecinos` = (va, vb, vc): de dónde salen las opciones falsas (por defecto, conceptos repartidos de la etapa)."""
    c, n = lista[i], len(lista)
    va, vb, vc = vecinos or ([lista[j] for j in _vecinos(i, n, d)] for d in (A, B, Cc))
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


def _repartir(preguntas, maximo=LECCIONES_POR_CONCEPTO, n_lecciones=None):
    """Reparte las preguntas en lecciones de 3 o más (hasta `maximo`). Primero se reparten las de escribir, ordenar o
    encontrar el error, para que cada lección mezcle tipos; si una queda solo con opción múltiple, su pregunta de
    «situación» pasa a escribirse (mismo dato, otra forma de responder).
    `n_lecciones` fija cuántas lecciones salen (para no cambiar la estructura del camino y conservar el progreso)."""
    n_lecciones = n_lecciones or max(1, min(maximo, len(preguntas) // 3))
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


# ---- dificultad que sube y ejercicios tipo Duolingo -------------------------------------------------------------
#
# Nivel 0 (primer cuarto del curso), 1 (hasta el 60 %) y 2 (el resto):
#   · opciones falsas: al principio de otros temas; después, de los conceptos MÁS PARECIDOS (hay que distinguirlos)
#   · pistas como «(7 letras)»: solo en el nivel 0
#   · ejercicios extra por lección: 1, 2 y 3 (unir parejas, armar la línea con fichas, completar el código)
#   · parejas: 3, 4 y 5; fichas trampa al armar: 2, 3 y 4
# Además se quitan las preguntas «regaladas»: las que se responden porque la opción correcta repite las palabras
# del enunciado y ninguna otra lo hace.

import random as _azar

EXTRAS_POR_LECCION = (1, 2, 3)
PAREJAS = (3, 4, 5)
TRAMPAS = (2, 3, 4)
HUECO = "▁▁▁"
_COMENTARIO = ("<!--", "/*", "-- ", "//", "# ", "#!", "*")


def _dificultad(k, n):
    pos = k / max(1, n - 1)
    return 0 if pos < 0.25 else 1 if pos < 0.6 else 2


def _texto_concepto(c):
    return f"{c['t']} {c['d']} {c['u']}"


def _parecidos(i, lista, desde, cuantos):
    """Los conceptos de la etapa más parecidos a lista[i] (comparten palabras y tienen textos de largo similar)."""
    c = lista[i]
    base = _palabras(_texto_concepto(c))
    ranking = []
    for j, o in enumerate(lista):
        if j == i:
            continue
        p = _palabras(_texto_concepto(o))
        ranking.append((len(base & p) / (len(base | p) or 1), -abs(len(o["d"]) - len(c["d"])), -j, j))
    ranking.sort(reverse=True)
    return [lista[j] for *_x, j in ranking[desde:desde + cuantos]]


def _raiz(w):
    return w[:5]


def _regalada(q):
    """True si la opción correcta comparte palabras con el enunciado y ninguna falsa lo hace (se adivina sin saber)."""
    if q["tipo"] != "opcion":
        return False
    enun = {_raiz(w) for w in _palabras(q["enunciado"])}
    if not enun:
        return False
    toca = lambda texto: bool({_raiz(w) for w in _palabras(texto)} & enun)
    falsas = [o for o in q["opciones"] if o != q["respuesta"]]
    return toca(q["respuesta"]) and not any(toca(o) for o in falsas)


_PISTA = re.compile(r"\s*\((?:\d+|un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\s+(?:letras?|caracteres?|n[úu]meros?|palabras?|d[íi]gitos?|s[íi]mbolos?)\)\s*$", re.I)


def _sin_pista(q):
    if q["tipo"] == "completar" and _PISTA.search(q["enunciado"]):
        return {**q, "enunciado": _PISTA.sub("", q["enunciado"]).rstrip() or q["enunciado"]}
    return q


# Fichas de código: textos entre comillas, etiquetas HTML, números, nombres (con guiones de CSS) y símbolos.
_FICHA = re.compile(r'"[^"\n]*"|\'[^\'\n]*\'|`[^`\n]*`|</?[A-Za-z][\w-]*(?:\s[^<>]*)?/?>|(?:(?<=\s)|^)--?[A-Za-z][\w-]*(?:=\S+)?|#[0-9A-Fa-f]{3,8}(?![\w])|(?:(?<=\s)|^)(?:~|\.{1,2})?/[\w.-]+(?:/[\w.-]*)*|\d[\d_]*(?:\.\d+)?'
                    r'|[A-Za-z_$@][\w$]*(?:-[A-Za-z][\w$]*)*|==|!=|<=|>=|=>|->|::|\*\*|//|&&|\|\||\+\+|\+=|-=|[^\s\w]')


def _fichas(linea):
    return _FICHA.findall(linea)


def _es_nombre(f):
    return bool(re.fullmatch(r"[A-Za-z_$@][\w$]*(?:-[A-Za-z][\w$]*)*", f)) and len(f) >= 2


def _lineas_codigo(c):
    """(índice, línea limpia, fichas) de las líneas de código útiles del ejemplo (sin comentarios)."""
    return _lineas_de(c["cod"])


@lru_cache(maxsize=50_000)
def _lineas_de(cod):
    out = []
    for k, l in enumerate(cod.split("\n")):
        t = l.strip()
        if not t or t.startswith(_COMENTARIO) or any(m in t for m in (" # ", "//", "<!--", "/*")) or len(t) > 64:
            continue
        f = _fichas(t)
        if "".join(f).replace(" ", "") != t.replace(" ", ""):
            continue          # la línea tiene algo que no se puede partir en fichas limpias
        out.append((k, t, tuple(f)))
    return tuple(out)


def _con_hueco(c, k, linea):
    lineas = c["cod"].split("\n")
    sangria = lineas[k][:len(lineas[k]) - len(lineas[k].lstrip())]
    lineas[k] = sangria + linea
    return "\n".join(lineas)


_FICHAS_ETAPA = {}


def _todas_fichas(lista, salvo):
    """Fichas de los ejemplos de la etapa (sin las del concepto `salvo`). Se calcula una vez por etapa."""
    clave = id(lista)
    if clave not in _FICHAS_ETAPA:
        _FICHAS_ETAPA[clave] = (lista, [(o, [x for _k, _t, f in _lineas_codigo(o) for x in f]) for o in lista])
    return [x for o, fs in _FICHAS_ETAPA[clave][1] if o is not salvo for x in fs]


def q_armar(i, lista, d):
    """Arma con fichas la línea que falta en el código (con fichas trampa de otros ejemplos)."""
    c = lista[i]
    candidatas = [(k, t, f) for k, t, f in _lineas_codigo(c) if 3 <= len(f) <= 9 and sum(_es_nombre(x) or x[:1] in "\"'<" for x in f) >= 1]
    if not candidatas:
        return None
    k, t, sol = max(candidatas, key=lambda x: (len(x[2]), -x[0]))
    azar = _azar.Random(c["t"] + "|armar")
    pool = [x for x in dict.fromkeys(_todas_fichas(lista, c)) if x not in sol and len(x) <= 24]
    nombres = [x for x in pool if _es_nombre(x) or x[:1] in "\"'<"]
    simbolos = [x for x in pool if x not in nombres]
    trampas = azar.sample(nombres, min(len(nombres), TRAMPAS[d] - 1)) + azar.sample(simbolos, min(len(simbolos), 1))
    trampas = list(dict.fromkeys(trampas))[:TRAMPAS[d]]
    if len(trampas) < 2:
        return None
    return ARM(f"Arma con las fichas la línea que falta. Este código {c['h']}.", _con_hueco(c, k, HUECO), sol, trampas,
               explicacion=f"La línea que faltaba es «{t}». En el ejemplo, el código {c['h']}.")


def q_hueco(i, lista, d, evitar=None):
    """¿Qué palabra falta en el código? Las opciones son palabras del mismo tipo de otros ejemplos (no se adivina)."""
    c = lista[i]
    texto = c["cod"]
    importantes = {_raiz(w) for w in _palabras(f"{c['t']} {c['d']}")}
    mejor = None
    for k, t, f in _lineas_codigo(c):
        if evitar is not None and k == evitar:
            continue
        for x in f:
            if not _es_nombre(x) or len(re.findall(rf"(?<![\w$-]){re.escape(x)}(?![\w$-])", texto)) != 1:
                continue
            puntos = (2 if _raiz(x.lower()) in importantes else 0) + min(len(x), 12) / 12
            if mejor is None or puntos > mejor[0]:
                mejor = (puntos, k, t, x)
    if not mejor:
        return None
    _p, k, t, x = mejor
    from collections import Counter
    frecuencia = Counter(_todas_fichas(lista, c))
    forma = lambda y: (y[:1].isupper(), "-" in y, "_" in y, y[:1] == "@", y.startswith("__"))   # misma «forma»: no se descartan por mayúscula o guion
    otros = [y for y in frecuencia if _es_nombre(y) and y != x and y not in texto and forma(y) == forma(x)]
    if len(otros) < 3:
        return None
    # Las opciones falsas se parecen a la correcta: palabras frecuentes del lenguaje (como return, for, print),
    # de largo parecido y, en los niveles altos, con la misma inicial
    otros.sort(key=lambda y: (-min(frecuencia[y], 6), abs(len(y) - len(x)) + (0 if d < 2 or y[:1].lower() == x[:1].lower() else 3), y))
    azar = _azar.Random(c["t"] + "|hueco")
    falsas = azar.sample(otros[:8], 3)
    linea = re.sub(rf"(?<![\w$-]){re.escape(x)}(?![\w$-])", HUECO, t, count=1)
    return O(f"¿Qué falta en el espacio {HUECO} del código?", x, *falsas, codigo=_con_hueco(c, k, linea),
             explicacion=f"Faltaba «{x}»: la línea completa es «{t}».")


_TIPOS_PAREJAS = (
    ("Une cada concepto con para qué sirve.", lambda o: o["t"], lambda o: _mayus(o["u"])),
    ("Une cada concepto con lo que es.", lambda o: o["t"], lambda o: _mayus(o["d"])),
    ("Une cada error común con el concepto donde pasa.", lambda o: _mayus(o["ec"]), lambda o: o["t"]),
)


def q_parejas(i, lista, d, variante):
    """Unir parejas con el concepto y otros de la etapa (en los niveles altos, los más parecidos)."""
    c = lista[i]
    n = PAREJAS[d]
    otros = _parecidos(i, lista, 0, 12) if d >= 1 else [lista[j] for j in _vecinos(i, len(lista), (2, 5, 8, 11, 14, 17)[:max(0, len(lista) - 1)])]
    for paso in range(len(_TIPOS_PAREJAS)):
        enunciado, izq, der = _TIPOS_PAREJAS[(variante + paso) % len(_TIPOS_PAREJAS)]
        grupo, vistos_i, vistos_d = [], set(), set()
        for o in [c] + otros:
            a, b = izq(o), der(o)
            if len(a) > 70 or len(b) > 80 or _clave(a) in vistos_i or _clave(b) in vistos_d:
                continue
            grupo.append((a, b))
            vistos_i.add(_clave(a)); vistos_d.add(_clave(b))
            if len(grupo) == n:
                break
        if len(grupo) == n and grupo[0][0] in (izq(c),):
            return PAR(enunciado, grupo)
    return None


def _extras(i, lista, d):
    """Ejercicios tipo Duolingo de un concepto, en orden de preferencia (sin repetir el mismo dato)."""
    out = [q_parejas(i, lista, d, i % 3)]
    arm = q_armar(i, lista, d)
    out.append(arm)
    linea_armar = None
    if arm:
        linea_armar = next((k for k, l in enumerate(arm["codigo"].split("\n")) if HUECO in l), None)
    out.append(q_hueco(i, lista, d, evitar=linea_armar) if d >= 1 else None)
    out.append(q_parejas(i, lista, d, i % 3 + 1))
    vistos, final = set(), []
    for q in out:
        if q is None:
            continue
        clave = (q["tipo"], q["enunciado"], q["codigo"], str(q["datos"]))
        if clave not in vistos:
            vistos.add(clave)
            final.append(q)
    return final


def _candidatas_con_nivel(i, lista, d):
    """Como _candidatas, pero con opciones falsas más parecidas según la dificultad y sin preguntas regaladas."""
    if d == 0 or len(lista) < 8:
        sale = _candidatas(i, lista)
    else:
        c = lista[i]
        cerca = _parecidos(i, lista, 0, 9)
        va, vb, vc = (cerca[0:3], cerca[3:6], cerca[6:9]) if d == 2 else (cerca[0:3], *[[lista[j] for j in _vecinos(i, len(lista), x)] for x in (B, Cc)])
        lejos = [[lista[j] for j in _vecinos(i, len(lista), x)] for x in (A, B, Cc)]
        sale = []
        for (q, dato), (q_lejos, _) in zip(_candidatas(i, lista, (va, vb, vc)), _candidatas(i, lista)):
            # Si dos conceptos parecidos tienen el mismo texto, esa pregunta vuelve a las opciones de otros temas
            if q["tipo"] == "opcion" and len({_clave(o) for o in q["opciones"]}) != len(q["opciones"]):
                q = q_lejos
            sale.append((q, dato))
        del lejos, c
    out = []
    for q, dato in sale:
        if _regalada(q):
            continue
        out.append((_sin_pista(q) if d >= 1 else q, dato))
    return out


def construir_etapas(etapas_conceptos, repaso=False):
    """etapas_conceptos = [(titulo, descripcion, [K, K, ...]), ...]  ->  lista de etapas para ETAPAS.
    Cada concepto es una sección con hasta 3 lecciones; ninguna pregunta del curso se repite ni se parece a otra.
    Las etapas largas se parten en partes de 45 lecciones como máximo. (`repaso` ya no se usa: repasar era repetir.)

    La CANTIDAD de lecciones de cada concepto se calcula igual que siempre (así `sync-retos` actualiza las preguntas
    sin tocar el progreso); lo que cambia es qué preguntas lleva cada lección y cuántas, según la dificultad."""
    registro, registro_nuevo = _Registro(), _Registro()
    extras_del_curso = set()   # ejercicios tipo Duolingo ya usados en el curso (dos ejemplos iguales no los repiten)
    etapas = []
    total = len(etapas_conceptos)
    for k_etapa, (titulo, desc, lista) in enumerate(etapas_conceptos):
        d = _dificultad(k_etapa, total)
        secciones = []
        for i, c in enumerate(lista):
            # 1) cuántas lecciones tiene este concepto (cálculo de siempre: no cambia la estructura del camino)
            elegidas = [q for q, dato in _candidatas(i, lista) if registro.admite(q, dato)]
            if len(elegidas) < 3:
                for q, _dato in _candidatas(i, lista):
                    if len(elegidas) >= 3:
                        break
                    if q not in elegidas and registro.admite(q, ""):
                        elegidas.append(q)
            if not elegidas:
                continue
            if all(q["tipo"] == "opcion" for q in elegidas):
                con_sit = next((k for k, q in enumerate(elegidas) if q.get("_situacion")), None)
                if con_sit is not None:
                    elegidas[con_sit] = elegidas[con_sit]["_situacion"]
                else:
                    for extra in (q_orden(c), q_codigo_concepto_escribir(c), q_situacion_completar(c)):
                        if extra is not None and registro.admite(extra, ""):
                            elegidas.append(extra)
                            break
            n_lecciones = len(_repartir(elegidas))

            # 2) las preguntas de verdad: más difíciles según el nivel y sin regaladas
            nuevas = [q for q, dato in _candidatas_con_nivel(i, lista, d) if registro_nuevo.admite(q, dato)]
            partes = _repartir(nuevas, n_lecciones=n_lecciones) if nuevas else [[] for _ in range(n_lecciones)]

            # 3) ejercicios tipo Duolingo (unir parejas, armar con fichas, completar el código), sin repetir y sin
            #    dos preguntas con la misma respuesta en una lección; cada lección queda con 3 preguntas o más.
            clave_q = lambda q: (" ".join(q["enunciado"].casefold().split()), q["codigo"], str(q["datos"].get("piezas", "")),
                                 str(q["datos"].get("pares", "")), str(q["datos"].get("solucion", "")))
            respuestas_de = lambda q: {_clave(r) for r in q["respuesta"].split("|") if r.strip()} if q["tipo"] in ("opcion", "completar") else set()
            usados = {clave_q(q) for qs in partes for q in qs}
            libres = [x for x in _extras(i, lista, d) if clave_q(x) not in extras_del_curso]
            reserva = [{k2: v for k2, v in (_sin_pista(q) if d >= 1 else q).items() if k2 != "_situacion"} for q in elegidas]
            por_leccion = EXTRAS_POR_LECCION[d]
            for k, qs in enumerate(partes):
                resp = set().union(*[respuestas_de(q) for q in qs]) if qs else set()
                mios = []
                for x in list(libres):
                    if len(mios) >= por_leccion:
                        break
                    if respuestas_de(x) & resp:
                        continue
                    mios.append(x)
                    libres.remove(x)
                    extras_del_curso.add(clave_q(x))
                    resp |= respuestas_de(x)
                # Si faltan preguntas: primero más ejercicios tipo Duolingo, luego las de siempre que no regalen la
                # respuesta y, solo si no queda otra, alguna de las de siempre (sin repetir nada del curso).
                for x in list(libres):
                    if len(qs) + len(mios) >= 3:
                        break
                    if not respuestas_de(x) & resp:
                        mios.append(x); libres.remove(x); extras_del_curso.add(clave_q(x)); resp |= respuestas_de(x)
                for permitir_regalada in (False, True):
                    for q in reserva:
                        if len(qs) + len(mios) >= 3:
                            break
                        if (_regalada(q) and not permitir_regalada) or clave_q(q) in usados or respuestas_de(q) & resp or not registro_nuevo.admite(q, ""):
                            continue
                        qs.append(q)
                        usados.add(clave_q(q))
                        resp |= respuestas_de(q)
                mezcla = []
                for n_q, q in enumerate(qs):
                    mezcla.append(q)
                    if n_q < len(mios):
                        mezcla.append(mios[n_q])
                mezcla += mios[len(qs):]
                partes[k] = mezcla
            n = len(partes)
            lecciones = [leccion((f"{c['t']} · práctica {k + 1} de {n}" if n > 1 else f"{c['t']} · práctica")[:80], *qs) for k, qs in enumerate(partes)]
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
                # Para Aprende interactivo: el reto con su respuesta (se revisa en el navegador) y el error común suelto
                "q": c["pr"][0], "a": str(c["pr"][1]), "f": _mayus(c["ec"]) + ".",
            })
    return out
