// «git push» de verdad: publica el último commit del proyecto en GitHub usando la API REST (Git Data API).
//
// Cómo funciona y qué NO hace (importante para no engañar a nadie):
//  · Necesita un token personal de GitHub que la persona escribe en la terminal. Se usa solo en esta pestaña,
//    NUNCA se guarda en el navegador ni en la cuenta de CódigoCamp, y solo se envía a api.github.com.
//  · Se publica la instantánea del último commit (git.committed) como UN commit nuevo encima de la rama remota.
//    CódigoCamp guarda los mensajes de cada commit local pero no el árbol de cada uno, así que no se puede
//    reproducir commit por commit; los mensajes locales van resumidos en el cuerpo del commit.
//  · Los archivos se añaden o actualizan; los que borraste localmente NO se borran en GitHub (para no
//    destruir por accidente cosas como un README creado en GitHub).

import { esMarcador, formatoBytes, leerMarcador } from "./archivos.js";

/** GitHub rechaza archivos de más de 100 MB en un push normal (sin Git LFS). */
export const MAX_GITHUB = 100 * 1024 * 1024;

const URL_REPO = /^https:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+?)(?:\.git)?\/?$/;
export const interpretarRemoto = (url) => { const m = URL_REPO.exec(url || ""); return m ? { owner: m[1], repo: m[2] } : null; };

const aBase64 = (bytes) => {
  let binario = "";
  for (let i = 0; i < bytes.length; i += 0x8000) binario += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binario);
};

export const base64Utf8 = (texto) => aBase64(new TextEncoder().encode(texto));

const codificarRama = (rama) => rama.split("/").map(encodeURIComponent).join("/");

function mensajeAmigable(error, contexto) {
  const e = error.estado;
  if (e === 401) return "GitHub rechazó el token (inválido o vencido). Crea uno nuevo en GitHub → Settings → Developer settings → Personal access tokens.";
  if (e === 403) return `GitHub negó el permiso${/rate limit/i.test(error.message) ? " (límite de peticiones; espera unos minutos)" : ""}. El token necesita permiso «Contents: Read and write» sobre ese repositorio.`;
  if (e === 404) return `No se encontró ${contexto}, o el token no tiene acceso. Revisa la URL del remoto y que el token incluya ese repositorio.`;
  if (e === 422) return `GitHub no aceptó los datos: ${error.message}`;
  if (error instanceof TypeError || e === undefined) return "No se pudo conectar con GitHub. Revisa tu conexión.";
  return `GitHub respondió con un error (${e}): ${error.message}`;
}

/**
 * @param {object} o
 * @param {object} o.py       proyecto { files, git }
 * @param {string} o.token
 * @param {(texto:string)=>void} [o.progreso]
 * @param {typeof fetch} [o.fetchFn]
 * @returns {Promise<{ sinCambios?: boolean, url: string, sha?: string, rama: string, archivos: number, rama_nueva: boolean }>}
 */
