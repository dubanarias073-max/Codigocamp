// Carga el Git real (isomorphic-git, incluido en /vendor/git) y crea el motor para esta cuenta.
import { cargarScript } from "./ejecucion.js";
import { claveCuenta } from "./cuenta.js";
import { MotorGit } from "./gitreal.js";

const csrf = () => (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
let promesa = null;

/** @param {object} o { usuario: { id, nombre, email }, archivos: ClienteArchivos } */
export function cargarGitReal({ usuario, archivos, credencial = null }) {
  promesa ??= (async () => {
    if (!globalThis.Buffer) await cargarScript("/vendor/git/buffer.min.js");
    if (!globalThis.git?.clone) await cargarScript("/vendor/git/isomorphic-git.min.js");
    if (!globalThis.GitHttp) await cargarScript("/vendor/git/http-web.js");
    if (!globalThis.LightningFS) await cargarScript("/vendor/git/lightning-fs.min.js");
    const cuenta = claveCuenta(usuario);
    const fs = new globalThis.LightningFS(`cc-git-${cuenta}`);   // el .git de cada cuenta, aparte
    const claveGlobal = `cc-git-global-${cuenta}`;               // git config --global de esta cuenta
    const global = () => { try { return JSON.parse(localStorage.getItem(claveGlobal) || "{}"); } catch { return {}; } };
    return new MotorGit({
      git: globalThis.git, fs, http: globalThis.GitHttp, corsProxy: `${location.origin}/api/git`,
      cabeceras: () => ({ "X-CSRFToken": csrf() }), archivos, claveGlobal, credencial,
      autor: () => ({ name: global()["user.name"] || usuario.nombre || "estudiante", email: global()["user.email"] || usuario.email || `${usuario.id}@usuarios.codigocamp` }),
    });
  })().catch((e) => { promesa = null; throw e; });
  return promesa;
}
