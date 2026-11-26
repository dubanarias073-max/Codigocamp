"""Detector de CÓDIGO malicioso: revisa el código que se ejecuta en el SERVIDOR de CódigoCamp (compiladores de /api/run,
Python con pip, PHP real, Docker) y los archivos de código que se suben.

El antivirus (servicios/antivirus.py) mira archivos binarios; los comandos de la terminal los revisa
servicios/comandos_peligrosos.py. Esto revisa el TEXTO de un programa buscando lo que solo hace un programa dañino:
  · control remoto del servidor (shell reverso: un socket conectado a una shell)
  · minar criptomonedas
  · robar claves y secretos (/etc/shadow, llaves SSH, la configuración .env y las claves de CódigoCamp)
  · secuestro de datos (cifrar archivos en masa y borrar los originales)
  · registrador de teclas (keylogger)
  · bomba fork (crear procesos sin fin para tumbar el servidor)
  · borrar el disco o la carpeta personal
  · ejecutar código escondido (base64, zlib o marshal dentro de exec/eval)
  · comandos peligrosos escritos dentro del programa (os.system("rm -rf /"), etc.)

Está pensado para NO molestar a quien aprende: un socket, un bucle, leer variables de entorno o cifrar un texto son
normales; solo se bloquean las COMBINACIONES que únicamente usa un programa dañino.
"""
import re

_F = re.I | re.S
MAX_REVISAR = 400_000


def _r(p):
    return re.compile(p, _F)


# (función que decide, gravedad, motivo, explicación)
SECRETOS_CC = _r(r"\b(?:ADMIN_CLAVE|SMTP_APP_PASSWORD|SAFE_BROWSING_KEY)\b")   # nombres propios de CódigoCamp (SECRET_KEY o GEMINI_API_KEY son normales en una app propia)
ARCHIVOS_SECRETOS = _r(r"/etc/shadow|/etc/sudoers|/proc/(?:self|1|\d+)/environ|\.ssh/id_(?:rsa|dsa|ecdsa|ed25519)(?![\w.]*\.pub)|\.aws/credentials|\.git-credentials|\.docker/config\.json|wallet\.dat|Login Data|(?:\.\./)+(?:backend/)?\.env\b")
MINERO = _r(r"stratum\+(?:tcp|ssl)://|\bxmrig\b|\bcoinhive\b|\bcryptonight\b|\bminexmr\b|\bnicehash\b|\bnanopool\b|\bsupportxmr\b|\bcpuminer\b|\bminerd\b")
SOCKET = _r(r"\bsocket\s*\.\s*socket\s*\(|\bnew\s+Socket\s*\(|\bfsockopen\s*\(|\bTCPSocket\s*\.\s*(?:new|open)|\bnet\s*\.\s*(?:Dial|connect|createConnection)\s*\(|\bconnect\s*\(\s*\w+\s*,\s*\(?\s*struct\s+sockaddr|\bsocket\s*\(\s*AF_INET")
CONECTA = _r(r"\.connect\s*\(|\bconnect\s*\(|new\s+Socket\s*\(\s*\"|fsockopen\s*\(|TCPSocket\s*\.\s*(?:new|open)|net\s*\.\s*Dial|createConnection\s*\(")
SHELL_REMOTA = _r(r"\bdup2\s*\(|pty\s*\.\s*spawn\s*\(|[\"'](?:/bin/(?:ba|z|da)?sh|cmd(?:\.exe)?|powershell(?:\.exe)?)[\"']|\b(?:Runtime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec|ProcessBuilder)\s*\([^)]*(?:/bin/|cmd|powershell)|\bproc_open\s*\(|\bshell_exec\s*\(|\bpassthru\s*\(")
TECLAS = _r(r"pynput\s*\.\s*keyboard|from\s+pynput\s+import\s+keyboard|\bGetAsyncKeyState\b|\bSetWindowsHookEx(?:A|W)?\b|\bkeyboard\s*\.\s*(?:on_press|hook)\s*\(|WH_KEYBOARD_LL")
# Leer de verdad un archivo (no solo nombrarlo en un comentario, un texto de ayuda o una lista de archivos a ignorar)
LECTURA = _r(r"\b(?:open|read_text|read_bytes|readFile|readFileSync|createReadStream|file_get_contents|fopen|file|sqlite3\s*\.\s*connect|connect|"
             r"shutil\s*\.\s*copy\w*|Files\s*\.\s*read\w*|ReadAllText|ReadAllBytes|File\s*\.\s*Open\w*|Get-Content)\s*\(|\bGet-Content\s")