export async function publicar({ py, token, progreso = () => {}, fetchFn = (...a) => fetch(...a), binario = null }) {
  const g = py.git;
  const destino = interpretarRemoto(g.remote);
  if (!destino) throw new Error("El remoto no es una URL de GitHub válida (https://github.com/usuario/repositorio.git).");
  const { owner, repo } = destino;
  const rama = g.branch;
  const base = `/repos/${owner}/${repo}`;

  const api = async (metodo, ruta, cuerpo, contexto = "el repositorio") => {
    let r;
    try {
      r = await fetchFn(`https://api.github.com${ruta}`, {
        method: metodo,
        headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", ...(cuerpo ? { "Content-Type": "application/json" } : {}) },
        body: cuerpo ? JSON.stringify(cuerpo) : undefined,
      });
    } catch (error) {
      const e = new Error(mensajeAmigable(error, contexto));
      e.fatal = true;
      throw e;
    }
    const datos = await r.json().catch(() => ({}));
    if (!r.ok) {
      const e = new Error(datos.message || `HTTP ${r.status}`);
      e.estado = r.status;
      e.amigable = mensajeAmigable(e, contexto);
      throw e;
    }
    return datos;
  };
  const conMensaje = async (promesa) => { try { return await promesa; } catch (e) { if (e.amigable) { const n = new Error(e.amigable); n.estado = e.estado; throw n; } throw e; } };

  const todas = Object.keys(g.committed).sort();
  const demasiado = todas.filter((r) => (leerMarcador(g.committed[r])?.tamano ?? 0) > MAX_GITHUB);
  const rutas = todas.filter((r) => !demasiado.includes(r));
  const omitidos = demasiado.map((r) => ({ ruta: r, motivo: `pesa ${formatoBytes(leerMarcador(g.committed[r]).tamano)}; GitHub no acepta archivos de más de 100 MB` }));
  if (!rutas.length) throw new Error(todas.length ? "Todos los archivos del commit pasan de 100 MB: GitHub no los acepta." : "No hay archivos en el último commit para publicar.");
  // Los archivos (imágenes, videos…) se publican con sus bytes reales, no con el marcador de texto que guarda el proyecto.
  const base64De = async (ruta) => {
    const t = g.committed[ruta];
    if (!esMarcador(t)) return base64Utf8(t);
    if (!binario) throw new Error(`No se pudo leer el archivo ${ruta} para publicarlo.`);
    try { return aBase64(await binario(t)); } catch (e) { throw new Error(`No se pudo leer el archivo ${ruta}: ${e.message}`); }
  };

  progreso("Comprobando el repositorio…");
  const info = await conMensaje(api("GET", base, null, `el repositorio ${owner}/${repo}`));
  if (info.permissions && info.permissions.push === false) throw new Error("El token solo puede leer ese repositorio: necesita permiso de escritura (Contents: Read and write).");

  const buscarRama = async (nombre) => {
    try { return (await api("GET", `${base}/git/ref/heads/${codificarRama(nombre)}`, null, "la rama")).object.sha; }
    catch (e) { if (e.estado === 404 || e.estado === 409) return null; throw e; }
  };
  let padre = await conMensaje(buscarRama(rama));
  const ramaNueva = padre === null;
  if (ramaNueva && info.default_branch && info.default_branch !== rama) padre = await conMensaje(buscarRama(info.default_branch));

  // Repositorio vacío: la API de Git Data no funciona hasta que exista un primer commit, así que se crea con la API de contenidos.
  if (padre === null && (info.size === 0 || ramaNueva)) {
    try {
      await api("POST", `${base}/git/blobs`, { content: "", encoding: "utf-8" });
    } catch (e) {
      if (e.estado === 409) {
        progreso("El repositorio está vacío: creando el commit inicial…");
        const primero = rutas[0];
        await conMensaje(api("PUT", `${base}/contents/${primero.split("/").map(encodeURIComponent).join("/")}`,
          { message: "Commit inicial desde CódigoCamp", content: await base64De(primero), branch: rama }, "el repositorio"));
        padre = await conMensaje(buscarRama(rama));
      } else throw new Error(e.amigable || e.message);
    }
  }

  // Blobs (en tandas pequeñas para no saturar la API).
  const entradas = [];
  let hechos = 0;
  for (let i = 0; i < rutas.length; i += 5) {
    const lote = rutas.slice(i, i + 5);
    const shas = await Promise.all(lote.map(async (ruta) => conMensaje(api("POST", `${base}/git/blobs`, { content: await base64De(ruta), encoding: "base64" }))));
    lote.forEach((ruta, k) => entradas.push({ path: ruta, mode: "100644", type: "blob", sha: shas[k].sha }));
    hechos += lote.length;
    progreso(`Subiendo archivos ${hechos}/${rutas.length}…`);
  }

  let arbolBase = null;
  if (padre) arbolBase = (await conMensaje(api("GET", `${base}/git/commits/${padre}`))).tree.sha;
  const arbol = await conMensaje(api("POST", `${base}/git/trees`, { ...(arbolBase ? { base_tree: arbolBase } : {}), tree: entradas }));
  const enlace = `https://github.com/${owner}/${repo}/tree/${rama}`;
  if (arbolBase && arbol.sha === arbolBase && !ramaNueva) return { sinCambios: true, url: enlace, rama, archivos: rutas.length, rama_nueva: false, omitidos };

  const locales = g.commits.map((c) => c.message.split("\n")[0]);
  const mensaje = locales.length > 1
    ? `${locales[0]}\n\nCommits locales incluidos (CódigoCamp):\n${locales.slice(0, 30).map((m) => `- ${m}`).join("\n")}`
    : locales[0] || "Actualización desde CódigoCamp";
  progreso("Creando el commit…");
  const commit = await conMensaje(api("POST", `${base}/git/commits`, { message: mensaje, tree: arbol.sha, parents: padre ? [padre] : [] }));
  if (ramaNueva) await conMensaje(api("POST", `${base}/git/refs`, { ref: `refs/heads/${rama}`, sha: commit.sha }));
  else await conMensaje(api("PATCH", `${base}/git/refs/heads/${codificarRama(rama)}`, { sha: commit.sha, force: false }));
  return { url: `https://github.com/${owner}/${repo}/commit/${commit.sha}`, sha: commit.sha, rama, archivos: rutas.length, rama_nueva: ramaNueva, omitidos };
}

