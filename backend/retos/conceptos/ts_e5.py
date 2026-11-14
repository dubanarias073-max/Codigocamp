"""TypeScript · Etapa 5: Práctica profesional."""
from ..generador import K

LISTA = [
K("tsconfig.json",
  d="archivo de configuración del compilador de TypeScript",
  u="definir cómo se compila el proyecto",
  mas="tsconfig.json indica carpetas, versión de JavaScript de salida y reglas de revisión. Se crea con tsc --init y se comparte con todo el equipo.",
  k=["tsconfig.json configura el compilador.", "Se crea con tsc --init.", "Define la salida y las reglas de revisión."],
  sit="Tu equipo necesita que todos compilen con las mismas reglas. ¿Qué archivo usas?",
  cod="""// tsconfig.json:  { "compilerOptions": { "target": "ES2020", "strict": true } }
console.log("Configuración compartida por todo el equipo");""",
  h="muestra un mensaje sobre la configuración compartida",
  pr=("El archivo de configuración de TypeScript se llama ___.json. (8 letras)", "tsconfig"),
  ec="compilar cada archivo con opciones distintas en cada equipo"),
K("Modo strict",
  d="opción que activa las comprobaciones más estrictas de tipos",
  u="detectar más errores antes de ejecutar",
  mas="\"strict\": true activa varias reglas a la vez, como no permitir null sin declararlo y no aceptar any implícito. Es la configuración recomendada para proyectos nuevos.",
  k=["strict activa las comprobaciones más estrictas.", "Impide null o undefined sin declararlos.", "Es recomendable en proyectos nuevos."],
  sit="Quieres que el compilador sea lo más exigente posible desde el inicio de un proyecto. ¿Qué activas?",
  cod="""// "strict": true  en tsconfig.json
let nombre: string = "Ana";   // con strict, nunca puede ser null sin declararlo
console.log(nombre);""",
  h="muestra una variable que con strict nunca será null",
  pr=("La opción que activa las comprobaciones estrictas es ___. (6 letras)", "strict"),
  ec="desactivar strict para evitar los errores en vez de corregirlos"),
K("async y await",
  d="sintaxis para escribir código asíncrono que se lee como secuencial",
  u="esperar resultados sin anidar callbacks",
  mas="Una función async siempre devuelve una Promise. Dentro de ella, await pausa hasta que otra Promise se resuelva y entrega su valor.",
  k=["async hace que una función devuelva una Promise.", "await espera el resultado de una Promise.", "await solo se usa dentro de funciones async."],
  sit="Necesitas esperar una respuesta antes de seguir con la siguiente línea, sin callbacks anidados. ¿Qué usas?",
  cod="""async function obtener(): Promise<number> { return 7; }
async function main() {
  const n = await obtener();   // espera el valor
  console.log("Recibido:", n);
}
main();""",
  h="espera un número de una función asíncrona y lo muestra",
  pr=("La palabra que espera una Promise es ___. (5 letras)", "await"),
  ec="usar await fuera de una función async",
  err=("function f() {\n  const x = await Promise.resolve(1);\n  return x;\n}", 2, "await solo puede usarse dentro de una función async.")),
K("try y catch",
  d="estructura que captura errores sin detener el programa",
  u="manejar fallos de forma controlada",
  mas="El código que puede fallar va en try. Si lanza un error, la ejecución salta a catch y allí se puede mostrar un mensaje o recuperar. finally se ejecuta siempre.",
  k=["try contiene el código que puede fallar.", "catch recibe el error y permite manejarlo.", "finally se ejecuta siempre."],
  sit="Un cálculo puede lanzar un error y no quieres que se caiga todo el programa. ¿Qué usas?",
  cod="""try {
  throw new Error("fallo simulado");   // código que puede fallar
} catch (e) {
  console.log("Error controlado");
} finally {
  console.log("Esto se ejecuta siempre");
}""",
  h="captura un error simulado sin romper el programa",
  pr=("El bloque que recibe el error es ___. (5 letras)", "catch"),
  ec="dejar el catch vacío y esconder los errores"),
K("Errores tipados",
  d="manejo de catch donde el error se trata como unknown",
  u="no asumir qué es lo que se lanzó",
  mas="Con strict, el error de catch es unknown porque en JavaScript se puede lanzar cualquier cosa. Comprueba con instanceof Error antes de leer su message.",
  k=["Con strict el error de catch es unknown.", "Hay que comprobar que es un Error antes de leer message.", "En JavaScript se puede lanzar cualquier valor."],
  sit="Dentro de catch quieres leer el mensaje del error con seguridad de tipos. ¿Qué haces?",
  cod="""try {
  throw new Error("algo falló");
} catch (e: unknown) {
  if (e instanceof Error) console.log(e.message);   // comprueba antes de usar
}""",
  h="muestra el mensaje solo si es un Error",
  pr=("Antes de leer message se comprueba con ___ Error. (instanceof)", "instanceof"),
  ec="leer e.message sin comprobar que e es un Error"),
K("Tipar respuestas JSON",
  d="definir la forma esperada de los datos que llegan de una API",
  u="trabajar con datos externos con ayuda del editor",
  mas="Los datos externos llegan sin tipo. Defines una interfaz con la forma esperada y la usas para tipar el resultado. TypeScript no valida el JSON real: conviene comprobarlo.",
  k=["Una interfaz describe la forma esperada del JSON.", "TypeScript no valida el JSON en tiempo de ejecución.", "Conviene comprobar los datos externos."],
  sit="Recibes un JSON de una API con id y nombre y quieres autocompletado al usarlo. ¿Qué haces?",
  cod="""interface Usuario { id: number; nombre: string }
const texto = '{"id":1,"nombre":"Ana"}';
const u = JSON.parse(texto) as Usuario;   // afirma la forma esperada
console.log(u.nombre);""",
  h="convierte un JSON de texto en un usuario tipado",
  pr=("El método que convierte texto JSON en objeto es JSON.___. (5 letras)", "parse"),
  ec="creer que as Usuario valida el contenido real del JSON"),
K("Archivos de declaración",
  d="archivos .d.ts que describen los tipos de código JavaScript",
  u="usar librerías de JavaScript con tipos",
  mas="Un archivo .d.ts contiene solo declaraciones de tipos, sin código. Permite que el editor entienda librerías escritas en JavaScript puro.",
  k=["Un archivo .d.ts contiene solo declaraciones de tipos.", "Permite tipar librerías escritas en JavaScript.", "No contiene código ejecutable."],
  sit="Usas una librería escrita en JavaScript y quieres autocompletado y tipos. ¿Qué necesitas?",
  cod="""// libreria.d.ts:  declare function saludar(nombre: string): string;
declare const version: string;
console.log("Los .d.ts solo describen tipos");""",
  h="muestra un mensaje sobre los archivos de declaración",
  pr=("Las declaraciones de tipos viven en archivos ___. (.d.ts)", ".d.ts", "d.ts"),
  ec="esperar que un .d.ts contenga código que se ejecuta"),
K("Paquetes @types",
  d="paquetes con los tipos de librerías que no los incluyen",
  u="añadir tipos a librerías de JavaScript desde npm",
  mas="Se instalan como npm install -D @types/nombre. Así librerías populares como lodash o node ganan tipos sin cambiar su código.",
  k=["@types agrupa tipos de librerías de la comunidad.", "Se instalan con npm como dependencia de desarrollo.", "Añaden tipos sin cambiar el código de la librería."],
  sit="Una librería popular de JavaScript no trae tipos y el editor no la entiende. ¿Qué instalas?",
  cod="""// npm install -D @types/node   // tipos de Node.js
console.log("Los @types añaden tipos a librerías existentes");""",
  h="muestra un mensaje sobre los paquetes @types",
  pr=("Los tipos de la comunidad se instalan con el prefijo ___/. (@types)", "@types"),
  ec="instalar @types de una librería que ya trae sus propios tipos"),
K("as const",
  d="aserción que fija un valor como literal e inmutable",
  u="obtener tipos literales exactos de un objeto o lista",
  mas="Con as const, los valores no se ensanchan a string o number: se conservan como literales y todo queda readonly. Muy útil para listas fijas de opciones.",
  k=["as const fija los valores como literales.", "Todo el valor queda como readonly.", "Sirve para listas fijas de opciones."],
  sit="Tienes una lista fija de colores y quieres que su tipo sea la unión exacta de esos textos. ¿Qué usas?",
  cod="""const colores = ["rojo", "verde", "azul"] as const;   // tipos literales
type Color = (typeof colores)[number];
const c: Color = "rojo";
console.log(c);""",
  h="obtiene un tipo con los colores permitidos de una lista fija",
  pr=("La aserción que fija un valor literal e inmutable es as ___. (5 letras)", "const"),
  ec="intentar modificar un array declarado con as const"),
K("satisfies",
  d="operador que comprueba un valor contra un tipo sin ensanchar su tipo",
  u="validar la forma de un objeto sin perder los tipos específicos",
  mas="valor satisfies Tipo verifica que el valor cumple el tipo pero conserva el tipo exacto del valor. A diferencia de una anotación, no lo ensancha.",
  k=["satisfies valida un valor contra un tipo.", "Conserva el tipo exacto del valor.", "Evita ensanchar el tipo como haría una anotación."],
  sit="Quieres comprobar que un objeto cumple un tipo pero conservar los tipos exactos de sus propiedades. ¿Qué usas?",
  cod="""type Paleta = Record<string, string | number[]>;
const p = { rojo: [255, 0, 0], verde: "#0f0" } satisfies Paleta;   // valida sin ensanchar
console.log(p.rojo.length);""",
  h="valida una paleta de colores conservando sus tipos",
  pr=("El operador que valida sin ensanchar el tipo es ___. (9 letras)", "satisfies"),
  ec="usar una anotación y perder los tipos específicos"),
K("Operador !",
  d="aserción de no nulo que afirma que un valor no es null ni undefined",
  u="indicar que sabes que existe un valor que TypeScript duda",
  mas="valor! le dice al compilador que confíe en ti. Si el valor sí es null, el programa fallará al ejecutar. Úsalo solo cuando estés completamente seguro.",
  k=["El operador ! afirma que el valor no es null ni undefined.", "Si te equivocas, el error ocurre al ejecutar.", "Solo conviene usarlo cuando estás seguro."],
  sit="Estás seguro de que un valor existe pero TypeScript cree que puede ser null. ¿Qué operador usas, con cuidado?",
  cod="""const nombres: string[] = ["Ana", "Luis"];
const primero = nombres.find((n) => n === "Ana")!;   // afirma que existe
console.log(primero.length);""",
  h="busca un nombre y afirma que existe",
  pr=("La aserción de no nulo se escribe con el signo ___. (!)", "!"),
  ec="usar ! para silenciar un posible null que sí puede ocurrir"),
K("ReturnType",
  d="tipo utilitario que obtiene el tipo que devuelve una función",
  u="reutilizar el tipo de retorno sin repetirlo",
  mas="ReturnType<typeof funcion> extrae el tipo de lo que devuelve esa función. Si cambias la función, el tipo se actualiza solo.",
  k=["ReturnType obtiene el tipo de retorno de una función.", "Se usa junto con typeof.", "El tipo se actualiza si cambia la función."],
  sit="Quieres un tipo igual al resultado de una función sin escribirlo a mano. ¿Qué utilitario usas?",
  cod="""function crearUsuario() { return { id: 1, nombre: "Ana" }; }
type Usuario = ReturnType<typeof crearUsuario>;   // { id: number; nombre: string }
const u: Usuario = crearUsuario();
console.log(u);""",
  h="obtiene el tipo del resultado de una función",
  pr=("El utilitario que obtiene el tipo de retorno es ___Type. (6 letras)", "return"),
  ec="escribir a mano el tipo y olvidar actualizarlo al cambiar la función"),
K("Parameters",
  d="tipo utilitario que obtiene los tipos de los parámetros de una función",
  u="reutilizar la firma de una función",
  mas="Parameters<typeof funcion> devuelve una tupla con los tipos de los parámetros, en orden. Es útil para envolver funciones sin repetir su firma.",
  k=["Parameters obtiene los tipos de los parámetros.", "Devuelve una tupla con los tipos en orden.", "Sirve para envolver funciones sin repetir la firma."],
  sit="Quieres envolver una función y que tu envoltorio acepte exactamente los mismos parámetros. ¿Qué utilitario usas?",
  cod="""function sumar(a: number, b: number): number { return a + b; }
type Args = Parameters<typeof sumar>;   // [a: number, b: number]
const args: Args = [2, 3];
console.log(sumar(...args));""",
  h="reutiliza los parámetros de una función para llamarla",
  pr=("El utilitario que obtiene los tipos de los parámetros es ___. (10 letras)", "parameters"),
  ec="cambiar la función y no actualizar el tipo de sus parámetros"),
K("Awaited",
  d="tipo utilitario que obtiene el tipo resultante de una Promise",
  u="saber qué tipo entrega un await",
  mas="Awaited<Promise<number>> da number. Resuelve también promesas anidadas. Es útil con ReturnType cuando una función async devuelve una Promise.",
  k=["Awaited obtiene el tipo que entrega una Promise.", "Resuelve promesas anidadas.", "Se combina con ReturnType en funciones async."],
  sit="Una función async devuelve Promise<Usuario> y quieres el tipo Usuario solo. ¿Qué utilitario usas?",
  cod="""async function cargar() { return { id: 1 }; }
type Datos = Awaited<ReturnType<typeof cargar>>;   // { id: number }
const d: Datos = { id: 2 };
console.log(d);""",
  h="obtiene el tipo que entrega una función async",
  pr=("El utilitario que quita la Promise del tipo es ___. (7 letras)", "awaited"),
  ec="usar Promise<T> donde en realidad se necesita T"),
K("ESLint",
  d="herramienta que revisa el estilo y los problemas del código",
  u="mantener un código limpio y coherente",
  mas="ESLint encuentra errores y malas prácticas más allá de los tipos, como variables sin usar o any innecesarios. Con typescript-eslint entiende TypeScript.",
  k=["ESLint revisa el estilo y los problemas del código.", "Detecta malas prácticas más allá de los tipos.", "typescript-eslint lo adapta a TypeScript."],
  sit="Tu equipo quiere que todo el código siga las mismas reglas de estilo y evite malas prácticas. ¿Qué herramienta usa?",
  cod="""// npm install -D eslint typescript-eslint
const sinUsar = 1;   // ESLint avisaría: variable sin usar
console.log("ESLint revisa el estilo");""",
  h="muestra un mensaje sobre la revisión con ESLint",
  pr=("La herramienta que revisa el estilo del código es ___. (6 letras)", "eslint"),
  ec="ignorar las advertencias de ESLint"),
K("Pruebas",
  d="código que comprueba automáticamente que tu programa funciona",
  u="detectar errores al cambiar el código",
  mas="Una prueba llama a una función con datos conocidos y comprueba el resultado esperado. Herramientas como Jest o Vitest las ejecutan en segundos.",
  k=["Una prueba comprueba automáticamente un comportamiento.", "Compara el resultado real con el esperado.", "Jest y Vitest ejecutan pruebas."],
  sit="Cada vez que cambias código temes romper algo ya hecho. ¿Qué práctica te protege?",
  cod="""function sumar(a: number, b: number): number { return a + b; }
const esperado = 5;
console.log(sumar(2, 3) === esperado ? "prueba superada" : "prueba fallida");""",
  h="comprueba que la suma da el valor esperado",
  pr=("El código que comprueba automáticamente tu programa es una ___. (6 letras)", "prueba", "test"),
  ec="cambiar el código sin ninguna prueba que lo respalde"),
K("Migrar JavaScript a TypeScript",
  d="proceso de pasar poco a poco un proyecto JavaScript a TypeScript",
  u="ganar seguridad de tipos sin reescribir todo",
  mas="Se activa allowJs, se renombran archivos de .js a .ts de uno en uno y se añaden tipos progresivamente. No hace falta convertir todo de golpe.",
  k=["Migrar es pasar un proyecto de JavaScript a TypeScript.", "Se puede hacer poco a poco.", "allowJs permite mezclar archivos .js y .ts."],
  sit="Tienes un proyecto JavaScript grande y no puedes reescribirlo de una vez. ¿Cómo avanzas?",
  cod="""// 1. allowJs: true   2. renombrar un archivo .js a .ts   3. añadir tipos poco a poco
let total: number = 0;
console.log(total);""",
  h="muestra un valor ya tipado como primer paso de migración",
  pr=("La opción que permite mezclar archivos .js y .ts es ___. (allowJs)", "allowjs"),
  ec="intentar convertir un proyecto grande de una sola vez"),
K("Evitar any",
  d="buena práctica de reemplazar any por tipos precisos",
  u="mantener la protección de TypeScript",
  mas="Cada any deja un hueco en la revisión. Prefiere unknown con comprobación, genéricos o interfaces. Activa la regla no-explicit-any para que el equipo lo evite.",
  k=["Cada any elimina la protección del tipado.", "unknown con comprobación es una alternativa más segura.", "La regla no-explicit-any ayuda a evitar any."],
  sit="Tu código está lleno de any y los errores aparecen al ejecutar. ¿Qué buena práctica aplicas?",
  cod="""function mostrar(valor: unknown): void {   // mejor unknown que any
  if (typeof valor === "string") console.log(valor);
  else console.log("no es texto");
}
mostrar("hola");
mostrar(5);""",
  h="trata distintos valores sin usar any",
  pr=("La alternativa segura a any es ___. (7 letras)", "unknown"),
  ec="usar any por comodidad cada vez que aparece un error de tipos"),
K("Eventos del DOM",
  d="tipos que describen los eventos y elementos de una página web",
  u="escribir código del navegador con ayuda del editor",
  mas="Elementos como HTMLInputElement y eventos como MouseEvent dan autocompletado. Algunas funciones, como querySelector, pueden devolver null y hay que comprobarlo.",
  k=["TypeScript incluye tipos para elementos y eventos del DOM.", "querySelector puede devolver null.", "Los tipos del DOM dan autocompletado."],
  sit="Quieres leer el valor de un campo de texto de la página con autocompletado y seguridad. ¿Qué haces?",
  cod="""// const campo = document.querySelector("input") as HTMLInputElement;
// console.log(campo.value);
console.log("Los tipos del DOM, como HTMLInputElement, dan autocompletado");""",
  h="muestra un mensaje sobre los tipos del DOM",
  pr=("El tipo de un campo de texto del DOM es HTML___Element. (Input)", "input"),
  ec="usar el resultado de querySelector sin comprobar que no sea null"),
K("Compilar para producción",
  d="generar el JavaScript final optimizado para publicar la aplicación",
  u="entregar un resultado listo para ejecutar sin TypeScript",
  mas="En producción se ejecuta el JavaScript generado, no los .ts. Se compila con tsc o con una herramienta como esbuild o Vite, y se publica la carpeta de salida.",
  k=["En producción se ejecuta el JavaScript generado.", "Se compila con tsc o herramientas como Vite.", "Se publica la carpeta de salida, no los archivos .ts."],
  sit="Tu aplicación ya está lista y debes publicarla. ¿Qué entregas al servidor?",
  cod="""// npm run build   -> compila a la carpeta dist/
console.log("Se publica dist/, no el código .ts");""",
  h="muestra un mensaje sobre qué se publica en producción",
  pr=("En producción se publica el código ___. (JavaScript)", "javascript"),
  ec="subir al servidor los archivos .ts sin compilar"),
]
