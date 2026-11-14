import test from "node:test";
import assert from "node:assert/strict";
import { Shell, tokenizar, enColumnas, comandoParaArchivo, relativa } from "../js/trabajo/shell.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { quitarAnsi } from "../js/trabajo/ansi.js";

function entorno(files = { "index.html": "<h1>Hola</h1>\n", "script.js": "console.log(1)\n", "src/app.js": "a\nb\nc\n", "src/lib/util.js": "u\n" }, ejecutores = {}) {
  const py = normalizarProyecto({ files });
  const cambios = [];
  const abiertos = [];
  const shell = new Shell({ proyecto: () => py, cambio: (i) => cambios.push(i), abrir: (r) => abiertos.push(r), usuario: "Ana", ejecutores, ahora: () => new Date("2026-01-01T00:00:00Z") });
  const sesion = shell.nuevaSesion();
  let out = "", err = "";
  sesion.out = (t) => { out += t; };
  sesion.err = (t) => { err += t; };
  const sh = async (linea) => { out = ""; err = ""; const codigo = await shell.ejecutar(linea, sesion); return { codigo, out: quitarAnsi(out), err: quitarAnsi(err) }; };
  return { py, shell, sesion, sh, cambios, abiertos };
}

test("tokenizar: comillas, escapes, variables, operadores y comentarios", () => {
  const t = (l, v) => tokenizar(l, v).tokens.map((x) => (x.t === "w" ? x.v : `<${x.v}>`));
  assert.deepEqual(t('echo "a b" \'c d\' e\\ f'), ["echo", "a b", "c d", "e f"]);
  assert.deepEqual(t("ls&&cat a|wc>x;pwd"), ["ls", "<&&>", "cat", "a", "<|>", "wc", "<>>", "x", "<;>", "pwd"]);
  assert.deepEqual(t('echo $USER "${USER}x" $?', { USER: "ana", "?": 3 }), ["echo", "ana", "anax", "3"]);
  assert.deepEqual(t("echo hola # nada"), ["echo", "hola"]);
  assert.deepEqual(t("echo ''"), ["echo", ""]);
  assert.match(tokenizar('echo "x').error, /comillas/);
  assert.match(tokenizar("sleep 1 &").error, /segundo plano/);
  assert.equal(tokenizar("ls *.js").tokens[1].glob, true);
});

test("REGRESIÓN: touch, mkdir, cat, cd, ls <ruta> y git add funcionan (antes lanzaban resolverRuta is not defined)", async () => {
  const { sh, py, sesion } = entorno();
  assert.equal((await sh("touch hola.txt")).codigo, 0);
  assert.ok("hola.txt" in py.files);
  assert.equal((await sh("mkdir docs")).codigo, 0);
  assert.ok(py.folders.includes("docs"));
  assert.equal((await sh("cat index.html")).out, "<h1>Hola</h1>\n");
  assert.equal((await sh("cd src")).codigo, 0);
  assert.equal(sesion.cwd, "src");
  assert.equal((await sh("pwd")).out, "/workspace/src\n");
  assert.match((await sh("ls ..")).out, /index\.html/);
  assert.equal((await sh("cd ../nada")).codigo, 1);
  assert.match((await sh("cd app.js")).err, /No es un directorio/);
  await sh("cd"); assert.equal(sesion.cwd, "");
  await sh("git init"); assert.equal((await sh("git add .")).codigo, 0);
  assert.ok(py.git.staged.includes("index.html"));
});

test("ls: columnas, ocultos, -l y varias rutas", async () => {
  const { sh } = entorno({ "a.txt": "", ".oculto": "", "b/c.txt": "x" });
  assert.equal((await sh("ls")).out, "b  a.txt\n");
  assert.match((await sh("ls -a")).out, /\.oculto/);
  assert.match((await sh("ls -l")).out, /drwxr-xr-x Ana .* b\n-rw-r--r-- Ana +0 a\.txt/);
  const r = await sh("ls b a.txt nada");
  assert.equal(r.codigo, 2);
  assert.match(r.err, /'nada'.*No existe/);
  assert.match(r.out, /a\.txt\n\nb:\nc\.txt/);
  assert.equal((await sh("ls -1")).out, "b\na.txt\n");
});

