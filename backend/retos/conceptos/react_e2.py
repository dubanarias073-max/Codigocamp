"""React · Etapa 2: Estado e interactividad."""
from ..generador import K

LISTA = [
K("useState",
  d="hook que guarda un dato que puede cambiar y vuelve a dibujar el componente",
  u="recordar valores como un contador, un texto escrito o si un menú está abierto",
  mas="useState devuelve un par: el valor actual y una función para cambiarlo. Cuando llamas a esa función, React vuelve a ejecutar el componente con el valor nuevo y actualiza la pantalla.",
  k=["useState guarda un dato que cambia con el tiempo.", "useState devuelve el valor y una función para cambiarlo.", "Al cambiar el estado, React vuelve a dibujar el componente."],
  sit="Quieres un contador que suba cada vez que pulsas un botón y que el número cambie en la pantalla. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [cuenta, setCuenta] = useState(0);   // valor inicial: 0
  return <button onClick={() => setCuenta(cuenta + 1)}>Clics: {cuenta}</button>;
}""",
  h="cuenta los clics en un botón con useState",
  pr=("El hook que guarda un dato que cambia se llama ___. (8 letras)", "usestate"),
  pr2=("useState devuelve un arreglo con el valor y una función para ___ (9 letras)", "cambiarlo", "actualizarlo"),
  ec="cambiar la variable directamente (cuenta = cuenta + 1) en vez de usar la función set"),
K("Variables normales vs estado",
  d="diferencia entre una variable común, que se reinicia, y el estado, que React recuerda",
  u="entender por qué una variable let no actualiza la pantalla",
  mas="Cada vez que React dibuja un componente vuelve a ejecutar la función, así que las variables let empiezan de cero. Además, cambiarlas no avisa a React. El estado se conserva entre dibujos y sí provoca un nuevo dibujo.",
  k=["Las variables normales se reinician en cada dibujo del componente.", "Cambiar una variable normal no actualiza la pantalla.", "El estado se conserva entre dibujos y actualiza la pantalla."],
  sit="Usaste let contador = 0 y contador++ en el clic, pero el número en pantalla nunca cambia. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  let normal = 0;                          // se reinicia en cada dibujo
  const [estado, setEstado] = useState(0); // React lo recuerda
  return (
    <button onClick={() => { normal++; setEstado(estado + 1); }}>
      normal: {normal} · estado: {estado}
    </button>
  );
}""",
  h="compara una variable normal con una de estado al hacer clic",
  pr=("Una variable let dentro del componente se ___ en cada dibujo. (9 letras)", "reinicia"),
  ec="usar variables let para datos que deben verse actualizados en pantalla"),
K("Formularios controlados",
  d="input cuyo valor vive en el estado y se actualiza con onChange",
  u="leer y validar lo que escribe la persona mientras escribe",
  mas="En un input controlado value={texto} viene del estado y onChange={e => setTexto(e.target.value)} lo actualiza. Así el estado es la única fuente de verdad y puedes validar, limpiar o transformar el texto.",
  k=["En un input controlado el valor viene del estado.", "onChange actualiza el estado con e.target.value.", "Un input con value pero sin onChange queda bloqueado."],
  sit="Quieres mostrar debajo del input, letra por letra, lo que la persona va escribiendo. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [nombre, setNombre] = useState("");
  return (
    <div>
      <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Tu nombre" />
      <p>Hola, {nombre || "…"}</p>
    </div>
  );
}""",
  h="muestra lo que se escribe en un input controlado",
  pr=("En onChange, el texto escrito se lee con e.target.___ (5 letras)", "value"),
  ec="poner value en un input sin onChange y que no deje escribir"),
K("Estado con objetos",
  d="guardar varios datos relacionados en un objeto dentro del estado",
  u="manejar un formulario con varios campos en un solo estado",
  mas="Para cambiar una parte del objeto no se modifica el original: se crea uno nuevo copiando el anterior con ...spread y cambiando solo la propiedad: setForm({ ...form, correo: valor }).",
  k=["Para cambiar un objeto del estado se crea uno nuevo.", "El spread ...form copia las propiedades del objeto anterior.", "Mutar el objeto del estado directamente no actualiza la pantalla."],
  sit="Tu formulario tiene nombre, correo y edad, y quieres guardarlos juntos y cambiar solo el campo que se edita. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [form, setForm] = useState({ nombre: "", correo: "" });
  const cambiar = (e) => setForm({ ...form, [e.target.name]: e.target.value });   // copia y cambia uno
  return (
    <div>
      <input name="nombre" value={form.nombre} onChange={cambiar} placeholder="Nombre" />
      <input name="correo" value={form.correo} onChange={cambiar} placeholder="Correo" />
      <pre>{JSON.stringify(form)}</pre>
    </div>
  );
}""",
  h="guarda un formulario de dos campos en un objeto del estado",
  pr=("Para copiar un objeto antes de cambiarlo se usan tres ___ (6 letras)", "puntos"),
  ec="hacer form.nombre = valor directamente sobre el objeto del estado"),
