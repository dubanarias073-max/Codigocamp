// Lecciones de Rust. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"Rust es muy rápido y seguro con la memoria.",
    p:["fn main es el inicio", "println! lleva signo de exclamación"],
    c:`fn main() {
  println!("¡Hola, CódigoCamp!");
}` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"Las variables son inmutables salvo que uses mut.",
    p:["let crea una variable", "let mut permite cambiarla"],
    c:`fn main() {
  let mut edad = 20;
  edad += 1;
  if edad >= 18 {
    println!("Mayor de edad: {}", edad);
  }
}` },
  { m:"Fundamentos", t:"Bucles", x:"for recorre un rango. 1..=5 incluye el 5.",
    p:["1..5 llega hasta el 4", "1..=5 llega hasta el 5"],
    c:`fn main() {
  for i in 1..=5 {
    println!("Vuelta {}", i);
  }
}` },
  { m:"Fundamentos", t:"Funciones", x:"fn define una función. La última expresión sin ; es el resultado.",
    p:["-> indica el tipo que devuelve", "Sin ; al final se devuelve el valor"],
    c:`fn doble(n: i32) -> i32 {
  n * 2
}

fn main() {
  println!("{}", doble(21));
}` },
  { m:"Intermedio", t:"Vectores y HashMap", x:"Vec<T> es una lista que crece y HashMap asocia claves con valores. Los iteradores los transforman.",
    p:["vec![] crea un vector", "push agrega al final", "iter().map().collect() transforma"],
    c:"use std::collections::HashMap;\n\nfn main() {\n  let mut nums = vec![1, 2, 3];\n  nums.push(4);\n  let dobles: Vec<i32> = nums.iter().map(|n| n * 2).collect();\n  println!(\"{:?}\", dobles);\n\n  let mut edades = HashMap::new();\n  edades.insert(\"Ana\", 20);\n  edades.insert(\"Luis\", 25);\n  println!(\"{:?}\", edades.get(\"Ana\"));\n}",
    r:"Suma todos los elementos con nums.iter().sum::<i32>()." },
  { m:"Intermedio", t:"Structs y métodos", x:"Las struct agrupan datos y los métodos se declaran en un bloque impl.",
    p:["struct define los campos", "impl agrega métodos", "&self presta la instancia sin tomarla"],
    c:"struct Persona {\n  nombre: String,\n  edad: u32,\n}\n\nimpl Persona {\n  fn saludar(&self) -> String {\n    format!(\"Hola, soy {} y tengo {}\", self.nombre, self.edad)\n  }\n}\n\nfn main() {\n  let p = Persona { nombre: String::from(\"Ana\"), edad: 20 };\n  println!(\"{}\", p.saludar());\n}",
    r:"Añade un método es_mayor que devuelva bool." },
  { m:"Avanzado", t:"Propiedad y préstamos", x:"Cada valor tiene un único dueño. Se puede prestar con referencias (&) sin entregar la propiedad.",
    p:["Al asignar un String se mueve su propiedad", "&valor presta de solo lectura", "&mut permite modificar, de una en una"],
    c:"fn longitud(texto: &String) -> usize {\n  texto.len()\n}\n\nfn agregar(texto: &mut String) {\n  texto.push_str(\" mundo\");\n}\n\nfn main() {\n  let mut s = String::from(\"hola\");\n  println!(\"{}\", longitud(&s));\n  agregar(&mut s);\n  println!(\"{}\", s);\n}",
    r:"Intenta usar s después de moverla a otra variable y lee el error del compilador.",
    e:"Dos referencias mutables a la vez no se permiten." },
  { m:"Avanzado", t:"Option, Result y enums", x:"Rust no tiene null ni excepciones: usa Option para valores que pueden faltar y Result para errores.",
    p:["Option<T> es Some(valor) o None", "Result<T, E> es Ok o Err", "match y ? manejan ambos casos"],
    c:"fn dividir(a: i32, b: i32) -> Result<i32, String> {\n  if b == 0 {\n    return Err(String::from(\"división entre 0\"));\n  }\n  Ok(a / b)\n}\n\nfn main() {\n  match dividir(10, 2) {\n    Ok(r) => println!(\"Resultado: {}\", r),\n    Err(e) => println!(\"Error: {}\", e),\n  }\n  let nums = vec![1, 2, 3];\n  println!(\"{:?}\", nums.get(10));\n}",
    r:"Llama a dividir(5, 0) y muestra el error.",
    e:"unwrap() entra en pánico si hay un error; úsalo solo en pruebas." },
  { m:"Experto", t:"Traits y genéricos", x:"Un trait define comportamiento compartido. Los genéricos escriben una función para muchos tipos.",
    p:["trait declara métodos", "impl Trait for Tipo lo implementa", "<T: Trait> restringe un genérico"],
    c:"trait Sonido {\n  fn hacer(&self) -> String;\n}\n\nstruct Perro;\nimpl Sonido for Perro {\n  fn hacer(&self) -> String { String::from(\"Guau\") }\n}\n\nfn mostrar<T: Sonido>(animal: T) {\n  println!(\"{}\", animal.hacer());\n}\n\nfn main() {\n  mostrar(Perro);\n}",
    r:"Crea la struct Gato y haz que también implemente Sonido." },
  { m:"Experto", t:"Cargo, pruebas y concurrencia", x:"Cargo compila, prueba y gestiona paquetes. Rust evita carreras de datos en tiempo de compilación.",
    p:["cargo test ejecuta las pruebas", "#[test] marca una función de prueba", "thread::spawn crea hilos"],
    c:"use std::thread;\n\nfn main() {\n  let hilo = thread::spawn(|| {\n    println!(\"Hola desde otro hilo\");\n  });\n  hilo.join().unwrap();\n  println!(\"Fin\");\n}",
    r:"Lanza 3 hilos con un bucle y espera a todos con join." },
];
