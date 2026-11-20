"""Terminales, etapas 4 y 5: automatizar con scripts y terminal profesional."""
from ..generador import K

E4 = [
K("Shebang y permisos de ejecución", d="primera línea #! que dice qué intérprete ejecuta el script", u="ejecutar un script con ./script.sh como si fuera un programa",
  mas="Un script de Bash empieza con #!/usr/bin/env bash. Después se le da permiso de ejecución con chmod +x script.sh y se ejecuta con ./script.sh. Sin el shebang, el sistema no sabe con qué programa abrirlo.",
  k=["El shebang va en la primera línea del script.", "chmod +x da permiso de ejecución a un archivo.", "./script.sh ejecuta un script de la carpeta actual."],
  sit="Escribiste copia.sh y al hacer ./copia.sh la terminal dice «Permiso denegado». ¿Qué le falta al archivo?",
  cod="""#!/usr/bin/env bash
# chmod +x hola.sh  y luego  ./hola.sh
echo "Script listo\"""", h="un script con shebang que imprime un mensaje",
  pr=("La orden que da permiso de ejecución es chmod ___. (2 caracteres)", "+x"),
  pr2=("La primera línea #! de un script se llama ___. (7 letras)", "shebang"),
  ec="olvidar el shebang y ejecutar el script con otro intérprete", out="Script listo"),
K("Argumentos y read", d="formas de recibir datos en un script de Bash", u="que el mismo script sirva para distintos archivos o nombres",
  mas="$1, $2… son los argumentos que escribes después del nombre del script; $# dice cuántos hay y $@ los trae todos. read nombre pide un dato por teclado y lo guarda en la variable nombre.",
  k=["$1 es el primer argumento de un script.", "$# cuenta los argumentos recibidos.", "read guarda en una variable lo que escribe el usuario."],
  sit="Tu script debe saludar al nombre que escribes después: ./saludo.sh Ana. ¿Qué variable lees?",
  cod="""#!/usr/bin/env bash
# ./saludo.sh Ana
echo "Hola, $1. Recibí $# argumento(s)\"""", h="saluda con el primer argumento y cuenta los argumentos",
  pr=("El primer argumento de un script de Bash es $___. (1 dígito)", "1"),
  pr2=("La orden que pide un dato por teclado es ___. (4 letras)", "read"),
  ec="usar $1 sin comillas y romper el script con nombres que tienen espacios", out="Hola, Ana. Recibí 1 argumento(s)"),
K("if en Bash", d="estructura que ejecuta órdenes solo si se cumple una condición", u="decidir qué hacer según un archivo, un número o un texto",
  mas="if [ condición ]; then … fi. Con -f archivo preguntas si existe un archivo, con -d una carpeta, -eq compara números y = compara textos. Los espacios dentro de [ ] son obligatorios.",
  k=["if en Bash termina con fi.", "[ -f archivo ] comprueba si un archivo existe.", "-eq compara números en Bash."],
  sit="Tu script debe crear notas.txt solo si todavía no existe. ¿Qué estructura usas?",
  cod="""#!/usr/bin/env bash
if [ -f notas.txt ]; then
  echo "Ya existe"
else
  touch notas.txt && echo "Creado"
fi""", h="crea notas.txt solo si no existe",
  pr=("En Bash, el bloque if se cierra con ___. (2 letras)", "fi"),
  pr2=("La prueba que mira si un archivo existe es [ -___ archivo ]. (1 letra)", "f"),
  ec="olvidar los espacios dentro de los corchetes", out="Creado"),
K("Bucles en Bash", d="estructuras for y while que repiten órdenes", u="procesar muchos archivos o repetir una tarea varias veces",
  mas="for archivo in *.txt; do … done recorre archivos; for i in {1..5} recorre números. while [ condición ]; do … done repite mientras se cumpla. Son la base para automatizar tareas repetitivas.",
  k=["for recorre una lista de elementos.", "Los bucles de Bash terminan con done.", "{1..5} genera los números del 1 al 5."],
  sit="Debes renombrar los 200 archivos .jpg de una carpeta agregando la fecha. ¿Qué estructura repite la orden por ti?",
  cod="""#!/usr/bin/env bash
for i in {1..3}; do
  echo "Vuelta $i"
done""", h="repite un mensaje tres veces",
  pr=("Los bucles de Bash terminan con la palabra ___. (4 letras)", "done"),
  pr2=("El bucle que repite mientras se cumpla una condición es ___. (5 letras)", "while"),
  ec="olvidar do después de la lista del for", out="Vuelta 1\nVuelta 2\nVuelta 3"),
K("Funciones en Bash", d="bloques de órdenes con nombre dentro de un script", u="no repetir el mismo código varias veces en un script",
  mas="Se declaran con nombre() { … } y se llaman escribiendo el nombre. Dentro, los argumentos también son $1, $2. local crea variables que solo existen dentro de la función.",
  k=["Una función de Bash se llama escribiendo su nombre.", "local crea una variable solo para la función.", "Dentro de una función, $1 es su primer argumento."],
  sit="Tu script imprime el mismo encabezado decorado en cinco partes distintas. ¿Qué usas para escribirlo una sola vez?",
  cod="""#!/usr/bin/env bash
titulo() { echo "=== $1 ==="; }
titulo "Respaldo\"""", h="define una función que imprime un título",
  pr=("La palabra que crea variables solo dentro de una función es ___. (5 letras)", "local"),
  pr2=("Para llamar a una función de Bash escribes su ___. (6 letras)", "nombre"),
  ec="llamar a la función antes de declararla", out="=== Respaldo ==="),
K("Código de salida", d="número que devuelve cada orden: 0 si salió bien, otro si falló", u="saber si una orden funcionó y reaccionar",
  mas="$? guarda el código de salida de la última orden. && ejecuta la siguiente solo si la anterior dio 0 y || solo si falló. En scripts, exit 1 termina avisando que hubo un error y set -e corta el script al primer fallo.",
  k=["El código de salida 0 significa éxito.", "$? guarda el código de la última orden.", "set -e detiene el script al primer error."],
  sit="Solo quieres publicar tu web si las pruebas pasaron bien. ¿Qué operador une las dos órdenes?",
  cod="""ls archivo_que_no_existe
echo "Código: $?\"""", h="muestra el código de salida de una orden que falló",
  pr=("La variable con el código de salida de la última orden es $___. (1 carácter)", "?"),
  pr2=("El código de salida de una orden exitosa es ___. (1 dígito)", "0"),
  ec="encadenar con ; y seguir aunque la orden anterior haya fallado", out="ls: no se puede acceder a 'archivo_que_no_existe': No existe el archivo o el directorio\nCódigo: 2"),
K("cron", d="programador de tareas de Linux y macOS", u="ejecutar un script solo cada día, hora o minuto",
  mas="crontab -e abre tus tareas programadas. Cada línea tiene cinco campos (minuto hora día mes día-de-semana) y la orden. 0 2 * * * ./respaldo.sh corre todos los días a las 2:00. En Windows se usa el Programador de tareas.",
  k=["cron ejecuta tareas a horas programadas.", "crontab -e edita las tareas programadas.", "Una línea de cron tiene cinco campos de tiempo."],
  sit="Quieres que tu script de copia de seguridad se ejecute solo todas las noches a las 2 a. m. ¿Qué herramienta usas en Linux?",
  cod="""# crontab -e  y agrega:
0 2 * * * /home/ana/respaldo.sh""", h="programa un script todos los días a las 2:00",
  pr=("La orden que edita las tareas programadas es ___ -e. (7 letras)", "crontab"),
  pr2=("Una línea de cron empieza con ___ campos de tiempo. (1 dígito)", "5", "cinco"),
  ec="usar rutas relativas en cron y que el script no encuentre sus archivos", out=""),
K("Scripts de PowerShell", d="archivos .ps1 con órdenes de PowerShell", u="automatizar tareas en Windows",
  mas="Un script .ps1 se ejecuta con .\\script.ps1. Windows bloquea los scripts por defecto: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned los permite para tu usuario. Las variables empiezan con $ y los parámetros se declaran con param().",
  k=["Los scripts de PowerShell tienen extensión .ps1.", "Set-ExecutionPolicy permite ejecutar scripts.", "param() declara los parámetros de un script."],
  sit="En Windows, tu script limpiar.ps1 no corre y aparece «la ejecución de scripts está deshabilitada». ¿Qué orden cambias?",
  cod="""# saludo.ps1  →  .\\saludo.ps1 -Nombre Ana
param([string]$Nombre = "mundo")
Write-Output "Hola, $Nombre\"""", h="un script .ps1 con un parámetro",
  pr=("La extensión de un script de PowerShell es .___. (3 caracteres)", "ps1"),
  pr2=("Los parámetros de un script .ps1 se declaran con ___(). (5 letras)", "param"),
  ec="desactivar toda la seguridad con Unrestricted para todo el equipo", out="Hola, Ana"),
]

