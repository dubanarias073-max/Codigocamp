"""TypeScript · Etapa 4: Genéricos y tipos avanzados."""
from ..generador import K

LISTA = [
K("Genéricos",
  d="tipos con parámetros que se concretan al usarlos",
  u="escribir código reutilizable que conserva el tipo",
  mas="Un genérico se escribe entre ángulos, como <T>. T funciona como una variable de tipo: se decide al usar la función o la clase, y TypeScript recuerda ese tipo en todo el código.",
  k=["Un genérico es un tipo con parámetro, como <T>.", "El tipo concreto se decide al usarlo.", "Los genéricos permiten reutilizar código sin perder el tipo."],
  sit="Quieres una función que devuelva lo mismo que recibe, sea del tipo que sea, sin perder el tipo. ¿Qué usas?",
  cod="""function identidad<T>(valor: T): T {   // T es el tipo variable
  return valor;
}
console.log(identidad<number>(5), identidad("hola"));""",
  h="devuelve el mismo valor de cualquier tipo",
  pr=("Un parámetro de tipo genérico se escribe entre ___. (<>)", "<>", "angulos", "ángulos"),
  ec="usar any en lugar de un genérico y perder el tipo"),
K("Funciones genéricas",
  d="funciones con parámetros de tipo propios",
  u="operar sobre varios tipos con una sola función",
  mas="Pones <T> después del nombre. TypeScript puede inferir T según el argumento, así que normalmente no hace falta indicarlo al llamar.",
  k=["Una función genérica declara <T> tras su nombre.", "T suele inferirse del argumento.", "Una sola función sirve para muchos tipos."],
  sit="Quieres obtener el primer elemento de cualquier lista, y que el resultado tenga el tipo de sus elementos. ¿Qué escribes?",
  cod="""function primero<T>(lista: T[]): T {   // lista de T, devuelve T
  return lista[0];
}
console.log(primero([10, 20]), primero(["a", "b"]));""",
  h="obtiene el primer elemento de listas de distintos tipos",
  pr=("En <T>, la T representa un ___. (tipo)", "tipo"),
  ec="indicar el tipo a mano cuando TypeScript ya lo infiere"),
K("Interfaces genéricas",
  d="interfaces que dependen de un tipo parámetro",
  u="describir estructuras que cambian según el tipo de dato",
  mas="interface Caja<T> { contenido: T } describe una caja de cualquier cosa. Al usarla se indica el tipo: Caja<string> o Caja<number>.",
  k=["Una interfaz genérica recibe un tipo parámetro.", "Al usarla se indica el tipo entre ángulos.", "Sirve para estructuras que contienen distintos tipos."],
  sit="Necesitas una «caja» que pueda guardar un número en un caso y un texto en otro. ¿Qué declaras?",
  cod="""interface Caja<T> { contenido: T }   // T se decide al usarla
const a: Caja<number> = { contenido: 5 };
const b: Caja<string> = { contenido: "hola" };
console.log(a.contenido, b.contenido);""",
  h="crea cajas de número y de texto con la misma interfaz",
  pr=("Una interfaz genérica se usa como Caja___. (<tipo>)", "<tipo>", "<number>", "<string>"),
  ec="olvidar indicar el tipo al usar una interfaz genérica"),
K("Restricciones con extends",
  d="límite que obliga a que el tipo genérico cumpla cierta forma",
  u="usar propiedades concretas dentro de una función genérica",
  mas="<T extends { length: number }> acepta solo tipos con length. Así dentro de la función puedes usar valor.length con seguridad.",
  k=["extends restringe los tipos que acepta un genérico.", "Permite usar propiedades del tipo restringido.", "Un tipo que no cumple la restricción da error."],
  sit="Tu función genérica necesita leer length, así que solo debe aceptar tipos que lo tengan. ¿Qué agregas?",
  cod="""function largo<T extends { length: number }>(v: T): number {   // exige length
  return v.length;
}
console.log(largo("hola"), largo([1, 2, 3]));""",
  h="mide el largo de textos y de listas",
  pr=("La restricción de un genérico usa la palabra ___. (7 letras)", "extends"),
  ec="llamar a una función restringida con un tipo que no tiene la propiedad exigida",
  err=("function largo<T extends { length: number }>(v: T) { return v.length; }\nconsole.log(largo(5));", 2, "Un número no tiene la propiedad length.")),
K("keyof",
  d="operador que obtiene las claves de un tipo como unión de textos",
  u="limitar valores a los nombres de propiedades existentes",
  mas="keyof Persona da \"nombre\" | \"edad\". Combinado con genéricos permite funciones que reciben un objeto y el nombre de una de sus propiedades.",
  k=["keyof obtiene los nombres de las propiedades de un tipo.", "El resultado es una unión de textos literales.", "Se combina con genéricos para leer propiedades con seguridad."],
  sit="Quieres una función que reciba un objeto y el nombre de una de sus propiedades, pero solo nombres válidos. ¿Qué usas?",
  cod="""type Persona = { nombre: string; edad: number };
type Claves = keyof Persona;   // "nombre" | "edad"
const k: Claves = "edad";
console.log(k);""",
  h="obtiene las claves válidas de un tipo",
  pr=("El operador que obtiene las claves de un tipo es ___. (5 letras)", "keyof"),
  ec="escribir un nombre de propiedad que no existe en el tipo"),
K("typeof en tipos",
  d="uso de typeof para obtener el tipo de una variable existente",
  u="reutilizar el tipo de un valor sin escribirlo a mano",
  mas="En posición de tipo, typeof variable da el tipo de esa variable. Evita duplicar definiciones cuando ya tienes un objeto de ejemplo.",
  k=["typeof en un tipo obtiene el tipo de una variable.", "Evita duplicar definiciones de tipo.", "Es útil cuando ya existe un objeto de ejemplo."],
  sit="Tienes un objeto de configuración y quieres un tipo con su misma forma sin escribirlo otra vez. ¿Qué usas?",
  cod="""const config = { modo: "oscuro", tamano: 14 };
type Config = typeof config;   // { modo: string; tamano: number }
const otra: Config = { modo: "claro", tamano: 12 };
console.log(otra);""",
  h="obtiene el tipo de un objeto existente",
  pr=("Para obtener el tipo de una variable existente se usa ___. (6 letras)", "typeof"),
  ec="escribir a mano un tipo que ya se puede obtener de un valor"),
K("Partial",
  d="tipo utilitario que vuelve opcionales todas las propiedades",
  u="representar cambios parciales de un objeto",
  mas="Partial<T> crea un tipo igual a T pero con todas las propiedades opcionales. Es común en funciones de actualización donde solo llegan algunos campos.",
  k=["Partial<T> vuelve opcionales todas las propiedades.", "Es útil para actualizaciones parciales.", "Partial no cambia el tipo original."],
  sit="Al actualizar un usuario solo llegan algunos campos, no todos. ¿Qué tipo utilitario usas?",
  cod="""type Usuario = { nombre: string; edad: number };
const cambios: Partial<Usuario> = { edad: 21 };   // nombre es opcional ahora
console.log(cambios);""",
  h="describe un cambio que solo trae la edad",
  pr=("El tipo utilitario que vuelve opcionales todas las propiedades es ___. (7 letras)", "partial"),
  ec="creer que Partial modifica el tipo original"),
K("Required",
  d="tipo utilitario que vuelve obligatorias todas las propiedades",
  u="exigir que no falte ningún dato opcional",
  mas="Required<T> es lo contrario de Partial: quita el ? de todas las propiedades. Sirve para formularios completos que ya se validaron.",
  k=["Required<T> vuelve obligatorias todas las propiedades.", "Es lo contrario de Partial.", "Quita el ? de las propiedades opcionales."],
  sit="Un tipo tiene campos opcionales, pero para guardar necesitas que estén todos. ¿Qué utilitario usas?",
  cod="""type Perfil = { nombre?: string; edad?: number };
const completo: Required<Perfil> = { nombre: "Ana", edad: 20 };   // todo obligatorio
console.log(completo);""",
  h="exige un perfil con todos sus campos",
  pr=("El tipo que vuelve obligatorias todas las propiedades es ___. (8 letras)", "required"),
  ec="olvidar un campo cuando se usa Required"),
K("Readonly<T>",
  d="tipo utilitario que vuelve de solo lectura todas las propiedades",
  u="proteger un objeto completo contra cambios",
  mas="Readonly<T> añade readonly a cada propiedad. Es una protección solo de TypeScript: no impide los cambios en tiempo de ejecución.",
  k=["Readonly<T> vuelve de solo lectura todas las propiedades.", "Protege un objeto completo en compilación.", "No impide cambios en tiempo de ejecución."],
  sit="Quieres que una configuración completa no pueda modificarse una vez creada. ¿Qué tipo usas?",
  cod="""type Ajustes = { tema: string; idioma: string };
const a: Readonly<Ajustes> = { tema: "oscuro", idioma: "es" };   // todo de solo lectura
console.log(a);""",
  h="crea unos ajustes de solo lectura",
  pr=("El tipo que vuelve de solo lectura un objeto es ___<T>. (8 letras)", "readonly"),
  ec="creer que Readonly protege el objeto también al ejecutar"),
K("Pick",
  d="tipo utilitario que toma solo algunas propiedades de un tipo",
  u="crear un tipo más pequeño con las propiedades necesarias",
  mas="Pick<T, \"a\" | \"b\"> crea un tipo con solo esas propiedades. Es útil para mostrar solo ciertos datos de un objeto grande.",
  k=["Pick<T, claves> toma solo las claves indicadas.", "El resultado es un tipo más pequeño.", "Las claves se indican como texto o unión de textos."],
  sit="Un tipo Usuario tiene muchos campos y para una lista solo necesitas el nombre. ¿Qué utilitario usas?",
  cod="""type Usuario = { id: number; nombre: string; clave: string };
type Resumen = Pick<Usuario, "id" | "nombre">;   // solo id y nombre
const r: Resumen = { id: 1, nombre: "Ana" };
console.log(r);""",
  h="crea un resumen con solo id y nombre",
  pr=("El utilitario que elige algunas propiedades es ___. (4 letras)", "pick"),
  ec="indicar una clave que no existe en el tipo"),
K("Omit",
  d="tipo utilitario que quita algunas propiedades de un tipo",
  u="excluir datos sensibles o innecesarios",
  mas="Omit<T, \"clave\"> crea un tipo igual a T sin esas propiedades. Es lo opuesto a Pick y es ideal para no exponer, por ejemplo, contraseñas.",
  k=["Omit<T, claves> quita las claves indicadas.", "Es lo opuesto a Pick.", "Sirve para excluir datos sensibles."],
  sit="Quieres devolver un usuario pero sin su contraseña. ¿Qué utilitario usas?",
  cod="""type Usuario = { id: number; nombre: string; clave: string };
type Publico = Omit<Usuario, "clave">;   // sin clave
const p: Publico = { id: 1, nombre: "Ana" };
console.log(p);""",
  h="crea un usuario público sin contraseña",
  pr=("El utilitario que quita propiedades de un tipo es ___. (4 letras)", "omit"),
  ec="confundir Omit con Pick"),
K("Record",
  d="tipo utilitario para objetos con claves y valores de un tipo fijo",
  u="describir diccionarios o tablas de búsqueda",
  mas="Record<K, V> describe un objeto cuyas claves son de tipo K y sus valores de tipo V. Con claves literales obliga a incluirlas todas.",
  k=["Record<K, V> describe un diccionario tipado.", "Todas las claves son de tipo K.", "Todos los valores son de tipo V."],
  sit="Quieres guardar el precio de cada fruta usando el nombre como clave. ¿Qué tipo usas?",
  cod="""const precios: Record<string, number> = { manzana: 1.2, pera: 0.9 };   // clave texto, valor número
console.log(precios["pera"]);""",
  h="guarda el precio de dos frutas por nombre",
  pr=("El utilitario para diccionarios clave-valor es ___. (6 letras)", "record"),
  ec="usar un valor del tipo equivocado en un Record"),
K("Tipos condicionales",
  d="tipos que eligen una alternativa según una condición con extends",
  u="calcular un tipo a partir de otro",
  mas="La forma es T extends U ? X : Y: si T encaja en U, el tipo es X; si no, es Y. Es como un if, pero entre tipos.",
  k=["Un tipo condicional elige un tipo según una condición.", "Se escribe con extends, ? y :.", "Funciona como un if entre tipos."],
  sit="Quieres un tipo que sea «sí» si T es texto y «no» en cualquier otro caso. ¿Qué escribes?",
  cod="""type EsTexto<T> = T extends string ? "sí" : "no";   // if entre tipos
const a: EsTexto<string> = "sí";
const b: EsTexto<number> = "no";
console.log(a, b);""",
  h="decide un tipo según sea texto o no",
  pr=("En un tipo condicional, la condición usa la palabra ___. (7 letras)", "extends"),
  ec="confundir la condición de tipos con un if de valores"),
K("Tipos mapeados",
  d="tipos que transforman cada propiedad de otro tipo",
  u="crear variantes de un tipo aplicando una regla a todas sus propiedades",
  mas="Se escribe { [K in keyof T]: ... } y recorre cada propiedad. Los utilitarios Partial y Readonly se construyen así.",
  k=["Un tipo mapeado recorre las propiedades de un tipo.", "Se escribe con [K in keyof T].", "Partial y Readonly son tipos mapeados."],
  sit="Quieres una versión de un tipo donde todas las propiedades sean booleanas. ¿Qué técnica usas?",
  cod="""type Persona = { nombre: string; edad: number };
type Banderas = { [K in keyof Persona]: boolean };   // cada propiedad pasa a boolean
const b: Banderas = { nombre: true, edad: false };
console.log(b);""",
  h="convierte todas las propiedades de un tipo en booleanas",
  pr=("En un tipo mapeado se recorre con [K ___ keyof T]. (2 letras)", "in"),
  ec="olvidar keyof y recorrer algo que no son claves"),
K("Uniones discriminadas",
  d="uniones de objetos que comparten una propiedad literal distintiva",
  u="distinguir con seguridad entre variantes de un mismo dato",
  mas="Cada variante tiene una propiedad como tipo: \"circulo\" o tipo: \"cuadrado\". Un switch sobre esa propiedad permite a TypeScript saber qué campos existen en cada caso.",
  k=["Una unión discriminada comparte una propiedad literal.", "El switch sobre esa propiedad acota el tipo.", "Permite saber qué campos existen en cada variante."],
  sit="Una figura puede ser círculo (radio) o cuadrado (lado) y quieres tratar cada una con seguridad. ¿Qué usas?",
  cod="""type Figura = { tipo: "circulo"; radio: number } | { tipo: "cuadrado"; lado: number };
function area(f: Figura): number {
  switch (f.tipo) {   // acota según tipo
    case "circulo": return Math.PI * f.radio ** 2;
    case "cuadrado": return f.lado ** 2;
  }
}
console.log(area({ tipo: "cuadrado", lado: 3 }));""",
  h="calcula el área de una figura que puede ser círculo o cuadrado",
  pr=("La propiedad compartida que identifica cada variante se llama ___. (13 letras: discriminante)", "discriminante"),
  ec="olvidar la propiedad que distingue las variantes"),
K("Guardas de tipo",
  d="funciones que indican a TypeScript qué tipo tiene un valor",
  u="acotar tipos con una comprobación propia",
  mas="Una guarda devuelve un predicado como valor is string. Si devuelve true, TypeScript trata el valor como ese tipo en el bloque siguiente.",
  k=["Una guarda de tipo usa un predicado como valor is Tipo.", "Si devuelve true, el valor se acota a ese tipo.", "Permite crear comprobaciones propias reutilizables."],
  sit="Quieres una función reutilizable que compruebe si un valor es un texto y avise a TypeScript. ¿Qué escribes?",
  cod="""function esTexto(v: unknown): v is string {   // predicado de tipo
  return typeof v === "string";
}
const x: unknown = "hola";
if (esTexto(x)) console.log(x.toUpperCase());""",
  h="comprueba con una guarda que un valor es texto",
  pr=("El predicado de una guarda se escribe v ___ string. (2 letras)", "is"),
  ec="devolver boolean normal en lugar de un predicado y perder el acotado"),
K("never",
  d="tipo de valores que nunca ocurren",
  u="marcar código inalcanzable o comprobar que se cubrieron todos los casos",
  mas="Una función que siempre lanza un error devuelve never. También se usa al final de un switch para que TypeScript avise si falta un caso.",
  k=["never representa valores que nunca ocurren.", "Una función que siempre lanza error devuelve never.", "Sirve para detectar casos sin cubrir."],
  sit="Tu función siempre lanza una excepción y nunca termina con normalidad. ¿Qué tipo de retorno declaras?",
  cod="""function fallar(msg: string): never {   // nunca devuelve
  throw new Error(msg);
}
try { fallar("algo salió mal"); } catch (e) { console.log("capturado"); }""",
  h="lanza un error con una función que devuelve never",
  pr=("El tipo de lo que nunca ocurre es ___. (5 letras)", "never"),
  ec="usar never donde sí hay un valor de retorno"),
K("Firmas de índice",
  d="tipo para objetos con claves que no se conocen de antemano",
  u="describir objetos usados como diccionarios",
  mas="Se escribe { [clave: string]: number }. Cualquier clave de texto es válida y su valor debe ser número. Es el equivalente a Record<string, number>.",
  k=["Una firma de índice describe claves desconocidas.", "Se escribe con [clave: string]: tipo.", "Es equivalente a Record<string, tipo>."],
  sit="No sabes los nombres de las claves, pero todos sus valores son números. ¿Qué escribes?",
  cod="""const notas: { [alumno: string]: number } = {};   // claves libres
notas["Ana"] = 9;
notas["Luis"] = 7;
console.log(notas);""",
  h="guarda notas por nombre de alumno",
  pr=("Una firma de índice se escribe [clave: ___]: tipo. (string)", "string"),
  ec="usar un valor del tipo equivocado en la firma de índice"),
K("Promise<T>",
  d="tipo de una operación asíncrona que devolverá un valor de tipo T",
  u="tipar resultados que llegan más tarde",
  mas="Promise<number> promete un número en el futuro. Se consume con then o con await dentro de una función async.",
  k=["Promise<T> representa un valor que llegará después.", "Se consume con then o con await.", "T es el tipo del valor prometido."],
  sit="Una función tarda en responder y devolverá un número más adelante. ¿Qué tipo declaras?",
  cod="""function esperar(): Promise<number> {   // promete un número
  return Promise.resolve(42);
}
esperar().then((n) => console.log(n));""",
  h="obtiene un número prometido y lo muestra",
  pr=("El tipo de un valor que llegará después es ___<T>. (7 letras)", "promise"),
  ec="usar el valor de una Promise sin esperar a que se resuelva"),
K("Clases genéricas",
  d="clases que dependen de un tipo parámetro",
  u="crear estructuras de datos reutilizables para cualquier tipo",
  mas="class Pila<T> guarda elementos de tipo T. Al crearla se decide el tipo: new Pila<number>(). Así una misma clase sirve para números, textos u objetos con seguridad.",
  k=["Una clase genérica recibe un tipo parámetro como <T>.", "El tipo se decide al crear la instancia.", "Una misma clase genérica sirve para muchos tipos."],
  sit="Quieres una pila que guarde solo números en un caso y solo textos en otro, con la misma clase. ¿Qué usas?",
  cod="""class Pila<T> {
  private items: T[] = [];
  apilar(x: T): void { this.items.push(x); }   // solo acepta T
  total(): number { return this.items.length; }
}
const p = new Pila<number>();
p.apilar(5);
console.log(p.total());""",
  h="crea una pila de números y cuenta sus elementos",
  pr=("Una clase genérica se crea como new Pila___. (<number>)", "<number>", "<tipo>", "<string>"),
  ec="mezclar tipos distintos en una clase genérica ya definida para un tipo"),
]
