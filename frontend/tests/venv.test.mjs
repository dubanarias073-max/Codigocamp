import test from "node:test";
import assert from "node:assert/strict";
import { Shell } from "../js/trabajo/shell.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { quitarAnsi } from "../js/trabajo/ansi.js";

function entorno() {
  const py = normalizarProyecto({ files: { "app.py": "import requests\nprint('hola')\n" } });
  const llamadas = [];
  const global = [];
  const ejecutores = { python: async (o) => { llamadas.push({ paquetes: o.almacenPip?.leer() ?? null }); o.out("hola\n"); return 0; } };
  const paquetes = { pip: async (o) => { const alm = o.almacen ?? { leer: () => global, guardar: (l) => { global.splice(0, global.length, ...l); } };
    if (o.args[0] === "install") { alm.guardar([...alm.leer(), ...o.args.slice(1)]); o.out(`instalado ${o.args.slice(1).join(" ")}${alm.venv ? " en venv" : ""}\n`); }
    if (o.args[0] === "freeze") o.out(alm.leer().join("\n") + "\n");
    return 0; } };
  const shell = new Shell({ proyecto: () => py, cambio: () => {}, usuario: "Ana", ejecutores, paquetes });
  const sesion = shell.nuevaSesion();
  let out = "", err = "";
  sesion.out = (t) => { out += t; }; sesion.err = (t) => { err += t; };
  const sh = async (l) => { out = ""; err = ""; const codigo = await shell.ejecutar(l, sesion); return { codigo, out: quitarAnsi(out), err: quitarAnsi(err) }; };
  return { py, sh, sesion, llamadas, global };
}

test("python -m venv crea la carpeta del entorno como en tu PC", async () => {
  const { py, sh } = entorno();
  const r = await sh("python -m venv .venv");
  assert.equal(r.codigo, 0, r.err);
  for (const f of ["pyvenv.cfg", ".gitignore", "bin/activate", "bin/python", "Scripts/activate.bat", "Scripts/Activate.ps1", "lib/python3.12/site-packages/cc-requisitos.txt"]) assert.ok(`.venv/${f}` in py.files, f);
  assert.match(py.files[".venv/pyvenv.cfg"], /include-system-site-packages = false/);
  assert.equal(py.files[".venv/.gitignore"].trim().split("\n").pop(), "*");
  assert.equal((await sh("python3 -m venv .venv")).codigo, 0, "repetir no falla");
  assert.equal((await sh("virtualenv env2")).codigo, 0);
  assert.ok("env2/pyvenv.cfg" in py.files);
  assert.equal((await sh("python -m venv app.py")).codigo, 1);
});

test("activar (bash, CMD y PowerShell), pip dentro del entorno y deactivate", async () => {
  const { sh, sesion, llamadas, global, py } = entorno();
  await sh("python -m venv .venv");
  assert.equal((await sh("source .venv/bin/activate")).codigo, 0);
  assert.equal(sesion.venv, ".venv");
  assert.equal(sesion.vars.VIRTUAL_ENV, "/workspace/.venv");
  assert.equal((await sh("echo $VIRTUAL_ENV")).out, "/workspace/.venv\n");
  assert.equal((await sh("which python")).out, "/workspace/.venv/bin/python\n");
  assert.match((await sh("pip install requests==2.31.0")).out, /en venv/);
  assert.deepEqual(global, [], "no toca el Python global");
  assert.match(py.files[".venv/lib/python3.12/site-packages/cc-requisitos.txt"], /requests==2.31.0/);
  await sh("python app.py");
  assert.deepEqual(llamadas.at(-1).paquetes, ["requests==2.31.0"]);
  assert.equal((await sh("pip freeze > requirements.txt")).codigo, 0);
  assert.equal(py.files["requirements.txt"], "requests==2.31.0\n");
  assert.equal((await sh("deactivate")).codigo, 0);
  assert.equal(sesion.venv, null);
  assert.equal(sesion.vars.VIRTUAL_ENV, undefined);
  await sh("python app.py");
  assert.equal(llamadas.at(-1).paquetes, null, "sin entorno usa el global");
  assert.equal((await sh("deactivate")).codigo, 1);
  // Windows: la terminal quita las barras invertidas
  assert.equal((await sh(".venv\\Scripts\\activate")).codigo, 0);
  assert.equal(sesion.venv, ".venv");
  await sh("deactivate");
  assert.equal((await sh(".\\.venv\\Scripts\\Activate.ps1")).codigo, 0);
  assert.equal(sesion.venv, ".venv");
  assert.equal((await sh(". .venv/bin/activate")).codigo, 0);
  assert.equal((await sh("source nada/bin/activate")).codigo, 1);
});
