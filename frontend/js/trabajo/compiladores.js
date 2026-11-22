// Componentes .vue y .svelte en la vista previa (lo que hacen @vitejs/plugin-vue y vite-plugin-svelte en «npm run dev»).
// Se compilan en el navegador con el compilador oficial de la MISMA versión de tu package.json (desde esm.sh, la primera
// vez; luego queda en caché). El resultado es un módulo ES normal que sigue el camino del resto de archivos.

const cache = new Map();   // url del compilador → promesa del módulo
const cargar = (url) => { if (!cache.has(url)) cache.set(url, import(/* @vite-ignore */ url).catch((e) => { cache.delete(url); throw e; })); return cache.get(url); };
const version = (deps, nombre, respaldo) => { const v = String(deps[nombre] ?? "").replace(/^[\^~=v]/, ""); return /^\d+(\.\d+){0,2}/.test(v) ? v : respaldo; };

/** id corto y estable por archivo (para los estilos «scoped» de Vue). */
export function idDe(ruta) {
  let h = 5381;
  for (let i = 0; i < ruta.length; i++) h = ((h << 5) + h + ruta.charCodeAt(i)) >>> 0;
  return h.toString(16).padStart(8, "0").slice(0, 8);
}

const inyectarCss = (css, ruta) => css ? `\n;(() => { const s = document.createElement("style"); s.dataset.archivo = ${JSON.stringify(ruta)}; s.textContent = ${JSON.stringify(css)}; document.head.appendChild(s); })();\n` : "";

/**
 * .vue → JS. Soporta <script setup>, <script>, <template>, <style> y <style scoped>, y lang="ts".
 * @param {string} texto  @param {string} ruta  @param {object} deps  @param {(codigo, ruta)=>Promise<string>} transpilar
 */
export async function compilarVue(texto, ruta, deps, transpilar, { compilador } = {}) {
  const sfc = compilador ?? await cargar(`https://esm.sh/@vue/compiler-sfc@${version(deps, "vue", "3.5.17")}`);
  const { descriptor, errors } = sfc.parse(texto, { filename: ruta, sourceMap: false });
  if (errors?.length) throw new Error(errors.map((e) => e.message || String(e)).join("\n"));
  const id = idDe(ruta);
  const scoped = descriptor.styles.some((s) => s.scoped);
  const ts = (descriptor.scriptSetup || descriptor.script)?.lang === "ts";
  let codigo;
  if (descriptor.script || descriptor.scriptSetup) {
    const s = sfc.compileScript(descriptor, { id, inlineTemplate: !!descriptor.scriptSetup, isProd: false, sourceMap: false,
      templateOptions: { compilerOptions: { scopeId: scoped ? `data-v-${id}` : undefined } } });
    codigo = sfc.rewriteDefault(s.content, "__sfc__", ts ? ["typescript"] : []);
    if (!descriptor.scriptSetup && descriptor.template) codigo += plantillaVue(sfc, descriptor, id, scoped, ruta);
  } else {
    codigo = "const __sfc__ = {};\n" + (descriptor.template ? plantillaVue(sfc, descriptor, id, scoped, ruta) : "");
  }
  if (scoped) codigo += `\n__sfc__.__scopeId = "data-v-${id}";`;
  codigo += `\n__sfc__.__file = ${JSON.stringify(ruta)};\nexport default __sfc__;\n`;
  if (ts) codigo = await transpilar(codigo, ruta.replace(/\.vue$/, ".ts"));
  const css = descriptor.styles.map((st) => {
    const r = sfc.compileStyle({ source: st.content, filename: ruta, id: `data-v-${id}`, scoped: st.scoped });
    if (r.errors?.length) throw new Error(r.errors.map((e) => e.message || String(e)).join("\n"));
    return r.code;
  }).join("\n");
  return codigo + inyectarCss(css, ruta);
}

function plantillaVue(sfc, descriptor, id, scoped, ruta) {
  const t = sfc.compileTemplate({ source: descriptor.template.content, filename: ruta, id, scoped, compilerOptions: { scopeId: scoped ? `data-v-${id}` : undefined } });
  if (t.errors?.length) throw new Error(t.errors.map((e) => e.message || String(e)).join("\n"));
  return "\n" + t.code.replace(/export function render/, "function render") + "\n__sfc__.render = render;";
}

/** .svelte → JS (Svelte 5; también Svelte 4). El CSS del componente se inyecta en la página. */
export async function compilarSvelte(texto, ruta, deps, { compilador } = {}) {
  const v = version(deps, "svelte", "5.34.0");
  const svelte = compilador ?? await cargar(`https://esm.sh/svelte@${v}/compiler`);
  const r = svelte.compile(texto, { filename: ruta, generate: Number(v.split(".")[0]) >= 5 ? "client" : "dom", css: "injected", dev: false });
  for (const w of r.warnings || []) console.warn(`${ruta}: ${w.message}`);
  return r.js.code;
}
