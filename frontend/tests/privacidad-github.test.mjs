// Navegador compartido: la sesión de GitHub de una cuenta de CódigoCamp nunca le queda a otra.
import { test } from "node:test";
import assert from "node:assert/strict";

class Almacen {
  constructor() { this.m = new Map(); }
  get length() { return this.m.size; }
  key(i) { return [...this.m.keys()][i] ?? null; }
  getItem(k) { return this.m.has(k) ? this.m.get(k) : null; }
  setItem(k, v) { this.m.set(k, String(v)); }
  removeItem(k) { this.m.delete(k); }
}
globalThis.localStorage = new Almacen();
globalThis.sessionStorage = new Almacen();
const { protegerCuenta, borrarDatosLocales } = await import("../js/privacidad.js");
const { claveCuenta } = await import("../js/trabajo/cuenta.js");
const ana = { id: 1, email: "ana@x.co" }, beto = { id: 2, email: "beto@x.co" };

test("al entrar otra cuenta en el mismo navegador se borra la sesión de GitHub de la anterior", async () => {
  await protegerCuenta(ana);
  localStorage.setItem(`cc-github-${claveCuenta(ana)}`, JSON.stringify({ token: "gho_ana", login: "ana" }));
  sessionStorage.setItem(`cc-github-${claveCuenta(ana)}`, JSON.stringify({ token: "gho_ana2" }));
  localStorage.setItem("cc_tema", "oscuro");
  await protegerCuenta(beto);
  assert.equal(localStorage.getItem(`cc-github-${claveCuenta(ana)}`), null);
  assert.equal(sessionStorage.getItem(`cc-github-${claveCuenta(ana)}`), null);
  assert.equal(localStorage.getItem("cc_tema"), "oscuro", "los ajustes neutros se quedan");
});

test("cerrar sesión borra la sesión de GitHub", async () => {
  localStorage.setItem(`cc-github-${claveCuenta(beto)}`, "{}");
  sessionStorage.setItem(`cc-github-${claveCuenta(beto)}`, "{}");
  await borrarDatosLocales();
  assert.equal(localStorage.getItem(`cc-github-${claveCuenta(beto)}`), null);
  assert.equal(sessionStorage.getItem(`cc-github-${claveCuenta(beto)}`), null);
});
