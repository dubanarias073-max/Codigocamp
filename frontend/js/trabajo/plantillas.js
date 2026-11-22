// Plantillas de «npm create vite@latest mi-app -- --template react» (las mismas que crea Vite, en versión corta).
// Se ven en la vista previa (que hace de «npm run dev»): JSX/TSX se transpila y las librerías vienen de esm.sh.

const LOGO = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="#646cff"/><path d="M20 22l12 24 12-24" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>\n`;

const CSS_BASE = `:root {
  font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  background-color: #1a1a1a;
  cursor: pointer;
}

button:hover {
  border-color: #646cff;
}

@media (prefers-color-scheme: light) {
  :root { color: #213547; background-color: #ffffff; }
  button { background-color: #f9f9f9; }
}
`;

const APP_CSS = `#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
}

.card {
  padding: 2em;
}
`;

const html = (titulo, entrada, id = "root") => `<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${titulo}</title>
  </head>
  <body>
    <div id="${id}"></div>
    <script type="module" src="/src/${entrada}"></script>
  </body>
</html>
`;

const APP_REACT = (ts) => `import { useState } from 'react'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState${ts ? "<number>" : ""}(0)

  return (
    <>
      <img src={viteLogo} className="logo" alt="Logo" />
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          El contador va en {count}
        </button>
        <p>
          Edita <code>src/App.${ts ? "tsx" : "jsx"}</code> y abre la vista previa para ver el cambio.
        </p>
      </div>
    </>
  )
}

export default App
`;

const MAIN_REACT = (ts) => `import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.${ts ? "tsx" : "jsx"}'

createRoot(document.getElementById('root')${ts ? "!" : ""}).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
`;

const APP_PREACT = `import { useState } from 'preact/hooks'
import './app.css'

export function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <h1>Vite + Preact</h1>
      <div class="card">
        <button onClick={() => setCount((count) => count + 1)}>
          El contador va en {count}
        </button>
        <p>Edita <code>src/app.jsx</code> y abre la vista previa.</p>
      </div>
    </>
  )
}
`;

const MAIN_PREACT = `import { render } from 'preact'
import './index.css'
import { App } from './app.jsx'

render(<App />, document.getElementById('app'))
`;

const MAIN_VANILLA = (ts) => `import './style.css'
import { setupCounter } from './counter.${ts ? "ts" : "js"}'

document.querySelector${ts ? "<HTMLDivElement>" : ""}('#app')${ts ? "!" : ""}.innerHTML = \`
  <div>
    <h1>Hola, Vite</h1>
    <div class="card">
      <button id="counter" type="button"></button>
    </div>
  </div>
\`

setupCounter(document.querySelector${ts ? "<HTMLButtonElement>" : ""}('#counter')${ts ? "!" : ""})
`;

const COUNTER = (ts) => `export function setupCounter(element${ts ? ": HTMLButtonElement" : ""}) {
  let counter = 0
  const setCounter = (count${ts ? ": number" : ""}) => {
    counter = count
    element.innerHTML = \`El contador va en \${counter}\`
  }
  element.addEventListener('click', () => setCounter(counter + 1))
  setCounter(0)
}
`;

const TSCONFIG = (jsx) => JSON.stringify({
  compilerOptions: {
    target: "ES2022", useDefineForClassFields: true, lib: ["ES2022", "DOM", "DOM.Iterable"], module: "ESNext", skipLibCheck: true,
    moduleResolution: "bundler", allowImportingTsExtensions: true, noEmit: true, strict: true, ...(jsx ? { jsx: "react-jsx", ...(jsx === "preact" ? { jsxImportSource: "preact" } : {}) } : {}),
  },
  include: ["src"],
}, null, 2) + "\n";

const APP_VUE = `<script setup>
import { ref } from 'vue'
import Contador from './components/Contador.vue'

const nombre = ref('Vite + Vue')
</script>

<template>
  <h1>{{ nombre }}</h1>
  <Contador :inicio="0" />
  <p>Edita <code>src/App.vue</code> y abre la vista previa.</p>
</template>

<style scoped>
h1 { color: #42b883; }
</style>
`;

const CONTADOR_VUE = `<script setup>
import { ref } from 'vue'

const props = defineProps({ inicio: { type: Number, default: 0 } })
const cuenta = ref(props.inicio)
</script>

<template>
  <div class="card">
    <button type="button" @click="cuenta++">El contador va en {{ cuenta }}</button>
  </div>
</template>
`;

const MAIN_VUE = `import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')
`;

const APP_SVELTE = `<script>
  import Contador from './lib/Contador.svelte'
  let nombre = 'Vite + Svelte'
</script>

<main>
  <h1>{nombre}</h1>
  <Contador />
  <p>Edita <code>src/App.svelte</code> y abre la vista previa.</p>
</main>

<style>
  h1 { color: #ff3e00; }
</style>
`;

