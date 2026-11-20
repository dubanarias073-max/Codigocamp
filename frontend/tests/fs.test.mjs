import test from "node:test";
import assert from "node:assert/strict";
import * as FS from "../js/trabajo/fs.js";

const nuevo = () => FS.normalizar({ files: { "index.html": "<h1>", "src/app.js": "x", "src/lib/util.js": "y" }, folders: ["vacia"] });

test("normalizar completa carpetas padre, descarta rutas inválidas y conflictos", () => {
  const py = FS.normalizar({
    files: { "a/b/c.txt": "1", "../evil": "x", "ok.js": "2", "mal:nombre.js": "3", "con espacio.js": "4", "a": "choca" , "__proto__": "p" },
    folders: ["z", "z/y", "../fuera"],
  });
  assert.deepEqual(Object.keys(py.files).sort(), ["a/b/c.txt", "con espacio.js", "ok.js"]);
  assert.deepEqual(py.folders, ["a", "a/b", "z", "z/y"]);
});

test("un proyecto vacío sigue vacío (no se restauran plantillas)", () => {
  const py = FS.normalizar({ files: {}, folders: [] });
  assert.deepEqual(py, { files: {}, folders: [] });
});

test("hijos separa carpetas y archivos y ordena de forma natural", () => {
  const py = FS.normalizar({ files: { "f10.js": "", "f2.js": "", "B.js": "", "src/x.js": "" }, folders: [] });
  assert.deepEqual(FS.hijos(py, ""), { dirs: ["src"], files: ["B.js", "f2.js", "f10.js"] });
  assert.deepEqual(FS.hijos(py, "src"), { dirs: [], files: ["x.js"] });
});

test("resolver maneja ., .., ~, rutas absolutas y rechaza lo que sale del proyecto", () => {
  assert.equal(FS.resolver("src", "lib"), "src/lib");
  assert.equal(FS.resolver("src/lib", ".."), "src");
  assert.equal(FS.resolver("src", "../.."), "");
  assert.equal(FS.resolver("src", "~"), "");
  assert.equal(FS.resolver("src", "~/a/b"), "a/b");
  assert.equal(FS.resolver("", "/workspace/x/y"), "x/y");
  assert.equal(FS.resolver("", "/workspace"), "");
  assert.equal(FS.resolver("", "/etc/passwd"), null);
  assert.equal(FS.resolver("", "mal:nombre"), null);
  assert.equal(FS.resolver("", "Mysql(base de datos)/a.sql"), "Mysql(base de datos)/a.sql");
  assert.equal(FS.resolver("", "__proto__"), null);
});

test("crearArchivo / crearCarpeta validan nombre, duplicados y padres", () => {
  const py = nuevo();
  assert.equal(FS.crearArchivo(py, "src/nuevo.js", "a").ok, true);
  assert.equal(FS.crearArchivo(py, "src/nuevo.js").ok, false);
  assert.equal(FS.crearArchivo(py, "no/existe/x.js").ok, false);
  assert.equal(FS.crearArchivo(py, "no/existe/x.js", "", { padres: true }).ok, true);
  assert.ok(py.folders.includes("no") && py.folders.includes("no/existe"));
  assert.equal(FS.crearArchivo(py, "index.html/hijo.txt").ok, false);
  assert.equal(FS.crearCarpeta(py, "src").ok, false);
  assert.equal(FS.crearCarpeta(py, "src", { padres: true }).creada, false);
  assert.equal(FS.crearCarpeta(py, "a/b/c", { padres: true }).ok, true);
});

