import test from "node:test";
import assert from "node:assert/strict";
import { publicar, interpretarRemoto, base64Utf8 } from "../js/trabajo/github.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";

const sha = (t) => { let h = 5381; for (const c of String(t)) h = ((h << 5) + h + c.charCodeAt(0)) >>> 0; return h.toString(16).padStart(8, "0") + "0".repeat(32); };

/** GitHub falso con la parte de la API REST que usa publicar(). */
function github({ vacio = false, readme = true, permisoEscritura = true, token = "tok" } = {}) {
  const e = { blobs: {}, arboles: {}, commits: {}, ramas: {}, llamadas: [], tokenVisto: null };
  if (!vacio) {
    e.blobs[sha("README")] = "README";
    const a = sha(JSON.stringify({ "README.md": sha("README") })); e.arboles[a] = readme ? { "README.md": sha("README") } : {};
    const c = sha("c0"); e.commits[c] = { tree: a, parents: [], message: "init" }; e.ramas.main = c;
  }
  const resp = (estado, datos) => ({ ok: estado < 400, status: estado, json: async () => datos });
  e.fetch = async (url, { method, headers, body }) => {
    const ruta = url.replace("https://api.github.com", ""); const b = body ? JSON.parse(body) : null;
    e.llamadas.push(`${method} ${ruta}`); e.tokenVisto = headers.Authorization;
    if (e.sinRed) throw new TypeError("Failed to fetch");
    if (headers.Authorization !== `Bearer ${token}`) return resp(401, { message: "Bad credentials" });
    let m;
    if ((m = /^\/repos\/ana\/proy$/.exec(ruta))) return method === "GET" ? resp(200, { default_branch: "main", size: vacio && !Object.keys(e.ramas).length ? 0 : 1, permissions: { push: permisoEscritura } }) : resp(404, {});
    if (!ruta.startsWith("/repos/ana/proy")) return resp(404, { message: "Not Found" });
    const r = ruta.slice("/repos/ana/proy".length);
    const vacioAhora = !Object.keys(e.ramas).length;
    if ((m = /^\/git\/ref\/heads\/(.+)$/.exec(r))) { if (vacioAhora) return resp(409, { message: "Git Repository is empty." }); const s = e.ramas[decodeURIComponent(m[1])]; return s ? resp(200, { object: { sha: s } }) : resp(404, { message: "Not Found" }); }
    if (r === "/git/blobs") { if (vacioAhora) return resp(409, { message: "Git Repository is empty." }); const s = sha(b.content); e.blobs[s] = b.content; return resp(201, { sha: s }); }
    if ((m = /^\/git\/commits\/(\w+)$/.exec(r))) return e.commits[m[1]] ? resp(200, { tree: { sha: e.commits[m[1]].tree } }) : resp(404, {});
    if (r === "/git/trees") { const base = b.base_tree ? { ...e.arboles[b.base_tree] } : {}; b.tree.forEach((t) => { base[t.path] = t.sha; }); const s = sha(JSON.stringify(Object.fromEntries(Object.entries(base).sort()))); e.arboles[s] = base; return resp(201, { sha: s }); }
    if (r === "/git/commits") { const s = sha("c" + JSON.stringify(b)); e.commits[s] = { tree: b.tree, parents: b.parents, message: b.message }; return resp(201, { sha: s }); }
    if (r === "/git/refs") { e.ramas[b.ref.replace("refs/heads/", "")] = b.sha; return resp(201, {}); }
    if ((m = /^\/git\/refs\/heads\/(.+)$/.exec(r)) && method === "PATCH") { e.ramas[decodeURIComponent(m[1])] = b.sha; return resp(200, {}); }
    if ((m = /^\/contents\/(.+)$/.exec(r)) && method === "PUT") { const t = sha("T" + m[1]); e.arboles[t] = { [decodeURIComponent(m[1])]: sha(atob(b.content)) }; const c = sha("cc" + m[1]); e.commits[c] = { tree: t, parents: [], message: b.message }; e.ramas[b.branch] = c; return resp(201, {}); }
    return resp(404, { message: "ruta no simulada " + r });
  };
  return e;
}
const proyecto = (extra = {}) => { const py = normalizarProyecto({ files: { "index.html": "<h1>Hola ñandú</h1>", "src/app.js": "x" } });
  py.git = { ...py.git, initialized: true, branch: "main", remote: "https://github.com/ana/proy.git", committed: { "index.html": "<h1>Hola ñandú</h1>", "src/app.js": "x" }, commits: [{ hash: "abc1234", message: "segundo", date: "d" }, { hash: "abc1233", message: "primero", date: "d" }], ...extra }; return py; };
const pub = (gh, py, token = "tok", progreso = () => {}) => publicar({ py, token, fetchFn: gh.fetch, progreso });

test("interpretarRemoto y base64 con acentos", () => {
  assert.deepEqual(interpretarRemoto("https://github.com/ana/proy.git"), { owner: "ana", repo: "proy" });
  assert.deepEqual(interpretarRemoto("https://github.com/ana/mi.repo"), { owner: "ana", repo: "mi.repo" });
  assert.equal(interpretarRemoto("https://gitlab.com/a/b"), null);
  assert.equal(atob(base64Utf8("a")), "a");
  assert.equal(new TextDecoder().decode(Uint8Array.from(atob(base64Utf8("ñandú €")), (c) => c.charCodeAt(0))), "ñandú €");
});