const CONTADOR_SVELTE = `<script>
  let cuenta = $state(0)
</script>

<div class="card">
  <button type="button" onclick={() => cuenta++}>El contador va en {cuenta}</button>
</div>
`;

const MAIN_SVELTE = `import { mount } from 'svelte'
import './app.css'
import App from './App.svelte'

const app = mount(App, { target: document.getElementById('app') })

export default app
`;

export const PLANTILLAS = ["vanilla", "vanilla-ts", "react", "react-ts", "preact", "vue", "svelte"];

/** Paquetes de cada plantilla: [dependencias, devDependencies]. */
export const PAQUETES = {
  vanilla: [[], ["vite"]],
  "vanilla-ts": [[], ["typescript", "vite"]],
  react: [["react", "react-dom"], ["@vitejs/plugin-react", "vite"]],
  "react-ts": [["react", "react-dom"], ["@types/react", "@types/react-dom", "@vitejs/plugin-react", "typescript", "vite"]],
  preact: [["preact"], ["@preact/preset-vite", "vite"]],
  vue: [["vue"], ["@vitejs/plugin-vue", "vite"]],
  svelte: [[], ["@sveltejs/vite-plugin-svelte", "svelte", "vite"]],
};

/** Versiones por si no hay conexión con el registro (las de finales de 2026 pueden ser más nuevas). */
export const VERSIONES_RESPALDO = {
  react: "19.1.0", "react-dom": "19.1.0", preact: "10.26.0", vite: "7.0.0", typescript: "5.8.3", "@vitejs/plugin-react": "4.6.0",
  "@preact/preset-vite": "2.10.0", "@types/react": "19.1.0", "@types/react-dom": "19.1.0",
  vue: "3.5.17", "@vitejs/plugin-vue": "6.0.0", svelte: "5.34.0", "@sveltejs/vite-plugin-svelte": "5.1.0",
};

/** Archivos de la plantilla { ruta relativa: texto } (sin package.json: lo arma paquetes.js con las versiones). */
export function archivosDePlantilla(plantilla, nombre) {
  const ts = plantilla.endsWith("-ts");
  const base = { "public/vite.svg": LOGO, ".gitignore": "node_modules\ndist\n*.local\n" };
  if (plantilla.startsWith("react")) {
    return {
      ...base, "index.html": html(nombre, `main.${ts ? "tsx" : "jsx"}`), [`src/main.${ts ? "tsx" : "jsx"}`]: MAIN_REACT(ts), [`src/App.${ts ? "tsx" : "jsx"}`]: APP_REACT(ts),
      "src/App.css": APP_CSS, "src/index.css": CSS_BASE,
      [`vite.config.${ts ? "ts" : "js"}`]: "import { defineConfig } from 'vite'\nimport react from '@vitejs/plugin-react'\n\nexport default defineConfig({\n  plugins: [react()],\n})\n",
      ...(ts ? { "tsconfig.json": TSCONFIG("react") } : {}),
    };
  }
  if (plantilla === "preact") {
    return {
      ...base, "index.html": html(nombre, "main.jsx", "app"), "src/main.jsx": MAIN_PREACT, "src/app.jsx": APP_PREACT, "src/app.css": APP_CSS.replace("#root", "#app"), "src/index.css": CSS_BASE,
      "vite.config.js": "import { defineConfig } from 'vite'\nimport preact from '@preact/preset-vite'\n\nexport default defineConfig({\n  plugins: [preact()],\n})\n",
    };
  }
  if (plantilla === "vue") {
    return {
      ...base, "index.html": html(nombre, "main.js", "app"), "src/main.js": MAIN_VUE, "src/App.vue": APP_VUE, "src/components/Contador.vue": CONTADOR_VUE,
      "src/style.css": CSS_BASE + APP_CSS.replace("#root", "#app"),
      "vite.config.js": "import { defineConfig } from 'vite'\nimport vue from '@vitejs/plugin-vue'\n\nexport default defineConfig({\n  plugins: [vue()],\n})\n",
    };
  }
  if (plantilla === "svelte") {
    return {
      ...base, "index.html": html(nombre, "main.js", "app"), "src/main.js": MAIN_SVELTE, "src/App.svelte": APP_SVELTE, "src/lib/Contador.svelte": CONTADOR_SVELTE,
      "src/app.css": CSS_BASE + APP_CSS.replace("#root", "#app"),
      "vite.config.js": "import { defineConfig } from 'vite'\nimport { svelte } from '@sveltejs/vite-plugin-svelte'\n\nexport default defineConfig({\n  plugins: [svelte()],\n})\n",
    };
  }
  return {
    ...base, "index.html": html(nombre, `main.${ts ? "ts" : "js"}`, "app"),
    [`src/main.${ts ? "ts" : "js"}`]: MAIN_VANILLA(ts), [`src/counter.${ts ? "ts" : "js"}`]: COUNTER(ts), "src/style.css": CSS_BASE + APP_CSS.replace("#root", "#app"),
    ...(ts ? { "tsconfig.json": TSCONFIG(null) } : {}),
  };
}
