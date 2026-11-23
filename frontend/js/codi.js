/* Codi, la mascota de CódigoCamp.
   Un pequeño robot compañero: cabeza con visor de cristal (sus ojos son luz), orejas en forma de llaves { },
   antena que se vuelve llama cuando tienes racha y sudadera con el emblema </>.
   Ánimos: feliz, fuego, preocupado, alarma, dormido, saludo, pensando, triste, celebra.
   codiSVG(animo, { tam, animado, titulo }) devuelve el <svg> listo para insertar. */

let n = 0;

const COLOR_OJOS = { fuego: "#d4ff5a", alarma: "#ff5a6e", triste: "#7aa7ff", dormido: "#5ef2ff", celebra: "#d4ff5a" };
const FRASES = {
  feliz: ["¡Bien hecho! Tu racha está a salvo", "¡Hoy cumpliste! Nos vemos mañana", "¡Qué crack! Ya practicaste hoy"],
  fuego: ["¡Estás en llamas!", "¡Racha imparable! Sigue así", "Nadie te para"],
  preocupado: ["¿Practicamos un ratito hoy?", "Tu racha te está esperando", "5 minutos y listo, ¿vamos?"],
  alarma: ["¡Tu racha está en peligro!", "¡Corre! Se acaba el día", "¡No dejes que se apague tu racha!"],
  dormido: ["Zzz… despiértame con una lección", "Empieza una racha hoy", "¿Hoy empezamos? Yo te acompaño"],
  saludo: ["¡Hola! Soy Codi", "¡Qué bueno verte!", "¿Listo para programar?"],
  pensando: ["Déjame pensar…", "Analizando tu código…", "Mmm, interesante…"],
  triste: ["Se apagó la racha… ¡empecemos otra!", "Mañana volvemos con todo", "Toda racha empieza con un día"],
  celebra: ["¡Lo lograste!", "¡Nivel superado!", "¡Eso es todo!"],
};
export const ANIMOS = Object.keys(FRASES);
export function fraseDe(animo, semilla = Math.floor(Date.now() / 600000)) {
  const l = FRASES[animo] || FRASES.feliz;
  return l[semilla % l.length];
}

function ojos(a, id, c) {
  const brillo = (x, y) => `<circle cx="${x}" cy="${y}" r="2.2" fill="#fff" opacity=".85"/>`;
  switch (a) {
    case "feliz": case "celebra":
      return `<g class="cdx-ojos" stroke="${c}" stroke-width="6.5" stroke-linecap="round" fill="none" filter="url(#${id}b)">
        <path d="M70 96q10-14 20 0"/><path d="M110 96q10-14 20 0"/></g>`;
    case "fuego":
      return `<g class="cdx-ojos cdx-parpadeo" fill="${c}" filter="url(#${id}b)">
        <path d="M70 84l20 5v14a6 6 0 0 1-6 6h-8a6 6 0 0 1-6-6z"/><path d="M130 84l-20 5v14a6 6 0 0 0 6 6h8a6 6 0 0 0 6-6z"/></g>
        ${brillo(76, 93)}${brillo(116, 93)}`;
    case "preocupado":
      return `<g stroke="${c}" stroke-width="3.5" stroke-linecap="round" opacity=".9"><path d="M70 76l16 5"/><path d="M130 76l-16 5"/></g>
        <g class="cdx-ojos cdx-parpadeo" fill="${c}" filter="url(#${id}b)"><rect x="73" y="86" width="14" height="18" rx="7"/><rect x="113" y="86" width="14" height="18" rx="7"/></g>
        ${brillo(78, 91)}${brillo(118, 91)}`;
    case "alarma":
      return `<g class="cdx-ojos" fill="${c}" filter="url(#${id}b)"><circle cx="80" cy="91" r="12"/><circle cx="120" cy="91" r="12"/></g>
        <circle cx="80" cy="91" r="4.5" fill="#1a0510"/><circle cx="120" cy="91" r="4.5" fill="#1a0510"/>${brillo(84, 86)}${brillo(124, 86)}`;
    case "dormido":
      return `<g class="cdx-ojos" stroke="${c}" stroke-width="5" stroke-linecap="round" fill="none" opacity=".75" filter="url(#${id}b)">
        <path d="M70 92q10 8 20 0"/><path d="M110 92q10 8 20 0"/></g>`;
    case "triste":
      return `<g stroke="${c}" stroke-width="3.5" stroke-linecap="round" opacity=".85"><path d="M71 80l15-5"/><path d="M129 80l-15-5"/></g>
        <g class="cdx-ojos cdx-parpadeo" fill="${c}" filter="url(#${id}b)"><rect x="73" y="86" width="14" height="16" rx="7"/><rect x="113" y="86" width="14" height="16" rx="7"/></g>
        <path class="cdx-lagrima" d="M84 104c3 5 4 7 4 9a4 4 0 0 1-8 0c0-2 1-4 4-9z" fill="#7aa7ff"/>`;
    case "pensando":
      return `<g class="cdx-ojos cdx-parpadeo" fill="${c}" filter="url(#${id}b)"><rect x="80" y="80" width="14" height="20" rx="7"/><rect x="118" y="80" width="14" height="20" rx="7"/></g>
        ${brillo(86, 85)}${brillo(124, 85)}`;
    default: // feliz neutro / saludo
      return `<g class="cdx-ojos cdx-parpadeo" fill="${c}" filter="url(#${id}b)"><rect x="73" y="80" width="15" height="23" rx="7.5"/><rect x="112" y="80" width="15" height="23" rx="7.5"/></g>
        ${brillo(79, 86)}${brillo(118, 86)}`;
  }
}

function boca(a, c) {
  const s = `stroke="${c}" stroke-width="4" stroke-linecap="round" fill="none"`;
  return {
    feliz: `<path d="M90 109q10 8 20 0" ${s}/>`, saludo: `<path d="M90 109q10 8 20 0" ${s}/>`,
    fuego: `<path d="M88 107q12 12 24 0z" fill="${c}"/>`, celebra: `<path d="M86 106q14 15 28 0z" fill="${c}"/>`,
    preocupado: `<path d="M90 112q5-4 10 0t10 0" ${s}/>`, triste: `<path d="M91 113q9-7 18 0" ${s}/>`,
    alarma: `<ellipse cx="100" cy="112" rx="6" ry="7" fill="${c}"/>`, pensando: `<path d="M93 111h12" ${s}/>`,
    dormido: `<path d="M95 111q5 3 10 0" ${s} opacity=".7"/>`,
  }[a] ?? `<path d="M90 109q10 8 20 0" ${s}/>`;
}