test("BORRADO: rm, rm -r, rmdir, comodines y protecciones", async () => {
  const { sh, py, cambios } = entorno();
  assert.match((await sh("rm src")).err, /Es un directorio/);
  assert.equal((await sh("rm script.js")).codigo, 0);
  assert.ok(!("script.js" in py.files));
  assert.equal(cambios.at(-1).borrado, "script.js");
  assert.equal((await sh("rm -r src")).codigo, 0);
  assert.deepEqual(Object.keys(py.files), ["index.html"]);
  assert.ok(!py.folders.includes("src") && !py.folders.includes("src/lib"));
  assert.match((await sh("rm nada")).err, /No existe/);
  assert.equal((await sh("rm -f nada")).codigo, 0);
  for (const peligro of ["rm -rf .", "rm -rf ..", "rm -rf /", "rm -rf ~"]) {
    const r = await sh(peligro);
    assert.notEqual(r.codigo, 0, peligro);
  }
  assert.ok("index.html" in py.files, "el proyecto sigue intacto");
  await sh("touch a.log b.log c.txt"); await sh("rm *.log");
  assert.ok(!("a.log" in py.files) && "c.txt" in py.files);
  await sh("mkdir vacia"); assert.equal((await sh("rmdir vacia")).codigo, 0);
  await sh("mkdir -p x/y"); assert.match((await sh("rmdir x")).err, /no está vacío/);
});

test("rm de la carpeta actual mueve el cwd al padre (como no perderse en una carpeta inexistente)", async () => {
  const { sh, sesion } = entorno();
  await sh("cd src/lib"); await sh("rm -r ../../src");
  assert.equal(sesion.cwd, "");
});

test("mv y cp: renombrar, mover a carpeta, copiar recursivo", async () => {
  const { sh, py, sesion } = entorno();
  assert.equal((await sh("mv script.js main.js")).codigo, 0);
  assert.ok("main.js" in py.files && !("script.js" in py.files));
  assert.equal((await sh("mv main.js src")).codigo, 0);
  assert.ok("src/main.js" in py.files);
  assert.match((await sh("cp src copia")).err, /-r/);
  assert.equal((await sh("cp -r src copia")).codigo, 0);
  assert.ok("copia/lib/util.js" in py.files);
  assert.equal((await sh("cp index.html src/lib")).codigo, 0);
  assert.ok("src/lib/index.html" in py.files);
  assert.match((await sh("mv nada x")).err, /No existe/);
  await sh("cd copia"); await sh("mv ../copia ../renombrada");
  assert.equal(sesion.cwd, "renombrada");
  assert.equal((await sh("mv src src/lib/dentro")).codigo, 1);
});

test("echo, redirecciones, pipes y encadenado", async () => {
  const { sh, py } = entorno();
  assert.equal((await sh('echo "hola   mundo"')).out, "hola   mundo\n");
  await sh("echo uno > a.txt"); await sh("echo dos >> a.txt");
  assert.equal(py.files["a.txt"], "uno\ndos\n");
  assert.equal((await sh("cat a.txt | wc -l")).out.trim(), "2");
  assert.equal((await sh("cat src/app.js | head -n 2")).out, "a\nb\n");
  assert.equal((await sh("cat src/app.js | tail -1")).out, "c\n");
  assert.equal((await sh("false_cmd || echo plan-b")).out, "plan-b\n");
  assert.equal((await sh("echo a && echo b; echo c")).out, "a\nb\nc\n");
  assert.equal((await sh("cat nada && echo no")).out, "");
  assert.match((await sh("echo x > carpeta/inexistente/f.txt")).err, /No existe|no válido/);
  assert.match((await sh("echo x > src")).err, /carpeta/i);
  assert.equal((await sh("echo $PWD")).out, "/workspace\n");
  await sh("export NOMBRE=Ana"); assert.equal((await sh('echo "Hola $NOMBRE"')).out, "Hola Ana\n");
  assert.equal((await sh("echo $?")).out, "0\n");
});

