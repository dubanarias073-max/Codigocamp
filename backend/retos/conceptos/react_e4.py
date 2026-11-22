"""React · Etapa 4: Rutas, datos y estilos."""
from ..generador import K

LISTA = [
K("React Router",
  d="biblioteca para tener varias páginas con su propia dirección en una app de React",
  u="navegar entre Inicio, Productos y Contacto sin recargar la página",
  mas="React Router muestra un componente distinto según la URL. Se instala con npm install react-router-dom y la app se envuelve en BrowserRouter. Así tu aplicación de una sola página parece un sitio con muchas páginas.",
  k=["React Router muestra componentes según la dirección.", "React Router se instala con npm install react-router-dom.", "Con React Router se navega sin recargar la página."],
  sit="Tu app necesita las páginas /inicio, /productos y /contacto y que el botón atrás del navegador funcione. ¿Qué usarías?",
  cod="""import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

const Inicio = () => <h2>🏠 Inicio</h2>;
const Contacto = () => <h2>✉️ Contacto</h2>;

function App() {
  return (
    <BrowserRouter>
      <nav><Link to="/">Inicio</Link> · <Link to="/contacto">Contacto</Link></nav>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/contacto" element={<Contacto />} />
      </Routes>
    </BrowserRouter>
  );
}""",
  h="navega entre dos páginas con React Router",
  pr=("El paquete de rutas para la web se instala como react-router-___ (3 letras)", "dom"),
  ec="usar etiquetas <a href> que recargan toda la página en vez de Link"),
K("Routes y Route",
  d="componentes que definen qué elemento se muestra en cada ruta",
  u="declarar el mapa de páginas de la aplicación",
  mas="Routes revisa la dirección actual y muestra el primer Route que coincide. Cada Route tiene path y element. path=\"*\" atrapa cualquier dirección que no exista.",
  k=["Route une un path con el elemento que se muestra.", "Routes muestra la ruta que coincide con la dirección.", "path=\"*\" captura las direcciones que no existen."],
  sit="Quieres declarar que en /perfil se muestre el componente Perfil y en /ajustes el componente Ajustes. ¿Qué usarías?",
  cod="""import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Link to="/perfil">Perfil</Link> · <Link to="/ajustes">Ajustes</Link>
      <Routes>
        <Route path="/perfil" element={<p>👤 Tu perfil</p>} />
        <Route path="/ajustes" element={<p>⚙️ Ajustes</p>} />
        <Route path="*" element={<p>Elige una opción</p>} />
      </Routes>
    </BrowserRouter>
  );
}""",
  h="muestra el perfil o los ajustes según la ruta",
  pr=("Cada Route tiene un path y la prop ___ con lo que se muestra. (7 letras)", "element"),
  ec="poner Route fuera de un Routes"),
K("Link y NavLink",
  d="componentes para navegar entre rutas sin recargar la página",
  u="hacer menús de navegación dentro de la app",
  mas="Link funciona como <a> pero cambia la ruta sin recargar. NavLink además sabe si su ruta está activa, para pintar el enlace actual con otro estilo.",
  k=["Link navega a otra ruta sin recargar la página.", "Link usa la prop to en lugar de href.", "NavLink sabe si su ruta es la activa."],
  sit="Tu menú usa <a href> y cada clic recarga toda la app y borra el estado. ¿Qué usarías?",
  cod="""import { BrowserRouter, NavLink, Routes, Route } from "react-router-dom";

const estilo = ({ isActive }) => ({ fontWeight: isActive ? 800 : 400, marginRight: 10 });

function App() {
  return (
    <BrowserRouter>
      <NavLink to="/" style={estilo}>Inicio</NavLink>
      <NavLink to="/blog" style={estilo}>Blog</NavLink>
      <Routes><Route path="/" element={<p>Inicio</p>} /><Route path="/blog" element={<p>Blog</p>} /></Routes>
    </BrowserRouter>
  );
}""",
  h="resalta el enlace de la página activa con NavLink",
  pr=("En Link, la dirección de destino va en la prop ___ (2 letras)", "to"),
  ec="usar href en Link en lugar de to"),
K("useNavigate",
  d="hook que permite cambiar de ruta desde el código",
  u="ir a otra página después de una acción, como iniciar sesión",
  mas="useNavigate devuelve una función: navigate('/panel') cambia de ruta. navigate(-1) vuelve atrás y { replace: true } reemplaza la entrada del historial.",
  k=["useNavigate devuelve una función para cambiar de ruta.", "navigate(-1) vuelve a la página anterior.", "useNavigate se usa después de acciones como iniciar sesión."],
  sit="Después de que el login responde bien, quieres llevar a la persona automáticamente a /panel. ¿Qué usarías?",
  cod="""import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();
  return <button onClick={() => navigate("/panel")}>Entrar</button>;   // cambia de ruta por código
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/panel" element={<p>✅ Bienvenido al panel</p>} />
      </Routes>
    </BrowserRouter>
  );
}""",
  h="lleva al panel al pulsar entrar",
  pr=("El hook para cambiar de ruta desde el código es ___. (11 letras)", "usenavigate"),
  ec="usar window.location.href y recargar toda la aplicación"),
K("useParams",
  d="hook que lee las partes variables de la ruta, como /producto/:id",
  u="mostrar el detalle de un producto según el id de la dirección",
  mas="En la ruta se marca la parte variable con dos puntos: path=\"/producto/:id\". Dentro del componente, useParams() devuelve { id: '42' }. Los parámetros siempre llegan como texto.",
  k=["useParams lee las partes variables de la ruta.", "En el path, la parte variable se marca con dos puntos.", "Los parámetros de useParams llegan como texto."],
  sit="Tienes una sola página de detalle y quieres que /producto/7 muestre el producto 7. ¿Qué usarías?",
  cod="""import { BrowserRouter, Routes, Route, Link, useParams } from "react-router-dom";

function Producto() {
  const { id } = useParams();                // "7" (texto)
  return <h3>Producto número {id}</h3>;
}

function App() {
  return (
    <BrowserRouter>
      <Link to="/producto/7">Ver producto 7</Link>
      <Routes><Route path="/producto/:id" element={<Producto />} /></Routes>
    </BrowserRouter>
  );
}""",
  h="muestra el número de producto que viene en la ruta",
  pr=("En el path, la parte variable se marca con dos ___: /producto/:id (6 letras)", "puntos"),
  ec="olvidar que los parámetros llegan como texto y compararlos con números"),
K("Rutas anidadas y Outlet",
  d="rutas dentro de otras que comparten un diseño común",
  u="tener un menú lateral fijo y cambiar solo el contenido",
  mas="Un Route puede tener Routes hijos. El componente padre pone <Outlet /> donde se dibujará la ruta hija. Así el diseño (menú, cabecera) se escribe una sola vez.",
  k=["Las rutas anidadas comparten el diseño del padre.", "Outlet marca dónde se dibuja la ruta hija.", "Con rutas anidadas el menú se escribe una sola vez."],
  sit="Tu panel tiene un menú lateral igual en /panel/ventas y /panel/clientes y solo cambia la parte derecha. ¿Qué usarías?",
  cod="""import { BrowserRouter, Routes, Route, Link, Outlet } from "react-router-dom";

function Panel() {
  return (
    <div style={{ display: "flex", gap: 16 }}>
      <nav><Link to="ventas">Ventas</Link><br /><Link to="clientes">Clientes</Link></nav>
      <section><Outlet /></section>       {/* aquí aparece la ruta hija */}
    </div>
  );
}

function App() {
  return (
    <BrowserRouter initialEntries={["/panel"]}>
      <Routes>
        <Route path="/panel" element={<Panel />}>
          <Route path="ventas" element={<p>📈 Ventas</p>} />
          <Route path="clientes" element={<p>👥 Clientes</p>} />
        </Route>
        <Route path="*" element={<Link to="/panel">Ir al panel</Link>} />
      </Routes>
    </BrowserRouter>
  );
}""",
  h="muestra ventas o clientes dentro del diseño del panel",
  pr=("El componente que marca dónde va la ruta hija es ___. (6 letras)", "outlet"),
  ec="olvidar poner <Outlet /> en el componente padre"),
K("CSS Modules",
  d="archivos .module.css cuyas clases solo afectan al componente que las importa",
  u="evitar que los estilos de un componente choquen con los de otro",
  mas="Al importar estilos from './Boton.module.css', cada clase se convierte en un nombre único. Se usa className={estilos.boton}. Dos componentes pueden tener la clase .boton sin pisarse.",
  k=["Las clases de CSS Modules solo afectan a su componente.", "Los archivos de CSS Modules terminan en .module.css.", "Las clases se usan como estilos.nombre en className."],
  sit="La clase .titulo de tu componente Tarjeta cambia sin querer los títulos de otra página. ¿Qué usarías?",
  cod="""// Boton.module.css:  .boton { background: #61dafb; }
// import estilos from "./Boton.module.css";
const estilos = { boton: "boton_x7f2" };   // así queda: un nombre único

function App() {
  return <button className={estilos.boton}>Clase con nombre único: {estilos.boton}</button>;
}""",
  h="usa una clase de CSS Modules con nombre único",
  pr=("Los archivos de CSS Modules terminan en .___.css (6 letras)", "module"),
  ec="escribir className=\"boton\" como texto en lugar de estilos.boton"),
K("Tailwind CSS en React",
  d="framework de CSS con clases pequeñas que se combinan en className",
  u="dar estilo rápido sin escribir archivos CSS aparte",
  mas="Tailwind trae clases como p-4, bg-sky-500 o rounded-xl que hacen una sola cosa. En Vite se instala como plugin. Para estilos según el estado se arma el className con un ternario.",
  k=["Tailwind usa clases pequeñas que hacen una sola cosa.", "Las clases de Tailwind se combinan en className.", "Tailwind evita escribir muchos archivos CSS aparte."],
  sit="Quieres maquetar rápido botones y tarjetas bonitas sin escribir hojas de estilo propias. ¿Qué usarías?",
  cod="""// npm install tailwindcss @tailwindcss/vite  (y el plugin en vite.config.js)
function App() {
  const activo = true;
  return (
    <button className={`px-4 py-2 rounded-xl text-white ${activo ? "bg-sky-500" : "bg-gray-400"}`}>
      Botón con Tailwind
    </button>
  );
}""",
  h="arma un botón con clases de Tailwind",
  pr=("En Tailwind, la clase para redondear mucho las esquinas es rounded-___ (2 letras)", "xl"),
  ec="pelear con clases de Tailwind y CSS propio que se contradicen"),
K("async/await con datos",
  d="escribir peticiones a una API de forma secuencial y fácil de leer",
  u="cargar datos en un efecto sin cadenas de then",
  mas="La función del efecto no puede ser async, así que adentro se crea una función async y se llama. Con try/catch se manejan los errores y con finally se apaga la carga.",
  k=["La función de useEffect no puede ser async directamente.", "Dentro del efecto se crea una función async y se llama.", "try/catch atrapa los errores de await."],
  sit="Tu cadena de .then().then().catch() se volvió difícil de leer y quieres escribirla como pasos. ¿Qué usarías?",
  cod="""import { useEffect, useState } from "react";

function App() {
  const [todo, setTodo] = useState(null);
  useEffect(() => {
    async function cargar() {                    // la función async va adentro
      try {
        const r = await fetch("https://jsonplaceholder.typicode.com/todos/1");
        setTodo(await r.json());
      } catch (e) {
        setTodo({ title: "Error: " + e.message });
      }
    }
    cargar();
  }, []);
  return <p>{todo ? todo.title : "Cargando…"}</p>;
}""",
  h="carga una tarea con async y await dentro de un efecto",
  pr=("Para esperar una promesa dentro de una función async se usa ___. (5 letras)", "await"),
  ec="escribir useEffect(async () => ...) que devuelve una promesa"),
K("Enviar datos con POST",
  d="mandar información del formulario al servidor con fetch y method POST",
  u="crear registros, como un nuevo comentario o usuario",
  mas="fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(datos) }) envía datos. Mientras se envía conviene desactivar el botón para no mandar dos veces.",
  k=["Para enviar datos con fetch se usa method: \"POST\".", "El cuerpo se envía con body: JSON.stringify(datos).", "La cabecera Content-Type indica que se envía JSON."],
  sit="Tu formulario de comentarios debe guardar el comentario en el servidor al pulsar «Publicar». ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [r, setR] = useState(null);
  const publicar = async () => {
    const res = await fetch("https://jsonplaceholder.typicode.com/posts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Hola", body: "Mi primer post", userId: 1 }),
    });
    setR(await res.json());
  };
  return <div><button onClick={publicar}>Publicar</button><pre>{r && JSON.stringify(r, null, 2)}</pre></div>;
}""",
  h="envía un post al servidor y muestra la respuesta",
  pr=("Para crear datos en el servidor, fetch usa el método ___ (4 letras)", "post"),
  ec="olvidar convertir el objeto con JSON.stringify antes de enviarlo"),
K("Axios",
  d="biblioteca para hacer peticiones HTTP con una API más cómoda que fetch",
  u="pedir y enviar datos con menos código y errores HTTP automáticos",
  mas="axios.get(url) devuelve la respuesta con los datos ya convertidos en res.data. A diferencia de fetch, lanza un error si el servidor responde 4xx o 5xx. Se pueden crear instancias con una URL base.",
  k=["Axios devuelve los datos ya convertidos en res.data.", "Axios lanza un error si el servidor responde con error.", "Axios se instala con npm install axios."],
  sit="Te cansaste de escribir res.json() y revisar res.ok en cada petición de tu app. ¿Qué biblioteca usarías?",
  cod="""import axios from "axios";
