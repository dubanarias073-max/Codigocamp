import test from "node:test";
import assert from "node:assert/strict";
import { importsDesde } from "../js/trabajo/extensiones.js";
import { COMPATIBLES, instalarTolerante } from "../js/trabajo/paquetes.js";

const proyecto = (files, folders = []) => ({ files, folders });

test("al encender una app solo cuenta lo que esa app importa (no otro framework del proyecto)", () => {
  const py = proyecto({
    "app.py": "from flask import Flask\nfrom rutas import api\nimport os\n",
    "rutas/__init__.py": "from .usuarios import bp\n",
    "rutas/usuarios.py": "from flask_cors import CORS\nfrom ..modelos import Usuario\nimport jwt\n",
    "modelos.py": "from flask_sqlalchemy import SQLAlchemy\n",
    "main.py": "from fastapi import FastAPI\n",
  }, ["rutas"]);
  assert.deepEqual(importsDesde(py, "app.py").sort(), ["flask", "flask_cors", "flask_sqlalchemy", "jwt"].sort());
  assert.deepEqual(importsDesde(py, "main.py"), ["fastapi"]);
  assert.ok(importsDesde(py, "no-existe.py").includes("fastapi"), "sin entrada: todo el proyecto, como antes");
});

test("FastAPI y compañía se instalan en versiones que funcionan en el navegador", async () => {
  const pedidos = [];
  const micropip = { install: async (x) => { pedidos.push(x); if (String(x).startsWith("fastapi==0.121")) throw new Error("Can't find a pure Python 3 wheel for 'pydantic-core==2.50.5'"); } };
  micropip.install.callKwargs = async () => {};
  await instalarTolerante(micropip, "fastapi");
  assert.deepEqual(pedidos.pop(), COMPATIBLES.fastapi, "sin versión: directo a la combinación probada");
  await instalarTolerante(micropip, "fastapi[standard]");
  assert.deepEqual(pedidos.pop(), COMPATIBLES.fastapi);
  const r = await instalarTolerante(micropip, "fastapi==0.121.0");
  assert.deepEqual(pedidos.pop(), COMPATIBLES.fastapi, "una versión que no funciona cae en la compatible");
  assert.match(r.aviso, /compatible/);
  await instalarTolerante(micropip, "flask");
  assert.equal(pedidos.pop(), "flask", "lo que no tiene problemas se instala tal cual");
});

test("leer /workspace vacío (mientras otro lo reescribe) nunca borra el proyecto", async () => {
  const { diferencias, aplicarCambios } = await import("../js/trabajo/ejecucion.js");
  const py = { files: { "a.py": "1", "b/c.py": "2" }, folders: ["b"] };
  const antes = { files: { ...py.files }, folders: [...py.folders] };
  const vacio = { files: {}, folders: [] };
  assert.equal(aplicarCambios(py, diferencias(antes, vacio)), false);
  assert.deepEqual(Object.keys(py.files), ["a.py", "b/c.py"]);
  const borroUno = { files: { "a.py": "1" }, folders: ["b"] };
  aplicarCambios(py, diferencias(antes, borroUno));
  assert.deepEqual(Object.keys(py.files), ["a.py"], "borrar algunos archivos sí se respeta");
});