function antena(a, id) {
  const llama = a === "fuego" || a === "celebra" || a === "feliz" || a === "alarma";
  const tallo = `<path d="M100 42V24" stroke="url(#${id}borde)" stroke-width="4" stroke-linecap="round"/>`;
  if (!llama) {
    const c = a === "dormido" ? "#3a5a7a" : a === "triste" ? "#5a7ab0" : "#5ef2ff";
    return `${tallo}<circle class="${a === "dormido" ? "" : "cdx-pulso"}" cx="100" cy="20" r="7" fill="${c}" filter="url(#${id}b)"/><circle cx="98" cy="18" r="2" fill="#fff" opacity=".7"/>`;
  }
  const grande = a === "fuego" || a === "celebra";
  const t = grande ? "translate(100 26) scale(1.35) translate(-100 -26)" : "";
  return `${tallo}<g class="cdx-llama" transform="${t}">
    <path d="M100 2c7 8 12 13 9 21-2 5-6 7-9 7s-8-2-10-7c-2-6 2-10 4-13 1 3 2 5 4 5-2-4-1-8 2-13z" fill="url(#${id}llama)" filter="url(#${id}b)"/>
    <path d="M100 14c3 4 5 6 4 10-1 2-3 3-4 3s-4-1-4-3c-1-3 1-5 2-7 0 2 1 2 2 2-1-2 0-3 0-5z" fill="#fff6b0"/></g>`;
}

function extras(a, id) {
  return {
    dormido: `<g class="cdx-z" fill="#9fd8ff" font-family="system-ui,sans-serif" font-weight="900"><text x="150" y="44" font-size="18">z</text><text x="164" y="26" font-size="13">z</text></g>`,
    preocupado: `<path class="cdx-gota" d="M160 58c4 7 6 10 6 13a6 6 0 0 1-12 0c0-3 2-6 6-13z" fill="#7fd6ff" opacity=".9"/>`,
    alarma: `<g class="cdx-alerta"><circle cx="164" cy="40" r="14" fill="#ff5a6e"/><rect x="161.5" y="30" width="5" height="13" rx="2.5" fill="#fff"/><circle cx="164" cy="48" r="2.8" fill="#fff"/></g>`,
    fuego: `<g class="cdx-chispas" fill="#d4ff5a"><path d="M30 40l2 6 6 2-6 2-2 6-2-6-6-2 6-2z"/><path d="M168 64l1.5 4.5 4.5 1.5-4.5 1.5-1.5 4.5-1.5-4.5-4.5-1.5 4.5-1.5z"/></g>`,
    celebra: `<g class="cdx-chispas"><path d="M28 36l2.5 7 7 2.5-7 2.5-2.5 7-2.5-7-7-2.5 7-2.5z" fill="#d4ff5a"/><path d="M170 30l2 5.5 5.5 2-5.5 2-2 5.5-2-5.5-5.5-2 5.5-2z" fill="#5ef2ff"/>
      </g>
      <g class="cdx-confeti"><rect x="40" y="10" width="6" height="10" rx="2" fill="#ff7ac6"/><rect x="152" y="16" width="6" height="10" rx="2" fill="#ffd34e"/>
      <circle cx="70" cy="6" r="3.5" fill="#5ef2ff"/><rect x="128" y="4" width="5" height="9" rx="2" fill="#b8ff3c"/><circle cx="20" cy="30" r="3" fill="#ffd34e"/><rect x="178" y="40" width="5" height="9" rx="2" fill="#ff7ac6"/></g>`,
    feliz: `<path class="cdx-chispas" d="M166 36l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" fill="#d4ff5a"/>`,
    pensando: `<g class="cdx-puntos" fill="#5ef2ff"><circle cx="150" cy="40" r="4"/><circle cx="162" cy="30" r="5"/><circle cx="176" cy="18" r="6"/></g>`,
    saludo: "",
    triste: "",
  }[a] ?? "";
}


