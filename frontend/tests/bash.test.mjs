import test from "node:test";
import assert from "node:assert/strict";
import { Shell } from "../js/trabajo/shell.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { quitarAnsi } from "../js/trabajo/ansi.js";
import { incompleta, aritmetica, sentencias } from "../js/trabajo/bash.js";

function entorno(files = {}) {
  const py = normalizarProyecto({ files: { "datos.csv": "nombre,edad\nana,17\nluis,30\nana,22\n", "notas.txt": "b\na\nc\na\n", ...files } });
  const shell = new Shell({ proyecto: () => py, cambio: () => {}, abrir: () => {}, usuario: "Ana", ejecutores: {}, ahora: () => new Date("2026-01-01T00:00:00Z") });
  const sesion = shell.nuevaSesion();
  let out = "", err = "";
  const entradas = [];
  sesion.out = (t) => { out += t; };
  sesion.err = (t) => { err += t; };
  sesion.leerLinea = async () => entradas.shift() ?? null;
  const sh = async (linea) => { out = ""; err = ""; const codigo = await shell.ejecutar(linea, sesion); return { codigo, out: quitarAnsi(out), err: quitarAnsi(err) }; };
  return { py, sh, sesion, entradas };
}

test("for, while, until, if/elif/else, case y for (( ))", async () => {
  const { sh } = entorno();
  assert.equal((await sh("for i in 1 2 3; do echo n$i; done")).out, "n1\nn2\nn3\n");
  assert.equal((await sh("for ((i=0; i<3; i++)); do echo $i; done")).out, "0\n1\n2\n");
  assert.equal((await sh("x=0; while [ $x -lt 3 ]; do echo $x; x=$((x+1)); done")).out, "0\n1\n2\n");
  assert.equal((await sh("y=3; until [ $y -eq 0 ]; do echo $y; y=$((y-1)); done")).out, "3\n2\n1\n");
  assert.equal((await sh('n=15; if [ $n -gt 20 ]; then echo grande; elif [ $n -gt 10 ]; then echo medio; else echo chico; fi')).out, "medio\n");
  assert.equal((await sh('f=foto.png; case $f in *.txt) echo texto;; *.png|*.jpg) echo imagen;; *) echo otro;; esac')).out, "imagen\n");
  assert.equal((await sh("for f in *.csv *.txt; do echo $f; done")).out, "datos.csv\nnotas.txt\n");
  assert.equal((await sh("for i in 1 2 3 4 5; do if [ $i -eq 2 ]; then continue; fi; if [ $i -eq 4 ]; then break; fi; echo $i; done")).out, "1\n3\n");
  assert.equal((await sh("for i in 1 2; do for j in a b; do echo $i$j; done; done")).out, "1a\n1b\n2a\n2b\n");
});

test("funciones, $1 $# $@, return, local y recursión", async () => {
  const { sh } = entorno();
  assert.equal((await sh('saluda() { echo "Hola $1, tienes $2 años ($# datos)"; }; saluda Ana 17')).out, "Hola Ana, tienes 17 años (2 datos)\n");
  assert.equal((await sh('suma() { return $(( $1 + $2 )); }; suma 2 3; echo $?')).out, "5\n");
  assert.equal((await sh('fact() { if [ $1 -le 1 ]; then echo 1; else echo $(( $1 * $(fact $(( $1 - 1 ))) )); fi; }; fact 5')).out, "120\n");
  assert.equal((await sh('todos() { for x in "$@"; do echo "[$x]"; done; }; todos "a b" c')).out, "[a b]\n[c]\n");
});

test("expansiones: $(( )), $( ), `cmd`, ${var...}, asignaciones y X=1 cmd", async () => {
  const { sh } = entorno();
  assert.equal((await sh("echo $((2 + 3 * 4)) $((10 / 3)) $((2 ** 8)) $((7 % 3))")).out, "14 3 256 1\n");
  assert.equal((await sh("echo hay $(ls | wc -l) archivos")).out.replace(/\s+/g, " ").trim(), "hay 2 archivos");
  assert.equal((await sh("echo `echo hola`")).out, "hola\n");
  assert.equal((await sh('nombre=codigocamp; echo ${#nombre} ${nombre^^} ${nombre:0:6} ${otro:-nada}')).out, "10 CODIGOCAMP codigo nada\n");
  assert.equal((await sh('a=archivo.tar.gz; echo ${a%%.*} ${a#*.} ${a/tar/zip}')).out, "archivo tar.gz archivo.zip.gz\n");
  assert.equal((await sh("x=5; ((x++)); echo $x; let x+=10; echo $x")).out, "6\n16\n");
  assert.equal((await sh("A=hola; echo $A")).out, "hola\n");
});

