// Sonidos de CódigoCamp (como en Duolingo, pero propios): se sintetizan con Web Audio, sin archivos.
//   correcto · incorrecto · leccion (terminaste una lección) · racha (¡hiciste la racha de hoy!) · cofre (se abre) ·
//   premio (cada premio que sale del cofre) · legendario (premio exclusivo) · moneda · clic
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
  correcto(t) { tono(nota(76), t, 0.12, { fin: nota(79) }); tono(nota(83), t + 0.09, 0.2, { fin: nota(88) }); },
  incorrecto(t) { tono(nota(55), t, 0.18, { tipo: "triangle", fin: nota(50), vol: 0.1 }); tono(nota(50), t + 0.13, 0.24, { tipo: "triangle", fin: nota(45), vol: 0.09 }); },
  clic(t) { tono(nota(84), t, 0.05, { tipo: "square", vol: 0.04 }); },
  moneda(t) { tono(nota(88), t, 0.07, { tipo: "square", vol: 0.05 }); tono(nota(95), t + 0.06, 0.16, { tipo: "square", vol: 0.05 }); },
  // Terminaste la lección: fanfarria corta que sube (Do–Mi–Sol–Do) con un acorde final
  leccion(t) {
    [72, 76, 79].forEach((n, i) => tono(nota(n), t + i * 0.11, 0.16, { tipo: "triangle", vol: 0.11 }));
    [84, 88, 91].forEach((n) => tono(nota(n), t + 0.34, 0.55, { tipo: "sine", vol: 0.07 }));
    tono(nota(60), t + 0.34, 0.55, { tipo: "triangle", vol: 0.07 });
    for (let i = 0; i < 5; i++) tono(nota(96 + i * 2), t + 0.5 + i * 0.05, 0.12, { vol: 0.025 });
  },
  // ¡Racha de hoy! Llamarada (ruido que sube) + acorde cálido que crece
  racha(t) {
    ruido(t, 0.45, { vol: 0.07, desde: 300, hasta: 3500 });
    [67, 71, 74, 79].forEach((n, i) => tono(nota(n), t + 0.15 + i * 0.07, 0.6 - i * 0.05, { tipo: "sawtooth", vol: 0.035, ataque: 0.04 }));
    tono(nota(91), t + 0.45, 0.35, { vol: 0.06 });
    tono(nota(95), t + 0.58, 0.45, { vol: 0.05 });
  },
  // El cofre se abre: crujido de madera, golpe y destellos que suben
  cofre(t) {
    ruido(t, 0.22, { vol: 0.05, desde: 200, hasta: 600, q: 3 });
    tono(nota(43), t + 0.18, 0.18, { tipo: "triangle", fin: nota(36), vol: 0.14 });
    ruido(t + 0.2, 0.25, { vol: 0.06, desde: 2000, hasta: 9000, q: 0.6 });
    [79, 83, 86, 91, 95, 98].forEach((n, i) => tono(nota(n), t + 0.28 + i * 0.055, 0.25, { vol: 0.05 }));
  },
  // Cada premio que sale
  premio(t) { tono(nota(86), t, 0.09, { tipo: "triangle", vol: 0.07 }); tono(nota(93), t + 0.07, 0.2, { tipo: "sine", vol: 0.06 }); },
  // Premio exclusivo / legendario: acorde brillante con eco
  legendario(t) {
    [76, 80, 83, 88].forEach((n) => tono(nota(n), t, 0.9, { vol: 0.05, ataque: 0.03 }));
    [88, 92, 95, 100].forEach((n, i) => tono(nota(n), t + 0.12 + i * 0.08, 0.5, { vol: 0.035 }));
    ruido(t, 0.6, { vol: 0.025, desde: 5000, hasta: 12000 });
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
