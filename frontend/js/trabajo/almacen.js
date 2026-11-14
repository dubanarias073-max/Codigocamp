// Guardado del proyecto: copia local (navegador) + copia en la cuenta (servidor).
//
// Reglas que evitan perder trabajo:
//  1. Cada cambio se guarda al instante en el navegador y se marca «sucio» (pendiente de subir).
//  2. La copia de la cuenta se sube poco después (o al pulsar Guardar / Ctrl+S, o al cerrar la pestaña).
//  3. Al abrir, NUNCA gana «la nube» a ciegas: si lo local tiene cambios pendientes y la cuenta no ha cambiado
//     desde la última sincronización, se conserva lo local y se sube. Solo si ambas versiones cambiaron por
//     separado se le pregunta a la persona cuál conservar.
//  4. Un proyecto vacío es un proyecto vacío: borrar todos los archivos no devuelve las plantillas.
import { normalizar, usoCaracteres } from "./fs.js";

const VERSION = 2;
const RAMA = /^[A-Za-z0-9._/-]{1,80}$/;
const HASH = /^[a-f0-9]{1,12}$/;

export const PLANTILLAS = {
  "index.html": "<!doctype html>\n<html lang=\"es\">\n<head>\n  <meta charset=\"utf-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n  <title>Mi proyecto</title>\n  <link rel=\"stylesheet\" href=\"styles.css\">\n</head>\n<body>\n  <main>\n    <h1>Hola, mundo</h1>\n    <p>Empieza a construir aquí.</p>\n  </main>\n  <script src=\"script.js\"></script>\n</body>\n</html>\n",
  "styles.css": "body {\n  margin: 0;\n  padding: 2rem;\n  font-family: system-ui, sans-serif;\n}\n",
  "script.js": "console.log(\"Proyecto listo\");\n",
};

export const gitNuevo = () => ({ initialized: false, branch: "main", staged: [], tracked: [], committed: {}, commits: [], remote: "", branches: {} });
export const proyectoNuevo = () => ({ ...normalizar({ files: { ...PLANTILLAS } }), git: gitNuevo() });

const esObjeto = (v) => v && typeof v === "object" && !Array.isArray(v);
const rutasValidas = (lista) => (Array.isArray(lista) ? lista.filter((r) => typeof r === "string") : []);

/** Limpia el estado de Git que venga de fuera. Es tolerante: lo que no entiende lo descarta. */
export function normalizarGit(crudo) {
  const g = esObjeto(crudo) ? crudo : {};
  const base = gitNuevo();
  const committed = {};
  if (esObjeto(g.committed)) for (const [r, t] of Object.entries(g.committed)) if (typeof t === "string") committed[r] = t;
  const branches = {};
  if (esObjeto(g.branches)) for (const [n, h] of Object.entries(g.branches)) if (RAMA.test(n) && (h === "" || HASH.test(h))) branches[n] = h;
  const commits = (Array.isArray(g.commits) ? g.commits : [])
    .filter((c) => esObjeto(c) && HASH.test(c.hash) && typeof c.message === "string" && typeof c.date === "string")
    .slice(0, 100)
    .map((c) => ({ hash: c.hash, message: c.message.slice(0, 200), date: c.date.slice(0, 40) }));
  return {
    ...base,
    initialized: g.initialized === true,
    branch: typeof g.branch === "string" && RAMA.test(g.branch) ? g.branch : "main",
    staged: [...new Set(rutasValidas(g.staged))],
    tracked: [...new Set(rutasValidas(g.tracked))],
    committed,
    commits,
    remote: typeof g.remote === "string" ? g.remote.slice(0, 250) : "",
    branches,
  };
}

export function normalizarProyecto(crudo) {
  return { ...normalizar(crudo), git: normalizarGit(crudo?.git) };
}

const ordenar = (v) => {
  if (Array.isArray(v)) return v.map(ordenar);
  if (esObjeto(v)) return Object.fromEntries(Object.keys(v).sort().map((k) => [k, ordenar(v[k])]));
  return v;
};
const canonico = (py) => JSON.stringify(ordenar({ files: py.files, folders: [...py.folders].sort(), git: py.git }));
export const iguales = (a, b) => canonico(a) === canonico(b);
export const resumen = (py) => ({ archivos: Object.keys(py.files).length, carpetas: py.folders.length, caracteres: usoCaracteres(py) });