// ------------------------------------------------------------------ accesorios (tienda → «Accesorios de Codi») ----
// capa: atras (detrás del cuerpo), cuello, cabeza, cara o frente (encima de todo). sinAntena: la tapa (gorros grandes).
export const ACCESORIOS_CODI = {
  // De temporada (no se venden: Codi se los pone solo en Halloween, etc., si no llevas otro accesorio)
  temp_bruja: { capa: "cabeza", sinAntena: true, svg: `<ellipse cx="100" cy="50" rx="68" ry="12" fill="#1e1b4b" stroke="#0f0a2e" stroke-width="3"/><path d="M62 48Q84 34 96-14Q112 6 108 20Q124 30 138 48Z" fill="#312e81" stroke="#0f0a2e" stroke-width="3" stroke-linejoin="round"/><path d="M66 44q34 8 68 0" stroke="#f97316" stroke-width="7" fill="none"/><rect x="92" y="38" width="14" height="12" rx="2" fill="#facc15" stroke="#a16207" stroke-width="2"/>` },
  temp_calabaza: { capa: "cabeza", svg: `<g transform="translate(150 40)"><ellipse rx="16" ry="13" fill="#f97316" stroke="#9a3412" stroke-width="2.5"/><path d="M-6-12q6 10 0 24M6-12q-6 10 0 24" stroke="#9a3412" stroke-width="2" fill="none"/><path d="M0-12q2-8 8-9" stroke="#15803d" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M-8-2l4 3-4 2zM8-2l-4 3 4 2zM-7 6q7 5 14 0" fill="#451a03" stroke="#451a03" stroke-width="1.5"/></g>` },
  codi_alas: { capa: "atras", svg: `<g class="cdx-alas" shape-rendering="crispEdges"><path d="M64 140H46V130H32V120H20V106H10V90H2V66H14V80H24V94H36V108H50V120H64Z" fill="#e0f2fe" stroke="#0284c7" stroke-width="3" stroke-linejoin="miter"/><path d="M136 140 H154 V130 H168 V120 H180 V106 H190 V90 H198 V66 H186 V80 H176 V94 H164 V108 H150 V120 H136 Z" fill="#e0f2fe" stroke="#0284c7" stroke-width="3" stroke-linejoin="miter"/><path d="M14 80v18M24 94v16M36 108v14M50 120v12" stroke="#7dd3fc" stroke-width="3"/><path d="M186 80 v18 M176 94 v16 M164 108 v14 M150 120 v12" stroke="#7dd3fc" stroke-width="3"/><path d="M2 66h12v4H2zM186 66h12v4h-12z" fill="#fde047"/></g>` },
  codi_kart: { capa: "frente", svg: `<g class="cdx-llama"><path d="M18 178q-14-4-16 6q10-2 16 2z" fill="#f97316"/><path d="M18 184q-12 2-12 10q8-6 14-6z" fill="#fde047"/></g><path d="M20 172q4-18 30-20h100q26 2 32 20l4 14H16z" fill="#ef4444" stroke="#7f1d1d" stroke-width="3" stroke-linejoin="round"/><path d="M40 160h120" stroke="#fff" stroke-opacity=".35" stroke-width="4" stroke-linecap="round"/><path d="M26 182h148v16H26z" fill="#991b1b" stroke="#7f1d1d" stroke-width="2"/><rect x="84" y="164" width="32" height="14" rx="4" fill="#fde047" stroke="#a16207" stroke-width="2"/><text x="100" y="175" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" font-weight="900" fill="#7f1d1d">01</text><g fill="#111827" stroke="#475569" stroke-width="3"><circle cx="46" cy="188" r="12"/><circle cx="154" cy="188" r="12"/></g><g fill="#94a3b8"><circle cx="46" cy="188" r="4"/><circle cx="154" cy="188" r="4"/></g><path d="M172 150v18" stroke="#334155" stroke-width="4"/><rect x="164" y="144" width="22" height="8" rx="3" fill="#1f2937"/>` },
  codi_explorador: { capa: "cabeza", sinAntena: true, svg: `<ellipse cx="100" cy="52" rx="72" ry="13" fill="#d6b77a" stroke="#78501f" stroke-width="3"/><path d="M52 50C52 6 148 6 148 50Z" fill="#e9cf96" stroke="#78501f" stroke-width="3"/><path d="M54 42q46 10 92 0" stroke="#3f6212" stroke-width="7" fill="none"/><path d="M84 16q16-8 32 0" stroke="#fff" stroke-opacity=".4" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M128 40q12-16 26-10q-12 2-18 14z" fill="#22c55e" stroke="#166534" stroke-width="2"/>` },
  codi_banda_ninja: { capa: "cabeza", svg: `<rect x="38" y="54" width="124" height="14" rx="5" fill="#dc2626" stroke="#7f1d1d" stroke-width="2.5"/><rect x="92" y="55" width="16" height="12" rx="2" fill="#cbd5e1" stroke="#475569" stroke-width="2"/><path d="M160 60q20 4 30 18q-14-4-26-6zM160 64q14 12 18 30q-10-12-20-20z" fill="#dc2626" stroke="#7f1d1d" stroke-width="2" stroke-linejoin="round"/>` },
  codi_carreras: { capa: "cabeza", sinAntena: true, svg: `<path d="M40 74C36 4 164 4 160 74L148 72C148 30 52 30 52 72Z" fill="#f8fafc" stroke="#1e293b" stroke-width="3"/><path d="M62 22q38-16 76 0l-6 10q-32-12-64 0z" fill="#ef4444"/><path d="M98 10h4v60h-4z" fill="#1e293b" opacity=".7"/><text x="100" y="52" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="900" fill="#ef4444" stroke="#1e293b" stroke-width="1">01</text>` },
  codi_escudo: { capa: "frente", svg: (a) => {
    // escudo en la mano izquierda y espada en la derecha; siguen a los brazos cuando saluda, celebra o piensa
    const izq = a === "celebra" ? [-19, -52] : a === "pensando" ? [34, -38] : [0, 0];
    const der = a === "saludo" || a === "celebra" ? [19, -52] : [0, 0];
    return `<g transform="translate(${der[0]} ${der[1]})"><path d="M154 158h8v-56l-4-9-4 9z" fill="#e2e8f0" stroke="#334155" stroke-width="2" stroke-linejoin="round"/><path d="M158 154v-50" stroke="#94a3b8" stroke-width="1.6"/><rect x="145" y="157" width="26" height="7" rx="3" fill="#facc15" stroke="#a16207" stroke-width="2"/><rect x="155" y="164" width="6" height="16" rx="2" fill="#7c2d12" stroke="#451a03" stroke-width="1.5"/><circle cx="158" cy="183" r="4.5" fill="#facc15" stroke="#a16207" stroke-width="1.5"/></g>`
      + `<g transform="translate(${izq[0]} ${izq[1]})"><path d="M18 150h40v18q0 20-20 28q-20-8-20-28z" fill="#1d4ed8" stroke="#facc15" stroke-width="3.5" stroke-linejoin="round"/><path d="M24 156h28v12q0 14-14 20q-14-6-14-20z" fill="#2563eb"/><text x="38" y="176" text-anchor="middle" font-family="ui-monospace,monospace" font-size="13" font-weight="900" fill="#fde047">{ }</text></g>`;
  } },
  codi_jefe_final: { capa: "cabeza", sinAntena: true, svg: `<path d="M54 50L46 6L72 30L86 0L100 24L114 0L128 30L154 6L146 50Z" fill="#1e1b4b" stroke="#a855f7" stroke-width="3" stroke-linejoin="round"/><rect x="54" y="42" width="92" height="12" rx="4" fill="#312e81" stroke="#a855f7" stroke-width="3"/><g fill="#f43f5e"><circle cx="100" cy="48" r="5"/><circle cx="76" cy="48" r="3.5"/><circle cx="124" cy="48" r="3.5"/></g><path d="M86 0L100 24 114 0" fill="none" stroke="#f0abfc" stroke-width="1.5" opacity=".6"/>` },
  codi_minero: { capa: "cabeza", sinAntena: true, svg: `<path d="M148 34L200 8V62Z" fill="#fde047" fill-opacity=".45"/><path d="M46 60C46 12 154 12 154 60Z" fill="#f59e0b" stroke="#92400e" stroke-width="3"/><path d="M100 14v44M70 22l6 34M130 22l-6 34" stroke="#b45309" stroke-width="4"/><rect x="40" y="50" width="120" height="14" rx="7" fill="#d97706" stroke="#92400e" stroke-width="2.5"/><circle cx="138" cy="34" r="11" fill="#fef9c3" stroke="#92400e" stroke-width="3"/><circle cx="138" cy="34" r="5" fill="#fff"/>` },
  codi_caballero: { capa: "cabeza", sinAntena: true, svg: `<path d="M100 18q14-24 34-14q-14 4-22 18z" fill="#ef4444" stroke="#7f1d1d" stroke-width="2.5"/><g shape-rendering="crispEdges"><path d="M48 62V34h8v-8h8v-8h72v8h8v8h8v28z" fill="#cbd5e1" stroke="#334155" stroke-width="3"/><path d="M60 34h80v6H60z" fill="#94a3b8"/><path d="M96 18h8v44h-8z" fill="#e2e8f0"/></g><g fill="#475569"><circle cx="58" cy="54" r="3"/><circle cx="142" cy="54" r="3"/></g>` },
  codi_vr: { capa: "cara", svg: `<path d="M38 88h124" stroke="#1f2937" stroke-width="8" stroke-linecap="round"/><rect x="56" y="74" width="88" height="36" rx="12" fill="#111827" stroke="#a855f7" stroke-width="3"/><rect x="62" y="80" width="76" height="24" rx="8" fill="url(#vrGrad)"/><defs><linearGradient id="vrGrad" x1="0" x2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#f472b6"/></linearGradient></defs><path d="M68 86h20" stroke="#fff" stroke-opacity=".7" stroke-width="3" stroke-linecap="round"/>` },
  codi_jetpack: { capa: "atras", svg: `<rect x="40" y="126" width="26" height="46" rx="9" fill="#64748b" stroke="#1e293b" stroke-width="3"/><rect x="134" y="126" width="26" height="46" rx="9" fill="#64748b" stroke="#1e293b" stroke-width="3"/><rect x="44" y="132" width="18" height="8" rx="3" fill="#ef4444"/><rect x="138" y="132" width="18" height="8" rx="3" fill="#ef4444"/><g class="cdx-llama"><path d="M44 172q9 26 9 30q0-4 9-30z" fill="#f97316"/><path d="M48 172q5 14 5 18q0-4 5-18z" fill="#fde047"/><path d="M138 172q9 26 9 30q0-4 9-30z" fill="#f97316"/><path d="M142 172q5 14 5 18q0-4 5-18z" fill="#fde047"/></g>` },
  codi_control: { capa: "frente", svg: `<rect x="66" y="148" width="68" height="30" rx="14" fill="#312e81" stroke="#c7d2fe" stroke-width="2.5"/><path d="M80 157v12M74 163h12" stroke="#e0e7ff" stroke-width="4" stroke-linecap="round"/><circle cx="114" cy="159" r="4" fill="#f43f5e"/><circle cx="123" cy="166" r="4" fill="#22c55e"/><circle cx="105" cy="166" r="3" fill="#facc15"/>` },
  codi_gorra: { capa: "cabeza", sinAntena: true, svg: `<path d="M46 58C46 8 154 8 154 58Z" fill="#ef4444" stroke="#7f1d1d" stroke-width="3"/><path d="M60 40q40-20 80 0" stroke="#fff" stroke-opacity=".25" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M150 50q34-4 44 12q-26 6-48-1z" fill="#b91c1c" stroke="#7f1d1d" stroke-width="3" stroke-linejoin="round"/><circle cx="100" cy="14" r="5" fill="#7f1d1d"/><text x="100" y="44" text-anchor="middle" font-family="ui-monospace,monospace" font-size="15" font-weight="900" fill="#fff">&lt;/&gt;</text>` },
  codi_gorro_lana: { capa: "cabeza", sinAntena: true, svg: `<path d="M48 60C48 10 152 10 152 60Z" fill="#14b8a6" stroke="#115e59" stroke-width="3"/><path d="M64 38h72M58 48h84M74 28h52" stroke="#5eead4" stroke-width="4" stroke-linecap="round"/><rect x="42" y="48" width="116" height="18" rx="9" fill="#0f766e" stroke="#115e59" stroke-width="3"/><path d="M52 52v10M64 52v10M76 52v10M88 52v10M100 52v10M112 52v10M124 52v10M136 52v10M148 52v10" stroke="#2dd4bf" stroke-width="3"/><circle cx="100" cy="12" r="11" fill="#f0fdfa" stroke="#5eead4" stroke-width="3"/>` },
  codi_navidad: { capa: "cabeza", sinAntena: true, svg: `<path d="M48 54Q58 4 116 8Q156 12 176 66L162 72Q150 34 122 30Q144 42 152 54Z" fill="#dc2626" stroke="#7f1d1d" stroke-width="3" stroke-linejoin="round"/><path d="M70 30q24-14 50-12" stroke="#fff" stroke-opacity=".25" stroke-width="5" fill="none" stroke-linecap="round"/><rect x="40" y="46" width="120" height="18" rx="9" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/><circle cx="170" cy="72" r="11" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>` },
  codi_pirata: { capa: "cabeza", sinAntena: true, svg: `<path d="M30 56Q56 26 100 30Q144 26 170 56Q150 2 100 4Q50 2 30 56Z" fill="#111827" stroke="#facc15" stroke-width="3" stroke-linejoin="round"/><circle cx="100" cy="28" r="9" fill="#f8fafc"/><circle cx="96.5" cy="27" r="2.2" fill="#111827"/><circle cx="103.5" cy="27" r="2.2" fill="#111827"/><path d="M88 42l24-6M88 36l24 6" stroke="#f8fafc" stroke-width="3.5" stroke-linecap="round"/>` },
  codi_vikingo: { capa: "cabeza", sinAntena: true, svg: `<path d="M56 40Q30 38 24 4Q42 26 62 30Z" fill="#fef3c7" stroke="#a16207" stroke-width="3" stroke-linejoin="round"/><path d="M144 40Q170 38 176 4Q158 26 138 30Z" fill="#fef3c7" stroke="#a16207" stroke-width="3" stroke-linejoin="round"/><path d="M46 60C46 12 154 12 154 60Z" fill="#94a3b8" stroke="#334155" stroke-width="3"/><path d="M100 14v44" stroke="#64748b" stroke-width="6"/><rect x="42" y="50" width="116" height="14" rx="7" fill="#a16207" stroke="#713f12" stroke-width="2.5"/><g fill="#fde68a"><circle cx="58" cy="57" r="2.6"/><circle cx="80" cy="57" r="2.6"/><circle cx="120" cy="57" r="2.6"/><circle cx="142" cy="57" r="2.6"/></g>` },
  codi_mago: { capa: "cabeza", sinAntena: true, svg: `<ellipse cx="100" cy="48" rx="66" ry="12" fill="#4c1d95" stroke="#2e1065" stroke-width="3"/><path d="M60 46Q86 30 102-22Q116 22 140 46Z" fill="#6d28d9" stroke="#2e1065" stroke-width="3" stroke-linejoin="round"/><path d="M68 44q32 8 66 0" stroke="#facc15" stroke-width="5" fill="none"/><g fill="#fde047"><path d="M96 10l2.5 6 6 2.5-6 2.5-2.5 6-2.5-6-6-2.5 6-2.5z"/><path d="M114 28l1.8 4.4 4.4 1.8-4.4 1.8-1.8 4.4-1.8-4.4-4.4-1.8 4.4-1.8z"/><circle cx="84" cy="32" r="2.4"/></g>` },
  codi_corona: { capa: "cabeza", sinAntena: true, svg: `<path d="M60 48L58 14L80 30L100 4L120 30L142 14L140 48Z" fill="#facc15" stroke="#a16207" stroke-width="3" stroke-linejoin="round"/><rect x="58" y="40" width="84" height="12" rx="4" fill="#eab308" stroke="#a16207" stroke-width="3"/><circle cx="100" cy="46" r="5" fill="#ef4444"/><circle cx="78" cy="46" r="4" fill="#22d3ee"/><circle cx="122" cy="46" r="4" fill="#22c55e"/><circle cx="58" cy="14" r="4" fill="#fef9c3"/><circle cx="100" cy="4" r="4.5" fill="#fef9c3"/><circle cx="142" cy="14" r="4" fill="#fef9c3"/>` },
  codi_birrete: { capa: "cabeza", sinAntena: true, svg: `<path d="M66 40v16q34 12 68 0V40" fill="#1f2937" stroke="#030712" stroke-width="3"/><path d="M100 12L170 32L100 52L30 32Z" fill="#111827" stroke="#030712" stroke-width="3" stroke-linejoin="round"/><circle cx="100" cy="32" r="4" fill="#facc15"/><path d="M100 32L154 40V66" stroke="#facc15" stroke-width="3" fill="none"/><path d="M148 64h12l-2 14h-8z" fill="#facc15"/>` },
  codi_halo: { capa: "cabeza", sinAntena: true, svg: `<ellipse cx="100" cy="22" rx="36" ry="9" fill="none" stroke="#fde047" stroke-width="6"/><ellipse cx="100" cy="22" rx="36" ry="9" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2"/><ellipse cx="100" cy="22" rx="44" ry="14" fill="none" stroke="#fde047" stroke-opacity=".25" stroke-width="8"/>` },
  codi_audifonos: { capa: "cabeza", svg: `<path d="M30 84C30 8 170 8 170 84" stroke="#111827" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M32 70C40 20 160 20 168 70" stroke="#f472b6" stroke-width="3" fill="none" stroke-linecap="round"/><rect x="14" y="66" width="28" height="48" rx="13" fill="#1f2937" stroke="#f472b6" stroke-width="3"/><rect x="158" y="66" width="28" height="48" rx="13" fill="#1f2937" stroke="#f472b6" stroke-width="3"/><circle cx="28" cy="90" r="5" fill="#f472b6"/><circle cx="172" cy="90" r="5" fill="#f472b6"/>` },
  codi_flor: { capa: "cabeza", svg: `<g transform="translate(144 42)"><g fill="#f9a8d4" stroke="#db2777" stroke-width="1.5"><circle cx="0" cy="-10" r="8"/><circle cx="9.5" cy="-3" r="8"/><circle cx="6" cy="8" r="8"/><circle cx="-6" cy="8" r="8"/><circle cx="-9.5" cy="-3" r="8"/></g><circle r="6" fill="#facc15" stroke="#ca8a04" stroke-width="1.5"/></g>` },
  codi_gafas: { capa: "cara", svg: `<g shape-rendering="crispEdges"><path d="M50 82h100v6H50zM62 82h32v20h-6v4H68v-4h-6zM106 82h32v20h-6v4h-20v-4h-6z" fill="none" stroke="#e2e8f0" stroke-width="5" stroke-linejoin="miter"/><path d="M50 82h100v6H50z" fill="#030712"/><path d="M62 82h32v20h-6v4H68v-4h-6z" fill="#030712"/><path d="M106 82h32v20h-6v4h-20v-4h-6z" fill="#030712"/><path d="M68 86h6v4h-6zM74 90h6v4h-6zM112 86h6v4h-6zM118 90h6v4h-6z" fill="#fff" opacity=".85"/></g>` },
  codi_bigote: { capa: "cara", svg: `<path d="M100 104c-6-7-19-10-28 0-4 4-10 3-12-1 1 9 13 12 22 9 8-2 12-6 18-6s10 4 18 6c9 3 21 0 22-9-2 4-8 5-12 1-9-10-22-7-28 0z" fill="#78350f" stroke="#451a03" stroke-width="1.5"/>` },
  codi_bufanda: { capa: "cuello", svg: `<rect x="56" y="130" width="88" height="16" rx="8" fill="#ef4444" stroke="#7f1d1d" stroke-width="2.5"/><path d="M76 131v14M96 131v14M116 131v14M136 131v14" stroke="#fde68a" stroke-width="4"/><path d="M118 142l6 34 14-3-4-32z" fill="#ef4444" stroke="#7f1d1d" stroke-width="2.5" stroke-linejoin="round"/><path d="M121 156l13-2M123 166l13-2" stroke="#fde68a" stroke-width="4"/>` },
  codi_corbatin: { capa: "cuello", svg: `<path d="M100 144L76 132v24zM100 144l24-12v24z" fill="#a855f7" stroke="#581c87" stroke-width="2.5" stroke-linejoin="round"/><rect x="93" y="137" width="14" height="14" rx="4" fill="#c084fc" stroke="#581c87" stroke-width="2.5"/>` },
  codi_capa: { capa: "atras", svg: `<path d="M64 136Q36 162 34 190Q50 182 64 190Q82 180 100 190Q118 180 136 190Q150 182 166 190Q164 162 136 136Z" fill="#dc2626" stroke="#7f1d1d" stroke-width="3" stroke-linejoin="round"/><path d="M70 150Q54 172 56 194" stroke="#fff" stroke-opacity=".2" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="66" cy="140" r="6" fill="#facc15" stroke="#a16207" stroke-width="2"/><circle cx="134" cy="140" r="6" fill="#facc15" stroke="#a16207" stroke-width="2"/>` },
  codi_astronauta: { capa: "frente", svg: `<circle cx="100" cy="88" r="84" fill="#7dd3fc" fill-opacity=".1" stroke="#e0f2fe" stroke-opacity=".85" stroke-width="4"/><path d="M40 52q20-34 60-38" stroke="#fff" stroke-opacity=".7" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M44 70q4-8 10-12" stroke="#fff" stroke-opacity=".5" stroke-width="4" fill="none" stroke-linecap="round"/><ellipse cx="100" cy="146" rx="46" ry="9" fill="#e2e8f0" stroke="#64748b" stroke-width="3"/>` },
};
let accesorioTemporada = null;
/** Accesorio que Codi se pone solo en una temporada (Navidad, Halloween…) cuando no llevas ninguno. */
export function ponerAccesorioTemporada(clave) {
  accesorioTemporada = ACCESORIOS_CODI[clave] ? clave : null;
  if (!accesorioPuesto) redibujarCodis();
}
let accesorioPuesto = (() => { try { return JSON.parse(localStorage.getItem("cc_cosm") || "{}").codi || null; } catch { return null; } })();
/** Cambia el accesorio de Codi y redibuja los Codi que ya están en la página. */
export function ponerAccesorioCodi(clave) {
  const nuevo = ACCESORIOS_CODI[clave] ? clave : null;
  if (nuevo === accesorioPuesto) return;
  accesorioPuesto = nuevo;
  redibujarCodis();
}
function redibujarCodis() {
  if (typeof document === "undefined") return;
  for (const svg of document.querySelectorAll("svg.codi:not([data-fijo])")) {
    const animo = [...svg.classList].find((c) => c.startsWith("codi-") && c !== "codi-animado")?.slice(5) || "feliz";
    const tam = Number(svg.getAttribute("width")) || null;
    svg.outerHTML = codiSVG(animo, { tam, animado: svg.classList.contains("codi-animado"), titulo: svg.getAttribute("aria-label") || undefined });
  }
}
const capaAcc = (acc, capa, a) => (acc && acc.capa === capa ? `<g class="cdx-acc cdx-acc-${capa}">${typeof acc.svg === "function" ? acc.svg(a) : acc.svg}</g>` : "");

