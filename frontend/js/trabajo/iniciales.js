// Código inicial al crear un archivo vacío (como las plantillas de VS Code): compila y se ejecuta con ▶ desde el primer
// momento. En Java la clase se llama igual que el archivo (Persona.java → class Persona).
const clase = (nombre) => {
  const base = nombre.replace(/\.[^.]+$/, "").replace(/[^A-Za-z0-9_]/g, "_");
  return /^[A-Za-z_]/.test(base) ? base : `_${base}`;
};

const INICIALES = {
  lua: () => `io.write("¿Cómo te llamas? ")
local nombre = io.read() or "amigo"
print("¡Hola, " .. nombre .. "! Bienvenido a Lua.")
for i = 1, 3 do
  print("Vuelta " .. i)
end
`,
  pl: () => `use strict;
use warnings;

print "¿Cómo te llamas? ";
my $nombre = <STDIN> // "amigo";
chomp $nombre;
print "¡Hola, $nombre! Bienvenido a Perl.\\n";
`,
  r: () => `cat("¿Cómo te llamas? ")
nombre <- readLines(file("stdin"), n = 1)
if (length(nombre) == 0) nombre <- "amigo"
cat("¡Hola,", nombre, "! Bienvenido a R.\\n")
notas <- c(4.5, 3.8, 5.0)
cat("Promedio:", mean(notas), "\\n")
`,
  scala: () => `import scala.io.StdIn.readLine

@main def hola(): Unit =
  print("¿Cómo te llamas? ")
  val nombre = Option(readLine()).getOrElse("amigo")
  println(s"¡Hola, $nombre! Bienvenido a Scala.")
`,
  hs: () => `main :: IO ()
main = do
  putStrLn "¿Cómo te llamas?"
  nombre <- getLine
  putStrLn ("¡Hola, " ++ nombre ++ "! Bienvenido a Haskell.")
  print (sum [1 .. 10])
`,
  exs: () => `nombre = IO.gets("¿Cómo te llamas? ") |> to_string() |> String.trim()
IO.puts("¡Hola, #{nombre}! Bienvenido a Elixir.")
Enum.each(1..3, fn i -> IO.puts("Vuelta #{i}") end)
`,
  jl: () => `print("¿Cómo te llamas? ")
nombre = readline()
println("¡Hola, $nombre! Bienvenido a Julia.")
println("Suma del 1 al 10: ", sum(1:10))
`,
  groovy: () => `def lector = new BufferedReader(new InputStreamReader(System.in))
print "¿Cómo te llamas? "
def nombre = lector.readLine() ?: "amigo"
println "¡Hola, \${nombre}! Bienvenido a Groovy."
`,
  cr: () => `print "¿Cómo te llamas? "
nombre = gets.to_s.chomp
puts "¡Hola, #{nombre}! Bienvenido a Crystal."
`,
  nim: () => `stdout.write "¿Cómo te llamas? "
let nombre = readLine(stdin)
echo "¡Hola, ", nombre, "! Bienvenido a Nim."
`,
  ml: () => `let () =
  print_string "¿Cómo te llamas? ";
  let nombre = try read_line () with End_of_file -> "amigo" in
  Printf.printf "¡Hola, %s! Bienvenido a OCaml.\\n" nombre
`,
  d: () => `import std.stdio;
import std.string;

void main()
{
    write("¿Cómo te llamas? ");
    string nombre = readln().strip();
    writeln("¡Hola, ", nombre, "! Bienvenido a D.");
}
`,
  pas: () => `program Hola;
var
  nombre: string;
begin
  write('¿Cómo te llamas? ');
  readln(nombre);
  writeln('¡Hola, ', nombre, '! Bienvenido a Pascal.');
end.
`,
  zig: () => `const std = @import("std");

pub fn main() !void {
    const salida = std.io.getStdOut().writer();
    try salida.print("¡Hola! Bienvenido a Zig.\\n", .{});
    var i: u8 = 1;
    while (i <= 3) : (i += 1) {
        try salida.print("Vuelta {d}\\n", .{i});
    }
}
`,
  lisp: () => `(format t "¿Cómo te llamas? ")
(finish-output)
(let ((nombre (or (read-line *standard-input* nil) "amigo")))
  (format t "¡Hola, ~a! Bienvenido a Common Lisp.~%" nombre))
`,
  sh: () => `#!/bin/bash
# Script de bash: ejecútalo con ./nombre.sh o bash nombre.sh
echo "¿Cómo te llamas?"
read nombre
echo "¡Hola, $nombre! Bienvenido a Bash."

for i in 1 2 3; do
  echo "Vuelta $i"
done
`,
  java: (n) => `import java.util.Scanner;

public class ${clase(n)} {
    public static void main(String[] args) {
        Scanner entrada = new Scanner(System.in);
        System.out.print("¿Cómo te llamas? ");
        String nombre = entrada.nextLine();
        System.out.println("¡Hola, " + nombre + "! Bienvenido a Java.");
    }
}
`,
  c: () => `#include <stdio.h>

int main(void) {
    char nombre[50];
    printf("¿Cómo te llamas? ");
    scanf("%49s", nombre);
    printf("¡Hola, %s! Bienvenido a C.\\n", nombre);
    return 0;
}
`,
  cpp: () => `#include <iostream>
#include <string>

int main() {
    std::string nombre;
    std::cout << "¿Cómo te llamas? ";
    std::getline(std::cin, nombre);
    std::cout << "¡Hola, " << nombre << "! Bienvenido a C++." << std::endl;
    return 0;
}
`,
  h: (n) => { const g = clase(n).toUpperCase() + "_H"; return `#ifndef ${g}\n#define ${g}\n\n// Declara aquí tus funciones, por ejemplo:\nint sumar(int a, int b);\n\n#endif\n`; },
  cs: (n) => `using System;

class ${clase(n)}
{
    static void Main()
    {
        Console.Write("¿Cómo te llamas? ");
        string nombre = Console.ReadLine();
        Console.WriteLine($"¡Hola, {nombre}! Bienvenido a C#.");
    }
}
`,
  kt: () => `fun main() {
    print("¿Cómo te llamas? ")
    val nombre = readLine() ?: "amigo"
    println("¡Hola, $nombre! Bienvenido a Kotlin.")
}
`,
  swift: () => `print("¿Cómo te llamas? ", terminator: "")
let nombre = readLine() ?? "amigo"
print("¡Hola, \\(nombre)! Bienvenido a Swift.")
`,
  php: () => `<?php
echo "¿Cómo te llamas? ";
$nombre = trim(fgets(STDIN));
echo "¡Hola, $nombre! Bienvenido a PHP.\\n";
`,
  rb: () => `print "¿Cómo te llamas? "
nombre = gets.to_s.chomp
puts "¡Hola, #{nombre}! Bienvenido a Ruby."
`,
  go: () => `package main

import "fmt"

func main() {
\tvar nombre string
\tfmt.Print("¿Cómo te llamas? ")
\tfmt.Scanln(&nombre)
\tfmt.Printf("¡Hola, %s! Bienvenido a Go.\\n", nombre)
}
`,
  rs: () => `use std::io;

fn main() {
    println!("¿Cómo te llamas?");
    let mut nombre = String::new();
    io::stdin().read_line(&mut nombre).expect("No se pudo leer");
    println!("¡Hola, {}! Bienvenido a Rust.", nombre.trim());
}
`,
};
INICIALES.cc = INICIALES.cpp; INICIALES.cxx = INICIALES.cpp; INICIALES.hpp = INICIALES.h;

