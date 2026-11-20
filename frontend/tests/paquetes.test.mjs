import test from "node:test";
import assert from "node:assert/strict";
import { ejecutarNpm, ejecutarPip, dependenciasDe, urlDeCdn, leerPackageJson, restaurarPaquetes, instalarTolerante } from "../js/trabajo/paquetes.js";
import { decidirPorPyPI } from "../js/trabajo/disponibilidad.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { Shell } from "../js/trabajo/shell.js";
import { quitarAnsi } from "../js/trabajo/ansi.js";

const jsd = (versiones) => async (url) => {
  const m = /resolve\/npm\/(.+)@(.+)$/.exec(url); const [nombre, rango] = [m[1], decodeURIComponent(m[2])];
  if (nombre === "sinred") throw new TypeError("Failed to fetch");
  const v = versiones[nombre]; return v ? { ok: true, status: 200, json: async () => ({ version: rango === "latest" || rango.startsWith("^") ? v : rango }) } : { ok: false, status: 404, json: async () => ({}) };
};
const npm = async (py, args, extra = {}) => { let out = "", err = ""; const r = await ejecutarNpm({ args, proyecto: py, out: (t) => { out += t; }, err: (t) => { err += t; }, fetchFn: jsd({ lodash: "4.17.21", dayjs: "1.11.10", "@scope/pkg": "2.0.0" }), ...extra }); return { codigo: r, out: quitarAnsi(out), err: quitarAnsi(err) }; };

test("npm init crea package.json y no lo pisa", async () => {
  const py = normalizarProyecto({ files: {} });
  assert.equal((await npm(py, ["init", "-y"])).codigo, 0);
  assert.equal(leerPackageJson(py).name, "mi-proyecto");
  assert.match((await npm(py, ["init", "-y"])).err, /ya existe/);
});

test("npm install añade dependencias reales a package.json (resolviendo la versión) y valida nombres", async () => {
  const py = normalizarProyecto({ files: {} });
  const r = await npm(py, ["install", "lodash", "dayjs@1.11.10", "@scope/pkg"]);
  assert.equal(r.codigo, 0); assert.match(r.out, /\+ lodash@4\.17\.21/);
  assert.deepEqual(leerPackageJson(py).dependencies, { "@scope/pkg": "^2.0.0", dayjs: "^1.11.10", lodash: "^4.17.21" });
  assert.match((await npm(py, ["i", "noexiste"])).err, /No se encontró «noexiste»/);
  assert.match((await npm(py, ["i", "Mal Nombre"])).err, /no es un nombre de paquete válido/);
  assert.match((await npm(py, ["i", "https://evil.com/x.tgz"])).err, /no es un nombre/);
  assert.match((await npm(py, ["i", "sinred"])).err, /conectar con el registro/);
  assert.equal((await npm(py, ["install", "-D", "dayjs"])).codigo, 0);
  assert.ok(leerPackageJson(py).devDependencies.dayjs);
});

test("npm uninstall, ls, y package.json roto se detecta", async () => {
  const py = normalizarProyecto({ files: { "package.json": '{"name":"x","version":"1.2.3","dependencies":{"lodash":"^4.0.0"}}' } });
  assert.match((await npm(py, ["ls"])).out, /x@1\.2\.3[\s\S]*└── lodash@4\.0\.0/);
  assert.equal((await npm(py, ["uninstall", "lodash"])).codigo, 0);
  assert.deepEqual(dependenciasDe(py), {});
  py.files["package.json"] = "{roto";
  assert.match((await npm(py, ["install", "lodash"])).err, /no es un JSON válido/);
});

test("npm run / start / test ejecutan los scripts con el shell", async () => {
  const py = normalizarProyecto({ files: { "package.json": '{"name":"app","version":"2.0.0","scripts":{"dev":"node index.js","test":"echo ok"}}', "server.js": "" } });
  const ejecutadas = [];
  const ejecutar = async (l) => { ejecutadas.push(l); return 0; };
  const r = await npm(py, ["run", "dev"], { ejecutar }); assert.match(r.out, /> app@2\.0\.0 dev\n> node index\.js/);
  await npm(py, ["test"], { ejecutar }); await npm(py, ["start"], { ejecutar });
  assert.deepEqual(ejecutadas, ["node index.js", "echo ok", "node server.js"], "start sin script usa server.js como npm");
  assert.match((await npm(py, ["run", "nada"], { ejecutar })).err, /no existe el script «nada»/);
  assert.match((await npm(py, ["run"], { ejecutar })).out, /dev\n    node index\.js/);
});

