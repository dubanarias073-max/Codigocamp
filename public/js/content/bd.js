// Curso: bases de datos de todo tipo. Son ejemplos para leer y copiar en cada herramienta.
// (SQL se puede practicar en MySQL Workbench con tu XAMPP.)
const r = String.raw;

export const BD = [
{ t: "¿Qué es una base de datos? Mapa de tipos",
  d: "Una base de datos guarda información organizada para consultarla, modificarla y protegerla. Hay muchos tipos y cada uno resuelve mejor un problema distinto. Este curso recorre los principales.",
  p: ["Un SGBD es el programa que gestiona la base de datos (MySQL, MongoDB…)", "Operaciones básicas: crear, leer, actualizar y borrar (CRUD)", "No existe «la mejor»: se elige según los datos y el uso", "En la última lección verás cómo decidir"],
  c: r`Tipo               Ejemplos                    Ideal para
-----------------  --------------------------  -----------------------------
Relacional (SQL)   MySQL, PostgreSQL, SQLite   Usuarios, pedidos, finanzas
Documental         MongoDB, Firestore          Catálogos, contenido flexible
Clave-valor        Redis, DynamoDB             Caché, sesiones, contadores
Columnar           Cassandra, HBase            Mucha escritura, escala enorme
Grafos             Neo4j, Amazon Neptune       Redes sociales, recomendaciones
Series temporales  InfluxDB, TimescaleDB       Sensores, métricas, bolsa
Vectorial          pgvector, Pinecone          Búsqueda por similitud (IA)` },

{ t: "Relacionales: tablas y SQL básico",
  d: "Las bases de datos relacionales guardan los datos en tablas con filas y columnas, y usan el lenguaje SQL. Cada tabla tiene una clave primaria que identifica cada fila. Es el tipo más usado y el que ya tienes en tu XAMPP (MySQL).",
  p: ["CREATE TABLE define la estructura", "INSERT añade filas; UPDATE las modifica; DELETE las borra", "PRIMARY KEY identifica cada fila; UNIQUE evita repetidos", "Cada columna tiene un tipo: INT, VARCHAR, DATE…", "Practica en MySQL Workbench"],
  c: r`CREATE TABLE estudiantes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  email VARCHAR(100) UNIQUE,
  edad INT
);

INSERT INTO estudiantes (nombre, email, edad)
VALUES ('Ana', 'ana@correo.com', 20),
       ('Luis', 'luis@correo.com', 22);

UPDATE estudiantes SET edad = 21 WHERE nombre = 'Ana';

DELETE FROM estudiantes WHERE nombre = 'Luis';` },

{ t: "SQL: consultar datos",
  d: "SELECT es la instrucción más importante: elige qué columnas ver, con qué condición, en qué orden y cuántas filas. Las funciones de agregación calculan totales y promedios.",
  p: ["WHERE filtra filas; ORDER BY ordena; LIMIT recorta", "COUNT, SUM, AVG, MIN y MAX resumen datos", "GROUP BY agrupa antes de resumir", "LIKE busca por patrón: LIKE 'A%'"],
  c: r`SELECT nombre, edad
FROM estudiantes
WHERE edad >= 18 AND nombre LIKE 'A%'
ORDER BY edad DESC
LIMIT 10;

SELECT COUNT(*) AS total, AVG(edad) AS edad_media
FROM estudiantes;

SELECT edad, COUNT(*) AS cuantos
FROM estudiantes
GROUP BY edad
HAVING COUNT(*) > 1;` },

{ t: "SQL: relaciones y JOIN",
  d: "Lo potente de las bases relacionales es conectar tablas. Una clave foránea en una tabla apunta a la clave primaria de otra. Con JOIN combinas los datos de ambas en una sola consulta.",
  p: ["Relaciones: uno a uno, uno a muchos y muchos a muchos", "FOREIGN KEY garantiza que la referencia exista", "INNER JOIN: solo filas que coinciden en ambas tablas", "LEFT JOIN: todas las de la izquierda, aunque no coincidan"],
  c: r`CREATE TABLE cursos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(80) NOT NULL
);

CREATE TABLE inscripciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  estudiante_id INT NOT NULL,
  curso_id INT NOT NULL,
  FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
  FOREIGN KEY (curso_id) REFERENCES cursos(id)
);

SELECT e.nombre, c.titulo
FROM inscripciones i
INNER JOIN estudiantes e ON e.id = i.estudiante_id
INNER JOIN cursos c ON c.id = i.curso_id;

-- Todos los estudiantes, tengan o no curso
SELECT e.nombre, c.titulo
FROM estudiantes e
LEFT JOIN inscripciones i ON i.estudiante_id = e.id
LEFT JOIN cursos c ON c.id = i.curso_id;` },

{ t: "Diseño: normalización, índices y transacciones",
  d: "Un buen diseño evita datos repetidos y errores. La normalización divide la información en tablas lógicas. Los índices aceleran las búsquedas, y las transacciones garantizan que un conjunto de operaciones se complete entero o no se haga.",
  p: ["1FN: cada celda guarda un solo valor", "2FN y 3FN: cada dato depende solo de su clave", "Un índice acelera lecturas pero hace más lentas las escrituras", "ACID: Atomicidad, Consistencia, Aislamiento y Durabilidad"],
  c: r`-- Índice para buscar rápido por email
CREATE INDEX idx_estudiantes_email ON estudiantes (email);

-- Transacción: transferir saldo entre dos cuentas
START TRANSACTION;
UPDATE cuentas SET saldo = saldo - 100 WHERE id = 1;
UPDATE cuentas SET saldo = saldo + 100 WHERE id = 2;
COMMIT;      -- confirma ambos cambios
-- ROLLBACK; -- si algo falla, deshace todo` },

{ t: "Documentales: MongoDB",
  d: "Las bases documentales guardan documentos con forma de JSON, sin esquema fijo. Cada documento puede tener campos distintos y contener listas u objetos anidados. MongoDB es la más popular.",
  p: ["Colecciones (como tablas) con documentos (como filas)", "Flexible: añade campos sin modificar una estructura", "Datos anidados: no siempre necesitas JOIN", "Consultas con operadores: $gte, $in, $set…"],
  c: r`// Insertar
db.estudiantes.insertOne({
  nombre: "Ana",
  edad: 20,
  cursos: ["HTML", "CSS"],
  direccion: { ciudad: "Madrid" }
})

// Buscar
db.estudiantes.find({ edad: { $gte: 18 } })

// Actualizar
db.estudiantes.updateOne({ nombre: "Ana" }, { $set: { edad: 21 } })

// Borrar
db.estudiantes.deleteOne({ nombre: "Ana" })` },

{ t: "Clave-valor: Redis",
  d: "Una base clave-valor es como un enorme diccionario: guardas un valor bajo una clave y lo recuperas al instante. Redis trabaja en memoria, por eso es rapidísimo. Se usa para caché, sesiones y contadores.",
  p: ["Operaciones muy simples: SET, GET, DEL", "EX / EXPIRE hacen que un dato caduque solo", "INCR cuenta de forma segura", "No es para consultas complejas"],
  c: r`SET usuario:1:nombre "Ana"
GET usuario:1:nombre

# Sesión que caduca en 1 hora
SET sesion:abc123 "datos" EX 3600
TTL sesion:abc123

# Contador de visitas
INCR visitas
INCR visitas
GET visitas` },

{ t: "Columnares: Cassandra",
  d: "Las bases de columnas anchas (como Cassandra) están diseñadas para escribir enormes cantidades de datos repartidos en muchos servidores. Se modelan según las consultas que harás, y no según las relaciones.",
  p: ["Escalan añadiendo servidores", "La clave de partición decide en qué servidor va cada dato", "La clave de clustering ordena los datos dentro de la partición", "Usan CQL, un lenguaje parecido a SQL pero sin JOIN"],
  c: r`CREATE KEYSPACE tienda
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE tienda;

CREATE TABLE pedidos_por_cliente (
  cliente_id uuid,
  fecha timestamp,
  total decimal,
  PRIMARY KEY (cliente_id, fecha)
) WITH CLUSTERING ORDER BY (fecha DESC);

SELECT * FROM pedidos_por_cliente
WHERE cliente_id = 123e4567-e89b-12d3-a456-426614174000
LIMIT 10;` },

{ t: "Grafos: Neo4j",
  d: "Las bases de grafos guardan nodos (cosas) y relaciones (conexiones entre ellas). Son perfectas cuando lo importante son las conexiones: redes sociales, recomendaciones, rutas o detección de fraude.",
  p: ["Nodo: una entidad con etiquetas y propiedades", "Relación: conexión con dirección y tipo", "Recorrer conexiones es muy rápido, sin JOIN costosos", "Neo4j usa el lenguaje Cypher"],
  c: r`CREATE (ana:Persona {nombre: "Ana"})
CREATE (luis:Persona {nombre: "Luis"})
CREATE (marta:Persona {nombre: "Marta"})
CREATE (ana)-[:AMIGA_DE]->(luis)
CREATE (luis)-[:AMIGO_DE]->(marta)

// Amigos de Ana
MATCH (p:Persona {nombre: "Ana"})-[:AMIGA_DE]->(amigo)
RETURN amigo.nombre

// Amigos de amigos (recomendaciones)
MATCH (p:Persona {nombre: "Ana"})-[*2]->(otro)
RETURN DISTINCT otro.nombre` },

{ t: "Series temporales y vectoriales",
  d: "Las bases de series temporales están optimizadas para datos con fecha y hora (sensores, métricas, bolsa). Las vectoriales guardan embeddings, listas de números que representan el significado de un texto o imagen, y buscan por similitud; son clave en aplicaciones de IA.",
  p: ["Series temporales: InfluxDB, TimescaleDB", "Se agrupan datos por intervalos de tiempo", "Vectoriales: pgvector, Pinecone, Qdrant", "Buscan «lo más parecido», no coincidencias exactas"],
  c: r`-- TimescaleDB: temperatura media por hora
SELECT time_bucket('1 hour', hora) AS intervalo,
       AVG(temperatura) AS media
FROM lecturas
GROUP BY intervalo
ORDER BY intervalo;

-- pgvector: los 3 textos más parecidos a un vector
CREATE EXTENSION vector;
CREATE TABLE documentos (id SERIAL PRIMARY KEY, texto TEXT, embedding vector(3));
INSERT INTO documentos (texto, embedding) VALUES ('hola', '[0.1, 0.9, 0.2]');
SELECT texto
FROM documentos
ORDER BY embedding <-> '[0.1, 0.8, 0.3]'
LIMIT 3;` },

{ t: "¿Cuál elegir? Guía de decisión",
  d: "Elegir una base de datos depende de cómo son tus datos y qué harás con ellos. En muchos proyectos reales se combinan varias: por ejemplo, MySQL para usuarios y pedidos, y Redis como caché.",
  p: ["Si dudas, empieza con una relacional", "Cambia solo cuando tengas una necesidad clara", "Combinar bases de datos es normal (persistencia políglota)", "Pregúntale al tutor por tu caso concreto"],
  c: r`¿Datos con estructura clara y relaciones?        -> Relacional (MySQL, PostgreSQL)
¿Datos flexibles que cambian de forma?           -> Documental (MongoDB)
¿Necesitas velocidad extrema o caché?            -> Clave-valor (Redis)
¿Millones de escrituras y muchos servidores?     -> Columnar (Cassandra)
¿Lo importante son las conexiones?               -> Grafos (Neo4j)
¿Datos que llegan con fecha y hora?              -> Series temporales (InfluxDB)
¿Búsqueda por significado o similitud (IA)?      -> Vectorial (pgvector)` },
];
