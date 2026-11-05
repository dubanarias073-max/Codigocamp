"""Bases de datos · Etapa 2: modelado de datos."""
from ..generador import K

LISTA = [
K("Entidad",
  d="cosa del mundo real sobre la que se guardan datos",
  u="decidir qué tablas necesita una base de datos",
  mas="Antes de crear tablas se piensa en las entidades: en una escuela serán alumno, curso y profesor. Cada entidad suele convertirse en una tabla. Un buen modelo empieza identificando bien las entidades.",
  k=["Una entidad es algo sobre lo que se guarda información.", "Cada entidad suele convertirse en una tabla.", "El modelado empieza identificando las entidades."],
  sit="Estás diseñando la base de una escuela y piensas en alumno, curso y profesor. ¿Qué estás identificando?",
  cod="""-- Cada entidad se convierte en una tabla
CREATE TABLE alumnos    (id INT PRIMARY KEY, nombre VARCHAR(40));
CREATE TABLE cursos     (id INT PRIMARY KEY, titulo VARCHAR(40));
CREATE TABLE profesores (id INT PRIMARY KEY, nombre VARCHAR(40));""",
  h="crea una tabla por cada entidad de una escuela",
  pr=("En una escuela, «alumno» o «curso» son ___. (9 letras)", "entidades"),
  pr2=("Cada entidad suele convertirse en una ___. (5 letras)", "tabla"),
  ec="meter varias entidades distintas en la misma tabla"),
K("Atributo",
  d="característica que describe a una entidad",
  u="decidir qué columnas tendrá cada tabla",
  mas="Los atributos del alumno pueden ser nombre, fecha de nacimiento y correo. Cada atributo se convierte en una columna. Conviene guardar datos simples e indivisibles: separa nombre y apellido en vez de uno solo.",
  k=["Un atributo describe una característica de una entidad.", "Cada atributo se convierte en una columna.", "Es mejor guardar datos simples en columnas separadas."],
  sit="Quieres decidir qué datos guardar de cada alumno: nombre, correo y fecha de nacimiento. ¿Qué defines?",
  cod="""CREATE TABLE alumnos (
  id INT PRIMARY KEY,
  nombre VARCHAR(40),       -- atributo: nombre
  apellido VARCHAR(40),     -- atributo: apellido (separado)
  correo VARCHAR(80),       -- atributo: correo
  nacimiento DATE           -- atributo: fecha de nacimiento
);""",
  h="define cinco atributos de un alumno como columnas separadas",
  pr=("Cada atributo de una entidad se convierte en una ___. (7 letras)", "columna"),
  pr2=("Conviene guardar nombre y apellido en columnas ___. (9 letras)", "separadas"),
  ec="guardar nombre y apellido juntos en una sola columna"),
K("Relación entre entidades",
  d="vínculo que une a dos entidades",
  u="reflejar cómo se conectan los datos en la vida real",
  mas="Un alumno se matricula en cursos, un cliente hace pedidos, un autor escribe libros. Esas conexiones son relaciones. Las relaciones se representan con verbos y luego se traducen en claves que conectan las tablas.",
  k=["Una relación une dos entidades.", "Las relaciones suelen describirse con verbos.", "Las relaciones se traducen en claves entre tablas."],
  sit="Quieres expresar que un cliente «realiza» pedidos, conectando dos entidades. ¿Qué defines?",
  cod="""-- clientes ---realiza---> pedidos
-- La relación se guarda con un campo que apunta al cliente
CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  cliente_id INT           -- aquí vive la relación
);""",
  h="expresa que un pedido pertenece a un cliente con un campo que lo apunta",
  pr=("Una conexión entre dos entidades es una ___. (8 letras)", "relación", "relacion"),
  pr2=("Las relaciones suelen describirse con un ___. (5 letras)", "verbo"),
  ec="olvidar relacionar las tablas y duplicar datos"),
K("Cardinalidad",
  d="número de elementos de una entidad que se relacionan con otra",
  u="saber si una relación es de uno a uno, uno a muchos o muchos a muchos",
  mas="Pregúntate dos veces. ¿Un cliente puede tener varios pedidos? Sí. ¿Un pedido puede tener varios clientes? No. Entonces es una relación de uno a muchos. Esa respuesta decide dónde se coloca la clave que conecta las tablas.",
  k=["La cardinalidad indica cuántos elementos se relacionan.", "Las tres cardinalidades son 1:1, 1:N y N:M.", "La cardinalidad decide dónde va la clave de conexión."],
  sit="Te preguntas cuántos pedidos puede tener un cliente y cuántos clientes un pedido. ¿Qué analizas?",
  cod="""-- Pregunta 1: ¿un cliente tiene varios pedidos?  SÍ  (muchos)
-- Pregunta 2: ¿un pedido tiene varios clientes?  NO  (uno)
-- Resultado: relación UNO a MUCHOS (1:N)
SELECT 'cliente 1 --- N pedidos' AS cardinalidad;""",
  h="razona la cardinalidad entre clientes y pedidos con dos preguntas",
  pr=("Las tres cardinalidades son 1:1, 1:N y ___. (3 caracteres)", "n:m", "m:n"),
  pr2=("La cardinalidad indica cuántos ___ se relacionan. (9 letras: elementos)", "elementos"),
  ec="decidir la cardinalidad sin hacerse las dos preguntas"),
K("Relación uno a muchos",
  d="relación donde un elemento se conecta con varios de otra tabla",
  u="modelar casos como cliente y pedidos",
  mas="Es la relación más común. La clave foránea se coloca en el lado «muchos»: cada pedido guarda el id de su cliente. Así un cliente tiene muchos pedidos y cada pedido pertenece a un solo cliente.",
  k=["En 1:N, la clave foránea va en la tabla del lado «muchos».", "Un cliente puede tener muchos pedidos.", "Cada pedido pertenece a un solo cliente."],
  sit="Quieres modelar que un autor escribe muchos libros, pero cada libro tiene un único autor. ¿Qué relación usas?",
  cod="""CREATE TABLE autores (id INT PRIMARY KEY, nombre VARCHAR(40));
CREATE TABLE libros (
  id INT PRIMARY KEY,
  titulo VARCHAR(60),
  autor_id INT,                          -- la clave va en el lado «muchos»
  FOREIGN KEY (autor_id) REFERENCES autores(id)
);""",
  h="conecta muchos libros con un único autor mediante clave foránea",
  pr=("En una relación 1:N, la clave foránea va en la tabla del lado ___. (6 letras)", "muchos"),
  pr2=("Un cliente puede tener muchos ___. (7 letras: pedidos)", "pedidos"),
  ec="colocar la clave foránea en el lado «uno»"),
K("Relación muchos a muchos",
  d="relación donde ambos lados pueden tener varios elementos",
  u="modelar casos como alumnos y cursos",
  mas="Un alumno se apunta a varios cursos y un curso tiene varios alumnos. Esta relación no se puede resolver con una sola clave: se necesita una tercera tabla intermedia que guarde las parejas alumno-curso.",
  k=["En N:M ambos lados pueden tener varios elementos.", "Una relación N:M necesita una tabla intermedia.", "Alumnos y cursos suelen formar una relación N:M."],
  sit="Un alumno puede matricularse en varios cursos y un curso tiene varios alumnos. ¿Qué relación es?",
  cod="""-- alumnos N --- M cursos  se resuelve con una tabla intermedia
CREATE TABLE matriculas (
  alumno_id INT,
  curso_id  INT,
  PRIMARY KEY (alumno_id, curso_id)   -- cada pareja solo una vez
);""",
  h="resuelve una relación de muchos a muchos con una tabla de parejas",
  pr=("Una relación N:M necesita una tabla ___. (11 letras)", "intermedia"),
  pr2=("Alumnos y cursos forman una relación ___:M. (una letra)", "n"),
  ec="intentar resolver N:M con una sola clave foránea"),
K("Tabla intermedia",
  d="tabla que une otras dos con una clave de cada una",
  u="guardar las parejas de una relación muchos a muchos",
  mas="La tabla intermedia (también llamada de unión o asociativa) tiene dos claves foráneas, una por cada tabla. Puede añadir datos propios de la relación, como la nota del alumno en ese curso o la fecha de matrícula.",
  k=["La tabla intermedia tiene una clave foránea por cada tabla unida.", "Puede guardar datos propios de la relación.", "Se usa para relaciones muchos a muchos."],
  sit="Quieres guardar la nota que cada alumno obtuvo en cada curso. ¿Dónde la pones?",
  cod="""CREATE TABLE notas (
  alumno_id INT,
  curso_id  INT,
  nota DECIMAL(4,2),                  -- dato propio de la relación
  PRIMARY KEY (alumno_id, curso_id),
  FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
  FOREIGN KEY (curso_id)  REFERENCES cursos(id)
);""",
  h="guarda la nota de cada alumno en cada curso en una tabla de unión",
  pr=("La tabla intermedia tiene una clave ___ por cada tabla que une. (8 letras)", "foránea", "foranea"),
  pr2=("Otro nombre de tabla intermedia es tabla de ___. (5 letras)", "unión", "union"),
  ec="guardar la nota en la tabla de alumnos"),
K("Relación uno a uno",
  d="relación donde cada elemento se conecta con uno solo del otro lado",
  u="separar datos opcionales o delicados en otra tabla",
  mas="Un usuario tiene un solo perfil y un perfil pertenece a un solo usuario. A menudo se unen en una sola tabla, pero se separan cuando los datos son opcionales, sensibles (como credenciales) o muy extensos. La clave foránea lleva UNIQUE para asegurar el uno a uno.",
  k=["En 1:1 cada elemento se conecta con uno solo del otro lado.", "Se separa en otra tabla cuando los datos son opcionales o sensibles.", "Una clave foránea UNIQUE garantiza el uno a uno."],
  sit="Cada usuario tiene exactamente un perfil con datos opcionales y cada perfil es de un único usuario. ¿Qué relación es?",
  cod="""CREATE TABLE perfiles (
  id INT PRIMARY KEY,
  usuario_id INT UNIQUE,            -- UNIQUE asegura el uno a uno
  biografia TEXT,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);""",
  h="vincula cada perfil con un único usuario",
  pr=("Para garantizar una relación 1:1, la clave foránea debe ser ___. (6 letras)", "unique", "única", "unica"),
  pr2=("Un usuario tiene ___ perfil en una relación uno a uno. (un número)", "1", "un", "uno"),
  ec="olvidar UNIQUE y permitir varios perfiles por usuario"),
K("Diagrama entidad-relación",
  d="dibujo que muestra entidades, atributos y relaciones",
  u="planificar la base de datos antes de crearla",
  mas="Se dibuja con rectángulos para las entidades, óvalos para los atributos y rombos o líneas para las relaciones. Un buen diagrama se hace en papel o con herramientas como Workbench o dbdiagram.io antes de escribir una sola línea de SQL.",
  k=["Un diagrama ER dibuja entidades y relaciones.", "Se hace antes de crear las tablas.", "Workbench puede generar diagramas ER."],
  sit="Quieres dibujar las entidades y sus relaciones antes de crear ninguna tabla. ¿Qué haces?",
  cod="""-- Diagrama en texto:
-- [clientes] 1 ----- N [pedidos] N ----- M [productos]
-- Cada [caja] sería una tabla; las líneas, claves foráneas.
SELECT 'primero se dibuja, luego se crea' AS consejo;""",
  h="describe en texto un diagrama con tres entidades y sus relaciones",
  pr=("Las siglas del diagrama que muestra entidades y relaciones son ___. (2 letras)", "er"),
  pr2=("El diagrama se hace ___ de crear las tablas. (5 letras)", "antes"),
  ec="empezar a crear tablas sin planificar el modelo"),
K("Clave foránea",
  d="columna que apunta a la clave primaria de otra tabla",
  u="conectar tablas y mantener los datos coherentes",
  mas="La clave foránea (FOREIGN KEY) guarda el id de otra tabla: pedidos.cliente_id apunta a clientes.id. El gestor impide guardar un pedido de un cliente que no existe y también impide borrar un cliente que tiene pedidos.",
  k=["Una clave foránea apunta a la clave primaria de otra tabla.", "Impide guardar valores que no existen en la tabla referenciada.", "Mantiene la integridad entre tablas."],
  sit="Quieres impedir que se guarde un pedido de un cliente que no existe. ¿Qué defines?",
  cod="""CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  cliente_id INT,
  total DECIMAL(8,2),
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)   -- apunta a clientes
);
INSERT INTO pedidos VALUES (1, 9999, 50);   -- falla si el cliente 9999 no existe""",
  h="impide guardar un pedido que apunta a un cliente inexistente",
  pr=("La clave que apunta a la clave primaria de otra tabla es la clave ___. (7 letras)", "foránea", "foranea"),
  pr2=("En inglés, clave foránea se escribe FOREIGN ___. (3 letras)", "key"),
  ec="guardar ids de clientes que no existen",
  err=("CREATE TABLE pedidos (\n  id INT PRIMARY KEY,\n  cliente_id INT,\n  FOREIGN KEY cliente_id REFERENCES clientes(id)\n);", 4, "Faltan los paréntesis: FOREIGN KEY (cliente_id) REFERENCES clientes(id).")),
K("Tipos numéricos",
  d="tipos de dato para guardar números enteros y decimales",
  u="elegir cómo guardar cantidades, edades y precios",
  mas="INT guarda enteros (edades, cantidades). DECIMAL(8,2) guarda números con decimales exactos, ideal para dinero: 8 dígitos en total, 2 de ellos decimales. FLOAT y DOUBLE son aproximados y no se recomiendan para dinero.",
  k=["INT guarda números enteros.", "DECIMAL guarda decimales exactos y es adecuado para dinero.", "FLOAT guarda decimales aproximados."],
  sit="Quieres guardar precios con céntimos sin errores de redondeo. ¿Qué tipo usas?",
  cod="""CREATE TABLE productos (
  id INT PRIMARY KEY,
  stock INT,                -- entero: 25
  precio DECIMAL(8,2),      -- exacto: 1234.56
  peso FLOAT                -- aproximado: 0.350
);""",
  h="guarda enteros, precios exactos y pesos aproximados",
  pr=("El tipo para números enteros es ___. (3 letras)", "int"),
  pr2=("El tipo exacto recomendado para dinero es ___. (7 letras)", "decimal"),
  ec="usar FLOAT para guardar dinero"),
K("Tipos de texto",
  d="tipos de dato para guardar cadenas de caracteres",
  u="guardar nombres, direcciones y descripciones",
  mas="CHAR(n) reserva siempre n caracteres (útil para códigos fijos). VARCHAR(n) guarda hasta n caracteres y ocupa solo lo necesario: es el más común. TEXT sirve para textos largos como biografías o comentarios.",
  k=["VARCHAR guarda texto de longitud variable hasta un máximo.", "CHAR reserva una longitud fija.", "TEXT sirve para textos largos."],
  sit="Quieres guardar nombres de hasta 50 caracteres ocupando solo el espacio necesario. ¿Qué tipo usas?",
  cod="""CREATE TABLE usuarios (
  id INT PRIMARY KEY,
  pais CHAR(2),             -- siempre 2 letras: PE, MX
  nombre VARCHAR(50),       -- hasta 50 caracteres
  biografia TEXT            -- texto largo
);""",
  h="elige el tipo de texto adecuado para código, nombre y biografía",
  pr=("El tipo de texto de longitud variable más común es ___. (7 letras)", "varchar"),
  pr2=("Para textos muy largos se usa el tipo ___. (4 letras)", "text"),
  ec="usar VARCHAR(5) para un campo que necesita más caracteres"),
K("Fechas y horas",
  d="tipos de dato para guardar fechas y momentos exactos",
  u="registrar cuándo ocurre algo",
  mas="DATE guarda solo la fecha (2026-03-15). TIME guarda una hora y DATETIME o TIMESTAMP guardan fecha y hora juntas. Nunca guardes fechas como texto: con el tipo correcto puedes ordenar, restar y filtrar fechas.",
  k=["DATE guarda solo la fecha.", "DATETIME guarda fecha y hora.", "No conviene guardar fechas como texto."],
  sit="Quieres registrar el momento exacto, con fecha y hora, en que se hizo un pedido. ¿Qué tipo usas?",
  cod="""CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  fecha_entrega DATE,                          -- solo día: 2026-03-15
  creado DATETIME DEFAULT CURRENT_TIMESTAMP    -- día y hora automáticos
);""",
  h="guarda la fecha de entrega y el momento exacto de creación del pedido",
  pr=("El tipo que guarda solo la fecha es ___. (4 letras)", "date"),
  pr2=("El tipo que guarda fecha y hora juntas es ___. (8 letras)", "datetime"),
  ec="guardar fechas como texto"),
K("Valores booleanos",
  d="tipo de dato que guarda verdadero o falso",
  u="guardar estados como activo, pagado o leído",
  mas="MySQL no tiene un tipo booleano propio: BOOLEAN es un alias de TINYINT(1), donde 0 es falso y 1 es verdadero. Otras bases como PostgreSQL sí tienen BOOLEAN. Se usa para banderas como activo, verificado o eliminado.",
  k=["En MySQL, BOOLEAN equivale a TINYINT(1).", "El valor 0 significa falso y el 1 verdadero.", "Los booleanos guardan estados como activo o pagado."],
  sit="Quieres guardar si un usuario está activo o no. ¿Qué tipo usas?",
  cod="""CREATE TABLE usuarios (
  id INT PRIMARY KEY,
  activo BOOLEAN DEFAULT TRUE       -- 1 = activo, 0 = inactivo
);
INSERT INTO usuarios (id, activo) VALUES (1, FALSE);""",
  h="guarda con un booleano si un usuario está activo o no",
  pr=("En MySQL, el valor 0 de un booleano significa ___. (5 letras)", "falso", "false"),
  pr2=("En MySQL, BOOLEAN equivale a TINYINT(___). (un número)", "1"),
  ec="guardar «sí» y «no» como texto"),
K("NOT NULL",
  d="restricción que obliga a que la columna tenga un valor",
  u="evitar campos importantes vacíos",
  mas="NULL significa «sin valor» y no es lo mismo que cero o texto vacío. Si una columna es NOT NULL, intentar insertar una fila sin ese dato produce un error. Úsalo en datos imprescindibles como el nombre o el correo.",
  k=["NOT NULL impide dejar la columna sin valor.", "NULL significa ausencia de valor.", "NULL no es lo mismo que cero ni que texto vacío."],
  sit="Quieres que sea obligatorio escribir el nombre al insertar una fila. ¿Qué restricción usas?",
  cod="""CREATE TABLE clientes (
  id INT PRIMARY KEY,
  nombre VARCHAR(40) NOT NULL,     -- obligatorio
  telefono VARCHAR(15)             -- opcional: puede ser NULL
);
INSERT INTO clientes (id) VALUES (1);   -- falla: falta el nombre""",
  h="exige nombre obligatorio y deja el teléfono como opcional",
  pr=("La restricción que obliga a tener valor es NOT ___. (4 letras)", "null"),
  pr2=("NULL significa ausencia de ___. (5 letras)", "valor"),
  ec="confundir NULL con cero o con texto vacío"),
K("DEFAULT",
  d="valor automático que se usa cuando no se indica otro",
  u="evitar escribir siempre los mismos datos",
  mas="Si no indicas un valor al insertar, la columna toma el DEFAULT: un estado «pendiente», un contador en 0 o la fecha actual. Reduce errores y simplifica las inserciones.",
  k=["DEFAULT define el valor por omisión de una columna.", "Se usa si al insertar no se indica un valor.", "Puede ser un texto, un número o la fecha actual."],
  sit="Quieres que todo pedido nuevo tenga el estado «pendiente» si no se indica otro. ¿Qué usas?",
  cod="""CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  estado VARCHAR(15) DEFAULT 'pendiente',   -- valor por defecto
  creado DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO pedidos (id) VALUES (1);        -- estado = 'pendiente'""",
  h="asigna automáticamente un estado y una fecha a cada pedido nuevo",
  pr=("El valor que se usa si no se indica otro se define con ___. (7 letras)", "default"),
  pr2=("La fecha y hora actuales se obtienen con CURRENT____. (9 letras)", "timestamp"),
  ec="olvidar el DEFAULT y obligar a escribir siempre el mismo valor"),
K("AUTO_INCREMENT",
  d="opción que numera automáticamente cada nueva fila",
  u="generar ids únicos sin escribirlos a mano",
  mas="Con AUTO_INCREMENT en la clave primaria, MySQL asigna 1, 2, 3… a cada fila nueva. Nunca reutiliza un número ya usado aunque borres filas. Al insertar, simplemente no indicas el id.",
  k=["AUTO_INCREMENT numera las filas automáticamente.", "Se suele usar en la clave primaria.", "Al insertar no hace falta indicar el id."],
  sit="Quieres que cada usuario nuevo reciba su id solo, sin escribirlo. ¿Qué opción usas?",
  cod="""CREATE TABLE usuarios (
  id INT PRIMARY KEY AUTO_INCREMENT,   -- 1, 2, 3...
  nombre VARCHAR(40)
);
INSERT INTO usuarios (nombre) VALUES ('Ana');    -- id = 1
INSERT INTO usuarios (nombre) VALUES ('Luis');   -- id = 2""",
  h="deja que MySQL asigne el id de cada usuario nuevo",
  pr=("La opción que numera filas automáticamente es ____INCREMENT. (4 letras)", "auto"),
  pr2=("AUTO_INCREMENT se suele usar en la clave ___. (8 letras)", "primaria"),
  ec="escribir ids a mano y provocar repetidos",
  err=("CREATE TABLE usuarios (\n  id INT AUTO_INCREMENT,\n  nombre VARCHAR(40)\n);", 2, "Una columna AUTO_INCREMENT debe ser clave primaria: id INT PRIMARY KEY AUTO_INCREMENT.")),
K("Redundancia de datos",
  d="repetición innecesaria de la misma información",
  u="detectar tablas mal diseñadas",
  mas="Si en la tabla pedidos escribes el nombre y la dirección del cliente en cada pedido, repites datos. Si el cliente cambia de dirección tendrías que corregir muchas filas y podrían quedar valores distintos. La solución es guardar al cliente una sola vez y referenciarlo.",
  k=["La redundancia es repetir los mismos datos sin necesidad.", "La redundancia dificulta las actualizaciones y crea inconsistencias.", "Se evita guardando cada dato una sola vez y referenciándolo."],
  sit="El nombre y la dirección de un cliente están repetidos en cada uno de sus pedidos. ¿Qué problema tiene el diseño?",
  cod="""-- MAL: se repite el cliente en cada pedido
-- pedidos(id, cliente_nombre, cliente_direccion, total)
-- BIEN: el cliente se guarda una sola vez
-- clientes(id, nombre, direccion)
-- pedidos(id, cliente_id, total)
SELECT 'guarda cada dato una sola vez' AS regla;""",
  h="contrasta una tabla con datos repetidos y otra con datos guardados una sola vez",
  pr=("Repetir innecesariamente la misma información es ___. (11 letras: redundancia)", "redundancia"),
  pr2=("Cada dato debería guardarse una sola ___. (3 letras)", "vez"),
  ec="copiar los datos del cliente en cada pedido"),
K("Normalización",
  d="proceso de organizar las tablas para evitar repeticiones y errores",
  u="obtener un diseño limpio y fácil de mantener",
  mas="La primera forma normal pide valores simples en cada celda (nada de listas). La segunda, que todo dependa de la clave completa. La tercera, que las columnas no dependan de otras columnas no clave. Con tres formas normales la mayoría de los diseños quedan sólidos.",
  k=["La normalización organiza las tablas para evitar redundancia.", "La primera forma normal exige un valor simple por celda.", "Las tres primeras formas normales bastan en la mayoría de casos."],
  sit="Quieres reorganizar tus tablas siguiendo reglas para eliminar repeticiones. ¿Qué proceso aplicas?",
  cod="""-- Primera forma normal: nada de listas en una celda
-- MAL:  alumnos(id, nombre, cursos = 'HTML, CSS, SQL')
-- BIEN: una fila por cada pareja alumno-curso
-- matriculas(alumno_id, curso_id)
SELECT '1FN: un valor simple por celda' AS regla;""",
  h="separa una lista guardada en una celda en filas independientes",
  pr=("El proceso de organizar tablas para evitar repeticiones es la ___. (13 letras)", "normalización", "normalizacion"),
  pr2=("La primera forma normal exige un valor ___ por celda. (6 letras)", "simple", "único", "unico"),
  ec="guardar listas separadas por comas en una sola celda"),
K("Convenciones de nombres",
  d="reglas para nombrar tablas y columnas de forma coherente",
  u="mantener la base ordenada y fácil de entender",
  mas="Elige un estilo y úsalo siempre: minúsculas con guion bajo (fecha_pedido), tablas en plural (clientes) o singular, pero sin mezclar. Evita espacios, tildes y palabras reservadas como order o group. La clave foránea suele llamarse tabla_id.",
  k=["Los nombres deben seguir un estilo coherente.", "Evita espacios, tildes y palabras reservadas.", "La clave foránea suele llamarse tabla_id."],
  sit="Quieres que todos los nombres de tablas y columnas sigan el mismo estilo claro. ¿Qué defines?",
  cod="""-- Buen estilo: minúsculas, guion bajo y sin tildes
CREATE TABLE clientes (id INT PRIMARY KEY, nombre_completo VARCHAR(80));
CREATE TABLE pedidos  (id INT PRIMARY KEY, cliente_id INT, fecha_pedido DATE);
-- Mal estilo: 'Nombre Completo', ÓrdenDelCliente, order""",
  h="usa nombres en minúsculas con guion bajo y claves tabla_id",
  pr=("Los nombres de columnas suelen escribirse en minúsculas con guion ___. (4 letras)", "bajo"),
  pr2=("La clave foránea hacia clientes suele llamarse cliente___. (3 caracteres)", "_id"),
  ec="usar espacios, tildes o palabras reservadas en los nombres"),
]
