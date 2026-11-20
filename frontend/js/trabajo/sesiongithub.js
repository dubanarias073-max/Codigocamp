// «Iniciar sesión con GitHub» en Trabajo, como en VS Code: cuando git push / pull / clone necesita permiso,
// se abre un cuadro con el botón de GitHub. Dos formas (las decide el servidor, ver backend/rutas/github.py):
//   · web          → ventana emergente de GitHub; al volver, la página /auth/github/callback/ entrega el token.
//   · dispositivo  → código de 8 letras que se escribe en github.com/login/device (como `gh auth login`).
// Si el servidor no tiene una OAuth App configurada, queda la opción de pegar un token personal.
//
// El token vive solo en esta pestaña (sessionStorage) salvo que la persona marque «Recordar en este navegador».
// Solo se usa para github.com (nunca se envía a GitLab u otros hosts).

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
export const esGitHub = (url) => { try { return /(^|\.)github\.com$/i.test(new URL(String(url || "")).hostname); } catch { return /github\.com/i.test(String(url || "")); } };

function aleatorio() {
  const b = new Uint8Array(18);
  crypto.getRandomValues(b);
  return Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
}

export class SesionGitHub {
  /**
   * @param {object} o
   * @param {string} o.cuenta           clave única de la cuenta de CódigoCamp (claveCuenta)
   * @param {(url:string, datos?:object)=>Promise<any>} o.api   helper de /js/auth.js
   * @param {typeof fetch} [o.fetchFn]
   */
  constructor({ cuenta, api, fetchFn = (...a) => fetch(...a) }) {
    this.clave = `cc-github-${cuenta}`;
    this.api = api;
    this.fetchFn = fetchFn;
    this.config = null;
    this.oyentes = new Set();
    this.datos = this.leer();
    this.enCurso = null;
  }

  leer() {
    for (const almacen of [sessionStorage, localStorage]) {
      try { const d = JSON.parse(almacen.getItem(this.clave) || "null"); if (d?.token) return d; } catch { /* nada */ }
    }
    return null;
  }

  guardar(datos, recordar) {
    this.datos = datos;
    try { sessionStorage.removeItem(this.clave); localStorage.removeItem(this.clave); } catch { /* nada */ }
    if (datos) { try { (recordar ? localStorage : sessionStorage).setItem(this.clave, JSON.stringify(datos)); } catch { /* sin espacio */ } }
    for (const f of this.oyentes) { try { f(this.datos); } catch { /* nada */ } }
  }

  alCambiar(f) { this.oyentes.add(f); return () => this.oyentes.delete(f); }
  get token() { return this.datos?.token || null; }
  get usuario() { return this.datos?.login || null; }
  /** Para el Git real: el token solo se entrega si la URL es de GitHub. */
  tokenPara(url) { return esGitHub(url) ? this.token : null; }
  cerrarSesion() { this.guardar(null); }
  /** GitHub rechazó el token (vencido, revocado…): se olvida para pedir uno nuevo. */
  invalidar() { if (this.datos) this.guardar(null); }

  async cargarConfig() {
    if (this.config) return this.config;
    try { this.config = await this.api("/api/github/config/"); } catch { this.config = { web: false, dispositivo: false, configurado: false }; }
    return this.config;
  }

