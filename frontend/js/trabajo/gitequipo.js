// Control de código fuente cuando la carpeta abierta es la de tu computador o celular (Conector): usa el Git que tienes
// instalado allá, con tu configuración y tus credenciales, igual que un editor de escritorio. Pull, push y clone corren
// en la terminal «🖥 equipo» para que veas lo que pasa (y si Git pide usuario o contraseña, lo escribes ahí).
import { leerEstadoGit } from "./equipo.js";
import { dialogo, menuContextual } from "./dialogos.js";
import * as FS from "./fs.js";
import { iconoArchivo } from "./iconos.js";

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const LETRA = { A: "agregado", M: "modificado", D: "eliminado", R: "renombrado", C: "copiado", U: "sin seguimiento", "!": "en conflicto" };
const comillas = (r) => (/^[\w./-]+$/.test(r) ? r : `"${r.replace(/"/g, '\\"')}"`);

/** Estado → { preparados, cambios, conflictos } con letras como VS Code y el mapa para colorear el árbol. */
export function clasificarCambios(cambios, prefijo = "") {
  const preparados = [], sinPreparar = [], conflictos = [];
  const quitar = (r) => (prefijo && r.startsWith(prefijo) ? r.slice(prefijo.length) : prefijo ? null : r);
  const mapa = new Map();
  for (const c of cambios) {
    const ruta = quitar(c.ruta);
    if (ruta === null) continue; // fuera de la carpeta abierta (el repositorio empieza más arriba)
    const par = c.x + c.y;
    if (["DD", "AU", "UD", "UA", "DU", "AA", "UU"].includes(par)) { conflictos.push({ ruta, letra: "!" }); mapa.set(ruta, "C"); continue; }
    if (par === "??") { sinPreparar.push({ ruta, letra: "U" }); mapa.set(ruta, "U"); continue; }
    if (c.x !== " " && c.x !== "?") preparados.push({ ruta, letra: c.x === "?" ? "U" : c.x });
    if (c.y !== " ") sinPreparar.push({ ruta, letra: c.y });
    if (c.x !== "D" && c.y !== "D") mapa.set(ruta, c.x === "A" ? "A" : "M");
  }
  return { preparados, sinPreparar, conflictos, mapa };
}

