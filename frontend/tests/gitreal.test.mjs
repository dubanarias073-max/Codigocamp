// Git real (isomorphic-git) sobre el proyecto: con un servidor Git local (git http-backend) y con GitHub de verdad.
import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { spawn, execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import fsNode from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MotorGit, clasificar } from "../js/trabajo/gitreal.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const buscar = ["/tmp/ig/node_modules", path.join(aqui, "../node_modules")].find((d) => fsNode.existsSync(path.join(d, "isomorphic-git")));
const req = buscar ? createRequire(path.join(buscar, "x.js")) : null;
const git = req?.("isomorphic-git");
const http = req?.("isomorphic-git/http/node");
const sinColor = (t) => t.replace(/\x1b\[[0-9;]*m/g, "");

function cuentaFalsa() {
  const datos = new Map();
  return {
    datos,
    async subir(bytes) { const h = createHash("sha256").update(bytes).digest("hex"); datos.set(h, new Uint8Array(bytes)); return `ccbin:v1:${h}:application/octet-stream:${bytes.length}`; },
    async bytes(m) { return datos.get(m.split(":")[2]); },
  };
}

function preparar(extra = {}) {
  const raiz = fsNode.mkdtempSync(path.join(os.tmpdir(), "ccgit-"));
  const cuenta = cuentaFalsa();
  let t = 1_763_560_000_000;
  const motor = new MotorGit({ git, fs: fsNode, http, raiz: path.join(raiz, "w"), corsProxy: null, archivos: cuenta, autor: () => ({ name: "Cristian", email: "cristian@example.com" }), ahora: () => new Date((t += 60_000)), ...extra });
  const py = normalizarProyecto({ files: {}, folders: [] });
  const correr = async (linea, { cwd = "", lineas = [] } = {}) => {
    let salida = "", errores = "", cambios = 0;
    const args = linea.match(/"[^"]*"|'[^']*'|\S+/g).map((x) => x.replace(/^["']|["']$/g, "")).slice(1);
    const codigo = await motor.ejecutar(args, { py, cwd, out: (s) => { salida += s; }, err: (s) => { errores += s; }, leerLinea: async () => lineas.shift() ?? null, cambio: () => { cambios++; } });
    return { codigo, salida: sinColor(salida), errores: sinColor(errores), cambios };
  };
  return { raiz, motor, py, correr, cuenta, limpiar: () => fsNode.rmSync(raiz, { recursive: true, force: true }) };
}

test("clasificar statusMatrix como git status", () => {
  assert.deepEqual(clasificar(["a", 0, 2, 0]), { preparado: null, sinPreparar: "sin" });
  assert.deepEqual(clasificar(["a", 0, 2, 2]), { preparado: "nuevo", sinPreparar: null });
  assert.deepEqual(clasificar(["a", 0, 2, 3]), { preparado: "nuevo", sinPreparar: "modificado" });
  assert.deepEqual(clasificar(["a", 1, 2, 1]), { preparado: null, sinPreparar: "modificado" });
  assert.deepEqual(clasificar(["a", 1, 2, 2]), { preparado: "modificado", sinPreparar: null });
  assert.deepEqual(clasificar(["a", 1, 0, 1]), { preparado: null, sinPreparar: "eliminado" });
  assert.deepEqual(clasificar(["a", 1, 0, 0]), { preparado: "eliminado", sinPreparar: null });
  assert.deepEqual(clasificar(["a", 1, 1, 0]), { preparado: "eliminado", sinPreparar: "sin" });
  assert.deepEqual(clasificar(["a", 1, 1, 1]), { preparado: null, sinPreparar: null });
});

