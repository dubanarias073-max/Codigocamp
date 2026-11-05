// Ejecuta el código del alumno en un Web Worker (aislado y con tiempo límite).
const workerFn = () => {
  const construir = (codigo, fn) =>
    new Function(codigo + "\n;return typeof " + fn + " === 'function' ? " + fn + " : undefined;")();
  const norm = (v) => {
    if (v === undefined) return "undefined";
    if (typeof v === "number" && !Number.isFinite(v)) return String(v);
    try { return JSON.stringify(v); } catch { return String(v); }
  };
  self.onmessage = (e) => {
    const d = e.data;
    try {
      if (d.modo === "tests") {
        const f = construir(d.codigo, d.fn);
        if (!f) { postMessage({ error: "No encontré la función «" + d.fn + "». Mantén ese nombre." }); return; }
        const res = d.casos.map((c) => {
          const entrada = c.a.map(norm).join(", ");
          const base = { entrada, esperado: norm(c.r), v: c.v !== false };
          try { const got = f(...c.a); return { ...base, ok: norm(got) === norm(c.r), got: norm(got) }; }
          catch (err) { return { ...base, ok: false, got: "Error: " + err.message }; }
        });
        postMessage({ res });
      } else {
        const mala = construir(d.defectuosa, d.fn);
        const buena = construir(d.correcta, d.fn);
        let a, b;
        try { a = norm(mala(...d.args)); } catch (err) { a = "Error: " + err.message; }
        try { b = norm(buena(...d.args)); } catch (err) { b = "Error: " + err.message; }
        postMessage({ distinto: a !== b, defectuosa: a, correcta: b });
      }
    } catch (err) { postMessage({ error: err.message }); }
  };
};

export const WORKER_SRC = "(" + workerFn.toString() + ")();";

export function correr(payload, ms = 3000) {
  return new Promise((resolve) => {
    let w, url;
    const fin = (r) => {
      clearTimeout(t);
      if (w) w.terminate();
      if (url) URL.revokeObjectURL(url);
      resolve(r);
    };
    const t = setTimeout(() => fin({ error: "Tiempo agotado: ¿tu código tiene un bucle infinito?" }), ms);
    try {
      url = URL.createObjectURL(new Blob([WORKER_SRC], { type: "text/javascript" }));
      w = new Worker(url);
      w.onmessage = (e) => fin(e.data);
      w.onerror = (e) => fin({ error: e.message || "Error al ejecutar el código" });
      w.postMessage(payload);
    } catch (e) {
      fin({ error: "No se pudo ejecutar: " + e.message });
    }
  });
}
