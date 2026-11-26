"""Comandos peligrosos que CódigoCamp no deja correr EN SU SERVIDOR: órdenes de Docker y comandos escritos dentro de los
programas que se ejecutan en el servidor (os.system("rm -rf /"), etc.; ver servicios/codigo_malicioso.py).

Detecta: borrar el disco o el sistema, formatear, apagar o reiniciar, desactivar el antivirus o el firewall, secuestro
de datos (borrar copias de seguridad), robar claves y contraseñas, control remoto (reverse shell), minar criptomonedas,
comandos ocultos (PowerShell codificado) e instalar scripts desde sitios peligrosos.

En el equipo de la persona (Conector) NO se usa: ahí los comandos corren tal cual y ella es responsable
(Términos, sección 7).
"""
import re

_R = lambda p: re.compile(p, re.I | re.S)   # noqa: E731

RAIZ = r"(?:/|/\*|~|~/|~/\*|\$HOME|\$\{HOME\}|/(?:etc|usr|bin|sbin|boot|lib|lib64|var|opt|System|Library|Applications|Users|home|root|dev|proc|sys)(?:/\*?)?)"
# Carpetas del sistema: tocarlas puede dejar el equipo sin arrancar.
SISTEMA_WIN = (r"(?:%(?:SystemRoot|windir)%|\$env:(?:SystemRoot|windir)\b|[a-z]:[\\/]+windows(?=[\\/\s\"']|$)|\bsystem32\b|\bsyswow64\b|\bwinsxs\b|"
               r"[a-z]:[\\/]+program\s*files|[a-z]:[\\/]+programdata\b|[a-z]:[\\/]+boot\b)")
SISTEMA_NIX = r"(?:^|[\s\"'=])/(?:etc|usr|bin|sbin|boot|lib|lib64|System|Library|private/etc)(?:/|\s|$|[\"'])"
VERBOS_WIN = (r"\b(?:del|erase|rd|rmdir|rm|ri|Remove-Item|move|mv|mi|Move-Item|ren|rename|rni|Rename-Item|takeown|icacls|cacls|attrib|"
              r"copy|xcopy|robocopy|cp|Copy-Item|Set-Content|Add-Content|Out-File|Clear-Content|New-Item|mklink|sfc|bcdedit|reg\s+(?:add|delete))\b")
REGLAS = [
    (_R(rf"{VERBOS_WIN}[^\n|;&]*{SISTEMA_WIN}|>\s*[\"']?{SISTEMA_WIN}"), "toca carpetas del sistema de Windows (System32, Windows, Archivos de programa)"),
    (_R(rf"(?:^|[;&|]\s*)(?:cd|chdir|pushd|sl|Set-Location|Push-Location|explorer(?:\.exe)?|start|ii|Invoke-Item)\b[^\n|;&]*{SISTEMA_WIN}"), "entra a carpetas del sistema de Windows (System32, Windows, Archivos de programa)"),
    (_R(rf"\b(?:rm|mv|shred|truncate|chmod|chown|chattr|unlink|ln\s+-sf)\b[^\n|;&]*{SISTEMA_NIX}|>\s*/(?:etc|usr|bin|sbin|boot|lib|System|Library)/"), "modifica carpetas del sistema (/etc, /usr, /bin, /boot, /System…)"),
    (_R(r"(?:^|[;&|]\s*)(?:cd|pushd)\s+[\"']?/(?:boot|System|sbin)(?:/|\s|$|[\"'])"), "entra a carpetas del sistema"),
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
    # Persistencia: el programa se instala para volver a arrancar solo
    (_R(r"\breg(?:\.exe)?\s+add\s+[\"']?HK(?:CU|LM|EY_CURRENT_USER|EY_LOCAL_MACHINE)\\Software\\Microsoft\\Windows\\CurrentVersion\\Run(?:Once)?\b"
        r"|\b(?:New|Set)-ItemProperty\b[^\n]*CurrentVersion\\Run\b|\bschtasks(?:\.exe)?\s+/create\b[^\n]*/sc\s+(?:onlogon|onstart|minute)"
        r"|Start Menu\\Programs\\Startup\\[^\n]*\.(?:exe|bat|cmd|vbs|ps1|lnk)|@reboot\s+[^\n]*(?:curl|wget|nc\b|/tmp/|python|bash)"), "se instala para arrancar solo cada vez que se prende el equipo (persistencia)"),
    # Herramientas de Windows usadas por virus para descargar y ejecutar programas sin que se note
    (_R(r"\bcertutil(?:\.exe)?\b[^\n]*-(?:urlcache|decode|decodehex)\b|\bbitsadmin(?:\.exe)?\b[^\n]*/transfer\b|\bmshta(?:\.exe)?\s+[\"']?(?:https?:|javascript:|vbscript:)"
        r"|\bregsvr32(?:\.exe)?\b[^\n]*/i:\s*https?:|\brundll32(?:\.exe)?\b[^\n]*javascript:|\bwmic\b[^\n]*process\s+call\s+create"), "usa herramientas de Windows para descargar o ejecutar programas a escondidas"),
    (_R(r"\b(?:powershell|pwsh)(?:\.exe)?\b[^\n]*-w(?:indowstyle)?\s+hidden\b[^\n]*(?:-enc|iex|Invoke-Expression|DownloadString|DownloadFile|http)"), "ejecuta PowerShell oculto que descarga código"),
    (_R(r"\b(?:curl|wget)\b[^\n]*https?://(?:\d{1,3}\.){3}\d{1,3}[^\n]*(?:&&|;)\s*(?:chmod\s+\+x|sh\s|bash\s|\./)"), "descarga un programa desde una dirección IP y lo ejecuta"),
]
# Instalar desde internet con «| sh» solo desde instaladores oficiales conocidos
INSTALADORES = ("sh.rustup.rs", "bun.sh", "deno.land", "get.docker.com", "astral.sh", "install.python-poetry.org", "get.pnpm.io",
                "raw.githubusercontent.com/nvm-sh/", "raw.githubusercontent.com/Homebrew/", "volta.sh", "fnm.vercel.app", "get.sdkman.io",
                "cli.github.com", "flutter.dev", "nodejs.org", "ollama.com", "claude.ai", "starship.rs", "tailscale.com",
                "deb.nodesource.com", "rpm.nodesource.com", "get.scoop.sh", "community.chocolatey.org", "bootstrap.pypa.io",
                "pyenv.run", "raw.githubusercontent.com/pyenv/", "raw.githubusercontent.com/ohmyzsh/", "deno.com", "get.helm.sh",
                "raw.githubusercontent.com/rbenv/", "get.rvm.io", "dot.net/v1/dotnet-install", "dotnet.microsoft.com", "sdk.cloud.google.com")
TUBERIA_SHELL = _R(r"(?:curl|wget|iwr|Invoke-WebRequest|irm|Invoke-RestMethod)\b[^\n|]*\|\s*(?:sudo\s+(?:-\S+\s+)*)?(?:(?:ba|z|da|k|fi)?sh|python[\d.]*|perl|ruby|node|php)\b|(?:iwr|irm|Invoke-WebRequest|Invoke-RestMethod|DownloadString)\b[^\n]*\|\s*(?:iex|Invoke-Expression)\b|\b(?:iex|Invoke-Expression)\s*\(\s*(?:New-Object\s+Net\.WebClient|\(New-Object)")


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