// ------------------------------------------------------------------------------ git clone ----
// Trae una instantánea del repositorio (no el historial completo): 3 consultas a la API (repositorio, últimos commits
// y árbol de archivos) y luego cada archivo desde raw.githubusercontent.com, que no cuenta para el límite de la API.
// Con token (repos privados) los archivos se piden a la API de blobs.

const URL_CLONAR = /^(?:https?:\/\/)?(?:www\.)?github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+?)(?:\.git)?\/?$/;
export function interpretarUrlClonar(url) {
  const texto = String(url || "").trim();
  if (/^git@github\.com:/.test(texto) || texto.startsWith("ssh://")) return { error: "Las URL SSH (git@github.com:…) no funcionan en el navegador. Usa la HTTPS: https://github.com/usuario/repositorio.git" };
  const m = URL_CLONAR.exec(texto);
  if (!m) return { error: "Solo se puede clonar desde GitHub: https://github.com/usuario/repositorio.git" };
  return { owner: m[1], repo: m[2] };
}

const decodificarBase64 = (b64) => Uint8Array.from(atob(b64.replace(/\s/g, "")), (c) => c.charCodeAt(0));
const codificarRuta = (ruta) => ruta.split("/").map(encodeURIComponent).join("/");

/**
 * @returns {Promise<{ owner, repo, rama, remoto, privado, vacio, truncado, commits: {hash,message,date}[], archivos: {ruta,bytes}[], omitidos: {ruta,motivo}[], ignorados: number }>}
 */
