"""React · Etapa 3: Efectos y hooks."""
from ..generador import K

LISTA = [
K("useEffect",
  d="hook que ejecuta código después de que el componente se dibuja",
  u="sincronizar el componente con algo externo, como una API o un temporizador",
  mas="useEffect recibe una función que React ejecuta después de pintar la pantalla. Sirve para lo que está fuera de React: pedir datos, suscribirse a eventos, cambiar el título de la pestaña o usar localStorage.",
  k=["useEffect ejecuta código después de dibujar el componente.", "useEffect sirve para sincronizar con sistemas externos.", "El código de useEffect no se ejecuta mientras React dibuja."],
  sit="Quieres que el título de la pestaña del navegador muestre cuántos mensajes nuevos tienes. ¿Qué usarías?",
  cod="""import { useEffect, useState } from "react";

function App() {
  const [n, setN] = useState(0);
  useEffect(() => {
    document.title = `(${n}) Mensajes`;   // se ejecuta después de dibujar
  }, [n]);
  return <button onClick={() => setN(n + 1)}>Nuevo mensaje ({n})</button>;
}""",
  h="cambia el título de la pestaña cuando cambia el contador",
  pr=("El hook que ejecuta código después de dibujar se llama ___. (9 letras)", "useeffect"),
  ec="cambiar el estado dentro de useEffect sin dependencias y crear un bucle infinito"),
K("Arreglo de dependencias",
  d="segundo parámetro de useEffect que indica cuándo debe volver a ejecutarse",
  u="controlar si el efecto corre una vez, siempre o cuando cambia un dato",
  mas="Con [] el efecto corre solo al montar el componente. Con [id] corre al montar y cada vez que id cambie. Sin arreglo corre después de cada dibujo. Todo lo que el efecto usa del componente debería estar en la lista.",
  k=["Con un arreglo vacío el efecto se ejecuta solo una vez al montar.", "Con [dato] el efecto se repite cuando ese dato cambia.", "Sin arreglo de dependencias el efecto corre en cada dibujo."],
  sit="Tu efecto pide los datos del usuario y debe repetirse solo cuando cambia el id del usuario. ¿Qué usarías?",
  cod="""import { useEffect, useState } from "react";

function App() {
  const [id, setId] = useState(1);
  const [log, setLog] = useState([]);
  useEffect(() => {
    setLog((l) => [...l, `Cargando usuario ${id}`]);   // solo cuando cambia id
  }, [id]);
  return (
    <div>
      <button onClick={() => setId(id + 1)}>Siguiente usuario</button>
      <ul>{log.map((x, i) => <li key={i}>{x}</li>)}</ul>
    </div>
  );
}""",
  h="registra una carga cada vez que cambia el id",
  pr=("Para que un efecto corra solo al montar, su arreglo de dependencias va ___. (5 letras)", "vacio", "vacío"),
  ec="omitir en las dependencias variables que el efecto sí usa"),
K("Limpieza del efecto",
  d="función que devuelve el efecto para deshacer lo que hizo",
  u="cancelar temporizadores y quitar suscripciones al desmontar",
  mas="Si el efecto devuelve una función, React la llama antes de volver a ejecutar el efecto y cuando el componente desaparece. Ahí se quita un setInterval, un addEventListener o una conexión.",
  k=["La función que devuelve useEffect es la limpieza.", "React ejecuta la limpieza al desmontar el componente.", "La limpieza también corre antes de repetir el efecto."],
  sit="Tu reloj usa setInterval y, al cambiar de página, sigue corriendo en segundo plano y da errores. ¿Qué usarías?",
  cod="""import { useEffect, useState } from "react";

function App() {
  const [s, setS] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setS((v) => v + 1), 1000);
    return () => clearInterval(t);   // limpieza: se detiene al desmontar
  }, []);
  return <p>⏱ {s} segundos</p>;
}""",
  h="cuenta segundos y detiene el temporizador al desmontar",
  pr=("Para detener un setInterval en la limpieza se llama a ___. (13 letras)", "clearinterval"),
  ec="crear un setInterval en un efecto sin limpiarlo"),
K("Pedir datos con fetch",
  d="traer información de una API dentro de un efecto",
  u="mostrar datos de un servidor, como productos o usuarios",
  mas="Dentro de useEffect se llama a fetch, se convierte la respuesta con json() y se guarda en el estado. Conviene manejar la carga, los errores y evitar actualizar el estado si el componente ya se desmontó.",
  k=["fetch dentro de useEffect trae datos de una API.", "La respuesta de fetch se convierte con res.json().", "Los datos de la API se guardan en el estado para mostrarlos."],
  sit="Quieres mostrar una lista de usuarios que vienen de https://jsonplaceholder.typicode.com/users. ¿Qué usarías?",
  cod="""import { useEffect, useState } from "react";

function App() {
  const [usuarios, setUsuarios] = useState([]);
  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/users")
      .then((res) => res.json())
      .then((datos) => setUsuarios(datos.slice(0, 5)));   // guarda los datos en el estado
  }, []);
  return <ul>{usuarios.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}""",
  h="muestra cinco usuarios traídos de una API",
  pr=("La función del navegador para pedir datos a una API es ___. (5 letras)", "fetch"),
  ec="llamar a fetch directamente en el cuerpo del componente en cada dibujo"),
K("Carga y errores",
  d="estados que indican si los datos están llegando o si algo falló",
  u="mostrar «Cargando…» y mensajes de error en lugar de una pantalla vacía",
  mas="Se usan estados como cargando y error junto a los datos. Mientras cargando es true se muestra un indicador; si fetch falla o la respuesta no es ok, se guarda el error y se muestra un mensaje claro.",
  k=["Un estado cargando muestra un indicador mientras llegan los datos.", "res.ok indica si el servidor respondió bien.", "Un estado de error permite mostrar un mensaje claro."],
  sit="Mientras llegan los datos tu página queda en blanco, y si falla internet no pasa nada visible. ¿Qué usarías?",
  cod="""import { useEffect, useState } from "react";

function App() {
  const [post, setPost] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/posts/1")
      .then((r) => { if (!r.ok) throw new Error(`Error ${r.status}`); return r.json(); })
      .then(setPost)
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false));
  }, []);
  if (cargando) return <p>Cargando…</p>;
  if (error) return <p>⚠️ {error}</p>;
  return <h3>{post.title}</h3>;
}""",
  h="muestra cargando, un error o el título del post",
  pr=("Para saber si el servidor respondió bien se revisa res.___ (2 letras)", "ok"),
  ec="no mostrar nada mientras cargan los datos ni cuando fallan"),
K("useRef",
  d="hook que guarda un valor que persiste entre dibujos sin volver a dibujar",
  u="guardar datos internos como un temporizador o el valor anterior",
  mas="useRef devuelve un objeto con la propiedad current. Puedes cambiar current cuando quieras y React no vuelve a dibujar. Es como una caja que el componente recuerda.",
  k=["useRef devuelve un objeto con la propiedad current.", "Cambiar ref.current no vuelve a dibujar el componente.", "Una ref conserva su valor entre dibujos."],
  sit="Quieres contar cuántas veces se dibuja un componente sin que contar provoque más dibujos. ¿Qué usarías?",
  cod="""import { useRef, useState } from "react";

function App() {
  const [t, setT] = useState("");
  const dibujos = useRef(0);
  dibujos.current++;                       // cambia sin volver a dibujar
  return (
    <div>
      <input value={t} onChange={(e) => setT(e.target.value)} placeholder="Escribe" />
      <p>Dibujos: {dibujos.current}</p>
    </div>
  );
}""",
  h="cuenta los dibujos con una ref",
  pr=("El valor de una ref se guarda en la propiedad ___. (7 letras)", "current"),
  ec="usar useRef para datos que deben verse actualizados en pantalla"),
K("Refs a elementos del DOM",
  d="conectar una ref con una etiqueta usando el atributo ref",
  u="enfocar un input, medir un elemento o hacer scroll",
  mas="Si pones ref={miRef} en una etiqueta, después de dibujar miRef.current es ese elemento del DOM. Con eso puedes llamar a focus(), scrollIntoView() o leer su tamaño.",
  k=["El atributo ref conecta una ref con un elemento del DOM.", "Después de dibujar, ref.current es el elemento real.", "Con una ref se puede enfocar un input con focus()."],
  sit="Quieres que al pulsar «Buscar» el cursor se ponga en el campo de búsqueda automáticamente. ¿Qué usarías?",
  cod="""import { useRef } from "react";

function App() {
  const campo = useRef(null);
  return (
    <div>
      <input ref={campo} placeholder="Buscar…" />
      <button onClick={() => campo.current.focus()}>Ir al buscador</button>   {/* elemento real */}
    </div>
  );
}""",
  h="enfoca el input al pulsar un botón",
  pr=("Para poner el cursor en un input se llama a ref.current.___() (5 letras)", "focus"),
  ec="usar document.getElementById en lugar de una ref en React"),
K("useMemo",
  d="hook que guarda el resultado de un cálculo costoso entre dibujos",
  u="no repetir cálculos pesados si sus datos no cambiaron",
  mas="useMemo(() => calcular(datos), [datos]) solo vuelve a calcular cuando cambian las dependencias. Úsalo para cálculos realmente costosos; para cosas simples no hace falta.",
  k=["useMemo guarda el resultado de un cálculo.", "useMemo recalcula solo cuando cambian sus dependencias.", "useMemo solo vale la pena para cálculos costosos."],
  sit="Tu componente filtra 50 000 productos en cada letra que escribes en otro campo y se pone lento. ¿Qué usarías?",
  cod="""import { useMemo, useState } from "react";

const numeros = Array.from({ length: 50000 }, (_, i) => i);

function App() {
  const [min, setMin] = useState(49990);
  const [nota, setNota] = useState("");
  const filtrados = useMemo(() => numeros.filter((n) => n >= min), [min]);   // solo si cambia min
  return (
    <div>
      <input value={nota} onChange={(e) => setNota(e.target.value)} placeholder="Nota (no recalcula)" />
      <button onClick={() => setMin(min - 1)}>Bajar mínimo</button>
      <p>{filtrados.length} números ≥ {min}</p>
    </div>
  );
}""",
  h="filtra una lista grande solo cuando cambia el mínimo",
  pr=("El hook que guarda el resultado de un cálculo costoso es ___. (7 letras)", "usememo"),
  ec="envolver cualquier cálculo pequeño en useMemo sin necesidad"),
K("useCallback",
  d="hook que guarda la misma función entre dibujos",
  u="evitar que hijos memorizados se vuelvan a dibujar por recibir una función nueva",
  mas="En cada dibujo las funciones se crean de nuevo. useCallback(fn, deps) devuelve la misma función mientras no cambien las dependencias. Sirve junto con React.memo o en dependencias de efectos.",
  k=["useCallback devuelve la misma función entre dibujos.", "useCallback crea otra función solo si cambian sus dependencias.", "useCallback se usa junto con React.memo."],
  sit="Pasas una función a un hijo memorizado con React.memo y aun así se vuelve a dibujar en cada cambio del padre. ¿Qué usarías?",
  cod="""import { memo, useCallback, useState } from "react";

const Boton = memo(function Boton({ alClic }) {
  console.log("Dibujando Boton");
  return <button onClick={alClic}>Sumar</button>;
});

function App() {
  const [n, setN] = useState(0);
  const [t, setT] = useState("");
  const sumar = useCallback(() => setN((v) => v + 1), []);   // misma función siempre
  return <div><input value={t} onChange={(e) => setT(e.target.value)} /><Boton alClic={sumar} /> {n}</div>;
}""",
  h="mantiene la misma función para que el botón no se vuelva a dibujar",
  pr=("El hook que guarda la misma función entre dibujos es ___. (11 letras)", "usecallback"),
  ec="usar useCallback sin React.memo esperando que mejore el rendimiento"),
K("React.memo",
  d="función que evita volver a dibujar un componente si sus props no cambiaron",
  u="optimizar componentes caros que reciben las mismas props",
  mas="memo(Componente) compara las props anteriores con las nuevas; si son iguales, reutiliza el resultado anterior. Es una optimización: primero mide si de verdad hay un problema de rendimiento.",
  k=["memo evita dibujar un componente si sus props son iguales.", "memo compara las props anteriores con las nuevas.", "memo es una optimización y no cambia el resultado."],
  sit="Una lista enorme se vuelve a dibujar cada vez que escribes en un buscador que no tiene nada que ver. ¿Qué usarías?",
  cod="""import { memo, useState } from "react";

const Lista = memo(function Lista({ items }) {
  console.log("Dibujando Lista");          // no aparece al escribir en el input
  return <ul>{items.map((x) => <li key={x}>{x}</li>)}</ul>;
});

const ITEMS = ["HTML", "CSS", "React"];

function App() {
  const [t, setT] = useState("");
  return <div><input value={t} onChange={(e) => setT(e.target.value)} placeholder="Escribe" /><Lista items={ITEMS} /></div>;
}""",
  h="evita volver a dibujar la lista al escribir en el input",
  pr=("La función que evita dibujar un componente con las mismas props es ___. (4 letras)", "memo"),
  ec="pasar un arreglo u objeto nuevo en cada dibujo a un componente con memo"),
K("Context",
  d="forma de compartir datos con muchos componentes sin pasarlos por props",
  u="tener disponibles el tema, el idioma o el usuario en toda la app",
  mas="Se crea con createContext, se envuelve la app con su Provider y un value, y cualquier componente de adentro lo lee con useContext. Evita pasar la misma prop por muchos niveles (prop drilling).",
  k=["Context comparte datos sin pasarlos por props en cada nivel.", "Context se crea con createContext.", "Context evita el prop drilling."],
  sit="Tienes que pasar el tema oscuro o claro por props a través de seis niveles de componentes. ¿Qué usarías?",
  cod="""import { createContext, useContext, useState } from "react";

const Tema = createContext("claro");                // 1. crear el contexto

function Boton() {
  const tema = useContext(Tema);                    // 3. leerlo en cualquier nivel
  return <button style={{ background: tema === "oscuro" ? "#222" : "#eee", color: tema === "oscuro" ? "#fff" : "#000" }}>Tema {tema}</button>;
}

function App() {
  const [tema, setTema] = useState("oscuro");
  return (
    <Tema.Provider value={tema}>                    {/* 2. darlo a toda la app */}
      <Boton />
      <button onClick={() => setTema(tema === "oscuro" ? "claro" : "oscuro")}>Cambiar</button>
    </Tema.Provider>
  );
}""",
  h="comparte el tema con un contexto",
  pr=("Pasar la misma prop por muchos niveles se llama prop ___. (8 letras)", "drilling"),
  pr2=("Un contexto se crea con la función create___ (7 letras)", "context"),
  ec="usar Context para todo, incluso datos que solo necesita un componente"),
K("useContext",
  d="hook que lee el valor del contexto más cercano",
  u="usar los datos compartidos dentro de cualquier componente",
  mas="useContext(MiContexto) devuelve el value del Provider más cercano hacia arriba. Si no hay Provider, devuelve el valor por defecto de createContext. Cuando el value cambia, los componentes que lo leen se vuelven a dibujar.",
  k=["useContext lee el value del Provider más cercano.", "Sin Provider, useContext devuelve el valor por defecto.", "Si el value cambia, quien usa useContext se vuelve a dibujar."],
  sit="Ya creaste un contexto con el usuario conectado y quieres mostrar su nombre en la barra de arriba. ¿Qué usarías?",
  cod="""import { createContext, useContext } from "react";

const Usuario = createContext({ nombre: "Invitado" });

function Barra() {
  const u = useContext(Usuario);                 // lee el Provider más cercano
  return <header>👤 {u.nombre}</header>;
}

function App() {
  return (
    <>
      <Barra />                                   {/* sin Provider: Invitado */}
      <Usuario.Provider value={{ nombre: "Ana" }}><Barra /></Usuario.Provider>
    </>
  );
}""",
  h="lee el usuario del contexto con y sin Provider",
  pr=("El hook que lee el valor de un contexto es ___. (10 letras)", "usecontext"),
  ec="usar useContext fuera de su Provider y recibir el valor por defecto sin darse cuenta"),
K("Provider",
  d="componente que entrega el valor de un contexto a todo lo que envuelve",
  u="decidir qué parte de la app tiene acceso a los datos compartidos",
  mas="Cada contexto trae su componente Provider. Lo que esté dentro puede leer su value. Es común crear un componente propio, como TemaProvider, que guarda el estado y lo entrega con su función para cambiarlo.",
  k=["Provider entrega el value del contexto a sus hijos.", "Solo los componentes dentro del Provider leen su value.", "Un Provider puede entregar el estado y la función para cambiarlo."],
  sit="Quieres que el carrito de compras esté disponible en todas las páginas de tu tienda. ¿Qué componente envolvería la app?",
  cod="""import { createContext, useContext, useState } from "react";

const Carrito = createContext(null);

function CarritoProvider({ children }) {
  const [items, setItems] = useState([]);
  return <Carrito.Provider value={{ items, agregar: (x) => setItems([...items, x]) }}>{children}</Carrito.Provider>;
}

function Tienda() {
  const { items, agregar } = useContext(Carrito);
  return <button onClick={() => agregar("🍕")}>Agregar · {items.join(" ")}</button>;
}

function App() {
  return <CarritoProvider><Tienda /></CarritoProvider>;
}""",
  h="entrega el carrito a toda la app con un Provider propio",
  pr=("El componente que entrega el valor de un contexto se llama ___. (8 letras)", "provider"),
  ec="olvidar envolver la app con el Provider"),
K("useReducer",
  d="hook que maneja estados complejos con una función reductora y acciones",
  u="ordenar la lógica cuando hay muchas formas de cambiar el estado",
  mas="useReducer(reducer, inicial) devuelve el estado y dispatch. Envías acciones como { type: 'agregar' } y el reducer decide cómo queda el estado nuevo. Junta toda la lógica de cambios en un solo lugar.",
  k=["useReducer devuelve el estado y la función dispatch.", "dispatch envía acciones al reducer.", "useReducer junta la lógica de cambios en una función."],
  sit="Tu lista de tareas tiene agregar, completar, borrar y limpiar, y tu componente está lleno de funciones con setTareas. ¿Qué usarías?",
  cod="""import { useReducer } from "react";

function reducer(estado, accion) {
  switch (accion.type) {
    case "sumar": return { n: estado.n + 1 };
    case "reiniciar": return { n: 0 };
    default: return estado;
  }
}

function App() {
  const [estado, dispatch] = useReducer(reducer, { n: 0 });
  return (
    <div>
      <p>{estado.n}</p>
      <button onClick={() => dispatch({ type: "sumar" })}>+1</button>
      <button onClick={() => dispatch({ type: "reiniciar" })}>Reiniciar</button>
    </div>
  );
}""",
  h="maneja un contador con acciones y un reducer",
  pr=("La función que envía acciones al reducer se llama ___. (8 letras)", "dispatch"),
  ec="mutar el estado dentro del reducer en lugar de devolver uno nuevo"),
K("Reducer",
  d="función pura que recibe el estado y una acción y devuelve el estado nuevo",
  u="describir todos los cambios posibles del estado en un solo lugar",
  mas="Un reducer no modifica nada: con el mismo estado y la misma acción siempre devuelve el mismo resultado. Por convención la acción es un objeto con type y, si hace falta, datos extra.",
  k=["Un reducer recibe el estado y una acción.", "Un reducer devuelve un estado nuevo sin modificar el anterior.", "Por convención una acción tiene una propiedad type."],
  sit="Quieres escribir, sin React, una función que diga cómo cambia el carrito con cada acción para poder probarla fácil. ¿Qué escribirías?",
  cod="""function carrito(estado, accion) {               // reducer: puro y sin efectos
  if (accion.type === "agregar") return [...estado, accion.producto];
  if (accion.type === "vaciar") return [];
  return estado;
}

function App() {
  const paso1 = carrito([], { type: "agregar", producto: "Libro" });
  const paso2 = carrito(paso1, { type: "agregar", producto: "Lápiz" });
  return <p>Carrito: {paso2.join(", ")}</p>;
}""",
  h="calcula el carrito aplicando acciones a un reducer",
  pr=("Por convención, una acción tiene una propiedad llamada ___. (4 letras)", "type"),
  ec="hacer peticiones o cambiar variables externas dentro del reducer"),
K("Hooks personalizados",
  d="funciones propias que empiezan con use y reúnen lógica con otros hooks",
  u="reutilizar lógica entre componentes, como leer el tamaño de la ventana",
  mas="Un hook personalizado es una función llamada useAlgo que usa useState, useEffect u otros hooks y devuelve lo que necesitas. Cada componente que lo usa tiene su propio estado.",
  k=["Un hook personalizado es una función que empieza con use.", "Un hook personalizado puede usar otros hooks.", "Cada componente que usa un hook tiene su propio estado."],
  sit="Tres componentes repiten el mismo código para saber si la ventana es de celular. ¿Qué usarías para no repetirlo?",
  cod="""import { useEffect, useState } from "react";

function useAnchoVentana() {                         // hook personalizado
  const [ancho, setAncho] = useState(window.innerWidth);
  useEffect(() => {
    const medir = () => setAncho(window.innerWidth);
    window.addEventListener("resize", medir);
    return () => window.removeEventListener("resize", medir);
  }, []);
  return ancho;
}

function App() {
  const ancho = useAnchoVentana();
  return <p>{ancho < 700 ? "📱 Celular" : "💻 Computador"} ({ancho}px)</p>;
}""",
  h="reutiliza la lógica del ancho de la ventana en un hook propio",
  pr=("El nombre de un hook personalizado empieza con ___. (3 letras)", "use"),
  ec="nombrar un hook sin el prefijo use y romper las reglas de los hooks"),
K("Reglas de los hooks",
  d="normas: llamar hooks solo en el nivel superior y solo en componentes o hooks",
  u="que React relacione cada estado con su hook en cada dibujo",
  mas="React identifica los hooks por el orden en que se llaman. Por eso no se llaman dentro de if, for o funciones internas, ni en funciones normales. El plugin eslint-plugin-react-hooks te avisa si rompes una regla.",
  k=["Los hooks se llaman en el nivel superior del componente.", "Los hooks no se llaman dentro de if ni de bucles.", "React reconoce cada hook por el orden en que se llama."],
  sit="Pusiste useState dentro de un if y React dice que el número de hooks cambió entre dibujos. ¿Qué revisarías?",
  cod="""import { useState } from "react";

function App() {
  const [visible, setVisible] = useState(true);   // ✅ arriba, siempre en el mismo orden
  const [texto] = useState("Regla cumplida");      // ✅
  // ❌ if (visible) { const [x] = useState(0); }   -> rompe el orden
  return <button onClick={() => setVisible(!visible)}>{visible ? texto : "…"}</button>;
}""",
  h="llama a los hooks siempre arriba y en el mismo orden",
  pr=("Los hooks se llaman siempre en el mismo ___ en cada dibujo. (5 letras)", "orden"),
  ec="llamar un hook dentro de un if o de un bucle"),
K("useId",
  d="hook que genera un identificador único y estable para el componente",
  u="conectar labels con inputs sin ids repetidos",
  mas="Si un componente con <label htmlFor> se usa varias veces, un id fijo se repetiría. useId da un id único por cada uso, estable entre dibujos y también al renderizar en el servidor.",
  k=["useId genera un id único para cada uso del componente.", "useId sirve para conectar un label con su input.", "El id de useId es estable entre dibujos."],
  sit="Tu componente Campo con label e input se usa tres veces en la página y los ids se repiten. ¿Qué usarías?",
  cod="""import { useId } from "react";

function Campo({ etiqueta }) {
  const id = useId();                          // único por cada Campo
  return <p><label htmlFor={id}>{etiqueta} </label><input id={id} /></p>;
}

function App() {
  return <><Campo etiqueta="Nombre" /><Campo etiqueta="Correo" /></>;
}""",
  h="crea campos con ids únicos usando useId",
  pr=("El hook que genera un id único y estable se llama ___. (5 letras)", "useid"),
  ec="usar Math.random() como id y que cambie en cada dibujo"),
K("Guardar en localStorage",
  d="combinar estado y efecto para que los datos sobrevivan al recargar",
  u="recordar preferencias o borradores aunque se cierre la pestaña",
  mas="El estado inicial se lee de localStorage con una función en useState y un efecto guarda el valor cada vez que cambia. Hay que convertir con JSON.stringify y JSON.parse los objetos.",
  k=["localStorage guarda datos que sobreviven al recargar.", "Un efecto guarda el estado en localStorage cuando cambia.", "Los objetos se guardan con JSON.stringify y se leen con JSON.parse."],
  sit="Quieres que el tema oscuro que eligió la persona siga puesto aunque recargue la página. ¿Qué usarías?",
  cod="""import { useEffect, useState } from "react";

function App() {
  const [nota, setNota] = useState(() => {
    try { return localStorage.getItem("nota") ?? ""; } catch { return ""; }   // lee al iniciar
  });
  useEffect(() => {
    try { localStorage.setItem("nota", nota); } catch { /* sin almacenamiento */ }   // guarda al cambiar
  }, [nota]);
  return <textarea value={nota} onChange={(e) => setNota(e.target.value)} placeholder="Se guarda sola" />;
}""",
  h="guarda una nota en localStorage cada vez que cambia",
  pr=("Para guardar un objeto en localStorage se convierte con JSON.___ (9 letras)", "stringify"),
  ec="leer localStorage en cada dibujo en lugar de solo al iniciar"),
K("Pasar refs a componentes hijos",
  d="permitir que el padre reciba la referencia a un elemento dentro de un componente hijo",
  u="enfocar o medir un input que está dentro de un componente propio",
  mas="En React 19 ref se pasa como una prop normal al componente hijo, que la coloca en su elemento. En versiones anteriores se envolvía el hijo con forwardRef. Así el padre puede llamar a ref.current.focus().",
  k=["En React 19 ref se puede recibir como una prop normal.", "En versiones anteriores se usaba forwardRef para pasar refs.", "El hijo coloca la ref en su elemento del DOM."],
  sit="Tu componente CampoTexto envuelve un input y el formulario padre necesita enfocarlo al abrir. ¿Qué usarías?",
  cod="""import { useRef } from "react";

function CampoTexto({ ref, ...props }) {      // React 19: ref llega como prop
  return <input ref={ref} {...props} />;
}

function App() {
  const campo = useRef(null);
  return <div><CampoTexto ref={campo} placeholder="Correo" /><button onClick={() => campo.current.focus()}>Enfocar</button></div>;
}""",
  h="enfoca un input que está dentro de un componente hijo",
  pr=("En versiones anteriores a React 19, la función para pasar refs era forward___ (3 letras)", "ref"),
  ec="intentar leer la ref de un componente que no la coloca en ningún elemento"),
]
