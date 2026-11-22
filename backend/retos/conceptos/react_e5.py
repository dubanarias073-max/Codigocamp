"""React · Etapa 5: React profesional."""
from ..generador import K

LISTA = [
K("React con TypeScript",
  d="escribir componentes en archivos .tsx con tipos para props y estado",
  u="detectar errores de props y datos antes de ejecutar la app",
  mas="Con Vite eliges la plantilla react-ts. Los componentes van en .tsx y las props se describen con un type o interface. TypeScript avisa si olvidas una prop o pasas un tipo equivocado.",
  k=["Los componentes con TypeScript van en archivos .tsx.", "Las props se describen con un type o una interface.", "TypeScript avisa si falta una prop obligatoria."],
  sit="En tu equipo pasan props con el tipo equivocado y los errores aparecen recién en el navegador. ¿Qué usarías?",
  cod="""type SaludoProps = { nombre: string; edad?: number };   // edad es opcional

function Saludo({ nombre, edad }: SaludoProps) {
  return <p>Hola {nombre}{edad ? `, tienes ${edad}` : ""}</p>;
}

function App() {
  return <Saludo nombre="Ana" edad={17} />;   // <Saludo /> daría error de tipos
}""",
  h="tipa las props de un componente con TypeScript",
  pr=("Los componentes de React con TypeScript van en archivos .___ (3 letras)", "tsx"),
  ec="usar any en todas las props y perder la ayuda de TypeScript"),
K("Tipar el estado y los eventos",
  d="indicar a TypeScript qué guarda useState y qué evento recibe cada manejador",
  u="evitar errores con datos que pueden ser null o con e.target",
  mas="useState<Usuario | null>(null) dice que el estado será un Usuario o null. Los eventos tienen tipos como React.ChangeEvent<HTMLInputElement> para que e.target.value sea texto.",
  k=["useState<Tipo>() indica qué guarda el estado.", "React.ChangeEvent<HTMLInputElement> tipa el evento de un input.", "Un estado que empieza vacío suele tiparse como Tipo | null."],
  sit="Tu estado empieza en null y luego guarda un usuario, y TypeScript se queja al leer usuario.nombre. ¿Qué usarías?",
  cod="""import { useState, type ChangeEvent } from "react";

type Usuario = { nombre: string };

function App() {
  const [usuario, setUsuario] = useState<Usuario | null>(null);   // Usuario o null
  const cambiar = (e: ChangeEvent<HTMLInputElement>) => setUsuario({ nombre: e.target.value });
  return <div><input onChange={cambiar} placeholder="Nombre" /><p>{usuario?.nombre ?? "Sin nombre"}</p></div>;
}""",
  h="tipa un estado que puede ser null y el evento de un input",
  pr=("El tipo del evento de un input es React.___Event (6 letras)", "change"),
  ec="olvidar que el estado puede ser null y leer sus propiedades sin revisar"),
K("Vitest",
  d="herramienta de pruebas rápida que funciona con Vite",
  u="comprobar automáticamente que tus funciones y componentes funcionan",
  mas="Vitest usa la misma configuración de Vite. Las pruebas van en archivos .test.jsx con describe, it/test y expect. npx vitest las ejecuta y se repiten al guardar.",
  k=["Vitest ejecuta pruebas en proyectos de Vite.", "Las pruebas usan test y expect.", "Los archivos de prueba suelen terminar en .test.jsx."],
  sit="Cada vez que cambias algo rompes sin querer otra parte, y quieres pruebas automáticas que corran al guardar. ¿Qué usarías?",
  cod="""// suma.test.js
//   import { test, expect } from "vitest";
//   test("suma 2 + 3", () => expect(suma(2, 3)).toBe(5));
const suma = (a, b) => a + b;

function App() {
  const ok = suma(2, 3) === 5;           // lo que comprobaría la prueba
  return <p>{ok ? "✅ La prueba pasaría" : "❌ Fallaría"}</p>;
}""",
  h="muestra si una prueba de suma pasaría",
  pr=("En una prueba, el valor se compara con expect(valor).to___(esperado) (2 letras)", "be"),
  ec="probar solo a mano en el navegador cada vez"),
K("React Testing Library",
  d="biblioteca para probar componentes como los usaría una persona",
  u="verificar que se ve el texto correcto y que los botones funcionan",
  mas="render dibuja el componente en la prueba y screen busca elementos por su texto o rol, como getByRole('button'). userEvent simula clics y escritura. Se prueba lo que ve la persona, no los detalles internos.",
  k=["React Testing Library prueba componentes como una persona los usa.", "screen.getByRole busca elementos por su rol.", "userEvent simula clics y escritura en las pruebas."],
  sit="Quieres una prueba que haga clic en «Sumar» y compruebe que aparece «Clics: 1». ¿Qué usarías?",
  cod="""// test("suma al hacer clic", async () => {
//   render(<Contador />);
//   await userEvent.click(screen.getByRole("button", { name: /sumar/i }));
//   expect(screen.getByText("Clics: 1")).toBeInTheDocument();
// });
import { useState } from "react";

function App() {
  const [n, setN] = useState(0);
  return <button onClick={() => setN(n + 1)}>Sumar · Clics: {n}</button>;
}""",
  h="muestra el componente que se probaría con Testing Library",
  pr=("En Testing Library, para buscar un botón se usa getBy___ (4 letras)", "role"),
  ec="probar detalles internos del componente en lugar de lo que ve la persona"),
K("Zustand",
  d="biblioteca pequeña para manejar estado global con un hook",
  u="compartir el carrito o la sesión entre páginas sin Context complicado",
  mas="create crea un store con datos y funciones. Cada componente usa el hook del store y solo se vuelve a dibujar si cambia la parte que lee. Es más simple que Redux y no necesita Provider.",
  k=["Zustand crea un estado global con la función create.", "Zustand no necesita envolver la app en un Provider.", "Con Zustand se lee el store con un hook."],
  sit="Tu app tiene muchos Contexts anidados para el carrito, el usuario y el tema, y quieres algo más simple. ¿Qué usarías?",
  cod="""import { create } from "zustand";

const useCarrito = create((set) => ({
  items: [],
  agregar: (x) => set((s) => ({ items: [...s.items, x] })),
}));

function Boton() { const agregar = useCarrito((s) => s.agregar); return <button onClick={() => agregar("🍔")}>Agregar</button>; }
function Total() { const items = useCarrito((s) => s.items); return <p>{items.length} productos {items.join("")}</p>; }

function App() {
  return <><Boton /><Total /></>;   // sin Provider
}""",
  h="comparte un carrito entre dos componentes con Zustand",
  pr=("En Zustand, el store se crea con la función ___ (6 letras)", "create"),
  ec="guardar en un store global datos que solo usa un componente"),
K("TanStack Query",
  d="biblioteca que pide, guarda en caché y actualiza datos del servidor",
  u="no repetir peticiones y tener carga, error y reintentos listos",
  mas="useQuery({ queryKey, queryFn }) devuelve data, isLoading y error. Los datos quedan en caché: si otro componente pide la misma clave, no se vuelve a pedir. Necesita un QueryClientProvider arriba.",
  k=["TanStack Query guarda en caché los datos del servidor.", "useQuery devuelve data, isLoading y error.", "Cada consulta se identifica con una queryKey."],
  sit="Varias páginas piden los mismos productos a la API y quieres caché, reintentos y estado de carga sin escribirlos tú. ¿Qué usarías?",
  cod="""import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";

const cliente = new QueryClient();

function Usuario() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["usuario", 1],
    queryFn: () => fetch("https://jsonplaceholder.typicode.com/users/1").then((r) => r.json()),
  });
  if (isLoading) return <p>Cargando…</p>;
  if (error) return <p>Error</p>;
  return <p>👤 {data.name}</p>;
}

function App() {
  return <QueryClientProvider client={cliente}><Usuario /></QueryClientProvider>;
}""",
  h="trae un usuario con useQuery y lo guarda en caché",
  pr=("Cada consulta de TanStack Query se identifica con una query___ (3 letras)", "key"),
  ec="olvidar el QueryClientProvider alrededor de la app"),
K("Next.js",
  d="framework de React con rutas por archivos y renderizado en el servidor",
  u="hacer sitios rápidos y fáciles de encontrar en Google",
  mas="En Next.js cada carpeta de app/ es una ruta y page.jsx su página. Puede dibujar en el servidor, generar páginas estáticas y tener rutas de API en el mismo proyecto. Se crea con npx create-next-app.",
  k=["En Next.js las rutas se crean con carpetas y archivos.", "Next.js puede dibujar las páginas en el servidor.", "Un proyecto de Next.js se crea con npx create-next-app."],
  sit="Tu tienda en React necesita que Google indexe bien cada producto y que las páginas abran rápido. ¿Qué framework usarías?",
  cod="""// app/page.jsx      -> ruta /
// app/blog/page.jsx -> ruta /blog
// npx create-next-app@latest mi-sitio
export default function App() {
  return <h1>Página de inicio de Next.js</h1>;
}""",
  h="muestra la página principal de un proyecto de Next.js",
  pr=("En Next.js, el archivo de cada página dentro de app/ se llama ___.jsx (4 letras)", "page"),
  ec="confundir Next.js con una biblioteca distinta de React"),
K("Server Components",
  d="componentes que se ejecutan solo en el servidor y envían HTML listo",
  u="leer la base de datos directamente y enviar menos JavaScript",
  mas="En Next.js los componentes son de servidor por defecto: pueden ser async y consultar datos sin useEffect. Los que usan estado o eventos llevan 'use client' al inicio del archivo.",
  k=["Los Server Components se ejecutan en el servidor.", "Un Server Component puede ser una función async.", "'use client' marca un componente que corre en el navegador."],
  sit="En Next.js quieres leer los productos de la base de datos dentro del componente sin useEffect ni API intermedia. ¿Qué usarías?",
  cod="""// app/productos/page.jsx (Server Component)
//   export default async function Productos() {
//     const productos = await db.producto.findMany();
//     return <ul>{productos.map(p => <li key={p.id}>{p.nombre}</li>)}</ul>;
//   }
// Un componente con useState lleva al inicio: "use client";
function App() {
  return <p>Los Server Components corren en el servidor 🖥️</p>;
}""",
  h="explica cómo sería un componente de servidor en Next.js",
  pr=("La directiva que marca un componente del navegador es \"use ___\" (6 letras)", "client"),
  ec="usar useState en un Server Component sin \"use client\""),
K("Build para producción",
  d="generar archivos optimizados de la app con npm run build",
  u="publicar la app en un servidor o hosting",
  mas="npm run build crea la carpeta dist con HTML, CSS y JS minificados. npm run preview la sirve para probarla. Esos archivos se suben a Netlify, Vercel, GitHub Pages o tu servidor.",
  k=["npm run build genera la versión de producción.", "Vite deja la app lista en la carpeta dist.", "npm run preview sirve el build para probarlo."],
  sit="Tu app ya funciona con npm run dev y ahora quieres los archivos optimizados para publicarla. ¿Qué comando usarías?",
  cod="""// npm run build    -> crea dist/ (minificado)
// npm run preview  -> prueba el resultado
function App() {
  return <p>Lista para producción 🚀 (los archivos quedan en dist/)</p>;
}""",
  h="indica dónde queda el resultado del build",
  pr=("Vite deja los archivos de producción en la carpeta ___ (4 letras)", "dist"),
  ec="subir la carpeta src al hosting en lugar de dist"),
K("Desplegar la app",
  d="publicar la app en internet con un servicio de hosting",
  u="que cualquiera pueda abrir tu proyecto con un enlace",
  mas="Servicios como Vercel y Netlify se conectan con tu repositorio de GitHub y publican cada cambio. En apps con React Router hay que redirigir todas las rutas a index.html para que /perfil no dé 404 al recargar.",
  k=["Vercel y Netlify publican apps de React desde GitHub.", "Cada push puede publicar una versión nueva.", "Las apps con rutas necesitan redirigir todo a index.html."],
  sit="Terminaste tu portafolio en React y quieres compartir un enlace que se actualice solo al hacer push. ¿Qué harías?",
  cod="""// netlify.toml (para que las rutas no den 404 al recargar):
// [[redirects]]
//   from = "/*"
//   to = "/index.html"
//   status = 200
function App() {
  return <p>🌍 Publicado en internet</p>;
}""",
  h="muestra la regla para que las rutas funcionen al publicar",
  pr=("Las rutas de una app de una sola página se redirigen todas a ___.html (5 letras)", "index"),
  ec="publicar una app con rutas sin redirigir todo a index.html y ver 404 al recargar"),
K("Accesibilidad en React",
  d="hacer componentes que puedan usar personas con lectores de pantalla o teclado",
  u="que todas las personas puedan usar tu app",
  mas="Usa etiquetas con significado (button, nav, label), textos alternativos en imágenes, aria-label en botones con solo íconos y que todo funcione con Tab y Enter. Un div con onClick no sirve con el teclado.",
  k=["Los botones deben ser <button>, no divs con onClick.", "aria-label describe un botón que solo tiene un ícono.", "Toda la app debería poder usarse con el teclado."],
  sit="Una persona que navega solo con teclado no puede usar tu menú hecho con divs. ¿Qué mejorarías?",
  cod="""function App() {
  return (
    <nav aria-label="Principal">
      <button aria-label="Cerrar menú">✖</button>      {/* botón real con nombre */}
      <img src="https://picsum.photos/40" alt="Foto de perfil de Ana" />
      <label htmlFor="q">Buscar</label> <input id="q" />
    </nav>
  );
}""",
  h="usa etiquetas accesibles con nombres claros",
  pr=("Para dar nombre a un botón que solo tiene un ícono se usa aria-___ (5 letras)", "label"),
  ec="hacer botones con div y onClick que no funcionan con el teclado"),
K("StrictMode",
  d="componente que activa comprobaciones extra solo en desarrollo",
  u="encontrar efectos sin limpieza y componentes impuros a tiempo",
  mas="StrictMode dibuja dos veces y ejecuta los efectos dos veces en desarrollo para que se noten los errores. En producción no hace nada. Por eso un console.log puede salir doble mientras programas.",
  k=["StrictMode solo actúa en desarrollo.", "StrictMode ejecuta los efectos dos veces para encontrar errores.", "En producción StrictMode no cambia nada."],
  sit="Tu console.log dentro de un efecto aparece dos veces en desarrollo y quieres saber si es un error. ¿Qué lo explica?",
  cod="""import { StrictMode, useEffect } from "react";

function Hijo() {
  useEffect(() => { console.log("Efecto (en desarrollo puede salir dos veces)"); }, []);
  return <p>Revisa la consola</p>;
}

function App() {
  return <StrictMode><Hijo /></StrictMode>;
}""",
  h="envuelve un componente en StrictMode para revisar sus efectos",
  pr=("StrictMode solo actúa en modo de ___ (10 letras)", "desarrollo"),
  ec="quitar StrictMode para ocultar un efecto mal escrito"),
K("useTransition",
  d="hook que marca una actualización como no urgente",
  u="que la interfaz siga respondiendo mientras se calcula algo pesado",
  mas="startTransition(() => setLista(...)) le dice a React que esa actualización puede esperar. Lo urgente, como escribir en un input, se atiende primero. isPending indica que la transición está en curso.",
  k=["useTransition marca actualizaciones como no urgentes.", "isPending indica que la transición sigue en curso.", "Con useTransition el input sigue respondiendo rápido."],
  sit="Al cambiar de pestaña tu app calcula una lista enorme y todo se congela un segundo. ¿Qué usarías?",
  cod="""import { useState, useTransition } from "react";

function App() {
  const [n, setN] = useState(0);
  const [pendiente, startTransition] = useTransition();
  const cargar = () => startTransition(() => setN((v) => v + 5000));   // no urgente
  return (
    <div>
      <button onClick={cargar}>Cargar 5000 más</button> {pendiente && "⏳"}
      <p>{Array.from({ length: n }).length} elementos</p>
    </div>
  );
}""",
  h="marca como no urgente una actualización pesada",
  pr=("useTransition devuelve isPending y la función start___ (10 letras)", "transition"),
  ec="usar transiciones para lo que escribe la persona en un input"),
K("useDeferredValue",
  d="hook que entrega una versión retrasada de un valor",
  u="que un input rápido no espere a que se dibuje una lista lenta",
  mas="const diferido = useDeferredValue(texto) devuelve el texto anterior mientras React está ocupado. El input usa texto y la lista pesada usa diferido, así escribir nunca se traba.",
  k=["useDeferredValue devuelve una versión retrasada de un valor.", "El input usa el valor actual y la lista el diferido.", "useDeferredValue evita que escribir se trabe."],
  sit="Al escribir en el buscador, cada letra tarda porque la lista de resultados es muy pesada. ¿Qué usarías?",
  cod="""import { useDeferredValue, useState } from "react";

const PALABRAS = Array.from({ length: 3000 }, (_, i) => `palabra ${i}`);

function App() {
  const [q, setQ] = useState("");
  const diferido = useDeferredValue(q);   // la lista usa el valor retrasado
  const res = PALABRAS.filter((p) => p.includes(diferido)).slice(0, 8);
  return <div><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar" /><ul>{res.map((p) => <li key={p}>{p}</li>)}</ul></div>;
}""",
  h="filtra una lista con un valor diferido del buscador",
  pr=("El hook que entrega una versión retrasada de un valor es use___Value (8 letras)", "deferred"),
  ec="usar el valor diferido en el input y que lo escrito aparezca tarde"),
K("React Hook Form",
  d="biblioteca para formularios rápidos con validación y menos código",
  u="manejar formularios grandes sin un useState por campo",
  mas="useForm devuelve register para conectar cada input, handleSubmit para enviar y formState.errors con los errores. Los inputs no se vuelven a dibujar en cada letra, por eso es muy rápido.",
  k=["useForm de React Hook Form maneja todo el formulario.", "register conecta cada input con el formulario.", "formState.errors contiene los errores de validación."],
  sit="Tu formulario de registro tiene 15 campos y escribir un useState y onChange para cada uno es eterno. ¿Qué usarías?",
  cod="""import { useForm } from "react-hook-form";

function App() {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const enviar = (datos) => alert(JSON.stringify(datos));
  return (
    <form onSubmit={handleSubmit(enviar)}>
      <input {...register("correo", { required: "El correo es obligatorio" })} placeholder="Correo" />
      {errors.correo && <p>{errors.correo.message}</p>}
      <button>Enviar</button>
    </form>
  );
}""",
  h="valida un correo obligatorio con React Hook Form",
  pr=("En React Hook Form, cada input se conecta con la función ___ (8 letras)", "register"),
  ec="mezclar inputs controlados con useState y register en el mismo campo"),
K("Estructura de carpetas",
  d="organizar el proyecto en carpetas como components, pages, hooks y services",
  u="encontrar rápido cada archivo cuando el proyecto crece",
  mas="Una estructura común: src/components para piezas reutilizables, src/pages para pantallas, src/hooks para hooks propios y src/services para llamadas a la API. Lo importante es ser consistente en todo el proyecto.",
  k=["src/components guarda los componentes reutilizables.", "src/pages guarda las pantallas de cada ruta.", "src/services guarda las llamadas a la API."],
  sit="Tu carpeta src tiene 60 archivos sueltos y ya no encuentras nada. ¿Qué harías?",
  cod="""// src/
//   components/Boton.jsx
//   pages/Inicio.jsx
//   hooks/useCarrito.js
//   services/api.js
//   App.jsx · main.jsx
function App() {
  return <p>📁 components · pages · hooks · services</p>;
}""",
  h="muestra una estructura de carpetas ordenada",
  pr=("Las pantallas de cada ruta suelen ir en la carpeta src/___ (5 letras)", "pages"),
  ec="dejar todos los archivos sueltos en src"),
K("Perfilar el rendimiento",
  d="medir qué componentes tardan en dibujarse antes de optimizar",
  u="optimizar donde de verdad hace falta",
  mas="La pestaña Profiler de React DevTools graba una interacción y muestra cuánto tardó cada componente y por qué se volvió a dibujar. Optimizar a ciegas con memo en todas partes complica el código sin mejorar.",
  k=["El Profiler muestra cuánto tarda en dibujarse cada componente.", "Antes de optimizar hay que medir.", "El Profiler indica por qué un componente se volvió a dibujar."],
  sit="Tu app se siente lenta al escribir y no sabes qué componente es el culpable. ¿Qué usarías primero?",
  cod="""import { Profiler, useState } from "react";

function App() {
  const [t, setT] = useState("");
  const medir = (id, fase, ms) => console.log(`${id} (${fase}): ${ms.toFixed(2)} ms`);
  return (
    <Profiler id="Formulario" onRender={medir}>
      <input value={t} onChange={(e) => setT(e.target.value)} placeholder="Escribe y mira la consola" />
    </Profiler>
  );
}""",
  h="mide cuánto tarda en dibujarse un formulario",
  pr=("La herramienta que mide cuánto tarda cada componente se llama ___ (8 letras)", "profiler"),
  ec="llenar la app de memo y useMemo sin medir antes"),
K("ESLint para React",
  d="revisor de código que avisa errores comunes de React y de los hooks",
  u="encontrar dependencias faltantes y malas prácticas al escribir",
  mas="Vite trae ESLint configurado. El plugin react-hooks revisa las reglas de los hooks y las dependencias de useEffect. Los avisos aparecen en el editor antes de ejecutar.",
  k=["ESLint revisa el código mientras escribes.", "El plugin react-hooks revisa las dependencias de useEffect.", "npm run lint ejecuta ESLint en el proyecto."],
  sit="Olvidaste una dependencia en useEffect y tu app muestra datos viejos; quieres que el editor te avise la próxima vez. ¿Qué usarías?",
  cod="""// npm run lint   ->  "React Hook useEffect has a missing dependency: 'id'"
import { useEffect, useState } from "react";

function App() {
  const [id] = useState(1);
  const [txt, setTxt] = useState("");
  useEffect(() => { setTxt(`Usuario ${id}`); }, [id]);   // ESLint pide incluir id
  return <p>{txt}</p>;
}""",
  h="incluye la dependencia que ESLint pediría",
  pr=("Para revisar el proyecto con ESLint se ejecuta npm run ___ (4 letras)", "lint"),
  ec="desactivar el aviso de dependencias en lugar de arreglar el efecto"),
K("Buenas prácticas de componentes",
  d="reglas para escribir componentes claros, pequeños y fáciles de mantener",
  u="que tu código se pueda leer y cambiar sin miedo",
  mas="Componentes pequeños con un solo trabajo, nombres claros, props bien nombradas, sin estados duplicados, lógica reutilizable en hooks y sin efectos innecesarios. Si un componente pasa de 200 líneas, probablemente hay que dividirlo.",
  k=["Un buen componente hace una sola cosa.", "La lógica repetida va en hooks personalizados.", "Los componentes muy largos conviene dividirlos."],
  sit="Revisas tu proyecto antes de entregarlo y quieres que otro programador lo entienda sin explicaciones. ¿Qué aplicarías?",
  cod="""// ✅ pequeño, nombre claro, props claras, sin efectos innecesarios
function PrecioFormateado({ valor, moneda = "COP" }) {
  return <b>{new Intl.NumberFormat("es-CO", { style: "currency", currency: moneda }).format(valor)}</b>;
}

function App() {
  return <p>Total: <PrecioFormateado valor={125000} /></p>;
}""",
  h="muestra un componente pequeño con una sola responsabilidad",
  pr=("Un buen componente tiene una sola ___ (16 letras)", "responsabilidad"),
  ec="hacer componentes enormes que mezclan datos, lógica y diseño"),
K("Proyecto final con React",
  d="unir componentes, estado, rutas y datos en una aplicación completa",
  u="demostrar todo lo aprendido en un portafolio",
  mas="Un buen proyecto final: una app de tareas, tienda o clima con varias páginas (React Router), datos de una API, estado global, formularios validados, diseño responsivo y publicada en internet con su repositorio en GitHub.",
  k=["Un proyecto final une componentes, estado, rutas y datos.", "Publicar el proyecto permite mostrarlo en un portafolio.", "Un proyecto final debería tener su repositorio en GitHub."],
  sit="Terminaste el curso de React y quieres algo que mostrar en entrevistas de trabajo. ¿Qué harías?",
  cod="""import { useState } from "react";

function App() {
  const [tareas, setTareas] = useState([{ id: 1, t: "Aprender React", ok: true }, { id: 2, t: "Publicar mi app", ok: false }]);
  const alternar = (id) => setTareas(tareas.map((x) => (x.id === id ? { ...x, ok: !x.ok } : x)));
  return (
    <ul>
      {tareas.map((x) => (
        <li key={x.id} onClick={() => alternar(x.id)} style={{ textDecoration: x.ok ? "line-through" : "none", cursor: "pointer" }}>{x.t}</li>
      ))}
    </ul>
  );
}""",
  h="muestra una lista de tareas que se marcan al hacer clic",
  pr=("Para mostrar tus proyectos a empresas se arma un ___ (10 letras)", "portafolio", "portfolio"),
  ec="dejar los proyectos solo en tu computador sin publicarlos"),
]