E5 = [
K("find y xargs", d="órdenes para buscar archivos y pasar los resultados a otra orden", u="encontrar y procesar archivos por nombre, tamaño o fecha",
  mas="find . -name \"*.log\" busca por nombre; -size +10M por tamaño y -mtime -1 por fecha. xargs toma la lista y se la pasa a otra orden: find . -name \"*.tmp\" | xargs rm. En PowerShell, Get-ChildItem -Recurse hace lo mismo.",
  k=["find busca archivos dentro de carpetas.", "find -name filtra por nombre.", "xargs pasa una lista a otra orden."],
  sit="Necesitas borrar todos los archivos .tmp que hay en muchas subcarpetas del proyecto. ¿Qué combinación usas?",
  cod="""find . -name "*.log" -size +1M""", h="busca archivos .log de más de 1 MB",
  pr=("La orden que busca archivos dentro de carpetas es ___. (4 letras)", "find"),
  pr2=("La orden que pasa la lista de resultados a otra orden es ___. (5 letras)", "xargs"),
  ec="ejecutar rm con xargs sin revisar antes qué encontró find", out="./logs/servidor.log"),
K("sed", d="editor de texto de la terminal que reemplaza y filtra líneas", u="cambiar texto en muchos archivos sin abrirlos",
  mas="sed 's/viejo/nuevo/g' archivo reemplaza todas las apariciones y muestra el resultado; con -i cambia el archivo. sed -n '5,10p' imprime solo las líneas 5 a 10.",
  k=["sed reemplaza texto con s/viejo/nuevo/.", "La g al final reemplaza todas las apariciones.", "sed -i modifica el archivo directamente."],
  sit="Debes cambiar «localhost» por «db» en el archivo de configuración sin abrir un editor. ¿Qué orden usas?",
  cod="""echo "hola mundo" | sed 's/mundo/terminal/'""", h="reemplaza una palabra en el texto",
  pr=("La orden de terminal que reemplaza texto con s/viejo/nuevo/ es ___. (3 letras)", "sed"),
  pr2=("La opción de sed que modifica el archivo directamente es -___. (1 letra)", "i"),
  ec="usar sed -i sin copia y dañar el archivo con un reemplazo mal escrito", out="hola terminal"),
K("awk", d="herramienta que procesa texto por columnas", u="sacar columnas y totales de archivos CSV o salidas de órdenes",
  mas="awk separa cada línea en campos $1, $2… (por espacios o con -F, para comas). awk -F, '{print $2}' datos.csv imprime la segunda columna y '{s+=$3} END {print s}' suma la tercera.",
  k=["awk trabaja con columnas de texto.", "En awk, $2 es la segunda columna.", "awk -F cambia el separador de columnas."],
  sit="Tienes un CSV de ventas y quieres sumar la columna del precio desde la terminal. ¿Qué herramienta usas?",
  cod="""printf "pan,2\\nleche,3\\n" | awk -F, '{s += $2} END {print s}'""", h="suma la segunda columna de un CSV",
  pr=("La herramienta de terminal que procesa texto por columnas es ___. (3 letras)", "awk"),
  pr2=("La opción de awk que cambia el separador es -___. (1 letra)", "F"),
  ec="olvidar -F, en un CSV y que awk separe por espacios", out="5"),
K("tar y zip", d="órdenes para empaquetar y comprimir archivos", u="enviar o respaldar una carpeta entera en un solo archivo",
  mas="tar -czf respaldo.tar.gz carpeta crea un archivo comprimido y tar -xzf respaldo.tar.gz lo extrae. zip -r web.zip web y unzip web.zip hacen lo mismo con .zip. En PowerShell existen Compress-Archive y Expand-Archive.",
  k=["tar -czf crea un archivo .tar.gz.", "tar -xzf extrae un archivo .tar.gz.", "zip -r comprime una carpeta completa."],
  sit="Debes enviar la carpeta del proyecto (sin abrir el explorador) en un solo archivo comprimido. ¿Qué orden usas?",
  cod="""tar -czf proyecto.tar.gz proyecto/
tar -tzf proyecto.tar.gz""", h="comprime una carpeta y lista su contenido",
  pr=("La orden clásica de Linux para empaquetar archivos es ___. (3 letras)", "tar"),
  pr2=("La opción de zip para incluir subcarpetas es -___. (1 letra)", "r"),
  ec="extraer un .tar.gz en la carpeta equivocada y mezclar archivos", out="proyecto/\nproyecto/index.html"),
K("curl", d="programa de terminal para hacer peticiones HTTP", u="probar APIs y descargar archivos sin navegador",
  mas="curl https://api.ejemplo.com muestra la respuesta. -X POST cambia el método, -H agrega cabeceras y -d envía datos. -o archivo guarda la descarga. Viene en Linux, macOS y Windows 10+.",
  k=["curl hace peticiones HTTP desde la terminal.", "curl -X POST cambia el método de la petición.", "curl -o guarda la respuesta en un archivo."],
  sit="Quieres probar que tu API responde en /productos sin abrir el navegador ni Postman. ¿Qué programa usas?",
  cod="""curl -s https://api.github.com/users/octocat | head -n 3""", h="consulta una API pública y muestra el comienzo",
  pr=("El programa de terminal para peticiones HTTP es ___. (4 letras)", "curl"),
  pr2=("La opción de curl que envía datos en el cuerpo es -___. (1 letra)", "d"),
  ec="olvidar la cabecera Content-Type al enviar JSON", out='{\n  "login": "octocat",\n  "id": 583231,'),
K("WSL", d="Subsistema de Windows para Linux", u="usar Bash y herramientas de Linux dentro de Windows",
  mas="wsl --install instala Ubuntu en Windows 10 y 11. Así tienes una terminal Linux real, con apt, para programar como en un servidor. VS Code se conecta con la extensión WSL y tus archivos de Windows están en /mnt/c.",
  k=["WSL ejecuta Linux dentro de Windows.", "wsl --install instala WSL con Ubuntu.", "En WSL, el disco C: está en /mnt/c."],
  sit="Tu curso usa comandos de Linux pero tu computador tiene Windows. ¿Qué instalas para tener Bash real?",
  cod="""# En PowerShell como administrador:
wsl --install
wsl -l -v""", h="instala WSL y lista las distribuciones",
  pr=("El Subsistema de Windows para Linux se llama ___. (3 letras)", "wsl"),
  pr2=("Dentro de WSL, el disco C: de Windows está en /mnt/___. (1 letra)", "c"),
  ec="guardar los proyectos en /mnt/c y que todo vaya más lento", out="  NAME      STATE           VERSION\n* Ubuntu    Running         2"),
K("Alias y .bashrc", d="atajos de órdenes y archivo de configuración de la terminal", u="escribir menos y dejar la terminal a tu gusto",
  mas="alias gs='git status' crea un atajo. Para que dure, se guarda en ~/.bashrc (Bash) o ~/.zshrc (zsh) y se recarga con source ~/.bashrc. En PowerShell se usa el archivo $PROFILE.",
  k=["alias crea un atajo para una orden.", "~/.bashrc guarda la configuración de Bash.", "source recarga el archivo de configuración."],
  sit="Escribes git status cien veces al día y quieres escribir solo gs. ¿Qué creas?",
  cod="""alias gs='git status'
alias""", h="crea un atajo y lista los alias",
  pr=("La orden que crea un atajo de terminal es ___. (5 letras)", "alias"),
  pr2=("El archivo de configuración de zsh es ~/.___. (5 letras)", "zshrc"),
  ec="crear el alias solo en la terminal abierta y perderlo al cerrarla", out="alias gs='git status'"),
K("tmux", d="multiplexor de terminal: varias terminales en una ventana", u="dejar procesos corriendo en un servidor aunque te desconectes",
  mas="tmux abre una sesión; Ctrl+b % divide en vertical y Ctrl+b \" en horizontal. Ctrl+b d te desconecta sin cerrar nada y tmux attach vuelve a la sesión. Es muy útil por SSH.",
  k=["tmux divide la terminal en paneles.", "Ctrl+b d se desconecta sin cerrar la sesión.", "tmux attach vuelve a una sesión abierta."],
  sit="Por SSH lanzas un proceso largo en el servidor y no quieres que se corte si se cae tu internet. ¿Qué herramienta usas?",
  cod="""tmux new -s trabajo
tmux ls""", h="crea una sesión de tmux y lista las sesiones",
  pr=("El multiplexor de terminal más usado es ___. (4 letras)", "tmux"),
  pr2=("Para volver a una sesión de tmux se usa tmux ___. (6 letras)", "attach"),
  ec="cerrar la ventana con exit y matar los procesos de la sesión", out="trabajo: 1 windows (created Thu Nov 19 12:00:00 2026)"),
]
