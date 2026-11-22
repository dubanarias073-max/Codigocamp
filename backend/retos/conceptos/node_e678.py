"""Node.js, etapas 6, 7 y 8: Express a fondo, datos y seguridad, calidad y producción."""
from ..generador import K

E6 = [
K("express.Router", d="mini aplicación de Express para agrupar rutas", u="separar las rutas por tema en archivos distintos",
  mas="Creas const r = express.Router(), le agregas r.get, r.post… y lo montas con app.use(\"/api/usuarios\", r). Así cada recurso vive en su propio archivo y app.js queda corto.",
  k=["express.Router agrupa rutas relacionadas.", "Un router se monta con app.use y un prefijo.", "Cada recurso puede tener su propio archivo de rutas."],
  sit="Tu app.js tiene 40 rutas de usuarios, productos y pedidos mezcladas. ¿Qué usas para separarlas por archivo?",
  cod="""import express from "express";
const usuarios = express.Router();
usuarios.get("/", (req, res) => res.json(["Ana", "Luis"]));
const app = express();
app.use("/api/usuarios", usuarios);
console.log("Rutas montadas en /api/usuarios");""", h="monta un router de usuarios con prefijo",
  pr=("Para agrupar rutas en Express se usa express.___ (6 letras)", "router"),
  pr2=("Un router se conecta a la app con app.___ (3 letras)", "use"),
  ec="repetir el prefijo /api/usuarios dentro de cada ruta del router", out="Rutas montadas en /api/usuarios"),
K("Parámetros de ruta", d="partes variables de la URL, como /productos/:id", u="leer qué recurso pide el cliente",
  mas="Con app.get(\"/productos/:id\") Express guarda el valor en req.params.id. Siempre llega como texto: conviértelo con Number() antes de buscar en la base de datos.",
  k=["req.params guarda las partes variables de la ruta.", "En la ruta, la parte variable empieza con dos puntos.", "Los parámetros de ruta llegan como texto."],
  sit="Quieres que /productos/15 devuelva el producto con id 15. ¿Dónde lees el 15 en Express?",
  cod="""app.get("/productos/:id", (req, res) => {
  const id = Number(req.params.id);
  res.json({ id, nombre: "Teclado" });
});
console.log({ id: Number("15") });""", h="lee el id de la ruta como número",
  pr=("En Express, el id de /productos/:id se lee en req.___.id (6 letras)", "params"),
  pr2=("Los parámetros de ruta siempre llegan como ___ (5 letras)", "texto"),
  ec="comparar req.params.id con un número sin convertirlo", out="{ id: 15 }"),
K("Query string", d="datos opcionales después del ? en la URL", u="filtrar, ordenar o paginar resultados",
  mas="En /productos?orden=precio&pagina=2, Express entrega req.query.orden y req.query.pagina. Son opcionales: da valores por defecto con ?? y valida que sean correctos.",
  k=["req.query contiene los datos después del ? de la URL.", "Los datos del query string son opcionales.", "El query string sirve para filtrar y paginar."],
  sit="Tu lista de productos debe permitir ?categoria=ropa para filtrar. ¿De qué objeto lees la categoría?",
  cod="""app.get("/productos", (req, res) => {
  const pagina = Number(req.query.pagina ?? 1);
  res.json({ pagina, categoria: req.query.categoria ?? "todas" });
});
console.log({ pagina: 1, categoria: "todas" });""", h="lee la página y la categoría con valores por defecto",
  pr=("Los datos después del ? se leen en req.___ (5 letras)", "query"),
  pr2=("Los pares del query string se separan con el símbolo ___ (1 carácter)", "&"),
  ec="suponer que el parámetro siempre viene y que es un número", out="{ pagina: 1, categoria: 'todas' }"),
K("express.json y req.body", d="middleware que convierte el cuerpo JSON de la petición en un objeto", u="recibir datos de formularios y apps en un POST",
  mas="Sin app.use(express.json()), req.body es undefined. Con él, el JSON enviado llega como objeto. Para formularios HTML clásicos se usa express.urlencoded({ extended: true }).",
  k=["express.json convierte el cuerpo JSON en req.body.", "Sin express.json, req.body queda undefined.", "express.urlencoded lee formularios HTML clásicos."],
  sit="Tu POST /usuarios siempre recibe req.body como undefined aunque el cliente envía JSON. ¿Qué middleware falta?",
  cod="""app.use(express.json());
app.post("/usuarios", (req, res) => {
  res.status(201).json({ creado: req.body.nombre });
});
console.log({ creado: "Ana" });""", h="recibe un JSON y responde con el nombre",
  pr=("El cuerpo de la petición se lee en req.___ (4 letras)", "body"),
  pr2=("Para formularios HTML clásicos se usa express.___ (10 letras)", "urlencoded"),
  ec="olvidar app.use(express.json()) y que req.body sea undefined", out="{ creado: 'Ana' }"),
K("Códigos de estado HTTP", d="números que indican el resultado de una petición", u="que el cliente sepa si todo salió bien o qué falló",
  mas="2xx éxito (200 OK, 201 creado, 204 sin contenido), 4xx error del cliente (400 datos malos, 401 sin sesión, 403 sin permiso, 404 no existe) y 5xx error del servidor (500). En Express: res.status(404).json(...).",
  k=["201 significa que se creó un recurso.", "404 significa que el recurso no existe.", "Los códigos 5xx son errores del servidor."],
  sit="Un cliente pide /usuarios/999 y ese usuario no existe. ¿Qué código de estado debe responder tu API?",
  cod="""const codigos = { creado: 201, noExiste: 404, sinPermiso: 403 };
console.log(codigos.noExiste);""", h="muestra el código de un recurso que no existe",
  pr=("Cuando se crea un recurso se responde con el código ___ (3 dígitos)", "201"),
  pr2=("Si el usuario no tiene permiso se responde ___ (3 dígitos)", "403"),
  ec="responder 200 con un mensaje de error dentro", out="404"),
K("CORS", d="reglas del navegador que controlan qué sitios pueden llamar a tu API", u="permitir que tu frontend en otro dominio use tu backend",
  mas="El navegador bloquea peticiones de http://localhost:5173 a http://localhost:3000 si el servidor no lo autoriza. El paquete cors agrega las cabeceras: app.use(cors({ origin: \"http://localhost:5173\" })). No uses origin: \"*\" con cookies.",
  k=["CORS lo aplica el navegador, no el servidor.", "El paquete cors autoriza otros orígenes.", "Con cookies no se debe usar el origen *."],
  sit="Tu React en el puerto 5173 llama a tu API en el 3000 y la consola dice «blocked by CORS policy». ¿Qué configuras en el backend?",
  cod="""import cors from "cors";
app.use(cors({ origin: "http://localhost:5173", credentials: true }));
console.log("CORS activo para 5173");""", h="autoriza al frontend de Vite",
  pr=("El paquete de Express para autorizar otros orígenes se llama ___ (4 letras)", "cors"),
  pr2=("Quien bloquea la petición por CORS es el ___ (9 letras)", "navegador"),
  ec="poner origin \"*\" junto con credenciales", out="CORS activo para 5173"),
K("Archivos estáticos", d="servir HTML, CSS, imágenes y JS tal cual desde una carpeta", u="publicar el frontend o las imágenes desde el mismo servidor",
  mas="app.use(express.static(\"public\")) hace que public/logo.png se vea en /logo.png. Puedes ponerle prefijo: app.use(\"/img\", express.static(\"fotos\")).",
  k=["express.static sirve archivos de una carpeta.", "Los archivos estáticos se envían sin procesarlos.", "Se puede servir una carpeta con un prefijo de ruta."],
  sit="Quieres que el index.html y el CSS de la carpeta public se vean desde tu servidor Express. ¿Qué middleware usas?",
  cod="""app.use(express.static("public"));
console.log("public/logo.png -> /logo.png");""", h="sirve la carpeta public",
  pr=("Para servir una carpeta en Express se usa express.___ (6 letras)", "static"),
  pr2=("La carpeta más común para archivos estáticos se llama ___ (6 letras)", "public"),
  ec="servir la carpeta del proyecto entera y exponer el .env", out="public/logo.png -> /logo.png"),
K("Subir archivos con multer", d="middleware para recibir archivos de formularios multipart", u="subir fotos de perfil o documentos",
  mas="multer({ dest: \"subidas/\", limits: { fileSize: 5e6 } }).single(\"foto\") guarda el archivo y lo deja en req.file. Valida el tipo (mimetype) y el tamaño, y nunca confíes en el nombre original.",
  k=["multer recibe archivos de formularios multipart.", "El archivo subido queda en req.file.", "Hay que limitar el tamaño y validar el tipo de archivo."],
  sit="Tu formulario envía una foto de perfil y en Express no la encuentras en req.body. ¿Qué middleware usas para recibirla?",
  cod="""import multer from "multer";
const subir = multer({ dest: "subidas/", limits: { fileSize: 5_000_000 } });
app.post("/foto", subir.single("foto"), (req, res) => res.json({ guardado: req.file.filename }));
console.log("Límite: 5 MB");""", h="recibe una foto de máximo 5 MB",
  pr=("El middleware de Express para subir archivos es ___ (6 letras)", "multer"),
  pr2=("Con .single, el archivo queda en req.___ (4 letras)", "file"),
  ec="aceptar archivos de cualquier tamaño y tipo", out="Límite: 5 MB"),
K("Cookies en Express", d="pequeños datos que el servidor guarda en el navegador", u="recordar la sesión o preferencias del usuario",
  mas="res.cookie(\"tema\", \"oscuro\", { httpOnly: true, secure: true, sameSite: \"lax\", maxAge: 86400000 }) la crea y cookie-parser la lee en req.cookies. httpOnly impide que JavaScript la lea.",
  k=["res.cookie crea una cookie en el navegador.", "httpOnly impide que JavaScript lea la cookie.", "cookie-parser deja las cookies en req.cookies."],
  sit="Quieres guardar el id de sesión en el navegador de forma que un script malicioso no pueda leerlo. ¿Qué opción de cookie activas?",
  cod="""res.cookie("sesion", "abc123", { httpOnly: true, sameSite: "lax", maxAge: 86_400_000 });
console.log("Cookie httpOnly por 1 día");""", h="crea una cookie segura por un día",
  pr=("La opción que impide que JavaScript lea una cookie es http___ (4 letras)", "only"),
  pr2=("Las cookies leídas quedan en req.___ (7 letras)", "cookies"),
  ec="guardar datos sensibles en cookies sin httpOnly", out="Cookie httpOnly por 1 día"),
K("Sesiones con express-session", d="datos del usuario guardados en el servidor y unidos a una cookie", u="mantener la sesión iniciada entre peticiones",
  mas="express-session crea una cookie con un id y guarda los datos en el servidor (req.session.usuarioId). En producción usa un almacén como Redis o la base de datos, no la memoria.",
  k=["La sesión guarda los datos en el servidor.", "El navegador solo guarda el id de la sesión.", "En producción las sesiones se guardan en Redis o en la base de datos."],
  sit="Después del login quieres recordar qué usuario es en cada petición sin enviarle sus datos al navegador. ¿Qué usas?",
  cod="""import session from "express-session";
app.use(session({ secret: process.env.SECRETO, resave: false, saveUninitialized: false }));
app.post("/login", (req, res) => { req.session.usuarioId = 7; res.sendStatus(204); });
console.log("Sesión guardada en el servidor");""", h="guarda el usuario en la sesión",
  pr=("Los datos de la sesión se guardan en req.___ (7 letras)", "session"),
  pr2=("La cookie de sesión solo guarda el ___ de la sesión (2 letras)", "id"),
  ec="usar el almacén en memoria en producción y perder sesiones al reiniciar", out="Sesión guardada en el servidor"),
K("Helmet", d="middleware que agrega cabeceras de seguridad HTTP", u="proteger tu app de ataques comunes con una sola línea",
  mas="app.use(helmet()) activa cabeceras como Content-Security-Policy, X-Content-Type-Options y Strict-Transport-Security. Es una de las primeras cosas a poner en una API de producción.",
  k=["Helmet agrega cabeceras de seguridad.", "Helmet se activa con app.use(helmet()).", "Content-Security-Policy limita qué scripts puede cargar la página."],
  sit="Una auditoría dice que tu servidor no envía cabeceras de seguridad. ¿Qué middleware de Express las agrega de una vez?",
  cod="""import helmet from "helmet";
app.use(helmet());
console.log("Cabeceras de seguridad activas");""", h="activa las cabeceras de seguridad",
  pr=("El middleware que agrega cabeceras de seguridad es ___ (6 letras)", "helmet"),
  pr2=("La cabecera que limita los scripts permitidos es Content-Security-___ (6 letras)", "policy"),
  ec="publicar una API sin cabeceras de seguridad", out="Cabeceras de seguridad activas"),
K("Límite de peticiones", d="limitar cuántas peticiones puede hacer un cliente en un tiempo", u="frenar ataques de fuerza bruta y abusos",
  mas="express-rate-limit permite, por ejemplo, 5 intentos de login cada 15 minutos por IP. Al pasarse, responde 429 Too Many Requests.",
  k=["Limitar peticiones frena la fuerza bruta.", "Al pasar el límite se responde 429.", "express-rate-limit limita por IP."],
  sit="Alguien intenta miles de contraseñas por segundo en tu /login. ¿Qué agregas a esa ruta?",
  cod="""import rateLimit from "express-rate-limit";
app.use("/login", rateLimit({ windowMs: 15 * 60_000, limit: 5 }));
console.log("Máximo 5 intentos cada 15 minutos");""", h="limita los intentos de login",
  pr=("El código HTTP de «demasiadas peticiones» es ___ (3 dígitos)", "429"),
  pr2=("Al ataque de probar miles de contraseñas se le llama fuerza ___ (5 letras)", "bruta"),
  ec="dejar el login sin límite de intentos", out="Máximo 5 intentos cada 15 minutos"),
K("Plantillas con EJS", d="motor que genera HTML en el servidor mezclando datos", u="crear páginas dinámicas sin un framework de frontend",
  mas="app.set(\"view engine\", \"ejs\") y res.render(\"perfil\", { nombre }) llena views/perfil.ejs. En la plantilla <%= nombre %> escapa el texto y <%- %> no lo escapa (cuidado con XSS).",
  k=["EJS genera HTML en el servidor.", "res.render llena una plantilla con datos.", "<%= %> escapa el texto para evitar XSS."],
  sit="Quieres generar en el servidor una página de perfil con el nombre del usuario, sin React. ¿Qué método de Express usas?",
  cod="""app.set("view engine", "ejs");
app.get("/perfil", (req, res) => res.render("perfil", { nombre: "Ana" }));
// views/perfil.ejs:  <h1>Hola, <%= nombre %></h1>
console.log("<h1>Hola, Ana</h1>");""", h="dibuja el perfil con una plantilla",
  pr=("Para dibujar una plantilla se usa res.___ (6 letras)", "render"),
  pr2=("Las plantillas de Express suelen ir en la carpeta ___ (5 letras)", "views"),
  ec="usar <%- %> con datos del usuario y abrir la puerta a XSS", out="<h1>Hola, Ana</h1>"),
K("Paginación en APIs", d="devolver los resultados por partes con página y límite", u="que listas enormes no saturen el servidor ni el cliente",
  mas="Con ?pagina=2&limite=20 calculas offset = (pagina - 1) * limite. Devuelve también el total y si hay más páginas. Pon un límite máximo para que nadie pida un millón de filas.",
  k=["El offset se calcula con (pagina - 1) * limite.", "La respuesta debe incluir el total de resultados.", "Hay que poner un límite máximo por página."],
  sit="Tu GET /productos devuelve 50 000 filas y tarda mucho. ¿Qué técnica aplicas?",
  cod="""const pagina = 3, limite = 20;
const offset = (pagina - 1) * limite;
console.log(offset);""", h="calcula desde qué fila empieza la página 3",
  pr=("Las filas que se saltan al paginar se llaman ___ (6 letras)", "offset"),
  pr2=("En SQL, la cantidad de filas por página se indica con ___ (5 letras)", "limit"),
  ec="dejar que el cliente pida cualquier límite sin un máximo", out="40"),
K("Errores en Express", d="middleware especial con cuatro parámetros que atrapa los errores", u="responder errores en un solo lugar y con el mismo formato",
  mas="Un middleware (err, req, res, next) va al final y recibe los errores de todas las rutas. Desde Express 5, los errores de funciones async también llegan ahí. No muestres la pila del error en producción.",
  k=["El middleware de errores tiene cuatro parámetros.", "El middleware de errores va al final de la app.", "En producción no se muestra la pila del error al cliente."],
  sit="Cada ruta tiene su propio try/catch con respuestas distintas. ¿Qué agregas para manejar los errores en un solo lugar?",
  cod="""app.use((err, req, res, next) => {
  console.error(err.message);
  res.status(err.status ?? 500).json({ error: "Algo salió mal" });
});
console.log("Manejador de errores listo");""", h="responde todos los errores con el mismo formato",
  pr=("El middleware de errores recibe ___ parámetros (6 letras)", "cuatro"),
  pr2=("El primer parámetro del middleware de errores es ___ (3 letras)", "err"),
  ec="mostrar el stack del error al usuario en producción", out="Manejador de errores listo"),
K("Versionar una API", d="incluir la versión en las rutas, como /api/v1", u="cambiar la API sin romper las apps que ya la usan",
  mas="Montas app.use(\"/api/v1\", rutasV1) y, cuando hay un cambio grande, app.use(\"/api/v2\", rutasV2). Las apps viejas siguen con v1 mientras se actualizan.",
  k=["Versionar evita romper a los clientes existentes.", "La versión suele ir en la ruta, como /api/v1.", "Dos versiones pueden convivir un tiempo."],
  sit="Debes cambiar el formato de respuesta de tu API, pero una app móvil vieja todavía la usa. ¿Qué haces?",
  cod="""app.use("/api/v1", (req, res) => res.json({ nombre: "Ana" }));
app.use("/api/v2", (req, res) => res.json({ usuario: { nombre: "Ana" } }));
console.log("v1 y v2 conviven");""", h="publica dos versiones de la API",
  pr=("La primera versión de una API suele ir en la ruta /api/___ (2 caracteres)", "v1"),
  pr2=("Versionar evita ___ a los clientes que ya usan la API (6 letras)", "romper"),
  ec="cambiar el formato de la API sin avisar ni versionar", out="v1 y v2 conviven"),
K("OpenAPI y Swagger", d="estándar para documentar una API y probarla desde el navegador", u="que otros sepan qué rutas tiene tu API y cómo usarlas",
  mas="Un archivo OpenAPI (YAML o JSON) describe rutas, parámetros y respuestas. swagger-ui-express lo muestra como una página interactiva en /docs para probar cada ruta.",
  k=["OpenAPI describe las rutas de una API.", "Swagger UI muestra la documentación como página interactiva.", "La documentación se puede probar desde el navegador."],
  sit="El equipo del frontend te pregunta a diario qué datos recibe cada ruta. ¿Qué publicas?",
  cod="""import swaggerUi from "swagger-ui-express";
const doc = { openapi: "3.0.0", info: { title: "Tienda", version: "1.0.0" }, paths: {} };
app.use("/docs", swaggerUi.serve, swaggerUi.setup(doc));
console.log("Documentación en /docs");""", h="publica la documentación en /docs",
  pr=("El estándar para describir APIs REST es Open___ (3 letras)", "api"),
  pr2=("La página interactiva de documentación se llama ___ UI (7 letras)", "swagger"),
  ec="dejar la API sin documentar y que nadie sepa usarla", out="Documentación en /docs"),
K("Estructura MVC", d="organizar el código en modelos, vistas y controladores", u="que un proyecto grande siga siendo fácil de entender",
  mas="routes/ define las URL, controllers/ tiene la lógica de cada ruta, models/ habla con la base de datos y services/ reúne la lógica de negocio reutilizable. Cada archivo hace una sola cosa.",
  k=["Los modelos hablan con la base de datos.", "Los controladores reciben la petición y responden.", "Las rutas solo conectan URL con controladores."],
  sit="Tu archivo de rutas tiene consultas SQL, validaciones y respuestas mezcladas en 900 líneas. ¿Qué organización aplicas?",
  cod="""const capas = ["routes", "controllers", "services", "models"];
console.log(capas.join(" -> "));""", h="muestra las capas de una API ordenada",
  pr=("En MVC, la C significa ___ (11 letras)", "controlador"),
  pr2=("La capa que habla con la base de datos es el ___ (6 letras)", "modelo"),
  ec="poner consultas SQL directamente en las rutas", out="routes -> controllers -> services -> models"),
K("Fastify", d="framework web para Node más rápido que Express y con validación incluida", u="crear APIs de alto rendimiento",
  mas="Fastify usa esquemas JSON para validar y serializar, lo que lo hace muy rápido. Las rutas se escriben parecido a Express: app.get(\"/\", async () => ({ hola: \"mundo\" })).",
  k=["Fastify es un framework web rápido para Node.", "Fastify valida con esquemas JSON.", "En Fastify, lo que devuelve la función se envía como respuesta."],
  sit="Tu API recibe miles de peticiones por segundo y quieres un framework más rápido que Express. ¿Cuál pruebas?",
  cod="""import Fastify from "fastify";
const app = Fastify();
app.get("/", async () => ({ hola: "mundo" }));
await app.listen({ port: 3000 });
console.log("Fastify en 3000");""", h="crea una API mínima con Fastify",
  pr=("El framework rápido de Node con esquemas JSON es ___ (7 letras)", "fastify"),
  pr2=("Fastify valida con esquemas en formato ___ (4 letras)", "json"),
  ec="cambiar de framework sin medir si el problema era la base de datos", out="Fastify en 3000"),
K("Proxy inverso con Nginx", d="servidor delante de Node que reparte las peticiones", u="servir HTTPS, archivos estáticos y varias apps en un mismo servidor",
  mas="Nginx recibe en el puerto 80/443 y reenvía a Node en el 3000 con proxy_pass. También comprime, sirve estáticos y maneja los certificados. En Express activa app.set(\"trust proxy\", 1).",
  k=["Nginx recibe las peticiones y las reenvía a Node.", "proxy_pass indica a dónde reenviar.", "Detrás de un proxy se activa trust proxy en Express."],
  sit="Quieres que tu API en el puerto 3000 responda en https://midominio.com. ¿Qué pones delante de Node?",
  cod="""# /etc/nginx/sites-enabled/api
# location / { proxy_pass http://localhost:3000; }
console.log("Nginx :443 -> Node :3000");""", h="describe cómo Nginx reenvía a Node",
  pr=("La instrucción de Nginx para reenviar a Node es proxy___ (5 letras con guion bajo)", "_pass"),
  pr2=("Detrás de un proxy, Express necesita trust ___ (5 letras)", "proxy"),
  ec="exponer Node directamente en el puerto 80 como root", out="Nginx :443 -> Node :3000"),
K("npx", d="comando que ejecuta un paquete de npm sin instalarlo de forma global", u="usar herramientas como create-vite una sola vez",
  mas="npx cowsay hola descarga el paquete temporalmente y lo ejecuta. También ejecuta los binarios instalados en node_modules/.bin del proyecto, como npx eslint.",
  k=["npx ejecuta paquetes sin instalarlos de forma global.", "npx usa primero los binarios del proyecto.", "npm create usa npx por dentro."],
  sit="Quieres probar una herramienta de línea de comandos una sola vez sin instalarla en todo el computador. ¿Qué comando usas?",
  cod='npx cowsay "Hola Node"', h="ejecuta un paquete sin instalarlo",
  pr=("Para ejecutar un paquete sin instalarlo se usa ___ (3 letras)", "npx"),
  pr2=("Los binarios del proyecto están en node_modules/.___ (3 letras)", "bin"),
  ec="instalar con -g herramientas que solo usarás una vez", out="< Hola Node >"),
K("Versiones de Node con nvm", d="herramienta para instalar y cambiar entre versiones de Node", u="trabajar en proyectos que piden versiones distintas",
  mas="nvm install 22 instala Node 22 y nvm use 20 cambia a la 20. Un archivo .nvmrc con el número hace que nvm use elija la versión del proyecto. En Windows existe nvm-windows. Usa versiones LTS.",
  k=["nvm instala varias versiones de Node.", "El archivo .nvmrc guarda la versión del proyecto.", "Las versiones LTS tienen soporte por más tiempo."],
  sit="Un proyecto viejo necesita Node 18 y tu proyecto nuevo Node 22. ¿Qué herramienta te deja cambiar entre ellas?",
  cod="""nvm install 22
nvm use 22
node -v""", h="instala y usa Node 22",
  pr=("El gestor de versiones de Node más usado es ___ (3 letras)", "nvm"),
  pr2=("Las versiones de Node con soporte largo se llaman ___ (3 letras)", "lts"),
  ec="usar una versión de Node sin soporte en producción", out="v22.11.0"),
]

