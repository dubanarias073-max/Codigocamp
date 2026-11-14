"""Rust · Etapa 4: propiedad, préstamos y tipos compuestos."""
from ..generador import K

LISTA = [
K("Propiedad", d="reglas que asignan a cada valor un dueño responsable de su ciclo de vida", u="administrar memoria sin recolector de basura", mas="Cada valor tiene un dueño y cuando ese dueño sale de ámbito el valor se libera. Una asignación puede mover la propiedad si el tipo no implementa Copy. Los préstamos permiten usar un valor sin transferir su propiedad.", k=["Cada valor tiene un dueño a la vez.", "El valor se libera cuando su dueño sale de ámbito.", "Un préstamo permite usar un valor sin tomar su propiedad."], sit="Quieres que el compilador controle quién libera cada valor sin un recolector de basura. ¿Qué sistema central de Rust aplica?", cod="""fn main() {
    let texto = String::from("dato");
    println!("{texto}");
}""", h="crea un String cuyo dueño es texto y lo usa", pr=("El sistema de Rust que controla dueños y ciclo de vida se llama ___.", "propiedad"), pr2=("Al salir el dueño de ámbito, el valor se ___ .", "libera"), ec="creer que dos vinculaciones poseen simultáneamente el mismo String", out="dato"),
K("Estructuras", d="tipos propios que agrupan campos con nombre y tipos definidos", u="modelar entidades con varios datos relacionados", mas="struct define un tipo compuesto con campos nombrados. Cada instancia asigna un valor a todos sus campos, salvo que se utilice sintaxis de actualización desde otra instancia. Los campos se acceden mediante punto.", k=["struct declara un tipo compuesto.", "Los campos de una estructura tienen nombre y tipo.", "Se accede a un campo con la notación instancia.campo."], sit="Quieres representar una persona con nombre y edad como un solo valor de tipo propio. ¿Qué declaración usas?", cod="""struct Persona { nombre: &'static str, edad: u8 }
fn main() {
    let p = Persona { nombre: "Ana", edad: 20 };
    println!("{}: {}", p.nombre, p.edad);
}""", h="crea una estructura Persona y muestra ambos campos", pr=("La palabra clave para declarar un tipo de campos nombrados es ___.", "struct"), pr2=("El campo de una instancia se lee con un punto: p.___.", "nombre"), ec="crear una instancia y dejar sin inicializar un campo requerido", out="Ana: 20"),
K("Movimiento de propiedad", d="transferencia del dueño de un valor no Copy a una vinculación nueva", u="pasar valores sin duplicar automáticamente su almacenamiento", mas="Al asignar un String a otro nombre, su propiedad se mueve y el nombre anterior deja de poder usarse. Esto evita que dos dueños liberen el mismo almacenamiento. Tipos simples como enteros implementan Copy y se copian en vez de moverse.", k=["Una asignación de String mueve su propiedad.", "Después del movimiento no se puede usar el nombre anterior.", "Los tipos Copy se copian en lugar de moverse."], sit="Quieres transferir un String a otro nombre sin clonar su búfer y dejar de usar el anterior. ¿Qué sucede en esa asignación?", cod="""fn main() {
    let original = String::from("sol");
    let nuevo = original;
    println!("{nuevo}");
}""", h="mueve la propiedad del String a nuevo y lo imprime", pr=("La transferencia de propiedad que invalida el nombre anterior se llama ___.", "movimiento"), pr2=("Después de mover original, puede usarse de nuevo: ___. (sí o no)", "no"), ec="usar una variable String después de haber movido su valor", out="sol"),
K("Clonar un String", d="método clone que crea una copia independiente de un valor propietario", u="conservar el dato original y obtener otro dueño", mas="clone solicita una duplicación explícita de un valor que implementa Clone. En String copia el contenido de texto a un almacenamiento separado. Puede implicar un costo, por lo que no se inserta automáticamente en cada asignación.", k=["String implementa Clone.", "clone crea un String con contenido independiente.", "La clonación de una cadena puede copiar su búfer."], sit="Necesitas conservar el String original y crear una segunda cadena propietaria con el mismo texto. ¿Qué método llamas?", cod="""fn main() {
    let original = String::from("luz");
    let copia = original.clone();
    println!("{original} {copia}");
}""", h="clona la cadena y muestra ambas vinculaciones válidas", pr=("El método que solicita duplicar explícitamente un valor es ___.", "clone"), pr2=("La clonación de String copia el texto a un almacenamiento independiente: ___. (sí o no)", "sí"), ec="esperar que asignar un String a otro nombre lo clone automáticamente", out="luz luz"),
K("Copy", d="rasgo que permite copiar ciertos valores al asignarlos o pasarlos", u="usar valores simples en varios lugares sin movimiento visible", mas="Copy marca tipos cuyo valor puede duplicarse implícitamente al asignarse. Enteros, bool y char son ejemplos de tipos Copy. String no lo implementa porque duplicar su almacenamiento requeriría una operación explícita como clone.", k=["Los enteros implementan Copy.", "Copy permite usar una vinculación después de asignar su valor a otra.", "String no implementa Copy."], sit="Al asignar un entero a otro nombre, ambos nombres deben seguir utilizables sin llamar clone. ¿Qué rasgo permite esta copia?", cod="""fn main() {
    let a = 12;
    let b = a;
    println!("{a} {b}");
}""", h="copia el entero y muestra ambos valores", pr=("El rasgo de copia implícita de valores pequeños se llama ___.", "Copy"), pr2=("String implementa Copy: ___. (sí o no)", "no"), ec="asumir que todos los tipos propietarios implementan Copy", out="12 12"),
K("Préstamo inmutable", d="referencia &T que permite leer un valor sin tomar su propiedad", u="compartir acceso de lectura a un dato", mas="&valor crea una referencia compartida a un valor. La referencia no toma su propiedad y permite leerlo mientras siga siendo válida. El dueño puede seguir usando el valor después del préstamo.", k=["&T es una referencia inmutable.", "Un préstamo inmutable no transfiere propiedad.", "Se pueden mantener varias referencias inmutables compatibles."], sit="Una función necesita leer un String sin apropiarse de él ni impedir que el llamador lo use después. ¿Qué tipo de referencia recibe?", cod="""fn longitud(s: &String) -> usize { s.len() }
fn main() {
    let texto = String::from("sol");
    println!("{} {}", longitud(&texto), texto);
}""", h="presta texto para leer su longitud y luego lo vuelve a usar", pr=("La referencia de lectura de un valor se escribe con el operador ___.", "&"), pr2=("Una referencia inmutable se anota como ___T.", "&"), ec="mover el dato cuando solo se necesita consultarlo", out="3 sol"),
K("Referencia mutable", d="referencia &mut T que permite modificar prestadamente un valor", u="dejar que una función cambie un dato que pertenece al llamador", mas="Una referencia mutable se crea con &mut y requiere acceso mutable al dueño. Mientras está activa, no puede coexistir con otras referencias al mismo dato. Esta exclusividad ayuda a evitar carreras de datos y cambios inesperados.", k=["&mut T permite modificar el valor prestado.", "El dueño debe ser mutable para crear una referencia mutable.", "Una referencia mutable es exclusiva mientras está activa."], sit="Una función debe cambiar el String del llamador sin quedarse con su propiedad. ¿Qué referencia recibe?", cod="""fn agregar(s: &mut String) { s.push('!'); }
fn main() {
    let mut texto = String::from("hola");
    agregar(&mut texto);
    println!("{texto}");
}""", h="presta texto de forma mutable y añade un signo", pr=("La referencia mutable se escribe con el operador ___mut.", "&"), pr2=("Para crear &mut texto, la vinculación texto debe declararse con ___.", "mut"), ec="intentar mutar un dato mediante una referencia inmutable", out="hola!"),
K("Regla de préstamos", d="restricción que excluye referencias mutables simultáneas con otros préstamos", u="prevenir escrituras concurrentes y referencias inválidas", mas="En un ámbito, Rust permite varias referencias inmutables o una referencia mutable, pero no ambas formas simultáneamente al mismo dato. El compilador usa los ámbitos de vida de las referencias para comprobar la regla. Una referencia no puede sobrevivir a los datos que señala.", k=["Pueden coexistir varias referencias inmutables.", "Una referencia mutable debe ser exclusiva.", "Una referencia no puede durar más que el dato referenciado."], sit="Quieres garantizar que durante una escritura no haya otra referencia activa al mismo dato. ¿Qué regla del sistema de préstamos aplica Rust?", cod="""fn main() {
    let mut valor = 1;
    let r = &mut valor;
    *r += 1;
    println!("{valor}");
}""", h="usa en exclusiva una referencia mutable y luego lee el valor", pr=("La restricción de préstamos que exige exclusividad para &mut se conoce como regla de ___.", "préstamos"), pr2=("Durante un préstamo mutable puede existir otra referencia al mismo dato: ___. (sí o no)", "no"), ec="mantener una referencia inmutable y crear a la vez una referencia mutable al mismo valor", out="2"),
K("Diferencia entre String y str", d="String posee texto modificable y str es el tipo de texto prestado", u="elegir entre almacenar texto y referenciarlo", mas="String es un tipo propietario con búfer UTF-8 que puede crecer. str es un tipo de texto dinámico que normalmente se usa detrás de una referencia como &str. Los literales de texto se prestan como &'static str.", k=["String posee el búfer de texto.", "str se usa habitualmente como &str.", "Un literal de cadena tiene duración estática."], sit="Una función debe aceptar tanto un literal como una vista de un String sin apropiarse del texto. ¿Qué tipo de parámetro textual flexible usas?", cod="""fn mostrar(s: &str) { println!("{s}"); }
fn main() {
    let propio = String::from("hola");
    mostrar("texto fijo");
    mostrar(&propio);
}""", h="acepta como &str tanto literal como préstamo de String", pr=("El tipo de texto prestado y sin tamaño estático se llama ___.", "str"), pr2=("Una función que recibe tanto String prestado como literal suele aceptar ___str.", "&"), ec="declarar un parámetro String cuando solo se necesita leer texto", out="texto fijo\nhola"),
K("Rebanada de cadena", d="referencia &str que apunta a una parte de una cadena UTF-8", u="leer un segmento de texto sin copiarlo", mas="Una rebanada de cadena se obtiene con un rango, como &texto[0..4], y presta bytes del String original. Los límites deben coincidir con límites válidos de caracteres UTF-8. Para obtener una vista segura por límites de texto se puede preferir str::get.", k=["&str puede representar un segmento de una cadena.", "Los rangos de String se expresan en bytes.", "Un límite dentro de un carácter UTF-8 puede provocar pánico."], sit="Quieres prestar una parte de un texto sin crear una copia propietaria y conoces límites UTF-8 válidos. ¿Qué tipo de vista obtienes?", cod="""fn main() {
    let texto = String::from("Rust");
    let parte: &str = &texto[0..2];
    println!("{parte}");
}""", h="presta los primeros dos bytes ASCII del texto", pr=("La vista prestada de un segmento textual tiene tipo ___.", "&str"), pr2=("Los límites de rango sobre String se miden en ___ UTF-8.", "bytes"), ec="cortar una cadena UTF-8 en mitad de un carácter multibyte", out="Ru"),
K("Ámbito y liberación", d="región donde una vinculación es válida y al final de la cual se libera su valor", u="razonar cuándo deja de existir un recurso", mas="Un ámbito se delimita normalmente con llaves. Una variable es válida dentro de su ámbito y, al salir, su valor propietario se destruye. Este orden permite que Rust libere recursos automáticamente sin recolector de basura.", k=["Las llaves delimitan un ámbito léxico.", "Una vinculación no se puede usar fuera de su ámbito.", "Los valores propietarios se destruyen al salir del ámbito."], sit="Un recurso debe liberarse automáticamente al terminar el bloque donde se creó. ¿Qué límite de código define ese ciclo de vida?", cod="""fn main() {
    {
        let mensaje = String::from("bloque");
        println!("{mensaje}");
    }
    println!("fin");
}""", h="crea el String en un ámbito interno que termina antes del mensaje final", pr=("La región de código donde una vinculación es válida se llama ___.", "ámbito"), pr2=("Los ámbitos Rust se delimitan con ___ .", "llaves"), ec="intentar acceder a un nombre local después de que su ámbito terminó", out="bloque\nfin"),
K("Campos abreviados", d="sintaxis de inicialización que omite el valor cuando coincide con el nombre", u="construir structs sin repetir nombres de variables", mas="Si una variable local tiene el mismo nombre que un campo, se puede escribir solo el nombre del campo en la instancia. La abreviatura produce el mismo resultado que campo: campo. No cambia la propiedad ni la mutabilidad.", k=["La abreviatura se permite cuando variable y campo tienen el mismo nombre.", "x equivale a x: x en la inicialización de struct.", "La abreviatura no infiere campos omitidos."], sit="Una variable local nombre debe usarse como valor del campo con ese mismo nombre sin repetirlo. ¿Qué sintaxis de struct aplicas?", cod="""struct Persona { nombre: &'static str }
fn main() {
    let nombre = "Ada";
    let p = Persona { nombre };
    println!("{}", p.nombre);
}""", h="usa la forma abreviada para inicializar el campo nombre", pr=("Escribir solo el identificador de un campo con variable homónima es inicialización ___ .", "abreviada"), pr2=("El campo abreviado nombre equivale a nombre: ___.", "nombre"), ec="creer que la abreviatura crea un campo con nombre diferente", out="Ada"),
K("Struct de tupla", d="estructura cuyos campos se identifican por posición", u="definir un tipo propio compacto con componentes tipados", mas="Una estructura de tupla se declara con campos tipados entre paréntesis y termina en punto y coma. Sus campos públicos se acceden por índice como .0. Aunque sus campos se parezcan a los de otra estructura, cada tipo sigue siendo distinto.", k=["Una estructura de tupla usa campos posicionales.", "La declaración termina con punto y coma.", "Los campos públicos se consultan con índices como .0."], sit="Quieres envolver un entero en un tipo propio compacto sin asignar nombre a su único campo. ¿Qué forma de estructura declaras?", cod="""struct Metros(i32);
fn main() {
    let distancia = Metros(12);
    println!("{}", distancia.0);
}""", h="construye el struct de tupla y lee su primer campo", pr=("El struct cuyos campos se escriben entre paréntesis se llama struct de ___.", "tupla"), pr2=("El primer campo de Metros se consulta mediante el índice ___.", "0"), ec="usar llaves para inicializar campos posicionales de una estructura de tupla", out="12"),
K("Métodos", d="funciones asociadas a un tipo y declaradas en un bloque impl", u="organizar operaciones junto al tipo que manipulan", mas="Un método se define dentro de impl Tipo y recibe a menudo self, &self o &mut self como primer parámetro. La sintaxis de punto llama el método sobre una instancia. El receptor indica si toma, lee o modifica la instancia.", k=["impl contiene métodos asociados a un tipo.", "&self presta la instancia para lectura.", "&mut self permite modificar la instancia."], sit="Quieres invocar una operación relacionada con un tipo usando la sintaxis instancia.metodo(). ¿Dónde defines esa función?", cod="""struct Caja { valor: i32 }
impl Caja {
    fn leer(&self) -> i32 { self.valor }
}
fn main() {
    let c = Caja { valor: 7 };
    println!("{}", c.leer());
}""", h="define e invoca un método de lectura de Caja", pr=("Los métodos de un tipo se declaran en un bloque ___.", "impl"), pr2=("El receptor de un método que solo lee la instancia se escribe ___.", "&self"), ec="definir el método fuera de impl cuando debía pertenecer al tipo", out="7"),
K("Método mutable", d="método cuyo receptor &mut self autoriza modificar la instancia", u="encapsular cambios de estado dentro de un tipo", mas="Un método con &mut self recibe un préstamo mutable de su instancia. El llamador necesita una instancia declarada con mut para invocarlo. El receptor limita el cambio a un acceso exclusivo durante la llamada.", k=["&mut self es un receptor mutable.", "La instancia llamadora debe ser mutable.", "Un método mutable puede cambiar los campos de self."], sit="Un método debe incrementar un campo de su instancia y el cambio debe persistir. ¿Qué receptor declaras?", cod="""struct Contador { valor: i32 }
impl Contador {
    fn incrementar(&mut self) { self.valor += 1; }
}
fn main() {
    let mut c = Contador { valor: 1 };
    c.incrementar();
    println!("{}", c.valor);
}""", h="incrementa el campo mediante un método mutable", pr=("El receptor que permite modificar la instancia es ___.", "&mut self"), pr2=("La instancia que llama un método &mut self debe declararse con ___.", "mut"), ec="invocar un método mutable sobre una instancia inmutable", out="2"),
K("Función asociada", d="función de impl sin parámetro self invocada con el nombre del tipo", u="proporcionar un constructor o una operación del tipo", mas="Una función asociada se declara dentro de impl pero no recibe self. Se invoca con la ruta Tipo::funcion(...), no con la sintaxis de método sobre una instancia. String::from es un ejemplo conocido.", k=["Una función asociada no recibe self.", "Se invoca con Tipo::nombre(...).", "String::from es una función asociada."], sit="Quieres crear una instancia con una operación que no necesita un objeto existente como receptor. ¿Cómo declaras esa función en impl?", cod="""struct Par(i32, i32);
impl Par {
    fn nuevo(a: i32, b: i32) -> Self { Self(a, b) }
}
fn main() {
    let p = Par::nuevo(2, 5);
    println!("{},{}", p.0, p.1);
}""", h="construye un Par con una función asociada sin receptor", pr=("Una función de impl que no recibe self es una función ___.", "asociada"), pr2=("La llamada a la función asociada nuevo usa la ruta Par::___ .", "nuevo"), ec="llamar una función asociada con sintaxis de punto como si tuviera receptor", out="2,5"),
K("Sintaxis de actualización", d="forma de struct que copia los campos restantes de otra instancia", u="crear un registro basado en otro y cambiar algunos campos", mas="La sintaxis ..otra al final de una instancia struct toma de otra los campos no especificados. Los campos usados se mueven o copian según sus tipos. La expresión de actualización debe ir al final.", k=["..instancia proporciona campos restantes.", "La expresión de actualización se escribe al final.", "Los campos no Copy pueden moverse desde la instancia original."], sit="Quieres construir un perfil con una edad distinta y conservar de un perfil previo el resto de los campos. ¿Qué sintaxis de actualización utilizas?", cod="""struct Perfil { edad: u8, activo: bool }
fn main() {
    let base = Perfil { edad: 18, activo: true };
    let nuevo = Perfil { edad: 20, ..base };
    println!("{} {}", nuevo.edad, nuevo.activo);
}""", h="crea un perfil cambiando edad y usando activo de base", pr=("La sintaxis que toma los campos restantes de una instancia es ..___.", "base"), pr2=("La actualización ..base debe escribirse al ___ de la instancia.", "final"), ec="poner ..base antes de los campos explícitos", out="20 true"),
K("Derivar Debug", d="atributo que genera una implementación de formato de depuración", u="imprimir una instancia con {:?} sin escribir la implementación manual", mas="#[derive(Debug)] pide al compilador generar la implementación del rasgo Debug cuando sus campos también lo implementan. La instancia se imprime normalmente con {:?}. Debug es para inspección, no garantiza un formato estable para persistencia.", k=['#[derive(Debug)] genera una implementación Debug.', 'Los campos también deben implementar Debug.', '{:?} usa la representación de depuración.'], sit="Necesitas inspeccionar una instancia propia con println! y el especificador {:?}. ¿Qué atributo agregas al tipo?", cod="""#[derive(Debug)]
struct Punto { x: i32 }
fn main() {
    println!("{:?}", Punto { x: 3 });
}""", h="deriva Debug e imprime la instancia Punto", pr=("El atributo que genera la implementación de depuración es #[derive(___)].", "Debug"), pr2=("El especificador de formato para depuración es ___.", "{:?}"), ec="usar {:?} en un tipo propio que no implementa Debug", out="Punto { x: 3 }"),
K("Desestructurar estructuras", d="extraer campos nombrados de una instancia mediante un patrón", u="obtener varios campos locales en una sola vinculación", mas="Un patrón struct escribe el nombre del tipo y los campos que se desean vincular. Los campos omitidos se pueden ignorar con .. cuando no se requiere comprobarlos. La desestructuración puede tomar o copiar campos según su tipo y patrón.", k=["Un patrón struct nombra los campos que extrae.", ".. omite los campos restantes del patrón.", "El patrón puede mover un campo no Copy."], sit="Quieres obtener la coordenada x de un Punto e ignorar el resto de sus campos. ¿Qué forma de patrón usas?", cod="""struct Punto { x: i32, y: i32 }
fn main() {
    let p = Punto { x: 4, y: 9 };
    let Punto { x, .. } = p;
    println!("{x}");
}""", h="extrae x e ignora y mediante un patrón struct", pr=("La extracción de campos de una instancia con un patrón se llama ___.", "desestructuración"), pr2=("En un patrón struct, los campos restantes se ignoran con ___.", ".."), ec="escribir un patrón sin cubrir campos restantes ni usar ..", out="4"),
K("Struct unitario", d="estructura sin campos declarados que aporta un tipo propio", u="crear un tipo marcador sin almacenar datos", mas="Un struct unitario se declara sin llaves ni campos y termina con punto y coma. Su valor se construye con el nombre del tipo. Puede implementar rasgos o servir como marcador de tipo sin ocupar espacio para campos.", k=["Un struct unitario no declara campos.", "Su declaración termina en punto y coma.", "El valor se construye con el nombre del tipo."], sit="Necesitas un tipo marcador que identifique una política pero no almacene ningún dato. ¿Qué estructura sin campos declaras?", cod="""struct Seguro;
fn main() {
    let _marcador = Seguro;
    println!("tipo marcador");
}""", h="crea un valor del tipo unitario Seguro", pr=("La estructura propia sin campos se llama struct ___.", "unitario"), pr2=("Un struct unitario se instancia escribiendo solo su ___ de tipo.", "nombre"), ec="intentar inicializar campos inexistentes en un struct unitario", out="tipo marcador"),
]
