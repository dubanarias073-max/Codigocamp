// Lecciones de TypeScript. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"TypeScript es JavaScript con tipos que detectan errores antes de ejecutar.",
    p:["Se compila a JavaScript", "Usa console.log para mostrar"],
    c:`console.log("¡Hola, CódigoCamp!");` },
  { m:"Primeros pasos", t:"Tipos", x:"Indicas el tipo con dos puntos.",
    p:["number, string, boolean", "Un tipo equivocado da error"],
    c:`const nombre: string = "Ana";
let edad: number = 20;
console.log(nombre, edad + 1);` },
  { m:"Fundamentos", t:"Funciones con tipos", x:"Puedes indicar el tipo de cada parámetro y del resultado.",
    p:["Tipos en parámetros y en el resultado", "El compilador avisa si te equivocas"],
    c:`function sumar(a: number, b: number): number {
  return a + b;
}
console.log(sumar(2, 3));` },
  { m:"Fundamentos", t:"Interfaces", x:"Una interface describe la forma que debe tener un objeto.",
    p:["Define nombres y tipos de propiedades", "Si falta una propiedad, hay error"],
    c:`interface Alumno {
  nombre: string;
  nota: number;
}
const a: Alumno = { nombre: "Ana", nota: 9 };
console.log(a.nombre, a.nota);` },
  { m:"Intermedio", t:"Arreglos y tuplas", x:"Un arreglo guarda varios valores del mismo tipo. Una tupla fija cuántos elementos hay y qué tipo tiene cada posición.",
    p:["number[] es un arreglo de números", "Una tupla [string, number] fija el orden de los tipos", "map, filter y reduce transforman arreglos sin cambiar el original"],
    c:"const notas: number[] = [7, 9, 8];\nconst par: [string, number] = [\"Ana\", 20];\n\nconst dobles = notas.map((n) => n * 2);\nconst altas = notas.filter((n) => n >= 8);\nconst suma = notas.reduce((a, n) => a + n, 0);\n\nconsole.log(dobles, altas, suma);\nconsole.log(par[0], par[1]);",
    r:"Calcula el promedio de notas dividiendo la suma entre notas.length.",
    e:"Escribir const notas: number[] = [\"7\"] da error: el arreglo solo admite números." },
  { m:"Intermedio", t:"Clases y modificadores", x:"Las clases agrupan datos y comportamiento. TypeScript añade public, private y readonly para controlar el acceso.",
    p:["constructor crea el objeto", "private oculta el miembro fuera de la clase", "Poner el modificador en el parámetro declara la propiedad automáticamente"],
    c:"class Cuenta {\n  constructor(private saldo: number, readonly titular: string) {}\n\n  depositar(monto: number): void {\n    this.saldo += monto;\n  }\n\n  verSaldo(): number {\n    return this.saldo;\n  }\n}\n\nconst c = new Cuenta(100, \"Ana\");\nc.depositar(50);\nconsole.log(c.titular, c.verSaldo());",
    r:"Añade un método retirar que no deje el saldo en negativo.",
    e:"Acceder a c.saldo desde fuera es un error de compilación porque es private." },
  { m:"Avanzado", t:"Uniones, literales y estrechamiento", x:"Un tipo unión permite varios tipos posibles. Con typeof o in, TypeScript \"estrecha\" el tipo dentro de cada rama.",
    p:["A | B significa «A o B»", "Los tipos literales limitan a valores exactos", "typeof dentro de un if estrecha el tipo"],
    c:"type Estado = \"cargando\" | \"listo\" | \"error\";\n\nfunction mostrar(valor: string | number): string {\n  if (typeof valor === \"string\") {\n    return valor.toUpperCase();\n  }\n  return valor.toFixed(2);\n}\n\nconst e: Estado = \"listo\";\nconsole.log(e, mostrar(\"hola\"), mostrar(3.14159));",
    r:"Prueba asignar \"otro\" a una variable de tipo Estado y lee el error.",
    e:"Usar any para evitar errores quita toda la protección; prefiere unknown y comprueba el tipo." },
  { m:"Avanzado", t:"Genéricos", x:"Los genéricos escriben una función o clase una sola vez y la usan con cualquier tipo, sin perder las comprobaciones.",
    p:["<T> es un tipo que se decide al usar la función", "Se pueden restringir con extends", "Array<T> y Promise<T> son genéricos que ya usas"],
    c:"function primero<T>(lista: T[]): T | undefined {\n  return lista[0];\n}\n\nfunction conId<T extends { id: number }>(obj: T): number {\n  return obj.id;\n}\n\nconsole.log(primero([10, 20, 30]));\nconsole.log(primero([\"a\", \"b\"]));\nconsole.log(conId({ id: 7, nombre: \"Ana\" }));",
    r:"Escribe una función ultimo<T> que devuelva el último elemento.",
    e:"Olvidar el tipo de retorno T | undefined cuando la lista puede estar vacía." },
  { m:"Experto", t:"Tipos utilitarios", x:"TypeScript trae tipos que transforman otros: Partial, Required, Pick, Omit y Record evitan repetir definiciones.",
    p:["Partial<T> vuelve opcionales todas las propiedades", "Pick y Omit eligen o quitan propiedades", "Record<K, V> crea un objeto con claves K y valores V"],
    c:"interface Usuario {\n  id: number;\n  nombre: string;\n  correo: string;\n}\n\nconst cambios: Partial<Usuario> = { nombre: \"Luz\" };\nconst resumen: Pick<Usuario, \"id\" | \"nombre\"> = { id: 1, nombre: \"Ana\" };\nconst puntos: Record<string, number> = { ana: 10, luis: 7 };\n\nconsole.log(cambios, resumen, puntos);",
    r:"Crea un tipo SinCorreo con Omit<Usuario, \"correo\">." },
  { m:"Experto", t:"Módulos, configuración y herramientas", x:"Un proyecto real divide el código en módulos y configura el compilador en tsconfig.json con el modo estricto.",
    p:["export e import comparten código entre archivos", "\"strict\": true activa las comprobaciones más útiles", "ESLint y Prettier mantienen el código limpio"],
    c:"// tsconfig.json recomendado\n// {\n//   \"compilerOptions\": {\n//     \"target\": \"ES2022\",\n//     \"strict\": true,\n//     \"outDir\": \"dist\"\n//   }\n// }\n\nexport function saludar(nombre: string): string {\n  return `Hola, ${nombre}`;\n}\n\nconsole.log(saludar(\"CódigoCamp\"));",
    r:"Activa \"strict\" en un proyecto y corrige los errores que aparezcan.",
    e:"Desactivar strict para que desaparezcan errores esconde fallos reales." },
];
