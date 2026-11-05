// Lecciones de PHP. Para añadir una, copia un bloque { ... } y cambia sus textos.
// m = módulo · t = título · x = explicación · p = puntos clave · c = código de ejemplo
export default [
  { m:"Primeros pasos", t:"Hola mundo", x:"PHP funciona en el servidor y genera páginas web.",
    p:["Empieza con <?php", "echo muestra texto"],
    c:`<?php
echo "¡Hola, CódigoCamp!";` },
  { m:"Primeros pasos", t:"Variables y decisiones", x:"Las variables empiezan con $.",
    p:["$nombre = \"Ana\";", ". une textos"],
    c:`<?php
$edad = 20;
if ($edad >= 18) {
  echo "Mayor de edad";
}` },
  { m:"Fundamentos", t:"Bucles", x:"for repite un bloque un número conocido de veces.",
    p:["for ($i = 1; $i <= 5; $i++)", "Las comillas dobles reemplazan $variables"],
    c:`<?php
for ($i = 1; $i <= 5; $i++) {
  echo "Vuelta $i\\n";
}` },
  { m:"Fundamentos", t:"Funciones", x:"function agrupa instrucciones y puede devolver un valor.",
    p:["return devuelve el resultado", "Los parámetros también llevan $"],
    c:`<?php
function doble($n) {
  return $n * 2;
}
echo doble(21);` },
  { m:"Intermedio", t:"Arreglos", x:"PHP tiene arreglos indexados y asociativos. foreach los recorre y funciones como count, sort y array_map los procesan.",
    p:["[1, 2, 3] es un arreglo indexado", "[\"a\" => 1] es un arreglo asociativo", "foreach ($a as $clave => $valor) recorre ambos"],
    c:"<?php\n$nums = [3, 1, 2];\nsort($nums);\nprint_r($nums);\n\n$edades = [\"Ana\" => 20, \"Luis\" => 25];\nforeach ($edades as $nombre => $edad) {\n  echo \"$nombre tiene $edad\\n\";\n}\necho count($nums);",
    r:"Usa array_map para duplicar cada número." },
  { m:"Intermedio", t:"Formularios y superglobales", x:"$_GET y $_POST traen los datos que envía el usuario. Siempre hay que validarlos y escaparlos.",
    p:["$_POST trae datos de un formulario method=\"post\"", "isset comprueba que exista el dato", "htmlspecialchars evita HTML malicioso"],
    c:"<?php\n// Simulamos los datos de un formulario\n$_POST = [\"nombre\" => \"<b>Ana</b>\"];\n\nif (isset($_POST[\"nombre\"])) {\n  $nombre = htmlspecialchars($_POST[\"nombre\"]);\n  echo \"Hola, $nombre\";\n}",
    r:"Valida que el nombre tenga al menos 3 caracteres con strlen.",
    e:"Imprimir datos del usuario sin escaparlos permite ataques XSS." },
  { m:"Avanzado", t:"Clases y objetos", x:"PHP es orientado a objetos: class define el molde, new crea el objeto y $this se refiere a él.",
    p:["__construct inicializa el objeto", "public, private y protected controlan el acceso", "extends permite heredar"],
    c:"<?php\nclass Persona {\n  public function __construct(private string $nombre, private int $edad) {}\n\n  public function saludar(): string {\n    return \"Hola, soy {$this->nombre} y tengo {$this->edad}\";\n  }\n}\n\n$p = new Persona(\"Ana\", 20);\necho $p->saludar();",
    r:"Crea la clase Estudiante que extienda Persona." },
  { m:"Avanzado", t:"Bases de datos con PDO", x:"PDO conecta PHP con MySQL. Las consultas preparadas separan el SQL de los datos y evitan la inyección SQL.",
    p:["PDO funciona con varias bases de datos", "prepare + execute usan parámetros", "Nunca concatenes datos del usuario en el SQL"],
    c:"<?php\n// Con una base real: $pdo = new PDO(\"mysql:host=localhost;dbname=codigocamp\", \"usuario\", \"clave\");\n// $stmt = $pdo->prepare(\"SELECT * FROM usuarios WHERE correo = ?\");\n// $stmt->execute([$correo]);\n// $filas = $stmt->fetchAll(PDO::FETCH_ASSOC);\n\necho \"Consulta preparada = datos seguros\";",
    r:"Escribe una consulta preparada para insertar un usuario con nombre y correo.",
    e:"Concatenar variables dentro del SQL abre la puerta a la inyección SQL." },
  { m:"Experto", t:"Sesiones y seguridad", x:"Las sesiones recuerdan al usuario entre páginas. Las contraseñas se guardan con password_hash, nunca en texto plano.",
    p:["session_start() activa la sesión", "$_SESSION guarda datos del usuario", "password_hash y password_verify protegen las claves"],
    c:"<?php\n$clave = \"secreta123\";\n$hash = password_hash($clave, PASSWORD_DEFAULT);\n\nvar_dump(password_verify(\"secreta123\", $hash));\nvar_dump(password_verify(\"otra\", $hash));",
    r:"Guarda el id del usuario en $_SESSION al iniciar sesión." },
  { m:"Experto", t:"Composer y Laravel", x:"Composer instala librerías. Laravel es el framework PHP más popular y organiza la app con MVC.",
    p:["composer require instala paquetes", "Laravel usa rutas, controladores y vistas", "MVC separa modelo, vista y controlador"],
    c:"<?php\n// composer require laravel/laravel\n//\n// routes/web.php\n// Route::get(\"/hola/{nombre}\", function ($nombre) {\n//     return \"Hola, $nombre\";\n// });\n\necho \"Composer + Laravel\";",
    r:"Instala Composer y crea un proyecto nuevo con composer create-project." },
];
