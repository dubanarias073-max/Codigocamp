// Puente con la app de Android (apps/android): dentro de la app existe window.CodigoCampApp.
// El widget de la pantalla de inicio usa la sesión de la app: cada vez que se abre una página con sesión,
// la app recibe el token de ESTA sesión; al cerrar sesión, el widget se desconecta.
export const enApp = () => typeof window !== "undefined" && !!window.CodigoCampApp;

let enviado = false;
export async function sincronizarWidgetApp(api) {
  if (!enApp() || enviado) return;
  enviado = true;
  try {
    const e = await api("/api/widget/conectar/");
    window.CodigoCampApp.conectarWidget(e.base, e.token);
  } catch { enviado = false; }
}

export function desconectarWidgetApp() {
  try { if (enApp()) window.CodigoCampApp.desconectarWidget(); } catch { /* app vieja */ }
}
