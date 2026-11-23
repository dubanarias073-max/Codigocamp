// Servidores de desarrollo de Trabajo, como en VS Code: cada uno queda en el panel PUERTOS y se abre en la vista previa.
//  · En el navegador: node/Express (http.createServer), nodemon / node --watch, servidores estáticos
//    (python -m http.server, npx serve, http-server, live-server) y Expo (con Expo Snack: web + QR para Expo Go).
//  · En el servidor de CódigoCamp: php -S (el servidor real de PHP).
//  · En Docker (si el servidor lo tiene): Next.js, Nuxt, Angular, Astro, Laravel, Rails, Spring Boot, Go, .NET…
import { color } from "./ansi.js";
import * as FS from "./fs.js";
import { esMarcador } from "./archivos.js";
import { alCambiarProyecto, avisar, detenerServidor, esperarDetencion, quitarServidor, registrarServidor, servidores } from "./puertos.js";

const MIME = { html: "text/html; charset=utf-8", htm: "text/html; charset=utf-8", css: "text/css; charset=utf-8", js: "text/javascript; charset=utf-8", mjs: "text/javascript; charset=utf-8", json: "application/json; charset=utf-8", txt: "text/plain; charset=utf-8", md: "text/plain; charset=utf-8", svg: "image/svg+xml", png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp", ico: "image/x-icon", pdf: "application/pdf", mp3: "audio/mpeg", mp4: "video/mp4", woff: "font/woff", woff2: "font/woff2", xml: "application/xml", csv: "text/csv; charset=utf-8", php: "text/plain; charset=utf-8" };
const mime = (r) => MIME[r.split(".").pop().toLowerCase()] || "application/octet-stream";
const enc = new TextEncoder();
const fecha = () => new Date().toUTCString().replace(/ GMT$/, "");
const respuesta = (status, tipo, cuerpo, extra = []) => ({ status, headers: [["content-type", tipo], ...extra], body: typeof cuerpo === "string" ? enc.encode(cuerpo) : cuerpo });
const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/** Opción con valor: -p 8080 / --port=8080 / --port 8080 */
function opcion(a, nombres) {
  for (let i = 0; i < a.length; i += 1) {
    for (const n of nombres) {
      if (a[i] === n) return a[i + 1];
      if (a[i].startsWith(n + "=")) return a[i].slice(n.length + 1);
    }
  }
  return undefined;
}
const sinOpciones = (a, conValor) => a.filter((x, i) => !x.startsWith("-") && !conValor.includes(a[i - 1]));

function puertoOcupado(io, puerto, quien) {
  const s = servidores.get(Number(puerto));
  io.err(`${quien}: el puerto ${puerto} ya está en uso${s ? ` por «${s.comando || s.framework}»` : ""}. Detén ese servidor (panel PUERTOS) o usa otro puerto.\n`);
  return 1;
}

export function instalarServidoresDev(COMANDOS, { contexto, archivoAEjecutar, ejecutorNo, ruta }) {
  // ------------------------------------------------------------------- servidor estático (archivos) ----
  async function servirEstatico(shell, io, { dir = ".", puerto, quien, estilo, recarga = true, spa = false, abrir = true }) {
    const py = io.py();
    const raiz = ruta(io, dir);
    if (raiz === null || !(raiz === "" || FS.esCarpeta?.(py, raiz) || py.folders?.includes(raiz) || Object.keys(py.files).some((r) => r.startsWith(raiz + "/")))) { io.err(`${quien}: no existe la carpeta '${dir}'\n`); return 1; }
    const bytesDe = shell.ejecutores.bytesDe;
    const log = (metodo, url, status) => {
      if (estilo === "python") io.out(`127.0.0.1 - - [${new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).replace(/ /g, "/")} ${new Date().toTimeString().slice(0, 8)}] "${metodo} ${url} HTTP/1.1" ${status} -\n`);
      else if (estilo === "serve") io.out(` ${color.gris("HTTP")}  ${new Date().toLocaleString("en-US")} ::1 ${metodo} ${url}\n ${color.gris("HTTP")}  ${new Date().toLocaleString("en-US")} ::1 Returned ${status}\n`);
      else io.out(`[${fecha()}] "${metodo} ${url}" ${status === 404 ? color.rojo("Error (404): \"Not found\"") : ""}\n`);
    };
    const reg = {
      framework: { python: "http.server", serve: "serve", "http-server": "http-server", "live-server": "Live Server" }[estilo] || "Estático", comando: io.comandoTexto || quien,
      pedir: async (req) => {
        const p = io.py();
        let camino = (req.url || "/").split("?")[0];
        try { camino = decodeURIComponent(camino); } catch { /* nada */ }
        let r = FS.unir ? FS.unir(raiz, camino.replace(/^\/+/, "")) : [raiz, camino.replace(/^\/+/, "")].filter(Boolean).join("/");
        r = r.replace(/\/+$/, "");
        const esDir = r === raiz || p.folders?.includes(r) || Object.keys(p.files).some((x) => x.startsWith(r + "/"));
        if (esDir && !(r in p.files)) {
          const indice = [r ? r + "/index.html" : "index.html", r ? r + "/index.htm" : "index.htm"].find((x) => x in p.files);
          if (indice) r = indice;
          else if (estilo === "python" || estilo === "http-server" || estilo === "serve") {
            const pre = r ? r + "/" : "";
            const hijos = [...new Set([...Object.keys(p.files), ...(p.folders || [])].filter((x) => x.startsWith(pre) && x !== r).map((x) => x.slice(pre.length).split("/")[0] + (x.slice(pre.length).includes("/") || (p.folders || []).includes(pre + x.slice(pre.length).split("/")[0]) ? "/" : "")))].sort();
            log(req.method || "GET", req.url, 200);
            const base = camino.endsWith("/") ? camino : camino + "/";
            return respuesta(200, "text/html; charset=utf-8", `<!DOCTYPE HTML><html lang="en"><head><meta charset="utf-8"><title>Directory listing for ${esc(base)}</title></head><body><h1>Directory listing for ${esc(base)}</h1><hr><ul>${hijos.map((h) => `<li><a href="${esc(base + h)}">${esc(h)}</a></li>`).join("")}</ul><hr></body></html>`);
          }
        }
        if (!(r in p.files) && spa) r = [raiz ? raiz + "/index.html" : "index.html"].find((x) => x in p.files) ?? r;
        if (!(r in p.files)) {
          log(req.method || "GET", req.url, 404);
          return respuesta(404, "text/html; charset=utf-8", estilo === "python" ? `<!DOCTYPE HTML><html lang="en"><head><meta charset="utf-8"><title>Error response</title></head><body><h1>Error response</h1><p>Error code: 404</p><p>Message: File not found.</p></body></html>` : "<h1>404 - Not Found</h1>");
        }
        log(req.method || "GET", req.url, 200);
        const contenido = p.files[r];
        if (esMarcador(contenido)) { try { return respuesta(200, mime(r), await bytesDe(contenido)); } catch { return respuesta(500, "text/plain", "No se pudo leer el archivo."); } }
        return respuesta(200, mime(r), contenido);
      },
    };
    if (!registrarServidor(puerto, reg)) return puertoOcupado(io, puerto, quien);
    const quitar = recarga ? alCambiarProyecto(() => { clearTimeout(reg.t); reg.t = setTimeout(avisar, 250); }) : () => {};
    if (abrir) shell.abrirUrl?.(`http://localhost:${puerto}/`);
    await esperarDetencion(io.sesion.senal, puerto);
    quitar();
    quitarServidor(puerto, servidores.get(Number(puerto)));
    return 130;
  }

  // python -m http.server [puerto] [-d dir]
  COMANDOS.__httpServerPython = async function (a, io) {
    const puerto = Number(sinOpciones(a, ["-d", "--directory", "-b", "--bind"])[0] || 8000);
    const dir = opcion(a, ["-d", "--directory"]) || ".";
    io.out(`Serving HTTP on :: port ${puerto} (http://[::]:${puerto}/) ...\n`);
    io.out(color.gris(`  → http://localhost:${puerto} en la vista previa · panel PUERTOS · Ctrl+C detiene\n`));
    const c = await servirEstatico(this, { ...io, comandoTexto: `python -m http.server ${puerto}` }, { dir, puerto, quien: "http.server", estilo: "python" });
    if (c === 130) io.out("\nKeyboard interrupt received, exiting.\n");
    return c;
  };
  COMANDOS.serve = async function (a, io) {
    const p = opcion(a, ["-l", "--listen", "-p", "--port"]);
    const puerto = Number(String(p || "3000").replace(/^.*:/, "")) || 3000;
    const dir = sinOpciones(a, ["-l", "--listen", "-p", "--port", "-c", "--config"])[0] || ".";
    io.out(`\n   ┌─────────────────────────────────────────┐\n   │                                         │\n   │   ${color.verde("Serving!")}                              │\n   │                                         │\n   │   - Local:    ${color.cian(`http://localhost:${puerto}`)}     │\n   │                                         │\n   └─────────────────────────────────────────┘\n\n`);
    return servirEstatico(this, { ...io, comandoTexto: `serve ${dir}` }, { dir, puerto, quien: "serve", estilo: "serve", spa: a.includes("-s") || a.includes("--single") });
  };
  COMANDOS["http-server"] = async function (a, io) {
    const puerto = Number(opcion(a, ["-p", "--port"]) || 8080);
    const dir = sinOpciones(a, ["-p", "--port", "-a", "-c"])[0] || (FS.tieneArchivo(io.py(), "public/index.html") ? "public" : ".");
    io.out(`${color.amarillo("Starting up http-server, serving")} ${color.cian("./" + dir.replace(/^\.\/?/, ""))}\n\nhttp-server version: 14.1.1\n\n${color.amarillo("Available on:")}\n  http://127.0.0.1:${color.verde(String(puerto))}\nHit CTRL-C to stop the server\n\n`);
    const c = await servirEstatico(this, { ...io, comandoTexto: `http-server ${dir}` }, { dir, puerto, quien: "http-server", estilo: "http-server" });
    if (c === 130) io.out(color.rojo("http-server stopped.\n"));
    return c;
  };
  COMANDOS["live-server"] = async function (a, io) {
    const puerto = Number(opcion(a, ["--port"]) || 8080);
    const dir = sinOpciones(a, ["--port", "--host", "--open", "--entry-file", "--wait"])[0] || ".";
    io.out(`Serving "${dir}" at http://127.0.0.1:${puerto}\nReady for changes\n`);
    return servirEstatico(this, { ...io, comandoTexto: `live-server ${dir}` }, { dir, puerto, quien: "live-server", estilo: "live-server", spa: a.some((x) => x.startsWith("--entry-file")) });
  };

  // ---------------------------------------------------------------- node --watch / nodemon ----
  async function conRecarga(shell, io, args, { nombre }) {
    const ej = shell.ejecutores.node;
    if (!ej) return ejecutorNo(io, "node");
    const py = io.py();
    let archivo = args.find((x) => !x.startsWith("-"));
    if (!archivo) {
      let pkg = null; try { pkg = JSON.parse(py.files[FS.unir(io.sesion.cwd || "", "package.json")] || py.files["package.json"] || "null"); } catch { /* nada */ }
      archivo = pkg?.main || ["server.js", "app.js", "index.js", "src/index.js", "src/server.js"].find((x) => FS.tieneArchivo(py, FS.unir(io.sesion.cwd || "", x)));
      if (!archivo) { io.err(`${nombre}: indica el archivo: ${nombre} server.js\n`); return 1; }
    }
    const resto = args.slice(args.indexOf(archivo) + 1);
    const senalTerminal = io.sesion.senal;
    const nm = nombre === "nodemon";
    const am = (t) => io.out(color.amarillo(t) + "\n");
    if (nm) { am("[nodemon] 3.1.4"); am("[nodemon] to restart at any time, enter `rs`"); am("[nodemon] watching path(s): *.*"); am("[nodemon] watching extensions: js,mjs,cjs,json"); am(`[nodemon] starting \`node ${archivo}\``); }
    let primera = true;
    while (!senalTerminal?.aborted) {
      const ctrl = new AbortController();
      const cortar = () => ctrl.abort();
      senalTerminal?.addEventListener("abort", cortar, { once: true });
      let reinicio = false, espera = 0;
      const cambio = () => { clearTimeout(espera); espera = setTimeout(() => { reinicio = true; ctrl.abort(); }, 350); };
      // Los archivos que escribe tu propio programa (db.json, logs…) no reinician el servidor
      const quitar = alCambiarProyecto((origen) => { if (origen !== "ejecucion" && origen !== "remoto-ejecucion") cambio(); });
      const f = archivoAEjecutar(shell, io, "node", archivo, ["js", "mjs", "cjs"]);
      if (!f) { quitar(); senalTerminal?.removeEventListener("abort", cortar); return 1; }
      const ioCiclo = { ...io, sesion: { ...io.sesion, senal: ctrl.signal } };
      const codigo = await ej({ ...contexto(shell, ioCiclo), abrir: primera ? shell.abrirUrl : null, comando: `${nombre} ${archivo}`, ruta: f.ruta, codigo: f.codigo, args: resto });
      primera = false;
      senalTerminal?.removeEventListener("abort", cortar);
      if (senalTerminal?.aborted) { quitar(); return 130; }
      if (!reinicio) {
        if (nm) am(codigo === 0 ? "[nodemon] clean exit - waiting for changes before restart" : color.rojo("[nodemon] app crashed - waiting for file changes before starting..."));
        else io.out(color.gris(codigo === 0 ? `Completed running '${archivo}'. Waiting for file changes before restarting...\n` : `Failed running '${archivo}'. Waiting for file changes before restarting...\n`));
        await new Promise((listo) => { const q = alCambiarProyecto((origen) => { if (origen !== "ejecucion") { q(); listo(); } }); senalTerminal?.addEventListener("abort", () => { q(); listo(); }, { once: true }); });
        if (senalTerminal?.aborted) { quitar(); return 130; }
      }
      quitar();
      if (nm) { am("[nodemon] restarting due to changes..."); am(`[nodemon] starting \`node ${archivo}\``); } else io.out(color.gris(`Restarting '${archivo}'\n`));
    }
    return 130;
  }
  COMANDOS.nodemon = function (a, io) { return conRecarga(this, io, a.filter((x) => !["--exec", "-e", "--ext", "-w", "--watch", "--ignore", "-i"].includes(x)), { nombre: "nodemon" }); };
  COMANDOS.__nodeWatch = function (a, io) { return conRecarga(this, io, a.filter((x) => !x.startsWith("--watch")), { nombre: "node --watch" }); };

  // ------------------------------------------------------------------------ php -S (real) ----
  COMANDOS.__phpServidor = async function (a, io) {
    const pedirApi = this.ejecutores.phpServidor;
    if (!pedirApi) return ejecutorNo(io, "php -S");
    const dir = a[a.indexOf("-S") + 1] || "localhost:8000";
    const puerto = Number(dir.split(":").pop()) || 8000;
    const docroot = ruta(io, opcion(a, ["-t"]) || ".") ?? "";
    const router = sinOpciones(a, ["-S", "-t", "-c", "-d"]).find((x) => x.endsWith(".php"));
    if (servidores.has(puerto)) return puertoOcupado(io, puerto, "php");
    const textos = () => { const p = io.py(); return Object.keys(p.files).filter((r) => !esMarcador(p.files[r]) && !/(^|\/)(node_modules|\.git|vendor\/bin)\//.test(r)).map((r) => ({ ruta: r, contenido: p.files[r] })); };
    io.out(color.gris("Encendiendo el servidor de PHP…\n"));
    let r;
    try { r = await pedirApi("iniciar", { archivos: textos(), docroot, router: router ? (ruta(io, router) ?? router) : null }); }
    catch (e) { io.err(`${e.message}\n`); return 1; }
    io.out(`[${fecha()}] PHP ${r.version} Development Server (http://${dir}) started\n`);
    io.out(color.gris(`  → http://localhost:${puerto} en la vista previa · panel PUERTOS · Ctrl+C detiene\n`));
    const bytesDe = this.ejecutores.bytesDe;
    let sincronizando = Promise.resolve();
    const reg = {
      framework: "PHP", comando: `php -S ${dir}`,
      pedir: async (req) => {
        await sincronizando;
        // Imágenes y otros binarios del proyecto: se sirven desde aquí (el servidor de PHP solo tiene los textos)
        const camino = decodeURIComponent((req.url || "/").split("?")[0]).replace(/^\/+/, "");
        const real = [docroot, camino].filter(Boolean).join("/");
        const p = io.py();
        if (real in p.files && esMarcador(p.files[real])) { try { return respuesta(200, mime(real), await bytesDe(p.files[real])); } catch { /* sigue */ } }
        const cuerpo = req.body ? btoa(String.fromCharCode(...(typeof req.body === "string" ? enc.encode(req.body) : new Uint8Array(req.body)))) : "";
        try {
          const d = await pedirApi("pedir", { metodo: req.method || "GET", ruta: req.url || "/", cabeceras: req.headers || [], cuerpo });
          for (const l of d.log || []) io.out(/\[(4|5)\d\d\]/.test(l) ? color.amarillo(l) + "\n" : l + "\n");
          return { status: d.status, headers: d.headers, body: Uint8Array.from(atob(d.cuerpo || ""), (c) => c.charCodeAt(0)) };
        } catch (e) { return respuesta(502, "text/plain; charset=utf-8", e.message); }
      },
      detener: () => { pedirApi("detener", {}).catch(() => {}); },
    };
    if (!registrarServidor(puerto, reg)) return puertoOcupado(io, puerto, "php");
    const quitar = alCambiarProyecto(() => { clearTimeout(reg.t); reg.t = setTimeout(() => { sincronizando = pedirApi("sincronizar", { archivos: textos() }).catch(() => {}).then(avisar); }, 300); });
    this.abrirUrl?.(`http://localhost:${puerto}/`);
    await esperarDetencion(io.sesion.senal, puerto);
    quitar();
    quitarServidor(puerto, servidores.get(puerto));
    pedirApi("detener", {}).catch(() => {});
    return 130;
  };

  // --------------------------------------------------------------------------------- Expo ----
  // Metro necesita Node completo; Expo Snack corre tu app en la web y en tu celular (Expo Go) sin instalar nada.
  COMANDOS.expo = async function (a, io) {
    const sub = a[0] && !a[0].startsWith("-") ? a[0] : "start";
    if (sub === "install" || sub === "add") return COMANDOS.npm.call(this, ["install", ...a.slice(1)], io);
    if (!["start", "web", "android", "ios"].includes(sub)) { io.err(`expo: «${sub}» no está disponible aquí. Usa: npx expo start (web, celular con QR) o npx expo install <paquete>.\n`); return 1; }
    const py = io.py();
    const cwd = io.sesion.cwd || "";
    const dentro = (r) => (cwd ? r.startsWith(cwd + "/") : true);
    const rel = (r) => (cwd ? r.slice(cwd.length + 1) : r);
    let pkg = null; try { pkg = JSON.parse(py.files[FS.unir(cwd, "package.json")] || "null"); } catch { /* nada */ }
    const entrada = ["App.js", "App.tsx", "App.jsx", "App.ts", "app/_layout.tsx", "app/_layout.js", "app/index.tsx", "app/index.js"].find((x) => FS.tieneArchivo(py, FS.unir(cwd, x)));
    if (!entrada) { io.err(`expo: no encontré App.js en ${cwd || "la carpeta del proyecto"}. Crea uno con:\n  export default function App() { return <Text>Hola</Text>; }\n`); return 1; }
    const archivos = {};
    let total = 0;
    for (const r of Object.keys(py.files)) {
      if (!dentro(r) || esMarcador(py.files[r]) || /(^|\/)(node_modules|\.git|\.expo|android|ios)\//.test(rel(r)) || !/\.(jsx?|tsx?|json|md)$/.test(r)) continue;
      if (/^(package-lock\.json|app\.json|eas\.json|tsconfig\.json|babel\.config\.js|metro\.config\.js)$/.test(rel(r))) continue;
      total += py.files[r].length;
      archivos[rel(r)] = { type: "CODE", contents: py.files[r] };
    }
    if (total > 60_000) io.err(color.amarillo("Aviso: el proyecto es grande; si Snack no lo abre, deja solo los archivos de la app (sin datos ni recursos pesados).\n"));
    const deps = Object.entries({ ...(pkg?.dependencies || {}) }).filter(([n]) => !/^(expo|react|react-native|react-dom|react-native-web|@expo\/metro-runtime)$/.test(n)).map(([n, v]) => `${n}@${String(v).replace(/^[\^~]/, "")}`);
    const sdk = String(pkg?.dependencies?.expo || "").match(/(\d+)\./)?.[1];
    const parametros = (plataforma, embebido) => new URLSearchParams({ name: pkg?.name || "codigocamp-expo", files: JSON.stringify(archivos), ...(deps.length ? { dependencies: deps.join(",") } : {}), ...(sdk ? { sdkVersion: `${sdk}.0.0` } : {}), platform: plataforma, preview: "true", theme: "dark", ...(embebido ? { supportedPlatforms: "web,ios,android" } : {}) }).toString();
    const urlWeb = `https://snack.expo.dev/embedded?${parametros("web", true)}`;
    const urlCelular = `https://snack.expo.dev/?${parametros("mydevice", false)}`;
    const puerto = 8081;
    if (servidores.has(puerto)) return puertoOcupado(io, puerto, "expo");
    io.out(`${color.gris("Starting project at")} ${FS.rutaAbsoluta ? FS.rutaAbsoluta(cwd) : "/" + cwd}\n${color.gris("Starting Metro Bundler (Expo Snack)")}\n\n`);
    io.out(`${color.verde("›")} Metro waiting on ${color.cian("exp://snack.expo.dev")}\n`);
    io.out(`${color.verde("›")} ${color.negrita ? color.negrita("Celular:") : "Celular:"} abre este enlace → toca «My Device» y escanea el QR con ${color.cian("Expo Go")} (Android) o la cámara (iPhone):\n  ${color.cian(urlCelular.length > 2000 ? "https://snack.expo.dev  (el enlace es muy largo: usa el botón «Abrir en el celular» del panel PUERTOS)" : urlCelular)}\n\n`);
    io.out(`${color.verde("›")} Web is waiting on ${color.cian(`http://localhost:${puerto}`)} ${color.gris("(vista previa de Trabajo)")}\n\n`);
    io.out(`${color.gris("› Press")} w ${color.gris("│ open web")}   ${color.gris("› Press")} r ${color.gris("│ reload app (también al guardar)")}   ${color.gris("› Ctrl+C │ detener")}\n`);
    const reg = { framework: "Expo", comando: "expo start", externo: urlWeb, celular: urlCelular };
    if (!registrarServidor(puerto, reg)) return puertoOcupado(io, puerto, "expo");
    this.abrirUrl?.(`http://localhost:${puerto}/`);
    // Al guardar, se vuelve a armar el Snack con el código nuevo (como el «Fast Refresh» de Metro)
    const quitar = alCambiarProyecto((origen) => {
      if (origen === "ejecucion") return;
      clearTimeout(reg.t);
      reg.t = setTimeout(async () => {
        const nuevo = await COMANDOS.__expoUrls?.call(this, io);
        if (nuevo) { reg.externo = nuevo.web; reg.celular = nuevo.celular; avisar(); io.out(color.gris(`› Reloading apps (${new Date().toLocaleTimeString()})\n`)); }
      }, 900);
    });
    COMANDOS.__expoUrls = async () => {
      const p = io.py(); const arch = {};
      for (const r of Object.keys(p.files)) {
        if (!dentro(r) || esMarcador(p.files[r]) || /(^|\/)(node_modules|\.git|\.expo|android|ios)\//.test(rel(r)) || !/\.(jsx?|tsx?|json|md)$/.test(r)) continue;
        if (/^(package-lock\.json|app\.json|eas\.json|tsconfig\.json|babel\.config\.js|metro\.config\.js)$/.test(rel(r))) continue;
        arch[rel(r)] = { type: "CODE", contents: p.files[r] };
      }
      Object.keys(archivos).forEach((k) => delete archivos[k]); Object.assign(archivos, arch);
      return { web: `https://snack.expo.dev/embedded?${parametros("web", true)}`, celular: `https://snack.expo.dev/?${parametros("mydevice", false)}` };
    };
    await esperarDetencion(io.sesion.senal, puerto);
    quitar();
    quitarServidor(puerto, servidores.get(puerto));
    return 130;
  };

  // -------------------------------------------- frameworks que necesitan un servidor real (Docker) ----
  const IMAGEN = { node: "node:22-alpine", php: "composer:2", ruby: "ruby:3.3", java: "maven:3-eclipse-temurin-21", gradle: "gradle:8-jdk21", go: "golang:1.23", dotnet: "mcr.microsoft.com/dotnet/sdk:8.0", python: "python:3.12-slim" };
  async function enDocker(shell, io, { nombre, imagen, orden, puerto, instalar = "" }) {
    const docker = shell.ejecutores.docker;
    if (servidores.has(puerto)) return puertoOcupado(io, puerto, nombre);
    const cont = `cc-dev-${nombre.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${puerto}`;
    const sh = [instalar, orden].filter(Boolean).join(" && ");
    io.out(color.gris(`${nombre} necesita un servidor real: lo enciendo en Docker (${imagen}). La primera vez descarga la imagen y las dependencias: puede tardar unos minutos…\n`));
    await COMANDOS.docker.call(shell, ["rm", "-f", cont], { ...io, out: () => {}, err: () => {} });
    const r = await docker({ args: ["run", "-d", "--name", cont, "-p", `${puerto}:${puerto}`, "-v", "./:/app", "-w", `/app${io.sesion.cwd ? "/" + io.sesion.cwd : ""}`, "-e", `PORT=${puerto}`, "-e", "HOST=0.0.0.0", imagen, "sh", "-c", sh],
      archivos: Object.keys(io.py().files).filter((x) => !esMarcador(io.py().files[x]) && !/(^|\/)(node_modules|\.git|vendor|target|bin|obj)\//.test(x)).map((x) => ({ ruta: x, contenido: io.py().files[x] })), cwd: "" });
    if (r.error) {
      io.err(r.salida || "Docker no respondió.\n");
      if (/desactivado|no está disponible|DOCKER_TRABAJO|not found|Cannot connect/i.test(r.salida || "")) {
        io.err(color.amarillo(`\n${nombre} no puede correr dentro del navegador y este servidor de CódigoCamp no tiene Docker activo.\nOpciones: (1) pídele al administrador que active Docker (DOCKER_TRABAJO=1); (2) usa algo que corre aquí: Vite + React (npm create vite@latest), Express (node server.js), FastAPI/Flask/Django, PHP (php -S localhost:8000) o Expo (npx expo start).\n`));
      }
      return 1;
    }
    const url = `${location.protocol}//${location.hostname}:${puerto}`;
    registrarServidor(puerto, { framework: nombre, comando: orden, externo: url, detener: () => { COMANDOS.docker.call(shell, ["stop", cont], { ...io, out: () => {}, err: () => {} }); } });
    io.out(color.cian(`🌐 ${nombre} en ${url}`) + color.gris("  (panel PUERTOS · Ctrl+C detiene el contenedor)\n\n"));
    shell.abrirUrl?.(`http://localhost:${puerto}/`);
    // Muestra el log del contenedor mientras corre (como la terminal de VS Code)
    let visto = 0;
    const senal = io.sesion.senal;
    while (!senal?.aborted && servidores.has(puerto)) {
      const l = await docker({ args: ["logs", cont], archivos: null, cwd: "" });
      const texto = l.salida || "";
      if (texto.length > visto) { io.out(texto.slice(visto)); visto = texto.length; }
      if (l.error && /No such container/i.test(texto)) break;
      await new Promise((ok) => { const t = setTimeout(ok, 2000); senal?.addEventListener("abort", () => { clearTimeout(t); ok(); }, { once: true }); });
    }
    detenerServidor(puerto);
    await COMANDOS.docker.call(shell, ["stop", cont], { ...io, out: () => {}, err: () => {} });
    return 130;
  }
  const puertoDe = (a, def) => Number(opcion(a, ["-p", "--port", "-P"]) || def);
  COMANDOS.next = function (a, io) { const p = puertoDe(a, 3000); return a[0] === "dev" || !a[0] ? enDocker(this, io, { nombre: "Next.js", imagen: IMAGEN.node, instalar: "npm install", orden: `npx next dev -H 0.0.0.0 -p ${p}`, puerto: p }) : enDocker(this, io, { nombre: "Next.js", imagen: IMAGEN.node, instalar: "npm install", orden: `npx next ${a.join(" ")}`, puerto: p }); };
  COMANDOS.nuxi = COMANDOS.nuxt = function (a, io) { const p = puertoDe(a, 3000); return enDocker(this, io, { nombre: "Nuxt", imagen: IMAGEN.node, instalar: "npm install", orden: `npx nuxi dev --host 0.0.0.0 --port ${p}`, puerto: p }); };
  COMANDOS.ng = function (a, io) { const p = puertoDe(a, 4200); if (a[0] !== "serve" && a[0] !== "s") { io.err("ng: aquí se puede usar «ng serve» (en Docker). Para crear proyectos usa: npx @angular/cli new mi-app (en tu PC) y súbelo a Trabajo.\n"); return 1; } return enDocker(this, io, { nombre: "Angular", imagen: IMAGEN.node, instalar: "npm install", orden: `npx ng serve --host 0.0.0.0 --port ${p} --disable-host-check`, puerto: p }); };
  COMANDOS.astro = function (a, io) { const p = puertoDe(a, 4321); return enDocker(this, io, { nombre: "Astro", imagen: IMAGEN.node, instalar: "npm install", orden: `npx astro dev --host 0.0.0.0 --port ${p}`, puerto: p }); };
  COMANDOS.gatsby = function (a, io) { const p = puertoDe(a, 8000); return enDocker(this, io, { nombre: "Gatsby", imagen: IMAGEN.node, instalar: "npm install", orden: `npx gatsby develop -H 0.0.0.0 -p ${p}`, puerto: p }); };
  COMANDOS.remix = function (a, io) { const p = puertoDe(a, 3000); return enDocker(this, io, { nombre: "Remix", imagen: IMAGEN.node, instalar: "npm install", orden: `npx remix vite:dev --host 0.0.0.0 --port ${p}`, puerto: p }); };
  COMANDOS.rails = function (a, io) { const p = puertoDe(a, 3000); if (!["s", "server"].includes(a[0])) { io.err("rails: aquí se puede usar «rails server» (en Docker).\n"); return 1; } return enDocker(this, io, { nombre: "Rails", imagen: IMAGEN.ruby, instalar: "bundle install", orden: `bin/rails server -b 0.0.0.0 -p ${p}`, puerto: p }); };
  COMANDOS.mvn = COMANDOS.mvnw = COMANDOS["./mvnw"] = function (a, io) { const p = 8080; if (!a.some((x) => x.includes("spring-boot:run"))) { io.err("mvn: aquí se puede usar «mvn spring-boot:run» (en Docker). Para un programa normal de Java usa: java Main.java\n"); return 1; } return enDocker(this, io, { nombre: "Spring Boot", imagen: IMAGEN.java, orden: `mvn -q spring-boot:run -Dspring-boot.run.arguments=--server.port=${p}`, puerto: p }); };
  COMANDOS.gradle = COMANDOS["./gradlew"] = function (a, io) { const p = 8080; if (!a.includes("bootRun")) { io.err("gradle: aquí se puede usar «gradle bootRun» (en Docker).\n"); return 1; } return enDocker(this, io, { nombre: "Spring Boot", imagen: IMAGEN.gradle, orden: `gradle bootRun --args=--server.port=${p}`, puerto: p }); };
  COMANDOS.__artisan = function (a, io) { const p = puertoDe(a, 8000); return enDocker(this, io, { nombre: "Laravel", imagen: IMAGEN.php, instalar: "composer install --no-interaction", orden: `php artisan serve --host 0.0.0.0 --port ${p}`, puerto: p }); };
  COMANDOS.__goServidor = function (a, io, puerto) { return enDocker(this, io, { nombre: "Go", imagen: IMAGEN.go, orden: `go run ${a.join(" ") || "."}`, puerto }); };
  COMANDOS.__dotnetServidor = function (a, io, puerto) { return enDocker(this, io, { nombre: ".NET", imagen: IMAGEN.dotnet, orden: `ASPNETCORE_URLS=http://0.0.0.0:${puerto} dotnet run`, puerto }); };
  COMANDOS.__nodeReal = function (a, io, puerto) { return enDocker(this, io, { nombre: "Node.js", imagen: IMAGEN.node, instalar: "npm install", orden: `node ${a.join(" ")}`, puerto }); };
}