test("urlDeCdn y dependenciasDe: versión fijada y subrutas", () => {
  const py = normalizarProyecto({ files: { "package.json": '{"dependencies":{"lodash":"^4.17.21","@a/b":"~1.0.0","x":"latest"}}' } });
  const d = dependenciasDe(py);
  assert.equal(urlDeCdn(d, "lodash"), "https://esm.sh/lodash@4.17.21");
  assert.equal(urlDeCdn(d, "lodash/fp"), "https://esm.sh/lodash@4.17.21/fp");
  assert.equal(urlDeCdn(d, "@a/b"), "https://esm.sh/@a/b@1.0.0");
  assert.equal(urlDeCdn(d, "x"), "https://esm.sh/x@latest");
  assert.equal(urlDeCdn(d, "otro"), null);
});

// ---- pip con un Pyodide falso ----
function pyodideFalso({ falla = {} } = {}) {
  const instalados = []; const llamadas = [];
  const pyo = {
    loadPackage: async (n) => { llamadas.push("load:" + n); },
    pyimport: () => ({
      install: async (e) => { if (falla[e]) throw new Error(falla[e]); instalados.push(e); },
      uninstall: async (n) => { const i = instalados.findIndex((x) => x.startsWith(n)); if (i < 0) throw new Error("not installed"); instalados.splice(i, 1); },
    }),
    runPython: () => JSON.stringify([["numpy", "1.26.4"], ["requests", "2.31.0"], ["micropip", "0.6"]]),
  };
  return { pyo, instalados, llamadas };
}
const memoria = () => { let l = []; return { leer: () => l, guardar: (x) => { l = x; } }; };
const pip = async (args, py, almacen, extra = {}) => { let out = "", err = ""; const codigo = await ejecutarPip({ args, proyecto: py, cwd: "", out: (t) => { out += t; }, err: (t) => { err += t; }, almacen, cargarPy: async () => py.__pyo, revisar: async () => ({ ok: true }), ...extra }); return { codigo, out: quitarAnsi(out), err: quitarAnsi(err) }; };

test("pip install instala con micropip, lo recuerda y uninstall lo quita", async () => {
  const f = pyodideFalso(); const py = normalizarProyecto({ files: {} }); py.__pyo = f.pyo; const al = memoria();
  const r = await pip(["install", "requests==2.31.0", "numpy"], py, al);
  assert.equal(r.codigo, 0); assert.deepEqual(f.instalados, ["requests==2.31.0", "numpy"]);
  assert.deepEqual(al.leer(), ["requests==2.31.0", "numpy"]);
  assert.match(r.out, /requests==2\.31\.0 instalado/);
  assert.equal((await pip(["uninstall", "numpy"], py, al)).codigo, 0);
  assert.deepEqual(al.leer(), ["requests==2.31.0"]);
});

test("pip: validación (sin URLs), -r requirements.txt, errores explicados", async () => {
  const f = pyodideFalso({ falla: { lxml: "Can't find a pure Python 3 wheel for 'lxml'" } });
  const py = normalizarProyecto({ files: { "requirements.txt": "# c\nrich==13.0\n\nflask>=2  # web\n-e .\n" } }); py.__pyo = f.pyo; const al = memoria();
  assert.match((await pip(["install", "https://evil.com/x.whl"], py, al)).err, /no es un nombre de paquete válido/);
  assert.match((await pip(["install", "../x"], py, al)).err, /no es un nombre/);
  assert.match((await pip(["install"], py, al)).err, /indica qué instalar/);
  assert.equal((await pip(["install", "-r", "requirements.txt"], py, al)).codigo, 0);
  assert.deepEqual(f.instalados, ["rich==13.0", "flask>=2"]);
  assert.match((await pip(["install", "-r", "nada.txt"], py, al)).err, /no se encontró/);
  const r = await pip(["install", "lxml"], py, al);
  assert.equal(r.codigo, 1); assert.match(r.err, /código compilado[\s\S]*numpy, pandas/);
  assert.ok(!al.leer().includes("lxml"));
  assert.match((await pip(["--version"], py, al)).out, /pip/);
  assert.match((await pip(["buscar"], py, al)).err, /orden desconocida/);
});

test("pip avisa antes si un paquete no existe para el navegador y propone alternativa", async () => {
  const f = pyodideFalso(); const py = normalizarProyecto({ files: {} }); py.__pyo = f.pyo; const al = memoria();
  const revisar = async (n) => (n === "psutil" ? { ok: false, motivo: "tiene código compilado", alternativa: "no hace falta en el navegador" } : { ok: true });
  const r = await pip(["install", "psutil", "rich"], py, al, { revisar });
  assert.equal(r.codigo, 1); assert.match(r.err, /psutil no se puede instalar[\s\S]*Alternativa: no hace falta/);
  assert.deepEqual(f.instalados, ["rich"]);   // los demás sí se instalan
  assert.match(r.out, /Resumen:.*1 instalado.*1 con error: psutil/);
});

