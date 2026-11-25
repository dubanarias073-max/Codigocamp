"""Detector de enlaces peligrosos (phishing, virus, estafas) para todo CódigoCamp.

Se usa antes de abrir un enlace de tus páginas en Trabajo, de un chat o de la IA, y antes de que el Conector o el
proxy de Trabajo descarguen algo. Resultado: {"nivel": "seguro" | "advertencia" | "bloqueado", "motivo": "…"}.
Un enlace «bloqueado» NO se abre aunque la persona insista: CódigoCamp no se hace responsable de abrirlo.

Privacidad: los enlaces que se revisan NO se guardan en la base de datos ni en los registros. Solo queda en memoria
un resultado por unos minutos (identificado con una huella SHA-256, no con el enlace) para no revisar dos veces.

Capas:
  1. Reglas propias: esquemas peligrosos (javascript:, data:, file:…), usuario y clave escondidos en el enlace
     («https://google.com@estafa.xyz»), dominios que imitan marcas (paypa1.com, g00gle.com, bancolombia-seguro.top…),
     caracteres de otros alfabetos que parecen letras normales (punycode), descargas de programas desde direcciones
     IP o acortadores, y dominios de listas negras.
  2. Listas públicas de malware y phishing (URLhaus de abuse.ch y otras): `flask --app app actualizar-listas` las
     descarga en backend/seguridad/listas/ (programa ese comando una vez al día).
  3. Google Safe Browsing, si pones SAFE_BROWSING_KEY en backend/.env (gratis en Google Cloud).
"""
import hashlib
import ipaddress
import os
import re
import threading
import time
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

CARPETA_LISTAS = Path(__file__).resolve().parent.parent / "seguridad" / "listas"
LISTA_LOCAL = Path(__file__).resolve().parent.parent / "seguridad" / "dominios_bloqueados.txt"

# Marcas que más se suplantan (en Colombia y en general) → sus dominios oficiales
MARCAS = {
    "google": {"google.com", "google.com.co", "googleapis.com", "gstatic.com", "googleusercontent.com", "youtube.com", "goo.gl", "g.co", "withgoogle.com", "web.app", "firebaseapp.com"},
    "gmail": {"gmail.com", "google.com"}, "youtube": {"youtube.com", "youtu.be", "google.com"},
    "microsoft": {"microsoft.com", "live.com", "office.com", "microsoftonline.com", "azure.com", "windows.net", "xbox.com", "msn.com", "azurewebsites.net"},
    "outlook": {"outlook.com", "live.com", "office.com", "microsoft.com"}, "office365": {"office.com", "microsoft.com"},
    "apple": {"apple.com", "icloud.com", "apple.co"}, "icloud": {"icloud.com", "apple.com"},
    "facebook": {"facebook.com", "fb.com", "fb.me", "meta.com", "facebook.net"}, "instagram": {"instagram.com", "facebook.com"},
    "whatsapp": {"whatsapp.com", "whatsapp.net", "wa.me"}, "netflix": {"netflix.com"}, "spotify": {"spotify.com"},
    "paypal": {"paypal.com", "paypal.me"}, "amazon": {"amazon.com", "amazon.es", "amazonaws.com", "aws.amazon.com", "a.co"},
    "mercadolibre": {"mercadolibre.com", "mercadolibre.com.co", "mercadopago.com", "mercadopago.com.co"},
    "bancolombia": {"bancolombia.com", "grupobancolombia.com"}, "davivienda": {"davivienda.com"}, "daviplata": {"daviplata.com", "davivienda.com"},
    "nequi": {"nequi.com.co", "nequi.com"}, "bbva": {"bbva.com", "bbva.com.co"}, "bancodebogota": {"bancodebogota.com"},
    "github": {"github.com", "github.io", "githubusercontent.com", "githubassets.com", "github.dev"},
    "binance": {"binance.com"}, "coinbase": {"coinbase.com"}, "metamask": {"metamask.io"},
    "steam": {"steampowered.com", "steamcommunity.com"}, "epicgames": {"epicgames.com"}, "roblox": {"roblox.com"},
    "tiktok": {"tiktok.com"}, "twitter": {"twitter.com", "x.com", "t.co"}, "linkedin": {"linkedin.com", "lnkd.in"},
    "dian": {"dian.gov.co"}, "sena": {"sena.edu.co", "senasofiaplus.edu.co"}, "codigocamp": set(),
}
ACORTADORES = {"bit.ly", "tinyurl.com", "cutt.ly", "is.gd", "t.co", "rb.gy", "shorturl.at", "ow.ly", "buff.ly", "rebrand.ly", "tiny.cc",
               "s.id", "v.gd", "shrtco.de", "t.ly", "bl.ink", "short.io", "goo.su", "clck.ru", "qr.ae"}