/** Código inicial para un archivo nuevo, o "" si su tipo no tiene plantilla. */
// Docker: un Dockerfile y un compose.yaml que funcionan con el proyecto de Python que ya tienes.
const DOCKERFILE = `# Imagen de tu app. Constrúyela y ejecútala en la terminal:
#   docker build -t miapp .
#   docker run --rm -it miapp
FROM python:3.12-slim

WORKDIR /app

# Primero las dependencias (así Docker las guarda en caché)
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Después tu código
COPY . .

CMD ["python", "main.py"]
`;
const COMPOSE = `# Varios servicios juntos. En la terminal:
#   docker compose up -d      (levanta todo)
#   docker compose ps         (qué está corriendo)
#   docker compose logs       (lo que imprimen)
#   docker compose down       (apaga todo)
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
    depends_on:
      - db
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: secreto
      MYSQL_DATABASE: mi_base
    ports:
      - "3307:3306"
`;
const ESPECIALES = { dockerfile: DOCKERFILE, "compose.yaml": COMPOSE, "compose.yml": COMPOSE, "docker-compose.yml": COMPOSE, "docker-compose.yaml": COMPOSE,
  ".dockerignore": "__pycache__/\n*.pyc\n.venv/\nvenv/\nnode_modules/\n.git/\n.env\n" };

export function codigoInicial(ruta) {
  const nombre = ruta.split("/").pop();
  if (ESPECIALES[nombre.toLowerCase()] !== undefined) return ESPECIALES[nombre.toLowerCase()];
  const ext = (nombre.match(/\.([^.]+)$/)?.[1] || "").toLowerCase();
  return INICIALES[ext] ? INICIALES[ext](nombre) : "";
}
