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
