"""Node.js, etapas 4 y 5: Node a fondo y ecosistema profesional."""
from ..generador import K

E4 = [
K("EventEmitter", d="clase de Node para emitir y escuchar eventos con nombre", u="avisar a otras partes del programa cuando algo pasa",
  mas="on(nombre, fn) registra un oyente y emit(nombre, datos) lo dispara; once escucha una sola vez. Muchos módulos de Node (servidores, streams) son EventEmitter por dentro.",
  k=["emit dispara un evento con nombre.", "on registra una función que escucha un evento.", "once escucha un evento una sola vez."],
  sit="Quieres que, cada vez que se registre un usuario, se envíe un correo y se guarde un log sin mezclar ese código. ¿Qué clase de Node usas?",
  cod="""import { EventEmitter } from "node:events";
const bus = new EventEmitter();
bus.on("registro", (n) => console.log(`Bienvenido, ${n}`));
bus.emit("registro", "Ana");""", h="emite un evento y lo escucha",
  pr=("El método que dispara un evento es ___. (4 letras)", "emit"),
  pr2=("El método que escucha un evento una sola vez es ___. (4 letras)", "once"),
  ec="olvidar quitar oyentes y acumular memoria", out="Bienvenido, Ana"),
K("Streams", d="flujos de datos que se procesan por partes", u="leer o enviar archivos grandes sin cargarlos enteros en memoria",
  mas="fs.createReadStream lee un archivo por trozos y pipeline une streams: leer → comprimir → escribir. Así se procesan archivos de varios GB con poca memoria. Las respuestas HTTP también son streams.",
  k=["Un stream procesa los datos por partes.", "createReadStream lee un archivo por trozos.", "pipeline une varios streams de forma segura."],
  sit="Debes comprimir un archivo de 4 GB y tu programa se queda sin memoria al leerlo entero. ¿Qué mecanismo de Node usas?",
  cod="""import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";
import { pipeline } from "node:stream/promises";
await pipeline(createReadStream("datos.csv"), createGzip(), createWriteStream("datos.csv.gz"));
console.log("Comprimido");""", h="comprime un archivo grande por partes",
  pr=("La función que une streams de forma segura es ___. (8 letras)", "pipeline"),
  pr2=("Para leer un archivo por trozos se usa createRead___. (6 letras)", "stream"),
  ec="usar readFile con archivos enormes", out="Comprimido"),
K("Buffer", d="bloque de bytes en memoria", u="trabajar con datos binarios: imágenes, archivos o texto en otras codificaciones",
  mas="Buffer.from(\"hola\") guarda el texto como bytes; toString(\"base64\") lo convierte a Base64 y Buffer.from(b64, \"base64\") lo devuelve. Los archivos leídos sin codificación llegan como Buffer.",
  k=["Un Buffer guarda bytes en memoria.", "toString(\"base64\") convierte un Buffer a Base64.", "readFile sin codificación devuelve un Buffer."],
  sit="Debes convertir una imagen a Base64 para enviarla dentro de un JSON. ¿Qué tipo de Node usas para manejar sus bytes?",
  cod="""const b = Buffer.from("hola");
console.log(b.length, b.toString("base64"));""", h="convierte un texto a bytes y a Base64",
  pr=("El tipo de Node que guarda bytes en memoria es ___. (6 letras)", "buffer"),
  pr2=("La codificación de texto para datos binarios más usada es ___. (6 caracteres)", "base64"),
  ec="convertir binarios a texto UTF-8 y dañarlos", out="4 aG9sYQ=="),
K("path y os", d="módulos para manejar rutas y datos del sistema operativo", u="que tu programa funcione igual en Windows, macOS y Linux",
  mas="path.join y path.resolve arman rutas con la barra correcta, path.extname da la extensión y path.basename el nombre. os.platform(), os.homedir() y os.cpus() describen el equipo. import.meta.dirname es la carpeta del archivo actual (Node 20.11+).",
  k=["path.extname devuelve la extensión de un archivo.", "os.platform dice el sistema operativo.", "import.meta.dirname es la carpeta del módulo actual."],
  sit="Tu programa arma rutas con \"carpeta/\" + archivo y en Windows falla. ¿Qué módulo usas para armarlas bien?",
  cod="""import path from "node:path";
console.log(path.extname("foto.final.png"), path.basename("/fotos/gato.jpg"));""", h="muestra la extensión y el nombre de un archivo",
  pr=("La función de path que da la extensión es ___. (7 letras)", "extname"),
  pr2=("El módulo de Node con datos del sistema operativo es ___. (2 letras)", "os"),
  ec="escribir rutas con \\\\ y que el programa falle en Linux", out=".png gato.jpg"),
K("child_process", d="módulo que ejecuta otros programas desde Node", u="correr comandos del sistema, como git o python, desde tu script",
  mas="execFile(\"git\", [\"status\"]) ejecuta un programa con argumentos seguros; spawn transmite la salida mientras corre. exec usa la shell: nunca le pases texto del usuario sin validar, porque permite inyección de comandos.",
  k=["child_process ejecuta otros programas.", "spawn transmite la salida mientras el programa corre.", "exec con datos del usuario permite inyección de comandos."],
  sit="Tu herramienta de Node debe ejecutar git log y mostrar su salida. ¿Qué módulo usas?",
  cod="""import { execFileSync } from "node:child_process";
console.log(execFileSync("node", ["--version"]).toString().trim());""", h="ejecuta node --version desde Node",
  pr=("El módulo de Node que ejecuta otros programas es child___. (8 caracteres)", "_process"),
  pr2=("La función que transmite la salida mientras corre es ___. (5 letras)", "spawn"),
  ec="pasar texto del usuario a exec sin validar", out="v20.18.0"),
K("crypto", d="módulo de criptografía de Node", u="crear hashes, identificadores aleatorios y cifrar datos",
  mas="crypto.createHash(\"sha256\").update(texto).digest(\"hex\") da la huella de un texto. crypto.randomUUID() crea identificadores únicos y randomBytes genera tokens seguros. Para contraseñas se usan funciones lentas como scrypt o bcrypt.",
  k=["createHash calcula la huella de un texto.", "randomUUID crea un identificador único.", "Las contraseñas se guardan con funciones lentas como scrypt."],
  sit="Necesitas generar un token aleatorio y seguro para el enlace de «recuperar contraseña». ¿Qué módulo de Node usas?",
  cod="""import { createHash } from "node:crypto";
console.log(createHash("sha256").update("hola").digest("hex").slice(0, 16));""", h="calcula el SHA-256 de un texto",
  pr=("El módulo de criptografía de Node es ___. (6 letras)", "crypto"),
  pr2=("La función que crea identificadores únicos es random___. (4 letras)", "uuid"),
  ec="usar Math.random para tokens de seguridad", out="b221d9dbb083a7f3"),
K("Worker threads", d="hilos que ejecutan JavaScript en paralelo dentro de Node", u="hacer cálculos pesados sin bloquear el servidor",
  mas="El bucle de eventos se congela con cálculos largos (comprimir imágenes, cifrar mucho). new Worker(\"tarea.js\") corre ese código en otro hilo y devuelve el resultado con mensajes (postMessage).",
  k=["Los worker threads ejecutan JavaScript en paralelo.", "Los workers se comunican con postMessage.", "Los cálculos largos bloquean el bucle de eventos."],
  sit="Tu API calcula un informe que tarda 10 segundos de CPU y mientras tanto ningún otro usuario puede entrar. ¿Qué usas?",
  cod="""import { Worker } from "node:worker_threads";
const w = new Worker("./calculo.js");
w.on("message", (r) => console.log("Resultado:", r));""", h="ejecuta un cálculo en otro hilo",
  pr=("Los workers se comunican con post___. (7 letras)", "message"),
  pr2=("El módulo de hilos de Node es node:worker___. (8 caracteres)", "_threads"),
  ec="usar workers para tareas de red que ya son asíncronas", out="Resultado: 832040"),
K("fetch en Node", d="función integrada para hacer peticiones HTTP (Node 18+)", u="consumir APIs externas desde tu servidor sin instalar nada",
  mas="Node trae fetch igual que el navegador: await fetch(url) y luego await r.json(). Revisa r.ok y usa AbortSignal.timeout(5000) para no esperar para siempre. Antes se usaban axios o node-fetch.",
  k=["Node 18 trae fetch integrado.", "r.ok indica si la respuesta fue exitosa.", "AbortSignal.timeout limita la espera de fetch."],
  sit="Tu servidor debe pedir el clima a una API externa y no quieres instalar ninguna librería. ¿Qué función usas?",
  cod="""const r = await fetch("https://api.github.com/users/octocat", { signal: AbortSignal.timeout(5000) });
const u = await r.json();
console.log(r.ok, u.login);""", h="consulta una API externa con límite de tiempo",
  pr=("La propiedad que indica si la respuesta fue exitosa es r.___. (2 letras)", "ok"),
  pr2=("Para limitar la espera se usa AbortSignal.___(ms). (7 letras)", "timeout"),
  ec="no revisar r.ok y procesar una página de error como datos", out="true octocat"),
]

