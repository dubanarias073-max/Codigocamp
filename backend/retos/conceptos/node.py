"""Node.js: JavaScript fuera del navegador, npm, módulos, servidores y APIs. 3 etapas."""
from ..generador import K
from .node_e678 import E6, E7, E8
from .node_e45 import E4, E5

E1 = [
K("Qué es Node.js", d="entorno que ejecuta JavaScript fuera del navegador", u="crear servidores, herramientas de terminal y APIs con JavaScript",
  mas="Node.js usa el motor V8 de Chrome para ejecutar JavaScript en tu computador o en un servidor. No tiene document ni window, pero sí acceso a archivos, red y procesos. Se ejecuta con node archivo.js.",
  k=["Node.js ejecuta JavaScript fuera del navegador.", "Node.js usa el motor V8 de Chrome.", "En Node.js no existen document ni window."],
  sit="Quieres usar JavaScript para crear el servidor de tu app, no solo la página del navegador. ¿Qué entorno usas?",
  cod="""// hola.js — se ejecuta con: node hola.js
console.log("Hola desde Node", process.version);""", h="imprime un saludo y la versión de Node",
  pr=("El entorno que ejecuta JavaScript fuera del navegador es ___. (4 letras)", "node", "nodejs"),
  pr2=("El motor de JavaScript que usa Node es ___. (2 caracteres)", "v8"),
  ec="usar document o window en código que corre en Node", out="Hola desde Node v20.18.0"),
K("npm", d="gestor de paquetes que viene con Node.js", u="instalar librerías y ejecutar scripts del proyecto",
  mas="npm init -y crea package.json, npm install paquete agrega una dependencia y npm run nombre ejecuta un script. Los paquetes se guardan en node_modules, que nunca se sube a Git porque se reinstala con npm install.",
  k=["npm instala librerías de JavaScript.", "npm init -y crea el archivo package.json.", "La carpeta node_modules no se sube a Git."],
  sit="Necesitas agregar la librería express a tu proyecto de Node. ¿Qué herramienta usas?",
  cod="""npm init -y
npm install express""", h="crea package.json e instala express",
  pr=("El gestor de paquetes que viene con Node es ___. (3 letras)", "npm"),
  pr2=("Los paquetes instalados se guardan en la carpeta node___. (8 caracteres)", "_modules"),
  ec="subir la carpeta node_modules al repositorio", out="added 64 packages in 2s"),
K("package.json", d="archivo que describe el proyecto y sus dependencias", u="que cualquiera instale lo mismo y ejecute los mismos scripts",
  mas="Tiene el nombre, la versión, las dependencias (dependencies y devDependencies) y los scripts, como \"dev\" o \"start\". package-lock.json fija las versiones exactas. Con \"type\": \"module\" se usa import/export.",
  k=["package.json lista las dependencias del proyecto.", "Los scripts de package.json se ejecutan con npm run.", "package-lock.json fija las versiones exactas."],
  sit="Quieres que npm run dev inicie tu servidor con una orden corta. ¿En qué archivo defines ese script?",
  cod="""{
  "name": "mi-api",
  "type": "module",
  "scripts": { "dev": "node --watch server.js" },
  "dependencies": { "express": "^4.21.0" }
}""", h="define el script dev y la dependencia express",
  pr=("El archivo que describe un proyecto de Node es package.___. (4 letras)", "json"),
  pr2=("Los scripts de package.json se ejecutan con npm ___. (3 letras)", "run"),
  ec="borrar package-lock.json y recibir versiones distintas", out=""),
K("Módulos", d="archivos que exportan e importan código entre sí", u="dividir el proyecto en partes pequeñas y reutilizables",
  mas="Con ES Modules se usa export y import (y \"type\": \"module\" en package.json o archivos .mjs). El estilo antiguo CommonJS usa module.exports y require. Los módulos de Node, como fs o path, se importan con el prefijo node:.",
  k=["export comparte código de un módulo.", "import trae código de otro módulo.", "CommonJS usa require en lugar de import."],
  sit="Escribiste funciones de cálculo en calculos.js y quieres usarlas en server.js. ¿Qué mecanismo usas?",
  cod="""// calculos.js
export const sumar = (a, b) => a + b;

// main.js
import { sumar } from "./calculos.js";
console.log(sumar(2, 3));""", h="exporta una función y la usa desde otro archivo",
  pr=("La palabra que comparte código desde un módulo es ___. (6 letras)", "export"),
  pr2=("En CommonJS, los módulos se cargan con ___. (7 letras)", "require"),
  ec="mezclar require e import en el mismo archivo", out="5"),
K("Sistema de archivos", d="módulo fs para leer y escribir archivos", u="guardar datos, leer configuraciones o procesar archivos",
  mas="node:fs/promises ofrece readFile, writeFile, mkdir y readdir con promesas. Se usan con await. path.join arma rutas sin preocuparte por / o \\ según el sistema.",
  k=["El módulo fs lee y escribe archivos.", "fs/promises permite usar await al leer archivos.", "path.join arma rutas válidas en cualquier sistema."],
  sit="Tu programa de Node debe guardar una lista de tareas en un archivo tareas.json. ¿Qué módulo usas?",
  cod="""import { writeFile, readFile } from "node:fs/promises";
await writeFile("tareas.json", JSON.stringify(["estudiar"]));
console.log(await readFile("tareas.json", "utf8"));""", h="escribe un archivo JSON y lo vuelve a leer",
  pr=("El módulo de Node para leer y escribir archivos es ___. (2 letras)", "fs"),
  pr2=("Para unir partes de una ruta se usa path.___. (4 letras)", "join"),
  ec="olvidar await y usar el archivo antes de que termine de escribirse", out='["estudiar"]'),
K("process y argumentos", d="objeto con información y control del programa en ejecución", u="leer argumentos, variables de entorno y terminar el programa",
  mas="process.argv tiene los argumentos de la terminal (los dos primeros son node y el archivo). process.env tiene las variables de entorno y process.exit(código) termina el programa. Con node --env-file=.env se cargan variables desde un archivo.",
  k=["process.argv contiene los argumentos de la terminal.", "process.env contiene las variables de entorno.", "process.exit termina el programa."],
  sit="Tu programa debe leer el nombre que el usuario escribe después de node saludo.js. ¿Qué usas?",
  cod="""// node saludo.js Ana
const nombre = process.argv[2] ?? "mundo";
console.log(`Hola, ${nombre}`);""", h="saluda con el nombre recibido por la terminal",
  pr=("La lista de argumentos de la terminal está en process.___. (4 letras)", "argv"),
  pr2=("Las variables de entorno están en process.___. (3 letras)", "env"),
  ec="leer process.argv[0] esperando el primer argumento del usuario", out="Hola, Ana"),
]

