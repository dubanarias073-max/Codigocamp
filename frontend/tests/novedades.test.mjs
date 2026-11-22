// Copiloto en línea, plantillas de Vue/Svelte, contactos e idioma.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { convienePedir, vecinos } from "../js/trabajo/copiloto-linea.js";
import { archivosDePlantilla, PAQUETES, PLANTILLAS } from "../js/trabajo/plantillas.js";
import { idDe } from "../js/trabajo/compiladores.js";
import { huellaCorreo, enlacesInvitacion } from "../js/contactos.js";

test("copiloto: pide al final de la línea, no a mitad de palabra", () => {
  assert.equal(convienePedir("function suma(a, b) {\n  ", "\n}"), true);
  assert.equal(convienePedir("const total = suma(", ")"), true);
  assert.equal(convienePedir("const tot", "al = 1"), false);
  assert.equal(convienePedir("x", ""), false);
});

test("copiloto: manda a la IA los archivos relacionados", () => {
  const r = vecinos({ "src/App.jsx": "import { api } from './api'", "src/api.js": "export const api = 1", "notas.md": "x" }, "src/App.jsx");
  assert.deepEqual(r.map((x) => x.ruta), ["src/api.js"]);
});

test("plantillas de Vue y Svelte", () => {
  assert.ok(PLANTILLAS.includes("vue") && PLANTILLAS.includes("svelte"));
  assert.deepEqual(PAQUETES.vue[0], ["vue"]);
  assert.ok(archivosDePlantilla("vue", "app")["src/App.vue"].includes("<script setup>"));
  assert.ok(archivosDePlantilla("svelte", "app")["src/main.js"].includes("mount(App"));
  assert.equal(idDe("src/App.vue"), idDe("src/App.vue"));
  assert.notEqual(idDe("src/App.vue"), idDe("src/Otro.vue"));
});

test("contactos: huella sha256 del correo en minúsculas y enlaces de invitación", () => {
  assert.equal(huellaCorreo(" ABC "), huellaCorreo("abc"));
  assert.equal(huellaCorreo("abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
  const e = enlacesInvitacion({ tel: ["+57 300 111 2222"], email: [] }, "https://cc/x");
  assert.ok(e.whatsapp.startsWith("https://wa.me/573001112222?text="));
  assert.ok(e.sms.startsWith("sms:+573001112222?body="));
  assert.equal(e.correo, null);
});

test("idioma: traduce interfaz y patrones, conserva lo que no conoce", () => {
  const w = {};
  const ctx = { window: w, document: { documentElement: {}, addEventListener() {} }, localStorage: { getItem: () => "en", setItem() {} },
    location: { pathname: "/pages/inicio.html" }, MutationObserver: class { observe() {} }, NodeFilter: {} };
  new Function(...Object.keys(ctx), readFileSync(new URL("../js/i18n.js", import.meta.url), "utf8"))(...Object.values(ctx));
  assert.equal(w.ccT("Configuración"), "Settings");
  assert.equal(w.ccT("  Guardar  "), "  Save  ");
  assert.equal(w.ccT("5 días de racha"), "5-day streak");
  assert.equal(w.ccT("Primer paso · Completa tu primera lección"), "First step · Complete your first lesson");
  assert.equal(w.ccT("Configuración · CódigoCamp"), "Settings · CódigoCamp");
  assert.equal(w.ccT("Hola profe"), "Hola profe");
});