E5 = [
K("TypeScript con Node", d="usar tipos de TypeScript en el código del servidor", u="detectar errores antes de ejecutar y tener mejor autocompletado",
  mas="Se instala typescript y @types/node, se crea tsconfig.json con npx tsc --init y se compila con tsc. En desarrollo, tsx (npx tsx server.ts) ejecuta TypeScript directamente; Node 22.6+ también puede con --experimental-strip-types.",
  k=["@types/node trae los tipos de Node.", "tsx ejecuta TypeScript directamente.", "tsc compila TypeScript a JavaScript."],
  sit="Tu API crece y quieres que el editor avise si pasas un número donde va un texto. ¿Qué agregas al proyecto de Node?",
  cod="""// server.ts  →  npx tsx server.ts
const puerto: number = Number(process.env.PORT ?? 3000);
console.log(`Puerto ${puerto}`);""", h="código de servidor con tipos",
  pr=("El paquete con los tipos de Node es @types/___. (4 letras)", "node"),
  pr2=("La herramienta que ejecuta TypeScript sin compilar antes es ___. (3 letras)", "tsx"),
  ec="usar any en todas partes y perder la ventaja de los tipos", out="Puerto 3000"),
K("JWT", d="token firmado que identifica al usuario en cada petición", u="autenticar APIs sin guardar sesiones en el servidor",
  mas="Al iniciar sesión, el servidor firma un JWT con jsonwebtoken (jwt.sign) y el cliente lo envía en la cabecera Authorization: Bearer. En cada petición se verifica con jwt.verify. El JWT no está cifrado: no pongas contraseñas dentro.",
  k=["Un JWT se envía en la cabecera Authorization.", "jwt.verify comprueba la firma del token.", "El contenido de un JWT no está cifrado."],
  sit="Tu app móvil debe llamar a tu API y la API debe saber qué usuario es en cada petición. ¿Qué tipo de token usas?",
  cod="""import jwt from "jsonwebtoken";
const token = jwt.sign({ id: 7 }, process.env.SECRETO, { expiresIn: "1h" });
console.log(jwt.verify(token, process.env.SECRETO).id);""", h="firma un token y lo verifica",
  pr=("Las siglas del token firmado para APIs son ___. (3 letras)", "jwt"),
  pr2=("La palabra que va antes del token en Authorization es ___. (6 letras)", "bearer"),
  ec="guardar datos secretos dentro del JWT", out="7"),
K("bcrypt", d="función lenta para guardar contraseñas como hash", u="que nadie pueda leer las contraseñas aunque roben la base de datos",
  mas="bcrypt.hash(clave, 12) genera un hash distinto cada vez (lleva sal) y bcrypt.compare(clave, hash) dice si coincide. El 12 es el costo: más alto, más lento y seguro. Nunca guardes contraseñas en texto plano.",
  k=["bcrypt guarda contraseñas como hash con sal.", "bcrypt.compare comprueba una contraseña.", "El costo de bcrypt controla qué tan lento es."],
  sit="Vas a guardar las contraseñas de los usuarios en tu base de datos MySQL. ¿Qué librería usas para no guardarlas en texto plano?",
  cod="""import bcrypt from "bcrypt";
const hash = await bcrypt.hash("Clave123", 12);
console.log(await bcrypt.compare("Clave123", hash));""", h="crea el hash de una contraseña y la comprueba",
  pr=("La función de bcrypt que comprueba una contraseña es ___. (7 letras)", "compare"),
  pr2=("El valor aleatorio que hace distinto cada hash se llama ___. (3 letras)", "sal"),
  ec="usar sha256 rápido para contraseñas", out="true"),
K("WebSockets", d="conexión que queda abierta para enviar datos en los dos sentidos", u="chats, notificaciones y juegos en tiempo real",
  mas="A diferencia de HTTP, el servidor puede enviar datos sin que el cliente pregunte. En Node se usa ws o Socket.IO: io.on(\"connection\"), socket.emit y socket.on. Es la base de los chats en vivo.",
  k=["Un WebSocket mantiene la conexión abierta.", "Con WebSockets el servidor envía datos sin pregunta del cliente.", "Socket.IO facilita los WebSockets en Node."],
  sit="Quieres que los mensajes de tu chat aparezcan al instante en la pantalla de los demás sin recargar. ¿Qué tecnología usas?",
  cod="""import { Server } from "socket.io";
const io = new Server(3000);
io.on("connection", (s) => s.on("mensaje", (m) => io.emit("mensaje", m)));""", h="un chat que reenvía cada mensaje a todos",
  pr=("La librería más usada para WebSockets en Node es socket.___. (2 letras)", "io"),
  pr2=("El evento de una conexión nueva en Socket.IO es ___. (10 letras)", "connection"),
  ec="preguntar al servidor cada segundo con fetch en lugar de usar WebSockets", out=""),
K("Prisma", d="ORM de Node que trabaja con la base de datos usando objetos y tipos", u="consultar MySQL o PostgreSQL sin escribir SQL a mano",
  mas="En schema.prisma defines los modelos; npx prisma migrate dev crea las tablas y prisma.usuario.findMany() consulta. Con TypeScript, el editor autocompleta los campos. Alternativas: Sequelize, TypeORM, Drizzle.",
  k=["Prisma define los modelos en schema.prisma.", "prisma migrate crea las tablas de la base.", "findMany consulta varios registros."],
  sit="Quieres consultar tu base MySQL desde Node con autocompletado y sin escribir SQL a mano. ¿Qué ORM usas?",
  cod="""import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();
console.log(await prisma.usuario.findMany({ take: 2 }));""", h="lista dos usuarios con Prisma",
  pr=("El archivo donde Prisma define los modelos es schema.___. (6 letras)", "prisma"),
  pr2=("El método de Prisma que trae varios registros es find___. (4 letras)", "many"),
  ec="cambiar las tablas a mano y desincronizar el esquema", out="[ { id: 1, nombre: 'Ana' }, { id: 2, nombre: 'Luis' } ]"),
K("Validación con zod", d="librería que valida datos con esquemas", u="rechazar datos mal formados antes de guardarlos",
  mas="z.object({ email: z.string().email() }) describe lo esperado; safeParse devuelve success y los errores sin lanzar excepciones. En una API se valida req.body antes de usarlo. Con TypeScript, z.infer saca el tipo del esquema.",
  k=["zod valida datos con esquemas.", "safeParse valida sin lanzar excepciones.", "z.infer saca el tipo de TypeScript de un esquema."],
  sit="Tu API recibe registros con correos mal escritos y edades negativas. ¿Qué librería usas para validar req.body?",
  cod="""import { z } from "zod";
const Usuario = z.object({ email: z.string().email(), edad: z.number().min(0) });
console.log(Usuario.safeParse({ email: "x", edad: -1 }).success);""", h="valida un objeto y muestra si es válido",
  pr=("El método de zod que valida sin lanzar errores es safe___. (5 letras)", "parse"),
  pr2=("Para sacar el tipo de un esquema se usa z.___. (5 letras)", "infer"),
  ec="confiar en lo que llega del cliente sin validar", out="false"),
K("Logs en producción", d="registros de lo que hace el servidor", u="encontrar errores en producción y medir el uso",
  mas="morgan registra cada petición de Express y pino o winston escriben logs con niveles (info, warn, error) en JSON. Nunca registres contraseñas ni tokens. En la nube, los logs se leen desde el panel del servicio.",
  k=["morgan registra cada petición de Express.", "Los logs tienen niveles como info y error.", "No se registran contraseñas ni tokens."],
  sit="Tu API falla a veces en producción y no sabes qué petición la rompe. ¿Qué agregas para registrar cada petición?",
  cod="""import morgan from "morgan";
app.use(morgan("dev"));""", h="registra cada petición en la consola",
  pr=("El middleware que registra cada petición de Express es ___. (6 letras)", "morgan"),
  pr2=("Una librería rápida de logs en JSON es ___. (4 letras)", "pino"),
  ec="registrar el cuerpo completo con contraseñas", out="GET /productos 200 4.512 ms - 87"),
K("Crear y publicar un paquete npm", d="convertir tu código en una librería o un comando que otros instalan", u="compartir herramientas propias con npm install o npx",
  mas="En package.json, \"bin\" convierte un archivo en comando (con #!/usr/bin/env node arriba) y \"exports\" define qué se importa. npm login y npm publish lo suben; npm version patch sube la versión antes de publicar.",
  k=["El campo bin crea un comando de terminal.", "npm publish sube el paquete al registro.", "npm version patch sube la versión del paquete."],
  sit="Hiciste una herramienta de terminal en Node y quieres que tus compañeros la usen con npx mi-herramienta. ¿Qué haces con el paquete?",
  cod="""{
  "name": "saludo-cli",
  "version": "1.0.0",
  "bin": { "saludo": "./cli.js" }
}""", h="package.json de un comando de terminal",
  pr=("El campo de package.json que crea un comando es ___. (3 letras)", "bin"),
  pr2=("La orden que sube el paquete al registro es npm ___. (7 letras)", "publish"),
  ec="publicar con claves o archivos .env dentro del paquete", out=""),
]
