// Progreso de retos (XP, racha, niveles). Se guarda en el navegador, separado por usuario.
const clave = (id) => "cc_retos_" + (id ?? "invitado");
const vacio = () => ({ xp: 0, racha: 0, ultimoDia: null, niveles: {} });

export const fechaLocal = (d = new Date()) => d.toLocaleDateString("en-CA"); // AAAA-MM-DD
const ayerDe = (d) => { const x = new Date(d); x.setDate(x.getDate() - 1); return fechaLocal(x); };

export function cargarProgreso(id) {
  try {
    const d = JSON.parse(localStorage.getItem(clave(id)));
    if (d && typeof d === "object") return { ...vacio(), ...d, niveles: d.niveles || {} };
  } catch { /* sin datos */ }
  return vacio();
}

export function guardarProgreso(id, p) {
  try { localStorage.setItem(clave(id), JSON.stringify(p)); } catch { /* almacenamiento no disponible */ }
}

// Días seguidos con actividad. Si pasó más de un día sin practicar, vuelve a 0.
export function rachaActual(p, ahora = new Date()) {
  if (!p.ultimoDia) return 0;
  if (p.ultimoDia === fechaLocal(ahora) || p.ultimoDia === ayerDe(ahora)) return p.racha;
  return 0;
}

export function registrarActividad(p, ahora = new Date()) {
  const hoy = fechaLocal(ahora);
  if (p.ultimoDia === hoy) return p;
  p.racha = p.ultimoDia === ayerDe(ahora) ? p.racha + 1 : 1;
  p.ultimoDia = hoy;
  return p;
}

export const nivelUsuario = (xp) => Math.floor(xp / 100) + 1;
