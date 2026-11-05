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
if (yaDentro) {
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
      location.href = r.user.onboarding ? "/pages/inicio.html" : "/pages/onboarding.html";
    } catch (e2) {
      mostrarError(e2?.message || "No se pudo conectar con el servidor. Inténtalo de nuevo.");
      boton.disabled = false;
      boton.textContent = textoBoton;
    }
  };
}
