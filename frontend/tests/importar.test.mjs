import test from "node:test";
import assert from "node:assert/strict";
import { limpiarNombre, limpiarRuta, clasificar, planificar, aplicar, raizComun, paraExportar, normalizarTexto, prepararArchivos, importarEn } from "../js/trabajo/importar.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { esMarcador, leerMarcador } from "../js/trabajo/archivos.js";

const enc = new TextEncoder();
const PNG = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 1, 2, 3]);
const MP4 = new Uint8Array([0, 0, 0, 0x18, 0x66, 0x74, 0x79, 0x70, 0x6d, 0x70, 0x34, 0x32, 9, 9]);
const txt = (ruta, t) => ({ ruta, bytes: enc.encode(t) });
const marcador = (c, tipo = "image/png", n = 11) => `ccbin:v1:${c.repeat(64)}:${tipo}:${n}`;

test("limpiarNombre y limpiarRuta: tildes, espacios, carpetas ignoradas y rutas peligrosas", () => {
  assert.equal(limpiarNombre("Mi Foto (1).PNG"), "Mi-Foto-_1.PNG");
  assert.equal(limpiarNombre("canción ñandú.mp3"), "cancion-nandu.mp3");
  assert.equal(limpiarNombre(".gitignore"), ".gitignore");
  for (const n of ["__init__.py", "__main__.py", "_config.yml", "a__b.js", "mi-archivo_2.js", ".env"]) assert.equal(limpiarNombre(n), n, `${n} no se toca`);
  assert.deepEqual(limpiarRuta("backend/application/__init__.py"), { ruta: "backend/application/__init__.py", renombrada: false });
  assert.equal(limpiarNombre(".."), null);
  assert.equal(limpiarNombre("x".repeat(150) + ".js").length, 120);
  assert.deepEqual(limpiarRuta("Mis Documentos/índice.html"), { ruta: "Mis-Documentos/indice.html", renombrada: true });
  assert.deepEqual(limpiarRuta("node_modules/x/index.js"), { ignorar: true });
  assert.deepEqual(limpiarRuta(".git/HEAD"), { ignorar: true });
  assert.deepEqual(limpiarRuta("a/.DS_Store"), { ignorar: true });
  assert.ok(limpiarRuta("../../etc/passwd").error);
});

test("clasificar: texto editable, cualquier binario como archivo, texto grande como archivo y tope por archivo", () => {
  assert.deepEqual(clasificar("a.txt", enc.encode("﻿uno\r\ndos\rtres")), { tipo: "texto", texto: "uno\ndos\ntres" });
  assert.equal(clasificar("logo.jpg", PNG).mime, "image/png", "manda el contenido, no la extensión");
  assert.equal(clasificar("clip.mp4", MP4).mime, "video/mp4");
  assert.equal(clasificar("logo.svg", enc.encode("<svg></svg>")).tipo, "texto");
  assert.deepEqual(clasificar("x.bin", new Uint8Array([1, 0, 2])), { tipo: "archivo", mime: "application/octet-stream" });
  assert.equal(clasificar("doc.pdf", enc.encode("%PDF-1.7 texto")).mime, "application/pdf");
  const grande = clasificar("datos.csv", enc.encode("a,b\n".repeat(300_000)));
  assert.deepEqual([grande.tipo, grande.mime, grande.grande], ["archivo", "text/csv", true]);
  const blob = { blob: new Blob([new Uint8Array(1_100_000)]), cabeza: MP4 };
  assert.equal(clasificar("v.mp4", blob).mime, "video/mp4");
  assert.match(clasificar("v.mp4", blob, { maxArchivo: 1000 }).motivo, /máximo 1000 B/);
  assert.equal(normalizarTexto("a\r\nb"), "a\nb");
});

test("planificar: quita la raíz común, renombra, ignora y trae todo tipo de archivos", () => {
  const py = normalizarProyecto({ files: { "index.html": "viejo" } });
  const origen = { archivos: [txt("repo-main/index.html", "nuevo"), txt("repo-main/Mi Carpeta/a b.js", "x"), { ruta: "repo-main/img/logo.png", bytes: PNG },
    txt("repo-main/node_modules/lib/i.js", "no"), { ruta: "repo-main/video.mp4", bytes: MP4 }], carpetas: ["repo-main/", "repo-main/vacia/"] };
  const plan = planificar(py, origen);
  assert.equal(plan.raiz, "repo-main");
  assert.deepEqual(plan.textos.map((t) => t.ruta).sort(), ["Mi-Carpeta/a-b.js", "index.html"]);
  assert.deepEqual(plan.binarios.map((i) => [i.ruta, i.tipo]), [["img/logo.png", "image/png"], ["video.mp4", "video/mp4"]]);
  assert.deepEqual(plan.reemplazados, ["index.html"]);
  assert.equal(plan.ignorados, 1);
  assert.deepEqual(plan.omitidos, []);
  assert.equal(plan.bytesArchivos, PNG.length + MP4.length);
  const escritos = aplicar(py, plan, new Map([["img/logo.png", marcador("a")], ["video.mp4", marcador("b", "video/mp4", 14)]]));
  assert.equal(escritos, 4);
  assert.ok(esMarcador(py.files["video.mp4"]));
  assert.ok(py.folders.includes("vacia") && py.folders.includes("Mi-Carpeta") && py.folders.includes("img"));
});