LECTURA_CONSOLA = _r(r"\b(?:cat|type|more|less|head|tail|cp|copy|scp|gc|Get-Content|base64|xxd|curl\s+-F|nc)\s")
# Mandar datos a internet (para saber si lo que se lee se envía a otra persona)
ENVIA = _r(r"requests\s*\.\s*(?:post|put|get)\s*\(|urlopen\s*\(|urllib\.request|http\.client|\bfetch\s*\(|axios\s*\.|XMLHttpRequest|"
           r"Invoke-WebRequest|Invoke-RestMethod|\bcurl\b|\bwget\b|WebClient|smtplib|\bsendto\s*\(|\.send\s*\(")
CIFRA = _r(r"\bFernet\b|\bAES\s*\.\s*new\b|\bChaCha20\b|\bCipher\s*\(|\.encrypt\s*\(")
RECORRE = _r(r"\bos\s*\.\s*walk\s*\(|\.rglob\s*\(|\bglob\s*\.\s*glob\s*\([^)]*recursive\s*=\s*True|Files\s*\.\s*walk\s*\(|filepath\s*\.\s*Walk|readdirSync|walkdir")
BORRA = _r(r"\bos\s*\.\s*(?:remove|unlink)\s*\(|\.unlink\s*\(|\bshutil\s*\.\s*rmtree\s*\(|Files\s*\.\s*delete|unlinkSync|os\s*\.\s*Remove")
FORK = _r(r"(?:while\s*\(?\s*(?:True|1|true)\s*\)?\s*[:{]|for\s*\(\s*;\s*;\s*\)\s*\{?)[^\n]{0,120}\n?[^\n]{0,120}\n?[^\n]{0,120}\b(?:os\s*\.\s*)?fork\s*\(|:\s*\(\s*\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:|(?:while\s*\(?\s*(?:True|1|true)\s*\)?\s*[:{])[^\n]{0,120}\n?[^\n]{0,120}\b(?:multiprocessing\s*\.\s*Process|subprocess\s*\.\s*Popen|os\s*\.\s*spawn\w*)\s*\([^\n]*\n?[^\n]{0,120}\.start\s*\(")
BORRAR_TODO = _r(r"\brmtree\s*\(\s*(?:[rRbB]?[\"'](?:/|[a-zA-Z]:\\\\?|~|/home|/root|/etc|/usr|/var|C:\\\\Windows)[\"']|os\s*\.\s*path\s*\.\s*expanduser\s*\(\s*[\"']~[\"']\s*\)|Path\s*\.\s*home\s*\(\s*\)|os\s*\.\s*environ\s*\[\s*[\"'](?:HOME|USERPROFILE)[\"']\s*\])\s*[,)]")
OCULTO = _r(r"\b(?:exec|eval|compile)\s*\(\s*(?:base64\s*\.\s*(?:b64|b32|b16|a85|b85)decode|zlib\s*\.\s*decompress|marshal\s*\.\s*loads|bytes\s*\.\s*fromhex|codecs\s*\.\s*decode\s*\([^)]*rot)|\beval\s*\(\s*(?:atob|Buffer\s*\.\s*from)\s*\(|\beval\s*\(\s*(?:base64_decode|gzinflate|str_rot13)\s*\(")
# --- Webshells y servidores que ejecutan lo que llega desde internet ---
_ENTRADA_WEB = r"(?:\$_(?:GET|POST|REQUEST|COOKIE|SERVER|FILES)\b|\breq(?:uest)?\s*\.\s*(?:query|body|params|args|form|values|cookies|headers)\b|\brequest\s*\.\s*(?:get_json|get_data)\s*\()"
WEBSHELL = _r(r"\b(?:eval|assert|system|exec|shell_exec|passthru|popen|proc_open|pcntl_exec|create_function)\s*\(\s*(?:@?\s*(?:stripslashes|base64_decode|urldecode|trim|str_rot13|gzinflate)\s*\(\s*)*@?\$_(?:GET|POST|REQUEST|COOKIE|SERVER)\b"
              r"|\$_(?:GET|POST|REQUEST|COOKIE)\s*\[[^\]]{1,40}\]\s*\(\s*\$_(?:GET|POST|REQUEST|COOKIE)"
              r"|\$(\w+)\s*=\s*\$_(?:GET|POST|REQUEST|COOKIE)\s*\[[^\]]{1,40}\]\s*;[^\n]{0,200}\$\1\s*\(\s*\$_(?:GET|POST|REQUEST|COOKIE)"
              r"|preg_replace\s*\(\s*['\"]([^'\"]).*?\2[a-df-z]*e[a-z]*['\"]\s*,")