test("grep, wc, find, tree", async () => {
  const { sh } = entorno();
  assert.equal((await sh("grep b src/app.js")).out, "b\n");
  assert.equal((await sh("grep -n console script.js")).out, "1:console.log(1)\n");
  assert.match((await sh("grep -rn a .")).out, /src\/app\.js:1:a/);
  assert.equal((await sh("grep zzz script.js")).codigo, 1);
  assert.equal((await sh("grep -c . src/app.js")).out, "3\n");
  assert.equal((await sh("wc -l src/app.js")).out.trim(), "3 src/app.js");
  assert.match((await sh("find . -name '*.js'")).out, /\.\/script\.js\n\.\/src\/app\.js/);
  assert.equal((await sh("find src -type d")).out, "src\nsrc/lib\n");
  const todo = (await sh("find")).out;
  assert.ok(todo.startsWith(".\n") && todo.includes("./src/lib/util.js\n") && todo.includes("./src/lib\n"));
  const t = (await sh("tree")).out;
  assert.match(t, /├── src\n│   ├── lib\n│   │   └── util\.js\n│   └── app\.js\n/);
  assert.match(t, /2 directorios, 4 archivos/);
});

test("code abre archivos; code de uno nuevo lo crea", async () => {
  const { sh, abiertos, py } = entorno();
  await sh("code script.js"); await sh("code nuevo.txt");
  assert.deepEqual(abiertos, ["script.js", "nuevo.txt"]);
  assert.ok("nuevo.txt" in py.files);
});

test("errores de sintaxis y comandos desconocidos o no disponibles", async () => {
  const { sh } = entorno();
  assert.equal((await sh("echo 'x")).codigo, 2);
  assert.equal((await sh("| ls")).codigo, 2);
  assert.equal((await sh("ls &&")).codigo, 2);
  assert.equal((await sh("echo a >")).codigo, 2);
  const r = await sh("foo");
  assert.equal(r.codigo, 127); assert.match(r.err, /orden no encontrada/);
  const n = await sh("npm install"); assert.equal(n.codigo, 127); assert.match(n.err, /no está disponible/);
  assert.match((await sh("help")).out, /Terminal de CódigoCamp/);
});

test("node y python reciben el archivo, la ruta y el contexto; REPL no disponible", async () => {
  const llamadas = [];
  const ej = (nombre) => async (c) => { llamadas.push([nombre, c.ruta, c.codigo, c.args, c.cwd]); c.out("salida\n"); return 0; };
  const { sh } = entorno(undefined, { node: ej("node"), python: ej("python"), ts: ej("ts"), servidor: async ({ lenguaje }) => ({ salida: `srv:${lenguaje}`, error: false }) });
  await sh("node script.js a b"); await sh("cd src"); await sh("node app.js");
  assert.deepEqual(llamadas[0], ["node", "script.js", "console.log(1)\n", ["a", "b"], ""]);
  assert.equal(llamadas[1][1], "src/app.js"); assert.equal(llamadas[1][4], "src");
  assert.equal((await sh("node nada.js")).codigo, 1);
  assert.match((await sh("node")).err, /REPL/);
  assert.equal((await sh("python3 -c 'print(1)'")).codigo, 0);
  assert.equal(llamadas.at(-1)[2], "print(1)");
});

