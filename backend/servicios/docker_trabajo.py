"""Docker de verdad para la terminal de Trabajo.

Los archivos del proyecto se copian a una carpeta del servidor (DOCKER_DIR/u<id>/<proyecto>) y ahí se ejecuta
`docker …` o `docker compose …` con el Docker del servidor (Docker Desktop en tu PC, o el del servidor).

Seguridad (Docker da mucho poder sobre la máquina):
  · Cada usuario solo ve y controla SUS contenedores (etiqueta codigocamp.usuario=<id>).
  · Sin --privileged, red/pid/ipc del host, --cap-add, --device ni docker.sock.
  · Los volúmenes de carpeta solo pueden usar la carpeta del proyecto (./ o $(pwd)); los volúmenes con nombre sí.
  · Límites de memoria, CPU y procesos por contenedor, y tiempo máximo por orden.

DOCKER_TRABAJO=1 lo enciende siempre, =0 lo apaga. Por defecto («auto») solo se enciende en desarrollo
(DEBUG=1, que es lo normal al correr CódigoCamp en tu PC), porque en un servidor público sería peligroso.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import uuid

DOCKER_DIR = os.getenv("DOCKER_DIR") or os.path.join(tempfile.gettempdir(), "codigocamp_docker")
ETIQUETA = "codigocamp.usuario"
TIEMPO_LARGO = int(os.getenv("DOCKER_TIEMPO_BUILD", "900"))   # build, pull, compose up
TIEMPO_RUN = int(os.getenv("DOCKER_TIEMPO_RUN", "120"))       # docker run sin -d
TIEMPO_CORTO = 60
MAX_SALIDA = 40_000
MAX_ARCHIVOS = 600
MAX_TOTAL = 25_000_000
LIMITES_RUN = {"--memory": "1g", "--cpus": "1", "--pids-limit": "512"}

RUTA = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[\w .@()+,=-]+(?:/[\w .@()+,=-]+)*$")
NOMBRE_PROYECTO = re.compile(r"[^a-z0-9_-]+")
PROHIBIDAS = ("--privileged", "--pid", "--ipc", "--uts", "--userns", "--cap-add", "--device", "--security-opt",
              "--cgroupns", "--cgroup-parent", "--device-cgroup-rule", "--runtime", "--isolation", "--gpus")
RED_HOST = re.compile(r"^(?:--net(?:work)?)(?:=|$)")

_estado = {"t": 0.0, "ok": None, "motivo": ""}
_candados = {}
_candado_global = threading.Lock()


class ErrorDocker(ValueError):
    pass


# ------------------------------------------------------------------------------ estado ----
def estado():
    modo = os.getenv("DOCKER_TRABAJO", "auto").lower()
    if modo in ("0", "no", "false"):
        return {"activo": False, "motivo": "Docker está desactivado en este servidor (DOCKER_TRABAJO=0)."}
    if not shutil.which("docker"):
        return {"activo": False, "motivo": "Docker no está instalado en el servidor de CódigoCamp. "
                "Instala Docker Desktop (https://www.docker.com/products/docker-desktop/), ábrelo y vuelve a intentarlo."}
    if modo == "auto" and os.getenv("DEBUG", "1") != "1":
        return {"activo": False, "motivo": "Por seguridad, Docker solo se enciende solo en desarrollo. "
                "El administrador puede activarlo con DOCKER_TRABAJO=1."}
    ahora = time.monotonic()
    if _estado["ok"] is None or ahora - _estado["t"] > 20:
        try:
            r = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"], capture_output=True, timeout=10)
            _estado.update(ok=r.returncode == 0 and bool(r.stdout.strip()), t=ahora,
                           motivo="" if r.returncode == 0 else r.stderr.decode("utf-8", "replace")[-300:])
        except (OSError, subprocess.TimeoutExpired) as x:
            _estado.update(ok=False, t=ahora, motivo=str(x))
    if not _estado["ok"]:
        return {"activo": False, "motivo": "Docker está instalado pero no está encendido. Abre Docker Desktop "
                "(o inicia el servicio de Docker) y vuelve a intentarlo."}
    return {"activo": True, "motivo": ""}


# --------------------------------------------------------------------- archivos ----
def _candado(uid):
    with _candado_global:
        return _candados.setdefault(uid, threading.Lock())


def _slug(nombre):
    return (NOMBRE_PROYECTO.sub("-", str(nombre or "proyecto").lower()).strip("-") or "proyecto")[:40]


def carpeta(uid, proyecto):
    return os.path.join(DOCKER_DIR, f"u{int(uid)}", _slug(proyecto))


def sincronizar(uid, proyecto, archivos):
    """Copia los archivos del proyecto a la carpeta del servidor. Solo toca los que CódigoCamp escribió antes:
    lo que creen tus contenedores (bases de datos, logs…) se respeta."""
    d = carpeta(uid, proyecto)
    os.makedirs(d, exist_ok=True)
    manifiesto = os.path.join(os.path.dirname(d), f".{_slug(proyecto)}.json")
    try:
        with open(manifiesto, encoding="utf-8") as f:
            antes = set(json.load(f))
    except (OSError, ValueError):
        antes = set()
    ahora = {}
    total = 0
    for a in (archivos or [])[:MAX_ARCHIVOS]:
        if not isinstance(a, dict):
            continue
        r, c = a.get("ruta"), a.get("contenido")
        if not isinstance(r, str) or not isinstance(c, str) or not RUTA.match(r):
            continue
        total += len(c)
        if total > MAX_TOTAL:
            raise ErrorDocker("El proyecto es demasiado grande para enviarlo a Docker.")
        ahora[r] = c
    for r, c in ahora.items():
        destino = os.path.join(d, *r.split("/"))
        try:
            with open(destino, encoding="utf-8", newline="") as f:
                if f.read() == c:
                    continue
        except (OSError, UnicodeDecodeError):
            pass
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8", newline="") as f:
            f.write(c)
    for r in antes - set(ahora):
        try:
            os.remove(os.path.join(d, *r.split("/")))
        except OSError:
            pass
    with open(manifiesto, "w", encoding="utf-8") as f:
        json.dump(sorted(ahora), f)
    return d


# ------------------------------------------------------------------- ejecutar ----
def _env():
    env = {k: v for k, v in os.environ.items()
           if not k.upper().endswith(("KEY", "SECRET", "PASSWORD", "TOKEN")) and k.upper() != "DATABASE_URL"}
    env["DOCKER_CLI_HINTS"] = "false"
    env["BUILDKIT_PROGRESS"] = "plain"
    return env


def _docker(args, cwd, tiempo=TIEMPO_CORTO, entrada=""):
    try:
        r = subprocess.run(["docker", *args], cwd=cwd, input=(entrada or "").encode("utf-8"), capture_output=True,
                           timeout=tiempo, env=_env())
        return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, f"\nTiempo agotado ({tiempo} s)."
    except OSError as x:
        return 127, f"No se pudo ejecutar docker: {x}"


def _es_mio(uid, ref, cwd):
    codigo, texto = _docker(["inspect", "-f", "{{index .Config.Labels \"%s\"}}" % ETIQUETA, ref], cwd, 20)
    return codigo == 0 and texto.strip().splitlines()[-1:] == [str(int(uid))]


_RAIZ = threading.local()


def _volumen(valor, d):
    """-v origen:destino[:modo] → el origen solo puede ser la carpeta del proyecto o un volumen con nombre."""
    partes = valor.split(":")
    if len(partes) < 2:
        return valor                                    # volumen anónimo: -v /datos
    origen = partes[0]
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", origen):
        return valor                                    # volumen con nombre
    origen = re.sub(r"^(\$\(pwd\)|\$\{?PWD\}?|%cd%|\$\{pwd\})", ".", origen, flags=re.I)
    if origen.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", origen) or "docker.sock" in valor:
        raise ErrorDocker(f"Por seguridad, los volúmenes solo pueden usar la carpeta de tu proyecto (por ejemplo -v ./:/app o -v $(pwd):/app), no «{partes[0]}».")
    abs_ = os.path.normpath(os.path.join(d, origen))
    raiz = getattr(_RAIZ, "d", None) or d
    if abs_ != raiz and not abs_.startswith(raiz + os.sep):
        raise ErrorDocker(f"El volumen «{partes[0]}» sale de la carpeta del proyecto.")
    return ":".join([abs_, *partes[1:]])


def _revisar_opciones(args, d, permitir_volumen=True):
    """Rechaza opciones peligrosas y adapta -v/--mount. Devuelve la lista nueva."""
    out = []
    i = 0
    while i < len(args):
        a = args[i]
        base = a.split("=", 1)[0]
        if base in PROHIBIDAS:
            raise ErrorDocker(f"La opción {base} no está permitida en CódigoCamp (daría control de toda la máquina).")
        if RED_HOST.match(a):
            valor = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            if valor in ("host",) or valor.startswith("container:"):
                raise ErrorDocker("La red del host no está permitida. Usa -p 8080:80 para publicar puertos.")
        if base in ("-v", "--volume") and permitir_volumen:
            valor = a.split("=", 1)[1] if "=" in a else args[i + 1] if i + 1 < len(args) else ""
            out += ["-v", _volumen(valor, d)]
            i += 1 if "=" in a else 2
            continue
        if base == "--mount":
            valor = a.split("=", 1)[1] if "=" in a else args[i + 1] if i + 1 < len(args) else ""
            campos = dict(p.split("=", 1) for p in valor.split(",") if "=" in p)
            if campos.get("type", "volume") == "bind":
                src = campos.get("source") or campos.get("src") or ""
                campos["source"] = _volumen(f"{src}:/x", d).rsplit(":/x", 1)[0]
                campos.pop("src", None)
                valor = ",".join(f"{k}={v}" for k, v in campos.items())
            out += ["--mount", valor]
            i += 1 if "=" in a else 2
            continue
        out.append(a)
        i += 1
    return out


def _sin_tty(args):
    """La terminal de CódigoCamp no es una TTY: -it / -t se quitan (se mantiene -i para la entrada)."""
    out = []
    for a in args:
        if a in ("-t", "--tty"):
            continue
        if re.fullmatch(r"-[a-zA-Z]+", a) and "t" in a and not a.startswith("--"):
            a = a.replace("t", "")
            if a == "-":
                continue
        out.append(a)
    return out


def _primero_no_opcion(args, con_valor=()):
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("-"):
            if a in con_valor and "=" not in a:
                i += 2
                continue
            i += 1
            continue
        return i
    return None


OPC_RUN_CON_VALOR = {"-p", "--publish", "-e", "--env", "--name", "-v", "--volume", "-w", "--workdir", "--env-file",
                     "-m", "--memory", "--cpus", "--label", "-l", "--entrypoint", "-u", "--user", "--network", "--net",
                     "--mount", "--restart", "-h", "--hostname", "--pids-limit", "--platform", "--add-host", "--expose",
                     "--health-cmd", "--stop-signal", "--shm-size", "--tmpfs", "--ulimit", "--dns"}


def _run(uid, args, d, entrada):
    args = _revisar_opciones(_sin_tty(args), d)
    i = _primero_no_opcion(args, OPC_RUN_CON_VALOR)
    if i is None:
        raise ErrorDocker("Falta la imagen: docker run [opciones] imagen [comando]")
    opciones, resto = args[:i], args[i:]
    extra = ["--label", f"{ETIQUETA}={int(uid)}"]
    for k, v in LIMITES_RUN.items():
        if not any(o == k or o.startswith(k + "=") or (k == "--memory" and o == "-m") for o in opciones):
            extra += [k, v]
    separado = any(o in ("-d", "--detach") or re.fullmatch(r"-[a-zA-Z]*d[a-zA-Z]*", o) for o in opciones)
    nombre = None
    if not separado and "--name" not in opciones and not any(o.startswith("--name=") for o in opciones):
        nombre = f"cc-{int(uid)}-{uuid.uuid4().hex[:8]}"
        extra += ["--name", nombre]
    codigo, texto = _docker(["run", *extra, *opciones, *resto], d, TIEMPO_LARGO if separado else TIEMPO_RUN, entrada)
    if codigo == 124 and nombre:
        _docker(["rm", "-f", nombre], d, 30)
        texto += " Se detuvo el contenedor. Para programas que siguen corriendo (servidores) usa docker run -d."
    elif nombre and "--rm" not in opciones:
        pass  # como Docker de verdad: el contenedor parado queda en «docker ps -a»
    return codigo, texto


def _compose(uid, args, d, proyecto, entrada):
    args = _sin_tty(args)
    # Opciones globales de compose: -f archivo, --profile, --env-file. Nada de -p (lo pone CódigoCamp).
    globales, i = [], 0
    while i < len(args) and args[i].startswith("-"):
        a = args[i]
        if a in ("-p", "--project-name") or a.startswith("--project-name="):
            i += 1 if "=" in a else 2
            continue
        if a in ("-f", "--file", "--env-file", "--profile") and "=" not in a:
            v = args[i + 1] if i + 1 < len(args) else ""
            if a in ("-f", "--file", "--env-file") and not RUTA.match(v):
                raise ErrorDocker(f"Archivo no válido: {v}")
            globales += [a, v]
            i += 2
            continue
        globales.append(a)
        i += 1
    if i >= len(args):
        raise ErrorDocker("Uso: docker compose up -d | down | ps | logs | build | exec <servicio> <comando> | run …")
    sub, resto = args[i], args[i + 1:]
    nombre = f"cc-u{int(uid)}-{_slug(proyecto)}"
    base = ["compose", "-p", nombre, *globales]

    # Revisar la configuración (lo que hay en compose.yaml) antes de construir o levantar nada.
    codigo, texto = _docker([*base, "config", "--format", "json"], d, 60)
    if codigo != 0:
        return codigo, texto
    try:
        conf = json.loads(texto[texto.index("{"):])
    except ValueError:
        return 1, texto
    servicios = conf.get("services") or {}
    for n, s in servicios.items():
        if s.get("privileged"):
            raise ErrorDocker(f"El servicio «{n}» usa privileged: no está permitido.")
        for clave in ("network_mode", "pid", "ipc", "userns_mode", "uts"):
            if str(s.get(clave) or "") == "host" or str(s.get(clave) or "").startswith("container:"):
                raise ErrorDocker(f"El servicio «{n}» usa {clave}: {s.get(clave)} (no permitido). Usa ports: para publicar puertos.")
        for clave in ("cap_add", "devices", "security_opt", "device_cgroup_rules"):
            if s.get(clave):
                raise ErrorDocker(f"El servicio «{n}» usa {clave}: no está permitido.")
        for v in s.get("volumes") or []:
            if isinstance(v, dict) and v.get("type") == "bind":
                src = os.path.normpath(v.get("source") or "")
                raiz = getattr(_RAIZ, "d", None) or d
                if "docker.sock" in src or (src != raiz and not src.startswith(raiz + os.sep)):
                    raise ErrorDocker(f"El servicio «{n}» monta «{v.get('source')}»: solo se puede montar la carpeta del proyecto (./).")
    # Etiqueta y límites para cada servicio (archivo extra fuera de tu proyecto).
    extra = {"services": {n: {"labels": {ETIQUETA: str(int(uid))},
                               **({} if s.get("mem_limit") else {"mem_limit": "1g"}),
                               **({} if s.get("pids_limit") else {"pids_limit": 512})}
                          for n, s in servicios.items()}}
    principal = [x for j, x in enumerate(globales) if j > 0 and globales[j - 1] in ("-f", "--file")]
    ruta_extra = os.path.join(os.path.dirname(d), f".{_slug(proyecto)}.cc-compose.json")
    with open(ruta_extra, "w", encoding="utf-8") as f:
        json.dump(extra, f)
    archivos = []
    if not principal:
        for c in ("compose.yaml", "compose.yml", "docker-compose.yml", "docker-compose.yaml"):
            if os.path.exists(os.path.join(d, c)):
                archivos = ["-f", c]
                break
    base = ["compose", "-p", nombre, *globales, *archivos, "-f", ruta_extra]

    if sub == "up":
        resto = [a for a in resto if a not in ("--attach-dependencies",)]
        if "-d" not in resto and "--detach" not in resto:
            resto = ["-d", *resto]
            aviso = "(La terminal no se queda pegada: los servicios se levantan en segundo plano. Mira su salida con docker compose logs)\n"
        else:
            aviso = ""
        codigo, texto = _docker([*base, "up", *resto], d, TIEMPO_LARGO)
        if codigo == 0:
            time.sleep(3)
            _, logs = _docker([*base, "logs", "--tail", "25", "--no-color"], d, 30)
            texto = aviso + texto + ("\n--- últimas líneas de los servicios ---\n" + logs if logs.strip() else "")
        return codigo, texto
    if sub == "logs":
        resto = [a for a in resto if a not in ("-f", "--follow")]
        if not any(a.startswith("--tail") or a == "-n" for a in resto):
            resto = ["--tail", "200", *resto]
        return _docker([*base, "logs", "--no-color", *resto], d, 60)
    if sub in ("exec", "run"):
        resto = ["-T", *[a for a in resto if a != "-T"]]
        if sub == "run":
            resto = _revisar_opciones(resto, d)
        return _docker([*base, sub, *resto], d, TIEMPO_RUN, entrada)
    if sub in ("build", "pull", "create"):
        return _docker([*base, sub, *resto], d, TIEMPO_LARGO)
    if sub in ("down", "ps", "stop", "start", "restart", "rm", "kill", "images", "config", "top", "port", "ls", "version", "pause", "unpause"):
        if sub == "rm" and "-f" not in resto and "--force" not in resto:
            resto = ["-f", *resto]
        return _docker([*base, sub, *resto], d, TIEMPO_LARGO if sub == "down" else TIEMPO_CORTO)
    raise ErrorDocker(f"docker compose {sub} no está disponible aquí.")


CON_CONTENEDOR = {"stop", "start", "restart", "rm", "logs", "exec", "inspect", "kill", "port", "top", "pause",
                  "unpause", "stats", "cp", "rename", "wait", "attach", "diff", "commit"}


def ejecutar(uid, args, proyecto="proyecto", archivos=None, entrada="", cwd=""):
    e = estado()
    if not e["activo"]:
        return {"salida": e["motivo"] + "\n", "error": True, "puertos": []}
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        raise ErrorDocker("Orden no válida.")
    args = [a[:500] for a in args][:80]
    if not args or args[0] in ("help", "--help", "-h"):
        return {"salida": AYUDA, "error": False, "puertos": []}
    if args[0].startswith("-"):
        if args[0] in ("-v", "--version"):
            args = ["--version"]
        else:
            raise ErrorDocker(f"La opción global {args[0]} no está permitida aquí.")
    sub, resto = args[0], args[1:]
    if sub == "container" and resto:
        sub, resto = {"ls": "ps", "list": "ps"}.get(resto[0], resto[0]), resto[1:]
    elif sub == "image" and resto:
        sub, resto = {"ls": "images", "list": "images", "rm": "rmi", "build": "build", "pull": "pull", "prune": "image-prune"}.get(resto[0], "image-" + resto[0]), resto[1:]
    with _candado(uid):
        raiz = sincronizar(uid, proyecto, archivos) if archivos is not None else carpeta(uid, proyecto)
        os.makedirs(raiz, exist_ok=True)
        cwd = str(cwd or "").strip("/")
        if cwd and not RUTA.match(cwd):
            raise ErrorDocker("Carpeta de trabajo no válida.")
        d = os.path.join(raiz, *cwd.split("/")) if cwd else raiz
        os.makedirs(d, exist_ok=True)
        _RAIZ.d = raiz
        if sub == "--version" or sub == "version":
            codigo, texto = _docker(["version"] if sub == "version" else ["--version"], d)
        elif sub == "info":
            codigo, texto = _docker(["info", "--format", "Servidor Docker {{.ServerVersion}} · {{.OperatingSystem}} · {{.NCPU}} CPU · contenedores tuyos: ver docker ps -a"], d)
        elif sub == "compose":
            codigo, texto = _compose(uid, resto, d, proyecto, entrada)
        elif sub == "run":
            codigo, texto = _run(uid, resto, d, entrada)
        elif sub == "ps":
            codigo, texto = _docker(["ps", "--filter", f"label={ETIQUETA}={int(uid)}", *[a for a in resto if a.startswith("-")]], d)
        elif sub == "images":
            codigo, texto = _docker(["images", *resto], d)
        elif sub == "build":
            resto = _revisar_opciones(resto, d, permitir_volumen=False)
            for j, a in enumerate(resto):
                if not a.startswith("-") and (j == 0 or resto[j - 1] not in ("-t", "--tag", "-f", "--file", "--build-arg", "--target", "--platform", "--label")):
                    if a not in (".", "./") and not RUTA.match(a):
                        raise ErrorDocker("El contexto de construcción debe ser una carpeta de tu proyecto (por ejemplo «.»).")
            codigo, texto = _docker(["build", "--label", f"{ETIQUETA}={int(uid)}", *resto], d, TIEMPO_LARGO)
        elif sub == "pull":
            codigo, texto = _docker(["pull", *resto], d, TIEMPO_LARGO)
        elif sub == "rmi":
            codigo, texto = _docker(["rmi", *resto], d)
        elif sub in ("network", "volume"):
            if not resto or resto[0] not in ("ls", "create", "rm", "inspect", "prune"):
                raise ErrorDocker(f"Uso: docker {sub} ls | create <nombre> | rm <nombre>")
            extra = ["--label", f"{ETIQUETA}={int(uid)}"] if resto[0] == "create" else []
            filtro = ["--filter", f"label={ETIQUETA}={int(uid)}"] if resto[0] == "prune" else []
            codigo, texto = _docker([sub, resto[0], *extra, *filtro, *resto[1:]], d)
        elif sub == "system" and resto[:1] == ["df"]:
            codigo, texto = _docker(["system", "df"], d)
        elif sub in CON_CONTENEDOR:
            resto = _sin_tty(resto)
            if sub == "exec":
                resto = _revisar_opciones(resto, d, permitir_volumen=False)
            if sub == "logs":
                resto = [a for a in resto if a not in ("-f", "--follow")]
            refs = [a for a in resto if not a.startswith("-")]
            objetivos = refs[:1] if sub in ("exec", "cp", "rename", "commit", "port", "top", "attach", "diff") else refs
            if sub == "cp":
                objetivos = [r.split(":", 1)[0] for r in refs if ":" in r]
            if not objetivos:
                raise ErrorDocker(f"Uso: docker {sub} <contenedor>")
            ajenos = [r for r in objetivos if not _es_mio(uid, r, d)]
            if ajenos:
                raise ErrorDocker(f"No tienes un contenedor llamado «{ajenos[0]}». Mira los tuyos con docker ps -a.")
            if sub == "stats":
                resto = ["--no-stream", *resto]
            if sub == "rm" and any(a in ("-f", "--force") for a in resto) is False:
                pass
            codigo, texto = _docker([sub, *resto], d, TIEMPO_RUN if sub == "exec" else TIEMPO_CORTO, entrada)
        elif sub == "container-prune" or (sub == "prune"):
            codigo, texto = _docker(["container", "prune", "-f", "--filter", f"label={ETIQUETA}={int(uid)}"], d)
        else:
            raise ErrorDocker(f"docker {sub} no está disponible aquí. Prueba: build, run, ps, images, logs, exec, stop, rm, compose.")
        _, puertos_txt = _docker(["ps", "--filter", f"label={ETIQUETA}={int(uid)}", "--format", "{{.Ports}}"], d, 20)
    puertos = sorted({int(p) for p in re.findall(r"(?:0\.0\.0\.0|\[::\]|127\.0\.0\.1):(\d+)->", puertos_txt)})
    _RAIZ.d = None
    texto = texto.replace(d + os.sep, "").replace(raiz + os.sep, "/workspace/").replace(raiz, "/workspace")
    if len(texto) > MAX_SALIDA:
        texto = "… (salida recortada)\n" + texto[-MAX_SALIDA:]
    return {"salida": texto, "error": codigo != 0, "puertos": puertos}


AYUDA = """Docker en CódigoCamp (con el Docker del servidor):
  docker build -t miapp .            construye una imagen con el Dockerfile de tu proyecto
  docker run --rm miapp              ejecuta y muestra la salida
  docker run -d -p 8080:80 miapp     deja un servidor corriendo (ábrelo en http://localhost:8080)
  docker run -v ./:/app …            monta tu proyecto dentro del contenedor
  docker ps [-a] · docker images · docker logs <c> · docker exec <c> <cmd>
  docker stop <c> · docker rm <c> · docker rmi <imagen> · docker pull <imagen>
  docker compose up -d · ps · logs · exec <servicio> <cmd> · down · build
Solo ves y controlas tus contenedores. Sin --privileged ni red del host.
"""
