"""TypeScript · Etapa 3: Clases y módulos."""
from ..generador import K

LISTA = [
K("Clases",
  d="plantilla que define propiedades y métodos de un tipo de objeto",
  u="crear muchos objetos con la misma estructura y comportamiento",
  mas="Una clase se declara con class y se usa con new para crear instancias. Reúne datos (propiedades) y acciones (métodos) en un solo lugar.",
  k=["Una clase es una plantilla para crear objetos.", "new crea una instancia de una clase.", "Una clase reúne propiedades y métodos."],
  sit="Necesitas crear muchos alumnos con los mismos datos y las mismas acciones. ¿Qué defines?",
  cod="""class Alumno {
  nombre: string = "Ana";
  saludar(): string { return "Hola, soy " + this.nombre; }   // método
}
const a = new Alumno();   // instancia
console.log(a.saludar());""",
  h="define una clase Alumno y usa una instancia",
  pr=("La palabra para declarar una clase es ___. (5 letras)", "class"),
  ec="usar la clase sin crear antes una instancia con new"),
K("Constructor",
  d="método especial que se ejecuta al crear una instancia",
  u="inicializar las propiedades del objeto con valores",
  mas="Se escribe constructor(...) dentro de la clase. Recibe parámetros y los asigna a this. Solo puede haber uno por clase.",
  k=["El constructor se ejecuta al crear una instancia.", "El constructor inicializa las propiedades.", "Una clase solo tiene un constructor."],
  sit="Cada alumno debe nacer con su nombre y su edad ya asignados. ¿Qué usas?",
  cod="""class Alumno {
  nombre: string;
  edad: number;
  constructor(nombre: string, edad: number) {   // se ejecuta con new
    this.nombre = nombre;
    this.edad = edad;
  }
}
const a = new Alumno("Luis", 20);
console.log(a.nombre, a.edad);""",
  h="crea un alumno con nombre y edad iniciales",
  pr=("El método que se ejecuta al crear una instancia es el ___. (11 letras)", "constructor"),
  ec="olvidar asignar los parámetros a this en el constructor"),
K("this",
  d="referencia al objeto actual dentro de una clase",
  u="acceder a las propiedades y métodos de la propia instancia",
  mas="Dentro de un método, this apunta a la instancia que lo llama. Sin this, el nombre se busca como una variable local y no como propiedad.",
  k=["this representa la instancia actual.", "this permite leer las propiedades del objeto.", "Sin this no se accede a las propiedades de la instancia."],
  sit="Dentro de un método necesitas leer la propiedad nombre del mismo objeto. ¿Qué usas?",
  cod="""class Gato {
  constructor(public nombre: string) {}
  hablar(): void { console.log(this.nombre + " dice miau"); }   // this.nombre
}
new Gato("Misu").hablar();""",
  h="muestra lo que dice un gato usando su nombre",
  pr=("Para referirte al objeto actual dentro de la clase usas ___. (4 letras)", "this"),
  ec="olvidar this al leer una propiedad dentro de un método",
  err=("class A {\n  n: number = 1;\n  ver() { console.log(n); }\n}", 3, "Debe ser this.n para leer la propiedad.")),
K("public y private",
  d="modificadores que controlan quién puede usar una propiedad o método",
  u="ocultar detalles internos de una clase",
  mas="public (por defecto) permite acceso desde cualquier lugar. private lo limita a la propia clase. Intentar usar un miembro private desde fuera da error al compilar.",
  k=["public permite acceder desde cualquier lugar.", "private limita el acceso a la propia clase.", "Acceder a un miembro private desde fuera da error."],
  sit="El saldo de una cuenta no debe modificarse directamente desde fuera. ¿Qué modificador usas?",
  cod="""class Cuenta {
  private saldo: number = 100;   // solo se usa dentro de la clase
  mostrar(): void { console.log(this.saldo); }
}
new Cuenta().mostrar();""",
  h="muestra un saldo guardado como propiedad privada",
  pr=("El modificador que oculta un miembro fuera de la clase es ___. (7 letras)", "private"),
  ec="acceder a una propiedad private desde fuera de la clase",
  err=("class C {\n  private x = 1;\n}\nconsole.log(new C().x);", 4, "x es private y no se puede leer desde fuera.")),
K("protected",
  d="modificador que permite acceso desde la clase y sus hijas",
  u="compartir miembros con subclases sin exponerlos al exterior",
  mas="protected es un punto medio entre public y private: lo ven la clase y las que heredan de ella, pero no el código externo.",
  k=["protected permite acceso a la clase y sus subclases.", "protected no es visible desde fuera de la jerarquía.", "protected es un punto medio entre public y private."],
  sit="Quieres que una propiedad la vean las clases hijas pero no el código externo. ¿Qué modificador usas?",
  cod="""class Animal {
  protected energia: number = 10;   // visible para las hijas
}
class Perro extends Animal {
  correr(): void { console.log("Energía:", this.energia); }
}
new Perro().correr();""",
  h="muestra una propiedad protegida desde una subclase",
  pr=("El modificador visible solo para la clase y sus hijas es ___. (9 letras)", "protected"),
  ec="confundir protected con private"),
K("Parámetros-propiedad",
  d="forma abreviada de declarar y asignar propiedades en el constructor",
  u="escribir menos código al crear clases",
  mas="Si anteponemos un modificador a un parámetro del constructor, como public nombre: string, TypeScript crea la propiedad y la asigna automáticamente.",
  k=["Un parámetro-propiedad declara y asigna a la vez.", "Se logra poniendo un modificador al parámetro del constructor.", "Ahorra escribir asignaciones repetidas."],
  sit="Estás cansado de declarar cada propiedad y asignarla en el constructor. ¿Qué atajo usas?",
  cod="""class Punto {
  constructor(public x: number, public y: number) {}   // declara y asigna
}
const p = new Punto(2, 3);
console.log(p.x, p.y);""",
  h="crea un punto con propiedades x e y en una sola línea",
  pr=("Un parámetro del constructor con un ___ como public crea la propiedad. (modificador)", "modificador"),
  ec="escribir el modificador y además repetir la asignación manualmente"),
K("readonly en clases",
  d="propiedad de clase que solo puede asignarse al crear la instancia",
  u="evitar que un dato se cambie después de crear el objeto",
  mas="Se puede asignar al declararla o dentro del constructor. Después, cualquier intento de cambiarla produce un error de compilación.",
  k=["readonly en una clase impide reasignar la propiedad.", "Solo puede asignarse en la declaración o en el constructor.", "Cambiarla después es un error de compilación."],
  sit="El número de documento de un cliente no debe cambiar tras crearlo. ¿Qué usas en la clase?",
  cod="""class Cliente {
  constructor(public readonly documento: string) {}   // no se reasigna
}
const c = new Cliente("123");
console.log(c.documento);""",
  h="crea un cliente con documento inmutable",
  pr=("La propiedad de clase que no se reasigna se marca ___. (8 letras)", "readonly"),
  ec="reasignar una propiedad readonly fuera del constructor"),
K("Herencia con extends",
  d="mecanismo por el que una clase hija toma lo de una clase padre",
  u="reutilizar código entre clases relacionadas",
  mas="class Hija extends Padre hereda propiedades y métodos. La hija puede añadir los suyos o sobrescribir los heredados.",
  k=["extends crea una clase hija de otra clase.", "La clase hija hereda propiedades y métodos.", "La hija puede sobrescribir métodos del padre."],
  sit="Perro y Gato comparten comportamientos de Animal y quieres no repetir código. ¿Qué usas?",
  cod="""class Animal { respirar(): void { console.log("respira"); } }
class Perro extends Animal {   // hereda de Animal
  ladrar(): void { console.log("guau"); }
}
const p = new Perro();
p.respirar();
p.ladrar();""",
  h="un perro usa un método heredado y uno propio",
  pr=("Una clase hereda de otra con la palabra ___. (7 letras)", "extends"),
  ec="repetir código en clases que podrían heredar"),
K("super",
  d="palabra que llama al constructor o a los métodos de la clase padre",
  u="reutilizar la inicialización o el comportamiento del padre",
  mas="En el constructor de una hija, super(...) debe llamarse antes de usar this. En un método, super.metodo() ejecuta la versión del padre.",
  k=["super llama al constructor de la clase padre.", "super debe llamarse antes de usar this en el constructor.", "super.metodo() ejecuta el método del padre."],
  sit="Una clase hija necesita ejecutar la inicialización de su padre antes de la suya. ¿Qué usas?",
  cod="""class Persona { constructor(public nombre: string) {} }
class Alumno extends Persona {
  constructor(nombre: string, public curso: string) {
    super(nombre);   // llama al constructor del padre
  }
}
console.log(new Alumno("Ana", "TS"));""",
  h="inicializa el nombre con el constructor del padre",
  pr=("La palabra que llama al constructor del padre es ___. (5 letras)", "super"),
  ec="usar this antes de llamar a super en el constructor",
  err=("class A { constructor(public n: string) {} }\nclass B extends A {\n  constructor(n: string) { this.n = n; super(n); }\n}", 3, "Hay que llamar a super antes de usar this.")),
K("Clases abstractas",
  d="clases que sirven de base y no pueden instanciarse directamente",
  u="definir una base común que obliga a las hijas a completar métodos",
  mas="Se declaran con abstract class. Pueden tener métodos abstractos sin cuerpo que cada hija debe implementar. No se puede hacer new de una clase abstracta.",
  k=["Una clase abstracta no se puede instanciar.", "Los métodos abstractos no tienen cuerpo.", "Las clases hijas deben implementar los métodos abstractos."],
  sit="Quieres una clase base «Figura» que obligue a cada figura a calcular su área, pero que nunca se cree sola. ¿Qué usas?",
  cod="""abstract class Figura {
  abstract area(): number;   // cada hija debe implementarlo
}
class Cuadrado extends Figura {
  constructor(public lado: number) { super(); }
  area(): number { return this.lado ** 2; }
}
console.log(new Cuadrado(4).area());""",
  h="calcula el área de un cuadrado desde una clase abstracta",
  pr=("La palabra que marca una clase como no instanciable es ___. (8 letras)", "abstract"),
  ec="intentar crear una instancia de una clase abstracta"),
K("implements",
  d="palabra que obliga a una clase a cumplir una interfaz",
  u="garantizar que una clase ofrece ciertos miembros",
  mas="class A implements I exige que A tenga todas las propiedades y métodos de I. Una clase puede implementar varias interfaces separadas por comas.",
  k=["implements obliga a cumplir una interfaz.", "Una clase puede implementar varias interfaces.", "Si falta un miembro, TypeScript marca error."],
  sit="Quieres asegurar que la clase Pato tenga el método volar definido en la interfaz Volador. ¿Qué usas?",
  cod="""interface Volador { volar(): void }
class Pato implements Volador {   // debe tener volar()
  volar(): void { console.log("El pato vuela"); }
}
new Pato().volar();""",
  h="un pato cumple la interfaz Volador",
  pr=("Una clase cumple una interfaz con la palabra ___. (10 letras)", "implements"),
  ec="olvidar implementar un método exigido por la interfaz"),
K("Getters y setters",
  d="métodos de acceso que se usan como si fueran propiedades",
  u="controlar la lectura y escritura de un dato",
  mas="get devuelve un valor calculado y set permite validar antes de guardar. Se usan sin paréntesis, como si fueran propiedades normales.",
  k=["Un getter se usa como una propiedad, sin paréntesis.", "Un setter puede validar antes de guardar.", "Los getters permiten valores calculados."],
  sit="Quieres validar que la edad no sea negativa cada vez que se asigna. ¿Qué usas?",
  cod="""class Persona {
  private _edad = 0;
  get edad(): number { return this._edad; }
  set edad(v: number) { if (v >= 0) this._edad = v; }   // valida
}
const p = new Persona();
p.edad = 20;
console.log(p.edad);""",
  h="guarda la edad solo si no es negativa",
  pr=("El método que lee un valor como propiedad se declara con ___. (3 letras)", "get"),
  ec="llamar a un getter con paréntesis"),
K("static",
  d="modificador de miembros que pertenecen a la clase y no a las instancias",
  u="compartir datos o utilidades sin crear objetos",
  mas="Un miembro static se usa con el nombre de la clase, como Matematica.pi. No necesita new y es común para constantes y funciones auxiliares.",
  k=["static pertenece a la clase y no a las instancias.", "Se usa con el nombre de la clase.", "No necesita crear una instancia con new."],
  sit="Quieres un contador compartido por todas las instancias, sin crear objetos para leerlo. ¿Qué usas?",
  cod="""class Contador {
  static total = 0;   // pertenece a la clase
  constructor() { Contador.total++; }
}
new Contador(); new Contador();
console.log(Contador.total);""",
  h="cuenta cuántas instancias se crearon",
  pr=("El modificador de miembros de clase compartidos es ___. (6 letras)", "static"),
  ec="intentar usar un miembro static desde una instancia"),
K("Métodos",
  d="funciones declaradas dentro de una clase",
  u="dar comportamiento a los objetos",
  mas="Un método se declara sin la palabra function y se llama con la instancia, como objeto.metodo(). Puede usar this para leer o modificar las propiedades.",
  k=["Un método es una función dentro de una clase.", "Se llama desde la instancia con un punto.", "Un método puede usar this."],
  sit="Quieres que cada objeto Contador sepa incrementarse a sí mismo. ¿Qué defines?",
  cod="""class Contador {
  valor = 0;
  sumar(): void { this.valor++; }   // método
}
const c = new Contador();
c.sumar(); c.sumar();
console.log(c.valor);""",
  h="incrementa un contador con un método",
  pr=("Un método se llama con el objeto, un punto y el ___. (nombre del método)", "nombre"),
  ec="olvidar los paréntesis al llamar a un método"),
K("Exportar",
  d="palabra que hace visible algo de un archivo para otros archivos",
  u="compartir funciones, clases y tipos entre archivos",
  mas="Con export delante de una declaración, otros módulos pueden importarla. Lo que no se exporta queda privado dentro del archivo.",
  k=["export hace visible algo para otros archivos.", "Lo no exportado queda privado en el archivo.", "Se puede exportar funciones, clases y tipos."],
  sit="Escribiste una función en un archivo y quieres usarla desde otro. ¿Qué debes hacer?",
  cod="""// archivo: matematica.ts
// export function doble(n: number): number { return n * 2; }
function doble(n: number): number { return n * 2; }
console.log(doble(21));""",
  h="define una función que luego podría exportarse",
  pr=("La palabra que comparte algo con otros archivos es ___. (6 letras)", "export"),
  ec="olvidar exportar lo que otro archivo necesita"),
K("Importar",
  d="palabra que trae a un archivo lo exportado por otro",
  u="usar código de otros archivos o librerías",
  mas="import { nombre } from \"./archivo\" trae lo exportado con ese nombre. Las rutas relativas empiezan con ./ y no se escribe la extensión .ts.",
  k=["import trae lo exportado por otro archivo.", "Las llaves indican el nombre exacto exportado.", "Las rutas relativas empiezan con ./."],
  sit="Quieres usar en tu archivo una función definida en otro. ¿Qué escribes?",
  cod="""// import { doble } from "./matematica";   // trae doble desde otro archivo
const doble = (n: number): number => n * 2;
console.log(doble(5));""",
  h="usa una función como si se hubiera importado",
  pr=("La palabra que trae algo de otro archivo es ___. (6 letras)", "import"),
  ec="usar una ruta equivocada en el import"),
K("export default",
  d="exportación principal de un archivo que se importa sin llaves",
  u="indicar la pieza principal de un módulo",
  mas="Cada archivo puede tener un solo export default. Al importarlo puedes elegir el nombre que quieras y no se usan llaves.",
  k=["Cada archivo puede tener un solo export default.", "El export default se importa sin llaves.", "Al importar puedes elegir el nombre libremente."],
  sit="Tu archivo exporta una única clase principal y quieres importarla sin llaves. ¿Qué usas?",
  cod="""// export default class Servicio { ... }
// import Servicio from "./servicio";   // sin llaves
class Servicio { nombre = "principal"; }
console.log(new Servicio().nombre);""",
  h="define la clase principal de un módulo",
  pr=("La exportación principal de un archivo es export ___. (7 letras)", "default"),
  ec="usar llaves al importar un export default"),
K("import type",
  d="importación que trae solo tipos y desaparece al compilar",
  u="importar tipos sin añadir código al resultado",
  mas="import type { Usuario } from \"./tipos\" garantiza que solo se usa como tipo. El compilador lo elimina del JavaScript generado.",
  k=["import type importa solo tipos.", "Se elimina del JavaScript generado.", "Evita importar código que solo sirve para tipar."],
  sit="Solo necesitas el tipo Usuario de otro archivo y no quieres traer su código. ¿Qué usas?",
  cod="""// import type { Usuario } from "./tipos";   // solo tipo, sin código
type Usuario = { nombre: string };
const u: Usuario = { nombre: "Ana" };
console.log(u.nombre);""",
  h="usa un tipo como si se hubiera importado solo como tipo",
  pr=("La importación que trae solo tipos es import ___. (4 letras)", "type"),
  ec="importar código completo cuando solo hacía falta un tipo"),
K("instanceof",
  d="operador que comprueba si un objeto pertenece a una clase",
  u="saber de qué clase es un objeto en tiempo de ejecución",
  mas="x instanceof Clase devuelve true si x fue creado con esa clase o una hija. TypeScript lo usa también para acotar el tipo dentro del if.",
  k=["instanceof comprueba si un objeto es de una clase.", "Devuelve true también para subclases.", "Acota el tipo dentro del if."],
  sit="Recibes un objeto y debes saber si es un Perro antes de pedirle que ladre. ¿Qué usas?",
  cod="""class Perro { ladrar(): void { console.log("guau"); } }
const x: Perro | string = new Perro();
if (x instanceof Perro) x.ladrar();   // aquí x es Perro""",
  h="comprueba que es un perro antes de ladrar",
  pr=("El operador que comprueba la clase de un objeto es ___. (10 letras)", "instanceof"),
  ec="usar typeof para comprobar clases"),
K("Polimorfismo",
  d="capacidad de objetos distintos de responder al mismo método de forma propia",
  u="tratar objetos distintos de manera uniforme",
  mas="Si Perro y Gato sobrescriben hablar(), puedes recorrer una lista de Animales llamando hablar() y cada uno responde a su manera sin que el código lo distinga.",
  k=["El polimorfismo permite que cada clase responda a su manera.", "Se apoya en métodos sobrescritos.", "Permite tratar objetos distintos de forma uniforme."],
  sit="Tienes una lista de animales distintos y quieres que cada uno haga su propio sonido con la misma llamada. ¿Qué aprovechas?",
  cod="""class Animal { hablar(): string { return "..."; } }
class Perro extends Animal { hablar(): string { return "guau"; } }
class Gato extends Animal { hablar(): string { return "miau"; } }
for (const a of [new Perro(), new Gato()]) console.log(a.hablar());""",
  h="cada animal responde con su propio sonido",
  pr=("Que objetos distintos respondan al mismo método a su manera es ___. (13 letras)", "polimorfismo"),
  ec="usar muchos if para distinguir clases en lugar de polimorfismo"),
]