test("planificar: límites de archivos, caracteres, espacio de la cuenta y choques archivo/carpeta", () => {
  const py = normalizarProyecto({ files: { src: "soy un archivo", "docs/a.md": "a" } });
  const muchos = Array.from({ length: 5010 }, (_, i) => txt(`f${String(i).padStart(4, "0")}.txt`, "x"));
  const plan = planificar(py, { archivos: [...muchos, txt("src/app.js", "x"), txt("docs", "x"), { ruta: "a.png", bytes: PNG }] }, { quitarRaiz: false, espacioArchivos: 5 });
  assert.equal(plan.textos.length, 4998); // 5000 - los 2 que ya hay
  assert.ok(plan.omitidos.some((o) => o.ruta === "src/app.js" && /ya hay/.test(o.motivo)));
  assert.ok(plan.omitidos.some((o) => o.ruta === "docs" && /ya hay/.test(o.motivo)));
  assert.ok(plan.omitidos.some((o) => o.ruta === "a.png" && /quedan 5 B libres/.test(o.motivo)));
  const caracteres = planificar(normalizarProyecto({ files: { "a.txt": "x".repeat(4_999_950) } }), { archivos: [txt("b.txt", "y".repeat(100))] });
  assert.match(caracteres.omitidos[0].motivo, /5 millones/);
  // Con cuenta, el texto que no cabe como editable se guarda completo como archivo (no se pierde).
  const conCuenta = planificar(normalizarProyecto({ files: { "a.txt": "x".repeat(4_999_950) } }), { archivos: [txt("b.txt", "y".repeat(100))] }, { textoComoArchivo: true });
  assert.deepEqual([conCuenta.omitidos.length, conCuenta.binarios[0].tipo, conCuenta.comoArchivo[0]], [0, "text/plain", "b.txt"]);
  const marcadoresNoCuentan = planificar(normalizarProyecto({ files: { "v.mp4": marcador("d", "video/mp4", 9), "a.txt": "x".repeat(4_999_000) } }), { archivos: [txt("b.txt", "y".repeat(900))] });
  assert.equal(marcadoresNoCuentan.textos.length, 1, "los marcadores no gastan el espacio de texto");
  const reemplazo = planificar(py, { archivos: [txt("src/app.js", "x")] }, { reemplazar: true, quitarRaiz: false });
  aplicar(py, reemplazo);
  assert.deepEqual(Object.keys(py.files), ["src/app.js"]);
});

test("raizComun y destino", () => {
  assert.equal(raizComun(["a/x", "a/y/z"]), "a");
  assert.equal(raizComun(["a/x", "b"]), null);
  const py = normalizarProyecto({ files: {} });
  aplicar(py, planificar(py, { archivos: [txt("x.js", "1")] }, { destino: "vendor/lib" }));
  assert.deepEqual(Object.keys(py.files), ["vendor/lib/x.js"]);
});

test("prepararArchivos: los pequeños se leen, los grandes quedan como Blob (sin cargarlos)", async () => {
  const pequeno = new Blob(["hola"]);
  const grande = new Blob([MP4, new Uint8Array(1_100_000)]);
  const [a, b] = await prepararArchivos([{ ruta: "a.txt", archivo: pequeno }, { ruta: "v.mp4", archivo: grande }]);
  assert.deepEqual([...a.bytes], [...enc.encode("hola")]);
  assert.equal(b.blob, grande);
  assert.equal(b.cabeza.length, 64);
});

test("importarEn: sube cada archivo con su nombre y su progreso; sin cuenta se omiten", async () => {
  const py = normalizarProyecto({ files: {} });
  const subidas = [];
  const progreso = [];
  const { plan, escritos } = await importarEn(py, { archivos: [{ ruta: "v.mp4", bytes: MP4 }, txt("a.js", "1")] }, {
    subir: async (d, o) => { subidas.push(o.nombre); o.progreso(0.5); return marcador("c", "video/mp4", 14); },
    espacio: async () => ({ libre: 1e9, maxArchivo: 1e9 }), progreso: (t) => progreso.push(t),
  });
  assert.equal(escritos, 2);
  assert.deepEqual(subidas, ["v.mp4"]);
  assert.ok(progreso.some((t) => /v\.mp4.*50 %/.test(t)));
  assert.equal(plan.omitidos.length, 0);
  const sin = await importarEn(normalizarProyecto({ files: {} }), { archivos: [{ ruta: "v.mp4", bytes: MP4 }] });
  assert.match(sin.plan.omitidos[0].motivo, /sesión/);
});

test("paraExportar: texto, archivos como Blob, tope del .zip y descargas fallidas", async () => {
  const ok = marcador("a", "image/png", 11);
  const roto = marcador("b", "image/png", 11);
  const enorme = marcador("e", "video/mp4", 5000);
  const py = normalizarProyecto({ files: { "a.txt": "hola", "img/a.png": ok, "img/b.png": roto, "v.mp4": enorme }, folders: ["vacia", "img"] });
  const r = await paraExportar(py, async (m) => { if (m === roto) throw new Error("404"); return new Blob([PNG]); }, { esMarcador, leerMarcador, maximo: 1000 });
  assert.deepEqual(r.archivos.map((a) => a.ruta), ["a.txt", "img/a.png"]);
  assert.deepEqual(r.fallidas, ["img/b.png"]);
  assert.deepEqual(r.grandes, ["v.mp4"]);
  assert.deepEqual(r.carpetas, ["vacia"]);
});
