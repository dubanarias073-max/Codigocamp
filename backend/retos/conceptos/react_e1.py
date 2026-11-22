"""React · Etapa 1: Primeros pasos (componentes, JSX y props)."""
from ..generador import K

LISTA = [
K("Qué es React",
  d="biblioteca de JavaScript para construir interfaces con componentes",
  u="crear páginas interactivas dividiéndolas en piezas reutilizables",
  mas="React lo creó Meta y hoy es la forma más usada de hacer interfaces web. Describes cómo se ve la pantalla según los datos y React se encarga de actualizar solo lo que cambia en el navegador.",
  k=["React es una biblioteca de JavaScript para interfaces.", "React divide la pantalla en componentes reutilizables.", "React actualiza solo las partes de la página que cambian."],
  sit="Tu página tiene muchas partes que se repiten y cambian con los datos, y actualizar el DOM a mano se volvió un caos. ¿Qué usarías?",
  cod="""// Un componente de React: una función que devuelve lo que se ve
function App() {
  return <h1>¡Hola desde React!</h1>;   // esto es JSX
}""",
  h="muestra un título creado con un componente de React",
  pr=("React es una ___ de JavaScript para interfaces. (10 letras)", "biblioteca", "libreria", "librería"),
  ec="pensar que React es un lenguaje distinto de JavaScript"),
K("Componente",
  d="función que devuelve una parte de la interfaz",
  u="armar la página con piezas pequeñas que se pueden reutilizar",
  mas="Un componente es una función de JavaScript cuyo nombre empieza con mayúscula y que devuelve JSX. Se usa como si fuera una etiqueta: <Tarjeta />. Una página grande se arma juntando componentes pequeños.",
  k=["Un componente es una función que devuelve JSX.", "El nombre de un componente empieza con mayúscula.", "Un componente se usa como una etiqueta: <Saludo />."],
  sit="Tienes el mismo botón con estilo en diez partes de tu página y quieres escribirlo una sola vez. ¿Qué usarías?",
  cod="""function Boton() {                      // componente: nombre con mayúscula
  return <button>Comprar</button>;
}

function App() {
  return (
    <div>
      <Boton />   {/* se usa como una etiqueta */}
      <Boton />
    </div>
  );
}""",
  h="crea un componente Boton y lo usa dos veces",
  pr=("El nombre de un componente empieza con letra ___. (8 letras)", "mayuscula", "mayúscula"),
  pr2=("Un componente se usa como una etiqueta que se cierra así: <Boton ___ (2 caracteres)", "/>"),
  ec="escribir el nombre del componente en minúscula, que React confunde con una etiqueta HTML"),
K("JSX",
  d="sintaxis que mezcla HTML dentro de JavaScript",
  u="describir la interfaz de forma clara dentro del componente",
  mas="JSX parece HTML pero es JavaScript: herramientas como Vite lo convierten en llamadas a React. Debe devolver un solo elemento raíz, todas las etiquetas se cierran y algunos atributos cambian de nombre.",
  k=["JSX parece HTML pero se convierte en JavaScript.", "En JSX todas las etiquetas deben cerrarse, incluso <img />.", "JSX devuelve un solo elemento raíz."],
  sit="Quieres escribir la estructura de tu componente con etiquetas parecidas a HTML en lugar de crear elementos con document.createElement. ¿Qué usarías?",
  cod="""function App() {
  // JSX: parece HTML, pero está dentro de JavaScript
  return (
    <section>
      <h2>Mi tienda</h2>
      <img src="https://picsum.photos/120" alt="Producto" />  {/* se cierra con /> */}
    </section>
  );
}""",
  h="muestra un título y una imagen escritos con JSX",
  pr=("La sintaxis que mezcla etiquetas con JavaScript en React se llama ___. (3 letras)", "jsx"),
  ec="dejar etiquetas sin cerrar como <img> o <br> en JSX"),
K("Crear un proyecto con Vite",
  d="herramienta que crea y arranca un proyecto de React en segundos",
  u="empezar un proyecto con servidor de desarrollo y recarga instantánea",
  mas="Con npm create vite@latest eliges React y obtienes una carpeta lista. Después npm install descarga las dependencias y npm run dev abre el servidor de desarrollo, que recarga la página al guardar.",
  k=["Vite crea proyectos de React con npm create vite@latest.", "npm run dev arranca el servidor de desarrollo de Vite.", "Vite recarga la página al guardar los archivos."],
  sit="Vas a empezar un proyecto nuevo de React y quieres un servidor que recargue al guardar, sin configurar nada a mano. ¿Qué usarías?",
  cod="""// En la terminal:
//   npm create vite@latest mi-app -- --template react
//   cd mi-app && npm install && npm run dev
function App() {
  return <p>Proyecto creado con Vite ⚡</p>;
}""",
  h="muestra el mensaje de un proyecto creado con Vite",
  pr=("El comando que arranca el servidor de desarrollo es npm run ___. (3 letras)", "dev"),
  ec="abrir el archivo index.html directamente sin npm run dev"),
K("createRoot",
  d="función que conecta React con un elemento del HTML",
  u="mostrar la aplicación de React dentro de la página",
  mas="En main.jsx se busca el div con id root y se crea la raíz con createRoot de react-dom/client. Luego render dibuja el componente principal. Solo se hace una vez por aplicación.",
  k=["createRoot viene de react-dom/client.", "createRoot recibe el elemento donde vivirá la app.", "render dibuja el componente principal dentro de la raíz."],
  sit="Ya tienes tu componente App, pero todavía no aparece en la página porque falta conectarlo con el div del HTML. ¿Qué usarías?",
  cod="""import { createRoot } from "react-dom/client";

function App() {
  return <h1>App conectada</h1>;
}

// main.jsx: conecta React con <div id="root"> del index.html
createRoot(document.getElementById("root")).render(<App />);""",
  h="conecta el componente App con el div root de la página",
  pr=("createRoot se importa de react-dom/___. (6 letras)", "client"),
  ec="llamar a createRoot varias veces sobre el mismo elemento"),
K("Expresiones con llaves",
  d="forma de poner valores de JavaScript dentro de JSX usando { }",
  u="mostrar variables, cálculos y resultados de funciones en la interfaz",
  mas="Dentro de las llaves puedes poner cualquier expresión: variables, operaciones, llamadas a funciones o ternarios. No caben sentencias como if o for, pero sí su versión en expresión.",
  k=["Las llaves { } muestran valores de JavaScript en JSX.", "Dentro de las llaves van expresiones, no sentencias como if.", "Las llaves también sirven en atributos: src={url}."],
  sit="Quieres mostrar en el título el nombre guardado en una variable y el total de una suma. ¿Qué usarías?",
  cod="""function App() {
  const nombre = "Ana";
  const precio = 20, cantidad = 3;
  return (
    <div>
      <h2>Hola, {nombre}</h2>                 {/* variable */}
      <p>Total: ${precio * cantidad}</p>   {/* cálculo */}
    </div>
  );
}""",
  h="muestra un nombre y un total calculado con llaves",
  pr=("Para mostrar una variable en JSX se escribe entre ___. (6 letras)", "llaves"),
  ec="poner un if dentro de las llaves en lugar de un ternario"),
K("className",
  d="atributo de JSX para asignar clases de CSS",
  u="dar estilos de una hoja CSS a los elementos del componente",
  mas="En JSX no se usa class porque es una palabra reservada de JavaScript: se usa className. Igual pasa con for, que en JSX es htmlFor. El valor puede ser texto o una expresión entre llaves.",
  k=["En JSX las clases se ponen con className.", "class es palabra reservada de JavaScript, por eso JSX usa className.", "En JSX el atributo for de un label se escribe htmlFor."],
  sit="Copiaste HTML con class=\"tarjeta\" a tu componente y React muestra una advertencia. ¿Qué usarías?",
  cod="""function App() {
  return (
    <div className="tarjeta">          {/* className, no class */}
      <label htmlFor="correo">Correo</label>
      <input id="correo" />
    </div>
  );
}""",
  h="usa className y htmlFor en lugar de class y for",
  pr=("En JSX, el atributo for de un label se escribe ___. (7 letras)", "htmlfor"),
  pr2=("En JSX, las clases de CSS se asignan con ___. (9 letras)", "classname"),
  ec="escribir class en lugar de className en JSX"),
K("Estilos en línea",
  d="atributo style que recibe un objeto de JavaScript",
  u="cambiar estilos según datos, como un color que depende del estado",
  mas="En JSX style no es texto: es un objeto con las propiedades en camelCase. Por eso se ven dobles llaves: las de afuera son de JSX y las de adentro son del objeto. Los números se toman como píxeles.",
  k=["style recibe un objeto de JavaScript, no un texto.", "Las propiedades de style van en camelCase, como backgroundColor.", "En style={{ }} las llaves de afuera son de JSX y las de adentro del objeto."],
  sit="Quieres que el fondo de una tarjeta cambie de color según una variable, directamente en el componente. ¿Qué usarías?",
  cod="""function App() {
  const urgente = true;
  return (
    <p style={{ backgroundColor: urgente ? "tomato" : "lightgreen", padding: 12 }}>
      {urgente ? "¡Urgente!" : "Todo bien"}   {/* padding: 12 = 12px */}
    </p>
  );
}""",
  h="pinta el fondo de rojo o verde según una variable",
  pr=("Las propiedades de style se escriben en ___ (backgroundColor). (9 letras)", "camelcase"),
  ec="escribir style=\"color: red\" como texto en JSX"),
K("Fragmentos",
  d="contenedor vacío <>...</> que agrupa elementos sin agregar etiquetas al HTML",
  u="devolver varios elementos sin envolverlos en un div extra",
  mas="Un componente solo puede devolver un elemento raíz. El fragmento <></> agrupa varios sin crear nada en la página. Si necesitas ponerle key, usa la forma larga <Fragment key=...>.",
  k=["Un fragmento <></> agrupa elementos sin crear un div.", "Los fragmentos resuelven la regla de un solo elemento raíz.", "Para ponerle key a un fragmento se usa <Fragment>."],
  sit="Tu componente devuelve un título y un párrafo, React da error, y no quieres agregar un div que rompa tu diseño. ¿Qué usarías?",
  cod="""function App() {
  return (
    <>                       {/* fragmento: no aparece en el HTML */}
      <h2>Título</h2>
      <p>Dos elementos sin div extra</p>
    </>
  );
}""",
  h="devuelve dos elementos agrupados en un fragmento",
  pr=("El contenedor vacío <></> se llama ___. (9 letras)", "fragmento", "fragment"),
  ec="devolver dos elementos sueltos sin envolverlos en un fragmento"),
K("Props",
  d="datos que un componente padre le pasa a un componente hijo",
  u="personalizar un mismo componente con valores distintos",
  mas="Las props se escriben como atributos al usar el componente y llegan como un objeto en el primer parámetro. Es común desestructurarlas: function Tarjeta({ titulo }). Son de solo lectura: el hijo no las cambia.",
  k=["Las props pasan datos del componente padre al hijo.", "Las props llegan como un objeto en el parámetro del componente.", "Un componente no debe modificar sus props."],
  sit="Tienes un componente Saludo y quieres que diga «Hola, Ana» en un lugar y «Hola, Luis» en otro. ¿Qué usarías?",
  cod="""function Saludo({ nombre }) {          // la prop llega desestructurada
  return <p>Hola, {nombre} 👋</p>;
}

function App() {
  return (
    <>
      <Saludo nombre="Ana" />
      <Saludo nombre="Luis" />
    </>
  );
}""",
  h="usa el mismo componente con dos nombres distintos",
  pr=("Los datos que el padre le pasa al hijo se llaman ___. (5 letras)", "props"),
  pr2=("Las props son de solo ___: el hijo no las cambia. (7 letras)", "lectura"),
  ec="intentar cambiar una prop dentro del componente hijo"),
K("children",
  d="prop especial con lo que se escribe entre la etiqueta de apertura y cierre",
  u="crear componentes contenedores como tarjetas o ventanas",
  mas="Todo lo que pongas dentro de <Tarjeta>...</Tarjeta> llega al componente como props.children. Así un mismo marco puede envolver cualquier contenido.",
  k=["children contiene lo que va entre las etiquetas del componente.", "children sirve para crear componentes que envuelven contenido.", "children se recibe como cualquier otra prop."],
  sit="Quieres un componente Tarjeta con borde y sombra que pueda envolver cualquier contenido distinto cada vez. ¿Qué usarías?",
  cod="""function Tarjeta({ children }) {        // lo de adentro llega en children
  return <div style={{ border: "2px solid #61dafb", padding: 12, borderRadius: 12 }}>{children}</div>;
}

function App() {
  return (
    <Tarjeta>
      <h3>Curso de React</h3>
      <p>Contenido dentro de la tarjeta</p>
    </Tarjeta>
  );
}""",
  h="envuelve un título y un párrafo con un componente Tarjeta",
  pr=("La prop con el contenido entre las etiquetas se llama ___. (8 letras)", "children"),
  ec="pasar el contenido como prop con otro nombre y olvidar mostrar children"),
K("Renderizado condicional",
  d="mostrar u ocultar partes de la interfaz según una condición",
  u="mostrar un mensaje solo si se cumple algo, como estar conectado",
  mas="En JSX se usa el ternario condicion ? a : b para elegir entre dos cosas, y condicion && elemento para mostrar algo solo si es verdadero. Cuidado: con && un 0 se muestra en pantalla.",
  k=["El ternario elige entre dos elementos en JSX.", "condicion && elemento muestra el elemento solo si es verdadero.", "Con && el número 0 aparece en pantalla, por eso conviene comparar."],
  sit="Quieres mostrar «Bienvenido» si la persona inició sesión y un botón «Entrar» si no. ¿Qué usarías?",
  cod="""function App() {
  const conectado = false;
  const mensajes = 3;
  return (
    <div>
      {conectado ? <p>Bienvenido 🎉</p> : <button>Entrar</button>}   {/* ternario */}
      {mensajes > 0 && <p>Tienes {mensajes} mensajes</p>}           {/* solo si es verdadero */}
    </div>
  );
}""",
  h="muestra un botón o un saludo según una condición",
  pr=("Para mostrar algo solo si es verdadero se usa el operador ___. (2 caracteres)", "&&"),
  ec="usar cantidad && elemento y que aparezca un 0 en pantalla"),
K("Listas con map",
  d="convertir un arreglo de datos en una lista de elementos con map",
  u="mostrar productos, tareas o mensajes que vienen en un arreglo",
  mas="map recorre el arreglo y devuelve un elemento JSX por cada dato. React muestra el arreglo resultante. Cada elemento de la lista necesita una prop key única.",
  k=["map convierte cada dato del arreglo en un elemento JSX.", "React puede mostrar arreglos de elementos.", "Cada elemento creado con map necesita una key."],
  sit="Tienes un arreglo con diez productos y quieres mostrar un <li> por cada uno sin escribirlos a mano. ¿Qué usarías?",
  cod="""function App() {
  const frutas = ["Mango", "Fresa", "Uva"];
  return (
    <ul>
      {frutas.map((f) => <li key={f}>{f}</li>)}   {/* un <li> por fruta */}
    </ul>
  );
}""",
  h="muestra una lista con un elemento por cada fruta",
  pr=("El método que convierte un arreglo en elementos JSX es ___. (3 letras)", "map"),
  ec="usar forEach, que no devuelve nada, en lugar de map"),
K("key",
  d="identificador único que React usa para reconocer cada elemento de una lista",
  u="que React actualice bien la lista cuando se agregan o borran elementos",
  mas="La key debe ser única entre hermanos y estable: lo ideal es el id del dato. Usar el índice puede causar errores cuando la lista se reordena o se borra un elemento del medio.",
  k=["key identifica cada elemento de una lista en React.", "La key debe ser única entre los hermanos de la lista.", "Es mejor usar el id del dato como key que el índice."],
  sit="React muestra la advertencia «Each child in a list should have a unique prop» en tu lista de tareas. ¿Qué usarías?",
  cod="""function App() {
  const tareas = [{ id: 7, texto: "Estudiar" }, { id: 9, texto: "Programar" }];
  return (
    <ul>
      {tareas.map((t) => (
        <li key={t.id}>{t.texto}</li>   // key única y estable: el id
      ))}
    </ul>
  );
}""",
  h="muestra tareas usando su id como key",
  pr=("La prop que identifica cada elemento de una lista es ___. (3 letras)", "key"),
  ec="usar el índice del arreglo como key en listas que cambian de orden"),
K("Eventos onClick",
  d="atributo que ejecuta una función cuando se hace clic",
  u="responder a lo que hace la persona, como pulsar un botón",
  mas="Los eventos en JSX van en camelCase (onClick, onChange, onSubmit) y reciben una función, no su resultado. Escribe onClick={saludar}, no onClick={saludar()}, porque así se ejecutaría al dibujar.",
  k=["Los eventos de JSX se escriben en camelCase, como onClick.", "onClick recibe una función, no el resultado de llamarla.", "onClick={saludar()} ejecuta la función al dibujar, no al hacer clic."],
  sit="Quieres que aparezca un mensaje cuando la persona pulse el botón «Saludar». ¿Qué usarías?",
  cod="""function App() {
  function saludar() {
    alert("¡Hola! 👋");
  }
  return <button onClick={saludar}>Saludar</button>;   // sin paréntesis
}""",
  h="muestra un mensaje al hacer clic en el botón",
  pr=("El evento de clic en JSX se escribe ___. (7 letras)", "onclick"),
  pr2=("onClick debe recibir una ___, no su resultado. (7 letras)", "funcion", "función"),
  ec="escribir onClick={saludar()} y que se ejecute al dibujar"),
K("Exportar e importar componentes",
  d="separar cada componente en su archivo y usarlo con import",
  u="organizar un proyecto grande en archivos pequeños",
  mas="Con export default function Boton() el archivo exporta su componente principal y otro archivo lo trae con import Boton from './Boton'. También hay exports con nombre: export function Icono() que se importan con llaves.",
  k=["export default exporta el componente principal de un archivo.", "Los exports con nombre se importan con llaves.", "Separar componentes en archivos ordena el proyecto."],
  sit="Tu archivo App.jsx tiene 600 líneas con diez componentes y quieres poner cada uno en su archivo. ¿Qué usarías?",
  cod="""// Boton.jsx:  export default function Boton() { ... }
// App.jsx:    import Boton from "./Boton";
function Boton({ texto }) {
  return <button>{texto}</button>;
}

export default function App() {
  return <Boton texto="Importado de otro archivo" />;
}""",
  h="usa un componente que vendría de otro archivo",
  pr=("Para exportar el componente principal de un archivo se escribe export ___. (7 letras)", "default"),
  ec="importar con llaves un componente exportado con export default"),
K("Imágenes y recursos",
  d="importar imágenes y archivos para usarlos en los componentes",
  u="mostrar logos y fotos que forman parte del proyecto",
  mas="En Vite puedes importar una imagen: import logo from './logo.png' y usarla en src={logo}. Los archivos de la carpeta public se usan con una ruta absoluta como /icono.png.",
  k=["En Vite una imagen se puede importar como un módulo.", "La imagen importada se usa en src con llaves.", "Los archivos de public se usan con una ruta que empieza con /."],
  sit="Quieres mostrar el logo.png que está en la carpeta src de tu proyecto de React. ¿Qué usarías?",
  cod="""// import logo from "./logo.png";   ->   <img src={logo} />
const logo = "https://picsum.photos/80";   // aquí usamos una imagen de internet

function App() {
  return <img src={logo} alt="Logo de mi app" width={80} />;
}""",
  h="muestra una imagen usando su ruta en src",
  pr=("Las imágenes que se usan con ruta absoluta (/foto.png) van en la carpeta ___. (6 letras)", "public"),
  ec="olvidar el atributo alt en las imágenes"),
K("Comentarios en JSX",
  d="notas dentro del JSX escritas como {/* comentario */}",
  u="explicar partes de la interfaz sin que se muestren",
  mas="Dentro del JSX no sirve <!-- -->: el comentario va entre llaves y con /* */. Fuera del JSX, en el JavaScript normal, se usan // y /* */ como siempre.",
  k=["En JSX los comentarios se escriben {/* así */}.", "<!-- --> de HTML no funciona dentro de JSX.", "Fuera del JSX se comenta con // como en JavaScript."],
  sit="Quieres dejar una nota dentro del JSX explicando una sección, pero <!-- --> aparece como texto. ¿Qué usarías?",
  cod="""function App() {
  // comentario normal de JavaScript
  return (
    <main>
      {/* comentario dentro del JSX: no se ve en la página */}
      <p>Solo se ve este párrafo</p>
    </main>
  );
}""",
  h="usa comentarios que no aparecen en la página",
  pr=("Dentro del JSX, un comentario va entre llaves y /* ... ___ (2 caracteres)", "*/"),
  ec="usar <!-- --> de HTML para comentar dentro de JSX"),
K("Composición de componentes",
  d="armar componentes grandes juntando componentes pequeños",
  u="mantener cada pieza simple y fácil de cambiar",
  mas="En React no se hereda de otros componentes: se componen. Una Página usa una Cabecera, una Lista y un Pie, y cada uno hace una sola cosa. Así es fácil probar y reutilizar cada parte.",
  k=["En React los componentes se componen, no se heredan.", "La composición junta componentes pequeños en uno grande.", "Cada componente debería hacer una sola cosa."],
  sit="Tu componente Pagina hace de todo y es difícil de leer; quieres separarlo en Cabecera, Contenido y Pie. ¿Qué usarías?",
  cod="""const Cabecera = () => <header><h2>CódigoCamp</h2></header>;
const Contenido = () => <p>Aprende React paso a paso.</p>;
const Pie = () => <footer><small>© 2026</small></footer>;

function App() {                // la página se compone de piezas pequeñas
  return (
    <>
      <Cabecera />
      <Contenido />
      <Pie />
    </>
  );
}""",
  h="arma una página juntando tres componentes pequeños",
  pr=("En React los componentes se combinan mediante ___. (11 letras)", "composicion", "composición"),
  ec="hacer un componente gigante que hace todo en vez de dividirlo"),
K("React Developer Tools",
  d="extensión del navegador para inspeccionar componentes, props y estado",
  u="encontrar errores viendo qué datos tiene cada componente",
  mas="React Developer Tools agrega las pestañas Components y Profiler a las herramientas del navegador. Ahí ves el árbol de componentes, sus props y su estado en vivo, y puedes cambiarlos para probar.",
  k=["React Developer Tools muestra el árbol de componentes.", "En React Developer Tools ves las props y el estado de cada componente.", "La pestaña Profiler mide qué componentes tardan en dibujarse."],
  sit="Un componente muestra un dato equivocado y quieres ver qué props y estado tiene en este momento. ¿Qué usarías?",
  cod="""// Instala la extensión «React Developer Tools» y abre F12 > Components
function Perfil({ nombre, nivel }) {
  return <p>{nombre} · nivel {nivel}</p>;   // en Components verás nombre y nivel
}

function App() {
  return <Perfil nombre="Ana" nivel={3} />;
}""",
  h="muestra un perfil cuyas props se pueden revisar en las herramientas",
  pr=("La pestaña de React Developer Tools con el árbol de componentes se llama ___. (10 letras)", "components"),
  ec="depurar todo con console.log sin mirar el árbol de componentes"),
]