export class PanelGitEquipo {
  /**
   * @param {object} o
   * @param {HTMLElement} o.raiz
   * @param {()=>object|null} o.equipo        equipo con la carpeta abierta ({ id, equipo, carpeta }) o null
   * @param {(equipo, args:string[])=>Promise<{codigo,salida,error}>} o.git
   * @param {(linea:string)=>void} o.correr  ejecuta en la terminal del equipo (pull, push, clone…)
   * @param {()=>object} o.proyecto
   * @param {(ruta, antes, despues)=>void} o.verDiff
   * @param {(ruta)=>void} o.abrir
   * @param {(texto, op)=>void} o.aviso
   * @param {(diff)=>Promise<string>} [o.pedirIA]
   * @param {(mapa:Map)=>void} [o.alEstado]   para colorear archivos y pestañas
   * @param {()=>void} [o.alCambiar]          Git cambió archivos (checkout, restore…): sincronizar ya
   */
  constructor(o) {
    Object.assign(this, o);
    this.ocupado = false;
    this.ultimo = null;
    this.raiz.addEventListener("click", (e) => { if (this.activo) this.#clic(e); });
    this.raiz.addEventListener("keydown", (e) => { if (this.activo && e.target.name === "mensaje" && (e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); this.#commit(); } });
  }

  get activo() { return Boolean(this.equipo()); }

  async #git(args, { silencio = false } = {}) {
    const eq = this.equipo();
    if (!eq) throw new Error("No hay una carpeta de tu equipo abierta.");
    const r = await this.git(eq, args);
    if (r.codigo !== 0 && !silencio) this.aviso((r.error || r.salida || "Git no pudo hacerlo").trim().split("\n").slice(-3).join(" "), { tipo: "error", ms: 9000 });
    return r;
  }

  /** Lee el estado del repositorio (también para colorear el árbol aunque el panel esté cerrado). */
  async estado() {
    const eq = this.equipo();
    if (!eq) return null;
    let r;
    try { r = await this.git(eq, ["status", "--porcelain=v1", "-b", "-z", "-uall"]); }
    catch (e) { return { error: e.message, sinGit: e.sin_git }; }
    if (r.codigo !== 0) return { noRepo: /not a git repository|no es un repositorio/i.test(r.error), error: r.error };
    const pre = await this.git(eq, ["rev-parse", "--show-prefix"]).catch(() => ({ salida: "" }));
    const prefijo = (pre.salida || "").trim();
    const e = leerEstadoGit(r.salida);
    const c = clasificarCambios(e.cambios, prefijo);
    this.ultimo = { ...e, ...c, prefijo };
    this.alEstado?.(c.mapa);
    return this.ultimo;
  }

  async render() {
    if (this.ocupado || !this.activo) return;
    const eq = this.equipo();
    const mensaje = this.raiz.querySelector("[name=mensaje]")?.value ?? "";
    const cab = `<div class="git-equipo-cab">🖥 Git de <b>${esc(eq.equipo)}</b> · <span title="${esc(eq.carpeta)}">${esc(FS.nombreBase(eq.carpeta.replace(/\\/g, "/")))}</span></div>`;
    if (!this.raiz.querySelector(".git-equipo-cab")) this.raiz.innerHTML = `${cab}<p class="git-nota">Leyendo Git de tu equipo…</p>`;
    const e = await this.estado();
    if (!this.activo) return;
    if (!e || e.error && !e.noRepo) {
      this.raiz.innerHTML = `${cab}<div class="git-vacio"><p>${e?.sinGit ? "Git no está instalado en tu equipo." : esc(e?.error || "No se pudo leer Git.")}</p>
        ${e?.sinGit ? '<a class="btn pri sm" href="https://git-scm.com/downloads" target="_blank" rel="noopener">Descargar Git</a><p class="git-nota">Instálalo, cierra y abre el Conector otra vez.</p>' : '<button type="button" class="btn sm" data-accion="actualizar">Reintentar</button>'}</div>`;
      return;
    }
    if (e.noRepo) {
      this.alEstado?.(new Map());
      this.raiz.innerHTML = `${cab}<div class="git-vacio"><p>Esta carpeta todavía no usa Git.</p>
        <button type="button" class="btn pri sm" data-accion="init">Inicializar repositorio</button>
        <button type="button" class="btn sm" data-accion="clonar">Clonar repositorio…</button>
        <p class="git-nota">Es el Git de tu equipo: usa tu nombre, tu correo y tus credenciales de GitHub de allá.</p></div>`;
      return;
    }
    const log = await this.#git(["log", "-15", "--pretty=format:%h%x09%an%x09%ar%x09%s"], { silencio: true });
    const commits = log.codigo === 0 ? log.salida.split("\n").filter(Boolean).map((l) => l.split("\t")) : [];
    const fila = (c, zona) => {
      const nombre = LETRA[c.letra] || "cambiado";
      const botones = zona === "preparados"
        ? `<button type="button" class="icono-btn" data-accion="unstage" data-ruta="${esc(c.ruta)}" title="Sacar de la preparación (git restore --staged)" aria-label="Sacar ${esc(c.ruta)}">−</button>`
        : `${c.letra !== "U" ? `<button type="button" class="icono-btn" data-accion="descartar" data-ruta="${esc(c.ruta)}" title="Descartar cambios (git restore)" aria-label="Descartar ${esc(c.ruta)}">↺</button>` : ""}<button type="button" class="icono-btn" data-accion="stage" data-ruta="${esc(c.ruta)}" title="Preparar (git add)" aria-label="Preparar ${esc(c.ruta)}">+</button>`;
      const l = c.letra === "!" ? "C" : c.letra;
      return `<div class="git-fila" data-ruta="${esc(c.ruta)}" data-letra="${esc(c.letra)}" title="${esc(c.ruta)} · ${nombre}">${iconoArchivo(c.ruta)}<span class="git-nombre">${esc(FS.nombreBase(c.ruta))}</span><span class="git-dir">${esc(FS.carpetaDe(c.ruta))}</span><span class="git-botones">${botones}</span><span class="git-letra git-${esc(l)}">${esc(c.letra)}</span></div>`;
    };
    const { preparados, sinPreparar, conflictos } = e;
    const hay = preparados.length || sinPreparar.length || conflictos.length;
    this.raiz.innerHTML = `${cab}
      <div class="git-cab"><span>⎇ <b>${esc(e.rama || "HEAD")}</b>${e.seguimiento ? ` · <span title="${esc(e.seguimiento)}">${esc(e.seguimiento.split("/")[0])}</span>` : ""}${e.adelante ? ` · ↑${e.adelante}` : ""}${e.atras ? ` · ↓${e.atras}` : ""}</span>
        <span><button type="button" class="icono-btn" data-accion="ramas" title="Cambiar de rama / crear rama" aria-label="Ramas">⎇</button><button type="button" class="icono-btn" data-accion="actualizar" title="Actualizar" aria-label="Actualizar">⟳</button></span></div>
      <textarea name="mensaje" rows="2" placeholder="Mensaje (Ctrl+Enter para confirmar en «${esc(e.rama || "HEAD")}»)" aria-label="Mensaje del commit">${esc(mensaje)}</textarea>
      ${this.pedirIA && hay ? '<button type="button" class="btn sm git-ia" data-accion="mensaje-ia" title="La IA escribe el mensaje a partir de tus cambios">✨ Mensaje con IA</button>' : ""}
      <button type="button" class="btn pri sm git-commit" data-accion="commit" ${hay ? "" : "disabled"}>✓ Confirmar${preparados.length ? "" : " todo"} (commit)</button>
      ${e.seguimiento ? `<button type="button" class="btn sm git-sync" data-accion="sincronizar" title="git pull y luego git push (en la terminal del equipo)">⟳ Sincronizar cambios${e.atras ? ` ↓${e.atras}` : ""}${e.adelante ? ` ↑${e.adelante}` : ""}</button>`
        : `<button type="button" class="btn sm git-sync" data-accion="publicar" ${commits.length ? "" : "disabled"} title="git remote add origin … y git push -u">⇡ Publicar en GitHub</button>`}
      ${conflictos.length ? `<div class="git-grupo"><div class="git-titulo">Conflictos de merge <span>${conflictos.length}</span></div>${conflictos.map((c) => fila(c, "cambios")).join("")}<p class="git-nota">Abre cada archivo, deja lo correcto entre <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code> y <code>&gt;&gt;&gt;&gt;&gt;&gt;&gt;</code>, prepáralo (+) y confirma.</p></div>` : ""}
      ${preparados.length ? `<div class="git-grupo"><div class="git-titulo">Cambios preparados <span>${preparados.length}</span><button type="button" class="icono-btn" data-accion="unstage-todo" title="Sacar todo" aria-label="Sacar todo">−</button></div>${preparados.map((c) => fila(c, "preparados")).join("")}</div>` : ""}
      <div class="git-grupo"><div class="git-titulo">Cambios <span>${sinPreparar.length}</span>${sinPreparar.length ? '<button type="button" class="icono-btn" data-accion="descartar-todo" title="Descartar todos los cambios" aria-label="Descartar todo">↺</button><button type="button" class="icono-btn" data-accion="stage-todo" title="Preparar todo (git add -A)" aria-label="Preparar todo">+</button>' : ""}</div>
        ${sinPreparar.length ? sinPreparar.map((c) => fila(c, "cambios")).join("") : '<p class="git-nota">No hay cambios desde el último commit.</p>'}</div>
      <div class="git-acciones">
        <button type="button" class="btn sm" data-accion="pull" ${e.seguimiento ? "" : "disabled"}>↓ Pull</button>
        <button type="button" class="btn sm" data-accion="push" ${commits.length ? "" : "disabled"}>↑ Push</button>
        <button type="button" class="btn sm" data-accion="stash" ${hay ? "" : "disabled"}>Stash</button>
        <button type="button" class="btn sm" data-accion="terminal" title="Abre la terminal de tu equipo en esta carpeta">🖥 Terminal</button>
      </div>
      ${commits.length ? `<div class="git-grupo"><div class="git-titulo">Historial (${esc(e.rama || "HEAD")})</div>${commits.map(([h, autor, cuando, asunto]) => `<div class="git-commit-item" title="${esc(autor)} · ${esc(cuando)}"><code>${esc(h)}</code> ${esc(asunto)}</div>`).join("")}</div>` : ""}
      <p class="git-nota">Git real de tu equipo: lo que hagas aquí es lo mismo que escribir <code>git</code> en su terminal.</p>`;
  }

  async #accion(fn) {
    if (this.ocupado) return;
    this.ocupado = true;
    this.raiz.classList.add("git-ocupado");
    try { await fn(); } catch (e) { this.aviso(e.message, { tipo: "error" }); }
    finally { this.ocupado = false; this.raiz.classList.remove("git-ocupado"); this.alCambiar?.(); await this.render(); }
  }

  async #commit() {
    const ta = this.raiz.querySelector("[name=mensaje]");
    const mensaje = ta?.value.trim();
    if (!mensaje) { this.aviso("Escribe un mensaje para el commit.", { tipo: "info" }); ta?.focus(); return; }
    await this.#accion(async () => {
      if (!this.ultimo?.preparados.length) await this.#git(["add", "-A"]);
      const r = await this.#git(["commit", "-m", mensaje]);
      if (r.codigo === 0) {
        ta.value = "";
        this.aviso(`Commit en ${this.ultimo?.rama || "tu rama"}: ${mensaje.split("\n")[0]}`, { tipo: "info" });
      } else if (/user\.(email|name)|tell me who you are|identity/i.test(r.error)) {
        this.aviso("Git de tu equipo no sabe tu nombre. En su terminal: git config --global user.name \"Tu nombre\" y git config --global user.email tu@correo.com", { tipo: "error", ms: 15000 });
      }
    });
  }