E2 = [
K("Asincronía en Node", d="forma de hacer tareas lentas sin bloquear el programa", u="atender muchas peticiones a la vez con un solo hilo",
  mas="Node tiene un bucle de eventos: mientras espera disco o red, sigue atendiendo otras cosas. Las tareas lentas devuelven promesas que se esperan con await dentro de funciones async. Las versiones Sync (readFileSync) bloquean y conviene evitarlas en servidores.",
  k=["El bucle de eventos permite atender muchas tareas a la vez.", "await espera una promesa dentro de una función async.", "Las funciones Sync bloquean el programa."],
  sit="Tu servidor se congela mientras lee un archivo grande y nadie más puede entrar. ¿Qué forma de programar lo evita?",
  cod="""const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
console.log("inicio");
await esperar(100);
console.log("fin");""", h="espera sin bloquear y luego continúa",
  pr=("La palabra que espera una promesa es ___. (5 letras)", "await"),
  pr2=("El mecanismo de Node que atiende tareas sin bloquear es el bucle de ___. (7 letras)", "eventos"),
  ec="usar readFileSync dentro de un servidor con muchos usuarios", out="inicio\nfin"),
K("Servidor HTTP", d="programa que responde peticiones de navegadores y apps", u="crear tu propia API o página dinámica",
  mas="El módulo node:http crea un servidor con createServer y lo pone a escuchar con listen. Cada petición trae req (método, URL, cabeceras) y se responde con res. En la práctica se usan frameworks como Express que lo simplifican.",
  k=["createServer crea un servidor HTTP.", "listen pone el servidor a escuchar en un puerto.", "Cada petición tiene un objeto req y uno res."],
  sit="Quieres que tu programa de Node responda «Hola» cuando abras localhost:3000 en el navegador. ¿Qué creas?",
  cod="""import { createServer } from "node:http";
createServer((req, res) => res.end("Hola")).listen(3000);
console.log("Escuchando en http://localhost:3000");""", h="crea un servidor que responde Hola en el puerto 3000",
  pr=("La función que crea un servidor HTTP es create___. (6 letras)", "server"),
  pr2=("La función que pone a escuchar el servidor es ___. (6 letras)", "listen"),
  ec="olvidar res.end y dejar la petición esperando para siempre", out="Escuchando en http://localhost:3000"),
K("Express", d="framework minimalista para crear servidores y APIs", u="definir rutas y respuestas con muy poco código",
  mas="app.get(ruta, manejador) responde a GET; también existen post, put y delete. express.json() lee cuerpos JSON y res.json() responde en JSON. app.listen(puerto) arranca el servidor.",
  k=["app.get define una ruta para peticiones GET.", "res.json responde con datos JSON.", "express.json permite leer cuerpos JSON."],
  sit="Quieres crear rápido una API con rutas como GET /productos sin manejar HTTP a mano. ¿Qué framework usas?",
  cod="""import express from "express";
const app = express();
app.use(express.json());
app.get("/productos", (req, res) => res.json([{ id: 1, nombre: "Pan" }]));
app.listen(3000);""", h="crea una API que devuelve productos en JSON",
  pr=("El framework de servidores más usado en Node es ___. (7 letras)", "express"),
  pr2=("Para responder en formato JSON se usa res.___. (4 letras)", "json"),
  ec="olvidar app.use(express.json()) y recibir el cuerpo vacío", out='[{"id":1,"nombre":"Pan"}]'),
K("API REST", d="estilo de API que usa URLs y métodos HTTP para manejar recursos", u="que el frontend lea y modifique datos del servidor",
  mas="Cada recurso tiene una URL (/tareas) y los métodos indican la acción: GET lee, POST crea, PUT o PATCH actualiza y DELETE borra. Las respuestas usan códigos: 200 bien, 201 creado, 404 no existe, 400 datos inválidos.",
  k=["En REST, POST se usa para crear recursos.", "El código 404 significa que el recurso no existe.", "El código 201 indica que se creó un recurso."],
  sit="Tu frontend necesita crear una tarea nueva en el servidor enviando sus datos. ¿Qué método HTTP usa?",
  cod="""app.post("/tareas", (req, res) => {
  const tarea = { id: Date.now(), ...req.body };
  res.status(201).json(tarea);
});""", h="crea una tarea y responde con el código 201",
  pr=("El método HTTP para crear recursos es ___. (4 letras)", "post"),
  pr2=("El código HTTP de «no encontrado» es ___. (3 dígitos)", "404"),
  ec="usar GET para borrar o modificar datos", out='{"id":1732012345678,"titulo":"Estudiar"}'),
K("Node con bases de datos", d="conectar tu servidor a MySQL, PostgreSQL o MongoDB", u="guardar los datos de tu app de forma permanente",
  mas="Cada base tiene su librería: mysql2 para MySQL (también el de XAMPP), pg para PostgreSQL y mongodb o mongoose para MongoDB. Se usan consultas con parámetros (?) para evitar inyección SQL y la conexión se guarda en variables de entorno.",
  k=["mysql2 conecta Node con MySQL.", "Las consultas con parámetros evitan la inyección SQL.", "Los datos de conexión se guardan en variables de entorno."],
  sit="Tu API de Node debe guardar usuarios en el MySQL de XAMPP. ¿Qué librería instalas?",
  cod="""import mysql from "mysql2/promise";
const db = await mysql.createConnection({ host: "localhost", user: "root", database: "finanbot_db" });
const [filas] = await db.query("SELECT * FROM usuarios WHERE id = ?", [1]);
console.log(filas);""", h="consulta un usuario en MySQL con un parámetro seguro",
  pr=("La librería más usada para conectar Node con MySQL es ___. (6 caracteres)", "mysql2"),
  pr2=("Para PostgreSQL se usa la librería ___. (2 letras)", "pg"),
  ec="armar consultas SQL concatenando texto del usuario", out="[ { id: 1, nombre: 'Ana' } ]"),
K("Middleware", d="funciones que se ejecutan antes de llegar a la ruta", u="registrar peticiones, validar sesiones o manejar errores en un solo lugar",
  mas="En Express, app.use(fn) agrega un middleware con (req, res, next). Llama a next() para seguir o responde para cortar. Así se hacen logs, autenticación, CORS y manejo de errores sin repetir código en cada ruta.",
  k=["Un middleware se ejecuta antes de la ruta.", "next() pasa al siguiente middleware.", "app.use agrega un middleware en Express."],
  sit="Quieres registrar en consola cada petición que llega a tu API sin escribirlo en cada ruta. ¿Qué usas?",
  cod="""app.use((req, res, next) => {
  console.log(req.method, req.url);
  next();
});""", h="muestra el método y la URL de cada petición",
  pr=("La función que pasa al siguiente middleware se llama ___. (4 letras)", "next"),
  pr2=("Para agregar un middleware en Express se usa app.___. (3 letras)", "use"),
  ec="olvidar llamar a next y dejar la petición colgada", out="GET /productos"),
]

