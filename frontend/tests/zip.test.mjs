import test from "node:test";
import assert from "node:assert/strict";
import { crearZip, leerZip, crc32 } from "../js/trabajo/zip.js";

const enc = new TextEncoder();
const dec = new TextDecoder();

test("crc32 conocido", () => {
  assert.equal(crc32(enc.encode("123456789")), 0xcbf43926);
});

for (const comprimir of [true, false]) {
  test(`crear y leer un zip ${comprimir ? "comprimido" : "sin comprimir"} conserva texto, binario, tildes y carpetas vacías`, async () => {
    const png = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 1, 2, 3, 255]);
    const largo = "línea repetida ñandú\n".repeat(200);
    const zip = await crearZip([{ ruta: "index.html", texto: "<h1>Hola</h1>" }, { ruta: "img/logo.png", bytes: png }, { ruta: "src/largo.txt", texto: largo }],
      { carpetas: ["vacia"], comprimir });
    const r = await leerZip(zip);
    assert.deepEqual(r.omitidos, []);
    assert.deepEqual(r.carpetas, ["vacia"]);
    const por = Object.fromEntries(r.archivos.map((a) => [a.ruta, a.bytes]));
    assert.equal(dec.decode(por["index.html"]), "<h1>Hola</h1>");
    assert.deepEqual([...por["img/logo.png"]], [...png]);
    assert.equal(dec.decode(por["src/largo.txt"]), largo);
    if (comprimir) assert.ok(zip.length < largo.length, "se comprimió");
  });
}

test("rechaza lo que no es zip y marca los dañados", async () => {
  await assert.rejects(leerZip(enc.encode("hola, no soy un zip")), /No parece un archivo \.zip/);
  const zip = await crearZip([{ ruta: "a.txt", texto: "contenido original" }], { comprimir: false });
  // Se busca en BYTES (latin1 = 1 carácter por byte): con UTF-8 la fecha del encabezado podía correr el índice
  const i = Buffer.from(zip).toString("latin1").indexOf("contenido");
  zip[i] = "X".charCodeAt(0);
  const r = await leerZip(zip);
  assert.equal(r.archivos.length, 0);
  assert.match(r.omitidos[0].motivo, /dañado/);
});

test("protección contra bombas: archivos y totales demasiado grandes se omiten sin descomprimir", async () => {
  const zip = await crearZip([{ ruta: "a.txt", texto: "a".repeat(5000) }, { ruta: "b.txt", texto: "b".repeat(5000) }, { ruta: "c.txt", texto: "c" }]);
  const r = await leerZip(zip, { limites: { entradas: 10, porArchivo: 4000, total: 10000 } });
  assert.deepEqual(r.archivos.map((a) => a.ruta), ["c.txt"]);
  assert.equal(r.omitidos.length, 2);
  await assert.rejects(leerZip(zip, { limites: { entradas: 2, porArchivo: 1e9, total: 1e9 } }), /máximo es 2/);
});