EJECUTABLES = {"exe", "scr", "msi", "bat", "cmd", "vbs", "ps1", "hta", "jar", "apk", "dmg", "pkg", "iso", "lnk", "dll", "com", "pif", "jse", "wsf", "reg"}
TLD_RIESGO = {"zip", "mov", "top", "xyz", "click", "country", "gq", "tk", "ml", "cf", "ga", "work", "rest", "cam", "monster", "quest", "sbs", "cfd", "lol"}
PALABRAS_CEBO = ("login", "verify", "verificar", "secure", "seguro", "update", "actualizar", "account", "cuenta", "wallet", "billetera",
                 "premio", "gana", "gratis", "free", "bonus", "regalo", "password", "clave", "suspend", "bloqueo", "confirm",
                 "robux", "vbucks", "generator", "generador", "hack", "airdrop", "giveaway", "sorteo", "reembolso", "soporte")
SEGUNDO_NIVEL = {"com.co", "gov.co", "edu.co", "org.co", "net.co", "com.mx", "com.ar", "co.uk", "com.br", "com.es", "com.au", "co.jp"}
HOMOGLIFOS = str.maketrans({"а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y", "і": "i", "ј": "j", "ѕ": "s", "ԁ": "d",
                            "ɡ": "g", "һ": "h", "ӏ": "l", "ο": "o", "α": "a", "ν": "v", "τ": "t", "κ": "k", "ı": "i", "ʟ": "l", "ɑ": "a"})
CONFUSIBLES = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b", "@": "a", "$": "s", "!": "i"})

_cache = {}
_lock = threading.Lock()
_listas = {"cargadas": 0.0, "dominios": set(), "urls": set()}


def _dominio_registrado(host):
    partes = host.split(".")
    if len(partes) >= 3 and ".".join(partes[-2:]) in SEGUNDO_NIVEL:
        return ".".join(partes[-3:])
    return ".".join(partes[-2:])


def _es_de(host, dominios):
    return any(host == d or host.endswith("." + d) for d in dominios)


def _distancia(a, b, maximo=2):
    """Distancia de edición (Levenshtein) acotada: «paypa1» y «paypal» → 1."""
    if abs(len(a) - len(b)) > maximo:
        return maximo + 1
    previa = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        fila = [i]
        for j, cb in enumerate(b, 1):
            fila.append(min(previa[j] + 1, fila[j - 1] + 1, previa[j - 1] + (ca != cb)))
        if min(fila) > maximo:
            return maximo + 1
        previa = fila
    return previa[-1]


def _cargar_listas():
    """Listas negras: la local (siempre) y las descargadas con `flask actualizar-listas` (se recargan cada 10 min)."""
    if time.time() - _listas["cargadas"] < 600:
        return
    dominios, urls = set(), set()
    archivos = [LISTA_LOCAL] + (sorted(CARPETA_LISTAS.glob("*.txt")) if CARPETA_LISTAS.exists() else [])
    for archivo in archivos:
        try:
            for linea in archivo.read_text(encoding="utf-8", errors="ignore").splitlines():
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                if linea.startswith(("0.0.0.0 ", "127.0.0.1 ")):   # formato de archivo hosts
                    linea = linea.split()[1]
                if "://" in linea:
                    urls.add(linea.lower().rstrip("/"))
                else:
                    dominios.add(linea.lower().lstrip("*."))
        except OSError:
            continue
    _listas.update(cargadas=time.time(), dominios=dominios, urls=urls)


