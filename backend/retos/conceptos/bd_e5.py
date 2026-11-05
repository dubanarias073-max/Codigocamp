"""Bases de datos · Etapa 5: rendimiento, seguridad y práctica profesional."""
from ..generador import K

LISTA = [
K("Índices",
  d="estructura que acelera las búsquedas en una columna",
  u="encontrar filas rápido sin recorrer toda la tabla",
  mas="Un índice funciona como el índice de un libro: en vez de leer todas las páginas, vas directo a la que buscas. Se crean sobre las columnas que más se usan en WHERE, JOIN y ORDER BY. Aceleran las lecturas, pero ralentizan un poco las escrituras y ocupan espacio.",
  k=["Un índice acelera las búsquedas por una columna.", "Los índices ralentizan un poco los INSERT y UPDATE.", "Se crean en columnas usadas en WHERE, JOIN y ORDER BY."],
  sit="Una consulta por correo tarda segundos en una tabla con millones de filas. ¿Qué creas para acelerarla?",
  cod="""CREATE INDEX idx_usuarios_correo ON usuarios (correo);   -- índice sobre el correo
SELECT * FROM usuarios WHERE correo = 'ana@correo.com';  -- ahora busca rápido
-- Sin índice, MySQL recorre TODAS las filas""",
  h="crea un índice para acelerar las búsquedas por correo",
  pr=("El comando que crea un índice es CREATE ___. (5 letras)", "index"),
  pr2=("Un índice acelera las ___ y puede ralentizar las escrituras. (9 letras: consultas)", "consultas", "lecturas", "búsquedas", "busquedas"),
  ec="crear índices en todas las columnas sin necesidad"),
K("Índices compuestos",
  d="índice que abarca varias columnas a la vez",
  u="acelerar consultas que filtran por más de una columna",
  mas="Un índice sobre (apellido, nombre) ayuda cuando buscas por apellido, o por apellido y nombre, pero no cuando buscas solo por nombre. El orden de las columnas importa: pon primero la que más se filtra. Un índice UNIQUE compuesto además impide repetir la combinación.",
  k=["Un índice compuesto abarca varias columnas.", "El orden de las columnas en el índice importa.", "Un UNIQUE compuesto impide repetir la combinación."],
  sit="Buscas con frecuencia por apellido y nombre a la vez. ¿Qué tipo de índice conviene?",
  cod="""CREATE INDEX idx_alumno_nombre ON alumnos (apellido, nombre);   -- compuesto
-- Ayuda a:  WHERE apellido = 'Pérez'
-- Ayuda a:  WHERE apellido = 'Pérez' AND nombre = 'Ana'
-- NO ayuda: WHERE nombre = 'Ana'   (la primera columna es apellido)""",
  h="crea un índice sobre dos columnas y explica cuándo se aprovecha",
  pr=("En un índice compuesto, el ___ de las columnas importa. (5 letras)", "orden"),
  pr2=("Un índice que abarca varias columnas se llama ___. (9 letras)", "compuesto"),
  ec="poner primero en el índice la columna menos usada"),
K("EXPLAIN",
  d="comando que muestra cómo ejecutará MySQL una consulta",
  u="descubrir por qué una consulta es lenta",
  mas="Si escribes EXPLAIN antes de un SELECT, MySQL no ejecuta la consulta, sino que muestra su plan: qué índice usa y cuántas filas piensa revisar. Si ves type = ALL, recorre toda la tabla; es la señal de que quizás falta un índice.",
  k=["EXPLAIN muestra el plan de ejecución de una consulta.", "El tipo ALL indica que se recorre toda la tabla.", "Sirve para decidir qué índices crear."],
  sit="Quieres saber si una consulta lenta está usando algún índice. ¿Qué escribes antes del SELECT?",
  cod="""EXPLAIN SELECT * FROM usuarios WHERE correo = 'ana@correo.com';
-- type = ALL   -> recorre toda la tabla (lento)
-- type = ref   -> usa un índice (rápido)
-- key          -> índice elegido; rows -> filas estimadas""",
  h="pide el plan de una consulta y explica cómo interpretarlo",
  pr=("La palabra que muestra el plan de una consulta es ___. (7 letras)", "explain"),
  pr2=("El tipo que indica recorrer toda la tabla es ___. (3 letras)", "all"),
  ec="optimizar consultas sin medirlas antes"),
K("Transacciones",
  d="grupo de operaciones que se ejecutan como una sola unidad",
  u="evitar datos a medias si algo falla",
  mas="Una transferencia bancaria resta dinero a una cuenta y lo suma a otra. Si falla en medio, no puede quedar la mitad hecha. Una transacción agrupa ambas operaciones: o se hacen todas o no se hace ninguna.",
  k=["Una transacción agrupa varias operaciones en una unidad.", "O se ejecutan todas las operaciones o ninguna.", "Evitan datos a medias cuando algo falla."],
  sit="Una transferencia debe restar a una cuenta y sumar a otra, o no hacerse en absoluto. ¿Qué usas?",
  cod="""START TRANSACTION;                                        -- empieza la unidad
UPDATE cuentas SET saldo = saldo - 100 WHERE id = 1;     -- resta
UPDATE cuentas SET saldo = saldo + 100 WHERE id = 2;     -- suma
COMMIT;                                                  -- confirma las dos""",
  h="agrupa una resta y una suma de saldo en una única unidad",
  pr=("Una transacción comienza con START ___. (11 letras)", "transaction"),
  pr2=("En una transacción se hace todo o ___. (5 letras: nada)", "nada"),
  ec="hacer operaciones relacionadas por separado y dejar datos a medias"),
K("COMMIT y ROLLBACK",
  d="comandos que confirman o deshacen una transacción",
  u="decidir si los cambios se guardan o se descartan",
  mas="COMMIT guarda definitivamente todos los cambios de la transacción. ROLLBACK los deshace y deja la base como estaba al empezar. Tras un error en la aplicación, se hace ROLLBACK para no dejar cambios a medias.",
  k=["COMMIT confirma definitivamente los cambios.", "ROLLBACK deshace los cambios de la transacción.", "Tras un error conviene hacer ROLLBACK."],
  sit="Algo falló a mitad de una transacción y quieres deshacer todo lo hecho. ¿Qué comando usas?",
  cod="""START TRANSACTION;
DELETE FROM pedidos WHERE cliente_id = 7;
-- ¡Me equivoqué de cliente!
ROLLBACK;                    -- todo vuelve a como estaba
-- Si hubiera sido correcto: COMMIT;""",
  h="deshace un borrado hecho por error dentro de una transacción",
  pr=("El comando que deshace una transacción es ___. (8 letras)", "rollback"),
  pr2=("El comando que confirma una transacción es ___. (6 letras)", "commit"),
  ec="olvidar COMMIT y creer que los cambios ya se guardaron"),
K("ACID",
  d="cuatro garantías de las transacciones fiables",
  u="confiar en que los datos quedan correctos aunque haya fallos",
  mas="ACID son las siglas de Atomicidad (todo o nada), Consistencia (se cumplen las reglas), Aislamiento (las transacciones simultáneas no se estorban) y Durabilidad (lo confirmado no se pierde ni con un apagón). MySQL con InnoDB las cumple.",
  k=["ACID significa Atomicidad, Consistencia, Aislamiento y Durabilidad.", "La atomicidad significa todo o nada.", "La durabilidad garantiza que lo confirmado no se pierde."],
  sit="Quieres describir las cuatro garantías que hacen fiables a las transacciones. ¿Qué sigla usas?",
  cod="""-- A: Atomicidad    -> todo o nada
-- C: Consistencia  -> siempre se cumplen las reglas
-- I: Aislamiento   -- transacciones simultáneas no se estorban
-- D: Durabilidad   -> lo confirmado no se pierde
SELECT 'InnoDB cumple ACID' AS motor;""",
  h="resume las cuatro garantías ACID de las transacciones",
  pr=("La A de ACID significa ___. (10 letras: atomicidad)", "atomicidad"),
  pr2=("La D de ACID significa ___. (11 letras: durabilidad)", "durabilidad"),
  ec="confundir consistencia con aislamiento"),
K("Concurrencia y bloqueos",
  d="situación en que varios usuarios usan los mismos datos a la vez",
  u="evitar que dos usuarios se pisen al modificar lo mismo",
  mas="Si dos personas compran la última entrada a la vez, sin control se venderían dos. La base de datos usa bloqueos: mientras una transacción modifica una fila, la otra espera. SELECT ... FOR UPDATE bloquea las filas leídas hasta terminar. Los bloqueos largos o cruzados pueden causar interbloqueos.",
  k=["Los bloqueos impiden que dos transacciones modifiquen lo mismo a la vez.", "SELECT ... FOR UPDATE bloquea las filas leídas.", "Un interbloqueo ocurre cuando dos transacciones se esperan mutuamente."],
  sit="Dos usuarios intentan comprar la última entrada a la vez. ¿Qué mecanismo evita venderla dos veces?",
  cod="""START TRANSACTION;
SELECT stock FROM entradas WHERE id = 1 FOR UPDATE;   -- bloquea la fila
UPDATE entradas SET stock = stock - 1 WHERE id = 1;   -- nadie más la toca
COMMIT;                                               -- libera el bloqueo""",
  h="bloquea la fila mientras se reserva la última entrada",
  pr=("Cuando dos transacciones se esperan mutuamente ocurre un ___. (13 letras)", "interbloqueo", "deadlock"),
  pr2=("Para bloquear las filas leídas se usa FOR ___. (6 letras)", "update"),
  ec="mantener transacciones abiertas demasiado tiempo"),
K("Usuarios y permisos",
  d="cuentas de la base de datos con derechos limitados",
  u="controlar quién puede leer, escribir o administrar",
  mas="CREATE USER crea una cuenta y GRANT le da permisos concretos sobre bases o tablas: SELECT, INSERT, UPDATE, DELETE. Cada aplicación debe tener su propio usuario con solo lo imprescindible, nunca el administrador.",
  k=["GRANT concede permisos a un usuario.", "Cada aplicación debería tener su propio usuario.", "La aplicación no debe usar la cuenta administradora."],
  sit="Quieres que el usuario de la web solo pueda leer y escribir en la base de la tienda. ¿Qué haces?",
  cod="""CREATE USER 'web'@'localhost' IDENTIFIED BY 'clave-larga-y-unica';
GRANT SELECT, INSERT, UPDATE ON tienda.* TO 'web'@'localhost';
-- Sin DELETE ni DROP: si la app es atacada, el daño es menor
SHOW GRANTS FOR 'web'@'localhost';""",
  h="crea un usuario web con permisos limitados y los consulta",
  pr=("El comando que concede permisos es ___. (5 letras)", "grant"),
  pr2=("El comando que retira permisos es ___. (6 letras)", "revoke"),
  ec="usar root en la aplicación"),
K("Inyección SQL",
  d="ataque que introduce código SQL malicioso en un campo",
  u="entender uno de los ataques más peligrosos y evitarlo",
  mas="Si construyes la consulta pegando texto del usuario, alguien puede escribir ' OR '1'='1 y entrar sin contraseña, o ; DROP TABLE usuarios; y borrar datos. Nunca se concatena la entrada del usuario dentro del SQL: se usan consultas preparadas.",
  k=["La inyección SQL introduce comandos maliciosos por un campo del usuario.", "Nunca se debe concatenar texto del usuario dentro de una consulta.", "Se evita con consultas preparadas."],
  sit="Alguien escribe ' OR '1'='1 en el campo de contraseña y entra sin conocerla. ¿Qué ataque es?",
  cod="""-- MAL: la consulta se construye pegando texto del usuario
-- "SELECT * FROM usuarios WHERE correo = '" + correo + "' AND clave = '" + clave + "'"
-- Si clave = ' OR '1'='1  la condición siempre es verdadera:
SELECT * FROM usuarios WHERE correo = 'x' AND clave = '' OR '1'='1';""",
  h="muestra cómo un texto malicioso hace que la condición siempre sea verdadera",
  pr=("El ataque que mete código SQL por un campo se llama inyección ___. (3 letras)", "sql"),
  pr2=("Para evitarlo se usan consultas ___. (10 letras)", "preparadas"),
  ec="pegar directamente en el SQL el texto que escribe el usuario"),
K("Consultas preparadas",
  d="consultas con marcadores que separan el SQL de los datos",
  u="evitar la inyección SQL y reutilizar consultas",
  mas="Se escribe la consulta con marcadores (? o :nombre) y los valores se envían aparte. La base de datos trata esos valores siempre como datos, nunca como SQL. Las librerías de cada lenguaje (PDO, mysql2, SQLAlchemy) lo hacen fácil.",
  k=["Las consultas preparadas separan el SQL de los datos.", "Los valores se envían aparte con marcadores.", "Son la defensa principal contra la inyección SQL."],
  sit="Quieres que lo que escribe el usuario nunca se interprete como código SQL. ¿Qué usas?",
  cod="""-- La consulta lleva marcadores ? y los valores viajan aparte
PREPARE buscar FROM 'SELECT * FROM usuarios WHERE correo = ? AND activo = ?';
SET @c = 'ana@correo.com', @a = 1;
EXECUTE buscar USING @c, @a;       -- @c nunca se interpreta como SQL""",
  h="separa la consulta de sus valores usando marcadores",
  pr=("En una consulta preparada, los valores se sustituyen por marcadores como el signo ___. (un carácter)", "?"),
  pr2=("Los valores de una consulta preparada se tratan siempre como ___. (5 letras)", "datos"),
  ec="creer que escapar comillas a mano es suficiente"),
K("Contraseñas con hash",
  d="forma de guardar contraseñas transformadas e irreversibles",
  u="que una filtración no revele las contraseñas reales",
  mas="Nunca se guarda la contraseña en texto plano. Se guarda su hash, calculado con un algoritmo lento y seguro como bcrypt o Argon2, junto con una sal aleatoria. Para comprobar un inicio de sesión se calcula el hash de lo escrito y se compara con el guardado.",
  k=["Las contraseñas se guardan como hash, no en texto plano.", "bcrypt y Argon2 son algoritmos recomendados para contraseñas.", "Para validar se compara el hash, no la contraseña original."],
  sit="Quieres que, aunque roben tu base de datos, no se vean las contraseñas reales. ¿Qué guardas?",
  cod="""CREATE TABLE usuarios (
  id INT PRIMARY KEY AUTO_INCREMENT,
  correo VARCHAR(80) UNIQUE NOT NULL,
  clave_hash VARCHAR(255) NOT NULL    -- aquí va el hash, nunca la clave real
);
-- Ejemplo ilustrativo de lo que se guarda (bcrypt):
-- $2b$12$KIXQe6q7mN... (60 caracteres)""",
  h="reserva una columna para el hash de la contraseña en lugar de la clave real",
  pr=("Las contraseñas se guardan como ___, no en texto plano. (4 letras)", "hash"),
  pr2=("Un algoritmo recomendado para contraseñas es ___. (6 letras)", "bcrypt", "argon2"),
  ec="guardar las contraseñas en texto plano",
  err=("CREATE TABLE usuarios (\n  id INT PRIMARY KEY,\n  correo VARCHAR(80),\n  contrasena VARCHAR(30)   -- guarda la contraseña tal cual\n);", 4, "Nunca se guarda la contraseña en texto plano: se debe guardar un hash.")),
K("Importar y exportar datos",
  d="mover datos hacia y desde la base mediante archivos",
  u="cargar datos masivos o llevarlos a otras herramientas",
  mas="Con LOAD DATA INFILE o el asistente de Workbench importas un CSV a una tabla. Con SELECT ... INTO OUTFILE o mysqldump exportas. El formato CSV lo abre cualquier hoja de cálculo. Revisa la codificación (UTF-8) y valida los datos antes de importarlos.",
  k=["Los archivos CSV permiten mover datos entre herramientas.", "mysqldump exporta una base completa.", "Conviene revisar la codificación UTF-8 al importar."],
  sit="Tienes 5000 alumnos en un archivo CSV y quieres cargarlos en una tabla. ¿Qué haces?",
  cod="""LOAD DATA LOCAL INFILE 'alumnos.csv'
INTO TABLE alumnos
FIELDS TERMINATED BY ','            -- columnas separadas por coma
LINES TERMINATED BY '\\n'
IGNORE 1 LINES                       -- salta la fila de títulos
(nombre, curso, nota);""",
  h="carga un archivo CSV en una tabla saltando la fila de títulos",
  pr=("Un archivo de datos separados por comas es un ___. (3 letras)", "csv"),
  pr2=("La herramienta que exporta bases completas es ___. (9 letras)", "mysqldump"),
  ec="importar datos sin revisarlos antes"),
K("Procedimientos almacenados",
  d="bloques de SQL guardados en la base que se ejecutan por nombre",
  u="reutilizar lógica y reducir viajes entre aplicación y base",
  mas="Un procedimiento se crea con CREATE PROCEDURE, recibe parámetros y se lanza con CALL. Es útil para operaciones repetidas o con varios pasos. A cambio, la lógica queda dentro de la base y es más difícil de versionar que el código de la aplicación.",
  k=["Un procedimiento almacenado se ejecuta con CALL.", "Puede recibir parámetros.", "La lógica queda guardada dentro de la base de datos."],
  sit="Quieres guardar en la base unos pasos repetidos para ejecutarlos con una sola llamada. ¿Qué creas?",
  cod="""DELIMITER //
CREATE PROCEDURE subir_nota(IN p_id INT, IN p_extra DECIMAL(4,2))
BEGIN
  UPDATE alumnos SET nota = LEAST(10, nota + p_extra) WHERE id = p_id;
END //
DELIMITER ;
CALL subir_nota(3, 0.5);     -- se ejecuta por su nombre""",
  h="guarda una operación con parámetros y la ejecuta con CALL",
  pr=("El comando que ejecuta un procedimiento almacenado es ___. (4 letras)", "call"),
  pr2=("El comando que crea un procedimiento es CREATE ___. (9 letras)", "procedure"),
  ec="esconder demasiada lógica del negocio dentro de la base"),
K("Triggers",
  d="código que se ejecuta automáticamente ante un cambio en una tabla",
  u="automatizar acciones como registrar auditorías",
  mas="Un trigger se asocia a una tabla y a un evento (INSERT, UPDATE o DELETE), antes o después. Por ejemplo, guardar en una tabla de historial cada vez que cambia el precio de un producto. Úsalos con moderación: los efectos ocultos son difíciles de depurar.",
  k=["Un trigger se ejecuta solo cuando ocurre un evento en la tabla.", "Puede ejecutarse antes o después del evento.", "Los triggers ocultos pueden dificultar la depuración."],
  sit="Quieres que cada vez que cambie el precio de un producto quede registrado automáticamente. ¿Qué usas?",
  cod="""CREATE TRIGGER guardar_historial
AFTER UPDATE ON productos
FOR EACH ROW
  INSERT INTO historial_precios (producto_id, precio_anterior, cambiado)
  VALUES (OLD.id, OLD.precio, NOW());   -- OLD: valores antes del cambio""",
  h="registra automáticamente el precio anterior cada vez que cambia",
  pr=("El código que se ejecuta automáticamente ante un cambio se llama ___. (7 letras)", "trigger", "disparador"),
  pr2=("En un trigger, OLD contiene los valores ___ del cambio. (5 letras)", "antes"),
  ec="llenar la base de triggers que nadie recuerda"),
K("Borrado en cascada",
  d="regla que decide qué pasa con los hijos al borrar un padre",
  u="evitar datos huérfanos al borrar registros relacionados",
  mas="Con ON DELETE CASCADE, al borrar un cliente se borran también sus pedidos. Con ON DELETE SET NULL, los pedidos quedan sin cliente. Con RESTRICT (por defecto) no te deja borrar al cliente mientras tenga pedidos. Elige según el significado del negocio.",
  k=["ON DELETE CASCADE borra también los registros hijos.", "ON DELETE SET NULL deja la clave foránea vacía.", "RESTRICT impide borrar un padre con hijos."],
  sit="Quieres que, al borrar un cliente, desaparezcan también todos sus pedidos. ¿Qué regla usas?",
  cod="""CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  cliente_id INT,
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    ON DELETE CASCADE          -- borra también los pedidos del cliente
);
DELETE FROM clientes WHERE id = 3;   -- sus pedidos se eliminan solos""",
  h="borra los pedidos automáticamente cuando se borra su cliente",
  pr=("La regla que borra también los registros hijos es ON DELETE ___. (7 letras)", "cascade"),
  pr2=("La regla por defecto que impide borrar un padre con hijos es ___. (8 letras)", "restrict"),
  ec="usar CASCADE sin pensar qué datos se perderán"),
K("Borrado lógico",
  d="técnica de marcar un registro como eliminado sin borrarlo",
  u="poder recuperar datos y conservar el historial",
  mas="En lugar de DELETE, se añade una columna como eliminado o borrado_en y se marca. Las consultas habituales filtran WHERE eliminado = 0. Permite deshacer errores y mantener el historial, a costa de tener que recordar el filtro siempre.",
  k=["El borrado lógico marca el registro sin eliminarlo.", "Permite recuperar datos borrados por error.", "Las consultas deben filtrar los registros marcados."],
  sit="Quieres «borrar» un usuario pero poder recuperarlo después si se arrepiente. ¿Qué técnica usas?",
  cod="""ALTER TABLE usuarios ADD eliminado BOOLEAN DEFAULT FALSE;
UPDATE usuarios SET eliminado = TRUE WHERE id = 9;     -- «borrado» lógico
SELECT * FROM usuarios WHERE eliminado = FALSE;        -- el resto de consultas lo filtran""",
  h="marca a un usuario como eliminado sin borrar sus datos",
  pr=("En el borrado ___, los datos se marcan pero no se eliminan. (6 letras)", "lógico", "logico"),
  pr2=("Las consultas deben filtrar con WHERE eliminado = ___. (5 letras)", "false", "0"),
  ec="olvidar filtrar los registros eliminados en las consultas"),
K("Optimizar consultas",
  d="conjunto de buenas prácticas para que las consultas sean rápidas",
  u="mantener la aplicación ágil cuando crecen los datos",
  mas="Pide solo las columnas necesarias, filtra con WHERE, usa índices en columnas de búsqueda, evita funciones sobre columnas indexadas en el WHERE y limita resultados con LIMIT. Mide con EXPLAIN antes y después. Optimiza solo lo que de verdad es lento.",
  k=["Conviene pedir solo las columnas y filas necesarias.", "Los índices aceleran las columnas que se buscan.", "Hay que medir con EXPLAIN antes y después de optimizar."],
  sit="Tu consulta tarda 5 segundos y quieres que sea rápida con buenas prácticas. ¿Qué haces?",
  cod="""-- Lento: trae todo y aplica una función a la columna indexada
SELECT * FROM pedidos WHERE YEAR(fecha) = 2026;
-- Rápido: columnas necesarias y condición que usa el índice
SELECT id, total FROM pedidos
WHERE fecha >= '2026-01-01' AND fecha < '2027-01-01';""",
  h="reescribe una consulta lenta para que aproveche el índice de fecha",
  pr=("Para ver el plan de una consulta antes de optimizarla se usa ___. (7 letras)", "explain"),
  pr2=("Conviene pedir solo las ___ necesarias en vez de SELECT *. (8 letras)", "columnas"),
  ec="optimizar a ciegas sin medir"),
K("Elegir una base de datos",
  d="criterio para decidir qué tipo de base usar en un proyecto",
  u="no usar una herramienta equivocada para el problema",
  mas="Para datos con relaciones claras y transacciones, una base relacional (MySQL, PostgreSQL). Para documentos flexibles, MongoDB. Para caché y datos temporales muy rápidos, Redis. Para pocos datos en una app pequeña, SQLite. Empieza simple y cambia solo si lo necesitas.",
  k=["Las bases relacionales sirven para datos con relaciones y transacciones.", "Redis es ideal para caché y datos temporales.", "SQLite es adecuada para proyectos pequeños."],
  sit="Vas a crear una tienda con clientes, pedidos y pagos que necesitan transacciones seguras. ¿Qué tipo de base eliges?",
  cod="""-- Guía rápida (en comentarios):
-- Tienda, banco, escuela ............ relacional: MySQL o PostgreSQL
-- Perfiles con campos cambiantes .... documental: MongoDB
-- Caché, sesiones, contadores ....... clave-valor: Redis
-- App móvil pequeña sin servidor .... SQLite
SELECT 'empieza simple' AS consejo;""",
  h="recomienda un tipo de base de datos según el proyecto",
  pr=("Para una tienda con transacciones seguras conviene una base ___. (10 letras)", "relacional"),
  pr2=("Una base muy rápida para caché y sesiones es ___. (5 letras)", "redis"),
  ec="elegir una base solo porque está de moda"),
K("Migraciones de esquema",
  d="cambios de estructura guardados en archivos versionados",
  u="actualizar la base de datos de forma ordenada y repetible",
  mas="En vez de modificar las tablas a mano, cada cambio (añadir una columna, crear una tabla) se escribe en un archivo numerado: 001_crear_clientes.sql, 002_añadir_telefono.sql. Así todo el equipo y todos los servidores aplican los mismos cambios en el mismo orden, y puedes ver el historial en Git.",
  k=["Una migración es un cambio de estructura guardado en un archivo.", "Las migraciones se aplican siempre en el mismo orden.", "Permiten que todos los entornos tengan la misma estructura."],
  sit="Quieres que todo el equipo aplique los mismos cambios de estructura en el mismo orden. ¿Qué usas?",
  cod="""-- Archivo 001_crear_clientes.sql
CREATE TABLE clientes (id INT PRIMARY KEY AUTO_INCREMENT, nombre VARCHAR(50));
-- Archivo 002_añadir_telefono.sql
ALTER TABLE clientes ADD telefono VARCHAR(15);
-- Cada archivo se ejecuta una sola vez y en orden""",
  h="describe dos cambios de estructura guardados en archivos numerados",
  pr=("Los archivos de migración se aplican siempre en el mismo ___. (5 letras)", "orden"),
  pr2=("Los archivos de migración suelen guardarse en un sistema de control de versiones como ___. (3 letras)", "git"),
  ec="modificar la estructura a mano en producción sin dejar registro"),
K("Proyecto base de una tienda",
  d="diseño completo de una base de datos para una tienda en línea",
  u="practicar todo lo aprendido en un caso real",
  mas="Para cerrar el curso, diseña la base de una tienda: clientes, productos, pedidos y detalle de pedido. Dibuja el diagrama, crea las tablas con sus claves y restricciones, inserta datos de prueba y responde preguntas con consultas: ventas por mes, clientes sin pedidos, productos más vendidos.",
  k=["Un proyecto completo parte de un diagrama y termina con consultas.", "Una tienda necesita clientes, productos, pedidos y detalle de pedido.", "Los datos de prueba permiten comprobar que las consultas funcionan."],
  sit="Quieres cerrar el curso diseñando una base completa para una tienda en línea. ¿Qué construyes?",
  cod="""CREATE TABLE clientes  (id INT PRIMARY KEY AUTO_INCREMENT, nombre VARCHAR(50) NOT NULL, correo VARCHAR(80) UNIQUE);
CREATE TABLE productos (id INT PRIMARY KEY AUTO_INCREMENT, nombre VARCHAR(50), precio DECIMAL(8,2));
CREATE TABLE pedidos   (id INT PRIMARY KEY AUTO_INCREMENT, cliente_id INT, fecha DATE,
                        FOREIGN KEY (cliente_id) REFERENCES clientes(id));
CREATE TABLE detalle   (pedido_id INT, producto_id INT, cantidad INT,
                        PRIMARY KEY (pedido_id, producto_id));
-- Pregunta: ¿cuánto vendió cada producto?
SELECT p.nombre, SUM(d.cantidad) AS vendidas
FROM detalle d JOIN productos p ON p.id = d.producto_id
GROUP BY p.nombre ORDER BY vendidas DESC;""",
  h="crea las cuatro tablas de una tienda y consulta cuánto vendió cada producto",
  pr=("Para cerrar el curso conviene hacer un ___ completo. (8 letras)", "proyecto"),
  pr2=("Antes de crear las tablas conviene dibujar el diagrama ___. (2 letras)", "er"),
  ec="empezar a crear tablas sin diseñar antes"),
]