test("pip instala por partes cuando una dependencia no existe para el navegador", async () => {
  const instalados = [];
  const install = async (e) => { if (e === "app-x" || e === "nativa") throw new Error("Can't find a pure Python 3 wheel for 'nativa'"); instalados.push(e); };
  install.callKwargs = async (e, kw) => { assert.equal(kw.deps, false); instalados.push(e + "(sin deps)"); };
  const r = await instalarTolerante({ install }, "app-x", { deps: async () => ["pura", "nativa"] });
  assert.deepEqual(instalados, ["app-x(sin deps)", "pura"]);
  assert.match(r.aviso, /sin nativa/);
  await assert.rejects(instalarTolerante({ install: async () => { throw new Error("no"); } }, "otro", { deps: async () => [] }));
});

test("decidirPorPyPI distingue Python puro de código compilado", () => {
  assert.equal(decidirPorPyPI({ urls: [{ filename: "requests-2.32.0-py3-none-any.whl" }] }).ok, true);
  assert.equal(decidirPorPyPI({ urls: [{ filename: "psutil-6.0-cp312-win_amd64.whl" }, { filename: "psutil-6.0.tar.gz" }] }).ok, false);
  assert.match(decidirPorPyPI({ urls: [{ filename: "x-1.0.tar.gz" }] }).motivo, /código fuente/);
});

test("pip list y freeze", async () => {
  const f = pyodideFalso(); const py = normalizarProyecto({ files: {} }); py.__pyo = f.pyo; const al = memoria(); al.guardar(["requests==2.31.0"]);
  assert.match((await pip(["list"], py, al)).out, /Package[\s\S]*numpy\s+1\.26\.4[\s\S]*requests\s+2\.31\.0/);
  assert.equal((await pip(["freeze"], py, al)).out, "requests==2.31.0\n");
});

test("restaurarPaquetes reinstala lo guardado una sola vez por pestaña y descarta entradas inválidas", async () => {
  const f = pyodideFalso(); let salida = "";
  await restaurarPaquetes({ pyo: f.pyo, lista: ["pkgrestaurado==1.0", "http://malo/x.whl", "../otro"], out: (t) => { salida += t; } });
  assert.deepEqual(f.instalados, ["pkgrestaurado==1.0"]);
  await restaurarPaquetes({ pyo: f.pyo, lista: ["pkgrestaurado==1.0"] });
  assert.equal(f.instalados.length, 1);
});

// ---- integración con el shell ----
test("shell: pip, python -m pip, npm, npx", async () => {
  const f = pyodideFalso(); const py = normalizarProyecto({ files: { "x.ts": "" } }); const al = memoria();
  const llamadas = [];
  const shell = new Shell({ proyecto: () => py, usuario: "Ana", ejecutores: { ts: async (c) => { llamadas.push(c.ruta); return 0; } },
    paquetes: { pip: (o) => ejecutarPip({ ...o, cargarPy: async () => f.pyo, almacen: al }), npm: (o) => ejecutarNpm({ ...o, fetchFn: jsd({ lodash: "4.17.21" }) }) } });
  const s = shell.nuevaSesion(); let out = "", err = ""; s.out = (t) => { out += t; }; s.err = (t) => { err += t; };
  assert.equal(await shell.ejecutar("pip install rich", s), 0);
  assert.equal(await shell.ejecutar("pip3 install tqdm", s), 0);
  assert.equal(await shell.ejecutar("python -m pip install attrs", s), 0, err);
  assert.deepEqual(f.instalados, ["rich", "tqdm", "attrs"]);
  assert.equal(await shell.ejecutar("npm init -y && npm install lodash && cat package.json", s), 0, err);
  assert.match(quitarAnsi(out), /"lodash": "\^4\.17\.21"/);
  assert.equal(await shell.ejecutar("npx ts-node x.ts", s), 0); assert.deepEqual(llamadas, ["x.ts"]);
  assert.equal(await shell.ejecutar("npx cowsay hola", s), 127); assert.match(quitarAnsi(err), /no se puede descargar «cowsay»/);
  assert.equal(await shell.ejecutar("python -m venv env", s), 0, "ahora sí se crean entornos virtuales");
  assert.ok("env/pyvenv.cfg" in py.files);
});
