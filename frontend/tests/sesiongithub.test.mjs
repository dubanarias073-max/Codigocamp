// «Iniciar sesión con GitHub»: el Git real usa la sesión solo para github.com y la pide al hacer push.
import { test } from "node:test";
import assert from "node:assert/strict";
import { MotorGit } from "../js/trabajo/gitreal.js";
import { esGitHub } from "../js/trabajo/sesiongithub.js";

function credencialFalsa(tokenAlIniciar = "gho_nuevo") {
  return {
    t: null, pedidas: 0, invalidadas: 0, usuario: "cristian",
    get token() { return this.t; },
    tokenPara(url) { return esGitHub(url) ? this.t : null; },
    async obtener() { this.pedidas += 1; this.t = tokenAlIniciar; return this.t; },
    invalidar() { this.invalidadas += 1; this.t = null; },
  };
}
const motor = (credencial) => new MotorGit({ git: {}, fs: { promises: {} }, http: {}, corsProxy: null, credencial });
const io = () => { const o = { salida: "", lineas: [] }; o.out = (s) => { o.salida += s; }; o.err = (s) => { o.salida += s; }; o.leerLinea = async () => o.lineas.shift() ?? null; return o; };

test("esGitHub reconoce solo github.com", () => {
  assert.equal(esGitHub("https://github.com/a/b.git"), true);
  assert.equal(esGitHub("https://www.github.com/a/b"), true);
  assert.equal(esGitHub("https://gitlab.com/a/b.git"), false);
  assert.equal(esGitHub("https://github.com.evil.example/a/b"), false);
  assert.equal(esGitHub("http://127.0.0.1:8790/repo.git"), false);
});

test("git push a GitHub sin sesión abre «Iniciar sesión con GitHub» y usa ese token", async () => {
  const c = credencialFalsa();
  const m = motor(c);
  const url = "https://github.com/cristian/finanbot.git";
  let auth = null;
  const r = await m.conRed(io(), async () => { auth = m.red().onAuth(url); return "ok"; }, { siempreToken: true, url });
  assert.equal(r, "ok");
  assert.equal(c.pedidas, 1);
  assert.deepEqual(auth, { username: "x-access-token", password: "gho_nuevo" });
  // segunda vez: ya hay sesión, no se vuelve a pedir
  await m.conRed(io(), async () => "ok", { siempreToken: true, url });
  assert.equal(c.pedidas, 1);
});

test("la sesión de GitHub nunca se envía a otro host", async () => {
  const c = credencialFalsa(); c.t = "gho_secreto";
  const m = motor(c);
  assert.deepEqual(m.red().onAuth("https://gitlab.com/x/y.git"), { cancel: true });
  const o = io(); o.lineas.push("glpat-otro");
  let auth = null;
  await m.conRed(o, async () => { auth = m.red().onAuth("https://gitlab.com/x/y.git"); }, { siempreToken: true, url: "https://gitlab.com/x/y.git" });
  assert.equal(c.pedidas, 0, "para GitLab se pide el token en la terminal");
  assert.equal(auth.password, "glpat-otro");
});

test("si GitHub rechaza la sesión guardada (401) se olvida y se pide iniciar sesión otra vez", async () => {
  const c = credencialFalsa("gho_renovado"); c.t = "gho_vencido";
  const m = motor(c);
  const url = "https://github.com/cristian/finanbot.git";
  let intentos = 0;
  const r = await m.conRed(io(), async () => {
    intentos += 1;
    if (m.red().onAuth(url).password === "gho_vencido") throw Object.assign(new Error("401"), { code: "HttpError", data: { statusCode: 401 } });
    return "publicado";
  }, { siempreToken: true, url });
  assert.equal(r, "publicado");
  assert.equal(c.invalidadas, 1);
  assert.equal(c.pedidas, 1);
  assert.equal(intentos, 2);
});

test("cancelar el inicio de sesión cancela el push", async () => {
  const c = credencialFalsa(); c.obtener = async () => null;
  const m = motor(c);
  await assert.rejects(m.conRed(io(), async () => "x", { siempreToken: true, url: "https://github.com/a/b.git" }), (e) => e.code === "x");
});

test("un 403 (sin permiso en ese repositorio) NO cierra la sesión de GitHub", async () => {
  const c = credencialFalsa(); c.t = "gho_valido";
  const m = motor(c);
  await assert.rejects(m.conRed(io(), async () => { throw Object.assign(new Error("403"), { code: "HttpError", data: { statusCode: 403 } }); },
    { siempreToken: true, url: "https://github.com/otro/repo.git" }));
  assert.equal(c.invalidadas, 0);
  assert.equal(c.token, "gho_valido");
  assert.match(m.mensaje({ code: "HttpError", data: { statusCode: 403 } }), /@cristian no puede escribir/);
});

test("varias cuentas de GitHub: agregar, cambiar, cerrar una y cerrar todas", async () => {
  const mem = () => { const d = new Map(); return { getItem: (k) => d.get(k) ?? null, setItem: (k, v) => d.set(k, String(v)), removeItem: (k) => d.delete(k), d }; };
  globalThis.localStorage = mem(); globalThis.sessionStorage = mem();
  const { SesionGitHub } = await import("../js/trabajo/sesiongithub.js");
  const usuarios = { t1: { login: "ana", name: "Ana", id: 1 }, t2: { login: "ana-trabajo", name: "Ana (trabajo)", id: 2 } };
  const fetchFn = async (_u, o) => { const t = o.headers.Authorization.split(" ")[1]; return { ok: true, status: 200, json: async () => usuarios[t] }; };
  const s = new SesionGitHub({ cuenta: "1", api: async () => ({}), fetchFn });
  await s.aceptar("t1", { recordar: true });
  await s.aceptar("t2", { recordar: false });
  assert.deepEqual(s.cuentas.map((c) => [c.login, c.activa]), [["ana", false], ["ana-trabajo", true]]);
  assert.equal(s.token, "t2");
  assert.ok(!JSON.stringify(s.cuentas).includes("t1"), "la lista para mostrar no lleva tokens");
  assert.ok(s.usar("ana")); assert.equal(s.token, "t1");
  // se lee igual desde el almacenamiento (otra instancia en la misma pestaña)
  const otra = new SesionGitHub({ cuenta: "1", api: async () => ({}), fetchFn });
  assert.equal(otra.usuario, "ana"); assert.equal(otra.cuentas.length, 2);
  // la recordada queda en localStorage, la otra solo en la pestaña
  assert.ok(localStorage.getItem("cc-github-1").includes("t1") && !localStorage.getItem("cc-github-1").includes("t2"));
  s.cerrarSesion("ana"); assert.equal(s.usuario, "ana-trabajo");
  s.cerrarTodas(); assert.equal(s.token, null); assert.equal(s.cuentas.length, 0);
  // formato viejo (una sola cuenta) se sigue leyendo
  localStorage.setItem("cc-github-2", JSON.stringify({ token: "t9", login: "vieja" }));
  assert.equal(new SesionGitHub({ cuenta: "2", api: async () => ({}), fetchFn }).usuario, "vieja");
});
