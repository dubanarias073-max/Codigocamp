// Código inicial al crear un archivo vacío (como las plantillas de VS Code): compila y se ejecuta con ▶ desde el primer
// momento. En Java la clase se llama igual que el archivo (Persona.java → class Persona).
const clase = (nombre) => {
  const base = nombre.replace(/\.[^.]+$/, "").replace(/[^A-Za-z0-9_]/g, "_");
  return /^[A-Za-z_]/.test(base) ? base : `_${base}`;
};

const INICIALES = {
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