test("flujo local completo: init, add, commit, ramas, merge, conflicto, stash, reset, revert, tag, log", { skip: !git && "falta isomorphic-git" }, async () => {
  const { py, correr, limpiar } = preparar();
  try {
    let r = await correr("git status");
    assert.equal(r.codigo, 128);
    assert.match(r.errores, /not a git repository/);
    r = await correr("git init");
    assert.match(r.salida, /Initialized empty Git repository/);
    py.files["index.html"] = "<h1>Hola</h1>\n";
    py.files["css/estilos.css"] = "body { color: red; }\n";
    py.folders.push("css");
    r = await correr("git status");
    assert.match(r.salida, /On branch main\n\nNo commits yet/);
    assert.match(r.salida, /Untracked files:[\s\S]*index\.html/);
    await correr("git add .");
    r = await correr("git status -s");
    assert.equal(r.salida, "A  css/estilos.css\nA  index.html\n");
    r = await correr('git commit -m "Primer commit"');
    assert.match(r.salida, /\[main \(root-commit\) [0-9a-f]{7}\] Primer commit\n 2 files changed, 2 insertions\(\+\), 0 deletions\(-\)/);
    r = await correr("git status");
    assert.match(r.salida, /nothing to commit, working tree clean/);

    // rama nueva con un cambio
    r = await correr("git switch -c estilos");
    assert.match(r.salida, /Switched to a new branch 'estilos'/);
    py.files["css/estilos.css"] = "body { color: blue; }\n";
    r = await correr("git diff");
    assert.match(r.salida, /-body \{ color: red; \}\n\+body \{ color: blue; \}/);
    r = await correr('git commit -am "Azul"');
    assert.equal(r.codigo, 0, r.errores);
    r = await correr("git checkout main");
    assert.match(r.salida, /Switched to branch 'main'/);
    assert.equal(py.files["css/estilos.css"], "body { color: red; }\n", "el checkout cambió el archivo en el proyecto");
    r = await correr("git merge estilos");
    assert.match(r.salida, /Fast-forward/);
    assert.equal(py.files["css/estilos.css"], "body { color: blue; }\n");

    // conflicto
    await correr("git switch -c otra");
    py.files["index.html"] = "<h1>Hola desde otra</h1>\n";
    await correr('git commit -am "Otra"');
    await correr("git switch main");
    py.files["index.html"] = "<h1>Hola desde main</h1>\n";
    await correr('git commit -am "Main"');
    r = await correr("git merge otra");
    assert.equal(r.codigo, 1);
    assert.match(r.salida, /CONFLICT \(content\): Merge conflict in index\.html/);
    assert.match(py.files["index.html"], /<<<<<<< main\n<h1>Hola desde main<\/h1>\n=======\n<h1>Hola desde otra<\/h1>\n>>>>>>> /);
    r = await correr('git commit -m "Unir"');
    assert.match(r.errores, /unmerged files/);
    py.files["index.html"] = "<h1>Hola de los dos</h1>\n";
    await correr("git add index.html");
    r = await correr('git commit -m "Unir otra"');
    assert.equal(r.codigo, 0, r.errores);
    r = await correr("git log --oneline");
    assert.match(r.salida, /^[0-9a-f]{7} \(HEAD -> main\) Unir otra\n/);
    assert.equal(r.salida.trim().split("\n").length, 5);
    r = await correr("git show HEAD --no-patch");
    assert.match(r.salida, /Author: Cristian <cristian@example\.com>/);
    r = await correr("git log -n 1");
    assert.match(r.salida, /Merge: [0-9a-f]{7} [0-9a-f]{7}/);

    // stash
    py.files["index.html"] = "<h1>a medias</h1>\n";
    r = await correr("git stash");
    assert.match(r.salida, /Saved working directory/, r.errores);
    assert.equal(py.files["index.html"], "<h1>Hola de los dos</h1>\n");
    await correr("git stash pop");
    assert.equal(py.files["index.html"], "<h1>a medias</h1>\n");
    await correr("git restore index.html");
    assert.equal(py.files["index.html"], "<h1>Hola de los dos</h1>\n");

    // reset y revert
    py.files["nuevo.txt"] = "x\n";
    await correr("git add nuevo.txt");
    await correr('git commit -m "Nuevo archivo"');
    r = await correr("git revert HEAD");
    assert.match(r.salida, /Revert "Nuevo archivo"/);
    assert.equal(py.files["nuevo.txt"], undefined, "revert quitó el archivo");
    r = await correr("git reset --hard HEAD~1");
    assert.match(r.salida, /HEAD is now at [0-9a-f]{7} Nuevo archivo/);
    assert.equal(py.files["nuevo.txt"], "x\n");
    await correr('git tag -a v1.0 -m "Versión 1"');
    r = await correr("git log --oneline -n 1");
    assert.match(r.salida, /tag: v1\.0/);
    r = await correr("git branch");
    assert.equal(r.salida, "  estilos\n* main\n  otra\n");
    r = await correr("git branch -d otra");
    assert.match(r.salida, /Deleted branch otra/);
    r = await correr("git rebase main");
    assert.match(r.errores, /no está disponible/);
    assert.ok(py.git.repos[""].respaldo.startsWith("ccbin:"), "el historial quedó respaldado en la cuenta");
  } finally { limpiar(); }
});