import { useEffect, useState } from "react";

function App() {
  const [nombre, setNombre] = useState("…");
  useEffect(() => {
    axios.get("https://jsonplaceholder.typicode.com/users/1")
      .then((res) => setNombre(res.data.name));   // los datos vienen en res.data
  }, []);
  return <p>Usuario: {nombre}</p>;
}""",
  h="trae el nombre de un usuario con axios",
  pr=("Con axios, los datos de la respuesta vienen en res.___ (4 letras)", "data"),
  ec="buscar los datos en res.json() cuando se usa axios"),
K("Variables de entorno en Vite",
  d="valores de configuración en el archivo .env que empiezan con VITE_",
  u="guardar la URL de la API según si es desarrollo o producción",
  mas="Vite solo expone a tu código las variables que empiezan con VITE_ y se leen con import.meta.env.VITE_API_URL. Nunca pongas ahí claves secretas: todo lo del frontend termina visible en el navegador.",
  k=["Las variables de Vite para el navegador empiezan con VITE_.", "Se leen con import.meta.env.", "Las claves secretas no deben ir en el frontend."],
  sit="Tu app usa http://localhost:8000 como API en desarrollo y otra dirección en producción, y no quieres cambiarlo a mano. ¿Qué usarías?",
  cod="""// .env:  VITE_API_URL=http://localhost:8000