K("Estado con arreglos",
  d="guardar listas en el estado y cambiarlas creando arreglos nuevos",
  u="agregar, quitar y editar elementos de una lista de tareas",
  mas="Para agregar se usa [...lista, nuevo]; para quitar, lista.filter; para editar, lista.map. Nunca push, splice o sort sobre el arreglo del estado, porque lo modifican en lugar de crear uno nuevo.",
  k=["Para agregar a un arreglo del estado se usa [...lista, nuevo].", "Para quitar elementos del estado se usa filter.", "push y splice modifican el arreglo y no deben usarse con el estado."],
  sit="Tienes una lista de tareas en el estado y quieres agregar una nueva y borrar otra sin modificar el arreglo original. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [tareas, setTareas] = useState(["Estudiar"]);
  const agregar = () => setTareas([...tareas, `Tarea ${tareas.length + 1}`]);   // nuevo arreglo
  const quitar = (t) => setTareas(tareas.filter((x) => x !== t));
  return (
    <div>
      <button onClick={agregar}>Agregar</button>
      <ul>{tareas.map((t) => <li key={t} onClick={() => quitar(t)}>{t} ✖</li>)}</ul>
    </div>
  );
}""",
  h="agrega y quita tareas de una lista en el estado",
  pr=("Para quitar elementos de un arreglo del estado se usa el método ___. (6 letras)", "filter"),
  ec="usar push sobre el arreglo del estado y esperar que se actualice"),
K("Actualización funcional",
  d="pasar una función a set para calcular el valor nuevo a partir del anterior",
  u="sumar varias veces seguidas sin perder actualizaciones",
  mas="setCuenta(c => c + 1) recibe el valor más reciente. Si llamas tres veces a setCuenta(cuenta + 1) en el mismo clic solo suma uno, porque cuenta es el mismo valor las tres veces; con la forma funcional suma tres.",
  k=["setCuenta(c => c + 1) usa el valor más reciente del estado.", "La forma funcional evita perder actualizaciones seguidas.", "Llamar varias veces a setCuenta(cuenta + 1) en el mismo clic suma solo una vez."],
  sit="Quieres que un botón «+3» llame tres veces a sumar uno, pero el contador solo sube de a uno. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [n, setN] = useState(0);
  const mas3 = () => {
    setN((v) => v + 1);   // cada llamada recibe el valor más nuevo
    setN((v) => v + 1);
    setN((v) => v + 1);
  };
  return <button onClick={mas3}>Valor: {n} (+3)</button>;
}""",
  h="suma tres al contador usando la forma funcional de set",
  pr=("A setN se le puede pasar una ___ que recibe el valor anterior. (7 letras)", "funcion", "función"),
  ec="hacer varias actualizaciones seguidas con el mismo valor viejo del estado"),
