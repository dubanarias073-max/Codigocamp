// CódigoCamp · widget para iPhone, iPad y Mac (app gratuita «Scriptable» de la App Store).
// Cómo usarlo: Configuración → App y widgets → «Widget para iPhone/iPad». Este archivo ya está conectado a tu sesión
// (sigue funcionando hasta que cierres sesión en CódigoCamp).
// En el widget, «Parameter» puede ser: racha (por defecto), meta o calendario.
// Tamaños: pequeño, mediano, grande y los de la pantalla de bloqueo (circular, rectangular y en línea).

const BASE = "__CC_BASE__";
const TOKEN = "__CC_TOKEN__";
const VISTA = String((typeof args !== "undefined" && args.widgetParameter) || "racha").trim().toLowerCase();
const fm = FileManager.local();
const cache = fm.joinPath(fm.documentsDirectory(), "codigocamp-widget.json");

const C = { fondo1: new Color("#0b1020"), fondo2: new Color("#121a33"), texto: new Color("#e5eaff"), sub: new Color("#8b95b8"),
  fuego: new Color("#ff9f1c"), verde: new Color("#caff4e"), rojo: new Color("#ff6b6b"), cian: new Color("#39e7ff") };

async function cargar() {
  try {
    const r = new Request(`${BASE}/api/widget/?t=${encodeURIComponent(TOKEN)}`);
    r.timeoutInterval = 20;
    r.headers = { Accept: "application/json" };
    const d = await r.loadJSON();
    if (r.response.statusCode !== 200) throw new Error(d.error || `HTTP ${r.response.statusCode}`);
    fm.writeString(cache, JSON.stringify(d));
    return { d, viejo: false };
  } catch (e) {
    if (fm.fileExists(cache)) return { d: JSON.parse(fm.readString(cache)), viejo: true, error: String(e.message || e) };
    return { d: null, error: String(e.message || e) };
  }
}

function texto(pila, t, tam, color = C.texto, negrita = false) {
  const x = pila.addText(String(t));
  x.font = negrita ? Font.boldSystemFont(tam) : Font.systemFont(tam);
  x.textColor = color;
  x.minimumScaleFactor = 0.6;
  x.lineLimit = 1;
  return x;
}

function semana(pila, d, tam) {
  const fila = pila.addStack();
  fila.layoutHorizontally();
  for (const dia of d.semana || []) {
    const col = fila.addStack();
    col.layoutVertically();
    col.centerAlignContent();
    const l = col.addText(dia.letra); l.font = Font.mediumSystemFont(tam * 0.7); l.textColor = dia.hoy ? C.texto : C.sub; l.centerAlignText();
    const i = col.addText(dia.icono); i.font = Font.systemFont(tam); i.centerAlignText();
    fila.addSpacer();
  }
}

function barra(pila, pct, ancho) {
  const ctx = new DrawContext();
  ctx.size = new Size(ancho, 8);
  ctx.opaque = false;
  ctx.respectScreenScale = true;
  const fondo = new Path(); fondo.addRoundedRect(new Rect(0, 0, ancho, 8), 4, 4);
  ctx.addPath(fondo); ctx.setFillColor(new Color("#ffffff", 0.15)); ctx.fillPath();
  const lleno = new Path(); lleno.addRoundedRect(new Rect(0, 0, Math.max(8, ancho * Math.min(100, pct) / 100), 8), 4, 4);
  ctx.addPath(lleno); ctx.setFillColor(C.verde); ctx.fillPath();
  pila.addImage(ctx.getImage()).imageSize = new Size(ancho, 8);
}