def _safe_browsing(url):
    clave = os.environ.get("SAFE_BROWSING_KEY", "").strip()
    if not clave:
        return None
    try:
        import requests
        r = requests.post(f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={clave}", timeout=6, json={
            "client": {"clientId": "codigocamp", "clientVersion": "1.0"},
            "threatInfo": {"threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                           "platformTypes": ["ANY_PLATFORM"], "threatEntryTypes": ["URL"], "threatEntries": [{"url": url}]}})
        if r.ok and r.json().get("matches"):
            tipo = r.json()["matches"][0].get("threatType", "")
            return {"MALWARE": "Google lo marca como sitio con virus", "SOCIAL_ENGINEERING": "Google lo marca como sitio de estafa (phishing)",
                    "UNWANTED_SOFTWARE": "Google lo marca por instalar programas no deseados"}.get(tipo, "Google lo marca como peligroso")
    except Exception:
        return None
    return None


def revisar_enlace(url, *, consultar_externos=True):
    """Revisa un enlace. Nunca lo guarda. Devuelve {"nivel", "motivo"}."""
    url = str(url or "").strip()[:4000]
    if not url:
        return {"nivel": "bloqueado", "motivo": "El enlace está vacío."}
    clave = hashlib.sha256(url.encode()).hexdigest()
    with _lock:
        hit = _cache.get(clave)
        if hit and time.time() - hit[0] < 600:
            return hit[1]
    r = _revisar(url, consultar_externos)
    with _lock:
        if len(_cache) > 5000:
            _cache.clear()
        _cache[clave] = (time.time(), r)
    return r


def _bloq(m):
    return {"nivel": "bloqueado", "motivo": m}


def _adv(m):
    return {"nivel": "advertencia", "motivo": m}


def _revisar(url, consultar_externos):
    if re.match(r"^\s*(javascript|data|vbscript|file|blob|filesystem|jar|ms-[a-z-]+|search-ms|ms-msdt):", url, re.I):
        return _bloq("Este tipo de enlace puede ejecutar código en tu equipo.")
    if re.match(r"^(mailto|tel):", url, re.I):
        return {"nivel": "seguro", "motivo": ""}
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url.lstrip("/")
    try:
        p = urlsplit(url)
        host = (p.hostname or "").lower().rstrip(".")
    except ValueError:
        return _bloq("El enlace está mal formado.")
    if not host:
        return _bloq("El enlace no tiene un sitio válido.")
    if p.username or "@" in (p.netloc or ""):
        return _bloq("El enlace esconde la dirección real detrás de un «@» (truco típico de estafas).")
    ruta = unquote(p.path or "").lower()
    ext = ruta.rsplit(".", 1)[-1] if "." in ruta.rsplit("/", 1)[-1] else ""

    _cargar_listas()
    sin_www = host[4:] if host.startswith("www.") else host
    if _es_de(sin_www, _listas["dominios"]) or url.lower().rstrip("/") in _listas["urls"]:
        return _bloq("Este sitio está en las listas de sitios con virus o estafas.")

    # IP en vez de nombre
    es_ip = False
    try:
        ipaddress.ip_address(host.strip("[]"))
        es_ip = True
    except ValueError:
        pass
    if es_ip and ext in EJECUTABLES:
        return _bloq("Descarga un programa directamente desde una dirección IP (forma común de repartir virus).")

    # Punycode / letras de otros alfabetos que imitan letras normales
    try:
        legible = host.encode().decode("idna") if "xn--" in host else host
    except UnicodeError:
        legible = host
    if "xn--" in host or any(ord(c) > 127 for c in legible):
        esqueleto = unicodedata.normalize("NFKD", legible.translate(HOMOGLIFOS)).encode("ascii", "ignore").decode()
        nombre = _dominio_registrado(esqueleto).split(".")[0].replace("-", "")
        if any(m in esqueleto.replace(".", "").replace("-", "") or (len(m) >= 5 and _distancia(nombre, m) <= 1) for m in MARCAS if MARCAS[m]):
            return _bloq("El nombre del sitio usa letras de otros alfabetos para imitar a una marca conocida.")
        return _adv("El nombre del sitio usa letras de otros alfabetos; revisa bien que sea el sitio que esperas.")

    # Suplantación de marcas: la marca aparece en el nombre pero el dominio no es el oficial
    registrado = _dominio_registrado(sin_www)
    base = registrado.split(".")[0]
    normal = base.translate(CONFUSIBLES).replace("-", "")
    etiquetas = [e.translate(CONFUSIBLES) for e in re.split(r"[.-]", sin_www)]
    partes_base = base.translate(CONFUSIBLES).split("-")
    for marca, oficiales in MARCAS.items():
        if not oficiales or _es_de(sin_www, oficiales):
            continue
        if normal == marca and base != marca:   # g00gle, paypa1, micr0soft…
            return _bloq(f"El nombre «{registrado}» cambia letras por números para imitar a {marca.capitalize()}.")
        if marca in partes_base and len(partes_base) > 1:   # bancolombia-seguro.top, secure-paypal.com
            return _bloq(f"El sitio se hace pasar por {marca.capitalize()} pero no es su dirección oficial.")
        if normal.startswith(marca) and normal != marca and any(normal[len(marca):].startswith(w) for w in PALABRAS_CEBO):
            return _bloq(f"El sitio se hace pasar por {marca.capitalize()} pero no es su dirección oficial.")
        if len(marca) >= 6 and normal != marca and _distancia(normal, marca) == 1:
            return _bloq(f"El nombre «{registrado}» se parece mucho a {marca.capitalize()} (imitación para engañar).")
        if marca in etiquetas[:-2] and any(w in sin_www + ruta for w in PALABRAS_CEBO):
            return _bloq(f"El enlace usa el nombre de {marca.capitalize()} en un sitio que no es el suyo para pedir datos.")

    # Un dominio «escondido» dentro de otro: login-microsoftonline.com.evil.ru, paypal.com.cuenta.top…
    sub = sin_www[: -len(registrado)].rstrip(".") if sin_www.endswith(registrado) else ""
    sub_etiquetas = [e.translate(CONFUSIBLES) for e in re.split(r"[.-]", sub)] if sub else []
    if sub and set(sub_etiquetas) & {"com", "net", "org", "co", "gov", "edu"}:
        unido = sub.translate(CONFUSIBLES).replace("-", "").replace(".", "")
        if any(m in unido for m in MARCAS if MARCAS[m] and len(m) >= 4):
            return _bloq(f"El enlace imita una dirección oficial, pero en realidad lleva a «{registrado}».")
        return _adv(f"El enlace parece otra dirección, pero en realidad lleva a «{registrado}».")

    tld = sin_www.rsplit(".", 1)[-1]
    if tld in TLD_RIESGO and sum(w in sin_www + ruta for w in PALABRAS_CEBO) >= 2:
        return _bloq("Es un sitio de estafa típico: dominio de alto riesgo con palabras como «gratis», «premio» o «verificar».")
    if ext in EJECUTABLES:
        if _es_de(sin_www, ACORTADORES) or tld in TLD_RIESGO:
            return _bloq("Descarga un programa desde un sitio poco confiable.")
        if re.search(r"\.(pdf|jpg|png|docx?|mp4)\.[a-z]+$", ruta):
            return _bloq("El archivo tiene doble extensión para disfrazar un programa.")
    if consultar_externos:
        motivo = _safe_browsing(url)
        if motivo:
            return _bloq(motivo + ".")
    if _es_de(sin_www, ACORTADORES):
        return _adv("Es un enlace acortado: no se ve a dónde lleva realmente.")
    if ext in EJECUTABLES:
        return _adv(f"Descarga un programa (.{ext}). Ábrelo solo si confías en quien te lo envió.")
    if tld in TLD_RIESGO and any(w in sin_www + ruta for w in PALABRAS_CEBO):
        return _adv("El sitio usa un dominio muy usado en estafas y palabras como «verificar» o «premio».")
    if es_ip and p.scheme == "http" and not ipaddress.ip_address(host.strip("[]")).is_private:
        return _adv("Es una dirección IP sin conexión segura (http).")
    return {"nivel": "seguro", "motivo": ""}


def enlaces_en(texto):
    """Enlaces que aparecen en un texto (comandos de la terminal, mensajes…)."""
    return re.findall(r"(?:https?://|www\.)[^\s'\"<>`|;]+", str(texto or ""), re.I)
