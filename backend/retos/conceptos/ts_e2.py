"""TypeScript · Etapa 2: Funciones, objetos e interfaces."""
from ..generador import K

LISTA = [
K("Funciones tipadas",
  d="funciones cuyos parámetros llevan un tipo",
  u="evitar llamar a una función con datos incorrectos",
  mas="Cada parámetro se escribe como nombre: tipo. Si llamas a la función con otro tipo o con argumentos de más o de menos, TypeScript lo marca como error.",
  k=["Una función tipada declara el tipo de cada parámetro.", "TypeScript rechaza llamadas con tipos incorrectos.", "También se comprueba la cantidad de argumentos."],
  sit="Quieres que una función de suma solo acepte números y no textos. ¿Qué haces?",
  cod="""function sumar(a: number, b: number) {   // parámetros con tipo
  return a + b;
}
console.log(sumar(2, 3));""",
  h="suma dos números con una función tipada",
  pr=("Los parámetros de una función se tipan con nombre___ tipo. (:)", ":", "dos puntos"),
  ec="llamar a una función con un texto donde espera un número",
  err=("function doble(n: number) {\n  return n * 2;\n}\nconsole.log(doble(\"5\"));", 4, "doble espera un number, no un texto.")),
K("Tipo de retorno",
  d="tipo del valor que devuelve una función, escrito después de los paréntesis",
  u="asegurar que la función devuelve lo prometido",
  mas="Se escribe con dos puntos tras los paréntesis: function f(): string. Si algún camino devuelve otro tipo, TypeScript avisa. Normalmente puede inferirse, pero escribirlo documenta la función.",
  k=["El tipo de retorno se escribe después de los paréntesis.", "TypeScript comprueba lo que devuelve la función.", "El tipo de retorno documenta la función."],
  sit="Quieres garantizar que una función siempre devuelva un texto. ¿Qué indicas?",
  cod="""function saludar(nombre: string): string {   // devuelve un string
  return "Hola " + nombre;
}
console.log(saludar("Ana"));""",
  h="devuelve un saludo con el nombre",
  pr=("El tipo de retorno va después de los ___. (paréntesis)", "parentesis", "paréntesis"),
  ec="devolver un tipo distinto al declarado"),
K("void",
  d="tipo de retorno de funciones que no devuelven ningún valor",
  u="indicar que una función solo hace una acción",
  mas="void se usa en funciones que muestran, guardan o modifican algo sin devolver un resultado. Una función void no debe usarse para asignar su resultado a una variable.",
  k=["void indica que la función no devuelve un valor.", "Se usa en funciones que solo realizan una acción.", "No se debe usar el resultado de una función void."],
  sit="Tu función solo imprime un mensaje y no devuelve nada. ¿Qué tipo de retorno declaras?",
  cod="""function avisar(msg: string): void {   // no devuelve nada
  console.log("Aviso:", msg);
}
avisar("Guardado");""",
  h="muestra un aviso sin devolver valor",
  pr=("El tipo de una función que no devuelve nada es ___. (4 letras)", "void"),
  ec="intentar usar el resultado de una función void"),
K("Parámetros opcionales",
  d="parámetros marcados con ? que pueden omitirse al llamar",
  u="permitir llamadas con menos argumentos",
  mas="Un parámetro con ? puede faltar y entonces vale undefined. Los opcionales deben ir al final de la lista de parámetros.",
  k=["Un parámetro opcional se marca con ?.", "Si se omite, el parámetro vale undefined.", "Los opcionales van después de los obligatorios."],
  sit="Quieres que el apellido pueda omitirse al llamar a la función. ¿Qué haces?",
  cod="""function saludar(nombre: string, apellido?: string) {   // ? lo hace opcional
  console.log(apellido ? nombre + " " + apellido : nombre);
}
saludar("Ana");
saludar("Ana", "Pérez");""",
  h="saluda con o sin apellido",
  pr=("Un parámetro opcional se marca con el signo ___. (?)", "?"),
  ec="poner un parámetro opcional antes de uno obligatorio",
  err=("function f(a?: number, b: number) {\n  return b;\n}", 1, "Un parámetro opcional no puede ir antes de uno obligatorio.")),
K("Valores por defecto",
  d="valor que toma un parámetro cuando no se envía ninguno",
  u="evitar comprobar si falta un argumento",
  mas="Se escribe con = después del parámetro. Si llamas sin ese argumento (o con undefined), se usa el valor por defecto. El tipo se infiere del valor.",
  k=["Un valor por defecto se escribe con = en el parámetro.", "Se usa cuando se omite el argumento.", "El tipo se infiere del valor por defecto."],
  sit="Si no se indica el saludo, quieres que se use «Hola» automáticamente. ¿Qué escribes?",
  cod="""function saludar(nombre: string, saludo: string = "Hola") {   // valor por defecto
  console.log(saludo, nombre);
}
saludar("Ana");""",
  h="saluda con «Hola» cuando no se indica otro saludo",
  pr=("El valor por defecto de un parámetro se asigna con el signo ___. (=)", "="),
  ec="creer que el valor por defecto reemplaza un argumento enviado"),
K("Parámetros rest",
  d="parámetro con ... que agrupa los argumentos sobrantes en un array",
  u="aceptar una cantidad variable de argumentos",
  mas="...nombre: tipo[] recoge todos los argumentos restantes en un array. Solo puede haber uno y debe ser el último parámetro.",
  k=["Un parámetro rest se escribe con tres puntos.", "Agrupa los argumentos sobrantes en un array.", "Debe ser el último parámetro."],
  sit="Quieres una función que sume cualquier cantidad de números. ¿Qué usas?",
  cod="""function sumar(...nums: number[]): number {   // recoge todos en un array
  return nums.reduce((a, b) => a + b, 0);
}
console.log(sumar(1, 2, 3, 4));""",
  h="suma todos los números recibidos",
  pr=("Un parámetro rest empieza con ___ puntos. (un número)", "3", "tres"),
  ec="poner el parámetro rest antes de otros parámetros"),
K("Funciones flecha",
  d="forma corta de escribir funciones con =>",
  u="escribir funciones breves y callbacks",
  mas="(a, b) => a + b equivale a una función completa. Si el cuerpo es una sola expresión, el return es implícito. Heredan el this del contexto donde se crean.",
  k=["Las funciones flecha se escriben con =>.", "Con una sola expresión el return es implícito.", "Una flecha hereda el this de su contexto."],
  sit="Necesitas pasar una función breve que duplique cada número de una lista. ¿Qué sintaxis usas?",
  cod="""const doble = (n: number): number => n * 2;   // flecha con retorno implícito
console.log([1, 2, 3].map(doble));""",
  h="duplica cada número de una lista",
  pr=("El símbolo de una función flecha es ___. (=>)", "=>"),
  ec="olvidar las llaves y el return cuando el cuerpo tiene varias líneas"),
K("Tipos de función",
  d="tipo que describe los parámetros y el retorno de una función",
  u="tipar variables o parámetros que contienen funciones",
  mas="Se escribe como (a: number, b: number) => number. Sirve para decir qué forma debe tener una función que se pasa como argumento (callback).",
  k=["Un tipo de función describe parámetros y retorno.", "Se usa para tipar callbacks.", "Se escribe con una flecha entre parámetros y retorno."],
  sit="Recibes una función como parámetro y quieres exigir que reciba un número y devuelva un texto. ¿Qué defines?",
  cod="""type Formato = (n: number) => string;   // forma de la función
const aTexto: Formato = (n) => "Nº " + n;
console.log(aTexto(7));""",
  h="define y usa un tipo para funciones que convierten números en texto",
  pr=("Un tipo de función separa parámetros y retorno con ___. (=>)", "=>"),
  ec="pasar una función con otra firma de la esperada"),
K("Objetos tipados",
  d="objetos cuya forma de propiedades y tipos está declarada",
  u="describir qué datos tiene un objeto",
  mas="Se escribe { nombre: string; edad: number }. TypeScript revisa que el objeto tenga todas las propiedades y que cada una sea del tipo correcto.",
  k=["Un objeto tipado declara sus propiedades y tipos.", "TypeScript revisa que no falte ninguna propiedad.", "Cada propiedad debe ser del tipo declarado."],
  sit="Quieres asegurar que un objeto persona siempre tenga nombre y edad. ¿Qué haces?",
  cod="""const persona: { nombre: string; edad: number } = {   // forma del objeto
  nombre: "Ana",
  edad: 20,
};
console.log(persona.nombre, persona.edad);""",
  h="crea un objeto persona con nombre y edad",
  pr=("Se accede a una propiedad de un objeto con ___ y su nombre. (un punto)", ".", "punto"),
  ec="olvidar una propiedad obligatoria del objeto",
  err=("const p: { nombre: string; edad: number } = {\n  nombre: \"Ana\",\n};", 1, "Falta la propiedad obligatoria edad.")),
K("Propiedades opcionales",
  d="propiedades de objeto marcadas con ? que pueden no existir",
  u="describir datos que a veces faltan",
  mas="En un tipo, nombre?: string indica que la propiedad puede faltar. Al leerla, su tipo incluye undefined, así que conviene comprobarla.",
  k=["Una propiedad opcional se marca con ? tras su nombre.", "Si falta, su valor es undefined.", "Conviene comprobar una propiedad opcional antes de usarla."],
  sit="El teléfono del usuario es opcional: algunos lo tienen y otros no. ¿Cómo lo describes?",
  cod="""type Usuario = { nombre: string; telefono?: string };   // telefono es opcional
const u: Usuario = { nombre: "Ana" };
console.log(u.telefono ?? "sin teléfono");""",
  h="muestra el teléfono o «sin teléfono» si falta",
  pr=("Una propiedad opcional se marca con ___ antes de los dos puntos. (?)", "?"),
  ec="usar una propiedad opcional sin comprobar que existe"),
K("readonly",
  d="modificador que impide cambiar una propiedad después de crearla",
  u="proteger datos que no deben modificarse",
  mas="Una propiedad readonly solo se asigna al crear el objeto. Intentar cambiarla después produce un error de compilación.",
  k=["readonly impide modificar una propiedad.", "Solo se puede asignar al crear el objeto.", "El error aparece al compilar."],
  sit="El id de un usuario no debe cambiar jamás después de crearse. ¿Qué modificador usas?",
  cod="""type Usuario = { readonly id: number; nombre: string };   // id no se puede cambiar
const u: Usuario = { id: 1, nombre: "Ana" };
u.nombre = "Eva";
console.log(u);""",
  h="cambia el nombre pero deja el id protegido",
  pr=("El modificador que impide cambiar una propiedad es ___. (8 letras)", "readonly"),
  ec="intentar reasignar una propiedad readonly",
  err=("type P = { readonly id: number };\nconst p: P = { id: 1 };\np.id = 2;", 3, "id es readonly y no se puede reasignar.")),
K("Alias de tipo",
  d="nombre propio que se da a un tipo con la palabra type",
  u="reutilizar un tipo sin repetirlo",
  mas="type Nombre = ... crea un alias que puedes usar en cualquier parte. Sirve para objetos, uniones, funciones y más. No crea un tipo nuevo, solo un nombre.",
  k=["type crea un alias para un tipo.", "Un alias se puede usar en muchos lugares.", "Un alias no crea un tipo nuevo, solo un nombre."],
  sit="Repites { x: number; y: number } en muchos sitios y quieres darle un nombre. ¿Qué usas?",
  cod="""type Punto = { x: number; y: number };   // alias reutilizable
const a: Punto = { x: 1, y: 2 };
console.log(a.x + a.y);""",
  h="define un tipo Punto y lo usa",
  pr=("La palabra que crea un alias de tipo es ___. (4 letras)", "type"),
  ec="repetir el mismo tipo en muchos lugares en vez de darle un alias"),
K("Interfaces",
  d="forma de describir la estructura que debe tener un objeto",
  u="definir contratos que los objetos deben cumplir",
  mas="interface Nombre { ... } declara propiedades y métodos. Es muy parecida a un alias de tipo para objetos, y las interfaces con el mismo nombre se fusionan.",
  k=["Una interface describe la forma de un objeto.", "Las interfaces definen contratos.", "Dos interfaces con el mismo nombre se fusionan."],
  sit="Quieres un contrato que todo objeto «Animal» debe cumplir. ¿Qué declaras?",
  cod="""interface Animal {   // contrato
  nombre: string;
  sonido(): string;
}
const perro: Animal = { nombre: "Rex", sonido: () => "Guau" };
console.log(perro.nombre, perro.sonido());""",
  h="declara una interfaz Animal y crea un perro que la cumple",
  pr=("La palabra para declarar un contrato de objeto es ___. (9 letras)", "interface"),
  ec="olvidar implementar una propiedad exigida por la interfaz"),
K("Extender interfaces",
  d="crear una interfaz nueva a partir de otra con extends",
  u="reutilizar propiedades y añadir las propias",
  mas="interface B extends A copia las propiedades de A y permite añadir más. Se puede extender de varias interfaces separándolas con comas.",
  k=["extends hereda las propiedades de otra interfaz.", "La interfaz nueva puede añadir sus propias propiedades.", "Se puede extender de varias interfaces a la vez."],
  sit="Quieres un «Empleado» que tenga todo lo de «Persona» y además un sueldo. ¿Qué usas?",
  cod="""interface Persona { nombre: string }
interface Empleado extends Persona { sueldo: number }   // hereda nombre
const e: Empleado = { nombre: "Ana", sueldo: 1500 };
console.log(e.nombre, e.sueldo);""",
  h="crea un empleado que hereda el nombre de Persona",
  pr=("Para heredar propiedades de otra interfaz se usa ___. (7 letras)", "extends"),
  ec="repetir manualmente las propiedades de la interfaz base"),
K("Unión de tipos",
  d="tipo que permite varias alternativas separadas por |",
  u="aceptar un valor que puede ser de más de un tipo",
  mas="string | number acepta texto o número. Para usar métodos de uno solo debes primero comprobar de qué tipo es con typeof.",
  k=["Una unión se escribe con el símbolo |.", "Una unión acepta cualquiera de sus tipos.", "Hay que acotar el tipo antes de usar métodos específicos."],
  sit="Un identificador puede ser un número o un texto. ¿Qué tipo declaras?",
  cod="""let id: string | number = 5;   // puede ser texto o número
id = "A-7";
console.log(id);""",
  h="guarda un id que cambia de número a texto",
  pr=("Una unión de tipos se separa con la barra ___. (|)", "|"),
  ec="usar un método de string sobre una unión sin comprobar el tipo"),
K("Tipos literales",
  d="tipos que aceptan solo valores exactos concretos",
  u="limitar una variable a unas pocas opciones permitidas",
  mas="En lugar de string puedes escribir \"norte\" | \"sur\" | \"este\". Solo se aceptarán esos valores y el editor los sugiere.",
  k=["Un tipo literal acepta solo valores concretos.", "Se combinan con | para listar opciones.", "El editor autocompleta las opciones permitidas."],
  sit="Una variable solo debe valer «norte», «sur», «este» u «oeste». ¿Qué tipo declaras?",
  cod="""type Direccion = "norte" | "sur" | "este" | "oeste";   // opciones exactas
const d: Direccion = "norte";
console.log(d);""",
  h="restringe una dirección a cuatro valores posibles",
  pr=("Un tipo que solo acepta un valor exacto se llama tipo ___. (7 letras)", "literal"),
  ec="asignar un valor que no está en la lista del tipo literal",
  err=("type Color = \"rojo\" | \"azul\";\nconst c: Color = \"verde\";", 2, "«verde» no está entre los valores permitidos.")),
K("Intersección de tipos",
  d="tipo que combina varios tipos con &",
  u="juntar propiedades de varios tipos en uno",
  mas="A & B exige que el valor cumpla A y B a la vez. Se usa para mezclar objetos pequeños en uno más completo.",
  k=["Una intersección se escribe con el símbolo &.", "El valor debe cumplir todos los tipos combinados.", "Sirve para juntar propiedades de varios tipos."],
  sit="Quieres un tipo que reúna a la vez las propiedades de «Nombre» y de «Edad». ¿Qué usas?",
  cod="""type ConNombre = { nombre: string };
type ConEdad = { edad: number };
const p: ConNombre & ConEdad = { nombre: "Ana", edad: 20 };   // cumple ambos
console.log(p);""",
  h="combina dos tipos en un objeto completo",
  pr=("La intersección de tipos se escribe con el signo ___. (&)", "&"),
  ec="confundir & (ambos) con | (alguno)"),
K("Acotar con typeof",
  d="comprobación del tipo de un valor para que TypeScript lo reconozca",
  u="usar con seguridad valores de tipo unión",
  mas="Dentro de if (typeof x === \"string\"), TypeScript sabe que x es string. A ese proceso se le llama acotar o estrechar el tipo (narrowing).",
  k=["typeof comprueba el tipo de un valor.", "Tras comprobar, TypeScript conoce el tipo exacto.", "Acotar el tipo se llama narrowing."],
  sit="Recibes un valor que puede ser texto o número y debes tratar cada caso por separado. ¿Qué técnica usas?",
  cod="""function mostrar(v: string | number) {
  if (typeof v === "string") console.log(v.toUpperCase());   // aquí v es string
  else console.log(v.toFixed(1));                           // aquí v es number
}
mostrar("hola");
mostrar(3);""",
  h="trata distinto un texto y un número",
  pr=("El operador que revisa el tipo de un valor es ___. (6 letras)", "typeof"),
  ec="usar métodos de un tipo sin comprobar antes"),
K("Aserción de tipos",
  d="indicación con as de que sabes más que el compilador sobre un tipo",
  u="decirle a TypeScript el tipo cuando tú lo conoces mejor",
  mas="valor as Tipo cambia el tipo solo para el compilador; no convierte nada en tiempo de ejecución. Úsala con cuidado: si te equivocas, el error aparece al ejecutar.",
  k=["as indica un tipo al compilador.", "as no convierte el valor en tiempo de ejecución.", "Una aserción incorrecta causa errores al ejecutar."],
  sit="Sabes que un valor desconocido es un texto y quieres tratarlo como tal. ¿Qué usas?",
  cod="""const dato: unknown = "hola";
const largo = (dato as string).length;   // afirmas que es string
console.log(largo);""",
  h="trata un valor desconocido como texto y mide su largo",
  pr=("La palabra que afirma un tipo es ___. (2 letras)", "as"),
  ec="usar as para convertir datos en lugar de comprobar su tipo"),
K("?. y ??",
  d="operadores para acceder a propiedades que pueden faltar y dar valores por defecto",
  u="evitar errores con valores null o undefined",
  mas="?. detiene la cadena y devuelve undefined si algo falta. ?? usa el valor de la derecha solo si el de la izquierda es null o undefined; a diferencia de ||, respeta el 0 y el texto vacío.",
  k=["?. evita errores al acceder a algo que puede faltar.", "?? da un valor si el de la izquierda es null o undefined.", "?? respeta el 0 y el texto vacío."],
  sit="Quieres leer el teléfono de un usuario que quizá no exista y mostrar «sin dato» si falta. ¿Qué operadores usas?",
  cod="""function telefono(u?: { tel?: string }): string {
  return u?.tel ?? "sin dato";   // ?. no falla y ?? da el valor por defecto
}
console.log(telefono(), telefono({ tel: "099" }));""",
  h="muestra «sin dato» cuando falta el usuario o su teléfono",
  pr=("El operador de acceso opcional es ___. (?.)", "?."),
  ec="usar || y perder valores válidos como 0"),
]