K("onSubmit y preventDefault",
  d="manejar el envío de un formulario sin que la página se recargue",
  u="procesar los datos del formulario con JavaScript",
  mas="El evento onSubmit va en la etiqueta form y se dispara al pulsar el botón o Enter. Lo primero es llamar e.preventDefault(), que evita la recarga de la página del navegador.",
  k=["onSubmit se pone en la etiqueta form.", "e.preventDefault() evita que la página se recargue al enviar.", "onSubmit también se dispara al pulsar Enter en un campo."],
  sit="Al enviar tu formulario de React la página se recarga y se pierde todo lo escrito. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [enviado, setEnviado] = useState("");
  const enviar = (e) => {
    e.preventDefault();                         // sin recargar la página
    setEnviado(new FormData(e.target).get("correo"));
  };
  return (
    <form onSubmit={enviar}>
      <input name="correo" type="email" required placeholder="correo@ejemplo.com" />
      <button>Suscribirme</button>
      {enviado && <p>Suscrito: {enviado}</p>}
    </form>
  );
}""",
  h="envía un formulario sin recargar la página",
  pr=("Para que el formulario no recargue la página se llama a e.___() (14 letras)", "preventdefault"),
  ec="poner onClick en el botón y olvidar que Enter también envía el formulario"),
K("Checkbox y select",
  d="inputs controlados que usan checked o value según el tipo",
  u="manejar casillas, opciones y listas desplegables en formularios",
  mas="Un checkbox controlado usa checked={valor} y en onChange se lee e.target.checked. Un select controlado usa value en la etiqueta select, igual que un input de texto.",
  k=["Un checkbox controlado usa checked en lugar de value.", "En un checkbox se lee e.target.checked.", "Un select controlado usa value en la etiqueta select."],
  sit="Tu formulario tiene una casilla «Acepto los términos» y una lista para elegir el país, y quieres guardarlas en el estado. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [acepto, setAcepto] = useState(false);
  const [pais, setPais] = useState("co");
  return (
    <div>
      <label><input type="checkbox" checked={acepto} onChange={(e) => setAcepto(e.target.checked)} /> Acepto</label>
      <select value={pais} onChange={(e) => setPais(e.target.value)}>
        <option value="co">Colombia</option><option value="mx">México</option>
      </select>
      <p>{acepto ? "✔" : "✖"} · {pais}</p>
    </div>
  );
}""",
  h="guarda una casilla y una lista desplegable en el estado",
  pr=("En un checkbox controlado se lee e.target.___ (7 letras)", "checked"),
  ec="leer e.target.value en un checkbox en lugar de checked"),
K("Levantar el estado",
  d="mover el estado al componente padre para que varios hijos lo compartan",
  u="sincronizar dos componentes que necesitan el mismo dato",
  mas="Si dos hermanos necesitan el mismo dato, el estado sube a su padre común. El padre pasa el valor por props y también la función para cambiarlo. Así hay una sola fuente de verdad.",
  k=["Levantar el estado es moverlo al padre común.", "El padre pasa el valor y la función para cambiarlo por props.", "Levantar el estado deja una sola fuente de verdad."],
  sit="Un buscador y una lista son hermanos, y la lista debe filtrarse con lo que se escribe en el buscador. ¿Qué usarías?",
  cod="""import { useState } from "react";

const Buscador = ({ texto, alCambiar }) => <input value={texto} onChange={(e) => alCambiar(e.target.value)} placeholder="Buscar" />;
const Lista = ({ texto }) => <ul>{["React", "Vue", "Svelte"].filter((x) => x.toLowerCase().includes(texto.toLowerCase())).map((x) => <li key={x}>{x}</li>)}</ul>;

function App() {
  const [texto, setTexto] = useState("");   // el estado vive en el padre
  return <><Buscador texto={texto} alCambiar={setTexto} /><Lista texto={texto} /></>;
}""",
  h="comparte el texto de búsqueda entre dos componentes hermanos",
  pr=("Cuando dos hermanos comparten un dato, el estado se sube al componente ___. (5 letras)", "padre"),
  ec="duplicar el mismo estado en dos componentes y que se desincronicen"),