const API = import.meta.env?.VITE_API_URL ?? "https://api.ejemplo.com";

function App() {
  return <p>La API está en: <code>{API}</code></p>;
}""",
  h="lee la dirección de la API desde las variables de entorno",
  pr=("En Vite, las variables de entorno se leen con import.meta.___ (3 letras)", "env"),
  ec="guardar una clave secreta en una variable VITE_ pensando que es privada"),
K("Validación de formularios",
  d="revisar los datos antes de enviarlos y mostrar errores claros",
  u="evitar datos incompletos o con formato equivocado",
  mas="Se validan los campos en onSubmit o mientras se escribe y se guardan los mensajes de error en el estado. Los atributos de HTML como required y type=email ayudan, pero el servidor siempre debe validar también.",
  k=["Validar evita enviar datos incompletos o mal escritos.", "Los mensajes de error se guardan en el estado.", "El servidor también debe validar los datos."],
  sit="Te llegan registros sin correo o con contraseñas de dos letras, y quieres avisar antes de enviar. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [clave, setClave] = useState("");
  const [error, setError] = useState("");
  const enviar = (e) => {
    e.preventDefault();
    if (clave.length < 8) return setError("La contraseña necesita al menos 8 caracteres");
    setError(""); alert("¡Registrado!");
  };
  return (
    <form onSubmit={enviar}>
      <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} placeholder="Contraseña" />
      <button>Registrar</button>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </form>
  );
}""",
  h="exige una contraseña de al menos ocho caracteres",
  pr=("Además del navegador, los datos siempre se validan en el ___ (8 letras)", "servidor", "backend"),
  ec="validar solo en el frontend y confiar en lo que llega al servidor"),