EJECUTA_ENTRADA = _r(r"\b(?:exec|execSync|spawn|spawnSync|execFile|system|popen|Popen|run|call|check_output|getoutput|shell_exec)\s*\(\s*(?:[^\n()]{0,40}\+\s*)?" + _ENTRADA_WEB
                     + r"|\bos\s*\.\s*(?:system|popen)\s*\(\s*(?:f?[\"'][^\"'\n]*[\"']\s*[+%]\s*)?" + _ENTRADA_WEB)
# --- Robo de sesiones y contraseñas que se envían a otra persona ---
DATOS_ROBADOS = _r(r"discord(?:canary|ptb)?[\\/]+Local Storage[\\/]+leveldb|Local Storage[\\/]+leveldb|\bCryptUnprotectData\b|\bwin32crypt\b|"
                   r"(?:Chrome|Edge|Brave|Opera)[^\n'\"]{0,60}User Data[^\n'\"]{0,80}(?:Cookies|Login Data|Web Data|Local State)|"
                   r"\bLogin Data\b|\bencrypted_value\b|\bpassword_value\b|\bLocal State\b[^\n]{0,80}\bos_crypt\b|\bwallet\.dat\b|Exodus[\\/]+exodus\.wallet|"
                   r"\bImageGrab\.grab\s*\(|\bpyautogui\.screenshot\s*\(|\bgetClipboardData\s*\(|\bpyperclip\.paste\s*\(")
ENVIO_EXTERNO = _r(r"discord(?:app)?\.com/api/webhooks/|api\.telegram\.org/bot|\bsmtplib\b|\bngrok\b|pastebin\.com/api|transfer\.sh|anonfiles|"
                   r"https?://(?!(?:127|10|0)\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.|169\.254\.)(?:\d{1,3}\.){3}\d{1,3}")
# --- Persistencia: se instala para volver a arrancar solo ---
PERSISTE = _r(r"CurrentVersion[\\/]+Run(?:Once)?\b[^\n]{0,200}(?:SetValueEx|SetValue|RegSetValue|reg\s+add|New-ItemProperty|Set-ItemProperty|\.RegWrite)"
              r"|(?:SetValueEx|RegSetValue|\.RegWrite)\s*\([^\n]{0,200}CurrentVersion[\\/]+Run\b"
              r"|(?:winreg\.)?SetValueEx\s*\(\s*\w+\s*,[^\n]*\n?[^\n]*(?:\.exe|\.bat|\.vbs|\.ps1)"
              r"|Start Menu[\\/]+Programs[\\/]+Startup|shell:startup|@reboot\s|/etc/rc\.local|~/\.config/autostart/|LaunchAgents/[^\n'\"]*\.plist")
# --- Descargar y abrir un programa (dropper) ---
DESCARGA = _r(r"MSXML2\.(?:Server)?XMLHTTP|WinHttp\.WinHttpRequest|URLDownloadToFile|Net\.WebClient|DownloadFile\s*\(|DownloadString\s*\(|Invoke-WebRequest|"
              r"urllib\.request\.urlretrieve|urlretrieve\s*\(|requests\.get\s*\([^\n]*\)\s*\.content|\bwget\.download\s*\(|fetch\s*\([^\n]*\.exe")
ABRE_PROGRAMA = _r(r"WScript\.Shell|Shell\.Application|\.ShellExecute\s*\(|ADODB\.Stream|os\.startfile\s*\(|Start-Process\b|\bIEX\b|Invoke-Expression|"
                   r"subprocess\.(?:Popen|run|call)\s*\(\s*\[?\s*[^\n)]*\.exe|chmod\s*\(\s*[^\n)]*0o?7[0-7]{2}|os\.chmod\s*\([^\n)]*0o?7")
# --- Ataques de denegación de servicio (inundar a otro servidor) ---
FLOOD = _r(r"SOCK_DGRAM[\s\S]{0,300}while\s*\(?\s*(?:True|1|true)\s*\)?\s*[:{][\s\S]{0,200}\.sendto\s*\(|"
           r"while\s*\(?\s*(?:True|1|true)\s*\)?\s*[:{][\s\S]{0,120}socket\s*\.\s*socket\s*\([\s\S]{0,200}\.(?:connect|send)\s*\([\s\S]{0,80}(?:_urandom|random)|"
           r"\bslowloris\b|\bhping3?\b[^\n]*--flood|\bSYN\s*flood\b")