K("Estado derivado",
  d="valor que se calcula a partir del estado en lugar de guardarse aparte",
  u="evitar estados duplicados que se desincronizan",
  mas="Si un dato se puede calcular con lo que ya tienes, no lo guardes en otro useState. Por ejemplo, el total de un carrito se calcula con reduce en cada dibujo. Menos estados, menos errores.",
  k=["El estado derivado se calcula en cada dibujo.", "No hace falta un useState para datos que se pueden calcular.", "Guardar datos calculables en el estado causa desincronización."],
  sit="Guardas los productos del carrito y además el total en otro useState, y a veces el total no coincide. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [carrito, setCarrito] = useState([{ n: "Libro", p: 30 }, { n: "Lápiz", p: 2 }]);
  const total = carrito.reduce((s, x) => s + x.p, 0);   // derivado: se calcula, no se guarda
  return (
    <div>
      <button onClick={() => setCarrito([...carrito, { n: "Borrador", p: 1 }])}>Agregar borrador</button>
      <p>{carrito.length} productos · Total ${total}</p>
    </div>
  );
}""",
  h="calcula el total del carrito a partir del estado",
  pr=("Un valor que se calcula a partir del estado se llama estado ___. (8 letras)", "derivado"),
  ec="guardar en el estado un dato que se puede calcular"),
K("Componentes puros",
  d="componentes que con las mismas props y estado siempre muestran lo mismo",
  u="que React pueda dibujar sin sorpresas ni efectos inesperados",
  mas="Un componente puro no cambia variables de afuera ni hace peticiones mientras se dibuja: solo calcula su JSX. Los cambios se hacen en eventos o en efectos. StrictMode dibuja dos veces en desarrollo para detectar impurezas.",
  k=["Un componente puro devuelve lo mismo con las mismas entradas.", "Un componente puro no modifica variables de afuera al dibujarse.", "StrictMode ayuda a encontrar componentes que no son puros."],
  sit="Tu componente suma 1 a una variable global cada vez que se dibuja y el número sale distinto cada vez. ¿Qué usarías?",
  cod="""let visitas = 0;   // ❌ variable de afuera

function Mal() { visitas++; return <p>Mal: {visitas}</p>; }   // cambia algo de afuera al dibujar
function Bien({ n }) { return <p>Bien: {n * 2}</p>; }       // ✅ solo calcula con sus props

function App() {
  return <><Bien n={4} /><Mal /></>;
}""",
  h="compara un componente puro con uno que modifica una variable externa",
  pr=("Un componente que con las mismas props muestra lo mismo es ___. (4 letras)", "puro"),
  ec="hacer peticiones o cambiar variables globales mientras el componente se dibuja"),
K("Inmutabilidad",
  d="regla de no modificar los datos del estado y crear copias nuevas",
  u="que React detecte los cambios y actualice la pantalla",
  mas="React compara la referencia anterior con la nueva: si mutas el mismo objeto, la referencia no cambia y React puede no actualizar. Por eso se crean copias con spread, map o filter.",
  k=["React detecta cambios comparando referencias.", "Mutar el estado puede hacer que la pantalla no se actualice.", "La inmutabilidad se logra creando copias con spread, map o filter."],
  sit="Haces usuario.puntos += 10 y luego setUsuario(usuario), pero la pantalla no cambia. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [u, setU] = useState({ nombre: "Ana", puntos: 0 });
  // ✅ copia nueva con el cambio (no u.puntos += 10)
  const sumar = () => setU({ ...u, puntos: u.puntos + 10 });
  return <button onClick={sumar}>{u.nombre}: {u.puntos} puntos</button>;
}""",
  h="suma puntos creando un objeto nuevo en lugar de mutarlo",
  pr=("La regla de no modificar los datos del estado se llama ___. (13 letras)", "inmutabilidad"),
  ec="mutar el objeto y llamar a set con la misma referencia"),
K("Pasar argumentos a eventos",
  d="usar una función flecha para enviar datos al manejador de un evento",
  u="saber qué elemento de una lista se pulsó",
  mas="onClick={() => borrar(id)} crea una función que, al hacer clic, llama a borrar con el id. Sin la flecha, borrar(id) se ejecutaría al dibujar.",
  k=["Para pasar argumentos a un evento se usa una función flecha.", "onClick={() => borrar(id)} llama a borrar solo al hacer clic.", "onClick={borrar(id)} se ejecuta al dibujar, no al hacer clic."],
  sit="Cada fila de tu lista tiene un botón «Eliminar» y necesitas saber el id de la fila que se pulsó. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [items, setItems] = useState([{ id: 1, n: "Pan" }, { id: 2, n: "Leche" }]);
  const borrar = (id) => setItems(items.filter((x) => x.id !== id));
  return (
    <ul>
      {items.map((x) => (
        <li key={x.id}>{x.n} <button onClick={() => borrar(x.id)}>Eliminar</button></li>   // flecha con el id
      ))}
    </ul>
  );
}""",
  h="borra el elemento cuyo botón se pulsó",
  pr=("Para pasar un argumento en onClick se envuelve la llamada en una función ___. (6 letras)", "flecha"),
  ec="escribir onClick={borrar(x.id)} y que se borre todo al dibujar"),
K("Varios estados",
  d="usar más de un useState en un mismo componente",
  u="separar datos independientes, como el texto y si hay un error",
  mas="Cada llamada a useState crea un estado independiente. Conviene separar los datos que cambian por separado y agrupar en un objeto los que siempre cambian juntos.",
  k=["Un componente puede tener varios useState.", "Cada useState guarda un dato independiente.", "Los datos que cambian juntos pueden agruparse en un objeto."],
  sit="Tu formulario necesita guardar lo escrito, si está cargando y si hubo un error, y son cosas que cambian por separado. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [correo, setCorreo] = useState("");
  const [error, setError] = useState("");      // otro estado independiente
  const validar = () => setError(correo.includes("@") ? "" : "Falta la @");
  return (
    <div>
      <input value={correo} onChange={(e) => setCorreo(e.target.value)} onBlur={validar} placeholder="Correo" />
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </div>
  );
}""",
  h="usa dos estados: el correo y su mensaje de error",
  pr=("Un mismo componente puede llamar a useState ___ veces. (6 letras)", "varias", "muchas"),
  ec="meter en un solo objeto datos que no tienen nada que ver"),
