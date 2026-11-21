// La IA de Trabajo solo cambia lo pedido: ediciones {buscar, reemplazar} sobre el archivo actual.
import { test } from "node:test";
import assert from "node:assert/strict";
import { aplicarEdiciones, validarCambios, extraerCambios } from "../js/trabajo/copiloto.js";

const LOGIN = `<!doctype html>
<html lang="es">
<head>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <form class="login tarjeta">
    <h1 class="titulo-grande">Entrar</h1>
    <input type="email" id="correo" placeholder="Correo">
    <input type="text" id="clave" placeholder="Contraseña">
    <button class="btn-verde">Entrar</button>
  </form>
</body>
</html>
`;
const py = (files) => ({ files, folders: [] });

test("cambia solo la línea de la contraseña y deja el diseño idéntico", () => {
  const r = aplicarEdiciones(LOGIN, [{ buscar: '    <input type="text" id="clave" placeholder="Contraseña">', reemplazar: '    <input type="password" id="clave" placeholder="Contraseña" minlength="8" required>' }]);
  assert.ok(!r.error, r.error);
  const antes = LOGIN.split("\n"), despues = r.texto.split("\n");
  assert.equal(antes.length, despues.length);
  const distintas = antes.filter((l, i) => l !== despues[i]);
  assert.deepEqual(distintas, ['    <input type="text" id="clave" placeholder="Contraseña">']);
  assert.match(r.texto, /class="login tarjeta"/);
  assert.match(r.texto, /class="titulo-grande"/);
});

test("si la IA copió mal la sangría, igual encuentra el sitio y respeta la sangría del archivo", () => {
  const r = aplicarEdiciones(LOGIN, [{ buscar: '<input type="text" id="clave" placeholder="Contraseña">', reemplazar: '<input type="password" id="clave" placeholder="Contraseña">' }]);
  assert.ok(!r.error, r.error);
  assert.match(r.texto, /\n    <input type="password" id="clave"/);
});

test("texto inexistente o repetido: no se aplica (en vez de adivinar)", () => {
  assert.match(aplicarEdiciones(LOGIN, [{ buscar: "<p>no existe</p>", reemplazar: "x" }]).error, /no se encontró/);
  assert.match(aplicarEdiciones(LOGIN, [{ buscar: "<input", reemplazar: "<x" }]).error, /2 lugares/);
});

test("respeta los finales de línea de Windows (CRLF)", () => {
  const win = LOGIN.replace(/\n/g, "\r\n");
  const r = aplicarEdiciones(win, [{ buscar: '<button class="btn-verde">Entrar</button>', reemplazar: '<button class="btn-verde" type="submit">Entrar</button>' }]);
  assert.ok(!r.error);
  assert.ok(!/[^\r]\n/.test(r.texto), "todas las líneas siguen con CRLF");
});

test("del bloque de la IA al cambio validado (editar)", () => {
  const resp = 'Cambio el tipo del campo.\n```cc-cambios\n{"resumen":"contraseña oculta","cambios":[{"accion":"editar","ruta":"index.html","ediciones":[{"buscar":"<input type=\\"text\\" id=\\"clave\\" placeholder=\\"Contraseña\\">","reemplazar":"<input type=\\"password\\" id=\\"clave\\" placeholder=\\"Contraseña\\">"}]}]}\n```';
  const { cambios } = extraerCambios(resp);
  const { validos, errores } = validarCambios(cambios, py({ "index.html": LOGIN }));
  assert.deepEqual(errores, []);
  assert.equal(validos.length, 1);
  assert.equal(validos[0].ediciones, 1);
  assert.match(validos[0].contenido, /type="password"/);
  assert.equal(validos[0].contenido.replace('type="password"', 'type="text"'), LOGIN);
});

test("reescribir un archivo existente casi entero queda marcado para avisar", () => {
  const otro = LOGIN.replace(/class="[^"]*"/g, 'class="nuevo-diseno"').replace(/<input/g, "<input data-x").replace(/<h1/, "<h2").replace(/<\/h1>/, "</h2>").replace("Entrar</button>", "Ingresar</button>").replace("<head>", "<head><meta charset=utf-8>").replace(/  /g, "\t");
  const { validos } = validarCambios([{ accion: "escribir", ruta: "index.html", contenido: otro }], py({ "index.html": LOGIN }));
  assert.equal(validos[0].reescritura, true);
});