# --- Nota de rescate (ransomware) ---
RESCATE = _r(r"(?:tus|sus|your|all\s+your|todos\s+tus|todos\s+sus)\s+(?:archivos|ficheros|documentos|files|data|datos)[^\n.]{0,60}(?:han\s+sido|fueron|have\s+been|are|est[aá]n)\s+"
             r"(?:cifrad|encriptad|bloquead|secuestrad|encrypted|locked)")
PAGO = _r(r"\bbitcoin\b|\bBTC\b|\bmonero\b|\bXMR\b|\bbilletera\b|\bwallet\b|\brescate\b|\bransom\b|\bdescifrador\b|\bdecryptor\b|\btor\s*browser\b|\.onion\b")
# --- Formulario falso que manda contraseñas a otra persona (phishing) ---
PHISHING = _r(r"<form[^>]*action\s*=\s*['\"]?(?:https?:)?//(?:api\.telegram\.org/bot|discord(?:app)?\.com/api/webhooks|(?:\d{1,3}\.){3}\d{1,3}|[^'\"\s>]*(?:ngrok|000webhost|formsubmit|webhook\.site|requestbin|pipedream))")
CLAVE_INPUT = _r(r"<input[^>]*type\s*=\s*['\"]?password")
EJECUTOR = _r(r"(?:system|popen|Popen|exec|execSync|spawn|spawnSync|execFile|shell_exec|passthru|run|call|check_call|check_output|getoutput|startfile|ShellExecute|Run|Start-Process|Invoke-Expression)\s*\(\s*\[?\s*$|`\s*$")
# Un texto que empieza como una orden de consola («rm -rf /», «powershell -enc …»), no como una frase o una expresión regular
PARECE_ORDEN = re.compile(r"\s*(?:sudo\s+)?(?:rm|del|erase|rd|rmdir|format|shutdown|reboot|poweroff|halt|vssadmin|bcdedit|wbadmin|wmic|reg|schtasks|certutil|bitsadmin|mshta|"
                          r"regsvr32|rundll32|powershell|pwsh|cmd|bash|sh|zsh|curl|wget|nc|ncat|socat|dd|mkfs(?:\.\w+)?|shred|wipefs|chmod|chown|crontab|net|netsh|sc|cipher|"
                          r"diskpart|iex|IEX|iwr|irm|taskkill|attrib|takeown|icacls|cat|cp|scp|type|userdel|passwd|history|wevtutil|xmrig|minerd|msfvenom|mimikatz|"
                          r"Invoke-Expression|Invoke-WebRequest|Remove-Item|Set-MpPreference|Add-MpPreference|Stop-Computer|Restart-Computer)(?:\.exe)?\s+\S")   # en minúscula, como se escribe en la consola (no «Shutdown all…» en un texto)
# Y que trae argumentos de consola (opciones, rutas, tuberías…): «shutdown error: …» en un mensaje no es una orden
ARGUMENTOS = re.compile(r"\s-{1,2}\w|\s/\w|[|>&;~$%\\]|://|\s[a-zA-Z]:|\s(?:now|\+\d+|\d+)\b")
# Scripts que son órdenes de consola: se revisa cada línea como si se escribiera en la terminal
SCRIPTS_CONSOLA = {"sh", "bash", "zsh", "fish", "ksh", "command", "bat", "cmd", "ps1", "psm1", "psd1"}

TEXTOS = re.compile(r"\"\"\"(.{0,3000}?)\"\"\"|'''(.{0,3000}?)'''|\"((?:[^\"\\\n]|\\.){0,2000})\"|'((?:[^'\\\n]|\\.){0,2000})'|`([^`]{0,2000})`", re.S)