K("Reiniciar con key",
  d="cambiar la key de un componente para que React lo cree de nuevo",
  u="limpiar el estado de un formulario al cambiar de persona",
  mas="Si la key de un componente cambia, React lo trata como uno nuevo: borra el anterior con su estado y crea otro desde cero. Es la forma limpia de reiniciar un formulario.",
  k=["Si cambia la key, React vuelve a crear el componente.", "Al cambiar la key se pierde el estado anterior del componente.", "key sirve para reiniciar un formulario al cambiar de elemento."],
  sit="Al pasar de un contacto a otro en tu chat, el borrador escrito para el anterior se queda en el input. ¿Qué usarías?",
  cod="""import { useState } from "react";

function Borrador() {
  const [t, setT] = useState("");
  return <input value={t} onChange={(e) => setT(e.target.value)} placeholder="Escribe…" />;
}

function App() {
  const [para, setPara] = useState("Ana");
  return (
    <div>
      <button onClick={() => setPara(para === "Ana" ? "Luis" : "Ana")}>Chat con {para}</button>
      <Borrador key={para} />   {/* otra key = componente nuevo */}
    </div>
  );
}""",
  h="reinicia el borrador al cambiar de contacto usando key",
  pr=("Para que React cree de nuevo un componente se le cambia la ___. (3 letras)", "key"),
  ec="intentar limpiar el estado a mano con efectos en lugar de usar key"),
K("Renderizado",
  d="proceso en que React ejecuta el componente para calcular qué mostrar",
  u="entender cuándo y por qué se actualiza la pantalla",
  mas="React dibuja al iniciar y cada vez que cambia el estado del componente o de su padre. Primero calcula el JSX y después cambia en el DOM solo lo que es distinto. Dibujar no es lo mismo que tocar el DOM.",
  k=["React vuelve a dibujar un componente cuando cambia su estado.", "Si un padre se vuelve a dibujar, sus hijos también.", "React solo cambia en el DOM lo que es distinto."],
  sit="Quieres entender por qué tu componente se ejecuta otra vez cada vez que escribes una letra. ¿Qué concepto revisarías?",
  cod="""import { useState } from "react";

function App() {
  const [t, setT] = useState("");
  console.log("Dibujando App con:", t);   // se ve en la consola en cada cambio
  return <input value={t} onChange={(e) => setT(e.target.value)} placeholder="Escribe y mira la consola" />;
}""",
  h="muestra en la consola cada vez que el componente se dibuja",
  pr=("Cuando React ejecuta el componente para calcular qué mostrar, se llama ___. (11 letras)", "renderizado", "render"),
  ec="creer que React reemplaza toda la página en cada cambio"),
K("Actualizaciones en lote",
  d="React agrupa varios cambios de estado en un solo dibujo",
  u="que varias actualizaciones seguidas no hagan dibujar varias veces",
  mas="Si en un clic cambias tres estados, React espera a que termine el manejador y dibuja una sola vez. Por eso, justo después de set, la variable todavía tiene el valor viejo.",
  k=["React agrupa los cambios de estado de un mismo evento.", "Después de llamar a set, la variable aún tiene el valor anterior.", "Agrupar actualizaciones evita dibujos innecesarios."],
  sit="Haces setN(5) y en la línea siguiente console.log(n) sigue mostrando el valor viejo. ¿Qué concepto lo explica?",
  cod="""import { useState } from "react";

function App() {
  const [n, setN] = useState(0);
  const [color, setColor] = useState("gray");
  const clic = () => {
    setN(n + 1);
    setColor("teal");
    console.log("n todavía vale", n);   // valor viejo: el cambio llega en el próximo dibujo
  };
  return <button style={{ color }} onClick={clic}>n = {n}</button>;
}""",
  h="cambia dos estados en un clic y React dibuja una sola vez",
  pr=("React agrupa varios cambios de estado en un solo ___ (6 letras)", "dibujo", "render"),
  ec="esperar que la variable de estado cambie en la línea siguiente a set"),
