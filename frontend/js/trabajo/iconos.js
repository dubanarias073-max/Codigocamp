// Iconos de archivo y carpeta (insignias de color, al estilo de los temas de VS Code).
import { extension, nombreBase } from "./fs.js";

const POR_EXT = {
  html: ["‹›", "html"], htm: ["‹›", "html"], css: ["#", "css"], scss: ["#", "css"], js: ["JS", "js"], mjs: ["JS", "js"], cjs: ["JS", "js"], jsx: ["⚛", "ts"],
  ts: ["TS", "ts"], tsx: ["⚛", "ts"], json: ["{}", "json"], py: ["Py", "py"], md: ["M↓", "md"], java: ["J", "java"], c: ["C", "c"], h: ["H", "c"],
  cpp: ["C+", "c"], cc: ["C+", "c"], cs: ["C#", "cs"], go: ["Go", "go"], rs: ["Rs", "rs"], php: ["php", "php"], rb: ["Rb", "rb"], sql: ["SQL", "sql"],
  sh: ["$", "sh"], bash: ["$", "sh"], lua: ["Lua", "py"], pl: ["Pl", "c"], r: ["R", "py"], scala: ["Sc", "kt"], hs: ["Hs", "kt"], exs: ["Ex", "rb"], ex: ["Ex", "rb"], jl: ["Jl", "py"], groovy: ["Gy", "kt"], cr: ["Cr", "rb"], nim: ["Nim", "py"], ml: ["ML", "kt"], d: ["D", "c"], pas: ["Pas", "c"], zig: ["Zig", "c"], lisp: ["λ", "kt"], swift: ["Sw", "rs"], kt: ["Kt", "kt"], svg: ["◇", "img"], png: ["▣", "img"], jpg: ["▣", "img"], jpeg: ["▣", "img"], gif: ["▣", "img"], webp: ["▣", "img"], avif: ["▣", "img"], bmp: ["▣", "img"], ico: ["▣", "img"], mp4: ["▶", "media"], webm: ["▶", "media"], mov: ["▶", "media"], mp3: ["♪", "media"], wav: ["♪", "media"], ogg: ["♪", "media"], m4a: ["♪", "media"], pdf: ["PDF", "pdf"], docx: ["W", "word"], doc: ["W", "word"], odt: ["W", "word"], rtf: ["W", "word"], xlsx: ["X", "excel"], xlsm: ["X", "excel"], xls: ["X", "excel"], ods: ["X", "excel"], pptx: ["P", "ppt"], ppt: ["P", "ppt"], odp: ["P", "ppt"], zip: ["ZIP", "bin"], ttf: ["Aa", "bin"], otf: ["Aa", "bin"], woff: ["Aa", "bin"], woff2: ["Aa", "bin"], exe: ["bin", "bin"], yml: ["!", "sh"], yaml: ["!", "sh"], txt: ["≡", "txt"], gitignore: ["◆", "git"], env: ["⚙", "git"],
};

export function iconoArchivo(ruta) {
  const base = nombreBase(ruta).toLowerCase();
  const docker = base === "dockerfile" || base === ".dockerignore" || /^(docker-)?compose\.ya?ml$/.test(base);
  const [texto, clase] = docker ? ["🐳", "docker"] : POR_EXT[extension(ruta)] ?? (base === ".gitignore" ? ["◆", "git"] : ["≡", "txt"]);
  return `<span class="fi fi-${clase}" aria-hidden="true">${texto}</span>`;
}

export const iconoCarpeta = (abierta) => abierta
  ? '<svg class="fi-carpeta" viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 4.5v8.2c0 .4.3.8.8.8h10.9l1.8-5.7H5.2L3.6 12.6M1.5 4.5V3.3c0-.4.3-.8.8-.8h3.4l1.2 1.6h5.6c.4 0 .8.3.8.8v1.6" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>'
  : '<svg class="fi-carpeta" viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 3.3c0-.4.3-.8.8-.8h3.4l1.2 1.6h6.3c.4 0 .8.3.8.8v7.8c0 .4-.3.8-.8.8H2.3c-.5 0-.8-.4-.8-.8z" fill="currentColor" fill-opacity=".25" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>';

export const chevron = '<svg class="chev" viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3.5L10.5 8 6 12.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>';