EXPLICA = {
    "remoto": "Un programa que conecta el servidor a otra computadora y le entrega una terminal («shell reversa») permite que un extraño controle CódigoCamp y los datos de todos los estudiantes.",
    "minero": "Minar criptomonedas usa la electricidad y el procesador de CódigoCamp en beneficio de otra persona y deja la plataforma lenta para todos.",
    "secretos": "Leer contraseñas del sistema, llaves privadas o las claves de configuración de CódigoCamp es un intento de robo de información.",
    "secuestro": "Cifrar archivos en masa y borrar los originales es lo que hace un virus de secuestro de datos (ransomware).",
    "teclas": "Un registrador de teclas (keylogger) espía todo lo que alguien escribe, incluidas sus contraseñas.",
    "fork": "Crear procesos sin fin (bomba fork) congela el servidor y deja a todos los estudiantes sin servicio.",
    "borrar": "Borrar el disco, el sistema o la carpeta personal destruye información de CódigoCamp o de otras personas.",
    "oculto": "Esconder código en base64, zlib o marshal y ejecutarlo es una técnica típica de virus para que nadie vea lo que hace.",
    "comando": "El programa intenta ejecutar un comando del sistema que puede dañar el servidor o robar información.",
    "webshell": "Una «webshell» deja que cualquiera, desde internet, ejecute órdenes en el servidor donde está el archivo: es la puerta trasera que usan los atacantes para tomar el control.",
    "robo": "El programa toma sesiones, contraseñas, cookies o capturas de pantalla y las envía a otra persona. Es un virus ladrón de información (stealer).",
    "persistencia": "El programa se instala para volver a arrancar solo cada vez que se prende el equipo, como hacen los virus para quedarse escondidos.",
    "descarga": "El programa descarga otro programa de internet y lo abre sin que la persona lo note: así llegan la mayoría de los virus (dropper).",
    "flood": "Inundar a otro servidor con tráfico es un ataque de denegación de servicio: es ilegal y deja sin servicio a otras personas.",
    "rescate": "Es la nota que deja un virus de secuestro de datos (ransomware) pidiendo dinero para devolver los archivos.",
    "phishing": "Es una página falsa de inicio de sesión que envía las contraseñas que escriban las personas a otro lugar (phishing).",
}