  /** Comprueba el token con GitHub y devuelve { login, nombre, email }. */
  async verificar(token) {
    let r;
    try { r = await this.fetchFn("https://api.github.com/user", { headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json" } }); }
    catch { throw new Error("No se pudo conectar con GitHub. Revisa tu conexión."); }
    if (r.status === 401) throw new Error("GitHub rechazó ese token (inválido o vencido).");
    if (!r.ok) throw new Error(`GitHub respondió ${r.status}.`);
    const u = await r.json();
    return { login: u.login, nombre: u.name || u.login, email: u.email || `${u.id}+${u.login}@users.noreply.github.com`, avatar: u.avatar_url || "" };
  }

  async aceptar(token, { recordar = false, metodo = "token", alcance = "" } = {}) {
    const info = await this.verificar(token);
    this.guardar({ token, ...info, metodo, alcance, desde: Date.now() }, recordar);
    return this.datos;
  }

  /**
   * Devuelve un token válido de GitHub. Si no hay sesión, muestra el cuadro «Iniciar sesión con GitHub».
   * @returns {Promise<string|null>} null si la persona cancela.
   */
  async obtener({ motivo = "" } = {}) {
    if (this.token) return this.token;
    this.enCurso ??= this.dialogo(motivo).finally(() => { this.enCurso = null; });
    return this.enCurso;
  }

  async dialogo(motivo) {
    const cfg = await this.cargarConfig();
    return new Promise((resolver) => {
      const d = document.createElement("dialog");
      d.className = "ide-dialogo gh-login";
      const puedeOAuth = cfg.web || cfg.dispositivo;
      d.innerHTML = `<form method="dialog" novalidate>
        <h3><svg viewBox="0 0 16 16" width="20" height="20" aria-hidden="true" style="vertical-align:-4px;margin-right:8px"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>Iniciar sesión en GitHub</h3>
        <p>${esc(motivo || "Para publicar (git push) en GitHub, CódigoCamp necesita permiso de tu cuenta de GitHub.")}</p>
        <div class="gh-paso" data-paso="inicio">
          ${puedeOAuth ? `<button type="button" class="ide-boton primario gh-boton" data-a="oauth">Iniciar sesión con GitHub</button>` : `<p class="ide-dialogo-nota">El inicio de sesión con GitHub no está activado en este servidor (falta <code>GITHUB_CLIENT_ID</code> en <code>backend/.env</code>). Mientras tanto puedes usar un token personal.</p>`}
          <details class="gh-token"${puedeOAuth ? "" : " open"}><summary>Usar un token personal</summary>
            <p class="ide-dialogo-nota">Créalo en <a href="https://github.com/settings/tokens/new?scopes=repo,workflow&description=CodigoCamp" target="_blank" rel="noopener">github.com/settings/tokens</a> con permiso <b>repo</b> (o uno «fine-grained» con <b>Contents: Read and write</b>).</p>
            <input type="password" class="gh-in" autocomplete="off" spellcheck="false" placeholder="ghp_… o github_pat_…" aria-label="Token de GitHub">
            <button type="button" class="ide-boton" data-a="token">Usar este token</button>
          </details>
          <label class="gh-recordar"><input type="checkbox"> Recordar en este navegador (no lo marques en un computador compartido)</label>
        </div>
        <div class="gh-paso" data-paso="espera" hidden><p class="gh-estado" role="status"></p><div class="gh-codigo" hidden></div>
          <button type="button" class="ide-boton primario" data-a="abrir" hidden>Copiar código y abrir GitHub</button></div>
        <p class="gh-error" role="alert" hidden></p>
        <div class="ide-dialogo-botones"><button type="button" class="ide-boton" data-a="cancelar">Cancelar</button></div>
      </form>`;
      const $ = (s) => d.querySelector(s);
      let terminado = false, temporizador = 0, ventana = null, canal = null, alMensaje = null, alStorage = null;
      const recordar = () => $(".gh-recordar input").checked;
      const limpiar = () => {
        clearTimeout(temporizador);
        try { canal?.close(); } catch { /* nada */ }
        if (alMensaje) removeEventListener("message", alMensaje);
        if (alStorage) removeEventListener("storage", alStorage);
      };
      const fin = (token) => { if (terminado) return; terminado = true; limpiar(); try { d.close(); } catch { /* nada */ } d.remove(); resolver(token); };
      const error = (texto) => { const e = $(".gh-error"); e.textContent = texto; e.hidden = !texto; };
      const espera = (texto) => { $('[data-paso="inicio"]').hidden = true; $('[data-paso="espera"]').hidden = false; $(".gh-estado").textContent = texto; };
      const volver = () => { limpiar(); $('[data-paso="inicio"]').hidden = false; $('[data-paso="espera"]').hidden = true; $(".gh-codigo").hidden = true; $('[data-a="abrir"]').hidden = true; };
      const exito = async (token, metodo, alcance) => {
        espera("Comprobando tu cuenta de GitHub…");
        try { await this.aceptar(token, { recordar: recordar(), metodo, alcance }); fin(token); }
        catch (e) { volver(); error(e.message); }
      };

      // ---- ventana emergente (flujo web) ----
      const conVentana = () => {
        const estado = aleatorio();
        // Se abre YA, dentro del clic: si no, Safari y Chrome la bloquean.
        ventana = window.open(`/auth/github/?estado=${estado}`, "cc-github", "popup=yes,width=620,height=780");
        if (!ventana) { error("El navegador bloqueó la ventana emergente. Permite ventanas emergentes para CódigoCamp o usa un token."); return; }
        espera("Termina de iniciar sesión en la ventana de GitHub…");
        const recibir = (m) => {
          if (!m || m.tipo !== "cc-github" || m.estado !== estado) return;
          if (m.token) exito(m.token, "web", m.alcance); else { volver(); error(m.error || "No se pudo iniciar sesión."); }
        };
        try { canal = new BroadcastChannel("cc-github"); canal.onmessage = (e) => recibir(e.data); } catch { /* navegador viejo */ }
        alMensaje = (e) => { if (e.origin === location.origin) recibir(e.data); };
        alStorage = (e) => { if (e.key === "cc-github-ping" && e.newValue) { try { recibir(JSON.parse(e.newValue)); } catch { /* nada */ } } };
        addEventListener("message", alMensaje);
        addEventListener("storage", alStorage);
      };

      // ---- código de dispositivo ----
      let codigo = null;
      const conDispositivo = async () => {
        error("");
        espera("Pidiendo un código a GitHub…");
        try { codigo = await this.api("/api/github/dispositivo/", {}); }
        catch (e) { volver(); error(e.message); return; }
        $(".gh-estado").innerHTML = `1. Copia este código · 2. Ábrelo en <b>${esc(codigo.url.replace(/^https:\/\//, ""))}</b> · 3. Autoriza a CódigoCamp.`;
        const c = $(".gh-codigo"); c.textContent = codigo.codigo; c.hidden = false;
        $('[data-a="abrir"]').hidden = false;
        $('[data-a="abrir"]').focus();
        let intervalo = codigo.intervalo * 1000;
        const vence = Date.now() + codigo.vence * 1000;
        const sondear = async () => {
          if (terminado) return;
          if (Date.now() > vence) { volver(); error("El código venció. Vuelve a intentarlo."); return; }
          try {
            const r = await this.api("/api/github/dispositivo/sondear/", { id: codigo.id });
            if (r.token) { exito(r.token, "dispositivo", r.alcance); return; }
            if (r.intervalo) intervalo = r.intervalo * 1000;
          } catch (e) { volver(); error(e.message); return; }
          temporizador = setTimeout(sondear, intervalo);
        };
        temporizador = setTimeout(sondear, intervalo);
      };

      d.addEventListener("click", async (e) => {
        const b = e.target.closest("[data-a]");
        if (!b) return;
        const a = b.dataset.a;
        if (a === "cancelar") { try { ventana?.close(); } catch { /* nada */ } fin(null); }
        else if (a === "oauth") { error(""); if (cfg.web) conVentana(); else conDispositivo(); }
        else if (a === "abrir" && codigo) {
          const copia = navigator.clipboard?.writeText(codigo.codigo).then(() => true, () => false) ?? Promise.resolve(false);
          window.open(codigo.url, "_blank", "noopener");
          if (await copia) $(".gh-estado").insertAdjacentHTML("beforeend", " <b>(código copiado)</b>");
          $(".gh-estado").insertAdjacentHTML("beforeend", "<br>Esperando a que autorices en GitHub…");
        } else if (a === "token") {
          const t = $(".gh-in").value.trim();
          if (!t) { error("Escribe el token."); return; }
          if (/\s/.test(t)) { error("Ese token no es válido (no puede tener espacios)."); return; }
          error("");
          exito(t, "token", "");
        }
      });
      $(".gh-in").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); d.querySelector('[data-a="token"]').click(); } });
      d.addEventListener("cancel", (e) => { e.preventDefault(); fin(null); });
      document.body.appendChild(d);
      d.showModal();
      (d.querySelector('[data-a="oauth"]') || $(".gh-in")).focus();
    });
  }
}