E3 = [
K("Variables de entorno en Node", d="configuración secreta fuera del código", u="cambiar claves y puertos sin tocar el código",
  mas="Node 20+ carga un archivo con node --env-file=.env server.js; antes se usaba el paquete dotenv. Se leen con process.env.NOMBRE. El .env va en .gitignore y se comparte un .env.example sin valores reales.",
  k=["process.env lee las variables de entorno.", "node --env-file carga un archivo .env.", "El archivo .env no se sube a Git."],
  sit="Tu API necesita la contraseña de la base de datos y no quieres escribirla en el código. ¿Dónde la pones?",
  cod="""// .env:  PUERTO=3000
// node --env-file=.env server.js
console.log(`Puerto: ${process.env.PUERTO}`);""", h="lee el puerto desde el archivo .env",
  pr=("El archivo donde se guardan las variables secretas es .___. (3 letras)", "env"),
  pr2=("El paquete clásico para cargar .env se llama ___. (6 letras)", "dotenv"),
  ec="subir el archivo .env con claves a GitHub", out="Puerto: 3000"),
K("nodemon y --watch", d="herramientas que reinician el servidor al guardar cambios", u="ver tus cambios sin reiniciar a mano",
  mas="node --watch server.js (Node 18+) reinicia solo cuando cambias un archivo. El paquete nodemon hace lo mismo con más opciones. Se suele poner en el script \"dev\" de package.json.",
  k=["node --watch reinicia el servidor al guardar.", "nodemon reinicia el servidor automáticamente.", "El reinicio automático se pone en el script dev."],
  sit="Cada vez que cambias el código debes detener y volver a iniciar el servidor a mano. ¿Qué opción de Node lo evita?",
  cod="""node --watch server.js""", h="inicia el servidor y lo reinicia al guardar cambios",
  pr=("La opción de Node que reinicia al guardar es --___. (5 letras)", "watch"),
  pr2=("El paquete clásico que reinicia el servidor solo es ___. (7 letras)", "nodemon"),
  ec="usar --watch en producción en lugar de un gestor de procesos", out="Restarting 'server.js'"),
K("Manejo de errores", d="capturar fallos para que el servidor no se caiga", u="responder con mensajes claros y registrar el problema",
  mas="Con try/catch capturas errores de await. En Express, un middleware de error tiene cuatro parámetros (err, req, res, next) y responde 500. Nunca muestres al usuario detalles internos como la consulta SQL o la clave.",
  k=["try/catch captura errores de código con await.", "Un middleware de error en Express tiene cuatro parámetros.", "El código 500 indica un error del servidor."],
  sit="Una consulta a la base de datos falla y tu servidor se cae para todos los usuarios. ¿Qué estructura lo evita?",
  cod="""app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "Algo salió mal" });
});""", h="captura los errores de la API y responde 500",
  pr=("La estructura que captura errores es try/___. (5 letras)", "catch"),
  pr2=("El código HTTP de error del servidor es ___. (3 dígitos)", "500"),
  ec="enviar al usuario el detalle interno del error", out='{"error":"Algo salió mal"}'),
K("Pruebas con node:test", d="ejecutor de pruebas integrado en Node", u="comprobar que tu código funciona después de cada cambio",
  mas="node:test trae test y node:assert trae comparaciones como assert.equal. Se ejecutan con node --test. Las pruebas automáticas evitan que un arreglo rompa otra cosa y se pueden correr en GitHub Actions.",
  k=["node --test ejecuta las pruebas del proyecto.", "assert.equal compara el valor obtenido con el esperado.", "Las pruebas se pueden ejecutar en GitHub Actions."],
  sit="Quieres comprobar automáticamente que tu función sumar sigue funcionando después de cada cambio. ¿Qué usas?",
  cod="""import { test } from "node:test";
import assert from "node:assert";
test("suma", () => assert.equal(2 + 3, 5));""", h="prueba que 2 + 3 dé 5",
  pr=("La opción de Node que ejecuta las pruebas es --___. (4 letras)", "test"),
  pr2=("El módulo de comparaciones de Node es node:___. (6 letras)", "assert"),
  ec="probar todo a mano y romper algo sin darte cuenta", out="✔ suma (0.6ms)\nℹ tests 1\nℹ pass 1"),
K("Despliegue de Node", d="poner tu servidor de Node en internet", u="que otras personas usen tu API o tu app",
  mas="Plataformas como Render, Railway o un VPS ejecutan npm start. El puerto se lee de process.env.PORT y se usa un gestor de procesos (pm2) o Docker para mantenerlo vivo. El frontend estático puede ir aparte en GitHub Pages o Netlify.",
  k=["En producción el puerto se lee de process.env.PORT.", "pm2 mantiene vivo un servidor de Node.", "Docker también sirve para desplegar apps de Node."],
  sit="Subiste tu API a un servicio en la nube y te asigna el puerto en una variable. ¿Qué debes leer en el código?",
  cod="""const puerto = process.env.PORT ?? 3000;
app.listen(puerto, () => console.log(`Listo en ${puerto}`));""", h="usa el puerto que asigna el servidor o el 3000",
  pr=("El gestor de procesos más usado para Node es ___. (3 caracteres)", "pm2"),
  pr2=("En la nube, el puerto suele venir en process.env.___. (4 letras)", "port"),
  ec="dejar el puerto fijo en el código y que el servidor no arranque", out="Listo en 3000"),
K("Frameworks sobre Node", d="herramientas construidas con Node para apps completas", u="elegir la herramienta adecuada para cada tipo de proyecto",
  mas="Vite sirve y compila el frontend (React, Vue, Svelte). Next.js y Nuxt hacen apps con servidor. NestJS organiza APIs grandes con módulos. Electron crea apps de escritorio, como VS Code, con tecnologías web.",
  k=["Vite es una herramienta de desarrollo para el frontend.", "Next.js crea apps de React con servidor.", "Electron crea apps de escritorio con tecnologías web."],
  sit="Quieres crear una aplicación de escritorio con HTML, CSS y JavaScript, como lo es VS Code. ¿Qué framework usas?",
  cod="""npm create vite@latest mi-app -- --template react
cd mi-app && npm install && npm run dev""", h="crea y arranca un proyecto de React con Vite",
  pr=("El framework para apps de escritorio con tecnología web es ___. (8 letras)", "electron"),
  pr2=("La herramienta que crea proyectos de React rápidos es ___. (4 letras)", "vite"),
  ec="elegir un framework enorme para un proyecto pequeño", out="VITE ready in 280 ms"),
]

ETAPAS_CONCEPTOS = [
    ("Node.js desde cero", "Ejecuta JavaScript en tu computador con npm y módulos", E1),
    ("Servidores y APIs", "HTTP, Express, REST, bases de datos y middleware", E2),
    ("Node profesional", "Configuración, errores, pruebas, despliegue y frameworks", E3),
    ("Node a fondo", "Eventos, streams, buffers, procesos, crypto, hilos y fetch", E4),
    ("Ecosistema profesional", "TypeScript, JWT, bcrypt, WebSockets, Prisma, zod, logs y npm", E5),
    ("Express a fondo", "Routers, parámetros, archivos, cookies, sesiones, seguridad y documentación", E6),
    ("Datos y seguridad", "MySQL, ORMs, Redis, tokens, OAuth, roles, XSS, CSRF y tiempo real", E7),
    ("Calidad y producción", "Pruebas, depuración, rendimiento, colas, GraphQL, Docker y CI", E8),
]
