// Lenguajes: 5 conceptos básicos, cada lenguaje trae su código para cada uno.
// Para añadir un lenguaje, agrega un objeto a LENGUAJES con 5 fragmentos en "c".
// run: "js" -> se puede ejecutar en el laboratorio (modo consola).
const r = String.raw;

export const CONCEPTOS = [
  { t: "Tu primer programa",
    d: "Todo programa empieza mostrando algo en pantalla. El clásico «Hola, mundo» comprueba que tu entorno funciona y te enseña la estructura mínima del lenguaje.",
    p: ["Cada lenguaje tiene su forma de imprimir texto", "Algunos necesitan una función principal (main)", "Los textos van entre comillas"] },
  { t: "Variables y tipos",
    d: "Una variable es una caja con nombre donde guardas un dato. Cada dato tiene un tipo: texto, número entero, decimal o verdadero/falso.",
    p: ["Elige nombres claros: edad, no x", "Algunos lenguajes exigen declarar el tipo y otros lo deducen", "Las constantes son valores que no cambian"] },
  { t: "Condicionales y bucles",
    d: "Los condicionales permiten que el programa decida qué camino seguir. Los bucles repiten acciones sin tener que copiar código.",
    p: ["if / else elige entre caminos", "for repite un número conocido de veces", "Cuidado con los bucles infinitos"] },
  { t: "Funciones",
    d: "Una función es un bloque de código con nombre que recibe datos, hace algo y puede devolver un resultado. Sirve para no repetir código.",
    p: ["Parámetros: los datos de entrada", "return: el resultado de salida", "Una función, una tarea"] },
  { t: "Listas y colecciones",
    d: "Una lista guarda varios valores juntos. Puedes añadir elementos, recorrerlos y contarlos.",
    p: ["Los índices suelen empezar en 0", "Se recorren con un bucle", "Añadir, quitar y buscar son las operaciones básicas"] },
];