test("repo existente con README: añade los archivos SIN borrar lo que ya había y avanza la rama", async () => {
  const gh = github(); const avances = [];
  const r = await pub(gh, proyecto(), "tok", (t) => avances.push(t));
  assert.equal(r.rama_nueva, false);
  const c = gh.commits[gh.ramas.main];
  assert.deepEqual(c.parents, [sha("c0")], "el padre es el commit anterior de GitHub");
  assert.deepEqual(Object.keys(gh.arboles[c.tree]).sort(), ["README.md", "index.html", "src/app.js"], "README conservado");
  assert.match(c.message, /^segundo\n\nCommits locales incluidos[\s\S]*- segundo\n- primero/);
  assert.equal(r.url, `https://github.com/ana/proy/commit/${gh.ramas.main}`);
  assert.ok(avances.some((a) => a.includes("2/2")));
});

test("publicar de nuevo sin cambios no crea otro commit", async () => {
  const gh = github(); const py = proyecto();
  await pub(gh, py); const tip = gh.ramas.main;
  const r = await pub(gh, py);
  assert.equal(r.sinCambios, true); assert.equal(gh.ramas.main, tip);
});

test("repositorio vacío: crea el commit inicial y publica todo", async () => {
  const gh = github({ vacio: true });
  const r = await pub(gh, proyecto());
  assert.ok(gh.llamadas.some((l) => l.startsWith("PUT /repos/ana/proy/contents/index.html")));
  const c = gh.commits[gh.ramas.main];
  assert.deepEqual(Object.keys(gh.arboles[c.tree]).sort(), ["index.html", "src/app.js"]);
  assert.equal(c.parents.length, 1);
  assert.ok(r.sha);
});

test("rama nueva parte de la rama por defecto", async () => {
  const gh = github(); const py = proyecto(); py.git.branch = "feature/x";
  const r = await pub(gh, py);
  assert.equal(r.rama_nueva, true);
  assert.deepEqual(gh.commits[gh.ramas["feature/x"]].parents, [sha("c0")]);
  assert.equal(gh.ramas.main, sha("c0"), "main no se toca");
});

test("el token solo viaja en la cabecera Authorization hacia api.github.com", async () => {
  const gh = github({ token: "ghp_secreto" }); const urls = [];
  const fetchFn = (u, o) => { urls.push(u); assert.ok(!u.includes("ghp_secreto")); assert.ok(!String(o.body || "").includes("ghp_secreto")); return gh.fetch(u, o); };
  await publicar({ py: proyecto(), token: "ghp_secreto", fetchFn });
  assert.ok(urls.every((u) => u.startsWith("https://api.github.com/")));
});

test("errores con mensajes claros: token malo, sin permiso, repo inexistente, sin red, sin remoto", async () => {
  await assert.rejects(pub(github(), proyecto(), "malo"), /rechazó el token/);
  await assert.rejects(pub(github({ permisoEscritura: false }), proyecto()), /necesita permiso de escritura/);
  const py = proyecto(); py.git.remote = "https://github.com/ana/otro.git";
  await assert.rejects(pub(github(), py), /No se encontró el repositorio ana\/otro/);
  const sinRed = github(); sinRed.sinRed = true;
  await assert.rejects(pub(sinRed, proyecto()), /No se pudo conectar con GitHub/);
  const sin = proyecto(); sin.git.remote = "";
  await assert.rejects(pub(github(), sin), /no es una URL de GitHub/);
  const vacio = proyecto(); vacio.git.committed = {};
  await assert.rejects(pub(github(), vacio), /No hay archivos/);
});

test("push de imágenes: se publican sus bytes reales, no el marcador de texto", async () => {
  const gh = github();
  const marcador = "ccbin:v1:" + "d".repeat(64) + ":image/png:4";
  const py = proyecto({ committed: { "index.html": "<img src='a.png'>", "a.png": marcador } });
  py.files["a.png"] = marcador;
  const pedidas = [];
  await publicar({ py, token: "tok", fetchFn: gh.fetch, binario: async (m) => { pedidas.push(m); return new Uint8Array([0x89, 0x50, 0x4e, 0x47]); } });
  assert.deepEqual(pedidas, [marcador]);
  const contenidos = Object.values(gh.blobs);
  assert.ok(contenidos.includes(btoa("\x89PNG")), "el blob lleva los bytes en base64");
  assert.ok(!contenidos.some((c) => String(c).includes("ccimg:")), "el marcador nunca llega a GitHub");
  await assert.rejects(publicar({ py, token: "tok", fetchFn: github().fetch }), /archivo a\.png/);
});

test("push: los archivos de más de 100 MB no se envían (GitHub los rechaza) y se informan", async () => {
  const gh = github();
  const enorme = "ccbin:v1:" + "f".repeat(64) + ":video/mp4:" + (150 * 1024 * 1024);
  const py = proyecto({ committed: { "index.html": "<h1>x</h1>", "video.mp4": enorme } });
  const pedidas = [];
  const r = await publicar({ py, token: "tok", fetchFn: gh.fetch, binario: async (m) => { pedidas.push(m); return new Uint8Array(1); } });
  assert.deepEqual(pedidas, [], "ni siquiera se descarga");
  assert.equal(r.omitidos[0].ruta, "video.mp4");
  assert.match(r.omitidos[0].motivo, /100 MB/);
});
