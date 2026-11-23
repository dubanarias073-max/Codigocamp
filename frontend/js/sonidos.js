// Sonidos de CódigoCamp con temática de código y sistemas operativos (originales: se sintetizan con Web Audio, sin archivos).
//   correcto («compilación exitosa») · incorrecto (zumbido de error del sistema) · clic (tecla mecánica) · teclear ·
//   moneda (commit) · leccion (arranque del sistema) · racha (llamarada + acorde de inicio) · cofre (descomprimir datos) ·
//   premio (notificación) · legendario (logro desbloqueado, consola retro) · ejecutar (Enter + ventilador) ·
//   programa_ok (proceso terminó con código 0) · programa_error (excepción) · arranque (inicio de sesión) ·
//   enviar / recibir (mensajes) · notificacion · guardar (Ctrl+S) · equipar · boop (tocar a Codi) · abrir · ia (respuesta) · nivel
// Se apagan en Configuración («Sonidos»), igual que los de las preguntas (cc_sonido = "0").

let ctx = null;
let salida = null;

export function sonidoActivo() {
  try { return localStorage.getItem("cc_sonido") !== "0"; } catch { return true; }
}

/** Hay que llamarlo dentro de un toque o clic (los navegadores no dejan sonar antes). */
export function prepararSonido() {
  if (!sonidoActivo()) return null;
  try {
    const A = window.AudioContext || window.webkitAudioContext;
    if (!A) return null;
    ctx ||= new A();
    if (!salida) {
      // Compresor suave: así los acordes no saturan en los parlantes del celular
      const comp = ctx.createDynamicsCompressor();
      comp.threshold.value = -18; comp.ratio.value = 4;
      salida = ctx.createGain();
      salida.gain.value = 0.9;
      salida.connect(comp).connect(ctx.destination);
    }
    ctx.resume?.().catch(() => {});
    return ctx;
  } catch { return null; }
}
// El primer toque en cualquier parte de la página deja el audio listo
for (const ev of ["pointerdown", "keydown", "touchstart"]) addEventListener(ev, () => prepararSonido(), { once: true, passive: true, capture: true });

function tono(f, t, dur, { tipo = "sine", fin = f, vol = 0.12, ataque = 0.012, destino = salida } = {}) {
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = tipo;
  o.frequency.setValueAtTime(f, t);
  if (fin !== f) o.frequency.exponentialRampToValueAtTime(fin, t + dur);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol, t + ataque);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g).connect(destino);
  o.start(t);
  o.stop(t + dur + 0.03);
}
function filtrado(f, t, dur, { tipo = "square", fin = f, vol = 0.08, corte = 1800, ataque = 0.005 } = {}) {
  const lp = ctx.createBiquadFilter();
  lp.type = "lowpass"; lp.frequency.value = corte; lp.Q.value = 0.7;
  lp.connect(salida);
  tono(f, t, dur, { tipo, fin, vol, ataque, destino: lp });
}
/** Tecla mecánica: chasquido de ruido muy corto + «toc» grave. */
function tecla(t, { vol = 0.06, agudo = 4500 } = {}) {
  ruido(t, 0.018, { vol, desde: agudo, hasta: agudo * 1.4, q: 2.5 });
  tono(180 + Math.random() * 60, t, 0.03, { tipo: "triangle", vol: vol * 0.7, ataque: 0.002 });
}
function ruido(t, dur, { vol = 0.08, desde = 800, hasta = 4000, q = 0.8 } = {}) {
  const n = Math.max(1, Math.floor(ctx.sampleRate * dur));
  const buf = ctx.createBuffer(1, n, ctx.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
  const src = ctx.createBufferSource();
  src.buffer = buf;
  const f = ctx.createBiquadFilter();
  f.type = "bandpass"; f.Q.value = q;
  f.frequency.setValueAtTime(desde, t);
  f.frequency.exponentialRampToValueAtTime(hasta, t + dur);
  const g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol, t + dur * 0.25);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  src.connect(f).connect(g).connect(salida);
  src.start(t);
  src.stop(t + dur + 0.02);
}
const nota = (n) => 440 * 2 ** ((n - 69) / 12);   // número MIDI → Hz

