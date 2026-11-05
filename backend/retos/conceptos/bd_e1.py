"""Bases de datos · Etapa 1: qué es una base de datos (casi todo teoría)."""
from ..generador import K

LISTA = [
K("Datos e información",
  d="los datos son hechos sueltos y la información son datos con sentido",
  u="entender por qué se guardan datos y cómo se convierten en información",
  mas="«Ana», «20» y «Lima» son datos sueltos. Cuando los juntas (Ana tiene 20 años y vive en Lima) se vuelven información útil. Una base de datos guarda datos de forma ordenada para poder convertirlos en información cuando los consultas.",
  k=["Un dato es un valor suelto, como un nombre o un número.", "La información son datos organizados que tienen sentido.", "Una base de datos guarda datos para obtener información."],
  sit="Tienes los valores sueltos «Ana», «20» y «Lima» y quieres saber cómo llamar a cada uno. ¿De qué hablas?",
  cod="""-- Tres datos sueltos
-- 'Ana'   20   'Lima'
-- Juntos y con sentido son información:
SELECT 'Ana' AS nombre, 20 AS edad, 'Lima' AS ciudad;""",
  h="junta tres datos sueltos en una fila con sentido",
  pr=("Los valores sueltos como «Ana» o «20» se llaman ___. (5 letras)", "datos"),
  pr2=("Los datos organizados con sentido forman la ___. (11 letras)", "información", "informacion"),
  ec="confundir un dato suelto con información completa"),
K("Base de datos",
  d="conjunto organizado de datos guardados para consultarlos",
  u="guardar mucha información de forma ordenada y segura",
  mas="Una base de datos es como un archivador digital muy bien organizado: guarda datos de usuarios, productos o pedidos y permite encontrarlos al instante. Casi toda aplicación web, de móvil o de juegos guarda su información en una.",
  k=["Una base de datos guarda información de forma organizada.", "Casi todas las aplicaciones usan una base de datos.", "Permite encontrar datos muy rápido."],
  sit="Quieres guardar los datos de miles de clientes de una tienda de forma ordenada para buscarlos al instante. ¿Qué usas?",
  cod="""-- Una base de datos agrupa varias tablas
CREATE DATABASE tienda;
USE tienda;
-- dentro irán las tablas: clientes, productos, pedidos...""",
  h="crea una base de datos llamada tienda y la selecciona",
  pr=("Un conjunto organizado de datos guardados es una ___ de datos. (4 letras)", "base"),
  pr2=("Las aplicaciones web guardan su información en una base de ___. (5 letras)", "datos"),
  ec="guardar toda la información en archivos sueltos sin orden"),
K("Para qué sirve una base de datos",
  d="herramienta para almacenar, consultar y proteger información",
  u="que muchas personas usen los mismos datos a la vez",
  mas="Cuando entras a una red social, el sistema consulta tu perfil, tus amigos y tus mensajes en una base de datos. Sirve para guardar sin perder, buscar rápido, compartir entre muchos usuarios y mantener los datos seguros y consistentes.",
  k=["Una base de datos permite buscar información rápidamente.", "Varias personas pueden usar los mismos datos a la vez.", "Protege los datos contra pérdidas y accesos no permitidos."],
  sit="Quieres que miles de usuarios consulten y modifiquen la misma información a la vez sin perderla. ¿Qué necesitas?",
  cod="""-- Ejemplo de uso real: buscar el perfil de un usuario
SELECT nombre, correo
FROM usuarios
WHERE id = 42;""",
  h="busca el nombre y el correo de un usuario concreto",
  pr=("Una base de datos permite que muchos ___ usen los mismos datos. (una palabra)", "usuarios", "usuarios a la vez"),
  pr2=("Además de guardar, una base de datos permite ___ datos rápido. (7 letras)", "buscar", "consultar"),
  ec="usar un archivo de texto para datos que cambian constantemente"),
K("Sistema gestor SGBD",
  d="programa que crea, administra y protege las bases de datos",
  u="gestionar los datos sin manipular archivos a mano",
  mas="El SGBD (o DBMS en inglés) es el programa intermediario: recibe tus peticiones, guarda y lee los datos del disco y controla quién puede acceder. MySQL, PostgreSQL y SQL Server son ejemplos. Tú nunca tocas los archivos directamente.",
  k=["El SGBD administra las bases de datos.", "MySQL y PostgreSQL son sistemas gestores.", "Las aplicaciones hablan con el SGBD, no con los archivos."],
  sit="Necesitas el programa que recibe tus consultas, lee el disco y controla los permisos. ¿Cómo se llama?",
  cod="""-- Le pides cosas al SGBD con SQL; él se encarga del resto
SHOW DATABASES;      -- lista las bases que gestiona
SELECT VERSION();    -- consulta qué gestor y versión es""",
  h="pregunta al gestor qué bases tiene y qué versión es",
  pr=("Las siglas de sistema gestor de bases de datos son ___. (4 letras)", "sgbd", "dbms"),
  pr2=("MySQL es un ejemplo de sistema ___ de bases de datos. (5 letras)", "gestor"),
  ec="creer que MySQL es la base de datos y no el gestor"),
K("Base de datos relacional",
  d="base de datos que guarda los datos en tablas relacionadas",
  u="organizar datos con estructura clara y conexiones entre ellos",
  mas="En el modelo relacional, la información está en tablas con filas y columnas, y las tablas se conectan mediante valores comunes (claves). Es el modelo más usado desde los años 70 y su lenguaje es SQL.",
  k=["Una base relacional guarda datos en tablas.", "Las tablas de una base relacional se conectan entre sí.", "El lenguaje de las bases relacionales es SQL."],
  sit="Quieres guardar clientes y pedidos en tablas conectadas entre sí. ¿Qué tipo de base de datos eliges?",
  cod="""-- Dos tablas conectadas: cada pedido apunta a un cliente
-- clientes(id, nombre)
-- pedidos(id, cliente_id, total)
SELECT c.nombre, p.total
FROM clientes c
JOIN pedidos p ON p.cliente_id = c.id;""",
  h="une la tabla de clientes con la de pedidos mediante un valor común",
  pr=("Una base que guarda datos en tablas conectadas es una base ___. (10 letras)", "relacional"),
  pr2=("El lenguaje de las bases relacionales es ___. (3 letras)", "sql"),
  ec="guardar toda la información en una única tabla gigante"),
K("Tabla",
  d="estructura de filas y columnas que guarda un tipo de datos",
  u="agrupar datos del mismo tema, como clientes o productos",
  mas="Una tabla representa un tipo de cosa: usuarios, productos, pedidos. Sus columnas definen qué datos se guardan de cada cosa (nombre, precio) y sus filas son cada elemento concreto. Una base de datos suele tener muchas tablas.",
  k=["Una tabla guarda datos del mismo tema.", "Una tabla tiene columnas y filas.", "Una base de datos puede tener muchas tablas."],
  sit="Quieres un espacio de la base de datos para todos los productos de tu tienda. ¿Qué creas?",
  cod="""-- Una tabla para los productos
CREATE TABLE productos (
  id INT,
  nombre VARCHAR(50),
  precio DECIMAL(8,2)
);""",
  h="define una tabla de productos con id, nombre y precio",
  pr=("Una tabla está formada por filas y ___. (8 letras)", "columnas"),
  pr2=("Escribe el comando para crear una tabla (dos palabras: CREATE ___).", "table"),
  ec="mezclar datos de temas distintos en la misma tabla"),
K("Fila o registro",
  d="cada elemento concreto guardado en una tabla",
  u="representar un cliente, un producto o un pedido en particular",
  mas="Cada fila de la tabla productos es un producto distinto: la fila 1 puede ser «Café», la fila 2 «Té». También se llama registro o tupla. Cada fila tiene un valor en cada columna.",
  k=["Una fila (o registro) representa un elemento concreto.", "Cada fila tiene un valor por cada columna.", "Insertar datos significa añadir filas."],
  sit="Quieres hablar de un producto concreto, por ejemplo el café, dentro de la tabla. ¿Qué parte de la tabla es?",
  cod="""-- Cada INSERT añade UNA fila (un registro)
INSERT INTO productos VALUES (1, 'Café', 4.50);
INSERT INTO productos VALUES (2, 'Té',   3.20);""",
  h="añade dos filas, una por cada producto",
  pr=("Otro nombre de «fila» en una tabla es ___. (8 letras)", "registro"),
  pr2=("Añadir datos a una tabla significa añadir ___. (5 letras)", "filas", "registros"),
  ec="confundir una fila con una columna"),
K("Columna o campo",
  d="característica que se guarda de cada elemento de la tabla",
  u="definir qué datos tiene cada registro",
  mas="Las columnas son los datos que se guardan de cada cosa: id, nombre, precio. Cada columna tiene un nombre y un tipo de dato (número, texto, fecha). Todas las filas comparten las mismas columnas.",
  k=["Una columna (o campo) define un tipo de dato de la tabla.", "Todas las filas comparten las mismas columnas.", "Cada columna tiene un nombre y un tipo de dato."],
  sit="Quieres hablar del dato «precio» que tienen todos los productos. ¿Qué parte de la tabla es?",
  cod="""-- Cada línea dentro del paréntesis es una columna
CREATE TABLE clientes (
  id      INT,           -- columna de números
  nombre  VARCHAR(40),   -- columna de texto
  alta    DATE           -- columna de fechas
);""",
  h="define tres columnas con distintos tipos de dato",
  pr=("Otro nombre de «columna» en una tabla es ___. (5 letras)", "campo"),
  pr2=("Cada columna tiene un nombre y un ___ de dato. (4 letras)", "tipo"),
  ec="añadir una columna distinta en cada fila"),
K("Clave primaria",
  d="columna que identifica de forma única cada fila",
  u="distinguir un registro de todos los demás",
  mas="El id es la clave primaria típica: no se repite ni puede estar vacío. Gracias a ella puedes decir «el cliente 7» sin dudas, aunque haya dos personas llamadas Ana. Cada tabla debería tener una.",
  k=["La clave primaria identifica cada fila de forma única.", "La clave primaria no puede repetirse ni estar vacía.", "Cada tabla debería tener una clave primaria."],
  sit="Hay dos clientes llamados Ana y quieres distinguirlos con un valor único. ¿Qué usas?",
  cod="""CREATE TABLE clientes (
  id INT PRIMARY KEY,      -- clave primaria: única y obligatoria
  nombre VARCHAR(40)
);
INSERT INTO clientes VALUES (1, 'Ana');
INSERT INTO clientes VALUES (2, 'Ana');   -- mismo nombre, distinto id""",
  h="distingue a dos clientes con el mismo nombre gracias a su clave primaria",
  pr=("La columna que identifica cada fila se llama clave ___. (8 letras)", "primaria"),
  pr2=("La clave primaria no puede ___. (7 letras: repetirse)", "repetirse"),
  ec="usar el nombre como clave primaria",
  err=("CREATE TABLE clientes (\n  id INT PRIMARY KEY,\n  nombre VARCHAR(40)\n);\nINSERT INTO clientes VALUES (1, 'Ana');\nINSERT INTO clientes VALUES (1, 'Luis');", 6, "El id 1 ya existe: una clave primaria no puede repetirse.")),
K("CRUD",
  d="las cuatro operaciones básicas sobre los datos",
  u="describir todo lo que una aplicación hace con la información",
  mas="CRUD son las siglas de Create (crear), Read (leer), Update (actualizar) y Delete (borrar). En SQL equivalen a INSERT, SELECT, UPDATE y DELETE. Casi todo lo que hace una app, desde registrar un usuario hasta borrar una foto, es una de estas cuatro.",
  k=["CRUD significa crear, leer, actualizar y borrar.", "INSERT crea, SELECT lee, UPDATE actualiza y DELETE borra.", "Casi toda aplicación se reduce a operaciones CRUD."],
  sit="Quieres nombrar las cuatro operaciones básicas: crear, leer, actualizar y borrar datos. ¿Qué sigla usas?",
  cod="""INSERT INTO tareas VALUES (1, 'Estudiar');     -- Create
SELECT * FROM tareas;                          -- Read
UPDATE tareas SET titulo = 'Repasar' WHERE id = 1;  -- Update
DELETE FROM tareas WHERE id = 1;               -- Delete""",
  h="recorre crear, leer, actualizar y borrar sobre una tabla de tareas",
  pr=("La R de CRUD significa ___ (leer en inglés). (4 letras)", "read"),
  pr2=("La D de CRUD significa ___ (borrar en inglés). (6 letras)", "delete"),
  ec="olvidar la cláusula WHERE al actualizar o borrar"),
K("SQL",
  d="lenguaje estándar para hablar con las bases de datos relacionales",
  u="pedir, añadir, modificar y borrar datos",
  mas="SQL significa Structured Query Language (lenguaje de consulta estructurado). Se parece al inglés: SELECT nombre FROM clientes. Con pocas palabras clave y mucha práctica puedes consultar millones de filas. Sirve en MySQL, PostgreSQL, SQL Server y muchos más.",
  k=["SQL significa Structured Query Language.", "SQL sirve para consultar y modificar bases relacionales.", "SQL se parece al inglés en su forma de escribirse."],
  sit="Quieres un lenguaje con el que pedir datos a una base relacional con frases casi en inglés. ¿Qué usas?",
  cod="""-- SQL se lee casi como inglés
SELECT nombre, edad     -- qué quiero ver
FROM alumnos            -- de qué tabla
WHERE edad >= 18;       -- con qué condición""",
  h="pide el nombre y la edad de los alumnos mayores de edad",
  pr=("SQL significa Structured ___ Language. (5 letras)", "query"),
  pr2=("La palabra de SQL para consultar datos es ___. (6 letras)", "select"),
  ec="creer que SQL es un lenguaje de programación general"),
K("Cliente y servidor de BD",
  d="modelo donde una aplicación pide datos a un servidor de bases de datos",
  u="separar la aplicación de la base que guarda los datos",
  mas="La base de datos vive en un servidor y las aplicaciones (clientes) se conectan por la red con usuario y contraseña. Así, muchas apps comparten la misma información y puedes mejorar el servidor sin tocar las aplicaciones. Cada conexión necesita servidor, puerto, usuario y contraseña.",
  k=["Las aplicaciones se conectan al servidor de la base de datos.", "Para conectarse hace falta servidor, puerto, usuario y contraseña.", "Muchas aplicaciones pueden usar la misma base."],
  sit="Tu aplicación está en un ordenador y los datos en otro, al que se conecta por la red. ¿Qué modelo usas?",
  cod="""-- Datos que necesita una conexión (ejemplo ilustrativo)
-- servidor:   127.0.0.1
-- puerto:     3306
-- usuario:    root
-- base:       tienda
SELECT 'conectado' AS estado;""",
  h="lista los datos necesarios para conectarse y confirma la conexión",
  pr=("El puerto habitual de MySQL es ___. (4 números)", "3306"),
  pr2=("Para conectarse a una base hace falta usuario y ___. (10 letras)", "contraseña", "contrasena"),
  ec="guardar la contraseña de la base dentro del código visible"),
K("MySQL",
  d="gestor de bases de datos relacionales gratuito y muy popular",
  u="alojar los datos de sitios web y aplicaciones",
  mas="MySQL se creó en 1995 y hoy lo usan WordPress, Facebook (en parte) y millones de sitios. MariaDB es una alternativa casi idéntica. Es gratuito, rápido y se instala fácil, por eso es ideal para aprender.",
  k=["MySQL es un gestor de bases de datos relacionales.", "MySQL es gratuito y muy popular.", "MariaDB es una alternativa casi idéntica a MySQL."],
  sit="Buscas un gestor gratuito, rápido y fácil de instalar para aprender SQL. ¿Cuál eliges?",
  cod="""-- Comandos habituales de MySQL
SHOW DATABASES;          -- ver las bases
CREATE DATABASE escuela; -- crear una base
USE escuela;             -- elegirla
SHOW TABLES;             -- ver sus tablas""",
  h="muestra, crea y selecciona bases de datos en MySQL",
  pr=("Una alternativa casi idéntica a MySQL es ___. (7 letras)", "mariadb"),
  pr2=("MySQL es gratuito y muy ___. (8 letras: pista, lo usa mucha gente)", "popular"),
  ec="confundir MySQL con el lenguaje SQL"),
K("XAMPP y Workbench",
  d="paquete que instala MySQL y herramienta visual para gestionarlo",
  u="tener un servidor de bases de datos en tu propio ordenador",
  mas="XAMPP instala en tu ordenador Apache, PHP y MySQL con un solo clic. MySQL Workbench es el programa gráfico donde escribes SQL, ves las tablas y diseñas esquemas. Primero enciendes MySQL en XAMPP y luego te conectas desde Workbench.",
  k=["XAMPP instala un servidor MySQL en tu ordenador.", "Workbench es una herramienta visual para trabajar con MySQL.", "Hay que encender MySQL en XAMPP antes de conectarse."],
  sit="Quieres un servidor MySQL en tu propio ordenador y un programa visual para manejarlo. ¿Qué instalas?",
  cod="""-- 1) Abre XAMPP y pulsa Start junto a MySQL
-- 2) Abre MySQL Workbench y conéctate a 127.0.0.1
-- 3) Prueba que todo funciona:
SELECT 'Hola, MySQL' AS saludo;""",
  h="confirma que la conexión con el servidor local funciona",
  pr=("El programa visual para trabajar con MySQL se llama MySQL ___. (9 letras)", "workbench"),
  pr2=("Antes de conectarte debes encender MySQL en ___. (5 letras)", "xampp"),
  ec="intentar conectarse sin encender el servidor MySQL"),
K("Bases de datos NoSQL",
  d="bases que no usan tablas y se adaptan a datos flexibles",
  u="guardar datos sin estructura fija o con enormes volúmenes",
  mas="NoSQL agrupa varios tipos: documentos (MongoDB), clave-valor (Redis), columnas (Cassandra) y grafos (Neo4j). Son útiles cuando los datos cambian mucho de forma o se necesita muchísima velocidad. No sustituyen a las relacionales: se eligen según el caso.",
  k=["NoSQL agrupa bases de datos que no usan tablas relacionales.", "MongoDB guarda documentos y Redis guarda pares clave-valor.", "NoSQL no sustituye a las bases relacionales."],
  sit="Tus datos cambian de forma constantemente y no encajan en tablas fijas. ¿Qué familia de bases consideras?",
  cod="""-- Un documento NoSQL (MongoDB) se parece a un objeto JSON:
-- { "nombre": "Ana", "intereses": ["web", "datos"], "edad": 20 }
-- Cada documento puede tener campos distintos
SELECT 'ejemplo conceptual' AS nota;""",
  h="muestra cómo se vería un documento flexible de una base NoSQL",
  pr=("MongoDB es una base de datos de ___. (10 letras: documentos)", "documentos"),
  pr2=("Redis guarda pares clave-___. (5 letras)", "valor"),
  ec="usar NoSQL por moda sin necesitarlo"),
K("Hoja de cálculo y base de datos",
  d="comparación entre guardar datos en Excel o en una base",
  u="elegir la herramienta adecuada para cada volumen de datos",
  mas="Una hoja de cálculo es excelente para pocos datos y un solo usuario. Cuando hay miles de filas, varias personas editando a la vez, relaciones entre tablas y exigencias de seguridad, necesitas una base de datos. Una base valida datos y evita duplicados con reglas.",
  k=["Una hoja de cálculo sirve bien para pocos datos y un usuario.", "Una base de datos soporta muchos usuarios y muchísimos datos.", "Una base de datos permite reglas para evitar datos erróneos."],
  sit="Tu hoja de cálculo ya tiene 200 000 filas y diez personas la editan a la vez. ¿Qué te conviene usar?",
  cod="""-- Una base de datos puede impedir datos duplicados
CREATE TABLE socios (
  dni VARCHAR(9) PRIMARY KEY,   -- dos socios no pueden tener el mismo dni
  nombre VARCHAR(40) NOT NULL   -- el nombre no puede quedar vacío
);""",
  h="impone reglas que una hoja de cálculo no puede garantizar",
  pr=("Para pocos datos y un solo usuario basta una hoja de ___. (7 letras)", "cálculo", "calculo"),
  pr2=("Para muchos usuarios a la vez conviene una base de ___. (5 letras)", "datos"),
  ec="usar una hoja de cálculo para una aplicación con muchos usuarios"),
K("Seguridad de los datos",
  d="medidas que protegen la información de accesos no permitidos",
  u="evitar robos, filtraciones y cambios indebidos",
  mas="Incluye contraseñas fuertes, usuarios con permisos mínimos, conexiones cifradas y no guardar contraseñas en texto plano. La aplicación nunca debe usar el usuario administrador. Una filtración de datos puede dañar a muchas personas.",
  k=["Cada usuario de la base debe tener solo los permisos necesarios.", "Las contraseñas de los usuarios nunca deben guardarse en texto plano.", "Las conexiones deben cifrarse cuando viajan por la red."],
  sit="Quieres que una aplicación solo pueda leer datos y no borrarlos. ¿Qué principio aplicas?",
  cod="""-- Principio de mínimos permisos: la app solo puede leer y añadir
CREATE USER 'app'@'localhost' IDENTIFIED BY 'una-clave-larga';
GRANT SELECT, INSERT ON tienda.* TO 'app'@'localhost';
-- (no se le da DELETE ni DROP)""",
  h="crea un usuario que solo puede consultar e insertar, no borrar",
  pr=("Cada usuario debe tener solo los permisos ___. (10 letras: necesarios)", "necesarios"),
  pr2=("Las contraseñas no deben guardarse en texto ___. (5 letras)", "plano"),
  ec="usar el usuario administrador (root) en la aplicación"),
K("Copias de seguridad",
  d="copias de los datos que permiten recuperarlos si algo falla",
  u="no perder información por errores, fallos o ataques",
  mas="Los discos fallan, las personas se equivocan y existen virus que cifran datos. Una copia de seguridad (backup) guardada en otro lugar te permite recuperarlo todo. Se programan automáticamente y se comprueba de vez en cuando que se pueden restaurar.",
  k=["Una copia de seguridad permite recuperar los datos tras un fallo.", "La copia debe guardarse en un lugar distinto al original.", "Conviene comprobar que la copia realmente se puede restaurar."],
  sit="Un error borra una tabla entera y quieres recuperarla tal como estaba ayer. ¿Qué necesitas?",
  cod="""-- Copia de seguridad desde la terminal (no es SQL):
--   mysqldump -u root -p tienda > copia_tienda.sql
-- Restaurarla:
--   mysql -u root -p tienda < copia_tienda.sql
SELECT 'haz copias y pruébalas' AS consejo;""",
  h="muestra cómo copiar y restaurar una base con mysqldump",
  pr=("En inglés, una copia de seguridad se llama ___. (6 letras)", "backup"),
  pr2=("Una copia de seguridad debe guardarse en un lugar ___ al original. (7 letras)", "distinto", "diferente"),
  ec="hacer copias pero no comprobar nunca que se pueden restaurar"),
K("Integridad de los datos",
  d="garantía de que los datos son correctos y coherentes",
  u="evitar datos incompletos, duplicados o contradictorios",
  mas="La base de datos puede imponer reglas: campos obligatorios (NOT NULL), valores únicos (UNIQUE), claves primarias y relaciones válidas (claves foráneas). Así un pedido no puede apuntar a un cliente que no existe y un correo no se registra dos veces.",
  k=["La integridad evita datos incorrectos o contradictorios.", "NOT NULL obliga a que un campo tenga valor.", "UNIQUE impide valores repetidos."],
  sit="Quieres impedir que dos usuarios se registren con el mismo correo. ¿Qué garantizas?",
  cod="""CREATE TABLE usuarios (
  id INT PRIMARY KEY,
  correo VARCHAR(80) NOT NULL UNIQUE,   -- obligatorio y sin repetir
  edad INT CHECK (edad >= 0)            -- no admite edades negativas
);""",
  h="impone correo obligatorio y único, y edad no negativa",
  pr=("La restricción que impide valores repetidos es ___. (6 letras)", "unique"),
  pr2=("La restricción que obliga a tener valor es NOT ___. (4 letras)", "null"),
  ec="confiar en que la aplicación valida todo y no poner reglas en la base"),
K("Cómo practicar bases de datos",
  d="hábito de crear tablas y consultas propias a diario",
  u="aprender SQL escribiendo consultas reales",
  mas="Crea una base pequeña sobre algo que te guste (tus películas, una tienda, un torneo) y hazte preguntas: ¿cuántas?, ¿cuáles son las más caras? Responde con SQL. Practicar con tus propias preguntas fija mucho mejor que copiar ejemplos.",
  k=["Practicar con datos que te interesan ayuda a aprender SQL.", "Hacerse preguntas y responderlas con consultas es un buen método.", "Practicar un poco cada día funciona mejor que mucho de golpe."],
  sit="Quieres aprender SQL de forma entretenida usando tus propios datos. ¿Qué haces?",
  cod="""-- Reto: crea tu mini base de películas y respóndele preguntas
CREATE TABLE peliculas (id INT PRIMARY KEY, titulo VARCHAR(60), anio INT);
INSERT INTO peliculas VALUES (1, 'Coco', 2017), (2, 'Soul', 2020);
SELECT titulo FROM peliculas WHERE anio > 2018;""",
  h="crea una pequeña tabla de películas y pregunta cuáles son posteriores a 2018",
  pr=("SQL se aprende practicando con tus propias ___. (9 letras: consultas)", "consultas", "preguntas"),
  pr2=("Practicar un poco cada ___ es mejor que mucho de golpe. (3 letras)", "día", "dia"),
  ec="leer sobre SQL sin escribir nunca una consulta"),
]