K("lazy y Suspense",
  d="cargar componentes solo cuando se necesitan y mostrar algo mientras llegan",
  u="que la app abra más rápido dividiendo el código",
  mas="lazy(() => import('./Pagina')) carga el componente la primera vez que se dibuja. Suspense muestra el fallback, por ejemplo «Cargando…», mientras llega. Es ideal para páginas que no se visitan siempre.",
  k=["lazy carga un componente solo cuando se necesita.", "Suspense muestra un fallback mientras el componente carga.", "lazy y Suspense hacen que la app abra más rápido."],
  sit="Tu app tarda en abrir porque incluye una página de reportes pesada que casi nadie visita. ¿Qué usarías?",
  cod="""import { lazy, Suspense, useState } from "react";

// import("./Reportes") se descarga solo al mostrarse
const Reportes = lazy(() => new Promise((ok) => setTimeout(() => ok({ default: () => <p>📊 Reportes listos</p> }), 1200)));

function App() {
  const [ver, setVer] = useState(false);
  return (
    <div>
      <button onClick={() => setVer(true)}>Ver reportes</button>
      {ver && <Suspense fallback={<p>Cargando…</p>}><Reportes /></Suspense>}
    </div>
  );
}""",
  h="carga los reportes al pedirlos y muestra cargando mientras tanto",
  pr=("La prop de Suspense con lo que se muestra mientras carga se llama ___. (8 letras)", "fallback"),
  ec="usar lazy sin envolver el componente en Suspense"),