K("Estado vs props",
  d="las props vienen del padre y el estado es propio del componente",
  u="decidir dónde guardar cada dato",
  mas="Las props son como los parámetros de una función: llegan de afuera y no se cambian. El estado es la memoria del componente y solo él lo cambia. Un estado de un padre suele llegar como prop a sus hijos.",
  k=["Las props llegan del componente padre.", "El estado es propio del componente y solo él lo cambia.", "El estado de un padre puede llegar como prop a un hijo."],
  sit="No sabes si guardar el nombre de usuario como estado del componente Perfil o recibirlo de App. ¿Qué diferencia revisarías?",
  cod="""import { useState } from "react";

function Insignia({ nivel }) {            // prop: viene del padre
  return <span>⭐ Nivel {nivel}</span>;
}

function App() {
  const [nivel, setNivel] = useState(1);   // estado: propio de App
  return <button onClick={() => setNivel(nivel + 1)}><Insignia nivel={nivel} /></button>;
}""",
  h="pasa un estado del padre como prop al hijo",
  pr=("El dato propio de un componente que puede cambiar se llama ___. (6 letras)", "estado", "state"),
  ec="copiar una prop en un useState y que deje de actualizarse"),
K("Mostrar y ocultar",
  d="alternar la visibilidad de una parte de la interfaz con un estado booleano",
  u="abrir y cerrar menús, modales o respuestas",
  mas="Un estado true o false decide si algo se muestra. Para alternar se usa setAbierto(a => !a). Al ocultar con && el componente se quita del todo y pierde su estado; con CSS solo se esconde.",
  k=["Un estado booleano controla si algo se muestra.", "setAbierto(a => !a) alterna entre verdadero y falso.", "Ocultar con && quita el componente y su estado."],
  sit="Quieres un botón «Ver respuesta» que muestre y esconda la solución de un ejercicio. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [ver, setVer] = useState(false);
  return (
    <div>
      <button onClick={() => setVer((v) => !v)}>{ver ? "Ocultar" : "Ver"} respuesta</button>
      {ver && <p>La respuesta es 42 ✨</p>}
    </div>
  );
}""",
  h="muestra y oculta una respuesta con un botón",
  pr=("Para alternar un booleano se usa el operador de negación ___ (1 carácter)", "!"),
  ec="usar dos estados distintos para abierto y cerrado"),
K("Contador con límites",
  d="validar el nuevo valor antes de guardarlo en el estado",
  u="impedir valores inválidos, como cantidades negativas",
  mas="Antes de llamar a set puedes revisar el valor: Math.max y Math.min ayudan a dejarlo dentro de un rango. También puedes deshabilitar los botones con disabled cuando se llega al límite.",
  k=["Antes de guardar un valor en el estado se puede validar.", "Math.max y Math.min mantienen un número dentro de un rango.", "disabled desactiva un botón cuando se llega al límite."],
  sit="Tu selector de cantidad del carrito deja bajar a -3 productos y subir a 999. ¿Qué usarías?",
  cod="""import { useState } from "react";

function App() {
  const [c, setC] = useState(1);
  const cambiar = (d) => setC((v) => Math.min(10, Math.max(1, v + d)));   // entre 1 y 10
  return (
    <div>
      <button onClick={() => cambiar(-1)} disabled={c === 1}>−</button>
      <b> {c} </b>
      <button onClick={() => cambiar(1)} disabled={c === 10}>+</button>
    </div>
  );
}""",
  h="mantiene una cantidad entre 1 y 10",
  pr=("El atributo que desactiva un botón al llegar al límite es ___. (8 letras)", "disabled"),
  ec="guardar cualquier valor en el estado sin validarlo"),
]
