"""Docker y Python con pip en el servidor: validaciones de seguridad (sin necesitar Docker ni internet)."""
import os
import subprocess

import pytest

from servicios import docker_trabajo as dk
from servicios import python_servidor as ps


@pytest.fixture
def carpeta(tmp_path, monkeypatch):
    monkeypatch.setattr(dk, "DOCKER_DIR", str(tmp_path / "dk"))
    monkeypatch.setattr(ps, "VENVS", str(tmp_path / "venvs"))
    return tmp_path


@pytest.fixture
def docker_falso(monkeypatch):
    """Simula el Docker del servidor y guarda las órdenes que recibe."""
    llamadas = []

    def falso(args, cwd, tiempo=60, entrada=""):
        llamadas.append(list(args))
        if args[:1] == ["inspect"]:
            return 0, "1\n" if args[-1] == "mio" else "2\n"
        if args[:2] == ["compose", "-p"] and "config" in args:
            return 0, os.environ.get("CC_CONF", '{"services": {"web": {"image": "x"}}}')
        return 0, "ok\n"
    monkeypatch.setattr(dk, "_docker", falso)
    monkeypatch.setattr(dk, "estado", lambda: {"activo": True, "motivo": ""})
    return llamadas


# ----------------------------------------------------------------------------- Docker ----
def test_docker_apagado_explica_como_encenderlo(monkeypatch, carpeta):
    monkeypatch.setenv("DOCKER_TRABAJO", "0")
    r = dk.ejecutar(1, ["ps"])
    assert r["error"] and "DOCKER_TRABAJO" in r["salida"]


def test_docker_sin_instalar(monkeypatch, carpeta):
    monkeypatch.setenv("DOCKER_TRABAJO", "1")
    monkeypatch.setattr(dk.shutil, "which", lambda n: None)
    assert "Docker Desktop" in dk.estado()["motivo"]


def test_produccion_apagado_por_defecto(monkeypatch):
    monkeypatch.delenv("DOCKER_TRABAJO", raising=False)
    monkeypatch.setenv("DEBUG", "0")
    monkeypatch.setattr(dk.shutil, "which", lambda n: "/usr/bin/docker")
    assert not dk.estado()["activo"]


@pytest.mark.parametrize("args", [
    ["run", "--privileged", "img"],
    ["run", "--cap-add=SYS_ADMIN", "img"],
    ["run", "--network", "host", "img"],
    ["run", "--net=host", "img"],
    ["run", "--pid=host", "img"],
    ["run", "-v", "/etc:/x", "img"],
    ["run", "-v", "/var/run/docker.sock:/var/run/docker.sock", "img"],
    ["run", "-v", "../../:/x", "img"],
    ["run", "--mount", "type=bind,source=/,target=/x", "img"],
    ["-H", "tcp://otro:2375", "ps"],
])
def test_opciones_peligrosas_bloqueadas(args, carpeta, docker_falso):
    with pytest.raises(ValueError):
        dk.ejecutar(1, args)


def test_run_agrega_etiqueta_limites_y_monta_el_proyecto(carpeta, docker_falso):
    dk.ejecutar(1, ["run", "--rm", "-it", "-v", "$(pwd):/app", "img", "python", "main.py"], "Mi App",
                [{"ruta": "main.py", "contenido": "print(1)"}])
    run = next(c for c in docker_falso if c[0] == "run")
    assert "codigocamp.usuario=1" in run and "--memory" in run and "--pids-limit" in run
    assert "-it" not in run and "-i" in run
    montaje = run[run.index("-v") + 1]
    assert montaje.endswith(":/app") and montaje.startswith(dk.carpeta(1, "Mi App"))
    assert open(os.path.join(dk.carpeta(1, "Mi App"), "main.py")).read() == "print(1)"


def test_solo_tus_contenedores(carpeta, docker_falso):
    dk.ejecutar(1, ["stop", "mio"])
    with pytest.raises(ValueError, match="No tienes"):
        dk.ejecutar(1, ["stop", "ajeno"])
    dk.ejecutar(1, ["ps", "-a"])
    assert any(c[0] == "ps" and "label=codigocamp.usuario=1" in c for c in docker_falso)