const SONIDOS = {
  // ✔ Compilación exitosa: Enter + dos «bips» de terminal que suben + destello
  correcto(t) {
    tecla(t, { vol: 0.05 });
    filtrado(nota(79), t + 0.03, 0.09, { tipo: "square", vol: 0.07, corte: 3200 });
    filtrado(nota(86), t + 0.11, 0.18, { tipo: "square", vol: 0.07, corte: 3600, fin: nota(91) });
    tono(nota(98), t + 0.2, 0.22, { vol: 0.035 });
  },
  // ✖ Error del sistema: zumbido grave de dos tonos (como un «bonk» de error), filtrado para que no moleste
  incorrecto(t) {
    filtrado(nota(50), t, 0.16, { tipo: "sawtooth", vol: 0.09, corte: 900 });
    filtrado(nota(44), t + 0.14, 0.26, { tipo: "sawtooth", vol: 0.09, corte: 700, fin: nota(41) });
    ruido(t, 0.05, { vol: 0.03, desde: 300, hasta: 500, q: 4 });
  },
  clic(t) { tecla(t, { vol: 0.05 }); },
  // Ráfaga de tecleo (Codi escribiendo código)
  teclear(t) { for (let i = 0; i < 7; i++) tecla(t + i * (0.055 + Math.random() * 0.04), { vol: 0.04, agudo: 3800 + Math.random() * 1600 }); },
  // git commit: «ping» de 8 bits
  moneda(t) { filtrado(nota(88), t, 0.06, { tipo: "square", vol: 0.05, corte: 5000 }); filtrado(nota(95), t + 0.06, 0.16, { tipo: "square", vol: 0.05, corte: 6000 }); },
  // Lección terminada = el sistema arranca: acorde cálido que se abre + arpegio de 8 bits
  leccion(t) {
    [48, 55, 64, 67].forEach((n, i) => tono(nota(n), t + i * 0.02, 1.1, { tipo: "triangle", vol: 0.06, ataque: 0.18 }));
    [72, 76, 79, 84, 88].forEach((n, i) => filtrado(nota(n), t + 0.35 + i * 0.07, 0.14, { tipo: "square", vol: 0.045, corte: 4200 }));
    tono(nota(91), t + 0.75, 0.6, { vol: 0.04, ataque: 0.02 });
  },
  // ¡Racha de hoy! Llamarada + acorde de inicio
  racha(t) {
    ruido(t, 0.45, { vol: 0.07, desde: 300, hasta: 3500 });
    [55, 62, 67, 71].forEach((n, i) => tono(nota(n), t + 0.1 + i * 0.03, 0.9, { tipo: "triangle", vol: 0.05, ataque: 0.12 }));
    [79, 83, 86, 91].forEach((n, i) => filtrado(nota(n), t + 0.4 + i * 0.06, 0.16, { tipo: "square", vol: 0.04, corte: 4500 }));
  },
  // Cofre = descomprimiendo datos: chirridos rápidos de transferencia + destellos
  cofre(t) {
    for (let i = 0; i < 10; i++) filtrado(nota(60 + ((i * 7) % 24)), t + i * 0.025, 0.03, { tipo: "square", vol: 0.035, corte: 3000 });
    tecla(t + 0.27, { vol: 0.06 });
    ruido(t + 0.28, 0.25, { vol: 0.05, desde: 2000, hasta: 9000, q: 0.6 });
    [79, 83, 86, 91, 95].forEach((n, i) => tono(nota(n), t + 0.32 + i * 0.05, 0.22, { vol: 0.045 }));
  },
  // Notificación del sistema (cada premio)
  premio(t) { tono(nota(84), t, 0.08, { vol: 0.06 }); tono(nota(91), t + 0.07, 0.18, { tipo: "triangle", vol: 0.06 }); },
  // Logro desbloqueado: arpegio de consola retro + acorde brillante
  legendario(t) {
    [72, 76, 79, 84, 88, 91, 96].forEach((n, i) => filtrado(nota(n), t + i * 0.05, 0.1, { tipo: "square", vol: 0.045, corte: 6000 }));
    [84, 88, 91, 96].forEach((n) => tono(nota(n), t + 0.38, 0.9, { vol: 0.04, ataque: 0.03 }));
    ruido(t + 0.36, 0.6, { vol: 0.02, desde: 5000, hasta: 12000 });
  },
  // Ejecutar: Enter + zumbido corto de «ventilador» que arranca
  ejecutar(t) { tecla(t, { vol: 0.06 }); ruido(t + 0.02, 0.22, { vol: 0.025, desde: 150, hasta: 900, q: 1.2 }); },
  // El programa terminó bien (exit 0)
  programa_ok(t) { filtrado(nota(81), t, 0.07, { vol: 0.05, corte: 4000 }); filtrado(nota(88), t + 0.07, 0.14, { vol: 0.05, corte: 4500 }); },
  // El programa terminó con error (excepción / exit ≠ 0)
  programa_error(t) { filtrado(nota(47), t, 0.22, { tipo: "sawtooth", vol: 0.07, corte: 800, fin: nota(43) }); },
  // Mensaje enviado: «whoosh» que sube (como un paquete de red que sale)
  enviar(t) { ruido(t, 0.16, { vol: 0.045, desde: 600, hasta: 5000, q: 0.9 }); filtrado(nota(84), t + 0.08, 0.07, { tipo: "square", vol: 0.035, corte: 5000 }); },
  // Mensaje recibido: dos gotas suaves (paquete que llega)
  recibir(t) { tono(nota(79), t, 0.09, { tipo: "triangle", vol: 0.07 }); tono(nota(86), t + 0.08, 0.16, { tipo: "triangle", vol: 0.06 }); },
  // Notificación (solicitud de amistad, aviso): campanita de sistema de 3 notas
  notificacion(t) { [88, 84, 91].forEach((n, i) => tono(nota(n), t + i * 0.09, 0.2, { vol: 0.05 })); },
  // Guardar (Ctrl+S): chasquido de disquete + bip corto
  guardar(t) { tecla(t, { vol: 0.05, agudo: 3000 }); ruido(t + 0.02, 0.08, { vol: 0.03, desde: 900, hasta: 1500, q: 3 }); filtrado(nota(84), t + 0.09, 0.06, { vol: 0.035, corte: 4000 }); },
  // Equipar un cosmético: destello mágico que sube
  equipar(t) { [76, 81, 86, 93].forEach((n, i) => tono(nota(n), t + i * 0.04, 0.18, { vol: 0.04 })); ruido(t + 0.05, 0.3, { vol: 0.02, desde: 4000, hasta: 11000 }); },
  // Tocar a Codi: «boop» de robot
  boop(t) { filtrado(nota(72), t, 0.07, { tipo: "square", vol: 0.05, corte: 2500, fin: nota(79) }); filtrado(nota(84), t + 0.07, 0.09, { tipo: "square", vol: 0.04, corte: 3000, fin: nota(76) }); },
  // Codi contento (caricias, bailar): trino de robot que sube
  codi_feliz(t) { [79, 84, 88, 91].forEach((n, i) => filtrado(nota(n), t + i * 0.06, 0.08, { tipo: "square", vol: 0.035, corte: 3200 })); },
  // Codi se ríe: «ji-ji-ji» de 8 bits
  codi_risa(t) { for (let i = 0; i < 4; i++) filtrado(nota(86 - i), t + i * 0.09, 0.06, { tipo: "square", vol: 0.04, corte: 3500, fin: nota(90 - i) }); },
  // Codi se duerme / despierta
  codi_bostezo(t) { tono(nota(67), t, 0.5, { tipo: "triangle", vol: 0.05, fin: nota(55) }); },
  codi_despierta(t) { tono(nota(60), t, 0.18, { tipo: "triangle", vol: 0.05, fin: nota(76) }); filtrado(nota(84), t + 0.16, 0.08, { tipo: "square", vol: 0.03, corte: 3000 }); },
  // Abrir un panel o menú: soplo corto
  abrir(t) { ruido(t, 0.09, { vol: 0.025, desde: 1500, hasta: 4500, q: 1 }); },
  // La IA respondió: chispa digital que sube (procesamiento terminado)
  ia(t) {
    for (let i = 0; i < 5; i++) filtrado(nota(84 + i * 3), t + i * 0.03, 0.05, { tipo: "square", vol: 0.025, corte: 7000 });
    tono(nota(96), t + 0.16, 0.35, { vol: 0.035 });
  },
  // Subir de nivel: fanfarria corta de 8 bits
  nivel(t) {
    [67, 71, 74, 79].forEach((n, i) => filtrado(nota(n), t + i * 0.08, 0.12, { tipo: "square", vol: 0.05, corte: 4500 }));
    [79, 83, 86].forEach((n) => tono(nota(n), t + 0.34, 0.7, { tipo: "triangle", vol: 0.045, ataque: 0.04 }));
  },
  // Inicio de sesión: acorde de arranque corto
  arranque(t) {
    [60, 64, 67, 72].forEach((n, i) => tono(nota(n), t + i * 0.06, 0.7 - i * 0.08, { tipo: "triangle", vol: 0.05, ataque: 0.05 }));
    tono(nota(79), t + 0.3, 0.5, { vol: 0.035 });
  },
};

/** Suena un efecto. Devuelve false si está apagado o el navegador no deja (antes de tocar la página). */
export function sonar(nombre, retraso = 0) {
  if (!sonidoActivo()) return false;
  const c = prepararSonido();
  if (!c || !SONIDOS[nombre]) return false;
  const go = () => { try { SONIDOS[nombre](c.currentTime + 0.01 + retraso); } catch { /* nada */ } };
  if (c.state === "running") go();
  else c.resume?.().then(go, () => {});
  return true;
}

/** Vibración corta en el celular junto con el sonido (si el teléfono lo permite). */
export function vibrar(patron = 20) { try { if (sonidoActivo()) navigator.vibrate?.(patron); } catch { /* nada */ } }
