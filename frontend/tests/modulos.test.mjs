import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { modulosDePagina, resolverRuta } from "../js/trabajo/modulos.js";
import { construirVistaPrevia } from "../js/trabajo/vista.js";
import { normalizarProyecto } from "../js/trabajo/almacen.js";
import { archivosDePlantilla } from "../js/trabajo/plantillas.js";
import { ejecutarNpm } from "../js/trabajo/paquetes.js";

const ts = createRequire(import.meta.url)("/tmp/tsdep/node_modules/typescript");
// Mismo transpilado que transpilarModulo (ejecucion.js), con el compilador instalado en las pruebas.
const transpilar = async (codigo, ruta, { jsxImportSource }) => {
  const r = ts.transpileModule(codigo, { fileName: ruta.replace(/\.m?js$/, ".jsx"), reportDiagnostics: true,
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX, jsxImportSource, isolatedModules: true } });
  const e = (r.diagnostics || []).filter((d) => d.category === 1);
  if (e.length) throw new Error(ts.flattenDiagnosticMessageText(e[0].messageText, "\n"));
  return r.outputText;
};
const decodificar = (url) => decodeURIComponent(url.slice(url.indexOf(",") + 1));

function proyectoReact(plantilla = "react", dir = "mi-app") {
  const files = {};
  for (const [r, t] of Object.entries(archivosDePlantilla(plantilla, "mi-app"))) files[`${dir}/${r}`] = t;
  files[`${dir}/package.json`] = JSON.stringify({ dependencies: { react: "^19.1.0", "react-dom": "^19.1.0" }, devDependencies: { vite: "^7.0.0" } });
  return normalizarProyecto({ files });
}

