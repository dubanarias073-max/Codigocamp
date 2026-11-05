// Logos de los lenguajes (SVG propios y estilizados, sin depender de internet).
// logo("python", 40) devuelve el <svg> listo para insertar.
const hex = (c, t, fs = 20) => `<polygon points="24,3 42,13.5 42,34.5 24,45 6,34.5 6,13.5" fill="${c}"/><text x="24" y="${fs > 16 ? 31 : 29}" text-anchor="middle" font-size="${fs}" font-weight="800" fill="#fff" font-family="Inter,Arial,sans-serif">${t}</text>`;
const cuadro = (c, t, tc) => `<rect x="4" y="4" width="40" height="40" rx="5" fill="${c}"/><text x="43" y="42" text-anchor="end" font-size="17" font-weight="800" fill="${tc}" font-family="Inter,Arial,sans-serif">${t}</text>`;
const bd = (c, extra = "") => `<ellipse cx="24" cy="11" rx="16" ry="6" fill="${c}"/><path d="M8 11v8c0 3.3 7.2 6 16 6s16-2.7 16-6v-8c0 3.3-7.2 6-16 6S8 14.300 8 11z" fill="${c}" opacity=".85"/><path d="M8 21v8c0 3.3 7.2 6 16 6s16-2.7 16-6v-8c0 3.3-7.2 6-16 6S8 24.300 8 21z" fill="${c}" opacity=".7"/><path d="M8 31v6c0 3.3 7.2 6 16 6s16-2.7 16-6v-6c0 3.3-7.2 6-16 6S8 34.300 8 31z" fill="${c}" opacity=".55"/>${extra}`;

export const LOGOS = {
  html: `<path d="M6 4l3.800 38L24 46l14.200-4L42 4z" fill="#e44d26"/><path d="M24 8v34.600l11.300-3.200L38.600 8z" fill="#f16529"/><text x="24" y="30" text-anchor="middle" font-size="20" font-weight="800" fill="#fff" font-family="Inter,Arial,sans-serif">5</text>`,
  css: `<path d="M6 4l3.800 38L24 46l14.200-4L42 4z" fill="#264de4"/><path d="M24 8v34.600l11.300-3.200L38.600 8z" fill="#2965f1"/><text x="24" y="30" text-anchor="middle" font-size="20" font-weight="800" fill="#fff" font-family="Inter,Arial,sans-serif">3</text>`,
  javascript: cuadro("#f7df1e", "JS", "#111"),
  typescript: cuadro("#3178c6", "TS", "#fff"),
  python: `<rect x="7" y="5" width="23" height="20" rx="9" fill="#3776ab"/><rect x="18" y="23" width="23" height="20" rx="9" fill="#ffd43b"/><rect x="7" y="17" width="16" height="12" fill="#3776ab"/><rect x="25" y="19" width="16" height="12" fill="#ffd43b"/><circle cx="16" cy="13" r="2.200" fill="#fff"/><circle cx="32" cy="35" r="2.200" fill="#1e1e1e"/>`,
  sql: bd("#f472b6", `<text x="24" y="31" text-anchor="middle" font-size="10" font-weight="800" fill="#fff" font-family="Inter,Arial,sans-serif">SQL</text>`),
  bd: bd("#f472b6"),
  java: `<path d="M11 22h21v9a9 9 0 0 1-9 9h-3a9 9 0 0 1-9-9z" fill="#5382a1"/><path d="M32 25h2.500a4.500 4.500 0 0 1 0 9H31" fill="none" stroke="#5382a1" stroke-width="3"/><path d="M9 44h25" stroke="#e76f00" stroke-width="3" stroke-linecap="round"/><path d="M17 6c-4 4 3 6 0 11M25 6c-4 4 3 6 0 11" fill="none" stroke="#e76f00" stroke-width="2.600" stroke-linecap="round"/>`,
  c: hex("#00599c", "C", 22),
  cpp: hex("#00599c", "C++", 15),
  csharp: hex("#9b4f96", "C#", 19),
  go: `<rect x="3" y="12" width="42" height="24" rx="12" fill="#00add8"/><text x="24" y="30" text-anchor="middle" font-size="16" font-weight="800" font-style="italic" fill="#fff" font-family="Inter,Arial,sans-serif">GO</text>`,
  rust: `<circle cx="24" cy="24" r="19" fill="none" stroke="#f74c00" stroke-width="5" stroke-dasharray="2.500 2.470"/><circle cx="24" cy="24" r="14" fill="none" stroke="#f74c00" stroke-width="5"/><text x="24" y="30" text-anchor="middle" font-size="16" font-weight="800" fill="#f74c00" font-family="Inter,Arial,sans-serif">R</text>`,
  swift: `<defs><linearGradient id="lgSw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffac45"/><stop offset="1" stop-color="#f05138"/></linearGradient></defs><rect x="3" y="3" width="42" height="42" rx="10" fill="url(#lgSw)"/><path d="M13 32c5 3 12 3 17-1 3-2 6-5 8-9-4 3-8 4-12 2 5-3 9-8 10-14-6 5-13 10-19 9z" fill="#fff"/>`,
  kotlin: `<defs><linearGradient id="lgKt" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#e44857"/><stop offset=".5" stop-color="#c711e1"/><stop offset="1" stop-color="#7f52ff"/></linearGradient></defs><polygon points="6,6 42,6 24,24 42,42 6,42" fill="url(#lgKt)"/>`,
  php: `<ellipse cx="24" cy="24" rx="21" ry="13" fill="#777bb3"/><text x="24" y="29" text-anchor="middle" font-size="13" font-weight="800" fill="#0f1224" font-family="Inter,Arial,sans-serif">php</text>`,
  ruby: `<polygon points="14,7 34,7 43,18 24,43 5,18" fill="#cc342d"/><polygon points="14,7 24,18 34,7" fill="#fff" opacity=".35"/><polygon points="5,18 24,18 24,43" fill="#000" opacity=".18"/><polygon points="5,18 14,7 24,18" fill="#fff" opacity=".18"/>`,
};

const NOMBRES = { html: "HTML", css: "CSS", javascript: "JS", typescript: "TS", python: "PY", sql: "SQL", bd: "BD", java: "JV", c: "C", cpp: "C++", csharp: "C#", go: "GO", rust: "RS", swift: "SW", kotlin: "KT", php: "PHP", ruby: "RB" };

export function logo(slug, tam = 40) {
  const dentro = LOGOS[slug];
  return dentro
    ? `<svg class="logo-l" viewBox="0 0 48 48" width="${tam}" height="${tam}" role="img" aria-label="Logo de ${slug}">${dentro}</svg>`
    : `<span class="logo-l logo-sigla" style="width:${tam}px;height:${tam}px">${NOMBRES[slug] || slug.slice(0, 2).toUpperCase()}</span>`;
}