def revisar_codigo(texto, nombre=""):
    """Devuelve None si el código está bien, o {"motivo", "categoria", "gravedad", "explicacion", "fragmento"}.
    nombre (opcional): con la extensión se revisan los scripts de consola (.sh, .bat, .ps1…) línea por línea."""
    t = str(texto or "")[:MAX_REVISAR]
    if not t.strip():
        return None

    def hallazgo(categoria, gravedad, motivo, patron=None):
        frag = ""
        if patron is not None:
            m = patron.search(t)
            if m:
                ini = t.rfind("\n", 0, m.start()) + 1
                fin = t.find("\n", m.end())
                frag = t[ini:fin if fin != -1 else None].strip()[:300]
        return {"categoria": categoria, "gravedad": gravedad, "motivo": motivo, "explicacion": EXPLICA[categoria], "fragmento": frag}

    ext = str(nombre or "").lower().rsplit(".", 1)[-1] if "." in str(nombre or "") else ""
    if ext in ("md", "txt", "csv", "rst", "log"):
        if RESCATE.search(t) and PAGO.search(t):
            return hallazgo("rescate", "critica", "es una nota de rescate de un virus de secuestro de datos", RESCATE)
        return None
    if ext in SCRIPTS_CONSOLA:
        from servicios.comandos_peligrosos import revisar_comando
        for linea in t.splitlines()[:5000]:
            limpia = linea.strip()
            if not limpia or limpia.startswith(("#", "::", "REM ", "rem ", "//")) and not limpia.startswith("#!"):
                continue
            motivo = revisar_comando(limpia)
            if motivo:
                return {"categoria": "comando", "gravedad": "alta", "motivo": f"el script {motivo}", "explicacion": EXPLICA["comando"], "fragmento": limpia[:300]}
    if RESCATE.search(t) and PAGO.search(t):
        return hallazgo("rescate", "critica", "es una nota de rescate de un virus de secuestro de datos", RESCATE)
    if CLAVE_INPUT.search(t) and PHISHING.search(t):
        return hallazgo("phishing", "critica", "es una página falsa que envía las contraseñas a otra persona", PHISHING)
    if WEBSHELL.search(t):
        return hallazgo("webshell", "critica", "es una puerta trasera (webshell) que ejecuta órdenes enviadas desde internet", WEBSHELL)
    if EJECUTA_ENTRADA.search(t):
        return hallazgo("webshell", "alta", "el servidor ejecuta como comando lo que llega desde internet (puerta trasera)", EJECUTA_ENTRADA)
    if DATOS_ROBADOS.search(t) and ENVIO_EXTERNO.search(t):
        return hallazgo("robo", "critica", "el programa roba sesiones o contraseñas y las envía a otra persona", DATOS_ROBADOS)
    if PERSISTE.search(t):
        return hallazgo("persistencia", "alta", "el programa se instala para arrancar solo con el equipo (persistencia)", PERSISTE)
    if DESCARGA.search(t) and ABRE_PROGRAMA.search(t):
        return hallazgo("descarga", "critica", "el programa descarga otro programa de internet y lo ejecuta", DESCARGA)
    if FLOOD.search(t):
        return hallazgo("flood", "alta", "el programa inunda a otro servidor con tráfico (ataque de denegación de servicio)", FLOOD)
    if MINERO.search(t):
        return hallazgo("minero", "critica", "el programa intenta minar criptomonedas", MINERO)
    if SOCKET.search(t) and CONECTA.search(t) and SHELL_REMOTA.search(t):
        return hallazgo("remoto", "critica", "el programa abre un control remoto del servidor (shell reversa)", SHELL_REMOTA)
    for m in ARCHIVOS_SECRETOS.finditer(t):
        ini = t.rfind("\n", 0, m.start()) + 1
        fin = t.find("\n", m.end())
        linea = t[ini:fin if fin != -1 else None]
        cerca = t[max(ini, m.start() - 80):min(len(t), m.end() + 40)]
        lee = LECTURA.search(cerca) or (ext in SCRIPTS_CONSOLA and LECTURA_CONSOLA.search(cerca))
        if lee and not linea.lstrip().startswith(("#", "//", "*", "--")):
            return hallazgo("secretos", "critica", "el programa intenta leer contraseñas, llaves privadas o la configuración secreta", ARCHIVOS_SECRETOS)
    # Leer variables secretas es normal en una app propia (os.environ["SECRET_KEY"]); lo peligroso es mandarlas a otro lado
    if SECRETOS_CC.search(t) and re.search(r"\b(?:os\s*\.\s*(?:environ|getenv)|getenv\s*\(|process\s*\.\s*env|System\s*\.\s*getenv|\$_ENV|\$_SERVER|ENV\s*\[)", t):
        return hallazgo("secretos", "critica", "el programa intenta leer las claves secretas de CódigoCamp", SECRETOS_CC)
    if CIFRA.search(t) and RECORRE.search(t) and BORRA.search(t):
        return hallazgo("secuestro", "critica", "el programa cifra archivos en masa y borra los originales (secuestro de datos)", CIFRA)
    if TECLAS.search(t):
        return hallazgo("teclas", "alta", "el programa registra las teclas que se pulsan (keylogger)", TECLAS)
    if FORK.search(t):
        return hallazgo("fork", "alta", "el programa crea procesos sin fin (bomba fork)", FORK)
    if BORRAR_TODO.search(t):
        return hallazgo("borrar", "alta", "el programa borra el disco, el sistema o la carpeta personal", BORRAR_TODO)
    if OCULTO.search(t):
        return hallazgo("oculto", "alta", "el programa ejecuta código escondido (ofuscado)", OCULTO)
    # Comandos peligrosos escritos como texto dentro del programa: os.system("rm -rf /"), exec("format c:")…
    from servicios.comandos_peligrosos import revisar_comando
    for m in TEXTOS.finditer(t):
        cadena = next((g for g in m.groups() if g), "")
        if len(cadena) < 4:
            continue
        # Una sola palabra («SHUTDOWN» en la lista de palabras clave de un resaltador) solo cuenta si se le pasa a algo
        # que ejecuta comandos: os.system("reboot"), exec("shutdown")…
        if not EJECUTOR.search(t[max(0, m.start() - 60):m.start()]) and not (len(cadena) <= 300 and "\n" not in cadena.strip() and PARECE_ORDEN.match(cadena)
                                                                               and ARGUMENTOS.search(cadena)):
            continue
        motivo = revisar_comando(cadena)
        if motivo:
            return {"categoria": "comando", "gravedad": None, "motivo": f"el programa intenta ejecutar un comando que {motivo}",
                    "explicacion": EXPLICA["comando"], "fragmento": cadena.strip()[:300]}
    return None


def revisar_proyecto(codigo=None, archivos=None):
    """Revisa el código principal y los archivos del proyecto ({ruta|nombre, contenido}). Devuelve el primer hallazgo."""
    piezas = []
    if isinstance(codigo, str):
        piezas.append(("", codigo))
    for a in (archivos or [])[:300] if isinstance(archivos, list) else []:
        if isinstance(a, dict) and isinstance(a.get("contenido"), str):
            piezas.append((str(a.get("ruta") or a.get("nombre") or "")[:200], a["contenido"]))
    for ruta, texto in piezas:
        r = revisar_codigo(texto, ruta)
        if r:
            r["archivo"] = ruta
            return r
    return None