function crear({ d, viejo, error }) {
  const fam = config.widgetFamily || "medium";
  const w = new ListWidget();
  w.refreshAfterDate = new Date(Date.now() + 30 * 60 * 1000);
  w.url = d?.url_practicar || `${BASE}/pages/inicio.html?app=1`;

  // ---- pantalla de bloqueo ----
  if (fam === "accessoryInline") { w.addText(d ? `🔥 ${d.racha} · ${d.practicado_hoy ? "✓ hoy" : "practica hoy"}` : "CódigoCamp"); return w; }
  if (fam === "accessoryCircular") {
    w.addAccessoryWidgetBackground = true;
    const a = w.addText(d ? "🔥" : "⚠️"); a.font = Font.systemFont(14); a.centerAlignText();
    const b = w.addText(d ? String(d.racha) : "—"); b.font = Font.boldSystemFont(20); b.centerAlignText(); b.minimumScaleFactor = 0.5;
    return w;
  }
  if (fam === "accessoryRectangular") {
    texto(w, d ? `🔥 ${d.racha} días de racha` : "CódigoCamp", 14, Color.white(), true);
    texto(w, d ? `${d.xp_hoy}/${d.meta_xp} XP hoy` : "Sin datos", 12, Color.white());
    texto(w, d ? (d.practicado_hoy ? "✓ Ya practicaste" : "Practica hoy") : (error || ""), 11, Color.white());
    return w;
  }

  const g = new LinearGradient(); g.colors = [C.fondo1, C.fondo2]; g.locations = [0, 1]; w.backgroundGradient = g;
  w.setPadding(14, 14, 12, 14);
  if (!d) {
    texto(w, "CódigoCamp", 15, C.verde, true); w.addSpacer(6);
    const e = w.addText(error && /sesi[oó]n|401/i.test(error) ? "Tu sesión de CódigoCamp se cerró. Inicia sesión y vuelve a descargar el widget en Configuración → App y widgets." : `Sin conexión: ${error || ""}`);
    e.font = Font.systemFont(12); e.textColor = C.sub;
    return w;
  }
  const chico = fam === "small";
  const cab = w.addStack(); cab.centerAlignContent();
  texto(cab, VISTA === "meta" ? "Meta de hoy" : VISTA === "calendario" ? "Calendario de racha" : "CódigoCamp", chico ? 11 : 12, C.sub, true);
  cab.addSpacer();
  texto(cab, `❤️ ${d.vidas}${chico ? "" : `  💎 ${d.diamantes}`}`, chico ? 11 : 12, C.texto);
  w.addSpacer(chico ? 4 : 6);

  if (VISTA === "meta") {
    texto(w, `${d.xp_hoy} / ${d.meta_xp} XP`, chico ? 22 : 26, C.texto, true);
    w.addSpacer(6); barra(w, d.progreso_hoy, chico ? 120 : 280); w.addSpacer(6);
    texto(w, `${d.progreso_hoy}% completado · 🔥 ${d.racha}`, 12, C.sub);
  } else {
    const fila = w.addStack(); fila.centerAlignContent();
    texto(fila, "🔥", chico ? 26 : 30);
    fila.addSpacer(6);
    const col = fila.addStack(); col.layoutVertically();
    texto(col, d.racha, chico ? 26 : 30, C.fuego, true);
    texto(col, d.racha === 1 ? "día de racha" : "días de racha", 11, C.sub);
    if (!chico && VISTA === "calendario") { fila.addSpacer(); const m = fila.addStack(); m.layoutVertically(); texto(m, `Mejor: ${d.racha_maxima}`, 12, C.texto, true); texto(m, `🧊 ${d.salvarrachas} salvarrachas`, 11, C.sub); }
    w.addSpacer(chico ? 6 : 8);
    if (!chico || fam === "large") semana(w, d, fam === "large" ? 18 : 14);
    else texto(w, d.semana_texto, 12, C.texto);
  }
  w.addSpacer();
  const pie = texto(w, viejo ? `Sin conexión · ${d.actualizado || ""}` : d.estado, 11, d.practicado_hoy ? C.verde : (d.racha && !d.practicado_hoy ? C.fuego : C.sub), true);
  pie.lineLimit = 2;
  if (fam === "large") {
    w.addSpacer(8);
    texto(w, `✨ ${d.xp} XP en total · Meta: ${d.xp_hoy}/${d.meta_xp} XP hoy`, 12, C.sub);
  }
  return w;
}

const resultado = await cargar();
const widget = crear(resultado);
if (config.runsInWidget || config.runsInAccessoryWidget) Script.setWidget(widget);
else await widget.presentMedium();
Script.complete();
