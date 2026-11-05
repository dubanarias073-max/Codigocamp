// Lógica de configuracion.html
import { iniciar, api, esc, aviso, aplicarTema } from "/js/app.js";
const { user, prog } = await iniciar("configuracion");
const $ = (id) => document.getElementById(id);
$("nombre").value = user.nombre;
$("alias").value = user.alias || "";
$("codigo").textContent = user.codigo || "";
$("meta").value = String(prog.perfil.meta_minutos);
$("tema").value = user.tema || "auto";
$("tema").onchange = () => aplicarTema($("tema").value); // vista previa al instante
$("curso").innerHTML = (await api("/api/cursos/")).cursos.map((c) => `<option value="${c.slug}"${c.slug === prog.curso_actual?.slug ? " selected" : ""}>${esc(c.nombre)}</option>`).join("");
$("f").onsubmit = async (e) => {
  e.preventDefault();
  try {
    await api("/api/ajustes/", { nombre: $("nombre").value, alias: $("alias").value, curso: $("curso").value, meta: Number($("meta").value), tema: $("tema").value });
    aplicarTema($("tema").value);
    aviso("Cambios guardados");
  } catch (x) { aviso(x.message, true); }
};
$("salir").onclick = async () => { try { await api("/api/auth/logout/", {}); } catch {} location.href = "/"; };