test("compilados en servidor: gcc guarda el resultado y ./prog lo muestra; java y kotlinc", async () => {
  const vistos = [];
  const servidor = async ({ lenguaje, codigo }) => { vistos.push(lenguaje); return { salida: codigo.includes("ERR") ? "main.c:1: error" : `hola desde ${lenguaje}`, error: codigo.includes("ERR") }; };
  const { sh } = entorno({ "m.c": "int main(){}", "mal.c": "ERR", "Main.java": "public class Main {}", "k.kt": "fun main(){}", "p.go": "x", "r.rb": "x" }, { servidor });
  assert.match((await sh("./prog")).err, /No existe/);
  assert.equal((await sh("gcc m.c -o prog")).codigo, 0);
  assert.equal((await sh("./prog")).out, "hola desde c\n");
  assert.equal((await sh("gcc m.c && ./a.out")).out, "hola desde c\n");
  assert.equal((await sh("gcc m.c -o prog && ./prog")).out, "hola desde c\n");
  await sh("gcc mal.c -o roto"); assert.match((await sh("./roto")).err + (await sh("./roto")).out, /error/);
  await sh("javac Main.java"); assert.equal((await sh("java Main")).out, "hola desde java\n");
  assert.equal((await sh("java Main.java")).out, "hola desde java\n");
  await sh("kotlinc k.kt -include-runtime -d k.jar"); assert.equal((await sh("java -jar k.jar")).out, "hola desde kotlin\n");
  assert.equal((await sh("go run p.go")).out, "hola desde go\n");
  assert.equal((await sh("ruby r.rb")).out, "hola desde ruby\n");
  assert.match((await sh("go build p.go")).err, /solo se admite/);
  assert.ok(vistos.includes("rust") === false);
});

test("run y comandoParaArchivo", async () => {
  assert.equal(comandoParaArchivo("src/app.js", ""), "node src/app.js");
  assert.equal(comandoParaArchivo("src/app.js", "src"), "node app.js");
  assert.equal(comandoParaArchivo("a/b.py", "x"), "python ../a/b.py");
  assert.equal(comandoParaArchivo("m.c", ""), "gcc m.c -o m && ./m");
  assert.equal(comandoParaArchivo("d/m.cpp", ""), "g++ d/m.cpp -o d/m && ./d/m");
  assert.equal(comandoParaArchivo("index.html", ""), null);
  assert.equal(relativa("a/b", "a/c/d"), "../c/d");
  assert.equal(relativa("", "x"), "x");
  const { sh } = entorno(undefined, { node: async (c) => { c.out("ok\n"); return 0; } });
  assert.match((await sh("run script.js")).out, /\$ node script\.js\nok/);
  assert.match((await sh("run index.html")).err, /Vista previa/);
});

test("completar: comandos, subcomandos de git, rutas y solo carpetas con cd", async () => {
  const { shell, sesion } = entorno();
  assert.deepEqual(shell.completar("gi", sesion).opciones, ["git "]);
  assert.ok(shell.completar("c", sesion).opciones.includes("cat "));
  assert.deepEqual(shell.completar("git sta", sesion).opciones, ["status "]);
  assert.deepEqual(shell.completar("cat s", sesion).opciones, ["src/", "script.js "]);
  assert.deepEqual(shell.completar("cat src/a", sesion).opciones, ["src/app.js "]);
  assert.deepEqual(shell.completar("cd s", sesion).opciones, ["src/"]);
  assert.equal(shell.completar("cat src/a", sesion).desde, 4);
  assert.deepEqual(shell.completar("ls nada/", sesion).opciones, []);
  assert.deepEqual(shell.completar("ls x && gi", sesion).opciones, ["git "]);
});

test("enColumnas reparte por columnas según el ancho", () => {
  assert.equal(enColumnas(["a", "b", "c", "d"], 80), "a  b  c  d");
  assert.equal(enColumnas(["aaaa", "bbbb", "cccc"], 10), "aaaa  cccc\nbbbb");
  assert.equal(enColumnas([], 80), "");
});