export async function clonar({ url, token = null, rama = null, fetchFn = (...a) => fetch(...a), progreso = () => {}, maxCommits = 20,
  maxArchivos = 5000, maxBytes = MAX_GITHUB, concurrencia = 6, reintentos = 4, pausa = 1500 }) {
  const destino = interpretarUrlClonar(url);
  if (destino.error) throw new Error(destino.error);
  const { owner, repo } = destino;
  const cabeceras = { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", ...(token ? { Authorization: `Bearer ${token}` } : {}) };

  const pedir = async (u, opciones) => {
    try { return await fetchFn(u, opciones); }
    catch { const e = new Error("No se pudo conectar con GitHub. Revisa tu conexión."); e.fatal = true; throw e; }
  };
  const api = async (ruta) => {
    const r = await pedir(`https://api.github.com${ruta}`, { headers: cabeceras });
    const datos = await r.json().catch(() => ({}));
    if (!r.ok) {
      const e = new Error(datos.message || `HTTP ${r.status}`);
      e.estado = r.status;
      if (r.status === 404) e.message = token
        ? `No se encontró ${owner}/${repo}, o el token no tiene acceso a ese repositorio.`
        : `No se encontró ${owner}/${repo}. Revisa la URL; si el repositorio es privado necesitas un token.`;
      else if (r.status === 401) e.message = "GitHub rechazó el token (inválido o vencido).";
      else if (r.status === 403 || r.status === 429) e.message = /rate limit/i.test(datos.message || "")
        ? (token ? "Llegaste al límite de consultas de GitHub. Espera unos minutos." : "GitHub permite 60 consultas por hora sin token y ya se usaron. Espera un rato o usa un token.")
        : "GitHub negó el acceso a ese repositorio.";
      throw e;
    }
    return datos;
  };

  progreso(`Conectando con github.com/${owner}/${repo}…`);
  const info = await api(`/repos/${owner}/${repo}`);
  const ramaFinal = rama || info.default_branch || "main";
  const remoto = `https://github.com/${owner}/${info.name || repo}.git`;
  const base = { owner, repo: info.name || repo, rama: ramaFinal, remoto, privado: Boolean(info.private), truncado: false, ignorados: 0 };

  let lista;
  try { lista = await api(`/repos/${owner}/${repo}/commits?sha=${encodeURIComponent(ramaFinal)}&per_page=${maxCommits}`); }
  catch (e) {
    if (e.estado === 409) return { ...base, vacio: true, commits: [], archivos: [], omitidos: [] }; // repositorio vacío
    if (e.estado === 404 && rama) throw new Error(`La rama «${rama}» no existe en ${owner}/${repo}.`);
    throw e;
  }
  if (!Array.isArray(lista) || !lista.length) return { ...base, vacio: true, commits: [], archivos: [], omitidos: [] };
  const usados = new Set();
  const commits = lista.map((c) => {
    let largo = 7;
    while (usados.has(c.sha.slice(0, largo)) && largo < 12) largo += 1;
    const hash = c.sha.slice(0, largo).toLowerCase();
    usados.add(hash);
    return { hash, message: String(c.commit?.message || "(sin mensaje)").slice(0, 200), date: String(c.commit?.author?.date || c.commit?.committer?.date || "").slice(0, 40) };
  });
  const cabeza = lista[0].sha;

  progreso("Leyendo la lista de archivos…");
  let arbol = await api(`/repos/${owner}/${repo}/git/trees/${lista[0].commit.tree.sha}?recursive=1`);
  if (arbol.truncated) {
    // Repositorio enorme: GitHub recortó la lista. Se recorre carpeta por carpeta para tenerla completa.
    progreso("El repositorio es grande: leyendo sus carpetas una por una…");
    const completo = [];
    const pendientes = [["", lista[0].commit.tree.sha]];
    while (pendientes.length) {
      const [prefijo, sha] = pendientes.shift();
      const t = await api(`/repos/${owner}/${repo}/git/trees/${sha}`);
      for (const e of t.tree || []) {
        const ruta = prefijo ? `${prefijo}/${e.path}` : e.path;
        completo.push({ ...e, path: ruta });
        if (e.type === "tree") pendientes.push([ruta, e.sha]);
      }
    }
    arbol = { truncated: false, tree: completo };
  }
  const omitidos = [];
  let ignorados = 0;
  const candidatos = [];
  for (const e of arbol.tree || []) {
    if (e.type === "commit") { omitidos.push({ ruta: e.path, motivo: "es un submódulo (otro repositorio)" }); continue; }
    if (e.type !== "blob") continue;
    // Se trae TODO lo que hay en el repositorio. Un enlace simbólico llega como un archivo con la ruta a la que apunta
    // (igual que hace Git en Windows).
    if (e.size > maxBytes) { omitidos.push({ ruta: e.path, motivo: `pesa ${(e.size / 1048576).toFixed(1)} MB` }); continue; }
    candidatos.push(e);
  }
  candidatos.sort((a, b) => a.path.localeCompare(b.path));
  for (const e of candidatos.splice(maxArchivos)) omitidos.push({ ruta: e.path, motivo: "no cabe: el repositorio tiene demasiados archivos" });

  const archivos = [];
  let hechos = 0;
  const esperar = (ms) => new Promise((ok) => setTimeout(ok, ms));
  const unaVez = async (e) => {
    if (token) return decodificarBase64((await api(`/repos/${owner}/${repo}/git/blobs/${e.sha}`)).content || "");
    const r = await pedir(`https://raw.githubusercontent.com/${owner}/${repo}/${cabeza}/${codificarRuta(e.path)}`);
    if (!r.ok) { const x = new Error(`HTTP ${r.status}`); x.estado = r.status; throw x; }
    return new Uint8Array(await r.arrayBuffer());
  };
  const descargar = async (e) => {
    for (let intento = 1; ; intento += 1) {
      try {
        const bytes = await unaVez(e);
        if (e.size !== undefined && bytes.length !== e.size && e.mode !== "120000") throw new Error("llegó incompleto");
        archivos.push({ ruta: e.path, bytes });
        break;
      } catch (error) {
        // Cortes, límites momentáneos (429) o archivos que llegan a medias: se reintenta antes de rendirse.
        if (intento < reintentos && error.estado !== 404) { await esperar(pausa * intento); continue; }
        if (error.fatal && intento >= reintentos) throw error;
        omitidos.push({ ruta: e.path, motivo: `no se pudo descargar (${error.message})` });
        break;
      }
    }
    hechos += 1;
    if (hechos % 10 === 0 || hechos === candidatos.length) progreso(`Recibiendo archivos: ${hechos}/${candidatos.length}`);
  };
  for (let i = 0; i < candidatos.length; i += concurrencia) await Promise.all(candidatos.slice(i, i + concurrencia).map(descargar));
  archivos.sort((a, b) => a.ruta.localeCompare(b.ruta));
  return { ...base, vacio: false, truncado: Boolean(arbol.truncated), commits, archivos, omitidos, ignorados };
}