test("test / [ ] / [[ ]] con archivos, cadenas y números", async () => {
  const { sh } = entorno();
  assert.equal((await sh("[ -f datos.csv ] && echo si || echo no")).out, "si\n");
  assert.equal((await sh("[ -d datos.csv ] && echo si || echo no")).out, "no\n");
  assert.equal((await sh('[ "a" = "a" ] && [ 3 -ge 2 ] && echo ok')).out, "ok\n");
  assert.equal((await sh('[[ hola.py == *.py ]] && echo python')).out, "python\n");
  assert.equal((await sh('[ -z "" ] && echo vacio')).out, "vacio\n");
});

test("filtros: sort, uniq, cut, tr, sed, awk, seq, rev, tee, diff, xargs", async () => {
  const { sh, py } = entorno();
  assert.equal((await sh("sort notas.txt | uniq -c")).out, "      2 a\n      1 b\n      1 c\n");
  assert.equal((await sh("sort -r notas.txt | head -n 1")).out, "c\n");
  assert.equal((await sh("cut -d , -f 1 datos.csv | tail -n 3 | sort -u")).out, "ana\nluis\n");
  assert.equal((await sh("echo Hola Mundo | tr a-z A-Z")).out, "HOLA MUNDO\n");
  assert.equal((await sh("echo 'hola mundo' | sed 's/mundo/CódigoCamp/'")).out, "hola CódigoCamp\n");
  assert.equal((await sh("sed -n '2p' notas.txt")).out, "a\n");
  assert.equal((await sh("awk -F , 'NR>1 {print $1, $2}' datos.csv")).out, "ana 17\nluis 30\nana 22\n");
  assert.equal((await sh("awk -F , 'NR>1 {s+=$2} END {print s}' datos.csv")).out, "69\n");
  assert.equal((await sh("seq 3 | rev")).out, "1\n2\n3\n");
  assert.equal((await sh("seq 2 2 6")).out, "2\n4\n6\n");
  assert.equal((await sh("echo copia | tee c.txt")).out, "copia\n");
  assert.equal(py.files["c.txt"], "copia\n");
  assert.equal((await sh("diff notas.txt notas.txt")).codigo, 0);
  assert.equal((await sh("echo a b c | xargs -n 1 echo x")).out, "x a\nx b\nx c\n");
  await sh("sed -i 's/a/A/g' notas.txt");
  assert.equal(py.files["notas.txt"], "b\nA\nc\nA\n");
});

test("scripts .sh: bash archivo.sh, ./archivo.sh con argumentos, source y exit", async () => {
  const { sh, sesion } = entorno({ "hola.sh": "#!/bin/bash\n# saludo\nfor n in \"$@\"; do\n  echo \"Hola $n\"\ndone\necho \"total: $#\"\nexit 3\necho nunca\n", "vars.sh": "MI_VAR=42\ncd /workspace\n" });
  const r = await sh("bash hola.sh Ana Luis");
  assert.equal(r.out, "Hola Ana\nHola Luis\ntotal: 2\n");
  assert.equal(r.codigo, 3);
  assert.equal((await sh("./hola.sh Eva")).out, "Hola Eva\ntotal: 1\n");
  await sh("source vars.sh");
  assert.equal(sesion.vars.MI_VAR, "42");
});

test("read lee de la terminal y de una tubería; alias", async () => {
  const { sh, entradas } = entorno();
  entradas.push("Ana 17");
  assert.equal((await sh('read nombre edad; echo "$nombre tiene $edad"')).out, "Ana tiene 17\n");
  assert.equal((await sh("alias saludo='echo hola'; saludo mundo")).out, "hola mundo\n");
});

test("líneas incompletas (para pedir más con >) y aritmética", () => {
  assert.equal(incompleta("for i in 1 2; do"), true);
  assert.equal(incompleta("for i in 1 2; do echo $i; done"), false);
  assert.equal(incompleta('echo "hola'), true);
  assert.equal(incompleta("if true; then"), true);
  assert.equal(incompleta("ls |"), true);
  assert.equal(incompleta("f() {"), true);
  assert.deepEqual(sentencias("echo a; for i in 1; do echo $i; done\necho b"), ["echo a", "for i in 1; do echo $i; done", "echo b"]);
  const v = { x: "2" };
  assert.equal(aritmetica("x = x * 10 + 1", v), "21");
  assert.equal(v.x, "21");
  assert.equal(aritmetica("5 > 3 && 2 == 2 ? 7 : 9", {}), "7");
});

test("un bucle infinito se detiene solo", async () => {
  const { sh } = entorno();
  const r = await sh("while true; do :; done");
  assert.match(r.err, /100 000 vueltas/);
});
