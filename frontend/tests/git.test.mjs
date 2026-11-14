import test from "node:test";
import assert from "node:assert/strict";
import { ejecutarGit, diffLineas, calcularEstado } from "../js/trabajo/git.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { quitarAnsi } from "../js/trabajo/ansi.js";

let n = 0;
const opc = { usuario: "Ana", ahora: () => new Date("2026-01-02T03:04:05Z"), hash: () => (++n).toString(16).padStart(7, "0") };
const nuevo = (files = { "a.txt": "uno\n", "src/b.js": "x\n" }) => normalizarProyecto({ files });
const git = (py, linea, cwd = "") => { const r = ejecutarGit(py, linea.split(" ").filter(Boolean), { ...opc, cwd }); return { ...r, texto: quitarAnsi(r.salida) }; };

test("sin init, los comandos explican qué hacer", () => {
  const r = git(nuevo(), "status");
  assert.equal(r.error, true);
  assert.match(r.texto, /git init/);
});

test("flujo completo: init, status, add, commit, log, status limpio", () => {
  const py = nuevo();
  assert.match(git(py, "init").texto, /Inicializado/);
  let s = git(py, "status").texto;
  assert.match(s, /En la rama main/); assert.match(s, /Aún no hay commits/); assert.match(s, /Archivos sin seguimiento:\n.*\n\ta\.txt\n\tsrc\//);
  assert.equal(git(py, "add .").cambio, true);
  s = git(py, "status").texto;
  assert.match(s, /Cambios a ser confirmados:[\s\S]*archivo nuevo: a\.txt[\s\S]*archivo nuevo: src\/b\.js/);
  const c = git(py, 'commit -m hola');   // el mensaje es un solo token en esta prueba
  assert.match(c.texto, /\[main \(commit-raíz\) 0000001\] hola/);
  assert.match(git(py, "status").texto, /árbol de trabajo está limpio/);
  assert.match(git(py, "log --oneline").texto, /^0000001 \(HEAD -> main\) hola$/);
  assert.match(git(py, "log").texto, /commit 0000001 \(HEAD -> main\)\nAuthor: Ana <ana@codigocamp.local>/);
});

test("modificar, borrar y renombrar se reflejan igual que en Git", () => {
  const py = nuevo(); git(py, "init"); git(py, "add ."); git(py, "commit -m base");
  py.files["a.txt"] = "dos\n"; delete py.files["src/b.js"]; py.files["c.txt"] = "nuevo";
  const s = git(py, "status").texto;
  assert.match(s, /Cambios no preparados[\s\S]*modificado:\s+a\.txt[\s\S]*eliminado:\s+src\/b\.js/);
  assert.match(s, /Archivos sin seguimiento:\n.*\n\tc\.txt/);
  git(py, "add a.txt");
  assert.match(git(py, "status").texto, /Cambios a ser confirmados:\n.*\n\tmodificado:\s+a\.txt/);
  git(py, "add src/b.js");  // eliminado
  const c = git(py, "commit -m cambios");
  assert.match(c.texto, /2 archivos cambiados/);
  assert.equal("src/b.js" in py.git.committed, false);
  assert.equal(py.git.tracked.includes("src/b.js"), false);
});

test("add de un archivo sin cambios no lo prepara; commit sin nada preparado falla; commit -am", () => {
  const py = nuevo(); git(py, "init"); git(py, "add ."); git(py, "commit -m base");
  assert.equal(git(py, "add a.txt").cambio, false);
  assert.equal(git(py, "commit -m x").error, true);
  assert.equal(git(py, "commit").error, true, "pide mensaje");
  py.files["a.txt"] = "z";
  const r = ejecutarGit(py, ["commit", "-am", "directo"], opc);
  assert.equal(r.error, false);
  assert.equal(py.git.committed["a.txt"], "z");
});

test("restore descarta cambios y --staged saca de preparación", () => {
  const py = nuevo(); git(py, "init"); git(py, "add ."); git(py, "commit -m base");
  py.files["a.txt"] = "cambiado"; delete py.files["src/b.js"];
  assert.equal(git(py, "restore a.txt").error, false);
  assert.equal(py.files["a.txt"], "uno\n");
  git(py, "restore src/b.js"); assert.equal(py.files["src/b.js"], "x\n");
  py.files["a.txt"] = "otra"; git(py, "add a.txt");
  git(py, "restore --staged a.txt");
  assert.deepEqual(py.git.staged, []);
  assert.equal(py.files["a.txt"], "otra");
  assert.equal(git(py, "restore nada.txt").error, true);
});

test(".gitignore oculta archivos y carpetas del status y de add .", () => {
  const py = nuevo({ "a.txt": "", ".gitignore": "*.log\nnode_modules/\n/build\n# c\n", "x.log": "", "node_modules/p/i.js": "", "src/y.log": "", "build/o.js": "", "src/build/ok.js": "" });
  git(py, "init");
  const s = git(py, "status").texto;
  assert.ok(!/x\.log|node_modules|y\.log|\tbuild\//.test(s), s);
  assert.match(s, /\.gitignore/);
  git(py, "add .");
  assert.ok(!py.git.staged.some((r) => /log$|node_modules|^build\//.test(r)), py.git.staged.join());
  assert.ok(py.git.staged.includes("src/build/ok.js"), "/build solo ignora la raíz");
  assert.equal(git(py, "add x.log").error, true);
});

test("diff muestra líneas añadidas y quitadas con contexto", () => {
  const py = nuevo({ "a.txt": "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n" }); git(py, "init"); git(py, "add ."); git(py, "commit -m base");
  py.files["a.txt"] = "1\n2\n3\n4\nCINCO\n6\n7\n8\n9\n10\n";
  const d = git(py, "diff").texto;
  assert.match(d, /diff --git a\/a\.txt b\/a\.txt/);
  assert.match(d, /@@ -2,7 \+2,7 @@/);
  assert.match(d, /\n-5\n\+CINCO\n/);
  assert.equal(git(py, "diff --staged").texto, "");
  git(py, "add .");
  assert.match(git(py, "diff --staged").texto, /\+CINCO/);
  assert.deepEqual(diffLineas("a", "a").every((o) => o.op === " "), true);
});

test("ramas: crear, listar, cambiar entre ramas iguales y negarse si divergen", () => {
  const py = nuevo(); git(py, "init");
  assert.equal(git(py, "branch dev").error, true, "sin commits no hay ramas");
  git(py, "add ."); git(py, "commit -m base");
  assert.match(git(py, "switch -c feature").texto, /nueva rama 'feature'/);
  assert.equal(py.git.branch, "feature");
  assert.match(git(py, "branch").texto, /\* feature\n {2}main/);
  assert.match(git(py, "switch main").texto, /'main'/);
  git(py, "switch feature"); py.files["z"] = "1"; git(py, "add z"); git(py, "commit -m en-feature");
  const r = git(py, "switch main");
  assert.equal(r.error, true); assert.match(r.texto, /mismo commit/);
  assert.equal(git(py, "branch -d main").error, false);
  assert.equal(git(py, "branch -d feature").error, true, "no se borra la rama actual");
  assert.match(git(py, "merge main").texto, /no está disponible/);
});

test("remote y push simulado", () => {
  const py = nuevo(); git(py, "init");
  assert.equal(git(py, "push").error, true);
  assert.equal(git(py, "remote add origin https://example.com/x.git").error, true);
  assert.equal(git(py, "remote add origin https://github.com/ana/proy.git").error, false);
  assert.match(git(py, "remote -v").texto, /origin\thttps:\/\/github.com\/ana\/proy.git \(push\)/);
  assert.match(git(py, "push").texto, /aún no hay commits/);
  git(py, "add ."); git(py, "commit -m base");
  assert.match(git(py, "push -u origin main").texto, /Simulación: no se envió nada/);
});