E7 = [
K("mysql2", d="paquete para conectar Node con MySQL o MariaDB", u="usar tu base de XAMPP desde una API de Node",
  mas="import mysql from \"mysql2/promise\"; const db = await mysql.createConnection({ host, user, password, database }). Luego const [filas] = await db.query(\"SELECT * FROM usuarios\").",
  k=["mysql2 conecta Node con MySQL y MariaDB.", "mysql2/promise permite usar await.", "query devuelve un arreglo con las filas primero."],
  sit="Quieres leer la tabla usuarios de tu MySQL de XAMPP desde Express. ¿Qué paquete instalas?",
  cod="""import mysql from "mysql2/promise";
const db = await mysql.createConnection({ host: "localhost", user: "root", database: "tienda" });
const [filas] = await db.query("SELECT COUNT(*) AS total FROM usuarios");
console.log(filas[0]);""", h="cuenta los usuarios de MySQL",
  pr=("El paquete más usado para MySQL en Node es mysql___ (1 dígito)", "2"),
  pr2=("Para usar await con mysql2 se importa mysql2/___ (7 letras)", "promise"),
  ec="guardar la contraseña de la base de datos dentro del código", out="{ total: 12 }"),
K("Consultas preparadas", d="consultas con ? en lugar de pegar los datos en el texto SQL", u="evitar la inyección SQL",
  mas="db.execute(\"SELECT * FROM usuarios WHERE email = ?\", [email]) envía los datos aparte de la consulta. Nunca armes SQL con `...${email}...`.",
  k=["Las consultas preparadas usan ? para los datos.", "Los datos viajan separados del texto SQL.", "Concatenar datos en el SQL permite inyección."],
  sit="Tu login arma el SQL con el correo escrito por el usuario y alguien entró escribiendo ' OR 1=1 --. ¿Qué usas?",
  cod="""const email = "ana@correo.com";
const sql = "SELECT id FROM usuarios WHERE email = ?";
console.log(sql, [email]);""", h="separa el SQL de los datos",
  pr=("En mysql2, el lugar de cada dato se marca con el símbolo ___ (1 carácter)", "?"),
  pr2=("El ataque que se evita con consultas preparadas es la ___ SQL (9 letras)", "inyeccion", "inyección"),
  ec="armar el SQL con plantillas de texto y datos del usuario", out="SELECT id FROM usuarios WHERE email = ? [ 'ana@correo.com' ]"),
K("Pool de conexiones", d="grupo de conexiones a la base de datos que se reutilizan", u="atender muchas peticiones a la vez sin abrir una conexión por cada una",
  mas="mysql.createPool({ ..., connectionLimit: 10 }) mantiene hasta 10 conexiones abiertas y las presta a cada consulta. Abrir una conexión nueva por petición es lento y agota el servidor.",
  k=["Un pool reutiliza conexiones a la base de datos.", "connectionLimit fija cuántas conexiones como máximo.", "Abrir una conexión por petición es lento."],
  sit="Con mucho tráfico tu API da «Too many connections» porque abre una conexión nueva en cada ruta. ¿Qué usas?",
  cod="""import mysql from "mysql2/promise";
const pool = mysql.createPool({ host: "localhost", user: "root", database: "tienda", connectionLimit: 10 });
console.log("Pool con 10 conexiones");""", h="crea un pool de 10 conexiones",
  pr=("El grupo de conexiones reutilizables se llama ___ (4 letras)", "pool"),
  pr2=("La opción con el máximo de conexiones es connection___ (5 letras)", "limit"),
  ec="abrir y no cerrar una conexión en cada petición", out="Pool con 10 conexiones"),
K("Transacciones en Node", d="grupo de consultas que se aplican todas o ninguna", u="que una compra no descuente dinero sin crear el pedido",
  mas="Con una conexión del pool: beginTransaction(), las consultas, commit() si todo salió bien o rollback() en el catch. Al final, release() devuelve la conexión.",
  k=["Una transacción aplica todas las consultas o ninguna.", "rollback deshace los cambios si algo falla.", "commit confirma los cambios de la transacción."],
  sit="Al comprar se descuenta el saldo, pero si falla la creación del pedido el dinero queda descontado. ¿Qué usas?",
  cod="""const c = await pool.getConnection();
try {
  await c.beginTransaction();
  // descontar saldo y crear pedido
  await c.commit();
} catch (e) { await c.rollback(); } finally { c.release(); }
console.log("Todo o nada");""", h="aplica la compra como una sola operación",
  pr=("Para deshacer una transacción se usa ___ (8 letras)", "rollback"),
  pr2=("Para confirmar una transacción se usa ___ (6 letras)", "commit"),
  ec="olvidar release y quedarse sin conexiones en el pool", out="Todo o nada"),
K("Sequelize", d="ORM que convierte tablas SQL en clases de JavaScript", u="trabajar con MySQL o PostgreSQL sin escribir SQL a mano",
  mas="Defines un modelo con sequelize.define(\"Usuario\", { nombre: DataTypes.STRING }) y usas Usuario.findAll(), create() o destroy(). Las asociaciones (hasMany, belongsTo) representan las relaciones.",
  k=["Sequelize es un ORM para bases SQL.", "Un modelo de Sequelize representa una tabla.", "hasMany y belongsTo representan relaciones."],
  sit="Quieres manejar tus tablas de MySQL como objetos de JavaScript con métodos como findAll. ¿Qué ORM clásico usas?",
  cod="""import { Sequelize, DataTypes } from "sequelize";
const sequelize = new Sequelize("sqlite::memory:");
const Usuario = sequelize.define("Usuario", { nombre: DataTypes.STRING });
await sequelize.sync();
await Usuario.create({ nombre: "Ana" });
console.log(await Usuario.count());""", h="crea un usuario y cuenta cuántos hay",
  pr=("Las herramientas que convierten tablas en objetos se llaman ___ (3 letras)", "orm"),
  pr2=("En Sequelize, la relación «uno a muchos» se declara con has___ (4 letras)", "many"),
  ec="usar sync({ force: true }) en producción y borrar todas las tablas", out="1"),
K("Mongoose", d="biblioteca para usar MongoDB con esquemas desde Node", u="dar estructura y validación a documentos de MongoDB",
  mas="Defines new mongoose.Schema({ nombre: { type: String, required: true } }) y un modelo con mongoose.model(\"Usuario\", esquema). Luego Usuario.find(), create() o findByIdAndUpdate().",
  k=["Mongoose agrega esquemas a MongoDB.", "Un esquema define los campos y sus tipos.", "required obliga a que un campo exista."],
  sit="Tu colección de MongoDB tiene documentos con campos mal escritos y quieres validarlos desde Node. ¿Qué biblioteca usas?",
  cod="""import mongoose from "mongoose";
const esquema = new mongoose.Schema({ nombre: { type: String, required: true } });
const Usuario = mongoose.model("Usuario", esquema);
console.log(Usuario.modelName);""", h="define un modelo de usuario con Mongoose",
  pr=("La biblioteca de Node con esquemas para MongoDB es ___ (8 letras)", "mongoose"),
  pr2=("Para que un campo sea obligatorio en Mongoose se usa ___ (8 letras)", "required"),
  ec="definir el modelo dentro de cada ruta y recompilarlo", out="Usuario"),
K("Redis desde Node", d="usar Redis como caché o almacén rápido desde una app de Node", u="acelerar respuestas guardando datos que se piden mucho",
  mas="Con el paquete redis: await cliente.set(\"clave\", valor, { EX: 60 }) guarda por 60 segundos y await cliente.get(\"clave\") lo lee. Si no está, consultas la base de datos y lo guardas.",
  k=["Redis guarda datos en memoria para leerlos rápido.", "La opción EX define en cuántos segundos expira.", "Si el dato no está en caché se busca en la base de datos."],
  sit="La página de inicio consulta los mismos productos destacados miles de veces por minuto. ¿Qué usas desde Node para acelerarla?",
  cod="""import { createClient } from "redis";
const cliente = await createClient().connect();
await cliente.set("destacados", JSON.stringify([1, 2, 3]), { EX: 60 });
console.log(await cliente.get("destacados"));""", h="guarda en caché por 60 segundos",
  pr=("En Redis, la opción para expirar en segundos es ___ (2 letras)", "ex"),
  pr2=("Guardar respuestas para reutilizarlas se llama ___ (6 letras)", "cache", "caché"),
  ec="guardar en caché sin expiración y mostrar datos viejos para siempre", out="[1,2,3]"),
K("Refresh tokens", d="token de larga duración que sirve para pedir nuevos tokens de acceso", u="mantener la sesión sin usar un JWT que dure meses",
  mas="El access token dura poco (15 min) y el refresh token días; cuando el primero vence, el cliente llama a /refresh. El refresh token se guarda en una cookie httpOnly y se puede revocar.",
  k=["El access token dura poco tiempo.", "El refresh token sirve para pedir un access token nuevo.", "Un refresh token se puede revocar al cerrar sesión."],
  sit="Tus JWT duran 30 días y si alguien roba uno puede usarlo todo ese tiempo. ¿Qué esquema aplicas?",
  cod="""const acceso = { dura: "15m" }, renovacion = { dura: "7d" };
console.log(`access ${acceso.dura}, refresh ${renovacion.dura}`);""", h="muestra cuánto dura cada token",
  pr=("El token que sirve para renovar la sesión se llama ___ token (7 letras)", "refresh"),
  pr2=("El token de corta duración se llama ___ token (6 letras)", "access"),
  ec="guardar el refresh token en localStorage", out="access 15m, refresh 7d"),
K("Login con Google (OAuth)", d="permitir entrar con una cuenta de Google en lugar de una contraseña propia", u="que registrarse sea más fácil y seguro",
  mas="Rediriges a Google con tu client_id, el usuario acepta y Google vuelve a tu callback con un código. Lo cambias por los datos del usuario. Passport (passport-google-oauth20) simplifica el flujo.",
  k=["OAuth permite entrar con una cuenta de otro servicio.", "Google devuelve un código al callback de tu app.", "Passport simplifica el inicio de sesión con terceros."],
  sit="Quieres un botón «Continuar con Google» en tu app de Express. ¿Qué protocolo usa ese inicio de sesión?",
  cod="""const pasos = ["redirigir a Google", "el usuario acepta", "callback con código", "obtener perfil"];
console.log(pasos.length);""", h="cuenta los pasos del login con Google",
  pr=("El protocolo para entrar con cuentas de terceros es ___ (5 caracteres)", "oauth"),
  pr2=("La biblioteca de Node para estrategias de login es ___ (8 letras)", "passport"),
  ec="publicar el client secret de Google en el frontend", out="4"),
K("Roles y permisos", d="decidir qué puede hacer cada usuario según su rol", u="que solo un administrador pueda borrar productos",
  mas="Guardas el rol en el usuario (admin, editor, cliente) y un middleware lo revisa: const soloAdmin = (req, res, next) => req.usuario.rol === \"admin\" ? next() : res.sendStatus(403).",
  k=["Un rol agrupa los permisos de un tipo de usuario.", "Un middleware puede revisar el rol antes de la ruta.", "Sin permiso se responde 403."],
  sit="Cualquier usuario con sesión puede llamar a DELETE /productos/5. ¿Qué agregas a esa ruta?",
  cod="""const soloAdmin = (req, res, next) => (req.usuario?.rol === "admin" ? next() : res.sendStatus(403));
app.delete("/productos/:id", soloAdmin, (req, res) => res.sendStatus(204));
console.log("Solo admin puede borrar");""", h="protege la ruta para administradores",
  pr=("Si el usuario no tiene el rol necesario se responde ___ (3 dígitos)", "403"),
  pr2=("El rol con todos los permisos suele llamarse ___ (5 letras)", "admin"),
  ec="ocultar el botón en el frontend pero dejar la ruta abierta", out="Solo admin puede borrar"),
K("XSS", d="ataque que inyecta scripts en una página a través de datos del usuario", u="saber cómo proteger tu app al mostrar contenido de otros",
  mas="Si muestras un comentario con innerHTML y contiene <script>, se ejecuta en el navegador de otros. Escapa siempre (textContent, <%= %>, React lo hace solo), usa Content-Security-Policy y cookies httpOnly.",
  k=["XSS inyecta scripts en páginas de otros usuarios.", "Escapar el texto evita que se ejecute como HTML.", "Las cookies httpOnly no se pueden robar con XSS."],
  sit="Un usuario dejó un comentario con <script> y roba las sesiones de quienes lo leen. ¿Cómo se llama ese ataque?",
  cod="""const escapar = (t) => t.replace(/[<>&"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" })[c]);
console.log(escapar("<script>robar()</script>"));""", h="escapa un comentario peligroso",
  pr=("El ataque de inyectar scripts en una página se llama ___ (3 letras)", "xss"),
  pr2=("Para mostrar texto sin interpretar HTML se usa text___ (7 letras)", "content"),
  ec="mostrar datos del usuario con innerHTML", out="&lt;script&gt;robar()&lt;/script&gt;"),
K("CSRF", d="ataque que hace que el navegador de la víctima envíe peticiones sin que lo sepa", u="proteger formularios y acciones con sesión por cookie",
  mas="Otra página hace un POST a tu sitio y el navegador envía la cookie de sesión. Se evita con cookies sameSite, un token CSRF en cada formulario y revisando el Origin.",
  k=["CSRF aprovecha que el navegador envía las cookies solo.", "Un token CSRF prueba que la petición viene de tu página.", "sameSite en las cookies reduce el riesgo de CSRF."],
  sit="Una página maliciosa envía un formulario oculto a tu /transferir y usa la sesión de la víctima. ¿Qué ataque es?",
  cod="""const token = crypto.randomUUID();
console.log(token.length);""", h="genera un token aleatorio para formularios",
  pr=("El ataque de enviar peticiones con la sesión de otro se llama ___ (4 letras)", "csrf"),
  pr2=("La opción de cookie que limita los envíos entre sitios es same___ (4 letras)", "site"),
  ec="aceptar POST con sesión por cookie sin token ni sameSite", out="36"),
K(".env.example", d="archivo con los nombres de las variables de entorno pero sin valores secretos", u="que otros sepan qué configurar sin ver tus claves",
  mas="Subes .env.example a Git con PORT=3000 y DB_PASSWORD= vacío, y pones .env en .gitignore. Quien clona copia el ejemplo a .env y llena sus valores.",
  k=[".env.example lista las variables sin sus secretos.", ".env debe estar en .gitignore.", "Quien clona copia .env.example a .env."],
  sit="Tu compañero clonó el proyecto y no sabe qué variables necesita, pero no quieres subir tus claves. ¿Qué archivo subes?",
  cod="""// .env.example
// PORT=3000
// DB_PASSWORD=
console.log(".env queda fuera de Git");""", h="describe el archivo de ejemplo",
  pr=("El archivo con variables sin secretos se llama .env.___ (7 letras)", "example"),
  pr2=("El archivo .env debe ir en .git___ (6 letras)", "ignore"),
  ec="subir el archivo .env con contraseñas a GitHub", out=".env queda fuera de Git"),
K("Correos con Nodemailer", d="paquete para enviar correos desde Node", u="mandar códigos de verificación o recuperar contraseñas",
  mas="createTransport({ host, port, auth }) configura el servidor SMTP y sendMail({ to, subject, html }) envía. Para recuperar contraseña: genera un token aleatorio de un solo uso que venza pronto.",
  k=["Nodemailer envía correos desde Node.", "Los correos salen por un servidor SMTP.", "Los enlaces de recuperación deben vencer pronto."],
  sit="Necesitas enviar un enlace para restablecer la contraseña al correo del usuario. ¿Qué paquete de Node usas?",
  cod="""import nodemailer from "nodemailer";
const t = nodemailer.createTransport({ host: "smtp.ejemplo.com", port: 587, auth: { user: "app", pass: process.env.SMTP } });
console.log("Transporte SMTP listo");""", h="prepara el envío de correos",
  pr=("El paquete de Node para enviar correos es ___ (10 letras)", "nodemailer"),
  pr2=("El protocolo para enviar correos es ___ (4 letras)", "smtp"),
  ec="enviar enlaces de recuperación que nunca vencen", out="Transporte SMTP listo"),
K("Compresión de respuestas", d="comprimir las respuestas con gzip o brotli antes de enviarlas", u="que la API y la página carguen más rápido",
  mas="app.use(compression()) comprime el JSON y el HTML si el navegador lo acepta (Accept-Encoding). Un JSON de 500 KB puede bajar a 60 KB.",
  k=["Comprimir reduce el tamaño de las respuestas.", "El navegador indica con Accept-Encoding qué compresión acepta.", "gzip y brotli son formatos de compresión."],
  sit="Tus respuestas JSON pesan 800 KB y en celulares tardan mucho. ¿Qué middleware agregas?",
  cod="""import compression from "compression";
app.use(compression());
console.log("Respuestas comprimidas con gzip");""", h="comprime todas las respuestas",
  pr=("El middleware de Express para comprimir se llama ___ (11 letras)", "compression"),
  pr2=("El formato de compresión más común en la web es ___ (4 letras)", "gzip"),
  ec="comprimir imágenes JPG que ya vienen comprimidas", out="Respuestas comprimidas con gzip"),
K("ETag y caché HTTP", d="cabeceras que permiten al navegador reutilizar respuestas sin descargarlas", u="ahorrar datos y tiempo en respuestas que no cambian",
  mas="Express envía un ETag (huella de la respuesta). Si el navegador manda If-None-Match con la misma huella, el servidor responde 304 sin cuerpo. Cache-Control: max-age=3600 permite guardar una hora.",
  k=["El ETag es una huella de la respuesta.", "304 significa que el navegador puede usar su copia.", "Cache-Control indica cuánto tiempo guardar una respuesta."],
  sit="El navegador descarga una y otra vez el mismo catálogo que no cambia en todo el día. ¿Qué cabecera indica cuánto tiempo guardarlo?",
  cod="""app.get("/catalogo", (req, res) => {
  res.set("Cache-Control", "public, max-age=3600");
  res.json([]);
});
console.log("Guardar 1 hora");""", h="permite guardar el catálogo una hora",
  pr=("La cabecera para decir cuánto guardar una respuesta es Cache-___ (7 letras)", "control"),
  pr2=("El código cuando el navegador puede usar su copia es ___ (3 dígitos)", "304"),
  ec="poner caché larga a datos privados del usuario", out="Guardar 1 hora"),
K("Socket.IO", d="biblioteca de tiempo real sobre WebSockets con reconexión y salas", u="hacer chats, notificaciones y juegos en vivo",
  mas="El servidor hace io.on(\"connection\", s => s.on(\"mensaje\", m => io.emit(\"mensaje\", m))). Tiene salas (socket.join(\"sala1\")), reconexión automática y funciona aunque WebSocket falle.",
  k=["Socket.IO comunica en tiempo real.", "io.emit envía un evento a todos los conectados.", "socket.join agrega un cliente a una sala."],
  sit="Quieres un chat donde los mensajes aparezcan al instante en todas las pantallas, con salas por grupo. ¿Qué biblioteca usas?",
  cod="""import { Server } from "socket.io";
const io = new Server(3001, { cors: { origin: "*" } });
io.on("connection", (s) => s.on("mensaje", (m) => io.emit("mensaje", m)));
console.log("Chat en tiempo real en 3001");""", h="reenvía cada mensaje a todos",
  pr=("En Socket.IO, para unirse a una sala se usa socket.___ (4 letras)", "join"),
  pr2=("Para enviar un evento a todos se usa io.___ (4 letras)", "emit"),
  ec="consultar el servidor cada segundo en lugar de usar tiempo real", out="Chat en tiempo real en 3001"),
K("Validar archivos subidos", d="revisar tipo, tamaño y contenido de lo que suben los usuarios", u="evitar que suban programas maliciosos o archivos gigantes",
  mas="Revisa el mimetype y la extensión permitidos, limita el tamaño, cambia el nombre por uno aleatorio y guárdalos fuera de las carpetas que se ejecutan. Para imágenes, procesarlas con sharp elimina contenido extraño.",
  k=["Hay que limitar el tamaño de los archivos subidos.", "El nombre original del archivo no es confiable.", "Los archivos subidos no deben guardarse donde se ejecutan."],
  sit="Alguien subió un archivo .php como «foto» y lo abrió en tu servidor. ¿Qué te faltó hacer?",
  cod="""const permitidos = ["image/png", "image/jpeg", "image/webp"];
console.log(permitidos.includes("application/x-php"));""", h="revisa si el tipo de archivo está permitido",
  pr=("El tipo de un archivo subido se revisa en su mime___ (4 letras)", "type"),
  pr2=("La biblioteca de Node para procesar imágenes es ___ (5 letras)", "sharp"),
  ec="guardar los archivos con el nombre que manda el usuario", out="false"),
K("HTTPS en desarrollo y producción", d="conexiones cifradas con certificados TLS", u="que nadie pueda leer contraseñas ni datos en el camino",
  mas="En producción el certificado lo da Let's Encrypt (gratis) y suele ponerlo Nginx o el hosting. En local puedes usar mkcert. Activa HSTS para obligar a usar HTTPS.",
  k=["HTTPS cifra la comunicación con TLS.", "Let's Encrypt da certificados gratis.", "HSTS obliga al navegador a usar HTTPS."],
  sit="Tu API de login funciona con http:// y las contraseñas viajan sin cifrar. ¿Qué necesitas?",
  cod="""const url = new URL("https://api.ejemplo.com/login");
console.log(url.protocol);""", h="muestra el protocolo seguro",
  pr=("La autoridad que da certificados gratis es Let's ___ (7 letras)", "encrypt"),
  pr2=("La cabecera que obliga a usar HTTPS se llama ___ (4 letras)", "hsts"),
  ec="enviar contraseñas por HTTP sin cifrar", out="https:"),
K("PostgreSQL con pg", d="paquete para conectar Node con PostgreSQL", u="usar la base de datos relacional más usada en la nube",
  mas="const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL }) y await pool.query(\"SELECT * FROM tareas WHERE id = $1\", [id]). En PostgreSQL los datos van en $1, $2… en lugar de ?.",
  k=["pg conecta Node con PostgreSQL.", "En pg los datos se marcan con $1, $2…", "DATABASE_URL guarda la cadena de conexión."],
  sit="Tu hosting te da una base PostgreSQL con una DATABASE_URL. ¿Qué paquete de Node usas para conectarte?",
  cod="""const sql = "SELECT * FROM tareas WHERE id = $1";
console.log(sql.includes("$1"));""", h="arma una consulta de PostgreSQL con parámetro",
  pr=("El paquete de Node para PostgreSQL se llama ___ (2 letras)", "pg"),
  pr2=("La variable con la cadena de conexión suele llamarse DATABASE___ (4 caracteres)", "_url"),
  ec="usar ? como en MySQL y que PostgreSQL dé error de sintaxis", out="true"),
K("JSON en Node", d="convertir objetos a texto JSON y de vuelta", u="guardar datos en archivos o enviarlos por una API",
  mas="JSON.stringify(obj, null, 2) lo convierte en texto con sangría y JSON.parse(texto) lo vuelve objeto. JSON.parse lanza un error si el texto está mal: envuélvelo en try/catch.",
  k=["JSON.stringify convierte un objeto en texto JSON.", "JSON.parse convierte texto JSON en objeto.", "JSON.parse lanza un error si el texto es inválido."],
  sit="Quieres guardar la lista de tareas en un archivo y leerla cuando el programa vuelva a abrir. ¿Qué funciones conviertes de ida y vuelta?",
  cod="""const texto = JSON.stringify({ tarea: "estudiar", hecha: false });
console.log(JSON.parse(texto).tarea);""", h="convierte un objeto a JSON y de vuelta",
  pr=("Para convertir texto JSON en objeto se usa JSON.___ (5 letras)", "parse"),
  pr2=("Para convertir un objeto en texto JSON se usa JSON.___ (9 letras)", "stringify"),
  ec="usar JSON.parse sin try/catch con datos que vienen de afuera", out="estudiar"),
K("Probar APIs con Thunder Client", d="herramientas para enviar peticiones a tu API sin un frontend", u="probar POST, PUT y DELETE mientras programas",
  mas="Thunder Client (extensión de VS Code), Postman o Bruno permiten elegir el método, la URL, cabeceras y cuerpo JSON. También puedes usar curl o un archivo .http con REST Client.",
  k=["Postman y Thunder Client envían peticiones de prueba.", "Se pueden enviar cuerpos JSON y cabeceras.", "curl también prueba APIs desde la terminal."],
  sit="Tu ruta POST /usuarios aún no tiene formulario y quieres probarla ya. ¿Qué tipo de herramienta usas?",
  cod="""curl -X POST http://localhost:3000/usuarios -H "Content-Type: application/json" -d '{"nombre":"Ana"}'""", h="envía un usuario con curl",
  pr=("La extensión de VS Code para probar APIs se llama Thunder ___ (6 letras)", "client"),
  pr2=("En curl, el método se indica con la opción -___ (1 letra)", "x"),
  ec="probar POST desde la barra del navegador, que solo hace GET", out='{"id":1,"nombre":"Ana"}'),
]