  async #clic(e) {
    const b = e.target.closest("[data-accion]");
    const fila = e.target.closest(".git-fila");
    if (!b && fila) return this.#verDiff(fila.dataset.ruta, fila.dataset.letra);
    if (!b) return;
    const a = b.dataset.accion;
    const r = b.dataset.ruta;
    const pref = this.ultimo?.prefijo || "";
    if (a === "actualizar") return this.render();
    if (a === "terminal") return this.correr("");
    if (a === "commit") return this.#commit();
    if (a === "init") return this.#accion(() => this.#git(["init"]));
    if (a === "clonar") {
      const url = await this.#pedir("Dirección del repositorio a clonar", "https://github.com/usuario/proyecto.git");
      if (url) this.correr(`git clone ${comillas(url)}`);
      return;
    }
    if (a === "stage") return this.#accion(() => this.#git(["add", "--", r]));
    if (a === "unstage") return this.#accion(() => this.#git(["restore", "--staged", "--", r]));
    if (a === "stage-todo") return this.#accion(() => this.#git(["add", "-A"]));
    if (a === "unstage-todo") return this.#accion(() => this.#git(["restore", "--staged", "."]));
    if (a === "descartar" || a === "descartar-todo") {
      const ok = await dialogo({ titulo: a === "descartar" ? `¿Descartar los cambios de «${r}»?` : "¿Descartar TODOS los cambios?", mensaje: "Vuelven a como estaban en el último commit. No se puede deshacer.", botones: [{ texto: "Descartar", valor: true, peligro: true }, { texto: "Cancelar", valor: false, cancelar: true }] });
      if (ok) return this.#accion(() => this.#git(a === "descartar" ? ["restore", "--", r] : ["restore", "."]));
      return;
    }
    if (a === "stash") return this.#accion(() => this.#git(["stash"]));
    if (a === "pull") return this.correr("git pull");
    if (a === "push") return this.correr(this.ultimo?.seguimiento ? "git push" : `git push -u origin ${comillas(this.ultimo?.rama || "main")}`);
    if (a === "sincronizar") return this.correr("git pull && git push");
    if (a === "publicar") {
      const url = await this.#pedir("Dirección del repositorio vacío de GitHub", "https://github.com/usuario/proyecto.git");
      if (url) this.correr(`git remote add origin ${comillas(url)} && git push -u origin ${comillas(this.ultimo?.rama || "main")}`);
      return;
    }
    if (a === "mensaje-ia") return this.#mensajeIA(b);
    if (a === "ramas") return this.#ramas(b);
  }

  async #pedir(titulo, ejemplo) {
    const v = prompt(`${titulo}\nEjemplo: ${ejemplo}`);
    return v ? v.trim() : null;
  }

  async #ramas(boton) {
    const r = await this.#git(["branch", "--format=%(refname:short)"], { silencio: true });
    const ramas = r.codigo === 0 ? r.salida.split("\n").map((x) => x.trim()).filter(Boolean) : [];
    const rect = boton.getBoundingClientRect();
    menuContextual(rect.left, rect.bottom + 4, [
      { texto: "＋ Crear rama nueva…", fn: async () => { const n = await this.#pedir("Nombre de la rama nueva", "mi-funcion"); if (n) this.#accion(() => this.#git(["switch", "-c", n])); } },
      "-",
      ...ramas.map((x) => ({ texto: `${x === this.ultimo?.rama ? "✓ " : "  "}${x}`, fn: () => { if (x !== this.ultimo?.rama) this.#accion(() => this.#git(["switch", x])); } })),
    ]);
  }

  async #verDiff(ruta, letra) {
    const pref = this.ultimo?.prefijo || "";
    const antes = letra === "U" || letra === "A" ? "" : await this.#git(["show", `HEAD:${pref}${ruta}`], { silencio: true }).then((r) => (r.codigo === 0 ? r.salida : "")).catch(() => "");
    const py = this.proyecto();
    const despues = FS.tieneArchivo(py, ruta) && typeof py.files[ruta] === "string" && !py.files[ruta].startsWith("ccbin:") && !py.files[ruta].startsWith("ccimg:") ? py.files[ruta] : "";
    this.verDiff(ruta, antes, despues);
  }

  async #mensajeIA(boton) {
    if (!this.pedirIA) return;
    const ta = this.raiz.querySelector("[name=mensaje]");
    boton.disabled = true; boton.textContent = "✨ Escribiendo…";
    try {
      let d = await this.#git(this.ultimo?.preparados.length ? ["diff", "--cached", "--stat", "-p"] : ["diff", "--stat", "-p"], { silencio: true });
      let texto = d.salida || "";
      const nuevos = (this.ultimo?.sinPreparar || []).filter((c) => c.letra === "U").map((c) => `+ archivo nuevo: ${c.ruta}`).join("\n");
      texto = `${texto}\n${nuevos}`.slice(0, 20000);
      if (!texto.trim()) { this.aviso("No hay cambios para describir.", { tipo: "info" }); return; }
      const m = await this.pedirIA(texto);
      if (m && ta) ta.value = m.trim();
    } catch (e) { this.aviso(e.message, { tipo: "error" }); }
    finally { boton.disabled = false; boton.textContent = "✨ Mensaje con IA"; }
  }
}