K("Portales",
  d="dibujar un componente en otra parte del DOM con createPortal",
  u="mostrar modales y avisos por encima de todo",
  mas="createPortal(jsx, document.body) pone el JSX fuera del contenedor del componente, pero sigue siendo parte del árbol de React: recibe props y eventos normalmente. Así un modal no queda cortado por un overflow.",
  k=["createPortal dibuja el JSX en otro lugar del DOM.", "Un portal sigue recibiendo props y eventos de React.", "Los portales se usan para modales y avisos."],
  sit="Tu ventana modal queda cortada porque está dentro de una tarjeta con overflow: hidden. ¿Qué usarías?",
  cod="""import { useState } from "react";
import { createPortal } from "react-dom";

function App() {
  const [abierto, setAbierto] = useState(false);
  return (
    <div style={{ overflow: "hidden", border: "1px solid #ccc", padding: 8 }}>
      <button onClick={() => setAbierto(true)}>Abrir modal</button>
      {abierto && createPortal(
        <div style={{ position: "fixed", inset: 0, background: "#0008", display: "grid", placeItems: "center" }} onClick={() => setAbierto(false)}>
          <p style={{ background: "#fff", padding: 20, borderRadius: 12 }}>Modal en document.body (clic para cerrar)</p>
        </div>, document.body)}
    </div>
  );
}""",
  h="abre un modal dibujado directamente en el body",
  pr=("La función para dibujar en otro lugar del DOM es create___ (6 letras)", "portal"),
  ec="dibujar el modal dentro de un contenedor con overflow hidden"),
