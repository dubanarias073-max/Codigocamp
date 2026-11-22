// Service worker de CódigoCamp: hace que la app se pueda instalar, abre aunque falle la red (página «sin conexión»),
// guarda en caché los archivos de la interfaz y actualiza el widget de racha (Windows 11).
const VERSION = "cc-v6";
const BASE = ["/offline.html", "/css/app.css", "/css/tema.css", "/js/app.js", "/js/auth.js", "/js/iconos.js", "/js/cosmeticos.js", "/js/carga.js", "/js/tema.js", "/js/i18n.js", "/js/pwa.js",
  "/img/app/icon-192.png", "/img/app/icon-512.png", "/img/logo-icon.png", "/img/favicon.png", "/manifest.webmanifest"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;               // CDN, GitHub… directo
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/auth/")) return; // datos y sesión: siempre red
  if (req.mode === "navigate") {
    // Páginas: red primero (siempre lo último); si no hay red, la copia guardada o la página sin conexión.
    e.respondWith(fetch(req).then((r) => { const copia = r.clone(); if (r.ok) caches.open(VERSION).then((c) => c.put(req, copia)); return r; })
      .catch(async () => (await caches.match(req)) || caches.match("/offline.html")));
    return;
  }
  if (/^\/(css|js|widgets)\//.test(url.pathname) || url.pathname === "/manifest.webmanifest") {
    // Código de la interfaz: red primero, así cada actualización (arreglos de seguridad incluidos) se usa al instante.
    // Sin red, la última copia guardada.
    e.respondWith(fetch(req).then((r) => { if (r.ok && r.type === "basic") { const copia = r.clone(); caches.open(VERSION).then((c) => c.put(req, copia)); } return r; })
      .catch(async () => (await caches.match(req)) || Response.error()));
    return;
  }
  if (/^\/(img|vendor)\//.test(url.pathname)) {
    // Imágenes y librerías grandes (Monaco, Pyodide): lo guardado al instante y se actualiza por detrás.
    e.respondWith(caches.open(VERSION).then(async (c) => {
      const guardada = await c.match(req);
      const red = fetch(req).then((r) => { if (r.ok && r.type === "basic") c.put(req, r.clone()); return r; }).catch(() => guardada);
      return guardada || red;
    }));
  }
});

// ---- Widgets (Windows 11: panel de widgets) ----
async function actualizarWidget(widget) {
  const def = widget.definition;
  const [plantilla, datos] = await Promise.all([
    fetch(def.msAcTemplate).then((r) => r.text()),
    fetch(def.data, { credentials: "same-origin" }).then((r) => (r.ok ? r.text() : JSON.stringify({
      racha: "—", estado: "Inicia sesión en CódigoCamp", xp: "—", diamantes: "—", vidas: "—", meta: "—", nombre: "", xp_hoy: 0, meta_xp: "—", progreso_hoy: 0,
      racha_maxima: "—", salvarrachas: "—", titulo: "", semana_texto: "· · · · · · ·", semana: "LMXJVSD".split("").map((letra) => ({ letra, icono: "·" })),
      url_practicar: `${location.origin}/pages/login.html`, url_cofres: `${location.origin}/pages/login.html`, url_calendario: `${location.origin}/pages/login.html`,
    }))).catch(() => JSON.stringify({ racha: "—", estado: "Sin conexión", semana_texto: "· · · · · · ·", semana: "LMXJVSD".split("").map((letra) => ({ letra, icono: "·" })),
      url_practicar: `${location.origin}/pages/inicio.html?app=1`, url_cofres: `${location.origin}/pages/recompensas.html?app=1`, url_calendario: `${location.origin}/pages/perfil.html?app=1#calendario` })),
  ]);
  await self.widgets.updateByTag(def.tag, { template: plantilla, data: datos });
}
async function actualizarTodos() {
  if (!self.widgets) return;
  for (const tag of ["racha", "meta", "calendario"]) {
    const w = await self.widgets.getByTag(tag).catch(() => null);
    if (w) await actualizarWidget(w);
  }
}
self.addEventListener("widgetinstall", (e) => e.waitUntil(actualizarWidget(e.widget)));
self.addEventListener("widgetresume", (e) => e.waitUntil(actualizarWidget(e.widget)));
self.addEventListener("widgetclick", (e) => { if (e.action === "abrir") e.waitUntil(self.clients.openWindow("/pages/inicio.html?app=1")); });
self.addEventListener("widgetuninstall", () => {});
self.addEventListener("periodicsync", (e) => { if (e.tag === "widget-racha") e.waitUntil(actualizarTodos()); });
self.addEventListener("message", (e) => { if (e.data === "actualizar-widget") e.waitUntil(actualizarTodos()); });