test("el historial vuelve en otro dispositivo (del respaldo en la cuenta)", { skip: !git && "falta isomorphic-git" }, async () => {
  const a = preparar();
  try {
    await a.correr("git init");
    a.py.files["a.txt"] = "uno\n";
    await a.correr("git add .");
    await a.correr('git commit -m "Uno"');
    // «otro dispositivo»: otro sistema de archivos vacío, la misma cuenta y el mismo proyecto
    const b = preparar({ archivos: a.cuenta });
    b.py.files = a.py.files; b.py.git = a.py.git;
    const r = await b.correr("git log --oneline");
    assert.match(r.salida, /recuperado de tu cuenta/);
    assert.match(r.salida, /Uno/);
    const s = await b.correr("git status");
    assert.match(s.salida, /working tree clean/);
    b.limpiar();
  } finally { a.limpiar(); }
});

test("binarios: se versionan con sus bytes reales y vuelven como archivo de la cuenta", { skip: !git && "falta isomorphic-git" }, async () => {
  const { py, correr, cuenta, limpiar } = preparar();
  try {
    const png = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0, 1, 2, 3, 255]);
    py.files["logo.png"] = await cuenta.subir(png);
    await correr("git init");
    await correr("git add .");
    await correr('git commit -m "Logo"');
    const png2 = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 9, 9]);
    py.files["logo.png"] = await cuenta.subir(png2);
    let r = await correr("git status -s");
    assert.equal(r.salida, " M logo.png\n");
    r = await correr("git diff");
    assert.match(r.salida, /Binary files a\/logo\.png and b\/logo\.png differ/);
    await correr("git restore logo.png");
    assert.deepEqual([...(await cuenta.bytes(py.files["logo.png"]))], [...png]);
  } finally { limpiar(); }
});

// ---- remoto: servidor Git local con git http-backend ----
async function servidorGit() {
  const dir = fsNode.mkdtempSync(path.join(os.tmpdir(), "ccsrv-"));
  execFileSync("git", ["init", "--bare", "-q", "-b", "main", path.join(dir, "repo.git")]);
  execFileSync("git", ["-C", path.join(dir, "repo.git"), "config", "http.receivepack", "true"]);
  const puerto = 8790 + Math.floor(Math.random() * 50);
  const proc = spawn("python3", [path.join(aqui, "apoyo/servidor_git.py"), dir, String(puerto)], { stdio: ["ignore", "pipe", "inherit"] });
  await new Promise((ok) => proc.stdout.on("data", (d) => String(d).includes("listo") && ok()));
  return { url: `http://127.0.0.1:${puerto}/repo.git`, dir, cerrar: () => { proc.kill(); fsNode.rmSync(dir, { recursive: true, force: true }); } };
}