E8 = [
K("Supertest", d="biblioteca para probar rutas de Express sin levantar el servidor", u="comprobar automáticamente que tu API responde bien",
  mas="request(app).get(\"/api/salud\").expect(200) hace la petición en memoria. Se combina con Vitest, Jest o node:test para revisar el cuerpo de la respuesta.",
  k=["Supertest prueba rutas de Express.", "Supertest no necesita levantar el servidor.", "expect(200) comprueba el código de estado."],
  sit="Quieres una prueba automática que verifique que GET /api/salud responde 200 en cada cambio. ¿Qué biblioteca usas?",
  cod="""import request from "supertest";
import { test } from "node:test";
test("salud", async () => {
  await request(app).get("/api/salud").expect(200);
});
console.log("1 prueba");""", h="prueba que la ruta de salud responde 200",
  pr=("La biblioteca para probar rutas de Express es ___ (9 letras)", "supertest"),
  pr2=("Para comprobar el código de estado se usa ___(200) (6 letras)", "expect"),
  ec="exportar la app con listen y que las pruebas dejen el puerto ocupado", out="1 prueba"),
K("Mocks en pruebas", d="reemplazar una función real por una falsa durante una prueba", u="probar sin llamar a la API de pagos ni enviar correos de verdad",
  mas="Con vi.fn() o mock.fn() creas funciones falsas que registran cómo las llamaron. Así pruebas tu lógica sin depender de servicios externos lentos o que cobran.",
  k=["Un mock reemplaza una función real en una prueba.", "Un mock registra cuántas veces y cómo lo llamaron.", "Los mocks evitan llamar servicios externos en las pruebas."],
  sit="Tu prueba de registro envía un correo real cada vez que la ejecutas. ¿Qué técnica usas para evitarlo?",
  cod="""import { mock } from "node:test";
const enviarCorreo = mock.fn();
enviarCorreo("ana@correo.com");
console.log(enviarCorreo.mock.callCount());""", h="cuenta las llamadas a una función falsa",
  pr=("Una función falsa para pruebas se llama ___ (4 letras)", "mock"),
  pr2=("En Vitest, una función falsa se crea con vi.___() (2 letras)", "fn"),
  ec="hacer pruebas que dependen de internet y fallan al azar", out="1"),
K("Cobertura de pruebas", d="porcentaje del código que ejecutan tus pruebas", u="encontrar partes del código que nadie está probando",
  mas="node --test --experimental-test-coverage o vitest --coverage muestran qué líneas y ramas se ejecutaron. Una cobertura alta ayuda, pero no garantiza que las pruebas revisen lo correcto.",
  k=["La cobertura mide qué parte del código ejecutan las pruebas.", "Una cobertura del 100 % no garantiza que no haya errores.", "vitest --coverage genera el reporte de cobertura."],
  sit="Quieres saber qué funciones de tu API no tienen ninguna prueba. ¿Qué reporte generas?",
  cod="""const lineas = 200, probadas = 170;
console.log(`${(probadas / lineas) * 100}%`);""", h="calcula el porcentaje de cobertura",
  pr=("El porcentaje de código que ejecutan las pruebas se llama ___ (9 letras)", "cobertura"),
  pr2=("En Vitest, el reporte se pide con la opción --___ (8 letras)", "coverage"),
  ec="perseguir el 100 % con pruebas que no revisan nada", out="85%"),
K("Depurar con --inspect", d="conectar las herramientas de Chrome o VS Code a un programa de Node", u="pausar en una línea y ver los valores de las variables",
  mas="node --inspect app.js abre un puerto de depuración; en Chrome vas a chrome://inspect o en VS Code usas «JavaScript Debug Terminal». debugger; en el código pausa ahí.",
  k=["node --inspect permite depurar con Chrome o VS Code.", "La palabra debugger pausa la ejecución.", "Al pausar se ven los valores de las variables."],
  sit="Tu API devuelve un total incorrecto y llenar el código de console.log ya no te ayuda. ¿Cómo arrancas Node para depurar?",
  cod="""// node --inspect app.js
const total = [10, 20].reduce((a, b) => a + b, 0);
console.log(total);""", h="calcula el total que quieres revisar",
  pr=("Para depurar Node se arranca con la opción --___ (7 letras)", "inspect"),
  pr2=("La palabra que pausa el programa en esa línea es ___ (8 letras)", "debugger"),
  ec="dejar sentencias debugger en el código de producción", out="30"),
K("Fugas de memoria", d="memoria que el programa ocupa y nunca libera", u="evitar que el servidor se vuelva lento y se caiga con el tiempo",
  mas="Arreglos o cachés que crecen sin límite, oyentes de eventos que no se quitan y temporizadores olvidados son las causas típicas. process.memoryUsage() y los snapshots de Chrome ayudan a encontrarlas.",
  k=["Una fuga de memoria hace crecer la memoria sin parar.", "Las cachés sin límite causan fugas.", "process.memoryUsage muestra cuánta memoria usa Node."],
  sit="Tu servidor arranca usando 80 MB y a los dos días usa 2 GB hasta que se cae. ¿Qué problema tiene?",
  cod="""const mb = (b) => Math.round(b / 1024 / 1024);
console.log(typeof mb(process.memoryUsage().heapUsed));""", h="mide la memoria en megabytes",
  pr=("La memoria que nunca se libera se llama ___ de memoria (4 letras)", "fuga"),
  pr2=("La función que mide la memoria es process.memory___ (5 letras)", "usage"),
  ec="guardar todo en una caché en memoria sin límite", out="number"),
K("cluster", d="módulo para ejecutar varias copias de tu servidor, una por núcleo", u="aprovechar todos los núcleos del procesador",
  mas="Node usa un solo hilo para tu JavaScript. cluster crea procesos hijos que comparten el mismo puerto. pm2 start app.js -i max hace lo mismo sin código.",
  k=["Node ejecuta tu JavaScript en un solo hilo.", "cluster crea una copia del servidor por núcleo.", "pm2 -i max usa todos los núcleos."],
  sit="Tu servidor tiene 8 núcleos y Node solo usa uno al 100 %. ¿Qué módulo usas para aprovecharlos todos?",
  cod="""import os from "node:os";
console.log(`Copias posibles: ${os.availableParallelism() > 0}`);""", h="revisa cuántas copias podrías lanzar",
  pr=("El módulo de Node para una copia por núcleo es ___ (7 letras)", "cluster"),
  pr2=("Con pm2, la opción para usar todos los núcleos es -i ___ (3 letras)", "max"),
  ec="guardar sesiones en memoria y perderlas entre copias del cluster", out="Copias posibles: true"),
K("Colas de trabajos", d="tareas que se guardan para hacerlas después en segundo plano", u="no hacer esperar al usuario mientras se envían correos o se procesan videos",
  mas="BullMQ guarda los trabajos en Redis: la API agrega cola.add(\"correo\", datos) y responde al instante; un worker los procesa con reintentos si fallan.",
  k=["Una cola guarda tareas para hacerlas después.", "Un worker procesa los trabajos de la cola.", "BullMQ usa Redis para guardar los trabajos."],
  sit="Al registrarse, el usuario espera 6 segundos mientras se envía el correo de bienvenida. ¿Qué usas para enviarlo en segundo plano?",
  cod="""const cola = [];
cola.push({ tipo: "correo", para: "ana@correo.com" });
console.log(`Trabajos pendientes: ${cola.length}`);""", h="agrega un trabajo a la cola",
  pr=("La biblioteca de colas sobre Redis más usada en Node es bull___ (2 letras)", "mq"),
  pr2=("El proceso que hace los trabajos de la cola se llama ___ (6 letras)", "worker"),
  ec="hacer tareas lentas dentro de la petición del usuario", out="Trabajos pendientes: 1"),
K("Tareas programadas", d="código que se ejecuta solo a cierta hora o cada cierto tiempo", u="enviar recordatorios diarios o limpiar datos viejos",
  mas="node-cron usa la sintaxis de cron: cron.schedule(\"0 18 * * *\", fn) se ejecuta todos los días a las 6 p. m. Con varias copias del servidor, asegúrate de que corra en una sola.",
  k=["node-cron programa tareas con la sintaxis de cron.", "\"0 18 * * *\" significa todos los días a las 6 p. m.", "Con varias copias, la tarea debe correr en una sola."],
  sit="Cada noche debes borrar los códigos de verificación vencidos. ¿Qué paquete de Node usas para programarlo?",
  cod="""// cron.schedule("0 3 * * *", limpiar)
const partes = "0 3 * * *".split(" ");
console.log(`Hora: ${partes[1]}`);""", h="lee la hora de una expresión cron",
  pr=("El paquete de Node para programar tareas es node-___ (4 letras)", "cron"),
  pr2=("Una expresión cron tiene ___ campos (5 letras)", "cinco"),
  ec="programar la misma tarea en cada copia del servidor y ejecutarla repetida", out="Hora: 3"),
K("GraphQL", d="lenguaje de consultas donde el cliente pide exactamente los campos que necesita", u="evitar pedir datos de más o hacer muchas peticiones",
  mas="Con un esquema (type Usuario { nombre: String }) y resolvers, el cliente envía { usuario(id: 1) { nombre } } a una sola ruta /graphql. Apollo Server y Yoga son servidores populares.",
  k=["En GraphQL el cliente elige los campos que recibe.", "GraphQL suele usar una sola ruta /graphql.", "Los resolvers obtienen los datos de cada campo."],
  sit="Tu app móvil solo necesita el nombre del usuario, pero la API REST le manda 40 campos. ¿Qué alternativa permite pedir solo ese campo?",
  cod="""const consulta = "{ usuario(id: 1) { nombre } }";
console.log(consulta.includes("nombre"));""", h="arma una consulta que pide solo el nombre",
  pr=("Las funciones que traen los datos en GraphQL se llaman ___ (9 letras)", "resolvers"),
  pr2=("Un servidor popular de GraphQL para Node es ___ Server (6 letras)", "apollo"),
  ec="usar GraphQL sin limitar la profundidad de las consultas", out="true"),
K("NestJS", d="framework de Node con módulos, controladores e inyección de dependencias", u="construir APIs grandes con una estructura ordenada",
  mas="NestJS usa TypeScript y decoradores: @Controller(\"usuarios\") y @Get() definen rutas, y los servicios se inyectan en el constructor. Por dentro usa Express o Fastify.",
  k=["NestJS organiza la app en módulos.", "NestJS usa decoradores como @Get.", "NestJS funciona sobre Express o Fastify."],
  sit="Tu equipo crece y quiere una API con estructura fija, TypeScript y estilo parecido a Angular. ¿Qué framework eligen?",
  cod="""// @Controller("usuarios") export class UsuariosController { @Get() todos() { return ["Ana"]; } }
console.log(["Ana"]);""", h="describe un controlador de NestJS",
  pr=("En NestJS, las rutas se marcan con ___ como @Get (11 letras)", "decoradores"),
  pr2=("NestJS funciona por dentro sobre Express o ___ (7 letras)", "fastify"),
  ec="usar NestJS para un script de 50 líneas", out="[ 'Ana' ]"),
K("Microservicios", d="dividir una aplicación grande en servicios pequeños e independientes", u="que equipos distintos desplieguen partes sin tocar las demás",
  mas="Usuarios, pagos y catálogo pueden ser servicios separados que se hablan por HTTP o colas de mensajes. Dan independencia, pero suman complejidad: empieza con un monolito ordenado.",
  k=["Un microservicio hace una sola parte del sistema.", "Los microservicios se comunican por HTTP o mensajes.", "Para proyectos pequeños un monolito ordenado es más simple."],
  sit="Tu tienda creció tanto que el equipo de pagos no puede desplegar sin esperar al del catálogo. ¿Qué arquitectura consideran?",
  cod="""const servicios = ["usuarios", "pagos", "catalogo"];
console.log(servicios.length);""", h="cuenta los servicios del sistema",
  pr=("Una app en un solo bloque se llama ___ (8 letras)", "monolito"),
  pr2=("Los servicios pequeños e independientes se llaman ___ (14 letras)", "microservicios"),
  ec="dividir en microservicios un proyecto de una sola persona", out="3"),
K("Workspaces de npm", d="varios paquetes en un solo repositorio que comparten dependencias", u="tener frontend, backend y librerías comunes juntos",
  mas="En el package.json raíz pones \"workspaces\": [\"apps/*\", \"packages/*\"]. npm install instala todo una vez y npm run dev -w apps/api ejecuta un paquete concreto.",
  k=["Los workspaces agrupan varios paquetes en un repositorio.", "npm install en la raíz instala todos los workspaces.", "-w ejecuta un comando en un workspace concreto."],
  sit="Tu frontend y tu backend comparten funciones de validación copiadas a mano en los dos. ¿Qué función de npm usas para compartirlas?",
  cod="""const raiz = { name: "mi-proyecto", workspaces: ["apps/*", "packages/*"] };
console.log(raiz.workspaces.length);""", h="cuenta las carpetas de workspaces",
  pr=("Para ejecutar en un workspace concreto se usa la opción -___ (1 letra)", "w"),
  pr2=("La clave del package.json para varios paquetes es ___ (10 letras)", "workspaces"),
  ec="copiar el mismo código en varios proyectos en lugar de compartirlo", out="2"),
K("Dockerizar una app de Node", d="empaquetar tu API con Node y sus dependencias en una imagen", u="que funcione igual en tu PC y en el servidor",
  mas="FROM node:22-alpine, COPY package*.json, RUN npm ci --omit=dev, COPY . y CMD [\"node\", \"app.js\"]. Copiar package.json antes que el código aprovecha la caché de capas.",
  k=["npm ci instala exactamente lo del package-lock.", "--omit=dev omite las dependencias de desarrollo.", "Copiar package.json primero aprovecha la caché de Docker."],
  sit="Tu API funciona en tu PC pero en el servidor falla por otra versión de Node. ¿Qué haces para que sea igual en todos lados?",
  cod="""// FROM node:22-alpine
// COPY package*.json ./
// RUN npm ci --omit=dev
// COPY . .
// CMD ["node", "app.js"]
console.log("Imagen lista");""", h="describe el Dockerfile de una API",
  pr=("El comando de instalación exacta para producción es npm ___ (2 letras)", "ci"),
  pr2=("La imagen base pequeña de Node termina en -___ (6 letras)", "alpine"),
  ec="copiar node_modules del PC dentro de la imagen", out="Imagen lista"),
K("CI para Node con GitHub Actions", d="ejecutar pruebas y lint automáticamente en cada push", u="enterarte de un error antes de que llegue a producción",
  mas="Un workflow usa actions/setup-node con la versión de Node, corre npm ci, npm run lint y npm test. Si algo falla, el pull request queda marcado en rojo.",
  k=["CI ejecuta las pruebas en cada push.", "setup-node instala la versión de Node en el workflow.", "Un pull request con pruebas fallidas se marca en rojo."],
  sit="Un compañero subió código que rompe las pruebas y nadie lo notó hasta producción. ¿Qué configuras en GitHub?",
  cod="""const pasos = ["checkout", "setup-node", "npm ci", "npm test"];
console.log(pasos.join(" → "));""", h="muestra los pasos del workflow",
  pr=("La acción que instala Node en un workflow es setup-___ (4 letras)", "node"),
  pr2=("Ejecutar pruebas en cada push se llama integración ___ (8 letras)", "continua"),
  ec="hacer merge sin esperar a que pasen las pruebas", out="checkout → setup-node → npm ci → npm test"),
K("Health checks", d="ruta que dice si el servidor y sus dependencias están funcionando", u="que el hosting reinicie la app si deja de responder",
  mas="GET /salud responde 200 con { ok: true } si la base de datos responde, o 503 si no. Docker, Kubernetes y los balanceadores la consultan cada pocos segundos.",
  k=["Un health check indica si el servidor funciona.", "Si una dependencia falla se responde 503.", "Kubernetes consulta el health check para reiniciar la app."],
  sit="Tu API se queda colgada sin caerse y el hosting no se da cuenta para reiniciarla. ¿Qué ruta agregas?",
  cod="""app.get("/salud", async (req, res) => {
  res.status(200).json({ ok: true });
});
console.log({ ok: true });""", h="responde que el servidor está bien",
  pr=("Si el servidor no puede atender se responde ___ (3 dígitos)", "503"),
  pr2=("La ruta que dice si la app funciona se llama health ___ (5 letras)", "check"),
  ec="que el health check responda 200 aunque la base de datos esté caída", out="{ ok: true }"),
K("Apagado ordenado", d="terminar las peticiones en curso y cerrar conexiones antes de salir", u="no cortar compras a la mitad cuando el servidor se reinicia",
  mas="Al recibir SIGTERM: server.close() deja de aceptar conexiones nuevas, esperas las actuales, cierras la base de datos y luego process.exit(0).",
  k=["SIGTERM es la señal que pide terminar el programa.", "server.close deja de aceptar conexiones nuevas.", "Hay que cerrar la base de datos antes de salir."],
  sit="Cada vez que despliegas, algunos usuarios reciben errores porque el servidor se cierra de golpe. ¿Qué implementas?",
  cod="""process.on("SIGTERM", () => {
  console.log("Cerrando con calma…");
  // server.close(() => process.exit(0));
});
console.log("Esperando SIGTERM");""", h="prepara el cierre ordenado",
  pr=("La señal que pide al programa terminar es SIG___ (4 letras)", "term"),
  pr2=("Para dejar de aceptar conexiones se usa server.___() (5 letras)", "close"),
  ec="matar el proceso sin esperar las peticiones en curso", out="Esperando SIGTERM"),
K("npm audit", d="comando que busca vulnerabilidades conocidas en tus dependencias", u="enterarte si un paquete que usas tiene un fallo de seguridad",
  mas="npm audit lista los paquetes vulnerables y su gravedad; npm audit fix actualiza los que se pueden arreglar sin romper. Dependabot lo hace automático en GitHub.",
  k=["npm audit busca vulnerabilidades en las dependencias.", "npm audit fix actualiza los paquetes vulnerables.", "Dependabot automatiza las actualizaciones de seguridad."],
  sit="Te avisan de una vulnerabilidad grave en un paquete muy usado. ¿Qué comando revisa si tu proyecto la tiene?",
  cod="""const reporte = { criticas: 0, altas: 1 };
console.log(reporte.altas > 0 ? "Actualizar" : "Todo bien");""", h="decide si hay que actualizar",
  pr=("Para arreglar vulnerabilidades automáticamente se usa npm audit ___ (3 letras)", "fix"),
  pr2=("El bot de GitHub que actualiza dependencias es ___ (10 letras)", "dependabot"),
  ec="usar npm audit fix --force sin revisar y romper la app", out="Actualizar"),
K("Lint y formato", d="herramientas que revisan errores comunes y dan el mismo estilo al código", u="que todo el equipo escriba igual y se detecten fallos antes de ejecutar",
  mas="ESLint encuentra variables sin usar, awaits olvidados y malas prácticas; Prettier formatea espacios y comillas. Se ejecutan con npm run lint y al guardar en el editor.",
  k=["ESLint encuentra errores comunes en el código.", "Prettier da formato uniforme al código.", "El lint puede ejecutarse en CI y al guardar."],
  sit="En tu equipo cada uno usa comillas y sangrías distintas y los pull requests se llenan de cambios de formato. ¿Qué herramienta lo resuelve?",
  cod="""const reglas = { semi: true, singleQuote: false };
console.log(Object.keys(reglas).length);""", h="cuenta las reglas de formato",
  pr=("La herramienta que da formato automático al código es ___ (8 letras)", "prettier"),
  pr2=("La herramienta que encuentra errores comunes es ___ (6 letras)", "eslint"),
  ec="discutir estilos en cada revisión en lugar de automatizarlos", out="2"),
K("Serverless con Node", d="funciones que se ejecutan en la nube solo cuando se llaman", u="publicar una API sin administrar servidores",
  mas="Vercel Functions, Netlify Functions o AWS Lambda ejecutan export default async (req) => Response.json(...) por cada petición. Pagas por uso, pero hay arranque en frío y límites de tiempo.",
  k=["Serverless ejecuta funciones solo cuando se llaman.", "En serverless se paga por uso.", "El arranque en frío hace lenta la primera llamada."],
  sit="Tienes una API pequeña que recibe pocas visitas y no quieres pagar un servidor encendido todo el día. ¿Qué modelo eliges?",
  cod="""const handler = async () => ({ statusCode: 200, body: "hola" });
console.log((await handler()).statusCode);""", h="ejecuta una función serverless",
  pr=("El servicio serverless de Amazon se llama AWS ___ (6 letras)", "lambda"),
  pr2=("La lentitud de la primera llamada se llama arranque en ___ (4 letras)", "frio", "frío"),
  ec="guardar archivos en el disco de una función serverless", out="200"),
K("Proyecto final: API completa", d="unir rutas, base de datos, autenticación, pruebas y despliegue", u="tener un proyecto de portafolio que demuestre todo lo aprendido",
  mas="Una API de tareas o tienda con Express, MySQL o MongoDB, registro con bcrypt y JWT, validación con zod, pruebas con Supertest, documentación OpenAPI, Docker y CI en GitHub Actions.",
  k=["Un proyecto final reúne todo lo aprendido.", "Una buena API incluye pruebas y documentación.", "Publicar el proyecto permite mostrarlo en un portafolio."],
  sit="Terminaste el curso de Node y quieres demostrarlo en una entrevista. ¿Qué construyes?",
  cod="""const piezas = ["Express", "MySQL", "JWT", "zod", "Supertest", "Docker", "CI"];
console.log(`${piezas.length} piezas`);""", h="cuenta las piezas del proyecto",
  pr=("El lugar donde muestras tus proyectos a empresas es tu ___ (10 letras)", "portafolio"),
  pr2=("Para empaquetar la API con todo lo necesario se usa ___ (6 letras)", "docker"),
  ec="dejar el proyecto sin README ni instrucciones para ejecutarlo", out="7 piezas"),
K("Scripts de npm", d="comandos con nombre definidos en el package.json", u="arrancar, probar y construir el proyecto con comandos cortos",
  mas="En \"scripts\": { \"dev\": \"node --watch app.js\", \"test\": \"node --test\" } defines atajos. Se ejecutan con npm run dev; start y test no necesitan run.",
  k=["Los scripts de npm se definen en package.json.", "npm run dev ejecuta el script dev.", "npm start y npm test no necesitan run."],
  sit="Siempre escribes un comando largo para arrancar tu servidor en modo desarrollo. ¿Dónde lo guardas como atajo?",
  cod="""const pkg = { scripts: { dev: "node --watch app.js", test: "node --test" } };
console.log(Object.keys(pkg.scripts).join(", "));""", h="muestra los scripts del proyecto",
  pr=("Para ejecutar el script dev se escribe npm ___ dev (3 letras)", "run"),
  pr2=("Los scripts se definen dentro de la clave ___ del package.json (7 letras)", "scripts"),
  ec="pedir a todos que memoricen comandos largos en vez de usar scripts", out="dev, test"),
K("Versiones semánticas en package.json", d="los símbolos ^ y ~ que indican qué actualizaciones aceptar", u="evitar que una actualización rompa tu proyecto",
  mas="^1.4.2 acepta 1.x.x (cambios menores y parches), ~1.4.2 solo 1.4.x (parches) y 1.4.2 exacto. package-lock.json fija las versiones instaladas: súbelo a Git.",
  k=["^ acepta versiones menores y parches.", "~ acepta solo parches.", "package-lock.json fija las versiones exactas instaladas."],
  sit="Quieres aceptar solo correcciones de errores de una librería y nunca funciones nuevas. ¿Qué símbolo pones antes de la versión?",
  cod="""const rangos = { "^1.4.2": "1.x.x", "~1.4.2": "1.4.x" };
console.log(rangos["~1.4.2"]);""", h="muestra qué acepta la tilde",
  pr=("El archivo que fija las versiones exactas es package-___.json (4 letras)", "lock"),
  pr2=("El símbolo que acepta solo parches es ___ (1 carácter)", "~"),
  ec="borrar package-lock.json y tener versiones distintas en cada PC", out="1.4.x"),
]