const leerCsrf = () => (typeof document === "undefined" ? "" : (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "");

export class Almacen {
  /**
   * @param {object} o
   * @param {string} o.clave           clave de localStorage de este usuario
   * @param {(estado:string, mensaje?:string)=>void} [o.alEstado]   cambios del estado de guardado
   * @param {()=>void} [o.alRemoto]    otra pestaña cambió el proyecto
   * @param {(info:object)=>Promise<"local"|"nube">} [o.resolverConflicto]
   */
  constructor({ clave, alEstado = () => {}, alRemoto = () => {}, resolverConflicto = async () => "local",
    fetchFn = (...a) => fetch(...a), storage = globalThis.localStorage, csrf = leerCsrf, retardo = 600, reintento = 3000 }) {
    Object.assign(this, { clave, alEstado, alRemoto, resolverConflicto, fetchFn, storage, csrf, retardo, reintento });
    this.proyecto = proyectoNuevo();
    this.sucio = false;
    this.base = null;        // marca de la cuenta en la última sincronización
    this.version = 0;        // sube con cada cambio; sirve para saber si hubo cambios mientras se subía
    this.estado = "iniciando";
    this.temporizador = null;
    this.corriendo = null;
    this.repetir = false;
    this.fallos = 0;
    this.errorLocalAvisado = false;
    this.reconciliado = false; // ya se comparó con la cuenta al menos una vez
    this.iniciado = false;
  }

  #estado(estado, mensaje = "") {
    this.estado = estado;
    this.alEstado(estado, mensaje);
  }

  #leerLocal() {
    try {
      const crudo = JSON.parse(this.storage.getItem(this.clave));
      if (!esObjeto(crudo)) return null;
      if (crudo.v === VERSION) return { proyecto: normalizarProyecto(crudo.proyecto), sucio: crudo.sucio === true, base: typeof crudo.base === "string" ? crudo.base : null };
      // Formato anterior (sin versión): pudo quedarse con cambios que nunca llegaron a la cuenta, así que se trata como pendiente.
      if (esObjeto(crudo.files)) return { proyecto: normalizarProyecto(crudo), sucio: true, base: null };
    } catch { /* datos ilegibles: se ignoran */ }
    return null;
  }

  #persistir() {
    try {
      this.storage.setItem(this.clave, JSON.stringify({ v: VERSION, proyecto: this.proyecto, sucio: this.sucio, base: this.base, ts: Date.now() }));
      this.errorLocalAvisado = false;
      return true;
    } catch {
      if (!this.errorLocalAvisado) this.#estado("errorLocal", "No hay espacio para guardar en este navegador.");
      this.errorLocalAvisado = true;
      return false;
    }
  }

  async #pedir(metodo, cuerpo, extra = {}) {
    const r = await this.fetchFn("/api/trabajo/", {
      method: metodo,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRFToken": this.csrf() },
      body: cuerpo,
      ...extra,
    });
    const datos = await r.json().catch(() => ({}));
    if (!r.ok) {
      const error = new Error(datos.error || "No se pudo conectar con el servidor.");
      error.estado = r.status;
      throw error;
    }
    return datos;
  }

  /** Carga el proyecto (local y cuenta) y lo deja listo en this.proyecto. */
  async iniciar() {
    const previo = this.#leerLocal();
    if (previo) {
      this.proyecto = previo.proyecto;
      this.sucio = previo.sucio;
      this.base = previo.base;
    }
    this.#estado("iniciando");
    const ok = await this.#reconciliar();
    this.iniciado = true;
    if (ok && this.sucio) await this.#subir();
    return this.proyecto;
  }

  /**
   * Compara lo local con la cuenta y decide qué versión vale. No sube nada: solo deja this.proyecto, this.sucio
   * y this.base en su sitio. Devuelve false si no pudo hablar con el servidor (se reintentará antes de subir).
   */
  async #reconciliar() {
    let remoto;
    try {
      remoto = await this.#pedir("GET");
    } catch (error) {
      this.#fallo(error);
      return false;
    }
    const local = this.#leerLocal(); // se lee DESPUÉS de la respuesta para incluir lo escrito mientras esperaba
    const token = remoto.actualizado ?? null;
    const reemplazar = (proyecto, sucio) => {
      const cambio = !iguales(proyecto, this.proyecto);
      this.proyecto = proyecto;
      this.sucio = sucio;
      this.base = token;
      this.reconciliado = true;
      this.#persistir();
      if (cambio && this.iniciado) this.alRemoto();
    };
    if (!remoto.proyecto) {
      // La cuenta todavía no tiene proyecto: se sube el local (o las plantillas si es la primera vez).
      reemplazar(local ? local.proyecto : this.proyecto, true);
      return true;
    }
    const nube = normalizarProyecto(remoto.proyecto);
    if (!local || !local.sucio || iguales(local.proyecto, nube)) {
      reemplazar(nube, false);
      this.#estado("guardado");
    } else if (local.base !== null && local.base === token) {
      reemplazar(local.proyecto, true); // solo cambió este navegador desde la última sincronización
    } else {
      const eleccion = await this.resolverConflicto({ local: resumen(local.proyecto), nube: resumen(nube) });
      if (eleccion === "nube") {
        reemplazar(nube, false);
        this.#estado("guardado");
      } else {
        reemplazar(local.proyecto, true);
      }
    }
    return true;
  }

  /** Avisa que el proyecto cambió: guarda al instante en el navegador y programa la subida. */
  cambiar() {
    this.version += 1;
    this.sucio = true;
    this.#persistir();
    this.#estado("guardando");
    clearTimeout(this.temporizador);
    this.temporizador = setTimeout(() => { void this.#subir(); }, this.retardo);
  }

  /** Sube ya (botón Guardar / Ctrl+S). Resuelve cuando termina, con true si quedó guardado en la cuenta. */
  async guardarAhora() {
    clearTimeout(this.temporizador);
    this.#persistir();
    await this.#subir();
    return this.estado === "guardado";
  }

  #subir() {
    this.repetir = true;
    if (!this.corriendo) this.corriendo = this.#bucle().finally(() => { this.corriendo = null; });
    return this.corriendo;
  }

  async #bucle() {
    while (this.repetir) {
      this.repetir = false;
      if (!this.reconciliado) {
        if (!(await this.#reconciliar())) return;
        if (!this.sucio) continue;
      }
      const version = this.version;
      this.#estado("guardando");
      try {
        const r = await this.#pedir("PUT", JSON.stringify(this.proyecto));
        this.base = r.actualizado ?? this.base;
        this.fallos = 0;
        if (version === this.version) {
          this.sucio = false;
          this.#estado("guardado");
        } else {
          this.repetir = true; // hubo cambios mientras se subía
        }
        this.#persistir();
      } catch (error) {
        this.#fallo(error);
        return;
      }
    }
  }

  #fallo(error) {
    const http = error.estado;
    if (http === 401 || http === 403) {
      this.#estado("sesion", "Tu sesión venció. Recarga la página e inicia sesión de nuevo; tu trabajo sigue guardado en este navegador.");
      return;
    }
    if (http === 400 || http === 413) {
      this.#estado("error", error.message);
      return;
    }
    this.#estado("sinconexion", "No hay conexión con el servidor. Tu trabajo está guardado en este navegador y se subirá solo.");
    this.fallos += 1;
    clearTimeout(this.temporizador);
    this.temporizador = setTimeout(() => { if (this.sucio) void this.#subir(); }, Math.min(30_000, this.reintento * 2 ** (this.fallos - 1)));
  }

  /** Para pagehide / visibilitychange: intenta mandar lo pendiente aunque la página se esté cerrando. */
  volcarAlSalir() {
    if (!this.sucio) return;
    clearTimeout(this.temporizador);
    const cuerpo = JSON.stringify(this.proyecto);
    if (cuerpo.length > 60_000) return; // keepalive limita el tamaño; lo pendiente queda marcado y se sube en la próxima visita
    try { void this.#pedir("PUT", cuerpo, { keepalive: true }).catch(() => {}); } catch { /* nada más que hacer */ }
  }

  /** Otra pestaña del mismo navegador guardó: se adopta su versión para no pisarla. */
  recargarDesdeLocal() {
    const local = this.#leerLocal();
    if (!local || iguales(local.proyecto, this.proyecto)) return false;
    this.proyecto = local.proyecto;
    this.sucio = local.sucio;
    this.base = local.base;
    this.version += 1;
    this.alRemoto();
    return true;
  }
}
