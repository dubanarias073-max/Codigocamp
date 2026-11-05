// Lecciones de SQL. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Consultas básicas", t:"Leer datos con SELECT", x:"SQL consulta bases de datos. Aquí practicas con la tabla alumnos(id, nombre, curso, nota).",
    p:["SELECT elige columnas", "FROM indica la tabla", "* significa todas las columnas"],
    c:`SELECT * FROM alumnos;` },
  { m:"Consultas básicas", t:"Filtrar y ordenar", x:"WHERE filtra filas y ORDER BY las ordena.",
    p:["WHERE nota >= 7", "ORDER BY nota DESC: de mayor a menor", "LIMIT 3 devuelve solo 3 filas"],
    c:`SELECT nombre, nota
FROM alumnos
WHERE nota >= 7
ORDER BY nota DESC;` },
  { m:"Resumir datos", t:"Contar y promediar", x:"Las funciones de agregación resumen muchas filas en un solo dato.",
    p:["COUNT(*) cuenta filas", "AVG calcula el promedio", "AS le pone nombre al resultado"],
    c:`SELECT COUNT(*) AS total, AVG(nota) AS promedio
FROM alumnos;` },
  { m:"Resumir datos", t:"Agrupar con GROUP BY", x:"GROUP BY junta las filas que comparten un valor y calcula un resumen de cada grupo.",
    p:["Una fila por cada curso", "Combina GROUP BY con COUNT o AVG", "HAVING filtra grupos"],
    c:`SELECT curso, COUNT(*) AS alumnos, AVG(nota) AS promedio
FROM alumnos
GROUP BY curso;` },
  { m:"Modificar datos", t:"Insertar y modificar", x:"INSERT añade filas y UPDATE cambia las que ya existen. Aquí los cambios solo duran mientras se ejecuta el código.",
    p:["INSERT INTO tabla (columnas) VALUES (...)", "UPDATE ... SET ... WHERE ...", "Sin WHERE se modifican todas las filas"],
    c:`INSERT INTO alumnos (nombre, curso, nota)
VALUES ("Eva", "SQL", 9.5);

UPDATE alumnos SET nota = 7 WHERE nombre = "Sara";

SELECT * FROM alumnos;` },
  { m:"Consultas avanzadas", t:"Buscar con LIKE", x:"LIKE busca textos que siguen un patrón.",
    p:["% es cualquier cantidad de letras", "_ es exactamente una letra", "No distingue mayúsculas en SQLite"],
    c:`SELECT nombre, curso
FROM alumnos
WHERE nombre LIKE "M%" OR curso LIKE "%y%";` },
  { m:"Consultas avanzadas", t:"MAX, MIN y subconsultas", x:"Una subconsulta es una consulta dentro de otra. Sirve para comparar contra un resultado calculado.",
    p:["MAX y MIN dan el mayor y el menor", "La subconsulta va entre paréntesis", "Se ejecuta primero la de dentro"],
    c:`SELECT nombre, nota
FROM alumnos
WHERE nota = (SELECT MAX(nota) FROM alumnos);` },
  { m:"Tablas", t:"Crear tablas", x:"CREATE TABLE define una tabla nueva con sus columnas y sus tipos.",
    p:["PRIMARY KEY identifica cada fila", "NOT NULL obliga a dar un valor", "Tipos comunes: INTEGER, TEXT, REAL"],
    c:`CREATE TABLE cursos (
  id INTEGER PRIMARY KEY,
  nombre TEXT NOT NULL
);
INSERT INTO cursos (nombre) VALUES ("HTML"), ("Python");
SELECT * FROM cursos;` },
  { m:"Tablas", t:"Unir tablas con JOIN", x:"JOIN combina filas de dos tablas que comparten un dato.",
    p:["ON indica la condición de unión", "Se pueden usar alias: alumnos a", "Es la base de las bases de datos relacionales"],
    c:`CREATE TABLE cursos (nombre TEXT, horas INTEGER);
INSERT INTO cursos VALUES ("HTML", 20), ("Python", 40), ("SQL", 15);

SELECT a.nombre, c.horas
FROM alumnos a
JOIN cursos c ON c.nombre = a.curso;` },
  { m:"Funciones", t:"Funciones de texto", x:"Las funciones de texto transforman cadenas: mayúsculas, longitud, partes de un texto y unión de valores.",
    p:["UPPER y LOWER cambian mayúsculas", "LENGTH cuenta caracteres", "|| une textos (CONCAT en MySQL)"],
    c:"SELECT UPPER(nombre) AS mayus,\n       LENGTH(nombre) AS letras,\n       nombre || \" - \" || curso AS ficha,\n       SUBSTR(nombre, 1, 3) AS inicio\nFROM alumnos;",
    r:"Muestra los nombres en minúsculas con LOWER." },
  { m:"Funciones", t:"Números y fechas", x:"ROUND redondea, ABS da el valor absoluto y las funciones de fecha trabajan con días y horas.",
    p:["ROUND(x, 1) deja un decimal", "ABS quita el signo", "date(\"now\") da la fecha de hoy"],
    c:"SELECT nombre,\n       ROUND(nota, 0) AS redondeada,\n       ABS(nota - 7) AS distancia_a_7,\n       date(\"2026-01-31\", \"+1 day\") AS manana\nFROM alumnos;",
    r:"Calcula la nota sobre 100 con nota * 10." },
  { m:"Funciones", t:"CASE: condiciones dentro de la consulta", x:"CASE devuelve un valor distinto según la condición, como un if dentro de SQL.",
    p:["CASE WHEN condición THEN valor", "ELSE cubre el resto de casos", "Siempre termina con END"],
    c:"SELECT nombre, nota,\n  CASE\n    WHEN nota >= 9 THEN \"Excelente\"\n    WHEN nota >= 7 THEN \"Bien\"\n    WHEN nota >= 6 THEN \"Regular\"\n    ELSE \"A mejorar\"\n  END AS nivel\nFROM alumnos\nORDER BY nota DESC;",
    r:"Añade una categoría \"Perfecto\" para notas de 10.",
    e:"Olvidar END o ELSE: sin ELSE los casos sobrantes devuelven NULL." },
  { m:"Subconsultas", t:"Subconsultas en WHERE", x:"Una subconsulta es una consulta dentro de otra. Sirve para comparar con un valor calculado.",
    p:["Va entre paréntesis", "Puede devolver un valor o una lista", "IN comprueba si un valor está en la lista"],
    c:"SELECT nombre, nota\nFROM alumnos\nWHERE nota > (SELECT AVG(nota) FROM alumnos);\n\nSELECT nombre, curso\nFROM alumnos\nWHERE curso IN (SELECT curso FROM alumnos WHERE nota >= 9);",
    r:"Muestra los alumnos con la nota más baja usando MIN en una subconsulta." },
  { m:"Subconsultas", t:"Consultas con nombre: WITH", x:"WITH crea una consulta temporal con nombre (CTE) que hace más legible una consulta larga.",
    p:["WITH nombre AS (consulta)", "Se usa después como si fuera una tabla", "Se pueden encadenar varias"],
    c:"WITH resumen AS (\n  SELECT curso, AVG(nota) AS promedio, COUNT(*) AS total\n  FROM alumnos\n  GROUP BY curso\n)\nSELECT curso, ROUND(promedio, 1) AS promedio, total\nFROM resumen\nWHERE promedio >= 7;",
    r:"Cambia el filtro para ver solo los cursos con más de un alumno." },
  { m:"Más tablas", t:"JOIN: LEFT y relaciones", x:"LEFT JOIN conserva todas las filas de la tabla izquierda, aunque no tengan pareja en la derecha.",
    p:["INNER JOIN devuelve solo coincidencias", "LEFT JOIN conserva toda la izquierda", "Sin pareja aparece NULL"],
    c:"CREATE TABLE tutores (curso TEXT, tutor TEXT);\nINSERT INTO tutores VALUES (\"HTML\", \"Elena\"), (\"Python\", \"Diego\");\n\nSELECT a.nombre, a.curso, t.tutor\nFROM alumnos a\nLEFT JOIN tutores t ON a.curso = t.curso;",
    r:"Cambia LEFT JOIN por INNER JOIN y compara cuántas filas salen.",
    e:"Olvidar la condición ON multiplica las filas sin sentido." },
  { m:"Más tablas", t:"Claves y restricciones", x:"Las restricciones protegen los datos: PRIMARY KEY, NOT NULL, UNIQUE, DEFAULT y CHECK.",
    p:["PRIMARY KEY identifica cada fila", "NOT NULL obliga a tener valor", "CHECK valida una condición"],
    c:"CREATE TABLE profes (\n  id INTEGER PRIMARY KEY,\n  correo TEXT NOT NULL UNIQUE,\n  edad INTEGER CHECK (edad >= 18),\n  activo INTEGER DEFAULT 1\n);\n\nINSERT INTO profes (correo, edad) VALUES (\"ana@mail.com\", 30);\nSELECT * FROM profes;",
    r:"Intenta insertar un profe con edad 15 y lee el error." },
  { m:"Más tablas", t:"ALTER TABLE y DROP", x:"ALTER TABLE cambia la estructura de una tabla y DROP TABLE la elimina por completo.",
    p:["ADD COLUMN agrega una columna", "DROP TABLE borra tabla y datos", "Haz copias antes de borrar"],
    c:"CREATE TABLE temas (nombre TEXT);\nALTER TABLE temas ADD COLUMN horas INTEGER DEFAULT 0;\nINSERT INTO temas (nombre) VALUES (\"SQL\");\nSELECT * FROM temas;",
    r:"Elimina la tabla con DROP TABLE temas; y vuelve a consultarla.",
    e:"DROP TABLE no se puede deshacer: comprueba el nombre antes." },
  { m:"Experto", t:"Índices y plan de ejecución", x:"Un índice acelera las búsquedas por una columna. EXPLAIN muestra cómo ejecutará la consulta el motor.",
    p:["CREATE INDEX nombre ON tabla (columna)", "Aceleran lecturas pero ocupan espacio", "EXPLAIN QUERY PLAN muestra el plan"],
    c:"CREATE INDEX idx_alumnos_curso ON alumnos (curso);\n\nEXPLAIN QUERY PLAN\nSELECT * FROM alumnos WHERE curso = \"SQL\";",
    r:"Ejecuta el plan sin crear el índice y compara." },
  { m:"Experto", t:"Vistas y transacciones", x:"Una vista guarda una consulta como tabla virtual. Una transacción agrupa cambios que se confirman o se deshacen juntos.",
    p:["CREATE VIEW guarda una consulta", "BEGIN inicia una transacción", "COMMIT confirma y ROLLBACK deshace"],
    c:"CREATE VIEW aprobados AS\nSELECT nombre, nota FROM alumnos WHERE nota >= 6;\n\nBEGIN;\nUPDATE alumnos SET nota = 10 WHERE nombre = \"Sara\";\nROLLBACK;\n\nSELECT * FROM aprobados;",
    r:"Cambia ROLLBACK por COMMIT y mira cómo cambia el resultado." },
  { m:"Experto", t:"Funciones de ventana", x:"Las funciones de ventana calculan sobre un grupo de filas sin colapsarlas: rankings, acumulados y promedios móviles.",
    p:["OVER define la ventana", "PARTITION BY divide en grupos", "RANK y ROW_NUMBER numeran las filas"],
    c:"SELECT nombre, curso, nota,\n       RANK() OVER (PARTITION BY curso ORDER BY nota DESC) AS puesto,\n       AVG(nota) OVER (PARTITION BY curso) AS promedio_curso\nFROM alumnos;",
    r:"Calcula la suma acumulada de notas con SUM(nota) OVER (ORDER BY id)." },
];