K("Error Boundaries",
  d="componentes que atrapan errores de sus hijos y muestran algo en su lugar",
  u="que un error en un componente no deje toda la app en blanco",
  mas="Un error al dibujar un componente rompe todo el árbol. Un Error Boundary lo atrapa y muestra un mensaje. Se escribe como clase con getDerivedStateFromError, o se usa la biblioteca react-error-boundary.",
  k=["Un Error Boundary atrapa errores al dibujar sus hijos.", "Un Error Boundary evita que toda la app quede en blanco.", "Los Error Boundaries se escriben con una clase o con react-error-boundary."],
  sit="Si el widget del clima falla, toda tu página queda en blanco, y quieres que solo esa parte muestre un aviso. ¿Qué usarías?",
  cod="""import { Component } from "react";

class Protector extends Component {
  state = { error: null };
  static getDerivedStateFromError(error) { return { error }; }   // atrapa el error
  render() { return this.state.error ? <p>⚠️ Esta parte falló</p> : this.props.children; }
}

function Clima() { throw new Error("API caída"); }

function App() {
  return <><h3>Mi panel</h3><Protector><Clima /></Protector><p>El resto sigue funcionando ✅</p></>;
}""",
  h="atrapa el error del clima y mantiene el resto de la página",
  pr=("El método estático que guarda el error en el estado es getDerivedStateFrom___ (5 letras)", "error"),
  ec="dejar que un error en un componente pequeño tumbe toda la aplicación"),
K("Paginación",
  d="mostrar una lista larga por partes con botones para avanzar",
  u="no cargar ni dibujar miles de elementos de una vez",
  mas="Se guarda la página actual en el estado y se calcula qué parte del arreglo mostrar con slice, o se pide al servidor solo esa página con ?page=2. Los botones se desactivan en la primera y la última.",
  k=["La paginación muestra la lista por partes.", "La página actual se guarda en el estado.", "slice toma solo los elementos de la página actual."],
  sit="Tu tabla tiene 2000 pedidos y el navegador se pone lento al mostrarlos todos. ¿Qué usarías?",
  cod="""import { useState } from "react";

const PEDIDOS = Array.from({ length: 23 }, (_, i) => `Pedido #${i + 1}`);

function App() {
  const [pag, setPag] = useState(0);
  const porPag = 5, total = Math.ceil(PEDIDOS.length / porPag);
  const visibles = PEDIDOS.slice(pag * porPag, pag * porPag + porPag);   // solo esta página
  return (
    <div>
      <ul>{visibles.map((p) => <li key={p}>{p}</li>)}</ul>
      <button disabled={pag === 0} onClick={() => setPag(pag - 1)}>Anterior</button>
      <span> {pag + 1} / {total} </span>
      <button disabled={pag === total - 1} onClick={() => setPag(pag + 1)}>Siguiente</button>
    </div>
  );
}""",
  h="muestra los pedidos de cinco en cinco",
  pr=("Para tomar solo una parte del arreglo se usa el método ___ (5 letras)", "slice"),
  ec="dibujar miles de filas de una vez en lugar de paginar"),
