const ed = document.getElementById("ed");
const out = document.getElementById("out");
const mode = document.getElementById("mode");

// Modo JavaScript: muestra en pantalla lo que escribas con console.log
function envolverJs(code) {
  return `<pre id="o" style="font:14px monospace;margin:0;white-space:pre-wrap"></pre>
<script>
const o = document.getElementById("o");
const w = (...a) => { o.textContent += a.map(x => typeof x === "object" ? JSON.stringify(x) : String(x)).join(" ") + "\\n"; };
console.log = w; console.error = w;
window.onerror = (m) => { w("Error: " + m); };
try {
${code}
} catch (e) { w("Error: " + e.message); }
<\/script>`;
}

export function run() {
  out.srcdoc = mode.value === "js" ? envolverJs(ed.value) : ed.value; // iframe con sandbox
}

export function loadInLab(code, m = "html") {
  mode.value = m;
  ed.value = code;
  run();
}

export const getCode = () => ed.value;
export const getModeLabel = () => (mode.value === "js" ? "JavaScript" : "HTML/CSS");

export function initLab(defaultCode) {
  ed.value = defaultCode;
  document.getElementById("run").onclick = run;
  mode.onchange = run;
  run();
}
