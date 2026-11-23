"""Comandos que la terminal «Mi equipo» (Conector) NUNCA ejecuta, aunque la persona insista.

Protege el computador o celular del estudiante (y a CódigoCamp) de: borrar el disco o el sistema, formatear,
apagar o reiniciar, desactivar el antivirus o el firewall, secuestro de datos (borrar copias de seguridad), robar
claves y contraseñas, dar control remoto del equipo a otro (reverse shell), minar criptomonedas, comandos ocultos
(PowerShell codificado) e instalar scripts desde sitios peligrosos.

El mismo filtro se aplica dos veces: en el servidor (antes de enviar la orden) y dentro del propio Conector
(codigocamp-conector.py), así que aunque alguien engañara al servidor, el equipo igual se niega.
Ninguna orden bloqueada se guarda.
"""
import re

_R = lambda p: re.compile(p, re.I | re.S)   # noqa: E731

RAIZ = r"(?:/|/\*|~|~/|~/\*|\$HOME|\$\{HOME\}|/(?:etc|usr|bin|sbin|boot|lib|lib64|var|opt|System|Library|Applications|Users|home|root|dev|proc|sys)(?:/\*?)?)"
REGLAS = [
    (_R(rf"\brm\s+(?:-[a-z]*\s+)*-[a-z]*r[a-z]*\s+(?:-[a-z-]+\s+)*(?:--no-preserve-root\s+)?[\"']?{RAIZ}[\"']?(?:\s|$|;|&|\|)"), "borra el sistema o tu carpeta personal completa"),
    (_R(r"--no-preserve-root"), "intenta borrar todo el disco"),
    (_R(r"\b(?:mkfs(?:\.\w+)?|wipefs|shred\s+.*?/dev/|fdisk\s+/dev/|parted\s+/dev/|sgdisk\s+-[zZ])"), "formatea o borra un disco"),
    (_R(r"\bdd\b[^\n]*\bof=/dev/(?!null\b|zero\b|stdout\b|stderr\b)"), "escribe directamente sobre un disco"),
    (_R(r">\s*/dev/(?:sd[a-z]|nvme\d|disk\d|hd[a-z]|mmcblk\d)"), "escribe directamente sobre un disco"),
    (_R(r"\bformat\s+[a-z]:"), "formatea una unidad de Windows"),
    (_R(r"\bdiskpart\b|\bcipher\s+/w\b|\bClear-Disk\b|\bFormat-Volume\b|\bInitialize-Disk\b"), "borra o formatea discos"),
    (_R(r"\b(?:del|erase)\s+(?:/[a-z]\s+)*[a-z]:\\(?:\*|windows|program files|users)?\s*(?:/[a-z]\s*)*$"), "borra una unidad o carpetas del sistema de Windows"),
    (_R(r"\b(?:rd|rmdir)\s+(?:/[a-z]\s+)*[a-z]:\\(?:windows|program files|users)?\s*(?:/[a-z]\s*)*$"), "borra una unidad o carpetas del sistema de Windows"),
    (_R(r"\bRemove-Item\b[^\n]*-Recurse[^\n]*(?:[a-z]:\\\s*(?:$|\s)|[a-z]:\\(?:windows|program files|users)\b|\$env:(?:USERPROFILE|SystemRoot|windir)|~[\\/]?\s*(?:$|\s))"), "borra carpetas del sistema o tu carpeta personal"),
    (_R(r":\s*\(\s*\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"), "es una «bomba fork» que congela el equipo"),
    (_R(r"(?:^|[;&|]\s*|\bsudo\s+)(?:shutdown|reboot|poweroff|halt|init\s+[06]|systemctl\s+(?:poweroff|reboot|halt))\b|\b(?:Stop|Restart)-Computer\b"), "apaga o reinicia el equipo"),
    (_R(rf"\bch(?:mod|own)\s+(?:-[a-z]*R[a-z]*\s+)\S*\s+{RAIZ}(?:\s|$)"), "cambia los permisos de todo el sistema"),
    (_R(r"Set-MpPreference[^\n]*-Disable|Add-MpPreference[^\n]*-Exclusion|\bsc(?:\.exe)?\s+(?:stop|delete|config)\s+(?:windefend|wdnissvc|sense|mpssvc)\b|netsh\s+(?:advfirewall|firewall)\s+set[^\n]*\boff\b|\bufw\s+disable\b|\bsetenforce\s+0\b|\bspctl\s+--master-disable\b|\bcsrutil\s+disable\b"), "desactiva el antivirus o el firewall"),
    (_R(r"\bvssadmin\b[^\n]*delete|\bwmic\s+shadowcopy\s+delete|\bwbadmin\s+delete|\bbcdedit\b|\breg(?:\.exe)?\s+delete\s+HKLM|\btmutil\s+(?:delete|disable)"), "borra copias de seguridad o la configuración de arranque (típico de virus de secuestro)"),
    (_R(r"/etc/shadow|\bmimikatz\b|\blsass(?:\.exe|\.dmp)?\b|\breg(?:\.exe)?\s+save\s+HKLM\\(?:SAM|SECURITY|SYSTEM)|Login Data\b|\bkeychain\b.*dump|\bsecurity\s+dump-keychain|~/\.ssh/id_(?:rsa|dsa|ecdsa|ed25519)(?![\w.]*\.pub)\b|\.aws/credentials|\.docker/config\.json|\.git-credentials"), "intenta leer contraseñas o claves privadas"),
    (_R(r"/dev/tcp/|\bnc(?:at)?\b[^\n]*\s-[a-z]*[ec]\s|\bsocat\b[^\n]*exec:|\bbash\s+-i\b[^\n]*[<>]&|\bpowershell\b[^\n]*Net\.Sockets\.TCPClient|\bmsfvenom\b|\bmeterpreter\b"), "abre un control remoto de tu equipo para otra persona"),
    (_R(r"\b(?:xmrig|minerd|cpuminer|nicehash|ethminer|t-rex|lolminer|nbminer)\b"), "instala un minero de criptomonedas"),
    (_R(r"\b(?:powershell|pwsh)(?:\.exe)?\b[^\n]*\s-(?:e|en|enc|enco|encod|encode|encoded|encodedcommand)\s+[A-Za-z0-9+/=]{16,}"), "ejecuta un comando oculto (codificado)"),
    (_R(r"\bcrontab\s+-r\b|\b(?:userdel|deluser)\s+\w|\bpasswd\s+(?:-d|--delete)\b|\bnet\s+user\s+\S+\s+/(?:delete|add)\b|\bnet\s+localgroup\s+administrators\b"), "cambia o borra usuarios del equipo"),
    (_R(r"\bhistory\s+-c\b.*\brm\b|\bwevtutil\s+cl\b|\bClear-EventLog\b"), "borra los registros del sistema para ocultar rastros"),
]
# Instalar desde internet con «| sh» solo desde instaladores oficiales conocidos
INSTALADORES = ("sh.rustup.rs", "bun.sh", "deno.land", "get.docker.com", "astral.sh", "install.python-poetry.org", "get.pnpm.io",
                "raw.githubusercontent.com/nvm-sh/", "raw.githubusercontent.com/Homebrew/", "volta.sh", "fnm.vercel.app", "get.sdkman.io",
                "cli.github.com", "flutter.dev", "nodejs.org", "ollama.com", "claude.ai", "starship.rs", "tailscale.com")
TUBERIA_SHELL = _R(r"(?:curl|wget|iwr|Invoke-WebRequest|irm|Invoke-RestMethod)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z|da|k)?sh\b|(?:iwr|irm|Invoke-WebRequest|Invoke-RestMethod|DownloadString)\b[^\n]*\|\s*(?:iex|Invoke-Expression)\b|\b(?:iex|Invoke-Expression)\s*\(\s*(?:New-Object\s+Net\.WebClient|\(New-Object)")


def revisar_comando(linea):
    """Motivo (en español) por el que se bloquea el comando, o None si se puede ejecutar."""
    texto = str(linea or "")
    for patron, motivo in REGLAS:
        if patron.search(texto):
            return motivo
    if TUBERIA_SHELL.search(texto):
        urls = re.findall(r"https?://[^\s'\"|)]+", texto)
        if not urls or not all(any(i in u for i in INSTALADORES) for u in urls):
            return "descarga y ejecuta un script de internet que no es de un instalador oficial conocido"
    return None
