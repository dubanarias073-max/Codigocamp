// Lógica de login.html y registro.html (el formulario indica su tipo en data-tipo)
import { api, getUser, setGuest } from "./auth.js";

const $ = (id) => document.getElementById(id);
const form = $("formAcceso");
const err = $("autherr");
const esRegistro = form.dataset.tipo === "registro";

// Reglas de contraseña (solo se exigen al registrarse). Deben coincidir con las del servidor.
const REGLAS = {
  largo: (p) => p.length >= 6,
  mayus: (p) => /[A-Z]/.test(p),
  num: (p) => /\d/.test(p),
};
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const mostrarError = (msg, campo) => {
  err.textContent = msg;
  form.querySelectorAll("[aria-invalid]").forEach((c) => c.removeAttribute("aria-invalid"));
  if (campo) { campo.setAttribute("aria-invalid", "true"); campo.focus(); }
};
const limpiarError = () => mostrarError("");

// Si ya hay una sesión iniciada, no tiene sentido ver el formulario
const yaDentro = await getUser();
const pideElegir = new URLSearchParams(location.search).get("elegir") === "1";
if (yaDentro && yaDentro.admin && pideElegir) {
  (await import("./elegir-admin.js")).mostrarEleccion(yaDentro);
} else if (yaDentro) {
  location.replace(yaDentro.onboarding ? "/pages/inicio.html" : "/pages/onboarding.html");
} else {
  document.body.classList.remove("cargando");

  // Mostrar / ocultar contraseña: cada ojito controla su propio campo
  document.querySelectorAll(".pw-ver").forEach((boton) => {
    const campo = boton.parentElement.querySelector("input");
    boton.onclick = () => {
      const ver = campo.type === "password";
      campo.type = ver ? "text" : "password";
      const texto = ver ? "Ocultar contraseña" : "Mostrar contraseña";
      boton.setAttribute("aria-pressed", String(ver));
      boton.setAttribute("aria-label", texto);
      boton.title = texto;
      boton.querySelector(".ojo").toggleAttribute("hidden", ver);       // los SVG no tienen la propiedad .hidden
      boton.querySelector(".ojo-x").toggleAttribute("hidden", !ver);
      campo.focus();
    };
  });

  // Registro: marca cada regla de la lista mientras la persona escribe
  const reglasLista = $("reglasPw");
  if (esRegistro && reglasLista) {
    const actualizarReglas = () => {
      const p = form.elements.password.value;
      reglasLista.querySelectorAll("[data-regla]").forEach((li) => {
        const cumple = REGLAS[li.dataset.regla]?.(p);
        li.classList.toggle("ok", Boolean(cumple));
      });
    };
    form.elements.password.addEventListener("input", actualizarReglas);
    actualizarReglas();
  }

  // En la app de Android, Google no deja entrar dentro de la app: se abre en el navegador del celular y al terminar
  // vuelve a la app con un código de un solo uso (así la sesión y el widget quedan en la app).
  const enApp = Boolean(globalThis.CodigoCampApp) || /CodigoCampApp\//.test(navigator.userAgent);
  document.querySelectorAll('a.google-acceso').forEach((a) => {
    if (!enApp) return;
    a.addEventListener("click", async (e) => {
      e.preventDefault();
      // Secreto que solo conoce la app: el navegador solo ve su sha256. Mientras eliges tu cuenta en el navegador, la app
      // pregunta al servidor y entra sola en cuanto Google termina (aunque el navegador no logre volver a la app).
      const bytes = crypto.getRandomValues(new Uint8Array(32));
      const secreto = btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      const huella = [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(secreto)))].map((x) => x.toString(16).padStart(2, "0")).join("");
      const url = new URL(`/auth/google/?app=1&espera=${huella}`, location.origin).href;
      try { globalThis.CodigoCampApp.abrirFuera(url); } catch { location.href = url; return; }
      esperarGoogle(secreto);
    });
  });

  function esperarGoogle(secreto) {
    document.getElementById("esperaGoogle")?.remove();
    const capa = document.createElement("div");
    capa.id = "esperaGoogle";
    capa.setAttribute("role", "dialog");
    capa.setAttribute("aria-live", "polite");
    capa.style.cssText = "position:fixed;inset:0;z-index:999;display:grid;place-items:center;padding:24px;background:rgba(5,10,25,.72);backdrop-filter:blur(4px)";
    capa.innerHTML = `<div style="max-width:340px;padding:26px 22px;border-radius:20px;background:var(--panel,#fff);color:var(--txt,#111);text-align:center;box-shadow:0 20px 50px rgba(0,0,0,.35)">
      <div style="width:42px;height:42px;margin:0 auto 12px;border:4px solid rgba(127,127,127,.25);border-top-color:var(--acc,#4ade80);border-radius:50%;animation:girarG 1s linear infinite"></div>
      <b style="font-size:18px">Continúa en el navegador</b>
      <p style="margin:10px 0 18px;line-height:1.5;opacity:.8">Elige tu cuenta de Google. Cuando termines, vuelve aquí: la app entra sola.</p>
      <button type="button" style="padding:11px 20px;border-radius:12px;border:1px solid rgba(127,127,127,.4);background:none;color:inherit;font:inherit;font-weight:700">Cancelar</button></div>
      <style>@keyframes girarG{to{transform:rotate(360deg)}}</style>`;
    document.body.append(capa);
    let vivo = true;
    capa.querySelector("button").onclick = () => { vivo = false; capa.remove(); };
    const inicio = Date.now();
    const csrf = () => decodeURIComponent((document.cookie.match(/(?:^|; )csrftoken=([^;]*)/) || [])[1] || "");
    const preguntar = async () => {
      if (!vivo) return;
      if (Date.now() - inicio > 180_000) { capa.remove(); mostrarError(ERRORES_GOOGLE.app); return; }
      try {
        const r = await fetch("/api/auth/app/esperar", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() }, body: JSON.stringify({ secreto }) });
        const j = await r.json().catch(() => ({}));
        if (j.listo) { vivo = false; location.replace(j.destino || "/pages/inicio.html?app=1"); return; }
        if (j.error) { vivo = false; capa.remove(); mostrarError(j.error); return; }
      } catch { /* sin red un momento: se vuelve a intentar */ }
      setTimeout(preguntar, document.hidden ? 1000 : 2000);
    };
    // Al volver a la app (la pestaña vuelve a estar visible) se pregunta enseguida.
    document.addEventListener("visibilitychange", () => { if (!document.hidden && vivo) preguntar(); });
    setTimeout(preguntar, 2500);
  }

  // Si Google no dejó entrar, el servidor vuelve con ?error=…: se explica qué pasó (antes no se veía nada).
  const params = new URLSearchParams(location.search);
  const ERRORES_GOOGLE = {
    google_config: "«Continuar con Google» no está disponible en este momento. Entra con tu correo y contraseña.",
    google_email: "Tu cuenta de Google no tiene un correo verificado. Usa otra cuenta de Google o entra con tu correo y contraseña.",
    google_conflict: "Ese correo ya está unido a OTRA cuenta de Google. Entra con la cuenta de Google que usaste la primera vez, o con tu correo y contraseña (si no la recuerdas: «¿Olvidaste tu contraseña?»).",
    google_inactive: "Esta cuenta está desactivada.",
    bloqueada: "Tu cuenta fue bloqueada por incumplir las normas de CódigoCamp. Revisa tu correo: ahí está el motivo.",
    app: "El enlace para volver a la app venció o ya se usó. Toca otra vez «Continuar con Google».",
  };
  const MOTIVOS_GOOGLE = {
    estado: "Google volvió a una dirección distinta a la que usaste para entrar. Abre CódigoCamp siempre con la misma dirección (por ejemplo http://localhost:5000, no 127.0.0.1) y vuelve a intentarlo.",
    rechazo: "Cancelaste el inicio de sesión en Google.",
    otro: "Google no pudo completar el inicio de sesión. Vuelve a intentarlo; si sigue, revisa que la dirección de redirección esté registrada en Google Cloud.",
  };
  const codigo = params.get("error");
  if (codigo) {
    mostrarError(codigo === "google" ? (MOTIVOS_GOOGLE[params.get("motivo")] || MOTIVOS_GOOGLE.otro) : (ERRORES_GOOGLE[codigo] || "No se pudo iniciar sesión con Google. Inténtalo otra vez."));
    history.replaceState(null, "", location.pathname + location.hash);
  }

  // Al escribir de nuevo, se quita el mensaje de error anterior
  form.addEventListener("input", limpiarError);

  // Devuelve el mensaje de error y el campo afectado, o null si todo está bien
  const validar = (d) => {
    const f = form.elements;
    if (esRegistro) {
      if (d.nombre.length < 2) return ["Escribe tu nombre (mínimo 2 letras).", f.nombre];
      if (d.nombre.length > 50) return ["El nombre es demasiado largo (máximo 50 caracteres).", f.nombre];
    }
    if (!EMAIL.test(d.email)) return ["Escribe un correo válido, por ejemplo tucorreo@ejemplo.com.", f.email];
    if (!d.password) return ["Escribe tu contraseña.", f.password];
    if (esRegistro) {
      if (!Object.values(REGLAS).every((ok) => ok(d.password)))
        return ["La contraseña debe tener mínimo 6 caracteres, una mayúscula y un número.", f.password];
      if (d.password !== d.password2) return ["Las contraseñas no coinciden.", f.password2];
    }
    return null;
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    limpiarError();

    const datos = {
      email: form.elements.email.value.trim().toLowerCase(),
      password: form.elements.password.value,
    };
    if (esRegistro) {
      datos.nombre = form.elements.nombre.value.trim();
      datos.password2 = form.elements.password2.value;
    }

    const problema = validar(datos);
    if (problema) { mostrarError(...problema); return; }
    delete datos.password2; // el servidor no lo necesita

    const boton = form.querySelector("[type=submit]");
    const textoBoton = boton.textContent;
    boton.disabled = true;
    boton.textContent = esRegistro ? "Creando cuenta…" : "Entrando…";
    try {
      const r = await api(esRegistro ? "/api/auth/register/" : "/api/auth/login/", datos);
      setGuest(false);
      if (r.user.admin) { (await import("./elegir-admin.js")).mostrarEleccion(r.user); return; }
      location.href = r.user.onboarding ? "/pages/inicio.html" : "/pages/onboarding.html";
    } catch (e2) {
      mostrarError(e2?.message || "No se pudo conectar con el servidor. Inténtalo de nuevo.");
      boton.disabled = false;
      boton.textContent = textoBoton;
    }
  };
}