test("plantilla React: JSX transpilado, imports propios, /vite.svg de public y React desde esm.sh con una sola copia", async () => {
  const py = proyectoReact();
  const m = await modulosDePagina(py, "mi-app/index.html", { transpilar });
  assert.deepEqual(m.errores, []);
  const im = m.importmap.imports;
  assert.equal(m.srcs.get("/src/main.jsx"), "@cc/mi-app/src/main.jsx");
  for (const k of ["@cc/mi-app/src/main.jsx", "@cc/mi-app/src/App.jsx", "@cc/mi-app/src/App.css", "@cc/mi-app/src/index.css", "@cc/mi-app/public/vite.svg"]) assert.ok(im[k], k);
  assert.equal(im.react, "https://esm.sh/react@19.1.0?external=react-dom,vite");
  assert.equal(im["react-dom/client"], "https://esm.sh/react-dom@19.1.0/client?external=react,vite");
  assert.ok(im["react/jsx-runtime"].startsWith("https://esm.sh/react@19.1.0/jsx-runtime"));
  const main = decodificar(im["@cc/mi-app/src/main.jsx"]);
  assert.match(main, /from "react\/jsx-runtime"/);
  assert.match(main, /import App from ['"]@cc\/mi-app\/src\/App\.jsx['"]/);
  assert.doesNotMatch(main, /<App \/>/, "el JSX ya no está");
  assert.match(decodificar(im["@cc/mi-app/src/App.css"]), /document\.createElement\("style"\)/);
  const html = construirVistaPrevia(py, "mi-app/index.html", { modulos: m });
  assert.match(html, /<script type="importmap">/);
  assert.ok(html.indexOf("importmap") < html.indexOf('<script type="module">'), "el import map va antes de los módulos");
  assert.match(html, /<script type="module">import "@cc\/mi-app\/src\/main\.jsx";<\/script>/);
});

test("TypeScript + React, Preact y vanilla también se preparan", async () => {
  const tsx = await modulosDePagina(proyectoReact("react-ts"), "mi-app/index.html", { transpilar });
  assert.deepEqual(tsx.errores, []);
  assert.doesNotMatch(decodificar(tsx.importmap.imports["@cc/mi-app/src/App.tsx"]), /useState<number>/);
  const files = {};
  for (const [r, t] of Object.entries(archivosDePlantilla("preact", "p"))) files[r] = t;
  files["package.json"] = JSON.stringify({ dependencies: { preact: "^10.26.0" } });
  const pre = await modulosDePagina(normalizarProyecto({ files }), "index.html", { transpilar });
  assert.deepEqual(pre.errores, []);
  assert.ok(pre.importmap.imports["preact/jsx-runtime"], "JSX de Preact");
  assert.ok(pre.importmap.imports["preact/hooks"]);
  const van = {};
  for (const [r, t] of Object.entries(archivosDePlantilla("vanilla-ts", "v"))) van[r] = t;
  const v = await modulosDePagina(normalizarProyecto({ files: van }), "index.html", { transpilar });
  assert.deepEqual(v.errores, []);
  assert.ok(v.importmap.imports["@cc/src/counter.ts"]);
});

test("errores claros: paquete sin instalar, archivo inexistente, JSX roto; CSS de paquetes; JSON e imágenes", async () => {
  const py = normalizarProyecto({ files: {
    "package.json": JSON.stringify({ dependencies: { bootstrap: "5.3.3", react: "19.1.0" } }),
    "index.html": '<script type="module">import "./app.js";</script>',
    "app.js": 'import "bootstrap/dist/css/bootstrap.min.css";\nimport datos from "./datos.json";\nimport foto from "./foto.png";\nimport axios from "axios";\nimport x from "./nada.js";\nimport "./roto.jsx";\nconsole.log(datos, foto);',
    "datos.json": '{"a": 1}', "foto.png": "ccbin:v1:" + "a".repeat(64) + ":image/png:10", "roto.jsx": "const a = <div>;",
  } });
  const m = await modulosDePagina(py, "index.html", { transpilar, enlaces: new Map([["a".repeat(64), "http://h/p/FOTO"]]) });
  const im = m.importmap.imports;
  assert.match(decodificar(im["bootstrap/dist/css/bootstrap.min.css"]), /cdn\.jsdelivr\.net\/npm\/bootstrap@5\.3\.3\/dist\/css\/bootstrap\.min\.css/);
  assert.match(decodificar(im["@cc/datos.json"]), /export default \{"a":1\}/);
  assert.match(decodificar(im["@cc/foto.png"]), /http:\/\/h\/p\/FOTO/);
  assert.match(decodificar(im.axios), /npm install axios/);
  assert.ok(m.errores.some((e) => /nada\.js/.test(e)));
  assert.ok(m.errores.some((e) => /roto\.jsx/.test(e)));
  assert.equal(resolverRuta(py, "", "./app", ""), "app.js", "sin extensión, como Vite");
});

test("npm create vite: crea la carpeta con package.json de versiones actuales y npm install trabaja en esa carpeta", async () => {
  const py = normalizarProyecto({ files: { "README.md": "x" } });
  let out = "", err = "";
  const fetchFn = async (url) => ({ ok: true, status: 200, json: async () => ({ version: url.includes("/react@") || url.includes("/react-dom@") ? "19.2.0" : "7.1.0" }) });
  const codigo = await ejecutarNpm({ args: ["create", "vite@latest", "mi-app", "--", "--template", "react"], proyecto: py, out: (t) => { out += t; }, err: (t) => { err += t; }, fetchFn });
  assert.equal(codigo, 0, err);
  const pkg = JSON.parse(py.files["mi-app/package.json"]);
  assert.equal(pkg.dependencies.react, "^19.2.0");
  assert.equal(pkg.scripts.dev, "vite");
  assert.ok("mi-app/src/App.jsx" in py.files && "mi-app/public/vite.svg" in py.files);
  assert.match(out, /cd mi-app[\s\S]*npm run dev/);
  const r = await ejecutarNpm({ args: ["install", "axios"], proyecto: py, out: () => {}, err: (t) => { err += t; }, fetchFn, cwd: "mi-app/src" });
  assert.equal(r, 0, err);
  assert.ok("axios" in JSON.parse(py.files["mi-app/package.json"]).dependencies, "se guardó en el package.json de la carpeta");
  assert.ok(!("package.json" in py.files));
  const otra = await ejecutarNpm({ args: ["create", "vite", "mi-app", "--template", "react"], proyecto: py, out: () => {}, err: (t) => { err += t; }, fetchFn });
  assert.equal(otra, 1);
  assert.match(err, /no está vacía/);
});

test("Vite: alias de vite.config.js, import.meta.env de .env y CSS Modules", async () => {
  const py = normalizarProyecto({ files: {
    "app/package.json": JSON.stringify({ dependencies: { react: "19.1.0", "react-dom": "19.1.0" } }),
    "app/vite.config.js": "import { defineConfig } from 'vite'\nimport react from '@vitejs/plugin-react'\nimport path from 'path'\nexport default defineConfig({\n  plugins: [react()],\n  resolve: { alias: { '@': path.resolve(__dirname, './src'), '~assets': '/src/assets' } },\n})\n",
    "app/.env": "VITE_API_URL=http://localhost:5000/api\nSECRETO=no-debe-llegar\nVITE_TITULO=\"Finanbot\" # comentario\n",
    "app/index.html": '<div id="root"></div><script type="module" src="/src/main.jsx"></script>',
    "app/src/main.jsx": "import { saludo } from '@/utils/saludo'\nimport s from './App.module.css'\nimport logo from '~assets/logo.svg'\nconsole.log(saludo(), import.meta.env.VITE_API_URL, import.meta.env.MODE, s.tarjeta, logo)\n",
    "app/src/utils/saludo.js": "export const saludo = () => 'hola'",
    "app/src/assets/logo.svg": "<svg/>",
    "app/src/App.module.css": ".tarjeta { padding: .5rem; transition: opacity .3s } .tarjeta:hover .titulo { color: red }",
  } });
  const m = await modulosDePagina(py, "app/index.html", { transpilar });
  assert.deepEqual(m.errores, []);
  const main = decodificar(m.importmap.imports["@cc/app/src/main.jsx"]);
  assert.match(main, /@cc\/app\/src\/utils\/saludo\.js/);
  assert.match(main, /@cc\/app\/src\/assets\/logo\.svg/);
  assert.match(main, /"VITE_API_URL":"http:\/\/localhost:5000\/api"/);
  assert.match(main, /"VITE_TITULO":"Finanbot"/);
  assert.doesNotMatch(main, /SECRETO/, "solo las VITE_* llegan al navegador");
  const css = decodificar(m.importmap.imports["@cc/app/src/App.module.css"]);
  assert.match(css, /\.tarjeta_\w+/);
  assert.match(css, /padding: \.5rem/, "los valores como .5rem no se tocan");
  assert.match(css, /export default \{"tarjeta":"tarjeta_\w+","titulo":"titulo_\w+"\}/);
});