test("push, clone y pull con un servidor Git (como GitHub)", { skip: !git && "falta isomorphic-git" }, async () => {
  const srv = await servidorGit();
  const a = preparar(), b = preparar();
  try {
    await a.correr("git init");
    a.py.files["README.md"] = "# Finanbot\n";
    await a.correr("git add .");
    await a.correr('git commit -m "Inicio"');
    // Las URLs de remoto deben ser https:// en CódigoCamp; en la prueba se agrega por la API.
    await git.addRemote({ fs: fsNode, dir: a.motor.dirFs(""), remote: "origin", url: srv.url });
    let r = await a.correr("git push -u origin main", { lineas: ["token-de-prueba"] });
    assert.equal(r.codigo, 0, r.errores);
    assert.match(r.salida, /main -> main/);
    assert.match(execFileSync("git", ["-C", path.join(srv.dir, "repo.git"), "log", "--oneline"], { encoding: "utf8" }), /Inicio/);
    // clonar en otro «dispositivo» (con la URL http del servidor local, por la API para saltar la regla https)
    r = await b.correr(`git clone ${srv.url.replace("http://", "https://")} finan`);
    assert.equal(r.codigo, 128, "con https al servidor local falla (no hay TLS) y lo dice");
    assert.match(r.errores, /fatal:/);
    await git.clone({ fs: fsNode, http, dir: b.motor.dirFs("finan"), url: srv.url });
    b.py.git.repos = { finan: { remote: srv.url, respaldo: "", rama: "main" } };
    await b.motor.desdeGit(b.py, "finan");
    assert.equal(b.py.files["finan/README.md"], "# Finanbot\n");
    b.py.files["finan/README.md"] = "# Finanbot\n\nChatbot de finanzas.\n";
    r = await b.correr('git commit -am "Descripción"', { cwd: "finan" });
    assert.equal(r.codigo, 0, r.errores);
    r = await b.correr("git status", { cwd: "finan" });
    assert.match(r.salida, /ahead of 'origin\/main' by 1 commit/);
    r = await b.correr("git push", { cwd: "finan", lineas: ["tok"] });
    assert.equal(r.codigo, 0, r.errores);
    // el primero hace pull
    r = await a.correr("git pull");
    assert.equal(r.codigo, 0, r.errores);
    assert.match(r.salida, /Fast-forward/);
    assert.equal(a.py.files["README.md"], "# Finanbot\n\nChatbot de finanzas.\n");
    // push rechazado si el remoto tiene trabajo nuevo
    a.py.files["a.txt"] = "a\n"; await a.correr("git add ."); await a.correr('git commit -m "A"'); await a.correr("git push");
    b.py.files["finan/b.txt"] = "b\n"; await b.correr("git add .", { cwd: "finan" }); await b.correr('git commit -m "B"', { cwd: "finan" });
    r = await b.correr("git push", { cwd: "finan" });
    assert.equal(r.codigo, 1);
    assert.match(r.errores, /git pull/);
    r = await b.correr("git pull", { cwd: "finan" });
    assert.equal(r.codigo, 0, r.errores);
    assert.match(r.salida, /Merge made/);
    assert.equal(b.py.files["finan/a.txt"], "a\n");
    r = await b.correr("git push", { cwd: "finan" });
    assert.equal(r.codigo, 0, r.errores);
    r = await b.correr("git log --oneline --graph", { cwd: "finan" });
    assert.match(r.salida, /\* [0-9a-f]{7} \(HEAD -> main, origin\/main\) Merge/);
  } finally { a.limpiar(); b.limpiar(); srv.cerrar(); }
});

test("REAL: git clone de GitHub con todo el historial (Finanbot)", { skip: (!git || process.env.SIN_RED) && "sin red o sin isomorphic-git", timeout: 180_000 }, async () => {
  const { py, correr, limpiar } = preparar();
  try {
    const r = await correr("git clone https://github.com/dubanarias073-max/Finanbot.git");
    assert.equal(r.codigo, 0, r.errores);
    assert.match(r.salida, /Cloning into 'Finanbot'/);
    const n = Number(/(\d+) commits/.exec(r.salida)?.[1]);
    assert.ok(n > 20, `trae el historial completo (${n} commits)`);
    assert.ok(py.files["Finanbot/Mysql(base de datos)/finanbot_db.sql"], "nombres reales, sin renombrar");
    assert.ok(Object.keys(py.files).some((f) => f.endsWith(".png") && py.files[f].startsWith("ccbin:")), "las imágenes llegan como archivos de la cuenta");
    const log = await correr("git log --oneline", { cwd: "Finanbot" });
    assert.equal(log.salida.trim().split("\n").length, n);
    const st = await correr("git status", { cwd: "Finanbot/frontend" });
    assert.match(st.salida, /up to date with 'origin\/main'[\s\S]*working tree clean/);
  } finally { limpiar(); }
});