export const LENGUAJES = [
{ n: "JavaScript", run: "js", ej: "Pruébalo aquí mismo en el laboratorio, o abre la consola del navegador con F12.",
  d: "El lenguaje de la web: da vida a las páginas y también corre en servidores con Node.js.",
  c: [
r`console.log("¡Hola, mundo!");`,
r`let nombre = "Ana";
const edad = 25;
let activo = true;
console.log(nombre, edad, activo);
console.log(typeof edad);`,
r`const nota = 8;
if (nota >= 5) {
  console.log("Aprobado");
} else {
  console.log("Suspenso");
}
for (let i = 1; i <= 3; i++) {
  console.log("Vuelta " + i);
}`,
r`function sumar(a, b) {
  return a + b;
}
console.log(sumar(2, 3));
const doble = (x) => x * 2;
console.log(doble(4));`,
r`const frutas = ["manzana", "pera", "uva"];
frutas.push("kiwi");
console.log(frutas.length);
for (const f of frutas) console.log(f);`] },

{ n: "TypeScript", ej: "Instala Node.js y ejecuta: npx tsx hola.ts",
  d: "JavaScript con tipos: detecta errores antes de ejecutar y escala mejor en proyectos grandes.",
  c: [
r`console.log("¡Hola, mundo!");`,
r`let nombre: string = "Ana";
const edad: number = 25;
let activo: boolean = true;
console.log(nombre, edad, activo);`,
r`const nota: number = 8;
if (nota >= 5) {
  console.log("Aprobado");
} else {
  console.log("Suspenso");
}
for (let i = 1; i <= 3; i++) {
  console.log("Vuelta " + i);
}`,
r`function sumar(a: number, b: number): number {
  return a + b;
}
console.log(sumar(2, 3));`,
r`const frutas: string[] = ["manzana", "pera"];
frutas.push("uva");
for (const f of frutas) console.log(f);`] },

{ n: "Python", ej: "Guarda el código como hola.py y ejecuta: python hola.py",
  d: "Sencillo y legible: ideal para empezar, análisis de datos, automatización e inteligencia artificial.",
  c: [
r`print("¡Hola, mundo!")`,
r`nombre = "Ana"
edad = 25
activo = True
print(nombre, edad, activo)
print(type(edad))`,
r`nota = 8
if nota >= 5:
    print("Aprobado")
else:
    print("Suspenso")
for i in range(1, 4):
    print("Vuelta", i)`,
r`def sumar(a, b):
    return a + b

print(sumar(2, 3))
doble = lambda x: x * 2
print(doble(4))`,
r`frutas = ["manzana", "pera", "uva"]
frutas.append("kiwi")
print(len(frutas))
for f in frutas:
    print(f)`] },

{ n: "Java", ej: "Guarda como Main.java, compila con javac Main.java y ejecuta con java Main",
  d: "Orientado a objetos, muy usado en empresas y en aplicaciones Android.",
  c: [
r`public class Main {
  public static void main(String[] args) {
    System.out.println("¡Hola, mundo!");
  }
}`,
r`// dentro de main()
String nombre = "Ana";
int edad = 25;
boolean activo = true;
System.out.println(nombre + " " + edad + " " + activo);`,
r`// dentro de main()
int nota = 8;
if (nota >= 5) {
  System.out.println("Aprobado");
} else {
  System.out.println("Suspenso");
}
for (int i = 1; i <= 3; i++) {
  System.out.println("Vuelta " + i);
}`,
r`static int sumar(int a, int b) {
  return a + b;
}
// uso dentro de main():
// System.out.println(sumar(2, 3));`,
r`import java.util.ArrayList;

// dentro de main()
ArrayList<String> frutas = new ArrayList<>();
frutas.add("manzana");
frutas.add("pera");
System.out.println(frutas.size());
for (String f : frutas) System.out.println(f);`] },

{ n: "C", ej: "Guarda como hola.c, compila con gcc hola.c -o hola y ejecuta ./hola",
  d: "Cercano a la máquina: te enseña cómo funcionan la memoria y el sistema por dentro.",
  c: [
r`#include <stdio.h>

int main(void) {
  printf("Hola, mundo!\n");
  return 0;
}`,
r`// dentro de main()
char inicial = 'A';
int edad = 25;
float altura = 1.70f;
printf("%c %d %.2f\n", inicial, edad, altura);`,
r`// dentro de main()
int nota = 8;
if (nota >= 5) {
  printf("Aprobado\n");
} else {
  printf("Suspenso\n");
}
for (int i = 1; i <= 3; i++) {
  printf("Vuelta %d\n", i);
}`,
r`int sumar(int a, int b) {
  return a + b;
}
// uso dentro de main():
// printf("%d\n", sumar(2, 3));`,
r`// dentro de main()
int numeros[3] = {10, 20, 30};
for (int i = 0; i < 3; i++) {
  printf("%d\n", numeros[i]);
}`] },

{ n: "C++", ej: "Guarda como hola.cpp, compila con g++ hola.cpp -o hola y ejecuta ./hola",
  d: "Rápido y versátil: videojuegos, motores gráficos y software de sistemas.",
  c: [
r`#include <iostream>

int main() {
  std::cout << "Hola, mundo!" << std::endl;
  return 0;
}`,
r`// dentro de main()
std::string nombre = "Ana";
int edad = 25;
bool activo = true;
std::cout << nombre << " " << edad << " " << activo << std::endl;`,
r`// dentro de main()
int nota = 8;
if (nota >= 5) {
  std::cout << "Aprobado\n";
} else {
  std::cout << "Suspenso\n";
}
for (int i = 1; i <= 3; i++) {
  std::cout << "Vuelta " << i << "\n";
}`,
r`int sumar(int a, int b) {
  return a + b;
}
// uso dentro de main():
// std::cout << sumar(2, 3);`,
r`#include <vector>

// dentro de main()
std::vector<std::string> frutas = {"manzana", "pera"};
frutas.push_back("uva");
for (const auto& f : frutas) std::cout << f << "\n";`] },

{ n: "C#", ej: "Instala .NET y ejecuta: dotnet new console, pega el código en Program.cs y luego dotnet run",
  d: "Lenguaje de Microsoft para aplicaciones, web y videojuegos con Unity.",
  c: [
r`Console.WriteLine("¡Hola, mundo!");`,
r`string nombre = "Ana";
int edad = 25;
bool activo = true;
Console.WriteLine(nombre + " " + edad + " " + activo);`,
r`int nota = 8;
if (nota >= 5) Console.WriteLine("Aprobado");
else Console.WriteLine("Suspenso");
for (int i = 1; i <= 3; i++) {
  Console.WriteLine("Vuelta " + i);
}`,
r`static int Sumar(int a, int b) {
  return a + b;
}
Console.WriteLine(Sumar(2, 3));`,
r`var frutas = new List<string> { "manzana", "pera" };
frutas.Add("uva");
foreach (var f in frutas) Console.WriteLine(f);`] },

{ n: "PHP", ej: "Con XAMPP: guarda hola.php en la carpeta htdocs y abre http://localhost/hola.php (o usa php hola.php)",
  d: "Programación del lado del servidor; mueve gran parte de la web, incluido WordPress.",
  c: [
r`<?php
echo "¡Hola, mundo!";`,
r`<?php
$nombre = "Ana";
$edad = 25;
$activo = true;
echo "$nombre tiene $edad años";`,
r`<?php
$nota = 8;
if ($nota >= 5) {
  echo "Aprobado\n";
} else {
  echo "Suspenso\n";
}
for ($i = 1; $i <= 3; $i++) {
  echo "Vuelta $i\n";
}`,
r`<?php
function sumar($a, $b) {
  return $a + $b;
}
echo sumar(2, 3);`,
r`<?php
$frutas = ["manzana", "pera"];
$frutas[] = "uva";
foreach ($frutas as $f) {
  echo $f . "\n";
}`] },

{ n: "Go", ej: "Guarda como hola.go y ejecuta: go run hola.go",
  d: "Creado por Google: simple, muy rápido y excelente para servidores y la nube.",
  c: [
r`package main

import "fmt"

func main() {
  fmt.Println("¡Hola, mundo!")
}`,
r`// dentro de main()
nombre := "Ana"
var edad int = 25
activo := true
fmt.Println(nombre, edad, activo)`,
r`// dentro de main()
nota := 8
if nota >= 5 {
  fmt.Println("Aprobado")
} else {
  fmt.Println("Suspenso")
}
for i := 1; i <= 3; i++ {
  fmt.Println("Vuelta", i)
}`,
r`func sumar(a int, b int) int {
  return a + b
}
// uso dentro de main():
// fmt.Println(sumar(2, 3))`,
r`// dentro de main()
frutas := []string{"manzana", "pera"}
frutas = append(frutas, "uva")
for _, f := range frutas {
  fmt.Println(f)
}`] },

{ n: "Rust", ej: "Guarda como hola.rs, compila con rustc hola.rs y ejecuta ./hola (o usa cargo run)",
  d: "Seguridad de memoria sin recolector de basura, con rendimiento parecido al de C.",
  c: [
r`fn main() {
    println!("¡Hola, mundo!");
}`,
r`// dentro de main()
let nombre = "Ana";
let edad: i32 = 25;
let mut puntos = 0; // mut: se puede cambiar
puntos += 10;
println!("{} {} {}", nombre, edad, puntos);`,
r`// dentro de main()
let nota = 8;
if nota >= 5 {
    println!("Aprobado");
} else {
    println!("Suspenso");
}
for i in 1..=3 {
    println!("Vuelta {}", i);
}`,
r`fn sumar(a: i32, b: i32) -> i32 {
    a + b
}
// uso dentro de main():
// println!("{}", sumar(2, 3));`,
r`// dentro de main()
let mut frutas = vec!["manzana", "pera"];
frutas.push("uva");
for f in &frutas {
    println!("{}", f);
}`] },

{ n: "Swift", ej: "En Mac, guarda como hola.swift y ejecuta: swift hola.swift (o usa Xcode)",
  d: "El lenguaje de Apple para crear apps de iPhone, iPad y Mac.",
  c: [
r`print("¡Hola, mundo!")`,
r`let nombre = "Ana"
var edad = 25
edad += 1
print(nombre, edad)`,
r`let nota = 8
if nota >= 5 {
  print("Aprobado")
} else {
  print("Suspenso")
}
for i in 1...3 {
  print("Vuelta \(i)")
}`,
r`func sumar(_ a: Int, _ b: Int) -> Int {
  return a + b
}
print(sumar(2, 3))`,
r`var frutas = ["manzana", "pera"]
frutas.append("uva")
for f in frutas {
  print(f)
}`] },

{ n: "Kotlin", ej: "La forma más fácil es IntelliJ IDEA: crea un proyecto Kotlin y pulsa Run",
  d: "Moderno y conciso; es el lenguaje preferido para Android.",
  c: [
r`fun main() {
  println("¡Hola, mundo!")
}`,
r`val nombre = "Ana"   // val no cambia
var edad = 25         // var sí cambia
edad += 1
println("$nombre $edad")`,
r`val nota = 8
if (nota >= 5) println("Aprobado") else println("Suspenso")
for (i in 1..3) {
  println("Vuelta $i")
}`,
r`fun sumar(a: Int, b: Int): Int {
  return a + b
}
println(sumar(2, 3))`,
r`val frutas = mutableListOf("manzana", "pera")
frutas.add("uva")
for (f in frutas) println(f)`] },

{ n: "Ruby", ej: "Guarda como hola.rb y ejecuta: ruby hola.rb",
  d: "Pensado para la felicidad del programador; es la base del framework Rails.",
  c: [
r`puts "¡Hola, mundo!"`,
r`nombre = "Ana"
edad = 25
activo = true
puts "#{nombre} tiene #{edad}"`,
r`nota = 8
if nota >= 5
  puts "Aprobado"
else
  puts "Suspenso"
end
3.times do |i|
  puts "Vuelta #{i + 1}"
end`,
r`def sumar(a, b)
  a + b
end
puts sumar(2, 3)`,
r`frutas = ["manzana", "pera"]
frutas << "uva"
frutas.each { |f| puts f }`] },
];