K("Búsqueda y filtros",
  d="filtrar una lista según lo que se escribe o elige",
  u="encontrar rápido un elemento en catálogos grandes",
  mas="El texto de búsqueda va en el estado y la lista visible se calcula con filter en cada dibujo. Conviene comparar en minúsculas y quitar espacios. Para listas muy grandes se combina con useMemo o con useDeferredValue.",
  k=["El texto de búsqueda se guarda en el estado.", "La lista visible se calcula con filter.", "Comparar en minúsculas evita fallos por mayúsculas."],
  sit="Tu catálogo tiene 300 cursos y quieres que se filtren mientras la persona escribe en un buscador. ¿Qué usarías?",
  cod="""import { useState } from "react";

const CURSOS = ["HTML", "CSS", "JavaScript", "React", "Python", "SQL"];

function App() {
  const [q, setQ] = useState("");
  const visibles = CURSOS.filter((c) => c.toLowerCase().includes(q.trim().toLowerCase()));
  return (
    <div>
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar curso" />
      <ul>{visibles.map((c) => <li key={c}>{c}</li>)}</ul>
      {!visibles.length && <p>Sin resultados</p>}
    </div>
  );
}""",
  h="filtra cursos mientras se escribe",
  pr=("Para comparar sin importar mayúsculas se convierte con to___Case() (5 letras)", "lower"),
  ec="guardar la lista filtrada en otro estado en lugar de calcularla"),
K("Imágenes responsivas y carga diferida",
  d="mostrar imágenes del tamaño adecuado y cargarlas solo cuando se ven",
  u="que la app cargue rápido en celulares",
  mas="loading=\"lazy\" hace que el navegador descargue la imagen cuando está por aparecer. Con srcSet (en camelCase en JSX) se ofrecen varios tamaños. Siempre se indica alt y, si se puede, width y height para evitar saltos.",
  k=["loading=\"lazy\" descarga la imagen cuando está por verse.", "En JSX el atributo srcset se escribe srcSet.", "width y height evitan saltos mientras carga la imagen."],
  sit="Tu galería de 100 fotos descarga todas al abrir y en el celular tarda muchísimo. ¿Qué usarías?",
  cod="""function App() {
  const fotos = [10, 20, 30, 40, 50, 60];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
      {fotos.map((n) => (
        <img key={n} src={`https://picsum.photos/id/${n}/300/200`} alt={`Foto ${n}`} width={300} height={200} loading="lazy" style={{ width: "100%", height: "auto" }} />
      ))}
    </div>
  );
}""",
  h="muestra una galería con imágenes de carga diferida",
  pr=("Para que una imagen se descargue al verse se usa loading=\"___\" (4 letras)", "lazy"),
  ec="olvidar width y height y que la página salte al cargar las imágenes"),
K("Rutas protegidas",
  d="páginas que solo se muestran si la persona inició sesión",
  u="impedir que alguien sin sesión entre al panel",
  mas="Un componente revisa si hay usuario; si no, devuelve <Navigate to=\"/login\" replace />. Si hay usuario, dibuja sus hijos u <Outlet />. Recuerda que el servidor también debe proteger los datos.",
  k=["Una ruta protegida revisa si hay sesión antes de mostrarse.", "Navigate redirige a otra ruta al dibujarse.", "El servidor también debe proteger los datos privados."],
  sit="Cualquiera que escriba /panel en la barra de direcciones entra a tu panel sin iniciar sesión. ¿Qué harías?",
  cod="""import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";

function Protegida({ usuario, children }) {
  return usuario ? children : <Navigate to="/login" replace />;   // sin sesión -> login
}

function App() {
  const [usuario, setUsuario] = useState(null);
  return (
    <BrowserRouter>
      <Link to="/panel">Ir al panel</Link>
      <Routes>
        <Route path="/login" element={<button onClick={() => setUsuario("Ana")}>Iniciar sesión</button>} />
        <Route path="/panel" element={<Protegida usuario={usuario}><p>🔒 Panel de {usuario}</p></Protegida>} />
      </Routes>
    </BrowserRouter>
  );
}""",
  h="envía al login a quien no tiene sesión",
  pr=("El componente de React Router que redirige al dibujarse es ___ (8 letras)", "navigate"),
  ec="proteger solo en el frontend y dejar la API abierta"),
]