def test_compose_up_queda_en_segundo_plano_y_con_etiqueta(carpeta, docker_falso):
    dk.ejecutar(1, ["compose", "up"], "p", [{"ruta": "compose.yaml", "contenido": "services: {}"}])
    up = next(c for c in docker_falso if "up" in c)
    assert "-d" in up and "cc-u1-p" in up
    extra = up[up.index("-f", up.index("-f") + 1) + 1] if up.count("-f") > 1 else up[up.index("-f") + 1]
    assert "codigocamp.usuario" in open(extra).read()


@pytest.mark.parametrize("conf", [
    '{"services": {"w": {"privileged": true}}}',
    '{"services": {"w": {"network_mode": "host"}}}',
    '{"services": {"w": {"volumes": [{"type": "bind", "source": "/etc", "target": "/x"}]}}}',
    '{"services": {"w": {"cap_add": ["ALL"]}}}',
])
def test_compose_peligroso_bloqueado(conf, carpeta, docker_falso, monkeypatch):
    monkeypatch.setenv("CC_CONF", conf)
    with pytest.raises(ValueError):
        dk.ejecutar(1, ["compose", "up", "-d"], "p", [])


def test_sincronizar_respeta_lo_que_crean_los_contenedores(carpeta):
    d = dk.sincronizar(1, "p", [{"ruta": "a.txt", "contenido": "1"}, {"ruta": "b/c.txt", "contenido": "2"}])
    open(os.path.join(d, "datos.db"), "w").write("de un contenedor")
    dk.sincronizar(1, "p", [{"ruta": "a.txt", "contenido": "1"}])
    assert not os.path.exists(os.path.join(d, "b", "c.txt"))
    assert os.path.exists(os.path.join(d, "datos.db"))


@pytest.mark.skipif(subprocess.run(["docker", "info"], capture_output=True).returncode != 0 if dk.shutil.which("docker") else True,
                    reason="sin Docker encendido")
def test_docker_real_version(carpeta, monkeypatch):
    monkeypatch.setenv("DOCKER_TRABAJO", "1")
    r = dk.ejecutar(1, ["--version"])
    assert not r["error"] and "Docker" in r["salida"]


# ---------------------------------------------------------------- Python en servidor ----
@pytest.mark.parametrize("malo", ["https://x.com/p.whl", "-r requirements.txt", "../x", "paq; rm -rf /", "--index-url=x"])
def test_pip_rechaza_lo_que_no_es_un_paquete(malo, carpeta):
    with pytest.raises(ValueError):
        ps.instalar(1, [malo])


def test_pip_acepta_versiones_y_extras():
    for bueno in ["numpy", "opencv-python==4.10.0.84", "fastapi[standard]>=0.110,<1", "mysqlclient"]:
        assert ps.ESPEC.match(bueno), bueno


def test_python_servidor_ejecuta_con_entrada_y_modulos_locales(carpeta):
    r = ps.ejecutar(1, "src/main.py", [
        {"ruta": "src/main.py", "contenido": "import util\nn = input('Nombre: ')\nprint('Hola', n, util.doble(21))"},
        {"ruta": "src/util.py", "contenido": "def doble(x):\n    return x * 2"},
    ], "Ana")
    assert not r["error"] and "Hola Ana 42" in r["salida"] and r["donde"] == "servidor"


def test_python_servidor_rutas_peligrosas(carpeta):
    with pytest.raises(ValueError):
        ps.ejecutar(1, "../x.py", [{"ruta": "../x.py", "contenido": "print(1)"}])


def test_python_servidor_apagado(monkeypatch, carpeta):
    monkeypatch.setenv("PYTHON_SERVIDOR", "0")
    with pytest.raises(ValueError, match="desactivad"):
        ps.instalar(1, ["numpy"])


# ---------------------------------------------------------------- IA en Trabajo ----
def test_ia_quita_cercas_de_codigo():
    from rutas.tutor import sin_cercas
    assert sin_cercas("```js\nconst a = 1;\n```") == "const a = 1;"
    assert sin_cercas("```\nprint(1)\n```") == "print(1)"
    assert sin_cercas("x = 2") == "x = 2"