/** El SVG de Codi. tam en px (o null para que llene su contenedor). accesorio: clave de ACCESORIOS_CODI (por defecto el que tiene puesto). */
export function codiSVG(animo = "feliz", { tam = 96, animado = true, titulo = "Codi, la mascota de CódigoCamp", accesorio } = {}) {
  const a = FRASES[animo] ? animo : "feliz";
  const acc = ACCESORIOS_CODI[accesorio === undefined ? (accesorioPuesto || accesorioTemporada) : accesorio] || null;
  const id = `cdx${++n}`;
  const c = COLOR_OJOS[a] || "#5ef2ff";
  const visor = a === "alarma" ? ["#2a0a16", "#140611"] : ["#08142a", "#040a18"];
  const brazoDer = a === "saludo" || a === "celebra"
    ? `<g class="cdx-saluda"><path d="M140 156c18-2 30-14 36-34" stroke="url(#${id}cuerpo)" stroke-width="15" stroke-linecap="round" fill="none"/><path d="M140 156c18-2 30-14 36-34" stroke="#5ef2ff" stroke-opacity=".35" stroke-width="2" fill="none"/><circle cx="177" cy="118" r="10" fill="#2b4170" stroke="#5ef2ff" stroke-width="2"/></g>`
    : `<path d="M145 148c9 4 13 12 13 20" stroke="url(#${id}cuerpo)" stroke-width="14" stroke-linecap="round" fill="none"/><circle cx="158" cy="170" r="8" fill="#2b4170" stroke="#5ef2ff" stroke-width="2" stroke-opacity=".6"/>`;
  const brazoIzq = a === "celebra"
    ? `<g><path d="M60 156c-18-2-30-14-36-34" stroke="url(#${id}cuerpo)" stroke-width="15" stroke-linecap="round" fill="none"/><path d="M60 156c-18-2-30-14-36-34" stroke="#5ef2ff" stroke-opacity=".35" stroke-width="2" fill="none"/><circle cx="23" cy="118" r="10" fill="#2b4170" stroke="#5ef2ff" stroke-width="2"/></g>`
    : a === "pensando"
      ? `<path d="M62 160c-14-4-10-22 10-26" stroke="url(#${id}cuerpo)" stroke-width="14" stroke-linecap="round" fill="none"/><path d="M62 160c-14-4-10-22 10-26" stroke="#5ef2ff" stroke-opacity=".35" stroke-width="2" fill="none"/><circle cx="76" cy="132" r="9" fill="#2b4170" stroke="#5ef2ff" stroke-width="2"/>`
      : `<path d="M55 148c-9 4-13 12-13 20" stroke="url(#${id}cuerpo)" stroke-width="14" stroke-linecap="round" fill="none"/><circle cx="42" cy="170" r="8" fill="#2b4170" stroke="#5ef2ff" stroke-width="2" stroke-opacity=".6"/>`;
  const arriba = a === "saludo" || a === "celebra" || a === "pensando";
  const tamAttr = tam ? `width="${tam}" height="${tam}"` : "";
  return `<svg class="codi codi-${a}${animado ? " codi-animado" : ""}" viewBox="0 0 200 200" ${tamAttr} role="img" aria-label="${titulo}" xmlns="http://www.w3.org/2000/svg">
  <title>${titulo}</title>
  <defs>
    <linearGradient id="${id}cab" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f4677"/><stop offset=".55" stop-color="#1b2b52"/><stop offset="1" stop-color="#111b36"/></linearGradient>
    <linearGradient id="${id}cuerpo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#25395f"/><stop offset="1" stop-color="#121d3a"/></linearGradient>
    <linearGradient id="${id}borde" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5ef2ff"/><stop offset="1" stop-color="#b8ff3c"/></linearGradient>
    <linearGradient id="${id}visor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${visor[0]}"/><stop offset="1" stop-color="${visor[1]}"/></linearGradient>
    <linearGradient id="${id}llama" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ff4d2e"/><stop offset=".55" stop-color="#ff9d1c"/><stop offset="1" stop-color="#ffe25a"/></linearGradient>
    <radialGradient id="${id}aura" cx=".5" cy=".55" r=".5"><stop offset="0" stop-color="${c}" stop-opacity=".22"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient>
    <filter id="${id}b" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <style>
    .codi-animado{overflow:visible;animation:cdxEntra .6s cubic-bezier(.3,1.7,.55,1) both}
    .codi-animado .cdx-todo{transform-box:view-box;transform-origin:100px 190px}
    .codi-feliz.codi-animado .cdx-todo{animation:cdxFeliz 4.2s ease-in-out infinite}
    .codi-saludo.codi-animado .cdx-todo{animation:cdxFeliz 4.2s ease-in-out infinite}
    .codi-celebra.codi-animado .cdx-todo{animation:cdxSalto .95s cubic-bezier(.3,.7,.4,1) infinite}
    .codi-fuego.codi-animado .cdx-todo{animation:cdxSalto 1.5s cubic-bezier(.3,.7,.4,1) infinite}
    .codi-alarma.codi-animado .cdx-todo{animation:cdxPanico .9s ease-in-out infinite}
    .codi-triste.codi-animado .cdx-todo{animation:cdxTriste 3.4s ease-in-out infinite}
    .codi-pensando.codi-animado .cdx-todo{animation:cdxPiensa 3.2s ease-in-out infinite}
    .codi-dormido.codi-animado .cdx-todo{animation:cdxRespira 4s ease-in-out infinite}
    .codi-preocupado.codi-animado .cdx-todo{animation:cdxFlota 3.2s ease-in-out infinite}
    .codi-preocupado.codi-animado .cdx-ojos{transform-box:view-box;animation:cdxMira 3.6s ease-in-out infinite}
    .codi-animado .cdx-parpadeo{transform-box:fill-box;transform-origin:center;animation:cdxParpadea 4.6s infinite}
    .codi-preocupado.codi-animado .cdx-parpadeo{animation:cdxParpadea 4.6s infinite,cdxMira 3.6s ease-in-out infinite}
    .codi-animado .cdx-llama{transform-box:fill-box;transform-origin:50% 100%;animation:cdxLlama .5s ease-in-out infinite alternate}
    .codi-animado .cdx-alas{transform-box:fill-box;transform-origin:50% 90%;animation:cdxAlas .55s ease-in-out infinite alternate}
    @keyframes cdxAlas{to{transform:scaleY(.78) translateY(4px)}}
    .codi-animado .cdx-pulso{animation:cdxPulso 2.4s ease-in-out infinite}
    .codi-animado .cdx-saluda{transform-box:view-box;transform-origin:140px 156px;animation:cdxSaluda .7s ease-in-out infinite}
    .codi-animado .cdx-z text{animation:cdxZ 2.6s ease-in-out infinite}
    .codi-animado .cdx-z text+text{animation-delay:.6s}
    .codi-animado .cdx-gota,.codi-animado .cdx-lagrima{animation:cdxGota 2.2s ease-in infinite}
    .codi-animado .cdx-alerta{transform-box:fill-box;transform-origin:center;animation:cdxSaltaAlerta .45s ease-in-out infinite alternate}
    .codi-animado .cdx-chispas{animation:cdxBrilla 1.2s ease-in-out infinite}
    .codi-animado .cdx-leds circle{animation:cdxBrilla 1.1s steps(2) infinite}.codi-animado .cdx-leds circle:nth-child(2n){animation-delay:.55s}
    .codi-animado .cdx-puntos circle{animation:cdxBrilla 1.4s ease-in-out infinite}
    .codi-animado .cdx-puntos circle+circle{animation-delay:.25s}.codi-animado .cdx-puntos circle+circle+circle{animation-delay:.5s}
    .codi-animado .cdx-confeti rect,.codi-animado .cdx-confeti circle{transform-box:fill-box;transform-origin:center;animation:cdxConfeti 1.6s ease-in infinite}
    .codi-animado .cdx-confeti :nth-child(2){animation-delay:.3s}.codi-animado .cdx-confeti :nth-child(3){animation-delay:.6s}
    .codi-animado .cdx-confeti :nth-child(4){animation-delay:.9s}.codi-animado .cdx-confeti :nth-child(5){animation-delay:1.2s}
    .codi-animado .cdx-confeti :nth-child(6){animation-delay:.45s}
    a:hover>.codi-animado .cdx-todo,a:hover .codi-animado .cdx-todo,.codi-animado:hover .cdx-todo,.codi-animado.cdx-saltar .cdx-todo{animation:cdxSalto .7s cubic-bezier(.3,.7,.4,1)}
    @keyframes cdxEntra{0%{transform:scale(.3) translateY(30px);opacity:0}60%{opacity:1}100%{transform:none}}
    @keyframes cdxFlota{50%{transform:translateY(-4px)}}
    @keyframes cdxFeliz{0%,62%,100%{transform:translateY(0) scale(1)}20%,45%{transform:translateY(-3px)}
      70%{transform:translateY(0) scale(1.1,.88)}78%{transform:translateY(-20px) scale(.93,1.08)}86%{transform:translateY(-22px) scale(1)}
      93%{transform:translateY(0) scale(1.07,.93)}97%{transform:scale(.98,1.02)}}
    @keyframes cdxSalto{0%{transform:translateY(0) scale(1,1)}14%{transform:translateY(0) scale(1.12,.86)}34%{transform:translateY(-26px) scale(.92,1.1)}
      52%{transform:translateY(-30px) scale(1,1) rotate(-4deg)}72%{transform:translateY(0) scale(1.1,.9) rotate(0)}86%{transform:scale(.96,1.04)}100%{transform:scale(1)}}
    @keyframes cdxPanico{0%,100%{transform:translate(0,0) rotate(0)}10%{transform:translate(-3px,0) rotate(-4deg)}20%{transform:translate(3px,0) rotate(4deg)}
      30%{transform:translate(-3px,0) rotate(-4deg)}40%{transform:translate(0,0) scale(1.08,.9)}55%{transform:translateY(-14px) scale(.95,1.06)}70%{transform:translateY(0) scale(1.06,.94)}}
    @keyframes cdxTriste{0%,100%{transform:translateY(2px) rotate(-2deg) scale(1,.98)}50%{transform:translateY(5px) rotate(-5deg) scale(1.02,.95)}}
    @keyframes cdxPiensa{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg) translateY(-2px)}}
    @keyframes cdxRespira{0%,100%{transform:scale(1,1)}50%{transform:scale(1.03,.96)}}
    @keyframes cdxMira{0%,20%,100%{transform:translateX(0)}30%,45%{transform:translateX(-5px)}55%,70%{transform:translateX(5px)}}
    @keyframes cdxParpadea{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.12)}}
    @keyframes cdxLlama{from{transform:scale(1) rotate(-4deg)}to{transform:scale(1.1,1.18) rotate(4deg)}}
    @keyframes cdxPulso{50%{opacity:.55}}
    @keyframes cdxSaluda{0%,100%{transform:rotate(0)}50%{transform:rotate(-18deg)}}
    @keyframes cdxZ{0%{opacity:0;transform:translate(0,6px)}40%{opacity:1}100%{opacity:0;transform:translate(6px,-8px)}}
    @keyframes cdxGota{0%{opacity:0;transform:translateY(-4px)}30%{opacity:1}100%{opacity:0;transform:translateY(10px)}}
    @keyframes cdxSaltaAlerta{from{transform:scale(1) rotate(-8deg)}to{transform:scale(1.18) rotate(8deg)}}
    @keyframes cdxBrilla{50%{opacity:.25}}
    @keyframes cdxConfeti{0%{transform:translateY(-10px) rotate(0);opacity:0}15%{opacity:1}100%{transform:translateY(70px) rotate(300deg);opacity:0}}
    @media (prefers-reduced-motion:reduce){.codi-animado,.codi-animado *{animation:none!important}}
  </style>
  <ellipse cx="100" cy="190" rx="50" ry="7" fill="#000" opacity=".28"/>
  <circle cx="100" cy="100" r="96" fill="url(#${id}aura)"/>
  ${extras(a, id)}
  <g class="cdx-todo">
    ${capaAcc(acc, "atras", a)}
    <!-- cuerpo con sudadera -->
    <rect x="76" y="180" width="18" height="11" rx="5.5" fill="#0d1530" stroke="#5ef2ff" stroke-opacity=".5" stroke-width="2"/>
    <rect x="106" y="180" width="18" height="11" rx="5.5" fill="#0d1530" stroke="#5ef2ff" stroke-opacity=".5" stroke-width="2"/>
    ${arriba ? "" : brazoIzq + brazoDer}
    <!-- torso: base de datos (cilindro con discos, como el logo) -->
    <path d="M62 140v38a38 10 0 0 0 76 0v-38" fill="url(#${id}cuerpo)" stroke="url(#${id}borde)" stroke-width="2.5"/>
    <path d="M62 153a38 10 0 0 0 76 0M62 166a38 10 0 0 0 76 0" fill="none" stroke="url(#${id}borde)" stroke-width="2" stroke-opacity=".75"/>
    <path d="M66 158a34 8 0 0 0 68 0" fill="none" stroke="#fff" stroke-opacity=".08" stroke-width="5"/>
    <ellipse cx="100" cy="140" rx="38" ry="10" fill="#2f4677" stroke="url(#${id}borde)" stroke-width="2.5"/>
    <g class="cdx-leds"><circle cx="72" cy="161" r="2.4" fill="#b8ff3c"/><circle cx="128" cy="161" r="2.4" fill="#5ef2ff"/>
      <circle cx="72" cy="174" r="2.4" fill="#5ef2ff"/><circle cx="128" cy="174" r="2.4" fill="#b8ff3c"/></g>
    <text x="100" y="179" text-anchor="middle" font-family="ui-monospace,Consolas,monospace" font-size="11" font-weight="900" fill="#b8ff3c">&lt;/&gt;</text>

    ${capaAcc(acc, "cuello", a)}
    <!-- antena -->
    ${acc?.sinAntena ? "" : antena(a, id)}
    <!-- orejas { } -->
    <g stroke="url(#${id}borde)" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round" fill="none" filter="url(#${id}b)">
      <path d="M36 58q-10 0-10 11v10q0 9-9 11 9 2 9 11v10q0 11 10 11"/>
      <path d="M164 58q10 0 10 11v10q0 9 9 11-9 2-9 11v10q0 11-10 11"/>
    </g>
    <!-- cabeza -->
    <rect x="38" y="40" width="124" height="98" rx="42" fill="url(#${id}cab)" stroke="url(#${id}borde)" stroke-width="3"/>
    <path d="M60 50q40-10 80 0" stroke="#fff" stroke-opacity=".18" stroke-width="5" stroke-linecap="round" fill="none"/>
    <!-- visor -->
    <rect x="52" y="62" width="96" height="62" rx="28" fill="url(#${id}visor)" stroke="#000" stroke-opacity=".4" stroke-width="2"/>
    <rect x="52" y="62" width="96" height="62" rx="28" fill="none" stroke="${c}" stroke-opacity=".28" stroke-width="1.5"/>
    <g class="cdx-mirada">${ojos(a, id, c)}</g>
    ${boca(a, c)}
    <ellipse cx="66" cy="112" rx="7" ry="3.5" fill="#ff7aa8" opacity="${a === "alarma" || a === "dormido" ? 0 : .35}"/>
    <ellipse cx="134" cy="112" rx="7" ry="3.5" fill="#ff7aa8" opacity="${a === "alarma" || a === "dormido" ? 0 : .35}"/>
    <path d="M64 70q12-6 26-6" stroke="#fff" stroke-opacity=".22" stroke-width="4" stroke-linecap="round" fill="none"/>
    ${capaAcc(acc, "cara", a)}
    ${capaAcc(acc, "cabeza", a)}
    ${arriba ? brazoIzq + brazoDer : ""}
    ${capaAcc(acc, "frente", a)}
  </g>
</svg>`;
}

/** Hace saltar a un Codi ya dibujado (por ejemplo al acertar). */
export function saltarCodi(raiz) {
  const svg = raiz?.matches?.(".codi") ? raiz : raiz?.querySelector?.(".codi");
  if (!svg) return;
  svg.classList.remove("cdx-saltar");
  void svg.getBoundingClientRect();
  svg.classList.add("cdx-saltar");
  setTimeout(() => svg.classList.remove("cdx-saltar"), 750);
}
