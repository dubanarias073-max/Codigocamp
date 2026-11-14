"""SQL · Etapa 4: Unir tablas y subconsultas."""
from ..generador import K

LISTA = [
K("Relaciones entre tablas",
  d="vínculo entre filas de dos tablas mediante una clave",
  u="evitar repetir datos guardándolos una sola vez",
  mas="En lugar de repetir el nombre del curso en cada alumno, se guarda el curso en su propia tabla y el alumno apunta a él con un id. Así cada dato vive en un solo lugar.",
  k=["Las relaciones conectan tablas mediante claves.", "Una relación evita repetir datos.", "Cada dato se guarda una sola vez y se enlaza por id."],
  sit="Muchos alumnos comparten el mismo curso y no quieres repetir sus datos en cada fila. ¿Qué diseñas?",
  cod="""-- cursos(id, nombre)       alumnos2(id, nombre, curso_id)
SELECT a.nombre, a.curso_id
FROM alumnos2 AS a;   -- curso_id apunta a cursos.id""",
  h="muestra cada alumno con el id del curso al que apunta",
  pr=("Las tablas se relacionan mediante una ___. (5 letras: clave)", "clave"),
  ec="repetir los mismos datos en muchas filas en vez de relacionar tablas"),
K("INNER JOIN",
  d="unión que devuelve solo las filas que coinciden en ambas tablas",
  u="combinar tablas mostrando solo coincidencias",
  mas="INNER JOIN une dos tablas según una condición escrita con ON. Si una fila no tiene pareja en la otra tabla, no aparece en el resultado.",
  k=["INNER JOIN devuelve solo las filas que coinciden.", "La condición de unión se escribe con ON.", "Las filas sin pareja no aparecen en un INNER JOIN."],
  sit="Quieres mostrar cada alumno junto al nombre de su curso, solo si tiene curso. ¿Qué unión usas?",
  cod="""SELECT a.nombre, c.titulo
FROM alumnos2 AS a
INNER JOIN cursos AS c ON a.curso_id = c.id;   -- solo coincidencias""",
  h="muestra cada alumno con el título de su curso",
  pr=("La palabra que escribe la condición de unión es ___. (2 letras)", "on"),
  ec="olvidar la condición ON y mezclar todas las filas",
  err=("SELECT a.nombre, c.titulo\nFROM alumnos2 a\nINNER JOIN cursos c;", 3, "Falta la condición ON: ON a.curso_id = c.id.")),
K("LEFT JOIN",
  d="unión que conserva todas las filas de la tabla izquierda",
  u="incluir filas aunque no tengan pareja",
  mas="LEFT JOIN devuelve todas las filas de la primera tabla; cuando no hay coincidencia en la segunda, sus columnas salen como NULL. Es ideal para ver qué falta.",
  k=["LEFT JOIN conserva todas las filas de la tabla izquierda.", "Sin coincidencia, las columnas de la derecha salen NULL.", "LEFT JOIN sirve para encontrar filas sin pareja."],
  sit="Quieres listar todos los alumnos, incluso los que no tienen curso asignado. ¿Qué unión usas?",
  cod="""SELECT a.nombre, c.titulo
FROM alumnos2 AS a
LEFT JOIN cursos AS c ON a.curso_id = c.id;   -- nadie se pierde""",
  h="lista todos los alumnos con su curso, aunque no tengan",
  pr=("La unión que conserva todas las filas de la izquierda es ___ JOIN. (4 letras)", "left"),
  ec="usar INNER JOIN y perder las filas sin pareja"),
K("Alias de tabla",
  d="nombre corto que se da a una tabla dentro de la consulta",
  u="escribir menos y evitar ambigüedades",
  mas="Después del nombre de la tabla se escribe un alias, con o sin AS, y se usa como prefijo de las columnas. Es obligatorio cuando se une una tabla consigo misma.",
  k=["Un alias de tabla es un nombre corto dentro de la consulta.", "El alias se usa como prefijo de las columnas.", "El alias evita ambigüedades entre columnas con el mismo nombre."],
  sit="Dos tablas tienen la columna id y escribir sus nombres completos es largo. ¿Qué usas?",
  cod="""SELECT a.nombre, c.titulo   -- a y c son alias
FROM alumnos2 AS a, cursos AS c
WHERE a.curso_id = c.id;""",
  h="usa alias cortos para dos tablas",
  pr=("Una tabla puede renombrarse con la palabra ___ y un alias. (2 letras)", "as"),
  ec="usar una columna con nombre repetido sin indicar de qué tabla es"),
K("Unir tres tablas",
  d="encadenar varios JOIN para combinar más de dos tablas",
  u="reunir datos repartidos en varias tablas",
  mas="Cada JOIN añade una tabla nueva a lo ya unido. Se leen de arriba hacia abajo, cada uno con su propia condición ON.",
  k=["Se pueden encadenar varios JOIN en una consulta.", "Cada JOIN lleva su propia condición ON.", "Unir tres tablas permite reunir datos de varias fuentes."],
  sit="Necesitas mostrar alumno, curso e instructor, que están en tres tablas distintas. ¿Qué haces?",
  cod="""SELECT a.nombre, c.titulo, i.nombre AS instructor
FROM alumnos2 AS a
JOIN cursos AS c ON a.curso_id = c.id      -- une alumnos con cursos
JOIN instructores AS i ON c.instructor_id = i.id;   -- y cursos con instructores""",
  h="muestra alumno, curso e instructor uniendo tres tablas",
  pr=("Para unir tres tablas se encadenan varios ___. (4 letras)", "join"),
  ec="olvidar la condición ON de uno de los JOIN"),
K("CROSS JOIN",
  d="unión que combina cada fila de una tabla con todas las de otra",
  u="generar todas las combinaciones posibles",
  mas="CROSS JOIN no lleva condición: si una tabla tiene 3 filas y la otra 4, el resultado tiene 12. Es útil para crear calendarios o catálogos de combinaciones, pero crece muy rápido.",
  k=["CROSS JOIN combina todas las filas de ambas tablas.", "CROSS JOIN no usa condición ON.", "El resultado de CROSS JOIN tiene filas1 por filas2 filas."],
  sit="Quieres todas las parejas posibles entre tallas y colores. ¿Qué unión usas?",
  cod="""SELECT t.talla, c.color
FROM tallas AS t
CROSS JOIN colores AS c;   -- cada talla con cada color""",
  h="genera todas las combinaciones de talla y color",
  pr=("La unión que combina todas las filas con todas es ___ JOIN. (5 letras)", "cross"),
  ec="usar CROSS JOIN con tablas grandes y generar millones de filas"),
K("Autounión",
  d="unión de una tabla consigo misma usando dos alias",
  u="relacionar filas de la misma tabla entre sí",
  mas="Se usa cuando una columna apunta a la misma tabla, por ejemplo empleado y jefe. La tabla aparece dos veces con alias distintos, como si fueran dos tablas.",
  k=["Una autounión une una tabla consigo misma.", "Una autounión necesita dos alias distintos.", "Sirve para jerarquías como empleado y jefe."],
  sit="Cada empleado guarda el id de su jefe, que también es un empleado. ¿Qué técnica usas para mostrar ambos nombres?",
  cod="""SELECT e.nombre AS empleado, j.nombre AS jefe
FROM empleados AS e
JOIN empleados AS j ON e.jefe_id = j.id;   -- la misma tabla dos veces""",
  h="muestra cada empleado junto a su jefe",
  pr=("En una autounión la tabla se escribe dos veces con distinto ___. (5 letras)", "alias"),
  ec="usar la misma tabla dos veces sin alias"),
K("UNION",
  d="operador que junta los resultados de dos consultas sin repetir filas",
  u="combinar listas de varias consultas",
  mas="UNION apila los resultados de dos SELECT en una sola lista y elimina los duplicados. Ambos SELECT deben tener la misma cantidad de columnas y tipos compatibles.",
  k=["UNION junta los resultados de dos consultas.", "UNION elimina las filas duplicadas.", "Los SELECT de un UNION deben tener el mismo número de columnas."],
  sit="Tienes dos consultas con nombres y quieres una sola lista sin repetidos. ¿Qué operador usas?",
  cod="""SELECT nombre FROM alumnos WHERE curso = 'HTML'
UNION   -- junta ambas listas sin repetidos
SELECT nombre FROM alumnos WHERE nota > 8;""",
  h="junta en una lista los alumnos de HTML y los de nota alta",
  pr=("El operador que une resultados sin duplicados es ___. (5 letras)", "union"),
  ec="usar UNION con consultas de distinta cantidad de columnas"),
K("UNION ALL",
  d="operador que junta los resultados de dos consultas conservando los repetidos",
  u="combinar listas sin perder ninguna fila",
  mas="UNION ALL no revisa duplicados, por eso es más rápido que UNION. Úsalo cuando sabes que no hay repetidos o cuando los necesitas.",
  k=["UNION ALL conserva las filas repetidas.", "UNION ALL es más rápido que UNION.", "UNION ALL no compara filas para quitar duplicados."],
  sit="Quieres juntar dos listas y conservar cada aparición, incluso las repetidas. ¿Qué operador usas?",
  cod="""SELECT curso FROM alumnos WHERE nota > 7
UNION ALL   -- conserva repetidos
SELECT curso FROM alumnos WHERE nota < 7;""",
  h="junta los cursos de notas altas y bajas sin quitar repetidos",
  pr=("El operador que junta conservando duplicados es UNION ___. (3 letras)", "all"),
  ec="creer que UNION ALL elimina duplicados"),
K("INTERSECT",
  d="operador que devuelve solo las filas presentes en ambas consultas",
  u="encontrar lo que dos resultados tienen en común",
  mas="INTERSECT compara los resultados de dos SELECT y deja únicamente las filas que aparecen en los dos. Elimina duplicados.",
  k=["INTERSECT devuelve las filas comunes a dos consultas.", "INTERSECT elimina duplicados.", "Una fila debe estar en ambos resultados para aparecer."],
  sit="Quieres los cursos que tienen alumnos con nota alta y también alumnos con nota baja. ¿Qué operador usas?",
  cod="""SELECT curso FROM alumnos WHERE nota >= 8
INTERSECT   -- solo lo que está en ambas
SELECT curso FROM alumnos WHERE nota < 8;""",
  h="muestra los cursos que aparecen en ambas consultas",
  pr=("El operador que deja solo lo común es ___. (9 letras)", "intersect"),
  ec="confundir INTERSECT con UNION"),
K("EXCEPT",
  d="operador que devuelve lo de la primera consulta que no está en la segunda",
  u="restar un resultado de otro",
  mas="EXCEPT toma las filas del primer SELECT y quita las que también aparecen en el segundo. El orden importa: A EXCEPT B no es igual que B EXCEPT A.",
  k=["EXCEPT resta los resultados de la segunda consulta a la primera.", "EXCEPT depende del orden de las consultas.", "EXCEPT elimina duplicados."],
  sit="Quieres los cursos que existen pero en los que nadie sacó más de 8. ¿Qué operador usas?",
  cod="""SELECT DISTINCT curso FROM alumnos
EXCEPT   -- resta la segunda lista de la primera
SELECT curso FROM alumnos WHERE nota > 8;""",
  h="muestra los cursos que no tienen notas mayores a 8",
  pr=("El operador que resta un resultado de otro es ___. (6 letras)", "except"),
  ec="invertir el orden y obtener otro resultado en EXCEPT"),
K("Subconsulta en WHERE",
  d="consulta escrita dentro de otra para obtener un valor de comparación",
  u="filtrar con un valor calculado por otra consulta",
  mas="La subconsulta va entre paréntesis y se ejecuta primero. Su resultado, por ejemplo el promedio, se usa en la condición de la consulta principal.",
  k=["Una subconsulta es una consulta dentro de otra.", "La subconsulta va entre paréntesis.", "Su resultado se usa en la condición de la consulta principal."],
  sit="Quieres los alumnos con nota mayor que el promedio, que antes hay que calcular. ¿Qué usas?",
  cod="""SELECT nombre, nota
FROM alumnos
WHERE nota > (SELECT AVG(nota) FROM alumnos);   -- primero calcula el promedio""",
  h="muestra los alumnos con nota sobre el promedio",
  pr=("Una subconsulta se escribe entre ___. (paréntesis)", "parentesis", "paréntesis"),
  ec="olvidar los paréntesis alrededor de la subconsulta",
  err=("SELECT nombre\nFROM alumnos\nWHERE nota > SELECT AVG(nota) FROM alumnos;", 3, "La subconsulta debe ir entre paréntesis.")),
K("Subconsulta con IN",
  d="subconsulta que devuelve una lista de valores para comparar con IN",
  u="filtrar según los resultados de otra consulta",
  mas="Cuando la subconsulta devuelve varias filas, se compara con IN en lugar de =. La condición es verdadera si el valor aparece en esa lista.",
  k=["IN con subconsulta compara contra una lista de resultados.", "La subconsulta de IN puede devolver varias filas.", "Se usa IN en lugar de = cuando hay varios valores."],
  sit="Quieres alumnos que estén en cursos con al menos dos inscritos, lista calculada por otra consulta. ¿Qué usas?",
  cod="""SELECT nombre, curso
FROM alumnos
WHERE curso IN (SELECT curso FROM alumnos
                GROUP BY curso HAVING COUNT(*) >= 2);   -- lista de cursos""",
  h="muestra los alumnos de cursos con dos o más inscritos",
  pr=("Con una subconsulta que devuelve varias filas se usa el operador ___. (2 letras)", "in"),
  ec="usar = con una subconsulta que devuelve varias filas"),
K("Subconsulta en FROM",
  d="consulta usada como si fuera una tabla temporal",
  u="trabajar sobre un resultado ya calculado",
  mas="Una subconsulta en FROM se llama tabla derivada y necesita un alias. Sirve para calcular algo por pasos y luego filtrar o resumir ese resultado.",
  k=["Una subconsulta en FROM actúa como tabla temporal.", "La tabla derivada necesita un alias.", "Permite calcular por pasos."],
  sit="Primero calculas el promedio por curso y luego quieres filtrar ese resultado. ¿Qué usas?",
  cod="""SELECT *
FROM (SELECT curso, AVG(nota) AS prom
      FROM alumnos GROUP BY curso) AS t   -- tabla derivada con alias
WHERE t.prom > 7;""",
  h="calcula promedios por curso y deja los mayores a 7",
  pr=("Una subconsulta en FROM necesita un ___. (5 letras)", "alias"),
  ec="olvidar ponerle alias a la subconsulta del FROM"),
K("Subconsulta correlacionada",
  d="subconsulta que depende de cada fila de la consulta principal",
  u="comparar cada fila con un cálculo propio de su grupo",
  mas="La subconsulta usa una columna de la consulta externa, así que se vuelve a ejecutar para cada fila. Permite, por ejemplo, comparar cada nota con el promedio de su propio curso.",
  k=["Una subconsulta correlacionada usa columnas de la consulta externa.", "Se ejecuta de nuevo para cada fila.", "Permite comparar cada fila con su propio grupo."],
  sit="Quieres alumnos cuya nota supera el promedio de su propio curso, no el general. ¿Qué usas?",
  cod="""SELECT a.nombre, a.nota
FROM alumnos AS a
WHERE a.nota > (SELECT AVG(b.nota) FROM alumnos AS b
                WHERE b.curso = a.curso);   -- depende de la fila a""",
  h="muestra los alumnos por encima del promedio de su curso",
  pr=("La subconsulta que usa columnas de la consulta externa es ___. (13 letras: correlacionada)", "correlacionada"),
  ec="olvidar la condición que enlaza la subconsulta con la fila externa"),
K("EXISTS",
  d="operador que comprueba si una subconsulta devuelve alguna fila",
  u="saber si existe al menos una coincidencia",
  mas="EXISTS devuelve verdadero si la subconsulta produce al menos una fila, sin importar su contenido. Suele ser más eficiente que IN con tablas grandes.",
  k=["EXISTS comprueba si una subconsulta devuelve alguna fila.", "EXISTS devuelve verdadero o falso.", "EXISTS no necesita conocer los valores devueltos."],
  sit="Quieres cursos que tengan al menos un alumno inscrito. ¿Qué operador usas?",
  cod="""SELECT c.titulo
FROM cursos AS c
WHERE EXISTS (SELECT 1 FROM alumnos2 AS a
              WHERE a.curso_id = c.id);   -- ¿hay algún alumno?""",
  h="muestra los cursos que tienen al menos un alumno",
  pr=("El operador que comprueba si hay alguna fila es ___. (6 letras)", "exists"),
  ec="creer que EXISTS compara valores en lugar de comprobar si hay filas"),
K("NOT EXISTS",
  d="operador que es verdadero cuando la subconsulta no devuelve filas",
  u="encontrar filas sin coincidencias",
  mas="NOT EXISTS deja pasar las filas para las que la subconsulta está vacía. Es una forma segura de buscar elementos que no tienen relación con otra tabla.",
  k=["NOT EXISTS es verdadero cuando la subconsulta no devuelve filas.", "NOT EXISTS sirve para buscar filas sin coincidencia.", "NOT EXISTS maneja bien los NULL."],
  sit="Quieres los cursos que todavía no tienen ningún alumno. ¿Qué operador usas?",
  cod="""SELECT c.titulo
FROM cursos AS c
WHERE NOT EXISTS (SELECT 1 FROM alumnos2 AS a
                  WHERE a.curso_id = c.id);   -- ningún alumno""",
  h="muestra los cursos sin alumnos",
  pr=("Para buscar filas sin coincidencias se usa NOT ___. (6 letras)", "exists"),
  ec="usar NOT IN con una lista que contiene NULL"),
K("Anti-unión",
  d="LEFT JOIN seguido de IS NULL para hallar filas sin pareja",
  u="encontrar elementos que no tienen relación",
  mas="Se hace un LEFT JOIN y luego se filtra con WHERE donde la columna de la segunda tabla es NULL. Así quedan solo las filas que no encontraron pareja.",
  k=["La anti-unión halla filas sin pareja en otra tabla.", "Combina LEFT JOIN con IS NULL.", "Es una alternativa a NOT EXISTS."],
  sit="Quieres los alumnos que no tienen ningún curso asignado usando un LEFT JOIN. ¿Qué técnica aplicas?",
  cod="""SELECT a.nombre
FROM alumnos2 AS a
LEFT JOIN cursos AS c ON a.curso_id = c.id
WHERE c.id IS NULL;   -- sin pareja en cursos""",
  h="muestra los alumnos sin curso",
  pr=("La anti-unión filtra con IS ___ en la tabla de la derecha. (4 letras)", "null"),
  ec="filtrar con IS NULL sobre la tabla izquierda en lugar de la derecha"),
K("WITH (CTE)",
  d="consulta con nombre que se define antes de la consulta principal",
  u="dividir una consulta compleja en pasos legibles",
  mas="WITH nombre AS (consulta) crea una expresión de tabla común que luego usas como si fuera una tabla. Hace el código más ordenado que anidar subconsultas.",
  k=["WITH define una consulta con nombre reutilizable.", "Una CTE se usa como si fuera una tabla.", "Una CTE hace la consulta más legible que anidar subconsultas."],
  sit="Tu consulta tiene subconsultas anidadas muy difíciles de leer. ¿Qué usas para ordenarla en pasos?",
  cod="""WITH promedios AS (
  SELECT curso, AVG(nota) AS prom FROM alumnos GROUP BY curso   -- paso 1
)
SELECT * FROM promedios WHERE prom > 7;   -- paso 2""",
  h="calcula promedios por curso en un paso y los filtra en otro",
  pr=("La palabra que define una CTE es ___. (4 letras)", "with"),
  ec="usar la CTE fuera de la consulta que la sigue"),
K("JOIN con GROUP BY",
  d="combinación de unir tablas y resumir los resultados por grupo",
  u="calcular totales usando datos de varias tablas",
  mas="Primero se unen las tablas y luego se agrupa el resultado. Con LEFT JOIN, COUNT(columna_derecha) cuenta cero para quien no tiene filas relacionadas.",
  k=["Se puede agrupar el resultado de un JOIN.", "Primero se unen las tablas y luego se agrupa.", "COUNT de la tabla derecha da cero si no hay coincidencias."],
  sit="Quieres saber cuántos alumnos tiene cada curso, incluidos los cursos vacíos. ¿Qué combinas?",
  cod="""SELECT c.titulo, COUNT(a.id) AS alumnos
FROM cursos AS c
LEFT JOIN alumnos2 AS a ON a.curso_id = c.id
GROUP BY c.titulo;   -- agrupa el resultado de la unión""",
  h="cuenta los alumnos de cada curso, incluso los vacíos",
  pr=("Después de unir tablas se resume con GROUP ___. (2 letras)", "by"),
  ec="contar con COUNT(*) y obtener 1 en cursos sin alumnos"),
]