test("borrar elimina archivo o carpeta completa y se puede restaurar", () => {
  const py = nuevo();
  const r = FS.borrar(py, "src");
  assert.equal(r.ok, true);
  assert.deepEqual(Object.keys(py.files), ["index.html"]);
  assert.deepEqual(py.folders, ["vacia"]);
  FS.restaurar(py, r.eliminado);
  assert.deepEqual(Object.keys(py.files).sort(), ["index.html", "src/app.js", "src/lib/util.js"]);
  assert.deepEqual(py.folders, ["src", "src/lib", "vacia"]);
  assert.equal(FS.borrar(py, "").ok, false);
  assert.equal(FS.borrar(py, "nada").ok, false);
});

test("mover renombra archivos y carpetas (con su contenido) y evita choques", () => {
  const py = nuevo();
  assert.equal(FS.mover(py, "src", "codigo").ok, true);
  assert.ok(FS.tieneArchivo(py, "codigo/app.js") && FS.tieneArchivo(py, "codigo/lib/util.js"));
  assert.ok(!FS.tieneArchivo(py, "src/app.js"));
  assert.deepEqual(py.folders, ["codigo", "codigo/lib", "vacia"]);
  assert.equal(FS.mover(py, "codigo", "codigo/lib/dentro").ok, false);
  assert.equal(FS.mover(py, "index.html", "vacia").ok, false);
  assert.equal(FS.mover(py, "index.html", "vacia/index.html").ok, true);
});

test("copiar exige -r para carpetas y respeta límites", () => {
  const py = nuevo();
  assert.equal(FS.copiar(py, "src", "copia").ok, false);
  assert.equal(FS.copiar(py, "src", "copia", { recursivo: true }).ok, true);
  assert.equal(py.files["copia/lib/util.js"], "y");
  assert.equal(FS.copiar(py, "index.html", "b.html").ok, true);
  const lleno = FS.normalizar({ files: {} });
  for (let i = 0; i < FS.LIMITES.archivos; i += 1) lleno.files[`f${i}.txt`] = "";
  assert.equal(FS.crearArchivo(lleno, "uno-mas.txt").ok, false);
});

test("escribirArchivo crea o anexa y no escribe sobre carpetas", () => {
  const py = nuevo();
  assert.equal(FS.escribirArchivo(py, "n.txt", "a").ok, true);
  assert.equal(FS.escribirArchivo(py, "n.txt", "b", { anexar: true }).ok, true);
  assert.equal(py.files["n.txt"], "ab");
  assert.equal(FS.escribirArchivo(py, "src", "x").ok, false);
  assert.equal(FS.escribirArchivo(py, "nada/x.txt", "x").ok, false);
});

test("expandirComodin devuelve coincidencias en el último tramo", () => {
  const py = FS.normalizar({ files: { "a.js": "", "b.js": "", "c.css": "", ".env": "", "src/x.js": "" } });
  assert.deepEqual(FS.expandirComodin(py, "", "*.js"), ["a.js", "b.js"]);
  assert.deepEqual(FS.expandirComodin(py, "", "src/*"), ["src/x.js"]);
  assert.deepEqual(FS.expandirComodin(py, "src", "../*.css"), ["../c.css"]);
  assert.deepEqual(FS.expandirComodin(py, "", "*.py"), []);
  assert.ok(!FS.expandirComodin(py, "", "*").includes(".env"));
});

test("errorDeNombre explica el problema", () => {
  assert.equal(FS.errorDeNombre("ok-1.js"), null);
  assert.equal(FS.errorDeNombre("con espacio (1).js"), null);
  assert.equal(FS.errorDeNombre("ñandú"), null);
  assert.match(FS.errorDeNombre("a/b"), /barras/);
  assert.match(FS.errorDeNombre("a?b"), /caracteres/);
  assert.match(FS.errorDeNombre("fin "), /espacio/);
  assert.match(FS.errorDeNombre(""), /nombre/);
});

test("nombreLibre añade sufijo numérico antes de la extensión", () => {
  const py = nuevo();
  assert.equal(FS.nombreLibre(py, "", "index.html"), "index-2.html");
  assert.equal(FS.nombreLibre(py, "", "libre.txt"), "libre.txt");
});
