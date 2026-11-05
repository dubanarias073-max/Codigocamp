"""Bases de datos · Etapa 4: consultas avanzadas."""
from ..generador import K

LISTA = [
K("COUNT",
  d="función que cuenta filas o valores",
  u="saber cuántos registros cumplen una condición",
  mas="COUNT(*) cuenta todas las filas; COUNT(columna) cuenta las filas donde esa columna no es NULL; COUNT(DISTINCT columna) cuenta valores distintos. Es una función de agregación: devuelve un solo valor para todo el conjunto de filas.",
  k=["COUNT(*) cuenta todas las filas.", "COUNT(columna) ignora los valores NULL.", "COUNT(DISTINCT columna) cuenta valores distintos."],
  sit="Quieres saber cuántos alumnos hay en la tabla. ¿Qué función usas?",
  cod="""SELECT COUNT(*) AS total_alumnos FROM alumnos;                 -- todas las filas
SELECT COUNT(telefono) AS con_telefono FROM alumnos;           -- ignora NULL
SELECT COUNT(DISTINCT curso) AS cursos_distintos FROM alumnos;  -- sin repetir""",
  h="cuenta alumnos, teléfonos registrados y cursos distintos",
  pr=("La función que cuenta filas es ___(*). (5 letras)", "count"),
  pr2=("COUNT(columna) ignora los valores ___. (4 letras)", "null"),
  ec="contar con COUNT(columna) esperando incluir los NULL"),
K("SUM y AVG",
  d="funciones que suman y calculan el promedio",
  u="obtener totales y medias de datos numéricos",
  mas="SUM(columna) suma todos los valores y AVG(columna) calcula la media. Ambas ignoran los NULL. Se pueden filtrar con WHERE antes de calcular. ROUND(AVG(nota), 2) redondea el promedio a dos decimales.",
  k=["SUM suma los valores de una columna.", "AVG calcula el promedio de una columna.", "Ambas funciones ignoran los valores NULL."],
  sit="Quieres saber el total vendido y el precio medio de los pedidos. ¿Qué funciones usas?",
  cod="""SELECT SUM(total) AS vendido,               -- suma de todos los pedidos
       AVG(total) AS ticket_medio,          -- promedio por pedido
       ROUND(AVG(total), 2) AS medio_2dec   -- promedio redondeado
FROM pedidos;""",
  h="calcula el total vendido y el ticket medio redondeado",
  pr=("La función que suma valores es ___. (3 letras)", "sum"),
  pr2=("La función que calcula el promedio es ___. (3 letras)", "avg"),
  ec="calcular promedios con una columna llena de NULL sin darse cuenta"),
K("MIN y MAX",
  d="funciones que devuelven el valor menor y el mayor",
  u="encontrar el más barato, el más caro o la fecha más reciente",
  mas="MIN y MAX funcionan con números, fechas y textos (por orden alfabético). Devuelven solo el valor, no la fila completa. Para obtener la fila del más caro conviene usar ORDER BY precio DESC LIMIT 1.",
  k=["MIN devuelve el valor más pequeño.", "MAX devuelve el valor más grande.", "Funcionan con números, fechas y textos."],
  sit="Quieres saber cuál es el precio más bajo y el más alto de los productos. ¿Qué funciones usas?",
  cod="""SELECT MIN(precio) AS el_mas_barato,
       MAX(precio) AS el_mas_caro
FROM productos;
SELECT MAX(fecha) AS ultimo_pedido FROM pedidos;   -- con fechas también""",
  h="obtiene el precio mínimo, el máximo y la fecha del último pedido",
  pr=("La función que devuelve el valor mayor es ___. (3 letras)", "max"),
  pr2=("La función que devuelve el valor menor es ___. (3 letras)", "min"),
  ec="esperar que MAX devuelva la fila completa y no solo el valor"),
K("GROUP BY",
  d="cláusula que agrupa filas para calcular por grupos",
  u="obtener totales por categoría, cliente o mes",
  mas="GROUP BY curso crea un grupo por cada curso y las funciones de agregación calculan dentro de cada grupo. Toda columna del SELECT que no sea una función de agregación debe aparecer en el GROUP BY.",
  k=["GROUP BY crea un grupo por cada valor distinto.", "Las funciones de agregación calculan dentro de cada grupo.", "Las columnas no agregadas del SELECT deben estar en el GROUP BY."],
  sit="Quieres saber cuántos alumnos hay en cada curso. ¿Qué cláusula usas?",
  cod="""SELECT curso,
       COUNT(*)  AS alumnos,
       AVG(nota) AS media
FROM alumnos
GROUP BY curso;               -- una fila por cada curso""",
  h="calcula alumnos y nota media separados por curso",
  pr=("La cláusula que agrupa filas es GROUP ___. (2 letras)", "by"),
  pr2=("GROUP BY se suele combinar con funciones de ___. (10 letras)", "agregación", "agregacion"),
  ec="seleccionar una columna que no está en el GROUP BY",
  err=("SELECT curso, nombre, COUNT(*)\nFROM alumnos\nGROUP BY curso;", 1, "La columna nombre no está en GROUP BY ni dentro de una función de agregación.")),
K("HAVING",
  d="cláusula que filtra los grupos ya calculados",
  u="quedarse con los grupos que cumplan una condición",
  mas="WHERE filtra filas antes de agrupar y HAVING filtra grupos después de calcular. HAVING es el único sitio donde puedes usar funciones de agregación como condición: HAVING COUNT(*) > 5.",
  k=["HAVING filtra grupos después de agrupar.", "WHERE filtra filas antes de agrupar.", "En HAVING sí se pueden usar funciones de agregación."],
  sit="Quieres mostrar solo los cursos que tienen más de 5 alumnos. ¿Qué cláusula usas?",
  cod="""SELECT curso, COUNT(*) AS alumnos
FROM alumnos
GROUP BY curso
HAVING COUNT(*) > 5;          -- filtra grupos ya calculados""",
  h="muestra solo los cursos con más de cinco alumnos",
  pr=("La cláusula que filtra grupos es ___. (6 letras)", "having"),
  pr2=("WHERE filtra filas ___ de agrupar. (5 letras)", "antes"),
  ec="usar COUNT(*) dentro de WHERE",
  err=("SELECT curso, COUNT(*)\nFROM alumnos\nWHERE COUNT(*) > 5\nGROUP BY curso;", 3, "No se pueden usar funciones de agregación en WHERE: debe ir en HAVING.")),
K("Orden de las cláusulas",
  d="secuencia fija en la que se escriben las partes de un SELECT",
  u="escribir consultas completas sin errores de sintaxis",
  mas="El orden de escritura es SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY y LIMIT. La base de datos las procesa en otro orden lógico: primero FROM, luego WHERE, GROUP BY, HAVING, SELECT y al final ORDER BY y LIMIT.",
  k=["El orden de escritura es SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT.", "WHERE siempre va antes de GROUP BY.", "LIMIT es la última cláusula."],
  sit="Una consulta con varias cláusulas da error de sintaxis por escribirlas en desorden. ¿Qué debes respetar?",
  cod="""SELECT curso, COUNT(*) AS alumnos      -- 1.º qué quiero ver
FROM alumnos                           -- 2.º de dónde
WHERE nota >= 5                        -- 3.º filtro de filas
GROUP BY curso                         -- 4.º agrupar
HAVING COUNT(*) > 2                    -- 5.º filtro de grupos
ORDER BY alumnos DESC                  -- 6.º ordenar
LIMIT 3;                               -- 7.º limitar""",
  h="escribe una consulta completa con todas las cláusulas en su orden",
  pr=("La cláusula que se escribe justo después de FROM es ___. (5 letras)", "where"),
  pr2=("La última cláusula de una consulta suele ser ___. (5 letras)", "limit"),
  ec="escribir WHERE después de GROUP BY",
  err=("SELECT curso, COUNT(*)\nFROM alumnos\nGROUP BY curso\nWHERE nota > 5;", 4, "WHERE debe ir antes de GROUP BY.")),
K("JOIN",
  d="operación que combina filas de dos tablas relacionadas",
  u="mostrar datos que están repartidos en varias tablas",
  mas="Los datos normalizados están separados: el pedido guarda un cliente_id, no el nombre. Con JOIN unes las tablas usando la condición ON, normalmente la clave foránea igualada a la clave primaria. El resultado parece una sola tabla.",
  k=["JOIN combina filas de dos tablas.", "ON indica la condición con que se emparejan las filas.", "Se suele unir clave foránea con clave primaria."],
  sit="Quieres mostrar el nombre del cliente junto a cada pedido, aunque estén en tablas distintas. ¿Qué operación usas?",
  cod="""SELECT clientes.nombre, pedidos.total
FROM pedidos
JOIN clientes ON pedidos.cliente_id = clientes.id;   -- empareja por la clave""",
  h="muestra el nombre del cliente junto al total de cada pedido",
  pr=("La palabra que indica la condición de unión es ___. (2 letras)", "on"),
  pr2=("La operación que combina filas de dos tablas es ___. (4 letras)", "join"),
  ec="olvidar la condición ON y unir todas las filas con todas"),
K("INNER JOIN",
  d="unión que solo devuelve las filas con pareja en ambas tablas",
  u="mostrar solo los datos que tienen relación",
  mas="INNER JOIN (o simplemente JOIN) descarta las filas sin pareja: un cliente sin pedidos no aparece, y un pedido sin cliente tampoco. Es la unión más habitual y suele ser la más rápida.",
  k=["INNER JOIN devuelve solo las filas con pareja en ambas tablas.", "JOIN solo es lo mismo que INNER JOIN.", "Los clientes sin pedidos no aparecen con INNER JOIN."],
  sit="Quieres listar únicamente los clientes que sí han hecho pedidos. ¿Qué unión usas?",
  cod="""SELECT c.nombre, p.id AS pedido
FROM clientes c
INNER JOIN pedidos p ON p.cliente_id = c.id;   -- solo clientes con pedidos""",
  h="lista clientes que tienen al menos un pedido",
  pr=("INNER JOIN devuelve solo filas con ___ en ambas tablas. (6 letras: pareja)", "pareja"),
  pr2=("Escribir solo JOIN equivale a ___ JOIN. (5 letras)", "inner"),
  ec="esperar que INNER JOIN muestre clientes sin pedidos"),
K("LEFT JOIN",
  d="unión que conserva todas las filas de la tabla izquierda",
  u="mostrar también los datos sin pareja, como clientes sin pedidos",
  mas="LEFT JOIN devuelve todas las filas de la tabla de la izquierda (la que va después de FROM) y, si no hay pareja, rellena con NULL. Para encontrar elementos sin relación se usa LEFT JOIN y luego WHERE derecha.id IS NULL.",
  k=["LEFT JOIN conserva todas las filas de la tabla izquierda.", "Si no hay pareja, las columnas de la derecha salen NULL.", "Con IS NULL se encuentran las filas sin relación."],
  sit="Quieres ver todos los clientes, incluso los que nunca han pedido. ¿Qué unión usas?",
  cod="""SELECT c.nombre, p.id AS pedido
FROM clientes c
LEFT JOIN pedidos p ON p.cliente_id = c.id;       -- todos los clientes
-- Clientes SIN pedidos:
SELECT c.nombre FROM clientes c
LEFT JOIN pedidos p ON p.cliente_id = c.id
WHERE p.id IS NULL;""",
  h="lista todos los clientes y luego solo los que nunca han hecho un pedido",
  pr=("La unión que conserva todas las filas de la tabla izquierda es ___ JOIN. (4 letras)", "left"),
  pr2=("Si no hay pareja, las columnas de la derecha salen ___. (4 letras)", "null"),
  ec="usar INNER JOIN cuando querías conservar todos los clientes"),
K("RIGHT JOIN",
  d="unión que conserva todas las filas de la tabla derecha",
  u="mostrar todos los elementos de la segunda tabla aunque no tengan pareja",
  mas="RIGHT JOIN es el espejo de LEFT JOIN: conserva todas las filas de la tabla de la derecha. Se usa poco, porque casi siempre se puede reescribir con LEFT JOIN cambiando el orden de las tablas, que se lee con más naturalidad.",
  k=["RIGHT JOIN conserva todas las filas de la tabla derecha.", "Es el espejo de LEFT JOIN.", "Casi siempre se puede reescribir como LEFT JOIN."],
  sit="Quieres listar todos los productos de la tabla derecha, incluso los que nunca se han vendido. ¿Qué unión usas?",
  cod="""SELECT pr.nombre, d.pedido_id
FROM detalle_pedido d
RIGHT JOIN productos pr ON pr.id = d.producto_id;   -- todos los productos
-- Equivale a: FROM productos pr LEFT JOIN detalle_pedido d ...""",
  h="lista todos los productos aunque nunca se hayan vendido",
  pr=("La unión que conserva todas las filas de la tabla derecha es ___ JOIN. (5 letras)", "right"),
  pr2=("RIGHT JOIN puede reescribirse como ___ JOIN cambiando el orden. (4 letras)", "left"),
  ec="confundir cuál es la tabla izquierda y cuál la derecha"),
K("Alias de tablas en JOIN",
  d="abreviaturas de las tablas para escribir consultas más cortas",
  u="evitar ambigüedad y repetir nombres largos",
  mas="Con FROM clientes AS c escribes c.nombre en vez de clientes.nombre. Es imprescindible cuando unes una tabla consigo misma o cuando dos tablas tienen columnas con el mismo nombre (como id): MySQL no sabría a cuál te refieres.",
  k=["Los alias acortan los nombres de tablas en la consulta.", "Se necesitan cuando dos tablas tienen columnas con el mismo nombre.", "Se escriben con AS o directamente tras el nombre."],
  sit="Dos tablas tienen una columna id y MySQL da error por ambigüedad. ¿Qué solución usas?",
  cod="""SELECT c.id AS cliente, p.id AS pedido, c.nombre
FROM clientes AS c
JOIN pedidos  AS p ON p.cliente_id = c.id;   -- c y p evitan el conflicto de «id»""",
  h="distingue dos columnas id con alias de tabla",
  pr=("Cuando dos columnas se llaman igual, hay que indicar la ___ de cada una. (5 letras: tabla)", "tabla"),
  pr2=("El alias de tabla se escribe con ___. (2 letras)", "as"),
  ec="escribir id sin indicar de qué tabla es",
  err=("SELECT id, nombre\nFROM clientes c\nJOIN pedidos p ON p.cliente_id = c.id;", 1, "id existe en las dos tablas: hay que escribir c.id o p.id.")),
K("Unir tres tablas",
  d="consulta que encadena varios JOIN",
  u="combinar datos de más de dos tablas",
  mas="Cada JOIN añade una tabla a la anterior. Para mostrar qué productos compró cada cliente: clientes JOIN pedidos JOIN detalle JOIN productos. Piensa en el camino que recorren las claves foráneas y escribe un JOIN por cada paso.",
  k=["Se pueden encadenar tantos JOIN como se necesite.", "Cada JOIN necesita su propia condición ON.", "Las claves foráneas marcan el camino entre tablas."],
  sit="Quieres mostrar el nombre del cliente, el pedido y el producto comprado, que están en tres tablas. ¿Qué haces?",
  cod="""SELECT c.nombre, p.id AS pedido, pr.nombre AS producto
FROM clientes c
JOIN pedidos p          ON p.cliente_id  = c.id        -- cliente -> pedido
JOIN detalle_pedido d   ON d.pedido_id   = p.id        -- pedido  -> detalle
JOIN productos pr       ON pr.id         = d.producto_id;  -- detalle -> producto""",
  h="une clientes, pedidos, detalles y productos siguiendo las claves",
  pr=("Cada JOIN necesita su propia condición ___. (2 letras)", "on"),
  pr2=("Las claves ___ marcan el camino entre las tablas. (8 letras)", "foráneas", "foraneas"),
  ec="olvidar la condición ON de alguna unión"),
K("Subconsulta",
  d="consulta escrita dentro de otra consulta",
  u="usar el resultado de una consulta como filtro o valor de otra",
  mas="Se escribe entre paréntesis. WHERE nota > (SELECT AVG(nota) FROM alumnos) busca los alumnos por encima de la media. También funciona con IN. Las subconsultas son potentes, pero a veces un JOIN es más claro y rápido.",
  k=["Una subconsulta es una consulta dentro de otra.", "Se escribe entre paréntesis.", "A veces un JOIN es más eficiente que una subconsulta."],
  sit="Quieres encontrar los alumnos con nota superior a la media de todos. ¿Qué técnica usas?",
  cod="""SELECT nombre, nota
FROM alumnos
WHERE nota > (SELECT AVG(nota) FROM alumnos);   -- la media se calcula primero
SELECT nombre FROM alumnos
WHERE curso IN (SELECT curso FROM cursos_activos);""",
  h="busca alumnos por encima de la media usando una consulta interna",
  pr=("Una subconsulta se escribe entre ___. (paréntesis)", "paréntesis", "parentesis", "()"),
  pr2=("Una subconsulta es una consulta dentro de ___ consulta. (3 letras)", "otra"),
  ec="olvidar los paréntesis de la subconsulta"),
K("EXISTS",
  d="operador que comprueba si una subconsulta devuelve alguna fila",
  u="preguntar «¿existe alguno?» sin importar cuántos",
  mas="WHERE EXISTS (SELECT 1 FROM pedidos WHERE ...) es verdadero si la subconsulta devuelve al menos una fila. Es muy eficiente para saber si hay relación, porque se detiene al encontrar la primera coincidencia. NOT EXISTS busca los que no tienen.",
  k=["EXISTS es verdadero si la subconsulta devuelve alguna fila.", "NOT EXISTS busca los que no tienen coincidencias.", "EXISTS se detiene al encontrar la primera coincidencia."],
  sit="Quieres saber qué clientes tienen al menos un pedido, sin importar cuántos. ¿Qué operador usas?",
  cod="""SELECT c.nombre
FROM clientes c
WHERE EXISTS (SELECT 1 FROM pedidos p WHERE p.cliente_id = c.id);   -- tiene algún pedido
-- Los que NO tienen ninguno:
SELECT c.nombre FROM clientes c
WHERE NOT EXISTS (SELECT 1 FROM pedidos p WHERE p.cliente_id = c.id);""",
  h="encuentra clientes con pedidos y clientes sin ninguno",
  pr=("El operador que pregunta si una subconsulta devuelve filas es ___. (6 letras)", "exists"),
  pr2=("Para encontrar a los que no tienen coincidencias se usa NOT ___. (6 letras)", "exists"),
  ec="usar EXISTS sin relacionar la subconsulta con la consulta externa"),
K("UNION",
  d="operador que junta los resultados de varias consultas",
  u="combinar listas de tablas distintas en un solo resultado",
  mas="UNION une los resultados de dos SELECT con el mismo número de columnas y tipos compatibles, eliminando duplicados. UNION ALL conserva los duplicados y es más rápido. Los nombres de columnas son los del primer SELECT.",
  k=["UNION une los resultados de varios SELECT.", "Los SELECT deben tener el mismo número de columnas.", "UNION ALL conserva los duplicados."],
  sit="Quieres una sola lista con los correos de clientes y los de proveedores. ¿Qué operador usas?",
  cod="""SELECT correo FROM clientes
UNION                          -- elimina repetidos
SELECT correo FROM proveedores;
-- UNION ALL los conserva y es más rápido:
SELECT correo FROM clientes
UNION ALL
SELECT correo FROM proveedores;""",
  h="junta los correos de dos tablas con y sin eliminar duplicados",
  pr=("El operador que junta resultados de varias consultas es ___. (5 letras)", "union"),
  pr2=("Para conservar los duplicados se usa UNION ___. (3 letras)", "all"),
  ec="unir consultas con distinto número de columnas"),
K("CASE",
  d="expresión que elige un resultado según condiciones",
  u="crear categorías o etiquetas dentro de una consulta",
  mas="CASE funciona como un «si… entonces… si no…»: WHEN condición THEN valor, y ELSE para el resto. Termina con END. Sirve para convertir notas en «Aprobado» y «Suspenso», o agrupar edades en rangos, sin modificar la tabla.",
  k=["CASE devuelve un valor según condiciones.", "Termina con END.", "ELSE define el resultado cuando no se cumple ninguna condición."],
  sit="Quieres mostrar «Aprobado» o «Suspenso» según la nota, sin guardar ese texto en la tabla. ¿Qué usas?",
  cod="""SELECT nombre, nota,
  CASE
    WHEN nota >= 9 THEN 'Sobresaliente'
    WHEN nota >= 5 THEN 'Aprobado'
    ELSE 'Suspenso'                 -- el resto de casos
  END AS resultado
FROM alumnos;""",
  h="convierte cada nota en una etiqueta de texto sin modificar la tabla",
  pr=("La expresión que elige un resultado según condiciones es ___. (4 letras)", "case"),
  pr2=("Una expresión CASE termina con la palabra ___. (3 letras)", "end"),
  ec="olvidar END al final del CASE",
  err=("SELECT nombre,\n  CASE WHEN nota >= 5 THEN 'Aprobado'\n  ELSE 'Suspenso'\nFROM alumnos;", 3, "Falta cerrar el CASE con END antes de FROM.")),
K("Funciones de texto",
  d="funciones que transforman o miden cadenas de texto",
  u="limpiar, unir o cambiar el formato de nombres y textos",
  mas="CONCAT une textos, UPPER y LOWER cambian a mayúsculas o minúsculas, LENGTH cuenta caracteres, TRIM quita espacios sobrantes y SUBSTRING extrae una parte. No cambian los datos guardados: solo el resultado de la consulta.",
  k=["CONCAT une varios textos en uno.", "UPPER convierte a mayúsculas y LOWER a minúsculas.", "TRIM elimina espacios al principio y al final."],
  sit="Quieres mostrar nombre y apellido en una sola columna y en mayúsculas. ¿Qué funciones usas?",
  cod="""SELECT CONCAT(nombre, ' ', apellido)       AS completo,   -- une textos
       UPPER(nombre)                        AS en_mayus,   -- MAYÚSCULAS
       LENGTH(nombre)                       AS letras,     -- cuántos caracteres
       TRIM('   hola   ')                   AS limpio      -- quita espacios
FROM alumnos;""",
  h="une, convierte y mide textos sin modificar los datos guardados",
  pr=("La función que une varios textos es ___. (6 letras)", "concat"),
  pr2=("La función que convierte a mayúsculas es ___. (5 letras)", "upper"),
  ec="creer que UPPER cambia el dato guardado en la tabla"),
K("Funciones de fecha",
  d="funciones que obtienen y calculan con fechas",
  u="saber qué día es, calcular edades o plazos",
  mas="NOW() devuelve la fecha y hora actuales, CURDATE() solo la fecha. YEAR, MONTH y DAY extraen partes. DATEDIFF resta dos fechas y DATE_ADD suma días. Con ellas sacas «pedidos del último mes» o «días hasta el vencimiento».",
  k=["NOW() devuelve la fecha y hora actuales.", "DATEDIFF calcula los días entre dos fechas.", "YEAR(), MONTH() y DAY() extraen partes de una fecha."],
  sit="Quieres calcular cuántos días han pasado desde cada pedido hasta hoy. ¿Qué función usas?",
  cod="""SELECT NOW()      AS ahora,                          -- fecha y hora actuales
       CURDATE()   AS hoy,                            -- solo la fecha
       YEAR(fecha) AS anio,                           -- extrae el año
       DATEDIFF(CURDATE(), fecha) AS dias_desde_pedido  -- días transcurridos
FROM pedidos;""",
  h="obtiene la fecha actual y los días transcurridos desde cada pedido",
  pr=("La función que devuelve la fecha y hora actuales es ___(). (3 letras)", "now"),
  pr2=("La función que calcula los días entre dos fechas es ___. (8 letras)", "datediff"),
  ec="comparar fechas como si fueran texto"),
K("Vistas",
  d="consulta guardada con nombre que se usa como una tabla",
  u="reutilizar consultas complejas y simplificar permisos",
  mas="CREATE VIEW resumen AS SELECT ... guarda la consulta. Después puedes escribir SELECT * FROM resumen como si fuera una tabla. La vista no guarda datos: ejecuta la consulta cada vez. Ayuda a ocultar columnas sensibles a ciertos usuarios.",
  k=["Una vista es una consulta guardada con nombre.", "Una vista no guarda datos propios.", "Las vistas pueden ocultar columnas sensibles."],
  sit="Quieres guardar una consulta compleja con JOIN para reutilizarla como si fuera una tabla. ¿Qué creas?",
  cod="""CREATE VIEW ventas_por_cliente AS
SELECT c.nombre, SUM(p.total) AS comprado
FROM clientes c JOIN pedidos p ON p.cliente_id = c.id
GROUP BY c.nombre;
SELECT * FROM ventas_por_cliente WHERE comprado > 100;   -- se usa como una tabla""",
  h="guarda una consulta con JOIN y agrupación y la consulta como una tabla",
  pr=("El comando que guarda una consulta con nombre es CREATE ___. (4 letras)", "view"),
  pr2=("Una vista ___ guarda datos propios. (no)", "no"),
  ec="creer que la vista copia los datos"),
K("COALESCE e IFNULL",
  d="funciones que sustituyen los valores NULL por otro valor",
  u="mostrar un texto o número por defecto cuando falta un dato",
  mas="IFNULL(telefono, 'Sin teléfono') devuelve el teléfono o el texto si es NULL. COALESCE acepta varios valores y devuelve el primero que no sea NULL. Evitan que los NULL rompan cálculos y presenten celdas vacías.",
  k=["IFNULL sustituye un NULL por otro valor.", "COALESCE devuelve el primer valor que no sea NULL.", "Los NULL pueden romper cálculos si no se sustituyen."],
  sit="Quieres mostrar «Sin teléfono» cuando un cliente no tiene teléfono registrado. ¿Qué función usas?",
  cod="""SELECT nombre,
       IFNULL(telefono, 'Sin teléfono')               AS tel,      -- reemplaza NULL
       COALESCE(movil, telefono, 'No indicado')       AS contacto  -- primer valor no nulo
FROM clientes;""",
  h="reemplaza datos ausentes por textos claros en el resultado",
  pr=("La función que devuelve el primer valor no nulo es ___. (8 letras)", "coalesce"),
  pr2=("La función que sustituye un NULL por otro valor es ___. (6 letras)", "ifnull"),
  ec="sumar columnas con NULL sin sustituirlos"),
]
