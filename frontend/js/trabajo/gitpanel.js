// Panel «Control de código fuente» (Ctrl+Shift+G), como el de VS Code: repositorios, rama, cambios, preparar,
// descartar, commit, sincronizar (pull + push), ramas e historial. Usa el mismo Git real que la terminal.
import { esMarcador, formatoBytes, leerMarcador } from "./archivos.js";
import { dialogo } from "./dialogos.js";
import * as FS from "./fs.js";
import { iconoArchivo } from "./iconos.js";

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const LETRA = { nuevo: ["A", "agregado"], modificado: ["M", "modificado"], eliminado: ["D", "eliminado"], sin: ["U", "sin seguimiento"], conflicto: ["!", "en conflicto"] };
const quitarColor = (t) => t.replace(/\x1b\[[0-9;]*m/g, "");

export class PanelGit {
  /**
   * @param {object} o { raiz, proyecto, motor: () => Promise<MotorGit>, alCambiar(info), correr(comando), verDiff(ruta, antes, despues), abrir(ruta), aviso, pedir }
   */
  constructor(o) {
    Object.assign(this, o);
    this.repo = null; // carpeta del repositorio elegido
    this.ocupado = false;
    this.raiz.addEventListener("click", (e) => this.#clic(e));
    this.raiz.addEventListener("change", (e) => { if (e.target.name === "repo") { this.repo = e.target.value; this.render(); } });
    this.raiz.addEventListener("keydown", (e) => { if (e.target.name === "mensaje" && (e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); this.#commit(); } });
  }

  async #git(args, { silencio = false } = {}) {
    const motor = await this.motor();
    let salida = "", errores = "";
    const py = this.proyecto();
    const codigo = await motor.ejecutar(args, {
      py, cwd: this.repo ?? "", out: (t) => { salida += t; }, err: (t) => { errores += t; },
      leerLinea: async (texto, op) => (op?.secreto ? this.pedirSecreto?.(texto) : this.pedir?.(texto, "")),
      cambio: () => this.alCambiar({ origen: "git" }),
    });
    if (codigo !== 0 && !silencio) this.aviso(quitarColor(errores || salida).trim().split("\n").slice(0, 3).join(" · ") || "Git falló", { tipo: "error", ms: 8000 });
    return { codigo, salida: quitarColor(salida), errores: quitarColor(errores) };
  }

  async render() {
    if (this.ocupado) return;
    const py = this.proyecto();
    const motor = await this.motor().catch(() => null);
    const mensaje = this.raiz.querySelector("[name=mensaje]")?.value ?? "";
    const repos = motor ? Object.keys(motor.repos(py)) : [];
    if (!motor || (!repos.length && !py.git.initialized)) {
      this.raiz.innerHTML = `<div class="git-vacio"><p>Este proyecto todavía no usa Git.</p>
        <button type="button" class="btn pri sm" data-accion="init">Inicializar repositorio</button>
        <button type="button" class="btn sm" data-accion="clonar">Clonar repositorio…</button>
        <p class="git-nota">Equivale a <code>git init</code> y <code>git clone</code> en la terminal. Es Git real: historial completo, ramas, commits y GitHub.</p></div>`;
      return;
    }
    if (!repos.length) { // proyecto con el Git anterior: se actualiza al abrir el panel
      await this.#git(["status"], { silencio: true });
      return this.render();
    }
    if (this.repo === null || !repos.includes(this.repo)) this.repo = repos.includes("") ? "" : repos[0];
    const dir = this.repo;
    try { await motor.asegurarGit(py, dir); await motor.haciaGit(py, dir); } catch (e) { this.raiz.innerHTML = `<p class="git-nota">No se pudo abrir el repositorio: ${esc(e.message)}</p>`; return; }
    const d = motor.dirFs(dir);
    const g = motor.git, fs = motor.fs;
    const [estado, rama, ramas, remotos, log] = await Promise.all([
      motor.estado(py, dir),
      g.currentBranch({ fs, dir: d }).catch(() => null),
      g.listBranches({ fs, dir: d }).catch(() => []),
      g.listRemotes({ fs, dir: d }).catch(() => []),
      g.log({ fs, dir: d, depth: 15 }).catch(() => []),
    ]);
    const seguimiento = rama ? await motor.seguimiento(d, rama).catch(() => "") : "";
    const delante = Number(/ahead of .* by (\d+)/.exec(seguimiento)?.[1] || 0), detras = Number(/behind .* by (\d+)/.exec(seguimiento)?.[1] || 0);
    const { preparados, sinPreparar, sinSeguimiento, conflictos } = estado;
    const ruta = (r) => (dir ? `${dir}/${r}` : r);
    const fila = (r, tipo, zona) => {
      const [letra, nombre] = LETRA[tipo];
      const botones = zona === "preparados"
        ? `<button type="button" class="icono-btn" data-accion="unstage" data-ruta="${esc(r)}" title="Sacar de la preparación (git restore --staged)" aria-label="Sacar ${esc(r)} de la preparación">−</button>`
        : `${tipo !== "sin" ? `<button type="button" class="icono-btn" data-accion="descartar" data-ruta="${esc(r)}" title="Descartar cambios (git restore)" aria-label="Descartar cambios de ${esc(r)}">↺</button>` : ""}<button type="button" class="icono-btn" data-accion="stage" data-ruta="${esc(r)}" title="Preparar (git add)" aria-label="Preparar ${esc(r)}">+</button>`;
      return `<div class="git-fila" data-ruta="${esc(r)}" data-tipo="${tipo}" data-zona="${zona}" title="${esc(r)} · ${nombre}">${iconoArchivo(r)}<span class="git-nombre">${esc(FS.nombreBase(r))}</span><span class="git-dir">${esc(FS.carpetaDe(r))}</span><span class="git-botones">${botones}</span><span class="git-letra git-${letra === "!" ? "C" : letra}">${letra}</span></div>`;
    };
    const cambios = [...sinPreparar.map((c) => [c.ruta, c.tipo]), ...sinSeguimiento.map((r) => [r, "sin"])].filter(([r]) => !conflictos.includes(r));
    const origen = remotos.find((x) => x.remote === "origin");
    this.raiz.innerHTML = `
      ${repos.length > 1 ? `<label class="git-repo">Repositorio <select name="repo">${repos.map((r) => `<option value="${esc(r)}" ${r === dir ? "selected" : ""}>${esc(r || "(raíz del proyecto)")}</option>`).join("")}</select></label>` : ""}
      <div class="git-cab"><span>⎇ <b>${esc(rama || "HEAD desacoplado")}</b>${origen ? ` · <span title="${esc(origen.url)}">origin</span>` : ""}${delante ? ` · ↑${delante}` : ""}${detras ? ` · ↓${detras}` : ""}</span>
        <span><button type="button" class="icono-btn" data-accion="ramas" title="Cambiar de rama / crear rama" aria-label="Ramas">⎇</button><button type="button" class="icono-btn" data-accion="actualizar" title="Actualizar" aria-label="Actualizar">⟳</button></span></div>
      <textarea name="mensaje" rows="2" placeholder="Mensaje (Ctrl+Enter para confirmar en «${esc(rama || "HEAD")}»)" aria-label="Mensaje del commit">${esc(mensaje)}</textarea>
      <button type="button" class="btn pri sm git-commit" data-accion="commit" ${preparados.length || cambios.length || conflictos.length ? "" : "disabled"}>✓ Confirmar${preparados.length ? "" : " todo"} (commit)</button>
      ${origen ? `<button type="button" class="btn sm git-sync" data-accion="sincronizar" title="git pull y luego git push">⟳ Sincronizar cambios${delante || detras ? ` ${detras ? `↓${detras} ` : ""}${delante ? `↑${delante}` : ""}` : ""}</button>` : `<button type="button" class="btn sm git-sync" data-accion="publicar" ${log.length ? "" : "disabled"} title="git remote add origin … y git push -u">⇡ Publicar en GitHub</button>`}
      ${conflictos.length ? `<div class="git-grupo"><div class="git-titulo">Conflictos de merge <span>${conflictos.length}</span></div>${conflictos.map((r) => fila(r, "conflicto", "cambios")).join("")}<p class="git-nota">Abre cada archivo, elige qué queda entre <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code> y <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code>, prepáralo (+) y confirma.</p></div>` : ""}
      ${preparados.length ? `<div class="git-grupo"><div class="git-titulo">Cambios preparados <span>${preparados.length}</span><button type="button" class="icono-btn" data-accion="unstage-todo" title="Sacar todo" aria-label="Sacar todo de la preparación">−</button></div>${preparados.map((c) => fila(c.ruta, c.tipo, "preparados")).join("")}</div>` : ""}
      <div class="git-grupo"><div class="git-titulo">Cambios <span>${cambios.length}</span>${cambios.length ? '<button type="button" class="icono-btn" data-accion="descartar-todo" title="Descartar todos los cambios" aria-label="Descartar todo">↺</button><button type="button" class="icono-btn" data-accion="stage-todo" title="Preparar todo (git add .)" aria-label="Preparar todo">+</button>' : ""}</div>
        ${cambios.length ? cambios.map(([r, t]) => fila(r, t, "cambios")).join("") : '<p class="git-nota">No hay cambios desde el último commit.</p>'}</div>
      <div class="git-acciones">
        <button type="button" class="btn sm" data-accion="pull" ${origen ? "" : "disabled"}>↓ Pull</button>
        <button type="button" class="btn sm" data-accion="push" ${origen && log.length ? "" : "disabled"}>↑ Push</button>
        <button type="button" class="btn sm" data-accion="stash" ${preparados.length || sinPreparar.length ? "" : "disabled"}>Stash</button>
        <button type="button" class="btn sm" data-accion="log">Historial</button>
      </div>
      ${log.length ? `<div class="git-grupo"><div class="git-titulo">Historial (${esc(rama || "HEAD")})</div>${log.map((c) => `<div class="git-commit-item" data-oid="${c.oid}" title="${esc(c.commit.author.name)} · ${new Date(c.commit.author.timestamp * 1000).toLocaleString()}"><code>${c.oid.slice(0, 7)}</code> ${esc(c.commit.message.split("\n")[0])}</div>`).join("")}</div>` : ""}
      <p class="git-nota">${ramas.length} rama${ramas.length === 1 ? "" : "s"} · Git real: historial completo en este navegador y respaldado en tu cuenta.</p>`;
    this.rutaCompleta = ruta;
  }

  async #accion(fn) {
    if (this.ocupado) return;
    this.ocupado = true;
    this.raiz.classList.add("git-ocupado");
    try { await fn(); } finally { this.ocupado = false; this.raiz.classList.remove("git-ocupado"); await this.render(); }
  }

  async #commit() {
    const ta = this.raiz.querySelector("[name=mensaje]");
    const mensaje = ta?.value.trim();
    if (!mensaje) { this.aviso("Escribe un mensaje que describa el cambio.", { tipo: "error" }); ta?.focus(); return; }
    await this.#accion(async () => {
      const motor = await this.motor();
      const e = await motor.estado(this.proyecto(), this.repo);
      if (!e.preparados.length) await this.#git(["add", "-A"]);
      const r = await this.#git(["commit", "-m", mensaje]);
      if (r.codigo === 0) { ta.value = ""; this.aviso(r.salida.split("\n")[0], { ms: 4000 }); }
    });
  }

  async #clic(e) {
    const b = e.target.closest("[data-accion]");
    const accion = b?.dataset.accion;
    const r = b?.dataset.ruta;
    const enCwd = (x) => x; // las rutas del panel ya son relativas al repositorio (cwd = carpeta del repositorio)
    if (accion === "init") return this.#accion(() => this.#git(["init"]));
    if (accion === "clonar") {
      const url = await this.pedir?.("URL del repositorio (GitHub, GitLab…)", "https://github.com/usuario/repositorio.git");
      if (url) this.correr(`git clone ${url}`);
      return;
    }
    if (accion === "stage") return this.#accion(() => this.#git(["add", enCwd(r)]));
    if (accion === "unstage") return this.#accion(() => this.#git(["restore", "--staged", enCwd(r)]));
    if (accion === "stage-todo") return this.#accion(() => this.#git(["add", "-A"]));
    if (accion === "unstage-todo") return this.#accion(() => this.#git(["restore", "--staged", "."]));
    if (accion === "descartar" || accion === "descartar-todo") {
      const todo = accion === "descartar-todo";
      const tipo = b.closest(".git-fila")?.dataset.tipo;
      const ok = await dialogo({ titulo: todo ? "¿Descartar todos los cambios?" : `¿Descartar los cambios de «${FS.nombreBase(r)}»?`, mensaje: "Vuelve a como estaba en el último commit. No se puede deshacer.", botones: [{ texto: "Descartar", valor: true, peligro: true }, { texto: "Cancelar", valor: false, cancelar: true }] });
      if (!ok) return;
      return this.#accion(async () => {
        if (todo) { await this.#git(["restore", "."], { silencio: true }); return; }
        if (tipo === "sin") { const py = this.proyecto(); delete py.files[this.rutaCompleta(r)]; this.alCambiar({ origen: "git" }); return; }
        await this.#git(["restore", enCwd(r)]);
      });
    }
    if (accion === "commit") return this.#commit();
    if (accion === "sincronizar") return this.correr(`${this.repo ? `cd /workspace/${this.repo} && ` : ""}git pull && git push`);
    if (accion === "pull") return this.correr(`${this.repo ? `cd /workspace/${this.repo} && ` : ""}git pull`);
    if (accion === "push") return this.correr(`${this.repo ? `cd /workspace/${this.repo} && ` : ""}git push`);
    if (accion === "publicar") {
      const url = await this.pedir?.("URL del repositorio de GitHub (créalo vacío en github.com/new)", "https://github.com/usuario/repositorio.git");
      if (url) this.correr(`${this.repo ? `cd /workspace/${this.repo} && ` : ""}git remote add origin ${url} && git push -u origin HEAD`);
      return;
    }
    if (accion === "stash") return this.#accion(() => this.#git(["stash"]));
    if (accion === "log") return this.correr(`${this.repo ? `cd /workspace/${this.repo} && ` : ""}git log --oneline --graph --all`);
    if (accion === "actualizar") return this.render();
    if (accion === "ramas") {
      const motor = await this.motor();
      const d = motor.dirFs(this.repo);
      const ramas = await motor.git.listBranches({ fs: motor.fs, dir: d });
      const remotas = (await motor.git.listBranches({ fs: motor.fs, dir: d, remote: "origin" }).catch(() => [])).filter((x) => x !== "HEAD" && !ramas.includes(x));
      const elegida = await this.elegir?.("Cambiar a la rama…", [...ramas.map((x) => ({ valor: x, texto: x })), ...remotas.map((x) => ({ valor: x, texto: `origin/${x}` })), { valor: "+nueva", texto: "+ Crear rama nueva…" }]);
      if (!elegida) return;
      if (elegida === "+nueva") {
        const nombre = await this.pedir?.("Nombre de la rama nueva", "mi-cambio");
        if (nombre) return this.#accion(() => this.#git(["switch", "-c", nombre.trim()]));
        return;
      }
      return this.#accion(() => this.#git(["switch", elegida]));
    }
    const commit = e.target.closest(".git-commit-item");
    if (commit) return this.correr(`${this.repo ? `cd /workspace/${this.repo} && ` : ""}git show ${commit.dataset.oid.slice(0, 7)}`);
    const f = !b && e.target.closest(".git-fila");
    if (!f) return;
    const motor = await this.motor();
    const py = this.proyecto();
    const completa = this.rutaCompleta(f.dataset.ruta);
    const d = motor.dirFs(this.repo);
    let head = null;
    try { head = await motor.git.resolveRef({ fs: motor.fs, dir: d, ref: "HEAD" }); } catch { /* sin commits */ }
    const antes = head ? await motor.textoEn(d, head, f.dataset.ruta) : null;
    const despues = py.files[completa] ?? null;
    if (antes?.startsWith("\u0000bin") || esMarcador(despues)) {
      const t = (x) => (esMarcador(x) ? `archivo de ${formatoBytes(leerMarcador(x).tamano)}` : x === null ? "no existe" : "archivo binario");
      this.aviso(`${f.dataset.ruta}: ${t(antes)} → ${t(despues)}`, { ms: 6000 });
      if (FS.tieneArchivo(py, completa)) this.abrir(completa);
      return;
    }
    this.verDiff(completa, antes ?? "", despues ?? "");
  }
}
